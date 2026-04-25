#!/usr/bin/env python3
"""歸墟殿第二輪修復 - 更積極的策略"""

import os, re, glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(WORKSPACE, "research")

# 第二輪：替換更高頻的組合詞
REPLACEMENTS_V2 = [
    # 歸墟殿 → 歸墟（在組織/勢力/人稱前省略「殿」字）
    ('歸墟殿的', '歸墟的'),
    ('歸墟殿在', '歸墟在'),
    ('歸墟殿已經', '歸墟已經'),
    ('歸墟殿就', '歸墟就'),
    ('歸墟殿也', '歸墟也'),
    ('歸墟殿還', '歸墟還'),
    ('歸墟殿是', '歸墟是'),
    ('歸墟殿有', '歸墟有'),
    ('歸墟殿的實', '歸墟的實'),
    ('歸墟殿的目', '歸墟的目'),
    ('歸墟殿的陰', '歸墟的陰'),
    ('歸墟殿的計', '歸墟的計'),
    ('歸墟殿的計', '歸墟的計'),
    ('歸墟殿的力', '歸墟的力'),
    ('歸墟殿的強', '歸墟的強'),
    ('歸墟殿的秘', '歸墟的秘'),
    ('歸墟殿的消', '歸墟的消'),
    ('歸墟殿的勢', '歸墟的勢'),
    ('歸墟殿的追', '歸墟的追'),
    ('歸墟殿的計', '歸墟的計'),
    ('歸墟殿所', '歸墟所'),
    ('歸墟殿內', '歸墟之內'),
    ('歸墟殿之', '歸墟之'),
    ('歸墟殿中', '歸墟之中'),
    ('歸墟殿裡', '歸墟之中'),
    # 歸墟殿即  → 歸墟即 
    ('歸墟殿即', '歸墟即'),
    ('歸墟殿的殺', '歸墟的殺'),
    ('歸墟殿的弟', '歸墟的弟'),
    ('歸墟殿的長', '歸墟的長'),
    ('歸墟殿的核', '歸墟的核'),
    ('歸墟殿的隱', '歸墟的隱'),
]

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    before = content.count('歸墟殿')
    
    if before == 0:
        return None
    
    # 應用第二輪替換
    for old, new in REPLACEMENTS_V2:
        content = content.replace(old, new)
    
    after = content.count('歸墟殿')
    reduced = before - after
    
    if reduced > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return (before, after, reduced)
    
    return None

def main():
    files = sorted(glob.glob(os.path.join(DIR, "chapter-*.md")),
                   key=lambda x: int(re.search(r'chapter-(\d+)', x).group(1)))
    
    total_before = 0
    total_after = 0
    fixed = 0
    
    print("=== 歸墟殿第二輪修復 ===\n")
    
    for fpath in files:
        result = fix_file(fpath)
        if result:
            before, after, reduced = result
            total_before += before
            total_after += after
            fixed += 1
            num = re.search(r'chapter-(\d+)', os.path.basename(fpath)).group(1)
            print(f"  Ch{num}: {before}→{after}次（-{reduced}）")
        else:
            # just count
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            total_before += content.count('歸墟殿')
            total_after += content.count('歸墟殿')
    
    total_reduced = total_before - total_after
    print(f"\n=== 統計 ===")
    print(f"修改章節：{fixed}章")
    print(f"歸墟殿：{total_before}→{total_after}次（-{total_reduced}次）")

if __name__ == '__main__':
    main()
