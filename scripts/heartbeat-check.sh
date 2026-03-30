#!/bin/bash
# Heartbeat check script
# 心跳檢查 - 驗證系統正常運行

set -e

LOG_FILE="/home/openclaw/.openclaw/workspace/logs/heartbeat.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 心跳檢查開始..." >> "$LOG_FILE"

# 檢查目錄是否存在
DIRS=(
    "/home/openclaw/.openclaw/workspace/my-novel-website"
    "/home/openclaw/.openclaw/workspace/logs"
    "/home/openclaw/.openclaw/workspace/scripts"
)

for DIR in "${DIRS[@]}"; do
    if [ -d "$DIR" ]; then
        echo "✅ 目錄存在: $DIR" >> "$LOG_FILE"
    else
        echo "❌ 目錄缺失: $DIR" >> "$LOG_FILE"
    fi
done

# 檢查關鍵文件
FILES=(
    "/home/openclaw/.openclaw/workspace/my-novel-website/index.html"
    "/home/openclaw/.openclaw/workspace/my-novel-website/style.css"
    "/home/openclaw/.openclaw/workspace/my-novel-website/main.js"
)

for FILE in "${FILES[@]}"; do
    if [ -f "$FILE" ]; then
        echo "✅ 文件存在: $(basename $FILE)" >> "$LOG_FILE"
    else
        echo "❌ 文件缺失: $(basename $FILE)" >> "$LOG_FILE"
    fi
done

# 檢查章節數量
CHAPTER_COUNT=$(ls -1 /home/openclaw/.openclaw/workspace/my-novel-website/chapter-*.html 2>/dev/null | wc -l)
echo "📚 當前章節總數: $CHAPTER_COUNT" >> "$LOG_FILE"

# 檢查最近一次自動更新的時間
if [ -f "/home/openclaw/.openclaw/workspace/logs/novel-update.log" ]; then
    LAST_UPDATE=$(stat -c %Y "/home/openclaw/.openclaw/workspace/logs/novel-update.log")
    LAST_UPDATE_STR=$(date -d @$LAST_UPDATE '+%Y-%m-%d %H:%M:%S')
    echo "🕐 最後自動更新: $LAST_UPDATE_STR" >> "$LOG_FILE"
else
    echo "⚠️  自動更新日誌不存在" >> "$LOG_FILE"
fi

# 檢查磁盤空間（可選）
DISK_USAGE=$(df -h /home/openclaw | awk 'NR==2 {print $5}')
echo "💾 磁盤使用率: $DISK_USAGE" >> "$LOG_FILE"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 心跳檢查完成" >> "$LOG_FILE"
