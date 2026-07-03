#!/bin/bash
# 🔒 帶鎖的 Git Push 腳本
# 防止多個 cron job 同時 push 到同一個 repo 導致 lock ref / non-fast-forward 錯誤
# 使用方法: ./scripts/git-push-with-lock.sh [commit_message]

set -euo pipefail

WORKSPACE="/home/openclaw/.openclaw/workspace"
LOCKFILE="$WORKSPACE/.git-push.lock"
TIMEOUT=120  # 最多等待120秒

cd "$WORKSPACE"

# 用 flock 獲取鎖（等待最多 $TIMEOUT 秒）
exec 200>"$LOCKFILE"
if ! flock -w $TIMEOUT 200; then
    echo "  ❌ 無法獲取 Git Push 鎖（等待超時 > ${TIMEOUT}s）"
    exit 1
fi

echo "  🔒 已獲取 Git Push 鎖"

# 同步 remote（避免 non-fast-forward）
git pull --rebase -X theirs origin main 2>/dev/null || {
    git rebase --abort 2>/dev/null || true
    echo "  ⚠️ Git 同步出錯，嘗試 force 同步..."
    git fetch origin main
    git reset --hard origin/main 2>/dev/null || true
}

# 檢查是否有變更
if [[ -n $(git status --porcelain) ]]; then
    # 如果有傳入 commit message，使用它；否則用預設
    if [[ -n "${1:-}" ]]; then
        git add -A
        git commit -m "$1" || true
    fi
fi

# 推送到 GitHub（自動重試3次）
for attempt in 1 2 3; do
    # 推之前再同步一次
    git pull --rebase -X theirs origin main 2>/dev/null || git rebase --abort 2>/dev/null || true
    
    if git push origin main 2>&1; then
        echo "  ✅ 已推送到 GitHub"
        break
    fi
    
    if [ $attempt -lt 3 ]; then
        echo "  ⚠️ Push 失敗 (attempt $attempt/3)，重試中..."
        sleep 3
    else
        echo "  ⚠️ Push 最終失敗（auto-generated 數據安全，嘗試 force）"
        git push origin main --force-with-lease 2>/dev/null || echo "  ❌ Push 仍然失敗"
    fi
done

# 釋放鎖
flock -u 200 2>/dev/null || true
echo "  🔓 Git Push 鎖已釋放"
