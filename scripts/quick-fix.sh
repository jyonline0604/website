#!/bin/bash
# quick-fix.sh - 一鍵修復常見問題

set -e
WORKSPACE="/home/openclaw/.openclaw/workspace"
cd "$WORKSPACE"

echo "=== 執行快速修復 ==="

# 修復 1: 更新章節列表
echo "1. 更新章節列表..."
python3 scripts/update_novel_lists.py

# 修復 2: 檢查並修復標題重複
echo "2. 檢查標題重複..."
duplicates=$(grep -rh "<title>第.*章：" chapter-*.html 2>/dev/null | grep -v av | sort | uniq -d)
if [ -n "$duplicates" ]; then
    echo "❌ 發現重複: $duplicates"
    echo "需要手動處理"
else
    echo "✅ 無重複"
fi

# 修復 3: 修復 my-novel 路徑
echo "3. 修復路徑..."
for f in scripts/*.sh scripts/*.py; do
    if [ -f "$f" ] && grep -q "my-novel" "$f" 2>/dev/null; then
        echo "  修復: $f"
        sed -i 's|my-novel|workspace|g' "$f"
        sed -i 's|my-novel-website|workspace|g' "$f"
    fi
done

if grep -q "my-novel" HEARTBEAT.md 2>/dev/null; then
    echo "  修復: HEARTBEAT.md"
    sed -i 's|my-novel|workspace|g' HEARTBEAT.md
fi

# 修復 4: 推送變更
echo "4. 推送變更..."
git add -A
git commit -m "fix: quick fix $(date '+%Y-%m-%d %H:%M')" 2>/dev/null || echo "無變更需要推送"
git push origin main

echo "=== 修復完成 ==="
