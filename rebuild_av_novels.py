#!/usr/bin/env python3
"""
重建av-novels.html的章節區域
問題：chapter-grid結構被破壞，章節卡片不完整
"""

import re
from pathlib import Path

def rebuild_av_novels():
    file_path = Path('/home/openclaw/.openclaw/workspace/av-novels.html')
    
    # 讀取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("分析當前結構...")
    
    # 找到所有章節卡片的起始位置
    card_starts = [(m.start(), int(m.group(1))) for m in re.finditer(r'<div class="chapter-card">', content)]
    print(f"找到 {len(card_starts)} 個章節卡片開始標籤")
    
    # 找到所有chapter-card-content的位置
    content_starts = [(m.start(), m.group(0)) for m in re.finditer(r'<div class="chapter-card-content">', content)]
    print(f"找到 {len(content_starts)} 個章節內容區塊")
    
    # 找到chapter-grid的位置
    grid_match = re.search(r'<div class="chapter-grid" id="chapterGrid">', content)
    if grid_match:
        print(f"找到chapter-grid於位置: {grid_match.start()}")
    else:
        print("❌ 未找到chapter-grid")
        return False
    
    # 找到chapter-grid之後的第一個chapter-card
    first_card_after_grid = None
    for pos, num in card_starts:
        if pos > grid_match.start():
            first_card_after_grid = (pos, num)
            break
    
    print(f"第一個在chapter-grid後的章節卡片: Chapter {first_card_after_grid[1] if first_card_after_grid else '無'}")
    
    # 提取損壞區域之前的內容
    header_end = grid_match.start()
    before_grid = content[:header_end]
    
    # 找到chapter-grid的結束位置（在倒數第二個</div>之前）
    # 根據結構，應該在倒數第6個</div>附近
    
    # 讓我找到所有chapter-card的結束位置
    card_ends = [(m.end(), int(re.search(r'chapter-(\d+)-av\.html', content[m.start():m.start()+200]).group(1))) 
                 for m in re.finditer(r'</div>\s*</div>\s*</div>\s*</div>\s*</div>\s*</div>', content)]
    
    print(f"找到 {len(card_ends)} 個章節卡片結束標記")
    
    if card_ends:
        # 最後一個章節卡片的結束位置
        last_card_end = card_ends[-1][0]
        print(f"最後章節卡片結束於: {last_card_end}")
        
        # chapter-grid的結束應該在最後一個章節卡片結束之後
        after_last_card = content[last_card_end:]
        grid_end_match = re.search(r'</div>\s*</div>\s*</div>\s*</div>\s*</div>\s*</div>', after_last_card)
        
        if grid_end_match:
            full_grid_end = last_card_end + grid_end_match.end()
            print(f"chapter-grid結束於: {full_grid_end}")
        else:
            # 嘗試直接找到</div>關閉chapter-grid
            search_start = last_card_end
            grid_close = content.find('</div>', search_start)
            if grid_close > 0:
                full_grid_end = grid_close + 6
                print(f"chapter-grid關閉於: {full_grid_end}")
            else:
                print("❌ 無法找到chapter-grid關閉標籤")
                return False
    else:
        print("❌ 找不到章節卡片結束位置")
        return False
    
    # 提取損壞區域之後的內容（頁腳等）
    after_grid = content[full_grid_end:]
    print(f"章節區域後內容長度: {len(after_grid)}")
    
    # 提取所有76個章節
    print("\n提取章節卡片...")
    
    # 方法：從頭開始遍歷，找到每個章節的完整卡片
    chapters = []
    
    # 找到所有章節卡片的開始
    card_positions = []
    for m in re.finditer(r'<div class="chapter-card">', content):
        card_positions.append(m.start())
    
    # 對於每個位置，嘗試提取完整的章節卡片
    for i, start_pos in enumerate(card_positions):
        # 找到這個章節的章節號
        chunk = content[start_pos:start_pos+500]
        num_match = re.search(r'chapter-(\d+)-av\.html', chunk)
        if num_match:
            chapter_num = int(num_match.group(1))
        else:
            continue
        
        # 找到這個卡片的結束（5個</div>）
        end_match = re.search(r'</div>\s*</div>\s*</div>\s*</div>\s*</div>', content[start_pos:])
        if end_match:
            end_pos = start_pos + end_match.end()
        else:
            # 嘗試更簡單的匹配
            end_pos = content.find('</div>', start_pos + 100)
            if end_pos > 0:
                end_pos += 6
        
        # 提取完整卡片
        card_html = content[start_pos:end_pos]
        
        # 驗證這是一個完整的卡片
        if 'chapter-card-content' in card_html and f'chapter-{chapter_num}-av.html' in card_html:
            chapters.append((chapter_num, card_html))
        else:
            # 可能結構損壞，嘗試另一種方式
            # 找到下一個章節卡片的開始
            if i + 1 < len(card_positions):
                next_start = card_positions[i + 1]
                card_html = content[start_pos:next_start]
                if 'chapter-card-content' in card_html and f'chapter-{chapter_num}-av.html' in card_html:
                    chapters.append((chapter_num, card_html))
    
    print(f"提取了 {len(chapters)} 個章節卡片")
    
    # 檢查是否包含第75章
    chapter_nums = [c[0] for c in chapters]
    print(f"章節號: {sorted(chapter_nums)[:10]}...{sorted(chapter_nums)[-5:]}")
    print(f"章節數量: {len(chapter_nums)}")
    
    # 檢查75章
    if 75 not in chapter_nums:
        print("❌ 第75章缺失！")
        # 嘗試從損壞區域提取第75章
        # 第75章的內容在chapter-grid開始處
        damaged_area = content[header_end:full_grid_end]
        
        # 查找chapter-75的內容
        ch75_match = re.search(r'(第 75 章.*?chapter-75-av\.html.*?</div>\s*</div>\s*</div>\s*</div>\s*</div>)', damaged_area, re.DOTALL)
        if ch75_match:
            ch75_content = '<div class="chapter-card">\n' + ch75_match.group(1)
            print("找到第75章內容，長度:", len(ch75_content))
            chapters.append((75, ch75_content))
    
    # 按章節號降序排序
    chapters.sort(key=lambda x: x[0], reverse=True)
    
    print(f"\n排序後（前10個）:")
    for i, (num, _) in enumerate(chapters[:10]):
        print(f"  {i+1}. Chapter {num}")
    
    # 重建chapter-grid
    new_grid = '<div class="chapter-grid" id="chapterGrid">\n'
    new_grid += '\n'.join([c[1] for c in chapters])
    new_grid += '\n</div>'
    
    # 重建完整HTML
    new_content = before_grid + new_grid + after_grid
    
    # 驗證
    print(f"\n重建後總長度: {len(new_content)}")
    print(f"原始長度: {len(content)}")
    
    # 保存
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("\n✅ 已保存修復後的文件")
    
    # 驗證結構
    new_cards = len(re.findall(r'<div class="chapter-card">', new_content))
    print(f"驗證: 找到 {new_cards} 個章節卡片")
    
    return True

if __name__ == '__main__':
    print("=== 重建av-novels.html章節區域 ===\n")
    rebuild_av_novels()