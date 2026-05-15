#!/usr/bin/env python3
"""
Transcode referenced JPG/PNG images under /img/ to WebP siblings, and
swap HTML refs to use the .webp version when the WebP is smaller.

Usage:
  scripts/transcode-webp.py [N]
    Process the N largest referenced JPG/PNG files lacking a webp sibling.
    Default N=50. Re-run to chip away at the next chunk.

Idempotent: skips files that already have a same-stem .webp.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / 'img'

def referenced_set():
    """Build the set of /img/X paths that any text file references."""
    scan_exts = {'.html', '.css', '.js', '.xml', '.json', '.md', '.svg'}
    chunks = []
    for r, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', 'vendor', 'img', 'fonts')]
        for f in files:
            if Path(f).suffix.lower() not in scan_exts:
                continue
            try:
                chunks.append(Path(r, f).read_text(encoding='utf-8', errors='ignore'))
            except Exception:
                pass
    return '\n'.join(chunks)

def candidates(blob, threshold=100*1024):
    out = []
    for f in os.listdir(IMG):
        p = IMG / f
        if not p.is_file():
            continue
        ext = p.suffix.lower()
        if ext not in ('.jpg', '.jpeg', '.png'):
            continue
        sz = p.stat().st_size
        if sz < threshold:
            continue
        if f'/img/{f}' not in blob and f'img/{f}' not in blob:
            continue
        webp = IMG / (p.stem + '.webp')
        if webp.exists():
            continue
        out.append((sz, f))
    out.sort(reverse=True)
    return out

def transcode(filename, quality=80):
    src = IMG / filename
    dst = IMG / (Path(filename).stem + '.webp')
    res = subprocess.run(
        ['convert', str(src), '-quality', str(quality), str(dst)],
        capture_output=True,
    )
    if res.returncode != 0 or not dst.exists():
        return None
    new_size = dst.stat().st_size
    old_size = src.stat().st_size
    return old_size, new_size

def swap_refs(filename, webp_name):
    """Replace /img/FILENAME with /img/WEBP across HTML files. Returns
    number of files touched."""
    touched = 0
    for r, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', 'vendor', 'img', 'fonts')]
        for f in files:
            if Path(f).suffix.lower() != '.html':
                continue
            path = Path(r, f)
            try:
                text = path.read_text(encoding='utf-8')
            except Exception:
                continue
            new = text.replace(f'/img/{filename}', f'/img/{webp_name}')
            if new != text:
                path.write_text(new, encoding='utf-8')
                touched += 1
    return touched

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    blob = referenced_set()
    cands = candidates(blob)
    if not cands:
        print('Nothing to do, all referenced images already have webp siblings.')
        return 0

    print(f'Found {len(cands)} candidates. Processing top {min(n, len(cands))}.')
    total_orig = 0
    total_new = 0
    reverted = 0
    skipped_unwritable = 0
    for sz, filename in cands[:n]:
        result = transcode(filename)
        if not result:
            print(f'  FAIL {filename}')
            continue
        old, new = result
        webp_name = Path(filename).stem + '.webp'
        if new < old:
            # WebP is a win; swap HTML refs
            n_files = swap_refs(filename, webp_name)
            total_orig += old
            total_new += new
            print(f'  {filename}: {old/1024:.0f} KB → {new/1024:.0f} KB ({100*(1-new/old):.0f}% off, {n_files} pages updated)')
        else:
            # WebP came out larger; don't swap. Try to remove the webp file.
            try:
                (IMG / webp_name).unlink()
            except OSError:
                skipped_unwritable += 1
            reverted += 1

    print()
    if total_orig:
        print(f'Total: {total_orig/1024/1024:.1f} MB → {total_new/1024/1024:.1f} MB ({100*(1-total_new/total_orig):.0f}% off)')
    if reverted:
        print(f'Skipped (webp >= original): {reverted}, {skipped_unwritable} webp files left over')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
