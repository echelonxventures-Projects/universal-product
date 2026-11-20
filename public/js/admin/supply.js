/* LUXORA Platform — the supply domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

async function vPlanning() {
  const [list, pos] = await Promise.all([api("/admin/planning", {}), api("/admin/planning/pos", {})]);
  const st = list.stats || {};
  const buy = (list.replenishments || []).filter(r => r.reorder_qty > 0);
  return `<div class="a-head"><h2>📦 Planning &amp; Replenishment</h2><p class="a-sub">Per-SKU demand forecast from real order history (weighted moving average + trend), reorder point, safety stock and lead-time-aware suggested purchase orders to the primary supplier. Run the plan after order spikes or on a schedule. Statuses &amp; priorities in Data Studio: <code>planStatuses</code>, <code>planPriorities</code>.</p></div>
  <div class="a-cards">
    <div class="a-card"><h3>Overview</h3>
      <div class="a-stats">${[["SKUs tracked", st.skus || 0], ["Active SKUs", st.active_skus || 0], ["Open suggestions", st.open || 0], ["Urgent", st.urgent || 0], ["Below reorder point", st.below_reorder || 0]].map(([k, v]) => `<div><b>${v}</b><span>${k}</span></div>`).join("")}</div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px">
        <button class="btn-yellow" data-act="plan-run">▶ Run plan</button>
        <button class="btn-white" data-act="plan-approve-all" ${buy.length ? "" : "disabled"}>Approve ${buy.length} suggestion${buy.length === 1 ? "" : "s"}</button>
      </div></div>
    <div class="a-card"><h3>Suggested purchase orders</h3>
      <div class="a-tablewrap"><table class="a-table"><thead><tr><th>supplier</th><th>lines</th><th>units</th><th>est. cost</th></tr></thead>
        <tbody>${(pos.purchaseOrders || []).map(p => `<tr><td>${esc(p.supplier_name)}</td><td>${p.lines.length}</td><td>${p.units}</td><td>${p.cost ? esc(p.cost.toFixed(2)) : "—"}</td></tr>`).join("") || '<tr><td colspan="4">No purchase orders — run the plan.</td></tr>'}</tbody></table></div></div>
  </div>
  <div class="a-card"><h3>Replenishment plan</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>sku</th><th>product</th><th>available</th><th>avg/day</th><th>forecast 30d</th><th>lead</th><th>safety</th><th>reorder pt</th><th>reorder qty</th><th>supplier</th><th>priority</th><th>status</th><th></th></tr></thead>
      <tbody>${(list.replenishments || []).map(r => `<tr>
        <td><code>${esc(r.sku_code || r.sku_id)}</code></td><td>${esc(r.product_title || r.product_id)}</td>
        <td>${r.available}</td><td>${(+r.avg_daily).toFixed(1)}</td><td>${r.forecast_30d}</td><td>${r.lead_days}d</td>
        <td>${r.safety_stock}</td><td>${r.reorder_point}</td>
        <td><b>${r.reorder_qty > 0 ? r.reorder_qty : "—"}</b></td>
        <td>${esc(r.supplier_name || "—")}</td>
        <td><span class="a-chip">${esc(r.priority)}</span></td>
        <td><span class="a-chip">${esc(r.status)}</span></td>
        <td>${!["ordered", "received"].includes(r.status) ? `<button class="btn-white sm" data-act="plan-approve" data-id="${r.id}">Approve</button>` : `<code>${esc(r.po_ref || "")}</code>`}</td>
      </tr>`).join("") || '<tr><td colspan="13">No plan yet — run the plan to forecast demand.</td></tr>'}</tbody></table></div>
  </div>`;
}
async function vOpsProc() {
  const d = await api("/admin/operations", {});
  const chip = s => `<span class="a-chip">${esc(s)}</span>`;
  return `<div class="a-head"><h2>🛒 Procurement</h2><p class="a-sub">Purchase requests and their lines. A request above the store's configured <code>approval_threshold</code> cannot advance to approved without a sign-off — the gate is a param, not a policy written in code. Statuses are the Data Studio list <code>opsPrStatuses</code>.</p></div>
  <div class="a-cards">
    <div class="a-card"><h3>Requests</h3>
      <div class="a-stats">${[["Open", (d.stats || {}).procurement ? (d.stats.procurement.open || 0) : 0], ["Shown", (d.requests || []).length]].map(([k, v]) => `<div><b>${v}</b><span>${k}</span></div>`).join("")}</div>
      <div style="margin-top:10px"><button class="btn-yellow" data-act="ops-new-request">＋ New purchase request</button></div></div>
  </div>
  <div class="a-card"><h3>Purchase requests</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>ref</th><th>requested by</th><th>department</th><th>lines</th><th>est. cost</th><th>status</th><th></th></tr></thead>
    <tbody>${(d.requests || []).map(r => { const next = { draft: "submitted", submitted: "approved", approved: "ordered", ordered: "received" }[r.status]; return `<tr>
      <td><code>${esc(r.ref)}</code></td><td>${esc(r.requested_by || "—")}</td><td>${esc(r.department || "—")}</td>
      <td>${r.lines}</td><td>${(+r.est_cost).toFixed(2)}</td><td>${chip(r.status)}</td>
      <td>${next ? `<button class="btn-white sm" data-act="ops-pr-advance" data-id="${r.id}" data-to="${next}">→ ${next}</button>` : ""}</td>
    </tr>`; }).join("") || `<tr><td colspan="7">No purchase requests yet.</td></tr>`}</tbody></table></div></div>`;
}

screen("suppliers", { group: "Supply Chain", label: "🏭 Suppliers", order: 0, render: async () => await entityTable("supplier") + await entityTable("product_supplier") });
screen("ops_proc", { group: "Supply Chain", label: "🛒 Purchase Requests", order: 1, render: async () => await vOpsProc() });
screen("planning", { group: "Supply Chain", label: "📈 Planning & Replenishment", order: 2, render: async () => await vPlanning() });
