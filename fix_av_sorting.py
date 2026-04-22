#!/usr/bin/env python3
"""
修復 av-novels.html 章節排序問題
章節應該按降序排列（最新章節在最前面）
"""

import re
import os
from pathlib import Path

def extract_chapter_cards(html_content):
    """從 HTML 內容中提取所有章節卡片"""
    cards = []
    current_card = []
    in_card = False
    div_level = 0
    
    lines = html_content.split('\n')
    for line in lines:
        if '<div class="chapter-card"' in line:
            in_card = True
            div_level = 0
        
        if in_card:
            current_card.append(line)
            # 計算 div 層級
            div_level += line.count('<div')
            div_level -= line.count('</div')
            
            # 如果 div_level 回到 0，表示章節卡片結束
            if div_level == 0 and current_card:
                cards.append('\n'.join(current_card))
                current_card = []
                in_card = False
    
    return cards

def get_chapter_number(card):
    """從章節卡片中提取章節號"""
    # 方法1: 從鏈接中提取
    match = re.search(r'chapter-(\d+)-av\.html', card)
    if match:
        return int(match.group(1))
    
    # 方法2: 從章節號中提取
    match = re.search(r'第\s*(\d+)\s*章', card)
    if match:
        return int(match.group(1))
    
    # 方法3: 從圖片中提取
    match = re.search(r'chapter-(\d+)-scene', card)
    if match:
        return int(match.group(1))
    
    return 0

def fix_av_novels_sorting():
    """修復 av-novels.html 的章節排序"""
    workspace = "/home/openclaw/.openclaw/workspace"
    av_path = Path(workspace) / "av-novels.html"
    
    if not av_path.exists():
        print(f"錯誤: 找不到 {av_path}")
        return False
    
    print(f"讀取 {av_path}...")
    content = av_path.read_text(encoding='utf-8')
    
    # 找到 chapter-grid 的開始和結束位置
    grid_start = content.find('<div class="chapter-grid" id="chapterGrid">')
    if grid_start == -1:
        print("錯誤: 找不到 chapter-grid")
        return False
    
    # 找到 grid 的結束位置（下一個相同層級的 </div>）
    grid_end = grid_start
    div_level = 0
    for i in range(grid_start, len(content)):
        if content[i:i+5] == '<div ':
            div_level += 1
        elif content[i:i+6] == '</div>':
            div_level -= 1
            if div_level == 0:
                grid_end = i + 6
                break
    
    if grid_end <= grid_start:
        print("錯誤: 找不到 grid 結束位置")
        return False
    
    # 提取 grid 內容
    grid_content = content[grid_start:grid_end]
    
    # 提取所有章節卡片
    cards = extract_chapter_cards(grid_content)
    
    if not cards:
        print("錯誤: 找不到任何章節卡片")
        return False
    
    print(f"找到 {len(cards)} 個章節卡片")
    
    # 獲取每個卡片的章節號
    chapter_numbers = [get_chapter_number(card) for card in cards]
    print(f"章節號: {chapter_numbers[:10]}...")
    
    # 檢查當前排序
    is_sorted_desc = all(chapter_numbers[i] >= chapter_numbers[i+1] for i in range(len(chapter_numbers)-1))
    
    if is_sorted_desc:
        print("✅ 章節已經按降序排列")
        return True
    
    print("⚠️  章節排序錯誤，正在修復...")
    
    # 按章節號降序排序
    sorted_pairs = sorted(zip(chapter_numbers, cards), key=lambda x: x[0], reverse=True)
    sorted_cards = [card for _, card in sorted_pairs]
    sorted_numbers = [num for num, _ in sorted_pairs]
    
    print(f"修復後章節號: {sorted_numbers[:10]}...")
    
    # 重建 grid 內容
    new_grid_content = '<div class="chapter-grid" id="chapterGrid">\n' + '\n'.join(sorted_cards) + '\n</div>'
    
    # 替換原內容
    new_content = content[:grid_start] + new_grid_content + content[grid_end:]
    
    # 寫回文件
    av_path.write_text(new_content, encoding='utf-8')
    
    print(f"✅ 已修復排序: {sorted_numbers[0]} → {sorted_numbers[-1]}")
    return True

def analyze_sorting_problem():
    """分析排序問題的根本原因"""
    print("🔍 分析排序問題...")
    
    # 檢查 generate_av_chapter.py 腳本
    script_path = Path("/home/openclaw/.openclaw/workspace/scripts/generate_av_chapter.py")
    if script_path.exists():
        script_content = script_path.read_text(encoding='utf-8')
        if 'sort_av_novels' in script_content:
            print("✅ generate_av_chapter.py 包含排序函數")
        else:
            print("❌ generate_av_chapter.py 缺少排序函數")
    
    # 檢查 cron 任務
    print("\n📅 檢查 cron 任務...")
    os.system("crontab -l 2>/dev/null | grep -i av")
    
    # 檢查最近的 AV 章節生成記錄
    print("\n📝 檢查最近的 AV 章節生成...")
    av_files = list(Path("/home/openclaw/.openclaw/workspace").glob("chapter-*-av.html"))
    av_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    if av_files:
        latest = av_files[0]
        print(f"最新的 AV 章節: {latest.name}")
        print(f"修改時間: {latest.stat().st_mtime}")
    else:
        print("找不到 AV 章節文件")

if __name__ == "__main__":
    print("🔄 開始修復 av-novels.html 章節排序問題")
    print("=" * 60)
    
    # 分析問題
    analyze_sorting_problem()
    
    print("\n" + "=" * 60)
    print("🔧 開始修復排序...")
    
    # 修復排序
    if fix_av_novels_sorting():
        print("\n✅ 修復完成！")
        print("\n📋 建議措施:")
        print("1. 更新 novel-av-generator SKILL.md 記錄此問題")
        print("2. 確保 generate_av_chapter.py 在生成新章節後自動調用排序")
        print("3. 添加定期檢查腳本，防止排序問題再次發生")
    else:
        print("\n❌ 修復失敗")