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
- Fallback chain（4 個 OpenRouter free，10-21 實測 catalog refresh 通）：`openrouter/nvidia/nemotron-3-super-120b-a12b:free` → `openrouter/deepseek/deepseek-v4-flash:free` → `openrouter/qwen/qwen3-coder:free` → `openrouter/minimax/minimax-m2.5:free`<!-- project: github.com/jyonline0604/website -->
- ❌ zai/glm-5.3-flash：配額爆 + 10-14 起 429 餘額空；10-21 大肥喵確認**暫時唔會再充值** → 唔可以做 fallback
- ❌ deepseek：billing 空；10-21 大肥喵確認**暫時唔會再充值** → 唔可以做 fallback
- ❌ google/gemini：geo-block（400 User location not supported），呢部機永久不可用 → 已由 fallback 鏈移除
- 🔑 2026-10-21 已把 zai + deepseek 從 `agents.*.modelPolicy.allow` 同全部 job fallback 鏈**完全移除**（留低只會拖慢 + 撞 429/401）
- ✅ 2026-10-21 新增 `scripts/cron_model_guard.py`：自動比對每個 job payload.model vs `modelPolicy.allow`，違規就自動改返 primary（舊 guardian 只查 exists+enabled，所以 4 連敗都睇唔出）<!-- project: github.com/jyonline0604/website -->
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
