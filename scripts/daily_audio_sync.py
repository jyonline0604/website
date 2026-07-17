#!/usr/bin/env python3
"""
daily_audio_sync.py — 每日用 Mosi TTS (韩立声) 生成一章語音
Flow: Chapter HTML → 提取文字 → Mosi TTS → MP3 → R2 upload → Player inject → Push
"""

import json, os, sys, subprocess, re, glob, urllib.request, urllib.error, time
from datetime import datetime

WORKSPACE = '/home/openclaw/.openclaw/workspace'

# Dropbox paths for fallback
DROPBOX_TOKEN_FILE = os.path.join(WORKSPACE, '.token-store', 'dropbox-token.txt')
DROPBOX_CREDS_FILE = os.path.join(WORKSPACE, '.token-store', 'dropbox-app-creds.txt')
STATE_FILE = os.path.join(WORKSPACE, '.dropbox-sync', 'audio_state.json')
MOSI_KEY_FILE = os.path.join(WORKSPACE, '.token-store', 'mosi-api-key.txt')
TMP_DIR = '/tmp/novel-audio-work'

# Mosi config
MOSI_API = 'https://api.mosi.cn/v1'
VOICE_ID = '84a96ce6-280f-4aca-ade4-8ce54d2c59f9'  # 韩立
TTS_MODEL = 'moss-tts'

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

def extract_chapter_text(chapter_num):
    """Extract and clean chapter text from HTML"""
    html_file = os.path.join(WORKSPACE, f'chapter-{chapter_num}.html')
    if not os.path.exists(html_file):
        log(f'❌ chapter-{chapter_num}.html not found')
        return None, None
    
    with open(html_file, 'r') as f:
        html = f.read()
    
    # Extract title
    title_match = re.search(r'<h1>(.*?)</h1>', html)
    title = title_match.group(1) if title_match else f'第{chapter_num}章'
    
    # Extract main content
    main_match = re.search(r'<main>(.*?)</main>', html, re.DOTALL)
    if not main_match:
        log(f'❌ No <main> content found')
        return None, None
    
    content = main_match.group(1)
    content = re.sub(r'<[^>]+>', '', content)
    content = content.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    
    # Remove metadata: "預計閱讀：X 分鐘"
    content = re.sub(r'預計閱讀[：:]\s*\d+\s*分鐘[（(]約\s*[\d,]+\s*字[）)].*', '', content)
    content = re.sub(r'預計閱讀.*?\n', '\n', content)
    content = re.sub(r'\n{3,}', '\n\n', content)
    content = content.strip()
    
    full_text = f'{title}。\n\n{content}'
    log(f'📝 Chapter {chapter_num}: {len(full_text)} chars extracted')
    return full_text, title

def generate_tts(text, chapter_num):
    """Generate TTS audio using Mosi API (韩立 voice)"""
    if not os.path.exists(MOSI_KEY_FILE):
        log('❌ Mosi API key not found')
        return None
    
    with open(MOSI_KEY_FILE) as f:
        api_key = f.read().strip()
    
    log(f'🎤 Submitting TTS (async) for Chapter {chapter_num} ({len(text)} chars)...')
    
    data = json.dumps({
        'model': TTS_MODEL,
        'input': text,
        'voice': VOICE_ID,
        'response_format': 'mp3',
        'delivery_method': 'url',
        'async': True,
        'language': 'zh'
    }).encode()
    
    req = urllib.request.Request(f'{MOSI_API}/audio/speech', data=data, method='POST')
    req.add_header('Authorization', 'Bearer ' + api_key)
    req.add_header('Content-Type', 'application/json')
    
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        task_id = result.get('id', '')
        log(f'   Task: {task_id[:30]}..., Status: {result.get("status")}')
        
        # Poll for completion
        for i in range(120):
            time.sleep(5)
            try:
                req2 = urllib.request.Request(f'{MOSI_API}/audio/tasks/{task_id}')
                req2.add_header('Authorization', 'Bearer ' + api_key)
                resp2 = urllib.request.urlopen(req2, timeout=15)
                task = json.loads(resp2.read())
                status = task.get('status', '')
                
                if status == 'SUCCESS':
                    audio_url = task.get('url', '')
                    if audio_url:
                        os.makedirs(TMP_DIR, exist_ok=True)
                        mp3_path = os.path.join(TMP_DIR, f'chapter-{chapter_num}.mp3')
                        urllib.request.urlretrieve(audio_url, mp3_path)
                        size = os.path.getsize(mp3_path)
                        log(f'✅ Downloaded: {size/1048576:.1f} MB')
                        
                        # Compress to 128kbps
                        final_path = os.path.join(TMP_DIR, f'chapter-{chapter_num}-final.mp3')
                        subprocess.run([
                            'ffmpeg', '-y', '-i', mp3_path,
                            '-codec:a', 'libmp3lame', '-b:a', '128k',
                            final_path
                        ], capture_output=True)
                        
                        final_size = os.path.getsize(final_path)
                        log(f'✅ Compressed to 128kbps: {final_size/1048576:.1f} MB')
                        return final_path
                    break
                elif status == 'FAILED':
                    log(f'❌ TTS failed: {json.dumps(task, ensure_ascii=False)[:200]}')
                    return None
                
                if i % 12 == 0 and i > 0:
                    log(f'   [{i*5}s] {status}')
            except Exception as e:
                if i % 12 == 0 and i > 0:
                    log(f'   [{i*5}s] poll retry...')
        else:
            log(f'❌ Timeout waiting for TTS task')
            return None
    except urllib.error.HTTPError as e:
        log(f'❌ Mosi API error: HTTP {e.code}: {e.read().decode()[:200]}')
        return None

def download_from_dropbox_fallback(chapter_num):
    """Fallback: Download pre-generated WAV from Dropbox, convert to MP3"""
    log(f'🔍 Checking Dropbox for EP{chapter_num:02d}.wav...')
    
    # Refresh token
    if not os.path.exists(DROPBOX_CREDS_FILE):
        log('  No Dropbox creds')
        return None
    
    with open(DROPBOX_CREDS_FILE) as f:
        creds = {}
        for line in f:
            if '=' in line:
                k, v = line.strip().split('=', 1)
                creds[k] = v
    
    body = 'grant_type=refresh_token&refresh_token=' + creds['REFRESH_TOKEN'] + '&client_id=' + creds['APP_KEY'] + '&client_secret=' + creds['APP_SECRET']
    req = urllib.request.Request('https://api.dropboxapi.com/oauth2/token', data=body.encode(), method='POST')
    try:
        token = json.loads(urllib.request.urlopen(req).read())['access_token']
    except:
        log('  ❌ Token refresh failed')
        return None
    
    # Download
    filename = f'EP{chapter_num:02d}.wav'
    path = f'/萬古塵埃/{filename}'
    url = 'https://content.dropboxapi.com/2/files/download'
    req = urllib.request.Request(url, method='POST')
    req.add_header('Authorization', 'Bearer ' + token)
    req.add_header('Dropbox-API-Arg', json.dumps({"path": path}))
    
    try:
        resp = urllib.request.urlopen(req, timeout=120)
        wav_data = resp.read()
        wav_path = os.path.join(TMP_DIR, filename)
        os.makedirs(TMP_DIR, exist_ok=True)
        with open(wav_path, 'wb') as f:
            f.write(wav_data)
        log(f'  ✅ Downloaded {filename} ({len(wav_data)/1048576:.1f} MB)')
        
        # Convert to MP3
        mp3_path = os.path.join(TMP_DIR, f'chapter-{chapter_num}.mp3')
        subprocess.run(['ffmpeg', '-y', '-i', wav_path, '-codec:a', 'libmp3lame', '-b:a', '128k', mp3_path], capture_output=True)
        mp3_size = os.path.getsize(mp3_path)
        log(f'  ✅ Converted to MP3 ({mp3_size/1048576:.1f} MB)')
        return mp3_path
    except urllib.error.HTTPError as e:
        log(f'  ❌ {filename} not found (HTTP {e.code})')
        return None

def upload_to_r2(mp3_path):
    """Upload MP3 to R2"""
    script = os.path.join(WORKSPACE, 'scripts', 'upload_audio_r2.py')
    result = subprocess.run(
        ['python3', script, mp3_path],
        capture_output=True, text=True, cwd=WORKSPACE
    )
    if '✅ 完成' in result.stdout:
        log('✅ Uploaded to R2')
        return True
    log(f'❌ Upload failed: {result.stdout[-200:]}')
    return False

def inject_player(chapter_num):
    """Inject audio player into chapter HTML"""
    script = os.path.join(WORKSPACE, 'scripts', 'inject_audio_player.py')
    result = subprocess.run(
        ['python3', script, str(chapter_num)],
        capture_output=True, text=True, cwd=WORKSPACE
    )
    ok = '✅' in result.stdout
    log(f'💉 Player inject: {"✅" if ok else "⚠️"}')
    return ok

def commit_push(chapter_num):
    """Commit and push"""
    subprocess.run(['git', '-C', WORKSPACE, 'add', f'chapter-{chapter_num}.html'], capture_output=True)
    result = subprocess.run(['git', '-C', WORKSPACE, 'commit', '-m',
        f'🎧 feat: Mosi TTS audio for Chapter {chapter_num} (韩立声)'], capture_output=True, text=True)
    push = subprocess.run(['git', '-C', WORKSPACE, 'push'], capture_output=True, text=True)
    if push.returncode == 0:
        log('🚀 Pushed to GitHub')
        return True
    log(f'⚠️  Push issue')
    return False

def main():
    state = read_state()
    ch = state['last_chapter'] + 1
    log(f'📋 Next: Chapter {ch}')
    
    # Extract text
    text, title = extract_chapter_text(ch)
    if not text:
        log(f'❌ Cannot extract Chapter {ch}')
        return 1
    
    # Try Mosi TTS first
    mp3 = generate_tts(text, ch)
    if not mp3:
        log(f'⚠️  Mosi TTS failed (可能quota用完), 嘗試 Dropbox fallback...')
        mp3 = download_from_dropbox_fallback(ch)
        if not mp3:
            log(f'❌ Both Mosi and Dropbox failed — skipping today')
            return 0  # Don't error, just skip
    
    # Upload
    if not upload_to_r2(mp3):
        return 1
    
    # Inject player
    inject_player(ch)
    
    # Update state
    state['last_chapter'] = ch
    state['total_processed'] = state.get('total_processed', 0) + 1
    state['last_sync'] = datetime.now().isoformat()
    save_state(state)
    
    # Push
    commit_push(ch)
    
    log(f'🎉 Chapter {ch} done! ({title})')
    return 0

if __name__ == '__main__':
    sys.exit(main())
