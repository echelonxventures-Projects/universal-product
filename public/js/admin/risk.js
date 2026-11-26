/* LUXORA Platform — the risk domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

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

screen("risk", { render: async () => await vRisk() });
