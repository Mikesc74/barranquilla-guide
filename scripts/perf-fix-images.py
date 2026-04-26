#!/usr/bin/env python3
"""
perf-fix-images.py — add decoding="async" to every <img> that lacks it.

Idempotent. Safe. decoding="async" is a paint-thread optimization with
no side-effects on layout or load priority — the browser decodes the
image off the main thread when ready.

Skips .bak files. Run from repo root.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Match an <img tag that doesn't already have decoding=
IMG_TAG = re.compile(r'<img\b([^>]*)>', re.IGNORECASE)


def patch_img(match: re.Match) -> str:
    attrs = match.group(1)
    if re.search(r'\bdecoding=', attrs, re.IGNORECASE):
        return match.group(0)
    # Insert decoding="async" right after <img
    return f'<img decoding="async"{attrs}>'


def fix_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    new_text, n = IMG_TAG.subn(patch_img, text)
    # subn returns total matches, not changes. Count actual diffs.
    if new_text == text:
        return 0
    path.write_text(new_text, encoding="utf-8")
    # Approximate change count: number of new "decoding=\"async\"" added.
    return new_text.count('decoding="async"') - text.count('decoding="async"')


def main() -> int:
    total_changed = 0
    files_changed = 0
    for f in ROOT.rglob("*.html"):
        if "/.git/" in str(f):
            continue
        if ".bak" in f.name:
            continue
        n = fix_file(f)
        if n > 0:
            files_changed += 1
            total_changed += n
            print(f"  {f.relative_to(ROOT)}: +{n} decoding attrs")
    print(f"\nDone. Added decoding=\"async\" to {total_changed} images across {files_changed} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
