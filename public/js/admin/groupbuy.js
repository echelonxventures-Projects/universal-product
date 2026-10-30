/* LUXORA Platform — the group-buy domain's store-console screens
   (_registry/business-domains.json). Loaded after the console shell (public/js/admin.js) in its
   scope; each screen registers its render, its wiring and its place in the nav. */
"use strict";

async function vGroupBuy() {
  const gate = await coGate("groupbuy");
  if (!gate.any) return coOff("group buying", "👥 Group Buying", gate.off);
  const d = await api("/admin/group-buys", {});
  return `<div class="a-head"><h2>👥 Group Buying</h2><p class="a-sub">A lower price when enough shoppers join by a deadline; a group that falls short cancels and refunds every member. The most one member may buy and closing when full are the <code>group_buying</code> capability's params.</p></div>
  <div class="a-card"><h3>New group</h3><div class="p-form"><div class="row"><label><span>Product id *</span><input id="gbProd"></label><label><span>Group price *</span><input id="gbPrice" type="number" step="0.01"></label>
    <label><span>Members needed *</span><input id="gbMin" type="number" min="2" value="2"></label><label><span>Most members</span><input id="gbMax" type="number"></label><label><span>Ends *</span><input id="gbEnd" type="datetime-local"></label></div>
    <button class="p-btn primary" id="gbSave">Open group</button></div></div>
  <div class="a-card"><div class="a-tablewrap"><table class="a-table"><thead><tr><th>title</th><th>price</th><th>members</th><th>ends</th><th>state</th><th></th></tr></thead><tbody>
    ${(d.groups || []).map(g => `<tr><td>${esc(g.title)}</td><td>${money(g.group_price)}</td><td>${g.members} / ${g.min_members}${g.max_members ? " (max " + g.max_members + ")" : ""}</td><td>${esc(g.ends_at)}</td><td>${stateChip(g.state)}</td>
      <td>${g.joinable ? `<button class="btn-white sm" data-co-post="/admin/group-buys/${g.id}/cancel">Cancel &amp; refund</button>` : ""}</td></tr>`).join("") || '<tr><td colspan="6">No groups.</td></tr>'}</tbody></table></div>
    <button class="btn-white sm" data-co-post="/admin/group-buys/tick">Settle ended groups now</button></div>`;
}
function wireGroupBuy() {
  const b = $("#gbSave"); if (b) b.onclick = () => postAndRender("/admin/group-buys", { product_id: fieldVal("#gbProd").trim(), group_price: Number(fieldVal("#gbPrice")), min_members: Number(fieldVal("#gbMin")), max_members: fieldVal("#gbMax") ? Number(fieldVal("#gbMax")) : null,
    ends_at: fieldVal("#gbEnd") ? new Date(fieldVal("#gbEnd")).toISOString() : "" }, "POST", "Group opened");
  wireCoPosts();
}
screen("groupbuy", { group: "Offers", label: "👥 Group Buying", render: vGroupBuy, wire: wireGroupBuy });
