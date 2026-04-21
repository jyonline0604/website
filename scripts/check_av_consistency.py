#!/usr/bin/env python3
"""
檢查有聲畫章節一致性
驗證所有有聲畫章節的導航列格式是否統一
"""
import os
import re
import glob

workspace = "/home/openclaw/.openclaw/workspace"
os.chdir(workspace)

# 標準導航列模板（第60章格式）
STANDARD_NAV_PATTERN = r'<nav aria-label="主要導航" class="nav">'

def check_av_file(filename):
    """檢查單個有聲畫文件的一致性"""
    chapter_num = extract_chapter_number(filename)
    if not chapter_num:
        return False, f"無法提取章節號碼: {filename}"
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # 1. 檢查是否有標準導航列
    if STANDARD_NAV_PATTERN not in content:
        issues.append("❌ 缺少標準導航列格式 (aria-label='主要導航')")
    
    # 2. 檢查導航列結構
    nav_match = re.search(r'<nav[^>]*>.*?</nav>', content, re.DOTALL)
    if not nav_match:
        issues.append("❌ 未找到導航列")
        return False, issues
    
    nav_html = nav_match.group(0)
    
    # 3. 檢查必要的鏈接
    required_links = [
        (r'href="chapter-\d+\.html"', "文字版鏈接"),
        (r'href="av-novels\.html"', "目錄鏈接"),
    ]
    
    for pattern, description in required_links:
        if not re.search(pattern, nav_html):
            issues.append(f"❌ 缺少{description}")
    
    # 4. 檢查章節鏈接（根據位置）
    if chapter_num > 1:
        prev_pattern = rf'href="chapter-{chapter_num-1}-av\.html"'
        if not re.search(prev_pattern, nav_html):
            issues.append(f"❌ 缺少上一章鏈接 (應指向 chapter-{chapter_num-1}-av.html)")
    
    if chapter_num < 78:  # 假設78是最後一章
        next_pattern = rf'href="chapter-{chapter_num+1}-av\.html"'
        if not re.search(next_pattern, nav_html):
            issues.append(f"❌ 缺少下一章鏈接 (應指向 chapter-{chapter_num+1}-av.html)")
    
    # 5. 檢查無障礙屬性
    if 'aria-label="主要導航"' not in nav_html:
        issues.append("❌ 缺少aria-label無障礙屬性")
    
    # 6. 檢查class名稱
    if 'class="nav"' not in nav_html:
        issues.append("❌ 缺少class='nav'")
    
    if issues:
        return False, issues
    else:
        return True, ["✅ 導航列格式正確"]

def extract_chapter_number(filename):
    """從文件名中提取章節號碼"""
    match = re.search(r'chapter-(\d+)-av\.html', filename)
    if match:
        return int(match.group(1))
    return None

def main():
    """主程序"""
    print("=" * 80)
    print("有聲畫章節一致性檢查")
    print("驗證所有有聲畫章節的導航列格式是否統一")
    print("=" * 80)
    
    # 查找所有有聲畫章節文件
    av_files = glob.glob("chapter-*-av.html")
    av_files.sort(key=lambda x: extract_chapter_number(x) or 0)
    
    print(f"找到 {len(av_files)} 個有聲畫章節文件")
    print()
    
    total_issues = 0
    passed_count = 0
    failed_count = 0
    
    for filename in av_files:
        chapter_num = extract_chapter_number(filename)
        print(f"🔍 檢查第{chapter_num}章: {filename}")
        
        passed, results = check_av_file(filename)
        
        if passed:
            passed_count += 1
            print(f"  {results[0]}")
        else:
            failed_count += 1
            for issue in results:
                print(f"  {issue}")
                total_issues += 1
        
        print()
    
    # 總結報告
    print("=" * 80)
    print("一致性檢查總結")
    print("=" * 80)
    print(f"總文件數: {len(av_files)}")
    print(f"通過檢查: {passed_count}")
    print(f"未通過: {failed_count}")
    print(f"總問題數: {total_issues}")
    print()
    
    if total_issues == 0:
        print("✅ 所有有聲畫章節導航列格式一致！")
        return True
    else:
        print("⚠️  發現不一致的導航列格式")
        print()
        print("修復建議:")
        print("1. 運行統一腳本: python3 scripts/unify_av_navigation.py")
        print("2. 檢查第60章格式作為標準")
        print("3. 確保新生成章節使用標準模板")
        return False

def check_single_chapter(chapter_num):
    """檢查單個章節"""
    filename = f"chapter-{chapter_num}-av.html"
    if not os.path.exists(filename):
        print(f"錯誤: 找不到文件 {filename}")
        return False
    
    print(f"🔍 檢查第{chapter_num}章: {filename}")
    passed, results = check_av_file(filename)
    
    if passed:
        print(f"  {results[0]}")
    else:
        for issue in results:
            print(f"  {issue}")
    
    return passed

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 檢查單個章節
        try:
            chapter_num = int(sys.argv[1])
            check_single_chapter(chapter_num)
        except ValueError:
            print("錯誤: 章節號碼必須是數字")
            sys.exit(1)
    else:
        # 檢查所有章節
        success = main()
        sys.exit(0 if success else 1)