# DeepSeek原生API設置指南

## 當前狀態

### 已配置的生成方案：
1. **OpenRouter版** (`generate_chapter_deepseek.py`)
   - 模型：`deepseek/deepseek-v3.2` (通過OpenRouter)
   - 狀態：✅ 已配置，API連接測試成功
   - 問題：通過第三方平台，非原生

2. **原生API版** (`generate_chapter_deepseek_native.py`)
   - 模型：`deepseek-chat` (DeepSeek-V3.2非思考模式)
   - 狀態：⚠️ 需要API密鑰
   - 優勢：直接使用官方API

3. **直接版** (`generate_chapter_direct.py`)
   - 方法：複製修改現有章節
   - 狀態：✅ 完全工作，作為備用方案

## 設置DeepSeek原生API

### 步驟1：申請API密鑰
1. 訪問：https://platform.deepseek.com/api_keys
2. 註冊/登錄DeepSeek賬號
3. 創建新的API密鑰
4. 複製密鑰（格式如：`sk-...xxxxxxxx`）

### 步驟2：配置密鑰
在 `.env` 文件中添加：
```bash
DEEPSEEK_API_KEY=sk-...你的API密鑰
```

或運行：
```bash
echo "DEEPSEEK_API_KEY=sk-...你的API密鑰" >> /home/openclaw/.openclaw/workspace/.env
```

### 步驟3：測試API連接
```bash
cd /home/openclaw/.openclaw/workspace
python3 scripts/test_deepseek_native.py
```

## API對比

| 特性 | OpenRouter版 | 原生API版 |
|------|-------------|-----------|
| **模型** | deepseek/deepseek-v3.2 | deepseek-chat (V3.2) |
| **上下文** | 163,840 tokens | 128,000 tokens |
| **成本** | OpenRouter定價 | DeepSeek官方定價 |
| **直接性** | 通過第三方 | 直接官方API |
| **穩定性** | 取決於OpenRouter | 取決於DeepSeek |
| **當前狀態** | ✅ 已配置 | ⚠️ 需要密鑰 |

## 定價參考（DeepSeek官方）
- **輸入**: ¥0.002元/千tokens
- **輸出**: ¥0.003元/千tokens
- **估算**: 每章2000字 ≈ 3000 tokens ≈ ¥0.015元

## 系統架構選擇

### 選項A：使用原生API（推薦）
```bash
# 修改 shell 腳本使用原生API
sed -i 's/generate_chapter_deepseek\.py/generate_chapter_deepseek_native.py/g' scripts/novel-daily-generator.sh
```

### 選項B：保持當前配置（OpenRouter）
- 優點：已測試工作
- 缺點：通過第三方

### 選項C：混合方案
```bash
# 優先嘗試原生API，失敗時用OpenRouter，再失敗用直接版
# 需要修改 shell 腳本實現三層回退
```

## 測試建議

1. **先測試API連接**
   ```bash
   curl -s -H "Authorization: Bearer YOUR_KEY" \
        -H "Content-Type: application/json" \
        -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"Hello"}]}' \
        https://api.deepseek.com/chat/completions
   ```

2. **測試生成質量**
   ```bash
   python3 scripts/generate_chapter_deepseek_native.py
   ```

3. **監控成本**
   - 記錄每次生成的token使用量
   - 估算月度成本

## 故障排除

### 常見問題：
1. **API密鑰無效**：檢查密鑰格式，重新申請
2. **請求超時**：增加timeout時間（腳本已設30秒）
3. **內容過短**：調整提示詞，增加max_tokens
4. **網絡問題**：檢查防火牆，確保能訪問api.deepseek.com

### 備用方案：
如果原生API有問題，可隨時切回：
```bash
# 切回OpenRouter版
sed -i 's/generate_chapter_deepseek_native\.py/generate_chapter_deepseek.py/g' scripts/novel-daily-generator.sh

# 或直接使用備用方案
sed -i 's/generate_chapter_deepseek.*\.py/generate_chapter_direct.py/g' scripts/novel-daily-generator.sh
```

## 下一步行動

1. **立即行動**：申請DeepSeek API密鑰並配置
2. **測試驗證**：運行測試腳本確認工作正常
3. **成本評估**：生成幾章後評估實際成本
4. **正式切換**：更新定時任務使用原生API

---

**最後更新**：2026-03-27 09:55 HKT  
**文檔維護**：小肥喵 🐱