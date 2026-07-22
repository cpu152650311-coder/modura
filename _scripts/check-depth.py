#!/usr/bin/env python3
"""Find all wrong-depth contact.html and other links across site."""
from pathlib import Path
import re

PROJECT = Path(r"c:\Users\Quentel\ClaudeCode\ems-prefab")
issues = []

for fp in PROJECT.glob("**/*.html"):
    rel = str(fp.relative_to(PROJECT)).replace("\\", "/")
    if "welcome" in rel:
        continue
    depth = rel.count("/")
    expected_up = "../" * depth if depth > 0 else ""

    html = fp.read_text(encoding="utf-8")

    # Check all relative href links for wrong depth
    for m in re.finditer(r'href="((?:\.\./)+)([^"]+)"', html):
        actual_prefix = m.group(1)
        target = m.group(2)
        # Skip absolute URLs, mailto, anchors, generated/
        if target.startswith(("http", "mailto:", "#", "generated/", "tel:")):
            continue
        # Skip CSS/JS files
        if target.endswith((".css", ".js")):
            continue
        # Check if depth is correct
        expected = expected_up + target.replace("../", "").replace("./", "")
        # If the target itself has ../, we need to check differently
        if actual_prefix != expected_up:
            issues.append((rel, m.group(0), actual_prefix, expected_up, target))

for rel, match, actual, expected, target in issues:
    print(f"WRONG: {rel}")
    print(f"  {match}")
    print(f"  expected prefix: '{expected}' (depth={rel.count('/')})")

print(f"\nTotal issues: {len(issues)}")
