# HEARTBEAT.md — 心跳巡檢清單

每次心跳（heartbeat-main）按以下順序做，唔好憑記憶重做舊任務：

## 步驟
1. 一次過攞齊現況：`bash scripts/ops-snapshot.sh`
   （gateway 狀態／版本、8 個 agent cron job 嘅 errs 同 fallback 鏈、網站 HTTP、workspace git 未推送同髒檔、MEMORY.md 行數、追蹤中敏感檔、Dropbox token 新鮮度、system cron 行數）
2. 章節 HTML 結構抽查（每日一次）：每個 `chapter-*.html` 只有 1 個 `<html>` 同 1 個 `<h1>`；數量合理。
3. 三倉一致性：workspace / Second-brain / Max-backup 未推送 = 0、髒檔 = 0。
4. Skill 副本唯一性：`novel-site-standards` 同 `novel-av-generator` 四處 md5 唯一數 = 1（睇 md5，唔係淨睇版本號）。

## 回覆規則
- 全部正常 → 淨係回覆單一 token `HEARTBEAT_OK`（唔好加 greeting／emoji／狀態報告／總結）。
- 有真實故障、錯誤、或需要大肥喵出手（充值、改設定、授權指令）先發訊息；之前已講過嘅唔好重複。
- 修復完：更新 `MEMORY.md`、`novel-site-standards/SKILL.md`（版本 +0.0.1 + 更新記錄）、跑 `scripts/sync_skill_copies.sh`、三倉都 push。

## 已知退役（唔好復原）
- system cron `send-briefing.sh`（08:15／17:55）：2026-11-01 大肥喵指令退役，已併入 OpenClaw agent 簡報 job。
- system cron Dropbox Volume 4 同步（CH926-1190）：2026-10-02 大肥喵指令退役，state 檔唔會再更新（唔係 bug，唔好加返）。
