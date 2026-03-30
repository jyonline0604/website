#!/usr/bin/env python3
"""
九巴 ETA 數據獲取腳本
使用 data.gov.hk 九巴和龍運巴士 ETA API
"""

import requests
import json
from datetime import datetime, timedelta

class KMBBusETA:
    """九巴 ETA 數據獲取類"""
    
    def __init__(self):
        self.base_url = "https://data.etabus.gov.hk/v1/transport/kmb"
        
    def get_all_routes(self):
        """獲取所有巴士路線"""
        try:
            url = f"{self.base_url}/route/"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            else:
                print(f"獲取路線失敗: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"獲取路線異常: {str(e)}")
            return []
    
    def get_popular_routes(self):
        """獲取熱門巴士路線"""
        # 香港熱門巴士路線
        popular_routes = [
            {"route": "1", "name_tc": "竹園邨 ↔ 尖沙咀碼頭", "bound": "O"},
            {"route": "1A", "name_tc": "中秀茂坪 ↔ 尖沙咀碼頭", "bound": "O"},
            {"route": "2", "name_tc": "蘇屋 ↔ 尖沙咀碼頭", "bound": "O"},
            {"route": "5", "name_tc": "彩虹 ↔ 尖沙咀碼頭", "bound": "O"},
            {"route": "6", "name_tc": "荔枝角 ↔ 尖沙咀碼頭", "bound": "O"},
            {"route": "9", "name_tc": "彩福 ↔ 尖沙咀碼頭", "bound": "O"},
            {"route": "101", "name_tc": "觀塘 ↔ 堅尼地城", "bound": "O"},
            {"route": "102", "name_tc": "美孚 ↔ 筲箕灣", "bound": "O"},
            {"route": "104", "name_tc": "白田 ↔ 中環", "bound": "O"},
            {"route": "112", "name_tc": "蘇屋 ↔ 北角", "bound": "O"}
        ]
        
        return popular_routes
    
    def get_route_stops(self, route, bound="O", service_type="1"):
        """獲取路線的巴士站列表"""
        try:
            url = f"{self.base_url}/route-stop/{route}/{bound}/{service_type}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            else:
                print(f"獲取路線 {route} 巴士站失敗: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"獲取路線 {route} 巴士站異常: {str(e)}")
            return []
    
    def get_stop_eta(self, stop_id, route, service_type="1"):
        """獲取巴士站 ETA"""
        try:
            url = f"{self.base_url}/eta/{stop_id}/{route}/{service_type}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            else:
                print(f"獲取巴士站 {stop_id} ETA 失敗: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"獲取巴士站 {stop_id} ETA 異常: {str(e)}")
            return []
    
    def get_eta_for_popular_stops(self):
        """獲取熱門巴士站的 ETA"""
        print("=== 九巴熱門路線 ETA 數據 ===")
        
        # 熱門路線和對應的熱門巴士站
        popular_stops = [
            {
                "route": "1",
                "stop_id": "18492910339410B1",  # 竹園邨總站
                "stop_name": "竹園邨總站",
                "route_name": "1號線 (竹園邨 ↔ 尖沙咀碼頭)"
            },
            {
                "route": "101",
                "stop_id": "EAA1C5A9B4D7A7F3",  # 觀塘市中心 (假設ID)
                "stop_name": "觀塘市中心",
                "route_name": "101號線 (觀塘 ↔ 堅尼地城)"
            },
            {
                "route": "1A",
                "stop_id": "9ED7E93749ABAE67",  # 天虹小學
                "stop_name": "天虹小學",
                "route_name": "1A號線 (中秀茂坪 ↔ 尖沙咀碼頭)"
            }
        ]
        
        eta_results = []
        
        for stop_info in popular_stops:
            route = stop_info["route"]
            stop_id = stop_info["stop_id"]
            stop_name = stop_info["stop_name"]
            route_name = stop_info["route_name"]
            
            print(f"\n檢查: {route_name} - {stop_name}")
            
            try:
                etas = self.get_stop_eta(stop_id, route)
                
                if etas:
                    # 過濾和處理 ETA 數據
                    valid_etas = []
                    for eta in etas:
                        eta_time = eta.get("eta")
                        remark_tc = eta.get("rmk_tc", "")
                        remark_en = eta.get("rmk_en", "")
                        
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
                                            "remark_tc": remark_tc,
                                            "remark_en": remark_en,
                                            "eta_time": eta_time
                                        })
                            except Exception as e:
                                print(f"  時間解析錯誤: {str(e)}")
                                continue
                    
                    if valid_etas:
                        # 按時間排序
                        valid_etas.sort(key=lambda x: x["minutes"])
                        
                        # 取最近的3班
                        for eta in valid_etas[:3]:
                            minutes = eta["minutes"]
                            remark = eta["remark_tc"] or eta["remark_en"]
                            
                            eta_results.append({
                                "route_name": route_name,
                                "stop_name": stop_name,
                                "minutes": minutes,
                                "remark": remark
                            })
                            
                            print(f"  ✓ {minutes}分鐘" + (f" ({remark})" if remark else ""))
                    else:
                        print(f"  ⚠️ 無30分鐘內的班次")
                else:
                    print(f"  ⚠️ 無ETA數據")
                    
            except Exception as e:
                print(f"  ✗ 獲取ETA失敗: {str(e)}")
                continue
        
        return eta_results
    
    def generate_eta_summary(self):
        """生成 ETA 摘要"""
        print("\n=== 生成九巴 ETA 摘要 ===")
        
        eta_data = self.get_eta_for_popular_stops()
        
        if not eta_data:
            print("❌ 無法獲取九巴 ETA 數據")
            return None
        
        # 構建摘要
        summary = "🚌 **九巴實時到站數據** (data.gov.hk 官方數據)\n\n"
        
        for eta in eta_data:
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
            
            summary += f"{emoji} **{route_name}**\n"
            summary += f"  站點: {stop_name}\n"
            summary += f"  預計: {minutes}分鐘"
            
            if remark:
                summary += f" ({remark})"
            
            summary += "\n\n"
        
        summary += f"⏰ 更新時間: {datetime.now().strftime('%H:%M')}\n"
        summary += "📡 數據來源: data.gov.hk 九巴和龍運巴士 ETA API"
        
        return summary

def main():
    """主函數"""
    print(f"當前時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    kmb_eta = KMBBusETA()
    
    # 測試 API 連接
    print("測試九巴 API 連接...")
    routes = kmb_eta.get_all_routes()
    
    if routes:
        print(f"✓ 成功獲取 {len(routes)} 條巴士路線")
        
        # 顯示前5條路線
        print("\n前5條巴士路線:")
        for i, route in enumerate(routes[:5]):
            route_num = route.get("route", "N/A")
            orig_tc = route.get("orig_tc", "N/A")
            dest_tc = route.get("dest_tc", "N/A")
            print(f"  {i+1}. {route_num}號線: {orig_tc} ↔ {dest_tc}")
    else:
        print("✗ 無法獲取巴士路線")
    
    # 生成 ETA 摘要
    summary = kmb_eta.generate_eta_summary()
    
    if summary:
        print("\n" + "="*60)
        print(summary)
        print("="*60)
    else:
        print("\n❌ 無法生成九巴 ETA 摘要")

if __name__ == "__main__":
    main()