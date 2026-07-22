#!/usr/bin/env python3
"""
Update all pages with per-page hero background images.
Each .page-hero section gets --hero-bg CSS variable with correct relative path.
Also bump CSS cache version to v=8.
"""
import re
from pathlib import Path

PROJECT = Path(r"c:\Users\Quentel\ClaudeCode\ems-prefab")

# Map of page path -> hero image file (no extension, script adds .webp)
HERO_MAP = {
    "about.html": "hero-about",
    "apartments.html": "hero-apartments",
    "blog.html": "hero-blog",
    "contact.html": "hero-contact",
    "hotels.html": "hero-hotels",
    "offices.html": "hero-offices",
    "process.html": "hero-process",
    "capabilities/index.html": "hero-capabilities",
    "capabilities/engineering/index.html": "hero-engineering",
    "capabilities/engineering/structural/index.html": "hero-structural",
    "capabilities/engineering/sustainability/index.html": "hero-sustainability",
    "capabilities/systems/index.html": "hero-building-systems",
    "capabilities/systems/hybrid/index.html": "hero-hybrid",
    "capabilities/systems/panelized/index.html": "hero-panelized",
    "capabilities/systems/volumetric/index.html": "hero-volumetric",
    "design-guides/index.html": "hero-design-guides",
    "factory/index.html": "hero-factory",
    "faq/index.html": "hero-faq",
    "how-it-works/index.html": "hero-how-it-works",
    "industries/index.html": "hero-industries",
    "industries/education/index.html": "hero-education",
    "industries/healthcare/index.html": "hero-healthcare",
    "industries/military-emergency/index.html": "hero-military",
    "industries/senior-living/index.html": "hero-senior-living",
    "privacy/index.html": "hero-privacy",
    "projects/index.html": "hero-projects",
    "quality/index.html": "hero-quality",
    "quote/index.html": "hero-quote",
    "shipping/index.html": "hero-shipping",
    "terms/index.html": "hero-terms",
    "blog/modular-office-buildings-guide.html": "hero-office-buildings-guide",
}

changes = 0

for page_path, hero_id in HERO_MAP.items():
    fp = PROJECT / page_path
    if not fp.exists():
        print(f"  [--] Not found: {page_path}")
        continue

    html = fp.read_text(encoding="utf-8")

    # Calculate depth for relative path
    depth = page_path.count("/")
    pfx = "../" * depth if depth > 0 else ""

    # Build the style attribute
    hero_url = f"{pfx}generated/{hero_id}.webp"
    style_attr = f'style="--hero-bg: url(\'{hero_url}\');"'

    # Add --hero-bg to .page-hero section
    # Pattern: <section class="page-hero">
    old = '<section class="page-hero">'
    new = f'<section class="page-hero" {style_attr}>'

    if old in html:
        html = html.replace(old, new, 1)
    else:
        # Might already have style attr or other variant
        print(f"  [??] No standard page-hero in: {page_path}")
        continue

    fp.write_text(html, encoding="utf-8")
    changes += 1
    print(f"  [OK] {page_path} -> {hero_url}")

# Bump CSS cache version v=7 -> v=8
for fp in PROJECT.glob("**/*.html"):
    rel = str(fp.relative_to(PROJECT))
    if "welcome" in rel:
        continue
    html = fp.read_text(encoding="utf-8")
    if "styles.css?v=7" in html:
        html = html.replace("styles.css?v=7", "styles.css?v=8")
        fp.write_text(html, encoding="utf-8")

print(f"\nTotal: {changes} pages updated")
print("CSS cache: v=7 -> v=8")
