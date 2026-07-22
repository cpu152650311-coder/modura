#!/usr/bin/env python3
"""Update all HTML files with new dropdown nav structure."""
import re
from pathlib import Path

PROJECT = Path(r"c:\Users\Quentel\ClaudeCode\ems-prefab")

EXCLUDE = {"blog/", "404.html"}

def get_all_html():
    files = []
    for fp in PROJECT.rglob("*.html"):
        rel = str(fp.relative_to(PROJECT)).replace("\\", "/")
        if any(rel.startswith(ex) for ex in EXCLUDE):
            continue
        files.append(fp)
    return files

def get_depth(fp):
    return len(fp.relative_to(PROJECT).parts) - 1

def build_nav(pfx):
    return f'''<nav class="nav" data-nav>
  <div class="nav-inner">
    <a href="{pfx}index.html" class="nav-logo"><span class="logo-mark"></span><span class="logo-text">MODURA</span></a>
    <button class="nav-toggle" data-nav-toggle aria-label="Menu"><span></span><span></span><span></span></button>
    <div class="nav-menu" data-nav-menu>
      <div class="nav-dropdown" data-nav-dropdown>
        <span class="nav-dropdown-toggle">Products</span>
        <div class="nav-dropdown-menu">
          <a href="{pfx}apartments.html">Apartments</a>
          <a href="{pfx}hotels.html">Hotels</a>
          <a href="{pfx}offices.html">Offices</a>
        </div>
      </div>
      <div class="nav-dropdown" data-nav-dropdown>
        <a href="{pfx}capabilities/" class="nav-dropdown-toggle">Capabilities</a>
        <div class="nav-dropdown-menu">
          <a href="{pfx}capabilities/">Overview</a>
          <a href="{pfx}capabilities/systems/">Building Systems</a>
          <a href="{pfx}capabilities/engineering/">Engineering</a>
        </div>
      </div>
      <div class="nav-dropdown" data-nav-dropdown>
        <a href="{pfx}industries/" class="nav-dropdown-toggle">Industries</a>
        <div class="nav-dropdown-menu">
          <a href="{pfx}industries/">Overview</a>
          <a href="{pfx}industries/healthcare/">Healthcare</a>
          <a href="{pfx}industries/education/">Education</a>
          <a href="{pfx}industries/senior-living/">Senior Living</a>
          <a href="{pfx}industries/military-emergency/">Military &amp; Emergency</a>
        </div>
      </div>
      <div class="nav-dropdown" data-nav-dropdown>
        <span class="nav-dropdown-toggle">Resources</span>
        <div class="nav-dropdown-menu">
          <a href="{pfx}how-it-works/">How It Works</a>
          <a href="{pfx}design-guides/">Design Guides</a>
          <a href="{pfx}shipping/">Shipping</a>
          <a href="{pfx}projects/">Projects</a>
          <a href="{pfx}faq/">FAQ</a>
          <a href="{pfx}blog.html">Blog</a>
        </div>
      </div>
      <div class="nav-dropdown" data-nav-dropdown>
        <span class="nav-dropdown-toggle">Company</span>
        <div class="nav-dropdown-menu">
          <a href="{pfx}about.html">About</a>
          <a href="{pfx}process.html">Process</a>
          <a href="{pfx}factory/">Factory</a>
          <a href="{pfx}quality/">Quality</a>
          <a href="{pfx}contact.html">Contact</a>
        </div>
      </div>
      <a href="{pfx}contact.html" class="nav-cta">Get Quote</a>
    </div>
  </div>
</nav>'''

files = get_all_html()
print(f"Found {len(files)} HTML files to update\n")

updated = 0
for fp in files:
    rel = str(fp.relative_to(PROJECT)).replace("\\", "/")
    depth = get_depth(fp)
    pfx = "../" * depth if depth > 0 else ""

    html = fp.read_text(encoding="utf-8")

    # Replace nav block (from <nav to </nav>)
    nav_pattern = re.compile(r'<nav class="nav" data-nav>.*?</nav>', re.DOTALL)
    new_nav = build_nav(pfx)
    if not nav_pattern.search(html):
        print(f"  [WARN] {rel}: no nav found")
        continue

    html = nav_pattern.sub(new_nav, html)
    fp.write_text(html, encoding="utf-8")
    updated += 1
    print(f"  [OK] {rel} (depth={depth}, pfx='{pfx}')")

print(f"\nDone. Updated: {updated} files")
