#!/usr/bin/env python3
"""
修復章節頁面嘅「下一章」連結

背景（2026-10-23）：dropbox_volume*_sync.py 舊流程每次同步只會將「最新一章」嘅
下一章連結改成返回目錄，之前批次尾章（例如 1746）嘅下一章永遠停喺 chapters.html，
讀者撳「下一章」會彈返目錄而唔係去到下一章。

用法：python3 scripts/fix_broken_next_links.py [novel_dir]
"""
import os
import re
import sys

NOVEL_DIR = sys.argv[1] if len(sys.argv) > 1 else "/home/openclaw/.openclaw/workspace"


def main():
    files = [f for f in os.listdir(NOVEL_DIR) if re.match(r"chapter-\d+\.html$", f)]
    if not files:
        print("❌ 搵唔到章節檔案")
        return 1
    nums = sorted(int(re.search(r"\d+", f).group()) for f in files)
    existing = set(nums)
    fixed = []

    for n in nums[:-1]:
        if (n + 1) not in existing:
            continue
        path = os.path.join(NOVEL_DIR, f"chapter-{n}.html")
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError:
            continue
        m = re.search(r'<a\b[^>]*\bid="nextLink"[^>]*>', content)
        if not m:
            continue
        tag = m.group(0)
        h = re.search(r'\bhref="([^"]*)"', tag)
        if not h:
            continue
        href = h.group(1)
        base = os.path.basename(href.split("#")[0].split("?")[0])
        if base in ("chapters.html", "#") or base == "":
            expected = f"chapter-{n + 1}.html"
            new_tag = tag[:h.start(1)] + expected + tag[h.end(1):]
            content = content[:m.start()] + new_tag + content[m.end():]
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            fixed.append((n, href, expected))

    print(f"✅ 掃描 {len(nums)} 章，修復 {len(fixed)} 個「下一章」連結")
    for n, old, new in fixed[:10]:
        print(f"   第{n}章: {old} → {new}")
    if len(fixed) > 10:
        print(f"   ... 仲有 {len(fixed) - 10} 個")
    return 0


if __name__ == "__main__":
    sys.exit(main())
