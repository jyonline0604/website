#!/usr/bin/env python3
"""
更新網站章節數量統計
自動從實際章節檔案計算數量並更新各頁面

使用方法：
    python3 update_chapter_counts.py

這個腳本會更新：
- author.html: 目前已有 X 章
- home.html: meta description 和 numberOfPages
- index.html: 登陸頁統計數字
"""

import re
import os
import glob

def count_chapters():
    """計算實際章節數量"""
    workspace = "/home/openclaw/.openclaw/workspace"
    os.chdir(workspace)
    
    # 計算 chapter-*.html 檔案數量（只計算 chapter-N.html 格式，排除 template 和其他）
    chapter_files = glob.glob("chapter-[0-9]*.html")
    # 只保留 chapter-數字.html 格式（如 chapter-1.html, chapter-101.html）
    chapter_files = [f for f in chapter_files if re.match(r'^chapter-\d+\.html$', f)]
    return len(chapter_files)

def update_author_html(count):
    """更新 author.html"""
    filepath = "/home/openclaw/.openclaw/workspace/author.html"
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新 chapterCount span
    pattern = r'<span id="chapterCount">\d+</span>'
    replacement = f'<span id="chapterCount">{count}</span>'
    new_content = re.sub(pattern, replacement, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"✅ author.html: 更新為 {count} 章")

def update_home_html(count):
    """更新 home.html"""
    filepath = "/home/openclaw/.openclaw/workspace/home.html"
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新 meta description 中的章節數量
    pattern = r'免費閱讀\d+\+章節'
    replacement = f'免費閱讀{count}+章節'
    new_content = re.sub(pattern, replacement, content)
    
    # 更新 numberOfPages
    pattern = r'"numberOfPages": \d+,'
    replacement = f'"numberOfPages": {count},'
    new_content = re.sub(pattern, replacement, new_content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"✅ home.html: 更新為 {count} 章")

def update_index_html(count):
    """更新 index.html"""
    filepath = "/home/openclaw/.openclaw/workspace/index.html"
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新 meta description
    pattern = r'免費閱讀\d+\+章節'
    replacement = f'免費閱讀{count}+章節'
    new_content = re.sub(pattern, replacement, content)
    
    # 更新 stat-number span（排除「每日」）
    # 只更新包含數字的 stat-number
    pattern = r'(<span class="stat-number">)(\d+)(\+</span>)'
    replacement = rf'\g<1>{count}\3'
    new_content = re.sub(pattern, replacement, new_content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"✅ index.html: 更新為 {count} 章")

def main():
    count = count_chapters()
    print(f"📊 計算到的章節數量：{count}")
    
    update_author_html(count)
    update_home_html(count)
    update_index_html(count)
    
    print(f"\n✅ 章節數量更新完成！")

if __name__ == "__main__":
    main()
