#!/bin/bash
# 財經新聞自動更新腳本
# 每小時更新一次財經新聞

set -e

cd /home/openclaw/.openclaw/workspace

echo "📰 開始更新財經新聞 $(date '+%Y-%m-%d %H:%M:%S')"

# 執行Python腳本抓取新聞
python3 scripts/fetch_finance_news.py

# 如果有Git變更，提交並推送


if [[ -n $(git status --porcelain finance-news.json) ]]; then
    echo "📝 檢測到財經新聞更新"
    
    # 添加並提交
    git add finance-news.json
    git commit -m "docs: update finance news $(date '+%Y-%m-%d %H:%M')" || true
    
    # 推送到GitHub
    git push origin main && echo "✅ 財經新聞已推送到GitHub"
else
    echo "📊 財經新聞無變化"
fi

echo "✅ 財經新聞更新完成 $(date '+%Y-%m-%d %H:%M:%S')"