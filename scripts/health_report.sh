#!/usr/bin/env bash
# health_report.sh — 每日健康報告（22:00 job）嘅單一入口
#
# 設計目標（2026-11-12）：cron job 只需要做 **一次** exec（行呢個 script），
# 唔使喺 code mode 入面逐項手寫指令。
# 原因：實測 22:00 job 喺 code mode 內誤寫 tools.exec(...) → ReferenceError 3 次，
#       每次都要重試，加上 minimax 429，令成個 run 由正常 5 分鐘拖到 21 分鐘。
#       減少 code mode 呼叫次數 = 減少 ReferenceError 同 429 嘅暴露面。
#
# 用法: bash scripts/health_report.sh
set -uo pipefail
WS=/home/openclaw/.openclaw/workspace
cd "$WS" || exit 1

echo "=== [A] 現況快照（唯讀）==="
bash "$WS/scripts/ops-snapshot.sh" "$WS"

echo "=== [B] 自動修復 ==="
REPAIRED=()
FAILED=()

# --- B1. Git：三倉未推送 commit → push（先 rebase 避免撞 CI commit）---
for r in "$WS" /home/openclaw/Second-brain /home/openclaw/Max-backup; do
  name=$(basename "$r")
  ahead=$(git -C "$r" rev-list --count @{u}..HEAD 2>/dev/null || echo 0)
  if [ "${ahead:-0}" -gt 0 ] 2>/dev/null; then
    if git -C "$r" pull --rebase -q origin main >/dev/null 2>&1 && git -C "$r" push -q origin main >/dev/null 2>&1; then
      REPAIRED+=("git push $name（$ahead 個 commit）")
    else
      FAILED+=("git push $name 失敗（$ahead 個 commit）")
    fi
  fi
done

# --- B2. DREAMS.md（03:00 Memory Dreaming 產出）→ commit + push，唔係刪 ---
if [ -f "$WS/DREAMS.md" ] && ! git -C "$WS" diff --quiet -- DREAMS.md 2>/dev/null; then
  if git -C "$WS" add DREAMS.md && git -C "$WS" commit -q -m "docs: update DREAMS.md (memory dreaming)" >/dev/null 2>&1; then
    git -C "$WS" pull --rebase -q origin main >/dev/null 2>&1
    if git -C "$WS" push -q origin main >/dev/null 2>&1; then
      REPAIRED+=("DREAMS.md commit + push")
    else
      FAILED+=("DREAMS.md push 失敗")
    fi
  else
    FAILED+=("DREAMS.md commit 失敗")
  fi
fi

# --- B3. untracked 暫存檔（*_output.txt / *.tmp / cron_output.txt 等）→ rm ---
while IFS= read -r f; do
  [ -n "$f" ] || continue
  case "$(basename "$f")" in
    DREAMS.md) continue ;;
    *_output.txt|*.tmp|cron_output.txt|*.log.tmp)
      if rm -f "$WS/$f" 2>/dev/null; then REPAIRED+=("rm $f"); else FAILED+=("rm $f 失敗"); fi ;;
  esac
done < <(git -C "$WS" status --porcelain 2>/dev/null | awk '$1=="??"{print $2}')

echo "  已修復: ${#REPAIRED[@]} 項"
for x in "${REPAIRED[@]:-}"; do [ -n "$x" ] && echo "    OK $x"; done
echo "  修復失敗: ${#FAILED[@]} 項"
for x in "${FAILED[@]:-}"; do [ -n "$x" ] && echo "    ERR $x"; done

echo "=== [C] 判定 ==="
http=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 https://kofhk.com/ 2>/dev/null || echo 000)
disk=$(df -P / 2>/dev/null | awk 'NR==2{gsub("%","",$5); print $5}')
disk=${disk:-0}
memavail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo 2>/dev/null)
memtotal=$(awk '/MemTotal/{print int($2/1024)}' /proc/meminfo 2>/dev/null)
cronerrs=$(openclaw cron list --json 2>/dev/null | python3 -c 'import json,sys' 2>/dev/null)
cronerrs=$(openclaw cron list --json 2>/dev/null | python3 -c '
import json,sys
try:
    d=json.load(sys.stdin)
except Exception:
    print(-1); raise SystemExit
jobs=d if isinstance(d,list) else (d.get("jobs") or d.get("automations") or [])
print(sum((j.get("state",{}) or {}).get("consecutiveErrors") or 0 for j in jobs))
' 2>/dev/null)
cronerrs=${cronerrs:--1}
tok="$WS/.token-store/dropbox-token.txt"
tokage=-1
if [ -f "$tok" ]; then
  tokage=$(( ( $(date +%s) - $(stat -c %Y "$tok" 2>/dev/null || echo 0) ) / 60 ))
fi
gitdirty=0; gitunpushed=0
for r in "$WS" /home/openclaw/Second-brain /home/openclaw/Max-backup; do
  gitdirty=$(( gitdirty + $(git -C "$r" status --porcelain 2>/dev/null | wc -l) ))
  gitunpushed=$(( gitunpushed + $(git -C "$r" rev-list --count @{u}..HEAD 2>/dev/null || echo 0) ))
done
dbsync=$(ls "$WS"/.dropbox-sync/volume*_state.json 2>/dev/null | wc -l)

web=OK; [ "$http" = "200" ] || web=WARN
dba=OK; if [ "$dbsync" -lt 1 ] || [ "$tokage" -lt 0 ] || [ "$tokage" -gt 240 ]; then dba=WARN; fi
sys=OK; if [ "$disk" -ge 90 ] 2>/dev/null; then sys=WARN; fi
if [ "$memtotal" -gt 0 ] 2>/dev/null && [ "$memavail" -lt $(( memtotal / 10 )) ]; then sys=WARN; fi
crn=OK; if [ "$cronerrs" -gt 0 ] 2>/dev/null; then crn=WARN; fi
git=OK; if [ "$gitdirty" -gt 0 ] || [ "$gitunpushed" -gt 0 ]; then git=WARN; fi

STATUS=OK
if [ "$http" != "200" ] || [ "$cronerrs" -gt 0 ] 2>/dev/null; then STATUS=FAIL; fi
if [ "$web" = "WARN" ] || [ "$dba" = "WARN" ] || [ "$sys" = "WARN" ] || [ "$crn" = "WARN" ] || [ "$git" = "WARN" ]; then
  [ "$STATUS" = "OK" ] && STATUS=WARN
fi
[ "${#FAILED[@]}" -gt 0 ] && STATUS=FAIL

echo "  網站 HTTP=$http | disk=${disk}% | mem_avail=${memavail}M/${memtotal}M | cron_errs=$cronerrs | token_age=${tokage}min | git髒檔=$gitdirty 未推送=$gitunpushed | dropbox_states=$dbsync"
echo "  受影響 job（consecutiveErrors > 0）:"
openclaw cron list --json 2>/dev/null | python3 -c '
import json,sys
d=json.load(sys.stdin)
jobs=d if isinstance(d,list) else (d.get("jobs") or d.get("automations") or [])
bad=[(j.get("name"),(j.get("state",{}) or {}).get("consecutiveErrors") or 0) for j in jobs if ((j.get("state",{}) or {}).get("consecutiveErrors") or 0)>0]
print("    "+(", ".join(n+"("+str(e)+")" for n,e in bad) if bad else "無"))
' 2>/dev/null
echo "  [LOOP_STATUS: $STATUS]"
echo "  [LOOP_DAILY: 網站$web, Dropbox$dba, 系統$sys, Cron$crn, Git$git]"
echo "=== 完 ==="