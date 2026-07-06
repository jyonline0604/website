#!/usr/bin/env python3
"""Fix hero background position - move down 5cm"""
import re, subprocess

WORKSPACE = "/home/openclaw/.openclaw/workspace"
fp = f"{WORKSPACE}/home.html"

with open(fp, 'r', encoding='utf-8') as f:
    html = f.read()

# Change center center to center top 5cm
new_html = re.sub(
    r"background:url\('assets/images/hero-bg\.jpg'\) center center/cover no-repeat",
    "background:url('assets/images/hero-bg.jpg') center top 5cm/cover no-repeat",
    html
)

if new_html != html:
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print("✅ background-position 已改為 center top 5cm")
    
    # Also increase padding-top for hero to give more room
    new_html2 = re.sub(
        r"\.hero\{min-height:100vh;padding:80px 32px 60px",
        ".hero{min-height:100vh;padding:120px 32px 60px",
        new_html
    )
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(new_html2)
    print("✅ hero padding-top 由 80px 加到 120px")
else:
    print("⚠️ No match found, checking current state...")
    # Show what the current hero background looks like
    m = re.search(r'\.hero\{.*?\}', html)
    if m:
        print(f"Current hero CSS: {m.group()[:200]}")

# Git
r = subprocess.run(['git', '-C', WORKSPACE, 'add', 'home.html'])
r = subprocess.run(['git', '-C', WORKSPACE, 'commit', '-m', 'fix: 背景圖向下移5cm + 增加hero padding'], capture_output=True, text=True)
if r.returncode == 0:
    print(f"✅ Committed: {r.stdout[:100]}")
else:
    print(f"⚠️ Commit: {r.stderr[:200]}")

r = subprocess.run(['git', '-C', WORKSPACE, 'push'], capture_output=True, text=True)
print(f"Push: {r.stdout[:200] if r.returncode == 0 else r.stderr[:200]}")
