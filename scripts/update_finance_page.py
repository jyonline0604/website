#!/usr/bin/env python3
"""
更新財經頁面腳本
將模擬數據替換為真實API數據顯示
"""

import re

def update_finance_page():
    """更新財經頁面"""
    finance_file = '/home/openclaw/.openclaw/workspace/finance.html'
    
    print("📄 開始更新財經頁面...")
    
    with open(finance_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 添加新的JavaScript引用
    js_ref = '<script src="assets/finance.js"></script>'
    
    # 找到最後一個</script>標籤，在它之前插入
    last_script_pos = content.rfind('</script>')
    if last_script_pos != -1:
        insert_pos = last_script_pos + len('</script>')
        content = content[:insert_pos] + '\n    ' + js_ref + content[insert_pos:]
        print("✅ 添加JavaScript引用")
    
    # 2. 替換市場概況部分
    market_section = '''        <!-- 市場概況 -->
        <section class="market-overview">
            <div class="section-header">
                <h2>📈 市場概況</h2>
                <div class="section-controls">
                    <button id="refresh-data" class="btn-refresh">🔄 刷新數據</button>
                    <span class="last-update">最後更新: <span id="last-update-time">載入中...</span></span>
                </div>
            </div>
            
            <div id="error-message" style="display: none;"></div>
            
            <div class="market-grid">
                <!-- 加密貨幣 -->
                <div class="market-section">
                    <h3>🪙 加密貨幣</h3>
                    <div class="market-cards" id="crypto-data">
                        <!-- 由JavaScript動態生成 -->
                    </div>
                </div>
                
                <!-- 股票指數 -->
                <div class="market-section">
                    <h3>📊 股票指數</h3>
                    <div class="market-cards" id="stock-data">
                        <!-- 由JavaScript動態生成 -->
                    </div>
                </div>
                
                <!-- 商品 -->
                <div class="market-section">
                    <h3>🛢️ 商品</h3>
                    <div class="market-cards" id="commodity-data">
                        <!-- 由JavaScript動態生成 -->
                    </div>
                </div>
                
                <!-- 外匯 -->
                <div class="market-section">
                    <h3>💱 外匯</h3>
                    <div class="market-cards" id="forex-data">
                        <!-- 由JavaScript動態生成 -->
                    </div>
                </div>
                
                <!-- 債券 -->
                <div class="market-section">
                    <h3>📜 債券</h3>
                    <div class="market-cards" id="bond-data">
                        <!-- 由JavaScript動態生成 -->
                    </div>
                </div>
            </div>
            
            <!-- 市場情緒 -->
            <div class="market-sentiment-section">
                <h3>😊 市場情緒</h3>
                <div id="market-sentiment">
                    <!-- 由JavaScript動態生成 -->
                </div>
            </div>
        </section>'''
    
    # 找到市場概況部分並替換
    market_start = content.find('<!-- 市場概況 -->')
    if market_start != -1:
        # 找到下一個section的開始
        next_section = content.find('<section', market_start + 100)
        if next_section != -1:
            content = content[:market_start] + market_section + content[next_section:]
            print("✅ 更新市場概況部分")
    
    # 3. 更新財經新聞部分
    news_section = '''        <!-- 財經新聞 -->
        <section class="finance-news">
            <div class="section-header">
                <h2>📰 最新財經新聞</h2>
                <div class="news-count">共 <span id="news-count">0</span> 條新聞</div>
            </div>
            
            <div class="news-container" id="finance-news">
                <!-- 由JavaScript動態生成 -->
            </div>
            
            <div class="news-footer">
                <p>新聞來源: Reuters, Bloomberg, CNBC, CoinDesk, CryptoSlate</p>
                <p>更新頻率: 每小時自動更新</p>
            </div>
        </section>'''
    
    # 找到財經新聞部分並替換
    news_start = content.find('<!-- 加密貨幣新聞 -->')
    if news_start != -1:
        # 找到下一個section的開始
        next_section = content.find('<section', news_start + 100)
        if next_section != -1:
            content = content[:news_start] + news_section + content[next_section:]
            print("✅ 更新財經新聞部分")
    
    # 4. 添加CSS樣式
    css_start = content.find('</style>')
    if css_start != -1:
        additional_css = '''
        /* 財經數據樣式 */
        .market-overview {
            margin-bottom: 40px;
        }
        
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--border);
        }
        
        .section-controls {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .btn-refresh {
            background: var(--accent);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: background 0.2s;
        }
        
        .btn-refresh:hover {
            background: var(--accent-light);
        }
        
        .btn-refresh:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .last-update {
            color: var(--text-secondary);
            font-size: 0.9rem;
        }
        
        .market-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .market-section {
            background: var(--bg-secondary);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid var(--border);
        }
        
        .market-section h3 {
            margin-top: 0;
            margin-bottom: 15px;
            color: var(--text-primary);
            font-size: 1.1rem;
        }
        
        .market-cards {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .market-card {
            background: var(--bg-tertiary);
            border-radius: 8px;
            padding: 15px;
            border-left: 4px solid var(--accent);
        }
        
        .market-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .market-header h3 {
            margin: 0;
            font-size: 1rem;
            color: var(--text-primary);
        }
        
        .market-category {
            background: var(--accent-light);
            color: var(--accent);
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
        }
        
        .market-price {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 5px;
        }
        
        .market-change {
            font-size: 0.9rem;
            margin-bottom: 10px;
        }
        
        .change-positive {
            color: #10b981;
        }
        
        .change-negative {
            color: #ef4444;
        }
        
        .market-details {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            font-size: 0.85rem;
        }
        
        .market-detail {
            display: flex;
            justify-content: space-between;
        }
        
        .detail-label {
            color: var(--text-secondary);
        }
        
        .detail-value {
            color: var(--text-primary);
            font-weight: 500;
        }
        
        .market-sentiment-section {
            background: var(--bg-secondary);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid var(--border);
            margin-top: 20px;
        }
        
        .sentiment-card {
            background: var(--bg-tertiary);
            border-radius: 8px;
            padding: 20px;
            border-left: 4px solid #666666;
        }
        
        .sentiment-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .sentiment-header h3 {
            margin: 0;
            font-size: 1.1rem;
        }
        
        .sentiment-label {
            font-weight: 700;
            font-size: 1rem;
        }
        
        .sentiment-meter {
            margin-bottom: 15px;
        }
        
        .meter-bar {
            height: 10px;
            background: var(--bg-secondary);
            border-radius: 5px;
            overflow: hidden;
            margin-bottom: 5px;
        }
        
        .meter-fill {
            height: 100%;
            border-radius: 5px;
            transition: width 0.5s ease;
        }
        
        .meter-labels {
            display: flex;
            justify-content: space-between;
            font-size: 0.8rem;
            color: var(--text-secondary);
        }
        
        .sentiment-index {
            font-size: 2rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 10px;
        }
        
        .sentiment-description {
            text-align: center;
            color: var(--text-secondary);
            margin-bottom: 10px;
            font-size: 0.9rem;
        }
        
        .sentiment-update {
            text-align: center;
            font-size: 0.8rem;
            color: var(--text-tertiary);
        }
        
        /* 財經新聞樣式 */
        .finance-news {
            margin-bottom: 40px;
        }
        
        .news-count {
            color: var(--text-secondary);
            font-size: 0.9rem;
        }
        
        .news-container {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .news-item {
            background: var(--bg-secondary);
            border-radius: 8px;
            padding: 20px;
            border: 1px solid var(--border);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .news-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            border-color: var(--accent);
        }
        
        .news-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 10px;
        }
        
        .news-header h4 {
            margin: 0;
            font-size: 1rem;
            color: var(--text-primary);
            flex: 1;
        }
        
        .news-source {
            background: var(--accent-light);
            color: var(--accent);
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            margin-left: 10px;
        }
        
        .news-summary {
            color: var(--text-secondary);
            font-size: 0.9rem;
            line-height: 1.5;
            margin-bottom: 10px;
        }
        
        .news-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.85rem;
        }
        
        .news-category {
            background: var(--bg-tertiary);
            color: var(--text-secondary);
            padding: 2px 8px;
            border-radius: 4px;
        }
        
        .news-time {
            color: var(--text-tertiary);
        }
        
        .news-link {
            color: var(--accent);
            text-decoration: none;
        }
        
        .news-link:hover {
            text-decoration: underline;
        }
        
        .news-footer {
            color: var(--text-secondary);
            font-size: 0.9rem;
            text-align: center;
            margin-top: 20px;
        }
        
        /* 錯誤消息樣式 */
        .error-message {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .error-icon {
            font-size: 1.2rem;
        }
        
        .error-text {
            color: #ef4444;
        }
        
        /* 更新通知 */
        .update-notification {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: var(--accent);
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 1000;
            animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        /* 響應式設計 */
        @media (max-width: 768px) {
            .section-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }
            
            .section-controls {
                width: 100%;
                justify-content: space-between;
            }
            
            .market-grid {
                grid-template-columns: 1fr;
            }
            
            .news-header {
                flex-direction: column;
                gap: 5px;
            }
            
            .news-source {
                align-self: flex-start;
                margin-left: 0;
            }
            
            .news-footer {
                flex-direction: column;
                gap: 5px;
                align-items: flex-start;
            }
        }'''
        
        content = content[:css_start] + additional_css + content[css_start:]
        print("✅ 添加CSS樣式")
    
    # 5. 移除舊的JavaScript代碼（模擬數據更新）
    # 找到舊的updateMarketData函數並移除
    old_js_start = content.find('// 簡單的市場數據更新（模擬）')
    if old_js_start != -1:
        old_js_end = content.find('// 投資計算器功能', old_js_start)
        if old_js_end != -1:
            content = content[:old_js_start] + content[old_js_end:]
            print("✅ 移除舊的模擬數據JavaScript")
    
    # 保存更新後的內容
    with open(finance_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 財經頁面更新完成")
    return True

if __name__ == '__main__':
    try:
        if update_finance_page():
            print("🎉 財經頁面已成功更新為使用真實API數據")
        else:
            print("❌ 財經頁面更新失敗")
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()