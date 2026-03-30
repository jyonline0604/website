#!/usr/bin/env python3
"""
測試DeepSeek原生API連接
"""

import os
import sys
import requests

WORKSPACE = "/home/openclaw/.openclaw/workspace"

def get_deepseek_api_key():
    """獲取DeepSeek原生API密鑰"""
    # 從環境變量獲取
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if api_key:
        return api_key
    
    # 從文件讀取
    env_file = os.path.join(WORKSPACE, ".env")
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith("DEEPSEEK_API_KEY="):
                    return line.strip().split("=", 1)[1]
    
    return None

def test_api_connection():
    """測試API連接"""
    print("=== DeepSeek原生API連接測試 ===\n")
    
    # 1. 檢查密鑰
    api_key = get_deepseek_api_key()
    if not api_key:
        print("❌ 未找到DeepSeek API密鑰")
        print("請在 .env 文件中添加: DEEPSEEK_API_KEY=你的密鑰")
        print("申請密鑰: https://platform.deepseek.com/api_keys")
        return False
    
    print(f"✅ 找到API密鑰: {api_key[:8]}...{api_key[-4:]}")
    
    # 2. 測試簡單請求
    print("\n2. 測試API連接...")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": "請用一句話介紹DeepSeek"}
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            model = result.get("model", "未知")
            
            print(f"✅ API連接成功！")
            print(f"   模型: {model}")
            print(f"   響應: {content}")
            
            # 檢查使用量
            if "usage" in result:
                usage = result["usage"]
                print(f"   Token使用: 輸入{usage.get('prompt_tokens', 0)} + 輸出{usage.get('completion_tokens', 0)}")
            
            return True
        else:
            print(f"❌ API請求失敗: {response.status_code}")
            print(f"   錯誤信息: {response.text[:200]}")
            
            if response.status_code == 401:
                print("   ⚠️ 可能原因: API密鑰無效或過期")
            elif response.status_code == 429:
                print("   ⚠️ 可能原因: 請求頻率限制")
            
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 請求超時（10秒）")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 網絡連接錯誤")
        print("   請檢查是否能訪問: https://api.deepseek.com")
        return False
    except Exception as e:
        print(f"❌ 未知錯誤: {e}")
        return False

def check_current_config():
    """檢查當前配置"""
    print("\n=== 當前系統配置檢查 ===\n")
    
    # 檢查shell腳本
    shell_script = os.path.join(WORKSPACE, "scripts", "novel-daily-generator.sh")
    if os.path.exists(shell_script):
        with open(shell_script, 'r', encoding='utf-8') as f:
            content = f.read()
            
            print("1. 定時任務配置:")
            if "generate_chapter_deepseek.py" in content:
                print("   ✅ 使用OpenRouter版DeepSeek")
            if "generate_chapter_deepseek_native.py" in content:
                print("   ✅ 使用原生API版DeepSeek")
            if "generate_chapter_direct.py" in content:
                print("   ✅ 有直接版備用方案")
    
    # 檢查腳本文件
    print("\n2. 可用生成腳本:")
    scripts_dir = os.path.join(WORKSPACE, "scripts")
    for script in os.listdir(scripts_dir):
        if script.startswith("generate_chapter_"):
            path = os.path.join(scripts_dir, script)
            size = os.path.getsize(path)
            print(f"   ✅ {script}: {size} 字節")

def show_next_steps():
    """顯示下一步行動"""
    print("\n=== 下一步行動建議 ===\n")
    
    api_key = get_deepseek_api_key()
    
    if not api_key:
        print("1. 🔑 申請DeepSeek API密鑰")
        print("   訪問: https://platform.deepseek.com/api_keys")
        print("   在 .env 文件中添加: DEEPSEEK_API_KEY=你的密鑰")
        print()
    
    print("2. 🧪 測試生成功能")
    print("   運行: python3 scripts/generate_chapter_deepseek_native.py")
    print()
    
    print("3. ⚙️ 切換到原生API（可選）")
    print("   修改 scripts/novel-daily-generator.sh:")
    print("   將 generate_chapter_deepseek.py 替換為 generate_chapter_deepseek_native.py")
    print()
    
    print("4. 📊 監控成本")
    print("   記錄每次生成的token使用量")
    print("   估算: 每章2000字 ≈ 3000 tokens ≈ ¥0.015元")
    print()
    
    print("5. 🔄 設置備用方案")
    print("   確保 scripts/novel-daily-generator.sh 有完整的錯誤處理")

if __name__ == "__main__":
    print("DeepSeek原生API設置助手")
    print("=" * 50)
    
    # 測試連接
    connection_ok = test_api_connection()
    
    # 檢查配置
    check_current_config()
    
    # 顯示建議
    show_next_steps()
    
    if connection_ok:
        print("\n✅ 所有檢查完成，系統準備就緒！")
    else:
        print("\n⚠️ 需要配置DeepSeek API密鑰才能使用原生API")
    
    print("\n詳細文檔請查看: DEEPSEEK_SETUP.md")