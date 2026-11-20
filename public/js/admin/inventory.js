/* LUXORA Platform — the inventory domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

async function vSerialized() {
  const products = ((await api("/meta/entity/product")).rows || []).map(p => ({ id: p.id, t: p.title || p.id }));
  return `<div class="p-panel"><div style="display:flex;gap:8px;align-items:flex-end;flex-wrap:wrap;margin-bottom:14px">
    <label><span>Bulk-generate units for</span><select id="sbProd">${products.map(p => `<option value="${esc(p.id)}">${esc(String(p.t).slice(0, 40))}</option>`).join("")}</select></label>
    <label><span>Count</span><input id="sbCount" type="number" value="5" min="1" max="500"></label>
    <label><span>Prefix (optional)</span><input id="sbPrefix" placeholder="e.g. SN-2026"></label>
    <button class="p-btn primary sm" id="sbGo">Generate</button></div>
    ${await entityTable("serialized")}</div>`;
}
function wireSerialized() { const g = $("#sbGo"); if (g) g.onclick = async () => { try { const r = await api("/admin/serialized/bulk", "POST", { product_id: $("#sbProd").value, count: Number($("#sbCount").value) || 1, prefix: $("#sbPrefix").value || undefined }); toast("Generated " + r.created + " serialized units"); render(); } catch (e) { toast(e.message); } }; }

screen("serialized", { group: "Orders & Fulfilment", label: "🔢 Serialized Items", order: 19, render: async () => await vSerialized(), wire: async () => { wireSerialized(); } });
