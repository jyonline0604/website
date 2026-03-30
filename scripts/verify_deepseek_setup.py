#!/usr/bin/env python3
"""
驗證DeepSeek生成系統設置
"""

import os
import sys
import re

WORKSPACE = "/home/openclaw/.openclaw/workspace"

def check_setup():
    """檢查系統設置"""
    print("=== DeepSeek生成系統設置驗證 ===\n")
    
    # 1. 檢查API密鑰
    print("1. 檢查API密鑰...")
    env_file = os.path.join(WORKSPACE, ".env")
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith("OPENROUTER_API_KEY="):
                    key = line.strip().split("=", 1)[1]
                    if key and len(key) > 20:
                        print(f"   ✅ API密鑰找到: {key[:10]}...{key[-10:]}")
                        break
            else:
                print("   ❌ 未找到OPENROUTER_API_KEY")
    else:
        print("   ❌ .env文件不存在")
    
    # 2. 檢查腳本文件
    print("\n2. 檢查腳本文件...")
    scripts = [
        "generate_chapter_deepseek.py",
        "generate_chapter_direct.py", 
        "novel-daily-generator.sh",
        "update_novel_lists.py"
    ]
    
    for script in scripts:
        path = os.path.join(WORKSPACE, "scripts", script)
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"   ✅ {script}: {size} 字節")
        else:
            print(f"   ❌ {script}: 不存在")
    
    # 3. 檢查模型配置
    print("\n3. 檢查DeepSeek模型配置...")
    deepseek_script = os.path.join(WORKSPACE, "scripts", "generate_chapter_deepseek.py")
    if os.path.exists(deepseek_script):
        with open(deepseek_script, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 檢查模型ID
            model_match = re.search(r'"model":\s*"([^"]+)"', content)
            if model_match:
                model_id = model_match.group(1)
                print(f"   ✅ 模型ID: {model_id}")
                
                if "deepseek" in model_id.lower():
                    print(f"   ✅ 使用DeepSeek模型")
                else:
                    print(f"   ⚠️ 不是DeepSeek模型: {model_id}")
            
            # 檢查上下文長度
            if "163840" in content:
                print(f"   ✅ 支持163,840 tokens上下文")
            
            # 檢查備用方案
            if "備用方案" in content or "generate_chapter_direct.py" in content:
                print(f"   ✅ 有備用方案")
    
    # 4. 檢查小說目錄
    print("\n4. 檢查小說目錄結構...")
    novel_dir = os.path.join(WORKSPACE, "my-novel")
    if os.path.exists(novel_dir):
        chapters = [f for f in os.listdir(novel_dir) if f.startswith("chapter-") and f.endswith(".html")]
        chapters.sort()
        
        print(f"   ✅ 找到 {len(chapters)} 個章節文件")
        print(f"   最新5章: {chapters[-5:] if len(chapters) >= 5 else chapters}")
        
        # 檢查最新章節
        if chapters:
            latest = chapters[-1]
            match = re.match(r"chapter-(\d+)\.html", latest)
            if match:
                latest_num = int(match.group(1))
                print(f"   最新章節: 第{latest_num}章")
                
                # 檢查內容
                latest_path = os.path.join(novel_dir, latest)
                with open(latest_path, 'r', encoding='utf-8') as f:
                    latest_content = f.read(1000)
                    if "林塵" in latest_content or "靈芯" in latest_content:
                        print(f"   ✅ 最新章節有內容")
                    else:
                        print(f"   ⚠️ 最新章節可能缺少內容")
    
    # 5. 檢查定時任務
    print("\n5. 檢查定時任務配置...")
    shell_script = os.path.join(WORKSPACE, "scripts", "novel-daily-generator.sh")
    if os.path.exists(shell_script):
        with open(shell_script, 'r', encoding='utf-8') as f:
            content = f.read()
            if "generate_chapter_deepseek.py" in content:
                print(f"   ✅ 使用DeepSeek生成腳本")
            if "備用方案" in content or "generate_chapter_direct.py" in content:
                print(f"   ✅ 有備用方案")
    
    # 6. 推薦的DeepSeek模型
    print("\n6. DeepSeek模型推薦:")
    print("   ✅ deepseek/deepseek-v3.2 - 163,840 tokens，適合長篇生成")
    print("   ✅ deepseek/deepseek-v3.2-speciale - 高計算變體，推理更強")
    print("   ✅ deepseek/deepseek-chat-v3-0324 - 旗艦聊天模型")
    print("   ⚠️ 注意：V3.2-Speciale可能成本更高")
    
    print("\n=== 驗證完成 ===")
    print("\n建議：")
    print("1. 先測試生成第67章（使用少量tokens測試）")
    print("2. 監控API使用成本")
    print("3. 確保備用方案工作正常")
    print("4. 明天07:00驗證自動執行結果")

if __name__ == "__main__":
    check_setup()