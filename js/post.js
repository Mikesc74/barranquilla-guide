/* post.js: per-post enhancements for the .guide network.
 *
 * Three self-contained features:
 *   1. A social share bar on each post (Facebook, X, WhatsApp, LinkedIn,
 *      Email, Copy link).
 *   2. A public "Read N times" counter inside each post.
 *   3. A "reads" badge on post cards in listings (guide catalog, archives,
 *      homepage guide/now cards, related-post cards).
 *
 * Loaded site-wide via a deferred <script>. The share bar + in-post counter
 * only run on single posts (pages with .article-header); the card decorator
 * runs on any page that has post cards. Share buttons need no backend; the
 * counts come from the Worker at counter.<site>, and if it is unreachable the
 * counts are simply omitted (share bar still works).
 *
 * Same file on all three sites; the site is detected from the hostname.
 */
(function () {
  "use strict";
  if (window.__guidesPostEnhanced) return;

  function counterBase() {
    return "https://counter." + location.hostname.replace(/^www\./, "");
  }

  // Normalise an href to an internal path so /x, /x.html and /x/index.html
  // all map to one key. Returns null for external links.
  function normPath(href) {
    var u;
    try { u = new URL(href, location.origin); } catch (e) { return null; }
    if (u.origin !== location.origin) return null;
    var p = u.pathname.replace(/index\.html$/i, "").replace(/\.html$/i, "");
    return p || "/";
  }

  var EYE =
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5C7 5 3 9.5 2 12c1 2.5 5 7 10 7s9-4.5 10-7c-1-2.5-5-7-10-7zm0 11a4 4 0 110-8 4 4 0 010 8zm0-2a2 2 0 100-4 2 2 0 000 4z"/></svg>';

  function injectStyles() {
    if (document.getElementById("pe-styles")) return;
    var css =
      ".pe-share{display:flex;align-items:center;flex-wrap:wrap;gap:.5rem;margin:1.5rem 0;font-family:inherit}" +
      ".pe-share .pe-label{font-size:.78rem;font-weight:600;letter-spacing:.05em;text-transform:uppercase;opacity:.6;margin-right:.15rem}" +
      ".pe-share a,.pe-share button{display:inline-flex;align-items:center;justify-content:center;width:38px;height:38px;border:0;border-radius:50%;background:#ecebe5;color:#1a1a2e;cursor:pointer;padding:0;text-decoration:none;transition:background .15s ease,color .15s ease,transform .15s ease}" +
      ".pe-share a:hover,.pe-share button:hover{transform:translateY(-1px)}" +
      ".pe-share svg{width:18px;height:18px;fill:currentColor;display:block}" +
      ".pe-share .pe-fb:hover{background:#1877f2;color:#fff}" +
      ".pe-share .pe-x:hover{background:#000;color:#fff}" +
      ".pe-share .pe-wa:hover{background:#25d366;color:#fff}" +
      ".pe-share .pe-li:hover{background:#0a66c2;color:#fff}" +
      ".pe-share .pe-em:hover{background:#555;color:#fff}" +
      ".pe-share .pe-cp:hover{background:#8a6d2f;color:#fff}" +
      ".pe-share .pe-cp.pe-ok{background:#2e7d32;color:#fff}" +
      ".pe-share-foot{margin-top:2rem;padding-top:1.25rem;border-top:1px solid rgba(0,0,0,.12)}" +
      ".pe-count{opacity:.85;white-space:nowrap}" +
      ".pe-card-count{align-items:center;gap:.3em;font-size:.8em;opacity:.78;white-space:nowrap;vertical-align:middle}" +
      ".pe-card-count svg{width:1em;height:1em;fill:currentColor;opacity:.85;display:inline-block;vertical-align:-.12em}" +
      ".pe-card-count.is-inline{display:inline-flex}" +
      ".pe-card-count.is-inline::before{content:'\\00b7';margin:0 .45em 0 .2em;opacity:.55}" +
      ".pe-card-count.is-block{display:flex;margin-top:.45rem}";
    var style = document.createElement("style");
    style.id = "pe-styles";
    style.textContent = css;
    document.head.appendChild(style);
  }

  // ---------- 1 + 2: share bar and in-post counter ----------
  function enhanceSinglePost() {
    var header = document.querySelector(".article-header");
    var body = document.querySelector(".article-body, .article-content");
    if (!header || !body) return; // not a single post
    var meta = document.querySelector(".article-header-meta, .article-meta");

    var canon = document.querySelector('link[rel="canonical"]');
    var url = (canon && canon.href) || location.href.split("#")[0];
    var ogTitle = document.querySelector('meta[property="og:title"]');
    var title = (ogTitle && ogTitle.content) || document.title || "";
    var path = normPath(location.href) || location.pathname;
    var U = encodeURIComponent(url);
    var T = encodeURIComponent(title);

    var ICON = {
      fb: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M22 12.06C22 6.5 17.52 2 12 2S2 6.5 2 12.06c0 5 3.66 9.15 8.44 9.94v-7.03H7.9v-2.9h2.54V9.84c0-2.52 1.5-3.92 3.8-3.92 1.1 0 2.25.2 2.25.2v2.48h-1.27c-1.25 0-1.64.78-1.64 1.58v1.9h2.79l-.45 2.9h-2.34V22c4.78-.79 8.44-4.94 8.44-9.94z"/></svg>',
      x: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18.244 2H21.5l-7.5 8.57L22.5 22h-6.6l-5.17-6.76L4.8 22H1.54l8.02-9.17L1.5 2h6.77l4.67 6.18L18.244 2zm-1.16 18h1.83L7.01 3.9H5.05L17.084 20z"/></svg>',
      wa: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M.06 24l1.69-6.16a11.86 11.86 0 01-1.59-5.95C.16 5.34 5.5 0 12.06 0a11.82 11.82 0 018.41 3.49 11.82 11.82 0 013.48 8.42c0 6.56-5.34 11.9-11.9 11.9a11.9 11.9 0 01-5.69-1.45L.06 24zm6.6-3.8c1.68.99 3.28 1.59 5.4 1.59 5.45 0 9.9-4.43 9.9-9.88a9.85 9.85 0 00-2.9-7 9.82 9.82 0 00-7-2.9c-5.46 0-9.9 4.43-9.9 9.88 0 2.07.65 3.6 1.74 5.27l-1 3.65 3.76-.98zM17.5 14.3c-.07-.12-.27-.2-.57-.35-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.96-.94 1.16-.17.2-.35.22-.65.07-.3-.15-1.26-.46-2.4-1.48-.88-.79-1.48-1.76-1.65-2.06-.17-.3-.02-.46.13-.61.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.02-.52-.07-.15-.67-1.62-.92-2.22-.24-.58-.49-.5-.67-.51l-.57-.01c-.2 0-.52.07-.79.37-.27.3-1.04 1.02-1.04 2.48 0 1.46 1.06 2.88 1.21 3.08.15.2 2.1 3.2 5.08 4.49.71.31 1.26.49 1.69.62.71.23 1.36.2 1.87.12.57-.08 1.76-.72 2.01-1.41.25-.7.25-1.29.17-1.42z"/></svg>',
      li: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.13 1.45-2.13 2.94v5.67H9.35V9h3.42v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.45v6.29zM5.34 7.43a2.07 2.07 0 110-4.14 2.07 2.07 0 010 4.14zM7.12 20.45H3.55V9h3.57v11.45zM22.22 0H1.77C.8 0 0 .77 0 1.73v20.54C0 23.22.8 24 1.77 24h20.45c.98 0 1.78-.78 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z"/></svg>',
      em: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 4h20a2 2 0 012 2v12a2 2 0 01-2 2H2a2 2 0 01-2-2V6a2 2 0 012-2zm10 7L2.5 6h19L12 11zm0 2.2L2 7.3V18h20V7.3l-10 5.9z"/></svg>',
      cp: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3.9 12a3.1 3.1 0 013.1-3.1h4V7h-4a5 5 0 100 10h4v-1.9h-4A3.1 3.1 0 013.9 12zM8 13h8v-2H8v2zm9-6h-4v1.9h4a3.1 3.1 0 010 6.2h-4V17h4a5 5 0 000-10z"/></svg>',
    };

    function link(key, label, href) {
      return (
        '<a class="pe-' + key + '" href="' + href + '" target="_blank" ' +
        'rel="noopener noreferrer" title="' + label + '" aria-label="' + label +
        '">' + ICON[key] + "</a>"
      );
    }
    function makeShareBar(extraClass) {
      var bar = document.createElement("div");
      bar.className = "pe-share" + (extraClass ? " " + extraClass : "");
      bar.setAttribute("aria-label", "Share this post");
      bar.innerHTML =
        '<span class="pe-label">Share</span>' +
        link("fb", "Share on Facebook", "https://www.facebook.com/sharer/sharer.php?u=" + U) +
        link("x", "Share on X", "https://twitter.com/intent/tweet?url=" + U + "&text=" + T) +
        link("wa", "Share on WhatsApp", "https://api.whatsapp.com/send?text=" + T + "%20" + U) +
        link("li", "Share on LinkedIn", "https://www.linkedin.com/sharing/share-offsite/?url=" + U) +
        link("em", "Share by email", "mailto:?subject=" + T + "&body=" + U) +
        '<button class="pe-cp" type="button" title="Copy link" aria-label="Copy link">' + ICON.cp + "</button>";
      var copyBtn = bar.querySelector(".pe-cp");
      copyBtn.addEventListener("click", function () {
        var done = function () {
          copyBtn.classList.add("pe-ok");
          copyBtn.setAttribute("title", "Link copied");
          setTimeout(function () {
            copyBtn.classList.remove("pe-ok");
            copyBtn.setAttribute("title", "Copy link");
          }, 1600);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(url).then(done, function () {});
        } else {
          var t = document.createElement("textarea");
          t.value = url;
          t.style.position = "fixed";
          t.style.opacity = "0";
          document.body.appendChild(t);
          t.select();
          try { document.execCommand("copy"); done(); } catch (e) {}
          document.body.removeChild(t);
        }
      });
      return bar;
    }

    // Top bar (top of the reading column, aligned with body text) and a foot bar.
    body.insertBefore(makeShareBar(), body.firstChild);
    body.appendChild(makeShareBar("pe-share-foot"));

    if (!meta) return;
    var base = counterBase();
    var sessionKey = "gv:" + path;
    var firstThisSession = true;
    try { firstThisSession = !sessionStorage.getItem(sessionKey); } catch (e) {}

    function showCount(n) {
      if (typeof n !== "number" || n < 0) return;
      var el = meta.querySelector(".pe-count");
      if (!el) {
        meta.appendChild(document.createTextNode(" · "));
        el = document.createElement("span");
        el.className = "pe-count";
        meta.appendChild(el);
      }
      el.textContent = "Read " + n.toLocaleString("en-US") + (n === 1 ? " time" : " times");
    }

    var endpoint, opts;
    if (firstThisSession) {
      try { sessionStorage.setItem(sessionKey, "1"); } catch (e) {}
      endpoint = base + "/hit?p=" + encodeURIComponent(path);
      opts = { method: "POST", keepalive: true };
    } else {
      endpoint = base + "/count?p=" + encodeURIComponent(path);
      opts = { method: "GET" };
    }
    fetch(endpoint, opts)
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) { if (d) showCount(d.count); })
      .catch(function () {});
  }

  // ---------- 3: card "reads" badges on listing pages ----------
  var CARD_CONFIGS = [
    { sel: "a.blog-card", meta: ".blog-card-meta" },
    { sel: "article.article-card", link: ".article-card-title a, .article-card-image[href], a[href]", meta: ".article-card-meta" },
    { sel: "a.article-card", meta: ".article-card-meta" },
    { sel: "a.gd", meta: ".meta" },
    { sel: "a.now-card", meta: null },
    { sel: "a.related-card", meta: null },
  ];

  function cardHref(card, cfg) {
    var a =
      card.tagName === "A" && card.getAttribute("href")
        ? card
        : card.querySelector(cfg.link || "a[href]");
    return a ? a.href : null;
  }

  function injectCardBadge(target, inline, n) {
    if (target.querySelector(".pe-card-count")) return;
    var span = document.createElement("span");
    span.className = "pe-card-count " + (inline ? "is-inline" : "is-block");
    var label = n.toLocaleString("en-US");
    span.title = label + (n === 1 ? " read" : " reads");
    span.innerHTML = EYE + "<span>" + label + "</span>";
    target.appendChild(span);
  }

  function decorateCards() {
    var byPath = {};
    CARD_CONFIGS.forEach(function (cfg) {
      var cards = document.querySelectorAll(cfg.sel);
      for (var i = 0; i < cards.length; i++) {
        var card = cards[i];
        if (card.getAttribute("data-pe-card")) continue;
        var href = cardHref(card, cfg);
        var path = href ? normPath(href) : null;
        if (!path) continue;
        card.setAttribute("data-pe-card", "1");
        var target = card, inline = false;
        if (cfg.meta) {
          var m = card.querySelector(cfg.meta);
          if (m) { target = m; inline = true; }
        }
        (byPath[path] = byPath[path] || []).push({ target: target, inline: inline });
      }
    });

    var paths = Object.keys(byPath);
    if (!paths.length) return;
    var base = counterBase();
    var qs = paths
      .slice(0, 100)
      .map(function (p) { return "p=" + encodeURIComponent(p); })
      .join("&");
    fetch(base + "/counts?" + qs)
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (map) {
        if (!map) return;
        paths.forEach(function (p) {
          var n = map[p];
          if (typeof n !== "number" || n <= 0) return;
          byPath[p].forEach(function (slot) {
            injectCardBadge(slot.target, slot.inline, n);
          });
        });
      })
      .catch(function () {});
  }

  function init() {
    if (window.__guidesPostEnhanced) return;
    window.__guidesPostEnhanced = true;
    injectStyles();
    enhanceSinglePost();
    decorateCards();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
