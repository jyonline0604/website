#!/bin/bash
# AI新聞更新腳本
export PATH="/home/openclaw/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
cd /home/openclaw/.openclaw/workspace
python3 /home/openclaw/.openclaw/workspace/scripts/fetch_ai_news.py >> /home/openclaw/.openclaw/workspace/logs/ai-news.log 2>&1
