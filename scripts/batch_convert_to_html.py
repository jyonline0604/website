#!/usr/bin/env python3
"""批量轉換所有章節 Markdown → HTML"""

import re, os, glob, time
from datetime import datetime

WORKSPACE = "/home/openclaw/.openclaw/workspace"
TEMPLATE = f"{WORKSPACE}/chapter-template.html"
SRC_DIR = f"{WORKSPACE}/research"
OUT_DIR = WORKSPACE

with open(TEMPLATE) as f:
    template = f.read()

# 找所有 chapter-N.md 文件
chapters = sorted(glob.glob(f"{SRC_DIR}/chapter-*.md"), 
                  key=lambda x: int(re.search(r'chapter-(\d+)', x).group(1)))

print(f"📚 找到 {len(chapters)} 個章節文件")

success = 0
errors = []

for src_path in chapters:
    try:
        num = int(re.search(r'chapter-(\d+)', src_path).group(1))
        
        with open(src_path) as f:
            content = f.read()
        
        # 提取標題
        title_match = re.search(r'^#\s+(第.+)$', content, re.MULTILINE)
        raw_title = title_match.group(1).strip() if title_match else f"第{num}章"
        # 如果標題以「第N章」開頭（後跟空格或：），去掉前綴避免重複
        chapter_title = re.sub(r'^第.+?章[：:\s]+', '', raw_title)
        if chapter_title == raw_title:  # 前綴不匹配，保持原樣
            chapter_title = raw_title
        chapter_num = str(num)
        
        # 清理內容
        text = re.sub(r'^#\s+.+\n?', '', content)
        text = re.sub(r'\n---\n', '\n<hr>\n', text)
        text = re.sub(r'\n\n+', '</p><p>', text)
        text = re.sub(r'\n', '<br>', text)
        text = f"<p>{text}</p>"
        text = re.sub(r'<br><br><p>', '<br></p><p>', text)
        text = re.sub(r'<p><br>', '<p>', text)
        text = re.sub(r'<br></p>', '</p>', text)
        text = re.sub(r'———', '<hr class="section-divider">', text)
        text = re.sub(r'<p>（第([^<]+?)完）</p>', r'<p class="chapter-end">（第\1完）</p>', text)
        
        # 構建 HTML
        html = template
        html = html.replace("{CHAPTER_NUM}", chapter_num)
        html = html.replace("{CHAPTER_TITLE}", chapter_title)
        html = html.replace("科技修真傳", "萬古塵埃")
        html = html.replace("{CONTENT}", text)
        html = html.replace("{PREV_NUM}", str(num - 1) if num > 1 else "0")
        
        out_path = f"{OUT_DIR}/chapter-{num}.html"
        with open(out_path, "w") as f:
            f.write(html)
        
        success += 1
        
    except Exception as e:
        errors.append(f"chapter-{num}: {e}")

print(f"\n✅ 成功: {success}/{len(chapters)}")
if errors:
    print(f"❌ 錯誤: {errors}")