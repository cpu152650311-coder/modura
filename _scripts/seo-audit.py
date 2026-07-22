#!/usr/bin/env python3
"""Comprehensive SEO audit for MODURA site."""
import re
from pathlib import Path

PROJECT = Path(r"c:\Users\Quentel\ClaudeCode\ems-prefab")

def get_files():
    files = []
    for fp in sorted(PROJECT.glob("**/*.html")):
        rel = str(fp.relative_to(PROJECT)).replace("\\", "/")
        if "welcome" in rel or "generated" in rel:
            continue
        files.append((fp, rel))
    return files

# ========== 1. JSON-LD & Schema ==========
print("=" * 60)
print("1. JSON-LD SCHEMA COVERAGE")
print("=" * 60)
pages_with_ld = []
pages_without_ld = []
for fp, rel in get_files():
    html = fp.read_text(encoding="utf-8")
    ld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
    if ld:
        pages_with_ld.append(rel)
    else:
        pages_without_ld.append(rel)

print(f"Pages WITH JSON-LD: {len(pages_with_ld)}")
print(f"Pages WITHOUT JSON-LD: {len(pages_without_ld)}")
for p in pages_without_ld:
    print(f"  MISSING: {p}")

# ========== 2. Email Consistency ==========
print("\n" + "=" * 60)
print("2. EMAIL CONSISTENCY (info@modura.build vs info@ems-prefab.com)")
print("=" * 60)
for fp, rel in get_files():
    html = fp.read_text(encoding="utf-8")
    emails = set(re.findall(r'mailto:([^"]+)', html))
    json_emails = set(re.findall(r'"email":\s*"([^"]+)"', html))
    all_emails = emails | json_emails
    has_modura = any("modura.build" in e for e in all_emails)
    has_emsprefab = any("ems-prefab.com" in e for e in all_emails)
    if has_modura and has_emsprefab:
        print(f"  INCONSISTENT: {rel} -> {all_emails}")

# ========== 3. Meta Titles & Descriptions ==========
print("\n" + "=" * 60)
print("3. META TITLES & DESCRIPTIONS")
print("=" * 60)
issues = []
for fp, rel in get_files():
    html = fp.read_text(encoding="utf-8")
    title_m = re.search(r"<title>(.*?)</title>", html)
    title = title_m.group(1) if title_m else ""
    if len(title) < 30:
        issues.append(f"  SHORT TITLE ({len(title)}c): {rel} -> {title[:80]}")
    elif len(title) > 65:
        issues.append(f"  LONG TITLE ({len(title)}c): {rel} -> {title[:80]}...")

    desc_m = re.search(r'<meta name="description" content="([^"]+)"', html)
    if desc_m:
        desc = desc_m.group(1)
        if len(desc) < 70:
            issues.append(f"  SHORT DESC ({len(desc)}c): {rel}")
        elif len(desc) > 160:
            issues.append(f"  LONG DESC ({len(desc)}c): {rel}")
    elif "404.html" not in rel:
        issues.append(f"  MISSING DESC: {rel}")

for i in issues:
    print(i)
print(f"Total meta issues: {len(issues)}")

# ========== 4. Image Alt Text ==========
print("\n" + "=" * 60)
print("4. IMAGE ALT TEXT AUDIT")
print("=" * 60)
total = 0
missing = 0
for fp, rel in get_files():
    html = fp.read_text(encoding="utf-8")
    imgs = re.findall(r"<img[^>]+>", html)
    for img in imgs:
        total += 1
        alt = re.search(r'alt="([^"]*)"', img)
        if not alt or alt.group(1) == "":
            missing += 1
            src = re.search(r'src="([^"]+)"', img)
            src_val = src.group(1) if src else "unknown"
            print(f"  MISSING ALT: {rel} -> {src_val}")

print(f"Total images: {total}, Missing alt: {missing}, Rate: {((total-missing)/total*100):.1f}%")

# ========== 5. Canonical & OG Tags ==========
print("\n" + "=" * 60)
print("5. CANONICAL & OG TAG COVERAGE")
print("=" * 60)
missing_canonical = []
missing_og = []
for fp, rel in get_files():
    html = fp.read_text(encoding="utf-8")
    if '<link rel="canonical"' not in html:
        missing_canonical.append(rel)
    if '<meta property="og:title"' not in html:
        missing_og.append(rel)

if missing_canonical:
    print(f"Missing canonical ({len(missing_canonical)}):")
    for p in missing_canonical:
        print(f"  {p}")
else:
    print("Canonical: ALL PRESENT ✓")
if missing_og:
    print(f"Missing OG tags ({len(missing_og)}):")
    for p in missing_og:
        print(f"  {p}")
else:
    print("OG tags: ALL PRESENT ✓")

# ========== 6. H1 Audit ==========
print("\n" + "=" * 60)
print("6. H1 USAGE")
print("=" * 60)
for fp, rel in get_files():
    html = fp.read_text(encoding="utf-8")
    h1s = re.findall(r"<h1[^>]*>(.*?)</h1>", html)
    if len(h1s) == 0:
        print(f"  MISSING H1: {rel}")
    elif len(h1s) > 1:
        print(f"  MULTIPLE H1 ({len(h1s)}): {rel}")

print("\nDone.")
