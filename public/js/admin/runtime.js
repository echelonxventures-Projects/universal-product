/* LUXORA Platform — the runtime domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

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

screen("monitor", { group: "Overview", label: "📈 Monitor", order: 2, render: async () => await vMonitor() });
