#!/usr/bin/env python3
"""
修復底部導航欄的HTML結構
"""

import os
import re
import glob

NOVEL_DIR = "/home/openclaw/.openclaw/workspace/my-novel"

def fix_bottom_nav(filepath):
    """修復單個文件的底部導航"""
    print(f"處理: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 檢查是否有正確的 nav 結構
    if '<nav class="bottom-nav">' in content:
        print(f"  ✅ nav結構正確")
        return True
    
    # 修補 nav 結構
    # 找到 </main> 後的內容，應該包含底部導航
    main_end = content.find('</main>')
    if main_end == -1:
        print(f"  ⚠️ 找不到 </main>")
        return False
    
    # 找到 <!-- Bottom Navigation -->
    nav_marker = content.find('<!-- Bottom Navigation -->', main_end)
    if nav_marker == -1:
        print(f"  ⚠️ 找不到 Bottom Navigation 標記")
        return False
    
    # 在 <!-- Bottom Navigation --> 後面插入 <nav class="bottom-nav">
    content = content.replace(
        '<!-- Bottom Navigation -->\n    <a href="chapter-',
        '<!-- Bottom Navigation -->\n    <nav class="bottom-nav">\n        <a href="chapter-'
    )
    
    # 在 </nav> 前面確保有換行
    # 找到最後的 </nav> 並確保它是關閉正確的 nav
    # 我們需要找到有下一章 span 的 </nav>
    
    # 修補：確保有 </nav> 結尾
    # 查找 "下一章 →</span>" 後面的 </nav>
    content = content.replace(
        '<span style="opacity:0.3; padding:10px 16px; display:inline-block;">下一章 →</span>\n    </nav>',
        '<span style="opacity:0.3; padding:10px 16px; display:inline-block;">下一章 →</span>\n    </nav>\n</nav>'
    )
    
    # 另一種可能：下一章 span 在同一行
    content = content.replace(
        '<span style="opacity:0.3; padding:10px 16px; display:inline-block;">下一章 →</span></nav>',
        '<span style="opacity:0.3; padding:10px 16px; display:inline-block;">下一章 →</span>\n    </nav>'
    )
    
    # 查找並修復：確保有多個 </nav> 的問題
    # 如果有多餘的 </nav>，只保留一個
    
    # 重新查找並修復結構
    # 找 "下一章 →</span>" 後面緊跟的 </nav>
    pattern = r'(<span style="opacity:0\.3; padding:10px 16px; display:inline-block;">下一章 →</span>\s*)</nav>(\s*</nav>)'
    content = re.sub(pattern, r'\1</nav>', content)
    
    # 確保有開始的 <nav>
    if '<nav class="bottom-nav">' not in content:
        content = content.replace(
            '<!-- Bottom Navigation -->\n    <a href="chapter-',
            '<!-- Bottom Navigation -->\n    <nav class="bottom-nav">\n        <a href="chapter-'
        )
    
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
    print("修復底部導航欄結構")
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
        if fix_bottom_nav(filepath):
            success += 1
    
    print("\n" + "=" * 60)
    print(f"完成！成功修復 {success}/{len(chapter_files)} 個文件")
    print("=" * 60)

if __name__ == "__main__":
    main()
