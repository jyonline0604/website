#!/usr/bin/env python3
"""
標點符號修復腳本 v2
修復第351-400章的標點問題
"""

import os
import re
import sys

WORKSPACE = "/home/openclaw/.openclaw/workspace"
NOVEL_DIR = WORKSPACE

def smart_punctuate(text):
    """智能標點 - 盡量保持人名完整性"""
    # 移除所有現有標點
    text = re.sub(r'[。，、；：！？""''【】『』（）()《》<>]', '', text)
    text = re.sub(r'\s+', '', text)
    
    if not text or len(text) < 10:
        return text
    
    # 人名列表
    names = [
        '葉塵', '凌風', '月璃', '月華', '月琳', '月瑤', '無面', '暗塵',
        '天穹', '守望者', '幽影尊', '幽影尊者', '靈械', '鴻蒙', '林塵',
        '星淵', '雲霧', '高原', '中央', '塔樓', '議會', '長老', '指揮官',
        '士兵', '居民', '工程師', '研究者', '守衛', '戰士', '凡人', '修士',
        '煉器師', '陣法師', '靈芯', '系統', '晶片', '處理器', '人工智能',
        '第九代', '第八代', '第七世', '第六代', '第五代', '第四代',
        '第三代', '第二代', '第一代', '第九世', '第八世', '第七世',
        '第六世', '第五世', '第四世', '第三世', '第二世', '第一世',
        '月輪', '星圖', '時空', '頻率', '共振', '和諧', '平衡', '演化',
        '能量', '波動', '信號', '傳輸', '傳遞', '數據', '信息', '知識',
        '天穹城', '高原裂谷', '雲霧迷宮', '世界頻率', '頻率織物', '封印網絡',
    ]
    
    result = []
    i = 0
    while i < len(text):
        # 檢查是否匹配人名
        matched_name = None
        for name in names:
            if text[i:i+len(name)] == name:
                matched_name = name
                break
        
        if matched_name:
            # 添加人名
            result.append(matched_name)
            i += len(matched_name)
            
            # 在人名後面找下一個有意義的字符
            if i < len(text):
                next_char = text[i]
                
                # 如果後面是「的」、「在」、「了」等，通常是斷句點
                if next_char in '的了著過':
                    # 但要確保後面還有內容
                    rest = text[i+1:i+10] if i+1 < len(text) else ''
                    if len(rest) > 2:
                        result.append('。')
                elif next_char == '的':
                    result.append('。')
                elif next_char == '在':
                    result.append('。')
        else:
            result.append(text[i])
            i += 1
    
    text = ''.join(result)
    
    # 第二步：智能添加逗號
    sentences = []
    current = []
    count = 0
    last_punct = -1
    
    for idx, char in enumerate(text):
        current.append(char)
        count += 1
        
        if char == '。':
            sentences.append(''.join(current))
            current = []
            count = 0
            last_punct = idx
        elif count >= 60 and char in '的了是在和與但或因為所以如果':
            # 找到合適的斷句點
            rest = text[idx+1:idx+5] if idx+1 < len(text) else ''
            if len(rest) > 0:
                sentences.append(''.join(current))
                current = []
                count = 0
    
    if current:
        sentences.append(''.join(current))
    
    # 第三步：重組，確保每句以句號結尾
    final = []
    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue
        
        # 確保結尾有標點
        if sent and sent[-1] not in '。！？':
            sent = sent + '。'
        
        # 添加空格改善可讀性
        final.append(sent)
    
    return ''.join(final)

def process_chapter(chapter_num):
    """處理單個章節"""
    chapter_file = os.path.join(NOVEL_DIR, f"chapter-{chapter_num}.html")
    
    if not os.path.exists(chapter_file):
        return False
    
    print(f"📖 第 {chapter_num} 章...", end=" ")
    
    with open(chapter_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    main_start = content.find('<main>')
    main_end = content.find('</main>')
    
    if main_start == -1 or main_end == -1:
        print("❌ 找不到內容區")
        return False
    
    main_content = content[main_start:main_end]
    paragraphs = re.findall(r'<p>(.*?)</p>', main_content, re.DOTALL)
    
    if not paragraphs:
        print("❌ 無段落")
        return False
    
    fixed = []
    for p in paragraphs:
        clean = re.sub(r'<[^>]+>', '', p).strip()
        if clean and len(clean) > 5:
            fixed.append(smart_punctuate(clean))
    
    if not fixed:
        print("❌ 無有效段落")
        return False
    
    new_main = '<main>\n' + '\n'.join(f'<p>{p}</p>' for p in fixed) + '\n    </main>'
    new_content = content[:main_start] + new_main + content[main_end + 8:]
    
    with open(chapter_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅")
    return True

def main():
    print("=== 標點修復 v2 ===\n")
    
    for ch in range(351, 401):
        process_chapter(ch)
    
    print("\n完成!")

if __name__ == "__main__":
    main()