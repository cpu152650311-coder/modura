#!/usr/bin/env python3
"""Replace all @modura.build emails -> sales@ems-prefab.com"""
import re
from pathlib import Path

PROJECT = Path(r"c:\Users\Quentel\ClaudeCode\ems-prefab")
NEW_EMAIL = "sales@ems-prefab.com"
changes = 0

for fp in PROJECT.glob("**/*.html"):
    rel = str(fp.relative_to(PROJECT))
    html = fp.read_text(encoding="utf-8")
    new_html = html.replace("sales@modura.build", NEW_EMAIL)
    new_html = new_html.replace("projects@modura.build", NEW_EMAIL)
    new_html = new_html.replace("info@modura.build", NEW_EMAIL)

    if new_html != html:
        fp.write_text(new_html, encoding="utf-8")
        changes += 1
        print(f"  [OK] {fp.relative_to(PROJECT)}")

# Also check llms.txt
llms = PROJECT / "llms.txt"
if llms.exists():
    txt = llms.read_text(encoding="utf-8")
    new_txt = txt.replace("sales@modura.build", NEW_EMAIL)
    if new_txt != txt:
        llms.write_text(new_txt, encoding="utf-8")
        changes += 1
        print("  [OK] llms.txt")

print(f"\nTotal: {changes} files changed")
print(f"All emails -> {NEW_EMAIL}")
