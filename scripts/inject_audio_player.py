#!/usr/bin/env python3
"""
inject_audio_player.py — 自動喺章節 HTML 加音頻播放器

Usage:
  python3 scripts/inject_audio_player.py 1               # 第1章
  python3 scripts/inject_audio_player.py --range 1 10     # 第1-10章
  python3 scripts/inject_audio_player.py --all             # 全部有音頻嘅章節
  python3 scripts/inject_audio_player.py --remove 1        # 移除播放器
  python3 scripts/inject_audio_player.py --check 1 50      # 檢查邊章有/冇播放器
"""

import os
import re
import sys
import json

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_BASE_URL = "https://audio.kofhk.com/audio"
CRED_FILE = os.path.join(WORKSPACE, ".r2-credentials.json")

AUDIO_PLAYER_HTML = """\
    <!-- 🎧 Audio Player -->
    <div class="audio-player-wrap">
      <span class="audio-icon">🎧</span>
      <audio controls preload="none">
        <source src="{audio_url}" type="audio/mpeg">
        您的瀏覽器不支援音頻播放。
      </audio>
      <span class="audio-label">AI 語音朗讀</span>
    </div>"""

AUDIO_CSS_LINK = '    <link rel="stylesheet" href="assets/audio-player.css">'


def get_chapter_file(num):
    return os.path.join(WORKSPACE, f"chapter-{num}.html")


def has_audio_player(html_content):
    return "audio-player-wrap" in html_content


def has_audio_css(html_content):
    return "audio-player.css" in html_content


def get_audio_url(num):
    """Generate R2 audio URL for a chapter"""
    return f"{AUDIO_BASE_URL}/chapter-{num}.mp3"


def inject_player(num, dry_run=False):
    """Inject audio player into a chapter HTML file"""
    filepath = get_chapter_file(num)
    if not os.path.exists(filepath):
        print(f"  ❌ chapter-{num}.html 唔存在")
        return False

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if has_audio_player(content):
        print(f"  ⏭️  chapter-{num}.html 已經有播放器")
        return "skip"

    # Add CSS link if not present
    if not has_audio_css(content):
        css_line = '\n' + AUDIO_CSS_LINK + '\n'
        # Insert after existing CSS link
        match = re.search(r'(<link rel="stylesheet" href="assets/chapter.css">)', content)
        if match:
            insert_pos = match.end()
            content = content[:insert_pos] + css_line + content[insert_pos:]

    # Insert audio player after top-bar div (before <h1>)
    audio_html = AUDIO_PLAYER_HTML.format(audio_url=get_audio_url(num))
    
    # Find the end of top-bar div and insert before <h1>
    pattern = r'(</div>\s*\n\s*)<h1>'
    result = re.subn(pattern, r'\1' + audio_html + '\n    <h1>', content, count=1)
    
    if result[1] == 0:
        print(f"  ⚠️  chapter-{num}.html: 搵唔到 top-bar/h1 插入點")
        return False

    new_content = result[0]

    if dry_run:
        print(f"  🔍 chapter-{num}.html: preview (dry-run)")
        return True

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"  ✅ chapter-{num}.html: 已注入播放器")
    return True


def remove_player(num, dry_run=False):
    """Remove audio player from a chapter HTML file"""
    filepath = get_chapter_file(num)
    if not os.path.exists(filepath):
        print(f"  ❌ chapter-{num}.html 唔存在")
        return False

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if not has_audio_player(content):
        print(f"  ⏭️  chapter-{num}.html 本來就冇播放器")
        return "skip"

    # Remove the audio player block
    pattern = r'\s*<!-- 🎧 Audio Player -->\s*\n\s*<div class="audio-player-wrap">.*?</div>\s*\n'
    new_content = re.sub(pattern, '\n', content, flags=re.DOTALL)

    if dry_run:
        print(f"  🔍 chapter-{num}.html: remove preview (dry-run)")
        return True

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"  🗑️  chapter-{num}.html: 已移除播放器")
    return True


def check_range(start, end):
    """Check which chapters have audio players"""
    have = []
    missing = []
    for num in range(start, end + 1):
        filepath = get_chapter_file(num)
        if not os.path.exists(filepath):
            missing.append((num, "file_missing"))
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        if has_audio_player(content):
            have.append(num)
        else:
            missing.append((num, "no_player"))

    print(f"\n📊 檢查結果 (Chapter {start}-{end}):")
    print(f"  ✅ 已有播放器: {len(have)} 章")
    print(f"  ❌ 未有播放器: {len(missing)} 章")
    if have:
        print(f"  已有: {', '.join(map(str, have))}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    if sys.argv[1] == "--range":
        if len(sys.argv) < 4:
            print("Usage: inject_audio_player.py --range <start> <end>")
            sys.exit(1)
        start, end = int(sys.argv[2]), int(sys.argv[3])
        print(f"🎧 注入播放器: Chapter {start}-{end}")
        success = 0
        for num in range(start, end + 1):
            result = inject_player(num)
            if result == True:
                success += 1
        print(f"\n✅ 完成: {success}/{end - start + 1} 注入成功")

    elif sys.argv[1] == "--remove":
        if len(sys.argv) < 3:
            print("Usage: inject_audio_player.py --remove <chapter_num>")
            sys.exit(1)
        remove_player(int(sys.argv[2]))

    elif sys.argv[1] == "--check":
        if len(sys.argv) < 3:
            print("Usage: inject_audio_player.py --check <start> [end]")
            sys.exit(1)
        start = int(sys.argv[2])
        end = int(sys.argv[3]) if len(sys.argv) > 3 else start
        check_range(start, end)

    else:
        try:
            num = int(sys.argv[1])
            inject_player(num)
        except ValueError:
            print(__doc__)
