#!/usr/bin/env bash
# ops-snapshot.sh — 一次過攞齊 OpenClaw 系統現況（唯讀，唔改任何嘢）
# 用法: bash scripts/ops-snapshot.sh [workspace]
# canonical 副本：workspace/scripts/ops-snapshot.sh  ≡  skill openclaw-selfheal-ops/scripts/ops-snapshot.sh（內容一致）
set -uo pipefail
WS="${1:-/home/openclaw/.openclaw/workspace}"
cd "$WS" || exit 1

echo "=== 1. 時間 ==="
date '+%F %T %Z'

echo "=== 2. Gateway / 版本 ==="
openclaw --version 2>&1 | head -1
systemctl --user show openclaw-gateway.service -p MainPID,ActiveEnterTimestamp 2>/dev/null
echo "--- 最近 stability 記錄（有 = 有崩潰/重啟異常）---"
ls -t "$HOME/.openclaw/logs/stability/" 2>/dev/null | head -3

echo "=== 3. 網站 ==="
curl -s -o /dev/null -w "kofhk.com: %{http_code} %{time_total}s\n" --max-time 10 https://kofhk.com/ 2>/dev/null

echo "=== 4. Cron jobs（名／errs／fallback 層數／lastRun）==="
openclaw cron list --json 2>/dev/null | python3 -c '
import json,sys,datetime
from collections import Counter
d=json.load(sys.stdin)
jobs=d if isinstance(d,list) else (d.get("jobs") or d.get("automations") or [])
c=Counter((j.get("name") or "") for j in jobs)
dup={n:k for n,k in c.items() if k>1}
tot=0
for j in jobs:
    st=j.get("state",{}) or {}
    ce=st.get("consecutiveErrors") or 0
    tot+=ce
    ts=datetime.datetime.fromtimestamp(st["lastRunAtMs"]/1000).strftime("%m-%d %H:%M") if st.get("lastRunAtMs") else "-"
    p=j.get("payload") or {}
    print("  %-8s %-28s errs=%s fb=%d last=%s status=%s" % ((j.get("id") or "")[:8],(j.get("name") or "")[:28],ce,len(p.get("fallbacks") or []),ts,st.get("lastRunStatus") or "-"))
print("  總數 %d | errs 合計 %d | 重複名 %s" % (len(jobs),tot,dup or "無"))
'

echo "=== 5. 模型可用性（近 30 分鐘 provider status）==="
journalctl --user -u openclaw-gateway.service --since "30 min ago" --no-pager 2>/dev/null | grep -oE "provider=[a-z]+ .*status=[0-9]+" | tail -4

echo "=== 6. 記憶檔 ==="
wc -l "$WS/MEMORY.md" 2>/dev/null | awk '{print "  MEMORY.md 行數:", $1}'
ls -t "$WS"/memory/*.md 2>/dev/null | head -3 | sed 's/^/  /'

echo "=== 7. Git（三倉 + hooks + 敏感檔 + 章節數）==="
for r in "$WS" /home/openclaw/Second-brain /home/openclaw/Max-backup; do
  if cd "$r" 2>/dev/null; then
    echo "  $(basename "$r"): 未推送 $(git rev-list --count origin/main..HEAD 2>/dev/null) | 髒檔 $(git status --porcelain | wc -l) | HEAD $(git rev-parse --short HEAD 2>/dev/null)"
  fi
done
cd "$WS"
echo -n "  hooks: "; ls .git/hooks/pre-commit .git/hooks/pre-push 2>/dev/null | wc -l
echo -n "  敏感檔命中: "; git status --short 2>/dev/null | grep -cE "openclaw.json|\.backup-pass|api_key|github_pat|sk-" || true
echo -n "  章節檔案數: "; ls chapter-*.html 2>/dev/null | wc -l

echo "=== 8. Skill 副本唯一性 ==="
SK=/home/openclaw/.openclaw/skills/novel-site-standards/SKILL.md
for f in "$SK" "$WS/.openclaw/skills/novel-site-standards/SKILL.md" /home/openclaw/Second-brain/skills/novel-site-standards/SKILL.md /home/openclaw/Max-backup/skills/novel-site-standards/SKILL.md; do
  [ -f "$f" ] && printf "  %s %s\n" "$(md5sum "$f" | awk '{print $1}')" "$f"
done
echo "  唯一 md5 數: $(md5sum "$SK" "$WS/.openclaw/skills/novel-site-standards/SKILL.md" /home/openclaw/Second-brain/skills/novel-site-standards/SKILL.md /home/openclaw/Max-backup/skills/novel-site-standards/SKILL.md 2>/dev/null | awk '{print $1}' | sort -u | wc -l)"

echo "=== 9. Dropbox state + token 新鮮度 ==="
ls "$WS"/.dropbox-sync/volume*_state.json 2>/dev/null | sed 's/^/  /'
TOK="$WS/.token-store/dropbox-token.txt"
if [ -f "$TOK" ]; then echo "  token $(wc -c < "$TOK") bytes | 最後續期 $(stat -c %y "$TOK" 2>/dev/null | cut -d. -f1)"; else echo "  token 檔缺失: $TOK"; fi

echo "=== 10. system cron（非註釋行數）==="
echo "  $(crontab -l 2>/dev/null | grep -vE '^[[:space:]]*#' | grep -c .) 行"

echo "=== 完 ==="
