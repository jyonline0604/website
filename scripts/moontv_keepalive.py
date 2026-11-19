#!/usr/bin/env python3
"""
MoonTV (jyonline0604/MoonTV) Upstream Sync 保活 + 自癒 watchdog
建立：2026-11-19

背景
----
GitHub 規則：repo 連續 60 日無活動，scheduled workflow 會被自動停用
（email 標題「The 'Upstream Sync' workflow ... will be disabled soon」）。
MoonTV fork 最後 push = 2026-02-05 → 已超 286 日，但 Upstream Sync 暫時仲
active（每 6 小時跑一次，全部 success）。

本 script 做三件事
------------------
1) 監察 fork 活動度（pushed_at）同 Upstream Sync workflow 狀態
2) 接近門檻 / 已被停用時：
   - 若 token 對 MoonTV 有寫入權限 → 自動做復原：
       a) 用 Git Data API 推一個「空 commit」（tree 不變 → 零檔案改動 →
          不會觸發 Build & Push Docker image、唔會污染內容、唔會 merge 衝突）
          → 重置 60 日倒數
       b) 用 Actions API 重新 enable 被停用嘅 workflow
   - 若無寫入權限 → 發 Telegram 通知，附即場可做嘅步驟
3) 順帶偵測 sync.yml 嘅 upstream 指向有冇錯（目前指緊 senshinya/MoonTV
   —— 一個 2025-08 停更嘅 repo，而真正上游係 samqin123/MoonTV）

設計原則
--------
- 永遠 exit 0（唔好令 cron 報錯）
- 冇寫入權限時自動降級為「通知」模式
- 通知去重：同一種告警 24 小時內唔重複發
"""
import base64, json, os, re, subprocess, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone, timedelta

REPO = "jyonline0604/MoonTV"
WORKSPACE = "/home/openclaw/.openclaw/workspace"
STATE_FILE = os.path.join(WORKSPACE, ".moontv-keepalive-state.json")
LOG_FILE = os.path.join(WORKSPACE, "logs/moontv-keepalive.log")
INACTIVITY_WARN_DAYS = 45      # 距離 60 日門檻剩幾多日就開始提醒
TELEGRAM_TARGET = "5344443732"
SYNC_WORKFLOW_ID = 230755924
EXPECTED_UPSTREAM = "samqin123/MoonTV"   # 真正上游（fork 嘅 GitHub parent）


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


def read_token():
    """搵 GitHub token：優先 .token-store，其次 git remote / .git-credentials"""
    # 1) 專用 token store（用戶可放一個有 MoonTV 寫入權限嘅 PAT 落嚟）
    for name in ("github-moontv-token.txt", "github-token.txt"):
        p = os.path.join(WORKSPACE, ".token-store", name)
        try:
            with open(p, encoding="utf-8") as f:
                t = f.read().strip()
            if t:
                return t, "token-store/" + name
        except OSError:
            pass
    # 2) 現有 repo remote（只有讀權限，夠做監察）
    try:
        url = subprocess.run(["git", "remote", "get-url", "origin"], cwd=WORKSPACE,
                             capture_output=True, text=True, timeout=20).stdout.strip()
        m = re.search(r"https://([^@]+)@", url)
        if m:
            t = m.group(1)
            if ":" in t:
                t = t.split(":", 1)[1]
            return t, "origin-remote"
    except Exception:
        pass
    # 3) git credentials
    try:
        for line in open("/home/openclaw/.git-credentials", encoding="utf-8"):
            m = re.search(r"https://[^:@/]+:([^@]+)@", line.strip())
            if m:
                return m.group(1), "git-credentials"
    except OSError:
        pass
    return None, None


def api(token, method, path, data=None, timeout=45):
    auth = "Basic " + base64.b64encode(("x-access-token:" + token).encode()).decode()
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request("https://api.github.com" + path, data=body, method=method)
    req.add_header("Authorization", auth)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "openclaw-moontv-keepalive")
    if body:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
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


def notify(text):
    """發 Telegram（經 openclaw CLI）"""
    try:
        # 動態解析 openclaw CLI（避免硬編碼 node 路徑）
        oc = None
        for d in sorted(os.listdir("/home/openclaw/.nvm/versions/node"), reverse=True):
            cand = "/home/openclaw/.nvm/versions/node/%s/bin/openclaw" % d
            if os.path.exists(cand):
                oc = cand
                break
        if not oc:
            oc = "/home/openclaw/.openclaw/tmp/agent-cli/openclaw"
        if not os.path.exists(oc):
            log("⚠️ 搵唔到 openclaw CLI，通知跳過")
            return
        r = subprocess.run([oc, "message", "send", "--channel", "telegram",
                            "--target", TELEGRAM_TARGET, "--message", text],
                           capture_output=True, text=True, timeout=90)
        log("📨 Telegram 通知: %s" % ("已發送" if r.returncode == 0 else "失敗 rc=%d %s" % (r.returncode, r.stderr[:100])))
    except Exception as e:
        log("⚠️ 通知失敗: %s" % e)


def load_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(s):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(s, f, ensure_ascii=False, indent=1)
    except OSError:
        pass


def notify_once(state, key, hours=24):
    """同一種告警 hours 小時內唔重複發"""
    last = state.get(key)
    now = time.time()
    if last and (now - float(last)) < hours * 3600:
        return False
    state[key] = now
    return True


def push_keepalive(token):
    """推一個空 commit（tree 不變）→ 重置 60 日倒數"""
    st, ref = api(token, "GET", "/repos/%s/git/ref/heads/main" % REPO)
    if st != 200:
        return False, "讀取 main ref 失敗 HTTP %s" % st
    main_sha = ref.get("object", {}).get("sha")
    if not main_sha:
        return False, "攞唔到 main sha"
    st, cm = api(token, "GET", "/repos/%s/git/commits/%s" % (REPO, main_sha))
    if st != 200:
        return False, "讀取 commit 失敗 HTTP %s" % st
    tree = cm.get("tree", {}).get("sha")
    if not tree:
        return False, "攞唔到 tree sha"
    st, commit = api(token, "POST", "/repos/%s/git/commits" % REPO, {
        "message": "chore: keep repo active (prevent GitHub auto-disabling scheduled workflows after 60 days of inactivity)",
        "tree": tree, "parents": [main_sha]})
    if st != 201:
        return False, "建立 commit 失敗 HTTP %s: %s" % (st, str(commit.get("message"))[:90])
    st, upd = api(token, "PATCH", "/repos/%s/git/refs/heads/main" % REPO,
                  {"sha": commit["sha"], "force": False})
    if st not in (200, 204):
        return False, "更新 ref 失敗 HTTP %s: %s" % (st, str(upd.get("message"))[:90])
    return True, commit["sha"][:12]


def enable_workflow(token):
    st, r = api(token, "PUT", "/repos/%s/actions/workflows/%s/enable" % (REPO, SYNC_WORKFLOW_ID))
    return st in (204, 200), "HTTP %s %s" % (st, str(r.get("message"))[:80])


def main():
    token, src = read_token()
    if not token:
        log("⚠️ 搵唔到 GitHub token，跳過")
        return 0
    st, repo = api(token, "GET", "/repos/%s" % REPO)
    if st != 200:
        log("⚠️ 讀取 repo 失敗 HTTP %s" % st)
        return 0
    pushed = repo.get("pushed_at")
    days = None
    if pushed:
        try:
            pt = datetime.strptime(pushed, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            days = (datetime.now(timezone.utc) - pt).days
        except Exception:
            pass
    st, wf = api(token, "GET", "/repos/%s/actions/workflows/%s" % (REPO, SYNC_WORKFLOW_ID))
    wf_state = wf.get("state") if st == 200 else "unknown"
    log("── 巡檢 ── token=%s | pushed_at=%s (%s 日前) | Upstream Sync=%s" %
        (src, pushed, days, wf_state))

    state = load_state()
    acted = False
    issues = []

    # --- 1) workflow 被停用 → 重新 enable ---
    if wf_state != "active":
        ok, msg = enable_workflow(token)
        if ok:
            log("✅ 已重新 enable Upstream Sync workflow")
            acted = True
        else:
            issues.append("⚠️ **Upstream Sync workflow 已被停用**（state=%s）\n"
                          "   自動 re-enable 失敗：%s\n"
                          "   → 手動處理：https://github.com/%s/actions/workflows/%s" %
                          (wf_state, msg, REPO, SYNC_WORKFLOW_ID))
            if notify_once(state, "wf_disabled", hours=72):
                pass
            else:
                issues[-1] = None

    # --- 2) 接近 60 日門檻 → 推空 commit 重置倒數 ---
    if days is not None and days >= INACTIVITY_WARN_DAYS:
        ok, msg = push_keepalive(token)
        if ok:
            log("✅ 已推空 commit 重置 60 日倒數 (new sha=%s)" % msg)
            acted = True
        else:
            issues.append("⚠️ **MoonTV fork 已 %d 日無 push**（GitHub 會喺 60 日自動停用 scheduled workflow）\n"
                          "   自動推空 commit 失敗：%s\n"
                          "   → 手動做其中一樣（30 秒）：喺 https://github.com/%s 改一個檔案（如 README）加個空格再 commit；"
                          "或 email 撳「Manage workflow」開啟防止被停用" % (days, msg, REPO))
            if notify_once(state, "inactive", hours=72):
                pass
            else:
                issues[-1] = None

    # --- 3) 順帶檢查 sync.yml upstream 指向 ---
    st, raw = api(token, "GET", "/repos/%s/contents/.github/workflows/sync.yml" % REPO)
    if st == 200:
        try:
            import base64 as b64
            content = b64.b64decode(raw.get("content", "")).decode("utf-8", "replace")
            m = re.search(r"upstream_sync_repo:\s*(\S+)", content)
            up = m.group(1) if m else "?"
            if up and EXPECTED_UPSTREAM not in up:
                if notify_once(state, "wrong_upstream", hours=168):
                    issues.append("ℹ️ fork 嘅 sync.yml 指向 %s，但真正上游係 %s（2146 stars，仍活躍）。"
                                  "而家兩邊 main 內容一致、暫時無影響，但上游一改就同步唔到。"
                                  "要改需要對 %s 有寫入權限嘅 token。" %
                                  (up, EXPECTED_UPSTREAM, REPO))
                log("ℹ️ sync.yml upstream 指向 %s（應為 %s）" % (up, EXPECTED_UPSTREAM))
        except Exception as e:
            log("ℹ️ sync.yml 檢查失敗: %s" % e)

    save_state(state)

    # 合併成一條訊息發出（去噪）
    msgs = [i for i in issues if i]
    if msgs:
        notify("🔔 **MoonTV Upstream Sync 保活巡檢**（jyonline0604/MoonTV）\n\n" + "\n\n".join(msgs) +
               "\n\n_自動 watchdog 已裝喺本機每日巡檢；有 MoonTV 寫入權限嘅 token 就會全自動處理。_")
    elif acted:
        log("✅ 已自動修復，毋須通知")

    log("── 完成 ── acted=%s issues=%d" % (acted, len(msgs)))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        log("❌ 未預期錯誤: %s" % e)
        sys.exit(0)
