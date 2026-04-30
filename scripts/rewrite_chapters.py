#!/usr/bin/env python3
"""
使用AI重新撰寫並添加標點的分段
"""

import os
import sys
import re

WORKSPACE = "/home/openclaw/.openclaw/workspace"
NOVEL_DIR = WORKSPACE
TXT_DIR = "/home/openclaw/.openclaw/media/inbound"

# 添加路徑
sys.path.append(os.path.join(WORKSPACE, 'scripts'))
from ai_multimodel import MultiModelAI

def rewrite_with_punctuation(text, chapter_num):
    """使用AI重新撰寫並添加標點"""
    prompt = f"""請將以下的小說章節內容進行修正：
1. 添加適當的標點符號（句號、逗號、頓號等）
2. 將內容合理分段（每段200-500字）
3. 保持原有的人物名稱和情節

原內容：
{text}

請直接輸出修正後的內容，不要添加任何解釋。"""
    
    try:
        ai = MultiModelAI()
        result = ai.generate_with_fallback(prompt, max_tokens=4000)
        return result
    except Exception as e:
        print(f"❌ AI生成失敗: {e}")
        return None

def read_txt_content(chapter_num):
    """讀取txt文件的內容 - 選擇最早上傳的版本"""
    candidates = []
    for filename in os.listdir(TXT_DIR):
        if f'第{chapter_num}章' in filename and filename.endswith('.txt'):
            txt_path = os.path.join(TXT_DIR, filename)
            try:
                stat = os.stat(txt_path)
                candidates.append((stat.st_mtime, stat.st_size, txt_path, filename))
            except:
                pass
    
    if not candidates:
        return None, None
    
    # 選擇最早上傳的文件
    candidates.sort(key=lambda x: x[0])  # 按mtime，最早的優先
    _, _, txt_path, filename = candidates[0]
    
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content, filename

def generate_html(chapter_num, title, content):
    """生成HTML文件"""
    template_path = os.path.join(NOVEL_DIR, "chapter-template.html")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # 替換標題
    full_title = f'第{chapter_num}章 · {title} - 萬古塵埃'
    template = template.replace('{title}', full_title)
    template = template.replace('<h1>{chapter_title}</h1>', f'<h1>第{chapter_num}章 · {title}</h1>')
    template = template.replace('{CHAPTER_NUM}', str(chapter_num))
    
    # 處理 prev/next 鏈接
    prev_num = chapter_num - 1 if chapter_num > 1 else 1
    next_num = chapter_num + 1
    
    template = template.replace('{prev_url}', f'chapter-{prev_num}.html')
    template = template.replace('{next_url}', f'chapter-{next_num}.html')
    template = template.replace('{canonical}', f'chapter-{chapter_num}.html')
    
    # 生成段落
    paragraphs = []
    
    # 按句號分割並分組
    sentences = re.split(r'([。！？])', content)
    
    current_para = []
    for i, sent in enumerate(sentences):
        if sent in '。！？':
            current_para.append(sent)
            # 每4-6句成為一個段落
            if len(current_para) >= 8 or (i < len(sentences) - 1 and sentences[i+1] and sentences[i+1][0] not in '「『【'):
                para_text = ''.join(current_para)
                if para_text.strip():
                    paragraphs.append(f'<p>{para_text.strip()}</p>')
                current_para = []
        elif sent.strip():
            current_para.append(sent)
    
    if current_para:
        para_text = ''.join(current_para)
        if para_text.strip():
            paragraphs.append(f'<p>{para_text.strip()}</p>')
    
    # 插入內容
    main_content = '\n'.join(paragraphs)
    
    main_start = template.find('<main>')
    main_end = template.find('</main>')
    
    if main_start != -1 and main_end != -1:
        new_template = template[:main_start + 6] + '\n' + main_content + '\n    ' + template[main_end:]
    else:
        new_template = template.replace('{content}', main_content)
    
    return new_template

def extract_title_and_content(txt_content):
    """從txt內容提取標題和正文"""
    lines = txt_content.strip().split('\n')
    
    title = None
    content_lines = []
    found_title = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if ('第' in line and '章' in line) or line.startswith('#'):
            match = re.search(r'第[零一二三四五六七八九十百千\d]+章[：:·\s]+(.+)', line)
            if match:
                title = match.group(1).strip()
                found_title = True
                continue
            elif '第' in line and '章' in line:
                match2 = re.search(r'第[零一二三四五六七八九十百千\d]+章[：:·]?\s*(.+)', line)
                if match2:
                    title = match2.group(1).strip()
                    found_title = True
                    continue
        elif not found_title and line:
            if len(line) < 50 and ('第' in line or '#' in line):
                match3 = re.search(r'第[零一二三四五六七八九十百千\d]+章[：:·\s]*([^\s#].+)', line)
                if match3:
                    title = match3.group(1).strip()
                    found_title = True
                    continue
                elif '第' in line and '章' in line:
                    title = line.replace('#', '').strip()
                    found_title = True
                    continue
        
        if found_title and line:
            content_lines.append(line)
    
    if not title:
        title = "待確認"
    
    full_content = '\n'.join(content_lines)
    
    return title, full_content

def process_chapter(chapter_num):
    """處理單個章節"""
    print(f"📖 第 {chapter_num} 章...", end=" ", flush=True)
    
    # 讀取txt
    txt_content, txt_filename = read_txt_content(chapter_num)
    if not txt_content:
        print(f"❌ 找不到txt文件")
        return False
    
    print(f"📄 ({len(txt_content)}字)", end=" ", flush=True)
    
    # 提取標題和內容
    title, content = extract_title_and_content(txt_content)
    
    if not content:
        print(f"❌ 無內容")
        return False
    
    # 使用AI重新撰寫
    print("✍️ AI重寫中...", end=" ", flush=True)
    rewritten = rewrite_with_punctuation(content, chapter_num)
    
    if not rewritten:
        print(f"❌ AI重寫失敗")
        return False
    
    print(f"✅ ({len(rewritten)}字)", end=" ", flush=True)
    
    # 生成HTML
    html_content = generate_html(chapter_num, title, rewritten)
    
    # 寫入文件
    output_path = os.path.join(NOVEL_DIR, f"chapter-{chapter_num}.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅")
    return True

def main():
    print("=== AI重新撰寫並添加標點 (361-400) ===\n")
    
    for ch in range(361, 401):
        success = process_chapter(ch)
        if not success:
            print(f"⚠️ 第 {ch} 章處理失敗，跳過")
    
    print("\n完成!")

if __name__ == "__main__":
    main()