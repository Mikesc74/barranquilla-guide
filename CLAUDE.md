# barranquilla.guide, orientation for Claude

This file is the fast path for any future Claude session working on this repo.
Read it first. Update the **Recent changes** log at the bottom every time you
hand files off for a commit. Keep the rest of the file current as the site
evolves.

---

## What this is

A static HTML site, originally exported from WordPress. No build step, no
framework, no CMS, files at the repo root are served directly.

- **Host**: Cloudflare Pages, project `barranquilla-guide-git`.
- **CF account**: NSC Account (`c98561adefb602704d4e7a6a1b7e7597`).
- **Domain**: https://barranquilla.guide/ (also `www.barranquilla.guide`).
- **Preview URL**: https://barranquilla-guide-git.pages.dev/
- **Deploy**: push to `main` on `Mikesc74/barranquilla-guide` → Cloudflare
  Pages auto-deploys in ~30 seconds.
- **Rollback parachute**: the old WordPress origin on Namecheap is still
  running but no DNS points at it. Don't touch it. Rollbacks are a one-click
  operation in the CF Pages dashboard (Deployments → "Rollback to this
  deployment").
- **Style reference**: medellin.guide, we try to match that clean, editorial
  look. Different repo shape (see **Sister site** below), don't copy
  patterns blindly.

---

## Repo layout

```
/                        index.html, sitemap.xml, robots.txt, _headers,
                         site.webmanifest, README.md, CLAUDE.md
/css/site.css            The one stylesheet, shared by every page
/js/main.js              The one script, nav, search, mobile menu,
                         newsletter form, auto-TOC
/img/                    All media (WordPress-exported filenames, many size
                         variants), referenced as /img/<basename>
/{slug}/index.html       One folder per post/page. ~87 of them.
/section/{slug}/         Section archives: live, explore, eat-drink, stay,
                         guides, magazine, neighborhoods
/category/now/           "Latest News" archive (weekly roundups)
/neighborhoods/{slug}/   Individual neighborhood pages
/scripts/                Utility scripts (currently just fix-og-images.py)
/tools/social-publisher  Unrelated helper, leave alone unless asked
```

Each HTML file has the full nav and footer inlined. Global changes (nav,
footer, script tags, CSP) have to be fanned out with `sed` across all HTML
files, or applied in `_headers`.

---

## Page template

### Page chrome (identical on every page)

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="theme-color" content="#1B2A47" />
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" />
  <meta name="description" content="..." />
  <link rel="canonical" href="https://barranquilla.guide/<slug>/" />

  <!-- Full OG + Twitter card block, see "Open Graph image metadata" below -->
  <!-- article:published_time + article:modified_time on posts -->

  <title>...</title>

  <link rel="icon" href="/img/favicon-32.jpg" sizes="32x32" />
  <link rel="icon" href="/img/favicon-192.jpg" sizes="192x192" />
  <link rel="apple-touch-icon" href="/img/favicon-180.jpg" />
  <link rel="manifest" href="/site.webmanifest" />

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Inter:wght@300;400;500;600&display=swap" />
  <link rel="stylesheet" href="/css/site.css?v=YYYYMMDDx" />

  <!-- GA4 gtag.js, measurement id G-FKFW8ZQJPN -->
</head>
<body>
<nav class="site-nav site-nav--solid" id="site-nav">...</nav>
<div class="mobile-nav" id="mobile-nav">...</div>
<div class="search-overlay" id="search-overlay">...</div>
```

The homepage uses `site-nav--transparent` on load (hero is dark enough to
read white text) and swaps to `site-nav--solid` on scroll. Interior pages are
always `site-nav--solid`.

### Single-post body

```html
<article class="single-article">
  <div class="article-hero">
    <div class="article-hero-image">
      <img width="W" height="H" src="/img/..." loading="eager" fetchpriority="high" ... />
    </div>
  </div>
  <header class="article-header">
    <span class="label">Guides</span>
    <h1>...</h1>
    <div class="article-header-meta">...author, date...</div>
  </header>
  <div class="article-body">
    <!-- Just H2/H3/P/blockquote/img, js/main.js auto-builds the sidebar TOC -->
    <h2 id="slug">Section heading</h2>
    <p>...</p>
    ...
  </div>
</article>
<!-- site-footer, chatbase-position-fix <style>, Chatbase init <script> -->
```

H2 headings carry `id` attributes already (legacy from WordPress). The
sidebar TOC relies on those ids; if an H2 has no id, `js/main.js`
auto-slugifies one.

---

## Brand colors & typography

From `css/site.css` design tokens:

- `--navy: #1B2A47`, primary text, nav on scroll, footer background.
- `--coral: #E8533A`, accent, CTA, active links, category labels, link
  color inside article body. **Coral is the headline accent on
  barranquilla.guide, not gold.**
- `--gold: #C9963A`, reserved for sponsored-content badges only.
- `--light-gray: #F4F4F2`, featured-guides and email-capture backgrounds.
- `--mid-gray: #D0D0CE`, `--dark-gray: #555555`, `--white: #FFFFFF`,
  `--black: #111111`.
- Fonts: `Playfair Display` (serif, headings) + `Inter` (sans, body) via
  Google Fonts.
- `--max-width: 1280px`, `--nav-height: 64px`.

---

## Key runtime features (globally applied)

### 1. Sticky sidebar Table of Contents

Implemented entirely in `css/site.css` and `js/main.js`, no per-guide HTML
edits required.

- `buildArticleToc()` in `main.js` finds every `h2`/`h3` inside
  `.article-body`, wraps the body + a generated `<aside class="article-toc">`
  in a grid layout, and hides any legacy `.toc` / `#ez-toc-container` block.
- Activates only if there are **≥3 H2s** in the article.
- Active section is tracked by a scroll listener that picks the heading
  closest above a fixed reading line (~140px from the top of the viewport).
- Under 1024px viewport, the grid collapses to single column and the TOC
  renders as a compact collapsible `<details>` panel above the body.

If you change the guide template in a way that renames `.article-body` or
`.single-article`, update the selectors in `buildArticleToc()` or the TOC
will silently stop appearing.

### 2. Nav / mobile menu / newsletter form

All in `js/main.js`. The newsletter form currently posts to a WordPress AJAX
endpoint (`bgData.ajaxUrl`) that is legacy from the WordPress origin, audit
before relying on it. The live newsletter pipeline is Formspree (see below).

There is **no on-site search**. The WordPress search endpoint was dropped
in the port, and on 2026-04-23 the magnifying-glass icon and full-screen
`search-overlay` sheet were removed entirely. Discovery on this site is
Chatbase (primary) + the hero "reading paths" (Planning a visit? / Thinking
of moving? / Already living here?) + in-body links.

### 3. Chatbase chatbot (primary discovery path)

Bot id `wv8hNpU46aEhF0eXDOVF4`. Loaded at the end of `<body>` via an inline
bootstrap script. A `<style id="chatbase-position-fix">` block just above it
tunes the bubble placement to sit above the sticky "Moving here?" CTA bar.
**Don't edit those coords casually, they're tuned.** CSP permits
`https://www.chatbase.co` in `script-src`, `connect-src`, and `frame-src`.

The homepage hero includes a `.hero-chat-cta` block with copy
("Got a question about Barranquilla? Ask our AI guide, fastest way to find
what you need.") and an "Ask the guide" button. The button calls
`window.chatbase('open')` via an inline `onclick` to trigger the widget
,  the Chatbase proxy queues the call until the embed script loads, so it
works even on first paint before the embed has loaded.

---

## Third-party chrome (IDs and endpoints)

- **Google Fonts**: `Playfair Display` + `Inter` via `fonts.googleapis.com`
  (preconnected).
- **GA4** measurement id `G-FKFW8ZQJPN` via `gtag.js` in `<head>`. No cookie
  consent gate currently; if you add one, mirror medellin.guide's
  `consent.js` pattern.
- **Chatbase** bot id `wv8hNpU46aEhF0eXDOVF4` (see above).
- **Formspree** endpoint `xgopjoao` handles the contact form and newsletter
  signups. Newsletter uses a hidden field `subject=newsletter-subscribe` so
  submissions can be filtered in the Formspree inbox.
- **Leaflet 1.9.4 from unpkg**, only loaded on `/city-map/`, not globally.

---

## Cloudflare Pages caching, IMPORTANT

`_headers` marks `/css/*`, `/js/*`, and `/img/*` with:

```
Cache-Control: public, max-age=31536000, immutable
```

One-year immutable cache. **Browsers and CF's edge will NOT re-fetch these
files.** If you edit `css/site.css` or `js/main.js`, you MUST also bump the
`?v=...` cache-buster on every `<link>` and `<script>` reference across the
~100 HTML files. Otherwise your changes will not reach visitors.

Quick bump (use a new version string each time, date-based, with a letter
suffix for intra-day bumps):

```bash
OLD=20260423b
NEW=20260424a
find . -name '*.html' -not -path './.git/*' -print0 \
  | xargs -0 sed -i '' "s/?v=${OLD}/?v=${NEW}/g"
grep -c "?v=${NEW}" visas-colombia-barranquilla/index.html   # expect 2
```

On Linux drop the empty `''` after `-i`.

HTML is `max-age=600, must-revalidate`, so content-only edits propagate
within 10 minutes without any cache-busting.

Current version in use: **`20260424a`** (update this line when you bump).

---

## `_headers`, security headers and CSP

`_headers` at the repo root sets HSTS, X-Frame-Options, X-Content-Type-Options,
Referrer-Policy, Permissions-Policy, Cross-Origin-Opener-Policy, and the full
CSP. Every path is covered by `/*`.

**Current CSP allow-list (don't drop any of these):**

- `script-src`: `'self' 'unsafe-inline' www.googletagmanager.com
  www.google-analytics.com www.chatbase.co unpkg.com
  static.cloudflareinsights.com`
- `style-src`: `'self' 'unsafe-inline' fonts.googleapis.com unpkg.com`
- `font-src`: `'self' fonts.gstatic.com data:`
- `img-src`: `'self' data: https:`
- `connect-src`: `'self' formspree.io *.google-analytics.com
  analytics.google.com www.chatbase.co`
- `frame-src`: `www.chatbase.co`
- `form-action`: `'self' https://formspree.io`

**If you add a new third-party script or fetch target, update `_headers`
first and deploy it, THEN add the script tag.** Otherwise the browser blocks
the request silently and the feature appears broken.

---

## How to work in this repo (deploy workflow)

The repo is cloned at `~/code/barranquilla-guide` on Mike's Mac. Commits go
out as `Mike Chartrand <mike@mikec.pro>` (git config already set in this
clone).

**Claude writes files directly into the clone. Mike reviews and runs the
commit + push.** Standard hand-off at the end of an edit session is one
command:

```bash
cd ~/code/barranquilla-guide && git add -A && git status
```

Mike reviews the staged diff, then he runs the commit + push himself.
Cloudflare Pages auto-deploys in ~30–40s. After the deploy lands, verify on
https://barranquilla.guide/ if the change is visible above the fold; use the
preview URL for anything sensitive.

**Update the Recent changes log at the bottom of this file in the same
commit.**

---

## Common tasks, quick recipes

### Fix a typo or edit body copy in one post

Open `/<slug>/index.html`, edit, hand off for commit. No cache-buster bump
needed (HTML is not `immutable`).

### Publish a new weekly roundup

1. Copy the most recent weekly (e.g.
   `whats-happening-in-barranquilla-week-of-april-20-2026/index.html`) into
   a new folder with the new date slug.
2. Update `<title>`, meta description, canonical, og:title, og:description,
   og:url, og:image (if the hero changed), article:published_time,
   article:modified_time, H1, and body content.
3. Add the URL to `sitemap.xml`.
4. At the bottom of the *previous* weekly, add a "This week's roundup" CTA
   linking to the new one.

### Add a new evergreen post

1. Copy a similar existing post as your template, match the
   `<article class="single-article">` wrapper, `article-hero`,
   `article-header`, `article-body` structure.
2. Swap content. Write H2/H3 sections, the sticky TOC appears automatically
   once there are 3+ H2s.
3. Add `width`/`height` attributes on every `<img>`. First image is
   `loading="eager" fetchpriority="high"`; every subsequent image is
   `loading="lazy"`.
4. Add the URL to `sitemap.xml`.
5. Link from 2–3 related hubs (section index, related posts, homepage card
   if featured).

### Add a new image

Drop it in `/img/`. Reference as `/img/filename.ext`, no
`/wp-content/uploads/YYYY/MM/...` paths, those are WordPress legacy and
don't exist here.

If the new image is an `og:image`, run `scripts/fix-og-images.py` after the
commit lands (or add the `og:image:width`/`height`/`type`/`alt` +
`twitter:image` tags by hand, the script is idempotent).

### Site-wide change to nav, footer, or script tags

Because every page has the markup inlined, fan out with `sed`:

```bash
find . -name 'index.html' -not -path './.git/*' -print0 \
  | xargs -0 sed -i '' 's|>Things to Do<|>Explore<|g'
```

Spot-check 2–3 files afterwards. If you find yourself doing this often, drop
a tiny helper in `scripts/` so the next global edit isn't 100-file surgery.

### Change `css/site.css` or `js/main.js`

Edit the file, then **bump `?v=...` across every HTML file** (see Caching
section above). Commit both the asset edit and the version bump in the same
push so the deploy is atomic.

### Rebuild `sitemap.xml` after content changes

No script exists for this yet (the README mentions
`scripts/build_sitemap.py` but only `fix-og-images.py` is actually checked
in). Regenerate by walking every `index.html` in the tree, emitting one
`<url>` each, with these priority/changefreq conventions:

| Path                  | priority | changefreq |
|-----------------------|----------|------------|
| Homepage              | 1.0      | daily      |
| `/category/*/`        | 0.9      | daily      |
| `/section/*/`         | 0.9      | weekly     |
| `/neighborhoods/*/`   | 0.8      | monthly    |
| Regular posts         | 0.7      | monthly    |
| Legal pages           | 0.3–0.4  | yearly     |

A small Python script in `scripts/build_sitemap.py` would be a reasonable
addition the next time the sitemap needs a full rebuild.

### Add a third-party script or external fetch

Edit `_headers` to expand the matching CSP directive first. Commit and
deploy the `_headers` change, then add the script tag in a follow-up commit.
Otherwise the browser blocks the request and you'll see CSP violation
messages in the console on first load.

---

## Open Graph image metadata

Every page must have a complete OG image block, or social platforms
(Facebook, LinkedIn, WhatsApp, Slack, iMessage) silently skip the image
preview. The required tags are:

```html
<meta property="og:image"            content="https://barranquilla.guide/img/<file>.jpg" />
<meta property="og:image:secure_url" content="https://barranquilla.guide/img/<file>.jpg" />
<meta property="og:image:type"       content="image/jpeg" />
<meta property="og:image:width"      content="1200" />
<meta property="og:image:height"     content="630" />
<meta property="og:image:alt"        content="<og:title>" />
<meta name="twitter:image"           content="https://barranquilla.guide/img/<file>.jpg" />
```

`scripts/fix-og-images.py` walks every HTML file, reads the real dimensions
off the image on disk, and inserts the missing tags. Idempotent, safe to
re-run after editing any guide:

```bash
python3 scripts/fix-og-images.py
```

**Watch out for og:image URLs that 404.** This site is a WordPress export
and some pages reference base filenames (e.g. `bus-interior.jpg`) where only
sized variants (`bus-interior-992x900.jpg`) exist on disk. CF Pages serves
an HTML 404 fallback for missing image paths, which Facebook silently
rejects. The script's "skip (image not found locally: ...)" output flags
these. Fix by swapping the og:image URL to the largest variant that exists
in `img/`.

**Forcing Facebook to re-scrape after a fix:** Facebook caches "no image"
for a long time. After changes hit production, paste the URL into
https://developers.facebook.com/tools/debug/ and click "Scrape Again".

---

## Conventions (strict)

- **Internal links are path-relative with trailing slash:** `/some-slug/`.
  Never `https://barranquilla.guide/...` for internal links.
- **Preserve `id=` attributes on headings.** External links and the auto-TOC
  depend on them.
- **Images live at `/img/<basename>`.** Not `/wp-content/...`.
- **Keep nav + footer consistent across every page.** If you change one,
  rebuild all.
- **No jQuery, AddToAny, lazy-load plugins, or Yoast JSON-LD.** Stripped in
  the port. Don't reintroduce.
- **No emojis in content** unless Mike specifically asks.
- **Evergreen over year-bumping.** Prefer "typically runs in October" over
  "October 2025" where the fact doesn't change year to year.
- **Canonical URLs include the trailing slash.**
- **First above-the-fold image**: `loading="eager" fetchpriority="high"`.
  Every other image: `loading="lazy"`. Always include `width`/`height` to
  prevent CLS.

---

## Voice

- Foreigner-perspective, direct, specific. Colombia-experienced reader tone,
  not generic travel-blog copy.
- Specific numbers. Quote prices in COP first, USD in parentheses with the
  exchange rate used (e.g. "COP 20,000 = USD 5 at 4,000:1"). SMMLV
  (Colombian minimum monthly wage) is the peg for many visa-related
  thresholds.
- **Flag cédula vs passport access wherever it differs.** Many venues,
  banks, medical providers, and government services behave differently for
  tourists (passport) vs residents (cédula). Call it out.
- **No "search Facebook for X."** Always direct links to the venue's
  Instagram, website, or WhatsApp.
- Editorial, insider tone. Read any existing guide for voice.
- Dates: bump `article:modified_time` and the human byline when you
  substantively update a post.

---

## Things to NOT touch

- **Don't commit credentials.** GitHub PAT and Cloudflare token are
  session-scoped; keep them out of the repo.
- **DNS records.** Apex + `www` CNAME to `barranquilla-guide-git.pages.dev`,
  both proxied (orange cloud). Stable; don't change unless specifically
  doing a cutover or rollback. The CF Pages API token in use is Pages-only
 , DNS edits need a broader token (ask Mike).
- **The `chatbase-position-fix` `<style>` coords**, tuned to sit above the
  sticky "Moving here?" CTA bar.
- **The `_headers` CSP.** Only add to it. Don't remove directives.
- **The Namecheap WordPress origin.** Rollback parachute, still running.
- **`tools/social-publisher/`.** Separate helper, not part of the public
  site. Leave alone unless asked.
- **Don't skip the cache-buster bump** when editing `site.css` or
  `main.js`, see Caching section.
- **Don't delete H2 `id` attributes.** External links and sitemap references
  may depend on them.

---

## Known gaps (as of 2026-04-23)

- **7 images referenced but missing in `/img/`**: `buenavista.webp`,
  `cinepolis2-1024x532.webp`, `language-exchange-2.png`,
  `playground-1024x683.jpg`, `sipaint-300x300.webp`, `stadio-717x1024.jpg`,
  and a screenshot with a non-ASCII filename. Re-upload if originals turn
  up.
- **Homepage has ~58 absolute `https://barranquilla.guide/<slug>/` URLs**
  inside a JS search-data object. They resolve correctly against prod DNS;
  no action needed unless one of the referenced slugs stops existing.
- **No on-site search.** Intentionally removed, the WordPress `?s=` query
  was gone after the static port, and rather than bolt Pagefind on top, the
  search UI was stripped on 2026-04-23. Discovery on this site is now
  handled by Catalina, not Chatbase.
- **Chatbase removed on 2026-05-13.** Bot id `wv8hNpU46aEhF0eXDOVF4` and the
  hero "Ask the guide" CTA were stripped network-wide so we could embed the
  Catalina chat widget cleanly. Stripper lives at `scripts/remove-chatbot.py`
  (idempotent). CSP entries swapped from `https://www.chatbase.co` to
  `https://catalina.barranquilla.guide` in `_headers` script-src + connect-src.
  The Catalina widget snippet itself is added by the broader network deploy
  (catalina worker + DNS for catalina.barranquilla.guide).
- **`scripts/build_sitemap.py` is referenced in the README but doesn't
  exist.** Only `fix-og-images.py` and `remove-search.py` are checked in.
- **No cookie-consent banner.** GA4 fires on every page load. Add a gate
  (mirror medellin.guide's `consent.js`) if that becomes a regulatory issue.

---

## If something goes wrong

- **Deploy failed.** CF Pages dashboard → `barranquilla-guide-git` →
  Deployments shows build logs. Revert the bad commit with `git revert` and
  push.
- **Need to roll back.** Pages keeps every prior deployment. Dashboard →
  Deployments → pick an earlier successful one → "Rollback to this
  deployment." One click.
- **Site down on production but preview works.** DNS or cert issue. Check
  Custom Domains in the Pages dashboard. If "pending," give it 60s. Longer
  than that, verify both CNAMEs still point to
  `barranquilla-guide-git.pages.dev`.
- **CSS/JS changes didn't land for visitors.** You forgot to bump the
  `?v=...` cache-buster, see the Caching section.
- **403/401 from GitHub push.** PAT rotated. Mike handles the push anyway,
  so this shouldn't be Claude's problem directly, flag it to Mike.
- **403/401 from Cloudflare API.** Token rotated. Ask Mike for a new one.

---

## Sister site: medellin.guide

The sister site (`Mikesc74/medellin-guide`) is a flat-file static site:
`guides/<slug>.html` (no per-slug directories), CSS inlined per-page (no
shared `/css/site.css`), manually curated TOCs instead of auto-generated, and
a Cloudflare Worker for form submissions instead of Formspree. **Different
shape, don't copy patterns blindly between the two.** See that repo's own
`CLAUDE.md` for its orientation.

---

## Recent changes

- **2026-05-21 (later x2)**, Cross-site quality sweep matching the medellin.guide Phase 2 work. (1) Corrected the inherited stale 2026 minimum-wage figures: SMMLV COP 1,423,500 to COP 1,750,905 across 7 pages, and in salary-for-colombian-maid + visas-colombia-barranquilla fixed the derived figures (auxilio 200,000 to 249,095, live-out floor to COP 2,000,000, the 3x visa-income floor 4,270,500 to 5,252,715 / about USD 1,310). (2) Enforced the house no-dashes rule site-wide: removed all en dashes (was 942), numeric ranges became "X to Y", prose dashes became commas, attached became hyphens; em dashes were already 0. 65 files touched, verified 0 dashes remain. STILL TODO to fully match medellin.guide: strip the unrelated Pexels stock photos (same `article-inline-photo` markup) and add the per-guide practical "say this" phrasebook tidbits on the same-titled guides. Deploy: `git add -A && git commit && git push`.
- **2026-05-21**, Evergreen cross-site content parity (Barranquilla): added 3 new long-form posts that existed on medellin.guide but were missing here, so the network's non-city-specific coverage matches. New posts (standard per-slug `/<slug>/index.html`, shared `/css/site.css`, auto-TOC, full OG block, Catalina widget): `buying-property-barranquilla/`, `bringing-money-to-colombia/`, `common-scams-barranquilla/`. Each adapted from the medellin.guide source and re-flavored for Barranquilla; the national legal/financial substance is retained (escritura/notaría/Oficina de Registro, Banco de la República foreign-investment registration for repatriation, the 4x1000/GMF, the denuncia + 123 process). COP-first with USD in parens at 4.000:1; concierge/service selling stripped; correct emergency line 123; 0 em/en dashes; single h1; every body H2 carries an id for the auto-TOC. Hero + og:image reuse the existing `/img/bus-3-992x900.webp` placeholder (swap for topical heroes later). Discovery wired: 3 URLs added to `sitemap.xml` (priority 0.7, monthly) and 3 cards to `/section/guides/index.html` (label How-to Guides). No CSS/JS edits, no cache-buster bump. Files: 3 new `<slug>/index.html`, `sitemap.xml`, `section/guides/index.html`. Hand-off: review with `cd ~/code/barranquilla-guide && git add -A && git status`, then commit + push.
- **2026-05-16 (later x2)**, Catching the log up on the paisa-boutique rebuild that happened earlier today (the pre-condition for the persona-rename and bilingual entries below). Wholesale theme port from medellin.guide, plus a WordPress-fingerprint scrub at the end. **(A) CSS.** `css/site.css` replaced with a clean paisa-boutique stylesheet (503 lines): warm cream / gold / terra / deep-green palette via `--pb-*` tokens (replacing the old cool-navy / coral system), Fraunces serif (display) loaded from Google Fonts CDN with the print/onload async pattern + Inter self-hosted sans, generous radii (14 to 18px on cards, pill 999px on buttons). New class system: `.pb-top` utility band, `.site-pb` sticky cream header with backdrop-blur, `.pb-drawer` mobile overlay, `.hero-merged` rounded `.cat-frame` hero, `.svc` service grid, `.gd` guide cards, `.now-card`, `.mag`, `.editorial-bg` ink feature, `.pb-newsletter`, `.site-pb-foot` deep-ink footer. **(B) Homepage rewrite.** `index.html` written from scratch around the new hero-merged with the Carnival photo + persona avatar + 4 CTA cards launching the chat widget, 2x2 browse-the-guide grid, 8-neighborhood horizontal strip, 4 cornerstone guides, ink editorial feature (Barranquilla vs Medellín vs Bogotá), 3 weekly-news cards, 4 magazine cards, newsletter to `newsletter.colguides.com/subscribe`, 4-column footer. **(C) Shell fan-out to 107 other pages.** Python + BeautifulSoup script removed each page's old `<nav.site-nav>`, `<div.mobile-nav>`, `<div.search-overlay>`, `<footer.site-footer>` blocks and inserted the new pb-* shell. Charo widget script (later Catalina, per the 2026-05-16 rename) + inline drawer-toggle JS appended before `</body>` on every page. **(D) Brand logo wire-up.** `<span class="pb-mark"><img src="/logo-b.webp">` markup site-wide. The 64x64 gold-and-navy serif-B medallion was supplied as `/logo-b.webp` + `/logo-b.png`. CSS: transparent container background, image fills the 34px circle. **(E) Favicons + webmanifest.** All sizes (32 / 180 / 192 / 270 / 512) replaced with B-medallion renderings; `site.webmanifest` theme_color → `#f6efe2` and background_color → `#fbf8f1` so installed PWAs match the cream site; added `/img/favicon-512.png` as a maskable icon; `?v=2` cache-buster on every favicon link; `<link rel="icon" sizes="512x512">` added to all 108 HTML `<head>` blocks. **(F) WordPress fingerprint scrub.** Stripped WP-export class soup from 89 `<article>` tags (kept `.single-article` since the auto-TOC JS depends on it; dropped `post`, `type-post`, `status-publish`, `format-standard`, `has-post-thumbnail`, `hentry`, `post-NNNN`, `category-*`, `section-*`). Removed `id="post-NNNN"` attrs (169 instances). Deleted 45 orphan `<div class="toc">` WP inline TOC blocks (the JS-built sidebar TOC is the only TOC now). Stripped `class="avatar avatar-80 photo"` markup from 88 author imgs. Pared 4 Gutenberg `wp-block-*` and `wp-post-image` class hooks. Verified by grep: 0 WP markers remain in class attributes anywhere on the site. **(G) `_headers`.** CSP `style-src` += `https://fonts.googleapis.com` and `font-src` += `https://fonts.gstatic.com` for Google Fonts. Early Hints `Link:` preload bumped to the current cache-buster. **(H) Cache-buster.** CSS bumped `?v=20260515a` → `?v=20260516e` over several iterations as logo + favicon + WP-scrub work landed during the day. **Practical impact.** Page chrome on all 108 pages is now visually and structurally identical to medellin.guide. Shared CSS, folder-per-post URLs, Cloudflare Pages auto-deploy, `/js/main.js` (auto-TOC + archive lazy-load), Catalina widget mount, and newsletter endpoint preserved unchanged. Em-dash audit clean throughout. The follow-on rename (Charo → Catalina) and bilingual EN/ES pass logged in the two entries below ran on top of this rebuild.

- **2026-05-16 (later)**, Bilingual chrome (EN/ES) + persona-rename completion. Two related changes shipped together. **(A) EN/ES toggle, mirrors medellin.guide.** Added the `html.lang-en .pb-es,html.lang-es .pb-en{display:none}` visibility rules + `.pb-langtog` pill styles to `css/site.css`. Added a 25-line lang-toggle IIFE to the bottom of `js/main.js` that reads `?lang=` → `localStorage.bgg_lang` → `navigator.language` (defaults EN), toggles `<html class="lang-en|lang-es">`, persists choice, swaps `document.title` from `<title data-lang>` variants. Fan-out script at `~/Library/Application Support/.../outputs/add_lang_toggle.py` walked all 108 HTML files and: added `class="lang-en"` to `<html>`, wrapped the skip-link, the `.pb-top` band tagline, every `.pb-nav` anchor, every `.pb-drawer` anchor, every footer-column `<h5>` heading, every footer link label, and the `Chat with` / `Ask` persona CTAs in `<span class="pb-en">EN</span><span class="pb-es">ES</span>` pairs. Article bodies left in English (same pattern as medellin.guide). Wrapping is scoped to chrome regions (`<div class="pb-top">`, `<header class="site-pb">`, `<aside class="pb-drawer">`, `<footer class="site-pb-foot">`) so article-body links to `/section/guides/` etc. are NOT touched. Homepage gained bilingual `<title data-lang>`, `<meta description data-lang>`, `<meta og:title|og:description|og:locale data-lang>`, and `<link rel="alternate" hreflang>` tags pointing at `?lang=es`. Toggle UI pill in the `.pb-top` right column ("EN | ES", gold-filled for the active language). The homepage and `404.html` don't load `/js/main.js` (they have inline scripts) so the toggle IIFE was inlined directly in both. Cache buster bumped `?v=20260516d` → `?v=20260516e` across all 108 HTML files. **(B) Persona rename, completion.** The 2026-05-16 (earlier) entry above noted the Charo→Catalina swap but the homepage hero still said "Charo" (lede paragraph, image alt, `<strong>` caption, "chat with" hint, "Talk to" CTA arrow). Today's pass replaced every `\bCharo\b` site-wide via `~/Library/Application Support/.../outputs/rename_persona.py`. Charo references now 0. Avatar image filenames left alone (`/charo-avatar-128.webp` and `/charo-avatar-56.webp` still on disk; only the visible alt text changed to "Catalina, Barranquilla Guide AI concierge"). Spanish translations for chrome are workable but a costeño read-through could tighten the tagline ("La guía insider de Barranquilla, comprobada por costeños.") and the nav labels ("Mapa", "Vivir aquí"). Em-dash audit clean on both sites.

- **2026-05-16**, Persona rename: dropped the per-city "Charo" (Barranquilla) and "Coral" (Cartagena) personas. All guides now use a single "Catalina" name end-to-end. UI button text replaced across all 108 HTML files: `Chat with Charo` → `Chat with Catalina`, `Ask Charo` → `Ask Catalina`. CSS comment `CHARO FRAME` → `CATALINA FRAME` in `css/site.css`. Worker still resolves per-city behavior from the Host header, only the surface name changed.

- **2026-05-15**, Catalina widget added network-wide. `_headers` CSP updated: added `https://catalina.barranquilla.guide` to `script-src` and `connect-src`. `<script src="https://catalina.barranquilla.guide/widget.js" defer></script>` injected before `</body>` across all 108 HTML files via sed fan-out. The widget is served by the catalina worker, which resolves the site context from the request Host header. Chatbase was already removed (2026-05-13). The catalina worker's `wrangler.toml` now includes `catalina.barranquilla.guide` as a custom domain; run `wrangler deploy` from `~/code/catalina` to activate DNS and route. Same deploy also wires up `catalina.thecartagena.guide`.

- **2026-05-08 (later same day)**, Hero-image diversification across the three most recent weeklies. The Apr 20, Apr 27, and May 4 posts had all been using `/img/Adobe-Express-file.png` (the generic blue weekly hero), so the `/category/now/` archive looked repetitive, three identical thumbnails stacked. Per-post pick is now the lead-story tie (took two passes, first attempt picked Malecón/bus/airport which Mike rejected as not matching the lead stories): **(1)** `/whats-happening-in-barranquilla-week-of-april-20-2026/` → `/img/food-barranquilla-colombia.jpg` family (1024×538 hero, 600×400 archive thumb, srcset 1024/768/600/300). Lead item that week was Burger Master 2026 at 19 restaurants. **(2)** `/whats-happening-in-barranquilla-week-of-april-27-2026/` → `/img/nightlife-barranquilla-1.jpg` family (1024×538 hero, 600×400 archive thumb, srcset 1024/768/600/300). Lead item was J Balvin's Friday-night stadium show at Estadio Romelio Martínez plus Plaza Urban Fest the same week. **(3)** `/whats-happening-in-barranquilla-week-of-may-4-2026/` → `/img/barranquilla-city-panoramic-view.jpg` family (1024×384 hero, 600×400 archive thumb, srcset 1024/900/768/600/300). No specific lead-story tie (no rain or JetBlue imagery in the repo), this is a city-skyline "Barranquilla right now" generic hero. All three: `og:image`, `og:image:secure_url`, `og:image:type` (jpeg, not png), `og:image:width`/`height` updated to match the new file's natural dimensions; `og:image:alt` rewritten to be image-descriptive rather than just the title; `twitter:image` updated. Article-hero `<img>` width/height/src/srcset/alt updated to match. The `/category/now/` archive's `posts-grid` cards swapped to the per-post 600×400 thumbnails. Bumped `article:modified_time` on Apr 20 → `2026-05-08T16:30:00+00:00` and Apr 27 → `2026-05-08T16:00:00+00:00` so Facebook/Slack/iMessage re-scrape and pick up the new previews. **Important next step**: run the Facebook scrape-debugger on each URL to force a refresh, `https://developers.facebook.com/tools/debug/` → paste each post URL → "Scrape Again". Otherwise FB will keep showing the old Adobe-Express thumbnail for days. No CSS or JS edits, no `?v=...` cache-buster bump needed.

- **2026-05-08**, Published the weekly news roundup `/whats-happening-in-barranquilla-week-of-may-4-2026/`. Five items: rainy season has actually started (the Tuesday Apr-28 aguaceros were the first proper ones), JetBlue's Oct-1 nonstop FLL→BAQ launch announcement (per Caribbean Journal May 3 + JetBlue IR, part of an 11-route FLL expansion after Spirit's exit from FLL), Perrenque Creativo marketing summit at Comfamiliar (May 6–7, Carnaval Queen Michelle Char Fernández keynoted), Atlántico vehicle sales +41.9% YoY in April per El Heraldo, and Diego El Cigala's flamenco show at Teatro José Consuegra Higgins last Thursday. Hero reused: `/img/Adobe-Express-file.png` (the standard weekly hero). **Site-wide wiring done in the same commit:** (1) homepage `now-grid` updated, May 4 card prepended, Apr 13 card aged out so the carousel still shows three cards (May 4 / Apr 27 / Apr 20); (2) `/category/now/index.html` archive, new `article-card` prepended above the Apr 27 card; (3) `sitemap.xml`, new `<url>` entry added with `lastmod=2026-05-08`, priority 0.7, changefreq weekly; previous Apr 27 entry's `lastmod` bumped to 2026-05-08 as well; (4) Apr 27 post updated, added "This week's roundup" CTA above the existing "Previously" line, and `article:modified_time` bumped to 2026-05-08T16:00:00+00:00 so Facebook/Slack/etc. re-scrape and pick up the new outbound link. No CSS or JS edits, no `?v=...` cache-buster bump needed (current is `20260507a`, untouched). **Items I deliberately skipped:** AllEvents.in had a "Bad Bunny at Estadio Metropolitano May 30" listing for Barranquilla, but Bad Bunny's tour pages confirm that date is Madrid (Riyadh Air Metropolitano), mis-attribution. Also passed on the Titos Bolos eviction (low foreigner-relevance), Expografitech (niche industry trade fair), and the Brazilian-investment outreach piece (civic positioning). **Action open for Mike**: review and run `cd ~/code/barranquilla-guide && git add -A && git status`, then commit + push. Source notes (JetBlue/Caribbean Journal/Spirit framing fact-check, El Cigala show confirmation flagged as "verify happened, not cancelled") saved at `~/Library/Application Support/Claude/local-agent-mode-sessions/.../outputs/barranquilla-weekly-2026-05-04-sources.md`.

- **2026-04-27**, Published the weekly news roundup `/whats-happening-in-barranquilla-week-of-april-27-2026/`. Six items: J Balvin at Estadio Romelio Martínez (Fri May 1, *Ciudad Primavera* tour), Plaza Urban Fest (Mon Apr 27), the new 42-of-100 Euro 6 buses now running on metropolitan routes (per El Heraldo Apr 23), dry-to-rainy-season transition heads-up, Colombia's digital-nomad visa being narrowed to tech-only adjudications, and Barranquilla's Booking.com 2026 must-visit recognition. Hero reused: `/img/Adobe-Express-file.png` (the standard weekly hero). No per-slug Pexels inline figure this week, keep tight. **Site-wide wiring done in the same commit:** (1) homepage `now-grid` updated, Apr 27 card prepended, Apr 6 card aged out so the carousel still shows three cards (Apr 27 / Apr 21 / Apr 13); (2) `/category/now/index.html` archive, new `article-card` prepended above the Apr 21 card; (3) `sitemap.xml`, new `<url>` entry added with `lastmod=2026-04-27`, priority 0.7, changefreq weekly; previous Apr 20 entry's `lastmod` bumped to 2026-04-27 as well; (4) Apr 20 post updated, added "This week's roundup" CTA above the existing "Previously" line, and `article:modified_time` bumped to 2026-04-27T14:30:00+00:00 so Facebook/Slack/etc. re-scrape and pick up the new outbound link. No CSS or JS edits, no `?v=...` cache-buster bump needed. **Action open for Mike**: review and run `cd ~/code/barranquilla-guide && git add -A && git status`, then commit + push. Source notes for fact-check (J Balvin show times, bus rollout count "42 of 100", digital-nomad visa "tech-only" framing) saved at `~/Library/Application Support/Claude/local-agent-mode-sessions/.../outputs/barranquilla-weekly-2026-04-27-sources.md`.

- **2026-04-26 (later same day)**, Image-delivery fix: the four homepage `cat-block-image` JPEGs were 2,036 KB total (852 + 525 + 431 + 228). PSI mobile flagged 1,244 KiB potential savings on these alone. Converted each to AVIF + WebP at desktop-friendly widths (1400w / 1280w / 1200w depending on source) and added matching 800w variants for future responsive serving. **Per image (mobile AVIF):** el-golf 852→96 KB (89% saving), negra-pulida 525→72 KB (86%), cumbia 431→34 KB (92%), family-food 228→56 KB (75%). **Index.html change:** each `style="background-image: url(...)"` is now `style="background-image: url(<jpeg>); background-image: image-set(url(<avif>) type('image/avif'), url(<webp>) type('image/webp'), url(<jpeg>))"`. Two declarations: vanilla `url()` first as the cascade fallback for browsers that don't parse `image-set()`; modern browsers ignore that and use the second line, picking AVIF first (95%+ browser support), WebP fallback, JPEG last. Original JPEGs retained on disk. Generated by an inline Python/Pillow script (Pillow has native AVIF write in this environment). 16 new files in `/img/` (4 sources × 2 widths × 2 formats). LCP element on the homepage is now the `<h1>` text (not the hero image), so this change targets total page weight, FCP, and the "Improve image delivery" PSI line; LCP improvement comes from the font swap path. Expected total page weight: 3,027 → ~1,250 KB on mobile.

- **2026-04-26**, Performance pass to fix the mobile blank-window flash and improve mobile LCP across the network. **Root cause for the flash:** Google Fonts CSS was loaded synchronously via `<link rel="stylesheet">` in `<head>`, which blocks first paint until `fonts.googleapis.com` returns. medellin.guide already had the `media="print"; onload="this.media='all'"` async pattern; barranquilla + cartagena did not. **Changes:** **(1)** All 103 HTML files now use the print/onload pattern with `<link rel="preload" as="style">` and a `<noscript>` fallback. The Google Fonts URL already carries `&display=swap`, so system-fallback fonts render immediately while Playfair/Inter download in the background. Sentinel `<!-- PERF: async fonts -->` and idempotent applier at `scripts/perf-fix-fonts.py`. **(2)** Homepage hero preload added: `<link rel="preload" as="image" href="/img/carnival1.webp" fetchpriority="high">`. Sentinel `<!-- PERF: hero preload (homepage) -->`. **(3)** `decoding="async"` added to 506 images across 75 article pages via `scripts/perf-fix-images.py` (idempotent). Off-thread image decode, no critical-path impact. **(4)** `loading="lazy"` added to 115 below-fold images (Gravatar avatars + WordPress wp-block-image figures) via `scripts/perf-fix-lazy.py`. Article-hero images keep `loading="eager"` per template convention, not touched. **(5)** `_headers` updated: added `/` block with `Link: </css/site.css?v=20260424a>; rel=preload; as=style` and `Link: </img/carnival1.webp>; rel=preload; as=image`. Cloudflare uses these as 103 Early Hints, pushing CSS + hero to the browser before our HTML response body is sent. No CSP changes. No cache-buster bump (no edits to `css/site.css` or `js/main.js`). Mike, verify in the CF Pages dashboard that Speed → Optimization has Brotli, HTTP/3, **Early Hints**, and Auto Minify all on; skip Rocket Loader (it can break inlined Chatbase + gtag scripts). Baseline + post-deploy measurement template at `~/Documents/Claude/Projects/perf-baseline-2026-04-26.md`.

- **2026-04-24**, Added Schema.org structured data to homepage `<head>`. Three JSON-LD blocks: `WebSite` with `@id` `https://barranquilla.guide/#website` and `inLanguage: en-US`; `Organization` with `@id` `https://barranquilla.guide/#organization`, founder Mike Chartrand, and `sameAs` Instagram + Facebook group; `CollectionPage` declaring this site as part of "Colombian City Guides" with `hasPart` linking medellin.guide and thecartagena.guide for cross-network topical signal. Injected after the `/css/site.css` link, before the GA4 gtag block. No CSS or JS changes, no `?v=` cache-buster bump needed. Test at `https://search.google.com/test/rich-results?url=https%3A%2F%2Fbarranquilla.guide`.


Newest first. Add an entry every time you push.

- **2026-04-25**, Cross-site network linking: added a "Sister Sites" column to the footer linking to medellin.guide and thecartagena.guide. Pairs with the existing `CollectionPage` `hasPart` schema for a structured-data + crawlable-link cross-network signal. Sentinel `<!-- SISTER_SITES_NETWORK -->` makes the block re-runnable from `~/Documents/Claude/Projects/medellin-network/deploy_v5.py`.

- **2026-04-24**, Consolidated the two Colombian-citizenship guides. The standalone `/how-to-apply-for-colombian-citizenship-through-naturalization/` post was retired and merged into `/colombian-citizenship-exam-study-guide/`, since the exam guide already covered Part 1 (eligibility, documents, fees, timeline, exam) and the duplication was confusing. Specifics: **(1)** Pulled the procedural content that was missing from the exam guide and added six new H2s between "The day of the exam" and the "Part Two" history divider, `after-approval` (cedula → passport → voter registration), `dual-citizenship` (foreign-passport entry, libreta militar, children-by-descent), `travel-benefits` (130+ countries, Schengen, US/Canada exception, extradition note), `loss-and-renunciation`, `common-mistakes`, and `attorneys` (COP 6-12M typical fees, when self-rep is viable). **(2)** Deleted `/how-to-apply-for-colombian-citizenship-through-naturalization/index.html` and its directory. **(3)** Added a 301 in `_redirects`: old slug → `/colombian-citizenship-exam-study-guide/`. **(4)** Removed the old article's URL from `sitemap.xml`. **(5)** Removed the old article's card from `/section/guides/index.html` (now 26 cards instead of 27). **(6)** Updated four files that linked to the old slug, fanned the URL swap across `visas-colombia-barranquilla/`, `tax-residency-colombia-2026-guide/` (also retitled the related-articles card to match the new guide's H1), `moving-to-barranquilla/`, and `colombian-citizenship-exam-study-guide/` itself (intra-page self-references in the intro and "Further reading"). No CSS/JS changes, no cache-buster bump needed.
- **2026-04-24**, Replaced the broken paginated `/section/guides/` archive with a single-page lazy-loaded view. Background: the WordPress-export only included page 1 of `/section/guides/` as a static file, the pagination footer linked to `/section/guides/page/2/`, `/3/`, `/4/` which never existed on disk, so Cloudflare Pages was serving the homepage as the SPA-style not-found fallback (visitors clicking "2" landed on `/`). Fix had two parts: **(1)** Rebuilt `/section/guides/index.html` to render all 27 guides in a single `posts-grid` instead of 12. The 11 existing page-1 cards were preserved verbatim (kept their original ids, dates, and labels, Carnival and the Kids guide both render with their `Explore` label as before). The 16 missing guides were generated from each post's own metadata (`og:title`, `article:published_time`, og:image), with a `<span class="label">How-to Guides</span>` and Mike Chartrand byline. Cards use `srcset` against the `-300/600/768/1024w` variants in `/img/` and `loading="lazy"` on the `<img>` so images defer until the card scrolls near the viewport, this is the "lazy load" the user asked for, handled by the browser, no extra JS. The pagination block at the bottom of the archive was removed. **(2)** Added 7 redirect rules to `_redirects` so legacy `/section/<term>/page/N/` URLs (from external links, old Google index, or sitemap copies) 301 to `/section/<term>/` instead of silently falling through to the homepage. Covered `guides`, `explore`, `live`, `eat-drink`, `stay`, `magazine`, plus `category/now`. No CSS/JS edits, no cache-buster bump needed. The ad slot card after the 8th article-card was preserved.
- **2026-04-24**, Renamed the "Guides" section to "How-to Guides" site-wide and made `/moving-to-barranquilla/` a guide rather than a separate top-level nav entry (mirrors the equivalent change on thecartagena.guide). Specifics: **(1)** Primary nav + mobile nav: "Moving to Barranquilla" entry now reads "How-to Guides" and points at `/section/guides/`. Fanned out across all 104 HTML files via sed. **(2)** Section page rebrand: `/section/guides/index.html` H1, `<title>`, and `og:title` swapped from "Guides" / "Guides Archives - Barranquilla Guide" to "How-to Guides" / "How-to Guides - Barranquilla Guide". **(3)** Site-wide article-card and post-header section labels: every `<span class="label">Guides</span>` (112 occurrences) → `<span class="label">How-to Guides</span>`. **(4)** Footer column heading: every `<div class="footer-nav-title">Guides</div>` (104 files) → `<div class="footer-nav-title">How-to Guides</div>`. The footer's "Moving Here" link inside that column was kept (page still exists). **(5)** `/moving-to-barranquilla/` page itself: added a `<span class="label"><a href="/section/guides/" style="color: var(--coral);">How-to Guides</a></span>` above the H1 in the article-header so it now reads as a guide. The page is otherwise unchanged - it remains a hub linking out to specific guides. **(6)** Added a Moving-to-Barranquilla card at the top of `/section/guides/`'s `posts-grid` (uses `/img/expats-2-600x400.jpg` as the thumbnail) so the guide is now listed in the archive. **(7)** Hero "reading paths" middle card on the homepage was left pointing at `/moving-to-barranquilla/` (the page is still the right curated landing for "Thinking of moving?"). No CSS/JS changes, no cache-buster bump, no CSP change.
- **2026-04-24**, Replaced the favicons with the new BG circle logo. Source: `~/Documents/Claude/Projects/Barranquilla.Guide/photos/BG Logo - Transparent .png`. Generated 4 transparent-background PNGs (32, 180, 192, 270) plus a legacy `favicon.ico` (16/32/48 multi-size), cropped tight to the logo's bounding circle and masked to a circle so corners render transparent (no white square around the icon). Updated 104 HTML files from `/img/favicon-*.jpg` → `/img/favicon-*.png` via sed. `site.webmanifest` 192 + 270 entries swapped from `image/jpeg` → `image/png`. Old `.jpg` favicons deleted from `/img/`. Heads-up for Mike: browsers cache favicons aggressively - hard reload or incognito to verify after deploy.
- **2026-04-24**, Fixed the newsletter form. It was throwing two `ReferenceError`s on every page load: `updateNav is not defined` and `bgData is not defined`. The `updateNav` reference was a strict-mode block-scoping bug, the function was declared inside the `if (nav && isHero)` block, so the `DOMContentLoaded` handler at the bottom couldn't see it. Hoisted the declaration to the IIFE scope and guarded with an early return when nav/hero aren't present. The `bgData` reference was the legacy WordPress AJAX path the CLAUDE.md flagged for audit, `bgData.ajaxUrl`/`bgData.nonce` were never injected into the static site, so the submit handler exploded mid-flight and the button hung on "Subscribing…" forever. Replaced the WP fetch with a direct POST to `https://formspree.io/f/xgopjoao` (the documented Formspree endpoint), with `Accept: application/json` so we get JSON back and can render inline status without redirecting. Also removed the dangling "Contact form → Brevo" IIFE at the bottom of `js/main.js`, it was a second `bgData.ajaxUrl` consumer that piggybacked on contact form submits to dual-write to Brevo via WordPress; with no WordPress backend it was dead code that threw on every contact submit. Updated `index.html` to drop two WP cruft hidden fields (`bg_newsletter_nonce`, `_wp_http_referer`) and add `<input type="hidden" name="subject" value="newsletter-subscribe" />` so submissions land in Formspree with the documented filterable subject. Cache-buster bumped `20260423c` → `20260424a` (208 refs across 103 HTML files). **Action still open for Mike**: confirm the Formspree `xgopjoao` inbox is monitored / forwarding to the right place; consider re-adding a server-side Brevo dual-write via Cloudflare Worker if email-marketing automation is needed.
- **2026-04-24**, `/city-map/`: added two UX features. **(1)** Every popup now has "Google Maps" and "Waze" directions buttons below the guide link, they open `maps.google.com/dir/?api=1&destination=LAT,LNG` and `waze.com/ul?ll=LAT,LNG&navigate=yes` respectively in a new tab, so users can hand off to the navigation app they already use on their phone. This is the high-value UX move: the custom map handles discovery, the user's existing Maps/Waze app handles turn-by-turn. **(2)** "📍 Find me" button added to the end of the filter bar, on click, calls `map.locate({setView:true,maxZoom:15,enableHighAccuracy:true})` and drops a pulsing blue dot at the user's location plus a translucent accuracy circle. Handles `locationerror` with an alert. Browser permission prompt fires on click (not on page load) so Chrome/Safari don't auto-block. No third-party scripts added, Leaflet's built-in `map.locate()` uses `navigator.geolocation` natively. No CSP edits needed. Also corrected Hampton by Hilton location in two places: the best-hotels article incorrectly said "Calle 98 / Villa Santos-Buenavista" but the real address is Cra 51B #79-246 in Alto Prado (confirmed via businesstravelnews.com listing, Dann Carlton is the Calle 98 hotel, Hampton is 8 blocks south on Cra 51B). Moved the pin from 11.0053, -74.8200 (Calle 85, San Vicente) to 11.0036, -74.8119 (Alto Prado, ~50m south of OSM-tagged café El Diario at Cra 51B #79-296). Updated the article paragraph accordingly.
- **2026-04-24**, Added `/colombian-citizenship-exam-study-guide/`, a long-form (approximately 45 min read, about 135 KB HTML) companion to the existing `/how-to-apply-for-colombian-citizenship-through-naturalization/` post. Part 1 covers the practical application (who qualifies, where to file at Cancillería, fees, timeline, exam format, day-of tips). Part 2 is a 15-chapter narrative history of Colombia, geography, pre-Columbian cultures, conquest, independence, Gran Colombia, 19th-century civil wars, Thousand Days' War, banana massacre, La Violencia, FARC/cartels, the 1991 Constitution, peace process, present-day. Each chapter closes with a "Key Facts for the Exam" block. Part 3 is reference material: 32-department table, date timeline, 30+ practice questions with answers, and an FAQ. Uses the existing `beautiful-flowers-in-barrio-abajo-1585x900.jpg` hero. Chatbase bootstrap included, standard nav/footer. No CSS/JS edits (no cache-buster bump needed). Scoped `<style>` in `<head>` styles `.key-facts` and tables inside `.article-body` only. Added URL to `sitemap.xml` with priority 0.8. Author byline: Mike Chartrand. Published date 2026-04-24.
- **2026-04-24**, Fixed 19 mis-located pins on `/city-map/`. Verified each
  against OpenStreetMap/Nominatim (reverse-geocoding every final value
  back to confirm the neighbourhood label). Biggest miss: **El Prado
  Hotel** was at 10.9890, -74.8072 (reverse-geocodes to `Las Delicias`),
  moved to 10.9992, -74.8003 (real Cra 54 & Cl 70 location, inside El
  Prado barrio). **Neighborhood pins** all moved to the actual barrios
  they name: El Prado (was Las Delicias), Villa Country, Buenavista,
  Riomar (all were in Altos del Limón or similar). **Named venues**:
  La Troja VIP (was ~1km north, now at Cra 44 & Cl 72), Mallorquin Eco
  Park, Airport BAQ terminal. **Editorial/category pins** that reference
  El Prado or act as El Prado zone markers, Best Restaurants Guide,
  Fine Dining (El Prado), Family Restaurants, Best Desserts, El Prado
  Nightlife Strip, Best Bars Guide, Nightlife Guide 2026, Salsa and
  Dance Schools, El Prado Walking Tour, were all sitting in Las
  Delicias / Boston / Barrio Colombia; relocated into El Prado proper
  (lat 10.993–10.997, lng -74.798 to -74.802). Coworking Zone generic
  pin moved into Alto Prado (where WeWork and Bronx Gym cluster).
  Confirmed that Marriott Barranquilla at 11.0172, -74.8406 is actually
  correct, OSM has it mapped as "Marriott, Calle 1A, Ciudad Mallorquín,
  Puerto Colombia" (the hotel is in Puerto Colombia municipality, not
  Barranquilla proper). No CSS/JS changes, no cache-buster bump needed.
- **2026-04-23**, Removed the broken on-site search UI (the WordPress
  `?s=` endpoint was gone after the port, so the magnifying-glass icon and
  full-screen `search-overlay` sheet led to dead URLs). Replaced the
  hero-search form on `index.html` with a `.hero-chat-cta` block that opens
  the existing Chatbase assistant. Dropped `.nav-search-btn`,
  `.search-overlay*`, and `.search-popular-link` CSS rules, and deleted
  the search overlay open/close code from `js/main.js`. Added
  `scripts/remove-search.py` (idempotent) which handles the nav + overlay
  removal and cache-buster bump across all 103 HTML files. Cache-buster
  bumped `20260423b` → `20260423c`. **Action still open for Mike**:
  confirm Chatbase (bot `wv8hNpU46aEhF0eXDOVF4`) is trained on
  `barranquilla.guide`, add the sitemap URL as a source in the Chatbase
  dashboard if not.
- **2026-04-23**, Expanded `CLAUDE.md` to match the medellin.guide
  operator's-manual standard. Added CF account id + preview URL, rollback
  parachute note, brand color tokens, Playfair + Inter font names, full CSP
  allow-list directive-by-directive, GA4 measurement id, Chatbase bot id +
  position-fix caveat, Formspree endpoint, Leaflet scoping, voice rules
  (foreigner perspective, COP/USD, cédula vs passport, no "search Facebook"),
  sitemap priority table, Known gaps (7 missing images, ~58 absolute URLs on
  homepage, no static search, missing `build_sitemap.py`, no consent
  banner), Things-to-NOT-touch list, If-something-goes-wrong recovery
  section, and medellin.guide sister-site cross-reference. Switched the
  deploy workflow to the hand-off pattern: Claude writes files, Mike reviews
  via `cd ~/code/barranquilla-guide && git add -A && git status`, Mike
  commits and pushes. Commits now go out as `Mike Chartrand
  <mike@mikec.pro>` (no "via Claude" suffix). Preserved the existing strong
  sections: the `?v=...` cache-buster caveat, Open Graph image metadata
  section, and auto-TOC explanation.
- **2026-04-23**, Completed Open Graph image metadata across every page
  (87 + 16 = 103 HTML files). Added `og:image:secure_url`, `og:image:type`,
  `og:image:width`, `og:image:height`, `og:image:alt`, and `twitter:image`
  alongside each existing `og:image`. Fixed 16 broken `og:image` URLs that
  pointed to base filenames where only sized variants existed on disk
  (causing CF Pages to return an HTML 404 fallback that Facebook rejected).
  Added `scripts/fix-og-images.py` to keep the metadata complete on future
  guide additions.
- **2026-04-23**, Added sticky sidebar Table of Contents to every guide
  (auto-generated from H2/H3 headings, coral active-state, mobile-collapsing
  layout under 1024px). Also introduced the `?v=...` cache-buster pattern
  on `/css/site.css` and `/js/main.js` because `_headers` marks them as
  immutable. Current version: `20260423b`. (Commits `b215c86`, `6dbaef9`,
  `e58b0fd`.)
