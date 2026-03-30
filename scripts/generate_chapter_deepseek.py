#!/usr/bin/env python3
"""
DeepSeek版小說章節生成腳本
使用DeepSeek V3.2模型生成高質量小說內容
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

def get_previous_chapters_context(chapter_num, num_chapters=3):
    """獲取前幾章的內容作為上下文"""
    context_parts = []
    
    for i in range(max(1, chapter_num - num_chapters), chapter_num):
        filepath = os.path.join(NOVEL_DIR, f"chapter-{i}.html")
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read(5000)  # 讀取前5000字符
                    
                    # 提取標題
                    title_match = re.search(r'<title>第\d+章：([^<]+)</title>', content)
                    title = title_match.group(1) if title_match else f"第{i}章"
                    
                    # 提取部分內容
                    content_match = re.search(r'<div class="chapter-content">(.*?)</div>', content, re.DOTALL)
                    if content_match:
                        text_content = content_match.group(1)
                        # 清理HTML標籤，保留文本
                        text_content = re.sub(r'<[^>]+>', ' ', text_content)
                        text_content = re.sub(r'\s+', ' ', text_content).strip()
                        
                        if len(text_content) > 500:
                            text_content = text_content[:500] + "..."
                        
                        context_parts.append(f"【第{i}章：{title}】\n{text_content}")
            except Exception as e:
                log(f"讀取第{i}章錯誤: {e}")
    
    return "\n\n".join(context_parts) if context_parts else "這是故事的新開始。"

def generate_with_deepseek(chapter_num, previous_context):
    """使用DeepSeek V3.2生成章節內容"""
    api_key = get_api_key()
    if not api_key:
        log("⚠️ 未找到API密鑰，無法使用DeepSeek生成")
        return None, None
    
    # 構建詳細的提示詞
    prompt = f"""請創作小說《科技修真傳》的第{chapter_num}章。

## 故事背景
這是一部科技與修真結合的小說。主角林塵擁有「靈芯」系統，可以將現代科技與修真功法結合。
目前故事進展到林塵發現了遠古的「火種」系統，正在探索其奧秘。

## 前情提要
{previous_context}

## 寫作要求
1. **章節標題**：第{chapter_num}章：XXXXXX（4-6個字，如「火種初鳴」、「靈芯覺醒」等）
2. **內容長度**：1500-2000字
3. **格式**：直接寫正文，不需要任何HTML標籤、Markdown格式或額外說明
4. **風格**：保持科技感與修真玄幻結合，文筆流暢，有畫面感
5. **劇情**：要有懸念和推進，自然延續之前的故事線，可以引入新元素但保持連貫
6. **角色**：林塵（主角）、靈芯系統（AI助手）、觀察者（神秘存在）

## 輸出格式
請直接以「第{chapter_num}章：標題」開始，然後是正文內容。
不要添加「以下是第{chapter_num}章內容」等前言，直接開始故事。"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek/deepseek-v3.2",  # 使用DeepSeek V3.2
        "messages": [
            {
                "role": "system", 
                "content": "你是一位專業的網絡小說作家，擅長創作科技修真題材。請嚴格按照用戶要求輸出小說內容，不要添加任何解釋、前言或後記。直接輸出故事內容。"
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "max_tokens": 4000,  # 足夠生成2000字內容
        "temperature": 0.8,  # 稍高的創造性
        "top_p": 0.9,
        "frequency_penalty": 0.3,  # 減少重複
        "presence_penalty": 0.3,   # 鼓勵多樣性
    }
    
    try:
        log(f"使用DeepSeek V3.2生成第{chapter_num}章內容...")
        log(f"上下文長度: {len(previous_context)} 字符")
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=45  # 45秒超時，給DeepSeek足夠時間
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            log(f"DeepSeek生成成功，原始內容長度: {len(content)} 字符")
            
            # 提取標題
            title_match = re.search(r'第\d+章：[^\n]+', content)
            if title_match:
                chapter_title = title_match.group(0).strip()
                # 清理標題
                chapter_title = re.sub(r'[<>]', '', chapter_title)
                # 移除標題後的內容
                content_start = content.find('\n', title_match.end())
                if content_start != -1:
                    content = content[content_start:].strip()
                else:
                    content = ""
            else:
                # 生成默認標題
                import random
                title_options = ["靈芯共鳴", "火種覺醒", "能量波動", "空間扭曲", 
                               "修真突破", "科技融合", "遠古密碼", "系統升級"]
                chapter_title = f"第{chapter_num}章：{random.choice(title_options)}"
            
            log(f"提取標題: {chapter_title}")
            log(f"清理後內容長度: {len(content)} 字符")
            
            # 確保內容有基本長度
            if len(content) < 500:
                log("⚠️ 警告：生成內容可能過短")
            
            return content, chapter_title
        else:
            log(f"DeepSeek生成失敗: {response.status_code}")
            log(f"錯誤信息: {response.text[:200]}")
            return None, None
            
    except requests.exceptions.Timeout:
        log("❌ DeepSeek API請求超時（45秒）")
        return None, None
    except Exception as e:
        log(f"❌ DeepSeek生成異常: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def create_chapter_file(chapter_num, ai_content, chapter_title):
    """創建章節文件 - 使用直接版方法確保可靠性"""
    # 使用第65章作為模板（確保可靠性）
    source_file = os.path.join(NOVEL_DIR, "chapter-65.html")
    
    if not os.path.exists(source_file):
        log(f"❌ 錯誤：找不到源文件 {source_file}")
        return None, None
    
    try:
        # 讀取第65章
        with open(source_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        log(f"使用第65章作為模板，大小: {len(template_content)} 字節")
        
        # 替換標題（多個位置）
        old_title_pattern = r'第65章：觀察者的低語'
        new_content = re.sub(old_title_pattern, chapter_title, template_content)
        
        # 替換其他65為當前章節號
        new_content = new_content.replace('第65章', f'第{chapter_num}章')
        new_content = new_content.replace('chapter-65.html', f'chapter-{chapter_num}.html')
        
        # 更新導航鏈接
        prev_num = chapter_num - 1 if chapter_num > 1 else ""
        next_num = chapter_num + 1
        
        if prev_num:
            new_content = new_content.replace('chapter-64.html', f'chapter-{prev_num}.html')
            new_content = new_content.replace('第64章', f'第{prev_num}章')
        
        new_content = new_content.replace('chapter-66.html', f'chapter-{next_num}.html')
        
        # 查找並替換內容區域
        # 尋找 <div class="chapter-content"> 標籤
        content_start = new_content.find('<div class="chapter-content">')
        if content_start != -1:
            content_end = new_content.find('</div>', content_start)
            if content_end != -1:
                # 構建新的內容
                new_chapter_content = f"""<div class="chapter-content">
{ai_content}
</div>"""
                
                # 替換內容
                new_content = new_content[:content_start] + new_chapter_content + new_content[content_end+6:]
        
        # 寫入新文件
        filename = f"chapter-{chapter_num}.html"
        filepath = os.path.join(NOVEL_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        log(f"已創建: {filepath}")
        
        # 驗證
        with open(filepath, 'r', encoding='utf-8') as f:
            final_content = f.read()
            
            if chapter_title not in final_content:
                log(f"⚠️ 警告：標題未正確插入")
            
            if f'第{chapter_num}章' not in final_content:
                log(f"❌ 錯誤：章節號未正確替換")
                return None, None
            
            log(f"✅ 驗證通過，大小: {len(final_content)} 字節")
        
        return filename, chapter_title
        
    except Exception as e:
        log(f"❌ 創建章節文件錯誤: {e}")
        import traceback
        traceback.print_exc()
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
        commit_msg = f'feat: 新增第{chapter_num}章「{chapter_title}」（DeepSeek生成）'
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
    log("開始生成新章節（DeepSeek V3.2版）...")
    
    # 獲取下一個章節號
    next_chapter = get_next_chapter_number()
    log(f"準備生成: 第{next_chapter}章")
    
    # 獲取前幾章上下文
    previous_context = get_previous_chapters_context(next_chapter, 3)
    log(f"獲取前3章上下文完成")
    
    # 使用DeepSeek生成內容
    ai_content, chapter_title = generate_with_deepseek(next_chapter, previous_context)
    
    if not ai_content or not chapter_title:
        log("❌ DeepSeek生成失敗，使用備用方案")
        # 備用方案：使用直接版
        import subprocess
        result = subprocess.run(
            ["python3", os.path.join(WORKSPACE, "scripts/generate_chapter_direct.py")],
            capture_output=True,
            text=True,
            cwd=WORKSPACE
        )
        
        if result.returncode == 0:
            log("✅ 備用方案成功")
            return True
        else:
            log("❌ 備用方案也失敗")
            return False
    
    # 創建章節文件
    filename, final_title = create_chapter_file(next_chapter, ai_content, chapter_title)
    if not filename:
        log("❌ 創建章節文件失敗")
        return False
    
    # 更新網站列表
    if not update_website_lists():
        log("⚠️ 更新網站列表時遇到問題，但章節已生成")
    
    # 提交到GitHub
    if not git_commit_and_push(next_chapter, final_title):
        log("⚠️ Git推送時遇到問題，但章節已生成")
    
    log(f"✅ 第{next_chapter}章「{final_title}」生成完成！（使用DeepSeek V3.2）")
    log("=" * 50)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)