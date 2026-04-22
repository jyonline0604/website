# Simple script to repair av-novels.html order
import re

with open('av-novels.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find the chapter grid section
start = html.find('<div class="chapter-grid" id="chapterGrid">')
end = html.find('</div>', html.find('</div>', html.find('</div>', start + 1) + 1) + 1)

if start == -1 or end == -1:
    print("Could not find chapter grid")
    exit(1)

grid_html = html[start:end]

# Find all chapter cards
cards = []
pos = 0
while True:
    card_start = grid_html.find('<div class="chapter-card"', pos)
    if card_start == -1:
        break
    card_end = grid_html.find('</div>', grid_html.find('</div>', grid_html.find('</div>', card_start + 1) + 1) + 1)
    if card_end == -1:
        break
    cards.append(grid_html[card_start:card_end+6])
    pos = card_end + 6

print(f"Found {len(cards)} chapter cards")

# Extract chapter numbers
def get_chap_num(card):
    m = re.search(r'chapter-(\d+)-av\.html', card)
    return int(m.group(1)) if m else 0

chap_nums = [get_chap_num(c) for c in cards]
print(f"Chapter numbers: {chap_nums[:10]}...")

# Check if already sorted
if all(chap_nums[i] >= chap_nums[i+1] for i in range(len(chap_nums)-1)):
    print("Already sorted correctly")
    exit(0)

# Sort cards by chapter number (descending)
sorted_pairs = sorted(zip(chap_nums, cards), key=lambda x: x[0], reverse=True)
sorted_cards = [card for _, card in sorted_pairs]
sorted_nums = [num for num, _ in sorted_pairs]

print(f"Sorted numbers: {sorted_nums[:10]}...")

# Rebuild grid
new_grid = '<div class="chapter-grid" id="chapterGrid">\n' + '\n'.join(sorted_cards) + '\n</div>'

# Replace in original HTML
new_html = html[:start] + new_grid + html[end:]

# Write back
with open('av-novels.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print("Fixed av-novels.html order")