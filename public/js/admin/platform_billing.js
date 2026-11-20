/* LUXORA Platform — the platform_billing domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

async function vBilling() {
  const [b, own] = await Promise.all([api("/admin/billing"), api("/modules")]);
  const canPay = !!(own.gates || {})["billing.self_pay"];
  let gws = [];
  if (canPay) { try { gws = (await api("/providers")).gateways; } catch (e) { } }
  return `
  <div class="p-cards">
    <div class="p-stat"><em>Plan</em><b>${esc(b.subscription ? b.subscription.plan : "—")}</b><small>${b.subscription ? money(b.subscription.price_month) + "/mo · " + esc(b.subscription.status) : ""}</small></div>
    <div class="p-stat"><em>Products</em><b>${b.usage.products} / ${b.subscription ? b.subscription.max_products : "∞"}</b></div>
    <div class="p-stat"><em>Orders this month</em><b>${b.usage.ordersMonth} / ${b.subscription ? b.subscription.max_orders_month : "∞"}</b></div>
  </div>
  <div class="p-panel"><h2>Invoices <span class="p-tag" style="font-weight:400;font-size:11px;margin-left:10px">${canPay ? "self-service payment enabled (Billing Pro)" : "Billing Pro enables self-service payment"}</span></h2><table class="p-table"><thead><tr><th>Number</th><th>Period</th><th class="num">Amount</th><th>Status</th><th>Paid</th><th></th></tr></thead>
    <tbody id="invBody">${b.invoices.map(i => `<tr><td>${esc(i.number)}</td><td>${esc(i.period_start)} → ${esc(i.period_end || "")}</td><td class="num">${money(i.amount)}</td><td><span class="badge ${esc(i.status)}">${esc(i.status)}</span></td><td>${esc(i.paid_at || "—")}</td><td>${canPay && i.status !== "paid" ? `<select data-inv="${i.id}" class="p-btn sm">${gws.map(g => `<option value="${esc(g.id)}">${esc(g.name)}</option>`).join("")}</select> <button class="p-btn sm primary" data-payinv="${i.id}">Pay</button>` : ""}</td></tr>`).join("") || '<tr><td colspan="6" class="p-empty">No invoices</td></tr>'}</tbody></table></div>`;
}

screen("billing", { group: "Payments & Finance", label: "🧮 Billing", order: 4, render: async () => await vBilling() });
