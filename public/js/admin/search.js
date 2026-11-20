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

screen("search", { group: "Storefront", label: "🔎 Search & Discovery", order: 1, render: async () => await vSearch() });
