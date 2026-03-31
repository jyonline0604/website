#!/usr/bin/env python3
"""
修復第69章文件
"""

import os
import re

novel_dir = "/home/openclaw/.openclaw/workspace"
chapter_file = os.path.join(novel_dir, "chapter-69.html")
backup_file = chapter_file + ".backup"

print(f"=== 修復第69章: {chapter_file} ===")

# 備份原文件
if os.path.exists(chapter_file):
    import shutil
    shutil.copy2(chapter_file, backup_file)
    print(f"✅ 已備份原文件到: {backup_file}")

# 讀取文件內容
with open(chapter_file, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"原文件長度: {len(content)} 字符")

# 檢查並修復常見問題
fixed_content = content

# 1. 確保只有一個<!DOCTYPE>
doctype_pattern = r'<!DOCTYPE[^>]*>'
doctypes = re.findall(doctype_pattern, fixed_content)
if len(doctypes) > 1:
    print(f"⚠️  發現 {len(doctypes)} 個<!DOCTYPE>，保留第一個")
    # 保留第一個，移除其他
    first_doctype = doctypes[0]
    fixed_content = re.sub(doctype_pattern, '', fixed_content)
    fixed_content = first_doctype + '\n' + fixed_content

# 2. 確保只有一個<html>開始標籤
html_start_pattern = r'<html[^>]*>'
html_starts = re.findall(html_start_pattern, fixed_content)
if len(html_starts) > 1:
    print(f"⚠️  發現 {len(html_starts)} 個<html>開始標籤，保留第一個")
    first_html = html_starts[0]
    fixed_content = re.sub(html_start_pattern, '', fixed_content)
    fixed_content = first_html + '\n' + fixed_content

# 3. 確保只有一個</html>結束標籤
html_end_pattern = r'</html>'
html_ends = re.findall(html_end_pattern, fixed_content)
if len(html_ends) > 1:
    print(f"⚠️  發現 {len(html_ends)} 個</html>結束標籤，保留最後一個")
    # 移除所有，然後在最後添加一個
    fixed_content = re.sub(html_end_pattern, '', fixed_content)
    fixed_content = fixed_content + '\n</html>'

# 4. 確保有完整的<head>和<body>結構
if '<head>' not in fixed_content:
    print("⚠️  缺少<head>標籤，添加中...")
    # 在<html>後添加<head>
    fixed_content = fixed_content.replace('<html lang="zh-Hant">', 
                                         '<html lang="zh-Hant">\n<head>')
    # 在適當位置添加</head>和<body>
    if '<body>' in fixed_content:
        # 在<body>前添加</head>
        fixed_content = fixed_content.replace('<body>', '</head>\n<body>')
    else:
        # 添加完整的head和body結構
        fixed_content = fixed_content.replace('</html>', '</head>\n<body>\n</body>\n</html>')

# 5. 確保有標題
if '<title>' not in fixed_content:
    print("⚠️  缺少<title>標籤，添加中...")
    # 在<head>中添加標題
    if '<head>' in fixed_content:
        head_end = fixed_content.find('</head>')
        if head_end == -1:
            head_end = fixed_content.find('<body>')
        if head_end != -1:
            title = '<title>第69章：能量風暴 - 科技修真傳</title>'
            fixed_content = fixed_content[:head_end] + title + '\n' + fixed_content[head_end:]

# 6. 確保有章節標題<h1>
if '<h1' not in fixed_content:
    print("⚠️  缺少<h1>章節標題，添加中...")
    # 在<body>中添加章節標題
    if '<body>' in fixed_content:
        body_start = fixed_content.find('<body>') + 6
        h1_title = '<h1>第69章：能量風暴</h1>'
        fixed_content = fixed_content[:body_start] + '\n' + h1_title + '\n' + fixed_content[body_start:]

# 寫入修復後的文件
with open(chapter_file, 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print(f"修復後文件長度: {len(fixed_content)} 字符")

# 驗證修復
print("\n=== 修復驗證 ===")

# 檢查基本結構
doctype_count = fixed_content.count('<!DOCTYPE')
html_start_count = fixed_content.count('<html')
html_end_count = fixed_content.count('</html>')
head_count = fixed_content.count('<head>')
body_count = fixed_content.count('<body>')
title_count = fixed_content.count('<title>')
h1_count = fixed_content.count('<h1')

print(f"<!DOCTYPE>: {doctype_count}")
print(f"<html>: {html_start_count}")
print(f"</html>: {html_end_count}")
print(f"<head>: {head_count}")
print(f"<body>: {body_count}")
print(f"<title>: {title_count}")
print(f"<h1>: {h1_count}")

if (doctype_count == 1 and html_start_count == 1 and html_end_count == 1 and
    head_count >= 1 and body_count >= 1 and title_count >= 1 and h1_count >= 1):
    print("✅ 文件結構修復完成")
else:
    print("⚠️  文件結構可能仍有問題")

print(f"\n原文件已備份到: {backup_file}")
print("如需恢復原文件，請執行:")
print(f"  cp {backup_file} {chapter_file}")