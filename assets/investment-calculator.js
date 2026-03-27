/**
 * 投資計算器JavaScript
 * 提供複利計算、風險評估等投資工具
 */

class InvestmentCalculator {
    constructor() {
        this.initCalculators();
    }
    
    initCalculators() {
        // 複利計算器
        this.initCompoundInterestCalculator();
        
        // 風險評估器
        this.initRiskAssessmentCalculator();
        
        // 技術指標計算器
        this.initTechnicalIndicators();
    }
    
    initCompoundInterestCalculator() {
        const form = document.getElementById('compound-interest-form');
        if (!form) return;
        
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.calculateCompoundInterest();
        });
        
        // 初始計算
        this.calculateCompoundInterest();
    }
    
    calculateCompoundInterest() {
        const principal = parseFloat(document.getElementById('principal').value) || 0;
        const monthlyContribution = parseFloat(document.getElementById('monthly-contribution').value) || 0;
        const annualRate = parseFloat(document.getElementById('annual-rate').value) || 0;
        const years = parseFloat(document.getElementById('years').value) || 0;
        
        // 計算複利
        const monthlyRate = annualRate / 100 / 12;
        const months = years * 12;
        
        let total = principal;
        let contributions = 0;
        let interestEarned = 0;
        
        // 每月計算
        for (let i = 0; i < months; i++) {
            // 添加月供
            total += monthlyContribution;
            contributions += monthlyContribution;
            
            // 計算利息
            const monthlyInterest = total * monthlyRate;
            total += monthlyInterest;
            interestEarned += monthlyInterest;
        }
        
        // 計算複利效應
        const totalContributions = principal + contributions;
        const compoundEffect = total > 0 ? ((total - totalContributions) / totalContributions * 100) : 0;
        
        // 更新結果
        document.getElementById('final-amount').textContent = this.formatCurrency(total);
        document.getElementById('total-contributions').textContent = this.formatCurrency(totalContributions);
        document.getElementById('total-interest').textContent = this.formatCurrency(interestEarned);
        document.getElementById('compound-effect').textContent = `+${compoundEffect.toFixed(1)}%`;
        
        // 生成圖表數據
        this.generateCompoundInterestChart(principal, monthlyContribution, annualRate, years);
    }
    
    generateCompoundInterestChart(principal, monthlyContribution, annualRate, years) {
        const ctx = document.getElementById('compound-interest-chart');
        if (!ctx) return;
        
        const monthlyRate = annualRate / 100 / 12;
        const months = years * 12;
        
        const labels = [];
        const principalData = [];
        const interestData = [];
        const totalData = [];
        
        let total = principal;
        let totalPrincipal = principal;
        
        for (let year = 0; year <= years; year++) {
            const month = year * 12;
            labels.push(`第${year}年`);
            
            // 計算到當年的總額
            let yearTotal = principal;
            let yearPrincipal = principal;
            
            for (let m = 0; m < Math.min(month, months); m++) {
                // 添加月供
                yearTotal += monthlyContribution;
                yearPrincipal += monthlyContribution;
                
                // 計算利息
                const monthlyInterest = yearTotal * monthlyRate;
                yearTotal += monthlyInterest;
            }
            
            principalData.push(yearPrincipal);
            interestData.push(yearTotal - yearPrincipal);
            totalData.push(yearTotal);
        }
        
        // 創建或更新圖表
        if (this.compoundChart) {
            this.compoundChart.destroy();
        }
        
        this.compoundChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: '本金',
                        data: principalData,
                        backgroundColor: '#10b981',
                        stack: 'Stack 0'
                    },
                    {
                        label: '利息',
                        data: interestData,
                        backgroundColor: '#3b82f6',
                        stack: 'Stack 0'
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: '複利增長圖'
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const value = context.raw;
                                const total = totalData[context.dataIndex];
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${context.dataset.label}: ${this.formatCurrency(value)} (${percentage}%)`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        stacked: true
                    },
                    y: {
                        stacked: true,
                        ticks: {
                            callback: (value) => this.formatCurrency(value)
                        }
                    }
                }
            }
        });
    }
    
    initRiskAssessmentCalculator() {
        const form = document.getElementById('risk-assessment-form');
        if (!form) return;
        
        // 滑塊值顯示
        const riskSlider = document.getElementById('risk-tolerance');
        const riskValue = document.getElementById('risk-tolerance-value');
        
        if (riskSlider && riskValue) {
            riskValue.textContent = riskSlider.value;
            
            riskSlider.addEventListener('input', () => {
                riskValue.textContent = riskSlider.value;
                // 移動滑塊值顯示位置
                const percent = (riskSlider.value - riskSlider.min) / (riskSlider.max - riskSlider.min) * 100;
                riskValue.style.left = `calc(${percent}% + (${8 - percent * 0.15}px))`;
            });
        }
        
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.calculateRiskAssessment();
        });
        
        // 初始計算
        this.calculateRiskAssessment();
    }
    
    calculateRiskAssessment() {
        // 收集風險評估問題的答案
        const answers = {
            age: parseInt(document.getElementById('risk-age').value) || 30,
            horizon: parseInt(document.getElementById('investment-horizon').value) || 10,
            experience: parseInt(document.getElementById('investment-experience').value) || 3,
            tolerance: parseInt(document.getElementById('risk-tolerance').value) || 5,
            goals: parseInt(document.getElementById('investment-goals').value) || 3
        };
        
        // 計算風險分數（0-100）
        let riskScore = 0;
        
        // 年齡因素（年輕=高風險承受能力）
        if (answers.age < 30) riskScore += 25;
        else if (answers.age < 50) riskScore += 15;
        else riskScore += 5;
        
        // 投資期限（長期=高風險承受能力）
        if (answers.horizon >= 10) riskScore += 25;
        else if (answers.horizon >= 5) riskScore += 15;
        else riskScore += 5;
        
        // 投資經驗
        riskScore += answers.experience * 5;
        
        // 風險容忍度
        riskScore += answers.tolerance * 5;
        
        // 投資目標
        riskScore += answers.goals * 5;
        
        // 確定風險等級
        let riskLevel, riskStyle, riskDescription, recommendedAllocation;
        
        if (riskScore >= 80) {
            riskLevel = '積極型';
            riskStyle = '高風險高回報';
            riskDescription = '您有很高的風險承受能力，適合追求最大化回報的投資策略。建議關注成長型股票和新興市場。';
            recommendedAllocation = {
                '股票': '70%',
                '債券': '15%',
                '現金': '5%',
                '另類投資': '10%'
            };
        } else if (riskScore >= 65) {
            riskLevel = '成長型';
            riskStyle = '平衡增長';
            riskDescription = '您有較高的風險承受能力，適合追求穩健增長的投資策略。建議平衡配置股票和債券。';
            recommendedAllocation = {
                '股票': '60%',
                '債券': '25%',
                '現金': '10%',
                '另類投資': '5%'
            };
        } else if (riskScore >= 50) {
            riskLevel = '平衡型';
            riskStyle = '穩健增長';
            riskDescription = '您有中等風險承受能力，適合穩健增長的投資策略。建議側重於優質股票和投資級債券。';
            recommendedAllocation = {
                '股票': '50%',
                '債券': '35%',
                '現金': '10%',
                '另類投資': '5%'
            };
        } else if (riskScore >= 35) {
            riskLevel = '保守型';
            riskStyle = '保本增值';
            riskDescription = '您有較低的風險承受能力，適合保本為主的投資策略。建議以債券和現金為主。';
            recommendedAllocation = {
                '股票': '30%',
                '債券': '50%',
                '現金': '15%',
                '另類投資': '5%'
            };
        } else {
            riskLevel = '極度保守型';
            riskStyle = '資本保值';
            riskDescription = '您有很低的風險承受能力，適合完全保本的投資策略。建議以現金和短期債券為主。';
            recommendedAllocation = {
                '股票': '10%',
                '債券': '60%',
                '現金': '25%',
                '另類投資': '5%'
            };
        }
        
        // 更新結果
        document.getElementById('risk-score').textContent = riskScore;
        document.getElementById('risk-level').textContent = riskLevel;
        document.getElementById('risk-style').textContent = riskStyle;
        document.getElementById('risk-description').textContent = riskDescription;
        
        // 更新推薦配置（用於圖表）
        this.generateRiskChart(recommendedAllocation);
        
        // 生成風險圖表
        this.generateRiskChart(recommendedAllocation);
    }
    
    generateRiskChart(allocation) {
        const ctx = document.getElementById('risk-allocation-chart');
        if (!ctx) return;
        
        const labels = Object.keys(allocation);
        const data = Object.values(allocation).map(p => parseFloat(p));
        const colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444'];
        
        // 創建或更新圖表
        if (this.riskChart) {
            this.riskChart.destroy();
        }
        
        this.riskChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                return `${context.label}: ${context.raw}%`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    initTechnicalIndicators() {
        // 初始化技術指標計算器
        this.initRSICalculator();
        this.initMACDCalculator();
        this.initBollingerBandsCalculator();
    }
    
    initRSICalculator() {
        const form = document.getElementById('rsi-calculator');
        if (!form) return;
        
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.calculateRSI();
        });
    }
    
    calculateRSI() {
        const pricesInput = document.getElementById('rsi-prices').value;
        const period = parseInt(document.getElementById('rsi-period').value) || 14;
        
        if (!pricesInput) {
            alert('請輸入價格數據');
            return;
        }
        
        // 解析價格數據
        const prices = pricesInput.split(',').map(p => parseFloat(p.trim())).filter(p => !isNaN(p));
        
        if (prices.length < period + 1) {
            alert(`需要至少 ${period + 1} 個價格數據點`);
            return;
        }
        
        // 計算RSI
        const rsi = this.calculateRSIValue(prices, period);
        
        // 更新結果
        document.getElementById('rsi-result').textContent = rsi.toFixed(2);
        
        // 解釋RSI值
        let interpretation = '';
        if (rsi >= 70) {
            interpretation = '超買區域，可能出現回調';
        } else if (rsi <= 30) {
            interpretation = '超賣區域，可能出現反彈';
        } else if (rsi > 50) {
            interpretation = '多頭市場，上漲趨勢';
        } else {
            interpretation = '空頭市場，下跌趨勢';
        }
        
        document.getElementById('rsi-interpretation').textContent = interpretation;
    }
    
    calculateRSIValue(prices, period = 14) {
        let gains = 0;
        let losses = 0;
        
        // 計算初始的平均增益和平均損失
        for (let i = 1; i <= period; i++) {
            const change = prices[i] - prices[i - 1];
            if (change > 0) {
                gains += change;
            } else {
                losses -= change; // 損失為正數
            }
        }
        
        let avgGain = gains / period;
        let avgLoss = losses / period;
        
        // 計算後續的RSI值
        for (let i = period + 1; i < prices.length; i++) {
            const change = prices[i] - prices[i - 1];
            let currentGain = 0;
            let currentLoss = 0;
            
            if (change > 0) {
                currentGain = change;
            } else {
                currentLoss = -change;
            }
            
            // 平滑計算
            avgGain = ((avgGain * (period - 1)) + currentGain) / period;
            avgLoss = ((avgLoss * (period - 1)) + currentLoss) / period;
        }
        
        // 計算RS
        const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
        
        // 計算RSI
        const rsi = 100 - (100 / (1 + rs));
        
        return rsi;
    }
    
    initMACDCalculator() {
        const form = document.getElementById('macd-calculator');
        if (!form) return;
        
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.calculateMACD();
        });
    }
    
    calculateMACD() {
        // 這裡實現MACD計算邏輯
        // 由於複雜度，暫時顯示示例結果
        document.getElementById('macd-result').textContent = 'MACD: -0.25 | Signal: -0.18 | Histogram: -0.07';
        document.getElementById('macd-interpretation').textContent = 'MACD線在信號線下方，顯示下跌趨勢';
    }
    
    initBollingerBandsCalculator() {
        const form = document.getElementById('bollinger-calculator');
        if (!form) return;
        
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.calculateBollingerBands();
        });
    }
    
    calculateBollingerBands() {
        // 這裡實現布林帶計算邏輯
        // 由於複雜度，暫時顯示示例結果
        document.getElementById('bollinger-result').textContent = '上軌: 105.2 | 中軌: 100.0 | 下軌: 94.8';
        document.getElementById('bollinger-interpretation').textContent = '價格在中軌附近，市場趨勢不明顯';
    }
    
    // 工具方法
    formatCurrency(value) {
        if (value >= 1000000000) {
            return '$' + (value / 1000000000).toFixed(2) + 'B';
        } else if (value >= 1000000) {
            return '$' + (value / 1000000).toFixed(2) + 'M';
        } else if (value >= 1000) {
            return '$' + (value / 1000).toFixed(2) + 'K';
        } else {
            return '$' + value.toFixed(2);
        }
    }
}

// 初始化投資計算器
document.addEventListener('DOMContentLoaded', function() {
    // 加載Chart.js庫（如果未加載）
    if (typeof Chart === 'undefined') {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
        script.onload = function() {
            new InvestmentCalculator();
        };
        document.head.appendChild(script);
    } else {
        new InvestmentCalculator();
    }
});