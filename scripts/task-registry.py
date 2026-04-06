#!/usr/bin/env python3
"""
Task Registry System - 任務追蹤系統
基於 Claude Code TaskRegistry 的實現

功能：
1. 任務狀態追蹤 (Created → Running → Completed/Failed/Stopped)
2. 任務歷史記錄
3. 失敗重試計數
4. 任務計時
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from enum import Enum

WORKSPACE = "/home/openclaw/.openclaw/workspace"
TASKS_DIR = os.path.join(WORKSPACE, ".tasks")

class TaskStatus(Enum):
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"

class Task:
    def __init__(self, task_id, prompt, description=None):
        self.task_id = task_id
        self.prompt = prompt
        self.description = description
        self.status = TaskStatus.CREATED
        self.created_at = time.time()
        self.updated_at = time.time()
        self.started_at = None
        self.completed_at = None
        self.output = ""
        self.retry_count = 0
        self.error = None
    
    def to_dict(self):
        return {
            "task_id": self.task_id,
            "prompt": self.prompt,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "output": self.output,
            "retry_count": self.retry_count,
            "error": self.error
        }
    
    @classmethod
    def from_dict(cls, d):
        task = cls(d["task_id"], d["prompt"], d.get("description"))
        task.status = TaskStatus(d["status"])
        task.created_at = d["created_at"]
        task.updated_at = d["updated_at"]
        task.started_at = d.get("started_at")
        task.completed_at = d.get("completed_at")
        task.output = d.get("output", "")
        task.retry_count = d.get("retry_count", 0)
        task.error = d.get("error")
        return task

class TaskRegistry:
    """
    任務註冊表
    基於 Claude Code Rust 實現：Arc<Mutex<HashMap<String, Task>>>
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
        self.tasks = {}
        self.counter = 0
        self.tasks_file = os.path.join(TASKS_DIR, "registry.json")
        self.load()
    
    def _ensure_dir(self):
        os.makedirs(TASKS_DIR, exist_ok=True)
    
    def create(self, prompt, description=None):
        """創建新任務"""
        self.counter += 1
        task_id = f"task-{self.counter:04d}"
        task = Task(task_id, prompt, description)
        self.tasks[task_id] = task
        self.save()
        return task
    
    def get(self, task_id):
        """獲取任務"""
        return self.tasks.get(task_id)
    
    def update(self, task):
        """更新任務"""
        task.updated_at = time.time()
        self.tasks[task.task_id] = task
        self.save()
    
    def start(self, task_id):
        """開始任務"""
        task = self.get(task_id)
        if task:
            task.status = TaskStatus.RUNNING
            task.started_at = time.time()
            task.updated_at = time.time()
            self.save()
            return task
        return None
    
    def complete(self, task_id, output=""):
        """任務完成"""
        task = self.get(task_id)
        if task:
            task.status = TaskStatus.COMPLETED
            task.completed_at = time.time()
            task.output = output
            task.updated_at = time.time()
            self.save()
            return task
        return None
    
    def fail(self, task_id, error):
        """任務失敗"""
        task = self.get(task_id)
        if task:
            task.status = TaskStatus.FAILED
            task.error = error
            task.retry_count += 1
            task.updated_at = time.time()
            self.save()
            return task
        return None
    
    def stop(self, task_id):
        """停止任務"""
        task = self.get(task_id)
        if task:
            task.status = TaskStatus.STOPPED
            task.completed_at = time.time()
            task.updated_at = time.time()
            self.save()
            return task
        return None
    
    def list_tasks(self, status=None):
        """列出任務"""
        if status is None:
            return list(self.tasks.values())
        return [t for t in self.tasks.values() if t.status == status]
    
    def get_duration(self, task_id):
        """獲取任務耗時（秒）"""
        task = self.get(task_id)
        if task and task.started_at:
            end = task.completed_at or time.time()
            return end - task.started_at
        return 0
    
    def save(self):
        """持久化"""
        self._ensure_dir()
        data = {
            "counter": self.counter,
            "tasks": {k: v.to_dict() for k, v in self.tasks.items()}
        }
        with open(self.tasks_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self):
        """加載"""
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, 'r') as f:
                    data = json.load(f)
                self.counter = data.get("counter", 0)
                self.tasks = {k: Task.from_dict(v) for k, v in data.get("tasks", {}).items()}
            except:
                self.tasks = {}
                self.counter = 0

# ============== Circuit Breaker ==============

class CircuitBreaker:
    """
    熔斷器 - 防止連續失敗
    基於 Claude Code 的 MAX_CONSECUTIVE_FAILURES 設計
    """
    _instance = None
    
    def __new__(cls, max_failures=3):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, max_failures=3):
        if self._initialized:
            return
        self._initialized = True
        self.max_failures = max_failures
        self.state_file = os.path.join(WORKSPACE, ".circuit-breaker.json")
        self.state = self._load()
    
    def _load(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"consecutive_failures": 0, "last_failure": None}
    
    def _save(self):
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f)
    
    def record_success(self):
        """記錄成功，重置計數"""
        self.state["consecutive_failures"] = 0
        self._save()
    
    def record_failure(self):
        """記錄失敗"""
        self.state["consecutive_failures"] += 1
        self.state["last_failure"] = time.time()
        self._save()
    
    def is_open(self):
        """熔斷器是否打開（阻止執行）"""
        return self.state["consecutive_failures"] >= self.max_failures
    
    def get_wait_time(self):
        """獲取需要等待的時間（秒）"""
        if self.state["last_failure"]:
            elapsed = time.time() - self.state["last_failure"]
            return max(0, 60 - elapsed)  # 失敗後等60秒
        return 0
    
    def reset(self):
        """重置熔斷器"""
        self.state = {"consecutive_failures": 0, "last_failure": None}
        self._save()

# =============# CLI Interface ==============

def cmd_create(prompt, desc=None):
    registry = TaskRegistry()
    task = registry.create(prompt, desc)
    print(f"✅ 任務已創建: {task.task_id}")
    return task

def cmd_list(status=None):
    registry = TaskRegistry()
    tasks = registry.list_tasks()
    if not tasks:
        print("沒有任務")
        return
    for t in tasks:
        duration = registry.get_duration(t.task_id)
        print(f"{t.task_id} | {t.status.value:10} | {t.prompt[:50]}...")
        if duration > 0:
            print(f"         | 耗時: {duration:.1f}秒")

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    
    if cmd == "create":
        prompt = sys.argv[2] if len(sys.argv) > 2 else "Default task"
        desc = sys.argv[3] if len(sys.argv) > 3 else None
        cmd_create(prompt, desc)
    elif cmd == "list":
        cmd_list()
    elif cmd == "status":
        cb = CircuitBreaker()
        print(f"熔斷器狀態: {'打開' if cb.is_open() else '關閉'}")
        print(f"連續失敗: {cb.state['consecutive_failures']}/{cb.max_failures}")
    elif cmd == "reset":
        cb = CircuitBreaker()
        cb.reset()
        print("熔斷器已重置")
