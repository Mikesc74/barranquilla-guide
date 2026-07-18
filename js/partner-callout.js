/**
 * Partner-recommendation callout box (content-strategy Phase 4, 2026-07-18).
 *
 * Usage in an article's .article-body:
 *   <div class="callout" data-partner-widget="doctor"></div>
 *   <script src="/js/partner-callout.js" defer></script>
 *
 * `data-partner-widget` is one of the partners.category values:
 * doctor | lawyer | tour | driver | dentist | realtor | visa | translator | other.
 *
 * This site is static (no build step, no server), so the box can't be
 * populated at publish time, it has to ask a live worker at view time. It
 * asks catalina.<this-site's-own-hostname>/api/partner-widget so each guide
 * only ever gets ITS OWN city's partners (barranquilla.guide asks
 * catalina.barranquilla.guide, never crosses into another city's data).
 *
 * If there's no active, vetted partner for that category yet (the normal
 * case today, see ~/code/project-wiki/content/guides-content-strategy.md),
 * the div is removed entirely, never a fake-looking placeholder box.
 */
(function () {
  function esc(s) {
    var d = document.createElement("div");
    d.textContent = s || "";
    return d.innerHTML;
  }

  function render(el, data) {
    el.classList.add("callout");
    var links = [];
    if (data.whatsapp) {
      var digits = String(data.whatsapp).replace(/[^\d]/g, "");
      links.push('<a href="https://wa.me/' + digits + '" target="_blank" rel="noopener">WhatsApp</a>');
    }
    if (data.website) {
      links.push('<a href="' + esc(data.website) + '" target="_blank" rel="noopener nofollow">Website</a>');
    }
    el.innerHTML =
      '<p style="margin:0 0 6px;font-weight:600">✓ Verified local partner: ' + esc(data.name) + "</p>" +
      "<p style=\"margin:0 0 6px\">" + esc(data.blurb) + "</p>" +
      (links.length ? '<p style="margin:0">' + links.join(" &middot; ") + "</p>" : "");
  }

  document.querySelectorAll("[data-partner-widget]").forEach(function (el) {
    var category = (el.getAttribute("data-partner-widget") || "").trim().toLowerCase();
    if (!category) { el.remove(); return; }
    var host = location.hostname.replace(/^www\./, "");
    var api = "https://catalina." + host + "/api/partner-widget?category=" + encodeURIComponent(category);
    fetch(api)
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (!data || !data.found) { el.remove(); return; }
        render(el, data);
      })
      .catch(function () { el.remove(); });
  });
})();
