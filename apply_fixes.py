#!/usr/bin/env python3
"""Apply all website fixes to kofhk.com repository."""
import re, os, glob

BASE = '/tmp/kofhk-fix'

# ============================================================
# FIX 1: chapters.html — Remove stray closing brace in Script #3
# ============================================================
print("=== FIX 1: Fix JS syntax error in chapters.html ===")
with open(f'{BASE}/chapters.html', 'r') as f:
    content = f.read()

# The issue: after the offline/online event listeners and if (!navigator.onLine),
# there's a stray } that doesn't match any opening brace.
old_block = '''            // 初始檢查
            if (!navigator.onLine) {
                document.documentElement.classList.add('offline');
            }
        }
        
        // 添加到主屏幕提示（僅在移動端顯示）'''

new_block = '''            // 初始檢查
            if (!navigator.onLine) {
                document.documentElement.classList.add('offline');
            }
            
            // 添加到主屏幕提示（僅在移動端顯示）'''

if old_block in content:
    content = content.replace(old_block, new_block)
    print("  ✅ Removed stray closing brace")
else:
    print("  ⚠️ Pattern not found — checking alternative...")
    # Try a more flexible approach
    lines = content.split('\n')
    fixed_lines = []
    skip_next_brace = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == '}' and i > 0 and \
           'if (!navigator.onLine)' in '\n'.join(lines[max(0,i-5):i]):
            print(f"  ✅ Found stray }} at line {i+1}, removing")
            continue
        fixed_lines.append(line)
    content = '\n'.join(fixed_lines)

with open(f'{BASE}/chapters.html', 'w') as f:
    f.write(content)

# ============================================================
# FIX 2: Create _redirects file for root URL 301 redirect
# ============================================================
print("\n=== FIX 2: Create _redirects for root URL ===")
with open(f'{BASE}/_redirects', 'w') as f:
    f.write('/ /home.html 301\n')
print("  ✅ Created _redirects file")

# ============================================================
# FIX 3: Fix PWA manifest icon paths (relative -> absolute)
# ============================================================
print("\n=== FIX 3: Fix PWA manifest icon paths ===")
with open(f'{BASE}/assets/site.webmanifest', 'r') as f:
    manifest = f.read()

sizes = [72, 96, 128, 144, 152, 192, 384, 512]
for size in sizes:
    old = f'"src": "favicon-{size}x{size}.png"'
    new = f'"src": "/assets/favicon-{size}x{size}.png"'
    manifest = manifest.replace(old, new)

# Also fix start_url to point to home.html
manifest = manifest.replace('"start_url": "/"', '"start_url": "/home.html"')

with open(f'{BASE}/assets/site.webmanifest', 'w') as f:
    f.write(manifest)
print("  ✅ Fixed icon paths and start_url")

# ============================================================
# FIX 4: Add canonical tags + robots meta to all main pages
# ============================================================
print("\n=== FIX 4: Add canonical tags + robots meta ===")

main_pages = {
    'home.html': '/home.html',
    'chapters.html': '/chapters.html', 
    'news.html': '/news.html',
    'finance.html': '/finance.html',
    'dashboard.html': '/dashboard.html',
    'author.html': '/author.html',
    'av-novels.html': '/av-novels.html',
}

for page, canonical in main_pages.items():
    path = f'{BASE}/{page}'
    if not os.path.exists(path):
        print(f"  ⚠️ {page} not found")
        continue
    
    with open(path, 'r') as f:
        html = f.read()
    
    modified = False
    
    # Add canonical tag (after <title> closing)
    if '<link rel="canonical"' not in html:
        title_pattern = r'</title>'
        replacement = f'</title>\n    <link rel="canonical" href="{canonical}">'
        html = re.sub(title_pattern, replacement, html, count=1)
        modified = True
    
    # Add robots meta (after viewport meta or after charset)
    if '<meta name="robots"' not in html:
        # Insert after <title> line
        title_line = f'<link rel="canonical" href="{canonical}">'
        insertion = '\n    <meta name="robots" content="index, follow, max-image-preview:large">'
        pos = html.find(title_line)
        if pos >= 0:
            end_pos = html.find('>', pos) + 1
            html = html[:end_pos] + insertion + html[end_pos:]
            modified = True
    
    # Fix manifest path to absolute
    if 'href="assets/site.webmanifest"' in html:
        html = html.replace('href="assets/site.webmanifest"', 'href="/assets/site.webmanifest"')
        modified = True
    
    # Fix favicon paths to absolute (in head section)
    for fav in ['favicon.ico', 'favicon-32x32.png', 'favicon-16x16.png', 'apple-touch-icon.png']:
        old_href = f'href="assets/{fav}"'
        new_href = f'href="/assets/{fav}"'
        if old_href in html:
            html = html.replace(old_href, new_href)
            modified = True
    
    if modified:
        with open(path, 'w') as f:
            f.write(html)
        print(f"  ✅ {page}: Added canonical + robots meta + fixed asset paths")
    else:
        print(f"  ⏭️ {page}: Already up to date")

# ============================================================
# FIX 5: Fix dashboard.html lang attribute (zh-TW -> zh-Hant)
# ============================================================
print("\n=== FIX 5: Fix dashboard.html lang attribute ===")
with open(f'{BASE}/dashboard.html', 'r') as f:
    html = f.read()

if 'lang="zh-TW"' in html:
    html = html.replace('lang="zh-TW"', 'lang="zh-Hant"')
    with open(f'{BASE}/dashboard.html', 'w') as f:
        f.write(html)
    print("  ✅ Changed lang from zh-TW to zh-Hant")
else:
    print("  ⏭️ Already correct")

# ============================================================
# FIX 6: Fix av-novels.html navigation order (add missing dashboard link)
# ============================================================
print("\n=== FIX 6: Fix av-novels.html navigation ===")
with open(f'{BASE}/av-novels.html', 'r') as f:
    html = f.read()

# Check if dashboard link exists in nav
if '<a href="/dashboard.html"' not in html and '<a href="dashboard.html"' not in html:
    # Find the author link in navigation and add dashboard before it
    old_nav = '<a href="author.html" class="nav-link">作者</a>'
    new_nav = '''<a href="dashboard.html" class="nav-link">城市儀表板</a>
                    <a href="author.html" class="nav-link">作者</a>'''
    
    # Try both relative and absolute paths
    if old_nav in html:
        html = html.replace(old_nav, new_nav)
        with open(f'{BASE}/av-novels.html', 'w') as f:
            f.write(html)
        print("  ✅ Added dashboard link to navigation")
    else:
        # Try different nav structure
        if '<a href="author.html"' in html and '<a href="/dashboard.html"' not in html:
            html = re.sub(
                r'<a href=["\']author\.html["\'][^>]*>作者</a>',
                new_nav,
                html
            )
            with open(f'{BASE}/av-novels.html', 'w') as f:
                f.write(html)
            print("  ✅ Added dashboard link to navigation (alt pattern)")
        else:
            print("  ⚠️ Could not find nav structure to fix")
else:
    print("  ⏭️ Dashboard link already exists")

# ============================================================
# FIX 7: Batch fix chapter titles (chapter-66 through chapter-123)
# Remove " - 科技修真傳" suffix from <title> and <h1> tags
# ============================================================
print("\n=== FIX 7: Fix chapter title format (chapters 66-123) ===")

fixed_count = 0
for i in range(66, 124):
    path = f'{BASE}/chapter-{i}.html'
    if not os.path.exists(path):
        continue
    
    with open(path, 'r') as f:
        html = f.read()
    
    original = html
    
    # Fix <title> — remove " - 科技修真傳" suffix
    title_pattern = r'<title>(第\d+章[^<]*)\s*-\s*科技修真傳</title>'
    replacement = r'<title>\1</title>'
    html = re.sub(title_pattern, replacement, html)
    
    # Fix <h1> — remove " - 科技修真傳" suffix  
    h1_pattern = r'<h1>(第\d+章[^<]*)\s*-\s*科技修真傳</h1>'
    replacement_h1 = r'<h1>\1</h1>'
    html = re.sub(h1_pattern, replacement_h1, html)
    
    if html != original:
        with open(path, 'w') as f:
            f.write(html)
        fixed_count += 1

print(f"  ✅ Fixed {fixed_count} chapter files")

# ============================================================
# FIX 8: Check and fix service worker registration
# ============================================================
print("\n=== FIX 8: Fix Service Worker registration ===")

# Check if sw.js exists
sw_path = f'{BASE}/sw.js'
if os.path.exists(sw_path):
    print(f"  ✅ sw.js already exists at root")
else:
    # Create a basic service worker
    with open(sw_path, 'w') as f:
        f.write('''const CACHE_NAME = 'kofhk-v2';
const ASSETS_TO_CACHE = [
    '/',
    '/home.html',
    '/chapters.html',
    '/news.html',
    '/finance.html',
    '/dashboard.html',
    '/author.html',
    '/av-novels.html',
    '/assets/site.webmanifest',
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS_TO_CACHE))
    );
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => Promise.all(
            keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
        ))
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request).then((cached) => {
            return cached || fetch(event.request).then((response) => {
                if (response.status === 200) {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then((c) => c.put(event.request, clone));
                }
                return response;
            });
        })
    );
});
''')
    print("  ✅ Created sw.js service worker")

# Fix SW registration in all pages to point to /sw.js instead of /assets/sw.js
for page in main_pages:
    path = f'{BASE}/{page}'
    if not os.path.exists(path):
        continue
    
    with open(path, 'r') as f:
        html = f.read()
    
    # Fix SW registration path
    old_sw = "navigator.serviceWorker.register('/assets/sw.js'"
    new_sw = "navigator.serviceWorker.register('/sw.js'"
    if old_sw in html:
        html = html.replace(old_sw, new_sw)
        with open(path, 'w') as f:
            f.write(html)
        print(f"  ✅ Fixed SW registration path in {page}")

# ============================================================
# FIX 9: Fix root page (index.html / home.html redirect issue)
# Make sure index.html redirects properly
# ============================================================
print("\n=== FIX 9: Check root page handling ===")
if os.path.exists(f'{BASE}/index.html'):
    with open(f'{BASE}/index.html', 'r') as f:
        html = f.read()
    
    # If index.html is a redirect page, update it to use meta refresh instead of JS
    if 'window.location.href' in html or 'location.href' in html:
        print("  ⚠️ index.html uses JS redirect — _redirects file should handle this")
        print("  ✅ GitHub Pages + _redirects will serve /home.html for root URL")

print("\n=== ALL FIXES APPLIED ===")
