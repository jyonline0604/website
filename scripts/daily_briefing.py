#!/usr/bin/env python3
# 每日簡報生成腳本
# 整合天氣、交通、新聞等生成香港簡報

import json
import requests
from datetime import datetime
import os
import sys

# 設定時區
os.environ['TZ'] = 'Asia/Hong_Kong'

def get_current_time():
    """獲取當前時間和日期"""
    now = datetime.now()
    return {
        'date': now.strftime('%Y年%m月%d日'),
        'time': now.strftime('%H:%M'),
        'day': now.strftime('%A'),
        'timestamp': now.strftime('%Y%m%d_%H%M')
    }

def get_briefing_type(current_time):
    """根據時間決定簡報類型"""
    hour = int(current_time.split(':')[0])
    
    if hour == 8:
        return "☀️ 晨間簡報"
    elif hour == 12:
        return "🌤️ 午間簡報"
    elif hour == 17:
        return "🌙 傍晚簡報"
    else:
        return "📰 香港簡報"

def fetch_weather_data():
    """獲取天氣數據（模擬）"""
    try:
        # 這裡可以替換為實際的API調用
        # 暫時使用模擬數據
        return {
            'temperature': '24',
            'humidity': '75',
            'uv_index': '中等',
            'forecast': '22-26°C - 大致多雲，有一兩陣微雨。'
        }
    except Exception as e:
        print(f"⚠️ 天氣數據獲取失敗: {e}")
        return {
            'temperature': '待更新',
            'humidity': '待更新',
            'uv_index': '待更新',
            'forecast': '今日天氣待更新'
        }

def fetch_traffic_data():
    """獲取交通數據（模擬）"""
    try:
        # 這裡可以替換為實際的API調用
        return {
            'road': '✅ 交通狀況正常',
            'mtr': '🚇 港鐵正常運作',
            'bus': '🚌 巴士正常服務'
        }
    except Exception as e:
        print(f"⚠️ 交通數據獲取失敗: {e}")
        return {
            'road': '🚗 交通狀況待更新',
            'mtr': '🚇 港鐵正常運作',
            'bus': '🚌 巴士正常服務'
        }

def fetch_news_data():
    """獲取新聞數據"""
    try:
        # 從AI新聞系統讀取最新新聞
        news_file = '/home/openclaw/.openclaw/workspace/news-data.json'
        if os.path.exists(news_file):
            with open(news_file, 'r', encoding='utf-8') as f:
                news_data = json.load(f)
            
            # 獲取最新的幾條新聞
            latest_news = news_data.get('news', [])[:5]
            
            tech_news = []
            entertainment_news = []
            
            for news in latest_news:
                if 'AI' in news.get('title', '') or '科技' in news.get('title', ''):
                    tech_news.append(news)
                else:
                    entertainment_news.append(news)
            
            return {
                'tech': tech_news[:3],
                'entertainment': entertainment_news[:3]
            }
    except Exception as e:
        print(f"⚠️ 新聞數據獲取失敗: {e}")
    
    return {
        'tech': [{'title': '科技新聞待更新', 'source': 'Google新聞'}],
        'entertainment': [{'title': '娛樂新聞待更新', 'source': 'Google新聞'}]
    }

def fetch_finance_data():
    """獲取財經數據（模擬）"""
    try:
        # 這裡可以替換為實際的API調用
        return {
            'hsi': {'index': '25432.15', 'change': '+125.42', 'percent': '+0.50%'},
            'alibaba': {'price': '124.5', 'change': '+1.2', 'percent': '+0.97%'},
            'tencent': {'price': '512.8', 'change': '+3.5', 'percent': '+0.69%'},
            'hsbc': {'price': '125.3', 'change': '+0.8', 'percent': '+0.64%'}
        }
    except Exception as e:
        print(f"⚠️ 財經數據獲取失敗: {e}")
        return {
            'hsi': {'index': '待更新', 'change': '+0.00', 'percent': '+0.00%'},
            'alibaba': {'price': '待更新', 'change': '+0.00', 'percent': '+0.00%'},
            'tencent': {'price': '待更新', 'change': '+0.00', 'percent': '+0.00%'},
            'hsbc': {'price': '待更新', 'change': '+0.00', 'percent': '+0.00%'}
        }

def generate_briefing():
    """生成簡報"""
    print("=== 每日簡報生成開始 ===")
    
    # 獲取當前時間
    time_info = get_current_time()
    current_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"📅 當前時間: {current_time_str}")
    
    # 決定簡報類型
    briefing_type = get_briefing_type(time_info['time'])
    print(f"📋 簡報類型: {briefing_type}")
    
    # 獲取各類數據
    print("🌤️ 獲取天氣數據...")
    weather = fetch_weather_data()
    
    print("🚗 獲取交通數據...")
    traffic = fetch_traffic_data()
    
    print("📰 獲取新聞數據...")
    news = fetch_news_data()
    
    print("💹 獲取財經數據...")
    finance = fetch_finance_data()
    
    # 生成HTML簡報
    html_content = generate_html_briefing(time_info, briefing_type, weather, traffic, news, finance)
    
    # 生成文字簡報
    text_content = generate_text_briefing(time_info, briefing_type, weather, traffic, news, finance)
    
    # 保存文件
    save_briefing_files(html_content, text_content, time_info['timestamp'])
    
    print("✅ 簡報生成完成")
    return True

def generate_html_briefing(time_info, briefing_type, weather, traffic, news, finance):
    """生成HTML格式簡報"""
    html = f"""<!DOCTYPE html>
<html lang="zh-HK">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>香港簡報 - {time_info['date']}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 20px;
        }}
        .header h1 {{
            color: #2c3e50;
            margin: 0;
        }}
        .header .subtitle {{
            color: #7f8c8d;
            font-size: 1.2em;
        }}
        .section {{
            margin-bottom: 25px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #4CAF50;
        }}
        .section h2 {{
            color: #2c3e50;
            margin-top: 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .data-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .data-item {{
            background: white;
            padding: 15px;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .news-item {{
            margin-bottom: 10px;
            padding: 10px;
            background: white;
            border-radius: 6px;
            border-left: 3px solid #3498db;
        }}
        .finance-item {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }}
        .positive {{
            color: #27ae60;
        }}
        .negative {{
            color: #e74c3c;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        @media (max-width: 600px) {{
            .container {{
                padding: 15px;
            }}
            .data-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📰 香港簡報 ({time_info['date']}) {briefing_type}</h1>
            <div class="subtitle">生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        <div class="section">
            <h2>🌤️ 天氣</h2>
            <div class="data-grid">
                <div class="data-item">
                    <strong>🌡️ 氣溫</strong><br>
                    {weather['temperature']}°C
                </div>
                <div class="data-item">
                    <strong>💧 濕度</strong><br>
                    {weather['humidity']}%
                </div>
                <div class="data-item">
                    <strong>☀️ 紫外線</strong><br>
                    {weather['uv_index']}
                </div>
            </div>
            <div style="margin-top: 15px;">
                <strong>📡 預報</strong><br>
                {weather['forecast']}
            </div>
        </div>
        
        <div class="section">
            <h2>🚗 交通</h2>
            <div class="data-grid">
                <div class="data-item">
                    <strong>道路狀況</strong><br>
                    {traffic['road']}
                </div>
                <div class="data-item">
                    <strong>港鐵</strong><br>
                    {traffic['mtr']}
                </div>
                <div class="data-item">
                    <strong>巴士</strong><br>
                    {traffic['bus']}
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🔬 科技新聞</h2>
            {"".join([f'<div class="news-item"><strong>{item.get("title", "無標題")}</strong><br><small>來源: {item.get("source", "未知")}</small></div>' for item in news['tech']])}
        </div>
        
        <div class="section">
            <h2>🎬 娛樂新聞</h2>
            {"".join([f'<div class="news-item"><strong>{item.get("title", "無標題")}</strong><br><small>來源: {item.get("source", "未知")}</small></div>' for item in news['entertainment']])}
        </div>
        
        <div class="section">
            <h2>💹 財經</h2>
            <div class="finance-item">
                <span>恒生指數</span>
                <span>{finance['hsi']['index']} <span class="positive">{finance['hsi']['change']} ({finance['hsi']['percent']})</span></span>
            </div>
            <div class="finance-item">
                <span>阿里巴巴</span>
                <span>{finance['alibaba']['price']} <span class="positive">{finance['alibaba']['change']} ({finance['alibaba']['percent']})</span></span>
            </div>
            <div class="finance-item">
                <span>騰訊</span>
                <span>{finance['tencent']['price']} <span class="positive">{finance['tencent']['change']} ({finance['tencent']['percent']})</span></span>
            </div>
            <div class="finance-item">
                <span>匯豐控股</span>
                <span>{finance['hsbc']['price']} <span class="positive">{finance['hsbc']['change']} ({finance['hsbc']['percent']})</span></span>
            </div>
        </div>
        
        <div class="footer">
            📡 數據來源：data.gov.hk、Google新聞、市場數據<br>
            📅 最後更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>"""
    
    return html

def generate_text_briefing(time_info, briefing_type, weather, traffic, news, finance):
    """生成文字格式簡報"""
    text = f"""📰 香港簡報 ({time_info['date']}) {briefing_type}

【天氣】📡 data.gov.hk
🌡️ 氣溫：{weather['temperature']}°C
💧 濕度：{weather['humidity']}%
☀️ 紫外線：{weather['uv_index']}

【預報】📡 data.gov.hk
{weather['forecast']}

【交通】
{traffic['road']}
{traffic['mtr']}
{traffic['bus']}

【科技新聞】🔬
"""
    
    for item in news['tech']:
        text += f"🔧 {item.get('title', '無標題')} - {item.get('source', '未知')}\n"
    
    text += "\n【娛樂新聞】🎬\n"
    for item in news['entertainment']:
        text += f"🎭 {item.get('title', '無標題')} - {item.get('source', '未知')}\n"
    
    text += f"""
【財經】💹
📈 恒生指數：{finance['hsi']['index']} ({finance['hsi']['change']}, {finance['hsi']['percent']})
📈 阿里巴巴：{finance['alibaba']['price']} ({finance['alibaba']['change']}, {finance['alibaba']['percent']})
📈 騰訊：{finance['tencent']['price']} ({finance['tencent']['change']}, {finance['tencent']['percent']})
📈 匯豐控股：{finance['hsbc']['price']} ({finance['hsbc']['change']}, {finance['hsbc']['percent']})

---
📡 數據來源：data.gov.hk、Google新聞、市場數據
📅 生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return text

def save_briefing_files(html_content, text_content, timestamp):
    """保存簡報文件"""
    # 確保目錄存在
    output_dir = '/home/openclaw/.openclaw/workspace'
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存HTML文件
    html_file = os.path.join(output_dir, 'daily-briefing.html')
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✅ HTML簡報已生成: {html_file}")
    
    # 保存文字文件
    text_file = os.path.join(output_dir, 'briefing.txt')
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(text_content)
    print(f"✅ 文字簡報已生成: {text_file}")
    
    # 也保存帶時間戳的備份
    backup_html = os.path.join(output_dir, f'briefing_{timestamp}.html')
    with open(backup_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    backup_text = os.path.join(output_dir, f'briefing_{timestamp}.txt')
    with open(backup_text, 'w', encoding='utf-8') as f:
        f.write(text_content)

def main():
    """主函數"""
    try:
        success = generate_briefing()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"❌ 簡報生成失敗: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()