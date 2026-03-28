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
| Seedream 4.5 | `seedream-4-5-251128` | 需 Token 有權限 |
| Seedream 4.0 | `seedream-4-0-250828` | 需 Token 有權限 |
| Gemini 3 Pro | `gemini-3-pro-image-preview` | ✅ 已確認可用 |

### 快速調用
```bash
# Gemini 3 Pro（已確認可用）
# Gemini 3 Pro（已確認可用）
SEEDREAM_API_KEY="sk-...45382" \
python3 .../generate_image.py \
  --prompt "描述" --model "gemini-3-pro-image-preview" --size "1024x1024"

# Seedream 4.5
SEEDREAM_API_KEY="sk-...45382" \
python3 .../generate_image.py --prompt "描述" --model "seedream-4-5-251128"
```

---

Add whatever helps you do your job. This is your cheat sheet.
