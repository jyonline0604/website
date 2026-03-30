#!/bin/bash
# 第二部章节生成 wrapper（每日 07:00 执行）
set -e
REPO_DIR="/home/openclaw/.openclaw/workspace/my-novel-website"
cd "$REPO_DIR"
LOG_FILE="/home/openclaw/.openclaw/workspace/logs/chapter-generator-part2.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 第二部章节生成开始..." >> "$LOG_FILE"
python3 generate_chapter_part2.py >> "$LOG_FILE" 2>&1
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 第二部章节生成完成" >> "$LOG_FILE"
else
    echo "❌ 第二部章节生成失败 (exit code: $EXIT_CODE)" >> "$LOG_FILE"
fi
exit $EXIT_CODE
