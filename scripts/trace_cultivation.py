#!/usr/bin/env python3
"""追蹤主角修為進度，找出真正的矛盾"""
import re, os

LVL_ORDER = ['感氣','聚元','築基','煉魂','凝神','化物','悟天','掌命','破虛','造界','超脫','永恆']
LVL_NUM = {l:i+1 for i,l in enumerate(LVL_ORDER)}

# Track protagonist level per chapter
protagonist_levels = {}

for ch in range(1, 136):
    path = f'research/chapter-{ch}.md'
    if not os.path.exists(path):
        continue
    text = open(path).read()
    
    # Record protagonist-level statements
    # Priority: explicit breakthrough > implicit state > mention
    best_lvl = None
    
    for lvl in LVL_ORDER:
        # "突破到X期" pattern
        if re.search(rf'(?:成功突破|終於突破|一舉突破|突破到|突破至|邁入|跨入)\S*{lvl}', text):
            best_lvl = lvl
            break
    
    if not best_lvl:
        for lvl in LVL_ORDER:
            # "已達到X期", "修為已達X期"
            if re.search(rf'(?:已達到|已達|達到.{0,4}|已恢復.{0,4}|恢復到.{0,4}){lvl}', text):
                # Check if about protagonist
                for m in re.finditer(rf'(?:已達到|已達|達到.{0,4}|已恢復.{0,4}|恢復到.{0,4}){lvl}', text):
                    ctx = text[max(0,m.start()-30):m.end()+10]
                    if '葉塵' in ctx or '他的' in ctx[:20] or '他的修為' in ctx:
                        best_lvl = lvl
                if best_lvl:
                    break
    
    if not best_lvl:
        # Check for "葉塵只有X期"
        for lvl in LVL_ORDER:
            for m in re.finditer(rf'(?:葉塵|他).{{0,30}}(?:只有|不過|已是|現在是).{{0,5}}{lvl}', text):
                best_lvl = lvl
    
    protagonist_levels[ch] = best_lvl

# Print progression
print(f"{'章節':>6} {'修為':>8} {'故事階段'}")
print("-"*40)
prev_lvl = None
for ch in range(1, 136):
    lvl = protagonist_levels.get(ch)
    if lvl:
        lvl_num = LVL_NUM.get(lvl, 0)
        if prev_lvl and lvl_num < prev_lvl:
            mark = f" ⚠️倒退{prev_lvl-lvl_num}級"
        elif prev_lvl and lvl_num > prev_lvl:
            mark = f" ↑突破{prev_lvl-lvl_num:+d}"
        else:
            mark = ""
        prev_lvl = lvl_num
        print(f"Ch{ch:>3}  {lvl:>6}  {mark}")
    else:
        print(f"Ch{ch:>3}  {'?':>8}")

print(f"\n\n=== 有明確修為嘅章節 ===")
counted = [ch for ch,lvl in protagonist_levels.items() if lvl]
print(f"共 {len(counted)} 章有明確修為提及，{135-len(counted)} 章需要推斷")
