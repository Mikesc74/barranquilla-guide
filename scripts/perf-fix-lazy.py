#!/usr/bin/env python3
"""
perf-fix-lazy.py — add loading="lazy" to clearly-below-fold <img> tags.

Idempotent. Conservative. Only targets two very-safe patterns:
  1. Gravatar author avatars (class="avatar")
  2. WordPress-export article body images (<figure class="wp-block-image">)

Article-hero images use loading="eager" by template convention and are
not touched.

Run from repo root.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Pattern: <img ... class="...avatar..." ...> without loading=
AVATAR = re.compile(
    r'(<img\b(?:(?!loading=)[^>])*\bclass="[^"]*\bavatar\b[^"]*"(?:(?!loading=)[^>])*)>',
    re.IGNORECASE,
)

# Pattern: an <img> inside a wp-block-image figure, without loading=
WP_FIGURE = re.compile(
    r'(<figure\s+class="wp-block-image[^"]*"[^>]*>\s*<img\b(?:(?!loading=)[^>])*)>',
    re.IGNORECASE,
)


def add_lazy(match: re.Match) -> str:
    return f'{match.group(1)} loading="lazy">'


def fix_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    out, a = AVATAR.subn(add_lazy, text)
    out, b = WP_FIGURE.subn(add_lazy, out)
    if out == text:
        return 0
    path.write_text(out, encoding="utf-8")
    return a + b


def main() -> int:
    total = 0
    files = 0
    for f in ROOT.rglob("*.html"):
        if "/.git/" in str(f) or ".bak" in f.name:
            continue
        n = fix_file(f)
        if n > 0:
            files += 1
            total += n
    print(f"Done. Added loading=\"lazy\" to {total} images across {files} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
