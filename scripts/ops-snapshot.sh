#!/usr/bin/env bash
# ops-snapshot.sh — 一次過攞齊系統現況（唯讀，唔改任何嘢）
# 用法: bash scripts/ops-snapshot.sh
set -uo pipefail
W="/home/openclaw/.openclaw/workspace"
cd "$W" || exit 1

echo "=== 1. Gateway / 版本 ==="
openclaw --version 2>&1 | head -2
systemctl --user is-active openclaw-gateway.service 2>/dev/null | sed 's/^/gateway service: /'

echo "=== 2. Cron jobs（名／錯誤／下一步）==="
timeout 30 openclaw cron list --json 2>/dev/null | python3 -c "
import sys, json
from collections import Counter
d = json.load(sys.stdin)
jobs = d.get('jobs') or d.get('automations') or []
c = Counter((j.get('name') or '') for j in jobs)
dup = {n: k for n, k in c.items() if k > 1}
errs = sum((j.get('state', {}).get('consecutiveErrors') or 0) for j in jobs)
for j in jobs:
    st = j.get('state', {})
    print('  %-8s %-28s last=%s errs=%s fb=%d' % (
        (j.get('id') or '')[:8], (j.get('name') or '')[:28],
        (st.get('lastRunAt') or '-'), st.get('consecutiveErrors') or 0,
        len((j.get('payload') or {}).get('fallbacks') or [])))
print('  總數 %d | errs 合計 %d | 重複名 %s' % (len(jobs), errs, dup or '無'))
" 2>&1 | head -20

echo "=== 3. 網站 HTTP ==="
printf '  kofhk.com: %s
' "$(curl -s -o /dev/null -w '%{http_code}' --max-time 12 https://kofhk.com/ 2>&1)"

echo "=== 4. Git（workspace）==="
echo "  未推送 $(git rev-list --count origin/main..HEAD 2>/dev/null) | 髒檔 $(git status --porcelain 2>/dev/null | wc -l) | HEAD $(git rev-parse --short HEAD 2>/dev/null)"
if [ "$(git status --porcelain 2>/dev/null | wc -l)" != "0" ]; then
  git status --porcelain 2>/dev/null | head -5 | sed 's/^/    /'
fi

echo "=== 5. 記憶檔 ==="
echo "  MEMORY.md $(wc -l < "$W/MEMORY.md" 2>/dev/null) 行 | memory/ $(ls -1 "$W/memory" 2>/dev/null | wc -l) 檔"

echo "=== 6. 敏感資料（追蹤中）==="
git ls-files 2>/dev/null | grep -Ei '(^|/)(\.env|.*token.*|.*secret.*|.*credential.*)$' | head -5 | sed 's/^/  ⚠ /'
echo "  （以上為空即正常）"

echo "=== 7. Dropbox token 新鮮度 ==="
TOK="$W/.token-store/dropbox-token.txt"
if [ -f "$TOK" ]; then
  echo "  token 存在 $(wc -c < "$TOK") bytes | 最後續期 $(stat -c %y "$TOK" 2>/dev/null | cut -d. -f1)"
else
  echo "  token 檔缺失: $TOK"
fi

echo "=== 8. 系統 cron（非註釋行數）==="
echo "  $(crontab -l 2>/dev/null | grep -v '^[[:space:]]*#' | grep -c .) 行"

echo "=== 完 ==="
