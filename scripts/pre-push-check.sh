#!/bin/bash
# pre-push hook - 推送前自動檢查章節頁面結構
# 安裝方式：cp scripts/pre-push-check.sh .git/hooks/pre-push

set -e

echo "🔍 執行推送前檢查..."

WORKSPACE="/home/openclaw/.openclaw/workspace"

# ============================================
# 檢查1：章節頁面 HTML 結構
# ============================================
check_chapters_html() {
    local file="$1"
    if [ ! -f "$file" ]; then
        echo "⚠️  $file 不存在，跳過檢查"
        return 0
    fi

    echo "📄 檢查 $file HTML結構..."

    local checks=0
    local total=5

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

# ============================================
# 檢查2：av-novels.html HTML 結構
# ============================================
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

# ============================================
# 檢查3：AV 章節完整性（新增！）
# 確保每個 chapter-*-av.html 都在 av-novels.html 中列出
# ============================================
check_av_completeness() {
    echo "📄 檢查 AV 章節完整性..."

    local av_dir="$WORKSPACE"
    local av_index="$WORKSPACE/av-novels.html"

    if [ ! -f "$av_index" ]; then
        echo "⚠️  av-novels.html 不存在，跳過檢查"
        return 0
    fi

    # 獲取所有 chapter-*-av.html 檔案（去掉路徑和 -av.html）
    local missing=0
    local total=0

    for av_file in "$av_dir"/chapter-*-av.html; do
        if [ -f "$av_file" ]; then
            total=$((total + 1))
            # 提取章節號，如 chapter-54-av.html -> 54
            chapter_num=$(basename "$av_file" | sed 's/chapter-\([0-9]*\)-av\.html/\1/')

            # 檢查這個章節是否在 av-novels.html 中
            if ! grep -q "chapter-$chapter_num-av.html" "$av_index"; then
                echo "❌ chapter-$chapter_num-av.html 未在 av-novels.html 中列出！"
                missing=$((missing + 1))
            fi
        fi
    done

    if [ $missing -eq 0 ]; then
        echo "✅ AV 章節完整性檢查通過 ($total 個章節全部在目錄中)"
        return 0
    else
        echo "❌ AV 章節完整性檢查失敗！$missing 個章節未在目錄中"
        return 1
    fi
}

# ============================================
# 主檢查流程
# ============================================

check_chapters_html "$WORKSPACE/chapters.html"
check_av_novels_html "$WORKSPACE/av-novels.html"
check_av_completeness  # 新增檢查！

echo ""
echo "✅ 所有檢查通過，可以推送！"
