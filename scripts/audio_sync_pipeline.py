#!/usr/bin/env python3
"""
audio_sync_pipeline.py — Daily Audio Sync Pipeline
取代 audio-daily-cron.sh (shell script)

流程：
  1. 檢查 Dropbox token，過期則 refresh
  2. 掃描 Dropbox /萬古塵埃/ 所有 chapter-{N}.mp3
  3. 對照 R2 真實情況 → 找出 Dropbox 有但 R2 冇既 audio
  4. 批量下載 → 上傳 R2 → inject player
  5. 驗證 → git push → 更新 state

用法：
  python3 scripts/audio_sync_pipeline.py          # 預設模式：處理所有 pending
  python3 scripts/audio_sync_pipeline.py --dry-run # 只檢視唔執行
  python3 scripts/audio_sync_pipeline.py --ch 21   # 只處理指定章節
"""

import os
import re
import sys
import json
import time
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# ==== CONFIG ====
DAILY_LIMIT = 1  # 每日只處理 1 章（大肥喵指定）
WORKSPACE = "/home/openclaw/.openclaw/workspace"
TOKEN_FILE = f"{WORKSPACE}/.token-store/dropbox-token.txt"
CREDS_FILE = f"{WORKSPACE}/.token-store/dropbox-app-creds.txt"
STATE_FILE = f"{WORKSPACE}/.dropbox-sync/audio_state.json"
LOG_FILE = f"{WORKSPACE}/.dropbox-sync/audio-cron.log"
BOT_TOKEN_FILE = f"{WORKSPACE}/.token-store/telegram-bot-token.txt"
CHAT_ID = "5344443732"
AUDIO_BASE = "https://audio.kofhk.com/audio"
DBSYNC_DIR = f"{WORKSPACE}/.dropbox-sync"

os.chdir(WORKSPACE)
os.makedirs(DBSYNC_DIR, exist_ok=True)
os.makedirs("/tmp/audio-sync", exist_ok=True)


# ==== LOGGING ====
def log(msg, also_stdout=True):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{ts}] {msg}"
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    if also_stdout:
        print(line)


def _ensure_bot_token():
    """Self-healing: token file 唔見/空時，自動從 OpenClaw config 提取重建"""
    if os.path.exists(BOT_TOKEN_FILE):
        with open(BOT_TOKEN_FILE) as f:
            if f.read().strip():
                return True
    try:
        cfg_path = "/home/openclaw/.openclaw/openclaw.json"
        with open(cfg_path) as f:
            cfg = json.load(f)
        token = cfg.get("channels", {}).get("telegram", {}).get("botToken", "")
        if not token:
            log("  ⚠️ openclaw.json 冇 botToken", also_stdout=False)
            return False
        with open(BOT_TOKEN_FILE, "w") as f:
            f.write(token.strip() + "\n")
        os.chmod(BOT_TOKEN_FILE, 0o600)
        log("  🔧 Bot token 已從 openclaw.json 自動重建", also_stdout=False)
        return True
    except Exception as e:
        log(f"  ⚠️ Bot token rebuild failed: {e}", also_stdout=False)
        return False


def notify(msg):
    """Send Telegram notification to user"""
    if not _ensure_bot_token():
        log(f"  ⚠️ No bot token file, can't notify", also_stdout=False)
        return
    with open(BOT_TOKEN_FILE) as f:
        token = f.read().strip()
    if not token:
        return
    try:
        subprocess.run([
            "curl", "-s", "-X", "POST",
            f"https://api.telegram.org/bot{token}/sendMessage",
            "-d", f"chat_id={CHAT_ID}",
            "-d", f"text={msg}",
            "-d", "parse_mode=HTML"
        ], capture_output=True, timeout=10)
    except Exception as e:
        log(f"  ⚠️ Notify failed: {e}", also_stdout=False)


# ==== DROPBOX TOKEN MANAGEMENT ====
def refresh_dropbox_token():
    """Check if token is valid, refresh if expired. Returns token string."""
    def _read_token():
        if not os.path.exists(TOKEN_FILE):
            return ""
        with open(TOKEN_FILE) as f:
            return f.read().strip()

    token = _read_token()
    if not token:
        log("  ⚠️ Token file empty")
        return token

    # Quick validation check
    r = subprocess.run([
        "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
        "-X", "POST", "https://api.dropboxapi.com/2/files/get_metadata",
        "-H", f"Authorization: Bearer {token}",
        "-H", "Content-Type: application/json",
        "-d", '{"path":"/"}'
    ], capture_output=True, text=True, timeout=15)
    http_code = r.stdout.strip()

    if http_code == "200":
        log("  ✓ Token still valid")
        return token

    log("  🔄 Token expired, refreshing...")

    if not os.path.exists(CREDS_FILE):
        log("  ⚠️ No dropbox-app-creds.txt, can't refresh")
        return token

    # Parse app credentials
    creds = {}
    with open(CREDS_FILE) as f:
        for line in f:
            line = line.strip()
            if "=" in line:
                k, v = line.split("=", 1)
                creds[k.strip()] = v.strip()

    app_key = creds.get("APP_KEY", "")
    app_secret = creds.get("APP_SECRET", "")
    refresh_tok = creds.get("REFRESH_TOKEN", "")
    if not app_key or not refresh_tok:
        log("  ⚠️ Missing APP_KEY or REFRESH_TOKEN in creds")
        return token

    # Do refresh (same as dropbox_volume4_sync.py)
    cmd = [
        "curl", "-s", "-X", "POST",
        "https://api.dropboxapi.com/oauth2/token",
        "-d", "grant_type=refresh_token",
        "-d", f"refresh_token={refresh_tok}",
        "-d", f"client_id={app_key}",
    ]
    if app_secret:
        cmd.extend(["-d", f"client_secret={app_secret}"])
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)

    try:
        data = json.loads(r.stdout)
        new_token = data.get("access_token", "")
        if new_token:
            with open(TOKEN_FILE, "w") as f:
                f.write(new_token)
            os.chmod(TOKEN_FILE, 0o600)
            log("  ✅ Token refreshed")
            return new_token
        else:
            log(f"  ❌ Refresh failed: {data}")
            return token
    except Exception as e:
        log(f"  ❌ Refresh error: {e}")
        return token


def dropbox_api(endpoint, data, download_to=None, token=None):
    """Call Dropbox API with proper headers"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    if download_to:
        # File download
        headers["Dropbox-API-Arg"] = json.dumps(data)
        r = subprocess.run([
            "curl", "-s", "-X", "POST",
            f"https://content.dropboxapi.com{endpoint}",
            "-H", f"Authorization: Bearer {token}",
            "-H", f"Dropbox-API-Arg: {json.dumps(data)}",
            "-o", download_to
        ], capture_output=True, timeout=120)
        return {"output": r.stdout, "err": r.stderr, "success": os.path.getsize(download_to) > 0}
    else:
        r = subprocess.run([
            "curl", "-s", "-X", "POST",
            f"https://api.dropboxapi.com{endpoint}",
            "-H", f"Authorization: Bearer {token}",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(data)
        ], capture_output=True, text=True, timeout=30)
        try:
            return json.loads(r.stdout)
        except json.JSONDecodeError:
            return {"error": r.stdout}


# ==== CORE FUNCTIONS ====
def scan_dropbox_audio(token):
    """Scan Dropbox /萬古塵埃/ for all chapter-{N}.mp3 files"""
    log("[scan] Scanning Dropbox /萬古塵埃/...")
    r = dropbox_api("/2/files/list_folder", {"path": "/萬古塵埃", "limit": 100}, token=token)
    entries = r.get("entries", [])
    if not entries and "error" in r:
        log(f"  ✗ List folder failed: {r.get('error','')}")
        # Try search fallback
        sr = dropbox_api("/2/files/search_v2", {"query": "chapter-", "path": "/", "max_results": 100}, token=token)
        matches = sr.get("matches", [])
        audio_files = {}
        for m in matches:
            md = m.get("metadata", {}).get("metadata", {})
            name = md.get("name", "")
            path = md.get("path_display", "")
            size = md.get("size", 0)
            if re.match(r"chapter-\d+\.mp3", name):
                ch = int(re.search(r"chapter-(\d+)", name).group(1))
                audio_files[ch] = {"path": path, "name": name, "size": size}
        log(f"  [search_v2 fallback] Found {len(audio_files)} audio files")
        return audio_files

    audio_files = {}
    for e in entries:
        name = e.get("name", "")
        if re.match(r"chapter-\d+\.mp3", name):
            m = re.search(r"chapter-(\d+)", name)
            if m:
                ch = int(m.group(1))
                audio_files[ch] = {
                    "path": e.get("path_display", f"/萬古塵埃/{name}"),
                    "name": name,
                    "size": e.get("size", 0),
                    "modified": e.get("server_modified", "")
                }
    log(f"  Found {len(audio_files)} audio files in Dropbox: CH{min(audio_files.keys())}-CH{max(audio_files.keys())}" if audio_files else "  Found 0 audio files")
    return audio_files


def check_r2_audio(ch_nums):
    """Check which chapters already have audio on R2"""
    log(f"[r2-check] Verifying {len(ch_nums)} chapters on R2...")
    existing = set()
    for ch in sorted(ch_nums):
        r = subprocess.run([
            "curl", "-sI", f"{AUDIO_BASE}/chapter-{ch}.mp3"
        ], capture_output=True, text=True, timeout=10)
        if "200" in r.stdout.split("\n")[0] if r.stdout else False:
            existing.add(ch)
        # Small delay to not hammer R2
        time.sleep(0.2)
    log(f"  R2 has: {len(existing)} / {len(ch_nums)}")
    return existing


def process_chapter(ch, dropbox_path, token):
    """Process a single chapter: download → upload R2 → inject player → verify"""
    log(f"\n{'='*50}")
    log(f"[ch{ch}] Processing {dropbox_path}...")
    tmp_file = f"/tmp/audio-sync/chapter-{ch}.mp3"

    # 1. Download from Dropbox
    log(f"[ch{ch}] Downloading from Dropbox...")
    r = dropbox_api("/2/files/download", {"path": dropbox_path}, download_to=tmp_file, token=token)
    size = os.path.getsize(tmp_file) if os.path.exists(tmp_file) else 0
    if size == 0:
        log(f"  ✗ Download failed (0 bytes)")
        return False
    log(f"  ✓ Downloaded: {size:,} bytes ({size/1024/1024:.1f} MB)")

    # 2. Upload to R2
    log(f"[ch{ch}] Uploading to R2...")
    r = subprocess.run([
        "python3", f"{WORKSPACE}/scripts/upload_audio_r2.py",
        tmp_file, f"chapter-{ch}.mp3"
    ], capture_output=True, text=True, timeout=60)
    for line in r.stdout.strip().split("\n"):
        if line.strip():
            log(f"  {line.strip()}", also_stdout=False)
    if r.returncode != 0:
        log(f"  ✗ R2 upload failed (exit code {r.returncode})")
        os.remove(tmp_file)
        return False

    # 3. Verify R2
    log(f"[ch{ch}] Verifying R2...")
    vr = subprocess.run([
        "curl", "-sI", f"{AUDIO_BASE}/chapter-{ch}.mp3"
    ], capture_output=True, text=True, timeout=10)
    if "200" in (vr.stdout.split("\n")[0] if vr.stdout else ""):
        log(f"  ✓ R2 verified: HTTP 200")
    else:
        log(f"  ✗ R2 verify failed: {vr.stdout[:100]}")
        os.remove(tmp_file)
        return False

    # 4. Inject audio player
    log(f"[ch{ch}] Injecting audio player...")
    r = subprocess.run([
        "python3", f"{WORKSPACE}/scripts/inject_audio_player.py", str(ch)
    ], capture_output=True, text=True, timeout=30)
    for line in r.stdout.strip().split("\n"):
        if line.strip():
            log(f"  {line.strip()}", also_stdout=False)

    # 5. Verify HTML
    html_file = f"{WORKSPACE}/chapter-{ch}.html"
    if os.path.exists(html_file):
        with open(html_file) as f:
            content = f.read()
        audio_count = content.count("<audio")
        log(f"[ch{ch}] HTML audio tags: {audio_count}")
        if audio_count == 0:
            log(f"  ✗ No audio tag in HTML!")
            os.remove(tmp_file)
            return False
    else:
        log(f"  ⚠️ chapter-{ch}.html not found!")

    os.remove(tmp_file)
    log(f"[ch{ch}] ✅ Complete!")
    return True


def git_push(chs):
    """Git add, commit and push"""
    log(f"\n[git] Pushing {len(chs)} chapter(s)...")
    files = [f"chapter-{ch}.html" for ch in chs]
    r = subprocess.run(["git", "add", "-A"], capture_output=True, text=True, timeout=15)
    if r.returncode != 0:
        log(f"  ✗ git add failed: {r.stderr[:200]}")
        return False

    # Check if anything to commit
    r = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True, timeout=10)
    if r.returncode == 0:
        log(f"  Nothing to commit")
        return True

    ch_str = ",".join([f"ch{c}" for c in sorted(chs)])
    r = subprocess.run([
        "git", "commit", "-m", f"chore: audio {ch_str} {datetime.now().strftime('%Y-%m-%d')}"
    ], capture_output=True, text=True, timeout=15)
    log(f"  Commit: {r.stdout.strip()[:200]}")

    # Pull rebase then push
    r = subprocess.run(["git", "pull", "--rebase", "origin", "main"],
                       capture_output=True, text=True, timeout=30)
    log(f"  Rebase: {r.stdout.strip()[:100]}{' (conflict!)' if 'CONFLICT' in r.stdout else ''}")
    if r.returncode != 0:
        log(f"  ✗ Rebase failed: {r.stderr[:200]}")
        return False

    r = subprocess.run(["git", "push", "origin", "main"],
                       capture_output=True, text=True, timeout=30)
    log(f"  Push: {r.stdout.strip()[:200]}")
    if r.returncode != 0:
        log(f"  ✗ Push failed: {r.stderr[:200]}")
        return False
    return True


def update_state(last_ch, processed_count, note=""):
    """Update audio_state.json with audit trail"""
    state = {
        "last_chapter": last_ch,
        "total_processed": processed_count,
        "last_sync": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "audio_sync_pipeline.py",
        "notes": note
    }
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    log(f"[state] Updated: last_chapter={last_ch}, total={processed_count}")


def load_state():
    """Load current state"""
    if not os.path.exists(STATE_FILE):
        return {"last_chapter": 0, "total_processed": 0}
    with open(STATE_FILE) as f:
        return json.load(f)


# ==== MAIN ====
def main():
    dry_run = "--dry-run" in sys.argv
    single_ch = None
    for arg in sys.argv:
        if arg.startswith("--ch="):
            single_ch = int(arg.split("=")[1])

    log("=" * 60)
    log("🚀 audio_sync_pipeline.py started")
    log(f"    {'DRY RUN' if dry_run else 'LIVE'} | {'Single: ch' + str(single_ch) if single_ch else 'Batch mode'}")
    log("=" * 60)

    # Step 0: Get valid token
    token = refresh_dropbox_token()
    if not token:
        log("❌ No valid token, aborting")
        notify("🎧 Audio sync failed: no valid Dropbox token")
        return 1

    # Step 1: Scan Dropbox
    dropbox_files = scan_dropbox_audio(token)
    if not dropbox_files:
        log("❌ No audio files found in Dropbox")
        return 0

    # Step 2: If single chapter specified, filter to it
    if single_ch:
        if single_ch not in dropbox_files:
            log(f"❌ Chapter {single_ch} not found in Dropbox")
            return 1
        pending_chs = {single_ch: dropbox_files[single_ch]}
    else:
        # Determine what needs processing by checking R2
        all_chs = set(dropbox_files.keys())
        r2_chs = check_r2_audio(all_chs)
        pending_chs = {ch: dropbox_files[ch] for ch in sorted(all_chs) if ch not in r2_chs}

    if not pending_chs:
        log("✅ All Dropbox audio files already on R2")
        return 0

    # 每日限額：只處理 DAILY_LIMIT 章
    daily_limit = DAILY_LIMIT
    pending_chs = dict(list(pending_chs.items())[:daily_limit])

    log(f"\n📋 Pending: {len(pending_chs)} chapters to process (daily limit={daily_limit})")
    for ch in sorted(pending_chs.keys()):
        f = pending_chs[ch]
        log(f"  CH{ch:>3}: {f['name']} ({f['size']//1024} KB)")

    if dry_run:
        log("\n🏁 DRY RUN — no changes made")
        return 0

    # Step 3: Process each chapter
    succeeded = []
    failed = []
    for ch in sorted(pending_chs.keys()):
        f = pending_chs[ch]
        ok = process_chapter(ch, f["path"], token)
        if ok:
            succeeded.append(ch)
        else:
            failed.append(ch)
            notify(f"🎧 ch{ch} audio sync failed — see log")

    # Step 4: Git push
    if succeeded:
        git_push(succeeded)
    else:
        log("⚠️ No chapters successfully processed, skipping git push")

    # Step 5: Update state
    if succeeded:
        update_state(
            max(succeeded),
            load_state().get("total_processed", 0) + len(succeeded),
            f"Synced: ch{','.join(map(str,succeeded))}; Failed: ch{','.join(map(str,failed))}" if failed else f"Synced: ch{','.join(map(str,succeeded))}"
        )

    # Step 6: Summary
    log("\n" + "=" * 60)
    log(f"📊 SUMMARY")
    log(f"   ✅ Succeeded: {len(succeeded)} — CH{succeeded}")
    log(f"   ❌ Failed:    {len(failed)} — {failed if failed else 'None'}")
    if succeeded:
        notify(f"🎧 Audio sync complete: ch{','.join(map(str,succeeded))} {'| ⚠️ Failed: '+','.join(map(str,failed)) if failed else ''}")
    log("=" * 60)
    log("✅ Pipeline complete")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
