#!/usr/bin/env python3
"""加速版生成器：一次生成5章"""
import os, sys, re, time, json
sys.path.append("/home/openclaw/.openclaw/workspace/scripts")
from ai_multimodel import MultiModelAI

OUT = "/home/openclaw/.openclaw/workspace/research"

SETTINGS = open("/home/openclaw/.openclaw/workspace/research/wangu-chenai-settings.md").read()[:2000]

# 一次性定義所有缺失章節的概要
OUTLINES = {
    # Batch 6-8 已完成跳過
    9: ("煉體", "用妖獸精血配合歸元訣煉體，肉身強度暴增"),
    10: ("蹤跡", "發現谷外有修仙者追蹤，謹慎撤離"),
    11: ("易容", "用陣皇易容術改變容貌，化名進入小鎮"),
    12: ("消息", "茶館偷聽消息，得知青雲宗被滲透"),
    13: ("黑市", "進入修仙者黑市，出售妖獸材料"),
    14: ("衝突", "黑市被地頭蛇盯上，展露實力"),
    15: ("殘卷", "購買到上古殘卷，記載輪迴者傳說"),
    16: ("解讀", "在客棧解讀殘卷，了解輪迴時代"),
    17: ("追兵", "歸墟殿探子出現，緊急撤離"),
    18: ("追殺", "荒野與歸墟殿成員交手，險勝"),
    19: ("重傷", "雖然擊殺敵人但重傷，意識到實力不足"),
    20: ("奇遇", "逃入隱秘靈脈洞穴"),
    21: ("療傷", "在靈脈中療傷，衝擊聚元後期"),
    22: ("突破", "成功突破聚元後期"),
    23: ("煉器", "利用礦石煉製第一件法寶"),
    24: ("試刀", "出洞測試法寶威力，斬殺二階妖獸"),
    25: ("地圖", "在洞深處發現古老地圖"),
    26: ("選擇", "決定前往天機洞"),
    27: ("路途", "穿越荒野，遭遇各種考驗"),
    28: ("風雨", "深夜暴雨遇險，丹尊知識救命"),
    29: ("救人", "路遇被追殺的散修"),
    30: ("結伴", "與散修結伴同行"),
    31: ("天機洞", "到達天機洞外圍"),
    32: ("禁制", "破解洞口上古禁制"),
    33: ("迷宮", "洞內如同巨大迷宮"),
    34: ("破解", "用陣皇記憶破解核心陣法"),
    35: ("輪迴玉珮", "獲得輪迴玉珮，與塵埃共鳴"),
    # 56-80
    56: ("揚名", "成為精英弟子，在天劍閣小有名氣"),
    57: ("暗訪", "開始暗中調查青雲宗變故"),
    58: ("故人消息", "得知雜役老伯下落"),
    59: ("青雲舊事", "青雲宗被歸墟殿滲透的內幕"),
    60: ("突破", "壓力下突破化物期"),
    61: ("疑問", "線索指向第一世死亡真相"),
    62: ("目標", "鎖定當年出賣者——王嘯"),
    63: ("王嘯", "調查王嘯的地位和行蹤"),
    64: ("計劃", "策劃接近王嘯"),
    65: ("機會", "王嘯將來天劍閣開會"),
    66: ("布陣", "在王嘯下榻處布陣"),
    67: ("會面", "易容成侍者接近王嘯"),
    68: ("試探", "言語試探確認他是兇手"),
    69: ("逼問", "深夜潛入制服王嘯"),
    70: ("真相", "王嘯說出受人指使"),
    71: ("主謀", "主謀是歸墟使"),
    72: ("大事", "歸墟殿在全大陸搜尋輪迴者"),
    73: ("塵埃之秘", "塵埃是輪迴之源碎片"),
    74: ("危機", "已被歸墟殿鎖定"),
    75: ("應對", "準備應對歸墟殿追殺"),
    76: ("煉丹", "用丹尊知識煉製突破丹藥"),
    77: ("突破", "服丹突破化物後期"),
    78: ("準備", "煉製陣盤法寶"),
    79: ("風聲", "歸墟殿追殺者已到"),
    80: ("交鋒", "與歸墟殿追殺者正面衝突"),
    # 102-135
    102: ("傳承", "獲得遠古大能殘留傳承"),
    103: ("共鳴", "傳承與塵埃強烈共鳴"),
    104: ("歸墟殿現", "歸墟殿核心成員出現"),
    105: ("交鋒", "與歸墟殿核心成員苦戰"),
    106: ("底牌", "動用前世記憶融合力量"),
    107: ("擊退", "以重傷代價擊退"),
    108: ("療養", "隱秘處療傷鞏固修為"),
    109: ("戰場之秘", "發現戰場與塵埃關聯"),
    110: ("核心", "前往戰場核心區域"),
    111: ("禁制", "核心禁制極其強大"),
    112: ("破解", "用陣皇記憶破解"),
    113: ("輪迴碎片", "發現另一塊輪迴碎片"),
    114: ("融合", "兩塊碎片融合"),
    115: ("異變", "融合引發天地異象"),
    116: ("圍攻", "被各方勢力包圍"),
    117: ("老者再現", "神秘老者解圍"),
    118: ("真相初現", "老者透露輪迴陰謀"),
    119: ("最終試煉", "接受萬古戰場最終試煉"),
    120: ("試煉一", "對抗心魔"),
    121: ("試煉二", "對抗幻境"),
    122: ("試煉三", "直面本心"),
    123: ("過關", "通過試煉獲得傳承"),
    124: ("離開", "萬古戰場關閉"),
    125: ("歸墟追殺", "歸墟殿佈下天羅地網"),
    126: ("血戰", "衝出包圍"),
    127: ("逃脫", "以掌命期修為撕開封鎖"),
    128: ("新目標", "決定前往靈天界"),
    129: ("告別", "向神秘老者告別"),
    130: ("傳送", "通過上古傳送陣"),
    131: ("初臨", "到達靈天界"),
    132: ("靈天界", "了解靈天界格局"),
    133: ("新身份", "建立新身份"),
    134: ("線索", "發現輪迴之源記載"),
    135: ("目標", "鎖定歸墟遺跡"),
}

def count_cn(text):
    return sum(1 for c in text if '\u4e00' <= c <= '\u9fff')

def generate_batch(ai, chapters, batch_info):
    """一次生成5章的概要"""
    ch_list = []
    for ch in chapters:
        title, outline = OUTLINES[ch]
        ch_list.append(f"第{ch}章「{title}」：{outline}")
    
    prompt = f"""{batch_info}

請一次寫出以下5章：
{chr(10).join(ch_list)}

要求：
1. 每章1500-2000中文字（先寫完整情節，之後再擴充）
2. 每章用「# 第X章 標題」開頭
3. 用破折號「---」分隔不同章節
4. 包含具體場景、對話、戰鬥描寫
5. 直接輸出，無需說明"""

    system = f"""你是《萬古塵埃》小說作者。{SETTINGS[:1000]}

寫作風格：有畫面感、節奏明快、戰鬥描寫細膩。直接輸出正文。"""

    content = ai.call_deepseek(prompt, system, max_tokens=8000)
    if not content:
        content = ai.call_openrouter(prompt, system, max_tokens=8000)
    return content

def parse_and_save(content, chapters):
    """從生成內容中解析並保存各章"""
    # 按章分割
    sections = re.split(r'# 第(\d+)章', content)
    saved = 0
    for i in range(1, len(sections), 2):
        ch_num = int(sections[i])
        ch_content = sections[i+1].strip() if i+1 < len(sections) else ""
        if ch_num in chapters and ch_content:
            full = f"# 第{ch_num}章 {OUTLINES[ch_num][0]}\n\n{ch_content}"
            path = os.path.join(OUT, f"chapter-{ch_num}.md")
            with open(path, "w") as f:
                f.write(full)
            cn = count_cn(full)
            print(f"  ✅ 第{ch_num}章: {cn}字")
            saved += 1
    return saved

def main():
    ai = MultiModelAI()
    total = 0
    
    # 只處理缺失的章節
    all_chapters = sorted(OUTLINES.keys())
    
    # 移除已存在的
    missing = []
    for ch in all_chapters:
        path = os.path.join(OUT, f"chapter-{ch}.md")
        if not os.path.exists(path):
            missing.append(ch)
    
    print(f"需要生成 {len(missing)} 章: {missing[:5]}...{missing[-3:]}")
    
    # 分組，每批5章
    batches = [missing[i:i+5] for i in range(0, len(missing), 5)]
    
    for idx, batch in enumerate(batches):
        ch_range = f"{batch[0]}-{batch[-1]}"
        print(f"\n批次 {idx+1}/{len(batches)}: 第{ch_range}章")
        
        batch_info = f"故事到目前為止："
        if batch[0] <= 35:
            batch_info += "葉塵已從青雲宗假死脫身，在荒野修煉突破到聚元期，發現妖獸山谷中的骨文遺跡，擊殺歸墟殿追兵後逃入靈脈洞穴。"
        elif batch[0] <= 80:
            batch_info += "葉塵化名加入天劍閣，查出第一世被師兄王嘯出賣，背後主謀是歸墟殿。他準備逃離天劍閣。"
        else:
            batch_info += "葉塵逃出天劍閣，在神秘老者指點下進入萬古戰場。在戰場中他獲得遠古傳承，發現另一塊輪迴碎片。"
        
        content = generate_batch(ai, batch, batch_info)
        if content:
            saved = parse_and_save(content, batch)
            total += saved
            print(f"  → 本批生成 {saved}/{len(batch)} 章")
        else:
            print(f"  ❌ 第{ch_range}生成失敗")
        
        time.sleep(3)
    
    # 匯總
    print(f"\n{'='*40}")
    print(f"總生成: {total} 章")
    for f in sorted(os.listdir(OUT)):
        if f.startswith("chapter-") and f.endswith(".md"):
            path = os.path.join(OUT, f)
            c = count_cn(open(path).read())
            num = re.findall(r'\d+', f)[0]
            print(f"  第{int(num):3d}章: {c:5d}字")

if __name__ == "__main__":
    main()
