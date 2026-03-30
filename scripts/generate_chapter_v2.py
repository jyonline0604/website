#!/usr/bin/env python3
"""
小說章節生成腳本 v2
使用 OpenRouter API 生成新章節，並自動更新網站
"""

import os
import sys
import json
import re
import time
from datetime import datetime
import requests

# 設置環境變量
os.environ['PATH'] = '/home/openclaw/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'

WORKSPACE = "/home/openclaw/.openclaw/workspace"
NOVEL_DIR = os.path.join(WORKSPACE, "my-novel")
LOG_FILE = os.path.join(WORKSPACE, "logs/novel-generator.log")

# 從環境變量獲取API密鑰
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    # 從文件讀取
    env_file = os.path.join(WORKSPACE, ".env")
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith("OPENROUTER_API_KEY="):
                    OPENROUTER_API_KEY = line.strip().split("=", 1)[1]
                    break

if not OPENROUTER_API_KEY:
    log("❌ 錯誤：未設置 OPENROUTER_API_KEY")
    sys.exit(1)

def log(message):
    """寫入日誌"""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_line = f"{timestamp} {message}"
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")
    
    print(log_line)
    return log_line

def get_latest_chapters(count=3):
    """獲取最新幾章的摘要"""
    chapters = []
    
    # 獲取所有章節文件
    chapter_files = []
    for filename in os.listdir(NOVEL_DIR):
        if filename.startswith("chapter-") and filename.endswith(".html"):
            match = re.match(r"chapter-(\d+)\.html", filename)
            if match:
                chapter_num = int(match.group(1))
                if chapter_num > 0:  # 排除模板
                    chapter_files.append((chapter_num, filename))
    
    # 按章節號排序
    chapter_files.sort(key=lambda x: x[0], reverse=True)
    
    # 讀取最新幾章
    for chapter_num, filename in chapter_files[:count]:
        filepath = os.path.join(NOVEL_DIR, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read(5000)  # 只讀前5000字節
            
            # 提取標題
            title_match = re.search(r'<title>(第\d+章：.*?)</title>', content)
            if title_match:
                title = title_match.group(1)
            else:
                title = f"第{chapter_num}章"
            
            # 提取正文前幾段
            content_match = re.search(r'<div class="chapter-content">(.*?)</div>', content, re.DOTALL)
            if content_match:
                text = content_match.group(1)
                # 清理HTML標籤
                text = re.sub(r'<[^>]+>', ' ', text)
                text = re.sub(r'\s+', ' ', text).strip()
                excerpt = text[:200] + "..." if len(text) > 200 else text
            else:
                excerpt = ""
            
            chapters.append({
                "number": chapter_num,
                "title": title,
                "excerpt": excerpt
            })
            
        except Exception as e:
            log(f"讀取章節 {filename} 錯誤: {e}")
    
    return chapters

def generate_chapter_content(previous_chapters):
    """使用OpenRouter API生成新章節內容"""
    
    # 構建提示詞
    prompt = f"""你是一位專業的小說作家，正在創作一部名為《科技修真傳》的網絡小說。
主角：林塵，一個擁有靈芯系統的現代修真者。

故事背景：
這是一個科技與修真結合的世界。林塵意外獲得了一個名為「靈芯」的系統，可以將現代科技與修真功法結合。
目前故事進展到林塵發現了遠古的「火種」系統，正在探索其奧秘。

最近章節摘要：
"""
    
    for i, chap in enumerate(previous_chapters, 1):
        prompt += f"{i}. {chap['title']}: {chap['excerpt']}\n"
    
    prompt += f"""
請根據以上故事進展，創作下一章（第{previous_chapters[0]['number'] + 1}章）。
要求：
1. 保持一貫的寫作風格：科技感與修真玄幻結合
2. 延續當前劇情線索
3. 章節標題格式：第X章：標題（4-6個字）
4. 內容長度：2000-3000字
5. 使用HTML格式，包含適當的段落標籤
6. 故事要有懸念和推進

請直接輸出完整的HTML章節內容，包括標題和正文。"""

    # API請求
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "minimax/minimax-m2.7",  # 使用MiniMax模型
        "messages": [
            {"role": "system", "content": "你是一位專業的網絡小說作家，擅長創作科技修真題材的小說。"},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 4000,
        "temperature": 0.7
    }
    
    try:
        log("正在調用OpenRouter API生成章節內容...")
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            log(f"API返回內容長度: {len(content)} 字")
            return content
        else:
            log(f"API錯誤: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        log(f"API調用異常: {e}")
        return None

def create_chapter_file(chapter_num, content):
    """創建章節HTML文件"""
    # 讀取模板
    template_path = os.path.join(NOVEL_DIR, "chapter-template.html")
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # 提取標題
        title_match = re.search(r'第\d+章：.*', content)
        if title_match:
            chapter_title = title_match.group(0)
        else:
            # 從內容中找標題
            title_match = re.search(r'<h1[^>]*>(.*?)</h1>', content)
            if title_match:
                chapter_title = title_match.group(1)
            else:
                chapter_title = f"第{chapter_num}章"
        
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
    """更新網站列表（首頁和章節目錄）"""
    try:
        # 調用我們之前創建的更新腳本
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
        os.system(f'git add {filename} home.html chapters.html')
        
        # 提交
        commit_msg = f'feat: 新增第{chapter_num}章「{chapter_title}」'
        os.system(f'git commit -m "{commit_msg}"')
        
        # 推送
        os.system('git push origin main')
        
        log("✅ 已推送到GitHub")
        return True
        
    except Exception as e:
        log(f"❌ Git錯誤: {e}")
        return False

def main():
    log("=" * 50)
    log("開始生成新章節...")
    
    # 獲取當前進度
    previous_chapters = get_latest_chapters(3)
    if not previous_chapters:
        log("❌ 無法獲取之前章節信息")
        return False
    
    current_chapter = previous_chapters[0]["number"]
    next_chapter = current_chapter + 1
    
    log(f"當前階段: 新紀元 (第{current_chapter}章)")
    log(f"準備生成: 第{next_chapter}章")
    log(f"已獲取 {len(previous_chapters)} 章摘要")
    
    # 生成新章節內容
    content = generate_chapter_content(previous_chapters)
    if not content:
        log("❌ 內容生成失敗")
        return False
    
    # 創建章節文件
    filename, chapter_title = create_chapter_file(next_chapter, content)
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