#!/bin/bash
# Wrapper for game guide update
set -e
REPO_DIR="/home/openclaw/.openclaw/workspace/my-novel-website"
cd "$REPO_DIR"
LOG_FILE="/home/openclaw/.openclaw/workspace/logs/guide-update.log"
echo "=== 攻略頁面更新 ($(date '+%Y-%m-%d %H:%M:%S')) ===" >> "$LOG_FILE"
if [ -f "auto-update-scripts/generate_guide_content.py" ]; then
    python3 auto-update-scripts/generate_guide_content.py >> "$LOG_FILE" 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ 攻略頁面更新完成" >> "$LOG_FILE"
        git add game-guide.html saint-seiya-guide.html beapro-football-guide.html kai-tian-guide.html >> "$LOG_FILE" 2>&1
        git commit -m "chore(guides): 自動更新攻略頁面 ($(date '+%Y-%m-%d'))" >> "$LOG_FILE" 2>&1
        git push >> "$LOG_FILE" 2>&1
        echo "✅ 已提交推送" >> "$LOG_FILE"
    else
        echo "❌ 更新失敗" >> "$LOG_FILE"
        exit 1
    fi
else
    echo "❌ generate_guide_content.py 不存在" >> "$LOG_FILE"
    exit 1
fi
