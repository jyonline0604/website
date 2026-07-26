#!/bin/bash
# 更新 AQHI 數據：fetch_aqhi_rss.py → aqhi-stations.json → git push
export PATH="/home/openclaw/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export HOME="/home/openclaw"
WORKSPACE="/home/openclaw/.openclaw/workspace"
cd "$WORKSPACE"
echo "[AQHI] $(date): Running fetch_aqhi_rss.py..."
python3 scripts/fetch_aqhi_rss.py 2>&1 || echo "fetch_aqhi_rss.py failed"
git add aqhi-stations.json
git diff --cached --quiet || {
  git commit -m "docs: update aqhi data $(date +%Y-%m-%d)"
  git push origin main 2>&1 || true
}
echo "[AQHI] Done"
