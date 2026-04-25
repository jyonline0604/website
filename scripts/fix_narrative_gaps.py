#!/usr/bin/env python3
"""修復敘事斷層 - 用DeepSeek生成連接段落"""

import os, re, glob, json
import requests

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(WORKSPACE, "research")
KEY = os.environ.get('DEEPSEEK_API_KEY', '')

def tokenize(text):
    chars = re.findall(r'[\u4e00-\u9fff]{2,4}', text)
    return set(chars)

def has_transition(filepath):
    """檢查章節是否已有過渡段落插入"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    # 檢查是否已有過渡標記（從第2-5行之間找）
    lines = content.split('\n')
    body_start = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and not stripped.startswith('<!--'):
            body_start = i
            break
    
    if body_start >= 0 and body_start + 3 < len(lines):
        # 看正文開始的幾行是否有過渡語氣
        transition_lines = []
        for i in range(body_start, min(body_start + 5, len(lines))):
            l = lines[i].strip()
            if l and len(l) > 10:
                transition_lines.append(l)
        body_text = ' '.join(transition_lines)
        # 檢查是否包含明顯的過渡句（情境連貫詞）
        indicators = ['這一刻', '此時', '就在', '此刻', '夜色', '數日後', '他轉身']
        count = sum(1 for ind in indicators if ind in body_text)
        return count >= 2
    
    return False

def get_discontinuity_pairs(top_n=15, skip_file='.fixed_pairs.txt'):
    # 讀取已修復的配對
    skip_set = set()
    if os.path.exists(skip_file):
        with open(skip_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    skip_set.add(line)
    
    files = sorted(glob.glob(os.path.join(DIR, 'chapter-*.md')),
                   key=lambda x: int(re.search(r'chapter-(\d+)', x).group(1)))
    
    pairs = []
    for i in range(len(files)-1):
        f1, f2 = files[i], files[i+1]
        num1 = int(re.search(r'chapter-(\d+)', f1).group(1))
        num2 = int(re.search(r'chapter-(\d+)', f2).group(1))
        
        pair_key = f'{num1}-{num2}'
        if pair_key in skip_set:
            continue
        
        with open(f1) as f:
            t1 = f.read()
        with open(f2) as f:
            t2 = f.read()
        
        end_text = t1[-300:] if len(t1) > 300 else t1
        start_text = t2[:300] if len(t2) > 300 else t2
        
        end_tokens = tokenize(end_text)
        start_tokens = tokenize(start_text)
        overlap = len(end_tokens.intersection(start_tokens))
        total = len(end_tokens.union(start_tokens))
        ratio = overlap / total if total > 0 else 0
        
        if ratio < 0.02:
            end_sample = re.findall(r'.{20}$', end_text.replace('\n', '')[:80]) 
            start_sample = re.findall(r'^.{20}', start_text.replace('\n', '')[:80])
            end_tail = end_text[-80:].replace('\n', ' ')[:60]
            start_head = start_text[:80].replace('\n', ' ')[:60]
            pairs.append((num1, num2, ratio, end_tail, start_head))
    
    return pairs[:top_n]

def fix_transition(num1, num2, end_text, start_text):
    """用DeepSeek生成過渡段落"""
    prompt = f"""你是小說《萬古塵埃》的編輯。你需要修復第{num1}章和第{num2}章之間的敘事斷層。

第{num1}章結尾：
...{end_text}

第{num2}章開頭：
{start_text}...

任務：用1-3句中文過渡段落，無縫連接兩章。過渡段落將插入第{num2}章開頭（保留原有開頭文字在前）。

注意：不要改變已有文字，只要生成過渡段落。只輸出過渡段落本身，不多餘解釋。"""

    try:
        resp = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7, "max_tokens": 200
            },
            timeout=30
        )
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content'].strip()
    except:
        pass
    return None

def main():
    pairs = get_discontinuity_pairs(15)
    
    if not pairs:
        print("無需修復的敘事斷層")
        return
    
    print(f"待修復敘事斷層：{len(pairs)}對\n")
    
    for num1, num2, ratio, end_tail, start_head in pairs:
        print(f"Ch{num1}→Ch{num2}（重疊率{ratio*100:.1f}%）")
        print(f"  ↑結尾：{end_tail}")
        print(f"  ↓開頭：{start_head}")
        
        # 讀取完整結尾和開頭
        with open(os.path.join(DIR, f'chapter-{num1}.md')) as f:
            text1 = f.read()
        with open(os.path.join(DIR, f'chapter-{num2}.md')) as f:
            text2 = f.read()
        
        end = text1[-250:] if len(text1) > 250 else text1
        start = text2[:250] if len(text2) > 250 else text2
        
        transition = fix_transition(num1, num2, end, start)
        
        if transition:
            print(f"  ✅ 過渡段落：{transition}")
            
            # 插入到第num2章開頭
            lines = text2.split('\n')
            # 找到正文起始行
            insert_pos = 0
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped and not stripped.startswith('#'):
                    insert_pos = i
                    break
            
            insert_text = f"\n{transition}\n"
            lines.insert(insert_pos, insert_text)
            
            with open(os.path.join(DIR, f'chapter-{num2}.md'), 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            print(f"  ✅ 已插入Ch{num2}")
        else:
            print(f"  ❌ 生成失敗")
        print()

if __name__ == '__main__':
    main()
