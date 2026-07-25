"""Generate sitemap.xml for kofhk.com with all chapters."""
import json
import os
from datetime import datetime, timezone

BASE = "https://kofhk.com"
SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

chapter_index_path = os.path.join(SITE_DIR, "workers", "chat-worker", "chapter-titles.json")
with open(chapter_index_path, "r", encoding="utf-8") as f:
    chapter_index = json.load(f)

chapters = chapter_index.get("chapters", [])
total = chapter_index.get("total", len(chapters))

print(f"Total chapters in index: {total}")

today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

static_pages = [
    ("/", "daily", "1.0"),
    ("/chapters.html", "daily", "1.0"),
    ("/author.html", "weekly", "0.8"),
    ("/news.html", "daily", "0.8"),
    ("/finance.html", "daily", "0.8"),
    ("/dashboard.html", "weekly", "0.7"),
    ("/bus-eta.html", "weekly", "0.7"),
]

lines = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
]

for path, freq, priority in static_pages:
    lines.append("  <url>")
    lines.append(f"    <loc>{BASE}{path}</loc>")
    lines.append(f"    <lastmod>{today}</lastmod>")
    lines.append(f"    <changefreq>{freq}</changefreq>")
    lines.append(f"    <priority>{priority}</priority>")
    lines.append("  </url>")

for ch in chapters:
    ch_num = ch.get("n", 0)
    ch_file = os.path.join(SITE_DIR, f"chapter-{ch_num}.html")
    if os.path.exists(ch_file):
        mtime = datetime.fromtimestamp(os.path.getmtime(ch_file), tz=timezone.utc)
        lastmod = mtime.strftime("%Y-%m-%d")
    else:
        lastmod = today
    lines.append("  <url>")
    lines.append(f"    <loc>{BASE}/chapter-{ch_num}.html</loc>")
    lines.append(f"    <lastmod>{lastmod}</lastmod>")
    lines.append("    <changefreq>weekly</changefreq>")
    lines.append("    <priority>0.6</priority>")
    lines.append("  </url>")

lines.append("</urlset>")

sitemap_path = os.path.join(SITE_DIR, "sitemap.xml")
with open(sitemap_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print(f"Written {len(chapters)} chapters + {len(static_pages)} pages to {sitemap_path}")
print(f"Total URLs: {len(chapters) + len(static_pages)}")
