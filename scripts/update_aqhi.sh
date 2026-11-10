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
  PUSH_OK=0
  for ATTEMPT in 1 2 3; do
    if git pull --rebase --autostash origin main >/dev/null 2>&1; then
      if git push origin main >/dev/null 2>&1; then PUSH_OK=1; break; fi
    fi
    echo "[AQHI] push attempt $ATTEMPT failed，10s 後重試..."
    bash "$WORKSPACE/scripts/git-clean-conflicts.sh"
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
