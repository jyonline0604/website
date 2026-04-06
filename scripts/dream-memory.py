#!/usr/bin/env python3
"""
Dream Memory System - 小肥喵的記憶整合系統
基於 Claude Code AutoDream 機制的實現

功能：
1. Triple Gate: 時間檢查 + 會話數檢查 + 鎖文件
2. Consolidation Lock: 防止多進程衝突
3. 記憶蒸餾: 自動從日記憶提取重要信息
4. Proactive Reminders: 主動提醒重要事項
"""

import os
import re
import sys
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

WORKSPACE = "/home/openclaw/.openclaw/workspace"
MEMORY_DIR = os.path.join(WORKSPACE, "memory")
MEMORY_FILE = os.path.join(WORKSPACE, "MEMORY.md")
LOCK_FILE = os.path.join(WORKSPACE, ".dream-lock")
LOG_FILE = os.path.join(WORKSPACE, "logs", "dream.log")

# 配置
CONFIG = {
    "min_hours": 24,      # 距離上次整合至少24小時
    "min_sessions": 3,   # 至少3個新會話
    "lock_stale_ms": 60 * 60 * 1000,  # 60分鐘後鎖過期
}

def log(msg):
    """寫日誌"""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{timestamp} {msg}")
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp} {msg}\n")

# ============== Triple Gate System ==============

def read_last_consolidated_at():
    """讀取上次整合時間（mtime作為時間戳）"""
    try:
        s = os.stat(LOCK_FILE)
        return s.st_mtime  # mtime = lastConsolidatedAt
    except FileNotFoundError:
        return 0

def is_process_running(pid):
    """檢查PID是否存活"""
    try:
        os.kill(pid, 0)  # signal 0 just checks existence
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True  # Permission denied but process exists

def try_acquire_lock():
    """
    嘗試獲取整合鎖
    成功 → 返回prior_mtime用於失敗時回滾
    失敗 → 返回None
    """
    now = time.time()
    
    # 檢查現有鎖
    prior_mtime = None
    holder_pid = None
    
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, 'r') as f:
                content = f.read().strip()
                if content:
                    holder_pid = int(content)
            s = os.stat(LOCK_FILE)
            prior_mtime = s.st_mtime
            
            # 檢查鎖是否有效（60分鐘內且PID存活）
            if (now - prior_mtime) * 1000 < CONFIG["lock_stale_ms"]:
                if holder_pid and is_process_running(holder_pid):
                    log(f"[Dream] 鎖被PID {holder_pid}持有（{int(now - prior_mtime)}秒前），跳過")
                    return None
        except (ValueError, FileNotFoundError):
            pass
    
    # 嘗試獲取鎖
    try:
        os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)
        with open(LOCK_FILE, 'w') as f:
            f.write(str(os.getpid()))
        
        # 驗證我們真的拿到了鎖
        with open(LOCK_FILE, 'r') as f:
            verify = f.read().strip()
        if verify == str(os.getpid()):
            log(f"[Dream] 獲取鎖成功，PID={os.getpid()}")
            return prior_mtime or 0
        else:
            log("[Dream] 獲取鎖失敗（被其他進程搶走）")
            return None
            
    except Exception as e:
        log(f"[Dream] 獲取鎖異常: {e}")
        return None

def rollback_lock(prior_mtime):
    """失敗時回滾鎖"""
    try:
        if prior_mtime == 0:
            os.unlink(LOCK_FILE)
        else:
            # 回滾mtime
            os.utime(LOCK_FILE, (prior_mtime, prior_mtime))
        log(f"[Dream] 鎖回滾成功")
    except Exception as e:
        log(f"[Dream] 鎖回滾失敗: {e}")

def release_lock():
    """釋放鎖"""
    try:
        os.unlink(LOCK_FILE)
    except FileNotFoundError:
        pass

# ============== Gate System ==============

def check_time_gate():
    """Gate 1: 時間檢查"""
    last_consolidated = read_last_consolidated_at()
    hours_since = (time.time() - last_consolidated) / 3600
    log(f"[Gate] 距離上次整合: {hours_since:.1f}小時")
    return hours_since >= CONFIG["min_hours"]

def check_session_gate():
    """Gate 2: 會話數檢查"""
    today = datetime.now().date()
    session_count = 0
    
    # 計算最近記憶文件數量
    for i in range(1, CONFIG["min_hours"] + 1):
        date = today - timedelta(days=i)
        filename = f"{date.strftime('%Y-%m-%d')}.md"
        filepath = Path(MEMORY_DIR) / filename
        if filepath.exists():
            session_count += 1
    
    log(f"[Gate] 最近24小時內有: {session_count}個記憶文件")
    return session_count >= CONFIG["min_sessions"]

# ============== Memory Processing ==============

def get_memory_files():
    """獲取最近N天的記憶文件"""
    memory_path = Path(MEMORY_DIR)
    today = datetime.now().date()
    files = []
    
    for i in range(1, CONFIG["min_hours"] + 2):
        date = today - timedelta(days=i)
        filename = f"{date.strftime('%Y-%m-%d')}.md"
        filepath = memory_path / filename
        if filepath.exists():
            files.append((filepath, date.strftime('%Y-%m-%d')))
    
    return files

def extract_events(content):
    """提取關鍵事件"""
    events = []
    
    # Emoji開頭的行
    emoji_re = re.compile(r'^[\s]*[✅❌⚠️🔧📝🔨💡🎯🚀📚🤖🐱📌]+[^\n]*')
    for line in content.split('\n'):
        line = line.strip()
        if emoji_re.match(line):
            events.append(line)
    
    # 關鍵詞匹配
    keywords = ['完成', '修復', '更新', '生成', '上傳', '推送', '失敗', '錯誤', '問題', '新增', '創建', '設置', '發現']
    for line in content.split('\n'):
        line = line.strip()
        for keyword in keywords:
            if keyword in line and len(line) > 10 and line not in events:
                events.append(line)
                break
    
    return events

def categorize_events(events):
    """分類事件"""
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

def generate_reminders(categories, session_count):
    """生成主動提醒"""
    reminders = []
    
    if len(categories['系統維護']) < 2:
        reminders.append("💡 系統維護記錄偏少")
    
    if len(categories['有聲畫制作']) == 0 and session_count > 2:
        reminders.append("🎬 有聲畫製作記錄偏少")
    
    if len(categories['代碼修復']) > 3:
        reminders.append("⚠️ 代碼修復較多，回顧是否有系統性問題")
    
    if len(categories['用戶互動']) > 5:
        reminders.append("👤 與用戶互動頻繁")
    
    return reminders[:3]

# ============== Memory Update ==============

def distill_memory(categories, lessons, reminders, date_str):
    """蒸餾記憶"""
    updates = []
    
    if reminders:
        updates.append(f"\n### 主動提醒 ({date_str})")
        for r in reminders:
            updates.append(f"- {r}")
    
    for cat_name, events in categories.items():
        if events:
            updates.append(f"\n### {cat_name} ({date_str})")
            for event in events[-2:]:
                updates.append(f"- {event}")
    
    if lessons:
        updates.append(f"\n### 經驗教訓 ({date_str})")
        for lesson in lessons[-3:]:
            updates.append(f"- {lesson}")
    
    return '\n'.join(updates)

def read_memory():
    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def find_insert_point(content):
    """找到最後一個---分隔線"""
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
                ['git', 'commit', '-m', f'dream: memory consolidation ({today})'],
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

# ============== Main Dream Process ==============

def dream():
    """執行記憶整合"""
    log("=" * 60)
    log("🌙 開始 Dream Memory 整合...")
    
    # Gate 1: 時間檢查
    if not check_time_gate():
        log("⏰ 時間Gate未通過，跳過")
        return
    
    # Gate 2: 會話數檢查
    if not check_session_gate():
        log("📊 會話Gate未通過，跳過")
        return
    
    # Gate 3: 嘗試獲取鎖
    prior_mtime = try_acquire_lock()
    if prior_mtime is None:
        log("🔒 鎖未獲取，跳過")
        return
    
    try:
        # 讀取記憶文件
        files = get_memory_files()
        log(f"📁 找到 {len(files)} 個記憶文件")
        
        if not files:
            log("沒有記憶文件")
            return
        
        # 分析每個文件
        all_events = []
        all_lessons = []
        all_categories = defaultdict(list)
        
        for filepath, date_str in files:
            log(f"分析: {date_str}")
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            events = extract_events(content)
            lessons = extract_lessons(content)
            categories = categorize_events(events)
            
            all_events.extend(events)
            all_lessons.extend(lessons)
            for cat, evts in categories.items():
                all_categories[cat].extend(evts)
        
        # 生成提醒
        reminders = generate_reminders(all_categories, len(files))
        
        # 蒸餾記憶
        today = datetime.now().strftime('%Y-%m-%d')
        memory_update = distill_memory(all_categories, all_lessons, reminders, today)
        
        if not memory_update:
            log("沒有新記憶")
            return
        
        # 更新MEMORY.md
        existing = read_memory()
        insert_pos = find_insert_point(existing)
        new_memory = existing[:insert_pos] + memory_update + existing[insert_pos:]
        
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            f.write(new_memory)
        
        log(f"✅ 記憶整合完成")
        log(f"   事件: {len(all_events)}")
        log(f"   教訓: {len(all_lessons)}")
        log(f"   提醒: {len(reminders)}")
        
        # 備份
        backup_to_repos()
        
    finally:
        # 釋放鎖
        release_lock()
    
    log("🌙 Dream 結束")
    log("=" * 60)

if __name__ == "__main__":
    dream()
