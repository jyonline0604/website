#!/bin/bash
# Security check script
# 檢查系統安全狀態

set -e

LOG_FILE="/home/openclaw/.openclaw/workspace/logs/security-check.log"
REPO_DIR="/home/openclaw/.openclaw/workspace/my-novel-website"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 開始安全檢查..." >> "$LOG_FILE"

# 1. 檢查是否有 .env 文件洩露
if [ -f "$REPO_DIR/.env" ]; then
    echo "❌ 警告: 發現 .env 文件（應該從 Git 移除）" >> "$LOG_FILE"
else
    echo "✅ .env 文件不存在（好）" >> "$LOG_FILE"
fi

# 2. 檢查 Git 狀態是否有未提交的敏感文件
cd "$REPO_DIR"
if git ls-files --others --exclude-standard | grep -q '\.env\|\.pem\|\.key'; then
    echo "❌ 警告: 發現未追蹤的敏感文件" >> "$LOG_FILE"
    git ls-files --others --exclude-standard | grep -E '\.env|\.pem|\.key' >> "$LOG_FILE"
else
    echo "✅ 未發現未追蹤的敏感文件" >> "$LOG_FILE"
fi

# 3. 檢查 API 密鑰是否在auth-profiles.json中（而不是.env）
if [ -f "/home/openclaw/.openclaw/agents/main/agent/auth-profiles.json" ]; then
    echo "✅ auth-profiles.json 存在" >> "$LOG_FILE"
else
    echo "⚠️  auth-profiles.json 不存在（API 密鑰可能使用 .env）" >> "$LOG_FILE"
fi

# 4. 檢查檢查點目錄權限
CHECKPOINT_DIR="$REPO_DIR/checkpoints"
if [ -d "$CHECKPOINT_DIR" ]; then
    PERMS=$(stat -c %a "$CHECKPOINT_DIR")
    if [ "$PERMS" -le 770 ]; then
        echo "✅ 檢查點目錄權限正確: $PERMS" >> "$LOG_FILE"
    else
        echo "⚠️  檢查點目錄權限過寬: $PERMS（建議 750 或 700）" >> "$LOG_FILE"
    fi
else
    echo "ℹ️  檢查點目錄尚未創建" >> "$LOG_FILE"
fi

# 5. 檢查日誌目錄
LOG_DIR="/home/openclaw/.openclaw/workspace/logs"
if [ -d "$LOG_DIR" ]; then
    echo "✅ 日誌目錄存在" >> "$LOG_FILE"
    # 檢查日誌文件大小（避免磁盘滿）
    SIZE=$(du -sh "$LOG_DIR" | cut -f1)
    echo "   日誌目錄大小: $SIZE" >> "$LOG_FILE"
else
    echo "❌ 日誌目錄不存在" >> "$LOG_FILE"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 安全检查完成" >> "$LOG_FILE"
