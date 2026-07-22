#!/usr/bin/env python3
"""Add Home link as first item in nav-menu across all HTML files."""
import re
from pathlib import Path

PROJECT = Path(r"c:\Users\Quentel\ClaudeCode\ems-prefab")
EXCLUDE = {"blog/", "404.html"}

count = 0
for fp in PROJECT.rglob("*.html"):
    rel = str(fp.relative_to(PROJECT)).replace("\\", "/")
    if any(rel.startswith(ex) for ex in EXCLUDE):
        continue
    html = fp.read_text(encoding="utf-8")
    depth = len(fp.relative_to(PROJECT).parts) - 1
    pfx = "../" * depth if depth > 0 else ""

    old = '<div class="nav-menu" data-nav-menu>\n      <div class="nav-dropdown" data-nav-dropdown>\n        <span class="nav-dropdown-toggle">Products</span>'
    new = f'<div class="nav-menu" data-nav-menu>\n      <a href="{pfx}index.html">Home</a>\n      <div class="nav-dropdown" data-nav-dropdown>\n        <span class="nav-dropdown-toggle">Products</span>'

    if old in html:
        html = html.replace(old, new)
        fp.write_text(html, encoding="utf-8")
        count += 1
        print(f"  [OK] {rel}")
    else:
        print(f"  [MISS] {rel}")

print(f"\nDone. Updated {count} files")
