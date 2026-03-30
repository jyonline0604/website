#!/bin/bash
# 發送簡報腳本

export PATH="/home/openclaw/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

WORKSPACE="/home/openclaw/.openclaw/workspace"
LOG_FILE="$WORKSPACE/logs/briefing-send.log"

echo "[$(date)] ==================================================" >> "$LOG_FILE"
echo "[$(date)] 開始發送簡報..." >> "$LOG_FILE"

cd "$WORKSPACE" || exit 1

# 生成簡報（使用完整官方數據版 v5）
echo "[$(date)] 使用完整官方數據版 v5 生成簡報..." >> "$LOG_FILE"
BRIEFING=$(python3 "$WORKSPACE/scripts/generate-briefing-full-v5.py" 2>&1)

# 如果官方版 v5 失敗，嘗試官方版 v4
if [ $? -ne 0 ]; then
    echo "[$(date)] 官方版 v5 失敗，嘗試官方版 v4..." >> "$LOG_FILE"
    BRIEFING=$(python3 "$WORKSPACE/scripts/generate-briefing-official-v4-final.py" 2>&1)
fi

# 如果官方版 v4 失敗，嘗試官方版 v3
if [ $? -ne 0 ]; then
    echo "[$(date)] 官方版 v4 失敗，嘗試官方版 v3..." >> "$LOG_FILE"
    BRIEFING=$(python3 "$WORKSPACE/scripts/generate-briefing-official-v3.py" 2>&1)
fi

# 如果官方版 v3 失敗，嘗試官方版 v2
if [ $? -ne 0 ]; then
    echo "[$(date)] 官方版 v3 失敗，嘗試官方版 v2..." >> "$LOG_FILE"
    BRIEFING=$(python3 "$WORKSPACE/scripts/generate-briefing-official-v2.py" 2>&1)
fi

# 如果官方版 v2 失敗，嘗試官方版 v1
if [ $? -ne 0 ]; then
    echo "[$(date)] 官方版 v2 失敗，嘗試官方版 v1..." >> "$LOG_FILE"
    BRIEFING=$(python3 "$WORKSPACE/scripts/generate-briefing-official.py" 2>&1)
fi

# 如果官方版 v1 失敗，嘗試增強版
if [ $? -ne 0 ]; then
    echo "[$(date)] 官方版 v1 失敗，嘗試增強版..." >> "$LOG_FILE"
    BRIEFING=$(python3 "$WORKSPACE/scripts/generate-briefing-enhanced.py" 2>&1)
fi

# 如果增強版失敗，嘗試真實數據版
if [ $? -ne 0 ]; then
    echo "[$(date)] 增強版失敗，嘗試真實數據版..." >> "$LOG_FILE"
    BRIEFING=$(python3 "$WORKSPACE/scripts/generate-briefing-real.py" 2>&1)
fi

# 如果真實數據版也失敗，使用模擬版
if [ $? -ne 0 ]; then
    echo "[$(date)] 真實數據版失敗，使用模擬版..." >> "$LOG_FILE"
    BRIEFING=$(python3 "$WORKSPACE/scripts/generate-briefing.py" 2>&1)
fi

# 檢查是否成功生成
if [ $? -eq 0 ]; then
    echo "[$(date)] 簡報生成成功，長度: ${#BRIEFING} 字符" >> "$LOG_FILE"
    
    # 發送到 Telegram
    echo "[$(date)] 發送到 Telegram..." >> "$LOG_FILE"
    openclaw message send --channel telegram --target 5344443732 --message "$BRIEFING" >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        echo "[$(date)] ✅ 簡報發送成功" >> "$LOG_FILE"
    else
        echo "[$(date)] ❌ 簡報發送失敗" >> "$LOG_FILE"
    fi
else
    echo "[$(date)] ❌ 簡報生成失敗" >> "$LOG_FILE"
    echo "$BRIEFING" >> "$LOG_FILE"
fi

echo "[$(date)] 發送任務完成" >> "$LOG_FILE"