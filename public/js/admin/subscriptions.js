/* LUXORA Platform — the subscriptions domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

async function vRetention() {
  const [rec, mem] = await Promise.all([api("/admin/recurring", {}), api("/admin/memberships", {})]);
  const scheds = rec.schedules || [];
  const byS = {}; scheds.forEach(s => byS[s.status] = (byS[s.status] || 0) + 1);
  const mems = mem.memberships || [];
  return `<div class="a-head"><h2>🔁 Subscriptions &amp; Members</h2><p class="a-sub">Subscribe &amp; Save recurring delivery schedules + paid membership tiers (benefits apply at checkout). Tiers &amp; frequencies in Data Studio: <code>membershipTiers</code>, <code>recFrequencies</code>.</p></div>
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

screen("retention", { render: async () => await vRetention() });
