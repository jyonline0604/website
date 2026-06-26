#!/bin/bash
# 財經數據自動更新腳本
# 每5分鐘更新一次財經數據

set -e

cd /home/openclaw/.openclaw/workspace

echo "🔄 開始更新財經數據 $(date '+%Y-%m-%d %H:%M:%S')"

# 先同步 remote，避免 non-fast-forward
git pull --rebase -X theirs origin main 2>/dev/null || {
  git rebase --abort 2>/dev/null || true
  echo "  ⚠️ Git 同步出錯，嘗試 force 同步..."
  git fetch origin main
  git reset --hard origin/main 2>/dev/null || true
}

# 執行Python腳本獲取數據
python3 scripts/fetch_finance_data.py

# 如果有Git變更，提交並推送
if [[ -n $(git status --porcelain finance-data.json) ]]; then
    echo "📝 檢測到財經數據更新"
    
    # 添加並提交
    git add finance-data.json
    git commit -m "docs: update finance data $(date '+%Y-%m-%d %H:%M')" || true
    
    # 推送到GitHub（自動重試3次，避免 non-fast-forward）
    for attempt in 1 2 3; do
      # 推之前再同步一次（其他 process 可能已更新）
      git pull --rebase -X theirs origin main 2>/dev/null || git rebase --abort 2>/dev/null || true
      
      if git push origin main 2>&1; then
        echo "  ✅ 財經數據已推送到GitHub"
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
    echo "📊 財經數據無變化"
fi

sync
echo "✅ 財經數據更新完成 $(date '+%Y-%m-%d %H:%M:%S')"
