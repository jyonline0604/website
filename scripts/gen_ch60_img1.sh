#!/bin/bash
export SEEDREAM_API_KEY="sk-REDACTED"
cd /home/openclaw/.openclaw/workspace

python3 /home/openclaw/.openclaw/skills/seedream-image-gen/scripts/generate_image.py \
  --prompt "Young Asian male, 20 years old, black short hair, sitting in a dark abandoned building rooftop machine room, glowing blue quantum crystal shaped like a heart pulsing on chest, blue data streams on forehead, wearing dark blue tech-combat suit, surrounded by ethereal blue spirit energy, multiple holographic UI panels floating in air showing cultivation progress data, moody cinematic lighting, sci-fi fantasy cultivation setting" \
  --model "gemini-3-pro-image-preview" \
  --size "1024x576" \
  --n 1 \
  --output-dir /home/openclaw/media/tool-image-generation/
