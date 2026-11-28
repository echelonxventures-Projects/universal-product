/* LUXORA Platform — the search domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

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

screen("search", { render: async () => await vSearch() });

/* ========== recommendations (lib/recommendations.js): what shoppers are shown, learnt from what is viewed and bought together ==========
   The shelves, the bases and the reasons are the engine's vocabulary; what each shelf earned is its own count. */
let recPv = null;
async function vRecommendations() {
  const r = await api("/admin/recommendations"), st = r.settings, m = r.model;
  const pct = v => v == null ? "—" : v + "%";
  const pvRows = (xs, title) => `<h4>${esc(title)}</h4>${coTbl(["product", "department", "score", "why"], xs, x => [`<code>${esc(x.id)}</code> ${esc(x.title)}`, esc(x.dept), x.score, esc(x.why || "")], "Nothing to show yet.")}`;
  const pv = recPv ? `<div class="a-card"><h3>What they would see</h3>
    ${recPv.shopper ? `<p class="a-sub">${recPv.shopper.personal ? "Their past orders shape these picks." : "Only what they viewed and have in the cart shapes these picks; their past orders do not (no grant for " + esc(r.purpose) + ")."}</p>
      ${pvRows(recPv.shopper.for_you, r.slots.for_you.label)}${pvRows(recPv.shopper.recent, r.slots.recent.label)}${pvRows(recPv.shopper.goes_with, r.slots.goes_with.label)}` : ""}
    ${recPv.product ? pvRows(recPv.product.bought_together, r.slots.bought_together.label) + pvRows(recPv.product.also_viewed, r.slots.also_viewed.label) + pvRows(recPv.product.similar, r.slots.similar.label) : ""}</div>` : "";
  const list = (k, xs, label) => `<label><span>${label}</span><input id="rec_${k}" value="${esc(xs.map(x => x.id).join(", "))}" placeholder="LX-…"></label>
    <div>${xs.map(x => `<span class="a-chip">${esc(x.title)}</span>`).join(" ")}</div>`;
  return `<div class="a-head"><h2>🎯 Recommendations</h2><p class="a-sub">Suggestions learnt from what shoppers view in the same visit and buy in the same order (or within a few weeks). Recent signals count more; a pair is measured against how popular each product is alone, so best-sellers do not crowd everything out. The pairs name nobody. A shopper's past orders shape their picks only on the basis below; what they view in the visit always does.</p></div>
  <div class="a-card"><h3>What has been learnt</h3>
    <p class="a-sub"><span class="a-chip">${m.pairs.buy} bought-together pairs</span> <span class="a-chip">${m.pairs.view} viewed-together pairs</span> <span class="a-chip">${m.products} products with partners</span></p>
    ${coTbl(["rebuilt", "orders read", "pairs kept", "products", "took"], m.runs, x => [esc(x.at), x.orders, x.pairs, x.products, x.ms + " ms"], "Not rebuilt yet — it is rebuilt nightly, or now.")}
    <p><button class="p-btn sm primary" id="recTrain">Rebuild from orders now</button></p></div>
  <div class="a-card"><h3>Shelves · last 30 days</h3>
    ${coTbl(["shelf", "page", "on", "shown", "clicked", "click rate", "bought", "of clicks", "revenue"], r.performance, x => [esc(x.label), esc(x.page), `<input type="checkbox" data-rec-shelf="${esc(x.slot)}"${st.shelves[x.slot] ? " checked" : ""} aria-label="${esc(x.label)} on">`, x.shown, x.clicked, pct(x.clickRate), x.bought, pct(x.buyRate), money(x.revenue)], "")}
    <p class="a-sub">Bought counts an order of a product within ${st.attributionDays} days of opening it from the shelf.</p></div>
  <div class="a-card"><h3>Settings</h3>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:8px">
      <label><span>Past orders shape picks</span><select id="recBasis">${r.bases.map(b => `<option value="${esc(b)}"${b === st.basis ? " selected" : ""}>${b === r.bases[0] ? "only with the shopper's grant" : "unless the shopper withdraws"}</option>`).join("")}</select></label>
      <label><span>A signal halves every (days)</span><input type="number" id="recHalf" min="1" max="3650" value="${st.halfLifeDays}"></label>
      <label><span>Most from one department</span><input type="number" id="recPer" min="1" max="24" value="${st.perDept}"></label>
      <label><span>Products on a shelf</span><input type="number" id="recSize" min="4" max="24" value="${st.shelfSize}"></label>
      <label><span>Days a click counts toward an order</span><input type="number" id="recAttr" min="1" max="30" value="${st.attributionDays}"></label></div>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:8px;margin-top:8px">${list("block", st.block, "Never recommend (product ids)")}${list("boost", st.boost, "Lift these (product ids)")}</div>
    <p><button class="p-btn sm primary" id="recSave">Save</button></p></div>
  <div class="a-card"><h3>Preview</h3>
    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end">
      <label><span>A customer's email</span><input id="recPvEmail" type="email"></label><button class="p-btn sm" id="recPvShopper">Show their picks</button>
      <label><span>A product id</span><input id="recPvProduct"></label><button class="p-btn sm" id="recPvProd">Show its shelves</button></div></div>
  ${pv}`;
}
function wireRecommendations() {
  const go = async (fn, msg) => { try { await fn(); if (msg) toast(msg); render(); } catch (e) { toast(e.message); } };
  const ids = k => $("#rec_" + k).value.split(/[\s,]+/).filter(Boolean);
  const t = $("#recTrain"); if (t) t.onclick = () => go(async () => { const x = await api("/admin/recommendations/train", "POST", {}); toast(`Read ${x.run.orders} orders · kept ${x.run.pairs} pairs`); });
  const sv = $("#recSave"); if (sv) sv.onclick = () => go(() => api("/admin/recommendations", "PUT", { basis: $("#recBasis").value, halfLifeDays: Number($("#recHalf").value), perDept: Number($("#recPer").value),
    shelfSize: Number($("#recSize").value), attributionDays: Number($("#recAttr").value), block: ids("block"), boost: ids("boost") }), "Saved");
  document.querySelectorAll("[data-rec-shelf]").forEach(i => i.onchange = () => go(() => api("/admin/recommendations", "PUT", { shelves: { [i.dataset.recShelf]: i.checked } }), "Saved"));
  const ps = $("#recPvShopper"); if (ps) ps.onclick = () => go(async () => { recPv = await api("/admin/recommendations/preview", { email: $("#recPvEmail").value }); });
  const pp = $("#recPvProd"); if (pp) pp.onclick = () => go(async () => { recPv = await api("/admin/recommendations/preview", { product: $("#recPvProduct").value }); });
}
screen("recommendations", { render: async () => await vRecommendations(), wire: wireRecommendations });
