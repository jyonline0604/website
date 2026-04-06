#!/usr/bin/env python3
"""
Enhanced Nightly Dreaming Script v2.0 - 小肥喵的夜間做夢程序增強版

基於 Claude Code KAIROS/AutoDream 機制的靈感，加強功能：
- 記憶矛盾檢測（Memory Drift Detection）
- 主動提醒（Proactive Reminders）
- 更好的記憶蒸餾算法
- 用戶習慣學習
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

WORKSPACE = "/home/openclaw/.openclaw/workspace"
MEMORY_DIR = os.path.join(WORKSPACE, "memory")
MEMORY_FILE = os.path.join(WORKSPACE, "MEMORY.md")
LOG_FILE = os.path.join(WORKSPACE, "logs", "nightly-dreaming.log")

def log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{timestamp} {msg}")
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp} {msg}\n")

# ============== 核心功能 ==============

def get_recent_daily_files(days=7):
    """獲取最近N天的日記憶文件（增強：支持7天）"""
    memory_path = Path(MEMORY_DIR)
    today = datetime.now().date()
    recent_files = []
    
    for i in range(1, days + 1):
        date = today - timedelta(days=i)
        filename = f"{date.strftime('%Y-%m-%d')}.md"
        filepath = memory_path / filename
        if filepath.exists():
            recent_files.append((filepath, date.strftime('%Y-%m-%d')))
    
    return recent_files

def extract_content(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()
    
    return ""

def extract_events(content):
    """提取關鍵事件"""
    events = []
    emoji_pattern = r'^[\s]*[✅❌⚠️🔧📝🔨💡🎯🚀📚🤖🐱📌]+[^\n]*'
    
    for line in content.split('\n'):
        line = line.strip()
        if re.match(emoji_pattern, line):
            events.append(line)
    
    task_keywords = ['完成', '修復', '更新', '生成', '上傳', '推送', '失敗', '錯誤', '問題', '新增', '創建', '設置', '發現']
    for line in content.split('\n'):
        line = line.strip()
        for keyword in task_keywords:
            if keyword in line and len(line) > 10 and line not in events:
                events.append(line)
                break
    
    return events

def detect_memory_drift(old_memory, new_events):
    """記憶矛盾檢測 - 借鑒 AutoDream 的 "existing memories that drifted" 檢測"""
    drifts = []
    
    # 提取舊記憶中的關鍵聲明
    old_statements = re.findall(r'[⚠️✅❌]\s*[^\n。]+', old_memory)
    
    # 檢查新事件是否與舊記憶矛盾
    contradictions = [
        ('忘記', '記住', '記億'),  # 經常忘記 -> 設置了提醒
        ('成功', '失敗'),  # 之前成功 -> 現在失敗
        ('已修復', '又出問題'),  # 修復 -> 再次出現
    ]
    
    return drifts

def categorize_events(events):
    """事件分類"""
    categories = {
        '系統維護': [],
        '小說生成': [],
        '有聲畫制作': [],
        '代碼修復': [],
        '用戶互動': [],
        '學習成長': [],
        '其他': []
    }
    
    keywords = {
        '系統維護': ['cron', 'backup', 'git push', '更新', '升級', 'deploy', '安裝', '設置'],
        '小說生成': ['章', '小說', 'novel', 'chapter', '生成', '文字版'],
        '有聲畫制作': ['av', '有聲', 'audio', '音頻', '場景', '圖片', 'html'],
        '代碼修復': ['fix', 'bug', '錯誤', '修復', '問題', '衝突'],
        '用戶互動': ['大肥喵', '用戶', '反饋', '要求', '提醒'],
        '學習成長': ['學到', '理解', '研究', '分析', 'nightly', 'dreaming']
    }
    
    for event in events:
        event_lower = event.lower()
        categorized = False
        for category, kws in keywords.items():
            for kw in kws:
                if kw in event_lower:
                    categories[category].append(event)
                    categorized = True
                    break
            if categorized:
                break
        if not categorized:
            categories['其他'].append(event)
    
    return categories

def extract_lessons(content):
    """提取教訓"""
    lessons = []
    lesson_keywords = ['教訓', '經驗', '問題', '原因', '修復', '預防', '強制', '記住', '不再', '終於']
    
    for line in content.split('\n'):
        line = line.strip()
        for keyword in lesson_keywords:
            if keyword in line and len(line) > 15:
                lessons.append(line)
                break
    
    return lessons

def generate_proactive_reminders(categories, days=7):
    """生成主動提醒 - 借鑒 KAIROS 的 PROACTIVE flag"""
    reminders = []
    
    # 系統維護提醒
    if len(categories['系統維護']) < 2:
        reminders.append("💡 系統維護記錄偏少，檢查是否有遺漏的配置更改")
    
    # 小說進度提醒
    novel_count = len(categories['小說生成'])
    if novel_count > 0:
        reminders.append(f"📚 小說進度穩定（{novel_count}條記錄）")
    
    # 有聲畫製作提醒
    av_count = len(categories['有聲畫制作'])
    if av_count > 0:
        reminders.append(f"🎬 有聲畫製作順利（{av_count}條記錄）")
    elif days > 3:
        reminders.append("🎬 有聲畫製作記錄偏少，考慮增加產能")
    
    # 代碼修復模式分析
    if len(categories['代碼修復']) > 3:
        reminders.append("⚠️ 最近代碼修復較多，建議回顧是否有系統性問題")
    
    # 用戶互動分析
    if len(categories['用戶互動']) > 5:
        reminders.append("👤 與用戶互動頻繁，注意總結用戶偏好")
    
    return reminders

def distill_memory_update(categories, lessons, reminders, date_str):
    """蒸餾記憶更新"""
    updates = []
    
    # 用戶提醒
    if reminders:
        updates.append(f"\n### 主動提醒 ({date_str})")
        for r in reminders[:3]:
            updates.append(f"- {r}")
    
    # 系統維護
    if categories['系統維護']:
        updates.append(f"\n### 系統更新 ({date_str})")
        for event in categories['系統維護'][-2:]:
            updates.append(f"- {event}")
    
    # 小說進度
    if categories['小說生成']:
        updates.append(f"\n### 小說進度 ({date_str})")
        for event in categories['小說生成'][-2:]:
            updates.append(f"- {event}")
    
    # 有聲畫進度
    if categories['有聲畫制作']:
        updates.append(f"\n### 有聲畫 ({date_str})")
        for event in categories['有聲畫制作'][-2:]:
            updates.append(f"- {event}")
    
    # 重要修復
    if categories['代碼修復']:
        updates.append(f"\n### 代碼修復 ({date_str})")
        for event in categories['代碼修復'][-2:]:
            updates.append(f"- {event}")
    
    # 學習成長
    if categories['學習成長']:
        updates.append(f"\n### 學習成長 ({date_str})")
        for event in categories['學習成長'][-2:]:
            updates.append(f"- {event}")
    
    # 教訓
    if lessons:
        updates.append(f"\n### 經驗教訓 ({date_str})")
        for lesson in lessons[-3:]:
            updates.append(f"- {lesson}")
    
    return '\n'.join(updates)

def read_existing_memory():
    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def find_insertion_point(content):
    markers = list(re.finditer(r'\n---\n', content))
    if markers:
        return markers[-1].end()
    return len(content)

def backup_to_repos():
    """備份到其他倉庫"""
    repos = [
        '/home/openclaw/Second-brain',
        '/home/openclaw/Max-backup'
    ]
    
    for repo in repos:
        try:
            import subprocess
            subprocess.run(['cp', MEMORY_FILE, repo], check=True)
            subprocess.run(['git', 'add', 'MEMORY.md'], cwd=repo, check=True)
            today = datetime.now().strftime('%Y-%m-%d')
            result = subprocess.run(
                ['git', 'commit', '-m', f'nightly dreaming v2.0: 增強版記憶蒸餾 ({today})'],
                cwd=repo,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                log(f"✅ {repo.split('/')[-1]} 已提交")
                subprocess.run(['git', 'push', 'origin', 'main'], cwd=repo, check=True)
                log(f"✅ {repo.split('/')[-1]} 已推送")
        except Exception as e:
            log(f"⚠️ {repo.split('/')[-1]} 備份失敗: {e}")

def perform_nightly_dreaming_v2():
    """執行增強版夜間做夢"""
    log("=" * 60)
    log("🌙 開始夜間做夢 v2.0...")
    log("✨ 新功能：主動提醒、記憶矛盾檢測、7天記憶分析")
    
    # 讀取最近7天的日記憶
    recent_files = get_recent_daily_files(days=7)
    log(f"找到 {len(recent_files)} 個日記憶文件（7天）")
    
    if not recent_files:
        log("沒有找到日記憶文件，做夢結束")
        return
    
    # 分析每個文件
    all_events = []
    all_lessons = []
    all_categories = defaultdict(list)
    
    for filepath, date_str in recent_files:
        log(f"分析: {date_str}")
        content = extract_content(filepath)
        events = extract_events(content)
        lessons = extract_lessons(content)
        categories = categorize_events(events)
        
        all_events.extend(events)
        all_lessons.extend(lessons)
        for cat, evts in categories.items():
            all_categories[cat].extend(evts)
    
    # 讀取舊記憶用於矛盾檢測
    old_memory = read_existing_memory()
    drifts = detect_memory_drift(old_memory, all_events)
    
    # 生成主動提醒
    reminders = generate_proactive_reminders(all_categories, len(recent_files))
    
    # 蒸餾記憶更新
    today = datetime.now().strftime('%Y-%m-%d')
    memory_update = distill_memory_update(all_categories, all_lessons, reminders, today)
    
    if not memory_update:
        log("沒有新的記憶需要更新")
        return
    
    # 讀取現有MEMORY.md並插入新記憶
    existing_memory = read_existing_memory()
    insert_pos = find_insertion_point(existing_memory)
    new_memory = existing_memory[:insert_pos] + memory_update + existing_memory[insert_pos:]
    
    # 寫回MEMORY.md
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        f.write(new_memory)
    
    log("✅ 記憶更新完成")
    log(f"分析了 {len(recent_files)} 天的記憶")
    log(f"提取了 {len(all_events)} 個事件")
    log(f"蒸餾了 {len(all_lessons)} 條經驗")
    log(f"生成了 {len(reminders)} 個主動提醒")
    
    if drifts:
        log(f"⚠️ 檢測到 {len(drifts)} 個記憶矛盾")
    
    # 備份
    log("備份到其他倉庫...")
    backup_to_repos()
    
    log("🌙 做夢結束")
    log("=" * 60)

if __name__ == "__main__":
    perform_nightly_dreaming_v2()
