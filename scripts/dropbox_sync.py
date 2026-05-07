#!/usr/bin/env python3
"""
Dropbox 小說章節同步腳本
自動監控 Dropbox/萬古塵埃/第一卷/ 資料夾，下載新章節並更新網站
"""

import dropbox
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path

# ==== 設定 ====
TOKEN_FILE = '/home/openclaw/.openclaw/workspace/.token-store/dropbox-token.txt'
WORKSPACE = '/home/openclaw/.openclaw/workspace'
TRACK_FILE = '/home/openclaw/.openclaw/workspace/.dropbox-sync/state.json'
DROPBOX_FOLDER = '/萬古塵埃/第一卷'
LOCAL_FOLDER = '/home/openclaw/.openclaw/workspace/novel-chapters-dropbox'

# ==== 工具函數 ====
def load_token():
    with open(TOKEN_FILE, 'r') as f:
        return f.read().strip()

def load_state():
    if os.path.exists(TRACK_FILE):
        with open(TRACK_FILE, 'r') as f:
            return json.load(f)
    return {'processed': {}, 'last_check': None}

def save_state(state):
    os.makedirs(os.path.dirname(TRACK_FILE), exist_ok=True)
    with open(TRACK_FILE, 'w') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def get_file_hash(content):
    return hashlib.md5(content).hexdigest()

def parse_chapter_number(filename):
    """從檔案名稱提取章節號，如 '第一章 落葉歸根.txt' -> 1"""
    import re
    match = re.search(r'第(\d+)章', filename)
    if match:
        return int(match.group(1))
    return None

def generate_chapter_html(txt_path, chapter_num, title):
    """將純文字章節轉換為 HTML"""
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 處理分段（空行分隔）
    paragraphs = []
    for block in content.split('\n\n'):
        block = block.strip()
        if block:
            # 處理手動換行（單個換行->space，雙換行->段落）
            lines = block.split('\n')
            para = ' '.join(line.strip() for line in lines if line.strip())
            if para:
                paragraphs.append(f'<p>{para}</p>')
    
    chapter_html = f'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>第{chapter_num}章 {title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Noto Serif TC', serif; max-width: 800px; margin: 0 auto; padding: 2rem; line-height: 1.8; background: #1a1a2e; color: #e0e0e0; }}
        h1 {{ color: #00d4ff; border-bottom: 2px solid #00d4ff; padding-bottom: 0.5rem; }}
        p {{ margin: 1rem 0; text-align: justify; }}
        .nav {{ display: flex; justify-content: space-between; margin: 2rem 0; padding: 1rem; background: #16213e; border-radius: 8px; }}
        .nav a {{ color: #00d4ff; text-decoration: none; padding: 0.5rem 1rem; border: 1px solid #00d4ff; border-radius: 4px; }}
        .nav a:hover {{ background: #00d4ff; color: #1a1a2e; }}
    </style>
</head>
<body>
    <h1>第{chapter_num}章 {title}</h1>
    <div class="content">
        {''.join(paragraphs)}
    </div>
    <div class="nav">
        <a href="chapter-{chapter_num-1}.html">← 上一章</a>
        <a href="index.html">目錄</a>
        <a href="chapter-{chapter_num+1}.html">下一章 →</a>
    </div>
</body>
</html>'''
    return chapter_html

# ==== 主流程 ====
def sync():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 開始同步 Dropbox...")
    
    token = load_token()
    dbx = dropbox.Dropbox(token)
    state = load_state()
    
    # 確保本地資料夾存在
    os.makedirs(LOCAL_FOLDER, exist_ok=True)
    os.makedirs(f'{LOCAL_FOLDER}/chapters', exist_ok=True)
    
    new_files = []
    
    # 列出 Dropbox 資料夾
    try:
        result = dbx.files_list_folder(DROPBOX_FOLDER)
    except Exception as e:
        print(f"❌ 無法訪問 Dropbox 資料夾: {e}")
        return
    
    for entry in result.entries:
        if not isinstance(entry, dropbox.files.FileMetadata):
            continue
        if not entry.name.endswith('.txt'):
            continue
        
        chapter_num = parse_chapter_number(entry.name)
        if chapter_num is None:
            continue
        
        file_hash = entry.id  # Use Dropbox file ID as unique identifier
        
        # 檢查是否需要下載
        if file_hash in state['processed']:
            continue
        
        print(f"📥 發現新章節: {entry.name}")
        
        # 下載檔案
        try:
            _, response = dbx.files_download(entry.path_display)
            content = response.content
        except Exception as e:
            print(f"  ❌ 下載失敗: {e}")
            continue
        
        # 保存到本地
        local_path = f'{LOCAL_FOLDER}/chapters/{entry.name}'
        with open(local_path, 'wb') as f:
            f.write(content)
        
        print(f"  ✅ 下載完成: {local_path}")
        
        # 更新狀態
        state['processed'][file_hash] = {
            'filename': entry.name,
            'chapter_num': chapter_num,
            'path': local_path,
            'server_modified': str(entry.server_modified),
            'downloaded_at': datetime.now().isoformat()
        }
        
        new_files.append({
            'num': chapter_num,
            'name': entry.name,
            'path': local_path
        })
    
    # 排序處理
    new_files.sort(key=lambda x: x['num'])
    
    if new_files:
        print(f"\n📊 本次同步: {len(new_files)} 個新章節")
        for f in new_files:
            print(f"   CH{f['num']:03d}: {f['name']}")
    else:
        print("✅ 沒有新章節需要同步")
    
    state['last_check'] = datetime.now().isoformat()
    save_state(state)
    
    return new_files

if __name__ == '__main__':
    sync()