#!/bin/bash
# OpenClaw自動更新腳本

set -e

# 設置環境變量
export PATH="/home/openclaw/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# 日誌文件
LOG_FILE="/home/openclaw/.openclaw/workspace/logs/openclaw-update.log"
VERSION_FILE="/home/openclaw/.openclaw/workspace/openclaw-version.json"

# 函數：記錄日誌
log_message() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local message="$1"
    echo "[$timestamp] $message" | tee -a "$LOG_FILE"
}

# 函數：獲取當前版本
get_current_version() {
    openclaw --version 2>/dev/null | grep -oP 'OpenClaw\s+\K[\d\.\-]+' || echo "unknown"
}

# 函數：備份當前版本
backup_current_version() {
    local current_version=$(get_current_version)
    local backup_dir="/home/openclaw/.openclaw/backup/openclaw"
    
    mkdir -p "$backup_dir"
    
    # 備份npm包信息
    npm list -g openclaw > "$backup_dir/openclaw-${current_version}.list" 2>&1
    
    log_message "已備份當前版本 $current_version 信息"
}

# 主函數
main() {
    log_message "🚀 OpenClaw自動更新開始"
    
    # 檢查當前版本
    CURRENT_VERSION=$(get_current_version)
    log_message "📋 當前版本: $CURRENT_VERSION"
    
    # 備份當前版本
    backup_current_version
    
    # 檢查是否有新版本
    log_message "🔍 檢查新版本..."
    LATEST_VERSION=$(npm view openclaw version 2>/dev/null || echo "unknown")
    
    if [ "$LATEST_VERSION" = "unknown" ]; then
        log_message "❌ 無法獲取最新版本信息"
        return 1
    fi
    
    log_message "🌐 最新版本: $LATEST_VERSION"
    
    # 比較版本
    if [ "$CURRENT_VERSION" = "$LATEST_VERSION" ]; then
        log_message "✅ 已是最新版本，無需更新"
        return 0
    fi
    
    log_message "🔄 發現新版本，開始更新..."
    
    # 執行更新
    log_message "📦 執行: npm update -g openclaw"
    if npm update -g openclaw 2>&1 | tee -a "$LOG_FILE"; then
        # 檢查更新後的版本
        NEW_VERSION=$(get_current_version)
        log_message "🎉 更新成功！新版本: $NEW_VERSION"
        
        # 更新版本記錄文件
        if [ -f "$VERSION_FILE" ]; then
            jq --arg current "$NEW_VERSION" --arg latest "$LATEST_VERSION" \
               '.current_version = $current | .last_updated = now | .update_available = false' \
               "$VERSION_FILE" > "${VERSION_FILE}.tmp" && mv "${VERSION_FILE}.tmp" "$VERSION_FILE"
        fi
        
        # 重啟OpenClaw服務（如果正在運行）
        if systemctl is-active --quiet openclaw-gateway 2>/dev/null; then
            log_message "🔄 重啟OpenClaw Gateway服務..."
            systemctl restart openclaw-gateway 2>&1 | tee -a "$LOG_FILE"
        fi
        
        return 0
    else
        log_message "❌ 更新失敗"
        return 1
    fi
}

# 執行主函數
main "$@"