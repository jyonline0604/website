#!/usr/bin/env python3
"""
更新簡化版首頁
只保留最新章節區域
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

def get_chapter_excerpt(filename):
    """獲取章節摘要"""
    filepath = os.path.join(NOVEL_DIR, filename)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read(3000)  # 讀前3000字節
            
            # 找正文內容
            content_start = content.find('<div class="chapter-content">')
            if content_start != -1:
                content_start += len('<div class="chapter-content">')
                content_end = content.find('</div>', content_start)
                if content_end != -1:
                    text = content[content_start:content_end]
                    # 清理HTML標籤
                    text = re.sub(r'<[^>]+>', ' ', text)
                    text = re.sub(r'\s+', ' ', text).strip()
                    
                    if len(text) > 100:
                        return text[:100] + "..."
                    return text if text else "林塵的修真科技之旅繼續展開..."
    
    except:
        pass
    
    return "林塵的修真科技之旅繼續展開..."

def calculate_date(chapter_num):
    """計算章節發布日期（從第60章開始為3月26日）"""
    # 第60章 = 3月26日，第61章 = 3月27日，依此類推
    base_day = 26  # 3月26日
    base_chapter = 60
    
    day = base_day + (chapter_num - base_chapter)
    month = 3
    
    # 處理月份轉換：3月最多31日
    if day > 31:
        month = 4
        day = day - 31
    
    return f"2026年{month}月{day}日"

def update_home_html():
    """更新簡化版首頁"""
    home_path = os.path.join(NOVEL_DIR, "home.html")
    
    # 讀取首頁模板
    with open(home_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 獲取所有章節
    chapters = get_all_chapters()
    
    # 過濾掉模板（chapter-0或非數字）
    valid_chapters = [c for c in chapters if c["num"] > 0]
    
    if not valid_chapters:
        print("❌ 沒有找到有效章節")
        return False
    
    print(f"找到 {len(valid_chapters)} 個章節")
    
    # 取最新5章
    latest_chapters = valid_chapters[-6:]  # 顯示6個最新章節
    print(f"最新6章: {[c['num'] for c in latest_chapters]}")
    
    # 生成章節卡片HTML
    chapter_cards_html = ""
    for chap in reversed(latest_chapters):  # 從最新到最舊
        excerpt = get_chapter_excerpt(chap["filename"])
        
        # 提取章節標題（去掉"第X章："部分）
        full_title = chap["title"]
        if "：" in full_title:
            chapter_name = full_title.split("：", 1)[1]
        else:
            chapter_name = full_title
        
        chapter_cards_html += f'''
            <a href="{chap['filename']}" class="chapter-card">
                <div class="chapter-number">第{chap['num']}章</div>
                <h3 class="chapter-title">{chapter_name}</h3>
                <p class="chapter-excerpt">{excerpt}</p>
                <div class="chapter-meta">
                    <span class="chapter-date">{calculate_date(chap['num'])}</span>
                    <span class="chapter-read">閱讀全文 →</span>
                </div>
            </a>'''
    
    # 找到並替換章節網格部分
    grid_start = content.find('<div class="chapter-grid">')
    if grid_start == -1:
        print("❌ 找不到章節網格區域")
        return False
    
    # 使用棧來正確追蹤嵌套的 HTML 標籤
    def find_matching_close_tag(html, start_pos):
        """找到與開始標籤匹配的關閉標籤位置"""
        open_count = 1
        pos = start_pos
        while open_count > 0 and pos < len(html):
            next_open = html.find('<div', pos)
            next_close = html.find('</div>', pos)
            
            if next_close == -1:
                return -1
            
            if next_open != -1 and next_open < next_close:
                open_count += 1
                pos = next_open + 1
            else:
                open_count -= 1
                if open_count == 0:
                    return next_close + 6
                pos = next_close + 1
        
        return -1
    
    grid_content_start = grid_start + len('<div class="chapter-grid">')
    grid_end = find_matching_close_tag(content, grid_content_start)
    
    if grid_end == -1:
        print("❌ 找不到章節網格結束標籤")
        return False
    
    # 構建新的網格內容
    new_grid = f'''<div class="chapter-grid">
{chapter_cards_html}
        </div>'''
    
    # 替換內容
    new_content = content[:grid_start] + new_grid + content[grid_end:]
    
    # 寫回文件
    with open(home_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ 已更新首頁，包含 {len(latest_chapters)} 個最新章節")
    return True

def main():
    print("=== 更新簡化版首頁 ===")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = update_home_html()
    
    if success:
        print("✅ 首頁更新完成")
        return 0
    else:
        print("❌ 首頁更新失敗")
        return 1

if __name__ == "__main__":
    sys.exit(main())