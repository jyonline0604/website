#!/usr/bin/env python3
"""
《萬古塵埃》第136-200章生成器
第一批：第136-140章
"""
import os, sys, re, time
sys.path.append("/home/openclaw/.openclaw/workspace/scripts")
from ai_multimodel import MultiModelAI

OUT = "/home/openclaw/.openclaw/workspace/research"

SETTINGS = open("/home/openclaw/.openclaw/workspace/research/wangu-chenai-settings.md").read()[:2000]
CHAPTER135 = open("/home/openclaw/.openclaw/workspace/research/chapter-135.md").read()

OUTLINES_136_140 = {
    136: ("歸墟令牌", "葉塵到達歸墟遺跡入口，用歸墟令牌打開封印，進入遠古大能隕落之地。裡面危機四伏，到處是禁制和陷阱。"),
    137: ("第一層", "葉塵進入歸墟遺跡第一層，遭遇上古傀儡獸。運用第三世陣皇的知識破解禁制，發現這一層藏有輪迴相關的壁畫。"),
    138: ("壁畫之秘", "壁畫記述遠古時代一段輪迴者與神秘組織的戰鬥。葉塵震驚發現，神秘組織的標誌竟與歸墟殿一模一樣。輪迴陰謀比想像中更古老。"),
    139: ("第二層", "葉塵破解第一層禁制，進入第二層。這裡充滿迷霧，元神稍弱者會迷失自我。他動用第八世輪迴行者的意境穩住神識。"),
    140: ("輪迴印記", "在第二層深處，葉塵感應到第三塊輪迴碎片的存在。同時察覺有其他進入者，他選擇先觀察，再決定是否接觸。"),
}

def count_cn(text):
    return sum(1 for c in text if '\u4e00' <= c <= '\u9fff')

def generate_batch(ai, chapters):
    ch_list = []
    for ch in chapters:
        title, outline = OUTLINES_136_140[ch]
        ch_list.append(f"第{ch}章「{title}」：{outline}")
    
    story_sofar = """第135章結局：葉塵摧毁九幽祭壇，獲得歸墟令牌。現正前往歸墟遺跡——遠古一位觸碰輪迴禁忌的大能隕落之地。他手中有2塊輪迴碎片，需要湊齊9塊才能解開輪迴之謎。目前修為：煉魂期（融合前幾世功法）。九世記憶：散修→戰神→陣皇→丹尊→劍帝→魔主→聖僧→輪迴行者。"""

    prompt = f"""你是《萬古塵埃》小說作者，請一次生成第136-140章。

故事背景：{story_sofar}

請一次寫出以下5章：
{chr(10).join(ch_list)}

要求：
1. 每章至少3000中文字（請寫充分、細節豐富）
2. 每章用「# 第X章 標題」開頭
3. 用「---」分隔不同章節
4. 重要情節要寫詳細：戰鬥要有招式和內心戲，突破要有過程和感受
5. 每章結尾要有懸念鉤子
6. 節奏明快，不要拖泥帶水
7. 直接輸出正文，不要任何說明"""

    system = f"""你是《萬古塵埃》小說作者。

小說設定：{SETTINGS[:1500]}

寫作風格：
- 東方玄幻/仙俠文風，有畫面感，節奏明快
- 融合凡人修仙傳的穩步升級感、仙逆的情感衝擊、遮天的宏大格局
- 每章3000+字，重要事情寫詳細
- 每章结尾要有鉤子
- 人物對話要自然"""

    content = ai.call_deepseek(prompt, system, max_tokens=12000)
    if not content:
        content = ai.call_openrouter(prompt, system, max_tokens=12000)
    return content

def parse_and_save(content, chapters):
    """從生成內容中解析並保存各章"""
    sections = re.split(r'# 第(\d+)章', content)
    saved = 0
    for i in range(1, len(sections), 2):
        ch_num = int(sections[i])
        ch_content = sections[i+1].strip() if i+1 < len(sections) else ""
        if ch_num in chapters and ch_content:
            full = f"# 第{ch_num}章 {OUTLINES_136_140[ch_num][0]}\n\n{ch_content}"
            path = os.path.join(OUT, f"chapter-{ch_num}.md")
            with open(path, "w") as f:
                f.write(full)
            cn = count_cn(full)
            print(f"  ✅ 第{ch_num}章「{OUTLINES_136_140[ch_num][0]}」: {cn}字")
            saved += 1
    return saved

def main():
    ai = MultiModelAI()
    chapters = [136, 137, 138, 139, 140]
    
    print(f"開始生成第136-140章...")
    content = generate_batch(ai, chapters)
    
    if content:
        print(f"生成成功，共 {len(content)} 字")
        saved = parse_and_save(content, chapters)
        print(f"\n本批完成：{saved}/{len(chapters)} 章")
        
        # 顯示生成結果的字數
        for ch in chapters:
            path = os.path.join(OUT, f"chapter-{ch}.md")
            if os.path.exists(path):
                c = count_cn(open(path).read())
                print(f"  第{ch}章: {c}字")
    else:
        print("❌ 生成失敗")

if __name__ == "__main__":
    main()