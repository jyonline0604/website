#!/usr/bin/env python3
"""《萬古塵埃》全書批量修復腳本 v1

這個腳本修復以下問題：
1. 簡轉繁（全書所有文件）
2. 移除 Markdown 痕跡（## 標題符號、AI生成備註）
3. 報表：統計各章字數、檢查截斷章節
"""

import os, re, glob
from opencc import OpenCC

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(WORKSPACE, "research")

cc = OpenCC('s2tw')

def fix_file(filepath):
    """對單個文件執行所有修復"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 1. 簡轉繁
    content = cc.convert(content)
    
    # 2. 移除 Markdown ## 標題符號（保留文字）
    content = re.sub(r'^##\s+', '', content, flags=re.MULTILINE)
    
    # 3. 移除 AI 生成備註
    content = re.sub(r'\n本章字數[：:].*', '', content)
    content = re.sub(r'\n本章共.*字.*', '', content)
    content = re.sub(r'\n（本章完.*', '', content)
    
    # 4. 移除重複的章節標題格式
    # 把「第X章：標題 - 萬古塵埃」這樣的格式統一
    # （保持一行）
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def analyze_chapter(filepath):
    """分析單個章節，返回統計信息"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    filename = os.path.basename(filepath)
    num = int(re.search(r'chapter-(\d+)', filename).group(1))
    
    # 總字數（中文字元）
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
    
    # 檢查結尾是否完整（最後非空行是否以句號/感嘆號/問號/省略號結尾）
    lines = [l for l in content.split('\n') if l.strip()]
    last_line = lines[-1].strip() if lines else ""
    is_truncated = not any(last_line.endswith(p) for p in '。！？…」』）】\n')
    # 但如果結尾是自然結束的例外
    if last_line.endswith('）') or last_line.endswith('】'):
        is_truncated = False
    
    # 檢查簡體字殘留
    simplified = len(re.findall(r'[万与丑专丛东丝丟两严丧个丬临为丽举么](?![\\/])', content))
    
    return {
        'num': num,
        'chars': chinese_chars,
        'truncated': is_truncated,
        'simplified': simplified,
        'filename': filename,
    }

def main():
    files = sorted(glob.glob(os.path.join(DIR, "chapter-*.md")),
                   key=lambda x: int(re.search(r'chapter-(\d+)', x).group(1)))
    
    print("=== 階段1：簡轉繁 + 格式清理 ===\n")
    fixed = 0
    for fpath in files:
        if fix_file(fpath):
            fixed += 1
            filename = os.path.basename(fpath)
            print(f"  ✅ {filename}")
    
    print(f"\n已修復 {fixed} 個章節\n")
    
    print("=== 階段2：章節統計分析 ===\n")
    stats = [analyze_chapter(fpath) for fpath in files]
    
    total_chars = sum(s['chars'] for s in stats)
    truncated = [s for s in stats if s['truncated']]
    simplified_issues = [s for s in stats if s['simplified'] > 0]
    
    print(f"總章數：{len(stats)}")
    print(f"總中文字數：{total_chars:,}")
    print(f"平均字數：{total_chars//len(stats):,}")
    print(f"\n最短10章：")
    for s in sorted(stats, key=lambda x: x['chars'])[:10]:
        print(f"  Ch{s['num']}: {s['chars']:,}字")
    
    if truncated:
        print(f"\n⚠️ 可能截斷的章節（{len(truncated)}個）：")
        for s in truncated:
            print(f"  Ch{s['num']} ({s['chars']:,}字)")
    else:
        print("\n✅ 無截斷章節")
    
    if simplified_issues:
        print(f"\n⚠️ 仍有簡體字殘留（{len(simplified_issues)}個）：")
        for s in sorted(simplified_issues, key=lambda x: -x['simplified'])[:10]:
            print(f"  Ch{s['num']}: {s['simplified']}處殘留")
    else:
        print("\n✅ 簡體字清理乾淨")
    
    print(f"\n=== 分析完成 ===")

if __name__ == '__main__':
    main()
