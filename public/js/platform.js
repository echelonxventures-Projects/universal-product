/* LUXORA Platform - super-admin console: tenants, plans, billing, providers, monitoring, audit */
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

function linkify(m) {
  return esc(m).replace(/\/(platform|admin)\.html(\?store=[A-Za-z0-9-]+)?/g, function (s) {
    return '<a href="' + s + '" style="text-decoration:underline">' + (s.indexOf("platform") >= 0 ? "Platform console" : "Store console") + " →</a>";
  });
}
function money(n) { return "$" + (+n).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
let toastT;
function toast(msg) {
  let t = $("#ptoast");
  if (!t) { t = document.createElement("div"); t.id = "ptoast"; t.className = "p-toast"; document.body.appendChild(t); }
  t.textContent = msg; t.classList.add("show");
  clearTimeout(toastT); toastT = setTimeout(() => t.classList.remove("show"), 3200);
}
const NAV = [["dash", "◈ Command"], ["provisioning", "🛡️ Provisioning"], ["tenants", "🏬 Stores · Catalogs"], ["geo", "🌍 Geo · Countries · Taxes"], ["plans", "💼 Plans"], ["subs", "🔁 Subscriptions"],
["invoices", "🧾 Invoices"], ["modules", "🧩 Module Marketplace"], ["providers", "🔌 Provider Registry"], ["ai", "🧠 AI · Providers & Plans"], ["offers", "🎁 Global Offers"], ["runtime", "🧩 Runtime · Infra"], ["monitor", "📈 Monitoring"], ["audit", "📜 Global Audit"]];
let view = "dash";
const P = { user: null, tenants: [], plans: [] };

function shell(content) {
  $("#app").innerHTML = `
  <div class="p-shell">
    <aside class="p-side">
      <div class="p-logo"><b>LUXORA</b><small>Platform Console</small></div>
      <nav class="p-nav">${NAV.map(([k, l]) => `<button data-v="${k}" class="${view === k ? "on" : ""}">${l}</button>`).join("")}</nav>
    </aside>
    <main class="p-main"><div class="p-top"><h1>${NAV.find(n => n[0] === view)[1].replace(/^\S+\s/, "")}</h1><span class="spacer"></span>
      <span class="p-chip">platform</span><span class="p-user">${esc(P.user.email)}</span>
      <button class="p-btn sm" id="logoutBtn">Sign out</button></div>
      <div id="vBody">${content}</div></main>
  </div>`;
  $$(".p-nav button").forEach(b => b.onclick = () => { view = b.dataset.v; render(); });
  $("#logoutBtn").onclick = async () => { await api("/platform/logout", "POST"); location.reload(); };
}

async function vDash() {
  const [rev, mon, tenants] = await Promise.all([api("/platform/revenue"), api("/platform/monitor"), api("/platform/tenants")]);
  const max = Math.max(1, ...rev.byMonth.map(m => m.paid));
  return `
  <div class="p-cards">
    <div class="p-stat"><em>MRR</em><b>${money(rev.mrr)}</b><small>recurring</small></div>
    <div class="p-stat"><em>Collected</em><b>${money(rev.collected)}</b></div>
    <div class="p-stat"><em>Outstanding</em><b>${money(rev.outstanding)}</b><small style="color:var(--p-red)">unpaid</small></div>
    <div class="p-stat"><em>Platform GMV</em><b>${money(rev.gmv)}</b><small>gateway fees ${money(rev.gatewayFees)}</small></div>
    <div class="p-stat"><em>Stores</em><b>${tenants.tenants.length}</b></div>
    <div class="p-stat"><em>Requests</em><b>${mon.totals.req}</b><small>${mon.totals.err} errors · ${mon.totals.avgMs}ms avg</small></div>
  </div>
  <div class="p-grid2">
    <div class="p-panel"><h2>Billing by month</h2><div class="p-chart">${rev.byMonth.map(m => `<div class="bar" style="height:${Math.max(4, m.paid / max * 100)}%" data-tip="${esc(m.m)}: ${money(m.paid)}"></div>`).join("") || '<div class="p-empty">No invoices</div>'}</div></div>
    <div class="p-panel"><h2>Stores</h2><table class="p-table"><thead><tr><th>Store</th><th>Mode</th><th class="num">Products</th><th class="num">GMV</th><th>Plan</th></tr></thead>
      <tbody>${tenants.tenants.map(t => `<tr><td><a href="/index.html?store=${esc(t.slug)}" target="_blank">${esc(t.name)}</a></td><td>${esc(t.mode)}</td><td class="num">${t.products}</td><td class="num">${money(t.gmv)}</td><td>${esc(t.plan || "—")}</td></tr>`).join("")}</tbody></table></div>
  </div>
  <div class="p-panel"><h2>System</h2><div class="p-kv"><em>Uptime</em><span>${Math.floor(mon.system.uptimeSec / 60)} min</span><em>Memory</em><span>${mon.system.rssMB} MB</span><em>Database</em><span>${mon.system.dbKB} KB</span><em>Node</em><span>${esc(mon.system.node)}</span></div></div>`;
}
async function vTenants() {
  const { tenants } = await api("/platform/tenants");
  P.tenants = tenants;
  return `
  <div class="p-panel"><div style="display:flex;align-items:center;gap:12px;margin-bottom:6px">
    <h2 style="margin:0">Stores (${tenants.length})</h2><span style="flex:1"></span>
    <button class="p-btn primary sm" id="newTenant">+ Launch store</button></div>
    <p style="margin:0 0 14px;color:var(--p-muted);font-size:13px">Each store's <b>Products</b>, SKUs &amp; inventory, orders, suppliers, compliance and settings live in that store's <b>Store Console</b> — click <b>Manage · Catalog</b> to open it for a store.</p>
    <div class="p-scroll-x"><table class="p-table"><thead><tr><th>Store</th><th>Slug</th><th>Jurisdiction</th><th>Owner</th><th>Mode</th><th>Industries</th><th class="num">Products</th><th class="num">Orders</th><th class="num">GMV</th><th>Plan</th><th>Status</th><th></th></tr></thead>
    <tbody>${tenants.map(t => `<tr><td><b>${esc(t.name)}</b></td><td>${esc(t.slug)}</td><td>${esc(t.country || "—")}</td><td class="p-tag">${esc((t.profile && t.profile.ownerEmail) || "—")}</td><td>${esc(t.mode)}</td>
      <td class="p-tag">${esc((t.industries || "[]").replace(/["[\]]/g, "").slice(0, 40))}</td>
      <td class="num">${t.products}</td><td class="num">${t.orders}</td><td class="num">${money(t.gmv)}</td>
      <td>${esc(t.plan || "—")}</td><td><span class="badge ${esc(t.status)}">${esc(t.status)}</span></td>
      <td style="white-space:nowrap"><button class="p-btn sm" data-open="${t.id}">Open</button>
        <button class="p-btn sm" data-tedit="${t.id}">Edit</button>
        <button class="p-btn sm primary" data-imp="${t.id}" title="Enter this store's Store Console — Products, SKUs, Orders and more">Manage · Catalog</button>
        <button class="p-btn sm" data-susp="${t.id}">${t.status === "active" ? "Suspend" : "Resume"}</button>
        <button class="p-btn sm" data-inv="${t.id}">Invoice</button>
        <button class="p-btn sm danger" data-del="${t.id}">✕</button></td></tr>`).join("")}</tbody></table></div></div>`;
}
async function vPlans() {
  const { plans } = await api("/platform/plans");
  P.plans = plans;
  return `<div class="p-panel"><div style="display:flex;align-items:center;gap:12px;margin-bottom:14px">
    <h2 style="margin:0">Plans</h2><span style="flex:1"></span><button class="p-btn primary sm" id="newPlan">+ New plan</button></div>
    <table class="p-table"><thead><tr><th>Name</th><th class="num">Price/mo</th><th>Currency</th><th class="num">Max products</th><th class="num">Max orders/mo</th><th></th></tr></thead>
    <tbody>${plans.map(p => `<tr><td><b>${esc(p.name)}</b></td><td class="num">${money(p.price_month)}</td><td>${esc(p.currency)}</td><td class="num">${p.max_products.toLocaleString()}</td><td class="num">${p.max_orders_month.toLocaleString()}</td>
      <td><button class="p-btn sm" data-editplan="${p.id}">Edit</button></td></tr>`).join("")}</tbody></table></div>`;
}
async function vSubs() {
  const [subs, tenants, plans] = await Promise.all([api("/meta/entity/subscription"), api("/platform/tenants"), api("/platform/plans")]);
  const tn = Object.fromEntries(tenants.tenants.map(t => [t.id, t.name]));
  const pn = Object.fromEntries(plans.plans.map(p => [p.id, p.name]));
  return `<div class="p-panel"><div style="display:flex;align-items:center;gap:12px;margin-bottom:14px">
    <h2 style="margin:0">Subscriptions</h2><span style="flex:1"></span><button class="p-btn primary sm" id="newSub">+ Assign plan</button></div>
    <table class="p-table"><thead><tr><th>Store</th><th>Plan</th><th>Status</th><th>Started</th><th>Renews</th></tr></thead>
    <tbody>${subs.rows.map(s => `<tr><td>${esc(tn[s.tenant_id] || s.tenant_id)}</td><td>${esc(pn[s.plan_id] || s.plan_id)}</td>
      <td><span class="badge ${esc(s.status)}">${esc(s.status)}</span></td><td>${esc(s.started_at)}</td><td>${esc(s.renews_at)}</td></tr>`).join("")}</tbody></table></div>`;
}
async function vInvoices() {
  const { invoices } = await api("/platform/invoices");
  return `<div class="p-panel"><h2>Invoices</h2>
    <table class="p-table"><thead><tr><th>Number</th><th>Store</th><th>Period</th><th class="num">Amount</th><th>Status</th><th>Issued</th><th></th></tr></thead>
    <tbody>${invoices.map(i => `<tr><td>${esc(i.number)}</td><td>${esc(i.tenant_name)}</td><td>${esc(i.period_start)} → ${esc(i.period_end || "")}</td>
      <td class="num">${money(i.amount)}</td><td><span class="badge ${esc(i.status)}">${esc(i.status)}</span></td><td class="p-tag">${esc(i.issued_at)}</td>
      <td>${i.status !== "paid" ? `<button class="p-btn sm primary" data-payinv="${i.id}">Collect</button>` : "✓"}</td></tr>`).join("")}</tbody></table></div>`;
}
async function vProviders() {
  const { custom, availability } = await api("/platform/custom-providers");
  const [pay, ship, not] = await Promise.all([api("/meta/entity/provider_def"), api("/meta/entity/country")]);
  const byCountry = {};
  availability.forEach(a => { (byCountry[a.provider_id] = byCountry[a.provider_id] || []).push(a.country_code); });
  const kindTable = (kind, title) => {
    const rows = pay.rows.filter(x => x.kind === kind);
    return `<div class="p-panel"><h2>${title} (${rows.length})</h2>
      <table class="p-table"><thead><tr><th></th><th>Provider</th><th>Countries (availability relation)</th><th>Methods</th><th class="num">Fee</th><th></th></tr></thead>
      <tbody>${rows.map(p => `<tr><td class="t-emoji">${esc(p.emoji)}</td><td><b>${esc(p.name)}</b><br><span class="p-tag">${esc(p.description || "")}</span></td>
        <td class="p-tag">${(byCountry[p.id] || []).length >= 13 ? "🌍 global · " + (byCountry[p.id] || []).length : esc((byCountry[p.id] || []).join(" "))}</td>
        <td class="p-tag">${esc((JSON.parse(p.methods || "[]")).join(", "))}</td><td class="num">${p.fee_pct}%</td>
        <td style="white-space:nowrap"><button class="p-btn sm" data-pedit="${p.id}">Edit</button>
        <button class="p-btn sm" data-pavail="${p.id}">Countries</button></td></tr>`).join("")}</tbody></table></div>`;
  };
  return `
  <p class="p-tag" style="margin:0 0 14px">Provider catalogue is entity data — provider_def + provider_availability (countries) + country + tax_mode. Edit here or via the entity APIs; every storefront and checkout reads these live.</p>
  ${kindTable("payment", "Payment providers")}
  <div class="p-grid2">${kindTable("shipping", "Shipping carriers")}${kindTable("notification", "Notification channels")}</div>
  <div class="p-panel"><h2>Custom providers (${custom.length})</h2>
    <table class="p-table"><thead><tr><th>Kind</th><th>ID</th><th>Name</th><th></th></tr></thead>
    <tbody>${custom.map(c => { const m = JSON.parse(c.manifest); return `<tr><td>${esc(c.kind)}</td><td>${esc(m.id)}</td><td>${esc(m.name)}</td><td><button class="p-btn sm danger" data-delprov="${c.id}">✕</button></td></tr>`; }).join("") || '<tr><td colspan="4" class="p-empty">None</td></tr>'}</tbody></table>
    <h2 style="margin-top:18px">Register a new provider (no code)</h2>
    <div class="p-form"><div class="row"><label><span>Kind</span><select id="cpKind"><option>payment</option><option>shipping</option><option>notification</option><option>tax</option></select></label>
    <label><span>Manifest (JSON)</span><textarea id="cpManifest" rows="6">{
  "id": "mybank", "name": "MyBank", "emoji": "🏦",
  "countries": ["IN"], "methods": ["upi", "netbanking"],
  "feePct": 1.5, "feeFixed": 0,
  "fields": [{"key":"apiKey","label":"API key","secret":true}]
}</textarea></label></div>
    <button class="p-btn primary" id="cpSave">Register provider</button></div></div>`;
}
async function vGeo() {
  const [cs, tm, pv, cy, fx] = await Promise.all([api("/meta/entity/country"), api("/meta/entity/tax_mode"), api("/meta/entity/provider_availability"), api("/meta/entity/currency"), api("/platform/fx")]);
  P.fx = fx;
  const cnt = {}; pv.rows.forEach(r => cnt[r.provider_id] = (cnt[r.provider_id] || 0) + 1);
  return `
  <div class="p-panel"><h2>Countries &amp; currencies (entity: country)</h2>
    <p class="p-tag">Storefronts derive currency, symbol, locale, decimals and default tax from these rows. Add a country → it instantly appears in every store's settings and provider availability.</p>
    <div class="p-scroll-x"><table class="p-table"><thead><tr><th>Code</th><th>Name</th><th>Currency</th><th>Symbol</th><th>Locale</th><th class="num">Decimals</th><th>Tax mode</th><th class="num">Rate</th><th class="num">Providers</th></tr></thead>
    <tbody>${cs.rows.map(c => `<tr><td><b>${esc(c.code)}</b></td><td>${esc(c.name)}</td><td>${esc(c.currency)}</td><td class="t-emoji" style="font-size:16px">${esc(c.symbol)}</td><td class="p-tag">${esc(c.locale)}</td><td class="num">${c.decimals}</td><td><span class="badge published">${esc(c.tax_mode)}</span></td><td class="num">${(c.tax_rate * 100).toFixed(2)}%</td><td class="num">${new Set(pv.rows.filter(x => x.country_code === c.code).map(x => x.provider_id)).size}</td></tr>`).join("")}</tbody></table></div>
    <button class="p-btn primary sm" id="addCountry">+ Add country</button></div>
  <div class="p-panel"><h2>Currencies &amp; FX (entity: currency)</h2>
    <p class="p-tag">Jurisdiction sets the default; stores may override to any currency here — storefront prices, cart and checkout totals convert at these rates and snapshot them per order.</p>
    <div class="p-scroll-x"><table class="p-table"><thead><tr><th>Code</th><th>Name</th><th>Symbol</th><th class="num">Decimals</th><th class="num">1 unit = USD</th><th>Countries</th><th></th></tr></thead>
    <tbody>${cy.rows.map(x => `<tr><td><b>${esc(x.code)}</b></td><td>${esc(x.name)}</td><td class="t-emoji" style="font-size:15px">${esc(x.symbol)}</td><td class="num">${x.decimals}</td><td class="num">${x.usd}</td>
      <td class="p-tag">${cs.rows.filter(c => c.currency === x.code).map(c => c.code).join(" ") || "—"}</td>
      <td style="white-space:nowrap"><button class="p-btn sm" data-cedit="${esc(x.code)}">Edit</button> <button class="p-btn sm danger" data-cdel="${esc(x.code)}">✕</button></td></tr>`).join("")}</tbody></table></div>
    <button class="p-btn primary sm" id="addCur">+ Add currency</button></div>
  <div class="p-panel"><h2>Conversions &amp; FX feed</h2>
    <div class="row3" style="display:grid;grid-template-columns:1fr 2fr auto;gap:12px;align-items:end">
      <label><span>Rate source</span><select id="fxProv"><option value="manual" ${(fx.provider.provider||"manual")==="manual"?"selected":""}>Manual (offline)</option><option value="feed" ${fx.provider.provider==="feed"?"selected":""}>HTTP JSON feed</option></select></label>
      <label><span>Feed URL — JSON of {"CODE": usdValue}</span><input id="fxUrl" value="${esc(fx.provider.url||"")}" placeholder="https://your-fx-provider.example/rates.json"></label>
      <span><button class="p-btn sm" id="fxProvSave">Save</button> <button class="p-btn sm primary" id="fxSync">⟳ Sync now</button></span></div>
    <p class="p-tag">Last sync: ${fx.lastSync ? esc(fx.lastSync.at)+" — applied "+fx.lastSync.applied.length+(fx.lastSync.skipped.length?" skipped "+fx.lastSync.skipped.join(","):"") : "never"} · USD is always the 1.0 anchor.</p>
    <details style="margin:10px 0"><summary class="p-tag" style="cursor:pointer">Bulk update rates (manual)</summary>
      <textarea id="fxBulk" rows="4" style="width:100%;background:var(--p-bg);border:1px solid var(--p-line);border-radius:10px;color:var(--p-text);padding:10px;font-family:monospace">{ "EUR": 1.08, "GBP": 1.27, "INR": 0.012 }</textarea>
      <button class="p-btn sm primary" id="fxBulkGo">Apply rates</button></details>
    <div class="row3" style="display:grid;grid-template-columns:1fr 1fr 1fr auto;gap:10px;align-items:end;margin-bottom:10px">
      <label><span>Convert amount</span><input id="cxAmount" type="number" step="any" value="100"></label>
      <label><span>From</span><select id="cxFrom">${cy.rows.map(x => `<option>${x.code}</option>`).join("")}</select></label>
      <label><span>To</span><select id="cxTo">${cy.rows.map(x => `<option value="${x.code}" ${x.code==="INR"?"selected":""}>${x.code}</option>`).join("")}</select></label>
      <button class="p-btn sm" id="cxGo">Convert →</button><div class="p-tag" id="cxOut"></div></div>
    <table class="p-table"><thead><tr><th>When</th><th>Currency</th><th class="num">USD value</th><th>Source</th><th>Detail</th></tr></thead>
    <tbody>${fx.history.slice(0, 25).map(h => `<tr><td class="p-tag">${esc(h.created_at)}</td><td><b>${esc(h.currency)}</b></td><td class="num">${h.usd}</td><td><span class="badge ${h.source==="feed"?"published":"draft"}">${esc(h.source)}</span></td><td class="p-tag">${esc((h.note||"").slice(0,48))}</td></tr>`).join("") || '<tr><td colspan="5" class="p-empty">No rate changes recorded yet — edit a rate or sync a feed</td></tr>'}</tbody></table></div>
  <div class="p-panel"><h2>Tax modes (entity: tax_mode)</h2>
    <table class="p-table"><thead><tr><th>Key</th><th>Label</th><th>Description</th><th></th></tr></thead>
    <tbody>${tm.rows.map(t => `<tr><td><b>${esc(t.key)}</b></td><td>${esc(t.label)}</td><td class="p-tag">${esc(t.description || "")}</td><td><span class="p-tag">${tm.rows.filter(x => x.tax_mode === t.key).length ? "" : ""}</span></td></tr>`).join("")}</tbody></table>
    <button class="p-btn primary sm" id="addTax">+ Add tax mode</button></div>`;
}
async function wireGeoFx() {
  const d = document;
  const g = id => d.getElementById(id);
  if (!g("fxSync")) return;
  g("fxProvSave").onclick = async () => { try { await api("/platform/fx/provider", "PUT", { provider: g("fxProv").value, url: g("fxUrl").value }); toast("FX provider saved"); render(); } catch (e) { toast(e.message); } };
  g("fxSync").onclick = async () => { try { const r = await api("/platform/fx/sync", "POST", {}); toast("Synced " + r.applied.length + " rates" + (r.skipped.length ? " (skipped " + r.skipped.join(",") + ")" : "")); render(); } catch (e) { toast(e.message); } };
  const bg = g("fxBulkGo"); if (bg) bg.onclick = async () => { try { const rates = JSON.parse(g("fxBulk").value); const r = await api("/platform/fx/rates", "POST", { rates, note: "platform bulk" }); toast("Applied " + r.applied.length + (r.skipped.length ? ", skipped " + r.skipped.join(",") : "")); render(); } catch (e) { toast(e.message); } };
  g("cxGo").onclick = async () => { try { const r = await api("/fx?amount=" + encodeURIComponent(g("cxAmount").value || 1) + "&from=" + g("cxFrom").value + "&to=" + g("cxTo").value); g("cxOut").textContent = `= ${r.result.toLocaleString()} ${r.to} (rate ${r.rate})`; } catch (e) { g("cxOut").textContent = e.message; } };
}
/* ============ MODULE MARKETPLACE: every capability is a purchasable product ============ */
async function vModules() {
  const { modules, installs, tenants } = await api("/platform/modules");
  P.mods = { modules, installs, tenants };
  const installedSet = new Set(installs.filter(i => i.status === "installed").map(i => i.tenant_id + "|" + i.module_id));
  const cats = {};
  modules.forEach(m => { (cats[m.category] = cats[m.category] || []).push(m); });
  return `
  <p class="p-tag" style="margin:0 0 14px">Modules are products: buying one creates a paid invoice (MOD-*) and applies its manifest — features, payment rails, catalog ranges, engine capabilities — instantly. Every store auto-purchases the free baselines (identity, gid, geo, cart, listing, checkout, seo, reco, billing).</p>
  ${Object.entries(cats).map(([cat, ms]) => `
  <div class="p-panel"><h2>${esc(cat)}</h2><div class="mod-grid">${ms.map(m => {
    const caps = (m.manifest.capabilities || []).join(", ");
    return `<div class="mod-card"><div class="mod-head"><b>${esc(m.name)}</b><span class="price">${m.price > 0 ? "$" + m.price : "free"}</span></div>
      <p class="p-tag">${esc(m.summary || "")}</p><p class="p-tag"><code>${esc(caps || m.id)}</code></p>
      <div class="mod-installs">${tenants.map(t => {
        const on = installedSet.has(t.id + "|" + m.id);
        return `<span class="mi ${on ? "on" : ""}" data-mod="${esc(m.id)}" data-tid="${t.id}" title="${esc(m.name)} → ${esc(t.name)}">${esc(t.slug)}</span>`;
      }).join("")}</div></div>`;
  }).join("")}</div></div>`).join("")}`;
}
async function wireModules() {
  document.querySelectorAll("[data-mod]").forEach(el => {
    el.onclick = async () => {
      const { modules, tenants } = P.mods;
      const m = modules.find(x => x.id === el.dataset.mod); const t = tenants.find(x => String(x.id) === el.dataset.tid);
      const installed = el.classList.contains("on");
      const fields = (m.manifest.fields || []);
      const mm = modal(`<div class="p-modal-head"><h3>${esc(m.name)} → ${esc(t.name)}</h3><button onclick="document.getElementById('modal').innerHTML=''">✕</button></div>
        <div class="p-form">
        ${installed ? `<p class="p-tag">${m.price > 0 ? "Purchased (invoice on record)." : "Baseline — auto-purchased at provisioning."}</p><button class="p-btn danger" id="mUn">Uninstall / disable</button>` :
          `<p class="p-tag">${m.price > 0 ? "Price: $" + m.price + " — a paid invoice will be created and marked collected." : "Free — installs instantly."}</p>
           ${fields.map(f => `<label><span>${esc(f.label || f.key)}</span><input data-cfg="${esc(f.key)}" placeholder="e.g. ${f.key === "requireLoginCheckout" ? "true" : "…"}"></label>`).join("")}
           <button class="p-btn primary" id="mBuy">Purchase & install</button>`}
        </div>`);
      if (installed) mm.querySelector("#mUn").onclick = async () => {
        try { await api("/platform/modules/" + encodeURIComponent(m.id) + "/uninstall", "POST", { tenant_id: t.id }); mm.innerHTML = ""; toast("Module disabled"); render(); } catch (e) { toast(e.message); }
      };
      else mm.querySelector("#mBuy").onclick = async () => {
        const cfg = {};
        mm.querySelectorAll("[data-cfg]").forEach(i => { if (i.value) cfg[i.dataset.cfg] = (i.value === "true" || i.value === "false") ? i.value === "true" : (isNaN(+i.value) ? i.value : +i.value); });
        try {
          const r = await api("/platform/modules/" + encodeURIComponent(m.id) + "/install", "POST", { tenant_id: t.id, config: cfg });
          mm.innerHTML = ""; toast(r.invoice ? "Installed · invoice " + r.invoice : "Installed"); render();
        } catch (e) { toast(e.message); }
      };
    };
  });
}

async function vMonitor() {
  const m = await api("/platform/monitor");
  const max = Math.max(1, ...m.series.map(x => x.req));
  return `
  <div class="p-cards">
    <div class="p-stat"><em>Total requests</em><b>${m.totals.req}</b><small>${m.totals.err} errors</small></div>
    <div class="p-stat"><em>Avg latency</em><b>${m.totals.avgMs}ms</b></div>
    <div class="p-stat"><em>Uptime</em><b>${Math.floor(m.system.uptimeSec / 60)}m</b></div>
    <div class="p-stat"><em>Memory</em><b>${m.system.rssMB}MB</b></div>
    <div class="p-stat"><em>DB size</em><b>${m.system.dbKB}KB</b></div>
  </div>
  <div class="p-panel"><h2>Live traffic · all tenants · last 30 min</h2>
    <div class="p-chart">${m.series.map(x => `<div class="bar" style="height:${Math.max(3, x.req / max * 100)}%" data-tip="${new Date(x.t).toLocaleTimeString()}: ${x.req}"></div>`).join("")}</div></div>
  <div class="p-grid2">
    <div class="p-panel"><h2>Top endpoints</h2><table class="p-table"><thead><tr><th>Endpoint</th><th class="num">Calls</th><th class="num">Err</th><th class="num">ms</th></tr></thead>
      <tbody>${m.endpoints.map(x => `<tr><td>${esc(x.endpoint)}</td><td class="num">${x.count}</td><td class="num">${x.err}</td><td class="num">${x.avgMs}</td></tr>`).join("")}</tbody></table></div>
    <div class="p-panel"><h2>Stores</h2><table class="p-table"><thead><tr><th>Slug</th><th>Name</th><th>Status</th></tr></thead>
      <tbody>${m.tenants.map(t => `<tr><td>${esc(t.slug)}</td><td>${esc(t.name)}</td><td><span class="badge ${esc(t.status)}">${esc(t.status)}</span></td></tr>`).join("")}</tbody></table></div>
  </div>`;
}
async function vAudit() {
  const { entries } = await api("/platform/audit");
  return `<div class="p-panel"><h2>Global audit trail</h2>
    <input class="p-search" placeholder="Filter…" id="auditQ" style="margin-bottom:12px">
    <div class="p-scroll-x"><table class="p-table" id="auditTbl"><thead><tr><th>When</th><th>Store</th><th>Actor</th><th>Action</th><th>Entity</th><th>Ref</th><th>Detail</th></tr></thead>
    <tbody>${entries.map(e => `<tr><td>${esc(e.created_at)}</td><td>${esc(e.tenant_id || "—")}</td><td>${esc(e.actor_type)} · ${esc(e.actor_name || "")}</td>
      <td><b>${esc(e.action)}</b></td><td>${esc(e.entity || "")}</td><td>${esc(e.entity_id || "")}</td><td class="p-tag">${esc((e.meta || "").slice(0, 80))}</td></tr>`).join("")}</tbody></table></div></div>`;
}

function modal(html) {
  let m = $("#modal");
  if (!m) { m = document.createElement("div"); m.id = "modal"; document.body.appendChild(m); }
  m.innerHTML = `<div class="p-modal"><div class="p-modal-box">${html}</div></div>`;
  m.querySelector(".p-modal").addEventListener("click", e => { if (e.target.classList.contains("p-modal")) m.innerHTML = ""; });
  return m;
}
document.addEventListener("click", async e => {
  try {
    const open = e.target.closest("[data-open]"), imp = e.target.closest("[data-imp]"), susp = e.target.closest("[data-susp]"),
      del = e.target.closest("[data-del]"), inv = e.target.closest("[data-inv]"), pay = e.target.closest("[data-payinv]"),
      editp = e.target.closest("[data-editplan]"), delprov = e.target.closest("[data-delprov]");
    if (open) window.open("/index.html?store=" + P.tenants.find(t => t.id == open.dataset.open).slug, "_blank");
    if (imp) { const r = await api(`/platform/tenants/${imp.dataset.imp}/impersonate`, "POST", {}); window.open(r.url, "_blank"); }
    if (susp) { const t = P.tenants.find(x => x.id == susp.dataset.susp); await api("/platform/tenants/" + t.id, "PUT", { status: t.status === "active" ? "suspended" : "active" }); render(); }
    if (del) { if (confirm("Delete store and ALL its data?")) { await api("/platform/tenants/" + del.dataset.del, "DELETE", {}); render(); } }
    if (inv) { await api(`/platform/tenants/${inv.dataset.inv}/invoice`, "POST", {}); toast("Invoice generated"); render(); }
    if (pay) {
      const m = modal(`<div class="p-modal-head"><h3>Collect invoice</h3><button data-mclose>✕</button></div>
        <div class="p-form"><label><span>Gateway</span><select id="payGw"><option>stripe</option><option>paypal</option><option>razorpay</option><option>adyen</option><option>bank</option></select></label>
        <button class="p-btn primary" id="payGo">Charge</button></div>`);
      m.querySelector("#payGo").onclick = async () => {
        const r = await api(`/platform/invoices/${pay.dataset.payinv}/pay`, "POST", { gateway: m.querySelector("#payGw").value });
        m.innerHTML = ""; toast("Paid · txn " + r.txn_ref); render();
      };
    }
    if (editp) {
      const p = P.plans.find(x => x.id == editp.dataset.editplan);
      const m = modal(`<div class="p-modal-head"><h3>${esc(p.name)}</h3><button data-mclose>✕</button></div>
        <div class="p-form"><div class="row"><label><span>Name</span><input id="plnName" value="${esc(p.name)}"></label><label><span>Price/mo</span><input id="plnPrice" type="number" step="any" value="${p.price_month}"></label></div>
        <div class="row"><label><span>Max products</span><input id="plnP" type="number" value="${p.max_products}"></label><label><span>Max orders/mo</span><input id="plnO" type="number" value="${p.max_orders_month}"></label></div>
        <button class="p-btn primary" id="plnSave">Save</button></div>`);
      m.querySelector("#plnSave").onclick = async () => {
        await api("/platform/plans/" + p.id, "PUT", { name: m.querySelector("#plnName").value, price_month: Number(m.querySelector("#plnPrice").value), max_products: Number(m.querySelector("#plnP").value), max_orders_month: Number(m.querySelector("#plnO").value) });
        m.innerHTML = ""; toast("Plan updated"); render();
      };
    }
    if (delprov) { await api("/platform/custom-providers/" + delprov.dataset.delprov, "DELETE", {}); render(); }
    if (e.target.id === "newTenant") return openTenantWizard(null);
    const edit = e.target.closest("[data-tedit]");
    if (edit) return openTenantWizard(Number(edit.dataset.tedit));
    if (e.target.id === "newPlan") {
      const mm = modal(`<div class="p-modal-head"><h3>New plan</h3><button data-mclose>✕</button></div>
        <div class="p-form"><div class="row"><label><span>Name</span><input id="npName"></label><label><span>Price/mo</span><input id="npPrice" type="number" step="any"></label></div>
        <div class="row"><label><span>Max products</span><input id="npP" type="number" value="500"></label><label><span>Max orders/mo</span><input id="npO" type="number" value="2000"></label></div>
        <button class="p-btn primary" id="npGo">Create</button></div>`);
      mm.querySelector("#npGo").onclick = async () => {
        await api("/platform/plans", "POST", { name: mm.querySelector("#npName").value, price_month: Number(mm.querySelector("#npPrice").value), max_products: Number(mm.querySelector("#npP").value), max_orders_month: Number(mm.querySelector("#npO").value) });
        mm.innerHTML = ""; toast("Plan created"); render();
      };
    }
    if (e.target.id === "newSub") {
      const [tenants, plans] = await Promise.all([api("/platform/tenants"), api("/platform/plans")]);
      const mm = modal(`<div class="p-modal-head"><h3>Assign plan</h3><button data-mclose>✕</button></div>
        <div class="p-form"><label><span>Store</span><select id="sbT">${tenants.tenants.map(t => `<option value="${t.id}">${esc(t.name)}</option>`).join("")}</select></label>
        <label><span>Plan</span><select id="sbP">${plans.plans.map(p => `<option value="${p.id}">${esc(p.name)}</option>`).join("")}</select></label>
        <button class="p-btn primary" id="sbGo">Assign</button></div>`);
      mm.querySelector("#sbGo").onclick = async () => {
        await api(`/platform/tenants/${mm.querySelector("#sbT").value}/subscribe`, "POST", { plan_id: Number(mm.querySelector("#sbP").value) });
        mm.innerHTML = ""; toast("Subscription updated"); render();
      };
    }
    if (e.target.id === "cpSave") {
      await api("/platform/custom-providers", "POST", { kind: $("#cpKind").value, manifest: JSON.parse($("#cpManifest").value) });
      toast("Provider registered platform-wide"); render();
    }
    const pe = e.target.closest("[data-pedit]"), pa = e.target.closest("[data-pavail]");
    if (pe) {
      const { rows } = await api("/meta/entity/provider_def");
      const r = rows.find(x => x.id === pe.dataset.pedit);
      const m = modal(`<div class="p-modal-head"><h3>${esc(r.name)}</h3><button data-mclose>✕</button></div>
        <div class="p-form"><div class="row3"><label><span>Name</span><input id="pvName" value="${esc(r.name)}"></label><label><span>Emoji</span><input id="pvEmoji" value="${esc(r.emoji || "")}"></label><label><span>Fee %</span><input id="pvFee" type="number" step="any" value="${r.fee_pct}"></label></div>
        <label><span>Methods (JSON)</span><input id="pvM" value="${esc(r.methods)}"></label>
        <label><span>Credential fields (JSON)</span><textarea id="pvF" rows="3">${esc(r.fields)}</textarea></label>
        <button class="p-btn primary" id="pvSave">Save</button></div>`);
      m.querySelector("#pvSave").onclick = async () => {
        await api("/meta/entity/provider_def/" + encodeURIComponent(r.id + "|" + r.kind), "PUT", { name: m.querySelector("#pvName").value, emoji: m.querySelector("#pvEmoji").value, fee_pct: Number(m.querySelector("#pvFee").value), methods: JSON.parse(m.querySelector("#pvM").value || "[]"), fields: JSON.parse(m.querySelector("#pvF").value || "[]") });
        m.innerHTML = ""; toast("Provider updated — live everywhere"); render();
      };
    }
    if (pa) {
      const [all0, av] = await Promise.all([api("/meta/entity/country"), api("/meta/entity/provider_availability")]);
      const have = new Set(av.rows.filter(x => x.provider_id === pa.dataset.pavail).map(x => x.country_code));
      const m = modal(`<div class="p-modal-head"><h3>Availability · ${esc(pa.dataset.pavail)}</h3><button data-mclose>✕</button></div>
        <div class="p-form">${all0.rows.map(c => `<label style="display:flex;gap:8px;align-items:center"><input type="checkbox" data-cc="${c.code}" ${have.has(c.code) ? "checked" : ""}> ${esc(c.name)} (${c.code} · ${esc(c.currency)})</label>`).join("")}
        <button class="p-btn primary" id="avSave">Save availability</button></div>`);
      m.querySelector("#avSave").onclick = async () => {
        const cur = new Set([...m.querySelectorAll("[data-cc]:checked")].map(x => x.dataset.cc));
        for (const c of m.querySelectorAll("[data-cc]")) {
          const key = c.dataset.cc;
          if (c.checked && !have.has(key)) await api("/meta/entity/provider_availability", "POST", { provider_id: pa.dataset.pavail, country_code: key });
          if (!c.checked && have.has(key)) await api("/meta/entity/provider_availability/" + encodeURIComponent(pa.dataset.pavail + "|" + key), "DELETE", {});
        }
        m.innerHTML = ""; toast("Availability saved"); render();
      };
    }
    if (e.target.id === "addCountry") {
      const m = modal(`<div class="p-modal-head"><h3>New country</h3><button data-mclose>✕</button></div>
        <div class="p-form"><div class="row3"><label><span>Code</span><input id="ncCode" maxlength="4" placeholder="CH"></label><label><span>Name</span><input id="ncName"></label><label><span>Currency</span><input id="ncCur" placeholder="CHF"></label></div>
        <div class="row3"><label><span>Symbol</span><input id="ncSym"></label><label><span>Locale</span><input id="ncLoc" placeholder="de-CH"></label><label><span>Decimals</span><input id="ncDec" type="number" value="2"></label></div>
        <div class="row"><label><span>Tax mode</span><input id="ncTm" value="vat"></label><label><span>Tax rate (0-1)</span><input id="ncTr" type="number" step="any" value="0.08"></label></div>
        <button class="p-btn primary" id="ncGo">Add</button></div>`);
      m.querySelector("#ncGo").onclick = async () => {
        const q = x => m.querySelector(x).value;
        await api("/meta/entity/country", "POST", { code: q("#ncCode").value.toUpperCase(), name: q("#ncName").value, currency: q("#ncCur").value, symbol: q("#ncSym").value, locale: q("#ncLoc").value, decimals: Number(q("#ncDec").value), tax_mode: q("#ncTm").value, tax_rate: Number(q("#ncTr").value) });
        m.innerHTML = ""; toast("Country entity created — now assignable to providers"); render();
      };
    }
    if (e.target.id === "addCur" || e.target.closest("[data-cedit]")) {
      const code = e.target.dataset ? e.target.dataset.cedit : null;
      const { rows } = await api("/meta/entity/currency");
      const x = code ? rows.find(r => r.code === code) : null;
      const mm = modal(`<div class="p-modal-head"><h3>${x ? "Edit " + esc(x.code) : "New currency"}</h3><button data-mclose>✕</button></div>
        <div class="p-form"><div class="row3"><label><span>Code *</span><input id="cyCode" value="${x ? esc(x.code) : ""}" ${x ? "disabled" : ""}></label><label><span>Name *</span><input id="cyName" value="${x ? esc(x.name) : ""}"></label><label><span>Symbol *</span><input id="cySym" value="${x ? esc(x.symbol) : ""}"></label></div>
        <div class="row3"><label><span>Decimals</span><input id="cyDec" type="number" value="${x ? x.decimals : 2}"></label><label><span>1 unit = USD</span><input id="cyUsd" type="number" step="0.000001" value="${x ? x.usd : 1}"></label><label><span>Active</span><select id="cyAct"><option value="1">yes</option><option value="0" ${x && !x.active ? "selected" : ""}>no</option></select></label></div>
        <button class="p-btn primary" id="cyGo">Save</button></div>`);
      mm.querySelector("#cyGo").onclick = async () => {
        const q = i => mm.querySelector(i).value;
        const body = { code: q("#cyCode").value.toUpperCase(), name: q("#cyName").value, symbol: q("#cySym").value, decimals: Number(q("#cyDec").value), usd: Number(q("#cyUsd").value), active: Number(q("#cyAct").value) };
        try { await api(x ? "/meta/entity/currency/" + encodeURIComponent(x.code) : "/meta/entity/currency", x ? "PUT" : "POST", body); mm.innerHTML = ""; toast("Currency saved"); render(); } catch (e2) { toast(e2.message); }
      };
    }
    const cdel = e.target.closest("[data-cdel]");
    if (cdel) { try { await api("/meta/entity/currency/" + encodeURIComponent(cdel.dataset.cdel), "DELETE", {}); toast("Currency removed"); render(); } catch (e2) { toast(e2.message); } }
    if (e.target.id === "addTax") {
      const key = prompt("Tax mode key (e.g. sales_tax)"); if (!key) return;
      const label = prompt("Label") || key;
      await api("/meta/entity/tax_mode", "POST", { key: key.toLowerCase().replace(/\W/g, "_"), label, description: "", fields: [] });
      toast("Tax mode created"); render();
    }
    if (e.target.id === "auditQ") {
      const q = e.target.value.toLowerCase();
      $$("#auditTbl tbody tr").forEach(tr => tr.style.display = tr.textContent.toLowerCase().includes(q) ? "" : "none");
    }
  } catch (err) { toast(err.message); }
});

/* ============ STORE PROVISIONING WIZARD: owner · jurisdiction · taxation · categories · gateways · plan ============ */
async function openTenantWizard(editId) {
  const [meta, cp, plans, tenants] = await Promise.all([api("/meta"), api("/platform/custom-providers"), api("/platform/plans"), api("/platform/tenants")]);
  const countries = meta.countries, industries = meta.industries, taxModes = meta.taxModes;
  const availBy = {};
  (cp.availability || []).forEach(a => (availBy[a.provider_id] = availBy[a.provider_id] || new Set()).add(a.country_code));
  const payProviders = cp.builtIn.payment;
  const t = editId ? tenants.tenants.find(x => x.id === editId) : null;
  const prof = t ? (typeof t.profile === "string" ? JSON.parse(t.profile || "{}") : (t.profile || {})) : {};
  let cur = t ? t.country : "US";
  const countryOf = code => countries.find(c => c.code === code) || countries[0];
  const defaultsFor = code => payProviders.filter(p => (availBy[p.id] || new Set()).has(code)).map(p => p.id).slice(0, 2).concat("cod");
  const m = modal(`
    <div class="p-modal-head"><h3>${t ? "Edit store — " + esc(t.name) : "Launch a new store"}</h3><button data-mclose>✕</button></div>
    <div class="p-form">
      <fieldset><legend>Store</legend>
        <div class="row"><label><span>Store name *</span><input id="wName" value="${t ? esc(t.name) : ""}" ${t ? "disabled" : ""} placeholder="NOVA MART"></label>
        <label><span>Slug *</span><input id="wSlug" value="${t ? esc(t.slug) : ""}" ${t ? "disabled" : ""} placeholder="nova"></label></div>
        <label><span>Tagline</span><input id="wTag" placeholder="Curated essentials, delivered"></label>
        <label><span>Deployment mode</span><select id="wMode">${meta.deployModes.map(x => `<option value="${x.key}" ${t && t.mode === x.key ? "selected" : ""}>${x.name} — ${x.desc}</option>`).join("")}</select></label>
      </fieldset>
      <fieldset><legend>Owner / operator account (store admin)</legend>
        <div class="row3"><label><span>Full name *</span><input id="wOwnName" value="${esc(prof.ownerName || "")}" placeholder="Nora Vey"></label>
        <label><span>Email *</span><input id="wOwnEmail" type="email" value="${esc(prof.ownerEmail || "")}" placeholder="owner@nova.shop"></label>
        <label><span>Phone</span><input id="wOwnPhone" value="${esc(prof.ownerPhone || "")}" placeholder="+1…"></label></div>
        <label><span>Password ${t ? "(leave blank to keep current)" : "* (min 6 chars)"}</span><input id="wOwnPass" type="password"></label>
      </fieldset>
      <fieldset><legend>Jurisdiction &amp; legal identity</legend>
        <div class="row3"><label><span>Country (tax + currency + gateways derive from this) *</span><select id="wCountry">${countries.map(c => `<option value="${c.code}" ${(t ? t.country : "US") === c.code ? "selected" : ""}>${esc(c.name)} (${c.code})</option>`).join("")}</select></label>
        <label><span>State / Province</span><input id="wState" value="${esc(prof.state || "")}"></label>
        <label><span>Tax / GST / VAT ID</span><input id="wTaxId" value="${esc(prof.taxId || "")}" placeholder="27AAAAA0000A1Z5"></label></div>
        <label><span>Registered legal entity name</span><input id="wLegal" value="${esc(prof.legalName || "")}" placeholder="Nova Mart Pvt Ltd"></label>
        <label><span>Registered address</span><input id="wReg" value="${esc(prof.registrationAddress || "")}"></label>
      </fieldset>
      <fieldset><legend>Taxation <span class="p-tag" id="wTaxHint"></span></legend>
        <div class="row"><label><span>Tax mode (blank = country default)</span><select id="wTaxMode"><option value="">— country default —</option>${taxModes.map(tm => `<option value="${tm.key}">${esc(tm.label)}</option>`).join("")}</select></label>
        <label><span>Tax rate 0-1 (blank = country default)</span><input id="wTaxRate" type="number" step="0.001" min="0" max="1"></label></div>
      </fieldset>
      <fieldset><legend>Product categories (industries this store sells)</legend>
        <p class="p-tag"><label style="display:inline"><input type="checkbox" id="wAllInd" checked> All industries (universal marketplace)</label></p>
        <div id="wIndGrid" class="ind-grid">${industries.map(i => `<label><input type="checkbox" data-ind="${i.key}"> ${i.icon} ${esc(i.name)}</label>`).join("")}</div>
      </fieldset>
      <fieldset><legend>Payment gateways <span class="p-tag" id="wGwHint"></span></legend>
        <div id="wGwGrid">${payProviders.map(p => `<label><input type="checkbox" data-gw="${p.id}" data-countries="${[...(availBy[p.id] || [])].join(" ")}"> ${p.emoji} ${esc(p.name)} <span class="p-tag">${p.feePct}%</span></label>`).join("")}</div>
      </fieldset>
      <div class="row"><label><span>Plan</span><select id="wPlan">${plans.plans.map(x => `<option value="${x.id}">${esc(x.name)} — ${x.price_month}/mo</option>`).join("")}</select></label>
      <label style="display:flex;gap:8px;align-items:center;align-self:end"><input type="checkbox" id="wSeed" checked> Seed demo catalog for selected industries</label></div>
      <button class="p-btn primary" id="wGo">${t ? "Save changes" : "Launch store"}</button>
    </div>`);
  const w = x => m.querySelector(x);
  function syncCountry() {
    cur = w("#wCountry").value;
    const c = countryOf(cur);
    w("#wTaxHint").textContent = "country default: " + c.tax_mode + " @ " + (c.tax_rate * 100).toFixed(1) + "%";
    const avail = payProviders.filter(p => (availBy[p.id] || new Set()).has(cur)).map(p => p.id);
    m.querySelectorAll("[data-gw]").forEach(cb => {
      const supported = cb.dataset.countries.split(" ").includes(cur);
      cb.closest("label").style.opacity = supported ? "1" : ".35";
      cb.disabled = !supported;
      if (!supported) cb.checked = false;
    });
    if (!t) avail.slice(0, 2).concat("cod").forEach(id => { const cb = m.querySelector('[data-gw="' + id + '"]'); if (cb && !cb.disabled) cb.checked = true; });
    w("#wGwHint").textContent = avail.length + " available in " + cur;
  }
  w("#wCountry").onchange = syncCountry;
  function syncAll() { const allOn = w("#wAllInd").checked; m.querySelectorAll("[data-ind]").forEach(c => { c.disabled = allOn; c.closest("label").style.opacity = allOn ? ".4" : "1"; }); }
  w("#wAllInd").onchange = syncAll; syncAll();
  if (t) { m.querySelectorAll("[data-gw]").forEach(cb => cb.checked = true); }
  syncCountry();
  w("#wGo").onclick = async () => {
    try {
      const inds = w("#wAllInd").checked ? [] : [...m.querySelectorAll("[data-ind]:checked")].map(c => c.dataset.ind);
      const pays = [...m.querySelectorAll("[data-gw]:checked")].map(c => c.dataset.gw);
      const payload = {
        name: w("#wName").value, slug: w("#wSlug").value, tagline: w("#wTag").value, mode: w("#wMode").value,
        owner: { name: w("#wOwnName").value, email: w("#wOwnEmail").value, password: w("#wOwnPass").value, phone: w("#wOwnPhone").value },
        jurisdiction: { country: cur, state: w("#wState").value, legalName: w("#wLegal").value, taxId: w("#wTaxId").value, registrationAddress: w("#wReg").value },
        tax: { mode: w("#wTaxMode").value || null, rate: w("#wTaxRate").value === "" ? null : Number(w("#wTaxRate").value) },
        industries: inds, gateways: pays.length ? pays : null, plan_id: Number(w("#wPlan").value), seedCatalog: w("#wSeed").checked
      };
      if (t && !payload.owner.password) delete payload.owner;
      if (t && !payload.owner.email) delete payload.owner;
      if (t) await api("/platform/tenants/" + t.id, "PUT", payload);
      else await api("/platform/tenants", "POST", payload);
      m.innerHTML = ""; toast(t ? "Store updated" : "Store launched"); render();
    } catch (e) { toast(e.message); }
  };
}
async function vAI() {
  const d = await api("/platform/ai");
  const cap = d.capabilities || [], prov = d.providers || [], plans = d.plans || [], tiers = d.tierByTenant || [];
  const usedBy = {}; (d.usage || []).forEach(u => usedBy[u.slug] = u);
  return `<div class="p-panel"><h2>🧠 AI · Providers, Capabilities & Plans</h2>
    <p style="color:var(--p-muted);font-size:13px">AI is a product on this platform: providers, capabilities, plans and pricing are all <b>editable data</b> (Provider Registry kind “ai”, Data Studio registries). Every store gets the <b>free built-in engine</b> automatically; premium models unlock only for <b>paid</b> stores (active paid plan or the AI Premium module).</p>
    <div class="p-grid"><div class="p-card"><h3>AI Providers (${prov.length})</h3><table class="p-table"><thead><tr><th></th><th>Provider</th><th>Cost / unit</th><th>Capabilities</th></tr></thead><tbody>
      ${prov.map(p => `<tr><td>${esc(p.emoji)}</td><td><b>${esc(p.name)}</b><br><code>${esc(p.id)}</code></td><td>${Number(p.feePct) === 0 && (!p.feeFixed) ? "<span class='badge published'>free</span>" : money(p.feeFixed || 0)}</td><td class="p-tag">${esc((p.methods || []).join(", "))}</td></tr>`).join("")}
    </tbody></table></div>
    <div class="p-card"><h3>Plans</h3>${plans.map(pl => `<div class="p-stat"><b>${esc(pl.name)}</b> · ${pl.price ? money(pl.price) + "/" + esc(pl.billing) : "free"}<div class="p-tag">${esc(pl.note)}</div></div>`).join("")}
    </div></div>
    <h3>Capabilities</h3><div class="p-grid">${cap.map(c => `<div class="p-card"><b>${esc(c.icon)} ${esc(c.name)}</b><div class="p-tag">${esc(c.unit)} · premium: ${(c.premiumProviders || []).join(", ") || "—"}</div><div style="font-size:12px">${esc(c.desc)}</div><div class="p-tag">free/day ${c.freeLimit.perDay} · premium/day ${c.premiumLimit.perDay}</div></div>`).join("")}</div>
    <h3>Store tiers & usage</h3><table class="p-table"><thead><tr><th>Store</th><th>AI tier</th><th>Why</th><th class="num">Calls</th><th class="num">Accrued</th></tr></thead><tbody>
      ${tiers.map(t => { const u = usedBy[t.slug] || {}; return `<tr><td>${esc(t.name)}</td><td><span class="badge ${t.premium ? "published" : "processing"}">${t.premium ? "premium" : "free"}</span></td><td class="p-tag">${t.hasPaidPlan ? "paid plan" : ""}${t.hasAiPro ? (t.hasPaidPlan ? " + " : "") + "AI Pro" : ""}${!t.premium ? "trial/free plan" : ""}</td><td class="num">${u.calls || 0}</td><td class="num">${money(u.cost || 0)}</td></tr>`; }).join("")}
    </tbody></table>
    <p class="p-tag">Manage providers in <b>🔌 Provider Registry</b> (add/enable “ai” kind). Editing capabilities/plans/limits = change the <code>aiCapabilities</code>/<code>aiPlans</code> registries in Data Studio — no code.</p></div>`;
}
async function vGlobalOffers() {
  const meta = await api("/meta"); const d = await api("/platform/offers");
  const opt = arr => (arr || []).map(x => `<option value="${esc(x.key || x)}">${esc(x.name || x)}</option>`).join("");
  const byFunder = d.stats && d.stats.byFunder || [];
  return `<div class="p-panel"><h2>🎁 Global Offers & Funder Settlements</h2>
    <p style="color:var(--p-muted);font-size:13px">Publish a platform-wide offer/coupon (scope = <b>global</b>) that every store inherits — bank cashbacks, brand vouchers, marketplace-wide sales. Funders are tracked so each redemption can be settled back to the paying bank/brand. Toggle whether stores honour global offers under <b>Provisioning</b>.</p>
    <div class="p-panel"><h3>New global offer</h3>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;align-items:end">
        <label><span>Name</span><input id="gName"></label>
        <label><span>Type</span><select id="gType">${opt(meta.offerTypes)}</select></label>
        <label><span>Value</span><input id="gValue" type="number" step="0.01" value="10"></label>
        <label><span>Code (optional)</span><input id="gCode"></label>
        <label><span>Channel</span><select id="gChan">${opt(meta.offerChannels)}</select></label>
        <label><span>Funder</span><select id="gFunder">${opt(meta.offerFunders)}</select></label>
        <label><span>Funder ref</span><input id="gFunderRef" placeholder="HDFC / Nike / GSTR"></label>
        <label><span>Usage limit</span><input id="gUse" type="number" value="0"></label>
      </div>
      <div style="margin-top:8px"><button class="p-btn primary sm" id="gSave">Publish global offer</button></div>
    </div>
    <h3>Live global offers</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>Name</th><th>Type</th><th>Channel</th><th>Funder</th><th class="num">Value</th><th class="num">Used/Limit</th><th>Status</th></tr></thead>
      <tbody>${(d.global || []).map(o => `<tr><td>${esc(o.name)}${o.code ? ` <code>${esc(o.code)}</code>` : ""}</td><td>${esc(o.type)}</td><td>${esc(o.channel)}</td><td>${esc(o.funder)}${o.funder_ref ? " " + esc(o.funder_ref) : ""}</td><td class="num">${esc(o.value)}</td><td class="num">${o.used}/${o.usage_limit || "∞"}</td><td><span class="badge ${o.status === "active" ? "published" : "draft"}">${esc(o.status)}</span></td></tr>`).join("") || '<tr><td colspan="7">No global offers.</td></tr>'}</tbody></table></div>
    <h3>Redemption split by funder</h3>${byFunder.length ? `<table class="p-table"><thead><tr><th>Funder</th><th class="num">Discount granted</th><th class="num">Redemptions</th></tr></thead><tbody>${byFunder.map(f => `<tr><td>${esc(f.funder)}</td><td class="num">${money(f.amount)}</td><td class="num">${f.redemptions}</td></tr>`).join("")}</tbody></table>` : '<p class="p-tag">No redemptions yet.</p>'}
    <h3>Recent redemptions (all stores)</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>Code</th><th class="num">Amount</th><th>Funder</th><th>Channel</th><th>Owner</th></tr></thead>
      <tbody>${(d.redemptions || []).slice(0, 15).map(r => `<tr><td><code>${esc(r.code)}</code></td><td class="num">${money(r.amount)}</td><td>${esc(r.funder)}${r.funder_ref ? " " + esc(r.funder_ref) : ""}</td><td>${esc(r.channel)}</td><td class="p-tag">${esc((r.owner || "").slice(0, 18))}</td></tr>`).join("") || '<tr><td colspan="5">—</td></tr>'}</tbody></table></div></div>`;
}
function wireGlobalOffers() {
  const g = document.getElementById("gSave"); if (!g) return;
  g.onclick = async () => { try { await api("/offers", "POST", { name: gval("gName"), type: gval("gType"), value: Number(gval("gValue")), code: gval("gCode"), channel: gval("gChan"), funder: gval("gFunder"), funder_ref: gval("gFunderRef"), usage_limit: Number(gval("gUse")) || 0, scope_level: "global", scope_type: "store" }); toast("Global offer published"); render(); } catch (e) { toast(e.message); } };
  function gval(id) { const el = document.getElementById(id); return el ? el.value : ""; }
}
async function vRuntime() {
  const d = await api("/platform/runtime"); const [eNv, fL] = await Promise.all([api("/platform/environments"), api("/platform/flags")]);
  const rt = d.runtime, cat = d.catalog, active = d.active;
  const concerns = Object.keys(cat.catalog);
  const envRows = (eNv.environments || []).map(e => `<tr><td><b>${esc(e.label)}</b>${e.active ? ' <span class="badge published">ACTIVE</span>' : ""}<br><code>${esc(e.name)}</code></td><td>${esc(e.region || "—")}</td><td class="p-tag">${e.tenants && e.tenants.length ? e.tenants.join(",") : "base"}</td><td>${(e.flags || []).length ? e.flags.map(f => `<code>${esc(f)}</code>`).join(" ") : "—"}</td><td class="p-tag">${Object.entries(e.runtime || {}).map(([k, v]) => `${k}:${v.driver}`).join(" ") || "defaults"}</td>
    <td style="text-align:right;white-space:nowrap"><button class="p-btn sm primary" data-envact="${esc(e.name)}">Activate</button> <button class="p-btn sm" data-envedit="${esc(e.name)}">Edit</button> <button class="p-btn sm danger" data-envdel="${esc(e.name)}">✕</button></td></tr>`).join("");
  const flagRows = Object.entries(fL.flags || {}).map(([k, f]) => `<tr><td><code>${esc(k)}</code></td><td>${esc(f.description || "")}</td><td><span class="badge ${f.default ? "published" : "draft"}">${f.default ? "on" : "off"}</span></td><td class="num">${f.rollout}%</td><td><button class="p-btn sm" data-flagedit="${esc(k)}" data-r="${f.rollout}" data-d="${f.default ? 1 : 0}">edit</button> <button class="p-btn sm danger" data-flagdel="${esc(k)}">✕</button></td></tr>`).join("");
  return `<div class="p-panel"><h2>🧩 Runtime · Infra</h2>
    <p style="color:var(--p-muted);font-size:13px;margin:0 0 12px">Every backend is a <b>config choice</b>. Define unlimited <b>named environments</b> (bundles of driver choices + secrets + feature flags), activate one to swap the whole topology, or set <code>LX_ENV=prod</code> at boot.</p>
    ${d.offline ? '<p class="badge processing" style="display:inline-block;padding:6px 10px;border-radius:8px;margin-bottom:8px">LX_OFFLINE=1 — outbound forced to simulated</p>' : ""}
    <h3>Environments</h3>
    ${envRows ? `<div class="p-scroll-x"><table class="p-table"><thead><tr><th>Environment</th><th>Region</th><th>Tenants</th><th>Flags</th><th>Runtime overlay</th><th></th></tr></thead><tbody>${envRows}</tbody></table></div>` : '<p class="p-tag">No environments yet — the base runtime below is active.</p>'}
    <div class="p-panel" style="margin-top:10px"><b>New environment</b>
      <div style="display:flex;gap:8px;align-items:end;flex-wrap:wrap;margin-top:6px">
        <label><span>Name</span><input id="envName" placeholder="prod-eu"></label>
        <label><span>Region</span><input id="envRegion" placeholder="eu-west-1"></label>
        <label><span>Tenant ids (CSV)</span><input id="envTenants" placeholder="1,4"></label>
        <button class="p-btn sm primary" id="envCreate">Create</button>
        <button class="p-btn sm" id="envExport">Export JSON</button>
        <label style="font-size:12px"><span>Import (JSON)</span><input type="file" id="envImportFile" accept="application/json" style="display:inline-block"></label>
      </div></div>
    <h3 style="margin-top:16px">Feature flags</h3>
    ${flagRows ? `<table class="p-table"><thead><tr><th>Flag</th><th>What</th><th>Default</th><th class="num">Rollout</th><th></th></tr></thead><tbody>${flagRows}</tbody></table>` : '<p class="p-tag">No flags.</p>'}
    <div style="display:flex;gap:8px;align-items:end;flex-wrap:wrap;margin-top:6px"><label><span>New flag</span><input id="flagName" placeholder="checkout.upsells"></label><label><span>Rollout %</span><input id="flagRollout" type="number" value="0" min="0" max="100"></label><label><span>Default on</span><input id="flagDefault" type="checkbox"></label><button class="p-btn sm primary" id="flagSave">Add</button></div>
    <h3 style="margin-top:16px">Base runtime (active now)</h3>
    <table class="p-table"><thead><tr><th>Concern</th><th>Default</th><th>Active</th><th>Driver</th><th>Connection</th></tr></thead><tbody>
      ${concerns.map(k => { const c = cat.catalog[k], cur = rt[k], kinds = c.drivers.map(dr => `<option ${dr === cur.driver ? "selected" : ""}>${dr}</option>`).join(""); const fields = cat.driverFields[cur.driver] || []; const params = cur.params || {}; const inp = fields.map(f => `<label style="display:block;font-size:11px"><span>${esc(f.label)}</span><input data-rtp="${k}.${f.key}" type="${f.secret ? "password" : "text"}" value="${esc(f.secret ? "••••" : (params[f.key] || ""))}" placeholder="${esc(f.key)}"></label>`).join("") || '<span class="p-tag">none</span>'; return `<tr><td><b>${esc(c.label)}</b><br><code>${k}</code></td><td><code>${c.default}</code></td><td><span class="p-tag">${esc(active[k] || cur.driver)}</span></td><td><select data-rt="${k}">${kinds}</select></td><td>${inp}</td></tr>`; }).join("")}
    </tbody></table>
    <div style="margin-top:12px"><button class="p-btn primary sm" id="rtSave">Apply base runtime</button> <button class="p-btn sm" id="rtTest">Test connections</button> <span id="rtTestOut" class="p-tag"></span></div></div>`;
}
function wireRuntime() {
  const $ = s => document.querySelector(s), $$ = s => Array.from(document.querySelectorAll(s));
  const baseBody = () => { const body = {}; $$("[data-rt]").forEach(sel => { body[sel.dataset.rt] = { driver: sel.value }; }); $$("[data-rtp]").forEach(inp => { const [k, field] = inp.dataset.rtp.split("."); body[k] = body[k] || {}; body[k].params = body[k].params || {}; if (inp.value && !inp.value.startsWith("••••")) body[k].params[field] = inp.value; }); return body; };
  const save = async () => { try { await api("/platform/runtime", "PUT", baseBody()); toast("Base runtime applied"); render(); } catch (e) { toast(e.message); } };
  if ($("#rtSave")) $("#rtSave").onclick = save;
  if ($("#rtTest")) $("#rtTest").onclick = async () => { const out = []; for (const c of ["cache", "ratelimit", "queue", "storage", "db"]) { try { const r = await api("/platform/runtime/test", "POST", { concern: c }); out.push(c + "=" + (r.ok ? "ok" : "FAIL") + (r.error ? ":" + r.error : "")); } catch (e) { out.push(c + "=err"); } } $("#rtTestOut").textContent = out.join(" · "); };
  if ($("#envCreate")) $("#envCreate").onclick = async () => { try { await api("/platform/environments?name=" + encodeURIComponent($("#envName").value), "POST", { name: $("#envName").value, label: $("#envName").value, region: $("#envRegion").value, tenants: $("#envTenants").value.split(",").map(x => Number(x)).filter(Boolean), runtime: baseBody() }); toast("Environment created"); render(); } catch (e) { toast(e.message); } };
  $$("[data-envact]").forEach(b => b.onclick = async () => { try { await api("/platform/environments/" + encodeURIComponent(b.dataset.envact) + "/activate", "POST", {}); toast("Environment activated"); render(); } catch (e) { toast(e.message); } });
  $$("[data-envdel]").forEach(b => b.onclick = async () => { if (!confirm("Delete environment?")) return; try { await api("/platform/environments/" + encodeURIComponent(b.dataset.envdel), "DELETE", {}); render(); } catch (e) { toast(e.message); } });
  $$("[data-envedit]").forEach(b => b.onclick = async () => { const e = (await api("/platform/environments/" + encodeURIComponent(b.dataset.envedit))).environment; $("#envName").value = e.name; $("#envRegion").value = e.region || ""; $("#envTenants").value = (e.tenants || []).join(","); /* load its overlay into selects */ for (const [k, cfg] of Object.entries(e.runtime || {})) { const sel = $(`[data-rt="${k}"]`); if (sel) sel.value = cfg.driver; } toast("Loaded " + e.name + " into the base form — Create to update"); });
  if ($("#envExport")) $("#envExport").onclick = async () => { const r = await api("/platform/environments-export"); const blob = new Blob([JSON.stringify(r.bundle, null, 1)], { type: "application/json" }); const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "luxora-environments.json"; a.click(); };
  if ($("#envImportFile")) $("#envImportFile").onchange = e => { const file = e.target.files[0]; if (!file) return; const fr = new FileReader(); fr.onload = async () => { try { const bundle = JSON.parse(fr.result); await api("/platform/environments-import", "POST", { bundle }); toast("Environments imported"); render(); } catch (err) { toast(err.message); } }; fr.readAsText(file); };
  if ($("#flagSave")) $("#flagSave").onclick = async () => { try { await api("/platform/flags/" + encodeURIComponent($("#flagName").value), "PUT", { name: $("#flagName").value, rollout: Number($("#flagRollout").value) || 0, default: $("#flagDefault").checked }); toast("Flag set"); render(); } catch (e) { toast(e.message); } };
  $$("[data-flagedit]").forEach(b => b.onclick = async () => { const r = Number(prompt("Rollout % (0-100)", b.dataset.r)); if (r == null) return; const d = confirm("Default ON?"); await api("/platform/flags/" + encodeURIComponent(b.dataset.flagedit), "PUT", { rollout: r, default: d }); render(); });
  $$("[data-flagdel]").forEach(b => b.onclick = async () => { await api("/platform/flags/" + encodeURIComponent(b.dataset.flagdel), "DELETE", {}); render(); });
}
async function render() {
  shell('<div class="p-empty">Loading…</div>');
  const body = $("#vBody");
  try {
    if (view === "dash") body.innerHTML = await vDash();
    else if (view === "provisioning") body.innerHTML = await vProvisioning();
    else if (view === "tenants") body.innerHTML = await vTenants();
    else if (view === "plans") body.innerHTML = await vPlans();
    else if (view === "subs") body.innerHTML = await vSubs();
    else if (view === "invoices") body.innerHTML = await vInvoices();
    else if (view === "modules") { body.innerHTML = await vModules(); await wireModules(); }
    else if (view === "providers") body.innerHTML = await vProviders();
    else if (view === "ai") body.innerHTML = await vAI();
    else if (view === "offers") { body.innerHTML = await vGlobalOffers(); wireGlobalOffers(); }
    else if (view === "runtime") { body.innerHTML = await vRuntime(); wireRuntime(); }
    else if (view === "geo") { body.innerHTML = await vGeo(); await wireGeoFx(); }
    else if (view === "monitor") body.innerHTML = await vMonitor();
    else if (view === "audit") body.innerHTML = await vAudit();
  } catch (e) { body.innerHTML = `<div class="p-empty">⚠️ ${esc(e.message)}</div>`; }
}
document.addEventListener("click", e => { if (e.target.closest("[data-mclose]")) { const mm = document.getElementById("modal"); if (mm) mm.innerHTML = ""; } }); /* __mclose */
(async function boot() {
  try {
    const me = await api("/platform/me");
    if (!me.admin) {
      $("#app").innerHTML = `<div class="p-login"><div class="p-login-box"><h1>LUXORA</h1><p>Platform Console</p>
        <form id="pf" class="p-form"><label><span>Email</span><input id="pe" type="email" required></label>
        <label><span>Password</span><input id="pp" type="password" required></label>
        <button class="p-btn primary" style="width:100%">Sign in</button></form>
        <p class="p-err hidden" id="pfErr" style="color:var(--p-red);font-size:13px;margin:10px 0 0"></p>
        <p class="hint" id="pfHint"></p>
        <p class="hint" id="pfStores">Store consoles: loading…</p></div></div>`;
      api("/stores").then(st => { const el = document.getElementById("pfStores"); if (el) el.innerHTML = "Store consoles: " + (st.stores || []).map(x => `<a href="/admin.html?store=${x.slug}">${x.name}</a>`).join(" · ") + " · <a href='/index.html'>Storefronts</a>"; }).catch(() => { });
      api("/platform/hint").then(h => { const el = document.getElementById("pfHint"); if (el && h.demo && h.email) el.innerHTML = "Owner sign-in: <code>" + esc(h.email) + "</code>" + (h.password ? " / <code>" + esc(h.password) + "</code>" : "") + " — set via env PLATFORM_EMAIL / PLATFORM_PASSWORD."; }).catch(() => { });
      $("#pf").onsubmit = async e => {
        e.preventDefault();
        try { await api("/platform/login", "POST", { email: $("#pe").value, password: $("#pp").value }); boot(); }
        catch (err) { const b = document.getElementById("pfErr"); if (b) { b.innerHTML = "⚠️ " + linkify(err.message); b.classList.remove("hidden"); } toast(err.message); }
      };
      return;
    }
    P.user = me.admin;
    render();
  } catch (e) { console.error(e); }
})();
