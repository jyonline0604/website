#!/usr/bin/env python3
"""
財經新聞自動更新腳本 v2 (2026-04-21 最終版)
從多個可靠來源獲取最新財經 + 加密貨幣新聞
使用 Python 標準庫，唔需要額外模組
"""

import os
import sys
import json
import re
from datetime import datetime
import urllib.request
import xml.etree.ElementTree as ET

# 設置環境變量 (cron 需要)
os.environ['PATH'] = '/home/openclaw/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'

WORKSPACE = "/opt/data/website"
FINANCE_NEWS_FILE = os.path.join(WORKSPACE, "finance-news.json")

# 財經新聞來源 (2026-04-21 最終版 - 全部測試過有效)
RSS_SOURCES = [
    # === 國際財經媒體 ===
    {
        "name": "MarketWatch",
        "url": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
        "keywords": ["market", "stock", "business"],
        "category": "stocks",
        "icon": "📈"
    },
    {
        "name": "CoinDesk",
        "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "keywords": ["bitcoin", "crypto", "blockchain", "ethereum"],
        "category": "crypto",
        "icon": "₿"
    },
]

def fetch_rss_news(source_config):
    """從 RSS 獲取新聞"""
    news_list = []
    try:
        url = source_config["url"]
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read()
            # 處理編碼
            try:
                tree = ET.fromstring(content)
            except:
                tree = ET.fromstring(content.decode('utf-8', errors='ignore'))
            
            for item in tree.findall('.//item')[:10]:
                title_elem = item.find('title')
                link_elem = item.find('link')
                desc_elem = item.find('description')
                
                if title_elem is not None and title_elem.text:
                    title = title_elem.text.strip()
                    
                    # 放寬過濾：如果 keywords 為空則全部接受，否則檢查關鍵詞
                    source_keywords = source_config.get("keywords", [])
                    if not source_keywords or any(kw.lower() in title.lower() for kw in source_keywords):
                        summary = ""
                        if desc_elem is not None and desc_elem.text:
                            # 清理 HTML 標籤
                            clean_desc = re.sub('<[^>]+>', '', desc_elem.text)
                            summary = clean_desc[:200]
                        
                        news_list.append({
                            "title": title[:150],
                            "link": link_elem.text if link_elem is not None else "#",
                            "summary": summary or "",
                            "source": source_config["name"],
                            "category": source_config.get("category", "business"),
                            "timestamp": datetime.now().isoformat()
                        })
        
    except Exception as e:
        print(f"  ⚠️ {source_config['name']} Error: {str(e)[:50]}")
    
    return news_list

def get_all_finance_news():
    """獲取所有財經新聞"""
    all_news = []
    seen_titles = set()
    
    print("📡 正在連接財經新聞來源...")
    for source in RSS_SOURCES:
        news = fetch_rss_news(source)
        for n in news:
            # 去重
            title_key = n["title"].lower()[:50]
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                all_news.append(n)
    
    # 按時間排序（最新嘅在前）
    all_news.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    print(f"✅ 總共獲取到 {len(all_news)} 條財經新聞")
    return all_news[:25]  # 最多返回 25 條

def update_finance_news():
    """更新財經新聞數據"""
    print(f"📰 財經新聞更新任務 v2 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 獲取新聞
    news_list = get_all_finance_news()
    
    if not news_list:
        print("❌ 未能獲取到新聞")
        return False
    
    # 保存 JSON 數據
    json_data = {
        "timestamp": datetime.now().isoformat(),
        "total_news": len(news_list),
        "news": news_list
    }
    
    json_path = FINANCE_NEWS_FILE
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 已保存 JSON 數據: {json_path} ({len(news_list)} 條新聞)")
    
    # Git commit & push (只提交 JSON)
    try:
        os.chdir(WORKSPACE)
        os.system('git add finance-news.json')
        commit_msg = f'docs: update finance news {datetime.now().strftime("%Y-%m-%d %H:%M")} ({len(news_list)}條)'
        os.system(f'git commit -m "{commit_msg}"')
        # Pull first to avoid rejection
        os.system('git pull origin main --rebase')
        os.system('git push origin main')
        print("✅ 已推送到 GitHub")
    except Exception as e:
        print(f"❌ Git Error: {e}")
    
    return True

if __name__ == "__main__":
    update_finance_news()
