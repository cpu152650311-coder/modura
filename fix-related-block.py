#!/usr/bin/env python3
"""modura: 在 article-nav 后插入 Related Articles 区块(5条内链,最可靠方案)"""
import re, json, glob, os

index = json.load(open('/tmp/modura-index.json'))
cands = json.load(open('/tmp/modura-cands.json'))

def keywords(slug):
    words = re.findall(r'[a-z0-9]+', slug.lower())
    stop = {'modular','construction','guide','2026','vs','the','a','an','for','and','how','to','with','build','guide'}
    return [w for w in words if w not in stop and len(w) > 2]

def anchor_text(title, slug):
    t = re.sub(r'^(How to |The |A |An )', '', title)
    t = re.sub(r'[:—|].*$', '', t).strip()
    t = re.sub(r'\s+', ' ', t).strip()
    return t.lower() if t else slug.replace('-', ' ')

# 补齐候选(同上次)
GENERIC = ['modular-apartment-buildings-cost-guide', 'modular-construction-financing-guide',
           'modular-construction-permitting-zoning-guide', 'modular-construction-timeline-schedule',
           'modular-construction-bim-digital-workflow', 'modular-vs-traditional-construction',
           'modular-construction-rfp-procurement-guide', 'modular-homes-single-family-buyers-guide',
           'modular-construction-lease-vs-buy', 'modular-building-materials-selection-guide']
GENERIC = [g for g in GENERIC if g in index]

for slug in cands:
    links = cands[slug]
    for g in GENERIC:
        if len(links) >= 5: break
        if g != slug and g not in links:
            links.append(g)
    if len(links) < 5:
        for other in index:
            if len(links) >= 5: break
            if other != slug and other not in links:
                links.append(other)

RELATED_TPL = '''
<div class="related-articles" style="max-width:var(--container-max);margin:0 auto;padding:var(--sp-12) var(--container-pad);">
  <h2 class="section-title" style="margin-bottom:var(--sp-6);">Related Reading</h2>
  <div class="related-list" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:var(--sp-4);">
    {items}
  </div>
</div>
'''

def make_item(slug):
    anchor = anchor_text(index.get(slug, slug), slug)
    return (f'<a href="../blog/{slug}.html" style="display:block;padding:var(--sp-4);'
            f'border:1px solid var(--c-border);border-radius:var(--r-md);text-decoration:none;'
            f'color:var(--c-text-secondary);font-weight:600;font-size:var(--fs-sm);'
            f'transition:all var(--dur-fast);">{anchor}</a>')

fixed = 0
for slug in cands:
    path = f'blog/{slug}.html'
    html = open(path, encoding='utf-8').read()
    # 已有related区块则跳过
    if 'related-articles' in html or 'Related Reading' in html:
        continue
    # 已有 ≥5 条正文内链则跳过
    existing = set(re.findall(r'href="(?:\.\./)?blog/([^"/]+?)(?:\.html)?"', html))
    existing.discard(slug)
    if len(existing) >= 5:
        continue
    # 在 article-nav 后插入
    marker = '</article>'
    if marker not in html:
        continue
    items = '\n    '.join(make_item(l) for l in links[:5])
    block = RELATED_TPL.format(items=items)
    html = html.replace(marker, marker + '\n' + block, 1)
    open(path, 'w', encoding='utf-8').write(html)
    fixed += 1

print(f"插入related区块: {fixed} 篇")

# 验证
below = []
for f in glob.glob('blog/*.html'):
    if 'blog-page' in f or os.path.basename(f) == 'index.html': continue
    html = open(f, encoding='utf-8').read()
    slug = os.path.basename(f).replace('.html','')
    links = set(re.findall(r'href="(?:\.\./)?blog/([^"/]+?)(?:\.html)?"', html))
    links.discard(slug)
    if len(links) < 5:
        below.append((slug, len(links)))
print(f"内链<5剩余: {len(below)} 篇")
for s, n in sorted(below, key=lambda x: x[1])[:10]:
    print(f"  {s}: {n}")
