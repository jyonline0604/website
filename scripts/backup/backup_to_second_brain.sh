#!/bin/bash
# Backup wrapper script
# 備份小說網站數據到本地備份目錄

set -e

LOG_FILE="/home/openclaw/.openclaw/workspace/logs/backup.log"
REPO_DIR="/home/openclaw/.openclaw/workspace/my-novel"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 開始備份小說網站..." >> "$LOG_FILE"

# 檢查仓库是否存在
if [ ! -d "$REPO_DIR" ]; then
    echo "❌ 錯誤: 仓库目錄不存在: $REPO_DIR" >> "$LOG_FILE"
    exit 1
fi

cd "$REPO_DIR"

# 創建備份目錄（如果不存在）
BACKUP_DIR="/home/openclaw/.openclaw/workspace/backups"
mkdir -p "$BACKUP_DIR"

# 生成備份文件名（時間戳）
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
BACKUP_FILE="$BACKUP_DIR/novel-website-backup-$TIMESTAMP.tar.gz"

# 執行備份（只備份重要文件，忽略 node_modules、.git 等）
tar -czf "$BACKUP_FILE" \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='*.log' \
    --exclude='backup_before_fix' \
    -C "$REPO_DIR" \
    . 2>> "$LOG_FILE"

if [ $? -eq 0 ]; then
    echo "✅ 備份完成: $BACKUP_FILE" >> "$LOG_FILE"
    
    # 保留最近 7 天的備份
    find "$BACKUP_DIR" -name "novel-website-backup-*.tar.gz" -mtime +7 -delete >> "$LOG_FILE" 2>&1
    echo "✅ 已清理 7 天前的舊備份" >> "$LOG_FILE"
else
    echo "❌ 備份失敗" >> "$LOG_FILE"
    exit 1
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 備份任務完成" >> "$LOG_FILE"
