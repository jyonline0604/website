#!/usr/bin/env python3
"""
《萬古塵埃》批量章節生成器
使用 DeepSeek API 生成完整章節
"""

import os
import sys
import time
import re

sys.path.append("/home/openclaw/.openclaw/workspace/scripts")
from ai_multimodel import MultiModelAI

OUTPUT_DIR = "/home/openclaw/.openclaw/workspace/research"
SETTINGS_FILE = "/home/openclaw/.openclaw/workspace/research/wangu-chenai-settings.md"

def get_settings():
    with open(SETTINGS_FILE, "r") as f:
        return f.read()

def build_system_prompt():
    settings = get_settings()
    return f"""你是《萬古塵埃》小說作者。小說設定如下：

{settings[:2000]}

寫作要求：
1. 每章3000+中文字（至少要3500字符以上）
2. 書面中文，有畫面感、節奏明快
3. 每章結尾要有鉤子
4. 融合凡人修仙傳的穩步升級感、仙逆的情感衝擊、遮天的宏大格局
5. 章節內要有具體場景描寫、戰鬥細節、心理活動"""

def generate_chapter(ai, chapter_num, title, outline, prev_chapter_summary=""):
    """生成單一章節"""
    
    prompt = f"""請生成《萬古塵埃》第{chapter_num}章「{title}」。

本章大綱：{outline}

{prev_chapter_summary}

要求：
- 正文至少3000中文字
- 使用「# 第{chapter_num}章 {title}」作為標題
- 結尾要有懸念鉤子
- 直接輸出正文，不要有任何說明文字"""

    system_prompt = build_system_prompt()
    
    # 嘗試 DeepSeek
    content = ai.call_deepseek(prompt, system_prompt, max_tokens=6000)
    if content:
        return content
    
    # 備用：OpenRouter
    content = ai.call_openrouter(prompt, system_prompt, max_tokens=6000)
    if content:
        return content
    
    return None

def count_chinese(text):
    return sum(1 for c in text if '\u4e00' <= c <= '\u9fff')

def save_chapter(chapter_num, content):
    path = os.path.join(OUTPUT_DIR, f"chapter-{chapter_num}.md")
    with open(path, "w") as f:
        f.write(content)
    chars = count_chinese(content)
    print(f"✅ 第{chapter_num}章 保存 ({chars}字)")
    return chars

def main():
    ai = MultiModelAI()
    
    # 批量定義 (第6-35章)
    batches = [
        # (start, end, prev_summary)
        (6, 10, "第5章結尾：葉塵發現妖獸山谷，準備深入探索"),
        (11, 15, "第10章結尾：葉塵擊敗山谷妖獸，獲得骨文傳承線索，決定前往附近小鎮打聽消息"),
        (16, 20, "第15章結尾：葉塵在小鎮黑市獲得殘卷，得知上古輪迴者傳說，歸墟殿探子出現"),
        (21, 25, "第20章結尾：葉塵擊殺歸墟殿追兵但重傷，逃入靈脈洞穴"),
        (26, 30, "第25章結尾：葉塵在洞穴中突破、煉製法寶，發現古地圖標記了天機洞"),
        (31, 35, "第30章結尾：葉塵結伴前往天機洞，路上救了散修，到達天機洞外圍"),
    ]
    
    outline_map = {
        6: "深入山谷，遭遇群獸圍攻，第二世戰神經驗救急",
        7: "山谷深處發現骨文遺跡，第一世記憶共鳴",
        8: "主動設伏獵殺妖獸，第一次完全掌握戰鬥節奏",
        9: "用妖獸精血配合歸元訣煉體，肉身強度暴增",
        10: "發現谷外有修仙者蹤跡，謹慎撤離，開始易容術練習",
        11: "用第三世陣皇的易容術改變容貌，化名進入青雲鎮",
        12: "在茶館偷聽消息，得知青雲宗被神秘勢力滲透",
        13: "找到修仙者黑市，出售妖獸材料",
        14: "黑市被地頭蛇盯上，展露實力震懾全場",
        15: "購買到上古殘卷，記載了輪迴者的傳說",
        16: "在客棧解讀殘卷，了解上古輪迴時代",
        17: "發現歸墟殿探子進入小鎮，緊急撤離",
        18: "在荒野與歸墟殿低級成員交手，險勝",
        19: "雖然擊殺敵人但自己重傷，意識到實力不足",
        20: "逃入隱秘靈脈洞穴，靈氣是外面的十倍",
        21: "利用靈脈療傷，衝擊聚元後期",
        22: "成功突破聚元後期，實力大增",
        23: "利用洞中礦石，憑陣皇知識煉製第一件法寶",
        24: "出洞測試法寶威力，一擊斬殺二階妖獸",
        25: "回洞探索深處，發現古地圖標記多處遠古遺跡",
        26: "選擇最近的遺跡「天機洞」，啟程前往",
        27: "穿越荒野路途，遭遇各種自然考驗",
        28: "深夜暴雨中遇險，第四世丹尊藥理知識救命",
        29: "路遇被妖獸追殺的散修，出手相助",
        30: "與散修結伴同行，打聽大陸消息",
        31: "到達天機洞外圍，發現已有其他人探索",
        32: "破解洞口上古禁制，展現陣法天賦",
        33: "洞內如同巨大迷宮，暗含陣法變化",
        34: "用陣皇記憶破解核心陣法",
        35: "獲得輪迴玉珮，與塵埃產生共鳴",
    }
    
    titles = {
        6:"妖獸山谷",7:"骨文遺跡",8:"獵殺",9:"煉體",10:"蹤跡",
        11:"易容",12:"消息",13:"黑市",14:"衝突",15:"殘卷",
        16:"解讀",17:"追兵",18:"追殺",19:"重傷",20:"奇遇",
        21:"療傷",22:"突破",23:"煉器",24:"試刀",25:"地圖",
        26:"選擇",27:"路途",28:"風雨",29:"救人",30:"結伴",
        31:"天機洞",32:"禁制",33:"迷宮",34:"破解",35:"輪迴玉珮",
    }
    
    total_chars = 0
    total_chapters = 0
    
    for start, end, prev_summary in batches:
        for ch in range(start, end + 1):
            outfile = os.path.join(OUTPUT_DIR, f"chapter-{ch}.md")
            
            # 跳過已存在的
            #if os.path.exists(outfile):
            #    c = count_chinese(open(outfile).read())
            #    print(f"⏭️ 第{ch}章 已存在 ({c}字)")
            #    total_chars += c
            #    total_chapters += 1
            #    continue
            
            time.sleep(2)  # 避免速率限制
            
            content = generate_chapter(ai, ch, titles[ch], outline_map[ch], prev_summary)
            if content:
                c = save_chapter(ch, content)
                total_chars += c
                total_chapters += 1
            else:
                print(f"❌ 第{ch}章 生成失敗")
            
            # 每5章更新一次prev_summary
            if ch == end:
                if ch <= 10:
                    pass  # 已經有初始設定

        # 更新前一batch的摘要（取最後一章的結尾）
        last_file = os.path.join(OUTPUT_DIR, f"chapter-{end}.md")
        if os.path.exists(last_file):
            content = open(last_file).read()
            last_200 = content[-200:] if len(content) > 200 else content
            # 更新下一batch的prev_summary...
    
    print(f"\n{'='*40}")
    print(f"生成完成！共{total_chapters}章，{total_chars}字")
    
    # 列出所有章節
    for f in sorted(os.listdir(OUTPUT_DIR)):
        if f.startswith("chapter-") and f.endswith(".md"):
            path = os.path.join(OUTPUT_DIR, f)
            c = count_chinese(open(path).read())
            num = re.findall(r'\d+', f)[0]
            print(f"  第{int(num):3d}章: {c:5d}字")

if __name__ == "__main__":
    main()
