#!/usr/bin/env python3
"""OpenClaw cron model-policy guard.

Detects and repairs automation model overrides that agents.*.modelPolicy.allow
would reject. Root cause of the 2026-10-21 outage: guardian only checked
"job exists + enabled", never the model override, so jobs looked healthy while
every run was rejected by policy.

2026-11-13 addition — provider-consistency rule:
OpenClaw 2026.11 records an inference account per job (model@profile) and the
runtime rejects any fallback candidate whose provider differs from the recorded
one ("Automation candidate is incompatible with its recorded inference account
and route"). So a job's primary and its whole fallback chain MUST live in the
same provider+profile, and the chain must not repeat the primary. This guard
therefore repairs chains inside one provider instead of resetting the primary to
agents.defaults.model.primary (which used to silently resurrect a dead chain).
"""
import json, os, subprocess, sys

CONFIG = os.path.expanduser("~/.openclaw/openclaw.json")
CLI = "openclaw"
FIX = "--fix" in sys.argv


def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def load_cfg():
    try:
        with open(CONFIG) as f:
            return json.load(f)
    except Exception as e:
        print("WARN: cannot read config: %s" % e)
        return {}


def allowed_models(cfg):
    agents = cfg.get("agents", {}) or {}
    allow = set()
    sources = [
        (agents.get("defaults", {}) or {}).get("modelPolicy", {}) or {},
        ((agents.get("entries", {}) or {}).get("main", {}) or {}).get("modelPolicy", {}) or {},
    ]
    for src in sources:
        allow.update(src.get("allow", []) or [])
    return allow


def profile_variant(base, allow):
    """搵 allow list 入面 "<base>@<profile>" 變體（2026.11 起每個 candidate 都要綁 account）。"""
    if not base:
        return None
    for a in sorted(allow):
        if a.startswith(base + "@"):
            return a
    return None


def chain_model(fbs, allow, primary):
    """揀一個同 fallback 鏈同一 provider+profile 嘅 model（避免跨 provider 死鏈）。"""
    for f in fbs:
        base = f.split("@", 1)[0]
        pv = profile_variant(base, allow)
        if pv:
            return pv
    if primary:
        return profile_variant(primary, allow) or primary
    return None


def dedupe_chain(fbs, model):
    """fallback 鏈唔可以重複 primary（自我指向 = 等於冇 fallback）。"""
    out, seen = [], set()
    for f in fbs:
        if f == model or f in seen:
            continue
        seen.add(f)
        out.append(f)
    return out


def main():
    cfg = load_cfg()
    allow = allowed_models(cfg)
    if not allow:
        print("WARN: allow list empty, skipping")
        return 0
    primary = ((cfg.get("agents", {}) or {}).get("defaults", {}) or {}).get("model", {}).get("primary")
    out = run(CLI + " cron list --json")
    if out.returncode != 0:
        print("WARN: cron list failed: %s" % out.stderr.strip()[:200])
        return 0
    try:
        data = json.loads(out.stdout)
    except Exception as e:
        print("WARN: bad json from cron list: %s" % e)
        return 0
    jobs = data if isinstance(data, list) else (data.get("jobs") or [])
    fixed = 0
    for j in jobs:
        name = j.get("name") or j.get("id")
        jid = j.get("id")
        payload = j.get("payload") or {}
        model = payload.get("model")
        fbs = payload.get("fallbacks") or []
        base = model.split("@", 1)[0] if model else model
        if model and model not in allow and base not in allow:
            print("WARN: %s model override %r not in policy allow list" % (name, model))
            if FIX and primary:
                # 保留原 chain 嘅 provider（2026.11 起跨 provider fallback 會被 runtime 直接拒絕）
                cand = chain_model(fbs, allow, primary)
                if not cand:
                    continue
                r = run(CLI + " cron edit %s --model %s" % (jid, cand))
                if r.returncode == 0:
                    print("FIXED: %s model -> %s" % (name, cand))
                    fixed += 1
                else:
                    print("WARN: model fix failed for %s: %s" % (name, r.stderr.strip()[:200]))
        if model and "@" not in model and primary:
            pv = chain_model(fbs, allow, primary)
            if pv:
                print("WARN: %s model override 冇 @profile（2026.11 起需要 recorded inference account）" % name)
                if FIX:
                    r = run(CLI + " cron edit %s --model %s" % (jid, pv))
                    if r.returncode == 0:
                        print("FIXED: %s model -> %s" % (name, pv))
                        fixed += 1
        bad = [f for f in fbs if f not in allow and f.split("@", 1)[0] not in allow]
        if bad:
            print("WARN: %s fallbacks not allowed: %s" % (name, ",".join(bad)))
            if FIX:
                good = []
                for f in fbs:
                    if f in allow:
                        good.append(f)
                        continue
                    pv = profile_variant(f.split("@", 1)[0], allow)
                    if pv:
                        good.append(pv)
                if not good:
                    pv = chain_model([], allow, primary)
                    good = [pv] if pv else []
                if good:
                    # primary 必須同 chain 同一 provider，且唔可以喺 chain 內重複
                    cand = chain_model(good, allow, primary)
                    good = dedupe_chain(good, cand)
                    if not good:
                        good = [cand]
                    r = run(CLI + " cron edit %s --model %s --fallbacks %s" % (jid, cand, ",".join(good)))
                    if r.returncode == 0:
                        print("FIXED: %s -> %s | fallbacks %s" % (name, cand, ",".join(good)))
                        fixed += 1
                    else:
                        print("WARN: fallback fix failed for %s: %s" % (name, r.stderr.strip()[:200]))
        state = j.get("state") or {}
        ce = state.get("consecutiveErrors") or 0
        if ce >= 3:
            print("WARN: %s consecutiveErrors=%s last=%s err=%s" % (name, ce, j.get("lastRunStatus"), (j.get("lastRunError") or "")[:140]))
    if not fixed:
        print("OK: every job model override is within policy allow list")
    return 0


sys.exit(main())
