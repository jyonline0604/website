#!/usr/bin/env python3
"""
港鐵下一班列車簡報生成器
使用 data.gov.hk 港鐵實時列車服務資訊 API
"""

import os
import sys
import json
import requests
from datetime import datetime

def get_mtr_next_train():
    """獲取港鐵下一班列車數據"""
    print("=== 港鐵下一班列車數據 ===")
    
    # 熱門港鐵站點
    stations = [
        {"line": "TKL", "station": "TKO", "name": "將軍澳站"},
        {"line": "TWL", "station": "TST", "name": "尖沙咀站"},
        {"line": "ISL", "station": "CEN", "name": "中環站"},
        {"line": "EAL", "station": "HUH", "name": "紅磡站"},
        {"line": "TKL", "station": "POA", "name": "寶琳站"}
    ]
    
    results = []
    
    for station in stations[:3]:  # 只檢查前3個站點
        line = station["line"]
        sta = station["station"]
        name = station["name"]
        
        try:
            # 港鐵下一班列車 API
            url = f"https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php?line={line}&sta={sta}&lang=tc"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == 1 and data.get("data"):
                    station_data = data["data"].get(f"{line}-{sta}")
                    
                    if station_data:
                        # 獲取兩個方向的列車
                        up_trains = station_data.get("UP", [])
                        down_trains = station_data.get("DOWN", [])
                        
                        # 合併並排序
                        all_trains = []
                        for train in up_trains[:2]:
                            train["direction"] = "上行"
                            all_trains.append(train)
                        
                        for train in down_trains[:2]:
                            train["direction"] = "下行"
                            all_trains.append(train)
                        
                        # 按時間排序
                        all_trains.sort(key=lambda x: x.get("time", ""))
                        
                        # 獲取最近的列車
                        if all_trains:
                            nearest = all_trains[0]
                            train_time = nearest.get("time", "")
                            dest = nearest.get("dest", "")
                            ttnt = nearest.get("ttnt", "")
                            direction = nearest.get("direction", "")
                            
                            # 計算分鐘差
                            try:
                                train_dt = datetime.strptime(train_time, "%Y-%m-%d %H:%M:%S")
                                now = datetime.now()
                                minutes = int((train_dt - now).total_seconds() / 60)
                                
                                if minutes >= 0:
                                    # 目的地映射
                                    dest_map = {
                                        "POA": "寶琳", "LHP": "康城", "TIK": "調景嶺",
                                        "NOP": "北角", "TST": "尖沙咀", "CEN": "中環",
                                        "HUH": "紅磡", "ADM": "金鐘", "KOW": "九龍",
                                        "MKK": "旺角", "TSY": "青衣", "TUC": "東涌"
                                    }
                                    
                                    dest_name = dest_map.get(dest, dest)
                                    
                                    results.append({
                                        "station": name,
                                        "minutes": minutes,
                                        "destination": dest_name,
                                        "direction": direction,
                                        "platform": nearest.get("plat", "1")
                                    })
                            except:
                                continue
            
            print(f"✓ {name}: 數據獲取成功")
            
        except Exception as e:
            print(f"✗ {name}: 數據獲取失敗 - {str(e)}")
            continue
    
    return results

def generate_briefing():
    """生成簡報"""
    print("\n=== 生成港鐵列車簡報 ===")
    
    trains = get_mtr_next_train()
    
    if not trains:
        print("❌ 無法獲取港鐵列車數據")
        return None
    
    # 構建簡報
    briefing = "🚇 **港鐵下一班列車** (data.gov.hk 實時數據)\n\n"
    
    for train in trains:
        station = train["station"]
        minutes = train["minutes"]
        destination = train["destination"]
        direction = train["direction"]
        
        if minutes <= 2:
            emoji = "🟢"
        elif minutes <= 5:
            emoji = "🟡"
        else:
            emoji = "🔵"
        
        briefing += f"{emoji} **{station}**: {minutes}分鐘 → {destination} ({direction})\n"
    
    briefing += f"\n⏰ 更新時間: {datetime.now().strftime('%H:%M')}"
    briefing += "\n📡 數據來源: data.gov.hk 港鐵實時列車服務資訊"
    
    return briefing

if __name__ == "__main__":
    print(f"當前時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    briefing = generate_briefing()
    
    if briefing:
        print("\n" + "="*50)
        print(briefing)
        print("="*50)
    else:
        print("❌ 簡報生成失敗")