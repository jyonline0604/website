#!/usr/bin/env python3
"""
修復av-novels.html - 完整重建章節結構
"""

import re

def fix_av_novels():
    with open('av-novels.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("=== 修復av-novels.html ===\n")
    
    # 找到chapter-grid的範圍
    grid_start = content.find('<div class="chapter-grid" id="chapterGrid">')
    grid_end = content.find('</div>', grid_start + 50) + 6
    
    print(f"1. chapter-grid範圍: {grid_start} - {grid_end}")
    
    # 提取頁眉（到chapter-grid開始）
    header = content[:grid_start + len('<div class="chapter-grid" id="chapterGrid">')]
    print(f"2. 頁眉長度: {len(header)}")
    
    # 找到頁腳（從chapter-grid結束後的第一個章節卡片結束）
    last_content = list(re.finditer(r'<div class="chapter-card-content">', content))[-1]
    footer_search_start = last_content.start()
    footer_start = content.find('</body>', footer_search_start)
    footer = content[footer_start:]
    print(f"3. 頁腳長度: {len(footer)}")
    
    # 提取所有章節
    chapters = {}
    
    # 方法：找到所有chapter-card開始，然後提取完整卡片
    card_starts = [(m.start(), m.group(0)) for m in re.finditer(r'<div class="chapter-card">', content)]
    print(f"4. 找到 {len(card_starts)} 個chapter-card")
    
    for i, (pos, _) in enumerate(card_starts):
        chunk = content[pos:pos+300]
        num_match = re.search(r'chapter-(\d+)-av\.html', chunk)
        if not num_match:
            continue
        
        chapter_num = int(num_match.group(1))
        
        # 找到卡片結束（5個</div>）
        end_search = content[pos:pos+800]
        end_match = re.search(r'</div>\s*</div>\s*</div>\s*</div>\s*</div>', end_search)
        if end_match:
            card_end = pos + end_match.end()
        else:
            continue
        
        card_html = content[pos:card_end]
        
        if 'chapter-card-content' in card_html:
            chapters[chapter_num] = card_html
    
    print(f"5. 提取了 {len(chapters)} 個完整章節卡片")
    
    # 處理第75章 - 它沒有chapter-card包裝
    grid_end_chunk = content[grid_end:grid_end+1000]
    if '第 75 章' in grid_end_chunk:
        # 找到了75章，手動包裝
        ch75_start = grid_end
        # 找到75章內容的結束
        end_marker = '</div>\n            </div>\n\n            <div class="chapter-card">'
        ch75_end = content.find(end_marker, ch75_start)
        if ch75_end < 0:
            ch75_end = content.find('</div>\n            </div>', ch75_start)
        if ch75_end > 0:
            ch75_content = content[ch75_start:ch75_end+20]
            # 包裝成chapter-card
            ch75_card = '<div class="chapter-card">\n' + ch75_content
            chapters[75] = ch75_card
            print(f"6. 提取第75章，長度: {len(ch75_card)}")
    
    print(f"7. 總共 {len(chapters)} 個章節")
    
    # 排序（降序）
    sorted_chapters = sorted(chapters.items(), key=lambda x: x[0], reverse=True)
    
    # 驗證
    nums = [n for n, _ in sorted_chapters]
    print(f"\n排序驗證:")
    print(f"   前10個: {nums[:10]}")
    print(f"   後5個: {nums[-5:]}")
    is_sorted = all(nums[i] >= nums[i+1] for i in range(len(nums)-1))
    print(f"   排序正確: {'是' if is_sorted else '否'}")
    
    # 重建
    grid_content = '\n'.join([c for _, c in sorted_chapters])
    new_content = header + '\n' + grid_content + '\n</div>' + footer
    
    print(f"\n8. 重建完成:")
    print(f"   原始長度: {len(content)}")
    print(f"   新長度: {len(new_content)}")
    
    # 保存
    with open('av-novels.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"   已保存")
    
    # 最終驗證
    final_cards = len(re.findall(r'<div class="chapter-card">', new_content))
    print(f"\n9. 最終驗證:")
    print(f"   chapter-card數量: {final_cards}")
    
    return True

if __name__ == '__main__':
    fix_av_novels()