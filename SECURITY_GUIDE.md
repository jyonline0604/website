# 安全指南 - API密鑰保護

## 重要原則
**永遠不要在輸出、日誌、代碼或對話中顯示完整的API密鑰。**

## 安全實踐

### 1. 文件權限
```bash
# .env文件應該只有所有者可讀寫
chmod 600 .env

# 檢查權限
ls -la .env  # 應該顯示 -rw-------
```

### 2. 安全顯示
在輸出中只顯示密鑰的部分字符：
```python
# ❌ 不安全
print(f"API密鑰: {api_key}")

# ✅ 安全
print(f"API密鑰: {api_key[:8]}...{api_key[-4:]}")
```

### 3. 日誌記錄
- 不要在日誌中記錄完整密鑰
- 使用環境變量而不是硬編碼
- 定期清理舊日誌

### 4. 代碼審查
定期運行安全檢查：
```bash
python3 scripts/security_check.py
```

## 當前配置狀態

### 已保護的密鑰
1. **OpenRouter API密鑰** - 保存在.env文件
2. **DeepSeek API密鑰** - 保存在.env文件

### 安全措施
- ✅ .env文件權限：600（僅所有者可讀寫）
- ✅ 腳本使用安全顯示
- ✅ 日誌中無完整密鑰
- ✅ 記憶檔中無完整密鑰

## 緊急處理

如果密鑰意外泄露：
1. **立即撤銷**：在對應平台撤銷泄露的密鑰
2. **生成新密鑰**：創建新的API密鑰
3. **更新配置**：更新.env文件中的密鑰
4. **檢查日誌**：清理可能包含舊密鑰的日誌

## 定期檢查
建議每週運行一次安全檢查：
```bash
# 檢查API密鑰安全
python3 scripts/security_check.py

# 檢查文件權限
find /home/openclaw/.openclaw/workspace -name "*.env*" -o -name "*config*" | xargs ls -la

# 檢查日誌中的敏感信息
grep -r "sk-" /home/openclaw/.openclaw/workspace/logs/ 2>/dev/null | head -5
```

## 開發者注意
編寫新腳本時：
1. 從環境變量讀取密鑰，不要硬編碼
2. 輸出時使用安全顯示函數
3. 測試時使用測試密鑰或環境變量
4. 提交代碼前檢查是否包含敏感信息

---

**最後更新**：2026-03-27 10:05 HKT  
**安全負責**：小肥喵 🐱