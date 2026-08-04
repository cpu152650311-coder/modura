#!/usr/bin/env python3
"""
Auto-generate paginated blog index for ems-prefab.com (MODURA).
Produces MODURA-style cards with blog-card / blog-tag format.
Standard pagination: « ← 1 2 3 ... → »

Usage:
  python3 generate-blog-index.py [--per-page N] [--dry-run]
"""

import os, re, sys, argparse
from datetime import datetime

PER_PAGE = 9
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Category classification by filename keywords
CATEGORY_RULES = [
    (['sustainability','green','leed','breeam','net-zero','energy','carbon','passive',
      'circular','biophilic','well-','solar','recycl','renewable','environmental'],
     'Sustainability'),
    (['hotel','hospitality','resort','motel','lodging','tourism','hostel'],
     'Hospitality'),
    (['healthcare','hospital','medical','clinic','dental','vet','pharmacy','surgical',
      'laboratory','lab-','clean-room','cleanroom','semiconductor','pharma'],
     'Healthcare & Labs'),
    (['education','school','university','college','campus','classroom','student',
      'dormitory','daycare','childcare','library'],
     'Education'),
    (['office','commercial','workplace','coworking','corporate','headquarters','retail',
      'store','showroom','dealership','bank','restaurant','brewery','distillery',
      'gas-station','ev-charging','film','sound-stage','data-center','colocation'],
     'Commercial'),
    (['apartment','residential','housing','affordable','multi-family','mixed-use',
      'senior-living','assisted-living','nursing','studio','condo','townhouse'],
     'Residential'),
    (['industrial','factory','warehouse','manufacturing','gigafactory','production',
      'cold-storage','food-processing','agricultural','farm','battery'],
     'Industrial'),
    (['military','emergency','disaster','relief','defense','barracks','deployable',
      'temporary','field-','rapid-deployment'],
     'Military & Emergency'),
    (['design','architecture','acoustic','soundproof','envelope','foundation',
      'structural','seismic','fire','customization','bim','expansion','addition'],
     'Design & Engineering'),
    (['procurement','rfp','bid','contract','cost','budget','roi','tax','depreciation',
      'insurance','warranty','investment','finance','leasing'],
     'Procurement & Finance'),
    (['standard','certification','mbi','code','compliance','regulation','inspection',
      'quality','iso'],
     'Industry Standards'),
    (['comparison','vs-','versus','alternative','traditional','site-built','container',
      '3d-print','stick-built'],
     'Industry Comparison'),
]

def classify_category(fname, content):
    """Determine category from filename and post content keywords."""
    fname_low = fname.lower()
    content_low = content.lower()[:2000]
    combined = fname_low + ' ' + content_low
    
    for keywords, cat in CATEGORY_RULES:
        if any(kw in combined for kw in keywords):
            return cat
    
    # Check for specific sub-patterns
    if 'modular-' in fname_low:
        # Try to infer from what follows "modular-"
        after = fname_low.split('modular-', 1)[1] if 'modular-' in fname_low else ''
        if any(w in after for w in ['hotel','resort']):
            return 'Hospitality'
        if any(w in after for w in ['hospital','medical','clinic']):
            return 'Healthcare & Labs'
    
    return 'Modular Construction'


def extract_meta(html_path):
    """Extract title, description, category, cover image from a blog post HTML file."""
    with open(html_path) as f:
        content = f.read()
    
    fname = os.path.basename(html_path)
    
    # Title: from <title>, strip " | MODURA" suffix
    title = ''
    m = re.search(r'<title>([^<]+)</title>', content)
    if m:
        title = m.group(1).split('|')[0].strip().rstrip('-').strip()
        title = re.sub(r'\s*\|\s*MODURA\s*$', '', title).strip()
    
    if not title:
        m = re.search(r'<h1[^>]*>([^<]+)</h1>', content)
        if m:
            title = m.group(1).strip()
    if not title:
        title = fname.replace('-', ' ').replace('.html', '').title()
    
    # Description
    desc = ''
    m = re.search(r'<meta name="description" content="([^"]+)"', content)
    if m:
        desc = m.group(1)[:180]
    
    # Category
    cat = classify_category(fname, content)
    
    # Cover image: look for cover/hero pattern
    img = ''
    for pattern in [r'<img[^>]*src="([^"]*(?:cover|hero)[^"]*\.(?:webp|png|jpg))"',
                    r'<img[^>]*src="([^"]*section-1[^"]*\.(?:webp|png|jpg))"',
                    r'<img[^>]*src="([^"]*\.(?:webp|png|jpg))"']:
        m = re.search(pattern, content)
        if m:
            img = m.group(1)
            break
    
    # Blog posts use ../generated/ but blog.html at root uses generated/
    # Normalize: remove ../ prefix for root-level blog.html usage
    if img.startswith('../generated/'):
        img = 'generated/' + img[len('../generated/'):]
    elif img.startswith('../'):
        img = img[3:]
    
    # Verify image exists (relative to project root)
    if img:
        img_abs = os.path.join(PROJECT_DIR, img)
        if not os.path.exists(img_abs):
            # Try with ../generated/ fallback (post may reference differently)
            alt = os.path.join(PROJECT_DIR, 'generated', os.path.basename(img))
            if os.path.exists(alt):
                img = 'generated/' + os.path.basename(img)
            else:
                print(f"  ⚠️  Missing image: {img} (from {fname})", file=sys.stderr)
                img = ''
    
    return {
        'file': fname,
        'title': title[:120],
        'desc': desc[:180],
        'cat': cat,
        'img': img
    }


def build_card(article):
    """Build a single blog card using MODURA-style HTML."""
    img_html = ''
    if article['img']:
        img_html = f'''          <div class="blog-card-img">
            <img src="{article['img']}" alt="{article['title'][:60]}" loading="lazy">
          </div>'''
    
    return f'''      <article class="blog-card" data-reveal>
        <a href="blog/{article['file']}" class="blog-card-link">
{img_html}
          <div class="blog-card-body">
            <span class="blog-tag">{article['cat']}</span>
            <h2>{article['title']}</h2>
            <p>{article['desc']}</p>
          </div>
        </a>
      </article>'''


def build_pagination(page, total_pages):
    """Build standard pagination nav: « ← 1 2 3 ... → »"""
    parts = ['      <nav class="blog-pagination" aria-label="Blog pages">']
    
    def page_url(p):
        if p == 0:
            return 'index.html'
        return f'blog-page-{p+1}.html'
    
    # « First
    if page > 0:
        parts.append(f'        <a href="blog/{page_url(0)}" class="page-btn page-first" title="First page">&laquo;</a>')
    else:
        parts.append(f'        <span class="page-btn page-first disabled">&laquo;</span>')
    
    # ← Previous
    if page > 0:
        parts.append(f'        <a href="blog/{page_url(page-1)}" class="page-btn page-prev" title="Previous page">&larr;</a>')
    else:
        parts.append(f'        <span class="page-btn page-prev disabled">&larr;</span>')
    
    # Page numbers: show ~11 pages window
    window = 5
    start_page = max(0, page - window)
    end_page = min(total_pages - 1, page + window)
    
    if end_page - start_page < 10:
        if start_page == 0:
            end_page = min(total_pages - 1, start_page + 10)
        elif end_page == total_pages - 1:
            start_page = max(0, end_page - 10)
    
    if start_page > 0:
        parts.append(f'        <a href="blog/{page_url(0)}" class="page-num">1</a>')
        if start_page > 1:
            parts.append(f'        <span class="page-dots">&hellip;</span>')
    
    for p in range(start_page, end_page + 1):
        num = p + 1
        if p == page:
            parts.append(f'        <span class="page-num active">{num}</span>')
        else:
            parts.append(f'        <a href="blog/{page_url(p)}" class="page-num">{num}</a>')
    
    if end_page < total_pages - 1:
        if end_page < total_pages - 2:
            parts.append(f'        <span class="page-dots">&hellip;</span>')
        parts.append(f'        <a href="blog/{page_url(total_pages-1)}" class="page-num">{total_pages}</a>')
    
    # Next →
    if page < total_pages - 1:
        parts.append(f'        <a href="blog/{page_url(page+1)}" class="page-btn page-next" title="Next page">&rarr;</a>')
    else:
        parts.append(f'        <span class="page-btn page-next disabled">&rarr;</span>')
    
    # Last »
    if page < total_pages - 1:
        parts.append(f'        <a href="blog/{page_url(total_pages-1)}" class="page-btn page-last" title="Last page">&raquo;</a>')
    else:
        parts.append(f'        <span class="page-btn page-last disabled">&raquo;</span>')
    
    parts.append('      </nav>')
    parts.append(f'      <div class="page-position">Page {page+1} of {total_pages}</div>')
    return '\n'.join(parts)


PAGINATION_CSS = '''
    /* === Standard Pagination (auto-generated) === */
    .blog-pagination {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 4px;
      flex-wrap: wrap;
      margin-top: 48px;
      margin-bottom: 16px;
    }
    .blog-pagination .page-btn,
    .blog-pagination .page-num {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 36px;
      height: 36px;
      padding: 0 8px;
      font-size: 14px;
      color: var(--text-secondary, #6b7280);
      text-decoration: none;
      border: 1px solid var(--border, #2a2a3e);
      border-radius: 6px;
      transition: all 0.2s;
      background: var(--bg-surface, #1a1a2e);
    }
    .blog-pagination .page-btn:hover,
    .blog-pagination .page-num:hover {
      color: var(--accent, #f97316);
      border-color: var(--accent, #f97316);
      background: rgba(249, 115, 22, 0.08);
    }
    .blog-pagination .page-num.active {
      background: var(--accent, #f97316);
      color: #fff;
      border-color: var(--accent, #f97316);
    }
    .blog-pagination .page-btn.disabled,
    .blog-pagination .page-num.disabled {
      opacity: 0.3;
      pointer-events: none;
    }
    .blog-pagination .page-dots {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 36px;
      height: 36px;
      color: var(--text-muted, #6b7280);
    }
    .page-position {
      text-align: center;
      font-size: 12px;
      color: var(--text-muted, #6b7280);
      margin-bottom: 48px;
    }
    @media (max-width: 768px) {
      .blog-pagination .page-btn,
      .blog-pagination .page-num {
        min-width: 32px;
        height: 32px;
        font-size: 12px;
      }
    }'''


def read_template():
    """Read blog.html template, extract head (before blog-list) and tail (from CTA)."""
    template_path = os.path.join(PROJECT_DIR, 'blog.html')
    if not os.path.exists(template_path):
        print("ERROR: blog.html template not found", file=sys.stderr)
        sys.exit(1)
    
    with open(template_path) as f:
        orig = f.read()
    
    # Find blog-list div (where cards go)
    list_start = orig.find('<div class="blog-list">')
    if list_start < 0:
        print("ERROR: No blog-list div found in template", file=sys.stderr)
        sys.exit(1)
    
    # Head: everything up to and including blog-list opening tag + newline
    list_open_end = orig.find('>', list_start) + 1
    head = orig[:list_open_end] + '\n'
    
    # Tail: from <!-- CTA --> to end
    tail_start = orig.find('<!-- CTA -->')
    if tail_start < 0:
        tail_start = orig.find('<section class="cta-band"')
    if tail_start < 0:
        print("ERROR: No CTA section found in template", file=sys.stderr)
        sys.exit(1)
    
    tail = orig[tail_start:]
    
    return head, tail


def main():
    parser = argparse.ArgumentParser(description='Generate paginated blog index for MODURA (ems-prefab.com)')
    parser.add_argument('--per-page', type=int, default=PER_PAGE, help=f'Cards per page (default: {PER_PAGE})')
    parser.add_argument('--dry-run', action='store_true', help='Print without writing')
    args = parser.parse_args()
    
    per_page = args.per_page
    
    # 1. Scan blog HTML files
    blog_dir = os.path.join(PROJECT_DIR, 'blog')
    files = [
        f for f in os.listdir(blog_dir)
        if f.endswith('.html')
        and f not in ('index.html', 'template.html')
        and not f.startswith('blog-page-')
    ]
    # Sort by file mtime, newest first. Filenames are slugs (not dates),
    # so alphabetical order would bury new posts on later pages.
    files.sort(key=lambda f: os.path.getmtime(os.path.join(blog_dir, f)), reverse=True)
    
    print(f"Found {len(files)} blog articles")
    
    # 2. Extract metadata
    articles = []
    for f in files:
        path = os.path.join(blog_dir, f)
        meta = extract_meta(path)
        articles.append(meta)
    
    # Sort newest first (relies on filename sorting since they're descriptive)
    # MODURA filenames aren't sequential — just use alphabetical as-is (sorted above)
    # The original blog.html lists newest first, and filenames are alphabetical
    # which tends to group similar topics. For pagination, alphabetical is fine.
    
    # 3. Read template
    head, tail = read_template()
    
    # 4. Generate paginated pages
    total_pages = (len(articles) + per_page - 1) // per_page
    
    print(f"Generating {total_pages} pages ({per_page} per page)")
    
    for page in range(total_pages):
        start = page * per_page
        end = start + per_page
        page_articles = articles[start:end]
        
        cards_html = '\n\n'.join(build_card(a) for a in page_articles)
        pagination = build_pagination(page, total_pages)
        
        page_html = f'''{head.rstrip()}
{cards_html}
    </div>
{pagination}
{PAGINATION_CSS}
{tail}'''
        
        filename = 'index.html' if page == 0 else f'blog-page-{page+1}.html'
        filepath = os.path.join(blog_dir, filename)
        
        if args.dry_run:
            print(f"  [DRY RUN] {filename}: {len(page_articles)} cards")
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(page_html)
            print(f"  ✓ {filename}: {len(page_articles)} cards")
    
    if not args.dry_run:
        print(f"\nDone! {total_pages} pages, {len(articles)} total cards")


if __name__ == '__main__':
    main()
