#!/usr/bin/env python3
"""
Strip the WordPress ez-toc Table of Contents HTML from every page.

Each affected page ships a fully-rendered <div id="ez-toc-container">…</div>
block (avg 19 KB, max 87 KB) which js/main.js then hides via
`element.style.display = 'none'` and replaces with a custom sidebar TOC
(`.article-toc`). The inline block is dead weight on the wire.

Removes:
  - <div class="ez-toc-*" id="ez-toc-container">…</nav></div>
  - any immediately surrounding blank line(s)

Idempotent. Run from anywhere; resolves repo root from script location.
Same shape as scripts/remove-chatbot.py.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The opening div carries the `id="ez-toc-container"` attribute (the class
# changes between ez-toc plugin versions, the id does not). The block
# always closes with `</nav></div>` because the structure is:
#   <div id="ez-toc-container"> <div class="ez-toc-title-container">…</div>
#     <nav><ul class="ez-toc-list">…</ul></nav>
#   </div>
EZ_TOC_RE = re.compile(
    r'\s*<div[^>]*id="ez-toc-container"[^>]*>.*?</nav></div>',
    re.DOTALL,
)


def main() -> int:
    touched = 0
    bytes_saved = 0
    for path in ROOT.rglob("*.html"):
        # Skip vendored dirs
        if "/node_modules/" in str(path) or "/vendor/" in str(path):
            continue
        text = path.read_text(encoding="utf-8")
        new, n = EZ_TOC_RE.subn("", text)
        if n > 0 and new != text:
            bytes_saved += len(text) - len(new)
            path.write_text(new, encoding="utf-8")
            touched += 1
    print(f"Stripped ez-toc block from {touched} HTML files. "
          f"~{bytes_saved // 1024} KB removed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
