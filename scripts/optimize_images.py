#!/usr/bin/env python3
"""
優化網站圖片大小
"""
import os
import subprocess

workspace = "/home/openclaw/.openclaw/workspace"
os.chdir(workspace)

def check_image_optimization_tools():
    """檢查圖片優化工具是否可用"""
    tools = ['convert', 'cwebp', 'optipng', 'jpegoptim']
    available = []
    
    for tool in tools:
        try:
            subprocess.run([tool, '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            available.append(tool)
        except:
            pass
    
    return available

def optimize_image(filepath, max_size_kb=500):
    """優化單個圖片文件"""
    if not os.path.exists(filepath):
        return False, "文件不存在"
    
    # 檢查文件大小
    size_kb = os.path.getsize(filepath) / 1024
    
    if size_kb <= max_size_kb:
        return False, f"文件大小合適 ({size_kb:.1f}KB)"
    
    filename = os.path.basename(filepath)
    ext = os.path.splitext(filename)[1].lower()
    
    try:
        if ext == '.jpg' or ext == '.jpeg':
            # 使用 jpegoptim 優化
            cmd = ['jpegoptim', '--max=90', '--strip-all', '--all-progressive', filepath]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                new_size_kb = os.path.getsize(filepath) / 1024
                return True, f"JPG優化成功: {size_kb:.1f}KB → {new_size_kb:.1f}KB"
        
        elif ext == '.png':
            # 使用 optipng 優化
            cmd = ['optipng', '-o2', '-strip', 'all', filepath]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                new_size_kb = os.path.getsize(filepath) / 1024
                return True, f"PNG優化成功: {size_kb:.1f}KB → {new_size_kb:.1f}KB"
        
        elif ext == '.webp':
            # WebP 已經比較優化，可以嘗試重新壓縮
            # 但需要謹慎，因為可能已經是最佳狀態
            return False, f"WebP文件 ({size_kb:.1f}KB)，建議保持原狀"
        
        else:
            return False, f"不支持的格式: {ext}"
    
    except Exception as e:
        return False, f"優化失敗: {str(e)}"
    
    return False, "未知錯誤"

def main():
    """主程序"""
    print("=" * 80)
    print("網站圖片優化檢查")
    print("=" * 80)
    
    # 檢查工具
    tools = check_image_optimization_tools()
    print(f"可用工具: {', '.join(tools) if tools else '無'}")
    print()
    
    # 查找大圖片
    large_images = []
    for root, dirs, files in os.walk('assets'):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                filepath = os.path.join(root, file)
                size_kb = os.path.getsize(filepath) / 1024
                if size_kb > 500:  # 大於500KB
                    large_images.append((filepath, size_kb))
    
    if not large_images:
        print("✅ 沒有發現過大的圖片文件")
        return
    
    print(f"發現 {len(large_images)} 個大圖片文件 (>500KB):")
    print()
    
    optimized_count = 0
    skipped_count = 0
    
    for filepath, size_kb in sorted(large_images, key=lambda x: x[1], reverse=True):
        print(f"📷 {filepath}")
        print(f"   大小: {size_kb:.1f}KB")
        
        # 嘗試優化
        success, message = optimize_image(filepath)
        
        if success:
            print(f"   ✅ {message}")
            optimized_count += 1
        else:
            print(f"   ⏭️ {message}")
            skipped_count += 1
        
        print()
    
    print("=" * 80)
    print("優化總結")
    print("=" * 80)
    print(f"總大圖片數: {len(large_images)}")
    print(f"優化成功: {optimized_count}")
    print(f"跳過: {skipped_count}")
    print()
    
    if not tools:
        print("⚠️ 建議安裝圖片優化工具:")
        print("  sudo apt-get install imagemagick webp optipng jpegoptim")
    else:
        print("✅ 圖片優化完成")

if __name__ == "__main__":
    main()