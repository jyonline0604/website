#!/usr/bin/env python3
"""
修復版小說章節生成腳本
使用DeepSeek API生成真正的新內容
"""

import os
import sys
import re
import json
import requests
from datetime import datetime

WORKSPACE = "/home/openclaw/.openclaw/workspace"
NOVEL_DIR = WORKSPACE
LOG_FILE = os.path.join(WORKSPACE, "logs/novel-generator-fixed.log")

def log(message):
    """寫入日誌"""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_line = f"{timestamp} {message}"
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")
    
    print(log_line)
    return log_line

def get_deepseek_api_key():
    """獲取DeepSeek API密鑰"""
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
    
    log("⚠️ 未找到DeepSeek API密鑰")
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

def get_previous_chapter_content(chapter_num):
    """獲取前一章的內容片段作為上下文"""
    if chapter_num <= 1:
        return "這是故事的開始。主角林塵剛剛發現自己體內有一個神秘的靈芯系統。"
    
    prev_file = os.path.join(NOVEL_DIR, f"chapter-{chapter_num-1}.html")
    if os.path.exists(prev_file):
        try:
            with open(prev_file, 'r', encoding='utf-8') as f:
                content = f.read(5000)  # 讀取前5000字符
            
            # 提取內容區域
            content_start = content.find('<div class="content">')
            if content_start != -1:
                content_end = content.find('</div>', content_start)
                if content_end != -1:
                    chapter_content = content[content_start+20:content_end]
                    # 清理HTML標籤
                    chapter_content = re.sub(r'<[^>]+>', '', chapter_content)
                    # 取最後500字符作為上下文
                    return chapter_content[-500:] if len(chapter_content) > 500 else chapter_content
        except Exception as e:
            log(f"讀取前一章錯誤: {e}")
    
    return f"延續第{chapter_num-1}章的故事。"

def generate_chapter_with_ai(chapter_num, previous_context):
    """使用DeepSeek API生成章節內容"""
    api_key = get_deepseek_api_key()
    if not api_key:
        log("❌ 未找到DeepSeek API密鑰")
        return None, None
    
    # 構建更好的提示詞
    prompt = f"""請創作小說《科技修真傳》的第{chapter_num}章。

故事背景：
- 主角：林塵，擁有神秘的靈芯系統
- 世界觀：科技與修真結合的未來世界
- 風格：東方玄幻 + 科幻元素

前一章內容摘要：
{previous_context}

請創作第{chapter_num}章，要求：
1. 標題：第{chapter_num}章：[4-6字的創意標題]
2. 內容：800-1200字，有劇情推進
3. 風格：保持科技修真特色，有對話和場景描寫
4. 直接從「第{chapter_num}章：[標題]」開始寫正文
5. 使用中文，段落清晰

請直接輸出小說內容，不要添加任何解釋或說明。"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system", 
                "content": "你是一位專業的網絡小說作家，擅長創作科技修真題材的小說。請直接輸出小說正文，不要添加任何解釋、說明或額外文字。"
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "max_tokens": 2500,
        "temperature": 0.7,
        "stream": False
    }
    
    try:
        log(f"使用DeepSeek API生成第{chapter_num}章內容...")
        
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers=headers,
            json=data,
            timeout=120  # 120秒超時
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            log(f"AI生成成功，原始內容長度: {len(content)} 字符")
            
            # 提取標題
            title_match = re.search(r'第\d+章：([^\n]+)', content)
            if title_match:
                chapter_title = title_match.group(1).strip()
            else:
                # 生成默認標題
                import random
                titles = ["靈芯覺醒", "科技突破", "修真奇遇", "時空裂縫", "能量風暴", 
                         "虛空試煉", "意識融合", "維度跨越", "系統升級", "遠古密碼"]
                chapter_title = random.choice(titles)
                content = f"第{chapter_num}章：{chapter_title}\n\n{content}"
            
            log(f"提取標題: 第{chapter_num}章：{chapter_title}")
            return content, chapter_title
        else:
            log(f"❌ DeepSeek API錯誤: {response.status_code} - {response.text[:200]}")
            return None, None
            
    except requests.exceptions.Timeout:
        log("❌ DeepSeek API請求超時")
        return None, None
    except Exception as e:
        log(f"❌ DeepSeek API異常: {str(e)}")
        return None, None

def create_chapter_file(chapter_num, ai_content, chapter_title):
    """創建章節HTML文件"""
    try:
        # 讀取模板
        template_file = os.path.join(NOVEL_DIR, "chapter-template.html")
        if not os.path.exists(template_file):
            log(f"❌ 錯誤：找不到模板文件 {template_file}")
            return None, None
        
        with open(template_file, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # 清理AI內容，提取純文本段落
        paragraphs = []
        lines = ai_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('第') or '章：' not in line:  # 跳過標題行
                # 分割長段落
                if len(line) > 200:
                    # 簡單分割
                    parts = re.split(r'[。！？]', line)
                    for part in parts:
                        if part.strip():
                            paragraphs.append(part.strip() + '。')
                else:
                    paragraphs.append(line)
        
        # 創建HTML段落
        html_paragraphs = []
        for para in paragraphs[:15]:  # 最多15個段落
            if para:
                html_paragraphs.append(f'<p>{para}</p>')
        
        if not html_paragraphs:
            html_paragraphs = ['<p>（本章內容生成中...）</p>']
        
        chapter_content = '\n'.join(html_paragraphs)
        
        # 替換模板中的佔位符
        template = template.replace('{CHAPTER_TITLE}', chapter_title)
        template = template.replace('{CHAPTER_NUM}', str(chapter_num))
        template = template.replace('{CONTENT}', chapter_content)
        
        # 更新導航鏈接
        prev_num = chapter_num - 1 if chapter_num > 1 else ""
        next_num = chapter_num + 1
        
        if prev_num:
            template = template.replace('{PREV_NUM}', str(prev_num))
        else:
            template = template.replace('{PREV_NUM}', '1')
        
        template = template.replace('{NEXT_NUM}', str(next_num))
        
        # 寫入文件
        filename = f"chapter-{chapter_num}.html"
        filepath = os.path.join(NOVEL_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(template)
        
        log(f"已創建: {filename}")
        log(f"標題: 第{chapter_num}章：{chapter_title}")
        log(f"段落數: {len(html_paragraphs)}")
        
        return filename, chapter_title
        
    except Exception as e:
        log(f"❌ 創建章節文件錯誤: {str(e)}")
        return None, None

def update_novel_lists():
    """更新小說網站列表"""
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
            log(f"❌ 更新網站列表失敗: {result.stderr[:200]}")
            return False
            
    except Exception as e:
        log(f"❌ 調用更新腳本錯誤: {e}")
        return False

def main():
    """主函數"""
    log("=" * 60)
    log("開始修復版小說章節生成...")
    
    # 檢查需要修復的章節
    chapters_to_fix = [66, 67]
    
    for chapter_num in chapters_to_fix:
        log(f"\n處理第{chapter_num}章...")
        
        # 檢查章節是否存在
        chapter_file = os.path.join(NOVEL_DIR, f"chapter-{chapter_num}.html")
        if not os.path.exists(chapter_file):
            log(f"第{chapter_num}章不存在，跳過")
            continue
        
        # 檢查章節內容是否為佔位符
        with open(chapter_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "這是第{chapter_num}章的佔位內容" in content or "佔位內容" in content:
            log(f"第{chapter_num}章是佔位內容，需要重新生成")
            
            # 獲取前一章內容作為上下文
            previous_context = get_previous_chapter_content(chapter_num)
            log(f"上下文長度: {len(previous_context)} 字符")
            
            # 使用AI生成新內容
            ai_content, chapter_title = generate_chapter_with_ai(chapter_num, previous_context)
            
            if ai_content and chapter_title:
                # 備份舊文件
                backup_file = f"{chapter_file}.backup"
                import shutil
                shutil.copy2(chapter_file, backup_file)
                log(f"已備份舊文件到: {backup_file}")
                
                # 創建新文件
                filename, final_title = create_chapter_file(chapter_num, ai_content, chapter_title)
                
                if filename:
                    log(f"✅ 第{chapter_num}章重新生成成功")
                else:
                    log(f"❌ 第{chapter_num}章重新生成失敗，恢復備份")
                    shutil.copy2(backup_file, chapter_file)
            else:
                log(f"❌ 第{chapter_num}章AI生成失敗，保持原樣")
        else:
            log(f"第{chapter_num}章已有內容，跳過")
    
    # 更新網站列表
    log("\n更新網站列表...")
    update_novel_lists()
    
    log("=" * 60)
    log("修復完成！")

if __name__ == "__main__":
    main()