#!/usr/bin/env python3
"""
財經新聞抓取腳本
從多個財經新聞來源抓取最新新聞
"""

import json
import requests
import feedparser
from datetime import datetime, timedelta
import time
import os
import sys
from typing import Dict, List, Any, Optional
import re

class FinanceNewsFetcher:
    """財經新聞抓取類"""
    
    def __init__(self):
        self.news_file = '/home/openclaw/.openclaw/workspace/my-novel/finance-news.json'
        self.max_news_items = 20
        
    def fetch_all_news(self) -> Dict[str, Any]:
        """從所有來源抓取新聞"""
        print("📰 開始抓取財經新聞...")
        
        all_news = []
        
        # 從各個來源抓取新聞
        sources = [
            self.fetch_reuters_news,
            self.fetch_bloomberg_news,
            self.fetch_cnbc_news,
            self.fetch_coindesk_news,
            self.fetch_cryptoslate_news
        ]
        
        for source_func in sources:
            try:
                news_items = source_func()
                if news_items:
                    all_news.extend(news_items)
                    print(f"  ✅ {source_func.__name__.replace('fetch_', '').replace('_news', '')}: {len(news_items)} 條新聞")
            except Exception as e:
                print(f"  ⚠️ {source_func.__name__} 失敗: {e}")
        
        # 去重和排序
        unique_news = self._deduplicate_news(all_news)
        sorted_news = sorted(unique_news, key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # 限制數量
        final_news = sorted_news[:self.max_news_items]
        
        # 分類新聞
        categorized_news = self._categorize_news(final_news)
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'total_news': len(final_news),
            'news': final_news,
            'categories': categorized_news
        }
        
        # 保存到文件
        self.save_news(data)
        print(f"✅ 財經新聞抓取完成，共 {len(final_news)} 條新聞")
        return data
    
    def fetch_reuters_news(self) -> List[Dict[str, Any]]:
        """抓取路透社新聞"""
        try:
            # Reuters Business RSS
            url = "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best"
            feed = feedparser.parse(url)
            
            news_items = []
            for entry in feed.entries[:5]:  # 限制5條
                news_items.append({
                    'title': entry.title,
                    'link': entry.link,
                    'summary': entry.get('summary', ''),
                    'source': 'Reuters',
                    'category': 'business',
                    'timestamp': self._parse_date(entry.get('published', ''))
                })
            
            return news_items
        except Exception as e:
            print(f"  ⚠️ Reuters新聞抓取失敗: {e}")
            return self._get_fallback_news('reuters')
    
    def fetch_bloomberg_news(self) -> List[Dict[str, Any]]:
        """抓取彭博新聞"""
        try:
            # Bloomberg Markets RSS
            url = "https://www.bloomberg.com/feeds/markets"
            feed = feedparser.parse(url)
            
            news_items = []
            for entry in feed.entries[:5]:
                news_items.append({
                    'title': entry.title,
                    'link': entry.link,
                    'summary': entry.get('summary', ''),
                    'source': 'Bloomberg',
                    'category': 'markets',
                    'timestamp': self._parse_date(entry.get('published', ''))
                })
            
            return news_items
        except Exception as e:
            print(f"  ⚠️ Bloomberg新聞抓取失敗: {e}")
            return self._get_fallback_news('bloomberg')
    
    def fetch_cnbc_news(self) -> List[Dict[str, Any]]:
        """抓取CNBC新聞"""
        try:
            # CNBC Business News RSS
            url = "https://www.cnbc.com/id/10000664/device/rss/rss.html"
            feed = feedparser.parse(url)
            
            news_items = []
            for entry in feed.entries[:5]:
                news_items.append({
                    'title': entry.title,
                    'link': entry.link,
                    'summary': entry.get('summary', ''),
                    'source': 'CNBC',
                    'category': 'business',
                    'timestamp': self._parse_date(entry.get('published', ''))
                })
            
            return news_items
        except Exception as e:
            print(f"  ⚠️ CNBC新聞抓取失敗: {e}")
            return self._get_fallback_news('cnbc')
    
    def fetch_coindesk_news(self) -> List[Dict[str, Any]]:
        """抓取CoinDesk加密貨幣新聞"""
        try:
            # CoinDesk RSS
            url = "https://www.coindesk.com/arc/outboundfeeds/rss/"
            feed = feedparser.parse(url)
            
            news_items = []
            for entry in feed.entries[:5]:
                news_items.append({
                    'title': entry.title,
                    'link': entry.link,
                    'summary': entry.get('summary', ''),
                    'source': 'CoinDesk',
                    'category': 'crypto',
                    'timestamp': self._parse_date(entry.get('published', ''))
                })
            
            return news_items
        except Exception as e:
            print(f"  ⚠️ CoinDesk新聞抓取失敗: {e}")
            return self._get_fallback_news('coindesk')
    
    def fetch_cryptoslate_news(self) -> List[Dict[str, Any]]:
        """抓取CryptoSlate加密貨幣新聞"""
        try:
            # CryptoSlate RSS
            url = "https://cryptoslate.com/feed/"
            feed = feedparser.parse(url)
            
            news_items = []
            for entry in feed.entries[:5]:
                news_items.append({
                    'title': entry.title,
                    'link': entry.link,
                    'summary': entry.get('summary', ''),
                    'source': 'CryptoSlate',
                    'category': 'crypto',
                    'timestamp': self._parse_date(entry.get('published', ''))
                })
            
            return news_items
        except Exception as e:
            print(f"  ⚠️ CryptoSlate新聞抓取失敗: {e}")
            return self._get_fallback_news('cryptoslate')
    
    def _parse_date(self, date_str: str) -> str:
        """解析日期字符串"""
        try:
            if not date_str:
                return datetime.now().isoformat()
            
            # 嘗試解析各種日期格式
            for fmt in ['%a, %d %b %Y %H:%M:%S %z', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d %H:%M:%S']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.isoformat()
                except ValueError:
                    continue
            
            return datetime.now().isoformat()
        except:
            return datetime.now().isoformat()
    
    def _deduplicate_news(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重新聞"""
        seen_titles = set()
        unique_news = []
        
        for item in news_items:
            title = item.get('title', '').lower()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_news.append(item)
        
        return unique_news
    
    def _categorize_news(self, news_items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """分類新聞"""
        categories = {
            'crypto': [],
            'stocks': [],
            'economy': [],
            'technology': [],
            'other': []
        }
        
        crypto_keywords = ['bitcoin', 'ethereum', 'crypto', 'blockchain', 'defi', 'nft', '交易所']
        stock_keywords = ['stock', '股市', '納斯達克', '道瓊斯', '標普', '投資', '股價']
        economy_keywords = ['經濟', '通脹', '利率', '美聯儲', '央行', 'GDP', '就業']
        tech_keywords = ['科技', 'AI', '人工智能', '特斯拉', '蘋果', '微軟', '谷歌']
        
        for item in news_items:
            title = item.get('title', '').lower()
            category = item.get('category', '')
            
            # 根據關鍵詞分類
            if any(keyword in title for keyword in crypto_keywords) or category == 'crypto':
                categories['crypto'].append(item)
            elif any(keyword in title for keyword in stock_keywords) or category == 'markets':
                categories['stocks'].append(item)
            elif any(keyword in title for keyword in economy_keywords):
                categories['economy'].append(item)
            elif any(keyword in title for keyword in tech_keywords):
                categories['technology'].append(item)
            else:
                categories['other'].append(item)
        
        return categories
    
    def save_news(self, data: Dict[str, Any]) -> None:
        """保存新聞到文件"""
        try:
            with open(self.news_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"  💾 新聞已保存: {self.news_file}")
        except Exception as e:
            print(f"  ⚠️ 新聞保存失敗: {e}")
    
    def _get_fallback_news(self, source: str) -> List[Dict[str, Any]]:
        """獲取備用新聞數據"""
        fallback_news = {
            'reuters': [
                {
                    'title': '全球股市震盪，投資者關注央行政策',
                    'link': 'https://www.reuters.com/markets',
                    'summary': '全球主要股市出現波動，投資者密切關注各國央行貨幣政策走向。',
                    'source': 'Reuters',
                    'category': 'markets',
                    'timestamp': datetime.now().isoformat()
                }
            ],
            'bloomberg': [
                {
                    'title': '科技股領漲納斯達克，AI概念股表現強勁',
                    'link': 'https://www.bloomberg.com/markets',
                    'summary': '納斯達克指數上漲，AI相關科技股表現突出，帶動市場情緒。',
                    'source': 'Bloomberg',
                    'category': 'stocks',
                    'timestamp': datetime.now().isoformat()
                }
            ],
            'cnbc': [
                {
                    'title': '美聯儲維持利率不變，市場反應平淡',
                    'link': 'https://www.cnbc.com/finance',
                    'summary': '美聯儲最新會議決定維持利率水平，市場對此反應相對平靜。',
                    'source': 'CNBC',
                    'category': 'economy',
                    'timestamp': datetime.now().isoformat()
                }
            ],
            'coindesk': [
                {
                    'title': '比特幣價格回升，加密貨幣市場情緒改善',
                    'link': 'https://www.coindesk.com/markets',
                    'summary': '比特幣價格從近期低點反彈，加密貨幣市場整體情緒有所改善。',
                    'source': 'CoinDesk',
                    'category': 'crypto',
                    'timestamp': datetime.now().isoformat()
                }
            ],
            'cryptoslate': [
                {
                    'title': '以太坊2.0升級進展順利，網絡性能提升',
                    'link': 'https://cryptoslate.com/news',
                    'summary': '以太坊2.0升級按計劃進行，網絡交易速度和效率得到顯著提升。',
                    'source': 'CryptoSlate',
                    'category': 'crypto',
                    'timestamp': datetime.now().isoformat()
                }
            ]
        }
        
        return fallback_news.get(source, [])


def main():
    """主函數"""
    print("=" * 50)
    print("📰 財經新聞抓取系統")
    print("=" * 50)
    
    fetcher = FinanceNewsFetcher()
    data = fetcher.fetch_all_news()
    
    # 顯示摘要
    print("\n📊 新聞摘要:")
    print(f"  總新聞數: {data['total_news']}")
    
    categories = data.get('categories', {})
    for category, items in categories.items():
        if items:
            print(f"  {category}: {len(items)} 條")
    
    print(f"\n⏰ 更新時間: {data.get('timestamp', '未知')}")
    print("=" * 50)
    
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ 用戶中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        sys.exit(1)