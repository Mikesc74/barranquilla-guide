/**
 * Shared analytics helper for barranquilla.guide / thecartagena.guide.
 *
 * The page's inline <head> snippet loads gtag.js and calls
 *   gtag('config', '<ID>', { send_page_view: false });
 *
 * This script then:
 *   1. Checks for headless / bot signals. If detected, skips everything.
 *   2. Sends the page_view manually so only humans count.
 *   3. Wires engagement events (scroll depth, dwell time, outbound clicks)
 *      so we can verify real human traffic in GA4 reports.
 *
 * Include with:
 *   <script defer src="/js/analytics-engagement.js" data-ga-id="G-XXXX"></script>
 */
(function () {
  'use strict';

  var thisScript = document.currentScript ||
    (function () {
      var all = document.getElementsByTagName('script');
      return all[all.length - 1];
    })();
  var GA_ID = thisScript && thisScript.getAttribute('data-ga-id');
  if (!GA_ID) return;

  function looksLikeBot() {
    try {
      if (navigator.webdriver === true) return true;
      var ua = (navigator.userAgent || '').toLowerCase();
      if (!ua) return true;
      var bots = ['headlesschrome', 'phantomjs', 'slimerjs', 'electron',
        'puppeteer', 'playwright', 'selenium', 'lighthouse', 'pagespeed',
        'gtmetrix', 'pingdom', 'uptimerobot', 'wpt.', 'webpagetest',
        'bot', 'spider', 'crawler', 'crawling', 'scraper'];
      for (var i = 0; i < bots.length; i++) {
        if (ua.indexOf(bots[i]) !== -1) return true;
      }
      if (!navigator.languages || navigator.languages.length === 0) return true;
    } catch (e) {}
    return false;
  }

  // Ensure gtag exists even if the inline block failed (it normally has).
  window.dataLayer = window.dataLayer || [];
  if (typeof window.gtag !== 'function') {
    window.gtag = function () { window.dataLayer.push(arguments); };
  }

  if (looksLikeBot()) return; // human-only from here on

  // Manual page_view: ensures bots above never trigger a session.
  window.gtag('event', 'page_view', {
    page_location: location.href,
    page_title: document.title,
    page_path: location.pathname + location.search
  });

  // ===== Scroll depth: 25 / 50 / 75 / 100 =====
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

  // ===== Dwell time: 15 / 30 / 60 / 90 seconds of visible page time =====
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

  // ===== Outbound clicks (different hostname) =====
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
})();
