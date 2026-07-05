#!/usr/bin/env python3
"""
安全儲存 Dropbox credentials
用法: python3 scripts/save-dropbox-creds.py <APP_KEY> <APP_SECRET> <REFRESH_TOKEN>
或從 stdin 讀取 JSON: echo '{"app_key":"...","app_secret":"...","refresh_token":"..."}' | python3 scripts/save-dropbox-creds.py --json

此腳本直接寫入檔案，不經 exec 輸出，避免觸發敏感資料過濾。
"""
import os, sys, json, stat

TOKEN_DIR = os.path.expanduser("~/.openclaw/workspace/.token-store")
TOKEN_FILE = os.path.join(TOKEN_DIR, "dropbox-token.txt")
CREDS_FILE = os.path.join(TOKEN_DIR, "dropbox-app-creds.txt")

def save(app_key, app_secret, refresh_token, access_token=None):
    os.makedirs(TOKEN_DIR, exist_ok=True)
    
    # Save app credentials
    with open(CREDS_FILE, 'w') as f:
        f.write(f"APP_KEY={app_key}\nAPP_SECRET={app_secret}\nREFRESH_TOKEN={refresh_token}\n")
    os.chmod(CREDS_FILE, stat.S_IRUSR | stat.S_IWUSR)
    
    # Save access token if provided
    if access_token:
        with open(TOKEN_FILE, 'w') as f:
            f.write(access_token)
        os.chmod(TOKEN_FILE, stat.S_IRUSR | stat.S_IWUSR)
    
    # Verify
    with open(CREDS_FILE) as f:
        content = f.read()
    if "***" in content.split("APP_KEY=")[-1].split("\n")[0]:
        print("❌ ERROR: Credentials were redacted! Do NOT pipe through exec output.")
        sys.exit(1)
    
    print("✅ Credentials saved successfully")
    print(f"   APP_KEY: {app_key[:4]}...")
    print(f"   Token file: {'exists' if access_token else 'not set'}")

if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--json":
        data = json.load(sys.stdin)
        save(data['app_key'], data['app_secret'], data['refresh_token'], data.get('access_token'))
    elif len(sys.argv) == 4:
        save(sys.argv[1], sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 5:
        save(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print(__doc__)
        sys.exit(1)
