# HEARTBEAT.md

```markdown
# 每天自動檢查任務
```

## 每日章節結構檢查

每天自動檢查 workspace/ 目錄下的 HTML 文件是否有拼接問題：

- 每個 `chapter-*.html` 文件應該只有 1 個 `<html>` 標籤（不含 chapter-template.html）
- 每個文件只應包含 1 個章節（每個文件只有 1 個 `<h1>` 標題）
- 檢查 `chapter-*.html` 文件數量是否合理（不含模板）

**如發現問題**：生成摘要報告，標記需要修復的文件

## OpenClaw版本檢查

每天檢查OpenClaw是否有新版本可用：

- 檢查當前安裝的OpenClaw版本
- 檢查npm上的最新版本
- 如果有新版本，記錄到日誌並通知

**檢查頻率**：每天一次（可根據需要調整）

```json
{
  "tasks": [
    {
      "name": "章節HTML結構檢查",
      "schedule": "daily",
      "time": "09:00",
      "check": "每個 chapter-*.html 只有 1 個 <html> 和 1 個 </html>，且只有 1 個<h1>章節標題",
      "action_if_fail": "生成問題報告，列出異常文件"
    },
    {
      "name": "記憶完整性檢查",
      "schedule": "daily",
      "time": "10:00",
      "check": "檢查 MEMORY.md 是否存在且大於 50 行，memory/ 目錄是否正常",
      "action_if_fail": "嘗試從 Max-backup 恢復最新備份"
    },
    {
      "name": "OpenClaw版本檢查",
      "schedule": "daily",
      "time": "11:00",
      "check": "檢查OpenClaw是否有新版本可用",
      "action_if_fail": "記錄到日誌，可選擇手動或自動更新"
    },
    {
      "name": "Skill更新檢查",
      "schedule": "daily",
      "time": "18:00",
      "check": "檢查上次任務中是否有遺留未更新的Skill更新日誌",
      "action_if_fail": "補更新並同步到Second-brain和Max-backup"
    }
  ]
}

## ⚠️ 強制規則

**每次執行以下操作後，必須立即更新 Skill（不等用戶提醒）：**
1. ✅ 修復任何系統問題
2. ✅ 發現並修正任何 bug
3. ✅ 用戶提出新規則或要求
4. ✅ 執行任何配置更改
5. ✅ 進行任何排版或結構修復

**更新後必須同步到：**
- `.openclaw/skills/novel-site-standards/`
- `.openclaw/skills/novel-av-generator/`
- Second-brain (git push)
- Max-backup (git push)
```
