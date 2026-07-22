#!/usr/bin/env python3
"""Fix wrong asset paths on depth-2 and depth-3 pages."""
from pathlib import Path

PROJECT = Path(r"c:\Users\Quentel\ClaudeCode\ems-prefab")

# Pages with wrong paths and their correct depth
FIXES = {
    # Depth 2: industries/education, military-emergency, senior-living
    "industries/education/index.html": {
        "depth": 2,
        "old_css_prefix": "../",
        "new_css_prefix": "../../",
        "old_contact_prefix": "../../../",  # contact.html at wrong depth
        "new_contact_prefix": "../../",
    },
    "industries/military-emergency/index.html": {
        "depth": 2,
        "old_css_prefix": "../",
        "new_css_prefix": "../../",
        "old_contact_prefix": "../../../",
        "new_contact_prefix": "../../",
    },
    "industries/senior-living/index.html": {
        "depth": 2,
        "old_css_prefix": "../",
        "new_css_prefix": "../../",
        "old_contact_prefix": "../../../",
        "new_contact_prefix": "../../",
    },
    # Depth 3: capabilities/systems/hybrid, panelized, volumetric
    "capabilities/systems/hybrid/index.html": {
        "depth": 3,
        "old_css_prefix": "../../",
        "new_css_prefix": "../../../",
        "old_contact_prefix": "../../../../",
        "new_contact_prefix": "../../../",
    },
    "capabilities/systems/panelized/index.html": {
        "depth": 3,
        "old_css_prefix": "../../",
        "new_css_prefix": "../../../",
        "old_contact_prefix": "../../../../",
        "new_contact_prefix": "../../../",
    },
    "capabilities/systems/volumetric/index.html": {
        "depth": 3,
        "old_css_prefix": "../../",
        "new_css_prefix": "../../../",
        "old_contact_prefix": "../../../../",
        "new_contact_prefix": "../../../",
    },
}

for page_rel, fix in FIXES.items():
    fp = PROJECT / page_rel
    if not fp.exists():
        print(f"  [--] Not found: {page_rel}")
        continue

    html = fp.read_text(encoding="utf-8")
    original = html

    old_css = fix["old_css_prefix"]
    new_css = fix["new_css_prefix"]
    old_contact = fix["old_contact_prefix"]
    new_contact = fix["new_contact_prefix"]

    # Fix CSS/JS paths: design-tokens.css, styles.css, reveal.js
    for asset in ["design-tokens.css", "styles.css", "reveal.js"]:
        old_path = f'{old_css}{asset}'
        new_path = f'{new_css}{asset}'
        html = html.replace(old_path, new_path)

    # Fix contact.html links
    html = html.replace(f'{old_contact}contact.html', f'{new_contact}contact.html')

    if html != original:
        fp.write_text(html, encoding="utf-8")
        print(f"  [OK] {page_rel}")
    else:
        print(f"  [??] No changes: {page_rel}")

print("\nDone.")
