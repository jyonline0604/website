#!/usr/bin/env python3
"""Update HTML img src references from .jpg/.png to .webp."""

import os
import re
from pathlib import Path

BASE = Path('/opt/data/website')

def update_html_refs():
    """Find all HTML files and replace .jpg/.png with .webp in img tags."""
    
    # Pattern to match img src attributes with jpg/png
    pattern = r'(src=["\'])(assets/[^"\']*?\.(?:jpg|jpeg|png))(["\'])'
    
    total_updates = 0
    
    for html_file in BASE.glob('**/*.html'):
        try:
            content = html_file.read_text(encoding='utf-8')
            
            def replace_src(match):
                prefix = match.group(1)
                old_path = match.group(2)
                suffix = match.group(3)
                
                # Check if .webp version exists
                old_path_str = str(old_path)
                new_path_str = old_path_str.rsplit('.', 1)[0] + '.webp'
                
                if (BASE / new_path_str).exists():
                    return prefix + new_path_str + suffix
                else:
                    return match.group(0)  # Keep original
            
            new_content = re.sub(pattern, replace_src, content)
            
            if new_content != content:
                html_file.write_text(new_content, encoding='utf-8')
                total_updates += 1
                print(f"Updated: {html_file.relative_to(BASE)}")
        except Exception as e:
            print(f"Error processing {html_file}: {e}")
    
    return total_updates

def main():
    print("Scanning HTML files for image references...")
    total = update_html_refs()
    print(f"\nTotal HTML files updated: {total}")

if __name__ == '__main__':
    main()
