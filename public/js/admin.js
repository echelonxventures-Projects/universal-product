/* LUXORA Platform - Store Admin console (metadata-driven) */
"use strict";

const $ = s => document.querySelector(s);
const $$ = s => Array.from(document.querySelectorAll(s));
function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }
function __csrf() { const m = /(?:^|; )azc=([^;]+)/.exec(document.cookie || ""); return m ? m[1] : ""; }
async function api(path, methodOrOpts, body) {
  let method = "GET";
  let bodyData = undefined;
  if (typeof methodOrOpts === "object") {
    method = methodOrOpts.method || "GET";
    bodyData = methodOrOpts.body || methodOrOpts;
  } else {
    method = methodOrOpts;
    bodyData = body;
  }
  const opt = { method, headers: { "Content-Type": "application/json", "x-csrf": __csrf() }, credentials: "same-origin" };
  // For GET/HEAD, convert body to query params instead of sending as body
  if ((method === "GET" || method === "HEAD") && bodyData && typeof bodyData === "object") {
    const qs = Object.entries(bodyData).map(([k,v]) => `${k}=${encodeURIComponent(v)}`).join("&");
    if (qs) {
      path += path.includes("?") ? "&" + qs : "?" + qs;
      delete opt.body;
    }
  } else if (bodyData !== undefined) {
    opt.body = JSON.stringify(bodyData);
  }
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
/* The nav is grouped by function so an operator finds "Payment Gateways" under
   Payments, not lost in a 45-item alphabet soup. Keys are unchanged — NAVSEC and
   canSee() still key off the flat list, and NAVFLAT drives title lookup. */
const NAV = [
  { g: "Overview", items: [["dash", "◈ Dashboard"], ["analytics", "📊 Analytics"], ["monitor", "📈 Monitor"]] },
  { g: "Catalogue", items: [["products", "📦 Products"], ["brands", "🏷️ Brands"], ["gcatalog", "🌐 Global Catalog"], ["skus", "🔖 SKUs & Inventory"], ["taxonomy", "🌳 Taxonomy"], ["attributes", "🧬 Attributes"], ["search", "🔎 Search & Discovery"], ["content", "🖼️ Home Content"]] },
  { g: "Orders & Fulfilment", items: [["orders", "🧾 Orders"], ["returns", "↩️ Returns"], ["rfqs", "📋 RFQs (B2B)"], ["logistics", "🚚 Logistics & Fulfilment"], ["serialized", "🔢 Serialized Items"], ["planning", "📦 Planning & Replenishment"], ["suppliers", "🚚 Suppliers & Procurement"]] },
  { g: "Marketplace & B2B", items: [["sellers", "🏪 Sellers"], ["contracts", "📝 Contracts (B2B)"], ["tenders", "🏛️ Tenders"], ["marketplace", "📣 Marketplace & Ads"]] },
  { g: "Commerce Ops", items: [["qcops", "⚡ Quick-commerce"], ["finops", "💸 Fintech Ops"], ["mktops", "🏪 Marketplace Ops"], ["tradeops", "🤝 Trade Ops"]] },
  { g: "Mobility (E17)", items: [["rides", "🚗 Rides & Dispatch"], ["fleet", "🚙 Fleet & Drivers"]] },
  { g: "Operations (E18)", items: [["ops_hr", "🧑‍💼 People & Payroll"], ["ops_proc", "🛒 Procurement"], ["ops_mfg", "🏭 Manufacturing"], ["ops_proj", "📐 Projects & Approvals"]] },
  { g: "Payments & Finance", items: [["payments", "💳 Payment Gateways"], ["settlements", "🤝 Settlements"], ["finance", "💰 Finance & Settlements"], ["billing", "🧮 Billing"]] },
  { g: "Growth & Retention", items: [["promotions", "💸 Offers & Coupons"], ["ugc", "⭐ Reviews & Q&A"], ["helpdesk", "🎧 Support Helpdesk"], ["affiliate", "🤝 Influencers & Affiliates"], ["retention", "🔁 Subscriptions & Members"], ["experiments", "🧪 Experiments"], ["goip", "Ω∞ GOIP"]] },
  { g: "AI & Automation", items: [["ai", "🤖 AI Studio"], ["webhooks", "🔗 Webhooks"]] },
  { g: "Identity & Access", items: [["sso", "🔐 SSO & Integrations"], ["structure", "🏢 Org Structure"], ["team", "👥 Team & Roles"]] },
  { g: "Geo & Localization", items: [["localizations", "🌐 Localizations"], ["shipping", "📦 Shipping & Tracking"], ["sitemap", "🔍 Sitemap & SEO"]] },
  { g: "Compliance & Risk", items: [["compliance", "✅ Compliance & Certs"], ["risk", "🛡️ Risk & Fraud"], ["audit", "📜 Audit Trail"], ["trash", "🗑️ Trash & Retention"]] },
  { g: "Settings & Data", items: [["settings", "⚙️ Settings"], ["studio", "🛠️ Data Studio"], ["modules", "🧩 Modules"]] },
  { g: "Reference", items: [["manual", "📘 User Manual"], ["architecture", "🏛️ Architecture"]] }
];
const NAVFLAT = NAV.flatMap(g => g.items);
const NAVSEC = { promotions: "offers", goip: "offers", ai: "ai", webhooks: "webhooks", trash: "trash", team: "team", studio: "studio", sso: "settings", structure: "tenancy" };
/* THE TENANT IS WHAT IT IS — a section is not universal. This map is the fitness of the
   store sections that are VERTICAL FACTS about the tenant — no capability atom owns them,
   so the tenant's own deploy MODE and INDUSTRIES govern them instead (lib/authz.js reads
   this through the compiled canonical registry). Serial tracking belongs to tracked-goods
   verticals; replenishment planning belongs to physical stock. Everything else that looks
   like a console section is lit by the capability atom that governs it — the surface is a
   shadow of the composition, declared on the atom in the catalog, never duplicated here.
   A section absent here applies to every tenant; an entry narrows it. The console's own
   nav never reads this directly; written as strict JSON because the compiler parses it. */
const NAVFIT = {
  "serialized": { "industries": ["electronics", "automotive", "telecom", "industrial", "healthcare", "pharma", "defense", "marine", "jewellery", "luxury", "art"] },
  "planning": { "notIndustries": ["digital", "software", "services", "subscription", "media", "education", "finance", "realestate", "travel", "energy", "telecom", "gov", "defense", "mining"] }
};
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
async function vMarketplace() {
  const [ads, m, rank] = await Promise.all([api("/marketplace/ads", {}), api("/admin/marketplace/metrics", {}), api("/marketplace/rank", { surface: "search", slots: 3 })]);
  const byM = {}; (ads.ads || []).forEach(a => byM[a.bid_model] = (byM[a.bid_model] || 0) + 1);
  return `<div class="a-head"><h2>📣 Marketplace &amp; Ads</h2><p class="a-sub">Ad inventory · GSP bidding · impression/click ledger · last-click attribution · seller KPIs · take-rate settlement. Bid models / attribution models / surfaces in Data Studio: <code>mktBidModels</code>, <code>mktAttribution</code>, <code>mktSurfaces</code>.</p></div>
  <div class="a-card"><h3>Ad inventory</h3>
    <p class="a-sub">${Object.entries(byM).map(([k, v]) => `<span class="a-chip">${esc(k)}·${v}</span>`).join("") || "no active ads"}</p>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>name</th><th>seller</th><th>model</th><th>bid</th><th>spent</th><th>status</th></tr></thead>
      <tbody>${(ads.ads || []).slice(0, 15).map(a => `<tr><td>${esc(a.name)}</td><td>${a.seller_id || "—"}</td><td><span class="a-chip">${esc(a.bid_model)}</span></td><td>${money(a.bid_amount)}</td><td>${money(a.spent)}</td><td><span class="a-chip">${esc(a.status)}</span></td></tr>`).join("") || '<tr><td colspan="6">No ads yet.</td></tr>'}</tbody></table></div>
  </div>
  <div class="a-card"><h3>Ad auction · surface <code>search</code> (top 3, GSP)</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>position</th><th>ad</th><th>seller</th><th>charge</th></tr></thead>
      <tbody>${(rank.ranked || []).map(r => `<tr><td>${r.position}</td><td>${esc(r.name)} <code>${r.ad}</code></td><td>${r.seller || "—"}</td><td>${money(r.charge)}</td></tr>`).join("") || '<tr><td colspan="4">No active bids.</td></tr>'}</tbody></table></div>
  </div>
  <div class="a-card"><h3>Seller KPIs</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>seller</th><th>orders</th><th>revenue</th><th>take rate</th><th>commission</th><th>ad spend</th><th>ad ROI</th></tr></thead>
      <tbody>${(m.sellers || []).map(x => `<tr><td>${esc(x.seller_id)}</td><td>${x.orders}</td><td>${money(x.revenue)}</td><td>${(x.take_rate*100).toFixed(0)}%</td><td>${money(x.commission)}</td><td>${money(x.ads_spend)}</td><td>${x.ad_roi}</td></tr>`).join("") || '<tr><td colspan="7">No seller data yet.</td></tr>'}</tbody></table></div>
  </div>`;
}
async function vUgc() {
  const [q, revs] = await Promise.all([api("/admin/ugc/queue", {}), api("/admin/reviews", {})]);
  const allR = revs.reviews || [];
  const byS = {}; allR.forEach(r => byS[r.state] = (byS[r.state] || 0) + 1);
  return `<div class="a-head"><h2>⭐ Reviews &amp; Q&amp;A</h2><p class="a-sub">Rich reviews (helpfulness votes, seller reply threads, media, moderation states) and product Q&amp;A. States &amp; roles are Data Studio registries: <code>ugcStates</code>, <code>ugcRoles</code>; behaviour toggles live in Settings → UGC.</p></div>
  <div class="a-card"><h3>Moderation queue · ${q.pending || 0} pending</h3>
    <p class="a-sub">${Object.entries(byS).map(([k, v]) => `<span class="a-chip">${esc(k)}·${v}</span>`).join("") || "no reviews"}</p>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>type</th><th>product</th><th>author</th><th>text</th><th>state</th></tr></thead>
      <tbody>${[
        ...q.reviews.map(r => ({ k: "review", p: r.product_id, a: r.name, t: (r.title + " — " + r.body).slice(0, 90), s: r.state, id: r.id })),
        ...q.questions.map(r => ({ k: "question", p: r.product_id, a: r.name, t: r.body.slice(0, 90), s: r.state, id: r.id })),
        ...q.answers.map(r => ({ k: "answer", p: r.product_id, a: r.name, t: r.body.slice(0, 90), s: r.state, id: r.id }))
      ].slice(0, 20).map(x => `<tr><td><span class="a-chip">${esc(x.k)}</span></td><td><code>${esc(x.p)}</code></td><td>${esc(x.a)}</td><td>${esc(x.t)}</td><td><span class="a-chip">${esc(x.s)}</span></td></tr>`).join("") || '<tr><td colspan="5">Queue is empty — everything published.</td></tr>'}</tbody></table></div>
  </div>
  <div class="a-card"><h3>Latest reviews</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>product</th><th>author</th><th>rating</th><th>helpful</th><th>state</th></tr></thead>
      <tbody>${allR.slice(0, 15).map(r => `<tr><td><code>${esc(r.product_id)}</code></td><td>${esc(r.name)}</td><td>${r.rating}★</td><td>${r.votes_helpful || 0}/${r.votes_total || 0}</td><td><span class="a-chip">${esc(r.state)}</span></td></tr>`).join("") || '<tr><td colspan="5">No reviews yet.</td></tr>'}</tbody></table></div>
  </div>`;
}
async function vHelpdesk() {
  const [list, sla] = await Promise.all([api("/admin/helpdesk/tickets", {}), api("/admin/helpdesk/sla", {})]);
  const tk = list.tickets || [];
  const byS = {}; tk.forEach(t => byS[t.status] = (byS[t.status] || 0) + 1);
  const breaches = (sla.health || []).filter(h => h.breach);
  return `<div class="a-head"><h2>🎧 Support Helpdesk</h2><p class="a-sub">Customer cases · agent assignment · SLA timers (first response + resolution per priority) · public replies vs internal notes · CSAT on close. Statuses / priorities / reasons in Data Studio: <code>hdStatuses</code>, <code>hdPriorities</code>, <code>hdReasons</code>.</p></div>
  <div class="a-card"><h3>Queue · ${tk.length} cases${breaches.length ? ` · <span class="a-chip">⚠ ${breaches.length} SLA breach</span>` : ""}</h3>
    <p class="a-sub">${Object.entries(byS).map(([k, v]) => `<span class="a-chip">${esc(k)}·${v}</span>`).join("") || "no cases"}</p>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>ref</th><th>subject</th><th>customer</th><th>priority</th><th>status</th><th>assignee</th><th>csat</th></tr></thead>
      <tbody>${tk.slice(0, 25).map(t => `<tr><td><code>${esc(t.ref)}</code></td><td>${esc(t.subject.slice(0, 48))}</td><td>${esc(t.owner_name)}</td><td><span class="a-chip">${esc(t.priority)}</span></td><td><span class="a-chip">${esc(t.status)}</span></td><td>${esc(t.assignee || "unassigned")}</td><td>${t.csat ? t.csat + "★" : "—"}</td></tr>`).join("") || '<tr><td colspan="7">No cases yet.</td></tr>'}</tbody></table></div>
  </div>
  <div class="a-card"><h3>SLA health</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>ref</th><th>priority</th><th>status</th><th>breach</th></tr></thead>
      <tbody>${(sla.health || []).slice(0, 15).map(h => `<tr><td><code>${esc(h.ref)}</code></td><td>${esc(h.priority)}</td><td>${esc(h.status)}</td><td>${h.breach ? `<span class="a-chip">⚠ ${esc(h.breach)}</span>` : "on schedule"}</td></tr>`).join("") || '<tr><td colspan="4">No open cases.</td></tr>'}</tbody></table></div>
  </div>
  <div class="a-card"><h3>Agent performance</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>agent</th><th>cases</th><th>responded</th><th>avg CSAT</th></tr></thead>
      <tbody>${(sla.agents || []).map(a => `<tr><td>${esc(a.assignee)}</td><td>${a.tickets}</td><td>${a.responded}</td><td>${a.csat ? a.csat + " / 5" : "—"}</td></tr>`).join("") || '<tr><td colspan="4">No agent activity.</td></tr>'}</tbody></table></div>
  </div>`;
}
/* ---------- Commerce Ops — the parity layer, surfaced. Each view reads this
   store's own capability composition first: a domain whose capabilities are all
   off shows one line ("switch it on in Capabilities") instead of empty tables,
   because an inert engine has no records to show. No vendor name appears — the
   domain declares what it does, never whose it is. ---------- */
let coCap = null;
async function coCaps() {
  if (!coCap) coCap = (await api("/capabilities")).catalog;
  return coCap;
}
/* the gate a domain's view reads: the atoms that govern THIS section, derived from the
   capability catalog the platform serves (each atom declares the sections it lights).
   The nav's visibility derives from the same declaration through lib/authz.js, so a leaf
   and the view behind it can never disagree about whether the domain is on. */
async function coGate(section) {
  const all = await coCaps();
  const keys = all.filter(c => (c.sections || []).includes(section)).map(c => c.key);
  const have = k => { const c = all.find(x => x.key === k); return !!(c && c.on); };
  const on = keys.filter(have);
  return { on, off: keys.filter(k => !have(k)), any: on.length > 0 };
}
function coOff(dom, label, off) {
  return `<div class="p-panel"><div class="a-head"><h2>${esc(label)}</h2>
    <p class="a-sub">This store has not switched on the ${esc(dom)} capabilities — the engines are inert and hold no records. <button class="p-btn sm" data-act="co-cap">Open ⚙️ Capabilities</button> to compose one.</p></div></div>`;
}
function coBadge(v) { return v == null || v === "" ? '<span class="p-tag">—</span>' : `<span class="a-chip">${esc(v)}</span>`; }
function coChips(rows, f) { const by = {}; rows.forEach(r => { const k = f(r); by[k] = (by[k] || 0) + 1; }); return Object.entries(by).map(([k, v]) => `<span class="a-chip">${esc(k)}·${v}</span>`).join(" ") || "none"; }
function coTbl(head, rows, cols, empty) {
  return `<div class="a-tablewrap"><table class="a-table"><thead><tr>${head.map(h => `<th>${h}</th>`).join("")}</tr></thead>
    <tbody>${rows.slice(0, 25).map(r => `<tr>${cols(r).map(c => `<td>${c}</td>`).join("")}</tr>`).join("") || `<tr><td colspan="${head.length}">${empty}</td></tr>`}</tbody></table></div>`;
}

/* ---------- Quick-commerce: dark stores, slots, serviceability, dispatch ---------- */
async function vQcOps() {
  const gate = await coGate("qcops");
  if (!gate.any) return coOff("quick-commerce", "⚡ Quick-commerce", gate.off);
  const d = await api("/qc/stores", {});
  const stores = d.stores || [], riders = d.riders || [];
  const runs = (await api("/qc/runs", {})).runs || [];
  const slots = await Promise.all((stores.slice(0, 4)).map(s => api("/qc/slots", { store: s.id, day: 0 }).then(x => x.slots || []).catch(() => [])));
  const flat = slots.flatMap((sl, i) => sl.map(x => ({ ...x, store: stores[i] && stores[i].name })));
  return `<div class="a-head"><h2>⚡ Quick-commerce Ops</h2>
    <p class="a-sub">Dark stores, delivery slots, per-store inventory pinning, riders and dispatch runs closed with a proof-of-delivery OTP. The promise a store advertises is its own minutes plus prep time, resolved per pincode. Kinds, statuses and vehicles are Data Studio registries: <code>qcStoreKinds</code>, <code>qcSlotStatuses</code>, <code>qcVehicles</code>.</p>
    <p class="a-sub"><b>On for this store:</b> ${gate.on.map(k => `<span class="a-chip">${esc(k)}</span>`).join(" ")}${gate.off.length ? ` <span class="p-tag">off: ${esc(gate.off.join(", "))}</span>` : ""}</p></div>
  <div class="a-card"><h3>Dark stores · ${stores.length}</h3>
    <p class="a-sub">${coChips(stores, s => s.kind || "dark_store")}</p>
    ${coTbl(["store", "code", "kind", "city", "pincode", "radius", "promise", "min order", "fee", "status"],
      stores, s => [esc(s.name), `<code>${esc(s.code)}</code>`, esc(s.kind), esc(s.city), esc(s.pincode), (s.service_radius_km || 0) + " km", (s.promise_minutes || 0) + " min", money(s.min_order), money(s.delivery_fee), coBadge(s.status)])}
    <button class="p-btn sm primary" data-act="co-new" data-key="dark_store">+ New dark store</button>
    <button class="p-btn sm" data-act="co-new" data-key="rider">+ New rider</button></div>
  <div class="a-card"><h3>Today's delivery slots</h3>
    ${coTbl(["window", "store", "capacity", "booked", "fee", "status"], flat,
      s => [`${esc(s.window_start)}–${esc(s.window_end)}`, esc(s.store || "—"), s.capacity, s.booked, s.fee ? money(s.fee) : "—", coBadge(s.status)],
      "No open slots today — create one from the dark store.")}</div>
  <div class="a-card"><h3>Riders · ${riders.length}</h3>
    ${coTbl(["rider", "phone", "vehicle", "city", "status", "rating", "deliveries"], riders,
      r => [esc(r.name), esc(r.phone || "—"), esc(r.vehicle || "—"), esc(r.city || "—"), coBadge(r.status), r.rating || "—", r.deliveries || 0])}</div>
  <div class="a-card"><h3>Dispatch runs · ${runs.length}</h3>
    <p class="a-sub">${coChips(runs, r => r.status)}</p>
    ${coTbl(["run", "store", "rider", "batch", "orders", "PoD OTP", "status"], runs,
      r => [`<code>${esc(r.ref)}</code>`, esc(String(r.store_id || "—")), esc(String(r.rider_id || "—")), r.batch_count || 0, (r.order_ids || []).length, `<code>${esc(r.pod_otp || "—")}</code>`, coBadge(r.status)])}
    <div style="display:flex;gap:8px;margin-top:8px;flex-wrap:wrap"><label><span>Store</span><select id="qcRunStore">${stores.map(s => `<option value="${s.id}">${esc(s.name)}</option>`).join("")}</select></label>
      <label><span>Rider</span><select id="qcRunRider">${riders.map(r => `<option value="${r.id}">${esc(r.name)}</option>`).join("")}</select></label>
      <label><span>Order ids (CSV)</span><input id="qcRunOrders" placeholder="101,102"></label>
      <button class="p-btn sm primary" id="qcRunGo">Create run</button></div></div>`;
}
function wireQcOps() {
  const g = $("#qcRunGo"); if (g) g.onclick = async () => {
    try {
      const orders = String($("#qcRunOrders").value || "").split(",").map(x => Number(x.trim())).filter(Boolean);
      const r = await api("/qc/runs", "POST", { store_id: Number($("#qcRunStore").value), rider_id: Number($("#qcRunRider").value), order_ids: orders, batch_count: orders.length });
      toast("Dispatch run " + (r.run && r.run.ref)); render();
    } catch (e) { toast(e.message); }
  };
}

/* ---------- Fintech Ops: UPI, QR, links, mandates, escrow, KYC, credit, payouts ---------- */
async function vFinOps() {
  const gate = await coGate("finops");
  if (!gate.any) return coOff("fintech", "💸 Fintech Ops", gate.off);
  const upi = (await api("/fintech/upi", {})).upi || [];
  const billers = (await api("/fintech/billers", {})).billers || [];
  const plans = (await api("/fintech/plans", {})).plans || [];
  const [escrowR, kycR, payoutR, loanR, polR, vchR] = await Promise.all([
    api("/meta/entity/escrow_hold", {}).catch(() => ({ rows: [] })),
    api("/meta/entity/kyc_profile", {}).catch(() => ({ rows: [] })),
    api("/meta/entity/bank_payout", {}).catch(() => ({ rows: [] })),
    api("/meta/entity/loan", {}).catch(() => ({ rows: [] })),
    api("/meta/entity/payment_link", {}).catch(() => ({ rows: [] })),
    api("/meta/entity/gift_voucher", {}).catch(() => ({ rows: [] })),
  ]);
  const escrows = escrowR.rows || [], kycs = kycR.rows || [], payouts = payoutR.rows || [],
    loans = loanR.rows || [], pols = polR.rows || [], vchs = vchR.rows || [];
  return `<div class="a-head"><h2>💸 Fintech Ops</h2>
    <p class="a-sub">The payment rails: UPI collect, QR scan-pay, tokenised links, auto-debit mandates, escrow hold/release, split settlements, KYC-gated credit (BNPL, loans), bank payouts, bills, recharge, P2P, insurance and gift vouchers. Money never leaves the single wallet ledger. Statuses, kinds and frequencies are registries: <code>finUpiStatuses</code>, <code>finLinkStatuses</code>, <code>finEscrowStatuses</code>.</p>
    <p class="a-sub"><b>On for this store:</b> ${gate.on.map(k => `<span class="a-chip">${esc(k)}</span>`).join(" ")}${gate.off.length ? ` <span class="p-tag">${esc(gate.off.length)} off</span>` : ""}</p></div>
  <div class="a-card"><h3>Escrow holds · ${escrows.length}</h3>
    <p class="a-sub">${coChips(escrows, e => e.status)}</p>
    ${coTbl(["escrow", "order", "buyer", "seller", "held", "status"], escrows,
      e => [`<code>${esc(e.ref)}</code>`, e.order_id || "—", esc(e.buyer), esc(e.seller), money(e.amount), coBadge(e.status)])}
    ${gate.on.includes("escrow") ? `<div style="display:flex;gap:8px;margin-top:8px;flex-wrap:wrap"><label><span>Order id</span><input id="finEscOrder" placeholder="101"></label>
      <label><span>Seller</span><input id="finEscSeller" placeholder="s:acme"></label><label><span>Amount</span><input id="finEscAmt" type="number" step="0.01" placeholder="50.00"></label>
      <button class="p-btn sm primary" id="finEscGo">Hold in escrow</button></div>` : ""}</div>
  <div class="a-card"><h3>KYC profiles · ${kycs.length}</h3>
    <p class="a-sub">${coChips(kycs, k => k.status)}</p>
    ${coTbl(["owner", "kind", "name", "company", "docs", "status"], kycs,
      k => [esc(k.owner), esc(k.kind), esc(k.full_name || "—"), esc(k.company || "—"), esc(k.doc_status || "—"), coBadge(k.status)])}
    ${gate.on.includes("kyc") ? `<button class="p-btn sm primary" data-act="co-new" data-key="kyc_profile">+ Submit KYC</button>` : ""}</div>
  <div class="a-cap" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px">
    <div class="a-card"><h3>Payment links · ${pols.length}</h3>
      ${coTbl(["link", "title", "amount", "status"], pols, p => [`<code>${esc(p.ref)}</code>`, esc(p.title), money(p.amount), coBadge(p.status)], "No links issued.")}</div>
    <div class="a-card"><h3>Bank payouts · ${payouts.length}</h3>
      ${coTbl(["payout", "payee", "amount", "status"], payouts, p => [`<code>${esc(p.ref)}</code>`, esc(p.payee), money(p.amount), coBadge(p.status)], "No payouts queued.")}
      ${gate.on.includes("bank_payouts") ? `<button class="p-btn sm primary" data-act="co-new" data-key="bank_payout">+ Queue payout</button>` : ""}</div>
    <div class="a-card"><h3>Loans · ${loans.length}</h3>
      ${coTbl(["loan", "owner", "principal", "emi", "status"], loans, l => [`<code>${esc(l.ref)}</code>`, esc(l.owner), money(l.principal), l.emi ? money(l.emi) : "—", coBadge(l.status)], "No credit issued.")}</div>
    <div class="a-card"><h3>Gift vouchers · ${vchs.length}</h3>
      ${coTbl(["code", "amount", "buyer", "status"], vchs, v => [`<code>${esc(v.code)}</code>`, money(v.amount), esc(v.buyer || "—"), coBadge(v.status)], "No vouchers issued.")}</div>
  </div>
  <div class="a-card"><h3>UPI handles · ${upi.length}</h3>
    ${coTbl(["owner", "vpa", "verified", "default", "status"], upi,
      u => [esc(u.owner), `<code>${esc(u.vpa)}</code>`, u.verified ? "✓" : "—", u.is_default ? "✓" : "—", coBadge(u.status)], "No VPA saved.")}</div>
  <div class="a-card"><h3>Billers · ${billers.length} · recharge plans · ${plans.length}</h3>
    <p class="a-sub">${(billers.slice(0, 12)).map(b => `<span class="a-chip">${esc(b.category)}·${esc(b.name)}</span>`).join(" ") || "no billers registered"}</p>
    <p class="a-sub">${plans.slice(0, 12).map(p => `<span class="a-chip">${esc(p.operator)}·${money(p.amount)}/${esc(p.validity || "")}</span>`).join(" ") || "no plans registered"}</p></div>`;
}
function wireFinOps() {
  const g = $("#finEscGo"); if (g) g.onclick = async () => {
    try {
      const r = await api("/fintech/escrow", "POST", { order_id: Number($("#finEscOrder").value), seller: $("#finEscSeller").value, amount: Number($("#finEscAmt").value) });
      toast("Escrow " + (r.escrow && r.escrow.ref)); render();
    } catch (e) { toast(e.message); }
  };
}

/* ---------- Marketplace Ops: onboarding, buy-box, FBA, health, claims ---------- */
async function vMktOps() {
  const gate = await coGate("mktops");
  if (!gate.any) return coOff("marketplace", "🏪 Marketplace Ops", gate.off);
  const [onb, perf, claim, fba, smart] = await Promise.all([
    api("/meta/entity/seller_onboarding", {}).catch(() => ({ rows: [] })),
    api("/meta/entity/seller_performance", {}).catch(() => ({ rows: [] })),
    api("/meta/entity/buyer_claim", {}).catch(() => ({ rows: [] })),
    api("/meta/entity/fba_inbound", {}).catch(() => ({ rows: [] })),
    api("/meta/entity/smart_fulfilment", {}).catch(() => ({ rows: [] })),
  ]);
  const onbs = onb.rows || [], perfs = perf.rows || [], claims = claim.rows || [],
    fbas = fba.rows || [], smarts = smart.rows || [];
  const prod = $("#f_product") ? $("#f_product").value : "";
  const bb = prod ? await api("/marketplace/offers/" + encodeURIComponent(prod), {}).catch(() => ({ offers: [], buybox: null })) : { offers: [], buybox: null };
  return `<div class="a-head"><h2>🏪 Marketplace Ops</h2>
    <p class="a-sub">Seller onboarding and review, multi-seller offers competing for one product's featured offer, fulfilment-centre inbound, account health that decides tier and suspension, buyer-protection claims and smart-fulfilment grading. The buy-box winner is the best composite of price, fulfilment speed and seller trust — each weight tunable in ⚙️ Capabilities.</p>
    <p class="a-sub"><b>On for this store:</b> ${gate.on.map(k => `<span class="a-chip">${esc(k)}</span>`).join(" ")}</p></div>
  <div class="a-card"><h3>Seller onboarding · ${onbs.length}</h3>
    <p class="a-sub">${coChips(onbs, o => o.status)}</p>
    ${coTbl(["business", "type", "gstin", "status", "review"], onbs,
      o => [esc(o.business_name), esc(o.business_type || "—"), `<code>${esc(o.gstin || "—")}</code>`, coBadge(o.status),
        o.status === "submitted" ? `<button class="p-btn sm primary" data-mktapp="${o.id}" data-v="approved">Approve</button> <button class="p-btn sm danger" data-mktapp="${o.id}" data-v="rejected">Reject</button>` : esc(o.reviewed_by || "—")])}
    <button class="p-btn sm primary" data-act="co-new" data-key="seller_onboarding">+ Apply as seller</button></div>
  <div class="a-card"><h3>Buy-box · product offers</h3>
    <div style="display:flex;gap:8px;margin-bottom:8px;flex-wrap:wrap"><label><span>Product id</span><input id="mktProd" placeholder="VR-ELEC-01" value="${esc(prod)}"></label>
      <button class="p-btn sm" id="mktLoad">Load offers</button>
      <button class="p-btn sm primary" id="mktBb">Recompute buy-box</button></div>
    ${coTbl(["seller", "price", "condition", "fulfilment", "score", "winner"], bb.offers || [],
      o => [esc(String(o.seller_id)), money(o.price), esc(o.condition || "new"), esc(o.fulfillment || "fbm"), (o.buybox_score || 0).toFixed(2), o.buybox ? '<span class="a-chip">★ featured</span>' : ""])}</div>
  <div class="a-cap" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px">
    <div class="a-card"><h3>Account health · ${perfs.length}</h3>
      ${coTbl(["seller", "period", "ODR", "late", "cancel", "score", "tier"], perfs,
        p => [esc(String(p.seller_id)), esc(p.period), (p.odr || 0).toFixed(2) + "%", (p.late_ship_rate || 0).toFixed(1) + "%", (p.cancel_rate || 0).toFixed(1) + "%", (p.health_score || 0).toFixed(0), coBadge(p.tier)], "No health computed.")}
      <button class="p-btn sm" data-act="co-mktperf">Recompute health</button></div>
    <div class="a-card"><h3>FBA inbound · ${fbas.length}</h3>
      ${coTbl(["ref", "units", "status"], fbas, f => [`<code>${esc(f.ref)}</code>`, f.units, coBadge(f.status)], "No inbound shipments.")}</div>
    <div class="a-card"><h3>Claims (A-to-z) · ${claims.length}</h3>
      ${coTbl(["ref", "order", "kind", "amount", "status"], claims,
        c => [`<code>${esc(c.ref)}</code>`, c.order_id || "—", esc(c.kind), c.amount ? money(c.amount) : "—", coBadge(c.status)], "No claims open.")}</div>
    <div class="a-card"><h3>Smart fulfilment · ${smarts.length}</h3>
      ${coTbl(["ref", "grade", "SLA", "status"], smarts, s => [`<code>${esc(s.ref)}</code>`, coBadge(s.grade), (s.sla_hours || 0) + " h", coBadge(s.status)], "Not enrolled.")}</div>
  </div>`;
}
function wireMktOps() {
  const load = $("#mktLoad"); if (load) load.onclick = () => render();
  const bb = $("#mktBb"); if (bb) bb.onclick = async () => {
    const p = $("#mktProd").value.trim(); if (!p) return toast("Enter a product id");
    try { const r = await api("/marketplace/buybox/" + encodeURIComponent(p), "POST", {}); toast("Buy-box recomputed · winner " + (r.winner ? r.winner.seller_id : "none")); render(); }
    catch (e) { toast(e.message); }
  };
  $$("[data-mktapp]").forEach(b => b.onclick = async () => {
    try { await api("/marketplace/onboarding/" + b.dataset.mktapp + "/review", "POST", { decision: b.dataset.v }); toast("Onboarding " + b.dataset.v); render(); }
    catch (e) { toast(e.message); }
  });
}

/* ---------- Trade Ops: assurance, gold suppliers, verification, LCs, RFQs ---------- */
async function vTradeOps() {
  const gate = await coGate("tradeops");
  if (!gate.any) return coOff("B2B trade", "🤝 Trade Ops", gate.off);
  const [ta, gold, ver, lc, quo, pl, doc] = await Promise.all([
    api("/meta/entity/trade_assurance", {}).catch(() => ({ rows: [] })),
    api("/meta/entity/gold_supplier", {}).catch(() => ({ rows: [] })),
    api("/meta/entity/company_verification", {}).catch(() => ({ rows: [] })),
    api("/meta/entity/letter_of_credit", {}).catch(() => ({ rows: [] })),
    api("/meta/entity/rfq_quote", {}).catch(() => ({ rows: [] })),
    api("/meta/entity/price_list", {}).catch(() => ({ rows: [] })),
    api("/meta/entity/export_document", {}).catch(() => ({ rows: [] })),
  ]);
  const tas = ta.rows || [], golds = gold.rows || [], vers = ver.rows || [], lcs = lc.rows || [],
    quos = quo.rows || [], pls = pl.rows || [], docs = doc.rows || [];
  return `<div class="a-head"><h2>🤝 Trade Ops</h2>
    <p class="a-sub">B2B trust and trade: order-level escrow with milestones, paid supplier memberships, company-verification audits, export/customs documents generated from an order's own fields, letters of credit, multi-seller RFQ bidding ranked by price then lead time, sealed-bid tender reverse auctions and per-segment price lists with MOQ enforcement.</p>
    <p class="a-sub"><b>On for this store:</b> ${gate.on.map(k => `<span class="a-chip">${esc(k)}</span>`).join(" ")}${gate.off.length ? ` <span class="p-tag">${esc(gate.off.length)} off</span>` : ""}</p></div>
  <div class="a-card"><h3>Trade assurance · ${tas.length}</h3>
    <p class="a-sub">${coChips(tas, t => t.status)}</p>
    ${coTbl(["ref", "order", "buyer", "seller", "amount", "milestone", "status"], tas,
      t => [`<code>${esc(t.ref)}</code>`, t.order_id || "—", esc(t.buyer), esc(t.seller), money(t.amount), esc(t.current_milestone || "—"), coBadge(t.status)])}
    ${gate.on.includes("trade_assurance") ? `<div style="display:flex;gap:8px;margin-top:8px;flex-wrap:wrap"><label><span>Order id</span><input id="trAsOrder" placeholder="101"></label>
      <label><span>Seller</span><input id="trAsSeller" placeholder="s:acme"></label><label><span>Amount</span><input id="trAsAmt" type="number" step="0.01" placeholder="500.00"></label>
      <button class="p-btn sm primary" id="trAsGo">Create assurance</button></div>` : ""}</div>
  <div class="a-cap" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px">
    <div class="a-card"><h3>Gold suppliers · ${golds.length}</h3>
      ${coTbl(["supplier", "tier", "verified", "status"], golds, g => [esc(String(g.supplier_id)), coBadge(g.tier), g.verified ? "✓" : "—", coBadge(g.status)], "No memberships.")}
      ${gate.on.includes("gold_supplier") ? `<button class="p-btn sm primary" data-act="co-new" data-key="gold_supplier">+ Enrol supplier</button>` : ""}</div>
    <div class="a-card"><h3>Company verification · ${vers.length}</h3>
      ${coTbl(["company", "country", "audit", "status"], vers, v => [esc(v.company_name), esc(v.country || "—"), esc(v.audit_by || "—"), coBadge(v.verification_status)], "No audits filed.")}
      ${gate.on.includes("company_verification") ? `<button class="p-btn sm primary" data-act="co-new" data-key="company_verification">+ Submit audit</button>` : ""}</div>
    <div class="a-card"><h3>Letters of credit · ${lcs.length}</h3>
      ${coTbl(["ref", "buyer", "seller", "amount", "status"], lcs, l => [`<code>${esc(l.lc_number || l.ref)}</code>`, esc(l.buyer), esc(l.seller), money(l.amount), coBadge(l.status)], "No LCs issued.")}</div>
    <div class="a-card"><h3>RFQ quotes · ${quos.length}</h3>
      ${coTbl(["rfq", "supplier", "unit price", "MOQ", "lead", "rank", "status"], quos,
        q => [esc(String(q.rfq_id)), esc(String(q.supplier_id)), money(q.unit_price), q.moq || "—", q.lead_days || "—", q.rank || "—", coBadge(q.status)], "No quotes yet.")}</div>
    <div class="a-card"><h3>Price lists · ${pls.length}</h3>
      ${coTbl(["name", "segment", "status"], pls, p => [esc(p.name), esc(p.segment || "—"), coBadge(p.status)], "No price lists.")}</div>
    <div class="a-card"><h3>Export documents · ${docs.length}</h3>
      ${coTbl(["ref", "kind", "dest", "value", "status"], docs,
        d => [`<code>${esc(d.ref)}</code>`, esc(d.doc_kind), esc(d.dest_country || "—"), d.total_value ? money(d.total_value) : "—", coBadge(d.status)], "No documents generated.")}</div>
  </div>`;
}
function wireTradeOps() {
  const g = $("#trAsGo"); if (g) g.onclick = async () => {
    try {
      const r = await api("/trade/assurance", "POST", { order_id: Number($("#trAsOrder").value), seller: $("#trAsSeller").value, amount: Number($("#trAsAmt").value) });
      toast("Assurance " + (r.assurance && r.assurance.ref)); render();
    } catch (e) { toast(e.message); }
  };
}

async function vRetention() {
  const [rec, mem] = await Promise.all([api("/admin/recurring", {}), api("/admin/memberships", {})]);
  const scheds = rec.schedules || [];
  const byS = {}; scheds.forEach(s => byS[s.status] = (byS[s.status] || 0) + 1);
  const mems = mem.memberships || [];
  return `<div class="a-head"><h2>🔁 Subscriptions &amp; Members</h2><p class="a-sub">Subscribe &amp; Save recurring delivery schedules + paid membership tiers (Prime / Plus / Walmart+ style; benefits apply at checkout). Tiers &amp; frequencies in Data Studio: <code>membershipTiers</code>, <code>recFrequencies</code>.</p></div>
  <div class="a-card"><h3>Recurring schedules · ${scheds.length} · ${rec.due} due now</h3>
    <p class="a-sub">${Object.entries(byS).map(([k, v]) => `<span class="a-chip">${esc(k)}·${v}</span>`).join("") || "none"}</p>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>product</th><th>customer</th><th>qty</th><th>freq</th><th>disc</th><th>next ship</th><th>cycles</th><th>status</th></tr></thead>
      <tbody>${scheds.slice(0, 20).map(s => `<tr><td><code>${esc(s.product_id)}</code> ${esc(s.product_title || "")}</td><td>${esc(s.owner)}</td><td>${s.qty}</td><td>${s.frequency_days}d</td><td>${s.discount_pct}%</td><td>${esc(String(s.next_ship_at).slice(0, 10))}</td><td>${s.cycles_completed}</td><td><span class="a-chip">${esc(s.status)}</span></td></tr>`).join("") || '<tr><td colspan="8">No subscriptions yet.</td></tr>'}</tbody></table></div>
    <button class="btn-yellow" data-act="admin-rec-process">Process due shipments</button>
  </div>
  <div class="a-card"><h3>Membership tiers</h3>
    <div>${(mem.tiers || []).map(t => `<span class="a-chip">${esc(t.name)} · ${money(t.price)}${t.benefits.length ? " · " + t.benefits.join(", ") : ""}</span>`).join("")}</div>
  </div>
  <div class="a-card"><h3>Members</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>customer</th><th>tier</th><th>status</th><th>renews</th></tr></thead>
      <tbody>${mems.slice(0, 20).map(m => `<tr><td>${esc(m.owner)}</td><td><span class="a-chip">${esc(m.tier_detail ? m.tier_detail.name : m.tier)}</span></td><td>${esc(m.status)}</td><td>${esc(String(m.renews_at || "").slice(0, 10))}</td></tr>`).join("") || '<tr><td colspan="4">No members yet.</td></tr>'}</tbody></table></div>
  </div>`;
}
async function vRisk() {
  const q = await api("/admin/risk/queue", {});
  const st = q.stats || { total: 0, approved: 0, held: 0, blocked: 0, pending: 0, avg_score: 0 };
  return `<div class="a-head"><h2>🛡️ Risk &amp; Fraud</h2><p class="a-sub">Order screening at checkout — velocity (owner / IP / card), blocklists, composite 0–100 score → approve / hold / block. Held and blocked orders land in this queue. Signals &amp; thresholds are Data Studio registries: <code>riskSignals</code>, <code>riskActions</code>.</p></div>
  <div class="a-card"><h3>Screening stats</h3>
    <p class="a-sub"><span class="a-chip">screened·${st.total}</span><span class="a-chip">approved·${st.approved}</span><span class="a-chip">held·${st.held}</span><span class="a-chip">blocked·${st.blocked}</span><span class="a-chip">avg score·${st.avg_score}</span></p>
  </div>
  <div class="a-card"><h3>Review queue · ${st.pending} open</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>ref</th><th>customer</th><th>amount</th><th>score</th><th>signals</th><th>decision</th></tr></thead>
      <tbody>${(q.queue || []).slice(0, 25).map(e => `<tr><td><code>${esc(e.ref || e.id)}</code></td><td>${esc(e.owner || "—")}</td><td>${money(e.amount)}</td><td><b>${e.score}</b></td><td>${Object.keys(JSON.parse(e.signals || "{}")).map(k => `<span class="a-chip">${esc(k)}</span>`).join("") || "—"}</td><td><span class="a-chip">${esc(e.action)}</span></td></tr>`).join("") || '<tr><td colspan="6">Queue is clear.</td></tr>'}</tbody></table></div>
  </div>`;
}
async function vExperiments() {
  const list = await api("/admin/experiments", {});
  return `<div class="a-head"><h2>🧪 Experiments</h2><p class="a-sub">A/B tests with weighted variants — assignment is deterministic per customer (stable hash), conversion tracked per variant with a 95% significance readout. Statuses in Data Studio: <code>expStatuses</code>.</p></div>
  <div class="a-card"><h3>Experiments</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>key</th><th>name</th><th>variants</th><th>status</th><th>metric</th></tr></thead>
      <tbody>${(list.experiments || []).map(e => `<tr><td><code>${esc(e.key)}</code></td><td>${esc(e.name)}</td><td>${(e.variants || []).map(v => `<span class="a-chip">${esc(v.key)}·${(v.share * 100).toFixed(0)}%</span>`).join("")}</td><td><span class="a-chip">${esc(e.status)}</span></td><td>${esc(e.metric)}</td></tr>`).join("") || '<tr><td colspan="5">No experiments yet.</td></tr>'}</tbody></table></div>
  </div>`;
}
async function vPlanning() {
  const [list, pos] = await Promise.all([api("/admin/planning", {}), api("/admin/planning/pos", {})]);
  const st = list.stats || {};
  const buy = (list.replenishments || []).filter(r => r.reorder_qty > 0);
  return `<div class="a-head"><h2>📦 Planning &amp; Replenishment</h2><p class="a-sub">Per-SKU demand forecast from real order history (weighted moving average + trend), reorder point, safety stock and lead-time-aware suggested purchase orders to the primary supplier. Run the plan after order spikes or on a schedule. Statuses &amp; priorities in Data Studio: <code>planStatuses</code>, <code>planPriorities</code>.</p></div>
  <div class="a-cards">
    <div class="a-card"><h3>Overview</h3>
      <div class="a-stats">${[["SKUs tracked", st.skus || 0], ["Active SKUs", st.active_skus || 0], ["Open suggestions", st.open || 0], ["Urgent", st.urgent || 0], ["Below reorder point", st.below_reorder || 0]].map(([k, v]) => `<div><b>${v}</b><span>${k}</span></div>`).join("")}</div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px">
        <button class="btn-yellow" data-act="plan-run">▶ Run plan</button>
        <button class="btn-white" data-act="plan-approve-all" ${buy.length ? "" : "disabled"}>Approve ${buy.length} suggestion${buy.length === 1 ? "" : "s"}</button>
      </div></div>
    <div class="a-card"><h3>Suggested purchase orders</h3>
      <div class="a-tablewrap"><table class="a-table"><thead><tr><th>supplier</th><th>lines</th><th>units</th><th>est. cost</th></tr></thead>
        <tbody>${(pos.purchaseOrders || []).map(p => `<tr><td>${esc(p.supplier_name)}</td><td>${p.lines.length}</td><td>${p.units}</td><td>${p.cost ? esc(p.cost.toFixed(2)) : "—"}</td></tr>`).join("") || '<tr><td colspan="4">No purchase orders — run the plan.</td></tr>'}</tbody></table></div></div>
  </div>
  <div class="a-card"><h3>Replenishment plan</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>sku</th><th>product</th><th>available</th><th>avg/day</th><th>forecast 30d</th><th>lead</th><th>safety</th><th>reorder pt</th><th>reorder qty</th><th>supplier</th><th>priority</th><th>status</th><th></th></tr></thead>
      <tbody>${(list.replenishments || []).map(r => `<tr>
        <td><code>${esc(r.sku_code || r.sku_id)}</code></td><td>${esc(r.product_title || r.product_id)}</td>
        <td>${r.available}</td><td>${(+r.avg_daily).toFixed(1)}</td><td>${r.forecast_30d}</td><td>${r.lead_days}d</td>
        <td>${r.safety_stock}</td><td>${r.reorder_point}</td>
        <td><b>${r.reorder_qty > 0 ? r.reorder_qty : "—"}</b></td>
        <td>${esc(r.supplier_name || "—")}</td>
        <td><span class="a-chip">${esc(r.priority)}</span></td>
        <td><span class="a-chip">${esc(r.status)}</span></td>
        <td>${!["ordered", "received"].includes(r.status) ? `<button class="btn-white sm" data-act="plan-approve" data-id="${r.id}">Approve</button>` : `<code>${esc(r.po_ref || "")}</code>`}</td>
      </tr>`).join("") || '<tr><td colspan="13">No plan yet — run the plan to forecast demand.</td></tr>'}</tbody></table></div>
  </div>`;
}
function shell(content) {  $("#app").innerHTML = `
  <div class="p-shell">
    <aside class="p-side" id="pSide">
      <div class="p-logo"><b>${esc(TT.brand?.name || TT.brand?.wordmark || "Store")}</b><small>Store Console · ${esc(TT.tenant.slug)}</small>
        <button class="p-side-close" id="pSideClose" aria-label="Close navigation">✕</button></div>
      <nav class="p-nav">${NAV.map(grp => {
        const items = grp.items.filter(([k]) => canSee(k));
        if (!items.length) return "";
        return `<div class="p-nav-grp"><small>${grp.g}</small>${items.map(([k, l]) => `<button data-v="${k}" class="${view === k ? "on" : ""}">${l}</button>`).join("")}</div>`;
      }).join("")}</nav>
      <div style="padding:16px 18px;border-top:1px solid rgba(255,255,255,.1);margin-top:12px">
        <a href="/index.html?store=${esc(TT.tenant.slug)}" target="_blank" style="color:var(--p-side-text)">↗ Open storefront</a>
      </div>
    </aside>
    <div class="p-scrim" id="pScrim"></div>
    <main class="p-main"><div class="p-top"><button class="p-hamburger" id="pBurger" aria-label="Open navigation">☰</button><h1 id="vTitle">${NAVFLAT.find(n => n[0] === view)[1].replace(/^\S+\s/, "")}</h1><span class="spacer"></span>
      <span class="p-chip">${esc(TT.tenant.mode)}</span><span class="p-user">${esc(A.user.name)}</span>
      <button class="p-btn sm" id="logoutBtn">Sign out</button></div>
      <div id="vBody">${content}</div></main>
  </div>`;
  $$(".p-nav button").forEach(b => b.onclick = () => { view = b.dataset.v; render(); });
  $("#logoutBtn").onclick = async () => { await api("/auth/logout", "POST"); location.href = "/index.html"; };
  wireDrawer();
}
/* the touch drawer: on tablet/phone the sidebar is off-canvas and opened by the hamburger.
   Mirrors the platform console's wiring so both consoles behave identically on a phone. */
function wireDrawer() {
  const side = $("#pSide"), scrim = $("#pScrim"), burger = $("#pBurger"), close = $("#pSideClose");
  if (burger) burger.onclick = () => { if (side) side.classList.add("p-side-open"); if (scrim) scrim.style.display = "block"; };
  const shut = () => { if (side) side.classList.remove("p-side-open"); if (scrim) scrim.style.display = "none"; };
  if (close) close.onclick = shut;
  if (scrim) scrim.onclick = shut;
  $$(".p-nav button").forEach(b => b.addEventListener("click", shut));
}

/* ---------- generic entity table/form ---------- */
/* Validation utilities */
function validateField(key, value, fieldDef) {
  const errors = [];
  // Required check
  if (fieldDef.required && (value === "" || value === null || value === undefined)) {
    errors.push(`${fieldDef.label} is required`);
    return errors;
  }
  // Skip if not required and empty
  if (!fieldDef.required && value === "") return errors;
  
  // Type-specific validation
  switch (fieldDef.type) {
    case "email":
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) errors.push(`${fieldDef.label} must be a valid email`);
      break;
    case "url":
      if (!/^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/.test(value)) errors.push(`${fieldDef.label} must be a valid URL`);
      break;
    case "number":
    case "money":
      if (value !== "" && isNaN(Number(value))) errors.push(`${fieldDef.label} must be a number`);
      if (fieldDef.min !== undefined && Number(value) < fieldDef.min) errors.push(`${fieldDef.label} must be >= ${fieldDef.min}`);
      if (fieldDef.max !== undefined && Number(value) > fieldDef.max) errors.push(`${fieldDef.label} must be <= ${fieldDef.max}`);
      break;
    case "text":
      if (fieldDef.minLength && value.length < fieldDef.minLength) errors.push(`${fieldDef.label} must be at least ${fieldDef.minLength} characters`);
      if (fieldDef.maxLength && value.length > fieldDef.maxLength) errors.push(`${fieldDef.label} must be at most ${fieldDef.maxLength} characters`);
      if (fieldDef.pattern && !new RegExp(fieldDef.pattern).test(value)) errors.push(`${fieldDef.label} has invalid format`);
      break;
    case "json":
      if (value && typeof value !== "object") errors.push(`${fieldDef.label} must be a valid JSON object/array`);
      break;
  }
  return errors;
}
function validateRow(row, def) {
  const errors = {};
  for (const f of def.fields) {
    const fieldErrors = validateField(f.key, row[f.key], f);
    if (fieldErrors.length > 0) errors[f.key] = fieldErrors;
  }
  return errors;
}
async function entityRows(key) { try { return (await api("/meta/entity/" + key)).rows; } catch (e) { return []; } }
async function refOptions(key) {
  const rows = await entityRows(key);
  return rows.map(r => {
    /* products carry their brand as the DISPLAY NAME (the string the catalogue, search facets,
       order snapshots and CSV exports all read), so the option value must be the label — the
       numeric row id would never match a real product and the form would render an empty
       required select and refuse every save. */
    if (key === "brand" && r.label != null) return { v: r.label, l: r.label };
    /* a platform-level master keyed by CODE (country, currency, subdivision) has no numeric id
       — its option value is the code itself. Falling back to r.id here would drop the value
       entirely, rendering an empty select that silently blocks every save of the record */
    const v = r.id != null ? r.id : (r.code != null ? r.code : r.key);
    return { v, l: r.title || r.name || r.label || r.code || r.ref || String(v) };
  });
}
async function fieldInput(f, val, registry) {
  const id = "f_" + f.key;
  if (f.type === "bool") return `<label><span>${esc(f.label)}</span><input type="checkbox" id="${id}" ${val ? "checked" : ""}></label>`;
  /* media and attributes are structured data the storefront renders directly, so they get
     row editors (public/js/editors.js) instead of a raw JSON textarea — mounted after the
     form is in the DOM by wireEditors(), read back by collect() */
  if (f.key === "media") return `<div class="p-field"><span class="p-field-l">${esc(f.label)}</span><div id="${id}" data-editor="media"></div></div>`;
  if (f.key === "attrs") return `<div class="p-field"><span class="p-field-l">${esc(f.label)}</span><div id="${id}" data-editor="attrs"></div></div>`;
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
    /* a record holding a value the registry no longer lists (a brand renamed or deleted
       underneath it, a legacy free-text value) must still be *representable*: without a
       matching option the select renders empty, and a REQUIRED ref then fails validation
       and silently blocks every save of that record — the value survives, unseen. */
    const unmatched = val != null && val !== "" && !opts.some(o => String(o.v) === String(val));
    return `<label><span>${esc(f.label)}</span><select id="${id}"><option value="">—</option>${unmatched ? `<option value="${esc(val)}" selected>${esc(val)}</option>` : ""}${opts.map(o => `<option value="${esc(o.v)}" ${String(o.v) === String(val) ? "selected" : ""}>${esc(o.l)}</option>`).join("")}</select></label>`;
  }
  const t = f.type === "money" || f.type === "number" ? "number" : f.type === "date" ? "date" : "text";
  const minAttr = f.min !== undefined ? `min="${f.min}"` : "";
  const maxAttr = f.max !== undefined ? `max="${f.max}"` : "";
  const patternAttr = f.pattern ? `pattern="${f.pattern}"` : "";
  const lengthAttrs = (f.minLength || f.maxLength) ? `data-minlen="${f.minLength||""}" data-maxlen="${f.maxLength||""}"` : "";
  return `<label><span>${esc(f.label)}${f.required ? " *" : ""}</span><input id="${id}" type="${t}" step="any" value="${esc(val == null ? "" : val)}" ${minAttr} ${maxAttr} ${patternAttr} ${lengthAttrs} ${f.readonly ? "disabled" : ""}></label>`;
}
function collect(def) {
  const row = {};
  for (const f of def.fields) {
    if (f.key === "media" || f.key === "attrs") {
      const get = formEditors[f.key];               /* structured editors expose a value accessor */
      if (get) { row[f.key] = get(); continue; }
    }
    const el = $("#f_" + f.key); if (!el || f.readonly) continue;
    let v = f.type === "bool" ? el.checked : el.value;
    if ((f.type === "json" || f.type === "multi") && v !== "") { try { v = JSON.parse(v); } catch (e) { toast("Invalid JSON in " + f.label); throw e; } }
    if (f.type === "money" || f.type === "number") v = v === "" ? null : Number(v);
    row[f.key] = v;
  }
  return row;
}
/* value accessors for the structured editors a form is currently showing, so collect()
   reads them back as objects without parsing a textarea */
const formEditors = {};
function wireEditors(fields, row, registry) {
  formEditors.media = null; formEditors.attrs = null;
  for (const f of fields) {
    const host = document.getElementById("f_" + f.key);
    if (!host || !host.dataset.editor) continue;
    let val = row[f.key];
    if (typeof val === "string") { try { val = JSON.parse(val); } catch (e) { val = f.key === "media" ? [] : {}; } }
    formEditors[f.key] = f.key === "media"
      ? mediaEditor(host, val, registry && registry.mediaKinds)
      : kvEditor(host, val);
  }
}
async function openForm(key, id, onDone) {
  const defs = (await api("/meta/entities")).entities;
  const storeDefs = Object.fromEntries(Object.entries(defs).filter(([, d]) => !d.platformOnly));
  const def = storeDefs[key];
  const registry = await api("/meta");
  let row = {};
  if (id != null) { const rows = await entityRows(key); row = rows.find(r => String(r[def.pk] ?? r.id) === String(id)) || {}; }
  const fields = def.fields.filter(f => !["tenant_id"].includes(f.key));
  $("#modal").innerHTML = `<div class="p-modal"><div class="p-modal-box"><div class="p-modal-head"><h3>${id != null ? "Edit" : "New"} ${esc(def.label.replace(/s$/, ""))}</h3><button id="mClose">✕</button></div>
    <div class="p-form" id="mForm">${await Promise.all(fields.map(f => fieldInput(f, row[f.key], registry))).then(a => a.join(""))}
      <div style="display:flex;gap:10px;margin-top:8px"><button class="p-btn primary" id="mSave">Save</button><button class="p-btn" id="mCancel">Cancel</button></div></div></div></div>`;
  $("#modal").classList.remove("hidden");
  wireEditors(fields, row, registry); /* mount the structured media/attrs editors now that
    their host divs are in the DOM — collect() reads them back via the accessors */
  const close = () => { const m = $("#modal"); m.innerHTML = ""; m.classList.add("hidden"); };
  $("#mClose").onclick = $("#mCancel").onclick = close;
  // Inline validation feedback
  $$("#mForm input, #mForm select, #mForm textarea").forEach(el => {
    el.oninput = el.onblur = () => {
      const f = def.fields.find(x => x.key === el.id.replace("f_", ""));
      if (!f) return;
      const val = f.type === "bool" ? el.checked : el.value;
      const errors = validateField(f.key, val, f);
      el.classList.toggle("field-invalid", errors.length > 0);
      el.classList.toggle("field-valid", errors.length === 0 && val !== "");
      el.title = errors.join("\n");
    };
  });
  $("#mSave").onclick = async () => {
    try {
      const body = collect(def);
      // Validate before submit
      const errs = validateRow(body, def);
      if (Object.keys(errs).length > 0) {
        const msg = Object.entries(errs).map(([k, v]) => v.join(", ")).join(" · ");
        toast(`Validation failed: ${msg}`);
        // Highlight fields
        Object.keys(errs).forEach(k => {
          const el = $("#f_" + k);
          if (el) { el.classList.add("field-invalid"); el.title = errs[k].join("\n"); }
        });
        return;
      }
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
  // Filter out platform-only entities for store admins
  const storeDefs = Object.fromEntries(Object.entries(defs).filter(([, d]) => !d.platformOnly));
  const def = storeDefs[key];
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
        ${opts.rowExtra ? opts.rowExtra(r) : ""}
        ${def.perm.write.length ? `<button class="p-btn sm" data-edit="${key}" data-id="${esc(r[def.pk] ?? r.id)}">Edit</button>
        <button class="p-btn sm danger" data-del="${key}" data-id="${esc(r[def.pk] ?? r.id)}">✕</button>` : ""}</td></tr>`).join("")}</tbody></table></div></div>`;
}
document.addEventListener("click", async e => {
  const nb = e.target.closest("[data-new]"), eb = e.target.closest("[data-edit]"), db = e.target.closest("[data-del]");
  const act = e.target.closest("[data-act]");
  try {
    if (act && act.dataset.act === "ship-order") return shipModal(act.dataset.id, act.dataset.num);
    if (act && act.dataset.act === "admin-rec-process") {
      const r = await api("/admin/recurring/process", "POST");
      toast(`Processed ${r.processed.length} due shipment(s) · ${r.remaining} remaining`); render();
    }
    if (act && act.dataset.act === "plan-run") {
      const r = await api("/admin/planning/run", "POST");
      toast(`Plan computed for ${r.planned} SKU(s) · ${r.stats.open} open suggestion(s)`); render();
    }
    if (act && act.dataset.act === "plan-approve-all") {
      const r = await api("/admin/planning/approve-all", "POST");
      toast(`Approved ${r.approved} suggestion(s)`); render();
    }
    if (act && act.dataset.act === "plan-approve") {
      const r = await api(`/admin/planning/${act.dataset.id}`, "PUT", { status: "approved" });
      toast(`Approved ${r.replenishment.po_ref}`); render();
    }
    /* E17 · mobility — the ride lifecycle advances through the engine's legal
       transitions; the console only carries the target status the operator clicked */
    if (act && act.dataset.act === "mob-next") {
      const r = await api(`/admin/mobility/rides/${act.dataset.id}`, "PUT", { status: act.dataset.to });
      if (r.error) toast(r.error); else { toast(`Ride ${r.ride.status}${r.ride.fare ? " · fare " + (+r.ride.fare).toFixed(2) : ""}`); render(); }
    }
    if (act && act.dataset.act === "mob-new-ride") {
      const pickup = prompt("Pickup point", "Downtown · 5th Ave"); if (pickup == null) return;
      const dropoff = prompt("Drop-off point", "Airport · Terminal 4"); if (dropoff == null) return;
      const kind = prompt("Vehicle kind (car · suv · bike · auto · van)", "car") || "car";
      const r = await api("/admin/mobility/rides", "POST", { rider: "Walk-up rider", pickup, dropoff, vehicle_kind: kind, payment_method: "cash" });
      if (r.error) toast(r.error); else { toast(`Requested ${r.ride.ref}${r.ride.driver ? " · dispatched to " + r.ride.driver.name : " · queued for dispatch"}`); render(); }
    }
    if (act && act.dataset.act === "mob-new-driver") {
      const name = prompt("Driver name"); if (!name) return;
      const kind = prompt("Vehicle kind (car · suv · bike · auto · van)", "car") || "car";
      const plate = prompt("Plate", "") || "";
      const r = await api("/admin/mobility/drivers", "POST", { name, vehicle_kind: kind, plate, status: "offline" });
      if (r.error) toast(r.error); else { toast(`Driver ${r.driver.name} added`); render(); }
    }
    if (act && act.dataset.act === "mob-new-vehicle") {
      const plate = prompt("Plate"); if (!plate) return;
      const kind = prompt("Kind (car · suv · bike · auto · van)", "car") || "car";
      const r = await api("/admin/mobility/vehicles", "POST", { plate, kind, capacity: kind === "suv" || kind === "van" ? 6 : 4 });
      if (r.error) toast(r.error); else { toast(`Vehicle ${r.vehicle.plate} registered`); render(); }
    }
    if (act && act.dataset.act === "mob-toggle-driver") {
      const r = await api(`/admin/mobility/drivers/${act.dataset.id}/toggle`, "POST", { online: act.dataset.to === "1" });
      if (r.error) toast(r.error); else { toast(`Driver ${r.driver.status}`); render(); }
    }
    if (act && act.dataset.act === "mob-deact-driver") {
      if (!confirm("Deactivate this driver? They leave dispatch immediately.")) return;
      const r = await api(`/admin/mobility/drivers/${act.dataset.id}/deactivate`, "POST");
      if (r.error) toast(r.error); else { toast("Driver deactivated"); render(); }
    }
    /* surge zones: the upsert rewrites every column, so a toggle carries the row back
       intact rather than sending the active bit alone (which would flatten the rest) */
    if (act && act.dataset.act === "mob-new-zone") zoneModal(null);
    if (act && act.dataset.act === "mob-edit-zone") {
      const zd = await api("/admin/mobility", {});
      const z = (zd.zones || []).find(x => String(x.id) === String(act.dataset.id));
      if (z) zoneModal(z); else toast("Zone not found");
    }
    if (act && act.dataset.act === "mob-toggle-zone") {
      const zd = await api("/admin/mobility", {});
      const z = (zd.zones || []).find(x => String(x.id) === String(act.dataset.id));
      if (!z) return toast("Zone not found");
      const r = await api("/admin/mobility/zones", "POST", {
        id: z.id, name: z.name, kind: z.kind, multiplier: z.multiplier,
        center_lat: z.center_lat, center_lng: z.center_lng, radius_km: z.radius_km,
        active: act.dataset.on === "1", starts_at: z.starts_at, ends_at: z.ends_at
      });
      if (r.error) toast(r.error); else { toast(`Zone ${r.zone.name} ${r.zone.active ? "active" : "paused"}`); render(); }
    }
    /* E18 · operations — HRMS/payroll, procurement, manufacturing and projects. Every
       advance honours the engine's own flow and approval gate; the console only carries
       the target status the operator clicked */
    if (act && act.dataset.act === "ops-new-employee") {
      const name = prompt("Employee name"); if (!name) return;
      const dept = prompt("Department", "Operations") || "";
      const salary = Number(prompt("Base salary", "5000")) || 0;
      const r = await api("/admin/ops/employees", "POST", { name, department: dept, base_salary: salary, status: "active" });
      if (r.error) toast(r.error); else { toast(`Employee ${r.employee.code} added`); render(); }
    }
    if (act && act.dataset.act === "ops-payroll-run") {
      const period = prompt("Period (YYYY-MM)", new Date().toISOString().slice(0, 7)) || new Date().toISOString().slice(0, 7);
      const r = await api("/admin/ops/payroll/run", "POST", { period });
      if (r.error) toast(r.error); else { toast(`Payroll run for ${r.run.period}: ${r.run.headcount} employees, net ${(+r.run.net).toFixed(2)}`); render(); }
    }
    if (act && act.dataset.act === "ops-payroll-status") {
      const r = await api(`/admin/ops/payroll/${act.dataset.id}`, "PUT", { status: act.dataset.to });
      if (r.error) toast(r.error); else { toast(`Payroll ${r.run.status}`); render(); }
    }
    if (act && act.dataset.act === "ops-new-request") {
      const item = prompt("What do you need?"); if (!item) return;
      const qty = Number(prompt("Quantity", "1")) || 1;
      const cost = Number(prompt("Estimated unit cost", "10")) || 0;
      const r = await api("/admin/ops/requests", "POST", { status: "draft", requested_by: "Console", lines: [{ item, qty, est_unit_cost: cost }] });
      if (r.error) toast(r.error); else { toast(`Purchase request ${r.request.ref} created`); render(); }
    }
    if (act && act.dataset.act === "ops-pr-advance") {
      const r = await api(`/admin/ops/requests/${act.dataset.id}`, "PUT", { status: act.dataset.to });
      if (r.error) toast(r.error); else { toast(`Request ${r.request.status}`); render(); }
    }
    if (act && act.dataset.act === "ops-new-wo") {
      const product = prompt("Product ID / SKU reference", "LX-CMP-005"); if (!product) return;
      const qty = Number(prompt("Quantity to build", "100")) || 100;
      const r = await api("/admin/ops/work-orders", "POST", { product_id: product, qty, status: "planned", unit_cost: 0 });
      if (r.error) toast(r.error); else { toast(`Work order ${r.workOrder.ref} created`); render(); }
    }
    if (act && act.dataset.act === "ops-wo-complete") {
      const r = await api(`/admin/ops/work-orders/${act.dataset.id}/complete`, "POST");
      if (r.error) toast(r.error); else { toast(`Completed ${r.completed} good unit(s)${r.scrapped ? ` · ${r.scrapped} scrapped` : ""}`); render(); }
    }
    if (act && act.dataset.act === "ops-new-project") {
      const name = prompt("Project name"); if (!name) return;
      const budget = Number(prompt("Budget", "10000")) || 0;
      const r = await api("/admin/ops/projects", "POST", { name, budget, status: "planning" });
      if (r.error) toast(r.error); else { toast(`Project ${r.project.code} created`); render(); }
    }
    if (act && act.dataset.act === "ops-new-task") {
      const title = prompt("Task title"); if (!title) return;
      const projectId = prompt("Project ID (blank for none)") || null;
      const r = await api("/admin/ops/tasks", "POST", { title, project_id: projectId, status: "todo" });
      if (r.error) toast(r.error); else { toast("Task created"); render(); }
    }
    if (act && act.dataset.act === "ops-task-done") {
      const r = await api("/admin/ops/tasks", "POST", { id: act.dataset.id, title: "—", status: "done" });
      if (r.error) toast(r.error); else { toast("Task done"); render(); }
    }
    if (act && act.dataset.act === "ops-task-time") {
      const h = Number(prompt("Hours to log", "1")) || 0;
      const r = await api(`/admin/ops/tasks/${act.dataset.id}/time`, "POST", { hours: h });
      if (r.error) toast(r.error); else { toast(`Logged ${h}h`); render(); }
    }
    if (act && act.dataset.act === "ops-appr") {
      const r = await api(`/admin/ops/approvals/${act.dataset.id}`, "PUT", { status: act.dataset.to });
      if (r.error) toast(r.error); else { toast(`Approval ${r.approval.status}`); render(); }
    }
    if (act && act.dataset.act === "co-new") openForm(act.dataset.key, null, render);
    if (act && act.dataset.act === "co-cap") { view = "settings"; coCap = null; render(); }
    if (act && act.dataset.act === "co-mktperf") {
      const rows = await api("/meta/entity/seller", {});
      let n = 0;
      for (const s of (rows.rows || [])) { try { await api("/marketplace/performance/" + s.id, "POST", {}); n++; } catch (e) { } }
      toast(`Health recomputed for ${n} seller(s)`); render();
    }
    if (nb) openForm(nb.dataset.new, null, render);
    if (eb) openForm(eb.dataset.edit, eb.dataset.id, render);
    if (db) { if (!confirm("Delete this record?")) return; await api(`/meta/entity/${db.dataset.del}/${encodeURIComponent(db.dataset.id)}`, "DELETE"); toast("Deleted"); render(); }
    /* tenancy hierarchy: select a node for the config inspector, suspend/activate, delete a
       subtree, open the new-node form, and set a config override on the selected node */
    if (act && act.dataset.act === "tn-sel") { if ($("#tnKeyIn")) tnKey = $("#tnKeyIn").value.trim(); tnSel = Number(act.dataset.id); render(); }
    if (act && act.dataset.act === "tn-toggle") { const t = await api(`/tenancy/node/${act.dataset.id}`, "PUT", { status: act.dataset.to }); toast(t.error || `Node ${act.dataset.to}`); render(); }
    if (act && act.dataset.act === "tn-del") {
      const n = act.dataset.id;
      if (!confirm("Delete this node and everything beneath it?")) return;
      const t = await api(`/tenancy/node/${n}`, "DELETE");
      if (tnSel === Number(n)) tnSel = null;
      toast(t.error || `Removed ${t.removed} node(s)`); render();
    }
    if (act && act.dataset.act === "tn-new") { const h = $("#tnModalHost"); if (h) { h.classList.remove("hidden"); h.querySelector(".p-modal").style.display = "flex"; } }
    if (act && act.dataset.act === "tn-create") {
      const parent = $("#tnParent") ? Number($("#tnParent").value) : null;
      const t = await api("/tenancy/node", "POST", { parent_id: parent, kind: $("#tnKind") ? $("#tnKind").value : "organization", name: $("#tnName") ? $("#tnName").value.trim() : "" });
      if (t.error) { toast(t.error); return; }
      toast(`Created ${t.path}`); render();
    }
    if (act && act.dataset.act === "tn-cfg-set") {
      tnKey = $("#tnKeyIn") ? $("#tnKeyIn").value.trim() : tnKey;
      const raw = $("#tnValIn") ? $("#tnValIn").value.trim() : "";
      let val = {};
      if (raw) { try { val = JSON.parse(raw); } catch (e) { toast("Value must be valid JSON"); return; } }
      const t = await api(`/tenancy/config/${act.dataset.id}/${encodeURIComponent(tnKey)}`, "POST", val);
      toast(t.error || "Configuration saved"); render();
    }
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
  /* the feature flags ARE capability atoms — read the catalog so the settings view
     labels each with its real name and points to where it is tuned */
  const cat = await api("/capabilities").catch(() => ({}));
  const capAtoms = {}; let capNote = "";
  if (cat && cat.catalog) {
    for (const c of cat.catalog) if (c.domain === "storefront") capAtoms[c.key] = c;
    const n = Object.keys(capAtoms).length;
    if (n) capNote = `The <b>${n}</b> toggles marked <span class="p-tag">atom</span> live in <b>◈ Capabilities</b> — switch and tune them there; this checkbox is the same bit.`;
  }
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
    ${Object.entries(st.features).map(([k, v]) => {
      const atom = (capAtoms || {})[k.replace(/([A-Z])/g, (_, c) => "_" + c.toLowerCase())];
      return `<label style="display:flex;gap:8px;align-items:center" title="${esc(atom ? atom.description : "a settings row, not yet an atom")}"><input type="checkbox" data-feat="${k}" ${v ? "checked" : ""}> ${esc(atom ? atom.label : k)}${atom ? ' <span class="p-tag">atom</span>' : ""}</label>`;
    }).join("")}
    </div>${capNote ? `<p class="hint" style="grid-column:1/-1">${capNote}</p>` : ""}</div>`)}
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
  const defs = Object.fromEntries(Object.entries((await api("/meta/entities")).entities).filter(([, d]) => !d.platformOnly));
  const customs = await api("/meta/entity/custom_provider").catch(() => ({ rows: [] }));
  return `
  <div class="p-panel"><h2>Entity Studio</h2>
    <p class="p-tag">Browse and manage entity data for this store.</p>
    <div style="display:flex;gap:10px;flex-wrap:wrap;margin:14px 0">${Object.entries(defs).map(([k, d]) => `<button class="p-btn sm ${k === A.studioSel ? "primary" : ""}" data-studio="${k}">${d.icon} ${esc(d.label)}</button>`).join("")}</div>
    <div id="studioBody">${A.studioSel ? await entityTable(A.studioSel) : '<div class="p-empty">Select an entity above</div>'}</div></div>`;
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

/* ---------- global catalog: platform-supplied products this store may list ----------
   The platform populates the global catalogue automatically (one canonical product per
   universe the constitution declares) and manually (console rows). A store admin may
   pull one into their own catalogue ONLY IF the platform has permitted it — the gate is
   server-side; this view never decides, it reports what the platform allows. */
async function vGcatalog() {
  let items = [];
  try { ({ items } = await api("/tenant/catalog/importable")); } catch (e) { toast(e.message); }
  const permitted = items.filter(i => i.permitted && !i.listed);
  const listed = items.filter(i => i.listed);
  const denied = items.filter(i => !i.permitted);
  const row = i => `<tr><td><b>${esc(i.name)}</b><div style="font-size:12px;color:var(--p-muted)">${esc(i.sku)}</div></td>
    <td class="p-tag">${esc(i.universe)}</td><td>${esc(i.type)}</td>
    <td>${i.listed ? '<span class="badge active">On your shelf</span>' : i.permitted ? '<button class="p-btn primary sm" data-gimp="' + i.id + '">Add to my store</button>' : '<span class="badge">🔒 ' + esc(i.reason || "Not permitted") + '</span>'}</td></tr>`;
  return `
  <div class="p-panel"><h2>🌐 Global Catalog — platform products</h2>
    <p style="margin:0 0 14px;color:var(--p-muted);font-size:13px">Every product archetype the platform supports (UPIP §1: Physical, Digital, OTT, Cloud, API, AI, Financial, Quantum, Future Unknown…), populated automatically from the constitution and extended by the platform admin. You may list one here <b>only when the platform has permitted your store</b> — import is idempotent and never counts against your plan quota.</p>
    <div class="p-stats" style="margin-bottom:14px">
      <div class="p-stat"><em>Available to you</em><b>${permitted.length}</b></div>
      <div class="p-stat"><em>Already on your shelf</em><b>${listed.length}</b></div>
      <div class="p-stat"><em>Not yet permitted</em><b>${denied.length}</b><small>request from the platform admin</small></div>
    </div>
    <div class="p-scroll-x"><table class="p-table"><thead><tr><th>Product</th><th>Universe</th><th>Type</th><th></th></tr></thead>
    <tbody>${items.map(row).join("") || '<tr><td colspan="4" class="p-empty">The global catalogue is empty</td></tr>'}</tbody></table></div></div>`;
}
function wireGcatalog() {
  $$("[data-gimp]").forEach(b => b.onclick = async () => {
    try {
      const r = await api("/tenant/catalog/import", "POST", { global_product_id: b.dataset.gimp });
      toast("Imported as " + r.type + (r.updated ? " (refreshed)" : ""));
      render();
    } catch (e) { toast(e.message); }
  });
}
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
  const aiGw = await api("/admin/ai-gateways").catch(() => ({ gateways: [] }));
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
    <div class="p-panel"><h3>AI Provider Credentials</h3>
      <p style="color:var(--p-muted);font-size:13px">Configure API keys for each AI provider. Secrets are stored encrypted server-side.</p>
      <div class="p-scroll-x"><table class="p-table"><thead><tr><th>Provider</th><th>Fields</th><th>Status</th><th></th></tr></thead>
      <tbody id="aiGwBody">${aiGw.gateways.map(gw => {
        const p = premProviders.find(p => p.id === gw.id) || {};
        const fields = p.fields || [];
        const hasSecret = fields.some(f => f.secret && (gw.config || {})[f.key]);
        return `<tr>
          <td><b>${esc(p.emoji)} ${esc(p.name)}</b><br><span class="p-tag">${esc(p.desc || "")}</span></td>
          <td><div style="display:flex;flex-wrap:wrap;gap:6px">${fields.map(f => {
            const val = (gw.config || {})[f.key] || "";
            const masked = f.secret && val ? `••••${val.slice(-4)}` : val;
            return `<label style="font-size:11px"><span>${esc(f.label)}</span><input data-aicred="${gw.id}" data-aikey="${f.key}" value="${esc(masked)}" style="font-size:11px" ${f.secret ? 'type="password"' : ''}></label>`;
          }).join("")}</div></td>
          <td>${hasSecret ? '<span class="badge active">configured</span>' : '<span class="badge processing">unconfigured</span>'}</td>
          <td><button class="p-btn sm" data-aicfg="${gw.id}">Test</button></td>
        </tr>`;
      }).join("") || '<tr><td colspan="4">No AI providers available. Configure them in Platform Console → Provider Registry.</td></tr>'}</tbody></table></div>
      <div style="margin-top:10px;display:flex;gap:10px"><button class="p-btn primary" id="aiGwSave">Save credentials</button><button class="p-btn" id="aiGwTestAll">Test all</button></div>
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
  const saveCredentials = async () => {
    const creds = {};
    $$("[data-aicred]").forEach(inp => {
      const id = inp.dataset.aicred, k = inp.dataset.aikey, v = inp.value;
      if (v) { creds[id] = creds[id] || {}; creds[id][k] = v; }
    });
    try { await api("/admin/ai-gateways", "PUT", creds); toast("AI credentials saved"); } catch (e) { toast(e.message); }
  };
  const testCredential = async id => {
    try { const r = await api("/admin/ai-gateways/" + encodeURIComponent(id) + "/test", "POST", {}); toast(r.message); } catch (e) { toast(e.message); }
  };
  const testAll = async () => {
    $$("[data-aicfg]").forEach(b => testCredential(b.dataset.aicfg));
  };
  if ($("#aiGwSave")) $("#aiGwSave").onclick = saveCredentials;
  if ($("#aiGwTestAll")) $("#aiGwTestAll").onclick = testAll;
  const collect = () => { const cap = $("#aiCapSel").value, p = {}; if (cap === "product_recommendation" || cap === "image_processing") { if ($("#aiPid").value) p.product_id = $("#aiPid").value; } if (cap === "data_analysis" && $("#aiCols").value) p.columns = $("#aiCols").value.split(",").map(x => x.trim()).filter(Boolean); return { cap, p }; };
  const run = async () => { const { cap, p } = collect(); try { const r = await api("/ai/run/" + encodeURIComponent(cap), "POST", p); $("#aiOut").textContent = JSON.stringify(r, null, 1); toast(cap + " · " + (r.tier || "") + " · " + money(r.cost || 0)); } catch (e) { $("#aiOut").textContent = "⚠ " + e.message; toast(e.message); } };
  const task = async () => { const { cap, p } = collect(); try { const r = await api("/ai/tasks", "POST", { capability: cap, params: p, runNow: true }); $("#aiOut").textContent = JSON.stringify(r.tasks.slice(0, 6), null, 1); toast("Queued"); render(); } catch (e) { toast(e.message); } };
  if ($("#aiRun")) $("#aiRun").onclick = run; if ($("#aiTask")) $("#aiTask").onclick = task;
  $$("[data-aicfg]").forEach(b => b.onclick = () => testCredential(b.dataset.aicfg));
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
/* this store's OWN role set — roles are per-store data. A store that has never edited its
   set inherits the platform default (ownSet false); the first edit forks it, and a fork can
   be dissolved back to the default. Defining a role is a team:write trust. */
async function vTeam() {
  const [r, s] = await Promise.all([api("/admin/roles"), api("/admin/staff")]);
  const roles = r.roles || [], secs = r.sections || [];
  const canEdit = (A.allowed || []).includes("*") || (A.allowed || []).includes("team");
  const row = u => `<tr><td><b>${esc(u.name)}</b><br><span class="p-tag">${esc(u.email)}</span></td>
    <td><select data-srole="${u.id}" ${String(u.id) === String(r.me.user.id) ? "disabled" : ""}>${roles.map(rl => `<option ${u.staff_role === rl.key ? "selected" : ""}>${esc(rl.key)}</option>`).join("")}</select></td>
    <td><span class="badge ${u.disabled ? "failed" : "published"}">${u.disabled ? "disabled" : "active"}</span></td>
    <td class="p-tag">${esc((u.last_login || "").slice(0, 16) || "never")}</td>
    <td style="text-align:right;white-space:nowrap"><button class="p-btn sm" data-sperm="${u.id}" title="Per-user overrides">Perms</button> ${String(u.id) !== String(r.me.user.id) ? `<button class="p-btn sm danger" data-sdel="${u.id}">Remove</button>` : ""}</td></tr>`;
  return `<div class="p-panel"><h2>👥 Team &amp; Roles</h2>
    <p style="color:var(--p-muted);font-size:13px;margin:0 0 12px">Staff share the store-console admin login but see and can only edit the sections their <b>role</b> grants. This store's roles are its own data${r.ownSet ? "" : " — it currently inherits the platform default, and the first edit forks it"}; per-user permission overrides take precedence.</p>
    <h3>Role definitions (this store) ${r.ownSet ? '<span class="badge">forked from the platform default</span>' : '<span class="badge">platform default</span>'}</h3>
    <div style="display:flex;gap:8px;margin-bottom:8px">${canEdit ? `<button class="p-btn primary sm" id="roleNew">+ New role</button>` : ""}${r.ownSet && canEdit ? `<button class="p-btn sm" id="roleReset">Reset to platform default</button>` : ""}</div>
    <div class="p-scroll-x"><table class="p-table"><thead><tr><th>Role</th><th>Grants (section: access)</th>${canEdit ? "<th></th>" : ""}</tr></thead><tbody>${roles.map(rl => `<tr><td><b>${esc(rl.name)}</b><br><code>${esc(rl.key)}</code></td><td class="p-tag">${Object.entries(rl.sections || {}).map(([k, v]) => `${esc(k)}=${esc(v)}`).join(" · ")}</td>${canEdit ? `<td style="text-align:right">${rl.key !== "owner" ? `<button class="p-btn sm" data-roleedit="${esc(rl.key)}">Edit</button>` : ""}</td>` : ""}</tr>`).join("")}</tbody></table></div>
    <h3>Members</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>Member</th><th>Role</th><th>Status</th><th>Last login</th><th></th></tr></thead><tbody>${(s.staff || []).map(row).join("")}</tbody></table></div>
    <div class="p-panel" style="margin-top:10px"><b>Add staff member</b><div style="display:flex;gap:8px;flex-wrap:wrap;align-items:end;margin-top:6px">
      <label><span>Name</span><input id="stName"></label><label><span>Email</span><input id="stEmail"></label>
      <label><span>Role</span><select id="stRole">${roles.filter(rl => rl.key !== "owner").map(rl => `<option>${esc(rl.key)}</option>`).join("")}</select></label>
      <label><span>Password</span><input id="stPw" type="text" placeholder="blank = generate"></label>
      <button class="p-btn primary sm" id="stAdd">Add member</button><span id="stGen" class="p-tag"></span></div></div></div>`;
}
/* the per-section grant editor: one control per console section, each read/write/off.
   It renders for create and edit from the same shape, so the two cannot drift. */
function roleModal(role, sections) {
  const r = role || { key: "", name: "", desc: "", sections: {} };
  const m = modal(`<div class="p-modal-head"><h3>${role ? "Edit role" : "New role"}</h3><button data-mclose>✕</button></div>
    <div class="p-form">
      <label><span>Name</span><input id="rmName" value="${esc(r.name)}" ${role ? "" : 'placeholder="e.g. Order Desk"'}></label>
      <label><span>Key (lowercase, no spaces)</span><input id="rmKey" value="${esc(r.key)}" ${role ? "disabled" : ""} placeholder="order_desk"></label>
      <label><span>Description</span><input id="rmDesc" value="${esc(r.desc || "")}"></label>
      <div class="p-tag">Grants — each section: write, read or off</div>
      <div style="max-height:260px;overflow:auto;border:1px solid var(--p-border);border-radius:8px;padding:8px">
      ${sections.map(sec => `<label style="display:flex;justify-content:space-between;align-items:center;padding:3px 0"><span>${esc(sec)}</span>
        <select data-rmsec="${esc(sec)}"><option value="">off</option><option ${r.sections && r.sections[sec] === "read" ? "selected" : ""} value="read">read</option><option ${r.sections && r.sections[sec] === "write" ? "selected" : ""} value="write">write</option></select></label>`).join("")}
      </div>
      <div class="p-err hidden" id="rmErr" style="color:var(--p-red);font-size:13px"></div>
      <button class="p-btn primary" id="rmSave">${role ? "Save role" : "Create role"}</button>
    </div>`);
  m.querySelector("#rmSave").onclick = async () => {
    const sections2 = {};
    m.querySelectorAll("[data-rmsec]").forEach(sel => { if (sel.value) sections2[sel.dataset.rmsec] = sel.value; });
    const body = { name: m.querySelector("#rmName").value.trim(), key: m.querySelector("#rmKey").value.trim().toLowerCase(), desc: m.querySelector("#rmDesc").value, sections: sections2 };
    try { await api("/admin/roles", "POST", body); document.getElementById("modal").innerHTML = ""; toast("Role saved"); render(); }
    catch (e) { const err = m.querySelector("#rmErr"); err.textContent = e.message; err.classList.remove("hidden"); }
  };
}
function wireTeam() {
  const $$ = s => Array.from(document.querySelectorAll(s));
  $$("[data-srole]").forEach(sel => sel.onchange = async () => { try { await api("/admin/staff/" + sel.dataset.srole, "PUT", { staff_role: sel.value }); toast("Role updated"); } catch (e) { toast(e.message); } });
  $$("[data-sdel]").forEach(b => b.onclick = async () => { if (!confirm("Disable this member?")) return; try { await api("/admin/staff/" + b.dataset.sdel, "DELETE"); render(); } catch (e) { toast(e.message); } });
  $$("[data-sperm]").forEach(b => b.onclick = async () => { const cur = prompt("Per-user overrides as JSON, e.g. {\"products\":\"read\",\"trash\":false}", "{}"); if (cur == null) return; try { await api("/admin/staff/" + b.dataset.sperm, "PUT", { perms: JSON.parse(cur) }); toast("Saved"); } catch (e) { toast(e.message); } });
  if (document.getElementById("stAdd")) document.getElementById("stAdd").onclick = async () => { try { const r = await api("/admin/staff", "POST", { name: document.getElementById("stName").value, email: document.getElementById("stEmail").value, staff_role: document.getElementById("stRole").value, password: document.getElementById("stPw").value || undefined }); if (r.generated) document.getElementById("stGen").textContent = "generated password: " + r.generated; toast("Member added"); render(); } catch (e) { toast(e.message); } };
  /* per-store role definition: create, edit, and dissolve a fork back to the default */
  const newBtn = document.getElementById("roleNew");
  if (newBtn) newBtn.onclick = async () => { const all = await api("/admin/roles"); roleModal(null, all.sections || []); };
  $$("[data-roleedit]").forEach(b => b.onclick = async () => {
    const all = await api("/admin/roles");
    const role = (all.roles || []).find(r => r.key === b.dataset.roleedit);
    roleModal(role, all.sections || []);
  });
  const resetBtn = document.getElementById("roleReset");
  if (resetBtn) resetBtn.onclick = async () => { if (!confirm("Discard this store's own roles and inherit the platform default again?")) return; try { await api("/admin/roles/reset", "POST", {}); toast("Reverted to the platform default"); render(); } catch (e) { toast(e.message); } };
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
/* ── tenancy hierarchy ── the tenant's own org tree (org → BU → brand → store → channel).
   Every node is data; the path is materialized so a subtree is one LIKE away, and the tree
   doubles as the CONFIG CASCADE — the inspector shows which node a resolved value came from. */
let tnSel = null, tnKey = "";
const TN_ICON = { tenant: "🏬", organization: "🏢", business_unit: "🧱", brand: "🏷️", store: "🏪", channel: "📡", website: "🌐", mobile_app: "📱", marketplace: "🛒", social: "💬", pos: "🧾", api_commerce: "🔌", region: "🗺️" };
function flatten(n, out = []) { out.push(n); (n.children || []).forEach(c => flatten(c, out)); return out; }
async function renderStructure() {
  const r = await api("/tenancy/tree");
  const kinds = r.kinds || [];
  const walk = (n, depth) => {
    const kids = (n.children || []).map(c => walk(c, depth + 1)).join("");
    const isRoot = n.parent_id == null;
    const st = n.status === "active" ? "canonical" : "retired";
    return `<div class="tn-row${tnSel === n.id ? " tn-sel" : ""}" style="margin-left:${depth * 20}px">
        <button class="tn-name" data-act="tn-sel" data-id="${n.id}" title="Inspect configuration">
          <span>${TN_ICON[n.kind] || "▪️"}</span><b>${esc(n.name)}</b></button>
        <code class="tn-path">${esc(n.path)}</code>
        <span class="badge ${st}">${esc(n.status)}</span>
        ${isRoot ? `<span class="p-sub">tenant root</span>` : `<span class="tn-acts">
          <button class="p-btn sm" data-act="tn-toggle" data-id="${n.id}" data-to="${n.status === "active" ? "suspended" : "active"}">${n.status === "active" ? "Suspend" : "Activate"}</button>
          <button class="p-btn sm danger" data-act="tn-del" data-id="${n.id}">✕</button></span>`}
      </div>${kids}`;
  };
  const treeHtml = r.tree ? walk(r.tree, 0) : `<div class="p-empty">No hierarchy yet</div>`;
  const nodes = r.tree ? flatten(r.tree) : [];
  if (tnSel != null && !nodes.some(n => n.id === tnSel)) tnSel = null;
  const sel = nodes.find(n => n.id === tnSel) || (r.tree || null);
  let inspector = "";
  if (sel) {
    let resolved = null;
    try { resolved = await api(`/tenancy/resolve/${sel.id}?key=${encodeURIComponent(tnKey)}`); } catch (e) { }
    const chain = (resolved && resolved.chain) || [];
    inspector = `<div class="p-panel" style="margin-top:16px">
      <div class="p-head"><b>${TN_ICON[sel.kind] || "▪️"} ${esc(sel.name)}</b><span class="p-sub">configuration cascade — deepest wins</span></div>
      <div class="p-form" style="grid-template-columns:1fr 2fr auto;align-items:end">
        <label>Key<input id="tnKeyIn" value="${esc(tnKey)}" placeholder="e.g. checkout.defaultCurrency"></label>
        <label>Value (JSON)<input id="tnValIn" placeholder='{"currency":"USD"}'></label>
        <button class="p-btn primary" data-act="tn-cfg-set" data-id="${sel.id}">Set on this node</button>
      </div>
      <div class="p-scroll-x" style="margin-top:12px"><table class="p-table"><thead><tr><th>Node</th><th>Kind</th><th>Own value for “${esc(tnKey || "all config")}”</th></tr></thead>
        <tbody>${chain.map(c => `<tr><td><code>${esc(c.path)}</code></td><td>${esc(c.kind)}</td><td><code>${esc(c.value == null || (typeof c.value === "object" && !Object.keys(c.value).length) ? "—" : JSON.stringify(c.value))}</code></td></tr>`).join("") || '<tr><td colspan="3" class="p-empty">no config set on the chain</td></tr>'}</tbody></table></div>
      ${tnKey ? `<div class="p-note">Resolved <b>${esc(tnKey)}</b> → <code>${esc(JSON.stringify(resolved && resolved.resolved))}</code></div>` : ""}
    </div>`;
  }
  const newForm = `<div class="p-modal"><div class="p-modal-box"><div class="p-modal-head"><h3>New node</h3><button data-mclose>✕</button></div>
    <div class="p-form">
      <label>Parent<select id="tnParent">${nodes.map(n => `<option value="${n.id}">${esc(n.path)}</option>`).join("")}</select></label>
      <label>Kind<select id="tnKind">${kinds.map(k => `<option value="${k}">${k}</option>`).join("")}</select></label>
      <label>Name<input id="tnName" placeholder="e.g. North America"></label>
    </div>
    <div style="margin-top:14px;text-align:right"><button class="p-btn primary" data-act="tn-create">Create node</button></div></div></div>`;
  return `<div class="p-panel">
      <div style="display:flex;gap:10px;align-items:center;margin-bottom:14px">
        <span class="p-tag">${nodes.length} node${nodes.length === 1 ? "" : "s"}</span><span style="flex:1"></span>
        <button class="p-btn primary sm" data-act="tn-new">+ New node</button></div>
      <div class="tn-tree">${treeHtml}</div>
    </div>${inspector}
    <div id="tnModalHost" class="hidden">${newForm}</div>`;
}

async function render() {
  shell('<div class="p-empty">Loading…</div>');
  const body = $("#vBody");
  try {
    if (view !== "dash" && !canSee(view)) { body.innerHTML = `<div class="p-empty">🔒 Your role (<b>${esc((A.user && A.user.staff_role) || "admin")}</b>) does not grant access to “${esc(view)}”.</div>`; return; }
    if (view === "dash") body.innerHTML = await vDash();
    else if (view === "products") body.innerHTML = await entityTable("product");
    else if (view === "gcatalog") { body.innerHTML = await vGcatalog(); wireGcatalog(); }
    else if (view === "skus") body.innerHTML = await entityTable("sku") + await entityTable("inventory") + await entityTable("warehouse") + await entityTable("variant_group");
    else if (view === "orders") body.innerHTML = await entityTable("order", { rowExtra: r => ["processing", "shipped"].includes(r.status) ? `<button class="p-btn sm primary" data-act="ship-order" data-id="${esc(r.id)}" data-num="${esc(r.num)}">${r.status === "shipped" ? "Label" : "Ship"}</button>` : "" });
    else if (view === "returns") body.innerHTML = await entityTable("ret");
    else if (view === "rfqs") body.innerHTML = await entityTable("rfq");
    else if (view === "sellers") body.innerHTML = await entityTable("seller");
    else if (view === "settlements") body.innerHTML = await entityTable("settlement");
    else if (view === "contracts") { body.innerHTML = await vContracts(); wireContracts(); }
    else if (view === "tenders") { body.innerHTML = await vTenders(); wireTenders(); }
    else if (view === "suppliers") body.innerHTML = await entityTable("supplier") + await entityTable("product_supplier");
    else if (view === "serialized") { body.innerHTML = await vSerialized(); wireSerialized(); }
    else if (view === "compliance") body.innerHTML = await entityTable("compliance");
    else if (view === "structure") body.innerHTML = await renderStructure();
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
    else if (view === "brands") body.innerHTML = await entityTable("brand");
    else if (view === "attributes") body.innerHTML = await entityTable("attribute");
    else if (view === "payments") { body.innerHTML = await vPayments(); wirePayments(); }
    else if (view === "settings") { body.innerHTML = await vSettings(); wireSettings(); }
    else if (view === "billing") body.innerHTML = await vBilling();
    else if (view === "modules") { body.innerHTML = await vModules(); }
    else if (view === "audit") { body.innerHTML = await vAudit(); wireAudit(); }
    else if (view === "marketplace") body.innerHTML = await vMarketplace();
    else if (view === "ugc") body.innerHTML = await vUgc();
    else if (view === "qcops") { body.innerHTML = await vQcOps(); wireQcOps(); }
    else if (view === "finops") { body.innerHTML = await vFinOps(); wireFinOps(); }
    else if (view === "mktops") { body.innerHTML = await vMktOps(); wireMktOps(); }
    else if (view === "tradeops") { body.innerHTML = await vTradeOps(); wireTradeOps(); }
    else if (view === "helpdesk") { body.innerHTML = await vHelpdesk(); wireHelpdesk(); } else if (view === "affiliate") renderAffiliate(); else if (view === "sitemap") renderSitemap(); else if (view === "shipping") renderShipping();
    else if (view === "retention") body.innerHTML = await vRetention();
    else if (view === "risk") body.innerHTML = await vRisk();
    else if (view === "experiments") body.innerHTML = await vExperiments();
    else if (view === "planning") body.innerHTML = await vPlanning();
    else if (view === "rides") body.innerHTML = await vRides();
    else if (view === "fleet") body.innerHTML = await vFleet();
    else if (view === "ops_hr") body.innerHTML = await vOpsHR();
    else if (view === "ops_proc") body.innerHTML = await vOpsProc();
    else if (view === "ops_mfg") body.innerHTML = await vOpsMfg();
    else if (view === "ops_proj") body.innerHTML = await vOpsProj();
    else if (view === "finance") body.innerHTML = await vFinance();
    else if (view === "logistics") body.innerHTML = await vLogistics();
    else if (view === "search") body.innerHTML = await vSearch();
    else if (view === "monitor") body.innerHTML = await vMonitor();
    else if (view === "studio") { body.innerHTML = await vStudio(); wireStudio(); }
    else if (view === "analytics") body.innerHTML = await vAnalytics();
    else if (view === "manual") window.open("/docs/user-manual.html", "_blank");
    else if (view === "architecture") window.open("/docs/architecture.html", "_blank");
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
  /* the unified console (/console.html) loads this bundle inside its own scope and
     drives the views itself; a guest-loaded bundle must not paint #app or it would
     clobber the one shell. LX_GUEST is set by that console's bundle wrapper */
  if (typeof LX_GUEST !== "undefined" && LX_GUEST) return;
  try {
    const [sess, cfg] = await Promise.all([api("/session"), api("/config")]);
    TT = cfg;
    if (!sess.user || sess.user.role !== "admin") {
      /* the platform console hands over here with ?token= (Stores → Catalogs →
         impersonate). The token is single-use and scoped to this store; redeeming
         it promotes this session to that store's admin without a password. */
      const t = new URLSearchParams(location.search).get("token");
      if (t) {
        try {
          const r = await api("/auth/token-exchange", "POST", { token: t });
          if (r.ok) { boot(); return; }
        } catch (e) { /* expired or issued for another store → fall through to the form */ }
      }
      const already = sess.user ? `<p class="m-help">Signed in as <b>${esc(sess.user.email)}</b> — a customer account, not a store admin. <a href="#" id="swAcct">Sign out</a></p>` : "";
      $("#app").innerHTML = `<div class="p-login"><div class="p-login-box"><h1>LUXORA</h1><p>Store Console</p>${already}
        <form id="lf" class="p-form"><label><span>Email</span><input id="le" type="email" required></label>
        <label><span>Password</span><input id="lp" type="password" required></label>
        <button class="p-btn primary" style="width:100%">Sign in</button></form>
        <p class="p-err hidden" id="lfErr" style="color:var(--p-red);font-size:13px;margin:10px 0 0"></p>
        <p class="hint" id="lfHint"></p>
        <p class="hint"><a href="/reset.html${TT ? "?store=" + encodeURIComponent(TT.tenant.slug) : ""}">Forgot your password?</a></p>
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

async function vDocs() {
  return `<div class="a-head">
    <h2>📄 Architecture & User Manual</h2>
    <p class="a-sub">Documentation for LUXORA Platform</p>
  </div>
  <div class="a-card">
    <h3>📘 User Manual</h3>
    <p>Complete guide for store administrators, customers, and platform operations.</p>
    <p><a href="/docs/user-manual.html" target="_blank">View User Manual</a></p>
    
    <h3>🏛️ Architecture Documentation</h3>
    <p>Technical architecture, schema, data models, and integration specs.</p>
    <p><a href="/docs/architecture.html" target="_blank">View Architecture</a></p>
    
    <h3>📚 Quick Links</h3>
    <ul>
      <li><a href="/GOIP-ROADMAP-2.md" target="_blank">GOIP Value Exchange Roadmap</a></li>
      <li><a href="/README.md" target="_blank">README</a></li>
      <li><a href="/USER_MANUAL.md" target="_blank">Full Manual (Source)</a></li>
    </ul>
  </div>
  <div class="a-card">
    <h3>🔗 Admin API Reference</h3>
    <p>Key endpoints for store administration.</p>
    <ul>
      <li><code>POST /admin/product</code> - Create product</li>
      <li><code>GET /admin/orders</code> - List orders</li>
      <li><code>GET /goip</code> - GOIP manifest</li>
    </ul>
  </div>`;
}

function wireDocs() {
  // Add click handlers if needed
}
/* ========== NEW MODULES - Affiliate, Sitemap, Shipping, Helpdesk ========== */

/* ========== Affiliate Network UI ========== */
function renderAffiliate() {
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
  const body = $("#vBody");
  if (body) body.innerHTML = html;
  else { const a = $("#app"); if (a) a.innerHTML += html; }
  const add = $("#affAdd"); if (add) add.onclick = () => createAffiliateModal();
  loadAffiliateStats();
  loadAffiliates();
}

async function loadAffiliateStats() {
  try {
    const res = await api("/affiliate/reports");
    const s = res.summary || {};
    /* $() returns the element; $$() returns an ARRAY — writing .innerHTML onto the array
       was a silent no-op, so the stats fetched here never painted at all */
    $("#affiliateStats").innerHTML = `
      <div class="stat">
        <div class="stat-num">${s.affiliates || 0}</div>
        <div class="stat-label">Affiliates</div>
      </div>
      <div class="stat">
        <div class="stat-num">$${(s.sales || 0).toLocaleString()}</div>
        <div class="stat-label">Total Sales</div>
      </div>
      <div class="stat">
        <div class="stat-num">$${(s.commissions || 0).toLocaleString()}</div>
        <div class="stat-label">Total Commissions</div>
      </div>
    `;
  } catch (e) { console.error(e); }
}

async function loadAffiliates() {
  try {
    const res = await api("/affiliate/affiliates");
    const list = $("#affiliateList");
    if (!res.affiliates?.length) {
      list.innerHTML = `<p class="a-sub">No affiliates yet. Add one to start tracking referrals.</p>`;
      return;
    }
    let html = `<div class="a-table"><thead><tr>
      <th>Name</th><th>Code</th><th>Status</th><th>Sales</th><th>Commissions</th>
    </tr></thead><tbody>`;
    res.affiliates.forEach(a => {
      html += `<tr>
        <td>${esc(a.name)}</td>
        <td><code>${esc(a.affiliate_code)}</code></td>
        <td><span class="stat-badge ${a.status}">${esc(a.status)}</span></td>
        <td>$${(a.lifetime_sales || 0).toLocaleString()}</td>
        <td>$${(a.lifetime_commissions || 0).toLocaleString()}</td>
      </tr>`;
    });
    html += `</tbody></div>`;
    list.innerHTML = html;
  } catch (e) { console.error(e); }
}

function createAffiliateModal() {
  const m = $("#modal");
  m.innerHTML = `
    <h3>Add Affiliate</h3>
    <form class="p-form">
      <label><span>Name</span><input type="text" id="affName" required></label>
      <label><span>Email</span><input type="email" id="affEmail"></label>
      <label><span>Tier</span>
        <select id="affTier">
          <option value="standard">Standard</option>
          <option value="gold">Gold</option>
          <option value="platinum">Platinum</option>
        </select>
      </label>
      <button class="p-btn primary">Create</button>
    </form>
  `;
  m.classList.remove("hidden");
  $("#affName").focus();
}

/* ========== Sitemap/SEO UI ========== */
function renderSitemap() {
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
  const body = $("#vBody");
  if (body) body.innerHTML = html;
  else { const a = $("#app"); if (a) a.innerHTML += html; }
  const g = $("#smGen"); if (g) g.onclick = () => generateSitemap();
  loadSitemapConfig();
}

async function loadSitemapConfig() {
  try {
    const res = await api("/sitemap/config");
    const c = res.config || {};
    $("#sitemapConfig").innerHTML = `
      <div class="p-form">
        <label><span>Hostname</span><input type="text" id="sitemapHost" value="${esc(c.hostname || "")}" style="width:300px"></label>
        <label><span>Max entries per file</span>
          <select id="sitemapMax">
            <option value="50000" ${c.max_per_file == 50000 ? "selected" : ""}>50,000</option>
            <option value="10000" ${c.max_per_file == 10000 ? "selected" : ""}>10,000</option>
          </select>
        </label>
        <button class="p-btn" id="sitemapSave">Save</button>
      </div>
    `;
    $("#sitemapSave").onclick = saveSitemapConfig;
    $("#sitemapLast").innerHTML = `<p>Sitemap generated: <code>${esc(c.last_generated || "Never")}</code></p>`;
  } catch (e) { console.error(e); }
}

async function saveSitemapConfig() {
  const hostname = $("#sitemapHost").value;
  const maxPerFile = parseInt($("#sitemapMax").value);
  const r = await api("/sitemap/config", "PUT", { hostname, max_per_file: maxPerFile });
  if (r && r.error) return toast("❌ " + r.error);
  toast("Sitemap config saved");
  loadSitemapConfig();
}

async function generateSitemap() {
  toast("Generating sitemap...");
  const res = await api("/sitemap/generate", "POST");
  if (res.ok) {
    toast("✅ Sitemap generated (" + res.entries + " URLs) — served at /api/sitemap.xml");
    loadSitemapConfig();
  } else {
    toast("❌ Error generating sitemap");
  }
}

/* ========== Shipping & Tracking UI ========== */
/* the carrier account is platform-wide (Platform → Provider Registry); what a store sets is
   its own ship-from address, the origin of every rate and label it buys */
function renderShipping() {
  const html = `
    <div class="a-head">
      <h2>📦 Shipping & Tracking</h2>
      <p class="a-sub">Carrier rates and labels, your ship-from address, and parcel tracking</p>
    </div>
    <div class="a-card">
      <h3>Carrier account</h3>
      <div id="shippingProviders"></div>
    </div>
    <div class="a-card">
      <h3>Ship-from address</h3>
      <p class="a-sub">Where your parcels leave from. Carriers price every rate from this address.</p>
      <div id="shipFrom"></div>
    </div>
    <div class="a-card">
      <h3>Track Shipment</h3>
      <p class="a-sub">Enter tracking number to see real-time status</p>
      <div class="p-form">
        <input type="text" id="trackNumber" placeholder="Tracking number" style="flex:1">
        <button class="p-btn" id="shTrack">Track</button>
      </div>
      <div id="trackResult"></div>
    </div>
  `;
  const body = $("#vBody");
  if (body) body.innerHTML = html;
  else { const a = $("#app"); if (a) a.innerHTML += html; }
  const tr = $("#shTrack"); if (tr) tr.onclick = () => trackShipment();
  loadShippingProviders();
  loadShipFrom();
}

async function loadShippingProviders() {
  const list = $("#shippingProviders");
  try {
    const res = await api("/shipping/providers");
    if (!res.providers?.length) {
      list.innerHTML = `<p class="a-sub">No carrier is connected yet. A platform admin connects EasyPost in <b>Platform console → Platform → Extension → 🔌 Provider Registry</b>. Until then, orders ship at your flat shipping fee and labels are bought outside LUXORA.</p>`;
      return;
    }
    list.innerHTML = `<div class="a-tablewrap"><table class="a-table"><thead><tr><th>Provider</th><th>Type</th><th>Status</th></tr></thead><tbody>${
      res.providers.map(p => `<tr><td>${esc(p.name)}</td><td><code>${esc(p.carrier_type)}</code></td><td><span class="badge ${esc(p.status)}">${p.status === "active" ? "connected" : esc(p.status)}</span></td></tr>`).join("")
    }</tbody></table></div>`;
  } catch (e) { list.innerHTML = `<p class="a-sub">${esc(e.message)}</p>`; }
}

async function loadShipFrom() {
  const box = $("#shipFrom");
  if (!box) return;
  let st;
  try { st = (await api("/admin/settings")).settings; }
  catch (e) { box.innerHTML = `<p class="a-sub">Only a store admin with Settings access can change the ship-from address.</p>`; return; }
  const a = (st.commerce && st.commerce.shipFrom) || {};
  const f = (k, label, ph) => `<label><span>${label}</span><input data-sf="${k}" value="${esc(a[k] || "")}" placeholder="${esc(ph || "")}"></label>`;
  box.innerHTML = `<div class="p-form">
    <div class="row">${f("name", "Contact name")}${f("company", "Company")}</div>
    <div class="row">${f("street1", "Street *")}${f("street2", "Apt, suite, unit")}</div>
    <div class="row3">${f("city", "City *")}${f("state", "State / region")}${f("zip", "Postal code *")}</div>
    <div class="row3">${f("country", "Country * (2 letters)", (st.commerce && st.commerce.country) || "US")}${f("phone", "Phone")}${f("email", "Email")}</div>
    <div style="display:flex;gap:8px"><button class="p-btn primary" id="sfSave">Save address</button>
    ${a.street1 ? '<button class="p-btn" id="sfClear">Remove address</button>' : ""}</div></div>`;
  $("#sfSave").onclick = async () => {
    const addr = {};
    box.querySelectorAll("[data-sf]").forEach(i => { addr[i.dataset.sf] = i.value.trim(); });
    if (!addr.country) addr.country = (st.commerce && st.commerce.country) || "US";
    try { await api("/admin/settings", "PUT", { commerce: { shipFrom: addr } }); toast("Ship-from address saved"); loadShipFrom(); }
    catch (e) { toast(e.message); }
  };
  const clr = $("#sfClear");
  if (clr) clr.onclick = async () => {
    if (!confirm("Remove the ship-from address? Carrier rates need one.")) return;
    try { await api("/admin/settings", "PUT", { commerce: { shipFrom: null } }); toast("Ship-from address removed"); loadShipFrom(); }
    catch (e) { toast(e.message); }
  };
}

async function trackShipment() {
  const number = $("#trackNumber").value;
  if (!number) return toast("Enter tracking number");
  try {
    const res = await api("/shipping/track/" + encodeURIComponent(number));
    if (res.tracking) {
      $("#trackResult").innerHTML = `
        <div class="a-table">
          <p><strong>Status:</strong> ${esc(res.tracking.status)}</p>
          <p><strong>Estimated Delivery:</strong> ${esc(res.tracking.estimated_delivery || "Unknown")}</p>
        </div>
      `;
    } else {
      toast("No tracking found for this number");
    }
  } catch (e) {
    toast("Error tracking shipment");
  }
}

/* ========== Helpdesk UI ========== */
function renderHelpdesk() {
  const html = `
    <div class="a-head">
      <h2>💬 Customer Support</h2>
      <p class="a-sub">Tickets, live chat, SMS support</p>
    </div>
    <div class="a-card">
      <h3>Active Tickets</h3>
      <div id="helpdeskTickets"></div>
    </div>
    <div class="a-card">
      <h3>Live Chat Status</h3>
      <div id="chatStatus"></div>
    </div>
  `;
  /* a view renders INTO #vBody like every other view — the old form wiped every .a-card
     and appended to #app, painting outside the shell and leaving the nav state stale */
  const body = $("#vBody");
  if (body) body.innerHTML = html;
  else { const a = $("#app"); if (a) a.innerHTML += html; }
  loadHelpdeskTickets();
  loadChatStatus();
}

async function loadHelpdeskTickets() {
  try {
    const res = await api("/admin/helpdesk/tickets");
    const list = $("#helpdeskTickets");
    if (!res.tickets?.length) {
      list.innerHTML = `<p class="a-sub">No tickets yet. Happy customers!</p>`;
      return;
    }
    let html = `<div class="a-table"><thead><tr>
      <th>Ref</th><th>Subject</th><th>Channel</th><th>Status</th><th>Priority</th>
    </tr></thead><tbody>`;
    res.tickets.forEach(t => {
      html += `<tr>
        <td><code>${esc(t.ref)}</code></td>
        <td>${esc(t.subject)}</td>
        <td><span class="stat-badge">${esc(t.channel || "email")}</span></td>
        <td><span class="stat-badge ${t.status}">${esc(t.status)}</span></td>
        <td><span class="stat-badge ${t.priority}">${esc(t.priority)}</span></td>
      </tr>`;
    });
    html += `</tbody></div>`;
    list.innerHTML = html;
  } catch (e) { console.error(e); }
}

async function loadChatStatus() {
  try {
    const res = await api("/helpdesk/agents/status");
    const status = $("#chatStatus");
    if (!res.agents?.length) {
      status.innerHTML = `<p class="a-sub">No agents configured yet.</p>`;
      return;
    }
    let html = `<div class="a-table"><thead><tr>
      <th>Agent</th><th>Status</th><th>Last Update</th>
    </tr></thead><tbody>`;
    res.agents.forEach(a => {
      html += `<tr>
        <td><code>${esc(a.agent_id)}</code></td>
        <td><span class="stat-badge ${a.status}">${esc(a.status)}</span></td>
        <td>${esc(a.updated_at)}</td>
      </tr>`;
    });
    html += `</tbody></div>`;
    status.innerHTML = html;
  } catch (e) { console.error(e); }
}

/* ========== E17 · the mobility universe (rides & dispatch · fleet) ==========
   The console renders only what lib/mobility.js answered: every fare, surge
   multiplier, ETA and cancellation fee was computed from the store's own capability
   params. No rate is hard-coded in this file. */
async function vRides() {
  const [d, caps] = await Promise.all([api("/admin/mobility", {}), coCaps()]);
  const surgeOn = !!((caps.find(c => c.key === "dynamic_pricing") || {}).on);
  const st = d.stats || {};
  const rides = d.rides || [];
  const active = rides.filter(r => !["completed", "cancelled"].includes(r.status));
  const done = rides.filter(r => ["completed", "cancelled"].includes(r.status));
  const NEXT = { requested: ["accepted", "Accept"], accepted: ["arrived", "Arrived"], arrived: ["trip_start", "Start trip"], trip_start: ["completed", "Complete"] };
  const chip = s => `<span class="a-chip">${esc(s)}</span>`;
  return `<div class="a-head"><h2>🚗 Rides &amp; Dispatch</h2><p class="a-sub">The ride lifecycle, surge pricing and live dispatch. Fares, cancellation fees and the platform commission are the store's own capability params — <code>ride_hailing</code> · <code>dynamic_pricing</code> · <code>dispatch</code> — and the legal transitions live in Data Studio (<code>mobilityTransitions</code>), so no rate or rule is hard-coded here.</p></div>
  <div class="a-cards">
    <div class="a-card"><h3>Live</h3>
      <div class="a-stats">${[["Rides", st.rides || 0], ["Active now", st.active || 0], ["Drivers online", st.drivers_online || 0], ["Gross revenue", (st.gross_revenue || 0).toFixed(2)], ["Avg rating", (st.avg_rating || 0).toFixed(1)]].map(([k, v]) => `<div><b>${v}</b><span>${k}</span></div>`).join("")}</div>
      <div style="margin-top:10px"><button class="btn-yellow" data-act="mob-new-ride">＋ Request a ride</button></div></div>
    <div class="a-card"><h3>Surge zones</h3>
      ${surgeOn ? `<div style="margin-bottom:8px"><button class="btn-yellow sm" data-act="mob-new-zone">＋ New zone</button></div>`
        : `<p class="p-tag">Switch on <code>dynamic_pricing</code> in ⚙️ Capabilities to raise a multiplier by zone.</p>`}
      <div class="a-tablewrap"><table class="a-table"><thead><tr><th>zone</th><th>kind</th><th>multiplier</th><th>radius</th><th>state</th>${surgeOn ? "<th></th>" : ""}</tr></thead>
      <tbody>${(d.zones || []).map(z => `<tr>
        <td>${esc(z.name)}</td><td>${esc(z.kind)}</td><td><b>×${(+z.multiplier).toFixed(2)}</b></td><td>${z.radius_km} km</td>
        <td>${chip(z.active ? "active" : "idle")}</td>
        ${surgeOn ? `<td style="white-space:nowrap">
          <button class="btn-white sm" data-act="mob-toggle-zone" data-id="${z.id}" data-on="${z.active ? 0 : 1}">${z.active ? "Pause" : "Resume"}</button>
          <button class="btn-white sm" data-act="mob-edit-zone" data-id="${z.id}">Edit</button></td>` : ""}
      </tr>`).join("") || `<tr><td colspan="${surgeOn ? 6 : 5}">No surge zones — every ride prices at ×1.</td></tr>`}</tbody></table></div></div>
  </div>
  <div class="a-card"><h3>Active rides (${active.length})</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>ref</th><th>rider</th><th>route</th><th>vehicle</th><th>driver</th><th>surge</th><th>eta</th><th>status</th><th></th></tr></thead>
    <tbody>${active.map(r => { const nx = NEXT[r.status]; return `<tr>
      <td><code>${esc(r.ref)}</code></td><td>${esc(r.rider || "—")}</td>
      <td>${esc(r.pickup)} → ${esc(r.dropoff)}</td><td>${chip(r.vehicle_kind)}</td>
      <td>${esc(r.driver_name || "unassigned")}</td>
      <td>${(+r.surge) > 1 ? `<b>×${(+r.surge).toFixed(2)}</b>` : "—"}</td>
      <td>${r.eta_min ? r.eta_min + " min" : "—"}</td><td>${chip(r.status)}</td>
      <td>${nx ? `<button class="btn-white sm" data-act="mob-next" data-id="${r.id}" data-to="${nx[0]}">${nx[1]}</button>` : ""}</td>
    </tr>`; }).join("") || `<tr><td colspan="9">No rides in flight — request one above.</td></tr>`}</tbody></table></div></div>
  <div class="a-card"><h3>Ride history</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>ref</th><th>rider</th><th>route</th><th>driver</th><th>distance</th><th>duration</th><th>fare</th><th>rating</th><th>status</th></tr></thead>
    <tbody>${done.map(r => `<tr>
      <td><code>${esc(r.ref)}</code></td><td>${esc(r.rider || "—")}</td>
      <td>${esc(r.pickup)} → ${esc(r.dropoff)}</td><td>${esc(r.driver_name || "—")}</td>
      <td>${(+r.distance_km).toFixed(1)} km</td><td>${(+r.duration_min).toFixed(0)} min</td>
      <td>${r.fare ? (+r.fare).toFixed(2) : "—"}</td><td>${r.rating || "—"}</td><td>${chip(r.status)}</td>
    </tr>`).join("") || `<tr><td colspan="9">No completed rides yet.</td></tr>`}</tbody></table></div></div>`;
}
/* a surge zone is authored as a form, not a prompt chain — eight values one question at a
   time would be unusable, and the engine's upsertZone validates exactly these fields.
   Editing re-sends the whole row: the upsert rewrites every column, so a partial body
   would silently flatten the multiplier and the coordinates back to their defaults. */
/* buy a carrier label for one order: the labels it already has come first (a parcel gets
   one label), then the parcel is weighed in, rated from the store's ship-from address, and
   one of the returned rates is bought. Buying marks a processing order shipped. */
async function shipModal(orderId, num) {
  const m = modal(`<div class="p-modal-head"><h3>Ship order ${esc(num || orderId)}</h3><button data-mclose>✕</button></div><div id="shipBody"><p class="a-sub">Loading…</p></div>`);
  const box = m.querySelector("#shipBody");
  m.querySelector("[data-mclose]").onclick = () => { m.innerHTML = ""; };
  const labelRow = l => `<tr><td>${esc(l.carrier || "")} ${esc(l.service || "")}</td><td><code>${esc(l.tracking_number)}</code></td><td><span class="badge ${esc(l.status)}">${esc(l.status)}</span></td><td>${/^https:\/\//.test(l.label_url || "") ? `<a href="${esc(l.label_url)}" target="_blank" rel="noopener">Print label ↗</a>` : ""}</td></tr>`;
  let existing = [];
  try { existing = (await api(`/shipping/orders/${encodeURIComponent(orderId)}/labels`)).labels || []; }
  catch (e) { box.innerHTML = `<p class="a-sub">${esc(e.message)}</p>`; return; }
  const form = () => {
    box.innerHTML = `${existing.length ? `<p class="a-sub">This order already has ${existing.length === 1 ? "a label" : existing.length + " labels"}:</p>
      <table class="p-table"><tbody>${existing.map(labelRow).join("")}</tbody></table>
      <p class="a-sub" style="margin-top:12px">Buy another only if the order ships in more than one parcel.</p>` : ""}
      <div class="p-form">
        <div class="row"><label><span>Weight (oz) *</span><input id="shW" type="number" min="0.1" step="0.1" placeholder="e.g. 18 (16 oz = 1 lb)"></label>
        <label><span>Length × width × height (in, optional)</span><span style="display:flex;gap:6px"><input id="shL" type="number" min="0" step="0.1" placeholder="L"><input id="shWd" type="number" min="0" step="0.1" placeholder="W"><input id="shH" type="number" min="0" step="0.1" placeholder="H"></span></label></div>
        <button class="p-btn primary" id="shRate">Get rates</button>
      </div><div id="shRates"></div>`;
    box.querySelector("#shRate").onclick = rate;
  };
  const rate = async () => {
    const weight = Number(box.querySelector("#shW").value);
    if (!(weight > 0)) return toast("Enter the parcel weight in ounces");
    const out = box.querySelector("#shRates");
    out.innerHTML = `<p class="a-sub">Asking the carriers…</p>`;
    let q;
    try { q = await api("/shipping/quote", "POST", { order_id: Number(orderId), parcel: { weight_oz: weight, length: Number(box.querySelector("#shL").value) || undefined, width: Number(box.querySelector("#shWd").value) || undefined, height: Number(box.querySelector("#shH").value) || undefined } }); }
    catch (e) { out.innerHTML = `<p class="a-sub">${esc(e.message)}${/ship-from/.test(e.message) ? ' — set it in <b>Shipping &amp; Tracking</b>.' : ""}</p>`; return; }
    if (!q.rates.length) { out.innerHTML = `<p class="a-sub">No carrier offered a rate for this parcel.${q.messages && q.messages.length ? " " + esc(q.messages.join(" · ")) : ""}</p>`; return; }
    out.innerHTML = `<table class="p-table" style="margin-top:12px"><thead><tr><th>Carrier</th><th>Service</th><th class="num">Days</th><th class="num">Price</th><th></th></tr></thead><tbody>${
      q.rates.map(x => `<tr><td>${esc(x.carrier)}</td><td>${esc(x.service)}</td><td class="num">${x.days == null ? "—" : esc(x.days)}</td><td class="num">${esc(x.price.toFixed(2))} ${esc(x.currency || "")}</td><td><button class="p-btn sm primary" data-buy="${esc(x.id)}">Buy label</button></td></tr>`).join("")
    }</tbody></table>`;
    out.querySelectorAll("[data-buy]").forEach(b => b.onclick = async () => {
      const x = q.rates.find(r => r.id === b.dataset.buy);
      if (!confirm(`Buy a ${x.carrier} ${x.service} label for ${x.price.toFixed(2)} ${x.currency || ""}? Your carrier account is charged.`)) return;
      out.querySelectorAll("[data-buy]").forEach(y => { y.disabled = true; });
      try {
        const l = await api("/shipping/label", "POST", { shipment_id: q.shipment_id, rate_id: x.id });
        box.innerHTML = `<p><b>Label bought.</b> The order is marked shipped, and a customer with an account is emailed the tracking number.</p>
          <table class="p-table"><tbody>${labelRow({ carrier: l.carrier, service: l.service, tracking_number: l.tracking_number, status: "pre_transit", label_url: l.label_url })}</tbody></table>`;
        toast("Label bought · " + l.tracking_number);
        render();
      } catch (e) { toast(e.message); out.querySelectorAll("[data-buy]").forEach(y => { y.disabled = false; }); }
    });
  };
  form();
}
function zoneModal(z) {
  const isEdit = !!z;
  const v = k => (z && z[k] != null) ? z[k] : "";
  const m = modal(`<div class="p-modal-head"><h3>${isEdit ? "Edit · " + esc(z.name) : "New surge zone"}</h3><button data-mclose>✕</button></div>
    <div class="p-form">
      <label><span>Name *</span><input id="znName" value="${esc(v("name"))}" placeholder="Airport surge"></label>
      <label><span>Kind</span><select id="znKind">${["geofence", "event", "weather"].map(k => `<option ${String(v("kind")) === k ? "selected" : ""}>${k}</option>`).join("")}</select></label>
      <label><span>Multiplier (never below 1)</span><input id="znMult" type="number" step="0.05" min="1" value="${v("multiplier") || 1.5}"></label>
      <label><span>Centre latitude</span><input id="znLat" type="number" step="any" value="${v("center_lat")}" placeholder="optional"></label>
      <label><span>Centre longitude</span><input id="znLng" type="number" step="any" value="${v("center_lng")}" placeholder="optional"></label>
      <label><span>Radius (km)</span><input id="znRad" type="number" step="0.1" min="0.1" value="${v("radius_km") || 3}"></label>
      <label class="checkbox-group"><input id="znActive" type="checkbox" ${!z || z.active ? "checked" : ""}> Active now</label>
      <label><span>Starts (optional)</span><input id="znStart" type="datetime-local" value="${esc(String(v("starts_at")).replace(" ", "T"))}"></label>
      <label><span>Ends (optional)</span><input id="znEnd" type="datetime-local" value="${esc(String(v("ends_at")).replace(" ", "T"))}"></label>
      <button class="p-btn primary" id="znSave">${isEdit ? "Save zone" : "Create zone"}</button>
    </div>`);
  m.querySelector("#znSave").onclick = async () => {
    const name = m.querySelector("#znName").value.trim();
    if (!name) return toast("Zone name is required");
    const body = {
      name,
      kind: m.querySelector("#znKind").value,
      multiplier: Number(m.querySelector("#znMult").value) || 1,
      center_lat: m.querySelector("#znLat").value,
      center_lng: m.querySelector("#znLng").value,
      radius_km: Number(m.querySelector("#znRad").value) || 3,
      active: m.querySelector("#znActive").checked
    };
    const st = m.querySelector("#znStart").value, en = m.querySelector("#znEnd").value;
    if (st) body.starts_at = st;
    if (en) body.ends_at = en;
    if (isEdit) body.id = z.id;
    try {
      const r = await api("/admin/mobility/zones", "POST", body);
      if (r.error) return toast(r.error);
      m.innerHTML = "";
      toast(isEdit ? "Zone updated" : `Zone ${r.zone.name} created · ×${(+r.zone.multiplier).toFixed(2)}`);
      render();
    } catch (e) { toast(e.message); }
  };
}
async function vFleet() {
  const d = await api("/admin/mobility", {});
  const st = d.stats || {};
  const chip = s => `<span class="a-chip">${esc(s)}</span>`;
  return `<div class="a-head"><h2>🚙 Fleet &amp; Drivers</h2><p class="a-sub">Driver onboarding, online state and the vehicle registry. Dispatch ranks candidates by rating then proximity, and a driver below the configured floor (<code>fleet_management · min_rating_to_dispatch</code>) is held out of matching. Vehicle kinds are the Data Studio list <code>mobilityVehicleKinds</code>.</p></div>
  <div class="a-cards">
    <div class="a-card"><h3>Fleet health</h3>
      <div class="a-stats">${[["Drivers", st.drivers || 0], ["Online", st.drivers_online || 0], ["Avg rating", (st.driver_avg_rating || 0).toFixed(2)], ["Completed", st.completed || 0], ["Cancelled", st.cancelled || 0]].map(([k, v]) => `<div><b>${v}</b><span>${k}</span></div>`).join("")}</div>
      <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap"><button class="btn-yellow" data-act="mob-new-driver">＋ Add driver</button><button class="btn-white" data-act="mob-new-vehicle">＋ Add vehicle</button></div></div>
    <div class="a-card"><h3>Vehicles</h3>
      <div class="a-tablewrap"><table class="a-table"><thead><tr><th>plate</th><th>kind</th><th>capacity</th><th>driver</th><th>odometer</th><th>insurance</th><th>status</th></tr></thead>
      <tbody>${(d.vehicles || []).map(v => `<tr><td><code>${esc(v.plate)}</code></td><td>${esc(v.kind)}</td><td>${v.capacity}</td>
      <td>${esc(v.driver_name || "—")}</td><td>${(+v.odometer).toFixed(0)} km</td><td>${esc(v.insurance_until || "—")}</td><td>${chip(v.status)}</td></tr>`).join("") || `<tr><td colspan="7">No vehicles registered.</td></tr>`}</tbody></table></div></div>
  </div>
  <div class="a-card"><h3>Drivers</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>name</th><th>city</th><th>vehicle</th><th>plate</th><th>rating</th><th>rides</th><th>earnings</th><th>state</th><th></th></tr></thead>
    <tbody>${(d.drivers || []).map(x => `<tr>
      <td>${esc(x.name)}${x.email ? `<div class="a-sub">${esc(x.email)}</div>` : ""}</td>
      <td>${esc(x.city || "—")}</td><td>${chip(x.vehicle_kind)}</td><td><code>${esc(x.plate || "—")}</code></td>
      <td>${(+x.rating).toFixed(2)}</td><td>${x.rides_completed}</td><td>${(+x.earnings).toFixed(2)}</td>
      <td>${chip(x.status)}</td>
      <td>${x.status === "suspended" ? "" : `<button class="btn-white sm" data-act="mob-toggle-driver" data-id="${x.id}" data-to="${x.status === "online" ? "0" : "1"}">${x.status === "online" ? "Go offline" : "Go online"}</button> <button class="btn-white sm" data-act="mob-deact-driver" data-id="${x.id}">Deactivate</button>`}
      ${x.deactivated_at ? `<span class="a-sub">since ${esc(x.deactivated_at)}</span>` : ""}</td>
    </tr>`).join("") || `<tr><td colspan="9">No drivers yet — add one above.</td></tr>`}</tbody></table></div></div>`;
}

/* ========== E18 · the operations universe (ERP · HRMS · procurement · manufacturing · projects)
   The console renders only what lib/operations.js answered: every tax rate, overtime
   multiple, approval threshold, yield and cost rate is a capability param, not a
   literal in this file. */
async function vOpsHR() {
  const d = await api("/admin/operations", {});
  const st = (d.stats || {}).payroll || {};
  const chip = s => `<span class="a-chip">${esc(s)}</span>`;
  return `<div class="a-head"><h2>🧑‍💼 People &amp; Payroll</h2><p class="a-sub">Employees, attendance and the payroll run. Overtime, allowances, deductions and tax are the store's own <code>workforce</code> params — a run is recomputed from them, never from a hard-coded rate. Attendance statuses and payroll statuses are Data Studio lists (<code>opsTaskStatuses</code> shape: editable, not code).</p></div>
  <div class="a-cards">
    <div class="a-card"><h3>Headcount</h3>
      <div class="a-stats">${[["Employees", st.employees || 0], ["Active", st.active_employees || 0], ["Payroll runs", st.runs || 0], ["Paid", st.paid_runs || 0], ["Last net", (st.last ? (+st.last.net).toFixed(0) : "—")]].map(([k, v]) => `<div><b>${v}</b><span>${k}</span></div>`).join("")}</div>
      <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap"><button class="btn-yellow" data-act="ops-new-employee">＋ Add employee</button><button class="btn-white" data-act="ops-payroll-run">▶ Run this month's payroll</button></div></div>
    <div class="a-card"><h3>Payroll runs</h3>
      <div class="a-tablewrap"><table class="a-table"><thead><tr><th>period</th><th>headcount</th><th>gross</th><th>deductions</th><th>net</th><th>status</th><th></th></tr></thead>
      <tbody>${(d.payroll || []).map(p => `<tr><td><code>${esc(p.period)}</code></td><td>${p.headcount}</td><td>${(+p.gross).toFixed(2)}</td><td>${(+p.deductions).toFixed(2)}</td><td><b>${(+p.net).toFixed(2)}</b></td><td>${chip(p.status)}</td>
      <td>${p.status !== "paid" ? `<button class="btn-white sm" data-act="ops-payroll-status" data-id="${p.id}" data-to="${p.status === "draft" ? "approved" : "paid"}">${p.status === "draft" ? "Approve" : "Mark paid"}</button>` : ""}</td></tr>`).join("") || `<tr><td colspan="7">No payroll runs yet.</td></tr>`}</tbody></table></div></div>
  </div>
  <div class="a-card"><h3>Employees</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>code</th><th>name</th><th>department</th><th>designation</th><th>salary</th><th>state</th></tr></thead>
    <tbody>${(d.employees || []).map(e => `<tr><td><code>${esc(e.code)}</code></td><td>${esc(e.name)}${e.email ? `<div class="a-sub">${esc(e.email)}</div>` : ""}</td><td>${esc(e.department || "—")}</td><td>${esc(e.designation || "—")}</td><td>${(+e.base_salary).toFixed(0)}</td><td>${chip(e.status)}</td></tr>`).join("") || `<tr><td colspan="6">No employees yet — add one above.</td></tr>`}</tbody></table></div></div>`;
}
async function vOpsProc() {
  const d = await api("/admin/operations", {});
  const chip = s => `<span class="a-chip">${esc(s)}</span>`;
  return `<div class="a-head"><h2>🛒 Procurement</h2><p class="a-sub">Purchase requests and their lines. A request above the store's configured <code>approval_threshold</code> cannot advance to approved without a sign-off — the gate is a param, not a policy written in code. Statuses are the Data Studio list <code>opsPrStatuses</code>.</p></div>
  <div class="a-cards">
    <div class="a-card"><h3>Requests</h3>
      <div class="a-stats">${[["Open", (d.stats || {}).procurement ? (d.stats.procurement.open || 0) : 0], ["Shown", (d.requests || []).length]].map(([k, v]) => `<div><b>${v}</b><span>${k}</span></div>`).join("")}</div>
      <div style="margin-top:10px"><button class="btn-yellow" data-act="ops-new-request">＋ New purchase request</button></div></div>
  </div>
  <div class="a-card"><h3>Purchase requests</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>ref</th><th>requested by</th><th>department</th><th>lines</th><th>est. cost</th><th>status</th><th></th></tr></thead>
    <tbody>${(d.requests || []).map(r => { const next = { draft: "submitted", submitted: "approved", approved: "ordered", ordered: "received" }[r.status]; return `<tr>
      <td><code>${esc(r.ref)}</code></td><td>${esc(r.requested_by || "—")}</td><td>${esc(r.department || "—")}</td>
      <td>${r.lines}</td><td>${(+r.est_cost).toFixed(2)}</td><td>${chip(r.status)}</td>
      <td>${next ? `<button class="btn-white sm" data-act="ops-pr-advance" data-id="${r.id}" data-to="${next}">→ ${next}</button>` : ""}</td>
    </tr>`; }).join("") || `<tr><td colspan="7">No purchase requests yet.</td></tr>`}</tbody></table></div></div>`;
}
async function vOpsMfg() {
  const d = await api("/admin/operations", {});
  const chip = s => `<span class="a-chip">${esc(s)}</span>`;
  return `<div class="a-head"><h2>🏭 Manufacturing</h2><p class="a-sub">Work orders and their bills of materials. Completion consumes the BOM and posts the finished good at the configured <code>yield_pct</code> with the configured <code>scrap_pct</code> loss — the yields are params, never guesses. Statuses are the Data Studio list <code>opsWoStatuses</code>.</p></div>
  <div class="a-cards">
    <div class="a-card"><h3>Work orders</h3>
      <div class="a-stats">${[["Open", (d.stats || {}).manufacturing ? (d.stats.manufacturing.open || 0) : 0], ["Shown", (d.workOrders || []).length]].map(([k, v]) => `<div><b>${v}</b><span>${k}</span></div>`).join("")}</div>
      <div style="margin-top:10px"><button class="btn-yellow" data-act="ops-new-wo">＋ New work order</button></div></div>
  </div>
  <div class="a-card"><h3>Work orders</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>ref</th><th>product</th><th>qty</th><th>completed</th><th>unit cost</th><th>status</th><th></th></tr></thead>
    <tbody>${(d.workOrders || []).map(w => `<tr>
      <td><code>${esc(w.ref)}</code></td><td>${esc(w.product_id || "—")}</td><td>${w.qty}</td><td>${w.completed_qty}</td>
      <td>${(+w.unit_cost).toFixed(2)}</td><td>${chip(w.status)}</td>
      <td>${w.status === "in_progress" ? `<button class="btn-white sm" data-act="ops-wo-complete" data-id="${w.id}">Complete</button>` : ""}</td>
    </tr>`).join("") || `<tr><td colspan="7">No work orders yet.</td></tr>`}</tbody></table></div></div>`;
}
async function vOpsProj() {
  const d = await api("/admin/operations", {});
  const chip = s => `<span class="a-chip">${esc(s)}</span>`;
  const st = (d.stats || {}).projects || {};
  return `<div class="a-head"><h2>📐 Projects &amp; Approvals</h2><p class="a-sub">Projects, tasks and the approval chain. Logged hours accrue to a project's spend at the configured <code>internal_cost_per_hour</code> — the rate is a param, so the same timesheet costs what the store says it costs. Approval kinds are the Data Studio list <code>opsApprovalKinds</code>.</p></div>
  <div class="a-cards">
    <div class="a-card"><h3>Portfolio</h3>
      <div class="a-stats">${[["Active projects", st.active || 0], ["Projects", (d.projects || []).length], ["Tasks", (d.tasks || []).length], ["Pending approvals", (d.approvals || []).filter(a => a.status === "pending").length]].map(([k, v]) => `<div><b>${v}</b><span>${k}</span></div>`).join("")}</div>
      <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap"><button class="btn-yellow" data-act="ops-new-project">＋ New project</button><button class="btn-white" data-act="ops-new-task">＋ New task</button></div></div>
    <div class="a-card"><h3>Approvals</h3>
      <div class="a-tablewrap"><table class="a-table"><thead><tr><th>kind</th><th>ref</th><th>requester</th><th>approver</th><th>status</th><th></th></tr></thead>
      <tbody>${(d.approvals || []).map(a => `<tr><td>${chip(a.kind)}</td><td><code>${esc(a.ref || a.ref_id)}</code></td><td>${esc(a.requester || "—")}</td><td>${esc(a.approver || "—")}</td><td>${chip(a.status)}</td>
      <td>${a.status === "pending" ? `<button class="btn-white sm" data-act="ops-appr" data-id="${a.id}" data-to="approved">Approve</button> <button class="btn-white sm" data-act="ops-appr" data-id="${a.id}" data-to="rejected">Reject</button>` : ""}</td></tr>`).join("") || `<tr><td colspan="6">No approvals pending.</td></tr>`}</tbody></table></div></div>
  </div>
  <div class="a-card"><h3>Projects</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>code</th><th>name</th><th>owner</th><th>budget</th><th>spent</th><th>tasks</th><th>status</th></tr></thead>
    <tbody>${(d.projects || []).map(p => `<tr><td><code>${esc(p.code)}</code></td><td>${esc(p.name)}</td><td>${esc(p.owner || "—")}</td><td>${(+p.budget).toFixed(0)}</td><td>${(+p.spent).toFixed(0)}</td><td>${p.tasks_done}/${p.tasks}</td><td>${chip(p.status)}</td></tr>`).join("") || `<tr><td colspan="7">No projects yet.</td></tr>`}</tbody></table></div></div>
  <div class="a-card"><h3>Tasks</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>title</th><th>project</th><th>assignee</th><th>est</th><th>logged</th><th>due</th><th>priority</th><th>status</th><th></th></tr></thead>
    <tbody>${(d.tasks || []).map(t => `<tr><td>${esc(t.title)}</td><td>${esc(t.project_code || "—")}</td><td>${esc(t.assignee || "—")}</td><td>${t.estimate_hours}h</td><td>${t.logged_hours}h</td><td>${esc(t.due_date || "—")}</td><td>${chip(t.priority)}</td><td>${chip(t.status)}</td>
    <td>${t.status !== "done" ? `<button class="btn-white sm" data-act="ops-task-done" data-id="${t.id}">Done</button> <button class="btn-white sm" data-act="ops-task-time" data-id="${t.id}">Log time</button>` : ""}</td></tr>`).join("") || `<tr><td colspan="9">No tasks yet.</td></tr>`}</tbody></table></div></div>`;
}

/* ========== Module Registration ========== */
window.renderAffiliate = renderAffiliate;
window.renderSitemap = renderSitemap;
window.renderShipping = renderShipping;
window.renderHelpdesk = renderHelpdesk;
window.generateSitemap = generateSitemap;
window.trackShipment = trackShipment;

