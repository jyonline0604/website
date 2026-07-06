"""Build enriched chapter-titles.json with description preview for better RAG search.

Extracts <title> and <meta name="description"> from each chapter-*.html file.
Output: workers/chat-worker/chapter-titles.json
"""

import json
import re
import os
from pathlib import Path

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = BASE_DIR / "workers" / "chat-worker" / "chapter-titles.json"

# Max chars from description to include (keep index compact)
MAX_DESC_CHARS = 120


def extract_chapter_info(filepath):
    """Extract title and description from a chapter HTML file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            html = f.read()
    except Exception:
        return None

    # Extract title from <title> tag
    title_match = re.search(r"<title>(.*?)</title>", html)
    if not title_match:
        return None
    title = title_match.group(1).strip()
    # Remove site suffix like " - 萬古塵埃"
    title = re.sub(r"\s*[-–—|]\s*萬古塵埃.*$", "", title)

    # Extract description from <meta name="description">
    desc_match = re.search(
        r'<meta\s+name="description"\s+content="([^"]*)"', html
    )
    description = ""
    if desc_match:
        description = desc_match.group(1).strip()
        # Truncate to max chars, breaking at a natural boundary
        if len(description) > MAX_DESC_CHARS:
            # Try to break at sentence boundary
            truncated = description[:MAX_DESC_CHARS]
            # Find last sentence-ending punctuation
            for punct in ["。」", "！", "？", "；", "，", "。", "!", "?", ";", ","]:
                idx = truncated.rfind(punct)
                if idx > MAX_DESC_CHARS // 2:
                    description = truncated[: idx + len(punct)]
                    break
            else:
                description = truncated

    return title, description


def extract_chapter_num(filename):
    """Extract chapter number from filename like 'chapter-442.html'."""
    match = re.search(r"chapter-(\d+)", filename)
    return int(match.group(1)) if match else None


def main():
    print("Building enriched chapter index...")

    chapters = []
    html_files = sorted(
        BASE_DIR.glob("chapter-*.html"),
        key=lambda p: extract_chapter_num(p.name) or 0,
    )

    for filepath in html_files:
        num = extract_chapter_num(filepath.name)
        if num is None:
            continue

        info = extract_chapter_info(filepath)
        if info is None:
            print(f"  SKIP: {filepath.name} (parse error)")
            continue

        title, description = info
        entry = {"n": num, "t": title}
        if description:
            entry["d"] = description
        chapters.append(entry)

    # Sort by chapter number
    chapters.sort(key=lambda c: c["n"])

    index = {
        "chapters": chapters,
        "total": len(chapters),
    }

    # Write JSON
    json_text = json.dumps(index, ensure_ascii=False, separators=(",", ":"))
    OUTPUT_PATH.write_text(json_text, encoding="utf-8")
    size_kb = OUTPUT_PATH.stat().st_size / 1024

    print(f"  Output: {OUTPUT_PATH}")
    print(f"  Chapters: {len(chapters)}")
    print(f"  Size: {size_kb:.1f} KB")

    # Show a few samples
    print("\n  Sample entries:")
    for entry in chapters[:3]:
        desc = entry.get("d", "")[:60]
        print(f"    [{entry['n']}] {entry['t']}")
        if desc:
            print(f"        {desc}...")

    # Show ch442 specifically
    for entry in chapters:
        if entry["n"] == 442:
            print(f"\n  Ch442: {entry['t']}")
            print(f"    Desc: {entry.get('d', 'NO DESC')[:120]}")
            break

    print("\nDone!")


if __name__ == "__main__":
    main()
