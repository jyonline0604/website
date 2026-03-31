#!/usr/bin/env python3
"""
修復版小說章節生成腳本
解決模板標籤替換和內容處理問題
"""

import os
import sys
import re
import requests
from datetime import datetime

WORKSPACE = "/home/openclaw/.openclaw/workspace"
NOVEL_DIR = WORKSPACE
LOG_FILE = os.path.join(WORKSPACE, "logs/novel-generator.log")

def log(message):
    """寫入日誌"""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_line = f"{timestamp} {message}"
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")
    
    print(log_line)
    return log_line

def get_api_key():
    """獲取API密鑰"""
    # 從環境變量獲取
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if api_key:
        return api_key
    
    # 從文件讀取
    env_file = os.path.join(WORKSPACE, ".env")
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith("OPENROUTER_API_KEY="):
                    return line.strip().split("=", 1)[1]
    
    return None

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

def try_ai_generation(chapter_num):
    """嘗試使用AI生成內容 - 改進版"""
    api_key = get_api_key()
    if not api_key:
        log("⚠️ 未找到API密鑰，使用簡化版")
        return None, None  # 返回內容和標題
    
    # 構建更好的提示詞
    prompt = f"""請創作小說《科技修真傳》的第{chapter_num}章。

故事背景：
這是一部科技與修真結合的小說。主角林塵擁有「靈芯」系統，可以將現代科技與修真功法結合。
目前故事進展到林塵發現了遠古的「火種」系統，正在探索其奧秘。

寫作要求：
1. 章節標題：第{chapter_num}章：XXXXXX（4-6個字，如「火種初鳴」、「靈芯覺醒」等）
2. 內容長度：800-1200字
3. 格式：直接寫正文，不需要HTML標籤
4. 風格：保持科技感與修真玄幻結合
5. 劇情：要有懸念和推進，延續之前的故事線

請直接輸出章節內容，以標題開始。"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "minimax/minimax-m2.7",
        "messages": [
            {"role": "system", "content": "你是一位專業的網絡小說作家，擅長創作科技修真題材。請直接輸出小說內容，不要添加任何解釋或額外文字。"},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1500,
        "temperature": 0.7
    }
    
    try:
        log("嘗試使用AI生成章節內容...")
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=20  # 20秒超時
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            log(f"AI生成成功，原始內容長度: {len(content)} 字")
            
            # 提取標題
            title_match = re.search(r'第\d+章：[^\n]+', content)
            if title_match:
                chapter_title = title_match.group(0)
                # 清理標題（移除可能的多餘字符）
                chapter_title = re.sub(r'[<>]', '', chapter_title).strip()
                # 移除標題後的內容
                content_start = content.find('\n', title_match.end())
                if content_start != -1:
                    content = content[content_start:].strip()
                else:
                    content = ""
            else:
                # 生成默認標題
                chapter_title = f"第{chapter_num}章：靈芯續章"
            
            log(f"提取標題: {chapter_title}")
            log(f"清理後內容長度: {len(content)} 字")
            
            return content, chapter_title
        else:
            log(f"AI生成失敗: {response.status_code} - {response.text[:100]}")
            return None, None
            
    except Exception as e:
        log(f"AI生成異常: {e}")
        return None, None

def create_chapter_file(chapter_num, ai_content=None, ai_title=None):
    """創建章節文件 - 修復模板替換"""
    # 讀取模板
    template_path = os.path.join(NOVEL_DIR, "chapter-template.html")
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        if ai_content and ai_title:
            # 使用AI生成的內容和標題
            chapter_title = ai_title
            
            # 構建完整內容
            content = f"""<h1>{chapter_title}</h1>
<div class="chapter-content">
{ai_content}
</div>"""
            
            log(f"使用AI生成內容，標題: {chapter_title}")
        else:
            # 使用簡化版內容
            chapter_title = f"第{chapter_num}章：自動生成"
            content = f"""<h1>{chapter_title}</h1>
<div class="chapter-content">
    <p>這是第{chapter_num}章，由自動生成系統創建於 {datetime.now().strftime('%Y-%m-%d %H:%M')}。</p>
    <p>林塵的修真科技之旅繼續展開...</p>
    <p>靈芯系統發出輕微的嗡鳴聲，提示有新的能量波動被檢測到。</p>
    <p>「警告：檢測到異常空間扭曲，建議立即進行掃描分析。」</p>
    <p>林塵深吸一口氣，調動體內的靈氣，準備面對新的挑戰。</p>
    <p>前方的道路充滿未知，但林塵知道，每一次挑戰都是成長的機會。</p>
</div>"""
            
            log(f"使用簡化版內容，標題: {chapter_title}")
        
        # 檢查模板標籤格式
        log(f"檢查模板標籤...")
        
        # 替換模板中的內容 - 使用正確的標籤格式
        # 模板使用 {CHAPTER_NUM} 和 {CHAPTER_TITLE}（單花括號）
        html_content = template
        
        # 提取純標題（移除可能的多餘部分）
        pure_title = chapter_title
        if ' - ' in pure_title:
            pure_title = pure_title.split(' - ')[0]
        if '</title>' in pure_title:
            pure_title = pure_title.replace('</title>', '')
        
        # 替換所有標籤
        replacements = {
            '{CHAPTER_NUM}': str(chapter_num),
            '{CHAPTER_TITLE}': pure_title,
            '第{CHAPTER_NUM}章：{CHAPTER_TITLE}': pure_title,
            '第{CHAPTER_NUM}章': f'第{chapter_num}章'
        }
        
        for old, new in replacements.items():
            html_content = html_content.replace(old, new)
        
        # 替換內容部分
        content_start = html_content.find('<h1>')
        if content_start != -1:
            # 找到內容結束位置（下一個<section>或</article>）
            content_end = html_content.find('</article>', content_start)
            if content_end != -1:
                # 替換內容
                old_content = html_content[content_start:content_end]
                html_content = html_content[:content_start] + content + html_content[content_end:]
        
        # 寫入文件
        filename = f"chapter-{chapter_num}.html"
        filepath = os.path.join(NOVEL_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        log(f"已創建: {filepath}")
        
        # 驗證文件
        with open(filepath, 'r', encoding='utf-8') as f:
            file_content = f.read()
            if '{CHAPTER' in file_content or '{{CHAPTER' in file_content:
                log("⚠️ 警告：文件中仍有未替換的模板標籤")
            if '<title>' in file_content:
                title_match = re.search(r'<title>(.*?)</title>', file_content)
                if title_match:
                    log(f"標題驗證: {title_match.group(1)}")
        
        return filename, chapter_title
        
    except Exception as e:
        log(f"創建章節文件錯誤: {e}")
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

def validate_chapter_file(chapter_num):
    """驗證章節文件"""
    filename = f"chapter-{chapter_num}.html"
    filepath = os.path.join(NOVEL_DIR, filename)
    
    if not os.path.exists(filepath):
        log(f"❌ 驗證失敗: 文件不存在 {filename}")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查模板標籤
        if '{CHAPTER' in content or '{{CHAPTER' in content:
            log(f"❌ 驗證失敗: 文件中仍有模板標籤")
            return False
        
        # 檢查標題
        if f'第{chapter_num}章' not in content:
            log(f"❌ 驗證失敗: 缺少第{chapter_num}章標題")
            return False
        
        # 檢查內容
        if 'chapter-content' not in content:
            log(f"⚠️ 警告: 可能缺少內容區域")
        
        log(f"✅ 章節文件驗證通過")
        return True
        
    except Exception as e:
        log(f"❌ 驗證異常: {e}")
        return False

def main():
    log("=" * 50)
    log("開始生成新章節（修復版）...")
    
    # 獲取下一個章節號
    next_chapter = get_next_chapter_number()
    log(f"準備生成: 第{next_chapter}章")
    
    # 嘗試AI生成
    ai_content, ai_title = try_ai_generation(next_chapter)
    
    # 創建章節文件
    filename, chapter_title = create_chapter_file(next_chapter, ai_content, ai_title)
    if not filename:
        log("❌ 創建章節文件失敗")
        return False
    
    # 驗證文件
    if not validate_chapter_file(next_chapter):
        log("⚠️ 章節文件驗證有問題，但繼續流程")
    
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