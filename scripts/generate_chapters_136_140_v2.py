#!/usr/bin/env python3
"""
《萬古塵埃》第136-140章 - 強化版生成器
每章要求3000+字
"""
import os, sys, re, time
sys.path.append("/home/openclaw/.openclaw/workspace/scripts")
from ai_multimodel import MultiModelAI

OUT = "/home/openclaw/.openclaw/workspace/research"

SETTINGS = open("/home/openclaw/.openclaw/workspace/research/wangu-chenai-settings.md").read()[:2000]

def count_cn(text):
    return sum(1 for c in text if '\u4e00' <= c <= '\u9fff')

STORY_SOFAR = """第135章結局：葉塵摧毁九幽祭壇，獲得歸墟令牌。他正前往歸墟遺跡——遠古一位觸碰輪迴禁忌的大能「輪迴天尊」隕落之地。目標：湊齊9塊輪迴碎片，解開輪迴之謎。

葉塵目前狀態：
- 修為：煉魂期（融合前幾世功法）
- 九世記憶：散修(第1世)→戰神(第2世)→陣皇(第3世)→丹尊(第4世)→劍帝(第5世)→魔主(第6世)→聖僧(第7世)→輪迴行者(第8世)
- 已獲碎片：2塊（需9塊）
- 持有：歸墟令牌（剛獲取）

寫作要求（嚴格遵守）：
1. 每章3000+中文字（約3500-4500字為佳）
2. 每章用「# 第X章 標題」作為標題
3. 重要情節（戰鬥、突破、內心戲）必須詳細描寫，不少於整章1/3
4. 每章要有具體的場景、動作、對話、心理活動
5. 每章结尾要有懸念鉤子（結尾要讓讀者想繼續看下一章）
6. 節奏明快，不要廢話
7. 各章內容不要重複，場景和情節要有區分度
8. 用「---」分隔不同章節"""

CHAPTERS = [
    (136, "歸墟令牌", """葉塵到達歸墟遺跡入口。必須詳細描寫：
- 抵達時的場景：虛空扭曲、死氣縱橫、天地變色
- 歸墟令牌的激活過程：符文流轉、裂縫撕開
- 葉塵的心理：期待與警惕交織
- 進入時遭遇的危機：空間裂縫中有什麼東西蘇醒
- 最終踏入遺跡的那一刻

重要：這是進入歸墟遗迹的第一章，要詳細刻畫那種遠古禁地的壓迫感和神秘感。葉塵要運用第三世陣皇的知識感受禁制。"""),

    (137, "第一層", """葉塵進入歸墟遺跡第一層。必須詳細描寫：
- 第一層的環境：上古傀儡獸守衛、遍地骸骨、禁制縱橫
- 與傀儡獸的戰鬥：要具體到招式（葉塵用第二世修羅戰神的近戰本能）
- 破解禁制的過程：運用第三世陣皇的知識
- 發現壁畫：遠古壁畫刻在石壁上，描述輪迴天尊的一生
- 壁畫內容透露的信息：暗示歸墟殿的存在

重要：戰鬥要有招式名、內心判斷、打鬥過程（至少300字）。禁制破解要有推理過程。"""),

    (138, "壁畫之秘", """葉塵仔細研究壁畫，發現驚人真相。必須詳細描寫：
- 壁畫內容：輪迴天尊與神秘組織的戰鬥，那個組織的標誌——與歸墟殿一模一樣
- 葉塵的震驚：這個陰謀比他想像的還要古老（至少數萬年）
- 壁畫暗示：歸墟殿在收集輪迴者的靈魂
- 葉塵的推測：自己可能只是被收集的對象之一
- 第一層深處的危機：有其他強者闖入，正在接近

重要：要詳細刻畫葉塵的心理活動（震驚、憤怒、警覺）。同時要有新的危機出现作為鉤子。"""),

    (139, "第二層", """葉塵穿過第一層，進入第二層迷霧地帶。必須詳細描寫：
- 第二層的環境：迷霧籠罩，能見度極低，會讓人迷失自我
- 葉塵運用第八世輪迴行者的意境穩住神識
- 遭遇迷霧中的幻象：前世死亡的場景重現（第一世被師兄出賣、第二世被圍攻……）
- 葉塵如何對抗心魔：第九世記憶中輪迴行者的經驗
- 穿過迷霧後看到的景象：一片巨大的廣場，有石碑林立

重要：幻象要有具體的前世死亡畫面，要能讓讀者感受到葉塵的痛苦。要有掙扎和突破的過程。"""),

    (140, "輪迴印記", """葉塵在第二層感應到第三塊輪迴碎片。必須詳細描寫：
- 感應過程：體內兩塊碎片產生共鳴，指向更深處
- 葉塵的選擇：繼續深入還是先觀望
- 發現其他進入者：感應到至少兩股氣息，一股熟悉（似曾見過），一股危險
- 葉塵躲藏觀察，看到：似乎是某大宗門的弟子，正在與另一方爭鬥
- 結尾鉤子：爭鬥的一方突然停下，似乎感應到了葉塵的存在

重要：最後要有明確的鉤子，讓讀者想知道"對方是誰"。"葉塵與那些人是敵是友？"留下懸念。"""),
]

def generate_single_chapter(ai, ch_num, title, outline_detail):
    prompt = f"""{STORY_SOFAR}

請詳細寫出第{ch_num}章「{title}」：

{outline_detail}

要求：
- 正文至少3000中文字（目標3500-4500字）
- 詳細的場景、動作、心理、對話
- 戰鬥要有招式名和過程（至少400字）
- 突破或危機要有細節（至少300字）
- 結尾鉤子要明確（200字左右懸念）
- 直接輸出，無任何其他文字"""

    system = f"""你是《萬古塵埃》小說作者。小說設定：{SETTINGS[:1500]}

寫作風格：
- 東方玄幻/仙俠，有畫面感，節奏明快
- 每章3000+字，重要情節詳細寫
- 戰鬥要有招式、內心判斷、過程
- 每章结尾要有懸念鉤子
- 直接輸出正文"""

    content = ai.call_deepseek(prompt, system, max_tokens=8000)
    if not content:
        content = ai.call_openrouter(prompt, system, max_tokens=8000)
    return content

def save_chapter(ch_num, title, content):
    full = f"# 第{ch_num}章 {title}\n\n{content.strip()}"
    path = os.path.join(OUT, f"chapter-{ch_num}.md")
    with open(path, "w") as f:
        f.write(full)
    cn = count_cn(full)
    return cn

def main():
    ai = MultiModelAI()
    
    for ch_num, title, outline_detail in CHAPTERS:
        print(f"\n生成第{ch_num}章「{title}」...")
        content = generate_single_chapter(ai, ch_num, title, outline_detail)
        
        if content:
            cn = save_chapter(ch_num, title, content)
            status = "✅" if cn >= 3000 else "⚠️"
            print(f"  {status} 第{ch_num}章「{title}」: {cn}字")
        else:
            print(f"  ❌ 第{ch_num}章生成失敗")
        
        time.sleep(2)
    
    print(f"\n{'='*40}")
    print("生成完成，結果：")
    for ch_num, title, _ in CHAPTERS:
        path = os.path.join(OUT, f"chapter-{ch_num}.md")
        if os.path.exists(path):
            c = count_cn(open(path).read())
            print(f"  第{ch_num}章「{title}」: {c}字")

if __name__ == "__main__":
    main()