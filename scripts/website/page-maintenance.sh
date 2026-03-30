#!/bin/bash
# Wrapper for website page maintenance
# Placeholder for future maintenance tasks

set -e

LOG_FILE="/home/openclaw/.openclaw/workspace/logs/page-maintenance.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 執行網站分頁維護檢查..." >> "$LOG_FILE"

REPO_DIR="/home/openclaw/.openclaw/workspace/my-novel-website"
cd "$REPO_DIR"

# Check for broken links or missing files (basic check)
echo "檢查章節文件完整性..." >> "$LOG_FILE"

MISSING_COUNT=0
for i in {1..52}; do
    if [ ! -f "chapter-$i.html" ] && [ "$i" -le "$(ls chapter-*.html 2>/dev/null | grep -oP 'chapter-\K[0-9]+' | sort -n | tail -1 2>/dev/null || echo 0)" ]; then
        echo "⚠️  第 $i 章文件缺失" >> "$LOG_FILE"
        MISSING_COUNT=$((MISSING_COUNT + 1))
    fi
done

if [ $MISSING_COUNT -eq 0 ]; then
    echo "✅ 所有章節文件完整" >> "$LOG_FILE"
else
    echo "❌ 發現 $MISSING_COUNT 個缺失文件" >> "$LOG_FILE"
fi

# Check if index.html needs update
if [ -f "index.html" ]; then
    echo "✅ index.html 存在" >> "$LOG_FILE"
else
    echo "❌ index.html 缺失" >> "$LOG_FILE"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 維護檢查完成" >> "$LOG_FILE"
