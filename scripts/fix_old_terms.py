#!/usr/bin/env python3
"""批量修正主線中嘅舊系統術語（元嬰→凝神、化神→化物、煉虛→悟天等）"""
import re, os

OLD_TERMS = {
    '金丹': '煉魂', '金丹期': '煉魂期', '金丹境': '煉魂境', '金丹修士': '煉魂修士',
    '元嬰期': '凝神期', '元嬰境': '凝神期', '元嬰': '凝神',
    '元嬰初期': '凝神初期', '元嬰中期': '凝神中期', '元嬰後期': '凝神後期', '元嬰巔峰': '凝神巔峰', '元嬰圓滿': '凝神圓滿',
    '化神期': '化物期', '化神境': '化物期', '化神': '化物',
    '化神初期': '化物初期', '化神中期': '化物中期', '化神後期': '化物後期', '化神巔峰': '化物巔峰', '化神圓滿': '化物圓滿',
    '煉虛期': '悟天期', '煉虛境': '悟天期', '煉虛': '悟天',
    '煉虛初期': '悟天初期', '煉虛中期': '悟天中期', '煉虛後期': '悟天後期', '煉虛巔峰': '悟天巔峰',
    '合體期': '掌命期', '合體境': '掌命期', '合體': '掌命',
    '大乘期': '破虛期', '大乘境': '破虛期', '大乘': '破虛',
    '渡劫期': '造界期', '渡劫境': '造界期', '渡劫丹': '造界丹', '渡劫': '造界',
    '真仙期': '超脫期', '真仙境': '超脫期', '真仙': '超脫',
}

# 按長度排序（長匹配優先）
SORTED_TERMS = sorted(OLD_TERMS.keys(), key=len, reverse=True)

# 記憶場景關鍵詞（這些場景中的舊系統術語是正確的）
MEMORY_CONTEXT = {
    '九世', '記憶', '前世', '前生', '上一世', '第一世', '第二世', '第三世', '第四世', '第五世', 
    '第六世', '第七世', '第八世', '第九世', '輪迴記憶', '回憶', '記得當年', '曾為', '曾經是',
    '那一世', '他前世', '回想起', '想起來', '記憶碎片', '輪迴傳承',
    '陣皇記憶', '丹尊記憶', '劍帝記憶', '戰神記憶', '魔主記憶', '聖僧記憶',
    '他的第八世', '他的前世', '曾是一', '那一世，他',
}

def is_flashback_context(text, pos, window=300):
    """判斷某個位置是否在記憶/回憶場景中"""
    start = max(0, pos - window)
    end = min(len(text), pos + window)
    ctx = text[start:end]
    for kw in MEMORY_CONTEXT:
        if kw in ctx:
            # Extra check - make sure the context is about a past life, not current
            if '他曾' in ctx or '曾經' in ctx or '前世' in ctx or '記憶中' in ctx:
                return True
            return True
    return False

def fix_chapter(filepath):
    """修正一個章節檔案中的舊系統術語"""
    with open(filepath, 'r') as f:
        text = f.read()
    
    original = text
    total_replaced = 0
    replacements = []
    
    for term in SORTED_TERMS:
        correct = OLD_TERMS[term]
        # Match whole words only (not partial matches like 化神 in 化神宗)
        pattern = re.compile(r'(?<!\w)' + re.escape(term) + r'(?!\w)')
        
        for m in pattern.finditer(text):
            if is_flashback_context(text, m.start()):
                continue  # Skip flashback contexts
            replacements.append((m.start(), m.end(), term, correct))
            total_replaced += 1
    
    # Apply replacements in reverse order (preserving positions)
    replacements.sort(key=lambda x: x[0], reverse=True)
    for start, end, old, new in replacements:
        text = text[:start] + new + text[end:]
    
    if text != original:
        with open(filepath, 'w') as f:
            f.write(text)
        return total_replaced
    return 0

def main():
    total = 0
    fixed_chapters = 0
    
    for i in range(1, 201):
        path = f'research/chapter-{i}.md'
        if not os.path.exists(path):
            continue
        
        n = fix_chapter(path)
        if n > 0:
            print(f"Ch{i:>3}: 修正{n:>3}處")
            total += n
            fixed_chapters += 1
    
    print(f"\n=== 完成 ===")
    print(f"影響章節：{fixed_chapters}章")
    print(f"總修正次數：{total}")

if __name__ == '__main__':
    main()
