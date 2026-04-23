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
