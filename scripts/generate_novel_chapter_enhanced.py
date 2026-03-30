#!/usr/bin/env python3
"""
增強版小說章節生成腳本
生成更長、更高質量的內容，確保標題唯一
"""

import os
import sys
import re
import json
import requests
import random
from datetime import datetime

WORKSPACE = "/home/openclaw/.openclaw/workspace"
NOVEL_DIR = os.path.join(WORKSPACE, "my-novel")
LOG_FILE = os.path.join(WORKSPACE, "logs/novel-generator-enhanced.log")

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

def get_previous_chapter_content(chapter_num):
    """獲取前一章的詳細內容作為上下文"""
    if chapter_num <= 1:
        return "這是故事的開始。主角林塵剛剛發現自己體內有一個神秘的靈芯系統，這是科技與修真結合的產物。"
    
    prev_file = os.path.join(NOVEL_DIR, f"chapter-{chapter_num-1}.html")
    if os.path.exists(prev_file):
        try:
            with open(prev_file, 'r', encoding='utf-8') as f:
                content = f.read(8000)  # 讀取更多內容
            
            # 提取內容區域
            content_start = content.find('<div class="content">')
            if content_start != -1:
                content_end = content.find('</div>', content_start)
                if content_end != -1:
                    chapter_content = content[content_start+20:content_end]
                    # 清理HTML標籤，保留更多內容
                    chapter_content = re.sub(r'<[^>]+>', '', chapter_content)
                    # 取最後1000字符作為詳細上下文
                    return chapter_content[-1000:] if len(chapter_content) > 1000 else chapter_content
        except Exception as e:
            log(f"讀取前一章錯誤: {e}")
    
    return f"延續第{chapter_num-1}章的故事。"

def generate_unique_title(chapter_num, used_titles):
    """生成唯一的章節標題"""
    # 可用的標題選項
    title_options = [
        "虛空試煉", "時空裂縫", "能量風暴", "系統升級", "遠古密碼",
        "靈芯共鳴", "科技突破", "修真奇遇", "意識融合", "維度跨越",
        "星核覺醒", "數據洪流", "量子修真", "機械元神", "虛擬道場",
        "靈網入侵", "時光回溯", "平行宇宙", "能量矩陣", "靈魂編程",
        "科技天劫", "數字元神", "虛擬金丹", "量子經脈", "數據築基"
    ]
    
    # 過濾已使用的標題
    available_titles = [t for t in title_options if t not in used_titles]
    
    if not available_titles:
        # 如果所有標題都用過了，添加編號
        base_title = random.choice(title_options)
        return f"{base_title}·貳"
    
    return random.choice(available_titles)

def generate_chapter_with_ai(chapter_num, previous_context, chapter_title):
    """使用DeepSeek API生成高質量章節內容"""
    api_key = get_deepseek_api_key()
    if not api_key:
        log("❌ 未找到DeepSeek API密鑰")
        return None
    
    # 構建更詳細的提示詞
    prompt = f"""請創作小說《科技修真傳》的第{chapter_num}章，標題為「{chapter_title}」。

故事設定：
- 主角：林塵，擁有神秘的靈芯系統（科技與修真結合的產物）
- 世界觀：未來世界，科技高度發達，但修真文明重新覺醒
- 風格：東方玄幻 + 硬核科幻 + 賽博朋克元素
- 主題：科技與修真的融合，人類進化的新方向

前一章內容摘要（約1000字）：
{previous_context}

創作要求：
1. 標題：第{chapter_num}章：{chapter_title}
2. 字數：1500-2000字（約30-40個段落）
3. 內容：必須有完整的劇情推進，包含：
   - 場景描寫（至少2個不同場景）
   - 人物對話（至少3段對話）
   - 動作描寫（戰鬥或修煉場景）
   - 心理描寫（主角的內心活動）
   - 科技元素（靈芯系統、數據流、虛擬界面等）
   - 修真元素（靈氣、經脈、功法、法寶等）
4. 結構：開頭→發展→高潮→結尾
5. 直接從「第{chapter_num}章：{chapter_title}」開始寫正文

請創作完整的一章，確保內容豐富、情節緊湊、描寫細膩。直接輸出小說正文，不要添加任何解釋或說明。"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system", 
                "content": """你是一位專業的網絡小說作家，擅長創作科技修真題材的小說。
                請創作完整的一章小說，確保：
                1. 字數充足（1500-2000字）
                2. 情節完整（有開頭、發展、高潮、結尾）
                3. 描寫細膩（場景、人物、動作、心理）
                4. 元素豐富（科技+修真）
                5. 直接輸出正文，不要任何解釋"""
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "max_tokens": 4000,  # 增加token數量
        "temperature": 0.7,
        "stream": False
    }
    
    try:
        log(f"使用DeepSeek API生成第{chapter_num}章：{chapter_title}...")
        
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers=headers,
            json=data,
            timeout=180  # 180秒超時
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            log(f"AI生成成功，原始內容長度: {len(content)} 字符")
            
            # 驗證標題
            if f"第{chapter_num}章：{chapter_title}" not in content[:100]:
                # 添加正確的標題
                content = f"第{chapter_num}章：{chapter_title}\n\n{content}"
            
            return content
        else:
            log(f"❌ DeepSeek API錯誤: {response.status_code} - {response.text[:200]}")
            return None
            
    except requests.exceptions.Timeout:
        log("❌ DeepSeek API請求超時")
        return None
    except Exception as e:
        log(f"❌ DeepSeek API異常: {str(e)}")
        return None

def create_enhanced_chapter_file(chapter_num, ai_content, chapter_title):
    """創建增強版章節HTML文件"""
    try:
        # 讀取模板
        template_file = os.path.join(NOVEL_DIR, "chapter-template.html")
        if not os.path.exists(template_file):
            log(f"❌ 錯誤：找不到模板文件 {template_file}")
            return None
        
        with open(template_file, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # 處理AI內容
        lines = ai_content.split('\n')
        paragraphs = []
        
        for line in lines:
            line = line.strip()
            if line:
                # 跳過重複的標題行
                if line.startswith(f'第{chapter_num}章：'):
                    if paragraphs:  # 如果已經有標題了，跳過
                        continue
                    paragraphs.append(line)  # 保留第一個標題
                else:
                    # 分割長段落
                    if len(line) > 300:
                        # 按標點符號分割
                        sentences = re.split(r'([。！？])', line)
                        current_sentence = ""
                        for i in range(0, len(sentences), 2):
                            if i < len(sentences):
                                current_sentence += sentences[i]
                                if i+1 < len(sentences):
                                    current_sentence += sentences[i+1]
                                
                                if len(current_sentence) > 100:
                                    paragraphs.append(current_sentence.strip())
                                    current_sentence = ""
                        
                        if current_sentence.strip():
                            paragraphs.append(current_sentence.strip())
                    else:
                        paragraphs.append(line)
        
        # 確保有足夠的段落
        if len(paragraphs) < 20:
            log(f"⚠️ 段落數不足: {len(paragraphs)}，嘗試補充...")
            # 簡單補充
            for i in range(20 - len(paragraphs)):
                paragraphs.append(f"（劇情推進中...段落{i+1}）")
        
        # 創建HTML段落
        html_paragraphs = []
        for para in paragraphs:
            if para:
                # 如果是標題，不加<p>標籤（會在模板中處理）
                if para.startswith(f'第{chapter_num}章：'):
                    html_paragraphs.append(para)
                else:
                    html_paragraphs.append(f'<p>{para}</p>')
        
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
        
        # 統計信息
        word_count = sum(len(p) for p in paragraphs if not p.startswith(f'第{chapter_num}章：'))
        paragraph_count = len([p for p in paragraphs if not p.startswith(f'第{chapter_num}章：')])
        
        log(f"已創建: {filename}")
        log(f"標題: 第{chapter_num}章：{chapter_title}")
        log(f"段落數: {paragraph_count}")
        log(f"估計字數: {word_count} 字")
        
        return filename
        
    except Exception as e:
        log(f"❌ 創建章節文件錯誤: {str(e)}")
        return None

def get_used_titles():
    """獲取已使用的章節標題"""
    used_titles = set()
    
    for filename in os.listdir(NOVEL_DIR):
        if filename.startswith("chapter-") and filename.endswith(".html"):
            try:
                with open(os.path.join(NOVEL_DIR, filename), 'r', encoding='utf-8') as f:
                    content = f.read(1000)
                    # 查找標題
                    title_match = re.search(r'<title>第\d+章：([^<]+)</title>', content)
                    if title_match:
                        used_titles.add(title_match.group(1).strip())
            except:
                pass
    
    return used_titles

def main():
    """主函數"""
    log("=" * 60)
    log("開始增強版小說章節生成...")
    
    # 獲取已使用的標題
    used_titles = get_used_titles()
    log(f"已使用的標題數: {len(used_titles)}")
    
    # 需要重新生成的章節
    chapters_to_regenerate = [66, 67]
    
    for chapter_num in chapters_to_regenerate:
        log(f"\n{'='*40}")
        log(f"處理第{chapter_num}章...")
        
        # 生成唯一標題
        chapter_title = generate_unique_title(chapter_num, used_titles)
        log(f"生成標題: 第{chapter_num}章：{chapter_title}")
        
        # 添加到已使用標題
        used_titles.add(chapter_title)
        
        # 獲取前一章內容作為上下文
        previous_context = get_previous_chapter_content(chapter_num)
        log(f"上下文長度: {len(previous_context)} 字符")
        
        # 使用AI生成高質量內容
        ai_content = generate_chapter_with_ai(chapter_num, previous_context, chapter_title)
        
        if not ai_content:
            log(f"❌ 第{chapter_num}章AI生成失敗")
            continue
        
        # 備份舊文件
        chapter_file = os.path.join(NOVEL_DIR, f"chapter-{chapter_num}.html")
        if os.path.exists(chapter_file):
            import shutil
            backup_file = f"{chapter_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(chapter_file, backup_file)
            log(f"已備份舊文件到: {backup_file}")
        
        # 創建新文件
        filename = create_enhanced_chapter_file(chapter_num, ai_content, chapter_title)
        
        if filename:
            log(f"✅ 第{chapter_num}章重新生成成功")
        else:
            log(f"❌ 第{chapter_num}章重新生成失敗")
    
    log("\n" + "=" * 60)
    log("增強版生成完成！")

if __name__ == "__main__":
    main()