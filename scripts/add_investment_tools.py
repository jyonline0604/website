#!/usr/bin/env python3
"""
將投資工具添加到財經頁面
"""

def add_investment_tools():
    """添加投資工具部分到財經頁面"""
    finance_file = '/home/openclaw/.openclaw/workspace/my-novel/finance.html'
    tools_file = '/home/openclaw/.openclaw/workspace/my-novel/assets/investment-tools.html'
    
    print("🛠️ 開始添加投資工具到財經頁面...")
    
    # 讀取投資工具HTML
    with open(tools_file, 'r', encoding='utf-8') as f:
        tools_html = f.read()
    
    # 讀取財經頁面
    with open(finance_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到財經新聞部分之後的位置
    news_end = content.find('</section>', content.find('<!-- 財經新聞 -->'))
    if news_end == -1:
        print("❌ 找不到財經新聞部分")
        return False
    
    # 在財經新聞部分之後插入投資工具
    insert_pos = news_end + len('</section>')
    new_content = content[:insert_pos] + '\n\n' + tools_html + content[insert_pos:]
    
    # 添加JavaScript引用
    js_ref = '<script src="assets/investment-calculator.js"></script>'
    last_script_pos = new_content.rfind('</script>')
    if last_script_pos != -1:
        insert_js_pos = last_script_pos + len('</script>')
        new_content = new_content[:insert_js_pos] + '\n    ' + js_ref + new_content[insert_js_pos:]
    
    # 添加Chart.js CDN（如果未存在）
    if 'cdn.jsdelivr.net/npm/chart.js' not in new_content:
        chartjs_ref = '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>'
        new_content = new_content.replace(js_ref, chartjs_ref + '\n    ' + js_ref)
    
    # 保存更新後的內容
    with open(finance_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ 投資工具已添加到財經頁面")
    return True

if __name__ == '__main__':
    try:
        if add_investment_tools():
            print("🎉 財經頁面投資工具添加完成")
        else:
            print("❌ 投資工具添加失敗")
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()