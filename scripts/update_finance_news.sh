#!/bin/bash
# 財經新聞自動更新腳本
# 每小時更新一次財經新聞

# ⚠️ 不使用 set -e，避免 Python 腳本失敗時 script 靜默退出
# git 相關錯誤由 git-push-with-lock.sh 處理

cd /home/openclaw/.openclaw/workspace

echo "📰 開始更新財經新聞 $(date '+%Y-%m-%d %H:%M:%S')"

# 執行Python腳本抓取新聞（允許失敗）
python3 scripts/fetch_finance_news.py || {
    echo "  ⚠️ fetch_finance_news.py 失敗（exit code: $?）"
}

# 如果有Git變更，用 lock 機制提交並推送
if [[ -n $(git status --porcelain finance-news.json) ]]; then
    echo "📝 檢測到財經新聞更新"
    git add finance-news.json
    git commit -m "docs: update finance news $(date '+%Y-%m-%d %H:%M') (條)" || true
    
    # 使用鎖機制推送，防止多 cron 衝突
    bash scripts/git-push-with-lock.sh
else
    echo "📊 財經新聞無變化"
fi

echo "✅ 財經新聞更新完成 $(date '+%Y-%m-%d %H:%M:%S')"
