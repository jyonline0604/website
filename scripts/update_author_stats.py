#!/usr/bin/env python3
"""
更新作者頁面 (author.html) 的章節統計數字
"""

import os
import re
import sys
from pathlib import Path

WORKSPACE = "/home/openclaw/.openclaw/workspace"
NOVEL_DIR = WORKSPACE

def sort_av_novels_chapters(workspace):
    """自動排序 av-novels.html 的章節順序（最新章節放最前面）"""
    av_path = Path(workspace) / "av-novels.html"
    
    if not av_path.exists():
        print(f"   ⚠️ 找不到 {av_path}，跳過排序")
        return
    
    content = av_path.read_text(encoding='utf-8')
    
    # 找到 chapter-grid
    grid_start = content.find('<div class="chapter-grid" id="chapterGrid">')
    if grid_start == -1:
        print("   ⚠️ 找不到 chapter-grid，跳過排序")
        return
    
    # 找到最後一個章節內容區塊的位置
    content_positions = list(re.finditer(r'<div class="chapter-card-content">', content))
    if not content_positions:
        print("   ⚠️ 找不到任何章節內容區塊，跳過排序")
        return
    
    last_content_pos = content_positions[-1].start()
    
    # 找到 grid 的結束位置
    grid_end_match = re.search(r'<\/div>\s*<\/div>', content[last_content_pos:])
    if not grid_end_match:
        print("   ⚠️ 找不到 grid 結束標籤，跳過排序")
        return
    
    grid_end = last_content_pos + grid_end_match.end()
    
    # 提取所有章節卡片 - 使用 split 代替正則表達式，避免多行匹配問題
    grid_section = content[grid_start:grid_end]
    parts = grid_section.split('<div class="chapter-card">')
    cards = ['<div class="chapter-card">' + part for part in parts[1:]]  # Skip first part (before first card)
    
    if not cards:
        print("   ⚠️ 找不到任何章節卡片，跳過排序")
        return
    
    # 提取章節號的函數
    def get_chapter_num(card):
        match = re.search(r'chapter-(\d+)-av\.html', card)
        if match:
            return int(match.group(1))
        title_match = re.search(r'第 (\d+) 章', card)
        return int(title_match.group(1)) if title_match else 0
    
    # 檢查當前是否已排序
    original_nums = [get_chapter_num(c) for c in cards]
    is_already_sorted = all(original_nums[i] >= original_nums[i+1] for i in range(len(original_nums)-1))
    
    if is_already_sorted:
        print(f"   ✅ 章節順序已正確 ({len(cards)} 章)")
        return
    
    # 按章節號降序排序（最新放最前）
    sorted_cards = sorted(cards, key=get_chapter_num, reverse=True)
    sorted_nums = [get_chapter_num(c) for c in sorted_cards]
    
    # 重建 grid 內容
    new_grid_content = '<div class="chapter-grid" id="chapterGrid">\n' + '\n'.join(sorted_cards) + '\n</div>'
    
    # 替換原內容
    new_content = content[:grid_start] + new_grid_content + content[grid_end:]
    
    # 寫回文件
    av_path.write_text(new_content, encoding='utf-8')
    print(f"   ✅ 已重新排序 ({len(sorted_cards)} 章): {sorted_nums[0]} → {sorted_nums[-1]}")


def count_chapters():
    """計算實際章節數量"""
    # 計算文字版章節（排除AV版本和模板）
    text_chapters = 0
    for filename in os.listdir(NOVEL_DIR):
        if filename.startswith("chapter-") and filename.endswith(".html"):
            # 排除AV版本
            if "-av.html" in filename:
                continue
            # 排除模板文件
            if "template" in filename:
                continue
            # 排除備份文件
            if "backup" in filename:
                continue
            
            # 驗證是有效的章節文件
            match = re.match(r"chapter-(\d+)\.html", filename)
            if match:
                text_chapters += 1
    
    # 計算AV章節數量
    av_chapters = 0
    for filename in os.listdir(NOVEL_DIR):
        if filename.startswith("chapter-") and filename.endswith("-av.html"):
            match = re.match(r"chapter-(\d+)-av\.html", filename)
            if match:
                av_chapters += 1
    
    return text_chapters, av_chapters

def update_author_html(text_chapters):
    """更新author.html中的章節統計"""
    author_path = os.path.join(NOVEL_DIR, "author.html")
    
    if not os.path.exists(author_path):
        print(f"❌ 文件不存在: {author_path}")
        return False
    
    try:
        with open(author_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找並替換章節數量
        # 模式：目前已有 [數字] 章
        pattern = r'目前已有\s*(\d+)\s*章'
        
        if re.search(pattern, content):
            # 替換為新的章節數量
            new_content = re.sub(pattern, f'目前已有 {text_chapters} 章', content)
            
            # 檢查是否有變化
            if new_content != content:
                with open(author_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✅ 已更新 author.html: 64 → {text_chapters} 章")
                return True
            else:
                print(f"ℹ️ author.html 已經是最新: {text_chapters} 章")
                return True
        else:
            print("❌ 在 author.html 中找不到章節統計文本")
            return False
            
    except Exception as e:
        print(f"❌ 更新 author.html 時出錯: {e}")
        return False

def update_av_novels_stats(text_chapters, av_chapters):
    """更新av-novels.html中的統計數字"""
    av_path = os.path.join(NOVEL_DIR, "av-novels.html")
    
    if not os.path.exists(av_path):
        print(f"ℹ️ 文件不存在: {av_path}")
        return True  # 不是錯誤，只是跳過
    
    try:
        with open(av_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        changed = False
        
        # 1. 更新已完成章節數 (AV章節數)
        # 查找 <div class="stat-number" id="totalChapters">[數字]</div>
        av_pattern = r'(<div class="stat-number" id="totalChapters">)\d+(</div>)'
        if re.search(av_pattern, content):
            new_content = re.sub(av_pattern, f'\\g<1>{av_chapters}\\g<2>', content)
            if new_content != content:
                content = new_content
                changed = True
                print(f"✅ 已更新 av-novels.html: AV章節數 → {av_chapters}")
        
        # 2. 更新總章節數
        # 查找第二個stat-number（總章節數）
        # 先找到所有stat-number
        stat_numbers = list(re.finditer(r'<div class="stat-number">(\d+)</div>', content))
        if len(stat_numbers) >= 2:
            # 第二個是總章節數
            total_pattern = stat_numbers[1].group(0)  # 完整的匹配文本
            total_number = stat_numbers[1].group(1)   # 數字部分
            
            if int(total_number) != text_chapters:
                new_total = total_pattern.replace(total_number, str(text_chapters))
                content = content.replace(total_pattern, new_total)
                changed = True
                print(f"✅ 已更新 av-novels.html: 總章節數 {total_number} → {text_chapters}")
        
        # 3. 更新完成度
        if len(stat_numbers) >= 3:
            # 第三個是完成度百分比
            percent_pattern = stat_numbers[2].group(0)
            percent_number = stat_numbers[2].group(1).replace('%', '')
            
            # 計算新的完成度
            if text_chapters > 0:
                new_percent = round((av_chapters / text_chapters) * 100)
                if int(percent_number) != new_percent:
                    new_percent_text = percent_pattern.replace(percent_number + '%', str(new_percent) + '%')
                    content = content.replace(percent_pattern, new_percent_text)
                    changed = True
                    print(f"✅ 已更新 av-novels.html: 完成度 {percent_number}% → {new_percent}%")
        
        if changed:
            with open(av_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return True
        
    except Exception as e:
        print(f"❌ 更新 av-novels.html 時出錯: {e}")
        return False

def main():
    print("📊 更新作者頁面和統計數字")
    print("=" * 50)
    
    # 計算章節數量
    text_chapters, av_chapters = count_chapters()
    print(f"📚 文字版章節: {text_chapters} 章")
    print(f"🎬 AV版章節: {av_chapters} 章")
    
    if text_chapters == 0:
        print("❌ 錯誤：沒有找到章節文件")
        return 1
    
    # 更新author.html
    print(f"\n🔄 更新 author.html...")
    if not update_author_html(text_chapters):
        return 1
    
    # 更新av-novels.html
    print(f"\n🔄 更新 av-novels.html...")
    if not update_av_novels_stats(text_chapters, av_chapters):
        return 1
    
    # 排序 av-novels.html 章節（確保最新章節在最前面）
    print(f"\n🔄 排序 av-novels.html 章節...")
    sort_av_novels_chapters(NOVEL_DIR)
    
    print(f"\n{'='*50}")
    print("🎉 更新完成！")
    print(f"📊 最新統計:")
    print(f"  • 文字版章節: {text_chapters} 章")
    print(f"  • AV版章節: {av_chapters} 章")
    print(f"  • 完成度: {round((av_chapters / text_chapters) * 100)}%")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())