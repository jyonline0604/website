#!/usr/bin/env python3
"""
章節處理任務強制檢查清單

每次處理新章節前，必須完成並通過此檢查清單。
沒有通過檢查，無法繼續執行任務。
"""

import os
import sys
from datetime import datetime

WORKSPACE = "/home/openclaw/.openclaw/workspace"
INBOUND_DIR = "/home/openclaw/.openclaw/media/inbound"
SKILL_PATH = "/home/openclaw/.openclaw/skills/novel-site-standards/SKILL.md"

def get_new_chapters():
    """檢查有待處理的新章節"""
    existing = set()
    for f in os.listdir(WORKSPACE):
        if f.startswith("chapter-") and f.endswith(".html"):
            m = f.replace("chapter-", "").replace(".html", "")
            if m.isdigit():
                existing.add(int(m))
    
    new_chapters = []
    for f in os.listdir(INBOUND_DIR):
        if f.startswith("第") and f.endswith(".txt"):
            import re
            m = re.search(r'第(\d+)章', f)
            if m:
                ch_num = int(m.group(1))
                if ch_num not in existing:
                    new_chapters.append((ch_num, f))
    
    return sorted(new_chapters)

def print_checklist():
    """印出強制檢查清單"""
    print("=" * 60)
    print("📋 章節處理任務 - 強制檢查清單")
    print("=" * 60)
    print()
    print("在開始處理新章節前，請確認以下項目：")
    print()
    print("【1】SKILL.md 已讀取")
    print("    □ 已閱讀 SKILL.md")
    print("    □ 已確認使用 chapter-template.html 作為模板")
    print()
    print("【2】源文件格式檢查")
    print("    □ 第一行為 '# 第X章 · 標題' 格式")
    print("    □ 無簡體字符（葉尘、灵等）")
    print()
    print("【3】模板確認")
    print("    □ 使用 chapter-template.html")
    print("    □ 不使用 convert_novel_to_html.py 的內嵌模板")
    print()
    print("【4】生成後檢查")
    print("    □ HTML結構正確（1個<html>、1個</html>、1個<h1>）")
    print("    □ 有 top-bar 導航列")
    print("    □ 有『返回目錄』連結")
    print("    □ 有字體/主題設定按鈕")
    print()
    print("【5】完成後必做")
    print("    □ 更新 chapters.html")
    print("    □ 更新 home.html")
    print("    □ 更新 SKILL.md 並同步到 Second-brain 和 Max-backup")
    print()
    print("【6】⚠️ 三處章節數量同步（忘記了會被責怪）")
    print("    □ author.html: <span id=\"chapterCount\">280</span>")
    print("    □ chapters.html meta: 完整收錄280章")
    print("    □ chapters.html JSON-LD: \"numberOfItems\": 280")
    print()
    print("=" * 60)
    print()
    
    response = input("請輸入『我已確認』開始執行任務：").strip()
    return response == "我已確認"

def main():
    new_chapters = get_new_chapters()
    
    if not new_chapters:
        print("✅ 沒有發現待處理的新章節")
        return True
    
    print(f"📚 發現 {len(new_chapters)} 個新章節待處理：")
    for ch_num, filename in new_chapters[:5]:
        print(f"   - 第{ch_num}章：{filename}")
    if len(new_chapters) > 5:
        print(f"   ... 還有 {len(new_chapters) - 5} 個")
    print()
    
    if not print_checklist():
        print("❌ 檢查未通過，任務取消")
        return False
    
    print("✅ 檢查通過，開始處理章節...")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
