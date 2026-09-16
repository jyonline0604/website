#!/bin/bash
# Dropbox token auto-renew wrapper
# 由 system cron 每 3hr 跑一次（token ~4hr 過期，3hr cron 避免 09-11/09-12 過期慘劇重演）

set -uo pipefail

export PATH="/home/openclaw/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

WORKSPACE="/home/openclaw/.openclaw/workspace"
SCRIPT="$WORKSPACE/scripts/renew_dropbox_token.py"
LOG_FILE="$WORKSPACE/logs/cron-token-renewal.log"
NOTIFY_TG="5344443732"

if [ ! -f "$SCRIPT" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S %z')] 搵唔到 script: $SCRIPT" | tee -a "$LOG_FILE"
    exit 1
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S %z')] 開始 Dropbox token auto-renew..." | tee -a "$LOG_FILE"

# 跑 Python script，timeout 60s
timeout 60 python3 "$SCRIPT" "$@"
RC=$?

if [ $RC -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S %z')] token renew 成功" | tee -a "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S %z')] token renew 失敗 exit=$RC" | tee -a "$LOG_FILE"
    # 簡單 Telegram 通知（如果 mosi key 有嘅話）
    if [ -f "$WORKSPACE/.token-store/mosi-api-key.txt" ]; then
        MOSI_KEY=$(cat "$WORKSPACE/.token-store/mosi-api-key.txt" 2>/dev/null)
        curl -s -m 5 -X POST "https://api.mosi.ai/v1/notify" \
            -H "Authorization: Bearer $MOSI_KEY" \
            -H "Content-Type: application/json" \
            -d "{\"chat_id\":\"$NOTIFY_TG\",\"text\":\"⚠️ Dropbox token auto-renew 失敗 exit=$RC\"}" \
            > /dev/null 2>&1 || true
    fi
fi

exit $RC
