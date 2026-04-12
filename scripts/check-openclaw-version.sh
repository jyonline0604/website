#!/bin/bash
# OpenClaw 版本檢查腳本
# 用途：檢查 OpenClaw 是否有新版本，如有則通知 Telegram

export PATH="/home/openclaw/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

cd /home/openclaw/.openclaw/workspace

# 取得當前安裝版本
CURRENT_VERSION=$(openclaw --version 2>/dev/null | head -1)
echo "=== OpenClaw 版本檢查 ==="
echo "當前版本：$CURRENT_VERSION"
echo "檢查時間：$(date '+%Y-%m-%d %H:%M:%S')"

# 取得 npm 最新版本
LATEST_VERSION=$(npm view openclaw version 2>/dev/null)
echo "最新版本：$LATEST_VERSION"

# 比對版本
if [ "$CURRENT_VERSION" != "$LATEST_VERSION" ]; then
    echo "🎉 有新版本！"
    
    # 發送 Telegram 通知
    MESSAGE="🔔 *OpenClaw 版本通知*

📌 當前版本：$CURRENT_VERSION
🆕 最新版本：$LATEST_VERSION
⏰ 檢查時間：$(date '+%Y-%m-%d %H:%M')

，建議更新！"

    # 使用 curl 發送到 Telegram
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
            -d "chat_id=$TELEGRAM_CHAT_ID" \
            -d "text=$MESSAGE" \
            -d "parse_mode=Markdown" > /dev/null 2>&1
        echo "已發送 Telegram 通知"
    fi
else
    echo "✅ 版本已是最新"
fi

echo "=== 檢查完成 ==="
