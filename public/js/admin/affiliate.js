/* LUXORA Platform — the affiliate domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

/* ========== Affiliate Network UI ========== */
function affiliateHtml() {
  /* a view renders INTO #vBody like every other view — writing to #app directly
     painted outside the console shell and left the nav's selected state stale */
  const html = `
    <div class="a-head">
      <h2>🤝 Influencers &amp; Affiliates</h2>
      <p class="a-sub">Manage affiliates, tracking, commissions, and payouts</p>
    </div>
    <div class="a-card">
      <h3>Affiliate Stats</h3>
      <div class="stats" id="affiliateStats"></div>
    </div>
    <div class="a-card">
      <h3>My Affiliates</h3>
      <p class="a-sub">Affiliates tracking and converting for your store</p>
      <div id="affiliateList"></div>
      <button class="p-btn" id="affAdd">+ Add Affiliate</button>
    </div>
  `;
  return html;
}
function wireAffiliate() {
  const add = $("#affAdd"); if (add) add.onclick = () => createAffiliateModal();
  loadAffiliateStats();
  loadAffiliates();
}

screen("affiliate", { group: "Marketing & Growth", label: "📣 Influencers & Affiliates", order: 0, render: async () => affiliateHtml(), wire: async () => { wireAffiliate(); } });
