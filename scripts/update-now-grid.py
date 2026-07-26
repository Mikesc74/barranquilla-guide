#!/usr/bin/env python3
"""
Rewrite the homepage "What's Happening" now-grid to show the 3 newest
/whats-happening-*/ posts. Day badge = week-start (Monday) date.

Run with no args from anywhere in the repo:
  python3 scripts/update-now-grid.py
Add --dry-run to preview without writing.

Slug formats handled:
  whats-happening-in-barranquilla-week-of-<month>-<day>-<year>   (canonical)
  whats-happening-barranquilla-<month>-<day>-<year>              (legacy)

Matches the site's actual bilingual card markup (pb-en/pb-es spans inside
a plain <a class="now-card">), NOT a generic single-language template.
Pulls the EN + ES <meta name="description" data-lang="..."> pairs from
each post for the excerpt; the day/month/title text is generated directly
from the post's date so it never depends on a <title> format matching.

The script looks for the markers in index.html:
  <!-- now-grid:auto -->
  <!-- /now-grid:auto -->
If absent, it injects them on first run around the existing now-grid block.
"""
from __future__ import annotations
import re, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

START_MARK = "<!-- now-grid:auto -->"
END_MARK   = "<!-- /now-grid:auto -->"

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}
MONTH_EN_FULL = {1: "January", 2: "February", 3: "March", 4: "April",
                 5: "May", 6: "June", 7: "July", 8: "August",
                 9: "September", 10: "October", 11: "November", 12: "December"}
MONTH_EN_SHORT = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
                  7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}
MONTH_ES_FULL = {1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
                 5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
                 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"}
MONTH_ES_SHORT = {1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
                  7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"}


def parse_slug(slug: str):
    """Return week-start date for a whats-happening-* slug, or None."""
    m = re.search(r"week-of-([a-z]+)-(\d{1,2})-(\d{4})$", slug)
    if not m:
        m = re.search(r"-([a-z]+)-(\d{1,2})-(\d{4})$", slug)
    if not m:
        return None
    mo = MONTHS.get(m.group(1).lower())
    if not mo:
        return None
    try:
        return date(int(m.group(3)), mo, int(m.group(2)))
    except ValueError:
        return None


def extract_excerpt(html_path: Path, lang: str) -> str:
    """Pull the <meta name="description" data-lang="{lang}" content="..."> text,
    regardless of attribute order. Falls back to og:description (EN only)."""
    text = html_path.read_text(encoding="utf-8")
    excerpt = ""
    for m in re.finditer(r"<meta\b[^>]*>", text, re.IGNORECASE):
        tag = m.group(0)
        if 'name="description"' not in tag and "name='description'" not in tag:
            continue
        dl = re.search(r'data-lang="([a-z]{2})"', tag, re.IGNORECASE)
        if not dl or dl.group(1).lower() != lang:
            continue
        c = re.search(r'content="([^"]*)"', tag, re.IGNORECASE)
        if c:
            excerpt = c.group(1).strip()
            break
    if not excerpt and lang == "en":
        m = re.search(
            r'<meta(?=[^>]*property="og:description")[^>]*content="([^"]*)"',
            text, re.IGNORECASE,
        )
        if m:
            excerpt = m.group(1).strip()

    if len(excerpt) > 190:
        cut = excerpt[:187].rsplit(" ", 1)[0]
        excerpt = cut + "…"
    return excerpt


def render_card(slug: str, when: date, excerpt_en: str, excerpt_es: str) -> str:
    day_str = f"{when.day:02d}"
    m_en = MONTH_EN_SHORT[when.month]
    m_es = MONTH_ES_SHORT[when.month]
    title_en = f"Week of {MONTH_EN_FULL[when.month]} {when.day}, {when.year}"
    title_es = f"Semana del {when.day} de {MONTH_ES_FULL[when.month]} de {when.year}"
    return (
        f'  <a href="/{slug}/" class="now-card">\n'
        f'    <div class="now-date"><span class="d">{day_str}</span>'
        f'<span class="m"><span class="pb-en">{m_en}</span><span class="pb-es">{m_es}</span></span></div>\n'
        f'    <div><h3><span class="pb-en">{title_en}</span><span class="pb-es">{title_es}</span></h3>'
        f'<p><span class="pb-en">{excerpt_en}</span><span class="pb-es">{excerpt_es}</span></p></div>\n'
        f'  </a>'
    )


def collect_posts():
    out = []
    for p in sorted(ROOT.glob("whats-happening-*/index.html")):
        slug = p.parent.name
        d = parse_slug(slug)
        if not d:
            continue
        excerpt_en = extract_excerpt(p, "en")
        excerpt_es = extract_excerpt(p, "es") or excerpt_en
        if not excerpt_en:
            continue
        out.append((d, slug, excerpt_en, excerpt_es))
    out.sort(key=lambda x: x[0], reverse=True)
    return out


def inject_markers_if_missing(text: str) -> str:
    """If the markers are missing, wrap the existing now-grid block in them."""
    if START_MARK in text and END_MARK in text:
        return text
    pattern = re.compile(
        r'(<div class="now-grid">\n)([\s\S]*?)(\n</div>\n</div></section>)',
    )
    def wrap(m):
        return f"{m.group(1)}{START_MARK}\n{m.group(2)}\n{END_MARK}{m.group(3)}"
    new, n = pattern.subn(wrap, text, count=1)
    if n != 1:
        raise SystemExit('could not find <div class="now-grid"> block to wrap with markers')
    return new


def replace_between_markers(text: str, cards_html: str) -> str:
    if START_MARK not in text or END_MARK not in text:
        raise SystemExit("markers missing even after injection, abort")
    before, _, rest = text.partition(START_MARK)
    middle, _, after = rest.partition(END_MARK)
    return f"{before}{START_MARK}\n{cards_html}\n{END_MARK}{after}"


def main():
    dry_run = "--dry-run" in sys.argv

    posts = collect_posts()
    if len(posts) < 1:
        print("no whats-happening posts found", file=sys.stderr)
        sys.exit(2)
    top = posts[:3]

    cards_html = "\n".join(render_card(slug, d, exc_en, exc_es)
                           for d, slug, exc_en, exc_es in top)

    text = INDEX.read_text(encoding="utf-8")
    text = inject_markers_if_missing(text)
    new_text = replace_between_markers(text, cards_html)

    print("Top 3 posts (newest first):")
    for d, slug, exc_en, _ in top:
        print(f"  {d.isoformat()}  /{slug}/")
        print(f"    {exc_en[:80]}")

    if dry_run:
        print("\n[dry-run] index.html not written")
        return

    if new_text == INDEX.read_text(encoding="utf-8"):
        print("\nno change (homepage already up to date)")
        return

    INDEX.write_text(new_text, encoding="utf-8")
    print("\nindex.html updated.")


if __name__ == "__main__":
    main()
