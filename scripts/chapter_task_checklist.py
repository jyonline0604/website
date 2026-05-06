#!/usr/bin/env python3
"""
章節處理任務強制檢查清單 v2

每次處理新章節前，必須完成並通過此檢查清單。
沒有通過檢查，無法繼續執行任務。

【2026-05-06 更新 v2.2】
- 新增：assets/chapters-data.json 同步檢查（每次章節變更必須重新生成）
- 新增：三處章節數量同步：author.html + chapters.html meta + chapters-data.json
- 更新：默認章節數從 460 改為 500
"""

import os
import re
import sys
from datetime import datetime

WORKSPACE = "/home/openclaw/.openclaw/workspace"
INBOUND_DIR = "/home/openclaw/.openclaw/media/inbound"
SKILL_PATH = "/home/openclaw/.openclaw/skills/novel-site-standards/SKILL.md"
TEMPLATE_PATH = os.path.join(WORKSPACE, "chapter-template.html")

# 簡體→繁體 轉換表（常見問題字符）
SIMPLIFY = {
    '叶尘':'葉塵','灵':'靈','万':'萬','时':'時',
    '经':'經','会':'會','说':'說','请':'請','话':'話','开':'開','关':'關','门':'門',
    '问':'問','学':'學','断':'斷','炼':'煉','苏':'蘇','陈':'陳','赵':'趙','张':'張',
    '许':'許','萧':'蕭','梦':'夢','觉':'覺','终':'終','从':'從','见':'見','间':'間',
    '场':'場','广':'廣','应':'應','当':'當','设':'設','进':'進','远':'遠','运':'運',
    '连':'連','还':'還','过':'過','达':'達','亿':'億','来':'來','无':'無','个':'個',
    '们':'們','国':'國','发':'發','后':'後','让':'讓','给':'給','着':'著','却':'卻',
    '刘':'劉','杨':'楊','周':'週','马':'馬','郑':'鄭','东':'東','变':'變','难':'難',
    '电':'電','条':'條','处':'處','总':'總','长':'長','旧':'舊','极':'極','体':'體',
    '里':'裡'
}

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
        # 匹配 第四百XX章_標題---UUID.txt 格式
        if f.startswith("第四百") and f.endswith(".txt"):
            m = re.search(r'第四百([零一二三四五六七八九十百千萬\d]+)章_(.+?)---', f)
            if m:
                cn = m.group(1)
                # 轉換中文數字
                num = 0
                if cn == '四十': num = 40
                elif cn == '四十一': num = 41
                # ... (完整轉換)
                local_map = {
                    '四十': 40, '四十一': 41, '四十二': 42, '四十三': 43, '四十四': 44,
                    '四十五': 45, '四十六': 46, '四十七': 47, '四十八': 48, '四十九': 49,
                    '五十': 50, '五十一': 51, '五十二': 52, '五十三': 53, '五十四': 54,
                    '五十五': 55, '五十六': 56, '五十七': 57, '五十八': 58, '五十九': 59,
                    '六十': 60
                }
                if cn in local_map:
                    global_num = 400 + local_map[cn]
                    if global_num not in existing:
                        title = m.group(2)
                        new_chapters.append((global_num, title, f))
    
    return sorted(new_chapters)

def check_simplified_chars(filepath):
    """檢查文件是否含有簡體字符"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    found = []
    for simp, trad in SIMPLIFY.items():
        if simp in content:
            found.append(simp)
    return found

def verify_html_title(ch_num, expected_title):
    """驗證HTML標題是否與預期匹配"""
    html_file = os.path.join(WORKSPACE, f"chapter-{ch_num}.html")
    if not os.path.exists(html_file):
        return False, "HTML文件不存在"
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取 <title> 標籤
    m = re.search(r'<title>第[零一二三四五六七八九十百千萬\d]+章\s*[·:：]\s*(.+?)</title>', content)
    if not m:
        return False, "無法提取HTML標題"
    
    html_title = m.group(1).strip()
    if html_title != expected_title:
        return False, f"標題不匹配！預期：{expected_title}，實際：{html_title}"
    
    return True, "OK"

def verify_home_chapter_cards():
    """驗證home.html的最新章節卡片標題是否正確"""
    home_file = os.path.join(WORKSPACE, "home.html")
    if not os.path.exists(home_file):
        return False, "home.html不存在"
    
    with open(home_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 檢查是否顯示「第XXX章」而非「標題」
    # 問題跡象：<h3 class="chapter-title">第460章</h3>
    bad_pattern = re.compile(r'<h3 class="chapter-title">第[零一二三四五六七八九十百千萬\d]+章</h3>')
    if bad_pattern.search(content):
        return False, "home.html顯示「第XXX章」而非章節標題！"
    
    # 確認有正確的標題
    good_pattern = re.compile(r'<h3 class="chapter-title">[^第][^<]+</h3>')
    if not good_pattern.search(content):
        return False, "home.html找不到正確的章節標題"
    
    return True, "OK"

def print_checklist(new_chapters_info):
    """印出強制檢查清單"""
    print("=" * 60)
    print("📋 章節處理任務 - 強制檢查清單 v2")
    print("=" * 60)
    print()
    print(f"📚 本次待處理：{len(new_chapters_info)} 個章節")
    for ch_num, title, fname in new_chapters_info[:3]:
        print(f"   CH{ch_num}: {title}")
    if len(new_chapters_info) > 3:
        print(f"   ... 還有 {len(new_chapters_info)-3} 個")
    print()
    print("在開始處理新章節前，請確認以下項目：")
    print()
    print("【1】SKILL.md 已讀取")
    print("    □ 已閱讀 SKILL.md")
    print("    □ 確認使用 chapter-template.html 作為模板")
    print()
    print("【2】源文件格式檢查")
    print("    □ 第一行為『第四百XX章 標題』格式（無#前綴也行）")
    print("    □ 無簡體字符（葉尘、灵、周、里 等）")
    print("    □ 標點符號完整")
    print()
    print("【3】生成HTML後【必須驗證】")
    print("    □ HTML結構正確（1個<html>、1個</html>、1個<h1>）")
    print("    □ <title> 標題與 inbound 文件名匹配")
    print("    □ 驗證命令：")
    print("      grep '<title>' chapter-XX.html")
    print()
    print("【4】生成home.html後【必須驗證】")
    print("    □ 章節卡片顯示標題而非「第XXX章」")
    print("    □ 驗證命令：")
    print("      grep 'chapter-title' home.html | head -5")
    print("    □ 正確應該顯示：<h3 class=\"chapter-title\">萬古荒漠</h3>")
    print("    □ 錯誤會顯示：<h3 class=\"chapter-title\">第460章</h3>")
    print()
    print("【5】完成後必做")
    print("    □ 更新 chapters.html")
    print("    □ 更新 home.html")
    print("    □ 更新 SKILL.md 並同步到 Second-brain 和 Max-backup")
    print()
    print("【6】⚠️ 四處章節數量同步（必須全部更新）")
    print("    □ index.html: meta description + 文字描述 + 統計數字 (500+)")
    print("    □ home.html: meta description + JSON-LD numberOfPages (500)")
    print("    □ chapters.html meta: description/og:description/twitter:description (500章)")
    print("    □ author.html: <span id=\"chapterCount\">500</span>")
    print("    □ assets/chapters-data.json: 完整重新生成（不能只追加）")
    print("    □ 驗證命令：grep '500\|chapterCount\"\>500' index.html home.html author.html chapters.html")
    print()
    print("【7】JSON 檔案注意事項")
    print("    ⚠️ assets/chapters-data.json 每次必須完整重新生成，不能只修改部分！")
    print("    ⚠️ 包含所有章節 CH1-CH500，不能有遺漏")
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
    for ch_num, title, fname in new_chapters[:5]:
        print(f"   CH{ch_num}: {title}")
    if len(new_chapters) > 5:
        print(f"   ... 還有 {len(new_chapters) - 5} 個")
    print()
    
    if not print_checklist(new_chapters):
        print("❌ 檢查未通過，任務取消")
        return False
    
    print("✅ 檢查通過，開始處理章節...")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
