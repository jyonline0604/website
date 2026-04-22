#!/usr/bin/env python3
"""
全面檢查 av-novels.html 的所有可能問題
"""

import re
import os
from pathlib import Path

def check_all():
    """檢查所有可能問題"""
    workspace = Path("/home/openclaw/.openclaw/workspace")
    av_path = workspace / "av-novels.html"
    
    if not av_path.exists():
        print("❌ 錯誤: 找不到 av-novels.html")
        return False
    
    content = av_path.read_text(encoding='utf-8')
    
    print("🔍 全面檢查 av-novels.html")
    print("=" * 60)
    
    # 1. 檢查章節排序
    print("1. 檢查章節排序...")
    pattern = r'chapter-(\d+)-av\.html'
    matches = re.findall(pattern, content)
    
    if not matches:
        print("   ❌ 找不到任何章節")
        return False
    
    nums = [int(m) for m in matches]
    print(f"   總章節數: {len(nums)}")
    print(f"   章節範圍: 第{min(nums)}章 到 第{max(nums)}章")
    
    # 檢查排序
    errors = []
    for i in range(len(nums)-1):
        if nums[i] < nums[i+1]:
            errors.append((i, nums[i], nums[i+1]))
    
    if errors:
        print(f"   ❌ 發現 {len(errors)} 個排序錯誤")
        for i, a, b in errors[:5]:
            print(f"     位置 {i}: 第{a}章 在 第{b}章 之後")
        if len(errors) > 5:
            print(f"     ... 還有 {len(errors)-5} 個錯誤")
    else:
        print("   ✅ 章節按降序排列正確")
    
    # 2. 檢查缺失章節
    print("\n2. 檢查缺失章節...")
    all_nums = set(nums)
    missing = []
    for i in range(2, max(nums) + 1):  # 從第2章開始檢查
        if i not in all_nums:
            missing.append(i)
    
    if missing:
        print(f"   ❌ 發現 {len(missing)} 個缺失章節")
        print(f"     缺失: {missing[:10]}{'...' if len(missing) > 10 else ''}")
    else:
        print("   ✅ 沒有缺失章節 (除了第1章)")
    
    # 3. 檢查重複章節
    print("\n3. 檢查重複章節...")
    from collections import Counter
    counts = Counter(nums)
    duplicates = [num for num, count in counts.items() if count > 1]
    
    if duplicates:
        print(f"   ❌ 發現 {len(duplicates)} 個重複章節: {duplicates}")
    else:
        print("   ✅ 沒有重複章節")
    
    # 4. 檢查HTML結構
    print("\n4. 檢查HTML結構...")
    
    # 檢查是否有正確的grid結構
    if '<div class="chapter-grid" id="chapterGrid">' in content:
        print("   ✅ 找到 chapter-grid")
    else:
        print("   ❌ 找不到 chapter-grid")
    
    # 檢查章節卡片數量是否匹配
    card_pattern = r'<div class="chapter-card"'
    card_count = len(re.findall(card_pattern, content))
    print(f"   章節卡片數量: {card_count} (應該為 {len(nums)})")
    
    if card_count == len(nums):
        print("   ✅ 卡片數量匹配")
    else:
        print(f"   ❌ 卡片數量不匹配! 連結: {len(nums)}, 卡片: {card_count}")
    
    # 5. 檢查圖片連結
    print("\n5. 檢查圖片連結...")
    
    # 檢查是否有章節缺少圖片
    img_pattern = r'<img src="assets/chapter-(\d+)-scene'
    img_matches = re.findall(img_pattern, content)
    img_nums = [int(m) for m in img_matches]
    
    missing_imgs = []
    for num in nums:
        if num not in img_nums:
            missing_imgs.append(num)
    
    if missing_imgs:
        print(f"   ❌ {len(missing_imgs)} 個章節缺少圖片: {missing_imgs[:10]}{'...' if len(missing_imgs) > 10 else ''}")
    else:
        print(f"   ✅ 所有 {len(nums)} 個章節都有圖片")
    
    # 6. 檢查實際文件是否存在
    print("\n6. 檢查AV章節文件是否存在...")
    missing_files = []
    for num in nums[:10]:  # 只檢查前10個
        file_path = workspace / f"chapter-{num}-av.html"
        if not file_path.exists():
            missing_files.append(num)
    
    if missing_files:
        print(f"   ❌ {len(missing_files)} 個AV文件不存在: {missing_files}")
    else:
        print("   ✅ 前10個AV章節文件都存在")
    
    # 7. 檢查標題是否匹配
    print("\n7. 檢查標題是否匹配...")
    
    # 提取前3個章節的標題
    card_pattern = r'<div class="chapter-card">.*?</div>\s*</div>\s*</div>'
    cards = re.findall(card_pattern, content, re.DOTALL)
    
    if cards:
        print("   前3個章節標題:")
        for i, card in enumerate(cards[:3], 1):
            num_match = re.search(r'chapter-(\d+)-av\.html', card)
            num = num_match.group(1) if num_match else '?'
            
            title_match = re.search(r'<h3 class="chapter-title">(.*?)</h3>', card)
            title = title_match.group(1) if title_match else '?'
            
            print(f"     第{num}章: {title}")
    else:
        print("   ❌ 無法提取章節卡片")
    
    print("\n" + "=" * 60)
    
    # 總結
    has_errors = bool(errors or missing or duplicates or missing_imgs or missing_files)
    
    if has_errors:
        print("❌ 發現問題，需要修復")
        return False
    else:
        print("✅ 所有檢查通過")
        return True

if __name__ == "__main__":
    check_all()