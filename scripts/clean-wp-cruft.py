#!/usr/bin/env python3
"""
Strip leftover WordPress-export cruft from every HTML page in the repo.

Removes, in this order:
  1. PEXELS_GENERIC_PLACEHOLDER / PEXELS_SECTION_IMAGE author-workflow
     HTML comments (never rendered, just bloat).
  2. WordPress block-editor class names from `class="…"` attributes:
     wp-block-*, wp-image-NNN, attachment-*, size-*, wp-post-image,
     wp-element-*, alignwide, aligncenter, alignleft, alignright,
     is-resized (the latter is unused by site CSS; is-active / is-loaded /
     is-open / is-hidden-lazy are kept because JS toggles them at runtime).
  3. Stale `data-sizes="…"` attributes left by the a3-lazy-load plugin
     (loader was removed; the value should just live on `sizes=`).
  4. Malformed `/ loading="lazy"` attribute order, where the void-element
     self-close slash got placed before another attribute. The slash
     should follow the last attribute, not interleave them.

Idempotent. Safe to re-run.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 1. PEXELS author-workflow comments
PEXELS_RE = re.compile(
    r'\s*<!--\s*PEXELS_(?:GENERIC_PLACEHOLDER|SECTION_IMAGE)\s*-->'
)

# 2. WordPress block-editor classes (all confirmed unstyled in css/site.css
# and unreferenced in js/*.js). Removed token-by-token from class attributes.
WP_CLASS_EXACT = {
    'wp-block-heading',
    'wp-block-image',
    'wp-block-list',
    'wp-block-group',
    'wp-block-group-is-layout-flow',
    'wp-block-button',
    'wp-block-buttons',
    'wp-block-buttons-is-layout-flex',
    'wp-block-gallery',
    'wp-block-separator',
    'wp-block-quote',
    'wp-block-pullquote',
    'wp-block-spacer',
    'wp-block-columns',
    'wp-block-column',
    'wp-element-caption',
    'wp-element-button',
    'wp-post-image',
    'attachment-bg-article-card',
    'attachment-bg-hero',
    'attachment-full',
    'attachment-large',
    'attachment-medium',
    'attachment-thumbnail',
    'size-bg-article-card',
    'size-bg-hero',
    'size-full',
    'size-large',
    'size-medium',
    'size-thumbnail',
    'alignwide',
    'alignfull',
    'aligncenter',
    'alignleft',
    'alignright',
    'is-resized',
    'has-alpha-channel-opacity',
}
# Patterns (regex) that match auto-generated tokens to drop
WP_CLASS_PATTERNS = [
    re.compile(r'^wp-image-\d+$'),
]

CLASS_ATTR_RE = re.compile(r'class="([^"]*)"')


def _clean_class(match: re.Match) -> str:
    classes = match.group(1).split()
    kept = []
    for c in classes:
        if c in WP_CLASS_EXACT:
            continue
        if any(p.match(c) for p in WP_CLASS_PATTERNS):
            continue
        kept.append(c)
    if not kept:
        return ''  # drop class="" entirely
    return f'class="{" ".join(kept)}"'


# 3. data-sizes → sizes
DATA_SIZES_RE = re.compile(r' data-sizes="')

# 4. ` / loading="x"` → ` loading="x"` (the slash belongs at the end of the tag, not mid-attrs)
LOADING_SLASH_RE = re.compile(r' / loading=')


def main() -> int:
    touched = 0
    pexels_removed = 0
    classes_pruned = 0
    sizes_renamed = 0
    loading_fixed = 0
    for path in ROOT.rglob('*.html'):
        s = str(path)
        if '/node_modules/' in s or '/vendor/' in s:
            continue
        text = path.read_text(encoding='utf-8')
        orig = text

        new = text
        # 1. PEXELS comments
        before = len(new)
        new = PEXELS_RE.sub('', new)
        pexels_removed += (before - len(new)) // 30  # rough comment-instance count

        # 2. WP classes
        def _track(m):
            cleaned = _clean_class(m)
            return cleaned
        new = CLASS_ATTR_RE.sub(_track, new)
        # Also clean up double-spaces inside any remaining class= attributes
        # that resulted from removing middle tokens, and trim ` class="" ` artifacts.
        new = re.sub(r' class="\s*"', '', new)
        def _normalize_ws(m):
            inner = re.sub(r'\s+', ' ', m.group(1).strip())
            return 'class="' + inner + '"' if inner else ''
        new = re.sub(r'class="([^"]*)"', _normalize_ws, new)
        # Clean up orphan whitespace where a class= attribute was the only
        # attribute on the tag (e.g. `<h2 >` left after `<h2 class="wp-block-heading">`
        # got stripped). Match tags with leftover spaces before > or />.
        new = re.sub(r'<(\w+)\s+>', r'<\1>', new)
        new = re.sub(r'<(\w+)\s+/>', r'<\1/>', new)
        # Also collapse multiple spaces left between attributes
        new = re.sub(r'(<\w+[^>]*?)  +', r'\1 ', new)

        # 3. data-sizes → sizes
        before = len(re.findall(DATA_SIZES_RE, new))
        new = DATA_SIZES_RE.sub(' sizes="', new)
        sizes_renamed += before

        # 4. ` / loading=` → ` loading=`
        before = len(re.findall(LOADING_SLASH_RE, new))
        new = LOADING_SLASH_RE.sub(' loading=', new)
        loading_fixed += before

        if new != orig:
            path.write_text(new, encoding='utf-8')
            touched += 1
            classes_pruned += orig.count('class=') - new.count('class=')

    print(f'Cleaned {touched} HTML files.')
    print(f'  PEXELS comments removed: {pexels_removed}')
    print(f'  class="" attrs eliminated: {classes_pruned}')
    print(f'  data-sizes renamed:        {sizes_renamed}')
    print(f'  loading= slashes fixed:    {loading_fixed}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
