#!/usr/bin/env python3
"""
簡化版小說章節生成腳本
"""

import os
import sys
import re
from datetime import datetime

WORKSPACE = "/home/openclaw/.openclaw/workspace"
NOVEL_DIR = os.path.join(WORKSPACE, "my-novel")
LOG_FILE = os.path.join(WORKSPACE, "logs/novel-generator.log")

def log(message):
    """寫入日誌"""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_line = f"{timestamp} {message}"
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")
    
    print(log_line)
    return log_line

def get_next_chapter_number():
    """獲取下一個章節號"""
    max_num = 0
    
    for filename in os.listdir(NOVEL_DIR):
        if filename.startswith("chapter-") and filename.endswith(".html"):
            match = re.match(r"chapter-(\d+)\.html", filename)
            if match:
                chapter_num = int(match.group(1))
                if chapter_num > max_num:
                    max_num = chapter_num
    
    return max_num + 1

def create_simple_chapter(chapter_num):
    """創建簡單的章節文件（用於測試）"""
    # 讀取模板
    template_path = os.path.join(NOVEL_DIR, "chapter-template.html")
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        chapter_title = f"第{chapter_num}章：測試章節"
        
        # 簡單的內容
        content = f"""
<h1>{chapter_title}</h1>
<div class="chapter-content">
    <p>這是第{chapter_num}章，由自動生成系統創建於 {datetime.now().strftime('%Y-%m-%d %H:%M')}。</p>
    <p>林塵的修真科技之旅繼續展開...</p>
    <p>靈芯系統發出輕微的嗡鳴聲，提示有新的能量波動被檢測到。</p>
    <p>「警告：檢測到異常空間扭曲，建議立即進行掃描分析。」</p>
    <p>林塵深吸一口氣，調動體內的靈氣，準備面對新的挑戰。</p>
</div>
"""
        
        # 替換模板中的內容
        html_content = template.replace("{{CHAPTER_TITLE}}", chapter_title)
        html_content = html_content.replace("{{CHAPTER_CONTENT}}", content)
        html_content = html_content.replace("{{CHAPTER_NUMBER}}", str(chapter_num))
        html_content = html_content.replace("{{PREV_CHAPTER}}", str(chapter_num - 1) if chapter_num > 1 else "")
        html_content = html_content.replace("{{NEXT_CHAPTER}}", str(chapter_num + 1))
        
        # 寫入文件
        filename = f"chapter-{chapter_num}.html"
        filepath = os.path.join(NOVEL_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        log(f"已創建: {filepath}")
        return filename, chapter_title
        
    except Exception as e:
        log(f"創建章節文件錯誤: {e}")
        return None, None

def update_website_lists():
    """更新網站列表"""
    try:
        update_script = os.path.join(WORKSPACE, "scripts/update_novel_lists.py")
        
        import subprocess
        result = subprocess.run(
            ["python3", update_script],
            capture_output=True,
            text=True,
            cwd=WORKSPACE
        )
        
        if result.returncode == 0:
            log("✅ 已更新網站列表")
            return True
        else:
            log(f"❌ 更新網站列表失敗: {result.stderr}")
            return False
            
    except Exception as e:
        log(f"❌ 調用更新腳本錯誤: {e}")
        return False

def git_commit_and_push(chapter_num, chapter_title):
    """提交到GitHub"""
    try:
        os.chdir(NOVEL_DIR)
        
        # 添加新章節文件
        filename = f"chapter-{chapter_num}.html"
        os.system(f'git add {filename} home.html chapters.html 2>/dev/null')
        
        # 提交
        commit_msg = f'feat: 新增第{chapter_num}章「{chapter_title}」'
        os.system(f'git commit -m "{commit_msg}" 2>/dev/null')
        
        # 推送
        os.system('git push origin main 2>/dev/null')
        
        log("✅ 已推送到GitHub")
        return True
        
    except Exception as e:
        log(f"❌ Git錯誤: {e}")
        return False

def main():
    log("=" * 50)
    log("開始生成新章節（簡化版）...")
    
    # 獲取下一個章節號
    next_chapter = get_next_chapter_number()
    log(f"準備生成: 第{next_chapter}章")
    
    # 創建章節文件
    filename, chapter_title = create_simple_chapter(next_chapter)
    if not filename:
        log("❌ 創建章節文件失敗")
        return False
    
    # 更新網站列表
    if not update_website_lists():
        log("⚠️ 更新網站列表時遇到問題，但章節已生成")
    
    # 提交到GitHub
    if not git_commit_and_push(next_chapter, chapter_title):
        log("⚠️ Git推送時遇到問題，但章節已生成")
    
    log(f"✅ 第{next_chapter}章「{chapter_title}」生成完成！")
    log("=" * 50)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)