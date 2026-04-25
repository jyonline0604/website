#!/usr/bin/env python3
import os, requests, json, time, sys

API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
if not API_KEY:
    print("❌ DEEPSEEK_API_KEY not set")
    sys.exit(1)

BASE_URL = 'https://api.deepseek.com'

def call_api(messages, max_tokens=150):
    headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
    resp = requests.post(f'{BASE_URL}/chat/completions', headers=headers, 
        json={'model': 'deepseek-chat', 'messages': messages, 'temperature': 0.3, 'max_tokens': max_tokens}, timeout=60)
    resp.raise_for_status()
    return resp.json()['choices'][0]['message']['content']

def get_preview(num, start=True):
    path = f'research/chapter-{num}.md'
    if not os.path.exists(path):
        return None
    with open(path) as f:
        text = f.read()
    if start:
        return text[:400].replace('\n', ' ').strip()
    else:
        return text[-400:].replace('\n', ' ').strip()

# Process all pairs
results = {}
total = 132

for i in range(1, total + 1):
    a, b = i, i + 1
    curr_end = get_preview(a, start=False)
    next_start = get_preview(b, start=True)
    
    if not curr_end or not next_start:
        print(f"⚠️  Ch{a}→{b}: skip (no data)")
        continue
    
    prompt = f"""為以下章節創作過渡句（只 output 一句，20字以內，繁體）：

上：「{curr_end[-200:]}」
下：「{next_start[:200]}」

直接output過渡句："""
    
    try:
        result = call_api([
            {'role': 'system', 'content': '你是仙俠小說編輯。'},
            {'role': 'user', 'content': prompt}
        ])
        results[f'Ch{a}→{b}'] = result.strip()
        print(f"✅ Ch{a}→{b}: {result.strip()[:40]}")
    except Exception as e:
        print(f"❌ Ch{a}→{b}: {e}")
        time.sleep(3)
    
    if i % 20 == 0:
        print(f"  ...progress: {i}/{total}")

# Save
with open('transition_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n完成 {len(results)}/{total} 過渡句")
