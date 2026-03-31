#!/bin/bash
# 財經數據自動更新腳本
# 每5分鐘更新一次財經數據

set -e

cd /home/openclaw/.openclaw/workspace

echo "🔄 開始更新財經數據 $(date '+%Y-%m-%d %H:%M:%S')"

# 執行Python腳本獲取數據
python3 scripts/fetch_finance_data.py

# 如果有Git變更，提交並推送
# cd my-novel (now in website repo directly)

if [[ -n $(git status --porcelain finance-data.json) ]]; then
    echo "📝 檢測到財經數據更新"
    
    # 添加並提交
    git add finance-data.json
    git commit -m "docs: update finance data $(date '+%Y-%m-%d %H:%M')" || true
    
    # 推送到GitHub
    git push origin main && echo "✅ 財經數據已推送到GitHub"
else
    echo "📊 財經數據無變化"
fi

echo "✅ 財經數據更新完成 $(date '+%Y-%m-%d %H:%M:%S')"