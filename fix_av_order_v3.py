#!/usr/bin/env python3
"""
修復av-novels.html章節排序問題 - v2
使用更簡單的方法：直接提取、排序、重寫章節卡片
"""

import re

def fix_av_order():
    file_path = '/home/openclaw/.openclaw/workspace/av-novels.html'
    
    # 讀取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到chapter-grid的開始和結束
    grid_start = content.find('<div class="chapter-grid" id="chapterGrid">')
    grid_end = content.find('</div>', grid_start) + 6  # 找到第一個</div>
    
    print(f"章節網格範圍: {grid_start} - {grid_end}")
    
    # 提取網格內容
    grid_content = content[grid_start:grid_end]
    
    print(f"網格內容長度: {len(grid_content)}")
    
    # 提取所有chapter-card
    cards = re.findall(r'<div class="chapter-card">.*?</div>\s*</div>\s*</div>', grid_content, re.DOTALL)
    
    print(f"找到 {len(cards)} 個章節卡片")
    
    # 提取章節號的函數
    def get_chapter_num(card):
        match = re.search(r'chapter-(\d+)-av\.html', card)
        return int(match.group(1)) if match else 0
    
    # 顯示當前順序（前10個）
    print("\n當前順序（前10個）:")
    for i, card in enumerate(cards[:10]):
        num = get_chapter_num(card)
        print(f"  {i+1}. Chapter {num}")
    
    # 按章節號降序排序
    sorted_cards = sorted(cards, key=get_chapter_num, reverse=True)
    
    print("\n排序後順序（前10個）:")
    for i, card in enumerate(sorted_cards[:10]):
        num = get_chapter_num(card)
        print(f"  {i+1}. Chapter {num}")
    
    # 驗證
    nums = [get_chapter_num(c) for c in sorted_cards]
    is_sorted = all(nums[i] >= nums[i+1] for i in range(len(nums)-1))
    print(f"\n驗證排序: {'✅ 正確' if is_sorted else '❌ 錯誤'}")
    
    # 檢查75和76
    for i, num in enumerate(nums):
        if num in [75, 76]:
            print(f"  章節 {num} 在位置 {i+1}")
    
    # 重建網格內容
    new_grid_content = '<div class="chapter-grid" id="chapterGrid">\n' + '\n'.join(sorted_cards) + '\n</div>'
    
    # 替換原內容
    new_content = content[:grid_start] + new_grid_content + content[grid_end:]
    
    # 寫回
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"\n✅ 已修復並保存")
    return True

if __name__ == '__main__':
    print("=== 修復av-novels.html章節排序 ===\n")
    fix_av_order()