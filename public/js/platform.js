/* LUXORA Platform - super-admin console: tenants, plans, billing, providers, monitoring, audit */
"use strict";

const $ = s => document.querySelector(s);
const $$ = s => Array.from(document.querySelectorAll(s));
function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }
function __csrf() { const m = /(?:^|; )azc=([^;]+)/.exec(document.cookie || ""); return m ? m[1] : ""; }
async function api(path, method = "GET", body) {
  let url = "/api" + path;
  const opt = { method, headers: { "Content-Type": "application/json", "x-csrf": __csrf() }, credentials: "same-origin" };
  if (method === "GET" && body) {
    const params = new URLSearchParams(body);
    url += "?" + params.toString();
  } else if (body) {
    opt.body = JSON.stringify(body);
  }
  const r = await fetch(url, opt);
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
function toast(msg, type = "info") {
  const container = document.getElementById("toastContainer");
  if (!container) { const div = document.createElement("div"); div.id = "toastContainer"; document.body.appendChild(div); }
  const toast = document.createElement("div");
  toast.className = "toast " + (type === "error" ? "error" : "success");
  toast.textContent = msg;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
  let t = $("#ptoast");
  if (!t) { t = document.createElement("div"); t.id = "ptoast"; t.className = "p-toast"; document.body.appendChild(t); }
  t.innerHTML = `<div class="toast $type"><span>✅</span> </div>`; t.classList.add("show");
  clearTimeout(toastT); toastT = setTimeout(() => t.classList.remove("show"), 3200);
}
const NAV = [["dash", "◈ Command"], ["provisioning", "🛡️ Provisioning"], ["tenants", "🏬 Stores · Catalogs"], ["geo", "🌍 Geo · Countries · Taxes"], ["plans", "💼 Plans"], ["subs", "🔁 Subscriptions"],
["invoices", "🧾 Invoices"], ["billing", "💳 Billing Ops"], ["gproducts", "🌐 Global Products"], ["modules", "🧩 Module Marketplace"], ["providers", "🔌 Provider Registry"], ["ai", "🧠 AI · Providers & Plans"], ["ucii", "🌀 UCII Ω∞ Registry"], ["ucos", "♾️ UCOS Ω∞ Constitution"], ["studio", "🛠️ Data Studio"], ["definitions", "📐 Entities"], ["offers", "Ω∞ GOIP · Value Exchange"], ["runtime", "🧩 Runtime · Infra"], ["monitor", "📈 Monitoring"], ["audit", "📜 Global Audit"], ["identity", "🔐 Identity"], ["identity-templates", "📋 Identity Templates"], ["manual", "📘 User Manual"], ["architecture", "🏛️ Architecture"]];
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
  const { providerKinds } = await api("/meta");
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
    <h2 style="margin-top:18px">Register a new provider</h2>
    <p class="p-tag">Fill in the form below to register a provider. ID is auto-generated.</p>
    <div class="p-form">
      <div class="row"><label><span>Kind</span><select id="cpKind">${(providerKinds || []).map(k => `<option>${esc(k)}</option>`).join("")}</select></label>
      <label><span>ID (auto)</span><input id="cpId" placeholder="Auto-generated UUID" readonly style="background:var(--p-bg)"></label>
      <label><span>Name (required)</span><input id="cpName" placeholder="e.g. My Payment Gateway"></label>
      <label><span>Emoji</span><input id="cpEmoji" placeholder="🔌" value="🔌"></label></div>
      <div class="row"><label><span>Description</span><input id="cpDesc" placeholder="Short description of what this provider does"></label></div>
      <div class="row"><label><span>Countries</span><input id="cpCountries" placeholder="* for all, or comma-separated codes (e.g. US,IN,CN)"></label>
      <label><span>Fee %</span><input id="cpFeePct" type="number" step="0.1" value="0"></label>
      <label><span>Fee (fixed)</span><input id="cpFeeFixed" type="number" step="0.01" value="0"></label></div>
      <div class="row"><label><span>Methods</span><input id="cpMethods" placeholder="Comma-separated (e.g. card,upi,netbanking)"></label>
      <button class="p-btn sm" id="cpAddField">+ Add credential field</button></div>
      <div id="cpFieldsContainer"></div>
      <button class="p-btn primary" id="cpSave">Register provider</button>
      <div id="cpError" class="p-tag" style="display:none;background:var(--p-red);color:#fff"></div>
    </div></div>`;
}
 async function vUCII() {
  const [caps, domains, policies, workflows, configs, entityTypes] = await Promise.all([
    api("/ucii/capabilities"),
    api("/ucii/domains"),
    api("/ucii/policies"),
    api("/ucii/workflows"),
    api("/ucii/config", "GET", { scope: "platform" }),
    api("/meta/entity-def")
  ]);
  
  const configCategories = {
    'identity': ['sso', 'mfa', 'auth'],
    'commerce': ['product', 'cart', 'order', 'payment'],
    'integrations': ['payments', 'shipping', 'tax']
  };
  
  const configByCategory = Object.fromEntries(
    Object.entries(configCategories).map(([cat, keys]) => [
      cat, 
      configs.config ? Object.keys(configs.config).filter(k => keys.some(key => k.includes(key))) : []
    ])
  );
  
  return `
  <div class="p-panel"><h2>UCII Ω∞ Registry</h2>
    <p class="p-tag">Zero duplicates, zero overlapping, zero gaps through registry-first design.</p>
    
    <div style="margin-top:14px">
      <h3>🧩 Capabilities</h3>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;margin:8px 0">
        ${caps.capabilities.map(c => `
          <div class="p-card" style="padding:12px">
            <div style="display:flex;justify-content:space-between;align-items:center">
              <div>
                <b>${esc(c.name)}</b>
                <div class="p-tag" style="font-size:12px">${esc(c.category || 'uncategorized')}</div>
              </div>
              <span class="badge ${esc(c.status)}">${esc(c.status)}</span>
            </div>
          </div>
        `).join('') || '<p class="p-tag">No capabilities defined.</p>'}
      </div>
      <button class="p-btn sm" data-action="newCap">+ New Capability</button>
    </div>
    
    <div style="margin-top:14px">
      <h3>🌐 Domains</h3>
      <div style="display:flex;gap:10px;flex-wrap:wrap;margin:8px 0">
        ${domains.domains.map(d => `
          <div class="p-tag" style="padding:8px 12px"><b>${esc(d.name)}</b></div>
        `).join('') || '<p class="p-tag">No domains defined.</p>'}
      </div>
      <button class="p-btn sm" data-action="newDomain">+ New Domain</button>
    </div>
    
    <div style="margin-top:14px">
      <h3>📜 Configuration</h3>
      ${Object.entries(configByCategory).map(([cat, items]) => `
        <div style="margin:10px 0">
          <h4 style="margin:0 0 5px">${esc(cat)}</h4>
          <div style="display:flex;gap:8px;flex-wrap:wrap">
            ${items.map(k => `<div class="p-tag" style="font-size:12px">${esc(k)}</div>`).join('') || '<span class="p-tag">No config</span>'}
          </div>
        </div>
      `).join('')}
    </div>
    
    <div style="margin-top:14px">
      <h3>📋 Entity Schemas</h3>
      <div style="display:flex;gap:10px;flex-wrap:wrap;margin:8px 0">
        ${(entityTypes.rows || []).map(e => `
          <div class="p-tag" style="padding:8px 12px">
            <b>${esc(e.key)}</b>
            <div class="p-tag" style="font-size:12px">${e.isBuiltIn ? 'Built-in' : 'Custom'}</div>
          </div>
        `).join('') || '<p class="p-tag">No entity schemas.</p>'}
      </div>
    </div>
    
    <div style="margin-top:14px">
      <h3>⚙️ Workflows & Policies</h3>
      <div style="display:flex;gap:20px;margin:8px 0">
        <div>
          <div class="p-tag"><b>${workflows.workflows.length}</b> workflows</div>
          <button class="p-btn sm" data-action="newWorkflow">+ New</button>
        </div>
        <div>
          <div class="p-tag"><b>${policies.policies.length}</b> policies</div>
          <button class="p-btn sm" data-action="newPolicy">+ New</button>
        </div>
      </div>
    </div>
  </div>`;
}
 async function vStudio() {
  const tenants = await api("/platform/tenants");
  const { rows: entityDefs } = await api("/meta/entity-def");
  const entities = entityDefs.map(e => ({ ...e, ...JSON.parse(e.def || "{}") }));
  return `
  <div class="p-panel"><h2>Platform Data Studio</h2>
    <p class="p-tag">Browse all entity data across all stores.</p>
    <div style="margin:14px 0">
      <label><span>Store</span><select id="studioTenant">${tenants.tenants.map(t => `<option value="${t.id}">${esc(t.name)} (${esc(t.slug)})</option>`).join("")}</select></label>
      <label><span>Entity</span><select id="studioEntity">${entities.map(e => `<option value="${esc(e.key)}">${esc(e.label)}</option>`).join("")}</select></label>
      <button class="p-btn primary" id="studioLoad">Load</button>
    </div>
    <div id="studioBody"></div>
  </div>`;
}
 async function vDefinitions() {
  const data = await api("/meta/entity-def");
  const rows = data.rows || [];
  const defs = rows.map(e => ({ 
    ...e, 
    ...JSON.parse(e.def || "{}"),
    isBuiltIn: e.isBuiltIn
  }));
  const tenants = await api("/platform/tenants");
  return `
  <div class="p-panel"><h2>Global Entity Definitions</h2>
    <p class="p-tag">Built-in entities (read-only) + custom entities you define. Stores only use what Platform enables.</p>
    <div style="display:flex;gap:10px;margin-bottom:14px">
      <button class="p-btn primary" id="newDef">+ Define Custom Entity</button>
    </div>
    <div class="p-scroll-x">
      <table class="p-table">
         <thead><tr><th>Key</th><th>Label</th><th>Icon</th><th>Enabled For</th><th></th></tr></thead>
         <tbody>${defs.map(e => {
           const enabledTenants = (tenants.tenants || []).filter(t => t.custom_entities && t.custom_entities.includes(e.key));
           if (e.isBuiltIn) {
             return `<tr><td><b>${esc(e.key)}</b><span class="p-tag" style="margin-left:8px">Built-in</span></td><td>${esc(e.label)}</td><td>${esc(e.icon)}</td><td><span class="p-tag">N/A</span></td><td><span class="p-tag">Read-only</span></td></tr>`;
           }
           const allTenants = (tenants.tenants || []).map(t => ({
             ...t,
             enabled: enabledTenants.some(et => et.id === t.id)
           }));
           const toggleBtns = allTenants.map(t => 
             `<button class="p-btn sm ${t.enabled ? 'primary' : ''}" data-toggle-entity="${e.key}" data-tenant="${t.id}">${t.enabled ? '✕' : '+'}</button>`
           ).join(" ");
           return `<tr><td><b>${esc(e.key)}</b></td><td>${esc(e.label)}</td><td>${esc(e.icon)}</td><td>${enabledTenants.length > 0 ? enabledTenants.map(t => `<span class="badge">${esc(t.slug)}</span>`).join(" ") : '<span class="p-tag">None</span>'}</td><td>${toggleBtns} <button class="p-btn sm" data-edit="${e.key}">Edit</button></td></tr>`;
         }).join("")}</tbody>
      </table>
    </div>
    <div class="p-modal" id="defModal" style="display:none">
      <div class="p-modal-box">
        <h3 id="defTitle">Define Entity</h3>
        <div class="p-form">
          <div class="row">
            <label><span>Key</span><input id="defKey" placeholder="service_contract"></label>
            <label><span>Label</span><input id="defLabel" placeholder="Service Contracts"></label>
          </div>
          <label><span>Icon</span><input id="defIcon" placeholder="🧾"></label>
          <label><span>Fields (JSON array)</span><textarea id="defFields" rows="5">[
  {"key":"name","label":"Name","type":"text","required":true},
  {"key":"value","label":"Value","type":"money"}
]</textarea></label>
          <div style="display:flex;gap:10px;margin-top:8px">
            <button class="p-btn primary" id="saveDef">Save</button>
            <button class="p-btn" id="cancelDef">Cancel</button>
          </div>
        </div>
      </div>
    </div>
  </div>`;
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
/* ============ GLOBAL PRODUCTS: platform-level master catalog tenants subscribe to ============ */
let gpFilter = "";
async function vGproducts() {
  const { products } = await api("/platform/global-products" + (gpFilter ? ("?category=" + encodeURIComponent(gpFilter)) : ""));
  const cats = [...new Set(products.map(p => p.category).filter(Boolean))];
  return `
  <div class="p-panel"><div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;flex-wrap:wrap">
    <h2 style="margin:0">Global Products (${products.length})</h2>
    <select id="gpCat" style="padding:6px 10px;border:1px solid var(--p-border);border-radius:8px;background:var(--p-bg)">
      <option value="">All categories</option>${cats.map(c => `<option value="${esc(c)}" ${c === gpFilter ? "selected" : ""}>${esc(c)}</option>`).join("")}
    </select>
    <span style="flex:1"></span>
    <button class="p-btn primary sm" id="gpNew">+ New global product</button></div>
    <p style="margin:0 0 14px;color:var(--p-muted);font-size:13px">Platform-level master products. Stores subscribe to these via <b>Store Product Config</b> (permissions per store), so one catalog feeds every tenant.</p>
    <div class="p-scroll-x"><table class="p-table"><thead><tr><th>SKU</th><th>Name</th><th>Category</th><th class="num">Price</th><th>Tax class</th><th>Type</th><th>Status</th><th></th></tr></thead>
    <tbody>${products.map(p => `<tr><td><b>${esc(p.sku)}</b></td><td>${esc(p.name)}</td><td class="p-tag">${esc(p.category || "—")}</td>
      <td class="num">${money(p.price)}</td><td>${esc(p.tax_class)}</td><td>${p.is_service ? "Service" : "Physical"}</td>
      <td><span class="badge ${esc(p.status)}">${esc(p.status)}</span></td>
      <td style="white-space:nowrap"><button class="p-btn sm" data-gpedit="${p.id}">Edit</button>
        <button class="p-btn sm danger" data-gpdel="${p.id}">✕</button></td></tr>`).join("") || '<tr><td colspan="8" class="p-empty">No global products yet</td></tr>'}</tbody></table></div></div>`;
}
function wireGproducts() {
  const cat = document.getElementById("gpCat");
  if (cat) cat.onchange = () => { gpFilter = cat.value; render(); };
  document.getElementById("gpNew").onclick = () => gpModal(null);
  $$("[data-gpedit]").forEach(b => b.onclick = () => {
    api("/platform/global-products").then(({ products }) => {
      const p = products.find(x => String(x.id) === b.dataset.gpedit);
      if (p) gpModal(p);
    }).catch(e => toast(e.message));
  });
  $$("[data-gpdel]").forEach(b => b.onclick = async () => {
    if (!confirm("Delete this global product?")) return;
    try { await api("/platform/global-products/" + b.dataset.gpdel, "DELETE", {}); toast("Deleted"); render(); }
    catch (e) { toast(e.message); }
  });
}
function gpModal(p) {
  const isEdit = !!p;
  const attrs = isEdit ? JSON.stringify(p.attributes || {}, null, 0) : "{}";
  const media = isEdit ? JSON.stringify(p.media || [], null, 0) : "[]";
  const m = modal(`
    <h3 style="margin:0 0 14px">${isEdit ? "Edit" : "New"} global product</h3>
    <div class="p-form" style="display:grid;gap:10px">
      <label><span>SKU *</span><input id="gpSku" value="${esc(p ? p.sku : "")}" placeholder="e.g. GPU-001"></label>
      <label><span>Name *</span><input id="gpName" value="${esc(p ? p.name : "")}"></label>
      <label><span>Description</span><textarea id="gpDesc" rows="2">${esc(p ? p.description : "")}</textarea></label>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px">
        <label><span>Category</span><input id="gpCatIn" value="${esc(p ? p.category : "")}"></label>
        <label><span>Price</span><input id="gpPrice" type="number" step="0.01" min="0" value="${p ? p.price : 0}"></label>
        <label><span>Tax class</span><select id="gpTax">${["standard", "reduced", "zero", "exempt"].map(t => `<option value="${t}" ${p && p.tax_class === t ? "selected" : ""}>${t}</option>`).join("")}</select></label>
      </div>
      <label style="display:flex;align-items:center;gap:8px"><input type="checkbox" id="gpService" ${p && p.is_service ? "checked" : ""}> Is a service (not a physical good)</label>
      <label><span>Status</span><select id="gpStatus">${["draft", "active", "retired"].map(s => `<option value="${s}" ${p && p.status === s ? "selected" : ""}>${s}</option>`).join("")}</select></label>
      <label><span>Attributes (JSON)</span><textarea id="gpAttrs" rows="3" class="p-code">${esc(attrs)}</textarea></label>
      <label><span>Media (JSON array)</span><textarea id="gpMedia" rows="2" class="p-code">${esc(media)}</textarea></label>
      <div class="p-err hidden" id="gpErr" style="color:var(--p-red);font-size:13px"></div>
      <div style="display:flex;gap:10px;justify-content:flex-end">
        <button class="p-btn" id="gpCancel">Cancel</button>
        <button class="p-btn primary" id="gpSave">${isEdit ? "Save changes" : "Create product"}</button></div>
    </div>`);
  m.querySelector("#gpCancel").onclick = () => { m.innerHTML = ""; };
  m.querySelector("#gpSave").onclick = async () => {
    const err = m.querySelector("#gpErr");
    const val = id => m.querySelector(id).value;
    let parsedAttrs, parsedMedia;
    try { parsedAttrs = JSON.parse(val("#gpAttrs") || "{}"); } catch (e) { err.textContent = "Attributes must be valid JSON"; err.classList.remove("hidden"); return; }
    try { parsedMedia = JSON.parse(val("#gpMedia") || "[]"); } catch (e) { err.textContent = "Media must be a valid JSON array"; err.classList.remove("hidden"); return; }
    if (!val("#gpSku").trim() || !val("#gpName").trim()) { err.textContent = "SKU and name are required"; err.classList.remove("hidden"); return; }
    const body = { sku: val("#gpSku").trim(), name: val("#gpName").trim(), description: val("#gpDesc"), category: val("#gpCatIn").trim(),
      price: Number(val("#gpPrice")) || 0, tax_class: val("#gpTax"), is_service: m.querySelector("#gpService").checked,
      attributes: parsedAttrs, media: parsedMedia, status: val("#gpStatus") };
    try {
      if (isEdit) await api("/platform/global-products/" + p.id, "PUT", body);
      else await api("/platform/global-products", "POST", body);
      toast(isEdit ? "Product updated" : "Product created"); m.innerHTML = ""; render();
    } catch (e) { err.textContent = e.message; err.classList.remove("hidden"); }
  };
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
    const cpFields = [];
    function renderCpFields() {
      const container = $("#cpFieldsContainer");
      if (!container) return;
      container.innerHTML = cpFields.map((f, i) => `
        <div style="display:flex;gap:8px;align-items:flex-end;margin-top:8px">
          <input placeholder="Key" value="${esc(f.key)}" style="flex:1" data-cpfkey="${i}">
          <input placeholder="Label" value="${esc(f.label)}" style="flex:1" data-cpflabel="${i}">
          <label style="font-size:12px"><input type="checkbox" ${f.secret ? "checked" : ""} data-cpfsecret="${i}"> Secret</label>
          <button class="p-btn sm danger" data-cpfdel="${i}">✕</button>
        </div>`).join("");
      $$("[data-cpfdel]").forEach(b => b.onclick = () => { cpFields.splice(Number(b.dataset.cpfdel), 1); renderCpFields(); });
      $$("[data-cpfkey]").forEach(inp => inp.oninput = () => { cpFields[inp.dataset.cpfkey].key = inp.value; });
      $$("[data-cpflabel]").forEach(inp => inp.oninput = () => { cpFields[inp.dataset.cpflabel].label = inp.value; });
      $$("[data-cpfsecret]").forEach(inp => inp.onchange = () => { cpFields[inp.dataset.cpfsecret].secret = inp.checked; });
    }
    // UUID generator
    const uuid = () => crypto.randomUUID ? crypto.randomUUID() : ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g,c=>(c^crypto.getRandomValues(new Uint8Array(1))[0]&15>>c/4).toString(16));
    // Generate UUID for ID field
    if ($("#cpId")) $("#cpId").value = uuid();
    // Initialize with default field
    cpFields.push({key:"apiKey",label:"API Key",secret:true});
    renderCpFields();
    if ($("#cpAddField")) $("#cpAddField").onclick = () => { cpFields.push({key:"",label:"",secret:false}); renderCpFields(); };
    // Validate UUID
    const validateUUID = (id) => {
      if (!id) return { valid: false, error: "ID is required" };
      if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(id))
        return { valid: false, error: "ID must be a valid UUID format" };
      return { valid: true };
    };
    // Validate provider name
    const validateName = (name) => {
      if (!name) return { valid: false, error: "Name is required" };
      if (name.length < 3 || name.length > 100)
        return { valid: false, error: "Name must be 3-100 characters" };
      return { valid: true };
    };
    // Validate methods
    const validateMethods = (methods) => {
      if (!methods || methods.length === 0)
        return { valid: false, error: "At least one method is required" };
      for (let i = 0; i < methods.length; i++) {
        if (!/^[a-z0-9_]+$/.test(methods[i]))
          return { valid: false, error: `Method ${i+1} must be lowercase alphanumeric with underscores` };
        if (methods[i].length < 2 || methods[i].length > 50)
          return { valid: false, error: `Method ${i+1} must be 2-50 characters` };
      }
      return { valid: true };
    };
    // Validate credential fields
    const validateFields = (fields) => {
      if (fields.length === 0) return { valid: false, error: "At least one credential field is required" };
      const seenKeys = new Set();
      for (let i = 0; i < fields.length; i++) {
        const f = fields[i];
        if (!f.key) return { valid: false, error: `Field ${i+1} is missing key` };
        if (!f.label) return { valid: false, error: `Field ${i+1} is missing label` };
        if (!/^[a-zA-Z][a-zA-Z0-9]*$/.test(f.key))
          return { valid: false, error: `Field ${i+1} key must start with letter, alphanumeric only` };
        if (seenKeys.has(f.key))
          return { valid: false, error: `Duplicate field key: ${f.key}` };
        seenKeys.add(f.key);
      }
      return { valid: true };
    };
    if (e.target.id === "cpSave") {
      const kind = $("#cpKind").value;
      const id = $("#cpId").value.trim();
      const name = $("#cpName").value.trim();
      const emoji = $("#cpEmoji").value.trim() || "🔌";
      const desc = $("#cpDesc").value.trim();
      const countries = $("#cpCountries").value.trim() || "*";
      const feePct = parseFloat($("#cpFeePct").value) || 0;
      const feeFixed = parseFloat($("#cpFeeFixed").value) || 0;
      const methods = $("#cpMethods").value.split(",").map(s => s.trim()).filter(Boolean);
      const error = $("#cpError");
      // Validate
      const idVal = validateUUID(id);
      if (!idVal.valid) { error.textContent = idVal.error; error.style.display = "block"; return; }
      const nameVal = validateName(name);
      if (!nameVal.valid) { error.textContent = nameVal.error; error.style.display = "block"; return; }
      const methodsVal = validateMethods(methods);
      if (!methodsVal.valid) { error.textContent = methodsVal.error; error.style.display = "block"; return; }
      const fieldsVal = validateFields(cpFields.filter(f => f.key));
      if (!fieldsVal.valid) { error.textContent = fieldsVal.error; error.style.display = "block"; return; }
      error.style.display = "none";
      const manifest = {
        id, name, emoji, desc,
        countries: countries.split(",").map(s => s.trim()).filter(Boolean),
        methods,
        fields: cpFields.filter(f => f.key).map(f => ({key:f.key,label:f.label,secret:f.secret})),
        feePct, feeFixed
      };
      await api("/platform/custom-providers", "POST", { kind, manifest });
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
/* ═══ GOIP Ω∞ — GLOBAL OFFER INFRASTRUCTURE PLATFORM · platform control plane ═══
   Nine surfaces over one constitution: the 8-stage chain, the 22 capabilities (live-invokable),
   the 67 domains, the value-exchange register, every registry, funding→settlement→payout,
   attribution, intelligence and commercialization. Nothing here is hardcoded: every list is a
   meta_lists registry served by /api/goip, editable in Data Studio. */
let goipTab = "constitution";
const GOIP_TABS = [["constitution", "Ω Constitution"], ["capabilities", "⚡ Capabilities"], ["domains", "🌐 67 Domains"],
["exchanges", "💠 Value Exchanges"], ["registries", "📚 Registries"], ["funding", "🏦 Funding · Settlement"],
["attribution", "🔗 Attribution · Graph"], ["intelligence", "🧠 Intelligence"], ["commercial", "💳 Commercialization"]];
const GOIP = { manifest: null, platform: null };
function gTabs() { return `<div class="p-nav" style="display:flex;flex-wrap:wrap;gap:6px;margin:0 0 12px">${GOIP_TABS.map(([k, l]) => `<button class="p-btn sm ${goipTab === k ? "primary" : ""}" data-gt="${k}">${l}</button>`).join("")}</div>`; }
function pj(v, d) { try { return v ? JSON.parse(v) : (d || {}); } catch (e) { return d || {}; } }
function gRow(k, v) { return `<tr><td class="p-tag">${esc(k)}</td><td>${v}</td></tr>`; }
function gCount(n, label, ok) { return `<div class="p-stat"><em>${esc(label)}</em><b>${n}</b><small style="color:${ok === false ? "var(--p-red)" : "var(--p-muted)"}">${ok === false ? "gap" : "complete"}</small></div>`; }

async function vGlobalOffers() {
  const [m, d] = await Promise.all([api("/goip"), api("/platform/offers")]);
  GOIP.manifest = m; GOIP.platform = d;
  const c = m.coverage;
  const head = `<div class="p-panel"><h2>Ω∞ GOIP — GLOBAL OFFER INFRASTRUCTURE PLATFORM</h2>
    <p style="color:var(--p-muted);font-size:13px;margin:0 0 10px">${esc(m.subtitle)} — a constitutional platform for <b>any</b> incentive, offer, promotion, benefit, entitlement, subsidy, commission, loyalty construct or future value-exchange model, across any industry, organization, country, planet, economy, calendar, governance model or reality. Consumers call <b>capabilities</b>; they never learn the words coupon, cashback or gift card.</p>
    <div class="p-cards">
      ${gCount(c.capabilities.bound + "/" + c.capabilities.declared, "Capabilities bound", c.capabilities.gap.length === 0)}
      ${gCount(c.domains.declared, "Constitutional domains", c.domains.overlapping === 0)}
      ${gCount(c.benefits.handled + "/" + c.benefits.declared, "Benefits with math", c.benefits.gap.length === 0)}
      ${gCount(c.contexts.declared, "Context dimensions", true)}
      ${gCount(c.engines.declared, "Decision engines", true)}
      ${gCount(c.economic.units, "Economic units", true)}
    </div></div>`;
  return head + gTabs() + `<div id="goipBody">` + (await gView()) + `</div>`;
}
async function gView() {
  const m = GOIP.manifest, d = GOIP.platform;
  if (goipTab === "constitution") return gConstitution(m, d);
  if (goipTab === "capabilities") return gCapabilities(m);
  if (goipTab === "domains") return gDomains(m, d);
  if (goipTab === "exchanges") return gExchanges(m, d);
  if (goipTab === "registries") return gRegistries(m);
  if (goipTab === "funding") return gFunding(m, d);
  if (goipTab === "attribution") return await gAttribution(m, d);
  if (goipTab === "intelligence") return await gIntelligence(m);
  if (goipTab === "commercial") return gCommercial(m, d);
  return "";
}
function gConstitution(m, d) {
  const c = m.coverage;
  return `<div class="p-grid">
    <div class="p-card"><h3>The chain every value exchange walks</h3>
      <table class="p-table"><tbody>${m.constitution.map(x => `<tr><td><b>${x.step}. ${esc(x.name)}</b><div class="p-tag">${esc(x.question)}</div></td><td class="p-tag">owner <code>${esc(x.owner)}</code><br>engine <code>${esc(x.engine)}</code></td></tr>`).join("")}</tbody></table></div>
    <div class="p-card"><h3>Zero-gap scorecard</h3><table class="p-table"><tbody>
      ${gRow("Capabilities declared → bound", c.capabilities.bound + " / " + c.capabilities.declared + (c.capabilities.gap.length ? ' <span class="badge draft">' + esc(c.capabilities.gap.join(",")) + "</span>" : ' <span class="badge published">no gap</span>'))}
      ${gRow("Benefits declared → with math", c.benefits.handled + " / " + c.benefits.declared + (c.benefits.gap.length ? ' <span class="badge draft">' + esc(c.benefits.gap.join(",")) + "</span>" : ' <span class="badge published">no gap</span>'))}
      ${gRow("Domains → distinct owners", c.domains.declared + " / " + c.domains.distinct_owners + (c.domains.overlapping ? ' <span class="badge draft">' + c.domains.overlapping + " overlapping</span>" : ' <span class="badge published">zero overlap</span>'))}
      ${gRow("Intelligence implemented", c.intelligence.implemented + " / " + c.intelligence.declared)}
      ${gRow("Fabrics", Object.entries(c.fabrics).map(([k, v]) => `${esc(k)} <b>${v}</b>`).join(" · "))}
      ${gRow("Temporal", c.temporal.calendars + " calendars · " + c.temporal.chronologies + " chronologies · " + c.temporal.units + " units")}
      ${gRow("Spatial", c.spatial.systems + " systems · " + c.spatial.coordinate_systems + " coordinate systems · " + c.spatial.nodes + " nodes")}
      ${gRow("Economic · reality", c.economic.units + " units · " + c.economic.classes + " classes · " + c.reality.models + " reality models")}
      ${gRow("Graph", c.graph.nodes + " node kinds · " + c.graph.edges + " relationships")}
      ${gRow("Surfaces · protocols", c.experience.surfaces + " experience surfaces · " + c.access.protocols + " access protocols")}
      ${gRow("Commercial", c.commercial.deployments + " deployment models · " + c.commercial.billing_models + " billing models · " + c.commercial.meters + " meters")}
    </tbody></table></div></div>
    <div class="p-panel"><h3>Experience fabric</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>Surface</th><th>Bound to</th><th>State</th></tr></thead><tbody>
      ${m.experience.map(x => `<tr><td>${esc(x.name)}</td><td class="p-tag"><code>${esc(x.binding)}</code></td><td><span class="badge ${x.state === "live" ? "published" : "draft"}">${esc(x.state)}</span></td></tr>`).join("")}
    </tbody></table></div></div>
    <div class="p-panel"><h3>Universal access fabric</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>Protocol</th><th>Bound to</th><th>State</th></tr></thead><tbody>
      ${m.access.map(x => `<tr><td>${esc(x.name)}</td><td class="p-tag"><code>${esc(x.binding)}</code></td><td><span class="badge ${x.state === "live" ? "published" : "draft"}">${esc(x.state)}</span></td></tr>`).join("")}
    </tbody></table></div></div>`;
}
function gCapabilities(m) {
  return `<div class="p-panel"><h3>Universal capability layer — the only vocabulary a consumer needs</h3>
    <p class="p-tag">Every call is <code>POST /api/goip/&lt;capability&gt;</code>. Scope decides who may call it: <b>any</b> = a shopper session, <b>tenant</b> = store admin, <b>platform</b> = this console. Each capability writes exactly one store and bills exactly one meter.</p>
    <div class="p-scroll-x"><table class="p-table"><thead><tr><th>Capability</th><th>Stage</th><th>Engine</th><th>Writes</th><th>Meter</th><th>Scope</th><th></th></tr></thead><tbody>
      ${m.capabilities.map(c => `<tr><td><b>${esc(c.name)}</b><br><code>${esc(c.key)}</code></td><td class="p-tag">${esc(c.stage)}</td><td class="p-tag">${esc(c.engine)}</td><td class="p-tag">${esc(c.writes || "—")}</td><td class="p-tag">${esc(c.meter)}</td><td><span class="badge ${c.scope === "platform" ? "draft" : "published"}">${esc(c.scope)}</span></td>
        <td style="text-align:right"><button class="p-btn sm" data-gcap="${esc(c.key)}">invoke</button></td></tr>`).join("")}
    </tbody></table></div>
    <div class="p-panel" style="margin-top:10px"><h3>Capability console</h3>
      <div style="display:flex;gap:8px;align-items:end;flex-wrap:wrap">
        <label><span>Capability</span><select id="gcSel">${m.capabilities.map(c => `<option value="${esc(c.key)}">${esc(c.key)} — ${esc(c.name)}</option>`).join("")}</select></label>
        <button class="p-btn primary sm" id="gcRun">Invoke</button>
      </div>
      <label style="display:block;margin-top:8px"><span>Input (JSON)</span><textarea id="gcBody" rows="5" style="width:100%;font-family:ui-monospace,monospace;font-size:12px">{ "amount": 250 }</textarea></label>
      <pre id="gcOut" class="p-scroll-x" style="background:var(--p-bg2,#0b1020);color:#9ae6b4;padding:10px;border-radius:8px;max-height:320px;overflow:auto;font-size:12px">—</pre>
    </div>
    <div class="p-panel"><h3>Decision fabric — 18 engines, one job each</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>Engine</th><th>Owns</th><th>Implementation</th></tr></thead><tbody>
      ${m.engines.map(e => `<tr><td><b>${esc(e.name)}</b></td><td>${esc(e.owns)}</td><td class="p-tag"><code>${esc(e.impl)}</code></td></tr>`).join("")}
    </tbody></table></div></div>
    <div class="p-panel"><h3>Context fabric — 25 dimensions resolved on every decision</h3><div class="p-grid">
      ${m.contexts.map(x => `<div class="p-card" style="padding:8px 10px"><b>${esc(x.name)}</b><div class="p-tag">${esc(x.source)}</div></div>`).join("")}
    </div></div>`;
}
function gDomains(m, d) {
  const counts = {}; (d.domains || []).forEach(x => counts[x.domain] = x.n);
  return `<div class="p-panel"><h3>67 constitutional domains — each with exactly one owner and one discriminator</h3>
    <p class="p-tag">The discriminator is what makes overlap impossible: no two domains select the same rows from the same store. Live counts are value-exchange records currently in each domain.</p>
    <div class="p-scroll-x"><table class="p-table"><thead><tr><th>#</th><th>Domain</th><th>Owner (store)</th><th>Discriminator</th><th>Fabric</th><th class="num">Records</th></tr></thead><tbody>
      ${m.domains.map(x => `<tr><td class="p-tag">${String(x.n).padStart(2, "0")}</td><td><b>${esc(x.name)}</b><br><code>${esc(x.key)}</code></td><td class="p-tag"><code>${esc(x.owner)}</code></td><td style="font-size:12px">${esc(x.discriminator)}</td><td><span class="badge ${x.fabric === "capability" ? "published" : "draft"}">${esc(x.fabric)}</span></td><td class="num">${counts[x.key] || 0}</td></tr>`).join("")}
    </tbody></table></div></div>`;
}
function gExchanges(m, d) {
  const opt = (arrx, val) => (arrx || []).map(x => `<option value="${esc(x.key || x)}" ${val === (x.key || x) ? "selected" : ""}>${esc(x.name || x)}</option>`).join("");
  const benefits = m.benefits, domains = m.domains, units = m.economic.units, places = m.spatial.nodes, cals = m.temporal.calendars, dist = m.fabrics.distribution;
  return `<div class="p-panel"><h3>Publish a global value exchange</h3>
    <p class="p-tag">Scope = <b>global</b> — every store inherits it (bank cashbacks, brand vouchers, government subsidies, marketplace-wide sales, partner benefits). Stores honour global exchanges only while <b>Provisioning → global offers</b> allows it.</p>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:8px;align-items:end">
      <label><span>Name</span><input id="gName" placeholder="Platform-wide 2% credit"></label>
      <label><span>Benefit</span><select id="gBenefit">${opt(benefits, "percentage_discount")}</select></label>
      <label><span>Value</span><input id="gValue" type="number" step="0.01" value="10"></label>
      <label><span>Code (optional)</span><input id="gCode" placeholder="GLOBAL10"></label>
      <label><span>Domain</span><select id="gDomain">${opt(domains, "incentive")}</select></label>
      <label><span>Channel</span><select id="gChan"><option>commerce</option><option>subscription</option><option>ai</option><option>any</option></select></label>
      <label><span>Funder</span><select id="gFunder">${opt(m.fabrics.funding.filter(f => f.kind === "source").map(f => ({ key: f.party_type === "split" ? "split" : f.key, name: f.name })))}</select></label>
      <label><span>Funder ref</span><input id="gFunderRef" placeholder="HDFC / Nike / Ministry"></label>
      <label><span>Economic unit</span><select id="gUnit"><option value="">store currency</option>${opt(units)}</select></label>
      <label><span>Reality</span><select id="gReality">${opt(m.realities, "any")}</select></label>
      <label><span>Calendar</span><select id="gCal"><option value="">any</option>${opt(cals)}</select></label>
      <label><span>Place (prefix)</span><select id="gPlace"><option value="">anywhere</option>${opt(places)}</select></label>
      <label><span>Usage limit</span><input id="gUse" type="number" value="0"></label>
      <label><span>Governance</span><select id="gGov">${opt(m.governance_states.map(x => ({ key: x, name: x })), "published")}</select></label>
    </div>
    <label style="display:block;margin-top:8px"><span>Distribution channels</span>
      <div style="display:flex;flex-wrap:wrap;gap:8px">${dist.map(c => `<label style="display:flex;gap:4px;align-items:center;font-size:12px"><input type="checkbox" data-gdist="${esc(c.key)}"> ${esc(c.name)}</label>`).join("")}</div></label>
    <label style="display:block;margin-top:8px"><span>Declared conditions (JSON over the resolved context)</span><input id="gCond" placeholder='{ "audience.orders": { "gte": 1 }, "cart.amount": { "gte": 100 } }'></label>
    <label style="display:block;margin-top:8px"><span>Funding split (JSON, multi-party)</span><input id="gFund" placeholder='{ "parties": [{ "party": "HDFC", "party_type": "bank", "share": 0.6 }, { "party": "NIKE", "party_type": "brand", "share": 0.4 }] }'></label>
    <div style="margin-top:8px"><button class="p-btn primary sm" id="gSave">Publish value exchange</button> <span class="p-tag" id="gSaveMsg"></span></div>
  </div>
  <div class="p-panel"><h3>Global value exchanges</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>Name</th><th>Domain · Benefit</th><th>Context</th><th>Funder</th><th class="num">Value</th><th class="num">Used/Limit</th><th>State</th><th></th></tr></thead>
    <tbody>${(d.global || []).map(o => `<tr><td><b>${esc(o.name)}</b>${o.code ? ` <code>${esc(o.code)}</code>` : ""}${o.version > 1 ? ` <span class="p-tag">v${o.version}</span>` : ""}</td>
      <td class="p-tag">${esc(o.domain || "incentive")}<br>${esc(o.benefit || o.type)}</td>
      <td class="p-tag">${esc(o.reality || "any")} · ${esc((pj(o.spatial_spec).include || []).join(",") || "anywhere")} · ${esc(pj(o.temporal_spec).calendar || "any calendar")} · ${esc(o.economic_unit || o.currency)}</td>
      <td>${esc(o.funder)}${o.funder_ref ? " " + esc(o.funder_ref) : ""}</td><td class="num">${esc(o.value)}</td><td class="num">${o.used}/${o.usage_limit || "∞"}</td>
      <td><span class="badge ${(pj(o.governance).state || o.status) === "published" || o.status === "active" ? "published" : "draft"}">${esc(pj(o.governance).state || o.status)}</span></td>
      <td style="text-align:right;white-space:nowrap"><button class="p-btn sm" data-ggov="publish" data-gid="${o.id}">publish</button> <button class="p-btn sm" data-ggov="suspend" data-gid="${o.id}">suspend</button> <button class="p-btn sm" data-ggov="version" data-gid="${o.id}">version</button></td></tr>`).join("") || '<tr><td colspan="8">No global value exchanges yet.</td></tr>'}</tbody></table></div></div>
  <div class="p-panel"><h3>Benefit fabric — 25 constructs, one math engine</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>Benefit</th><th>Handler (offers.HANDLERS)</th><th>Direction</th><th>Unit</th><th>Grants</th></tr></thead><tbody>
    ${m.benefits.map(b => `<tr><td><b>${esc(b.name)}</b><br><code>${esc(b.key)}</code></td><td class="p-tag"><code>${esc(b.type)}</code></td><td>${esc(b.direction)}</td><td class="p-tag">${esc(b.unit || "—")}</td><td class="p-tag">${esc(b.grants || "—")}</td></tr>`).join("")}
  </tbody></table></div></div>`;
}
function gRegistries(m) {
  const tbl = (title, rows, cols) => `<div class="p-panel"><h3>${esc(title)}</h3><div class="p-scroll-x"><table class="p-table"><thead><tr>${cols.map(c => `<th>${esc(c[0])}</th>`).join("")}</tr></thead><tbody>${(rows || []).map(r => `<tr>${cols.map(c => `<td>${esc(typeof c[1] === "function" ? c[1](r) : r[c[1]])}</td>`).join("")}</tr>`).join("")}</tbody></table></div></div>`;
  return `<p class="p-tag">Every row below is a <code>meta_lists</code> registry — add a calendar, a planet, an economic unit, a benefit, a channel, an attribution model or an entire civilization in <b>Data Studio → Registries</b> and the engines obey it on the next request. No code, no redeploy, no redesign.</p>
  ${tbl("Temporal authority · calendars", m.temporal.calendars, [["Calendar", "name"], ["Key", "key"], ["Chronology", "chronology"], ["Epoch", "epoch"], ["Day (s)", "day_seconds"], ["Year (days)", "year_days"], ["Authority", "authority"]])}
  ${tbl("Chronologies", m.temporal.chronologies, [["Chronology", "name"], ["Base unit", "base_unit"], ["Rotation (s)", "rotation_seconds"]])}
  ${tbl("Temporal measurement", m.temporal.units, [["Unit", "name"], ["Key", "key"], ["Seconds", "seconds"]])}
  ${tbl("Spatial systems", m.spatial.systems, [["System", "name"], ["Body", "body"], ["Levels", r => (r.levels || []).join(" → ")], ["Coordinates", "coordinate"]])}
  ${tbl("Coordinate systems", m.spatial.coordinates, [["System", "name"], ["Axes", r => (r.axes || []).join(", ") || "—"], ["Unit", "unit"]])}
  ${tbl("Spatial hierarchy", m.spatial.nodes, [["Path", "key"], ["Name", "name"], ["System", "system"], ["Level", "level"], ["Parent", r => r.parent || "—"]])}
  ${tbl("Economic units", m.economic.units, [["Unit", "name"], ["Key", "key"], ["Class", "class"], ["Decimals", "decimals"], ["Rate → USD", r => r.base_rate || "declared"], ["Settleable", r => r.settleable ? "yes" : "no"]])}
  ${tbl("Reality models", m.realities, [["Reality", "name"], ["Key", "key"]])}
  ${tbl("Distribution fabric", m.fabrics.distribution, [["Channel", "name"], ["Bound to", "binding"], ["State", "state"]])}
  ${tbl("Attribution fabric", m.fabrics.attribution, [["Attribution", "name"], ["Basis", "basis"], ["Default model", "model"]])}
  ${tbl("Funding fabric", m.fabrics.funding, [["Funding", "name"], ["Party type", r => r.party_type || "—"], ["Kind", "kind"]])}
  ${tbl("Settlement fabric", m.fabrics.settlement, [["Element", "name"], ["Store", "store"], ["Stage", "stage"]])}
  ${tbl("Governance fabric", m.fabrics.governance, [["Engine", "name"], ["Action", "action"], ["Store", "store"]])}`;
}
function gFunding(m, d) {
  const t = d.treasury || { positions: [], burn: { monthly: [] } };
  const byFunder = (d.stats && d.stats.byFunder) || [];
  return `<div class="p-cards">
      ${(t.positions || []).map(p => `<div class="p-stat"><em>${esc(p.unit)} treasury</em><b>${p.available}</b><small>allocated ${p.allocated} · consumed ${p.consumed}</small></div>`).join("") || '<div class="p-stat"><em>Treasury</em><b>—</b><small>no budgets funded yet</small></div>'}
      <div class="p-stat"><em>Avg monthly burn</em><b>${money((t.burn && t.burn.average) || 0)}</b><small>last ${(t.burn && t.burn.monthly || []).length} periods</small></div>
    </div>
    <div class="p-panel"><h3>Fund a budget</h3>
      <div style="display:flex;gap:8px;align-items:end;flex-wrap:wrap">
        <label><span>Funder</span><select id="fFunder">${(m.fabrics.funding.filter(f => f.kind === "source")).map(f => `<option value="${esc(f.party_type === "split" ? "split" : f.key)}">${esc(f.name)}</option>`).join("")}</select></label>
        <label><span>Funder ref</span><input id="fRef" placeholder="HDFC"></label>
        <label><span>Unit</span><select id="fUnit">${m.economic.units.map(u => `<option value="${esc(u.key)}">${esc(u.key)}</option>`).join("")}</select></label>
        <label><span>Domain</span><select id="fDomain">${m.domains.map(x => `<option value="${esc(x.key)}" ${x.key === "incentive" ? "selected" : ""}>${esc(x.name)}</option>`).join("")}</select></label>
        <label><span>Amount</span><input id="fAmount" type="number" value="1000"></label>
        <button class="p-btn primary sm" id="fGo">Allocate</button>
      </div></div>
    <div class="p-panel"><h3>Budgets</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>Funder</th><th>Domain</th><th>Unit</th><th>Period</th><th class="num">Allocated</th><th class="num">Reserved</th><th class="num">Consumed</th><th class="num">Available</th><th class="num">Burn</th><th>Status</th></tr></thead><tbody>
      ${(d.budgets || []).map(b => `<tr><td>${esc(b.funder)}${b.funder_ref ? " " + esc(b.funder_ref) : ""}</td><td class="p-tag">${esc(b.domain)}</td><td>${esc(b.unit)}</td><td class="p-tag">${esc(b.period)}</td><td class="num">${b.allocated}</td><td class="num">${b.reserved}</td><td class="num">${b.consumed}</td><td class="num">${b.available}</td><td class="num">${b.burn_pct}%</td><td><span class="badge ${b.status === "open" ? "published" : "draft"}">${esc(b.status)}</span></td></tr>`).join("") || '<tr><td colspan="10">No budgets — allocate one above.</td></tr>'}
    </tbody></table></div></div>
    <div class="p-panel"><h3>Settlement &amp; payout</h3>
      <div style="display:flex;gap:8px;align-items:end;flex-wrap:wrap;margin-bottom:8px">
        <label><span>Period</span><input id="sPeriod" value="${esc(d.period || "")}" placeholder="YYYY-MM"></label>
        <button class="p-btn primary sm" id="sRun">Run settlement</button>
        <span class="p-tag">Each redeemed-but-unsettled redemption is attributed to its funding parties exactly once — re-running settles nothing twice.</span>
      </div>
      <div class="p-scroll-x"><table class="p-table"><thead><tr><th>Period</th><th>Party</th><th>Type</th><th>Unit</th><th class="num">Gross</th><th class="num">Fees</th><th class="num">Net</th><th class="num">Redemptions</th><th>Status</th><th></th></tr></thead><tbody>
        ${(d.settlements || []).map(x => `<tr><td class="p-tag">${esc(x.period)}</td><td><b>${esc(x.party)}</b></td><td class="p-tag">${esc(x.party_type)}</td><td>${esc(x.unit)}</td><td class="num">${x.gross}</td><td class="num">${x.fees}</td><td class="num">${x.net}</td><td class="num">${x.redemptions}</td><td><span class="badge ${x.status === "paid" || x.status === "reconciled" ? "published" : "draft"}">${esc(x.status)}</span>${x.reference ? `<br><code>${esc(x.reference)}</code>` : ""}</td>
          <td style="text-align:right;white-space:nowrap">${x.status === "accrued" ? `<button class="p-btn sm" data-sapprove="${x.id}" data-stenant="${x.tenant_id}">approve</button> ` : ""}${x.status === "accrued" || x.status === "approved" ? `<button class="p-btn sm primary" data-spay="${x.id}" data-stenant="${x.tenant_id}">pay</button>` : ""}${x.status === "paid" ? `<button class="p-btn sm" data-srec="${x.id}" data-stenant="${x.tenant_id}">reconcile</button>` : ""}</td></tr>`).join("") || '<tr><td colspan="10">Nothing accrued yet — run a settlement.</td></tr>'}
      </tbody></table></div></div>
    <div class="p-panel"><h3>Redemption split by funder (all stores)</h3>${byFunder.length ? `<table class="p-table"><thead><tr><th>Funder</th><th class="num">Value granted</th><th class="num">Redemptions</th></tr></thead><tbody>${byFunder.map(f => `<tr><td>${esc(f.funder)}</td><td class="num">${money(f.amount)}</td><td class="num">${f.redemptions}</td></tr>`).join("")}</tbody></table>` : '<p class="p-tag">No redemptions yet.</p>'}</div>`;
}
async function gAttribution(m, d) {
  let tp = { touchpoints: [] };
  try { tp = await api("/goip/touchpoints"); } catch (e) { }
  return `<div class="p-panel"><h3>Attribution fabric</h3>
    <p class="p-tag">Touchpoints are captured by <code>POST /api/goip/track</code> from any surface; <code>POST /api/goip/attribute</code> replays a subject's path through any declared model (${m.fabrics.attribution_models.join(", ")}) and splits revenue and commission across the parties that earned it.</p>
    <div style="display:flex;gap:8px;align-items:end;flex-wrap:wrap">
      <label><span>Subject (owner)</span><input id="aOwner" placeholder="t1:u:2"></label>
      <label><span>Model</span><select id="aModel">${m.fabrics.attribution_models.map(x => `<option>${esc(x)}</option>`).join("")}</select></label>
      <label><span>Revenue</span><input id="aValue" type="number" value="0"></label>
      <label><span>Commission %</span><input id="aRate" type="number" value="10"></label>
      <button class="p-btn primary sm" id="aRun">Attribute</button>
    </div>
    <pre id="aOut" class="p-scroll-x" style="background:var(--p-bg2,#0b1020);color:#9ae6b4;padding:10px;border-radius:8px;margin-top:8px;max-height:260px;overflow:auto;font-size:12px">—</pre>
  </div>
  <div class="p-panel"><h3>Recent touchpoints</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>When</th><th>Kind</th><th>Party</th><th>Channel</th><th>Subject</th><th class="num">Value</th></tr></thead><tbody>
    ${(tp.touchpoints || []).slice(-25).reverse().map(t => `<tr><td class="p-tag">${esc(String(t.created_at || "").slice(0, 19))}</td><td><span class="badge ${t.kind === "conversion" ? "published" : "draft"}">${esc(t.kind)}</span></td><td>${esc(t.party)}<div class="p-tag">${esc(t.party_type)}</div></td><td class="p-tag">${esc(t.channel)} · ${esc(t.distribution)}</td><td class="p-tag">${esc((t.owner || "").slice(0, 22))}</td><td class="num">${t.value}</td></tr>`).join("") || '<tr><td colspan="6">No touchpoints recorded yet.</td></tr>'}
  </tbody></table></div></div>
  <div class="p-panel"><h3>Universal incentive graph</h3>
    <p class="p-tag">${m.graph.nodes.length} node kinds · ${m.graph.edges.length} relationships, projected onto the platform's existing <code>links</code> table — every edge is queryable with <code>GET /api/goip/exchanges/:id</code>.</p>
    <div class="p-grid">${m.graph.nodes.map(n => `<div class="p-card" style="padding:6px 10px"><b>${esc(n.key)}</b><div class="p-tag">${esc(n.store)}</div></div>`).join("")}</div>
    <p style="margin-top:8px">${m.graph.edges.map(e => `<code style="margin-right:6px">${esc(e)}</code>`).join("")}</p></div>`;
}
async function gIntelligence(m) {
  return `<div class="p-panel"><h3>Intelligence fabric — 15 readings over live data</h3>
    <div style="display:flex;gap:8px;align-items:end;flex-wrap:wrap">
      <label><span>Reading</span><select id="iSel">${m.fabrics.intelligence.map(x => `<option value="${esc(x.key)}">${esc(x.name)}</option>`).join("")}</select></label>
      <button class="p-btn primary sm" id="iRun">Read</button>
      <span class="p-tag">Generation readings propose drafts; nothing publishes without the governance engine.</span>
    </div>
    <pre id="iOut" class="p-scroll-x" style="background:var(--p-bg2,#0b1020);color:#9ae6b4;padding:10px;border-radius:8px;margin-top:8px;max-height:420px;overflow:auto;font-size:12px">Pick a reading.</pre>
  </div>`;
}
function gCommercial(m, d) {
  const meters = d.meters || [], installs = d.installs || [];
  return `<div class="p-panel"><h3>Deployment models</h3><div class="p-grid">
      ${m.commercialization.deployments.map(x => `<div class="p-card" style="padding:8px 10px"><b>${esc(x.name)}</b><div class="p-tag"><code>${esc(x.key)}</code></div></div>`).join("")}
    </div></div>
    <div class="p-panel"><h3>Billing models — every capability bills a meter</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>Model</th><th>Meter</th><th>Unit</th><th class="num">Rate</th><th class="num">Metered qty</th><th class="num">Accrued</th></tr></thead><tbody>
      ${m.commercialization.billing_models.map(b => { const live = meters.find(x => x.kind === b.meter) || { qty: 0, amount: 0 }; return `<tr><td><b>${esc(b.name)}</b></td><td class="p-tag"><code>${esc(b.meter)}</code></td><td class="p-tag">${esc(b.unit)}</td><td class="num">${b.rate}</td><td class="num">${live.qty || 0}</td><td class="num">${money(live.amount || 0)}</td></tr>`; }).join("")}
    </tbody></table></div>
    <p class="p-tag">Meters are written through <code>billing.meter()</code> into <code>usage_records</code> — they ride the existing invoice run, so GOIP usage appears as billed lines on the store's next invoice. Rates apply only to stores that purchased the GOIP module; everyone else is metered at zero.</p></div>
    <div class="p-panel"><h3>Stores entitled to GOIP</h3><table class="p-table"><thead><tr><th>Store</th><th>Status</th></tr></thead><tbody>
      ${installs.map(i => `<tr><td>${esc(i.slug)}</td><td><span class="badge ${i.status === "installed" ? "published" : "draft"}">${esc(i.status)}</span></td></tr>`).join("") || '<tr><td colspan="2">No store has purchased GOIP yet — sell it in <b>🧩 Module Marketplace</b>.</td></tr>'}
    </tbody></table></div>`;
}
function wireGlobalOffers() {
  const $id = i => document.getElementById(i);
  const gval = i => { const el = $id(i); return el ? el.value : ""; };
  const jparse = (v, d) => { try { return v ? JSON.parse(v) : d; } catch (e) { return d; } };
  document.querySelectorAll("[data-gt]").forEach(b => b.onclick = async () => {
    goipTab = b.dataset.gt;
    document.querySelectorAll("[data-gt]").forEach(x => x.classList.toggle("primary", x.dataset.gt === goipTab));
    const body = $id("goipBody"); if (body) { body.innerHTML = '<div class="p-empty">Loading…</div>'; body.innerHTML = await gView(); wireGlobalOffers(); }
  });
  if ($id("gSave")) $id("gSave").onclick = async () => {
    const dist = [...document.querySelectorAll("[data-gdist]")].filter(c => c.checked).map(c => c.dataset.gdist);
    const place = gval("gPlace"), cal = gval("gCal");
    try {
      const r = await api("/goip/create", "POST", {
        name: gval("gName"), benefit: gval("gBenefit"), value: Number(gval("gValue")), code: gval("gCode"),
        domain: gval("gDomain"), channel: gval("gChan"), funder: gval("gFunder"), funder_ref: gval("gFunderRef"),
        economic_unit: gval("gUnit"), reality: gval("gReality"), usage_limit: Number(gval("gUse")) || 0,
        temporal: cal ? { calendar: cal } : {}, spatial: place ? { include: [place] } : {},
        conditions: jparse(gval("gCond"), {}), funding: jparse(gval("gFund"), {}), distribution: dist,
        governance: { state: gval("gGov") }, scope_level: "global", scope_type: "store", status: "active"
      });
      toast("Value exchange published (#" + (r.result && r.result.id) + ")"); render();
    } catch (e) { toast(e.message); }
  };
  document.querySelectorAll("[data-ggov]").forEach(b => b.onclick = async () => {
    try { const r = await api("/goip/govern", "POST", { id: Number(b.dataset.gid), action: b.dataset.ggov }); toast(b.dataset.ggov + " → " + ((r.result && r.result.state) || (r.result && r.result.id) || "ok")); render(); }
    catch (e) { toast(e.message); }
  });
  if ($id("gcRun")) $id("gcRun").onclick = async () => {
    const out = $id("gcOut"); out.textContent = "…";
    try { const r = await api("/goip/" + gval("gcSel"), "POST", jparse(gval("gcBody"), {})); out.textContent = JSON.stringify(r, null, 2); }
    catch (e) { out.textContent = "⚠️ " + e.message; }
  };
  document.querySelectorAll("[data-gcap]").forEach(b => b.onclick = () => { const sel = $id("gcSel"); if (sel) { sel.value = b.dataset.gcap; sel.scrollIntoView({ block: "center" }); } });
  if ($id("fGo")) $id("fGo").onclick = async () => {
    try { await api("/goip/fund", "POST", { funder: gval("fFunder"), funder_ref: gval("fRef"), unit: gval("fUnit"), domain: gval("fDomain"), amount: Number(gval("fAmount")) || 0 }); toast("Budget allocated"); render(); }
    catch (e) { toast(e.message); }
  };
  if ($id("sRun")) $id("sRun").onclick = async () => {
    try { const r = await api("/goip/settle", "POST", { period: gval("sPeriod"), all: true }); toast((r.result.redemptions_settled || 0) + " redemptions settled across all stores"); render(); }
    catch (e) { toast(e.message); }
  };
  document.querySelectorAll("[data-spay]").forEach(b => b.onclick = async () => {
    const fees = prompt("Payout fees (blank = 0)"); if (fees === null) return;
    try { const r = await api("/goip/pay", "POST", { id: Number(b.dataset.spay), fees: Number(fees) || 0, tenant_id: Number(b.dataset.stenant || 0) || undefined }); toast("Paid " + r.result.net + " " + r.result.unit + " · " + r.result.reference); render(); }
    catch (e) { toast(e.message); }
  });
  document.querySelectorAll("[data-sapprove]").forEach(b => b.onclick = async () => {
    try { await api("/goip/settle", "POST", { approve: Number(b.dataset.sapprove), tenant_id: Number(b.dataset.stenant || 0) || undefined }); toast("Settlement approved"); render(); }
    catch (e) { toast(e.message); }
  });
  document.querySelectorAll("[data-srec]").forEach(b => b.onclick = async () => {
    const ref = prompt("External reference (bank statement id)"); if (ref === null) return;
    try { await api("/goip/settle", "POST", { reconcile: Number(b.dataset.srec), external_ref: ref, tenant_id: Number(b.dataset.stenant || 0) || undefined }); toast("Reconciled"); render(); }
    catch (e) { toast(e.message); }
  });
  if ($id("aRun")) $id("aRun").onclick = async () => {
    const out = $id("aOut"); out.textContent = "…";
    try { const r = await api("/goip/attribute", "POST", { owner: gval("aOwner"), model: gval("aModel"), value: Number(gval("aValue")) || 0, commission_rate: Number(gval("aRate")) || 0 }); out.textContent = JSON.stringify(r.result, null, 2); }
    catch (e) { out.textContent = "⚠️ " + e.message; }
  };
  if ($id("iRun")) $id("iRun").onclick = async () => {
    const out = $id("iOut"); out.textContent = "…";
    try { const r = await api("/goip/intelligence/" + gval("iSel")); out.textContent = JSON.stringify(r.result, null, 2); }
    catch (e) { out.textContent = "⚠️ " + e.message; }
  };
}
function wireDefinitions() {
  const $id = i => document.getElementById(i);
  const modal = $id("defModal");
  $id("newDef").onclick = () => { $id("defTitle").textContent = "Define Entity"; $id("defKey").value = ""; $id("defLabel").value = ""; $id("defIcon").value = ""; $id("defFields").value = ""; modal.style.display = "block"; };
  $id("cancelDef").onclick = () => { modal.style.display = "none"; };
  $id("saveDef").onclick = async () => {
    const key = $id("defKey").value.trim();
    const label = $id("defLabel").value.trim();
    const icon = $id("defIcon").value.trim() || "🧬";
    const fields = JSON.parse($id("defFields").value || "[]");
    if (!key || !label || !Array.isArray(fields)) { alert("Key, label and fields required"); return; }
    try {
      await api("/meta/entity-def", "POST", { key, label, icon, fields });
      toast("Entity definition saved"); modal.style.display = "none"; render();
    } catch (e) { toast(e.message); }
  };
 $$("[data-edit]").forEach(b => b.onclick = async () => {
    const key = b.dataset.edit;
    const row = await api("/meta/entity-def");
    const def = row.rows.find(r => r.key === key);
    if (!def) return;
    $id("defTitle").textContent = "Edit Entity";
    $id("defKey").value = def.key;
    $id("defLabel").value = JSON.parse(def.def || "{}").label;
    $id("defIcon").value = JSON.parse(def.def || "{}").icon || "";
    $id("defFields").value = JSON.stringify(JSON.parse(def.def || "{}").fields || [], null, 2);
    modal.style.display = "block";
  });
  $$("[data-toggle-entity]").forEach(b => b.onclick = async () => {
    const key = b.dataset.toggleEntity;
    const tenantId = b.dataset.tenant;
    const enabled = b.textContent === '✕';
    try {
      if (enabled) {
        await api(`/meta/entity-def/${key}/disable?tenant_id=${tenantId}`, "POST");
      } else {
        await api(`/meta/entity-def/${key}/enable?tenant_id=${tenantId}`, "POST");
      }
      toast(enabled ? "Entity disabled for store" : "Entity enabled for store");
      render();
    } catch (e) { toast(e.message); }
  });
 }
function wireStudio() {
  const $ = s => document.getElementById(s);
  if ($("#studioLoad")) $("#studioLoad").onclick = async () => {
    const tenantId = $("#studioTenant").value;
    const entity = $("#studioEntity").value;
    try {
      const { rows } = await api(`/meta/entity/${entity}?tenant_id=${tenantId}`);
      const def = (await api("/meta/entity-def")).rows.find(r => r.key === entity);
      const schema = JSON.parse(def.def || "{}");
      const fields = schema.fields || [];
      const tbody = rows.map(r => {
        const cells = fields.filter(f => f.list).map(f => `<td>${esc(r[f.key] || "")}</td>`).join("");
        return `<tr>${cells}<td><button class="p-btn sm" data-view="${r.id}">View</button></td></tr>`;
      }).join("") || '<tr><td colspan="5" class="p-empty">No data</td></tr>';
      $("#studioBody").innerHTML = `<div class="p-panel"><h3>${esc(schema.label || entity)} Data</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>${fields.filter(f => f.list).map(f => `<th>${esc(f.label)}</th>`).join("")}<th>Actions</th></tr></thead><tbody>${tbody}</tbody></table></div></div>`;
    } catch (e) { toast(e.message); }
  };
}
function wireUCII() {
  const $ = s => document.querySelector(s);
  $$("[data-action]").forEach(b => b.onclick = async () => {
    const action = b.dataset.action;
    try {
      if (action === "newCap") {
        const key = prompt("Capability key (e.g., offer_engine):");
        if (!key) return;
        const name = prompt("Name:", key);
        await api("/ucii/capabilities", "POST", { key, name, category: "custom", status: "active" });
        toast("Capability created"); render();
      } else if (action === "newDomain") {
        const key = prompt("Domain key (e.g., commerce):");
        if (!key) return;
        await api("/ucii/domains", "POST", { key, status: "active" });
        toast("Domain created"); render();
      } else if (action === "newPolicy") {
        const key = prompt("Policy key (e.g., max_discount_limit):");
        if (!key) return;
        const domain = prompt("Domain:", "commerce");
        await api("/ucii/policies", "POST", { key, domain, rule: "{}", status: "active" });
        toast("Policy created"); render();
      } else if (action === "newWorkflow") {
        const key = prompt("Workflow key (e.g., order_fulfillment):");
        if (!key) return;
        const domain = prompt("Domain:", "commerce");
        await api("/ucii/workflows", "POST", { key, domain, trigger: "event", steps: "[]", status: "active" });
        toast("Workflow created"); render();
      } else if (action === "newSchema") {
        const key = prompt("Entity schema key (e.g., customer_extension):");
        if (!key) return;
        const label = prompt("Label:", key);
        await api("/meta/entity-def", "POST", { key, label, icon: "📋", fields: [] });
        toast("Schema created"); render();
      }
    } catch (e) { toast(e.message); }
  });
  
  // Click on capability to configure
  $$("[data-cap]").forEach(b => b.onclick = async () => {
    const capKey = b.dataset.cap;
    try {
      const [cap, config] = await Promise.all([
        api("/ucii/capabilities"),
        api("/ucii/config", "GET", { key: capKey, scope: "platform" })
      ]);
      const capability = cap.capabilities.find(c => c.key === capKey);
      if (!capability) { toast("Capability not found"); return; }
      
      const configData = config.config || {};
      const configStr = JSON.stringify(configData, null, 2);
      
      const configBody = `
        <div class="p-panel"><h3>Configure ${esc(capability.name)}</h3>
          <textarea id="capConfig" rows="12" style="width:100%;font-family:monospace">${esc(configStr)}</textarea>
          <div style="margin-top:10px">
            <button class="p-btn primary" id="saveCapConfig">Save Configuration</button>
            <button class="p-btn" id="cancelCapConfig">Cancel</button>
          </div>
        </div>`;
      
      const modal = document.createElement("div");
      modal.className = "p-modal";
      modal.id = "capConfigModal";
      modal.innerHTML = configBody;
      document.body.appendChild(modal);
      modal.style.display = "block";
      
      document.getElementById("saveCapConfig").onclick = async () => {
        try {
          const newConfig = JSON.parse(document.getElementById("capConfig").value);
          await api("/ucii/config", "POST", { key: capKey, value: newConfig, scope: "platform" });
          toast("Configuration saved");
          modal.remove();
          render();
        } catch (e) {
          alert("Invalid JSON: " + e.message);
        }
      };
      
      document.getElementById("cancelCapConfig").onclick = () => { modal.remove(); };
    } catch (e) { toast(e.message); }
  });
}
/* UCOS Ω∞ Constitution — the two Architecture documents parsed into a canonical registry.
   The console only ever READS the seeded tables; the documents remain the single truth. */
async function vUCOS() {
  const [man, docs, h] = await Promise.all([api("/ucos/manifest"), api("/ucos/docs"), api("/ucos/health").catch(() => null)]);
  const stat = k => k.toLocaleString();
  const hc = h || {};
  const badge = hc.ok
    ? '<span class="badge published">healthy</span>'
    : '<span class="badge failed">' + esc(hc.status || "unknown") + '</span>';
  const probs = (hc.problems || []).map(p2 => '<div class="p-tag" style="margin:3px 0">' + esc(p2.severity || "warn") + " · " + esc(p2.code) + " — " + esc(p2.detail || "") + '</div>').join("");
  return `
  <div class="p-panel"><h2>♾️ UCOS Ω∞ · Constitutional Registry</h2>
    <p class="p-tag">Knowledge-Once · Configuration-Over-Code · Registry-First — the Architecture documents are parsed, never transcribed. Every row points back to its source line.</p>
    <div style="display:flex;align-items:center;gap:8px;margin:10px 0;flex-wrap:wrap">
      ${badge}
      <span class="p-tag">sections ${stat((hc.counts || {}).sections || 0)} · articles ${stat((hc.counts || {}).articles || 0)} · concepts ${stat((hc.counts || {}).concepts || 0)} · edges ${stat((hc.counts || {}).edges || 0)}</span>
      <button class="p-btn sm" id="ucosHealthBtn">↻ Health</button>
      <button class="p-btn sm" id="ucosDriftBtn">Drift check</button>
    </div>
    ${probs ? '<div class="p-card" style="padding:10px;margin-bottom:10px">' + probs + '</div>' : ""}
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:12px;margin-top:14px">
      ${(docs.documents || []).map(d => `
        <div class="p-card" style="padding:14px">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <div><b>${esc(d.code)} Ω∞</b><div class="p-tag" style="font-size:12px">${esc(d.kind)}</div></div>
            <span class="badge active">${stat(d.sections + d.articles)} containers</span>
          </div>
          <div style="font-size:13px;margin:8px 0;color:var(--p-fg)">${esc(d.name)}</div>
          <div class="p-tag">📄 ${esc(d.file)} · ${stat(d.lines)} lines</div>
          <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:8px">
            <span class="p-tag">Parts ${stat(d.parts)}</span>
            <span class="p-tag">Sections ${stat(d.sections)}</span>
            <span class="p-tag">Articles ${stat(d.articles)}</span>
            <span class="p-tag">Concepts ${stat(d.concepts)}</span>
            <span class="p-tag">Registries ${stat(d.registries)}</span>
          </div>
          <div style="margin-top:10px;display:flex;gap:6px;flex-wrap:wrap">
            <button class="p-btn sm" data-browse="${esc(d.doc_id)}" data-kind="sections">Sections</button>
            <button class="p-btn sm" data-browse="${esc(d.doc_id)}" data-kind="articles">Articles</button>
            <button class="p-btn sm" data-browse="${esc(d.doc_id)}" data-kind="concepts">Concepts</button>
            <button class="p-btn sm" data-browse="${esc(d.doc_id)}" data-kind="registries">Registries</button>
          </div>
        </div>`).join("")}
    </div>
    <div style="margin-top:16px">
      <h3>🔎 Search the constitution</h3>
        <div style="display:flex;gap:8px">
          <input id="ucosQ" placeholder="e.g. quantum, entitlement, quantity…" class="p-form" style="flex:1;padding:10px 12px;border-radius:10px;border:1px solid var(--p-line);background:var(--p-bg);color:var(--p-text);font-size:13.5px">
          <button class="p-btn primary" id="ucosGo">Search</button>
        </div>
      <div id="ucosResults" style="margin-top:10px"></div>
      <div id="ucosPager" style="margin-top:6px;display:flex;gap:8px;align-items:center"></div>
    </div>
    <div style="margin-top:16px">
      <button class="p-btn" data-action="ucosReparse">↻ Re-parse documents (idempotent)</button>
      <span class="p-tag" style="margin-left:8px">Re-reads the source files; duplicates are prevented by unique keys</span>
    </div>
  </div>`;
}
function wireUCOS() {
  const stat2 = n => Number(n || 0).toLocaleString();
  /* registry list items render as chips, not a raw JSON blob */
  const renderItems = items => (Array.isArray(items) ? items : [])
    .map(i => '<span class="p-tag" style="margin:2px">' + esc(typeof i === "string" ? i : (i && i.name) || JSON.stringify(i)) + '</span>').join(" ");
  /* a page of rows: sections/articles/concepts/registries share this renderer */
  const renderResults = (rows, kind) => {
    const el = document.getElementById("ucosResults");
    if (!el) return;
    if (!rows.length) { el.innerHTML = '<p class="p-tag">No matches.</p>'; return; }
    el.innerHTML = rows.map(r => {
      if (kind === "registries") return '<div class="p-card" style="padding:10px;margin:6px 0;font-size:13px">' +
        '<b>' + esc(r.name) + '</b> <span class="p-tag">' + esc(r.container_name || "") + ' · line ' + stat2(r.line) + '</span>' +
        '<div style="margin-top:5px">' + renderItems(r.items) + '</div></div>';
      return '<div class="p-card" style="padding:10px;margin:6px 0;font-size:13px">' +
        '<b>' + esc(r.name) + '</b> <span class="p-tag">' + esc(kind) + ' · line ' + stat2(r.line) + '</span>' +
        (r.container ? '<div class="p-tag">in ' + esc(r.container) + '</div>' : "") +
        '<button class="p-btn sm" style="margin-left:6px" data-graph="' + esc(r.doc || "") + '" data-gtype="' + esc(kind === "concepts" ? "concept" : "section") + '" data-gid="' + esc(r.qkey || r.key || "") + '" data-gname="' + esc((r.name || "").slice(0, 40)) + '" data-gcontainer="' + esc(r.container || "") + '">⌘ graph</button>' +
        '</div>';
    }).join("");
    wireGraph();
  };
  /* paginated browser: keeps a cursor so Next/Prev walk the real total */
  let cursor = { doc: "", kind: "", offset: 0, limit: 25, part: null, q: null };
  const renderPager = (total, offset, limit) => {
    const el = document.getElementById("ucosPager");
    if (!el) return;
    const pages = Math.ceil(total / limit) || 1;
    const cur = Math.floor(offset / limit) + 1;
    el.innerHTML = '<span class="p-tag">' + stat2(total) + ' rows · page ' + cur + ' / ' + pages + '</span> ' +
      (offset > 0 ? '<button class="p-btn sm" data-pg="prev">← Prev</button>' : "") +
      (offset + limit < total ? '<button class="p-btn sm" data-pg="next">Next →</button>' : "");
    el.querySelectorAll("[data-pg]").forEach(b => b.onclick = () => loadPage(b.dataset.pg === "next" ? cursor.offset + cursor.limit : Math.max(0, cursor.offset - cursor.limit)));
  };
  const loadPage = async offset => {
    const c = cursor;
    try {
      const params = { limit: c.limit, offset: offset == null ? c.offset : offset };
      if (c.part != null) params.part = c.part;
      if (c.q) params.q = c.q;
      const r = await api(`/ucos/${c.doc}/${c.kind}`, "GET", params);
      c.offset = offset == null ? c.offset : offset;
      const rows = r[c.kind] || [];
      renderResults(rows.map(x => Object.assign({ doc: c.doc }, x, { name: x.name || x.label || x.qkey, container: x.container_name || x.container || x.title || "" })), c.kind);
      renderPager(Number(r.total || rows.length), Number(r.offset || 0), Number(r.limit || c.limit));
    } catch (e) { toast(e.message); }
  };
  $$("[data-browse]").forEach(b => b.onclick = () => {
    cursor = { doc: b.dataset.browse, kind: b.dataset.kind, offset: 0, limit: 25, part: null, q: null };
    loadPage(0);
  });
  const go = async () => {
    const q = (document.getElementById("ucosQ") || {}).value;
    if (!q) return;
    try { const r = await api("/ucos/search", "GET", { q, limit: 30 }); renderResults(r.results || [], "search"); }
    catch (e) { toast(e.message); }
  };
  const btn = document.getElementById("ucosGo");
  if (btn) btn.onclick = go;
  const inp = document.getElementById("ucosQ");
  if (inp) inp.onkeydown = e => { if (e.key === "Enter") go(); };
  $$("[data-action='ucosReparse']").forEach(b => b.onclick = async () => {
    try { const r = await api("/ucos/reparse", "POST", {}); toast(`Re-parsed: ${r.stats.sections} sections, ${r.stats.concepts} concepts, ${r.stats.edges} edges`); render(); }
    catch (e) { toast(e.message); }
  });
  const hb = document.getElementById("ucosHealthBtn");
  if (hb) hb.onclick = () => render();
  const dbtn = document.getElementById("ucosDriftBtn");
  if (dbtn) dbtn.onclick = async () => {
    try { const r = await api("/ucos/drift", "GET", {}); toast(r.drifted ? "⚠ " + r.message : "✓ " + r.message); }
    catch (e) { toast(e.message); }
  };
  /* graph explorer: a node and its immediate neighbourhood as radial SVG */
  const wireGraph = () => {
    $$("[data-graph]").forEach(b => b.onclick = async () => {
      const doc = b.dataset.graph, type = b.dataset.gtype, id = b.dataset.gid;
      if (!doc || !id) return;
      try {
        const r = await api(`/ucos/${doc}/neighbours`, "GET", { type, id, limit: 60 });
        drawGraph(doc, type, id, b.dataset.gname || id, b.dataset.gcontainer || "", r);
      } catch (e) { toast(e.message); }
    });
  };
  const drawGraph = (doc, type, id, name, container, r) => {
    const el = document.getElementById("ucosResults");
    if (!el) return;
    const edges = r.edges || [], names = r.names || {};
    const cx = 220, cy = 180, R = 120;
    const label = (t, i2) => names[t + "|" + i2] || i2;
    const pts = edges.map((e, i2) => {
      const isSrc = e.source_type === type && String(e.source_id) === String(id);
      const other = isSrc ? { t: e.target_type, id: e.target_id, rel: e.rel } : { t: e.source_type, id: e.source_id, rel: e.rel };
      const ang = (i2 / Math.max(1, edges.length)) * Math.PI * 2 - Math.PI / 2;
      return { x: cx + R * Math.cos(ang), y: cy + R * Math.sin(ang), t: other.t, id: other.id, rel: other.rel, name: label(other.t, other.id) };
    });
    el.innerHTML = '<div class="p-card" style="padding:12px">' +
      '<div style="display:flex;justify-content:space-between;align-items:center"><b>⌘ Knowledge graph · ' + esc(name) + '</b>' +
      '<button class="p-btn sm" id="ucosGraphClose">close</button></div>' +
      '<div class="p-tag">' + esc(type) + ' · ' + esc(container || doc) + ' · ' + edges.length + ' edge(s)</div>' +
      '<svg viewBox="0 0 440 360" style="width:100%;max-width:560px;margin-top:8px">' +
      pts.map(p2 => '<line x1="' + cx + '" y1="' + cy + '" x2="' + (+p2.x.toFixed(1)) + '" y2="' + (+p2.y.toFixed(1)) + '" stroke="var(--p-line)" stroke-width="1"/>').join("") +
      pts.map(p2 => '<g data-node="' + esc(p2.t + "|" + p2.id) + '" style="cursor:pointer"><circle cx="' + (+p2.x.toFixed(1)) + '" cy="' + (+p2.y.toFixed(1)) + '" r="5" fill="' + (p2.t === "concept" ? "#6b8cff" : p2.t === "section" ? "#37b24d" : "#868e96") + '"/><text x="' + (+p2.x.toFixed(1)) + '" y="' + (+p2.y.toFixed(1) - 9) + '" font-size="9" text-anchor="middle" fill="var(--p-text)">' + esc((p2.name || p2.id || "").slice(0, 26)) + '</text></g>').join("") +
      '<circle cx="' + cx + '" cy="' + cy + '" r="9" fill="var(--p-accent)"/><text x="' + cx + '" y="' + (cy - 14) + '" font-size="10" font-weight="bold" text-anchor="middle" fill="var(--p-text)">' + esc((name || id).slice(0, 30)) + '</text>' +
      '</svg></div>';
    const cl = document.getElementById("ucosGraphClose");
    if (cl) cl.onclick = () => { el.innerHTML = ""; };
    el.querySelectorAll("[data-node]").forEach(g => g.onclick = () => {
      const parts = g.dataset.node.split("|");
      const t = parts[0], nid = parts.slice(1).join("|");
      if (!t || !nid) return;
      api(`/ucos/${doc}/neighbours`, "GET", { type: t, id: nid, limit: 60 })
        .then(rr => drawGraph(doc, t, nid, names[t + "|" + nid] || nid, "", rr))
        .catch(e2 => toast(e2.message));
    });
  };
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
    <div style="margin-top:12px"><button class="p-btn primary sm" id="rtSave">Apply base runtime</button> <button class="p-btn sm" id="rtTest">Test connections</button> <span id="rtTestOut" class="p-tag"></span></div></div>
    <div class="p-panel"><h2>🐘 Database (Postgres cutover)</h2>
      <p style="color:var(--p-muted);font-size:13px;margin:0 0 10px">Set driver <b>postgres</b> + connection string above and save, then dry-run / verify / apply. SQLite is the default; nothing changes until you switch.</p>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px"><button class="p-btn sm" id="dbPing">Test connection</button><button class="p-btn sm" id="dbDry">Dry-run migration</button><button class="p-btn sm primary" id="dbApply">Apply migration</button><button class="p-btn sm danger" id="dbBack">Revert to SQLite</button></div>
      <pre id="dbOut" style="background:#0b0d12;color:#cfe;padding:10px;border-radius:10px;font-size:12px;max-height:220px;overflow:auto">Status loading…</pre>
      <h3 style="margin-top:12px">Regions &amp; Edge / CDN</h3><div id="regWrap" class="p-tag">loading…</div>
    </div>`;
}
function wireRuntime() {
  const $ = s => document.querySelector(s), $$ = s => Array.from(document.querySelectorAll(s));
  const baseBody = () => { const body = {}; $$("[data-rt]").forEach(sel => { body[sel.dataset.rt] = { driver: sel.value }; }); $$("[data-rtp]").forEach(inp => { const [k, field] = inp.dataset.rtp.split("."); body[k] = body[k] || {}; body[k].params = body[k].params || {}; if (inp.value && !inp.value.startsWith("••••")) body[k].params[field] = inp.value; }); return body; };
  const save = async () => { try { await api("/platform/runtime", "PUT", baseBody()); toast("Base runtime applied"); render(); } catch (e) { toast(e.message); } };
  if ($("#rtSave")) $("#rtSave").onclick = save;
  if ($("#rtTest")) $("#rtTest").onclick = async () => { const out = []; for (const c of ["cache", "ratelimit", "queue", "storage", "db"]) { try { const r = await api("/platform/runtime/test", "POST", { concern: c }); out.push(c + "=" + (r.ok ? "ok" : "FAIL") + (r.error ? ":" + r.error : "")); } catch (e) { out.push(c + "=err"); } } $("#rtTestOut").textContent = out.join(" · "); };
  const dbLog = obj => { const el = document.getElementById("dbOut"); if (el) el.textContent = JSON.stringify(obj, null, 1).slice(0, 4000); };
  (async () => { try { dbLog(await api("/platform/db")); } catch (e) { dbLog({ error: e.message }); } })();
  if ($("#dbPing")) $("#dbPing").onclick = async () => { try { dbLog(await api("/platform/db/ping", "POST", {})); } catch (e) { dbLog({ error: e.message }); } };
  if ($("#dbDry")) $("#dbDry").onclick = async () => { try { dbLog(await api("/platform/db/apply", "POST", { dryRun: true })); } catch (e) { dbLog({ error: e.message }); } };
  if ($("#dbApply")) $("#dbApply").onclick = async () => { if (!confirm("Apply migration to the configured Postgres? Runs DDL + data copy.")) return; try { dbLog(await api("/platform/db/apply", "POST", {})); } catch (e) { dbLog({ error: e.message }); } };
  if ($("#dbBack")) $("#dbBack").onclick = async () => { try { await api("/platform/db/switch", "POST", { driver: "sqlite" }); toast("Reverted to SQLite"); render(); } catch (e) { toast(e.message); } };
  let REG = { list: [], cdn: "" };
  const renderReg = () => { const el = document.getElementById("regWrap"); if (!el) return; el.innerHTML = `${REG.list.map((r, i) => `<span class="p-tag"><input data-regk="${i}" value="${esc(r.key)}" size="8"> <input data-regl="${i}" value="${esc(r.label)}" size="10"> <button class="p-btn sm danger" data-regdel="${i}">✕</button></span>`).join(" ")}<div style="margin-top:6px"><label>CDN base URL <input id="cdn" value="${esc(REG.cdn || "")}" placeholder="https://cdn.example (blank = off)" style="min-width:280px"></label> <button class="p-btn sm" id="regAdd">+ region</button> <button class="p-btn sm primary" id="regSave">Save regions</button></div>`; };
  (async () => { try { REG = await api("/platform/regions"); renderReg(); } catch (e) { const el = document.getElementById("regWrap"); if (el) el.textContent = "regions error: " + e.message; } })();
  const regWrap = document.getElementById("regWrap"); if (regWrap) regWrap.onclick = e => {
    if (e.target.id === "regAdd") { REG.list.push({ key: "", label: "" }); renderReg(); }
    else if (e.target.dataset && e.target.dataset.regdel) { REG.list.splice(Number(e.target.dataset.regdel), 1); renderReg(); }
    else if (e.target.id === "regSave") { document.querySelectorAll("[data-regk]").forEach(x => { REG.list[Number(x.dataset.regk)] = REG.list[Number(x.dataset.regk)] || {}; REG.list[Number(x.dataset.regk)].key = x.value; }); document.querySelectorAll("[data-regl]").forEach(x => { REG.list[Number(x.dataset.regl)].label = x.value; }); REG.cdn = (document.getElementById("cdn") || {}).value || ""; api("/platform/regions", "PUT", REG).then(() => toast("Regions saved")).catch(er => toast(er.message)); }
  };
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
async function vBillingOps() {
  const d = await api("/platform/billing/aging"); const tenants = (await api("/platform/tenants")).tenants;
  const ag = d.aging, inv = (d.all && d.all.invoices) || [], notes = (d.all && d.all.notes) || [], events = (d.all && d.all.events) || [];
  const bStatus = s => `<span class="badge ${s === "paid" ? "published" : s === "overdue" ? "failed" : "processing"}">${esc(s)}</span>`;
  return `<div class="p-panel"><h2>💳 Billing Ops</h2>
    <p style="color:var(--p-muted);font-size:13px;margin:0 0 12px">Line-item subscription + usage invoicing, tax (via the Tax engine), credit notes / refunds-to-wallet (via the Offers wallet), dunning, and receivables aging.</p>
    <div class="p-cards" style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px">
      <div class="p-stat"><b>${money(ag.current)}</b> current</div><div class="p-stat"><b>${money(ag.d30)}</b> 1–30d</div><div class="p-stat"><b>${money(ag.d60)}</b> 31–60d</div><div class="p-stat"><b>${money(ag.d90)}</b> 60d+</div>
      <div class="p-stat"><b>${money(ag.total)}</b> receivable</div>
    </div>
    <div style="display:flex;gap:8px;margin-bottom:12px"><button class="p-btn sm primary" id="runDunning">Run dunning sweep</button>
      <span id="dunOut" class="p-tag"></span></div>
    <h3>Generate invoice</h3>
    <div style="display:flex;gap:8px;align-items:end;flex-wrap:wrap"><label><span>Store</span><select id="biTenant">${tenants.map(t => `<option value="${t.id}">${esc(t.name)}</option>`).join("")}</select></label><button class="p-btn sm" id="biGo">Issue monthly + usage invoice</button></div>
    <h3>Record metered usage</h3>
    <div style="display:flex;gap:8px;align-items:end;flex-wrap:wrap">
      <label><span>Store</span><select id="usTenant">${tenants.map(t => `<option value="${t.id}">${esc(t.name)}</option>`).join("")}</select></label>
      <label><span>Kind</span><select id="usKind"><option>ai</option><option>orders</option><option>storage</option><option>api</option><option>manual</option></select></label>
      <label><span>Description</span><input id="usDesc" placeholder="AI premium units"></label>
      <label><span>Qty</span><input id="usQty" type="number" value="1"></label>
      <label><span>Unit</span><input id="usUnit" type="number" step="0.01" value="0"></label>
      <button class="p-btn sm" id="usGo">Add usage</button></div>
    <h3>Invoices (all stores)</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>#</th><th class="num">Amount</th><th>Status</th><th>Period</th><th>Lines</th><th></th></tr></thead><tbody>
      ${inv.map(i => `<tr><td><code>${esc(i.number)}</code></td><td class="num">${money(i.amount)}</td><td>${bStatus(i.status)}</td><td>${esc(i.period_start || "")}→${esc(i.period_end || "")}</td><td class="p-tag">${(i.lines || []).map(l => `${l.kind} ${money(l.amount)}`).join(", ")}</td>
        <td style="text-align:right"><button class="p-btn sm danger" data-ref="${i.id}">Credit/Refund</button></td></tr>`).join("") || '<tr><td colspan="6">None.</td></tr>'}
    </tbody></table></div>
    <h3>Credit notes</h3>${notes.length ? `<table class="p-table"><thead><tr><th>#</th><th class="num">Amount</th><th>Wallet</th><th>Reason</th></tr></thead><tbody>${notes.map(n => `<tr><td><code>${esc(n.number)}</code></td><td class="num">${money(n.amount)}</td><td>${n.to_wallet ? "yes" : "no"}</td><td>${esc(n.reason || "")}</td></tr>`).join("")}</tbody></table>` : '<p class="p-tag">None.</p>'}
    <h3>Billing events</h3><div class="p-tag" style="max-height:220px;overflow:auto">${events.slice(0, 20).map(e => { let d = {}; try { d = JSON.parse(e.detail || "{}"); } catch (x) { } return `${esc((e.created_at || "").slice(0, 16))} · ${esc(e.kind)} · ${esc(JSON.stringify(d))}`; }).join("<br>") || "—"}</div>
    </div>`;
}
function wireBillingOps() {
  const $ = s => document.querySelector(s);
  if ($("#runDunning")) $("#runDunning").onclick = async () => { try { const r = await api("/platform/billing/dunning", "POST", {}); $("#dunOut").textContent = (r.actions.length) + " overdue actions"; render(); } catch (e) { toast(e.message); } };
  if ($("#biGo")) $("#biGo").onclick = async () => { try { await api("/platform/tenants/" + $("#biTenant").value + "/invoice", "POST", {}); toast("Invoice issued"); render(); } catch (e) { toast(e.message); } };
  if ($("#usGo")) $("#usGo").onclick = async () => { try { await api("/platform/usage", "POST", { tenant_id: Number($("#usTenant").value), kind: $("#usKind").value, description: $("#usDesc").value || $("#usKind").value, qty: Number($("#usQty").value) || 1, unit_amount: Number($("#usUnit").value) || 0 }); toast("Usage recorded"); render(); } catch (e) { toast(e.message); } };
  document.querySelectorAll("[data-ref]").forEach(b => b.onclick = async () => { const amt = prompt("Refund amount (blank = full)"); try { await api("/platform/invoices/" + b.dataset.ref + "/refund", "POST", { amount: amt ? Number(amt) : undefined, to_wallet: confirm("Credit to the store's customer wallet? (OK) or log a credit note only (Cancel)") }); toast("Credit note issued"); render(); } catch (e) { toast(e.message); } });
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
    else if (view === "billing") { body.innerHTML = await vBillingOps(); wireBillingOps(); }
    else if (view === "gproducts") { body.innerHTML = await vGproducts(); wireGproducts(); }
    else if (view === "modules") { body.innerHTML = await vModules(); await wireModules(); }
    else if (view === "providers") body.innerHTML = await vProviders();
    else if (view === "ucii") { body.innerHTML = await vUCII(); wireUCII(); }
    else if (view === "ucos") { body.innerHTML = await vUCOS(); wireUCOS(); }
    else if (view === "studio") { body.innerHTML = await vStudio(); wireStudio(); }
    else if (view === "ai") body.innerHTML = await vAI();
    else if (view === "offers") { body.innerHTML = await vGlobalOffers(); wireGlobalOffers(); }
    else if (view === "runtime") { body.innerHTML = await vRuntime(); wireRuntime(); }
    else if (view === "identity") { body.innerHTML = await viewIdentity(); wireIdentity(); }
    else if (view === "identity-templates") { body.innerHTML = await viewIdentityTemplates(); wireIdentityTemplates(); }
    else if (view === "definitions") { body.innerHTML = await vDefinitions(); wireDefinitions(); }
    else if (view === "geo") { body.innerHTML = await vGeo(); await wireGeoFx(); }
    else if (view === "monitor") body.innerHTML = await vMonitor();
    else if (view === "audit") body.innerHTML = await vAudit();
    else if (view === "manual") window.open("/docs/user-manual.html", "_blank");
    else if (view === "architecture") window.open("/docs/architecture.html", "_blank");
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

async function vDocs() {
  return `<div class="p-head">
    <h2>📄 Architecture & User Manual</h2>
    <p class="p-sub">Documentation for LUXORA Platform</p>
  </div>
  <div class="p-card">
    <h3>📘 User Manual</h3>
    <p>Comprehensive guide for all platform roles (Platform Admin, Store Admin, Customers).</p>
    <p><a href="/docs/user-manual.html" target="_blank">View User Manual</a></p>
    
    <h3>🏛️ Architecture Documentation</h3>
    <p>Technical architecture, data models, and API specifications.</p>
    <p><a href="/docs/architecture.html" target="_blank">View Architecture</a></p>
    
    <h3>📚 Quick Links</h3>
    <ul>
      <li><a href="/GOIP-ROADMAP-2.md" target="_blank">GOIP Roadmap</a></li>
      <li><a href="/README.md" target="_blank">README</a></li>
      <li><a href="/USER_MANUAL.md" target="_blank">Full Manual (Source)</a></li>
    </ul>
  </div>
  <div class="p-card">
    <h3>🔗 API Reference</h3>
    <p>See the platform API endpoints for integration.</p>
    <ul>
      <li><code>POST /api/goip/:capability</code> - GOIP value exchange capabilities</li>
      <li><code>GET /api/platform/security</code> - Security scorecard</li>
      <li><code>GET /healthz</code> - Health check</li>
    </ul>
  </div>`;
}

function wireDocs() {
  // Add click handlers if needed for docs page
}

// Platform Policies
async function vPolicies() {
  shell('<div class="p-empty">Loading...</div>');
  try {
    const res = await api("/platform/policies");
    const policiesList = res.policies || [];
    if (policiesList.length === 0) {
      $$("#app").innerHTML = `<div class="p-panel"><h2>🔒 Platform Policies</h2>
        <p class="p-tag">No policies configured. Use Platform Console or API:</p>
        <pre>curl -X PUT http://localhost:8787/api/platform/policies/seo \\\\
  -d '{"metaDescription": "Store description"}'</pre>
      </div>`;
      return;
    }
    let html = `<div class="p-panel"><h2>🔒 Platform Policies</h2>
      <div class="p-tablewrap"><table class="p-table"><thead>
        <tr><th>Category</th><th>Config</th><th>Actions</th></tr>
      </thead><tbody>`;
    policiesList.forEach(p => {
      try {
        const config = JSON.parse(p.value || "{}");
        html += `<tr>
          <td><code>${esc(p.key.replace("policy.", ""))}</code></td>
          <td><pre>${esc(JSON.stringify(config, null, 2))}</pre></td>
          <td><button class="p-btn sm" onclick="editPolicy('${p.key}')">Edit</button>
              <button class="p-btn sm danger" onclick="deletePolicy('${p.key}')">✕</button></td>
        </tr>`;
      } catch(e) { html += `<tr><td>${esc(p.key)}</td><td>Invalid</td><td>✕</td></tr>`; }
    });
    html += `</tbody></table></div>
      <button class="p-btn primary" onclick="addPolicy()">+ Add Policy</button>
    </div>`;
    $$("#app").innerHTML = html;
  } catch (e) {
    $$("#app").innerHTML = `<div class="p-panel">Error: ${esc(e.message)}</div>`;
  }
}

function addPolicy() {
  const category = prompt("Policy category (seo, reviews, features):");
  if (!category) return;
  const configStr = prompt("JSON configuration:");
  if (!configStr) return;
  try {
    const config = JSON.parse(configStr);
    api(`/platform/policies/${category}`, "PUT", config).then(() => {
      toast("Policy saved"); viewPolicies();
    }).catch(e => toast(e.message));
  } catch(e) { toast("Invalid JSON"); }
}

function editPolicy(key) {
  const current = prompt("Update policy JSON:");
  if (!current) return;
  try {
    api(`/platform/policies/${key}`, "PUT", JSON.parse(current)).then(() => {
      toast("Policy updated"); viewPolicies();
    }).catch(e => toast(e.message));
  } catch(e) { toast("Invalid JSON"); }
}

function deletePolicy(key) {
  if (confirm("Delete policy?")) {
    api(`/platform/policies/${key}`, "DELETE").then(() => {
      toast("Policy deleted"); viewPolicies();
    }).catch(e => toast(e.message));
  }
}

async function wirePolicies() {
  // Setup policy UI listeners if needed
}

async function viewIdentity() {
  try {
    const [settingsRes, providersRes, templatesRes] = await Promise.all([
      api("/admin/identity-settings").catch(() => ({ settings: {} })),
      api("/admin/identity-providers").catch(() => ({ providers: [] })),
      api("/platform/identity-templates").catch(() => ({ templates: [] }))
    ]);
    const settings = settingsRes.settings || {};
    const providers = providersRes.providers || [];
    const templates = templatesRes.templates || [];
    
    const password = settings.password || {};
    const mfa = settings.mfa || {};
    const session = settings.session || {};
    const login = settings.login || {};
    
    return `<div class="card">
      <h3>🔐 Identity & Authentication Configuration</h3>
      <div class="form-group">
        <label>Password Policy</label>
        <div class="grid grid-2">
          <input type="number" id="minLen" value="${password.minLength || 8}" min="6" max="64" placeholder="Min Length">
          <input type="number" id="expiryDays" value="${password.expiryDays || 0}" min="0" max="365" placeholder="Expiry Days">
        </div>
        <div style="margin-top:8px;display:flex;gap:8px;flex-wrap:wrap">
          <label class="checkbox-group"><input type="checkbox" id="reqUpper" ${password.requireUppercase ? 'checked' : ''}> Require Uppercase</label>
          <label class="checkbox-group"><input type="checkbox" id="reqNumbers" ${password.requireNumbers ? 'checked' : ''}> Require Numbers</label>
          <label class="checkbox-group"><input type="checkbox" id="reqSpecial" ${password.requireSpecialChars ? 'checked' : ''}> Require Special Chars</label>
        </div>
      </div>
      
      <div class="form-group">
        <label>Multi-Factor Authentication</label>
        <label class="checkbox-group"><input type="checkbox" id="mfaEnabled" ${mfa.enabled ? 'checked' : ''}> Enable MFA</label>
        <label class="checkbox-group"><input type="checkbox" id="mfaAdmin" ${mfa.requireForAdmin ? 'checked' : ''}> Require for Admins</label>
      </div>
      
      <div class="form-group">
        <label>Session Settings</label>
        <div class="grid grid-3">
          <input type="number" id="sessTimeout" value="${session.timeoutMinutes || 120}" min="5" max="1440" placeholder="Timeout (min)">
          <input type="number" id="sessMax" value="${session.maxConcurrent || 3}" min="1" max="10" placeholder="Max Concurrent">
          <input type="number" id="sessRemember" value="${session.rememberMeDays || 30}" min="1" max="365" placeholder="Remember Me">
        </div>
      </div>
      
      <div class="form-group">
        <label>Login Settings</label>
        <div class="grid grid-2">
          <input type="number" id="maxAttempts" value="${login.maxAttempts || 5}" min="1" max="20" placeholder="Max Attempts">
          <input type="number" id="lockout" value="${login.lockoutMinutes || 30}" min="1" max="240" placeholder="Lockout (min)">
        </div>
        <label class="checkbox-group" style="margin-top:8px"><input type="checkbox" id="guestCheckout" ${login.allowGuestCheckout ? 'checked' : ''}> Allow Guest Checkout</label>
      </div>
      
      <button class="btn" onclick="saveIdentity()">Save Settings</button>
    </div>
    
    <div class="card" style="margin-top:16px">
      <h3>🔌 Identity Providers</h3>
      <div id="providersList" class="grid" style="grid-template-columns:1fr">
        ${providers.map(p => `
          <div class="card" style="border:1px solid var(--border-color);margin-bottom:8px">
            <div style="display:flex;justify-content:space-between;align-items:center">
              <div>
                <b>${esc(p.name)}</b>
                <span class="badge" style="margin-left:8px">${esc(p.provider_type)}</span>
                <span class="badge ${p.enabled ? 'badge-success' : ''}" style="margin-left:8px">${p.enabled ? 'Enabled' : 'Disabled'}</span>
              </div>
              <div>
                <button class="btn-icon" onclick="editProvider('${esc(p.id)}')">✎</button>
                <button class="btn-icon" style="color:var(--danger)" onclick="deleteProvider('${esc(p.id)}')">✕</button>
              </div>
            </div>
          </div>
        `).join('') || '<p class="alert alert-info">No providers configured. Click + Add Provider below.</p>'}
      </div>
      <button class="btn" style="margin-top:12px" onclick="addProvider()">+ Add Provider</button>
    </div>
    
    <div class="card" style="margin-top:16px">
      <h3>📋 Apply Global Template</h3>
      <select id="tmplSelect" class="form-group">
        <option value="">-- Select a template --</option>
        ${templates.map(t => `<option value="${t.id}">${esc(t.name)}${t.is_default ? ' (Default)' : ''}</option>`).join('')}
      </select>
      <button class="btn btn-outline" onclick="applyTemplate()">Apply to this store</button>
    </div>
    
    <div class="card" style="margin-top:16px">
      <h3>🔧 Provider Types</h3>
      <p class="p-tag">Customize available authentication types</p>
      ${['sso','oauth','otp','magic_link','biometric'].map(type => `
        <div class="card" style="border:1px solid var(--border-color);margin-bottom:8px">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <div><b>${type.toUpperCase()}</b> <span class="badge">Built-in</span></div>
            <button class="btn-icon" onclick="editProviderType('${type}')">Configure</button>
          </div>
        </div>
      `).join('')}
      <div class="card">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <div><b>Create Custom Type</b></div>
          <button class="btn" onclick="addProviderType()">+ New</button>
        </div>
      </div>
    </div>`;
  } catch (e) {
    return `<div class="card" style="color:var(--danger)">Error: ${esc(e.message)}</div>`;
  }
}

async function saveIdentity() {
  const body = {
    password: {
      minLength: parseInt(document.getElementById("minLen").value) || 8,
      requireUppercase: !!document.getElementById("reqUpper").checked,
      requireNumbers: !!document.getElementById("reqNumbers").checked,
      requireSpecialChars: !!document.getElementById("reqSpecial").checked,
      expiryDays: parseInt(document.getElementById("expiryDays").value) || 0
    },
    mfa: {
      enabled: !!document.getElementById("mfaEnabled").checked,
      requireForAdmin: !!document.getElementById("mfaAdmin").checked
    },
    session: {
      timeoutMinutes: parseInt(document.getElementById("sessTimeout").value) || 120,
      maxConcurrent: parseInt(document.getElementById("sessMax").value) || 3,
      rememberMeDays: parseInt(document.getElementById("sessRemember").value) || 30
    },
    login: {
      maxAttempts: parseInt(document.getElementById("maxAttempts").value) || 5,
      lockoutMinutes: parseInt(document.getElementById("lockout").value) || 30,
      allowGuestCheckout: !!document.getElementById("guestCheckout").checked
    }
  };
  try {
    await api("/admin/identity-settings", "PUT", body);
    toast("Settings saved");
    viewIdentity();
  } catch (e) {
    toast("Error: " + e.message);
  }
}

async function applyTemplate() {
  const tmplId = document.getElementById("tmplSelect").value;
  if (!tmplId) return toast("Select a template");
  try {
    await api("/admin/identity-templates/apply", "POST", { template_id: tmplId });
    toast("Template applied");
    viewIdentity();
  } catch (e) {
    toast("Error: " + e.message);
  }
}

async function addProvider() {
  const modal = document.createElement("div");
  modal.className = "modal-overlay";
  modal.innerHTML = `
    <div class="modal">
      <div class="modal-header">
        <h3 class="modal-title">Add Identity Provider</h3>
        <button class="btn-icon" onclick="this.closest('.modal-overlay').remove()">✕</button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label>Provider Type</label>
          <select id="provTypeAdd">
            <option value="sso">SSO (Okta, Azure AD, Google)</option>
            <option value="oauth">OAuth/Social (Google, Facebook, Apple)</option>
            <option value="openid">OpenID Connect</option>
            <option value="ldap">LDAP</option>
            <option value="otp">OTP (Email/SMS)</option>
            <option value="magic_link">Magic Link (Passwordless Email)</option>
            <option value="biometric">Biometric (WebAuthn)</option>
          </select>
        </div>
        <div class="form-group">
          <label>Name</label>
          <input type="text" id="provNameAdd" placeholder="e.g., Company SSO">
        </div>
        <div id="provFieldsAdd"></div>
        <div class="form-group checkbox-group">
          <input type="checkbox" id="provEnabledAdd" checked>
          <label>Enabled</label>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-outline" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
        <button class="btn" onclick="saveProviderAdd()">Save</button>
      </div>
    </div>
  `;
  document.body.appendChild(modal);
  
  const typeSelect = modal.querySelector("#provTypeAdd");
  const fieldsDiv = modal.querySelector("#provFieldsAdd");
  
  typeSelect.onchange = () => {
    const type = typeSelect.value;
    fieldsDiv.innerHTML = _getProviderFields(type);
  };
  typeSelect.onchange();
  
  function _getProviderFields(type) {
    switch (type) {
      case "sso":
        return `<div class="form-group"><label>Provider</label><select id="provProviderAdd"><option value="okta">Okta</option><option value="azure">Azure AD</option><option value="google">Google</option><option value="saml-generic">SAML Generic</option></select></div><div class="form-group"><label>SSO URL</label><input type="text" id="provUrlAdd" placeholder="https://company.okta.com/sso"></div><div class="form-group"><label>Domains</label><input type="text" id="provDomainsAdd" placeholder="company.com,acme.com"></div><div class="form-group"><label>Entity ID</label><input type="text" id="provEntityIdAdd" placeholder="urn:okta:example"></div>`;
      case "oauth":
        return `<div class="form-group"><label>Provider</label><select id="provProviderAdd"><option value="google">Google</option><option value="facebook">Facebook</option><option value="apple">Apple</option></select></div><div class="form-group"><label>Client ID</label><input type="text" id="provClientIdAdd"></div><div class="form-group"><label>Client Secret</label><input type="text" id="provClientSecretAdd"></div><div class="form-group"><label>Redirect URI</label><input type="text" id="provRedirectAdd"></div>`;
      case "otp":
        return `<div class="form-group"><label>Delivery</label><select id="provProviderAdd"><option value="email">Email</option><option value="sms">SMS</option><option value="both">Both</option></select></div><div class="form-group"><label>From</label><input type="text" id="provFromAdd" placeholder="noreply@example.com"></div>`;
      case "magic_link":
        return `<div class="form-group"><label>From Email</label><input type="text" id="provFromAdd" placeholder="noreply@example.com"></div><div class="form-group"><label>Base URL</label><input type="text" id="provBaseUrlAdd" placeholder="https://yourapp.com"></div>`;
      case "openid":
        return `<div class="form-group"><label>OpenID Provider URL</label><input type="text" id="provOpenidUrlAdd" placeholder="https://accounts.google.com"></div><div class="form-group"><label>Client ID</label><input type="text" id="provOpenidClientIdAdd"></div><div class="form-group"><label>Client Secret</label><input type="text" id="provOpenidClientSecretAdd"></div>`;
      case "ldap":
        return `<div class="form-group"><label>LDAP Server</label><input type="text" id="provLdapServerAdd" placeholder="ldap://ldap.example.com"></div><div class="form-group"><label>Base DN</label><input type="text" id="provLdapBaseDnAdd" placeholder="dc=example,dc=com"></div><div class="form-group"><label>Bind DN</label><input type="text" id="provLdapBindDnAdd"></div><div class="form-group"><label>Bind Password</label><input type="password" id="provLdapBindPassAdd"></div>`;
      case "biometric":
        return `<div class="form-group"><label>RP ID</label><input type="text" id="provRpIdAdd" placeholder="yourapp.com"></div><div class="form-group"><label>RP Name</label><input type="text" id="provRpNameAdd" placeholder="Your App"></div>`;
      default: return "";
    }
  }
  
  window.saveProviderAdd = async () => {
    const type = typeSelect.value;
    const name = document.getElementById("provNameAdd")?.value.trim();
    const enabled = document.getElementById("provEnabledAdd")?.checked;
    if (!name) return toast("Enter provider name");
    
    const config = {};
    const getVal = id => document.getElementById(id)?.value;
    config.provider = getVal("provProviderAdd");
    
    if (type === "sso") {
      config.ssoUrl = getVal("provUrlAdd");
      config.domains = getVal("provDomainsAdd").split(",").map(s => s.trim()).filter(Boolean);
      config.entityId = getVal("provEntityIdAdd");
    } else if (type === "oauth") {
      config.clientId = getVal("provClientIdAdd");
      config.clientSecret = getVal("provClientSecretAdd");
      config.redirectUri = getVal("provRedirectAdd");
    } else if (type === "openid") {
      config.providerUrl = getVal("provOpenidUrlAdd");
      config.clientId = getVal("provOpenidClientIdAdd");
      config.clientSecret = getVal("provOpenidClientSecretAdd");
    } else if (type === "ldap") {
      config.server = getVal("provLdapServerAdd");
      config.baseDn = getVal("provLdapBaseDnAdd");
      config.bindDn = getVal("provLdapBindDnAdd");
      config.bindPassword = getVal("provLdapBindPassAdd");
    } else if (type === "otp") {
      config.from = getVal("provFromAdd");
    } else if (type === "magic_link") {
      config.from = getVal("provFromAdd");
      config.baseUrl = getVal("provBaseUrlAdd");
    } else if (type === "biometric") {
      config.rpId = getVal("provRpIdAdd");
      config.rpName = getVal("provRpNameAdd");
    }
    
    try {
      await api("/admin/identity-providers", "PUT", { provider_type: type, name, enabled, config });
      toast("Provider added");
      modal.remove();
      viewIdentity();
    } catch (e) {
      toast("Error: " + e.message);
    }
  };
}
async function addProviderType() {
  const modal = document.createElement("div");
  modal.style.cssText = "position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);display:flex;align-items:center;justify-content:center;z-index:99999;"
  modal.innerHTML = `
    <div class="modal">
      <div class="modal-header">
        <h3 class="modal-title">Create New Provider Type</h3>
        <button class="btn-icon" onclick="this.closest('.modal-overlay').remove()">✕</button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label>Key (e.g., ldap, saml)</label>
          <input type="text" id="newProvKey" placeholder="custom">
        </div>
        <div class="form-group">
          <label>Label (e.g., LDAP, SAML)</label>
          <input type="text" id="newProvLabel" placeholder="Custom Provider">
        </div>
        <div class="form-group">
          <label>Fields (JSON)</label>
          <textarea id="newProvFields" rows="5" placeholder='[{"key":"url","label":"URL","type":"text"}]'></textarea>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-outline" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
        <button class="btn" onclick="saveNewProviderType()">Create</button>
      </div>
    </div>
  `;
  document.body.appendChild(modal);
  window.saveNewProviderType = async () => {
    const key = document.getElementById("newProvKey").value.trim();
    const label = document.getElementById("newProvLabel").value.trim();
    const fields = document.getElementById("newProvFields").value.trim();
    if (!key || !label) return toast("Enter key and label");
    try {
      const fieldsObj = fields ? JSON.parse(fields) : [];
      await api("/admin/identity-provider-types", "POST", { 
        key, label, schema: { fields: fieldsObj } 
      });
      toast("Provider type created");
      modal.remove();
      viewIdentity();
    } catch (e) {
      toast("Error: " + e.message);
    }
  };
}
async function viewIdentityTemplates() {
  shell('<div class="p-empty">Loading...</div>');
  try {
    const res = await api("/platform/identity-templates");
    const templates = res.templates || [];
    
    let html = `<div class="p-panel"><h2>📋 Global Identity Templates</h2>
      <p class="p-tag">Centralized identity configurations for provisioning new stores</p>
      
      <div class="p-form">
        <h3>Create Template</h3>
        <label><span>Name</span><input type="text" id="tmplName" placeholder="e.g., Enterprise SSO"></label>
        <label><span>Description</span><input type="text" id="tmplDesc" placeholder="SSO + MFA + strong passwords"></label>
        <label><span>Set as default</span><input type="checkbox" id="tmplDefault"></label>
        
        <h4>Template Configuration</h4>
        <div class="p-form">
          <h5>Password Policy</h5>
          <label><span>Min Length</span><input type="number" id="tmplPwdMin" value="12"></label>
          <label><span>Require Uppercase</span><input type="checkbox" id="tmplPwdUpper" checked></label>
          <label><span>Require Numbers</span><input type="checkbox" id="tmplPwdNum" checked></label>
          <label><span>Require Special</span><input type="checkbox" id="tmplPwdSpec" checked></label>
          <label><span>Expiry (days)</span><input type="number" id="tmplPwdExpiry" value="90"></label>
          
          <h5>MFA</h5>
          <label><span>Enable MFA</span><input type="checkbox" id="tmplMfaEnabled"></label>
          <label><span>Require for Admins</span><input type="checkbox" id="tmplMfaAdmin" checked></label>
          
          <h5>Session</h5>
          <label><span>Timeout (minutes)</span><input type="number" id="tmplSessTimeout" value="120"></label>
          <label><span>Max Concurrent</span><input type="number" id="tmplSessMax" value="3"></label>
          
          <h5>Login</h5>
          <label><span>Max Attempts</span><input type="number" id="tmplLoginMax" value="5"></label>
          <label><span>Lockout (minutes)</span><input type="number" id="tmplLoginLockout" value="30"></label>
        </div>
        
        <button class="p-btn primary" onclick="saveTemplate()">Create Template</button>
      </div>
      
      <h3>Saved Templates</h3>
      <div class="p-tablewrap"><table class="p-table"><thead>
        <tr><th>Name</th><th>Description</th><th>Actions</th></tr>
      </thead><tbody>`;
      
    templates.forEach(t => {
      const cfg = typeof t.config === 'string' ? JSON.parse(t.config) : t.config;
      const def = t.is_default ? '★ Default' : '';
      html += `<tr>
        <td>${esc(t.name)} ${def}</td>
        <td>${esc(t.description || '')}</td>
        <td>
          <button class="p-btn sm" onclick="editTemplate(${t.id})">Edit</button>
          <button class="p-btn sm danger" onclick="deleteTemplate(${t.id})">✕</button>
        </td>
      </tr>`;
    });
    
    html += `</tbody></table></div>
    </div>`;
    $$("#app").innerHTML = html;
  } catch (e) {
    $$("#app").innerHTML = `<div class="p-panel">Error: ${esc(e.message)}</div>`;
  }
}

async function saveTemplate() {
  const name = $("#tmplName").value.trim();
  if (!name) return toast("Enter template name");
  
  const config = {
    password: {
      minLength: parseInt($("#tmplPwdMin").value) || 12,
      requireUppercase: !!$("#tmplPwdUpper").checked,
      requireNumbers: !!$("#tmplPwdNum").checked,
      requireSpecialChars: !!$("#tmplPwdSpec").checked,
      expiryDays: parseInt($("#tmplPwdExpiry").value) || 90
    },
    mfa: {
      enabled: !!$("#tmplMfaEnabled").checked,
      requireForAdmin: !!$("#tmplMfaAdmin").checked
    },
    session: {
      timeoutMinutes: parseInt($("#tmplSessTimeout").value) || 120,
      maxConcurrent: parseInt($("#tmplSessMax").value) || 3
    },
    login: {
      maxAttempts: parseInt($("#tmplLoginMax").value) || 5,
      lockoutMinutes: parseInt($("#tmplLoginLockout").value) || 30
    }
  };
  
  try {
    await api("/platform/identity-templates", "POST", {
      name,
      description: $("#tmplDesc").value,
      config,
      is_default: !!$("#tmplDefault").checked
    });
    toast("Template created");
    viewIdentityTemplates();
  } catch (e) {
    toast("Error: " + e.message);
  }
}

async function editTemplate(id) {
  try {
    const res = await api(`/platform/identity-templates/${id}`);
    const t = res.template;
    const cfg = t.config || {};
    
    const confirm = window.confirm("Edit template: " + t.name + "\nThis will open a form to edit all settings.");
    if (!confirm) return;
    
    // For now, just delete and recreate
    if (window.confirm("Delete and recreate this template? (Simple edit for now)")) {
      await api(`/platform/identity-templates/${id}`, "DELETE");
      toast("Template deleted - please recreate");
      viewIdentityTemplates();
    }
  } catch (e) {
    toast("Error: " + e.message);
  }
}

async function deleteTemplate(id) {
  if (!confirm("Delete this template?")) return;
  try {
    await api(`/platform/identity-templates/${id}`, "DELETE");
    toast("Template deleted");
    viewIdentityTemplates();
  } catch (e) {
    toast("Error: " + e.message);
  }
}

async function wireIdentityTemplates() {
  // Add listeners if needed
}

async function applyTemplate() {
  const tmplId = $("#tmplSelect").value;
  if (!tmplId) return toast("Select a template");
  
  try {
    await api("/platform/identity-templates/" + tmplId + "/apply", "POST", { tenant_id: 1 });
    toast("Template applied");
    viewIdentity();
  } catch (e) {
    toast("Error: " + e.message);
  }
}

async function wireIdentity() {
  // Wire up event listeners for the Identity page
}
