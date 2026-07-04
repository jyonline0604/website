"""
Local data updater for KOFHK website.
Fetches fresh market data, finance news, and AI news.
Usage: python local_update.py
"""
import sys
import os
import json
from datetime import datetime

# Add scripts dir to path to reuse existing fetchers
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(SCRIPTS_DIR)
sys.path.insert(0, SCRIPTS_DIR)

print(f"Workspace: {WORKSPACE}")
print(f"Scripts:   {SCRIPTS_DIR}")

# ── 1. Finance Market Data ──────────────────────────────────────────
print("\n" + "=" * 50)
print("1/3 獲取財經市場數據...")

from fetch_finance_data import FinanceDataFetcher

fetcher = FinanceDataFetcher()
fetcher.cache_file = os.path.join(WORKSPACE, "finance-data.json")
fetcher.cache_duration = 0  # force fresh fetch (disable cache)
data = fetcher.fetch_all_data()

output_path = os.path.join(WORKSPACE, "finance-data.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"  -> finance-data.json ({os.path.getsize(output_path)} bytes)")


# ── 2. Finance News ─────────────────────────────────────────────────
print("\n" + "=" * 50)
print("2/3 獲取財經新聞...")

import urllib.request
import xml.etree.ElementTree as ET
import re

RSS_SOURCES = [
    {
        "name": "MarketWatch",
        "url": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
        "keywords": ["market", "stock", "business"],
        "category": "stocks",
        "icon": "\U0001f4c8"
    },
    {
        "name": "CoinDesk",
        "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "keywords": ["bitcoin", "crypto", "blockchain", "ethereum"],
        "category": "crypto",
        "icon": "₿"
    },
]

all_finance_news = []
for source in RSS_SOURCES:
    try:
        req = urllib.request.Request(source["url"], headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=15) as response:
            raw_data = response.read()
        root = ET.fromstring(raw_data)
        items = root.findall(".//item")[:5]
        for item in items:
            title_el = item.find("title")
            link_el = item.find("link")
            desc_el = item.find("description")
            pubdate_el = item.find("pubDate")

            title = title_el.text if title_el is not None else ""
            link = link_el.text if link_el is not None else "#"
            raw_desc = desc_el.text if desc_el is not None else ""
            clean_desc = re.sub(r"<[^>]+>", "", raw_desc)[:300]
            pubdate = pubdate_el.text if pubdate_el is not None else datetime.now().isoformat()

            if title and len(title) > 10:
                all_finance_news.append({
                    "title": title.strip(),
                    "link": link.strip(),
                    "description": clean_desc.strip(),
                    "pubDate": pubdate,
                    "source": source["name"],
                    "category": source["category"],
                    "icon": source["icon"]
                })
        print(f"  {source['name']}: {len(items)} items")
    except Exception as e:
        print(f"  !! {source['name']}: {e}")

all_finance_news = all_finance_news[:8]

finance_news_data = {
    "timestamp": datetime.now().isoformat(),
    "total_news": len(all_finance_news),
    "news": all_finance_news
}

output_path = os.path.join(WORKSPACE, "finance-news.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(finance_news_data, f, ensure_ascii=False, indent=2)
print(f"  -> finance-news.json: {len(all_finance_news)} articles")


# ── 3. AI News ──────────────────────────────────────────────────────
print("\n" + "=" * 50)
print("3/3 獲取AI新聞...")

AI_FEEDS = [
    ("TechCrunch", "https://techcrunch.com/feed/", "model"),
    ("The Verge", "https://www.theverge.com/rss/index.xml", "industry"),
    ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index", "research"),
    ("Wired", "https://www.wired.com/feed/rss", "industry"),
    ("BBC Technology", "https://feeds.bbci.co.uk/news/technology/rss.xml", "industry"),
    ("Reuters Tech", "https://www.reutersagency.com/feed/", "industry"),
]

AI_KEYWORDS = [
    "AI", "artificial intelligence", "GPT", "LLM", "large language model",
    "machine learning", "deep learning", "neural network", "chatbot",
    "Copilot", "Gemini", "Claude", "OpenAI", "Anthropic", "transformer",
    "diffusion", "stable diffusion", "DALL", "Midjourney",
    "NLP", "computer vision", "robotics", "autonomous",
    "model", "training", "fine-tuning", "inference", "token",
    "generative", "prompt", "agent", "AGI", "alignment"
]

all_ai_news = []
for name, url, cat in AI_FEEDS:
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read()
        root = ET.fromstring(raw)
        items = root.findall(".//item")[:5]
        count = 0
        for item in items:
            title_el = item.find("title")
            link_el = item.find("link")
            desc_el = item.find("description")
            pubdate_el = item.find("pubDate")

            title = title_el.text if title_el is not None else ""
            link = link_el.text if link_el is not None else "#"
            raw_desc = desc_el.text if desc_el is not None else ""
            clean_desc = re.sub(r"<[^>]+>", "", raw_desc)[:300]
            pubdate = pubdate_el.text if pubdate_el is not None else datetime.now().isoformat()

            # Filter: only include AI-related articles
            title_upper = title.upper()
            is_ai = any(kw.upper() in title_upper for kw in AI_KEYWORDS)
            if not is_ai:
                is_ai = any(kw.upper() in clean_desc.upper() for kw in AI_KEYWORDS[:15])

            if title and is_ai:
                all_ai_news.append({
                    "title": title.strip(),
                    "link": link.strip(),
                    "description": clean_desc.strip(),
                    "pubDate": pubdate,
                    "source": name,
                    "category": cat
                })
                count += 1
        print(f"  {name}: {count} AI articles")
    except Exception as e:
        print(f"  !! {name}: {e}")

all_ai_news = all_ai_news[:8]

ai_news_data = {
    "lastUpdate": datetime.now().isoformat(),
    "count": len(all_ai_news),
    "news": all_ai_news
}

output_path = os.path.join(WORKSPACE, "news-data.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(ai_news_data, f, ensure_ascii=False, indent=2)
print(f"  -> news-data.json: {len(all_ai_news)} articles")

# ── Summary ─────────────────────────────────────────────────────────
print("\n" + "=" * 50)
print("完成! 更新文件:")
for fname in ["finance-data.json", "finance-news.json", "news-data.json"]:
    fpath = os.path.join(WORKSPACE, fname)
    if os.path.exists(fpath):
        mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
        print(f"  {fname}  ({os.path.getsize(fpath)} bytes, {mtime.isoformat()})")
    else:
        print(f"  {fname}  MISSING!")
print("=" * 50)
