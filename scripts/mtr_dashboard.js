/**
 * 港鐵全線路實時數據 - Dashboard 專用版本
 * 在 dashboard.html 中顯示所有10條線路
 */

// 港鐵線路配置
const MTR_LINES_DASHBOARD = [
    { code: 'AEL', name: '機場快線', color: '#0066CC', stations: ['HOK', 'AIR'], description: '機場快線' },
    { code: 'TCL', name: '東涌線', color: '#FF6600', stations: ['HOK', 'TUC'], description: '東涌線' },
    { code: 'TKL', name: '將軍澳線', color: '#8B5CF6', stations: ['NOP', 'TKO'], description: '將軍澳線' },
    { code: 'TWL', name: '荃灣線', color: '#E2231A', stations: ['TST', 'TSW'], description: '荃灣線' },
    { code: 'ISL', name: '港島線', color: '#0098D8', stations: ['CEN', 'CHW'], description: '港島線' },
    { code: 'EAL', name: '東鐵線', color: '#1FB25A', stations: ['ADM', 'LOW'], description: '東鐵線' },
    { code: 'TML', name: '屯馬線', color: '#803090', stations: ['TUM', 'WKS'], description: '屯馬線' },
    { code: 'KTL', name: '觀塘線', color: '#F9A01B', stations: ['WHA', 'SSP'], description: '觀塘線' },
    { code: 'SIL', name: '南港島線', color: '#999999', stations: ['ADM', 'LET'], description: '南港島線' },
    { code: 'DRL', name: '迪士尼線', color: '#FF6699', stations: ['SUN', 'DIS'], description: '迪士尼線' }
];

// 車站名稱映射
const STATION_NAMES_DASHBOARD = {
    'HOK': '香港', 'AIR': '機場', 'TUC': '東涌', 'NOP': '北角', 'TKO': '將軍澳',
    'TST': '尖沙咀', 'TSW': '荃灣', 'CEN': '中環', 'CHW': '柴灣', 'ADM': '金鐘',
    'LOW': '羅湖', 'TUM': '屯門', 'WKS': '烏溪沙', 'WHA': '黃埔', 'SSP': '觀塘',
    'LET': '海怡半島', 'SUN': '欣澳', 'DIS': '迪士尼'
};

// 全局變量
let mtrAutoRefreshInterval = null;

/**
 * 獲取港鐵實時數據
 */
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

/**
 * 獲取線路最近列車時間
 */
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
                    delay: data.isdelay === 'Y',
                    updateTime: data.sys_time
                };
            }
        }
    }
    return null;
}

/**
 * 格式化時間顯示
 */
function formatTime(minutes) {
    if (minutes === 0) return '即將到達';
    if (minutes === 1) return '1分鐘';
    return `${minutes}分鐘`;
}

/**
 * 獲取時間顏色類別
 */
function getTimeClass(minutes) {
    if (minutes <= 1) return 'time-arriving';
    if (minutes <= 3) return 'time-soon';
    return 'time-normal';
}

/**
 * 更新所有線路顯示
 */
async function updateAllLines() {
    const container = document.getElementById('mtrData');
    if (!container) return;
    
    // 顯示加載中
    container.innerHTML = `
        <div class="loading">
            載入港鐵全線路數據...
        </div>
    `;
    
    try {
        // 獲取所有線路數據
        const promises = MTR_LINES_DASHBOARD.map(line => getLineNextTrain(line));
        const results = await Promise.all(promises);
        
        let html = '<div class="mtr-lines-grid">';
        
        MTR_LINES_DASHBOARD.forEach((line, index) => {
            const trainInfo = results[index];
            const hasData = trainInfo !== null;
            const isDelayed = hasData ? trainInfo.delay : false;
            
            html += `
                <div class="mtr-line-card" style="border-color: ${line.color};" 
                     onclick="showMTRStationDetail('${line.code}', '${line.stations[0]}')">
                    <div class="line-header">
                        <span class="line-color" style="background-color: ${line.color};"></span>
                        <span class="line-name">${line.name}</span>
                        ${isDelayed ? '<span class="delay-badge">延誤</span>' : ''}
                    </div>
                    <div class="line-stations">
            `;
            
            // 顯示該線路的車站
            line.stations.forEach((stationCode, stationIndex) => {
                const stationData = stationIndex === 0 ? trainInfo : null;
                const stationName = STATION_NAMES_DASHBOARD[stationCode] || stationCode;
                
                html += `
                    <div class="station-item">
                        <span class="station-name">${stationName}站</span>
                `;
                
                if (stationData) {
                    const timeClass = getTimeClass(stationData.minutes);
                    const timeText = formatTime(stationData.minutes);
                    
                    html += `
                        <span class="next-train ${timeClass}">${timeText}</span>
                    `;
                } else {
                    html += `
                        <span class="next-train" style="color: #666;">--</span>
                    `;
                }
                
                html += `</div>`;
            });
            
            html += `
                    </div>
                    <div class="line-footer">
                        <span class="click-hint">點擊查看詳情</span>
                        ${hasData ? `<span style="font-size: 0.8rem;">${trainInfo.updateTime.split(' ')[1]}</span>` : ''}
                    </div>
                </div>
            `;
        });
        
        html += `
            </div>
            <div class="mtr-update-time">
                更新時間: ${new Date().toLocaleTimeString('zh-HK')} | 數據來源: data.gov.hk
            </div>
        `;
        
        container.innerHTML = html;
        
        // 啟動自動刷新
        startMTRAutoRefresh();
        
    } catch (error) {
        console.error('更新港鐵數據失敗:', error);
        container.innerHTML = `
            <div class="error" style="text-align: center; padding: 40px; color: #ff6b6b;">
                無法連接港鐵數據服務
                <br>
                <button onclick="updateAllLines()" style="margin-top: 15px; padding: 8px 16px; background: rgba(0,212,255,0.2); color: #00d4ff; border: none; border-radius: 6px; cursor: pointer;">
                    重試連接
                </button>
            </div>
        `;
    }
}

/**
 * 顯示車站詳情
 */
async function showMTRStationDetail(lineCode, stationCode) {
    const container = document.getElementById('mtrData');
    const line = MTR_LINES_DASHBOARD.find(l => l.code === lineCode);
    
    if (!container || !line) return;
    
    container.innerHTML = `
        <div class="station-detail-view">
            <div class="detail-header" style="border-color: ${line.color};">
                <button class="back-btn" onclick="updateAllLines()">← 返回所有線路</button>
                <span class="detail-title" style="color: ${line.color};">${line.name} - ${STATION_NAMES_DASHBOARD[stationCode] || stationCode}站</span>
            </div>
            <div class="loading">
                載入車站詳情中...
            </div>
        </div>
    `;
    
    try {
        const data = await fetchMTRData(lineCode, stationCode);
        
        if (data?.status === 1) {
            const key = `${lineCode}-${stationCode}`;
            const stationData = data.data[key];
            const stationName = STATION_NAMES_DASHBOARD[stationCode] || stationCode;
            
            let html = `
                <div class="station-detail-view">
                    <div class="detail-header" style="border-color: ${line.color};">
                        <button class="back-btn" onclick="updateAllLines()">← 返回所有線路</button>
                        <span class="detail-title" style="color: ${line.color};">${line.name} - ${stationName}站</span>
                    </div>
            `;
            
            if (stationData) {
                html += '<div class="station-detail-grid">';
                
                // 上行列車
                const upTrains = stationData.UP || [];
                if (upTrains.length > 0) {
                    html += `
                        <div class="direction-card">
                            <div class="direction-label">上行 (往市區方向)</div>
                            <div class="train-list">
                    `;
                    
                    upTrains.slice(0, 3).forEach(train => {
                        const minutes = parseInt(train.ttnt) || 0;
                        const timeClass = getTimeClass(minutes);
                        const timeText = formatTime(minutes);
                        const destName = STATION_NAMES_DASHBOARD[train.dest] || train.dest;
                        
                        html += `
                            <div class="train-item">
                                <span class="train-dest">往 ${destName}</span>
                                <span class="train-time ${timeClass}">${timeText}</span>
                                <span class="train-platform">月台 ${train.plat}</span>
                            </div>
                        `;
                    });
                    
                    html += `</div></div>`;
                }
                
                // 下行列車
                const downTrains = stationData.DOWN || [];
                if (downTrains.length > 0) {
                    html += `
                        <div class="direction-card">
                            <div class="direction-label">下行 (往郊區方向)</div>
                            <div class="train-list">
                    `;
                    
                    downTrains.slice(0, 3).forEach(train => {
                        const minutes = parseInt(train.ttnt) || 0;
                        const timeClass = getTimeClass(minutes);
                        const timeText = formatTime(minutes);
                        const destName = STATION_NAMES_DASHBOARD[train.dest] || train.dest;
                        
                        html += `
                            <div class="train-item">
                                <span class="train-dest">往 ${destName}</span>
                                <span class="train-time ${timeClass}">${timeText}</span>
                                <span class="train-platform">月台 ${train.plat}</span>
                            </div>
                        `;
                    });
                    
                    html += `</div></div>`;
                }
                
                html += '</div>';
                
                // 延誤狀態
                if (data.isdelay === 'Y') {
                    html += `
                        <div class="delay-notice">
                            ⚠️ 此線路目前有延誤，請留意車站廣播
                        </div>
                    `;
                }
                
                // 更新時間
                html += `
                    <div style="text-align: center; margin-top: 20px; color: #a0aec0; font-size: 0.9rem;">
                        數據更新時間: ${data.sys_time}
                    </div>
                `;
            } else {
                html += `
                    <div class="error" style="text-align: center; padding: 40px; color: #ff6b6b;">
                        暫無列車數據
                    </div>
                `;
            }
            
            html += '</div>';
            container.innerHTML = html;
        } else {
            container.innerHTML = `
                <div class="station-detail-view">
                    <div class="detail-header" style="border-color: ${line.color};">
                        <button class="back-btn" onclick="updateAllLines()">← 返回所有線路</button>
                        <span class="detail-title" style="color: ${line.color};">${line.name} - ${STATION_NAMES_DASHBOARD[stationCode] || stationCode}站</span>
                    </div>
                    <div class="error" style="text-align: center; padding: 40px; color: #ff6b6b;">
                        無法獲取車站數據
                        <br>
                        <button onclick="showMTRStationDetail('${lineCode}', '${stationCode}')" style="margin-top: 15px; padding: 8px 16px; background: rgba(0,212,255,0.2); color: #00d4ff; border: none; border-radius: 6px; cursor: pointer;">
                            重試
                        </button>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('加載車站詳情失敗:', error);
        container.innerHTML = `
            <div class="station-detail-view">
                <div class="detail-header" style="border-color: ${line.color};">
                    <button class="back-btn" onclick="updateAllLines()">← 返回所有線路</button>
                    <span class="detail-title" style="color: ${line.color};">${line.name} - ${STATION_NAMES_DASHBOARD[stationCode] || stationCode}站</span>
                </div>
                <div class="error" style="text-align: center; padding: 40px; color: #ff6b6b;">
                    網絡連接錯誤
                    <br>
                    <button onclick="showMTRStationDetail('${lineCode}', '${stationCode}')" style="margin-top: 15px; padding: 8px 16px; background: rgba(0,212,255,0.2); color: #00d4ff; border: none; border-radius: 6px; cursor: pointer;">
                        重試
                    </button>
                </div>
            </div>
        `;
    }
}

/**
 * 啟動自動刷新
 */
function startMTRAutoRefresh() {
    if (mtrAutoRefreshInterval) {
        clearInterval(mtrAutoRefreshInterval);
    }
    mtrAutoRefreshInterval = setInterval(updateAllLines, 30000); // 每30秒刷新
}

/**
 * 停止自動刷新
 */
function stopMTRAutoRefresh() {
    if (mtrAutoRefreshInterval) {
        clearInterval(mtrAutoRefreshInterval);
        mtrAutoRefreshInterval = null;
    }
}

/**
 * 頁面加載完成後初始化
 */
function initMTRDashboard() {
    // 等待頁面完全加載
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(updateAllLines, 1000);
        });
    } else {
        setTimeout(updateAllLines, 1000);
    }
    
    // 當頁面不可見時停止刷新，可見時恢復
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            stopMTRAutoRefresh();
        } else {
            startMTRAutoRefresh();
        }
    });
}

// 導出函數供全局使用
window.updateAllLines = updateAllLines;
window.showMTRStationDetail = showMTRStationDetail;
window.startMTRAutoRefresh = startMTRAutoRefresh;
window.stopMTRAutoRefresh = stopMTRAutoRefresh;

// 自動初始化
initMTRDashboard();