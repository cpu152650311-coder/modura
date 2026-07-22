#!/usr/bin/env python3
"""Check all internal links for broken references."""
import re
from pathlib import Path

PROJECT = Path(r"c:\Users\Quentel\ClaudeCode\ems-prefab")

# Collect all existing page paths
all_pages = set()
for fp in PROJECT.glob("**/*.html"):
    if "welcome" in str(fp) or "node_modules" in str(fp):
        continue
    rel = str(fp.relative_to(PROJECT)).replace("\\", "/")
    # Register all variants
    all_pages.add(rel)
    if rel.endswith("/index.html"):
        dir_path = rel[:-10]  # remove "index.html"
        all_pages.add(dir_path)
        all_pages.add(dir_path[:-1])  # without trailing slash

# Check all internal links
broken = []
for fp in sorted(PROJECT.glob("**/*.html")):
    if "welcome" in str(fp) or "node_modules" in str(fp):
        continue
    rel_path = str(fp.relative_to(PROJECT)).replace("\\", "/")
    html = fp.read_text(encoding="utf-8")
    links = re.findall(r'href="([^"]+)"', html)

    for link in links:
        if link.startswith("http") or link.startswith("mailto:") or link.startswith("#"):
            continue

        # Strip query string and fragment
        clean_link = link.split("?")[0].split("#")[0]
        if clean_link.endswith(".css") or clean_link.endswith(".png") or clean_link.endswith(".ico") or clean_link.endswith(".webp") or clean_link.endswith(".js"):
            continue

        # Resolve relative path
        base_dir = str(fp.parent.relative_to(PROJECT)).replace("\\", "/")

        # Resolve ../ and ./
        if clean_link.startswith("/"):
            resolved = clean_link.lstrip("/")
        else:
            parts = (base_dir + "/" + clean_link).split("/") if base_dir else clean_link.split("/")
            resolved_parts = []
            for p in parts:
                if p == "..":
                    if resolved_parts:
                        resolved_parts.pop()
                elif p and p != ".":
                    resolved_parts.append(p)
            resolved = "/".join(resolved_parts)

        # Check existence on filesystem
        found = False
        checks = [resolved, resolved + ".html", resolved + "/index.html"]
        for check in checks:
            if (PROJECT / check).exists():
                found = True
                break

        if not found:
            broken.append((rel_path, link, resolved))

if broken:
    print(f"Found {len(broken)} broken links:")
    for f, link, resolved in broken:
        print(f"  {f} -> {link}")
else:
    print("No broken links found!")
