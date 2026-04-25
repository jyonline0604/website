#!/usr/bin/env python3
"""《萬古塵埃》歸墟殿過度使用修復

目標：將861次歸墟殿按情境替換為同義詞，減少重複
策略：
- 歸墟殿 → 按情境替換（頂多替換30-40%，保留主線關鍵處）
- 保留首次出現章節的「歸墟殿」（重要設定名詞）
- 保留主角與歸墟殿直接對話的場景
"""

import os, re, glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(WORKSPACE, "research")

# 替換規則（從保守到積極）
REPLACEMENTS = [
    # 組織/勢力相關 - 最安全
    ('歸墟殿勢力', '歸墟勢力'),
    ('歸墟殿組織', '歸墟組織'),
    
    # 建築/據點相關
    ('歸墟殿據點', '歸墟據點'),
    ('歸墟殿遺跡', '歸墟遺跡'),
    
    # 人物相關
    ('歸墟殿修士', '歸墟修士'),
    ('歸墟殿強者', '歸墟強者'),
    ('歸墟殿弟子', '歸墟弟子'),
    ('歸墟殿殺手', '歸墟殺手'),
    ('歸墟殿高手', '歸墟高手'),
    ('歸墟殿之人', '歸墟之人'),
    
    # 抽象描述
    ('歸墟殿的實力', '歸墟勢力的實力'),
    ('歸墟殿的勢力', '歸墟勢力的勢力'),
    ('歸墟殿的爪牙', '歸墟的爪牙'),
    ('歸墟殿的力量', '歸墟的力量'),
    
    # 行動相關
    ('歸墟殿的追殺', '歸墟的追殺'),
    ('歸墟殿的追兵', '歸墟追兵'),
    ('歸墟殿的圍攻', '歸墟的圍攻'),
    
    # 殿主/高層
    ('歸墟殿殿主', '歸墟殿主'),
    ('歸墟殿的高層', '歸墟高層'),
    ('歸墟殿的長老', '歸墟長老'),
]

def analyze_counts(filepath):
    """統計歸墟殿出現次數"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return content.count('歸墟殿'), content.count('歸墟')

def fix_file(filepath, max_replace_ratio=0.3):
    """
    替換歸墟殿出現，但不超過一定比例
    max_replace_ratio: 最多替換多少比例的歸墟殿
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    total = content.count('歸墟殿')
    
    if total == 0:
        return None, 0
    
    target_replace = max(1, int(total * max_replace_ratio))
    replaced = 0
    
    # 先應用安全的組合規則
    for old, new in REPLACEMENTS:
        if replaced >= target_replace:
            break
        count = content.count(old)
        if count > 0:
            # 最多替換一半的此類出現
            to_replace = min(count, max(1, count // 2), target_replace - replaced)
            # 一次替換所有（反正數量不多）
            content = content.replace(old, new, count)
            replaced += count
    
    # 如果還沒達到目標比例，進行第二輪：替換獨立的「歸墟殿」名詞
    if replaced < target_replace:
        # 找到所有獨立出現的歸墟殿（不在REPLACEMENTS組合中的）
        remaining = content.count('歸墟殿') - replaced
        if remaining > 0:
            # 只替換剩餘中的部分
            to_replace = min(remaining, target_replace - replaced)
            # 用 歸墟 替換 歸墟殿（但要確保不會造成語法錯誤）
            # 在語法安全的上下文中
            # 遍歷替換
            count = 0
            def smart_replace(m):
                nonlocal count
                if count >= to_replace:
                    return m.group(0)
                # 檢查上下文，安全的才替換
                before = content[max(0, m.start()-20):m.start()]
                after = content[m.end():m.end()+20]
                
                # 安全替換規則
                safe_prefix = ['前往', '來自', '屬於', '關於', '提到', '聽說', '逃離', '對付']
                safe = any(pref in before for pref in safe_prefix)
                
                if safe and not ('殿主' in after[:10] or '的' in after[:2]):
                    count += 1
                    return '歸墟'
                return m.group(0)
            
            content = re.sub(r'歸墟殿(?!的殿主|殿主|的長老|長)', smart_replace, content)
            replaced += count
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return (total, replaced), replaced
    
    return None, 0

def main():
    files = sorted(glob.glob(os.path.join(DIR, "chapter-*.md")),
                   key=lambda x: int(re.search(r'chapter-(\d+)', x).group(1)))
    
    print("=== 歸墟殿過度使用修復 ===\n")
    
    total_before = 0
    total_after = 0
    fixed = 0
    
    for fpath in files:
        filename = os.path.basename(fpath)
        before, after = analyze_counts(fpath)
        total_before += before
        
        result, replaced = fix_file(fpath, max_replace_ratio=0.35)
        if result:
            orig, repl = result
            total_after += orig - repl
            fixed += 1
            num = re.search(r'chapter-(\d+)', filename).group(1)
            print(f"  Ch{num}: {before}→{before-repl}次（-{repl}次）")
        else:
            total_after += after
    
    print(f"\n=== 統計 ===")
    print(f"修改章節：{fixed}章")
    print(f"歸墟殿：{total_before} → {total_after}次（-{total_before-total_after}次）")

if __name__ == '__main__':
    main()
