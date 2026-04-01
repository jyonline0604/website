#!/usr/bin/env python3
"""
每日備份腳本
自動備份核心檔案去 Second-brain (GitHub)
"""

import os
import subprocess
from datetime import datetime

WORKSPACE = "/home/openclaw/.openclaw/workspace"
BACKUP_DIR = f"{WORKSPACE}/backups"
SECOND_BRAIN_DIR = f"{WORKSPACE}/Second-brain"
LOG_FILE = f"{WORKSPACE}/logs/daily-backup.log"

def log(msg):
    """寫日誌"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(f"[{timestamp}] {msg}")

def run_cmd(cmd):
    """執行命令"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def main():
    log("🚀 開始每日備份...")
    
    # 加密密碼
    backup_pass_path = f"{WORKSPACE}/.backup-pass"
    if not os.path.exists(backup_pass_path):
        log("❌ 找不到加密密碼")
        return
    
    with open(backup_pass_path, "r") as f:
        backup_pass = f.read().strip()
    
    # 生成備份檔案
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{BACKUP_DIR}/workspace-daily-backup-{timestamp}.tar.gz.enc"
    
    # 排除敏感檔案和過大的目錄
    excludes = [
        "node_modules", ".git", "__pycache__", "*.pyc",
        "auth-profiles.json", "notify-config.json", 
        "twitter_last_post.json", ".backup-pass", "*.enc",
        "Second-brain", ".openclaw", "encrypted-backups",
        "backup_before_fix", "*.log"
    ]
    
    exclude_args = " ".join([f"--exclude='{e}'" for e in excludes])
    
    # 建立tar加密
    cmd = f"""cd {WORKSPACE} && tar czf - chapter-*.html *.html assets scripts memory AGENTS.md SOUL.md USER.md MEMORY.md TOOLS.md HEARTBEAT.md {exclude_args} 2>/dev/null | openssl enc -aes-256-cbc -salt -pbkdf2 -pass pass:"{backup_pass}" -out {backup_file}"""
    
    code, out, err = run_cmd(cmd)
    if code != 0:
        log(f"❌ 備份失敗: {err}")
        return
    
    log(f"✅ 備份檔案已創建: {backup_file}")
    
    # 複製去 Second-brain
    cmd = f"cp {backup_file} {SECOND_BRAIN_DIR}/"
    run_cmd(cmd)
    
    # Git add & commit
    os.chdir(SECOND_BRAIN_DIR)
    run_cmd("git add .")
    
    commit_msg = f"backup: daily {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    run_cmd(f'git commit -m "{commit_msg}"')
    
    # Push (修正: 正確的 repository URL)
    code, out, err = run_cmd("git push https://github.com/jyonline0604/Second-brain.git main 2>&1")
    if "error" in err.lower() or "failed" in err.lower():
        log(f"⚠️ Push失敗: {err}")
    else:
        log(f"✅ 已推送到 Second-brain")
    
    # 清理舊備份（保留最近7日）
    cmd = f"find {BACKUP_DIR}/workspace-daily-backup-*.tar.gz.enc -mtime +7 -delete"
    run_cmd(cmd)
    
    log("🎉 每日備份完成!")

if __name__ == "__main__":
    main()
