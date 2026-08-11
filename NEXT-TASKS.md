# NEXT-TASKS.md — barranquilla.guide

Ranked PROPOSE backlog from the Watchman audit. Highest estimated impact first.
Everything here is work **Claude implements once approved** — there is no other
implementer. Nothing in this file has been applied.

Generated 2026-08-08 (Watchman run 1). Updated 2026-08-10 (Watchman run 2).
See `AUDIT-LOG.md` for what was already auto-fixed this run.

---

## NEW PROPOSALS FROM RUN 2 (2026-08-10)

### B1. CRITICAL: Zero monetization infrastructure deployed (Section 9)

**Impact: HIGHEST revenue opportunity**

Unlike medellin-guide (23 pages with affiliate links), barranquilla.guide has:
- 0 affiliate links site-wide (Viator, Booking, GetYourGuide)
- 0 partner-widget deployments
- 0 gated PDF lead-magnets
- 0 conversion event tracking

**This site is completely unmonetized despite having the same infrastructure.**

**Quick wins:**
1. Deploy Viator/GetYourGuide affiliate links to all tour/day-trip guides
   (tours-medellin equivalent, day-trips-from-barranquilla, etc.)
2. Deploy partner widgets to medical/visa guides (doctor, dentist, visa categories)
3. Wire up GA4 conversion events
4. Consider gated PDFs for 3-5 high-value articles

**Effort:** ~3-4 hours (product-code lookups already done in August 2026 per
CLAUDE.md, just need to add links to barranquilla pages)

---

### B2. CRITICAL: GDPR compliance risk (Section 10)

**Impact: HIGH regulatory risk** — Same as medellin-guide.

97/139 pages fire GA4 without user consent, violating GDPR/CCPA.

**Fix:** Deploy existing consent.js pattern site-wide.

**Effort:** ~30 minutes

---

### B3. Meta title truncation (91/139 pages >60 chars) — Section 2

**Impact: Moderate CTR loss** — Worst of all 3 sites.

**Decision needed:** Whether to rewrite titles blindly or wait for GSC data to
target high-opportunity keywords first.

---

### B4. 10 pages missing image width/height (CLS ranking factor) — Section 6

**Impact: Moderate** — Core Web Vitals ranking factor.

**Effort:** ~30 minutes (scripted dimension extraction + verify)

---

### NEW: M1. Card image duplicates (Section 16 audit)

**Moderate priority:** Three image-reuse issues found:

1. **`og-carnival1.webp` used 5 times** on unrelated page types
   - `/about` (About page)
   - `/advertise` (Advertise page)
   - `/category/now` (News/weekly posts archive)
   - `/city-map` (Map page)
   - `/neighborhoods` (Neighborhoods archive)

   These are all different page purposes; each should have its own image. Carnival imagery
   only makes sense for entertainment/events context, not for site navigation pages.

   **Fix:** Replace with distinct images:
   - /about → about/team/city photo
   - /advertise → advertising/business context
   - /category/now → news/current events generic
   - /city-map → map/city layout
   - /neighborhoods → residential/district imagery

2. **`barranquilla-city-panoramic-view.jpg` used 2 times** on different weekly updates.
   Weekly posts are time-sensitive and each week's news is distinct—should not share
   the exact same image even if reusing a generic city view. Minor issue.

3. **`gran-malecon-barranquilla-waterfront.jpg` used 2 times** on different weekly updates.
   Same as above—two different weeks, two different story sets, should have distinct imagery.

**Impact:** Medium—primarily affects non-traffic-driving utility pages and weekly posts.
5 image replacements needed.

**Next step:** Source distinct images for the use cases above, update og:image links.

---

### 1. Meta titles are too long on 91 pages — direct CTR loss on traffic you already have

Google truncates titles past roughly 60 characters, so on 91 of 139 pages
the tail of the headline never reaches the searcher. Worst offenders run 70–104
characters. This is not a bug — the titles are accurate — it is lost click-through
on pages that are *already ranking*, which makes it some of the cheapest available
traffic on the site.

**Why it's PROPOSE, not AUTO-FIX:** rewriting a title on an already-indexed page is
a real editorial change with ranking consequences, and it needs a judgment call on
which keyword gets the front-loaded slot.

**Proposed approach:** rather than rewriting all 91 blind, start with the pages
that already rank well enough that a better title pays off immediately. That
targeting needs GSC impression/position data (see FLAG in `AUDIT-LOG.md`). If you
can export GSC performance to the repo, Claude can rank the list properly and
rewrite the top 15–20 first. Without it, Claude can still do a
sensible-but-untargeted pass on the longest offenders.

### 2. Meta descriptions are too long on 33 pages

Same failure mode, same tier. Several run 200–348 characters — well over double the
useful limit — so Google either truncates hard or rewrites the snippet itself. The
weekly "What's happening" posts are consistently the worst, which suggests the
weekly-post template is the actual thing to fix, not each post individually.
Fixing the template stops the bleed going forward and is a much smaller change.

### 3. Unbalanced block-level tags

`supermarkets-grocery-shopping-in-barranquilla-the-complete-guide-2026/index.html` (li 166/167), `colombian-citizenship-exam-study-guide/index.html` (ul 83/82, li 540/539), `city-map/index.html` (div 33/32)

Browsers silently paper over this, but it can corrupt layout, break the
bilingual toggle, and confuse Google's DOM parse. Each needs an individual repair
plus a visual check.

### 4. 9 orphan pages (live and indexable, zero internal links pointing at them)

Nothing on the site links to these, so they receive no internal link equity and are
reachable only via sitemap or direct URL. Most are retired `noindex` redirect stubs
and are correctly orphaned — **but not all of them are**, and the ones that aren't
are quietly invisible. Needs a page-by-page call: link it properly into the nav/hub
structure, or retire it deliberately.

### 5. 10 pages have images without explicit `width`/`height`

Causes cumulative layout shift (a Core Web Vitals ranking factor). Mechanical to
fix, but it requires reading real pixel dimensions off each file on disk to avoid
setting a wrong aspect ratio — so it is a scripted pass worth doing deliberately
rather than a blind find-and-replace.

### 6. 9 pages have no `og:image`

They share to Facebook/WhatsApp/LinkedIn/iMessage with no preview image at all,
which measurably suppresses click-through on shared links. Most are utility pages
(404, legal, retired stubs) where it genuinely does not matter — but the live ones
should inherit the site default. Needs a decision on which get a real bespoke image
versus the default.

### 7. Five outbound links still use plain `http://`

`procrear.com.co`, `unesdoc.unesco.org`, `atcbaq.com`, `drjorgedaes.com`,
`lagosdecaujaral.com`. Each needs its HTTPS support verified before switching —
blindly rewriting to `https://` would create dead links if the host doesn't support
it. Also worth checking: `www.fvap.gov` (used twice) looks like a malformed
hostname and may already be dead.

### 8. The bilingual single-file `data-lang` pattern itself (biggest open structural question)

Both language versions of every article live in one HTML file, shown/hidden with
CSS. Google therefore sees one URL containing two full articles in two languages,
with no `hreflang`, no separate URLs, and no way to rank the Spanish version
independently. `AUDIT-CHECKLIST.md` itself flags this as *"possibly the largest
structural issue."* This run confirmed the mechanics but did **not** attempt to
quantify the damage, which needs real search data.

This is a genuine fork in the road — splitting to `/es/` URLs would be a large,
irreversible restructure of an already-indexed site. **Recommend deciding this one
deliberately rather than letting it drift.** Claude can prepare a written
options/impact analysis first, before anything is touched.

---

## Not yet audited (no proposals yet)

Sections 6 (performance), 7 (mobile/UX), 8 (accessibility), 9 (conversion &
monetization), 11 (competitive/keyword), 12 (off-page/authority), 13 (security &
legal), 15 (editorial ops). Next run starts at section 4.
