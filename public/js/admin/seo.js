/* LUXORA Platform — the seo domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

/* ========== Sitemap/SEO UI ========== */
function sitemapHtml() {
  const html = `
    <div class="a-head">
      <h2>🔍 Sitemap & SEO</h2>
      <p class="a-sub">Auto-generate XML sitemaps for search engines</p>
    </div>
    <div class="a-card">
      <h3>Sitemap Configuration</h3>
      <div id="sitemapConfig"></div>
    </div>
    <div class="a-card">
      <h3>Generate Sitemap</h3>
      <p class="a-sub">Creates XML sitemap for submission to Google, Bing, etc.</p>
      <button class="p-btn primary" id="smGen">🔄 Generate Now</button>
    </div>
    <div class="a-card">
      <h3>Last Generated</h3>
      <div id="sitemapLast"></div>
    </div>
  `;
  return html;
}
function wireSitemap() {
  const g = $("#smGen"); if (g) g.onclick = () => generateSitemap();
  loadSitemapConfig();
}

screen("sitemap", { render: async () => sitemapHtml(), wire: async () => { wireSitemap(); } });
