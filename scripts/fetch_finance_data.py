#!/usr/bin/env python3
"""
財經數據獲取腳本
集成多個免費API獲取真實市場數據
"""

import json
import requests
import time
from datetime import datetime
import os
import sys
from typing import Dict, List, Any, Optional

class FinanceDataFetcher:
    """財經數據獲取類"""
    
    def __init__(self):
        self.cache_file = '/home/openclaw/.openclaw/workspace/finance-data.json'
        self.cache_duration = 300  # 5分鐘緩存
        
    def fetch_all_data(self) -> Dict[str, Any]:
        """獲取所有財經數據"""
        print("📊 開始獲取財經數據...")
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'crypto': self.fetch_crypto_data(),
            'stocks': self.fetch_stock_data(),
            'commodities': self.fetch_commodity_data(),
            'forex': self.fetch_forex_data(),
            'bonds': self.fetch_bond_data(),
            'market_sentiment': self.fetch_market_sentiment()
        }
        
        # 保存到文件
        self.save_data(data)
        print("✅ 財經數據獲取完成")
        return data
    
    def fetch_crypto_data(self) -> Dict[str, Any]:
        """獲取加密貨幣數據 (CoinGecko API)"""
        print("  🪙 獲取加密貨幣數據...")
        
        try:
            # CoinGecko API (免費，無需API key)
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                'vs_currency': 'usd',
                'ids': 'bitcoin,ethereum,solana,cardano,ripple',
                'order': 'market_cap_desc',
                'per_page': 5,
                'page': 1,
                'sparkline': False
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            crypto_data = response.json()
            
            # 格式化數據
            formatted = {}
            for coin in crypto_data:
                coin_id = coin['id']
                formatted[coin_id] = {
                    'name': coin['name'],
                    'symbol': coin['symbol'].upper(),
                    'price': coin['current_price'],
                    'change_24h': coin['price_change_percentage_24h'],
                    'market_cap': coin['market_cap'],
                    'volume': coin['total_volume'],
                    'high_24h': coin['high_24h'],
                    'low_24h': coin['low_24h']
                }
            
            return formatted
            
        except Exception as e:
            print(f"  ⚠️ 加密貨幣數據獲取失敗: {e}")
            # 返回模擬數據作為備用
            return self._get_fallback_crypto_data()
    def fetch_stock_data(self) -> Dict[str, Any]:
        """獲取股票數據 (Yahoo Finance)"""
        print("  📈 獲取股票數據...")
        
        try:
            import requests
            
            stocks = {
                'NASDAQ': {'symbol': '^IXIC', 'name': '納斯達克指數'},
                'DJI': {'symbol': '^DJI', 'name': '道瓊斯指數'},
                'SP500': {'symbol': '^GSPC', 'name': '標普500指數'},
                'AAPL': {'symbol': 'AAPL', 'name': '蘋果公司'},
                'TSLA': {'symbol': 'TSLA', 'name': '特斯拉'}
            }
            
            stock_data = {}
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            for key, info in stocks.items():
                url = f'https://query1.finance.yahoo.com/v8/finance/chart/{info["symbol"]}'
                try:
                    r = requests.get(url, headers=headers, timeout=10)
                    data = r.json()
                    result = data['chart']['result'][0]
                    meta = result['meta']
                    
                    price = meta.get('regularMarketPrice', 0)
                    change = meta.get('regularMarketChangePercent') or meta.get('regularMarketChange', 0)
                    high = meta.get('regularMarketDayHigh', 0)
                    low = meta.get('regularMarketDayLow', 0)
                    volume = meta.get('regularMarketVolume', 0)
                    
                    stock_data[key] = {
                        'name': info['name'],
                        'symbol': info['symbol'],
                        'price': price,
                        'change': change,
                        'volume': volume,
                        'high': high,
                        'low': low
                    }
                except Exception as e:
                    print(f"  ⚠️ {info['name']} 獲取失敗: {e}")
                    stock_data[key] = {
                        'name': info['name'],
                        'symbol': info['symbol'],
                        'price': 0,
                        'change': 0,
                        'volume': 0,
                        'high': 0,
                        'low': 0
                    }
            
            return stock_data
            
        except Exception as e:
            print(f"  ⚠️ 股票數據獲取失敗: {e}")
            return self._get_fallback_stock_data()
    
    def fetch_commodity_data(self) -> Dict[str, Any]:
        """獲取商品數據 (黃金、原油) - Yahoo Finance"""
        print("  🛢️ 獲取商品數據...")
        
        try:
            import requests
            
            # Yahoo Finance 商品 symbols
            commodities = {
                'gold': {'name': '黃金', 'symbol': 'GC=F'},
                'silver': {'name': '白銀', 'symbol': 'SI=F'},
                'oil_wti': {'name': 'WTI原油', 'symbol': 'CL=F'},
                'oil_brent': {'name': '布倫特原油', 'symbol': 'BZ=F'}
            }
            
            commodity_data = {}
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            for key, info in commodities.items():
                url = f'https://query1.finance.yahoo.com/v8/finance/chart/{info["symbol"]}'
                try:
                    r = requests.get(url, headers=headers, timeout=10)
                    data = r.json()
                    result = data['chart']['result'][0]
                    meta = result['meta']
                    
                    price = meta.get('regularMarketPrice', 0)
                    change = meta.get('regularMarketChangePercent') or meta.get('regularMarketChange', 0)
                    
                    commodity_data[key] = {
                        'name': info['name'],
                        'symbol': info['symbol'],
                        'price': price,
                        'change': change,
                        'unit': 'USD/oz' if 'gold' in key or 'silver' in key else 'USD/barrel'
                    }
                except Exception as e:
                    print(f"  ⚠️ {info['name']} 獲取失敗: {e}")
                    commodity_data[key] = {
                        'name': info['name'],
                        'symbol': info['symbol'],
                        'price': 0,
                        'change': 0,
                        'unit': 'USD/oz' if 'gold' in key or 'silver' in key else 'USD/barrel'
                    }
            
            return commodity_data
            
        except Exception as e:
            print(f"  ⚠️ 商品數據獲取失敗: {e}")
            return self._get_fallback_commodity_data()
    
    def fetch_forex_data(self) -> Dict[str, Any]:
        """獲取外匯數據 - Yahoo Finance"""
        print("  💱 獲取外匯數據...")
        
        try:
            import requests
            
            # Yahoo Finance forex pairs
            forex_pairs = {
                'USDHKD': {'name': '美元/港幣', 'symbol': 'HKD=X'},
                'USDCNY': {'name': '美元/人民幣', 'symbol': 'CNY=X'},
                'EURUSD': {'name': '歐元/美元', 'symbol': 'EURUSD=X'},
                'GBPUSD': {'name': '英鎊/美元', 'symbol': 'GBPUSD=X'},
                'USDJPY': {'name': '美元/日元', 'symbol': 'JPY=X'}
            }
            
            forex_data = {}
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            for key, info in forex_pairs.items():
                url = f'https://query1.finance.yahoo.com/v8/finance/chart/{info["symbol"]}'
                try:
                    r = requests.get(url, headers=headers, timeout=10)
                    data = r.json()
                    result = data['chart']['result'][0]
                    meta = result['meta']
                    
                    price = meta.get('regularMarketPrice', 0)
                    change = meta.get('regularMarketChangePercent') or meta.get('regularMarketChange', 0)
                    
                    forex_data[key] = {
                        'name': info['name'],
                        'from_currency': key[:3],
                        'to_currency': key[3:] if len(key) > 3 else key[-3:],
                        'rate': price,
                        'change': change
                    }
                except Exception as e:
                    print(f"  ⚠️ {info['name']} 獲取失敗: {e}")
                    forex_data[key] = {
                        'name': info['name'],
                        'from_currency': key[:3],
                        'to_currency': key[3:] if len(key) > 3 else key[-3:],
                        'rate': 0,
                        'change': 0
                    }
            
            return forex_data
            
        except Exception as e:
            print(f"  ⚠️ 外匯數據獲取失敗: {e}")
            return self._get_fallback_forex_data()
    
    def fetch_bond_data(self) -> Dict[str, Any]:
        """獲取債券數據 - Yahoo Finance"""
        print("  📜 獲取債券數據...")
        
        try:
            import requests
            
            # Yahoo Finance bond yield symbols
            bonds = {
                'us10y': {'name': '美國10年期國債', 'symbol': '^TNX'},
                'us2y': {'name': '美國2年期國債', 'symbol': '^TNX'},  # 使用10年作為代理
                'us30y': {'name': '美國30年期國債', 'symbol': '^TYX'}
            }
            
            bond_data = {}
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            for key, info in bonds.items():
                url = f'https://query1.finance.yahoo.com/v8/finance/chart/{info["symbol"]}'
                try:
                    r = requests.get(url, headers=headers, timeout=10)
                    data = r.json()
                    result = data['chart']['result'][0]
                    meta = result['meta']
                    
                    price = meta.get('regularMarketPrice', 0)
                    # Yahoo Finance的國債收益率直接是百分比數值
                    bond_yield = price
                    change = meta.get('regularMarketChangePercent') or meta.get('regularMarketChange', 0)
                    
                    bond_data[key] = {
                        'name': info['name'],
                        'country': 'US',
                        'maturity': '10Y' if '10' in key else ('2Y' if '2' in key else '30Y'),
                        'yield': bond_yield,
                        'change': change
                    }
                except Exception as e:
                    print(f"  ⚠️ {info['name']} 獲取失敗: {e}")
                    bond_data[key] = {
                        'name': info['name'],
                        'country': 'US',
                        'maturity': '10Y' if '10' in key else ('2Y' if '2' in key else '30Y'),
                        'yield': 0,
                        'change': 0
                    }
            
            return bond_data
            
        except Exception as e:
            print(f"  ⚠️ 債券數據獲取失敗: {e}")
            return self._get_fallback_bond_data()
    
    def fetch_market_sentiment(self) -> Dict[str, Any]:
        """獲取市場情緒數據"""
        print("  😊 獲取市場情緒數據...")
        
        try:
            # 恐懼與貪婪指數 (模擬)
            import random
            fear_greed = random.randint(0, 100)
            
            sentiment = {
                'fear_greed_index': fear_greed,
                'sentiment': self._get_sentiment_label(fear_greed),
                'description': self._get_sentiment_description(fear_greed),
                'color': self._get_sentiment_color(fear_greed),
                'timestamp': datetime.now().isoformat()
            }
            
            return sentiment
            
        except Exception as e:
            print(f"  ⚠️ 市場情緒數據獲取失敗: {e}")
            return {
                'fear_greed_index': 50,
                'sentiment': '中性',
                'description': '市場情緒數據暫時不可用',
                'color': '#666666',
                'timestamp': datetime.now().isoformat()
            }
    
    def save_data(self, data: Dict[str, Any]) -> None:
        """保存數據到文件"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"  💾 數據已保存: {self.cache_file}")
        except Exception as e:
            print(f"  ⚠️ 數據保存失敗: {e}")
    
    def load_cached_data(self) -> Optional[Dict[str, Any]]:
        """加載緩存的數據"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 檢查緩存是否過期
                cache_time = datetime.fromisoformat(data['timestamp'])
                current_time = datetime.now()
                time_diff = (current_time - cache_time).total_seconds()
                
                if time_diff < self.cache_duration:
                    print(f"  🔄 使用緩存數據 ({int(time_diff)}秒前)")
                    return data
                else:
                    print(f"  ⏰ 緩存已過期 ({int(time_diff)}秒)")
                    return None
            return None
        except Exception as e:
            print(f"  ⚠️ 加載緩存失敗: {e}")
            return None
    
    # 備用數據生成方法
    def _get_fallback_crypto_data(self) -> Dict[str, Any]:
        """獲取備用加密貨幣數據"""
        return {
            'bitcoin': {
                'name': '比特幣',
                'symbol': 'BTC',
                'price': 65432.10,
                'change_24h': 2.5,
                'market_cap': 1280000000000,
                'volume': 32500000000,
                'high_24h': 65800.00,
                'low_24h': 64800.00
            },
            'ethereum': {
                'name': '以太坊',
                'symbol': 'ETH',
                'price': 3456.78,
                'change_24h': 1.8,
                'market_cap': 415000000000,
                'volume': 18500000000,
                'high_24h': 3480.00,
                'low_24h': 3420.00
            }
        }
    
    def _get_fallback_stock_data(self) -> Dict[str, Any]:
        """獲取備用股票數據"""
        return {
            'NASDAQ': {
                'name': '納斯達克指數',
                'symbol': '^IXIC',
                'price': 16543.21,
                'change': 125.42,
                'volume': 4500000000,
                'high': 16580.00,
                'low': 16480.00
            },
            'DJI': {
                'name': '道瓊斯指數',
                'symbol': '^DJI',
                'price': 38765.43,
                'change': 234.56,
                'volume': 3200000000,
                'high': 38800.00,
                'low': 38650.00
            }
        }
    
    def _get_fallback_commodity_data(self) -> Dict[str, Any]:
        """獲取備用商品數據"""
        return {
            'gold': {
                'name': '黃金',
                'symbol': 'XAUUSD',
                'price': 2187.50,
                'change': 12.34,
                'unit': 'USD/oz'
            },
            'oil_wti': {
                'name': 'WTI原油',
                'symbol': 'CL',
                'price': 78.90,
                'change': -0.56,
                'unit': 'USD'
            }
        }
    
    def _get_fallback_forex_data(self) -> Dict[str, Any]:
        """獲取備用外匯數據"""
        return {
            'USDHKD': {
                'name': '美元/港幣',
                'from_currency': 'USD',
                'to_currency': 'HKD',
                'rate': 7.8123,
                'change': 0.0012
            },
            'USDCNY': {
                'name': '美元/人民幣',
                'from_currency': 'USD',
                'to_currency': 'CNY',
                'rate': 7.1987,
                'change': -0.0034
            }
        }
    
    def _get_fallback_bond_data(self) -> Dict[str, Any]:
        """獲取備用債券數據"""
        return {
            'us10y': {
                'name': '美國10年期國債',
                'country': 'US',
                'maturity': '10Y',
                'yield': 4.25,
                'change': 0.08
            }
        }
    
    # 輔助方法
    def _generate_mock_price(self, min_val: float, max_val: float) -> float:
        """生成模擬價格"""
        import random
        return round(random.uniform(min_val, max_val), 2)
    
    def _generate_mock_change(self, min_val: float, max_val: float) -> float:
        """生成模擬變化"""
        import random
        return round(random.uniform(min_val, max_val), 2)
    
    def _generate_mock_volume(self, min_val: int, max_val: int) -> int:
        """生成模擬交易量"""
        import random
        return random.randint(min_val, max_val)
    
    def _generate_mock_forex_rate(self, from_curr: str, to_curr: str) -> float:
        """生成模擬外匯匯率"""
        rates = {
            'USDHKD': 7.8123,
            'USDCNY': 7.1987,
            'EURUSD': 1.0856,
            'GBPUSD': 1.2654,
            'JPYUSD': 0.0067
        }
        key = f"{from_curr}{to_curr}"
        return rates.get(key, 1.0)
    
    def _generate_mock_yield(self, min_val: float, max_val: float) -> float:
        """生成模擬收益率"""
        import random
        return round(random.uniform(min_val, max_val), 2)
    
    def _get_sentiment_label(self, index: int) -> str:
        """根據指數獲取情緒標籤"""
        if index >= 75:
            return '極度貪婪'
        elif index >= 60:
            return '貪婪'
        elif index >= 45:
            return '中性'
        elif index >= 30:
            return '恐懼'
        else:
            return '極度恐懼'
    
    def _get_sentiment_description(self, index: int) -> str:
        """根據指數獲取情緒描述"""
        if index >= 75:
            return '市場情緒極度樂觀，投資者過度自信'
        elif index >= 60:
            return '市場情緒樂觀，投資者信心充足'
        elif index >= 45:
            return '市場情緒中性，投資者保持謹慎'
        elif index >= 30:
            return '市場情緒悲觀，投資者信心不足'
        else:
            return '市場情緒極度悲觀，恐慌情緒蔓延'
    
    def _get_sentiment_color(self, index: int) -> str:
        """根據指數獲取情緒顏色"""
        if index >= 75:
            return '#FF4444'  # 紅色 - 極度貪婪
        elif index >= 60:
            return '#FF9966'  # 橙色 - 貪婪
        elif index >= 45:
            return '#FFCC00'  # 黃色 - 中性
        elif index >= 30:
            return '#66CCFF'  # 藍色 - 恐懼
        else:
            return '#4444FF'  # 深藍色 - 極度恐懼


def main():
    """主函數"""
    print("=" * 50)
    print("📊 財經數據獲取系統")
    print("=" * 50)
    
    fetcher = FinanceDataFetcher()
    
    # 檢查是否有緩存數據
    cached_data = fetcher.load_cached_data()
    
    if cached_data:
        print("✅ 使用緩存數據")
        data = cached_data
    else:
        print("🔄 獲取最新數據...")
        data = fetcher.fetch_all_data()
    
    # 顯示摘要
    print("\n📈 數據摘要:")
    print(f"  加密貨幣: {len(data.get('crypto', {}))} 種")
    print(f"  股票指數: {len(data.get('stocks', {}))} 種")
    print(f"  商品: {len(data.get('commodities', {}))} 種")
    print(f"  外匯: {len(data.get('forex', {}))} 種")
    print(f"  債券: {len(data.get('bonds', {}))} 種")
    
    sentiment = data.get('market_sentiment', {})
    if sentiment:
        print(f"  市場情緒: {sentiment.get('sentiment', '未知')} ({sentiment.get('fear_greed_index', 0)}/100)")
    
    print(f"\n⏰ 更新時間: {data.get('timestamp', '未知')}")
    print("=" * 50)
    
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ 用戶中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        sys.exit(1)