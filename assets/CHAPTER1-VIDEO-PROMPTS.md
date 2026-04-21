# 第1章 - 視頻生成Prompt設定

## 場景1：廢土黎明
**時間**: 5秒
**Prompt**:
```
A young Chinese man in tattered military blanket crouching in darkness of abandoned skyscraper, cyberpunk wasteland atmosphere,铅云笼罩的天空, dim moonlight filtering through broken windows, ruins of advanced technology around, dust particles floating, tense and dramatic, cinematic composition
```
**氛圍**: 緊張、壓抑、神秘

---

## 場景2：靈芯覺醒
**時間**: 5秒
**Prompt**:
```
Close-up of a young man's face illuminated by glowing blue chip, ancient black crystal chip embedded in wall glowing with ethereal blue light, dust and cobwebs around, his eyes widening in shock, electricity particles flowing from chip to his mind, dramatic light rays, mystical sci-fi atmosphere
```
**氛圍**: 震撼、神秘、科技感

---

## 場面3：系統激活
**時間**: 5秒
**Prompt**:
```
Young Chinese man sitting meditation pose, holographic blue interface floating in his mind showing cultivation system interface, data streams and meridian maps appearing in air around him, soft blue glow emanating from his body, ethereal atmosphere, mystical tech fusion
```
**氛圍**: 奇幻、超凡、期待

---

## 場面4：靈氣吸納
**時間**: 5秒
**Prompt**:
```
Young Chinese man in meditation, wisps of white spiritual energy flowing from air into his body, subtle golden light particles surrounding him, dramatic backlighting, calm focused expression, cultivation world aesthetic, cinematic meditation scene
```
**氛圍**: 寧靜、神奇、修煉感

---

## 場面5：極速逃亡
**時間**: 5秒
**Prompt**:
```
Young man leaping through ventilation shafts in abandoned cyberpunk building, cables and broken pipes around, blue glow trail behind him, camera following his fast movement, dust trails in air, dynamic action sequence, dramatic speed lines
```
**氛圍**: 緊張、刺激、速度感

---

## 場面6：堅定眼神（結尾）
**時間**: 5秒
**Prompt**:
```
Close-up of young Chinese man's eyes, determined and resolute gaze, blue energy faintly glowing in his pupils, lying in dark underground passage, shadows on face, dramatic lighting from above, epic inspirational mood, cinematic portrait
```
**氛圍**: 決心、轉折、希望

---

## 使用說明

### Seedance 2.0 Fast API 格式
```python
response = requests.post(
    url="https://openrouter.ai/api/v1/videos",
    headers={"Authorization": f"Bearer {API_KEY}"},
    data=json.dumps({
        "model": "bytedance/seedance-2.0-fast",
        "prompt": "完整Prompt文字"
    })
)
```

### 建議生成順序
1. 場面1 - 廢土黎明（開場）
2. 場面2 - 靈芯覺醒（高潮1）
3. 場面3 - 系統激活（過渡）
4. 場面4 - 靈氣吸納（修煉）
5. 場面5 - 極速逃亡（動作）
6. 場面6 - 堅定眼神（結尾）

### 總時長
約30秒，可以剪輯成一個完整的預告片

---

## 角色外觀提醒

生成林塵時，確保包含：
- 短黑髮、髮尾藍光
- 24歲年輕人
- 堅定冷靜的眼神
- 未來風格戰甲痕跡（可選）
- 量子靈芯光效