#!/bin/bash
# system-health-check.sh - 小說網站系統健康檢查

echo "=== 小說網站健康檢查 ==="
echo "時間: $(date)"
echo ""

echo "1. 檢查 crontab 是否正常"
crontab -l | grep -v "^#" | head -5
echo ""

echo "2. 檢查章節標題唯一性"
duplicates=$(grep -rh "<title>第.*章：" chapter-*.html 2>/dev/null | grep -v av | sort | uniq -d | wc -l)
if [ "$duplicates" -gt 0 ]; then
    echo "❌ 發現 $duplicates 個重複標題"
    grep -rh "<title>第.*章：" chapter-*.html | grep -v av | sort | uniq -d
else
    echo "✅ 無重複標題"
fi
echo ""

echo "3. 檢查 my-novel 路徑引用"
my_novel_refs=$(grep -r "my-novel" scripts/ --include="*.sh" --include="*.py" 2>/dev/null | grep -v "^#" | wc -l)
if [ "$my_novel_refs" -gt 0 ]; then
    echo "❌ 發現 $my_novel_refs 處 my-novel 引用"
    grep -r "my-novel" scripts/ --include="*.sh" --include="*.py" 2>/dev/null | grep -v "^#"
else
    echo "✅ 無 my-novel 引用"
fi
echo ""

echo "4. 檢查備份狀態"
tail -3 logs/memory-backup.log 2>/dev/null
echo ""

echo "5. 檢查 HEARTBEAT.md 路徑"
if grep -q "my-novel" HEARTBEAT.md 2>/dev/null; then
    echo "❌ HEARTBEAT.md 仍有 my-novel 引用"
else
    echo "✅ HEARTBEAT.md 路徑正確"
fi
echo ""

echo "6. 檢查章節 HTML 結構"
bad_html=$(grep -c "<html" chapter-*.html 2>/dev/null | grep -v ":1$" | wc -l)
if [ "$bad_html" -gt 0 ]; then
    echo "❌ 發現 $bad_html 個 HTML 結構異常"
else
    echo "✅ HTML 結構正常"
fi
echo ""

echo "=== 檢查完成 ==="
