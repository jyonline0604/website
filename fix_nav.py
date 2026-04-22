import re

def fix_chapter(ch_num, prev_ch, next_ch):
    filename = f'chapter-{ch_num}-av.html'
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The old problematic nav pattern
    old_nav_pattern = r'<nav class="nav-bar">\s*<a href="[^"]*">← 章節目錄</a>\s*<div class="nav-center">\s*<button class="nav-btn" onclick="prevScene\(\)">◀ 上一場景</button>\s*<button class="nav-btn" onclick="nextScene\(\)">下一場景 ▶</button>\s*</div>\s*<a href="chapter-\d+\.html">第\d+章 →</a>\s*</nav>'
    
    # New nav with proper chapter navigation
    prev_link = f'<a href="chapter-{prev_ch}-av.html">← 第{prev_ch}章</a>' if prev_ch else '<span style="opacity:0.3">← 上一章</span>'
    next_link = f'<a href="chapter-{next_ch}.html">第{next_ch}章 →</a>' if next_ch else '<span style="opacity:0.3">下一章 →</span>'
    
    new_nav = f'''<nav class="nav-bar">
        {prev_link}
        <div class="nav-center">
            <button class="nav-btn" onclick="prevScene()">◀ 上一場景</button>
            <button class="nav-btn" onclick="nextScene()">下一場景 ▶</button>
        </div>
        {next_link}
    </nav>'''
    
    # Check if this chapter has the problematic nav pattern
    if re.search(old_nav_pattern, content):
        content = re.sub(old_nav_pattern, new_nav, content)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {filename}")
        return True
    else:
        print(f"No change needed for {filename}")
        return False

# Fix chapters 79, 80, 81
fix_chapter(79, 78, 80)
fix_chapter(80, 79, 81)
fix_chapter(81, 80, None)  # 81 is the latest, no next chapter