/* LUXORA Platform — the marketplace domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

async function vMarketplace() {
  const [ads, m, rank] = await Promise.all([api("/marketplace/ads", {}), api("/admin/marketplace/metrics", {}), api("/marketplace/rank", { surface: "search", slots: 3 })]);
  const byM = {}; (ads.ads || []).forEach(a => byM[a.bid_model] = (byM[a.bid_model] || 0) + 1);
  const tgt = a => { let t = {}; try { t = JSON.parse(a.target || "{}"); } catch (e) { } return [t.product_id ? "<code>" + esc(t.product_id) + "</code>" : "", (t.keywords || []).map(k => '<span class="a-chip">' + esc(k) + "</span>").join(" "), t.surface ? esc(t.surface) : ""].filter(Boolean).join(" · ") || "—"; };
  return `<div class="a-head"><h2>📣 Marketplace &amp; Ads</h2><p class="a-sub">Ad inventory · GSP bidding · impression/click ledger · last-click attribution · seller KPIs · take-rate settlement. Bid models / attribution models / surfaces in Data Studio: <code>mktBidModels</code>, <code>mktAttribution</code>, <code>mktSurfaces</code>. Sponsored products in search, the reserve price, budgets and schedules are the <code>sponsored_ads</code> capability's.</p></div>
  <div class="a-card"><h3>New sponsored product</h3>
    <div class="p-form"><div class="row"><label><span>Name *</span><input id="adName"></label><label><span>Product id *</span><input id="adProd"></label><label><span>Seller id</span><input id="adSeller"></label></div>
      <div class="row"><label><span>Keywords (comma-separated; blank = every search)</span><input id="adKw"></label>
        <label><span>Surface</span><select id="adSurf"><option value="">any</option>${(ads.surfaces || []).map(x => `<option>${esc(x)}</option>`).join("")}</select></label></div>
      <div class="row"><label><span>Bid model</span><select id="adModel">${(ads.bid_models || []).map(b => `<option value="${esc(b.key)}">${esc(b.name || b.key)}</option>`).join("")}</select></label>
        <label><span>Bid *</span><input id="adBid" type="number" min="0" step="0.01"></label><label><span>Budget (0 = none)</span><input id="adBudget" type="number" min="0" step="0.01" value="0"></label></div>
      <div class="row"><label><span>Starts</span><input id="adStart" type="datetime-local"></label><label><span>Ends</span><input id="adEnd" type="datetime-local"></label></div>
      <button class="p-btn primary" id="adCreate">Create ad</button></div></div>
  <div class="a-card"><h3>Ad inventory</h3>
    <p class="a-sub">${Object.entries(byM).map(([k, v]) => `<span class="a-chip">${esc(k)}·${v}</span>`).join("") || "no active ads"}</p>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>name</th><th>seller</th><th>target</th><th>model</th><th>bid</th><th>spent / budget</th><th>status</th></tr></thead>
      <tbody>${(ads.ads || []).slice(0, 25).map(a => `<tr><td>${esc(a.name)}</td><td>${a.seller_id || "—"}</td><td>${tgt(a)}</td><td><span class="a-chip">${esc(a.bid_model)}</span></td><td>${money(a.bid_amount)}</td><td>${money(a.spent)}${Number(a.budget) > 0 ? " / " + money(a.budget) : ""}</td><td><span class="a-chip">${esc(a.status)}</span></td></tr>`).join("") || '<tr><td colspan="7">No ads yet.</td></tr>'}</tbody></table></div>
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
function wireMarketplace() {
  const b = $("#adCreate"); if (!b) return;
  b.onclick = async () => {
    const kw = $("#adKw").value.split(",").map(x => x.trim()).filter(Boolean);
    const target = Object.assign({ product_id: $("#adProd").value.trim() }, kw.length ? { keywords: kw } : {}, $("#adSurf").value ? { surface: $("#adSurf").value } : {});
    if (!$("#adName").value.trim() || !target.product_id || !(Number($("#adBid").value) > 0)) return toast("Name, product and a bid are required");
    try {
      await api("/admin/marketplace/ads", "POST", { name: $("#adName").value.trim(), seller_id: $("#adSeller").value || null, bid_model: $("#adModel").value, bid_amount: Number($("#adBid").value),
        budget: Number($("#adBudget").value) || 0, target, start_at: $("#adStart").value ? new Date($("#adStart").value).toISOString() : null, end_at: $("#adEnd").value ? new Date($("#adEnd").value).toISOString() : null });
      toast("Ad created"); render();
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
        smIs("seller_onboarding", o.status, "awaiting_review") ? `<button class="p-btn sm primary" data-mktapp="${o.id}" data-v="${esc(smFirst("seller_onboarding", "approved"))}">Approve</button> <button class="p-btn sm danger" data-mktapp="${o.id}" data-v="${esc(smFirst("seller_onboarding", "rejected"))}">Reject</button>` : esc(o.reviewed_by || "—")])}
    <button class="p-btn sm primary" data-act="co-new" data-key="seller_onboarding">+ Apply as seller</button></div>
  <div class="a-card"><h3>Buy-box · product offers</h3>
    <div style="display:flex;gap:8px;margin-bottom:8px;flex-wrap:wrap"><label><span>Product id</span><input id="mktProd" placeholder="VR-ELEC-01" value="${esc(prod)}"></label>
      <button class="p-btn sm" id="mktLoad">Load offers</button>
      <button class="p-btn sm primary" id="mktBb">Recompute buy-box</button></div>
    ${coTbl(["seller", "price", "condition", "fulfilment", "score", "winner"], bb.offers || [],
      o => [esc(String(o.seller_id)), money(o.price), esc(o.condition || "new"), esc(o.fulfillment || dfl("mktFulfillment")), (o.buybox_score || 0).toFixed(2), o.buybox ? '<span class="a-chip">★ featured</span>' : ""])}</div>
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
async function vBrandReg() {
  const gate = await coGate("brandreg");
  if (!gate.any) return coOff("brand registry", "™️ Brand Registry", gate.off);
  const d = await api("/admin/brand-registry", {});
  window.__br = d;
  const owners = (d.claims || []).filter(c => c.owner);
  const kindName = k => ((d.reportKinds || []).find(x => x.key === k) || { name: k }).name;
  return `<div class="a-head"><h2>™️ Brand Registry</h2><p class="a-sub">Sellers prove they own a brand; an approved owner reports infringing offers, and upholding a report moves the offer to the state the <code>brand_registry</code> capability names. Report kinds are the <code>brandReportKinds</code> registry.</p></div>
  <div class="a-card"><h3>Claims</h3>
    <div class="p-form"><div class="row"><label><span>Brand *</span><select id="brBrand">${(d.brands || []).map(b => `<option value="${esc(b.key)}">${esc(b.label)}</option>`).join("")}</select></label>
      <label><span>Seller</span><select id="brSeller"><option value="">— the store —</option>${(d.sellers || []).map(s => `<option value="${s.id}">${esc(s.name)}</option>`).join("")}</select></label></div>
      <div class="row"><label><span>Trademark number</span><input id="brTm"></label><label><span>Trademark office</span><input id="brOffice"></label></div>
      <label><span>Evidence (one item per line)</span><textarea id="brEv" rows="2"></textarea></label>
      <button class="p-btn primary" id="brClaim">Submit claim</button></div>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>brand</th><th>seller</th><th>trademark</th><th>state</th><th>notes</th><th></th></tr></thead>
    <tbody>${(d.claims || []).map(c => `<tr><td>${esc(c.brand)}</td><td>${esc(c.seller ? c.seller.name : "the store")}</td><td>${esc(c.trademark_number || "—")}${c.trademark_office ? " · " + esc(c.trademark_office) : ""}</td>
      <td>${stateChip(c.state)}</td><td>${esc(c.notes || "")}</td><td style="white-space:nowrap">${verbButtons(d.claimActions || [], c, "br-claim")}</td></tr>`).join("") || '<tr><td colspan="6">No claims yet.</td></tr>'}</tbody></table></div></div>
  <div class="a-card"><h3>Infringement reports</h3>
    ${owners.length ? `<div class="p-form"><div class="row"><label><span>Reporting owner *</span><select id="brOwner">${owners.map(c => `<option value="${c.id}">${esc(c.brand)} · ${esc(c.seller ? c.seller.name : "the store")}</option>`).join("")}</select></label>
      <label><span>Kind *</span><select id="brKind">${(d.reportKinds || []).map(k => `<option value="${esc(k.key)}">${esc(k.name)}</option>`).join("")}</select></label></div>
      <div class="row"><label><span>Offer id</span><input id="brOffer"></label><label><span>…or product id</span><input id="brProd"></label><label><span>and seller</span><select id="brRSeller"><option value="">—</option>${(d.sellers || []).map(s => `<option value="${s.id}">${esc(s.name)}</option>`).join("")}</select></label></div>
      <label><span>Details</span><textarea id="brDetails" rows="2"></textarea></label>
      <button class="p-btn primary" id="brReport">File report</button></div>` : '<p class="a-sub">A brand needs an approved owner before anyone can report against it.</p>'}
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>brand</th><th>kind</th><th>product</th><th>offer</th><th>seller</th><th>details</th><th>state</th><th></th></tr></thead>
    <tbody>${(d.reports || []).map(r => `<tr><td>${esc(r.brand)}</td><td>${esc(kindName(r.kind))}</td><td><code>${esc(r.product_id || "—")}</code></td><td>${r.offer ? "#" + r.offer.id + " · " + esc(r.offer.offer_status) : "—"}</td>
      <td>${esc(r.seller_id || "—")}</td><td>${esc(r.details || "")}${r.outcome ? "<br><i>" + esc(r.outcome) + "</i>" : ""}</td><td>${stateChip(r.state)}</td><td style="white-space:nowrap">${verbButtons(d.reportActions || [], r, "br-report")}</td></tr>`).join("") || '<tr><td colspan="8">No reports.</td></tr>'}</tbody></table></div></div>`;
}
function wireBrandReg() {
  const c = $("#brClaim"); if (c) c.onclick = async () => {
    try { await api("/admin/brand-registry/claims", "POST", { brand: $("#brBrand").value, seller_id: $("#brSeller").value || null, trademark_number: $("#brTm").value, trademark_office: $("#brOffice").value, evidence: $("#brEv").value }); toast("Claim submitted"); render(); }
    catch (e) { toast(e.message); }
  };
  const r = $("#brReport"); if (r) r.onclick = async () => {
    try { await api("/admin/brand-registry/reports", "POST", { claim_id: $("#brOwner").value, kind: $("#brKind").value, offer_id: $("#brOffer").value || null, product_id: $("#brProd").value || null, seller_id: $("#brRSeller").value || null, details: $("#brDetails").value }); toast("Report filed"); render(); }
    catch (e) { toast(e.message); }
  };
  $$("[data-br-claim]").forEach(b => b.onclick = async () => {
    const notes = prompt("Notes for the record (optional)", ""); if (notes === null) return;
    try { const x = await api("/admin/brand-registry/claims/" + b.dataset.id, "POST", { action: b.dataset.brClaim, notes }); toast("Claim " + x.claim.state.label); render(); } catch (e) { toast(e.message); }
  });
  $$("[data-br-report]").forEach(b => b.onclick = async () => {
    const outcome = prompt("Outcome, for the record", ""); if (outcome === null) return;
    try { const x = await api("/admin/brand-registry/reports/" + b.dataset.id, "POST", { action: b.dataset.brReport, outcome }); toast("Report " + x.report.state.label + (x.report.offers_affected ? " · " + x.report.offers_affected + " offer(s) moved" : "")); render(); } catch (e) { toast(e.message); }
  });
}
async function vListings() {
  const gate = await coGate("listings");
  if (!gate.any) return coOff("shopper selling", "🏷️ Shopper Listings", gate.off);
  const d = await api("/admin/listings", {});
  const staffVerbs = (d.actions || []).filter(a => a.staff_only);
  return `<div class="a-head"><h2>🏷️ Shopper Listings</h2><p class="a-sub">Items shoppers sell. Review, commission and the holding period before proceeds are credited are the <code>peer_listings</code> capability's params; conditions are the <code>mktConditions</code> registry.</p></div>
  <div class="a-card"><div class="a-tablewrap"><table class="a-table"><thead><tr><th>title</th><th>seller</th><th>price</th><th>sold</th><th>condition</th><th>state</th><th></th></tr></thead><tbody>
    ${(d.listings || []).map(l => `<tr><td>${esc(l.title)}${l.product_id ? ` <code>${esc(l.product_id)}</code>` : ""}<div class="p-tag">${esc((l.description || "").slice(0, 120))}</div></td><td>${esc(l.by || "")}</td><td>${money(l.price)}</td><td>${l.sold}/${l.qty}</td><td>${esc(l.condition || "")}</td><td>${stateChip(l.state)}</td>
      <td style="white-space:nowrap">${staffVerbs.filter(a => (l.next || []).includes(a.to)).map(a => `<button class="btn-white sm" data-co-post="/admin/listings/${l.id}" data-co-body='${esc(JSON.stringify({ action: a.verb }))}' data-co-ask="Notes for the seller (optional)">${esc(a.verb)}</button>`).join(" ")}</td></tr>`).join("") || '<tr><td colspan="7">No listings.</td></tr>'}</tbody></table></div></div>`;
}

screen("brandreg", { group: "Catalogue", label: "™️ Brand Registry", order: 3, render: async () => await vBrandReg(), wire: async () => { wireBrandReg(); } });
screen("marketplace", { group: "Marketing & Growth", label: "📢 Marketplace & Ads", order: 3, render: async () => await vMarketplace(), wire: async () => { wireMarketplace(); } });
screen("sellers", { group: "Sellers & B2B", label: "🏪 Sellers", order: 0, render: async () => await entityTable("seller") });
screen("listings", { group: "Sellers & B2B", label: "🏷️ Shopper Listings", order: 1, render: async () => await vListings(), wire: async () => { wireCoPosts(); } });
screen("mktops", { group: "Business Operations", label: "🏬 Marketplace Ops", order: 1, render: async () => await vMktOps(), wire: async () => { wireMktOps(); } });
