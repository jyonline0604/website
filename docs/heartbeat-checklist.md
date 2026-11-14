# 心跳巡檢清單（canonical 版）

> 本檔係**版本控制嘅來源**。真正餵畀 heartbeat lane 嘅係 cron job scratch，
> 改完本檔必須跑 `bash scripts/sync_heartbeat_scratch.sh` 同步過去（script 會自動由本檔寫入
> `openclaw cron scratch 9dc7d6c3-617f-410d-9881-e87453c33037`）。
> 唔好再喺 workspace 根目錄放 `HEARTBEAT.md`——新版 OpenClaw 已改用 cron-owned scratch，
> workspace 根目錄嗰個檔只會令 `openclaw doctor` 一直報 legacy-heartbeat-file warning。

每次心跳（heartbeat-main）按以下順序做，唔好憑記憶重做舊任務：

## 步驟
1. 一次過攞齊現況：`bash scripts/ops-snapshot.sh`
   （gateway 狀態／版本、8 個 agent cron job 嘅 errs 同 fallback 鏈、網站 HTTP、workspace git 未推送同髒檔、MEMORY.md 行數、追蹤中敏感檔、Dropbox token 新鮮度、system cron 行數）
2. 章節 HTML 結構抽查（每日一次）：每個 `chapter-*.html` 只有 1 個 `<html>` 同 1 個 `<h1>`；數量合理。
3. 三倉一致性：workspace / Second-brain / Max-backup 未推送 = 0、髒檔 = 0。
   - 若髒檔只有 `DREAMS.md`（03:00 Memory Dreaming job 產出，唔會自己 commit）：先 `git add DREAMS.md && git commit`，再 `git pull --rebase origin main`，最後 `git push` —— 直接 push 會撞 CI 每日新聞 commit 造成 non-fast-forward。
4. Skill 副本唯一性：`novel-site-standards` 同 `novel-av-generator` 四處 md5 唯一數 = 1（睇 md5，唔係淨睇版本號）。

## 回覆規則
- 全部正常 → 淨係回覆單一 token `HEARTBEAT_OK`（唔好加 greeting／emoji／狀態報告／總結）。
- 有真實故障、錯誤、或需要大肥喵出手（充值、改設定、授權指令）先發訊息；之前已講過嘅唔好重複。
- 修復完：更新 `MEMORY.md`、`novel-site-standards/SKILL.md`（版本 +0.0.1 + 更新記錄）、跑 `scripts/sync_skill_copies.sh`、三倉都 push。

## 已知退役（唔好復原）
- system cron `send-briefing.sh`（08:15／17:55）：2026-11-01 大肥喵指令退役，已併入 OpenClaw agent 簡報 job。
- system cron Dropbox Volume 4 同步（CH926-1190）：2026-10-02 大肥喵指令退役，state 檔唔會再更新（唔係 bug，唔好加返）。
  - ⚠️ 2026-11-14 加咗**雙重守衛**：`.dropbox-sync/volume4_RETIRED` marker 存在時，`scripts/dropbox-volume4-daily-sync.sh` 同 `scripts/dropbox_volume4_sync.py` 都會即刻 skip（唔改 state、唔推 Git、唔 source backup-memory.sh）。因為簡報 job 有「自動修復：state 分歧就直接修復」權力，08:16 曾自行執行咗已退役嘅 V4 腳本（改寫 state + 多推一次 commit）。要復活 V4 必須先由大肥喵確認，然後刪走 marker。
- Dropbox Volume 2（CH501-675）／Volume 3（CH676-925）：已全部處理完、無排程。

## 通知大肥喵嘅唯一可靠路徑
`conversations_send` 工具而家有 outputSchema bug（多回傳 `gated` 欄 → 驗證失敗，且 journald 核實**冇實際出站**），
所以**唔可以用佢當成已通知**；要真係通知就用本回合嘅 plain assistant reply。
