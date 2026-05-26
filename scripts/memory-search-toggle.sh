#!/bin/bash
# memory-search-toggle.sh - 開關本地記憶搜索
# 用法: ./memory-search-toggle.sh on|off|status

ACTION="${1:-status}"
CONFIG="$HOME/.openclaw/openclaw.json"

case "$ACTION" in
  on)
    echo "📖 開啟本地記憶搜索..."
    openclaw config patch --stdin 2>/dev/null << 'EOF'
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "provider": "ollama",
        "model": "nomic-embed-text:v1.5"
      }
    }
  }
}
EOF
    openclaw gateway restart 2>&1 &
    echo "✅ 記憶搜索已開啟（Gateway 重啟中...）"
    echo "⚠️ 注意：CPU 使用率會上升，用完請關閉"
    ;;
  off)
    echo "🔒 關閉記憶搜索..."
    openclaw config patch --stdin 2>/dev/null << 'EOF'
{
  "agents": {
    "defaults": {
      "memorySearch": null
    }
  }
}
EOF
    openclaw gateway restart 2>&1 &
    echo "✅ 記憶搜索已關閉，CPU 恢復正常"
    ;;
  status)
    if openclaw config get agents.defaults.memorySearch 2>&1 | grep -q "provider"; then
      echo "📖 記憶搜索：🟢 開啟中"
    else
      echo "📖 記憶搜索：🔴 已關閉"
    fi
    ;;
  *)
    echo "用法: $0 {on|off|status}"
    exit 1
    ;;
esac
