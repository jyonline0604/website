#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate feed.xml (RSS 2.0) for 萬古塵埃 from assets/chapters-data.json.

pubDate for each chapter is linearly interpolated between the first chapter's
publish date and the latest chapter's publish date, so dates stay within a
realistic range instead of spanning 1000+ days.

Usage:
  python3 scripts/generate_rss.py
  python3 scripts/generate_rss.py --latest-date 2026-07-08 --oldest-date 2026-01-01
"""
import json
import sys
import os
import datetime

BASE_URL = "https://kofhk.com"
SITE_TITLE = "萬古塵埃"
SITE_DESC = "《萬古塵埃》官方網站 - 每日更新的AI生成小說，融合科技與修真的奇幻世界。作者：大肥喵。"
AUTHOR = "大肥喵"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse_args():
    base = BASE_URL
    latest = datetime.date.today()
    oldest = datetime.date(2026, 1, 1)
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--base-url" and i + 1 < len(args):
            base = args[i + 1].rstrip("/"); i += 2
        elif args[i] == "--latest-date" and i + 1 < len(args):
            latest = datetime.datetime.strptime(args[i + 1], "%Y-%m-%d").date(); i += 2
        elif args[i] == "--oldest-date" and i + 1 < len(args):
            oldest = datetime.datetime.strptime(args[i + 1], "%Y-%m-%d").date(); i += 2
        else:
            i += 1
    return base, latest, oldest


def load_chapters():
    with open(os.path.join(ROOT, "assets", "chapters-data.json"), encoding="utf-8") as f:
        data = json.load(f)
    data.sort(key=lambda c: c.get("num", 0))
    return data


def xml_escape(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;"))


def main():
    base, latest, oldest = parse_args()
    chapters = load_chapters()
    if not chapters:
        print("No chapters found", file=sys.stderr); sys.exit(1)

    max_num = max(c.get("num", 0) for c in chapters)
    span_days = (latest - oldest).days
    # guard: if only 1 chapter or invalid span, collapse to latest
    denom = max(max_num - 1, 1)
    by_num = {c.get("num"): c for c in chapters}

    items = []
    for num in range(max_num, 0, -1):
        ch = by_num.get(num)
        if not ch:
            continue
        title = ch.get("title", "")
        # num==max -> latest ; num==1 -> oldest ; linear in between
        day_offset = int(round(span_days * (max_num - num) / denom))
        pub_date = latest - datetime.timedelta(days=day_offset)
        pub_rfc = pub_date.strftime("%a, %d %b %Y 00:00:00 +0800")
        link = "%s/chapter-%d.html" % (base, num)
        items.append(
            '    <item>\n'
            '      <title>%s</title>\n' % xml_escape("第%d章 · %s" % (num, title)) +
            '      <link>%s</link>\n' % xml_escape(link) +
            '      <guid isPermaLink="true">%s</guid>\n' % xml_escape(link) +
            '      <pubDate>%s</pubDate>\n' % pub_rfc +
            '      <author>%s</author>\n' % xml_escape(AUTHOR) +
            '      <description>%s</description>\n' % xml_escape(
                "《萬古塵埃》第%d章：%s" % (num, title)) +
            '    </item>'
        )

    build_date = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0800")
    rss = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        '  <channel>\n'
        '    <title>%s</title>\n' % xml_escape(SITE_TITLE) +
        '    <link>%s</link>\n' % xml_escape(base) +
        '    <atom:link href="%s/feed.xml" rel="self" type="application/rss+xml" />\n' % xml_escape(base) +
        '    <description>%s</description>\n' % xml_escape(SITE_DESC) +
        '    <language>zh-Hant</language>\n'
        '    <lastBuildDate>%s</lastBuildDate>\n' % build_date +
        '    <generator>generate_rss.py</generator>\n' +
        '\n'.join(items) +
        '\n  </channel>\n'
        '</rss>\n'
    )
    out = os.path.join(ROOT, "feed.xml")
    with open(out, "w", encoding="utf-8") as f:
        f.write(rss)
    print("Wrote %s with %d items" % (out, len(items)))


if __name__ == "__main__":
    main()
