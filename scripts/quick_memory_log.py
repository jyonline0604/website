#!/usr/bin/env python3
"""
快速記憶記錄工具
確保每次重要操作後立即記錄
"""

import os
from datetime import datetime

def quick_log(category, message):
    """快速記錄到當天記憶檔"""
    workspace = "/home/openclaw/.openclaw/workspace"
    memory_dir = os.path.join(workspace, "memory")
    
    # 確保目錄存在
    os.makedirs(memory_dir, exist_ok=True)
    
    # 獲取今天文件
    today = datetime.now().strftime("%Y-%m-%d")
    memory_file = os.path.join(memory_dir, f"{today}.md")
    
    # 準備記錄
    timestamp = datetime.now().strftime("%H:%M")
    entry = f"""
### {category}
**時間**: {timestamp}

{message}

---
"""
    
    # 追加到文件
    with open(memory_file, "a", encoding="utf-8") as f:
        f.write(entry)
    
    print(f"✅ 已記錄到記憶檔: {memory_file}")
    return memory_file

def log_security_fix(issue, fix, commit_hash=None):
    """記錄安全修復"""
    message = f"**問題**: {issue}\n**修復**: {fix}"
    if commit_hash:
        message += f"\n**GitHub提交**: {commit_hash}"
    
    return quick_log("安全修復", message)

def log_github_push(files, commit_hash, commit_message):
    """記錄GitHub推送"""
    if isinstance(files, list):
        files_text = "\n".join([f"- {f}" for f in files[:3]])
        if len(files) > 3:
            files_text += f"\n- ...等{len(files)}個文件"
    else:
        files_text = f"- {files}"
    
    message = f"""**提交哈希**: {commit_hash}
**提交信息**: {commit_message}
**推送文件**:
{files_text}
**GitHub鏈接**: https://github.com/jyonline0604/website/commit/{commit_hash}"""
    
    return quick_log("GitHub推送", message)

def log_lesson_learned(lesson, context):
    """記錄學習教訓"""
    message = f"""**教訓**: {lesson}
**情境**: {context}
**行動**: 立即記錄到記憶檔避免忘記"""
    
    return quick_log("學習教訓", message)

# 測試
if __name__ == "__main__":
    print("=== 快速記憶記錄工具測試 ===")
    
    # 測試各種記錄
    log_security_fix(
        "API密鑰在TOOLS.md中暴露",
        "修復為部分顯示，擴展.gitignore",
        "e535980"
    )
    
    log_github_push(
        [".gitignore", "TOOLS.md", "DEEPSEEK_SETUP.md"],
        "e535980",
        "fix: 修復敏感資料外洩問題"
    )
    
    log_lesson_learned(
        "修復問題後要立即更新記憶檔",
        "修復敏感資料外洩問題後忘記更新記憶檔"
    )
    
    print("\n✅ 測試完成！")