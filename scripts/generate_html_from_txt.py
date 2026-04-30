#!/usr/bin/env python3
"""
從txt文件生成HTML章節
直接讀取帶標點的txt文件，生成標準HTML
"""

import os
import re
import sys

WORKSPACE = "/home/openclaw/.openclaw/workspace"
NOVEL_DIR = WORKSPACE
TXT_DIR = "/home/openclaw/.openclaw/media/inbound"

def read_txt_content(chapter_num):
    """讀取txt文件的內容 - 優先選擇最新上傳的（時戳更新）"""
    candidates = []
    for filename in os.listdir(TXT_DIR):
        if f'第{chapter_num}章' in filename and filename.endswith('.txt'):
            txt_path = os.path.join(TXT_DIR, filename)
            try:
                stat = os.stat(txt_path)
                candidates.append((stat.st_mtime, txt_path, filename))
            except:
                pass
    
    if not candidates:
        return None, None
    
    # 選擇最新上傳的（mtime最大）
    candidates.sort(key=lambda x: x[0], reverse=True)
    _, txt_path, filename = candidates[0]
    
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content, filename

def extract_title_and_content(txt_content):
    """從txt內容提取標題和正文"""
    lines = txt_content.strip().split('\n')
    
    # 找到標題行（第一行或含有「第X章」的行）
    title = None
    content_lines = []
    found_title = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 檢查是否是標題行
        if ('第' in line and '章' in line) or line.startswith('#'):
            # 可能是標題
            match = re.search(r'第[零一二三四五六七八九十百千\d]+章[：:·\s]+(.+)', line)
            if match:
                title = match.group(1).strip()
                found_title = True
            elif '第' in line and '章' in line:
                # 標題在行內
                match2 = re.search(r'第[零一二三四五六七八九十百千\d]+章[：:·]?\s*(.+)', line)
                if match2:
                    title = match2.group(1).strip()
                    found_title = True
        elif not found_title and line:
            # 還沒找到標題，可能是標題行
            if len(line) < 50 and ('第' in line or '#' in line):
                match3 = re.search(r'第[零一二三四五六七八九十百千\d]+章[：:·\s]*([^\s#].+)', line)
                if match3:
                    title = match3.group(1).strip()
                    found_title = True
                    continue
                elif '第' in line and '章' in line:
                    title = line.replace('#', '').strip()
                    found_title = True
        
        if found_title and line and '第' not in line:
            content_lines.append(line)
        elif not found_title:
            content_lines.append(line)
    
    # 如果沒找到標題，用默認
    if not title:
        title = "待確認"
    
    # 合併內容行
    full_content = '\n'.join(content_lines)
    
    return title, full_content

def generate_html(chapter_num, title, content):
    """生成HTML文件"""
    template_path = os.path.join(NOVEL_DIR, "chapter-template.html")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # 替換標題
    template = template.replace('{title}', f'第{chapter_num}章 · {title} - 萬古塵埃')
    
    # 處理 prev/next 鏈接
    prev_num = chapter_num - 1 if chapter_num > 1 else 1
    next_num = chapter_num + 1
    
    template = template.replace('{prev_url}', f'chapter-{prev_num}.html')
    template = template.replace('{next_url}', f'chapter-{next_num}.html')
    template = template.replace('{canonical}', f'chapter-{chapter_num}.html')
    
    # 生成段落
    # 清理內容並分段
    paragraphs = []
    
    # 按句號分割，但保留句號
    sentences = re.split(r'([。！？])', content)
    
    current_para = []
    for i, sent in enumerate(sentences):
        if sent in '。！？':
            current_para.append(sent)
            # 每3-5句成為一個段落
            if len(current_para) >= 6 or (i < len(sentences) - 1 and sentences[i+1] and sentences[i+1][0] not in '「『【'):
                para_text = ''.join(current_para)
                if para_text.strip():
                    paragraphs.append(f'<p>{para_text.strip()}</p>')
                current_para = []
        elif sent.strip():
            current_para.append(sent)
    
    # 最後一段
    if current_para:
        para_text = ''.join(current_para)
        if para_text.strip():
            paragraphs.append(f'<p>{para_text.strip()}</p>')
    
    # 插入內容
    main_content = '\n'.join(paragraphs)
    
    # 找到 <main> 位置
    main_start = template.find('<main>')
    main_end = template.find('</main>')
    
    if main_start != -1 and main_end != -1:
        new_template = template[:main_start + 6] + '\n' + main_content + '\n    ' + template[main_end:]
    else:
        # 找不到main，用content替代
        new_template = template.replace('{content}', main_content)
    
    return new_template

def process_chapter(chapter_num):
    """處理單個章節"""
    print(f"📖 第 {chapter_num} 章...", end=" ")
    
    # 讀取txt
    txt_content, txt_filename = read_txt_content(chapter_num)
    if not txt_content:
        print(f"❌ 找不到txt文件")
        return False
    
    print(f"📄 ({txt_filename})", end=" ")
    
    # 提取標題和內容
    title, content = extract_title_and_content(txt_content)
    
    if not content:
        print(f"❌ 無內容")
        return False
    
    # 生成HTML
    html_content = generate_html(chapter_num, title, content)
    
    # 寫入文件
    output_path = os.path.join(NOVEL_DIR, f"chapter-{chapter_num}.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ ({title})")
    return True

def main():
    print("=== 從txt生成HTML ===\n")
    
    # 處理 351-360
    for ch in range(351, 361):
        process_chapter(ch)
    
    print("\n完成!")

if __name__ == "__main__":
    main()