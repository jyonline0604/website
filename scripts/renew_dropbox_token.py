#!/usr/bin/env python3
"""
Dropbox access token auto-renew script
用 APP_KEY + APP_SECRET + REFRESH_TOKEN 換新 short-lived access token
由 scripts/renew-dropbox-token.sh（每 3hr 跑）調用
"""
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

CREDS_FILE = Path('/home/openclaw/.openclaw/workspace/.token-store/dropbox-app-creds.txt')
TOKEN_FILE = Path('/home/openclaw/.openclaw/workspace/.token-store/dropbox-token.txt')
LOG_FILE = Path('/home/openclaw/.openclaw/workspace/logs/dropbox-token-renewal.log')

TOKEN_URL = 'https://api.dropboxapi.com/oauth2/token'
TEST_URL = 'https://api.dropboxapi.com/2/users/get_current_account'


def log(msg: str, level: str = 'INFO') -> None:
    ts = datetime.now(timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S %z')
    line = f'[{ts}] [{level}] {msg}'
    print(line)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')


def read_creds() -> dict:
    if not CREDS_FILE.exists():
        log(f'❌ creds file 唔存在: {CREDS_FILE}', 'ERROR')
        sys.exit(1)
    creds = {}
    with open(CREDS_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            creds[k.strip()] = v.strip()
    for key in ('APP_KEY', 'APP_SECRET', 'REFRESH_TOKEN'):
        if key not in creds:
            log(f'❌ creds 缺少 {key}', 'ERROR')
            sys.exit(1)
    return creds


def refresh_access_token(creds: dict, timeout: int = 15) -> str:
    """用 refresh_token 換新 access token（帶 retry+backoff）"""
    last_err = None
    for attempt in range(3):
        try:
            resp = requests.post(
                TOKEN_URL,
                data={
                    'grant_type': 'refresh_token',
                    'refresh_token': creds['REFRESH_TOKEN'],
                    'client_id': creds['APP_KEY'],
                    'client_secret': creds['APP_SECRET'],
                },
                timeout=timeout,
            )
            if resp.status_code == 200:
                data = resp.json()
                new_token = data.get('access_token')
                expires_in = data.get('expires_in', '?')
                if not new_token:
                    raise ValueError('response 冇 access_token')
                log(f'  ✅ 換到新 token (expires_in={expires_in}s, prefix={new_token[:12]}...)')
                return new_token
            last_err = f'HTTP {resp.status_code}: {resp.text[:200]}'
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            last_err = f'{type(e).__name__}: {str(e)[:100]}'
        except Exception as e:
            last_err = f'{type(e).__name__}: {str(e)[:100]}'

        if attempt < 2:
            wait = 2 ** attempt
            log(f'  ⏳ 第 {attempt+1}/3 次失敗 ({last_err})，{wait}s 後重試')
            time.sleep(wait)

    log(f'❌ 全部 retry 失敗: {last_err}', 'ERROR')
    sys.exit(2)


def save_token(new_token: str) -> None:
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    if TOKEN_FILE.exists():
        backup = TOKEN_FILE.with_suffix('.txt.bak')
        backup.write_text(TOKEN_FILE.read_text())
    TOKEN_FILE.write_text(new_token)
    os.chmod(TOKEN_FILE, 0o600)
    log(f'  ✅ token saved → {TOKEN_FILE} (mode 600, {len(new_token)} bytes)')


def test_token(token: str, timeout: int = 10) -> bool:
    """用新 token ping Dropbox API 確認有效"""
    try:
        resp = requests.post(
            TEST_URL,
            headers={'Authorization': 'Bearer ' + token},
            timeout=timeout,
        )
        if resp.status_code == 200:
            acct = resp.json()
            log(f"  ✅ token 有效：account={acct.get('name','?')} email={acct.get('email','?')}")
            return True
        log(f'❌ token test 失敗 HTTP {resp.status_code}: {resp.text[:200]}', 'ERROR')
        return False
    except Exception as e:
        log(f'❌ token test exception: {e}', 'ERROR')
        return False


def main():
    log('=' * 60)
    log('🔑 Dropbox token auto-renew 開始')

    creds = read_creds()
    log(f'  creds: APP_KEY={creds["APP_KEY"][:8]}... REFRESH_TOKEN={creds["REFRESH_TOKEN"][:8]}...')

    new_token = refresh_access_token(creds)
    if not test_token(new_token):
        log('❌ token test 失敗，唔 save', 'ERROR')
        sys.exit(3)
    save_token(new_token)

    log('✅ 完成')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        log('⚠️ interrupted', 'WARN')
        sys.exit(130)
    except Exception as e:
        log(f'❌ uncaught: {e}', 'ERROR')
        sys.exit(99)
