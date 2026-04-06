#!/usr/bin/env python3
import re

# Read the av-novels.html file
with open('av-novels.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Update statistics
# Total AV chapters: 46 (after adding chapter 46)
# Total chapters: 81
# Completion: 46/81 = 56.79% ≈ 57%

# Update total chapters count
content = re.sub(r'<div class="stat-number" id="totalChapters">\d+</div>', 
                 '<div class="stat-number" id="totalChapters">46</div>', content)

# Update completion percentage (57%)
content = re.sub(r'<div class="stat-number">\d+%</div>\s*<div class="stat-label">完成度</div>',
                 '<div class="stat-number">57%</div>\n                <div class="stat-label">完成度</div>', content)

# Create new chapter card for chapter 46
new_chapter_card = '''            <div class="chapter-card">
                <div class="chapter-card-image">
                    <img src="assets/chapter-46-scene1.jpg" alt="第46章">
                    <div class="chapter-badge">New</div>
                </div>
                <div class="chapter-card-content">
                    <div class="chapter-number">第 46 章</div>
                    <h3 class="chapter-title">量子金丹</h3>
                    <p class="chapter-desc">林塵進行仿生金丹實驗引發量子坍縮，發現金丹紋路與銀河系懸臂吻合，未來自己現身警告時間線收束！</p>
                    <div class="chapter-actions">
                        <a href="chapter-46-av.html" class="btn btn-primary">🎬 有聲畫</a>
                        <a href="chapter-46.html" class="btn btn-secondary">文字版</a>
                    </div>
                </div>
            </div>

'''

# Find where to insert the new chapter card (after the chapter-grid opening div)
# We need to insert it after the opening of chapter-grid and before the existing first chapter card
pattern = r'(<div class="chapter-grid" id="chapterGrid">\s*\n)'
match = re.search(pattern, content)
if match:
    # Insert new chapter card after the chapter-grid opening
    insert_pos = match.end()
    content = content[:insert_pos] + new_chapter_card + content[insert_pos:]
    
    # Remove "New" badge from the previous newest chapter (chapter 45)
    content = re.sub(r'<div class="chapter-badge">New</div>\s*\n\s*</div>\s*\n\s*<div class="chapter-card-content">\s*\n\s*<div class="chapter-number">第 45 章</div>',
                     '</div>\n                <div class="chapter-card-content">\n                    <div class="chapter-number">第 45 章</div>', content)

# Write the updated content back
with open('av-novels.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated av-novels.html with chapter 46 and new statistics")