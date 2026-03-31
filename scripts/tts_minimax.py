#!/usr/bin/env python3
"""
MiniMax Text-to-Speech HD API 客戶端
"""

import requests
import json
import sys
import os
import argparse

API_URL = "https://api.minimaxi.com/v1/t2a_v2"

def get_api_key():
    auth_file = os.path.expanduser("~/.openclaw/agents/main/agent/auth-profiles.json")
    try:
        with open(auth_file, 'r') as f:
            data = json.load(f)
            profiles = data.get('profiles', {})
            minimax_key = profiles.get('minimax:cn', {}).get('key') or profiles.get('minimax', {}).get('key')
            if minimax_key:
                return minimax_key
    except:
        pass
    return os.environ.get('MINIMAX_API_KEY', '')

VOICES = {
    "male-qn-qingse": "男聲-清脆",
    "male-qn-bailing": "男聲-低沉",
    "male-tianmei": "男聲-甜美",
    "male-yunyang": "男聲-活力",
    "male-zhiqi": "男聲-知性",
    "male-qingyin": "男聲-青春",
    "female-shaoyu": "女聲-少御",
    "female-zhongtan": "女聲-御姐",
    "female-baiying": "女聲-磁性",
    "female-xiaoyuan": "女聲-可愛",
    "female-hongzhen": "女聲-溫柔",
    "female-tianmei": "女聲-甜美",
}

MODELS = {
    "speech-2.8-hd": "Speech 2.8 HD",
    "speech-2.8-turbo": "Speech 2.8 Turbo",
    "speech-02-hd": "Speech 02 HD",
    "speech-01-hd": "Speech 01 HD",
}

def generate_speech(text, output_file="output.mp3", voice_id="female-shaoyu", model="speech-2.8-hd", speed=1.0, emotion="happy"):
    api_key = get_api_key()
    if not api_key:
        print("錯誤: 找不到 MiniMax API Key")
        return False
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "text": text,
        "stream": False,
        "voice_setting": {
            "voice_id": voice_id,
            "speed": speed,
            "vol": 1,
            "pitch": 0,
            "emotion": emotion
        },
        "audio_setting": {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3",
            "channel": 1
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        
        if result.get('base_resp', {}).get('status_code') == 0:
            audio_hex = result.get('data', {}).get('audio')
            if audio_hex:
                audio_data = bytes.fromhex(audio_hex)
                with open(output_file, 'wb') as f:
                    f.write(audio_data)
                print(f"✅ 已保存: {output_file}")
                return True
        
        print(f"❌ API錯誤: {result}")
        return False
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='MiniMax TTS HD')
    parser.add_argument('text', help='要轉換為語音的文字')
    parser.add_argument('-o', '--output', default='output.mp3', help='輸出文件名')
    parser.add_argument('-v', '--voice', default='male-qn-bailing', choices=list(VOICES.keys()), help='語音選擇')
    parser.add_argument('-m', '--model', default='speech-2.8-hd', choices=list(MODELS.keys()), help='模型選擇')
    parser.add_argument('-s', '--speed', type=float, default=1.0, help='語速')
    parser.add_argument('-e', '--emotion', default='happy', choices=['happy', 'sad', 'angry', 'fearful', 'disgusted', 'surprised'], help='情緒')
    parser.add_argument('--list-voices', action='store_true', help='列出所有可用語音')
    
    args = parser.parse_args()
    
    if args.list_voices:
        print("可用語音:")
        for vid, name in VOICES.items():
            print(f"  {vid}: {name}")
        return
    
    success = generate_speech(args.text, args.output, args.voice, args.model, args.speed, args.emotion)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
