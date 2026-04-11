#!/bin/bash
# pre-push hook - 推送前自動檢查章節頁面結構
# 安裝方式：cp scripts/pre-push-check.sh .git/hooks/pre-push

set -e

echo "🔍 執行推送前檢查..."

# 檢查章節頁面結構
check_chapters_html() {
    local file="$1"
    if [ ! -f "$file" ]; then
        echo "⚠️  $file 不存在，跳過檢查"
        return 0
    fi

    echo "📄 檢查 $file HTML結構..."

    local checks=0
    local total=5

    # 使用 [ ] && checks=$((checks+1)) 避免 (( )) 的返回值問題
    grep -q '<div class="container">' "$file" && checks=$((checks+1)) || echo "❌ 缺少 container"
    grep -q '<div class="chapter-list">' "$file" && checks=$((checks+1)) || echo "❌ 缺少 chapter-list"
    grep -q '<div class="sort-controls">' "$file" && checks=$((checks+1)) || echo "❌ 缺少 sort-controls"
    grep -q '<div class="chapter-list-grid"' "$file" && checks=$((checks+1)) || echo "❌ 缺少 chapter-list-grid"
    grep -q '<div class="chapter-groups"' "$file" && checks=$((checks+1)) || echo "❌ 缺少 chapter-groups"

    if [ $checks -eq $total ]; then
        echo "✅ HTML結構檢查通過 ($checks/$total)"
        return 0
    else
        echo "❌ HTML結構檢查失敗 ($checks/$total)"
        return 1
    fi
}

# 檢查 av-novels.html 結構
check_av_novels_html() {
    local file="$1"
    if [ ! -f "$file" ]; then
        echo "⚠️  $file 不存在，跳過檢查"
        return 0
    fi

    echo "📄 檢查 $file HTML結構..."

    local checks=0
    local total=2

    grep -q '<div class="container">' "$file" && checks=$((checks+1)) || echo "❌ av-novels 缺少container"
    grep -q '<div class="chapter-grid"' "$file" && checks=$((checks+1)) || echo "❌ av-novels 缺少chapter-grid"

    if [ $checks -eq $total ]; then
        echo "✅ av-novels HTML結構檢查通過 ($checks/$total)"
        return 0
    else
        echo "❌ av-novels HTML結構檢查失敗 ($checks/$total)"
        return 1
    fi
}

# 主檢查流程
WORKSPACE="/home/openclaw/.openclaw/workspace"

check_chapters_html "$WORKSPACE/chapters.html"
check_av_novels_html "$WORKSPACE/av-novels.html"

echo "✅ 所有檢查通過，可以推送！"
