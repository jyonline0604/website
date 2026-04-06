#!/usr/bin/env python3
"""
Session Persistence - 會話持久化系統
基於 Claude Code Session Storage 的實現

功能：
1. 保存當前會話狀態
2. 保存最近的重要上下文
3. 自動恢復
"""

import os
import json
import time
from datetime import datetime

WORKSPACE = "/home/openclaw/.openclaw/workspace"
SESSION_FILE = os.path.join(WORKSPACE, ".session-state.json")

class SessionState:
    def __init__(self):
        self.last_activity = time.time()
        self.session_start = time.time()
        self.current_task = None
        self.completed_tasks = []
        self.failed_tasks = []
        self.important_context = {}
        self.pending_commits = []
        self.reminders = []
    
    def to_dict(self):
        return {
            "last_activity": self.last_activity,
            "session_start": self.session_start,
            "current_task": self.current_task,
            "completed_tasks": self.completed_tasks[-10:],  # 只保留最近10個
            "failed_tasks": self.failed_tasks[-5:],
            "important_context": self.important_context,
            "pending_commits": self.pending_commits,
            "reminders": self.reminders,
            "saved_at": datetime.now().isoformat()
        }
    
    @classmethod
    def from_dict(cls, d):
        state = cls()
        state.last_activity = d.get("last_activity", time.time())
        state.session_start = d.get("session_start", time.time())
        state.current_task = d.get("current_task")
        state.completed_tasks = d.get("completed_tasks", [])
        state.failed_tasks = d.get("failed_tasks", [])
        state.important_context = d.get("important_context", {})
        state.pending_commits = d.get("pending_commits", [])
        state.reminders = d.get("reminders", [])
        return state

class SessionPersistence:
    """
    會話持久化
    定期保存狀態，崩潰後可恢復
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.state = SessionState()
        self.load()
    
    def load(self):
        """加載上次會話狀態"""
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, 'r') as f:
                    data = json.load(f)
                self.state = SessionState.from_dict(data)
                return True
            except:
                pass
        return False
    
    def save(self):
        """保存當前狀態"""
        self.state.last_activity = time.time()
        with open(SESSION_FILE, 'w') as f:
            json.dump(self.state.to_dict(), f, indent=2, ensure_ascii=False)
    
    def set_current_task(self, task):
        """設置當前任務"""
        self.state.current_task = task
        self.save()
    
    def complete_task(self, task):
        """任務完成"""
        if task in self.state.failed_tasks:
            self.state.failed_tasks.remove(task)
        if task not in self.state.completed_tasks:
            self.state.completed_tasks.append({
                "task": task,
                "completed_at": datetime.now().isoformat()
            })
        self.state.current_task = None
        self.save()
    
    def fail_task(self, task, error):
        """任務失敗"""
        if task in self.state.completed_tasks:
            return
        if task not in [f["task"] for f in self.state.failed_tasks]:
            self.state.failed_tasks.append({
                "task": task,
                "error": error,
                "failed_at": datetime.now().isoformat()
            })
        self.state.current_task = None
        self.save()
    
    def add_context(self, key, value):
        """添加重要上下文"""
        self.state.important_context[key] = {
            "value": value,
            "added_at": datetime.now().isoformat()
        }
        self.save()
    
    def add_pending_commit(self, description):
        """添加待提交的文件"""
        if description not in self.state.pending_commits:
            self.state.pending_commits.append(description)
            self.save()
    
    def remove_pending_commit(self, description):
        """移除已提交"""
        if description in self.state.pending_commits:
            self.state.pending_commits.remove(description)
            self.save()
    
    def get_context(self, key):
        """獲取上下文"""
        return self.state.important_context.get(key, {}).get("value")
    
    def is_stale(self, hours=24):
        """會話是否過期（超過N小時無活動）"""
        return (time.time() - self.state.last_activity) > (hours * 3600)
    
    def get_summary(self):
        """獲取會話摘要"""
        return {
            "session_duration": time.time() - self.state.session_start,
            "tasks_completed": len(self.state.completed_tasks),
            "tasks_failed": len(self.state.failed_tasks),
            "pending_commits": len(self.state.pending_commits),
            "context_keys": list(self.state.important_context.keys()),
            "last_activity": datetime.fromtimestamp(self.state.last_activity).isoformat(),
            "is_stale": self.is_stale()
        }

def cmd_status():
    """顯示會話狀態"""
    sp = SessionPersistence()
    summary = sp.get_summary()
    
    print("=" * 50)
    print("📊 當前會話狀態")
    print("=" * 50)
    
    duration_hours = summary["session_duration"] / 3600
    print(f"會話時長: {duration_hours:.1f} 小時")
    print(f"完成任務: {summary['tasks_completed']}")
    print(f"失敗任務: {summary['tasks_failed']}")
    print(f"待提交: {summary['pending_commits']}")
    print(f"上下文: {summary['context_keys']}")
    print(f"最後活動: {summary['last_activity']}")
    print(f"過期: {'是 ⚠️' if summary['is_stale'] else '否 ✅'}")
    
    if sp.state.pending_commits:
        print("\n待提交：")
        for c in sp.state.pending_commits:
            print(f"  - {c}")
    
    if sp.state.failed_tasks:
        print("\n失敗任務：")
        for f in sp.state.failed_tasks[-3:]:
            print(f"  - {f['task']}: {f['error'][:50]}...")
    
    if sp.state.completed_tasks:
        print("\n最近完成：")
        for t in sp.state.completed_tasks[-3:]:
            print(f"  ✅ {t['task']}")

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    if cmd == "status":
        cmd_status()
    elif cmd == "save":
        sp = SessionPersistence()
        sp.save()
        print("✅ 會話已保存")
    elif cmd == "clear":
        sp = SessionPersistence()
        sp.state = SessionState()
        sp.save()
        print("✅ 會話已清除")
