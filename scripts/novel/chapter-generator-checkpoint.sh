#!/bin/bash
# Wrapper for novel chapter generation with checkpoint support
# Calls the generate_chapter_checkpoint.sh.direct script

set -e

REPO_DIR="/home/openclaw/.openclaw/workspace/my-novel-website"
cd "$REPO_DIR"

LOG_FILE="/home/openclaw/.openclaw/workspace/logs/chapter-generator.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 開始生成新章節（檢查點模式）..." >> "$LOG_FILE"

# Check if checkpoint script exists
if [ -f "generate_chapter_checkpoint.sh.direct" ]; then
    # 確保檢查點目錄存在
    mkdir -p checkpoints
    
    # 執行檢查點版本的小说生成
    bash generate_chapter_checkpoint.sh.direct >> "$LOG_FILE" 2>&1
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo "✅ 章節生成完成（檢查點模式）" >> "$LOG_FILE"
    else
        echo "❌ 章節生成失敗 (exit code: $EXIT_CODE)" >> "$LOG_FILE"
    fi
    
    exit $EXIT_CODE
else
    echo "❌ 錯誤: generate_chapter_checkpoint.sh.direct 不存在" >> "$LOG_FILE"
    exit 1
fi
