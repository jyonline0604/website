#!/usr/bin/env python3
import subprocess
import sys
import os

os.environ["SEEDREAM_API_KEY"] = "sk-REDACTED"
os.environ["PYTHONPATH"] = "/home/openclaw/.openclaw/skills/seedream-image-gen/scripts"

script = "/home/openclaw/.openclaw/skills/seedream-image-gen/scripts/generate_image.py"

prompts = [
    # Scene 1: Opening - warship bridge, battlefield view
    "Young Asian male warrior on bridge of futuristic sci-fi cultivation warship, looking at vast space battlefield through large window, floating alien bug carcasses with dim blue spiritual light debris scattered across void like strange star belts, black short hair with glowing blue circuit patterns on forehead, blue glowing heart-shaped quantum crystal on chest, dark blue combat suit, concerned focused expression, one hand touching spirit pattern control panel, cinematic lighting, sci-fi fantasy cultivation style",
    
    # Scene 2: Cultivation room - analyzing bug corpse
    "Young Asian male warrior in high-tech cultivation room with soft blue spiritual light, floating alien bug corpse suspended in center with shell covered in flowing blue spirit energy patterns, his hands forming cultivation seals with blue spiritual energy tendrils flowing into specimen, intense concentration expression, blue holographic displays showing molecular structure analysis floating around, spirit rune arrays on walls, sci-fi fantasy interior, dramatic lighting",
    
    # Scene 3: Analysis - neural network discovery
    "Sci-fi fantasy command bridge interior with multiple floating holographic displays, young Asian male warrior (black short hair, blue glowing quantum crystal on chest, dark blue combat suit) pointing at large holographic projection showing complex neural network structure of alien bug collective consciousness, frequency curves and data charts floating in air, officer in Chinese style military uniform standing nearby, blue and purple lighting, futuristic Chinese sci-fi aesthetic, dramatic scene of discovery and revelation",
    
    # Scene 4: Alarm - bug corpse awakening
    "High-tech cultivation laboratory with emergency red alarm lights flashing, young Asian male warrior (blue glowing crystal on chest, dark blue combat suit) in defensive posture with hands forming seals, multiple layered defensive spirit formation barriers activating in concentric blue light circles around him, alien bug corpse in center with blue spiritual energy flowing through shell cracks and patterns starting to glow and rotate, ominous energy swirling, serious alert expression, dramatic red and blue lighting contrast, sense of impending danger",
    
    # Scene 5: Cliffhanger - awakened threat
    "Young Asian male warrior standing defiantly in high-tech cultivation room filled with activated defensive formations (blue translucent barriers layered around him), fierce determined expression with one hand raised summoning spiritual power, terrifying alien bug corpse fully awakened before him - shell gaps glowing intensely with blue spirit light, ominous swirling energy around creature, blue energy surrounding his body, dark shadows contrasting with glowing spirit energy, cliffhanger moment, dramatic lighting, sci-fi fantasy cultivation style"
]

output_dir = "/home/openclaw/media/tool-image-generation"

for i, prompt in enumerate(prompts, 1):
    print(f"\n=== Generating Scene {i} ===")
    result = subprocess.run(
        ["python3", script,
         "--prompt", prompt,
         "--model", "gemini-3-pro-image-preview",
         "--size", "1024x1024",
         "--output-dir", output_dir],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
