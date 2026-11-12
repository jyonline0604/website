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

# 2026-10-01: gateway 已改用 nvm node24 安裝；舊 ~/.npm-global CLI（schema15）讀唔到 schema17 數據庫，唔可以排先
# 2026-10-31: 唔好硬編碼 nvm node 路徑（升級後舊 install 會殘留，令版本檢查報錯版本）
# 動態搵「有 openclaw 安裝」嘅最新 node 目錄
_OC_NODE_BIN=""
for _d in $(ls -d /home/openclaw/.nvm/versions/node/v*/ 2>/dev/null | sort -V -r); do
  if [ -x "${_d}bin/openclaw" ]; then _OC_NODE_BIN="${_d}bin"; break; fi
done
export PATH="${_OC_NODE_BIN:-/home/openclaw/.nvm/versions/node/v24.22.2/bin}:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export LC_ALL=C.UTF-8

WORKSPACE="/home/openclaw/.openclaw/workspace"
LOG="$WORKSPACE/logs/cron-guardian.log"
TELEGRAM_TO="5344443732"
# 2026-11-12 修正：每條 fallback 必須綁同 provider 配對嘅 account（@openrouter:default），
# 否則 fallback 切去 openrouter 會觸發「Automation candidate is incompatible with its recorded
# inference account and route」hard-fail（2026-11-12 08:15 早上簡報就係咁死咗，errs=1、delivery=unknown）。
# 教訓：fallback 值一定要帶 @profile 綁定，唔可以淨係寫 provider/model。
# 2026-11-11 修正：原本呢度寫 --fallbacks \"minimax/MiniMax-M3.1-Flash@minimax:cn\"（自我指向 = 等於冇 fallback），
# 令 12:55 中午簡報喺 429 限流時重試 9 次後放棄、靜靜冇送達。
# 而家改用 agents.defaults.model.fallbacks 同一條鏈（全部 openrouter free、Auth: yes、喺 modelPolicy allow 清單入面）。
FALLBACKS="openrouter/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free@openrouter:default,openrouter/cohere/north-mini-code:free@openrouter:default,openrouter/nvidia/nemotron-3-ultra-550b-a55b:free@openrouter:default,openrouter/poolside/laguna-s-2.1:free@openrouter:default,openrouter/recursive/flint-v1.0:free@openrouter:default"

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
                --fallbacks "$FALLBACKS" \ \
                --model "minimax/MiniMax-M3.1-Flash@minimax:cn" \
                --timeout-seconds 3600 \
                --message "$(cat <<'EOF'
【早上簡報 08:15】

📰 天氣/交通 digest（必須包含）：先用 1 次 exec 執行
`python3 /home/openclaw/.openclaw/workspace/scripts/generate-briefing-full-v5.py\`
（約 6 秒，stdout 就係完整「📰 香港簡報」digest），將輸出原樣貼喺報告**最前面**
（【天氣】【天氣警告】【預報】【展望】【特別交通消息】【港鐵列車到站】【娛樂】【科技】【財經】）。
若加埋下面內容會超過 3600 字，digest 只保留【天氣】【天氣警告】【預報】【特別交通消息】【港鐵列車到站】五段。

按以下順序執行並報告：

1. 網站狀態：檢查 https://kofhk.com 是否正常回傳 200
2. 系統健康：磁碟用量、記憶體、運行時間
3. Dropbox 同步狀態：Volume 4 最後執行結果
4. 今日 cron 排程一覽
5. 已知問題追蹤

⚠️ 自動修復：檢測到 state 分歧、cron 異常、缺失檔案等問題時，直接修復，不需等人類指示。

⚠️ 重要規則（防止誤判失敗）：
- 檢查 cron 狀態必須用 exec 執行「openclaw cron list --json」或「crontab -l」，**唔好用 cron tool**（isolated session 有 scoping，只顯示自己，會誤判其他 jobs 消失）
- 記憶備份 08:00/20:00、Volume 5 Dropbox 11:00、財經 09/15/21 都係 **system cron（crontab -l）**，唔會出現喺 OpenClaw cron list——見到佢哋喺 crontab 就係正常
- 2026-11-01 起 system cron 簡報（send-briefing.sh）已退休，天氣 digest 併入本簡報；**唔好再報告「雙軌簡報」問題**
- 若其他 cron 顯示 error，只須在報告中列出，**絕不可因此令本簡報標記為失敗**
- 本簡報無論如何都必須完整輸出報告並完成送達

📊 報告末尾強制輸出評估：
[LOOP_STATUS: OK|WARN|FAIL]
- OK = 全部正常
- WARN = 有非嚴重問題（例如其他 cron 有 error，但本簡報仍正常送達）
- FAIL = 僅當網站掛掉、磁碟快滿等嚴重問題
⚠️ 執行方式（2026-11-11 修正）：code mode 入面只有直接注入嘅全域，exec 要寫 exec({command: ...})
或用 shell 腳本；**唔好寫 tools.exec(...)**（會 ReferenceError，令成個 run 白撞到 LLM idle timeout）。
檢查 cron 狀態用 exec 執行 openclaw cron list --json。
EOF
)" 2>>"$LOG" && log "✅ 早上簡報已重建" || log "❌ 早上簡報重建失敗"
            ;;
        "中午簡報 12:55")
            openclaw cron add --name "中午簡報 12:55" --cron "55 12 * * *" --tz "Asia/Hong_Kong" \
                --agent main --session isolated --announce --channel telegram --to "$TELEGRAM_TO" \
                --fallbacks "$FALLBACKS" \ \
                --model "minimax/MiniMax-M3.1-Flash@minimax:cn" \
                --timeout-seconds 3600 \
                --message "$(cat <<'EOF'
【中午簡報 12:55】

⚠️ 執行效率規則（因 2026-10-22 12:55 曾超時 20 分鐘）：全程**只做 1-2 次 exec**（用一條 bash 指令一次過收集所有資料），之後最多只准再讀 1-2 個細節。唔准逐項分開 call 工具。所有外部指令加 timeout 20 保護。

📋 執行步驟：
1. 一次 exec 收集：
   - curl -s -o /dev/null -w "%{http_code}" -m 15 https://kofhk.com
   - openclaw cron list --json（用 --timeout 15000 或直接解析 state）
   - crontab -l
   - tail 各同步 log（dropbox-volume5-sync.log、dropbox-volume6-sync.log、dropbox-volume7-sync.log）
   - df -h /; free -h; uptime; ps -eo pid,pcpu,pmem,etime,comm --sort=-pmem | head -8
2. 從上面輸出整理報告（唔需要再讀檔案）。
3. 檢查 Dropbox state：.dropbox-sync/volume5_state.json、volume6_state.json、volume7_state.json vs assets/chapters-data.json 章節數。分歧 → 自動修復並 git commit。⚠️ 檢查線上章節數一定要加 cache-buster：curl -s "https://kofhk.com/assets/chapters-data.json?v=$(date +%s)"（無 cache-buster 會攞到 Cloudflare 舊快取，落後 6 章，會誤判為分歧）
4. 有 consecutiveErrors>0 → 報告根因；可用 openclaw cron edit 調整（timeout-seconds 或精簡 message）。
5. git 未推送 commit → 自動 git push。

⚠️ 檢查 cron job 時請使用正確的名字「早上簡報 08:15」，不要使用 08:00！
⚠️ 檢查 cron 狀態必須用 exec 執行「openclaw cron list --json」或「crontab -l」，**絕對唔好用 cron tool**（isolated session 有 scoping，只顯示自己 agent 嘅 job，會誤判其他 jobs 消失！）
⚠️ 以下任務係 **system cron（crontab -l）**，唔會出現喺 OpenClaw cron list：記憶備份 08:00/20:00、Volume 4/5/6 Dropbox 11:00、財經 10:00/16:00、AQHI 10:00/16:00、新聞備份 10:10/16:10、cron-guardian 09:30/21:30、Dropbox token 續期每 3 小時、OpenClaw 版本檢查 11:00、自動記憶 23:00 —— 見到佢哋喺 crontab 就係正常，**唔係消失**！
- 2026-11-01 起 system cron 簡報（send-briefing.sh）已退休，天氣 digest 併入早上/傍晚簡報；**唔好再報告「雙軌簡報」問題**

📊 報告末尾強制輸出評估：
[LOOP_STATUS: OK|WARN|FAIL]
⚠️ 執行方式（2026-11-11 修正）：code mode 入面只有直接注入嘅全域，exec 要寫 exec({command: ...})
或用 shell 腳本；**唔好寫 tools.exec(...)**（會 ReferenceError，令成個 run 白撞到 LLM idle timeout）。
檢查 cron 狀態用 exec 執行 openclaw cron list --json。
EOF
)" 2>>"$LOG" && log "✅ 中午簡報已重建" || log "❌ 中午簡報重建失敗"
            ;;
        "傍晚簡報 17:55 — 日結")
            openclaw cron add --name "傍晚簡報 17:55 — 日結" --cron "55 17 * * *" --tz "Asia/Hong_Kong" \
                --agent main --session isolated --announce --channel telegram --to "$TELEGRAM_TO" \
                --fallbacks "$FALLBACKS" \ \
                --model "minimax/MiniMax-M3.1-Flash@minimax:cn" \
                --timeout-seconds 3600 \
                --message "$(cat <<'EOF'
【傍晚簡報 17:55 — 日結】

⚠️ 執行效率規則（因之前 5 次超時）：全程**只做 2 次 exec**（1 次跑天氣 digest 腳本 + 1 次用一個 bash 指令一次過收集所有系統資料），之後最多只准再讀 1-2 個細節。唔准逐項分開 call 工具。所有外部指令加 timeout 20 保護。

📰 天氣/交通 digest（必須包含）：先用 1 次 exec 執行
`python3 /home/openclaw/.openclaw/workspace/scripts/generate-briefing-full-v5.py\`
（約 6 秒，stdout 就係完整「📰 香港簡報」digest），將輸出原樣貼喺報告**最前面**
（【天氣】【天氣警告】【預報】【展望】【特別交通消息】【港鐵列車到站】【娛樂】【科技】【財經】）。
若加埋下面內容會超過 3600 字，digest 只保留【天氣】【天氣警告】【預報】【特別交通消息】【港鐵列車到站】五段。

📋 執行步驟：
1. 一次 exec 收集：
   - curl -s -o /dev/null -w "%{http_code}" -m 15 https://kofhk.com
   - openclaw cron list --json（用 --timeout 15000 或直接解析 state）
   - crontab -l
   - tail 各同步 log（dropbox-volume5-sync.log、dropbox-volume6-sync.log、dropbox-volume7-sync.log）
   - df -h /; free -h; uptime
2. 從上面輸出整理報告（唔需要再讀檔案）。
3. 檢查 Dropbox state：.dropbox-sync/volume5_state.json、volume6_state.json、volume7_state.json vs assets/chapters-data.json 章節數。分歧 → 自動修復並 git commit。⚠️ 檢查線上章節數一定要加 cache-buster：curl -s "https://kofhk.com/assets/chapters-data.json?v=$(date +%s)"（無 cache-buster 會攞到 Cloudflare 舊快取，落後 6 章，會誤判為分歧）
4. 有 consecutiveErrors>0 → 報告根因；可用 openclaw cron edit 調整（timeout-seconds 0 或精簡 message）。
5. git 未推送 commit → 自動 git push。

⚠️ 檢查 cron 狀態必須用 exec 執行「openclaw cron list --json」或「crontab -l」，**絕對唔好用 cron tool**（isolated session 有 scoping）。
⚠️ 以下係 system cron（crontab -l），唔會出現喺 openclaw cron list：記憶備份 08:00/20:00、Volume 5/6 Dropbox 11:00、Volume 7 11:30、財經 10/16、AQHI 10/16、token 續期、新聞備份 10:10/16:10、guardian 09:30/21:30、版本檢查 11:00、自動記憶 23:00 —— 見到即正常，唔係消失。
- 2026-11-01 起 system cron 簡報（send-briefing.sh）已退休，天氣 digest 併入本簡報；**唔好再報告「雙軌簡報」問題**

📊 結尾輸出：
[LOOP_STATUS: OK|WARN|FAIL]
[LOOP_DAILY: 簡報✅/⚠️, Dropbox✅/⚠️, 網站✅/⚠️, 系統✅/⚠️]
⚠️ 執行方式（2026-11-11 修正）：code mode 入面只有直接注入嘅全域，exec 要寫 exec({command: ...})
或用 shell 腳本；**唔好寫 tools.exec(...)**（會 ReferenceError，令成個 run 白撞到 LLM idle timeout）。
檢查 cron 狀態用 exec 執行 openclaw cron list --json。
EOF
)" 2>>"$LOG" && log "✅ 傍晚簡報已重建" || log "❌ 傍晚簡報重建失敗"
            ;;
        "每日健康報告 22:00")
            openclaw cron add --name "每日健康報告 22:00" --cron "0 22 * * *" --tz "Asia/Hong_Kong" \
                --agent main --session isolated --announce --channel telegram --to "$TELEGRAM_TO" \
                --fallbacks "$FALLBACKS" \ \
                --model "minimax/MiniMax-M3.1-Flash@minimax:cn" \
                --timeout-seconds 3600 \
                --message "$(cat <<'EOF'
【每日健康報告 22:00】

⚡ 執行方式（2026-11-12 修正）：**只做一次 exec**，跑現成腳本；唔好喺 code mode 入面逐項手寫指令：
exec({command: "bash /home/openclaw/.openclaw/workspace/scripts/health_report.sh"})
該腳本已一次過做齊：① 現況快照（網站 HTTP／8 個 cron job errs+fallback 層數+lastRun／三倉 git 未推送+髒檔／MEMORY.md 行數／敏感檔／章節數／兩個 skill 四處 md5 唯一性／Dropbox state+token 新鮮度／system cron 行數）② 自動修復（三倉未推送 commit→push、DREAMS.md→commit+push、untracked 暫存檔→rm）③ 判定（[LOOP_STATUS]／[LOOP_DAILY]）。

⚠️ 絕對唔好寫 tools.exec(...)：code mode 只有直接注入嘅全域，寫成 tools.* 會 ReferenceError，白撞到 LLM idle timeout（2026-11-12 22:00 就係咁由 5 分鐘拖到 21 分鐘）。
⚠️ 唔好用 cron tool 睇 cron 狀態（isolated session 有 scoping，只顯示自己 agent 嘅 job，會誤判其他 jobs 消失）——腳本第 4 段已用 openclaw cron list --json 攞齊。
⚠️ 以下係 **system cron（crontab -l）**，唔會出現喺 OpenClaw cron list：記憶備份 08:00/20:00、Volume 5 Dropbox 11:00、財經 10:00/16:00、AQHI 10:00/16:00、自動記憶 23:00 —— 見到佢哋喺 crontab 就係正常，**唔係消失**！
- 2026-11-01 起 system cron 簡報（send-briefing.sh）已退休，天氣 digest 併入早上/傍晚簡報；**唔好再報告「雙軌簡報」問題**。

📋 你要做的：讀上面 exec 嘅輸出 → 整理成健康報告（每個項目 ✅/⚠️ + 列出腳本自動修復咗咩）→ 交付 Telegram。
結尾一定要保留腳本輸出嘅 [LOOP_STATUS: ...] 同 [LOOP_DAILY: ...] 兩行。
EOF
)" 2>>"$LOG" && log "✅ 健康報告已重建" || log "❌ 健康報告重建失敗"
            ;;
        "每日 Audio Sync 10:00")
            openclaw cron add --name "每日 Audio Sync 10:00" --cron "0 10 * * *" --tz "Asia/Hong_Kong" \
                --agent main --session isolated --announce --channel telegram --to "$TELEGRAM_TO" \
                --fallbacks "$FALLBACKS" \
                --model "minimax/MiniMax-M3.1-Flash@minimax:cn" \
                --timeout-seconds 1800 \
                --message "Run daily audio sync: exec \`cd /home/openclaw/.openclaw/workspace && python3 scripts/audio_sync_pipeline.py\` and report results. ⚠️ 執行方式：code mode 內用 exec({command: ...}) 或 shell 腳本，**唔好寫 tools.exec(...)**（會 ReferenceError）。" \
                2>>"$LOG" && log "✅ Audio Sync 已重建" || log "❌ Audio Sync 重建失敗"
            ;;
        "OpenClaw Version Check")
            openclaw cron add --name "OpenClaw Version Check" --cron "0 11 * * *" \
                --agent main --session isolated --announce --channel telegram --to "$TELEGRAM_TO" \
                --fallbacks "$FALLBACKS" \ \
                --model "minimax/MiniMax-M3.1-Flash@minimax:cn" \
                --timeout-seconds 600 \
                --message "請執行 /home/openclaw/.openclaw/workspace/scripts/check-openclaw-version.sh 並報告結果 ⚠️ 執行方式：code mode 內用 exec({command: ...}) 或 shell 腳本，**唔好寫 tools.exec(...)**（會 ReferenceError）。" \
                2>>"$LOG" && log "✅ Version Check 已重建" || log "❌ Version Check 重建失敗"
            ;;
        *)
            log "未知 job 名稱: $name"
            ;;
    esac
}

# 關鍵 jobs 清單
FIXED=0
for JOB in "早上簡報 08:15" "中午簡報 12:55" "傍晚簡報 17:55 — 日結" "每日健康報告 22:00" "每日 Audio Sync 10:00" "OpenClaw Version Check"; do
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
# ------------------------------------------------------------
# Part 1b: model override policy guard (2026-10-21)
# Root cause: old guardian only checked "job exists + enabled", never the
# payload.model override. Jobs that overrode a model outside
# agents.*.modelPolicy.allow failed every single run while the guardian
# logged "all OK". This block validates each job model/fallbacks against
# the policy allow list and auto-repairs violations.
# ------------------------------------------------------------
if [ -f "$WORKSPACE/scripts/cron_model_guard.py" ]; then
    GUARD_OUT=$(python3 "$WORKSPACE/scripts/cron_model_guard.py" --fix 2>&1)
    while IFS= read -r gline; do log "$gline"; done <<< "$GUARD_OUT"
    GUARD_FIXED=$(printf "%s
" "$GUARD_OUT" | grep -c "^FIXED:" || true)
    if [ "${GUARD_FIXED:-0}" -gt 0 ]; then
        FIXED=$((FIXED + GUARD_FIXED))
    fi
fi
CRONTAB=$(crontab -l 2>/dev/null)
SYSTEM_TASKS=(
    "backup-memory.sh"
    # 2026-11-01 大肥喵指令退休：send-briefing.sh（system cron 簡報）唔喺守護名單 —
    # 天氣 digest 已併入 OpenClaw cron agent 簡報（早上 08:15 / 傍晚 17:55），
    # crontab 已註釋，guardian 唔會加返（照 Volume 4 退役做法）。
    "dropbox-volume5-daily-sync.sh"
    "dropbox-volume6-daily-sync.sh"
    "dropbox-volume7-daily-sync.sh"
    "update_finance.sh"
    "update_finance_news.sh"
    "update_aqhi.sh"
    "auto-daily-memory-log.sh"
    # 2026-11-05 大肥喵指令：版本檢查收單軌（保留 OpenClaw cron job「OpenClaw Version Check」，
    # 退役 system cron 軌）— 同一腳本兩軌各行一次會令大肥喵每日收兩次同樣 Telegram 通知。
    # check_openclaw_update.py **唔喺守護名單**：crontab 冇佢係正確狀態，唔好自動加返。
)
# 2026-10-23: system cron 條目會喺 crontab 改寫時意外被註釋（2026-10-21 Vol5 已中招一次）。
# 呢度保留完整 cron 行，偵測到「被註釋 = 缺失」就自動加返（append，唔會洗掉其他條目）。
# ⚠️ dropbox-volume4-daily-sync.sh **唔喺守護名單**：Volume 4 已按用戶 2026-10-02 指令退役
#    （SKILL.md v2.9.92），crontab 註釋咗係正確狀態，唔好自動加返。
declare -A DROPBOX_CRON=(
    ["dropbox-volume5-daily-sync.sh"]="0 11 * * * cd /home/openclaw/.openclaw/workspace && bash scripts/dropbox-volume5-daily-sync.sh >> /home/openclaw/.openclaw/workspace/logs/dropbox-volume5-sync.log 2>&1"
    ["dropbox-volume6-daily-sync.sh"]="0 11 * * * cd /home/openclaw/.openclaw/workspace && bash scripts/dropbox-volume6-daily-sync.sh >> /home/openclaw/.openclaw/workspace/logs/dropbox-volume6-sync.log 2>&1"
    ["dropbox-volume7-daily-sync.sh"]="30 11 * * * cd /home/openclaw/.openclaw/workspace && bash scripts/dropbox-volume7-daily-sync.sh >> /home/openclaw/.openclaw/workspace/logs/dropbox-volume7-sync.log 2>&1"
)
for TASK in "${SYSTEM_TASKS[@]}"; do
    # 只睇未註釋嘅行（grep -v '^[[:space:]]*#'），註釋咗嘅等於缺失
    if echo "$CRONTAB" | grep -v '^[[:space:]]*#' | grep -q "$TASK"; then
        log "✅ system cron 存在: $TASK"
    elif [ -n "${DROPBOX_CRON[$TASK]:-}" ]; then
        log "❌ system cron 缺失（自動加回）: $TASK"
        ( crontab -l 2>/dev/null; echo "# 2026-10-23 cron-guardian 自動還原"; echo "${DROPBOX_CRON[$TASK]}" ) | crontab -
        CRONTAB=$(crontab -l 2>/dev/null)
        FIXED=$((FIXED+1))
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
