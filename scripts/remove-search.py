#!/usr/bin/env python3
"""
One-shot fan-out that strips the defunct WordPress search UI from every HTML
page and bumps the /css + /js cache-buster.

What it removes:
  1. The <button class="nav-search-btn">…</button> in every page's primary nav.
  2. The entire <div class="search-overlay">…</div> block (the full-screen
     search sheet triggered by the old magnifying-glass icon).
  3. Bumps '?v=20260423b' → '?v=20260423c' on every /css/site.css and
     /js/main.js reference, so browsers pick up the matching main.js edits
     (search wiring removed).

Idempotent: running it twice produces no change.

The hero-search form on index.html and the search-overlay open/close code in
js/main.js are handled separately (hand edits) so the chat CTA replacement
and the JS cleanup are reviewable.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

OLD_BUSTER = "?v=20260423b"
NEW_BUSTER = "?v=20260423c"

# The nav search button is a single multi-line block. Match its leading
# indentation through the closing </button> and trailing newline so the
# surrounding nav structure stays clean.
NAV_SEARCH_RE = re.compile(
    r'[ \t]*<button class="nav-search-btn"[^>]*>.*?</button>\s*\n',
    re.DOTALL,
)

OVERLAY_START = '<div class="search-overlay"'


def remove_balanced_div(html: str, start_marker: str) -> tuple[str, bool]:
    """
    Find `start_marker` in `html` (must be the opening of a <div ...> tag)
    and remove the whole balanced <div>…</div> block, including the full
    line it sits on (leading indent + trailing newline).
    Returns (new_html, removed).
    """
    idx = html.find(start_marker)
    if idx == -1:
        return html, False

    # Walk forward counting <div and </div> to find the matching close.
    pos = idx
    depth = 0
    open_tag = re.compile(r"<div[\s>]")
    close_tag = re.compile(r"</div>")
    while pos < len(html):
        o = open_tag.search(html, pos)
        c = close_tag.search(html, pos)
        if c is None:
            return html, False  # malformed — leave it alone
        if o is not None and o.start() < c.start():
            depth += 1
            pos = o.end()
        else:
            depth -= 1
            end = c.end()
            if depth == 0:
                # Extend `end` through trailing whitespace + newline.
                while end < len(html) and html[end] in " \t":
                    end += 1
                if end < len(html) and html[end] == "\n":
                    end += 1
                # Pull `idx` back to the start of its line so we don't leave
                # an orphan indent.
                line_start = html.rfind("\n", 0, idx)
                line_start = 0 if line_start == -1 else line_start + 1
                return html[:line_start] + html[end:], True
            pos = end
    return html, False


def process_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    text = original

    # 1. Nav search button
    text, _ = NAV_SEARCH_RE.subn("", text)

    # 2. Search overlay div (loop in case a page somehow has two; normally one)
    while True:
        text, removed = remove_balanced_div(text, OVERLAY_START)
        if not removed:
            break

    # 3. Cache-buster bump
    text = text.replace(OLD_BUSTER, NEW_BUSTER)

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> int:
    html_files = [
        p for p in ROOT.rglob("*.html")
        if ".git" not in p.parts
    ]
    changed = 0
    for f in html_files:
        if process_file(f):
            changed += 1
    print(f"Modified {changed} of {len(html_files)} HTML files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
