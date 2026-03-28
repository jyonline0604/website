#!/usr/bin/env python3
"""
自動記憶記錄器
確保每次重要修改後自動記錄到記憶檔
"""

import os
import sys
from datetime import datetime

WORKSPACE = "/home/openclaw/.openclaw/workspace"
MEMORY_DIR = os.path.join(WORKSPACE, "memory")

def ensure_memory_dir():
    """確保記憶目錄存在"""
    if not os.path.exists(MEMORY_DIR):
        os.makedirs(MEMORY_DIR, exist_ok=True)
        print(f"✅ 創建記憶目錄: {MEMORY_DIR}")

def get_today_memory_file():
    """獲取今天的記憶文件路徑"""
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(MEMORY_DIR, f"{today}.md")

def log_to_memory(category, title, content, tags=None):
    """
    記錄到記憶檔
    
    Args:
        category: 分類（如：系統修改、問題修復、學習教訓）
        title: 標題
        content: 內容（可以是字符串或列表）
        tags: 標籤列表
    """
    ensure_memory_dir()
    
    memory_file = get_today_memory_file()
    
    # 格式化時間
    timestamp = datetime.now().strftime("%H:%M")
    full_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M HKT")
    
    # 準備內容
    if isinstance(content, list):
        content_text = "\n".join([f"- {item}" for item in content])
    else:
        content_text = str(content)
    
    # 準備標籤
    tags_text = ""
    if tags:
        tags_text = " ".join([f"#{tag}" for tag in tags])
    
    # 準備記錄條目
    entry = f"""
### {category}: {title} {tags_text}
**時間**: {timestamp}

{content_text}

---
"""
    
    # 檢查文件是否存在
    file_exists = os.path.exists(memory_file)
    
    if file_exists:
        # 追加到文件
        with open(memory_file, "a", encoding="utf-8") as f:
            f.write(entry)
        print(f"✅ 追加到記憶檔: {memory_file}")
    else:
        # 創建新文件
        header = f"""# {datetime.now().strftime("%Y-%m-%d")} 記憶

*記憶文件創建時間: {full_timestamp}*

"""
        with open(memory_file, "w", encoding="utf-8") as f:
            f.write(header + entry)
        print(f"✅ 創建記憶檔: {memory_file}")
    
    return memory_file

def log_system_modification(modification_type, description, files_modified=None, github_commit=None):
    """記錄系統修改"""
    content = []
    
    content.append(f"**修改類型**: {modification_type}")
    content.append(f"**描述**: {description}")
    
    if files_modified:
        if isinstance(files_modified, list):
            content.append("**修改文件**:")
            for file in files_modified:
                content.append(f"  - {file}")
        else:
            content.append(f"**修改文件**: {files_modified}")
    
    if github_commit:
        content.append(f"**GitHub提交**: {github_commit}")
    
    return log_to_memory(
        category="系統修改",
        title=modification_type,
        content=content,
        tags=["system", "modification"]
    )

def log_problem_fix(problem, solution, result):
    """記錄問題修復"""
    content = [
        f"**問題**: {problem}",
        f"**解決方案**: {solution}",
        f"**結果**: {result}"
    ]
    
    return log_to_memory(
        category="問題修復",
        title="問題已解決",
        content=content,
        tags=["fix", "problem"]
    )

def log_lesson_learned(lesson, context, action):
    """記錄學習教訓"""
    content = [
        f"**教訓**: {lesson}",
        f"**情境**: {context}",
        f"**行動**: {action}"
    ]
    
    return log_to_memory(
        category="學習教訓",
        title="重要教訓",
        content=content,
        tags=["lesson", "learning"]
    )

def log_github_push(files, commit_hash, commit_message):
    """記錄GitHub推送"""
    content = [
        f"**提交哈希**: {commit_hash}",
        f"**提交信息**: {commit_message}",
        "**推送文件**:"
    ]
    
    if isinstance(files, list):
        for file in files:
            content.append(f"  - {file}")
    else:
        content.append(f"  - {files}")
    
    github_url = f"https://github.com/jyonline0604/website/commit/{commit_hash}"
    content.append(f"**GitHub鏈接**: {github_url}")
    
    return log_to_memory(
        category="GitHub推送",
        title="代碼已推送",
        content=content,
        tags=["github", "push", "code"]
    )

# 測試功能
if __name__ == "__main__":
    print("=== 自動記憶記錄器測試 ===")
    print(f"當前時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 測試各種記錄
    test_files = ["scripts/test1.py", "scripts/test2.py"]
    
    # 1. 記錄系統修改
    log_system_modification(
        modification_type="新增功能",
        description="添加自動記憶記錄系統",
        files_modified=test_files,
        github_commit="abc123"
    )
    
    # 2. 記錄問題修復
    log_problem_fix(
        problem="忘記自動記憶記錄",
        solution="創建自動記憶記錄器",
        result="現在所有修改都會自動記錄"
    )
    
    # 3. 記錄學習教訓
    log_lesson_learned(
        lesson="永遠記住自動記憶記錄原則",
        context="修改真實財經新聞系統後忘記記錄",
        action="創建自動記錄機制避免再次忘記"
    )
    
    # 4. 記錄GitHub推送
    log_github_push(
        files=test_files,
        commit_hash="17e089b",
        commit_message="feat: 添加真實財經新聞系統"
    )
    
    print("\n✅ 測試完成！")
    print(f"記憶文件: {get_today_memory_file()}")