#!/usr/bin/env python3
"""
將favicon添加到所有HTML頁面
"""

import os
import re
import sys

WORKSPACE = "/home/openclaw/.openclaw/workspace"

def add_favicon_to_file(filepath):
    """向單個文件添加favicon鏈接"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查是否已經有favicon
        if 'favicon' in content.lower() or 'apple-touch-icon' in content.lower():
            print(f"  ℹ️ {os.path.basename(filepath)}: 已有favicon")
            return False
        
        # 查找<head>標籤後的位置
        head_match = re.search(r'<head[^>]*>', content)
        if not head_match:
            print(f"  ❌ {os.path.basename(filepath)}: 找不到<head>標籤")
            return False
        
        head_end = head_match.end()
        
        # favicon鏈接代碼
        favicon_code = '''
    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="assets/favicon.ico">
    <link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="assets/favicon-16x16.png">
    <link rel="apple-touch-icon" sizes="180x180" href="assets/apple-touch-icon.png">
    <link rel="manifest" href="assets/site.webmanifest">
    <meta name="theme-color" content="#1e293b">
'''
        
        # 插入favicon代碼
        new_content = content[:head_end] + favicon_code + content[head_end:]
        
        # 寫回文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"  ✅ {os.path.basename(filepath)}: 已添加favicon")
        return True
        
    except Exception as e:
        print(f"  ❌ {os.path.basename(filepath)}: 錯誤 - {e}")
        return False

def add_favicon_to_all_pages():
    """向所有HTML頁面添加favicon"""
    print("🔗 向所有HTML頁面添加favicon...")
    print("=" * 50)
    
    # 主要頁面
    main_pages = [
        "home.html", "chapters.html", "av-novels.html", 
        "news.html", "finance.html", "dashboard.html",
        "author.html", "index.html"
    ]
    
    updated_count = 0
    total_count = 0
    
    # 處理主要頁面
    for page in main_pages:
        filepath = os.path.join(WORKSPACE, page)
        if os.path.exists(filepath):
            total_count += 1
            if add_favicon_to_file(filepath):
                updated_count += 1
    
    # 處理章節頁面（批量處理，只顯示統計）
    print(f"\n📚 處理章節頁面...")
    chapter_files = []
    
    # 收集所有章節文件
    for filename in os.listdir(WORKSPACE):
        if filename.startswith("chapter-") and filename.endswith(".html"):
            filepath = os.path.join(WORKSPACE, filename)
            chapter_files.append(filepath)
    
    chapter_updated = 0
    for i, filepath in enumerate(chapter_files):
        total_count += 1
        if add_favicon_to_file(filepath):
            chapter_updated += 1
            updated_count += 1
        
        # 每處理50個文件顯示進度
        if (i + 1) % 50 == 0:
            print(f"  已處理 {i+1}/{len(chapter_files)} 個章節文件...")
    
    print(f"\n{'='*50}")
    print("📊 添加favicon完成！")
    print(f"• 總共處理文件: {total_count} 個")
    print(f"• 成功添加favicon: {updated_count} 個")
    print(f"• 章節文件更新: {chapter_updated} 個")
    print(f"• 主要頁面更新: {updated_count - chapter_updated} 個")
    
    if updated_count > 0:
        # 創建site.webmanifest文件
        create_webmanifest()
        return True
    else:
        print("⚠️ 沒有文件被更新")
        return False

def create_webmanifest():
    """創建PWA manifest文件"""
    manifest_path = os.path.join(WORKSPACE, "assets", "site.webmanifest")
    
    manifest_content = '''{
  "name": "科技修真傳",
  "short_name": "科技修真傳",
  "description": "融合科技與修真的AI生成小說",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#1e293b",
  "theme_color": "#1e293b",
  "icons": [
    {
      "src": "favicon-72x72.png",
      "sizes": "72x72",
      "type": "image/png"
    },
    {
      "src": "favicon-96x96.png",
      "sizes": "96x96",
      "type": "image/png"
    },
    {
      "src": "favicon-128x128.png",
      "sizes": "128x128",
      "type": "image/png"
    },
    {
      "src": "favicon-144x144.png",
      "sizes": "144x144",
      "type": "image/png"
    },
    {
      "src": "favicon-152x152.png",
      "sizes": "152x152",
      "type": "image/png"
    },
    {
      "src": "favicon-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "favicon-384x384.png",
      "sizes": "384x384",
      "type": "image/png"
    },
    {
      "src": "favicon-512x512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
'''
    
    try:
        with open(manifest_path, 'w', encoding='utf-8') as f:
            f.write(manifest_content)
        print("✅ 已創建: assets/site.webmanifest")
        
        # 創建缺失的圖標尺寸
        create_missing_icon_sizes()
        
    except Exception as e:
        print(f"⚠️ 無法創建manifest文件: {e}")

def create_missing_icon_sizes():
    """創建manifest中缺失的圖標尺寸"""
    from PIL import Image, ImageDraw, ImageFont
    
    assets_dir = os.path.join(WORKSPACE, "assets")
    sizes = [72, 96, 144, 152, 192, 384, 512]
    
    for size in sizes:
        filename = f"favicon-{size}x{size}.png"
        filepath = os.path.join(assets_dir, filename)
        
        if not os.path.exists(filepath):
            try:
                # 創建新圖片
                img = Image.new('RGBA', (size, size), (30, 41, 59, 255))
                draw = ImageDraw.Draw(img)
                
                # 根據尺寸調整文字
                if size >= 192:
                    text = "科技修真"
                    font_size = size // 6
                elif size >= 96:
                    text = "科修"
                    font_size = size // 3
                else:
                    text = "科"
                    font_size = size // 2
                
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
                except:
                    font = ImageFont.load_default()
                
                try:
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                except:
                    text_width, text_height = draw.textsize(text, font=font)
                
                x = (size - text_width) // 2
                y = (size - text_height) // 2
                
                draw.text((x, y), text, fill=(255, 215, 0, 255), font=font)
                img.save(filepath, 'PNG')
                print(f"  ✅ 創建缺失圖標: {filename}")
                
            except Exception as e:
                print(f"  ⚠️ 無法創建 {filename}: {e}")

if __name__ == "__main__":
    success = add_favicon_to_all_pages()
    sys.exit(0 if success else 1)