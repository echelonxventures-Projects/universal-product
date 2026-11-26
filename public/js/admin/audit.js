/* LUXORA Platform — the audit domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

async function vAudit() {
  const a = await api("/admin/audit");
  return `<div class="p-panel"><h2>Audit trail · ${a.entries.length} entries</h2>
    <input class="p-search" placeholder="Filter…" id="auditQ" style="margin-bottom:12px">
    <div class="p-scroll-x"><table class="p-table" id="auditTbl"><thead><tr><th>When</th><th>Actor</th><th>Action</th><th>Entity</th><th>Ref</th><th>Detail</th></tr></thead>
    <tbody>${a.entries.map(e => `<tr><td>${esc(e.created_at)}</td><td>${esc(e.actor_type)} · ${esc(e.actor_name || "")}</td><td><b>${esc(e.action)}</b></td><td>${esc(e.entity || "")}</td><td>${esc(e.entity_id || "")}</td><td class="p-tag">${esc((e.meta || "").slice(0, 90))}</td></tr>`).join("")}</tbody></table></div></div>`;
}
/* ---------- Trash & Retention (governance) ---------- */
async function vTrash() {
  const d = await api("/admin/trash");
  const items = d.items || []; const counts = d.counts || {}; const ret = d.retention || {};
  return `<div class="p-panel"><h2>🗑️ Trash &amp; Retention</h2>
    <p style="color:var(--p-muted);font-size:13px;margin:0 0 12px">Deleting content moves it to the trash (soft delete) — it disappears from the storefront but stays restorable. Retention purges tombstoned rows older than the policy (data-driven, per entity; 0 = keep forever).</p>
    <div class="p-panel"><b>Retention (days; 0 = never purge)</b><div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:6px">
      ${Object.keys({ _default: 1, products: 1, orders: 1, reviews: 1, offers: 1, coupons: 1 }).map(k => `<label style="font-size:12px"><span>${esc(k)}</span><input data-ret="${k}" type="number" value="${ret[k] != null ? ret[k] : ""}" placeholder="—"></label>`).join("")}
      <button class="p-btn sm primary" id="retSave">Save policy</button></div></div>
    <h3>Trashed (${items.length})</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>Entity</th><th>Reference</th><th>Deleted</th><th></th></tr></thead><tbody>
      ${items.map(i => `<tr><td><code>${esc(i.entity)}</code></td><td>${esc(i.id)}</td><td>${esc((i.deleted_at || "").slice(0, 16))}</td><td style="text-align:right"><button class="p-btn sm" data-restore="${esc(i.entity)}" data-id="${esc(i.id)}">Restore</button></td></tr>`).join("") || '<tr><td colspan="4">Trash is empty.</td></tr>'}
    </tbody></table></div>
    <div style="margin-top:10px;display:flex;gap:8px;align-items:center"><button class="p-btn sm danger" id="purgeNow">Purge expired (per retention)</button><span class="p-tag">${Object.entries(counts).filter(x => x[1]).map(x => `${x[0]}: ${x[1]}`).join(" · ") || "nothing trashed"}</span></div></div>`;
}
function wireTrash() {
  const $ = s => document.querySelector(s), $$ = s => Array.from(document.querySelectorAll(s));
  $$("[data-restore]").forEach(b => b.onclick = async () => { try { await api(`/admin/trash/${encodeURIComponent(b.dataset.restore)}/${encodeURIComponent(b.dataset.id)}/restore`, "POST", {}); toast("Restored"); render(); } catch (e) { toast(e.message); } });
  if ($("#retSave")) $("#retSave").onclick = async () => { const patch = {}; $$("[data-ret]").forEach(i => { if (i.value !== "") patch[i.dataset.ret] = Number(i.value); }); try { await api("/admin/retention", "PUT", patch); toast("Retention saved"); render(); } catch (e) { toast(e.message); } };
  if ($("#purgeNow")) $("#purgeNow").onclick = async () => { if (!confirm("Purge tombstoned rows past their retention? This is permanent.")) return; try { const r = await api("/admin/trash/purge", "POST", {}); toast("Purged " + Object.values(r.purged || {}).reduce((a, b) => a + b, 0)); render(); } catch (e) { toast(e.message); } };
}
function wireAudit() {
  $("#auditQ").oninput = e => {
    const q = e.target.value.toLowerCase();
    $$("#auditTbl tbody tr").forEach(tr => tr.style.display = tr.textContent.toLowerCase().includes(q) ? "" : "none");
  };
}

screen("audit", { render: async () => await vAudit(), wire: async () => { wireAudit(); } });
screen("trash", { render: async () => await vTrash(), wire: async () => { wireTrash(); } });
