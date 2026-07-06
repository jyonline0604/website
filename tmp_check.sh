#!/bin/bash
echo "=== home.html background ==="
grep -n "hero\|background-image\|bg\|landing" /home/openclaw/.openclaw/workspace/home.html 2>/dev/null | head -20
echo "=== assets/images/ ==="
ls -la /home/openclaw/.openclaw/workspace/assets/images/ 2>/dev/null | head -20
echo "=== inbound image ==="
find /home/openclaw/ -path "*/inbound/*e2b12b68*" 2>/dev/null | head -5
find /home/openclaw/ -name "*.jpg" -path "*e2b12b68*" 2>/dev/null | head -5
