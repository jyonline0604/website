#!/usr/bin/env python3
"""
完整重建av-novels.html的章節區域
問題：HTML結構嚴重損壞，章節卡片不完整
"""

import re
from pathlib import Path

def rebuild_av_novels_complete():
    file_path = Path('/home/openclaw/.openclaw/workspace/av-novels.html')
    
    # 讀取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("=== 分析並重建av-novels.html ===\n")
    
    # 找到頁眉結束位置（到chapter-grid之前）
    grid_start = content.find('<div class="chapter-grid" id="chapterGrid">')
    header_end = grid_start
    
    print(f"1. 頁眉到位置: {header_end}")
    
    # 找到頁腳開始位置（chapter-grid之後的最後一個章節卡片結束）
    # 找到最後一個chapter-card-content
    last_content_match = list(re.finditer(r'<div class="chapter-card-content">', content))[-1]
    last_content_pos = last_content_match.start()
    
    # 從最後一個content往後找到頁腳
    footer_start = content.find('</body>', last_content_pos)
    if footer_start < 0:
        footer_start = len(content)
    
    print(f"2. 頁腳從位置: {footer_start}")
    
    # 提取頁眉和頁腳
    header = content[:grid_start] + '<div class="chapter-grid" id="chapterGrid">\n'
    footer = '\n</div>' + content[footer_start:]
    
    print(f"3. 頁眉長度: {len(header)}, 頁腳長度: {len(footer)}")
    
    # 提取所有76個章節
    # 方法：找到所有chapter-card-content，然後往前找對應的chapter-card
    
    content_positions = [m.start() for m in re.finditer(r'<div class="chapter-card-content">', content)]
    print(f"4. 找到 {len(content_positions)} 個章節內容區塊")
    
    chapters = []
    
    for content_pos in content_positions:
        # 從content位置往前找到chapter-card
        # 搜索範圍：content_pos - 2000 到 content_pos
        search_start = max(0, content_pos - 2000)
        search_chunk = content[search_start:content_pos]
        
        # 找到最後一個chapter-card
        card_matches = list(re.finditer(r'<div class="chapter-card">', search_chunk))
        
        if card_matches:
            # 有chapter-card，提取從card到content結束的完整卡片
            card_start = search_start + card_matches[-1].start()
            # 找到這個chapter-card的結束（5個</div>）
            end_search = content[content_pos:content_pos+500]
            end_match = re.search(r'</div>\s*</div>\s*</div>\s*</div>\s*</div>', end_search)
            if end_match:
                card_end = content_pos + end_match.end()
            else:
                card_end = content_pos + 400
            
            card_html = content[card_start:card_end]
        else:
            # 沒有chapter-card，只有chapter-card-content
            # 這是第75章，需要手動添加chapter-card包裝
            end_search = content[content_pos:content_pos+500]
            end_match = re.search(r'</div>\s*</div>\s*</div>\s*</div>\s*</div>', end_search)
            if end_match:
                card_end = content_pos + end_match.end()
            else:
                card_end = content_pos + 400
            
            # 手動構建完整的chapter-card
            card_html = '<div class="chapter-card">\n' + content[content_pos-86:card_end]
        
        # 提取章節號
        num_match = re.search(r'chapter-(\d+)-av\.html', card_html)
        if num_match:
            chapter_num = int(num_match.group(1))
            chapters.append((chapter_num, card_html))
        else:
            # 嘗試從章節標題提取
            title_match = re.search(r'第 (\d+) 章', card_html)
            if title_match:
                chapter_num = int(title_match.group(1))
                chapters.append((chapter_num, card_html))
    
    print(f"5. 提取了 {len(chapters)} 個章節")
    
    # 按章節號降序排序
    chapters.sort(key=lambda x: x[0], reverse=True)
    
    # 驗證排序
    print(f"\n6. 排序驗證:")
    nums = [c[0] for c in chapters]
    print(f"   前10個: {nums[:10]}")
    print(f"   後5個: {nums[-5:]}")
    
    is_sorted = all(nums[i] >= nums[i+1] for i in range(len(nums)-1))
    print(f"   排序正確: {'✅' if is_sorted else '❌'}")
    
    # 檢查75章
    if 75 in nums:
        print(f"   75章存在: ✅")
    else:
        print(f"   75章存在: ❌")
    
    # 重建HTML
    grid_content = '\n'.join([c[1] for c in chapters])
    new_content = header + grid_content + footer
    
    print(f"\n7. 重建完成:")
    print(f"   原始長度: {len(content)}")
    print(f"   新長度: {len(new_content)}")
    
    # 保存
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"   已保存: ✅")
    
    # 驗證
    new_cards = len(re.findall(r'<div class="chapter-card">', new_content))
    new_contents = len(re.findall(r'<div class="chapter-card-content">', new_content))
    print(f"\n8. 驗證:")
    print(f"   chapter-card數量: {new_cards}")
    print(f"   chapter-card-content數量: {new_contents}")
    print(f"   匹配: {'✅' if new_cards == new_contents else '❌'}")
    
    return True

if __name__ == '__main__':
    rebuild_av_novels_complete()