#!/usr/bin/env python3
"""
有聲畫小説章節生成器
用法: python3 generate_av_chapter.py <章節號>
例如: python3 generate_av_chapter.py 14
"""

import sys
import os
import subprocess
import requests
import json

# 設定
WORKSPACE = "/home/openclaw/.openclaw/workspace"
NOVEL_DIR = WORKSPACE
ASSETS_DIR = os.path.join(NOVEL_DIR, "assets")
TTS_SCRIPT = os.path.join(WORKSPACE, "scripts", "tts_minimax.py")

def get_api_key():
    auth_file = os.path.expanduser("~/.openclaw/agents/main/agent/auth-profiles.json")
    try:
        with open(auth_file, 'r') as f:
            data = json.load(f)
            profiles = data.get('profiles', {})
            return profiles.get('minimax:cn', {}).get('key') or profiles.get('minimax', {}).get('key')
    except:
        return os.environ.get('MINIMAX_API_KEY', '')

def extract_chapter_text(chapter_num):
    """從 HTML 提取章節文字"""
    html_file = os.path.join(NOVEL_DIR, f"chapter-{chapter_num}.html")
    if not os.path.exists(html_file):
        print(f"錯誤: 找不到 {html_file}")
        return None
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取 content div
    start = content.find('<div class="content">')
    end = content.find('</div>', start)
    if start == -1 or end == -1:
        print("錯誤: 無法找到章節內容")
        return None
    
    text = content[start:end]
    # 移除 HTML 標籤
    import re
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('"', '"').replace('"', '"').replace('——', '，')
    # 清理多餘空白
    text = ' '.join(text.split())
    
    return text[:50000]  # 限制長度

def generate_tts_edge(text, output_file):
    """使用 Edge TTS 生成音頻"""
    # 寫入臨時文件
    temp_file = "/tmp/tts_input.txt"
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(text)
    
    # Edge TTS 命令
    cmd = [
        "edge-tts",
        "--voice", "zh-HK-HiuGaaiNeural",
        "--file", temp_file,
        "--write-media", output_file
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"TTS 錯誤: {result.stderr}")
        return False
    return True

def generate_tts_minimax(text, output_file, voice="male-qn-qingse"):
    """使用 MiniMax TTS 生成音頻"""
    api_key = get_api_key()
    if not api_key:
        print("警告: 找不到 MiniMax API Key，跳過")
        return False
    
    url = "https://api.minimaxi.com/v1/t2a_v2"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "speech-2.8-hd",
        "text": text,
        "stream": False,
        "voice_setting": {
            "voice_id": voice,
            "speed": 1.0,
            "vol": 1,
            "pitch": 0,
            "emotion": "happy"
        },
        "audio_setting": {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3",
            "channel": 1
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        result = response.json()
        if result.get('base_resp', {}).get('status_code') == 0:
            audio_hex = result.get('data', {}).get('audio')
            if audio_hex:
                audio_data = bytes.fromhex(audio_hex)
                with open(output_file, 'wb') as f:
                    f.write(audio_data)
                return True
        print(f"MiniMax TTS 錯誤: {result}")
        return False
    except Exception as e:
        print(f"MiniMax TTS 異常: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("用法: python3 generate_av_chapter.py <章節號>")
        print("例如: python3 generate_av_chapter.py 14")
        sys.exit(1)
    
    chapter_num = int(sys.argv[1])
    prev_chapter = chapter_num - 1
    
    print(f"=== 開始生成第 {chapter_num} 章有聲畫 ===")
    
    # 1. 提取文字
    print("1. 提取章節文字...")
    text = extract_chapter_text(chapter_num)
    if not text:
        sys.exit(1)
    print(f"   文字長度: {len(text)} 字")
    
    # 2. 生成音頻
    print("2. 生成音頻...")
    audio_file = os.path.join(ASSETS_DIR, f"chapter{chapter_num}_audio.mp3")
    
    # 先嘗試 MiniMax TTS
    tts_success = generate_tts_minimax(text, audio_file)
    if not tts_success:
        print("   MiniMax TTS 失敗，改用 Edge TTS...")
        tts_success = generate_tts_edge(text, audio_file)
    
    if not tts_success:
        print("錯誤: 音頻生成失敗")
        sys.exit(1)
    
    # 檢查音頻文件
    if os.path.getsize(audio_file) < 10000:
        print(f"警告: 音頻文件太小 ({os.path.getsize(audio_file)} bytes)，可能生成失敗")
    
    print(f"   音頻: {audio_file} ({os.path.getsize(audio_file)} bytes)")
    
    print(f"\n=== 第 {chapter_num} 章素材已準備 ===")
    print(f"音頻: {audio_file}")
    print(f"\n請先查看章節內容，再生成符合劇情的場景圖片：")
    print(f"查看章節: cat {os.path.join(NOVEL_DIR, f'chapter-{chapter_num}.html')} | head -c 2000")
    print(f"然後生成3張符合該章節實際劇情的圖片")

if __name__ == "__main__":
    main()
