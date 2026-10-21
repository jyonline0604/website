#!/usr/bin/env python3
"""OpenClaw cron model-policy guard.

Detects and repairs automation model overrides that agents.*.modelPolicy.allow
would reject. Root cause of the 2026-10-21 outage: guardian only checked
"job exists + enabled", never the model override, so jobs looked healthy while
every run was rejected by policy.
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
        if model and model not in allow:
            print("WARN: %s model override %r not in policy allow list" % (name, model))
            if FIX and primary:
                r = run(CLI + " cron edit %s --model %s" % (jid, primary))
                if r.returncode == 0:
                    print("FIXED: %s model -> %s" % (name, primary))
                    fixed += 1
                else:
                    print("WARN: model fix failed for %s: %s" % (name, r.stderr.strip()[:200]))
        bad = [f for f in fbs if f not in allow]
        if bad:
            print("WARN: %s fallbacks not allowed: %s" % (name, ",".join(bad)))
            if FIX:
                good = [f for f in fbs if f in allow] or ([primary] if primary else [])
                if good:
                    r = run(CLI + " cron edit %s --fallbacks %s" % (jid, ",".join(good)))
                    if r.returncode == 0:
                        print("FIXED: %s fallbacks -> %s" % (name, ",".join(good)))
                        fixed += 1
                    else:
                        print("WARN: fallback fix failed for %s" % name)
        state = j.get("state") or {}
        ce = state.get("consecutiveErrors") or 0
        if ce >= 3:
            print("WARN: %s consecutiveErrors=%s last=%s err=%s" % (name, ce, j.get("lastRunStatus"), (j.get("lastRunError") or "")[:140]))
    if not fixed:
        print("OK: every job model override is within policy allow list")
    return 0


sys.exit(main())
