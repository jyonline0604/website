#!/bin/bash
# 更新 AQHI 數據：fetch_aqhi_rss.py → aqhi-stations.json → git push
export PATH="/home/openclaw/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export HOME="/home/openclaw"
WORKSPACE="/home/openclaw/.openclaw/workspace"
cd "$WORKSPACE"
echo "[AQHI] $(date): Running fetch_aqhi_rss.py..."
if ! python3 scripts/fetch_aqhi_rss.py 2>&1; then
  echo "[AQHI] fetch failed — 保留舊數據，唔 commit 空數據"
  exit 0
fi
exec 200>>"$WORKSPACE/.git-push.lock"
flock -w 180 200 || { echo "[AQHI] 拿不到 git 鎖，跳過本次"; exit 0; }

# 2026-11-10 修復：先清走其他 script 殘留嘅衝突／rebase 狀態，
# 否則 git commit 會直接 fatal "unmerged files"（U finance-news.json）
bash "$WORKSPACE/scripts/git-clean-conflicts.sh"

git add aqhi-stations.json
git diff --cached --quiet || {
  if ! git commit -m "docs: update aqhi data $(date +%Y-%m-%d)"; then
    echo "[AQHI] commit 失敗 → 清理衝突狀態後重試一次"
    bash "$WORKSPACE/scripts/git-clean-conflicts.sh"
    git add aqhi-stations.json
    git commit -m "docs: update aqhi data $(date +%Y-%m-%d)" || echo "[AQHI] ⚠️ commit 重試仍失敗，留待下一輪"
  fi
  # 併發 push 競爭防護（2026-09-20 autostash；2026-09-22 改重試循環；
  # 2026-11-10 加強：每次失敗後清理衝突狀態，唔好留低 U 狀態連累其他 script）
  # 2026-11-10 22:xx 再修（真正根因）：舊版將 push 放喺「pull 成功」分支入面，
  #   同一分鐘 finance / finance-news 有未提交改動時 pull --rebase 一定 fail
  #   （cannot pull with rebase: You have unstaged changes）→ push 一次都冇試過
  #   → 報「三次重試仍失敗」，commit 滯留本地，線上 AQHI 停留喺上一個鐘。
  #   修法：① push 獨立嘗試，唔再 gate 喺 pull 上面；② pull 用 -X theirs 自動解衝突；
  #         ③ pull 失敗就 abort 清理 + stash 未提交改動再試；④ 絕不 reset --hard 掉本地 commit。
  PUSH_OK=0
  for ATTEMPT in 1 2 3; do
    bash "$WORKSPACE/scripts/git-clean-conflicts.sh"
    if git pull --rebase -X theirs origin main >/dev/null 2>&1; then
      git push origin main >/dev/null 2>&1 && PUSH_OK=1
    else
      git rebase --abort >/dev/null 2>&1 || true
      if [ -n "$(git status --porcelain)" ]; then
        git stash push -u -m "aqhi-autostash $(date +%Y%m%d-%H%M%S)" >/dev/null 2>&1 || true
        if git pull --rebase -X theirs origin main >/dev/null 2>&1; then
          git push origin main >/dev/null 2>&1 && PUSH_OK=1
        fi
        git stash pop >/dev/null 2>&1 || echo "[AQHI] ⚠️ stash pop 有衝突，改動保留喺 stash"
      else
        git push origin main >/dev/null 2>&1 && PUSH_OK=1
      fi
    fi
    if [ "$PUSH_OK" = "1" ]; then break; fi
    echo "[AQHI] push attempt $ATTEMPT failed，10s 後重試..."
    sleep 10
  done
  if [ "$PUSH_OK" = "1" ]; then
    BEHIND=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo "?")
    [ "$BEHIND" = "0" ] && echo "[AQHI] ✅ push 確認完成（origin/main 已含本次 commit）"                         || echo "[AQHI] ⚠️ push 話成功但仍有 $BEHIND 個 commit 未推"
  else
    echo "[AQHI] ⚠️ push 三次重試仍失敗，留待下一輪自動恢復"
  fi
}
echo "[AQHI] Done"
