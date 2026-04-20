#!/usr/bin/env python3
"""
第1章6個場景視頻生成腳本
使用林塵角色圖片作為參考
"""

import json
import requests
import time
import os

API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/videos"
CHARACTER_IMAGE = "https://kofhk.com/assets/linchen-portrait-new.png"

# 6個場景的prompts
SCENES = [
    {
        "name": "scene1-wasteland",
        "prompt": "Young Chinese man in tattered military blanket crouching in darkness of abandoned skyscraper, cyberpunk wasteland atmosphere,铅云笼罩的天空, dim moonlight filtering through broken windows, ruins of advanced technology around, dust particles floating, tense and dramatic, cinematic vertical composition 9:16",
        "filename": "chapter1-scene1-wasteland.mp4"
    },
    {
        "name": "scene2-chip-awakening",
        "prompt": "Close-up of a young man's face illuminated by glowing blue chip, ancient black crystal chip embedded in wall glowing with ethereal blue light, dust and cobwebs around, his eyes widening in shock, electricity particles flowing from chip to his mind, dramatic light rays, mystical sci-fi atmosphere, vertical 9:16",
        "filename": "chapter1-scene2-chip-awakening.mp4"
    },
    {
        "name": "scene3-system-activation",
        "prompt": "Young Chinese man sitting meditation pose, holographic blue interface floating in his mind showing cultivation system interface, data streams and meridian maps appearing in air around him, soft blue glow emanating from his body, ethereal atmosphere, mystical tech fusion, vertical 9:16",
        "filename": "chapter1-scene3-system-activation.mp4"
    },
    {
        "name": "scene4-energy-absorption",
        "prompt": "Young Chinese man in meditation, wisps of white spiritual energy flowing from air into his body, subtle golden light particles surrounding him, dramatic backlighting, calm focused expression, cultivation world aesthetic, cinematic meditation scene, vertical 9:16",
        "filename": "chapter1-scene4-energy-absorption.mp4"
    },
    {
        "name": "scene5-escape",
        "prompt": "Young man leaping through ventilation shafts in abandoned cyberpunk building, cables and broken pipes around, blue glow trail behind him, camera following his fast movement, dust trails in air, dynamic action sequence, dramatic speed lines, vertical 9:16",
        "filename": "chapter1-scene5-escape.mp4"
    },
    {
        "name": "scene6-determined-eyes",
        "prompt": "Close-up of young Chinese man's eyes, determined and resolute gaze, blue energy faintly glowing in his pupils, lying in dark underground passage, shadows on face, dramatic lighting from above, epic inspirational mood, cinematic portrait, vertical 9:16",
        "filename": "chapter1-scene6-determined-eyes.mp4"
    }
]

def generate_video(scene_prompt, scene_name, filename):
    """生成單個視頻"""
    print(f"🚀 生成場景: {scene_name}")
    print(f"Prompt: {scene_prompt[:100]}...")
    
    payload = {
        "model": "bytedance/seedance-2.0-fast",
        "prompt": scene_prompt,
        "image": CHARACTER_IMAGE,
        "aspect_ratio": "9:16",
        "resolution": "720p"
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        # 提交生成請求
        response = requests.post(API_URL, headers=headers, json=payload)
        response_data = response.json()
        
        if "id" not in response_data:
            print(f"❌ 提交失敗: {response_data}")
            return None
            
        job_id = response_data["id"]
        polling_url = response_data["polling_url"]
        print(f"✅ 提交成功，Job ID: {job_id}")
        
        # 輪詢等待完成
        for i in range(30):
            time.sleep(5)
            poll_response = requests.get(polling_url, headers=headers)
            poll_data = poll_response.json()
            
            status = poll_data.get("status")
            print(f"  輪詢 {i+1}: 狀態 = {status}")
            
            if status == "completed":
                video_url = poll_data.get("unsigned_urls", [])[0]
                print(f"✅ 視頻生成完成: {video_url}")
                return video_url
            elif status == "failed":
                print(f"❌ 生成失敗: {poll_data}")
                return None
        
        print("❌ 超時")
        return None
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return None

def download_video(video_url, filename):
    """下載視頻"""
    print(f"📥 下載視頻: {filename}")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    
    try:
        response = requests.get(video_url, headers=headers, stream=True)
        response.raise_for_status()
        
        with open(f"assets/{filename}", "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size = os.path.getsize(f"assets/{filename}") / (1024 * 1024)
        print(f"✅ 下載完成: {filename} ({file_size:.1f} MB)")
        return True
        
    except Exception as e:
        print(f"❌ 下載失敗: {e}")
        return False

def main():
    print("🎬 開始生成第1章6個場景視頻")
    print(f"使用角色圖片: {CHARACTER_IMAGE}")
    print("=" * 50)
    
    results = []
    
    for i, scene in enumerate(SCENES, 1):
        print(f"\n📹 場景 {i}/6: {scene['name']}")
        print("-" * 30)
        
        # 生成視頻
        video_url = generate_video(scene["prompt"], scene["name"], scene["filename"])
        
        if video_url:
            # 下載視頻
            success = download_video(video_url, scene["filename"])
            if success:
                results.append({
                    "scene": scene["name"],
                    "filename": scene["filename"],
                    "url": video_url,
                    "status": "success"
                })
            else:
                results.append({
                    "scene": scene["name"],
                    "filename": scene["filename"],
                    "status": "download_failed"
                })
        else:
            results.append({
                "scene": scene["name"],
                "filename": scene["filename"],
                "status": "generation_failed"
            })
        
        # 場景之間等待一下
        if i < len(SCENES):
            print(f"⏳ 等待10秒後繼續...")
            time.sleep(10)
    
    # 輸出結果
    print("\n" + "=" * 50)
    print("🎬 生成結果總結")
    print("=" * 50)
    
    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"✅ 成功: {success_count}/6")
    
    for result in results:
        status_icon = "✅" if result["status"] == "success" else "❌"
        print(f"{status_icon} {result['scene']}: {result['status']}")
    
    # 保存結果到文件
    with open("assets/chapter1-video-results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 結果已保存到: assets/chapter1-video-results.json")

if __name__ == "__main__":
    main()