/* ─── Barranquilla Guide — main.js ─────────────────────────────── */
(function () {
  'use strict';

  /* ── Nav scroll behavior ──────────────────────────────────────── */
  var nav = document.getElementById('site-nav');
  var isHero = document.querySelector('.hero');

  if (nav && isHero) {
    function updateNav() {
      if (window.scrollY > 60) {
        nav.classList.remove('site-nav--transparent');
        nav.classList.add('site-nav--solid');
      } else {
        nav.classList.add('site-nav--transparent');
        nav.classList.remove('site-nav--solid');
      }
    }
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

  /* ── Search overlay ───────────────────────────────────────────── */
  var searchToggle  = document.getElementById('search-toggle');
  var searchOverlay = document.getElementById('search-overlay');
  var searchClose   = document.getElementById('search-overlay-close');

  function openSearch() {
    searchOverlay.classList.add('is-open');
    searchOverlay.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    var input = searchOverlay.querySelector('input[type="search"]');
    if (input) setTimeout(function () { input.focus(); }, 100);
  }

  function closeSearch() {
    searchOverlay.classList.remove('is-open');
    searchOverlay.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  if (searchToggle)  searchToggle.addEventListener('click', openSearch);
  if (searchClose)   searchClose.addEventListener('click', closeSearch);

  /* ── Esc key closes all overlays ─────────────────────────────── */
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      closeSearch();
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

  /* ── Newsletter form ─────────────────────────────────────────── */
  var newsletterForm   = document.getElementById('newsletter-form');
  var newsletterStatus = document.getElementById('newsletter-status');

  if (newsletterForm) {
    newsletterForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var emailInput = newsletterForm.querySelector('input[type="email"]');
      var submitBtn  = newsletterForm.querySelector('.email-capture-submit');
      var email      = emailInput ? emailInput.value.trim() : '';

      if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        if (newsletterStatus) {
          newsletterStatus.textContent = 'Please enter a valid email address.';
          newsletterStatus.style.color = 'var(--coral)';
        }
        return;
      }

      // Show loading state
      submitBtn.textContent = 'Subscribing…';
      submitBtn.disabled = true;

      // AJAX to WordPress
      var data = new FormData();
      data.append('action', 'bg_subscribe');
      data.append('email', email);
      data.append('nonce', bgData.nonce);

      fetch(bgData.ajaxUrl, { method: 'POST', body: data })
        .then(function (r) { return r.json(); })
        .then(function (res) {
          if (res.success) {
            submitBtn.textContent = 'Subscribed ✓';
            submitBtn.style.background = '#2a7a4b';
            if (emailInput) emailInput.value = '';
            if (newsletterStatus) {
              newsletterStatus.textContent = 'You\'re in. Welcome to the guide.';
              newsletterStatus.style.color = '#2a7a4b';
            }
          } else {
            submitBtn.textContent = 'Subscribe';
            submitBtn.disabled = false;
            if (newsletterStatus) {
              newsletterStatus.textContent = res.data && res.data.message ? res.data.message : 'Something went wrong. Please try again.';
              newsletterStatus.style.color = 'var(--coral)';
            }
          }
        })
        .catch(function () {
          submitBtn.textContent = 'Subscribe';
          submitBtn.disabled = false;
        });
    });
  }

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

    // Collect candidate headings — prefer H2, include H3 as sub-items
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
      a.textContent = hd.textContent.replace(/\s+/g, ' ').trim();
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

})();


/* ── Contact form → Brevo (List #9) ─────────────────────────────── */
(function () {
  var contactForm = document.querySelector('form[action*="formspree"]');
  if (contactForm) {
    contactForm.addEventListener('submit', function () {
      var emailEl = contactForm.querySelector('[name="email"]');
      var nameEl  = contactForm.querySelector('[name="name"]');
      if (!emailEl || !emailEl.value) { return; }
      var d = new FormData();
      d.append('action', 'bg_contact_brevo');
      d.append('email', emailEl.value);
      d.append('name',  nameEl ? nameEl.value : '');
      d.append('nonce', bgData.nonce);
      fetch(bgData.ajaxUrl, { method: 'POST', body: d }).catch(function () {});
    });
  }
}());
