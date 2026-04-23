#!/usr/bin/env python3
"""
Walk every HTML file in the repo and ensure the Open Graph image metadata is
complete. Facebook, LinkedIn, WhatsApp, Slack, and the rest expect to see
image dimensions declared alongside og:image; without them, the first scrape
often fails silently and the share preview never renders an image.

For each HTML file this script:
  - Finds the <meta property="og:image" ...> tag.
  - Reads the real dimensions off the image on disk.
  - Inserts (if missing) og:image:secure_url, og:image:type, og:image:width,
    og:image:height, og:image:alt, and twitter:image alongside it.

Idempotent: running it twice produces no change.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Optional

try:
    from PIL import Image
except ImportError:
    print("Install Pillow first:  pip install pillow --break-system-packages", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
SITE_ORIGIN = "https://barranquilla.guide"

OG_IMAGE_RE = re.compile(
    r'<meta\s+property="og:image"\s+content="([^"]+)"\s*/?>',
    re.IGNORECASE,
)
HAS_OG_WIDTH = re.compile(r'property="og:image:width"', re.IGNORECASE)
HAS_TW_IMAGE = re.compile(r'name="twitter:image"', re.IGNORECASE)


def dims_for(url: str) -> Optional[tuple[int, int]]:
    """Map a site-absolute og:image URL to local disk dimensions."""
    if url.startswith(SITE_ORIGIN):
        rel = url[len(SITE_ORIGIN):]
    else:
        rel = url
    rel = rel.lstrip("/")
    path = ROOT / rel
    if not path.exists():
        return None
    try:
        with Image.open(path) as im:
            return im.size
    except Exception:
        return None


def mime_for(url: str) -> str:
    lower = url.lower()
    if lower.endswith(".png"):
        return "image/png"
    if lower.endswith(".webp"):
        return "image/webp"
    if lower.endswith(".gif"):
        return "image/gif"
    return "image/jpeg"


def extract_alt(html: str) -> str:
    """Use og:title as alt; fall back to <title>."""
    m = re.search(r'<meta\s+property="og:title"\s+content="([^"]+)"', html, re.IGNORECASE)
    if m:
        return m.group(1)
    m = re.search(r"<title>([^<]+)</title>", html, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return ""


def process(path: Path) -> str:
    html = path.read_text(encoding="utf-8")
    m = OG_IMAGE_RE.search(html)
    if not m:
        return "skip (no og:image)"

    already_width = bool(HAS_OG_WIDTH.search(html))
    already_tw = bool(HAS_TW_IMAGE.search(html))
    if already_width and already_tw:
        return "skip (already complete)"

    url = m.group(1)
    dims = dims_for(url)
    if not dims:
        return f"skip (image not found locally: {url})"
    width, height = dims
    mime = mime_for(url)
    alt = extract_alt(html).replace('"', "&quot;")

    indent = "  "  # match the two-space indent used throughout the file

    new_tags = []
    if not already_width:
        new_tags.extend([
            f'{indent}<meta property="og:image:secure_url" content="{url}" />',
            f'{indent}<meta property="og:image:type" content="{mime}" />',
            f'{indent}<meta property="og:image:width" content="{width}" />',
            f'{indent}<meta property="og:image:height" content="{height}" />',
        ])
        if alt:
            new_tags.append(f'{indent}<meta property="og:image:alt" content="{alt}" />')
    if not already_tw:
        new_tags.append(f'{indent}<meta name="twitter:image" content="{url}" />')

    if not new_tags:
        return "skip"

    original_tag = m.group(0)
    replacement = original_tag + "\n" + "\n".join(new_tags)
    new_html = html.replace(original_tag, replacement, 1)
    path.write_text(new_html, encoding="utf-8")
    return f"updated ({width}x{height})"


def main() -> int:
    changed = 0
    skipped = 0
    for html_path in ROOT.rglob("*.html"):
        if ".git" in html_path.parts:
            continue
        result = process(html_path)
        rel = html_path.relative_to(ROOT)
        print(f"  {rel}: {result}")
        if result.startswith("updated"):
            changed += 1
        else:
            skipped += 1
    print(f"\nChanged {changed} files, skipped {skipped}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
