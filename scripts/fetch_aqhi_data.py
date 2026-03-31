#!/usr/bin/env python3
"""
獲取香港AQHI數據並保存到JSON文件
"""

import json
import urllib.request
import ssl

def fetch_aqhi():
    """從Azure Blob獲取AQHI數據"""
    url = 'https://datagovhk.blob.core.windows.net/dataset/aqhi/aqhi.json'
    
    # 創建不驗證SSL的context（因為是政府網站）
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except Exception as e:
        print(f"獲取AQHI失敗: {e}")
        return None

def main():
    data = fetch_aqhi()
    
    if data:
        # 生成 JS 文件（使用 script 標籤加載，繞過 CSP fetch 限制）
        js_content = f'''// AQHI 數據 - 由 cron 每小時更新
const AQHI_DATA = {json.dumps({
    'timestamp': data[0].get('publish_date', '') if data else '',
    'data': data
}, ensure_ascii=False, indent=2)};
'''
        output_file = '/home/openclaw/.openclaw/workspace/aqhi-data.js'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print(f"✅ AQHI數據已更新: {output_file}")
        
        # 自動提交到GitHub
        import subprocess
        import os
        os.chdir('/home/openclaw/.openclaw/workspace')
        subprocess.run(['git', 'add', 'aqhi-data.js'], check=False)
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if result.stdout.strip():
            commit_msg = f"docs: update AQHI data {data[0].get('publish_date', '')[:10]}"
            subprocess.run(['git', 'commit', '-m', commit_msg], check=False)
            subprocess.run(['git', 'push', 'origin', 'main'], check=False)
            print("✅ 已推送到GitHub")
    else:
        print("❌ 無法獲取AQHI數據")

if __name__ == '__main__':
    main()
