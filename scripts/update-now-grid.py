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
MONTH_SHORT = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
               7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}


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


def extract_title_excerpt(html_path: Path) -> tuple[str, str]:
    text = html_path.read_text(encoding="utf-8")
    t = re.search(r"<title>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
    title = (t.group(1).strip() if t else "")
    # Strip " | Site Name" / " · suffix" / " – suffix" suffixes, but not a
    # regular hyphen (real titles use hyphens, e.g. "Week of May 4 - 2026").
    title = re.split(r"\s+[\|·–—]\s+", title)[0].strip()

    d = re.search(
        r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']',
        text, re.IGNORECASE,
    ) or re.search(
        r'<meta\s+property=["\']og:description["\']\s+content=["\']([^"\']+)["\']',
        text, re.IGNORECASE,
    )
    excerpt = (d.group(1).strip() if d else "")
    if len(excerpt) > 150:
        cut = excerpt[:147].rsplit(" ", 1)[0]
        excerpt = cut + "…"
    return title, excerpt


def render_card(slug: str, when: date, title: str, excerpt: str) -> str:
    return (
        '            <article class="now-card">\n'
        f'                <a href="/{slug}/">\n'
        '                    <div class="now-card-date">\n'
        f'                        <span class="now-card-day">{when.day}</span>\n'
        f'                        <span class="now-card-month">{MONTH_SHORT[when.month]}</span>\n'
        '                    </div>\n'
        '                    <div class="now-card-body">\n'
        f'                        <h3 class="now-card-title">{title}</h3>\n'
        f'                        <p class="now-card-excerpt">{excerpt}</p>\n'
        '                    </div>\n'
        '                </a>\n'
        '            </article>'
    )


def collect_posts():
    out = []
    for p in sorted(ROOT.glob("whats-happening-*/index.html")):
        slug = p.parent.name
        d = parse_slug(slug)
        if not d:
            continue
        title, excerpt = extract_title_excerpt(p)
        if not title:
            continue
        out.append((d, slug, title, excerpt))
    out.sort(key=lambda x: x[0], reverse=True)
    return out


def inject_markers_if_missing(text: str) -> str:
    """If the markers are missing, wrap the existing now-grid block in them."""
    if START_MARK in text and END_MARK in text:
        return text
    pattern = re.compile(
        r'(<div class="now-grid"[^>]*>)([\s\S]*?)(</article>\s*</div>)',
    )
    def wrap(m):
        return f"{m.group(1)}\n{START_MARK}\n{m.group(2)}{m.group(3).split('</article>')[0]}</article>\n{END_MARK}\n{m.group(3).split('</article>',1)[1]}"
    new, n = pattern.subn(wrap, text, count=1)
    if n != 1:
        raise SystemExit("could not find <div class=\"now-grid\"> ... last </article></div> to wrap")
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

    cards_html = "\n".join(render_card(slug, d, title, excerpt)
                           for d, slug, title, excerpt in top)

    text = INDEX.read_text(encoding="utf-8")
    text = inject_markers_if_missing(text)
    new_text = replace_between_markers(text, cards_html)

    print("Top 3 posts (newest first):")
    for d, slug, title, _ in top:
        print(f"  {d.isoformat()}  /{slug}/")
        print(f"    {title}")

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
