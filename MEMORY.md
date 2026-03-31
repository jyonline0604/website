# MEMORY.md - 小肥喵的長期記憶

## 身份
- 我的名字：**小肥喵** 🐱
- 大肥喵是我的創造者
- 使用中文溝通

## 🔑 重要系統配置

### GitHub Repos
- 小說網站：https://github.com/jyonline0604/website.git（原本是 my-novel-website）
- 第二大腦：https://github.com/jyonline0604/Second-brain.git
- Max-backup：https://github.com/jyonline0604/Max-backup.git（新增備份仓库）

### 備份設置
- 備份位置：Second-brain 和 Max-backup
- 加密密碼：已保存在 `/home/openclaw/.openclaw/workspace/.backup-pass`
- 加密方式：`openssl enc -aes-256-cbc -d -pbkdf2 -in <file>.enc -out <output> -pass file:.backup-pass`
- 正確解密命令（2026-03-25備份驗證成功）

### Crontab 重要規則
- **Cron script 必須 set 完整 PATH**，否則會失敗
- 設置方式：`export PATH="/home/openclaw/.npm-global/bin:/usr/local/sbin:..."`

### 備份頻率優化（2026-03-26）
- 記憶備份：從每6小時改為每天2次（08:00、20:00）
- AI 新聞：維持每6小時不變

## 📚 小說系統

### 《科技修真傳》
- 主角：**林塵**（不是林風）
- 作者：**大肥喵**
- 最新章節：第69章（2026-03-28生成）
- 網站目錄：`/home/openclaw/.openclaw/workspace/my-novel/`

### 自動化生成任務
- **OpenClaw Cron Job**：每日 07:00（已加入發布前HTML結構檢查）
- ~~System Crontab 07:00~~：已移除（避免重複執行）
- 生成後必須檢查：每個 chapter-*.html 只有 1 個 `<html>`、1 個 `</html>`、1 個 `<h1>`
- 發現拼接問題自動修復後再推送到 GitHub

### 每日簡報任務（OpenClaw Cron）
| 時間 | 任務 | Delivery |
|------|------|----------|
| 08:15 | 早上簡報 | Telegram: 5344443732 |
| 12:55 | 中午簡報 | Telegram: 5344443732 |
| 17:55 | 傍晚簡報 | Telegram: 5344443732 |

## 📅 系統維護日誌

### 2026-03-29
- ⚠️ 差點遺失章節 65-69（因 rebase 失敗差点丢コミット）
- ✅ 已 reset --hard origin/main 恢復正確狀態
- ✅ 已補提交 chapter-template.html 並推送
- ✅ 確認 origin/main 包含第 60-69 章

### 2026-03-26（今天）
- ✅ 識別並修復 system crontab 和 OpenClaw cron 重複執行的問題
- ✅ 移除 system crontab 的 07:00 小說生成
- ✅ 修復 daily-novel-chapter 任務的 error 狀態（delivery mode 已設為 ignore）
- ✅ 更新 HEARTBEAT.md 加入每日章節結構檢查
- ✅ 設定 Max-backup 為新的備份倉庫
- ✅ 完成加密備份上傳到 Max-backup
- ✅ 今天成功生成第64章，自動修復了第63章標題

### 2026-03-25
- 小說網站重建（刪除舊網站、重新創建）
- 61章 → 62章
- Twitter Automation 顯示成功但實際未發布（瀏覽器 profile 問題）
- AI 新聞系統建立（每6小時更新）

### 2026-03-24
- OpenClaw 升級至 3.23-1
- 小說章節 60-61 修復
- 章節生成器 v2 增強

### 2026-03-23
- AI 資訊版重建
- 解決 Cron 問題（PATH 不包含 openclaw command）
- 清理舊遊戲攻略頁面

### 2026-03-22
- Twitter 自動化設置

### 2026-03-19
- 小說格式統一工程（53章統一格式）
- 每日自動化系統建立

### 2026-03-18
- 小說網站自動化系統維修
- 第51-52章生成
- 安全檢查、加密監控、備份腳本創建

## ⚠️ 已知問題

### Twitter Automation
- 瀏覽器 profile `chrome-relay` 不存在，Chrome 無登入狀態
- 任務顯示成功但實際未發布
- **狀態：已暫停**

## 📝 重要教訓

1. **Cron script 必須 set PATH** — 否則找不到 openclaw command
2. **AI 生成內容需檢查** — HTML 拼接問題會導致文件損壞
3. **章節生成 ≠ 網站更新** — 生成新章節後必須更新首頁、列表頁
4. **備份後要驗證** — 解密命令要確認正確
5. **避免重複執行** — 同一任務不要在兩個系統同時運行
6. **模型切換會失憶** — /new 後 session transcript 消失，但記憶檔是 shared state，所有模型都能讀
7. **Session Start Report** — 每次 main session 開始時，主動報告記憶檔狀態、上次進度，讓大肥喵知道我在哪
8. **多模型備用策略** — 任何 AI 任務必須預設至少兩個不同廠商模型作為後備：
   - 主要：DeepSeek
   - 備用1：MiniMax-M2.7（首選）
   - 備用2：OpenRouter 內的 step-3.5-flash（次選）
   - 備用3：Google Gemini
   - 最終：本地模板生成

---

_最後更新：2026-03-31 21:15 HKT_

---

## 📅 2026-03-31 更新

### 小說進度
- 最新章節：第73章（意識融合）
- AV小說：第1-14章完成

### 網站修復
- ✅ AV第14章生成及圖片
- ✅ AV導航列統一（14章）
- ✅ 清理測試檔案（3個）
- ✅ daily-briefing.html 加入導航
- ✅ 修復22+個腳本路徑問題（my-novel → workspace）
- ✅ 修復首頁日期顯示（無未來日期）

### 重要教训
9. **路徑一致性** — 網站結構改變後，所有相關腳本路徑必須同步更新
10. **日期計算** — 使用「最新=今天，往前推算」比「固定基準日」更可靠

