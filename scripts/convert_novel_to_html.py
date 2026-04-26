#!/usr/bin/env python3
"""將文本格式的小說章節轉換為HTML格式"""

import re
import os
import sys

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
    # 提取章節標題，如 "第一章 · 標題" 或 "第一章 標題"
    title_match = re.search(r'^#\s*第[一二三四五六七八九十百零\d]+章[·\s]+(.+)$', text, re.MULTILINE)
    if title_match:
        chapter_title = title_match.group(1).strip()
    else:
        chapter_title = "未定標題"
    
    # 移除 markdown 標題
    content = re.sub(r'^#\s*第.+$\n', '', text, flags=re.MULTILINE)
    
    # 將段落分割並格式化
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
    
    # 提取章節號碼
    ch_num_match = re.search(r'第([零一二三四五六七八九十百\d]+)章', title)
    if ch_num_match:
        display_num = ch_num_match.group(1)
    else:
        display_num = str(chapter_num)
    
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
    import glob
    
    # 獲取所有 txt 文件
    txt_files = sorted(glob.glob('/home/openclaw/.openclaw/media/inbound/第*章*.txt'))
    
    print(f"找到 {len(txt_files)} 個章節文件")
    
    for txt_file in txt_files:
        # 提取章節號
        match = re.search(r'第([零一二三四五六七八九十百\d]+)章', os.path.basename(txt_file))
        if match:
            # 將中文數字轉換為數字
            cn_nums = {'零':0,'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10}
            num_str = match.group(1)
            if num_str in cn_nums:
                ch_num = cn_nums[num_str]
            elif '十' in num_str:
                # 處理十一, 十二等
                parts = num_str.split('十')
                if parts[0] == '':
                    ch_num = 10
                else:
                    ch_num = cn_nums.get(parts[0], 1) * 10 + cn_nums.get(parts[1], 0)
            else:
                ch_num = cn_nums.get(num_str, int(num_str) if num_str.isdigit() else 0)
        else:
            print(f"無法從檔案名提取章節號: {txt_file}")
            continue
        
        prev_num = ch_num - 1 if ch_num > 1 else None
        next_num = ch_num + 1
        
        print(f"處理: {txt_file} -> Chapter {ch_num}")
        
        html = convert_chapter(txt_file, ch_num, prev_num, next_num)
        
        output_file = f'/home/openclaw/.openclaw/workspace/chapter-{ch_num}.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"  已保存: {output_file}")

if __name__ == '__main__':
    main()
