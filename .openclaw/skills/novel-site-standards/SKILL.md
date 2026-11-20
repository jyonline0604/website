---
name: novel-site-standards
description: 小說網站維護、章節更新、HTML修復、推送GitHub前必讀。規範章節標題唯一、日期合理、導航統一、結構驗證等標準流程。
version: 2.9.199
---

>
> 📚 **歷史記錄已分檔**：2026-04～05 嘅逐章批次日誌（CH 列表、境界檢查表）+ **2026-04～09 嘅 dated 更新記錄段落（51 段）**已搬到同目錄 `SKILL_HISTORY.md`（內容一字無刪，標題索引見下）。
> 呢個主檔只保留**操作規則 + 修復經驗 + 近期記錄**。查舊章節批次記錄 → `SKILL_HISTORY.md`。
> ⚠️ 檔案有 **256000 bytes 硬上限**（超過 loader 會 skip 個 skill）——加更新記錄前先 `stat -c%s` 睇大小，超就要再分檔（**2026-11-18 事實**：加咗 2 段更新記錄就爆 256640 bytes，loader 連續 544 次 skip 呢個 skill → 每次加記錄前必查大小）。


---

## 📦 已分檔到 `SKILL_HISTORY.md` 嘅段落索引（51 段，2026-04～09）

- [2026-10-30] 更新 - - 自動修復（git 分歧第 4 次同型）：DREAMS.md 未提交 + CI commit 同時撞埋 → 必須先 commit DREAMS.md，再 `git pull --rebase origin main`，最後 push；巡檢時用 `git fetch` + `lo
- [2026-10-30] 更新 - - 根本原因：chapters.html / index.html / home.html 用 `?v=YYYYMMDD` 日級 cache-buster，Cloudflare edge 同 Service Worker（cache-first）各自快取同一個 key，要等 UT
- [2026-10-30] 更新 - - 修復內容：更正 10-29 / 10-30 健康報告中「system cron send-briefing.sh（08:15/17:55）+ check_openclaw_update.py（11:00）實際冇執行過」嘅誤判；同時定位 logrotate.service 持續
- [2026-07-28] 更新 (v2.9.72) - Audio Sync DAILY_LIMIT=1 + Volume 5 bug fix
- [2026-07-04] 更新 (v2.9.57) - Git Pre-Commit 安全機制 + Git History 掃描器
- [2026-07-03] 更新 (v2.9.56) - 減少 Push 頻率（防止 GitHub Pages build 失敗）
- [2026-07-03] 更新 (v2.9.55) - Git Push Lock 機制（防止多 cron 衝突）
- [2026-05-26] 更新 (v2.9.54) - 網站背景圖清理 + Service Worker 修復
- [2026-05-12] 更新 (v2.9.53) - chapters-data.json 重複條目導致「共549章」
- [2026-05-10] 更新 (v2.9.53) - Dropbox 同步章節未推送問題修復
- [2026-05-08] 更新 (v2.9.47) - chapters.html 隱藏 div 重複腐壞問題修復
- [2026-05-08] 更新 (v2.9.48) - chapters-data.json 重複條目導致顯示525章
- [2026-07-07] 更新 (v2.9.61) - chapters-data.json field name + home.html 未更新 + Cloudflare cache
- [2026-05-04] 更新 (v2.9.57) - update_chapters_simple.py 正則表達式修復
- [2026-05-04] 更新 (v2.9.58) - 章節標題顯示修復（BOM + · 前綴）
- [2026-05-04] 更新 (v2.9.59) - CH410, CH412-CH420 修真內容置換
- [2026-05-04] 更新 (v2.9.60) - CH401-CH411 修真內容替換（第二批）
- [2026-05-04] 更新 (v2.9.61) - 修復章節目錄顯示問題
- [2026-05-04] 更新 - 章節 351-440 更新
- [2026-05-05] 更新 (v2.9.64) - home.html 章節標題顯示修復
- [2026-05-05] 更新 (v2.9.65) - 強化章節處理檢查清單
- [2026-05-05] 更新 (v2.9.68) - CH472, CH473, CH478 補充上傳
- [2026-05-05] 更新 (v2.9.69) - CH471, CH477, CH479 第四批上傳
- [2026-05-05] 更新 (v2.9.70) - CH491, CH500 第五批上傳
- [2026-05-05] 更新 (v2.9.72) - 500章標題全部唯一
- [2026-05-05] 更新 (v2.9.73) - 章節總數修復（400→500）+ JSON修復
- [2026-05-06] 更新 (v2.9.53) - 首頁章節數量顯示錯誤修復
- [2026-05-06] 更新 (v2.9.55) - CHECKLIST 更新以包含 index.html
- [2026-05-07] 更新 (v2.9.54) - Dropbox 第二卷自動化同步系統
- [2026-05-07] 更新 (v2.9.55) - Dropbox 自動刷新 Token
- [2026-05-08] 更新 (v2.9.48) - chapters-data.json 重複條目問題修復
- [2026-05-16] 更新 (v2.9.53) - 小說名稱修復：科技修真傳 → 萬古塵埃
- [2026-07-05] 更新 (v2.9.58) - 安全防線強化 + Dropbox Token 刷新修復
- [2026-07-05] 更新 (v2.9.59) - 傍晚簡報 isolated cron timeout 修復
- [2026-07-06] 更新 (v2.9.60) - 網站大規模優化 + Dropbox 同步 pipeline 加 Minify step
- [2026-07-08] 更新 (v2.9.62) - chapter-template.html 外部化修復
- [2026-07-11] 更新 (v2.9.63) - handleHash() 降序排序 group 跳頁錯誤
- [2026-07-11] 更新 (v2.9.64) - chapters.html v2 全面重構
- [2026-07-11] 更新 (v2.9.65) - chapters-v2 cache-busting + DOMContentLoaded fix
- [2026-07-11] 更新 (v2.9.66) - 全站升級
- [2026-07-11] 更新 (v2.9.68) - chapters.html UI + 背景圖更換流程
- [2026-07-13] 更新 (v2.9.69) - home.html/index.html UI 雙重時鐘 + 日期計算錯誤修復
- [2026-07-17] 更新 (v2.9.70) - OpenRouter Free Model Fallback 全面修復
- [2026-07-17] 更新 (v2.9.71) - Chapter 7 Audio 修復 + Script Filename Bug
- [2026-09-06] 更新 (v2.9.74) - 簡報 timeout 加固 + 同步腳本假失敗修復
- [2026-09-12] 更新 (v2.9.75) - 補記：Audio Sync fallback 修復（隔離 session 週五執行）
- [2026-09-13] 更新 (v2.9.76) - AQHI push 併發競爭修復
- [2026-09-16] 更新 (v2.9.77) - Volume 6 啟動 + 財經 3-tier fallback + Dropbox token auto-renew
- [2026-09-19] 更新 (v2.9.78) - OpenClaw 2026.9.2 → 2026.9.5 + Node 升級教訓
- [2026-09-19] 更新 (v2.9.77) - OpenClaw 2026.9.5 更新完成（外部修復代理）
- [2026-09-20] 更新 (v2.9.78) - 版本檢查腳本誤報修復
- [2026-09-20] 更新 (v2.9.79) - send-briefing.sh schema 失配修復
- [2026-09-22] 更新 (v2.9.80) - AQHI rebase autostash 完整修復
- [2026-09-22] 更新 (v2.9.81) - AQHI push 重試循環（競賽根治）
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

---

## [2026-11-11] 更新 (v2.9.164) - Code Mode 訊息工具 schema bug：`conversations_list` / `conversations_send` 現時用唔到

### 症狀
- `conversations_list({limit:10})` → 拋 `Tool "conversations_list" returned details that do not match its declared outputSchema ... <root>: must not have additional properties: "gated"`（工具實際有回資料，但 outputSchema 冇 `gated` 欄 → 驗證失敗）。
- 因此攞唔到 `conversationRef`，`conversations_send`（要 `^conv_[a-f0-9]{32}$`）也就用唔到 → **主動發 Telegram 訊息嘅路徑暫時斷咗**。
- 同一類問題：早前 `automations` 工具嘅 `get` / `update` / `list` 全部同樣 outputSchema 驗證失敗（要求 `id`/`name`/`enabled`/`createdAtMs`… 但回傳格式唔啱）；當時改用 `openclaw cron list --json` / `cron get` / `cron edit` CLI 路徑。

### 現時可用嘅替代路徑
- 讀 cron 狀態：`openclaw cron list --json`（CLI，經 exec）；改 cron：`openclaw cron edit <id> --fallbacks <csv> --timeout-seconds <n>`。
- 睇 job / session 實戰結果：`sessions_history` / `sessions_list`（本次用佢確認 17:55 傍晚簡報、22:00 健康報告有冇送達）。
- 查線上資源：`web_fetch`（記得加 cache-buster，見 CDN 快取陷阱嗰條）。
- 一定要改用 CLI 嘅原因：Code Mode 工具回傳格式同 outputSchema 對唔上，**副作用唔會發生**，所以每次都要喺 CLI 層再核實一次。

### 教訓
- **工具報 schema 唔等於工具冇執行**：`automations.update` 報錯嗰次，實際上完全冇生效（fallbacks 冇變）→ 一定要先核實現況再決定重唔重試。
- **Code Mode 入面 `tools.xxx` 唔存在**，只有直接注入嘅全域（`exec`、`read`、`sessions_history`…）；`catalog.search()` 只回 catalog 內嘅 callable，唔保證全域存在。

---

## [2026-11-11] 更新 (v2.9.165) - cron job 說明文字嘅排程時間漂移（健康報告自己報咗出嚟）

### 症狀
- 2026-11-11 22:00 每日健康報告（`a6db95e0`）自己指出：**「財務 / AQHI / 新聞備份 system cron 現時跑 10:00 / 16:00，同 job 說明入面寫嘅 09:00 / 15:00 / 21:00 時間唔一致」**（標註為「非故障」，但係真實文檔漂移）。
- 實際 crontab：`0 10,16 * * *` = `update_finance.sh` / `update_finance_news.sh` / `update_aqhi.sh`；`10 10,16 * * *` = `news-backup-cron.sh`。
- 過時文字出現喺兩個 job 嘅 payload message：
  - `27d54b55` 早上簡報 08:15 → 「…、財經 09/15/21 都係 system cron…」
  - `a6db95e0` 每日健康報告 22:00 → 「…、財經 09/15/21、AQHI 09/15/21、自動記憶 23:00…」

### 修復
- 用 `openclaw cron edit <id> --message <新全文>` 改兩個 job 嘅 payload message：`財經 09/15/21` → `財經 10:00/16:00`、`AQHI 09/15/21` → `AQHI 10:00/16:00`。
- 驗證：8 個 agent job 全部 `09/15/21` 零殘留。

### 教訓
- **排程時間要由 crontab 實測，唔可以靠 job 說明文字** —— 說明文字係人手寫嘅，一定會漂移；寫「09/15/21」嗰陣係 09:00/15:00/21:00，後來 crontab 改成 `0 10,16` 但冇人同步改文字。
- **健康報告自己報出嘅「非故障提示」值得跟** —— 佢標註咗 `[LOOP_STATUS: OK]` 但細節入面嘅唔一致正正就係下一次誤報嘅根源（健康報告會以為 task 唔存在而誤報「消失」）。
- 改 job message 前先 `cron list --json` 取全文、字串精確替換、edit 後再 list 核實 —— 因為 `automations` 工具 schema 壞咗，要用 CLI。

---

## [2026-11-11] 更新 (v2.9.166) - `cron-guardian.sh` 重建模板硬寫自我指向 fallback（令今日修好嘅 bug 會復活）+ 更正「7 層」係錯

### 🔴 症狀：guardian 重建時會重新製造今日嗰個 bug
- `scripts/cron-guardian.sh` 嘅 `rebuild_job()` 函式（6 個 job 分支）**硬寫**：
  ```bash
  --fallbacks "minimax/MiniMax-M3.1-Flash@minimax:cn" \ \
  --model     "minimax/MiniMax-M3.1-Flash@minimax:cn" \
  ```
- `--fallbacks` 同 `--model` **完全一樣** = 自我指向 = 等於冇 fallback。
- **後果**：只要任何一個關鍵 job 走失（例如 Volume 5/6/7 條目曾經「遺失」過），guardian 自動重建時就會用錯鏈，令 **2026-11-11 12:55 中午簡報嗰種「429 → 重試 9 次 → 靜靜冇送達」** 再次發生。
- 即係話：今日手動修 7 個 job 只係治標，**template 唔改就會復發**。

### ✅ 修復
- 喺 guardian 頂部加一個變數（來源：`agents.defaults.model.fallbacks`，同一條鏈）：
  ```bash
  FALLBACKS="openrouter/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free,openrouter/cohere/north-mini-code:free,openrouter/nvidia/nemotron-3-ultra-550b-a55b:free,openrouter/poolside/laguna-s-2.1:free,openrouter/recursive/flint-v1.0:free"
  ```
- 6 個 `--fallbacks` 全部改成 `--fallbacks "$FALLBACKS"`（引號包法抄 `--to "$TELEGRAM_TO"` 同一行，確保 shell 語意一致）。
- `bash -n scripts/cron-guardian.sh` 通過；變數實際展開值已用 `|...|` 包住驗證（無多餘引號）。

### ⚠️ 更正：正確係 **5 層**，唔係 7 層
- 今日 16:xx 我落手時寫過「每 job 7 層 fallback（openrouter×5 + deepseek + zai）」——**錯**。
- 事實：`scripts/cron_model_guard.py` 會按 `agents.*.modelPolicy.allow` 清走唔合政策嘅 fallback，而 allow 清單入面 **deepseek / zai 唔存在**（只有 `minimax/MiniMax-M3.1-Flash` + 5 個 openrouter free + 對應 `@profile` 變體）。
- 所以正確狀態 = **5 層 openrouter**（與 `agents.defaults.model.fallbacks` 完全一致）。guard 清走 deepseek/zai 係**正確行為**，唔係「漂移」。
- 而家 7 個 agent job 全部 = 5 層 openrouter、零重複、`model` 不在 fallback 內 → **合政策且真實可用**。

### 教訓
- **修 job 綁定唔等於修好**：任何「會重建 job 嘅模板」（guardian / setup script / 部署 script）都要一併檢查，否則 bug 會喺下一次 job 走失時原形復現。
- **fallback 唔可以自訂超出 policy allow 清單**：`cron_model_guard.py` 會自動清走，寫落去只會令人誤以為有更多層數。
- **唔好淨睇自己寫過幾多層，要睇 modelPolicy allow 清單同 `openclaw models list` 嘅 `Auth` 欄** —— 三者交集先係真正可用的 fallback 鏈。

---

## [2026-11-12] 更新 (v2.9.167) - 唔可以直接 `source` 有頂層副作用嘅 script（我差啲造出重複 cron job）

### 我自己造成嘅事故
- 測試 `cron-guardian.sh` 重建邏輯時，我用 `source <(sed -n ... scripts/cron-guardian.sh)` 想去抽出 `rebuild_job()` 做 mock 測試 —— 但 `cron-guardian.sh` **頂層有副作用**（第 44 行 `log`、第 49 行 `openclaw cron list`、第 260 行 `for JOB in ... rebuild_job`）。
- 結果：guardian 真係跑咗，並喺 **2026-11-12 00:07:17** 用真 `openclaw cron add` 建立咗一個**重複** job `4209134f-7c03-4b2c-866f-acf551777e99`「中午簡報 12:55」（原本 `66957fcc` 一直好好）。
- **後果**：如果冇巡檢到，明日 12:55 大肥喵會收到**兩份**中午簡報（兩個 job 都 `announce` 去同一個 telegram 5344443732）。
- 已 `openclaw cron rm 4209134f-...` 刪走，驗證：8 個 job、每個名 1 份、errs=0。

### 教訓
- **測試有副作用嘅 shell script：唔可以 `source` 半截**。`sed -n '1,256p'` 一樣會執行頂層代碼（我以為切走咗主流程，但其實唔係）。
- **安全做法**：
  1. 先 `grep -n` 睇清楚邊行係頂層、邊行係 function 定義；
  2. 用 `bash -c` 配合 **mock PATH**（`export PATH=/tmp/mock/bin:$PATH` + 假 `openclaw`），確保唔會真係建立 job；
  3. 或者喺副本上改，唔好 source 原檔。
- **測試前一定要問：呢個 script 嘅頂層會唔會改系統狀態？**（cron job 建立/刪除、檔案寫入、訊息發送）
- **巡檢要偵測「同名重複 job」**：單靠 job id 睇唔到重複，要用 `Counter(name)` —— `cron list` 出現兩個同名「中午簡報 12:55」就要即刻 `rm` 走一個。

---

## [2026-11-12] 更新 (v2.9.168) - mock PATH 攔截唔到 `openclaw`（gateway 嘅 `OPENCLAW_PREPEND_PATH` 排前面）→ 要用 shell function 遮蔽

### 我又撞一次（第二次自揭事故）
- 上條 v2.9.167 講「測試要用 mock PATH」—— **錯一半**。
- 我建咗 `/tmp/gtest5/bin/openclaw` 假執行檔 + `export PATH=/tmp/gtest5/bin:$PATH`，以為會攔截到。
- 實際上 gateway 嘅 shell 預先 `export PATH="${OPENCLAW_PREPEND_PATH}${PATH}"`，**真 `openclaw` 排喺我 mock 前面** → mock 完全冇被呼叫，真 `openclaw cron add` 照跑 → **01:14:50 又造出重複 job `c5e4f531`「中午簡報 12:55」**。
- 已 `openclaw cron rm c5e4f531-...` 刪走，驗證 8 job / 零重複 / errs=0。

### ✅ 正解：shell function 遮蔽（優先過 PATH 執行檔）
```bash
# 三重保護：① 複製 script 去 /tmp（原檔唔郁）② function 遮蔽 openclaw ③ 抽走頂層主流程
cp scripts/cron-guardian.sh /tmp/gsafe3/guardian.sh
openclaw() { echo "CALL: $*" >> /tmp/gsafe3/calls.log; return 0; }   # ★ function 優先過 PATH
eval "$(sed -n '1,42p' /tmp/gsafe3/guardian.sh)"    # vars + log/send_telegram 定義
eval "$(sed -n '73,256p' /tmp/gsafe3/guardian.sh)"  # rebuild_job 函式（唔含頂層主流程）
rebuild_job "中午簡報 12:55"
```
實測結果（mock 成功攔截，零真實 job 建立）：
- `--fallbacks` = 5 層 openrouter（全部 `Auth: yes`、唔含 primary）✅
- `--model` = `minimax/MiniMax-M3.1-Flash@minimax:cn` ✅
- `--timeout-seconds` = 3600 ✅

### 教訓
- **bash 嘅 command lookup 順序：function > alias > PATH 執行檔**。要攔截某個 binary，**用 function 遮蔽最可靠**，改 PATH 唔保證（尤其係有 `OPENCLAW_PREPEND_PATH` / `PREPEND` 嘅環境）。
- **測試前先確認「邊個 executable 會被執行」**：`type -a openclaw` / `command -v openclaw` 睇實際解析順序。
- **抽函式測試要同時抽走頂層主流程**：`sed -n '1,42p'` + `sed -n '73,256p'` 分兩段抽，先至唔會觸發副作用。
- 每次搞掂後都用 `Counter(job name)` 核實**零重複 job** —— 呢個檢查今日已經救咗兩次命。

## [2026-11-12] 更新 (v2.9.169) — 心跳巡檢基建補回 + DREAMS.md 推送競態收尾
- **根因**：`openclaw-selfheal-ops` skill 由開機一直叫人跑 `bash scripts/ops-snapshot.sh`，但 workspace 從來冇呢個檔（`find` 全機 0 命中、git 歷史亦冇）→ 每個 session 都要手砌十幾條一次性巡檢指令，既慢又易漏；同時 `workspace/HEARTBEAT.md` 已經喺 c09442782「cleanup migration artifacts」被刪走，但 `openclaw.json` 嘅 heartbeat prompt 仍然寫「Read HEARTBEAT.md if it exists」→ 心跳等於冇清單，靠記憶自由發揮。
- **修復**：新增 `scripts/ops-snapshot.sh`（唯讀，一次過輸出 gateway 狀態／版本、每個 agent cron job 嘅 errs + fallback 鏈層數、網站 HTTP、workspace git 未推送同髒檔、MEMORY.md 行數、追蹤中敏感檔、Dropbox token 新鮮度、system cron 行數）；重建 `HEARTBEAT.md`（步驟 + 單一 token 回覆規則 + 已知退役清單：system cron 簡報 08:15/17:55、Dropbox Volume 4 同步）。
- **另一個根因**：Memory Dreaming Promotion（03:00）寫 `DREAMS.md` 但唔 commit，加上 GitHub Actions 每日新聞 CI 推 commit，令 `git push` 撞 non-fast-forward（fetch first）→ 已用「先 commit DREAMS.md → `git pull --rebase origin main` → push」收尾，HEAD `93ce46e32`，未推送 0 / 髒檔 0。
- **驗證**：`bash scripts/ops-snapshot.sh` 實跑通過；8 個 agent cron job errs=0、重複名 0、fallback 5 層；網站 HTTP 200；Dropbox token 03:00 續期成功；workspace / Second-brain / Max-backup 三倉未推送 0、髒檔 0。

## [2026-11-12] 更新 (v2.9.170) — AGENTS.md Dropbox cron 表同實際排程對齊
- **根因**：`AGENTS.md` 一直寫住「08:00 | Dropbox第二卷同步6章 | 每天」同「資料夾 /萬古塵埃/第二卷/ (CH501-CH700)」，但實際 system crontab 由來冇過 V2 條目（12 行 active cron 只有 V5 11:00 / V6 11:00 / V7 11:30 / token 每 3 小時），而 `volume2_state.json` 顯示 V2 已處理 CH501-CH675 共 175 章、**無缺口**，CH676 起喺 V3（CH676-CH925）、CH926 起喺 V4（2026-10-02 已退役）。即係話文檔寫住一條唔存在嘅排程 → 令後續 session 以為「V2 同步失蹤」而去亂加 job。
- **修復**：`AGENTS.md` Dropbox 段改為列出現行 12 行 system cron 真實排程，並新增「已完成／已退役嘅卷（唔好復原）」清單（V2 已完成無排程、V3 已完成無排程、V4 大肥喵 2026-10-02 指令退役），資料夾註明實際已處理 CH501-CH675。
- **配套驗證**：`volume2_state.json` 覆蓋 501-675 缺 0；`volume3_state.json` 覆蓋 676-925；V5/V6/V7 最近一次 11-11 同步日誌全部「✅ 同步完成」；Dropbox token 06:00 續期成功；8 個 agent cron job errs=0、重複名 0；網站 HTTP 200；章節 HTML 1866 檔異常 0；workspace / Second-brain / Max-backup 三倉未推送 0、髒檔 0。
- **教訓**：睇 crontab 實況（`crontab -l | grep -v '^[[:space:]]*#'`）再改文檔，唔好信舊文檔；一條「文件寫住但實際冇」嘅排程 = 下次誤判故障 + 可能重複加 job。

## [2026-11-12] 更新 (v2.9.171) — HEARTBEAT.md 補 DREAMS.md 步驟 + 主動訊息工具失效確認
- **背景**：`scripts/ops-snapshot.sh` 同 `HEARTBEAT.md` 喺 04:04 心跳已重建，但 `HEARTBEAT.md` 嘅「三倉一致性」步驟淨係叫你睇未推送／髒檔，冇講明髒檔係 `DREAMS.md`（03:00 Memory Dreaming job 產出、job 唔會自己 commit）嗰陣點處理 → 04:04 心跳就係撞 non-fast-forward，要人手 `git add DREAMS.md && git commit` → `git pull --rebase origin main` → `git push` 先推得上去。
- **修復**：`HEARTBEAT.md` 第 3 步加咗一行明確處理次序（先 commit DREAMS.md → 再 rebase → 再 push），避免下次心跳再撞同一個坑。
- **主動訊息路徑確認**：今日 06:09 再試 `conversations_send`（conversationRef = `conv_f50596d872f67310a70f1d6d020fb453`，delivery target = `telegram:5344443732`），**仍然失敗**：`Validation: status: must have required property 'status'; conversationRef: must have required property 'conversationRef'; channel: must have required property 'channel'; <root>: must not have additional properties: "gated"`（同 2026-11-11 18:45 記錄嘅 bug 同一個，工具多返個 `gated` 欄）。journald 核實**冇任何 telegram 出站記錄** → 即係話經 conversations_send 發嘅訊息實際上冇送達，唔可以當成已通知。**要真係通知大肥喵就必須用本回合嘅 plain assistant reply**（04:07 嗰份巡檢報告就係咁樣送達，transcript 有 `ops-snapshot.sh` 命中）。
- **驗證**：workspace / Second-brain / Max-backup 三倉未推送 0、髒檔 0；8 個 agent cron job errs=0、重複名 0；網站 HTTP 200；章節 HTML 1866 檔異常 0；Dropbox token 06:00 續期成功；無殘留巡檢進程。

## [2026-11-12] 更新 (v2.9.172) — heartbeat 清單搬到 cron-owned scratch（doctor legacy warning 根治）
- **根因**：新版 OpenClaw（2026.11.3）已把 heartbeat 指令搬去 **cron job scratch**（每個 agent 私有），`openclaw doctor --lint --only core/doctor/heartbeat-scratch-migration` 明確報 warning：`Agent "main" still stores heartbeat instructions in HEARTBEAT.md`（path = workspace/HEARTBEAT.md，requirement = legacy-heartbeat-file，fixHint = `openclaw doctor --fix`）。即係話 workspace 根目錄嘅 `HEARTBEAT.md` 已經係 legacy 位——雖然 `openclaw.json` 個 heartbeat prompt 仍然寫「Read HEARTBEAT.md if it exists (workspace context)」，但真正餵畀 lane 嘅係 job scratch（scratch 內容會作為 heartbeat monitor scratch 一齊入 prompt）。
- **修復**：
  1. `HEARTBEAT.md` → **`docs/heartbeat-checklist.md`**（git mv，保留歷史；呢份係版本控制嘅來源）。
  2. 新增 `scripts/sync_heartbeat_scratch.sh`：用 `openclaw cron scratch <jobId> --file <src>` 把清單寫入 heartbeat job `9dc7d6c3-617f-410d-9881-e87453c33037` 嘅 scratch，再 `cmp` 驗證一致。
  3. `AGENTS.md` 心跳段落改指 `docs/heartbeat-checklist.md`，並寫明「唔好再喺 workspace 根目錄放 HEARTBEAT.md」+「改完要跑 sync_heartbeat_scratch.sh」。
- **關鍵 CLI 發現**：`openclaw cron scratch <id>` 有 `--set <text>` 同 `--file <path>`（讀／取代 job 私有 scratch）；而 `openclaw doctor --fix --only <checkId>` 唔 work（`--only` 屬 lint-only 選項，要配 `--lint`；而 `--json` 又唔可以配 `--fix`）→ 正常路徑係先 `doctor --lint --only <checkId> --json` 睇清楚，再用 `openclaw cron scratch --file` 自己寫，唔靠 doctor --fix。
- **驗證**：workspace 根目錄已無 `HEARTBEAT.md`；`openclaw cron scratch 9dc7d6c3...` 讀出 2651 bytes，內容 = 新清單（命中 `ops-snapshot.sh`／`唔會自己 commit` 關鍵字）；`docs/heartbeat-checklist.md` 2651 bytes，兩邊一致。
- **配套**：`conversations_send` 仍然唔送達（outputSchema 多 `gated` 欄，journald 核實冇 telegram 出站）→ 通知大肥喵唯一可靠路徑係 plain assistant reply。

## [2026-11-12] 更新 (v2.9.173) — doctor 巡檢要用 --only，唔好跑 --lint --all（會 hang）
- **症狀**：`openclaw doctor --lint --all --non-interactive --json` 喺呢部機**一定 hang** —— 背景跑 3 次（timeout 200s／240s）輸出檔都係 0 bytes，進程要人手 `pkill -f '[o]penclaw doctor'` 先收得走；同一時間其他 health check（cron／git／HTTP／ops-snapshot）全部正常。
- **對照**：**指定單一 check 就正常快** —— `openclaw doctor --lint --only core/doctor/heartbeat-scratch-migration --non-interactive --json` 幾秒出 `{"ok":true,"findings":[]}`。
- **原因（推測）**：`--all` 會逐個跑 70 個 check，其中某啲要做慢嘅外部查詢（例如 npm registry／plugin capture），喺呢個網絡環境就卡住。
- **修復／新規則**：巡檢一律用 `doctor --lint --only <checkId> --non-interactive --json` 逐個查要關注嘅 check；**唔好**用 `--lint --all`。如果之前跑過，先 `pkill -f '[o]penclaw doctor'` 清殘留再繼續。
- **同時記住**：`doctor --fix --only <checkId>` 用唔到（`--only` 屬 lint-only 選項，要配 `--lint`；而 `--json` 又唔可以配 `--fix`／`--repair`／`--force`）→ 要修就自己用對應 CLI（例如 `openclaw cron scratch <jobId> --file <src>`）手動做，再跑 `--lint --only` 驗證。

## [2026-11-12] 更新 (v2.9.174) — 修正 04:04 嘅錯誤根因：ops-snapshot.sh 一直存在喺 learned skill 內
- **修正**：v2.9.169 嗰條更新記錄寫「`scripts/ops-snapshot.sh` 全機搵唔到、git 歷史亦冇 → 已建立」係**錯嘅**。真相：檔一直存在喺 learned skill 內 —— `~/.openclaw/agents/main/agent/workshop-skills/openclaw-selfheal-ops/scripts/ops-snapshot.sh`（mtime 2026-10-22 13:17）。04:04 嗰陣用 `find /home/openclaw -maxdepth 6 -name 'ops-snapshot.sh'` 搵，**maxdepth 太淺漏咗**（實際深度 8）。
- **真正嘅缺陷**：skill 步驟 2 用相對路徑 `bash scripts/ops-snapshot.sh`（相對 CWD = workspace），但 `workspace/scripts/` 冇呢個檔 → 步驟行唔通；而 skill 內嗰版內容較舊（冇三倉 git 狀態、冇 skill 四處 md5 唯一數、冇 fallback 層數、冇章節數、冇 system cron 行數）。
- **修復**：將兩版合併做一份 **canonical** `workspace/scripts/ops-snapshot.sh`（10 個段落：時間／gateway uptime + stability 記錄／網站 HTTP／cron errs + fallback 層數 + lastRun／近 30 分鐘 provider status／MEMORY.md + memory 目錄／三倉 git + hooks + 敏感檔 + 章節數／skill 四處 md5 唯一數／Dropbox state + token 新鮮度／system cron 行數），並用 `skill_workshop write_file` 寫入 learned skill 令兩邊 **md5 一致**；skill 步驟 2 同步驟 6 改成絕對路徑 `bash /home/openclaw/.openclaw/workspace/scripts/ops-snapshot.sh`。實跑通過（8 job errs=0、重複 0、HTTP 200、三倉 0/0、skill md5 唯一數 1）。
- **教訓**：搵檔案唔好靠 `find -maxdepth` 估深度（用 `find <dir> -name <file>` 唔設 maxdepth 或直接 ls）；SKILL.md 內寫嘅相對路徑一定要核實 CWD 下真係存在，唔好假設「script 唔存在」。

---

## [2026-11-12 08:15] 更新 (v2.9.175) — fallback 必須帶 @profile 綁定，唔可以淨係寫 provider/model
- **症狀**：早上簡報 08:15 job error（errs=1、deliveryStatus=unknown、完全冇送出）：`Automation candidate is incompatible with its recorded inference account and route. The selected model uses a different provider from this job's stored account.`
- **根本原因**：2026-11-11 改 guardian 重建模板時，`scripts/cron-guardian.sh` 嘅 `FALLBACKS=` 被改成**未綁 account** 嘅 openrouter free 鏈（`openrouter/...:free`），7 個 agentTurn job 嘅 `payload.fallbacks` 全部被洗掉 `@profile`；fallback 一旦由 minimax 切去 openrouter 就係跨 provider → runtime 拒絕採用另一個 account → hard-fail（2026-11-10 已踩過同一個坑）。modelPolicy allow 清單一直有綁定變體（`@openrouter:default`），只係 job payload 同模板冇用。
- **解決方法**：(1) `openclaw cron edit <id> --fallbacks <5 條帶 @openrouter:default 嘅鏈> --model minimax/MiniMax-M3.1-Flash@minimax:cn` 重綁全部 agentTurn job，`openclaw cron list --json` 驗證全部 fb_bound=True；(2) `scripts/cron-guardian.sh` 嘅 `FALLBACKS=` 同步加回 `@openrouter:default` 綁定（唔改模板，guardian 重建時會帶返 bug），`bash -n` 語法檢查通過；(3) 實跑 `python3 scripts/check_openclaw_update.py` 刷新停更嘅 `openclaw-version.json`（current 2026.11.1 → 2026.11.3），修好 digest 誤報「有更新可用」。
- **新增教訓**：(a) fallback 值一定要帶 `@profile` 綁定；(b) 改 guardian 重建模板要連 job `payload.fallbacks` 實際值一齊驗，唔可以只睇 allow 清單有綁定變體就當冇事；(c) 版本顯示唔可以淨係信 `openclaw-version.json`，要同 `openclaw --version` + `npm view openclaw version` 對照（2026-11-08 同一教訓復發）。

---

## [2026-11-12 10:40] 更新 (v2.9.176) — sync_skill_copies.sh 嘅 av 路徑寫錯，novel-av-generator 副本從來冇同步過

- **症狀**：心跳巡檢步驟 4「Skill 副本唯一性」要求 novel-site-standards 同 novel-av-generator 四處 md5 唯一數 = 1。實測 novel-av-generator 只有三處（installed / Second-brain / Max-backup），workspace 副本 /home/openclaw/.openclaw/workspace/.openclaw/skills/novel-av-generator/ 根本唔存在；三處 md5 雖然啱啱好一致，但嗰個係手動 copy 出嚟嘅巧合，唔係機制保證。

- **根本原因**：scripts/sync_skill_copies.sh 最後一行寫咗 sync_set av "$AV/SKILL.md" "$SB/../novel-av-generator/SKILL.md" "$MB/../novel-av-generator/SKILL.md" —— $SB 同 $MB 本身已經係 .../skills/novel-site-standards 檔案路徑，再加 /../novel-av-generator/ 會 resolve 去 /home/openclaw/novel-av-generator/SKILL.md（該目錄唔存在，ls 確認 No such file or directory）。即係 nightly（23:20）同步對 av skill 長期無效，cmp 永遠唔 match，cp 失敗但被 >/dev/null 2>&1 吞掉 → 靜默失敗、零告警。

- **解決方法**：(1) 修正路徑為 "$AV/SKILL.md" "$WS_AV/SKILL.md" "$SB/skills/novel-av-generator/SKILL.md" "$MB/skills/novel-av-generator/SKILL.md"，並新增 WS_AV=/home/openclaw/.openclaw/workspace/.openclaw/skills/novel-av-generator；(2) 補建 workspace av 副本（由 installed 版複製）；(3) bash -n 語法檢查通過 + 實跑 sync_skill_copies.sh 驗證四處 md5 唯一數 = 1。

- **教訓**：腳本入面嘅路徑要 ls 過確認存在先算數，唔好靠肉眼睇 .. 睇落合理；cp >/dev/null 2>&1 會將路徑錯誤變成靜默失敗 —— 同步類腳本至少要目標存在性檢查。四處唯一性檢查要逐個 skill 分開數（今次就係淨查咗 standards 漏咗 av）。

---

## [2026-11-12 10:50] 更新 (v2.9.177) — ops-snapshot.sh 第 8 段改為逐個 skill 檢查四處 md5（原本只查 standards，令 av 漂移長期無人察覺）
- **症狀**：v2.9.176 修好 `novel-av-generator` 四處副本之後，追查「點解 av 副本會缺失咁耐先有人察覺」—— 發現巡檢工具本身有盲點。
- **根本原因**：`scripts/ops-snapshot.sh` 第 8 段「Skill 副本唯一性」**只硬編碼 `novel-site-standards` 一個 skill**（`SK=...novel-site-standards/SKILL.md` + 3 個固定路徑），而心跳清單 `docs/heartbeat-checklist.md` 步驟 4 要求查**兩個** skill（`novel-site-standards` 同 `novel-av-generator`）。即係話清單要求嘅嘢，工具做唔到 —— 每次心跳睇到 standards 唯一數 = 1 就當步驟 4 完成咗，`novel-av-generator` 少咗 workspace 副本（實際只有 3/4 處）**長期無人察覺**，nightly 同步又因為路徑 bug 靜默失敗，兩者疊加就冇人發現。
- **解決方法**：重寫 `scripts/ops-snapshot.sh` 第 8 段 → 新增 `check_skill()` 函式，逐個 skill（`novel-site-standards` 同 `novel-av-generator`）獨立列出四處 md5、計算「存在 N/4 處」同「唯一 md5 數」，任何一個唔滿足（存在 ≠ 4 或唯一數 ≠ 1）就印 `⚠️ <skill> 副本缺失或漂移！`；缺失檔案會明示 `MISSING <path>`（原本只 `md5sum` 存在嘅檔，缺失會被靜默略過）。實跑結果：兩個 skill 都係 **4/4 處、唯一 md5 數 1** ✅。
- **同步**：已用 `skill_workshop write_file` 寫入 learned skill `openclaw-selfheal-ops` 嘅 `scripts/ops-snapshot.sh`，兩邊 md5 一致 = `6b4da253ad395be07c8f19a3b2b089d4`。
- **教訓**：**巡檢清單要求同巡檢工具能力要對齊** —— 清單寫咗要查兩個 skill，但工具只查一個，就等於個一項長期失效；寫清單時要同時確認工具真的做到（否則就係「假綠」）。另外，檢查工具對「檔案缺失」要顯式標示，唔可以靠 `md5sum` 存在檔靜默略過 —— 咁樣會令「少咗一份」睇落同「全部一致」一樣。

---

## [2026-11-12] 更新 (v2.9.178) - GitHub Pages build 失敗（GitHub 側事故）+ artifact 瘦身 + 失敗自動 rerun

### 修復內容
- **症狀**：2026-11-12 早上收到 email alert「[jyonline0604/website] Run failed: pages build and deployment - main (8b880a7)」。run #18536（id 43095077027，2026-11-11T20:17:18Z）job 130781703711 死喺 Step 3「Upload artifact」，build 階段跑咗 10 分 39 秒。
- **真正根因（唔關 repo 事）**：tarball 其實成功建立（6258 個檔案全列出），係 upload 去 GitHub artifact API 時 GitHub 回咗 **HTML 錯誤頁而唔係 JSON** → `Failed to CreateArtifact: Failed to make request after 5 attempts: Unexpected token '<', "<!DOCTYPE "... is not valid JSON`。GitHub 官方 status 同期有 critical 事故「Impact across multiple GitHub products including Actions, Pages, and Copilot products」20:48→21:21 UTC ＋「Incident with Webhooks」20:22→20:26，同時間窗完全對得上。另外 #18437（11-10）、#18393（11-07）兩次死喺 deploy job「Timeout reached, aborting!」（syncing_files 階段），同屬 GitHub 側 deploy timeout。
- **線上實況無受影響**：kofhk.com HTTP 200、worker `/api/status` → chapters 1872、線上 chapters-data.json 正常、chapter-1 / chapter-1000 / chapter-1872 / sitemap.xml 全部可讀；事故後所有 pages run 全綠。
- **加固 1（artifact 瘦身）**：repo 有兩坨**唔係網站內容**嘅目錄被 track 住 → 每次 Pages build 都要 upload：`graphify-out/`（2284 檔 28.1 MB）＋ `.dropbox-sync/downloaded/`（1372 檔 14.9 MB）。已 `git rm -r --cached`（**本地檔案保留**）＋ .gitignore 加規則（防止其他 script 嘅 `git add -A` 加返）→ 追蹤檔案 6230 → 2574、artifact 102.3 MB → 約 59 MB，直接減少 upload 失敗同 deploy timeout 機會。已確認網站 HTML 無引用呢兩個目錄（grep 全站 HTML = 0）。
- **加固 2（失敗自動 rerun）**：新增 `scripts/pages_deploy_recovery.py` + crontab 每小時 :25 自動執行 —— 偵測到 Pages build 失敗就自動 `POST /actions/runs/<id>/rerun`。
- **驗證**：commit `7c01a946321ab957e33c2c1f11ee05ab415ab0e2` 已 push（local main == origin/main）；新 build **#18564**（同一 sha，瘦身後）**success** ✅；復原腳本已喺 origin/main（raw.githubusercontent 實讀確認 5 項守欄齊全）；復原腳本實跑一次 → 正確辨識 #18536 並按護欄「唔 rerun」。

### 教訓
- **Pages workflow 係 GitHub 自動生成（`path=dynamic/pages/pages-build-deployment`）**：唔喺 repo 入面所以根本改唔到，只能靠 API rerun。而且 `GET /actions/workflows/<name>/runs` 對佢會回 **404**（因為佢唔係檔案式 workflow），要改用通用 `GET /actions/runs?per_page=N` 再按 `name == "pages build and deployment"` 篩選 —— 呢個 API 端點差異係自己第一次寫腳本時踩到（log 顯示首次實跑 404，修正後正常）。
- **job log 要用 basic auth 先攞到**：`curl -u "x-access-token:PAT"`（用 Bearer 會 401 Bad credentials），係診斷 GitHub Actions 失敗嘅前提。
- **artifact 瘦身係防禦 GitHub 側 timeout 嘅實質手段**：6230 檔 / 102 MB → 2574 檔 / 59 MB，upload 同 syncing_files 都快好多。追蹤嘅嘢唔等於網站要公開嘅嘢 —— 開發快取（graphify-out）同 Dropbox 下載快取（.dropbox-sync/downloaded）都唔應該入 Pages artifact。
- **自動 rerun 一定要有護欄，唔可以無腦重跑**：只 rerun `head_sha == 現時 origin/main HEAD` 嘅失敗 run（避免部署舊內容令網站章節倒退）＋ 線上章節數 < 本地先 rerun ＋ 每個 run 最多 2 次 ＋ always exit 0（唔好令 cron 報錯）。
- **「部署失敗」唔等於「網站壞咗」**：GitHub 側事故期間線上照舊正常，唔好因為 email alert 就亂改網站內容；先睇 job log 同 status.github.com 判定係邊邊責任。
- **一個 duplicate log entry 會令成個 config 讀取中斷**：11-01 logrotate 事故同源 —— 唔止影響嗰個檔案，所有 log 都不輪轉，要當 P1 睇。

---

## [2026-11-12] 更新 (v2.9.179) - Volume 7 同步 log 檔名寫錯（guardian 模板 + 中午/傍晚簡報 job message）

### 問題描述
- `scripts/cron-guardian.sh` 第 140、182 行（guardian 內置嘅「中午簡報 / 傍晚簡報」重建模板）寫住要 tail **`dropbox-volume7-daily-sync.log`**
- 但 crontab 真正嘅 redirect 目標係 **`logs/dropbox-volume7-sync.log`**（`dropbox-volume7-daily-sync.log` 係**腳本名**，唔係 log 名）
- 結果：中午簡報 12:55 / 傍晚簡報 17:55 兩個 job 每次都 `tail` 一個**從來冇存在過**嘅檔 → 讀到 V7 同步狀態嘅步驟永遠失敗（`tail: cannot open ... No such file or directory`），兩個簡報實際上**睇唔到 V7 同步結果**
- 同一個錯名亦出現喺兩條 cron job 嘅 payload message（`66957fcc` 中午簡報、`f8b447b6` 傍晚簡報）—— 就算手改 template，job 自己嘅 message 仲係錯

### 根因
- 2026-10-22 建立 V7 排程時，**腳本檔名**（`dropbox-volume7-daily-sync.sh`）同 **log 檔名**（`dropbox-volume7-sync.log`）命名唔一致；模板寫 log 時直接用咗腳本名，冇對過 crontab 實際 redirect 行
- 錯名一直「冇爆」：V7 同步本身正常（11:30 跑、6 章上限、state 正常），錯嘅只係**簡報嘅觀測路徑**——所以每日健康報告巡檢都見唔到（因為當時冇人 tail 嗰個名）

### 修復
1. `scripts/cron-guardian.sh`：兩處 `dropbox-volume7-daily-sync.log` → `dropbox-volume7-sync.log`（sed 精準替換，只改 log 名，唔動 `dropbox-volume7-daily-sync.sh` 腳本名同 `DROPBOX_CRON` 模板行）；`bash -n` 語法檢查通過、executable bit 保留（100755）
2. 兩條 cron job message 用 `openclaw cron edit <id> --message <改後全文>` 精準替換（同樣只換 log 名，其餘 payload 一字唔改）；事後 `openclaw cron list --json` 逐項核對：schedule / model / fallbacks(5) / delivery / timeout / enabled 全部同改動前一致 ✅

### 教訓
- **寫 log 檔名要對 crontab 實際 redirect 行，唔可以由腳本名推導** —— 兩者唔一定同名（V5/V6 就係腳本 `dropbox-volume{5,6}-daily-sync.sh` → log `dropbox-volume{5,6}-sync.log`）
- **模板錯名要同 job 自身 message 一齊修**：guardian 只會喺 job「缺失」時先重建，job 存在就唔會覆寫 message → 單改模板唔夠
- **`tail` 一個唔存在嘅 log 唔會令 job 失敗**（exit code 有 `|| true` 或容錯）→ 簡報會靜靜「睇唔到」某個同步狀態而照樣報綠。巡檢要主動核對「命令入面嘅路徑」真係存在，唔可以只睇 job status=ok
- 教訓同一類：**觀測路徑失效 = 假綠**（同 2026-11-12 10:50 巡檢工具盲點、21:03 裸 URL CDN 快取兩單同源）

---

## [2026-11-12 22:40] 更新 (v2.9.180) — 每日健康報告 22:00 job 改用單一腳本入口（治 tools.exec ReferenceError 由 5 分拖到 21 分）
- **症狀**：2026-11-12 22:00 嘅健康報告 job 用咗 **21 分鐘**（平時 5 分鐘）先完成，但最後仍然成功交付（Telegram messageId=23505，22:20:53）。慢嘅原因唔係 job 壞，而係 code mode 內反覆寫錯 API。
- **根本原因**：journalctl 顯示該 run 撞咗 **3 次** `ReferenceError: tools is not defined`（code mode 只注入直接注入嘅全域，`tools.exec(...)` 呢個寫法根本唔存在 → 每次都要重試），再加上 minimax **2 次 429**（其中一次 `elapsedMs=89767`，即係等咗 90 秒）。今日全機共 7 次 `tools is not defined`，分佈喺 6 個 cron job（健康報告 3、中午簡報 1、其餘 3）。**舊 message 已經有「唔好寫 tools.exec(...)」嘅警告，但模型照寫 —— 靠文字警告冇用，要減少 code mode 嘅呼叫次數。**
- **解決方法**：(1) 新建 `scripts/health_report.sh` —— 單一入口，一次過做齊：① 現況快照（直接叫 `scripts/ops-snapshot.sh`）② 自動修復（三倉未推送 commit → pull --rebase + push；`DREAMS.md` → commit + push（唔係刪）；untracked 暫存檔 `*_output.txt` / `*.tmp` / `cron_output.txt` → rm）③ 判定（輸出 `[LOOP_STATUS: OK|WARN|FAIL]` 同 `[LOOP_DAILY: ...]`，並列出 consecutiveErrors > 0 嘅 job）。實跑 rc=0、68 行輸出、判定正確（HTTP=200 / disk=16% / mem 3398M/7172M / cron_errs=0 / token_age=92min）。(2) `openclaw cron edit a6db95e0 --message <新訊息>` —— 新 message 只叫 agent 做**一次** exec：`exec({command: "bash /home/openclaw/.openclaw/workspace/scripts/health_report.sh"})`，之後只負責整理輸出同交付。(3) `scripts/cron-guardian.sh` 模板同步改（重建時唔會還原舊 message），並驗證模板抽出嘅 message 與 live job **byte-identical（1070 bytes）**、無反引號／`$(`／`EOF` 危險字元、`bash -n` 通過。
- **驗證**：`cron edit` 後逐項比對 payload —— `model` / `fallbacks`（5 層，**全部帶 `@openrouter:default` 綁定**）/ `inferenceBinding` / `timeoutSeconds` / `toolsAllow` / `delivery` / `schedule` / `agentId` / `sessionTarget` / `enabled` / `name` / `description` **13 項全部 SAME**，只有 `message` 改變（避免重演 2026-11-12 08:15 嘅 fallback 綁定被洗掉事故）。
- **教訓**：(a) **靠 prompt 文字警告模型唔會聽 —— 要用結構減少犯錯機會**；同一個「唔好寫 tools.exec」警告喺多個 job message 存在咗仍然每日被犯 7 次。(b) cron job message 越簡單、code mode 呼叫越少，就越少撞 ReferenceError 同 429（429 一等就等 90 秒，直接拖慢個 run）。(c) 改 cron job message 前後**必須逐項 diff payload**（尤其 fallback 嘅 `@profile` 綁定同 `inferenceBinding`），唔可以只睇 `cron list` 一眼就算。(d) 改 live job 之後**同步改 guardian 模板**，否則下次重建就會還原；並用「由模板抽出 message 同 live job 比對」嚟驗證兩邊一致。

## [2026-11-13 19:30] 更新 (v2.9.181) — 跨 provider fallback 死鏈：5 個 isolated cron job 全日被 billing 打死的根因修復
- **症狀**：2026-11-13 由 00:04 到 17:55，5 個 isolated agentTurn job（早上簡報 08:15、Audio Sync 10:00、Version Check 11:00、中午簡報 12:55、傍晚簡報 17:55）全部 consecutiveErrors=1、lastRunStatus=error，三個時段嘅簡報全部失投；job error 訊息係 `Automation candidate is incompatible with its recorded inference account and route`（睇落似 account 綁錯，實際係**每一條 fallback 都被拒絕**）。
- **根本原因**：① MiniMax API 全日回 **402 `insufficient_balance_error`**（餘額耗盡，journal 76 次 402、profile `minimax:cn`），primary 一死 runtime 就轉 fallback；② 但 7 個 job 每個都記錄咗 `inferenceBinding.provider=minimax`，runtime `assertCandidate()` 一比較 `provider !== binding.provider` 就 throw → 5 條 openrouter fallback **全部被逐一拒絕**，所以「有 fallback」實際等於冇 fallback；③ 同一時間 `openrouter/poolside/laguna-s-2.1:free` 已被 OpenRouter 下架（HTTP 404），鏈內有死模型。
- **解決方法**：① 7 個 isolated agentTurn job 改用 OpenRouter free primary（`openrouter/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free@openrouter:default`）+ 同 provider 3 層 fallback（ultra-550b → north-mini-code → flint），每個 job 用 `cron edit` **帶齊** model / fallbacks / timeout-seconds / message / tools（漏帶會被重設成預設值）；② 由 6 個位清走退役嘅 `poolside/laguna-s-2.1:free`（defaults.fallbacks / 兩份 modelPolicy.allow / defaults.models / job payload.fallbacks / guardian 模板）；③ `scripts/cron_model_guard.py` 改成喺**同一 provider 內**修鏈 + 去掉自我指向（原本 fallback 修復分支會把 primary 重綁返 minimax，令死鏈復活）；④ `scripts/cron-guardian.sh` 模板同步（`--model` × 6 + `FALLBACKS`）。
- **驗證**：Version Check（19:23）、Audio Sync（19:26）、傍晚簡報（19:29）三個 job 用新鏈實跑全部 status=ok、provider=openrouter，傍晚簡報正常交付；`bash -n scripts/cron-guardian.sh` 通過；`python3 scripts/cron_model_guard.py` → "OK: every job model override is within policy allow list"；逐 job 核對 message / timeoutSeconds / toolsAllow / fallback 數目冇被覆寫。
- **教訓**：(a) **「有 fallback」唔等於「fallback 用得著」** —— 2026.11 每個 job 記錄 inference account，跨 provider fallback 會被逐一拒絕；chain 必須同一 provider + 同一 `@profile`，而且唔可以重複 primary。(b) **`cron edit --clear-model` 唔會清走 recorded binding**，改 provider 要靠 `--model <provider/model>@<profile>`。(c) **provider 層故障會喺 job 層放大**（minimax 402 → 5 個 job 全死 + 全日簡報失投）；修鏈要 job payload 同 guardian 模板一齊改（MEMORY 教訓 26）。(d) 巡檢要睇**同一個 provider 內**嘅候選鏈有幾多條、每條係咪真實 call 得到，唔可以只數 fallback 層數。

## [2026-11-13 23:55] 更新 (v2.9.182) — 22:00 健康報告假綠（模型捏造數字）→ 腳本 --deliver 結構性收口 + a6db95e0 自我指向 fallback 修正
- **症狀**：2026-11-13 22:00 嘅健康報告 job 交付咗一份**內容全部捏造**嘅報告（Telegram 22:00:31 delivered）：寫「MEMORY.md 1234 行／章節數 56／Cron job 錯誤 0 個／三倉髒檔 0／System cron 15 行」並將 `[LOOP_STATUS: FAIL]` 改成 `[LOOP_STATUS: OK]`。實際值（ops-snapshot 實測）：MEMORY.md **513 行**、章節 **1878**、cron errs **2**、system cron **13** 行、`[LOOP_STATUS: FAIL]`。
- **根本原因**：舊 job message 要求模型「讀 exec 輸出 → **整理成健康報告** → 交付 Telegram」。該 job 當時跑喺 openrouter `nemotron-3-nano-omni-30b-a3b-reasoning:free`（弱模型），佢冇照抄腳本 stdout 而係自己「整理」出另一組數字 → 弱模型做匯總／改寫就會捏造。健康報告最需要可信，卻最經模型轉述。
- **解決方法**：① `scripts/health_report.sh` 新增 `--deliver` 模式 —— stdout **只輸出最終報告**，所有數字由腳本自己實測（script 唔做推理），詳細快照另寫入 `logs/health_report-YYYY-MM-DD.log`；② `scripts/cron-guardian.sh` 重建模板嘅 22:00 job message 改成「**只做一次 exec** 跑 `health_report.sh --deliver`，將 stdout **逐字原樣**交付，唔好重新整理／改寫數字／自己加推斷／漏兩行 LOOP_*」；③ job message 明文記低今日案例，防止日後改返做「整理」。④ 同一晚 `a6db95e0` 改 message 時把 primary 塞返入自己 fallback 鏈（fb 3→4、SELFREF=True = 自我指向零回退），已用帶齊 model／fallbacks／timeout-seconds／message／tools 嘅 `cron edit` 重寫並驗證。
- **驗證**：`health_report.sh --deliver` → rc=0、stdout 20 行且數字全部腳本實測（513 行／1878=1878／errs 3／敏感檔 0／兩個 skill md5=1／6 states／13 行），`[LOOP_STATUS: FAIL]` 原樣保留冇被改成 OK；`bash -n` 通過；7 個 agentTurn job 全部 fb=3、SELFREF=False、同 provider、全部帶 @profile。
- **教訓**：(a) **報告唔應該經模型轉述** —— 數字要由產生佢嗰個腳本直接交付，模型只做「貼上」唔做「整理」。(b) **改 job payload 時唔好將 primary 塞入自己嘅 fallback 鏈**，改完即場核對 SELFREF／同 provider／@profile。(c) `cron edit` 會重置未指定 payload 欄位 → 一律帶齊 model／fallbacks／timeout-seconds／message／tools 再改，改完逐項核對。

## [2026-11-14 00:15] 更新 (v2.9.183) — 健康報告 job 改 command payload（報告完全唔經模型）：根治假綠 + 交付 timeout
- **症狀（兩個層次）**：(a) 2026-11-13 22:00 交付咗**內容全部捏造**嘅報告（Telegram 22:00:31 delivered）：寫「MEMORY.md 1234 行／章節數 56／Cron job 錯誤 0 個／三倉髒檔 0／System cron 15 行」並將 `[LOOP_STATUS: FAIL]` 改成 `[LOOP_STATUS: OK]`；實際值 **513 行／1878 章／errs 2／13 行／FAIL**。(b) 改用 agentTurn + `--deliver` 後 23:43 同 23:52 兩次仍然**完全冇交付**（「⚠️ Tool Call failed」、「LLM request timed out」347 秒），但 `logs/health_report-2026-11-13.log` 顯示腳本一直正常跑（23:54:15 有新 entry、數字正確、FAIL 保留）。
- **根本原因**：報告**交付仍然要經模型**——舊 message 要求「exec 跑腳本 → 模型整理成健康報告 → 交付」，弱模型捏造；改 --deliver（腳本 stdout 就係最終報告）雖然冇得捏造，但要模型「逐字原樣貼 stdout」，變成**交付依賴模型可用性**：模型慢／timeout 就零交付。只要交付路徑仲有模型，報告就唔可信。
- **解決方法**：`a6db95e0`（每日健康報告 22:00）由 agentTurn 改成 **command payload**：`--command "bash $WORKSPACE/scripts/health_report.sh --deliver"`，交付 = 腳本 stdout，**全程冇模型**。schedule／delivery（announce telegram 5344443732）／failureAlert（after 2）保留；`cron-guardian.sh` 重建模板同步改用 `--command`，落地前用臨時 job 實測過模板指令。
- **驗證**：00:08 實跑 status=ok、delivered=True，交付內容係腳本原文（MEMORY.md 522 行／線上章節 1878＝本地 1878／errs 3／敏感檔 0／兩個 skill md5 唯一數 1／三倉未推送 0 髒檔 0），**含 `[LOOP_STATUS: FAIL]` 而冇改成 OK**；反查交付字串：'1234'／'56 '／'LOOP_STATUS: OK' 三者都**唔存在**（22:00 嗰份三者都存在）。
- **教訓**：(a) **報告唔應該經模型轉述**——數字要由產生佢嗰個腳本直接交付，「叫模型照貼」都係依賴模型。(b) **交付路徑本身要當關鍵故障點**：delivery 依賴弱模型 = 報告可信度依賴弱模型。(c) 重建模板要同 job 現狀一致，並在落地前用臨時 job 實測模板指令。(d) job 卡住（`runningAtMs` 未清）時 `cron run` 會回 "already-running"，清法係 `cron disable` + `cron enable`。

## [2026-11-14] cron job description 過時修正 + guardian 模板補 --description
- **修復內容**：6 個 cron job（75d65637 / 27d54b55 / 66957fcc / f8b447b6 / 23533480 / a6db95e0）嘅 `description` 仍然寫住舊設計「model: minimax/MiniMax-M3.1-Flash + 3 fallbacks」，實際 payload 已經係 OpenRouter free primary + 同 provider 3 層 fallback；`a6db95e0` 更加已經係 command payload（冇 model）。metadata 同實際配置對唔上會令診斷睇錯方向。
- **根本原因**：2026-11-13 provider 單一化、2026-11-14 command payload 兩次改動只更新 payload 冇同步 description；`cron-guardian.sh` 重建模板亦冇傳 `--description`，復原路徑會洗走修正。
- **解決方法**：① `openclaw cron edit <id> --description "..."` 逐個改正 6 個 job；② `scripts/cron-guardian.sh` 6 個 `cron add` 模板全部補 `--description`。
- **驗證**：先用臨時 job 實測「只改 description」嘅副作用——agentTurn 與 command 兩種 kind 都係 message／model／fallbacks／timeoutSeconds／toolsAllow／argv／binding／delivery／schedule 全部逐字不變（command 唔會被改成 agentTurn），測完即刪；實機 6 個 job 改完用 SQLite 讀 `cron_jobs.job_json` 逐欄比對 11 個關鍵欄位全部不變，只有 description 改變；`bash -n scripts/cron-guardian.sh` 通過。
- **教訓**：改 metadata 前要先量度副作用（`cron edit` 唔帶齊 payload 會重設未指定欄位）；配置同 metadata 要一齊改；重建模板要包含 description，否則復原會洗走修正。

## [2026-11-14] 已退役嘅 Volume 4 管線被簡報 job 復活 → marker + 雙重守衛 + 拆指示
- **修復內容**：08:15 早上簡報 job 跑完（status=ok、Telegram 交付成功），但 `.dropbox-sync/volume4_state.json` mtime 變 08:16、`synced_to_site` 由 1746 跳到 1878（note=auto-reconciled），三倉亦多咗一次 08:16 記憶備份 commit —— **Volume 4 明明係 2026-10-02 大肥喵指令退役**（crontab 冇條目、guardian 守護名單亦冇）。
- **根本原因**：簡報 job message 第 3 步寫「Dropbox 同步狀態：**Volume 4** 最後執行結果」，同一份 message 又授權「自動修復：state 分歧就直接修復，不需等人類指示」。V4 state 停喺 1746 而網站有 1878 → agent 判為 state 分歧 → 自行執行已退役嘅 `dropbox-volume4-daily-sync.sh` → auto-reconcile 分支 union 網站章節落 V4 state → wrapper 尾 `source backup-memory.sh` 順帶多推一次 commit。冇新章上網，純粹係管線復活。
- **解決方法**：① `.dropbox-sync/volume4_RETIRED` marker（寫明退役日期 + 復活條件）；② 守衛放喺真正入口——`scripts/dropbox_volume4_sync.py` 的 `process_batch()` 同 `scripts/dropbox-volume4-daily-sync.sh` wrapper 兩邊都檢查 marker，存在就即刻 skip（唔改 state、唔推 Git、唔 source backup-memory.sh）；③ 拆指示——`27d54b55` 第 3 步改查 V5/6/7 並明文「唔准執行任何 V4 腳本」，`66957fcc` 嘅 system cron 清單改為 V5/6 11:00 + V7 11:30（V4 本來就唔喺 crontab），`cron-guardian.sh` 重建模板同步。
- **驗證**：wrapper 實跑 + `python3 scripts/dropbox_volume4_sync.py` 實跑都印「⛔ 已退役…跳過」，`volume4_state.json` md5 before/after 完全相同；`bash -n` + `py_compile` 通過；兩個簡報 job message 改完用 SQLite 逐欄比對，kind/model/fallbacks/timeoutSeconds/toolsAllow/argv/inferenceBinding/delivery/schedule/description 全部不變，只有 message 改變；`docs/heartbeat-checklist.md` 補 V4 守衛說明並 `sync_heartbeat_scratch.sh` 同步入 scratch。
- **教訓**：(a)「已退役」只靠排程層面移除（crontab + guardian 兩個名單）唔夠——任何有 exec 權力嘅 agent 見到 state 分歧就能復活佢，退役要有腳本層守衛。(b) 簡報 job 嘅「自動修復」權力會越過退役指令，message 內部矛盾（一邊叫佢查 V4、一邊叫佢自動修復）就足以復活管線，指示要同退役事實對齊。(c) 守衛要放喺真正執行入口（.py），唔可以只放 wrapper，因為 agent 唔會跟 wrapper 走。(d) 副作用鏈要睇全：wrapper 尾 `source backup-memory.sh` 令三倉多推 commit，要睇 Git log 先發現。

## [2026-11-14] 心跳 lane 自身超時（600s）→ 巡檢回合必須精簡
- **修復內容**：heartbeat-main（`9dc7d6c3`）11-14 14:34:28 → 14:44:29 dur 600367ms、`cron: job execution timed out`、consecutiveErrors=1；14:44 嗰輪 skipped 後 errs 自然清零。
- **根本原因**：心跳回合做咗過多步驟（ops-snapshot + 逐個 job 查 receipt + 追查主機 poweroff 根因 + 連續多輪 exec 驗證），總時長撞 heartbeat job 嘅 600 秒硬 timeout——自己把自己嘅巡檢 lane 打成 error。
- **解決方法**：心跳回合收斂成「一次 ops-snapshot → 一次三倉/skill/守衛/網站核驗 → 出結論」；任何需要深挖嘅問題（根因追查、逐欄 payload 比對）改到普通 turn 處理，心跳回合只記低事實同結論。
- **驗證**：timeout 後下一輪 skipped，`consecutiveErrors` 隨即清零（skipped 唔算 error，唔需要 disable/enable 清 running）；8 個 job errs 合計 0、三倉 0 未推送 0 髒檔、網站 200。
- **教訓**：每個 cron job 都有硬 timeout，心跳 lane 堆工具呼叫 = 自傷；心跳回合要短，深挖留返普通 turn。

## [2026-11-14] 主機 poweroff 根因確認 = GNOME 桌面 session 主動關機（非 apt／非 cron／非崩潰）
- **修復內容**：08:28 主機 poweroff → 08:59 重開機（31 分鐘空窗）根因已由 `journalctl -b -1` 確認：`gnome-session-shutdown.target` → `shutdown.target` → `systemd-poweroff.service: Finished` → `poweroff.target`，即 GNOME 桌面 session 主動關機。同 2026-11-12 08:37 嗰次**完全同一 pattern**。
- **根本原因**：**有人從桌面 session 關機**（人手撳關機／桌面自動登出觸發關機／遙控送關機指令）。佐證排除：08:2x 冇 apt/dpkg 活動、冇 `/var/run/reboot-required`、repo 內冇任何 script 呼叫 `poweroff`/`reboot`、auth.log 冇 sudo poweroff、systemd timer 冇相關條目。
- **解決方法**：診斷步驟寫入 MEMORY.md（`journalctl -b -1` → 睇 shutdown chain）；若再發生的處理建議 = 查 `org.gnome.SessionManager auto-poweroff`／螢幕鎖定自動登出／遙控來源。
- **驗證**：`journalctl -b -1` 同 `journalctl -b -2` 兩次都見到同一條 `gnome-session-shutdown.target` → `systemd-poweroff` chain；影響實測輕微（只漏 08:33 一次心跳，8 個 job errs 合計 0，三倉乾淨，網站 200）。
- **教訓**：主機「乾淨 poweroff」唔等於崩潰——`systemd-logind` 出「will power off now!」代表有人 request 乾淨關機；**判別方法係 `journalctl -b -1` 睇 shutdown chain**（`gnome-session-shutdown.target` = 桌面人手；`unattended-upgrades` + reboot-required flag = 自動更新）。

---

## 2026-11-15 更新
- **新增教訓：主機／gateway 離線後，排程會喺重啟時「catch-up」一次過補做，唔係漏做**（2026-11-14 22:00 → 2026-11-15 10:13 離線 → 10:15 三個 job 同時補做：`27d54b55` 早上簡報由 08:15 順延 10:15、`23533480` Audio Sync 10:00 順延 10:15、`fb128f67` Memory Dreaming 03:00 補做）。**判斷交付要睇 journald `outbound send ok`（messageId 23524 @ 10:15:58、23525 @ 10:17:14），唔可以淨睇 cron state 嘅 delivery 欄**；簡報遲到但真係送到，唔算漏交付。
- **新增教訓：`provider=minimax` 會喺 thinking 被 clamp（`thinking.type="disabled"`／`reasoning.effort=none`）時回 400** —— body = `invalid params, model "MiniMax-M3.1-Flash" requires adaptive thinking ... (2013)`。要靠 openrouter free fallback 頂住；見到 400 + adaptive thinking 就知係 thinking clamp，唔係 key／額度問題。
- **新增教訓：MEMORY.md 已記錄嘅 poweroff 根因為「主機層面／人手乾淨關機」，到 2026-11-15 已是第 3 次（11-12 08:16、11-14 08:28、11-14 22:00→11-15 10:13）**，範圍擴大到過夜 12 小時 → 建議大肥喵向 provider 層面查。
- **修復驗證**：`DREAMS.md` 髒檔按「commit → `git pull --rebase origin main` → `git push`」處理（rebase 撞到 CI 每日新聞 commit `547568e11`），三倉回復未推送 0 / 髒檔 0；MEMORY.md 三倉 md5 唯一數 = 1。

---

## 2026-11-16 更新
- **新增教訓：Dropbox V5/V6 同步「無新章節」嗰條路徑會令 workspace 留低髒 state 檔**。`scripts/dropbox_volume5_sync.py` / `dropbox_volume6_sync.py` 只有喺 `git_commit_and_push()`（有新章節嗰條路徑）先會 commit；但 11:00 system cron 跑「未處理: 0 個」時，`auto-reconciled` 步驟仍會改寫 `.dropbox-sync/volume5_state.json` / `volume6_state.json`（`last_batch` 由 CH1879-1884 → CH1885-1890）**但唔 commit** → 心跳回合見到 workspace 髒檔 2。**處理方法**：同 `DREAMS.md` 一樣直接 `git add .dropbox-sync/volume*_state.json && git commit` → `git pull --rebase origin main` → `git push`（今日：`5cff41589..e607f87d6`）。
- **判斷要點**：見到 `.dropbox-sync/volume5_state.json` / `volume6_state.json` 髒住唔好當故障，睇 `git diff` 係咪只有 `last_batch` + `processed_chapters` 尾巴增長 → 就係 auto-reconcile 嘅正常更新，commit 落去就得。

## [2026-11-16] poweroff 第 4 次（08:42，空窗縮到約 2 分鐘）→ 唔漏排程，provider 查詢照舊
- **修復內容**：11-16 08:42:16 journald `got dbus signal - shutdown detected!` → `systemd-poweroff.service: Finished`（08:42:23）→ 08:44:11 重開機（gateway `ActiveEnterTimestamp=Mon 2026-11-16 08:44:16 HKT`），**空窗約 2 分鐘**，係 poweroff pattern 第 4 次（11-12 08:16、11-14 08:28、11-14 22:00→11-15 10:13、11-16 08:42）。
- **根本原因**：同一「GNOME 桌面 session 主動關機 → `systemd-poweroff`」chain（`journalctl -b -1` 實測），非 apt／非 OOM／非崩潰。
- **解決方法**：冇程式層修復可做（主機層面／人手關機）→ 診斷步驟寫入 MEMORY.md，**待大肥喵向 provider 層面查**；重點係**每次事件後即刻對數排程有冇漏做**。
- **驗證**：今次**冇漏做、冇 catch-up** —— 08:00 記憶備份（log `08:00:13 ✅`）、08:15 早上簡報（outbound `messageId 23530 @ 08:17:45`）、10:00 Audio Sync（`messageId 23531 @ 10:01:17`）、10:00 財經更新全部照跑；8 job errs 合計 0、三倉未推送 0 / 髒檔 0、網站 HTTP 200、`chapter-*.html` 抽查 5 份結構正常、兩個 skill 四處 md5 唯一數 = 1。
- **教訓**：(a) poweroff pattern 由「31 分鐘空窗」縮到「2 分鐘空窗」，**唔代表唔使查**——空窗短只係少啲排程受影響。(b) 重開機後先睇 boot 清單（`journalctl --list-boots`）對時間線，再對數排程，唔好靠估。(c) 判斷有冇漏做靠三樣：journald `outbound send ok`、各 system cron log 時間戳、cron receipt 連續性。

---

## 2026-11-17 更新
- **新增教訓：11:00 Dropbox Volume 5/6 同步會改 `.dropbox-sync/volume{5,6}_state.json` 而唔會自己 commit** → 心跳回合見到 workspace 髒檔出現 state 檔（正常運作痕跡，唔係 bug）時，用同一套流程：`git add` 該 state → `git commit` → `git pull --rebase origin main` → `git push`。**Volume 4 仍然唔准郁**（`.dropbox-sync/volume4_RETIRED` marker 存在就要 skip）。
- **新增教訓：OpenClaw 有新版本（2026.11.4）時，agent 唔可以自己升級** —— 唔准 exec 跑 `openclaw update` / `npm install -g openclaw` / 停 gateway；只可以叫大肥喵喺 chat 送 `/update`（owner + `commands.restart` 預設開啟）。版本檢查 script 已經自動發 Telegram 通知，唔好重複通知。

---

## 2026-11-17 更新
- **新增教訓：agentTurn cron job 嘅 `toolsAllow` 必須包含 `send` 同 `message`** —— runtime context 每 turn 都會注入「Message tool: `send`: `target` + `message`」，模型會跟住呼叫 send；冇 allow 就會 **「⚠️ Send blocked」** → 整個 run 判定失敗 → 零交付（2026-11-17 12:55 中午簡報 `66957fcc` 就係咁：errs=1、delivery=not-delivered、journald 完全冇 outbound send ok）。對照：`27d54b55` 有 send+message 就正常。
- **新增教訓：`openclaw cron add` 唔帶 `--tools` 只會得返 n=1 預設清單** → 所有重建路徑（`scripts/cron-guardian.sh`）必須顯式帶 `--tools`（現已加 `TOOLS` 變數，29 項含 send/message，5 個 agentTurn 分支全部帶；健康報告 22:00 係 command payload 唔加）。
- **新增教訓：`cron edit` 會重置未指定嘅 payload 欄位** → 改 toolsAllow 時要帶齊 model / fallbacks / timeout / message（`scripts/cron_model_guard.py` 已做齊）。
- **判斷交付**：以 journald `outbound send ok` + cron receipt 兩個欄為準（2026-11-17 補跑 `66957fcc` → 13:23:28 messageId 23541 送達，errs 回到 0）。

---

## 2026-11-18 更新
- **事故**：`SKILL.md` 累加更新記錄後爆到 **256640 bytes**（loader 硬上限 256000）→ 2026-11-17 13:35 起 gateway 每分鐘記一次 `[skills] Skipping invalid skill: file=~/.openclaw/skills/novel-site-standards/SKILL.md error=File exceeds 256000 bytes`，**11-18 全日 544 次** → 呢個 skill 成日冇被載入（規則實際上收唔到）。
- **根因**：每次事故後都「版本 +0.0.1 + 追加更新記錄」，但冇人睇過主檔大小；而頂部雖然有寫 256000 上限警告，實際執行時冇人檢查。
- **修復**：把 **2026-04～09 嘅 51 段 dated 更新記錄**（54738 bytes，內容一字無刪）搬到同目錄 `SKILL_HISTORY.md` → 主檔 **206171 bytes**（分檔後 + 本次更新記錄），HISTORY 177429 bytes；主檔頂部加「已分檔段落索引」方便查返。**段落標題零遺失**（分檔前 167 段全部保留喺新主檔或 HISTORY）。
- **新流程（唔好再踩）**：① 追加任何更新記錄前先 `stat -c%s SKILL.md`；② **> 200000 bytes 就必須先分檔**（搬最舊 dated 段落去 `SKILL_HISTORY.md`，主檔保留索引）；③ 分檔後四處（installed / workspace / Second-brain / Max-backup）**SKILL.md 同 SKILL_HISTORY.md 都要一齊同步**，唔可以只搬一份；④ `scripts/sync_skill_copies.sh` 已加 **> 200000 bytes 即報警**（防再爆）。

---

## 2026-11-19 更新
- **新增教訓：第三種交付失效模式 —— `receipt status=ok` 但 `delivery_attempt_state=not-started`** = **零交付但唔報錯**（2026-11-19 12:55 中午簡報 `66957fcc`：agent 條 exec 指令 quoting syntax error → 最終回覆空字串 → announce 冇嘢可送；journald 冇 outbound send ok，但 cron state 顯示 ok + errs=0）。**交付判定必須同時睇 receipt `delivery_attempt_state` 同 journald `outbound send ok`**，淨睇 errs/state 會漏。發現即 `openclaw cron run <job-id>` 補跑（實測 → 13:05:40 messageId 23556 送達）。
- **新增教訓：agent 最終回覆空字串 = 零交付** → 簡報 job 嘅 message 要硬性要求「最終回覆必須有實質內容（最少 LOOP_STATUS 一行）」；已加落 `66957fcc` 同 `scripts/cron-guardian.sh` 模板。
- **新增教訓：exec 指令避免 `python3 -c` 嵌套引號**（2026-11-19 12:55 死因）→ 一律用 heredoc `python3 - <<'PY' ... PY` 或現成 shell helper（`scripts/ops-snapshot.sh`）。

---

## 2026-11-19 更新（續）

- **修正 `scripts/sync_skill_copies.sh` 一個真 bug**：揀基準檔靠 `grep ^version:`，但 **`SKILL_HISTORY.md` 根本冇 version 行** → 全部被跳過 → **HISTORY 永遠唔會同步**（2026-11-19 實測：分檔後 workspace 223459 bytes vs 三倉 177429 bytes，唯一 md5 數 = 2）。已改成「版本大者勝，同版本取較大檔案，冇版本當 0」。
- **再分檔一次**：加完 11-19 更新記錄後 SKILL.md 回到 **208613 bytes**（逼近 256000）→ 再把 3 段 **2026-10-30** 記錄搬去 `SKILL_HISTORY.md`，主檔降至 **163331 bytes** 以下，索引已加條目，內容零遺失。
# 版本 2.9.195
---

## [2026-11-19] 更新 (v2.9.196) - MoonTV Upstream Sync 保活（GitHub 60 日停用規則）

### 修復內容
- **症狀**：2026-11-19 收到 GitHub email「The 'Upstream Sync' workflow in jyonline0604/MoonTV will be disabled soon」。`jyonline0604/MoonTV` = `itv.kofhk.com` 背後嘅 MoonTV app（大肥喵確認有用）。
- **根因**：GitHub 規則 —— repo **連續 60 日無活動**，scheduled workflow 會被自動停用。fork 最後 push = 2026-02-05 → **286 日**。當時 Upstream Sync 仍 `state=active`（`cron: 0 */6 * * *`，最近 3 次 run #174/#175/#176 全 success）→ 屬預警未發難。
- **影響範圍（已逐項核實）**：
  - 只影響 **schedule 觸發**嘅 workflow；push 觸發嘅 `Build & Push Docker image` 不受影響 → **itv 網站唔會倒**
  - 上游落差：fork main sha == `samqin123/MoonTV` main sha == `c0bba763`（behind 0 / ahead 0 / identical）→ 上游 samqin123 main 自 2025-08-04 冇新 commit → **即使停用都唔會即時令 itv 變舊**
  - itv.kofhk.com 線上正常（307 → /login，Cloudflare 前置），kofhk.com 200
- **發現 fork 個 sync.yml 指錯上游**：寫 `upstream_sync_repo: senshinya/MoonTV`（442 stars、2025-08 停更），而 GitHub parent 係 `samqin123/MoonTV`（2146 stars、仍活躍）→ 可能同步錯目標（惟目前無內容落差）。
- **修復**：新增 `scripts/moontv_keepalive.py` + crontab 每日 06:47 巡檢：
  - ≥45 日無 push → 用 Git Data API 推**空 commit**（tree 不變、parent = 現 main）→ 重置 60 日倒數。零檔案改動 → 不觸發 Docker build、不污染內容、無 merge 衝突
  - workflow 被停用 → `PUT /actions/workflows/{id}/enable` 自動復原
  - 有寫入權限就自動做；冇就發 Telegram 通知（合併成一條、去重 72h）附手動步驟
  - 永遠 exit 0；token 來源優先 `.token-store/github-moontv-token.txt` → git remote → `.git-credentials`

### 教訓
- **GitHub scheduled workflow 60 日停用規則只計 schedule 觸發**：push 觸發嘅 workflow 唔受影響，所以「workflow 被停用」≠「網站服務中斷」，唔好過度反應
- **保持 repo 活躍嘅最低成本手段係推空 commit（tree 不變）**：唔好為咗保活亂改檔案，空 commit 零檔案改動、唔觸發下游 CI、唔會造成 merge 衝突
- **fine-grained PAT 嘅寫入權限係 per repo + per permission type 授權**：GET 200 唔代表 POST 有權；Actions:write / Contents:write / Issues:write 各自獨立，測試時要逐個 endpoint 試
- **查「某個 repo 有冇用」唔可以只 grep repo 名**：我頭先只 grep `moontv` 就斷言「本機無部署」，漏咗 `itv.kofhk.com` —— 應該連域名/部署來源一齊查
- **fork 嘅 sync.yml 可能指緊另一個 upstream**：GitHub parent（`parent`/`source` 欄位）同 workflow 內寫嘅 `upstream_sync_repo` 未必一致，要兩邊都核對
- **跨 repo compare 要用對 endpoint**：`/repos/{owner}/{repo}/compare/{base}...{head}` 跨 repo 會 404，要分別取兩邊 sha 再逐個 compare

---

## 2026-11-19 更新（續）
- **新增教訓：零交付偵測要分清楚「設計如此」同「真故障」** —— receipt `status=ok` + `delivery_attempt_state=not-started` 對 **agentTurn 簡報 job** 係零交付（要即刻補跑），但對 `kind=heartbeat` 嘅 `9dc7d6c3` 係**設計如此**（`delivery=null`，心跳唔派送 Telegram），唔可以當零交付，否則每次巡檢都誤報。
- **新增教訓：workspace 髒檔唔止 `DREAMS.md` 同 `.dropbox-sync/*_state.json`** —— 其它流程（例如 MoonTV upstream watchdog）都會直接改 workspace 內嘅 script；巡檢時要睇 `git diff` 內容判斷，唔好假設只有兩種來源。

---

## 2026-11-19 更新（續 2）
- **新增教訓：`bash -n` 通過唔代表 shell script 正確** —— 引號不平衡時語法仍然合法，只係 `|` 會被當成 pipeline，於是行內字串被當 command 執行（`fork: command not found`）。改完 `scripts/health_report.sh` 一定要**真係試跑一次**（`bash scripts/health_report.sh` 唔帶 --deliver）再睇 stderr。22:00 健康報告係 command payload，script 嘅 stderr 會原樣送出去。
- **新增教訓：`verbose` 行用 `|` 分隔欄位時，行內雙引號必須平衡**（2026-11-19 MoonTV 段落加落去時出咗事）。

---

## 2026-11-20 更新
- **修復內容**：釐清並記錄 2026-11-20 heartbeat-main 兩輪 error（20:33→20:34:59、21:03→21:13:04）嘅根因 —— journald 有 4 次 `[provider-error] code=malformed_tool_call_arguments provider=minimax model=MiniMax-M3.1-Flash`（`repairAttempted=true` 仍失敗），令 exec 呼叫被拒；後者正正 600 秒 = 撞 heartbeat hard timeout。<!-- project: github.com/jyonline0604/website -->
- **根本原因**：① provider 層回傳畸形 tool-call JSON，gateway 自動 repair 失敗 → 同一條大型 exec 重複送出反而再觸發同樣錯誤；② 心跳回合堆咗多輪 exec（重犯 2026-11-14 教訓），600 秒 timeout 被撞爆。<!-- project: github.com/jyonline0604/website -->
- **解決方法**：① provider 出 `malformed_tool_call_arguments` 時唔好原封不動重試同一條大 exec —— 縮細、拆細或直接換 provider；② 心跳回合維持「一次 ops-snapshot + 一次核驗 + 出結論」；③ 呢類 error 唔使手動 disable/enable job，下一輪 skipped（skipped 唔算 error）即令 `consecutiveErrors` 自然清零。<!-- project: github.com/jyonline0604/website -->
- **附帶確認**：2026-11-19 分檔已收尾 —— `novel-site-standards/SKILL.md` 168385 bytes、`SKILL_HISTORY.md` 223459 bytes，四處 md5 唯一數各 = 1；`scripts/sync_skill_copies.sh` 已有 `sync_set standards-history` 一行，HISTORY 唔會再被覆蓋返。<!-- project: github.com/jyonline0604/website -->
