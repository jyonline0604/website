#!/bin/bash
# 清理 git 殘留嘅合併／rebase 衝突狀態（2026-11-10 新增）
#
# 背景：多個 cron script（finance / finance-news / news-backup / aqhi）喺同一分鐘跑，
#       其中一個 git pull --rebase --autostash 失敗後會令 index 留低 unmerged（U）狀態，
#       令其他 script 嘅 git commit 直接 fatal：
#         "error: Committing is not possible because you have unmerged files."
#       2026-11-10 實測：10:00 AQHI commit fatal（U finance-news.json）、16:00 push 三次重試全失敗。
#
# 用法：直接執行，或由其他 script 呼叫（冇參數 = 淨係清理並 exit 0）
set -uo pipefail
WORKSPACE="/home/openclaw/.openclaw/workspace"
cd "$WORKSPACE" 2>/dev/null || exit 0

if [ -d "$WORKSPACE/.git/rebase-merge" ] || [ -d "$WORKSPACE/.git/rebase-apply" ]; then
  echo "  🧹 清理殘留 rebase 狀態"
  git rebase --abort >/dev/null 2>&1 || true
fi

UNMERGED=$(git ls-files -u 2>/dev/null | awk '{print $4}' | sort -u)
if [ -n "$UNMERGED" ]; then
  echo "  🧹 清理 unmerged 檔案: $(echo "$UNMERGED" | tr '\n' ' ')"
  for f in $UNMERGED; do
    git checkout HEAD -- "$f" >/dev/null 2>&1 || git rm -f --cached "$f" >/dev/null 2>&1 || true
  done
fi
exit 0
