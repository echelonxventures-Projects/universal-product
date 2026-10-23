/* LUXORA Platform — the offer domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its render,
   its wiring and its place in the Offers group of the nav. */
"use strict";

async function vGroupBuy() {
  const gate = await coGate("groupbuy");
  if (!gate.any) return coOff("group buying", "👥 Group Buying", gate.off);
  const d = await api("/admin/group-buys", {});
  return `<div class="a-head"><h2>👥 Group Buying</h2><p class="a-sub">A lower price when enough shoppers join by a deadline; a group that falls short cancels and refunds every member. The most one member may buy and closing when full are the <code>group_buying</code> capability's params.</p></div>
  <div class="a-card"><h3>New group</h3><div class="p-form"><div class="row"><label><span>Product id *</span><input id="gbProd"></label><label><span>Group price *</span><input id="gbPrice" type="number" step="0.01"></label>
    <label><span>Members needed *</span><input id="gbMin" type="number" min="2" value="2"></label><label><span>Most members</span><input id="gbMax" type="number"></label><label><span>Ends *</span><input id="gbEnd" type="datetime-local"></label></div>
    <button class="p-btn primary" id="gbSave">Open group</button></div></div>
  <div class="a-card"><div class="a-tablewrap"><table class="a-table"><thead><tr><th>title</th><th>price</th><th>members</th><th>ends</th><th>state</th><th></th></tr></thead><tbody>
    ${(d.groups || []).map(g => `<tr><td>${esc(g.title)}</td><td>${money(g.group_price)}</td><td>${g.members} / ${g.min_members}${g.max_members ? " (max " + g.max_members + ")" : ""}</td><td>${esc(g.ends_at)}</td><td>${stateChip(g.state)}</td>
      <td>${g.joinable ? `<button class="btn-white sm" data-co-post="/admin/group-buys/${g.id}/cancel">Cancel &amp; refund</button>` : ""}</td></tr>`).join("") || '<tr><td colspan="6">No groups.</td></tr>'}</tbody></table></div>
    <button class="btn-white sm" data-co-post="/admin/group-buys/tick">Settle ended groups now</button></div>`;
}
function wireGroupBuy() {
  const b = $("#gbSave"); if (b) b.onclick = () => postAndRender("/admin/group-buys", { product_id: fieldVal("#gbProd").trim(), group_price: Number(fieldVal("#gbPrice")), min_members: Number(fieldVal("#gbMin")), max_members: fieldVal("#gbMax") ? Number(fieldVal("#gbMax")) : null,
    ends_at: fieldVal("#gbEnd") ? new Date(fieldVal("#gbEnd")).toISOString() : "" }, "POST", "Group opened");
  wireCoPosts();
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
    <td class="p-tag">${esc(o.domain || dfl("goipDomains"))}<br>${esc(o.benefit || o.type)}</td>
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
  OFFER_SCOPES = meta.offerScopes || [];
  const types = meta.offerTypes || [], chans = meta.offerChannels || [], dirs = meta.offerDirections || [], scopes = meta.offerScopes || [], funders = meta.offerFunders || [], stacks = meta.stackingPolicies || [], cKinds = meta.couponKinds || [];
  const opt = (arr, lblFn) => arr.map(x => `<option value="${esc(x.key || x)}">${esc(lblFn ? lblFn(x) : (x.name || x))}</option>`).join("");
  /* the value's unit is the offer type's declaration: a percentage, or an amount in the offer's currency */
  const unitOf = o => { const u = (types.find(t => t.key === o.type) || {}).unit; return u === "amount" ? " " + (o.currency || "") : (u || ""); };
  const statusBadge = st => `<span class="badge ${st === "active" ? "published" : "draft"}">${esc(st)}</span>`;
  const row = o => `<tr><td><b>${esc(o.name)}</b>${o.code ? ` <code>${esc(o.code)}</code>` : ""}${o.tenant_id === 0 ? ' <span class="p-tag">GLOBAL</span>' : ""}</td>
    <td>${esc(o.type)}</td><td><span class="p-tag">${esc(o.direction)}</span></td><td>${esc(o.channel)}</td>
    <td>${esc(o.scope_type)}${o.scope && (o.scope.products || o.scope.categories || o.scope.node || o.scope.brands) ? ` <span class="p-tag">${esc([].concat(o.scope.products || o.scope.categories || o.scope.node || o.scope.brands).join(",").slice(0, 30))}</span>` : ""}</td>
    <td>${esc(o.funder)}${o.funder_ref ? ` ${esc(o.funder_ref)}` : ""}</td><td class="num">${esc(o.value)}${esc(unitOf(o))}</td>
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
  /* a scope's value goes in the field its offerScopes row declares (a taxonomy scope takes one node) */
  const readScope = () => { const st = $("#oScope").value, csv = $("#oScopeVal").value.split(",").map(x => x.trim()).filter(Boolean); const row = (OFFER_SCOPES || []).find(r => (r.key || r) === st) || {}; const f = (row.scope || [])[0]; if (!f) return {}; return { [f]: row.match === "taxonomy" ? (csv[0] || "") : csv }; };
  const save = async (id) => {
    const body = { name: $("#oName").value, type: $("#oType").value, value: Number($("#oValue").value), code: $("#oCode").value, channel: $("#oChan").value, scope_type: $("#oScope").value, scope: readScope(), funder: $("#oFunder").value, funder_ref: $("#oFunderRef").value, brand_ref: "", direction: $("#oDir").value, stack_policy: $("#oStack").value, max_discount: Number($("#oMax").value) || 0, min_amount: Number($("#oMin").value) || 0, currency: ($("#oCur") || {}).value || (TT && TT.commerce && TT.commerce.currency) || DFLT.currency, usage_limit: Number($("#oUse").value) || 0, per_owner_limit: Number(($("#oOwner") || {}).value) || 0, priority: Number($("#oPri").value) || 0, starts: $("#oStart").value || null, ends: $("#oEnd").value || null, status: $("#oStatus").value };
    try { await api("/offers" + (id ? "/" + id : ""), id ? "PUT" : "POST", body); toast("Offer saved"); render(); } catch (e) { toast(e.message); }
  };
  $("#oSave").onclick = () => save(window.__oeid || null);
  $$("[data-oedit]").forEach(b => b.onclick = async () => { window.__oeid = b.dataset.oedit; const o = ((await api("/offers")).offers.find(x => String(x.id) === b.dataset.oedit) || {}); $("#oName").value = o.name || ""; $("#oType").value = o.type || "percent"; $("#oValue").value = o.value || 0; $("#oCode").value = o.code || ""; $("#oChan").value = o.channel || dfl("offerChannels"); $("#oScope").value = o.scope_type || "store"; $("#oScopeVal").value = [].concat((o.scope || {}).products || (o.scope || {}).categories || (o.scope || {}).brands || (o.scope || {}).node || []).join(","); $("#oFunder").value = o.funder || "self"; $("#oFunderRef").value = o.funder_ref || ""; $("#oDir").value = o.direction || "discount"; $("#oStack").value = o.stack_policy || "stack_with_others";     $("#oMax").value = o.max_discount || ""; $("#oMin").value = o.min_amount || ""; $("#oUse").value = o.usage_limit || 0; if ($("#oCur")) $("#oCur").value = o.currency || "USD"; if ($("#oOwner")) $("#oOwner").value = o.per_owner_limit || 0; $("#oPri").value = o.priority || 0; $("#oStatus").value = o.status || "active"; $("#oEditHint").textContent = "editing #" + b.dataset.oedit; $("#oSave").textContent = "Update offer"; });
  $$("[data-oret]").forEach(b => b.onclick = async () => { try { await api("/offers/" + b.dataset.oret, "DELETE"); toast("Retired"); render(); } catch (e) { toast(e.message); } });
  $("#cCreate").onclick = async () => { try { await api("/offers/coupons", "POST", { kind: $("#cKind").value, code: $("#cCode").value, value: Number($("#cVal").value), funder: $("#cFunder").value, funder_ref: $("#cFunderRef").value, max_uses: Number($("#cMax").value) || 1, per_owner_limit: Number(($("#cOwner") || {}).value) || 1 }); toast("Coupon created"); render(); } catch (e) { toast(e.message); } };
  $("#cGen").onclick = async () => { try { const r = await api("/offers/coupons/generate", "POST", { count: 10, kind: $("#cKind").value, funder: $("#cFunder").value, funder_ref: $("#cFunderRef").value, value: Number($("#cVal").value), per_owner_limit: Number(($("#cOwner") || {}).value) || 1 }); toast(r.count + " codes (" + r.batch + ")"); render(); } catch (e) { toast(e.message); } };
  $$("[data-cvoid]").forEach(b => b.onclick = async () => { try { await api("/offers/coupons/" + b.dataset.cvoid, "DELETE"); toast("Voided"); render(); } catch (e) { toast(e.message); } });
  $("#pvGo").onclick = async () => { try { const r = await api("/offers/preview", "POST", { amount: Number($("#pvAmt").value), channel: $("#pvChan").value, coupon: $("#pvCode").value }); $("#pvOut").textContent = JSON.stringify({ discount: r.discount, credits: r.credits, freeShip: r.freeShip, netBase: r.netBase, applied: r.applied.map(a => a.name + " (" + a.type + ")") }, null, 1); } catch (e) { $("#pvOut").textContent = "⚠ " + e.message; } };
  $("#wlGo").onclick = async () => { try { const r = await api("/wallet/ledger" + ($("#wlOwner").value ? "?owner=" + encodeURIComponent($("#wlOwner").value) : "")); $("#wlOut").innerHTML = "balance " + money(r.balance) + "<br>" + (r.entries || []).map(e2 => `${esc(e2.kind)} ${Number(e2.amount).toFixed(2)} → ${money(e2.balance_after)} · ${esc((e2.created_at || "").slice(0, 16))}`).join("<br>") || "no entries"; } catch (e) { toast(e.message); } };
}

screen("promotions", { group: "Offers", label: "🎟️ Offers & Coupons", section: "offers", render: vOffers, wire: wireOffers });
screen("goip", { group: "Offers", label: "Ω∞ GOIP", section: "offers", render: vGoip, wire: wireGoip });
screen("groupbuy", { group: "Offers", label: "👥 Group Buying", render: vGroupBuy, wire: wireGroupBuy });
screen("pricematch", { group: "Offers", label: "🏷️ Price Match", render: vCases, wire: wireCases });
screen("tradeins", { group: "Offers", label: "♻️ Trade-ins", render: vCases, wire: wireCases });
