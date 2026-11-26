/* LUXORA Platform — the catalog domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

/* ---------- the platform master: what this store may do with it, and what it has proposed ----------
   A store never edits the master: it proposes, and the global platform reviews each proposal
   (lib/master-contributions.js). The actions, kinds and statuses all come from the API. */
async function vMasterContrib() {
  const [p, c] = await Promise.all([api("/tenant/master/permissions"), api("/tenant/master/contributions")]);
  const perms = p.permissions || [], acts = p.actions || [], kinds = p.kinds || [];
  const permRow = x => `<tr><td>${esc((x.scope || []).length ? x.scope.length + " part(s) of the master" : "the whole master")}</td><td>${esc((x.actions || []).join(", "))}</td><td>${esc(x.review || "")}</td><td>${esc((x.visible || []).join(", ") || "all")}</td></tr>`;
  const conRow = x => `<tr><td>${esc(x.action)}</td><td><code>${esc(x.target || "—")}</code></td><td><code>${esc(JSON.stringify(x.patch || x.proposal || {}).slice(0, 80))}</code></td><td>${stateChip(x.state)}</td><td>${esc(x.placement || "")}</td><td>${esc(x.reason || "")}</td>
    <td>${x.awaiting ? `<button class="btn-white sm" data-mc-withdraw="${esc(x.uid)}">Withdraw</button>` : ""}</td></tr>`;
  return `<div class="a-head"><h2>🤝 Master Contributions</h2><p class="a-sub">The platform master is the global platform's. What this store may do with it is its permissions; every change it proposes is reviewed there, then applied to the master, added as new, attached as an addendum, or rejected with a reason.</p></div>
  <div class="a-card"><h3>Permissions</h3><div class="a-tablewrap"><table class="a-table"><thead><tr><th>covers</th><th>actions</th><th>review</th><th>visible attributes</th></tr></thead><tbody>${perms.map(permRow).join("") || '<tr><td colspan="4">No permissions yet — the platform grants them.</td></tr>'}</tbody></table></div></div>
  <div class="a-card"><h3>Propose</h3><div class="a-form">
    <label>Proposal <select id="mcAction">${acts.map(a => `<option value="${esc(a.name)}" data-target="${a.target ? 1 : 0}">${esc((a.title && (a.title.en || Object.values(a.title)[0])) || a.name)}</option>`).join("")}</select></label>
    <label>On (master key or id) <input id="mcTarget" placeholder="leave empty for an addition"></label>
    <label>Title <input id="mcTitle"></label>
    <label>Facts (JSON) <input id="mcFacts" placeholder='{"colour":"teal"}'></label>
    <label>Kind (an addition) <select id="mcKind">${kinds.map(k => `<option value="${esc(k.kind)}">${esc((k.title && (k.title.en || Object.values(k.title)[0])) || k.name)}</option>`).join("")}</select></label>
    <label>Under (taxonomy key, an addition) <input id="mcAt"></label>
    <button class="btn" id="mcPropose">Propose</button></div></div>
  <div class="a-card"><h3>Proposals</h3><div class="a-tablewrap"><table class="a-table"><thead><tr><th>proposal</th><th>on</th><th>change</th><th>state</th><th>landed as</th><th>reason</th><th></th></tr></thead><tbody>${(c.contributions || []).map(conRow).join("") || '<tr><td colspan="7">Nothing proposed yet.</td></tr>'}</tbody></table></div></div>`;
}
function wireMasterContrib() {
  const val = id => (document.querySelector(id) || {}).value || "";
  const go = document.querySelector("#mcPropose");
  if (go) go.onclick = () => {
    let facts = null;
    try { facts = val("#mcFacts").trim() ? JSON.parse(val("#mcFacts")) : null; } catch (e) { return toast("Facts must be JSON"); }
    const action = val("#mcAction"), title = val("#mcTitle").trim();
    const patch = Object.assign({}, title ? { title: { en: title } } : {}, facts ? { facts } : {});
    const body = val("#mcTarget").trim() ? { action, target: val("#mcTarget").trim(), patch }
      : { action, proposal: { kind: val("#mcKind"), at: val("#mcAt").trim() ? [val("#mcAt").trim()] : [], title: { en: title }, facts: facts || undefined } };
    postAndRender("/tenant/master/contributions", body, "POST", "Proposed — the platform reviews it");
  };
  $$("[data-mc-withdraw]").forEach(b => b.onclick = () => postAndRender("/tenant/master/contributions/" + encodeURIComponent(b.dataset.mcWithdraw) + "/withdraw", {}, "POST", "Withdrawn"));
}
/* ---------- global catalog: platform-supplied products this store may list ----------
   The platform populates the global catalogue automatically (one canonical product per
   universe the constitution declares) and manually (console rows). A store admin may
   pull one into their own catalogue ONLY IF the platform has permitted it — the gate is
   server-side; this view never decides, it reports what the platform allows. */
async function vGcatalog() {
  let items = [];
  try { ({ items } = await api("/tenant/catalog/importable")); } catch (e) { toast(e.message); }
  const permitted = items.filter(i => i.permitted && !i.listed);
  const listed = items.filter(i => i.listed);
  const denied = items.filter(i => !i.permitted);
  const row = i => `<tr><td><b>${esc(i.name)}</b><div style="font-size:12px;color:var(--p-muted)">${esc(i.sku)}</div></td>
    <td class="p-tag">${esc(i.universe)}</td><td>${esc(i.type)}</td>
    <td>${i.listed ? '<span class="badge active">On your shelf</span>' : i.permitted ? '<button class="p-btn primary sm" data-gimp="' + i.id + '">Add to my store</button>' : '<span class="badge">🔒 ' + esc(i.reason || "Not permitted") + '</span>'}</td></tr>`;
  return `
  <div class="p-panel"><h2>🌐 Global Catalog — platform products</h2>
    <p style="margin:0 0 14px;color:var(--p-muted);font-size:13px">Every product archetype the platform supports (UPIP §1: Physical, Digital, OTT, Cloud, API, AI, Financial, Quantum, Future Unknown…), populated automatically from the constitution and extended by the platform admin. You may list one here <b>only when the platform has permitted your store</b> — import is idempotent and never counts against your plan quota.</p>
    <div class="p-stats" style="margin-bottom:14px">
      <div class="p-stat"><em>Available to you</em><b>${permitted.length}</b></div>
      <div class="p-stat"><em>Already on your shelf</em><b>${listed.length}</b></div>
      <div class="p-stat"><em>Not yet permitted</em><b>${denied.length}</b><small>request from the platform admin</small></div>
    </div>
    <div class="p-scroll-x"><table class="p-table"><thead><tr><th>Product</th><th>Universe</th><th>Type</th><th></th></tr></thead>
    <tbody>${items.map(row).join("") || '<tr><td colspan="4" class="p-empty">The global catalogue is empty</td></tr>'}</tbody></table></div></div>`;
}
function wireGcatalog() {
  $$("[data-gimp]").forEach(b => b.onclick = async () => {
    try {
      const r = await api("/tenant/catalog/import", "POST", { global_product_id: b.dataset.gimp });
      toast("Imported as " + r.type + (r.updated ? " (refreshed)" : ""));
      render();
    } catch (e) { toast(e.message); }
  });
}

screen("products", { render: async () => await entityTable("product") });
screen("skus", { render: async () => await entityTable("sku") + await entityTable("inventory") + await entityTable("warehouse") + await entityTable("variant_group") });
screen("brands", { render: async () => await entityTable("brand") });
screen("taxonomy", { render: async () => await entityTable("taxonomy") });
screen("attributes", { render: async () => await entityTable("attribute") });
screen("gcatalog", { render: async () => await vGcatalog(), wire: async () => { wireGcatalog(); } });
screen("mastercontrib", { render: async () => await vMasterContrib(), wire: async () => { wireMasterContrib(); } });

/* ---------- size guides and pre-orders ---------- */
async function vSizeGuides() {
  const gate = await coGate("sizeguides");
  if (!gate.any) return coOff("size guides", "📏 Size Guides", gate.off);
  const d = await api("/admin/size-guides", {});
  return `<div class="a-head"><h2>📏 Size Guides</h2><p class="a-sub">An item shows the guide that names it, else its brand's, else its department's. One row per line, cells separated by commas; the first row is the heading.</p></div>
  <div class="a-card"><div class="p-form"><div class="row"><label><span>Name</span><input id="sgName"></label><label><span>For</span><select id="sgScope">${d.scopes.map(x => `<option>${esc(x)}</option>`).join("")}</select></label><label><span>Item id, brand or department</span><input id="sgTarget"></label></div><label><span>Table</span><textarea id="sgRows" rows="5" placeholder="Size, Chest (cm), Waist (cm)"></textarea></label><label><span>Note</span><input id="sgNote"></label><button class="p-btn primary" id="sgAdd">Add guide</button></div>
  <div class="a-tablewrap"><table class="a-table"><thead><tr><th>guide</th><th>for</th><th>sizes</th><th></th></tr></thead><tbody>${d.guides.map(x => `<tr><td>${esc(x.name)}</td><td>${esc(x.scope)}: ${esc(x.target)}</td><td>${x.rows.length - 1}</td><td><button class="btn-white sm" data-sgdel="${x.id}">Remove</button></td></tr>`).join("") || '<tr><td colspan="4">No guides yet.</td></tr>'}</tbody></table></div></div>`;
}
function wireSizeGuides() {
  const b = $("#sgAdd"); if (b) b.onclick = () => postAndRender("/admin/size-guides", { name: fieldVal("#sgName"), scope: fieldVal("#sgScope"), target: fieldVal("#sgTarget"), rows: fieldVal("#sgRows"), note: fieldVal("#sgNote") }, "POST", "Guide added");
  $$("[data-sgdel]").forEach(x => x.onclick = async () => { try { await api("/admin/size-guides/" + x.dataset.sgdel, "DELETE"); render(); } catch (e) { toast(e.message); } });
}
async function vPreorders() {
  const gate = await coGate("preorders");
  if (!gate.any) return coOff("pre-orders", "⏳ Pre-orders", gate.off);
  const d = await api("/admin/preorders", {});
  return `<div class="a-head"><h2>⏳ Pre-orders</h2><p class="a-sub">Until its day an item sells from the promise, not from the shelf. On that day it sells from the shelf again.</p></div>
  <div class="a-card"><div class="p-form"><div class="row"><label><span>Product id</span><input id="poId"></label><label><span>Ships on</span><input id="poDay" type="date"></label><label><span>Most to promise</span><input id="poMax" type="number" min="1"></label><button class="p-btn primary" id="poAdd">Save</button></div></div>
  <div class="a-tablewrap"><table class="a-table"><thead><tr><th>item</th><th>ships on</th><th>promised</th><th></th></tr></thead><tbody>${d.preorders.map(x => `<tr><td>${esc(x.title)}</td><td>${esc(x.ships_on)}${x.open ? "" : " · now selling"}</td><td>${x.taken} / ${x.max_qty}</td><td><button class="btn-white sm" data-podel="${esc(x.product_id)}">Remove</button></td></tr>`).join("") || '<tr><td colspan="4">Nothing on pre-order.</td></tr>'}</tbody></table></div></div>`;
}
function wirePreorders() {
  const b = $("#poAdd"); if (b) b.onclick = () => postAndRender("/admin/preorders", { product_id: fieldVal("#poId").trim(), ships_on: fieldVal("#poDay"), max_qty: Number(fieldVal("#poMax")) }, "POST", "Saved");
  $$("[data-podel]").forEach(x => x.onclick = async () => { try { await api("/admin/preorders/" + encodeURIComponent(x.dataset.podel), "DELETE"); render(); } catch (e) { toast(e.message); } });
}
screen("sizeguides", { render: async () => await vSizeGuides(), wire: async () => { wireSizeGuides(); } });
screen("preorders", { render: async () => await vPreorders(), wire: async () => { wirePreorders(); } });
