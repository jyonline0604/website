/**
 * 財經數據處理JavaScript
 * 從本地JSON文件加載真實市場數據
 */

class FinanceDataManager {
    constructor() {
        this.dataFile = 'finance-data.json';
        this.newsFile = 'finance-news.json';
        this.updateInterval = 300000; // 5分鐘
        this.lastUpdateTime = null;
    }
    
    async init() {
        console.log('📊 初始化財經數據管理器');
        
        // 加載數據
        await this.loadFinanceData();
        await this.loadFinanceNews();
        
        // 設置定時更新
        setInterval(() => this.loadFinanceData(), this.updateInterval);
        
        // 更新UI
        this.updateUI();
        
        // 更新時間顯示
        this.updateTimeDisplay();
    }
    
    async loadFinanceData() {
        try {
            const response = await fetch(this.dataFile + '?t=' + Date.now());
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            this.financeData = data;
            this.lastUpdateTime = new Date(data.timestamp);
            
            console.log('✅ 財經數據加載成功');
            this.updateMarketDataUI();
            this.updateTimeDisplay();
            
            return true;
        } catch (error) {
            console.error('❌ 財經數據加載失敗:', error);
            this.showErrorMessage('財經數據暫時不可用，請稍後重試');
            return false;
        }
    }
    
    async loadFinanceNews() {
        try {
            const response = await fetch(this.newsFile + '?t=' + Date.now());
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            this.financeNews = data;
            
            console.log('✅ 財經新聞加載成功');
            this.updateNewsUI();
            
            return true;
        } catch (error) {
            console.error('❌ 財經新聞加載失敗:', error);
            return false;
        }
    }
    
    updateMarketDataUI() {
        if (!this.financeData) return;
        
        const data = this.financeData;
        
        // 更新加密貨幣
        this.updateCryptoData(data.crypto);
        
        // 更新股票
        this.updateStockData(data.stocks);
        
        // 更新商品
        this.updateCommodityData(data.commodities);
        
        // 更新外匯
        this.updateForexData(data.forex);
        
        // 更新債券
        this.updateBondData(data.bonds);
        
        // 更新市場情緒
        this.updateMarketSentiment(data.market_sentiment);
    }
    
    updateCryptoData(cryptoData) {
        if (!cryptoData) return;
        
        const container = document.getElementById('crypto-data');
        if (!container) return;
        
        let html = '';
        
        // 主要加密貨幣
        const mainCryptos = ['bitcoin', 'ethereum', 'solana'];
        mainCryptos.forEach(cryptoId => {
            const crypto = cryptoData[cryptoId];
            if (crypto) {
                html += this.createCryptoCard(crypto);
            }
        });
        
        container.innerHTML = html;
    }
    
    createCryptoCard(crypto) {
        const changeClass = crypto.change_24h >= 0 ? 'change-positive' : 'change-negative';
        const changeIcon = crypto.change_24h >= 0 ? '↗' : '↘';
        
        return `
            <div class="market-card">
                <div class="market-header">
                    <h3>${crypto.name} (${crypto.symbol})</h3>
                    <span class="market-category">加密貨幣</span>
                </div>
                <div class="market-price">$${this.formatNumber(crypto.price, 2)}</div>
                <div class="market-change ${changeClass}">
                    ${changeIcon} ${crypto.change_24h >= 0 ? '+' : ''}${crypto.change_24h.toFixed(2)}%
                </div>
                <div class="market-details">
                    <div class="market-detail">
                        <span class="detail-label">市值:</span>
                        <span class="detail-value">$${this.formatNumber(crypto.market_cap, 0)}</span>
                    </div>
                    <div class="market-detail">
                        <span class="detail-label">24h交易量:</span>
                        <span class="detail-value">$${this.formatNumber(crypto.volume, 0)}</span>
                    </div>
                    <div class="market-detail">
                        <span class="detail-label">24h高/低:</span>
                        <span class="detail-value">$${this.formatNumber(crypto.high_24h, 0)} / $${this.formatNumber(crypto.low_24h, 0)}</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    updateStockData(stockData) {
        if (!stockData) return;
        
        const container = document.getElementById('stock-data');
        if (!container) return;
        
        let html = '';
        
        // 主要股票指數
        const mainStocks = ['NASDAQ', 'DJI', 'SP500'];
        mainStocks.forEach(stockId => {
            const stock = stockData[stockId];
            if (stock) {
                html += this.createStockCard(stock);
            }
        });
        
        container.innerHTML = html;
    }
    
    createStockCard(stock) {
        const changeClass = stock.change >= 0 ? 'change-positive' : 'change-negative';
        const changeIcon = stock.change >= 0 ? '↗' : '↘';
        
        return `
            <div class="market-card">
                <div class="market-header">
                    <h3>${stock.name} (${stock.symbol})</h3>
                    <span class="market-category">股票指數</span>
                </div>
                <div class="market-price">${this.formatNumber(stock.price, 2)}</div>
                <div class="market-change ${changeClass}">
                    ${changeIcon} ${stock.change >= 0 ? '+' : ''}${stock.change.toFixed(2)}
                </div>
                <div class="market-details">
                    <div class="market-detail">
                        <span class="detail-label">成交量:</span>
                        <span class="detail-value">${this.formatNumber(stock.volume, 0)}</span>
                    </div>
                    <div class="market-detail">
                        <span class="detail-label">當日高/低:</span>
                        <span class="detail-value">${this.formatNumber(stock.high, 2)} / ${this.formatNumber(stock.low, 2)}</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    updateCommodityData(commodityData) {
        if (!commodityData) return;
        
        const container = document.getElementById('commodity-data');
        if (!container) return;
        
        let html = '';
        
        // 主要商品
        const commodities = ['gold', 'oil_wti'];
        commodities.forEach(commodityId => {
            const commodity = commodityData[commodityId];
            if (commodity) {
                html += this.createCommodityCard(commodity);
            }
        });
        
        container.innerHTML = html;
    }
    
    createCommodityCard(commodity) {
        const changeClass = commodity.change >= 0 ? 'change-positive' : 'change-negative';
        const changeIcon = commodity.change >= 0 ? '↗' : '↘';
        
        return `
            <div class="market-card">
                <div class="market-header">
                    <h3>${commodity.name} (${commodity.symbol})</h3>
                    <span class="market-category">商品</span>
                </div>
                <div class="market-price">$${this.formatNumber(commodity.price, 2)}</div>
                <div class="market-change ${changeClass}">
                    ${changeIcon} ${commodity.change >= 0 ? '+' : ''}${commodity.change.toFixed(2)}
                </div>
                <div class="market-details">
                    <div class="market-detail">
                        <span class="detail-label">單位:</span>
                        <span class="detail-value">${commodity.unit}</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    updateForexData(forexData) {
        if (!forexData) return;
        
        const container = document.getElementById('forex-data');
        if (!container) return;
        
        let html = '';
        
        // 主要外匯對
        const forexPairs = ['USDHKD', 'USDCNY', 'EURUSD'];
        forexPairs.forEach(forexId => {
            const forex = forexData[forexId];
            if (forex) {
                html += this.createForexCard(forex);
            }
        });
        
        container.innerHTML = html;
    }
    
    createForexCard(forex) {
        const changeClass = forex.change >= 0 ? 'change-positive' : 'change-negative';
        const changeIcon = forex.change >= 0 ? '↗' : '↘';
        
        return `
            <div class="market-card">
                <div class="market-header">
                    <h3>${forex.name}</h3>
                    <span class="market-category">外匯</span>
                </div>
                <div class="market-price">${forex.rate.toFixed(4)}</div>
                <div class="market-change ${changeClass}">
                    ${changeIcon} ${forex.change >= 0 ? '+' : ''}${forex.change.toFixed(4)}
                </div>
                <div class="market-details">
                    <div class="market-detail">
                        <span class="detail-label">貨幣對:</span>
                        <span class="detail-value">${forex.from_currency}/${forex.to_currency}</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    updateBondData(bondData) {
        if (!bondData) return;
        
        const container = document.getElementById('bond-data');
        if (!container) return;
        
        let html = '';
        
        // 主要債券
        const bonds = ['us10y', 'us2y'];
        bonds.forEach(bondId => {
            const bond = bondData[bondId];
            if (bond) {
                html += this.createBondCard(bond);
            }
        });
        
        container.innerHTML = html;
    }
    
    createBondCard(bond) {
        const changeClass = bond.change >= 0 ? 'change-positive' : 'change-negative';
        const changeIcon = bond.change >= 0 ? '↗' : '↘';
        
        return `
            <div class="market-card">
                <div class="market-header">
                    <h3>${bond.name}</h3>
                    <span class="market-category">債券</span>
                </div>
                <div class="market-price">${bond.yield.toFixed(2)}%</div>
                <div class="market-change ${changeClass}">
                    ${changeIcon} ${bond.change >= 0 ? '+' : ''}${bond.change.toFixed(2)}%
                </div>
                <div class="market-details">
                    <div class="market-detail">
                        <span class="detail-label">國家:</span>
                        <span class="detail-value">${bond.country}</span>
                    </div>
                    <div class="market-detail">
                        <span class="detail-label">期限:</span>
                        <span class="detail-value">${bond.maturity}</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    updateMarketSentiment(sentimentData) {
        if (!sentimentData) return;
        
        const container = document.getElementById('market-sentiment');
        if (!container) return;
        
        const index = sentimentData.fear_greed_index || 50;
        const sentiment = sentimentData.sentiment || '中性';
        const description = sentimentData.description || '市場情緒數據暫時不可用';
        const color = sentimentData.color || '#666666';
        
        container.innerHTML = `
            <div class="sentiment-card" style="border-left-color: ${color}">
                <div class="sentiment-header">
                    <h3>市場情緒指數</h3>
                    <span class="sentiment-label" style="color: ${color}">${sentiment}</span>
                </div>
                <div class="sentiment-meter">
                    <div class="meter-bar">
                        <div class="meter-fill" style="width: ${index}%; background: ${color}"></div>
                    </div>
                    <div class="meter-labels">
                        <span>極度恐懼</span>
                        <span>恐懼</span>
                        <span>中性</span>
                        <span>貪婪</span>
                        <span>極度貪婪</span>
                    </div>
                </div>
                <div class="sentiment-index" style="color: ${color}">${index}/100</div>
                <div class="sentiment-description">${description}</div>
                <div class="sentiment-update">
                    更新時間: ${new Date(sentimentData.timestamp).toLocaleString('zh-HK')}
                </div>
            </div>
        `;
    }
    
    updateNewsUI() {
        if (!this.financeNews) return;
        
        const container = document.getElementById('finance-news');
        if (!container) return;
        
        const news = this.financeNews.news || [];
        let html = '';
        
        // 顯示最新5條新聞
        news.slice(0, 5).forEach(item => {
            html += this.createNewsItem(item);
        });
        
        container.innerHTML = html;
    }
    
    createNewsItem(news) {
        const timeAgo = this.getTimeAgo(news.timestamp);
        
        return `
            <div class="news-item">
                <div class="news-header">
                    <h4>${news.title}</h4>
                    <span class="news-source">${news.source}</span>
                </div>
                <div class="news-summary">${news.summary || '無摘要'}</div>
                <div class="news-footer">
                    <span class="news-category">${news.category || '財經'}</span>
                    <span class="news-time">${timeAgo}</span>
                    <a href="${news.link}" target="_blank" class="news-link">閱讀原文</a>
                </div>
            </div>
        `;
    }
    
    updateUI() {
        // 更新所有UI組件
        this.updateMarketDataUI();
        this.updateNewsUI();
    }
    
    updateTimeDisplay() {
        const timeElement = document.getElementById('last-update-time');
        if (timeElement && this.lastUpdateTime) {
            const timeStr = this.lastUpdateTime.toLocaleString('zh-HK', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
            timeElement.textContent = timeStr;
        }
    }
    
    showErrorMessage(message) {
        const errorContainer = document.getElementById('error-message');
        if (errorContainer) {
            errorContainer.innerHTML = `
                <div class="error-message">
                    <span class="error-icon">⚠️</span>
                    <span class="error-text">${message}</span>
                </div>
            `;
            errorContainer.style.display = 'block';
        }
    }
    
    // 工具方法
    formatNumber(num, decimals = 2) {
        if (num === undefined || num === null) return 'N/A';
        
        if (num >= 1000000000) {
            return (num / 1000000000).toFixed(decimals) + 'B';
        } else if (num >= 1000000) {
            return (num / 1000000).toFixed(decimals) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(decimals) + 'K';
        } else {
            return num.toLocaleString('en-US', {
                minimumFractionDigits: decimals,
                maximumFractionDigits: decimals
            });
        }
    }
    
    getTimeAgo(timestamp) {
        if (!timestamp) return '未知時間';
        
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (diffMins < 1) return '剛剛';
        if (diffMins < 60) return `${diffMins}分鐘前`;
        if (diffHours < 24) return `${diffHours}小時前`;
        if (diffDays < 7) return `${diffDays}天前`;
        
        return date.toLocaleDateString('zh-HK');
    }
}

// 初始化財經數據管理器
document.addEventListener('DOMContentLoaded', function() {
    const financeManager = new FinanceDataManager();
    financeManager.init();
    
    // 手動刷新按鈕
    const refreshBtn = document.getElementById('refresh-data');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', async function() {
            refreshBtn.disabled = true;
            refreshBtn.textContent = '更新中...';
            
            await financeManager.loadFinanceData();
            await financeManager.loadFinanceNews();
            
            refreshBtn.disabled = false;
            refreshBtn.textContent = '刷新數據';
            
            // 顯示更新成功提示
            const notification = document.createElement('div');
            notification.className = 'update-notification';
            notification.textContent = '✅ 數據更新成功';
            document.body.appendChild(notification);
            
            setTimeout(() => notification.remove(), 3000);
        });
    }
});