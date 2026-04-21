#!/usr/bin/env python3
"""
為文字版章節添加有聲畫按鈕
自動掃描所有有AV版本但缺少按鈕的章節並添加

用法: python3 add_av_buttons_to_text.py
或指定章節: python3 add_av_buttons_to_text.py 71 72 73
"""

import os
import re
import sys

WORKSPACE = "/home/openclaw/.openclaw/workspace"

# 有聲畫按鈕的HTML
AV_BUTTON = '<a href="av-novels.html" style="display:inline-flex;align-items:center;padding:8px 12px;background:rgba(102,126,234,0.8);color:white;border-radius:8px;text-decoration:none;font-size:0.85rem;margin-right:8px;">🎬 有聲畫</a>'

def add_av_button(chapter_num):
    """為指定章節添加有聲畫按鈕"""
    text_file = os.path.join(WORKSPACE, f"chapter-{chapter_num}.html")
    av_file = os.path.join(WORKSPACE, f"chapter-{chapter_num}-av.html")
    
    # 檢查AV版本是否存在
    if not os.path.exists(av_file):
        return False, "沒有AV版本"
    
    # 檢查文字版是否存在
    if not os.path.exists(text_file):
        return False, "文字版不存在"
    
    # 讀取文件
    with open(text_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 檢查是否已有按鈕
    if 'av-novels' in content or '🎬 有聲' in content:
        return False, "已有按鈕"
    
    # 查找插入位置：<span class="chapter-title">第X章</span> 之後
    # 匹配模式：章節標題後、header-right之前
    pattern = r'(<span class="chapter-title">第\d+章[^<]*</span>\s*)(<div class="header-right">)'
    match = re.search(pattern, content)
    
    if match:
        # 在chapter-title之後、header-right之前插入有聲畫按鈕
        new_content = re.sub(
            pattern,
            r'\1\n            ' + AV_BUTTON + r'\n            \2',
            content
        )
        
        # 保存
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, "成功"
    else:
        return False, "找不到插入位置"

def scan_and_fix():
    """掃描所有章節，自動修復有按鈕問題的章節"""
    print("=== 掃描並修復有聲畫按鈕 ===\n")
    
    fixed = []
    skipped = []
    
    # 掃描章節1-200
    for i in range(1, 201):
        text_file = os.path.join(WORKSPACE, f"chapter-{i}.html")
        av_file = os.path.join(WORKSPACE, f"chapter-{i}-av.html")
        
        # 跳過不存在的章節
        if not os.path.exists(text_file):
            continue
        
        # 跳過沒有AV版本的章節
        if not os.path.exists(av_file):
            continue
        
        # 讀取檢查是否有按鈕
        with open(text_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'av-novels' in content or '🎬 有聲' in content:
            skipped.append((i, "已有按鈕"))
            continue
        
        # 需要修復
        success, msg = add_av_button(i)
        if success:
            fixed.append(i)
            print(f"  ✅ 第{i}章：已添加有聲畫按鈕")
        else:
            print(f"  ❌ 第{i}章：{msg}")
            skipped.append((i, msg))
    
    print(f"\n=== 修復完成 ===")
    print(f"已修復: {len(fixed)} 個章節")
    if fixed:
        print(f"章節列表: {fixed}")
    print(f"跳過: {len(skipped)} 個章節")
    
    return fixed, skipped

def main():
    if len(sys.argv) > 1:
        # 指定章節號
        chapter_nums = [int(x) for x in sys.argv[1:]]
        print(f"=== 為指定章節添加有聲畫按鈕 ===\n")
        
        for num in chapter_nums:
            success, msg = add_av_button(num)
            if success:
                print(f"✅ 第{num}章：已添加有聲畫按鈕")
            else:
                print(f"❌ 第{num}章：{msg}")
    else:
        # 自動掃描並修復
        fixed, skipped = scan_and_fix()
        return len(fixed)

if __name__ == '__main__':
    main()