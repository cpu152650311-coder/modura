#!/usr/bin/env python3
"""modura: 为内链<5的文章批量插入自然锚文本内链"""
import re, json, glob, os

index = json.load(open('/tmp/modura-index.json'))
cands = json.load(open('/tmp/modura-cands.json'))

def keywords(slug):
    words = re.findall(r'[a-z0-9]+', slug.lower())
    stop = {'modular','construction','guide','2026','vs','the','a','an','for','and','how','to','with','build','guide'}
    return [w for w in words if w not in stop and len(w) > 2]

def anchor_text(title, slug):
    """从标题生成简短锚文本"""
    t = re.sub(r'^(How to |The |A |An )', '', title)
    t = re.sub(r'[:—|].*$', '', t).strip()
    t = re.sub(r'\s+', ' ', t).strip()
    if len(t) > 48:
        t = t[:45].rstrip() + '…'
    return t.lower() if t else slug.replace('-', ' ')

# 补齐候选:通用主题(商业/成本/时间) + 任意高频文章
GENERIC = ['modular-apartment-buildings-cost-guide', 'modular-construction-financing-guide',
           'modular-construction-permitting-zoning-guide', 'modular-construction-timeline-schedule',
           'modular-construction-bim-digital-workflow', 'modular-vs-traditional-construction',
           'modular-construction-rfp-procurement-guide', 'modular-homes-single-family-buyers-guide',
           'modular-construction-lease-vs-buy', 'modular-building-materials-selection-guide']
GENERIC = [g for g in GENERIC if g in index]

fixed = 0
for slug in cands:
    links = cands[slug]
    # 补齐到5条:先加通用,再加其他任意(避免重复)
    for g in GENERIC:
        if len(links) >= 5: break
        if g != slug and g not in links:
            links.append(g)
    if len(links) < 5:
        for other in index:
            if len(links) >= 5: break
            if other != slug and other not in links:
                links.append(other)

# 验证所有链接目标存在
missing = []
for slug, links in cands.items():
    for l in links:
        if l not in index:
            missing.append((slug, l))
print("不存在的目标:", missing[:5] if missing else "无 ✅")

# 插入内链: 在正文长段落末尾加一句话
def insert_links(html, links, self_slug):
    added = 0
    paras = list(re.finditer(r'<p>(.*?)</p>', html, re.S))
    for m in reversed(paras):
        if added >= 5: break
        p_text = m.group(1)
        plain = re.sub(r'<[^>]+>', '', p_text)
        if len(plain) < 180: continue
        if 'href="' in p_text: continue
        insert_at = p_text.rfind('</')
        if insert_at < 0: continue
        link_slug = links[added]
        anchor = anchor_text(index[link_slug], link_slug)
        sentence = f' For a deeper look, our <a href="../blog/{link_slug}.html">{anchor}</a> guide covers the details.'
        new_p = p_text[:insert_at] + sentence + p_text[insert_at:]
        html = html.replace(m.group(0), f'<p>{new_p}</p>', 1)
        added += 1
    return html, added

noil = json.load(open('/tmp/modura-noil.json'))
for slug in noil:
    path = f'blog/{slug}.html'
    html = open(path, encoding='utf-8').read()
    if 'href="../blog/' in html and len(set(re.findall(r'href="\.\./blog/([^"/]+)', html))) >= 5:
        continue
    new_html, added = insert_links(html, cands[slug], slug)
    open(path, 'w', encoding='utf-8').write(new_html)
    fixed += 1
    if added < 5:
        print(f"⚠️ {slug}: 只插入{added}条")

print(f"\n修改: {fixed} 篇")
