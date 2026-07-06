#!/bin/bash
WORKSPACE="/home/openclaw/.openclaw/workspace"
cd "$WORKSPACE"

# Find the hero CSS and change background-position
python3 -c "
import re
with open('home.html','r',encoding='utf-8') as f:
    html = f.read()

# Change .hero background-position from center center to center top 5cm
old = \".hero{min-height:100vh;padding:80px 32px 60px;text-align:center;background:url('assets/images/hero-bg.jpg') center center/cover no-repeat;\"
new = \".hero{min-height:100vh;padding:80px 32px 60px;text-align:center;background:url('assets/images/hero-bg.jpg') center top 5cm/cover no-repeat;\"

if old in html:
    html = html.replace(old, new)
    with open('home.html','w',encoding='utf-8') as f:
        f.write(html)
    print('✅ 背景圖已向下移 5cm')
else:
    print('⚠️ 未找到 match，嘗試用 regex...')
    # Try regex
    html2 = re.sub(
        r\"background:url\('assets/images/hero-bg\.jpg'\) center center/cover no-repeat\",
        \"background:url('assets/images/hero-bg.jpg') center top 5cm/cover no-repeat\",
        html
    )
    if html2 != html:
        with open('home.html','w',encoding='utf-8') as f:
            f.write(html2)
        print('✅ regex 方式完成')
    else:
        print('❌ 完全搵唔到')

# Git commit
import subprocess
subprocess.run(['git','add','home.html'], cwd='.')
subprocess.run(['git','commit','-m','fix: 登陸頁背景圖向下移5cm'], cwd='.')
subprocess.run(['git','push'], cwd='.')
" > output.txt 2>&1
cat output.txt
