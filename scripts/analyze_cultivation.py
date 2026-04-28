#!/usr/bin/env python3
"""掃描所有章節，建立修為境界追蹤表"""
import re, os, json

# 正統12級系統 (最終方案 v2)
# 大境界（共12個）
# 感氣 → 聚元 → 築基 → 煉魂 → 凝神 → 化物 → 悟天 → 掌命 → 破虛 → 造界 → 超脫 → 永恆
LEVELS_12 = {
    '感氣': 1, '感氣期': 1, '感氣境': 1, '感氣前期': 1, '感氣中期': 1, '感氣後期': 1, '感氣圓滿': 1,
    '聚元': 2, '聚元期': 2, '聚元境': 2, '聚元圓滿': 2, '聚元前期': 2, '聚元中期': 2, '聚元後期': 2, '聚元前期巔峰': 2, '聚元中期巔峰': 2, '聚元後期巔峰': 2, '聚元半步': 2,
    '築基': 3, '築基期': 3, '築基境': 3, '築基圓滿': 3, '築基前期': 3, '築基中期': 3, '築基後期': 3, '築基前期巔峰': 3, '築基中期巔峰': 3, '築基後期巔峰': 3, '築基半步': 3, '築基巔峰': 3,
    '煉魂': 4, '煉魂期': 4, '煉魂境': 4, '煉魂圓滿': 4, '煉魂前期': 4, '煉魂中期': 4, '煉魂後期': 4, '煉魂前期巔峰': 4, '煉魂中期巔峰': 4, '煉魂後期巔峰': 4, '煉魂半步': 4, '煉魂巔峰': 4,
    '凝神': 5, '凝神期': 5, '凝神境': 5, '凝神圓滿': 5, '凝神前期': 5, '凝神中期': 5, '凝神後期': 5, '凝神前期巔峰': 5, '凝神中期巔峰': 5, '凝神後期巔峰': 5, '凝神半步': 5, '凝神巔峰': 5,
    '化物': 6, '化物期': 6, '化物境': 6, '化物圓滿': 6, '化物前期': 6, '化物中期': 6, '化物後期': 6, '化物前期巔峰': 6, '化物中期巔峰': 6, '化物後期巔峰': 6, '化物半步': 6, '化物巔峰': 6,
    '悟天': 7, '悟天期': 7, '悟天境': 7, '悟天圓滿': 7, '悟天前期': 7, '悟天中期': 7, '悟天後期': 7, '悟天前期巔峰': 7, '悟天中期巔峰': 7, '悟天後期巔峰': 7, '悟天半步': 7, '悟天巔峰': 7,
    '掌命': 8, '掌命期': 8, '掌命境': 8, '掌命圓滿': 8, '掌命前期': 8, '掌命中期': 8, '掌命後期': 8, '掌命前期巔峰': 8, '掌命中期巔峰': 8, '掌命後期巔峰': 8, '掌命半步': 8, '掌命巔峰': 8,
    '破虛': 9, '破虛期': 9, '破虛境': 9, '破虛圓滿': 9, '破虛前期': 9, '破虛中期': 9, '破虛後期': 9, '破虛前期巔峰': 9, '破虛中期巔峰': 9, '破虛後期巔峰': 9, '破虛半步': 9, '破虛巔峰': 9,
    '造界': 10, '造界期': 10, '造界境': 10, '造界圓滿': 10, '造界前期': 10, '造界中期': 10, '造界後期': 10, '造界前期巔峰': 10, '造界中期巔峰': 10, '造界後期巔峰': 10, '造界半步': 10, '造界巔峰': 10,
    '超脫': 11, '超脫期': 11, '超脫境': 11, '超脫圓滿': 11, '超脫前期': 11, '超脫中期': 11, '超脫後期': 11, '超脫前期巔峰': 11, '超脫中期巔峰': 11, '超脫後期巔峰': 11, '超脫半步': 11, '超脫巔峰': 11,
    '永恆': 12, '永恆期': 12, '永恆境': 12, '永恆圓滿': 12, '永恆前期': 12, '永恆中期': 12, '永恆後期': 12, '永恆前期巔峰': 12, '永恆中期巔峰': 12, '永恆後期巔峰': 12, '永恆半步': 12, '永恆巔峰': 12,
}

# 小境界8階段（統一套式）
# 1:前期 2:前期巔峰 3:中期 4:中期巔峰 5:後期 6:後期巔峰 7:半步（巔）8:圓滿→突破
MINOR_STAGES = ['前期', '前期巔峰', '中期', '中期巔峰', '後期', '後期巔峰', '半步（巔）', '圓滿']

# 舊系統（九世記憶專用，生成時被錯誤用在主線）
OLD_TERMS = {
    '金丹': (4, '舊_金丹'), '金丹期': (4, '舊_金丹'), '金丹境': (4, '舊_金丹'),
    '元嬰': (5, '舊_元嬰'), '元嬰期': (5, '舊_元嬰'), '元嬰境': (5, '舊_元嬰'),
    '化神': (6, '舊_化神'), '化神期': (6, '舊_化神'), '化神境': (6, '舊_化神'),
    '煉虛': (7, '舊_煉虛'), '煉虛期': (7, '舊_煉虛'), '煉虛境': (7, '舊_煉虛'),
    '合體': (8, '舊_合體'), '合體期': (8, '舊_合體'), '合體境': (8, '舊_合體'),
    '大乘': (9, '舊_大乘'), '大乘期': (9, '舊_大乘'),
    '渡劫': (10, '舊_渡劫'), '渡劫期': (10, '舊_渡劫'),
}

ALL_TERMS = {**LEVELS_12, **OLD_TERMS}
TERM_NAMES = sorted(ALL_TERMS.keys(), key=len, reverse=True)  # longest first for regex

level_names_l12 = ['感氣','聚元','築基','煉魂','凝神','化物','悟天','掌命','破虛','造界','超脫','永恆']
level_names_old = ['金丹','元嬰','化神','煉虛','合體','大乘','渡劫','真仙']

def extract_levels(text, chapter_num):
    """找出章節中所有修為提及"""
    found = []
    for term in TERM_NAMES:
        for m in re.finditer(re.escape(term), text):
            start = max(0, m.start()-15)
            end = min(len(text), m.end()+15)
            context = text[start:end].replace('\n', ' ')
            found.append({
                'term': term,
                'level': ALL_TERMS[term],
                'pos': m.start(),
                'context': f"...{context}..."
            })
    return found

def get_dominant_level(mentions, threshold=2):
    """找出章節中最主要的修為（出現次數最多）"""
    from collections import Counter
    if not mentions:
        return None, 0
    c = Counter()
    for m in mentions:
        lvl = m['level']
        if isinstance(lvl, tuple):
            c[lvl[1]] += 1  # old term
        else:
            c[f'l12_{lvl}'] += 1  # new term
    most_common = c.most_common(1)[0]
    return most_common[0], most_common[1]

def main():
    results = {}
    
    for i in range(1, 136):
        path = f'research/chapter-{i}.md'
        if not os.path.exists(path):
            results[i] = {'error': 'file not found'}
            continue
        
        with open(path, 'r') as f:
            text = f.read()
        
        mentions = extract_levels(text, i)
        dominant, count = get_dominant_level(mentions)
        
        results[i] = {
            'chars': len(text),
            'mentions': len(mentions),
            'dominant': dominant,
            'details': mentions[:20]  # limit
        }
    
    # Print per-chapter analysis
    print("章節修為追蹤表")
    print("=" * 70)
    print(f"{'章節':<8} {'字數':<6} {'提及':<4} {'主要修為':<20} {'倒退?'}")
    print("-" * 70)
    
    prev_lvl = 0
    prev_name = "無"
    backward_count = 0
    
    for i in range(1, 136):
        r = results[i]
        if 'error' in r:
            print(f"Ch{i:<4}  ❌ {r['error']}")
            continue
        
        dom = r['dominant']
        chars = r['chars']
        ment = r['mentions']
        
        if dom and dom.startswith('l12_'):
            lvl = int(dom.replace('l12_', ''))
            name = level_names_l12[lvl-1]
        elif dom:
            # old term or none
            name = f"[舊] {dom}" if dom else "未知"
            lvl = 0  # unknown mapping
        else:
            name = "無"
            lvl = 0
        
        backward = ""
        if lvl > 0 and prev_lvl > 0 and lvl < prev_lvl:
            backward = f" ⚠️ {prev_name}({prev_lvl})→{name}({lvl}) 倒退{prev_lvl-lvl}級"
            backward_count += 1
        
        print(f"Ch{i:<4} {chars:<5} {ment:<3} {name:<20} {backward}")
        
        if lvl > 0:
            prev_lvl = lvl
            prev_name = name
    
    print("-" * 70)
    print(f"總倒退次數：{backward_count}")

if __name__ == '__main__':
    main()
