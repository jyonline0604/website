#!/usr/bin/env bash
# OpenRouter API key 更新工具（2026-09-06 小肥喵）
# 用法：sudo -iu openclaw bash /home/openclaw/.openclaw/workspace/scripts/update-openrouter-key.sh
# 流程：貼 key（隱藏輸入）→ 驗證 → 寫入 systemd drop-in + .env → daemon-reload → 重啟 gateway
set -uo pipefail

DROPIN="/home/openclaw/.config/systemd/user/openclaw-gateway.service.d/openrouter-key.conf"
ENVF="/home/openclaw/.openclaw/workspace/.env"

echo "🔑 OpenRouter key 更新工具"
echo "   （取得新 key：https://openrouter.ai/settings/keys）"
read -rsp "貼 OpenRouter API key (sk-or-...)： " K
echo ""

if [ -z "$K" ]; then
  echo "❌ 冇輸入 key，退出"
  exit 1
fi

echo -n "🔍 驗證 key 中... "
CODE=$(curl -s -o /tmp/or-key-check.json -w "%{http_code}" -H "Authorization: Bearer $K" https://openrouter.ai/api/v1/key)
if [ "$CODE" != "200" ]; then
  echo "❌ key 無效（HTTP $CODE）：$(head -c 120 /tmp/or-key-check.json)"
  echo "   冇寫入任何檔案，請檢查 key 再試"
  rm -f /tmp/or-key-check.json
  exit 1
fi
LABEL=$(python3 -c "import json;d=json.load(open('/tmp/or-key-check.json')).get('data',{});print(d.get('label') or '(無標籤)')" 2>/dev/null)
echo "✅ 有效（label: $LABEL）"
rm -f /tmp/or-key-check.json

# 1. 更新 systemd drop-in（整行重寫為標準引號格式）
sed -i "s|^Environment=.*|Environment=\"OPENROUTER_API_KEY=$K\"|" "$DROPIN" \
  && echo "✅ 已更新 drop-in：$DROPIN" \
  || { echo "❌ drop-in 寫入失敗"; exit 1; }

# 2. 更新 workspace .env（ai_multimodel.py 腳本用）
if grep -q "^OPENROUTER_API_KEY=" "$ENVF"; then
  sed -i "s|^OPENROUTER_API_KEY=.*|OPENROUTER_API_KEY=$K|" "$ENVF"
else
  echo "OPENROUTER_API_KEY=$K" >> "$ENVF"
fi
echo "✅ 已更新 .env"

# 3. 重載 + 重啟 gateway（會斷線 ~15 秒）
echo "🔄 daemon-reload + 重啟 gateway（短暫斷線）..."
systemctl --user daemon-reload
systemctl --user restart openclaw-gateway

sleep 8
STATE=$(systemctl --user is-active openclaw-gateway)
if [ "$STATE" = "active" ]; then
  echo "✅ 完成！Gateway 已帶新 key 重啟，OpenRouter fallback 鏈生效："
  echo "   zai/glm-5.3-flash → zai/glm-5.3 → nemotron-3-ultra-550b:free → nemotron-3.5-lightning:free"
else
  echo "⚠️ gateway 狀態：$STATE — 等 30 秒再查：systemctl --user status openclaw-gateway"
fi
