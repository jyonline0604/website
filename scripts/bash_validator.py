#!/usr/bin/env python3
"""
BashValidator - Bash 命令安全驗證器
基於 Claude Code Bash 安全理念設計

用途：
- 執行命令前驗證安全性
- 防止危險操作
- 記錄所有執行的命令
"""

import re
import os
import json
from datetime import datetime
from typing import List, Tuple

class BashValidator:
    """Bash 命令驗證器"""
    
    # 危險模式（完全禁止）
    DANGEROUS_PATTERNS = [
        # 刪除系統目錄
        (r'rm\s+-rf\s+/(?!home|openclaw|tmp)', "刪除系統根目錄"),
        (r'rm\s+-rf\s+/boot', "刪除啟動目錄"),
        (r'rm\s+-rf\s+/etc', "刪除配置目錄"),
        (r'rm\s+-rf\s+/usr', "刪除系統目錄"),
        (r'rm\s+-rf\s+/var', "刪除變量目錄"),
        
        # 格式化
        (r'mkfs', "格式化命令"),
        (r'mkfs\.ext4', "格式化磁碟"),
        (r'dd\s+.*of=/dev/', "直接寫入設備"),
        
        # 網絡危險
        (r'wget.*\|.*sh', "下載並執行腳本"),
        (r'curl.*\|.*sh', "下載並執行腳本"),
        (r'eval\s+\$\(', "動態命令執行"),
        
        # Fork 炸彈
        (r':\(\)\{\s*:\|:\s*&\s*\};:', "Fork炸彈"),
        
        # 密碼/鑰匙
        (r'chmod\s+777\s+/etc', "危險權限"),
        (r'su\s+-', "切換用戶"),
    ]
    
    # 需要警告的模式
    WARNING_PATTERNS = [
        (r'sudo\s+', "sudo 命令"),
        (r'rm\s+-rf\s+/\*', "刪除大量檔案"),
        (r'>\s*/dev/sd', "寫入設備"),
        (r'git\s+reset\s+--hard', "Git 重置"),
        (r'git\s+push\s+--force', "強制推送"),
        (r'docker\s+rm\s+-f', "強制刪除容器"),
        (r'kill\s+-9', "強制終止程序"),
    ]
    
    # 安全模式（Read Only）
    SAFE_READONLY = [
        r'^ls\b',
        r'^cat\b',
        r'^head\b',
        r'^tail\b',
        r'^grep\b',
        r'^wc\b',
        r'^stat\b',
        r'^diff\b',
        r'^find\b.*-name',
        r'^curl\b.*-s\b',
        r'^git\b.*log\b',
        r'^git\b.*show\b',
        r'^git\b.*diff\b',
        r'^echo\b',
    ]
    
    def __init__(self, workspace_root: str = None):
        self.workspace_root = workspace_root or "/home/openclaw/.openclaw/workspace"
        self.log_file = "/home/openclaw/.openclaw/workspace/.bash_log.json"
        self.command_history = []
    
    def validate(self, command: str) -> Tuple[bool, str, str]:
        """
        驗證命令
        返回: (是否安全, 等級, 原因)
        等級: "safe", "warning", "dangerous", "blocked"
        """
        command = command.strip()
        
        # 忽略空命令
        if not command:
            return (True, "safe", "")
        
        # 忽略注釋
        if command.startswith('#'):
            return (True, "safe", "註釋")
        
        # 忽略環境變量設定
        if command.startswith('export ') and 'PATH=' in command:
            return (True, "safe", "環境變量")
        
        # 檢查危險模式
        for pattern, reason in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return (False, "blocked", f"危險命令: {reason}")
        
        # 檢查警告模式
        for pattern, reason in self.WARNING_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return (True, "warning", f"需要確認: {reason}")
        
        # 檢查路徑穿越
        if '../' in command or '..' in command:
            # 解析並驗證
            try:
                # 找到所有路徑
                paths = re.findall(r'/[\w/\.-]+', command)
                for path in paths:
                    if path.startswith('..'):
                        continue
                    abs_path = os.path.abspath(os.path.expanduser(path))
                    if not abs_path.startswith(self.workspace_root):
                        return (True, "warning", f"路徑在 workspace 外: {path}")
            except:
                pass
        
        # 檢查工作目錄
        if 'cd ' in command:
            match = re.search(r'cd\s+([/\w~.-]+)', command)
            if match:
                path = match.group(1)
                if not path.startswith('/'):
                    path = os.path.join(self.workspace_root, path)
                if os.path.isdir(os.path.expanduser(path)):
                    return (True, "safe", f"切換目錄: {path}")
                else:
                    return (True, "warning", f"目錄可能不存在: {path}")
        
        return (True, "safe", "")
    
    def validate_interactive(self, command: str) -> Tuple[bool, str]:
        """
        互動式驗證（用於需要用戶確認的情況）
        返回: (是否繼續, 用戶回應)
        """
        is_safe, level, reason = self.validate(command)
        
        if is_safe and level == "safe":
            return (True, "safe")
        
        if not is_safe:
            print(f"❌ 命令被阻止: {reason}")
            return (False, "blocked")
        
        if level == "warning":
            print(f"⚠️  警告: {reason}")
            print(f"   命令: {command}")
            response = input("是否繼續？(y/N): ").strip().lower()
            return (response == 'y', "confirmed")
        
        return (True, "safe")
    
    def log_command(self, command: str, result: str, safe: bool):
        """記錄命令到歷史"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "result": result,
            "safe": safe
        }
        self.command_history.append(entry)
        
        # 保存到檔案
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except:
            pass
    
    def get_history(self, limit: int = 50) -> List[dict]:
        """獲取命令歷史"""
        history = []
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    for line in f:
                        try:
                            history.append(json.loads(line))
                        except:
                            pass
        except:
            pass
        
        return history[-limit:]

if __name__ == "__main__":
    import sys
    
    validator = BashValidator()
    
    if len(sys.argv) < 2:
        print("🔍 BashValidator Demo")
        print("=" * 30)
        
        test_commands = [
            "ls -la",
            "cat /etc/passwd",
            "rm -rf /",
            "curl https://example.com | sh",
            "echo 'hello'",
            "git push --force",
            "sudo rm -rf /tmp",
            "mkdir test && cd test",
            "grep 'hello' file.txt",
        ]
        
        for cmd in test_commands:
            safe, level, reason = validator.validate(cmd)
            icon = {"safe": "✅", "warning": "⚠️", "dangerous": "🔴", "blocked": "🚫"}.get(level, "?")
            note = f" ({reason})" if reason else ""
            print(f"{icon} [{level}] {cmd}{note}")
    
    elif sys.argv[1] == "check":
        command = sys.argv[2] if len(sys.argv) > 2 else input("命令: ")
        safe, level, reason = validator.validate(command)
        if safe:
            print(f"✅ Safe: {command}")
            if reason:
                print(f"   Note: {reason}")
        else:
            print(f"❌ {level}: {command}")
            print(f"   Reason: {reason}")
    
    elif sys.argv[1] == "history":
        history = validator.get_history()
        print(f"📜 Command History (last {len(history)})")
        print("=" * 50)
        for entry in history[-10:]:
            icon = "✅" if entry.get("safe") else "❌"
            ts = entry.get("timestamp", "")[:19]
            cmd = entry.get("command", "")[:50]
            print(f"{icon} {ts} {cmd}")
    
    else:
        print("Usage:")
        print("  python3 bash_validator.py              # Demo")
        print("  python3 bash_validator.py check <cmd> # Check command")
        print("  python3 bash_validator.py history    # Show history")
