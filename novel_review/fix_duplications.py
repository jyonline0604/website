#!/usr/bin/env python3
"""Fix duplicated content in novel chapters."""

import os
import re

NOVEL_DIR = "/home/openclaw/.openclaw/workspace/novel_review"

def get_chapter_number(filename):
    match = re.search(r'第(\d+)章', filename)
    return int(match.group(1)) if match else 0

def read_chapter(filename):
    filepath = os.path.join(NOVEL_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_chapter(filename, content):
    filepath = os.path.join(NOVEL_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def find_best_split_point(text, chapter_title):
    """
    Find the best split point when chapter content is repeated twice.
    Returns the end position of the first occurrence.
    """
    # The chapter starts with the title line like "# 第XX章 · 標題"
    title_pattern = re.escape(chapter_title)
    
    # Find first occurrence of title (start of chapter)
    first_start = text.find(chapter_title)
    if first_start == -1:
        return None
    
    # Find second occurrence of title (start of repetition)
    second_start = text.find(chapter_title, first_start + len(chapter_title))
    if second_start == -1:
        return None
    
    return second_start

def fix_chapter_with_internal_duplication(filename):
    """Fix chapters where content is repeated twice."""
    content = read_chapter(filename)
    
    # Extract chapter title from first line
    lines = content.split('\n')
    if not lines:
        return False
    
    title_line = lines[0]
    
    # Find the best split point
    split_point = find_best_split_point(content, title_line)
    
    if split_point is None:
        print(f"  Could not find split point for {filename}")
        return False
    
    # Keep only the first occurrence (before the repetition starts)
    fixed_content = content[:split_point]
    
    # Clean up any trailing whitespace
    fixed_content = fixed_content.rstrip() + '\n'
    
    write_chapter(filename, fixed_content)
    return True

def main():
    chapters = [f for f in os.listdir(NOVEL_DIR) if f.startswith('第') and f.endswith('.txt')]
    chapters = sorted(chapters, key=get_chapter_number)
    
    # Chapters with internal duplication (confirmed by analysis)
    duplicated_chapters = [
        21, 22, 23, 24, 25, 26, 27, 28, 29, 30,  # From CH21-CH30 range
        108  # Also has small duplication
    ]
    
    print("FIXING CHAPTERS WITH INTERNAL DUPLICATION")
    print("=" * 50)
    
    fixed_count = 0
    for ch_num in duplicated_chapters:
        filename = f"第{ch_num}章.txt"
        filepath = os.path.join(NOVEL_DIR, filename)
        
        if not os.path.exists(filepath):
            print(f"SKIP {filename} - file not found")
            continue
        
        print(f"Fixing {filename}...", end=" ")
        if fix_chapter_with_internal_duplication(filename):
            print("OK")
            fixed_count += 1
        else:
            print("FAILED")
    
    print(f"\nTotal fixed: {fixed_count}")

if __name__ == "__main__":
    main()
