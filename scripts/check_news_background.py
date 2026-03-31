#!/usr/bin/env python3
"""
檢查新聞頁面背景圖問題
"""

import os
import re
import sys

WORKSPACE = "/home/openclaw/.openclaw/workspace"
NOVEL_DIR = WORKSPACE

def check_news_background():
    """檢查新聞頁面背景圖"""
    print("🔍 檢查新聞頁面背景圖問題")
    print("="*50)
    
    news_path = os.path.join(NOVEL_DIR, "news.html")
    
    try:
        with open(news_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        # 1. 檢查整個頁面背景
        if 'body::before' in content:
            print("✅ 整個頁面有背景圖 (body::before)")
        
        # 2. 檢查新聞卡片內的背景圖
        if '.news-card-body::before' in content:
            issues.append("❌ 新聞卡片內有背景圖 (.news-card-body::before)")
            print("❌ 發現問題: 新聞卡片內有背景圖")
        else:
            print("✅ 新聞卡片內沒有背景圖")
        
        # 3. 檢查新聞卡片圖像背景
        news_card_image_bg = re.search(r'\.news-card-image\s*{[^}]*background:\s*([^;]+)', content)
        if news_card_image_bg:
            bg_value = news_card_image_bg.group(1).strip()
            if bg_value != 'transparent':
                issues.append(f"❌ 新聞卡片圖像背景不是透明: {bg_value}")
                print(f"❌ 新聞卡片圖像背景: {bg_value}")
            else:
                print("✅ 新聞卡片圖像背景是透明")
        
        # 4. 檢查JavaScript中的背景設置
        js_bg_pattern = r'const bgColor\s*=\s*["\']([^"\']+)["\']'
        js_match = re.search(js_bg_pattern, content)
        if js_match:
            js_bg = js_match.group(1)
            if js_bg != 'transparent':
                issues.append(f"❌ JavaScript中設置了背景: {js_bg}")
                print(f"❌ JavaScript背景設置: {js_bg}")
            else:
                print("✅ JavaScript背景設置為透明")
        
        # 5. 檢查是否有其他背景圖引用
        bg_images = re.findall(r'background.*url\(["\']?([^"\')]+)', content)
        for bg_img in bg_images:
            if 'news-bg.jpg' in bg_img:
                location = "整個頁面" if 'body::before' in content else "未知位置"
                print(f"ℹ️ 背景圖引用: {bg_img} ({location})")
        
        if issues:
            print(f"\n⚠️ 發現 {len(issues)} 個問題:")
            for issue in issues:
                print(f"  {issue}")
            return False
        else:
            print("\n✅ 所有背景圖設置正確")
            return True
            
    except Exception as e:
        print(f"❌ 檢查錯誤: {e}")
        return False

def main():
    success = check_news_background()
    
    print("\n" + "="*50)
    if success:
        print("✅ 新聞頁面背景圖檢查通過")
        return 0
    else:
        print("⚠️ 需要修復新聞頁面背景圖問題")
        return 1

if __name__ == "__main__":
    sys.exit(main())