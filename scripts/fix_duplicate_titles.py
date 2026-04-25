#!/usr/bin/env python3
"""生成唯一章節標題 - 替換重複標題"""

import os, re, json, glob
import requests

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(WORKSPACE, "research")
DEEPSEEK_KEY = os.environ.get('DEEPSEEK_API_KEY', '')

# 重複標題分組
DUPLICATE_GROUPS = [
    # 「待定」佔位標題
    {'chapters': [156, 157, 158, 159, 160], 'old_title': '待定'},
    # 「戰場風雲」×4
    {'chapters': [123, 126, 128, 129], 'old_title': '戰場風雲'},
    # 「突破」×4
    {'chapters': [22, 60, 77, 100], 'old_title': '突破'},
    # 「萬古塵埃」×6（這些是章節標題與書名相同）
    {'chapters': [168, 172, 173, 191, 193, 194], 'old_title': '萬古塵埃'},
    # 以下為×2組
    {'chapters': [5, 6], 'old_title': '妖獸山谷'},
    {'chapters': [32, 111], 'old_title': '禁制'},
    {'chapters': [34, 112], 'old_title': '破解'},
    {'chapters': [51, 134], 'old_title': '線索'},
    {'chapters': [62, 135], 'old_title': '目標'},
    {'chapters': [80, 105], 'old_title': '交鋒'},
    {'chapters': [170, 196], 'old_title': '天穹裂了。'},  # 可能有句號
]

def get_chapter_context(num, lines=8):
    """獲取章節開頭內容用於生成標題"""
    fpath = os.path.join(DIR, f"chapter-{num}.md")
    if not os.path.exists(fpath):
        return None
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 跳過標題行，獲取正文的前幾行
    body_lines = []
    for line in content.split('\n'):
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            body_lines.append(stripped)
    
    context = '\n'.join(body_lines[:lines])
    return context

def generate_titles_via_api(group):
    """用DeepSeek API生成唯一標題"""
    chapters = group['chapters']
    old = group['old_title']
    
    # 收集每個章節的上下文
    contexts = []
    for ch in chapters:
        ctx = get_chapter_context(ch)
        if ctx:
            contexts.append(f"第{ch}章：\n{ctx}")
    
    context_text = '\n---\n'.join(contexts)
    
    prompt = f"""你係《萬古塵埃》小說嘅章節標題命名助手。

小說係修仙輪迴題材，主角葉塵經歷九世輪迴尋找真相。

以下幾章嘅標題都係「{old}」，但係佢哋嘅內容唔同。請根據每章嘅開頭內容，生成**獨一無二**嘅4字中文標題畀每章。

重要規則：
- 每個標題必須與其他章節不同
- 標題要反映該章嘅核心情節
- 用4個字

章節內容：
{context_text}

請按以下JSON格式回覆（只需輸出JSON，唔需要其他文字）：
{{"titles": {{"第X章": "新標題", "第Y章": "新標題"}}}}
"""
    
    try:
        resp = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 500
            },
            timeout=30
        )
        
        if resp.status_code == 200:
            data = resp.json()
            text = data['choices'][0]['message']['content']
            # 提取JSON
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result.get('titles', {})
        else:
            print(f"  API錯誤: {resp.status_code}")
            return {}
    except Exception as e:
        print(f"  請求失敗: {e}")
        return {}

def main():
    all_titles = {}
    
    for group in DUPLICATE_GROUPS:
        chapters = group['chapters']
        old = group['old_title']
        ch_str = ', '.join(str(c) for c in chapters)
        print(f"\n=== 「{old}」({len(chapters)}章: {ch_str}) ===")
        
        result = generate_titles_via_api(group)
        
        if result:
            for ch, new_title in sorted(result.items()):
                # 提取章節號
                m = re.search(r'(\d+)', ch)
                if m:
                    num = int(m.group(1))
                    all_titles[num] = new_title
                    print(f"  Ch{num}: {old} → {new_title}")
        else:
            print(f"  ❌ 生成失敗，使用手動備用標題")
            # 備用方案
            for i, ch in enumerate(chapters):
                all_titles[ch] = f"{old}（{['續','再','三','終','變'][i] if i < 5 else str(i+1)}）"
                print(f"  Ch{ch}: {old} → {all_titles[ch]}（備用）")
    
    # 應用標題到文件
    print(f"\n=== 應用標題 ===\n")
    for num, new_title in sorted(all_titles.items()):
        fpath = os.path.join(DIR, f"chapter-{num}.md")
        if not os.path.exists(fpath):
            print(f"  文件不存在: chapter-{num}.md")
            continue
        
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替換第一行標題
        # 處理多種標題格式
        lines = content.split('\n')
        modified = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            # 匹配 # 第X章 舊標題 或 # 舊標題 格式
            if re.match(r'^##?\s*(第\d+章[：:]?\s*)?.*$', stripped):
                # 提取章節前綴
                prefix_match = re.match(r'^(##?\s*第\d+章[：:]?\s*)', stripped)
                if prefix_match:
                    prefix = prefix_match.group(1)
                    lines[i] = f"{prefix}{new_title}"
                else:
                    # 只有 ## 開頭的情況
                    hash_prefix = re.match(r'^(##?\s*)', stripped).group(1)
                    lines[i] = f"{hash_prefix}{new_title}"
                modified = True
                break
        
        if modified:
            content = '\n'.join(lines)
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  Ch{num}: ✅ 更新成功")
        else:
            print(f"  Ch{num}: ⚠️ 未找到標題行")

if __name__ == '__main__':
    main()
