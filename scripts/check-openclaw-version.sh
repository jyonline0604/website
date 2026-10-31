#!/bin/bash
# OpenClaw 版本檢查腳本
# 用途：檢查 OpenClaw 是否有新版本，如有則通知 Telegram

# 2026-09-20: gateway 已改用 nvm node24 安裝（2026.9.5）；舊 ~/.npm-global 係孤兒（2026.9.2），唔可以排先，否則誤報有更新
# 2026-10-31: 唔好硬編碼 nvm node 路徑（升級後舊 install 會殘留，令版本檢查報錯版本）
# 動態搵「有 openclaw 安裝」嘅最新 node 目錄
_OC_NODE_BIN=""
for _d in $(ls -d /home/openclaw/.nvm/versions/node/v*/ 2>/dev/null | sort -V -r); do
  if [ -x "${_d}bin/openclaw" ]; then _OC_NODE_BIN="${_d}bin"; break; fi
done
export PATH="${_OC_NODE_BIN:-/home/openclaw/.nvm/versions/node/v24.22.2/bin}:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

cd /home/openclaw/.openclaw/workspace

# 取得當前安裝版本（完整輸出含 hash）
CURRENT_VERSION_FULL=$(openclaw --version 2>/dev/null | head -1)
# 提取版本號：OpenClaw 2026.5.22 (a374c3a) → 2026.5.22
CURRENT_VERSION=$(echo "$CURRENT_VERSION_FULL" | grep -oP '\d+\.\d+\.\d+' | head -1)
echo "=== OpenClaw 版本檢查 ==="
echo "當前版本：$CURRENT_VERSION_FULL"
echo "檢查時間：$(date '+%Y-%m-%d %H:%M:%S')"

# 取得 npm 最新版本
LATEST_VERSION=$(npm view openclaw version 2>/dev/null)
echo "最新版本：$LATEST_VERSION"

# 比對版本（只比較數字部分）
if [ -n "$CURRENT_VERSION" ] && [ "$CURRENT_VERSION" != "$LATEST_VERSION" ]; then
    echo "🎉 有新版本！"
    
    # 發送 Telegram 通知
    MESSAGE="🔔 【OpenClaw 版本通知】

📌 當前版本：$CURRENT_VERSION_FULL
🆕 最新版本：$LATEST_VERSION
⏰ 檢查時間：$(date '+%Y-%m-%d %H:%M')

，建議更新！"
    # 2026-10-25 修復：cron 環境無 TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID -> 舊 curl 路徑由安裝以來從來冇發出過（版本通知一直要人手轉發）。
    # 改用 openclaw CLI（與 send-briefing.sh 一致，憑證由 OpenClaw config 處理），curl 保留作後備。
    if openclaw message send --channel telegram --target 5344443732 --message "$MESSAGE" > /dev/null 2>&1; then
        echo "已發送 Telegram 通知（openclaw CLI）"
    elif [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
            -d "chat_id=$TELEGRAM_CHAT_ID" \
            -d "text=$MESSAGE" \
            -d "parse_mode=Markdown" > /dev/null 2>&1
        echo "已發送 Telegram 通知（curl 後備）"
    else
        echo "⚠️ Telegram 通知未送出（CLI 與 env 兩條路都失敗）"
    fi
else
    echo "✅ 版本已是最新"
fi

echo "=== 檢查完成 ==="
