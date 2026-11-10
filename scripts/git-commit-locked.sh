#!/bin/bash
# git add + commit 序列化：同一把 .git-push.lock，避免多個 cron script 同時 commit/pull 撞 rebase 衝突
set -uo pipefail
WORKSPACE="/home/openclaw/.openclaw/workspace"
cd "$WORKSPACE"
exec 200>>"$WORKSPACE/.git-push.lock"
if ! flock -w 180 200; then
  echo "  ❌ 拿不到 git 鎖（等待超時）"
  exit 1
fi
bash "$WORKSPACE/scripts/git-clean-conflicts.sh"
FILE="$1"
MSG="$2"
git add "$FILE" || exit 1
git commit -m "$MSG" || true
