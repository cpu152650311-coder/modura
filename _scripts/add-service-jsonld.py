#!/usr/bin/env python3
"""Add Service JSON-LD to capabilities hub pages."""
from pathlib import Path

PROJECT = Path(r"c:\Users\Quentel\ClaudeCode\ems-prefab")

PAGES = {
    "capabilities/index.html": {
        "name": "Modular Construction Capabilities — Building Systems, Engineering & Production",
        "desc": "Complete modular construction capabilities: volumetric, panelized, and hybrid building systems; structural and sustainability engineering; factory production with 14-station assembly line."
    },
    "capabilities/systems/index.html": {
        "name": "Modular Building Systems — Volumetric, Panelized & Hybrid Construction",
        "desc": "Three modular building systems compared: 3D volumetric modules for maximum factory completion, 2D panelized systems for shipping efficiency, and hybrid systems combining both approaches."
    },
    "capabilities/engineering/index.html": {
        "name": "Modular Construction Engineering — Structural Design, MEP & Sustainability",
        "desc": "Full in-house engineering for modular construction: structural design to Eurocodes EN 1990-1999, BIM coordination to LOD 400, MEP integration, fire strategy, acoustic design, and sustainability analysis."
    }
}

for rel_path, svc in PAGES.items():
    fp = PROJECT / rel_path
    html = fp.read_text(encoding="utf-8")

    service_json = f'''<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@graph": [
    {{
      "@type": "Service",
      "name": "{svc["name"]}",
      "provider": {{ "@type": "Organization", "name": "MODURA", "url": "https://ems-prefab.com" }},
      "description": "{svc["desc"]}",
      "areaServed": ["US", "EU", "UK", "AU", "Middle East", "Asia-Pacific"],
      "serviceType": "Modular Construction"
    }},
    {{
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://ems-prefab.com/"}},
        {{"@type": "ListItem", "position": 2, "name": "{svc["name"].split(" — ")[0].replace("Modular ","")}", "item": "https://ems-prefab.com/{rel_path.replace('index.html','')}"}}
      ]
    }}
  ]
}}
</script>'''

    # Replace existing BreadcrumbList-only JSON-LD with Service + BreadcrumbList
    import re
    old = re.compile(r'<script type="application/ld\+json">.*?</script>', re.DOTALL)
    html = old.sub(service_json, html, count=1)

    fp.write_text(html, encoding="utf-8")
    print(f"  [OK] {rel_path}")

print("Done.")
