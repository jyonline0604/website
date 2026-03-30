#!/usr/bin/env python3
"""
香港簡報生成腳本 v5（簡化版）
包含九巴 ETA 數據
"""

import os
import sys
import json
import requests
from datetime import datetime

def get_kmb_eta():
    """獲取九巴 ETA 數據"""
    print("獲取九巴 ETA 數據...")
    
    # 九巴熱門路線
    popular_stops = [
        {
            "route": "1",
            "stop_id": "18492910339410B1",  # 竹園邨總站
            "stop_name": "竹園邨總站",
            "route_name": "1號線 (竹園邨 ↔ 尖沙咀碼頭)"
        }
    ]
    
    results = []
    
    for stop_info in popular_stops:
        route = stop_info["route"]
        stop_id = stop_info["stop_id"]
        stop_name = stop_info["stop_name"]
        route_name = stop_info["route_name"]
        
        try:
            # 九巴 ETA API
            url = f"https://data.etabus.gov.hk/v1/transport/kmb/eta/{stop_id}/{route}/1"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("data"):
                    etas = data["data"]
                    
                    # 處理 ETA 數據
                    valid_etas = []
                    for eta in etas:
                        eta_time = eta.get("eta")
                        remark = eta.get("rmk_tc", eta.get("rmk_en", ""))
                        
                        if eta_time:
                            try:
                                # 解析時間
                                eta_dt = datetime.fromisoformat(eta_time.replace('Z', '+00:00'))
                                now = datetime.now().astimezone()
                                
                                # 計算分鐘差
                                time_diff = (eta_dt - now).total_seconds() / 60
                                
                                if time_diff >= 0:  # 未來時間
                                    minutes = int(time_diff)
                                    
                                    if minutes <= 30:  # 只顯示30分鐘內的班次
                                        valid_etas.append({
                                            "minutes": minutes,
                                            "remark": remark
                                        })
                            except:
                                continue
                    
                    if valid_etas:
                        # 按時間排序
                        valid_etas.sort(key=lambda x: x["minutes"])
                        
                        # 取最近的班次
                        nearest = valid_etas[0]
                        minutes = nearest["minutes"]
                        remark = nearest["remark"]
                        
                        results.append({
                            "route_name": route_name,
                            "stop_name": stop_name,
                            "minutes": minutes,
                            "remark": remark
                        })
                        
                        print(f"✓ {route_name}: {minutes}分鐘" + (f" ({remark})" if remark else ""))
                    else:
                        print(f"⚠️ {route_name}: 無30分鐘內的班次")
                else:
                    print(f"⚠️ {route_name}: 無ETA數據")
            else:
                print(f"✗ {route_name}: API 錯誤 {response.status_code}")
                
        except Exception as e:
            print(f"✗ {route_name}: 異常 {str(e)}")
            continue
    
    return results

def generate_briefing():
    """生成簡報"""
    print("\n=== 生成香港簡報 v5 ===")
    
    # 獲取九巴 ETA 數據
    kmb_etas = get_kmb_eta()
    
    # 構建簡報
    briefing = f"""📰 香港簡報 ({datetime.now().strftime('%Y年%m月%d日')}) ☀️ 午間簡報

【九巴實時到站】🚌 data.gov.hk 官方數據"""
    
    if kmb_etas:
        for eta in kmb_etas:
            route_name = eta["route_name"]
            stop_name = eta["stop_name"]
            minutes = eta["minutes"]
            remark = eta["remark"]
            
            if minutes <= 3:
                emoji = "🟢"
            elif minutes <= 10:
                emoji = "🟡"
            else:
                emoji = "🔵"
            
            briefing += f"\n{emoji} {route_name}"
            briefing += f"\n  站點: {stop_name}"
            briefing += f"\n  預計: {minutes}分鐘"
            if remark:
                briefing += f" ({remark})"
            briefing += "\n"
    else:
        briefing += "\n📊 九巴數據更新中"
    
    briefing += f"""

【數據來源】📡
• 九巴 ETA: data.gov.hk 九巴和龍運巴士 ETA API
• 更新時間: {datetime.now().strftime('%H:%M')}
• 官方網站: data.gov.hk、kmb.hk"""
    
    return briefing

if __name__ == "__main__":
    print(f"當前時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    briefing = generate_briefing()
    
    print("\n" + "="*60)
    print(briefing)
    print("="*60)