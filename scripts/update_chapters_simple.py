#!/usr/bin/env python3
"""
更新簡化版章節目錄
"""

import os
import sys
import re
from datetime import datetime

WORKSPACE = "/home/openclaw/.openclaw/workspace"
NOVEL_DIR = WORKSPACE

def get_all_chapters():
    """獲取所有章節信息"""
    chapters = []
    
    for filename in os.listdir(NOVEL_DIR):
        if filename.startswith("chapter-") and filename.endswith(".html"):
            match = re.match(r"chapter-(\d+)\.html", filename)
            if match:
                chapter_num = int(match.group(1))
                
                # 讀取章節標題
                filepath = os.path.join(NOVEL_DIR, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read(2000)
                        title_match = re.search(r'<title>第\d+章：([^<]+)</title>', content)
                        if title_match:
                            title = f"第{chapter_num}章：{title_match.group(1)}"
                        else:
                            title = f"第{chapter_num}章"
                except:
                    title = f"第{chapter_num}章"
                
                chapters.append({
                    "num": chapter_num,
                    "filename": filename,
                    "title": title
                })
    
    # 按章節號排序
    chapters.sort(key=lambda x: x["num"])
    return chapters

def update_chapters_html():
    """更新章節目錄"""
    chapters_path = os.path.join(NOVEL_DIR, "chapters.html")
    
    # 讀取章節目錄模板
    with open(chapters_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 獲取所有章節
    chapters = get_all_chapters()
    
    # 過濾掉模板（chapter-0或非數字）
    valid_chapters = [c for c in chapters if c["num"] > 0]
    
    if not valid_chapters:
        print("❌ 沒有找到有效章節")
        return False
    
    print(f"找到 {len(valid_chapters)} 個章節")
    
    # 生成章節列表HTML（從第1章到最新章）
    chapters_html = ""
    for chap in valid_chapters:
        # 提取章節名稱（去掉"第X章："部分）
        full_title = chap["title"]
        if "：" in full_title:
            chapter_name = full_title.split("：", 1)[1]
        else:
            chapter_name = "科技修真傳"
        
        chapters_html += f'''
            <a href="{chap['filename']}" class="chapter-item">
                <div class="chapter-info">
                    <div class="chapter-num">第{chap['num']}章</div>
                    <div class="chapter-name">{chapter_name}</div>
                </div>
                <div class="chapter-arrow">→</div>
            </a>'''
    
    # 找到並替換章節網格部分
    grid_start = content.find('<div class="chapter-list-grid" id="chapterGrid">')
    if grid_start == -1:
        print("❌ 找不到章節列表網格區域")
        return False
    
    # 使用棧來正確追蹤嵌套的 HTML 標籤
    def find_matching_close_tag(html, start_pos):
        """找到與開始標籤匹配的關閉標籤位置"""
        open_count = 1  # 已經找到了開始標籤
        pos = start_pos
        while open_count > 0 and pos < len(html):
            # 找到下一個 <div 或 </div>
            next_open = html.find('<div', pos)
            next_close = html.find('</div>', pos)
            
            if next_close == -1:
                return -1
            
            if next_open != -1 and next_open < next_close:
                # 遇到新的開標籤
                open_count += 1
                pos = next_open + 1
            else:
                # 遇到關閉標籤
                open_count -= 1
                if open_count == 0:
                    return next_close + 6  # 返回 </div> 後的位置
                pos = next_close + 1
        
        return -1
    
    grid_content_start = grid_start + len('<div class="chapter-list-grid" id="chapterGrid">')
    grid_end = find_matching_close_tag(content, grid_content_start)
    
    if grid_end == -1:
        print("❌ 找不到章節列表網格結束標籤")
        return False
    
    # 構建新的網格內容
    new_grid = f'''<div class="chapter-list-grid" id="chapterGrid">
{chapters_html}
        </div>'''
    
    # 替換內容：保留 grid_start 之前的所有內容，替換網格內容
    new_content = content[:grid_start] + new_grid + content[grid_end:]
    
    # 更新章節總數
    total_chapters = len(valid_chapters)
    new_content = re.sub(r'id="totalChapters">共 \d+ 章</div>', 
                        f'id="totalChapters">共 {total_chapters} 章</div>', new_content)
    
    # 寫回文件
    with open(chapters_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ 已更新章節目錄，包含 {total_chapters} 個章節")
    return True

def main():
    print("=== 更新章節目錄 ===")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = update_chapters_html()
    
    if success:
        print("✅ 章節目錄更新完成")
        return 0
    else:
        print("❌ 章節目錄更新失敗")
        return 1

if __name__ == "__main__":
    sys.exit(main())