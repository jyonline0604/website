#!/usr/bin/env python3
import os, requests, json, time

API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
if not API_KEY:
    # Try to load from environment directly
    import subprocess
    result = subprocess.run(['bash', '-c', 'echo $DEEPSEEK_API_KEY'], capture_output=True, text=True)
    API_KEY = result.stdout.strip()

BASE_URL = 'https://api.deepseek.com'

def call_api(messages, max_tokens=100):
    headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
    resp = requests.post(f'{BASE_URL}/chat/completions', headers=headers, 
        json={'model': 'deepseek-chat', 'messages': messages, 'temperature': 0.1, 'max_tokens': max_tokens}, timeout=60)
    resp.raise_for_status()
    return resp.json()['choices'][0]['message']['content']

CULTIVATION_LEVELS = {
    '感氣': 1, '聚元': 2, '築基': 3, '煉魂': 4, '凝神': 5,
    '化物': 6, '悟天': 7, '掌命': 8, '破虛': 9, '造界': 10,
    '超脫': 11, '永恆': 12
}

timeline = {}

for ch in range(1, 136):
    path = f'research/chapter-{ch}.md'
    if not os.path.exists(path):
        continue
    text = open(path).read()[:2000]
    
    prompt = f"""分析以下章節，判断主角叶尘当前的修为等级。

只输出以下格式：修为名（如感氣期、聚元期、築基期等，或"未明確"）

章节 {ch}：
{text[:600]}"""

    try:
        result = call_api([
            {'role': 'system', 'content': '你是修仙小說修为分析专家。'},
            {'role': 'user', 'content': prompt}
        ])
        
        level_str = result.strip()
        
        for lvl_name, lvl_val in CULTIVATION_LEVELS.items():
            if lvl_name in level_str:
                timeline[ch] = {'level': lvl_val, 'name': lvl_name}
                print(f"Ch{ch}: L{lvl_val} ({lvl_name})")
                break
        else:
            if '未明確' in level_str or '不明' in level_str:
                timeline[ch] = {'level': None, 'name': '未明確'}
                print(f"Ch{ch}: 未明確")
            else:
                print(f"Ch{ch}: 解析失敗 ({level_str[:20]})")
        
    except Exception as e:
        print(f"Ch{ch} ❌: {e}")
        time.sleep(5)
    
    if ch % 20 == 0:
        print(f"  ... {ch}/135")

with open('cultivation_timeline.json', 'w', encoding='utf-8') as f:
    json.dump(timeline, f, ensure_ascii=False, indent=2)

print(f"\n完成！共 {len(timeline)} 章")
