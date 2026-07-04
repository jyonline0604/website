#!/bin/bash
# ==========================================================
# Git History 敏感資料掃描器
# 掃描成個 Git history 有冇 API Keys / Tokens 外洩
# ==========================================================

RED='\033[0;31m'; YELLOW='\033[1;33m'; GREEN='\033[0;32m'; BLUE='\033[0;34m'; NC='\033[0m'
VERBOSE=false; [ "$1" = "--verbose" ] && VERBOSE=true

cd /home/openclaw/.openclaw/workspace
echo -e "${BLUE}🔍 Git History 敏感資料掃描...${NC}\n"

SCANS=0; LEAKS=0

check_pattern() {
  local label="$1"; local pattern="$2"; local limit="${3:-5}"
  RESULTS=$(git log --all -p --pickaxe-all -S "$pattern" --pretty="format:%h %s" 2>/dev/null | grep -B1 "$pattern" | head -$((limit*3)) || true)
  if [ -n "$RESULTS" ] && echo "$RESULTS" | grep -q "$pattern"; then
    echo -e "${RED}  ❌ $label — 喺 git history 中發現${NC}"
    echo "$RESULTS" | head -$((limit*2)); echo ""; LEAKS=$((LEAKS+1))
  elif $VERBOSE; then echo -e "${GREEN}  ✅ $label — 安全${NC}"; fi
  SCANS=$((SCANS+1))
}

check_file_in_history() {
  local label="$1"; local filepath="$2"
  RESULTS=$(git log --all --oneline -- "$filepath" 2>/dev/null | head -5)
  if [ -n "$RESULTS" ]; then
    echo -e "${RED}  ❌ $label ($filepath) — 曾經被 git 追蹤過${NC}"; echo "$RESULTS"; echo ""
    LEAKS=$((LEAKS+1))
  elif $VERBOSE; then echo -e "${GREEN}  ✅ $label ($filepath) — 從未被 git 追蹤${NC}"; fi
  SCANS=$((SCANS+1))
}

echo -e "${YELLOW}━━━ 檔案追蹤檢查 ━━━${NC}"
check_file_in_history "Token Store" ".token-store/"
check_file_in_history "Backup Password" ".backup-pass"

echo -e "${YELLOW}━━━ API Key 模式檢查 ━━━${NC}"
check_pattern "OpenAI API Key (sk-...)" "sk-[a-zA-Z0-9]" 3
check_pattern "GitHub PAT (ghp_...)" "ghp_" 3
check_pattern "Dropbox Token (sl.)" "sl\.[a-zA-Z0-9._-]\{50,\}" 3

echo -e "${YELLOW}━━━ Config 檢查 ━━━${NC}"
check_pattern "API_KEY=xxx" "API_KEY=" 3
check_pattern "SECRET_KEY=xxx" "SECRET_KEY=" 3
check_pattern "REFRESH_TOKEN" "REFRESH_TOKEN" 3

echo -e "\n${BLUE}========================================${NC}"
if [ "$LEAKS" -gt 0 ]; then
  echo -e "${RED}⚠️  發現 $LEAKS 個問題！建議 revoke 外洩 tokens + BFG cleanup${NC}"
else
  echo -e "${GREEN}✅ 安全！0 個問題${NC}"
fi
echo -e "${BLUE}========================================${NC}"
exit $LEAKS
