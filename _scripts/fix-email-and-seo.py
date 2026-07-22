#!/usr/bin/env python3
"""
1. Change all emails: info@modura.build / info@ems-prefab.com -> sales@modura.build
2. Add JSON-LD/canonical/OG to 3 missing blog posts
3. Add JSON-LD to privacy and terms
4. Bump CSS cache version
"""
import re
from pathlib import Path

PROJECT = Path(r"c:\Users\Quentel\ClaudeCode\ems-prefab")
SALES = "sales@modura.build"

changes = 0

# ====== 1. Email replacement (all files) ======
for fp in PROJECT.glob("**/*.html"):
    html = fp.read_text(encoding="utf-8")
    new_html = html.replace("info@modura.build", SALES).replace("info@ems-prefab.com", SALES)
    if new_html != html:
        fp.write_text(new_html, encoding="utf-8")
        changes += 1
        print(f"  [EMAIL] {fp.relative_to(PROJECT)}")

# ====== 2. Fix 3 blog posts missing SEO metadata ======
MISSING_BLOGS = [
    "blog/sustainable-modular-building.html",
    "blog/modular-vs-traditional-construction.html",
    "blog/how-modular-hotels-cut-construction-time.html",
]

CANONICAL_BASE = "https://ems-prefab.com"

for blog_path in MISSING_BLOGS:
    fp = PROJECT / blog_path
    if not fp.exists():
        print(f"  [??] {blog_path} not found")
        continue
    html = fp.read_text(encoding="utf-8")

    # Extract title and description from existing meta
    title_m = re.search(r"<title>(.*?)</title>", html)
    desc_m = re.search(r'<meta name="description" content="([^"]+)"', html)
    title = title_m.group(1) if title_m else "MODURA Blog"
    desc = desc_m.group(1) if desc_m else ""

    rel_path = blog_path
    canonical_url = f"{CANONICAL_BASE}/{rel_path}"

    # Build SEO block
    seo_block = f"""<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://ems-prefab.com/generated/hero-modular-construction.webp">
<meta property="og:url" content="{canonical_url}">
<meta property="og:type" content="article">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="https://ems-prefab.com/generated/hero-modular-construction.webp">
<link rel="canonical" href="{canonical_url}">
"""

    # Build Article JSON-LD
    ld_json = f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@graph": [
    {{
      "@type": "Article",
      "headline": "{title}",
      "description": "{desc}",
      "url": "{canonical_url}",
      "publisher": {{ "@type": "Organization", "name": "MODURA", "url": "https://ems-prefab.com" }},
      "datePublished": "2026-07-22",
      "dateModified": "2026-07-22"
    }},
    {{
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://ems-prefab.com/"}},
        {{"@type": "ListItem", "position": 2, "name": "Blog", "item": "https://ems-prefab.com/blog/"}},
        {{"@type": "ListItem", "position": 3, "name": "{title}", "item": "{canonical_url}"}}
      ]
    }}
  ]
}}
</script>"""

    # Insert OG/canonical after the existing meta description
    if '<meta property="og:title"' not in html:
        desc_pos = html.find('<meta name="description"')
        desc_end = html.find('>', desc_pos) + 1
        html = html[:desc_end] + '\n' + seo_block + html[desc_end:]

    # Insert JSON-LD before </head>
    if '<script type="application/ld+json">' not in html:
        html = html.replace('</head>', ld_json + '\n</head>')

    fp.write_text(html, encoding="utf-8")
    changes += 1
    print(f"  [SEO] {blog_path}")

# ====== 3. Add JSON-LD to privacy and terms ======
for page in ["privacy/index.html", "terms/index.html"]:
    fp = PROJECT / page
    if not fp.exists():
        continue
    html = fp.read_text(encoding="utf-8")
    if '<script type="application/ld+json">' in html:
        print(f"  [--] {page} already has JSON-LD")
        continue

    label = "Privacy Policy" if "privacy" in page else "Terms of Service"
    slug = "privacy" if "privacy" in page else "terms"
    ld = f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@graph": [
    {{
      "@type": "Organization",
      "name": "MODURA",
      "url": "https://ems-prefab.com",
      "logo": "https://ems-prefab.com/generated/logo-transparent.png",
      "email": "{SALES}"
    }},
    {{
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://ems-prefab.com/"}},
        {{"@type": "ListItem", "position": 2, "name": "{label}", "item": "https://ems-prefab.com/{slug}/"}}
      ]
    }}
  ]
}}
</script>"""
    html = html.replace('</head>', ld + '\n</head>')
    fp.write_text(html, encoding="utf-8")
    changes += 1
    print(f"  [LD+JSON] {page}")

# ====== 4. Bump CSS cache ======
for fp in PROJECT.glob("**/*.html"):
    if "welcome" in str(fp) or "generated" in str(fp):
        continue
    html = fp.read_text(encoding="utf-8")
    if "styles.css?v=6" in html:
        html = html.replace("styles.css?v=6", "styles.css?v=7")
        fp.write_text(html, encoding="utf-8")

print(f"\nTotal changes: {changes} files")
print("CSS cache: v=6 -> v=7")
