#!/usr/bin/env python3
"""
重新生成乾淨的meta description
"""

import os
import re
import sys

WORKSPACE = "/home/openclaw/.openclaw/workspace"

def get_chapter_title(filepath):
    """從文件獲取章節標題"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read(3000)  # 讀取前3000字符
        
        # 方法1：從<title>標籤提取
        title_match = re.search(r'<title>(第\d+章[：:]?\s*(.*?))</title>', content)
        if title_match:
            full_title = title_match.group(1)
            # 提取標題部分
            if '：' in full_title:
                title = full_title.split('：', 1)[1].strip()
            elif ':' in full_title:
                title = full_title.split(':', 1)[1].strip()
            else:
                title = full_title.replace('第', '').replace('章', '').strip()
            
            if title and len(title) > 2:
                return title
        
        # 方法2：從<h1>標籤提取
        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content)
        if h1_match:
            h1_text = re.sub(r'<[^>]+>', '', h1_match.group(1)).strip()
            if h1_text and len(h1_text) > 2:
                # 移除「第X章」前綴
                cleaned = re.sub(r'^第\d+章[：:]?\s*', '', h1_text)
                if cleaned and len(cleaned) > 2:
                    return cleaned
        
        # 方法3：從文件名推測
        filename = os.path.basename(filepath)
        match = re.match(r"chapter-(\d+)(-av)?\.html", filename)
        if match:
            chapter_num = match.group(1)
            return f"第{chapter_num}章"
        
        return "科技修真傳"
        
    except Exception as e:
        print(f"❌ 讀取標題錯誤 {filepath}: {e}")
        return "科技修真傳"

def generate_clean_description(filepath):
    """生成乾淨的meta description"""
    filename = os.path.basename(filepath)
    is_av = "-av.html" in filename
    
    # 獲取章節號
    match = re.match(r"chapter-(\d+)(-av)?\.html", filename)
    chapter_num = match.group(1) if match else "1"
    
    # 獲取標題
    title = get_chapter_title(filepath)
    
    if is_av:
        # AV章節描述
        return f"《科技修真傳》第{chapter_num}章：{title} - 有聲畫版本。圖文並茂+完整朗讀，沉浸式體驗科技修真世界。免費在線閱讀。"
    else:
        # 文字章節描述
        return f"《科技修真傳》第{chapter_num}章：{title}。免費閱讀完整章節，體驗融合科技與修真的奇幻小說。每日更新，作者：大肥喵。"

def update_file_description(filepath, new_description):
    """更新文件的meta description"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找並替換description
        pattern = r'<meta name="description" content="[^"]*">'
        
        if re.search(pattern, content):
            # 替換現有的
            new_content = re.sub(pattern, f'<meta name="description" content="{new_description}">', content)
        else:
            # 添加新的（在viewport之後）
            viewport_pattern = r'<meta name="viewport"[^>]*>'
            match = re.search(viewport_pattern, content)
            if match:
                viewport_end = match.end()
                meta_tag = f'\n    <meta name="description" content="{new_description}">'
                new_content = content[:viewport_end] + meta_tag + content[viewport_end:]
            else:
                return False
        
        # 寫回文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
        
    except Exception as e:
        print(f"❌ 更新文件錯誤 {filepath}: {e}")
        return False

def main():
    print("🔄 重新生成乾淨的meta description...")
    print("=" * 60)
    
    # 處理章節文件
    chapter_files = []
    for filename in os.listdir(WORKSPACE):
        if filename.startswith("chapter-") and filename.endswith(".html"):
            filepath = os.path.join(WORKSPACE, filename)
            chapter_files.append(filepath)
    
    total_chapters = len(chapter_files)
    updated_chapters = 0
    
    print(f"📚 處理 {total_chapters} 個章節文件...")
    
    for i, filepath in enumerate(chapter_files):
        filename = os.path.basename(filepath)
        
        # 生成新描述
        new_description = generate_clean_description(filepath)
        
        # 更新文件
        if update_file_description(filepath, new_description):
            updated_chapters += 1
        
        # 顯示進度
        if (i + 1) % 50 == 0:
            print(f"  已處理 {i+1}/{total_chapters} 個章節...")
    
    # 主要頁面的描述（保持不變或輕微優化）
    main_pages = [
        ("home.html", "《科技修真傳》官方網站 - 每日更新的AI生成小說，融合科技與修真的奇幻世界。免費閱讀120+章節，體驗獨特的科技修真之旅。作者：大肥喵。"),
        ("chapters.html", "《科技修真傳》完整章節目錄 - 查看所有120章小說內容。科技與修真融合的奇幻故事，每日更新，免費閱讀。"),
        ("av-novels.html", "《科技修真傳》有聲畫版本 - 70章圖文並茂+完整朗讀。沉浸式體驗科技修真世界，免費在線觀看。"),
        ("news.html", "AI新聞資訊 - 最新人工智能、機器學習、科技發展動態。每日更新，掌握AI前沿技術。"),
        ("finance.html", "財經資訊 - 加密貨幣、美股市場、投資分析。即時行情，專業分析，助你把握投資機會。"),
        ("dashboard.html", "香港實時資訊儀表板 - 天氣、交通、新聞一站式查看。香港生活必備工具。"),
        ("author.html", "大肥喵 - 《科技修真傳》作者介紹。創作理念、作品集、聯繫方式。"),
        ("index.html", "科技修真傳 - 融合科技與修真的AI生成小說。每日更新，免費閱讀完整章節。")
    ]
    
    updated_main = 0
    print(f"\n🏠 更新主要頁面...")
    
    for filename, description in main_pages:
        filepath = os.path.join(WORKSPACE, filename)
        if os.path.exists(filepath):
            if update_file_description(filepath, description):
                updated_main += 1
                print(f"  ✅ {filename}: 已更新")
    
    print(f"\n{'='*60}")
    print("📊 重新生成完成！")
    print(f"• 章節文件更新: {updated_chapters}/{total_chapters}")
    print(f"• 主要頁面更新: {updated_main}/{len(main_pages)}")
    
    # 顯示示例
    if chapter_files:
        sample_file = chapter_files[0]
        sample_desc = generate_clean_description(sample_file)
        print(f"\n📋 示例描述:")
        print(f"  {sample_desc}")
    
    return updated_chapters > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)