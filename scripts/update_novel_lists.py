#!/usr/bin/env python3
"""
更新小說網站的首頁和章節目錄
"""

import os
import re
from datetime import datetime

WORKSPACE = "/home/openclaw/.openclaw/workspace"
NOVEL_DIR = WORKSPACE

def get_chapter_info():
    """獲取所有章節信息"""
    chapters = []
    
    for filename in os.listdir(NOVEL_DIR):
        if filename.startswith("chapter-") and filename.endswith(".html"):
            match = re.match(r"chapter-(\d+)\.html", filename)
            if match:
                chapter_num = int(match.group(1))
                filepath = os.path.join(NOVEL_DIR, filename)
                
                # 讀取標題
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read(2000)  # 只讀前2000字節找標題
                    
                    # 找標題
                    title_match = re.search(r'<title>(第\d+章：.*?)</title>', content)
                    if title_match:
                        title = title_match.group(1)
                    else:
                        # 備用：從文件名推測
                        title = f"第{chapter_num}章"
                
                chapters.append({
                    "num": chapter_num,
                    "filename": filename,
                    "title": title,
                    "path": filename
                })
    
    # 按章節號排序
    chapters.sort(key=lambda x: x["num"])
    return chapters

def update_home_html(chapters):
    """更新首頁 (home.html) - 使用簡化版更新"""
    # 導入簡化版更新函數
    import subprocess
    import sys
    
    print("使用簡化版首頁更新...")
    
    # 運行簡化版更新腳本
    result = subprocess.run(
        [sys.executable, os.path.join(WORKSPACE, "scripts/update_home_simple.py")],
        capture_output=True,
        text=True,
        cwd=WORKSPACE
    )
    
    if result.returncode == 0:
        print("✅ 簡化版首頁更新成功")
        return True
    else:
        print(f"❌ 簡化版首頁更新失敗: {result.stderr}")
        return False

def get_chapter_excerpt(filename):
    """獲取章節摘要"""
    filepath = os.path.join(NOVEL_DIR, filename)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read(5000)  # 讀前5000字節
            
            # 找正文開始
            body_start = content.find('<div class="chapter-content">')
            if body_start != -1:
                # 找正文內容
                body_text = content[body_start:body_start+2000]
                # 移除HTML標籤
                import re
                clean_text = re.sub(r'<[^>]+>', ' ', body_text)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                
                # 取前100字作為摘要
                if len(clean_text) > 100:
                    return clean_text[:100] + "..."
                return clean_text
    except:
        pass
    
    return "林塵的修真科技之旅繼續展開..."

def update_chapters_html(chapters):
    """更新章節目錄 - 使用簡化版更新"""
    # 導入簡化版更新函數
    import subprocess
    import sys
    
    print("使用簡化版章節目錄更新...")
    
    # 運行簡化版更新腳本
    result = subprocess.run(
        [sys.executable, os.path.join(WORKSPACE, "scripts/update_chapters_simple.py")],
        capture_output=True,
        text=True,
        cwd=WORKSPACE
    )
    
    if result.returncode == 0:
        print("✅ 簡化版章節目錄更新成功")
        return True
    else:
        print(f"❌ 簡化版章節目錄更新失敗: {result.stderr}")
        return False

def main():
    print(f"📚 開始更新小說網站列表 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    chapters = get_chapter_info()
    print(f"  找到 {len(chapters)} 個章節文件（包括模板）")
    
    # 顯示最新5章
    print("  最新章節：")
    for chap in chapters[-5:]:
        print(f"    - {chap['title']}")
    
    update_home_html(chapters)
    update_chapters_html(chapters)
    
    print("✅ 更新完成！")

if __name__ == "__main__":
    main()