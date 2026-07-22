#!/usr/bin/env python3
"""
Update MODURA footer site-wide:
1. Replace footer-brand: add logo img + MODURA text
2. Remove Contact column (email + address)
3. Reorganize: Brand | Products | Resources | Company
4. Change address to Shenzhen
"""
import re
from pathlib import Path

PROJECT = Path(r"c:\Users\Quentel\ClaudeCode\ems-prefab")
NEW_ADDRESS = "Qianwan Hard Technology Industrial Park, Bao'an District, Shenzhen, Guangdong 518101, China"

html_files = [f for f in PROJECT.glob("**/*.html") if "welcome" not in str(f) and "generated" not in str(f)]
print(f"Found {len(html_files)} HTML files")

updated_footer = 0
updated_address = 0

for fp in html_files:
    rel = fp.relative_to(PROJECT)
    depth = len(rel.parts) - 1
    pfx = "../" * depth if depth > 0 else ""

    html = fp.read_text(encoding="utf-8")
    original = html
    changed = False

    # --- 1. Replace old address everywhere ---
    old_addr = "24 Enterprise Way, Suite 100"
    if old_addr in html:
        html = html.replace(old_addr, NEW_ADDRESS)
        updated_address += 1
        changed = True

    # --- 2. Remove Contact column (email + address span) ---
    contact_re = re.compile(
        r'<div class="footer-col"><h4>Contact</h4><a href="mailto:[^"]+">[^<]*</a><span>[^<]*</span></div>'
    )
    if contact_re.search(html):
        html = contact_re.sub('', html)
        changed = True

    # --- 3. Replace footer-brand: add logo img before MODURA text ---
    brand_re = re.compile(
        r'(<div class="footer-col footer-brand">)'
        r'<span class="logo-text">MODURA</span>'
        r'(<p>Premium modular construction for apartments, hotels, and offices\. Build better\. Build faster\.</p></div>)'
    )
    if brand_re.search(html):
        new_brand = (
            r'\1'
            f'<a href="{pfx}index.html" class="footer-logo">'
            f'<img src="{pfx}generated/logo-transparent.png" alt="MODURA" class="logo-mark" width="36" height="36">'
            f'<span class="logo-text">MODURA</span></a>'
            r'\2'
        )
        html = brand_re.sub(new_brand, html)
        changed = True

    # --- 4. Split Company column into Resources + Company ---
    # Match the entire Company div with all inline links
    company_re = re.compile(
        r'<div class="footer-col"><h4>Company</h4>'
        r'(.*?)'
        r'</div>'
    )
    m = company_re.search(html)
    if m:
        company_content = m.group(1)
        # Extract all <a> links
        links = re.findall(r'<a href="([^"]+)">([^<]+)</a>', company_content)

        # Define which links go to Resources vs Company
        resource_labels = {'How It Works', 'Design Guides', 'Shipping', 'Projects', 'FAQ', 'Blog'}
        company_labels = {'About Us', 'Process', 'Factory', 'Quality', 'Contact'}

        resource_links = [(href, label) for href, label in links if label in resource_labels]
        company_links = [(href, label) for href, label in links if label in company_labels]

        if resource_links and company_links:
            resource_html = '<div class="footer-col"><h4>Resources</h4>' + ''.join(
                f'<a href="{h}">{l}</a>' for h, l in resource_links
            ) + '</div>'
            company_html = '<div class="footer-col"><h4>Company</h4>' + ''.join(
                f'<a href="{h}">{l}</a>' for h, l in company_links
            ) + '</div>'

            html = html.replace(m.group(0), resource_html + company_html)
            changed = True

    if changed:
        fp.write_text(html, encoding="utf-8")
        updated_footer += 1
        print(f"  [OK] {rel}")

print(f"\nDone: {updated_footer} footers updated, {updated_address} address replacements")
