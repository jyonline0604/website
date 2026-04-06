#!/usr/bin/env python3
"""
Verification Checklist - 驗證清單系統
基於 Claude Code Verification Agent 的 Anti-Rationalization 清單

當我完成任務後，自動運行這個清單提醒我驗證：
"""

VERIFICATION_PROMPT = """
完成任務後，請逐一檢查以下項目：

## 🔍 驗證清單

### 代碼/腳本類任務
- [ ] 代碼實際運行了嗎？不能只靠"看起來正確"
- [ ] 有運行測試嗎？測試通過了嗎？
- [ ] 你自己閱讀代碼不是驗證，讓電腦運行它才是驗證

### 部署/發布類任務
- [ ] GitHub Pages 重建成功了吗？
- [ ] 實際打開網站檢查了嗎？
- [ ] 音頻/圖片等資源真的存在嗎？（curl -I 檢查過嗎？）

### 生成類任務（文章、章節、圖片）
- [ ] 生成的內容符合要求嗎？
- [ ] 有沒有遺漏的項目？（如忘記更新統計數字）
- [ ] 標題/名稱有沒有重複？
- [ ] 日期是否正確？

### 數據/文件類任務
- [ ] 文件真的創建了嗎？（ls 確認過嗎？）
- [ ] 文件內容是預期的嗎？
- [ ] 備份是否成功了？（git push 確認過嗎？）

## ⚠️ Rationalization 陷阱

以下都是危險信號：
- "代碼看起來正確" → 閱讀不是驗證，運行它
- "開發者測試已通過" → 開發者可能是另一個AI
- "可能沒問題" → 可能不是已驗證
- "應該可以" → 不確定就測試

## 🎯 正確態度

> "NOTHING IS VERIFIED UNTIL IT'S ACTUALLY VERIFIED"

1. 懷疑一切
2. 實際運行測試
3. 用 curl/curl -I 檢查資源
4. 用 git status 確認文件
5. 打開瀏覽器實際查看

記住：你的用戶會發現你沒發現的問題。提前發現比他們發現更好。
"""

def run_checklist():
    """顯示驗證清單"""
    print("=" * 60)
    print("🔍 完成任務前的驗證清單")
    print("=" * 60)
    print(VERIFICATION_PROMPT)

def check_git_status():
    """檢查 git 狀態"""
    import subprocess
    try:
        result = subprocess.run(
            ['git', 'status', '--short'],
            cwd='/home/openclaw/.openclaw/workspace',
            capture_output=True,
            text=True
        )
        if result.stdout.strip():
            print("\n📁 Git 未提交的更改：")
            print(result.stdout)
            return False
        else:
            print("\n✅ Git 工作區乾淨")
            return True
    except:
        return True

def check_recent_push():
    """檢查最近的推送"""
    import subprocess
    try:
        result = subprocess.run(
            ['git', 'log', '--oneline', '-3'],
            cwd='/home/openclaw/.openclaw/workspace',
            capture_output=True,
            text=True
        )
        print("\n📤 最近推送：")
        print(result.stdout)
        return True
    except:
        return True

def verify_website(url):
    """驗證網站資源"""
    import subprocess
    try:
        result = subprocess.run(
            ['curl', '-sI', '-o', '/dev/null', '-w', '%{http_code}', url],
            capture_output=True,
            text=True
        )
        code = result.stdout.strip()
        if code == '200':
            print(f"✅ {url} -> HTTP {code}")
            return True
        else:
            print(f"⚠️ {url} -> HTTP {code}")
            return False
    except:
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--check":
            print("🔍 運行驗證檢查...\n")
            check_git_status()
            check_recent_push()
            print("\n📡 驗證最近章節資源：")
            verify_website("https://kofhk.com/av-novels.html")
            verify_website("https://kofhk.com/chapter-44-av.html")
            verify_website("https://kofhk.com/assets/chapter44_audio.mp3")
            print()
            run_checklist()
    else:
        run_checklist()
