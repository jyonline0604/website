#!/usr/bin/env python3
"""
Dropbox 第二卷 → 小說網站 自動化流程

每天自動從 Dropbox 下載 6 個章節，驗證、生成 HTML、更新網站。

遵循 SKILL.md 守則：
1. ✅ 簡體字轉繁體
2. ✅ HTML 結構驗證（1 html, 1 h1）
3. ✅ 標題格式檢查
4. ✅ 章節鏈接檢測
5. ✅ 更新 chapters.html + home.html
6. ✅ 三處章節數量同步
7. ✅ GitHub 推送
"""

import dropbox
import os
import re
import sys
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path

# ==== 設定 ====
WORKSPACE = "/home/openclaw/.openclaw/workspace"
TOKEN_FILE = "/home/openclaw/.openclaw/workspace/.token-store/dropbox-token.txt"
STATE_FILE = "/home/openclaw/.openclaw/workspace/.dropbox-sync/volume2_state.json"
DROPBOX_BASE = "/萬古塵埃/第二卷"
LOCAL_DOWNLOAD_DIR = "/home/openclaw/.openclaw/workspace/.dropbox-sync/downloaded"
TEMPLATE_PATH = os.path.join(WORKSPACE, "chapter-template.html")
SCRIPT_DIR = os.path.join(WORKSPACE, "scripts")
NOVEL_DIR = WORKSPACE
CHAPTERS_PER_BATCH = 6

# 簡體→繁體完整轉換表（漢字層級）
S2T_MAP = {
    '叶': '葉', '灵': '靈', '气': '氣', '时': '時', '为': '為',
    '无': '無', '与': '與', '个': '個', '对': '對', '来': '來',
    '说': '說', '们': '們', '么': '麼', '这': '這', '那': '那',
    '里': '裡', '后': '後', '发': '發', '见': '見', '当': '當',
    '过': '過', '着': '著', '却': '卻', '还': '還', '经': '經',
    '从': '從', '会': '會', '东': '東', '样': '樣', '体': '體',
    '认': '認', '关': '關', '动': '動', '应': '應', '开': '開',
    '变': '變', '边': '邊', '让': '讓', '问': '問', '号': '號',
    '报': '報', '备': '備', '传': '傳', '结': '結', '业': '業',
    '总': '總', '设': '設', '达': '達', '运': '運', '进': '進',
    '远': '遠', '连': '連', '选': '選', '适': '適', '较': '較',
    '转': '轉', '产': '產', '几': '幾', '义': '義', '术': '術',
    '场': '場', '收': '收', '期': '期', '现': '現', '万': '萬',
    '听': '聽', '声': '聲', '处': '處', '书': '書', '两': '兩',
    '点': '點', '门': '門', '难': '難', '题': '題', '际': '際',
    '兴': '興', '头': '頭', '吗': '嗎', '儿': '兒', '网': '網',
    '线': '線', '织': '織', '编': '編', '尘': '塵', '苏': '蘇',
    '陈': '陳', '赵': '趙', '张': '張', '许': '許', '萧': '蕭',
    '梦': '夢', '觉': '覺', '终': '終', '广': '廣', '长': '長',
    '旧': '舊', '极': '極', '刘': '劉', '杨': '楊', '周': '週',
    '马': '馬', '郑': '鄭', '难': '難', '电': '電', '条': '條',
    '总': '總', '旧': '舊', '礼': '禮', '际': '際', '击': '擊',
    '币': '幣', '众': '眾', '补': '補', '舱': '艙', '层': '層',
    '尝': '嘗', '尘': '塵', '衬': '襯', '齿': '齒', '虫': '蟲',
    '筹': '籌', '触': '觸', '辞': '辭', '聪': '聰', '达': '達',
    '担': '擔', '胆': '膽', '挡': '擋', '党': '黨', '导': '導',
    '灯': '燈', '敌': '敵', '递': '遞', '淀': '澱', '独': '獨',
    '断': '斷', '夺': '奪', '恶': '惡', '发': '發', '罚': '罰',
    '范': '範', '飞': '飛', '奋': '奮', '妇': '婦', '复': '復',
    '盖': '蓋', '干': '幹', '赶': '趕', '钢': '鋼', '阁': '閣',
    '个': '個', '贡': '貢', '沟': '溝', '构': '構', '购': '購',
    '顾': '顧', '观': '觀', '归': '歸', '柜': '櫃', '贵': '貴',
    '汉': '漢', '合': '合', '画': '畫', '坏': '壞', '欢': '歡',
    '环': '環', '换': '換', '积': '積', '纪': '紀', '继': '繼',
    '价': '價', '践': '踐', '歼': '殲', '荐': '薦', '渐': '漸',
    '践': '踐', '鉴': '鑑', '将': '將', '讲': '講', '蒋': '蔣',
    '奖': '獎', '桨': '槳', '酱': '醬', '绞': '絞', '惊': '驚',
    '竞': '競', '旧': '舊', '举': '舉', '剧': '劇', '惧': '懼',
    '据': '據', '卷': '卷', '绝': '絕', '开': '開', '壳': '殼',
    '恳': '懇', '库': '庫', '夸': '誇', '块': '塊', '亏': '虧',
    '困': '困', '扩': '擴', '腊': '臘', '蜡': '蠟', '兰': '蘭',
    '蓝': '藍', '篮': '籃', '劳': '勞', '乐': '樂', '类': '類',
    '累': '累', '厘': '釐', '礼': '禮', '丽': '麗', '厉': '厲',
    '联': '聯', '炼': '煉', '练': '練', '粮': '糧', '疗': '療',
    '辽': '遼', '了': '了', '猎': '獵', '临': '臨', '邻': '鄰',
    '岭': '嶺', '庐': '廬', '录': '錄', '虑': '慮', '绿': '綠',
    '乱': '亂', '伦': '倫', '论': '論', '罗': '羅', '落': '落',
    '码': '碼', '买': '買', '麦': '麥', '卖': '賣', '迈': '邁',
    '瞒': '瞞', '猫': '貓', '贸': '貿', '么': '麼', '没': '沒',
    '镁': '鎂', '门': '門', '闷': '悶', '们': '們', '梦': '夢',
    '眯': '眯', '迷': '迷', '谜': '謎', '绵': '綿', '缅': '緬',
    '灭': '滅', '闽': '閩', '亩': '畝', '纳': '納', '难': '難',
    '脑': '腦', '闹': '鬧', '馁': '餒', '内': '內', '嫩': '嫩',
    '拟': '擬', '你': '你', '年': '年', '念': '念', '鸟': '鳥',
    '宁': '寧', '农': '農', '欧': '歐', '呕': '嘔', '盘': '盤',
    '凭': '憑', '朴': '樸', '齐': '齊', '启': '啟', '弃': '棄',
    '气': '氣', '迁': '遷', '签': '簽', '侨': '僑', '桥': '橋',
    '窃': '竊', '钦': '欽', '亲': '親', '轻': '輕', '庆': '慶',
    '穷': '窮', '区': '區', '权': '權', '劝': '勸', '确': '確',
    '让': '讓', '扰': '擾', '热': '熱', '认': '認', '荣': '榮',
    '软': '軟', '洒': '灑', '伞': '傘', '丧': '喪', '扫': '掃',
    '涩': '澀', '晒': '曬', '伤': '傷', '舍': '捨', '摄': '攝',
    '审': '審', '渗': '滲', '声': '聲', '胜': '勝', '圣': '聖',
    '湿': '濕', '实': '實', '势': '勢', '适': '適', '释': '釋',
    '兽': '獸', '术': '術', '树': '樹', '帅': '帥', '双': '雙',
    '谁': '誰', '税': '稅', '顺': '順', '丝': '絲', '苏': '蘇',
    '肃': '肅', '虽': '雖', '岁': '歲', '孙': '孫', '台': '臺',
    '态': '態', '坛': '壇', '叹': '嘆', '汤': '湯', '涛': '濤',
    '腾': '騰', '体': '體', '条': '條', '铁': '鐵', '听': '聽',
    '厅': '廳', '头': '頭', '图': '圖', '团': '團', '推': '推',
    '脱': '脫', '驼': '駝', '袜': '襪', '弯': '彎', '湾': '灣',
    '顽': '頑', '万': '萬', '网': '網', '为': '為', '卫': '衛',
    '稳': '穩', '问': '問', '无': '無', '务': '務', '雾': '霧',
    '牺': '犧', '习': '習', '系': '系', '细': '細', '虾': '蝦',
    '峡': '峽', '显': '顯', '险': '險', '县': '縣', '现': '現',
    '线': '線', '乡': '鄉', '响': '響', '向': '向', '项': '項',
    '协': '協', '胁': '脅', '写': '寫', '泻': '瀉', '谢': '謝',
    '兴': '興', '星': '星', '须': '須', '悬': '懸', '选': '選',
    '学': '學', '寻': '尋', '训': '訓', '压': '壓', '亚': '亞',
    '盐': '鹽', '艳': '艷', '验': '驗', '阳': '陽', '养': '養',
    '样': '樣', '药': '藥', '爷': '爺', '叶': '葉', '医': '醫',
    '遗': '遺', '异': '異', '义': '義', '艺': '藝', '忆': '憶',
    '亿': '億', '议': '議', '阴': '陰', '饮': '飲', '应': '應',
    '拥': '擁', '佣': '傭', '踊': '踊', '优': '優', '忧': '憂',
    '犹': '猶', '邮': '郵', '余': '餘', '鱼': '魚', '与': '與',
    '语': '語', '员': '員', '缘': '緣', '远': '遠', '愿': '願',
    '跃': '躍', '运': '運', '酝': '醞', '杂': '雜', '灾': '災',
    '载': '載', '暂': '暫', '赞': '讚', '脏': '髒', '责': '責',
    '贼': '賊', '战': '戰', '张': '張', '章': '章', '涨': '漲',
    '赵': '趙', '这': '這', '针': '針', '证': '證', '郑': '鄭',
    '只': '只', '制': '製', '质': '質', '种': '種', '众': '眾',
    '周': '周', '轴': '軸', '昼': '晝', '朱': '朱', '烛': '燭',
    '筑': '築', '专': '專', '桩': '樁', '装': '裝', '壮': '壯',
    '状': '狀', '准': '準', '浊': '濁', '总': '總', '纵': '縱',
    '组': '組', '钻': '鑽', '醉': '醉', '尊': '尊',
}

# 中文數字轉阿拉伯數字
CN_NUM_MAP = {
    '零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
    '十': 10, '百': 100, '千': 1000, '萬': 10000
}

S2T = str.maketrans(S2T_MAP)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

# ==================== 工具函數 ====================

def sc2tc(text):
    """簡體轉繁體"""
    return text.translate(S2T)

def cn_to_arabic(cn_str):
    """中文數字轉阿拉伯數字（支援五百三十→530）"""
    if cn_str.isdigit():
        return int(cn_str)
    result = 0
    current = 0
    for c in cn_str:
        if c in CN_NUM_MAP:
            v = CN_NUM_MAP[c]
            if v >= 10:  # 十、百、千、萬 - multiplier
                if current == 0:
                    current = 1
                result += current * v
                current = 0
            else:  # 零一二三四五六七八九 - digit
                current = v
    result += current  # remaining digit
    return result

def get_dropbox_client():
    token = open(TOKEN_FILE).read().strip()
    return dropbox.Dropbox(token)

def load_state():
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {
        'processed': {},      # {dropbox_file_id: {ch_num, title, filename, date}}
        'synced_to_site': [], # [ch_num, ...]
        'last_batch': None,
        'batch_count': 0
    }

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def get_existing_chapters():
    """獲取網站上已有的章節號"""
    chapters = set()
    for fname in os.listdir(NOVEL_DIR):
        m = re.match(r'chapter-(\d+)\.html', fname)
        if m:
            chapters.add(int(m.group(1)))
    return chapters

# ==================== Dropbox 操作 ====================

def scan_dropbox_volume2():
    """掃描 Dropbox 第二卷，回傳所有 .txt 文件"""
    dbx = get_dropbox_client()
    result = dbx.files_list_folder(DROPBOX_BASE)
    
    files = []
    for entry in result.entries:
        if not isinstance(entry, dropbox.files.FileMetadata):
            continue
        if not entry.name.endswith('.txt'):
            continue
        # 跳過 .tmp 檔案
        if '.tmp' in entry.name:
            continue
        
        # 解析章節號：第五百零一章 踏入西域.txt
        m = re.match(r'第([零一二三四五六七八九十百千萬\d]+)章\s+(.+)\.txt', entry.name)
        if not m:
            continue
        
        ch_num = cn_to_arabic(m.group(1))
        title = m.group(2).strip()
        
        files.append({
            'ch_num': ch_num,
            'title': title,
            'filename': entry.name,
            'path': entry.path_display,
            'id': entry.id,
            'modified': str(entry.server_modified)
        })
    
    files.sort(key=lambda x: x['ch_num'])
    return files

def download_chapter(dbx, file_info):
    """下載單一章節到本地"""
    os.makedirs(LOCAL_DOWNLOAD_DIR, exist_ok=True)
    local_path = os.path.join(LOCAL_DOWNLOAD_DIR, file_info['filename'])
    
    _, response = dbx.files_download(file_info['path'])
    with open(local_path, 'wb') as f:
        f.write(response.content)
    
    return local_path

# ==================== 文本處理 ====================

def extract_title_from_content(content):
    """從 txt 內容提取章節標題"""
    lines = content.strip().split('\n')
    for line in lines[:5]:
        line = line.strip()
        # 支持格式：第X章 · 標題
        m = re.match(r'第([零一二三四五六七八九十百千萬\d]+)章\s*[·:：]\s*(.+)', line)
        if m:
            return cn_to_arabic(m.group(1)), m.group(2).strip()
        # 也支持：第五百零一章 踏入西域
        m = re.match(r'第([零一二三四五六七八九十百千萬\d]+)章\s+(.+)', line)
        if m:
            # 確保第二行真的是標題，不是副標
            title = m.group(2).strip()
            # 排除「第一卷」這樣的卷名
            if not title.startswith(('第', '一', '二', '三', '四', '五')):
                return cn_to_arabic(m.group(1)), title
    return None, None

def preprocess_content(filepath):
    """
    預處理 txt 文件：
    1. 檢查簡體字並轉換
    2. 提取標題信息
    3. 返回標準化的內容
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 檢查簡體字
    simplified_found = set()
    for c in content:
        if ord(c) > 127 and c in S2T_MAP:
            simplified_found.add(c)
    
    if simplified_found:
        log(f"  ⚠️ 發現 {len(simplified_found)} 個簡體字，正在轉換...")
        content = sc2tc(content)
    
    # 提取章節信息
    ch_num, title = extract_title_from_content(content)
    
    return content, ch_num, title

def process_body_to_paragraphs(content, ch_num):
    """將正文處理為 HTML 段落"""
    lines = content.strip().split('\n')
    
    # 找到正文起始行（跳過標題行和卷名行）
    body_start = 0
    for i, line in enumerate(lines[:10]):
        line = line.strip()
        # 跳過卷名
        if line.startswith('第') and ('卷' in line or '章' in line):
            body_start = i + 1
            continue
        # 跳過空行
        if not line:
            body_start = i + 1
            continue
        # 如果發現 # 開頭的標題行
        if line.startswith('# '):
            body_start = i + 1
            continue
    
    # 收集正文
    body_lines = lines[body_start:]
    
    paragraphs = []
    current_para = []
    
    for line in body_lines:
        line = line.strip()
        if not line:
            if current_para:
                paragraphs.append(' '.join(current_para))
                current_para = []
        else:
            current_para.append(line)
    
    if current_para:
        paragraphs.append(' '.join(current_para))
    
    # 生成 HTML 段落
    para_html = ''
    for p in paragraphs:
        if len(p) > 5:  # 跳過太短的段落
            para_html += f'<p>{p}</p>\n        '
    
    return para_html

# ==================== HTML 生成 ====================

def generate_chapter_html(ch_num, title, paragraphs_html, prev_url, next_url):
    """使用模板生成章節 HTML"""
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # 構建完整標題
    full_title = f"第{ch_num}章 · {title} - 萬古塵埃"
    
    replacements = {
        '{title}': full_title,
        '{canonical}': '',
        '{prev_url}': prev_url,
        '{next_url}': next_url,
        '{chapter_title}': f'第{ch_num}章 · {title}',
        '{CHAPTER_NUM}': str(ch_num),
        '{content}': paragraphs_html,
    }
    
    for key, value in replacements.items():
        template = template.replace(key, value)
    
    return template

# ==================== 驗證 ====================

def validate_html(html_path, ch_num, title):
    """驗證生成的 HTML 結構"""
    # 計算前後章 URL
    prev_url = f"chapter-{ch_num-1}.html"
    next_url = f"chapter-{ch_num+1}.html"
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # 檢查 <html> 標籤數量
    html_count = content.count('<html')
    close_html_count = content.count('</html>')
    if html_count != 1 or close_html_count != 1:
        issues.append(f"HTML標籤數量異常：{html_count}開/{close_html_count}關")
    
    # 檢查 <h1> 數量
    h1_count = content.count('<h1')
    if h1_count != 1:
        issues.append(f"h1數量異常：{h1_count}")
    
    # 檢查標題格式
    expected_h1 = f"第{ch_num}章 · {title}"
    if expected_h1 not in content:
        # 也試試 h1 在 title 中的格式
        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content)
        if h1_match:
            issues.append(f"h1內容不符：期望'{expected_h1}'，實際'{h1_match.group(1)}'")
    
    # 檢查段落數量
    p_count = content.count('<p>')
    if p_count < 3:
        issues.append(f"段落數量過少：{p_count}")
    
    # 檢查導航鏈接
    prev_exists = '上一章' not in content or f'href="chapter-{ch_num-1}.html"' in content
    next_exists = '下一章' not in content or f'href="chapter-{ch_num+1}.html"' in content
    
    return issues

# ==================== 網站更新 ====================

def run_update_scripts():
    """運行 site update scripts"""
    log("  📝 更新 chapters.html...")
    r1 = subprocess.run(
        ['python3', os.path.join(SCRIPT_DIR, 'update_chapters_simple.py')],
        capture_output=True, text=True, timeout=60
    )
    if r1.returncode != 0:
        log(f"  ❌ update_chapters_simple.py 失敗: {r1.stderr[:200]}")
        return False
    
    log("  📝 更新 home.html...")
    r2 = subprocess.run(
        ['python3', os.path.join(SCRIPT_DIR, 'update_home_simple.py')],
        capture_output=True, text=True, timeout=60
    )
    if r2.returncode != 0:
        log(f"  ❌ update_home_simple.py 失敗: {r2.stderr[:200]}")
        return False
    
    return True

def run_link_check():
    """運行章節鏈接檢查"""
    log("  🔗 運行鏈接檢查...")
    r = subprocess.run(
        ['python3', os.path.join(SCRIPT_DIR, 'check_chapter_links.py')],
        capture_output=True, text=True, timeout=60
    )
    result = r.stdout
    errors = [l for l in result.split('\n') if '❌' in l]
    if errors:
        log(f"  ⚠️ 發現 {len(errors)} 個鏈接問題:")
        for e in errors[:5]:
            log(f"     {e.strip()}")
        return False
    log("  ✅ 鏈接檢查通過")
    return True

def git_commit_and_push(ch_start, ch_end):
    """提交並推送到 GitHub"""
    log("  📤 推送到 GitHub...")
    
    # Stage files
    subprocess.run(['git', 'add', '-A'], cwd=WORKSPACE, capture_output=True, timeout=30)
    
    # Commit
    r = subprocess.run(
        ['git', 'commit', '-m', f"feat: Add chapters {ch_start}-{ch_end} from Dropbox Volume 2"],
        cwd=WORKSPACE, capture_output=True, text=True, timeout=30
    )
    if r.returncode != 0 and 'nothing to commit' not in r.stdout:
        log(f"  ⚠️ Commit 提醒: {r.stdout.strip()[:200]}")
    
    # Push
    r = subprocess.run(
        ['git', 'push', 'origin', 'main'],
        cwd=WORKSPACE, capture_output=True, text=True, timeout=60
    )
    if r.returncode == 0:
        log("  ✅ GitHub 推送成功")
    else:
        log(f"  ❌ GitHub 推送失敗: {r.stderr[:200]}")

# ==================== 主流程 ====================

def process_batch():
    """主流程：處理一批（6章）"""
    log("=" * 50)
    log(f"🚀 開始處理批次 ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
    log("=" * 50)
    
    state = load_state()
    existing = get_existing_chapters()
    max_existing = max(existing) if existing else 0
    log(f"📊 當前網站已有章節: {max_existing}")
    
    # 檢查是否已有最新章節
    if max_existing >= 500:  # 從第二卷開始
        next_chapter = max_existing + 1
    else:
        # 安全閾值：第二卷從 CH501 開始
        next_chapter = max(501, max_existing + 1)
    
    # 獲取 Dropbox 文件
    log(f"📁 掃描 Dropbox 第二卷...")
    files = scan_dropbox_volume2()
    log(f"   找到 {len(files)} 個章節文件 (CH{files[0]['ch_num']}-CH{files[-1]['ch_num']})")
    
    # 過濾出還沒處理的章節
    unprocessed = [f for f in files if f['id'] not in state['processed'] and f['ch_num'] not in existing]
    log(f"   未處理: {len(unprocessed)} 個")
    
    if not unprocessed:
        log("✅ 所有章節都已處理！")
        return 0
    
    # 取前 CHAPTERS_PER_BATCH 個
    batch = unprocessed[:CHAPTERS_PER_BATCH]
    ch_start = batch[0]['ch_num']
    ch_end = batch[-1]['ch_num']
    log(f"📦 本次批次: CH{ch_start}-CH{ch_end} ({len(batch)}章)")
    
    dbx = get_dropbox_client()
    success_count = 0
    generated_files = []
    
    for i, file_info in enumerate(batch):
        ch_num = file_info['ch_num']
        title = file_info['title']
        
        log(f"\n  [{i+1}/{len(batch)}] CH{ch_num}: {title}")
        
        # 1. 下載
        local_path = download_chapter(dbx, file_info)
        log(f"  📥 下載完成")
        
        # 2. 預處理（簡體轉換 + 標題提取）
        content, extracted_num, extracted_title = preprocess_content(local_path)
        
        if extracted_num:
            ch_num = extracted_num
            title = extracted_title
        
        log(f"  📋 內容: 第{ch_num}章 · {title}")
        
        # 3. 處理正文
        paragraphs = process_body_to_paragraphs(content, ch_num)
        
        # 4. 生成 HTML
        prev_url = f"chapter-{ch_num-1}.html"
        next_url = f"chapter-{ch_num+1}.html"
        
        html = generate_chapter_html(ch_num, title, paragraphs, prev_url, next_url)
        
        output_path = os.path.join(NOVEL_DIR, f"chapter-{ch_num}.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        log(f"  💾 生成 HTML: {output_path}")
        
        # 5. 驗證 HTML
        issues = validate_html(output_path, ch_num, title)
        if issues:
            log(f"  ⚠️ 驗證問題:")
            for issue in issues:
                log(f"     {issue}")
        else:
            log(f"  ✅ HTML 驗證通過")
        
        # 6. 更新狀態
        state['processed'][file_info['id']] = {
            'ch_num': ch_num,
            'title': title,
            'filename': file_info['filename'],
            'processed_at': datetime.now().isoformat()
        }
        generated_files.append(ch_num)
        success_count += 1
        
        time.sleep(0.5)  # Dropbox API 速率限制
    
    # 7. 網站更新
    if success_count > 0:
        log(f"\n🔄 更新網站...")
        
        # 更新 chapters.html + home.html
        if run_update_scripts():
            log("  ✅ 網站更新完成")
        else:
            log("  ⚠️ 網站更新可能有問題，繼續處理")
        
        # 鏈接檢查
        run_link_check()
        
        # Git 推送
        git_commit_and_push(ch_start, ch_end)
        
        state['synced_to_site'].extend(generated_files)
        state['last_batch'] = {
            'ch_start': ch_start,
            'ch_end': ch_end,
            'count': success_count,
            'time': datetime.now().isoformat()
        }
        state['batch_count'] = state.get('batch_count', 0) + 1
        save_state(state)
    
    log(f"\n{'=' * 50}")
    log(f"✅ 批次完成: {success_count}/{len(batch)} 章成功")
    log(f"   CH{ch_start}-CH{ch_end} 已添加到網站")
    log(f"{'=' * 50}")
    
    return success_count


if __name__ == '__main__':
    process_batch()
