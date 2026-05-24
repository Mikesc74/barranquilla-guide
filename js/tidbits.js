/* tidbits.js · Colombian City Guides "Local tips" widget.
 * Injects a small, sourced "Local tips" box into a guide article, built from
 * the per-site /tidbits.json. Each tidbit maps to one or more guide slugs; this
 * matches the current page slug and renders the matching high-confidence tips.
 * Self-contained: injects its own styles, fails silent, no external deps.
 * House style: no em dashes. Color is paired with text labels (Mike is
 * red-green colour blind), never color alone.
 */
(function () {
  "use strict";
  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn, { once: true });
    } else {
      fn();
    }
  }

  function pageSlugs() {
    // Candidate slugs from the path. Handles /guides/<slug>.html (medellin)
    // and /<slug>/ (barranquilla, cartagena). The non-slug segments
    // ("guides", "index") simply will not match any tidbit's guides array.
    var parts = (location.pathname || "/").split("/");
    var out = [];
    for (var i = 0; i < parts.length; i++) {
      var p = parts[i];
      if (!p) continue;
      p = p.replace(/\.html$/i, "");
      if (p && p.toLowerCase() !== "index") out.push(p);
    }
    return out;
  }

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function injectStyles() {
    if (document.getElementById("tidbits-style")) return;
    var css =
      ".tidbits-box{margin:2rem 0;padding:1rem 1.25rem;background:#f7f8fa;" +
      "border:1px solid #e3e6ea;border-left:4px solid #1B2A47;border-radius:8px;" +
      "font-family:inherit;line-height:1.5}" +
      ".tidbits-box .tidbits-hd{font-size:.74rem;font-weight:700;letter-spacing:.06em;" +
      "text-transform:uppercase;color:#1B2A47;margin:0 0 .7rem}" +
      ".tidbits-box .tidbit{margin:0 0 .9rem}" +
      ".tidbits-box .tidbit:last-child{margin-bottom:0}" +
      ".tidbits-box .tidbit-t{display:block;font-weight:700;color:#1a1a1a;" +
      "font-size:.97rem;margin:0 0 .2rem}" +
      ".tidbits-box .tidbit-b{margin:0;color:#333;font-size:.93rem}" +
      ".tidbits-box .tidbit-say{margin:.35rem 0 0;font-size:.86rem;color:#4a4a4a}" +
      ".tidbits-box .tidbit-say b{color:#1B2A47}" +
      ".tidbits-box .tidbit-say i{font-style:italic}" +
      ".tidbits-box .tidbit-src{display:inline-block;margin:.3rem 0 0;font-size:.78rem}" +
      ".tidbits-box .tidbit-src a{color:#1B2A47}";
    var st = document.createElement("style");
    st.id = "tidbits-style";
    st.textContent = css;
    document.head.appendChild(st);
  }

  function render(matches, lang) {
    var isES = (lang || "").toLowerCase().indexOf("es") === 0;
    var box = document.createElement("section");
    box.className = "tidbits-box";
    box.setAttribute("aria-label", isES ? "Datos locales" : "Local tips");
    var html = '<p class="tidbits-hd">' + (isES ? "Datos locales" : "Local tips") + "</p>";
    for (var i = 0; i < matches.length; i++) {
      var t = matches[i];
      html += '<div class="tidbit">';
      html += '<strong class="tidbit-t">' + esc(t.title) + "</strong>";
      html += '<p class="tidbit-b">' + esc(t.tidbit) + "</p>";
      var say = isES ? t.say_es : (t.say_en || t.say_es);
      if (say) {
        html += '<p class="tidbit-say"><b>' + (isES ? "Dilo así:" : "Say it:") +
          '</b> <i>' + esc(say) + "</i></p>";
      }
      if (t.source && /^https?:\/\//i.test(t.source)) {
        html += '<span class="tidbit-src"><a href="' + esc(t.source) +
          '" target="_blank" rel="nofollow noopener">' +
          (isES ? "fuente" : "source") + "</a></span>";
      }
      html += "</div>";
    }
    box.innerHTML = html;
    return box;
  }

  ready(function () {
    try {
      var slugs = pageSlugs();
      if (!slugs.length) return;
      var container = document.querySelector(".article-content, .article-body") ||
        document.querySelector("article") || document.querySelector("main");
      if (!container) return;

      fetch("/tidbits.json", { credentials: "omit" })
        .then(function (r) { return r.ok ? r.json() : []; })
        .then(function (data) {
          if (!Array.isArray(data) || !data.length) return;
          var slugSet = {};
          for (var i = 0; i < slugs.length; i++) slugSet[slugs[i]] = 1;
          var matches = [];
          for (var j = 0; j < data.length; j++) {
            var g = data[j].guides || [];
            for (var k = 0; k < g.length; k++) {
              if (slugSet[g[k]]) { matches.push(data[j]); break; }
            }
            if (matches.length >= 4) break;
          }
          if (!matches.length) return;
          injectStyles();
          var lang = document.documentElement.getAttribute("lang") || "en";
          container.appendChild(render(matches, lang));
        })
        .catch(function () {});
    } catch (e) { /* fail silent */ }
  });
})();
