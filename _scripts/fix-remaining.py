#!/usr/bin/env python3
"""Fix the 8 files that didn't match the regex pattern."""
import re
from pathlib import Path

PROJECT = Path(r"c:\Users\Quentel\ClaudeCode\ems-prefab")

FILES = [
    "index.html",
    "capabilities/systems/hybrid/index.html",
    "capabilities/systems/panelized/index.html",
    "capabilities/systems/volumetric/index.html",
    "industries/education/index.html",
    "industries/military-emergency/index.html",
    "industries/senior-living/index.html",
]

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
      <a href="{pfx}process.html">Process</a><a href="{pfx}projects/">Projects</a><a href="{pfx}blog.html">Blog</a><a href="{pfx}about.html">About</a><a href="{pfx}contact.html" class="nav-cta">Get Quote</a>
    </div>
  </div>
</nav>'''

def build_footer(pfx):
    return f'''<footer class="footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-col footer-brand"><span class="logo-text">MODURA</span><p>Premium modular construction for apartments, hotels, and offices. Build better. Build faster.</p></div>
      <div class="footer-col"><h4>Products</h4><a href="{pfx}apartments.html">Apartments</a><a href="{pfx}hotels.html">Hotels</a><a href="{pfx}offices.html">Offices</a><a href="{pfx}capabilities/">Capabilities</a><a href="{pfx}industries/">Industries</a></div>
      <div class="footer-col"><h4>Company</h4><a href="{pfx}about.html">About Us</a><a href="{pfx}process.html">Process</a><a href="{pfx}factory/">Factory</a><a href="{pfx}quality/">Quality</a><a href="{pfx}projects/">Projects</a><a href="{pfx}faq/">FAQ</a><a href="{pfx}blog.html">Blog</a><a href="{pfx}contact.html">Contact</a></div>
      <div class="footer-col"><h4>Contact</h4><a href="mailto:info@modura.build">info@modura.build</a><span>24 Enterprise Way, Suite 100</span></div>
    </div>
    <div class="footer-bottom"><p>&copy; 2026 MODURA. All rights reserved. ISO 9001 &middot; ISO 14001 &middot; CE Certified.</p></div>
  </div>
</footer>'''

for rel_path in FILES:
    fp = PROJECT / rel_path
    depth = get_depth(fp)
    pfx = "../" * depth if depth > 0 else ""

    html = fp.read_text(encoding="utf-8")

    # Replace nav block (from <nav to </nav>)
    nav_pattern = re.compile(r'<nav class="nav" data-nav>.*?</nav>', re.DOTALL)
    new_nav = build_nav(pfx)
    html = nav_pattern.sub(new_nav, html)

    # Replace footer block (from <footer to </footer>)
    footer_pattern = re.compile(r'<footer class="footer">.*?</footer>', re.DOTALL)
    new_footer = build_footer(pfx)
    html = footer_pattern.sub(new_footer, html)

    fp.write_text(html, encoding="utf-8")
    print(f"  [OK] {rel_path} (depth={depth}, pfx='{pfx}')")

print("\nDone.")
