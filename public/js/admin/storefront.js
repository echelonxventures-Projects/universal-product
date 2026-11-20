/* LUXORA Platform — the storefront domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

/* ---------- views ---------- */
async function vDash() {
  const st = await api("/admin/stats");
  const max = Math.max(1, ...st.daily.map(d => d.t));
  return `
  <div class="p-cards">
    <div class="p-stat"><em>Revenue</em><b>${money(st.revenue)}</b><small>lifetime GMV</small></div>
    <div class="p-stat"><em>Orders</em><b>${st.orders}</b><small>${st.pending} open</small></div>
    <div class="p-stat"><em>Customers</em><b>${st.customers}</b></div>
    <div class="p-stat"><em>Products</em><b>${st.products}</b><small>plan: ${esc(st.plan.name)} (${st.plan.max_products} max)</small></div>
  </div>
  <div class="p-grid2">
    <div class="p-panel"><h2>Revenue · last 14 days</h2>
      <div class="p-chart">${st.daily.length ? st.daily.map(d => `<div class="bar" style="height:${Math.max(4, d.t / max * 100)}%" data-tip="${esc(d.d)}: ${money(d.t)}"></div>`).join("") : '<div class="p-empty">No orders yet</div>'}</div></div>
    <div class="p-panel"><h2>Payment gateways</h2>
      <table class="p-table"><thead><tr><th>Gateway</th><th>Count</th><th class="num">Volume</th><th class="num">Fees</th></tr></thead>
      <tbody>${st.payments.map(p => `<tr><td>${esc(p.gateway)}</td><td>${p.c}</td><td class="num">${money(p.amt)}</td><td class="num">${money(p.fee)}</td></tr>`).join("") || '<tr><td colspan="4" class="p-empty">No payments yet</td></tr>'}</tbody></table></div>
  </div>
  <div class="p-grid2">
    <div class="p-panel"><h2>Recent orders</h2><table class="p-table"><thead><tr><th>Order</th><th>Customer</th><th class="num">Total</th><th>Status</th></tr></thead>
      <tbody>${st.recent.map(o => `<tr><td>${esc(o.num)}</td><td>${esc(o.name)}</td><td class="num">${money(o.total)}</td><td><span class="badge ${esc(o.status)}">${esc(o.status)}</span></td></tr>`).join("") || '<tr><td colspan="4" class="p-empty">None</td></tr>'}</tbody></table></div>
    <div class="p-panel"><h2>Low stock</h2><table class="p-table"><thead><tr><th>Product</th><th class="num">Stock</th></tr></thead>
      <tbody>${st.lowStock.map(p => `<tr><td>${esc(p.title.slice(0, 46))}</td><td class="num" style="color:${p.st <= 3 ? "var(--p-red)" : "inherit"}">${p.stock}</td></tr>`).join("") || '<tr><td colspan="2" class="p-empty">All healthy</td></tr>'}</tbody></table></div>
  </div>`;
}

screen("dash", { group: "Overview", label: "◈ Dashboard", order: 0, render: async () => await vDash() });
screen("content", { group: "Storefront", label: "🖼️ Home Content", order: 0, render: async () => await entityTable("banner") + await entityTable("card") + await entityTable("department") });
