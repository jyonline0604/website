#!/usr/bin/env python3
"""Convert images to WebP using ffmpeg with multiprocessing."""

import os
import re
import subprocess
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

BASE = Path('/opt/data/website')
ASSETS_DIR = BASE / 'assets'

SKIP_DIRS = {'seedream_output', '.git'}

def convert_one(args):
    """Convert a single image to WebP."""
    img_path, quality = args
    
    webp_path = img_path.with_suffix('.webp')
    
    # Skip if already exists
    if webp_path.exists():
        return None  # Already done
    
    try:
        cmd = [
            'ffmpeg', '-y', '-i', str(img_path),
            '-c:v', 'libwebp',
            '-q', str(quality),
            str(webp_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and webp_path.exists():
            orig_size = img_path.stat().st_size
            new_size = webp_path.stat().st_size
            savings = ((orig_size - new_size) / orig_size * 100) if orig_size > 0 else 0
            return (img_path, orig_size, new_size, savings)
        else:
            return None
    except Exception as e:
        print(f"ERROR: {img_path.name} -> {e}")
        return None

def find_image_files():
    """Find all image files in assets directory."""
    images = []
    
    for ext in ['*.jpg', '*.jpeg', '*.png']:
        for f in ASSETS_DIR.rglob(ext):
            rel = f.relative_to(BASE)
            skip = False
            for skip_dir in SKIP_DIRS:
                if str(rel).startswith(skip_dir + '/') or skip_dir in rel.parts:
                    skip = True
                    break
            if not skip:
                images.append(f)
    
    return sorted(images)

def main():
    images = find_image_files()
    print(f"Found {len(images)} images to convert")
    
    # Prepare args (quality 85 is good balance)
    tasks = [(img, 85) for img in images]
    
    converted = []
    failed = 0
    
    # Use 4 workers for parallel conversion
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(convert_one, task): task[0] for task in tasks}
        
        total = len(futures)
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            if result:
                img_path, orig_size, new_size, savings = result
                converted.append(result)
                print(f"[{i}/{total}] {img_path.name}: {orig_size/1024:.0f}KB -> {new_size/1024:.0f}KB ({savings:.0f}% saved)")
            else:
                failed += 1
    
    # Summary
    total_orig = sum(r[1] for r in converted)
    total_new = sum(r[2] for r in converted)
    total_savings = ((total_orig - total_new) / total_orig * 100) if total_orig > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"Conversion complete!")
    print(f"  Converted: {len(converted)}")
    print(f"  Failed/Skipped: {failed}")
    print(f"  Original size: {total_orig/1024/1024:.1f} MB")
    print(f"  New size: {total_new/1024/1024:.1f} MB")
    print(f"  Total savings: {total_savings:.0f}% ({(total_orig - total_new)/1024/1024:.1f} MB)")

if __name__ == '__main__':
    main()
