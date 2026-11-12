#!/bin/bash
# Skill 四處副本自動對齊（根治漂移復發）
# 已安裝 / workspace 副本 / Second-brain / Max-backup —— 以版本號最高嗰份為準
set -u
SK=/home/openclaw/.openclaw/skills/novel-site-standards
AV=/home/openclaw/.openclaw/skills/novel-av-generator
WS=/home/openclaw/.openclaw/workspace/.openclaw/skills/novel-site-standards
WS_AV=/home/openclaw/.openclaw/workspace/.openclaw/skills/novel-av-generator
SB=/home/openclaw/Second-brain/skills/novel-site-standards
MB=/home/openclaw/Max-backup/skills/novel-site-standards
LOG=/home/openclaw/.openclaw/workspace/logs/skill-sync.log
mkdir -p "$(dirname "$LOG")"
log() { echo "[$(date "+%F %T")] $*" >> "$LOG"; }
ver() { grep -m1 "^version:" "$1" 2>/dev/null | awk "{print \$2}"; }
sync_set() {
  local label=$1; shift
  local best="" bestv=""
  for f in "$@"; do
    [ -f "$f" ] || continue
    local v=$(ver "$f")
    [ -n "$v" ] || continue
    if [ -z "$bestv" ] || [ "$(printf "%s\n%s\n" "$bestv" "$v" | sort -V | tail -1)" = "$v" ]; then bestv="$v"; best="$f"; fi
  done
  [ -z "$best" ] && return 0
  local changed=0
  for f in "$@"; do
    if ! cmp -s "$best" "$f"; then cp "$best" "$f"; changed=1; fi
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
      git push >/dev/null 2>&1
    fi
  fi
  return 0
}
sync_set standards "$SK/SKILL.md" "$WS/SKILL.md" "$SB/SKILL.md" "$MB/SKILL.md"
sync_set standards-history "$SK/SKILL_HISTORY.md" "$WS/SKILL_HISTORY.md" "$SB/SKILL_HISTORY.md" "$MB/SKILL_HISTORY.md"
sync_set av "$AV/SKILL.md" "$WS_AV/SKILL.md" "$SB/skills/novel-av-generator/SKILL.md" "$MB/skills/novel-av-generator/SKILL.md"
log "done"
