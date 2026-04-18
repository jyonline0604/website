#!/usr/bin/env python3
"""
修復meta description中的CSS代碼問題
"""

import os
import re
import sys

WORKSPACE = "/home/openclaw/.openclaw/workspace"

def clean_description(description):
    """清理description中的CSS代碼"""
    # 移除CSS變量等內容
    cleaned = re.sub(r':root\s*\{[^}]*\}', '', description)
    cleaned = re.sub(r'\[data-theme="[^"]*"\]\s*\{[^}]*\}', '', cleaned)
    cleaned = re.sub(r'--[a-z-]+:\s*[^;]+;', '', cleaned)
    cleaned = re.sub(r'#[0-9A-Fa-f]{3,6}', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    # 如果清理後太短，使用默認描述
    if len(cleaned) < 50:
        # 嘗試提取章節號和標題
        match = re.search(r'第(\d+)章[：:]?\s*(.*?)《', description)
        if match:
            chapter_num = match.group(1)
            title = match.group(2) if match.group(2) else ""
            cleaned = f"《科技修真傳》第{chapter_num}章：{title}。免費閱讀完整章節，體驗融合科技與修真的奇幻小說。作者：大肥喵。"
        else:
            cleaned = "《科技修真傳》 - 融合科技與修真的AI生成小說。每日更新，免費閱讀完整章節。作者：大肥喵。"
    
    # 確保長度合理
    if len(cleaned) > 160:
        cleaned = cleaned[:157] + "..."
    
    return cleaned

def fix_file_descriptions(filepath):
    """修復單個文件的meta description"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找meta description
        pattern = r'<meta name="description" content="([^"]*)">'
        match = re.search(pattern, content)
        
        if not match:
            return False  # 沒有description
        
        old_description = match.group(1)
        new_description = clean_description(old_description)
        
        if old_description == new_description:
            return False  # 無需修改
        
        # 替換description
        new_content = content.replace(
            f'<meta name="description" content="{old_description}">',
            f'<meta name="description" content="{new_description}">'
        )
        
        # 寫回文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        filename = os.path.basename(filepath)
        print(f"  ✅ {filename}: 已修復")
        return True
        
    except Exception as e:
        filename = os.path.basename(filepath) if 'filepath' in locals() else '未知文件'
        print(f"  ❌ {filename}: 錯誤 - {e}")
        return False

def main():
    print("🔧 修復meta description中的CSS代碼問題...")
    print("=" * 60)
    
    # 處理所有HTML文件
    html_files = []
    for filename in os.listdir(WORKSPACE):
        if filename.endswith(".html"):
            filepath = os.path.join(WORKSPACE, filename)
            html_files.append(filepath)
    
    total_files = len(html_files)
    fixed_count = 0
    
    for i, filepath in enumerate(html_files):
        if fix_file_descriptions(filepath):
            fixed_count += 1
        
        # 顯示進度
        if (i + 1) % 50 == 0:
            print(f"  已處理 {i+1}/{total_files} 個文件...")
    
    print(f"\n{'='*60}")
    print("📊 修復完成！")
    print(f"• 總共處理文件: {total_files} 個")
    print(f"• 修復description: {fixed_count} 個")
    
    # 顯示修復前後對比
    print(f"\n📋 修復前後對比:")
    if html_files:
        sample_file = html_files[0]
        try:
            with open(sample_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            pattern = r'<meta name="description" content="([^"]*)">'
            match = re.search(pattern, content)
            if match:
                description = match.group(1)
                print(f"  修復後: {description[:80]}...")
        except:
            pass
    
    return fixed_count > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)