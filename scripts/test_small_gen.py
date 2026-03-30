#!/usr/bin/env python3
"""
小規模測試DeepSeek原生API生成
"""

import os
import sys
import requests
from datetime import datetime

WORKSPACE = "/home/openclaw/.openclaw/workspace"

def get_deepseek_api_key():
    """獲取DeepSeek原生API密鑰"""
    env_file = os.path.join(WORKSPACE, ".env")
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith("DEEPSEEK_API_KEY="):
                    return line.strip().split("=", 1)[1]
    return None

def test_small_generation():
    """測試小規模生成"""
    print("=== 小規模DeepSeek生成測試 ===\n")
    
    api_key = get_deepseek_api_key()
    if not api_key:
        print("❌ 未找到API密鑰")
        return False
    
    print(f"✅ API密鑰找到: {api_key[:8]}...")
    
    # 簡單的測試提示
    prompt = "請寫小說《科技修真傳》第67章的標題和第一段（100字左右）。標題格式：第67章：XXXXXX"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是專業小說作家。"},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 200,
        "temperature": 0.7,
        "stream": False
    }
    
    try:
        print("發送請求到DeepSeek API...")
        start_time = datetime.now()
        
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"請求耗時: {elapsed:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            print(f"\n✅ 生成成功！")
            print(f"模型: {result.get('model', '未知')}")
            print(f"內容:\n{content}")
            
            # 顯示使用量
            if "usage" in result:
                usage = result["usage"]
                print(f"\nToken使用:")
                print(f"  輸入: {usage.get('prompt_tokens', 0)} tokens")
                print(f"  輸出: {usage.get('completion_tokens', 0)} tokens")
                print(f"  總計: {usage.get('total_tokens', 0)} tokens")
            
            return True
        else:
            print(f"\n❌ 請求失敗: {response.status_code}")
            print(f"錯誤: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n❌ 請求超時（30秒）")
        return False
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        return False

if __name__ == "__main__":
    success = test_small_generation()
    sys.exit(0 if success else 1)