#!/usr/bin/env python3
"""
Add a <link rel="preload" as="image" fetchpriority="high"> to every interior
page's <head> so the LCP hero image starts downloading before the HTML parser
gets to the <img> tag.

Heuristic for "the hero image" of a page:
  - The first `<img>` tag carrying `fetchpriority="high"`. Every article and
    listing template on barranquilla.guide sets this on the hero image only.
  - The src URL is extracted from that tag.

Idempotent. If a `<!-- PERF: hero preload -->` sentinel is already in the
head (or any `rel="preload"` for the same URL), the file is left alone.
The homepage uses its own explicit preload comment (`<!-- PERF: hero preload (homepage) -->`)
and is recognised by the same sentinel match.

Skips pages with no fetchpriority="high" img (404.html, plain page templates).
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

HERO_IMG_RE = re.compile(
    r'<img[^>]*?\bsrc="([^"]+)"[^>]*?\bfetchpriority="high"[^>]*?>'
    r'|<img[^>]*?\bfetchpriority="high"[^>]*?\bsrc="([^"]+)"[^>]*?>',
    re.IGNORECASE,
)
PRELOAD_SENTINEL_RE = re.compile(
    r'<!--\s*PERF:\s*hero preload[^>]*-->',
    re.IGNORECASE,
)
# Where to inject in head, just before the async-fonts comment if present, else before </head>
FONTS_COMMENT_RE = re.compile(r'\s*<!-- PERF: async fonts -->')


def main() -> int:
    touched = 0
    skipped_no_hero = 0
    skipped_already = 0
    for path in ROOT.rglob('*.html'):
        s = str(path)
        if any(x in s for x in ('/.git/', '/node_modules/', '/vendor/')):
            continue
        text = path.read_text(encoding='utf-8')

        if PRELOAD_SENTINEL_RE.search(text):
            skipped_already += 1
            continue

        m = HERO_IMG_RE.search(text)
        if not m:
            skipped_no_hero += 1
            continue
        hero_src = m.group(1) or m.group(2)

        # Build the preload line. Place it after preconnect, before async fonts.
        preload_line = (
            '\n  <!-- PERF: hero preload -->'
            f'\n  <link rel="preload" as="image" href="{hero_src}" fetchpriority="high">'
        )

        fm = FONTS_COMMENT_RE.search(text)
        if fm:
            new = text[:fm.start()] + preload_line + text[fm.start():]
        else:
            # Fall back to inserting right before </head>
            new = text.replace('</head>', preload_line + '\n</head>', 1)

        if new != text:
            path.write_text(new, encoding='utf-8')
            touched += 1

    print(f'Added hero preload to {touched} pages.')
    print(f'  Skipped (already had preload): {skipped_already}')
    print(f'  Skipped (no fetchpriority hero): {skipped_no_hero}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
