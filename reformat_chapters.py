#!/usr/bin/env python3
import re
import os

template_path = '/home/openclaw/.openclaw/workspace/my-novel/chapter-template.html'
chapters_dir = '/home/openclaw/.openclaw/workspace/my-novel/'

with open(template_path, 'r', encoding='utf-8') as f:
    template = f.read()

for i in range(1, 62):
    chapter_file = os.path.join(chapters_dir, f'chapter-{i}.html')
    if not os.path.exists(chapter_file):
        continue
    
    with open(chapter_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract chapter title
    title_match = re.search(r'第(\d+)章：([^<]+)', content)
    if title_match:
        chapter_num = title_match.group(1)
        chapter_title = title_match.group(2).strip()
    else:
        chapter_num = str(i)
        chapter_title = '未知章節'
    
    # Extract article content
    content_match = re.search(r'<div class="content">([\s\S]*?)</div>\s*</article>', content)
    if content_match:
        article_content = content_match.group(1).strip()
    else:
        # Try different patterns
        content_match = re.search(r'<div class="chapter">([\s\S]*?)</div>', content)
        if content_match:
            article_content = content_match.group(1).strip()
        else:
            article_content = '<p>內容載入中...</p>'
    
    # Clean up the content - extract just paragraphs
    paragraphs = re.findall(r'<p>(.*?)</p>', article_content, re.DOTALL)
    cleaned_content = ''
    for p in paragraphs:
        p = p.strip()
        if p:
            cleaned_content += f'            <p>{p}</p>\n'
    
    if not cleaned_content:
        cleaned_content = '            <p>內容載入中...</p>\n'
    
    prev_num = i - 1 if i > 1 else 1
    next_num = i + 1 if i < 61 else 61
    
    # Generate new chapter
    new_chapter = template
    new_chapter = new_chapter.replace('{CHAPTER_NUM}', chapter_num)
    new_chapter = new_chapter.replace('{CHAPTER_TITLE}', chapter_title)
    new_chapter = new_chapter.replace('{PREV_NUM}', str(prev_num))
    new_chapter = new_chapter.replace('{NEXT_NUM}', str(next_num))
    new_chapter = new_chapter.replace('{CONTENT}', cleaned_content)
    
    with open(chapter_file, 'w', encoding='utf-8') as f:
        f.write(new_chapter)
    
    print(f'Updated chapter-{i}.html: {chapter_title}')

print('\nDone! All chapters reformatted.')
