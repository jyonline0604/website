#!/usr/bin/env python3
"""
TaskRegistry - 簡單的任務追蹤系統
基於 Claude Code TaskRegistry 概念設計

用途：
- 記錄所有任務及其狀態
- 追蹤任務進度
- 防止重複執行
"""

import json
import os
from datetime import datetime
from enum import Enum

TASKS_FILE = "/home/openclaw/.openclaw/workspace/.tasks.json"

class TaskStatus(Enum):
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"

class Task:
    def __init__(self, task_id: str, prompt: str, description: str = ""):
        self.task_id = task_id
        self.prompt = prompt
        self.description = description
        self.status = TaskStatus.CREATED
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "task_id": self.task_id,
            "prompt": self.prompt,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @staticmethod
    def from_dict(data):
        task = Task(data["task_id"], data["prompt"], data.get("description", ""))
        task.status = TaskStatus(data["status"])
        task.created_at = data["created_at"]
        task.updated_at = data["updated_at"]
        return task

class TaskRegistry:
    def __init__(self):
        self.tasks = {}
        self.load()
    
    def load(self):
        """從檔案載入任務"""
        if os.path.exists(TASKS_FILE):
            try:
                with open(TASKS_FILE, 'r') as f:
                    data = json.load(f)
                    self.tasks = {k: Task.from_dict(v) for k, v in data.items()}
            except:
                self.tasks = {}
    
    def save(self):
        """儲存任務到檔案"""
        with open(TASKS_FILE, 'w') as f:
            data = {k: v.to_dict() for k, v in self.tasks.items()}
            json.dump(data, f, indent=2)
    
    def create(self, task_id: str, prompt: str, description: str = "") -> Task:
        """創建新任務"""
        task = Task(task_id, prompt, description)
        self.tasks[task_id] = task
        self.save()
        return task
    
    def get(self, task_id: str) -> Task:
        """獲取任務"""
        return self.tasks.get(task_id)
    
    def update_status(self, task_id: str, status: TaskStatus):
        """更新任務狀態"""
        if task_id in self.tasks:
            self.tasks[task_id].status = status
            self.tasks[task_id].updated_at = datetime.now().isoformat()
            self.save()
    
    def list_tasks(self, status: TaskStatus = None):
        """列出任務"""
        if status:
            return [t for t in self.tasks.values() if t.status == status]
        return list(self.tasks.values())
    
    def delete(self, task_id: str):
        """刪除任務"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self.save()
    
    def is_running(self, task_id: str) -> bool:
        """檢查任務是否正在執行"""
        task = self.get(task_id)
        return task and task.status == TaskStatus.RUNNING
    
    def report(self) -> str:
        """生成任務報告"""
        lines = ["📋 Task Registry Report", "=" * 30]
        
        by_status = {}
        for task in self.tasks.values():
            status = task.status.value
            by_status[status] = by_status.get(status, 0) + 1
        
        lines.append(f"總任務數：{len(self.tasks)}")
        for status, count in by_status.items():
            lines.append(f"  {status}: {count}")
        
        lines.append("")
        lines.append("最近任務：")
        for task in sorted(self.tasks.values(), key=lambda t: t.updated_at, reverse=True)[:5]:
            lines.append(f"  [{task.status.value}] {task.task_id} - {task.description or task.prompt[:50]}")
        
        return "\n".join(lines)

if __name__ == "__main__":
    import sys
    
    registry = TaskRegistry()
    
    if len(sys.argv) < 2:
        print(registry.report())
    elif sys.argv[1] == "create" and len(sys.argv) >= 4:
        task_id = sys.argv[2]
        prompt = sys.argv[3]
        desc = sys.argv[4] if len(sys.argv) > 4 else ""
        task = registry.create(task_id, prompt, desc)
        print(f"✅ Created task: {task_id}")
    elif sys.argv[1] == "status" and len(sys.argv) >= 3:
        task_id = sys.argv[2]
        task = registry.get(task_id)
        if task:
            print(f"Task: {task.task_id}")
            print(f"Status: {task.status.value}")
            print(f"Created: {task.created_at}")
            print(f"Updated: {task.updated_at}")
        else:
            print(f"❌ Task not found: {task_id}")
    elif sys.argv[1] == "running":
        registry.update_status(sys.argv[2], TaskStatus.RUNNING)
        print(f"▶️  Task {sys.argv[2]} is now RUNNING")
    elif sys.argv[1] == "complete":
        registry.update_status(sys.argv[2], TaskStatus.COMPLETED)
        print(f"✅ Task {sys.argv[2]} is now COMPLETED")
    elif sys.argv[1] == "fail":
        registry.update_status(sys.argv[2], TaskStatus.FAILED)
        print(f"❌ Task {sys.argv[2]} is now FAILED")
    elif sys.argv[1] == "list":
        for task in registry.list_tasks():
            print(f"  [{task.status.value}] {task.task_id}")
    else:
        print("Usage:")
        print("  python3 task_registry.py              # Show report")
        print("  python3 task_registry.py create <id> <prompt> [desc]  # Create task")
        print("  python3 task_registry.py status <id>  # Show task status")
        print("  python3 task_registry.py running <id> # Mark as running")
        print("  python3 task_registry.py complete <id> # Mark as completed")
        print("  python3 task_registry.py fail <id>    # Mark as failed")
        print("  python3 task_registry.py list         # List all tasks")
