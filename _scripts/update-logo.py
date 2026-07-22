#!/usr/bin/env python3
"""Replace CSS logo-mark span with actual logo image + add favicon links in all HTML files."""
from pathlib import Path

PROJECT = Path(r"c:\Users\Quentel\ClaudeCode\ems-prefab")
EXCLUDE = {"blog/", "404.html"}

FAVICON_LINKS = '''<link rel="icon" type="image/x-icon" href="{pfx}generated/favicon.ico">
<link rel="apple-touch-icon" sizes="180x180" href="{pfx}generated/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="192x192" href="{pfx}generated/icon-192.png">
<link rel="icon" type="image/png" sizes="512x512" href="{pfx}generated/icon-512.png">'''

count = 0
for fp in PROJECT.rglob("*.html"):
    rel = str(fp.relative_to(PROJECT)).replace("\\", "/")
    if any(rel.startswith(ex) for ex in EXCLUDE):
        continue
    html = fp.read_text(encoding="utf-8")
    depth = len(fp.relative_to(PROJECT).parts) - 1
    pfx = "../" * depth if depth > 0 else ""

    # 1. Replace logo-mark span with img
    old_logo = '<span class="logo-mark"></span>'
    new_logo = f'<img src="{pfx}generated/logo-transparent.png" alt="MODURA" class="logo-mark" width="32" height="32">'
    if old_logo in html:
        html = html.replace(old_logo, new_logo)
    else:
        print(f"  [WARN] {rel}: logo-mark span not found")
        continue

    # 2. Add favicon links after viewport meta (only if not already present)
    if 'favicon.ico' not in html:
        favicon_html = FAVICON_LINKS.format(pfx=pfx)
        html = html.replace(
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f'<meta name="viewport" content="width=device-width, initial-scale=1.0">\n{favicon_html}'
        )

    fp.write_text(html, encoding="utf-8")
    count += 1
    print(f"  [OK] {rel}")

print(f"\nDone. Updated {count} files")
