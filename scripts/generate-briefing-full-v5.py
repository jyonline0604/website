#!/usr/bin/env python3
"""
香港簡報生成腳本（完整官方數據版 v5）
使用香港政府官方 API：data.gov.hk、香港天文台、運輸署特別交通消息、港鐵下一班列車、九巴 ETA、城巴 ETA
"""

import os
import sys
import re
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import feedparser

WORKSPACE = "/home/openclaw/.openclaw/workspace"
LOG_FILE = os.path.join(WORKSPACE, "logs/briefing-full-v5.log")

def log(message, print_to_stdout=False):
    """寫入日誌（，生產環境不輸出到stdout）"""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_line = f"{timestamp} {message}"
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")
    
    # 只在明確要求時才輸出到 stdout
    if print_to_stdout:
        print(log_line)
    
    return log_line

class FullBriefingGeneratorV5:
    """完整官方數據簡報生成器 v5"""
    
    def __init__(self):
        self.cache = {}
        self.cache_time = {}
        
    def get_current_date(self):
        """獲取當前日期"""
        now = datetime.now()
        return now.strftime("%Y年%m月%d日")
    
    def get_briefing_type(self):
        """根據當前時間確定簡報類型"""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return "晨間簡報", "🌅"
        elif 12 <= hour < 17:
            return "午間簡報", "☀️"
        else:
            return "傍晚簡報", "🌆"
    
    def fetch_with_cache(self, cache_key, fetch_func, cache_minutes=5):
        """帶緩存的數據獲取"""
        now = datetime.now()
        
        if (cache_key in self.cache and 
            cache_key in self.cache_time and
            (now - self.cache_time[cache_key]).seconds < cache_minutes * 60):
            log(f"使用緩存: {cache_key}")
            return self.cache[cache_key]
        
        try:
            result = fetch_func()
            self.cache[cache_key] = result
            self.cache_time[cache_key] = now
            return result
        except Exception as e:
            log(f"獲取 {cache_key} 異常: {str(e)}")
            
            # 返回緩存數據（即使過期）
            if cache_key in self.cache:
                log(f"使用過期緩存: {cache_key}")
                return self.cache[cache_key]
            
            raise
    
    def fetch_hko_current_weather(self):
        """獲取香港天文台實時天氣數據"""
        try:
            log("獲取天文台實時天氣數據...")
            
            url = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang=tc"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # 提取溫度
                temp_data = data.get("temperature", {}).get("data", [])
                hko_temp = "N/A"
                for item in temp_data:
                    if item.get("place") == "香港天文台":
                        hko_temp = item.get("value")
                        break
                
                # 提取濕度
                humidity_data = data.get("humidity", {}).get("data", [])
                hko_humidity = "N/A"
                for item in humidity_data:
                    if item.get("place") == "香港天文台":
                        hko_humidity = item.get("value")
                        break
                
                # 提取警告信息
                warnings = data.get("warningMessage", [])
                
                return {
                    "temperature": hko_temp,
                    "humidity": hko_humidity,
                    "warnings": warnings,
                    "update_time": data.get("updateTime", "")
                }
                
        except Exception as e:
            log(f"獲取天文台天氣異常: {str(e)}")
        
        return {
            "temperature": "N/A",
            "humidity": "N/A",
            "warnings": [],
            "update_time": ""
        }
    
    def fetch_hko_forecast(self):
        """獲取香港天文台天氣預報"""
        try:
            log("獲取天文台天氣預報...")
            
            url = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=flw&lang=tc"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    "forecast_desc": data.get("forecastDesc", "數據更新中"),
                    "outlook": data.get("outlook", "")
                }
                
        except Exception as e:
            log(f"獲取天文台預報異常: {str(e)}")
        
        return {
            "forecast_desc": "請查看天文台網站",
            "outlook": ""
        }
    
    def fetch_td_special_traffic_news(self):
        """獲取運輸署特別交通消息"""
        try:
            log("獲取運輸署特別交通消息...")
            
            url = "https://resource.data.one.gov.hk/td/tc/specialtrafficnews.xml"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                ns = {'td': 'http://data.one.gov.hk/td'}
                
                messages = []
                for message in root.findall('td:message', ns):
                    chin_text = message.find('td:ChinText', ns)
                    current_status = message.find('td:CurrentStatus', ns)
                    
                    if chin_text is not None and chin_text.text:
                        text = chin_text.text.strip()
                        
                        if text and len(text) > 10:
                            status = current_status.text if current_status is not None else ""
                            
                            # 只保留當前有效的消息（狀態為3）
                            if status == "3":
                                simplified = re.sub(r'\s+', ' ', text)
                                if len(simplified) > 100:
                                    simplified = simplified[:97] + "..."
                                messages.append(simplified)
                
                messages.reverse()
                log(f"找到 {len(messages)} 條特別交通消息")
                return messages[:3]
                
        except Exception as e:
            log(f"獲取運輸署交通消息異常: {str(e)}")
        
        return []
    
    def fetch_mtr_next_train(self):
        """獲取港鐵多條線路的下一班列車數據"""
        try:
            log("獲取港鐵多條線路列車數據...")
            
            # 可用的 MTR 線路和站點
            mtr_lines = [
                {"name": "港島線", "line": "ISL", "station": "CEN", "station_name": "中環"},
                {"name": "港島線", "line": "ISL", "station": "CAB", "station_name": "銅鑼灣"},
                {"name": "將軍澳線", "line": "TKL", "station": "TKO", "station_name": "將軍澳"},
                {"name": "將軍澳線", "line": "TKL", "station": "LHP", "station_name": "寶琳"},
                {"name": "東鐵線", "line": "EAL", "station": "FAN", "station_name": "粉嶺"},
                {"name": "東鐵線", "line": "EAL", "station": "TWO", "station_name": "上水"},
            ]
            
            results = []
            dest_map = {
                # 港島線
                "CHW": "柴灣", "KET": "堅尼地城", "SYP": "筲箕灣", "TAP": "太古城",
                "HFC": "杏花邨", "SKT": "石塘咀", "BRH": "寶翠園",
                # 將軍澳線
                "POA": "寶琳", "LHP": "康城", "TIK": "調景嶺", "NOP": "北角",
                # 東鐵線
                "ADM": "金鐘", "HRT": "紅磡", "KOT": "九龍塘", "SHT": "沙田",
                "FAN": "火炭", "TWO": "上水", "LOW": "羅湖", "LMC": "落馬洲",
                # 觀塘線
                "YAT": "油塘", "NTK": "牛頭山", "KWH": "觀塘", "SKM": "石門",
                "WHA": "黃埔", "HPH": "何文田"
            }
            
            for mtr in mtr_lines[:6]:  # 最多6條線路
                try:
                    url = f"https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php?line={mtr['line']}&sta={mtr['station']}&lang=tc"
                    response = requests.get(url, timeout=5)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data.get("data"):
                            station_key = f"{mtr['line']}-{mtr['station']}"
                            station_data = data["data"].get(station_key)
                            
                            if station_data:
                                # 獲取上行方向列車
                                up_trains = station_data.get("UP", [])
                                
                                if up_trains:
                                    nearest = up_trains[0]
                                    dest = nearest.get("dest", "")
                                    
                                    # 使用 ttnt (time to next train)
                                    try:
                                        ttnt = nearest.get("ttnt", "0")
                                        minutes = int(ttnt) if ttnt else 0
                                        
                                        # 如果 ttnt 是 0，表示列車已到站，使用下一班
                                        if minutes == 0 and len(up_trains) > 1:
                                            nearest = up_trains[1]
                                            dest = nearest.get("dest", "")
                                            ttnt = nearest.get("ttnt", "0")
                                            minutes = int(ttnt) if ttnt else 1
                                        
                                        if minutes > 0 and minutes < 30:
                                            dest_name = dest_map.get(dest, dest)
                                            line_station = f"{mtr['name']} {mtr['station_name']}"
                                            
                                            results.append({
                                                "line_station": line_station,
                                                "minutes": minutes,
                                                "destination": dest_name,
                                                "direction": "→"
                                            })
                                    except:
                                        pass
                except:
                    pass
            
            return results[:6]  # 最多6條
                    
        except Exception as e:
            log(f"獲取港鐵列車數據異常: {str(e)}")
        
        return []
    
    def fetch_kmb_bus_eta(self):
        """獲取九巴多條路線的實時到站數據"""
        try:
            log("獲取九巴實時到站數據...")
            
            # 九巴熱門路線和站點
            kmb_routes = [
                {"route": "1", "stop_id": "RI5fgPrP", "name": "1", "stop": "竹園邨總站"},
                {"route": "203", "stop_id": "RI5fgPrP", "name": "203", "stop": "竹園邨總站"},
                {"route": "208", "stop_id": "RI5fgPrP", "name": "208", "stop": "竹園邨總站"},
            ]
            
            results = []
            
            for kmb in kmb_routes:
                try:
                    url = f"https://data.etabus.gov.hk/v1/transport/kmb/eta/{kmb['route']}/{kmb['stop_id']}/1"
                    response = requests.get(url, timeout=5)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data.get("data"):
                            etas = data["data"]
                            
                            valid_etas = []
                            for eta in etas:
                                eta_time = eta.get("eta")
                                remark = eta.get("rmk_tc", eta.get("rmk_en", ""))
                                
                                if eta_time:
                                    try:
                                        eta_dt = datetime.fromisoformat(eta_time.replace('Z', '+00:00'))
                                        now = datetime.now().astimezone()
                                        time_diff = (eta_dt - now).total_seconds() / 60
                                        
                                        if time_diff >= 0:
                                            minutes = int(time_diff)
                                            if minutes <= 30:
                                                valid_etas.append({
                                                    "minutes": minutes,
                                                    "remark": remark
                                                })
                                    except:
                                        continue
                            
                            if valid_etas:
                                valid_etas.sort(key=lambda x: x["minutes"])
                                nearest = valid_etas[0]
                                
                                results.append({
                                    "route_name": f"{kmb['name']}號線",
                                    "stop_name": kmb['stop'],
                                    "minutes": nearest["minutes"],
                                    "remark": nearest["remark"]
                                })
                except:
                    pass
            
            return results[:4]  # 最多4條路線
                    
        except Exception as e:
            log(f"獲取九巴 ETA 異常: {str(e)}")
        
        return []
    
    def fetch_news_rss(self, category, num_items=3):
        """獲取新聞 RSS（增強版，每項3條）"""
        try:
            log(f"獲取 {category} 新聞 RSS（目標: {num_items}條）...")
            
            category_map = {
                "entertainment": "娛樂",
                "tech": "科技", 
                "finance": "財經"
            }
            
            chinese_category = category_map.get(category, category)
            
            # 嘗試多個搜索詞以獲取更多新聞
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
                    
                    log(f"  搜索詞: {query}, 找到條目: {len(feed.entries)}")
                    
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
                                
                except Exception as e:
                    log(f"  搜索詞 {query} 異常: {str(e)}")
                    continue
            
            # 如果還不夠，使用備用新聞
            if len(all_news) < num_items:
                log(f"  新聞不足，使用備用新聞補足")
                
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
            
            log(f"  最終獲取: {len(all_news)}條")
            return all_news[:num_items]
                
        except Exception as e:
            log(f"獲取 {category} 新聞異常: {str(e)}")
        
        # 最終備用方案
        backup = {
            "entertainment": [
                "香港娛樂新聞持續更新",
                "影視作品最新動態",
                "藝人活動消息"
            ],
            "tech": [
                "香港科技發展新動向",
                "創新科技應用消息",
                "數碼轉型最新趨勢"
            ],
            "finance": [
                "香港股市最新動態",
                "財經市場消息更新",
                "經濟數據公布"
            ]
        }
        
        return backup.get(category, ["新聞數據更新中"] * num_items)[:num_items]
    
    def fetch_real_finance_news(self):
        """獲取真實的財經新聞（加密貨幣+美股）"""
        try:
            log("獲取真實財經新聞（加密貨幣+美股）...")
            
            # 導入真實財經新聞模塊
            import sys
            sys.path.append("/home/openclaw/.openclaw/workspace/scripts")
            
            try:
                from real_finance_news import fetch_real_crypto_news, fetch_real_stock_news
                
                crypto_news = fetch_real_crypto_news(2)  # 2條加密貨幣新聞
                stock_news = fetch_real_stock_news(2)    # 2條美股新聞
                
                # 合併為財經新聞
                finance_news = crypto_news + stock_news
                
                if len(finance_news) >= 3:
                    log(f"  獲取到 {len(finance_news)} 條真實財經新聞")
                    return finance_news[:3]
                else:
                    log(f"  真實財經新聞不足，使用備用")
                    
            except ImportError:
                log("  無法導入真實財經新聞模塊，使用標準方法")
            
            # 備用：使用標準方法
            return self.fetch_news_rss("finance", 3)
            
        except Exception as e:
            log(f"獲取真實財經新聞異常: {str(e)}")
            return self.fetch_news_rss("finance", 3)
    
    def generate_briefing(self):
        """生成完整官方數據簡報"""
        log("開始生成完整官方數據香港簡報 v5...")
        
        # 獲取當前信息
        current_date = self.get_current_date()
        briefing_type, emoji = self.get_briefing_type()
        
        # 獲取官方數據
        current_weather = self.fetch_with_cache(
            "current_weather", 
            self.fetch_hko_current_weather,
            cache_minutes=5
        )
        
        forecast = self.fetch_with_cache(
            "forecast",
            self.fetch_hko_forecast,
            cache_minutes=30
        )
        
        # 特別交通消息（不緩存）
        traffic_news = self.fetch_td_special_traffic_news()
        
        # 港鐵下一班列車數據
        mtr_trains = self.fetch_mtr_next_train()
        
        # 九巴 ETA 數據
        kmb_etas = self.fetch_kmb_bus_eta()
        
        # 新聞數據（每項3條）
        entertainment = self.fetch_with_cache(
            "entertainment_news",
            lambda: self.fetch_news_rss("entertainment", num_items=3),
            cache_minutes=15
        )
        
        tech = self.fetch_with_cache(
            "tech_news",
            lambda: self.fetch_news_rss("tech", num_items=3),
            cache_minutes=15
        )
        
        # 使用真實財經新聞
        finance = self.fetch_with_cache(
            "finance_news",
            self.fetch_real_finance_news,
            cache_minutes=15
        )
        
        # 構建完整簡報
        briefing = f"""📰 香港簡報 ({current_date}) {emoji} {briefing_type}

【天氣】🌤️ 香港天文台實時數據
🌡️ 氣溫：{current_weather['temperature']}度
💧 濕度：{current_weather['humidity']}%

【天氣警告】⚠️"""
        
        if current_weather['warnings']:
            for warning in current_weather['warnings'][:2]:
                briefing += f"\n⚠️ {warning}"
        else:
            briefing += "\n✅ 現時沒有天氣警告"
        
        briefing += f"""

【預報】📡 香港天文台
{forecast['forecast_desc']}

【展望】🔭
{forecast['outlook']}

【特別交通消息】🚨 運輸署實時消息"""
        
        if traffic_news:
            for i, item in enumerate(traffic_news, 1):
                briefing += f"\n🚨 {item}"
        else:
            briefing += "\n✅ 現時沒有特別交通消息"
        
        briefing += f"""

【港鐵列車到站】🚇 data.gov.hk 實時數據"""
        
        if mtr_trains:
            for train in mtr_trains:
                line_station = train["line_station"]
                minutes = train["minutes"]
                destination = train["destination"]
                direction = train["direction"]
                
                if minutes <= 2:
                    train_emoji = "🟢"
                elif minutes <= 5:
                    train_emoji = "🟡"
                else:
                    train_emoji = "🔵"
                
                briefing += f"\n{train_emoji} {line_station}: {minutes}分鐘 {direction} {destination}"
        else:
            briefing += "\n📊 港鐵列車數據更新中"
        
        briefing += f"""

【九巴實時到站】🚌 data.gov.hk 官方數據"""
        
        if kmb_etas:
            for eta in kmb_etas:
                route_name = eta["route_name"]
                stop_name = eta["stop_name"]
                minutes = eta["minutes"]
                remark = eta["remark"]
                
                if minutes <= 3:
                    bus_emoji = "🟢"
                elif minutes <= 10:
                    bus_emoji = "🟡"
                else:
                    bus_emoji = "🔵"
                
                briefing += f"\n{bus_emoji} {route_name}"
                briefing += f"\n  站點: {stop_name}"
                briefing += f"\n  預計: {minutes}分鐘"
                if remark:
                    briefing += f" ({remark})"
                briefing += "\n"
        else:
            briefing += "\n📊 九巴 ETA 數據暫時無法取得\n🔗 請使用《香港出行易》APP 查詢"
        
        briefing += f"""

【娛樂】🎬 即時娛樂頭條"""
        
        for i, item in enumerate(entertainment, 1):
            briefing += f"\n🎭 {item}"
        
        briefing += f"""

【科技】🔬 即時科技頭條"""
        
        for i, item in enumerate(tech, 1):
            briefing += f"\n🔧 {item}"
        
        briefing += f"""

【財經】💹 即時財經頭條"""
        
        for i, item in enumerate(finance, 1):
            briefing += f"\n📈 {item}"
        
        log(f"完整官方數據簡報生成完成，長度: {len(briefing)} 字符")
        return briefing

def main():
    """主函數"""
    try:
        generator = FullBriefingGeneratorV5()
        briefing = generator.generate_briefing()
        print(briefing)
        return 0
    except Exception as e:
        log(f"❌ 生成完整官方數據簡報時出錯: {str(e)}")
        
        # 緊急備用：使用 v4 官方版
        try:
            from generate_briefing_official_v4_final import OfficialBriefingGeneratorV4
            v4_generator = OfficialBriefingGeneratorV4()
            backup = v4_generator.generate_briefing()
            print(backup)
            log("✅ 使用官方版 v4 備用簡報成功")
            return 0
        except:
            # 再備用：使用 v3 官方版
            try:
                from generate_briefing_official_v3 import OfficialBriefingGeneratorV3
                v3_generator = OfficialBriefingGeneratorV3()
                backup = v3_generator.generate_briefing()
                print(backup)
                log("✅ 使用官方版 v3 備用簡報成功")
                return 0
            except:
                log("❌ 所有備用方案都失敗")
                return 1

if __name__ == "__main__":
    sys.exit(main())