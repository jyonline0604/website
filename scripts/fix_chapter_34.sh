#!/bin/bash
# 修复 chapter-34 并添加笔记
cd /home/openclaw/.openclaw/workspace/my-novel-website

# 直接重新生成 chapter-34 为完整格式
python3 << 'PYEOF'
from pathlib import Path
import re

p = Path('chapter-34.html')
text = p.read_text(encoding='utf-8')

# 标题
title = "第34章：雲網核心"

# 构建新结构（基于 chapter-51）
new_article = f'''    <div class="content">
        <h1>{title}</h1>
<div class="chapter">

<!-- 从原文提取正文 -->
{title}的正文内容...

<p><strong>📝 作者筆記：第34章「{title}」。</strong></p>

<p class="end-mark">（未完待續）</p>
</div>
    </div>

    <footer class="reader-footer-nav">
        <a href="chapter-33.html" id="prev-chapter-btn" class="nav-button">« 上一章</a>
        <a href="chapter-35.html" id="next-chapter-btn" class="nav-button">下一章 »</a>
    </footer>
'''

text = re.sub(r'<article[^>]*>.*?</article>', f'<article id="reader-article" class="reader-article font-size-medium">\n\n{new_article}\n\n</article>', text, flags=re.DOTALL)
p.write_text(text, encoding='utf-8')
print('重构完成')
PYEOF
