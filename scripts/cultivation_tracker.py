#!/usr/bin/env python3
"""
Comprehensive cultivation tracker for 萬古塵埃
Tracks protagonist's cultivation level through all 135 chapters
"""
import os, re, json

CULTIVATION_LEVELS = {
    '感氣': 1, '聚元': 2, '築基': 3, '煉魂': 4, '凝神': 5,
    '化物': 6, '悟天': 7, '掌命': 8, '破虛': 9, '造界': 10,
    '超脫': 11, '永恆': 12
}

def extract_chapter_cultivation(ch_num, text):
    """Extract protagonist's cultivation level from chapter"""
    # Key patterns that indicate protagonist's level
    patterns = [
        # Direct level mentions with 葉塵 as subject
        r'葉塵.{0,20}(?:的修為|已達|邁入|突破到|達到|晋升|修煉到了)(?:了)?([感氣聚元築基煉魂凝神化物悟天掌命破虛造界超脫永恆]+(?:期|境|層))',
        r'葉塵.{0,15}修為(?:是|為|已達|在)([感氣聚元築基煉魂凝神化物悟天掌命破虛造界超脫永恆]+(?:期|境|層))',
        # When 葉塵 does something requiring level
        r'以葉塵現在的修為.{0,10}([感氣聚元築基煉魂凝神化物悟天掌命破虛造界超脫永恆]+(?:期|境|層))',
        # Narrative description
        r'此刻的葉塵.{0,20}([感氣聚元築基煉魂凝神化物悟天掌命破虛造界超脫永恆]+(?:期|境|層))',
    ]
    
    results = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            if m in CULTIVATION_LEVELS:
                results.append((CULTIVATION_LEVELS[m], m, pattern[:50]))
    
    return results

def build_timeline():
    """Build cultivation timeline for all 135 chapters"""
    timeline = {}
    
    for i in range(1, 136):
        path = f'research/chapter-{i}.md'
        if not os.path.exists(path):
            continue
        with open(path) as f:
            text = f.read()
        
        levels = extract_chapter_cultivation(i, text)
        if levels:
            # Take the highest/most relevant level mentioned
            timeline[i] = max(levels, key=lambda x: x[0])
        else:
            timeline[i] = None
    
    return timeline

def check_timeline(timeline):
    """Check for inconsistencies in timeline"""
    issues = []
    prev_level = None
    prev_ch = None
    
    for ch in sorted(timeline.keys()):
        current = timeline[ch]
        if current is None:
            continue
        
        curr_level, curr_name, _ = current
        
        if prev_level is not None:
            diff = curr_level - prev_level
            # Allow increases up to 2 levels (breakthrough arcs)
            # Allow stays (0)
            # Allow small drops for power suppression (-1)
            # Anything else is suspicious
            if diff < -1:
                issues.append((prev_ch, ch, prev_level, curr_level, diff))
            elif diff > 2:
                issues.append((prev_ch, ch, prev_level, curr_level, diff))
        
        prev_level = curr_level
        prev_ch = ch
    
    return issues

if __name__ == '__main__':
    timeline = build_timeline()
    
    # Save timeline
    timeline_data = {ch: {'level': lvl[0] if lvl else None, 'name': lvl[1] if lvl else None} 
                    for ch, lvl in timeline.items()}
    with open('cultivation_timeline.json', 'w', encoding='utf-8') as f:
        json.dump(timeline_data, f, ensure_ascii=False, indent=2)
    
    issues = check_timeline(timeline)
    
    print(f"Timeline built for {len(timeline)} chapters")
    print(f"Found {len(issues)} potential cultivation inconsistencies")
    
    for prev_ch, ch, prev_lvl, curr_lvl, diff in issues[:20]:
        print(f"  Ch{prev_ch}→{ch}: L{prev_lvl}→L{curr_lvl} ({diff:+d})")
