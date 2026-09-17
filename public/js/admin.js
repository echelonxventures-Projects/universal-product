/* LUXORA Platform - Store Admin console (metadata-driven) */
"use strict";

const $ = s => document.querySelector(s);
const $$ = s => Array.from(document.querySelectorAll(s));
function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }
function __csrf() { const m = /(?:^|; )azc=([^;]+)/.exec(document.cookie || ""); return m ? m[1] : ""; }
async function api(path, method = "GET", body) {
  const opt = { method, headers: { "Content-Type": "application/json", "x-csrf": __csrf() }, credentials: "same-origin" };
  if (body) opt.body = JSON.stringify(body);
  const r = await fetch("/api" + path, opt);
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.error || ("HTTP " + r.status));
  return data;
}
let TT = null;

function linkify(m) {
  return esc(m).replace(/\/(platform|admin)\.html(\?store=[A-Za-z0-9-]+)?/g, function (s) {
    return '<a href="' + s + '" style="text-decoration:underline">' + (s.indexOf("platform") >= 0 ? "Platform console" : "Store console") + " →</a>";
  });
}
function money(n) { const d = (TT && TT.commerce && TT.commerce.decimals != null) ? TT.commerce.decimals : 2; try { return new Intl.NumberFormat(TT.commerce.locale, { style: "currency", currency: TT.commerce.currency, minimumFractionDigits: d, maximumFractionDigits: d }).format(+n); } catch (e) { return ((TT && TT.commerce && TT.commerce.symbol) || "$") + (+n).toFixed(d); } }
let toastT;
function toast(msg) {
  let t = $("#ptoast");
  if (!t) { t = document.createElement("div"); t.id = "ptoast"; t.className = "p-toast"; document.body.appendChild(t); }
  t.textContent = msg; t.classList.add("show");
  clearTimeout(toastT); toastT = setTimeout(() => t.classList.remove("show"), 3000);
}
const NAV = [
  ["dash", "◈ Dashboard"], ["products", "📦 Products"], ["skus", "🔖 SKUs & Inventory"], ["orders", "🧾 Orders"],
  ["returns", "↩️ Returns"], ["rfqs", "📋 RFQs (B2B)"], ["sellers", "🏪 Sellers"], ["settlements", "🤝 Settlements"],
  ["contracts", "📝 Contracts (B2B)"], ["tenders", "🏛️ Tenders"], ["suppliers", "🚚 Suppliers & Procurement"], ["serialized", "🔢 Serialized Items"], ["compliance", "✅ Compliance & Certs"], ["localizations", "🌐 Localizations"],
  ["ai", "🤖 AI Studio"], ["webhooks", "🔗 Webhooks"], ["trash", "🗑️ Trash & Retention"], ["sso", "🔐 SSO & Integrations"],
  ["promotions", "💸 Offers & Coupons"], ["goip", "Ω∞ GOIP"],   ["search", "🔎 Search & Discovery"],   ["logistics", "🚚 Logistics & Fulfilment"], ["finance", "💰 Finance & Settlements"], ["content", "🖼️ Home Content"], ["taxonomy", "🌳 Taxonomy"], ["attributes", "🧬 Attributes"],
  ["payments", "💳 Payment Gateways"], ["modules", "🧩 Modules"], ["settings", "⚙️ Settings"], ["billing", "🧮 Billing"], ["analytics", "📊 Analytics"], ["audit", "📜 Audit Trail"],
  ["monitor", "📈 Monitor"], ["team", "👥 Team & Roles"], ["studio", "🛠️ Data Studio"]
];
const NAVSEC = { promotions: "offers", goip: "offers", ai: "ai", webhooks: "webhooks", trash: "trash", team: "team", studio: "studio", sso: "settings" };
const navSection = k => NAVSEC[k] || k;
const canSee = k => { if (!A.allowed || A.allowed.includes("*")) return true; if (k === "dash") return true; return A.allowed.includes(navSection(k)); };
let view = "dash";

async function vSearch() {
  const [res, rec, suggest] = await Promise.all([api("/search", { q: "home" }), api("/recommend", { anchor: "LX-ELS-007", limit: 5 }), api("/suggest", { prefix: "so" })]);
  const facets = res.facets || {};
  return `<div class="a-head"><h2>🔎 Search &amp; Discovery</h2><p class="a-sub">Faceted, typo-tolerant query · registry-driven synonyms &amp; boosts · co-purchase / co-view recommendations. Configuration lives in Data Studio: <code>searchSynonyms</code>, <code>searchBoosts</code>.</p></div>
  <div class="a-card"><h3>Sample query · <code>q=home</code></h3>
    <p class="a-sub">matched <b>${res.matched}</b> · facets ${Object.entries(facets).slice(0, 8).map(([k, v]) => `<span class="a-chip">${esc(k)}·${v}</span>`).join("")}</p>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>id</th><th>title</th><th>brand</th><th>dept</th><th>price</th><th>rating</th><th>reason</th></tr></thead>
      <tbody>${res.items.map(i => `<tr><td><code>${esc(i.id)}</code></td><td>${esc(i.title)}</td><td>${esc(i.brand)}</td><td>${esc(i.dept)}</td><td>${money(i.price)}</td><td>${i.rating}</td><td>${i.reason ? `<span class="a-chip">${esc(i.reason)}</span>` : "—"}</td></tr>`).join("") || '<tr><td colspan="7">—</td></tr>'}</tbody></table></div>
  </div>
  <div class="a-card"><h3>Recommendations · co-purchase of <code>LX-ELS-007</code></h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>id</th><th>title</th><th>weight</th></tr></thead>
      <tbody>${(rec.items || []).map(i => `<tr><td><code>${esc(i.id)}</code></td><td>${esc(i.title)}</td><td>${i.weight}</td></tr>`).join("") || '<tr><td colspan="3">No co-purchase signal yet.</td></tr>'}</tbody></table></div>
  </div>
  <div class="a-card"><h3>Autocomplete · prefix <code>so</code></h3>
    <div>${(suggest.items || []).map(t => `<span class="a-chip">${esc(t)}</span>`).join(" ") || "—"}</div>
  </div>`;
}
async function vLogistics() {
  const [ships, sla, carriers] = await Promise.all([api("/shipments", {}), api("/admin/sla", { days: 3 }), api("/carriers", {})]);
  const statuses = ships.statuses || [];
  const by = {}; ships.shipments.forEach(s => by[s.status] = (by[s.status] || 0) + 1);
  return `<div class="a-head"><h2>🚚 Logistics &amp; Fulfilment</h2><p class="a-sub">Fulfilment state machine · shipment tracking · 3PL carrier abstraction · warehouse routing · SLA · return disposition. States &amp; dispositions live in Data Studio: <code>logisticsStates</code>, <code>logisticsDispositions</code>.</p></div>
  <div class="a-card"><h3>Active shipments</h3>
    <p class="a-sub">${Object.entries(by).map(([k, v]) => `<span class="a-chip">${esc(k)}·${v}</span>`).join(" ") || "none"}</p>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>ref</th><th>order</th><th>carrier</th><th>status</th><th>warehouse</th></tr></thead>
      <tbody>${ships.shipments.slice(0, 25).map(s => `<tr><td><code>${esc(s.tracking_ref)}</code></td><td>${s.order_id}</td><td>${esc(s.carrier || "—")}</td><td><span class="a-chip">${esc(s.status)}</span></td><td>${s.warehouse_id || "—"}</td></tr>`).join("") || '<tr><td colspan="5">No shipments yet.</td></tr>'}</tbody></table></div>
  </div>
  <div class="a-card"><h3>SLA breaches (&gt;3 days undelivered)</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>ref</th><th>status</th><th>created</th></tr></thead>
      <tbody>${sla.breaches.map(b => `<tr><td><code>${esc(b.tracking_ref)}</code></td><td>${esc(b.status)}</td><td>${esc(b.created_at)}</td></tr>`).join("") || '<tr><td colspan="3">On schedule.</td></tr>'}</tbody></table></div>
  </div>
  <div class="a-card"><h3>3PL carriers (registry)</h3>
    <div>${(carriers.carriers || []).map(c => `<span class="a-chip">${esc(c.emoji || "")} ${esc(c.name)}</span>`).join(" ") || "none configured"}</div>
  </div>`;
}
async function vFinance() {
  const [disp, pays, led] = await Promise.all([api("/admin/fin/disputes"), api("/admin/fin/payouts"), api("/admin/fin/ledger", { owner: "t1:s:demo" })]);
  const byS = {}; disp.disputes.forEach(d => byS[d.state] = (byS[d.state] || 0) + 1);
  return `<div class="a-head"><h2>💰 Finance &amp; Settlements</h2><p class="a-sub">Chargebacks / disputes · multi-gateway retries · batch payout runs · bank-feed reconciliation · FX-aware ledger. States &amp; kinds in Data Studio: <code>finDisputeStates</code>, <code>finPayoutKinds</code>, <code>finReconSources</code>.</p></div>
  <div class="a-card"><h3>Disputes / chargebacks</h3>
    <p class="a-sub">${Object.entries(byS).map(([k, v]) => `<span class="a-chip">${esc(k)}·${v}</span>`).join("") || "none open"}</p>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>ref</th><th>payment</th><th>amount</th><th>state</th></tr></thead>
      <tbody>${disp.disputes.slice(0, 15).map(d => `<tr><td><code>${esc(d.ref)}</code></td><td>${d.payment_id || "—"}</td><td>${money(d.amount)} ${esc(d.currency)}</td><td><span class="a-chip">${esc(d.state)}</span></td></tr>`).join("") || '<tr><td colspan="4">No disputes.</td></tr>'}</tbody></table></div>
  </div>
  <div class="a-card"><h3>Payout runs</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>ref</th><th>kind</th><th>seller</th><th>gross</th><th>net</th><th>status</th><th>items</th></tr></thead>
      <tbody>${pays.payouts.slice(0, 15).map(p => `<tr><td><code>${esc(p.ref)}</code></td><td>${esc(p.kind)}</td><td>${p.seller_id || "—"}</td><td>${money(p.gross)}</td><td>${money(p.net)}</td><td><span class="a-chip">${esc(p.status)}</span></td><td>${p.items}</td></tr>`).join("") || '<tr><td colspan="7">No payout runs.</td></tr>'}</tbody></table></div>
  </div>
  <div class="a-card"><h3>FX ledger · <code>t1:s:demo</code></h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>kind</th><th>amount</th><th>currency</th><th>balance_after</th></tr></thead>
      <tbody>${(led.entries || []).slice(0, 10).map(e => `<tr><td>${esc(e.kind)}</td><td>${money(e.amount)}</td><td>${esc(e.currency)}</td><td>${money(e.balance_after)}</td></tr>`).join("") || '<tr><td colspan="4">—</td></tr>'}</tbody></table></div>
  </div>`;
}
function shell(content) {
  $("#app").innerHTML = `
  <div class="p-shell">
    <aside class="p-side">
      <div class="p-logo"><b>${esc(TT.brand.wordmark)}</b><small>Store Console · ${esc(TT.tenant.slug)}</small></div>
      <nav class="p-nav">${NAV.filter(([k]) => canSee(k)).map(([k, l]) => `<button data-v="${k}" class="${view === k ? "on" : ""}">${l}</button>`).join("")}</nav>
      <div style="padding:18px 22px;border-top:1px solid var(--p-line);margin-top:14px">
        <a href="/index.html?store=${esc(TT.tenant.slug)}" target="_blank">↗ Open storefront</a>
      </div>
    </aside>
    <main class="p-main"><div class="p-top"><h1 id="vTitle">${NAV.find(n => n[0] === view)[1].replace(/^\S+\s/, "")}</h1><span class="spacer"></span>
      <span class="p-chip">${esc(TT.tenant.mode)}</span><span class="p-user">${esc(A.user.name)}</span>
      <button class="p-btn sm" id="logoutBtn">Sign out</button></div>
      <div id="vBody">${content}</div></main>
  </div>`;
  $$(".p-nav button").forEach(b => b.onclick = () => { view = b.dataset.v; render(); });
  $("#logoutBtn").onclick = async () => { await api("/auth/logout", "POST"); location.href = "/index.html"; };
}

/* ---------- generic entity table/form ---------- */
async function entityRows(key) { try { return (await api("/meta/entity/" + key)).rows; } catch (e) { return []; } }
async function refOptions(key) { const rows = await entityRows(key); return rows.map(r => ({ v: r.id != null ? r.id : r.key, l: r.title || r.name || r.label || r.code || r.ref || String(r.id || r.key) })); }
async function fieldInput(f, val, registry) {
  const id = "f_" + f.key;
  if (f.type === "bool") return `<label><span>${esc(f.label)}</span><input type="checkbox" id="${id}" ${val ? "checked" : ""}></label>`;
  if (f.type === "json" || f.type === "multi") return `<label><span>${esc(f.label)} (JSON)</span><textarea id="${id}" rows="3">${esc(typeof val === "string" ? val : JSON.stringify(val || (f.type === "multi" ? [] : {}), null, 1))}</textarea></label>`;
  if (f.type === "select") {
    let opts = Array.isArray(f.options) ? f.options : (f.options && String(f.options).includes(".") ? String(f.options).split(".").reduce((o, k) => (o || {})[k], registry) : (registry && registry[f.options])) || [];
    if (f.options === "lifecycle") opts = registry.lifecycle;
    if (f.options === "productTypes") opts = registry.productTypes.map(t => t.key);
    if (f.options === "sellerRoles") opts = registry.sellerRoles;
    if (f.options === "promoTypes") opts = registry.promoTypes.map(t => t.key);
    if (f.options === "deployModes") opts = registry.deployModes.map(t => t.key);
    return `<label><span>${esc(f.label)}</span><select id="${id}">${opts.map(o => `<option ${o === val ? "selected" : ""}>${esc(o)}</option>`).join("")}</select></label>`;
  }
  if (f.type.startsWith("ref:")) {
    const opts = await refOptions(f.type.slice(4));
    return `<label><span>${esc(f.label)}</span><select id="${id}"><option value="">—</option>${opts.map(o => `<option value="${esc(o.v)}" ${String(o.v) === String(val) ? "selected" : ""}>${esc(o.l)}</option>`).join("")}</select></label>`;
  }
  const t = f.type === "money" || f.type === "number" ? "number" : f.type === "date" ? "date" : "text";
  return `<label><span>${esc(f.label)}${f.required ? " *" : ""}</span><input id="${id}" type="${t}" step="any" value="${esc(val == null ? "" : val)}" ${f.readonly ? "disabled" : ""}></label>`;
}
function collect(def) {
  const row = {};
  for (const f of def.fields) {
    const el = $("#f_" + f.key); if (!el || f.readonly) continue;
    let v = f.type === "bool" ? el.checked : el.value;
    if ((f.type === "json" || f.type === "multi") && v !== "") { try { v = JSON.parse(v); } catch (e) { toast("Invalid JSON in " + f.label); throw e; } }
    if (f.type === "money" || f.type === "number") v = v === "" ? null : Number(v);
    row[f.key] = v;
  }
  return row;
}
async function openForm(key, id, onDone) {
  const defs = (await api("/meta/entities")).entities;
  const def = defs[key];
  const registry = await api("/meta");
  let row = {};
  if (id != null) { const rows = await entityRows(key); row = rows.find(r => String(r[def.pk] ?? r.id) === String(id)) || {}; }
  const fields = def.fields.filter(f => !["tenant_id"].includes(f.key));
  $("#modal").innerHTML = `<div class="p-modal"><div class="p-modal-box"><div class="p-modal-head"><h3>${id != null ? "Edit" : "New"} ${esc(def.label.replace(/s$/, ""))}</h3><button id="mClose">✕</button></div>
    <div class="p-form" id="mForm">${await Promise.all(fields.map(f => fieldInput(f, row[f.key], registry))).then(a => a.join(""))}
      <div style="display:flex;gap:10px;margin-top:8px"><button class="p-btn primary" id="mSave">Save</button><button class="p-btn" id="mCancel">Cancel</button></div></div></div></div>`;
  $("#modal").classList.remove("hidden");
  const close = () => { const m = $("#modal"); m.innerHTML = ""; m.classList.add("hidden"); };
  $("#mClose").onclick = $("#mCancel").onclick = close;
  $("#mSave").onclick = async () => {
    try {
      const body = collect(def);
      if (id != null) await api(`/meta/entity/${key}/${encodeURIComponent(id)}`, "PUT", body);
      else {
        if (def.pkType === "text" && body[def.pk]) await api(`/meta/entity/${key}`, "POST", body);
        else await api(`/meta/entity/${key}`, "POST", body);
      }
      close(); toast("Saved"); onDone && onDone();
    } catch (e) { toast(e.message); }
  };
}
async function entityTable(key, opts = {}) {
  const defs = (await api("/meta/entities")).entities;
  const def = defs[key];
  if (!def) return `<div class="p-empty">No access to ${esc(key)}</div>`;
  const rows = await entityRows(key);
  const listFields = def.fields.filter(f => f.list);
  const filtered = opts.filter ? rows.filter(opts.filter) : rows;
  return `<div class="p-panel"><div style="display:flex;gap:10px;margin-bottom:14px;align-items:center">
      <input class="p-search" placeholder="Filter ${esc(def.label.toLowerCase())}…" data-tbl="${key}">
      <span class="p-tag">${filtered.length} records</span><span style="flex:1"></span>
      ${def.perm.write.length ? `<button class="p-btn primary sm" data-new="${key}">+ New</button>` : ""}</div>
    <div class="p-scroll-x"><table class="p-table" data-tblm="${key}"><thead><tr>${listFields.map(f => `<th>${esc(f.label)}</th>`).join("")}<th></th></tr></thead>
      <tbody>${filtered.slice(0, 200).map(r => `<tr>${listFields.map(f => {
        let v = r[f.key];
        if (f.type === "bool") v = v ? "✓" : "—";
        if (f.type === "money") v = v != null ? money(v) : "";
        if (f.key === "title" || f.key === "name") v = `<span class="t-emoji">${esc(r.emoji || "")}</span> ${esc(String(v).slice(0, 60))}`;
        if (["status", "lifecycle"].includes(f.key)) v = `<span class="badge ${esc(v)}">${esc(v)}</span>`;
        return `<td>${v == null ? "" : v}</td>`;
      }).join("")}<td style="text-align:right;white-space:nowrap">
        ${def.perm.write.length ? `<button class="p-btn sm" data-edit="${key}" data-id="${esc(r[def.pk] ?? r.id)}">Edit</button>
        <button class="p-btn sm danger" data-del="${key}" data-id="${esc(r[def.pk] ?? r.id)}">✕</button>` : ""}</td></tr>`).join("")}</tbody></table></div></div>`;
}
document.addEventListener("click", async e => {
  const nb = e.target.closest("[data-new]"), eb = e.target.closest("[data-edit]"), db = e.target.closest("[data-del]");
  try {
    if (nb) openForm(nb.dataset.new, null, render);
    if (eb) openForm(eb.dataset.edit, eb.dataset.id, render);
    if (db) { if (!confirm("Delete this record?")) return; await api(`/meta/entity/${db.dataset.del}/${encodeURIComponent(db.dataset.id)}`, "DELETE"); toast("Deleted"); render(); }
  } catch (err) { toast(err.message); }
});
document.addEventListener("input", e => {
  const inp = e.target.closest("[data-tbl]");
  if (!inp) return;
  const q = inp.value.toLowerCase();
  document.querySelectorAll(`[data-tblm="${inp.dataset.tbl}"] tbody tr`).forEach(tr => {
    tr.style.display = tr.textContent.toLowerCase().includes(q) ? "" : "none";
  });
});

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
async function vPayments() {
  const g = await api("/admin/gateways");
  return `
  <div class="p-panel"><h2>Payment gateways · ${esc(g.country.name)} (${esc(g.country.currency)})</h2>
    <p class="p-tag">Enable gateways available in your country. Secrets are stored server-side and never sent to the browser.</p>
    <table class="p-table"><thead><tr><th></th><th>Gateway</th><th>Methods</th><th>Fee</th><th>Mode</th><th>Enabled</th><th>Primary</th><th></th></tr></thead>
    <tbody>${g.gateways.map(x => `<tr><td class="t-emoji">${x.emoji}</td><td><b>${esc(x.name)}</b><br><span class="p-tag">${esc(x.desc || "")}</span></td>
      <td class="p-tag">${esc((x.methods || []).join(", "))}</td><td>${x.feePct}%${x.feeFixed ? " + " + money(x.feeFixed) : ""}</td>
      <td><select data-gwmode="${x.id}"><option ${x.mode === "sandbox" ? "selected" : ""}>sandbox</option><option ${x.mode === "live" ? "selected" : ""}>live</option></select></td>
      <td><input type="checkbox" data-gwen="${x.id}" ${x.enabled ? "checked" : ""}></td>
      <td><input type="radio" name="gwprimary" data-gwpri="${x.id}" ${x.primary ? "checked" : ""} ${x.enabled ? "" : "disabled"}></td>
      <td><button class="p-btn sm" data-gwtest="${x.id}">Test</button> <button class="p-btn sm" data-gwcfg="${x.id}">Configure</button></td></tr>`).join("")}</tbody></table>
    <div style="margin-top:14px;display:flex;gap:10px"><button class="p-btn primary" id="gwSave">Save gateway config</button></div></div>
  <div class="p-grid2">
    <div class="p-panel"><h2>Shipping carriers</h2><table class="p-table"><thead><tr><th></th><th>Carrier</th><th>ETA</th><th>Base fee</th></tr></thead>
      <tbody>${g.carriers.map(c => `<tr><td class="t-emoji">${c.emoji}</td><td>${esc(c.name)}</td><td>${c.eta[0]}–${c.eta[1]} days</td><td>${c.baseFee ? money(c.baseFee) : "—"}</td></tr>`).join("") || '<tr><td colspan="4" class="p-empty">None enabled</td></tr>'}</tbody></table></div>
    <div class="p-panel"><h2>Notifications</h2><p class="p-tag">Active channels: ${g.notifiers.map(n => n.emoji + " " + esc(n.name)).join(", ") || "console log"}</p>
      <p class="p-tag">Order events are dispatched to every enabled channel (audit-logged).</p></div>
  </div>
  <div class="p-panel"><h2>Payments ledger</h2><div id="payLedger"></div></div>`;
}
async function vSettings() {
  const { settings: st, countries, taxModes, currencies } = await api("/admin/settings");
  const geo = { countries, taxModes, currencies };
  const reg = await api("/meta");
  const sec = (name, title, html) => `<div class="p-panel" data-sec="${name}"><h2>${title}</h2>${html}</div>`;
  const inp = (path, label, val, type = "text") => `<label><span>${label}</span><input data-set="${path}" type="${type}" step="any" value="${esc(val)}"></label>`;
  return `
  ${sec("brand", "Brand", `<div class="p-form"><div class="row">
    ${inp("brand.name", "Store name", st.brand.name)}${inp("brand.wordmark", "Wordmark", st.brand.wordmark)}</div>
    ${inp("brand.tagline", "Tagline", st.brand.tagline)}${inp("brand.supportEmail", "Support email", st.brand.supportEmail)}
    <label><span>Logo (emoji, text or inline SVG)</span><textarea data-set="brand.logo" rows="2">${esc(st.brand.logo || "")}</textarea></label>
    ${inp("brand.poweredBy", "Powered-by line", st.brand.poweredBy)}
    ${inp("brand.footerNote", "Footer note ({year} {brand})", st.brand.footerNote)}</div>`)}
  ${sec("theme", "Theme & Aesthetics", `<div class="p-form"><div class="row3">
    ${inp("theme.bg", "Background", st.theme.bg, "color")}${inp("theme.surface", "Surface", st.theme.surface, "color")}${inp("theme.ink", "Ink", st.theme.ink, "color")}
    ${inp("theme.header", "Header", st.theme.header, "color")}${inp("theme.accent", "Accent", st.theme.accent, "color")}${inp("theme.accentDeep", "Accent deep", st.theme.accentDeep, "color")}
    ${inp("theme.link", "Link", st.theme.link, "color")}${inp("theme.star", "Stars", st.theme.star, "color")}${inp("theme.deal", "Deal red", st.theme.deal, "color")}
    </div><div class="row">
    ${inp("theme.radius", "Corner radius", st.theme.radius)}${inp("theme.radiusBtn", "Button radius", st.theme.radiusBtn)}</div>
    ${inp("theme.fontDisplay", "Display font stack", st.theme.fontDisplay)}${inp("theme.fontBody", "Body font stack", st.theme.fontBody)}
    <label><span>Custom CSS</span><textarea data-set="theme.customCSS" rows="4">${esc(st.theme.customCSS || "")}</textarea></label>
    <div class="swatch-row">${[["Gold Noir", "#C6A15B", "#0C0E13"], ["Rose Atelier", "#B76E79", "#1A1214"], ["Emerald", "#2E8B6E", "#0E1A16"], ["Midnight Blue", "#5B9BD5", "#0B1220"], ["Terracotta", "#C46A4A", "#1C1210"]].map(([n, a, h]) => `<button class="swatch" title="${n}" data-preset="${a}|${h}" style="background:linear-gradient(135deg,${a},${h})"></button>`).join("")}</div></div>`)}
  ${sec("commerce", "Commerce & Localization", `<div class="p-form"><div class="row3">
    <label><span>Country <em class="p-tag">(drives currency, symbol, locale, default tax — managed in Platform → Geo)</em></span><select data-set="commerce.country">${geo.countries.map(c => `<option ${st.commerce.country === c.code ? "selected" : ""} value="${c.code}">${esc(c.name)} (${esc(c.currency)} ${esc(c.symbol)})</option>`).join("")}</select></label>
    <label><span>Currency <em class="p-tag">(default: jurisdiction currency — pick another to sell in a different settlement currency at live FX)</em></span><select data-set="commerce.currency"><option value="">— from country (${esc(geo.countries.find(c => c.code === st.commerce.country) ? geo.countries.find(c => c.code === st.commerce.country).currency : "")}) —</option>${geo.currencies.map(x => `<option value="${x.code}" ${st.commerce.currency === x.code ? "selected" : ""}>${esc(x.name)} (${x.code} ${esc(x.symbol)}) · 1=${x.usd} USD</option>`).join("")}</select></label>
    ${inp("commerce.symbol", "Symbol (blank = from country)", st.commerce.symbol || "")}
    <label><span>Locale <em class="p-tag">(blank = from country)</em></span><input data-set="commerce.locale" value="${esc(st.commerce.locale || "")}"></label>
    <label><span>Tax mode <em class="p-tag">(blank = country default)</em></span><select data-set="commerce.taxMode"><option value="">— country default —</option>${geo.taxModes.map(t => `<option value="${t.key}" ${st.commerce.taxMode === t.key ? "selected" : ""}>${esc(t.label)} (${esc(t.description || t.key)})</option>`).join("")}</select></label>
    <label><span>Tax rate (0-1, blank = country default)</span><input data-set="commerce.taxRate" type="number" step="any" value="${st.commerce.taxRate == null ? "" : st.commerce.taxRate}"></label>
    ${inp("commerce.freeShipThreshold", "Free shipping ≥", st.commerce.freeShipThreshold, "number")}${inp("commerce.shipFee", "Shipping fee", st.commerce.shipFee, "number")}
    ${inp("commerce.daysPriority", "Priority days", st.commerce.daysPriority, "number")}${inp("commerce.daysStandard", "Standard days", st.commerce.daysStandard, "number")}
    ${inp("commerce.perPage", "Results per page", st.commerce.perPage, "number")}${inp("commerce.cartMaxQty", "Cart max qty", st.commerce.cartMaxQty, "number")}
    </div></div>`)}
  ${sec("features", "Feature Flags", `<div class="p-form"><div class="row3">
    ${Object.entries(st.features).map(([k, v]) => `<label style="display:flex;gap:8px;align-items:center"><input type="checkbox" data-feat="${k}" ${v ? "checked" : ""}> ${esc(k)}</label>`).join("")}
    </div></div>`)}
  ${sec("copy", "Copy & Wording", `<div class="p-form"><div class="row">
    ${Object.entries(st.copy).slice(0, 24).map(([k, v]) => inp("copy." + k, k, v)).join("")}</div></div>`)}
  ${sec("mode", "Deployment Mode", `<div class="p-form"><div class="row">
    <label><span>Mode</span><select id="modeSel">${reg.deployModes.map(m => `<option value="${m.key}" ${TT.tenant.mode === m.key ? "selected" : ""}>${m.name} — ${m.desc}</option>`).join("")}</select></label>
    <label><span>Industries (empty = all)</span><input id="modeInds" value="${esc((TT.tenant.industries || []).join(","))}" placeholder="furniture,grocery"></label></div>
    <button class="p-btn" id="modeSave">Apply mode</button>`)}
  <div style="display:flex;gap:12px"><button class="p-btn primary" id="setSave">Save all settings</button>
    <button class="p-btn danger" id="setReset">Reset to defaults</button></div>`;
}
async function vModules() {
  const [mkt, own] = await Promise.all([api("/market"), api("/modules")]);
  const has = id => own.installed.some(x => x.id === id);
  const cats = {};
  mkt.modules.forEach(m => { (cats[m.category] = cats[m.category] || []).push(m); });
  return `
  <p class="p-tag" style="margin:0 0 14px">This store's capabilities: ${own.capabilities.map(c => `<span class="p-chip">${esc(c)}</span>`).join(" ")} — purchase more below; billed via store invoice (MOD-*).</p>
  ${Object.entries(cats).map(([cat, ms]) => `<div class="p-panel"><h2>${esc(cat)}</h2>
    ${ms.map(m => {
    const on = has(m.id);
    return `<div style="display:flex;gap:14px;align-items:center;padding:10px 0;border-bottom:1px solid var(--p-line)">
      <div style="flex:1"><b>${esc(m.name)}</b> <span class="p-tag">${m.price > 0 ? "$" + m.price + " one-time" : "free"} · ${m.capabilities.map(esc).join(", ")}</span><br><span class="p-tag">${esc(m.summary || "")}</span></div>
      ${on ? `<button class="p-btn sm danger" data-rel="${esc(m.id)}">Release</button>` : `<button class="p-btn sm primary" data-buy="${esc(m.id)}">Purchase</button>`}</div>`;
  }).join("")}</div>`).join("")}`;
}
document.addEventListener("click", async e => {
  const buy = e.target.closest("[data-buy]"), rel = e.target.closest("[data-rel]");
  if (!buy && !rel) return;
  try {
    if (rel) { await api("/modules/release", "POST", { module_id: rel.dataset.rel }); toast("Module released"); render(); return; }
    const mkt = await api("/market"); const m = mkt.modules.find(x => x.id === buy.dataset.buy);
    const fields = (m.fields || []);
    const mm = modal(`<div class="p-modal-head"><h3>Purchase — ${esc(m.name)}</h3><button data-mclose>✕</button></div><div class="p-form">
      <p class="p-tag">${m.price > 0 ? "An invoice of $" + m.price + " (MOD-*) will be created and marked collected." : "Free module."}</p>
      ${fields.map(f => `<label><span>${esc(f.label || f.key)}</span><input data-mcfg="${esc(f.key)}" placeholder="${esc(f.key)}"></label>`).join("")}
      <button class="p-btn primary" id="mbuyGo">Confirm purchase</button></div>`);
    mm.querySelector("#mbuyGo").onclick = async () => {
      const cfg = {};
      mm.querySelectorAll("[data-mcfg]").forEach(i => { if (i.value) cfg[i.dataset.mcfg] = (i.value === "true" || i.value === "false") ? i.value === "true" : (isNaN(+i.value) ? i.value : +i.value); });
      try { const r = await api("/modules/purchase", "POST", { module_id: m.id, config: cfg }); mm.innerHTML = ""; toast(r.invoice ? "Purchased · invoice " + r.invoice : "Installed"); render(); } catch (e2) { toast(e2.message); }
    };
  } catch (err) { toast(err.message); }
});

function modal(html) {
  let m = document.getElementById("modal");
  if (!m) { m = document.createElement("div"); m.id = "modal"; document.body.appendChild(m); }
  m.innerHTML = `<div class="p-modal"><div class="p-modal-box">${html}</div></div>`;
  return m;
}
async function vBilling() {
  const [b, own] = await Promise.all([api("/admin/billing"), api("/modules")]);
  const canPay = own.capabilities.includes("billingPro");
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
document.addEventListener("click", async e => {
  const pay = e.target.closest("[data-payinv]");
  if (pay) {
    const sel = document.querySelector(`[data-inv="${pay.dataset.payinv}"]`);
    try { const r = await api("/billing/invoices/" + pay.dataset.payinv + "/pay", "POST", { gateway: sel ? sel.value : undefined }); toast(r.ok ? "Invoice " + r.number + " paid" : "Failed"); render(); } catch (err) { toast(err.message); }
  }
});
async function vAudit() {
  const a = await api("/admin/audit");
  return `<div class="p-panel"><h2>Audit trail · ${a.entries.length} entries</h2>
    <input class="p-search" placeholder="Filter…" id="auditQ" style="margin-bottom:12px">
    <div class="p-scroll-x"><table class="p-table" id="auditTbl"><thead><tr><th>When</th><th>Actor</th><th>Action</th><th>Entity</th><th>Ref</th><th>Detail</th></tr></thead>
    <tbody>${a.entries.map(e => `<tr><td>${esc(e.created_at)}</td><td>${esc(e.actor_type)} · ${esc(e.actor_name || "")}</td><td><b>${esc(e.action)}</b></td><td>${esc(e.entity || "")}</td><td>${esc(e.entity_id || "")}</td><td class="p-tag">${esc((e.meta || "").slice(0, 90))}</td></tr>`).join("")}</tbody></table></div></div>`;
}
async function vMonitor() {
  const m = await api("/admin/monitor");
  const max = Math.max(1, ...m.series.map(x => x.req));
  return `
  <div class="p-cards">
    <div class="p-stat"><em>Requests</em><b>${m.totals.req}</b><small>${m.totals.err} errors</small></div>
    <div class="p-stat"><em>Avg latency</em><b>${m.totals.avgMs}ms</b></div>
  </div>
  <div class="p-panel"><h2>Live traffic · last 30 min</h2>
    <div class="p-chart">${m.series.map(x => `<div class="bar" style="height:${Math.max(3, x.req / max * 100)}%" data-tip="${new Date(x.t).toLocaleTimeString()}: ${x.req} req"></div>`).join("")}</div></div>
  <div class="p-panel"><h2>Endpoints</h2><table class="p-table"><thead><tr><th>Endpoint</th><th class="num">Calls</th><th class="num">Errors</th><th class="num">Avg ms</th></tr></thead>
    <tbody>${m.endpoints.map(x => `<tr><td>${esc(x.endpoint)}</td><td class="num">${x.count}</td><td class="num">${x.err}</td><td class="num">${x.avgMs}</td></tr>`).join("")}</tbody></table></div>`;
}
async function vStudio() {
  const defs = (await api("/meta/entities")).entities;
  const customs = await api("/meta/entity/custom_provider").catch(() => ({ rows: [] }));
  return `
  <div class="p-panel"><h2>Universal Entity Studio</h2>
    <p class="p-tag">Every entity on the platform is metadata. Pick one to browse/edit, or define a brand-new entity — it instantly gets CRUD, validation, audit and UI.</p>
    <div style="display:flex;gap:10px;flex-wrap:wrap;margin:14px 0">${Object.entries(defs).map(([k, d]) => `<button class="p-btn sm ${k === A.studioSel ? "primary" : ""}" data-studio="${k}">${d.icon} ${esc(d.label)}</button>`).join("")}</div>
    <div id="studioBody">${A.studioSel ? await entityTable(A.studioSel) : '<div class="p-empty">Select an entity above</div>'}</div></div>
  <div class="p-panel"><h2>Define a new entity</h2>
    <div class="p-form"><div class="row3">
      <label><span>Key (snake_case)</span><input id="ceKey" placeholder="e.g. service_contract"></label>
      <label><span>Label</span><input id="ceLabel" placeholder="Service Contracts"></label>
      <label><span>Icon</span><input id="ceIcon" placeholder="🧾"></label></div>
    <label><span>Fields (JSON array)</span><textarea id="ceFields" rows="5">[
  {"key":"name","label":"Name","type":"text","required":true,"list":true},
  {"key":"value","label":"Value","type":"money","list":true},
  {"key":"active","label":"Active","type":"bool","list":true}
]</textarea></label>
    <button class="p-btn primary" id="ceSave">Create entity</button></div></div>`;
}

/* ---------- render ---------- */
/* ---------- serialized / contracts / tenders (custom screens over the entity engine) ---------- */
const pj = (x, d) => { try { return JSON.parse(x == null || x === "" ? (d || "null") : x); } catch (e) { return d == null ? null : JSON.parse(d); } };
async function vSerialized() {
  const products = ((await api("/meta/entity/product")).rows || []).map(p => ({ id: p.id, t: p.title || p.id }));
  return `<div class="p-panel"><div style="display:flex;gap:8px;align-items:flex-end;flex-wrap:wrap;margin-bottom:14px">
    <label><span>Bulk-generate units for</span><select id="sbProd">${products.map(p => `<option value="${esc(p.id)}">${esc(String(p.t).slice(0, 40))}</option>`).join("")}</select></label>
    <label><span>Count</span><input id="sbCount" type="number" value="5" min="1" max="500"></label>
    <label><span>Prefix (optional)</span><input id="sbPrefix" placeholder="e.g. SN-2026"></label>
    <button class="p-btn primary sm" id="sbGo">Generate</button></div>
    ${await entityTable("serialized")}</div>`;
}
function wireSerialized() { const g = $("#sbGo"); if (g) g.onclick = async () => { try { const r = await api("/admin/serialized/bulk", "POST", { product_id: $("#sbProd").value, count: Number($("#sbCount").value) || 1, prefix: $("#sbPrefix").value || undefined }); toast("Generated " + r.created + " serialized units"); render(); } catch (e) { toast(e.message); } }; }
async function vContracts() {
  const rows = (await api("/meta/entity/contract")).rows || [];
  return `<div class="p-panel"><div style="display:flex;gap:8px;align-items:flex-end;flex-wrap:wrap;margin-bottom:14px">
    <label><span>Buyer name</span><input id="ncName" placeholder="Acme Corp"></label>
    <label><span>Buyer email</span><input id="ncEmail" placeholder="buy@acme.example"></label>
    <label><span>Product ids (CSV)</span><input id="ncProducts" placeholder="VR-HARD-01"></label>
    <label><span>Fixed unit price</span><input id="ncPrice" type="number" step="0.01" placeholder="10.00"></label>
    <label><span>Min qty</span><input id="ncMin" type="number" value="10"></label>
    <button class="p-btn primary sm" id="ncGo">+ New contract</button></div>
    <div class="p-scroll-x"><table class="p-table"><thead><tr><th>Ref</th><th>Buyer</th><th>Products</th><th>Price</th><th>Min</th><th>Valid</th><th>Status</th><th></th></tr></thead>
    <tbody>${rows.map(c => { const pr = pj(c.pricing, "{}") || {}, pid = pj(c.product_ids, "[]") || []; const fp = pr.fixed ? Object.values(pr.fixed)[0] : (Array.isArray(pr.tiers) && pr.tiers[0] ? pr.tiers[0].price : null); return `<tr><td><b>${esc(c.ref)}</b></td><td>${esc(c.buyer_name)}<br><span class="p-tag">${esc(c.buyer_email)}</span></td><td>${esc((pid).join(", "))}</td><td>${fp != null ? money(fp) : "—"}</td><td>${esc(c.min_qty)}</td><td>${esc(c.valid_from || "")}→${esc(c.valid_to || "")}</td><td><span class="badge ${esc(c.status)}">${esc(c.status)}</span></td><td style="white-space:nowrap;text-align:right">${c.status !== "active" ? `<button class="p-btn sm" data-cstat="${c.id}" data-v="active">Activate</button>` : ""}${c.status === "active" ? `<button class="p-btn sm" data-cstat="${c.id}" data-v="expired">Expire</button> <button class="p-btn sm danger" data-cstat="${c.id}" data-v="terminated">Terminate</button>` : ""} <button class="p-btn sm" data-cedit="${c.id}" data-id="${esc(c.id)}">Edit</button> <button class="p-btn sm danger" data-cdel="${c.id}">✕</button></td></tr>`; }).join("")}</tbody></table></div></div>`;
}
function wireContracts() {
  $$("[data-cstat]").forEach(b => b.onclick = async () => { try { await api(`/admin/contracts/${b.dataset.cstat}/status`, "PUT", { status: b.dataset.v }); toast("Contract " + b.dataset.v); render(); } catch (e) { toast(e.message); } });
  $$("[data-cedit]").forEach(b => b.onclick = () => openForm("contract", b.dataset.id, render));
  $$("[data-cdel]").forEach(b => b.onclick = async () => { if (!confirm("Delete contract?")) return; try { await api(`/meta/entity/contract/${b.dataset.cdel}`, "DELETE"); toast("Deleted"); render(); } catch (e) { toast(e.message); } });
  const g = $("#ncGo"); if (g) g.onclick = async () => {
    const ids = $("#ncProducts").value.split(",").map(x => x.trim()).filter(Boolean), pv = Number($("#ncPrice").value), pricing = {}; if (ids.length && pv) { pricing.fixed = {}; ids.forEach(id => pricing.fixed[id] = pv); }
    try { const r = await api("/admin/contracts", "POST", { buyer_name: $("#ncName").value, buyer_email: $("#ncEmail").value, product_ids: ids, pricing, min_qty: Number($("#ncMin").value) || 1 }); toast("Contract " + r.ref); render(); } catch (e) { toast(e.message); }
  };
}
async function vTenders() {
  const rows = (await api("/meta/entity/tender")).rows || [];
  return `<div class="p-panel"><div style="display:flex;gap:8px;align-items:flex-end;flex-wrap:wrap;margin-bottom:14px">
    <label><span>Title</span><input id="ntTitle" placeholder="Annual fastener supply"></label>
    <label><span>Issuing org</span><input id="ntOrg" placeholder="BuildRight LLC"></label>
    <label><span>Budget</span><input id="ntBudget" type="number" step="1" placeholder="120000"></label>
    <button class="p-btn primary sm" id="ntGo">+ New tender</button></div>
    <div class="p-scroll-x"><table class="p-table"><thead><tr><th>Ref</th><th>Title</th><th>Org</th><th>Budget</th><th>Closes</th><th>Status</th><th></th></tr></thead>
    <tbody>${rows.map(t => `<tr><td><b>${esc(t.ref)}</b></td><td>${esc(t.title)}</td><td>${esc(t.buyer_org)}</td><td>${t.budget ? money(t.budget) : "—"}</td><td>${esc(t.close_at || "")}</td><td><span class="badge ${esc(t.status)}">${esc(t.status)}</span>${t.awarded_contract_id ? ` <span class="p-tag">→ contract #${esc(t.awarded_contract_id)}</span>` : ""}</td><td style="white-space:nowrap;text-align:right">${(t.status === "open" || t.status === "in_review") ? `<button class="p-btn sm primary" data-taward="${t.id}">Award → contract</button>` : ""} <button class="p-btn sm danger" data-tdel="${t.id}">✕</button></td></tr>`).join("")}</tbody></table></div></div>`;
}
function wireTenders() {
  $$("[data-taward]").forEach(b => b.onclick = async () => { try { const r = await api(`/admin/tenders/${b.dataset.taward}/award`, "POST", {}); toast("Awarded → " + r.contract_ref); render(); } catch (e) { toast(e.message); } });
  $$("[data-tdel]").forEach(b => b.onclick = async () => { if (!confirm("Delete tender?")) return; try { await api(`/meta/entity/tender/${b.dataset.tdel}`, "DELETE"); toast("Deleted"); render(); } catch (e) { toast(e.message); } });
  const g = $("#ntGo"); if (g) g.onclick = async () => { try { const r = await api("/admin/tenders", "POST", { title: $("#ntTitle").value, buyer_org: $("#ntOrg").value, budget: Number($("#ntBudget").value) || 0 }); toast("Tender " + r.ref); render(); } catch (e) { toast(e.message); } };
}

/* ---------- AI Studio (capability layer) ---------- */
async function vAI() {
  const ov = await api("/ai");
  const cap = ov.capabilities || [];
  const st = ov.settings || {};
  const premProviders = (await api("/meta")).providersAi || [];
  const tierBadge = t => `<span class="badge ${t === "premium" ? "active" : "processing"}">${esc(t)}</span>`;
  return `<div class="p-panel"><div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
      <h2 style="margin:0">🤖 AI Studio</h2>
      <span class="p-tag">store tier: ${tierBadge(ov.plan.tier)}</span>
      <span style="flex:1"></span>
      <span class="p-tag">${(ov.usage && ov.usage.totalCalls) || 0} calls · ${money(ov.usage && ov.usage.totalCost || 0)} accrued</span>
    </div>
    <p style="margin:0 0 14px;color:var(--p-muted);font-size:13px">Free built-in engine is on for every store (1st priority). Premium models (OpenAI / Anthropic / Stability / Google Vision) unlock for paid stores or after buying the <b>AI Premium</b> module — configure provider + model per capability below.</p>
    <div class="p-cards" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px;margin-bottom:16px">
      ${cap.map(c => `<div class="p-stat" style="border:1px solid var(--p-line);border-radius:12px;padding:12px">
        <div style="display:flex;align-items:center;gap:6px"><b>${esc(c.icon)} ${esc(c.name)}</b>${tierBadge(c.tier)}</div>
        <div style="font-size:12px;color:var(--p-muted);margin:4px 0">${esc(c.desc)}</div>
        <div style="font-size:12px">Provider: <b>${c.provider ? esc(c.provider.emoji + " " + c.provider.name) : "—"}</b> · model <code>${esc(c.model || "—")}</code></div>
        <div style="font-size:12px;color:${c.status === "premium_locked" ? "var(--p-red)" : "var(--p-muted)"}">Status: ${esc(c.status.replace("_", " "))} · ${c.remaining}/${c.limits.perDay} left today</div>
        <label style="display:flex;align-items:center;gap:6px;font-size:12px;margin-top:8px">
          <input type="checkbox" data-aiprem="${esc(c.key)}" ${st[c.key] && st[c.key].premium ? "checked" : ""} ${c.tier === "premium" ? "" : "disabled"}> use premium model
        </label>
        <div style="display:flex;gap:6px;margin-top:6px">
          <select data-aiprov="${esc(c.key)}" ${c.tier === "premium" ? "" : "disabled"}><option value="">provider…</option>${(premProviders.filter(p => (c.key)).map(p => `<option value="${esc(p.id)}" ${st[c.key] && st[c.key].provider === p.id ? "selected" : ""}>${esc(p.name)}</option>`).join(""))}</select>
          <input data-aimodel="${esc(c.key)}" placeholder="model" value="${esc((st[c.key] || {}).model || "")}" style="flex:1" ${c.tier === "premium" ? "" : "disabled"}>
        </div>
      </div>`).join("")}
    </div>
    <div class="p-panel"><h3>Run a capability</h3>
      <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end">
        <label><span>Capability</span><select id="aiCapSel">${cap.map(c => `<option value="${esc(c.key)}">${esc(c.name)}</option>`).join("")}</select></label>
        <label><span>Product id (reco/image)</span><input id="aiPid" placeholder="LX-ELS-001"></label>
        <label><span>Columns (analysis, CSV)</span><input id="aiCols" placeholder="price,brand,rating"></label>
        <button class="p-btn primary sm" id="aiRun">Run</button>
        <button class="p-btn sm" id="aiTask">Queue as task</button>
      </div>
      <pre id="aiOut" class="p-code" style="margin-top:10px;max-height:340px;overflow:auto;background:#0b0d12;color:#cfe;border-radius:10px;padding:10px;font-size:12px">Run a capability to see output…</pre></div>
    <div class="p-panel"><h3>Usage ledger</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>Capability</th><th>Provider</th><th>Tier</th><th class="num">Units</th><th class="num">Cost</th><th class="num">Calls</th><th>Last</th></tr></thead>
      <tbody>${(ov.usage && ov.usage.rows || []).map(u => `<tr><td>${esc(u.capability)}</td><td>${esc(u.provider)}</td><td>${esc(u.tier)}</td><td class="num">${u.units}</td><td class="num">${money(u.cost)}</td><td class="num">${u.calls}</td><td>${esc(u.last || "")}</td></tr>`).join("") || '<tr><td colspan="7">No AI calls yet.</td></tr>'}</tbody></table></div></div>
    <div class="p-panel"><h3>Recent tasks</h3><div id="aiTasks">${(await api("/ai/tasks")).tasks.map(t => `<div class="p-tag" style="display:block;margin:4px 0">${esc(t.capability)} · <b>${esc(t.status)}</b> · ${money(t.cost || 0)}</div>`).join("") || "No tasks."}</div></div>
    </div>`;
}
function wireAI() {
  const save = async () => {
    const ai = {};
    $$("[data-aiprem]").forEach(cb => { const k = cb.dataset.aiprem; ai[k] = ai[k] || {}; ai[k].premium = cb.checked; });
    $$("[data-aiprov]").forEach(sel => { const k = sel.dataset.aiprov; ai[k] = ai[k] || {}; if (sel.value) ai[k].provider = sel.value; });
    $$("[data-aimodel]").forEach(inp => { const k = inp.dataset.aimodel; ai[k] = ai[k] || {}; if (inp.value) ai[k].model = inp.value; });
    try { await api("/admin/settings", "PUT", { ai }); toast("AI configuration saved"); render(); } catch (e) { toast(e.message); }
  };
  $$("[data-aiprem],[data-aiprov],[data-aimodel]").forEach(el => el.onchange = el.onblur = save);
  const collect = () => { const cap = $("#aiCapSel").value, p = {}; if (cap === "product_recommendation" || cap === "image_processing") { if ($("#aiPid").value) p.product_id = $("#aiPid").value; } if (cap === "data_analysis" && $("#aiCols").value) p.columns = $("#aiCols").value.split(",").map(x => x.trim()).filter(Boolean); return { cap, p }; };
  const run = async () => { const { cap, p } = collect(); try { const r = await api("/ai/run/" + encodeURIComponent(cap), "POST", p); $("#aiOut").textContent = JSON.stringify(r, null, 1); toast(cap + " · " + (r.tier || "") + " · " + money(r.cost || 0)); } catch (e) { $("#aiOut").textContent = "⚠ " + e.message; toast(e.message); } };
  const task = async () => { const { cap, p } = collect(); try { const r = await api("/ai/tasks", "POST", { capability: cap, params: p, runNow: true }); $("#aiOut").textContent = JSON.stringify(r.tasks.slice(0, 6), null, 1); toast("Queued"); render(); } catch (e) { toast(e.message); } };
  if ($("#aiRun")) $("#aiRun").onclick = run; if ($("#aiTask")) $("#aiTask").onclick = task;
}

/* ---------- Central Offers & Coupons (data-driven builder) ---------- */
/* ═══ GOIP Ω∞ — store surface: the constitution as this store can use it ═══
   A store admin gets the decision tester (what applies, what does not, and WHY), the store's own
   value exchanges (its own + the global ones it inherits), subject entitlements and unit balances,
   its funding budgets and settlements, and the capability list it is entitled to call. */
async function vGoip() {
  const [man, ex, tre] = await Promise.all([api("/goip"), api("/goip/exchanges"), api("/goip/treasury").catch(() => ({ budgets: [], treasury: { positions: [] } }))]);
  const entitled = man.entitled;
  const opt = (a, sel) => (a || []).map(x => `<option value="${esc(x.key || x)}"${(x.key || x) === sel ? " selected" : ""}>${esc(x.name || x)}</option>`).join("");
  const rows = (ex.exchanges || []).map(o => `<tr>
    <td><b>${esc(o.name)}</b>${o.code ? ` <code>${esc(o.code)}</code>` : ""}${o.tenant_id === 0 ? ' <span class="p-tag">INHERITED</span>' : ""}</td>
    <td class="p-tag">${esc(o.domain || "incentive")}<br>${esc(o.benefit || o.type)}</td>
    <td class="p-tag">${esc(o.reality || "any")} · ${esc((JSON.parse(o.spatial_spec || "{}").include || []).join(",") || "anywhere")} · ${esc(o.economic_unit || o.currency)}</td>
    <td>${esc(o.funder)}${o.funder_ref ? " " + esc(o.funder_ref) : ""}</td>
    <td class="num">${esc(o.value)}</td><td class="num">${o.used}/${o.usage_limit || "∞"}</td>
    <td><span class="badge ${(o.governance || {}).state === "published" || o.status === "active" ? "published" : "draft"}">${esc((o.governance || {}).state || o.status)}</span></td></tr>`).join("")
    || '<tr><td colspan="7">No value exchanges yet.</td></tr>';
  return `<div class="p-panel"><h2>Ω∞ GOIP — Value Exchange</h2>
    <p style="color:var(--p-muted);font-size:13px;margin:0 0 8px">Every offer, coupon, cashback, reward, voucher, membership, subsidy or commission this store runs is one <b>value exchange</b> resolved against the live context: reality · time · place · economy · governance · audience. This screen is where you test what applies, and why it does not when it does not.</p>
    ${entitled === false ? '<p class="p-tag" style="padding:8px 10px;border-radius:8px;background:rgba(245,158,11,.12)">This store has not purchased <b>GOIP Ω∞</b> — reads work, capability calls are metered at zero and some writes stay closed. Buy it under <b>🧩 Modules</b>.</p>' : '<p class="p-tag"><span class="badge published">entitled</span> GOIP is installed on this store — all 22 capabilities are callable and metered.</p>'}
  </div>

  <div class="p-panel"><h3>Decision tester — ask the platform what applies right now</h3>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;align-items:end">
      <label><span>Capability</span><select id="gzCap"><option value="apply">apply — what would apply</option><option value="discover">discover — what is available</option><option value="validate">validate — is this code usable</option><option value="compare">compare — rank every candidate</option><option value="recommend" disabled>recommend (via discover)</option></select></label>
      <label><span>Cart amount</span><input id="gzAmount" type="number" value="200"></label>
      <label><span>Code</span><input id="gzCode" placeholder="GOIPWELCOME"></label>
      <label><span>Place</span><select id="gzPlace"><option value="">store default</option>${opt(man.spatial.nodes)}</select></label>
      <label><span>Economic unit</span><select id="gzUnit"><option value="">store currency</option>${opt(man.economic.units)}</select></label>
      <label><span>Subject (owner)</span><input id="gzOwner" placeholder="t1:u:2"></label>
      <label><span>Objective</span><select id="gzObj">${opt(["max_benefit", "min_cost", "max_margin", "max_conversion", "balanced"])}</select></label>
      <button class="p-btn primary sm" id="gzRun">Run</button>
    </div>
    <div id="gzSummary" style="margin-top:10px"></div>
    <pre id="gzOut" class="p-scroll-x" style="background:#0b1020;color:#9ae6b4;padding:10px;border-radius:8px;max-height:320px;overflow:auto;font-size:12px">—</pre>
  </div>

  <div class="p-panel"><h3>Value exchanges (this store + inherited)</h3><div class="p-scroll-x"><table class="p-table">
    <thead><tr><th>Name</th><th>Domain · Benefit</th><th>Context</th><th>Funder</th><th class="num">Value</th><th class="num">Used</th><th>State</th></tr></thead>
    <tbody>${rows}</tbody></table></div></div>

  <div class="p-panel"><h3>Subject lookup — entitlements &amp; non-money balances</h3>
    <div style="display:flex;gap:8px;align-items:end;flex-wrap:wrap">
      <label><span>Subject (owner)</span><input id="gzSubj" placeholder="t1:u:2"></label>
      <button class="p-btn sm" id="gzSubjGo">Look up</button>
      <span class="p-tag">Entitlements are memberships, tiers, assets and deferred value — benefits that are not money.</span>
    </div>
    <div id="gzSubjOut" style="margin-top:8px"></div></div>

  <div class="p-panel"><h3>Funding &amp; settlement for this store</h3>
    <div class="p-scroll-x"><table class="p-table"><thead><tr><th>Funder</th><th>Domain</th><th>Unit</th><th class="num">Allocated</th><th class="num">Consumed</th><th class="num">Available</th><th class="num">Burn</th></tr></thead><tbody>
      ${(tre.budgets || []).map(b => `<tr><td>${esc(b.funder)}${b.funder_ref ? " " + esc(b.funder_ref) : ""}</td><td class="p-tag">${esc(b.domain)}</td><td>${esc(b.unit)}</td><td class="num">${b.allocated}</td><td class="num">${b.consumed}</td><td class="num">${b.available}</td><td class="num">${b.burn_pct}%</td></tr>`).join("") || '<tr><td colspan="7">No budgets funded for this store yet.</td></tr>'}
    </tbody></table></div>
    <p class="p-tag" style="margin-top:6px">Forecast: ${(tre.forecast && tre.forecast.projection || []).map(p => esc(p.period) + " → " + esc(p.projected_cost)).join(" · ") || "not enough history yet"}</p></div>

  <div class="p-panel"><h3>Capabilities this store can call</h3><div class="p-scroll-x"><table class="p-table">
    <thead><tr><th>Capability</th><th>Stage</th><th>Scope</th><th>Meter</th></tr></thead><tbody>
    ${man.capabilities.map(c => `<tr><td><code>POST /api/goip/${esc(c.key)}</code><br><span class="p-tag">${esc(c.name)}</span></td><td class="p-tag">${esc(c.stage)}</td><td><span class="badge ${c.scope === "platform" ? "draft" : "published"}">${esc(c.scope)}</span></td><td class="p-tag">${esc(c.meter)}</td></tr>`).join("")}
    </tbody></table></div></div>`;
}
function wireGoip() {
  const $i = id => document.getElementById(id);
  const val = id => { const el = $i(id); return el ? el.value : ""; };
  if ($i("gzRun")) $i("gzRun").onclick = async () => {
    const out = $i("gzOut"), sum = $i("gzSummary");
    out.textContent = "…"; sum.innerHTML = "";
    const body = { amount: Number(val("gzAmount")) || 0, coupon: val("gzCode") || undefined, objective: val("gzObj") };
    if (val("gzPlace")) body.spatial = { node: val("gzPlace") };
    if (val("gzUnit")) body.currency = val("gzUnit");
    if (val("gzOwner")) body.owner = val("gzOwner");
    try {
      const r = await api("/goip/" + val("gzCap"), "POST", body);
      const res = r.result || {};
      const applied = (res.applied || []).map(a => `<span class="badge published">${esc(a.name)} · ${esc(a.amount || a.credits || (a.freeShip ? "free ship" : a.grant ? "grant" : ""))}${a.unit ? " " + esc(a.unit) : ""}</span>`).join(" ");
      const rejected = (res.rejected || []).map(x => `<div class="p-tag">✗ <b>${esc(x.name || x.id)}</b> — ${esc((x.reasons || []).join("; "))}</div>`).join("");
      const ctx = res.context ? `<div class="p-tag">context: ${esc(res.context.reality)} · ${esc(res.context.temporal.calendar)} · ${esc(res.context.spatial.node)} · ${esc(res.context.economic.unit)} · segments ${esc((res.context.audience.segments || []).join(","))}</div>` : "";
      sum.innerHTML = (res.discount !== undefined ? `<b>discount ${res.discount}</b> · credits ${res.credits} · free shipping ${res.freeShip ? "yes" : "no"}<br>` : "") + applied + ctx + rejected;
      out.textContent = JSON.stringify(r, null, 2);
    } catch (e) { out.textContent = "⚠️ " + e.message; }
  };
  if ($i("gzSubjGo")) $i("gzSubjGo").onclick = async () => {
    const owner = val("gzSubj"); const box = $i("gzSubjOut"); box.innerHTML = "…";
    try {
      const [ent, led] = await Promise.all([api("/goip/entitlements?owner=" + encodeURIComponent(owner)), api("/wallet/ledger?owner=" + encodeURIComponent(owner))]);
      const units = {}; (led.entries || []).forEach(e => { units[e.currency] = (units[e.currency] || 0) + Number(e.amount); });
      box.innerHTML = `<p class="p-tag">Money wallet: <b>${led.balance}</b> · unit balances: ${Object.entries(units).map(([u, v]) => `<b>${esc(u)} ${Math.round(v * 100) / 100}</b>`).join(" · ") || "none"}</p>
        <table class="p-table"><thead><tr><th>Benefit</th><th>Tier</th><th class="num">Qty</th><th>Unit</th><th>Ends / due</th><th>Status</th></tr></thead><tbody>
        ${(ent.entitlements || []).map(e => `<tr><td>${esc(e.benefit)}</td><td>${esc(e.tier || "—")}</td><td class="num">${e.qty}</td><td>${esc(e.unit || "—")}</td><td>${esc(e.ends || "—")}</td><td><span class="badge ${e.status === "active" ? "published" : "draft"}">${esc(e.status)}</span></td></tr>`).join("") || '<tr><td colspan="6">No entitlements for this subject.</td></tr>'}
        </tbody></table>`;
    } catch (e) { box.innerHTML = '<p class="p-tag">⚠️ ' + esc(e.message) + "</p>"; }
  };
}
async function vOffers() {
  const meta = await api("/meta");
  const [off, cp, an] = await Promise.all([api("/offers"), api("/offers/coupons"), api("/offers/analytics")]);
  const types = meta.offerTypes || [], chans = meta.offerChannels || [], dirs = meta.offerDirections || [], scopes = meta.offerScopes || [], funders = meta.offerFunders || [], stacks = meta.stackingPolicies || [], cKinds = meta.couponKinds || [];
  const opt = (arr, lblFn) => arr.map(x => `<option value="${esc(x.key || x)}">${esc(lblFn ? lblFn(x) : (x.name || x))}</option>`).join("");
  const statusBadge = st => `<span class="badge ${st === "active" ? "published" : "draft"}">${esc(st)}</span>`;
  const row = o => `<tr><td><b>${esc(o.name)}</b>${o.code ? ` <code>${esc(o.code)}</code>` : ""}${o.tenant_id === 0 ? ' <span class="p-tag">GLOBAL</span>' : ""}</td>
    <td>${esc(o.type)}</td><td><span class="p-tag">${esc(o.direction)}</span></td><td>${esc(o.channel)}</td>
    <td>${esc(o.scope_type)}${o.scope && (o.scope.products || o.scope.categories || o.scope.node || o.scope.brands) ? ` <span class="p-tag">${esc([].concat(o.scope.products || o.scope.categories || o.scope.node || o.scope.brands).join(",").slice(0, 30))}</span>` : ""}</td>
    <td>${esc(o.funder)}${o.funder_ref ? ` ${esc(o.funder_ref)}` : ""}</td><td class="num">${esc(o.value)}${esc(o.currency === "USD" ? "%" + (o.type === "percent" || o.type === "flash_percent" ? "" : "") : "")}</td>
    <td class="num">${o.usage_limit ? o.used + "/" + o.usage_limit : o.used}</td><td>${statusBadge(o.status)}</td>
    <td style="text-align:right;white-space:nowrap"><button class="p-btn sm" data-oedit="${o.id}">Edit</button><button class="p-btn sm danger" data-oret="${o.id}">Retire</button></td></tr>`;
  return `<div class="p-panel"><h2>💸 Offers & Coupons</h2>
    <p style="color:var(--p-muted);font-size:13px;margin:0 0 10px">One central engine used by cart, checkout, <b>platform billing</b> and <b>AI</b>. Types / scopes / funders / channels are configurable registries — the form options come from data, not code.</p>
    <div class="p-panel"><h3>New / edit offer</h3>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;align-items:end">
        <label><span>Name</span><input id="oName"></label>
        <label><span>Type</span><select id="oType">${opt(types)}</select></label>
        <label><span>Value</span><input id="oValue" type="number" step="0.01" value="10"></label>
        <label><span>Code (optional → coupon)</span><input id="oCode"></label>
        <label><span>Channel</span><select id="oChan">${opt(chans)}</select></label>
        <label><span>Scope</span><select id="oScope">${opt(scopes)}</select></label>
        <label><span>Scope values (CSV/keys)</span><input id="oScopeVal" placeholder="e.g. grocery,furniture or LX-ELS-001"></label>
        <label><span>Funder</span><select id="oFunder">${opt(funders)}</select></label>
        <label><span>Funder ref</span><input id="oFunderRef" placeholder="bank/brand id"></label>
        <label><span>Direction</span><select id="oDir">${opt(dirs)}</select></label>
        <label><span>Stack policy</span><select id="oStack">${opt(stacks)}</select></label>
        <label><span>Max discount</span><input id="oMax" type="number" step="0.01" placeholder="0 = none"></label>
        <label><span>Min spend</span><input id="oMin" type="number" step="0.01"></label>
        <label><span>Currency (fixed amt)</span><select id="oCur"><option>USD</option><option>EUR</option><option>GBP</option><option>INR</option><option>AED</option></select></label>
        <label><span>Usage limit</span><input id="oUse" type="number" value="0"></label>
        <label><span>Per-owner limit</span><input id="oOwner" type="number" value="0"></label>
        <label><span>Priority</span><input id="oPri" type="number" value="0"></label>
        <label><span>Starts</span><input id="oStart" type="date"></label>
        <label><span>Ends</span><input id="oEnd" type="date"></label>
        <label><span>Status</span><select id="oStatus"><option>active</option><option>draft</option><option>scheduled</option><option>inactive</option></select></label>
      </div>
      <div style="margin-top:8px"><button class="p-btn primary sm" id="oSave">Save offer</button><span class="p-tag" id="oEditHint"></span></div>
    </div>
    <h3>Active & saved offers</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>Name</th><th>Type</th><th>Dir</th><th>Channel</th><th>Scope</th><th>Funder</th><th class="num">Value</th><th class="num">Used</th><th>Status</th><th></th></tr></thead><tbody>${off.offers.map(row).join("") || '<tr><td colspan="10">No offers yet.</td></tr>'}</tbody></table></div>
    <div class="p-panel"><h3>Coupons</h3>
      <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:end">
        <label><span>Kind</span><select id="cKind">${opt(cKinds)}</select></label>
        <label><span>Code</span><input id="cCode" placeholder="auto if blank"></label>
        <label><span>Value</span><input id="cVal" type="number" step="0.01"></label>
        <label><span>Funder</span><select id="cFunder">${opt(funders)}</select></label>
        <label><span>Funder ref</span><input id="cFunderRef" placeholder="e.g. HDFC"></label>
        <label><span>Max uses</span><input id="cMax" type="number" value="1"></label>
        <label><span>Per owner</span><input id="cOwner" type="number" value="1"></label>
        <button class="p-btn primary sm" id="cCreate">+ Coupon</button>
        <button class="p-btn sm" id="cGen">Generate 10 codes</button>
      </div>
      <div class="p-scroll-x" style="margin-top:10px"><table class="p-table"><thead><tr><th>Code</th><th>Kind</th><th>Funder</th><th class="num">Value</th><th class="num">Used/Max</th><th>Status</th><th></th></tr></thead><tbody>
        ${(cp.coupons || []).map(c => `<tr><td><code>${esc(c.code)}</code>${c.tenant_id === 0 ? ' <span class="p-tag">GLOBAL</span>' : ""}</td><td>${esc(c.kind)}</td><td>${esc(c.funder)}${c.funder_ref ? " " + esc(c.funder_ref) : ""}</td><td class="num">${esc(c.value)}</td><td class="num">${c.used}/${c.max_uses}</td><td>${statusBadge(c.status)}</td><td style="text-align:right"><button class="p-btn sm danger" data-cvoid="${c.id}">Void</button></td></tr>`).join("") || '<tr><td colspan="7">No coupons.</td></tr>'}
      </tbody></table></div>
      <h3>Redemption performance</h3>
      <div class="p-cards" style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:8px">
        <div class="p-stat"><b>${(an.totals && an.totals.redemptions) || 0}</b> redemptions</div>
        <div class="p-stat"><b>${money(an.totals && an.totals.discount || 0)}</b> discount given</div>
        <div class="p-stat"><b>${money(an.totals && an.totals.credits || 0)}</b> credits rewarded</div>
      </div>
      ${(an.byCode || []).filter(x => x.k).length ? `<table class="p-table"><thead><tr><th>Top codes</th><th class="num">Times</th><th class="num">Discount</th></tr></thead><tbody>${an.byCode.filter(x => x.k).slice(0, 8).map(x => `<tr><td><code>${esc(x.k)}</code></td><td class="num">${x.n}</td><td class="num">${money(x.discount)}</td></tr>`).join("")}</tbody></table>` : ""}
      ${(an.byFunder || []).length ? `<p class="p-tag">By funder: ${an.byFunder.map(x => `${esc(x.k || "self")}: ${x.n} (${money(x.discount)})`).join(" · ")}</p>` : ""}
      <h3>Recent redemptions</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>Code</th><th class="num">Amount</th><th>Funder</th><th>Channel</th><th>Owner</th><th>When</th></tr></thead><tbody>
        ${(cp.redemptions || []).slice(0, 12).map(r => `<tr><td><code>${esc(r.code)}</code></td><td class="num">${money(r.amount)}</td><td>${esc(r.funder)}${r.funder_ref ? " " + esc(r.funder_ref) : ""}</td><td>${esc(r.channel)}</td><td class="p-tag">${esc((r.owner || "").slice(0, 16))}</td><td>${esc((r.created_at || "").slice(0, 16))}</td></tr>`).join("") || '<tr><td colspan="6">No redemptions yet.</td></tr>'}
      </tbody></table></div>
    </div>
    <div class="p-panel"><h3>Preview the engine (what a cart would get)</h3>
      <div style="display:flex;gap:8px;align-items:end;flex-wrap:wrap">
        <label><span>Amount</span><input id="pvAmt" type="number" step="0.01" value="50"></label>
        <label><span>Channel</span><select id="pvChan">${opt(chans)}</select></label>
        <label><span>Coupon</span><input id="pvCode" placeholder="optional"></label>
        <button class="p-btn sm" id="pvGo">Evaluate</button>
      </div><pre id="pvOut" style="margin-top:8px;background:#0b0d12;color:#cfe;padding:10px;border-radius:10px;font-size:12px;max-height:220px;overflow:auto"></pre></div>
    <div class="p-panel"><h3>Wallet ledger</h3><div style="display:flex;gap:8px;align-items:end"><label><span>Owner (e.g. t1:u2)</span><input id="wlOwner" placeholder="leave blank for your session"></label><button class="p-btn sm" id="wlGo">Show</button></div><div id="wlOut" style="margin-top:8px" class="p-tag">—</div></div>
    </div>`;
}
function wireOffers() {
  const $ = s => document.querySelector(s); const $$ = s => Array.from(document.querySelectorAll(s));
  const readScope = () => { const st = $("#oScope").value, csv = $("#oScopeVal").value.split(",").map(x => x.trim()).filter(Boolean); if (st === "product") return { products: csv }; if (st === "category") return { categories: csv }; if (st === "brand") return { brands: csv }; if (st === "node") return { node: csv[0] || "" }; return {}; };
  const save = async (id) => {
    const body = { name: $("#oName").value, type: $("#oType").value, value: Number($("#oValue").value), code: $("#oCode").value, channel: $("#oChan").value, scope_type: $("#oScope").value, scope: readScope(), funder: $("#oFunder").value, funder_ref: $("#oFunderRef").value, brand_ref: "", direction: $("#oDir").value, stack_policy: $("#oStack").value, max_discount: Number($("#oMax").value) || 0, min_amount: Number($("#oMin").value) || 0, currency: ($("#oCur") || {}).value || "USD", usage_limit: Number($("#oUse").value) || 0, per_owner_limit: Number(($("#oOwner") || {}).value) || 0, priority: Number($("#oPri").value) || 0, starts: $("#oStart").value || null, ends: $("#oEnd").value || null, status: $("#oStatus").value };
    try { await api("/offers" + (id ? "/" + id : ""), id ? "PUT" : "POST", body); toast("Offer saved"); render(); } catch (e) { toast(e.message); }
  };
  $("#oSave").onclick = () => save(window.__oeid || null);
  $$("[data-oedit]").forEach(b => b.onclick = async () => { window.__oeid = b.dataset.oedit; const o = ((await api("/offers")).offers.find(x => String(x.id) === b.dataset.oedit) || {}); $("#oName").value = o.name || ""; $("#oType").value = o.type || "percent"; $("#oValue").value = o.value || 0; $("#oCode").value = o.code || ""; $("#oChan").value = o.channel || "commerce"; $("#oScope").value = o.scope_type || "store"; $("#oScopeVal").value = [].concat((o.scope || {}).products || (o.scope || {}).categories || (o.scope || {}).brands || (o.scope || {}).node || []).join(","); $("#oFunder").value = o.funder || "self"; $("#oFunderRef").value = o.funder_ref || ""; $("#oDir").value = o.direction || "discount"; $("#oStack").value = o.stack_policy || "stack_with_others";     $("#oMax").value = o.max_discount || ""; $("#oMin").value = o.min_amount || ""; $("#oUse").value = o.usage_limit || 0; if ($("#oCur")) $("#oCur").value = o.currency || "USD"; if ($("#oOwner")) $("#oOwner").value = o.per_owner_limit || 0; $("#oPri").value = o.priority || 0; $("#oStatus").value = o.status || "active"; $("#oEditHint").textContent = "editing #" + b.dataset.oedit; $("#oSave").textContent = "Update offer"; });
  $$("[data-oret]").forEach(b => b.onclick = async () => { try { await api("/offers/" + b.dataset.oret, "DELETE"); toast("Retired"); render(); } catch (e) { toast(e.message); } });
  $("#cCreate").onclick = async () => { try { await api("/offers/coupons", "POST", { kind: $("#cKind").value, code: $("#cCode").value, value: Number($("#cVal").value), funder: $("#cFunder").value, funder_ref: $("#cFunderRef").value, max_uses: Number($("#cMax").value) || 1, per_owner_limit: Number(($("#cOwner") || {}).value) || 1 }); toast("Coupon created"); render(); } catch (e) { toast(e.message); } };
  $("#cGen").onclick = async () => { try { const r = await api("/offers/coupons/generate", "POST", { count: 10, kind: $("#cKind").value, funder: $("#cFunder").value, funder_ref: $("#cFunderRef").value, value: Number($("#cVal").value), per_owner_limit: Number(($("#cOwner") || {}).value) || 1 }); toast(r.count + " codes (" + r.batch + ")"); render(); } catch (e) { toast(e.message); } };
  $$("[data-cvoid]").forEach(b => b.onclick = async () => { try { await api("/offers/coupons/" + b.dataset.cvoid, "DELETE"); toast("Voided"); render(); } catch (e) { toast(e.message); } });
  $("#pvGo").onclick = async () => { try { const r = await api("/offers/preview", "POST", { amount: Number($("#pvAmt").value), channel: $("#pvChan").value, coupon: $("#pvCode").value }); $("#pvOut").textContent = JSON.stringify({ discount: r.discount, credits: r.credits, freeShip: r.freeShip, netBase: r.netBase, applied: r.applied.map(a => a.name + " (" + a.type + ")") }, null, 1); } catch (e) { $("#pvOut").textContent = "⚠ " + e.message; } };
  $("#wlGo").onclick = async () => { try { const r = await api("/wallet/ledger" + ($("#wlOwner").value ? "?owner=" + encodeURIComponent($("#wlOwner").value) : "")); $("#wlOut").innerHTML = "balance " + money(r.balance) + "<br>" + (r.entries || []).map(e2 => `${esc(e2.kind)} ${Number(e2.amount).toFixed(2)} → ${money(e2.balance_after)} · ${esc((e2.created_at || "").slice(0, 16))}`).join("<br>") || "no entries"; } catch (e) { toast(e.message); } };
}

/* ---------- Outbound Webhooks ---------- */
async function vWebhooks() {
  const d = await api("/admin/webhooks");
  const ev = d.events || [];
  const whRow = w => `<tr><td><code>${esc((w.url || "").slice(0, 46))}</code>${w.description ? `<br><span class="p-tag">${esc(w.description)}</span>` : ""}</td><td class="p-tag">${(w.events || []).map(e => `<code>${esc(e)}</code>`).join(" ")}</td><td><span class="badge ${w.active ? "published" : "draft"}">${w.active ? "active" : "off"}</span></td>
    <td style="text-align:right;white-space:nowrap"><button class="p-btn sm" data-wtest="${w.id}">Send test</button> <button class="p-btn sm danger" data-wwipe="${w.id}">✕</button></td></tr>`;
  const dl = (d.deliveries || []).slice(0, 40).map(x => `<tr><td><code>${esc(x.event)}</code></td><td><span class="badge ${x.status === 'delivered' ? 'published' : x.status === 'failed' ? 'failed' : 'processing'}">${esc(x.status)}</span></td><td class="num">${x.attempts}</td><td class="p-tag">${esc((x.response || "").slice(0, 40))}</td><td>${esc((x.created_at || "").slice(0, 16))}</td></tr>`).join("");
  return `<div class="p-panel"><h2>🔗 Webhooks</h2>
    <p style="color:var(--p-muted);font-size:13px;margin:0 0 12px">Outbound events to your endpoints — payloads are HMAC-signed (X-Lux-Signature) and retried. Available events are a data registry; pick which ones each hook receives.</p>
    <div class="p-panel"><b>Add endpoint</b><div style="display:flex;gap:8px;align-items:end;flex-wrap:wrap;margin-top:6px">
      <label><span>URL</span><input id="whUrl" placeholder="https://hooks.acme/orders" style="min-width:240px"></label>
      <label><span>Secret</span><input id="whSecret" placeholder="signing secret"></label>
      <label><span>Description</span><input id="whDesc"></label>
      <button class="p-btn primary sm" id="whAdd">Add webhook</button></div>
      <div style="margin-top:6px" class="p-tag">Events: ${ev.map(e => `<label style="margin-right:8px"><input type="checkbox" class="whEv" value="${esc(e)}"> ${esc(e)}</label>`).join("")}</div>
    </div>
    <h3>Endpoints</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>URL</th><th>Events</th><th>Status</th><th></th></tr></thead><tbody>${(d.webhooks || []).map(whRow).join("") || '<tr><td colspan="4">No webhooks.</td></tr>'}</tbody></table></div>
    <div style="margin-top:8px"><button class="p-btn sm" id="whDrain">Retry failed / deliver queued</button></div>
    <h3>Recent deliveries</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>Event</th><th>Status</th><th class="num">Tries</th><th>Response</th><th>When</th></tr></thead><tbody>${dl || '<tr><td colspan="5">No deliveries yet.</td></tr>'}</tbody></table></div></div>`;
}
function wireWebhooks() {
  const $ = s => document.querySelector(s), $$ = s => Array.from(document.querySelectorAll(s));
  if ($("#whAdd")) $("#whAdd").onclick = async () => { const events = $$(".whEv:checked").map(c => c.value); try { await api("/admin/webhooks", "POST", { url: $("#whUrl").value, secret: $("#whSecret").value, description: $("#whDesc").value, events: events.length ? events : ["*"] }); toast("Webhook added"); render(); } catch (e) { toast(e.message); } };
  $$("[data-wwipe]").forEach(b => b.onclick = async () => { if (!confirm("Delete webhook?")) return; try { await api("/admin/webhooks/" + b.dataset.wwipe, "DELETE"); render(); } catch (e) { toast(e.message); } });
  $$("[data-wtest]").forEach(b => b.onclick = async () => { try { const r = await api("/admin/webhooks/" + b.dataset.wtest + "/test", "POST", { event: "store.test" }); toast(r.ok ? "Test dispatched" : "Failed"); render(); } catch (e) { toast(e.message); } });
  if ($("#whDrain")) $("#whDrain").onclick = async () => { try { const r = await api("/admin/webhooks/drain", "POST", {}); toast((r.drained || 0) + " attempted, " + (r.remaining || 0) + " pending"); render(); } catch (e) { toast(e.message); } };
}
/* ---------- Trash & Retention (governance) ---------- */
async function vTrash() {
  const d = await api("/admin/trash");
  const items = d.items || []; const counts = d.counts || {}; const ret = d.retention || {};
  return `<div class="p-panel"><h2>🗑️ Trash &amp; Retention</h2>
    <p style="color:var(--p-muted);font-size:13px;margin:0 0 12px">Deleting content moves it to the trash (soft delete) — it disappears from the storefront but stays restorable. Retention purges tombstoned rows older than the policy (data-driven, per entity; 0 = keep forever).</p>
    <div class="p-panel"><b>Retention (days; 0 = never purge)</b><div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:6px">
      ${Object.keys({ _default: 1, products: 1, orders: 1, reviews: 1, offers: 1, coupons: 1 }).map(k => `<label style="font-size:12px"><span>${esc(k)}</span><input data-ret="${k}" type="number" value="${ret[k] != null ? ret[k] : ""}" placeholder="—"></label>`).join("")}
      <button class="p-btn sm primary" id="retSave">Save policy</button></div></div>
    <h3>Trashed (${items.length})</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>Entity</th><th>Reference</th><th>Deleted</th><th></th></tr></thead><tbody>
      ${items.map(i => `<tr><td><code>${esc(i.entity)}</code></td><td>${esc(i.id)}</td><td>${esc((i.deleted_at || "").slice(0, 16))}</td><td style="text-align:right"><button class="p-btn sm" data-restore="${esc(i.entity)}" data-id="${esc(i.id)}">Restore</button></td></tr>`).join("") || '<tr><td colspan="4">Trash is empty.</td></tr>'}
    </tbody></table></div>
    <div style="margin-top:10px;display:flex;gap:8px;align-items:center"><button class="p-btn sm danger" id="purgeNow">Purge expired (per retention)</button><span class="p-tag">${Object.entries(counts).filter(x => x[1]).map(x => `${x[0]}: ${x[1]}`).join(" · ") || "nothing trashed"}</span></div></div>`;
}
function wireTrash() {
  const $ = s => document.querySelector(s), $$ = s => Array.from(document.querySelectorAll(s));
  $$("[data-restore]").forEach(b => b.onclick = async () => { try { await api(`/admin/trash/${encodeURIComponent(b.dataset.restore)}/${encodeURIComponent(b.dataset.id)}/restore`, "POST", {}); toast("Restored"); render(); } catch (e) { toast(e.message); } });
  if ($("#retSave")) $("#retSave").onclick = async () => { const patch = {}; $$("[data-ret]").forEach(i => { if (i.value !== "") patch[i.dataset.ret] = Number(i.value); }); try { await api("/admin/retention", "PUT", patch); toast("Retention saved"); render(); } catch (e) { toast(e.message); } };
  if ($("#purgeNow")) $("#purgeNow").onclick = async () => { if (!confirm("Purge tombstoned rows past their retention? This is permanent.")) return; try { const r = await api("/admin/trash/purge", "POST", {}); toast("Purged " + Object.values(r.purged || {}).reduce((a, b) => a + b, 0)); render(); } catch (e) { toast(e.message); } };
}
/* ---------- Team & Roles (RBAC) ---------- */
async function vTeam() {
  const [r, s] = await Promise.all([api("/admin/roles"), api("/admin/staff")]);
  const roles = r.roles || [], secs = r.sections || [];
  const isOwner = !A.allowed || A.allowed.includes("*") || (A.allowed.includes("team") && A.allowed.length > 5);
  const row = u => `<tr><td><b>${esc(u.name)}</b><br><span class="p-tag">${esc(u.email)}</span></td>
    <td><select data-srole="${u.id}" ${String(u.id) === String(r.me.user.id) ? "disabled" : ""}>${roles.map(rl => `<option ${u.staff_role === rl.key ? "selected" : ""}>${esc(rl.key)}</option>`).join("")}</select></td>
    <td><span class="badge ${u.disabled ? "failed" : "published"}">${u.disabled ? "disabled" : "active"}</span></td>
    <td class="p-tag">${esc((u.last_login || "").slice(0, 16) || "never")}</td>
    <td style="text-align:right;white-space:nowrap"><button class="p-btn sm" data-sperm="${u.id}" title="Per-user overrides">Perms</button> ${String(u.id) !== String(r.me.user.id) ? `<button class="p-btn sm danger" data-sdel="${u.id}">Remove</button>` : ""}</td></tr>`;
  return `<div class="p-panel"><h2>👥 Team &amp; Roles</h2>
    <p style="color:var(--p-muted);font-size:13px;margin:0 0 12px">Staff share the store-console admin login but see and can only edit the sections their <b>role</b> grants. Roles are editable data; per-user permission overrides take precedence.</p>
    <h3>Role definitions (data)</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>Role</th><th>Grants (section: access)</th></tr></thead><tbody>${roles.map(rl => `<tr><td><b>${esc(rl.name)}</b><br><code>${esc(rl.key)}</code></td><td class="p-tag">${Object.entries(rl.sections || {}).map(([k, v]) => `${esc(k)}=${esc(v)}`).join(" · ")}</td></tr>`).join("")}</tbody></table></div>
    <h3>Members</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>Member</th><th>Role</th><th>Status</th><th>Last login</th><th></th></tr></thead><tbody>${(s.staff || []).map(row).join("")}</tbody></table></div>
    <div class="p-panel" style="margin-top:10px"><b>Add staff member</b><div style="display:flex;gap:8px;flex-wrap:wrap;align-items:end;margin-top:6px">
      <label><span>Name</span><input id="stName"></label><label><span>Email</span><input id="stEmail"></label>
      <label><span>Role</span><select id="stRole">${roles.filter(rl => rl.key !== "owner").map(rl => `<option>${esc(rl.key)}</option>`).join("")}</select></label>
      <label><span>Password</span><input id="stPw" type="text" placeholder="blank = generate"></label>
      <button class="p-btn primary sm" id="stAdd">Add member</button><span id="stGen" class="p-tag"></span></div></div></div>`;
}
function wireTeam() {
  const $$ = s => Array.from(document.querySelectorAll(s));
  $$("[data-srole]").forEach(sel => sel.onchange = async () => { try { await api("/admin/staff/" + sel.dataset.srole, "PUT", { staff_role: sel.value }); toast("Role updated"); } catch (e) { toast(e.message); } });
  $$("[data-sdel]").forEach(b => b.onclick = async () => { if (!confirm("Disable this member?")) return; try { await api("/admin/staff/" + b.dataset.sdel, "DELETE"); render(); } catch (e) { toast(e.message); } });
  $$("[data-sperm]").forEach(b => b.onclick = async () => { const cur = prompt("Per-user overrides as JSON, e.g. {\"products\":\"read\",\"trash\":false}", "{}"); if (cur == null) return; try { await api("/admin/staff/" + b.dataset.sperm, "PUT", { perms: JSON.parse(cur) }); toast("Saved"); } catch (e) { toast(e.message); } });
  if (document.getElementById("stAdd")) document.getElementById("stAdd").onclick = async () => { try { const r = await api("/admin/staff", "POST", { name: document.getElementById("stName").value, email: document.getElementById("stEmail").value, staff_role: document.getElementById("stRole").value, password: document.getElementById("stPw").value || undefined }); if (r.generated) document.getElementById("stGen").textContent = "generated password: " + r.generated; toast("Member added"); render(); } catch (e) { toast(e.message); } };
}
/* ---------- SSO & Integrations (SSO/SAML, SCIM, transfers, tax) ---------- */
async function vSso() {
  const [s, tks, tf, tax] = await Promise.all([api("/admin/sso"), api("/admin/webhooks").catch(() => ({ webhooks: [] })), api("/admin/transfers"), api("/admin/tax/report")]);
  const c = s.connection || { enabled: false };
  return `<div class="p-panel"><h2>🔐 SSO & Integrations</h2>
    <p style="color:var(--p-muted);font-size:13px;margin:0 0 12px">Single sign-on and directory sync via fill-in-the-blank config. Nothing activates until you enable it.</p>
    <div class="p-panel"><b>SAML / OIDC SSO</b>
      <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:end;margin-top:6px">
        <label><span>Enabled</span><input id="ssoOn" type="checkbox" ${c.enabled ? "checked" : ""}></label>
        <label><span>Provider</span><select id="ssoProv"><option ${c.provider === "okta" ? "selected" : ""}>okta</option><option ${c.provider === "entra" ? "selected" : ""}>entra</option><option ${c.provider === "google" ? "selected" : ""}>google</option><option ${c.provider === "saml-generic" ? "selected" : ""}>saml-generic</option></select></label>
        <label><span>Entity ID</span><input id="ssoEnt" value="${esc(c.entityId || "")}"></label>
        <label><span>SSO URL</span><input id="ssoUrl" style="min-width:240px" value="${esc(c.ssoUrl || "")}" placeholder="https://idp.example/app/sso"></label>
        <label><span>Email domains</span><input id="ssoDom" value="${esc((c.domains || []).join(","))}" placeholder="corp.com,acme.com"></label>
        <button class="p-btn primary sm" id="ssoSave">Save SSO</button></div>
      <p class="p-tag" style="margin-top:6px">Store admins on these domains log in via <code>/admin.html → SSO</code>; the IdP redirect is built from the connection (placeholder SAMLRequest until your metadata is loaded).</p></div>
    <div class="p-panel"><b>SCIM 2.0 (directory sync)</b><div style="display:flex;gap:8px;align-items:end;margin-top:6px"><label><span>Label</span><input id="scimLbl" placeholder="okta bridge"></label><button class="p-btn sm" id="scimTok">Issue SCIM token</button></div><div id="scimOut" class="p-tag" style="margin-top:6px">Tokens: bearer at <code>/scim/Users?tenant_id=${(window.__tid || 1)}</code> — HR/IdP pushes staff here.</div></div>
    <div class="p-panel"><b>Warehouse stock transfers</b><div style="display:flex;gap:8px;flex-wrap:wrap;align-items:end;margin-top:6px">
      <label><span>SKU</span><input id="trSku" type="number"></label><label><span>From WH</span><input id="trFrom" type="number"></label><label><span>To WH</span><input id="trTo" type="number"></label><label><span>Qty</span><input id="trQty" type="number" value="1"></label><button class="p-btn sm primary" id="trGo">Transfer</button></div>
      <div class="p-tag" style="margin-top:6px">Recent: ${(tf.transfers || []).slice(0, 5).map(x => `${x.sku_id} ${x.qty} ${x.from_warehouse}→${x.to_warehouse}`).join(" · ") || "none"}</div></div>
    <div class="p-panel"><b>Tax — period remittance</b><div class="p-tag" style="margin-top:4px">Period ${esc(tax.period || "")}: taxable ${money(tax.taxable || 0)} · collected ${money(tax.taxCollected || 0)} ${esc(tax.currency || "")} — <a href="/api/admin/tax/report" target="_blank">report</a></div></div>
    </div>`;
}
function wireSso() {
  const $ = s => document.querySelector(s);
  if ($("#ssoSave")) $("#ssoSave").onclick = async () => { try { await api("/admin/sso", "PUT", { enabled: $("#ssoOn").checked, provider: $("#ssoProv").value, entityId: $("#ssoEnt").value, ssoUrl: $("#ssoUrl").value, domains: $("#ssoDom").value.split(",").map(x => x.trim()).filter(Boolean) }); toast("SSO saved"); } catch (e) { toast(e.message); } };
  if ($("#scimTok")) $("#scimTok").onclick = async () => { try { const r = await api("/admin/scim/token", "POST", { label: $("#scimLbl").value || "default" }); $("#scimOut").innerHTML = "Token (shown once): <code>" + esc(r.token) + "</code>"; } catch (e) { toast(e.message); } };
  if ($("#trGo")) $("#trGo").onclick = async () => { try { await api("/admin/transfers", "POST", { sku_id: Number($("#trSku").value), from_warehouse: Number($("#trFrom").value), to_warehouse: Number($("#trTo").value), qty: Number($("#trQty").value) || 1 }); toast("Transferred"); render(); } catch (e) { toast(e.message); } };
}
async function render() {
  shell('<div class="p-empty">Loading…</div>');
  const body = $("#vBody");
  try {
    if (view !== "dash" && !canSee(view)) { body.innerHTML = `<div class="p-empty">🔒 Your role (<b>${esc((A.user && A.user.staff_role) || "admin")}</b>) does not grant access to “${esc(view)}”.</div>`; return; }
    if (view === "dash") body.innerHTML = await vDash();
    else if (view === "products") body.innerHTML = await entityTable("product");
    else if (view === "skus") body.innerHTML = await entityTable("sku") + await entityTable("inventory") + await entityTable("warehouse") + await entityTable("variant_group");
    else if (view === "orders") body.innerHTML = await entityTable("order");
    else if (view === "returns") body.innerHTML = await entityTable("ret");
    else if (view === "rfqs") body.innerHTML = await entityTable("rfq");
    else if (view === "sellers") body.innerHTML = await entityTable("seller");
    else if (view === "settlements") body.innerHTML = await entityTable("settlement");
    else if (view === "contracts") { body.innerHTML = await vContracts(); wireContracts(); }
    else if (view === "tenders") { body.innerHTML = await vTenders(); wireTenders(); }
    else if (view === "suppliers") body.innerHTML = await entityTable("supplier") + await entityTable("product_supplier");
    else if (view === "serialized") { body.innerHTML = await vSerialized(); wireSerialized(); }
    else if (view === "compliance") body.innerHTML = await entityTable("compliance");
    else if (view === "localizations") body.innerHTML = await entityTable("localization");
    else if (view === "ai") { body.innerHTML = await vAI(); wireAI(); }
    else if (view === "webhooks") { body.innerHTML = await vWebhooks(); wireWebhooks(); }
    else if (view === "trash") { body.innerHTML = await vTrash(); wireTrash(); }
    else if (view === "sso") { body.innerHTML = await vSso(); wireSso(); }
    else if (view === "team") { body.innerHTML = await vTeam(); wireTeam(); }
    else if (view === "promotions") { body.innerHTML = await vOffers(); wireOffers(); }
    else if (view === "goip") { body.innerHTML = await vGoip(); wireGoip(); }
    else if (view === "content") body.innerHTML = await entityTable("banner") + await entityTable("card") + await entityTable("department");
    else if (view === "taxonomy") body.innerHTML = await entityTable("taxonomy");
    else if (view === "attributes") body.innerHTML = await entityTable("attribute");
    else if (view === "payments") { body.innerHTML = await vPayments(); wirePayments(); }
    else if (view === "settings") { body.innerHTML = await vSettings(); wireSettings(); }
    else if (view === "billing") body.innerHTML = await vBilling();
    else if (view === "modules") { body.innerHTML = await vModules(); }
    else if (view === "audit") { body.innerHTML = await vAudit(); wireAudit(); }
    else if (view === "finance") body.innerHTML = await vFinance();
    else if (view === "logistics") body.innerHTML = await vLogistics();
    else if (view === "search") body.innerHTML = await vSearch();
    else if (view === "monitor") body.innerHTML = await vMonitor();
    else if (view === "studio") { body.innerHTML = await vStudio(); wireStudio(); }
    else if (view === "analytics") body.innerHTML = await vAnalytics();
  } catch (e) { body.innerHTML = `<div class="p-empty">⚠️ ${esc(e.message)}</div>`; }
}
function wireAudit() {
  $("#auditQ").oninput = e => {
    const q = e.target.value.toLowerCase();
    $$("#auditTbl tbody tr").forEach(tr => tr.style.display = tr.textContent.toLowerCase().includes(q) ? "" : "none");
  };
}
function wireStudio() {
  $$("[data-studio]").forEach(b => b.onclick = () => { A.studioSel = b.dataset.studio; render(); });
  $("#ceSave").onclick = async () => {
    try {
      await api("/meta/entity-def", "POST", { key: $("#ceKey").value.trim(), label: $("#ceLabel").value.trim(), icon: $("#ceIcon").value.trim() || "🧬", fields: JSON.parse($("#ceFields").value) });
      toast("Entity created — it now appears in the studio & nav"); render();
    } catch (e) { toast(e.message); }
  };
}
function wirePayments() {
  $("#gwSave").onclick = async () => {
    const gateways = $$("[data-gwen]").map(cb => {
      const id = cb.dataset.gwen;
      return { id, enabled: cb.checked, primary: ($(`[data-gwpri="${id}"]`) || {}).checked, mode: ($(`[data-gwmode="${id}"]`) || {}).value, config: (A.gwCfg || {})[id] || {} };
    });
    A.gwCfg = {};
    await api("/admin/gateways", "PUT", { gateways });
    toast("Gateway configuration saved"); render();
  };
  $$("[data-gwtest]").forEach(b => b.onclick = async () => {
    try { const r = await api(`/admin/gateways/${b.dataset.gwtest}/test`, "POST", {}); toast(r.message); } catch (e) { toast(e.message); }
  });
  $$("[data-gwcfg]").forEach(b => b.onclick = async () => {
    const g = (await api("/admin/gateways")).gateways.find(x => x.id === b.dataset.gwcfg);
    $("#modal").innerHTML = `<div class="p-modal"><div class="p-modal-box"><div class="p-modal-head"><h3>${esc(g.name)} configuration</h3><button id="mClose">✕</button></div>
      <div class="p-form">${(g.fields || []).map(f => `<label><span>${esc(f.label)}${f.secret ? " (secret)" : ""}</span><input data-gcfg="${f.key}" value="${esc(g.config[f.key] || "")}" ${f.secret ? 'type="password"' : ""}></label>`).join("") || '<p class="p-tag">No credentials needed.</p>'}
      <button class="p-btn primary" id="mCfgSave">Save</button></div></div></div>`;
    $("#modal").classList.remove("hidden");
    const closeGw = () => { const m = $("#modal"); m.innerHTML = ""; m.classList.add("hidden"); };
    $("#mClose").onclick = closeGw;
    $("#mCfgSave").onclick = () => {
      A.gwCfg = A.gwCfg || {};
      A.gwCfg[g.id] = A.gwCfg[g.id] || {};
      $$("[data-gcfg]").forEach(i => { if (i.value && !i.value.startsWith("••••")) A.gwCfg[g.id][i.dataset.gcfg] = i.value; });
      Object.assign(A.gwCfg[g.id], g.config);
      closeGw(); toast("Credentials staged — press Save gateway config");
    };
  });
}
function wireSettings() {
  $$("[data-preset]").forEach(b => b.onclick = () => {
    const [a, h] = b.dataset.preset.split("|");
    $('[data-set="theme.accent"]').value = a; $('[data-set="theme.header"]').value = h;
  });
  $("#setSave").onclick = async () => {
    const body = { brand: {}, theme: {}, commerce: {}, copy: {}, features: {} };
    $$("[data-set]").forEach(i => {
      const [sec, key] = i.dataset.set.split(".");
      body[sec][key] = i.type === "number" ? Number(i.value) : i.value;
    });
    $$("[data-feat]").forEach(cb => body.features[cb.dataset.feat] = cb.checked);
    for (const k of Object.keys(body)) if (!Object.keys(body[k]).length) delete body[k];
    await api("/admin/settings", "PUT", body);
    TT = await api("/config");
    toast("Settings saved — storefront updated live");
  };
  $("#setReset").onclick = async () => { if (confirm("Reset all settings to platform defaults?")) { await api("/admin/settings/reset", "POST"); TT = await api("/config"); render(); } };
  $("#modeSave").onclick = async () => {
    await api("/admin/mode", "PUT", { mode: $("#modeSel").value, industries: $("#modeInds").value.split(",").map(x => x.trim()).filter(Boolean) });
    TT = await api("/config"); toast("Deployment mode applied"); render();
  };
}

/* ---------- boot ---------- */
const A = { user: null, gwCfg: {}, studioSel: null };
document.addEventListener("click", e => { const close = e.target.closest("[data-mclose]") || (e.target.classList && e.target.classList.contains("p-modal")); if (close) { const mm = document.getElementById("modal"); if (mm) { mm.innerHTML = ""; mm.classList.add("hidden"); } } }); /* __mclose + backdrop */
(async function boot() {
  try {
    const [sess, cfg] = await Promise.all([api("/session"), api("/config")]);
    TT = cfg;
    if (!sess.user || sess.user.role !== "admin") {
      const already = sess.user ? `<p class="m-help">Signed in as <b>${esc(sess.user.email)}</b> — a customer account, not a store admin. <a href="#" id="swAcct">Sign out</a></p>` : "";
      $("#app").innerHTML = `<div class="p-login"><div class="p-login-box"><h1>LUXORA</h1><p>Store Console</p>${already}
        <form id="lf" class="p-form"><label><span>Email</span><input id="le" type="email" required></label>
        <label><span>Password</span><input id="lp" type="password" required></label>
        <button class="p-btn primary" style="width:100%">Sign in</button></form>
        <p class="p-err hidden" id="lfErr" style="color:var(--p-red);font-size:13px;margin:10px 0 0"></p>
        <p class="hint" id="lfHint"></p>
        <p class="hint">Store console for ${esc(TT ? TT.tenant.slug : "this store")} · Platform owner? <a href="/platform.html">Platform console →</a> · <a href="/index.html">← Storefront</a></p></div></div>`;
      const sw = $("#swAcct"); if (sw) sw.onclick = async e => { e.preventDefault(); await api("/auth/logout", "POST"); boot(); };
      api("/hint").then(h => { const el = $("#lfHint"); if (el && h.demo && h.email) el.innerHTML = "This store's admin: <code>" + esc(h.email) + "</code>" + (h.password ? " / <code>" + esc(h.password) + "</code>" : ""); }).catch(() => { });
      $("#lf").onsubmit = async e => {
        e.preventDefault();
        try { await api("/auth/login", "POST", { email: $("#le").value, password: $("#lp").value }); boot(); }
        catch (err) { const b = $("#lfErr"); if (b) { b.innerHTML = "⚠️ " + linkify(err.message); b.classList.remove("hidden"); } toast(err.message); }
      };
      return;
    }
    A.user = sess.user;
    A.allowed = Array.isArray(sess.allowedSections) ? sess.allowedSections : null;
    if (!$("#modal")) { const m = document.createElement("div"); m.id = "modal"; m.className = "hidden"; document.body.appendChild(m); }
    render();
  } catch (e) { console.error(e); }
})();
