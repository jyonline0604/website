#!/usr/bin/env python3
"""
檢查 av-novels.html 章節排序
章節應該按降序排列（最新章節在最前面）
"""

import re
import sys
from pathlib import Path

def check_av_sorting():
    """檢查 av-novels.html 的章節排序"""
    workspace = Path("/home/openclaw/.openclaw/workspace")
    av_path = workspace / "av-novels.html"
    
    if not av_path.exists():
        print(f"錯誤: 找不到 {av_path}")
        return False
    
    content = av_path.read_text(encoding='utf-8')
    
    # 提取所有章節號
    pattern = r'chapter-(\d+)-av\.html'
    matches = re.findall(pattern, content)
    
    if not matches:
        print("錯誤: 找不到任何章節")
        return False
    
    chapter_nums = [int(m) for m in matches]
    
    print(f"📊 檢查 av-novels.html 章節排序")
    print(f"   總章節數: {len(chapter_nums)}")
    print(f"   最新章節: 第{chapter_nums[0]}章")
    print(f"   最舊章節: 第{chapter_nums[-1]}章")
    
    # 檢查是否按降序排列
    is_sorted = all(chapter_nums[i] >= chapter_nums[i+1] for i in range(len(chapter_nums)-1))
    
    if is_sorted:
        print("✅ 章節按降序排列正確")
        return True
    else:
        print("❌ 章節排序錯誤！")
        
        # 找出所有錯誤
        errors = []
        for i in range(len(chapter_nums)-1):
            if chapter_nums[i] < chapter_nums[i+1]:
                errors.append((i, chapter_nums[i], chapter_nums[i+1]))
        
        print(f"   發現 {len(errors)} 個排序錯誤:")
        for i, a, b in errors[:5]:  # 只顯示前5個錯誤
            print(f"     位置 {i}: 第{a}章 在 第{b}章 之後 (應該在前面)")
        
        if len(errors) > 5:
            print(f"     ... 還有 {len(errors)-5} 個錯誤")
        
        return False

def main():
    """主函數"""
    print("🔍 檢查 AV 章節排序")
    print("=" * 50)
    
    if check_av_sorting():
        print("\n✅ 所有檢查通過")
        sys.exit(0)
    else:
        print("\n❌ 發現排序問題，請運行修復腳本")
        print("   建議運行: python3 scripts/generate_av_chapter.py --sort-only")
        sys.exit(1)

if __name__ == "__main__":
    main()