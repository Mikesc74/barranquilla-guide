# barranquilla.guide · Full Audit Report

Date: 2026-05-14
Scope: 107 HTML pages, `/css/site.css`, `/js/main.js`, `/img/` (1,878 files, 343 MB), `_headers`, `_redirects`, build scripts.
Four parallel agents: content/brand/imaging, code/architecture, security, performance.

## TL;DR

The site is in genuinely good shape underneath. The delivery layer is excellent: Cloudflare Pages with brotli + HTTP/2, immutable long-cache headers, a tight CSP, no jQuery or WordPress runtime cruft, vanilla 5.7 KB brotli JS, zero em dashes in shipped HTML, no leaked secrets, no `wp-admin` / `xmlrpc` / `wp-content` artifacts, near-perfect lazy-load coverage, full alt-text coverage.

The fixes cluster in four buckets:

1. **Honesty/accuracy slips that contradict the brand voice** (About page says Mike lives in Barranquilla, homepage claims "thousands" of community members).
2. **Broken function** (21 of 36 city-map markers 404, visa-lead form swallows submissions silently, broken Cloudflare email-protection stubs on /advertise/, 12 pages on stale CSS version).
3. **One single perf lever: images.** 343 MB, 90% JPG, zero WebP siblings, Polish is OFF, 142 MB completely unreferenced.
4. **Defense-in-depth nits** (missing SRI on unpkg Leaflet, CSP gaps that currently block functional embeds, no form honeypot).

Below: ranked punch list with file:line refs.

---

## Critical (fix before next push)

### C1. About page says Mike lives in Barranquilla
`about/index.html:120`. Mike lives in Medellín. The same paragraph claims "every neighborhood profile, restaurant recommendation, and cost breakdown comes from me actually walking the streets", but 15 of 90 article pages are bylined Paulette Romero. Two honesty-rule violations on one page.
Fix: rewrite to acknowledge Medellín base, Santi partnership, and Paulette as a Barranquilla-based contributor.

### C2. Homepage fabricates community size
`index.html:610` says "Join thousands of locals, expats, and visitors sharing tips". Pre-launch, unverifiable. Banned per house style.
Fix: "Join the Barranquilla community on Facebook and WhatsApp." Drop the count claim.

### C3. City Map: 21 of 36 markers (58%) point to dead URLs
`city-map/index.html:200-254`, JS `places` array. The `u:` property on 21 markers references old WP-era slugs that don't exist as static pages. Every tap on the map = 404. Full list in the content-agent report; representative examples: `/best-restaurants-in-barranquilla-2026-where-to-eat-right-now/` → should be `/best-restaurants-barranquilla/`; `/exploring-barranquillas-vibrant-malls/` → `/barranquilla-malls/`; `/things-to-do-in-barranquilla-the-complete-2026-guide/` → `/things-to-do-around-barranquilla/`.
Fix: rewrite the array with current slugs.

### C4. /advertise/ shows literal `[email protected]` (broken Cloudflare email decoder)
`advertise/index.html:154` and `:211`. Cloudflare's email-obfuscation script only runs on cloudflare.com-hosted assets; on Pages it leaves a permanent broken stub. Both the English block and the Spanish (En español) block hit this. No `mailto:` exists anywhere on the site to compensate.
Fix: replace both with a real address (e.g. `hello@barranquilla.guide`) or a `/contact/` link.

### C5. Visa-lead form on `index.html` silently swallows submissions
`index.html` ~lines 205-230. The form has no `action`, the only handler is mangled WP-exported markup: `<script>` wrapped in a `<p>` with literal `<br />` between every line. On submit, JS does `console.log('Visa lead:', data)` then `alert('Thank you! An immigration specialist will contact you within 24 hours.')`. The lead never reaches a server. The alert promises a 24-hour response that will never come.
Fix: either point at Formspree (matching `contact/index.html`), or just delete the box and replace with a CTA link to `/contact/`. Latter is honest given no immigration partner exists.

### C6. `_headers` preloads a stale CSS version
`_headers:21` says `</css/site.css?v=20260424a>; rel=preload`, but `index.html:41` references `?v=20260514a`. The Early Hints preload buys nothing; the browser still re-fetches.
Fix: sync the two, or drop the query string since `/css/*` is `immutable`.

---

## High priority

### H1. 12 pages still reference stale `?v=20260507a` CSS/JS
Files: `whats-happening-in-barranquilla-week-of-may-{4,11}-2026/`, `start-small-business-barranquilla-2026-guide/`, all 7 `section/*/index.html`, `category/now/index.html`. The other 95 pages are on `?v=20260514a`. Next CSS change will partially-deploy.
Fix: `sed -i '' 's/v=20260507a/v=20260514a/g'` across the 12 files.

### H2. Site ships ~1.3 MB of WordPress ez-toc HTML that JS hides
67 of 107 HTML pages contain a fully-rendered `<div id="ez-toc-container">…</div>` block (avg 19 KB/page, max 87 KB on `shipping-household-goods`). `js/main.js:175` literally sets `style.display = 'none'` on it, then injects a custom sidebar TOC.
Fix: write `scripts/remove-ez-toc.py` mirroring the existing `remove-chatbot.py` shape; strip on next pass.

### H3. Two LCP hero images set both `loading="lazy"` and `fetchpriority="high"`
`best-gyms-in-barranquilla/` and `dancing-in-barranquilla-salsa-cumbia-champeta-where-to-learn-2026/`. `loading="lazy"` wins, so the LCP image defers. Inconsistent on two pages, fine on 87.
Fix: change `loading="lazy"` to `loading="eager"` on those two.

### H4. Marketing-speak hits in URLs and visible copy
The shipped HTML is clean of em dashes, but banned phrases remain in user-visible places:

- `exploring-the-enchanting-neighborhoods-of-barranquilla/` slug + H1, referenced from 20 other pages (full list in content report). Rename to `/neighborhoods-of-barranquilla/` or use the existing `/neighborhoods/` index, fix all 20 inbound links.
- "premier" × 2 on city-map (`Kava Rooftop`, `Dann Carlton`).
- "leading cocktail bar" on `best-bars-craft-drinks-barranquilla/index.html:160`.
- "seamless" / "seamlessly" on the city-vs-city, Amazon-shipping, and SIM-card pages.
- "vibrant" in alt text and link labels in `section/live/`, `city-map/`, `best-bars-craft-drinks-barranquilla/`.
- `el-prado-hotel-a-historic-gem-in-the-heart-of-barranquilla/` slug ("gem" + "heart of").
- "easy-to-navigate experience" on `everything-you-need-to-know-about-barranquilla/index.html:293` ("navigate" as metaphor is banned).

### H5. Section listing pages and `neighborhoods/` are missing `<meta name="description">`
9 files: all 7 `section/*/index.html`, `category/now/index.html`, `neighborhoods/index.html`. Google generates its own snippet, but you give up control.

### H6. Missing SRI on `unpkg.com` Leaflet on `/city-map/`
`city-map/index.html:155-156` loads `leaflet@1.9.4/dist/leaflet.css` and `leaflet.js` from unpkg with no `integrity` or `crossorigin`. A successful unpkg supply-chain compromise (precedent: event-stream, ua-parser-js) = full XSS on every city-map visitor.
Fix: self-host Leaflet under `/js/` and `/css/`, then drop `unpkg.com` from the CSP allowlist. (Or compute SRI hashes and add to both tags, pinned to 1.9.4.)

### H7. GetYourGuide widget script is CSP-blocked
`things-to-do-around-barranquilla/index.html:257` and `fun-things-to-do-in-barranquilla-as-a-group/index.html:263` load `widget.getyourguide.com/dist/pa.umd.production.min.js` which is not on the `script-src` allowlist. Functional regression, not a security issue.
Fix: decide if you actually want the widget. If yes, add `widget.getyourguide.com` to `script-src` AND `frame-src`. If no, delete the script + container divs.

### H8. Six neighborhood pages have Google Maps iframes that CSP `frame-src 'self'` blocks
`neighborhoods/{villa-country,ciudad-jardin,el-prado,alto-prado,riomar,puerto-colombia}/index.html:131`. Browser refuses to render.
Fix: add `https://www.google.com` and `https://maps.google.com` to `frame-src`, or replace iframes with static map screenshots that link out.

### H9. Two broken `<img>` srcset variants
`everything-you-need-to-know-about-barranquilla/index.html:254` references `Screenshot-2024-08-07-at-11.07.16 PM-300x246.png` and `-150x123.png` which don't exist on disk. Browser falls back, but the filename-with-spaces is also fragile.
Fix: rename the base file to a slug-friendly name, regenerate variants, or drop srcset.

---

## Performance: the big image story

The single most material lever on this site. Picking either C-perf-1 OR H-perf-1 below cuts most pages' LCP by ~50%.

### C-perf-1. Toggle Cloudflare Polish on (Lossy + WebP)
30-second dashboard click. Requires Pro plan (about COP $100.000/mo). Edge transcodes every JPG/PNG to WebP per request, caches at edge. Site-wide image bytes drop 60-70%. Heaviest interior LCPs (currently 4-5 s) drop to ~2-2.5 s. Closest thing to a single-switch win.

### H-perf-1. Alternative if no Polish: bulk JPG→WebP transcode
1,664 JPG files (305 MB). `cwebp -q 80` over all, emit sibling `.webp`, swap `<img src>` (WebP support is universal since Safari 14). ~213 MB saved on disk, same site-wide LCP win as Polish.

### H-perf-2. Delete 142 MB of unreferenced images
557 of 1,878 files are not referenced from any HTML/CSS/JS/XML/JSON. Notably `Adobe-Express-file.*` set and a `*-section-*.jpg` series from prior tooling.
```bash
cd ~/code/barranquilla-guide
# Get the unreferenced list first, eyeball before deleting
```
Repo goes from 346 MB to ~205 MB. No user-facing change, big DX/clone-speed/deploy win.

### H-perf-3. Add hero `<link rel="preload" as="image">` to every interior page
Currently only the homepage has it. The 106 interior pages set `fetchpriority="high"` on the `<img>` but the head-preload would gate discovery 200-500 ms earlier on slow connections.

### H-perf-4. Replace the 10 worst hero images
`image-13.png` (646 KB) used as LCP on 6+ pages, plus `el-tabor-barranquilla.png` (1.17 MB) and `estadio-edgar-renteria-scaled.jpg` (2560px, 820 KB). Worst offenders move from "Poor" to "Good" CWV.

---

## Medium (technical debt)

### M1. Footer / newsletter CSS classes for removed features
`css/site.css` lines 567-630, 899-925, 878-890, 930-950. Newsletter footer bar (commit `cf8f5ea` stripped the HTML but not the CSS), ad-slot rules (never wired up, comment references `functions.php > bg_ad_slot()` that doesn't exist), 404 styles (no `404.html` exists; `_redirects` sends `/tools/*` to a non-existent `/404.html`), and `.sponsored-badge` / `.sponsored-notice` / `.editorial-pullquote` / `.hero-ctas` / `.nbhd-card-desc` / `.no-posts` are unused.
Fix: either create `404.html` (matches the `_redirects` rule, gives you a branded 404) or remove those rules. Strip the rest. Saves ~200 lines, ~8 KB raw.

### M2. CSP still allowlists `catalina.barranquilla.guide`
`_headers:14`. No HTML references it (Catalina lives at `catalina.medellin.guide`). The subdomain likely doesn't even resolve.
Fix: drop from `script-src` and `connect-src` until you actually embed Catalina here.

### M3. WordPress block classes everywhere
`wp-block-heading` × 565, `wp-block-image` × 138, `wp-block-list` × 74, plus `wp-block-group`, `wp-block-button`, `attachment-*`, `size-*`, `wp-post-image`, `wp-image-N`, `alignwide`, etc. No CSS styles them. Pure WP-export residue.
Fix: one-shot `sed`/Python pass.

### M4. Inline `style="…"` ×2,146 across 107 pages
~20 per page. Mostly WP-block-generated repetitions like `width:100%;height:auto;border-radius:10px;box-shadow:…` on `<img>` and `background:#f0f4f8;border-radius:8px;padding:…` on callout boxes.
Fix: two utility classes (`.article-photo`, `.callout-box`) absorb most of them. Makes site-wide visual changes one-file edits.

### M5. `data-sizes` left over from stripped a3-lazy-load plugin
~100 `<figure class="wp-block-image">` blocks have `data-sizes="(max-width: 1024px) 100vw, 1024px"` instead of `sizes="…"`. Browser ignores `data-sizes`, defaults `sizes` to 100vw, picks the wrong srcset candidate on mobile.
Fix: site-wide `sed 's/ data-sizes="/ sizes="/g'`.

### M6. 109 occurrences of malformed `/ loading="lazy"` attribute order
Self-close slash misplaced inside void element tag. HTML5 parsers tolerate it; linters yell.
Fix: site-wide `sed 's| / loading=| loading=|g'`.

### M7. Gravatar leaks visitor IP + email hash to Automattic on every article page
89 files reference `secure.gravatar.com/avatar/<sha256-of-mike-email>`. Privacy policy doesn't mention it. Also: all three Gravatar hashes (Mike, Paulette, unknown) use `d=mm` fallback so the avatar renders as the WP default silhouette anyway.
Fix: self-host `/img/mike-author-80.jpg` and `/img/paulette-author-80.jpg`, sed-replace the gravatar refs. Removes a third-party request, fixes the silhouette issue, closes the privacy gap.

### M8. `.DS_Store` is tracked at repo root
43 KB Finder dropping.
```bash
echo '.DS_Store' >> .gitignore && git rm --cached .DS_Store
```

### M9. Sitemap missing the latest weekly roundup
`whats-happening-in-barranquilla-week-of-may-11-2026/index.html` was added after `sitemap.xml` was regenerated (2026-05-08).
Fix: run `scripts/build_sitemap.py` after weekly-roundup commits, or wire into the pre-push hook.

### M10. Forms have no honeypot
`contact/index.html:117` and `:155` both post to `formspree.io/f/xgopjoao` with no `_gotcha` field. Risk is Formspree quota burn, not data exposure. Both contact and newsletter share one endpoint, so when one gets sniffed, both flood.
Fix: add `<input type="text" name="_gotcha" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px;">` to both forms. Consider splitting endpoints.

### M11. 71 HTML files contain leftover `<!-- PEXELS_GENERIC_PLACEHOLDER -->` / `<!-- PEXELS_SECTION_IMAGE -->` comments
Author-workflow markers. Don't render but bloat HTML.

### M12. 13 pages with heading-hierarchy skips (h1 → h3 before h2)
The WP-block tour-CTA pattern: `<h1>title</h1>` → CTA box with `<h3>title</h3>` → article `<h2>`. Minor a11y issue.
Fix: change CTA-box `<h3>` to `<p class="cta-title">` and style it.

### M13. 17 `alt=""` on neighborhood pages that look content-bearing
`neighborhoods/{villa-country,ciudad-jardin,el-prado,alto-prado,riomar,puerto-colombia}/index.html`. Empty alt is fine for decorative; these look like real photos.

### M14. Two `<img>` missing width/height (CLS risk)
`fun-things-to-do-in-barranquilla-as-a-group/` and `barranquilla-malls/index.html:138` (the latter also has malformed `/ loading=`).

### M15. Author/byline inconsistency
75 pages bylined "Mike Chartrand", 15 bylined "Paulette Romero". No `/author/paulette-romero/` page. About page contradicts the bylines (per C1).
Fix: add Paulette to About, or unify all bylines.

---

## Low / nice-to-have

- Section "now" `_redirects` rule points at a non-existent `section/now/index.html`.
- CSS has 4 `!important` flags; one is a redundant `<style>` hack on `index.html:483` for `.now-grid`. Move to `site.css`, delete the inline `<style>`.
- WP theme header comment still at top of `site.css`.
- Site `lang="en"` declared site-wide; advertise page's Spanish block should be wrapped in `<section lang="es">`.
- Title tag on `dental-work-in-barranquilla-costs-quality-medical-tourism-2026-guide/` is 91 chars (truncated in SERPs).
- Consider self-hosting the 4 actually-used Google Font weights (currently loading 12 variants from gstatic). Saves a DNS handshake and ~100-300 KB.
- Cloudflare Pages Auto Minify on `site.css` would shave another ~15 KB cold.
- Schema.org Organization on homepage lacks `address` / `contactPoint`. Add Norte Sur Consulting NIT 901.956.771-1 + Colombia address.
- `pre-push` hook (`scripts/git-hooks/pre-push`) is excellent. Document the symlink command in README so future contributors install it.
- `tools/social-publisher/posted_history.json` is 18 bytes, publisher hasn't run yet. Either run it or note as WIP.

---

## What came back clean (informational)

- **Zero em dashes** in shipped HTML/CSS/JS. (6 in `scripts/*.py`, not user-visible.)
- **Zero secrets** in the deployable surface. `tools/social-publisher/publisher.py` reads `ANTHROPIC_API_KEY` from env; `.gitignore` correctly excludes `.env` and `config.json`.
- **No WordPress runtime cruft**: no `xmlrpc.php`, `wp-admin/`, `wp-json/`, `wp-content/`, `readme.html`, `license.txt`, `<meta name="generator">`, `wp-emoji`, `_wpemojiSettings`, `oembed`, `rank-math`, `yoast`. Rare for a WP export.
- **No jQuery, no jetpack, no wp-embed.** Vanilla JS, 5.7 KB brotli.
- **All 1,088 `<img>` tags have alt attributes.** 991 have `loading="lazy"`. 88 have `loading="eager"` (heroes). 90 have `fetchpriority`.
- **All forms** point at Formspree (or the newsletter Worker), none at `admin-post.php`.
- **Zero broken `<img src>`** out of 1,088 references. Zero broken internal `<a href>` paths in HTML.
- **`_headers` security posture is tight**: HSTS preload, frame-ancestors none, X-Frame-Options DENY, granular `form-action`, `connect-src`, COOP same-origin, Permissions-Policy locked down. Only gaps are SRI + the catalina/GYG allowances above.
- **GA4 only** for analytics. No GTM container, no Facebook Pixel, no Hotjar, no FullStory.
- **No mixed content** in subresources (4 http:// links exist in body anchor `href`, auto-upgraded by CSP `upgrade-insecure-requests`).
- **HTTP/2 + brotli** on all responses. `/css/` and `/img/` cache HIT with `immutable`. Homepage 9.5 KB over the wire. CWV-friendly delivery layer.
- **Personal data hygiene clean**: `mike@mikec.pro` does not appear in public HTML, neither do Santi's or Catalina's phone numbers, nor Deirdre's name. The only emails in body copy are instructional placeholders.

---

## Recommended sequence

Same-day, 1-2 hours total:
1. C1 (About page rewrite)
2. C2 (homepage community line)
3. C5 (delete or repair visa form)
4. C6 + H1 (cache-bust version sync, sed)
5. C4 (replace email-protected stubs on /advertise/)
6. H3 (lazy-LCP on 2 pages)

Same-day if Polish is acceptable:
7. C-perf-1 (Cloudflare Polish toggle)

Next session, 2-4 hours:
8. C3 (rewrite city-map JS array)
9. H2 (strip ez-toc HTML site-wide; new `scripts/remove-ez-toc.py`)
10. H4 (marketing-speak: rename `enchanting-neighborhoods` slug + 20 inbound links, fix premier/leading/seamless hits)
11. H-perf-2 (delete 142 MB unreferenced images)
12. H-perf-3 (add hero preload to interior pages)
13. H6 (self-host Leaflet or add SRI)
14. H7 (decide on GetYourGuide widget)
15. H8 (fix Google Maps iframe CSP, or replace with screenshots)

Backlog (medium / nice-to-have): M1 through M15 and the low items. Batch over a long weekend with mechanical `sed` passes.
