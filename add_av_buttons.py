#!/usr/bin/env python3
"""
為文字版章節添加有聲畫按鈕
只為有對應AV版本的章節添加按鈕
"""

import os
import re

def add_av_button():
    workspace = '/home/openclaw/.openclaw/workspace'
    
    # 需要添加按鈕的章節（有AV版本但沒有按鈕）
    # 根據之前的檢查：71, 72, 73, 74, 75, 76
    chapters_to_fix = [71, 72, 73, 74, 75, 76]
    
    fixed_count = 0
    
    for chapter_num in chapters_to_fix:
        text_file = f'{workspace}/chapter-{chapter_num}.html'
        av_file = f'{workspace}/chapter-{chapter_num}-av.html'
        
        # 檢查AV版本是否存在
        if not os.path.exists(av_file):
            print(f"跳過第{chapter_num}章：沒有AV版本")
            continue
        
        # 檢查文字版是否存在
        if not os.path.exists(text_file):
            print(f"跳過第{chapter_num}章：文字版不存在")
            continue
        
        # 讀取文件
        with open(text_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查是否已有按鈕
        if 'av-novels' in content or '🎬 有聲' in content:
            print(f"第{chapter_num}章：已有按鈕，跳過")
            continue
        
        # 檢查header-right的位置
        header_right_pattern = r'(<span class="chapter-title">第\d+章[^<]*</span>\s*)(<div class="header-right">)'
        match = re.search(header_right_pattern, content)
        
        if match:
            # 在chapter-title之後、header-right之前插入有聲畫按鈕
            av_button = '''<a href="av-novels.html" style="display:inline-flex;align-items:center;padding:8px 12px;background:rgba(102,126,234,0.8);color:white;border-radius:8px;text-decoration:none;font-size:0.85rem;margin-right:8px;">🎬 有聲畫</a>'''
            
            new_content = re.sub(
                header_right_pattern,
                r'\1' + av_button + r'\n            \2',
                content
            )
            
            # 保存
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            fixed_count += 1
            print(f"第{chapter_num}章：✅ 已添加有聲畫按鈕")
        else:
            print(f"第{chapter_num}章：❌ 找不到插入位置")
    
    print(f"\n完成：修復了 {fixed_count} 個章節")
    return fixed_count

if __name__ == '__main__':
    add_av_button()