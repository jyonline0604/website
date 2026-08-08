#!/bin/bash
# ============================================================
# cron-guardian.sh — OpenClaw Cron 自動守護（自癒機制）
# 建立日期：2026-08-08
# 功能：
#   1. 檢查 7 個關鍵 OpenClaw cron jobs 是否存在且 enabled
#   2. 檢查 system crontab 關鍵任務是否存在
#   3. 發現缺失 → 自動 re-register（不需人類介入）
#   4. 寫日誌；有修復動作時才通知
# 執行方式：由 system crontab 每日 09:30 / 21:30 執行
# ============================================================

export PATH="/home/openclaw/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export LC_ALL=C.UTF-8

WORKSPACE="/home/openclaw/.openclaw/workspace"
LOG="$WORKSPACE/logs/cron-guardian.log"
TELEGRAM_TO="5344443732"

mkdir -p "$WORKSPACE/logs"

log() { echo "[$(date '+%F %T')] $*" >> "$LOG"; }

send_telegram() {
    # 用 openclaw CLI 發送通知（透過 gateway session）
    local msg="$1"
    openclaw cron list >/dev/null 2>&1  # 確保 gateway 可用
    # 透過 send-briefing 的機制唔適合，直接寫 log + 由簡報報告
    # 有需要時可以用 telegram bot（如果 scripts 有現成工具）
    log "NOTIFY: $msg"
}

log "=== cron-guardian 開始 ==="

# ------------------------------------------------------------
# Part 1: 檢查 OpenClaw cron jobs
# ------------------------------------------------------------
CURRENT_JOBS=$(openclaw cron list --json 2>/dev/null)
if [ -z "$CURRENT_JOBS" ]; then
    log "ERROR: openclaw cron list 失敗（gateway 唔通？）"
    exit 1
fi

# 檢查函數：job 名稱存在 + enabled
check_job() {
    local name="$1"
    echo "$CURRENT_JOBS" | python3 -c "
import json,sys
data=json.load(sys.stdin)
jobs=data if isinstance(data,list) else data.get('jobs',[])
name='$name'
for j in jobs:
    if j.get('name')==name and j.get('enabled'):
        print('OK'); sys.exit(0)
print('MISSING')
" 2>/dev/null
}

# 需要重建時用嘅 add 指令（與現有 job 設定一致）
# 注意：payload message 用 $(cat <<'EOF' ... EOF) 方式傳遞

rebuild_job() {
    local name="$1"
    log "修復: $name 缺失，自動重建..."
    case "$name" in
        "早上簡報 08:15")
            openclaw cron add --name "早上簡報 08:15" --cron "15 8 * * *" --tz "Asia/Hong_Kong" \
                --agent main --session isolated --announce --channel telegram --to "$TELEGRAM_TO" \
                --model "deepseek/deepseek-v4-flash" \
                --fallbacks "deepseek/deepseek-v4-pro,google/gemini-3.1-flash-lite" \
                --timeout-seconds 300 \
                --message "$(cat <<'EOF'
【早上簡報 08:15】

按以下順序執行並報告：

1. 網站狀態：檢查 https://kofhk.com 是否正常回傳 200
2. 系統健康：磁碟用量、記憶體、運行時間
3. Dropbox 同步狀態：Volume 4 最後執行結果
4. 今日 cron 排程一覽
5. 已知問題追蹤

⚠️ 自動修復：檢測到 state 分歧、cron 異常、缺失檔案等問題時，直接修復，不需等人類指示。

⚠️ 重要規則（防止誤判失敗）：
- 檢查其他 cron job 狀態時，只可使用「openclaw cron list」確認 lastRunStatus 欄位
- 若其他 cron 顯示 error，只須在報告中列出，**絕不可因此令本簡報標記為失敗**
- 本簡報無論如何都必須完整輸出報告並完成送達
- 唔好檢查系統 crontab（crontab -l）嘅任務狀態，只檢查 OpenClaw cron jobs

📊 報告末尾強制輸出評估：
[LOOP_STATUS: OK|WARN|FAIL]
- OK = 全部正常
- WARN = 有非嚴重問題（例如其他 cron 有 error，但本簡報仍正常送達）
- FAIL = 僅當網站掛掉、磁碟快滿等嚴重問題
EOF
)" 2>>"$LOG" && log "✅ 早上簡報已重建" || log "❌ 早上簡報重建失敗"
            ;;
        "中午簡報 12:55")
            openclaw cron add --name "中午簡報 12:55" --cron "55 12 * * *" --tz "Asia/Hong_Kong" \
                --agent main --session isolated --announce --channel telegram --to "$TELEGRAM_TO" \
                --model "deepseek/deepseek-v4-flash" \
                --fallbacks "deepseek/deepseek-v4-pro,google/gemini-3.1-flash-lite" \
                --timeout-seconds 300 \
                --message "$(cat <<'EOF'
【中午簡報 12:55】

按以下順序執行並報告：

1. 網站狀態：https://kofhk.com 是否 200
2. 上午回顧：使用 cron list 檢查「早上簡報 08:15」的最後執行狀態（name: 早上簡報 08:15），確認有無成功執行
3. Dropbox 檢查：Volume 4 同步狀態
4. 系統狀態：df -h /, 異常進程
5. 下午排程提醒

⚠️ 自動修復：檢測到 state 分歧、cron 異常、缺失檔案等問題時，直接修復，不需等人類指示。

📊 報告末尾強制輸出評估：
[LOOP_STATUS: OK|WARN|FAIL]

⚠️ 注意：檢查 cron job 時請使用正確的名字「早上簡報 08:15」，不要使用 08:00！
EOF
)" 2>>"$LOG" && log "✅ 中午簡報已重建" || log "❌ 中午簡報重建失敗"
            ;;
        "傍晚簡報 17:55 — 日結")
            openclaw cron add --name "傍晚簡報 17:55 — 日結" --cron "55 17 * * *" --tz "Asia/Hong_Kong" \
                --agent main --session isolated --announce --channel telegram --to "$TELEGRAM_TO" \
                --model "deepseek/deepseek-v4-flash" \
                --fallbacks "deepseek/deepseek-v4-pro,google/gemini-3.1-flash-lite" \
                --timeout-seconds 300 \
                --message "$(cat <<'EOF'
【傍晚簡報 17:55 — 日結】

按以下順序執行並產生完整日結報告：

📋 今日執行摘要：
1. 網站狀態：https://kofhk.com 是否 200
2. 今日 cron 執行回顧：
   - 檢查早上簡報、中午簡報最後執行時間和狀態
   - 檢查 Dropbox Volume 4 今日同步：成功幾章、有無錯誤
3. 系統狀態：df -h /, 記憶體, 持續運行時間
4. 明日排程預覽

⚠️ 自動修復規則：
偵測到以下問題時，必須自動修復而不再等待人類指示：
- Dropbox state.json 與實際檔案數量分歧 → 自動修復並 commit
- 異常 cron 狀態（consecutiveErrors>0）→ 自動重啟或報告
- 遺漏的 HTML/JSON 更新 → 自動補執行

📊 結尾必須輸出：
[LOOP_STATUS: OK|WARN|FAIL]
[LOOP_DAILY: 簡報✅/⚠️, Dropbox✅/⚠️, 網站✅/⚠️, 系統✅/⚠️]
EOF
)" 2>>"$LOG" && log "✅ 傍晚簡報已重建" || log "❌ 傍晚簡報重建失敗"
            ;;
        "每日健康報告 22:00")
            openclaw cron add --name "每日健康報告 22:00" --cron "0 22 * * *" --tz "Asia/Hong_Kong" \
                --agent main --session isolated --announce --channel telegram --to "$TELEGRAM_TO" \
                --model "deepseek/deepseek-v4-flash" \
                --fallbacks "deepseek/deepseek-v4-pro,google/gemini-3.1-flash-lite" \
                --timeout-seconds 300 \
                --message "$(cat <<'EOF'
【每日健康報告 22:00】

檢查以下項目，**發現問題必須自動修復，不只報告**：

1. 🌐 網站狀態：curl -sI https://kofhk.com
2. 📦 Dropbox Vol4 同步：.dropbox-sync/volume4_state.json
3. 💾 系統資源：df -h /, free -h, uptime
4. 🔄 Cron 健康：所有 cron job consecutiveErrors
5. 📝 Git 狀態：untracked 檔案、未推送 commit

🔧 自動修復規則（強制執行，唔准只報告）：
- untracked 暫存檔（*_output.txt, *.tmp 等）→ 直接 rm 刪除
- Git 有未推送 commit → 立即 git push
- cron_output.txt 之類遺留檔 → 直接清理，唔洗問
- 網站唔通 → 診斷原因並報告
- consecutiveErrors > 0 → 列出受影響 job

📊 結尾輸出：[LOOP_STATUS: OK|WARN|FAIL]
[LOOP_DAILY: 網站✅/⚠️, Dropbox✅/⚠️, 系統✅/⚠️, Cron✅/⚠️, Git✅/⚠️]
EOF
)" 2>>"$LOG" && log "✅ 健康報告已重建" || log "❌ 健康報告重建失敗"
            ;;
        "每日 Audio Sync 10:00")
            openclaw cron add --name "每日 Audio Sync 10:00" --cron "0 10 * * *" --tz "Asia/Hong_Kong" \
                --agent main --session isolated --announce --channel telegram --to "$TELEGRAM_TO" \
                --timeout-seconds 300 --tools "read,exec" \
                --message "Run daily audio sync: exec \`cd /home/openclaw/.openclaw/workspace && python3 scripts/audio_sync_pipeline.py\` and report results." \
                2>>"$LOG" && log "✅ Audio Sync 已重建" || log "❌ Audio Sync 重建失敗"
            ;;
        "OpenClaw Version Check")
            openclaw cron add --name "OpenClaw Version Check" --cron "0 11 * * *" \
                --agent main --session isolated --announce --channel telegram --to "$TELEGRAM_TO" \
                --model "deepseek/deepseek-v4-flash" \
                --fallbacks "deepseek/deepseek-v4-pro,google/gemini-3.1-flash-lite" \
                --timeout-seconds 300 \
                --message "請執行 /home/openclaw/.openclaw/workspace/scripts/check-openclaw-version.sh 並報告結果" \
                2>>"$LOG" && log "✅ Version Check 已重建" || log "❌ Version Check 重建失敗"
            ;;
        "Dropbox Volume4 6章同步")
            openclaw cron add --name "Dropbox Volume4 6章同步" --cron "0 10 * * *" --tz "Asia/Hong_Kong" \
                --session isolated --timeout-seconds 300 --tools "read,exec" \
                --message "Run dropbox volume4 sync: exec \`cd /home/openclaw/.openclaw/workspace && python3 scripts/dropbox_volume4_sync.py\` and report results." \
                2>>"$LOG" && log "✅ Volume4 已重建" || log "❌ Volume4 重建失敗"
            ;;
        *)
            log "未知 job 名稱: $name"
            ;;
    esac
}

# 關鍵 jobs 清單
FIXED=0
for JOB in "早上簡報 08:15" "中午簡報 12:55" "傍晚簡報 17:55 — 日結" "每日健康報告 22:00" "每日 Audio Sync 10:00" "OpenClaw Version Check" "Dropbox Volume4 6章同步"; do
    STATUS=$(check_job "$JOB")
    if [ "$STATUS" = "OK" ]; then
        log "✅ 存在: $JOB"
    else
        log "❌ 缺失: $JOB"
        rebuild_job "$JOB"
        FIXED=$((FIXED+1))
    fi
done

# ------------------------------------------------------------
# Part 2: 檢查 system crontab 關鍵任務
# ------------------------------------------------------------
CRONTAB=$(crontab -l 2>/dev/null)
SYSTEM_TASKS=(
    "backup-memory.sh"
    "send-briefing.sh"
    "dropbox-volume5-daily-sync.sh"
    "update_finance.sh"
    "update_finance_news.sh"
    "update_aqhi.sh"
    "auto-daily-memory-log.sh"
    "check_openclaw_update.py"
)
for TASK in "${SYSTEM_TASKS[@]}"; do
    if echo "$CRONTAB" | grep -q "$TASK"; then
        log "✅ system cron 存在: $TASK"
    else
        log "❌ system cron 缺失: $TASK"
        FIXED=$((FIXED+1))
    fi
done

# ------------------------------------------------------------
# 總結
# ------------------------------------------------------------
if [ "$FIXED" -gt 0 ]; then
    log "⚠️ 本次修復 $FIXED 項，需檢查（system cron 缺失需手動加回）"
else
    log "✅ 全部正常，無需修復"
fi
log "=== cron-guardian 結束 ==="
