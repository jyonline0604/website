#!/usr/bin/env python3
"""
修復HTML文件中的div標籤平衡問題
"""
import re
import sys

def fix_div_balance(filename):
    """修復div標籤平衡問題"""
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 統計div標籤
    div_open = 0
    div_close = 0
    for line in lines:
        div_open += line.count('<div')
        div_close += line.count('</div>')
    
    print(f"文件: {filename}")
    print(f"div開啟: {div_open}, div關閉: {div_close}")
    
    if div_open == div_close:
        print("✅ div標籤已經平衡")
        return True
    
    diff = div_open - div_close
    print(f"❌ div標籤不匹配: 差 {diff} 個")
    
    if diff < 0:  # 多餘的關閉標籤
        print(f"需要刪除 {-diff} 個多餘的 </div>")
        
        # 嘗試找到並刪除多餘的關閉標籤
        new_lines = []
        removed = 0
        to_remove = -diff
        
        for line in lines:
            if removed < to_remove and '</div>' in line:
                # 刪除一個</div>
                new_line = line.replace('</div>', '', 1)
                new_lines.append(new_line)
                removed += 1
                print(f"  刪除了第{len(new_lines)}行的一個</div>")
            else:
                new_lines.append(line)
        
        # 寫回文件
        with open(filename, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print(f"✅ 已刪除 {removed} 個多餘的 </div>")
        
    else:  # 多餘的開啟標籤
        print(f"需要刪除 {diff} 個多餘的 <div")
        # 這裡可以實現刪除多餘開啟標籤的邏輯
    
    # 驗證修復
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_div_open = content.count('<div')
    new_div_close = content.count('</div>')
    
    print(f"修復後: div開啟: {new_div_open}, div關閉: {new_div_close}")
    
    if new_div_open == new_div_close:
        print("✅ 修復成功！div標籤現在平衡了")
        return True
    else:
        print("❌ 修復失敗，div標籤仍然不匹配")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 fix_div_balance.py <文件名>")
        sys.exit(1)
    
    filename = sys.argv[1]
    success = fix_div_balance(filename)
    sys.exit(0 if success else 1)