#!/bin/bash
# audio-daily-cron.sh — 每日音頻流程（大肥喵2026-07-25定義）
# 流程：Dropbox 搵音頻 → 上傳R2 → 播放器注入 → 驗證
# 若無音頻 → Telegram 通知大肥喵
# 每天 10:00 HKT (system crontab)
set -euo pipefail
export PATH="/home/openclaw/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export HOME="/home/openclaw"
WORKSPACE="/home/openclaw/.openclaw/workspace"
LOG_FILE="$WORKSPACE/.dropbox-sync/audio-cron.log"
STATE_FILE="$WORKSPACE/.dropbox-sync/audio_state.json"
BOT_TOKEN_FILE="$WORKSPACE/.token-store/telegram-bot-token.txt"
# 讀取 Dropbox token，過期則自動 refresh
refresh_dropbox_token() {
  local token_file="$WORKSPACE/.token-store/dropbox-token.txt"
  local creds_file="$WORKSPACE/.token-store/dropbox-app-creds.txt"
  local token
  token=$(cat "$token_file" 2>/dev/null || echo "")
  if [ -z "$token" ]; then
    echo "  ⚠️ Token file empty, can't verify" >> "$LOG_FILE"
    echo "$token"
    return
  fi
  # Test if token is valid (quick metadata check on /.dropbox_never_upload)
  local test_r
  test_r=$(curl -s -o /dev/null -w "%{http_code}" -X POST "https://api.dropboxapi.com/2/files/get_metadata" \
    -H "Authorization: Bearer $token" \
    -H "Content-Type: application/json" \
    -d '{"path":"/"}' 2>/dev/null || echo "000")
  if [ "$test_r" = "200" ]; then
    # Token still valid
    echo "$token"
    return
  fi
  echo "  🔄 Token 過期，嘗試 refresh..." >> "$LOG_FILE"
  # Read app credentials for refresh
  if [ ! -f "$creds_file" ]; then
    echo "  ⚠️ No dropbox-app-creds.txt, can't refresh" >> "$LOG_FILE"
    echo "$token"
    return
  fi
  local app_key refresh_token
  app_key=$(grep '^APP_KEY=' "$creds_file" | cut -d= -f2-)
  refresh_token=$(grep '^REFRESH_TOKEN=' "$creds_file" | cut -d= -f2-)
  if [ -z "$refresh_token" ] || [ -z "$app_key" ]; then
    echo "  ⚠️ Missing APP_KEY or REFRESH_TOKEN in creds" >> "$LOG_FILE"
    echo "$token"
    return
  fi
  local new_token
  new_token=$(curl -s -X POST "https://api.dropboxapi.com/oauth2/token" \
    -d "grant_type=refresh_token" \
    -d "refresh_token=$refresh_token" \
    -d "client_id=$app_key" 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null || echo "")
  if [ -n "$new_token" ]; then
    echo "$new_token" > "$token_file"
    chmod 600 "$token_file"
    echo "  ✅ Token 已刷新" >> "$LOG_FILE"
    echo "$new_token"
  else
    echo "  ❌ Token refresh 失敗" >> "$LOG_FILE"
    echo "$token"
  fi
}
DROPBOX_TOKEN=$(refresh_dropbox_token || true)
CHAT_ID="5344443732"
echo "===== $(date '+%Y-%m-%d %H:%M:%S') =====" >> "$LOG_FILE"
cd "$WORKSPACE"
LAST_CH=$(python3 -c "import json;print(json.load(open('$STATE_FILE'))['last_chapter'])" 2>/dev/null || echo "14")
NEXT_CH=$((LAST_CH + 1))
echo "State: last=$LAST_CH, next=$NEXT_CH" >> "$LOG_FILE"

notify() {
  local msg="$1"
  local token
  token=$(cat "$BOT_TOKEN_FILE" 2>/dev/null || echo "")
  if [ -z "$token" ]; then
    # Self-healing: token file 唔見/空時，自動從 openclaw.json 重建
    token=$(python3 -c "
import json
path = '/home/openclaw/.openclaw/openclaw.json'
try:
    cfg = json.load(open(path))
    print(cfg.get('channels', {}).get('telegram', {}).get('botToken', ''))
except Exception:
    print('')
" 2>/dev/null)
    if [ -n "$token" ]; then
      echo "$token" > "$BOT_TOKEN_FILE"
      chmod 600 "$BOT_TOKEN_FILE"
      echo "[$(date '+%Y-%m-%dT%H:%M:%SZ')] 🔧 Bot token 已從 openclaw.json 自動重建" >> "$LOG_FILE"
    fi
  fi
  [ -n "$token" ] && curl -s -X POST "https://api.telegram.org/bot${token}/sendMessage" \
    -d "chat_id=$CHAT_ID" -d "text=$msg" -d "parse_mode=HTML" >/dev/null 2>&1 || true
}

# [1] 在 Dropbox 找音頻
echo "[1] Searching Dropbox for ch$NEXT_CH audio..." >> "$LOG_FILE"
AUDIO_FOUND=""
# 正確路徑：大肥喵上載到 /萬古塵埃/chapter-{N}.mp3
# 2026-07-26 fix: 之前用錯路徑導致 script 假陰性
for DPATH in "/萬古塵埃/chapter-$NEXT_CH.mp3" "/萬古塵埃/第二卷/audio/chapter-$NEXT_CH.mp3" "/audio/chapter-$NEXT_CH.mp3"; do
  R=$(curl -s -X POST "https://api.dropboxapi.com/2/files/get_metadata" \
    -H "Authorization: Bearer $DROPBOX_TOKEN" -H "Content-Type: application/json" \
    -d "{\"path\":\"$DPATH\"}" 2>&1)
  if echo "$R" | grep -q '"name"'; then AUDIO_FOUND="$DPATH"; break; fi
done
if [ -z "$AUDIO_FOUND" ]; then
  SR=$(curl -s -X POST "https://api.dropboxapi.com/2/files/search_v2" \
    -H "Authorization: Bearer $DROPBOX_TOKEN" -H "Content-Type: application/json" \
    -d "{\"query\":\"chapter-$NEXT_CH.mp3\",\"path\":\"/\"}" 2>&1)
  MATCH=$(echo "$SR" | python3 -c "
import sys,json
try:
  d=json.load(sys.stdin)
  for m in d.get('matches',[]):
    p=m.get('metadata',{}).get('metadata',{}).get('path_display','')
    if p: print(p); break
except: pass
" 2>/dev/null)
  [ -n "$MATCH" ] && AUDIO_FOUND="$MATCH"
fi
if [ -z "$AUDIO_FOUND" ]; then
  echo "  ✗ ch$NEXT_CH audio not in Dropbox. Notifying user..." >> "$LOG_FILE"
  notify "🎧 ch${NEXT_CH} 音頻未上傳 — Dropbox 搵唔到 chapter-${NEXT_CH}.mp3"
  echo "===== NO AUDIO =====" >> "$LOG_FILE"; exit 0
fi
echo "  ✓ Found: $AUDIO_FOUND" >> "$LOG_FILE"

# [2] 下載並上傳到 R2
echo "[2] Uploading $AUDIO_FOUND → R2..." >> "$LOG_FILE"
TMP="/tmp/chapter-$NEXT_CH.mp3"
curl -s -X POST "https://content.dropboxapi.com/2/files/download" \
  -H "Authorization: Bearer $DROPBOX_TOKEN" \
  -H "Dropbox-API-Arg: {\"path\":\"$AUDIO_FOUND\"}" -o "$TMP" 2>&1 >> "$LOG_FILE"
if [ ! -s "$TMP" ]; then
  notify "🎧 ch${NEXT_CH} 音頻下載失敗 — Dropbox download error"
  echo "  ✗ Download failed" >> "$LOG_FILE"; exit 1
fi
python3 scripts/upload_audio_r2.py "$TMP" "chapter-$NEXT_CH.mp3" 2>&1 >> "$LOG_FILE"
rm -f "$TMP"
echo "  ✓ R2 upload done" >> "$LOG_FILE"

# [3] 注入播放器
echo "[3] Injecting audio player into chapter-$NEXT_CH.html..." >> "$LOG_FILE"
python3 scripts/inject_audio_player.py "$NEXT_CH" 2>&1 >> "$LOG_FILE"
echo "  ✓ Player injected" >> "$LOG_FILE"

# [4] 驗證
echo "[4] Verifying..." >> "$LOG_FILE"
P=$(grep -c '<audio' "chapter-$NEXT_CH.html" 2>/dev/null || echo "0")
R=$(curl -sI "https://audio.kofhk.com/audio/chapter-$NEXT_CH.mp3" | head -1 | grep -c "200" || echo "0")
if [ "$P" -gt 0 ] && [ "$R" -gt 0 ]; then
  echo "  ✓ ch$NEXT_CH verified: player=$P R2=200" >> "$LOG_FILE"
  python3 -c "
import json
s=json.load(open('$STATE_FILE'))
s['last_chapter']=$NEXT_CH
s['total_processed']=s.get('total_processed',0)+1
s['last_sync']='$(date -u +%Y-%m-%dT%H:%M:%S)'
json.dump(s,open('$STATE_FILE','w'),indent=2)
" 2>&1 >> "$LOG_FILE"
else
  notify "🎧 ch${NEXT_CH} 音頻驗證失敗 — player=$P R2=$R"
  echo "  ✗ Verify failed: player=$P R2=$R" >> "$LOG_FILE"
fi

# Git push
echo "[+] Git push..." >> "$LOG_FILE"
git add -A && git diff --cached --quiet || git commit -m "chore: audio ch$NEXT_CH $(date +%Y-%m-%d)"
git push origin main 2>&1 >> "$LOG_FILE"
echo "===== COMPLETE =====" >> "$LOG_FILE"
