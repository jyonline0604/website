#!/bin/bash
# 每日記憶日誌腳本
export PATH="/home/openclaw/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
cd /home/openclaw/.openclaw/workspace
python3 /home/openclaw/.openclaw/workspace/scripts/auto-memory-logger.py >> /home/openclaw/.openclaw/workspace/logs/memory-auto.log 2>&1
