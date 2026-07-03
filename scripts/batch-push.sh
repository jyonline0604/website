#!/bin/bash
# 批次推送腳本 — 單一推送入口，取代各 script 獨立的 push
# 整合：
#   1. flock 防止同機多個 push 同時執行
#   2. GitHub API 檢查 Pages 部署狀態，避免重疊部署
#   3. 合併所有 pending commits 為一次性推送
#
# 使用方法: ./scripts/batch-push.sh ["custom commit message"]

set -euo pipefail

WORKSPACE="/home/openclaw/.openclaw/workspace"
LOCKFILE="$WORKSPACE/.git-push.lock"
TIMEOUT=180

# GitHub repo info
REPO="jyonline0604/website"
GITHUB_API="https://api.github.com/repos/${REPO}"

cd "$WORKSPACE"

# ── Step 1: 取得檔案鎖 ──
exec 200>"$LOCKFILE"
if ! flock -w $TIMEOUT 200; then
    echo "  ❌ 無法獲取 Git Push 鎖（等待超時 > ${TIMEOUT}s）"
    exit 1
fi
echo "  🔒 已獲取 Git Push 鎖"

# ── Step 2: 檢查是否有進行中的 Pages 部署 ──
check_pages_deploying() {
    # 用 deployments API 檢查最新部署狀態
    local status
    status=$(curl -sf --connect-timeout 5 --max-time 10 \
        -H "Accept: application/vnd.github+json" \
        -H "User-Agent: kofhk-batch-push" \
        "${GITHUB_API}/deployments?environment=github-pages&per_page=1" 2>/dev/null | \
        python3 -c "
import json, sys
data = json.load(sys.stdin)
if data and len(data) > 0:
    # Check statuses for the latest deployment
    import subprocess, urllib.request
    url = data[0]['statuses_url']
    req = urllib.request.Request(url, headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'kofhk'})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            statuses = json.loads(resp.read())
            latest = statuses[0] if statuses else {}
            print(latest.get('state', 'unknown'))
    except:
        print('unknown')
else:
    print('none')
" 2>/dev/null || echo "unknown")

    case "$status" in
        queued|in_progress|waiting)
            return 0  # 部署中
            ;;
        *)
            return 1  # 空閒或未知（繼續推送）
            ;;
    esac
}

if check_pages_deploying; then
    echo "  ⏳ GitHub Pages 部署進行中，等待完成..."
    for i in $(seq 1 30); do
        sleep 10
        if ! check_pages_deploying; then
            echo "  ✅ Pages 部署已完成，繼續推送"
            break
        fi
        if [ $i -eq 30 ]; then
            echo "  ⚠️ 等待超時（5分鐘），強制推送"
        fi
    done
fi

# ── Step 3: 同步 remote ──
echo "  🔄 同步 remote..."
git pull --rebase -X theirs origin main 2>/dev/null || {
    git rebase --abort 2>/dev/null || true
    echo "  ⚠️ Rebase 失敗，使用 fetch + reset"
    git fetch origin main
    git reset --hard origin/main 2>/dev/null || true
}

# ── Step 4: 檢查是否有任何變更，合併為單一 commit ──
if [[ -z $(git status --porcelain) ]]; then
    echo "  📭 無變更需要推送"
    flock -u 200 2>/dev/null || true
    echo "  🔓 Git Push 鎖已釋放"
    exit 0
fi

# 如果有自訂 commit message 就使用，否則生成統一的批次訊息
if [[ -n "${1:-}" ]]; then
    COMMIT_MSG="$1"
else
    COMMIT_MSG="📦 批次數據更新 $(date -u '+%Y-%m-%d %H:%M UTC')"
fi

echo "  📝 提交變更: $COMMIT_MSG"
git add -A
git commit -m "$COMMIT_MSG" || true

# ── Step 5: 推送 ──
echo "  🚀 推送中..."
for attempt in 1 2 3; do
    git pull --rebase -X theirs origin main 2>/dev/null || git rebase --abort 2>/dev/null || true

    if git push origin main 2>&1; then
        echo "  ✅ 已推送到 GitHub"
        break
    fi

    if [ $attempt -lt 3 ]; then
        echo "  ⚠️ Push 失敗 (attempt $attempt/3)，重試中..."
        sleep 5
    else
        echo "  ⚠️ Push 最終失敗，嘗試 force-with-lease"
        git push origin main --force-with-lease 2>/dev/null || echo "  ❌ Push 仍然失敗"
    fi
done

# ── 釋放鎖 ──
flock -u 200 2>/dev/null || true
echo "  🔓 Git Push 鎖已釋放"
