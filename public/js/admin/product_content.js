/* LUXORA Platform — the product_content domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

async function vRichContent() {
  const gate = await coGate("richcontent");
  if (!gate.any) return coOff("rich content", "✨ Rich Content", gate.off);
  const d = await api("/admin/rich-content", {});
  window.__rc = d;
  return `<div class="a-head"><h2>✨ Rich Product Content</h2><p class="a-sub">Brand content below a product's details. The modules and their fields are the <code>contentModules</code> registry; review, the module limit and owner-only publishing are the <code>rich_content</code> capability's params.</p></div>
  <div class="a-card"><h3>Author</h3>
    <div class="p-form"><div class="row"><label><span>Product id *</span><input id="rcProd" placeholder="e.g. LX1A2B3C4D"></label>
      <label><span>On behalf of seller</span><select id="rcSeller"><option value="">— the store —</option>${(d.sellers || []).map(s => `<option value="${s.id}">${esc(s.name)}</option>`).join("")}</select></label></div>
      <div id="rcMods"></div>
      <div class="row"><label><span>Add a module</span><select id="rcKind">${(d.modules || []).map(m => `<option value="${esc(m.key)}">${esc(m.name)}</option>`).join("")}</select></label><button class="btn-white sm" id="rcAdd">＋ Add</button></div>
      <button class="p-btn primary" id="rcSave">Save draft</button></div></div>
  <div class="a-card"><h3>Content</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>product</th><th>version</th><th>modules</th><th>state</th><th>by</th><th>review</th><th></th></tr></thead>
    <tbody>${(d.content || []).map(c => `<tr><td>${esc(c.product ? c.product.title : c.product_id)} <code>${esc(c.product_id)}</code></td><td>v${c.version}</td>
      <td>${c.modules.map(m => `<span class="a-chip">${esc(((d.modules || []).find(x => x.key === m.kind) || { name: m.kind }).name)}</span>`).join(" ")}</td>
      <td>${stateChip(c.state)}</td><td>${esc(c.author || "—")}</td><td>${esc(c.review_notes || "")}</td>
      <td style="white-space:nowrap"><button class="btn-white sm" data-rc-edit="${c.id}">Edit</button> ${verbButtons(d.actions || [], c, "rc-act")}</td></tr>`).join("") || '<tr><td colspan="7">No rich content yet.</td></tr>'}</tbody></table></div></div>`;
}
function wireRichContent() {
  const d = window.__rc || {};
  const box = $("#rcMods"); if (!box) return;
  let mods = [];
  const draw = () => {
    box.innerHTML = mods.map((m, i) => { const def = (d.modules || []).find(x => x.key === m.kind); return def ? rcModuleHtml(def, m, i) : ""; }).join("") || '<p class="a-sub">No modules yet — add one below.</p>';
    $$("[data-rc-drop]").forEach(b => b.onclick = () => { collect(); mods.splice(Number(b.dataset.rcDrop), 1); draw(); });
  };
  /* read what was typed back into the module list before redrawing or saving */
  const collect = () => { $$("[data-rc-mod]").forEach(el => { const m = { kind: el.dataset.kind }; el.querySelectorAll("[data-f]").forEach(f => { m[f.dataset.f] = f.value; }); mods[Number(el.dataset.rcMod)] = m; }); };
  draw();
  $("#rcAdd").onclick = () => { collect(); mods.push({ kind: $("#rcKind").value }); draw(); };
  $("#rcSave").onclick = async () => {
    collect();
    try { const r = await api("/admin/rich-content", "POST", { product_id: $("#rcProd").value.trim(), seller_id: $("#rcSeller").value || null, modules: mods }); toast("Draft saved · v" + r.content.version); render(); }
    catch (e) { toast(e.message); }
  };
  $$("[data-rc-edit]").forEach(b => b.onclick = () => {
    const c = (d.content || []).find(x => String(x.id) === b.dataset.rcEdit); if (!c) return;
    $("#rcProd").value = c.product_id; $("#rcSeller").value = c.seller_id || "";
    mods = c.modules.map(m => Object.assign({}, m)); draw(); window.scrollTo(0, 0);
  });
  $$("[data-rc-act]").forEach(b => b.onclick = async () => {
    const notes = prompt("Notes for the author (optional)", ""); if (notes === null) return;
    try { const r = await api("/admin/rich-content/" + b.dataset.id, "POST", { action: b.dataset.rcAct, notes }); toast("Content " + r.content.state.label); render(); } catch (e) { toast(e.message); }
  });
}

screen("richcontent", { group: "Catalogue", label: "✨ Rich Content", order: 4, render: async () => await vRichContent(), wire: async () => { wireRichContent(); } });
