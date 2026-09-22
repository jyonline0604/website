#!/bin/bash
# 更新 AQHI 數據：fetch_aqhi_rss.py → aqhi-stations.json → git push
export PATH="/home/openclaw/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export HOME="/home/openclaw"
WORKSPACE="/home/openclaw/.openclaw/workspace"
cd "$WORKSPACE"
echo "[AQHI] $(date): Running fetch_aqhi_rss.py..."
if ! python3 scripts/fetch_aqhi_rss.py 2>&1; then
  echo "[AQHI] fetch failed (exit $?) — 保留舊數據，唔 commit 空數據"
  exit 0
fi
git add aqhi-stations.json
git diff --cached --quiet || {
  git commit -m "docs: update aqhi data $(date +%Y-%m-%d)"
  # 併發 push 競爭防護（2026-09-20 autostash；2026-09-22 改重試循環：16:00 財經 job 同分鐘寫 finance-news.json，
  # 單次 autostash 剛 stash 完又見新改動 → abort。3 次重試 + 10s 等待大機率避開競賽窗口）
  PUSH_OK=0
  for ATTEMPT in 1 2 3; do
    if git pull --rebase --autostash origin main >/dev/null 2>&1; then
      if git push origin main >/dev/null 2>&1; then PUSH_OK=1; break; fi
    fi
    echo "[AQHI] push attempt $ATTEMPT failed，10s 後重試..."
    sleep 10
  done
  [ "$PUSH_OK" = "1" ] || echo "[AQHI] ⚠️ push 三次重試仍失敗，留待下一輪自動恢復"
}
echo "[AQHI] Done"
