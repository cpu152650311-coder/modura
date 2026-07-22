#!/usr/bin/env python3
"""Content quality audit: word count, thin pages, headings structure."""
import re
from pathlib import Path

PROJECT = Path(r"c:\Users\Quentel\ClaudeCode\ems-prefab")

# Thin page threshold
THIN_THRESHOLD = 300  # words

print("=" * 60)
print("CONTENT QUALITY AUDIT")
print("=" * 60)

thin_pages = []
for fp in sorted(PROJECT.glob("**/*.html")):
    rel = str(fp.relative_to(PROJECT)).replace("\\", "/")
    if "welcome" in rel or "generated" in rel:
        continue
    html = fp.read_text(encoding="utf-8")

    # Extract text content (strip HTML tags)
    text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    words = len(text.split())

    if words < THIN_THRESHOLD:
        thin_pages.append((rel, words))

    # Heading structure
    h1s = re.findall(r"<h1[^>]*>(.*?)</h1>", html)
    h2s = re.findall(r"<h2[^>]*>(.*?)</h2>", html)
    h3s = re.findall(r"<h3[^>]*>(.*?)</h3>", html)

# Report thin pages
if thin_pages:
    print(f"\nThin pages (<{THIN_THRESHOLD} words):")
    for p, w in sorted(thin_pages, key=lambda x: x[1]):
        print(f"  {w:5d} words: {p}")
else:
    print(f"\nNo thin pages (<{THIN_THRESHOLD} words) found.")

print("\n" + "=" * 60)
print("PAGE SIZE COMPARISON (top 5 heaviest)")
print("=" * 60)
sizes = []
for fp in sorted(PROJECT.glob("**/*.html")):
    rel = str(fp.relative_to(PROJECT)).replace("\\", "/")
    if "welcome" in rel or "generated" in rel:
        continue
    html = fp.read_text(encoding="utf-8")
    text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    words = len(text.split())
    bytes_size = len(html)
    sizes.append((rel, words, bytes_size))

for rel, words, bs in sorted(sizes, key=lambda x: x[2], reverse=True)[:5]:
    print(f"  {bs:6,d} bytes / {words:5,d} words: {rel}")

print("\n" + "=" * 60)
print("INTERNAL LINKING: Pages with < 5 internal links")
print("=" * 60)
for fp, rel in [(fp, str(fp.relative_to(PROJECT)).replace("\\", "/")) for fp in sorted(PROJECT.glob("**/*.html"))]:
    if "welcome" in rel or "generated" in rel:
        continue
    html = fp.read_text(encoding="utf-8")
    links = re.findall(r'href="([^"]+)"', html)
    internal = [l for l in links if not l.startswith("http") and not l.startswith("mailto:") and not l.startswith("#") and not l.endswith(".css")]
    if len(internal) < 5:
        print(f"  {len(internal):2d} links: {rel}")

print("\nDone.")
