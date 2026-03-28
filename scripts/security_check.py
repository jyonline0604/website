#!/usr/bin/env python3
"""
安全檢查腳本
確保API密鑰不會在輸出中泄露
"""

import os
import re

WORKSPACE = "/home/openclaw/.openclaw/workspace"

def check_api_key_exposure():
    """檢查API密鑰是否在文件中泄露"""
    print("=== API密鑰安全檢查 ===\n")
    
    issues_found = 0
    
    # 1. 檢查.env文件權限
    env_file = os.path.join(WORKSPACE, ".env")
    if os.path.exists(env_file):
        stat = os.stat(env_file)
        mode = stat.st_mode & 0o777
        
        print("1. .env文件權限檢查:")
        if mode == 0o600:
            print("   ✅ 權限正確 (600)")
        else:
            print(f"   ⚠️ 權限不安全: {oct(mode)}")
            print("   建議: chmod 600 .env")
            issues_found += 1
    
    # 2. 檢查腳本文件中的密鑰泄露
    print("\n2. 檢查腳本文件中的API密鑰:")
    scripts_dir = os.path.join(WORKSPACE, "scripts")
    
    # API密鑰模式（sk-開頭，長度約50字符）
    api_key_pattern = r'sk-[a-zA-Z0-9]{40,50}'
    
    for script_file in os.listdir(scripts_dir):
        if script_file.endswith('.py') or script_file.endswith('.sh'):
            filepath = os.path.join(scripts_dir, script_file)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # 檢查是否包含完整的API密鑰
                    matches = re.findall(api_key_pattern, content)
                    if matches:
                        print(f"   ⚠️ {script_file}: 發現可能的API密鑰")
                        for match in matches[:2]:  # 只顯示前2個
                            print(f"     發現: {match[:8]}...{match[-4:]}")
                        issues_found += 1
                    else:
                        # 檢查是否只顯示部分密鑰
                        safe_patterns = [
                            r'api_key\[:8\].*\.\.\.',
                            r'api_key\[:10\].*\.\.\.',
                            r'key\[:8\].*\.\.\.'
                        ]
                        for pattern in safe_patterns:
                            if re.search(pattern, content):
                                print(f"   ✅ {script_file}: 使用安全顯示方式")
                                break
            except:
                pass
    
    # 3. 檢查日誌文件
    print("\n3. 檢查日誌文件:")
    log_file = os.path.join(WORKSPACE, "logs/novel-generator.log")
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                # 只檢查最後100行
                lines = f.readlines()[-100:]
                for i, line in enumerate(lines, 1):
                    if re.search(api_key_pattern, line):
                        print(f"   ⚠️ 日誌第{i}行: 發現可能的API密鑰")
                        # 顯示安全版本
                        safe_line = re.sub(api_key_pattern, lambda m: f"{m.group(0)[:8]}...{m.group(0)[-4:]}", line)
                        print(f"     內容: {safe_line.strip()[:80]}")
                        issues_found += 1
                        break
                else:
                    print("   ✅ 日誌中未發現完整API密鑰")
        except:
            print("   ⚠️ 無法讀取日誌文件")
    
    # 4. 檢查記憶檔
    print("\n4. 檢查記憶檔:")
    memory_files = [
        os.path.join(WORKSPACE, "MEMORY.md"),
        os.path.join(WORKSPACE, "memory/2026-03-27.md")
    ]
    
    for mem_file in memory_files:
        if os.path.exists(mem_file):
            try:
                with open(mem_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if re.search(api_key_pattern, content):
                        print(f"   ⚠️ {os.path.basename(mem_file)}: 發現API密鑰")
                        issues_found += 1
                    else:
                        print(f"   ✅ {os.path.basename(mem_file)}: 安全")
            except:
                pass
    
    # 總結
    print(f"\n=== 檢查完成 ===")
    if issues_found == 0:
        print("✅ 所有安全檢查通過！")
    else:
        print(f"⚠️ 發現 {issues_found} 個安全問題")
        print("\n建議修復:")
        print("1. 確保.env文件權限為600")
        print("2. 在腳本中只顯示API密鑰的部分字符")
        print("3. 從日誌和記憶檔中移除完整密鑰")
        print("4. 定期更換API密鑰")

def safe_api_key_display(api_key):
    """安全顯示API密鑰（只顯示部分字符）"""
    if not api_key or len(api_key) < 12:
        return "[無效密鑰]"
    return f"{api_key[:8]}...{api_key[-4:]}"

if __name__ == "__main__":
    check_api_key_exposure()
    
    # 示範安全顯示
    print("\n=== 安全顯示示範 ===")
    test_key = "sk-test1234567890123456789012345678901234567890"
    print(f"完整密鑰: {test_key}")
    print(f"安全顯示: {safe_api_key_display(test_key)}")