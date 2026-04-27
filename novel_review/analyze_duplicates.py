#!/usr/bin/env python3
"""Systematic analysis of novel CH1-140 for duplicate/copy-paste issues."""

import os
import re
from collections import defaultdict

NOVEL_DIR = "/home/openclaw/.openclaw/workspace/novel_review"

def get_chapter_number(filename):
    match = re.search(r'第(\d+)章', filename)
    return int(match.group(1)) if match else 0

def read_chapter(filename):
    filepath = os.path.join(NOVEL_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def find_duplicate_paragraphs(text, min_length=100):
    """Find paragraphs that appear more than once in a chapter."""
    paragraphs = re.split(r'\n\n+', text)
    seen = defaultdict(list)
    duplicates = []
    
    for i, para in enumerate(paragraphs):
        para = para.strip()
        if len(para) < min_length:
            continue
        # Normalize whitespace
        normalized = re.sub(r'\s+', ' ', para)
        seen[normalized].append((i, para[:80]))
    
    for para, locations in seen.items():
        if len(locations) > 1:
            duplicates.append({
                'text': para[:100],
                'count': len(locations),
                'positions': [loc[0] for loc in locations]
            })
    return duplicates

def extract_ending(text, num_chars=200):
    """Extract the last num_chars of a chapter."""
    return text[-num_chars:].strip()

def find_similar_endings(chapters, similarity_threshold=0.8):
    """Find chapters with similar endings."""
    endings = {}
    for ch in chapters:
        text = read_chapter(ch)
        ending = extract_ending(text, 300)
        endings[ch] = ending
    
    issues = []
    chapter_list = sorted(endings.keys(), key=get_chapter_number)
    
    for i, ch1 in enumerate(chapter_list):
        for ch2 in chapter_list[i+1:]:
            e1 = endings[ch1]
            e2 = endings[ch2]
            
            # Simple similarity check - count common characters
            len_min = min(len(e1), len(e2))
            if len_min < 50:
                continue
            
            common = 0
            for c1, c2 in zip(e1, e2):
                if c1 == c2:
                    common += 1
            
            similarity = common / len_min
            if similarity >= similarity_threshold:
                issues.append({
                    'ch1': ch1,
                    'ch2': ch2,
                    'similarity': similarity,
                    'e1_preview': e1[:100],
                    'e2_preview': e2[:100]
                })
    
    return issues

def main():
    # Get all chapter files
    chapters = [f for f in os.listdir(NOVEL_DIR) if f.startswith('第') and f.endswith('.txt')]
    chapters = sorted(chapters, key=get_chapter_number)
    
    print(f"Total chapters: {len(chapters)}")
    print(f"Chapter range: {get_chapter_number(chapters[0])} - {get_chapter_number(chapters[-1])}")
    print()
    
    # Find internal duplicates within chapters
    print("=" * 60)
    print("INTERNAL DUPLICATES (same chapter repeated paragraphs)")
    print("=" * 60)
    
    for ch in chapters:
        text = read_chapter(ch)
        dups = find_duplicate_paragraphs(text)
        if dups:
            print(f"\n*** {ch} ***")
            for dup in dups:
                print(f"  Paragraph repeated {dup['count']} times at positions: {dup['positions']}")
                print(f"  Preview: {dup['text'][:80]}...")
    
    # Find similar endings between chapters
    print("\n" + "=" * 60)
    print("SIMILAR ENDINGS (copy-paste between chapters)")
    print("=" * 60)
    
    issues = find_similar_endings(chapters, 0.75)
    for issue in issues:
        ch1_num = get_chapter_number(issue['ch1'])
        ch2_num = get_chapter_number(issue['ch2'])
        print(f"\n*** CH{ch1_num} vs CH{ch2_num} (similarity: {issue['similarity']:.0%}) ***")
        print(f"  CH{ch1_num} ending: {issue['e1_preview'][:80]}...")
        print(f"  CH{ch2_num} ending: {issue['e2_preview'][:80]}...")
    
    print(f"\nTotal similar ending issues: {len(issues)}")

if __name__ == "__main__":
    main()
