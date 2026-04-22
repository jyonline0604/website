import re

# Read the file
with open('av-novels.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Check if chapter-1-av already exists
if 'chapter-1-av.html' in content:
    print("Chapter 1 already exists in av-novels.html")
else:
    # Find the pattern for chapter 2 card closing and insert chapter 1 before the final closing tags
    # Look for the structure that closes before </body>

    # Find the position just before the final closing </div></div></div></div></body></html>
    # We need to insert the chapter 1 card at the right position

    # Find chapter 2's closing - it ends with:
    # </div></div></div>  (chapter-card-content, chapter-card, grid-container?) 
    # then more closing divs and </body>

    # Let's find the closing sequence
    search_pattern = r'(<div class="chapter-number">第 2 章</div>.*?chapter-2-av\.html.*?</div>\s*</div>\s*)(</body>)'

    match = re.search(search_pattern, content, re.DOTALL)
    if match:
        # Insert chapter 1 card before </body>
        ch1_card = '''<div class="chapter-card">
                <div class="chapter-card-image">
                    <img src="assets/chapter-1-scene1.webp" alt="第1章" loading="lazy">
                </div>
                <div class="chapter-card-content">
                    <div class="chapter-number">第 1 章</div>
                    <h3 class="chapter-title">靈芯覺醒</h3>
                    <p class="chapter-desc">林塵在互聯網黑暗中甦醒，發現自己穿越到一個科技與修真共存的世界。還沒來得及理解環境，神秘聲音在腦中響起：「靈芯系統綁定成功」。他要在一小時內讓全網知道他的存在，否則系統將被收回。（本章完）</p>
                    <div class="chapter-actions">
                        <a href="chapter-1-av.html" class="btn btn-primary">🎬 有聲畫</a>
                        <a href="chapter-1.html" class="btn btn-secondary">文字版</a>
                    </div>
                </div>
            </div>
'''
        new_content = content[:match.start()] + match.group(1) + ch1_card + match.group(2) + content[match.end():]

        # Actually let's be more careful - find the last </div></body> sequence
        pass

    # Simpler approach: find the last chapter card and add after it
    # The last card is chapter 2, we need to add chapter 1 after it
    last_card_end = content.rfind('</div>\n            </div>\n</div>\n            </div>\n        </div>\n    </div>\n</div>')

    if last_card_end == -1:
        # Try different pattern
        last_card_end = content.rfind('chapter-2-av.html')

    print(f"Found chapter 2 at position: {content.rfind('chapter-2-av.html')}")

    # Find the end of chapter 2 card
    # It ends with the chapter-actions div, then closing divs
    ch2_end = content.find('</div>\n            </div>\n</div>', content.find('chapter-2-av.html'))
    print(f"Chapter 2 card ends around: {ch2_end}")

    # Actually let's just insert before </body>
    body_end = content.rfind('</body>')
    print(f"Body ends at: {body_end}")

    # The content before </body> has closing divs, insert the chapter 1 card there
    ch1_card = '''<div class="chapter-card">
                <div class="chapter-card-image">
                    <img src="assets/chapter-1-scene1.webp" alt="第1章" loading="lazy">
                </div>
                <div class="chapter-card-content">
                    <div class="chapter-number">第 1 章</div>
                    <h3 class="chapter-title">靈芯覺醒</h3>
                    <p class="chapter-desc">林塵在互聯網黑暗中甦醒，發現自己穿越到一個科技與修真共存的世界。還沒來得及理解環境，神秘聲音在腦中響起：「靈芯系統綁定成功」。他要在一小時內讓全網知道他的存在，否則系統將被收回。（本章完）</p>
                    <div class="chapter-actions">
                        <a href="chapter-1-av.html" class="btn btn-primary">🎬 有聲畫</a>
                        <a href="chapter-1.html" class="btn btn-secondary">文字版</a>
                    </div>
                </div>
            </div>
'''

    # Find where to insert - before the last closing divs that precede </body>
    insert_pos = content.rfind('</div>\n            </div>\n        </div>\n    </div>\n</div>')
    print(f"Insert position: {insert_pos}")

    if insert_pos > 0:
        new_content = content[:insert_pos] + ch1_card + content[insert_pos:]
        with open('av-novels.html', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Added chapter 1 to av-novels.html")
    else:
        print("Could not find insertion point")