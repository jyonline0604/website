#!/bin/bash
# 財經新聞自動更新腳本
# 每小時更新新聞，但每2小時才 push 到 GitHub
# 減少 GitHub Pages build 頻率

cd /home/openclaw/.openclaw/workspace

echo "📰 開始更新財經新聞 $(date '+%Y-%m-%d %H:%M:%S')"

# 執行Python腳本抓取新聞（允許失敗）
python3 scripts/fetch_finance_news.py || {
    echo "  ⚠️ fetch_finance_news.py 失敗（exit code: $?）"
}

# 判斷是否應該 push（每2小時：只在偶數整點推）
CURRENT_HOUR=$(date '+%H')
CURRENT_MIN=$(date '+%M')
SHOULD_PUSH=0
if [ "$CURRENT_MIN" = "00" ] && [ $((10#$CURRENT_HOUR % 2)) -eq 0 ]; then
    SHOULD_PUSH=1
fi

# 如果有Git變更
if [[ -n $(git status --porcelain finance-news.json) ]]; then
    echo "📝 檢測到財經新聞更新"
    git add finance-news.json
    git commit -m "docs: update finance news $(date '+%Y-%m-%d %H:%M')" || true
    
    if [ "$SHOULD_PUSH" = "1" ]; then
        echo "  🕐 偶數整點，執行批次推送"
        bash scripts/batch-push.sh
    else
        echo "  ⏸️ 非推送時段（$CURRENT_HOUR:$CURRENT_MIN），跳過 push，等待下個偶數整點"
    fi
else
    echo "📊 財經新聞無變化"
fi

echo "✅ 財經新聞更新完成 $(date '+%Y-%m-%d %H:%M:%S')"
