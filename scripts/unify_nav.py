#!/usr/bin/env python3
"""統一全站導航列"""
import re, os

WORKSPACE = "/home/openclaw/.openclaw/workspace"

UNIFIED_NAV = '''        <a href="home.html"{home_active}>首頁</a>
        <a href="chapters.html"{chapters_active}>章節</a>
        <a href="news.html"{news_active}>AI 新聞</a>
        <a href="finance.html"{finance_active}>財經</a>
        <a href="https://itv.kofhk.com/" rel="noopener noreferrer"{itv_active}>ITV</a>
        <a href="dashboard.html"{dashboard_active}>城市儀表板</a>
        <a href="bus-eta.html"{bus_active}>巴士報站</a>
        <a href="author.html"{author_active}>作者</a>'''

# Which pages to update and their active link
PAGES = {
    "home.html": "home",
    "index.html": "home",
    "chapters.html": "chapters",
    "chapters-v2-preview.html": "chapters",
    "chapters-v3-preview.html": "chapters",
    "home-v2-preview.html": "home",
    "finance.html": "finance",
    "news.html": "news",
    "dashboard.html": "dashboard",
    "bus-eta.html": "bus",
    "author.html": "author",
}

updated = 0
for filename, active_page in PAGES.items():
    filepath = os.path.join(WORKSPACE, filename)
    if not os.path.exists(filepath):
        print(f"  ⚠️ {filename}: not found, skipping")
        continue
    
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    # Build the nav with active class
    nav_html = UNIFIED_NAV.format(
        home_active=' class="active"' if active_page == "home" else "",
        chapters_active=' class="active"' if active_page == "chapters" else "",
        news_active=' class="active"' if active_page == "news" else "",
        finance_active=' class="active"' if active_page == "finance" else "",
        itv_active=' class="active"' if active_page == "itv" else "",
        dashboard_active=' class="active"' if active_page == "dashboard" else "",
        author_active=' class="active"' if active_page == "author" else "",
        bus_active=' class="active"' if active_page == "bus" else "",
    )
    
    # Find and replace the <nav> block
    # Different pages have different nav structures, find the common pattern
    nav_start = None
    nav_end = None
    
    # Pattern 1: <nav class="nav" id="navMenu">...</nav>
    m = re.search(r'(<nav[^>]*id="navMenu"[^>]*>).*?(</nav>)', content, re.DOTALL)
    if m:
        nav_start, nav_end = m.start(1), m.end(2)
    
    # Pattern 2: <nav aria-label="主要導航" ...>...</nav>
    if nav_start is None:
        m = re.search(r'(<nav[^>]*aria-label="[^"]*導航[^"]*"[^>]*>).*?(</nav>)', content, re.DOTALL)
        if m:
            nav_start, nav_end = m.start(1), m.end(2)
    
    # Pattern 3: Just look for navMenu
    if nav_start is None:
        m = re.search(r'id="navMenu"[^>]*>', content)
        if m:
            # find surrounding nav tags
            before = content[:m.end()]
            start_pos = before.rfind('<nav')
            if start_pos >= 0:
                # find matching </nav>
                depth = 1
                pos = m.end()
                while depth > 0 and pos < len(content):
                    next_open = content.find('<nav', pos)
                    next_close = content.find('</nav>', pos)
                    if next_close == -1:
                        break
                    if next_open != -1 and next_open < next_close:
                        depth += 1
                        pos = next_open + 1
                    else:
                        depth -= 1
                        if depth == 0:
                            nav_start = start_pos
                            nav_end = next_close + 6
                        pos = next_close + 6

    if nav_start is None:
        print(f"  ❌ {filename}: nav not found")
        continue
    
    # Get the opening tag
    opening_tag = content[nav_start:content.index('>', nav_start)+1]
    
    new_nav = opening_tag + '\n' + nav_html + '\n    </nav>'
    new_content = content[:nav_start] + new_nav + content[nav_end:]
    
    with open(filepath, 'w', encoding='utf-8-sig') as f:
        f.write(new_content)
    
    print(f"  ✅ {filename}: unified nav ({active_page} active)")
    updated += 1

print(f"\n✅ {updated} pages updated")
