#!/bin/bash
# 財經新聞自動更新腳本
# 每小時更新一次財經新聞

set -e

cd /home/openclaw/.openclaw/workspace

echo "📰 開始更新財經新聞 $(date '+%Y-%m-%d %H:%M:%S')"

# 先同步 remote，避免 non-fast-forward
git pull --rebase -X theirs origin main 2>/dev/null || {
  git rebase --abort 2>/dev/null || true
  echo "  ⚠️ Git 同步出錯，嘗試 force 同步..."
  git fetch origin main
  git reset --hard origin/main 2>/dev/null || true
}

# 執行Python腳本抓取新聞
python3 scripts/fetch_finance_news.py

# 如果有Git變更，提交並推送
if [[ -n $(git status --porcelain finance-news.json) ]]; then
    echo "📝 檢測到財經新聞更新"
    
    # 添加並提交
    git add finance-news.json
    git commit -m "docs: update finance news $(date '+%Y-%m-%d %H:%M')" || true
    
    # 推送到GitHub（自動重試3次，避免 non-fast-forward）
    for attempt in 1 2 3; do
      git pull --rebase -X theirs origin main 2>/dev/null || git rebase --abort 2>/dev/null || true
      
      if git push origin main 2>&1; then
        echo "  ✅ 財經新聞已推送到GitHub"
        break
      fi
      
      if [ $attempt -lt 3 ]; then
        echo "  ⚠️ Push 失敗 (attempt $attempt/3)，重試中..."
        sleep 3
      else
        echo "  ⚠️ Push 最終失敗，嘗試 force 推送（auto-generated 數據安全）"
        git push origin main --force-with-lease 2>/dev/null || echo "  ❌ Push 仍然失敗"
      fi
    done
else
    echo "📊 財經新聞無變化"
fi

echo "✅ 財經新聞更新完成 $(date '+%Y-%m-%d %H:%M:%S')"
