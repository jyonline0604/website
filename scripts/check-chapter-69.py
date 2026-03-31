#!/usr/bin/env python3
"""
檢查第69章文件問題
"""

import os
import re

novel_dir = "/home/openclaw/.openclaw/workspace"
chapter_file = os.path.join(novel_dir, "chapter-69.html")

print(f"=== 檢查第69章: {chapter_file} ===")

# 檢查文件是否存在
if not os.path.exists(chapter_file):
    print("❌ 文件不存在")
    exit(1)

print(f"✅ 文件存在，大小: {os.path.getsize(chapter_file)} 字節")

# 讀取文件內容
with open(chapter_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 檢查基本HTML結構
print("\n=== HTML結構檢查 ===")

# 檢查DOCTYPE
doctype_count = content.count('<!DOCTYPE')
print(f"<!DOCTYPE> 數量: {doctype_count}")

# 檢查<html>開始標籤
html_start_count = content.count('<html')
print(f"<html> 開始標籤數量: {html_start_count}")

# 檢查</html>結束標籤  
html_end_count = content.count('</html>')
print(f"</html> 結束標籤數量: {html_end_count}")

# 檢查標題
title_match = re.search(r'<title>(.*?)</title>', content)
if title_match:
    print(f"標題: {title_match.group(1)}")
else:
    print("❌ 未找到標題")

# 檢查章節標題
h1_count = content.count('<h1')
print(f"<h1> 標籤數量: {h1_count}")

# 檢查是否有明顯的HTML錯誤
if '<html><html>' in content:
    print("❌ 發現重複的<html>標籤")
elif '</html></html>' in content:
    print("❌ 發現重複的</html>標籤")
else:
    print("✅ 無明顯HTML結構錯誤")

# 檢查文件開頭和結尾
print("\n=== 文件開頭 (前10行) ===")
with open(chapter_file, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i < 10:
            print(f"{i+1}: {line.rstrip()}")
        else:
            break

print("\n=== 文件結尾 (最後10行) ===")
with open(chapter_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines[-10:]):
        print(f"{len(lines)-9+i}: {line.rstrip()}")

# 檢查home.html中的鏈接
home_file = os.path.join(novel_dir, "home.html")
if os.path.exists(home_file):
    print("\n=== 檢查home.html中的鏈接 ===")
    with open(home_file, 'r', encoding='utf-8') as f:
        home_content = f.read()
    
    # 查找第69章鏈接
    chapter_69_pattern = r'<a href="chapter-69\.html".*?>.*?第69章.*?</a>'
    matches = re.findall(chapter_69_pattern, home_content, re.DOTALL)
    
    if matches:
        print(f"✅ 在home.html中找到第69章鏈接")
        # 簡化顯示鏈接
        for match in matches[:1]:
            simplified = re.sub(r'\s+', ' ', match)
            print(f"   鏈接: {simplified[:100]}...")
    else:
        print("❌ 在home.html中未找到第69章鏈接")

print("\n=== 檢查完成 ===")