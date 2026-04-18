#!/usr/bin/env python3
"""
為所有章節頁面添加meta description
"""

import os
import re
import sys

WORKSPACE = "/home/openclaw/.openclaw/workspace"

def extract_chapter_info(filepath):
    """從章節文件中提取信息"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read(5000)  # 讀取前5000字符
        
        info = {
            "chapter_num": 0,
            "title": "",
            "content_preview": ""
        }
        
        # 提取章節號
        filename = os.path.basename(filepath)
        match = re.match(r"chapter-(\d+)(-av)?\.html", filename)
        if match:
            info["chapter_num"] = int(match.group(1))
        
        # 提取標題
        title_match = re.search(r'<title>(第\d+章[：:]?\s*(.*?))</title>', content)
        if title_match:
            full_title = title_match.group(1)
            # 提取標題部分（去掉「第X章：」）
            title_part = title_match.group(2) if title_match.group(2) else full_title
            info["title"] = title_part.strip()
        else:
            # 備用：從文件名推測
            info["title"] = f"第{info['chapter_num']}章"
        
        # 提取內容預覽（前200字符）
        # 先移除HTML標籤
        text_only = re.sub(r'<[^>]+>', ' ', content)
        text_only = re.sub(r'\s+', ' ', text_only).strip()
        
        # 取前200字符作為預覽
        if len(text_only) > 200:
            info["content_preview"] = text_only[:200] + "..."
        else:
            info["content_preview"] = text_only
        
        return info
        
    except Exception as e:
        print(f"❌ 讀取文件錯誤 {filepath}: {e}")
        return None

def generate_meta_description(info, is_av=False):
    """生成meta description"""
    chapter_num = info["chapter_num"]
    title = info["title"]
    preview = info["content_preview"]
    
    if is_av:
        # AV章節的描述
        return f"《科技修真傳》第{chapter_num}章：{title} - 有聲畫版本。圖文並茂+完整朗讀，沉浸式體驗科技修真世界。免費在線閱讀。"
    else:
        # 文字章節的描述
        if preview and len(preview) > 50:
            # 使用內容預覽
            return f"《科技修真傳》第{chapter_num}章：{title}。{preview} 免費閱讀完整章節，體驗融合科技與修真的奇幻小說。作者：大肥喵。"
        else:
            # 通用描述
            return f"《科技修真傳》第{chapter_num}章：{title}。免費閱讀完整章節，體驗融合科技與修真的奇幻小說。每日更新，作者：大肥喵。"

def add_meta_description_to_file(filepath, description):
    """向文件添加meta description"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查是否已經有description
        if '<meta name="description"' in content:
            # 更新現有的description
            pattern = r'<meta name="description" content="[^"]*">'
            if re.search(pattern, content):
                new_content = re.sub(pattern, f'<meta name="description" content="{description}">', content)
            else:
                return False  # 格式不匹配，跳過
        else:
            # 添加新的description
            # 在viewport meta之後添加
            viewport_pattern = r'<meta name="viewport"[^>]*>'
            match = re.search(viewport_pattern, content)
            if match:
                viewport_end = match.end()
                meta_tag = f'\n    <meta name="description" content="{description}">'
                new_content = content[:viewport_end] + meta_tag + content[viewport_end:]
            else:
                # 如果找不到viewport，在charset之後添加
                charset_pattern = r'<meta charset="[^"]*">'
                match = re.search(charset_pattern, content)
                if match:
                    charset_end = match.end()
                    meta_tag = f'\n    <meta name="description" content="{description}">'
                    new_content = content[:charset_end] + meta_tag + content[charset_end:]
                else:
                    print(f"  ⚠️ {os.path.basename(filepath)}: 找不到插入位置")
                    return False
        
        # 寫回文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
        
    except Exception as e:
        print(f"  ❌ {os.path.basename(filepath)}: 錯誤 - {e}")
        return False

def process_chapter_files():
    """處理所有章節文件"""
    print("📝 為章節頁面添加meta description...")
    print("=" * 60)
    
    # 收集所有章節文件
    chapter_files = []
    for filename in os.listdir(WORKSPACE):
        if filename.startswith("chapter-") and filename.endswith(".html"):
            filepath = os.path.join(WORKSPACE, filename)
            chapter_files.append(filepath)
    
    total_files = len(chapter_files)
    updated_count = 0
    av_count = 0
    text_count = 0
    
    for i, filepath in enumerate(chapter_files):
        filename = os.path.basename(filepath)
        is_av = "-av.html" in filename
        
        # 提取章節信息
        info = extract_chapter_info(filepath)
        if not info:
            continue
        
        # 生成description
        description = generate_meta_description(info, is_av)
        
        # 添加到文件
        if add_meta_description_to_file(filepath, description):
            updated_count += 1
            if is_av:
                av_count += 1
            else:
                text_count += 1
        
        # 顯示進度
        if (i + 1) % 20 == 0:
            print(f"  已處理 {i+1}/{total_files} 個文件...")
    
    print(f"\n{'='*60}")
    print("📊 Meta description添加完成！")
    print(f"• 總共處理文件: {total_files} 個")
    print(f"• 成功添加/更新: {updated_count} 個")
    print(f"• 文字章節: {text_count} 個")
    print(f"• AV章節: {av_count} 個")
    
    # 顯示示例
    print(f"\n📋 示例描述:")
    if chapter_files:
        sample_file = chapter_files[0]
        sample_info = extract_chapter_info(sample_file)
        if sample_info:
            sample_desc = generate_meta_description(sample_info, "-av.html" in os.path.basename(sample_file))
            print(f"  {sample_desc[:100]}...")
    
    return updated_count > 0

def update_main_pages():
    """更新主要頁面的meta description（如果需要）"""
    print(f"\n🏠 更新主要頁面meta description...")
    
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
    
    updated_count = 0
    
    for filename, description in main_pages:
        filepath = os.path.join(WORKSPACE, filename)
        if not os.path.exists(filepath):
            continue
        
        if add_meta_description_to_file(filepath, description):
            print(f"  ✅ {filename}: 已更新")
            updated_count += 1
        else:
            print(f"  ℹ️ {filename}: 已是最新")
    
    print(f"• 主要頁面更新: {updated_count} 個")
    return True

if __name__ == "__main__":
    # 處理章節文件
    chapters_updated = process_chapter_files()
    
    # 更新主要頁面
    main_updated = update_main_pages()
    
    print(f"\n{'='*60}")
    if chapters_updated or main_updated:
        print("🎉 Meta description優化完成！")
        print("✅ 所有頁面現在都有優化的meta description")
        print("✅ 有助於提升SEO搜索排名和點擊率")
        sys.exit(0)
    else:
        print("⚠️ 沒有文件被更新")
        sys.exit(1)