#!/usr/bin/env python3
import re
import sys

def extract_chapter_cards(html_content):
    """從HTML中提取所有章節卡片"""
    # 使用更簡單的方法：找到所有chapter-card開始標籤
    cards = []
    start = 0
    
    while True:
        # 找到下一個chapter-card開始
        start = html_content.find('<div class="chapter-card">', start)
        if start == -1:
            break
        
        # 找到對應的結束
        # 計算div嵌套層級
        pos = start
        div_level = 0
        while pos < len(html_content):
            if html_content[pos:pos+5] == '<div ':
                div_level += 1
            elif html_content[pos:pos+6] == '</div>':
                div_level -= 1
                if div_level == 0:
                    end = pos + 6
                    card = html_content[start:end]
                    cards.append(card)
                    start = end
                    break
            pos += 1
        
        if pos >= len(html_content):
            break
    
    return cards

def get_chapter_number(card):
    """從卡片中提取章節號"""
    match = re.search(r'第\s*(\d+)\s*章', card)
    if match:
        return int(match.group(1))
    return 0

def sort_chapter_cards(cards):
    """按章節號降序排序卡片"""
    # 創建(章節號, 卡片)的列表
    chapter_cards = []
    for card in cards:
        chapter_num = get_chapter_number(card)
        if chapter_num > 0:
            chapter_cards.append((chapter_num, card))
    
    # 按章節號降序排序
    chapter_cards.sort(key=lambda x: x[0], reverse=True)
    
    # 返回排序後的卡片
    return [card for _, card in chapter_cards]

def fix_av_novels_order(input_file, output_file):
    """修復av-novels.html的章節次序"""
    # 讀取文件
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 分割文件：header + 章節網格部分 + footer
    # 找到章節網格的開始和結束
    grid_start = content.find('<div class="chapter-grid" id="chapterGrid">')
    if grid_start == -1:
        print("錯誤：找不到章節網格開始")
        return False
    
    # 找到章節網格結束（下一個</div>關閉章節網格）
    grid_content = content[grid_start:]
    
    # 提取所有章節卡片
    cards = extract_chapter_cards(grid_content)
    print(f"找到 {len(cards)} 個章節卡片")
    
    if len(cards) == 0:
        print("錯誤：沒有找到章節卡片")
        return False
    
    # 顯示當前的章節次序
    print("當前前10個章節次序：")
    for i, card in enumerate(cards[:10]):
        chap_num = get_chapter_number(card)
        print(f"  {i+1}. 第 {chap_num} 章")
    
    # 排序卡片
    sorted_cards = sort_chapter_cards(cards)
    
    print("\n排序後的前10個章節次序：")
    for i, card in enumerate(sorted_cards[:10]):
        chap_num = get_chapter_number(card)
        print(f"  {i+1}. 第 {chap_num} 章")
    
    # 重建章節網格內容
    new_grid_content = '<div class="chapter-grid" id="chapterGrid">\n'
    for card in sorted_cards:
        new_grid_content += '            ' + card.strip() + '\n'
    new_grid_content += '        </div>'
    
    # 替換原來的章節網格內容
    # 找到章節網格結束（在最後一個卡片之後）
    grid_end = grid_start
    temp_content = content[grid_start:]
    div_count = 0
    for i, char in enumerate(temp_content):
        if temp_content[i:i+5] == '<div ':
            div_count += 1
        elif temp_content[i:i+6] == '</div>':
            div_count -= 1
            if div_count == 0:
                grid_end = grid_start + i + 6
                break
    
    if grid_end <= grid_start:
        print("錯誤：無法找到章節網格結束")
        return False
    
    # 重建完整內容
    new_content = content[:grid_start] + new_grid_content + content[grid_end:]
    
    # 寫入輸出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"\n已修復章節次序並保存到: {output_file}")
    return True

if __name__ == "__main__":
    input_file = "/home/openclaw/.openclaw/workspace/av-novels.html"
    output_file = "/home/openclaw/.openclaw/workspace/av-novels-fixed.html"
    
    if fix_av_novels_order(input_file, output_file):
        print("修復成功！")
        sys.exit(0)
    else:
        print("修復失敗！")
        sys.exit(1)