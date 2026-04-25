#!/usr/bin/env python3
"""批量修復小說修為系統稱謂 v4（使用設定檔12大境界）

正確體系：感氣→聚元→築基→煉魂→凝神→化物→悟天→掌命→破虛→造界→超脫→永恆
保留：九世記憶表境界（元嬰/化神/煉虛/合體/大乘/渡劫/真仙）- 只在前世回憶中使用

需要替換的錯誤詞（不在12大境界也不在九世記憶中）：
- 金丹 → 煉魂（同等級，築基之上第一階）
- 煉氣 → 感氣（入門第一級）
- 凝丹 → 煉魂（能量凝聚/靈魂淬煉）
"""

import os, re, glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(WORKSPACE, "research")

REPLACEMENTS = [
    # 金丹 → 煉魂（各級別變體）
    ('金丹大圓滿', '煉魂大圓滿'),
    ('金丹巔峰', '煉魂巔峰'),
    ('金丹後期', '煉魂後期'),
    ('金丹中期', '煉魂中期'),
    ('金丹初期', '煉魂初期'),
    ('金丹期', '煉魂期'),
    ('金丹境', '煉魂境'),
    # 煉氣 → 感氣
    ('煉氣大圓滿', '感氣大圓滿'),
    ('煉氣巔峰', '感氣巔峰'),
    ('煉氣高層', '感氣高層'),
    ('煉氣中低層', '感氣中低層'),
    ('煉氣十層', '感氣十層'),
    ('煉氣九層', '感氣九層'),
    ('煉氣八層', '感氣八層'),
    ('煉氣七層', '感氣七層'),
    ('煉氣六層', '感氣六層'),
    ('煉氣五層', '感氣五層'),
    ('煉氣四層', '感氣四層'),
    ('煉氣三層', '感氣三層'),
    ('煉氣二層', '感氣二層'),
    ('煉氣一層', '感氣一層'),
    ('煉氣期', '感氣期'),
    ('煉氣境', '感氣境'),
    ('煉氣訣', '感氣訣'),
    # 凝丹 → 煉魂
    ('凝丹大圓滿', '煉魂大圓滿'),
    ('凝丹巔峰', '煉魂巔峰'),
    ('凝丹後期', '煉魂後期'),
    ('凝丹中期', '煉魂中期'),
    ('凝丹初期', '煉魂初期'),
    ('凝丹期', '煉魂期'),
    ('凝丹境', '煉魂境'),
]

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changes = []
    for old, new in REPLACEMENTS:
        count = content.count(old)
        if count > 0:
            content = content.replace(old, new)
            changes.append((old, new, count))
    
    if changes:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return changes
    return None

def main():
    files = sorted(glob.glob(os.path.join(DIR, "chapter-*.md")),
                   key=lambda x: int(re.search(r'chapter-(\d+)', x).group(1)))
    
    print(f"掃描 {len(files)} 個章節...\n")
    
    total_fixed = 0
    total_by_type = {}
    
    for fpath in files:
        filename = os.path.basename(fpath)
        changes = fix_file(fpath)
        if changes:
            total_fixed += 1
            num = re.search(r'chapter-(\d+)', filename).group(1)
            for old, new, count in changes:
                key = f"{old}→{new}"
                total_by_type[key] = total_by_type.get(key, 0) + count
            if len([c for c in changes if c[2] > 0]) <= 2:
                detail = ', '.join(f"{o}→{n}×{c}" for o,n,c in changes)
                print(f"  Ch{num}: {detail}")
    
    print(f"\n=== 統計 ===")
    print(f"修改章節：{total_fixed}/{len(files)}")
    print(f"總修改次數：{sum(total_by_type.values())}")
    for change, count in sorted(total_by_type.items()):
        print(f"  {change}: {count}次")

if __name__ == '__main__':
    main()
