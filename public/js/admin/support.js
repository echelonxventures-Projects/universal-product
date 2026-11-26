/* LUXORA Platform — the support domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

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

screen("enquiries", { render: view => vCases(view), wire: () => wireCases() });
screen("helpdesk", { render: async () => await vHelpdesk() });
