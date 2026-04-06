#!/bin/bash
# Dream Memory System - Cron Wrapper
# 每天凌晨3點自動運行

export PATH="/home/openclaw/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

cd /home/openclaw/.openclaw/workspace
python3 scripts/dream-memory.py >> logs/dream-cron.log 2>&1
