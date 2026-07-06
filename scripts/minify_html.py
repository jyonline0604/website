"""Minify HTML files for kofhk.com — no external dependencies.
Usage: python scripts/minify_html.py [--dry-run]
"""
import re
import os
import sys
from pathlib import Path
from html.parser import HTMLParser

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent

# Files/dirs to skip
SKIP_FILES = {'404.html', 'offline.html', 'chat-test.html', 'chapter-template.html'}
SKIP_PREFIXES = ('_fetched_',)

# Conservative inline CSS minification
def minify_css(css):
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)  # remove comments
    css = re.sub(r'\s+', ' ', css)  # collapse whitespace
    css = re.sub(r'\s*([{}:;,>+~])\s*', r'\1', css)  # remove whitespace around separators
    css = re.sub(r';\s*}', '}', css)  # remove trailing semicolons before }
    return css.strip()

# Conservative inline JS minification
def minify_js(js):
    # Remove single-line comments (careful with URLs)
    js = re.sub(r'(?<!:)//(?!\S*?(?:https?:|ftp:))[^\n]*', '', js)
    # Remove multi-line comments
    js = re.sub(r'/\*.*?\*/', '', js, flags=re.DOTALL)
    # Collapse whitespace but preserve newlines (they matter in JS)
    lines = []
    for line in js.split('\n'):
        stripped = line.strip()
        if stripped:
            lines.append(stripped)
    return '\n'.join(lines)

def minify_html(filepath, dry_run=False):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    original_size = len(html)

    # Step 1: Extract and protect <style>, <script>, <pre>, <textarea> blocks
    protected = {}
    counter = [0]

    def protect(match):
        key = f'__PROTECTED_{counter[0]}__'
        counter[0] += 1
        tag_name = match.group(1).lower()
        attrs = match.group(2) or ''
        content = match.group(3) or ''
        if tag_name == 'style':
            protected[key] = f'<style{attrs}>{minify_css(content)}</style>'
        elif tag_name == 'script':
            protected[key] = f'<script{attrs}>{minify_js(content)}</script>'
        else:
            protected[key] = match.group(0)  # don't touch <pre>, <textarea>
        return key

    # Protect style, script, pre, textarea blocks
    html = re.sub(
        r'<(style|script|pre|textarea)([^>]*)>([\s\S]*?)</\1>',
        protect,
        html,
        flags=re.I
    )

    # Step 2: Remove HTML comments (keep conditional comments, IE directives, and meta)
    html = re.sub(r'<!--(?![\s\[])(?!.*?\[endif\])(.*?)-->', '', html, flags=re.DOTALL)

    # Step 3: Collapse whitespace between HTML tags
    html = re.sub(r'>\s+<', '><', html)

    # Step 4: Collapse multiple spaces within lines (preserving attribute meaning)
    html = re.sub(r' {2,}', ' ', html)

    # Step 5: Remove blank lines
    html = re.sub(r'\n\s*\n', '\n', html)

    # Step 6: Remove leading/trailing whitespace on each line
    lines = [l.strip() for l in html.split('\n')]
    html = '\n'.join(l for l in lines if l)

    # Step 7: Restore protected blocks
    for key, content in protected.items():
        html = html.replace(key, content)

    new_size = len(html)
    savings = (1 - new_size / original_size) * 100 if original_size > 0 else 0

    if not dry_run:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

    return original_size, new_size, savings


def main():
    dry_run = '--dry-run' in sys.argv
    action = 'DRY RUN' if dry_run else 'Minifying'

    html_files = [f for f in BASE_DIR.glob('*.html')
                  if f.name not in SKIP_FILES
                  and not f.name.startswith(SKIP_PREFIXES)]

    print(f"{action} {len(html_files)} HTML files...")
    print()

    total_orig = 0
    total_new = 0

    for filepath in sorted(html_files):
        orig, new, savings = minify_html(filepath, dry_run)
        total_orig += orig
        total_new += new
        indicator = 'OK' if savings > 0 else '--'
        print(f"  {indicator} {filepath.name}: {orig/1024:.1f}KB -> {new/1024:.1f}KB ({savings:.1f}%)")

    total_savings = (1 - total_new / total_orig) * 100 if total_orig > 0 else 0
    print()
    print(f"Total: {total_orig/1024:.1f}KB → {total_new/1024:.1f}KB ({total_savings:.1f}% saved)")
    print(f"Reduction: {(total_orig - total_new) / 1024:.1f}KB")

    if dry_run:
        print("\n[DRY RUN — no files changed]")


if __name__ == '__main__':
    main()
