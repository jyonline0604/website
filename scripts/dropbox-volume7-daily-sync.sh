#!/bin/bash
# Dropbox Volume 7 每日自動化更新腳本
# 每天從 Dropbox 第七卷自動下載 6 章並更新網站
#
# 2026-10-22 建立：Volume 6 已完成（CH1461-1740），接棒第七卷（CH1741 起）
# 排程時間用 11:30（唔同 V4/V5/V6 嘅 11:00 撞，避開 token 刷新同 git push 競態）

export PATH="/home/openclaw/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

WORKSPACE="/home/openclaw/.openclaw/workspace"

cd "$WORKSPACE"

# 序列化 Dropbox 同步（多個 job 同時跑會同時刷新 token / 同時 push 同一 repo）
LOCK_FILE="/tmp/dropbox-sync.lock"
exec 9>"$LOCK_FILE"
flock -w 900 9 || { echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 取得 Dropbox 同步鎖超時，本次跳過"; exit 1; }

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🚀 開始每日 Dropbox Volume 7 同步..."

# 執行同步腳本（腳本內建每日 6 章硬上限 + 防重複檢查）
python3 scripts/dropbox_volume7_sync.py 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Dropbox Volume 7 同步完成"

# 備份記憶（成功時才備份）
source /home/openclaw/.openclaw/workspace/scripts/backup-memory.sh 2>/dev/null || true
