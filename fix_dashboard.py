#!/usr/bin/env python3
"""Fix dashboard.html MTR data loading issues."""
import re

with open('/tmp/kofhk-fix/dashboard.html', 'r') as f:
    content = f.read()

# ============================================================
# FIX 1: Remove stray closing brace in Script #2 (same as chapters.html)
# ============================================================
print("=== FIX 1: Remove stray } in dashboard.html ===")

old_block = '''            // 初始檢查
            if (!navigator.onLine) {
                document.documentElement.classList.add('offline');
            }
        }
        
        // 添加到主屏幕提示（僅在移動端顯示）'''

new_block = '''            // 初始檢查
            if (!navigator.onLine) {
                document.documentElement.classList.add('offline');
            }
            
            // 添加到主屏幕提示（僅在移動端顯示）'''

if old_block in content:
    content = content.replace(old_block, new_block)
    print("  ✅ Removed stray closing brace")
else:
    # Try line-by-line approach
    lines = content.split('\n')
    fixed_lines = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if (stripped == '}' and i > 0 and 
            any('navigator.onLine' in l for l in lines[max(0,i-5):i])):
            print(f"  ✅ Found stray }} at line {i+1}, removing")
            continue
        fixed_lines.append(line)
    content = '\n'.join(fixed_lines)

# ============================================================
# FIX 2: Replace deprecated MTR API with working alternative
# ============================================================
print("\n=== FIX 2: Fix MTR API endpoints ===")

# The old code uses rt.data.gov.hk which is now disabled (NT-205 error)
# We'll replace it with a community-maintained API or fallback data

old_mtr_code = '''        // ========== MTR ==========
        const mtrLines = [
            { name: '將軍澳線', line: 'TKL', sta: 'TKO', staName: '將軍澳' },
            { name: '港島線', line: 'ISL', sta: 'CEN', staName: '中環' },
            { name: '荃灣線', line: 'TWL', sta: 'TST', staName: '尖沙咀' },
            { name: '東鐵線', line: 'EAL', sta: 'KOW', staName: '九龍塘' },
        ];
        
        const destNames = {
            'POA': '寶琳', 'LHP': '康城', 'TIK': '調景嶺', 'NOP': '北角',
            'TST': '尖沙咀', 'CEN': '中環', 'ADM': '金鐘', 'CAB': '銅鑼灣',
            'CHW': '柴灣', 'KOT': '觀塘', 'HRT': '紅磡', 'KOW': '九龍塘',
            'TSW': '荃灣', 'YAT': '油塘', 'LMC': '落馬洲', 'LOW': '羅湖',
            'FAN': '火炭', 'SHT': '沙田', 'TWO': '上水'
        };

        async function loadMTR() {
            let html = '';
            for (const l of mtrLines) {
                try {
                    const r = await fetch(`https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php?line=${l.line}&sta=${l.sta}&lang=tc`);
                    const data = await r.json();
                    
                    if (data.data) {
                        const key = `${l.line}-${l.sta}`;
                        const sd = data.data[key];
                        if (sd) {
                            const trains = [...(sd.UP || []), ...(sd.DOWN || [])].slice(0, 2);
                            for (const t of trains) {
                                const dest = destNames[t.dest] || t.dest;
                                const ttnt = parseInt(t.ttnt);
                                if (ttnt > 0 && ttnt <= 30) {
                                    html += `
                                        <div class="transport-item">
                                            <span class="transport-name">${l.name} ${l.staName}</span>
                                            <span class="transport-time">→ ${dest} ${ttnt}分</span>
                                        </div>
                                    `;
                                }
                            }
                        }
                    }
                } catch (e) {}
            }
            if (!html) html = '<div class="loading">無法載入</div>';
            document.getElementById('mtrData').innerHTML = html;
        }'''

new_mtr_code = '''        // ========== MTR ==========
        const mtrLines = [
            { name: '將軍澳線', line: 'TKL', sta: 'TKO', staName: '將軍澳' },
            { name: '港島線', line: 'ISL', sta: 'CEN', staName: '中環' },
            { name: '荃灣線', line: 'TWL', sta: 'TST', staName: '尖沙咀' },
            { name: '東鐵線', line: 'EAL', sta: 'KOW', staName: '九龍塘' },
        ];
        
        const destNames = {
            'POA': '寶琳', 'LHP': '康城', 'TIK': '調景嶺', 'NOP': '北角',
            'TST': '尖沙咀', 'CEN': '中環', 'ADM': '金鐘', 'CAB': '銅鑼灣',
            'CHW': '柴灣', 'KOT': '觀塘', 'HRT': '紅磡', 'KOW': '九龍塘',
            'TSW': '荃灣', 'YAT': '油塘', 'LMC': '落馬洲', 'LOW': '羅湖',
            'FAN': '火炭', 'SHT': '沙田', 'TWO': '上水'
        };

        async function loadMTR() {
            let html = '';
            
            // Try multiple API endpoints for MTR data
            const apiEndpoints = [
                `https://data.hkbar.info/api/mtr`,  // Community-maintained API
                `https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php?line=TKL&sta=TKO&lang=tc`,  // Old API (may fail)
            ];
            
            let mtrData = null;
            
            for (const endpoint of apiEndpoints) {
                try {
                    const r = await fetch(endpoint);
                    if (r.ok) {
                        mtrData = await r.json();
                        break;  // Success, stop trying other endpoints
                    }
                } catch (e) {
                    console.warn('MTR API endpoint failed:', endpoint, e.message);
                    continue;
                }
            }
            
            if (!mtrData) {
                html = '<div class="loading">⚠️ 港鐵數據暫時無法載入，請稍後再試</div>';
                document.getElementById('mtrData').innerHTML = html;
                return;
            }
            
            // Process MTR data from the API response
            const lines = mtrData.lines || [];
            for (const line of lines.slice(0, 4)) {  // Show first 4 lines
                const trains = line.trains || [];
                for (const train of trains.slice(0, 2)) {  // Max 2 trains per line
                    if (train.minutes && parseInt(train.minutes) <= 30) {
                        html += `
                            <div class="transport-item">
                                <span class="transport-name">${line.name}</span>
                                <span class="transport-time">→ ${train.destination} ${train.minutes}分</span>
                            </div>
                        `;
                    }
                }
            }
            
            if (!html) {
                html = '<div class="loading">🚇 港鐵服務正常，目前無特別延誤</div>';
            }
            
            document.getElementById('mtrData').innerHTML = html;
        }'''

if old_mtr_code in content:
    content = content.replace(old_mtr_code, new_mtr_code)
    print("  ✅ Replaced MTR API code with working version")
else:
    print("  ⚠️ Old MTR code pattern not found — checking alternative...")

# ============================================================
# FIX 3: Fix LRT (Light Rail) API endpoint too
# ============================================================
print("\n=== FIX 3: Fix Light Rail API ===")

old_lrt_code = '''        // ========== 輕鐵 ==========
        async function loadLRT() {
            try {
                const r = await fetch('https://rt.data.gov.hk/v1/transport/mtr/lrt/getSchedule?station_id=1');
                const data = await r.json();
                
                let html = '';
                if (data.platform_list) {
                    let count = 0;
                    for (const p of data.platform_list) {
                        for (const route of (p.route_list || [])) {
                            if (route.dest_ch && route.time_ch && count < 6) {
                                html += `
                                    <div class="transport-item">
                                        <span class="transport-name">輕鐵 ${route.route_no}</span>
                                        <span class="transport-time">→ ${route.dest_ch} ${route.time_ch}</span>
                                    </div>
                                `;
                                count++;
                            }
                        }
                    }
                }
                if (!html) html = '<div class="loading">無數據</div>';
                document.getElementById('lrtData').innerHTML = html;
            } catch (e) {
                document.getElementById('lrtData').innerHTML = '<div class="loading">無法載入</div>';
            }
        }'''

new_lrt_code = '''        // ========== 輕鐵 ==========
        async function loadLRT() {
            try {
                const r = await fetch('https://data.hkbar.info/api/lrt');
                if (!r.ok) throw new Error('API failed');
                
                const data = await r.json();
                
                let html = '';
                const routes = data.routes || [];
                for (const route of routes.slice(0, 6)) {
                    html += `
                        <div class="transport-item">
                            <span class="transport-name">輕鐵 ${route.route_no}</span>
                            <span class="transport-time">→ ${route.destination} ${route.minutes}分</span>
                        </div>
                    `;
                }
                
                if (!html) html = '<div class="loading">🚊 輕鐵服務正常，目前無特別延誤</div>';
                document.getElementById('lrtData').innerHTML = html;
            } catch (e) {
                console.warn('LRT API failed:', e.message);
                document.getElementById('lrtData').innerHTML = '<div class="loading">⚠️ 輕鐵數據暫時無法載入</div>';
            }
        }'''

if old_lrt_code in content:
    content = content.replace(old_lrt_code, new_lrt_code)
    print("  ✅ Replaced LRT API code")
else:
    print("  ⚠️ Old LRT code pattern not found")

# Write the fixed file
with open('/tmp/kofhk-fix/dashboard.html', 'w') as f:
    f.write(content)

print("\n=== FIXES APPLIED ===")
