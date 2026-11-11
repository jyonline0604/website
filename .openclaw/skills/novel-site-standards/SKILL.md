---
name: novel-site-standards
description: 小說網站維護、章節更新、HTML修復、推送GitHub前必讀。規範章節標題唯一、日期合理、導航統一、結構驗證等標準流程。
version: 2.9.163
---

>
> 📚 **歷史記錄已分檔**：2026-04～05 嘅逐章批次日誌（CH 列表、境界檢查表）已搬到同目錄 `SKILL_HISTORY.md`（內容一字無刪）。
> 呢個主檔只保留**操作規則 + 修復經驗 + 近期記錄**。查舊章節批次記錄 → `SKILL_HISTORY.md`。
> ⚠️ 檔案有 **256000 bytes 硬上限**（超過 loader 會 skip 個 skill）——加更新記錄前先 `stat -c%s` 睇大小，超就要再分檔。


---

## [2026-10-21] 更新 (v2.9.84) - Volume 5 system cron 條目遺失 + cron-guardian 權限修復

### 問題描述
1. **Dropbox Volume 5 每日同步停咗 18 日**：crontab 只剩 Volume 4 / Volume 6，冇 Volume 5 條目；logs/dropbox-volume5-sync.log 最後執行係 2026-10-03 10:23
2. **scripts/cron-guardian.sh 權限跌咗**：git diff 顯示 old mode 100755 -> new mode 100644，cron-guardian 靠直接執行會 fail
3. **scripts/cron_model_guard.py 未入 git**（新寫嘅 model-policy guard 冇 commit）

### 根因
1. Volume 5 條目喺早前清理 system cron 時被刪走；cron-guardian 只重建 **OpenClaw cron jobs**，永遠唔會重建 system cron 條目
2. 用 edit/write 覆寫 shell script 嘅時候冇保留 executable bit

### 修復
1. crontab 加回（append 方式：讀現有 -> 檢查重複 -> 加一行 -> crontab -，唔覆蓋其他條目）：
   0 11 * * * cd /home/openclaw/.openclaw/workspace && bash scripts/dropbox-volume5-daily-sync.sh >> /home/openclaw/.openclaw/workspace/logs/dropbox-volume5-sync.log 2>&1
2. 手動補跑 Volume 5 sync -> state 分歧自動修復 1575 -> 1689，未處理章節 0（第五卷冇新章，冇 backlog）
3. chmod +x scripts/cron-guardian.sh scripts/cron_model_guard.py
4. workspace commit + push（8d77ba10c，push 前先 git pull --rebase 解決 non-fast-forward）

### 教訓
- **system cron 同 OpenClaw cron 係兩套機制**：guardian 只保 OpenClaw cron jobs；system cron 條目要自己用 crontab -l 核對
- 改完 shell script 一定要睇 git diff 嘅 mode 行（755->644 = 權限跌咗）
- 修 crontab 永遠用 append，唔好覆蓋式寫入

## [2026-07-28] 更新 (v2.9.72) - Audio Sync DAILY_LIMIT=1 + Volume 5 bug fix

### 問題描述
1. **Audio Sync 一次過處理 10 章**：大肥喵指定每日只更新 1 章
2. **Volume 5 cron crash**：`dropbox_volume5_sync.py` 中 `sorted(set(list + set))` 出錯
   - `state['synced_to_site'] = sorted(set(state.get('synced_to_site', []) + existing))`
   - `existing` 係 `set`，不能直接用 `+` 串接 `list`
3. **Volume 2 & Volume 4 已完成但 cron 未停用**：
   - Volume 2 cron 仍每日 10:00 執行
   - Volume 4 cron 每日 11:00 與 Volume 5 同一時間，可能 git conflict

### 修復
1. **`audio_sync_pipeline.py`**：新增 `DAILY_LIMIT = 1` config，每日只處理 1 章
2. **`dropbox_volume5_sync.py`**：`sorted(set(... + list(existing)))` ✅
3. **System crontab**：Volume 2 & Volume 4 cron 已 disable
4. **Volume 5 cron**：保持 `CHAPTERS_PER_BATCH = 6` 不變
5. **Git 修復**：`git pull --rebase && git push` 成功推送 CH1191-CH1197

### 今日成功同步
- 🎧 Audio Sync：CH31-CH40（因為改 config 前已 run）
- 📖 Volume 5：CH1191-CH1197（7章）

### 預防措施
- 更改 batch size 前必須確認係 Audio 定 Text sync
- 已完成 Volume 嘅 cron 要 disable 避免 git conflict

---

## [2026-07-04] 更新 (v2.9.57) - Git Pre-Commit 安全機制 + Git History 掃描器

### 問題描述
- Dropbox credentials 曾被意外 commit 到 GitHub 公開 repo
- 舊 credentials 仍存在 git history 中，任何人都可 git log 查看
- 沒有人手去確保每次 commit 前檢查敏感資料

### 修復
1. **Pre-commit hook** (`.git/hooks/pre-commit`)：每次 commit 自動掃描，block 敏感檔案
   - 檢查 `.token-store/`, `.backup-pass`, `openclaw.json` 等敏感路徑
   - 檢查 API Key 模式 (`sk-`, `ghp_`, Dropbox tokens 等)
   - 檢查 Private Key / PEM 檔案
   - 檢查 Secrets / Passwords 檔案
2. **Git History 掃描器** (`scripts/scan-git-history.sh`)：掃描整條 git history
   - 支援 verbose 模式
   - 可每日 cron 檢查
3. **更新 HEARTBEAT.md**：加入每日自動 git history 掃描

### 經驗
- 人類記憶唔可靠，commit 前必須有自動化檢查
- Git pre-commit hook 係最前端嘅防線
- `.gitignore` + pre-commit hook 雙重保護先穩陣

## [2026-07-03] 更新 (v2.9.56) - 減少 Push 頻率（防止 GitHub Pages build 失敗）

### 問題描述
即使加上 Push Lock 機制，大肥喵仍收到 GitHub email alert 關於 "Run failed"。

### 根因
**GitHub Pages build 失敗**。每次 push 到 main branch 都自動觸發 Pages deployment，
每日約 50+ 次 push（每30分鐘一次），Pages 無法處理高頻 deployment queue，
大量 build 失敗或 timeout。

### 修復
1. **`update_finance.sh`**：數據每30分鐘照常收集，但**只有偶數整點（:00 且 hour%2==0）才 push**
   - 即每日 0、2、4、6、8、10、12、14、16、18、20、22 時（12次/日）
   - 比之前 48 次/日減少 75%
2. **`update_finance_news.sh`**：同上，只在偶數整點 push
3. **`fetch_aqhi_data.py`**：同上，只在偶數整點 push

### 效果
- 每日 push 次數：~50 → ~14（集中在偶數整點，同時只 push 一次）
- GitHub Pages build 頻率：每 30 分鐘一次 → 每 2 小時一次
- Linux `flock` 鎖確保同時只 push 一次

### 經驗
- GitHub Pages 有 deployment rate limit，push 太頻繁會導致 build 失敗
- 數據收集頻率和 push 頻率應該分離：收集可以頻繁，push 要控制
- `set -e` 在 cron scripts 很危險

## [2026-07-03] 更新 (v2.9.55) - Git Push Lock 機制（防止多 cron 衝突）

### 問題描述
多個 cron jobs 同時 push 到同一 GitHub repo 導致 "cannot lock ref" / "non-fast-forward" 錯誤，
GitHub 每30分鐘發送 email alert 給大肥喵。

### 影響的 cron jobs
- `update_finance.sh`（每30分鐘，`:00` 和 `:30`）
- `update_finance_news.sh`（每小時，`:00`）
- `fetch_aqhi_data.py`（每小時，`:00` 直接調用 git push）
- `fetch_ai_news.py`（每6小時，直接調用 git push）

### 修復
1. **新增 `scripts/git-push-with-lock.sh`**：使用 `flock` 實現文件鎖，120 秒超時
2. **重寫 `update_finance.sh`、`update_finance_news.sh`**：移除 `set -e`（避免靜默失敗），改用 lock 同步
3. **更新 `fetch_aqhi_data.py`、`fetch_ai_news.py`**：`git push origin main` → `bash scripts/git-push-with-lock.sh`

### 設計原則
- `flock` 是 Linux 原生文件鎖，不會有 race condition
- 鎖文件 `.git-push.lock` 在 workspace 根目錄
- 120 秒超時確保即使一個 script hang 住也不會永久阻塞
- 推之前自動 `git pull --rebase`，推失敗自動重試 3 次
- 最終失敗仍 fallback 到 `--force-with-lease`

### 經驗
- 多個 cron jobs push 同一 repo 必須用鎖隔離
- `set -e` 在 cron scripts 很危險：Python 腳本失敗會讓 bash script 靜默退出
- Python 直接調用 `subprocess.run(['git', 'push'])` 無法利用 bash 的錯誤處理邏輯

## [2026-05-26] 更新 (v2.9.54) - 網站背景圖清理 + Service Worker 修復

### 問題描述
- 22個無用背景圖佔用 ~5MB 空間（news-bg 多版本、index-bg.png 2MB、chapters-bg 等）
- Service Worker 引用不存在的 av-novels.html
- CACHE_NAME 使用 Date.now() 導致舊快取無法清除（每次部署產生新快取）
- index.html 中 og:title 與 <title> 不一致（「首頁」vs「官方網站」）

### 修復
- git rm 移除 22 個未引用背景圖
- Service Worker：移除 av-novels.html staticUrls、CACHE_NAME 改為靜態版號 v2.1.0
- 統一 index.html og:title / twitter:title 與 <title> 為「官方網站」
- 已推送 GitHub（commit 172acf1b）

### 經驗
- repo 中有大量未引用圖片需定期清理
- Service Worker 的 cache key 不應該用 Date.now()，應用固定版本號
- OG meta 標籤應與 <title> 一致

---

## [2026-05-12] 更新 (v2.9.53) - chapters-data.json 重複條目導致「共549章」

### 問題描述
kofhk.com/chapters.html 顯示「共549章」，但實際只有536章。

### 根本原因
1. `scripts/dropbox_volume2_sync.py` 使用 `re.match(r"chapter-(\d+)\.html", fname)` 匹配文件
2. 存在 `chapter-1-restored.html` 和 `chapter-1-working.html` 兩個舊文件
3. 正則將兩個文件誤匹配為 chapter-1，導致 JSON 產生13個重複條目
4. 動態JS（`loadChaptersData()`）讀取 JSON 後顯示 `chaptersData.length`（549），覆蓋了靜態HTML的正確計數

### 修復內容
1. `scripts/dropbox_volume2_sync.py`：`re.match` → `re.fullmatch`（兩處）
2. 重新生成 `assets/chapters-data.json`（536獨特條目，無重複）
3. 刪除誤匹配的舊文件 `chapter-1-restored.html`、`chapter-1-working.html`
4. 修復 chapters.html 中錯誤的「126章」描述為「536章」

### 預防措施
- 正則匹配文件名必須使用 `re.fullmatch` 而非 `re.match`
- 每次生成 chapters-data.json 必須完整重新生成，不能追加
- 文件中不要保留 `chapter-N-xxx.html` 這種容易誤匹配的命名

## [2026-05-10] 更新 (v2.9.53) - Dropbox 同步章節未推送問題修復

### 問題描述
用戶反映 kofhk.com 看不到第519-524章節。

### 根本原因
`git push origin main` 被拒絕（遠端有新提交），但我**沒有注意到推送失敗**，繼續其他工作。 Commit `52ee7235` 只存在於本地，未能推送到 GitHub。

```
error: failed to push some refs to 'https://github.com/jyonline0604/website.git'
hint: Updates were rejected because the remote contains work that you do not
```

### 修復流程
1. `git stash` — 保存本地未提交的更改
2. `git pull origin main --rebase` — 拉取遠端並變基
3. `git stash pop` — 恢復本地更改
4. `git push origin main` — 重新推送

### 預防措施
**⚠️ 每次執行 `git push` 後，必須確認輸出是否包含 `main -> main` 或 `Everything up-to-date`**

| 推送結果 | 判斷 |
|---------|------|
| `main -> main` | ✅ 成功 |
| `Everything up-to-date` | ✅ 成功（無需推送） |
| `rejected` / `fetch first` | ❌ 失敗，需 `git pull --rebase` 後重新推送 |

**如果推送失敗，必須立即修復，不得遺留到下一個工作！**

### 為何之前沒發現？
- 推送腳本有預檢查（HTML結構驗證），但**沒有在推送失敗時發出警告**
- 我誤以為腳本 output 包含 `✅ 所有檢查通過，可以推送！` 就是成功

---

## [2026-05-08] 更新 (v2.9.47) - chapters.html 隱藏 div 重複腐壞問題修復

### 問題描述
chapters.html 文件存在嚴重腐壞：
- 每個章節組的隱藏 `<div id="group-XXX-YYY">` 被複製了 75-76 次
- 存在虛假的章節組（如 `group-3751-3860`、`group-3851-3860` 等）
- 文件大小從正常的 ~200KB 膨脹到 663KB
- Google 等搜索引擎可能索引到這些錯誤數據

### 根本原因
`update_chapters_simple.py` 每次運行都會在 chapter-groups 區域之前**添加**新的 hidden divs，但**不會刪除**舊的。隨著章節增加（從 400 → 500 → 512），這些 hidden divs 不斷累積並重複。

### 修復內容
1. 手動清理 chapters.html 中所有在 chapter-groups 之前的 hidden divs
2. 重新運行 `python3 scripts/update_chapters_simple.py` 生成正確的章節組
3. 驗證三處章節數量同步（author.html、chapters.html meta、JSON-LD）
4. 推送 GitHub

### 受影響指標
| 項目 | 修復前 | 修復後 |
|------|--------|--------|
| 文件大小 | 663 KB | 204 KB |
| 文件行數 | 8306 行 | 4596 行 |
| hidden div 數量 | 3760 個（75+倍重複） | 52 個（每組1個）|

### 預防措施
- 未來修改 `update_chapters_simple.py` 時，確保完全替換而非追加 hidden divs
- 定期檢查 chapters.html 文件大小是否合理
- **重要**：每次章節變更（新增/修改）後，必須同步重新生成 `assets/chapters-data.json`

---

## [2026-05-08] 更新 (v2.9.48) - chapters-data.json 重複條目導致顯示525章

### 問題描述
用戶反映即使刷新後仍顯示「共525章」而非正確的512章。

### 根本原因
`assets/chapters-data.json` 包含 525 個條目（13個章節重複了）：
- CH66(×2), 67(×2), 78(×2), 80(×3), 81(×2), 82(×2), 90(×3), 92(×3), 93(×3)
- JavaScript 動態載入此 JSON 計算章節數量

### 修復內容
1. 重新掃描所有 `chapter-*.html` 文件，提取章節號和標題
2. 生成乾淨的 `chapters-data.json`（移除重複，保留最後出現的正確標題）
3. 從 525 條 → 512 條
4. 推送 GitHub

### 為何之前沒發現？
- 我一直只檢查 HTML 結構和 meta tags，忽略了 JavaScript 動態載入的 JSON 數據源
- **教訓**：遇到數量顯示問題時，必須檢查所有可能的數據來源

---

## 🔧 維護八誡（快速查找）

當遇到問題時，按照以下順序檢查：

| # | 檢查項目 | 關鍵操作 |
|---|----------|----------|
| **0** | **⚠️ 內容連貫性檢查** | **請由第1章從頭開始,幫我檢查文章內容的連貫性等相關問題** |
| 1 | **中文數字正則** | 使用 `[零一二三四五六七八九十百千萬\d]+` 匹配章節號 |
| 2 | **正則同步檢查** | 修復 `update_chapters_simple.py` 時同步檢查 `update_home_simple.py` |
| 3 | **txt源文件格式** | 檢查第一行是否為 `# 第X章 · 標題` |
| 4 | **簡體字混合** | 生成HTML前檢查並轉換（葉尘→葉塵、灵→靈等） |
| 5 | **chapters.html + home.html 同步更新** | 修復後必須同時運行兩個更新腳本 |
| 6 | **四處章節數量同步** | author.html、chapters.html meta、JSON-LD、chapters-data.json |
| 7 | **GitHub推送前檢查清單** | 結構驗證 → 更新 → 提交 → 推送 → 更新SKILL |

### ⚠️ 最重要的守則：內容連貫性檢查

**每次處理新章節上傳時，必須執行：**

1. **請由第1章從頭開始,幫我檢查文章內容的連貫性等相關問題**
2. 如果發現連貫性問題（如：角色名字錯誤、劇情邏輯矛盾、時間線衝突等），必須先修復
3. 修復完成後才能生成HTML並更新章節目錄

**連貫性檢查重點：**
- 角色名字是否一致（葉塵 vs 葉尘）
- 劇情是否連貫（上文提到的情節，下文是否呼應）
- 時間線是否正確（早晨→下午→晚上 是否合理）
- 世界觀設定是否一致（修為境界、勢力名稱等）

### 常見錯誤對照

| 錯誤現象 | 根本原因 | 解決方法 |
|----------|----------|----------|
| 章節顯示「科技修真傳」 | 正則表達式 `\d+` 不匹配中文數字 | 改用 `[零一二三四五六七八九十百千萬\d]+` |
| 首頁顯示「第260章」而非標題 | `update_home_simple.py` 正則不一致 | 同步修復兩個腳本的正則 |
| 章節數量不正確 | 三處未同步更新 | 同時更新 author.html、chapters.html |

---


### ⚠️ 強制檢查清單（每次處理新章節前必讀）

**每次處理新章節前，必須運行：**
```bash
python3 scripts/chapter_task_checklist.py
```

**完整檢查清單：**
0. ✅ **⚠️ 內容連貫性檢查**（由第1章開始檢查）
1. ✅ SKILL.md 已讀取
2. ✅ 源文件格式檢查（#前綴、無簡體字）
3. ✅ **⚠️ 文章分段和標點符號檢查**
   - 段落長度是否合理（每段建議200-500字以內）
   - 標點符號是否完整（句號、逗號、頓號等）
   - 是否有大段連續文字無任何標點（超過300字無句號為異常）
   - 發現問題時，檢查txt源文件是否為完整版本
4. ✅ 修復發現的問題（如有）
5. ✅ 使用 chapter-template.html 生成HTML
6. ✅ 驗證HTML結構（`<main>`、`<h1>`、導航按鈕）
7. ✅ **⚠️ 四處章節數量必須同步**：
   - author.html `<span id="chapterCount">`
   - chapters.html meta 標籤 (`完整收錄XXX章`)
   - chapters.html JSON-LD (`numberOfItems: XXX`)
   - assets/chapters-data.json (JSON 陣列長度)
7. ✅ **同時運行 update_chapters_simple.py + update_home_simple.py**
8. ✅ 提交並推送 GitHub
9. ✅ 驗證網站顯示正確
10. ✅ 完成後更新 SKILL.md 並同步到 Second-brain + Max-backup

**⚠️ 最重要的守則：**
> **請由第1章從頭開始,幫我檢查文章內容的連貫性等相關問題**

**⚠️ 警告：**
- 每次修復章節HTML後，**必須同時運行兩個更新腳本**！
- **三處章節數量必須同步**！

**沒有通過檢查，無法執行任務！**

**⚠️ 最重要的守則：**
> **請由第1章從頭開始,幫我檢查文章內容的連貫性等相關問題**

**⚠️ 警告：每次修復章節HTML後，必須同時運行兩個更新腳本！**

**沒有通過檢查，無法執行任務！**

## [2026-07-07] 更新 (v2.9.61) - chapters-data.json field name + home.html 未更新 + Cloudflare cache

### 問題1：chapters-data.json field name 搞錯（嚴重！）
- **現象**：chapters.html 全部 link 變成 `chapter-undefined.html`
- **根因**：regenerate JSON 時用咗 `chapter` 做 field name
- **JS code 用 `ch.num`** — 兩者唔匹配
- **修復**：JSON field name 必須係 `num`，唔係 `chapter`

### 問題2：home.html 未隨 Dropbox sync 更新
- **現象**：home.html 最新章節停喺 CH1009，但網站已有 CH1015
- **根因**：Dropbox sync script 話更新 home.html 但實際冇郁到
- **檢測方法**：每次 Dropbox sync batch 後，檢查 home.html 最下面6張 chapter-card 係咪最新
- **修復**：手動執行 `python3 scripts/update_home_simple.py`

### 問題3：Cloudflare Cache max-age 錯用 43200（12小時）
- **問題**：`max-age=43200` 秒 = 12小時，但以爲係 2小時
- **修復**：改爲 `max-age=7200`（2小時）
- **教訓**：`max-age` 係**秒為單位**，唔好同小時搞錯

### 強制檢查清單新增
每次 Dropbox sync batch 完，必須驗證：
1. ✅ chapters-data.json (1015條, field=num)
2. ✅ chapters.html (JS用 ch.num)
3. ✅ home.html (最新6章 chapter-card)
4. ✅ Cloudflare cache header (max-age=7200)

---

## 📝 重要修復經驗總結 (2026-04-28)

### 1. txt源文件標題格式
- **要求**：標題行必須以 `# ` 開頭
- **後果**：缺少前綴會導致生成HTML時標題顯示為「第X章 · 第X章」
- **預防**：收到新txt文件後，立即檢查第一行是否為 `# 第X章 · 標題`

### 2. 修復txt後必須更新chapters.html
- **流程**：修復txt源文件 → 重新生成HTML → **重新運行update_chapters_simple.py** → 提交chapters.html
- **後果**：只更新HTML但忘記更新chapters.html，會導致章節列表頁顯示錯誤標題
- **預防**：將「更新chapters.html」作為標準流程步驟

### 3. 簡體字混合問題
- **發現**：上傳的txt文件含有簡體字符（葉尘、灵等）
- **修復**：建立完整簡體→繁體對照表，批量轉換
- **預防**：在生成HTML前檢查並修復所有簡體字符

### 4. 章節數量顯示（三處需同步）
| 位置 | 修正項目 |
|------|----------|
| author.html | `<span id="chapterCount">200</span>` |
| chapters.html meta | `完整收錄200章` |
| chapters.html JSON-LD | `"numberOfItems": 200` |

### 5. GitHub推送前檢查清單
- [ ] 修復後重新運行 `update_chapters_simple.py`
- [ ] 驗證 chapters.html 中的標題是否正確
- [ ] 驗證章節數量顯示（author.html、chapters.html）
- [ ] 提交並推送
- [ ] **立即更新 SKILL.md**（不等用戶提醒）

---

### 6. 中文數字正則表達式問題
- **問題**：中文章節號使用中文數字（第二百五十一章）而非阿拉伯數字
- **受影響**：`update_chapters_simple.py`、`update_home_simple.py`
- **解決**：所有章節相關正則必須使用 `[零一二三四五六七八九十百千萬\d]+` 匹配中文數字
- **模板**：
  ```python
  r'<title>第[零一二三四五六七八九十百千萬\d]+章\s*[·:：]\s*(.+?)\s*-\s*萬古塵埃</title>'
  ```

### 7. home.html 和 chapters.html 正則必須同步
- **問題**：今天發現 `update_home_simple.py` 和 `update_chapters_simple.py` 正則不一致
- **後果**：chapters.html 修復了，但 home.html 還是顯示錯誤標題
- **預防**：修復正則表達式時，必須檢查所有相關脚本


## 🎨 漫畫系統 (2026-04-29)

### 系統概述
將《萬古塵埃》文字版轉換為彩色CG漫畫版，便於視覺化閱讀。

### 目錄結構
```
manga/
  chapter-1/
    index.html          # 漫畫閱讀頁面
    01-cover.png       # 封面場景
    02-xxx.png        # 各場景圖
    ...
    characters/
      01_yechen.png   # 葉塵角色定裝照
      02_yetianba.png  # 葉天霸角色定裝照
```

### 角色設定（必須統一）

| 角色 | 年齡 | 外貌 | 服裝 | 特徵 |
|------|------|------|------|------|
| **葉塵** | 16歲 | 黑短髮，劍眉，眼神堅毅內斂 | 簡樸灰白長袍 | 頸戴暗灰色玉墜 |
| **葉天霸** | 17歲 | 英俊，驕傲神情，眉宇間有霸氣 | 紫色華麗金紋家主脈服飾 | 姿態傲慢 |
| **凌風** | 成年 | 英俊可靠 | 俠客風格服裝 | 天穹城城主 |
| **月璃** | 成年 | 深邃神秘 | 深藍近黑長裙，銀色星紋 | 間諜網絡掌控者 |

### 角色參考圖（完整列表 2026-04-30）

**重要**：生成漫畫場景時，必須使用對應的角色參考圖 URL！

#### 主要角色
| 角色 | 參考圖 URL |
|------|------------|
| 葉塵 | `https://kofhk.com/assets/manga-characters/yechen-character.png` |
| 葉天霸 | `https://kofhk.com/assets/manga-characters/yetianba-character.png` |
| 蘇清雪 | `https://kofhk.com/assets/manga-characters/suqingxue-character.png` |
| 凌風 | `https://kofhk.com/assets/manga-characters/lingfeng-character.png` |
| 月璃 | `https://kofhk.com/assets/manga-characters/yueli-character.png` |
| 王虎 | `https://kofhk.com/assets/manga-characters/wanghu-character.png` |

#### 守望者/遠古存在
| 角色 | 參考圖 URL |
|------|------------|
| 太一 | `https://kofhk.com/assets/manga-characters/taiyi-character.png` |
| 守塵 | `https://kofhk.com/assets/manga-characters/shouchen-character.png` |
| 塵淵 | `https://kofhk.com/assets/manga-characters/chenyuan-character.png` |
| 源塵 | `https://kofhk.com/assets/manga-characters/yuanchen-character.png` |

#### 暗淵閣（反派）
| 角色 | 參考圖 URL |
|------|------------|
| 幽影尊者 | `https://kofhk.com/assets/manga-characters/youying-character.png` |
| 寒淵 | `https://kofhk.com/assets/manga-characters/hanyuan-character.png` |
| 無面 | `https://kofhk.com/assets/manga-characters/wumian-character.png` |

#### 宗門
| 角色 | 參考圖 URL |
|------|------------|
| 玄冥子 | `https://kofhk.com/assets/manga-characters/xuanmingzi-character.png` |
| 墨岩 | `https://kofhk.com/assets/manga-characters/moyan-character.png` |
| 趙明軒 | `https://kofhk.com/assets/manga-characters/zhaomingxuan-character.png` |

#### 葉家/其他
| 角色 | 參考圖 URL |
|------|------------|
| 福伯 | `https://kofhk.com/assets/manga-characters/fubo-character.png` |
| 葉蒼雲 | `https://kofhk.com/assets/manga-characters/yecangyun-character.png` |
| 葉青 | `https://kofhk.com/assets/manga-characters/yeqing-character.png` |
| 趙明遠 | `https://kofhk.com/assets/manga-characters/zhaomingyuan-character.png` |

#### 角色展示頁面
所有角色參考圖已整合至角色展示頁面：
https://kofhk.com/characters.html

### 圖片生成流程

#### 步驟1：下載角色參考圖（如需要）
```bash
mkdir -p manga/characters/
curl -sL "https://kofhk.com/assets/manga-characters/yechen-character.png" -o manga/characters/yechen-character.png
curl -sL "https://kofhk.com/assets/manga-characters/yetianba-character.png" -o manga/characters/yetianba-character.png
```

#### 步驟2：規劃漫畫場景
根據章節內容規劃 7-10 個關鍵場景，每個場景：
1. 確定主要角色
2. 確定場景環境
3. 確定情緒/動作

#### 步驟3：生成場景圖片（關鍵！）
**⚠️ 正確方式**：將角色參考圖 URL **直接寫入 prompt 文字中**

```bash
# ✅ 正確：用 `image_generate` 並將角色 URL 放在 prompt 內
image_generate \
  --prompt "MAIN CHARACTER: Ye Chen, 16 years old, black short hair, sharp eyebrows, gray-white robe, jade pendant on neck. Reference: https://kofhk.com/assets/manga-characters/yechen-character.png Scene: dawn at misty mountain field, character stands alone looking at his palms..." \
  --model minimax/image-01 \
  --size 1024x1024 \
  --filename manga-ch2-01.png
```

**❌ 錯誤方式**：使用 `image` 參數（該參數僅用於編輯模式，會失敗）

```bash
# ❌ 錯誤：會失敗！
image_generate \
  --prompt "..." \
  --image "https://kofhk.com/assets/manga-characters/yechen-character.png"  # ❌ 不要用 image 參數！
```

**Prompt 格式要求**：
1. 開頭描述角色外貌（年齡、髮型、眼神、服裝、特徵）
2. 加入 `Reference: https://kofhk.com/assets/manga-characters/yechen-character.png`
3. 描述場景和動作
4. 結尾加 `High detail CG animation style, keep character EXACTLY as reference`

**示例 Prompt（葉塵在黎明荒田）**：
```
Chinese xianxia anime style manga panel. Character: young male protagonist Ye Chen, 16 years old, black short hair, sharp eyebrows, determined eyes, wearing simple gray-white traditional Chinese robe, dark gray jade pendant hanging from neck. Reference: https://kofhk.com/assets/manga-characters/yechen-character.png Scene: dawn at an abandoned medicinal field on a misty back mountain, character stands alone looking at his palms where faint gray mist swirls around. Ancient Chinese fantasy setting, misty morning atmosphere. Keep Ye Chen's appearance EXACTLY as reference. High detail CG animation style.
```

**示例 Prompt（葉天霸在家族大廳）**：
```
Chinese xianxia anime style manga panel. Character: handsome young male Ye Tianba, 17 years old, proud expression, heroic bearing, wearing luxurious purple gold-trimmed traditional Chinese robe with家主脉 emblem. Reference: https://kofhk.com/assets/manga-characters/yetianba-character.png Scene: grand clan hall, character standing arrogantly with hands behind back. Ancient Chinese fantasy setting, golden morning light. Keep Ye Tianba's appearance EXACTLY as reference. High detail CG animation style.
```

#### 步驟4：組裝漫畫 HTML
按照下方「漫畫HTML結構」組裝 index.html

### 漫畫HTML結構

```html
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <title>第X章 · 標題 - 萬古塵埃 漫畫版</title>
    <style>
        .manga-container { max-width: 800px; margin: 0 auto; }
        .manga-page { background: #0f0f1a; margin-bottom: 40px; }
        .page-image { width: 100%; display: block; }
        .page-caption { padding: 20px; text-align: center; }
        .nav-buttons { display: flex; justify-content: center; gap: 20px; }
    </style>
</head>
<body>
    <div class="manga-container">
        <header><h1>第X章 · 標題</h1></header>
        
        <!-- 每個場景 -->
        <div class="manga-page">
            <img src="01-cover.png" class="page-image">
            <div class="page-caption">
                <h2>場景標題</h2>
                <p>場景描述文字...</p>
            </div>
        </div>
        
        <nav class="nav-buttons">
            <a href="../chapters.html">← 返回目錄</a>
            <a href="../../chapter-X.html">📖 文字版</a>
        </nav>
    </div>
</body>
</html>
```

### 文字版章節導航按鈕

#### 頂部 top-bar（已存在，不動）
```html
<div class="top-bar">
    <a href="chapters.html">← 返回目錄</a>
    <div class="controls">
        <select id="themeSelect">...</select>
        <select id="fontSize">...</select>
    </div>
</div>
```

#### 底部 nav（三按鈕 + 新增漫畫版）
```html
<nav class="nav">
    <a href="{prev_url}">← 上一章</a>
    <a href="chapters.html">📖 返回目錄</a>
    <a href="manga/chapter-{N}/" class="manga-btn">🎨 漫畫</a>
    <a href="{next_url}">下一章 →</a>
</nav>
```

#### 新增 CSS 樣式
```css
.manga-btn {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    color: white;
    padding: 10px 25px;
    border-radius: 25px;
    text-decoration: none;
    font-weight: bold;
}
.manga-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(245, 158, 11, 0.5);
}
```

### 腳本工具

```bash
# 為所有章節添加漫畫按鈕
python3 scripts/add_manga_button.py

# 指定章節添加
python3 scripts/add_manga_button.py 5
```

### 漫畫按鈕更新記錄

| 日期 | 內容 | Commit |
|------|------|--------|
| 2026-04-29 | 首次添加漫畫按鈕（章節1-310） | `f0629e57` |
| 2026-04-29 | 修復為四按鈕導航（增加📚目錄） | `d3480a73` |

### 技術說明

- **使用模型**：MiniMax Image-01（Gemini/Seedream 配額不足時使用）
- **圖片尺寸**：1024x1024（正方形）
- **風格**：彩色CG修仙風格（Chinese xianxia anime）
- **生成數量**：每章 7-10 個場景

### 質量要求

1. **角色一致性**：葉塵必須是 16歲青年，不能是小孩
2. **場景數量**：每章 7-10 個關鍵場景
3. **文字配合**：每個場景需配合該章節的關鍵劇情文字
4. **角色出场**：葉塵必須在每個場景出現

### 發布流程

1. 生成所有場景圖片
2. 組裝漫畫 HTML 頁面
3. 提交到 GitHub
4. 為所有文字版章節添加漫畫按鈕
5. 更新 SKILL.md 並同步到 Second-brain 和 Max-backup

---

## [2026-05-04] 更新 (v2.9.57) - update_chapters_simple.py 正則表達式修復

### 問題描述
章節標題顯示不正確，chapters.html 中只顯示「第381章」而非「裂空蟲潮」。

### 根本原因
正則表達式中的 `[^<]+?` 非貪心匹配在某些情況下失效，無法正確提取標題。

### 修復內容
```python
# 舊（失效）
title_match = re.search(r'<title>第[零一二三四五六七八九十百千萬\d]+章\s*[·:：]\s*([^<]+?)(?:\s*-\s*萬古塵埃)?</title>', content)

# 新（正確）
title_match = re.search(r'<title>第[零一二三四五六七八九十百千萬\d]+章\s+([^<]+?)\s*[·-]\s*萬古塵埃</title>', content)
```

### 關鍵改動
1. `[·:：]` → `\\s+` — 匹配空格分隔符
2. `[^<]+?` 非貪心 → `[^<]+` 貪心 — 確保正確匹配

### GitHub推送
- **Commit**: `1b7327a0`

### SKILL 更新
- ✅ v2.9.57 已同步至 Second-brain 和 Max-backup


---

## [2026-05-04] 更新 (v2.9.58) - 章節標題顯示修復（BOM + · 前綴）

### 問題描述
1. **BOM 問題**：部分章節（如 CH400）HTML 檔案 title 標籤內含 BOM（`\ufeff`），導致正則表達式匹配失敗
2. **· 前綴問題**：CH1 等章節顯示為「· 落葉歸根」而非「落葉歸根」

### 根本原因
1. 某些章節 HTML 檔案含 BOM（chapter-382, 383, 386, 390, 394, 397, 398, 399, 400）
2. 正則表達式 `[^<]+?` 提取了「· 落葉歸根」

### 修復內容
1. **BOM 移除**：使用 `encoding='utf-8-sig'` 自動移除 BOM
2. **正則更新**：
   - 格式A: `<title>第X章 · 標題 - 萬古塵埃</title>` → 提取 `標題`
   - 格式B: `<title>第三百八十一章 標題 · 萬古塵埃</title>` → 提取 `標題`
3. **移除 · 前綴**：使用 `lstrip('·').strip()`

### GitHub推送
- **Commit**: `40b70f02`

### SKILL 更新
- ✅ v2.9.58 已同步至 Second-brain 和 Max-backup


---

## [2026-05-04] 更新 (v2.9.59) - CH410, CH412-CH420 修真內容置換

### 任務背景
大肥喵上傳10個txt文件（CH410, CH412-CH420），替換現有的科幻HTML內容。

### 上傳檔案（10個）
| 檔案名 | 章節 | 標題 |
|--------|------|------|
| 第四百一十章_古城滄州---... | CH410 | 古城滄州 |
| 第四百一十二章_黑市交易---... | CH412 | 黑市交易 |
| 第四百一十三章_危機四伏---... | CH413 | 危機四伏 |
| 第四佰一十四章_絕望平原---... | CH414 | 絕望平原 |
| 第四百一十五章_幻境考驗---... | CH415 | 幻境考驗 |
| 第四百一十六章_登山之路---... | CH416 | 登山之路 |
| 第四百一十七章_劍斬守護---... | CH417 | 劍斬守護 |
| 第四百一十八章_巨門之前---... | CH418 | 巨門之前 |
| 第四百一十九章_門後世界---... | CH419 | 門後世界 |
| 第四百二十章_葉家淵源---... | CH420 | 葉家淵源 |

### 修真關鍵詞驗證
- 葉塵 ✓
- 天淵門 ✓
- 深淵之門 ✓
- 葉滄瀾 ✓

### 技術修復
1. **num_to_cn() 函數**：正確處理 410→四百一十、420→四百二十
2. **UTF-8 BOM 處理**：使用 encoding='utf-8-sig'

### GitHub推送
- **Commit**: `3fb45671`

### SKILL 更新
- ✅ v2.9.59 已同步至 Second-brain 和 Max-backup


---

## [2026-05-04] 更新 (v2.9.60) - CH401-CH411 修真內容替換（第二批）

### 任務背景
大肥喵上傳剩餘的10個txt文件，替換舊版科幻HTML內容。

### 上傳檔案（10個）
| 檔案名 | 章節 | 標題 | 段落 |
|--------|------|------|------|
| 第四百零一章_東行啟程---... | CH401 | 東行啟程 | 63段 |
| 第四百零二章_荒山夜宿---... | CH402 | 荒山夜宿 | 51段 |
| 第四百零三章_古廟奇遇---... | CH403 | 古廟奇遇 | 19段 |
| 第四百零四章_輪迴殿使---... | CH404 | 輪迴殿使 | 31段 |
| 第四百零五章_令牌之秘---... | CH405 | 令牌之秘 | 17段 |
| 第四百零六章_風雲暗湧---... | CH406 | 風雲暗湧 | 19段 |
| 第四百零七章_天淵追兵---... | CH407 | 天淵追兵 | 23段 |
| 第四百零八章_一戰驚鴻---... | CH408 | 一戰驚鴻 | 18段 |
| 第四百零九章_東域見聞---... | CH409 | 東域見聞 | 17段 |
| 第四百一十一章_暗夜襲殺---... | CH411 | 暗夜襲殺 | 17段 |

### 修真關鍵詞驗證
- 葉塵 ✓
- 天淵門 ✓
- 輪迴令 ✓
- 深淵之門 ✓
- 葉滄瀾 ✓

### 技術修復
1. **num_to_cn() 函數**：修復 401→四百零一、409→四百零九
2. **數字顯示**：第四百零一章（不是四百一章）

### 數字轉換邏輯
```
if n >= 100: parts.append(digits[n//100] + '百'); n = n % 100
if n >= 10: parts.append(digits[n//10] + '十'); n = n % 10
elif len(parts) > 0: parts.append('零')  # 補足零
```

### GitHub推送
- **Commit**: `fda67425`

### SKILL 更新
- ✅ v2.9.60 已同步至 Second-brain 和 Max-backup


---

## [2026-05-04] 更新 (v2.9.61) - 修復章節目錄顯示問題

### 問題描述
章節目錄（chapters.html）中 CH401-420 顯示「第401章」而非實際標題（如「東行啟程」）。

### 根本原因
1. 新生成的 HTML 使用 title 格式：`第四百零一章 · 東行啟程`（不含「- 萬古塵埃」後綴）
2. `update_chapters_simple.py` 的正則表達式只支援：
   - `第50章 · 陳雷尋仇 - 萬古塵埃`
   - `第四百章 遠方之路 · 萬古塵埃`
3. 無法匹配新的中文數字格式

### 修復方案
新增 `title_match_c` 正則表達式：
```python
title_match_c = re.search(r'<title>第[零一二三四五六七八九十百千萬\d]+章\s+[·]\s*([^<]+?)(?:\s*-\s*萬古塵埃)?</title>', content)
```

### 驗證結果
| 章節 | 標題 |
|------|------|
| CH401 | 東行啟程 |
| CH402 | 荒山夜宿 |
| CH403 | 古廟奇遇 |
| CH410 | 古城滄州 |
| CH420 | 葉家淵源 |

### GitHub推送
- **Commit**: `33a39ff9`

### SKILL 更新
- ✅ v2.9.61 已同步至 Second-brain 和 Max-backup


## [2026-05-04] 更新 - 章節 351-440 更新
- 更新章節 351-440 HTML 檔案
- 更新 chapters.html 和 home.html
- GitHub推送完成

---

## [2026-05-05] 更新 (v2.9.64) - home.html 章節標題顯示修復

### 問題
首頁最新章節區域的章節標題顯示不正確：
- `<h3 class="chapter-title">` 只顯示「第460章」而非「萬古荒漠」
- 原因是 update_home_simple.py 的正則表達式未正確匹配新版HTML格式

### 根本原因
新生成的HTML標題格式為：
- `<title>第四百六十章 · 萬古荒漠</title>` （無「- 萬古塵埃」後綴）

但正則表達式要求結尾必須有 `-\s*萬古塵埃`：
```python
# 舊（錯誤）
r'<title>第[零一二三四五六七八九十百千萬\d]+章\s*[·:：]\s*(.+?)\s*-\s*萬古塵埃</title>'

# 新（正確）
r'<title>第[零一二三四五六七八九十百千萬\d]+章\s*[·:：]\s*(.+?)(?:\s*-\s*萬古塵埃)?</title>'
```

### 修復內容
- 修改 `scripts/update_home_simple.py` 的正則表達式，使用可選非捕獲組 `(?:\s*-\s*萬古塵埃)?`
- 重新生成 home.html

### GitHub推送
- **Commit**: `1b8cdd74`

### SKILL 更新
- ✅ v2.9.64 已同步至 Second-brain 和 Max-backup

---

## [2026-05-05] 更新 (v2.9.65) - 強化章節處理檢查清單

### 問題
CH441-460和CH421-440接連出現標題錯誤，根本原因是沒有強制驗證機制。

### 修復內容
更新 `scripts/chapter_task_checklist.py` 為 v2 版本：
1. 新增 `verify_html_title()` - 驗證HTML標題是否與inbound匹配
2. 新增 `verify_home_chapter_cards()` - 驗證home.html顯示標題而非章號
3. 新增 `check_simplified_chars()` - 檢測簡體字符
4. 改進 `get_new_chapters()` - 正確匹配「第四百XX章_標題」格式

### 驗證命令（每次生成後必須執行）
```bash
# 驗證HTML標題
grep '<title>' chapter-XX.html
# 正確：<title>第四百六十章 · 萬古荒漠</title>
# 錯誤：<title>第四百六章 · 頻率網絡的深層探索</title>

# 驗證home.html卡片
grep 'chapter-title' home.html | head -5
# 正確：<h3 class="chapter-title">萬古荒漠</h3>
# 錯誤：<h3 class="chapter-title">第460章</h3>
```

### GitHub推送
- **Commit**: `chapter_task_checklist.py` 已更新

### SKILL 更新
- ✅ v2.9.65 已同步至 Second-brain 和 Max-backup

---

## [2026-05-05] 更新 (v2.9.68) - CH472, CH473, CH478 補充上傳

### 處理記錄
大肥喵再次上傳3個章節，修復了之前缺失的CH472、CH473、CH478。

### 統計
| 上傳時間 | 章節 |
|----------|------|
| 20:08 (第一批) | CH461-470, CH480-489 (20章) |
| 20:29 (第二批) | CH474-476 (3章) |
| 20:32 (第三批) | CH472, CH473, CH478 (3章) |

### 仍未入庫
CH471、CH477、CH479 — 等待大肥喵上傳

### CH476/CH478/CH480 截斷問題
- inbound 檔案在段落中斷，未含完整章節內容
- 已標註，但仍生成HTML發布

### SKILL 更新
- ✅ v2.9.68 已同步至 Second-brain 和 Max-backup

---

## [2026-05-05] 更新 (v2.9.69) - CH471, CH477, CH479 第四批上傳

### 處理結果
全部 20 個章節（CH461-489）已完成入庫。

### 章節統計（最終）
| 章節 | 標題 | 段落 | 狀態 |
|------|------|------|------|
| CH471 | 歸途之路 | 59 | ✅ 完整 |
| CH477 | 輪迴之聲 | 26 | ⚠️ 截斷 |
| CH479 | 跨越門檻 | 23 | ⚠️ 截斷 |

### 截斷檔案說明
- CH476、CH477、CH478、CH479、CH480 的 inbound 檔案均不完整
- CH471-475 完整其餘章節段落正常

### 最終完成度
- **總章節數**: 489 章
- **GitHub**: `3aeabfe9`

### SKILL 更新
- ✅ v2.9.69 已同步至 Second-brain 和 Max-backup

---

## [2026-05-05] 更新 (v2.9.70) - CH491, CH500 第五批上傳

### 新增章節
| 章節 | 標題 | 段落 | 備註 |
|------|------|------|------|
| CH491 | 巔峰劫難 | 23 | ⚠️ 截斷（~2276字） |
| CH500 | 塵埃落定 | 58 | ✅ 完整（第一卷完） |

### 進度
- **總章節**: 490 章
- **最新章節**: CH500 塵埃落定（第一卷完）
- **GitHub**: `2aca8388`

### 截斷統計（已入庫但內容不完整）
CH476, CH477, CH478, CH479, CH480, CH491

### SKILL 更新
- ✅ v2.9.70 已同步至 Second-brain 和 Max-backup

---

## [2026-05-05] 更新 (v2.9.72) - 500章標題全部唯一

### 問題
24個標題重複，共53章需要改名：
- 暗流湧動 出現4次
- 天劫降臨、出現3次
- 鞏固根基、鞏固境界 各出現3次
- 其餘19個標題各出現2次

### 修改內容
| 原標題 | 次數 | 新標題 |
|--------|------|--------|
| 暗流湧動 | 4 | 劍氣凝煉/神秘老者/暗處的眼睛/長老會議 |
| 天劫降臨 | 3 | 築基天劫/三重天劫/元嬰極境 |
| 鞏固根基 | 3 | 靈力蛻變/感知天地/瀑布悟道 |
| 鞏固境界 | 3 | 靈力掌控/閉關沉澱/元嬰穩固 |
| 蒼瀾歷練 | 2 | 野獸出沒/古蹟探險 |
| 風雨欲來 | 2 | 修煉體系/危機徵兆 |
| 再入蒼瀾 | 2 | 潛行之術/隊友重逢 |
| 雖敗猶榮 | 2 | 大師兄風範/一招制敵 |
| 衝刺巔峰 | 2 | 元氣流轉/山洞隱居 |
| 藏經悟道 | 2 | 功法研讀/瓶頸困擾 |
| 遠古遺跡 | 2 | 壁畫秘密/符文陣法 |
| 塵淵揚威 | 2 | 百年天才/十六強對決 |
| 滿載而歸 | 2 | 地下通道/輪迴領悟 |
| 衝擊瓶頸 | 2 | 紫靈丹效/凝神瓶頸 |
| 塵埃未定 | 2 | 宿命對決/元氣恢復 |
| 劫後餘生 | 2 | 慘勝代價/傷後閒暇 |
| 凝神之秘 | 2 | 傳承空間/元氣液化 |
| 後期巔峰 | 2 | 力量飛躍/元嬰對話 |
| 塵埃未落 | 2 | 隱藏實力/劍招打磨 |
| 塵淵真意 | 2 | 凝神契機/傷疤經驗 |
| 苏醒的代價 | 2 | 頻率感知/核心意識 |
| 新的黎明 | 2 | 地裂關閉/共生共存 |
| 父親的足跡 | 2 | 神秘筆跡/第四個守望 |
| 深淵之門 | 2 | 晨光重現/裂縫探查 |

### GitHub
- Commit: `66e66f50`

### 驗證
- ✅ 500章標題全部唯一
- ✅ chapters.html 已更新
- ✅ home.html 已更新

---

## [2026-05-05] 更新 (v2.9.73) - 章節總數修復（400→500）+ JSON修復

### 問題描述
大肥喵在網站截圖中發現兩處章節總數錯誤：
1. **author.html**: `<span id="chapterCount">400</span>` 顯示「已有400章」
2. **chapters.html**: meta description 顯示「完整收錄400章」

### 修復內容

#### 1. author.html 修復
```html
<!-- 修復前 -->
<span id="chapterCount">400</span>

<!-- 修復後 -->
<span id="chapterCount">500</span>
```

#### 2. chapters.html meta 修復
```html
<!-- 修復前 -->
<meta name="description" content="《萬古塵埃》章節列表 - 完整收錄400章...">
<meta property="og:description" content="...完整收錄400章...">
<meta name="twitter:description" content="...收錄400章...">

<!-- 修復後 -->
完整收錄500章
```

#### 3. assets/chapters-data.json 隱藏問題 ⚠️
**問題**: JSON檔案只包含135章（當時生成後未更新）
**影響**: JavaScript動態載入時顯示不正確的章節數
**修復**: 重新生成完整500章的JSON檔案

### GitHub Commit
- `9580ef7e` - fix: update chapter count from 400 to 500
- `13c61b9c` - fix: update chapters-data.json from 460 to 500 chapters

### 預防措施
日後任何章節變更（新增/修改/刪除），必須同時更新：
- [x] author.html 的 chapterCount
- [x] chapters.html 的 meta description (3處)
- [x] assets/chapters-data.json（完整重新生成）

---

## [2026-05-06] 更新 (v2.9.53) - 首頁章節數量顯示錯誤修復

### 問題描述
首頁 (index.html) 顯示「460+章節」，但實際有 500 章節。

### 發現的問題
| 文件 | 問題 | 修復後 |
|------|------|--------|
| index.html | meta description: 460+ | 500+ |
| index.html | 文字描述: 460+ | 500+ |
| index.html | 統計數字: 460+ | 500+ |
| home.html | meta description: 130+ | 500+ |
| home.html | JSON-LD numberOfPages: 130 | 500 |
| chapters.html | JSON-LD numberOfItems: 400 | 500 |

### 修復內容
- `index.html`: 三處 460+ → 500+
- `home.html`: 兩處 130/130 → 500/500
- `chapters.html`: 一處 400 → 500

### GitHub推送
- **Commit**: `c295d617`

### 預防措施
章節數量顯示需要同步檢查多個位置：
1. index.html (meta description, 文字描述, 統計數字)
2. home.html (meta description, JSON-LD)
3. chapters.html (meta description, JSON-LD)
4. author.html (chapterCount span)

---

## [2026-05-06] 更新 (v2.9.55) - CHECKLIST 更新以包含 index.html

### 更新背景
今日修復首頁章節數量顯示錯誤（index.html 顯示 460+ 而非 500+），發現 CHECKLIST 需要更新以包含 index.html。

### CHECKLIST 更新內容

#### 四處章節數量同步（更新版）
**舊版**：author.html + chapters.html meta + chapters-data.json

**新版**：需要檢查四個位置：
1. **index.html** (meta description, 文字描述, 統計數字)
2. **home.html** (meta description, JSON-LD numberOfPages)
3. **chapters.html** (meta description, JSON-LD numberOfItems)
4. **author.html** (chapterCount span)

### 修復的文件
- `index.html`: 460+ → 500+ (三處)
- `home.html`: 130 → 500 (兩處)
- `chapters.html`: 400 → 500 (一處)

### chapter_task_checklist.py 更新
已更新預設章節數從 460 → 500，並在【6】項新增 index.html 檢查。

### GitHub推送
- **Commit**: `c295d617`

### 預防措施
每次更新章節數量時，必須檢查所有四個位置：
1. ✅ index.html (meta description, 文字描述, 統計數字)
2. ✅ home.html (meta description, JSON-LD numberOfPages)
3. ✅ chapters.html (meta description, JSON-LD numberOfItems)
4. ✅ author.html (chapterCount span)

---

## [2026-05-07] 更新 (v2.9.54) - Dropbox 第二卷自動化同步系統

### 新增功能
Dropbox 自動化同步系統建立，每天08:00自動從Dropbox第二卷下載6章並更新網站。

### 系統組件
1. **Token**: `./token-store/dropbox-token.txt` (600權限)
2. **主腳本**: `scripts/dropbox_volume2_sync.py`
3. **Cron Shell**: `scripts/dropbox-daily-sync.sh`
4. **狀態追蹤**: `.dropbox-sync/volume2_state.json`
5. **Cron Job**: OpenClaw cron @ 08:00 daily

### 流程
1. 掃描 Dropbox `/萬古塵埃/第二卷/` (CH501-CH700)
2. 比對網站已有章節 (CH1-500)
3. 取前6章未處理的
4. 下載 → 簡轉繁 → 生成 HTML → 驗證 → 更新網站 → 推送 GitHub

### 已知限制
- Link checker 顯示舊章節有441個預先存在的鏈接問題（kofhk.com URL vs 相對路徑）
- 這些是歷史遺留問題，不影響新章節

### GitHub推送
- **Commit**: `81354ed9`


## [2026-05-07] 更新 (v2.9.55) - Dropbox 自動刷新 Token

### 修復內容
解決 Dropbox Access Token 4小時過期問題

### 解決方案
使用 OAuth2 Refresh Token 實現自動 Token 刷新：
1. 建立 Dropbox App （key: hqpy450lnc4wn7b）
2. 通過 PKCE 授權流程獲取 Refresh Token
3. Token 過期時腳本自動使用 Refresh Token 換新

### 相關文件
- `.token-store/dropbox-refresh-token.txt` (Refresh Token, 永不過期)
- `.token-store/dropbox-app-creds.txt` (App Key + App Secret + Refresh Token)
- `.token-store/dropbox-token.txt` (Access Token, 自動刷新)

### 腳本更新
- `scripts/dropbox_volume2_sync.py`: 新增 `refresh_access_token()` 函數
- `get_dropbox_client()` 現在會自動檢測 Token 過期並刷新


---

## [2026-05-08] 更新 (v2.9.48) - chapters-data.json 重複條目問題修復

### 問題描述
用戶反映即使刷新後仍顯示「共525章」而非正確的512章。

### 根本原因
`assets/chapters-data.json` 包含 525 個條目，其中 13 個章節有重複：
- CH66, 67, 78, 80(×3), 81, 82, 90(×3), 92(×3), 93(×3)
- 導致 JavaScript 載入時計算出 525 章

### 修復內容
1. 從頭掃描所有 `chapter-*.html` 文件重新生成 `chapters-data.json`
2. 移除重複條目，保留正確標題
3. 從 525 條 → 512 條
4. 推送到 GitHub

### 預防措施
- 未來生成 chapters-data.json 前先檢查並移除重複條目
- 考慮將 chapters-data.json 生成邏輯整合到 update_chapters_simple.py

---

## [2026-05-16] 更新 (v2.9.53) - 小說名稱修復：科技修真傳 → 萬古塵埃

### 問題描述
用戶反映 dashboard.html、finance.html、news.html 中的左上方仍使用舊小說名字「科技修真傳」，應為「萬古塵埃」。

### 根本原因
在之前的章節更新中，僅更新了章節頁面和目錄頁面，但未同步更新網站的其他頁面（dashboard、finance、news）。

### 修復內容
1. 使用 `sed` 命令批量替換以下文件中的「科技修真傳」為「萬古塵埃」：
   - `/home/openclaw/.openclaw/workspace/dashboard.html`
   - `/home/openclaw/.openclaw/workspace/finance.html`
   - `/home/openclaw/.openclaw/workspace/news.html`
2. 替換範圍包括：meta 標籤、title 標籤、JSON-LD 結構化數據、導航列Logo、頁腳版權聲明等。

### 驗證
- 確認上述三個文件中不再出現「科技修真傳」字樣。
- 確認所有替換後的文件在本地預覽正常。

### GitHub推送
- **Commit**: `待產生` - 將在修復後推送至 GitHub。

### 預防措施
- 以後更新小說名稱時，必須同時更新所有網站頁面，而不僅是章節頁面。
- 更新 SKILL.md 並同步到 Second-brain 和 Max-backup。

---

## [2026-07-05] 更新 (v2.9.58) - 安全防線強化 + Dropbox Token 刷新修復

### 問題
1. Dropbox App 被停用，需更換 credentials
2. 安全過濾系統將 `cat > file << EOF` 寫入的機密替換為 `***`
3. Python `requests.post` 與 Dropbox API token refresh 不相容
4. Nemotron 模型在 isolated cron 中無法回應
5. `seedream-image-gen/SKILL.md` 的 API Key 存在 git history 中

### 修復
1. **Credentials 安全管理**：使用 `scripts/save-dropbox-creds.py` 寫入機密，不經 exec 輸出層
2. **Token refresh**：三個 dropbox_volume*_sync.py 的 token refresh 改用 `subprocess.run(['curl', ...])` 替代 `requests.post`
3. **Cron job 模型**：Dropbox cron 改為 deepseek-v4-flash 為主，Nemotron 為 fallback
4. **Pre-push hook**：新增 `.git/hooks/pre-push`，push 前掃描所有待推送 commits（就算 `--no-verify` 繞過 pre-commit 也會攔截）

### 安全防線（五層）
1. `.gitignore` → `.token-store/` 永不追蹤
2. `pre-commit` → commit 前攔截
3. `pre-push` 🆕 → push 前攔截
4. `scripts/scan-git-history.sh` → 定期深度掃描
5. 記憶檔加密備份 → `openssl enc -aes-256-cbc`

### 敏感資料清除
- 使用 `git filter-repo --replace-text` 從三個倉庫徹底清除 API Key
- 驗證方法：`git log --all --oneline -S "sk-kNFHUJo"` 回傳 0

### 教訓
- 機密寫入不要用 heredoc，用 Python 腳本從 stdin/argv 接收
- Dropbox API → curl，不是 requests
- Nemotron 不可靠，不適合 cron job
- pre-commit 可被 `--no-verify` 繞過，pre-push 才是最後防線
- 定期 `git log -S` 掃描所有倉庫找敏感資料

---

## [2026-07-05] 更新 (v2.9.59) - 傍晚簡報 isolated cron timeout 修復

### 問題
傍晚簡報 cron job 連續 4 次 timeout：
`cron: job execution timed out (last phase: model-call-started)`
每次 exactly 120 秒。

### 錯誤診斷過程
1. 最初判斷為 DeepSeek API 負載問題
2. 大肥喵指出：main session 用緊同一個 DeepSeek 但正常回應
3. 查 OpenClaw docs 發現 isolated cron session 有獨立 watchdog timeout
4. 出處：*"These watchdogs are capped independently from long timeoutSeconds values so cold-start/auth/context failures surface quickly"*

### 根本原因
OpenClaw isolated cron session（`sessionTarget: "isolated"`）的 model init 階段有硬性 watchdog（~120s），
獨立於 payload 的 `timeoutSeconds` 設定。
Main session 冇呢個限制。

### 修復
將傍晚簡報 cron job 改為 main session systemEvent：
- `sessionTarget`: `isolated` → `main`
- `payload.kind`: `agentTurn` → `systemEvent`
- `payload.message`: 「【傍晚簡報】」→ 「發送傍晚簡報到 Telegram」

### 經驗
- 不要先入為主以為問題在 API — 先確認 main session 能否正常 call model
- Isolated cron 的 watchdog 與 timeoutSeconds 無關，無法加長
- 純文字輸出嘅 cron job（簡報、提醒）用 main session 比 isolated 更穩定

---

## [2026-07-06] 更新 (v2.9.60) - 網站大規模優化 + Dropbox 同步 pipeline 加 Minify step

### 網站改動（由大肥喵完成）

| # | 建議 | 狀態 |
|:---:|---|---|
| 2 | chapters.html 分頁 | ✅ 每頁100章，1.15MB→854KB |
| 4 | HTML 壓縮 | ✅ 11.9MB→8.7MB，-26.7% |
| 6 | 清理 repo 雜物 | ✅ 刪除30個 .py 腳本等 |
| 7 | 導覽一致性 | ✅ index.html 跳轉+canonical |
| 8 | 多媒體優化 | ✅ 移除4MB未引用 mp3/mp4 |
| 9 | 手機閱讀體驗 | ✅ 浮動導覽列+閱讀進度 |

### chapters.html 新架構
- **不再伺服器渲染全部章節**（舊：寫入所有 `<a class="chapter-item">`）
- **改為 assets/chapters-data.json 載入資料**
- **JavaScript 客户端分頁**：100章/頁
- dropbox sync pipeline 已識別此變更並保留 JSON 更新邏輯

### Dropbox Volume4 同步 pipeline 更新
- ✅ 新增 `run_minify()` step 於 link check 之前
- 新章節生成後自動 minify，保持與現有章節一致性
- `minify_html.py` 已存在（SKIP: chapter-template.html）

### 影響的自動化任務
1. **Dropbox Volume4 同步（08:00）** → 已更新，pipeline 最終運行：
   ```
   生成HTML → 驗證 → Update scripts → Minify → Link check → JSON更新 → Git push
   ```
2. 其他 cron jobs 不受影響 ✅

### 注意事項
- `chapter-template.html` 需保持非 minified（模板文件）
- chapters-data.json 更新邏輯在 sync script 內，不需外部腳本
- 現有 chapters.html 有重複 group IDs，下次 run 會自動清理

## [2026-07-08] 更新 (v2.9.62) - chapter-template.html 外部化修復

### 背景
GitHub Actions 執行咗 11 項網站優化，包括章節頁 CSS/JS 外部化。
所有 1021 章已移除 inline style/script，改為引用 `assets/chapter.css` + `assets/chapter.js`。

### 問題
`chapter-template.html` 未同步更新，仍包含 inline `<style>` 和 `<script>`。
聽朝 Dropbox sync 生成新章節時會產生不一致：
- 重複 CSS（inline + 冇 external link）
- 沒有 `chapter.js` → 冇主題切換、閱讀時間

### 修復
- 移除 template 中 inline `<style>...</style>`，改為 `<link rel="stylesheet" href="assets/chapter.css">`
- 移除 inline `<script>...</script>`，改為 `<script src="assets/chapter.js" defer></script>`
- 保留 `chapter-nav.js` 引用
- 同步到備份倉庫 + GitHub push

### 教訓
網站外部優化後必須同步檢查所有 template 文件。

---

## [2026-07-11] 更新 (v2.9.63) - handleHash() 降序排序 group 跳頁錯誤

### 問題
- `chapters.html` 中 `handleHash()` 用 `Math.ceil(target / PER_PAGE)` 計頁數，只適用升序排列
- Default sort 係 desc（降序），1039章時 `#group-1031-1039`：
  - 應該跳第1頁（1039→940），1031-1039 全部可見
  - 實際跳第11頁（39→1），完全錯晒
- 大肥喵反映 group button 點擊後顯示錯誤章節

### 根因
`handleHash()` 假設章節升序排列（1→1039），從未考慮降序場景。大多數 user 用 default desc sort 都會 hit 呢個 bug。

### 修復
```javascript
function handleHash() {
  // ...
  let page;
  if (currentSort === 'desc') {
    const position = allChapters.length - target;
    page = Math.floor(position / PER_PAGE) + 1;
  } else {
    page = Math.ceil(target / PER_PAGE);
  }
  // ...
}
```

### 教訓
- 任何與排序相關的計算（page、anchor、hash routing）都要檢查 sort direction
- `update_chapters_simple.py` 只更新 HTML structure，不改 JS — fix 保留在 chapters.html 中
- GitHub Pages 部署 ~30s 延遲，Cloudflare 可能有短暫 stale cache

---

## [2026-07-11] 更新 (v2.9.64) - chapters.html v2 全面重構

### 問題
- 舊版 407KB，1039 條靜態 HTML chapter items hardcode
- 3000章時會有 ~1.2MB + 300 個 group buttons
- 冇搜尋、冇快速跳轉、10章一組極難用

### 新設計
- **檔案**: 407KB → 26.7KB (-94%)，全動態從 `chapters-data.json` 加載
- **Volume tabs**: 取代 100+ group buttons，只顯示有內容的卷
- **搜尋欄**: 章節號碼 + 標題關鍵字，300ms debounce
- **快速跳轉**: Hero 區輸入章節號碼，click 直達 `chapter-N.html`
- **PER_PAGE**: 20 章/頁
- **Scroll buttons**: 回到頂部 ⬆ + 直達底部 ⬇（與 chat widget 對齊）
- **Hash 兼容**: `#group-1031-1039` → 自動跳轉對應 Volume tab，`#vol-4` → filter 第四卷
- **保留**: header/nav/hamburger/PWA/chat-widget/RSS/footer 全部不變

### 同步更新
- `update_chapters_simple.py`: 完全重寫 → 只更新 meta description，不再生成靜態 HTML
- Dropbox sync 流程不變（仍會 call update_chapters_simple.py）
- 舊版備份：`chapters-v1-backup.html`

### 注意
- 章節列表完全由 JS 動態渲染，依賴 `chapters-data.json` 正確
- 如果 chapters-data.json 載入失敗，會顯示「載入失敗」提示
- Volume definitions 在 JS 中 hardcode，若卷數結構變更需要同步更新 JS

---

## [2026-07-11] 更新 (v2.9.65) - chapters-v2 cache-busting + DOMContentLoaded fix

### 問題
- 大肥喵反映 v2 上線後仍見到最新章節只有 1033（非 1039）
- 排查發現 chapters-data.json 和其他邏輯均正確

### 修復三項
1. **Cache-busting**: `assets/chapters-data.json?v=20260711v2` → 瀏覽器強制重新載入 JSON
2. **DOMContentLoaded race condition**: 
   ```javascript
   if (document.readyState === 'loading') {
     document.addEventListener('DOMContentLoaded', init);
   } else {
     init();
   }
   ```
   防止 script 在 DOMContentLoaded 後執行導致 init() 永不觸發
3. **Footer v2 標記**: 頁底加入 `<span>v2</span>` 方便 debug 確認版本

### 教訓
- 頁尾 script 不能用單純 `DOMContentLoaded` listener，必須檢查 `readyState`
- 動態 JSON 載入應加 version parameter 防 browser cache
- 部署後要加 visible version marker 方便確認新版上線

---

## [2026-07-11] 更新 (v2.9.66) - 全站升級

### chapters.html v3 人性化功能
1. **已讀/未讀標記**: localStorage `readChapters`，click 章節自動標記，✅ 圖標 + 綠色邊框
2. **閱讀進度條**: Hero 區「已讀 X/1039 章 · Y%」，漸變進度條
3. **書籤功能**: ☆/★ toggle，獨立書籤 filter，localStorage `bookmarks`
4. **NEW badge**: 最新 20 章 🆕 標記，最新 6 章顯示「新章節」

### home.html v2 人性化功能
5. **搜尋直達**: 入數字即跳章節，打關鍵字有 dropdown suggestions，從 chapters-data.json 加載
6. **閱讀 Streak**: localStorage `readingDays`，連續天數 + 鼓勵語句（🔥 連續閱讀 X 天）
7. **相對更新時間**: 🕐 X分鐘前/小時前/天前更新，60秒 auto-refresh

### 漫畫版下線
- 1040 章節 manga button 全部移除
- characters.html + 20 張 assets/manga-characters/ 圖片已刪除
- add_manga_button.py 已刪除

### 全站導航統一
- 建立 `unify_nav.py` 統一全站導航列
- 11 個頁面統一：首頁|章節|AI新聞|財經|ITV|儀表板|巴士|作者
- 移除 chapters.html 中 av-novels.html / aqhi.html (404) 連結

### 腳本更新
- `update_chapters_simple.py`: meta-only（v2 已重寫，v3 相容）
- `update_home_simple.py`: 相容（仍用 chapter-grid class）
- `unify_nav.py`: 新增 11 頁統一導航腳本

---

## 🚨 [2026-07-11] 嚴重事故 (v2.9.67) - sed line-delete 砍掉 1009 章內容

### 事故
- Commit `410c07014`: 用 `sed -i '/manga-btn/d' chapter-*.html` 移除漫畫按鈕
- 舊格式章節係 minified 單行 HTML，整行含 `manga-btn` → 整頁內容被砍
- 1009 個章節變成空白殼（只剩 script tags），需外人修復

### 根因
- `sed '/pattern/d'` 係 **delete entire line**，唔係 delete matching substring
- 單行 minified HTML 檔中，任何 matching line 都會整頁消失

### 正確做法
```bash
# ❌ 錯誤：delete matching lines
sed -i '/manga-btn/d' chapter-*.html

# ✅ 正確：targeted substring replacement
sed -i 's|<a href="https://kofhk.com/manga/[^"]*" class="manga-btn">[^<]*</a>||g' chapter-*.html
```

### 防範措施
1. **永不對 HTML 檔案使用 `sed '/pattern/d'`（line deletion）**
2. **Bulk operation 前必須先 test 1-2 files**
3. **Verify 內容完整性**：唔只 check HTTP status，要 check `<main>` tag, body size, actual content
4. **Git diff before commit**：大規模改動前 `git diff --stat` 確認改動範圍合理

---

## [2026-07-11] 更新 (v2.9.68) - chapters.html UI + 背景圖更換流程

### chapters.html 背景圖顯示問題
- 背景圖 1280×720（16:9）在 ultrawide 螢幕僅 40vh 時只顯示 ~30%
- **修複**: Hero 高度桌面 40→70vh / 手機 35→50vh
- **漸層遮罩**: 用 `::after` 偽元素（上 30%→下 75%）比 inline gradient 更靈活
- **背景定位**: `center top/cover` 比 `center/cover` 顯示更多上部內容

### UI 透明化
- `.toolbar` 背景透明：`background: var(--card-bg)` → `transparent`
- `.vol-tabs` 背景透明
- `.chapter-list` 背景透明

### 背景圖更換流程
1. 大肥喵 send 圖時要確認清楚邊張圖用邊頁
2. 最好叫佢分別用「home」同「chapter」標明
3. Telegram media 可能有 compression，inbound file 可能唔係原圖
4. 若大肥喵話「唔係我新上傳的圖片」，請佢重新 send 一次

### 教訓
- 兩張圖要分開放，唔好搞錯邊張係邊頁
- 背景圖顯示效果要考慮 hero height + gradient overlay + toolbar transparency 三者配合
- Cache-buster（`?v=2`）係解決瀏覽器 cache 嘅快速方案

---

## [2026-07-13] 更新 (v2.9.69) - home.html/index.html UI 雙重時鐘 + 日期計算錯誤修復

### 問題描述
另一個AI將 home.html 和 index.html 改為 JS 動態渲染（從 chapters-data.json 載入），但遺留三個前端 bug：
1. **雙重時鐘 🕐🕐**：HTML 已有 `<span>🕐</span>`，JS 文字又加 `'🕐 ...'` 前綴
2. **"5 天前更新"**：`renderLatestChapters()` 用 `now - (latest.length - 1)` = `now - 5天` 計算日期
3. **"無法取得更新時間"**：standalone script 在 XHR 完成前已執行，找不到 DOM 日期數據

### 根因
- 另一個AI改了靜態卡片→JS動態渲染但沒同步修正日期計算邏輯
- 獨立 relative-time script 沒有處理「章節數據尚未載入」的過渡狀態

### 修復內容
1. 移除所有 JS 文字中的 🕐 前綴，只保留 HTML `<span>🕐</span>`
2. 修正 `renderLatestChapters()` footer 日期：移除 `d0.setDate(d0.getDate() - (latest.length - 1))`，直接用 `now`
3. Standalone script：XHR 未完成時顯示「載入中…」並 `setTimeout(1000)` 重試
4. `renderLatestChapters()` 不再設定 `#updateTimeText`，由 standalone script 統一處理
5. 同步修復 home.html 和 index.html

### 對系統影響
- ✅ **零影響** Cron 任務（Dropbox sync、簡報、健康檢查等）
- ✅ **零影響** 後端數據腳本（chapters-data.json、update_*.py）
- ✅ 純前端 JS/CSS 修改，僅影響頁面顯示

### 教訓
- JS 動態渲染引入新 bug 時，必須全面檢查日期計算、DOM 操作、過渡狀態
- 靜態→動態遷移後，原有 standalone scripts 的執行時序可能改變
- 應統一由一個 script 處理時間顯示，避免多處邏輯衝突

---

## [2026-07-17] 更新 (v2.9.70) - OpenRouter Free Model Fallback 全面修復

### 問題
- 多個 isolated cron sessions（簡報、audio-tts、version-check）連續 failure
- 根因：(1) 部分 job 完全冇 fallbacks，(2) 部分 fallbacks 用錯 `openrouter/` prefix 格式，(3) DeepSeek free tier timeout + Gemini quota exhausted

### 修復
1. 從 OpenRouter 344 models 中 review 出 16 個適合做 agent fallback 嘅 free models（✅ tools support）
2. 最佳 fallback chain：NVIDIA Nemotron Ultra/Super → Qwen Next → Gemma 4 → openrouter/free
3. 已更新 4 個 cron jobs 嘅 fallbacks（daily-audio-tts、早上簡報、傍晚簡報、Version Check）
4. 深夜簡報 timeout 由 180s→300s；Version Check timeout 由 180s→300s

### 任務影響
- ✅ 零負面影響：只改 fallback model list + timeout，不改業務邏輯
- ⚠️ 中午簡報 (66957fcc)：list 有但 get 唔到，可能 orphan，需要手動檢查

---

## [2026-07-17] 更新 (v2.9.71) - Chapter 7 Audio 修復 + Script Filename Bug

### 問題
- Chapter 7 AI 語音朗讀冇反應
- 根因：`generate_tts()` output `chapter-{N}-final.mp3`，但 `inject_audio_player.py` expects `chapter-{N}.mp3`
- R2 upload 返 200 success 但 public URL 404（filename mismatch）

### 修復
1. 手動上傳 `chapter-7.mp3` 到 R2 → ✅ HTTP 200
2. Fix `daily_audio_sync.py`: compressed output 由 `-final.mp3` 改為 `.mp3`，用 `shutil.move()` rename temp file

### 教訓
- Pipeline filename convention 要統一 — upstream output name = downstream expected name
- R2 upload success ≠ public URL accessible，要 verify 最終 URL

---

## [2026-09-06] 更新 (v2.9.74) - 簡報 timeout 加固 + 同步腳本假失敗修復

### 修復內容
1. 三個簡報 cron job（早上 08:15 / 中午 12:55 / 傍晚 17:55）timeout 300s→600s：zai 推理模型回應慢，300s 會超時（傍晚簡報 17:55 首 run 超時實證）。CLI：`openclaw cron edit <id> --timeout-seconds 600`
2. dropbox_volume4/5_sync.py 移除 update_home_simple.py 呼叫：home.html 已改為 JS 動態載入 chapters-data.json，靜態網格不存在，呼叫必定失敗並令同步回報假失敗。真實數據由 update_chapters_simple.py + update_chapter_counts.py 覆蓋

### 根本原因
- home.html 2026 年中改版為動態渲染後，舊靜態更新腳本無同步退役
- 推理模型（glm-5.3-flash）回應時間長，job timeout 要預鬆

### 解決方法
- 過時腳本呼叫直接移除（先實測確認必敗 + 驗證無數據遺漏）
- cron timeout 用 CLI edit 而非 automations tool（isolated session 受限）

---

## [2026-09-12] 更新 (v2.9.75) - 補記：Audio Sync fallback 修復（隔離 session 週五執行）

### 修復內容
- 每日 Audio Sync 10:00 job fallbacks 由死透嘅 openrouter free models 改為 zai/glm-5.3-flash + 備援測試；timeout 300s→600s（Sep 12 10:00 首跑成功驗證）
- 每日健康報告 22:00 model 轉 MiniMax-M3 + OpenRouter free fallbacks（避 zai 週配額，2026-09-12 晚生效）

### 根本原因
- OpenRouter key Sep 6 換新後週中失效（401），舊 fallback 全滅放大咗 zai 配額爆嘅影響

### 教訓
- 隔離 session 執行嘅修復都要補入 skill 日誌（config 更改追溯性）

---

## [2026-09-13] 更新 (v2.9.76) - AQHI push 併發競爭修復

### 修復內容
- update_aqhi.sh push 前加 `git pull --rebase origin main`：消除與財經/新聞/Vol5 同步 job 併發 push 嘅「fetch first」拒絕（aqhi-update.log 長期警告源）

### 根本原因
- 多個 cron job 同時 push 同一 repo，fast-forward 檢查失敗；原腳本 push 失敗只 log 唔重試

---

## [2026-09-16] 更新 (v2.9.77) - Volume 6 啟動 + 財經 3-tier fallback + Dropbox token auto-renew

### 新增功能
- **Volume 6 Dropbox 同步 infra**：
  - `scripts/dropbox_volume6_sync.py`（mirror V5，fix boundary 1190→1460 + chapters/vol6-only scan）
  - `scripts/dropbox-volume6-daily-sync.sh`（11:00 HKT 每日）
  - `.dropbox-sync/volume6_state.json`
  - 系統 crontab 加 `0 11 * * *` → `dropbox-volume6-daily-sync.sh`
  - cron-guardian.sh 加 V6 rebuild case + FIXED + SYSTEM_TASKS lists
  - 首批 6 章已 publish：CH1461-CH1466（2026-09-16）

- **財經數據 fallback chain 全面加固**（commit `32ce63814` + `6f3d2066b`）：
  - Crypto 3-tier：CoinGecko（primary + retry/backoff）→ CoinCap → CoinPaprika
  - Commodities 3-tier：Yahoo Finance → Stooq.com（CSV API）→ hardcoded mock
  - Stocks/Forex/Bonds：加 `is_fallback: True` 標記（透明度統一）
  - 全 5 個 category fallback path 都有 `is_fallback: True` flag

- **Dropbox token auto-renew**（commit `4f30c6241`）：
  - `scripts/renew_dropbox_token.py`：3次 retry + exponential backoff (1/2/4s)
  - `scripts/renew-dropbox-token.sh`：wrapper，timeout 60s + 失敗 Telegram 通知
  - 系統 crontab `0 */3 * * *`（token 4hr 過期，3hr cron buffer）

### 修復內容
- fetch_finance_data.py 修 sed patch 撞 regex bug（success path 唔再被標 is_fallback）
- 統一 `_mark_fallback` + `_request_with_retry` helper 畀全 5 個 category 用
- V6 state.json init bug：`synced_to_site: 0` (int) → `[]` (list) 避免 TypeError

### 根本原因
- 09-16 21:00 cron 因 CoinGecko read timeout + CoinCap DNS 失敗導致 crypto 跌入 hardcoded fallback 但無 transparency 標記 → 用戶揭發財經版數據虛構
- 09-12 token 過期慘劇：cron job 全部死但無自動 renew 機制

### 教訓
- 任何 fallback data 必須標 `is_fallback: True` 避免誤導（透明度係 trust 嘅基礎）
- Copy+edit+deploy 後必須 run test 確認（script syntax OK ≠ runtime OK）
- 重要 token 必須 auto-renew（token lifetime 4hr → cron 3hr 留 buffer）
- 多 source fallback chain 設計：Tier 1 primary + Tier 2 backup + Tier 3 mock，唔好淨係靠單一 source


---

## [2026-09-19] 更新 (v2.9.78) - OpenClaw 2026.9.2 → 2026.9.5 + Node 升級教訓

### 修復內容
- **Node v22.23.2 → v24.21.0**（via nvm）：OpenClaw 2026.9.5 需要 Node ≥24.16
- **OpenClaw npm 版本升級**：2026.9.2 → 2026.9.5（commit `npm i -g openclaw@latest`）
- **self-contained binary 阻擋升級**：`/home/openclaw/.openclaw/tmp/agent-cli/openclaw` 帶 embedded Node v22.23.2 搶 PATH priority；**必須 `rm` 咗先升級有效**

### 根本原因
1. OpenClaw CLI 首次運行會喺 `~/.openclaw/tmp/agent-cli/` 生成 self-contained binary（含 embedded Node），後續 upgrade npm 版本唔會 touch 呢個 binary
2. `~/.npmrc` 嘅 `prefix=/home/openclaw/.npm-global` 同 nvm 全局 node 衝突，要 `nvm use --delete-prefix v24.21.0` 清 prefix
3. systemd gateway service 自動重啟後會重生成 tmp/agent-cli binary — 每次 restart 後都要 rm

### 教訓
- **PATH 優先順序陷阱**：agent-cli binary 永遠搶先 npm-global → 要做系統級 upgrade 必須刪 agent-cli
- **`openclaw update` 唔會跨 binary**：self-contained 同 npm 兩套裝置並存，update 只 touch 一邊
- **node 同 binary 必須匹配**：embedded node v22.23.2 + npm node v24.21.0 = 不一致會跑出唔同行為
- **`nvm use --delete-prefix` 係關鍵**：解決 `.npmrc` prefix 同 nvm global 衝突

### 升級 checklist（2026-09-19 實戰）
1. `nvm install 24` → 裝 v24.21.0
2. `nvm use --delete-prefix v24.21.0` → 解 npmrc prefix 衝突
3. `rm /home/openclaw/.openclaw/tmp/agent-cli/openclaw` → 刪 self-contained binary
4. `npm i -g openclaw@latest` → 升 npm 版到 v2026.9.5
5. `systemctl --user restart openclaw-gateway` → 重啟揾新 binary
6. `which openclaw && openclaw --version` → 確認指 npm version
7. `journalctl --user -u openclaw-gateway -n 20` → 確認 startup log

Refs: 大肥喵 2026-09-19 11:08 '怎樣更新ubuntu 主機內的 node' + 11:13 'B'

---

## [2026-09-19] 更新 (v2.9.77) - OpenClaw 2026.9.5 更新完成（外部修復代理）

### 事件
- Node 升級 v24.21.0 後，update 撞「global-install-foreign-destination」（nvm node 24 有第二套 OpenClaw，服務用 ~/.npm-global 嗰套）
- update 系統自動啟動 opencode 修復代理完成收尾：2026.9.5 安裝成功、13 日「update in progress」旗標清除、gateway 重啟 healthy

---

## [2026-09-20] 更新 (v2.9.78) - 版本檢查腳本誤報修復

### 修復內容
- check-openclaw-version.sh PATH 移除排先嘅 ~/.npm-global/bin，改用 nvm node24 bin
- 根因：gateway 已改用 nvm 安裝（2026.9.5，systemd ExecStart 已指向），舊 ~/.npm-global（2026.9.2）係孤兒；腳本硬編碼 PATH 讀咗孤兒版本 → 每日誤報「有新版本」
- 驗證：2026.9.5 == latest 2026.9.5 ✅

### 教訓
- 安裝位置遷移後，所有硬編碼舊路徑嘅腳本都要同步檢查

---

## [2026-09-20] 更新 (v2.9.79) - send-briefing.sh schema 失配修復

### 修復內容
- send-briefing.sh PATH 移除 ~/.npm-global/bin，改用 nvm node24 CLI（同 v2.9.78 版本檢查腳本同一類病）
- 根因：gateway 升級 2026.9.5 後 SQLite schema 15→17，孤兒舊 CLI（2026.9.2 schema 15）啟動即拒絕 → 9/19 傍晚、9/20 早上 system cron 簡報連續發送失敗
- 驗證：新 CLI cron list 讀 schema17 數據庫正常 ✅

### 教訓
- 安裝遷移後受影響腳本：check-openclaw-version.sh、send-briefing.sh（仲有冇其他 ~/.npm-global 硬編碼要逐步排查）
- OpenClaw cron jobs（走 gateway）唔受影響；受影響嘅係 system cron 直調 CLI 嘅腳本

---

## [2026-09-22] 更新 (v2.9.80) - AQHI rebase autostash 完整修復

### 修復內容
- update_aqhi.sh 嘅 `git pull --rebase` 加 `--autostash`：DREAMS.md（Memory Dreaming job 輸出）長期未提交令 rebase 靜默拒絕 → push 持續被拒（9/13 嘅修補唔完整）
- 實測：髒工作區下 rebase 成功（Already up to date）

### 教訓
- 修併發 push 競爭時要考慮工作區有其他 job 嘅未提交輸出（autostash 係正解）
- Vol5→Vol6 係正常交接（Vol6 由 CH1461 接手，1-1521 無缺口），簡報「Vol5 orphaned 需補返」係誤判，切勿補返

---

## [2026-09-22] 更新 (v2.9.81) - AQHI push 重試循環（競賽根治）

### 修復內容
- update_aqhi.sh push 改 3 次重試循環（pull --rebase --autostash → push，失敗等 10s 再試）
- 根因升級認知：9/20 autostash 只解決 DREAMS.md 髒工作區；真兇係 16:00 財經 job 同分鐘寫 finance-news.json — autostash 剛 stash 完，rebase 又見新改動 → 「Cannot fast-forward」abort

### 教訓
- 共享工作區多 job 併發 git 操作，單次 attempt 贏唔到秒級競賽，要重試循環

---

## [2026-10-01] 更新 (v2.9.82) - cron-guardian 復活 + Audio Sync 重建收編

### 修復內容
1. cron-guardian.sh PATH 移除 ~/.npm-global/bin（孤兒 2026.9.2 CLI，schema15 讀唔到 gateway schema17）→ 改用 nvm node24 bin。呢個自癒機制自 9/19 schema 升級後一直靜默失效（每 run 報「gateway 唔通？」誤導）
2. guardian 10/1 08:38 首次成功端到端運行：發現 Audio Sync job 缺失 → 自動重建；已為重建 job 補 model=zai/glm-5.3-flash + fallbacks=zai/glm-5.3 + timeout 600（模板原本冇帶 model，會用死 OpenRouter 預設鏈）
3. guardian system cron 期望清單移除已完成退役嘅 Vol5（Vol6 由 CH1461 接手，章節 1-1564 無缺口），避免以後誤報「需補回」

### 教訓
- 安裝位置遷移後嘅硬編碼 PATH 影響面係全部 system cron 腳本：check-openclaw-version.sh（v2.9.78）、send-briefing.sh（v2.9.79）、cron-guardian.sh（本版）— 遷移後要逐一排查
- guardian 重建模板必須帶齊 model/fallbacks/timeout，否則重建出嚟嘅 job 會用死預設鏈

---

## [2026-10-21] 更新 (v2.9.83) - 模型改名炸 cron override + provider billing 空窗

### 事件
- OpenClaw 升級 2026.10.5 時 minimax 模型改名 MiniMax-M3 → MiniMax-M3.1-Flash；cron job 嘅 model override 仲用舊 id，被 agents.entries.main.modelPolicy.allow 整個 job 拒絕（錯誤訊息係 policy 拒絕，唔似模型故障）→ 早上/中午/傍晚簡報 + 健康報告各 4 連敗
- 同期 zai 帳戶 429 余额不足 → heartbeat 隊列積壓 29 連敗 + 記憶自動日誌缺檔

### 修復
- 大肥喵 10/21 15:37-15:43 已改 agent default + 全部 cron job override 為新 id（cron-guardian 驗證 policy 全綠）✅
- 補跑早上簡報驗證修復生效

### 教訓
- 升級 OpenClaw 後要即刻核對：(1) 各 cron job payload.model / fallbacks (2) cron-guardian.sh 重建模板 (3) agents.*.modelPolicy.allow — 改名會靜靜令 job 全滅
- provider 級 billing/配額掛掉 = 全鏈盲，必須至少一個跨廠可用後備（否則完全無後備）

---

## [2026-10-21] 更新 (v2.9.85) - cron model override 失效陷阱 + payload override 會關咗 fallbacks

### 問題描述
1. **OpenClaw cron job 全線 modelPolicy 拒絕**：舊 override `minimax/MiniMax-M3` 唔喺 `agents.entries.*.modelPolicy.allow` 入面，preflight 直接拒（錯誤訊息：automation model override 'minimax/MiniMax-M3' rejected by agents.entries.*.modelPolicy.allow）。
2. **補跑仍然 600s timeout**：修正 override 後，manual run 卡喺 `model-call-started` 整整 600s。log 顯示 `[model-fallback] configured fallbacks disabled by user model override` —— 即係 **job payload 設咗 model override 之後，agents.defaults.model.fallbacks 唔會生效**，單一模型 hang 就無後備接手。
3. **heartbeat-main 連續 29 次 error**：main session 嘅 user model override 停喺 `zai/glm-5.3-flash`，該 provider 429 餘額不足 → 每次 heartbeat 都係 agent-runner-failure。

### 根本原因
- Model id 改名/下架後，cron job payload 同 cron-guardian.sh 模板入面嘅舊 id 唔會自動跟住改，config policy 又會喺 preflight 階段硬拒。
- payload model override 係「專用模式」：會覆蓋掉 fallback 鏈，變成單點故障。
- 逐個 session 嘅 user model override 會令該 session（連 heartbeat）脫離全局 model 設定。

### 解決方法
1. 全部 8 個 OpenClaw job 嘅 `payload.model` 統一改為 `minimax/MiniMax-M3.1-Flash`，並喺 `modelPolicy.allow` 列出同一組 id（minimax + openrouter free + gemini flash lite）。
2. **同步更新 `scripts/cron-guardian.sh` 入面嘅 `--fallbacks` 模板**（cron-guardian 會用自己嘅模板重建 job，唔改就會還原返舊值）。
3. 主 session 用緊嘅 zai 額度問題 → 切返 MiniMax-M3.1-Flash。
4. 補跑唔當驗證：一定要睇 `openclaw cron runs <id>` 嘅 run history（status / durationMs / error）確認係真成功。

### 檢查清單（下次升級 / 改 model id 必做）
- [ ] `openclaw cron list --json` 逐個 job 睇 `payload.model` + `payload.fallbacks` 係咪全部喺 `modelPolicy.allow` 入面
- [ ] `grep -n 'model\|fallbacks' scripts/cron-guardian.sh` 睇重建模板有冇舊 id
- [ ] `crontab -l` 確認 system cron（send-briefing.sh 08:15/17:55、Dropbox Vol4/5/6、財經/AQHI、記憶備份、自動記憶）全部在列
- [ ] `openclaw cron runs <id>` 睇真實執行結果，唔好只睇 `lastRunStatus`

---

## [2026-10-21] 更新 (v2.9.86) - Provider 退場（ZAI/DeepSeek 唔再充值）+ cron 自癒機制補上 model-policy 檢查

### 問題描述
1. **大肥喵 10/21 15:54 確認：zai 同 deepseek 暫時唔會再充值**。舊 fallback 鏈仲留住 `zai/glm-5.3-flash` + `deepseek/deepseek-v4-flash` → 一被 fallback 就撞 429 billing / 401 auth，白白拖慢兼拖冧其他後備
2. **cron-guardian.sh 有盲區**：佢只查 job「存在 + enabled」，**唔查 payload.model / fallbacks**。所以 4 連敗（modelPolicy 拒絕）期間，guardian 日誌照寫「✅ 全部正常，無需修復」— 自癒機制自己失效咗
3. **timeout 600s 唔夠**：修正 override 後，簡報類 job 仍然跑足 600s 撞 `model-call-started` timeout（payload model override 會覆蓋全局 fallbacks，單一模型 hang 就死）

### 根本原因
- Provider 退場時，只改 job payload 唔夠 — `agents.*.modelPolicy.allow` 仲留住舊 id，就會由 policy 層直接拒絕整個 job，錯誤訊息係「not in allow list」（唔似 billing，難查）
- 自癒腳本只覆蓋「結構」唔覆蓋「執行參數」→ 結構正常但執行必死的 job 會被當成健康

### 解決方法
1. `agents.defaults.modelPolicy.allow` + `agents.entries.main.modelPolicy.allow`：**完全移除 zai/* 同 deepseek/*（付費 provider）**，只留 minimax + openrouter free + google；`agents.defaults.models` 同樣清走 zai/glm-5.3、zai/glm5.3-flash、deepseek/*、openrouter/inclusionai/ling-3.0-flash:free
2. 6 個 LLM cron job fallback 鏈統一 → 4 個 OpenRouter free：`nemotron-3-super-120b-a12b:free` → `deepseek-v4-flash:free` → `qwen3-coder:free` → `minimax-m2.5:free`
3. **新增 `scripts/cron_model_guard.py`**：自動比對每個 job `payload.model` / `payload.fallbacks` vs `modelPolicy.allow`，違規即自動改返 primary。已用「故意注入 zai/glm-5.3」實測：守衛自動偵測 + 自動修復 ✅
4. cron-guardian.sh 加 Part 1b 呼叫上述守衛；重建模板 6 處 fallback 同步改（rebuild 出嚟嘅 job 先會合法）
5. timeout 放寬：簡報類 600→1200s、Audio Sync 600→1800s
6. provider catalogue 補回 `MiniMax-M3.1-Flash` 定義（M3 已改名下架，仲留舊 id 會 401）

### 檢查清單（provider 退場 / 改 model id 必做）
- [ ] `openclaw config get agents.defaults.modelPolicy.allow` 同 `agents.entries.main.modelPolicy.allow` → 移除要退場嘅 provider
- [ ] `openclaw config get agents.defaults.models` → 清走退場 provider 嘅 models 項
- [ ] 逐個 job 睇 `payload.model` + `payload.fallbacks` 全部喺 allow list 入面（`openclaw cron list --json`）
- [ ] `grep -n -- "--model|--fallbacks" scripts/cron-guardian.sh` 睇重建模板有冇舊 id
- [ ] 補跑一個 job 並用 `openclaw cron runs <id>` 睇真實 status / durationMs / deliveryStatus
- [ ] `python3 scripts/cron_model_guard.py --fix` 應回報 "every job model override is within policy allow list"

### 教訓
- Provider 退場要**由 modelPolicy.allow 開始清**，唔係淨係改 fallback
- 免費後備全部集中喺 OpenRouter 一間 = 單點故障；google 永久 geo-block → 目前冇跨廠後備，要留意
- 「自癒腳本」自己都會有盲區：守衛一定要覆蓋 job 嘅**實際執行參數**，唔只係存在性

---

## [2026-10-21] 更新 (v2.9.87) — 傍晚簡報日結 cron 連續 5 次超時，自動修復

### 問題描述
- OpenClaw cron job「傍晚簡報 17:55 — 日結」(id f8b447b6) 連續 5 次 `consecutiveErrors`，error = `cron: job execution timed out (last phase: tool-execution-started)`，每次卡死喺 20 分鐘上限（lastDurationMs ≈ 1200700）。

### 根因
- payload 指示太多步驟、逐項分開 call 工具，每個 exec 都慢，累計超過 20 分鐘 scheduler 上限；timeoutSeconds 設 1800 但實際被 1200s 硬頂切斷。

### 修復
- `openclaw cron edit f8b447b6-... --timeout-seconds 0`（取消 scheduler timeout）
- 精簡 message：要求「只做 1 次 exec 收集所有資料 + 最多 1-2 次讀檔」，所有外部指令加 `timeout 20` 保護。

### 教訓
- isolated cron session 有工具呼叫時間上限，prompt 必須強制限次數；多項檢查要合併成單一 exec 批次。
- `openclaw cron edit` 先有 --message / --timeout-seconds / --model；`openclaw cron update` 唔存在。

---

## [2026-10-21] 更新 (v2.9.88) — 健康報告清理遺留空檔 + 17:55 job timeout 修正

### 問題描述
1. **工作區根目錄有遺留空檔 `4}`**（0 bytes，2026-07-16 遺落）：係 shell 重定向 typo 造成嘅 artifact，已被 commit 入 git（ed97fc6a6）。
2. 「傍晚簡報 17:55 — 日結」喺 v2.9.87 修復後仍然 5 次 timeout；`--timeout-seconds 0` 只係喺 18:16 成功跑咗一次（319s）。

### 修復
- `git rm "4}"` + commit + `git push origin main`（網站倉庫 jyonline0604/website）。
- `openclaw cron edit f8b447b6-... --timeout-seconds 1800`（由 0 改為有限但充足嘅 30 分鐘，避免無限卡死同時確保唔會撞 1200s 硬頂）。
- 「每日健康報告 22:00」timeout 同樣由 1200 → 1800。

### 教訓
- `timeout-seconds 0`（無上限）唔係最佳解：一旦 prompt 又變複雜就會無限掛住。有限但 > 預估執行時間嘅值（1800）先係穩健選擇。
- shell 重定向 typo 產生嘅怪檔名（`4}`）會被 git 當成合法路徑 commit 入去；清理時要 `git rm` 而唔係 `rm`，否則下一個 pull 又會還原。
- `openclaw cron list --json` 嘅 `state.consecutiveErrors` 係累計值，修好 model/timeout 之後要睇 `openclaw cron runs <id>` 確認新一次執行真係 ok 先可以當歸零。

---

## [2026-10-21] 更新 (v2.9.89) — code-mode exec 呼叫方式 + 遺留 .bak 清理判準

### 問題描述
1. Code Mode exec 內寫 `tools.exec(...)` 會直接炸 `ReferenceError: tools is not defined`（exec bridge 會喺 code-mode / shell-mode 之間隨機跳，唔穩定）。
2. 工作區殘留 `scripts/audio-daily-cron.sh.bak`（2026-07-27 舊備份，無任何 script 引用）同 `.token-store/dropbox-token.txt.bak`。

### 修復
- Code mode 一律用全域 `exec({command, timeoutSeconds})`，唔好寫 `tools.exec`；輸出讀 `r.output`，若果係 null 就 `text(JSON.stringify(r))` 再解析 `output[0].text`。
- 刪除冇人引用嘅 `scripts/audio-daily-cron.sh.bak`；保留 `renew_dropbox_token.py` 自動生成嘅 `dropbox-token.txt.bak`（功能安全副本，每次 token 續期會自動重建，唔係遺留檔）。

### 教訓
- exec bridge 係隨機 flaky：同一段 code 上一秒有 `tools`、下一秒冇 → 每次 exec 都要寫防禦式輸出解析。
- 清理 `.bak` 前必須 `git check-ignore -v` + `grep` 引用：被 gitignore 嘅自動生成備份唔應該亂刪（否則會破壞 rollback 安全網）。
- 深度掃描遺留檔用 `find . -not -path './.git/*' \( -name '*_output.txt' -o -name '*.tmp' -o -name 'cron_output.txt' ... \)`，唔好只睇 `git status`（gitignored 嘅檔案佢唔會報）。

---

## [2026-10-21] 更新 (v2.9.90) - 根目錄殘留備份檔批量清理 + .backup-pass 保護

### 問題描述
網站根目錄堆積 30 個 2026-04 時期嘅備份殘留檔（`*.html.backup*`、`*.html.backup.YYYYMMDD_HHMMSS`、`*.new-design.backup`、`chapters.html.backup_test`、`audio_sync_output.log`），全部被 .gitignore 排除，所以 `git status` 睇唔到，長期無人清理。

### 根本原因
歷次 HTML 修復流程用「複製原檔 → 改檔」方式留低備份，冇回收步驟；`.gitignore` 令佢哋對 git 檢查完全隱形。

### 解決方法
1. `git ls-files --others --ignored --exclude-standard | grep '\.backup'` 列出所有隱形殘留檔
2. 逐個 grep 引用 + `git ls-files --error-unmatch` 確認無引用、未被 git 追蹤
3. 用 `gio trash`（可復原）逐個清走

### ⚠️ 必須保留（唔可以當殘留檔清理）
| 檔案 | 用途 |
|------|------|
| `.backup-pass` | 記憶備份 openssl 加密密碼，scripts/backup-memory.sh / daily_backup.py 依賴 |
| `.token-store/dropbox-token.txt.bak` | renew_dropbox_token.py 每次續期自動生成嘅回滾副本 |
| `av-novels.html.broken.20260420_142301` | git 已追蹤檔案，刪除會產生 commit diff |

### 新增標準
- 健康報告清理前：先 `git check-ignore` / `git ls-files --error-unmatch` 判斷屬性，再 grep 引用，最後先動手
- 清理用 `gio trash` 而唔係 `rm`，保留可復原性
- 清理後必須驗證 live 對應檔（chapters.html / news.html / news-data.json）仍然完好 + 網站仍然 200

---

## [2026-10-22] 更新 (v2.9.91) - 簡報巡檢新增 systemd failed 檢查 + root 權限限制處理

### 問題描述
早上簡報巡檢發現 `systemctl --failed` 有 `logrotate.service loaded failed failed`（journal: `error: cloud-init-base:1 duplicate log entry for /var/log/cloud-init.log`）。unattended cron session 冇 root 權限：`sudo -n` 被拒（interactive authentication required）、`exec elevated:true` 被 gate 擋（tools.elevated.enabled 未開），所以自動修復做唔到。

### 根本原因
/etc/logrotate.d/cloud-init 同 /etc/logrotate.d/cloud-init-base 兩個檔案內容完全重複（都輪轉 /var/log/cloud-init*.log），logrotate 遇到重複 log entry 就 skip 個檔並 exit 1，systemd 就標記 service failed。

### 解決方法
1. 巡檢加入 `systemctl --failed --no-pager` + `journalctl -u <service> -n 30 --no-pager`，唔可以淨係睇 df / free
2. 遇到需要 root 嘅修復：唔好空轉同反覆重試，直接記錄到 memory/issues.md + 簡報報告，並附一段可以一鍵執行嘅人手指令
3. 權限提升路徑：exec `elevated:true` 需要 tools.elevated.enabled 開啟，unattended cron session 一律唔可用 → 唔好再試

### 新增標準
- 簡報巡檢 checklist 加：systemd failed unit、logrotate/rotate 類服務健康
- root 權限問題屬於「需人手處理」報告項，唔會令本簡報標記為 FAIL
- 其他巡檢重點：scripts/ 對應檔案逐個存在性檢查（crontab 有條目但腳本唔存在 = 隱性故障）、Dropbox 三卷 state 同線上章節數一致性、OpenRouter fallback key 實測 /api/v1/models

---

## [2026-10-22] 更新 (v2.9.92) — 簡報 job 超時治理 + Dropbox 同步修復驗證流程

### 問題描述
「中午簡報 12:55」(66957fcc) 於 12:55 首次執行撞 20 分鐘 scheduler 硬頂（lastRunStatus=error、lastErrorReason=timeout、consecutiveErrors=1、lastDurationMs=1200408），無報告送到 Telegram。同期 Volume 4 於 11:00 因 token 競態中止（Dropbox token file is empty or missing）。

### 根本原因
1. isolated cron job prompt 拆成多個工具呼叫，累積執行時間超時；--timeout-seconds 設 1200 就係硬頂。
2. 四個寫 Dropbox token 嘅位置用非原子 open(TOKEN_FILE,"w")，truncate→write 窗口被並發進程讀到空字串；同一時間三個 volume job 併發 push 同一 site repo。

### 解決方法
1. openclaw cron edit <id> --timeout-seconds 1800 + prompt 頂部加「只做 1-2 次 exec，一次過用一條 bash 指令收集所有資料」效率規則（與 17:55 日結 job 一致）。
2. token 寫入改 tmp + fsync + os.replace() 原子寫；read_token() 加重試 helper；crontab 一律叫 dropbox-volumeN-daily-sync.sh wrapper，三個 wrapper 全部 flock -w 900 /tmp/dropbox-sync.lock 序列化；backup-memory.sh 加 flock + push 前 git pull --rebase 重試。
3. 修完必做「手動補跑驗證」：直接跑 wrapper，確認 exit 0 + state 分歧自動修復 + 章節數一致。

### 新增標準
- 巡檢必查「上一個 12:55/17:55 job 自己有冇 timeout」——自己嘅 job 狀態差過其他 job 先值得即時修。
- isolated cron job 一律限制工具呼叫次數；加大 timeout 只係買時間，唔係根治。
- crontab 直接呼叫 python3 scripts/x.py 會漏掉 wrapper 入面嘅加鎖邏輯，一律改 wrapper。
- 12:55 job 另需檢查「上午各 job 最後一次 lastRunStatus」而非只看條目存在。
## [2026-10-22] 更新 (v2.9.93) — Dropbox 三卷同步 token 競態 + 記憶備份 push 撞車

### 問題描述
1. 2026-10-22 11:00 三個 Dropbox 同步 job（Volume 4 / 5 / 6）同時執行：
   - Volume 4：`RuntimeError: Dropbox token file is empty or missing`（整輪中止）
   - Volume 6：`dropbox.dropbox_client.BadInputException: OAuth2 access token or refresh token or app key/secret must be set`（中斷，積壓 57 章）
   - Volume 5：成功（贏咗競態），第五卷冇新章
2. `logs/memory-backup.log` 出現 `remote rejected main -> main (cannot lock ref 'refs/heads/main')`：三個 job 同時觸發 `backup-memory.sh`，git push 互相撞車
3. Volume 4 state 分歧：`synced_to_site=1683`，實際站點=1689

### 根因
- 四個寫 token 嘅位置（`dropbox_volume4/5/6_sync.py` + `renew_dropbox_token.py`）都用 `open(TOKEN_FILE,'w')` **非原子**寫入：truncate 與 write 之間有窗口，並發時另一進程讀到空字串 → V4 報「Token 檔案異常」、V6 報 BadInputException
- 三個同步 job 11:00 同時 push 同一個 site repo 同兩個 backup repo → non-fast-forward / cannot lock ref

### 修復
1. **原子寫入 token**：寫 tmp 檔（`.tmp.<pid>`）→ flush + fsync → `os.replace()`，四個 script 全部改；新增 `read_token()` helper（重試 5 次 × 0.4s）取代裸 `open().read()`
2. **flock 序列化**：新增 `scripts/dropbox-volume4-daily-sync.sh`（V4 原本 crontab 直接跑 python，冇 wrapper 所以加唔到鎖）；V4/V5/V6 三個 wrapper 全部加 `flock -w 900 /tmp/dropbox-sync.lock`
3. **`backup-memory.sh`**：加 `flock -w 300 /tmp/memory-backup.lock`；push 前 `git pull --rebase origin main`，失敗重試 3 次
4. crontab Volume 4 條目改用新 wrapper（合併式改動，其餘條目不動）
5. 補跑 V6 同步，把積壓章節追平；V4 state 分歧由腳本自動修復到 CH1689

### 教訓
- 所有「多進程共享嘅憑證檔」必須 tmp + `os.replace()` 原子寫入，唔好直接 `open(f,'w')`
- 同一時間跑嘅 cron job 如果共用 token / 共用 git repo，要用 flock 序列化，原子寫入只解決一半
- crontab 一律叫 wrapper script（`bash scripts/xxx.sh`），唔好直接 `python3 scripts/xxx.py`，否則加鎖、清理、備份等邏輯會漏
- 同時令多個 job 觸發同一個 git push 前，先 `git pull --rebase`（否則 remote rejected）
## [2026-10-22] 更新 (v2.9.92) - 退役 Vol4 crontab 條目 + 11:00 token 競態

### 修復內容
- system crontab 移除 dropbox-volume4-daily-sync.sh（用戶 2026-10-02 指令退役、2026-10-10 已清但條目復活）
- 起因：三個 Volume sync 同時 11:00 併發寫同一個 .token-store/dropbox-token.txt → 今日 11:00 Vol4 直接死「Token 檔案異常，中止執行 / token file is empty or missing」

### 教訓
- 同一 token 檔唔可以畀多個 job 同分鐘寫 — 併發 sync 要錯開時間或統一由一方寫 token
- 已完成卷（Vol5 CH1460）嘅每日 sync 仲喺 crontab（11:00），仲係併發寫 token 嘅第二個來源 — 待大肥喵確認是否清走
- 新章節部署後 Cloudflare 邊可能快取咗「部署前」嘅 404：直連 ?cb=1 就 200（cf-cache-status MISS）→ 對外連結加 query 或清 Cloudflare cache

---

## [2026-10-22] 更新 (v2.9.94) - Volume 6 完成 + Volume 7 接棒（每日 6 章硬上限 / 防重複）

### 事件
- **Volume 6 完成**：Dropbox 第六卷 CH1461-1740 = 280 章全上傳，站點 CH1-1740 無缺章 ✅
- **1689 → 1740 查證結論**：今日多咗 51 章（CH1690-1740）**唔係新上載**——直查 Dropbox 第六卷見 280 個 .txt、server_modified 全部 ≤ 2026-05-23，即係積壓檔案；V6 腳本被**連續執行 9 次**（每次 6 章）就推晒 51 章
- **教訓核心**：同步腳本「每次執行做一批」唔等於「每日一批」。冇跨執行累計上限，重複觸發就一日推幾十章

### Volume 7 建立
- `scripts/dropbox_volume7_sync.py`（由 V6 派生）：Dropbox `/萬古塵埃/第七卷`、起始 CH1741
- `DAILY_CHAPTER_LIMIT = 6` + `.dropbox-sync/volume7_daily_count.json`：**跨執行每日累計上限 6 章**
- **防重複**：目標章節 HTML 已存在即跳過（唔重複生成／重複上傳）
- `scripts/dropbox-volume7-daily-sync.sh` + crontab `30 11 * * *`：**11:30 錯開** V4/V5/V6 嘅 11:00，避開 token 刷新／push 競態
- push 前 `git pull --rebase`（多排程同時 push 同一 repo 必需）

### 實測
- 首次實跑 CH1741-1746 = 剛好 6 章 ✅
- 第二次實跑 → `⛔ 今日已上傳 6/6 章，達到每日上限，跳過本次`，章節數維持 1746 ✅

### 檢查清單（新增／改動同步排程必做）
- [ ] **跨執行每日上限**：唔好只靠 `CHAPTERS_PER_BATCH`，要另有 state 檔記錄當日累計
- [ ] **已存在檔案檢查**：目標 chapter-N.html 已存在就跳過
- [ ] **錯開排程時間**：唔好同其他 push 同一 repo 嘅排程同一分鐘
- [ ] **push 前 rebase**：`git pull --rebase origin main` 再 push
- [ ] **查證新章真確性**：直接 list Dropbox 睇 `server_modified` + 逐章比對正文 hash（commit message 唔可信）

---

## [2026-10-22] 更新 (v2.9.95) - 傍晚簡報日結巡檢 + 線上驗證 cache-buster 紀律

### 修復內容
- 傍晚簡報 17:55 job (f8b447b6) 執行效率規則生效：單一 exec 批次收集全部資料（curl / openclaw cron list --json / crontab -l / log tails / df / free / uptime），唔再逐項分開 call 工具
- 巡檢結果寫入 memory/2026-10-22.md + MEMORY.md，git commit + push（flock .git-push.lock + git pull --rebase）

### 教訓
- **線上章節數驗證一定要加 cache-buster**：直接 curl /assets/chapters-data.json 可能見到部署前嘅舊快取（今日 1740 vs 實際 1746），加 ?cb=<timestamp> 就係真實值；cf-cache-status: MISS 即係真實內容
- 同一個檔案本地/遠端行數唔同唔一定係「未推送」：今日 local HEAD == origin/main（8c626a883）、三倉 clean，只有 Cloudflare 邊舊快取
- **SKILL.md 三處版本可能分叉**（local 2.9.93 vs backup 2.9.94）：同步前一定要 diff，用較新嘅 backup 版做 base 合併再寫回三處，唔可以直接 cp local 覆蓋 backup（會靜靜刪走 backup 有而 local 冇嘅 v2.9.92/v2.9.94 兩節）
- 記憶檔 memory/ 已被 .gitignore，但已被 track 嘅 memory/YYYY-MM-DD.md 仍然可以 git add（要 -f 先會加新檔案，唔好亂加）

### 補記（18:00 Skill 更新檢查補課）
- SKILL.md 截斷事故：本地檔被其他 session 覆寫，10-21 區段（v2.9.83-2.9.88）消失 → 由 Second-brain HEAD~1 還原完整版（5307 行）再併入當日新條目
- cp 陷阱：cp src DIR/ 會保留原檔名（造成 skills/.../skill_merged.md 殘留檔而 SKILL.md 冇覆蓋）→ 一律用 cp src DST_FILE；同步後必核對三處行數一致
- 用戶重啟部機撞正排程時段 → 該 cron job 會記「interrupted by gateway restart」（errs+1）；處理：確認係人為重啟（無 stability crash bundle）後補跑該 job 即可，cron 不會自動回補

---

## [2026-10-23] 更新 (v2.9.96) - cron-guardian「註釋 = 缺失」自癒 + 退役卷唔好自動加返

### 事件（早上簡報 08:15 補跑巡檢）
- **08:15 部機重啟**：journal 顯示 boot -1 終止於 08:15:21（乾淨關機），boot 0 起於 09:12:41；冇任何 cron/timer 觸發。system cron `send-briefing.sh` 停喺「發送到 Telegram…」無成功行，OpenClaw job 27d54b55 記 `cron: job interrupted by gateway restart`（跑咗 3691 秒）→ 兩邊 08:15 簡報一齊中斷，09:50 補跑送出
- **V4 log 停喺 2026-10-22 11:00**：嗰次係已知 token 競態（「Token 檔案異常，中止執行」）；2026-10-22 12:59 已改用 tmp + `os.replace()` 原子寫入 + 重試讀取，手動補跑 09:53 驗證通過（state 1740→1746，未處理 0）

### 真正修復：scripts/cron-guardian.sh
1. **「被註釋 = 缺失」**：舊邏輯 `echo "$CRONTAB" | grep -q "$TASK"` 會將註釋行當成「條目存在」→ 改用 `grep -v '^[[:space:]]*#'` 先過濾註釋
2. **Dropbox 卷條目自癒**：`declare -A DROPBOX_CRON` 保留 V5/V6/V7 完整 cron 行，偵測到缺失就 append 加返（唔會洗掉其他條目）
3. **V4 明確排除**：Volume 4 已按用戶 2026-10-02 指令退役（見 v2.9.92），註釋咗嘅條目係**正確狀態**，唔可以自動加返 → 排除並加註解釋

### 教訓（重要）
- **自動修復前必須先讀 SKILL.md 確認條目係「意外遺失」定「刻意退役」**：今次見到 V4 條目被註釋，一度當成 2026-10-21 Vol5 同類事故加返條目，讀到 v2.9.92 先發現係按指令退役，即刻回滾 crontab 原狀。冇讀 Skill 就自動修復 = 可能違背用戶指令
- **部機重啟會同時打斷 system cron + OpenClaw cron 兩套機制**：gateway 用 `systemctl --user openclaw-gateway.service`（enabled）自動起返，但 cron 唔會自動回補中斷嘅 job，要人手/agent 補跑
- `journalctl --list-boots` 係查「幾點重啟過、係咪意外」最快嘅指令

### 檢查清單（新增）
- [ ] 發現 system cron 條目唔見／被註釋 → **先 grep SKILL.md 確認係退役定係遺失**先至修
- [ ] 自動加回 crontab 一律用 append（讀現有 → 檢查重複 → 加行 → `crontab -`），唔好覆蓋式寫入
- [ ] 改完 crontab 要再 `crontab -l` 核對一次（改動同驗證分開兩步）

---

## [2026-10-23] 更新 (v2.9.97) - V4 crontab 退役文件化 + 判斷教訓（承 v2.9.96 原子寫入修復）

### 內容
- Dropbox Volume 4 crontab 條目：已按 2026-10-02 退役指令保持「註釋行」狀態（唔排程，附原因註解，guardian 已明確排除 V4）
- 11:00 併發寫 token 嘅真因修復 = token 檔 tmp + os.replace() 原子寫入（v2.9.96 已驗證有效，V4 10-22 失敗 → 10-23 09:53 補跑 state 1746 exit 0 ✅）

### 教訓（重要）
- 移除/修改任何排程條目前，必須先 grep SKILL.md + memory/ 確認係「意外遺失」定「刻意退役」，再動手；今次差啲把刻意退役嘅 V4 當成「條目復活」而誤刪

---

## [2026-10-23] 更新 (v2.9.98) - Dropbox token 備份檔權限加固（.bak 664 → 600）

### 問題描述
- `scripts/renew_dropbox_token.py` 寫舊 token 備份 `.token-store/dropbox-token.txt.bak` 用 `backup.write_text()`，權限受 umask 影響實測 **664**（group/other 可讀）；主 token `dropbox-token.txt` 係 600 → 憑證備份檔變成權限漏洞兼長期遺留檔
- 每日健康報告 22:00 巡檢時發現並清理

### 根本原因
- `Path.write_text()` 唔會 chmod，新檔預設 644，被 umask 002 變 664；`save_token()` 只有 tmp 嗰行有 `os.chmod(tmp, 0o600)`，backup 嗰行漏咗

### 解決方法
1. `save_token()` 加 `os.chmod(backup, 0o600)`（已 patch，已通過 py_compile）
2. 刪走舊嘅 `.token-store/dropbox-token.txt.bak`（遺留憑證副本）
3. 實跑 `scripts/renew-dropbox-token.sh` 驗證：新 token 600、備份檔 600、Dropbox API ping 有效、exit 0

### 檢查清單（token / 憑證類檔案）
- [ ] `ls -la .token-store/` 全部檔案權限 = 600
- [ ] 冇憑證副本殘留（*.bak / *.old / *.tmp）
- [ ] 改完要實跑一次 renewal 驗證，唔好只靠 compile
- [ ] 同步 SKILL.md 落 Second-brain + Max-backup 前先 diff（避免靜靜哋覆蓋 backup 有嘅更新記錄）

---

## [2026-10-23] 更新 (v2.9.99) - 章節「下一章」連結真缺陷修復 + 檢查器 regex 修正

### 問題描述
1. **真缺陷（線上 101 頁）**：每批 6 章同步後，舊尾章嘅「下一章」連結永遠停喺 `chapters.html`（讀者撳「下一章」彈返目錄）。線上實測 chapter-1746.html 確認。
2. **工具 bug**：`check_chapter_links.py` 舊 regex `<a[^>]*href="([^"]+)"[^>]*>.*上一章.*</a>` 嘅 `.*` 會跨 `</a>` 邊界攞錯 href，加上未處理絕對 URL → 每日同步報 2354 個假錯誤，真正錯誤只有 101 個。

### 根本原因
- `fix_latest_chapter_next()` 只處理「最新一章」，舊尾章嘅 nextLink 從未被還原
- 檢查器 regex 太寬鬆（跨標籤貪婪匹配）同埋只接受相對路徑

### 解決方法
1. `fix_latest_chapter_next()` 擴充：最新一章→返回目錄 + 修復所有非最新章節嘅 nextLink（`chapters.html`/`#` → `chapter-N+1.html`）；V4/V5/V6/V7 四份同步腳本同步改
2. 新增 `scripts/fix_broken_next_links.py`（一鍵修復工具），已修 101 頁
3. `check_chapter_links.py`：改用 `id="prevLink"/"nextLink"` 精準抽 href + `normalize_link()` 正規化絕對 URL + 邊界章容許 `#`/`chapters.html`

### 驗證
- 修復後重跑檢查器：1752 章、**0 個鏈接問題**
- 單元測試：temp dir 內 chapter-1 嘅 nextLink 由 `chapters.html` 還原做 `chapter-2.html`

### 檢查清單（章節導航）
- [ ] 同步後 `python3 scripts/check_chapter_links.py` → 0 個 ❌
- [ ] 抽查上一批尾章嘅「下一章」係指向 chapter-N+1.html（唔係返回目錄）
- [ ] 線上抽查用 `?cb=` cache-buster（Cloudflare 舊快取會誤導）
- [ ] 檢查器報錯時，先分「真缺陷」同「工具 bug」再改站點

---

## [2026-10-24] 更新 — git 分歧（CI 直接 push 同一 repo）
- **症狀**：本地 `git push` 被拒「tip of your current branch is behind its remote counterpart」；origin/main 多咗 `github-actions[bot]` 嘅新聞/財務/RSS 自動更新 commit
- **根本原因**：GitHub Actions 同本地 workspace 用同一個 repo（github.com/jyonline0604/website），CI 推咗之後本地唔會自動 fetch；人手 push 前無 pull
- **解決方法**：
  1. **推送前必須 `git pull --rebase origin main`**（同步腳本 `git_commit_and_push()` 已內置，V5/V6/V7 都冇事）
  2. rebase 衝突時 DREAMS.md 一般唔會撞（CI 唔會改 DREAMS.md）
  3. 檢查完記得 `git rev-list --left-right --count HEAD...origin/main` → 應該 0 0
- **配套**：Memory Dreaming Promotion（03:00）寫 DREAMS.md 但唔 commit → repo 唔 clean；簡報巡檢要 `git status --porcelain` 順手 commit + push
- **檢查清單（git）**：
  - [ ] 每日簡報：`git status --porcelain` 三倉皆空（唔空就 commit + push）
  - [ ] 推送前先 `git pull --rebase origin main`
  - [ ] `git rev-list --left-right --count HEAD...origin/main` → 0 0

---

## [2026-10-25] 更新 (v2.9.101) — 部機重啟令 system cron 漏跑（需人手補跑）
- **症狀**：機於 **06:48:58** 關機、**09:35:18** 先開機（journal `gnome-session-shutdown.target` → `systemd-poweroff`，同 issue #10 一樣係 GNOME 桌面人手操作，唔係 cron/timer 觸發）；開機後 08:00 記憶備份、08:15 system cron 簡報、09:00 Dropbox token 續期全部漏跑
- **根本原因**：**cron 唔會自動回補**停機期間錯過嘅 job；OpenClaw scheduler 有 missed-run catch-up（08:15 job 於 09:39 補跑），但 system crontab 冇
- **解決方法**（開機後第一個 agent 回合要即刻做）：
  1. `journalctl --list-boots` 睇 boot 0 / boot -1 時間 → 對齊漏跑窗口
  2. 漏咗嘅 system cron 逐個手動補跑（記憶備份 `bash scripts/backup-memory.sh`、token 續期 `bash scripts/renew-dropbox-token.sh`）
  3. **唔好補跑 send-briefing.sh**：OpenClaw cron 簡報 job 會自己 catch-up 補送，補跑 system cron 會重覆發送兩次
  4. 補跑前先 `flock` 睇有冇另一個實例行緊（backup-memory.sh / renew-dropbox-token.sh 本身已有 flock）
- **檢查清單（開機後巡檢）**：
  - [ ] `who -b` / `journalctl --list-boots` → 確認最後一次開機時間同而家相差幾多
  - [ ] `systemctl --failed` → 重啟後 failed unit 通常清零（apport/logrotate 只喺 AC 供電時 fail）
  - [ ] 逐一核對漏跑窗口內嘅 system cron（08:00 備份 / 09:00 token / 10:00 財經 / 11:00 同步）
  - [ ] 補跑 token 續期：確認 `.token-store/dropbox-token.txt` 權限仍然 600
  - [ ] 三倉 `git rev-list --left-right --count origin/main...HEAD` → 0 0

---
## [2026-10-25] 更新 - 版本檢查 Telegram 通知路徑修復（cron 環境冇 env token）

### 修復內容
- check-openclaw-version.sh 嘅 Telegram 通知改用 openclaw message send CLI（同 send-briefing.sh 一致，憑證由 OpenClaw config 處理），curl + env token 保留作後備
- 根因：cron 環境從來冇 TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID → 舊 curl 路徑由安裝以來一次都冇成功發出過，版本通知一直要靠人手轉發
- 實測：修復後 2026.10.6 -> 2026.10.7 通知成功送出 Telegram

### 教訓
- cron / system 環境跑嘅腳本唔可以假設有互動式 shell 嘅 env 變數；要用 openclaw CLI 或明確由檔案讀 token


---
## [2026-10-25] 更新 - 版本檢查 .py 報錯版本 + 升級建議修正

### 修復內容
- check_openclaw_update.py 嘅 PATH 由舊 ~/.npm-global/bin 改為 nvm node24：之前讀到孤兒安裝（2026.9.5），每日 11:00 系統 cron 記錄嘅「當前版本」係錯的（實際 2026.10.5）
- 升級建議由「npm update -g openclaw」改為「openclaw update（唔好用裸 npm i -g openclaw，會靜靜裝舊版）」；update_openclaw.sh 同步修正（未被 crontab 使用，但保留作人手更新用）

### 教訓
- 同一類「孤兒 ~/.npm-global PATH」問題已出現 5 次（check-openclaw-version.sh v2.9.78、send-briefing.sh v2.9.79、cron-guardian.sh v2.9.82、check_openclaw_update.py v2.9.102、update_openclaw.sh v2.9.102）→ 升級/搬遷後要全局 grep 一次舊路徑
- 版本檢查腳本要報「gateway 實際運行」嘅版本，唔係 PATH 撞到嘅第一個 openclaw


---

## [2026-10-25] 更新 (v2.9.104) - skill 版本號 bump 教訓（附帶修正）

### 事項
- 我用「逐段 +1」做版本 bump，令 2.9.101 錯變 3.10.102（兩倉同步後即察覺並改正為 2.9.102）
- 正確做法：只 bump 最後一段（patch），major/minor 保持不變

### 教訓
- 版本號必須逐段核對再寫入，唔好用程式逐段 +1（2.9.101 -> 3.10.102 破壞語意化版本）；寫入後要核對本地 + 兩備份倉三處版本一致

---

## [2026-10-26] 更新 (v2.9.105) - 開機後 git 分歧自癒 + chapter state「假分歧」判定法

### 事項
- **開機後 git 分歧**：部機重啟（07:53 起機）後 workspace 落後 origin/main 2 個 commit（GitHub Actions CI 推嘅新聞/財務更新），同時 DREAMS.md 有 Memory Dreaming Promotion (03:00) 未提交改動 → `git pull --rebase` 因 unstaged changes 被拒
- **修復**：先 `git add DREAMS.md && git commit`，再 `git pull --rebase origin main`，最後 `git push` → 三倉（workspace / Second-brain / Max-backup）全部 0/0

### 教訓
- **`git pull --rebase` 一定要先 commit 或 stash**：有 unstaged changes 會直接報 `cannot pull with rebase`，唔會自動幫你處理
- **chapter state「假分歧」**：站上 1764 章，但 V3/V6 state 嘅 `processed` 缺少 790-795 / 1467-1468 / 1499-1503（13 章）。呢啲章係**手動加落站**（git log 見 `feat: Add chapters 1467-1472 from Dropbox Volume 6`），state 冇記錄，但同步腳本有 `f['ch_num'] not in existing` 防護（existing = 本地 chapter-*.html 檔名）→ **唔會重複下載、唔會覆蓋** → 唔需要修
- **判定 state 分歧嘅正確方法**：唔好淨係比對 processed 數量，要比對 **(a) site 線上 chapters-data.json 章號集合** vs **(b) 各卷 state 章號集合**，再睇 **本地 chapter-*.html 實際存在嘅檔案**。同步腳本 guard 係睇本地檔案，唔係睇 state
- **Cloudflare 快取唔會令站點壞**：`?v=YYYYMMDD` 參數令 chapters-data.json 每次都係 fresh（cf-cache-status HIT 但 age=0）；裸路徑 `/assets/chapters-data.json` 可能係舊快取（age=327759s），但頁面 JS 一律帶 `?v=` → 唔影響用戶
- **service-worker.js 對 JSON 用 Cache First**：`/assets/chapters-data.json` 喺 staticUrls 內，舊 SW cache 會持有舊 JSON；頁面用 `?v=` 參數令 URL 不同 → SW match 唔中 → 自動取新，無實害

---

---

## [2026-10-28] 更新 - 卡住 rebase + Detached HEAD 自動修復

### 修復內容
- 症狀：本地 finance-data commit（16:00 HKT）撞 GitHub Actions 同日更新（12:55 UTC）→ rebase 衝突 UU finance-data.json + Detached HEAD
- 修復：git rebase --abort → git reset --hard origin/main（遠端更新更晚，丟棄過時本地 commit 無資料損失）→ scripts/git-health-check.sh --fix
- 驗證：git 狀態健康、工作區乾淨、未推送 0

### 教訓
- 同一個自動生成資料檔（finance-data.json）被本地 cron 同 GitHub Actions 同時改 → 必然衝突；衝突時以較新嘅遠端為準 reset --hard
- 心跳 09:00 Git 健康檢查係呢類卡死嘅第一道防線（發現即自動修復 + 通知）

---

## [2026-10-28] 更新 (v2.9.107) - 三份 SKILL.md 版本分叉自癒 + 早報 git 分歧自癒

### 修復內容
- **三份 SKILL.md 版本分叉**：local v2.9.95（5349 行）vs Second-brain / Max-backup v2.9.106（5534 行，兩份一致）→ local 缺失 v2.9.96-2.9.106 共 185 行（cron-guardian 自癒、Volume 7 建立、開機後巡檢等條目全部唔喺 local）→ 以 backup 版（較新且係 local 超集）覆寫 local → bump 至 v2.9.107 → 三份 5534 行 + 逐行 diff 一致
- **website repo git 分歧**：本地落後 origin/main 1 個 CI commit（2026-10-27 18:30 UTC 新聞/財務/RSS 更新）+ DREAMS.md 未提交（03:00 Memory Dreaming Promotion 寫入）→ 先 commit DREAMS.md → `git pull --rebase origin main` → push 成功（c1f29671e..5c54ea5e8），三倉 0/0
- **backup 倉明文 MEMORY.md 過期**：Second-brain / Max-backup 嘅 MEMORY.md 停留 2026-10-22，本地已於 10-26 重寫為精簡版（31KB）→ 用 live 本地版覆寫兩份明文副本 + 補齊 memory/ 日誌檔，舊版由 backup 倉 git history 保留

### 教訓
- **三份 SKILL.md 同步前一定要 diff + 對行數**：單向 cp 會靜靜丟走另一方嘅更新區段（呢次 local 就係少咗 185 行）；覆寫方向固定係「較新嗰份 → 較舊嗰份」，因為較新嗰份係超集
- **backup 倉明文 MEMORY.md 唔會跟 daily backup script 更新**：`backup-memory.sh` 只做加密 tarball（MEMORY.md + memory/*.md 打包再 encrypt，08:00 / 20:00 兩次），明文副本只喺人手 cp 時更新 → 明文副本會靜靜過期，但唔代表備份失效，唔好因此重跑或重建 tarball
- **git pull --rebase 前一定先 commit / stash**：有 unstaged changes 會被直接拒絕（2026-10-24、10-26、10-28 連續三次驗證同一件事）
- **判定線上章節數一定要加 cache-buster**：裸路徑 `/assets/chapters-data.json` 有 Cloudflare 舊快取，加 `?cb=<ts>` 先係真實值（今日線上 1776 = 本地 chapters-data.json 1776 = 本地 chapter-*.html 1776 檔 + template）
- **volume state 合計數 ≠ 線上章節數係正常**：今日 V2-V7 state 合計 1263 章，線上 1776 章，差額係 CH1-500 早期章 + 手動加落站嘅章節（同步腳本 guard 以本地 chapter-*.html 檔名為準，唔會重複下載），唔好當成 state 分歧去修
## [2026-10-28] 更新 - chat-worker 依賴目錄入 .gitignore + chapter-titles 章數修正

### 修復內容（隔離 session 執行，小肥喵補記 skill 日誌）
- .gitignore 補 node_modules/（原本缺失，150M 未追蹤依賴目錄）；補交 package-lock.json
- chat-worker assets/chapter-titles.json 由 1776 章修正至 1782 章（對齊 assets/chapters-data.json 零分歧）
- commit 399645001 已 push（origin/main、Second-brain、Max-backup 均 0 未推送）

### 教訓
- Node 依賴目錄必須入 .gitignore，否則未追蹤依賴會令 push/clone 體積失控
- 章節標題索引（chapter-titles.json）同主索引（chapters-data.json）要同批更新，否則網站前端會少 6 章

---
## [2026-10-28] 更新 (v2.9.108) - chat-worker CI 結構性 bug 修復 + OpenRouter free 模型退役

### 修復內容
- **chat-worker 索引永久凍結（結構性根因）**：原本 `部署 Chat Worker` 一旦失敗，GitHub 自動 skip 後面「提交索引」步驟 → worker 索引停喺 CH1776，而站點已 CH1782，兩者永久失同步；而且原本用 `git diff` 判斷「需唔需要部署」，索引一提交就永遠回 false，**即使部署失敗都唔會再部署**。改用 SHA-256 hash 對比 `.deployed-index-hash` marker 檔（部署成功先更新 marker），失敗就下次 run 自動重試。
- **deploy 步驤加韌性**：`continue-on-error: true` ＋ 3 次重試（每次間隔 30 秒）＋ 提交索引步驤加 `if: always()`；Cloudflare 端回 `10500 internal server error` 屬暫時性錯誤，重試即成功。
- **marker 二次 bug（自己引入）**：`git add .deployed-index-hash` 後，commit 只喺「索引有變更」時先做 → marker 永遠 commit 唔到 → 下次 run 又當作需要部署而無謂重複部署。修正為「有任何 staged 改動就 commit」。
- **實測驗證**：run #447 / #448 全綠（16 個 step 全部 success）；線上 `GET /api/status` → `{"ok":true,"chapters":1782}`，chat API 正常答出 CH1781「若曦之道」／CH1782「並肩而行」；marker hash 與 index hash 一致。
- **OpenRouter free 模型退役**：fallback 鏈第一棒 `openrouter/minimax/minimax-m3.1-flash:free` 已於 2026-10-22 結束 free 試用期並被 OpenRouter 移除（API 回 404）→ 成條 fallback 鏈第一棒係死鏈。實測 16 隻現存 `:free` 模型後改用：`nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` → `cohere/north-mini-code:free` → `nvidia/nemotron-3-ultra-550b-a55b:free` → `poolside/laguna-s-2.1:free` → `recursive/flint-v1.0:free`。config（defaults + entries.main modelPolicy.allow）、6 個 cron job 嘅 fallback override、cron-guardian.sh 全部同步更換，`cron_model_guard.py` 驗證通過。

### 教訓
- **「提交索引」步驟一定要 `if: always()`**：部署一死，後續步驟會被 GitHub 自動 skip，令「部署失敗」變成「索引凍結」嘅隱性永久故障。
- **自己 commit 落 git 嘅部署產物唔可以用 `git diff` 做變更偵測**：用 hash marker（部署成功先更新），否則提交一次之後永遠唔會再部署。
- **marker 檔本身都要有 commit 路徑**：`git add` 完唔 commit 等於冇 add；commit 條件要睇「有冇 staged 改動」而唔係「某個特定檔案有冇變」。
- **fallback 鏈嘅第一棒會靜靜死掉**：OpenRouter free 試用期會結束（2026-10-22 minimax-m3.1-flash 就係），`/api/v1/models` catalog 要定期核對，唔好淨係信舊 config。
- **實測模型可用性要用真 chat/completions 實測**，唔好淨係睇 catalog 存在：`/api/v1/models` 有唔代表 call 到（`liquid/lfm-2.5-2.6b:free` 429、`thinkingmachines/inkling:free` 403 只准 agentic harness）。
- **2026-10-26 pages 部署失敗係 GitHub 側暫時性 OIDC 問題**（`Failed to get ID Token: Request timeout`），之後連續 20+ 次 pages run 全綠 → 唔使改 workflow。

---
## [2026-10-29] 更新 (v2.9.109) - logrotate duplicate log entry 復發 + 每日 state 零分歧基線

### 修復內容
- **logrotate.service 復發 failed（issue #7）**：`/etc/logrotate.d/cloud-init` 同 `/etc/logrotate.d/cloud-init-base` 內容一模一樣（各 144 bytes），logrotate 見到 `duplicate log entry for /var/log/cloud-init.log` 就 skip 個檔 exit 1。2026-10-29 00:04 機器接上 AC 電 → ConditionACPower=true 終於滿足 → logrotate 真係啟動 → 又 fail（2026-10-25～10-28 每日 journal 都係「skipped, unmet condition」所以睇落似正常）。unattended cron session 冇 sudo 密碼（`sudo -n true` 被拒：interactive authentication is required），無法自動修復 → 只能記錄 + 俾大肥喵人手指令。

### 教訓
- **ConditionACPower=true = 間歇性失敗嘅源頭**：logrotate 只喺桌面接 AC 電時先會行，journal 顯示「skipped, unmet condition」唔代表健康 → 巡檢 logrotate 要睇 `systemctl --failed`，唔係睇 journal 有冇 skip。
- **duplicate log entry 唯一修法**：root 移走重複檔（`sudo mv /etc/logrotate.d/cloud-init-base /etc/logrotate.d/cloud-init-base.disabled`）→ `sudo logrotate -d /etc/logrotate.conf | grep -i error` 驗證 → `sudo systemctl reset-failed logrotate.service` 清 failed 標記。
- **每日簡報 state 零分歧基線（2026-10-29 實測）**：線上 `/assets/chapters-data.json`（加 `?v=YYYYMMDD` cache-buster）1782 章 = 本地 `chapter-*.html` **數字檔** 1782 = V7 state max CH1782。計本地檔時要用 `ls chapter-*.html | grep -cE '^chapter-[0-9]+\.html$'`——`chapter-template.html` 唔匹配數字檔名，唔好計入（否則會差 1 誤報分歧）。
- **Volume 4 唔算故障**：按 2026-10-02 指令退役（crontab 註釋 + cron-guardian 明文排除），最後實跑 2026-10-22 11:00 因 token 競態中止 → 簡報只作記錄，**唔好自動加返條目**（見 issue #8 教訓）。


---

## 2026-10-30 更新
- 自動修復（git 分歧第 4 次同型）：DREAMS.md 未提交 + CI commit 同時撞埋 → 必須先 commit DREAMS.md，再 `git pull --rebase origin main`，最後 push；巡檢時用 `git fetch` + `log HEAD..origin/main` 睇分歧。
- 線上一致性判定加硬規則：Cloudflare 裸路徑 `/assets/chapters-data.json` 會有舊快取（age 過日），必須加 `?v=YYYYMMDD`（或隨機 query）再 curl，否則會誤報「線上少章」嘅假分歧（issues #14）。
- Volume 4 維持退役（2026-10-02 指令）：crontab 註釋 + cron-guardian 明文排除；2026-10-22 最後一次實跑因 token 競態中止，唔算故障，只作記錄。

---

## 2026-10-30 更新 - 章節索引 cache-buster 每小時 key（Hourly Cache-Buster）（assets/chapters-data.json）用戶端最長 24 小時見唔到新章（今日線上索引只列到 CH1788，線上源已到 CH1794）
- 根本原因：chapters.html / index.html / home.html 用 `?v=YYYYMMDD` 日級 cache-buster，Cloudflare edge 同 Service Worker（cache-first）各自快取同一個 key，要等 UTC 換日先失效
- 解決方法：cache-buster 改為每小時一個 key（`?v=YYYYMMDDHH`，slice(0,13).replace(/[-:T]/g,'')），滯後由 ~24h 降至 ≤1h；已 commit + push
- 檢查重點：裸路徑 /assets/chapters-data.json 可能係 Cloudflare 舊快取（假分歧），要同時驗 `?v=<當前小時key>`；/api/status 反映線上源真實章節數

---

---

## 2026-10-30 更新 - 健康檢查診斷法修正（空 redirect log ≠ 腳本冇行）+ logrotate 重複條目
- 修復內容：更正 10-29 / 10-30 健康報告中「system cron send-briefing.sh（08:15/17:55）+ check_openclaw_update.py（11:00）實際冇執行過」嘅誤判；同時定位 logrotate.service 持續 failed 嘅根因
- 根本原因（診斷法錯咗）：判定 system cron 有冇行，**唔可以只睇 crontab redirect 目標 log**。send-briefing.sh 內部用自己嘅 `LOG_FILE=logs/briefing-send.log`、check_openclaw_update.py 用 `logs/openclaw-update.log`，stdout 冇輸出 → `logs/briefing-morning.log` / `briefing-evening.log` / `openclaw-check.log` 永遠 0 bytes，但腳本其實每次都有跑（syslog 有 CRON 行、送達有 Msg ID）
  - 正確判定三路對照：① `grep CRON /var/log/syslog`（有冇 spawn）② 腳本內部 LOG_FILE（跑成唔成）③ 實際送達紀錄（Msg ID / ✅ 行）
  - 今日實測：10-30 08:15:01 / 11:00:01 / 17:55:01 三條 CRON 行齊全；17:55 簡報生成 1031 字符、送達成功（Msg 23362）；11:00 版本檢查寫入 openclaw-update.log（偵測到 2026.10.9 可更新）
- 解決方法：已寫入 MEMORY.md 教訓清單 #31；health 檢查以後必查 syslog CRON 行，唔再單靠 redirect log 空檔判斷
- 附帶根因（logrotate.service failed）：`/etc/logrotate.d/cloud-init-base` 同 `/etc/logrotate.d/cloud-init` 內容完全重複（都係 `/var/log/cloud-init*.log`，Jul 24 cloud-init 升級多出）→ logrotate "duplicate log entry" exit 1 → systemd failed
  - 修復需 root：`sudo rm /etc/logrotate.d/cloud-init-base && sudo systemctl reset-failed logrotate`（兩檔 root 擁有，無人值守 session 嘅 sudo 需要互動密碼 → 留待大肥喵手動執行）
  - 影響輕微：只影響 /var/log 系統日誌輪轉；workspace logs（44M）唔受影響
- 檢查重點：Dropbox Volume 4 同步已退役（大肥喵 2026-10-02 指令，synced_to_site=1746、batch 44），crontab 註釋明寫「勿啟用，勿由 guardian 加返」→ 任何自動修復都**唔可以**加返 V4 條目

---
## [2026-10-30] 更新 - cron 條目判定陷阱（redirect log 空 ≠ 未執行）

### 教訓（三路對照，缺一不可）
- 判定 system cron 條目有冇執行，必須三路對照：(1) syslog CRON 行（含 /var/log/syslog.1，rotation 會令早段行唔喺當前檔）(2) 腳本內部 LOG_FILE 嘅發送記錄 (3) openclaw cron list + crontab -l
- **redirect 目標 log 空 ≠ 腳本冇行**：send-briefing.sh / check_openclaw_update.py 自己寫 LOG_FILE，crontab 的 >> 重定向檔自然空 —— 我 10-30 13:10 因此誤判「三條條目死咗、冇後備」，仲差啲叫大肥喵移除重建
- **雙軌並存 = 每日兩份簡報**：system crontab 腳本版（每日兩次「發送任務完成」）+ OpenClaw cron agent 版（較詳細）—— 報告一份嘅講法只係針對其中一軌
- 判斷要睇「實際投遞幾多次」，唔係睇 log 有幾多行

### 處理
- A/B 選項（重建 vs 移除 crontab 條目）作廢：後備機制正常，唔好動 crontab

---

## [2026-10-31] 更新 - 重啟後復原巡檢 + 每日雙軌簡報確認（已知設計，待大肥喵決定）

### 檢查內容
- 主機 2026-10-31 07:55:37 重啟（uptime 由 4 日 14 小時 → 20 分鐘）後第一次簡報巡檢：cron.service 07:55:37 啟動 → 08:00 記憶備份、08:15 system cron 簡報（Msg 23365）都有 syslog 執行記錄；OpenClaw cron 8 個 job 全部 enabled + lastStatus=ok + consecutiveErrors=0

### 發現（已知設計，唔算 bug）
- 每日簡報雙軌並存：system cron send-briefing.sh（08:15 / 17:55）同 OpenClaw cron agent job（早上簡報 08:15 / 傍晚簡報 17:55）都會送達 → 大肥喵每日收 2 份（今日 08:15：Msg 23365 + agent 版）
  - 唔可以用 shell dedup 解決：system cron 08:15:07 先送，agent 報告約 08:19 先到（去重方向相反）
  - 真正去重必須揀一套：保留 system cron 做後備（移除 OpenClaw 簡報 job）或者只留 OpenClaw cron（移除 crontab 兩條）— 屬大肥喵決定，guardian 唔會自動改

### 附帶確認
- Dropbox 零分歧：本地 chapters-data.json 1794 章 = V7 state synced_to_site max 1794；V4 仍退役（state 1746 / batch 44，唔加返）
- logrotate 重複條目仍在（/etc/logrotate.d/cloud-init-base vs cloud-init）：重啟後 systemctl --failed 只剩 apport-autoreport.service（無關），但下次輪轉仍會 duplicate log entry fail → 需 root：sudo rm /etc/logrotate.d/cloud-init-base && sudo systemctl reset-failed logrotate（unattended session 冇 sudo 密碼）

### 教訓
- 開機 / 重啟後第一次巡檢要加驗三路：cron.service 啟動時間 + syslog CRON 行（記憶備份 08:00、簡報 08:15）+ OpenClaw cron job 狀態
- 每日簡報雙軌係「已知設計」，報告時要講明兩軌都正常，唔好誤判成重複 bug 自己亂改 crontab

---
## [2026-10-31] 更新 (v2.9.115) - 升級後殘留舊 nvm install 令版本檢查報錯版本

### 修復內容
- **症狀**：2026-10-31 大肥喵 12:40 已 `/update` 升級到 OpenClaw 2026.10.9 (8b18b55)，但 11:00 版本檢查 Telegram 通知同中午簡報仍然報「當前版本 2026.10.5 → 最新 2026.10.9，有更新」→ 假警報。
- **根因**：升級會安裝到**新嘅 nvm node 目錄**（v24.22.2 = OpenClaw 2026.10.9），但**舊 install 唔會自動移除**（v24.21.0 = OpenClaw 2026.10.5 仍然喺磁碟）。5 個 workspace 腳本硬編碼 `export PATH="/home/openclaw/.nvm/versions/node/v24.21.0/bin:..."` → 讀到嘅永遠係舊 CLI。gateway 自己（systemd ExecStart + tmp/agent-cli wrapper）已經用新版本，所以只有「腳本報版本」會錯，實際運作冇問題。
- **修復**：5 個腳本（`check-openclaw-version.sh`、`check_openclaw_update.py`、`update_openclaw.sh`、`send-briefing.sh`、`cron-guardian.sh`）改成**動態解析** —— 列出 `~/.nvm/versions/node/v*//` 用 `sort -V -r` 由新到舊，揀第一個有 `bin/openclaw` 嘅目錄，fallback v24.22.2。以後升級唔使再改腳本。
- **驗證**：`env -i bash scripts/check-openclaw-version.sh`（清空環境變數）→ 報 `OpenClaw 2026.10.9 (8b18b55)` + `✅ 版本已是最新`；commit `482c05db4` 已 push。
- **順帶確認**：`agents.defaults.models` 已乾淨（無退役 `:free` 模型殘留、5 隻新 free 模型齊全）、fallback 鏈 5 隻全部實測 chat/completions 可用；systemd unit 嘅 `.reconcile-*.bak` 備份檔內 v24.21.0 引用只係備份檔，唔生效。

### 教訓
- **升級後唔好淨係睇 `/status`**：要三方對照 —— (1) gateway 實際進程用邊個 node（`ps -eo pid,args | grep openclaw`）、(2) systemd unit 嘅 ExecStart / PATH、(3) workspace 腳本有冇硬編碼舊 nvm 路徑。三者唔一致就會出現「gateway 已更新但腳本報舊版」。
- **nvm 裝多版本 = 孤兒 install 會留低**：`nvm install` 唔會自動清舊版本，目錄仲喺度就仲行到舊 CLI。所有腳本引用 nvm node 路徑都應該動態解析，唔好硬編碼版本號。
- **`sort -V -r` 揀 node 目錄一定要加存在性檢查**（`-x bin/openclaw`），因為可能有更新嘅 node 目錄但未裝 openclaw。
- **報「有新版」之前要核對 gateway 進程版本**，唔好照抄腳本輸出 —— 假版本警報會消耗大肥喵對自動通知嘅信任。

---

## [2026-10-31] 更新 (v2.9.116) - logrotate 長期失敗修復（duplicate entry + ConditionACPower）

### 修復內容
- **症狀**：`systemctl --failed` 長期有 failed unit；journal 顯示 logrotate 每日失敗或被 skip。
- **根因 1（duplicate entry）**：`/etc/logrotate.d/cloud-init` 同 `cloud-init-base` 兩個檔案內容完全相同（都係 `/var/log/cloud-init*.log`），但係由**兩個唔同 dpkg 套件**擁有（`cloud-init` 同 `cloud-init-base`，26.1-0ubuntu3~26.04.1）→ logrotate 報 `duplicate log entry for /var/log/cloud-init.log`，整個 config 讀取中斷 → **其它所有 log 都唔輪轉**。
- **根因 2（ConditionACPower）**：Ubuntu 預設 `logrotate.service` 有 `ConditionACPower=true`，部機以電池供電（ADP1 online=0）→ 每日 timer 觸發都被 skip（journal 大量 "skipped, unmet condition check"）。
- **修復 1（duplicate）**：**唔可以直接 `rm`**（兩個檔案都係 dpkg 擁有，rm 會令 dpkg 檔案清單不一致 + 套件更新時復原）。正確做法係 `dpkg-divert --local --rename --add --divert /root/cloud-init-base.logrotate.disabled /etc/logrotate.d/cloud-init-base` → 檔案移出 include 目錄，dpkg 記錄 diversion，`dpkg -V` 乾淨、套件更新唔會復原。**注意**：單純 `dpkg-divert --rename` 改名做 `.distrib` 唔夠 —— logrotate 只 skip 副檔名以 `~` 開頭/結尾嘅，`.distrib` 照樣會被讀取 → duplicate 仍在，必須 divert 去 include 目錄外。
- **修復 2（ACPower）**：建立 drop-in `/etc/systemd/system/logrotate.service.d/override.conf` 寫 `[Unit] ConditionACPower=`（空值 = 取消條件），原 unit 檔案完全不動（可逆、唔會被套件更新覆蓋），跟 `systemctl daemon-reload`。
- **驗證**：`/usr/sbin/logrotate -d /etc/logrotate.conf` exit=0（之前 exit=1）；`systemctl start logrotate.service` → `status=0/SUCCESS`（之前 skipped/failed）；`systemctl --failed` = 0。

### 教訓
- **logrotate 工具唔喺預設 PATH**：`logrotate` 實際路徑係 `/usr/sbin/logrotate`，exec 環境冇 `/usr/sbin` 會出現 "command not found" → 之前用 `logrotate -d` 驗證時錯誤被 grep 食咗，睇落好似「冇 duplicate」。驗證 logrotate 一定要用 `/usr/sbin/logrotate` 或 `sudo`。
- **duplicate log entry 會令成個 config 讀取中斷**，唔止影響嗰個檔案 —— 一個重複條目就令所有 log 唔輪轉，要當 P1 睇。
- **dpkg 擁有嘅設定檔唔好用 rm**：用 `dpkg-divert --local --rename --add --divert <目錄外位置>` 保持 dpkg 一致性，並用 `dpkg -V <pkg>` 驗證。
- **systemd Condition 可以用 drop-in 清空**：`[Unit] ConditionXxx=` 空值即取消，比直接改 `/usr/lib/systemd/system` 嘅 unit 檔安全（唔會被更新覆蓋、隨時刪 drop-in 復原）。
- **24x7 服務機唔應該因為「插電定放電」而唔做日誌輪轉**。

---

## [2026-11-01] 更新 (v2.9.117) - 清理 ignored 殘留必須用 git clean -fdX（唔可以用 rm -rf）

### 修復內容
- **症狀**：每日健康報告清理 media/inbound 嘅 openclaw-staged-* 殘留時，用 find -mtime +7 -exec rm -rf {} +，結果 git status 出現 4 個 D（deleted）—— 呢 4 張 jpg 其實已被 git 追蹤（網站圖片），唔係純 ignored 殘留。
- **根因**：media/inbound/openclaw-staged-*/ 入面每個目錄都有自己嘅 .gitignore（忽略目錄內容），但已經被 commit 過嘅圖片檔本身係 tracked；用 rm -rf 唔會理會 tracked / ignored 之分 → 直接刪走 tracked 檔。
- **解決方法**：
  1. 即時 git checkout -- media/inbound/ 還原 4 個 tracked 檔（驗證：git status 乾淨 + git ls-files media/inbound 全部存在於 disk）。
  2. 之後改用 git clean -fdX <path> 清理 —— -X = 只刪 ignored 檔案，tracked 檔案永遠唔會郁。
  3. 清理前先用 git clean -ndX <path> dry-run 睇清楚會刪咩。
- **驗證**：清理後 media/inbound 由 2.1M 降到 220K，4 個 tracked 圖片全部在 disk，git status --porcelain 空、git status -sb = main...origin/main。

### 教訓
- **「gitignore 咗」≠「可以 rm」**：一個目錄入面嘅檔案可能一部分 ignored、一部分 tracked，清理前必須分清。
- **清理前先 dry-run**：git clean -ndX <path> 唔會真刪，但會列出所有會被移除嘅檔案 —— 見到有 tracked 內容就停手。
- **tracked 檔被誤刪唔好 commit 落去**：即刻 git checkout -- <path> 還原，確認 git status 乾淨先繼續。
- **主機重啟後要主動補跑漏咗嘅 system cron**：停機期間嘅記憶備份 20:00、自動記憶 23:00、cron-guardian 21:30、健康報告 22:00 會靜靜漏跑，開機後要人手/健康報告補做（記憶備份可手動跑 scripts/backup-memory.sh）。

---

## [2026-11-01] 更新 — v2.9.118
- 修復內容：website repo push non-fast-forward 導致簡報/健康 job 推送失敗
- 根本原因：同一個 website repo 由多個 cron job（bus ETA 數據、財經、AQHI、簡報記憶）同時寫入，本機未 fetch 就 push 會被 remote 進度擋住
- 解決方法：push 前必須 git fetch origin，再檢查 git log HEAD..origin/main，有 behind 就 git pull --rebase origin main，然後再 push
- 附加教訓：workspace memory/ 目錄被 .gitignore 忽略，記憶備份要靠 scripts/backup-memory.sh（Second-brain + Max-backup）或手動 cp，唔會自動進 website repo

---

## [2026-11-01] 更新 (v2.9.119) - 退休 system cron 簡報軌（雙軌簡報 → 單軌）

### 修復內容
- **問題**：每日早上/傍晚各送兩次簡報 —— system cron（`scripts/send-briefing.sh` 08:15/17:55，用 `openclaw message send` 直接送 Telegram）同 OpenClaw cron agent 版（08:15/12:55/17:55，agent 產出報告）。
- **關鍵發現（唔係重複而係互補）**：system cron 版送嘅係「📰 香港簡報」digest（天氣/天氣警告/預報/展望/特別交通消息/港鐵列車到站/娛樂/科技/財經，實測 978 字、6 秒），agent 版送嘅係系統狀態報告（網站/Dropbox/cron/git/自動修復）。**兩者內容唔重疊**，所以唔可以直接刪 system cron 而唔補內容。
- **修復（退休 system cron 軌 + digest 併入 agent 版）**：
  1. `crontab`：`send-briefing.sh` 兩條（08:15 / 17:55）**註釋**（保留原行 + 「勿啟用、勿由 guardian 加返」註記，照 Volume 4 退役做法）
  2. `scripts/cron-guardian.sh` `SYSTEM_TASKS` **移除** `send-briefing.sh` —— 唔移除會被 guardian 自動加返（Volume 4 就係咁中招）
  3. 4 個 OpenClaw cron job message 更新（早上 08:15 / 中午 12:55 / 傍晚 17:55 — 日結 / 每日健康報告 22:00）：早上同傍晚加入 digest 步驟（1 次 exec 跑 `generate-briefing-full-v5.py`，stdout 原樣貼報告最前；超 3600 字就只留 5 段），4 個都移除「簡報 08:15/17:55 係 system cron」嘅 system cron 清單描述 + 加「已退休，唔好再報告雙軌簡報問題」註記
  4. guardian 嘅 4 個 heredoc 同步換成同一份 message（避免 guardian 重建 job 時回退舊 prompt）
  5. `scripts/send-briefing.sh` 保留但標記退役（可還原）
- **驗證**：手動實跑 `cron-guardian.sh` → **冇加返** `send-briefing.sh`（crontab active 行 = 0）；4 個 job message 確認 digest 步驟在位、反引號無多餘反斜杠、已退役註記在位。
- **效果**：每個時段得一條訊息，內容 = 天氣 digest + 系統狀態報告（合共）。

### 教訓
- **「雙軌」唔一定係重複**：退休前一定要先比對兩軌實際內容（用 `cron list --json` 抽 `payload.message` + 實跑生成器睇輸出），否則會漏咗其中一軌嘅獨有內容。呢次 system cron 版嘅天氣 digest 就係 agent 版冇嘅。
- **退役一個 system cron 條目要改三個地方**：crontab（註釋）、guardian `SYSTEM_TASKS`（移除，否則自動加返）、guardian 嘅 rebuild heredoc（同步，否則重建時回退）。漏咗第二項 = 條目復活；漏咗第三項 = prompt 內容回退。
- **改 cron job message 要用 `openclaw cron edit <id> --message "$(cat file)"`**，同時要同步 guardian heredoc（兩份 source of truth）。
- **退休嘅任務唔好由 agent 繼續當成「已知問題」報告**：要喺新 message 內加一句「已退役，唔好再報告」，否則簡報會每日繼續叫人做同一個決定。
- **Python heredoc 寫入含反引號嘅字串要小心 escape**：用 `\`` 會喺輸出留低反斜杠（SyntaxWarning: invalid escape sequence），寫入檔案後要 grep 一次 `cat -A` 核對。

---

## [2026-11-02] 更新 (v2.9.120) - 早上簡報全綠 + issue #7（logrotate duplicate）結案

### 修復內容
- **DREAMS.md 未提交**：03:00 Memory Dreaming Promotion 每日寫入 DREAMS.md，但網站 repo 一直留低 1 個 unstaged 檔案 → 每日早上簡報 commit + `git pull --rebase origin main` + push origin/main，三倉 0/0。
- **issue #7 結案**：`/etc/logrotate.d/cloud-init-base`（duplicate log entry 根因檔）已經唔存在，`systemctl --failed` = 0 failed units → 之前連續多日「logrotate failed」係真·已修好，唔使再等大肥喵人手做 `sudo mv`。
- **SKILL.md 同步**：local + website repo（force-add）+ Second-brain + Max-backup 四份 v2.9.120 md5 一致。

### 巡檢要點（2026-11-02 驗證有效）
- **線上一致性一定要加 cache-buster**：`assets/chapters-data.json?v=YYYYMMDD` 先至係用戶見到嘅版本；裸路徑係 Cloudflare 舊快取（issue #14）。
- **Dropbox V4 保持退役**（勿加返）：V5/V6/V7 三條 11:00/11:00/11:30 就夠；V7 已接棒到 CH1806，線上 = 本地 = state = 1806 零分歧。
- **早簡報 digest 併入 agent 版**（2026-11-01 起）：單一 exec 跑 `generate-briefing-full-v5.py` 攞 stdout 就夠，唔使再跑已退休嘅 `send-briefing.sh`，亦唔好再報「雙軌簡報」。
- **system cron 檢查用 `crontab -l` + `openclaw cron list --json`（exec 執行）**，唔好用 cron tool（isolated session scoping 會令其他 job 唔見）。

### 教訓
- **每日 03:00 dreaming 產出要納入早上簡報嘅自動修復流程**：唔好等到 human 發現，先 commit（+ rebase + push）就係最平成本的修法。
- **睇 systemctl --failed 之後要再睇根因檔案**：logrotate 有 ConditionACPower=true，「skipped」唔等於健康；duplicate 檔真係唔存在，先可以結案。

---

## [2026-11-04] 更新 (v2.9.121) - 早上簡報巡檢：git 分歧第 4 次復發（自動修復）+ 三份 SKILL.md 一致性驗證

### 事件（2026-11-04 08:15 早上簡報）
- **症狀**：website repo（= workspace，jyonline0604/website）git fetch 後本地落後 origin/main 1 個 CI commit（b62c22eba..ab1073884，GitHub Actions 新聞/財務/RSS 自動更新），同時 git status 有未提交嘅 M DREAMS.md（03:00 Memory Dreaming Promotion 產出 14 行）
- **修復**：先 commit DREAMS.md → git pull --rebase origin main（rebase 成功，CI 冇碰 DREAMS.md）→ git push origin main（ab1073884..124039b5e）→ 分歧 0/0、工作區乾淨
- **巡檢全部綠**：kofhk.com 200（0.75s）；線上 assets/chapters-data.json?v=20261104 = 1818 章 = 本地 chapters-data.json 1818 = V7 state max CH1818 → 零分歧；systemctl --failed = 0（issue #7 根因檔真係已移除，連續 3 日清零）；磁碟 / 16%（68G/468G、377G 可用）；Mem available 3.0Gi / 7.0Gi、swap 0；uptime 1 日 10 小時、load 0.69
- **Dropbox**：V5 270 章 / V6 273 章（max CH1740）/ V7 78 章（max CH1818）2026-11-03 全部「未處理 0」；V7 11:30 加載 CH1813-CH1818 6/6 成功；V4 維持退役（state 265 章 CH926-1190 全處理，勿加返）
- **Cron**：OpenClaw 8 個 job 全部 enabled + lastStatus=ok + consecutiveErrors=0 + delivered；system cron（crontab -l）條目全在位；cron-guardian 2026-11-03 21:30 實跑「全部正常，無需修復」
- **SKILL.md 同步**：local + Second-brain + Max-backup 三份 v2.9.120 md5 一致（f40d8f673959，5756 行）→ 改為 v2.9.121 後再同步三份

### 教訓
- **「記憶備份 08:00 已成功」唔等於「網站 repo 已同步」**：08:00 記憶備份只打包 MEMORY.md + memory/*.md，網站 repo 嘅 CI commit 係另一條線 → 早上簡報一定要自己做 git fetch + git status --porcelain 雙查
- **git 分歧係第 4 次復發（#11 / #13 / 10-31 / 今日）**：根治方向係 03:00 dreaming 直接 commit + push，或者加一個 05:00 嘅 git pull --rebase && git push system cron；目前靠簡報巡檢兜底
- **SKILL.md 同步前一定要 md5 + 行數雙驗**（issue #12/#14 教訓）：今日三份一致（5756 行 / md5 f40d8f673959），確認無分叉先改
- **同一天多個 session 唔好用同一個標題 append**（issue #14 教訓）：今日標題用「(v2.9.121) - 早上簡報巡檢：git 分歧第 4 次復發」以便辨識
- **線上一致性一定要加 cache-buster**（issue #14）：?v=20261104 先至係用戶見到嘅版本

---
## [2026-11-04] 更新 - skill 副本漂移：已安裝副本可能落後於備份倉

### 問題
- 18:00 Skill更新檢查發現：已安裝 skill ( ~/.openclaw/skills/novel-site-standards/SKILL.md ) 停留喺 v2.9.120，而 workspace 副本 + Second-brain + Max-backup 都已係 v2.9.121
- 即係當日新寫嘅條目（cache-buster 修復、logrotate 結案、git 分歧自癒、cron 退休等）並未載入 runtime 實際讀取嘅 skill

### 修復
- 以備份倉最新版本覆蓋已安裝副本，並將四處副本（已安裝 / workspace 副本 / Second-brain / Max-backup）重新對齊同一版本
- 新增本條 + 版本號 bump 同步四處

### 教訓
- skill 有四個副本（已安裝目錄、workspace 內 .openclaw/skills 副本、Second-brain、Max-backup）；任何一處更新後都要 md5 + 版本號四處核對，否則 runtime 讀嘅可能係舊版本
- 更新後務必核對：md5sum 四處 + grep version 四處，唔好只睇 git push 成功


---

## [2026-11-04] 更新 - git add 對「已被 .gitignore 忽略但仍被追蹤」檔案會 exit 1，&& 鏈會斷

### 問題
- workspace 嘅 .gitignore 忽略 `.openclaw/` 同 `memory/`，但 `memory/2026-11-04.md` 同 `.openclaw/skills/novel-site-standards/SKILL.md` 其實係**已被追蹤**（tracked）嘅檔案
- 執行 `git add -A memory/2026-11-04.md .openclaw/skills/.../SKILL.md && git commit ...` 時，git 印出 "The following paths are ignored by one of your .gitignore files" 並 **exit code = 1**
- 但實際上檔案**已經 stage 成功**（`git status --porcelain` 顯示 `M ` 而唔係 ` M`）—— 因為 exit 1，&& 鏈令 git commit **被完全跳過**，令人誤以為 add 失敗

### 修復
- 將 `git add` 同 `git commit` 拆開做，先睇 `git status --porcelain` 確認已 staged（`M ` = staged，` M` = 只係工作區改動）
- 需要的話用 `git add -f` 強制加入被 ignore 但已追蹤嘅路徑

### 教訓
- **`git add` exit code 唔等於「有冇 stage 到」**：對 tracked-but-ignored 檔案，git 會 warn + exit 1，但 staging 其實成功
- 唔好將 `git add` 用 `&&` 直接串去 `git commit`；改為分開執行 + 用 `git status --porcelain` 實測 staged 狀態
- push 之後照舊用 `git fetch origin` + `git status -sb` 判斷真實狀態（已記錄於 2026-11-04 早上簡報教訓）

---
## [2026-11-05] 更新 - 版本檢查收單軌（退役 system crontab 軌）

### 修復內容
- 移除 system crontab 的「OpenClaw版本檢查 每天11:00」條目（check_openclaw_update.py），保留 OpenClaw cron job「OpenClaw Version Check」作唯一軌
- 解決：同一個腳本兩軌各行一次 → 大肥喵每日收兩次完全相同嘅版本 Telegram 通知（11:00:09 + 11:03:22）
- 與簡報軌一致（11-01 已退役 system cron 簡報軌、保留 OpenClaw cron 軌）→ 全面單軌

### 保留軌的好處
- OpenClaw cron job 照跑同一個腳本 → Telegram 通知照發（大肥喵一樣收到）
- 額外多一份好處：執行結果會入 agent 對話（可做交接/審計），system crontab 軌唔會
- 若將來想回復雙軌，只要把 crontab 條目加返即可（已安裝腳本不變）

---

## [2026-11-05 13:15 更新] 簡報送達驗證 + 連環重啟處理

### 修復內容
- 更正 memory/2026-11-05.md 嘅錯誤記述：08:44 嘅 catch-up 補跑其實喺 08:49 被 gateway restart 打斷、**未送達**（真係送達係 13:15 重試）
- memory/issues.md #10 補上今日第 6、7 次重啟嘅復發記錄（boot -2 08:07:00 → boot -1 08:41:06→08:49:29 → boot 0 08:50:21）

### 根本原因
- 機房連環人手關機（GNOME 桌面），起機後 OpenClaw scheduler 自動 catch-up，但 catch-up 排程會撞正下一次重啟 → 被 gateway restart 中斷

### 解決方法
- 簡報送達狀態一律以 automations runs 嘅 delivered / deliveryStatus 為準，唔用 memory 筆記做準
- catch-up 被斬斷時由 scheduler 自動重試，唔需人手補跑；重試成功後更正 memory 紀錄

### 步驟
1. 睇 journalctl --list-boots 對齊每次重啟時間窗
2. 睇 automations runs 確認 job 係 delivered 定 interrupted
3. 修正 memory/2026-11-05.md + issues.md #10
4. 同步 SKILL.md 四份副本（local / website repo / Second-brain / Max-backup），版本 +0.0.1

---
## [2026-11-05] 更新 - 收單軌只係刪 crontab 唔夠：cron-guardian 會加返

### 問題
- 11:45 移除 system crontab 版本檢查條目（收單軌），但 cron-guardian.sh 嘅 SYSTEM_TASKS 仍列住 check_openclaw_update.py
- guardian 每 30 分鐘巡檢一次「缺失 = 加返」→ 今晚 21:30 就會把條目加返，雙軌重現
- 教訓同 send-briefing.sh 退役（11-01）完全一樣：守護機制會同「退役」對抗

### 修復
- cron-guardian.sh：把 check_openclaw_update.py 從 SYSTEM_TASKS 移除（照 send-briefing.sh / Vol4 退役做法加註說明：crontab 冇佢係正確狀態，唔好加返）
- 清理 crontab 殘留註釋行
- 實跑 guardian 驗證：冇加返，單軌維持 ✅（crontab 11 條）

### 教訓
- 「退役某個 system cron 條目」係三步：(1) 刪 crontab 行 (2) 從 cron-guardian SYSTEM_TASKS 移除 (3) 實跑 guardian 驗證唔會加返 — 淨做 (1) 一定會喺下一輪巡檢復發


---

## [2026-11-05 22:00] 更新 - push 腳本嘅 reset --hard 會靜靜抹走未提交改動

### 問題（今晚 22:00 健康報告實測中招）
- `scripts/git-push-with-lock.sh` / `scripts/batch-push.sh` 順序係「先 `git pull --rebase` → 後 commit」
- 一有本地未提交改動，rebase 必然報 "cannot pull with rebase: You have unstaged changes" → fallback 行 `git reset --hard origin/main`
- 後果：未提交改動被靜靜刪走（今晚 SKILL.md v2.9.126 + memory/2026-11-05.md 紀錄就係咁消失，仲要靠 Second-brain 副本先搶返）
- 同一個 bug 今日 10:11 新聞後備 log 已經出現過一次「rebase/push 失敗」，當時只當作普通失敗，冇追根因為 destructive fallback

### 修復
- 兩個腳本都改成「先 commit → 後 pull --rebase → 最後 push」
- fallback 改用 stash 安全同步：`git stash push -u` → fetch/reset → `git stash pop`，唔再無條件 `reset --hard`
- 同步四份 SKILL.md 副本（local ~/.openclaw/skills / website repo / Second-brain / Max-backup）

### 教訓
- 任何腳本入面嘅 `git reset --hard` fallback 都係「最後手段」級危險：同步失敗時佢唔會報錯，只會靜靜刪資料
- 「rebase/push 失敗」呢類 log 唔可以當雜訊，要追落 fallback 邏輯先算修好
- 推前必須先 commit，rebase 嘅前提就係乾淨工作區

---

## [2026-11-06] 更新 (v2.9.128) - 早上簡報巡檢：git 分歧第 6 次復發自動修復 + 線上一致性三來源核對法

### 事件（2026-11-06 08:15 早上簡報）
- 巡檢全綠：kofhk.com 200（0.68s）／磁碟 16%（68G/468G、377G 可用）／Mem available 2.8Gi／uptime 23h25m（boot 0 自 11-05 08:50:21，今日無重啟）／systemctl --failed = 0
- 線上一致性：assets/chapters-data.json?v=20261106 = 1830 章 = 本地 chapter-N.html 1830 檔（1-1830 零缺口）= V7 state max CH1830 → 零分歧
- Dropbox：V4 依 2026-10-02 指令退役（勿加返）；V5/V6/V7 2026-11-05 全部正常（V5/V6「未處理 0」、V7 6/6 成功）
- 自動修復：workspace 落後 origin/main 1 個 CI commit + DREAMS.md、memory/2026-11-05.md 未提交 → commit → pull --rebase → push → 三倉 0/0

### 新增：線上一致性三來源核對法
- 三個來源必須對齊先算「零分歧」：
  1. 線上索引：https://kofhk.com/assets/chapters-data.json?v=YYYYMMDD（必須帶 cache-buster；裸路徑 /chapters-data.json 係 404，裸 /assets/… 可能有舊快取）
  2. 本地實際檔：ls chapter-*.html | grep -E 'chapter-[0-9]+\.html' | wc -l（要扣 chapter-template.html / chapters.html），再檢 1..N 無缺口
  3. 各卷 state max：.dropbox-sync/volume7_state.json（最前卷）嘅 ch_num 最大值
- 三者數字相等 → 零分歧；唔等就要逐個來源查邊個係舊值
- 裸路徑 /chapters-data.json 回 404 係正常（網站只有 assets/ 版本），唔好誤報成「索引遺失」

### 教訓
- git 分歧已連續 6 次復發（10-24、10-28、10-31、11-04、11-05、11-06），成因係 GitHub Actions 直接推同一 repo → 根治方向仍然係「每日簡報巡檢固定 fetch + status 雙查並自動 rebase push」
- 判定線上一致性唔可以只 curl 一條 URL，要三來源對照（線上 JSON / 本地檔 / state）

---
## [2026-11-06] 更新 - 2026.11 升級後舊 cron job 失去 inference account（全部報錯）

### 症狀
- 部機升到 OpenClaw 2026.11.1 後，中午簡報 12:55 報錯：Automation has no recorded inference account. Explicitly select its account with a model@profile update before running it
- 後果：該次簡報完全冇送出（deliveryStatus unknown），而其餘 agentTurn job（傍晚簡報 17:55、健康報告 22:00、Audio Sync、版本檢查、早上簡報）隨時會同樣爆 — 等於整個 automation 停擺
- 注意：升級前最後一次成功係 11:00 版本檢查（報 2026.10.9），即係升級喺 11:00-12:55 之間發生

### 修法（官方 docs：docs/automation/cron-jobs/troubleshooting.md）
- openclaw cron edit <jobId> --model "<provider/model>@<profileId>"
- profileId = openclaw.json auth.profiles 嘅 key（例如 minimax:cn、openrouter:default、zai:default）
- 已對 6 個 agentTurn job 全部綁定 minimax/MiniMax-M3.1-Flash@minimax:cn

### 教訓
- **每次升級 OpenClaw（尤其 minor 版）之後，一定要批量重綁 cron job 嘅 model@profile** —— 舊 job 冇 recorded inference account 就會全線報錯，唔止一個 job
- 檢查方法：openclaw cron list --json 睇 payload.model 有冇 @profile；errs>0 睇 state.lastError（會直接寫明根因）
- 症狀同 2026-10-21 升級炸 cron（模型改名）同類，但今次係 account 綁定機制改變


---
## [2026-11-06] 更新（補） - cron_model_guard 會把 @profile 綁定改返落去

### 第二個陷阱
- 綁完 model@profile 之後，scripts/cron_model_guard.py 會判定 payload.model「唔喺 modelPolicy.allow 白名單」→ 自動 --fix 改返無 profile 嘅 primary model
- 即係話：綁 profile 修好 automation 之后，guard 會喺下一輪把綁定還原 → 17:55 / 22:00 又會報 "no recorded inference account" 爆

### 修復
- cron_model_guard.py：比較時用 base model（剝走 @profile）對白名單；fallbacks 同樣處理；--fix 時保留原本嘅 @profile suffix（唔會還原走）
- openclaw.json 嘅 modelPolicy.allow（defaults + entries.main）加入 minimax/MiniMax-M3.1-Flash@minimax:cn
- 實跑驗證：OK: every job model override is within policy allow list ✅

### 教訓
- 升級後綁 model@profile 係必須，但要同步睇 cron_model_guard.py 同 modelPolicy.allow，否則守衛會靜靜還原
- 任何「自動修復」型守衛腳本，都要檢查佢嘅白名單／比對邏輯會唔會抵銷我哋啱啱做嘅修復


---
## [2026-11-07] 更新 - 自動生成數據檔 push 衝突（finance-data / finance-news）

### 症狀
- 09:15 推送驗證發現有未推送 commit，執行 git pull --rebase 時卡住：both modified: finance-news.json
- 繼續 rebase 再撞：finance-data.json（同一批 16:00 數據）
- 根因：本地 system cron（update_finance_news.sh / update_finance.sh，10/16 時段）同 GitHub Actions 喺同一個時間窗各自寫同一份自動生成 JSON → 兩邊都改同一檔 → rebase 必然衝突

### 處理
- 逐個解決衝突：git checkout --theirs（rebase 中 = 正在重放嘅 commit 版本）→ git add → 驗證 JSON 有效 → GIT_EDITOR=true git rebase --continue，迴圈至 rebase 完成 → git push
- 結果：rebase 完成、push 成功（d2c71fbc4..78c06367c）、0 未推送 / 0 髒檔、線上 finance-data.json 正常

### 教訓
- 自動生成數據檔（finance-data.json / finance-news.json / aqhi-data.json）每日必然出現 rebase 衝突，唔係故障
- 處理流程固定：checkout --theirs → add → 驗 JSON → rebase --continue（迴圈）→ push
- 唔好因為衝突就 git reset --hard 或 abort（會丟失當日已生成數據）


---
## [2026-11-07] 更新 - 22:00 健康報告巡檢（CI commit 落後同步 + 全綠確認）

### 症狀
- `git fetch` 發現 origin/main 多 1 個 commit（b60a56985 CI 每日自動更新新聞/市場數據/sitemap/RSS，13:41 UTC），本地 behind 1、ahead 0、工作區乾淨 → 唔係故障，係 CI 正常推播

### 處理
- `git pull --rebase origin main` → 零衝突（因為本地冇改同一批自動生成 JSON）→ 分歧即刻歸 0/0
- 追加 22:00 健康報告記憶 → commit + push（b60a56985..a85e76fd4）→ 0 未推送 / 0 髒檔

### 教訓
- 每日健康報告出現 behind 1（CI 自動生成數據 commit）時，先 fetch + `pull --rebase`；只要本地冇同一批數據改動就零衝突，唔需要 `checkout --theirs` 迴圈
- 真正需要迴圈解決嘅情況：本地 system cron（財經/財經新聞/AQHI 10,16）同 CI 寫同一批 JSON（見 2026-11-07 09:15 條目）
- `.token-store/dropbox-token.txt.bak` 係 renew_dropbox_token.py 每次續期自動重建嘅回滾副本（權限 600），唔係遺留檔，唔好刪

---
## [2026-11-07] 更新 - skill 副本漂移復發（已安裝副本落後一個版本）

### 症狀
- 22:00 健康報告出新條目（v2.9.132）並 push 到 Second-brain / Max-backup / workspace 副本
- 但**已安裝**副本（~/.openclaw/skills/novel-site-standards/SKILL.md，runtime 真正讀嗰份）停留喺 v2.9.131 → 今日新教訓未入 runtime 指引
- 18:00 Skill更新檢查靠「四處 md5 唯一值 = 1」捉到（唯一值 = 2 即漂移）

### 修復
- 以三處一致嘅 v2.9.132 覆蓋已安裝副本，再 bump 到 v2.9.133 並四處同步
- 教訓重申：更新 skill 必須四處同步（已安裝 / workspace 副本 / Second-brain / Max-backup）；每日檢查要核對「四處 md5 唯一值 == 1」，唔係只睇 git push 成功


---
## [2026-11-07] 更新（補） - skill 副本漂移根治：新增 nightly 自動對齊 cron

### 為乜要做
- 副本漂移今日第二次復發（已安裝 v2.9.131 vs 其餘三處 v2.9.132）→ runtime 讀緊舊指引
- 18:00 檢查可以捉到並手動修，但「22:00 健康報告出新版本」呢類事發生喺檢查之後 → 只能等第二日
- 根治：新增 scripts/sync_skill_copies.sh + system crontab 23:20 自動對齊四處（以版本號最高嗰份為準）並 commit/push

### 用法
- scripts/sync_skill_copies.sh：四處（已安裝 / workspace 副本 / Second-brain / Max-backup）對齊 standards + av-generator，備份倉有變更就自動 commit + push
- crontab：20 23 * * *（記憶備份 23:00、自動記憶日誌之後）
- 每日檢查仍要核對「四處 md5 唯一值 == 1」做雙保險


---
## [2026-11-08] 更新 - openclaw-version.json 狀態檔停更 → 每日簡報錯報「有更新可用」

### 症狀
- 早上簡報 digest 長期顯示「⚠️ OpenClaw：有更新可用（v2026.10.10）」
- 但實際 `openclaw --version` = 2026.11.1、`npm view openclaw version` = 2026.11.1 → 根本冇更新

### 根本原因
- `scripts/generate-briefing-full-v5.py` 讀 `workspace/openclaw-version.json` 顯示版本狀態
- 該檔只由 `scripts/check_openclaw_update.py` 更新
- 但 OpenClaw cron「OpenClaw Version Check」行嘅係 `scripts/check-openclaw-version.sh`（純 shell，**唔寫** version.json）
- 結果 version.json 停留喺 2026-10-05（current 2026.10.9 / latest 2026.10.10 / update_available=true）→ 每日簡報都係報假版本

### 修復
- `scripts/check-openclaw-version.sh` 尾端加：跑 `check_openclaw_update.py` 同步刷新 version.json（冇更新時唔會誤發 Telegram）
- 即時補跑一次 → version.json 更新為 current=2026.11.1 / latest=2026.11.1 / update_available=false
- 驗證：重跑 digest → 顯示「✅ OpenClaw：v2026.11.1（最新）」✅

### 教訓
- 簡報顯示嘅狀態要同「實際執行嘅那個腳本」對齊：cron 行 shell 版、狀態檔由 python 版寫 → 兩者必須串埋
- 巡檢見到「有更新可用」要即場核對 `openclaw --version` vs `npm view openclaw version`，唔可以只信狀態檔

---

## [2026-11-08] 更新 - 早上簡報 08:15 job 撞 1200s timeout → 該輪報告未送達

### 症狀
- 08:15 該輪 job 跑足 1203.771s（> timeoutSeconds 1200）→ `cron: job execution timed out (last phase: model-call-started)`
- lastRunStatus=error、consecutiveErrors=1、lastDeliveryStatus=unknown → **Telegram 冇收到早上簡報**（報告已寫好但announce 送達前先被閘）
- scheduler 08:35 自動補跑本輪

### 根本原因
- 該輪同時做咗「修 openclaw-version.json + SKILL.md 四份同步 + 三倉 git push + 記憶寫入」
- 每一步都係獨立 model call，累積耗時撞 1200s 上限 → job 被閘死，announce 無機會送達

### 修復
- `openclaw cron edit 27d54b55-3523-4475-8ad5-b07445cc4378 --timeout-seconds 1800`（1200 → 1800）
- 驗證：`openclaw cron list --json` → payload.timeoutSeconds = 1800

### 教訓
- 簡報類 job timeoutSeconds 要按「實際工作負載 × 單步 model call 成本」估，唔好淨係跟其他 job 一律 1200s
- 同一輪做「巡檢 + 修復 + SKILL 同步 + 三倉 push」時，總時長好易超標 → 要么放寬 timeout，要么將 git push / SKILL 同步拆去獨立 job
- 睇 job 有冇送達要睇 `lastDeliveryStatus` + `automations runs` 嘅 delivered/error 欄位，唔可以只睇 job 存在（教訓 #10 同款）

---

## [2026-11-08 08:56] 更新 - `cron edit --timeout-seconds` 只對下一次 run 生效；補跑輪自我犧牲

### 症狀
- 08:15 輪跑足 1203.771s 撞 1200s 上限 -> `cron: job execution timed out (last phase: model-call-started)`、deliveryStatus=unknown -> 未送達
- 08:35 scheduler 補跑輪：同一輪內完成 `openclaw cron edit ... --timeout-seconds 1800` + SKILL v2.9.136 + 三倉 push，但**同一個 run** 仍用開跑時嘅 1200s -> 再被閘死（dur=1200.4s）-> consecutiveErrors=2
- 結果：08:15 + 08:35 兩輪都冇到 Telegram；08:56 輪（1800s 上限）先交付

### 根本原因
- `openclaw cron edit` 改 payload 只由**下一次 run** 生效；正在跑嘅 run 沿用啟動時嘅 config revision -> 補跑輪改咗都救唔到自己
- 補跑輪把「修復 + SKILL 同步 + 三倉 push」塞入同一輪 -> 工作量必然長過 1200s -> 再次自我犧牲

### 修復
- timeoutSeconds 1200 -> 1800（`openclaw cron list --json` -> payload.timeoutSeconds=1800，已驗證）
- 08:56 輪以 1800s 上限完成巡檢 + 報告，經 message tool 直接送達

### 教訓
- 補跑/重試輪係「最低成本交付」嘅最後機會：只做巡檢 + 報告，唔做維修；SKILL 同步 / 三倉 push 留俾 22:00 健康報告
- timeout edit 後要即刻 `openclaw cron list --json` 睇 payload 確認新值，並確認新 run 已用新 revision
- 核對簡報有冇送達要睇 deliveryStatus + delivered 欄位（教訓 #10 同款），唔可以只信 memory 筆記
---
## [2026-11-08] 更新 - provider 掛死令排程失送 + provider 級 timeout 快速失敗

### 症狀（2026-11-08 早上）
- 早上簡報 08:15 job errs=2、status=error、delivered=None → 大肥喵完全收唔到早上簡報
- lastError: cron: job execution timed out (last phase: model-call-started)，每次都係 20 分鐘（1200 秒）
- gateway log: provider=minimax api=anthropic-messages 連續 60 秒級 error 之後 TimeoutError
- 補跑（08:35 / 08:55）同樣掛死 → 證明唔係單次偶發

### 根因
- minimax anthropic-messages 路由今朝極慢/無回應，isolated cron lane 喺 model-call 階段無限等
- job payload timeoutSeconds=1800 保護唔到（lane 20 分鐘先被剪），所以成個 job 靜靜死咗，
  大肥喵收到唔到簡報而通知亦冇送出去

### 修復
- openclaw.json: models.providers.minimax.timeoutSeconds = 120（原本冇設定）
  → provider 請求 120 秒內無回應就快速失敗，scheduler 即刻切換 fallback（openrouter 5 個 free model）
  → 由「掛死 20 分鐘全線失送」變成「2 分鐘內 fallback 接手」
- 教訓：provider 級 timeout 一定要設；只靠 job timeoutSeconds 唔夠，因為失送發生喺 lane 剪斷之前

### 附帶發現
- cron run 手動觸發時，若主 session lane 仍忙，會回 already-running（唔係 job 壞）
  → 診斷時要分清「job 失敗」同「lane 排隊」，唔好誤判為 job 壞

---
## [2026-11-08] 更新 - MiniMax 推理停擺 + agent 回合 timeout 太短

### 症狀
- 早上簡報 08:15 job 連續三輪失敗（08:15 / 08:35 / 08:55）：cron: job execution timed out (last phase: model-call-started) → 模型端唔回應，唔係腳本問題
- 09:04 第 4 輪成功交付（errs 清零、delivered=True）→ scheduler catch-up 自癒成功，簡報無漏
- 同一日 agent 互動回合亦被 120s 逾時切斷（報 Request timed out before a response was generated）

### 修復
- agents.defaults.timeoutSeconds 120 -> 600（主 agent 回合上限太短，重工具巡檢回合易被腰斬）
- job 本身 timeoutSeconds=1800 維持不變（cron 專用），fallbacks 5 條（openrouter free 模型）保持

### 教訓
- job execution timed out (last phase: model-call-started) = 模型端停擺，唔係工作腳本壞；睇 runs 記錄就分得出（model-call-started vs 其他 phase）
- 互動回合被 Request timed out 截斷時，先查 agents.defaults.timeoutSeconds 而唔係亂加 exec timeout

---
## [2026-11-08] 更新 - 跨 provider fallback 必須各自綁 account（否則切換即硬失敗）

### 症狀
- 每日 Audio Sync 10:00 job 報錯：Automation candidate is incompatible with its recorded inference account and route.
- 2026.11.1 邏輯（dist/run-executor）：binding 存在時，若 candidate provider != binding.provider 就 throw，唔會靜默切換
- 即係：job 綁咗 minimax:cn（11-06 升級後修 inference account 時綁定），但 fallback 係 openrouter/* 冇綁 account → 一旦 MiniMax timeout 要切 fallback 就硬失敗
- 只係 Audio Sync 中招：今日 10:00 撞正 MiniMax 停擺；其他 job 撞正就一樣爆

### 修復
- 6 個 agentTurn job 嘅 5 條 fallback 全部改為 model@openrouter:default（每個 fallback 帶自己嘅 stored account）
- Audio Sync 補跑 11:34 → status=ok、delivered=True、errs 歸零

### 教訓
- 2026.11 起：job 嘅 inference account 一旦綁定，跨 provider fallback 必須各自綁 account，否則 fallback 唔會被採用（會直接硬失敗）
- 升級或改 model@profile 時，fallbacks 要一併檢查同樣式，唔可以只睇 primary
---
## [2026-11-08] 更新 - 自動生成資料檔 rebase 衝突：殘留衝突標記曾被推上線

### 症狀
- 16:0x 拉遠端更新時 git pull --rebase 撞 finance-news.json / finance-data.json 衝突（本地 16:00 新資料 vs 遠端 CI 14:53 舊資料）
- 解決衝突時用錯方向：finance-news.json 取到遠端版 + 帶住衝突標記版本，被 git add 後隨 rebase 一起 commit 並 push（b5cde377b）
- 驗證階段先發現：finance-news.json INVALID JSON、含 2 個衝突標記 → 線上新聞資料檔一度無效

### 修復
- 重取乾淨版本：git show 37566baae:finance-news.json（本地 16:00 有效版本）→ 覆寫 → commit 70d55ddae → push
- 驗證：本地 / origin/main / 線上 https://kofhk.com/finance-news.json 全部 valid JSON、0 衝突標記

### 教訓
- rebase 解決衝突時，ours/theirs 喺 rebase 語意相反：ours = 上游（遠端），theirs = 正在重放嘅本地 commit；本地更新嘅話要取 theirs
- 任何寫入自動生成資料檔嘅 commit，push 前必須驗 JSON 有效性 + 衝突標記數（grep -c "<<<<<<<"），唔好靠肉眼
- 解完衝突要即刻驗檔案內容，唔好等到下一次巡檢先發現
---

## 2026-11-08 更新
- 傍晚簡報 cron (f8b447b6) 連續 5 次於 model-call-started 階段超時
- 根因：timeoutSeconds=1800 太短，模型首輪呼叫耗盡預算
- 解決：openclaw cron edit 將 timeoutSeconds 調高至 3600

---

---

## 2026-11-10 更新 (根因已由 openclaw runtime 原始碼確認)
- 症狀：5 個 agentTurn cron (早上簡報 08:15、中午簡報 12:55、每日 Audio Sync 10:00、每日健康報告 22:00、傍晚簡報 17:55) 連續 error，統一訊息 "Automation candidate is incompatible with its recorded inference account and route."
- 真正根因 (run-executor.runtime 原始碼)：job 用 model@profile 會記錄 inference binding (provider=minimax)；minimax primary 本身常被 rate_limit，一 cut 去跨 provider 嘅 openrouter fallback 就觸發 providerOverride != binding.provider 而 hard error，唔會靜靜哋降級。
- 已作廢嘅誤診：唔係 "@minimax:cn suffix 唔喺 modelPolicy.allow"；allow list 一直有 minimax/MiniMax-M3.1-Flash@minimax:cn。
- 正確修法 (error-playbook 1b)：每條 fallback 都要綁同 provider 配對嘅 account，即 openrouter/<model>:free@openrouter:default；primary 明確寫 minimax/MiniMax-M3.1-Flash@minimax:cn；allow list 補 @openrouter:default 變體。
- 驗證方法：每個 job fb=N/N (全部 fallback 帶 @)，再 cron run 補跑，consecutiveErrors 歸零兼 lastRunStatus=ok、lastDelivered=true。
- 同步：scripts/cron-guardian.sh 重建模板嘅 --model / --fallbacks 一樣要帶 @profile，否則下次重建會還原壞狀態。

---
## [2026-11-10] 更新 - cron 全線爆一日嘅真正根因（guardian 重建順序）+ 防復發加固

### 真正根因（runtime 原始碼 captureCronInferenceBinding + 實測時間線）
- 根因（runtime 原始碼 captureCronInferenceBinding + run-executor 保護網核實）：job 嘅 inference binding 由 **primary** model reference（`model@profile`）capture → binding.provider = minimax、account = minimax:cn；run 時候選 provider ≠ binding.provider 就直接 throw `Automation candidate is incompatible with its recorded inference account and route`（唔會靜靜哋降級）
- 即係：minimax primary 一 rate_limit／slow，scheduler 切去 openrouter fallback 就必然 hard-fail → 11-09 08:15 起 6 個 agentTurn job 全線爆、一日冇簡報（2026.11 規則：a switch cannot adopt a different account）
- 已驗證可行嘅設定：primary `minimax/MiniMax-M3.1-Flash@minimax:cn` + 每條 fallback 各自綁自己 account（`openrouter/…:free@openrouter:default`），並且改完 fallback 之後即刻重綁一次 primary（令 job 重新 capture 授權）→ 2026-11-10 17:15 早上簡報、17:26 版本檢查、17:27 Audio Sync 全部 ok + delivered
- 殘餘風險（要知）：呢個設定下 fallback 仍係跨 provider，一旦 minimax 再 rate-limit，openrouter fallback 切換一樣會 hard-fail；要完全冇呢個風險就要整條候選鏈同 provider（例如全部 openrouter）
- cron-guardian.sh 模板：每個 block 單一 `--fallbacks`（各自 @openrouter:default）→ 單一 `--model`（@minimax:cn）→ 單一 `--timeout-seconds`，順序同上面一致，確保重建唔會還原壞狀態

### 已加固
- scripts/cron-guardian.sh：6 個 job block 全部正規化成單一 --fallbacks → 單一 --model → 單一 --timeout-seconds（3600 簡報 / 1800 Audio Sync / 600 版本檢查），語法已驗
- scripts/cron_model_guard.py：新增 profile_variant()；model 修復用 known-good `<primary>@<profile>` 變體；fallback 修復唔再退回無 @profile 嘅 primary；改完 fallbacks 即刻重綁 primary；新增「model override 冇 @profile」檢查
- 4 個重型簡報 job timeoutSeconds 1800 → 3600（model-call-started 慢回時唔會中途被斬；11-10 中午簡報正正係 1800s 內 model 未回而被斬）

### 教訓
- 「最後一次 account 選擇決定 job 記錄 account」：任何 `cron edit --model/--fallbacks` 都要諗清楚最後一個參數係邊個 provider；重建 job 嘅 script 更加要留意參數順序
- 重建 / 修復 automation 後一定要 `cron list` 睇 payload 實值（model + fallbacks 嘅 @profile），再 `cron run` 補跑到 delivered=true 為止；唔可以只睇 job 存在同 enabled
- 有 recorded account 嘅 job 唔能夠採用跨 provider fallback（a switch cannot adopt a different account）→ fallback 綁自己 account 只係避免 policy 駁回，唔會令跨 provider 切換合法；minimax 慢回時要靠 timeout + catch-up，唔係靠 fallback
- 修完要逐個 force run 驗證（errs 歸零 + lastRunStatus=ok + delivered=true）
---

## [2026-11-10] 更新
- 修復內容：OpenClaw cron job 連續報 Automation candidate is incompatible with its recorded inference account and route.
- 根本原因：automation 記錄嘅 inference account / route 綁定過期，需用 openclaw cron edit 重綁 model + fallbacks + delivery（announce / telegram / to）
- 解決方法：openclaw cron edit <id> --model minimax/MiniMax-M3.1-Flash@minimax:cn --fallbacks <openrouter 清單> --timeout-seconds 3600 --announce --channel telegram --to <chatId>；用 openclaw cron list --json 檢查 consecutiveErrors / lastDeliveryError
---
## [2026-11-10] 更新 - code mode 入面要用 exec(...) 直接呼叫，唔可以用 tools.exec(...)

### 症狀
- isolated cron session（健康報告 22:00 嗰輪）code-mode 直接爆 `ReferenceError: tools is not defined`（stack 落喺 openclaw-code-mode/user.js:2）
- 主 session 相同情況亦出現過（`tools` 未定義），改用 exec(...) 直接呼叫就正常

### 根因
- code mode sandbox 只有直接注入嘅全域（exec / ls / read / write / process 等），`tools` 呢個 wrapper 全域並唔存在；寫 tools.exec(...) 一定 ReferenceError

### 做法
- code mode 內一律用 `exec({command: ...})` 直接呼叫，唔好包 tools.exec
- shell 腳本用 write() 寫成檔再 exec 跑，唔好喺 code 內砌長 heredoc（引號會撞，寫多次都會出現 SyntaxError）

---

## [2026-11-10] 更新 (v2.9.148) - 移除跨 provider fallback（Automation candidate is incompatible with its recorded inference account and route）

### 症狀
- 6 個 agentTurn cron job（早上簡報 08:15 / 中午簡報 12:55 / 傍晚簡報 17:55 / 每日健康報告 22:00 / 每日 Audio Sync 10:00 / OpenClaw Version Check）喺 minimax 短暫抖動時全部 hard-fail：lastDeliveryStatus=unknown、delivery=not-started，run transcript 出現 `run-failed-before-reply` → 「Automation candidate is incompatible with its recorded inference account and route.」。
- session transcript 顯示候選鏈由 `openrouter/poolside/laguna-s-2.1:free` → `openrouter/recursive/flint-v1.0:free`（跨 provider 切換）之後先爆。
- 連續 3 晚（11-08 / 11-09 / 11-10）每日健康報告連續 error，delivery 完全冇送達。

### 根本原因
- 2026.11 起 agentTurn job 用 `model@profile` 記錄 inference binding（provider=minimax / profileId=minimax:cn）。fallback 鏈一旦切去另一個 provider（openrouter），runtime 拒絕採用另一個 account → hard-fail。**跨 provider fallback 唔係真正後備，係 fatal 陷阱**。
- minimax provider 只提供 1 個可用模型（MiniMax-M3.1-Flash），冇第二個同 provider 模型砌真正 fallback 鏈；但 runtime 本身有 transient same-model retry（8 次），足以頂 minimax 短暫 model-fetch timeout（實測 119s timeout 後自動 retry 1/8）。

### 修復
- 6 個 job 全部改成 `--model minimax/MiniMax-M3.1-Flash@minimax:cn` + `--fallbacks minimax/MiniMax-M3.1-Flash@minimax:cn`（同 account、同 provider），用 `openclaw cron edit` **先 fallbacks 後 model** 重綁。
- `scripts/cron-guardian.sh` 6 個重建 block 嘅 fallback 串同步改成同 provider（唔改重建模板 → guardian 下次重建會把跨 provider fallback 帶返嚟）。
- 驗證：`openclaw cron list --json` 逐個確認 `payload.fallbacks`；sqlite `cron_jobs` 逐個確認 `inferenceBinding.provider=minimax` / `profileId=minimax:cn`。

### 教訓
- fallback 一定要同 recorded binding 同一個 provider/profile；跨 provider fallback 只會令原本可以 retry 嘅抖動變成 hard-fail。
- 修 payload 唔止要改 job，仲要改重建模板（guardian），否則復發。
- `openclaw cron edit` 只由**下一次 run** 生效；正在跑嘅 run 沿用啟動時嘅 config revision。

---

## [2026-11-10] 更新 - update_aqhi.sh push 迴圈：報「三次重試失敗」但其實從來冇 push 過

### 症狀
- 10:00 / 16:00 兩輪 AQHI 都報「[AQHI] push 三次重試仍失敗，留待下一輪自動恢復」，但同一分鐘 finance / finance-news 亦在改同一批 JSON。

### 根本原因
- `scripts/update_aqhi.sh` 把 `git push` 寫死喺 `git pull --rebase` **成功分支**入面。同一分鐘有其他 script 未提交改動時，pull 必然 fail（cannot pull with rebase: You have unstaged changes）→ push 一次都冇試過 → 但 log 仍然印「push attempt N failed」。commit 滯留本地，線上 AQHI 停喺上一個鐘。

### 修復
- push 改為獨立嘗試，唔再 gate 喺 pull 成功上面。
- pull 用 `-X theirs` 自動解衝突；pull 失敗就 `rebase --abort` 清理 + stash 未提交改動再試。
- 絕不 `reset --hard` 掉本地 commit（batch-push.sh 嘅舊 fallback 做法會抹走改動）。

### 教訓
- 「push 失敗」嘅 log 未必代表 push 過；睇清楚係 pull 失敗定 push 失敗，先唔會查錯方向。
- 同一分鐘多 script 寫同一個 repo → 全部 git 操作都必須經 flock（`.git-push.lock`）序列化，push 唔可以依賴 pull 成功。

---

## [2026-11-10] 更新 (v2.9.149) - 自動記憶 logger 每日寫入硬編碼 demo 假記錄（污染 216 個記憶檔）

### 症狀
- 每日 23:00（system cron `0 23 * * * scripts/auto-daily-memory-log.sh`）之後，當日 memory 檔必然多出 4 條假記錄：
  `### 系統修改: 新增功能`（GitHub提交: abc123、修改文件: scripts/test1.py + scripts/test2.py）
  `### 問題修復`（忘記自動記憶記錄）、`### 學習教訓`（永遠記住自動記憶記錄原則）、`### GitHub推送`（17e089b / feat: 添加真實財經新聞系統）。
- `scripts/test1.py` / `scripts/test2.py` 根本唔存在；`abc123` 唔係真 commit。
- 污染範圍：workspace memory/ 216 個檔案、252 處 demo 條目；Second-brain + Max-backup 記憶副本各 213 檔、852 區塊。

### 根因
- `scripts/auto-memory-logger.py` 個 `if __name__ == "__main__":` 段落係**測試示範碼**（硬編碼 test_files / abc123 / 17e089b），但 system cron 每日直接 `python3 auto-memory-logger.py` 執行 → 每日都寫入假記錄。

### 修復
1. `scripts/auto-memory-logger.py` 的 `__main__` 改成 `main_auto()`：`git log --since=midnight` 攞真實提交 → 寫**單一**「每日提交摘要」條目（hash 去重；無新提交就唔寫）。舊 demo 段落整段移除。
2. 清理 216 個 workspace 記憶檔 + 兩個備份倉各 213 個記憶副本嘅 demo 區塊（864 + 852 + 852 區塊）；demo 條目以外嘅內容一字無改。
3. 記憶 dreaming promotion 嘅 `- Candidate:` metadata（引用過 demo 文字嘅索引）唔當污染，保留原狀。

### 教訓
- **任何每日 cron 跑嘅 python script，`__main__` 唔可以係 demo/test 碼**：demo 段落應該用 `if __name__ == "__main__":` 隔離 + 明確 flag 先行，唔好每日自動寫入記憶檔。
- 記憶檔出現「時間戳好靚但內容一模一樣」嘅條目 = 有 cron 喺度寫模板假資料，要即刻查 `grep -c` 同源碼 `__main__`。
- 記憶備份（Second-brain / Max-backup 嘅 memory/ 副本）會同步污染，清理時要三倉一齊清，唔好只清 workspace。

---

## [2026-11-11] 更新 (v2.9.150) - 記憶 logger 摘要格式修正（雙重 `- ` 前綴）

### 問題
- v2.9.149 修好 demo 假記錄後，新版 logger 寫出嘅摘要條目每行都係 `- - ...`（`- ## 每日 git 提交摘要` / `- `b21882aabb` ...`）。

### 根因
- `log_to_memory()` 對 list 型 content 會逐行加 `- ` 前綴；我原本將摘要行本身寫成 `- `xxx``，再經 list 傳入 → 前綴疊加。

### 修復
1. 摘要行本身唔再加 `- `。
2. `content` 由 list 改成單一 string（`chr(10).join(lines)`）傳入 → `log_to_memory` 唔會再逐行加前綴。
3. 已移除寫歪咗嘅舊摘要條目並重跑驗證：輸出為 `## 每日 git 提交摘要 (auto-memory-logger)` + 每行 `` `hash` subject — files ``，格式正確。

### 教訓
- `log_to_memory()` content 傳 list 會自動加 `- `；要保留原格式（Markdown 標題／code 行）就傳單一 string。

---

## [2026-11-11] 更新 (v2.9.151) - SKILL.md 撞 256KB 載入上限 → 分檔瘦身（skill 會被跳過）

### 症狀
- 2026-11-11 08:15 早上簡報嗰輪 cron 連續兩次 `[agents/code-mode] Code Mode execution failed`，job `lastError` 顯示 `cron: job interrupted by gateway restart`。
- journal 同一秒出現：`[skills] Skipping invalid skill: file=~/.openclaw/skills/novel-site-standards/SKILL.md error=File exceeds 256000 bytes`。
- 即係**標準 SKILL 已經載入唔到**（檔案 299787 bytes > 256000 上限）→ 任何新 session 都讀唔到維護規範。

### 根因
- 每次修復都往 SKILL.md 追加更新記錄（由 v2.9.84 一路加到 v2.9.150），檔案由 ~180KB 膨脹到 299787 bytes，越過 skill loader 嘅 256000 bytes 上限。
- loader 遇到超限檔案直接 skip（唔報錯、只喺 journal 講一句）→ 靜靜哋失效。

### 修復
1. 逐章批次日誌（`## [日期] 更新 ... CHxxx-xxx`、2026-04-27～05-02 舊記錄）共 89 個區塊 122360 bytes → 搬去 `SKILL_HISTORY.md`（同一 skill 目錄），內容一字不刪。
2. SKILL.md 保留全部**操作規則類**區塊（維護八誡、強制檢查清單、Git/cron/Dropbox/章節處理修復經驗、2026-07 起全部記錄）→ 177427 bytes，重新落喺上限之內。
3. SKILL.md 開頭加「歷史記錄已分檔」指引；`scripts/sync_skill_copies.sh` 加埋 SKILL_HISTORY.md 同步，四處保持一致。

### 教訓
- **SKILL.md 有 256000 bytes 硬上限**：加更新記錄前要計大小，接近上限就要先分檔（規則留主檔、流水日誌搬 SKILL_HISTORY.md），唔可以無限追加。
- `Skipping invalid skill` 只喺 journal 出現，唔會通知用戶 → 每次加完 skill 更新都要 `stat -c%s` 檢查 + 確認 loader 冇 skip。
- 主機重啟（08:16 poweroff → 09:21 開機）令 08:15 嗰輪 cron 中斷；重啟後要補跑受影響 job。

---

## [2026-11-11] 更新 (v2.9.152) - code-mode 提示只加咗 1 個 job → 其餘 5 個全撞 tools.exec ReferenceError

### 症狀
- 早上簡報 08:15 連續兩輪 error：`cron: job interrupted by gateway restart`（主機 08:16 poweroff、09:21 開機）→ 補跑再撞 `LLM request timed out.`（dur 371834ms），deliveryStatus=unknown、final reply 係空 → 大肥喵嗰邊收唔到完整早報。
- 補跑 session transcript 見到 agent 寫 `tools.exec({command: ...})` → code mode 入面 `tools` 全域唔存在 → ReferenceError → 空轉到 LLM idle timeout。

### 根因
- 2026-11-10 18:10 修「跨 provider fallback」嗰陣，code-mode 提示（用 `exec(...)` 唔好寫 `tools.exec(...)`）只加咗入**每日健康報告 22:00** 一個 job。
- 其餘 5 個 agentTurn job（早上/中午/傍晚簡報、Audio Sync、Version Check）嘅 message 冇提示 → 一樣會撞 ReferenceError。
- `scripts/cron-guardian.sh` 6 個重建 block 嘅 message 模板亦冇提示 → 即使補咗 job，guardian 重建都會帶返舊 message（同一類「唔改模板就會復發」陷阱）。

### 修復
1. 5 個 job 補提示：`openclaw cron edit <id> --message <原 message + 提示>`（每個 +206 字），連原有健康報告共 6/6 覆蓋。
2. `scripts/cron-guardian.sh` 6 個重建 block（4 個 heredoc message + 2 個 inline message）同步加提示，guardian 重建唔會再丟。
3. 補跑早報：`openclaw cron run 27d54b55-...`（runId cron-request.697522dd-24e8-487a-8c60-d96209dba004）。

### 教訓
- **修 job payload 唔止要改現存 job，仲要同步改重建模板**（guardian / cron_model_guard），否則下次重建復發 —— 同「跨 provider fallback 模板」同一個坑。
- **同一類提示要覆蓋所有同類 job**，唔可以只改出事嗰個。
- 症狀對照：`LLM request timed out.` + final reply 空 + deliveryStatus=unknown → 唔係模型掛，係 agent turn 內部 ReferenceError 空轉到 idle timeout；查 session transcript 睇佢寫咗 `tools.exec` 未。
- cron `deliveryStatus=unknown` 唔代表一定冇送達（09:33 有 outbound send ok），要同時睇 transcript 嘅 final reply 有冇內容。

---

## [2026-11-11] 更新 (v2.9.153) - minimax 單一 account：provider 靜默 = 全線 agentTurn job 冇退路

### 症狀
- 2026-11-11 10:03 Audio Sync 報 `LLM request timed out.`（dur 238299ms）；同日早上簡報補跑亦係 `LLM request timed out.`。
- 實際業務工作正常（直接跑 `scripts/audio_sync_pipeline.py` exit 0，R2 10/10 已在）。

### 根因（runtime 原文 + 本機配置）
- journal：`Profile minimax:cn idle timeout (model silent). No further authorized account for this provider; create a backup auth profile and add its id to auth.order to enable failover.`
- `openclaw.json` → `auth.profiles` 只有 `minimax:cn` 一個 minimax profile（另有 deepseek/openrouter/google/zai，但係**另一個 provider**）。
- 2026-11-10 已確認：有 recorded inference binding 嘅 job **唔可以**用跨 provider fallback（runtime `assertCandidate` 直接 throw）。→ minimax 靜默時冇任何自動退路。

### 教訓
- **同 provider 第二條 account** 先係真後備（runtime 支援 `auth.order` 輪換同 provider profile）；跨 provider fallback 係 fatal 陷阱，兩樣唔可以當成一樣。
- 症狀對照：`LLM request timed out.` + 業務腳本手動跑正常 → 係 provider/account 層面問題，唔係 job 內容問題；先手動驗證業務，唔好亂改 job payload。
- 每日 08:00 起檢查 minimax 429 / idle timeout 數量：>5 次即代表 provider 唔穩，要準備補跑。

---

## [2026-11-11] 更新 (v2.9.154) - push 腳本 auto-stash + reset --hard 會靜靜吞掉未提交內容（Oct 9 夢境失蹤一個月）

### 症狀
- `DREAMS.md` 明明每日 03:00 有產出，但 **2026-10-09 兩篇夢境從來冇出現過喺 git 歷史**（日期序列由 Oct 8 直接跳去 Oct 24）。
- 排查時發現 workspace 有 2 個殘留 stash：`stash@{0}: autostash`（DREAMS.md + finance-news.json）、`stash@{1}: On main: local-test-data-09-19`。

### 根因
- `scripts/git-push-with-lock.sh` / `scripts/batch-push.sh` 嘅 fallback 路徑：`git stash push -u` → `git reset --hard origin/main` → `git stash pop`。
- `git stash pop` 撞衝突時只印一句 warning，改動**留喺 stash**，而 push 腳本唔會再理 → 內容靜靜消失（既喺 HEAD 唔喺工作樹）。
- 每日 03:00 dreaming 寫完 DREAMS.md 未 commit，同分鐘另一個 push 腳本 push 咗 finance/news 資料 → 撞正呢個窗口 → Oct 9 兩篇夢境就係咁樣被吞咗（殘留咗一個月先被巡檢發現）。

### 修復
1. **兩支 push 腳本**：fallback 路徑改成**先 `git add -A` + commit**，只有仍然髒先 stash；`git stash pop` 失敗時自動把 patch 導出到 `backups/stash-recovery/stash-<ts>.patch` 並大聲報告（唔再靜靜吞）。
2. **`scripts/git-health-check.sh`** 新增 `check_stash_leftover()`：偵測到殘留 stash 就報「有 N 個殘留 git stash（改動可能卡住未合併）」，`--fix` 會導出 patch 但**唔自動 drop**（等人確認）。
3. **救援**：由 `stash@{0}:DREAMS.md` 抽返 Oct 9 兩篇夢境，以行級插入（插入位置 = Oct 24 之前最近嘅 `---` 分隔行），並用「抽走插入段 == 原檔」精確驗證零副作用 → 2267 → 2309 行、純 42 行新增，已 commit + push。

### 教訓
- **push 腳本嘅 fallback 唔可以只靠 stash 兜底**：pop 失敗 = 內容靜靜蒸發。要 commit-first + 衝突時導出 patch + 明示警告。
- **每日產生嘅內容檔（DREAMS.md / 記憶檔）必須自己 commit**，唔好假設「遲啲另一個 push 會帶埋」—— 佢哋可能正正就係被嗰個 push 吞。
- 巡檢發現殘留 stash 要當**事故**處理：逐個比對 HEAD 有冇獨有內容 → 有就救返 → 冇先可以 drop。
- 修檔案（尤其長文檔）插入內容要用**行級**操作 + 「抽走插入段 == 原檔」驗證；用 chunk 重序列化會靜靜改格式/刪內容（本次試過：2266 → 2179 行，即刻回滾）。


---

## 2026-11-11 13:20 更新
- **內容**：cron job 全部補上跨 provider fallback chain（deepseek/deepseek-v4-flash → zai/glm-5.3），並修正中午簡報 12:55 timeout 600 → 1800s。
- **根本原因**：`中午簡報 12:55` 12:58 執行失敗 —— `Rate-limit recovery stopped after 9 automatic retries | 429`（lastErrorReason=rate_limit）。所有 OpenClaw cron job 嘅 `payload.fallbacks` 只填咗自己 `minimax/MiniMax-M3.1-Flash@minimax:cn`，等於冇後備 → MiniMax 一限流就直接死。
- **解決方法**：`openclaw cron edit <id> --fallbacks "deepseek/deepseek-v4-flash,zai/glm-5.3" --timeout-seconds N`；N 沿用原本值（早/晚簡報 3600、健康報告 3600、Audio Sync 1800、中午簡報 1800、版本檢查 600），唔好亂改大 job 嘅 timeout。
- **新教訓**：設定 fallback 一定要用**唔同 provider**（deepseek / zai 都有獨立 auth profile）；填返同一個 minimax model 等於冇填。fallback 鏈順序：先 deepseek（快、穩），後 zai。

---

## [2026-11-11] 更新 (v2.9.156) - 補上 v2.9.155 嘅遺漏：deepseek/zai 其實都係死路，真正可用嘅係 openrouter；+ `cron edit` 會偷改 timeout

### 對 v2.9.155 嘅更正
- v2.9.155 話「跨 provider fallback（deepseek → zai）」已經修好 —— **只係修咗一半**。實測 `openclaw models list`：
  - `deepseek` → `Model discovery authentication was rejected for deepseek`（認證被拒，deepseek 根本跑唔到）
  - `zai` → `Configured model "zai/glm-5v-turbo" is not present in the provider's last successful server catalog`（目錄 stale）
  - `google` → `Model discovery is unavailable for google (profile google:default)`
  - **只有 openrouter 5 個 free 模型係 `Auth: yes`**（`nemotron-3-nano-omni-30b-a3b-reasoning:free`、`north-mini-code:free`、`nemotron-3-ultra-550b-a55b:free`、`laguna-s-2.1:free`、`flint-v1.0:free`）
- 結論：v2.9.155 落嘅 `deepseek,zai` 兩條 = **假 fallback**（有填但跑唔到），429 時一樣會死。

### 最終修復
- 每個 agent job 嘅 `fallbacks` = `[deepseek, zai, + 5 個 openrouter free]`（保留舊嘅喺前面 + openrouter 做實體安全網）→ 每 job **7 層 fallback**。
- 修正後：7 個 agent job 全部 `consecutiveErrors=0`、`lastRunStatus=ok`、零重複、零「fallback == primary」。

### ⚠️ 三個必知陷阱
1. **`openclaw cron edit` 會偷改 `timeoutSeconds`**：只傳 `--fallbacks` 而唔傳 `--timeout-seconds`，原本 3600 嘅 job 會被改成 **1800**（CLI 預設值）。**每次 edit 都要顯式帶原 timeout**，並在 edit 後 `cron get` 核實。
2. **`--fallbacks` 格式係逗號分隔 CSV**（唔係 JSON array）。
3. **`automations` 工具喺 Code Mode 壞咗**：`get` / `update` / `list` 全部回 `Tool "automations" returned details that do not match its declared outputSchema`（要求 `id`/`name`/`enabled`/`createdAtMs`… 但回傳唔啱），**side effect 不會發生**。改用 `openclaw cron list --json` / `cron get` / `cron edit` CLI，並且 edit 後一定要再 get 核實。

### 驗證 fallback 真係可用嘅方法
- 唔好淨係睇「有冇填落個欄」→ **睇 `openclaw models list` 嘅 `Auth` 欄**（`yes` 先算真係有憑證）。
- 已用 `Auth: yes` 嘅 5 個 openrouter free 模型做跨 provider 安全網。

---

## [2026-11-11] 更新 (v2.9.157) - 兩個「待辦決策」其實唔存在問題，結案（避免重複問用戶 / 重複報告）

### ① 「簡報雙軌 dedup」→ 已於 2026-11-01 退役，唔係待決事項
- crontab 第 7 / 11 行明確註記：**2026-11-01 大肥喵指令退休：system cron 簡報（`send-briefing.sh` 08:15 / 17:55）已退役**，天氣/交通 digest 已併入 OpenClaw cron agent 簡報（08:15 / 12:55 / 17:55），每個時段得一條訊息。**勿啟用，勿由 guardian 加返。**
- 兩條條目都已 `#` 註釋；`scripts/send-briefing.sh` 檔案仍留喺度（mtime Nov 1 18:13）但**唔會被執行**。
- MEMORY.md 已有呢條退休記錄。**唔好再報告「雙軌簡報」問題、唔好再問用戶揀方案。**

### ② 「Audio Sync / legacy mp3 處理」→ 實測無 legacy 檔，唔使處理
- `scripts/audio_sync_pipeline.py` 嘅匹配正則係 `chapter-\d+\.mp3`（掃 Dropbox `/萬古塵埃/`）。
- 實測 Dropbox 根層：`mp3 總數 10`（chapter-71 ~ chapter-76 等）、**script 會 match 10 個、會被跳過 0 個** → 冇命名唔合規嘅檔。
- 根層其餘 12 項係卷資料夾（第一卷 ~ 第十一卷）同 `韓立sound.WAV`（唔屬章節 mp3，唔應該處理）。
- R2 線上實測 `https://audio.kofhk.com/audio/chapter-71..76.mp3` 全部 **HTTP/2 200**。
- 本機 repo 內 `*.mp3` 數量 = 0（mp3 住喺 Dropbox + R2，唔入 git，正常）。
- Audio Sync cron job `23533480`（每日 10:00）最近一次 11-11 10:07 `status=ok / delivered / errs=0`。
- 註：MEMORY.md 第 16 條「Pipeline filename convention 要一致（`-final.mp3` 教訓）」係指**生成時**命名要一致，唔係指現存 legacy 檔待清。

### 教訓
- **待辦清單嘅「要用戶決定」唔一定真係要決定**：先查 crontab / 實測現況，確認係「已退役」「唔存在」定「真係要揀」，先好去問用戶。浪費用戶注意力同時間。
- **診斷查現況時，判斷式要同被診斷嘅 script 一致**：我第一次用 `name[:-4].isdigit()` 當「標準命名」，但 script 用嘅係 `re.match(r'chapter-\d+\.mp3')` → 10 個全部被誤報為「非標準」，差啲寫錯結論落 MEMORY.md。

---

## [2026-11-11] 更新 (v2.9.158) - fallback 鏈**次序**同樣重要：openrouter 必須排喺 deepseek/zai 前面

### 補 v2.9.156 / v2.9.157 未覆蓋嘅一環
- v2.9.156 補咗「邊啲 fallback 真係可用」，v2.9.157 結案咗兩個待決項 —— 但**兩者都冇處理 fallback 鏈嘅次序**。
- 原次序係 `[deepseek/deepseek-v4-flash, zai/glm-5.3, openrouter×5]`（deepseek/zai 在前）。既然實測 **deepseek 認證被拒絕、zai 目錄 stale**，呢兩個排頭就等于「每次回退先撞兩堵死牆」→ 可能未輪到 openrouter 就已經耗盡重試。

### 最終正確次序
```
fallbacks = [
  openrouter/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free,   # 實測 Auth: yes
  openrouter/cohere/north-mini-code:free,                            # 實測 Auth: yes
  openrouter/nvidia/nemotron-3-ultra-550b-a55b:free,                 # 實測 Auth: yes
  openrouter/poolside/laguna-s-2.1:free,                             # 實測 Auth: yes
  openrouter/recursive/flint-v1.0:free,                              # 實測 Auth: yes
  deepseek/deepseek-v4-flash,   # 保留但排後（認證被拒，機會用唔到）
  zai/glm-5.3,                   # 保留但排後（目錄 stale）
]
```
- 7 個 agent job 全部：**首個 fallback = openrouter**、`model` 不在 fallback 內、零重複、timeout 全部原值。

### 教訓
- **fallback 鏈唔止要睇「有冇填」，仲要睇「次序」** —— 死路排喺前面，等於喺背後擺好嘅安全網被自己擋住。
- **`openclaw cron edit` 係逐個 job 一次過 patch**：7 個 job 逐個跑需要時間，exec timeout 唔夠時會**只改咗一部分** → 一定要喺 edit 後**逐個 job 再 list 一次核實首個 fallback**，唔好假設全部改齊（本次就係咁：第一次只改好 4 個，補做先齊）。

---

## [2026-11-11] 更新 (v2.9.159) - `batch-push.sh` 只睇 working tree 就早退 → commit 永遠留喺本地唔 push

### 症狀
- 2026-11-11 16:17 心跳巡檢發現：**有 1 個未推送 commit**（`953c4d66c` `docs: update finance data 2026-11-11 16:00`），工作樹乾淨、HEAD 正常。
- `git-health-check.sh` 同步報「⚠️ 有 1 個未推送的 commit」。

### 根因
- `scripts/batch-push.sh` Step 3 只判斷 **working tree**：
  ```bash
  if [[ -z $(git status --porcelain) ]]; then echo "📭 無變更需要推送"; exit 0; fi
  ```
- 但 `scripts/update_finance.sh` / `update_finance_news.sh` 嘅流程係：先用 `scripts/git-commit-locked.sh <file> <msg>` **commit 咗**，之後先叫 `batch-push.sh`。
- 所以到 `batch-push.sh` 行到 Step 3 時，改動**已經被 commit 咗** → working tree 乾淨 → 腳本誤判「無變更」→ **早退，commit 永遠留喺本地**。
- 16:00 嗰次完整 log 實锤：`[main 953c4d66c] docs: update finance data...` → `🕐 偶數整點，執行批次推送` → `📭 無變更需要推送` → `🔓 Git Push 鎖已釋放`（**由頭到尾冇 push**）。
- 補充：`git-push-with-lock.sh` 冇同款 bug（佢唔會因樹乾淨而早退，Step 5 一定會 push）。

### 修復
- `batch-push.sh` Step 3 改為 **working tree + 未推送 commit 雙重判斷**：
  ```bash
  git fetch origin main --quiet 2>/dev/null || true
  UNPUSHED=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)
  if [[ -z $(git status --porcelain) ]] && [ "$UNPUSHED" -eq 0 ]; then ... exit 0; fi
  if [[ -z $(git status --porcelain) ]] && [ "$UNPUSHED" -gt 0 ]; then
      echo "  📤 工作樹乾淨但有 $UNPUSHED 個未推送 commit → 繼續推送（唔可以早退）"
  fi
  ```

### 教訓
- **「工作樹乾淨」≠「冇嘢要推」**：已經 commit 但未 push，兩者係唔同狀態。判斷要推唔推，一定要睇 `git rev-list --count origin/main..HEAD`，唔可以淨睇 `git status --porcelain`。
- **凡是「先 commit、之後叫 push 腳本」嘅流程，push 腳本就必須查未推送 commit** —— 呢個分工模式好易令人寫出錯判斷。
- 巡檢要同時睇 `git log origin/main..HEAD` 同 `git status --short`；只用後者會漏。
- **`git fetch` 要喺數之前做**，唔係 `origin/main` 本地 ref 舊咗就會數錯（以為有未推送 commit，其實已推）。

---

## [2026-11-11] 更新 (v2.9.160) - 修復驗證（沙盒精確重現 + 真實流程測試）

### 驗證方法（可重用）
1. **真實流程測試**：用 `git-commit-locked.sh` 先 commit（模擬 `update_finance.sh` 嘅做法），再叫 `batch-push.sh` → 觀察到佢正常 push ✅
2. **沙盒精確重現**（關鍵場景：樹乾淨 + 有未推送 commit）：
   ```bash
   T=/tmp/bp-test; rm -rf $T; mkdir -p $T
   git init --bare $T/origin.git -q; git clone -q $T/origin.git $T/ws
   cd $T/ws; git config user.email t@t.local; git config user.name tester
   mkdir -p scripts; echo hi > a.txt; git add -A; git commit -qm first
   git branch -M main; git push -q -u origin main
   # 複製真實 batch-push.sh 並改 WORKSPACE / LOCKFILE / REPO 指向沙盒
   sed -i "s|^WORKSPACE=.*|WORKSPACE="$T/ws"|" scripts/batch-push.sh
   sed -i "s|^LOCKFILE=.*|LOCKFILE="$T/ws/.git-push.lock"|" scripts/batch-push.sh
   sed -i "s|^REPO=.*|REPO="nonexistent-org/nonexistent-repo"|" scripts/batch-push.sh
   echo second >> a.txt; git add -A; git commit -qm 'second commit (clean tree)'
   bash scripts/batch-push.sh   # 應該推，唔應該早退
   ```
   結果：`🚀 推送中...` → `✅ 已推送到 GitHub`，遠端 `a6d0fd4..9b1ef13` ✅（修復前同一場景會印 `📭 無變更需要推送` 早退）。

### 補充驗證陷阱
- **唔可以直接喺真實 workspace 測「乾淨樹 + 未推送 commit」**：一 commit 就即刻被 push，測唔到；要靠沙盒先重現到。
- 沙盒 `git clone` 空 remote 會印 `warning: You appear to have cloned an empty repository.` —— 正常，唔係錯誤。
- 睇遠端有無收到 commit 要用 `git --git-dir=$T/origin.git log`（bare repo 唔能用 `git -C`）。


---

## 2026-11-11 更新
- 修復內容：線上章節數驗證改為加 cache-buster（?v=timestamp）
- 根本原因：CDN edge 持續 serve 舊版 assets/chapters-data.json，普通 fetch 落後 6 章（1860 vs 1866）會被誤判為同步分歧
- 解決方法：cron-guardian.sh 嘅線上章節數檢查加入 cache-buster（?v=$(date +%s)）；驗證線上資源一律帶 cache-buster，唔好淨係睇普通 fetch 結果

---

## [2026-11-11] 更新 (2.9.163) - Skill 副本「漂移」陷阱：bump 完唔跑 sync，四處 md5 就會唔一致

### 症狀（2026-11-11 18:33 巡檢實際遇到）
- 另一個 session 喺 17:57–18:04 將 `novel-site-standards` 由 v2.9.160 bump 到 v2.9.162，並已同步 **Second-brain + Max-backup**。
- 但 **workspace repo 內嘅 `.openclaw/skills/novel-site-standards/SKILL.md` 仍停留 v2.9.160** → 四處 md5 唯一數 = **2**（唔一致）。
- 單靠「版本號一致」會漏；md5 檢查就捉到。

### 修復
- 跑 `scripts/sync_skill_copies.sh` → 四處全部對齊、md5 唯一數 = 1 ✅

### 教訓
- **Bump skill 之後必須即跑 `sync_skill_copies.sh`**：檢查要睇 **md5 唯一數 == 1**（四處：主 skill、workspace `.openclaw/skills/`、Second-brain、Max-backup），唔係淨睇版本號。
- **HEARTBEAT.md 18:00「Skill更新檢查」要同時查版本 + md5**：版本一致但 md5 唔一致 = 有副本漏同步（本次就係咁）。
- 多 session 併發改 skill 時，bump 前先讀主檔當前版本（唔好假設係自己上次嗰個），避免版本號撞車。

