/* LUXORA Platform — the order domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

async function vSubstitutions() {
  const gate = await coGate("substitutions");
  if (!gate.any) return coOff("substitutions", "🔄 Substitutions", gate.off);
  const oid = window.__subOrder || "";
  const d = oid ? await api("/admin/substitutions/" + encodeURIComponent(oid), {}).catch(e => ({ error: e.message })) : null;
  return `<div class="a-head"><h2>🔄 Substitutions</h2><p class="a-sub">At picking: each line shows the shopper's own choice (the <code>substitutionPolicies</code> registry). Propose a substitute, or mark the line unavailable to refund it. Whether a dearer substitute is charged is the <code>substitutions</code> capability's param.</p></div>
  <div class="a-card"><div class="p-form"><div class="row"><label><span>Order id</span><input id="sbOrder" value="${esc(oid)}"></label><button class="p-btn primary" id="sbLoad">Open order</button></div></div>
    ${d && d.error ? `<p class="a-sub">${esc(d.error)}</p>` : ""}
    ${d && d.lines ? `<div class="a-tablewrap"><table class="a-table"><thead><tr><th>item</th><th>qty</th><th>shopper's choice</th><th>substitute id</th><th></th></tr></thead><tbody>${d.lines.map(l => `<tr><td>${esc(l.title || l.product_id)}</td><td>${l.qty}</td><td>${esc(l.policy ? l.policy.name : "—")}</td>
      <td>${l.policy && l.policy.allows ? `<input data-sb-sub="${esc(l.product_id)}" placeholder="${l.policy.needs_item && l.preference ? esc(l.preference.product_id) : "product id"}" ${l.policy.needs_item ? "disabled" : ""}>` : "—"}</td>
      <td style="white-space:nowrap">${l.policy && l.policy.allows ? `<button class="btn-white sm" data-sb-prop="${esc(l.product_id)}">Propose</button> ` : ""}<button class="btn-white sm" data-sb-un="${esc(l.product_id)}">Unavailable</button></td></tr>`).join("")}</tbody></table></div>
    <h3>Decisions</h3><div class="a-tablewrap"><table class="a-table"><thead><tr><th>item</th><th>substitute</th><th>qty</th><th>refund</th><th>state</th></tr></thead><tbody>${d.substitutions.map(x => `<tr><td><code>${esc(x.product_id)}</code></td><td><code>${esc(x.substitute_id || "—")}</code></td><td>${x.qty}</td><td>${money(x.refund)}</td><td>${stateChip(x.state)}</td></tr>`).join("") || '<tr><td colspan="5">None yet.</td></tr>'}</tbody></table></div>` : ""}</div>`;
}
function wireSubstitutions() {
  const load = $("#sbLoad"); if (!load) return;
  load.onclick = () => { window.__subOrder = fieldVal("#sbOrder").trim(); render(); };
  const oid = window.__subOrder;
  $$("[data-sb-prop]").forEach(b => b.onclick = () => postAndRender("/admin/substitutions/" + encodeURIComponent(oid), { product_id: b.dataset.sbProp, substitute_id: (($$("[data-sb-sub]").find(i => i.dataset.sbSub === b.dataset.sbProp)) || {}).value }, "POST", "Substitute proposed"));
  $$("[data-sb-un]").forEach(b => b.onclick = () => { if (confirm("Refund this line as unavailable?")) postAndRender("/admin/substitutions/" + encodeURIComponent(oid), { product_id: b.dataset.sbUn, unavailable: true }, "POST", "Refunded"); });
}

screen("orders", { render: async () => { await loadSM(); return await entityTable("order", { rowExtra: r => smIs("order", r.status, "shippable") || smIs("order", r.status, "in_transit") ? `<button class="p-btn sm primary" data-act="ship-order" data-id="${esc(r.id)}" data-num="${esc(r.num)}">${smIs("order", r.status, "in_transit") ? "Label" : "Ship"}</button>` : "" }); } });
screen("substitutions", { render: async () => await vSubstitutions(), wire: async () => { wireSubstitutions(); } });
