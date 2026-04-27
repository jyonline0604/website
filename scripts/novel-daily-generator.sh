#!/bin/bash
# 每日小說章節生成腳本（多模型版本）
# 使用備用策略：DeepSeek → MiniMax → OpenRouter → Gemini → 本地模板

# 載入環境變量
set -a
source /home/openclaw/.openclaw/workspace/.env
set +a

# 設置完整 PATH（Cron 需要）
export PATH="/home/openclaw/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

WORKSPACE="/home/openclaw/.openclaw/workspace"
NOVEL_DIR="$WORKSPACE"
LOG_FILE="$WORKSPACE/logs/novel-daily.log"

echo "==========================================================" >> "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 開始多模型每日章節生成..." >> "$LOG_FILE"

cd "$WORKSPACE" || exit 1

# 執行多模型章節生成器
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 執行多模型生成器..." >> "$LOG_FILE"
python3 "$WORKSPACE/scripts/novel_generator_multimodel.py" --daily --count 3 >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 多模型生成成功" >> "$LOG_FILE"
    
    # 推送新章節到 GitHub
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 推送章節到 GitHub..." >> "$LOG_FILE"
    cd "$NOVEL_DIR" || exit 1
    git add -A >> "$LOG_FILE" 2>&1
    git commit -m "docs: auto-generate chapter $(date '+%Y-%m-%d')" >> "$LOG_FILE" 2>&1
    git push origin main >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 已推送到 GitHub" >> "$LOG_FILE"
        
        # 更新作者頁面和統計數字
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 更新作者頁面和統計數字..." >> "$LOG_FILE"
        python3 "$WORKSPACE/scripts/update_author_stats.py" >> "$LOG_FILE" 2>&1
        
        # 更新章節數量統計（author.html, home.html, index.html）
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 更新章節數量統計..." >> "$LOG_FILE"
        python3 "$WORKSPACE/scripts/update_chapter_counts.py" >> "$LOG_FILE" 2>&1
        
        # 如果有更新，再次提交
        cd "$NOVEL_DIR" || exit 1
        if git status --porcelain | grep -q "author.html\|av-novels.html\|home.html\|index.html"; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] 提交更新的統計數字..." >> "$LOG_FILE"
            git add author.html av-novels.html home.html index.html >> "$LOG_FILE" 2>&1
            git commit -m "docs: update chapter statistics" >> "$LOG_FILE" 2>&1
            git push origin main >> "$LOG_FILE" 2>&1
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 已更新統計數字" >> "$LOG_FILE"
        else
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] ℹ️ 統計數字已是最新" >> "$LOG_FILE"
        fi
        
        # 排序章節順序（確保正確）
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 排序章節順序..." >> "$LOG_FILE"
        python3 "$WORKSPACE/scripts/update_author_stats.py" >> "$LOG_FILE" 2>&1
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ GitHub 推送失敗" >> "$LOG_FILE"
    fi
    
    cd "$WORKSPACE" || exit 1
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 多模型生成失敗，退出碼: $EXIT_CODE" >> "$LOG_FILE"
    
    # 嘗試備用方案
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 嘗試備用方案..." >> "$LOG_FILE"
    
    # 備用1: 使用簡單生成器
    python3 "$WORKSPACE/scripts/generate_novel_chapter_simple.py" >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 備用方案成功" >> "$LOG_FILE"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 所有方案都失敗" >> "$LOG_FILE"
    fi
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 生成任務完成" >> "$LOG_FILE"
echo "==========================================================" >> "$LOG_FILE"

# 返回最後的退出碼
exit $EXIT_CODE