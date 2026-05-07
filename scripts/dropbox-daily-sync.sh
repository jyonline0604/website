#!/bin/bash
# Dropbox Volume 2 每日自動化更新脚本
# 每天從 Dropbox 第二卷自動下載 6 章並更新網站

export PATH="/home/openclaw/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

WORKSPACE="/home/openclaw/.openclaw/workspace"

cd "$WORKSPACE"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🚀 開始每日 Dropbox Volume 2 同步..."

# 執行同步腳本
python3 scripts/dropbox_volume2_sync.py 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Dropbox Volume 2 同步完成"

# 備份記憶（成功時才備份）
source /home/openclaw/.openclaw/workspace/scripts/backup-memory.sh 2>/dev/null || true