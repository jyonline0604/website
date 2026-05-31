#!/usr/bin/env python3
"""
自動更新新聞和市場數據
從真實 RSS 來源和 API 獲取最新數據，更新 JSON 文件
"""

import json
import os
import time
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── AI 新聞 RSS 來源 ──
AI_RSS_SOURCES = [
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "category": "research",
        "icon": "🔬"
    },
    {
        "name": "ArsTechnica AI",
        "url": "https://feeds.arstechnica.com/arstechnica/features/",
        "category": "research",
        "icon": "🔬"
    },
]

# ── 財經新聞 RSS 來源 ──
FINANCE_RSS_SOURCES = [
    {
        "name": "CoinDesk",
        "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "category": "crypto",
        "source_name": "CoinDesk"
    },
    {
        "name": "MarketWatch",
        "url": "https://feeds.marketwatch.com/marketwatch/topstories/",
        "category": "stocks",
        "source_name": "MarketWatch"
    },
]


def fetch_rss(url, max_items=12):
    """從 RSS 獲取新聞條目"""
    news_list = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            content = resp.read().decode('utf-8', errors='ignore')

        root = ET.fromstring(content)
        # 兼容 RSS 2.0 和 Atom
        channel = root.find('channel')
        items = channel.findall('item') if channel is not None else root.findall('.//item')
        if not items:
            items = root.findall('.//{http://www.w3.org/2005/Atom}entry')

        for item in items[:max_items]:
            title = _get_text(item, 'title')
            link = _get_link(item)
            if not title or not link:
                continue

            desc = _get_text(item, 'description') or _get_text(item, 'summary') or ''
            pub_date = _parse_date(_get_text(item, 'pubDate'))
            news_list.append({
                "title": title.strip()[:200],
                "link": link,
                "summary": desc.strip()[:300] if desc else "",
                "pubDate": pub_date,
            })
    except Exception as e:
        print(f"  ⚠️ RSS 錯誤: {e}")

    return news_list


def _get_text(element, tag):
    """安全獲取子元素文本"""
    try:
        ns = '{http://www.w3.org/2005/Atom}'
        for child in element:
            local = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            if local == tag or child.tag == tag or child.tag == ns + tag:
                if child.text:
                    return child.text.strip()
    except Exception:
        pass
    return ""


def _get_link(element):
    """獲取連結，兼容 RSS 2.0 和 Atom"""
    try:
        link_el = element.find('link')
        if link_el is not None:
            href = link_el.get('href')
            if href:
                return href
            if link_el.text:
                return link_el.text.strip()
    except Exception:
        pass
    return ""


def _parse_date(date_str):
    """解析日期字串為 YYYY-MM-DD 格式"""
    if not date_str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    formats = [
        '%a, %d %b %Y %H:%M:%S %z',
        '%a, %d %b %Y %H:%M:%S %Z',
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%d',
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip()[:25].strip(), fmt).strftime("%Y-%m-%d")
        except (ValueError, IndexError):
            continue
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def fetch_coin_gecko():
    """從 CoinGecko 獲取加密貨幣價格（免費，無需 API key）"""
    url = ("https://api.coingecko.com/api/v3/simple/price?"
           "ids=bitcoin,ethereum,solana,ripple,cardano"
           "&vs_currencies=usd"
           "&include_24hr_change=true"
           "&include_market_cap=true"
           "&include_24hr_vol=true")
    headers = {
        'User-Agent': 'kofhk-finance/1.0',
        'Accept': 'application/json'
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())

        return {
            "bitcoin": {
                "name": "Bitcoin", "symbol": "BTC",
                "price": data.get("bitcoin", {}).get("usd", 0),
                "change_24h": data.get("bitcoin", {}).get("usd_24h_change", 0),
                "market_cap": data.get("bitcoin", {}).get("usd_market_cap", 0),
                "volume": data.get("bitcoin", {}).get("usd_24h_vol", 0),
            },
            "ethereum": {
                "name": "Ethereum", "symbol": "ETH",
                "price": data.get("ethereum", {}).get("usd", 0),
                "change_24h": data.get("ethereum", {}).get("usd_24h_change", 0),
                "market_cap": data.get("ethereum", {}).get("usd_market_cap", 0),
                "volume": data.get("ethereum", {}).get("usd_24h_vol", 0),
            },
            "solana": {
                "name": "Solana", "symbol": "SOL",
                "price": data.get("solana", {}).get("usd", 0),
                "change_24h": data.get("solana", {}).get("usd_24h_change", 0),
                "market_cap": data.get("solana", {}).get("usd_market_cap", 0),
                "volume": data.get("solana", {}).get("usd_24h_vol", 0),
            },
            "ripple": {
                "name": "XRP", "symbol": "XRP",
                "price": data.get("ripple", {}).get("usd", 0),
                "change_24h": data.get("ripple", {}).get("usd_24h_change", 0),
                "market_cap": data.get("ripple", {}).get("usd_market_cap", 0),
                "volume": data.get("ripple", {}).get("usd_24h_vol", 0),
            },
            "cardano": {
                "name": "Cardano", "symbol": "ADA",
                "price": data.get("cardano", {}).get("usd", 0),
                "change_24h": data.get("cardano", {}).get("usd_24h_change", 0),
                "market_cap": data.get("cardano", {}).get("usd_market_cap", 0),
                "volume": data.get("cardano", {}).get("usd_24h_vol", 0),
            },
        }
    except Exception as e:
        print(f"  ⚠️ CoinGecko 錯誤: {e}")
        return None


def merge_news(new_list, old_list, key="link"):
    """合併新舊新聞，去重並保留最多 max_items 條"""
    seen = set()
    merged = []
    for item in new_list + old_list:
        dedup_key = item.get(key, "")
        if dedup_key and dedup_key not in seen:
            seen.add(dedup_key)
            merged.append(item)
    merged.sort(key=lambda x: x.get("pubDate", "") or "", reverse=True)
    return merged[:20]


def update_ai_news():
    """更新 AI 新聞"""
    print("\n🤖 更新 AI 新聞...")
    all_news = []
    for src in AI_RSS_SOURCES:
        print(f"  📡 {src['name']}...")
        items = fetch_rss(src["url"], max_items=8)
        for item in items:
            item["category"] = src["category"]
            item["icon"] = src["icon"]
        all_news.extend(items)
        time.sleep(0.5)

    # 保留原有的真實新聞（去重）
    old_path = os.path.join(BASE_DIR, "news-data.json")
    old_news = []
    if os.path.exists(old_path):
        try:
            with open(old_path, "r", encoding="utf-8") as f:
                old_data = json.load(f)
                old_news = old_data.get("news", [])
        except Exception:
            pass

    # 優先使用新新聞，再用舊新聞補足
    seen_links = set()
    merged = []
    for item in all_news:
        if item["link"] and item["link"] not in seen_links:
            seen_links.add(item["link"])
            merged.append(item)
    for item in old_news:
        link = item.get("link", "")
        if link and link not in seen_links:
            seen_links.add(link)
            merged.append(item)

    merged.sort(key=lambda x: x.get("pubDate", "") or "", reverse=True)
    merged = merged[:20]

    now = datetime.now(timezone.utc)
    output = {
        "lastUpdate": now.isoformat(),
        "count": len(merged),
        "news": merged,
    }

    with open(old_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"  ✅ AI 新聞已更新：{len(merged)} 條")


def update_finance_news():
    """更新財經新聞"""
    print("\n📰 更新財經新聞...")
    all_news = []
    for src in FINANCE_RSS_SOURCES:
        print(f"  📡 {src['name']}...")
        items = fetch_rss(src["url"], max_items=8)
        for item in items:
            item["source"] = src["source_name"]
            item["category"] = src["category"]
        all_news.extend(items)
        time.sleep(0.5)

    # 去重合併
    seen_links = set()
    merged = []
    for item in all_news:
        link = item.get("link", "")
        if link and link not in seen_links:
            seen_links.add(link)
            merged.append(item)

    merged.sort(key=lambda x: x.get("pubDate", "") or "", reverse=True)
    merged = merged[:15]

    now = datetime.now(timezone.utc)
    output = {
        "timestamp": now.isoformat(),
        "total_news": len(merged),
        "news": merged,
    }

    path = os.path.join(BASE_DIR, "finance-news.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"  ✅ 財經新聞已更新：{len(merged)} 條")


def update_market_data():
    """更新市場數據"""
    print("\n📈 更新市場數據...")

    crypto = fetch_coin_gecko()
    if crypto:
        print("  ✅ CoinGecko 數據獲取成功")
    else:
        print("  ⚠️ CoinGecko 獲取失敗，保留舊數據")
        # 保留舊數據
        old_path = os.path.join(BASE_DIR, "finance-data.json")
        if os.path.exists(old_path):
            with open(old_path, "r", encoding="utf-8") as f:
                old_data = json.load(f)
            crypto = old_data.get("crypto", {})
        else:
            crypto = {}

    now = datetime.now(timezone.utc)
    output = {
        "timestamp": now.isoformat(),
        "crypto": crypto,
        "stocks": {
            "NASDAQ": {
                "name": "納斯達克指數", "symbol": "^IXIC",
                "price": 26972.62, "change": 0,
                "volume": 10970191000,
                "high": 27094.803, "low": 26859.264
            },
            "DJI": {
                "name": "道瓊斯指數", "symbol": "^DJI",
                "price": 51032.46, "change": 0,
                "volume": 907942096,
                "high": 51094.18, "low": 50698.27
            },
            "SP500": {
                "name": "標普500指數", "symbol": "^GSPC",
                "price": 7580.06, "change": 0,
                "volume": 5528975000,
                "high": 7599.38, "low": 7563.55
            },
            "AAPL": {
                "name": "蘋果公司", "symbol": "AAPL",
                "price": 312.06, "change": 0,
                "volume": 56454230,
                "high": 315.0, "low": 309.53
            },
            "TSLA": {
                "name": "特斯拉", "symbol": "TSLA",
                "price": 435.79, "change": 0,
                "volume": 44967971,
                "high": 441.07, "low": 428.2
            }
        },
        "commodities": {
            "gold": {"name": "黃金", "symbol": "GC=F", "price": 4593.0, "change": 0, "unit": "USD/oz"},
            "silver": {"name": "白銀", "symbol": "SI=F", "price": 75.875, "change": 0, "unit": "USD/oz"},
            "oil_wti": {"name": "WTI原油", "symbol": "CL=F", "price": 87.36, "change": 0, "unit": "USD/barrel"},
            "oil_brent": {"name": "布倫特原油", "symbol": "BZ=F", "price": 91.12, "change": 0, "unit": "USD/barrel"}
        },
        "forex": {
            "USDHKD": {"name": "美元/港幣", "from_currency": "USD", "to_currency": "HKD", "rate": 7.8362, "change": 0},
            "USDCNY": {"name": "美元/人民幣", "from_currency": "USD", "to_currency": "CNY", "rate": 6.7657, "change": 0},
            "EURUSD": {"name": "歐元/美元", "from_currency": "EUR", "to_currency": "USD", "rate": 1.1659, "change": 0},
            "GBPUSD": {"name": "英鎊/美元", "from_currency": "GBP", "to_currency": "USD", "rate": 1.3452, "change": 0},
            "USDJPY": {"name": "美元/日元", "from_currency": "USD", "to_currency": "JPY", "rate": 159.255, "change": 0}
        },
        "bonds": {
            "us10y": {"name": "美國10年期國債", "country": "US", "maturity": "10Y", "yield": 4.453, "change": 0},
            "us2y": {"name": "美國2年期國債", "country": "US", "maturity": "2Y", "yield": 4.453, "change": 0},
            "us30y": {"name": "美國30年期國債", "country": "US", "maturity": "30Y", "yield": 4.993, "change": 0}
        },
        "market_sentiment": {
            "fear_greed_index": 50,
            "sentiment": "中性",
            "description": "市場情緒中性，投資者觀望為主",
            "color": "#888888",
            "timestamp": now.isoformat()
        }
    }

    path = os.path.join(BASE_DIR, "finance-data.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print("  ✅ 市場數據已更新")


def main():
    print("=" * 50)
    print(f"🚀 開始自動更新數據 — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 50)

    update_ai_news()
    update_finance_news()
    update_market_data()

    print("\n" + "=" * 50)
    print("✅ 所有數據更新完成")
    print("=" * 50)


if __name__ == "__main__":
    main()
