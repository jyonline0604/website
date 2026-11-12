#!/bin/bash
# Skill 四處副本自動對齊（根治漂移復發）
# 已安裝 / workspace 副本 / Second-brain / Max-backup —— 以版本號最高嗰份為準
# 2026-11-12 v2：修正 av 路徑 bug（$SB/../novel-av-generator 解析去不存在目錄 → 靜默失敗）
#                  + 目標目錄自動建立 + cp 失敗即報警（唔再吞錯）
set -u
SK_DIR=/home/openclaw/.openclaw/skills/novel-site-standards
AV_DIR=/home/openclaw/.openclaw/skills/novel-av-generator
WS_DIR=/home/openclaw/.openclaw/workspace/.openclaw/skills
SB_DIR=/home/openclaw/Second-brain/skills
MB_DIR=/home/openclaw/Max-backup/skills
SK=$SK_DIR/SKILL.md
AV=$AV_DIR/SKILL.md
WS=$WS_DIR/novel-site-standards/SKILL.md
WS_AV=$WS_DIR/novel-av-generator/SKILL.md
SB=$SB_DIR/novel-site-standards/SKILL.md
MB=$MB_DIR/novel-site-standards/SKILL.md
LOG=/home/openclaw/.openclaw/workspace/logs/skill-sync.log
mkdir -p "$(dirname "$LOG")"
log() { echo "[$(date "+%F %T")] $*" >> "$LOG"; echo "[$(date "+%F %T")] $*"; }
ver() { grep -m1 "^version:" "$1" 2>/dev/null | awk "{print \$2}"; }
sync_set() {
  local label=$1; shift
  local best="" bestv=""
  for f in "$@"; do
    [ -f "$f" ] || continue
    local v=$(ver "$f")
    [ -n "$v" ] || continue
    if [ -z "$bestv" ] || [ "$(printf "%s\n%s\n" "$bestv" "$v" | sort -V | tail -1)" = "$v" ]; then bestv=$v; best=$f; fi
  done
  [ -z "$best" ] && return 0
  local changed=0 failed=0
  for f in "$@"; do
    local d; d=$(dirname "$f")
    if [ ! -d "$d" ]; then
      mkdir -p "$d" 2>/dev/null || { log "$label 目標目錄建立失敗：$d"; failed=1; continue; }
      log "$label 建立目標目錄 $d"
    fi
    if ! cmp -s "$best" "$f"; then
      if cp "$best" "$f"; then changed=1; else log "$label 複製失敗：$best -> $f"; failed=1; fi
    fi
  done
  if [ "$changed" = "1" ]; then
    log "$label 對齊 -> v$(ver "$best") (基準 $(basename "$(dirname "$best")"))"
    for repo in /home/openclaw/Second-brain /home/openclaw/Max-backup; do
      cd "$repo" || continue
      if [ -n "$(git status --short skills/ 2>/dev/null)" ]; then
        git add skills/ >/dev/null 2>&1
        git commit -m "chore: skill 副本自動對齊 (nightly sync)" >/dev/null 2>&1
        git pull --rebase -q >/dev/null 2>&1
        git push >/dev/null 2>&1 && log "pushed $repo"
      fi
    done
    cd /home/openclaw/.openclaw/workspace
    if [ -n "$(git status --short .openclaw/ 2>/dev/null)" ]; then
      git add -f .openclaw/skills/ >/dev/null 2>&1
      git commit -m "docs: skill 副本自動對齊 (nightly sync)" >/dev/null 2>&1
      git pull --rebase -q >/dev/null 2>&1
      git push >/dev/null 2>&1 && log "pushed workspace (.openclaw/skills)"
    fi
  fi
  [ "$failed" = "1" ] && log "$label 有複製失敗項目 ⚠️ 需要人手檢查"
  return 0
}
sync_set standards "$SK" "$WS" "$SB" "$MB"
sync_set standards-history "$SK_DIR/SKILL_HISTORY.md" "$WS_DIR/novel-site-standards/SKILL_HISTORY.md" "$SB_DIR/novel-site-standards/SKILL_HISTORY.md" "$MB_DIR/novel-site-standards/SKILL_HISTORY.md"
sync_set av "$AV" "$WS_AV" "$SB_DIR/novel-av-generator/SKILL.md" "$MB_DIR/novel-av-generator/SKILL.md"
log "done"
