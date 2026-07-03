#!/bin/bash
# 財經數據自動更新腳本
# 每30分鐘更新一次財經數據（00及30分）

# ⚠️ 不使用 set -e，避免 Python 腳本失敗時 script 靜默退出
# git 相關錯誤由 git-push-with-lock.sh 處理

cd /home/openclaw/.openclaw/workspace

echo "🔄 開始更新財經數據 $(date '+%Y-%m-%d %H:%M:%S')"

# 執行Python腳本獲取數據（允許失敗，記錄錯誤但不中斷流程）
python3 scripts/fetch_finance_data.py || {
    echo "  ⚠️ fetch_finance_data.py 失敗（exit code: $?）"
}

# 如果有Git變更，用 lock 機制提交並推送
if [[ -n $(git status --porcelain finance-data.json) ]]; then
    echo "📝 檢測到財經數據更新"
    git add finance-data.json
    git commit -m "docs: update finance data $(date '+%Y-%m-%d %H:%M')" || true
    
    # 使用鎖機制推送，防止多 cron 衝突
    bash scripts/git-push-with-lock.sh
else
    echo "📊 財經數據無變化"
fi

echo "✅ 財經數據更新完成 $(date '+%Y-%m-%d %H:%M:%S')"
