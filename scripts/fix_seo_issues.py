#!/usr/bin/env python3
"""
修復 home.html 和 chapters.html 的SEO問題
"""

import os
import re
import sys

WORKSPACE = "/home/openclaw/.openclaw/workspace"
NOVEL_DIR = WORKSPACE

def add_meta_tags(filepath, page_type):
    """添加meta標籤"""
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 根據頁面類型設置meta內容
        if page_type == "home":
            description = "《科技修真傳》官方網站 - 每日更新的AI生成小說，融合科技與修真的奇幻世界。作者：大肥喵。"
            keywords = "科技修真傳, AI小說, 修真小說, 科技小說, 每日更新, 大肥喵"
            title = "科技修真傳 - 首頁"
        else:  # chapters
            description = "《科技修真傳》章節目錄 - 完整收錄所有章節，從第1章到最新章節，支持分組瀏覽和排序功能。"
            keywords = "科技修真傳, 章節目錄, 小說章節, 修真小說, 科技小說, 在線閱讀"
            title = "章節目錄 - 科技修真傳"
        
        # 檢查是否已有meta描述
        if '<meta name="description"' not in content:
            # 在charset meta後添加
            charset_pos = content.find('<meta charset="UTF-8">')
            if charset_pos == -1:
                charset_pos = content.find('<meta charset="utf-8">')
            
            if charset_pos != -1:
                # 找到charset meta的結束位置
                meta_end = content.find('>', charset_pos) + 1
                new_meta = f'\n    <meta name="description" content="{description}">\n    <meta name="keywords" content="{keywords}">\n    <meta name="author" content="大肥喵">\n    <meta property="og:title" content="{title}">\n    <meta property="og:description" content="{description}">\n    <meta property="og:type" content="website">'
                content = content[:meta_end] + new_meta + content[meta_end:]
        
        # 寫回文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 已為 {os.path.basename(filepath)} 添加SEO meta標籤")
        return True
        
    except Exception as e:
        print(f"❌ 修復 {os.path.basename(filepath)} SEO錯誤: {e}")
        return False

def fix_accessibility_issues():
    """修復無障礙訪問問題"""
    
    chapters_path = os.path.join(NOVEL_DIR, "chapters.html")
    
    try:
        with open(chapters_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 為排序按鈕添加aria-label
        content = re.sub(
            r'<button class="sort-btn" onclick="sortChapters\(\'desc\'\)">',
            '<button class="sort-btn" onclick="sortChapters(\'desc\')" aria-label="按降序排列章節">',
            content
        )
        
        content = re.sub(
            r'<button class="sort-btn" onclick="sortChapters\(\'asc\'\)">',
            '<button class="sort-btn" onclick="sortChapters(\'asc\')" aria-label="按升序排列章節">',
            content
        )
        
        # 為分組按鈕添加aria-label
        content = re.sub(
            r'<a href="#group-(\d+)-(\d+)" class="group-btn">',
            r'<a href="#group-\1-\2" class="group-btn" aria-label="跳轉到第\1-\2章">',
            content
        )
        
        # 為導航按鈕添加aria-label
        content = re.sub(
            r'<button class="nav-btn" onclick="prevChapter\(\)">◀</button>',
            '<button class="nav-btn" onclick="prevChapter()" aria-label="上一章">◀</button>',
            content
        )
        
        content = re.sub(
            r'<button class="nav-btn" onclick="nextChapter\(\)">▶</button>',
            '<button class="nav-btn" onclick="nextChapter()" aria-label="下一章">▶</button>',
            content
        )
        
        # 寫回文件
        with open(chapters_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 已修復 chapters.html 無障礙訪問問題")
        return True
        
    except Exception as e:
        print(f"❌ 修復無障礙訪問錯誤: {e}")
        return False

def check_chapter_links_count():
    """檢查章節鏈接數量"""
    
    chapters_path = os.path.join(NOVEL_DIR, "chapters.html")
    
    try:
        with open(chapters_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 計算頁面中的章節鏈接
        chapter_links = re.findall(r'chapter-\d+\.html', content)
        
        # 計算實際章節文件（排除模板）
        actual_chapters = len([f for f in os.listdir(NOVEL_DIR) 
                              if f.startswith('chapter-') and f.endswith('.html') 
                              and f != 'chapter-0.html'])
        
        print(f"頁面章節鏈接: {len(chapter_links)} 個")
        print(f"實際章節文件: {actual_chapters} 個")
        
        if len(chapter_links) != actual_chapters:
            print(f"⚠️ 章節鏈接數量不匹配")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 檢查章節鏈接錯誤: {e}")
        return False

def main():
    print("🔧 修復 home.html 和 chapters.html 問題")
    print("="*50)
    
    # 修復SEO問題
    print("\n1. 修復SEO問題:")
    home_path = os.path.join(NOVEL_DIR, "home.html")
    chapters_path = os.path.join(NOVEL_DIR, "chapters.html")
    
    add_meta_tags(home_path, "home")
    add_meta_tags(chapters_path, "chapters")
    
    # 修復無障礙訪問問題
    print("\n2. 修復無障礙訪問問題:")
    fix_accessibility_issues()
    
    # 檢查章節鏈接數量
    print("\n3. 檢查章節鏈接數量:")
    check_chapter_links_count()
    
    print("\n" + "="*50)
    print("✅ 修復完成！")
    
    # 重新運行檢查
    print("\n重新運行檢查...")
    os.system(f"cd {WORKSPACE} && python3 scripts/check_home_chapters.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())