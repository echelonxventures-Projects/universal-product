/* LUXORA Platform — the gift card domain's store-console screens
   (_registry/business-domains.json). Loaded after the console shell (public/js/admin.js) in its
   scope; each screen registers its render, its wiring and its place in the nav. */
"use strict";

/* gift cards (lib/giftcards.js): every card of the store with its last four, value, state and
   recipient; staff issue one (its code is shown once) or void one with a reason. gift_cards is a
   storefront atom: it lights no console leaf of its own (the screen sits in the Offers section,
   like coupons), and when the store does not offer gift cards the API says so and this shows it */
async function vGiftCards() {
  const d = await api("/admin/gift-cards", {}).catch(e => ({ error: e.message, cards: [] }));
  if (d.error) return `<div class="a-head"><h2>🎁 Gift Cards</h2><p class="a-sub">${esc(d.error)}</p></div>`;
  return `<div class="a-head"><h2>🎁 Gift Cards</h2><p class="a-sub">Cards worth ${money(d.min_amount)}–${money(d.max_amount)}, ${Number(d.validity_days) ? "valid " + Number(d.validity_days) + " days" : "never expiring"} — the <code>gift_cards</code> capability's settings. Shoppers buy them as an item${(d.items || []).length ? " (" + d.items.map(x => esc(x.title)).join(", ") + ")" : " — no item is a gift card yet: set its <code>gift_card</code> fact"}; a redeemed card lands in the gift balance, spent first at checkout.</p></div>
  <div class="a-card"><h3>Issue a card</h3><div class="p-form"><div class="row"><label><span>Value *</span><input id="gcvAmt" type="number" step="0.01"></label>
    <label><span>Occasion</span><select id="gcvOcc"><option value="">—</option>${(d.occasions || []).map(o => `<option value="${esc(o.key || o)}">${esc((o.icon ? o.icon + " " : "") + (o.name || o.key || o))}</option>`).join("")}</select></label></div>
    <div class="row"><label><span>Recipient</span><input id="gcvTo"></label><label><span>Their email</span><input id="gcvEmail" type="email"></label><label><span>Holder (owner key)</span><input id="gcvBuyer" placeholder="t1:u:42"></label></div>
    <label><span>Message</span><input id="gcvMsg"></label><button class="p-btn primary" id="gcvIssue">Issue</button><p id="gcvOut" class="a-sub"></p></div></div>
  <div class="a-card"><h3>Cards · ${(d.cards || []).length}</h3><div class="a-tablewrap"><table class="a-table"><thead><tr><th>card</th><th>value</th><th>how</th><th>recipient</th><th>occasion</th><th>until</th><th>state</th><th></th></tr></thead><tbody>
    ${(d.cards || []).map(c => `<tr><td><code>…${esc(c.last4)}</code></td><td>${money(c.amount)}</td><td>${esc(c.source)}${c.order_ref ? " · " + esc(c.order_ref) : ""}</td><td>${esc(c.recipient || "—")}</td><td>${esc(c.occasion || "—")}</td>
      <td>${esc((c.expires_at || "").slice(0, 10) || "—")}</td><td>${stateChip(c.state)}</td><td>${c.redeemable ? `<button class="btn-white sm" data-co-post="/admin/gift-cards/${esc(c.id)}/void" data-co-ask="Why void it?" data-co-field="reason">Void</button>` : ""}</td></tr>`).join("") || '<tr><td colspan="8">No cards yet.</td></tr>'}</tbody></table></div></div>`;
}
function wireGiftCards() {
  const b = $("#gcvIssue");
  if (b) b.onclick = async () => {
    try {
      const r = await api("/admin/gift-cards", "POST", { amount: fieldVal("#gcvAmt"), occasion: fieldVal("#gcvOcc"), recipient: fieldVal("#gcvTo"), recipient_email: fieldVal("#gcvEmail"), buyer: fieldVal("#gcvBuyer"), message: fieldVal("#gcvMsg") });
      $("#gcvOut").innerHTML = `Issued — code <code>${esc(r.card.code)}</code> (shown once; give it to its recipient).`;
    } catch (e) { toast(e.message); }
  };
  wireCoPosts();
}
screen("giftcards", { group: "Offers", label: "🎁 Gift Cards", section: "offers", render: vGiftCards, wire: wireGiftCards });
