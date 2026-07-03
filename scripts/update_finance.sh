#!/bin/bash
# 財經數據自動更新腳本
# 每30分鐘更新數據（00及30分），但每2小時才 push 到 GitHub
# 減少 GitHub Pages build 頻率，避免 deployment 失敗

cd /home/openclaw/.openclaw/workspace

echo "🔄 開始更新財經數據 $(date '+%Y-%m-%d %H:%M:%S')"

# 執行Python腳本獲取數據（允許失敗）
python3 scripts/fetch_finance_data.py || {
    echo "  ⚠️ fetch_finance_data.py 失敗（exit code: $?）"
}

# 判斷是否應該 push（每2小時：只在偶數整點推）
CURRENT_HOUR=$(date '+%H')
CURRENT_MIN=$(date '+%M')
SHOULD_PUSH=0
if [ "$CURRENT_MIN" = "00" ] && [ $((10#$CURRENT_HOUR % 2)) -eq 0 ]; then
    SHOULD_PUSH=1
fi

# 如果有Git變更
if [[ -n $(git status --porcelain finance-data.json) ]]; then
    echo "📝 檢測到財經數據更新"
    git add finance-data.json
    git commit -m "docs: update finance data $(date '+%Y-%m-%d %H:%M')" || true
    
    if [ "$SHOULD_PUSH" = "1" ]; then
        echo "  🕐 偶數整點，執行推送"
        bash scripts/git-push-with-lock.sh
    else
        echo "  ⏸️ 非推送時段（$CURRENT_HOUR:$CURRENT_MIN），跳過 push，等待下個整點"
    fi
else
    echo "📊 財經數據無變化"
fi

echo "✅ 財經數據更新完成 $(date '+%Y-%m-%d %H:%M:%S')"
