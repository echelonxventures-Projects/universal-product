/* LUXORA Platform — the experiments domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

async function vExperiments() {
  const list = await api("/admin/experiments", {});
  return `<div class="a-head"><h2>🧪 Experiments</h2><p class="a-sub">A/B tests with weighted variants — assignment is deterministic per customer (stable hash), conversion tracked per variant with a 95% significance readout. Statuses in Data Studio: <code>expStatuses</code>.</p></div>
  <div class="a-card"><h3>Experiments</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>key</th><th>name</th><th>variants</th><th>status</th><th>metric</th></tr></thead>
      <tbody>${(list.experiments || []).map(e => `<tr><td><code>${esc(e.key)}</code></td><td>${esc(e.name)}</td><td>${(e.variants || []).map(v => `<span class="a-chip">${esc(v.key)}·${(v.share * 100).toFixed(0)}%</span>`).join("")}</td><td><span class="a-chip">${esc(e.status)}</span></td><td>${esc(e.metric)}</td></tr>`).join("") || '<tr><td colspan="5">No experiments yet.</td></tr>'}</tbody></table></div>
  </div>`;
}

screen("experiments", { render: async () => await vExperiments() });
