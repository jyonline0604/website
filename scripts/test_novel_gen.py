#!/usr/bin/env python3
"""
測試小說生成
"""

import os
import sys
import requests

# 設置環境變量
os.environ['PATH'] = '/home/openclaw/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'

WORKSPACE = "/home/openclaw/.openclaw/workspace"

# 從環境變量獲取API密鑰
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    # 從文件讀取
    env_file = os.path.join(WORKSPACE, ".env")
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith("OPENROUTER_API_KEY="):
                    OPENROUTER_API_KEY = line.strip().split("=", 1)[1]
                    break

if not OPENROUTER_API_KEY:
    print("❌ 錯誤：未設置 OPENROUTER_API_KEY")
    sys.exit(1)

print(f"API Key: {OPENROUTER_API_KEY[:20]}...")

# 測試API
headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "minimax/minimax-m2.7",
    "messages": [
        {"role": "system", "content": "你是一位小說作家。"},
        {"role": "user", "content": "寫一段100字的小說開頭，關於科技修真。"}
    ],
    "max_tokens": 200,
    "temperature": 0.7
}

try:
    print("調用API...")
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=30
    )
    
    print(f"狀態碼: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        print(f"成功！內容長度: {len(content)}")
        print(f"內容前100字: {content[:100]}...")
    else:
        print(f"錯誤: {response.text}")
        
except Exception as e:
    print(f"異常: {e}")
    import traceback
    traceback.print_exc()