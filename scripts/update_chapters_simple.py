#!/usr/bin/env python3
"""
更新章節目錄 v2 (2026-07-11)
- 只更新 meta description 中的章節數量（章節列表由 JS 動態渲染）
- 不再生成靜態 chapter items 和 group buttons
"""

import os
import sys
import re
from datetime import datetime

WORKSPACE = "/home/openclaw/.openclaw/workspace"

def count_chapters():
    """計算章節總數"""
    count = 0
    max_num = 0
    for filename in os.listdir(WORKSPACE):
        m = re.match(r"chapter-(\d+)\.html", filename)
        if m:
            count += 1
            num = int(m.group(1))
            if num > max_num:
                max_num = num
    return count, max_num

def update_chapters_html():
    """更新 meta description 中的章節數量"""
    chapters_path = os.path.join(WORKSPACE, "chapters.html")

    with open(chapters_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    count, max_num = count_chapters()
    if count == 0:
        print("❌ 沒有找到章節文件")
        return False

    print(f"找到 {count} 個章節 (最新: 第{max_num}章)")

    # Update meta description
    new_desc = f'<meta name="description" content="《萬古塵埃》章節列表 - 完整收錄{count}章免費閱讀，修仙愛好者首選平台，葉塵九世輪迴修仙之旅。">'
    old_desc_pattern = r'<meta name="description" content="[^"]*">'
    new_content = re.sub(old_desc_pattern, new_desc, content)

    # Update OG description
    new_og = f'<meta property="og:description" content="《萬古塵埃》章節目錄 - 完整收錄{count}章，支持分卷瀏覽、搜尋和排序功能。">'
    old_og_pattern = r'<meta property="og:description" content="[^"]*">'
    new_content = re.sub(old_og_pattern, new_og, new_content)

    # Update Twitter description  
    new_tw = f'<meta name="twitter:description" content="《萬古塵埃》章節目錄 - 完整收錄{count}章，支持分卷瀏覽、搜尋和排序功能。">'
    old_tw_pattern = r'<meta name="twitter:description" content="[^"]*">'
    new_content = re.sub(old_tw_pattern, new_tw, new_content)

    with open(chapters_path, 'w', encoding='utf-8-sig') as f:
        f.write(new_content)

    print(f"✅ 已更新 meta 描述: {count} 章")
    return True

def main():
    print("=== 更新章節目錄 v2 ===")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    success = update_chapters_html()

    if success:
        print("✅ 章節目錄更新完成")
        return 0
    else:
        print("❌ 章節目錄更新失敗")
        return 1

if __name__ == "__main__":
    sys.exit(main())
