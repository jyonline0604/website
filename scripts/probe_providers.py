#!/usr/bin/env python3
"""Probe real provider availability (read-only). Prints status codes only, never keys."""
import json, os, sqlite3, urllib.request, urllib.error

DB = os.path.expanduser("~/.openclaw/state/openclaw.sqlite")
con = sqlite3.connect(DB)
rows = con.execute("SELECT value_json FROM config_machine_state WHERE state_key='authProfiles.store'").fetchall()
store = json.loads(rows[0][0])
profiles = store.get("profiles") or {}

def req(url, headers, payload):
    data = json.dumps(payload).encode()
    r = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(r, timeout=45) as resp:
            body = resp.read().decode("utf-8", "replace")
            return resp.status, body
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return 0, str(e)[:200]

def summarize(status, body, kind):
    try:
        d = json.loads(body)
    except Exception:
        return "unparsable"
    if kind == "anthropic":
        if d.get("type") == "error" or d.get("error"):
            err = d.get("error") or {}
            return "ERR type=%s msg=%s" % (err.get("type"), str(err.get("message"))[:80])
        txt = "".join(b.get("text", "") for b in (d.get("content") or []))
        return "OK text_len=%d sample=%r" % (len(txt), txt[:40])
    if "error" in d and d.get("error"):
        err = d["error"]
        return "ERR type=%s msg=%s" % (err.get("type") or err.get("code"), str(err.get("message"))[:80])
    choices = d.get("choices") or []
    if choices:
        msg = choices[0].get("message") or {}
        txt = msg.get("content")
        if not txt:
            txt = msg.get("reasoning") or ""
        return "OK text_len=%d sample=%r" % (len(txt or ""), (txt or "")[:40])
    return "no-choices"

print("=== minimax profiles (anthropic endpoint) ===")
for pid in [p for p in profiles if p.startswith("minimax")]:
    key = profiles[pid].get("key") or ""
    if not key:
        continue
    st, body = req(
        "https://api.minimaxi.com/anthropic/v1/messages",
        {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
        {"model": "MiniMax-M3.1-Flash", "max_tokens": 16, "messages": [{"role": "user", "content": "say OK"}]},
    )
    print("  %-28s suffix=%s HTTP %s | %s" % (pid, key[-4:], st, summarize(st, body, "anthropic")))

print()
print("=== openrouter free chain (chat/completions) ===")
or_key = (profiles.get("openrouter:default") or {}).get("key") or ""
models = [
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "cohere/north-mini-code:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "poolside/laguna-s-2.1:free",
    "recursive/flint-v1.0:free",
]
for m in models:
    st, body = req(
        "https://openrouter.ai/api/v1/chat/completions",
        {"authorization": "Bearer " + or_key, "content-type": "application/json"},
        {"model": m, "max_tokens": 24, "messages": [{"role": "user", "content": "say OK"}]},
    )
    print("  %-52s HTTP %s | %s" % (m, st, summarize(st, body, "chat")))
