#!/usr/bin/env python3
import os, sys, tarfile, shutil, subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/openclaw/.openclaw/workspace")

# 載入 .env 文件中的環境變數
ENV_FILE = WORKSPACE / ".env"
if ENV_FILE.exists():
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()
BACKUP_DIR = WORKSPACE / "backups"
ENCRYPTED_DIR = WORKSPACE / "encrypted-backups"

INCLUDE_DIRS = ["my-novel-website", "memory", "scripts"]
EXCLUDE_PATTERNS = [".env", ".git", ".backup-pass", "/logs/", "node_modules", "__pycache__", ".pyc", ".DS_Store"]

def should_exclude(p: Path) -> bool:
    s = str(p)
    return any(pat in s for pat in EXCLUDE_PATTERNS)

def create_backup():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"novel-website-backup-{timestamp}.tar.gz"
    BACKUP_DIR.mkdir(exist_ok=True)
    print(f"📦 创建备份: {backup_file.name}")
    with tarfile.open(backup_file, "w:gz") as tar:
        for d in INCLUDE_DIRS:
            dir_path = WORKSPACE / d
            if not dir_path.exists(): continue
            print(f"  ✅ 添加: {d}/ (过滤)")
            for root, dirs, files in os.walk(dir_path):
                root_path = Path(root)
                dirs[:] = [x for x in dirs if not should_exclude(root_path / x)]
                for f in files:
                    fp = root_path / f
                    if should_exclude(fp): continue
                    try:
                        tar.add(fp, arcname=root_path.relative_to(WORKSPACE) / f)
                    except: pass
    return backup_file

def encrypt_backup(backup_file: Path) -> Path:
    encrypted_file = ENCRYPTED_DIR / f"{backup_file.name}.enc"
    ENCRYPTED_DIR.mkdir(exist_ok=True)
    print(f"🔒 加密备份: {encrypted_file.name}")
    password = os.getenv("BACKUP_ENCRYPTION_PASSWORD")
    if not password and (WORKSPACE / ".backup-pass").exists():
        password = open(WORKSPACE / ".backup-pass").read().strip()
    if not password:
        print("❌ 未设置备份密码"); return None
    cmd = ["openssl", "enc", "-aes-256-cbc", "-salt", "-pbkdf2", "-in", str(backup_file), "-out", str(encrypted_file), "-pass", f"pass:{password}"]
    if subprocess.run(cmd, capture_output=True).returncode == 0:
        backup_file.unlink()
        return encrypted_file
    print("❌ 加密失败"); return None

def upload_to_github(encrypted_file: Path):
    print("☁️  上传到 GitHub...")
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ 未设置 GITHUB_TOKEN 环境变量")
        print("   请使用: export GITHUB_TOKEN=your_token")
        raise RuntimeError("Missing GITHUB_TOKEN")
    repo_url = f"https://{token}@github.com/jyonline0604/Second-brain.git"
    if not (WORKSPACE / "Second-brain").exists():
        subprocess.run(["git", "clone", repo_url, "Second-brain"], check=True, capture_output=True)
    else:
        subprocess.run(["git", "-C", "Second-brain", "pull"], check=True, capture_output=True)
    dest = WORKSPACE / "Second-brain" / encrypted_file.name
    shutil.copy2(encrypted_file, dest)
    for c in [["add", encrypted_file.name], ["commit", "-m", f"Backup: {encrypted_file.name}"], ["push"]]:
        subprocess.run(["git", "-C", "Second-brain"] + c, check=True, capture_output=True)
    print(f"✅ 已上传: {encrypted_file.name}")

def main():
    print("=== 安全备份开始 ===")
    bf = create_backup()
    if not bf: sys.exit(1)
    ef = encrypt_backup(bf)
    if not ef: sys.exit(1)
    try: upload_to_github(ef)
    except Exception as e: print(f"❌ 上传失败: {e}"); sys.exit(1)
    print("=== 安全备份完成 ===")

if __name__ == "__main__": main()
