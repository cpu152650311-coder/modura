#!/usr/bin/env python3
"""
Auto-generate paginated blog index from blog/ HTML files.
Eliminates manual index editing, git conflicts, card format drift, and duplicates.

Usage:
  python3 generate-blog-index.py [--per-page N] [--dry-run]
"""

import os, re, sys, argparse
from datetime import datetime

PER_PAGE = 9
BLOG_DIR = os.path.dirname(os.path.abspath(__file__))

def extract_meta(html_path):
    """Extract title, description, category, cover image from a blog HTML file."""
    with open(html_path) as f:
        content = f.read()
    
    # Title: from <title> or first <h1>
    title = ""
    m = re.search(r'<title>([^<]+)</title>', content)
    if m:
        title = m.group(1).split('|')[0].strip().rstrip('-').strip()
    if not title:
        m = re.search(r'<h1[^>]*>([^<]+)</h1>', content)
        if m:
            title = m.group(1).strip()
    if not title:
        title = os.path.splitext(os.path.basename(html_path))[0].replace('-', ' ').title()
    
    # Description
    desc = ""
    m = re.search(r'<meta name="description" content="([^"]+)"', content)
    if m:
        desc = m.group(1)[:160]
    
    # Category: from first blog-card-category or og:type or file path heuristics
    cat = "Technical Guide"
    cat_slug = "design-engineering"
    
    fname = os.path.basename(html_path).lower()
    # Procurement keywords
    if any(kw in fname for kw in ['procurement','quote','supplier','buy','cost','price',
            'blanket','spot','consignment','turnkey','counterfeit','import','nre','incoterms',
            'duty','esd','compliance','inspection','scorecard','negotiation','sourcing']):
        cat = "Procurement Guide"
        cat_slug = "procurement"
    # Manufacturing keywords  
    elif any(kw in fname for kw in ['manufacturing','assembly','solder','reflow','depanel',
            'ipc','microsection','ul-','warpage','testing','process','quick-turn','prototype',
            'wave','selective','stencil','bga','cob','hdi','heavy-copper','flex','rigid',
            'impedance','gerber','via-','surface-finish','lead-free','leaded','trace-width',
            'current-capacity','dfm','dft','first-article','fai','acceptance','microsection',
            'cross-section','laminate','substrate','conformal','copper','lead-time']):
        cat = "Manufacturing Guide"
        cat_slug = "manufacturing"
    # Industry applications
    elif any(kw in fname for kw in ['industry','automotive','medical','agriculture','railway',
            'ev-','energy','data-center','server','robotics','aerospace','audio','surveillance',
            'telecom','5g','consumer','led','iot','charging','storage','semiconductor',
            'defense','marine','smart-']):
        cat = "Industry Application"
        cat_slug = "industry"
    
    # Cover image
    img = ""
    # Try blog-cover pattern first
    m = re.search(r'<img[^>]*src="([^"]*blog-cover[^"]*\.(?:webp|png|jpg))"', content)
    if not m:
        m = re.search(r'<img[^>]*src="([^"]*(?:cover|hero)[^"]*\.(?:webp|png|jpg))"', content)
    if m:
        img = m.group(1)
        # Normalize path: ../generated/ → /generated/
        if img.startswith('../generated/'):
            img = '/generated/' + img[len('../generated/'):]
        if img.startswith('../'):
            img = '/' + img[3:]
    
    # Verify image exists
    if img:
        img_abs = os.path.join(BLOG_DIR, img.lstrip('/'))
        if not os.path.exists(img_abs):
            print(f"  ⚠️  Missing image: {img} (from {os.path.basename(html_path)})", file=sys.stderr)
            img = ""
    
    return {
        'file': os.path.basename(html_path),
        'title': title[:100],
        'desc': desc[:160],
        'cat': cat,
        'cat_slug': cat_slug,
        'img': img
    }


def build_card(article):
    """Build a single blog card HTML using OLD format (matches existing CSS)."""
    img_html = f'<img src="{article["img"]}" alt="{article["title"]}" loading="lazy" class="blog-card-img">' if article['img'] else ''
    date_html = f'<div class="date">{article.get("date", "")} · {article["cat"]}</div>' if article.get('date') else ''
    
    return f'''      <a data-cat="{article['cat_slug']}" href="/blog/{article['file']}" class="blog-card-link">
        <div class="blog-card">
          {img_html}
          <div class="blog-card-body">
            {date_html}
            <h3>{article['title']}</h3>
            <p>{article['desc']}</p>
          </div>
        </div>
      </a>'''


def build_pagination(page, total_pages):
    """Build pagination with First/Prev/numbers/Next/Last, showing 5 pages around current."""
    parts = ['      <nav class="blog-pagination" aria-label="Blog pages">']
    
    # URL helper
    def page_url(p):
        return 'index.html' if p == 0 else f'blog-page-{p+1}.html'
    
    # « First
    if page > 0:
        parts.append(f'        <a href="/blog/{page_url(0)}" class="page-btn page-first" title="First page">«</a>')
    else:
        parts.append(f'        <span class="page-btn page-first disabled">«</span>')
    
    # ← Previous
    if page > 0:
        parts.append(f'        <a href="/blog/{page_url(page-1)}" class="page-btn page-prev" title="Previous page">←</a>')
    else:
        parts.append(f'        <span class="page-btn page-prev disabled">←</span>')
    
    # Page numbers: show pages around current (window of ~7 pages)
    window = 5
    start_page = max(0, page - window)
    end_page = min(total_pages - 1, page + window)
    
    # Adjust window to always show ~11 pages when possible
    if end_page - start_page < 10:
        if start_page == 0:
            end_page = min(total_pages - 1, start_page + 10)
        elif end_page == total_pages - 1:
            start_page = max(0, end_page - 10)
    
    if start_page > 0:
        parts.append(f'        <a href="/blog/{page_url(0)}" class="page-num">1</a>')
        if start_page > 1:
            parts.append(f'        <span class="page-dots">…</span>')
    
    for p in range(start_page, end_page + 1):
        num = p + 1
        if p == page:
            parts.append(f'        <span class="page-num active">{num}</span>')
        else:
            parts.append(f'        <a href="/blog/{page_url(p)}" class="page-num">{num}</a>')
    
    if end_page < total_pages - 1:
        if end_page < total_pages - 2:
            parts.append(f'        <span class="page-dots">…</span>')
        parts.append(f'        <a href="/blog/{page_url(total_pages-1)}" class="page-num">{total_pages}</a>')
    
    # Next →
    if page < total_pages - 1:
        parts.append(f'        <a href="/blog/{page_url(page+1)}" class="page-btn page-next" title="Next page">→</a>')
    else:
        parts.append(f'        <span class="page-btn page-next disabled">→</span>')
    
    # Last »
    if page < total_pages - 1:
        parts.append(f'        <a href="/blog/{page_url(total_pages-1)}" class="page-btn page-last" title="Last page">»</a>')
    else:
        parts.append(f'        <span class="page-btn page-last disabled">»</span>')
    
    parts.append('      </nav>')
    parts.append(f'      <div class="page-position">Page {page+1} of {total_pages}</div>')
    return '\n'.join(parts)


def read_template():
    """Read the blog index template, extracting head and tail."""
    template_path = os.path.join(BLOG_DIR, 'blog', 'index.html')
    if not os.path.exists(template_path):
        # Fallback: read blog-index-template.html
        template_path = os.path.join(BLOG_DIR, 'blog-index-template.html')
    
    if not os.path.exists(template_path):
        print("ERROR: No template found (blog/index.html or blog-index-template.html)", file=sys.stderr)
        sys.exit(1)
    
    with open(template_path) as f:
        orig = f.read()
    
    # Find the blog-grid section to split head/tail
    grid_start = orig.find('<div class="blog-grid')
    if grid_start < 0:
        print("ERROR: No blog-grid div found in template", file=sys.stderr)
        sys.exit(1)
    
    head = orig[:grid_start]
    
    # Find tail (after blog cards, before footer/section-cta)
    # Look for section-cta or footer after the blog-grid area
    tail_start = orig.rfind('<section class="section section-cta"')
    if tail_start < 0:
        tail_start = orig.rfind('<section class="section-cta"')
    if tail_start < 0:
        tail_start = orig.rfind('<footer')
    if tail_start < 0:
        # Last resort: take everything after </section> near the end
        sections = list(re.finditer(r'</section>', orig))
        if len(sections) >= 2:
            tail_start = sections[-2].end()
    
    tail = orig[tail_start:] if tail_start > 0 else ''
    
    # Clean head: remove any existing blog cards between blog-grid and its closing
    head = re.sub(
        r'(<div class="blog-grid[^>]*>).*?(</div>\s*</div>\s*</section>)',
        r'\1\n    <!-- cards injected by generate-blog-index.py -->\n  </div>\n</div>\n</section>',
        head, flags=re.DOTALL
    )
    
    return head, tail


def main():
    parser = argparse.ArgumentParser(description='Generate paginated blog index')
    parser.add_argument('--per-page', type=int, default=PER_PAGE, help=f'Cards per page (default: {PER_PAGE})')
    parser.add_argument('--dry-run', action='store_true', help='Print what would be generated without writing')
    args = parser.parse_args()
    
    per_page = args.per_page
    
    # 1. Scan blog HTML files
    blog_dir = os.path.join(BLOG_DIR, 'blog')
    files = sorted([
        f for f in os.listdir(blog_dir)
        if f.endswith('.html') 
        and f not in ('index.html', 'template.html')
        and not f.startswith('blog-page-')
    ])
    
    print(f"Found {len(files)} blog articles")
    
    # 2. Extract metadata
    articles = []
    for f in files:
        path = os.path.join(blog_dir, f)
        meta = extract_meta(path)
        articles.append(meta)
    
    # Sort by filename (newest first based on naming convention)
    # Most sites name blogs with dates or sequential numbers
    articles.reverse()  # newest first
    
    # 3. Read template
    head, tail = read_template()
    
    # Update article count in filter button
    head = re.sub(r'All\d+', f'All{len(articles)}', head)
    
    # 4. Generate paginated pages
    total_pages = (len(articles) + per_page - 1) // per_page
    
    print(f"Generating {total_pages} pages ({per_page} per page)")
    
    for page in range(total_pages):
        start = page * per_page
        end = start + per_page
        page_articles = articles[start:end]
        
        cards_html = '\n'.join(build_card(a) for a in page_articles)
        pagination = build_pagination(page, total_pages)
        
        page_html = f'''{head.rstrip()}
    <div class="blog-grid reveal">
{cards_html}
    </div>
  </div>
</section>
{pagination}
{tail}'''
        
        filename = 'index.html' if page == 0 else f'blog-page-{page+1}.html'
        filepath = os.path.join(blog_dir, filename)
        
        if args.dry_run:
            print(f"  [DRY RUN] {filename}: {len(page_articles)} cards")
        else:
            with open(filepath, 'w') as f:
                f.write(page_html)
            print(f"  ✓ {filename}: {len(page_articles)} cards")
    
    if not args.dry_run:
        print(f"\nDone! {total_pages} pages, {len(articles)} total cards")
        print("Next: git add blog/index.html blog/blog-page-*.html && git commit && git push")


if __name__ == '__main__':
    main()
