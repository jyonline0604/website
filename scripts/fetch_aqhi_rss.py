#!/usr/bin/env python3
"""
Fetch AQHI per-station data from EPD RSS feed and output JSON.
Parse from raw bytes to avoid encoding issues on Windows.
"""

import json
import re
import ssl
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

RSS_URL = "https://www.aqhi.gov.hk/epd/ddata/html/out/aqhi_ind_rss_ChT.xml"
OUTPUT_FILE = "aqhi-stations.json"


def parse_station(item):
    title_el = item.find("title")
    desc_el = item.find("description")
    if title_el is None or desc_el is None:
        return None
    name = (title_el.text or "").strip()
    desc = (desc_el.text or "").strip()
    m = re.search(r"(\u4e00\u822c\u76e3\u6e2c\u7ad9|\u8def\u908a\u76e3\u6e2c\u7ad9)\s*:\s*(\d+)\s*(\S+)", desc)
    if not m:
        return None
    stype = "general" if "\u4e00\u822c" in m.group(1) else "roadside"
    return {"name": name, "type": stype, "aqhi": int(m.group(2)), "risk": m.group(3)}


def risk_label(vals):
    if not vals:
        return None, None, "-"
    mn, mx = min(vals), max(vals)
    if mx <= 3:
        r = "Low"
    elif mx <= 6:
        r = "Moderate"
    elif mx <= 7:
        r = "High"
    elif mx <= 10:
        r = "Very High"
    else:
        r = "Serious"
    return mn, mx, r


def main():
    script_dir = Path(__file__).resolve().parent
    output_path = script_dir.parent / OUTPUT_FILE

    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(
            RSS_URL, headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            raw = resp.read()
    except Exception as e:
        print(f"Error fetching RSS: {e}", file=sys.stderr)
        sys.exit(1)

    root = ET.fromstring(raw)
    channel = root.find("channel")
    if channel is None:
        print("No <channel> in RSS", file=sys.stderr)
        sys.exit(1)

    pub_el = channel.find("pubDate")
    pub_date = (pub_el.text or "").strip() if pub_el is not None else ""

    stations = []
    for item in channel.findall("item"):
        s = parse_station(item)
        if s:
            stations.append(s)

    gv = [s["aqhi"] for s in stations if s["type"] == "general"]
    rv = [s["aqhi"] for s in stations if s["type"] == "roadside"]
    g_min, g_max, g_risk = risk_label(gv)
    r_min, r_max, r_risk = risk_label(rv)

    output = {
        "timestamp": pub_date,
        "updated": datetime.now().isoformat(),
        "summary": {
            "general": {
                "aqhi_min": g_min,
                "aqhi_max": g_max,
                "health_risk": g_risk,
            },
            "roadside": {
                "aqhi_min": r_min,
                "aqhi_max": r_max,
                "health_risk": r_risk,
            },
        },
        "stations": stations,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Wrote {len(stations)} stations to {output_path}")
    print(f"  General: {g_min}-{g_max} ({g_risk})")
    print(f"  Roadside: {r_min}-{r_max} ({r_risk})")


if __name__ == "__main__":
    main()
