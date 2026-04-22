#!/usr/bin/env python3
"""Fix finance.html script issues properly."""

with open('finance.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Issue 1: Fix orphaned script code after </script> tags
# The pattern is: </script> followed by orphaned code without <script> opening tag

fixes = [
    ('</script>        // 載入財經新聞', '</script>\n    <script>\n        // 載入財經新聞'),
    ('</script>        // 圖片懶加載實現', '</script>\n    <script>\n        // 圖片懶加載實現'),
    ('</script>        // 註冊Service Worker', '</script>\n    <script>\n        // 註冊Service Worker'),
]

for old, new in fixes:
    if old in content:
        content = content.replace(old, new)
        print(f'Fixed: {old[:50]}...')
    else:
        print(f'Not found: {old[:50]}...')

# Issue 2: The duplicated loadFinanceNews function needs to be removed
# The second one starts with "    <script>\n        // 載入財經新聞" after line 1743
# and ends before "    <!-- 投資工具部分 -->"

# Find and remove the duplicated function block (from line 1744 to before <!-- 投資工具部分 -->)
import re

# Pattern to match the duplicate script block
# It starts with the orphaned script we just fixed, and contains the second loadFinanceNews
# We need to find where the first loadFinanceNews function properly ends and remove the duplicate

# The first loadFinanceNews is at line 1661
# The duplicate starts after </script> at line 1743

# Find the second occurrence of "        async function loadFinanceNews() {"
second_func_pattern = r'(\}\s*\n    )\s*\n    <script>\s*\n        // 載入財經新聞\s*\n        async function loadFinanceNews\(\) \{.*?\n        }\s*\n    (\n    <!-- 投資工具部分 -->)'

match = re.search(second_func_pattern, content, re.DOTALL)
if match:
    print(f"Found duplicate at position {match.start()} to {match.end()}")
    # Keep the first part (ending with }) and the second part (<!-- 投資工具部分 -->)
    # Remove the duplicate script tag and function
    content = content[:match.start()] + match.group(1) + match.group(2) + content[match.end():]
    print("Removed duplicate loadFinanceNews function")
else:
    print("Duplicate pattern not found, trying alternate approach...")

# Issue 3: The end of the file has orphaned PWA code before <script src="assets/main.js"
# Fix: ensure proper script tag closure
old_pwa = '''});
            }
        });
    
    <script src="assets/main.js" defer></script>'''

new_pwa = '''});
            }
        });
    </script>

    <script src="assets/main.js" defer></script>'''

if old_pwa in content:
    content = content.replace(old_pwa, new_pwa)
    print("Fixed PWA code at end")
else:
    print("PWA end pattern not found")

with open('finance.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done!")
