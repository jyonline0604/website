#!/bin/bash
# ==========================================================
# Git Pre-Commit Security Hook
# 每次 git commit 前自動檢查敏感資料
# ==========================================================

RED='\033[0;31m'; YELLOW='\033[1;33m'; GREEN='\033[0;32m'; NC='\033[0m'
LEAKS_FOUND=0

echo -e "${YELLOW}🔒 Security Pre-Commit 檢查中...${NC}"

# 檢查 1：敏感路徑
for p in ".token-store/" ".backup-pass" "openclaw.json" ".env" "notify-config.json"; do
  STAGED=$(git diff --cached --name-only -- "$p" 2>/dev/null || true)
  [ -n "$STAGED" ] && echo -e "${RED}  ❌ 敏感檔案被 stage: $STAGED${NC}" && LEAKS_FOUND=$((LEAKS_FOUND+1))
done

# 檢查 2：staged 文本檔案內容
STAGED_FILES=$(git diff --cached --name-only 2>/dev/null || true)
for FILE in $STAGED_FILES; do
  case "$FILE" in *.gitignore|scripts/git-security-hook.sh|scripts/scan-git-history.sh) continue;; esac
  case "$FILE" in *.py|*.sh|*.md|*.html|*.js|*.txt|*.json|*.yaml|*.yml|*.cfg|*.conf|*.ini) ;; *) continue;; esac
  CONTENT=$(git show ":$FILE" 2>/dev/null || true)
  
  echo "$CONTENT" | grep -q 'sk-[a-zA-Z0-9]\{16\}' && echo -e "${RED}  ❌ $FILE: 發現疑似 API Key (sk-...)${NC}" && LEAKS_FOUND=$((LEAKS_FOUND+1))
  echo "$CONTENT" | grep -q 'ghp_[a-zA-Z0-9]\{20\}' && echo -e "${RED}  ❌ $FILE: 發現疑似 GitHub PAT${NC}" && LEAKS_FOUND=$((LEAKS_FOUND+1))
  echo "$CONTENT" | grep -q 'sl\.[a-zA-Z0-9._-]\{50\}' && echo -e "${RED}  ❌ $FILE: 發現疑似 Dropbox Token${NC}" && LEAKS_FOUND=$((LEAKS_FOUND+1))
  echo "$CONTENT" | grep -q 'AKIA[0-9A-Z]\{16\}' && echo -e "${RED}  ❌ $FILE: 發現疑似 AWS Key${NC}" && LEAKS_FOUND=$((LEAKS_FOUND+1))
  echo "$CONTENT" | grep -q 'BEGIN.*PRIVATE KEY' && echo -e "${RED}  ❌ $FILE: 發現 Private Key${NC}" && LEAKS_FOUND=$((LEAKS_FOUND+1))
done

if [ "$LEAKS_FOUND" -gt 0 ]; then
  echo -e "${RED}╔══════════════════════════╗${NC}"
  echo -e "${RED}║  SECURITY COMMIT BLOCKED ║${NC}"
  echo -e "${RED}║  $LEAKS_FOUND 個問題         ║${NC}"
  echo -e "${RED}╚══════════════════════════╝${NC}"
  echo "  可用: git reset HEAD <file>"
  exit 1
fi

echo -e "${GREEN}  ✅ 安全檢查通過${NC}"
exit 0
