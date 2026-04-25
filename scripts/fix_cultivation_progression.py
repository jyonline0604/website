#!/usr/bin/env python3
"""修正修為倒退：找出每個章節的正確修為，用AI修正級數錯誤的句子"""
import re, os, json, requests, sys

API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
BASE_URL = 'https://api.deepseek.com'

# 12級系統名稱
L12 = {1:'感氣',2:'聚元',3:'築基',4:'煉魂',5:'凝神',6:'化物',7:'悟天',8:'掌命',9:'破虛',10:'造界',11:'超脫',12:'永恆'}
INV_L12 = {v:k for k,v in L12.items()}

# 預計正確修為進度（按故事發展）
# 卷1: 青雲宗假死→荒野修煉→天機洞探險 (Ch1-40)
# 卷2: 天劍閣入門→歸墟殿浮現 (Ch41-80)  
# 卷3: 萬古戰場→靈天界 (Ch81-135)
EXPECTED_PROGRESSION = {
    # 卷1: 凡塵界初期
    1: '感氣', 2: '感氣', 3: '感氣', 4: '感氣', 5: '感氣',
    6: '感氣', 7: '聚元', 8: '聚元', 9: '聚元', 10: '聚元',
    11: '聚元', 12: '聚元', 13: '築基', 14: '築基', 15: '築基',
    16: '築基', 17: '築基', 18: '煉魂', 19: '煉魂', 20: '煉魂',
    21: '煉魂', 22: '煉魂', 23: '凝神', 24: '凝神', 25: '凝神',
    26: '凝神', 27: '凝神', 28: '化物', 29: '化物', 30: '化物',
    31: '化物', 32: '化物', 33: '化物', 34: '化物', 35: '化物',
    # 卷2: 天劍閣
    36: '化物', 37: '化物', 38: '化物', 39: '化物', 40: '化物',
    41: '化物', 42: '化物', 43: '化物', 44: '化物', 45: '化物',
    46: '化物', 47: '化物', 48: '化物', 49: '化物', 50: '化物',
    51: '悟天', 52: '悟天', 53: '悟天', 54: '悟天', 55: '悟天',
    56: '悟天', 57: '悟天', 58: '悟天', 59: '悟天', 60: '悟天',
    # 卷3: 歸墟殿崛起
    61: '掌命', 62: '掌命', 63: '掌命', 64: '掌命', 65: '掌命',
    66: '掌命', 67: '掌命', 68: '掌命', 69: '掌命', 70: '掌命',
    71: '破虛', 72: '破虛', 73: '破虛', 74: '破虛', 75: '破虛',
    76: '破虛', 77: '破虛', 78: '破虛', 79: '破虛', 80: '破虛',
    # 卷4: 萬古戰場前期
    81: '破虛', 82: '破虛', 83: '破虛', 84: '造界', 85: '造界',
    86: '造界', 87: '造界', 88: '造界', 89: '造界', 90: '造界',
    91: '造界', 92: '造界', 93: '造界', 94: '造界', 95: '造界',
    # 卷5: 萬古戰場後期
    96: '超脫', 97: '超脫', 98: '超脫', 99: '超脫', 100: '超脫',
    101: '超脫', 102: '超脫', 103: '超脫', 104: '超脫', 105: '超脫',
    106: '永恆', 107: '永恆', 108: '永恆', 109: '永恆', 110: '永恆',
    # 卷6: 靈天界
    111: '永恆', 112: '永恆', 113: '永恆', 114: '永恆', 115: '永恆',
    116: '永恆', 117: '永恆', 118: '永恆', 119: '永恆', 120: '永恆',
    121: '永恆', 122: '永恆', 123: '永恆', 124: '永恆', 125: '永恆',
    126: '永恆', 127: '永恆', 128: '永恆', 129: '永恆', 130: '永恆',
    131: '永恆', 132: '永恆', 133: '永恆', 134: '永恆', 135: '永恆',
}

def call_api(messages, max_tokens=500):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': 'deepseek-chat',
        'messages': messages,
        'temperature': 0.3,
        'max_tokens': max_tokens
    }
    resp = requests.post(f'{BASE_URL}/chat/completions', headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()['choices'][0]['message']['content']

def main():
    # First pass: identify backward steps using actual reading + AI
    print("=== 掃描修為倒退章節 ===")
    
    # Read each chapter and check for major wrong-level sentences
    for i in range(5, 136):  # Check suspicious chapters
        expected = EXPECTED_PROGRESSION.get(i)
        if not expected:
            continue
        
        path = f'research/chapter-{i}.md'
        if not os.path.exists(path):
            continue
        with open(path, 'r') as f:
            text = f.read()
        
        expected_lvl = INV_L12[expected]
        
        # Find wrong-level sentences
        bad_sentences = []
        for lvl_name, lvl_num in INV_L12.items():
            if lvl_num == expected_lvl:
                continue  # Skip the correct level
            pattern = f'達到了{lvl_name}|突破到{lvl_name}|修為已達{lvl_name}|{lvl_name}期修士'
            for m in re.finditer(pattern, text, re.DOTALL):
                pos = m.start()
                # Check context - is this about the protagonist?
                ctx_start = max(0, pos - 80)
                ctx = text[ctx_start:pos+30].replace('\n', ' ')
                bad_sentences.append((lvl_name, lvl_num, ctx))
        
        if len(bad_sentences) > 0:
            wrong_summary = '; '.join(f'{n}({l})' for n,l,_ in bad_sentences[:3])
            print(f"Ch{i:>3}: 應為{expected}實際出現={wrong_summary}")

if __name__ == '__main__':
    main()
