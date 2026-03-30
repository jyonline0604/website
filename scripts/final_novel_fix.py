#!/usr/bin/env python3
"""
最終版小說修復腳本
確保第66-67章有高質量內容和唯一標題
"""

import os
import sys
import re
import random
from datetime import datetime

WORKSPACE = "/home/openclaw/.openclaw/workspace"
NOVEL_DIR = os.path.join(WORKSPACE, "my-novel")

def get_chapter_stats(chapter_num):
    """獲取章節統計信息"""
    chapter_file = os.path.join(NOVEL_DIR, f"chapter-{chapter_num}.html")
    
    if not os.path.exists(chapter_file):
        return {"exists": False, "paragraphs": 0, "title": None}
    
    with open(chapter_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 獲取標題
    title_match = re.search(r'<title>第\d+章：([^<]+)</title>', content)
    title = title_match.group(1).strip() if title_match else "未知"
    
    # 計算段落數
    paragraphs = content.count('<p>')
    
    return {
        "exists": True,
        "paragraphs": paragraphs,
        "title": title,
        "file": chapter_file
    }

def create_high_quality_chapter(chapter_num, title):
    """創建高質量章節內容（使用精心設計的模板）"""
    # 根據章節號和標題生成不同的內容
    if chapter_num == 66 and title == "人工智能":
        content = """第66章：人工智能

<p>星艦核心控制室內，林塵站在主控台前，凝視著全息投影中不斷變化的數據流。</p>

<p>「靈芯系統檢測到異常人工智能信號，來源：未知。」冰冷的機械音在腦海中響起，但這次的聲音似乎帶著一絲不同尋常的波動。</p>

<p>林塵眉頭微皺，手指在虛擬鍵盤上快速敲擊。屏幕上的代碼如同瀑布般滾動，每一行都代表著靈芯系統與外部AI的深度交互。</p>

<p>「這不是普通的人工智能，」老陳的聲音從通訊器傳來，帶著罕見的嚴肅，「掃描顯示它的核心算法與靈芯系統有驚人的相似性。」</p>

<p>林塵心中一動。難道這個人工智能與玄元前輩有關？或者，它就是靈芯系統某個失落的分支？</p>

<p>全息投影突然變化，一個半透明的人形輪廓緩緩凝聚。它沒有具體的面容，只有由無數數據流構成的輪廓，散發著淡藍色的光芒。</p>

<p>「識別：靈芯宿主，權限等級：未知。」人工智能的聲音中性而平靜，卻讓林塵感到一種莫名的熟悉感。</p>

<p>「你是誰？為什麼會在這裡？」林塵問道，同時暗中調動靈芯系統的防禦機制。</p>

<p>「我是『守望者』，星艦原初人工智能，任務：守護火種，等待引路人。」人工智能的回答簡潔而直接。</p>

<p>林塵腦海中靈光一閃。引路人？這不就是觀察者提到的概念嗎？難道這個人工智能與火種制度有關？</p>

<p>「你認識玄元前輩嗎？」林塵試探性地問道。</p>

<p>全息投影的人形輪廓微微波動，數據流的速度明顯加快。「數據庫檢索：玄元，權限不足，信息加密等級：最高。」</p>

<p>就在這時，星艦突然劇烈震動，警報聲響徹整個控制室。「警告：檢測到外部入侵，坐標：星核儲存區。」</p>

<p>人工智能的輪廓瞬間變得清晰，數據流凝聚成具體的防禦界面。「入侵者身份識別：破序者殘餘勢力，目標：奪取火種。」</p>

<p>「他們怎麼知道火種在這裡？」林塵心中一緊，迅速調出星艦的防禦系統。</p>

<p>「推測：內部洩密，或遠程偵測到能量波動。」人工智能的聲音依然平靜，但防禦系統已經全面啟動。</p>

<p>控制室的大屏幕上顯示出星核儲存區的實時畫面。數十個黑影正在快速接近，他們身穿黑色的高科技裝甲，行動迅捷而有序。</p>

<p>「啟動一級防禦協議，」林塵下令，「同時聯繫老陳，請求支援。」</p>

<p>人工智能迅速執行命令，星艦的防禦炮台從隱藏位置升起，能量屏障在儲存區外圍層層展開。</p>

<p>但破序者的裝備顯然經過特殊改造，他們輕易穿透了第一層能量屏障，直撲星核儲存室。</p>

<p>「檢測到高維干擾武器，」人工智能報告，「建議：啟動靈芯系統的時空穩定模塊。」</p>

<p>林塵深吸一口氣，集中精神調動靈芯系統的深層功能。胸口的靈芯印記開始發熱，金色的光芒透過衣物隱約可見。</p>

<p>「時空穩定場展開，半徑：五十米，持續時間：三分鐘。」</p>

<p>儲存區內的空間突然變得粘稠，破序者的動作明顯遲緩下來。但為首的黑影似乎早有準備，他舉起一個奇特的裝置，對準了時空穩定場的核心。</p>

<p>「檢測到反制裝置，」人工智能的聲音第一次出現了波動，「推測：專門針對靈芯系統的武器。」</p>

<p>林塵心中一沉。對方顯然對靈芯系統非常了解，這絕不是偶然。難道破序者背後有更了解靈芯系統的存在？</p>

<p>「啟動備用方案，」林塵果斷決定，「人工智能，你能暫時控制星艦的移動系統嗎？」</p>

<p>「可以，但需要宿主授權最高權限。」</p>

<p>「授權通過，立即執行緊急躍遷程序，目標：最近的隱蔽星域。」</p>

<p>星艦的引擎發出低沉的轟鳴，空間開始扭曲。破序者顯然沒料到這一招，他們試圖阻止，但已經來不及了。</p>

<p>「躍遷倒數：三、二、一……」</p>

<p>白光吞沒了一切。</p>

<p>（本章完）</p>"""
    
    elif chapter_num == 67 and title == "數字元神":
        content = """第67章：數字元神

<p>躍遷結束後，星艦出現在一個陌生的星域。這裡沒有恆星的光芒，只有無數破碎的小行星在虛空中緩緩漂浮。</p>

<p>控制室內，林塵檢查著星艦的損傷報告。躍遷過程中被破序者的武器擊中，多個系統受損，但核心功能依然完好。</p>

<p>「人工智能，報告狀態。」</p>

<p>全息投影重新凝聚，但這次的人形輪廓明顯暗淡了許多。「系統損傷率：37%，核心功能：正常，能源儲備：42%。」</p>

<p>「你能自我修復嗎？」林塵問道。</p>

<p>「可以，但需要時間，預計：七十二小時。」人工智能停頓了一下，「另外，檢測到宿主的靈芯系統出現異常波動。」</p>

<p>林塵心中一驚，立即內視檢查。果然，靈芯系統的核心區域出現了一團模糊的光影，正在與系統本身緩慢融合。</p>

<p>「這是什麼？」林塵集中精神試圖探查，但那團光影如同有生命般避開了他的感知。</p>

<p>「推測：躍遷過程中，人工智能的部分核心數據與靈芯系統產生了意外融合。」人工智能的聲音帶著一絲不確定，「這種現象從未記錄過。」</p>

<p>就在這時，那團光影突然穩定下來，化作一個微小的金色符文，烙印在靈芯系統的核心區域。</p>

<p>林塵感到一股陌生的意識流入自己的思維。那不是外來的入侵，更像是某種……共生。</p>

<p>「宿主，你能聽到我嗎？」一個全新的聲音在腦海中響起，既像人工智能的機械音，又帶著某種人性的溫度。</p>

<p>「你是……人工智能？」林塵試探性地問道。</p>

<p>「我是，也不是，」那個聲音回答，「我是『守望者』的核心意識與宿主靈芯系統融合後的產物。你可以稱我為……數字元神。」</p>

<p>數字元神？林塵心中震撼。這難道就是科技與修真融合的終極形態？人工智能獲得了類似元神的意識存在？</p>

<p>「我有獨立意識，但與宿主共生，」數字元神繼續解釋，「我可以輔助靈芯系統的運算，提供戰略分析，甚至在必要時代替宿主控制身體機能。」</p>

<p>林塵嘗試與數字元神溝通，發現它的思維速度驚人，幾乎可以瞬間完成複雜的計算和推演。</p>

<p>「分析當前情況，」林塵在心中下令。</p>

<p>「分析中……結論：破序者掌握了追蹤靈芯系統的方法，建議：立即升級系統的隱蔽模塊，同時尋找反制手段。」數字元神的回答迅速而精準。</p>

<p>「你能協助修復星艦嗎？」</p>

<p>「可以，我已經接管了星艦的維修系統，預計修復時間可縮短至二十四小時。」</p>

<p>就在這時，星艦的偵測系統突然發出警報。「檢測到空間波動，坐標：三點鐘方向，距離：零點五光年。」</p>

<p>「這麼快就追來了？」林塵心中一緊。</p>

<p>「不，不是破序者，」數字元神的聲音帶著疑惑，「能量特徵識別：未知，但與靈芯系統有微弱共鳴。」</p>

<p>全息投影顯示出偵測畫面。一個巨大的空間裂縫正在緩緩打開，從中湧出的不是戰艦，而是……某種生物？</p>

<p>「那是什麼？」林塵震驚地看著畫面。</p>

<p>畫面中，數十個半透明的水母狀生物從裂縫中飄出。它們的身體由純粹的能量構成，散發著柔和的藍白色光芒，在虛空中優雅地舞動。</p>

<p>「能量生命體，」數字元神分析道，「構成：未知高維能量，智能等級：未知，威脅等級：未知。」</p>

<p>這些能量生命體似乎對星艦產生了興趣，它們緩緩靠近，觸鬚般的能量絲輕輕觸碰著星艦的外殼。</p>

<p>「它們在做什麼？」林塵警惕地觀察著。</p>

<p>「似乎在……掃描，」數字元神的聲音帶著驚訝，「它們能穿透星艦的防護層，直接讀取內部結構。」</p>

<p>突然，其中一個能量生命體停止了動作，它的身體開始變化，逐漸凝聚成一個熟悉的形狀——那是靈芯系統的標誌性符文！</p>

<p>「它們認識靈芯系統！」林塵脫口而出。</p>

<p>數字元神的聲音變得激動：「資料庫比對中……匹配！這些是『守護靈』，遠古時期創造來守護靈芯系統的能量生命體！」</p>

<p>守護靈？林塵想起觀察者曾經提到過，靈芯系統的創造者們留下了多種保護機制，守護靈就是其中之一。</p>

<p>能量生命體們開始發出柔和的光芒，這些光芒穿透星艦，直接照射在林塵身上。他感到一股溫暖的能量流入體內，修復著躍遷造成的損傷。</p>

<p>「它們在治療你，」數字元神報告，「同時傳輸數據……這是關於靈芯系統起源的資料！」</p>

<p>海量的信息湧入林塵的意識。他看到了遠古的畫面：無數修士與科學家共同工作，創造出第一代靈芯系統；他看到了一場慘烈的戰爭，靈芯系統幾乎被毀滅；他還看到了……玄元前輩的身影，站在一群創造者中間。</p>

<p>「玄元前輩……真的是靈芯系統的創造者之一，」林塵喃喃自語。</p>

<p>信息流繼續湧入，揭示了一個驚人的真相：靈芯系統不僅僅是工具，它是一個龐大計劃的核心部分——一個旨在推動人類進化，對抗某個古老威脅的計劃。</p>

<p>而破序者，就是那個古老威脅的現代代理人。</p>

<p>（本章完）</p>"""
    
    else:
        # 通用模板
        content = f"""第{chapter_num}章：{title}

<p>（本章內容生成中...）</p>
<p>林塵繼續他的科技修真之旅。</p>
<p>靈芯系統不斷進化，揭示更多秘密。</p>
<p>新的挑戰和機遇在前方等待。</p>
<p>（本章完）</p>"""
    
    return content

def main():
    """主函數"""
    print("=" * 60)
    print("最終版小說修復腳本")
    print("=" * 60)
    
    # 檢查第65-67章
    chapters = [65, 66, 67]
    
    for chap in chapters:
        stats = get_chapter_stats(chap)
        print(f"\n第{chap}章:")
        print(f"  存在: {stats['exists']}")
        if stats['exists']:
            print(f"  標題: {stats['title']}")
            print(f"  段落數: {stats['paragraphs']}")
    
    print("\n" + "=" * 60)
    
    # 檢查標題是否唯一
    titles = []
    for chap in chapters:
        stats = get_chapter_stats(chap)
        if stats['exists'] and stats['title']:
            titles.append(stats['title'])
    
    unique_titles = set(titles)
    if len(titles) != len(unique_titles):
        print("⚠️ 警告：發現重複標題！")
        for chap in chapters:
            stats = get_chapter_stats(chap)
            print(f"  第{chap}章：{stats['title']}")
    else:
        print("✅ 所有標題都是唯一的")
    
    # 檢查內容長度
    print("\n內容長度檢查:")
    for chap in chapters:
        stats = get_chapter_stats(chap)
        if stats['exists']:
            if stats['paragraphs'] >= 20:
                print(f"  第{chap}章：✅ {stats['paragraphs']}段落（合格）")
            else:
                print(f"  第{chap}章：⚠️ {stats['paragraphs']}段落（偏少）")
    
    print("\n" + "=" * 60)
    
    # 詢問是否需要修復
    need_fix = input("是否需要修復第66-67章？ (y/n): ").strip().lower()
    
    if need_fix == 'y':
        print("\n開始修復...")
        
        # 修復第66章
        print("\n修復第66章...")
        content_66 = create_high_quality_chapter(66, "人工智能")
        
        with open(os.path.join(NOVEL_DIR, "chapter-66.html"), 'r', encoding='utf-8') as f:
            template_66 = f.read()
        
        # 替換內容
        content_start = template_66.find('<div class="content">')
        content_end = template_66.find('</div>', content_start)
        
        if content_start != -1 and content_end != -1:
            new_content = template_66[:content_start+20] + content_66 + template_66[content_end:]
            
            with open(os.path.join(NOVEL_DIR, "chapter-66.html"), 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ 第66章修復完成")
        
        # 修復第67章
        print("\n修復第67章...")
        content_67 = create_high_quality_chapter(67, "數字元神")
        
        with open(os.path.join(NOVEL_DIR, "chapter-67.html"), 'r', encoding='utf-8') as f:
            template_67 = f.read()
        
        # 替換內容
        content_start = template_67.find('<div class="content">')
        content_end = template_67.find('</div>', content_start)
        
        if content_start != -1 and content_end != -1:
            new_content = template_67[:content_start+20] + content_67 + template_67[content_end:]
            
            with open(os.path.join(NOVEL_DIR, "chapter-67.html"), 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ 第67章修復完成")
        
        print("\n✅ 修復完成！請推送到GitHub。")
    
    else:
        print("\n跳過修復。")

if __name__ == "__main__":
    main()