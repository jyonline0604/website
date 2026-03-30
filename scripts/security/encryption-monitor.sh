#!/bin/bash
# Encryption monitor script
# 監控加密狀態（示例：檢查是否有未加密的敏感文件）

set -e

LOG_FILE="/home/openclaw/.openclaw/workspace/logs/encryption-monitor.log"
REPO_DIR="/home/openclaw/.openclaw/workspace/my-novel-website"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 開始加密監控..." >> "$LOG_FILE"

# 此腳本為示例，實際內容取決於你的加密方案
# 例如：檢查 .env 是否加密、檢查備份文件是否加密等

# 1. 檢查是否有未加密的敏感文件
SENSITIVE_FILES=(".env" "*.pem" "*.key" "*.crt")

for pattern in "${SENSITIVE_FILES[@]}"; do
    FOUND=$(find "$REPO_DIR" -name "$pattern" -type f 2>/dev/null)
    if [ -n "$FOUND" ]; then
        echo "❌ 發現未加密的敏感文件: $FOUND" >> "$LOG_FILE"
    else
        echo "✅ 無未加密的 $pattern 文件" >> "$LOG_FILE"
    fi
done

# 2. 檢查 backups 目錄是否存在（加密備份）
BACKUP_DIR="/home/openclaw/.openclaw/workspace/backups"
if [ -d "$BACKUP_DIR" ]; then
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/*.tar.gz 2>/dev/null | wc -l)
    echo "✅ 備份目錄存在，共有 $BACKUP_COUNT 個備份文件" >> "$LOG_FILE"
else
    echo "⚠️  備份目錄不存在（可能尚未創建）" >> "$LOG_FILE"
fi

# 3. 檢查是否有加密工具可用
if command -v gpg &> /dev/null; then
    echo "✅ GPG 加密工具可用" >> "$LOG_FILE"
else
    echo "⚠️  GPG 未安裝（可選）" >> "$LOG_FILE"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 加密監控完成" >> "$LOG_FILE"
