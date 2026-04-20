#!/usr/bin/env python3
"""
測試 ByteDance Seedance 2.0 Fast 影片生成 API

使用方法:
    python3 test_seedance_api.py

通過 OpenRouter API 生成影片
"""

import requests
import json
import os
import time

# OpenRouter API 配置
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')

# 如果沒有，通過其他方式獲取
if not OPENROUTER_API_KEY:
    # 嘗試從配置文件讀取
    config_file = os.path.expanduser('~/.openclaw/openclaw.json')
    try:
        import json
        with open(config_file, 'r') as f:
            config = json.load(f)
            # 查找OpenRouter API key
            if 'auth' in config and 'profiles' in config['auth']:
                for key, profile in config['auth']['profiles'].items():
                    if 'apiKey' in profile:
                        OPENROUTER_API_KEY = profile['apiKey']
                        break
    except:
        pass

API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Seedance 2.0 Fast 模型名稱
MODEL = "bytedance/seedance-2.0-fast"

def test_seedance_api():
    """測試 Seedance 2.0 Fast API"""
    
    if not OPENROUTER_API_KEY:
        print("❌ 找不到 OpenRouter API Key")
        print("請設置環境變量: export OPENROUTER_API_KEY=your_key")
        return False
    
    print("=== 測試 ByteDance Seedance 2.0 Fast API ===\n")
    print(f"模型: {MODEL}")
    print(f"API: {API_URL}\n")
    
    # 測試請求
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://kofhk.com",
        "X-Title": "科技修真傳"
    }
    
    # 測試請求 - 文本生成影片
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "生成一個5秒的科幻風格短影片，展示一個未來城市的夜景，充滿霓虹燈光和飛行汽車"
            }
        ],
        "max_tokens": 1000,
        "temperature": 0.7
    }
    
    print("發送測試請求...")
    print(f"提示詞: {payload['messages'][0]['content'][:50]}...\n")
    
    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=120
        )
        
        print(f"狀態碼: {response.status_code}")
        print(f"響應: {response.text[:1000]}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ API 連接成功！")
            print(f"Model: {result.get('model', 'N/A')}")
            
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0].get('message', {}).get('content', '')
                print(f"\n生成的內容:\n{content[:500]}")
            
            return True
        else:
            print(f"\n❌ API 錯誤: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"\n❌ 請求異常: {e}")
        return False

def check_api_credits():
    """檢查 OpenRouter 帳號 Credits"""
    if not OPENROUTER_API_KEY:
        print("❌ 找不到 API Key")
        return
    
    url = "https://openrouter.ai/api/v1/auth/key"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print("\n=== OpenRouter 帳號資訊 ===")
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ 無法獲取帳號資訊: {response.status_code}")
    except Exception as e:
        print(f"❌ 獲取帳號資訊失敗: {e}")

if __name__ == '__main__':
    print("=== Seedance 2.0 Fast 影片生成 API 測試 ===\n")
    
    # 先檢查 Credits
    check_api_credits()
    
    # 測試 API
    print("\n")
    test_seedance_api()