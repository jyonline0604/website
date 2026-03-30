#!/usr/bin/env python3
"""
增強版新聞獲取測試
確保每項新聞都能獲取3條
"""

import feedparser
import re

def fetch_enhanced_news(category, num_items=3):
    """增強版新聞獲取"""
    print(f"\n=== 獲取 {category} 新聞（目標: {num_items}條）===")
    
    category_map = {
        "entertainment": "娛樂",
        "tech": "科技", 
        "finance": "財經"
    }
    
    chinese_category = category_map.get(category, category)
    
    # 嘗試多個搜索詞
    search_queries = [
        f"{chinese_category}+香港",
        f"{chinese_category}",
        "香港"
    ]
    
    all_news = []
    
    for query in search_queries:
        if len(all_news) >= num_items:
            break
            
        try:
            url = f"https://news.google.com/rss/search?q={query}&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
            feed = feedparser.parse(url)
            
            print(f"  搜索詞: {query}, 找到條目: {len(feed.entries)}")
            
            for entry in feed.entries:
                if len(all_news) >= num_items:
                    break
                    
                title = entry.get("title", "")
                
                if title:
                    # 清理標題
                    clean_title = re.sub(r' - [^-]+$', '', title)
                    clean_title = re.sub(r'\s*-\s*[^-]+$', '', clean_title)
                    clean_title = clean_title.strip()
                    
                    # 過濾條件
                    if (len(clean_title) > 10 and
                        not clean_title.startswith('http') and
                        any(char in clean_title for char in ['的', '是', '在', '有', '了', '，', '。']) and
                        clean_title not in all_news):
                        
                        all_news.append(clean_title)
                        print(f"    ✓ {clean_title[:50]}...")
                        
        except Exception as e:
            print(f"    ✗ 搜索詞 {query} 異常: {str(e)}")
            continue
    
    # 如果還不夠，使用備用新聞
    if len(all_news) < num_items:
        print(f"  新聞不足，使用備用新聞補足")
        
        backup_news = {
            "entertainment": [
                "香港娛樂新聞持續更新",
                "影視作品最新動態", 
                "藝人活動消息",
                "演唱會門票熱賣",
                "電影票房最新排名"
            ],
            "tech": [
                "香港科技發展新動向",
                "創新科技應用消息",
                "數碼轉型最新趨勢",
                "人工智能技術突破",
                "智慧城市建設進展"
            ],
            "finance": [
                "香港股市最新動態",
                "財經市場消息更新",
                "經濟數據公布",
                "金融政策調整",
                "投資市場分析"
            ]
        }
        
        backup = backup_news.get(category, [f"{chinese_category}新聞{i+1}" for i in range(5)])
        
        for item in backup:
            if len(all_news) >= num_items:
                break
            if item not in all_news:
                all_news.append(item)
                print(f"    📝 備用: {item}")
    
    print(f"  最終獲取: {len(all_news)}條")
    return all_news[:num_items]

# 測試所有類別
print("=== 增強版新聞獲取測試 ===")
print(f"當前時間: 2026-03-28 18:30")

categories = ["entertainment", "tech", "finance"]

for category in categories:
    news = fetch_enhanced_news(category, 3)
    
    print(f"\n{category} 新聞結果:")
    for i, item in enumerate(news, 1):
        print(f"  {i}. {item}")
    
    print("-" * 60)

print("\n=== 測試完成 ===")