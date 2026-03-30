#!/usr/bin/env python3
"""
修復所有章節的「上一章」、「下一章」和「返回目錄」鏈接
"""

import os
import re
import sys
from datetime import datetime

WORKSPACE = "/home/openclaw/.openclaw/workspace"
NOVEL_DIR = os.path.join(WORKSPACE, "my-novel")

def get_all_chapter_files():
    """獲取所有章節文件"""
    chapters = []
    
    for filename in os.listdir(NOVEL_DIR):
        if filename.startswith("chapter-") and filename.endswith(".html"):
            match = re.match(r"chapter-(\d+)\.html", filename)
            if match:
                chapter_num = int(match.group(1))
                chapters.append({
                    "num": chapter_num,
                    "filename": filename,
                    "path": os.path.join(NOVEL_DIR, filename)
                })
    
    # 按章節號排序
    chapters.sort(key=lambda x: x["num"])
    return chapters

def fix_chapter_navigation(chapters):
    """修復章節導航鏈接"""
    print("=== 修復章節導航鏈接 ===\n")
    
    # 創建章節號到文件名的映射
    chapter_map = {chap["num"]: chap["filename"] for chap in chapters}
    max_chapter = max(chapter_map.keys()) if chapter_map else 0
    
    print(f"總章節數: {len(chapters)} (第1章到第{max_chapter}章)")
    print(f"排除模板: chapter-0.html (模板文件)\n")
    
    fixed_count = 0
    
    for chap in chapters:
        if chap["num"] == 0:  # 跳過模板
            continue
            
        filepath = chap["path"]
        chapter_num = chap["num"]
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 計算正確的鏈接
            prev_chapter = f"chapter-{chapter_num-1}.html" if chapter_num > 1 else None
            next_chapter = f"chapter-{chapter_num+1}.html" if chapter_num < max_chapter else None
            
            # 修復底部導航
            bottom_nav_fixed = False
            
            # 修復「上一章」鏈接
            if prev_chapter:
                # 查找並替換錯誤的上一章鏈接
                wrong_prev_pattern = r'<a href="[^"]*">← 上一章</a>'
                correct_prev = f'<a href="{prev_chapter}">← 上一章</a>'
                
                if re.search(wrong_prev_pattern, content):
                    content = re.sub(wrong_prev_pattern, correct_prev, content)
                    bottom_nav_fixed = True
            else:
                # 第1章：上一章應該是灰色不可點擊
                wrong_prev_pattern = r'<a href="[^"]*">← 上一章</a>'
                disabled_prev = '<span style="opacity:0.3; padding:10px 16px; display:inline-block;">← 上一章</span>'
                
                if re.search(wrong_prev_pattern, content):
                    content = re.sub(wrong_prev_pattern, disabled_prev, content)
                    bottom_nav_fixed = True
            
            # 修復「下一章」鏈接
            if next_chapter:
                # 查找並替換錯誤的下一章鏈接
                wrong_next_pattern = r'<span style="opacity:0\.3;[^>]*>下一章 →</span>'
                correct_next = f'<a href="{next_chapter}">下一章 →</a>'
                
                if re.search(wrong_next_pattern, content):
                    content = re.sub(wrong_next_pattern, correct_next, content)
                    bottom_nav_fixed = True
            else:
                # 最新章節：下一章應該是灰色不可點擊
                wrong_next_pattern = r'<a href="[^"]*">下一章 →</a>'
                disabled_next = '<span style="opacity:0.3; padding:10px 16px; display:inline-block;">下一章 →</span>'
                
                if re.search(wrong_next_pattern, content):
                    content = re.sub(wrong_next_pattern, disabled_next, content)
                    bottom_nav_fixed = True
            
            # 修復JavaScript導航函數
            js_fixed = False
            
            # 查找prevChapter函數
            prev_js_pattern = r'function prevChapter\(\)\s*{[^}]*window\.location\.href\s*=\s*["\'][^"\']*["\'];[^}]*}'
            
            if prev_chapter:
                correct_prev_js = f'''function prevChapter() {{
    window.location.href = "{prev_chapter}";
}}'''
            else:
                correct_prev_js = '''function prevChapter() {
    // 已經是第一章
    alert("已經是第一章了！");
}'''
            
            if re.search(prev_js_pattern, content):
                content = re.sub(prev_js_pattern, correct_prev_js, content)
                js_fixed = True
            
            # 查找nextChapter函數
            next_js_pattern = r'function nextChapter\(\)\s*{[^}]*window\.location\.href\s*=\s*["\'][^"\']*["\'];[^}]*}'
            
            if next_chapter:
                correct_next_js = f'''function nextChapter() {{
    window.location.href = "{next_chapter}";
}}'''
            else:
                correct_next_js = '''function nextChapter() {
    // 已經是最新章節
    alert("已經是最新章節了！");
}'''
            
            if re.search(next_js_pattern, content):
                content = re.sub(next_js_pattern, correct_next_js, content)
                js_fixed = True
            
            # 添加返回目錄鏈接（如果不存在）
            if '返回目錄' not in content:
                # 在底部導航後添加返回目錄按鈕
                bottom_nav_end = content.find('</nav>')
                if bottom_nav_end != -1:
                    toc_button = '''
    <div style="text-align:center; margin-top:20px;">
        <a href="chapters.html" style="display:inline-block; padding:10px 20px; background:#6366f1; color:white; text-decoration:none; border-radius:8px; font-weight:500;">返回目錄</a>
    </div>'''
                    content = content[:bottom_nav_end+6] + toc_button + content[bottom_nav_end+6:]
            
            # 寫回文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            if bottom_nav_fixed or js_fixed:
                fixed_count += 1
                print(f"✅ 已修復第{chapter_num}章導航鏈接")
                
        except Exception as e:
            print(f"❌ 修復第{chapter_num}章錯誤: {e}")
    
    return fixed_count

def main():
    print(f"🔧 章節導航修復工具 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 獲取所有章節
    chapters = get_all_chapter_files()
    
    if not chapters:
        print("❌ 沒有找到章節文件")
        return 1
    
    # 修復章節導航
    fixed_count = fix_chapter_navigation(chapters)
    
    print(f"\n{'='*50}")
    print(f"修復完成！共修復 {fixed_count} 個章節")
    
    # 運行檢測腳本驗證修復
    print("\n=== 驗證修復結果 ===")
    os.system(f"cd {WORKSPACE} && python3 scripts/check_chapter_links.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())