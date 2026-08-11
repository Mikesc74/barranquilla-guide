/**
 * barranquilla.guide, Cookie consent banner (strict opt-in / GDPR-grade)
 *
 * Drop this file at /consent.js on Cloudflare Pages and load it FIRST in <head>.
 * It blocks Google Analytics until the user consents.
 *
 * API (from anywhere on the page):
 *   window.mgConsent.open()         // reopen the preferences modal
 *   window.mgConsent.get()          // { analytics: bool, ts: number }
 *   window.mgConsent.reset()        // clear stored choice (for testing)
 *   window.addEventListener('mg-consent-change', e => {...})
 *
 * Integration pattern: remove any hard-coded GA4 script from index.html.
 * This script re-injects it only after the user consents.
 *
 * Note: the Catalina chat widget at catalina.barranquilla.guide/widget.js loads
 * unconditionally (no consent gating), it only stores a transient session id
 * in sessionStorage, which doesn't require consent under GDPR's strictly-
 * necessary exemption.
 */
(function () {
  'use strict';

  // ====== Config ======
  var CONSENT_KEY = 'bg_consent';
  var CONSENT_VERSION = 2; // bump to re-prompt all users after a policy change
  var GA_MEASUREMENT_ID = 'G-FKFW8ZQJPN';

  // ====== Utilities ======
  function loadChoice() {
    try {
      var raw = localStorage.getItem(CONSENT_KEY);
      if (!raw) return null;
      var parsed = JSON.parse(raw);
      if (parsed.v !== CONSENT_VERSION) return null; // re-prompt after policy change
      return parsed;
    } catch (e) { return null; }
  }

  function saveChoice(analytics) {
    var data = {
      v: CONSENT_VERSION,
      analytics: !!analytics,
      ts: Date.now()
    };
    try { localStorage.setItem(CONSENT_KEY, JSON.stringify(data)); } catch (e) {}
    return data;
  }

  function isGpcOrDnt() {
    try {
      if (navigator.globalPrivacyControl === true) return true;
      if (navigator.doNotTrack === '1' || window.doNotTrack === '1') return true;
    } catch (e) {}
    return false;
  }

  function dispatchChange(choice) {
    try {
      window.dispatchEvent(new CustomEvent('bg-consent-change', { detail: choice }));
    } catch (e) {}
  }

  // ====== Script loaders ======
  var loaded = { ga: false };

  // Bot guard: skip GA entirely for automated/headless agents so the property
  // reflects real human traffic. GA4 also has a built-in "known bots" filter,
  // this just catches the headless cases that slip through.
  function looksLikeBot() {
    try {
      if (navigator.webdriver === true) return true;
      var ua = (navigator.userAgent || '').toLowerCase();
      if (!ua) return true;
      // Common headless / crawler signatures.
      var bots = ['headlesschrome', 'phantomjs', 'slimerjs', 'electron',
        'puppeteer', 'playwright', 'selenium', 'lighthouse', 'pagespeed',
        'gtmetrix', 'pingdom', 'uptimerobot', 'wpt.', 'webpagetest',
        'bot', 'spider', 'crawler', 'crawling', 'scraper'];
      for (var i = 0; i < bots.length; i++) {
        if (ua.indexOf(bots[i]) !== -1) return true;
      }
      // No language ≈ bot.
      if (!navigator.languages || navigator.languages.length === 0) return true;
    } catch (e) {}
    return false;
  }

  function wireEngagementEvents() {
    if (!window.gtag) return;
    // Scroll depth: 25 / 50 / 75 / 100.
    var seenScroll = {};
    var thresholds = [25, 50, 75, 100];
    function onScroll() {
      var d = document.documentElement;
      var b = document.body;
      var scrolled = (d.scrollTop || b.scrollTop) + (window.innerHeight || d.clientHeight);
      var total = Math.max(d.scrollHeight, b.scrollHeight, d.offsetHeight, b.offsetHeight);
      if (total <= 0) return;
      var pct = (scrolled / total) * 100;
      for (var i = 0; i < thresholds.length; i++) {
        var t = thresholds[i];
        if (pct >= t && !seenScroll[t]) {
          seenScroll[t] = true;
          window.gtag('event', 'scroll_depth', { percent: t });
        }
      }
    }
    var scrollTimer = null;
    window.addEventListener('scroll', function () {
      if (scrollTimer) return;
      scrollTimer = setTimeout(function () { scrollTimer = null; onScroll(); }, 250);
    }, { passive: true });

    // Dwell milestones: 15s / 30s / 60s / 90s of active page time.
    var dwellSeen = {};
    var dwellMs = 0;
    var lastTick = Date.now();
    var visible = !document.hidden;
    function tick() {
      var now = Date.now();
      if (visible) dwellMs += (now - lastTick);
      lastTick = now;
      var secs = Math.floor(dwellMs / 1000);
      [15, 30, 60, 90].forEach(function (m) {
        if (secs >= m && !dwellSeen[m]) {
          dwellSeen[m] = true;
          window.gtag('event', 'dwell_time', { seconds: m });
        }
      });
    }
    document.addEventListener('visibilitychange', function () {
      tick();
      visible = !document.hidden;
      lastTick = Date.now();
    });
    setInterval(tick, 5000);

    // Outbound clicks (different hostname).
    document.addEventListener('click', function (e) {
      var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
      if (!a) return;
      var href = a.getAttribute('href') || '';
      if (!/^https?:\/\//i.test(href)) return;
      try {
        var u = new URL(href);
        if (u.hostname && u.hostname !== location.hostname) {
          window.gtag('event', 'click_outbound', {
            outbound_url: href,
            outbound_host: u.hostname
          });
        }
      } catch (err) {}
    }, true);
  }

  function loadGA() {
    if (loaded.ga) return;
    if (looksLikeBot()) return; // don't even register; keeps data clean
    loaded.ga = true;
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_MEASUREMENT_ID;
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', GA_MEASUREMENT_ID, {
      anonymize_ip: true,
      // Mark this as a real visit so engagement-based filters in GA4 work cleanly.
      send_page_view: true
    });
    wireEngagementEvents();
  }

  function applyChoice(choice) {
    if (!choice) return;
    if (choice.analytics) loadGA();
    dispatchChange(choice);
  }

  // ====== UI ======
  var STYLES = [
    '.bg-consent-root *{box-sizing:border-box}',
    '.bg-consent-banner{position:fixed;left:1rem;right:1rem;bottom:1rem;max-width:560px;margin:0 auto;background:#fff;border:1px solid #e8e8e4;border-radius:12px;box-shadow:0 12px 40px rgba(0,0,0,.18);padding:1.25rem 1.5rem;font-family:Inter,system-ui,sans-serif;color:#1a1a2e;z-index:2147483000;font-size:15px;line-height:1.5}',
    '.bg-consent-banner h3{font-family:"Playfair Display",Georgia,serif;font-size:1.2rem;font-weight:700;margin:0 0 .4rem}',
    '.bg-consent-banner p{margin:0 0 1rem;color:#444}',
    '.bg-consent-banner a{color:#c9a84c;text-decoration:underline}',
    '.bg-consent-buttons{display:flex;flex-wrap:wrap;gap:.5rem}',
    '.bg-btn{padding:.55rem 1rem;border-radius:8px;font-size:.92rem;font-weight:600;border:1px solid transparent;cursor:pointer;font-family:inherit;transition:all .2s ease}',
    '.bg-btn-primary{background:#c9a84c;color:#fff}',
    '.bg-btn-primary:hover{background:#e8c97e;color:#1a1a2e}',
    '.bg-btn-secondary{background:#fff;color:#1a1a2e;border-color:#e8e8e4}',
    '.bg-btn-secondary:hover{border-color:#c9a84c;color:#c9a84c}',
    '.bg-btn-link{background:transparent;color:#666;padding:.55rem .5rem}',
    '.bg-btn-link:hover{color:#1a1a2e;text-decoration:underline}',
    '.bg-consent-overlay{position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:2147483001;display:flex;align-items:center;justify-content:center;padding:1rem;font-family:Inter,system-ui,sans-serif}',
    '.bg-consent-modal{background:#fff;border-radius:12px;max-width:520px;width:100%;padding:1.75rem;max-height:90vh;overflow-y:auto;color:#1a1a2e}',
    '.bg-consent-modal h3{font-family:"Playfair Display",Georgia,serif;font-size:1.4rem;margin:0 0 .5rem}',
    '.bg-consent-modal > p{color:#444;margin:0 0 1.25rem;line-height:1.55}',
    '.bg-consent-row{border:1px solid #e8e8e4;border-radius:8px;padding:1rem;margin-bottom:.75rem}',
    '.bg-consent-row-head{display:flex;justify-content:space-between;align-items:center;gap:1rem;margin-bottom:.35rem}',
    '.bg-consent-row h4{margin:0;font-size:1rem;font-weight:600}',
    '.bg-consent-row p{margin:0;font-size:.88rem;color:#666;line-height:1.45}',
    '.bg-locked{font-size:.82rem;color:#999;font-style:italic}',
    '.bg-switch{position:relative;display:inline-block;width:40px;height:22px;flex-shrink:0}',
    '.bg-switch input{opacity:0;width:0;height:0}',
    '.bg-slider{position:absolute;cursor:pointer;inset:0;background:#ccc;border-radius:22px;transition:.2s}',
    '.bg-slider:before{position:absolute;content:"";height:16px;width:16px;left:3px;bottom:3px;background:#fff;border-radius:50%;transition:.2s}',
    '.bg-switch input:checked + .bg-slider{background:#c9a84c}',
    '.bg-switch input:checked + .bg-slider:before{transform:translateX(18px)}',
    '.bg-consent-modal-actions{display:flex;gap:.5rem;justify-content:flex-end;flex-wrap:wrap;margin-top:1rem}',
    '@media (max-width:520px){.bg-consent-banner{left:.5rem;right:.5rem;bottom:.5rem;padding:1rem}.bg-consent-buttons{flex-direction:column}.bg-btn{width:100%}}',
    '.bg-consent-root[hidden]{display:none!important}'
  ].join('');

  function injectStyles() {
    if (document.getElementById('bg-consent-styles')) return;
    var s = document.createElement('style');
    s.id = 'bg-consent-styles';
    s.textContent = STYLES;
    document.head.appendChild(s);
  }

  function buildBanner() {
    var root = document.createElement('div');
    root.className = 'bg-consent-root';
    root.setAttribute('role', 'dialog');
    root.setAttribute('aria-labelledby', 'bg-consent-title');
    root.setAttribute('aria-describedby', 'bg-consent-desc');
    root.innerHTML = [
      '<div class="bg-consent-banner">',
      '  <h3 id="bg-consent-title">Cookies &amp; your privacy</h3>',
      '  <p id="bg-consent-desc">We use essential cookies to run the site. We\'d also like your permission to use analytics (to understand what\'s working). You can change this anytime. <a href="/privacy-policy#cookies">Read our Cookie Policy</a>.</p>',
      '  <div class="bg-consent-buttons">',
      '    <button class="bg-btn bg-btn-primary" data-action="accept-all">Accept all</button>',
      '    <button class="bg-btn bg-btn-secondary" data-action="reject-all">Only necessary</button>',
      '    <button class="bg-btn bg-btn-link" data-action="customize">Customize</button>',
      '  </div>',
      '</div>'
    ].join('');
    return root;
  }

  function buildModal(current) {
    var cur = current || { analytics: false };
    var root = document.createElement('div');
    root.className = 'bg-consent-overlay';
    root.setAttribute('role', 'dialog');
    root.setAttribute('aria-modal', 'true');
    root.setAttribute('aria-labelledby', 'bg-consent-modal-title');
    root.innerHTML = [
      '<div class="bg-consent-modal">',
      '  <h3 id="bg-consent-modal-title">Cookie preferences</h3>',
      '  <p>Choose which cookies you\'re comfortable with. Your choice is saved on this device and you can change it anytime.</p>',
      '  <div class="bg-consent-row">',
      '    <div class="bg-consent-row-head"><h4>Strictly necessary</h4><span class="bg-locked">Always on</span></div>',
      '    <p>Required to keep the site secure and reachable (Cloudflare), and to remember your cookie choice.</p>',
      '  </div>',
      '  <div class="bg-consent-row">',
      '    <div class="bg-consent-row-head">',
      '      <h4>Analytics</h4>',
      '      <label class="bg-switch"><input type="checkbox" data-cat="analytics"' + (cur.analytics ? ' checked' : '') + '><span class="bg-slider"></span></label>',
      '    </div>',
      '    <p>Google Analytics 4, with IP anonymization. Helps us understand aggregate traffic and improve the site.</p>',
      '  </div>',
      '  <div class="bg-consent-modal-actions">',
      '    <button class="bg-btn bg-btn-link" data-action="reject-all">Reject all</button>',
      '    <button class="bg-btn bg-btn-secondary" data-action="save">Save preferences</button>',
      '    <button class="bg-btn bg-btn-primary" data-action="accept-all">Accept all</button>',
      '  </div>',
      '</div>'
    ].join('');
    return root;
  }

  // ====== State machine ======
  var bannerEl = null;
  var modalEl = null;

  function showBanner() {
    if (bannerEl) return;
    bannerEl = buildBanner();
    document.body.appendChild(bannerEl);
    bannerEl.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-action]');
      if (!btn) return;
      var a = btn.getAttribute('data-action');
      if (a === 'accept-all') finalize(true);
      else if (a === 'reject-all') finalize(false);
      else if (a === 'customize') openModal();
    });
  }

  function closeBanner() {
    if (bannerEl && bannerEl.parentNode) bannerEl.parentNode.removeChild(bannerEl);
    bannerEl = null;
  }

  function openModal() {
    if (modalEl) return;
    var current = loadChoice() || { analytics: false };
    modalEl = buildModal(current);
    document.body.appendChild(modalEl);
    modalEl.addEventListener('click', function (e) {
      if (e.target === modalEl) return closeModal(); // click outside
      var btn = e.target.closest('[data-action]');
      if (!btn) return;
      var a = btn.getAttribute('data-action');
      if (a === 'accept-all') {
        modalEl.querySelectorAll('input[data-cat]').forEach(function (i) { i.checked = true; });
        finalize(true);
      } else if (a === 'reject-all') {
        finalize(false);
      } else if (a === 'save') {
        var an = modalEl.querySelector('input[data-cat="analytics"]').checked;
        finalize(an);
      }
    });
    document.addEventListener('keydown', escHandler);
  }

  function escHandler(e) {
    if (e.key === 'Escape') closeModal();
  }

  function closeModal() {
    if (modalEl && modalEl.parentNode) modalEl.parentNode.removeChild(modalEl);
    modalEl = null;
    document.removeEventListener('keydown', escHandler);
  }

  function finalize(analytics) {
    var choice = saveChoice(analytics);
    applyChoice(choice);
    closeBanner();
    closeModal();
  }

  // ====== Public API ======
  window.bgConsent = {
    get: function () { return loadChoice(); },
    open: function () {
      // If the user's already made a choice, skip the banner and open the modal.
      if (loadChoice()) { openModal(); }
      else { showBanner(); }
    },
    reset: function () {
      try { localStorage.removeItem(CONSENT_KEY); } catch (e) {}
      loaded.ga = false;
    }
  };

  // ====== Boot ======
  function boot() {
    injectStyles();
    var existing = loadChoice();
    if (existing) {
      applyChoice(existing);
      return;
    }
    // No stored choice. Respect GPC/DNT as an implicit decline of non-essential.
    if (isGpcOrDnt()) {
      var choice = saveChoice(false);
      applyChoice(choice);
      return;
    }
    showBanner();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
