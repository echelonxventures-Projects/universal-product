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
  ["promotions", "🎯 Promotions"], ["content", "🖼️ Home Content"], ["taxonomy", "🌳 Taxonomy"], ["attributes", "🧬 Attributes"],
  ["payments", "💳 Payment Gateways"], ["modules", "🧩 Modules"], ["settings", "⚙️ Settings"], ["billing", "🧮 Billing"], ["analytics", "📊 Analytics"], ["audit", "📜 Audit Trail"],
  ["monitor", "📈 Monitor"], ["studio", "🛠️ Data Studio"]
];
let view = "dash";

function shell(content) {
  $("#app").innerHTML = `
  <div class="p-shell">
    <aside class="p-side">
      <div class="p-logo"><b>${esc(TT.brand.wordmark)}</b><small>Store Console · ${esc(TT.tenant.slug)}</small></div>
      <nav class="p-nav">${NAV.map(([k, l]) => `<button data-v="${k}" class="${view === k ? "on" : ""}">${l}</button>`).join("")}</nav>
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
  $("#modal").innerHTML = `<div class="p-modal-box"><div class="p-modal-head"><h3>${id != null ? "Edit" : "New"} ${esc(def.label.replace(/s$/, ""))}</h3><button id="mClose">✕</button></div>
    <div class="p-form" id="mForm">${await Promise.all(fields.map(f => fieldInput(f, row[f.key], registry))).then(a => a.join(""))}
      <div style="display:flex;gap:10px;margin-top:8px"><button class="p-btn primary" id="mSave">Save</button><button class="p-btn" id="mCancel">Cancel</button></div></div></div>`;
  $("#modal").classList.remove("hidden");
  $("#mClose").onclick = $("#mCancel").onclick = () => $("#modal").classList.add("hidden");
  $("#mSave").onclick = async () => {
    try {
      const body = collect(def);
      if (id != null) await api(`/meta/entity/${key}/${encodeURIComponent(id)}`, "PUT", body);
      else {
        if (def.pkType === "text" && body[def.pk]) await api(`/meta/entity/${key}`, "POST", body);
        else await api(`/meta/entity/${key}`, "POST", body);
      }
      $("#modal").classList.add("hidden"); toast("Saved"); onDone && onDone();
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
async function render() {
  shell('<div class="p-empty">Loading…</div>');
  const body = $("#vBody");
  try {
    if (view === "dash") body.innerHTML = await vDash();
    else if (view === "products") body.innerHTML = await entityTable("product");
    else if (view === "skus") body.innerHTML = await entityTable("sku") + await entityTable("inventory") + await entityTable("warehouse");
    else if (view === "orders") body.innerHTML = await entityTable("order");
    else if (view === "returns") body.innerHTML = await entityTable("ret");
    else if (view === "rfqs") body.innerHTML = await entityTable("rfq");
    else if (view === "sellers") body.innerHTML = await entityTable("seller");
    else if (view === "settlements") body.innerHTML = await entityTable("settlement");
    else if (view === "promotions") body.innerHTML = await entityTable("promotion");
    else if (view === "content") body.innerHTML = await entityTable("banner") + await entityTable("card") + await entityTable("department");
    else if (view === "taxonomy") body.innerHTML = await entityTable("taxonomy");
    else if (view === "attributes") body.innerHTML = await entityTable("attribute");
    else if (view === "payments") { body.innerHTML = await vPayments(); wirePayments(); }
    else if (view === "settings") { body.innerHTML = await vSettings(); wireSettings(); }
    else if (view === "billing") body.innerHTML = await vBilling();
    else if (view === "modules") { body.innerHTML = await vModules(); }
    else if (view === "audit") { body.innerHTML = await vAudit(); wireAudit(); }
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
    $("#modal").innerHTML = `<div class="p-modal-box"><div class="p-modal-head"><h3>${esc(g.name)} configuration</h3><button id="mClose">✕</button></div>
      <div class="p-form">${(g.fields || []).map(f => `<label><span>${esc(f.label)}${f.secret ? " (secret)" : ""}</span><input data-gcfg="${f.key}" value="${esc(g.config[f.key] || "")}" ${f.secret ? 'type="password"' : ""}></label>`).join("") || '<p class="p-tag">No credentials needed.</p>'}
      <button class="p-btn primary" id="mCfgSave">Save</button></div></div>`;
    $("#modal").classList.remove("hidden");
    $("#mClose").onclick = () => $("#modal").classList.add("hidden");
    $("#mCfgSave").onclick = () => {
      A.gwCfg = A.gwCfg || {};
      A.gwCfg[g.id] = A.gwCfg[g.id] || {};
      $$("[data-gcfg]").forEach(i => { if (i.value && !i.value.startsWith("••••")) A.gwCfg[g.id][i.dataset.gcfg] = i.value; });
      Object.assign(A.gwCfg[g.id], g.config);
      $("#modal").classList.add("hidden"); toast("Credentials staged — press Save gateway config");
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
document.addEventListener("click", e => { if (e.target.closest("[data-mclose]")) { const mm = document.getElementById("modal"); if (mm) mm.innerHTML = ""; } }); /* __mclose */
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
    if (!$("#modal")) { const m = document.createElement("div"); m.id = "modal"; m.className = "hidden"; document.body.appendChild(m); }
    render();
  } catch (e) { console.error(e); }
})();
