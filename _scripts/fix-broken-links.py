#!/usr/bin/env python3
"""Fix broken contact.html links at wrong depth."""
import re
from pathlib import Path

PROJECT = Path(r"c:\Users\Quentel\ClaudeCode\ems-prefab")

FIXES = [
    # capabilities/systems/hybrid, panelized, volumetric (depth 3): ../../contact.html -> ../../../contact.html
    {
        "dirs": ["capabilities/systems/hybrid", "capabilities/systems/panelized", "capabilities/systems/volumetric"],
        "old": "../../contact.html",
        "new": "../../../contact.html",
    },
    # industries/education, military-emergency, senior-living (depth 2): ../contact.html -> ../../contact.html
    {
        "dirs": ["industries/education", "industries/military-emergency", "industries/senior-living"],
        "old": "../contact.html",
        "new": "../../contact.html",
    },
]

for fix in FIXES:
    for d in fix["dirs"]:
        fp = PROJECT / d / "index.html"
        if fp.exists():
            html = fp.read_text(encoding="utf-8")
            old = fix["old"]
            new = fix["new"]
            if old in html:
                html = html.replace(old, new)
                fp.write_text(html, encoding="utf-8")
                print(f"  [FIX] {d}/index.html: {old} -> {new}")
            else:
                print(f"  [--] {d}/index.html: {old} not found")
        else:
            print(f"  [??] {d}/index.html: file not found")

print("Done.")
