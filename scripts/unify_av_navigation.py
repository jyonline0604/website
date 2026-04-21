#!/usr/bin/env python3
"""
統一有聲畫章節導航列格式
按照第60章格式標準化所有有聲畫章節的導航列
"""
import os
import re
import glob

workspace = "/home/openclaw/.openclaw/workspace"
os.chdir(workspace)

# 第60章標準導航列模板
STANDARD_NAV_TEMPLATE = '''    <nav aria-label="主要導航" class="nav">
        <a href="chapter-{chapter}.html">← 文字版</a>
        <a href="chapter-{prev_chapter}-av.html">第{prev_chapter}章</a>
        <a href="chapter-{next_chapter}-av.html">第{next_chapter}章</a>
        <a href="av-novels.html">📚 目錄</a>
    </nav>'''

def extract_chapter_number(filename):
    """從文件名中提取章節號碼"""
    match = re.search(r'chapter-(\d+)-av\.html', filename)
    if match:
        return int(match.group(1))
    return None

def get_prev_next_chapters(chapter_num):
    """獲取上一章和下一章的章節號碼"""
    prev_chapter = chapter_num - 1
    next_chapter = chapter_num + 1
    
    # 檢查章節是否存在
    prev_exists = os.path.exists(f"chapter-{prev_chapter}-av.html")
    next_exists = os.path.exists(f"chapter-{next_chapter}-av.html")
    
    return prev_chapter, next_chapter, prev_exists, next_exists

def fix_navigation_in_file(filename):
    """修復單個文件的導航列"""
    chapter_num = extract_chapter_number(filename)
    if not chapter_num:
        print(f"❌ 無法從文件名提取章節號碼: {filename}")
        return False
    
    print(f"🔧 處理第{chapter_num}章: {filename}")
    
    # 讀取文件內容
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找現有的導航列
    nav_pattern = r'<nav[^>]*>.*?</nav>'
    nav_match = re.search(nav_pattern, content, re.DOTALL)
    
    if not nav_match:
        print(f"  ⚠️ 未找到導航列，跳過")
        return False
    
    old_nav = nav_match.group(0)
    print(f"  找到導航列: {old_nav[:50]}...")
    
    # 獲取上一章和下一章信息
    prev_chapter, next_chapter, prev_exists, next_exists = get_prev_next_chapters(chapter_num)
    
    # 構建新的導航列
    if prev_exists and next_exists:
        # 有上一章和下一章
        new_nav = STANDARD_NAV_TEMPLATE.format(
            chapter=chapter_num,
            prev_av=prev_chapter,
            prev_chapter=prev_chapter,
            next_av=next_chapter,
            next_chapter=next_chapter
        )
    elif prev_exists and not next_exists:
        # 只有上一章（可能是最後一章）
        new_nav = f'''    <nav aria-label="主要導航" class="nav">
        <a href="chapter-{chapter_num}.html">← 文字版</a>
        <a href="chapter-{prev_chapter}-av.html">第{prev_chapter}章</a>
        <a href="av-novels.html">📚 目錄</a>
    </nav>'''
    elif not prev_exists and next_exists:
        # 只有下一章（可能是第一章）
        new_nav = f'''    <nav aria-label="主要導航" class="nav">
        <a href="chapter-{chapter_num}.html">← 文字版</a>
        <a href="chapter-{next_chapter}-av.html">第{next_chapter}章</a>
        <a href="av-novels.html">📚 目錄</a>
    </nav>'''
    else:
        # 既沒有上一章也沒有下一章（不應該發生）
        new_nav = f'''    <nav aria-label="主要導航" class="nav">
        <a href="chapter-{chapter_num}.html">← 文字版</a>
        <a href="av-novels.html">📚 目錄</a>
    </nav>'''
    
    # 替換導航列
    new_content = content.replace(old_nav, new_nav)
    
    # 寫回文件
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"  ✅ 已更新導航列")
    return True

def main():
    """主程序"""
    print("=" * 80)
    print("統一有聲畫章節導航列格式")
    print("按照第60章格式標準化所有有聲畫章節")
    print("=" * 80)
    
    # 查找所有有聲畫章節文件
    av_files = glob.glob("chapter-*-av.html")
    av_files.sort(key=lambda x: extract_chapter_number(x) or 0)
    
    print(f"找到 {len(av_files)} 個有聲畫章節文件")
    print()
    
    fixed_count = 0
    skipped_count = 0
    
    for filename in av_files:
        if fix_navigation_in_file(filename):
            fixed_count += 1
        else:
            skipped_count += 1
        print()
    
    print("=" * 80)
    print("修復總結")
    print("=" * 80)
    print(f"總文件數: {len(av_files)}")
    print(f"修復成功: {fixed_count}")
    print(f"跳過: {skipped_count}")
    print()
    
    # 顯示一些示例
    print("標準導航列格式示例:")
    print("-" * 40)
    print("""    <nav aria-label="主要導航" class="nav">
        <a href="chapter-60.html">← 文字版</a>
        <a href="chapter-59-av.html">第59章</a>
        <a href="chapter-61-av.html">第61章</a>
        <a href="av-novels.html">📚 目錄</a>
    </nav>""")
    
    return fixed_count > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)