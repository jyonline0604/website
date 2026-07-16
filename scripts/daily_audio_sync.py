#!/usr/bin/env python3
"""
daily_audio_sync.py — 每日從 Dropbox 抓一章 WAV → 轉 MP3 → upload R2 → 注入 player
Dropbox source: /萬古塵埃/EP{N}.wav
State file: .dropbox-sync/audio_state.json
"""

import json, os, sys, subprocess, re, glob, urllib.request, urllib.error
from datetime import datetime

WORKSPACE = '/home/openclaw/.openclaw/workspace'
STATE_FILE = os.path.join(WORKSPACE, '.dropbox-sync', 'audio_state.json')
DROPBOX_TOKEN = os.path.join(WORKSPACE, '.token-store', 'dropbox-token.txt')
DROPBOX_CREDS = os.path.join(WORKSPACE, '.token-store', 'dropbox-app-creds.txt')
DROPBOX_PATH = '/萬古塵埃'
R2_CREDS = os.path.join(WORKSPACE, '.r2-credentials.json')
TMP_DIR = '/tmp/novel-audio-work'

def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{ts}] {msg}')

def read_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {'last_chapter': 5, 'total_processed': 5}

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def refresh_dropbox_token():
    """Refresh Dropbox token using app creds"""
    if not os.path.exists(DROPBOX_CREDS):
        log('❌ No Dropbox app creds file')
        return False
    
    app_creds = {}
    with open(DROPBOX_CREDS) as f:
        for line in f:
            if '=' in line:
                k, v = line.strip().split('=', 1)
                app_creds[k] = v
    
    data = f"grant_type=refresh_token&refresh_token=***"]}&client_id={app_creds['APP_KEY']}&client_secret=***)"
    req = urllib.request.Request('https://api.dropboxapi.com/oauth2/token', data=data, method='POST')
    
    try:
        resp = urllib.request.urlopen(req)
        new_token = json.loads(resp.read())['access_token']
        with open(DROPBOX_TOKEN, 'w') as f:
            f.write(new_token)
        os.chmod(DROPBOX_TOKEN, 0o600)
        return new_token
    except Exception as e:
        log(f'❌ Token refresh failed: {e}')
        return None

def download_from_dropbox(chapter_num, token):
    """Download EP{N}.wav from Dropbox"""
    filename = f'EP{chapter_num:02d}.wav'
    path = f'{DROPBOX_PATH}/{filename}'
    local = os.path.join(TMP_DIR, filename)
    
    url = 'https://content.dropboxapi.com/2/files/download'
    req = urllib.request.Request(url, method='POST')
    req.add_header('Authorization', 'Bearer ' + token)
    req.add_header('Dropbox-API-Arg', json.dumps({"path": path}))
    
    try:
        resp = urllib.request.urlopen(req, timeout=120)
        data = resp.read()
        os.makedirs(TMP_DIR, exist_ok=True)
        with open(local, 'wb') as f:
            f.write(data)
        log(f'✅ Downloaded {filename} ({len(data)/1048576:.1f} MB)')
        return local
    except urllib.error.HTTPError as e:
        log(f'❌ {filename} not found in Dropbox (HTTP {e.code})')
        return None

def convert_to_mp3(wav_path, chapter_num):
    """Convert WAV to MP3"""
    mp3_path = os.path.join(TMP_DIR, f'chapter-{chapter_num}.mp3')
    
    result = subprocess.run([
        'ffmpeg', '-y', '-i', wav_path,
        '-codec:a', 'libmp3lame', '-b:a', '128k',
        mp3_path
    ], capture_output=True, text=True)
    
    if os.path.exists(mp3_path):
        size = os.path.getsize(mp3_path)
        log(f'✅ Converted → chapter-{chapter_num}.mp3 ({size/1048576:.1f} MB)')
        return mp3_path
    else:
        log(f'❌ Conversion failed')
        return None

def upload_to_r2(mp3_path):
    """Upload MP3 to R2 using existing script"""
    script = os.path.join(WORKSPACE, 'scripts', 'upload_audio_r2.py')
    result = subprocess.run(
        ['python3', script, mp3_path],
        capture_output=True, text=True, cwd=WORKSPACE
    )
    if '✅ 完成' in result.stdout:
        log(f'✅ Uploaded to R2')
        return True
    else:
        log(f'❌ Upload failed: {result.stdout[-200:]}')
        return False

def inject_player(chapter_num):
    """Inject audio player into chapter HTML"""
    script = os.path.join(WORKSPACE, 'scripts', 'inject_audio_player.py')
    result = subprocess.run(
        ['python3', script, str(chapter_num)],
        capture_output=True, text=True, cwd=WORKSPACE
    )
    return '✅' in result.stdout

def commit_push(chapter_num):
    """Commit and push to GitHub"""
    subprocess.run(['git', '-C', WORKSPACE, 'add', 
        f'chapter-{chapter_num}.html',
        '.dropbox-sync/audio_state.json'], capture_output=True)
    subprocess.run(['git', '-C', WORKSPACE, 'commit', '-m',
        f'🎧 feat: Audio chapter {chapter_num} from Dropbox'], capture_output=True)
    result = subprocess.run(['git', '-C', WORKSPACE, 'push'], capture_output=True, text=True)
    return result.returncode == 0


def main():
    state = read_state()
    next_ch = state['last_chapter'] + 1
    log(f'📋 State: last={state["last_chapter"]}, next=Chapter {next_ch}')
    
    # Refresh token
    token = refresh_dropbox_token()
    if not token:
        return 1
    
    # Download
    wav_file = download_from_dropbox(next_ch, token)
    if not wav_file:
        log(f'⏭️  EP{next_ch:02d}.wav not yet uploaded to Dropbox — skipping today')
        return 0
    
    # Convert
    mp3_file = convert_to_mp3(wav_file, next_ch)
    if not mp3_file:
        return 1
    
    # Upload to R2
    if not upload_to_r2(mp3_file):
        return 1
    
    # Inject player
    if inject_player(next_ch):
        log(f'✅ Player injected into chapter-{next_ch}.html')
    else:
        log(f'⚠️  Player injection may have issues')
    
    # Update state
    state['last_chapter'] = next_ch
    state['total_processed'] = state.get('total_processed', 0) + 1
    state['last_sync'] = datetime.now().isoformat()
    save_state(state)
    
    # Commit and push
    if commit_push(next_ch):
        log(f'🚀 Pushed to GitHub')
    else:
        log(f'⚠️  Push may have failed, but audio uploaded')
    
    log(f'🎉 Chapter {next_ch} audio complete!')
    return 0

if __name__ == '__main__':
    sys.exit(main())
