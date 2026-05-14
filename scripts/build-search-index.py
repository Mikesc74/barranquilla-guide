#!/usr/bin/env python3
"""
build-search-index.py  —  Builds /search-index.json for barranquilla.guide.

Crawls every index.html in the repo, extracts title / description / section /
body-text snippet, and writes a JSON array to search-index.json at the repo root.

Run from the repo root:
    python3 scripts/build-search-index.py

Re-run any time you publish new content.
"""

import json
import re
from pathlib import Path

REPO_ROOT  = Path(__file__).parent.parent
OUTPUT     = REPO_ROOT / 'search-index.json'
SITE_NAME  = 'Barranquilla Guide'

# Top-level dirs to skip entirely
SKIP_DIRS = {'.git', 'scripts', 'tools', '_scripts', '_shared'}

# Page slugs to omit from the index (utility / legal pages)
SKIP_SLUGS = {
    'privacy-policy', 'affiliate-disclosure', 'advertise',
    'contact', 'about', 'photo-credits', 'city-map',
}


# ── helpers ────────────────────────────────────────────────────────────────────

def strip_tags(html):
    return re.sub(r'<[^>]+>', ' ', html)


def decode_entities(text):
    return (
        text.replace('&amp;',  '&')
            .replace('&lt;',   '<')
            .replace('&gt;',   '>')
            .replace('&#039;', "'")
            .replace('&quot;', '"')
            .replace('&nbsp;', ' ')
            .replace('&hellip;', '...')
            .replace('&mdash;', '-')
            .replace('&ndash;', '-')
    )


def clean(html):
    return re.sub(r'\s+', ' ', decode_entities(strip_tags(html))).strip()


def meta(html, name):
    m = re.search(r'<meta\s+name="' + name + r'"\s+content="([^"]*)"', html)
    return clean(m.group(1)) if m else ''


# ── main ───────────────────────────────────────────────────────────────────────

def build():
    pages = []

    for p in sorted(REPO_ROOT.rglob('index.html')):
        rel   = p.parent.relative_to(REPO_ROOT)
        parts = rel.parts

        # Skip tool/script dirs
        if parts and parts[0] in SKIP_DIRS:
            continue

        # Skip utility slugs (first or last segment)
        if parts and (parts[0] in SKIP_SLUGS or parts[-1] in SKIP_SLUGS):
            continue

        # Skip section archives and category archives (thin pages, not useful in search)
        if parts and parts[0] in {'section', 'category'}:
            continue

        html = p.read_text(encoding='utf-8', errors='ignore')

        # Title — strip " - Barranquilla Guide" suffix
        title = ''
        m = re.search(r'<title[^>]*>(.*?)</title>', html, re.S)
        if m:
            title = clean(m.group(1))
            title = re.sub(
                r'\s*[|\-–,]\s*' + re.escape(SITE_NAME) + r'.*$',
                '', title
            ).strip()
        if not title:
            continue

        description = meta(html, 'description')

        # Section label — first <span class="label"> in the page
        section = ''
        m = re.search(r'<span class="label"[^>]*>(.*?)</span>', html, re.S)
        if m:
            section = clean(m.group(1))

        # Body snippet — first 300 chars of .article-body text
        body = ''
        m = re.search(r'<div class="article-body">(.*?)(?:</div>\s*</article>|</div>\s*</div>)',
                      html, re.S)
        if m:
            body = clean(m.group(1))[:300]

        # URL
        if not parts:
            url = '/'
        else:
            url = '/' + '/'.join(parts) + '/'

        pages.append({
            'url':         url,
            'title':       title,
            'description': description,
            'section':     section,
            'body':        body,
        })

    # Sort: homepage first, then alphabetical by title
    pages.sort(key=lambda x: (x['url'] != '/', x['title'].lower()))

    OUTPUT.write_text(
        json.dumps(pages, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    print(f'Wrote {len(pages)} pages -> {OUTPUT}')
    print('Done. Commit search-index.json alongside the other changes.')


if __name__ == '__main__':
    build()
