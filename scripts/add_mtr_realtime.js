/**
 * 港鐵實時數據整合腳本
 * 用於 dashboard.html
 */

// 港鐵線路顏色映射
const MTR_LINE_COLORS = {
    'TKL': '#8B5CF6',  // 將軍澳線 - 紫色
    'TWL': '#E2231A',  // 荃灣線 - 紅色
    'ISL': '#0098D8',  // 港島線 - 藍色
    'EAL': '#1FB25A',  // 東鐵線 - 綠色
    'TML': '#803090',  // 屯馬線 - 紫色
    'KTL': '#F9A01B',  // 觀塘線 - 橙色
    'TCL': '#FF6600',  // 東涌線 - 橙色
    'AEL': '#0066CC',  // 機場快線 - 藍色
    'DRL': '#FF6699',  // 迪士尼線 - 粉紅色
    'SIL': '#999999'   // 南港島線 - 灰色
};

// 車站代碼到中文名稱映射
const STATION_NAMES = {
    // 將軍澳線
    'TKO': '將軍澳', 'LHP': '康城', 'POA': '寶琳', 'TIK': '調景嶺', 'NOP': '北角',
    'YAT': '油塘', 'TKW': '坑口',
    
    // 荃灣線
    'TST': '尖沙咀', 'TSW': '荃灣', 'CEN': '中環', 'ADM': '金鐘', 'MOK': '旺角',
    'JOR': '佐敦', 'YMT': '油麻地', 'SHS': '深水埗', 'LCK': '荔枝角', 'LAT': '藍田',
    
    // 港島線
    'WCH': '灣仔', 'CAB': '銅鑼灣', 'TIH': '天后', 'FOH': '炮台山', 'SKW': '筲箕灣',
    'CHW': '柴灣', 'SWH': '西灣河', 'TAK': '太古', 'QUB': '鰂魚涌',
    
    // 東鐵線
    'SHS': '上水', 'LOW': '羅湖', 'FOT': '火炭', 'TAW': '大圍', 'KOT': '九龍塘',
    'MKK': '旺角東', 'HUH': '紅磡', 'ETS': '尖東',
    
    // 屯馬線
    'TUM': '屯門', 'SIH': '兆康', 'YUL': '元朗', 'AUS': '柯士甸', 'HUH': '紅磡',
    'WKS': '烏溪沙', 'TWO': '大圍', 'DIH': '鑽石山', 'KAT': '啟德'
};

// 線路代碼到中文名稱映射
const LINE_NAMES = {
    'TKL': '將軍澳線',
    'TWL': '荃灣線',
    'ISL': '港島線',
    'EAL': '東鐵線',
    'TML': '屯馬線',
    'KTL': '觀塘線',
    'TCL': '東涌線',
    'AEL': '機場快線',
    'DRL': '迪士尼線',
    'SIL': '南港島線'
};

// 要顯示的車站列表（熱門車站）
const POPULAR_STATIONS = [
    { line: 'TWL', sta: 'TST', name: '尖沙咀' },  // 荃灣線 - 尖沙咀
    { line: 'ISL', sta: 'CEN', name: '中環' },    // 港島線 - 中環
    { line: 'TKL', sta: 'TKO', name: '將軍澳' },  // 將軍澳線 - 將軍澳
    { line: 'EAL', sta: 'SHS', name: '上水' },    // 東鐵線 - 上水
    { line: 'TML', sta: 'TUM', name: '屯門' }     // 屯馬線 - 屯門
];

/**
 * 獲取港鐵實時數據
 */
async function fetchMTRData(line, station) {
    try {
        const url = `https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php?line=${line}&sta=${station}`;
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error(`獲取 ${line}-${station} 數據失敗:`, error);
        return null;
    }
}

/**
 * 格式化列車信息
 */
function formatTrainInfo(train, direction) {
    if (!train) return '';
    
    const destCode = train.dest;
    const destName = STATION_NAMES[destCode] || destCode;
    const minutes = train.ttnt;
    
    // 根據分鐘數顯示不同的顏色
    let timeClass = 'time-normal';
    if (minutes <= 1) timeClass = 'time-arriving';
    else if (minutes <= 3) timeClass = 'time-soon';
    
    return `
        <div class="transport-item">
            <span class="line-icon" style="background-color: var(--line-color);">
                ${direction === 'UP' ? '↑' : '↓'}
            </span>
            <span class="station">往 ${destName}</span>
            <span class="time ${timeClass}">${minutes}分鐘</span>
            <span class="platform">月台 ${train.plat}</span>
        </div>
    `;
}

/**
 * 更新港鐵數據顯示
 */
async function updateMTRDisplay() {
    const container = document.getElementById('mtrData');
    if (!container) return;
    
    // 顯示加載中
    container.innerHTML = '<div class="loading">載入港鐵實時數據...</div>';
    
    // 獲取所有車站數據
    const promises = POPULAR_STATIONS.map(station => 
        fetchMTRData(station.line, station.sta)
    );
    
    try {
        const results = await Promise.all(promises);
        
        let html = '';
        
        results.forEach((data, index) => {
            const station = POPULAR_STATIONS[index];
            
            if (data && data.status === 1) {
                const key = `${station.line}-${station.sta}`;
                const stationData = data.data[key];
                
                if (stationData) {
                    // 設置線路顏色
                    const lineColor = MTR_LINE_COLORS[station.line] || '#666666';
                    
                    html += `
                        <div class="station-card">
                            <div class="station-header">
                                <span class="line-badge" style="background-color: ${lineColor};">
                                    ${LINE_NAMES[station.line] || station.line}
                                </span>
                                <span class="station-name">${station.name}站</span>
                                <span class="update-time">${data.sys_time.split(' ')[1]}</span>
                            </div>
                    `;
                    
                    // 上行列車
                    const upTrains = stationData.UP || [];
                    if (upTrains.length > 0) {
                        html += '<div class="direction-section">';
                        html += '<div class="direction-label">上行</div>';
                        html += upTrains.slice(0, 2).map(train => 
                            formatTrainInfo(train, 'UP')
                        ).join('');
                        html += '</div>';
                    }
                    
                    // 下行列車
                    const downTrains = stationData.DOWN || [];
                    if (downTrains.length > 0) {
                        html += '<div class="direction-section">';
                        html += '<div class="direction-label">下行</div>';
                        html += downTrains.slice(0, 2).map(train => 
                            formatTrainInfo(train, 'DOWN')
                        ).join('');
                        html += '</div>';
                    }
                    
                    html += '</div>';
                }
            }
        });
        
        if (html) {
            container.innerHTML = html;
            
            // 添加 CSS 樣式
            addMTRStyles();
            
            // 添加延誤提示（如果有）
            const hasDelay = results.some(data => data && data.isdelay === 'Y');
            if (hasDelay) {
                container.innerHTML += `
                    <div class="delay-notice">
                        ⚠️ 部分線路有延誤，請留意車站廣播
                    </div>
                `;
            }
            
            // 添加數據來源說明
            container.innerHTML += `
                <div class="data-source">
                    數據來源: data.gov.hk • 更新時間: ${new Date().toLocaleTimeString('zh-HK')}
                </div>
            `;
        } else {
            container.innerHTML = '<div class="error">無法獲取港鐵數據，請稍後再試</div>';
        }
        
    } catch (error) {
        console.error('更新港鐵數據失敗:', error);
        container.innerHTML = `
            <div class="error">
                無法連接港鐵數據服務
                <div class="retry-btn" onclick="updateMTRDisplay()">重試</div>
            </div>
        `;
    }
}

/**
 * 添加 CSS 樣式
 */
function addMTRStyles() {
    if (document.getElementById('mtr-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'mtr-styles';
    style.textContent = `
        .station-card {
            background: white;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid var(--line-color, #666);
        }
        
        .station-header {
            display: flex;
            align-items: center;
            margin-bottom: 12px;
            padding-bottom: 10px;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .line-badge {
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
            margin-right: 10px;
        }
        
        .station-name {
            font-weight: bold;
            font-size: 1.1rem;
            flex-grow: 1;
        }
        
        .update-time {
            font-size: 0.8rem;
            color: #666;
        }
        
        .direction-section {
            margin-bottom: 10px;
        }
        
        .direction-label {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 5px;
            font-weight: 500;
        }
        
        .transport-item {
            display: flex;
            align-items: center;
            padding: 8px 10px;
            background: #f8f9fa;
            border-radius: 8px;
            margin-bottom: 8px;
            transition: background 0.2s;
        }
        
        .transport-item:hover {
            background: #e9ecef;
        }
        
        .line-icon {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            margin-right: 10px;
            font-size: 0.9rem;
        }
        
        .station {
            flex-grow: 1;
            font-weight: 500;
        }
        
        .time {
            font-weight: bold;
            margin-right: 15px;
            min-width: 60px;
            text-align: right;
        }
        
        .time-arriving {
            color: #dc3545;
        }
        
        .time-soon {
            color: #fd7e14;
        }
        
        .time-normal {
            color: #28a745;
        }
        
        .platform {
            font-size: 0.9rem;
            color: #666;
            min-width: 70px;
            text-align: right;
        }
        
        .delay-notice {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 10px;
            border-radius: 8px;
            margin-top: 15px;
            text-align: center;
            font-weight: 500;
        }
        
        .data-source {
            font-size: 0.8rem;
            color: #999;
            text-align: center;
            margin-top: 15px;
            padding-top: 10px;
            border-top: 1px solid #eee;
        }
        
        .error {
            text-align: center;
            padding: 20px;
            color: #dc3545;
        }
        
        .retry-btn {
            display: inline-block;
            background: #007bff;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            margin-top: 10px;
            cursor: pointer;
            font-weight: 500;
        }
        
        .retry-btn:hover {
            background: #0056b3;
        }
        
        .loading {
            text-align: center;
            padding: 30px;
            color: #666;
        }
    `;
    
    document.head.appendChild(style);
}

/**
 * 初始化港鐵數據
 */
function initMTRData() {
    // 頁面加載完成後更新數據
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            updateMTRDisplay();
            
            // 每30秒更新一次
            setInterval(updateMTRDisplay, 30000);
        });
    } else {
        updateMTRDisplay();
        setInterval(updateMTRDisplay, 30000);
    }
}

// 導出函數供外部使用
window.MTRData = {
    init: initMTRData,
    update: updateMTRDisplay,
    fetch: fetchMTRData
};

// 自動初始化
initMTRData();