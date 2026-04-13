import subprocess
import os

os.environ["SEEDREAM_API_KEY"] = "sk-REDACTED"

prompts = [
    ("chapter-60-scene1", "Young Asian male, 20 years old, black short hair, sitting in a dark abandoned building rooftop machine room, glowing blue quantum crystal shaped like a heart pulsing on chest, blue data streams on forehead, wearing dark blue tech-combat suit, surrounded by ethereal blue spirit energy, multiple holographic UI panels floating in air showing cultivation progress data, moody cinematic lighting, sci-fi fantasy cultivation setting"),
    ("chapter-60-scene2", "Dramatic scene of young Asian male with black short hair and blue glowing circuit patterns on forehead, dodging through a dark underground parking garage filled with rusty abandoned cars, seven black-robed figures surrounding from all directions, ceiling collapsing with dust and debris, blue spirit energy trail behind the young fighter, intense cinematic action shot, sci-fi fantasy"),
    ("chapter-60-scene3", "Epic battle scene in an abandoned factory, young Asian male warrior with black short hair holding glowing blue spirit energy sword made of data particles, fighting against a handsome young man in black robe with cold cruel smile, blue energy blade clashing with black spirit fist, sparks and shockwaves shattering nearby rusty machines, dramatic lighting with blue and black contrast, sci-fi fantasy cultivation style"),
    ("chapter-60-scene4", "Dramatic moment in abandoned factory, young Asian male warrior with glowing blue quantum crystal on chest, releasing a powerful sphere of blue spirit energy from his palm like a shockwave attack, blue light explosion illuminating the dark factory, a black-robed young man being blasted away crashing into the wall, both characters mid-action, epic combat moment, cinematic lighting, sci-fi fantasy cultivation"),
    ("chapter-60-scene5", "Dramatic scene in dark abandoned factory, an elderly white-haired sage figure with golden eyes and ethereal aura, standing calmly with overwhelming presence, the young black-haired warrior lying injured on the ground looking up in awe, a black-robed enemy figure fleeing in fear in the background, the elder's gaze piercing with ancient wisdom, golden light particles surrounding the elder, cinematic dramatic lighting, powerful atmospheric composition, sci-fi fantasy cultivation"),
]

for name, prompt in prompts:
    print(f"Generating {name}...")
    result = subprocess.run([
        "python3",
        "/home/openclaw/.openclaw/skills/seedream-image-gen/scripts/generate_image.py",
        "--prompt", prompt,
        "--model", "gemini-3-pro-image-preview",
        "--size", "1024x576",
        "--n", "1",
        "--output-dir", "/home/openclaw/media/tool-image-generation/"
    ], env=os.environ)
    print(f"  Result: {result.returncode}")
