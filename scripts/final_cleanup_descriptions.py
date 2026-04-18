#!/usr/bin/env python3
"""
最終清理：確保每個文件只有一個乾淨的description
"""

import os
import re
import sys

WORKSPACE = "/home/openclaw/.openclaw/workspace"

def clean_file_descriptions(filepath):
    """清理文件的description標籤"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        filename = os.path.basename(filepath)
        
        # 1. 找到所有description標籤
        pattern = r'<meta name="description" content="([^"]*)">'
        matches = list(re.finditer(pattern, content))
        
        if not matches:
            return False  # 沒有description
        
        if len(matches) == 1:
            # 只有一個，檢查是否需要清理內容
            match = matches[0]
            old_desc = match.group(1)
            
            # 檢查是否包含CSS代碼
            if ':root' in old_desc or '--' in old_desc or '[data-theme' in old_desc:
                # 需要重新生成
                return regenerate_description(filepath, content)
            else:
                return False  # 已經乾淨
        
        else:
            # 多個description，保留第一個乾淨的
            print(f"  ⚠️ {filename}: 發現 {len(matches)} 個description標籤")
            
            # 找到第一個相對乾淨的
            clean_desc = None
            for match in matches:
                desc = match.group(1)
                if ':root' not in desc and '--' not in desc and '[data-theme' not in desc:
                    clean_desc = desc
                    break
            
            if not clean_desc:
                # 都沒有乾淨的，使用第一個
                clean_desc = matches[0].group(1)
                # 清理CSS代碼
                clean_desc = re.sub(r':root\s*\{[^}]*\}', '', clean_desc)
                clean_desc = re.sub(r'\[data-theme="[^"]*"\]\s*\{[^}]*\}', '', clean_desc)
                clean_desc = re.sub(r'--[a-z-]+:\s*[^;]+;', '', clean_desc)
                clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()
            
            # 刪除所有description標籤
            new_content = content
            for match in reversed(matches):
                new_content = new_content[:match.start()] + new_content[match.end():]
            
            # 在viewport之後添加乾淨的description
            viewport_pattern = r'<meta name="viewport"[^>]*>'
            viewport_match = re.search(viewport_pattern, new_content)
            
            if viewport_match:
                viewport_end = viewport_match.end()
                meta_tag = f'\n    <meta name="description" content="{clean_desc}">'
                new_content = new_content[:viewport_end] + meta_tag + new_content[viewport_end:]
            
            # 寫回文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"  ✅ {filename}: 清理完成")
            return True
        
    except Exception as e:
        print(f"  ❌ 處理錯誤 {filepath}: {e}")
        return False

def regenerate_description(filepath, content):
    """重新生成description"""
    filename = os.path.basename(filepath)
    
    # 簡單生成一個乾淨的描述
    if filename.startswith("chapter-"):
        match = re.match(r"chapter-(\d+)(-av)?\.html", filename)
        chapter_num = match.group(1) if match else "1"
        is_av = "-av" in filename if match else False
        
        if is_av:
            new_desc = f"《科技修真傳》第{chapter_num}章 - 有聲畫版本。圖文並茂+完整朗讀，沉浸式體驗科技修真世界。免費在線閱讀。"
        else:
            new_desc = f"《科技修真傳》第{chapter_num}章。免費閱讀完整章節，體驗融合科技與修真的奇幻小說。每日更新，作者：大肥喵。"
    else:
        # 主要頁面
        page_names = {
            "home.html": "《科技修真傳》官方網站 - 每日更新的AI生成小說，融合科技與修真的奇幻世界。",
            "chapters.html": "《科技修真傳》完整章節目錄 - 查看所有章節內容。",
            "av-novels.html": "《科技修真傳》有聲畫版本 - 圖文並茂+完整朗讀。",
            "news.html": "AI新聞資訊 - 最新人工智能、科技發展動態。",
            "finance.html": "財經資訊 - 加密貨幣、美股市場分析。",
            "dashboard.html": "香港實時資訊儀表板 - 天氣、交通、新聞。",
            "author.html": "大肥喵 - 《科技修真傳》作者介紹。",
            "index.html": "科技修真傳 - 融合科技與修真的AI生成小說。"
        }
        new_desc = page_names.get(filename, "科技修真傳 - AI生成小說網站")
    
    # 替換現有的description
    pattern = r'<meta name="description" content="[^"]*">'
    new_content = re.sub(pattern, f'<meta name="description" content="{new_desc}">', content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  ✅ {filename}: 重新生成description")
        return True
    
    return False

def main():
    print("🧼 最終清理：確保每個文件只有一個乾淨的description")
    print("=" * 60)
    
    # 處理所有HTML文件
    html_files = []
    for filename in os.listdir(WORKSPACE):
        if filename.endswith(".html"):
            filepath = os.path.join(WORKSPACE, filename)
            html_files.append(filepath)
    
    total_files = len(html_files)
    cleaned_count = 0
    
    for i, filepath in enumerate(html_files):
        if clean_file_descriptions(filepath):
            cleaned_count += 1
        
        # 顯示進度
        if (i + 1) % 50 == 0:
            print(f"  已處理 {i+1}/{total_files} 個文件...")
    
    print(f"\n{'='*60}")
    print("📊 最終清理完成！")
    print(f"• 總共處理文件: {total_files} 個")
    print(f"• 清理/修復文件: {cleaned_count} 個")
    
    # 驗證結果
    print(f"\n🔍 驗證結果:")
    test_files = ["chapter-1.html", "home.html", "chapters.html"]
    for test_file in test_files:
        test_path = os.path.join(WORKSPACE, test_file)
        if os.path.exists(test_path):
            with open(test_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            matches = list(re.finditer(r'<meta name="description" content="([^"]*)">', content))
            if len(matches) == 1:
                desc = matches[0].group(1)
                print(f"  ✅ {test_file}: 1個description, 長度{len(desc)}字符")
            else:
                print(f"  ❌ {test_file}: {len(matches)}個description")
    
    return cleaned_count > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)