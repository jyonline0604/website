#!/usr/bin/env python3
"""
統一更新所有頁面的章節數量
用法：python3 update_chapter_counts.py
"""
import os
import re
import json

workspace = "/home/openclaw/.openclaw/workspace"
os.chdir(workspace)

def count_chapter_files():
    """計算實際的章節文件數量"""
    count = 0
    for f in os.listdir('.'):
        if f.startswith('chapter-') and f.endswith('.html'):
            if '-av' not in f and 'template' not in f:
                count += 1
    return count

def update_author_html(count):
    """更新 author.html 的章節數量"""
    filename = 'author.html'
    if not os.path.exists(filename):
        print(f"⚠️ {filename} 不存在")
        return False
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找並更新章節數量
    # 匹配：<span id="chapterCount">129</span> 或直接的數字
    pattern1 = r'<span id="chapterCount">\d+</span>'
    replacement1 = f'<span id="chapterCount">{count}</span>'
    
    if re.search(pattern1, content):
        content = re.sub(pattern1, replacement1, content)
    else:
        # 嘗試匹配「目前已有 X 章」
        pattern2 = r'目前已有\s*\d+\s*章'
        replacement2 = f'目前已有 <span id="chapterCount">{count}</span> 章'
        content = re.sub(pattern2, replacement2, content)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def update_chapters_data_json(count):
    """更新 chapters-data.json 文件"""
    json_file = 'assets/chapters-data.json'
    if not os.path.exists(json_file):
        print(f"⚠️ {json_file} 不存在")
        return False
    
    # 讀取現有數據
    with open(json_file, 'r', encoding='utf-8') as f:
        chapters = json.load(f)
    
    current_count = len(chapters)
    
    if current_count >= count:
        print(f"  chapters-data.json 已有 {current_count} 個章節，無需更新")
        return True
    
    # 需要添加新章節
    # 從 HTML 文件獲取章節標題
    for ch_num in range(current_count + 1, count + 1):
        chapter_file = f'chapter-{ch_num}.html'
        if os.path.exists(chapter_file):
            with open(chapter_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取標題
            title_match = re.search(r'<title>第\d+章：(.+?) -', content)
            if title_match:
                title = title_match.group(1)
            else:
                title = f"第{ch_num}章"
            
            chapters.append({
                "number": ch_num,
                "title": f"第{ch_num}章 {title} - 科技修真傳 →",
                "url": f"chapter-{ch_num}.html"
            })
            print(f"  添加第{ch_num}章: {title}")
    
    # 寫入更新後的數據
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(chapters, f, ensure_ascii=False, indent=2)
    
    return True

def update_home_html(count):
    """更新 home.html 的章節數量（如果有）"""
    filename = 'home.html'
    if not os.path.exists(filename):
        return False
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找「共 X 章」或類似的模式
    pattern = r'共\s*\d+\s*章'
    if re.search(pattern, content):
        content = re.sub(pattern, f'共 {count} 章', content)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def verify_updates():
    """驗證更新結果"""
    print("\n" + "=" * 50)
    print("驗證更新結果:")
    print("=" * 50)
    
    # 檢查 author.html
    with open('author.html', 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r'chapterCount">(\d+)</span>', content)
    if match:
        print(f"✅ author.html: {match.group(1)} 章")
    
    # 檢查 chapters-data.json
    with open('assets/chapters-data.json', 'r', encoding='utf-8') as f:
        chapters = json.load(f)
    print(f"✅ chapters-data.json: {len(chapters)} 章")

# 主程序
print("=" * 60)
print("統一更新章節數量")
print("=" * 60)

# 計算實際章節數量
actual_count = count_chapter_files()
print(f"\n📊 實際章節文件數量: {actual_count}")

# 更新各個文件
print("\n📝 更新文件:")

print("1. author.html...")
if update_author_html(actual_count):
    print("   ✅ 已更新")
else:
    print("   ❌ 更新失敗")

print("2. chapters-data.json...")
update_chapters_data_json(actual_count)

print("3. home.html...")
if update_home_html(actual_count):
    print("   ✅ 已更新")
else:
    print("   ⏭️ 無需更新")

# 驗證
verify_updates()

print("\n" + "=" * 60)
print("✅ 更新完成！")
print("=" * 60)
