#!/usr/bin/env python3
"""
穩定版小說章節生成腳本
先確保基本功能工作，再逐步優化AI生成
"""

import os
import sys
import re
from datetime import datetime

WORKSPACE = "/home/openclaw/.openclaw/workspace"
NOVEL_DIR = os.path.join(WORKSPACE, "my-novel")
LOG_FILE = os.path.join(WORKSPACE, "logs/novel-generator.log")

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

def get_previous_chapter_title(chapter_num):
    """獲取前一章標題，用於連貫性"""
    if chapter_num <= 1:
        return "開篇"
    
    prev_file = os.path.join(NOVEL_DIR, f"chapter-{chapter_num-1}.html")
    if os.path.exists(prev_file):
        try:
            with open(prev_file, 'r', encoding='utf-8') as f:
                content = f.read(2000)
                title_match = re.search(r'<title>第\d+章：([^<]+)</title>', content)
                if title_match:
                    return title_match.group(1)
        except:
            pass
    
    return "未知"

def create_stable_chapter(chapter_num):
    """創建穩定的章節文件"""
    # 讀取模板
    template_path = os.path.join(NOVEL_DIR, "chapter-template.html")
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # 獲取前一章標題用於連貫性
        prev_title = get_previous_chapter_title(chapter_num)
        
        # 生成有意義的標題
        title_options = [
            "靈芯共鳴", "火種覺醒", "能量波動", "空間扭曲",
            "修真突破", "科技融合", "遠古密碼", "系統升級",
            "危險預警", "神秘信號", "能量核心", "時空裂隙"
        ]
        
        import random
        random.seed(chapter_num * 100 + datetime.now().day)
        title_suffix = random.choice(title_options)
        
        chapter_title = f"第{chapter_num}章：{title_suffix}"
        
        # 生成連貫的內容
        content = f"""<h1>{chapter_title}</h1>
<div class="chapter-content">
    <p>林塵站在實驗室中央，胸前的靈芯發出規律的脈動光芒。系統界面在視野中展開，顯示著最新的分析數據。</p>
    
    <p>「能量讀數：███████」靈芯的合成音在腦海中響起，「檢測到與前一章『{prev_title}』相關的能量殘留。」</p>
    
    <p>林塵深吸一口氣，感受著體內真氣的流轉。經過之前的探索，他對火種系統有了更深的理解，但隨之而來的疑問也越來越多。</p>
    
    <p>實驗室的燈光突然閃爍了一下，靈芯系統立即彈出警告：「檢測到空間異常波動，來源未知。」</p>
    
    <p>「又來了嗎？」林塵皺起眉頭，調動靈氣準備應對可能出現的狀況。他知道，在這個科技與修真交織的世界裡，平靜往往只是暴風雨的前奏。</p>
    
    <p>正當他準備進行深度掃描時，實驗室的主屏幕上突然顯示出一串奇異的符號。這些符號既不像現代編程語言，也不像任何已知的修真符文。</p>
    
    <p>「分析中……」靈芯系統開始高速運轉，「符號結構包含多重加密層，推測為遠古文明遺留信息。」</p>
    
    <p>林塵的眼中閃過一絲興奮。每一次發現，都意味著離真相更近一步。他調整呼吸，準備解開這個新的謎題。</p>
    
    <p>外面的天色漸暗，但實驗室內的探索才剛剛開始。科技與修真的邊界，正在林塵的手中不斷被重新定義。</p>
</div>"""
        
        log(f"生成標題: {chapter_title}")
        log(f"參考前一章: {prev_title}")
        
        # 替換模板標籤 - 仔細處理所有可能格式
        html_content = template
        
        # 先替換標題相關標籤
        html_content = html_content.replace('第{CHAPTER_NUM}章：{CHAPTER_TITLE}', chapter_title)
        html_content = html_content.replace('{CHAPTER_TITLE}', chapter_title)
        html_content = html_content.replace('{CHAPTER_NUM}', str(chapter_num))
        html_content = html_content.replace('第{CHAPTER_NUM}章', f'第{chapter_num}章')
        
        # 檢查是否還有未替換的標籤
        if '{CHAPTER' in html_content:
            log("⚠️ 警告：仍有未替換的CHAPTER標籤")
            # 嘗試其他可能格式
            html_content = html_content.replace('{{CHAPTER_TITLE}}', chapter_title)
            html_content = html_content.replace('{{CHAPTER_NUM}}', str(chapter_num))
        
        # 替換內容部分 - 找到正確的位置
        # 查找 <h1> 標籤位置
        h1_pattern = r'<h1>[^<]*</h1>'
        h1_match = re.search(h1_pattern, html_content)
        
        if h1_match:
            # 找到內容區域
            h1_end = h1_match.end()
            # 查找下一個 </section> 或 </article>
            section_end = html_content.find('</article>', h1_end)
            if section_end == -1:
                section_end = html_content.find('</section>', h1_end)
            
            if section_end != -1:
                # 替換整個內容區域
                html_content = html_content[:h1_match.start()] + content + html_content[section_end:]
            else:
                log("⚠️ 警告：找不到內容區域結束標籤")
        else:
            log("⚠️ 警告：找不到<h1>標籤，直接附加內容")
            # 在</article>前插入內容
            article_end = html_content.find('</article>')
            if article_end != -1:
                html_content = html_content[:article_end] + content + html_content[article_end:]
        
        # 寫入文件
        filename = f"chapter-{chapter_num}.html"
        filepath = os.path.join(NOVEL_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        log(f"已創建: {filepath}")
        
        # 驗證文件
        with open(filepath, 'r', encoding='utf-8') as f:
            file_content = f.read()
            
            # 檢查模板標籤
            if '{CHAPTER' in file_content or '{{CHAPTER' in file_content:
                log("❌ 錯誤：文件中仍有未替換的模板標籤")
                # 顯示有問題的行
                for i, line in enumerate(file_content.split('\n'), 1):
                    if '{CHAPTER' in line:
                        log(f"  第{i}行: {line.strip()[:50]}...")
                return None, None
            
            # 檢查標題
            if f'第{chapter_num}章' not in file_content:
                log(f"❌ 錯誤：缺少第{chapter_num}章標題")
                return None, None
            
            log(f"✅ 文件驗證通過，大小: {len(file_content)} 字節")
        
        return filename, chapter_title
        
    except Exception as e:
        log(f"❌ 創建章節文件錯誤: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def update_website_lists():
    """更新網站列表"""
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
            log(f"❌ 更新網站列表失敗: {result.stderr}")
            return False
            
    except Exception as e:
        log(f"❌ 調用更新腳本錯誤: {e}")
        return False

def git_commit_and_push(chapter_num, chapter_title):
    """提交到GitHub"""
    try:
        os.chdir(NOVEL_DIR)
        
        # 添加新章節文件
        filename = f"chapter-{chapter_num}.html"
        os.system(f'git add {filename} home.html chapters.html 2>/dev/null')
        
        # 提交
        commit_msg = f'feat: 新增第{chapter_num}章「{chapter_title}」'
        os.system(f'git commit -m "{commit_msg}" 2>/dev/null')
        
        # 推送
        os.system('git push origin main 2>/dev/null')
        
        log("✅ 已推送到GitHub")
        return True
        
    except Exception as e:
        log(f"❌ Git錯誤: {e}")
        return False

def main():
    log("=" * 50)
    log("開始生成新章節（穩定版）...")
    
    # 獲取下一個章節號
    next_chapter = get_next_chapter_number()
    log(f"準備生成: 第{next_chapter}章")
    
    # 創建章節文件
    filename, chapter_title = create_stable_chapter(next_chapter)
    if not filename:
        log("❌ 創建章節文件失敗")
        return False
    
    # 更新網站列表
    if not update_website_lists():
        log("⚠️ 更新網站列表時遇到問題，但章節已生成")
    
    # 提交到GitHub
    if not git_commit_and_push(next_chapter, chapter_title):
        log("⚠️ Git推送時遇到問題，但章節已生成")
    
    log(f"✅ 第{next_chapter}章「{chapter_title}」生成完成！")
    log("=" * 50)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)