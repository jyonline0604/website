"""Download GMB route and stop data as static JSON files.
Saves incrementally to survive crashes."""
import json, os, sys, time, urllib.request, urllib.error

BASE = "https://data.etagmb.gov.hk"
OUT = "data"
os.makedirs(OUT, exist_ok=True)

def api(path):
    url = f"{BASE}{path}"
    req = urllib.request.Request(url)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except Exception as e:
            if attempt == 2:
                print(f"  FAIL: {path}: {e}", flush=True)
                return None
            time.sleep(2)

# --- Step 1: Route list + details ---
routes_file = f"{OUT}/gmb_routes.json"
all_details = []

if os.path.exists(routes_file):
    print("Loading existing gmb_routes.json...", flush=True)
    with open(routes_file, "r", encoding="utf-8") as f:
        all_details = json.load(f).get("data", [])
    print(f"  Loaded {len(all_details)} existing direction entries", flush=True)

if not all_details:
    print("Fetching route list...", flush=True)
    rd = api("/route")
    if not rd:
        print("FATAL: cannot fetch routes", flush=True); sys.exit(1)
    regions = rd["data"]["routes"]
    total = sum(len(v) for v in regions.values())
    print(f"  {total} routes across {list(regions.keys())}", flush=True)

    fetched = 0
    for region, codes in regions.items():
        for code in codes:
            d = api(f"/route/{region}/{code}")
            if d and "data" in d:
                for entry in d["data"]:
                    for direction in entry.get("directions", []):
                        all_details.append({
                            "route_id": entry["route_id"],
                            "region": entry["region"],
                            "route_code": entry["route_code"],
                            "route_seq": direction["route_seq"],
                            "orig_tc": direction.get("orig_tc", ""),
                            "orig_en": direction.get("orig_en", ""),
                            "dest_tc": direction.get("dest_tc", ""),
                            "dest_en": direction.get("dest_en", ""),
                        })
            fetched += 1
            if fetched % 100 == 0:
                print(f"  Route details: {fetched}/{total}", flush=True)
            time.sleep(0.05)

    print(f"  Got {len(all_details)} direction entries", flush=True)
    with open(routes_file, "w", encoding="utf-8") as f:
        json.dump({
            "type": "GMBRouteList", "version": "1.0",
            "generated_timestamp": rd.get("generated_timestamp", ""),
            "data": all_details,
        }, f, ensure_ascii=False)
    print(f"  Saved gmb_routes.json ({os.path.getsize(routes_file):,} bytes)", flush=True)

# --- Step 2: Route stops ---
stops_file = f"{OUT}/gmb_route_stops.json"
route_stops = {}

if os.path.exists(stops_file):
    print("Loading existing gmb_route_stops.json...", flush=True)
    with open(stops_file, "r", encoding="utf-8") as f:
        route_stops = json.load(f).get("data", {})
    print(f"  Loaded {len(route_stops)} existing stop entries", flush=True)

total = len(all_details)
done = 0
for d in all_details:
    key = f"{d['route_id']}_{d['route_seq']}"
    if key in route_stops:
        done += 1
        continue
    rs = api(f"/route-stop/{d['route_id']}/{d['route_seq']}")
    if rs:
        data = rs.get("data", {})
        raw_stops = data.get("route_stops", data)
        if isinstance(raw_stops, list):
            stops = []
            for s in raw_stops:
                stops.append({
                    "stop_seq": s.get("stop_seq"),
                    "stop_id": s.get("stop_id"),
                    "name_tc": s.get("name_tc", ""),
                    "name_en": s.get("name_en", ""),
                })
            route_stops[key] = stops
    done += 1
    if done % 50 == 0:
        # Incremental save
        with open(stops_file, "w", encoding="utf-8") as f:
            json.dump({
                "type": "GMBRouteStopList", "version": "1.0",
                "generated_timestamp": "",
                "data": route_stops,
            }, f, ensure_ascii=False)
        print(f"  Route stops: {done}/{total} (saved)", flush=True)
    time.sleep(0.05)

# Final save
with open(stops_file, "w", encoding="utf-8") as f:
    json.dump({
        "type": "GMBRouteStopList", "version": "1.0",
        "generated_timestamp": "",
        "data": route_stops,
    }, f, ensure_ascii=False)

print(f"\nDone! routes: {os.path.getsize(routes_file):,} bytes, stops: {os.path.getsize(stops_file):,} bytes", flush=True)
