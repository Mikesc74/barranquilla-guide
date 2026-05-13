#!/usr/bin/env python3
"""
Strip the Chatbase chatbot from every HTML page in this repo.

Removes:
  - the `<style id="chatbase-position-fix">…</style>` block (per-page)
  - the `<!-- Chatbase AI assistant -->` comment + bootstrap `<script>` block
  - the homepage hero `<div class="hero-chat-cta">…</div>` block (the one
    whose button calls window.chatbase('open'))

Idempotent. Run after porting from the WordPress export. Adapted from the
cartagena-guide version (cartagena-guide/scripts/remove-chatbot.py); both
sites used the same Chatbase bootstrap pattern.

CSS rules for `#chatbase-*` and `.hero-chat-cta*` in css/site.css are
removed by a separate sed pass (handled inline in the deploy script, not
here, since CSS state is more linear and easier to inspect manually).
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

STYLE_RE = re.compile(
    r'\s*<style id="chatbase-position-fix">.*?</style>',
    re.DOTALL,
)

SCRIPT_RE = re.compile(
    r'\s*(?:<!-- Chatbase AI assistant -->\s*)?<script>\s*\(function\(\)\{[^<]*?chatbase[^<]*?\}\)\(\);\s*</script>',
    re.DOTALL,
)

HERO_CTA_RE = re.compile(
    r'\s*<div class="hero-chat-cta">.*?</div>\s*</div>',
    re.DOTALL,
)


def main() -> int:
    touched = 0
    for path in ROOT.rglob("*.html"):
        # Skip node_modules and any nested vendor dirs if they exist
        if "/node_modules/" in str(path):
            continue
        text = path.read_text(encoding="utf-8")
        new = STYLE_RE.sub("", text)
        new = SCRIPT_RE.sub("", new)
        new = HERO_CTA_RE.sub("", new)
        if new != text:
            path.write_text(new, encoding="utf-8")
            touched += 1
    print(f"Stripped Chatbase from {touched} HTML files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
