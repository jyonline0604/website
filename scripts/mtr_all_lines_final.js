/**
 * 港鐵全線路實時數據
 * 顯示所有10條港鐵線路
 */

const MTR_LINES = [
    { code: 'AEL', name: '機場快線', color: '#0066CC', stations: ['HOK', 'AIR'] },
    { code: 'TCL', name: '東涌線', color: '#FF6600', stations: ['HOK', 'TUC'] },
    { code: 'TKL', name: '將軍澳線', color: '#8B5CF6', stations: ['NOP', 'TKO'] },
    { code: 'TWL', name: '荃灣線', color: '#E2231A', stations: ['TST', 'TSW'] },
    { code: 'ISL', name: '港島線', color: '#0098D8', stations: ['CEN', 'CHW'] },
    { code: 'EAL', name: '東鐵線', color: '#1FB25A', stations: ['ADM', 'LOW'] },
    { code: 'TML', name: '屯馬線', color: '#803090', stations: ['TUM', 'WKS'] },
    { code: 'KTL', name: '觀塘線', color: '#F9A01B', stations: ['WHA', 'SSP'] },
    { code: 'SIL', name: '南港島線', color: '#999999', stations: ['ADM', 'LET'] },
    { code: 'DRL', name: '迪士尼線', color: '#FF6699', stations: ['SUN', 'DIS'] }
];

const STATION_NAMES = {
    'HOK': '香港', 'AIR': '機場', 'TUC': '東涌', 'NOP': '北角', 'TKO': '將軍澳',
    'TST': '尖沙咀', 'TSW': '荃灣', 'CEN': '中環', 'CHW': '柴灣', 'ADM': '金鐘',
    'LOW': '羅湖', 'TUM': '屯門', 'WKS': '烏溪沙', 'WHA': '黃埔', 'SSP': '觀塘',
    'LET': '海怡半島', 'SUN': '欣澳', 'DIS': '迪士尼'
};

async function fetchMTRData(line, station) {
    try {
        const url = `https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php?line=${line}&sta=${station}`;
        const response = await fetch(url);
        return response.ok ? await response.json() : null;
    } catch (error) {
        console.error(`獲取 ${line}-${station} 數據失敗:`, error);
        return null;
    }
}

async function getLineNextTrain(line) {
    for (const station of line.stations) {
        const data = await fetchMTRData(line.code, station);
        if (data?.status === 1) {
            const key = `${line.code}-${station}`;
            const stationData = data.data[key];
            const trains = [...(stationData?.UP || []), ...(stationData?.DOWN || [])];
            if (trains.length > 0) {
                const nextTrain = trains[0];
                return {
                    minutes: parseInt(nextTrain.ttnt) || 0,
                    dest: nextTrain.dest,
                    station: station,
                    delay: data.isdelay === 'Y'
                };
            }
        }
    }
    return null;
}

function formatTime(minutes) {
    if (minutes === 0) return '即將到達';
    if (minutes === 1) return '1分鐘';
    return `${minutes}分鐘`;
}

function getTimeClass(minutes) {
    if (minutes <= 1) return 'time-arriving';
    if (minutes <= 3) return 'time-soon';
    return 'time-normal';
}

async function updateAllLines() {
    const container = document.getElementById('mtrData');
    if (!container) return;
    
    container.innerHTML = `
        <div class="mtr-header">
            <span class="title">🚇 港鐵全線路實時狀態</span>
            <span class="refresh-btn" onclick="updateAllLines()" title="刷新數據">⟳</span>
        </div>
        <div class="loading-all">載入所有線路數據...</div>
    `;
    
    const promises = MTR_LINES.map(line => getLineNextTrain(line));
    const results = await Promise.all(promises);
    
    let html = `
        <div class="mtr-header">
            <span class="title">🚇 港鐵全線路實時狀態</span>
            <span class="refresh-btn" onclick="updateAllLines()" title="刷新數據">⟳</span>
        </div>
        <div class="lines-grid">
    `;
    
    MTR_LINES.forEach((line, index) => {
        const trainInfo = results[index];
        const hasData = trainInfo !== null;
        const minutes = hasData ? trainInfo.minutes : null;
        const isDelayed = hasData ? trainInfo.delay : false;
        
        html += `
            <div class="line-item" style="border-color: ${line.color};" 
                 onclick="showLineDetail('${line.code}')">
                <div class="line-header">
                    <span class="line-color" style="background-color: ${line.color};"></span>
                    <span class="line-name">${line.name}</span>
                    ${isDelayed ? '<span class="delay-badge">延誤</span>' : ''}
                </div>
                <div class="line-body">
        `;
        
        if (hasData) {
            const timeClass = getTimeClass(minutes);
            const timeText = formatTime(minutes);
            const destName = STATION_NAMES[trainInfo.dest] || trainInfo.dest;
            const stationName = STATION_NAMES[trainInfo.station] || trainInfo.station;
            
            html += `
                    <div class="train-info">
                        <div class="next-train ${timeClass}">${timeText}</div>
                        <div class="train-details">
                            <span class="station">${stationName}站</span>
                            <span class="dest">往 ${destName}</span>
                        </div>
                    </div>
            `;
        } else {
            html += `
                    <div class="no-data">
                        <span class="no-data-text">暫無數據</span>
                    </div>
            `;
        }
        
        html += `
                </div>
                <div class="line-footer">
                    <span class="click-hint">點擊查看詳情 →</span>
                </div>
            </div>
        `;
    });
    
    html += `
        </div>
        <div class="data-footer">
            <span class="update-time">更新時間: ${new Date().toLocaleTimeString('zh-HK')}</span>
            <span class="data-source">數據來源: data.gov.hk</span>
        </div>
    `;
    
    container.innerHTML = html;
    addMTRStyles();
    
    // 自動刷新
    setTimeout(updateAllLines, 30000);
}

async function showLineDetail(lineCode) {
    const container = document.getElementById('mtrData');
    const line = MTR_LINES.find(l => l.code === lineCode);
    if (!container || !line) return;
    
    container.innerHTML = `
        <div class="line-detail-header">
            <button class="back-btn" onclick="updateAllLines()">← 返回所有線路</button>
            <span class="line-title" style="color: ${line.color};">${line.name}</span>
        </div>
        <div class="line-stations-list">
            <div class="loading">載入車站數據...</div>
        </div>
    `;
    
    const promises = line.stations.map(station => fetchMTRData(line.code, station));
    const results = await Promise.all(promises);
    
    let html = '';
    
    line.stations.forEach((stationCode, index) => {
        const data = results[index];
        const stationName = STATION_NAMES[stationCode] || stationCode;
        
        html += `
            <div class="station-detail-card">
                <div class="station-header" style="border-color: ${line.color};">
                    <span class="station-name">${stationName}站</span>
                    <span class="station-code">${stationCode}</span>
                </div>
        `;
        
        if (data?.status === 1) {
            const key = `${line.code}-${stationCode}`;
            const stationData = data.data[key];
            
            if (stationData) {
                // 上行列車
                const upTrains = stationData.UP || [];
                if (upTrains.length > 0) {
                    html += '<div class="direction-section">';
                    html += '<div class="direction-label">上行</div>';
                    html += upTrains.slice(0, 2).map(train => {
                        const minutes = parseInt(train.ttnt) || 0;
                        const timeClass = getTimeClass(minutes);
                        const destName = STATION_NAMES[train.dest] || train.dest;
                        return `
                            <div class="train-item ${timeClass}">
                                <span class="train-dest">往 ${destName}</span>
                                <span class="train-time">${formatTime(minutes)}</span>
                                <span class="train-platform">月台 ${train.plat}</span>
                            </div>
                        `;
                    }).join('');
                    html += '</div>';
                }
                
                // 下行列車
                const downTrains = stationData.DOWN || [];
                if (downTrains.length > 0) {
                    html += '<div class="direction-section">';
                    html += '<div class="direction-label">下行</div>';
                    html += downTrains.slice(0, 2).map(train => {
                        const minutes = parseInt(train.ttnt) || 0;
                        const timeClass = getTimeClass(minutes);
                        const destName = STATION_NAMES[train.dest] || train.dest;
                        return `
                            <div class="train-item ${timeClass}">
                                <span class="train-dest">往 ${destName}</span>
                                <span class="train-time">${formatTime(minutes)}</span>
                                <span class="train-platform">月台 ${train.plat}</span>
                            </div>
                        `;
                    }).join('');
                    html += '</div>';
                }
                
                if (data.isdelay === 'Y') {
                    html += '<div class="delay-notice">⚠️ 此線路有延誤</div>';
                }
                
                html += `<div class="update-time">更新: ${data.sys_time.split(' ')[1]}</div>`;
            } else {
                html += '<div class="no-data">暫無列車數據</div>';
            }
        } else {
            html += '<div class="error">無法獲取數據</div>';
        }
        
        html += '</div>';
    });
    
    document.querySelector('.line-stations-list').innerHTML = html;
}

function addMTRStyles() {
    if (document.getElementById('mtr-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'mtr-styles';
    style.textContent = `
        .mtr-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .mtr-header .title {
            font-size: 1.3rem;
            font-weight: bold;
            color: #333;
        }
        
        .refresh-btn {
            cursor: pointer;
            font-size: 1.5rem;
            color: #007bff;
            transition: transform 0.3s;
            padding: 5px;
            border-radius: 50%;
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .refresh-btn:hover {
            transform: rotate(180deg);
            background: #f8f9fa;
        }
        
        .lines-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .line-item {
            background: white;
            border-radius: 12px;
            padding: 20px;
            border-top: 4px solid;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .line-item:hover {
            transform: translateY(-4px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        }
        
        .line-header {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .line-color {
            width: 16px;
            height: 16px;
            border-radius: 50%;
            margin-right: 10px;
        }
        
        .line-name {
            font-weight: bold;
            font-size: 1.1rem;
            flex-grow: 1;
        }
        
        .delay-badge {
            background: #dc3545;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        
        .line-body {
            margin: 15px 0;
        }
        
        .train-info {
            text-align: center;
        }
        
        .next-train {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 5px;
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
        
        .train-details {
            font-size: 0.9rem;
            color: #666;
        }
        
        .station {
            display: block;
            margin-bottom: 2px;
        }
        
        .dest {
            display: block;
            font-weight: 500;
        }
        
        .no-data {
            text-align: center;
            padding: 20px 0;
            color: #999;
        }
        
        .line-footer {
            text-align: right;
            font-size: 0.8rem;
            color: #007bff;
            font-weight: 500;
            padding-top: 10px;
            border-top: 1px solid #eee;
        }
        
        .data-footer {
            display: flex;
            justify-content: space-between;
            font-size: 0.8rem;
            color: #999;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }
        
        .line-detail-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .back-btn {
            padding: 8px 16px;
            background: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            margin-right: 15px;
        }
        
        .line-title {
            font-weight: bold;
            font-size: 1.2rem;
        }
        
        .line-stations-list {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .station-detail-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .station-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 3px solid;
        }
        
        .station-name {
            font-weight: bold;
            font-size: 1.1rem;
        }
        
        .station-code {
            font-size: 0.9rem;
            color: #999;
            font-family: monospace;
        }
        
        .direction-section {
            margin-bottom: 15px;
        }
        
        .direction-label {
            font-weight: bold;
            margin-bottom: 10px;
            color: #666;
        }
        
        .train-item {
            display: flex;
            align-items: center;
            padding: 10px;
            margin-bottom: 8px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .train-dest {
            flex-grow: 1;
            font-weight: 500;
        }
        
        .train-time {
            margin: 0 15px;
            font-weight: bold;
        }
        
        .train-platform {
            font-size: 0.9rem;
            color: #666;
        }
        
        .delay-notice {
            background: #fff3cd;
            color: #856404;
            padding: 10px;
            border-radius: 6px;
            margin: 15px 0;
            text-align: center;
            border: 1px solid #ffeaa7;
        }
        
        .update-time {
            font-size: 0.8rem;
            color: #999;
            text-align: right;
            margin-top: 10px;
        }
        
        .loading-all {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .error {
            text-align: center;
            padding: 20px;
            color: #dc3545;
        }
