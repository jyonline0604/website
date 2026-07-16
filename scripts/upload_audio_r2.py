#!/usr/bin/env python3
"""
upload_audio_r2.py — 上傳 MP3 到 Cloudflare R2
使用 S3 兼容 API (SigV4 簽名，無需 boto3)

Usage:
  python3 scripts/upload_audio_r2.py chapter-1.mp3              # 單個
  python3 scripts/upload_audio_r2.py --batch ./mp3_output/       # 批次
  python3 scripts/upload_audio_r2.py --list                       # 列出 bucket 內容
  python3 scripts/upload_audio_r2.py --delete chapter-1.mp3       # 刪除
"""

import hashlib
import hmac
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

CRED_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".r2-credentials.json")
PREFIX = "audio/"  # R2 入面嘅 folder


def load_creds():
    with open(CRED_FILE, "r") as f:
        return json.load(f)


def sign_request(creds, method, path, body=None, content_type=None):
    """生成 SigV4 簽名 headers"""
    account_id = creds["account_id"]
    access_key = creds["access_key_id"]
    secret_key = creds["secret_access_key"]
    bucket = creds["bucket"]
    region = "auto"
    service = "s3"

    host = f"{bucket}.{account_id}.r2.cloudflarestorage.com"
    t = datetime.now(timezone.utc)
    amz_date = t.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = t.strftime("%Y%m%d")

    payload_hash = hashlib.sha256(body or b"").hexdigest()

    canonical_headers = (
        f"host:{host}\n"
        f"x-amz-content-sha256:{payload_hash}\n"
        f"x-amz-date:{amz_date}\n"
    )
    signed_headers = "host;x-amz-content-sha256;x-amz-date"

    canonical_request = (
        f"{method}\n{path}\n\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
    )
    scope = f"{date_stamp}/{region}/{service}/aws4_request"
    string_to_sign = (
        f"AWS4-HMAC-SHA256\n{amz_date}\n{scope}\n"
        f"{hashlib.sha256(canonical_request.encode()).hexdigest()}"
    )

    def sign(key, msg):
        return hmac.new(key, msg.encode(), hashlib.sha256).digest()

    k_date = sign(("AWS4" + secret_key).encode(), date_stamp)
    k_region = sign(k_date, region)
    k_service = sign(k_region, service)
    k_signing = sign(k_service, "aws4_request")
    signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()

    auth = (
        f"AWS4-HMAC-SHA256 Credential={access_key}/{scope},"
        f"SignedHeaders={signed_headers},Signature={signature}"
    )

    headers = {
        "Authorization": auth,
        "x-amz-date": amz_date,
        "x-amz-content-sha256": payload_hash,
    }
    if content_type:
        headers["Content-Type"] = content_type
    if body:
        headers["Content-Length"] = str(len(body))

    return f"https://{host}{path}", headers


def upload_file(filepath, creds):
    """上傳單個文件"""
    if not os.path.exists(filepath):
        print(f"❌ 檔案唔存在: {filepath}")
        return False

    filename = os.path.basename(filepath)
    # 標準化命名: chapter-{num}.mp3
    r2_path = f"/{PREFIX}{filename}"

    with open(filepath, "rb") as f:
        body = f.read()

    file_size = len(body)
    url, headers = sign_request(creds, "PUT", r2_path, body, "audio/mpeg")

    print(f"📤 上傳中: {filename} ({file_size / 1024 / 1024:.1f} MB) ...", end=" ")

    try:
        req = urllib.request.Request(url, data=body, method="PUT")
        for k, v in headers.items():
            req.add_header(k, v)
        with urllib.request.urlopen(req) as resp:
            status = resp.status
        if status == 200:
            public_url = f"https://audio.kofhk.com/{PREFIX}{filename}"
            print(f"✅ 完成!")
            print(f"   🔗 {public_url}")
            return public_url
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP {e.code}: {e.read().decode()[:200]}")
        return None
    return None


def batch_upload(dirpath, creds, pattern=".mp3"):
    """批次上傳目錄中所有 MP3"""
    import glob
    files = sorted(glob.glob(os.path.join(dirpath, f"*{pattern}")))
    if not files:
        print(f"❌ 搵唔到 {pattern} 檔案喺: {dirpath}")
        return

    print(f"📂 批次上傳 {len(files)} 個檔案...")
    results = []
    for f in files:
        url = upload_file(f, creds)
        if url:
            results.append((os.path.basename(f), url))
    
    print(f"\n✅ 完成: {len(results)}/{len(files)} 成功")
    if results:
        print("\n上傳清單:")
        for name, url in results:
            print(f"  • {name} → {url}")


def list_objects(creds):
    """列出 bucket 中 audio/* 嘅檔案"""
    path = "/"
    query = "prefix=audio%2F"
    url, headers = sign_request(creds, "GET", f"{path}?{query}")

    try:
        req = urllib.request.Request(url)
        for k, v in headers.items():
            req.add_header(k, v)
        with urllib.request.urlopen(req) as resp:
            data = resp.read().decode()
        
        # 簡單 XML parsing（R2 返回 S3 格式 XML）
        import xml.etree.ElementTree as ET
        root = ET.fromstring(data)
        ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
        
        objects = []
        for obj in root.findall(".//s3:Contents", ns):
            key = obj.find("s3:Key", ns).text
            size = int(obj.find("s3:Size", ns).text)
            size_mb = size / 1024 / 1024
            objects.append((key, f"{size_mb:.2f} MB"))
        
        total = sum(float(s.split()[0]) for _, s in objects)
        print(f"📋 Bucket: audio/ ({len(objects)} files, {total:.1f} MB total)\n")
        for key, size in sorted(objects):
            print(f"  • {key} ({size})")
        print(f"\n  Total: {total:.1f} MB")
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP {e.code}: {e.read().decode()[:200]}")


def delete_object(filename, creds):
    """刪除某個檔案"""
    r2_path = f"/{PREFIX}{filename}"
    url, headers = sign_request(creds, "DELETE", r2_path)
    
    try:
        req = urllib.request.Request(url, method="DELETE")
        for k, v in headers.items():
            req.add_header(k, v)
        with urllib.request.urlopen(req) as resp:
            print(f"🗑️  已刪除: {PREFIX}{filename}")
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP {e.code}: {e.read().decode()[:200]}")


if __name__ == "__main__":
    creds = load_creds()

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    if sys.argv[1] == "--list":
        list_objects(creds)
    elif sys.argv[1] == "--batch":
        dirpath = sys.argv[2] if len(sys.argv) > 2 else "."
        batch_upload(dirpath, creds)
    elif sys.argv[1] == "--delete":
        if len(sys.argv) < 3:
            print("Usage: upload_audio_r2.py --delete <filename>")
            sys.exit(1)
        delete_object(sys.argv[2], creds)
    else:
        upload_file(sys.argv[1], creds)
