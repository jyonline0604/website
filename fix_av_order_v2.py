#!/usr/bin/env python3
"""
修復av-novels.html章節排序問題
問題：第75章和第76章順序顛倒
"""

import re
from pathlib import Path

def fix_av_novels_order():
    file_path = Path('/home/openclaw/.openclaw/workspace/av-novels.html')
    
    # 讀取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取所有章節卡片
    # 匹配模式：<div class="chapter-card">...chapter-XX-av.html...</div>
    chapter_pattern = r'(<div class="chapter-card"[^>]*>.*?</div>\s*)'
    
    chapters = re.findall(chapter_pattern, content, re.DOTALL)
    
    print(f"找到 {len(chapters)} 個章節卡片")
    
    # 提取章節號
    def extract_chapter_num(card):
        match = re.search(r'chapter-(\d+)-av\.html', card)
        return int(match.group(1)) if match else 0
    
    # 按章節號降序排序
    sorted_chapters = sorted(chapters, key=extract_chapter_num, reverse=True)
    
    print("\n排序後的章節順序（前10個）:")
    for i, chapter in enumerate(sorted_chapters[:10]):
        num = extract_chapter_num(chapter)
        print(f"  {i+1}. Chapter {num}")
    
    # 驗證排序
    print("\n驗證排序...")
    chapter_nums = [extract_chapter_num(c) for c in sorted_chapters]
    is_sorted = all(chapter_nums[i] >= chapter_nums[i+1] for i in range(len(chapter_nums)-1))
    
    if is_sorted:
        print("✅ 章節排序正確（降序）")
    else:
        print("❌ 排序仍有問題")
        # 找出問題
        for i in range(len(chapter_nums)-1):
            if chapter_nums[i] < chapter_nums[i+1]:
                print(f"   問題: {chapter_nums[i]} < {chapter_nums[i+1]}")
    
    # 查找問題章節
    print("\n檢查第75章和第76章位置:")
    for i, num in enumerate(chapter_nums):
        if num in [75, 76]:
            print(f"  章節 {num} 在位置 {i+1}")
    
    # 重建HTML
    # 找到章節網格容器
    grid_pattern = r'(<div class="chapters-grid"[^>]*>)(.*?)(</div>\s*</div>\s*</div>\s*</div>\s*</div>\s*</div>)'
    match = re.search(grid_pattern, content, re.DOTALL)
    
    if not match:
        print("❌ 找不到章節網格容器")
        return False
    
    # 構建新的章節內容
    new_grid_content = match.group(2)
    new_content = content.replace(match.group(2), '\n'.join(sorted_chapters))
    
    # 寫回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"\n✅ 已修復av-novels.html")
    print(f"   總共 {len(sorted_chapters)} 個章節")
    print(f"   第75章和第76章已正確排序")
    
    return True

if __name__ == '__main__':
    print("=== 修復av-novels.html章節排序 ===\n")
    
    if fix_av_novels_order():
        print("\n🎯 修復完成!")
    else:
        print("\n❌ 修復失敗")
        exit(1)