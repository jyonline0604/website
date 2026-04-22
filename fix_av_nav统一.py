#!/usr/bin/env python3
"""Fix navigation bar for chapters 79-81 to match chapter 76 style."""

import re

def fix_chapter_76_style(ch_num, prev_ch, next_ch):
    filename = f'chapter-{ch_num}-av.html'
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The new nav HTML matching chapter 76 style
    new_nav = f'''<!-- Skip Navigation Link -->
    <a href="#main-content" class="skip-navigation" style="position:absolute;left:-9999px;top:auto;width:1px;height:1px;overflow:hidden;z-index:-1;">跳到主要內容</a>
    <!-- Navigation -->
            <nav aria-label="主要導航" class="nav">
        <a href="chapter-{ch_num}.html">← 文字版</a>
        <a href="chapter-{prev_ch}-av.html">第{prev_ch}章</a>
        <a href="chapter-{next_ch}-av.html">第{next_ch}章</a>
        <a href="av-novels.html">📚 目錄</a>
    </nav>'''
    
    # Pattern to match the old nav-bar
    old_pattern = r'<!-- Navigation -->\s*<nav class="nav-bar">.*?</nav>'
    
    if re.search(old_pattern, content, re.DOTALL):
        content = re.sub(old_pattern, new_nav, content, flags=re.DOTALL)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {filename}")
        return True
    else:
        print(f"No nav-bar found in {filename}")
        return False

# Fix chapters 79, 80, 81
fix_chapter_76_style(79, 78, 80)
fix_chapter_76_style(80, 79, 81)
fix_chapter_76_style(81, 80, 82)
