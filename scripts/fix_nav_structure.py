#!/usr/bin/env python3
"""
修復底部導航欄的HTML結構 - 完整版
"""

import os
import re
import glob

NOVEL_DIR = "/home/openclaw/.openclaw/workspace/my-novel"

def fix_nav_structure(filepath):
    """修復單個文件的底部導航"""
    print(f"處理: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 檢查是否有正確的 nav 結構
    has_nav_open = '<nav class="bottom-nav">' in content
    has_nav_close = '</nav>' in content
    
    if has_nav_open and content.count('</nav>') == 1:
        print(f"  ✅ nav結構正確")
        return True
    
    # 找到 <!-- Bottom Navigation --> 的位置
    marker = '<!-- Bottom Navigation -->'
    marker_pos = content.find(marker)
    if marker_pos == -1:
        print(f"  ⚠️ 找不到 Bottom Navigation 標記")
        return False
    
    marker_end = marker_pos + len(marker)
    
    # 檢查下一個字符
    next_char = content[marker_end] if marker_end < len(content) else '\n'
    
    # 如果 <!-- Bottom Navigation --> 後面直接是 <span 或 <a 或 <nav，則已經有 opening tag
    if next_char.strip().startswith('<nav'):
        print(f"  ✅ 已有opening tag")
        return True
    
    # 如果後面是 <span 或 <a，則需要插入 <nav class="bottom-nav">
    if next_char in ('\n', ' ', '<'):
        # 在 <!-- Bottom Navigation --> 和下一個標籤之間插入 <nav class="bottom-nav">
        content = content[:marker_end] + '\n    <nav class="bottom-nav">' + content[marker_end:]
        print(f"  🔧 添加了 opening tag")
    
    # 現在檢查是否有正確的 closing tag
    # 應該只有一個 </nav> 在 bottom-nav 區域
    # 找到 bottom-nav 區域的結尾（Settings Modal 之前）
    settings_marker = '<!-- Settings Modal -->'
    settings_pos = content.find(settings_marker)
    
    if settings_pos != -1:
        # 找到 bottom-nav 最後一個 </nav> 的位置
        nav_close = content.rfind('</nav>', marker_pos, settings_pos)
        if nav_close != -1:
            # 確保只有一個 </nav>
            # 如果有多個 </nav>，刪除多餘的
            all_nav_closes = [m.start() for m in re.finditer('</nav>', content)]
            if len(all_nav_closes) > 1:
                # 找到倒數第二個 </nav> 的位置
                second_last = all_nav_closes[-2]
                # 刪除倒數第二個之後的所有 </nav>，然後只保留一個
                content = content[:second_last] + '</nav>' + content[all_nav_closes[-1]+6:]
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ 已修復")
        return True
    else:
        print(f"  ⚠️ 無法修復")
        return False

def main():
    print("=" * 60)
    print("修復底部導航欄結構 - 完整版")
    print("=" * 60)
    
    # 獲取所有章節文件
    all_files = glob.glob(os.path.join(NOVEL_DIR, "chapter-*.html"))
    chapter_files = []
    for f in all_files:
        if 'chapter-template' not in f:
            match = re.search(r'chapter-(\d+)', f)
            if match:
                chapter_files.append((int(match.group(1)), f))
    
    chapter_files.sort(key=lambda x: x[0])
    chapter_files = [f[1] for f in chapter_files]
    
    print(f"找到 {len(chapter_files)} 個章節文件\n")
    
    success = 0
    for filepath in chapter_files:
        if fix_nav_structure(filepath):
            success += 1
    
    print("\n" + "=" * 60)
    print(f"完成！成功修復 {success}/{len(chapter_files)} 個文件")
    print("=" * 60)

if __name__ == "__main__":
    main()
