#!/usr/bin/env python3
"""
perf-fix-fonts.py — async-load Google Fonts CSS to kill mobile blank-window flash.

Idempotent. Re-runnable. Replaces every render-blocking
<link rel="stylesheet" href="https://fonts.googleapis.com/...">
with a print/onload pattern + <noscript> fallback.

Usage:  python3 scripts/perf-fix-fonts.py
Run from the repo root.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Match the existing render-blocking Google Fonts <link> in either attr order.
# Variant A: <link rel="stylesheet" href="https://fonts.googleapis.com/...">
# Variant B: <link href="https://fonts.googleapis.com/..." rel="stylesheet"/>
PATTERN_A = re.compile(
    r'<link\s+rel="stylesheet"\s+href="(https://fonts\.googleapis\.com/css2\?[^"]+)"\s*/?>',
    re.IGNORECASE,
)
PATTERN_B = re.compile(
    r'<link\s+href="(https://fonts\.googleapis\.com/css2\?[^"]+)"\s+rel="stylesheet"\s*/?>',
    re.IGNORECASE,
)

# Sentinel so we never double-rewrite a page.
SENTINEL = "<!-- PERF: async fonts -->"


def replacement(match: re.Match) -> str:
    # Normalize HTML-encoded ampersands — they're valid in href, but cleaner once.
    href = match.group(1)
    return (
        f'{SENTINEL}\n'
        f'  <link rel="preload" as="style" href="{href}">\n'
        f'  <link rel="stylesheet" href="{href}" media="print" onload="this.media=\'all\'">\n'
        f'  <noscript><link rel="stylesheet" href="{href}"></noscript>'
    )


def fix_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if SENTINEL in text:
        return False  # already done
    new_text, n = PATTERN_A.subn(replacement, text, count=1)
    if n == 0:
        new_text, n = PATTERN_B.subn(replacement, text, count=1)
    if n == 0:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    changed = 0
    skipped = 0
    files = list(ROOT.rglob("*.html"))
    for f in files:
        if "/.git/" in str(f):
            continue
        if fix_file(f):
            changed += 1
            print(f"  fixed: {f.relative_to(ROOT)}")
        else:
            skipped += 1
    print(f"\nDone. Fixed {changed}, skipped {skipped} (already done or no fonts link).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
