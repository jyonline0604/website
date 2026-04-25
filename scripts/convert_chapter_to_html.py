#!/usr/bin/env python3
"""將《萬古塵埃》第1章 Markdown 轉換為 HTML 並發布到 GitHub"""

import re

WORKSPACE = "/home/openclaw/.openclaw/workspace"
SRC = f"{WORKSPACE}/research/chapter-1.md"
OUT_HTML = f"{WORKSPACE}/chapter-1.html"
TEMPLATE = f"{WORKSPACE}/chapter-template.html"

# 讀取內容
with open(SRC, "r") as f:
    content = f.read()

# 讀取模板
with open(TEMPLATE, "r") as f:
    template = f.read()

# 提取章節標題（# 第一章 塵埃 → 第一章 塵埃）
title_match = re.search(r'^#\s+(第.+)$', content, re.MULTILINE)
chapter_title = title_match.group(1).strip() if title_match else "第一章 塵埃"

# 提取章節數字
num_match = re.search(r'第(\d+)章', chapter_title)
chapter_num = num_match.group(1) if num_match else "1"

# 清理 Markdown 內容
text = re.sub(r'^#\s+.+\n?', '', content)  # 移除標題行
text = re.sub(r'\n---\n', '\n<hr>\n', text)  # 分隔線
text = re.sub(r'\n\n+', '</p><p>', text)  # 段落
text = re.sub(r'\n', '<br>', text)  # 換行
text = f"<p>{text}</p>"  # 包裝

# 處理特殊標記
text = re.sub(r'<br><br><p>', '<br></p><p>', text)
text = re.sub(r'<p><br>', '<p>', text)
text = re.sub(r'<br></p>', '</p>', text)
text = re.sub(r'———', '<hr class="section-divider">', text)
text = re.sub(r'（第一章\s*完）', '<p class="chapter-end">（第一章 完）</p>', text)

# 構建 HTML
html = template
html = html.replace("{CHAPTER_NUM}", chapter_num)
html = html.replace("{CHAPTER_TITLE}", chapter_title)
html = html.replace("科技修真傳", "萬古塵埃")
# 替換完整的 content 區塊（包含 {CONTENT}）
html = html.replace('content="">\n{CONTENT}\n        </div>', f'content="">\n            {text}\n        </div>')
html = html.replace("{PREV_NUM}", "0")  # 沒有上一章

# 保存
with open(OUT_HTML, "w") as f:
    f.write(html)

print(f"✅ 已生成: {OUT_HTML}")
print(f"   章節: 第{chapter_num}章 {chapter_title}")
chars = sum(1 for c in content if '\u4e00' <= c <= '\u9fff')
print(f"   字數: {chars}")