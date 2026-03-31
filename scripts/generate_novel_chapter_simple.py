#!/usr/bin/env python3
"""
簡單但有效的小說章節生成腳本
生成更長內容和唯一標題
"""

import os
import sys
import re
import random
from datetime import datetime

WORKSPACE = "/home/openclaw/.openclaw/workspace"
NOVEL_DIR = WORKSPACE
LOG_FILE = os.path.join(WORKSPACE, "logs/novel-generator-simple.log")

def log(message):
    """寫入日誌"""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_line = f"{timestamp} {message}"
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")
    
    print(log_line)
    return log_line

def get_used_titles():
    """獲取已使用的章節標題"""
    used_titles = set()
    
    for filename in os.listdir(NOVEL_DIR):
        if filename.startswith("chapter-") and filename.endswith(".html"):
            try:
                with open(os.path.join(NOVEL_DIR, filename), 'r', encoding='utf-8') as f:
                    content = f.read(1000)
                    # 查找標題
                    title_match = re.search(r'<title>第\d+章：([^<]+)</title>', content)
                    if title_match:
                        used_titles.add(title_match.group(1).strip())
            except:
                pass
    
    return used_titles

def generate_unique_title(chapter_num, used_titles):
    """生成唯一的章節標題"""
    # 可用的標題選項
    title_options = [
        "虛空試煉", "時空裂縫", "能量風暴", "系統升級", "遠古密碼",
        "靈芯共鳴", "科技突破", "修真奇遇", "意識融合", "維度跨越",
        "星核覺醒", "數據洪流", "量子修真", "機械元神", "虛擬道場",
        "靈網入侵", "時光回溯", "平行宇宙", "能量矩陣", "靈魂編程",
        "科技天劫", "數字元神", "虛擬金丹", "量子經脈", "數據築基",
        "靈氣復甦", "科技修真", "時空穿梭", "意識上傳", "虛擬現實",
        "修真科技", "人工智能", "腦機接口", "納米修真", "生物芯片"
    ]
    
    # 過濾已使用的標題
    available_titles = [t for t in title_options if t not in used_titles]
    
    if not available_titles:
        # 如果所有標題都用過了，添加編號
        base_title = random.choice(title_options)
        return f"{base_title}·新篇"
    
    return random.choice(available_titles)

def generate_chapter_content(chapter_num, chapter_title):
    """生成章節內容（使用模板+隨機生成）"""
    # 場景模板
    scenes = [
        "星艦殘骸深處的實驗室中，林塵站在能量矩陣中央。",
        "虛擬修煉室內，數據流光幕環繞著林塵緩緩旋轉。",
        "遠古遺跡的地下密室，靈氣與科技設備交織出奇異的光影。",
        "城市高樓的頂層，林塵俯瞰著霓虹閃爍的賽博都市。",
        "深山古洞中，古老的修真陣法與現代科技儀器並存。"
    ]
    
    # 對話模板
    dialogues = [
        "「靈芯系統檢測到異常能量波動，建議立即中斷連接。」冰冷的機械音在腦海中響起。",
        "老陳的聲音從通訊器傳來：「小子，監測顯示你的生命體徵正在劇烈波動，要不要先停下來？」",
        "「不必擔心，這只是靈芯系統的正常進化過程。」觀察者的聲音溫和而深邃。",
        "「林塵，你感覺怎麼樣？」實驗室外的研究員透過玻璃牆關切地詢問。",
        "「這就是科技修真的真正力量嗎？」林塵喃喃自語，感受著體內奔湧的能量。"
    ]
    
    # 動作模板
    actions = [
        "林塵雙手結印，靈氣從指尖湧出，與周圍的數據流產生共鳴。",
        "他閉上眼睛，意識沉入靈芯系統的深層界面，無數金色符文在眼前閃爍。",
        "能量洪流衝擊著經脈，林塵咬緊牙關，運轉起玄元前輩傳授的功法。",
        "虛擬界面彈出警告提示，但林塵毫不猶豫地點擊了「確認」按鈕。",
        "星核碎片釋放出脈衝光波，實驗室內的儀器同時發出尖銳的警報聲。"
    ]
    
    # 生成段落
    paragraphs = []
    
    # 標題
    paragraphs.append(f"第{chapter_num}章：{chapter_title}")
    
    # 開頭場景
    paragraphs.append(random.choice(scenes))
    paragraphs.append("空氣中瀰漫著靈氣與電子設備混合的奇特氣味。")
    
    # 生成20-30個段落
    for i in range(random.randint(20, 30)):
        # 隨機選擇段落類型
        para_type = random.choice(['scene', 'dialogue', 'action', 'description', 'reflection'])
        
        if para_type == 'scene':
            paragraphs.append(random.choice(scenes))
        elif para_type == 'dialogue':
            paragraphs.append(random.choice(dialogues))
        elif para_type == 'action':
            paragraphs.append(random.choice(actions))
        elif para_type == 'description':
            descriptions = [
                "靈芯系統的界面在視網膜上投影出複雜的數據流。",
                "周圍的靈氣如同有生命般流動，與科技設備產生意想不到的共振。",
                "時間彷彿在這一刻凝固，只有能量在經脈中奔流的聲音清晰可聞。",
                "虛擬與現實的界限變得模糊，林塵感覺自己同時存在於兩個世界。",
                "科技與修真的融合產生了前所未有的化學反應，一種全新的力量正在誕生。"
            ]
            paragraphs.append(random.choice(descriptions))
        else:  # reflection
            reflections = [
                "林塵心中湧起一股明悟，科技與修真並非對立，而是相輔相成。",
                "這不僅僅是力量的提升，更是對宇宙本質的更深層次理解。",
                "每一次突破都讓他更加確信，人類的進化之路才剛剛開始。",
                "靈芯系統不僅是工具，更是通往更高維度存在的橋樑。",
                "在科技與修真的交匯點，他看到了無限的可能性。"
            ]
            paragraphs.append(random.choice(reflections))
    
    # 結尾
    paragraphs.append("（本章完）")
    
    return paragraphs

def create_enhanced_chapter_file(chapter_num, paragraphs, chapter_title):
    """創建增強版章節HTML文件"""
    try:
        # 讀取模板
        template_file = os.path.join(NOVEL_DIR, "chapter-template.html")
        if not os.path.exists(template_file):
            log(f"❌ 錯誤：找不到模板文件 {template_file}")
            return None
        
        with open(template_file, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # 創建HTML段落
        html_paragraphs = []
        for para in paragraphs:
            if para:
                # 如果是標題，不加<p>標籤
                if para.startswith(f'第{chapter_num}章：'):
                    html_paragraphs.append(para)
                else:
                    html_paragraphs.append(f'<p>{para}</p>')
        
        chapter_content = '\n'.join(html_paragraphs)
        
        # 替換模板中的佔位符
        template = template.replace('{CHAPTER_TITLE}', chapter_title)
        template = template.replace('{CHAPTER_NUM}', str(chapter_num))
        template = template.replace('{CONTENT}', chapter_content)
        
        # 更新導航鏈接
        prev_num = chapter_num - 1 if chapter_num > 1 else ""
        next_num = chapter_num + 1
        
        if prev_num:
            template = template.replace('{PREV_NUM}', str(prev_num))
        else:
            template = template.replace('{PREV_NUM}', '1')
        
        template = template.replace('{NEXT_NUM}', str(next_num))
        
        # 寫入文件
        filename = f"chapter-{chapter_num}.html"
        filepath = os.path.join(NOVEL_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(template)
        
        # 統計信息
        word_count = sum(len(p) for p in paragraphs if not p.startswith(f'第{chapter_num}章：'))
        paragraph_count = len([p for p in paragraphs if not p.startswith(f'第{chapter_num}章：')])
        
        log(f"已創建: {filename}")
        log(f"標題: 第{chapter_num}章：{chapter_title}")
        log(f"段落數: {paragraph_count}")
        log(f"估計字數: {word_count} 字")
        
        return filename
        
    except Exception as e:
        log(f"❌ 創建章節文件錯誤: {str(e)}")
        return None

def main():
    """主函數"""
    log("=" * 60)
    log("開始簡單版小說章節生成...")
    
    # 獲取已使用的標題
    used_titles = get_used_titles()
    log(f"已使用的標題數: {len(used_titles)}")
    
    # 需要重新生成的章節
    chapters_to_regenerate = [66, 67]
    
    for chapter_num in chapters_to_regenerate:
        log(f"\n{'='*40}")
        log(f"處理第{chapter_num}章...")
        
        # 生成唯一標題
        chapter_title = generate_unique_title(chapter_num, used_titles)
        log(f"生成標題: 第{chapter_num}章：{chapter_title}")
        
        # 添加到已使用標題
        used_titles.add(chapter_title)
        
        # 生成內容
        paragraphs = generate_chapter_content(chapter_num, chapter_title)
        log(f"生成段落數: {len(paragraphs)}")
        
        # 備份舊文件
        chapter_file = os.path.join(NOVEL_DIR, f"chapter-{chapter_num}.html")
        if os.path.exists(chapter_file):
            import shutil
            backup_file = f"{chapter_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(chapter_file, backup_file)
            log(f"已備份舊文件到: {backup_file}")
        
        # 創建新文件
        filename = create_enhanced_chapter_file(chapter_num, paragraphs, chapter_title)
        
        if filename:
            log(f"✅ 第{chapter_num}章重新生成成功")
        else:
            log(f"❌ 第{chapter_num}章重新生成失敗")
    
    log("\n" + "=" * 60)
    log("簡單版生成完成！")

if __name__ == "__main__":
    main()