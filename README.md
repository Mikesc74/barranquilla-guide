# barranquilla-guide

Static HTML for [barranquilla.guide](https://barranquilla.guide/), served from Cloudflare Pages.

## Deploy

Push to `main` → CF Pages auto-deploys (project `barranquilla-guide-git`, preview URL `barranquilla-guide-git.pages.dev`).

No build step. Files at repo root are served directly.

## Structure

- `index.html` - homepage
- `<slug>/index.html` - posts at `/<slug>/` (mirrors WordPress pretty permalinks, trailing slash)
- `section/<term>/index.html` - section taxonomy archives (live, explore, eat-drink, stay, guides, magazine, neighborhoods)
- `category/<term>/index.html` - category archives (currently just `/category/now/` for weekly roundups)
- `neighborhoods/<slug>/index.html` - individual neighborhood pages (custom post type in WP)
- `<page-slug>/index.html` - standalone pages (about, contact, advertise, privacy-policy, etc.)
- `img/` - all media files
- `css/site.css` - theme CSS (edge-cached, `Cache-Control: max-age=31536000, immutable`)
- `js/main.js` - theme JS (nav toggles, search overlay)
- `_headers` - Cloudflare Pages security + caching headers
- `sitemap.xml` - sitemap (regenerate via `scripts/build_sitemap.py` after content changes)

## Editorial

New post: create `<slug>/index.html` from the template, commit, push. CF deploys in ~30s.

## Contact + newsletter

Forms POST to Formspree `xgopjoao`. Change `<form action=...>` in `contact/index.html` if migrating providers.

## Local setup

After cloning, install the pre-push HTML tag-balance hook:

```bash
ln -sf ../../scripts/git-hooks/pre-push .git/hooks/pre-push
```

The hook runs `scripts/check-tag-balance.py` against any changed `*.html` and blocks the push if it sees unbalanced tags. Added 2026-05-13 after a chatbot strip left a dangling `</div>`.

## Maintenance scripts

Idempotent, run from the repo root:

- `scripts/clean-wp-cruft.py` strips WordPress block-editor cruft (wp-block-*, attachment-*, size-*, data-sizes, etc.) and PEXELS author-workflow comments
- `scripts/remove-ez-toc.py` strips the inline ez-toc TOC block (the sidebar TOC is generated at runtime by `js/main.js`)
- `scripts/perf-fix-hero-preload.py` adds a `<link rel="preload" as="image" fetchpriority="high">` for each page's hero image
- `scripts/perf-fix-fonts.py`, `perf-fix-images.py`, `perf-fix-lazy.py` are the original perf pass scripts
- `scripts/build-search-index.py` regenerates `search-index.json`
- `scripts/delete-unreferenced-images.sh` deletes images under `img/` not referenced anywhere (one-time cleanup)
