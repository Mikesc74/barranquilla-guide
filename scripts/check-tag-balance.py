#!/usr/bin/env python3
# check-tag-balance.py, bail if any HTML file passed on stdin (or via argv)
# has unbalanced <section>, <div>, <main>, <article>, <nav>, <header>, or
# <footer> open/close counts.
#
# Why: the 2026-05-13 "Strip Chatbase chatbot" commit deleted way more
# than chatbase, it cut the hero reading-paths nav, the scroll indicator,
# and the entire neighborhoods strip from index.html. The closing
# </section> for hero also went missing, breaking the homepage layout on
# desktop and mobile. This is a cheap structural check that would have
# caught it: opens != closes means somebody cut too much.
#
# Usage:
#   python3 scripts/check-tag-balance.py path/to/file.html [more...]
#   git diff --name-only @{u}..HEAD -- '*.html' | python3 scripts/check-tag-balance.py
#
# Exits 0 on balanced, 1 on any imbalance, 2 if no files to check.

import re, sys

TAGS = ("section", "div", "main", "article", "nav", "header", "footer")

# Files from argv or stdin
files = sys.argv[1:]
if not files:
    files = [line.strip() for line in sys.stdin if line.strip()]
files = [f for f in files if f.endswith(".html")]

if not files:
    print("[check-tag-balance] no HTML files to check, skipping")
    sys.exit(0)

errs = []
for f in files:
    try:
        s = open(f, encoding="utf-8").read()
    except FileNotFoundError:
        continue  # file was deleted, fine
    for tag in TAGS:
        opens  = len(re.findall(rf"<{tag}\b",  s))
        closes = len(re.findall(rf"</{tag}>", s))
        if opens != closes:
            errs.append(f"  {f}: <{tag}> opens={opens} closes={closes} (diff {opens - closes})")

if errs:
    print("\n[check-tag-balance] HTML TAG IMBALANCE\n", file=sys.stderr)
    for e in errs:
        print(e, file=sys.stderr)
    print(
        "\n  An open/close mismatch usually means a chunk got accidentally\n"
        "  deleted (e.g. a too-greedy regex replace). Fix the tag balance\n"
        "  before pushing, or run `git push --no-verify` to bypass.\n",
        file=sys.stderr,
    )
    sys.exit(1)

print(f"[check-tag-balance] OK · {len(files)} file(s) balanced")
