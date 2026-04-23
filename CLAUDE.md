# barranquilla.guide — orientation for Claude

This file is the fast path for any future Claude session working on this repo.
Read it first. Update the **Recent changes** log at the bottom every time you
commit. Keep the rest of the file current as the site evolves.

---

## What this is

A fully static HTML site. No build step, no framework, no CMS. Originally
exported from WordPress; now just files.

- **Host**: Cloudflare Pages (project connected to the GitHub repo).
- **Domain**: https://barranquilla.guide/
- **Deploy**: push to `main` → Cloudflare Pages auto-deploys in ~30 seconds.
- **Style reference**: medellin.guide — we try to match that clean, editorial look.

---

## Repo layout

```
/                        index.html, sitemap.xml, robots.txt, _headers, site.webmanifest
/css/site.css            The one stylesheet — shared by every page
/js/main.js              The one script — shared by every page
/img/                    All images (WordPress-exported filenames, many size variants)
/{slug}/index.html       One folder per guide/page. ~78 guides.
/section/{slug}/         Section landing pages (explore, live, eat-drink, guides)
/category/{slug}/        Tag/category archive pages
/neighborhoods/{slug}/   Neighborhood deep-dives
```

Each guide is a standalone HTML file. There is no shared header/footer include —
every page has the full nav, footer, and scripts inlined. That means global
changes (nav, footer, scripts, CSP) have to be fanned out with `sed` across all
HTML files, or applied in `_headers`.

---

## Page template (what every guide looks like)

```html
<article class="single-article">
  <div class="article-hero">...hero image...</div>
  <header class="article-header">
    <span class="label">Guides</span>
    <h1>...</h1>
    <div class="article-header-meta">...author, date, read time...</div>
  </header>
  <div class="article-body">
    <p class="guide-intro">...</p>
    <!-- legacy inline TOC block — now auto-hidden by JS -->
    <h2 id="slug">Section heading</h2>
    <p>...</p>
    ...
  </div>
</article>
```

H2 headings carry `id` attributes already (legacy from WordPress). The sidebar
TOC relies on those ids; if an H2 has no id, `js/main.js` auto-slugifies one.

---

## Key runtime features (globally applied)

### 1. Sticky sidebar Table of Contents

Implemented entirely in `css/site.css` and `js/main.js` — no per-guide HTML edits.

- `buildArticleToc()` in `main.js` finds every `h2` / `h3` inside `.article-body`,
  wraps the body + a generated `<aside class="article-toc">` in a grid layout,
  and hides any legacy `.toc` / `#ez-toc-container` block.
- Active section is tracked by a scroll listener that picks the heading closest
  above a fixed reading line (~140px from the top of the viewport).
- Under 1024px viewport, the grid collapses to single column and the TOC sits
  above the body as a compact block.

If you change the guide template in a way that renames `.article-body` or
`.single-article`, update the selectors in `buildArticleToc()` or the TOC will
silently stop appearing.

### 2. Nav / search / mobile menu / newsletter form

All in `js/main.js`. The newsletter form posts to a WordPress AJAX endpoint
(`bgData.ajaxUrl`) that may or may not still be live — audit before relying on
it. Contact form relays to Brevo via the same endpoint.

### 3. Chatbase chatbot

Loaded at the bottom of every page. CSS in `css/site.css` and `_headers`
CSP allows `https://www.chatbase.co`.

---

## Cloudflare Pages caching — IMPORTANT

`_headers` marks `/css/*` and `/js/*` with:

```
Cache-Control: public, max-age=31536000, immutable
```

One-year immutable cache. **Browsers and CF's edge will NOT re-fetch these
files.** If you edit `css/site.css` or `js/main.js`, you MUST also bump the
`?v=...` cache-buster on every `<link>` and `<script>` reference across the
~80 HTML files. Otherwise your changes will not reach visitors.

Quick bump (use a new version string each time — date-based is fine):

```bash
OLD=20260423b
NEW=20260424a
find . -name '*.html' -not -path './.git/*' -print0 \
  | xargs -0 sed -i "s/?v=${OLD}/?v=${NEW}/g"
grep -c "?v=${NEW}" visas-colombia-barranquilla/index.html   # expect 2
```

Current version in use: **`20260423b`** (update this line when you bump).

---

## How to work in this repo (clone + commit)

The repo is private. Clone URL and credentials are supplied in-session — never
commit them to the repo itself.

```bash
git clone https://Mikesc74:<GITHUB_PAT>@github.com/Mikesc74/barranquilla-guide.git
cd barranquilla-guide
git config user.name  "Mike Chartrand via Claude"
git config user.email "mike@mikec.pro"
```

Workflow:

1. Edit in the clone.
2. Commit with a clear message (sentence case, explain the *why* in the body).
3. Push to `main`. Cloudflare Pages auto-deploys.
4. Wait ~30–40s, then verify on https://barranquilla.guide/ before reporting done.
5. Update the **Recent changes** log in this file (`CLAUDE.md`) and include it
   in the same push.

Cloudflare: the API token and account id are supplied in-session if you need
to touch Pages directly (rare — git push is enough for code changes).

---

## Common tasks — quick recipes

### Add a new guide

1. Create `/new-guide-slug/index.html` by copying an existing guide (e.g.
   `visas-colombia-barranquilla/index.html`) and replacing title, meta, hero
   image, body content.
2. Ensure H2 headings have `id` attributes (slug-ified). The sidebar TOC
   auto-generates from them.
3. Add the URL to `sitemap.xml`.
4. Add a card to relevant section landing pages (`/section/*/index.html`).
5. Commit, push, verify.

### Site-wide change to nav, footer, or scripts

Because every page has the markup inlined, use `sed` to fan out the change
across all HTML files. Example — renaming a nav link:

```bash
find . -name 'index.html' -not -path './.git/*' -print0 \
  | xargs -0 sed -i 's|>Things to Do<|>Explore<|g'
```

Always spot-check a couple of files afterwards.

### Change `css/site.css` or `js/main.js`

Edit the file, then **bump `?v=...` across all HTML** (see Caching section above).
Commit both the asset edit and the version bump in the same push so the deploy
is atomic.

### Add a third-party script

Edit `_headers` to expand the CSP `script-src` / `connect-src` / etc. directives.
Then add the `<script>` tag to the HTML (site-wide = `sed` fan-out; one-page = edit
that file only).

---

## Conventions

- **Tone / voice**: editorial, insider, written for expats and travelers who
  want real answers, not generic listicles. See any existing guide for voice.
- **Dates**: articles use 2026 dates (`article:published_time`, `article:modified_time`,
  and the human-readable byline). When updating a guide, bump the
  `modified_time` to today.
- **Images**: live in `/img/`. Serve multiple sizes via `srcset` where possible.
  Keep `loading="lazy"` on everything except the above-the-fold hero image.
- **Currency**: COP figures are the primary reference; USD approximations in
  parentheses. SMMLV (Colombian minimum monthly wage) is the peg for many
  visa-related thresholds.
- **Internal links**: use absolute paths (`/visas-colombia-barranquilla/`),
  trailing slash.

---

## Things to be careful about

- **Don't commit credentials.** The GitHub PAT and Cloudflare token are
  session-scoped; keep them out of this file and out of any commit.
- **Don't skip the cache-buster bump** when editing `site.css` or `main.js` —
  see Caching section.
- **Don't break the TOC structure.** The guide template uses
  `<article class="single-article">` → `.article-body`. The sidebar TOC
  relies on exactly that.
- **Don't delete H2 `id` attributes.** External links and sitemap references
  may depend on them. If you must, update internal links accordingly.
- **`_headers` is strict.** CSP blocks any script/font/image source that isn't
  explicitly allowed. After adding a third-party integration, check the
  browser console for CSP violations.

---

## Open Graph image metadata

Every page must have a complete OG image block, or social platforms (Facebook,
LinkedIn, WhatsApp, Slack, iMessage) silently skip the image preview. The
required tags are:

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
off the image on disk, and inserts the missing tags. Idempotent — safe to
re-run after editing any guide. Run it whenever you add a new page or change
an `og:image` URL:

```bash
python3 scripts/fix-og-images.py
```

**Watch out for og:image URLs that 404.** This site is a WordPress export and
some pages reference base filenames (e.g. `bus-interior.jpg`) where only sized
variants (`bus-interior-992x900.jpg`) exist on disk. CF Pages serves an HTML
404 fallback for missing image paths — which Facebook silently rejects.
The script's "skip (image not found locally: ...)" output flags these. Fix by
swapping the og:image URL to the largest variant that exists in `img/`.

**Forcing Facebook to re-scrape after a fix:** Facebook caches "no image" for
a long time. After changes hit production, paste the URL into
https://developers.facebook.com/tools/debug/ and click "Scrape Again".

## Recent changes

Newest first. Add an entry every time you push.

- **2026-04-23** — Completed Open Graph image metadata across every page
  (87 + 16 = 103 HTML files). Added `og:image:secure_url`, `og:image:type`,
  `og:image:width`, `og:image:height`, `og:image:alt`, and `twitter:image`
  alongside each existing `og:image`. Fixed 16 broken `og:image` URLs that
  pointed to base filenames where only sized variants existed on disk
  (causing CF Pages to return an HTML 404 fallback that Facebook rejected).
  Added `scripts/fix-og-images.py` to keep the metadata complete on future
  guide additions.
- **2026-04-23** — Added sticky sidebar Table of Contents to every guide
  (auto-generated from H2/H3 headings, coral active-state, mobile-collapsing
  layout under 1024px). Also introduced the `?v=...` cache-buster pattern on
  `/css/site.css` and `/js/main.js` because `_headers` marks them as immutable.
  Current version: `20260423b`. (Commits `b215c86`, `6dbaef9`, `e58b0fd`.)
