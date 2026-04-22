#!/usr/bin/env python3
"""Fix finance.html script issues - line-based processing."""

lines = open('finance.html', 'r', encoding='utf-8').readlines()

result = []
i = 0
skip_mode = False
skip_count = 0

while i < len(lines):
    line = lines[i]
    
    # Detect orphaned code after </script> that needs a <script> tag before it
    if '</script>' in line and i + 1 < len(lines) and '// 載入財經新聞' in lines[i+1]:
        # Add </script> and a new <script> tag
        result.append(line)  # Keep </script>
        result.append('    <script>\n')  # Add opening script tag
        i += 1
        # Skip the orphaned comment line, the next line is the function start
        # But we need to continue and NOT skip the function
        continue
    
    if '</script>' in line and i + 1 < len(lines) and '// 圖片懶加載實現' in lines[i+1]:
        result.append(line)
        result.append('    <script>\n')
        i += 1
        continue
    
    if '</script>' in line and i + 1 < len(lines) and '// 註冊Service Worker' in lines[i+1]:
        result.append(line)
        result.append('    <script>\n')
        i += 1
        continue
    
    # Skip the duplicate loadFinanceNews function
    # It starts with "        // 載入財經新聞" after the orphaned script tag
    if '        // 載入財經新聞' in line and not skip_mode:
        # Check if we're in the main script or orphaned section
        # The original function ends at line ~1697
        # Lines after ~1743 are orphaned
        # We need to identify which occurrence this is
        # Look ahead - if this is followed by "        async function loadFinanceNews() {"
        if i + 1 < len(lines) and 'async function loadFinanceNews()' in lines[i+1]:
            # This is the start of a function
            # Count how many times we've seen loadFinanceNews already
            prev_count = sum(1 for l in result if 'async function loadFinanceNews()' in l)
            if prev_count >= 1:
                # This is a duplicate, skip until we hit <!-- 投資工具部分
                skip_mode = True
                skip_count = 0
                i += 1
                continue
    
    if skip_mode:
        if '    <!-- 投資工具部分 -->' in line:
            result.append(line)
            skip_mode = False
        i += 1
        continue
    
    # Fix end of file: orphaned PWA code before <script src="assets/main.js"
    if '    \n' in line and i + 1 < len(lines) and '<script src="assets/main.js"' in lines[i+1]:
        result.append(line)
        result.append('    </script>\n')
        i += 1
        continue
    
    result.append(line)
    i += 1

open('finance.html', 'w', encoding='utf-8').writelines(result)
print('Done! Fixed finance.html')
