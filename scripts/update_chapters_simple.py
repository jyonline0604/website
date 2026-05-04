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
                        title_match = re.search(r'<title>第[零一二三四五六七八九十百千萬\d]+章\s+([^<]+?)\s*[·-]\s*萬古塵埃</title>', content)
                        if title_match:
                            title = f"第{chapter_num}章：{title_match.group(1).strip()}"
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
    
    # 動態生成按鈕組（每10章為一組）
    max_chapter = max(c["num"] for c in valid_chapters)
    
    # 計算按鈕組
    button_groups = []
    
    # 從最大章節往下計算每10章一組
    # 例如 93 章 → 第一組是 81-93，第二組是 71-80...
    next_group_end = ((max_chapter - 1) // 10) * 10 + 10  # 90
    if next_group_end > max_chapter:
        next_group_end = max_chapter
    next_group_start = next_group_end - 9  # 82 (for 90) or max_chapter - 9
    
    first_group_start = ((max_chapter - 1) // 10) * 10 + 1  # 81
    first_group_end = max_chapter  # 93
    
    button_groups.append(f"{first_group_start}-{first_group_end}")
    
    # 生成其餘按鈕組
    for start in range(first_group_start - 10, 0, -10):
        end = start + 9
        if end >= 1:
            button_groups.append(f"{start}-{end}")
    
    # 生成按鈕 HTML
    # 生成隱藏的 group id 元素（用於錨點跳轉）
    group_ids_html = ""
    for group in button_groups:
        group_id = f"group-{group}"
        group_ids_html += f'        <div id="{group_id}" style="position:absolute; opacity:0; pointer-events:none; height:1px; overflow:hidden;"></div>\n'

    buttons_html = '<div class="chapter-groups" id="chapterGroups">\n'
    buttons_html += '            <a href="#" class="group-btn active" >全部</a>\n'
    for group in button_groups:
        group_id = f"group-{group}"
        group_aria = f"跳轉到第{group}章"
        buttons_html += f'            <a href="#{group_id}" class="group-btn" aria-label="{group_aria}">{group}</a>\n'
    buttons_html += '        </div>'
    
    # 替換按鈕區域 - 使用棧正確解析嵌套的 HTML 標籤
    groups_id = '<div class="chapter-groups" id="chapterGroups">'
    groups_start = content.find(groups_id)
    if groups_start == -1:
        print("❌ 找不到章節按鈕區域")
        return False
    
    groups_content_start = groups_start + len(groups_id)
    
    # 使用棧找到匹配的 </div>
    open_count = 1
    pos = groups_content_start
    while open_count > 0 and pos < len(content):
        next_open = content.find('<div', pos)
        next_close = content.find('</div>', pos)
        
        if next_close == -1:
            print("❌ 找不到按鈕區域關閉標籤")
            return False
        
        if next_open != -1 and next_open < next_close:
            open_count += 1
            pos = next_open + 1
        else:
            open_count -= 1
            if open_count == 0:
                groups_end = next_close + 6  # After </div>
            pos = next_close + 6
    
    # 保留 groups_start 之前的內容 + 新的按鈕 HTML + groups_end 之後的內容
    content = content[:groups_start] + group_ids_html + buttons_html + '\n        ' + content[groups_end:]
    print(f"✅ 已更新按鈕組: {button_groups[0]}, 71-80, 61-70...")
    
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