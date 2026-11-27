/* LUXORA Platform — the material requirements planning screen (lib/mrp.js; _registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope. Bills of materials, the master
   schedule, a planning run and what it suggests, turned into purchase and work orders. */
"use strict";

let mrpItem = null;
async function vMrp() {
  const r = await api("/admin/mrp");
  const b = mrpItem ? await api("/admin/mrp/boms/" + encodeURIComponent(mrpItem)).catch(() => null) : null;
  const tree = (c, d) => c.components.map(x => `<div style="padding-left:${d * 16}px">${esc(x.component_id)} · ${esc(x.title || "")} × ${x.qty}${x.scrap_pct ? ` (+${x.scrap_pct}% lost)` : ""}</div>${tree(x, d + 1)}`).join("");
  const open = r.suggestions.filter(s => s.open);
  return `<div class="a-head"><h2>🏭 Planning (MRP)</h2><p class="a-sub">What to make and buy, and by when: what must be ready, less what is on the shelf and on order, through each item's bill of materials.</p></div>
  <div class="a-card"><h3>Bill of materials</h3><div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end"><label><span>Item</span><input id="mrpI" maxlength="80" value="${esc(mrpItem || "")}"></label><button class="p-btn sm" id="mrpShow">Show</button></div>
    <p class="a-sub">One component a line: item code | quantity | % lost — for example: LX-CMP-001 | 2 | 0</p><textarea id="mrpB" rows="4" style="width:100%">${b ? b.bom.components.map(c => `${c.component_id} | ${c.qty} | ${c.scrap_pct}`).join("\n") : ""}</textarea>
    <button class="p-btn sm primary" id="mrpSave">Save the bill</button>${b ? (b.bom.components.length ? `<div style="margin-top:8px">${tree(b.bom, 0)}</div>` : `<p class="a-sub">No components: it is bought.</p>`) : ""}
    ${coTbl(["item", "", "components", ""], r.boms, x => [esc(x.product_id), esc(x.title || ""), x.components, `<button class="p-btn sm" data-mrp-item="${esc(x.product_id)}">Open</button>`], "No bills of materials yet.")}</div>
  <div class="a-card"><h3>Planning for an item</h3><div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end"><label><span>Item</span><input id="mrpPI" maxlength="80"></label><label><span>Lead time, days</span><input id="mrpPL" type="number" min="0" style="width:80px"></label>
    <label><span>Safety stock</span><input id="mrpPS" type="number" min="0" style="width:80px"></label><label><span>Smallest lot</span><input id="mrpPM" type="number" min="1" value="1" style="width:80px"></label><button class="p-btn sm" id="mrpPGo">Save</button></div></div>
  <div class="a-card"><h3>What must be ready</h3><div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end"><label><span>Item</span><input id="mrpDI" maxlength="80"></label><label><span>Quantity</span><input id="mrpDQ" type="number" min="1" style="width:80px"></label>
    <label><span>By</span><input id="mrpDD" type="date"></label><label><span>Note</span><input id="mrpDN" maxlength="300"></label><button class="p-btn sm" id="mrpDGo">Add</button></div>
    ${coTbl(["item", "", "quantity", "by", "note", ""], r.demand, d => [esc(d.product_id), esc(d.title || ""), d.qty, esc(d.due_date), esc(d.note || ""), `<button class="p-btn sm" data-mrp-undemand="${d.id}">Remove</button>`], "Nothing scheduled.")}</div>
  <div class="a-card"><h3>Plan</h3><div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end"><label><span>Days ahead</span><input id="mrpH" type="number" min="1" max="730" value="${r.run ? r.run.horizon_days : 60}" style="width:80px"></label>
    <button class="p-btn sm primary" id="mrpRun">Run planning</button>${open.length ? `<button class="p-btn sm" id="mrpConv">Make the orders (${open.length})</button>` : ""}</div>
    ${r.run ? `<p class="a-sub"><code>${esc(r.run.ref)}</code> · ${esc(r.run.ran_at)} · ${r.run.suggestions} suggestions · ${r.run.late} late</p>` : ""}
    ${coTbl(["", "item", "quantity", "needed", "on the shelf", "on order", "safety", "by", "order or start by", "from", ""], r.suggestions, s => [esc((r.actions[s.action] || {}).label || s.action), `${esc(s.product_id)} <span class="a-sub">${esc(s.title || "")}</span>`, `<b>${s.qty}</b>`, s.gross, s.available, s.incoming, s.safety, esc(s.need_by),
      esc(s.order_by) + (s.late ? ' <span class="p-tag">late</span>' : ""), esc(s.supplier || ""), s.open ? `<button class="p-btn sm" data-mrp-dismiss="${s.id}">Dismiss</button>` : coBadge(s.status) + (s.made_ref ? ` <code>${esc(s.made_ref)}</code>` : "")], "Run planning to see what to make and buy.")}</div>`;
}
function wireMrp() {
  const go = async (fn, msg) => { try { await fn(); if (msg) toast(msg); render(); } catch (e) { toast(e.message); } };
  const v = id => $(id).value.trim();
  const sh = $("#mrpShow"); if (sh) sh.onclick = () => { mrpItem = v("#mrpI"); render(); };
  document.querySelectorAll("[data-mrp-item]").forEach(b => b.onclick = () => { mrpItem = b.dataset.mrpItem; render(); });
  const sv = $("#mrpSave"); if (sv) sv.onclick = () => go(() => api("/admin/mrp/boms/" + encodeURIComponent(v("#mrpI")), "PUT", { components: v("#mrpB").split("\n").map(l => l.split("|").map(x => x.trim())).filter(x => x[0]).map(([component_id, qty, scrap]) => ({ component_id, qty: Number(qty), scrap_pct: Number(scrap) || 0 })) }), "Saved");
  const pg = $("#mrpPGo"); if (pg) pg.onclick = () => go(() => api("/admin/mrp/items/" + encodeURIComponent(v("#mrpPI")), "PUT", { lead_days: v("#mrpPL") === "" ? null : Number(v("#mrpPL")), safety_stock: Number(v("#mrpPS")) || 0, min_lot: Number(v("#mrpPM")) || 1 }), "Saved");
  const dg = $("#mrpDGo"); if (dg) dg.onclick = () => go(() => api("/admin/mrp/demand", "POST", { product_id: v("#mrpDI"), qty: Number(v("#mrpDQ")), due_date: v("#mrpDD"), note: v("#mrpDN") }), "Added");
  document.querySelectorAll("[data-mrp-undemand]").forEach(b => b.onclick = () => go(() => api("/admin/mrp/demand/" + b.dataset.mrpUndemand, "DELETE"), "Removed"));
  const rn = $("#mrpRun"); if (rn) rn.onclick = () => go(() => api("/admin/mrp/run", "POST", { horizon_days: Number(v("#mrpH")) }), "Planned");
  const cv = $("#mrpConv"); if (cv) cv.onclick = () => go(async () => { const r = await api("/admin/mrp/convert", "POST", {}); toast("Made " + r.made.map(m => m.ref).join(", ")); });
  document.querySelectorAll("[data-mrp-dismiss]").forEach(b => b.onclick = () => go(() => api("/admin/mrp/suggestions/" + b.dataset.mrpDismiss + "/dismiss", "POST", {}), "Dismissed"));
}
screen("mrp", { render: async () => await vMrp(), wire: wireMrp });
