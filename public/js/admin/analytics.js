/* LUXORA Platform — the analytics domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

async function vAnalytics() {
  const a = await api("/admin/analytics");
  const max = Math.max(1, ...a.byDay.map(d => d.revenue));
  return `
  <div class="p-cards">
    <div class="p-stat"><em>Inventory value</em><b>${money(a.invValue)}</b></div>
    <div class="p-stat"><em>Funnel</em><b>${a.funnel.views} → ${a.funnel.carts} → ${a.funnel.orders}</b><small>views → carts → orders</small></div>
  </div>
  <div class="p-grid2">
    <div class="p-panel"><h2>30-day revenue</h2><div class="p-chart">${a.byDay.map(d => `<div class="bar" style="height:${Math.max(4, d.revenue / max * 100)}%" data-tip="${esc(d.d)} ${money(d.revenue)}"></div>`).join("")}</div></div>
    <div class="p-panel"><h2>Top products</h2><table class="p-table"><thead><tr><th></th><th>Product</th><th class="num">Units</th><th class="num">Revenue</th></tr></thead>
      <tbody>${a.topProducts.map(p => `<tr><td class="t-emoji">${esc(p.emoji)}</td><td>${esc(p.title.slice(0, 44))}</td><td class="num">${p.units}</td><td class="num">${money(p.rev)}</td></tr>`).join("")}</tbody></table></div>
  </div>
  <div class="p-panel"><h2>Sales by industry</h2><table class="p-table"><thead><tr><th>Industry</th><th class="num">Revenue</th></tr></thead>
    <tbody>${a.byIndustry.map(x => `<tr><td>${esc(x.industry)}</td><td class="num">${money(x.rev)}</td></tr>`).join("") || '<tr><td colspan="2" class="p-empty">No sales yet</td></tr>'}</tbody></table></div>`;
}

screen("analytics", { render: async () => await vAnalytics() });
