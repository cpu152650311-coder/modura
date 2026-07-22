#!/usr/bin/env python3
"""Update nav and footer across ALL HTML files to add shipping, how-it-works, design-guides links."""
import re
from pathlib import Path

PROJECT = Path(r"c:\Users\Quentel\ClaudeCode\ems-prefab")

# Exclude blog articles and 404
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
      <a href="{pfx}apartments.html">Apartments</a><a href="{pfx}hotels.html">Hotels</a><a href="{pfx}offices.html">Offices</a>
      <a href="{pfx}capabilities/">Capabilities</a><a href="{pfx}industries/">Industries</a>
      <a href="{pfx}process.html">Process</a><a href="{pfx}how-it-works/">How It Works</a><a href="{pfx}design-guides/">Design Guides</a><a href="{pfx}shipping/">Shipping</a>
      <a href="{pfx}projects/">Projects</a><a href="{pfx}blog.html">Blog</a><a href="{pfx}about.html">About</a><a href="{pfx}contact.html" class="nav-cta">Get Quote</a>
    </div>
  </div>
</nav>'''

def build_footer(pfx):
    return f'''<footer class="footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-col footer-brand"><span class="logo-text">MODURA</span><p>Premium modular construction for apartments, hotels, and offices. Build better. Build faster.</p></div>
      <div class="footer-col"><h4>Products</h4><a href="{pfx}apartments.html">Apartments</a><a href="{pfx}hotels.html">Hotels</a><a href="{pfx}offices.html">Offices</a><a href="{pfx}capabilities/">Capabilities</a><a href="{pfx}industries/">Industries</a></div>
      <div class="footer-col"><h4>Company</h4><a href="{pfx}about.html">About Us</a><a href="{pfx}process.html">Process</a><a href="{pfx}how-it-works/">How It Works</a><a href="{pfx}factory/">Factory</a><a href="{pfx}quality/">Quality</a><a href="{pfx}shipping/">Shipping</a><a href="{pfx}design-guides/">Design Guides</a><a href="{pfx}projects/">Projects</a><a href="{pfx}faq/">FAQ</a><a href="{pfx}blog.html">Blog</a><a href="{pfx}contact.html">Contact</a></div>
      <div class="footer-col"><h4>Contact</h4><a href="mailto:info@modura.build">info@modura.build</a><span>24 Enterprise Way, Suite 100</span></div>
    </div>
    <div class="footer-bottom"><p>&copy; 2026 MODURA. All rights reserved. ISO 9001 &middot; ISO 14001 &middot; CE Certified.</p></div>
  </div>
</footer>'''

files = get_all_html()
print(f"Found {len(files)} HTML files to update\n")

updated = 0
skipped = 0

for fp in files:
    rel = str(fp.relative_to(PROJECT)).replace("\\", "/")
    depth = get_depth(fp)
    pfx = "../" * depth if depth > 0 else ""

    html = fp.read_text(encoding="utf-8")

    # Check if this file already has the new nav (has "How It Works" link)
    if 'how-it-works/' in html:
        skipped += 1
        print(f"  [SKIP] {rel} (already updated)")
        continue

    # Replace nav block
    nav_pattern = re.compile(r'<nav class="nav" data-nav>.*?</nav>', re.DOTALL)
    new_nav = build_nav(pfx)
    html = nav_pattern.sub(new_nav, html)

    # Replace footer block
    footer_pattern = re.compile(r'<footer class="footer">.*?</footer>', re.DOTALL)
    new_footer = build_footer(pfx)
    html = footer_pattern.sub(new_footer, html)

    fp.write_text(html, encoding="utf-8")
    updated += 1
    print(f"  [OK] {rel} (depth={depth}, pfx='{pfx}')")

print(f"\nDone. Updated: {updated}, Skipped: {skipped}")
