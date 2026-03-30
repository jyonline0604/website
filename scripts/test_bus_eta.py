#!/usr/bin/env python3
"""
測試九巴 ETA API
"""

import requests
import json
from datetime import datetime

def test_kmb_eta():
    """測試九巴 ETA API"""
    
    # 九巴 1 號路線（尖沙咀碼頭 ↔ 竹園邨）
    # 參數說明：
    # - route: 路線號碼
    # - bound: 方向 (1=去程, 2=回程)
    # - stop: 巴士站編號
    # - stop_seq: 巴士站序號
    # - servicetype: 服務類型 (01=正常服務)
    
    test_cases = [
        {
            "name": "九巴 1 號線（往竹園邨）",
            "params": {
                "action": "geteta",
                "lang": "tc",
                "route": "1",
                "bound": "1",
                "stop": "CA01S00500",  # 尖沙咀碼頭
                "stop_seq": "1",
                "servicetype": "01"
            }
        },
        {
            "name": "九巴 101 號線（往堅尼地城）",
            "params": {
                "action": "geteta",
                "lang": "tc",
                "route": "101",
                "bound": "1",
                "stop": "CA01S00500",
                "stop_seq": "1",
                "servicetype": "01"
            }
        }
    ]
    
    base_url = "http://etav3.kmb.hk/"
    
    for test in test_cases:
        print(f"\n=== 測試: {test['name']} ===")
        
        try:
            response = requests.get(base_url, params=test['params'], timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"狀態碼: {response.status_code}")
                print(f"響應: {json.dumps(data, ensure_ascii=False, indent=2)}")
                
                # 解析 ETA 數據
                if 'response' in data:
                    for eta in data['response']:
                        if 'eta' in eta:
                            eta_time = eta['eta']
                            remark = eta.get('remark', {}).get('zh', '')
                            print(f"預計到站: {eta_time} - {remark}")
            else:
                print(f"錯誤: 狀態碼 {response.status_code}")
                print(f"響應: {response.text[:200]}")
                
        except Exception as e:
            print(f"異常: {str(e)}")

def test_ctb_eta():
    """測試城巴 ETA API"""
    print("\n=== 測試城巴 ETA ===")
    
    # 城巴 API 端點（示例）
    try:
        # 城巴 5B 號線
        url = "https://rt.data.gov.hk/v1/transport/citybus-nwfb/eta/CTB/5B/1"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"城巴 API 響應: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}")
        else:
            print(f"城巴 API 錯誤: {response.status_code}")
            
    except Exception as e:
        print(f"城巴 API 異常: {str(e)}")

def test_data_gov_hk_bus():
    """測試 data.gov.hk 巴士數據"""
    print("\n=== 測試 data.gov.hk 巴士數據 ===")
    
    try:
        # 嘗試獲取巴士路線列表
        url = "https://resource.data.one.gov.hk/td/routesearch.json"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"找到 {len(data)} 條巴士路線")
            
            # 顯示前幾條路線
            for i, route in enumerate(data[:5]):
                print(f"{i+1}. {route.get('route', 'N/A')} - {route.get('dest_tc', 'N/A')}")
        else:
            print(f"data.gov.hk API 錯誤: {response.status_code}")
            
    except Exception as e:
        print(f"data.gov.hk API 異常: {str(e)}")

if __name__ == "__main__":
    print("開始測試巴士 ETA API...")
    print(f"當前時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_kmb_eta()
    test_ctb_eta()
    test_data_gov_hk_bus()