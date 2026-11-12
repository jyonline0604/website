#!/usr/bin/env python3
"""
GitHub Pages 部署失敗自動復原（2026-11-12）

背景：2026-11-11 20:17 UTC Pages build run #18536 失敗，根因係 GitHub 側重大事故
（status.github.com: "Impact across multiple GitHub products including Actions, Pages,
and Copilot products", critical, 20:48->21:21）—— upload-artifact 收到 GitHub 錯誤頁
（HTML）而唔係 JSON，5 次重試全失敗。另有 #18437 / #18393 死喺 deploy job
「Timeout reached, aborting!」（syncing_files 階段等 Pages 部署超時）。

Pages workflow 係 GitHub 自動生成（path=dynamic/pages/pages-build-deployment），
唔喺 repo 入面所以無法直接改 workflow；唯一可控嘅做法係：偵測失敗 run 後
重新觸發（rerun）。

安全護欄（防止部署舊內容令網站倒退）：
  - 只會 rerun「head_sha == 現時 origin/main HEAD」嘅失敗 run
    → 絕唔會 rerun 舊 sha，否則會把舊內容部署上線、令章節數倒退
  - 每個 run id 最多 rerun 2 次（state 檔記錄）
  - rerun 前先比對線上章節數 vs 本地章節數（cache-buster），
    線上已經追平就唔需要 rerun
  - 全部用 exit 0 結束，唔會令 cron 報錯
"""

import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

REPO = "jyonline0604/website"
WORKSPACE = "/home/openclaw/.openclaw/workspace"
LOG_FILE = os.path.join(WORKSPACE, "logs/pages-deploy-recovery.log")
STATE_FILE = os.path.join(WORKSPACE, "logs/pages-deploy-recovery-state.json")
SITE = "https://kofhk.com/assets/chapters-data.json"
MAX_RERUN_PER_RUN = 2


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = "[%s] %s" % (ts, msg)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass
    print(line)


def get_token():
    try:
        url = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=WORKSPACE, capture_output=True, text=True, timeout=20,
        ).stdout.strip()
    except Exception:
        return None
    m = re.search(r"https://([^@]+)@", url)
    return m.group(1) if m else None


def api(token, path, method="GET", data=None):
    url = "https://api.github.com" + path
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", "Bearer " + token)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "openclaw-pages-recovery")
    if body:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            raw = r.read().decode("utf-8", "replace")
            return r.status, (json.loads(raw) if raw.strip() else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {"raw": raw[:200]}
    except Exception as e:
        return 0, {"error": str(e)}


def local_chapters():
    try:
        with open(os.path.join(WORKSPACE, "assets/chapters-data.json"), encoding="utf-8") as f:
            d = json.load(f)
        return len(d) if isinstance(d, list) else int(d.get("total", 0))
    except Exception:
        return 0


def live_chapters():
    """線上章節數（帶 cache-buster，避免 Cloudflare 舊快取）"""
    try:
        req = urllib.request.Request(SITE + "?v=%d" % int(time.time()),
                                     headers={"User-Agent": "openclaw-pages-recovery"})
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read().decode("utf-8", "replace"))
        return len(d) if isinstance(d, list) else int(d.get("total", 0))
    except Exception:
        return 0


def origin_head():
    try:
        out = subprocess.run(
            ["git", "ls-remote", "origin", "refs/heads/main"],
            cwd=WORKSPACE, capture_output=True, text=True, timeout=30,
        ).stdout.strip()
        return out.split()[0] if out else None
    except Exception:
        return None


def load_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(state):
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=1)
    except OSError:
        pass


def main():
    token = get_token()
    if not token:
        log("⚠️ 攞唔到 GitHub token，跳過")
        return 0

    head = origin_head()
    loc, live = local_chapters(), live_chapters()
    log("── 巡檢開始 ── origin/main=%s | 本地章節=%s | 線上章節=%s" %
        (head[:8] if head else "?", loc, live))

    # 注意：Pages workflow 係 GitHub 自動生成（path=dynamic/pages/pages-build-deployment），
    # 用 /actions/workflows/<name>/runs 會回 404；改用通用 /actions/runs 再按名稱篩選
    st, data = api(token, "/repos/%s/actions/runs?per_page=30" % REPO)
    if st != 200:
        log("⚠️ 拉唔到 runs list (HTTP %s)：%s" % (st, str(data)[:120]))
        return 0

    runs = [r for r in data.get("workflow_runs", [])
            if r.get("name") == "pages build and deployment"]
    if not runs:
        log("ℹ️ 近 30 個 run 入面搵唔到 pages build and deployment")
        return 0
    failed = [r for r in runs if r.get("conclusion") == "failure"]
    recent_fail = failed[0] if failed else None
    if not recent_fail:
        log("✅ 近 12 個 Pages run 冇失敗")
        return 0

    log("ℹ️ 最近失敗 run: #%s sha=%s (%s)" %
        (recent_fail["run_number"], recent_fail["head_sha"][:8], recent_fail["created_at"][:16]))

    # --- 護欄 1：只處理當前 origin/main HEAD 的失敗 run（避免部署舊內容令網站倒退）---
    if head and recent_fail["head_sha"] != head:
        log("ℹ️ 失敗 run 嘅 sha 唔等於現時 origin/main HEAD（可能已被後續 commit 蓋過）→ 唔 rerun")
        return 0

    # --- 護欄 2：線上已經追平就唔需要 rerun ---
    if loc and live and live >= loc:
        log("✅ 線上章節數 %s >= 本地 %s，部署實際已生效（可能係後續成功 run 補上）→ 唔 rerun" % (live, loc))
        return 0

    state = load_state()
    rid = str(recent_fail["id"])
    tries = int(state.get(rid, 0))
    if tries >= MAX_RERUN_PER_RUN:
        log("⚠️ run #%s 已經 rerun 過 %d 次（上限 %d）→ 唔再自動重試，需人手跟進" %
            (recent_fail["run_number"], tries, MAX_RERUN_PER_RUN))
        return 0

    st2, resp = api(token, "/repos/%s/actions/runs/%s/rerun" % (REPO, rid), method="POST")
    if st2 in (201, 202):
        state[rid] = tries + 1
        save_state(state)
        log("✅ 已觸發 rerun：run #%s（attempt %d/%d），下一次 run 會重新 build + deploy" %
            (recent_fail["run_number"], tries + 1, MAX_RERUN_PER_RUN))
    else:
        log("❌ rerun 觸發失敗 (HTTP %s)：%s" % (st2, str(resp)[:160]))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        log("❌ 未預期錯誤：%s" % e)
        sys.exit(0)
