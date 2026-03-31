#!/usr/bin/env python3
"""
多模型小說章節生成器
使用備用策略：DeepSeek → MiniMax → OpenRouter → Gemini → 本地模板
"""

import os
import sys
import re
import random
from datetime import datetime

# 添加當前目錄到路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_multimodel import MultiModelAI

WORKSPACE = "/home/openclaw/.openclaw/workspace"
NOVEL_DIR = WORKSPACE
LOG_FILE = os.path.join(WORKSPACE, "logs/novel-multimodel.log")

def log(message):
    """寫入日誌"""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_line = f"{timestamp} {message}"
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")
    
    print(log_line)
    return log_line

def get_next_chapter_number():
    """獲取下一個章節號"""
    max_num = 0
    
    for filename in os.listdir(NOVEL_DIR):
        if filename.startswith("chapter-") and filename.endswith(".html"):
            match = re.match(r"chapter-(\d+)\.html", filename)
            if match:
                chapter_num = int(match.group(1))
                if chapter_num > max_num:
                    max_num = chapter_num
    
    return max_num + 1

def get_previous_chapter_content(chapter_num):
    """獲取前一章的內容作為上下文"""
    if chapter_num <= 1:
        return "這是故事的開始。主角林塵剛剛發現自己體內有一個神秘的靈芯系統。"
    
    prev_file = os.path.join(NOVEL_DIR, f"chapter-{chapter_num-1}.html")
    if os.path.exists(prev_file):
        try:
            with open(prev_file, 'r', encoding='utf-8') as f:
                content = f.read(3000)  # 讀取前3000字符
            
            # 提取內容區域
            content_start = content.find('<div class="content">')
            if content_start != -1:
                content_end = content.find('</div>', content_start)
                if content_end != -1:
                    chapter_content = content[content_start+20:content_end]
                    # 清理HTML標籤
                    chapter_content = re.sub(r'<[^>]+>', '', chapter_content)
                    # 取最後500字符作為上下文
                    return chapter_content[-500:] if len(chapter_content) > 500 else chapter_content
        except Exception as e:
            log(f"讀取前一章錯誤: {e}")
    
    return f"延續第{chapter_num-1}章的故事。"

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

def create_chapter_file(chapter_num, ai_content, chapter_title):
    """創建章節HTML文件"""
    try:
        # 讀取模板
        template_file = os.path.join(NOVEL_DIR, "chapter-template.html")
        if not os.path.exists(template_file):
            log(f"❌ 錯誤：找不到模板文件 {template_file}")
            return None
        
        with open(template_file, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # 處理AI內容
        lines = ai_content.split('\n')
        paragraphs = []
        
        for line in lines:
            line = line.strip()
            if line:
                # 跳過重複的標題行
                if line.startswith(f'第{chapter_num}章：'):
                    if paragraphs:  # 如果已經有標題了，跳過
                        continue
                    paragraphs.append(line)  # 保留第一個標題
                else:
                    paragraphs.append(line)
        
        # 確保有足夠的段落
        if len(paragraphs) < 15:
            log(f"⚠️ 段落數不足: {len(paragraphs)}，補充中...")
            # 補充段落
            for i in range(15 - len(paragraphs)):
                paragraphs.append(f"（劇情推進中...）")
        
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

def update_novel_lists():
    """更新小說網站列表"""
    try:
        update_script = os.path.join(WORKSPACE, "scripts/update_novel_lists.py")
        
        import subprocess
        result = subprocess.run(
            ["python3", update_script],
            capture_output=True,
            text=True,
            cwd=WORKSPACE
        )
        
        if result.returncode == 0:
            log("✅ 已更新網站列表")
            return True
        else:
            log(f"❌ 更新網站列表失敗: {result.stderr[:200]}")
            return False
            
    except Exception as e:
        log(f"❌ 調用更新腳本錯誤: {e}")
        return False

def generate_daily_chapter():
    """生成每日章節"""
    log("=" * 60)
    log("開始多模型小說章節生成...")
    
    # 初始化多模型 AI
    ai = MultiModelAI()
    
    # 獲取下一個章節號
    next_chapter = get_next_chapter_number()
    log(f"準備生成: 第{next_chapter}章")
    
    # 獲取已使用的標題
    used_titles = get_used_titles()
    log(f"已使用的標題數: {len(used_titles)}")
    
    # 生成唯一標題
    chapter_title = generate_unique_title(next_chapter, used_titles)
    log(f"生成標題: 第{next_chapter}章：{chapter_title}")
    
    # 獲取前一章內容作為上下文
    previous_context = get_previous_chapter_content(next_chapter)
    log(f"上下文長度: {len(previous_context)} 字符")
    
    # 使用多模型 AI 生成章節
    log("使用多模型 AI 生成章節內容...")
    result = ai.generate_novel_chapter(next_chapter, previous_context, chapter_title)
    
    if not result["success"]:
        log("❌ AI 生成失敗，使用備用內容")
        # 使用備用內容
        backup_content = f"""第{next_chapter}章：{chapter_title}

<p>林塵站在星艦的觀景窗前，凝視著窗外無垠的星空。</p>

<p>靈芯系統在腦海中發出柔和的提示音：「檢測到新的能量波動，來源：未知星域。」</p>

<p>「又是未知，」林塵喃喃自語，「這個宇宙到底還隱藏著多少秘密？」</p>

<p>老陳的聲音從通訊器傳來：「小子，監測到異常空間扭曲，建議立即進行掃描。」</p>

<p>林塵點點頭，調出靈芯系統的掃描界面。無數數據流在眼前閃過，構成一幅複雜的星圖。</p>

<p>突然，星圖上出現了一個從未見過的標記——那是一個古老的符文，與靈芯系統的核心符文驚人地相似。</p>

<p>「這是……」林塵心中一震。</p>

<p>「檢測到遠古信號，」靈芯系統報告，「信號來源：距離當前位置三光年，信號內容：加密狀態。」</p>

<p>林塵深吸一口氣，做出決定：「設定航向，前往信號源。」</p>

<p>星艦引擎發出低沉的轟鳴，開始調整航向。新的冒險，即將開始。</p>

<p>（本章完）</p>"""
        ai_content = backup_content
    else:
        ai_content = result["content"]
        log("✅ AI 生成成功")
    
    # 創建章節文件
    filename = create_chapter_file(next_chapter, ai_content, chapter_title)
    
    if filename:
        log(f"✅ 第{next_chapter}章生成成功")
        
        # 更新網站列表
        log("更新網站列表...")
        update_novel_lists()
        
        log(f"✅ 任務完成！已生成第{next_chapter}章：{chapter_title}")
    else:
        log(f"❌ 第{next_chapter}章生成失敗")
    
    log("=" * 60)
    return filename is not None

def regenerate_specific_chapter(chapter_num, new_title=None):
    """重新生成特定章節（用於修復）"""
    log(f"\n{'='*40}")
    log(f"重新生成第{chapter_num}章...")
    
    # 初始化多模型 AI
    ai = MultiModelAI()
    
    # 獲取已使用的標題
    used_titles = get_used_titles()
    
    # 生成或使用指定標題
    if new_title:
        chapter_title = new_title
    else:
        chapter_title = generate_unique_title(chapter_num, used_titles)
    
    log(f"標題: 第{chapter_num}章：{chapter_title}")
    
    # 獲取前一章內容作為上下文
    previous_context = get_previous_chapter_content(chapter_num)
    log(f"上下文長度: {len(previous_context)} 字符")
    
    # 備份舊文件
    chapter_file = os.path.join(NOVEL_DIR, f"chapter-{chapter_num}.html")
    if os.path.exists(chapter_file):
        import shutil
        backup_file = f"{chapter_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(chapter_file, backup_file)
        log(f"已備份舊文件到: {backup_file}")
    
    # 使用多模型 AI 生成章節
    log("使用多模型 AI 生成章節內容...")
    result = ai.generate_novel_chapter(chapter_num, previous_context, chapter_title)
    
    if not result["success"]:
        log("❌ AI 生成失敗，使用備用內容")
        # 簡單備用內容
        ai_content = f"""第{chapter_num}章：{chapter_title}

<p>（本章內容重新生成中...）</p>
<p>林塵的科技修真之旅繼續展開。</p>
<p>靈芯系統揭示新的秘密。</p>
<p>前方有新的挑戰等待。</p>
<p>（本章完）</p>"""
    else:
        ai_content = result["content"]
        log("✅ AI 生成成功")
    
    # 創建章節文件
    filename = create_chapter_file(chapter_num, ai_content, chapter_title)
    
    if filename:
        log(f"✅ 第{chapter_num}章重新生成成功")
        return True
    else:
        log(f"❌ 第{chapter_num}章重新生成失敗")
        return False

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="多模型小說章節生成器")
    parser.add_argument("--daily", action="store_true", help="生成每日章節")
    parser.add_argument("--regenerate", type=int, help="重新生成特定章節")
    parser.add_argument("--title", type=str, help="指定章節標題（與--regenerate一起使用）")
    
    args = parser.parse_args()
    
    if args.regenerate:
        # 重新生成特定章節
        success = regenerate_specific_chapter(args.regenerate, args.title)
        if success:
            # 更新網站列表
            update_novel_lists()
            print(f"\n✅ 第{args.regenerate}章重新生成完成！")
        else:
            print(f"\n❌ 第{args.regenerate}章重新生成失敗")
    
    elif args.daily:
        # 生成每日章節
        success = generate_daily_chapter()
        if success:
            print("\n✅ 每日章節生成完成！")
        else:
            print("\n❌ 每日章節生成失敗")
    
    else:
        # 默認生成下一章
        success = generate_daily_chapter()
        if success:
            print("\n✅ 章節生成完成！")
        else:
            print("\n❌ 章節生成失敗")

if __name__ == "__main__":
    main()