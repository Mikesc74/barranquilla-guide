/* ─── Barranquilla Guide, main.js ─────────────────────────────── */
(function () {
  'use strict';

  /* ── Nav scroll behavior ──────────────────────────────────────── */
  var nav = document.getElementById('site-nav');
  var isHero = document.querySelector('.hero');

  function updateNav() {
    if (!nav || !isHero) return;
    if (window.scrollY > 60) {
      nav.classList.remove('site-nav--transparent');
      nav.classList.add('site-nav--solid');
    } else {
      nav.classList.add('site-nav--transparent');
      nav.classList.remove('site-nav--solid');
    }
  }

  if (nav && isHero) {
    window.addEventListener('scroll', updateNav, { passive: true });
    updateNav();
  } else if (nav) {
    // On interior pages, always solid
    nav.classList.remove('site-nav--transparent');
    nav.classList.add('site-nav--solid');
  }

  /* ── Hero image zoom-out on load ──────────────────────────────── */
  var heroBg = document.getElementById('hero-bg');
  if (heroBg) {
    window.addEventListener('load', function () {
      heroBg.classList.add('is-loaded');
    });
  }

  /* ── Mobile nav ───────────────────────────────────────────────── */
  var hamburger  = document.getElementById('nav-hamburger');
  var mobileNav  = document.getElementById('mobile-nav');
  var mobileClose = document.getElementById('mobile-nav-close');

  function openMobileNav() {
    mobileNav.classList.add('is-open');
    mobileNav.setAttribute('aria-hidden', 'false');
    hamburger.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
  }

  function closeMobileNav() {
    mobileNav.classList.remove('is-open');
    mobileNav.setAttribute('aria-hidden', 'true');
    hamburger.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  }

  if (hamburger) hamburger.addEventListener('click', openMobileNav);
  if (mobileClose) mobileClose.addEventListener('click', closeMobileNav);

  /* ── Esc key closes the mobile nav ────────────────────────────── */
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      closeMobileNav();
    }
  });

  /* ── Neighborhood strip drag scroll (desktop) ────────────────── */
  var strip = document.getElementById('neighborhoods-strip');
  var wrap  = strip && strip.parentElement;

  if (wrap) {
    var isDown = false, startX, scrollLeft;

    wrap.addEventListener('mousedown', function (e) {
      isDown = true;
      startX = e.pageX - wrap.offsetLeft;
      scrollLeft = wrap.scrollLeft;
      wrap.style.cursor = 'grabbing';
    });

    wrap.addEventListener('mouseleave', function () {
      isDown = false;
      wrap.style.cursor = '';
    });

    wrap.addEventListener('mouseup', function () {
      isDown = false;
      wrap.style.cursor = '';
    });

    wrap.addEventListener('mousemove', function (e) {
      if (!isDown) return;
      e.preventDefault();
      var x = e.pageX - wrap.offsetLeft;
      wrap.scrollLeft = scrollLeft - (x - startX);
    });
  }

  /* ── Newsletter forms (canonical, multi-instance) ─────────────────
   * Every page can carry 1+ <form class="newsletter-form" data-city="..."
   * data-source="...">. We POST JSON to the guides-newsletter Worker
   * and show inline status.
   */
  document.querySelectorAll('form.newsletter-form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var city   = form.getAttribute('data-city')   || 'barranquilla';
      var source = form.getAttribute('data-source') || 'unknown';
      var input  = form.querySelector('input[type="email"]');
      var btn    = form.querySelector('button[type="submit"]');
      var status = form.querySelector('[role="status"], .newsletter-status, .email-capture-note');
      var email  = (input && input.value || '').trim();

      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        if (status) { status.textContent = 'Please enter a valid email address.'; status.style.color = 'var(--coral)'; }
        return;
      }

      var origBtn = btn ? btn.textContent : '';
      if (btn) { btn.textContent = 'Subscribing…'; btn.disabled = true; }

      fetch('https://newsletter.colguides.com/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify({ email: email, city: city, source: source })
      })
        .then(function (r) { return r.json().then(function (b) { return { ok: r.ok && b.ok !== false, body: b }; }); })
        .then(function (res) {
          if (res.ok) {
            var msg = res.body && res.body.state === 'already_confirmed'
              ? "You're already subscribed. Thanks!"
              : 'Check your inbox to confirm your email.';
            if (btn)   { btn.textContent = 'Subscribed ✓'; btn.style.background = '#2a7a4b'; }
            if (input) input.value = '';
            if (status){ status.textContent = msg; status.style.color = '#2a7a4b'; }
          } else {
            if (btn) { btn.textContent = origBtn || 'Subscribe'; btn.disabled = false; }
            var err = (res.body && res.body.error) || '';
            var human = err === 'invalid_email' ? 'Please enter a valid email address.'
                      : err === 'invalid_city'  ? 'Form configuration error. Please tell us.'
                      :                            'Something went wrong. Please try again.';
            if (status) { status.textContent = human; status.style.color = 'var(--coral)'; }
          }
        })
        .catch(function () {
          if (btn) { btn.textContent = origBtn || 'Subscribe'; btn.disabled = false; }
          if (status) { status.textContent = 'Network error. Please try again.'; status.style.color = 'var(--coral)'; }
        });
    });
  });

  /* ── Lazy load: trigger nav update on DOMContentLoaded ──────── */
  document.addEventListener('DOMContentLoaded', function () {
    if (nav && isHero) updateNav();
  });

  /* ── Auto-generated sticky Table of Contents on guide pages ──── */
  function slugify(str) {
    return String(str)
      .toLowerCase()
      .trim()
      .replace(/[\u2018\u2019\u201c\u201d]/g, '')
      .replace(/&[^;]+;/g, '')
      .replace(/[^a-z0-9\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-+|-+$/g, '');
  }

  function buildArticleToc() {
    var article = document.querySelector('article.single-article');
    if (!article) return;
    var body = article.querySelector('.article-body');
    if (!body) return;

    // Hide any legacy inline TOC blocks so the new sidebar is the only TOC
    var inlineToc = body.querySelectorAll('.toc, #ez-toc-container');
    for (var i = 0; i < inlineToc.length; i++) {
      inlineToc[i].style.display = 'none';
    }

    // Collect candidate headings, prefer H2, include H3 as sub-items
    var allHeadings = body.querySelectorAll('h2, h3');
    var headings = [];
    var usedIds = {};
    for (var j = 0; j < allHeadings.length; j++) {
      var h = allHeadings[j];
      // Skip headings that live inside a hidden TOC/legacy block
      if (h.closest('.toc') || h.closest('#ez-toc-container')) continue;
      var text = h.textContent.replace(/\s+/g, ' ').trim();
      if (!text) continue;
      if (!h.id) {
        var slug = slugify(text) || 'section';
        var base = slug;
        var n = 2;
        while (document.getElementById(slug) || usedIds[slug]) {
          slug = base + '-' + n++;
        }
        h.id = slug;
      }
      usedIds[h.id] = true;
      headings.push(h);
    }

    // Need enough H2s to justify a TOC
    var h2Count = 0;
    for (var k = 0; k < headings.length; k++) if (headings[k].tagName === 'H2') h2Count++;
    if (h2Count < 3) return;

    // Build the aside element
    var aside = document.createElement('aside');
    aside.className = 'article-toc';
    aside.setAttribute('aria-label', 'Table of contents');

    var isMobile = window.matchMedia('(max-width: 1024px)').matches;
    var listHost;
    if (isMobile) {
      var details = document.createElement('details');
      details.className = 'article-toc-details';
      details.open = false;
      var summary = document.createElement('summary');
      summary.textContent = 'Jump to section';
      details.appendChild(summary);
      aside.appendChild(details);
      listHost = details;
    } else {
      var title = document.createElement('div');
      title.className = 'article-toc-title';
      title.textContent = 'Jump to';
      aside.appendChild(title);
      listHost = aside;
    }

    var list = document.createElement('ol');
    list.className = 'article-toc-list';

    for (var m = 0; m < headings.length; m++) {
      var hd = headings[m];
      var li = document.createElement('li');
      li.className = hd.tagName === 'H3' ? 'toc-level-3' : 'toc-level-2';
      var a = document.createElement('a');
      a.href = '#' + hd.id;
      // Bilingual headings carry .pb-en/.pb-es spans; preserve them so the
      // TOC switches language with the body. Plain headings stay text-only.
      if (hd.querySelector('.pb-en, .pb-es')) {
        a.innerHTML = hd.innerHTML;
      } else {
        a.textContent = hd.textContent.replace(/\s+/g, ' ').trim();
      }
      a.setAttribute('data-target', hd.id);
      li.appendChild(a);
      list.appendChild(li);
    }
    listHost.appendChild(list);

    // Wrap .article-body and the aside in a grid layout
    var layout = document.createElement('div');
    layout.className = 'article-layout';
    body.parentNode.insertBefore(layout, body);
    layout.appendChild(aside);
    layout.appendChild(body);

    // Smooth scroll + collapse mobile TOC on click
    var tocLinks = list.querySelectorAll('a');
    tocLinks.forEach(function (link) {
      link.addEventListener('click', function () {
        if (isMobile) {
          var det = aside.querySelector('details');
          if (det) det.open = false;
        }
      });
    });

    // Active-section tracking: find the heading closest above the reading line
    var linkByIdMap = {};
    tocLinks.forEach(function (link) { linkByIdMap[link.getAttribute('data-target')] = link; });
    var currentActive = null;

    function setActive(id) {
      if (currentActive === id) return;
      if (currentActive && linkByIdMap[currentActive]) {
        linkByIdMap[currentActive].classList.remove('is-active');
      }
      if (id && linkByIdMap[id]) {
        linkByIdMap[id].classList.add('is-active');
        if (!isMobile) {
          var linkRect = linkByIdMap[id].getBoundingClientRect();
          var asideRect = aside.getBoundingClientRect();
          if (linkRect.top < asideRect.top || linkRect.bottom > asideRect.bottom) {
            linkByIdMap[id].scrollIntoView({ block: 'nearest' });
          }
        }
      }
      currentActive = id;
    }

    function updateActive() {
      // Reading line sits ~140px below the top of the viewport (just below the nav)
      var line = 140;
      var chosen = headings[0];
      for (var n = 0; n < headings.length; n++) {
        var top = headings[n].getBoundingClientRect().top;
        if (top - line <= 0) {
          chosen = headings[n];
        } else {
          break;
        }
      }
      // If the page is scrolled to the very bottom, activate the last heading
      if ((window.innerHeight + window.scrollY) >= (document.body.scrollHeight - 4)) {
        chosen = headings[headings.length - 1];
      }
      if (chosen) setActive(chosen.id);
    }

    var scrollTicking = false;
    window.addEventListener('scroll', function () {
      if (scrollTicking) return;
      scrollTicking = true;
      window.requestAnimationFrame(function () {
        updateActive();
        scrollTicking = false;
      });
    }, { passive: true });
    window.addEventListener('resize', updateActive);
    updateActive();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', buildArticleToc);
  } else {
    buildArticleToc();
  }

  /* ── Archive lazy-load: reveal posts in batches as user scrolls ── */
  function initArchiveLazyLoad() {
    var grid = document.querySelector('.archive-grid .posts-grid');
    if (!grid) return;

    // Only direct article-card children of the grid
    var allCards = grid.children;
    var cards = [];
    for (var i = 0; i < allCards.length; i++) {
      if (allCards[i].classList && allCards[i].classList.contains('article-card')) {
        cards.push(allCards[i]);
      }
    }

    var INITIAL = 6;
    var BATCH = 6;
    if (cards.length <= INITIAL) return; // not enough to lazy-load

    // Hide cards beyond the initial batch
    for (var j = INITIAL; j < cards.length; j++) {
      cards[j].classList.add('is-hidden-lazy');
    }
    var visibleCount = INITIAL;

    // Hide the empty static pagination div, replaced by infinite scroll
    var paginationEl = document.querySelector('.archive-grid .pagination');
    if (paginationEl) paginationEl.style.display = 'none';

    // Sentinel placed right after the grid; observed to trigger reveals
    var sentinel = document.createElement('div');
    sentinel.className = 'archive-lazy-sentinel';
    sentinel.setAttribute('aria-hidden', 'true');
    sentinel.style.height = '1px';
    grid.parentNode.insertBefore(sentinel, grid.nextSibling);

    var observer;

    function reveal() {
      var end = Math.min(visibleCount + BATCH, cards.length);
      for (var k = visibleCount; k < end; k++) {
        cards[k].classList.remove('is-hidden-lazy');
      }
      visibleCount = end;
      if (visibleCount >= cards.length) {
        if (observer) observer.disconnect();
        if (sentinel && sentinel.parentNode) sentinel.parentNode.removeChild(sentinel);
      }
    }

    if ('IntersectionObserver' in window) {
      observer = new IntersectionObserver(function (entries) {
        for (var i2 = 0; i2 < entries.length; i2++) {
          if (entries[i2].isIntersecting) {
            reveal();
            break;
          }
        }
      }, { rootMargin: '600px 0px' });
      observer.observe(sentinel);
    } else {
      // No IO support, just show everything
      for (var m = visibleCount; m < cards.length; m++) {
        cards[m].classList.remove('is-hidden-lazy');
      }
      if (sentinel.parentNode) sentinel.parentNode.removeChild(sentinel);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initArchiveLazyLoad);
  } else {
    initArchiveLazyLoad();
  }

})();

/* ── Language toggle EN/ES (mirrors medellin.guide) ────────────────
   Reads ?lang= URL param, else localStorage.bgg_lang, else navigator.language.
   Applies html.lang-en or html.lang-es; CSS handles visibility of .pb-en/.pb-es. */
(function () {
  var html = document.documentElement;
  var qs; try { qs = new URLSearchParams(location.search); } catch (e) { qs = null; }
  var picked = qs && qs.get('lang');
  if (!picked) { try { picked = localStorage.getItem('bgg_lang'); } catch (e) {} }
  if (!picked) {
    var nav = (navigator.language || 'en').toLowerCase();
    picked = nav.indexOf('es') === 0 ? 'es' : 'en';
  }
  if (picked !== 'es') picked = 'en';
  apply(picked);
  function apply(l) {
    html.classList.remove('lang-en', 'lang-es');
    html.classList.add('lang-' + l);
    html.setAttribute('lang', l);
    try { localStorage.setItem('bgg_lang', l); } catch (e) {}
    document.querySelectorAll('title[data-lang]').forEach(function (t) {
      if (t.getAttribute('data-lang') === l) document.title = t.textContent;
    });
    // Swap placeholders (and other attributes can't use .pb-en/.pb-es spans)
    document.querySelectorAll('[data-ph-en],[data-ph-es]').forEach(function (el) {
      var ph = el.getAttribute('data-ph-' + l);
      if (ph != null) el.setAttribute('placeholder', ph);
    });
  }
  document.querySelectorAll('.pb-langtog a').forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      var l = a.getAttribute('data-l');
      apply(l);
      try {
        var u = new URL(location.href);
        u.searchParams.set('lang', l);
        history.replaceState(null, '', u.toString());
      } catch (err) {}
    });
  });
})();

/* The legacy WordPress AJAX dual-write to Brevo was removed on
   2026-04-24. Contact + newsletter forms now go straight to
   Formspree. If we re-add an email-marketing integration, wire it
   server-side (Cloudflare Worker) instead of leaking it into the
   client. */

/* ── Search ── added by add-search.py ────────────────────────────────────────*/
(function () {
  'use strict';

  var overlay  = document.getElementById('search-overlay');
  var input    = document.getElementById('search-input');
  var results  = document.getElementById('search-results');
  var closeBtn = document.getElementById('search-close');
  var openBtns = document.querySelectorAll('.js-search-open');

  if (!overlay || !input) return;

  var idx   = null;
  var timer = null;

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
        '<p class="search-no-results">No results for "' + esc(query) + '".</p>';
      return;
    }

    results.innerHTML = hits.map(function (r) {
      var p = r.p;
      return (
        '<a href="' + esc(p.url) + '" class="search-result">' +
        (p.section ? '<div class="search-result-label">' + esc(p.section) + '</div>' : '') +
        '<div class="search-result-title">' + esc(p.title) + '</div>' +
        (p.description ? '<div class="search-result-desc">' + esc(p.description) + '</div>' : '') +
        '</a>'
      );
    }).join('');
  }

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

/* Local tips widget loader (2026-05-23) */
(function(){try{if(window.__tidbitsLoaded)return;window.__tidbitsLoaded=1;var s=document.createElement("script");s.defer=true;s.src="/js/tidbits.js?v=20260523a";(document.head||document.documentElement).appendChild(s);}catch(e){}})();
