#!/usr/bin/env python3
"""Analyze and fix cultivation inconsistencies in problem chapters"""
import os, requests, json, time

API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
BASE_URL = 'https://api.deepseek.com'

def call_api(messages, max_tokens=500):
    headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
    resp = requests.post(f'{BASE_URL}/chat/completions', headers=headers, 
        json={'model': 'deepseek-chat', 'messages': messages, 'temperature': 0.1, 'max_tokens': max_tokens}, timeout=90)
    resp.raise_for_status()
    return resp.json()['choices'][0]['message']['content']

# The 24 problem chapters from diagnostic report
problem_pairs = [
    (2,3),(6,7),(8,9),(17,18),(26,27),(35,36),(39,40),(44,45),
    (52,54),(57,60),(65,66),(69,70),(72,73),(74,75),(75,77),
    (80,82),(86,87),(102,103),(112,113),(114,116),(123,124),
    (127,128),(129,130),(133,134)
]

def get_chapter_context(chapters):
    """Get full context for multiple chapters"""
    result = {}
    for ch in chapters:
        path = f'research/chapter-{ch}.md'
        if os.path.exists(path):
            with open(path) as f:
                text = f.read()
            # Get last 600 chars of previous chapter, first 600 of current
            if chapters.index(ch) > 0:
                prev_ch = chapters[chapters.index(ch) - 1]
                prev_path = f'research/chapter-{prev_ch}.md'
                if os.path.exists(prev_path):
                    prev_text = open(prev_path).read()
                    result[(prev_ch, ch)] = {
                        'prev_end': prev_text[-600:].replace('\n', ' '),
                        'curr_start': text[:600].replace('\n', ' ')
                    }
            else:
                result[(ch, ch+1)] = {
                    'prev_end': '',
                    'curr_start': text[:600].replace('\n', ' ')
                }
    return result

# Full analysis with proper context
all_issues = []
all_ok = []

for prev_ch, ch in problem_pairs:
    prev_path = f'research/chapter-{prev_ch}.md'
    curr_path = f'research/chapter-{ch}.md'
    if not os.path.exists(prev_path) or not os.path.exists(curr_path):
        continue
    
    prev_text = open(prev_path).read()[-800:].replace('\n', ' ')
    curr_text = open(curr_path).read()[:800].replace('\n', ' ')
    
    prompt = f"""你是小說編輯，檢查章節銜接的合理性。

【章節{prev_ch}結尾，重點描述】：
「{prev_text}」

【章節{ch}開頭，重點描述】：
「{curr_text}」

請分析：
1. 葉塵在章節{prev_ch}結尾時的修為？依據是？
2. 葉塵在章節{ch}開頭時的修為？依據是？
3. 兩者是否有矛盾？還是其實合理（壓制/回憶/敵人等）？
4. 有矛盾的話，具體需要修改哪個句子？

回覆格式（繁體）：
問題：...
章節{prev_ch}修為：...（依據：...）
章節{ch}修為：...（依據：...）
矛盾：是/否
如有矛盾，需要修改的句子：..."""

    try:
        result = call_api([
            {'role': 'system', 'content': '你是一個嚴謹的小說編輯。'},
            {'role': 'user', 'content': prompt}
        ])
        
        has_issue = '矛盾：是' in result or '需要修改' in result
        if has_issue:
            all_issues.append((prev_ch, ch, result))
            print(f"⚠️ Ch{prev_ch}→{ch}: 有問題需要修復")
        else:
            all_ok.append((prev_ch, ch, result))
            print(f"✅ Ch{prev_ch}→{ch}: OK")
        
    except Exception as e:
        print(f"❌ Ch{prev_ch}→{ch}: {e}")
        time.sleep(5)
    
    time.sleep(1)

print(f"\n共 {len(all_issues)} 個需要修復")
print(f"共 {len(all_ok)} 個確認OK")

# Save results
with open('problem_analysis.json', 'w', encoding='utf-8') as f:
    json.dump({'issues': all_issues, 'ok': [(a,b,r[:500]) for a,b,r in all_ok]}, f, ensure_ascii=False, indent=2)

print("\n詳細分析已保存到 problem_analysis.json")
