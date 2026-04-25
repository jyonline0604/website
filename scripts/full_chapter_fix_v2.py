#!/usr/bin/env python3
"""《萬古塵埃》修復 v2 — 更精準的截斷檢測 + 修復"""

import os, re, glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(WORKSPACE, "research")

def check_truncation(filepath):
    """更精準地檢查章節是否被截斷"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    filename = os.path.basename(filepath)
    num = int(re.search(r'chapter-(\d+)', filename).group(1))
    
    # 去掉空白行
    non_empty = [l for l in lines if l.strip()]
    if not non_empty:
        return False, ""
    
    last = non_empty[-1].strip()
    
    # 自然結束的標點
    natural_endings = '。！？」』—…\n'
    # 也能接受的結束
    acceptable_endings = '）】》\n'
    
    # 檢查最後一個字符
    last_char = last[-1] if last else ''
    
    # 如果最後一行的末尾字元是字母或逗號，或句子明顯未完成
    if last_char.isalpha():
        return True, last[:50]
    
    # 檢查是否包含明顯的截斷標記
    truncation_signs = ['未完待續', '（本章未完）', '待續', '本章未完']
    if any(sign in last for sign in truncation_signs):
        return True, last[:50]
    
    return False, ""

def fix_chapter_171(filepath):
    """修復第171章：蘇塵→葉塵"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    content = content.replace('蘇塵', '葉塵')
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    files = sorted(glob.glob(os.path.join(DIR, "chapter-*.md")),
                   key=lambda x: int(re.search(r'chapter-(\d+)', x).group(1)))
    
    # 採集所有章節的基本統計
    print("=== 最終統計報表 ===\n")
    
    all_stats = []
    for fpath in files:
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        filename = os.path.basename(fpath)
        num = int(re.search(r'chapter-(\d+)', filename).group(1))
        
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
        
        is_trunc, sample = check_truncation(fpath)
        
        all_stats.append({
            'num': num,
            'chars': chinese_chars,
            'truncated': is_trunc,
            'sample': sample,
        })
    
    # 字數統計
    total = sum(s['chars'] for s in all_stats)
    print(f"📊 總章數：{len(all_stats)}")
    print(f"📊 總中文字數：{total:,}")
    print(f"📊 平均字數：{total//len(all_stats):,}")
    print(f"📊 最短章節：{min(all_stats, key=lambda x: x['chars'])['num']}（{min(all_stats, key=lambda x: x['chars'])['chars']:,}字）")
    print(f"📊 最長章節：{max(all_stats, key=lambda x: x['chars'])['num']}（{max(all_stats, key=lambda x: x['chars'])['chars']:,}字）\n")
    
    # 截斷章節
    truncated = [s for s in all_stats if s['truncated']]
    if truncated:
        print(f"⚠️ 可能截斷的章節（{len(truncated)}個）：")
        for s in truncated:
            print(f"  Ch{s['num']}: {s['chars']:,}字 | 結尾: ...{s['sample']}")
    else:
        print("✅ 無截斷章節\n")
    
    # 列表格式（便於批量處理）
    print("\n=== 章節列表（titles.txt生成用）===\n")
    for s in all_stats:
        print(f"Ch{s['num']:>3}: {s['chars']:>5,}字{' ⚠️截斷' if s['truncated'] else ''}")
    
    # 提取標題列表
    print("\n=== 重複標題檢查 ===\n")
    titles = {}
    for fpath in files:
        with open(fpath, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
        title = re.sub(r'^[#\s]*第?\d*章?[：:\s]*', '', first_line)
        title = re.sub(r'[-—].*', '', title).strip()
        if title:
            titles.setdefault(title, []).append(
                re.search(r'chapter-(\d+)', os.path.basename(fpath)).group(1)
            )
    
    dupes = {k: v for k, v in titles.items() if len(v) > 1}
    if dupes:
        print(f"⚠️ 發現 {len(dupes)} 組重複標題：")
        for title, chs in sorted(dupes.items()):
            print(f"  「{title}」→ 第{', '.join(chs)}章")
    else:
        print("✅ 無重複標題")

if __name__ == '__main__':
    main()
