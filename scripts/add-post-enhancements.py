#!/usr/bin/env python3
"""Idempotently add the post.js <script> tag before </body> on every HTML page.

Usage:
    python3 add-post-enhancements.py <repo_root> <script_src>

Example:
    python3 add-post-enhancements.py ~/code/medellin-guide /post.js
    python3 add-post-enhancements.py ~/code/barranquilla-guide /js/post.js?v=20260522a

Safe to re-run: a file is skipped if it already references post.js.
"""
import os
import re
import sys

SENTINEL = "post.js"


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    root = os.path.abspath(os.path.expanduser(sys.argv[1]))
    src = sys.argv[2]
    tag = '<script src="%s" defer></script>' % src

    changed = skipped = 0
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirnames:
            dirnames.remove(".git")
        for name in filenames:
            if not name.endswith(".html"):
                continue
            fp = os.path.join(dirpath, name)
            with open(fp, "r", encoding="utf-8") as f:
                html = f.read()
            if SENTINEL in html:
                skipped += 1
                continue
            # find the LAST </body> (case-insensitive)
            matches = list(re.finditer(r"</body\s*>", html, re.IGNORECASE))
            if not matches:
                skipped += 1
                continue
            m = matches[-1]
            # preserve the indentation that precedes </body> on its line
            line_start = html.rfind("\n", 0, m.start()) + 1
            indent = re.match(r"[ \t]*", html[line_start:m.start()]).group(0)
            insertion = "%s%s\n" % (indent, tag)
            new_html = html[: m.start()] + insertion + html[m.start():]
            with open(fp, "w", encoding="utf-8") as f:
                f.write(new_html)
            changed += 1
    print("changed=%d skipped=%d  (%s)" % (changed, skipped, root))


if __name__ == "__main__":
    main()
