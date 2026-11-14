#!/bin/bash
# Dropbox Volume 4 每日自動化更新腳本
# 每天從 Dropbox 第四卷自動下載 6 章並更新網站

export PATH="/home/openclaw/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

WORKSPACE="/home/openclaw/.openclaw/workspace"

cd "$WORKSPACE"

# 2026-11-14 守衛：Volume 4 已於 2026-10-02 按大肥喵指令退役（勿啟用、勿由 guardian 加返）。
# 2026-11-14 08:16 呢條 wrapper 曾被「早上簡報 08:15」job 嘅「自動修復：檢測到 state 分歧就直接修復」
# 指示觸發 → 已退役管線復活、改寫 .dropbox-sync/volume4_state.json、仲順帶 source 咗 backup-memory.sh。
# marker 存在就唔准執行；要復活必須先由大肥喵確認並刪除 marker。
RETIRED_MARKER="$WORKSPACE/.dropbox-sync/volume4_RETIRED"
if [ -f "$RETIRED_MARKER" ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⛔ Volume 4 已退役（2026-10-02 大肥喵指令，勿啟用）；本次跳過，唔會改 state、唔會觸發記憶備份"
  exit 0
fi

# 2026-10-22 修：序列化 Dropbox 同步（3 個 job 同時跑會同時刷新 token / 同時 push 同一 repo）
LOCK_FILE="/tmp/dropbox-sync.lock"
exec 9>"$LOCK_FILE"
flock -w 900 9 || { echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 取得 Dropbox 同步鎖超時，本次跳過"; exit 1; }

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🚀 開始每日 Dropbox Volume 4 同步..."

# 執行同步腳本
python3 scripts/dropbox_volume4_sync.py 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Dropbox Volume 4 同步完成"

# 備份記憶（成功時才備份）
source /home/openclaw/.openclaw/workspace/scripts/backup-memory.sh 2>/dev/null || true
