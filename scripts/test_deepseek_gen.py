#!/usr/bin/env python3
"""
測試DeepSeek生成腳本
生成第67章測試內容
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 導入DeepSeek生成函數
from generate_chapter_deepseek import (
    get_api_key, get_previous_chapters_context, 
    generate_with_deepseek, log
)

def test_deepseek_generation():
    """測試DeepSeek生成"""
    print("=== 測試DeepSeek V3.2生成能力 ===")
    
    # 檢查API密鑰
    api_key = get_api_key()
    if not api_key:
        print("❌ 未找到API密鑰")
        return False
    
    print("✅ API密鑰找到")
    
    # 測試章節號
    test_chapter = 67
    
    # 獲取上下文
    print(f"獲取第{test_chapter}章的前情提要...")
    context = get_previous_chapters_context(test_chapter, 2)
    print(f"上下文長度: {len(context)} 字符")
    print(f"前情提要:\n{context[:500]}...\n")
    
    # 測試生成
    print(f"測試生成第{test_chapter}章內容...")
    content, title = generate_with_deepseek(test_chapter, context)
    
    if content and title:
        print(f"✅ 生成成功！")
        print(f"標題: {title}")
        print(f"內容長度: {len(content)} 字符")
        print(f"內容預覽:\n{content[:300]}...")
        
        # 分析內容質量
        keywords = ["林塵", "靈芯", "火種", "修真", "科技", "能量", "系統"]
        keyword_count = sum(content.count(keyword) for keyword in keywords)
        print(f"\n關鍵詞出現次數: {keyword_count}")
        
        # 段落分析
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        print(f"段落數量: {len(paragraphs)}")
        
        if len(content) >= 1000:
            print("✅ 內容長度符合要求 (≥1000字符)")
        else:
            print("⚠️ 內容可能偏短")
            
        return True
    else:
        print("❌ 生成失敗")
        return False

if __name__ == "__main__":
    success = test_deepseek_generation()
    sys.exit(0 if success else 1)