#!/usr/bin/env python3
import re
import sys

with open('av-novels.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find chapter grid
start = content.find('<div class="chapter-grid" id="chapterGrid">')
if start == -1:
    print("找不到 chapter-grid")
    sys.exit(1)

# Find end of grid
end = start
div_level = 0
for i in range(start, len(content)):
    if content[i:i+5] == '<div ':
        div_level += 1
    elif content[i:i+6] == '</div>':
        div_level -= 1
        if div_level == 0:
            end = i + 6
            break

grid_content = content[start:end]

# Extract chapter cards using a simpler method
# Each card starts with <div class="chapter-card">
cards = []
pos = 0
while True:
    card_start = grid_content.find('<div class="chapter-card"', pos)
    if card_start == -1:
        break
    
    # Find the end of this card
    card_end = card_start
    card_div_level = 0
    for i in range(card_start, len(grid_content)):
        if grid_content[i:i+5] == '<div ':
            card_div_level += 1
        elif grid_content[i:i+6] == '</div>':
            card_div_level -= 1
            if card_div_level == 0:
                card_end = i + 6
                break
    
    if card_end > card_start:
        cards.append(grid_content[card_start:card_end])
        pos = card_end
    else:
        break

print(f"找到 {len(cards)} 個章節卡片")

# Get chapter numbers
def get_num(card):
    m = re.search(r'chapter-(\d+)-av\.html', card)
    if m:
        return int(m.group(1))
    m = re.search(r'第\s*(\d+)\s*章', card)
    if m:
        return int(m.group(1))
    return 0

nums = [get_num(c) for c in cards]
print(f"章節順序: {nums[:10]}...")

# Check if sorted
is_sorted = all(nums[i] >= nums[i+1] for i in range(len(nums)-1))
if is_sorted:
    print("✅ 已經按降序排列")
    sys.exit(0)

print("⚠️  排序錯誤，正在修復...")

# Sort by chapter number (descending)
sorted_pairs = sorted(zip(nums, cards), key=lambda x: x[0], reverse=True)
sorted_cards = [c for _, c in sorted_pairs]
sorted_nums = [n for n, _ in sorted_pairs]

print(f"修復後順序: {sorted_nums[:10]}...")

# Rebuild grid
new_grid = '<div class="chapter-grid" id="chapterGrid">\n' + '\n'.join(sorted_cards) + '\n</div>'

# Replace in content
new_content = content[:start] + new_grid + content[end:]

# Write back
with open('av-novels.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"✅ 已修復排序: {sorted_nums[0]} → {sorted_nums[-1]}")