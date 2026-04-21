#!/usr/bin/env python3
"""
測試 ByteDance Seedance 2.0 Fast 視頻生成 API

通過 OpenRouter 的 /api/v1/videos 端點生成視頻
"""

import requests
import json
import time
import os

# OpenRouter API Key
API_KEY = "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"

# API 端點
VIDEOS_URL = "https://openrouter.ai/api/v1/videos"

def test_video_generation():
    """測試 Seedance 2.0 Fast 視頻生成"""
    
    print("=== 測試 ByteDance Seedance 2.0 Fast 視頻生成 ===\n")
    
    # Step 1: 提交視頻生成請求
    print("1. 提交視頻生成請求...")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": "bytedance/seedance-2.0-fast",
        "prompt": "A serene mountain landscape at sunset with clouds drifting by"
    }
    
    try:
        response = requests.post(
            url=VIDEOS_URL,
            headers=headers,
            data=json.dumps(payload),
            timeout=60
        )
        
        print(f"狀態碼: {response.status_code}")
        print(f"響應: {response.text[:500]}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ 請求成功！")
            
            job_id = result.get("id")
            polling_url = result.get("polling_url")
            
            print(f"Job ID: {job_id}")
            print(f"Polling URL: {polling_url}")
            
            if job_id and polling_url:
                # Step 2: 輪詢完成狀態
                print("\n2. 等待視頻生成完成...")
                
                while True:
                    poll_response = requests.get(
                        url=polling_url,
                        headers=headers,
                        timeout=30
                    )
                    
                    if poll_response.status_code == 200:
                        status_data = poll_response.json()
                        status = status_data.get("status", "unknown")
                        print(f"   Status: {status}")
                        
                        if status == "completed":
                            unsigned_urls = status_data.get("unsigned_urls", [])
                            if unsigned_urls:
                                print(f"\n✅ 視頻生成完成！")
                                print(f"視頻 URL: {unsigned_urls[0]}")
                            break
                        elif status == "failed":
                            print(f"❌ 視頻生成失敗: {status_data.get('error', 'Unknown error')}")
                            break
                        
                        time.sleep(5)
                    else:
                        print(f"輪詢請求失敗: {poll_response.status_code}")
                        break
            else:
                print("❌ 沒有獲得 job_id 或 polling_url")
        else:
            print(f"❌ 請求失敗: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ 異常: {e}")

if __name__ == "__main__":
    test_video_generation()