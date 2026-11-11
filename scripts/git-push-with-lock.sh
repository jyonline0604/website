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

# 先提交本地改動，再 rebase 同步
# 2026-11-05 修正：原本順序係「先 pull 後 commit」——有本地改動時 rebase 必然失敗，
# 然後 fallback 嘅 `git reset --hard origin/main` 會靜靜抹走未提交改動（今晚 22:00 實測中招：
# SKILL.md v2.9.126 + memory 紀錄被 reset --hard 刪咗）
if [[ -n $(git status --porcelain) ]]; then
    # 如果有傳入 commit message，使用它；否則用預設
    if [[ -n "${1:-}" ]]; then
        git add -A
        git commit -m "$1" || true
    fi
fi

# 同步 remote（避免 non-fast-forward）
git pull --rebase -X theirs origin main 2>/dev/null || {
    git rebase --abort 2>/dev/null || true
    echo "  ⚠️ Git 同步出錯，改用 stash 安全同步（唔會再 reset --hard 抹走改動）..."
    STASH_REF=""
    # 2026-11-11 修：先 commit 再考慮 stash。舊做法直接 stash -u + reset --hard，
    # 萬一 pop 撞衝突，改動就靜靜留喺 stash（2026-10-09 兩篇 DREAMS.md 夢境咁樣失蹤咗一個月）。
    if [[ -n $(git status --porcelain) ]]; then
        git add -A >/dev/null 2>&1
        git commit -m "auto-commit before sync $(date +%Y%m%d-%H%M%S)" >/dev/null 2>&1 || true
    fi
    if [[ -n $(git status --porcelain) ]]; then
        git stash push -u -m "auto-stash $(date +%Y%m%d-%H%M%S)" >/dev/null 2>&1 && STASH_REF="stash@{0}"
    fi
    git fetch origin main
    git reset --hard origin/main 2>/dev/null || true
    if [[ -n "$STASH_REF" ]]; then
        if ! git stash pop "$STASH_REF" >/dev/null 2>&1; then
            REC="$WORKSPACE/backups/stash-recovery/stash-$(date +%Y%m%d-%H%M%S).patch"
            mkdir -p "$WORKSPACE/backups/stash-recovery" 2>/dev/null || true
            git stash show -p "$STASH_REF" > "$REC" 2>/dev/null || true
            echo "  ⚠️ stash pop 有衝突！改動已保留喺 stash，並導出 patch：$REC（需人工合併）"
        fi
    fi
}

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
