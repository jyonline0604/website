#!/bin/bash
export SEEDREAM_API_KEY="${SEEDREAM_API_KEY:-YOUR_KEY_HERE}"
python3 /home/openclaw/.openclaw/skills/seedream-image-gen/scripts/generate_image.py "$@"
