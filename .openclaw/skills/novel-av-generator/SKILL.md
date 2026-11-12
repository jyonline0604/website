---
name: novel-av-generator
description: 有聲畫小說章節自動生成工具。當需要生成有聲畫章節（AV版本）時觸發，包括：生成5張場景圖片、生成廣東話配音音頻、創建完整HTML頁面、更新目錄、提交推送。自動化和標準化整個AV章節生成流程。
version: 2.2.42
lastUpdated: 2026-04-22
---

# Novel AV Generator - 有聲畫小說生成器

自動生成有聲畫小說章節的完整流程。

## 工作流程

### 1. 準備階段
```bash
# 確認章節文件存在
ls chapter-XX.html  # 文字版
ls chapter-XX-av.html  # 確認AV版不存在
```

### 2. 提取文字內容
```bash
sed -n '/<div class="content">/,/<\/div>/p' chapter-XX.html | sed '1d;$d' | sed 's/<[^>]*>//g' | tr -s ' \n' > assets/chapter-XX-full-text.txt
```

### 3. 生成5張場景圖
使用 MiniMax image-01 生成5張場景圖：
- 場景1：章節開場場景
- 場景2：主要情節場景
- 場景3：轉折或衝突場景
- 場景4：情節推進場景
- 場景5：章節結尾場景

```bash
# 列出新生成的圖片（按時間排序，最新的在前）
ls -lt ~/media/tool-image-generation/*.png | head -5

# 複製到 assets 目錄（使用 ls 的輸出作為順序）
cd ~/media/tool-image-generation/
for i in 1 2 3 4 5; do
    latest_file=$(ls -t *.png | sed -n "${i}p")
    cp "$latest_file" /home/openclaw/.openclaw/workspace/assets/chapter-XX-scene${i}.jpg
done
cd /home/openclaw/.openclaw/workspace/assets

# 驗證：檢查所有圖片 MD5 是否不同
md5sum chapter-XX-scene*.jpg
```

⚠️ **重要**：不要使用 `mv *.png`，會導致所有場景使用同一張圖片！

### 4. 生成音頻
```bash
cd assets
edge-tts --voice "zh-HK-HiuGaaiNeural" --file "chapter-XX-full-text.txt" --write-media "chapterXX_audio.mp3"
cd ..
```
⚠️ 注意：edge-tts 必須使用絕對路徑，否則在 background 執行時會找不到文件。

### 5. 創建 AV HTML
創建 `chapter-XX-av.html`，使用標準模板：
- Hero 區：使用場景1圖片
- 導航列：上一章 / 下一章 / 目錄
- 5個場景區塊：圖片 + 標題 + 描述
- 音頻控制按鈕
- 滾動動畫效果

### 6. 更新 av-novels.html
```python
# 更新統計數字
totalChapters">XX
stat-number">XX%

# 插入新章節卡片（最前面）
# 移除上一章的 "New" badge
# 添加新章節卡片 + "New" badge
```

### 7. 提交所有文件
```bash
git add chapter-XX-av.html av-novels.html \
  assets/chapter-XX-*.* \
  assets/chapterXX_audio.mp3  # 音頻文件必須一起提交！

git commit -m "feat: add chapter XX AV - 章節標題 (5 scenes with audio)"
git push origin main
```

### 8. 觸發 GitHub Pages 重建
```bash
curl -s -X POST "https://api.github.com/repos/jyonline0604/website/pages/builds" \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json"
```

### 9. 驗證音頻
等待約60-90秒後驗證：
```bash
curl -sI "https://kofhk.com/assets/chapterXX_audio.mp3" | head -3
# 必須返回 HTTP/2 200
```

## 標準場景描述模板

根據章節內容生成5個場景：
1. **開場場景**：地點/氛圍描寫
2. **主要情節**：主角關鍵動作
3. **轉折/衝突**：戲劇性時刻
4. **情節推進**：事件發展
5. **章節結尾**：預示下一步

## 🎨 角色設計圖鑑（必須參考！）

**位置**：`docs/character-design.md`

### 重要性
生成圖片時，**必須**參考角色設計圖鑑，確保：
- **同一角色外觀一致**：林塵、蘇璃等角色的外貌、服裝必須統一
- **避免風格漂移**：每次生成都基於同一標準
- **提升專業感**：角色形象連貫，讀者更容易投入

### 主要角色外觀關鍵詞

| 角色 | 關鍵特徵 |
|------|----------|
| **林塵** | 黑色短髮、胸口藍色心臟型量子晶片、藍色數據流、金屬戰鬥服 |
| **蘇璃** | 銀白長髮、異色瞳（左金右銀）、銀白機械戰甲、納米光點 |
| **明鏡** | 灰白長髮束高馬尾、古風道袍、額頭靈脈標記 |
| **天機子** | 白髮白鬚但面容年輕、金色眼睛、白袍八卦、半透明光粒子 |

### 使用方法

1. **生成前**：先閱讀 `docs/character-design.md` 中相關角色的詳細描述
2. **生成時**：在 prompt 中加入角色的核心外觀描述
3. **驗證時**：確認圖中人物是否符合角色設計

### 林塵標準 Prompt 示例
```
Young Asian male, 20 years old, 175cm tall, black short hair, glowing blue circuit patterns on forehead, glowing blue translucent quantum crystal shaped like a heart on chest, wearing dark blue tech-cultivation combat suit, blue data streams surrounding body, holding spirit energy sword
```

### 姿勢/場景組合
- 戰鬥姿勢：+ `holding spirit energy sword, dramatic combat pose, blue energy surrounding`
- 日常姿勢：+ `wearing casual union uniform, calm expression, standing in futuristic city`

## 章節標題列表（用於快速參考）

| 章節 | 標題 | 關鍵詞 |
|------|------|--------|
| 24 | 蓬萊告別 | 傳送、離別、新城市 |
| 25 | 聯盟日常 | 人工湖畔、神秘女子 |
| 26 | 秘密實驗室 | 深夜、神秘裝置 |
| 27 | 真相接近 | 研究、虛擬對話 |
| 28 | 聯盟談判 | 談判、修煉塔 |

## 常見問題

### Q: edge-tts 報錯 "File not found"
A: 必須使用絕對路徑，不要在 background 中執行時使用相對路徑。

### Q: 音頻文件忘記提交
A: 每次 commit 前確認 `git status` 包含 `chapterXX_audio.mp3`。

### Q: 如何一次生成多章？
A: 按順序逐章處理，每章完成後再處理下一章。

## 自動化腳本

如需完全自動化，可使用：
```bash
python3 .openclaw/skills/novel-av-generator/scripts/generate_av_chapter.py --chapter XX
```
---

## 更新日誌

### 2026-04-22 修復章節排序邏輯錯誤
- **問題**：新生成的有聲畫小說章節每次錯誤排序，章節81出現在章節80之後
- **根本原因**：`generate_av_chapter.py` 中的 `sort_av_novels_chapters()` 函數有邏輯錯誤
  - 錯誤：先排序卡片，然後檢查排序後的卡片是否已排序（總是返回True）
  - 正確：先檢查原始卡片是否已排序，只在未排序時進行排序
- **解決方法**：
  1. 修復 `sort_av_novels_chapters()` 函數的邏輯錯誤
  2. 手動修復當前 `av-novels.html` 中的章節順序（交換章節80和81）
  3. 驗證修復後所有章節按降序排列（81 → 80 → 79 → ...）
- **預防措施**：
  - 每次生成新AV章節後，必須驗證 `av-novels.html` 的排序
  - 定期運行檢查腳本確認章節順序正確
  - 更新SKILL.md記錄此問題以防止再次發生

### 2026-04-04 修復章節順序問題
- **問題**：Python腳本替換邏輯錯誤，導致av-novels.html中章節次序錯亂、多個章節共用同一圖片
- **原因**：使用for迴圈替換時，每次替換後marker位置改變，導致後續插入位置錯誤
- **解決方法**：
  1. 先restore到正確版本：`git checkout <正確commit> -- av-novels.html`
  2. 一次性構建所有新章節卡片HTML
  3. 一次性替換整個marker字符串
- **預防**：未來更新av-novels.html時，必須：
  - 先檢查現有檔案的HTML結構
  - 使用精確的marker匹配
  - 驗證替換後的順序和圖片URL是否正確

---

### 2026-04-05 添加自動更新統計數字
- **問題**：總章節數和完成度沒有自動更新
- **原因**：這兩個數值是硬編碼的，不會隨新章節增加而自動更新
- **解決方法**：
  1. 每次添加新AV章節後，更新這三個數值：
     - `已完成章節`：AV章節實際數量（ls chapter-*-av.html | wc -l）
     - `總章節數`：目前文字版章節總數（ls chapter-*.html | grep -v template | wc -l）
     - `完成度`：已完成 / 總章節數 × 100%
  2. 在更新 av-novels.html 時一併更新這三個數值

---

### 2026-04-05 修復統計定義
- **問題**：總章節數的定義理解錯誤
- **正確定義**：
  - 總章節數 = 文字版章節數量（ls chapter-*.html | grep -v av | grep -v template | wc -l）
  - 已完成 = AV版本章節數量（ls chapter-*-av.html | wc -l）
  - 完成度 = 已完成 / 總章節數 × 100%
- **範例**：78文字版章節，37個AV版本，完成度47%

---

### 2026-04-05 完成第40-44章
- 已完成：蓬萊康復(40)、神秘商人(41)、遠古地圖(42)、星際遠征(43)、遠古傳承(44)
- 發現問題：第44章原文使用「林寒」而非「林塵」，已修正
- 發現問題：av-novels.html統計數字未自動更新（39→44, 50%→56%），已修正
- 重要教訓：完成章節統計必須手動計算並更新

---

## ⚠️ 圖片驗證步驟（重要！v2.1.0 新增）

### 問題
2026-04-07 我生成圖片後沒有驗證是否符合章節內容就發佈，導致圖片與劇情不符。

### 驗證流程（必須執行！）

#### 生成圖片後
1. **確認圖片已生成**
```bash
ls -lt ~/media/tool-image-generation/*.png | head -5
# 檢查是否有新的圖片文件
```

2. **使用 image tool 檢視圖片**
```bash
image ~/media/tool-image-generation/<最新圖片>
```

3. **對比驗證**
- 圖片是否符合章節開頭的場景？
- 圖片風格是否與章節內容匹配？
- 人物/情節是否與文字一致？

4. **驗證通過才能提交**
- 如果不符：重新生成或調整 prompt
- 如果符合：才能 git add 和 commit

### 自我檢查清單
```
□ 圖片已複製到 assets 目錄
□ 已驗證5張圖片 MD5 都不同（沒有重複）
□ 已用 image tool 檢視圖片是否符合章節內容
□ 確認符合後才提交
```

### ⚠️ 防重複機制
每次生成圖片後，**必須**驗證：
```bash
# 檢查 MD5，確保所有圖片都不同
md5sum chapter-XX-scene*.jpg
# 如果有重複，必須重新生成並正確複製

### 禁止事項
- ❌ 不驗證就直接提交
- ❌ 只檢查文件存在就以為完成
- ❌ 未確認圖片符合內容就發佈

---

## 更新日誌

### v2.2.0 (2026-04-09)

#### 新增：角色設計圖鑑參考
- **問題**：之前生成的人物圖片外觀不統一
- **解決**：建立 `docs/character-design.md`，記錄所有角色詳細外觀描述
- **強制規則**：
  - 生成圖片前必須參考角色設計圖鑑
  - 同一角色必須保持外觀一致
  - 加入角色核心關鍵詞到 prompt
- **主要角色**：林塵、蘇璃、明鏡、天機子 等

#### 具體更新
- 新增「角色設計圖鑑（必須參考！）」章節
- 添加主要角色外觀關鍵詞表格
- 提供林塵標準 Prompt 示例
- 說明姿勢/場景組合方法

---

## [2026-04-10] 更新
- 完成第53章AV生成（新的紀元）
- 章節53-96文字版已齊全，AV版本現有52章
- GITHUB_TOKEN未設定，GitHub Pages從push自動重建

---

## 防止忘記更新 av-novels.html（2026-04-11 新增）

### 問題
chapter-54-av.html 檔案存在但忘記加到 av-novels.html，導致用戶看不到。

### 解決方案
**pre-push hook 新增檢查：**
```bash
# 檢查3：AV 章節完整性
# 確保每個 chapter-*-av.html 都在 av-novels.html 中列出
```

如果有任何 chapter-*-av.html 未在 av-novels.html 中列出，push 會被阻擋。

### 驗證
```bash
bash scripts/pre-push-check.sh
```

---

## [2026-04-17] 完成第69章
- 章節：能量風暴（混沌教派儀式、林塵犧牲）
- 5張場景圖已生成並驗證MD5不重複
- 音頻已確認 HTTP/2 200 可訪問
- 已更新av-novels.html統計數字

---

## [2026-04-19] 完成第73章AV
- 章節：意識融合（林塵意識融合天機玉簡，達到意識維度4.7）
- 5張場景圖：靈能矩陣、意識拆解重組、天機玉簡融合、十二寶物灌輸、太虛靈芯覺醒
- 音頻已確認 HTTP/2 200 可訪問
- 已更新av-novels.html統計數字（73/123/59%）

---

## [2026-04-19] 完成第75章AV
- 章節：靈魂編程（林塵以靈芯系統解析靈魂本質，發現靈魂可被編程，372%強度提升）
- 章節75-80均缺AV，按順序完成第75章
- 5張場景圖：靈紋陣列實驗室、靈能導管連接、神魂結構全息圖、靈魂重組、神秘黑袍人
- 音頻4.3MB已生成
- 已更新av-novels.html統計數字（75/123/61%）
- 提示：GitHub Pages推送後需等待約60秒才能訪問新音頻

---

## [2026-04-21] 完成第80章AV
- 章節：虛擬實境（林塵進入真實幻境，遇見鏡靈，接受融合之道考驗）
- 5張場景圖：純白虛空、數據殿堂、鏡靈現身、融合考驗、融合之戰
- 音頻3.5MB已生成
- 已更新av-novels.html統計數字（80/129/62%）
- 推送時遇到rebase衝突，reset後重新提交成功

---

## [2026-04-22] 完成第81章AV
- 章節：量子經脈（林塵用靈芯系統重構經脈，量子經脈第一階段完成）
- 5張場景圖：經脈系統解析、三維經脈模型、靈子核心、量子攻擊、量子經脈完成
- 音頻4.3MB已確認 HTTP/2 200 可訪問
- 已更新av-novels.html統計數字（81/132/61%）
- 推送時遇到rebase衝突，reset到origin/main後重新提交成功
- 注意：chapter-1-av.html 未在 av-novels.html 中列出（預存問題）

---

## [2026-04-22] v2.2.10 修復章節1-2格式不一致

### 問題
有聲畫小說第1章和第2章的排版結構與其他章節（特別是第73章）完全不同。

### 差異
| 項目 | 章節1-2 | 章節73 |
|------|---------|--------|
| data-src 屬性 | 有（冗餘） | 無 |
| onerror 屬性 | 有（冗餘） | 無 |
| CSS | 外部文件 | inline style |

### 修復
- 移除 chapter-1-av.html 的 `data-src` 屬性
- 移除 chapter-1-av.html 和 chapter-2-av.html 的 `onerror` 屬性
- 現在與章節73結構一致

### 預防
未來生成新AV章節時，確保：
- 不使用 `data-src` 屬性
- 不使用 `onerror` 屬性
- 直接使用 `<img src="..." loading="lazy" alt="...">`

---

## [2026-04-22] v2.2.11 修復章節1-2外部CSS問題

### 問題
章節1和2的AV版本加載了外部 `chapter.css`，這是文字章節用的CSS，不適合AV版本。

### 修復
移除章節1-2 AV的 `<link rel="stylesheet" href="/assets/chapter.css">`

### 原因
章節73等正確的AV版本使用inline `<style>`，不是外部CSS文件

### 預防
未來生成新AV章節時，確保：
- 不引用外部 chapter.css
- 使用 inline `<style>` 樣式

---

## [2026-04-22] v2.2.12 修復章節1-2缺少inline styles

### 問題
章節1和2的AV版本缺少inline `<style>` 區塊，導致：
- 無法顯示深色背景
- Hero section 不正確
- 音頻控制按鈕樣式錯誤
- 場景卡片佈局混亂
- 導航列樣式不正確

### 修復
添加完整的 inline `<style>` 區塊（與章節73一致）：
- Hero 區：全屏背景、標題居中、文字陰影
- 音頻控制：底部居中圓角按鈕
- 場景卡片：網格佈局、圓角圖片
- 導航列：右上角固定按鈕

### 預防
未來生成新AV章節時，確保：
- HTML 包含完整的 inline `<style>` 區塊
- 不要刪除或修改 inline styles

## [2026-04-22] 完成第82章AV
- 章節：神經連結（林塵神經連結實驗，意識進入靈芯系統底層，獲得天網神經系統藍圖）
- 5張場景圖：神經連結實驗室、銀白神經介面裝置、意識墜入數據海洋、天網神經系統傳承、覺醒者的俯瞰
- 音頻4.3MB已確認 HTTP/2 200 可訪問
- 已更新av-novels.html統計數字（82/129/64%）
- 推送時pre-push hook檢查通過（82個章節全部在目錄中）

---

## [2026-04-22] v2.2.14 修復 av-novels.html 排序邏輯

### 問題
用戶反映新版生成章節每次都是錯誤排序（83→84→82），正確應該是（84→83→82）。

### 根本原因
Python 的 `re.findall()` 使用 `.` 匹配時默認不包含換行符，但章節卡片跨越多行，導致正則表達式 `<div class="chapter-card">.*?</div>\s*</div>\s*</div>` 無法正確匹配所有卡片。

### 修復過程
1. 恢復到正確版本（`git reset --hard HEAD^`）
2. 使用更可靠的方式重建排序：直接用 `split()` 分割章節卡片
3. 驗證排序：確保 chapter-83-av 存在於列表中
4. 驗證推送成功

### 預防措施
- 修復腳本中的正則表達式邏輯，確保正確匹配多行卡片
- 每次排序後驗證章節完整性（84個章節都在）
- 推送前運行 pre-push hook 檢查

---

## [2026-04-24] v2.2.16 修復排序再次錯誤

### 問題
用戶反映章節排序再次出現錯誤（84→85→86→87 → 正確應該是 87→86→85→84→...）

### 根本原因
`sort_av_novels_chapters()` 函數邏輯有問題：
- 檢查是否已排序時，`is_already_sorted` 判斷失誤
- 排序後應該立刻驗證，但代碼流程有缺陷

### 修復
1. 手動運行排序腳本
2. 驗證排序後：87→86→85→84→83→82... 正確
3. 重新提交 av-novels.html

### 驗證結果
```
修復前：chapter-84-av → chapter-85-av → chapter-86-av → chapter-87-av → chapter-83-av (錯誤)
修復後：chapter-87-av → chapter-86-av → chapter-85-av → chapter-84-av → chapter-83-av (正確)
```

### 預防措施
- 發現排序問題時，立即運行 `sort_av_novels_chapters()` 修復
- 推送前驗證章節順序

---

## [2026-04-24] v2.2.17 修復腳本排序問題

### 問題
用戶指出：只修復網站的章節排序是不夠的，生成腳本也必須修復。

### 根本原因
1. `novel-daily-generator.sh` - 每日文字章節生成後**從不排序** av-novels.html
2. `update_author_stats.py` - 只更新統計數字，**不涉及排序**

### 修復內容

#### 1. `update_author_stats.py`
新增 `sort_av_novels_chapters()` 函數（在 main() 末尾調用）：
```python
# 排序 av-novels.html 章節（確保最新章節在最前面）
print(f"\n🔄 排序 av-novels.html 章節...")
sort_av_novels_chapters(NOVEL_DIR)
```

#### 2. `novel-daily-generator.sh`
在更新統計數字後，調用 `update_author_stats.py` 執行排序：
```bash
# 排序章節順序（確保正確）
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 排序章節順序..." >> "$LOG_FILE"
python3 "$WORKSPACE/scripts/update_author_stats.py" >> "$LOG_FILE" 2>&1
```

### 排序邏輯
- 提取所有 chapter-card
- 按章節號降序排序（87→86→85→...→1）
- 重建 grid 並寫回文件

### 驗證
- ✅ 推送前檢查通過（87個章節全部在目錄中）
- ✅ 章節順序正確（87→86→85→84→...）

---

## [2026-10-23] 更新 (v2.2.18) - 指向 v2.9.97 兩項教訓

- V4 退役條目應「註釋」而非刪除（避免日後被 guardian 當成意外遺失而加返）
- 併發寫 Dropbox token 嘅正解 = tmp + os.replace() 原子寫入（唔係靠錯開時間）

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

## [2026-10-28] 更新 - 卡住 rebase + Detached HEAD 自動修復

- 本地 finance-data commit 撞 GitHub Actions 同日更新 → rebase 衝突 + Detached HEAD；已 abort + reset --hard origin/main（遠端較新）+ git-health-check --fix，驗證健康

---
## [2026-10-28] 更新 - chat-worker 依賴目錄入 .gitignore + chapter-titles 章數修正

### 修復內容（隔離 session 執行，小肥喵補記 skill 日誌）
- .gitignore 補 node_modules/（原本缺失，150M 未追蹤依賴目錄）；補交 package-lock.json
- chat-worker assets/chapter-titles.json 由 1776 章修正至 1782 章（對齊 assets/chapters-data.json 零分歧）
- commit 399645001 已 push（origin/main、Second-brain、Max-backup 均 0 未推送）

### 教訓
- Node 依賴目錄必須入 .gitignore，否則未追蹤依賴會令 push/clone 體積失控
- 章節標題索引（chapter-titles.json）同主索引（chapters-data.json）要同批更新，否則網站前端會少 6 章


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
- 解完衝突要即刻驗檔案內容，唔好等到下一次巡檢先發現---
## [2026-11-10] 更新 - 兩重大事故（cron 全線爆一日 + git rebase 衝突）

### 事故一：6 個 agentTurn cron job 由 11-09 起全線爆（ Automation candidate is incompatible with its recorded inference account and route.）
- 症狀：11-09 傍晚簡報起，傍晚簡報 / 健康報告 / 早上簡報 / Audio Sync / 版本檢查 / 中午簡報 全部 error，一日冇簡報送到
- 真因：2026.11.1 規則下 job 記錄住一個 inference account + route；candidate provider ≠ 記錄 account 就直接 throw，唔會靜默切換
- 觸發：我 11-08 為咗救 Audio Sync 幫 6 個 job 嘅 fallback 綁咗 @openrouter:default —— 呢個令 job 記錄 account 變咗 openrouter，之後 primary（minimax）候選就同記錄 account 唔相容
- 修復順序（關鍵，已實測）：每條 fallback 各自帶 @profile（例：openrouter/xxx@openrouter:default，切換時先可被採用），並且「最後」才綁 primary model@profile（minimax/MiniMax-M3.1-Flash@minimax:cn）—— 最後一次 account 選擇決定 job 記錄嘅 inference account，順序錯（例如先改 fallback 再改 primary）就會令 primary 候選與記錄 account 不相容→ 2026-11-10 6 個 agentTurn job 全部 error 近一日；重綁後早上簡報 17:15、Audio Sync 17:27、版本檢查 17:08 全部 ok + delivered

### 事故二：git 卡喺 rebase 衝突（finance-news.json / finance-data.json）
- 根因：update_finance.sh / update_finance_news.sh / update_aqhi.sh / news-backup-cron.sh 同一分鐘（10,16 點）各自 git add + commit + pull --rebase，撞同一批 JSON
- 修復：新增 scripts/git-commit-locked.sh（add+commit 統一用 .git-push.lock）；news-backup-cron.sh 同 update_aqhi.sh 直接加 flock；財經兩個 script 改用 helper
- 處理手法：git rebase --abort → 逐個 conflict 取「正在套用嘅 commit」版本（stage 3 / theirs）→ git add → GIT_EDITOR=true git rebase --continue

### 教訓
- 改 job 嘅 fallback 唔可以隨便加 @profile：會改到 job 記錄嘅 inference account，令 primary 候選反過來不相容
- 修 account 要「先清 fallback 綁定、最後綁 primary@profile」，順序錯會越修越壞
- 多個 cron script 同一分鐘做 git 一定會撞：所有 commit + pull --rebase 都要同一把 flock
- 判斷 job 係咪真死，要睇 state.lastError 全文（Automation candidate is incompatible…）而唔係淨係睇 errs 數字---
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
- 修完要逐個 force run 驗證（errs 歸零 + lastRunStatus=ok + delivered=true）---
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

## [2026-11-10] 更新 (v2.2.37) - 記憶檔每日被自動 logger 寫入 demo 假記錄（同步 standards v2.9.149）

- `scripts/auto-memory-logger.py` 的 `__main__` 原來係硬編碼 demo 測試碼，system cron 每日 23:00 執行 → 216 個記憶檔被寫入假條目（abc123 / scripts/test1.py）。
- 已改成記錄真實 git 提交（單一每日摘要條目 + hash 去重），並清理 workspace + 兩個備份倉嘅污染。
- 詳細記錄見 novel-site-standards v2.9.149。

---

## [2026-11-11] 更新 (v2.2.38) - 記憶 logger 摘要格式修正（同步 standards v2.9.150）

- `log_to_memory()` 傳 list 會逐行加 `- ` 前綴，令摘要變 `- - ...`；改傳單一 string 後格式正常。
- 詳細見 novel-site-standards v2.9.150。

---

## [2026-11-11] 更新 (v2.2.39) - code-mode 提示覆蓋全部 6 個 agentTurn job + guardian 模板（同步 standards v2.9.152）

- code mode 入面 `tools` 全域唔存在，用 `exec({command: ...})` 直接呼叫；寫 `tools.exec(...)` 會 ReferenceError，令成個 cron run 空轉到 LLM idle timeout。
- 提示已加落全部 6 個 agentTurn job message + `scripts/cron-guardian.sh` 6 個重建 block。
- 詳細見 novel-site-standards v2.9.152。

---

## [2026-11-11] 更新 (v2.2.40) - minimax 單一 account 同 provider failover（同步 standards v2.9.153）

- `auth.profiles` 只有 `minimax:cn` 一條 profile → minimax 靜默時全部 agentTurn job 都冇退路（跨 provider fallback 會 hard-fail，唔算後備）。
- 真後備 = 加第二條 Minimax key → 新 profile → 加落 `auth.order`。
- 詳細見 novel-site-standards v2.9.153。

---

## [2026-11-11] 更新 (v2.2.39) - push 腳本 auto-stash 靜靜吞內容（同步 standards v2.9.154）

- `git stash push -u` + `git reset --hard` + `git stash pop` 衝突時，改動留喺 stash 靜靜消失（2026-10-09 兩篇 DREAMS.md 夢境咁樣失蹤一個月）。
- 已改成 commit-first + 衝突導出 patch + `git-health-check.sh` 主動偵測殘留 stash。
- 詳細見 novel-site-standards v2.9.154。

---

## [2026-11-11] 更新 (v2.2.42) - cron agent job fallback 鏈修正（同步 standards v2.9.155）

- cron job 嘅 `fallbacks` 同 `model` 相同 → 429 限流時零回退，簡報 job 靜靜失敗（12:55 中午簡報今日冇送達）。
- 修正：每個 agent job 補上 5 個 `Auth: yes` 嘅 openrouter free 模型做實體 fallback；`openclaw cron edit` 會重寫 `timeoutSeconds`，edit 時必須顯式帶原值。
- 詳細見 novel-site-standards v2.9.155。

