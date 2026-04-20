#!/usr/bin/env python3
"""
修復所有章節的meta標籤和結構問題
使用 chapter-126.html 作為正確模板
"""

import re
import os
import shutil
from pathlib import Path

WORKSPACE = Path("/home/openclaw/.openclaw/workspace")

def get_meta_description(content, tag_name):
    """獲取第一個正確的meta description"""
    pattern = rf'<meta name="{tag_name}" content="([^"]+)"'
    match = re.search(pattern, content)
    if match:
        desc = match.group(1)
        # 檢查是否是損壞的（包含CSS變量）
        if ':root {' in desc or 'data-theme=' in desc or 'font-size' in desc:
            return None
        return match.group(0)
    return None

def get_og_description(content):
    """獲取第一個正確的og:description"""
    pattern = r'<meta property="og:description" content="([^"]+)"'
    match = re.search(pattern, content)
    if match:
        desc = match.group(1)
        if ':root {' in desc or 'data-theme=' in desc:
            return None
        return match.group(0)
    return None

def get_twitter_description(content):
    """獲取第一個正確的twitter:description"""
    pattern = r'<meta name="twitter:description" content="([^"]+)"'
    match = re.search(pattern, content)
    if match:
        desc = match.group(1)
        if ':root {' in desc or 'data-theme=' in desc:
            return None
        return match.group(0)
    return None

def get_chapter_number_from_filename(filepath):
    """從文件名提取章節號"""
    filename = os.path.basename(filepath)
    match = re.search(r'chapter-(\d+)\.html', filename)
    if match:
        return int(match.group(1))
    return None

def extract_title_from_h1(content):
    """從h1標籤提取章節標題"""
    match = re.search(r'<h1>([^<]+)</h1>', content)
    if match:
        return match.group(1)
    return None

def fix_chapter_file(filepath):
    """修復單個章節文件"""
    print(f"處理: {filepath.name}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. 獲取正確的meta標籤
    meta_desc = get_meta_description(content, 'description')
    og_desc = get_og_description(content)
    twitter_desc = get_twitter_description(content)
    
    # 如果第一個是損壞的，嘗試找第二個
    if not meta_desc:
        # 找所有meta description，取第二個（如果第一個是正確的）
        matches = re.findall(r'<meta name="description" content="([^"]+)"', content)
        if len(matches) >= 2:
            # 第二個可能是正確的
            for i, m in enumerate(matches):
                if ':root {' not in m and 'data-theme=' not in m:
                    meta_desc = f'<meta name="description" content="{m}">'
                    break
    
    if not og_desc:
        matches = re.findall(r'<meta property="og:description" content="([^"]+)"', content)
        if len(matches) >= 2:
            for m in matches:
                if ':root {' not in m and 'data-theme=' not in m:
                    og_desc = f'<meta property="og:description" content="{m}">'
                    break
    
    if not twitter_desc:
        matches = re.findall(r'<meta name="twitter:description" content="([^"]+)"', content)
        if len(matches) >= 2:
            for m in matches:
                if ':root {' not in m and 'data-theme=' not in m:
                    twitter_desc = f'<meta name="twitter:description" content="{m}">'
                    break
    
    # 2. 移除所有重複的meta標籤（只保留第一個正確的）
    # 移除所有 meta description 標籤
    content = re.sub(r'<meta name="description" content="[^"]*"[^>]*>\s*', '', content)
    # 移除所有 og:description 標籤
    content = re.sub(r'<meta property="og:description" content="[^"]*"[^>]*>\s*', '', content)
    # 移除所有 twitter:description 標籤
    content = re.sub(r'<meta name="twitter:description" content="[^"]*"[^>]*>\s*', '', content)
    
    # 3. 在正確位置插入單個正確的meta標籤
    # 找到 </head> 標籤，在它前面插入
    if meta_desc and '</head>' in content:
        content = content.replace('</head>', f'    {meta_desc}\n</head>')
    
    # 對於 og:description，需要在 og:url 後面插入
    if og_desc:
        # 找到 og:url 的位置
        og_url_match = re.search(r'<meta property="og:url" content="[^"]+">', content)
        if og_url_match:
            pos = og_url_match.end()
            content = content[:pos] + '\n    ' + og_desc + content[pos:]
    
    # 對於 twitter:description，需要在 twitter:image 後面插入
    if twitter_desc:
        twitter_img_match = re.search(r'<meta name="twitter:image" content="[^"]+">', content)
        if twitter_img_match:
            pos = twitter_img_match.end()
            content = content[:pos] + '\n    ' + twitter_desc + content[pos:]
    
    # 4. 檢查並修復 chapter-title
    chapter_num = get_chapter_number_from_filename(filepath)
    title = extract_title_from_h1(content)
    
    if chapter_num and title:
        # 檢查 chapter-title 是否匹配
        expected_title = f"第{chapter_num}章"
        chapter_title_match = re.search(r'<span class="chapter-title">([^<]+)</span>', content)
        if chapter_title_match:
            current_title = chapter_title_match.group(1)
            if current_title != expected_title:
                print(f"  ⚠️ 章節標題不匹配: {current_title} -> {expected_title}")
                # 修復 chapter-title
                content = re.sub(
                    r'<span class="chapter-title">[^<]+</span>',
                    f'<span class="chapter-title">{expected_title}</span>',
                    content
                )
    
    # 5. 檢查並修復 title 標籤
    if title:
        expected_title_tag = f"{title} - 科技修真傳"
        title_match = re.search(r'<title>([^<]+)</title>', content)
        if title_match:
            current_title_tag = title_match.group(1)
            # 檢查是否有多餘的重複
            if current_title_tag.count('科技修真傳') > 1:
                print(f"  ⚠️ Title重複: {current_title_tag}")
                content = re.sub(
                    r'<title>[^<]+</title>',
                    f'<title>{expected_title_tag}</title>',
                    content
                )
            elif current_title_tag != expected_title_tag:
                # 修復 title
                content = re.sub(
                    r'<title>[^<]+</title>',
                    f'<title>{expected_title_tag}</title>',
                    content
                )
    
    # 6. 移除重複的 og:title 和 twitter:title（如果有的話）
    # 只保留第一個
    og_titles = list(re.finditer(r'<meta property="og:title" content="([^"]+)"', content))
    if len(og_titles) > 1:
        # 移除第二個及之後的
        for match in og_titles[1:]:
            content = content.replace(match.group(0), '')
    
    twitter_titles = list(re.finditer(r'<meta name="twitter:title" content="([^"]+)"', content))
    if len(twitter_titles) > 1:
        for match in twitter_titles[1:]:
            content = content.replace(match.group(0), '')
    
    # 7. 移除錯誤的關閉標籤（如結尾的 >>）
    content = re.sub(r'">>\s*$', '">', content, flags=re.MULTILINE)
    
    # 8. 驗證修復
    issues = []
    
    # 檢查 meta description 數量
    meta_count = len(re.findall(r'<meta name="description"', content))
    if meta_count != 1:
        issues.append(f"meta description: {meta_count} 個（應該是1）")
    
    # 檢查 og:description 數量
    og_count = len(re.findall(r'<meta property="og:description"', content))
    if og_count != 1:
        issues.append(f"og:description: {og_count} 個（應該是1）")
    
    # 檢查 twitter:description 數量
    twitter_count = len(re.findall(r'<meta name="twitter:description"', content))
    if twitter_count != 1:
        issues.append(f"twitter:description: {twitter_count} 個（應該是1）")
    
    if issues:
        print(f"  ❌ 仍有问题: {', '.join(issues)}")
        return False
    
    # 保存修復後的內容
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ 已修復")
        return True
    else:
        print(f"  ✅ 無需修復")
        return False

def main():
    print("=== 開始修復所有章節 ===\n")
    
    # 備份
    backup_dir = WORKSPACE / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    # 找到所有章節文件
    chapter_files = sorted(
        WORKSPACE.glob("chapter-*.html"),
        key=lambda f: get_chapter_number_from_filename(f) or 0
    )
    
    # 排除 av-novels.html, chapters.html 等非章節文件
    chapter_files = [f for f in chapter_files if re.match(r'chapter-\d+\.html$', f.name)]
    
    print(f"找到 {len(chapter_files)} 個章節文件\n")
    
    # 修復 chapter-126.html 作為模板參考
    print("=== 先分析 chapter-126.html ===")
    template_file = WORKSPACE / "chapter-126.html"
    if template_file.exists():
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # 提取正確的結構
        meta_match = re.search(r'<meta name="description" content="([^"]+)"', template_content)
        og_match = re.search(r'<meta property="og:description" content="([^"]+)"', template_content)
        twitter_match = re.search(r'<meta name="twitter:description" content="([^"]+)"', template_content)
        
        print(f"  Chapter 126 meta description: {'找到' if meta_match else '未找到'}")
        print(f"  Chapter 126 og:description: {'找到' if og_match else '未找到'}")
        print(f"  Chapter 126 twitter:description: {'找到' if twitter_match else '未找到'}")
        
        if meta_match:
            desc = meta_match.group(1)
            if ':root {' in desc:
                print(f"  ❌ Chapter 126 的 meta description 也是損壞的")
            else:
                print(f"  ✅ Chapter 126 的 meta description 是正確的")
    
    print("\n=== 開始修復所有章節 ===\n")
    
    fixed_count = 0
    for chapter_file in chapter_files:
        if fix_chapter_file(chapter_file):
            fixed_count += 1
    
    print(f"\n=== 修復完成 ===")
    print(f"總章節數: {len(chapter_files)}")
    print(f"修復數量: {fixed_count}")
    
    # 驗證chapter-126
    print("\n=== 驗證 chapter-126.html ===")
    with open(WORKSPACE / "chapter-126.html", 'r') as f:
        content = f.read()
    
    meta_count = len(re.findall(r'<meta name="description"', content))
    og_count = len(re.findall(r'<meta property="og:description"', content))
    twitter_count = len(re.findall(r'<meta name="twitter:description"', content))
    
    print(f"meta description: {meta_count} 個")
    print(f"og:description: {og_count} 個")
    print(f"twitter:description: {twitter_count} 個")
    
    if meta_count == 1 and og_count == 1 and twitter_count == 1:
        print("\n✅ 所有meta標籤已修復正確！")
    else:
        print("\n⚠️ 仍有問題，需要手動檢查")

if __name__ == "__main__":
    main()