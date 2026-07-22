#!/usr/bin/env python3
"""Batch update nav and footer across all MODURA HTML files, then generate sitemap."""
import re
import os
from pathlib import Path
from datetime import date

PROJECT = Path(r"c:\Users\Quentel\ClaudeCode\ems-prefab")

# Nav: the new links to insert
# OLD: "...Offices">\n      <a href="{p}process.html">Process</a>..."
# NEW: insert Capabilities, Industries before Process; Projects before Blog
def patch_file(fp: Path):
    rel = fp.relative_to(PROJECT)
    depth = len(rel.parts) - 1  # 0=root, 1=factory/, 2=capabilities/systems/, 3=capabilities/systems/volumetric/
    pfx = "../" * depth if depth > 0 else ""

    html = fp.read_text(encoding="utf-8")

    # --- NAV UPDATE ---
    # Pattern: the line after Offices that starts the second row of nav links
    # Matches: whitespace + <a href="{pfx}process.html">Process</a>... through </a> before nav-cta
    old_nav_row = re.compile(
        r'(<a href="' + re.escape(pfx) + r'offices\.html">Offices</a>)\s*\n\s*'
        r'(<a href="' + re.escape(pfx) + r'process\.html">Process</a>)'
        r'(<a href="' + re.escape(pfx) + r'blog\.html">Blog</a>)'
        r'(<a href="' + re.escape(pfx) + r'about\.html">About</a>)'
        r'(<a href="' + re.escape(pfx) + r'contact\.html" class="nav-cta">Get Quote</a>)'
    )

    def nav_replacer(m):
        indent = "      "
        return (
            m.group(1) + "\n" +
            indent + f'<a href="{pfx}capabilities/">Capabilities</a>'
                    f'<a href="{pfx}industries/">Industries</a>' + "\n" +
            indent + m.group(2) +
                    f'<a href="{pfx}projects/">Projects</a>' +
                    m.group(3) + m.group(4) + m.group(5)
        )

    html, count_nav = old_nav_row.subn(nav_replacer, html)

    # --- FOOTER UPDATE ---
    # Update Products column: add Capabilities + Industries links after Offices
    products_col = re.compile(
        r'(<h4>Products</h4>)'
        r'(<a href="' + re.escape(pfx) + r'apartments\.html">Apartments</a>)'
        r'(<a href="' + re.escape(pfx) + r'hotels\.html">Hotels</a>)'
        r'(<a href="' + re.escape(pfx) + r'offices\.html">Offices</a>)'
    )
    def products_replacer(m):
        return (
            m.group(1) + m.group(2) + m.group(3) + m.group(4) +
            f'<a href="{pfx}capabilities/">Capabilities</a>'
            f'<a href="{pfx}industries/">Industries</a>'
        )
    html, count_f1 = products_col.subn(products_replacer, html)

    # Update Company column: add Factory, Quality, Projects, FAQ
    company_col = re.compile(
        r'(<h4>Company</h4>)'
        r'(<a href="' + re.escape(pfx) + r'about\.html">About Us</a>)'
        r'(<a href="' + re.escape(pfx) + r'process\.html">Process</a>)'
        r'(<a href="' + re.escape(pfx) + r'blog\.html">Blog</a>)'
        r'(<a href="' + re.escape(pfx) + r'contact\.html">Contact</a>)'
    )
    def company_replacer(m):
        return (
            m.group(1) + m.group(2) + m.group(3) +
            f'<a href="{pfx}factory/">Factory</a>'
            f'<a href="{pfx}quality/">Quality</a>'
            f'<a href="{pfx}projects/">Projects</a>'
            f'<a href="{pfx}faq/">FAQ</a>' +
            m.group(4) + m.group(5)
        )
    html, count_f2 = company_col.subn(company_replacer, html)

    if count_nav or count_f1 or count_f2:
        fp.write_text(html, encoding="utf-8")
        print(f"  [OK] {rel} (nav:{count_nav} prod:{count_f1} comp:{count_f2})")
    else:
        print(f"  [??] {rel} - no matches (may already be updated)")

    return count_nav > 0


# --- MAIN ---
print("=== MODURA Nav/Footer Batch Update ===\n")

html_files = sorted(PROJECT.glob("**/*.html"))
# Exclude blog articles and 404
html_files = [f for f in html_files if "blog/" not in str(f) and f.name != "404.html"]

updated = 0
for fp in html_files:
    if patch_file(fp):
        updated += 1

print(f"\n=== Updated {updated}/{len(html_files)} files ===")

# --- SITEMAP GENERATION ---
print("\n=== Generating sitemap.xml ===")
today = date.today().isoformat()
BASE = "https://ems-prefab.com"

# Manual URL list with priorities
urls = [
    # Core pages
    ("/", "1.0"),
    ("/about/", "0.8"),
    ("/process/", "0.8"),
    ("/contact/", "0.8"),
    ("/blog/", "0.7"),
    # Original product pages
    ("/apartments/", "0.8"),
    ("/hotels/", "0.8"),
    ("/offices/", "0.8"),
    # New trust pages
    ("/factory/", "0.8"),
    ("/quality/", "0.8"),
    ("/projects/", "0.7"),
    ("/faq/", "0.6"),
    ("/quote/", "0.7"),
    ("/privacy/", "0.3"),
    ("/terms/", "0.3"),
    # Capabilities
    ("/capabilities/", "0.8"),
    ("/capabilities/systems/", "0.8"),
    ("/capabilities/systems/volumetric/", "0.7"),
    ("/capabilities/systems/panelized/", "0.7"),
    ("/capabilities/systems/hybrid/", "0.7"),
    ("/capabilities/engineering/", "0.8"),
    ("/capabilities/engineering/structural/", "0.7"),
    ("/capabilities/engineering/sustainability/", "0.7"),
    # Industries
    ("/industries/", "0.8"),
    ("/industries/healthcare/", "0.7"),
    ("/industries/education/", "0.7"),
    ("/industries/senior-living/", "0.7"),
    ("/industries/military-emergency/", "0.7"),
]

# Blog articles
blog_dir = PROJECT / "blog"
if blog_dir.exists():
    for bf in sorted(blog_dir.glob("*.html")):
        slug = bf.stem
        urls.append((f"/blog/{slug}/", "0.6"))

sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for path, priority in urls:
    sitemap += f"  <url>\n"
    sitemap += f"    <loc>{BASE}{path}</loc>\n"
    sitemap += f"    <lastmod>{today}</lastmod>\n"
    sitemap += f"    <priority>{priority}</priority>\n"
    sitemap += f"  </url>\n"
sitemap += '</urlset>\n'

sitemap_path = PROJECT / "sitemap.xml"
sitemap_path.write_text(sitemap, encoding="utf-8")
print(f"  [OK] sitemap.xml written ({len(urls)} URLs)")
print("\n=== Done ===")
