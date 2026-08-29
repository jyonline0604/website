#!/bin/bash
# ============================================================
# news-backup-cron.sh — AI 新聞本地後備更新
# 背景：GitHub Actions「每日自動更新數據」schedule 曾多次冇觸發
#       （2026-08-27、2026-08-29），導致 news.html 停更一日。
# 功能：檢查 news-data.json 嘅 lastUpdate 是否為「今日」；
#       唔係今日 → 本地跑 update_data.py 補更新 + push。
#       係今日 → 靜默退出（GitHub Actions 已正常運作）。
# 用法：crontab: 10 9,15,21 * * * 此script
# ============================================================
export PATH="/home/openclaw/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
set -uo pipefail

cd /home/openclaw/.openclaw/workspace || exit 1
LOG="logs/news-backup-cron.log"
mkdir -p logs

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] $*" >> "$LOG"; }

# 1. 檢查 lastUpdate 是否今日（HKT）
TODAY_HKT=$(TZ=Asia/Hong_Kong date '+%Y-%m-%d')
LAST_UPDATE=$(python3 -c "
import json
try:
    d = json.load(open('news-data.json'))
    print(d.get('lastUpdate', ''))
except Exception:
    print('')
" 2>/dev/null)

if [ -z "$LAST_UPDATE" ]; then
    log "⚠️ 無法讀取 news-data.json lastUpdate，強制更新"
elif [[ "$LAST_UPDATE" == "$TODAY_HKT"* ]]; then
    log "✅ 數據已係今日（$LAST_UPDATE），GitHub Actions 正常，無需後備"
    exit 0
else
    log "⚠️ 數據停留喺 $LAST_UPDATE（今日=$TODAY_HKT），觸發本地後備更新"
fi

# 2. 本地跑更新（最多重試 3 次）
ok=0
for i in 1 2 3; do
    log "🔄 第 $i 次執行 update_data.py..."
    if python3 update_data.py >> "$LOG" 2>&1; then
        ok=1
        break
    fi
    sleep 10
done

if [ "$ok" -ne 1 ]; then
    log "❌ 3 次重試均失敗，放棄（等待下個排程）"
    exit 1
fi

# 3. 重新生成 sitemap + RSS
python3 scripts/generate_sitemap.py >> "$LOG" 2>&1
python3 scripts/generate_rss.py >> "$LOG" 2>&1

# 4. 有變更先 commit（避免無變更時產生空 commit）
if git diff --quiet -- 'news-data.json' 'finance-news.json' 'finance-data.json' 'sitemap.xml' 'feed.xml'; then
    log "📭 更新完成但無檔案變更"
    exit 0
fi

# 5. 提交 + 推送（先 rebase 避免 remote 有新 commit）
git add news-data.json finance-news.json finance-data.json sitemap.xml feed.xml
git commit -m "📅 本地後備：每日自動更新新聞、市場數據、sitemap 與 RSS ($(TZ=Asia/Hong_Kong date '+%Y-%m-%d %H:%M HKT'))" >> "$LOG" 2>&1

if git pull --rebase origin main >> "$LOG" 2>&1; then
    git push origin main >> "$LOG" 2>&1 && log "✅ 推送成功"
else
    log "⚠️ rebase/push 失敗，稍後 cron-guardian 會再檢查"
    exit 1
fi

log "✅ 本地後備更新完成"
