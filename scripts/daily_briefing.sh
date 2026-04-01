#!/bin/bash
# 每日简报生成脚本（08:15, 12:55, 17:55 执行）
# 负责整合天气、交通、新闻等生成 HK 简报
# 生成后自动推送到 GitHub

set -e

cd /home/openclaw/.openclaw/workspace

# 调用 Python 脚本生成简报
python3 scripts/daily_briefing.py

# 自动推送到 GitHub
cd /home/openclaw/.openclaw/workspace

# Add and commit the briefing files
git add daily-briefing.html briefing.txt
git commit -m "docs: update daily briefing $(date '+%Y-%m-%d %H:%M')" || exit 0

# Push to GitHub
git push origin main

echo "✅ Daily briefing pushed to GitHub"
