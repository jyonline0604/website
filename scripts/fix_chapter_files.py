#!/usr/bin/env python3
"""
修復小說章節HTML文件
- 每個文件只保留第一個章節的內容
- 修復導航鏈接
"""

import os
import re
import glob
import shutil

NOVEL_DIR = "/home/openclaw/.openclaw/workspace/my-novel"

def extract_first_chapter(html_content):
    """從拼接的HTML中提取第一個章節"""
    first_html_end = html_content.find('</html>')
    if first_html_end == -1:
        return html_content
    return html_content[:first_html_end + len('</html>')]

def extract_chapter_number(html_content):
    """從HTML中提取章節號"""
    match = re.search(r'<h1>第(\d+)章', html_content)
    if match:
        return int(match.group(1))
    return None

def extract_chapter_title(html_content):
    """從HTML中提取章節標題"""
    match = re.search(r'<h1>第\d+章：([^<]+)</h1>', html_content)
    if match:
        return match.group(1)
    return ""

def fix_navigation_links(html_content, chapter_num, total_chapters):
    """修復導航鏈接"""
    
    # 修復上一章鏈接
    if chapter_num > 1:
        prev_link = '<a href="chapter-{}.html">← 上一章</a>'.format(chapter_num - 1)
    else:
        prev_link = '<span style="opacity:0.3">← 上一章</span>'
    
    # 修復下一章鏈接
    if chapter_num < total_chapters:
        next_link = '<a href="chapter-{}.html">下一章 →</a>'.format(chapter_num + 1)
    else:
        next_link = '<span style="opacity:0.3">下一章 →</span>'
    
    # 替換上一章導航 (bottom-nav)
    pattern_prev = r'(<nav class="bottom-nav">\s*<a href="chapter-\d+\.html">← 上一章</a>|<nav class="bottom-nav">\s*<span style="opacity:0\.3">← 上一章</span>)'
    html_content = re.sub(pattern_prev, prev_link, html_content, flags=re.DOTALL)
    
    # 替換下一章導航 (bottom-nav)
    pattern_next = r'(<a href="chapter-\d+\.html">下一章 →</a>\s*</nav>|<span style="opacity:0\.3">下一章 →</span>\s*</nav>)'
    html_content = re.sub(pattern_next, next_link + '</nav>', html_content, flags=re.DOTALL)
    
    # 修復 header 中的章節標題
    html_content = re.sub(
        r'<span class="chapter-title">第\d+章</span>',
        '<span class="chapter-title">第{}章</span>'.format(chapter_num),
        html_content
    )
    
    # 修復 page title
    title = extract_chapter_title(html_content)
    html_content = re.sub(
        r'<title>第\d+章：[^<]+</title>',
        '<title>第{}章：{}</title>'.format(chapter_num, title),
        html_content
    )
    
    # 修復 prevChapter 函數
    if chapter_num > 1:
        prev_func = "function prevChapter() {{ window.location.href = 'chapter-{}.html'; }}".format(chapter_num - 1)
    else:
        prev_func = "function prevChapter() {{ }}"
    
    html_content = re.sub(
        r'function prevChapter\(\) \{[^}]+\}',
        prev_func,
        html_content
    )
    
    # 修復 nextChapter 函數
    if chapter_num < total_chapters:
        next_func = "function nextChapter() {{ window.location.href = 'chapter-{}.html'; }}".format(chapter_num + 1)
    else:
        next_func = "function nextChapter() {{ }}"
    
    html_content = re.sub(
        r'function nextChapter\(\) \{[^}]+\}',
        next_func,
        html_content
    )
    
    return html_content

def fix_file(filepath, total_chapters):
    """修復單個文件"""
    print("處理: {}".format(filepath))
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    content = extract_first_chapter(content)
    
    chapter_num = extract_chapter_number(content)
    if chapter_num is None:
        print("  ⚠️ 無法識別章節號，跳過")
        return False
    
    content = fix_navigation_links(content, chapter_num, total_chapters)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("  ✅ 第{}章已修復".format(chapter_num))
    return True

def main():
    print("=" * 60)
    print("小說章節HTML文件修復腳本")
    print("=" * 60)
    
    # 獲取所有章節文件
    all_files = glob.glob(os.path.join(NOVEL_DIR, "chapter-*.html"))
    chapter_files = []
    for f in all_files:
        if 'chapter-template' not in f:
            match = re.search(r'chapter-(\d+)', f)
            if match:
                chapter_files.append((int(match.group(1)), f))
    
    chapter_files.sort(key=lambda x: x[0])
    chapter_files = [f[1] for f in chapter_files]
    
    total_chapters = len(chapter_files)
    print("找到 {} 個章節文件\n".format(total_chapters))
    
    # 備份所有文件
    print("創建備份...")
    backup_dir = os.path.join(NOVEL_DIR, "backup_before_fix")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    for f in chapter_files:
        backup_path = os.path.join(backup_dir, os.path.basename(f))
        shutil.copy2(f, backup_path)
    print("備份完成: {}\n".format(backup_dir))
    
    # 修復每個文件
    print("開始修復...")
    success_count = 0
    for filepath in chapter_files:
        if fix_file(filepath, total_chapters):
            success_count += 1
    
    print("\n" + "=" * 60)
    print("修復完成！成功修復 {}/{} 個文件".format(success_count, total_chapters))
    print("=" * 60)
    
    # 驗證修復結果
    print("\n驗證修復結果...")
    with open(chapter_files[0], 'r', encoding='utf-8') as f:
        content = f.read()
    html_count = content.count('</html>')
    print("chapter-1.html 包含 {} 個 HTML 文檔 (應該是 1)".format(html_count))
    
    with open(chapter_files[-1], 'r', encoding='utf-8') as f:
        content = f.read()
    html_count_last = content.count('</html>')
    last_chap_num = len(chapter_files)
    print("chapter-{}.html 包含 {} 個 HTML 文檔 (應該是 1)".format(last_chap_num, html_count_last))

if __name__ == "__main__":
    main()
