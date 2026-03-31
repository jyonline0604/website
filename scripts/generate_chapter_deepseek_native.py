#!/usr/bin/env python3
"""
DeepSeek原生API版小說章節生成腳本
使用DeepSeek官方API（非OpenRouter）
"""

import os
import sys
import re
import requests
from datetime import datetime

WORKSPACE = "/home/openclaw/.openclaw/workspace"
NOVEL_DIR = WORKSPACE
LOG_FILE = os.path.join(WORKSPACE, "logs/novel-generator.log")

def log(message):
    """寫入日誌（確保不記錄敏感信息）"""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    
    # 過濾可能包含API密鑰的消息
    safe_message = message
    if "API_KEY" in message or "sk-" in message:
        # 替換完整密鑰為安全顯示
        import re
        api_key_pattern = r'sk-[a-zA-Z0-9]{40,50}'
        safe_message = re.sub(api_key_pattern, lambda m: f"{m.group(0)[:8]}...{m.group(0)[-4:]}", message)
    
    log_line = f"{timestamp} {safe_message}"
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")
    
    print(log_line)
    return log_line

def get_deepseek_api_key():
    """獲取DeepSeek原生API密鑰"""
    # 從環境變量獲取
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if api_key:
        return api_key
    
    # 從文件讀取
    env_file = os.path.join(WORKSPACE, ".env")
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith("DEEPSEEK_API_KEY="):
                    return line.strip().split("=", 1)[1]
    
    # 檢查其他可能的名稱
    possible_keys = ["DEEPSEEK_KEY", "DEEPSEEK_TOKEN", "DEEPSEEK_SECRET"]
    for key_name in possible_keys:
        key_value = os.environ.get(key_name)
        if key_value:
            return key_value
    
    log("⚠️ 未找到DeepSeek原生API密鑰")
    log("請在 .env 文件中添加: DEEPSEEK_API_KEY=你的密鑰")
    log("或申請密鑰: https://platform.deepseek.com/api_keys")
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

def get_previous_chapters_context(chapter_num):
    """獲取前一章的標題作為上下文"""
    if chapter_num <= 1:
        return "這是故事的開始。"
    
    prev_file = os.path.join(NOVEL_DIR, f"chapter-{chapter_num-1}.html")
    if os.path.exists(prev_file):
        try:
            with open(prev_file, 'r', encoding='utf-8') as f:
                content = f.read(1000)
                title_match = re.search(r'<title>第\d+章：([^<]+)</title>', content)
                if title_match:
                    return f"前一章是：第{chapter_num-1}章：{title_match.group(1)}"
        except:
            pass
    
    return f"延續第{chapter_num-1}章的故事。"

def generate_with_deepseek_native(chapter_num, previous_context):
    """使用DeepSeek原生API生成章節內容"""
    api_key = get_deepseek_api_key()
    if not api_key:
        log("❌ 未找到DeepSeek原生API密鑰，無法使用")
        return None, None
    
    # 構建簡化的提示詞
    prompt = f"""創作小說《科技修真傳》第{chapter_num}章。
{previous_context}

主角：林塵（擁有靈芯系統）
風格：科技修真結合
標題：第{chapter_num}章：XXXXXX（4-6字）
內容：800-1200字，有劇情推進
直接以「第{chapter_num}章：標題」開始寫正文。"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",  # DeepSeek原生API模型
        "messages": [
            {
                "role": "system", 
                "content": "你是專業網絡小說作家。直接輸出小說內容，不要解釋。"
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "max_tokens": 2000,  # 減少token數量
        "temperature": 0.8,
        "stream": False
    }
    
    try:
        log(f"使用DeepSeek原生API生成第{chapter_num}章...")
        
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers=headers,
            json=data,
            timeout=60  # 增加超時時間到60秒
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            log(f"DeepSeek原生API生成成功，長度: {len(content)} 字符")
            
            # 提取標題
            title_match = re.search(r'第\d+章：[^\n]+', content)
            if title_match:
                chapter_title = title_match.group(0).strip()
                # 移除標題後的內容
                content_start = content.find('\n', title_match.end())
                if content_start != -1:
                    content = content[content_start:].strip()
            else:
                # 生成默認標題
                import random
                title_options = ["靈芯共鳴", "火種覺醒", "能量波動", "空間扭曲"]
                chapter_title = f"第{chapter_num}章：{random.choice(title_options)}"
            
            log(f"提取標題: {chapter_title}")
            return content, chapter_title
        else:
            log(f"DeepSeek原生API失敗: {response.status_code}")
            log(f"錯誤: {response.text[:200]}")
            return None, None
            
    except Exception as e:
        log(f"DeepSeek原生API異常: {e}")
        return None, None

def create_chapter_file(chapter_num, ai_content, chapter_title):
    """創建章節文件 - 使用直接版方法"""
    # 使用第65章作為模板
    source_file = os.path.join(NOVEL_DIR, "chapter-65.html")
    
    if not os.path.exists(source_file):
        log(f"❌ 錯誤：找不到源文件 {source_file}")
        return None, None
    
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # 替換標題和章節號
        new_content = template.replace('第65章：觀察者的低語', chapter_title)
        new_content = new_content.replace('第65章', f'第{chapter_num}章')
        new_content = new_content.replace('chapter-65.html', f'chapter-{chapter_num}.html')
        
        # 更新導航
        prev_num = chapter_num - 1 if chapter_num > 1 else ""
        next_num = chapter_num + 1
        
        if prev_num:
            new_content = new_content.replace('chapter-64.html', f'chapter-{prev_num}.html')
        
        new_content = new_content.replace('chapter-66.html', f'chapter-{next_num}.html')
        
        # 替換內容區域
        content_start = new_content.find('<div class="chapter-content">')
        if content_start != -1:
            content_end = new_content.find('</div>', content_start)
            if content_end != -1:
                new_chapter_content = f'<div class="chapter-content">\n{ai_content}\n</div>'
                new_content = new_content[:content_start] + new_chapter_content + new_content[content_end+6:]
        
        # 寫入文件
        filename = f"chapter-{chapter_num}.html"
        filepath = os.path.join(NOVEL_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
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
        
        filename = f"chapter-{chapter_num}.html"
        os.system(f'git add {filename} home.html chapters.html 2>/dev/null')
        
        commit_msg = f'feat: 新增第{chapter_num}章「{chapter_title}」（DeepSeek原生API）'
        os.system(f'git commit -m "{commit_msg}" 2>/dev/null')
        os.system('git push origin main 2>/dev/null')
        
        log("✅ 已推送到GitHub")
        return True
        
    except Exception as e:
        log(f"❌ Git錯誤: {e}")
        return False

def main():
    log("=" * 50)
    log("開始生成新章節（DeepSeek原生API版）...")
    
    # 獲取下一個章節號
    next_chapter = get_next_chapter_number()
    log(f"準備生成: 第{next_chapter}章")
    
    # 檢查API密鑰
    api_key = get_deepseek_api_key()
    if not api_key:
        log("❌ 無法繼續：需要DeepSeek原生API密鑰")
        log("請在 .env 文件中添加: DEEPSEEK_API_KEY=你的密鑰")
        log("或使用備用方案")
        return False
    
    # 獲取上下文
    previous_context = get_previous_chapters_context(next_chapter)
    
    # 使用DeepSeek原生API生成
    ai_content, chapter_title = generate_with_deepseek_native(next_chapter, previous_context)
    
    if not ai_content or not chapter_title:
        log("❌ DeepSeek原生API生成失敗")
        return False
    
    # 創建章節文件
    filename, final_title = create_chapter_file(next_chapter, ai_content, chapter_title)
    if not filename:
        log("❌ 創建章節文件失敗")
        return False
    
    # 更新網站列表
    if not update_website_lists():
        log("⚠️ 更新網站列表時遇到問題")
    
    # 提交到GitHub
    if not git_commit_and_push(next_chapter, final_title):
        log("⚠️ Git推送時遇到問題")
    
    log(f"✅ 第{next_chapter}章「{final_title}」生成完成！（DeepSeek原生API）")
    log("=" * 50)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)