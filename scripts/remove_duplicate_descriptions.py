#!/usr/bin/env python3
"""
刪除重複的meta description標籤
"""

import os
import re
import sys

WORKSPACE = "/home/openclaw/.openclaw/workspace"

def remove_duplicate_descriptions(filepath):
    """刪除文件中的重複description標籤"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找所有description標籤
        pattern = r'<meta name="description" content="[^"]*">'
        matches = list(re.finditer(pattern, content))
        
        if len(matches) <= 1:
            return False  # 沒有重複
        
        # 保留第一個，刪除其他
        first_match = matches[0]
        to_remove = matches[1:]
        
        # 從後往前刪除，避免位置變化
        new_content = content
        for match in reversed(to_remove):
            new_content = new_content[:match.start()] + new_content[match.end():]
        
        # 寫回文件
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            filename = os.path.basename(filepath)
            print(f"  ✅ {filename}: 刪除了 {len(to_remove)} 個重複標籤")
            return True
        
        return False
        
    except Exception as e:
        filename = os.path.basename(filepath) if 'filepath' in locals() else '未知文件'
        print(f"  ❌ {filename}: 錯誤 - {e}")
        return False

def main():
    print("🧹 清理重複的meta description標籤...")
    print("=" * 60)
    
    # 處理所有HTML文件
    html_files = []
    for filename in os.listdir(WORKSPACE):
        if filename.endswith(".html"):
            filepath = os.path.join(WORKSPACE, filename)
            html_files.append(filepath)
    
    total_files = len(html_files)
    cleaned_count = 0
    
    for i, filepath in enumerate(html_files):
        if remove_duplicate_descriptions(filepath):
            cleaned_count += 1
        
        # 顯示進度
        if (i + 1) % 50 == 0:
            print(f"  已處理 {i+1}/{total_files} 個文件...")
    
    print(f"\n{'='*60}")
    print("📊 清理完成！")
    print(f"• 總共處理文件: {total_files} 個")
    print(f"• 清理重複標籤: {cleaned_count} 個")
    
    return cleaned_count > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)