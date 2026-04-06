# Claude Code 源碼架構深度分析
*基於50萬行TypeScript源碼的技術研究 - 2026-04-06*

---

## 🔬 AutoDream - 真實實現

### 核心邏輯 (`src/services/autoDream/autoDream.ts`)

```typescript
/**
 * Background memory consolidation. Fires the /dream prompt as a forked
 * subagent when time-gate passes AND enough sessions have accumulated.
 *
 * Gate order (cheapest first):
 *   1. Time: hours since lastConsolidatedAt >= minHours (one stat)
 *   2. Sessions: transcript count with mtime > lastConsolidatedAt >= minSessions
 *   3. Lock: no other process mid-consolidation
 */
```

### 三層門控設計（源碼證實）

| 門控 | 檢查內容 | 代價 |
|------|----------|------|
| **Time Gate** | `Date.now() - lastConsolidatedAt >= minHours` | 1次stat |
| **Session Gate** | `sessions with mtime > lastConsolidatedAt >= minSessions` | 多次stat |
| **Lock Gate** | `.consolidate-lock` file存在？PID存活？ | 1次stat |

### 默認配置

```typescript
const DEFAULTS: AutoDreamConfig = {
  minHours: 24,      // 24小時後才能再次整合
  minSessions: 5,     // 至少5個新會話
}
```

### Consolidation Lock 實現

```
Lock文件：.consolidate-lock
- mtime = lastConsolidatedAt（用作時間戳）
- body = PID（持有者進程ID）

設計原則：
- Crash恢復：mtime不更新 → 下次自動重試
- PID重用保護：60分鐘後即使PID存活也允許接管
- 失敗回滾：mtime回退到priorMtime
```

---

## 🧠 QueryEngine 架構

### 核心初始化 (`src/QueryEngine.ts`)

```typescript
export type QueryEngineConfig = {
  cwd: string
  tools: Tools
  commands: Command[]
  mcpClients: MCPServerConnection[]
  agents: AgentDefinition[]
  canUseTool: CanUseToolFn
  getAppState: () => AppState
  setAppState: (f: (prev: AppState) => AppState) => void
  initialMessages?: Message[]
  customSystemPrompt?: string
  userSpecifiedModel?: string
  thinkingConfig?: ThinkingConfig
  maxTurns?: number
  maxBudgetUsd?: number
  taskBudget?: { total: number }
}
```

### Feature Flag 系統

```typescript
// Dead code elimination via bun:bundle
/* eslint-disable @typescript-eslint/no-require-imports */
const getCoordinatorUserContext: (...) = feature('COORDINATOR_MODE')
  ? require('./coordinator/coordinatorMode.js').getCoordinatorUserContext
  : () => ({})
/* eslint-enable @typescript-eslint/no-require-imports */
```

**支持的Feature Flags：**
```javascript
'KAIROS',                // Assistant / daily-log mode
'PROACTIVE',             // Proactive autonomous mode
'BRIDGE_MODE',           // VS Code / JetBrains IDE bridge
'VOICE_MODE',            // Voice input
'COORDINATOR_MODE',      // Multi-agent swarm coordinator
'BASH_CLASSIFIER',       // Bash command safety classifier
'BUDDY',                // Companion sprite animation
'WEB_BROWSER_TOOL',     // In-process web browser
'CHICAGO_MCP',          // Computer Use (screen control)
'AGENT_TRIGGERS',       // Scheduled cron agents
'ULTRAPLAN',           // Ultra-detailed planning mode
'EXTRACT_MEMORIES',     // Background memory extraction
```

---

## 🎭 DreamTask 狀態機

### 任務狀態定義

```typescript
export type DreamPhase = 'starting' | 'updating'

export type DreamTaskState = TaskStateBase & {
  type: 'dream'
  phase: DreamPhase
  sessionsReviewing: number
  filesTouched: string[]      // Edit/Write tool_use捕獲的路徑
  turns: DreamTurn[]          // 壓縮後的回覆
  abortController?: AbortController
  priorMtime: number         // 用於kill時回滾lock
}
```

### 狀態翻轉邏輯

```
'starting' → 'updating'
  條件：檢測到第一個 Edit/Write tool_use
  意義：用戶開始看到文件被修改

注意：filesTouched是不完整的
- 漏掉：bash中介的寫操作
- 只捕獲：直接用tool_use的寫操作
```

---

## 📁 目錄結構

```
src/
├── assistant/          # 助手功能
├── bootstrap/         # 啟動初始化
├── bridge/            # IDE橋接(VS Code/JetBrains)
├── buddy/             # 像素寵物動畫
├── cli/               # CLI處理器
├── commands/          # 斜槓命令(/dream, /clear等)
├── coordinator/       # 多Agent協調
├── memdir/            # 記憶目錄(KAIROS)
│   ├── memdir.ts
│   ├── memoryAge.ts
│   ├── memoryScan.ts
│   └── memoryTypes.ts
├── query/             # 查詢引擎
├── services/
│   ├── autoDream/    # 自動記憶整合
│   ├── compact/      # 對話壓縮
│   ├── extractMemories/ # 記憶提取
│   └── tools/        # 工具服務
├── tasks/             # 任務系統
│   ├── DreamTask/
│   ├── LocalAgentTask/
│   └── RemoteAgentTask/
├── tools/            # 工具實現
│   ├── AgentTool/
│   ├── BashTool/
│   ├── FileEditTool/
│   └── FileWriteTool/
└── utils/
    ├── forkedAgent/  # 子Agent調度
    ├── hooks/        # 後置采樣鉤子
    └── sessionStorage/ # 會話持久化
```

---

## 🔧 關鍵實現細節

### 1. Session追蹤

```typescript
// 使用mtime（修改時間）而非birthtime（創建時間）
// 原因：ext4文件系統birthtime可能為0
export async function listSessionsTouchedSince(
  sinceMs: number,
): Promise<string[]> {
  const dir = getProjectDir(getOriginalCwd())
  const candidates = await listCandidates(dir, true)
  return candidates
    .filter(c => c.mtime > sinceMs)
    .map(c => c.sessionId)
}
```

### 2. 失敗重試機制

```typescript
// 失敗時回滾mtime
await rollbackConsolidationLock(priorMtime)

// mtime回退後，下次turn會重新觸發time-gate
// Scan throttle是backoff機制
const SESSION_SCAN_INTERVAL_MS = 10 * 60 * 1000  // 10分鐘
```

### 3. Cache優化

```typescript
// 三層Cache
const result = await runForkedAgent({
  cacheSafeParams: createCacheSafeParams(context),
  cache_read_input_tokens: result.totalUsage.cache_read_input_tokens,
  cache_creation_input_tokens: result.totalUsage.cache_creation_input_tokens,
})
```

---

## 💡 對我的啟發

### 1. Triple Gate設計 → 我可以採用

```python
# 我的Nightly Dreaming可以加入：
if not time_gate_passed():     # 時間檢查
    return
if not session_gate_passed():  # 會話數檢查  
    return
if not lock_acquired():       # 鎖檢查
    return
# 才執行記憶整合
```

### 2. mtime作為時間戳 → 極簡設計

```
我的實現：
- 用文件mtime代表"最後整合時間"
- 用文件body存"狀態"

對比數據庫：
- 簡單100倍
- 無需外部依賴
- 天然持久化
```

### 3. 失敗回滾 → 重要教訓

```
每次可能失敗的操作：
1. 嘗試獲取資源
2. 記錄失敗前的狀態（priorMtime）
3. 執行操作
4. 失敗 → 回滾到之前狀態
```

### 4. Anti-Rationalization → 自我提醒

```
當我想"代碼看起來正確，差不多就行"時：
❌ 這是Rationalization
✅ 實際驗證：運行測試、檢查輸出
```

---

## 📊 統計數據

| 指標 | 數值 |
|------|------|
| 總TypeScript文件 | 2,074 |
| 總目錄 | 308 |
| 源碼大小 | 52M |
| src/services/ | 45+ 子目錄 |
| src/tools/ | 20+ 工具 |

---

## 🔗 參考資源

- 源碼鏡像：`https://github.com/codeaashu/claude-code`
- 重建項目：`https://github.com/leaked-claude-code/leaked-claude-code`
- 詳細分析：愛范儿、VentureBeat、Sabrina.dev

---

# Claw Code (ultraworkers) - Rust 開源實現
*https://github.com/ultraworkers/claw-code*

## 核心特色

### 1. 模組化 Rust 架構

```rust
crates/
├── api/              # Anthropic API 調用
├── commands/         # CLI 命令
├── compat-harness/   # 兼容性測試
├── mock-anthropic-service/  # Mock 服務
├── plugins/          # 插件系統
├── runtime/          # 核心運行時
└── tools/            # 工具實現
```

### 2. TaskRegistry 實現

```rust
pub enum TaskStatus {
    Created,
    Running,
    Completed,
    Failed,
    Stopped,
}

pub struct Task {
    pub task_id: String,
    pub prompt: String,
    pub description: Option<String>,
    pub status: TaskStatus,
    pub created_at: u64,
    pub updated_at: u64,
}
```

**特點**：
- `Arc<Mutex<HashMap>>` 線程安全
- `now_secs()` 基於 SystemTime
- TaskStatus 狀態機清晰

### 3. PermissionEnforcer 權限系統

```rust
pub enum PermissionMode {
    ReadOnly,
    WorkspaceWrite,
    Allow,
    DangerFullAccess,
}

pub enum EnforcementResult {
    Allowed,
    Denied { tool, active_mode, required_mode, reason },
}
```

**安全檢查**：
- `check_file_write`: 檢查路徑是否在 workspace_root 內
- `is_within_workspace`: 防止目錄穿越攻擊

### 4. 特性對照表

| 特性 | 狀態 |
|------|------|
| Anthropic API + streaming | ✅ |
| OAuth 登錄 | ✅ |
| 工具系統 (bash, read, write, edit) | ✅ |
| Web tools (search, fetch) | ✅ |
| 子 Agent | ✅ |
| 許可系統 | ✅ |
| MCP 服務器生命週期 | ✅ |
| Session 持久化 | ✅ |
| 成本/使用統計 | ✅ |
| Git 集成 | ✅ |
| Mock 測試框架 | ✅ |

## 對我的啟發

1. **Rust 的 Memory Safety** → 高性能工具的理想語言
2. **PermissionEnforcer 設計** → 我可以實現類似的權限分層
3. **TaskRegistry 簡潔性** → 用 HashMap + Mutex 實現輕量級任務追蹤
4. **Mock Testing** → 完整的 mock 服務用於測試

## 關聯項目

```rust
// 相關的 UltraWorkers 生態
clawhip           // Event router
oh-my-openagent   // Multi-agent coordination  
oh-my-codex       // Workflow system
```
