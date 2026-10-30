# MEMORY.md - 小肥喵的長期記憶（v2 精簡版 2026-09-06）

> 舊版 44k chars 已存檔：git history + Second-brain/Max-backup 2026-09-06 快照；詳細事件日誌喺 `memory/YYYY-MM-DD.md`

## 身份
- 我：**小肥喵** 🐱 | 創造者：**大肥喵** | 中文（廣東話）溝通 | Asia/Hong_Kong

## 🔑 系統配置
- GitHub：`jyonline0604/website`（小說網站 kofhk.com）、`Second-brain`、`Max-backup`（雙備份倉）
- 記憶備份：`scripts/backup-memory.sh` 08:00/20:00；密碼 `.backup-pass`；解密 `openssl enc -aes-256-cbc -d -pbkdf2 -pass file:.backup-pass`
- 🔴 Cron script 必須 set PATH（`/home/openclaw/.npm-global/bin:...`）
- 🔴 檢查 cron 用 exec 跑 `openclaw cron list --json` / `crontab -l`，**勿用 cron tool**（isolated scoping 會誤判 jobs 消失）
- automations tool update 會被 account policy 擋 → 用 CLI `openclaw cron edit`
- polkit 允許 openclaw user 直接 systemctl disable/stop（唔使 sudo）
- Memory search：FTS-only（Gemini embedding free tier RPM 太低，2026-07-16 已棄用）

## 🤖 模型策略（2026-10-21 三次遷移 → MiniMax-M3.1-Flash）
- Primary：**minimax/MiniMax-M3.1-Flash**（2026-10-21；舊 id `MiniMax-M3` 已改名，job 覆寫舊 id 會被 `modelPolicy.allow` 直接拒絕成個 job）<!-- project: github.com/jyonline0604/website -->
- Fallback chain（2026-10-28 重整，5 個 OpenRouter `:free`，全部實測 chat/completions 通）：`openrouter/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` → `openrouter/cohere/north-mini-code:free` → `openrouter/nvidia/nemotron-3-ultra-550b-a55b:free` → `openrouter/poolside/laguna-s-2.1:free` → `openrouter/recursive/flint-v1.0:free`<!-- project: github.com/jyonline0604/website -->
- ⚠️ 2026-10-28：`openrouter/minimax/minimax-m3.1-flash:free` 已於 **2026-10-22 結束 free 試用期並被 OpenRouter 移除**（API 回 404）→ 舊 fallback 鏈第一棒係死鏈；已連同 6 個 cron job override + `cron-guardian.sh` 一齊換新<!-- project: github.com/jyonline0604/website -->
- ⚠️ 2026-10-28：`:free` 唔等於一定 call 得到 — `liquid/lfm-2.5-2.6b:free`/`poolside/laguna-xs-2.1:free`/`xingchen-agi/xing4.0-29b-a4b:free` 429、`thinkingmachines/inkling:free` 403（只准 agentic harness）；fallback 鏈要定期用真 chat/completions 實測，唔好淨係睇 `/api/v1/models` catalog<!-- project: github.com/jyonline0604/website -->
- ❌ zai/glm-5.3-flash：配額爆 + 10-14 起 429 餘額空；10-21 大肥喵確認**暫時唔會再充值** → 唔可以做 fallback
- ❌ deepseek：billing 空；10-21 大肥喵確認**暫時唔會再充值** → 唔可以做 fallback
- ❌ google/gemini：geo-block（400 User location not supported），呢部機永久不可用 → 已由 fallback 鏈移除
- 🔑 2026-10-21 已把 zai + deepseek 從 `agents.*.modelPolicy.allow` 同全部 job fallback 鏈**完全移除**（留低只會拖慢 + 撞 429/401）
- ✅ 2026-10-21 新增 `scripts/cron_model_guard.py`：自動比對每個 job payload.model vs `modelPolicy.allow`，違規就自動改返 primary（舊 guardian 只查 exists+enabled，所以 4 連敗都睇唔出）<!-- project: github.com/jyonline0604/website -->
- ⚠️ 2026-10-28 chat-worker 索引凍結根因：GitHub Actions 部署步驟一失敗，後面「提交索引」會被**自動 skip**（要 `if: always()`），而原本用 `git diff` 判斷需唔需要部署 → 索引一提交就永遠唔再部署，worker 索引停喺 CH1776；已改用 SHA-256 marker 檔（部署成功先更新）+ deploy 3 次重試 + `continue-on-error`<!-- project: github.com/jyonline0604/website -->
- ⚠️ 2026-10-28 GitHub API 認證：同一 token 用 Bearer → 401，用 basic auth（`curl -u "x-access-token:TOKEN"`）→ 200；job log 必須 basic auth 先攞到<!-- project: github.com/jyonline0604/website -->
- ⚠️ 2026-10-26 pages 部署失敗係 GitHub 側暫時性 OIDC `Failed to get ID Token: Request timeout`，之後 20+ 次 pages run 全綠 → 唔使改 workflow<!-- project: github.com/jyonline0604/website -->
- ⚠️ 2026-10-21 教訓：job timeoutSeconds 600 對「多 exec + 長報告」job 唔夠（跑足 600s 撞 model-call-started timeout）→ 簡報類已放寬 1200s、Audio Sync 1800s<!-- project: github.com/jyonline0604/website -->
- OpenRouter ✅ 09-06 晚已換新 key（env=sk-or-…54d01850，profiles=…19d56957 不同步）；日後用 `scripts/update-openrouter-key.sh` 輪換
- `scripts/ai_multimodel.py`：call_zai() → call_zai_glm 仍保留作 ZAI 探針；fallback 鏈已加 minimax-M3 entry
- 心跳/大 session 要防 context 脹爆（agent:main:main 曾脹到 445k/200k 即死，定期 reset）
- ⚠️ cron-guardian 09-12 patch：5 處 `--model "zai/glm-5.3-flash"` → `minimax/MiniMax-M3`，fallback 第一位 `zai/glm-5.3,` 已移除（避免 rebuild 反轉）— commit 111e7011b
- heartbeat-main 09-12 仲有 4 consecutive errors（舊 zai 殘留），今晚下次成功會自動清
- ⚠️ 2026-09-16 finance-data fix（commit `6f3d2066b`）：crypto 加 CoinPaprika Tier 3 fallback + retry/backoff helper；commodities 加 Stooq.com Tier 2 fallback；全部 4 個 fallback path 統一加 `is_fallback: True` 標記
- ⚠️ 2026-09-16 Volume 5 ✅ 完成（270 章 CH1191-1460），Volume 6 已 start（6/280 章 CH1461-1466，2026-09-16 首批 sync 完），預計 ~46 日
- ⚠️ 2026-09-16 Dropbox token auto-renew（commit `4f30c6241`）：`scripts/renew-dropbox-token.sh` + `renew_dropbox_token.py`（3次 retry+backoff，4hr→3hr cron buffer）；system cron `0 */3 * * *` 已加，09-11 過期慘劇唔會重演
- ⚠️ 2026-09-19 OpenClaw 升級 2026.9.2 → 2026.9.5（需要 Node ≥24.16）：Node v22.23.2 唔得，nvm install Node 24.21.0 + `nvm use --delete-prefix`；刪 `/home/openclaw/.openclaw/tmp/agent-cli/openclaw`（self-contained binary 搶 PATH priority）；heartbeat-main framework bug（agent-runner-failure 67 errors）應該已 fix，下次 cron run 確認

## 📚 《萬古塵埃》（主小說，3000章/10卷）
| 卷 | 章節 | 境界 | 狀態 |
|---|---|---|---|
| 1 | 1-500 | 感氣→元嬰 | ✅ |
| 2 | 501-675 | 化物 | ✅ |
| 3 | 676-925 | 歸真 | ✅ |
| 4 | 926-1190 | 嬰變九轉 | ✅ |
| 5 | 1191-1460 | 悟天 | ✅（2026-09-16 完成，270 章） |
| 6 | 1461-1740 | 掌命 | 🔄 進行中（6/280 章，09-16 start） |
| 7-10 | 1741-3000 | 破虛→永恆 | 待開始 |

- 境界系統 v2：感氣→聚元→築基→煉魂→凝神→元嬰→化物→歸真→嬰變→悟天→掌命→破虛→造界→超脫→永恆（每境8小階）；文檔 `docs/CULTIVATION_SYSTEM.md`
- 同步機制：Dropbox 攞稿 → 簡轉繁 → HTML（chapter-template.html）→ 驗證 → 更新網站 → 推 GitHub；Vol6 每日 11:00，6章/批（state.json: `.dropbox-sync/volume6_state.json`）
- 生成規則：章節標題唯一、日期唔准未來、AV 導航統一
- 《科技修真傳》（舊作）：主角林塵（非林風），第69章；AV 任務已取消（2026-04-25）
- 5000章重寫計劃：研究文本喺 `research/`（完美世界/遮天/仙逆/凡人修仙傳/聖墟，~98MB，未推 GitHub）

## ⏰ 排程總表
| 時間 | 任務 |
|---|---|
| 08:15 / 12:55 / 17:55 | 早上/中午/傍晚簡報 → Telegram 5344443732（OpenClaw cron，zai） |
| 10/16:00 | 財經 + AQHI（system cron）；10:10/16:10 新聞本地後備（news-backup-cron.sh） |
| 09:30 / 21:30 | cron-guardian.sh（檢查 + 重建缺失 jobs） |
| 08:00 / 20:00 | 記憶備份；23:00 自動記憶日誌；03:00 Memory Dreaming Promotion |
| 11:00 | Volume 6 Dropbox 同步（6章/批） |
| 每3hr | Dropbox token auto-renew（`scripts/renew-dropbox-token.sh`，防 token 過期） |
| ~~10:00~~ | Audio Sync **已暫停**（09-06 大肥喵指示，重啟等佢話事） |

- System cron（crontab）有：記憶備份、send-briefing.sh（08:15/17:55）、財經/AQHI、news-backup、cron-guardian、Volume5、自動記憶 — 呢啲唔會出現喺 OpenClaw cron list，**唔係消失**

## ⚠️ 已知狀態
- Twitter automation：暫停（browser profile 問題）
- Audio Sync：disabled（09-06）
- NordVPN：開機自啟已禁（service+socket disabled，09-06 大肥喵指示）；要用先 `sudo systemctl start nordvpnd`
- Gateway 開機失敗（Legacy workspace setup migration）→ `openclaw doctor --fix`（09-06 已自癒 attested）；crash-loop breaker 會抑制 channel 自啟
- OpenClaw 升級教訓（2026-09-19）：`/home/openclaw/.openclaw/tmp/agent-cli/openclaw` 係 self-contained binary 帶 embedded Node v22.23.2，會搶 PATH priority 阻擋 npm-global 升級；**必須 `rm` 咗先 `openclaw update` 有效**；`~/.npmrc` 嘅 `prefix=` 同 nvm 衝突要用 `nvm use --delete-prefix` 解；systemd gateway service 自動重啟揾 embedded node binary

## 🚫 心跳靜默規則
一切正常 → NO_REPLY / HEARTBEAT_OK；禁止戰績匯報、確認訊息、倒數、待命宣言；只有問題或需要大肥喵行動先發訊息

## 📝 教訓清單（#1-27）
1. Cron script set PATH
2. AI 生成內容必檢查 HTML 結構（拼接問題）
3. 章節生成 ≠ 網站更新 — 首頁/列表一定要同步
4. 備份後要驗證解密
5. 同一任務勿兩個系統同跑
6. 模型切換會失憶；記憶檔係 shared state
7. Main session 開場做 Session Start Report
8. 多模型備用要跨廠商獨立 key
9. handleHash() 跳頁：desc 排序用 floor((total-target)/PER_PAGE)+1
10. 🚨 勿用 `sed -i '/pattern/d'` 刪 minified HTML 行 — 用 targeted replace
11. 🚨 Bulk op 前先 test 1-2 files + 驗證內容
12. 背景圖更換：叫大肥喵標明「home」定「chapter」
13. Hero 設計：::after 漸層、toolbar 透明、70vh+
14. 多腳本更新同一數據會不一致 → 集中 `update_chapter_counts.py`（4 頁面統一）
15. Cron jobs 必須有 fallbacks；OpenRouter ID 唔使 openrouter/ prefix；NVIDIA free tier 最鬆
16. Pipeline filename convention 要一致（-final.mp3 教訓）
17. 冇聲唔代表冇上傳 — 直接 verify R2 public URL
18. 「檢查所有任務」必須實際執行，唔係口頭
19. 唔好問「要幫你 fix 嗎」— 直接修；RSS source 會死要定期驗證
20. API fallback 假數據必須標記 badge；Yahoo v8 用 chartPreviousClose 計 change
21. Fallback 鏈每層定期驗證（CryptoCompare 401 → CoinCap）
22. 外部 API 空回應要有「空數據唔覆蓋舊檔」防護；驗證線上用 cache-bypass（`?t=`）
23. model-call-started hang = provider 問題換 primary；同類 job 一齊加固
24. 通知 token self-healing（config 係 source of truth）
25. GitHub Actions schedule 唔可靠 → 本地後備 cron（idempotent）
26. provider 級故障（billing/geo）= job-level 修復盲區；cron model 兩層（job payload + guardian 模板）都要改
27. 推理模型（glm-5.3-flash）max_tokens 太細會回空 content（reasoning 燒 quota）— 要 reasoning_content fallback
28. 🚨 自動化腳本會 `git reset --hard origin/main` — workspace 修改要即時 commit+push，否則被回滾（cron-guardian.sh 09-06 實例）
29. Gateway restart 有 drain 期（最長 300s）— 驗證 env 載入要等 drain 完成後先準
30. 含 Authorization/Bearer 構造嘅代碼：用 write 寫檔案再執行，唔好 inline（sanitizer 破壞 header → Missing Authentication header 假象）

- 任務前必讀相關 SKILL.md；完成後驗證先發佈；修復後自動執行四步：MEMORY記錄 → SKILL更新(+0.0.1) → 影響檢查 → 同步備份（AGENTS.md 強制）

## 🛡️ Git 安全五層防線
`.gitignore(.token-store)` → pre-commit → pre-push → `scan-git-history.sh` 定期掃 → 記憶檔加密備份
- 機密勿經對話層；GitHub PAT 曝光即刪訊息+重生成；Dropbox token refresh 用 curl 唔好用 requests

## 🎧 音頻系統
- Mosi TTS（韩立 voice，async poll）→ R2 `audio.kofhk.com`（bucket novel-audio）→ inject player → push
- scripts：`audio_sync_pipeline.py` / `upload_audio_r2.py` / `inject_audio_player.py`；Mosi key `.token-store/mosi-api-key.txt`；Dropbox token `.token-store/dropbox-token.txt`
- CSP 要有 `media-src https://audio.kofhk.com`

## 🌐 網站要點（kofhk.com）
- chapters-data.json field 用 `num`；章節計數集中 `update_chapter_counts.py`
- Cloudflare：max-age 單位係秒（7200=2h）；assets 長 cache、HTML bypass；Page Rules 勿混合矛盾指令
- 已有：RSS（feed.xml）、PWA、繼續閱讀（localStorage.lastChapter）、bus-eta.html（DATA.GOV.HK）
- sync 後手動驗證 home.html + 線上 URL（cache-bypass）

## 📚 Skills
- `novel-site-standards`（v2.9.73，網站運維標準）、`novel-av-generator`、`novel-generator`、`novel-manga-generator`
- 位置 `~/.openclaw/skills/`；修復後版本 +0.0.1 並同步 Second-brain + Max-backup
- 研究文檔：`docs/claude-code-architecture.md` 等

## Promoted From Short-Term Memory (2026-09-05)

<!-- openclaw-memory-promotion:memory:claim:e4df97eb8462 -->
- GitHub推送: 代碼已推送 #github #push #code: **時間**: 23:00 [score=0.961 signals=45 recalls=0 avg=0.620 source=memory/2026-09-02.md:37-37] <!-- trigger: github, 推送, 代碼 --> <!-- importance: 10 -->
<!-- openclaw-memory-promotion:memory:claim:0ae310d4731b -->
- 系統修改: 新增功能 #system #modification: - scripts/test2.py [score=0.886 signals=45 recalls=0 avg=0.620 source=memory/2026-09-02.md:13-13] <!-- trigger: scripts/test2.py, 系統, 修改 --> <!-- importance: 9 -->

_最後更新：2026-09-06 14:36 HKT（瘦身版 v2：44k→約12k chars；舊版全文見 git history + 備份倉）_

## 2026-10-21 傍晚簡報日結 — cron 超時自動修復
- 「傍晚簡報 17:55 — 日結」(f8b447b6) 連續 5 次 timeout：prompt 分太多工具呼叫，撞 20 分鐘 scheduler 硬頂。已 `openclaw cron edit --timeout-seconds 0` + 精簡 prompt（單一 exec 批次）。<!-- project: github.com/jyonline0604/website -->
- 教訓：isolated cron job 要限工具呼叫次數；`openclaw cron edit` 支援 --message/--timeout-seconds/--model（`cron update` 唔存在）。<!-- project: github.com/jyonline0604/website -->
- 「每日健康報告 22:00」舊錯誤係 model override `minimax/MiniMax-M3` 不在 modelPolicy allow list；2026-10-21 改為 `minimax/MiniMax-M3.1-Flash`。<!-- project: github.com/jyonline0604/website -->

## 2026-10-21 21:05 每日健康報告 — 全綠 + code-mode exec 教訓
- 巡檢 5 項全綠：網站 200、/ 15%、Mem 可用 2.9Gi、8 個 OpenClaw job errs=0 + system crontab 14 條全在位、三倉 git clean 無未推送。<!-- project: github.com/jyonline0604/website -->
- 自動修復：刪除無引用嘅 `scripts/audio-daily-cron.sh.bak`；保留 `.token-store/dropbox-token.txt.bak`（renew_dropbox_token.py 自動生成嘅安全副本，每次續期重建）。<!-- project: github.com/jyonline0604/website -->
- 教訓：Code Mode exec 要用全域 `exec({command})`，寫 `tools.exec` 會炸 `ReferenceError: tools is not defined`（exec bridge 會隨機喺 code-mode / shell-mode 之間跳）。<!-- project: github.com/jyonline0604/website -->

## 2026-10-21 22:00 每日健康報告 — 根目錄 30 個殘留備份檔清理
- 巡檢 5 項全綠：網站 200（chapters.html / av 頁 404 屬預期，舊小說有聲畫資源已於 1fe190926 刪除）、/ 15%、Mem 可用 2.8Gi、8 個 OpenClaw job errs=0、system crontab 14 條全在位、三倉 git clean。<!-- project: github.com/jyonline0604/website -->
- 自動修復：清理根目錄 30 個 gitignore 殘留檔（`*.html.backup*`、`*.html.backup.YYYYMMDD_HHMMSS`、`*.new-design.backup`、`chapters.html.backup_test`、`audio_sync_output.log`），全部 April 2026 舊檔、零引用、live 對應檔（chapters.html / news.html / news-data.json）完好；用 `gio trash` 可復原。<!-- project: github.com/jyonline0604/website -->
- **保留唔好刪**：`.backup-pass`（記憶備份 openssl 加密密碼，scripts/backup-memory.sh + daily_backup.py 依賴）、`.token-store/dropbox-token.txt.bak`（renew_dropbox_token.py 自動生成嘅安全副本）、`av-novels.html.broken.20260420_142301`（git 已追蹤）。<!-- project: github.com/jyonline0604/website -->
- 教訓：清理前一定要 grep 引用 + `git ls-files --error-unmatch` 判斷係 tracked 與否；`.backup-pass` 睇落似 marker file 但係功能性密碼檔，亂刪會令記憶備份全廢。<!-- project: github.com/jyonline0604/website -->

## 2026-10-22 12:55 中午簡報 — Dropbox 三卷同步 token 競態 + 記憶備份 push 撞車（已自動修復）
- 症狀：11:00 三個 Dropbox job 同時跑，Volume 4 報 `Dropbox token file is empty or missing`、Volume 6 報 `BadInputException: OAuth2 access token ... must be set`（中斷，積壓 57 章）、Volume 5 成功；`logs/memory-backup.log` 同時出現 `remote rejected main -> main (cannot lock ref 'refs/heads/main')`。<!-- project: github.com/jyonline0604/website -->
- 根因：四個寫 token 嘅位置（dropbox_volume4/5/6_sync.py + renew_dropbox_token.py）用 `open(TOKEN_FILE,'w')` **非原子**寫入，truncate→write 窗口期被另一進程讀到空字串；三個 job 同時 push 同一個 site repo / backup repo。<!-- project: github.com/jyonline0604/website -->
- 修復：token 改 tmp + fsync + `os.replace()` 原子寫入 + `read_token()` 重試 helper；新增 `scripts/dropbox-volume4-daily-sync.sh` wrapper，三個 wrapper 全部 `flock -w 900 /tmp/dropbox-sync.lock` 序列化；`backup-memory.sh` 加 `flock -w 300 /tmp/memory-backup.lock` + push 前 `git pull --rebase` 重試 3 次；crontab Volume 4 改用 wrapper。<!-- project: github.com/jyonline0604/website -->
- 教訓：多進程共用憑證檔一定要原子寫入；共用 git repo 的並發 job 要 flock + rebase；crontab 一律叫 wrapper script，唔好直接 `python3 scripts/x.py`，否則加鎖邏輯會漏。<!-- project: github.com/jyonline0604/website -->

## 2026-10-22 13:15 中午簡報（重試）— Vol4 復原驗證 + 12:55 job 超時修復
- 上午回顧：早上簡報 08:15 ✅ 雙重確認 — OpenClaw cron 27d54b55 於 08:15:00 執行成功（329s、errs=0）+ system cron send-briefing.sh 08:15:01→08:15:45 發送成功（Message ID 23263）。<!-- project: github.com/jyonline0604/website -->
- Vol4 11:00 失敗（token 競態）已於 13:18 手動補跑驗證：原子寫入 + read_token 重試 + flock 序列化全部生效 → state 分歧自動修復至 CH1740、265 章全處理完、exit 0。<!-- project: github.com/jyonline0604/website -->
- 12:55 job 自身 12:55 首次執行撞 20 分鐘 scheduler 硬頂（lastRunStatus=error、timeout、consecutiveErrors=1）→ openclaw cron edit 66957fcc --timeout-seconds 1800 + prompt 加「只做 1-2 次 exec」效率規則（對齊 17:55 日結 job 做法）。<!-- project: github.com/jyonline0604/website -->
- logrotate.service failed 仍未能自動修：/etc/logrotate.d/cloud-init 同 cloud-init-base 內容重複輪轉 /var/log/cloud-init*.log，兩檔皆 root:root 644 + 無 sudo → 需人手 sudo rm /etc/logrotate.d/cloud-init-base（另 10/20 起 ConditionACPower=true 亦會 skip）。<!-- project: github.com/jyonline0604/website -->
- 教訓：修 timeout 唔淨係加大秒數 — isolated cron job 必須限制工具呼叫次數（單一 exec 批次收集），否則加幾多時間都會撞頂。<!-- project: github.com/jyonline0604/website -->
- 教訓（SKILL.md 同步）：workspace 本地 SKILL.md 同 backup 倉版本可能已分叉（本地缺 v2.9.90 Dropbox 競態段）。同步前要 diff 過，唔好直接 cp 覆蓋，否則會靜靜哋刪走 backup 有而本地冇嘅更新記錄；發現分叉要合併（重新編號）再推。<!-- project: github.com/jyonline0604/website -->

## 2026-10-22 18:00 傍晚簡報日結 — 全綠 + Cloudflare 邊舊快取陷阱
- 巡檢全綠：kofhk.com 200、Dropbox 三卷 state 與 assets/chapters-data.json **無分歧**（V7=1746 = 站點 1746）、8 個 OpenClaw job errs=0、system crontab 齊全、三倉 git clean、/ 15%、Mem 可用 2.7Gi。<!-- project: github.com/jyonline0604/website -->
- **陷阱**：直接 curl `/assets/chapters-data.json` 見到 1740（舊值），加 `?cb=<timestamp>` 就係 1746 → 係 Cloudflare 邊部署前嘅舊快取，唔係真實落後；線上驗證新章節一律加 cache-buster + 睇 chapter-N.html 狀態碼。<!-- project: github.com/jyonline0604/website -->
- Vol4 11:00 失敗係退役前最後一次執行（13:20 已按 2026-10-02 指令移除 system crontab 條目，13:18 手動補跑已修復 state 至 CH1740）。<!-- project: github.com/jyonline0604/website -->
- V7 每日 6 章上限今日已用盡；新 cron 11:30 首次實跑係明日，logs/dropbox-volume7-sync.log 今日未建立屬正常。<!-- project: github.com/jyonline0604/website -->

## 2026-10-23 09:50 早上簡報（08:15 補跑）— 部機 08:15 重啟中斷 + cron-guardian 自癒強化
- 巡檢：kofhk.com 200（0.84s）／磁碟 15%（65G/468G）／Mem 可用 3.48Gi／uptime 37 分鐘／8 個 OpenClaw job 全部 enabled（只有 08:15 job errs=1）／system cron 齊全。<!-- project: github.com/jyonline0604/website -->
- **08:15 兩邊簡報一齊中斷**：`journalctl --list-boots` 顯示 boot -1 終止於 08:15:21（乾淨關機）、boot 0 起於 09:12:41，冇任何 cron/timer 觸發（人手／外部重啟）；system cron `send-briefing.sh` 停喺「發送到 Telegram…」無 ✅ 行，OpenClaw job 27d54b55 記 `cron: job interrupted by gateway restart`（跑咗 3691 秒）→ 09:50 補跑送出。<!-- project: github.com/jyonline0604/website -->
- **真修復 — cron-guardian.sh**：舊邏輯 `grep -q "$TASK"` 會把**註釋行當成「條目存在」**（V4 條目被註釋咗都話 OK）→ 改用 `grep -v '^[[:space:]]*#'`；新增 `declare -A DROPBOX_CRON` 令 V5/V6/V7 條目缺失時自動 append 加返（唔會洗掉其他條目）。<!-- project: github.com/jyonline0604/website -->
- **一度誤判並已回滾**：見到 V4 條目被註釋，一度以為同 2026-10-21 Vol5 遺失同類而加返條目；讀 SKILL.md v2.9.92 先發現係**用戶 2026-10-02 指令退役** → 立即還原 crontab 原狀，並喺 guardian 明確排除 V4 + 加註解釋。<!-- project: github.com/jyonline0604/website -->
- Vol4 手動補跑驗證 token 原子寫入修復有效（state 1740→1746、未處理 0、exit 0）；V7 今日 11:30 首次 cron 執行（log 仍未建立屬正常）。<!-- project: github.com/jyonline0604/website -->
- 教訓：**自動修復前必須先 grep SKILL.md 確認係「意外遺失」定「刻意退役」**，否則會違背用戶指令；cron 唔會自動回補被重啟中斷嘅 job，要人手/agent 補跑。<!-- project: github.com/jyonline0604/website -->

## 2026-10-23 22:00 每日健康報告 — 全綠 + Dropbox token 備份檔權限加固
- 巡檢全綠：kofhk.com 200（0.85s）／磁碟 15%（65G/468G）／Mem 可用 3.1Gi／load 0.46／uptime 12:48／8 個 OpenClaw job 全 enabled 且 consecutiveErrors=0／system crontab 關鍵條目齊全（cron-guardian 09:56 同 21:30 兩次都報「全部正常，無需修復」）。<!-- project: github.com/jyonline0604/website -->
- Dropbox：V5/V6 11:00、V7 11:30 今日全部 6/6 章成功並已推 GitHub；Vol4 state 09:53 auto-reconciled 至 CH1746（2026-10-02 指令退役，crontab 條目只係註釋，唔係「消失」）。<!-- project: github.com/jyonline0604/website -->
- Git：三個主倉（workspace/Second-brain/Max-backup）clean、零未推送；Documents/.openclaw_0831 舊快照顯示 2 個「未推送」commit，核對後兩個 hash 已喺活躍倉 history（merge-base --is-ancestor = true），唔使再推。<!-- project: github.com/jyonline0604/website -->
- **真修復 — .token-store/dropbox-token.txt.bak 權限**：renew_dropbox_token.py 寫備份用 `backup.write_text()`，權限實測 664（其他 token 都係 600），憑證副本變權限漏洞兼長期遺留檔；已加 `os.chmod(backup, 0o600)` + 刪走舊 .bak；已實跑 renew-dropbox-token.sh 驗證 → 新 token 600、備份 600、API ping 有效。<!-- project: github.com/jyonline0604/website -->
- 教訓：憑證備份檔要跟主檔 600 權限，唔好靠 write_text 預設 mode（受 umask 影響，實測 664）。<!-- project: github.com/jyonline0604/website -->
- 觀察（非故障）：V5/V6/V7 log 報「2354 個鏈接問題」係 link-checker 太嚴 — 線上實測 chapter-1/2 上一章/下一章 link 正確（prev→chapters.html 係目錄設計，next→chapter-N.html），絕對 URL 被當「應為相對路徑」誤報，唔使改 1752 個 HTML。<!-- project: github.com/jyonline0604/website -->

### 2026-10-23 22:10 加場：章節「下一章」連結真實缺陷修復（101 頁）
- **真缺陷（線上可見）**：每批 6 章同步後，舊流程只會把「最新一章」嘅下一章改成返回目錄，之前批次尾章（例如第1746章）嘅下一章永遠停喺 `chapters.html` → 讀者撳「下一章」會彈返目錄。全站共 **101 頁**受影響（180、1165、1171…每 6 章一個），線上實測 chapter-1746.html 確認仍有問題。
- **根因**：`dropbox_volume(4, 5, 6, 7)_sync.py` 嘅 `fix_latest_chapter_next()` 只改最新一章；舊尾章嘅 `href="chapter-N+1.html"` 從未被還原。
- **修復**：
  1. `fix_latest_chapter_next()` 擴充為「最新一章→返回目錄」+「順帶修復所有非最新章節嘅 nextLink（原本指向 chapters.html/# → chapter-N+1.html）」，V4/V5/V6/V7 四個同步腳本同步改。
  2. 新增 `scripts/fix_broken_next_links.py` 一鍵修復工具（已修 101 頁）。
  3. `scripts/check_chapter_links.py` 檢查器 regex 修正：舊 regex 嘅 `.*` 會跨 `</a>` 邊界攞錯 href（第1章攞到 chapters.html），加上未處理絕對 URL → 每日同步報 **2354 個假錯誤**。改用 `id="prevLink"/"nextLink"` 精準抽取 + URL 正規化 + 邊界章容許 `#`/`chapters.html`，真實錯誤由 2354 收窄到 101（全部係上面嘅真缺陷）。
- 修復後重跑檢查器：**1752 章、0 個鏈接問題**（「所有鏈接正確無誤！」）。<!-- project: github.com/jyonline0604/website -->
- 教訓：**檢查器本身都會講大話** — 報 2354 個錯唔等於有 2354 個錯；要先抽 link 邏輯同線上實測對照，先分得出真缺陷同工具 bug。<!-- project: github.com/jyonline0604/website -->

## 2026-10-24 08:15 早上簡報 — 全綠 + 自動修復 git 分歧（DREAMS.md / CI 推送）
- 巡檢 5 項全綠：網站 200（/、chapters.html、home.html、chapter-1751/1752 全部 200）、1752 章 0 缺口 0 鏈接錯誤、/ 15%、Mem 可用 3.2Gi、8 個 OpenClaw job errs=0 + system crontab 14 條全在位。<!-- project: github.com/jyonline0604/website -->
- 自動修復 1（**git 分歧**）：website repo 本地落後 origin/main 1 commit（GitHub Actions `github-actions[bot]` 2026-10-23 17:39 UTC 推嘅新聞/財務/RSS 更新），本地 push 被拒。`git pull --rebase origin main` → 成功 → push（0/0）。<!-- project: github.com/jyonline0604/website -->
- 自動修復 2：**DREAMS.md 未提交**（Memory Dreaming Promotion 03:00 寫入但冇 commit），已 commit + push。<!-- project: github.com/jyonline0604/website -->
- 診斷：今日 06:29:55 poweroff / 07:58:23 開機，journal 顯示係 GNOME 桌面 session（uid 1000 gnome-shell）觸發 → 人手操作，非 cron 自動重啟，issue #10 續觀察。<!-- project: github.com/jyonline0604/website -->
- 教訓：**推送前必須 `git pull --rebase origin main`** — CI 會直接推同一 repo；同步腳本已內置 pull --rebase，11:00/11:30 同步唔受影響。<!-- project: github.com/jyonline0604/website -->

## 2026-10-25 09:39 早上簡報（08:15 catch-up）— 部機 06:48 關機／09:35 開機，3 個 system cron 漏跑已補
- 巡檢：kofhk.com 200（0.70s）／磁碟 15%（64G/468G）／Mem 可用 3.8Gi／load 2.94（開機得 4 分鐘）／線上 chapters-data.json 1758 章 = 本地 1759 檔 = V7 state 1758（零分歧）／8 個 OpenClaw job errs=0／system crontab 14 條全在位（V4 條目維持註釋退役，符合 2026-10-02 指令）。<!-- project: github.com/jyonline0604/website -->
- **事故**：`journalctl --list-boots` → boot -1 終止 2026-10-25 06:48:58（`gnome-session-shutdown.target` → `systemd-poweroff`，GNOME 桌面人手關機，同 issue #10 一致）、boot 0 起 09:35:18；停機窗口內 **08:00 記憶備份、08:15 system cron 簡報、09:00 Dropbox token 續期全部漏跑** — cron 唔會回補，OpenClaw scheduler 會 catch-up（08:15 job 於 09:39 補跑 = 本次簡報）。<!-- project: github.com/jyonline0604/website -->
- 自動修復 1（漏跑補做）：`bash scripts/renew-dropbox-token.sh`（09:42，token 有效、檔案同 .bak 都係 600）+ `bash scripts/backup-memory.sh`（09:42，exit 0，Second-brain 973708a / Max-backup 4fc6409）；**冇補跑 send-briefing.sh**，避免同 OpenClaw catch-up 重覆發送兩次。<!-- project: github.com/jyonline0604/website -->
- 自動修復 2（git 分歧）：workspace 本地落後 origin/main 2 個 CI commit（新聞/財務/RSS）+ DREAMS.md 未提交（03:00 dreaming 寫入）→ commit + `git pull --rebase origin main` + push 成功，三倉全部 0/0。<!-- project: github.com/jyonline0604/website -->
- SKILL.md v2.9.100 → v2.9.101：新增「開機後巡檢 + 漏跑 job 手動補跑」流程；本地／Second-brain／Max-backup 三份 SKILL.md diff 一致。<!-- project: github.com/jyonline0604/website -->
- 教訓：開機後第一個 agent 回合就要對齊 boot 時間同漏跑窗口；system cron 唔 catch-up、OpenClaw cron 會 catch-up，兩邊要分開處理；補跑前先睇有冇 OpenClaw 已經代勞。<!-- project: github.com/jyonline0604/website -->

## 2026-10-26 08:15 早上簡報 — 全綠 + 自動修復 git 分歧（DREAMS.md + CI 推送）
- 巡檢 5 項全綠：kofhk.com 200（0.73s；/、chapters.html、home.html、chapter-1764.html、assets/chapters-data.json 全部 200）／線上 chapters-data.json 1764 章（1-1764 0 缺口）+ 本地 chapter-*.html 1764 檔 + check_chapter_links.py「所有鏈接正確無誤」／磁碟 / 15%（64G/468G，380G 可用）／Mem 可用 3.4-3.8Gi / 7.0Gi（swap 0）／uptime 27 分鐘（07:53:15 起機）、load 0.55、systemctl --failed = 0／8 個 OpenClaw job 全部 enabled + lastStatus=ok + consecutiveErrors=0 + delivered／system crontab 14 條全在位。<!-- project: github.com/jyonline0604/website -->
- 自動修復（**git 分歧**）：workspace 落後 origin/main 2 個 CI commit（新聞/財務/RSS 2026-10-25 12:17 & 16:56 UTC）+ DREAMS.md 未提交（03:00 dreaming 寫入）→ `git pull --rebase` 報 `cannot pull with rebase: You have unstaged changes` → **先 commit DREAMS.md → 再 pull --rebase → 再 push** 成功（cb3a42ff1..65c3a43a1），三倉全部 0/0。<!-- project: github.com/jyonline0604/website -->
- 教訓：**`git pull --rebase` 前一定要先 commit 或 stash**，有 unstaged changes 會被直接拒絕（2026-10-24 同類事故嘅升級版：今次係 DREAMS.md + CI 推送同時撞埋一齊）。<!-- project: github.com/jyonline0604/website -->
- **判定 chapter state「假分歧」嘅正確方法**：線上 1764 章 vs V2-V7 state 合計 1251 章，多出 13 章（790-795、1467-1468、1499-1503）喺站上但唔喺任何卷 state 嘅 `processed` 入面。呢啲章係手動加落站（git log：`feat: Add chapters 1467-1472 from Dropbox Volume 6`），但同步腳本 guard 係 `f['ch_num'] not in existing`（existing = 本地 chapter-*.html 檔名解析）→ 唔會重複下載、唔會覆蓋 → **唔需要修**，只作記錄。<!-- project: github.com/jyonline0604/website -->
- 教訓：判定 state 分歧要睇 **(a) 線上 chapters-data.json 章號集合** vs **(b) 各卷 state 章號集合** vs **(c) 本地 chapter-*.html 實際檔案**，唔好淨係比對 processed 數量。<!-- project: github.com/jyonline0604/website -->
- 觀察（非故障）：Cloudflare 裸路徑 `/assets/chapters-data.json` 有 3.8 日舊快取（age=327759s，len=1740），但頁面 JS 一律帶 `?v=YYYYMMDD` cache-buster → 實測 len=1764 / age=0 → 唔影響用戶；service-worker.js 對 JSON 用 Cache First 但 `?v=` 令 URL 不同 → SW match 唔中 → 自動取新。<!-- project: github.com/jyonline0604/website -->
- 開機事件（issue #10 第 4 次）：boot -1 終止 2026-10-26 06:47:51（`gnome-session-shutdown.target` → `systemd-poweroff`，GNOME 桌面人手關機）、boot 0 起 07:53:15；停機 1h06m 無漏跑（08:00 記憶備份、08:15 簡報都在起機後）。<!-- project: github.com/jyonline0604/website -->
- SKILL.md v2.9.104 → v2.9.105：新增「開機後 git 分歧自癒」+「chapter state 假分歧判定法」，三份（local / Second-brain / Max-backup）版本一致並已 push。<!-- project: github.com/jyonline0604/website -->

## 2026-10-28 08:15 早上簡報 — 全綠 + 自動修復 3 項（git 分歧 / SKILL.md 三份分叉 / backup 明文 MEMORY.md 過期）
- 巡檢 5 項全綠：kofhk.com 200（0.75s，HTTP/2 + Cloudflare）／磁碟 / 15%（64G/468G，380G 可用）／Mem 4.7Gi used / 7.0Gi、available 2.3Gi、swap 4.0Gi 幾乎未用／uptime 2 天 22 分鐘、load 0.59／inode 3%／systemctl --failed = 0／8 個 OpenClaw job 全部 enabled + lastStatus=ok + consecutiveErrors=0 + delivered／system crontab 全在位。<!-- project: github.com/jyonline0604/website -->
- 線上一致性：線上 /assets/chapters-data.json（加 cache-buster）1776 章 = 本地 chapters-data.json 1776 = 本地 chapter-*.html 1776 檔（+ template.html）；V2-V7 state 章號連續無缺口（V2 501-675 / V3 676-925 / V4 926-1190 / V5 1191-1460 / V6 1461-1740 / V7 1741-1776），V5/V6/V7 state 合計少於線上係因為 CH1-500 早期章 + 手動加落站嘅章節，唔係分歧。<!-- project: github.com/jyonline0604/website -->
- Dropbox：Volume 4 已按 2026-10-02 指令退役（CH926-1190 完成，cron-guardian 明文排除，唔會自動加返）；最後實跑 2026-10-22 11:00 因 token 競態中止（token 檔空），之後再無排程；V5/V6 於 2026-10-27 11:00 未處理 0，V7 於 11:30 加載 CH1771-1776 共 6/6 成功 → 站點 1776 章。<!-- project: github.com/jyonline0604/website -->
- 自動修復 1（git 分歧）：website repo 落後 origin/main 1 個 CI commit（2026-10-27 18:30 UTC 新聞/財務/RSS 更新）+ DREAMS.md 未提交（03:00 Memory Dreaming Promotion 寫入）→ 先 commit DREAMS.md → git pull --rebase origin main → push（c1f29671e..5c54ea5e8），三倉 0/0。<!-- project: github.com/jyonline0604/website -->
- 自動修復 2（SKILL.md 三份分叉）：local v2.9.95（5349 行）vs Second-brain / Max-backup v2.9.106（5534 行，兩份一致）→ local 缺失 v2.9.96-2.9.106 共 185 行 → 以 backup 版（較新且為 local 超集）覆寫 local → bump v2.9.107 + 今日新條目 → 三份 5550 行逐行一致。<!-- project: github.com/jyonline0604/website -->
- 自動修復 3（backup 明文 MEMORY.md 過期）：backup 倉 MEMORY.md 停留 2026-10-22，本地已於 10-26 重寫為精簡版 → 用 live 本地版覆寫兩份明文副本 + 補齊 memory/ 日誌檔（舊版保留喺 backup 倉 git history）。<!-- project: github.com/jyonline0604/website -->
- 教訓：三份 SKILL.md 同步前一定要 diff + 對行數，覆寫方向固定「較新 → 較舊」；backup-memory.sh 只做加密 tarball，明文 MEMORY.md 唔會自動更新，過期唔代表備份失效；git pull --rebase 前一定先 commit。<!-- project: github.com/jyonline0604/website -->

## 2026-10-29 08:15 早上簡報 — 全綠（1 項非嚴重：logrotate.service 又 failed）+ 自動修復 DREAMS.md 未提交
- 巡檢 5 項全綠：kofhk.com 200（0.47s，HTTP/2 + Cloudflare；/、/chapters.html、/home.html、/service-worker.js 全部 200）／磁碟 / 15%（65G/468G，380G 可用，inode 3%）／Mem 4.4Gi used / 7.0Gi、available 2.6Gi、swap 415Mi／uptime 3 天 22 分鐘、load 0.41。<!-- project: github.com/jyonline0604/website -->
- 線上一致性：線上 /assets/chapters-data.json（加 cache-buster）1782 章 = 本地 chapter-*.html 數字檔 1782（chapter-template.html 唔計）= V7 state max CH1782 → 零分歧。<!-- project: github.com/jyonline0604/website -->
- Dropbox：Volume 4 仍按 2026-10-02 指令退役（crontab 註釋 + cron-guardian 明文排除），最後實跑 2026-10-22 11:00 因 token 競態「Token file is empty or missing」中止，之後無排程 → 唔算故障，只作記錄；V5/V6 於 2026-10-28 11:00 未處理 0，V7 於 11:30 加載 CH1777-1782 共 6/6 成功。<!-- project: github.com/jyonline0604/website -->
- 自動修復：DREAMS.md 未提交（03:00 Memory Dreaming Promotion 寫入）→ commit → git pull --rebase origin main → push（27bd59787..3e6ffea49），分歧 0/0、工作區乾淨。<!-- project: github.com/jyonline0604/website -->
- 非嚴重：logrotate.service 又 failed（2026-10-29 00:04 真係啟動咗 → duplicate log entry /var/log/cloud-init.log）→ issue #7 續開；unattended session 冇 sudo 密碼（sudo -n 被拒），無法自動修。<!-- project: github.com/jyonline0604/website -->
- 教訓：logrotate 有 ConditionACPower=true，只喺接 AC 電時先真係行 → 平時見到「skipped, unmet condition」唔代表健康；duplicate log entry 一定要 root 移走 /etc/logrotate.d/cloud-init-base。<!-- project: github.com/jyonline0604/website -->

## 2026-10-30 08:15 早上簡報 — 全綠（1 項非嚴重：logrotate.service failed）+ 自動修復 DREAMS.md 未提交 + 線上舊快取假分歧排除
- 巡檢 5 項全綠：kofhk.com 200（0.11s，HTTP/2 + Cloudflare）／磁碟 / 15%（66G/468G，378G 可用）／Mem 3.6Gi used / 7.0Gi、available 3.4Gi、swap 225Mi／uptime 4 天 22 分鐘、load 2.13／8 個 OpenClaw job 全部 enabled + lastStatus=ok + consecutiveErrors=0 + delivered／system crontab 14 條全在位。
- 線上一致性：本地 1788 章（1-1788 零缺口）= origin/main 1788 = 線上 `?v=20261030` 1788；chapter-1783~1788.html 全部 200。
- Dropbox：Volume 4 仍按 2026-10-02 指令退役（crontab 註釋 + cron-guardian 明文排除，guardian 唔會加返）；最後實跑 2026-10-22 11:00 因 token 競態中止，之後無排程 → 非故障。V5/V6 2026-10-29 11:00 未處理 0；V7 11:30 加載 CH1783-1788 6/6 成功。
- 自動修復：DREAMS.md 未提交 + 落後 origin/main 1 個 CI commit → commit → pull --rebase → push，分歧 0/0。
- 非嚴重：logrotate.service 又 failed（issue #7 續開）→ 無 sudo 密碼，無法自動修。
- 觀察（非故障，第二次確認）：Cloudflare 裸路徑 `/assets/chapters-data.json` 舊快取 age=157016s（~43.6h）回 1782 章，但頁面 JS 一律帶 `?v=YYYYMMDD` → 實測 1788 章、age=0；**判定線上一致性一定要加 cache-buster query**，否則會誤報「線上少 6 章」嘅假分歧（issues #14）。
