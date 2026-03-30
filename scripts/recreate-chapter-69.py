#!/usr/bin/env python3
"""
重新創建第69章文件
"""

import os
import re

novel_dir = "/home/openclaw/.openclaw/workspace/my-novel"
chapter_68 = os.path.join(novel_dir, "chapter-68.html")
chapter_69 = os.path.join(novel_dir, "chapter-69.html")
chapter_69_backup = chapter_69 + ".backup2"

print(f"=== 重新創建第69章 ===")

# 備份當前文件
if os.path.exists(chapter_69):
    import shutil
    shutil.copy2(chapter_69, chapter_69_backup)
    print(f"✅ 已備份當前文件到: {chapter_69_backup}")

# 讀取第68章作為模板
if not os.path.exists(chapter_68):
    print(f"❌ 第68章文件不存在: {chapter_68}")
    exit(1)

with open(chapter_68, 'r', encoding='utf-8') as f:
    template = f.read()

print(f"第68章模板長度: {len(template)} 字符")

# 提取第69章內容（從備份中）
if os.path.exists(chapter_69 + ".backup"):
    with open(chapter_69 + ".backup", 'r', encoding='utf-8') as f:
        old_content = f.read()
    
    # 嘗試提取章節內容（<article>標籤內的內容）
    article_pattern = r'<article[^>]*>(.*?)</article>'
    article_match = re.search(article_pattern, old_content, re.DOTALL)
    
    if article_match:
        chapter_content = article_match.group(1)
        print(f"✅ 從備份中提取到章節內容，長度: {len(chapter_content)} 字符")
    else:
        # 嘗試提取<body>內的內容
        body_pattern = r'<body[^>]*>(.*?)</body>'
        body_match = re.search(body_pattern, old_content, re.DOTALL)
        if body_match:
            chapter_content = body_match.group(1)
            print(f"✅ 從備份中提取到body內容，長度: {len(chapter_content)} 字符")
        else:
            # 使用默認內容
            chapter_content = """
            <h1>第69章：能量風暴</h1>
            <div class="chapter-meta">
                <span class="author">作者：大肥喵</span>
                <span class="date">發布日期：2026年3月28日</span>
            </div>
            <div class="chapter-content">
                <p>林塵站在實驗室中央，周圍的能量波動越來越強烈。</p>
                <p>「警告！能量水平超出安全閾值！」系統的警報聲不斷響起。</p>
                <p>他深吸一口氣，雙手快速在控制面板上操作。這是他的最新發明——能量穩定器，但顯然還需要進一步調整。</p>
                <p>突然，一道藍色的能量光束從設備中心射出，直衝天花板。林塵迅速啟動防護罩，將能量束限制在安全範圍內。</p>
                <p>「成功了！」他興奮地喊道。經過數週的努力，終於找到了穩定高能量場的方法。</p>
                <p>這時，實驗室的門打開了，導師走了進來。</p>
                <p>「林塵，我聽說你的實驗有了突破？」導師問道。</p>
                <p>「是的，導師。我剛剛成功穩定了第三級能量場。」林塵匯報道。</p>
                <p>導師點點頭，眼中露出讚賞的神色。「很好。你的進步很快。不過要記住，能量控制不僅是技術問題，更是心境的體現。」</p>
                <p>林塵若有所思地點點頭。他明白導師的意思——修真之道，技術與心境缺一不可。</p>
                <p>「接下來，我打算嘗試將這種穩定技術應用到實戰中。」林塵說出了自己的計劃。</p>
                <p>「有想法是好的，但要循序漸進。」導師提醒道，「能量控制一旦失誤，後果不堪設想。」</p>
                <p>「我明白，導師。我會小心的。」</p>
                <p>導師離開後，林塵繼續調整設備。他知道，這只是開始。真正的挑戰還在後面。</p>
                <p>夜幕降臨，實驗室的燈光依然明亮。林塵的身影在各種儀器間忙碌，他的修真科技之旅，才剛剛進入新的階段。</p>
            </div>
            """
            print("⚠️  無法從備份提取內容，使用默認內容")
else:
    # 使用默認內容
    chapter_content = """
    <h1>第69章：能量風暴</h1>
    <div class="chapter-meta">
        <span class="author">作者：大肥喵</span>
        <span class="date">發布日期：2026年3月28日</span>
    </div>
    <div class="chapter-content">
        <p>林塵站在實驗室中央，周圍的能量波動越來越強烈。</p>
        <p>「警告！能量水平超出安全閾值！」系統的警報聲不斷響起。</p>
        <p>他深吸一口氣，雙手快速在控制面板上操作。這是他的最新發明——能量穩定器，但顯然還需要進一步調整。</p>
        <p>突然，一道藍色的能量光束從設備中心射出，直衝天花板。林塵迅速啟動防護罩，將能量束限制在安全範圍內。</p>
        <p>「成功了！」他興奮地喊道。經過數週的努力，終於找到了穩定高能量場的方法。</p>
        <p>這時，實驗室的門打開了，導師走了進來。</p>
        <p>「林塵，我聽說你的實驗有了突破？」導師問道。</p>
        <p>「是的，導師。我剛剛成功穩定了第三級能量場。」林塵匯報道。</p>
        <p>導師點點頭，眼中露出讚賞的神色。「很好。你的進步很快。不過要記住，能量控制不僅是技術問題，更是心境的體現。」</p>
        <p>林塵若有所思地點點頭。他明白導師的意思——修真之道，技術與心境缺一不可。</p>
        <p>「接下來，我打算嘗試將這種穩定技術應用到實戰中。」林塵說出了自己的計劃。</p>
        <p>「有想法是好的，但要循序漸進。」導師提醒道，「能量控制一旦失誤，後果不堪設想。」</p>
        <p>「我明白，導師。我會小心的。」</p>
        <p>導師離開後，林塵繼續調整設備。他知道，這只是開始。真正的挑戰還在後面。</p>
        <p>夜幕降臨，實驗室的燈光依然明亮。林塵的身影在各種儀器間忙碌，他的修真科技之旅，才剛剛進入新的階段。</p>
    </div>
    """
    print("⚠️  備份文件不存在，使用默認內容")

# 修改模板為第69章
# 1. 修改標題
new_content = template.replace('第68章：納米修真 - 科技修真傳', '第69章：能量風暴 - 科技修真傳')
new_content = new_content.replace('第68章：納米修真', '第69章：能量風暴')

# 2. 修改導航鏈接
new_content = new_content.replace('chapter-67.html', 'chapter-68.html')  # 上一章改為68
new_content = new_content.replace('chapter-69.html', 'chapter-70.html')  # 下一章改為70

# 3. 替換章節內容
# 找到<article>標籤並替換內容
article_pattern = r'<article[^>]*>.*?</article>'
if re.search(article_pattern, new_content, re.DOTALL):
    new_content = re.sub(article_pattern, f'<article>\n{chapter_content}\n</article>', new_content, flags=re.DOTALL)
    print("✅ 已替換<article>內容")
else:
    # 如果沒有<article>，在<body>內替換主要內容
    body_pattern = r'<body[^>]*>.*?<main[^>]*>.*?</main>.*?</body>'
    if re.search(body_pattern, new_content, re.DOTALL):
        new_body = f'<body>\n<main>\n{chapter_content}\n</main>\n</body>'
        new_content = re.sub(body_pattern, new_body, new_content, flags=re.DOTALL)
        print("✅ 已替換<body>內<main>內容")
    else:
        print("⚠️  無法找到內容區域，將內容添加到文件末尾")
        new_content = new_content.replace('</body>', f'\n{chapter_content}\n</body>')

# 寫入新文件
with open(chapter_69, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"✅ 第69章已重新創建，長度: {len(new_content)} 字符")

# 驗證新文件
print("\n=== 新文件驗證 ===")
with open(chapter_69, 'r', encoding='utf-8') as f:
    first_lines = [next(f) for _ in range(10)]
    
print("文件開頭:")
for i, line in enumerate(first_lines, 1):
    print(f"{i}: {line.rstrip()}")

# 檢查關鍵元素
with open(chapter_69, 'r', encoding='utf-8') as f:
    content = f.read()
    
checks = [
    ("<!DOCTYPE", "DOCTYPE聲明"),
    ("<html", "HTML開始標籤"),
    ("第69章：能量風暴", "章節標題"),
    ("</html>", "HTML結束標籤"),
    ("chapter-68.html", "上一章鏈接"),
    ("chapter-70.html", "下一章鏈接"),
]

print("\n關鍵元素檢查:")
for pattern, description in checks:
    count = content.count(pattern)
    status = "✅" if count > 0 else "❌"
    print(f"{status} {description}: {count}")

print(f"\n✅ 第69章重新創建完成")
print(f"原文件備份: {chapter_69_backup}")
print(f"第一次備份: {chapter_69}.backup")