#!/usr/bin/env bash
# sync_heartbeat_scratch.sh — 把 docs/heartbeat-checklist.md 同步入 heartbeat job 嘅 cron scratch
# 用法: bash scripts/sync_heartbeat_scratch.sh
set -uo pipefail
W="/home/openclaw/.openclaw/workspace"
SRC="$W/docs/heartbeat-checklist.md"
JOB="9dc7d6c3-617f-410d-9881-e87453c33037"

[ -f "$SRC" ] || { echo "❌ 搵唔到 $SRC"; exit 1; }
cd "$W" || exit 1

echo "→ 寫入 cron scratch (job $JOB)"
openclaw cron scratch "$JOB" --file "$SRC" >/dev/null 2>&1 || {
  echo "❌ openclaw cron scratch 寫入失敗"; exit 1; }

echo "→ 驗證"
TMP=$(mktemp)
openclaw cron scratch "$JOB" > "$TMP" 2>&1
if cmp -s "$SRC" "$TMP"; then
  echo "✅ scratch 內容同 $SRC 一致 ($(wc -c < "$TMP") bytes)"
  rm -f "$TMP"; exit 0
fi
echo "⚠️ scratch 同 $SRC 有差異："
diff "$SRC" "$TMP" | head -20
rm -f "$TMP"
exit 1
