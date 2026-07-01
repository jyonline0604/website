#!/usr/bin/env python3
"""
每週自動更新巴士路線/車站數據
從 DATA.GOV.HK API 獲取最新九巴和城巴路線資料
MTR 港鐵巴士數據來自靜態 CSV，較少變動，不自動更新
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# API endpoints
KMB_BASE = "https://data.etabus.gov.hk/v1/transport/kmb"
CTB_ROUTE_URL = "https://rt.data.gov.hk/v2/transport/citybus/route/ctb"

os.makedirs(DATA_DIR, exist_ok=True)


def fetch_json(url, timeout=120):
    """下載 JSON 數據"""
    headers = {
        "User-Agent": "kofhk-bus-updater/1.0",
        "Accept": "application/json",
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            return json.loads(raw.decode("utf-8-sig"))
    except Exception as e:
        print(f"  ERROR: {e}")
        return None


def save_json(filename, data):
    """儲存 JSON 到 data/ 目錄"""
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    size_kb = os.path.getsize(path) / 1024
    print(f"  OK  {filename} ({size_kb:.0f} KB)")


def update_kmb_routes():
    """下載 KMB 路線列表"""
    print("\n[KMB] 下載路線列表...")
    data = fetch_json(f"{KMB_BASE}/route/")
    if data and "data" in data:
        save_json("kmb_routes.json", data)
        return True
    print("  FAILED")
    return False


def update_kmb_route_stops():
    """下載 KMB 路線-車站對照表"""
    print("\n[KMB] 下載路線-車站對照表...")
    data = fetch_json(f"{KMB_BASE}/route-stop/", timeout=180)
    if data and "data" in data:
        save_json("kmb_route_stops.json", data)
        return True
    print("  FAILED")
    return False


def update_kmb_stops():
    """下載 KMB 車站列表"""
    print("\n[KMB] 下載車站列表...")
    data = fetch_json(f"{KMB_BASE}/stop/", timeout=120)
    if data and "data" in data:
        save_json("kmb_stops.json", data)
        return True
    print("  FAILED")
    return False


def update_ctb_routes():
    """下載 CTB 城巴路線列表"""
    print("\n[CTB] 下載城巴路線列表...")
    data = fetch_json(CTB_ROUTE_URL, timeout=60)
    if data:
        # CTB API 直接返回 {data: [...]}
        save_json("ctb_routes.json", data)
        return True
    print("  FAILED")
    return False


def main():
    print("=" * 50)
    print(f"Bus data update — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 50)

    ok = 0
    fail = 0

    for name, fn in [
        ("KMB Routes", update_kmb_routes),
        ("KMB Route-Stops", update_kmb_route_stops),
        ("KMB Stops", update_kmb_stops),
        ("CTB Routes", update_ctb_routes),
    ]:
        try:
            if fn():
                ok += 1
            else:
                fail += 1
        except Exception as e:
            print(f"  EXCEPTION: {e}")
            fail += 1
        time.sleep(1)

    print(f"\n{'='*50}")
    print(f"Result: {ok} OK, {fail} FAILED")
    print(f"{'='*50}")

    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
