#!/usr/bin/env python3
"""Generate HTML from new novel txt files (CH1-10)"""
import re
import os

TEMPLATE_PATH = "/home/openclaw/.openclaw/workspace/chapter-template.html"
INBOUND_DIR = "/home/openclaw/.openclaw/media/inbound"
WORKSPACE_DIR = "/home/openclaw/.openclaw/workspace"

CHAPTER_FILES = {
    1: "第一章_落葉歸根---0908f9b4-45a7-4689-b92d-71cfea5efdf4.txt",
    2: "第二章_初感元氣---19207dd0-0dee-4a51-8576-7d79e789084f.txt",
    3: "第三章_族會風波---addccf30-a7b6-42d4-bc90-10edb4e93a49.txt",
    4: "第四章_塵埃訣---1b53eca4-8d68-48f9-994a-bcc473d91b0e.txt",
    5: "第五章_進山準備---dc3897e7-ebde-440c-a494-5808382f1cb9.txt",
    6: "第六章_蒼瀾歷練---7054075e-3161-4ac6-9338-3b70905c0697.txt",
    7: "第七章_月下突破---0ea994da-fd8c-4923-ab82-b7d4bb9878fd.txt",
    8: "第八章_洞中傳承---0152d183-e804-4790-80b4-80ab29b2d887.txt",
    9: "第九章_各懷鬼胎---64b68770-cddb-40c6-a56e-d12f798e07ba.txt",
    10: "第十章_風雨欲來---ffa046d2-bcfa-4f82-b79e-01902d7498d0.txt",
}

# Simplified to Traditional Chinese mapping
S2T = str.maketrans({
    '叶': '葉', '灵': '靈', '气': '氣', '时': '時', '为': '為',
    '无': '無', '与': '與', '个': '個', '对': '對', '来': '來',
    '说': '說', '们': '們', '么': '麼', '这': '這', '那': '那',
    '里': '裡', '后': '後', '发': '發', '见': '見', '当': '當',
    '过': '過', '着': '著', '却': '卻', '还': '還', '经': '經',
    '从': '從', '只': '只', '要': '要', '会': '會', '东': '東',
    '样': '樣', '体': '體', '认': '認', '关': '關', '动': '動',
    '应': '應', '开': '開', '变': '變', '边': '邊', '让': '讓',
    '问': '問', '号': '號', '报': '報', '备': '備', '传': '傳',
    '结': '結', '业': '業', '总': '總', '设': '設', '达': '達',
    '运': '運', '进': '進', '远': '遠', '连': '連', '选': '選',
    '适': '適', '较': '較', '车': '車', '转': '轉', '产': '產',
    '几': '幾', '义': '義', '术': '術', '回': '回', '此': '此',
    '因': '因', '但': '但', '或': '或', '向': '向', '被': '被',
    '把': '把', '给': '給', '至': '至', '内': '內', '场': '場',
    '收': '收', '期': '期', '现': '現', '望': '望', '克': '克',
    '服': '服', '再': '再', '已': '已', '做': '做', '成': '成',
    '没': '沒', '万': '萬', '听': '聽', '声': '聲', '处': '處',
    '书': '書', '两': '兩', '物': '物', '点': '點', '前': '前',
    '然': '然', '能': '能', '看': '看', '想': '想', '十': '十',
    '百': '百', '千': '千', '万': '萬', '门': '門', '关': '關',
    '难': '難', '题': '題', '际': '際', '非': '非', '常': '常',
    '正': '正', '比': '比', '特': '特', '别': '別', '等': '等',
    '得': '得', '地': '地', '方': '方', '法': '法', '第': '第',
    '最': '最', '高': '高', '兴': '興', '头': '頭', '吗': '嗎',
    '吧': '吧', '啊': '啊', '呢': '呢', '情': '情', '者': '者',
    '它': '它', '女': '女', '男': '男', '儿': '兒', '时': '時',
    '缃': '緗', '网': '網', '线': '線', '织': '織', '编': '編',
})

def sc2tc(text):
    return text.translate(S2T)

def cn_to_arabic(cn):
    """Convert Chinese numeral to Arabic."""
    if cn.isdigit():
        return int(cn)
    map_ = {'零':0,'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10,'百':100,'千':1000,'萬':10000}
    result = 0
    temp = 0
    for c in cn:
        if c in map_:
            v = map_[c]
            if v >= 100:
                result = (result or 1) * v
                temp = 0
            else:
                temp += v
    return result + temp

def extract_info(content):
    """Extract chapter number and title."""
    lines = content.strip().split('\n')
    
    # CH1 has "萬古塵埃\n第一卷 塵埃甦醒\n第一章 落葉歸根"
    # CH2 starts with "第二章 初感元氣"
    # CH3 starts with "第三章 族會風波"
    # etc.
    for i, line in enumerate(lines[:5]):
        line = line.strip()
        # Try pattern: 第X章 [·:： ] title
        m = re.match(r'第([零一二三四五六七八九十百千萬\d]+)章\s*[·:： ]?\s*(.+)$', line)
        if m:
            return cn_to_arabic(m.group(1)), m.group(2).strip(), i
    return None, None, 0

def process_body(content, start_line):
    """Process story body into HTML paragraphs."""
    lines = content.strip().split('\n')
    
    # Skip title and volume lines
    body = []
    for line in lines[start_line:]:
        line = line.strip()
        if not line:
            continue
        # Skip empty/short lines and headers
        if line.startswith('萬古塵埃') or line.startswith('第') or line.startswith('#'):
            continue
        # Skip chapter end marker
        if re.match(r'.*（第[一二三四五六七八九十百千萬\d]+章\s*完）', line):
            line = re.sub(r'（第[一二三四五六七八九十百千萬\d]+章\s*完）', '', line).strip()
        if line:
            body.append(line)
    
    # Join all text
    text = ' '.join(body)
    # Convert simplified chars
    text = sc2tc(text)
    
    # Split into paragraphs by sentence-ending punctuation
    sentences = re.split(r'[。！？」』】"\n]+', text)
    
    paras = []
    current = []
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        current.append(s)
        if len(' '.join(current)) > 150:
            para_text = '。'.join(current) + '。'
            paras.append(f'<p>{para_text}</p>')
            current = []
    
    if current:
        para_text = '。'.join(current) + '。'
        paras.append(f'<p>{para_text}</p>')
    
    return paras

def main():
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template = f.read()
    
    for ch_num, filename in sorted(CHAPTER_FILES.items()):
        filepath = os.path.join(INBOUND_DIR, filename)
        if not os.path.exists(filepath):
            print(f"❌ NOT FOUND: {filename}")
            continue
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        ch_arabic, title, start_line = extract_info(content)
        if not title or not ch_arabic:
            print(f"❌ EXTRACT FAILED: {filename}")
            continue
        
        prev_url = f'https://kofhk.com/chapter-{ch_arabic-1}.html' if ch_arabic > 1 else '#'
        next_url = f'https://kofhk.com/chapter-{ch_arabic+1}.html'
        
        paras = process_body(content, start_line)
        body_html = '\n        '.join(paras)
        
        html = template
        canonical_url = f'https://kofhk.com/chapter-{ch_arabic}.html'
        html = html.replace('{chapter_title}', f'第{ch_arabic}章 · {title}')
        html = html.replace('{content}', body_html)
        html = html.replace('{prev_url}', prev_url)
        html = html.replace('{next_url}', next_url)
        html = html.replace('{CHAPTER_NUM}', str(ch_arabic))
        html = html.replace('{canonical}', canonical_url)
        
        # Title tag
        html = re.sub(r'<title>.*?</title>', f'<title>第{ch_arabic}章 · {title} - 萬古塵埃</title>', html)
        
        output_path = os.path.join(WORKSPACE_DIR, f'chapter-{ch_arabic}.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ CH{ch_arabic}: 第{ch_arabic}章 · {title}")

if __name__ == '__main__':
    main()
