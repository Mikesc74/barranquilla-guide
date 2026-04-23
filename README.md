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
