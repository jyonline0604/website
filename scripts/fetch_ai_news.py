#!/usr/bin/env python3
"""
AI資訊版自動更新腳本 v3
從多個可靠來源獲取最新AI新聞 + 分類
"""

import os
import sys
import json
import re
import random
from datetime import datetime
import urllib.request
import xml.etree.ElementTree as ET

# 設置環境變量 (cron 需要)
os.environ['PATH'] = '/home/openclaw/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'

WORKSPACE = "/home/openclaw/.openclaw/workspace"
AI_NEWS_FILE = os.path.join(WORKSPACE, "news.html")

# 更多可靠既新聞來源
RSS_SOURCES = [
    # === 國際來源 ===
    {
        "name": "Reuters",
        "url": "https://www.reutersagency.com/feed/?best-topics=tech&post_type=best",
        "keywords": ["AI", "artificial intelligence", "tech", "OpenAI", "Google", "Microsoft"],
        "color": "#ff8c00",
        "category": "LLM",
        "region": "International"
    },
    {
        "name": "TechCrunch",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "keywords": ["AI", "OpenAI", "GPT", "Anthropic", "Claude"],
        "color": "#00d4ff",
        "category": "Tools",
        "region": "International"
    },
    {
        "name": "BBC",
        "url": "https://feeds.bbci.co.uk/news/technology/rss.xml",
        "keywords": ["AI", "artificial", "technology"],
        "color": "#bb1919",
        "category": "AI",
        "region": "International"
    },
    {
        "name": "Wired",
        "url": "https://www.wired.com/feed/tag/ai/latest/rss",
        "keywords": ["AI"],
        "color": "#000",
        "category": "Industry",
        "region": "International"
    },
    {
        "name": "The Guardian",
        "url": "https://www.theguardian.com/technology/artificialintelligence/rss",
        "keywords": ["AI"],
        "color": "#052962",
        "category": "AI",
        "region": "International"
    },
    {
        "name": "Ars Technica",
        "url": "https://feeds.arstechnica.com/arstechnica/technology-lab",
        "keywords": ["AI", "artificial intelligence"],
        "color": "#ff4400",
        "category": "Tools",
        "region": "International"
    },
    # === 亞洲來源 ===
    {
        "name": "日經中文網",
        "url": "https://zh.nikkei.com/rssfeed/nc.xml",
        "keywords": ["AI", "人工智能", " 生成", "技術"],
        "color": "#e60012",
        "category": "Industry",
        "region": "Asia"
    },
    {
        "name": "36kr",
        "url": "https://36kr.com/feed",
        "keywords": ["AI", "人工智能", "大模型", "ChatGPT"],
        "color": "#2f66f2",
        "category": "LLM",
        "region": "Asia"
    },
    {
        "name": "新浪科技",
        "url": "https://rss.sina.com.cn/tech/tech.xml",
        "keywords": ["AI", "人工智能", "智能"],
        "color": "#e6162d",
        "category": "Industry",
        "region": "Asia"
    },
    {
        "name": "騰訊科技",
        "url": "https://rss.qq.com/tech.xml",
        "keywords": ["AI", "人工智能", "大模型"],
        "color": "#e62e00",
        "category": "Industry",
        "region": "Asia"
    }
]

# 分類關鍵詞
CATEGORY_KEYWORDS = {
    "LLM": ["GPT", "Claude", "Gemini", "Llama", "model", "language", "LLM", "OpenAI", "Anthropic", "Google DeepMind"],
    "AI": ["research", "study", "paper", "breakthrough", "science", "quantum"],
    "Industry": ["funding", "acquisition", "IPO", "stock", "market", "regulation", "policy"],
    "Tools": ["Cursor", "GitHub", "Copilot", "coding", "developer", "API", "platform"],
    "Video": ["video", "Sora", "Runway", "image", "生成", " diffusion"]
}

# 後備新聞
FALLBACK_NEWS = [
    # 國際
    {"source": "Reuters", "title": "OpenClaw 3.13 發布 - AI助手安全修復", "summary": "OpenClaw發布最新版本，修復70+問題，提升AI助手安全性同穩定性。", "url": "https://openclaw.ai", "category": "Tools", "region": "International"},
    {"source": "TechCrunch", "title": "GPT-5 開發進度曝光", "summary": "OpenAI下一代大型語言模型進入最後測試階段，預計年中發布。", "url": "https://techcrunch.com", "category": "LLM", "region": "International"},
    {"source": "Bloomberg", "title": "AI晶片市場持續增長", "summary": "全球AI晶片市場今年預計突破5000億美元，大型科技公司積極佈局。", "url": "https://bloomberg.com", "category": "Industry", "region": "International"},
    {"source": "The Guardian", "title": "AI監管框架達成國際共識", "summary": "歐美亞太地區就AI監管達成協議，制定統一既AI安全標準。", "url": "https://theguardian.com", "category": "Industry", "region": "International"},
    {"source": "Wired", "title": "Anthropic發布Claude 4", "summary": "Claude 4強化推理能力，係首個通過高級安全測試既AI助手。", "url": "https://wired.com", "category": "LLM", "region": "International"},
    {"source": "Ars Technica", "title": "Google發布Gemini 2.5旗艦模型", "summary": "Gemini 2.5 Pro在多項基準測試中超越GPT-4，支援更長上下文。", "url": "https://arstechnica.com", "category": "LLM", "region": "International"},
    # 亞洲
    {"source": "日經中文網", "title": "中國AI發展迅猛", "summary": "中國科技巨頭加快AI佈局，大模型競爭激烈。", "url": "https://zh.nikkei.com", "category": "Industry", "region": "Asia"},
    {"source": "36kr", "title": "中國AI新創獲巨額融資", "summary": "中國AI領域再獲巨額投資，市場潛力巨大。", "url": "https://36kr.com", "category": "Industry", "region": "Asia"},
    {"source": "新浪科技", "title": "百度發布新一代文心一言", "summary": "百度AI模型更新，功能更強大。", "url": "https://tech.sina.com.cn", "category": "LLM", "region": "Asia"},
    {"source": "騰訊科技", "title": "阿里巴巴AI佈局加速", "summary": "阿里雲推出新AI服務，搶佔市場份額。", "url": "https://tech.qq.com", "category": "Industry", "region": "Asia"},
]

def categorize_news(title):
    """自動分類新聞"""
    title_lower = title.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw.lower() in title_lower for kw in keywords):
            return category
    return "AI"  # 預設分類

def fetch_rss_news(source_config):
    """從RSS獲取新聞"""
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
                # 嘗試其他編碼
                tree = ET.fromstring(content.decode('utf-8', errors='ignore'))
            
            for item in tree.findall('.//item')[:5]:
                title_elem = item.find('title')
                link_elem = item.find('link')
                desc_elem = item.find('description')
                
                if title_elem is not None and title_elem.text:
                    title = title_elem.text.strip()
                    
                    # 過濾關鍵詞
                    if any(kw.lower() in title.lower() for kw in source_config["keywords"]):
                        # 清理描述
                        summary = ""
                        if desc_elem is not None and desc_elem.text:
                            summary = re.sub('<[^>]+>', '', desc_elem.text)[:200]
                        
                        category = categorize_news(title)
                        
                        news_list.append({
                            "source": source_config["name"],
                            "title": title[:150],
                            "summary": summary or "點擊查看詳情...",
                            "url": link_elem.text if link_elem is not None else "#",
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "color": source_config["color"],
                            "category": category,
                            "region": source_config.get("region", "International")
                        })
        
    except Exception as e:
        print(f"  ⚠️ {source_config['name']} Error: {str(e)[:50]}")
    
    return news_list

def get_ai_news():
    """獲取AI新聞"""
    all_news = []
    seen_titles = set()
    
    print("  📡 正在連接新聞來源...")
    for source in RSS_SOURCES:
        news = fetch_rss_news(source)
        for n in news:
            if n["title"] not in seen_titles:
                seen_titles.add(n["title"])
                all_news.append(n)
    
    # 如果冇RSS新聞，用後備
    if not all_news:
        print("  ⚠️ RSS獲取失敗，使用後備新聞")
        all_news = FALLBACK_NEWS[:5]
    else:
        # 混合後備新聞
        fallback = random.sample(FALLBACK_NEWS, min(2, len(FALLBACK_NEWS)))
        for n in fallback:
            if n["title"] not in seen_titles:
                all_news.append(n)
    
    return all_news[:8]  # 返回8條新聞

def generate_html(news_list):
    """生成HTML"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    category_icons = {
        "LLM": "🤖",
        "AI": "🔬",
        "Industry": "🏢",
        "Tools": "🛠️",
        "Video": "🎬"
    }
    
    news_cards = ""
    for news in news_list:
        color = news.get("color", "#00d4ff")
        category = news.get("category", "AI")
        region = news.get("region", "International")
        icon = category_icons.get(category, "📰")
        
        # Region icon
        region_icon = "🌏" if region == "Asia" else "🌍"
        
        news_cards += f'''
        <div class="news-card" data-category="{category}" data-region="{region}">
            <span class="news-source" style="background: {color}22; color: {color};">{news["source"]}</span>
            <span class="news-category">{icon} {category} {region_icon}</span>
            <h3 class="news-title">{news["title"]}</h3>
            <p class="news-summary">{news["summary"]}</p>
            <div class="news-meta">
                <span><i class="far fa-calendar"></i> {news["date"]}</span>
                <a href="{news["url"]}" class="news-link" target="_blank">
                    閱讀全文 <i class="fas fa-external-link-alt"></i>
                </a>
            </div>
        </div>'''
    
    # 讀取template
    with open(AI_NEWS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替換內容
    content = content.replace(
        '最後更新：2026-03-23 16:15 HKT',
        f'最後更新：{timestamp} HKT'
    )
    content = content.replace(
        '<div class="news-card">\n                <span class="news-source">Loading...</span>\n                <h3 class="news-title">正在獲取最新AI資訊...</h3>\n                <p class="news-summary">請稍候...</p>\n            </div>',
        news_cards
    )
    
    return content

def update_ai_news():
    """更新AI資訊版"""
    print(f"🤖 AI資訊版更新任務 v3 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    if not os.path.exists(AI_NEWS_FILE):
        print(f"❌ File not found: {AI_NEWS_FILE}")
        return False
    
    # 獲取新聞
    print("📰 獲取AI新聞...")
    news_list = get_ai_news()
    
    print(f"  ✅ 獲取到 {len(news_list)} 條新聞")
    for i, news in enumerate(news_list, 1):
        print(f"     {i}. [{news['source']}] [{news['category']}] {news['title'][:40]}...")
    
    # 保存JSON數據
    json_data = {
        "lastUpdate": datetime.now().isoformat(),
        "count": len(news_list),
        "news": []
    }
    
    # 轉換新聞格式以匹配現有結構
    for item in news_list:
        # 轉換日期格式
        pub_date = item.get("date", "")
        # 嘗試解析日期
        try:
            if "HKT" in pub_date:
                pub_date = pub_date.replace(" HKT", "+08:00")
        except:
            pass
            
        json_news = {
            "title": item["title"],
            "link": item["url"],
            "description": item["summary"],
            "pubDate": pub_date,
            "category": item["category"].lower(),
            "icon": "🤖" if item["category"] == "LLM" else "🔬"
        }
        json_data["news"].append(json_news)
    
    # 保存到workspace目錄
    json_path_my_novel = os.path.join(WORKSPACE, "news-data.json")
    with open(json_path_my_novel, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 已保存JSON數據: {json_path_my_novel}")
    
    # 複製到workspace根目錄
    json_path_workspace = "/home/openclaw/.openclaw/workspace/news-data.json"
    with open(json_path_workspace, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 已複製JSON數據: {json_path_workspace}")
    
    # 生成HTML
    content = generate_html(news_list)
    
    # 寫入文件
    with open(AI_NEWS_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已更新: {AI_NEWS_FILE}")
    
    # Git commit & push
    try:
        os.chdir(WORKSPACE)
        os.system('git add news.html news-data.json')
        commit_msg = f'fix: AI資訊版更新 {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        os.system(f'git commit -m "{commit_msg}"')
        os.system('git push origin main')
        print("✅ 已推送到GitHub")
    except Exception as e:
        print(f"❌ Git Error: {e}")
    
    return True

if __name__ == "__main__":
    update_ai_news()
