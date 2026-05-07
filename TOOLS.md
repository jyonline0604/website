# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## AI 圖片生成

### 老張AI（laozhang.ai）- 預設
- **API Key**: `sk-...45382` (完整密鑰保存在安全位置)
- **Base URL**: `https://api.laozhang.ai/v1`
- **技能**: `/home/openclaw/.openclaw/skills/seedream-image-gen/`

#### 可用模型
| 模型 | ID | 備註 |
|------|-----|------|
| **MiniMax Image-01** | `image-01` | ✅ **預設模型** |
| Seedream 4.5 | `seedream-4-5-251128` | 需 Token 有權限 |
| Seedream 4.0 | `seedream-4-0-250828` | 需 Token 有權限 |
| Gemini 3 Pro | `gemini-3-pro-image-preview` | 備用 |

### 快速調用
```bash
# MiniMax Image-01（預設）
SEEDREAM_API_KEY="sk-...45382" \
python3 .../generate_image.py \
  --prompt "描述" --model "image-01" --size "1024x1024"

# Gemini 3 Pro（備用）
SEEDREAM_API_KEY="sk-...45382" \
python3 .../generate_image.py \
  --prompt "描述" --model "gemini-3-pro-image-preview" --size "1024x1024"
```

---

Add whatever helps you do your job. This is your cheat sheet.

---

## 🎤 語音合成（收藏）

### OmniVoice（待測試）
- **URL**: https://github.com/k2-fsa/OmniVoice
- **功能**: 600+語言零樣本TTS、聲音克隆、屬性控制
- **優勢**: 聲音質量可能比 Edge TTS 更好
- **需求**: GPU 或 Apple Silicon
- **狀態**: 收藏中

---

## 🚀 Dropbox 小説自動化（2026-05-07 新增）

### Dropbox 賬號
- **Email**: hotcha2028@gmail.com
- **Name**: Lam liu
- **資料夾**: `/萬古塵埃/第二卷/` (CH501-CH700)

### Token
- 位置：`.token-store/dropbox-token.txt` (600 權限)
- 類型：OAuth2 Access Token

### 自動化腳本
- **主腳本**: `scripts/dropbox_volume2_sync.py` — 下載、轉換、生成HTML、更新網站、推送GitHub
- **Cron Shell**: `scripts/dropbox-daily-sync.sh`

### Cron 定時任務
| 時間 | 任務 | 頻率 |
|------|------|------|
| 08:00 | Dropbox第二卷同步6章 | 每天 |

### 功能
- 自動檢測 Dropbox 新章節
- 簡體→繁體轉換
- HTML模板生成（使用 chapter-template.html）
- 更新 chapters.html + home.html
- GitHub 推送
- 狀態追蹤（`.dropbox-sync/volume2_state.json`）

### 流程
1. 掃描 Dropbox/第二卷 → 比對本地已有章節
2. 取前6章未處理的
3. 下載 → 簡轉繁 → 生成 HTML → 驗證 → 更新網站 → 推送 GitHub
