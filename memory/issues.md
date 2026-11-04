# 已知問題追蹤

## Active Issues

### ⚠️ #10 - 2026-10-23 08:15 部機重啟，兩邊簡報一齊中斷（已補跑）
- **症狀**：system cron `send-briefing.sh`（08:15）log 停喺「發送到 Telegram…」無 ✅ 成功行；OpenClaw job 27d54b55 記 `cron: job interrupted by gateway restart`（跑咗 3691 秒，08:15→09:16）
- **根因**：journal `journalctl --list-boots` 顯示 boot -1 終止於 **2026-10-23 08:15:21**（shutdown.target 乾淨關機），boot 0 開始於 **09:12:41**；重啟唔係任何 cron / timer 觸發（已查 crontab @reboot、systemd timers、workspace scripts），似係人手／外部操作
- **影響**：08:15 早報未送達 → 09:50 由 OpenClaw cron 補跑送出（本次簡報）
- **處理**：確認 gateway 用 `systemctl --user openclaw-gateway.service`（enabled）自動喺開機起返；cron 唔會自動回補，重啟撞正排程要人手補跑
- **2026-10-24 更新**：同日再有一次 — 06:29:55 乾淨 poweroff、07:58:23 重新開機（uptime 17 分鐘）。journal 顯示 shutdown 由 **GNOME 桌面 session（uid 1000 / gnome-shell）** 觸發（gnome-session-shutdown.target → systemd-poweroff），**唔係** cron / systemd timer / unattended-upgrades → 確認係人手操作，無自動重啟機制。07:58 起機後 08:00 記憶備份、08:15 早報、11:00 同步全部正常，無補跑需要。
- **2026-10-26 更新（第四次）**：boot -1 終止於 **2026-10-26 06:47:51**（journal：`gnome-session-shutdown.target` → `systemd-poweroff`，GNOME 桌面人手關機）、boot 0 起於 **07:53:15**；停機 1h06m，**今次無漏跑**（08:00 記憶備份、08:15 system cron 簡報都喺起機後正常執行，08:15 簡報成功送出 Message ID 23301）。systemctl --failed = 0。開機後 workspace git 落後 origin/main 2 個 CI commit + DREAMS.md 未提交 → 已 commit → pull --rebase → push，三倉 0/0。<!-- project: github.com/jyonline0604/website -->
- **2026-10-25 更新（第三次）**：boot -1 終止於 **2026-10-25 06:48:58**（journal：`gnome-session-shutdown.target` → `systemd-poweroff`，GNOME 桌面人手關機）、boot 0 起於 **09:35:18**；停機 2h46m 令 **08:00 記憶備份、08:15 system cron 簡報、09:00 Dropbox token 續期** 漏跑。cron 唔會回補 → 已由 09:39 簡報回合手動補跑備份 + token 續期（**冇補跑 send-briefing.sh**，避免同 OpenClaw catch-up 重覆發送）。OpenClaw scheduler 自動 catch-up，08:15 job 於 09:39 補跑送達。`systemctl --failed` 重啟後清零（apport / logrotate 未再 fail）。

### ⚠️ #9 - apport-autoreport.service failed（低影響，2026-10-23 新發現）
- **症狀**：`systemctl --failed` 出現 `apport-autoreport.service loaded failed failed`
- **根因**：ExecStart `/usr/share/apport/whoopsie-upload-all --timeout 20` exit=2（連唔到 Ubuntu crash-report 伺服器）
- **影響**：純裝飾性 crash report 上報，唔影響網站 / cron / 同步
- **狀態**：Active（低影響，唔需要即時處理）

### ✅ #8 - Volume 4 crontab 條目「被註釋」→ 查證係按指令退役，唔係 bug（2026-10-23 早上簡報）
- **現象**：crontab 只見 `# Dropbox Volume 4 同步 - 每天11:00` 註釋行，冇 active 條目；logs/dropbox-volume4-sync.log 停喺 2026-10-22 11:00（嗰次因 token 競態失敗）
- **一度誤判**：自動修復時以為同 2026-10-21 Vol5 條目遺失同類，已加返條目 → 讀 SKILL.md v2.9.92 先發現係**用戶 2026-10-02 指令退役**（Vol4 CH926-1190 已完成）
- **已回滾**：crontab 還原原狀（V4 條目維持註釋），冇留低多餘條目
- **真正修復**：cron-guardian.sh 強化 —「被註釋 = 缺失」檢查（grep -v '^[[:space:]]*#'）+ V5/V6/V7 缺失自動加返（append，唔會洗掉其他條目）+ V4 明確排除並加註解釋
- **教訓**：自動修復前必須先讀 SKILL.md 確認條目係「意外遺失」定「刻意退役」，否則會違反用戶指令

### ✅ #5 - heartbeat-main 連續 29 次 error（system-owned monitor job，2026-10-19 起）— 已於 2026-10-21 18:00 確認恢復
- **症狀**：每 30 分鐘一次 heartbeat 失敗（agent-runner-failure），consecutiveErrors=29
- **根因**：main session 帶 session-level model override -> zai/glm-5.3-flash；journal 顯示 configured fallbacks disabled by user model override -> zai 429 billing -> 無 fallback 兜底
- **修復**：主 session override 已清空（openclaw.json main.model = None，預設 minimax/MiniMax-M3.1-Flash）
- **驗證**：2026-10-21 18:00 檢查，heartbeat-main lastRunStatus=ok、consecutiveErrors=0 ✅
- **2026-10-22 08:15 復檢**：heartbeat-main lastStatus=ok、consecutiveErrors=0、30 分鐘節奏正常 → **確認 Resolved**

### ⚠️ #3 - OpenClaw cron model override 違反 modelPolicy（2026-10-21 已修復，觀察中）
- **2026-10-21 18:00 更新**：8 個 OpenClaw job 嘅 payload.model 已全部改為 minimax/MiniMax-M3.1-Flash，preflight error 已無再出現；但 consecutiveErrors 尚未清零（簡報類 4-5、Audio Sync 6），需下一個排程週期自然歸零
- **症狀**：早上/中午/傍晚簡報 + 每日健康報告 全部 cron-preflight error（minimax/MiniMax-M3 not in modelPolicy.allow）
- **修復**：payload.model -> minimax/MiniMax-M3.1-Flash；新增 scripts/cron_model_guard.py 自動偵測+修復
- **驗證**：cron-guardian.sh 已改用新 model + 跨廠商 fallbacks；2026-10-21 15:40 retry 已成功送達
- **2026-10-22 08:15 確認**：8/8 OpenClaw job 全部 lastStatus=ok、consecutiveErrors=0、lastDelivery=delivered → **實質 healed，可降級為 Resolved**（保留觀察項）

### ✅ #7 - logrotate.service failed（duplicate log entry）— 2026-11-02 確認根因已消失，結案
- **症狀**：`systemctl --failed` 出現 `logrotate.service loaded failed failed`；journal 顯示 `error: cloud-init-base:1 duplicate log entry for /var/log/cloud-init.log`
- **根因**：`/etc/logrotate.d/cloud-init` 同 `/etc/logrotate.d/cloud-init-base` 兩個檔案內容完全一樣（都輪轉 `/var/log/cloud-init*.log`），logrotate 遇到重複 log entry 就會 skip 個檔並 exit 1
- **影響**：只有 `/var/log/cloud-init*.log` 唔會被輪轉，其他 logrotate 規則正常；系統碟用量得 15%，暫時無實質風險
- **自動修復嘗試**：`sudo -n`（無密碼）被拒、`exec elevated` 在 unattended cron session 不可用（tools.elevated.enabled 未開），所以 **無法自動修復**
- **人手修復指令**（大肥喵一次過執行）：
  ```
  sudo mv /etc/logrotate.d/cloud-init-base /etc/logrotate.d/cloud-init-base.disabled
  sudo logrotate -d /etc/logrotate.conf | grep -i error   # 應該冇 duplicate
  sudo systemctl reset-failed logrotate.service
  ```
- **狀態**：Active（低影響，待人手處理）→ **2026-10-23 更新**：已唔再出現喺 `systemctl --failed`（journal 顯示 logrotate 自 10-20 起每日 skipped，ConditionACPower=true 未满足）；重複檔案 /etc/logrotate.d/cloud-init-base 仍在，重啟恢復 AC 供電後仍會再 fail
- **2026-10-29 08:15 更新（復發）**：機器於 2026-10-29 00:04 接上 AC 電 → ConditionACPower=true 終於滿足 → logrotate 真係啟動 → 再次 `error: cloud-init-base:1 duplicate log entry for /var/log/cloud-init.log` → exit 1 → `systemctl --failed` 又見 logrotate.service failed。兩個檔案仍然一模一樣（各 144 bytes，diff 無輸出）。unattended session `sudo -n true` 被拒（需互動認證）→ **仍然無法自動修復**，等大肥喵人手執行：`sudo mv /etc/logrotate.d/cloud-init-base /etc/logrotate.d/cloud-init-base.disabled && sudo logrotate -d /etc/logrotate.conf | grep -i error && sudo systemctl reset-failed logrotate.service`
- **教訓**：logrotate 嘅 ConditionACPower=true 令佢淨係喺接 AC 電時真係行 → journal 見到「skipped, unmet condition」唔代表健康，巡檢要睇 `systemctl --failed`

- **2026-10-30 08:15 更新（續發）**：今日 08:15 `systemctl --failed` 仍然只見 logrotate.service failed（其餘 0 個 failed unit）；AC 供電仍然接住，所以 logrotate 每日真係行 → 同一個 duplicate log entry 錯誤持續。unattended session `sudo -n true` 仍被拒（interactive authentication required）→ **仍然無法自動修復**，繼續等大肥喵人手執行上面三行指令。<!-- project: github.com/jyonline0604/website -->
- **2026-11-02 08:15 更新（✅ 已修復／結案）**：根因檔 `/etc/logrotate.d/cloud-init-base` 已經唔存在（root 已移除），`systemctl --failed` = **0 failed units** → 連續多日嘅 logrotate failed 係真·已修好，唔使再人手執行任何 sudo 指令。<!-- project: github.com/jyonline0604/website -->

### ℹ️ #14 - 線上 chapters-data.json 裸路徑舊快取 → 假「state 分歧」警報（2026-10-30 早上簡報確認，非故障）
- **現象**：直接 curl 裸路徑 https://kofhk.com/assets/chapters-data.json（無 query）回 **1782** 章，但本地同 origin/main 都係 **1788** 章 → 睇落似「線上少咗 6 章」嘅 state 分歧
- **根因**：Cloudflare 邊對裸路徑嗰條 URL 有 ~43.6 小時舊快取（cf-cache-status: HIT、age: 157016、last-modified: 2026-10-28 03:30 UTC）；但頁面 JS 一律用 `assets/chapters-data.json?v=YYYYMMDD` cache-buster → 實測 `?v=20261030` 回 1788 章、age=0
- **實測**：chapter-1783.html ~ chapter-1788.html 線上全部 200；chapter-1788.html title =「第1788章 · 風雨前夕 - 萬古塵埃」
- **結論**：**唔係故障，唔需要 purge**；巡檢判定線上一致性必須加 `?v=`（或隨機 query）再 curl，否則會誤報分歧
- **教訓**：Cloudflare 裸路徑快取 ≠ 用戶見到嘅內容；index.html / home.html / chapters.html 全部帶日期 cache-buster<!-- project: github.com/jyonline0604/website -->

## Resolved Issues

### ✅ #11 - website repo 本地落後 origin/main 1 commit（2026-10-24 早上簡報發現並修復）
- **現象**：`git push` 被拒（tip behind remote）；origin/main 有 `github-actions[bot]` 嘅 2026-10-23 17:39 UTC 新聞/財務/RSS 更新 commit，本地未 pull
- **根因**：GitHub Actions 直接推同一 repo，本地 workspace 唔會自動 fetch；人手 push 前無 pull
- **修復**：`git pull --rebase origin main` → rebase 成功（DREAMS.md 無衝突，CI 冇碰過 DREAMS.md）→ push 成功，分歧歸零（0/0）
- **預防**：同步腳本 `git_commit_and_push()` 本身已內置 `git pull --rebase`（V5/V6/V7 都有），所以 11:00/11:30 同步唔受影響；人手 push 前要記得先 pull



### ✅ #6 - Dropbox Volume 5 system cron 條目遺失（2026-10-21 早上簡報發現並修復）
- **現象**：crontab 冇 Volume 5 條目，最後同步停喺 2026-10-03
- **修復**：append 方式加回 0 11 * * * dropbox-volume5-daily-sync.sh；手動補跑（state 1575->1689，未處理 0）；cron-guardian.sh 權限回復 +x
- **提交**：workspace 8d77ba10c

### ✅ #4 - zai/glm-5.3-flash 餘額不足（billing，2026-10-21 修復）
- **症狀**：每日 Audio Sync 10:00 -> All models failed (2): zai 429 余额不足
- **修復**：job payload 改用 minimax/MiniMax-M3.1-Flash；15:46 手動補跑 audio_sync_pipeline.py（無 pending 章節）



### ✅ #1 - Cron Scheduler Jobs 反覆消失（2026-07-17 發現，2026-08-09 確認已解決）
- **狀態**：Resolved
- **現象**：Gateway cron scheduler jobs 反覆消失
- **解決**：2026-08-09 08:15 檢查，全 7 個 OpenClaw cron jobs 正常運作，連續多日無消失
- **穩定運行**：自 2026-07-29 以來無再現

### ✅ #2 - Dropbox Volume4 TypeError（2026-08-08 發現，已修復）
- **現象**：`TypeError: can only concatenate list (not "set") to list` at line 612
- **根因**：`state['synced_to_site'] = sorted(set(state.get(...) + existing))` 使用 `+` 串接 list+set
- **修復**：改用 `|` (set union): `sorted(set(state.get(...)) | existing)`
- **影響**：2026-08-08 10:00 批次失敗，後續 17:57 自動修復成功（73章，CH1191-1263）

### ✅ #12 - 三份 SKILL.md 版本分叉 + backup 明文 MEMORY.md 過期（2026-10-28 早上簡報發現並修復）
- **症狀**：local SKILL.md v2.9.95（5349 行）vs Second-brain / Max-backup v2.9.106（5534 行，兩份一致）→ local 缺失 v2.9.96-2.9.106 共 185 行（cron-guardian 自癒、Volume 7 建立、開機後巡檢等條目全部唔喺 local）；backup 倉 MEMORY.md 停留 2026-10-22，本地已於 10-26 重寫為精簡版
- **根因**：SKILL.md 三份靠人手 cp 同步，冇一致性檢查 → 單向覆寫會令一份靜靜落後；`backup-memory.sh` 只做加密 tarball（MEMORY.md + memory/*.md 打包再 encrypt，08:00 / 20:00 兩次），明文副本唔會自動更新 → 明文副本靜靜過期
- **修復**：以 backup 較新版（超集）覆寫 local SKILL.md → bump v2.9.107 + 今日新條目 → 三份 md5 一致（5550 行）；用 live 本地 MEMORY.md 覆寫兩份 backup 明文副本 + 補齊 memory/ 日誌檔 → 三倉 commit + push，全部 0/0、工作區乾淨
- **教訓**：三份 SKILL.md 同步前一定要 diff + 對行數，覆寫方向固定「較新 → 較舊」（較新嗰份係超集）；明文 MEMORY.md 過期 ≠ 備份失效，加密 tarball 每日正常產生
- **附帶坑位**：website repo 嘅 `.openclaw/skills/novel-site-standards/SKILL.md` 係以前 force-add 過嘅 tracked 檔（.gitignore 第 62 行有 `.openclaw/`）→ 改完要用 `git add -f`，否則 pull --rebase 會被 unstaged changes 擋住

### ✅ #13 - website repo git 分歧（2026-10-28 早上簡報發現並修復）
- **症狀**：本地落後 origin/main 1 個 CI commit（GitHub Actions 2026-10-27 18:30 UTC 新聞/財務/RSS 更新）+ DREAMS.md 未提交（03:00 Memory Dreaming Promotion 寫入）
- **修復**：先 commit DREAMS.md → `git pull --rebase origin main` → push（c1f29671e..e1c07df1a），三倉 0/0
- **教訓**：pull --rebase 前一定先 commit **所有** 改動（包括被 .gitignore 忽略但已 tracked 嘅 SKILL.md），今日就係第一次只 commit 咗 MEMORY.md、漏咗 SKILL.md，第二次補 `git add -f` 先成功

### ✅ #14 - SKILL.md 版本分叉復發（2026-10-30 22:00 健康報告發現並修復）+ 誤判更正
- **症狀**：real local SKILL.md（v2.9.111）缺失 v2.9.107/108/109 三個區段，而 website repo 入面 force-add 嘅副本（v2.9.110）反而齊；兩份備份倉又係 local 嘅複本 → 四份內容分叉（本地行數反而較少）
- **根因**：同日兩個 session 各自 append 同一個標題「## 2026-10-30 更新」（08:15 簡報寫 git 分歧／線上一致性，cache-buster 修復寫 hourly key），互相覆寫 → 版本號升咗但內容冇合併
- **修復**：逐行 diff 確認 website-repo 副本係「C 底 + 缺失區段」→ 三方合併（C 底 + cache-buster 區段改名保留 + 新診斷法區段）→ version 2.9.112 → 4 份 md5 一致（5620 行）→ 三倉 commit + push
- **教訓**：同日多個 session append 同一份 SKILL.md 一定要用**唔同標題**（或先 diff 再合併），唔可以靠版本號判斷邊份新；「行數較多」≠「版本較新」，兩者要分開驗
- **同時更正**：10-29 / 10-30 報告聲稱「send-briefing.sh（08:15/17:55）+ check_openclaw_update.py（11:00）三條 system cron 冇執行過」係**誤判** → syslog CRON 行 + 腳本內部 LOG_FILE + 實際送達 Msg ID 三路對照證實每日都有跑（教訓 #31）

### ℹ️ #11 復發記錄 — website repo git 分歧第 4 次（2026-11-04 早上簡報發現並修復）
- **症狀**：workspace（= website repo）落後 origin/main 1 個 GitHub Actions commit（b62c22eba..ab1073884，新聞/財務/RSS 自動更新）+ DREAMS.md 未提交（03:00 Memory Dreaming Promotion 產出）
- **修復**：commit DREAMS.md → git pull --rebase origin main → git push origin main（ab1073884..124039b5e）→ 分歧 0/0、工作區乾淨
- **復發次數**：#11（10-24）、#13（10-28）、10-31、今日 = 第 4 次 → 屬高頻問題，根治方向係 03:00 dreaming 直接 commit+push，或加 05:00 拉取推送 system cron<!-- project: github.com/jyonline0604/website -->
