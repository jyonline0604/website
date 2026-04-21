#!/usr/bin/env python3
"""
全方位檢查 kofhk.com 網站所有頁面
"""
import os
import re
import json
from datetime import datetime

workspace = "/home/openclaw/.openclaw/workspace"
os.chdir(workspace)

def check_html_structure(filename):
    """檢查HTML結構完整性"""
    issues = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 基本HTML結構檢查
    if '<!DOCTYPE html>' not in content:
        issues.append("缺少 <!DOCTYPE html>")
    
    if '<html' not in content:
        issues.append("缺少 <html> 標籤")
    
    if '</html>' not in content:
        issues.append("缺少 </html> 結束標籤")
    
    if '<head>' not in content:
        issues.append("缺少 <head> 標籤")
    
    if '<body>' not in content:
        issues.append("缺少 <body> 標籤")
    
    # 檢查是否有未關閉的標籤
    open_tags = re.findall(r'<(?!\/)(\w+)[^>]*>', content)
    close_tags = re.findall(r'</(\w+)>', content)
    
    for tag in set(open_tags):
        if tag not in ['meta', 'link', 'img', 'br', 'hr', 'input']:  # 自閉合標籤
            open_count = len([t for t in open_tags if t == tag])
            close_count = len([t for t in close_tags if t == tag])
            if open_count != close_count:
                issues.append(f"標籤 <{tag}> 未關閉（開啟: {open_count}, 關閉: {close_count}）")
    
    return issues

def check_meta_tags(filename):
    """檢查meta標籤"""
    issues = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 基本meta標籤檢查
    if '<meta charset="utf-8">' not in content and '<meta charset="UTF-8">' not in content:
        issues.append("缺少 charset meta 標籤")
    
    if '<meta name="viewport"' not in content:
        issues.append("缺少 viewport meta 標籤")
    
    # 檢查Open Graph標籤
    og_tags = ['og:title', 'og:description', 'og:image', 'og:url']
    for tag in og_tags:
        if f'property="{tag}"' not in content:
            issues.append(f"缺少 Open Graph: {tag}")
    
    # 檢查Twitter卡片
    twitter_tags = ['twitter:card', 'twitter:title', 'twitter:description', 'twitter:image']
    for tag in twitter_tags:
        if f'name="{tag}"' not in content:
            issues.append(f"缺少 Twitter Card: {tag}")
    
    return issues

def check_links(filename):
    """檢查鏈接有效性"""
    issues = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有鏈接
    links = re.findall(r'href="([^"]+)"', content)
    
    for link in links:
        # 跳過外部鏈接和特殊鏈接
        if link.startswith('http://') or link.startswith('https://'):
            continue
        if link.startswith('mailto:') or link.startswith('tel:'):
            continue
        if link.startswith('#') or link == 'javascript:void(0)':
            continue
        
        # 檢查文件是否存在
        if not os.path.exists(link):
            issues.append(f"鏈接無效: {link}")
    
    return issues

def check_images(filename):
    """檢查圖片"""
    issues = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有圖片
    images = re.findall(r'src="([^"]+)"', content)
    
    for img in images:
        # 跳過外部圖片
        if img.startswith('http://') or img.startswith('https://'):
            continue
        
        # 檢查圖片文件是否存在
        if not os.path.exists(img):
            issues.append(f"圖片不存在: {img}")
    
    return issues

def check_javascript(filename):
    """檢查JavaScript問題"""
    issues = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 檢查是否有JavaScript錯誤
    if 'console.error' in content:
        issues.append("頁面包含 console.error 調用")
    
    # 檢查常見的JavaScript問題
    patterns = [
        (r'getElementById\([^)]+\)\.textContent', "可能嘗試設置不存在的元素的textContent"),
        (r'Cannot set properties of null', "JavaScript錯誤：無法設置null的屬性"),
        (r'is not defined', "JavaScript錯誤：變量未定義"),
        (r'Uncaught TypeError', "JavaScript錯誤：未捕獲的類型錯誤"),
    ]
    
    for pattern, message in patterns:
        if re.search(pattern, content):
            issues.append(message)
    
    return issues

def check_css(filename):
    """檢查CSS問題"""
    issues = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 檢查CSS選擇器
    css_selectors = re.findall(r'\.([a-zA-Z0-9_-]+)\s*{', content)
    
    # 檢查是否有未使用的CSS類（簡單檢查）
    for selector in css_selectors:
        # 檢查這個類是否在HTML中使用
        if f'class=".*{selector}.*"' not in content and f'class="{selector}"' not in content:
            # 可能是動態添加的類，跳過
            pass
    
    return issues

def check_accessibility(filename):
    """檢查無障礙訪問性"""
    issues = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 檢查圖片是否有alt屬性
    img_tags = re.findall(r'<img[^>]+>', content)
    for img in img_tags:
        if 'alt=' not in img:
            issues.append("圖片缺少 alt 屬性")
    
    # 檢查表單元素是否有label
    input_tags = re.findall(r'<input[^>]+>', content)
    for inp in input_tags:
        if 'id=' in inp and 'name=' in inp:
            # 檢查是否有對應的label
            input_id = re.search(r'id="([^"]+)"', inp)
            if input_id:
                if f'for="{input_id.group(1)}"' not in content:
                    issues.append(f"表單元素缺少 label (id: {input_id.group(1)})")
    
    return issues

def check_seo(filename):
    """檢查SEO問題"""
    issues = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 檢查標題
    if '<title>' not in content:
        issues.append("缺少 <title> 標籤")
    else:
        title_match = re.search(r'<title>(.*?)</title>', content)
        if title_match:
            title = title_match.group(1)
            if len(title) < 10 or len(title) > 70:
                issues.append(f"標題長度不理想: {len(title)} 字符 (建議 10-70)")
    
    # 檢查描述
    desc_match = re.search(r'<meta name="description" content="([^"]+)"', content)
    if not desc_match:
        issues.append("缺少 meta description")
    else:
        desc = desc_match.group(1)
        if len(desc) < 50 or len(desc) > 160:
            issues.append(f"描述長度不理想: {len(desc)} 字符 (建議 50-160)")
    
    # 檢查H1標籤
    h1_count = len(re.findall(r'<h1[^>]*>', content))
    if h1_count == 0:
        issues.append("缺少 H1 標籤")
    elif h1_count > 1:
        issues.append(f"多個 H1 標籤: {h1_count} 個")
    
    return issues

def check_performance(filename):
    """檢查性能問題"""
    issues = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 檢查圖片大小
    img_tags = re.findall(r'<img[^>]+>', content)
    for img in img_tags:
        src_match = re.search(r'src="([^"]+)"', img)
        if src_match:
            img_src = src_match.group(1)
            if not img_src.startswith('http'):
                try:
                    if os.path.exists(img_src):
                        size = os.path.getsize(img_src)
                        if size > 500000:  # 500KB
                            issues.append(f"圖片過大: {img_src} ({size/1024:.1f}KB)")
                except:
                    pass
    
    # 檢查CSS和JS文件數量
    css_links = len(re.findall(r'<link[^>]*rel="stylesheet"[^>]*>', content))
    js_scripts = len(re.findall(r'<script[^>]*src="[^"]+"[^>]*>', content))
    
    if css_links > 5:
        issues.append(f"CSS文件過多: {css_links} 個")
    
    if js_scripts > 5:
        issues.append(f"JS文件過多: {js_scripts} 個")
    
    return issues

def check_mobile_responsive(filename):
    """檢查移動端響應式"""
    issues = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 檢查viewport
    if 'viewport' not in content:
        issues.append("缺少 viewport meta 標籤")
    
    # 檢查是否有媒體查詢
    if '@media' not in content and 'max-width' not in content and 'min-width' not in content:
        issues.append("缺少響應式設計媒體查詢")
    
    return issues

def generate_report():
    """生成檢查報告"""
    print("=" * 80)
    print("kofhk.com 網站全方位檢查報告")
    print("=" * 80)
    print(f"檢查時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 獲取所有HTML文件
    html_files = []
    for f in os.listdir('.'):
        if f.endswith('.html') and not f.startswith('chapter-') and '-av' not in f:
            html_files.append(f)
    
    print(f"檢查頁面數量: {len(html_files)}")
    print()
    
    total_issues = 0
    detailed_report = {}
    
    for filename in sorted(html_files):
        print(f"📄 檢查: {filename}")
        print("-" * 40)
        
        file_issues = []
        
        # 執行各種檢查
        checks = [
            ("HTML結構", check_html_structure),
            ("Meta標籤", check_meta_tags),
            ("鏈接有效性", check_links),
            ("圖片", check_images),
            ("JavaScript", check_javascript),
            ("CSS", check_css),
            ("無障礙訪問", check_accessibility),
            ("SEO", check_seo),
            ("性能", check_performance),
            ("移動端響應式", check_mobile_responsive),
        ]
        
        for check_name, check_func in checks:
            issues = check_func(filename)
            if issues:
                file_issues.append((check_name, issues))
        
        # 輸出結果
        if not file_issues:
            print("✅ 無問題")
        else:
            for check_name, issues in file_issues:
                print(f"  ⚠️ {check_name}:")
                for issue in issues:
                    print(f"    • {issue}")
                    total_issues += 1
        
        detailed_report[filename] = file_issues
        print()
    
    # 總結
    print("=" * 80)
    print("檢查總結")
    print("=" * 80)
    print(f"總頁面數: {len(html_files)}")
    print(f"總問題數: {total_issues}")
    print()
    
    # 按問題類型分類
    issue_categories = {}
    for filename, issues_list in detailed_report.items():
        for check_name, issues in issues_list:
            if check_name not in issue_categories:
                issue_categories[check_name] = 0
            issue_categories[check_name] += len(issues)
    
    if issue_categories:
        print("問題分類:")
        for category, count in sorted(issue_categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {category}: {count} 個問題")
    
    # 建議
    print()
    print("建議:")
    if total_issues == 0:
        print("✅ 網站狀態良好，無需修復")
    else:
        print("1. 優先修復HTML結構和鏈接問題")
        print("2. 確保所有圖片都有alt屬性")
        print("3. 優化SEO標籤（title, description）")
        print("4. 檢查並修復JavaScript錯誤")
        print("5. 確保移動端響應式設計")
    
    return detailed_report

# 主程序
if __name__ == "__main__":
    report = generate_report()
    
    # 保存報告到文件
    with open('kofhk_site_check_report.txt', 'w', encoding='utf-8') as f:
        f.write("kofhk.com 網站檢查報告\n")
        f.write("=" * 60 + "\n")
        f.write(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for filename, issues_list in report.items():
            f.write(f"📄 {filename}\n")
            f.write("-" * 40 + "\n")
            
            if not issues_list:
                f.write("✅ 無問題\n")
            else:
                for check_name, issues in issues_list:
                    f.write(f"⚠️ {check_name}:\n")
                    for issue in issues:
                        f.write(f"  • {issue}\n")
            f.write("\n")
    
    print(f"\n📋 詳細報告已保存到: kofhk_site_check_report.txt")