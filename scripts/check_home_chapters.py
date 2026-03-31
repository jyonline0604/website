#!/usr/bin/env python3
"""
全方位檢查 home.html 和 chapters.html
"""

import os
import re
import sys
from datetime import datetime

WORKSPACE = "/home/openclaw/.openclaw/workspace"
NOVEL_DIR = WORKSPACE

def check_html_structure(filepath, filename):
    """檢查HTML結構完整性"""
    print(f"\n📋 檢查 {filename} HTML結構:")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        # 1. 檢查基本HTML標籤
        if '<!DOCTYPE html>' not in content:
            issues.append("❌ 缺少 <!DOCTYPE html> 聲明")
        
        if '<html' not in content:
            issues.append("❌ 缺少 <html> 標籤")
        elif '</html>' not in content:
            issues.append("❌ 缺少 </html> 結束標籤")
        
        if '<head>' not in content:
            issues.append("❌ 缺少 <head> 標籤")
        elif '</head>' not in content:
            issues.append("❌ 缺少 </head> 結束標籤")
        
        if '<body>' not in content:
            issues.append("❌ 缺少 <body> 標籤")
        elif '</body>' not in content:
            issues.append("❌ 缺少 </body> 結束標籤")
        
        # 2. 檢查字符編碼
        if '<meta charset="UTF-8">' not in content and '<meta charset="utf-8">' not in content:
            issues.append("❌ 缺少 UTF-8 字符編碼聲明")
        
        # 3. 檢查視口設置
        if '<meta name="viewport"' not in content:
            issues.append("❌ 缺少視口設置 (viewport)")
        
        # 4. 檢查標題
        if '<title>' not in content:
            issues.append("❌ 缺少 <title> 標籤")
        
        # 5. 檢查CSS鏈接
        if 'fonts.googleapis.com' not in content:
            issues.append("⚠️ 缺少 Google Fonts 鏈接")
        
        # 6. 檢查JavaScript
        if '<script>' in content and '</script>' not in content:
            issues.append("❌ JavaScript 標籤不完整")
        
        # 7. 檢查圖片引用
        img_tags = re.findall(r'<img[^>]*src="([^"]+)"', content)
        for img_src in img_tags:
            if img_src.startswith('assets/'):
                img_path = os.path.join(NOVEL_DIR, img_src)
                if not os.path.exists(img_path):
                    issues.append(f"❌ 圖片不存在: {img_src}")
        
        # 8. 檢查CSS背景圖
        bg_images = re.findall(r'background.*url\(["\']?([^"\')]+)', content)
        for bg_img in bg_images:
            if bg_img.startswith('assets/'):
                bg_path = os.path.join(NOVEL_DIR, bg_img)
                if not os.path.exists(bg_path):
                    issues.append(f"❌ 背景圖片不存在: {bg_img}")
        
        # 9. 檢查鏈接有效性
        links = re.findall(r'<a[^>]*href="([^"]+)"', content)
        for link in links:
            if link.startswith('http://') or link.startswith('https://'):
                continue  # 外部鏈接跳過
            elif link.startswith('#'):
                continue  # 頁內錨點跳過
            elif link.startswith('mailto:'):
                continue  # 郵件鏈接跳過
            elif link.startswith('tel:'):
                continue  # 電話鏈接跳過
            else:
                # 檢查內部鏈接
                if link.endswith('.html'):
                    link_path = os.path.join(NOVEL_DIR, link)
                    if not os.path.exists(link_path):
                        issues.append(f"❌ 內部鏈接文件不存在: {link}")
        
        if issues:
            for issue in issues:
                print(f"  {issue}")
        else:
            print("  ✅ HTML結構完整")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"  ❌ 讀取文件錯誤: {e}")
        return False

def check_css_issues(filepath, filename):
    """檢查CSS問題"""
    print(f"\n🎨 檢查 {filename} CSS問題:")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        # 1. 提取所有CSS
        css_content = ""
        style_matches = re.findall(r'<style[^>]*>([\s\S]*?)</style>', content)
        for match in style_matches:
            css_content += match
        
        # 2. 檢查CSS語法錯誤（簡單檢查）
        if '{' in css_content and '}' in css_content:
            # 檢查大括號匹配
            open_braces = css_content.count('{')
            close_braces = css_content.count('}')
            if open_braces != close_braces:
                issues.append(f"❌ CSS大括號不匹配: {{={open_braces}, }}={close_braces}")
        else:
            issues.append("⚠️ 沒有找到CSS樣式")
        
        # 3. 檢查未關閉的CSS規則
        lines = css_content.split('\n')
        in_rule = False
        for i, line in enumerate(lines, 1):
            if '{' in line and '}' not in line:
                in_rule = True
            elif '}' in line and in_rule:
                in_rule = False
            elif in_rule and i == len(lines):
                issues.append(f"❌ CSS規則未關閉 (可能在第{i}行附近)")
        
        # 4. 檢查響應式設計
        if '@media' not in css_content:
            issues.append("⚠️ 缺少響應式設計 (@media queries)")
        
        # 5. 檢查變量定義
        if ':root' not in css_content:
            issues.append("⚠️ 缺少CSS變量定義 (:root)")
        
        if issues:
            for issue in issues:
                print(f"  {issue}")
        else:
            print("  ✅ CSS語法正確")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"  ❌ 檢查CSS錯誤: {e}")
        return False

def check_javascript_issues(filepath, filename):
    """檢查JavaScript問題"""
    print(f"\n⚡ 檢查 {filename} JavaScript問題:")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        # 1. 提取所有JavaScript
        js_content = ""
        script_matches = re.findall(r'<script[^>]*>([\s\S]*?)</script>', content)
        for match in script_matches:
            js_content += match
        
        if not js_content.strip():
            print("  ℹ️ 沒有JavaScript代碼")
            return True
        
        # 2. 檢查函數定義
        function_defs = re.findall(r'function\s+(\w+)\s*\(', js_content)
        if function_defs:
            print(f"  ℹ️ 找到 {len(function_defs)} 個函數: {', '.join(function_defs)}")
        
        # 3. 檢查事件監聽器
        if 'addEventListener' in js_content or 'onclick=' in content:
            print("  ℹ️ 有事件處理代碼")
        
        # 4. 檢查控制台錯誤
        if 'console.error' in js_content or 'throw new Error' in js_content:
            issues.append("⚠️ 可能有錯誤處理代碼")
        
        # 5. 檢查未定義的變量（簡單檢查）
        lines = js_content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'undefined' in line and '!==' not in line and '===' not in line:
                issues.append(f"⚠️ 可能使用未定義變量 (第{i}行): {line.strip()[:50]}")
        
        if issues:
            for issue in issues:
                print(f"  {issue}")
        else:
            print("  ✅ JavaScript代碼正常")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"  ❌ 檢查JavaScript錯誤: {e}")
        return False

def check_accessibility(filepath, filename):
    """檢查無障礙訪問問題"""
    print(f"\n♿ 檢查 {filename} 無障礙訪問:")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        # 1. 檢查圖片alt屬性
        img_tags = re.findall(r'<img[^>]*>', content)
        for img_tag in img_tags:
            if 'alt=' not in img_tag:
                issues.append("❌ 圖片缺少alt屬性")
                break
        
        # 2. 檢查表單標籤
        # 只檢查真正的表單元素，不包括普通按鈕
        if '<input' in content or '<select' in content or '<textarea' in content:
            # 簡單檢查是否有標籤
            if '<label' not in content:
                issues.append("⚠️ 表單元素可能缺少標籤")
        
        # 3. 檢查語義標籤
        semantic_tags = ['<header>', '<nav>', '<main>', '<section>', '<article>', '<footer>']
        found_semantic = False
        for tag in semantic_tags:
            if tag in content:
                found_semantic = True
                break
        
        if not found_semantic:
            issues.append("⚠️ 缺少語義HTML標籤")
        
        # 4. 檢查顏色對比度（簡單檢查）
        if 'color: white' in content and 'background: black' not in content:
            # 這只是簡單檢查，實際需要更複雜的對比度計算
            pass
        
        if issues:
            for issue in issues:
                print(f"  {issue}")
        else:
            print("  ✅ 無障礙訪問基本合格")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"  ❌ 檢查無障礙訪問錯誤: {e}")
        return False

def check_performance(filepath, filename):
    """檢查性能問題"""
    print(f"\n⚡ 檢查 {filename} 性能問題:")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        # 1. 檢查文件大小
        file_size = os.path.getsize(filepath)
        if file_size > 1024 * 100:  # 大於100KB
            issues.append(f"⚠️ 文件較大: {file_size/1024:.1f}KB")
        else:
            print(f"  ℹ️ 文件大小: {file_size/1024:.1f}KB")
        
        # 2. 檢查內聯CSS和JS
        style_count = content.count('<style')
        script_count = content.count('<script')
        
        if style_count > 3:
            issues.append(f"⚠️ 內聯CSS較多: {style_count} 處")
        else:
            print(f"  ℹ️ 內聯CSS: {style_count} 處")
        
        if script_count > 3:
            issues.append(f"⚠️ 內聯JS較多: {script_count} 處")
        else:
            print(f"  ℹ️ 內聯JS: {script_count} 處")
        
        # 3. 檢查圖片優化
        img_tags = re.findall(r'<img[^>]*>', content)
        if img_tags:
            print(f"  ℹ️ 圖片數量: {len(img_tags)}")
        
        # 4. 檢查外部資源
        external_resources = re.findall(r'src="https?://', content) + re.findall(r'href="https?://', content)
        if external_resources:
            print(f"  ℹ️ 外部資源: {len(external_resources)} 個")
        
        if issues:
            for issue in issues:
                print(f"  {issue}")
        else:
            print("  ✅ 性能表現良好")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"  ❌ 檢查性能錯誤: {e}")
        return False

def check_specific_home_issues():
    """檢查首頁特定問題"""
    print(f"\n🏠 檢查首頁特定問題:")
    
    home_path = os.path.join(NOVEL_DIR, "home.html")
    
    try:
        with open(home_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        # 1. 檢查最新章節顯示
        latest_chapters = re.findall(r'chapter-\d+\.html', content)
        if len(latest_chapters) < 3:
            issues.append(f"❌ 最新章節顯示不足: {len(latest_chapters)} 個")
        else:
            print(f"  ℹ️ 顯示最新章節: {len(latest_chapters)} 個")
        
        # 2. 檢查日期顯示
        if 'March' in content or 'April' in content:
            # 檢查是否有錯誤的日期（如March 32）
            wrong_dates = re.findall(r'March\s+(3[2-9]|[4-9]\d|\d{3,})', content)
            wrong_dates += re.findall(r'April\s+([4-9]\d|\d{3,})', content)
            if wrong_dates:
                issues.append(f"❌ 發現錯誤日期: {wrong_dates}")
            else:
                print("  ✅ 日期顯示正確")
        
        # 3. 檢查導航鏈接
        nav_links = ['home.html', 'chapters.html', 'news.html', 'author.html']
        for link in nav_links:
            if link not in content:
                issues.append(f"❌ 缺少導航鏈接: {link}")
        
        # 4. 檢查背景圖
        if 'hero-bg.jpg' not in content:
            issues.append("❌ 缺少背景圖引用")
        else:
            bg_path = os.path.join(NOVEL_DIR, 'assets/hero-bg.jpg')
            if not os.path.exists(bg_path):
                issues.append("❌ 背景圖片文件不存在")
            else:
                print("  ✅ 背景圖正常")
        
        if issues:
            for issue in issues:
                print(f"  {issue}")
            return False
        else:
            print("  ✅ 首頁功能完整")
            return True
            
    except Exception as e:
        print(f"  ❌ 檢查首頁錯誤: {e}")
        return False

def check_specific_chapters_issues():
    """檢查章節目錄特定問題"""
    print(f"\n📚 檢查章節目錄特定問題:")
    
    chapters_path = os.path.join(NOVEL_DIR, "chapters.html")
    
    try:
        with open(chapters_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        # 1. 檢查章節鏈接數量
        chapter_links = re.findall(r'chapter-\d+\.html', content)
        # 獲取實際章節文件數量
        actual_chapters = len([f for f in os.listdir(NOVEL_DIR) if f.startswith('chapter-') and f.endswith('.html') and f != 'chapter-0.html'])
        
        if len(chapter_links) != actual_chapters:
            issues.append(f"❌ 章節鏈接數量不匹配: 頁面顯示 {len(chapter_links)} 個，實際有 {actual_chapters} 個")
        else:
            print(f"  ✅ 章節鏈接完整: {len(chapter_links)} 個")
        
        # 2. 檢查分組按鈕
        group_buttons = re.findall(r'group-btn', content)
        if len(group_buttons) < 6:
            issues.append(f"❌ 分組按鈕不足: {len(group_buttons)} 個")
        else:
            print(f"  ℹ️ 分組按鈕: {len(group_buttons)} 個")
        
        # 3. 檢查排序功能
        if 'sortChapters' not in content:
            issues.append("❌ 缺少排序功能")
        else:
            print("  ✅ 排序功能正常")
        
        # 4. 檢查背景圖
        if 'chapters-bg.jpg' not in content:
            issues.append("❌ 缺少背景圖引用")
        else:
            bg_path = os.path.join(NOVEL_DIR, 'assets/chapters-bg.jpg')
            if not os.path.exists(bg_path):
                issues.append("❌ 背景圖片文件不存在")
            else:
                print("  ✅ 背景圖正常")
        
        # 5. 檢查分組跳轉功能
        if '#group-' not in content:
            issues.append("❌ 缺少分組跳轉功能")
        
        if issues:
            for issue in issues:
                print(f"  {issue}")
            return False
        else:
            print("  ✅ 章節目錄功能完整")
            return True
            
    except Exception as e:
        print(f"  ❌ 檢查章節目錄錯誤: {e}")
        return False

def check_broken_links(filepath, filename):
    """檢查斷鏈"""
    print(f"\n🔗 檢查 {filename} 斷鏈:")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        broken_count = 0
        
        # 檢查所有鏈接
        links = re.findall(r'href="([^"]+)"', content)
        for link in links:
            if link.startswith('http://') or link.startswith('https://'):
                continue  # 跳過外部鏈接檢查
            elif link.startswith('#'):
                continue  # 跳過頁內錨點
            elif link.startswith('mailto:') or link.startswith('tel:'):
                continue  # 跳過特殊鏈接
            elif link.endswith('.html'):
                # 檢查HTML文件是否存在
                link_path = os.path.join(NOVEL_DIR, link)
                if not os.path.exists(link_path):
                    issues.append(f"❌ 斷鏈: {link}")
                    broken_count += 1
        
        if broken_count > 0:
            print(f"  ❌ 發現 {broken_count} 個斷鏈")
            for issue in issues[:5]:  # 只顯示前5個
                print(f"    {issue}")
            if broken_count > 5:
                print(f"    ... 還有 {broken_count-5} 個斷鏈")
            return False
        else:
            print("  ✅ 沒有發現斷鏈")
            return True
            
    except Exception as e:
        print(f"  ❌ 檢查斷鏈錯誤: {e}")
        return False

def check_seo(filepath, filename):
    """檢查SEO問題"""
    print(f"\n🔍 檢查 {filename} SEO問題:")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        # 1. 檢查meta描述
        if '<meta name="description"' not in content:
            issues.append("⚠️ 缺少meta描述 (description)")
        
        # 2. 檢查關鍵字
        if '<meta name="keywords"' not in content:
            issues.append("⚠️ 缺少meta關鍵字 (keywords)")
        
        # 3. 檢查標題長度
        title_match = re.search(r'<title>([^<]+)</title>', content)
        if title_match:
            title = title_match.group(1)
            if len(title) < 10 or len(title) > 60:
                issues.append(f"⚠️ 標題長度不理想: {len(title)} 字符 (建議10-60)")
            else:
                print(f"  ℹ️ 標題長度: {len(title)} 字符")
        
        # 4. 檢查H1標籤
        h1_count = content.count('<h1')
        if h1_count == 0:
            issues.append("❌ 缺少H1標題")
        elif h1_count > 1:
            issues.append(f"⚠️ 多個H1標題: {h1_count} 個")
        else:
            print("  ✅ H1標題正常")
        
        if issues:
            for issue in issues:
                print(f"  {issue}")
            return False
        else:
            print("  ✅ SEO基礎良好")
            return True
            
    except Exception as e:
        print(f"  ❌ 檢查SEO錯誤: {e}")
        return False

def main():
    print(f"🔍 全方位檢查 home.html 和 chapters.html - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    files_to_check = [
        ("home.html", "首頁"),
        ("chapters.html", "章節目錄")
    ]
    
    overall_results = {}
    
    for filename, display_name in files_to_check:
        print(f"\n{'='*60}")
        print(f"📄 檢查 {display_name} ({filename})")
        print(f"{'='*60}")
        
        filepath = os.path.join(NOVEL_DIR, filename)
        
        if not os.path.exists(filepath):
            print(f"❌ 文件不存在: {filename}")
            overall_results[filename] = False
            continue
        
        # 執行所有檢查
        checks = [
            ("HTML結構", check_html_structure(filepath, filename)),
            ("CSS問題", check_css_issues(filepath, filename)),
            ("JavaScript問題", check_javascript_issues(filepath, filename)),
            ("無障礙訪問", check_accessibility(filepath, filename)),
            ("性能問題", check_performance(filepath, filename)),
            ("斷鏈檢查", check_broken_links(filepath, filename)),
            ("SEO問題", check_seo(filepath, filename))
        ]
        
        # 特定頁面檢查
        if filename == "home.html":
            checks.append(("首頁特定問題", check_specific_home_issues()))
        elif filename == "chapters.html":
            checks.append(("章節目錄特定問題", check_specific_chapters_issues()))
        
        # 統計結果
        passed = sum(1 for _, result in checks if result)
        total = len(checks)
        
        overall_results[filename] = passed == total
        
        print(f"\n📊 {display_name} 檢查結果: {passed}/{total} 項通過")
        
        # 顯示失敗的檢查
        failed_checks = [name for name, result in checks if not result]
        if failed_checks:
            print(f"❌ 失敗的檢查: {', '.join(failed_checks)}")
        else:
            print(f"✅ 所有檢查通過！")
    
    # 總結報告
    print(f"\n{'='*60}")
    print("📋 總結報告")
    print(f"{'='*60}")
    
    all_passed = all(overall_results.values())
    
    if all_passed:
        print("🎉 恭喜！所有檢查都通過了！")
        print("✅ home.html - 完整無誤")
        print("✅ chapters.html - 完整無誤")
    else:
        print("⚠️ 發現一些問題需要修復:")
        for filename, passed in overall_results.items():
            status = "✅ 通過" if passed else "❌ 需要修復"
            print(f"  {filename}: {status}")
    
    print(f"\n檢查完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())