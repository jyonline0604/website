#!/usr/bin/env python3
"""
檢查OpenClaw版本更新的腳本
"""

import os
import sys
import json
import subprocess
import requests
from datetime import datetime
import re

# 設置環境變量
os.environ['PATH'] = '/home/openclaw/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'

# 日誌文件路徑
LOG_FILE = "/home/openclaw/.openclaw/workspace/logs/openclaw-update.log"
VERSION_FILE = "/home/openclaw/.openclaw/workspace/openclaw-version.json"

def get_current_version():
    """獲取當前OpenClaw版本"""
    try:
        result = subprocess.run(
            ["openclaw", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            # 解析版本號，例如: "OpenClaw 2026.3.23-2 (7ffe7e4)"
            match = re.search(r'OpenClaw\s+([\d\.\-]+)', result.stdout)
            if match:
                return match.group(1)
        return "unknown"
    except Exception as e:
        print(f"❌ 獲取當前版本失敗: {e}")
        return "error"

def get_npm_version():
    """從npm獲取OpenClaw版本"""
    try:
        result = subprocess.run(
            ["npm", "list", "-g", "openclaw"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            # 解析npm輸出，例如: "openclaw@2026.3.23-2"
            for line in result.stdout.split('\n'):
                if 'openclaw@' in line:
                    match = re.search(r'openclaw@([\d\.\-]+)', line)
                    if match:
                        return match.group(1)
        return "unknown"
    except Exception as e:
        print(f"❌ 獲取npm版本失敗: {e}")
        return "error"

def check_npm_latest_version():
    """檢查npm上的最新版本"""
    try:
        # 使用npm view命令檢查最新版本
        result = subprocess.run(
            ["npm", "view", "openclaw", "version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            latest_version = result.stdout.strip()
            if latest_version:
                return latest_version
        
        # 備用方法：檢查GitHub releases
        try:
            response = requests.get(
                "https://api.github.com/repos/openclaw/openclaw/releases/latest",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                tag_name = data.get('tag_name', '')
                # 移除可能的'v'前綴
                if tag_name.startswith('v'):
                    return tag_name[1:]
                return tag_name
        except:
            pass
            
        return "unknown"
    except Exception as e:
        print(f"❌ 檢查最新版本失敗: {e}")
        return "error"

def load_version_history():
    """加載版本歷史記錄"""
    if os.path.exists(VERSION_FILE):
        try:
            with open(VERSION_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    # 默認歷史記錄
    return {
        "current_version": "unknown",
        "last_checked": None,
        "latest_version": "unknown",
        "update_available": False,
        "check_history": []
    }

def save_version_history(data):
    """保存版本歷史記錄"""
    try:
        with open(VERSION_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ 保存版本歷史失敗: {e}")
        return False

def log_message(message):
    """記錄日誌"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    
    print(log_entry)
    
    # 寫入日誌文件
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
    except:
        pass

def main():
    """主函數"""
    print("🔍 OpenClaw版本檢查開始")
    print("=" * 50)
    
    # 加載歷史記錄
    history = load_version_history()
    
    # 獲取當前版本
    current_version = get_current_version()
    npm_version = get_npm_version()
    
    print(f"📋 當前版本:")
    print(f"   CLI版本: {current_version}")
    print(f"   NPM版本: {npm_version}")
    
    # 檢查最新版本
    print("\n🌐 檢查最新版本...")
    latest_version = check_npm_latest_version()
    print(f"   最新版本: {latest_version}")
    
    # 判斷是否需要更新
    update_available = False
    if current_version != "unknown" and latest_version != "unknown" and current_version != latest_version:
        # 簡單的版本比較（假設版本號格式為 YYYY.MM.DD-X）
        try:
            current_parts = current_version.replace('-', '.').split('.')
            latest_parts = latest_version.replace('-', '.').split('.')
            
            # 比較每個部分
            for i in range(min(len(current_parts), len(latest_parts))):
                cur = int(current_parts[i]) if current_parts[i].isdigit() else 0
                lat = int(latest_parts[i]) if latest_parts[i].isdigit() else 0
                
                if lat > cur:
                    update_available = True
                    break
                elif lat < cur:
                    break
        except:
            # 如果版本比較失敗，使用字符串比較
            if latest_version > current_version:
                update_available = True
    
    # 更新歷史記錄
    check_record = {
        "timestamp": datetime.now().isoformat(),
        "current_version": current_version,
        "npm_version": npm_version,
        "latest_version": latest_version,
        "update_available": update_available
    }
    
    history["current_version"] = current_version
    history["last_checked"] = datetime.now().isoformat()
    history["latest_version"] = latest_version
    history["update_available"] = update_available
    history["check_history"].append(check_record)
    
    # 只保留最近10次檢查記錄
    if len(history["check_history"]) > 10:
        history["check_history"] = history["check_history"][-10:]
    
    # 保存歷史記錄
    save_version_history(history)
    
    # 輸出結果
    print("\n📊 檢查結果:")
    if update_available:
        print(f"   ⚠️  發現新版本: {latest_version}")
        print(f"   📅 當前版本: {current_version}")
        print(f"   🔄 建議更新: npm update -g openclaw")
        
        # 記錄警告日誌
        log_message(f"警告: OpenClaw有新版本可用 - 當前: {current_version}, 最新: {latest_version}")
    else:
        if current_version == "unknown" or latest_version == "unknown":
            print("   ℹ️  版本檢查不完整")
        elif current_version == latest_version:
            print("   ✅ 已是最新版本")
        else:
            print("   ✅ 版本檢查完成")
    
    print(f"\n📝 詳細記錄已保存: {VERSION_FILE}")
    print(f"📋 日誌文件: {LOG_FILE}")
    
    return update_available

if __name__ == "__main__":
    try:
        update_needed = main()
        sys.exit(0 if not update_needed else 1)
    except Exception as e:
        print(f"❌ 腳本執行失敗: {e}")
        sys.exit(1)