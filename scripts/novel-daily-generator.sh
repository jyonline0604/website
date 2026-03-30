#!/bin/bash
# 每日小說章節生成腳本（多模型版本）
# 使用備用策略：DeepSeek → MiniMax → OpenRouter → Gemini → 本地模板

# 載入環境變量
set -a
source /home/openclaw/.openclaw/workspace/.env
set +a

# 設置完整 PATH（Cron 需要）
export PATH="/home/openclaw/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

WORKSPACE="/home/openclaw/.openclaw/workspace"
NOVEL_DIR="$WORKSPACE/my-novel"
LOG_FILE="$WORKSPACE/logs/novel-daily.log"

echo "==========================================================" >> "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 開始多模型每日章節生成..." >> "$LOG_FILE"

cd "$WORKSPACE" || exit 1

# 執行多模型章節生成器
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 執行多模型生成器..." >> "$LOG_FILE"
python3 "$WORKSPACE/scripts/novel_generator_multimodel.py" --daily >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 多模型生成成功" >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 多模型生成失敗，退出碼: $EXIT_CODE" >> "$LOG_FILE"
    
    # 嘗試備用方案
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 嘗試備用方案..." >> "$LOG_FILE"
    
    # 備用1: 使用簡單生成器
    python3 "$WORKSPACE/scripts/generate_novel_chapter_simple.py" >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 備用方案成功" >> "$LOG_FILE"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 所有方案都失敗" >> "$LOG_FILE"
    fi
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 生成任務完成" >> "$LOG_FILE"
echo "==========================================================" >> "$LOG_FILE"

# 返回最後的退出碼
exit $EXIT_CODE