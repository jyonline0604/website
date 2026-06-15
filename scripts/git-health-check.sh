#!/bin/bash
# Git Health Check - 檢測並自動修復常見 Git 問題
# 
# 檢查項目：
# 1. Stuck rebase (卡住的 rebase)
# 2. Merge conflicts (合併衝突)
# 3. Detached HEAD
# 4. Un-pushed commits
#
# 使用方式：
#   bash scripts/git-health-check.sh           # 檢查並報告
#   bash scripts/git-health-check.sh --fix     # 檢查並自動修復

set -e

WORKSPACE="/home/openclaw/.openclaw/workspace"
cd "$WORKSPACE"

FIX_MODE=false
[[ "$1" == "--fix" ]] && FIX_MODE=true

ISSUES=0
REPORT=""

check_rebase() {
    local rebase_dir
    rebase_dir=$(git rev-parse --git-dir 2>/dev/null)/rebase-merge
    local rebase_apply
    rebase_apply=$(git rev-parse --git-dir 2>/dev/null)/rebase-apply
    
    if [ -d "$rebase_dir" ] || [ -d "$rebase_apply" ]; then
        ISSUES=$((ISSUES + 1))
        REPORT+="⚠️  找到卡住的 rebase"
        
        if [ -d "$rebase_dir" ]; then
            local onto
            onto=$(cat "$rebase_dir/onto" 2>/dev/null | head -c 12)
            local orig
            orig=$(cat "$rebase_dir/orig-head" 2>/dev/null | head -c 12)
            REPORT+=" (onto: $onto, orig: $orig)"
        fi
        
        REPORT+="\n"
        
        if $FIX_MODE; then
            echo "🔧 自動 abort rebase..."
            if git rebase --abort 2>/dev/null; then
                REPORT+="✅ 已自動 abort 卡住的 rebase\n"
            else
                REPORT+="❌ 無法自動 abort rebase（可能需要手動處理）\n"
            fi
        fi
    fi
}

check_detached_head() {
    local branch
    branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
    if [ "$branch" = "HEAD" ]; then
        ISSUES=$((ISSUES + 1))
        REPORT+="⚠️  Detached HEAD 狀態\n"
        
        if $FIX_MODE; then
            local current_hash
            current_hash=$(git rev-parse HEAD)
            echo "🔧 修復 detached HEAD -> 重置 main 到當前 commit..."
            git branch -f main "$current_hash"
            git checkout main 2>/dev/null || true
            REPORT+="✅ 已修復 detached HEAD，main 已移動到 $current_hash\n"
        fi
    fi
}

check_merge_conflicts() {
    if git diff --check --cached 2>/dev/null | grep -q "conflict\|<<<<<<<\|=======\|>>>>>>>"; then
        ISSUES=$((ISSUES + 1))
        REPORT+="⚠️  存在未解決的合併衝突\n"
        
        if $FIX_MODE; then
            local conflict_files
            conflict_files=$(git diff --name-only --diff-filter=U 2>/dev/null | head -5)
            REPORT+="⚠️  衝突文件（頭5個）：\n$conflict_files\n"
            REPORT+="⚠️  無法自動修復衝突，請手動處理\n"
        fi
    fi
    
    # 也檢查 MERGE_HEAD
    if [ -f "$(git rev-parse --git-dir)/MERGE_HEAD" ]; then
        ISSUES=$((ISSUES + 1))
        REPORT+="⚠️  進行中的 merge（MERGE_HEAD 存在）\n"
        
        if $FIX_MODE; then
            echo "🔧 嘗試自動 abort merge..."
            if git merge --abort 2>/dev/null; then
                REPORT+="✅ 已自動 abort merge\n"
            else
                REPORT+="❌ 無法自動 abort merge\n"
            fi
        fi
    fi
}

check_unpushed_commits() {
    local unpushed
    unpushed=$(git log --oneline origin/main..HEAD 2>/dev/null | wc -l)
    if [ "$unpushed" -gt 0 ]; then
        ISSUES=$((ISSUES + 1))
        REPORT+="⚠️  有 $unpushed 個未推送的 commit\n"
        
        # 檢查是否包含新章節
        local chapter_commits
        chapter_commits=$(git log --oneline origin/main..HEAD -- 'chapter-*.html' 2>/dev/null | wc -l)
        if [ "$chapter_commits" -gt 0 ]; then
            REPORT+="📚 其中 $chapter_commits 個 commit 包含章節文件\n"
        fi
        
        if $FIX_MODE; then
            echo "🔧 自動推送未推送的 commit..."
            if git push origin main 2>&1; then
                REPORT+="✅ 已成功推送 $unpushed 個 commit\n"
            else
                local push_result=$?
                if [ $push_result -eq 128 ]; then
                    REPORT+="⚠️  Push 被拒絕（可能分支分歧），嘗試 force push...\n"
                    if git push origin main --force-with-lease 2>&1; then
                        REPORT+="✅ Force push 成功\n"
                    else
                        REPORT+="❌ Force push 也失敗，請手動檢查\n"
                    fi
                else
                    REPORT+="❌ Push 失敗（錯誤碼: $push_result），請手動檢查\n"
                fi
            fi
        fi
    fi
}

check_diff_with_remote() {
    local local_sha origin_sha
    local_sha=$(git rev-parse HEAD)
    origin_sha=$(git rev-parse origin/main 2>/dev/null || echo "none")
    
    if [ "$local_sha" != "$origin_sha" ]; then
        # 已經被 check_unpushed_commits 覆蓋
        true
    fi
}

# ========== 主流程 ==========

if $FIX_MODE; then
    echo "🔧 Git Health Check (Auto-Fix Mode)"
else
    echo "🔍 Git Health Check (Report Only)"
fi
echo "=========================================="
echo ""

check_rebase
check_detached_head
check_merge_conflicts
check_unpushed_commits

echo ""
echo "=========================================="

if [ $ISSUES -eq 0 ]; then
    echo "✅ Git 狀態健康，一切正常"
    exit 0
else
    echo -e "$REPORT"
    echo "⚠️  發現 $ISSUES 個問題"
    if $FIX_MODE; then
        echo "🔧 自動修復完成"
    else
        echo "💡 使用 --fix 參數可自動修復可修復的問題"
    fi
    exit 0
fi
