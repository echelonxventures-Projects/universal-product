/* LUXORA Platform — the price_discovery domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

async function vNegotiation() {
  const gate = await coGate("negotiation");
  if (!gate.any) return coOff("offers", "🤝 Offers", gate.off);
  const d = await api("/admin/price-offers", {});
  return `<div class="a-head"><h2>🤝 Offers</h2><p class="a-sub">Shoppers' offers on the store's own products (offers on a shopper's listing are that shopper's to answer). Floors, automatic thresholds and windows are the <code>price_negotiation</code> capability's params.</p></div>
  <div class="a-card"><div class="a-tablewrap"><table class="a-table"><thead><tr><th>product</th><th>qty</th><th>offer</th><th>counter</th><th>state</th><th>expires</th><th></th></tr></thead><tbody>
    ${(d.offers || []).map(o => `<tr><td>${esc(o.product ? o.product.title : "")}</td><td>${o.qty}</td><td>${money(o.amount)}</td><td>${o.counter_amount != null ? money(o.counter_amount) : "—"}</td><td>${stateChip(o.state)}</td><td>${esc(String(o.expires_at || "").slice(0, 16))}</td>
      <td style="white-space:nowrap">${o.awaiting_you ? `<button class="btn-white sm" data-co-post="/admin/price-offers/${o.id}" data-co-body='{"action":"accept"}'>Accept</button> <button class="btn-white sm" data-co-post="/admin/price-offers/${o.id}" data-co-body='{"action":"counter"}' data-co-ask="Your counter price" data-co-field="amount">Counter</button> <button class="btn-white sm" data-co-post="/admin/price-offers/${o.id}" data-co-body='{"action":"refuse"}'>Refuse</button>` : ""}</td></tr>`).join("") || '<tr><td colspan="7">No offers.</td></tr>'}</tbody></table></div></div>`;
}
async function vAuctions() {
  const gate = await coGate("auctions");
  if (!gate.any) return coOff("auctions", "🔨 Auctions", gate.off);
  const d = await api("/admin/auctions", {});
  return `<div class="a-head"><h2>🔨 Auctions</h2><p class="a-sub">Timed auctions with automatic bidding. The bid increments, the last-minute extension and the payment window are the <code>auctions</code> capability's params.</p></div>
  <div class="a-card"><h3>New auction</h3><div class="p-form"><div class="row"><label><span>Product id *</span><input id="auProd"></label><label><span>Starting price *</span><input id="auStart" type="number" step="0.01"></label>
    <label><span>Reserve</span><input id="auRes" type="number" step="0.01"></label><label><span>Buy it now</span><input id="auBn" type="number" step="0.01"></label></div>
    <div class="row"><label><span>Starts (blank: now)</span><input id="auFrom" type="datetime-local"></label><label><span>Ends *</span><input id="auTo" type="datetime-local"></label></div>
    <button class="p-btn primary" id="auSave">Open auction</button></div></div>
  <div class="a-card"><div class="a-tablewrap"><table class="a-table"><thead><tr><th>product</th><th>price</th><th>bids</th><th>reserve</th><th>ends</th><th>state</th><th></th></tr></thead><tbody>
    ${(d.auctions || []).map(a => `<tr><td>${esc(a.product ? a.product.title : "")}</td><td>${money(a.current_price != null ? a.current_price : a.start_price)}</td><td>${a.bids}</td><td>${a.reserve_met ? "met" : "not met"}</td><td>${esc(a.ends_at)}</td><td>${stateChip(a.state)}</td>
      <td>${a.live || (a.state && !a.final_price && !a.bids) ? `<button class="btn-white sm" data-co-post="/admin/auctions/${a.id}/cancel">Cancel</button>` : ""}</td></tr>`).join("") || '<tr><td colspan="7">No auctions.</td></tr>'}</tbody></table></div>
    <button class="btn-white sm" data-co-post="/admin/auctions/tick">Close ended auctions now</button></div>`;
}
function wireAuctions() {
  const b = $("#auSave"); if (b) b.onclick = () => postAndRender("/admin/auctions", { product_id: fieldVal("#auProd").trim(), start_price: Number(fieldVal("#auStart")), reserve_price: fieldVal("#auRes") ? Number(fieldVal("#auRes")) : null, buy_now_price: fieldVal("#auBn") ? Number(fieldVal("#auBn")) : null,
    starts_at: fieldVal("#auFrom") ? new Date(fieldVal("#auFrom")).toISOString() : undefined, ends_at: fieldVal("#auTo") ? new Date(fieldVal("#auTo")).toISOString() : "" }, "POST", "Auction opened");
  wireCoPosts();
}

screen("auctions", { render: async () => await vAuctions(), wire: async () => { wireAuctions(); } });
screen("negotiation", { render: async () => await vNegotiation(), wire: async () => { wireCoPosts(); } });
