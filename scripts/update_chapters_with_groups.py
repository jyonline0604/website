#!/usr/bin/env python3
"""
更新章節目錄（帶分組按鈕和降序排列）
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
    
    # 按章節號排序（降序：從最新到最舊）
    chapters.sort(key=lambda x: x["num"], reverse=True)
    return chapters

def get_chapter_groups(chapters):
    """獲取章節分組信息（降序排列分組）"""
    groups = []
    
    # 過濾掉模板（chapter-0）
    valid_chapters = [c for c in chapters if c["num"] > 0]
    
    if not valid_chapters:
        return groups
    
    max_chapter = max(c["num"] for c in valid_chapters)
    
    # 創建分組：每10章一組，從最高開始
    # 計算最後一組的起始章節
    last_group_start = ((max_chapter - 1) // 10) * 10 + 1
    
    # 從最高分組開始創建（降序）
    for start in range(last_group_start, 0, -10):
        end = min(start + 9, max_chapter)
        group_chapters = [c for c in valid_chapters if start <= c["num"] <= end]
        
        if group_chapters:
            # 分組內的章節已經是降序排列（因為chapters是降序的）
            groups.append({
                "start": start,
                "end": end,
                "chapters": sorted(group_chapters, key=lambda x: x["num"], reverse=True),
                "id": f"group-{start}-{end}"
            })
    
    return groups

def update_chapters_html():
    """更新章節目錄（帶分組）"""
    chapters_path = os.path.join(NOVEL_DIR, "chapters.html")
    
    # 讀取章節目錄模板
    with open(chapters_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 獲取所有章節（降序排列）
    chapters = get_all_chapters()
    
    # 過濾掉模板（chapter-0）
    valid_chapters = [c for c in chapters if c["num"] > 0]
    
    if not valid_chapters:
        print("❌ 沒有找到有效章節")
        return False
    
    print(f"找到 {len(valid_chapters)} 個章節（降序排列）")
    
    # 獲取章節分組
    groups = get_chapter_groups(chapters)
    print(f"創建 {len(groups)} 個章節分組")
    
    # 生成章節列表HTML（帶分組標記）
    chapters_html = ""
    
    for group in groups:
        # 添加分組標題
        chapters_html += f'''
            <div class="chapter-group" id="{group['id']}">
                <h3 class="group-title">第{group['start']}-{group['end']}章</h3>
        '''
        
        # 添加該組的章節
        for chap in group["chapters"]:
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
        
        # 結束分組
        chapters_html += '''
            </div>
        '''
    
    # 找到並替換章節網格部分
    grid_start = content.find('<div class="chapter-list-grid" id="chapterGrid">')
    if grid_start == -1:
        print("❌ 找不到章節列表網格區域")
        return False
    
    # 找到章節網格結束位置（下一個</div>）
    grid_end = content.find('</div>', grid_start)
    if grid_end == -1:
        print("❌ 找不到章節列表網格結束標籤")
        return False
    
    # 構建新的網格內容
    new_grid = f'''<div class="chapter-list-grid" id="chapterGrid">
{chapters_html}
        </div>'''
    
    # 替換內容
    new_content = content[:grid_start] + new_grid + content[grid_end+6:]
    
    # 更新章節總數
    total_chapters = len(valid_chapters)
    new_content = re.sub(r'id="totalChapters">共 \d+ 章</div>', 
                        f'id="totalChapters">共 {total_chapters} 章</div>', new_content)
    
    # 寫回文件
    with open(chapters_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ 已更新章節目錄，包含 {total_chapters} 個章節，{len(groups)} 個分組")
    return True

def main():
    print("=== 更新章節目錄（帶分組）===")
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