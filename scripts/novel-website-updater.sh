#!/bin/bash
# Wrapper for novel website updater
# Calls the daily_page_updater.sh script

set -e

REPO_DIR="/home/openclaw/.openclaw/workspace/my-novel-website"
cd "$REPO_DIR"

LOG_FILE="/home/openclaw/.openclaw/workspace/logs/novel-update.log"

echo "=== 小說網站自動更新開始 ($(date '+%Y-%m-%d %H:%M:%S')) ===" >> "$LOG_FILE"

# Check if updater script exists
if [ -f "auto-update-scripts/daily_page_updater.sh" ]; then
    bash auto-update-scripts/daily_page_updater.sh >> "$LOG_FILE" 2>&1
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo "✅ 小說網站自動更新完成" >> "$LOG_FILE"
    else
        echo "❌ 小說網站自動更新失敗 (exit code: $EXIT_CODE)" >> "$LOG_FILE"
    fi
    
    exit $EXIT_CODE
else
    echo "❌ 錯誤: daily_page_updater.sh 不存在" >> "$LOG_FILE"
    exit 1
fi
