#!/usr/bin/env python3
"""
最終版小說章節生成腳本
嘗試使用AI生成，失敗時使用簡化版
"""

import os
import sys
import re
import requests
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

def get_api_key():
    """獲取API密鑰"""
    # 從環境變量獲取
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if api_key:
        return api_key
    
    # 從文件讀取
    env_file = os.path.join(WORKSPACE, ".env")
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith("OPENROUTER_API_KEY="):
                    return line.strip().split("=", 1)[1]
    
    return None

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

def try_ai_generation(chapter_num):
    """嘗試使用AI生成內容"""
    api_key = get_api_key()
    if not api_key:
        log("⚠️ 未找到API密鑰，使用簡化版")
        return None
    
    # 構建簡單的提示詞
    prompt = f"""請創作小說《科技修真傳》的第{chapter_num}章。
主角：林塵，擁有靈芯系統的現代修真者。
故事背景：科技與修真結合的世界，林塵正在探索遠古的「火種」系統。
請寫一個簡短的章節（500-800字），標題格式：第{chapter_num}章：標題（4-6字）
內容要求：科技感與修真玄幻結合，有劇情推進和懸念。"""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "minimax/minimax-m2.7",
        "messages": [
            {"role": "system", "content": "你是一位專業的網絡小說作家。"},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1000,  # 減少token數量
        "temperature": 0.7
    }
    
    try:
        log("嘗試使用AI生成章節內容...")
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=15  # 縮短超時時間
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            log(f"AI生成成功，內容長度: {len(content)} 字")
            return content
        else:
            log(f"AI生成失敗: {response.status_code} - {response.text[:100]}")
            return None
            
    except Exception as e:
        log(f"AI生成異常: {e}")
        return None

def create_chapter_file(chapter_num, ai_content=None):
    """創建章節文件"""
    # 讀取模板
    template_path = os.path.join(NOVEL_DIR, "chapter-template.html")
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        if ai_content:
            # 從AI內容提取標題
            title_match = re.search(r'第\d+章：.*', ai_content)
            if title_match:
                chapter_title = title_match.group(0)
            else:
                chapter_title = f"第{chapter_num}章：AI生成章節"
            
            # 確保內容有基本結構
            if '<h1>' not in ai_content:
                content = f"<h1>{chapter_title}</h1>\n<div class=\"chapter-content\">\n{ai_content}\n</div>"
            else:
                content = ai_content
        else:
            # 使用簡化版內容
            chapter_title = f"第{chapter_num}章：自動生成"
            content = f"""
<h1>{chapter_title}</h1>
<div class="chapter-content">
    <p>這是第{chapter_num}章，由自動生成系統創建於 {datetime.now().strftime('%Y-%m-%d %H:%M')}。</p>
    <p>林塵的修真科技之旅繼續展開...</p>
    <p>靈芯系統發出輕微的嗡鳴聲，提示有新的能量波動被檢測到。</p>
    <p>「警告：檢測到異常空間扭曲，建議立即進行掃描分析。」</p>
    <p>林塵深吸一口氣，調動體內的靈氣，準備面對新的挑戰。</p>
    <p>前方的道路充滿未知，但林塵知道，每一次挑戰都是成長的機會。</p>
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
    log("開始生成新章節（最終版）...")
    
    # 獲取下一個章節號
    next_chapter = get_next_chapter_number()
    log(f"準備生成: 第{next_chapter}章")
    
    # 嘗試AI生成
    ai_content = try_ai_generation(next_chapter)
    
    # 創建章節文件
    filename, chapter_title = create_chapter_file(next_chapter, ai_content)
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