#!/usr/bin/env python3
"""為文字版章節添加漫畫版導航按鈕"""

import os
import re

CHAPTERS_DIR = "/home/openclaw/.openclaw/workspace"

# 需要添加的CSS
MANGA_CSS = """
        .manga-btn {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white;
            padding: 10px 25px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .manga-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(245, 158, 11, 0.5);
        }"""

def add_manga_button(chapter_num):
    """為指定章節添加漫畫按鈕"""
    filename = f"chapter-{chapter_num}.html"
    filepath = os.path.join(CHAPTERS_DIR, filename)
    
    if not os.path.exists(filepath):
        print(f"⚠️ {filename} 不存在")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 檢查是否已有漫畫按鈕
    if 'manga-btn' in content:
        print(f"⏭️ {filename} 已有漫畫按鈕")
        return True
    
    # 添加CSS（如果還沒有）
    if '.manga-btn' not in content:
        # 在 .nav a:hover 後面添加漫畫按鈕樣式
        content = re.sub(
            r'(\.nav a:hover \{\s*background: var\(\--accent\);\s*color: white;\s*\})',
            r'\1\n' + MANGA_CSS.strip(),
            content
        )
    
    # 替換導航列，添加漫畫按鈕
    manga_url = f"https://kofhk.com/manga/chapter-{chapter_num}/"
    prev_url = f"https://kofhk.com/chapter-{chapter_num - 1}.html" if chapter_num > 1 else "#"
    next_url = f"https://kofhk.com/chapter-{chapter_num + 1}.html"
    
    # 構建新的導航
    prev_text = "← 上一章" if chapter_num > 1 else "← 首頁"
    prev_href = prev_url if chapter_num > 1 else "https://kofhk.com/"
    
    new_nav = f'''    <nav class="nav">
        <a href="{prev_href}">{prev_text}</a>
        <a href="{manga_url}" class="manga-btn">🎨 漫畫版</a>
        <a href="{next_url}">下一章 →</a>
    </nav>'''
    
    # 替換現有的導航
    old_nav_pattern = r'<nav class="nav">.*?</nav>'
    content = re.sub(old_nav_pattern, new_nav, content, flags=re.DOTALL)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ {filename} 已添加漫畫按鈕")
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 指定章節
        chapter = int(sys.argv[1])
        add_manga_button(chapter)
    else:
        # 為所有章節添加（1-310）
        for i in range(1, 311):
            add_manga_button(i)
        print("\n✅ 全部完成!")
