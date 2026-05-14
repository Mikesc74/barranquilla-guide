#!/usr/bin/env python3
"""
add-search.py  —  One-shot installer for client-side search on barranquilla.guide.

What it does (idempotent, safe to re-run):
  1. Appends search CSS to css/site.css
  2. Appends search JS to js/main.js
  3. Injects search button into .nav-right on every HTML page
  4. Injects search button into mobile-nav on every HTML page
  5. Injects search overlay div after #mobile-nav on every HTML page
  6. Bumps the ?v= cache-buster on all HTML, site.css, and main.js references

Run from the repo root:
    python3 scripts/add-search.py

Then:
    python3 scripts/build-search-index.py
    git add -A && git status
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
OLD_VER   = '20260424a'
NEW_VER   = '20260514a'
DOMAIN    = 'barranquilla.guide'

# ── Sentinel used to detect already-processed files/assets ────────────────────
SENTINEL = 'js-search-open'
CSS_SENTINEL = '/* ── Search ── added by add-search.py'
JS_SENTINEL  = '/* ── Search ── added by add-search.py'

# ── HTML snippets ──────────────────────────────────────────────────────────────

NAV_BTN = (
    '<button class="nav-search-btn js-search-open" '
    'aria-label="Search" type="button">'
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'aria-hidden="true">'
    '<circle cx="11" cy="11" r="7"/>'
    '<line x1="16.5" y1="16.5" x2="22" y2="22"/>'
    '</svg></button>'
)

MOBILE_BTN = (
    '<button class="mobile-search-btn js-search-open" '
    'aria-label="Search" type="button">'
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'aria-hidden="true">'
    '<circle cx="11" cy="11" r="7"/>'
    '<line x1="16.5" y1="16.5" x2="22" y2="22"/>'
    '</svg> Search</button>'
)

OVERLAY = f'''\
<div class="search-overlay" id="search-overlay" role="dialog" aria-modal="true" aria-label="Search {DOMAIN}">
  <div class="search-overlay-inner">
    <div class="search-box">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><line x1="16.5" y1="16.5" x2="22" y2="22"/></svg>
      <input type="search" id="search-input" placeholder="Search {DOMAIN}&#8230;" autocomplete="off">
      <button class="search-close" id="search-close" aria-label="Close search">&times;</button>
    </div>
    <div class="search-results" id="search-results"><p class="search-hint">Type to search&hellip;</p></div>
  </div>
</div>'''

# ── CSS ────────────────────────────────────────────────────────────────────────

SEARCH_CSS = '''
/* ── Search ── added by add-search.py ────────────────────────────────────────*/

/* Desktop search button in .nav-right */
.nav-search-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px 8px;
  color: var(--white);
  display: flex;
  align-items: center;
  opacity: 0.75;
  transition: opacity 0.2s;
  border-radius: 4px;
  flex-shrink: 0;
}
.nav-search-btn:hover { opacity: 1; }
.nav-search-btn svg { width: 18px; height: 18px; stroke: currentColor; }

/* Mobile search button inside .mobile-nav */
.mobile-search-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  background: rgba(255, 255, 255, 0.07);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 4px;
  color: var(--white);
  cursor: pointer;
  font-family: inherit;
  font-size: 1rem;
  padding: 12px 20px;
  margin: 0 0 8px;
  text-align: left;
}
.mobile-search-btn svg { width: 18px; height: 18px; opacity: 0.65; flex-shrink: 0; }
.mobile-search-btn:hover { background: rgba(255, 255, 255, 0.13); }

/* Full-screen search overlay */
.search-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(27, 42, 71, 0.97);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 80px 16px 24px;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.18s;
}
.search-overlay.is-open {
  opacity: 1;
  pointer-events: all;
}
.search-overlay-inner {
  width: 100%;
  max-width: 640px;
}

/* Search input box */
.search-box {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  padding: 12px 16px;
}
.search-box svg {
  width: 20px;
  height: 20px;
  stroke: rgba(255, 255, 255, 0.5);
  flex-shrink: 0;
}
#search-input {
  flex: 1;
  background: none;
  border: none;
  outline: none;
  color: #fff;
  font-size: 1.125rem;
  font-family: inherit;
  min-width: 0;
}
#search-input::placeholder { color: rgba(255, 255, 255, 0.35); }
.search-close {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  font-size: 1.6rem;
  line-height: 1;
  padding: 0 4px;
  flex-shrink: 0;
}
.search-close:hover { color: #fff; }

/* Results list */
.search-results {
  margin-top: 10px;
  max-height: calc(100vh - 240px);
  overflow-y: auto;
}
.search-result {
  display: block;
  padding: 13px 16px;
  border-radius: 4px;
  text-decoration: none;
  transition: background 0.12s;
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
}
.search-result:last-child { border-bottom: none; }
.search-result:hover { background: rgba(255, 255, 255, 0.08); }
.search-result-label {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.09em;
  color: var(--coral);
  margin-bottom: 3px;
}
.search-result-title {
  font-family: 'Playfair Display', serif;
  font-size: 1.05rem;
  color: #fff;
  margin-bottom: 3px;
}
.search-result-desc {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.5);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.search-no-results {
  color: rgba(255, 255, 255, 0.5);
  padding: 24px 16px;
  font-size: 0.9rem;
}
.search-hint {
  color: rgba(255, 255, 255, 0.3);
  padding: 16px;
  font-size: 0.85rem;
}

/* ── End Search ───────────────────────────────────────────────────────────────*/
'''

# ── JavaScript ─────────────────────────────────────────────────────────────────

SEARCH_JS = r'''
/* ── Search ── added by add-search.py ────────────────────────────────────────*/
(function () {
  'use strict';

  var overlay  = document.getElementById('search-overlay');
  var input    = document.getElementById('search-input');
  var results  = document.getElementById('search-results');
  var closeBtn = document.getElementById('search-close');
  var openBtns = document.querySelectorAll('.js-search-open');

  if (!overlay || !input) return;

  var idx   = null;   // cached search index
  var timer = null;

  /* ── helpers ── */
  function esc(s) {
    return String(s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function scoreField(text, terms) {
    if (!text) return 0;
    var t = text.toLowerCase(), s = 0;
    for (var i = 0; i < terms.length; i++) {
      if (t.indexOf(terms[i]) !== -1) s++;
    }
    return s;
  }

  /* ── open / close ── */
  function open() {
    overlay.classList.add('is-open');
    document.body.style.overflow = 'hidden';
    input.focus();
    if (!idx) loadIndex();
  }

  function close() {
    overlay.classList.remove('is-open');
    document.body.style.overflow = '';
    input.value = '';
    results.innerHTML = '<p class="search-hint">Type to search…</p>';
  }

  /* ── index ── */
  function loadIndex() {
    fetch('/search-index.json')
      .then(function (r) { return r.json(); })
      .then(function (data) {
        idx = data;
        if (input.value.trim()) runSearch(input.value);
      })
      .catch(function () {
        results.innerHTML = '<p class="search-no-results">Search unavailable.</p>';
      });
  }

  /* ── search ── */
  function runSearch(query) {
    if (!idx) return;
    var q = query.toLowerCase().trim();
    if (!q) {
      results.innerHTML = '<p class="search-hint">Type to search…</p>';
      return;
    }
    var terms = q.split(/\s+/).filter(Boolean);

    var hits = idx
      .map(function (p) {
        var s = scoreField(p.title, terms)       * 10
              + scoreField(p.description, terms) * 5
              + scoreField(p.body, terms)         * 1;
        return { p: p, s: s };
      })
      .filter(function (r) { return r.s > 0; })
      .sort(function (a, b) { return b.s - a.s; })
      .slice(0, 8);

    if (!hits.length) {
      results.innerHTML =
        '<p class="search-no-results">No results for “' + esc(query) + '”.</p>';
      return;
    }

    results.innerHTML = hits.map(function (r) {
      var p = r.p;
      return (
        '<a href="' + esc(p.url) + '" class="search-result">' +
        (p.section
          ? '<div class="search-result-label">' + esc(p.section) + '</div>'
          : '') +
        '<div class="search-result-title">' + esc(p.title) + '</div>' +
        (p.description
          ? '<div class="search-result-desc">' + esc(p.description) + '</div>'
          : '') +
        '</a>'
      );
    }).join('');
  }

  /* ── events ── */
  openBtns.forEach(function (btn) { btn.addEventListener('click', open); });

  if (closeBtn) closeBtn.addEventListener('click', close);

  overlay.addEventListener('click', function (e) {
    if (e.target === overlay) close();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && overlay.classList.contains('is-open')) close();
  });

  input.addEventListener('input', function () {
    clearTimeout(timer);
    var val = input.value;
    timer = setTimeout(function () { runSearch(val); }, 180);
  });

  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') {
      var first = results.querySelector('.search-result');
      if (first) first.click();
    }
  });
}());
/* ── End Search ───────────────────────────────────────────────────────────────*/
'''

# ── HTML processing ─────────────────────────────────────────────────────────────

def mobile_nav_close_pos(html):
    """Return index just after the closing </div> of #mobile-nav."""
    pos = html.find('id="mobile-nav"')
    if pos == -1:
        return -1
    div_start = html.rfind('<div', 0, pos)
    i = html.find('>', div_start) + 1
    depth = 1
    while depth > 0 and i < len(html):
        nxt_open  = html.find('<div', i)
        nxt_close = html.find('</div>', i)
        if nxt_close == -1:
            break
        if nxt_open != -1 and nxt_open < nxt_close:
            depth += 1
            i = nxt_open + 4
        else:
            depth -= 1
            i = nxt_close + 6
    return i


def process_html(path):
    html = path.read_text(encoding='utf-8', errors='ignore')

    # Idempotency
    if SENTINEL in html:
        return False

    changed = False

    # 1. Insert search button as first child of .nav-right
    m = re.search(r'(<div class="nav-right">\s*)', html)
    if m:
        pos = m.end()
        html = html[:pos] + NAV_BTN + '\n      ' + html[pos:]
        changed = True

    # 2. Insert search button in mobile-nav, after the close button
    m = re.search(
        r'(<button class="mobile-nav-close"[^>]*>(?:.*?)</button>)',
        html,
        re.DOTALL,
    )
    if m:
        pos = m.end()
        html = html[:pos] + '\n  ' + MOBILE_BTN + html[pos:]
        changed = True

    # 3. Insert search overlay after #mobile-nav closing </div>
    end = mobile_nav_close_pos(html)
    if end != -1:
        html = html[:end] + '\n' + OVERLAY + html[end:]
        changed = True

    # 4. Bump cache-buster
    html = html.replace(f'?v={OLD_VER}', f'?v={NEW_VER}')

    if changed:
        path.write_text(html, encoding='utf-8')
    return changed


# ── Asset patching ─────────────────────────────────────────────────────────────

def patch_css():
    p = REPO_ROOT / 'css' / 'site.css'
    css = p.read_text(encoding='utf-8', errors='ignore')
    if CSS_SENTINEL in css:
        print('  css/site.css : search styles already present, skipping')
        return
    p.write_text(css + SEARCH_CSS, encoding='utf-8')
    print('  css/site.css : search styles appended')


def patch_js():
    p = REPO_ROOT / 'js' / 'main.js'
    js = p.read_text(encoding='utf-8', errors='ignore')
    if JS_SENTINEL in js:
        print('  js/main.js   : search code already present, skipping')
        return
    p.write_text(js + SEARCH_JS, encoding='utf-8')
    print('  js/main.js   : search code appended')


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print(f'add-search.py running on {REPO_ROOT}\n')
    patch_css()
    patch_js()

    updated = skipped = 0
    skip_dirs = {'.git', 'scripts', 'tools', '_scripts', '_shared'}

    for html_path in sorted(REPO_ROOT.rglob('index.html')):
        rel   = html_path.relative_to(REPO_ROOT)
        parts = rel.parts
        if parts and parts[0] in skip_dirs:
            continue
        if process_html(html_path):
            updated += 1
            print(f'  HTML updated : {rel}')
        else:
            skipped += 1

    print(f'\nHTML : {updated} updated, {skipped} already done')
    print(f'Cache-buster : {OLD_VER} -> {NEW_VER}')
    print('\nNext:')
    print('  python3 scripts/build-search-index.py')
    print('  git add -A && git status')


if __name__ == '__main__':
    main()
