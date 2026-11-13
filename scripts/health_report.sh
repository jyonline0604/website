#!/usr/bin/env bash
# health_report.sh — 每日健康報告（22:00 job）嘅單一入口
#
# 設計目標（2026-11-12）：cron job 只需要做 **一次** exec（行呢個 script），
# 唔使喺 code mode 入面逐項手寫指令。
# 原因：實測 22:00 job 喺 code mode 內誤寫 tools.exec(...) → ReferenceError 3 次，
#       每次都要重試，加上 minimax 429，令成個 run 由正常 5 分鐘拖到 21 分鐘。
#       減少 code mode 呼叫次數 = 減少 ReferenceError 同 429 嘅暴露面。
#
# 2026-11-13 新增 --deliver 模式（結構性收口，唔經模型轉述）：
#   stdout 只輸出「最終報告」，所有數字由本腳本自己實測；詳細快照寫入 logs/health_report-YYYY-MM-DD.log。
#   背景：22:00 job 交俾模型「整理成健康報告」時，弱模型會捏造數字 —— 2026-11-13 22:00 交咗
#   「MEMORY.md 1234 行／章節 56／cron 錯誤 0 個」而實際係 513 行／1878 章／errs 2，
#   連 [LOOP_STATUS: FAIL] 都改成 OK → 假綠。健康報告本身唔需要推理，唔應該經模型。
#
# 用法: bash scripts/health_report.sh [--deliver]
set -uo pipefail
WS=/home/openclaw/.openclaw/workspace
cd "$WS" || exit 1

DELIVER=0
[ "${1:-}" = "--deliver" ] && DELIVER=1
mkdir -p "$WS/logs"
LOGFILE="$WS/logs/health_report-$(date +%F).log"

# verbose：--deliver 模式寫去 log 檔，一般模式直接 stdout
verbose() {
  if [ "$DELIVER" = 1 ]; then printf '%s\n' "$@" >> "$LOGFILE"; else printf '%s\n' "$@"; fi
}

SNAP=""
if [ "$DELIVER" = 1 ]; then
  SNAP=$(mktemp)
  bash "$WS/scripts/ops-snapshot.sh" "$WS" > "$SNAP" 2>&1
  { echo "=== [A] 現況快照（唯讀） $(date '+%F %T') ==="; cat "$SNAP"; } >> "$LOGFILE"
else
  echo "=== [A] 現況快照（唯讀）==="
  bash "$WS/scripts/ops-snapshot.sh" "$WS"
fi

verbose "=== [B] 自動修復 ==="
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

verbose "  已修復: ${#REPAIRED[@]} 項"
for x in "${REPAIRED[@]:-}"; do [ -n "$x" ] && verbose "    OK $x"; done
verbose "  修復失敗: ${#FAILED[@]} 項"
for x in "${FAILED[@]:-}"; do [ -n "$x" ] && verbose "    ERR $x"; done

http=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 https://kofhk.com/ 2>/dev/null || echo 000)
disk=$(df -P / 2>/dev/null | awk 'NR==2{gsub("%","",$5); print $5}')
disk=${disk:-0}
memavail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo 2>/dev/null)
memtotal=$(awk '/MemTotal/{print int($2/1024)}' /proc/meminfo 2>/dev/null)
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

verbose "  網站 HTTP=$http | disk=${disk}% | mem_avail=${memavail}M/${memtotal}M | cron_errs=$cronerrs | token_age=${tokage}min | git髒檔=$gitdirty 未推送=$gitunpushed | dropbox_states=$dbsync"
verbose "  受影響 job（consecutiveErrors > 0）:"
openclaw cron list --json 2>/dev/null | python3 -c '
import json,sys
d=json.load(sys.stdin)
jobs=d if isinstance(d,list) else (d.get("jobs") or d.get("automations") or [])
bad=[(j.get("name"),(j.get("state",{}) or {}).get("consecutiveErrors") or 0) for j in jobs if ((j.get("state",{}) or {}).get("consecutiveErrors") or 0)>0]
print("    "+(", ".join(n+"("+str(e)+")" for n,e in bad) if bad else "無"))
' >> "$LOGFILE" 2>/dev/null
verbose "  [LOOP_STATUS: $STATUS]"
verbose "  [LOOP_DAILY: 網站$web, Dropbox$dba, 系統$sys, Cron$crn, Git$git]"
verbose "=== 完 ==="

# ---------- --deliver：最終報告（數字全部本腳本實測，唔經模型）----------
if [ "$DELIVER" = 1 ]; then
  export WS HTTP="$http" DISK="$disk" MEMAVAIL="$memavail" MEMTOTAL="$memtotal"
  export CRONERRS="$cronerrs" TOKAGE="$tokage" GITDIRTY="$gitdirty" GITUNPUSHED="$gitunpushed"
  export DBSYNC="$dbsync" STATUS="$STATUS" WEB="$web" DBA="$dba" SYS="$sys" CRN="$crn" GIT="$git"
  export REPAIRED_JOINED="$(printf '%s
' "${REPAIRED[@]:-}" | grep -v '^$' | paste -sd ';' -)"
  export FAILED_JOINED="$(printf '%s
' "${FAILED[@]:-}" | grep -v '^$' | paste -sd ';' -)"
  python3 - <<'PYEOF'
import json, os, subprocess, urllib.request, time

WS = os.environ["WS"]
mark = lambda ok: "✅" if ok else "⚠️"

def sh(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception:
        return ""

def jload(cmd):
    try:
        return json.loads(subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30).stdout)
    except Exception:
        return None

jobs = jload("openclaw cron list --json") or []
if isinstance(jobs, dict):
    jobs = jobs.get("jobs") or jobs.get("automations") or []
total_jobs = len(jobs)
errs = int(os.environ.get("CRONERRS") or 0)
bad = [(j.get("name"), (j.get("state") or {}).get("consecutiveErrors") or 0)
       for j in jobs if ((j.get("state") or {}).get("consecutiveErrors") or 0) > 0]

mem_lines = sh("wc -l < %s/MEMORY.md" % WS) or "?"
import glob as _glob, re as _re
ch_local = len([p for p in _glob.glob(os.path.join(WS, "chapter-*.html"))
               if _re.fullmatch(r"chapter-\d+\.html", os.path.basename(p))]) or "?"
ch_files = sh("ls %s/chapter-*.html 2>/dev/null | wc -l" % WS) or "?"
try:
    ch_index = len(json.load(open(os.path.join(WS, "assets/chapters-data.json"))))
except Exception:
    ch_index = "?"
ch_online = "?"
try:
    url = "https://kofhk.com/assets/chapters-data.json?v=%d" % int(time.time())
    _req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(_req, timeout=25) as resp:
        ch_online = len(json.loads(resp.read().decode("utf-8", "replace")))
except Exception:
    pass

sk = {}
for name in ("novel-site-standards", "novel-av-generator"):
    paths = [
        os.path.expanduser("~/.openclaw/skills/%s/SKILL.md" % name),
        os.path.join(WS, ".openclaw/skills/%s/SKILL.md" % name),
        "/home/openclaw/Second-brain/skills/%s/SKILL.md" % name,
        "/home/openclaw/Max-backup/skills/%s/SKILL.md" % name,
    ]
    import hashlib
    hs = set()
    present = 0
    for p in paths:
        try:
            hs.add(hashlib.md5(open(p, "rb").read()).hexdigest())
            present += 1
        except Exception:
            pass
    sk[name] = (present, len(hs))

syscron = sh("crontab -l 2>/dev/null | grep -vE '^[[:space:]]*#' | grep -c .") or "?"
sens = sh("cd %s && git status --porcelain | grep -cE 'openclaw.json|\\.backup-pass|api_key|github_pat|sk-'" % WS) or "0"
tok_age = int(os.environ.get("TOKAGE") or -1)
tok_bytes = os.path.getsize(os.path.join(WS, ".token-store/dropbox-token.txt")) if os.path.exists(os.path.join(WS, ".token-store/dropbox-token.txt")) else 0
repaired = [x for x in (os.environ.get("REPAIRED_JOINED") or "").split(";") if x]
failed = [x for x in (os.environ.get("FAILED_JOINED") or "").split(";") if x]

print("📊 每日健康報告 (%s)" % time.strftime("%Y-%m-%d %H:%M"))
print()
print("🌐 網站 kofhk.com — HTTP %s %s" % (os.environ.get("HTTP"), mark(os.environ.get("HTTP") == "200")))
print("⏱ Cron job — %d 個，consecutiveErrors 合計 %d %s" % (total_jobs, errs, mark(errs == 0)))
if bad:
    for n, e in bad:
        print("   ⚠️ %s（consecutiveErrors=%d）" % (n, e))
else:
    print("   無連續錯誤 job")
print("📚 章節 — 線上 %s ／ 本地 %s（chapters-data.json %s；chapter-*.html 檔案 %s 個，含 template）%s"
      % (ch_online, ch_local, ch_index, ch_files,
         mark(str(ch_online) == str(ch_local) == str(ch_index))))
print("🧠 MEMORY.md — %s 行" % mem_lines)
print("🔐 敏感檔命中 — %s %s" % (sens, mark(str(sens) == "0")))
for name, (present, uniq) in sk.items():
    print("🗂 Skill 副本 — %s：%d/4 處，md5 唯一數 %d %s" % (name, present, uniq, mark(present == 4 and uniq == 1)))
print("💾 Dropbox — state %s 個；token %s bytes，%s分鐘前續期 %s"
      % (os.environ.get("DBSYNC"), tok_bytes, tok_age,
         mark(0 <= tok_age <= 240 and int(os.environ.get("DBSYNC") or 0) >= 1)))
print("🖥 系統 — disk %s%%、記憶體可用 %sM/%sM %s"
      % (os.environ.get("DISK"), os.environ.get("MEMAVAIL"), os.environ.get("MEMTOTAL"),
         mark(os.environ.get("SYS") == "OK")))
print("📦 system cron — %s 行" % syscron)
print("🔧 自動修復 — %d 項%s" % (len(repaired), ("：" + "、".join(repaired)) if repaired else ""))
if failed:
    print("   ❌ 修復失敗：%s" % "、".join(failed))
print("📤 三倉 git — 未推送 %s、髒檔 %s %s"
      % (os.environ.get("GITUNPUSHED"), os.environ.get("GITDIRTY"),
         mark(os.environ.get("GITUNPUSHED") == "0" and os.environ.get("GITDIRTY") == "0")))
print()
print("[LOOP_STATUS: %s]" % os.environ.get("STATUS"))
print("[LOOP_DAILY: 網站%s, Dropbox%s, 系統%s, Cron%s, Git%s]"
      % (os.environ.get("WEB"), os.environ.get("DBA"), os.environ.get("SYS"),
         os.environ.get("CRN"), os.environ.get("GIT")))
PYEOF
  [ -n "$SNAP" ] && rm -f "$SNAP"
fi
