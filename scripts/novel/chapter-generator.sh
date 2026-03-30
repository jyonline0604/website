#!/bin/bash
# 章節生成腳本 - 每日07:00自動生成新章節並推送到GitHub
# 調用 generate_chapter.py 進行智能生成

LOG_FILE="/home/openclaw/.openclaw/workspace/logs/chapter-generator.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ========== 開始自動生成章節 ==========" >> "$LOG_FILE"

# 執行智能章節生成器 (包含 GitHub push)
cd /home/openclaw/.openclaw/workspace/my-novel-website
python3 generate_chapter.py >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ========== 章節生成完成 ==========" >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ========== 章節生成失敗 (exit: $EXIT_CODE) ==========" >> "$LOG_FILE"
fi

exit 0
