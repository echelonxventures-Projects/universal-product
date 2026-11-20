/* LUXORA Platform — the cart domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

/* ---------- try and buy (lib/trials.js) ---------- */
async function vTrials() {
  const gate = await coGate("trials");
  if (!gate.any) return coOff("try and buy", "👟 Try and Buy", gate.off);
  const d = await api("/admin/trials", {}).catch(e => ({ trials: [], error: e.message }));
  return `<div class="a-head"><h2>👟 Try and Buy</h2><p class="a-sub">Items on trial: the deposit paid, the window to decide, and what the shopper did — kept (the rest charged) or returned (the deposit back). A closed window keeps what was not returned.</p></div>
  <div class="a-card"><div class="a-tablewrap"><table class="a-table"><thead><tr><th>#</th><th>order</th><th>item</th><th>shopper</th><th>price</th><th>deposit</th><th>decide by</th><th>state</th><th>charged</th><th>refunded</th></tr></thead><tbody>
  ${(d.trials || []).map(t => `<tr><td>${t.id}</td><td>#${t.order_id}</td><td><code>${esc(t.product_id)}</code></td><td>${esc(t.owner)}</td><td>${money(t.unit)} × ${t.qty}</td><td>${money(t.deposit)}</td><td>${esc(t.ends_at)}</td><td>${stateChip(t.state)}</td><td>${t.charged ? money(t.charged) : ""}</td><td>${t.refunded ? money(t.refunded) : ""}</td></tr>`).join("") || `<tr><td colspan="10">${esc(d.error || "Nothing on trial.")}</td></tr>`}</tbody></table></div></div>`;
}
/* ---------- tips (lib/tips.js) ---------- */
async function vTips() {
  const gate = await coGate("tips");
  if (!gate.any) return coOff("tips", "💝 Tips", gate.off);
  const d = await api("/admin/tips", {});
  return `<div class="a-head"><h2>💝 Tips</h2><p class="a-sub">Shoppers add ${esc(d.label)} from ${(d.choices || []).map(money).join(", ")} or their own amount up to ${money(d.max)} — the <code>tips</code> capability's params (⚙️ Capabilities). Each tip is kept on its order.</p></div>`;
}
/* ---------- service fees (lib/fees.js) ---------- */
async function vCharges() {
  const gate = await coGate("fees");
  if (!gate.any) return coOff("service fees", "🧾 Service Fees", gate.off);
  const d = await api("/admin/charges", {});
  return `<div class="a-head"><h2>🧾 Service Fees</h2><p class="a-sub">A fee is charged when its conditions hold — under an order amount, inside a window of the store's local hours, or always — and waived for members or with free shipping where it says.</p></div>
  <div class="a-card"><h3>Fee</h3><div class="p-form">
    <div class="row"><label><span>Code *</span><input id="fcCode"></label><label><span>Name *</span><input id="fcName" placeholder="Small order fee"></label><label><span>Amount</span><input id="fcAmt" type="number" step="0.01"></label><label><span>% of the order</span><input id="fcPct" type="number" step="0.1"></label></div>
    <div class="row"><label><span>Only under an order of</span><input id="fcBelow" type="number" step="0.01"></label><label><span>From hour (local)</span><input id="fcFrom" type="number" min="0" max="23"></label><label><span>To hour</span><input id="fcTo" type="number" min="0" max="23"></label></div>
    <div class="row"><label><input type="checkbox" id="fcMem"> Waived for members</label><label><input type="checkbox" id="fcFree"> Waived with free shipping</label><label><input type="checkbox" id="fcTax"> Taxed</label></div>
    <button class="p-btn primary" id="fcSave">Save fee</button></div></div>
  <div class="a-card"><h3>Fees</h3><div class="a-tablewrap"><table class="a-table"><thead><tr><th>code</th><th>name</th><th>charge</th><th>when</th><th>waived</th><th></th></tr></thead><tbody>
    ${(d.rules || []).map(r => `<tr><td><code>${esc(r.code)}</code></td><td>${esc(r.name)}</td><td>${r.amount ? money(r.amount) : ""}${r.amount && r.percent ? " + " : ""}${r.percent ? r.percent + "%" : ""}${r.taxable ? " · taxed" : ""}</td>
      <td>${r.below_amount != null ? "under " + money(r.below_amount) : "any amount"}${r.from_hour != null ? " · " + r.from_hour + ":00–" + r.to_hour + ":00" : ""}</td><td>${[r.waive_for_members ? "members" : "", r.waive_with_free_shipping ? "free shipping" : ""].filter(Boolean).join(", ") || "—"}</td>
      <td><button class="btn-white sm" data-co-post="/admin/charges/${encodeURIComponent(r.code)}" data-co-method="DELETE">Remove</button></td></tr>`).join("") || '<tr><td colspan="6">No fees.</td></tr>'}</tbody></table></div></div>`;
}
function wireCharges() {
  const save = $("#fcSave"); if (!save) return;
  save.onclick = () => postAndRender("/admin/charges", { code: fieldVal("#fcCode"), name: fieldVal("#fcName"), amount: fieldVal("#fcAmt"), percent: fieldVal("#fcPct"), below_amount: fieldVal("#fcBelow"),
    from_hour: fieldVal("#fcFrom"), to_hour: fieldVal("#fcTo"), waive_for_members: $("#fcMem").checked, waive_with_free_shipping: $("#fcFree").checked, taxable: $("#fcTax").checked }, "POST", "Fee saved");
  wireCoPosts();
}

screen("fees", { group: "Orders & Fulfilment", label: "🧾 Service Fees", order: 9, render: async () => await vCharges(), wire: async () => { wireCharges(); } });
screen("tips", { group: "Orders & Fulfilment", label: "💝 Tips", order: 10, render: async () => await vTips() });
screen("trials", { group: "Orders & Fulfilment", label: "👟 Try and Buy", order: 11, render: async () => await vTrials() });
