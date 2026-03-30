#!/bin/bash
# 記憶備份腳本
# 在模型切換前自動執行，備份所有記憶文件到 Max-backup

set -e

WORKSPACE="/home/openclaw/.openclaw/workspace"
BACKUP_NAME="memory-backup-$(date +%Y%m%d_%H%M%S)"
LOG_FILE="$WORKSPACE/logs/memory-backup.log"

echo "[$(date)] === 開始記憶備份 ===" >> "$LOG_FILE"

cd "$WORKSPACE" || exit 1

# 確保日誌目錄存在
mkdir -p "$WORKSPACE/logs"

# 創建臨時備份目錄
TEMP_DIR="/tmp/${BACKUP_NAME}"
mkdir -p "$TEMP_DIR"

# 複製記憶文件
cp "$WORKSPACE/MEMORY.md" "$TEMP_DIR/" 2>/dev/null || true
cp "$WORKSPACE/memory/"*.md "$TEMP_DIR/" 2>/dev/null || true

# 檢查是否有內容
if [ ! "$(ls -A "$TEMP_DIR" 2>/dev/null)" ]; then
    echo "[$(date)] 無記憶文件需要備份" >> "$LOG_FILE"
    rm -rf "$TEMP_DIR"
    exit 0
fi

# 壓縮
tar -czf "/tmp/${BACKUP_NAME}.tar.gz" -C "$TEMP_DIR" . 2>/dev/null

# 加密
openssl enc -aes-256-cbc -pbkdf2 -iter 100000 -salt -in "/tmp/${BACKUP_NAME}.tar.gz" -out "/tmp/${BACKUP_NAME}.tar.gz.enc" -pass file:"$WORKSPACE/.backup-pass" 2>> "$LOG_FILE"

# 複製到 Second-brain 並推送
if [ -d "$WORKSPACE/Second-brain" ]; then
    cd "$WORKSPACE/Second-brain"
    cp "/tmp/${BACKUP_NAME}.tar.gz.enc" "./memory-backup-${BACKUP_NAME}.tar.gz.enc"
    git add "memory-backup-${BACKUP_NAME}.tar.gz.enc" 2>/dev/null
    git commit -m "memory: auto backup $(date +%Y-%m-%d\ %H:%M)" 2>/dev/null || true
    # 推送到 Max-backup
    git push Max-backup main 2>> "$LOG_FILE" || true
    # 推送到 Second-brain (origin)
    git push origin main 2>> "$LOG_FILE" || true
fi

# 清理
rm -rf "$TEMP_DIR" "/tmp/${BACKUP_NAME}.tar.gz" "/tmp/${BACKUP_NAME}.tar.gz.enc"

echo "[$(date)] === 記憶備份完成 ===" >> "$LOG_FILE"
