#!/usr/bin/env python3
"""
PermissionEnforcer - 權限安全檢查系統
基於 Claude Code PermissionEnforcer 概念設計

用途：
- 防止危險操作（如刪除系統檔案）
- 防止目錄穿越攻擊
- 確保操作在允許範圍內
"""

import os
import re
from enum import Enum
from pathlib import Path

class PermissionMode(Enum):
    READ_ONLY = "readonly"
    WORKSPACE_WRITE = "workspace_write"
    ALLOW = "allow"
    DANGER_FULL_ACCESS = "danger_fullaccess"

class EnforcementResult:
    ALLOWED = "allowed"
    DENIED = "denied"
    
    def __init__(self, allowed: bool, reason: str = ""):
        self.allowed = allowed
        self.reason = reason
    
    def __bool__(self):
        return self.allowed

class PermissionEnforcer:
    """權限執行器"""
    
    def __init__(self, workspace_root: str = None):
        self.workspace_root = workspace_root or "/home/openclaw/.openclaw/workspace"
        self.mode = PermissionMode.ALLOW
        
        # 危險模式白名單
        self.dangerous_commands = [
            r'rm\s+-rf\s+/',           # 刪除根目錄
            r'rm\s+-rf\s+/boot',        # 刪除啟動目錄
            r'dd\s+if=.*of=/dev/sd',   # 磁碟寫入危險命令
            r'mkfs\.',                  # 格式化
            r':\(\)\{:\|:&\};:',        # Fork炸彈
        ]
        
        # 只讀模式白名單（這些命令可以安全執行）
        self.readonly_safe = [
            r'^cat\s+',                 # 讀取檔案
            r'^head\s+',                # 讀取開頭
            r'^tail\s+',                # 讀取結尾
            r'^grep\s+',                # 搜尋
            r'^ls\s+',                  # 列目錄
            r'^stat\s+',                # 查看狀態
            r'^wc\s+',                  # 計數
            r'^diff\s+',                # 比較
            r'^curl\s+.*-s\s+',        # 讀取網頁（不寫入）
        ]
    
    def set_mode(self, mode: PermissionMode):
        """設定權限模式"""
        self.mode = mode
        print(f"🔐 Permission mode: {mode.value}")
    
    def check_command(self, command: str) -> EnforcementResult:
        """檢查命令是否安全"""
        # Danger Full Access 模式不做檢查
        if self.mode == PermissionMode.DANGER_FULL_ACCESS:
            return EnforcementResult(True)
        
        # 檢查危險命令
        for dangerous in self.dangerous_commands:
            if re.search(dangerous, command):
                return EnforcementResult(
                    False, 
                    f"危險命令：{dangerous}"
                )
        
        # Read Only 模式只允許安全命令
        if self.mode == PermissionMode.READ_ONLY:
            for safe in self.readonly_safe:
                if re.match(safe, command.strip()):
                    return EnforcementResult(True)
            return EnforcementResult(False, "Read Only 模式不允許此命令")
        
        # Workspace Write 模式檢查是否在 workspace 內
        if self.mode == PermissionMode.WORKSPACE_WRITE:
            # 檢查是否包含寫入操作
            write_indicators = [r'>\s*', r'\|', r'tee\s+', r'cp\s+.*dest', r'mv\s+']
            for indicator in write_indicators:
                if re.search(indicator, command):
                    # 檢查目標路徑
                    path_match = re.search(r'/[\w/\.-]+', command)
                    if path_match:
                        path = path_match.group(0)
                        if not self.is_within_workspace(path):
                            return EnforcementResult(
                                False, 
                                f"路徑在 workspace 外：{path}"
                            )
        
        return EnforcementResult(True)
    
    def check_file_write(self, file_path: str) -> EnforcementResult:
        """檢查檔案寫入是否安全"""
        if self.mode == PermissionMode.READ_ONLY:
            return EnforcementResult(False, "Read Only 模式不允許寫入")
        
        if self.mode == PermissionMode.WORKSPACE_WRITE:
            if not self.is_within_workspace(file_path):
                return EnforcementResult(
                    False, 
                    f"路徑在 workspace 外：{file_path}"
                )
        
        return EnforcementResult(True)
    
    def is_within_workspace(self, path: str) -> bool:
        """檢查路徑是否在 workspace 內（防止目錄穿越）"""
        try:
            # 解析為絕對路徑
            abs_path = os.path.abspath(os.path.expanduser(path))
            abs_workspace = os.path.abspath(self.workspace_root)
            
            # 確保是目錄
            if not os.path.isdir(abs_workspace):
                return False
            
            # 檢查是否在 workspace 內
            return abs_path.startswith(abs_workspace + os.sep) or abs_path == abs_workspace
        except:
            return False
    
    def check_path_traversal(self, path: str) -> EnforcementResult:
        """檢查路徑穿越攻擊"""
        # 防止 ../ 穿越
        if '..' in path:
            # 解析並檢查
            try:
                resolved = os.path.realpath(path)
                if not self.is_within_workspace(resolved):
                    return EnforcementResult(False, "路徑穿越檢測：嘗試離開 workspace")
            except:
                return EnforcementResult(False, "路徑解析失敗")
        
        return EnforcementResult(True)
    
    def enforce(self, action: str, target: str = None) -> EnforcementResult:
        """執行權限檢查"""
        if action == "command":
            return self.check_command(target or "")
        elif action == "write":
            return self.check_file_write(target or "")
        elif action == "traversal":
            return self.check_path_traversal(target or "")
        else:
            return EnforcementResult(False, f"未知操作：{action}")

if __name__ == "__main__":
    import sys
    
    enforcer = PermissionEnforcer()
    
    if len(sys.argv) < 2:
        print("🔐 PermissionEnforcer Demo")
        print("=" * 30)
        
        # 測試
        test_commands = [
            "rm -rf /",
            "cat /etc/passwd",
            "ls -la",
            "grep 'hello' test.txt",
            "curl -s https://example.com",
        ]
        
        for mode in [PermissionMode.READ_ONLY, PermissionMode.WORKSPACE_WRITE]:
            enforcer.set_mode(mode)
            print(f"\nMode: {mode.value}")
            for cmd in test_commands:
                result = enforcer.check_command(cmd)
                status = "✅" if result else "❌"
                reason = f" ({result.reason})" if not result else ""
                print(f"  {status} {cmd}{reason}")
    
    elif sys.argv[1] == "check":
        command = sys.argv[2] if len(sys.argv) > 2 else ""
        result = enforcer.check_command(command)
        if result:
            print(f"✅ Allowed: {command}")
        else:
            print(f"❌ Denied: {command} - {result.reason}")
    
    elif sys.argv[1] == "mode":
        mode_name = sys.argv[2] if len(sys.argv) > 2 else "allow"
        try:
            mode = PermissionMode(mode_name)
            enforcer.set_mode(mode)
        except:
            print(f"❌ Unknown mode: {mode_name}")
            print("Available modes: readonly, workspace_write, allow, danger_fullaccess")
    
    elif sys.argv[1] == "workspace":
        path = sys.argv[2] if len(sys.argv) > 2 else ""
        result = enforcer.is_within_workspace(path)
        print(f"{'✅' if result else '❌'} {path}")
    
    else:
        print("Usage:")
        print("  python3 permission_enforcer.py              # Demo")
        print("  python3 permission_enforcer.py check <cmd>  # Check command")
        print("  python3 permission_enforcer.py mode <mode>   # Set mode")
        print("  python3 permission_enforcer.py workspace <path>  # Check workspace")
