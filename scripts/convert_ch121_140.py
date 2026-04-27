#!/usr/bin/env python3
"""將 CH121-140 文本文件轉換為HTML格式（支持 UUID 文件名）"""

import re
import os

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="canonical" href="{canonical}">
    <link rel="prev" href="{prev_url}">
    <link rel="next" href="{next_url}">
    <style>
        :root {{
            --bg: #FAFBFC;
            --text: #1F2937;
            --accent: #6366F1;
            --border: #E5E7EB;
            --panel-bg: #FFFFFF;
            --font-size: 18px;
            --line-height: 1.8;
        }}
        body {{
            font-family: 'Noto Serif TC', serif;
            background: var(--bg);
            color: var(--text);
            line-height: var(--line-height);
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            font-size: 1.8em;
            text-align: center;
            padding: 30px 0;
            border-bottom: 2px solid var(--accent);
            margin-bottom: 30px;
        }}
        p {{
            text-indent: 2em;
            margin: 1em 0;
            font-size: var(--font-size);
        }}
        .nav {{
            display: flex;
            justify-content: space-between;
            padding: 20px 0;
            border-top: 1px solid var(--border);
            margin-top: 40px;
        }}
        .nav a {{
            color: var(--accent);
            text-decoration: none;
            padding: 10px 20px;
            border: 1px solid var(--accent);
            border-radius: 5px;
        }}
        .nav a:hover {{
            background: var(--accent);
            color: white;
        }}
    </style>
</head>
<body>
    <h1>{chapter_title}</h1>
    <main>
{content}
    </main>
    <nav class="nav">
        <a href="{prev_url}">← 上一章</a>
        <a href="{next_url}">下一章 →</a>
    </nav>
</body>
</html>"""

def extract_title_and_content(text):
    """從文本中提取標題和內容"""
    title_match = re.search(r'^#\s*第[一二三四五六七八九十百零\d]+章[·\s]+(.+)$', text, re.MULTILINE)
    if title_match:
        chapter_title = title_match.group(1).strip()
    else:
        chapter_title = "未定標題"
    
    content = re.sub(r'^#\s*第.+$\n', '', text, flags=re.MULTILINE)
    
    paragraphs = content.strip().split('\n')
    formatted_paras = []
    for p in paragraphs:
        p = p.strip()
        if p:
            formatted_paras.append(f'        <p>{p}</p>')
    
    return chapter_title, '\n'.join(formatted_paras)

def convert_chapter(text_file, chapter_num, prev_num, next_num, base_url="https://kofhk.com"):
    """轉換單一章節"""
    with open(text_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    title, content = extract_title_and_content(text)
    
    html = TEMPLATE.format(
        title=f'第{chapter_num}章：{title} - 萬古塵埃',
        canonical=f'{base_url}/chapter-{chapter_num}.html',
        prev_url=f'{base_url}/chapter-{prev_num}.html' if prev_num else '#',
        next_url=f'{base_url}/chapter-{next_num}.html' if next_num else '#',
        chapter_title=f'第{chapter_num}章 · {title}',
        content=content
    )
    
    return html

def main():
    inbound_dir = '/home/openclaw/.openclaw/media/inbound'
    
    # 處理的章節範圍
    chapters_to_process = range(121, 141)
    
    for ch_num in chapters_to_process:
        # 優先查找 ch{num}--- UUID 格式（最新上傳的版本）
        uuid_pattern = f'ch{ch_num}---'
        uuid_file = None
        for f in os.listdir(inbound_dir):
            if f.startswith(uuid_pattern) and f.endswith('.txt'):
                uuid_file = os.path.join(inbound_dir, f)
                break
        
        # 否則找 第{num}章---UUID 格式
        chapter_pattern = f'第{ch_num}章---'
        chapter_file = None
        if uuid_file is None:
            for f in os.listdir(inbound_dir):
                if f.startswith(chapter_pattern) and f.endswith('.txt'):
                    chapter_file = os.path.join(inbound_dir, f)
                    break
        
        target_file = uuid_file if uuid_file else chapter_file
        
        if target_file is None:
            print(f"CH{ch_num}: 找不到文件，跳過")
            continue
        
        prev_num = ch_num - 1 if ch_num > 1 else None
        next_num = ch_num + 1
        
        print(f"處理 CH{ch_num}: {os.path.basename(target_file)}")
        
        html = convert_chapter(target_file, ch_num, prev_num, next_num)
        
        output_file = f'/home/openclaw/.openclaw/workspace/chapter-{ch_num}.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"  已保存: {output_file}")

if __name__ == '__main__':
    main()
