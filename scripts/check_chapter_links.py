#!/usr/bin/env python3
"""
檢測所有章節文件的「上一章」和「下一章」鏈接問題
"""

import os
import re
import sys
from datetime import datetime

WORKSPACE = "/home/openclaw/.openclaw/workspace"
NOVEL_DIR = WORKSPACE

def get_all_chapter_files():
    """獲取所有章節文件"""
    chapters = []
    
    for filename in os.listdir(NOVEL_DIR):
        if filename.startswith("chapter-") and filename.endswith(".html"):
            match = re.match(r"chapter-(\d+)\.html", filename)
            if match:
                chapter_num = int(match.group(1))
                chapters.append({
                    "num": chapter_num,
                    "filename": filename,
                    "path": os.path.join(NOVEL_DIR, filename)
                })
    
    # 按章節號排序
    chapters.sort(key=lambda x: x["num"])
    return chapters

def check_chapter_links(chapters):
    """檢查章節鏈接"""
    print("=== 章節鏈接檢測報告 ===\n")
    
    # 創建章節號到文件名的映射
    chapter_map = {chap["num"]: chap["filename"] for chap in chapters}
    max_chapter = max(chapter_map.keys()) if chapter_map else 0
    min_chapter = min(chapter_map.keys()) if chapter_map else 0
    
    print(f"總章節數: {len(chapters)} (第{min_chapter}章到第{max_chapter}章)")
    print(f"排除模板: chapter-0.html (模板文件)\n")
    
    issues = []
    
    for chap in chapters:
        if chap["num"] == 0:  # 跳過模板
            continue
            
        filepath = chap["path"]
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 檢查「上一章」鏈接
            prev_match = re.search(r'<a[^>]*href="([^"]+)"[^>]*>.*上一章.*</a>', content)
            prev_link = prev_match.group(1) if prev_match else None
            
            # 檢查「下一章」鏈接
            next_match = re.search(r'<a[^>]*href="([^"]+)"[^>]*>.*下一章.*</a>', content)
            next_link = next_match.group(1) if next_match else None
            
            # 檢查「返回目錄」鏈接
            toc_match = re.search(r'<a[^>]*href="([^"]+)"[^>]*>.*返回目錄.*</a>', content)
            toc_link = toc_match.group(1) if toc_match else None
            
            # 預期鏈接
            expected_prev = f"chapter-{chap['num']-1}.html" if chap['num'] > 1 else None
            expected_next = f"chapter-{chap['num']+1}.html" if chap['num'] < max_chapter else None
            
            # 檢查問題
            chapter_issues = []
            
            # 檢查上一章
            if chap['num'] == 1:
                # 第1章不應該有上一章
                if prev_link:
                    chapter_issues.append(f"❌ 第1章不應該有「上一章」鏈接，但找到: {prev_link}")
            else:
                if not prev_link:
                    chapter_issues.append(f"❌ 缺少「上一章」鏈接")
                elif prev_link != expected_prev:
                    chapter_issues.append(f"❌ 「上一章」鏈接錯誤: {prev_link} (應為: {expected_prev})")
            
            # 檢查下一章
            if chap['num'] == max_chapter:
                # 最新章節不應該有下一章
                if next_link:
                    chapter_issues.append(f"❌ 第{chap['num']}章是最新章節，不應該有「下一章」鏈接，但找到: {next_link}")
            else:
                if not next_link:
                    chapter_issues.append(f"❌ 缺少「下一章」鏈接")
                elif next_link != expected_next:
                    chapter_issues.append(f"❌ 「下一章」鏈接錯誤: {next_link} (應為: {expected_next})")
            
            # 檢查返回目錄
            if not toc_link:
                chapter_issues.append(f"❌ 缺少「返回目錄」鏈接")
            elif toc_link != "chapters.html":
                chapter_issues.append(f"❌ 「返回目錄」鏈接錯誤: {toc_link} (應為: chapters.html)")
            
            if chapter_issues:
                issues.append({
                    "chapter": chap['num'],
                    "filename": chap['filename'],
                    "issues": chapter_issues
                })
                
        except Exception as e:
            issues.append({
                "chapter": chap['num'],
                "filename": chap['filename'],
                "issues": [f"❌ 讀取文件錯誤: {e}"]
            })
    
    return issues

def check_home_html():
    """檢查首頁的章節鏈接"""
    print("=== 首頁鏈接檢測 ===\n")
    
    home_path = os.path.join(NOVEL_DIR, "home.html")
    
    try:
        with open(home_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查最新章節鏈接
        latest_links = re.findall(r'<a[^>]*href="(chapter-\d+\.html)"[^>]*class="chapter-card"[^>]*>', content)
        
        print(f"首頁最新章節鏈接: {len(latest_links)} 個")
        
        if latest_links:
            print("最新章節鏈接:")
            for link in latest_links:
                print(f"  - {link}")
        
        # 檢查導航鏈接
        nav_links = re.findall(r'<a[^>]*href="([^"]+)"[^>]*class="nav a"[^>]*>', content)
        if nav_links:
            print(f"\n導航鏈接: {len(nav_links)} 個")
        
        return True
        
    except Exception as e:
        print(f"❌ 檢查首頁錯誤: {e}")
        return False

def check_chapters_html():
    """檢查章節目錄的鏈接"""
    print("\n=== 章節目錄鏈接檢測 ===\n")
    
    chapters_path = os.path.join(NOVEL_DIR, "chapters.html")
    
    try:
        with open(chapters_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查章節鏈接
        chapter_links = re.findall(r'<a[^>]*href="(chapter-\d+\.html)"[^>]*class="chapter-item"[^>]*>', content)
        
        print(f"章節目錄鏈接: {len(chapter_links)} 個")
        
        # 檢查是否有重複鏈接
        unique_links = set(chapter_links)
        if len(chapter_links) != len(unique_links):
            print(f"❌ 發現重複鏈接: 總共 {len(chapter_links)} 個鏈接，但只有 {len(unique_links)} 個唯一鏈接")
            
            # 找出重複的鏈接
            from collections import Counter
            link_counts = Counter(chapter_links)
            duplicates = {link: count for link, count in link_counts.items() if count > 1}
            
            if duplicates:
                print("重複的鏈接:")
                for link, count in duplicates.items():
                    print(f"  - {link}: {count} 次")
        
        # 檢查分組按鈕鏈接
        group_buttons = re.findall(r'<a[^>]*href="#group-\d+-\d+"[^>]*class="group-btn"[^>]*>', content)
        print(f"分組按鈕: {len(group_buttons)} 個")
        
        return True
        
    except Exception as e:
        print(f"❌ 檢查章節目錄錯誤: {e}")
        return False

def main():
    print(f"📚 章節鏈接檢測 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 獲取所有章節
    chapters = get_all_chapter_files()
    
    if not chapters:
        print("❌ 沒有找到章節文件")
        return 1
    
    # 檢查章節文件鏈接
    issues = check_chapter_links(chapters)
    
    if issues:
        print(f"\n⚠️ 發現 {len(issues)} 個章節有鏈接問題:\n")
        
        for issue in issues:
            print(f"第{issue['chapter']}章 ({issue['filename']}):")
            for problem in issue['issues']:
                print(f"  {problem}")
            print()
    else:
        print("✅ 所有章節鏈接正確！\n")
    
    # 檢查首頁
    check_home_html()
    
    # 檢查章節目錄
    check_chapters_html()
    
    # 總結
    print("\n" + "="*50)
    print("檢測完成！")
    
    if issues:
        print(f"發現 {len(issues)} 個章節需要修復")
        return 1
    else:
        print("所有鏈接正確無誤！")
        return 0

if __name__ == "__main__":
    sys.exit(main())