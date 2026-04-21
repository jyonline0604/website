#!/usr/bin/env python3
"""
獲取真實AI新聞資訊
使用真實RSS來源獲取最新新聞，移除虛構的fallback邏輯
"""

import os
import sys
import json
import time
from datetime import datetime
import urllib.request
import xml.etree.ElementTree as ET

WORKSPACE = "/home/openclaw/.openclaw/workspace"

# 真实可用的RSS来源
RSS_SOURCES = [
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "keywords": ["AI", "artificial intelligence", "OpenAI", "Google", "Microsoft", "GPT", "Claude", "Gemini", "Meta", "NVIDIA"],
        "category": "industry"
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/feed/",
        "keywords": ["AI", "artificial intelligence", "machine learning", "deep learning"],
        "category": "research"
    }
]

def fetch_rss_news(source_config):
    """從RSS獲取新聞"""
    news_list = []
    try:
        url = source_config["url"]
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*'
        }
        
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read().decode('utf-8', errors='ignore')
        
        root = ET.fromstring(content)
        items = root.findall('.//item')
        
        for item in items[:10]:
            try:
                title_elem = item.find('title')
                link_elem = item.find('link')
                desc_elem = item.find('description') or item.find('summary')
                date_elem = item.find('pubDate') or item.find('published')
                
                if title_elem is not None and title_elem.text:
                    title = title_elem.text.strip()
                else:
                    continue
                    
                if link_elem is not None:
                    link = link_elem.text.strip() if link_elem.text else ''
                    if not link:
                        link_elem_href = item.find('link[@href]')
                        if link_elem_href is not None:
                            link = link_elem_href.get('href', '')
                else:
                    continue
                    
                description = ""
                if desc_elem is not None and desc_elem.text:
                    description = desc_elem.text.strip()[:300]
                    
                pub_date = ""
                if date_elem is not None and date_elem.text:
                    try:
                        pub_date = datetime.strptime(date_elem.text.strip()[:16], '%a, %d %b %Y %H:%M').strftime('%Y-%m-%d')
                    except:
                        pub_date = datetime.now().strftime("%Y-%m-%d")
                else:
                    pub_date = datetime.now().strftime("%Y-%m-%d")
                
                news_list.append({
                    "title": title,
                    "link": link,
                    "description": description,
                    "pubDate": pub_date,
                    "category": source_config["category"],
                    "icon": "🤖" if source_config["category"] == "industry" else "🔬"
                })
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"   ⚠️ {source_config['name']}: {str(e)[:60]}")
    
    return news_list

def get_ai_news():
    """獲取AI新聞"""
    all_news = []
    seen_titles = set()
    
    print("📡 正在獲取真實AI新聞...")
    
    for source in RSS_SOURCES:
        print(f"   🔗 {source['name']}...")
        news = fetch_rss_news(source)
        
        for n in news:
            title_key = n["title"].lower().strip()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                all_news.append(n)
        
        time.sleep(0.5)
    
    # 按日期排序
    all_news.sort(key=lambda x: x.get("pubDate", ""), reverse=True)
    all_news = all_news[:20]
    
    return all_news

def main():
    print("🚀 開始獲取真實AI新聞...")
    
    news_list = get_ai_news()
    
    print(f"\n📊 新聞統計: {len(news_list)} 條")
    
    if len(news_list) == 0:
        print("❌ 無法獲取新聞，請檢查網絡連接")
        # 創建一個提示消息而不是虛構新聞
        news_data = {
            "lastUpdate": datetime.now().isoformat(),
            "count": 0,
            "news": [{
                "title": "新聞服務暫時不可用",
                "link": "https://kofhk.com/news.html",
                "description": "我們正在努力恢復新聞服務。請稍後再試。",
                "pubDate": datetime.now().strftime("%Y-%m-%d"),
                "category": "industry",
                "icon": "📰"
            }]
        }
    else:
        news_data = {
            "lastUpdate": datetime.now().isoformat(),
            "count": len(news_list),
            "news": news_list
        }
    
    json_path = os.path.join(WORKSPACE, "news-data.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 新聞已保存: {json_path}")
    print(f"   更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n📰 最新新聞示例:")
    for i, news in enumerate(news_list[:5], 1):
        print(f"   {i}. {news['title'][:60]}...")

if __name__ == "__main__":
    main()
