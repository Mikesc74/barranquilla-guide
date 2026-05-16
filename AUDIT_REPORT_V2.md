# barranquilla.guide · Re-Audit Delta Report

Date: 2026-05-15 (run after the C, H, M, Low, and Perf batches landed)
Method: same four parallel agents as original audit, briefed on what was supposedly fixed, told to verify + flag regressions + flag new issues.

## TL;DR

**Most previous fixes held.** Em dashes zero, slug renames clean, CSP tightened correctly, Leaflet vendored, fonts self-hosted, ez-toc gone, hero preloads in, WebP transcode clean, contact-form honeypot in place, alt text on neighborhood pages, all 21 city-map broken markers fixed, About page correct on Medellín, sitemap current.

**Three things didn't fully land + one new critical:**

1. **CRITICAL (new):** `AUDIT_REPORT.md`, `CLAUDE.md`, `README.md`, `/scripts/*`, `img-unref*.txt` are all deployed to the public site. `barranquilla.guide/CLAUDE.md` and `barranquilla.guide/AUDIT_REPORT.md` are reachable URLs. They contain internal docs, past CSP weaknesses, PII (`mike@mikec.pro`, Deirdre's name), and the full toolchain. Fix is one rule in `_redirects`.

2. **HIGH:** Newsletter form on 107 pages has no `_gotcha` honeypot. Only the two Formspree forms in `/contact/` got it. The newsletter form posting to `newsletter.colguides.com/subscribe` is unguarded everywhere.

3. **HIGH:** `_headers` is missing cache rules for `/fonts/*` and `/vendor/*`. Both fall to default 4-hour TTL instead of the immutable 1-year on `/css/`, `/js/`, `/img/`. Repeat visitors revalidate fonts every 4 hours for no reason.

4. **MEDIUM:** The utility-class refactor only half-landed. `.article-photo`, `.fig-meta`, `.info-box`, `.cta-title` are in use. `.content-narrow`, `.content-narrow--end`, `.related-section`, `.related-grid-3` are defined but never used in HTML (the inline-style swap step never ran for those 4 patterns). 1,302 inline `style=` attrs remain (audit said 565 were swapped; 4 of 8 utility-class swaps actually shipped).

## What's verified clean (the fixes that held)

Content/brand:
- About page correct on Medellín, Paulette credited.
- Homepage no "thousands" community claim.
- All 21 city-map markers point at real slugs.
- /advertise/ broken email stubs replaced with /contact/ links.
- Visa form on /barranquilla-guide/ gone, replaced with CTA.
- Both slug renames (enchanting-neighborhoods, el-prado-hotel-gem) clean: URLs, H1, title, meta, 301 redirects, sitemap, search-index all consistent.
- Zero em dashes anywhere.
- Zero "premier", "enchanting", "leading cocktail", "world-class", "seamless".
- Author bylines: 89 articles using `/img/team/mike.svg` or `/img/team/paulette.svg`, zero Gravatar refs.
- 9 listing pages all have non-empty meta descriptions.
- 6 neighborhood pages: zero `alt=""` (50 images, all described).
- /advertise/ Spanish section wrapped in `<section lang="es">`.
- Sitemap has 107 URLs including may-11 weekly + both renamed slugs.

Code/security:
- CSP: dropped unpkg, catalina, fonts.googleapis.com, fonts.gstatic.com. Kept gtag, GA, cloudflareinsights. Added widget.getyourguide.com, google.com, maps.google.com.
- Leaflet 1.9.4 self-hosted at /vendor/leaflet/1.9.4/, zero unpkg refs.
- 6 Google Maps iframes have real src + sandbox attr + matching CSP frame-src.
- 18 woff2 fonts under /fonts/, @font-face block at top of site.css, zero gstatic refs in HTML.
- /404.html exists, uses error-404 styles.
- New build scripts present + executable (clean-wp-cruft, remove-ez-toc, perf-fix-hero-preload, transcode-webp, fetch-fonts, delete-unreferenced-images).
- README documents pre-push hook + scripts.
- Zero PII in public HTML (mike@mikec.pro, Santi/Catalina phones, Deirdre absent).
- Zero WordPress runtime artifacts.

Performance:
- Image folder: 343 MB → 298 MB (-45 MB).
- 809 WebP siblings created. Zero missed swaps on hero images (all referenced JPGs/PNGs with smaller WebP siblings have been swapped in HTML).
- All 1,085 `<img>` tags have width + height attrs (CLS clean).
- 89 interior pages have hero preload.
- ez-toc dead-strip held (zero `<div id="ez-toc-container">` left).
- All 108 HTML pages reference `site.css?v=20260515a`.
- Predicted LCP: average interior page 3.8-4.5s → 1.6-2.0s (2-2.5s shaved off).
- CSS still ~8 KB brotli on the wire.

## Things that didn't fully land

### CRITICAL · Internal docs servable at public URLs

After deploy, these will be reachable:
- `https://barranquilla.guide/AUDIT_REPORT.md` (18 KB · contains a documented history of past CSP weaknesses and the full architecture)
- `https://barranquilla.guide/CLAUDE.md` (47 KB · contains `mike@mikec.pro`, "Deirdre", internal infra, build conventions, deployment commands, master-portal architecture)
- `https://barranquilla.guide/README.md` (lower sensitivity)
- `https://barranquilla.guide/scripts/clean-wp-cruft.py` and 16 other build scripts (recon value, no secrets)
- `https://barranquilla.guide/img-unref.txt` and `img-unref-list.txt` (33 KB each, junk listings)

Fix: add to `_redirects`

```
/AUDIT_REPORT.md /404.html 404
/AUDIT_REPORT_V2.md /404.html 404
/CLAUDE.md /404.html 404
/README.md /404.html 404
/scripts/* /404.html 404
/img-unref.txt /404.html 404
/img-unref-list.txt /404.html 404
/fonts/google-fonts.css /404.html 404
/fonts/_faces.json /404.html 404
```

### HIGH · Newsletter form lacks honeypot on 107 pages

`<form class="newsletter-form" data-city="barranquilla" action="https://newsletter.colguides.com/subscribe" method="post">` appears on every page (footer prefoot). Zero of them have `_gotcha`. Fix is one find-replace adding the input across all 107 occurrences.

### HIGH · `/fonts/*` and `/vendor/*` not in immutable cache

Live verification:
```
/fonts/inter-400-latin.woff2 → cache-control: public, max-age=14400, must-revalidate
/vendor/leaflet/1.9.4/leaflet.js → cache-control: public, max-age=14400, must-revalidate
```
Both should be `max-age=31536000, immutable` like /css/, /js/, /img/. Fix is six lines in `_headers`.

### MEDIUM · Utility-class refactor half-landed

CSS rules defined but zero HTML uses:
- `.content-narrow` · 88 pages still ship `style="max-width:740px;margin:0 auto;padding:0 32px;"`
- `.content-narrow--end` · 88 pages still ship the same with `padding:0 32px 40px;`
- `.related-section` · 65 pages still ship `style="padding-top:0;border-top:1px solid var(--light-gray);"`
- `.related-grid-3` · 65 pages still ship `style="grid-template-columns:repeat(3,1fr);"`

Plus the HTML uses `.related-posts-section` (plural) in 5 files where CSS rule is `.related-section`. Either rename one or the other.

Total still-inline `style=` attrs: 1,302 site-wide.

### MEDIUM · WP block-editor cruft survives in 11 files

`clean-wp-cruft.py` missed BEM-modifier variants. Still in HTML:
- `wp-block-group__inner-container`, `wp-block-button__link`, `wp-block-gallery-is-layout-flex`, `wp-block-gallery-1`
- `is-layout-flow` (10×), `is-layout-flex` (6×), `is-style-outline` (1×), `is-cropped` (1×)
- `has-vivid-red-background-color` (4×), `has-white-color` (4×), `has-text-color` (4×), `has-background` (8×)
- `has-nested-images` (1×), `columns-default` (1×)

Files: `whats-happening-in-barranquilla-week-of-{april-6,april-13,april-20,april-27,may-4,may-11}-2026/`, `pets-mascotas-barranquilla-2026/`, `barranquilla-wedding-guide-2026/`, `expat-networking.../`, `barranquilla-with-kids-family-guide-2026/`, `nautical-sports-center-salinas/`.

The `has-*-color` and `has-background` classes are not defined in `css/site.css`, so the join-Facebook / join-WhatsApp CTAs in those 11 files render with browser-default button styling rather than the intended brand styling. Worth verifying in browser whether they look broken.

### MEDIUM · Marketing-speak survivors

"vibrant" still in body copy:
- `where-to-stay-in-barranquilla/index.html:152` "not as vibrant as El Prado for nightlife"
- `best-bars-craft-drinks-barranquilla/index.html:229` "A vibrant, authentically Barranquillero bar"
- `study-spanish-in-barranquilla/index.html:118` "vibrant Latin American city"
- 2 in HTML build-instruction comments (not user-visible but bloat)

"navigate" as metaphor:
- `index.html:377` "understand the city, not just navigate it"
- `neighborhoods/villa-country/index.html:200` "without having to navigate Barranquilla's sprawl"
- `neighborhoods/riomar/index.html:235` "navigate the city on foot"

"gem":
- `the-best-fine-dining-restaurants-in-barranquilla/index.html:121` "Manuel is a culinary gem"
- `city-map/index.html:218` El Celler popup "a fine dining gem in northern Barranquilla"

"world-famous":
- `san-basilio-de-palenque/index.html:244` "world-famous for mixing up"
- `city-map/index.html:241` "world-famous Barranquilla Carnival"

### MEDIUM · og:image:type mismatch on renamed pages

`barranquilla-neighborhoods/index.html:18` says `<meta content="image/jpeg" property="og:image:type"/>` but lines 16-17 point at `.webp`. Same on `el-prado-hotel/`. Facebook debugger flags this. One sed fix.

### LOW · One LCP still on JPG instead of WebP

`popular-sports-in-barranquilla/index.html:32,97` preloads + heroes `estadio-edgar-renteria-scaled.jpg` (820 KB) even though `estadio-edgar-renteria-scaled.webp` exists. This was the one case where my round-1 swap was reverted because the WebP came out 7% larger. A resize+retranscode would fix it but requires deleting the existing webp file (sandbox can't, Mike can).

### LOW · `best-coworking-spaces-barranquilla/index.html:97` hero is JPG with no WebP sibling

The hero is `coworking-barranquilla-1.jpg` at 1,200px. No WebP exists on disk. Transcode-webp.py would create one if rerun.

### LOW · Filename with literal space

`/img/Screenshot-2024-08-07-at-11.07.16 PM.webp` (narrow no-break space inside filename). Works because browsers URL-encode it, but fragile. Suggest rename to a slug-safe filename.

### LOW · 204 MB orphan images still on disk

The `delete-unreferenced-images.sh` script ready since the previous round still hasn't been run. The orphan set grew because round-2 created 681 new WebP siblings while the originals stayed.

### LOW · Other cosmetic items

- Missing newline before `<link rel="stylesheet">` after the second font preload on every page (linter / parser doesn't care; future-diff noise).
- `colombian-citizenship-exam-study-guide/index.html` is 152 KB (just long content, but might benefit from a content-skim or per-page-split).
- Generic 1-word alts on many neighborhood images (`alt="Villa Country"`). Not a regression, but worth a future pass for richer descriptions.

## Priority fix sequence

1. **5-minute fix, ship immediately**: `_redirects` rules to 404 the markdown + scripts + working artifacts. Closes the critical exposure.
2. **5-minute fix**: 2 lines in `_headers` to add `/fonts/*` and `/vendor/*` immutable cache.
3. **20-minute fix**: newsletter-form honeypot site-wide (one find-replace) + finish the 4 utility-class swaps + og:image:type sed.
4. **Backlog**: marketing-speak prose touch-ups, WP-cruft strip v2 (BEM patterns), popular-sports LCP webp regen, image-folder cleanup.

Net assessment: the audit fixes mostly stuck, the site is in much better shape than the original baseline, and the only urgent item is the internal-docs exposure.
