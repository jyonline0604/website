#!/usr/bin/env python3
"""
創建簡單的favicon圖標
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_favicon():
    """創建favicon圖標"""
    assets_dir = "/home/openclaw/.openclaw/workspace/assets"
    
    # 確保assets目錄存在
    os.makedirs(assets_dir, exist_ok=True)
    
    # 創建多種尺寸的favicon
    sizes = [(16, 16), (32, 32), (64, 64), (128, 128), (256, 256)]
    
    for size in sizes:
        # 創建新圖片
        img = Image.new('RGBA', size, (30, 41, 59, 255))  # 深藍背景
        draw = ImageDraw.Draw(img)
        
        # 根據尺寸調整文字大小
        if size[0] >= 64:
            # 大圖標：顯示「科修」兩個字
            try:
                # 嘗試加載字體
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size[0] // 2)
                text = "科修"
            except:
                # 如果字體不存在，使用默認
                font = ImageFont.load_default()
                text = "KX" if size[0] >= 32 else "K"
        else:
            # 小圖標：只顯示「科」或字母
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size[0] - 4)
                text = "科" if size[0] >= 32 else "K"
            except:
                font = ImageFont.load_default()
                text = "K"
        
        # 計算文字位置（居中）
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except:
            # 舊版PIL兼容
            text_width, text_height = draw.textsize(text, font=font)
        
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        # 繪製文字（金色）
        draw.text((x, y), text, fill=(255, 215, 0, 255), font=font)  # 金色文字
        
        # 保存圖片
        filename = f"favicon-{size[0]}x{size[1]}.png"
        filepath = os.path.join(assets_dir, filename)
        img.save(filepath, 'PNG')
        print(f"✅ 創建: {filename}")
    
    # 創建ICO文件（兼容舊瀏覽器）
    try:
        # 加載32x32圖標
        icon_32 = Image.open(os.path.join(assets_dir, "favicon-32x32.png"))
        
        # 創建ICO文件（包含多種尺寸）
        icon_32.save(os.path.join(assets_dir, "favicon.ico"), format='ICO', sizes=[(16, 16), (32, 32)])
        print("✅ 創建: favicon.ico")
    except Exception as e:
        print(f"⚠️ 無法創建ICO文件: {e}")
    
    # 創建Apple Touch圖標
    apple_size = (180, 180)
    apple_img = Image.new('RGBA', apple_size, (30, 41, 59, 255))
    apple_draw = ImageDraw.Draw(apple_img)
    
    try:
        apple_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        apple_text = "科修"
    except:
        apple_font = ImageFont.load_default()
        apple_text = "KX"
    
    try:
        bbox = apple_draw.textbbox((0, 0), apple_text, font=apple_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except:
        text_width, text_height = apple_draw.textsize(apple_text, font=apple_font)
    
    x = (apple_size[0] - text_width) // 2
    y = (apple_size[1] - text_height) // 2
    
    apple_draw.text((x, y), apple_text, fill=(255, 215, 0, 255), font=apple_font)
    apple_img.save(os.path.join(assets_dir, "apple-touch-icon.png"), 'PNG')
    print("✅ 創建: apple-touch-icon.png")
    
    print(f"\n🎉 Favicon創建完成！保存在: {assets_dir}/")
    return True

if __name__ == "__main__":
    create_favicon()