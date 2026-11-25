/* LUXORA Platform — cart domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the cart domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "cart", routes(kit) {
  const { features, stock, CFG, CHECKOUT_LOCKS, T, apiCheckoutOnce, bad, bookings, cartPayload, checkoutTotals, commerceOf, engineFail, fees, get, json, lineterms, money2, ownerFor, pickup, requireAdmin, requireStaff, rules, run, shippingFor, shopperCall, signedIn, trials } = kit;

  function apiCartGet(req, res, url, s) { json(res, 200, cartPayload(s)); }
  function apiCartAdd(req, res, url, s, body) {
    const c = CFG(s);
    /* only a published, live product can be added (an unpublished or trashed one could be bought) */
    const p = get("SELECT * FROM products WHERE tenant_id=? AND id=? AND lifecycle='published' AND deleted_at IS NULL", T(s), body.id);
    if (!p) return bad(res, "Unknown product", 404);
    let skuId = null;
    if (body.sku_id != null && body.sku_id !== "") { const sk = get("SELECT id FROM skus WHERE id=? AND product_id=? AND tenant_id=? AND active=1", Number(body.sku_id), p.id, T(s)); if (!sk) return bad(res, "Unknown variant for this product"); skuId = sk.id; }
    const owner = ownerFor(s);
    const qty = Math.max(1, Math.min(c.commerce.cartMaxQty, Math.floor(Number(body.qty)) || 1));
    /* the line's terms, each checked by the engine that owns it; the same terms add to one line */
    let terms;
    try { terms = lineterms.clean({ tid: T(s), owner, product: p, qty, signedIn: !!s.user_id }, body.terms); }
    catch (e) { if (!e.status) throw e; return bad(res, e.message, e.status); }
    /* a bookable product is bought with the time chosen for it */
    if (!terms.booking && bookings.offer(T(s), p.id)) return bad(res, "Choose a time to book first", 409);
    /* a product a kind of case gates (a prescription item) needs a valid case of that kind on its line */
    try { require("../cases.js").checkGates(T(s), owner, p, terms); } catch (e) { if (!e.status) throw e; return bad(res, e.message, e.status); }
    const line = lineterms.keyOf(terms);
    const lim = Object.keys(terms).length ? lineterms.priceLine({ tid: T(s), owner, product: p, qty }, terms, p.price).maxQty : Infinity;
    /* what a feature says of this line: a seat or an amount to choose, a closed kitchen, a limit */
    const fr = features.rule({ tid: T(s), owner, product: p, qty, terms, sku: skuId });
    if (fr.problems.length) return bad(res, p.title + ": " + fr.problems.join("; "), 409);
    const left = Math.min(Math.floor(stock.available(T(s), p, skuId) / features.engines.get("sell_by_weight").count(T(s), p.id, terms)), fr.maxQty);
    if (!(left > 0)) return bad(res, "Item is sold out");
    const cap = Math.min(c.commerce.cartMaxQty, isFinite(lim) ? lim : Infinity, left);
    const ex = get("SELECT qty FROM cart_items WHERE owner=? AND product_id=? AND line=?", owner, p.id, line);
    if (ex) run("UPDATE cart_items SET qty=?, sku_id=? WHERE owner=? AND product_id=? AND line=?", Math.min(cap, ex.qty + qty), skuId, owner, p.id, line);
    else run("INSERT INTO cart_items(owner,product_id,qty,sku_id,line,terms) VALUES(?,?,?,?,?,?)", owner, p.id, Math.min(cap, qty), skuId, line, JSON.stringify(terms));
    json(res, 200, cartPayload(s));
  }
  function apiCartPut(req, res, url, s, body) {
    const c = CFG(s);
    const owner = ownerFor(s);
    const qty = Number(body.qty);
    if (!(Number.isInteger(qty) && qty >= 1 && qty <= c.commerce.cartMaxQty)) return bad(res, "Invalid quantity");
    if (body.line != null) run("UPDATE cart_items SET qty=? WHERE owner=? AND product_id=? AND line=?", qty, owner, body.id, String(body.line));
    else run("UPDATE cart_items SET qty=? WHERE owner=? AND product_id=?", qty, owner, body.id);
    json(res, 200, cartPayload(s));
  }
  function apiCartDel(req, res, url, s, body, id) {
    const line = url.searchParams.get("line");
    if (line != null) run("DELETE FROM cart_items WHERE owner=? AND product_id=? AND line=?", ownerFor(s), id, line);
    else run("DELETE FROM cart_items WHERE owner=? AND product_id=?", ownerFor(s), id);
    json(res, 200, cartPayload(s));
  }
  /* the checkout page's summary, priced by the same code checkout charges with */
  async function apiCheckoutQuote(req, res, url, s, body) {
    const c = { ...CFG(s), commerce: commerceOf(s) };
    s.__co = { ...(body || {}) };
    const cart = cartPayload(s);
    if (!cart.items.length) return bad(res, "Bag is empty", 400);
    const ship = await shippingFor(s, c, cart, body || {});
    if (ship.error) return bad(res, ship.error, ship.errorStatus);
    const t = checkoutTotals(s, c, cart, ship.shipBase);
    const m = c.commerce;
    json(res, 200, { carrier: ship.carrier, source: ship.source, note: ship.note, free: ship.free, eta: ship.eta,
      pickup: ship.pickup ? { id: ship.pickup.id, name: ship.pickup.name, address: ship.pickup.address, city: ship.pickup.city, hours: ship.pickup.hours } : null,
      rate_id: ship.rate ? ship.rate.id : null,
      rates: ship.rates.map(r => ({ id: r.id, carrier: r.carrier, service: r.service, days: r.days, price: money2(m, r.priceBase) })),
      charges: t.charges.lines.map(l => ({ name: l.name, amount: money2(m, l.amount) })),
      shipFee: money2(m, ship.shipBase), surcharge: money2(m, t.surcharge), gift: money2(m, t.giftUsed), tax: money2(m, t.tax), total: money2(m, t.total) });
  }
  async function apiCheckout(req, res, url, s, body) {
    const key = T(s) + "|" + ownerFor(s);
    if (CHECKOUT_LOCKS.has(key)) return bad(res, "A checkout is already in progress for this bag", 409);
    CHECKOUT_LOCKS.add(key);
    try { return await apiCheckoutOnce(req, res, url, s, body); }
    finally { CHECKOUT_LOCKS.delete(key); }
  }
  function apiTrialsMine(req, res, url, s) { if (signedIn(s, res, "see your trials")) shopperCall(res, () => ({ trials: trials().mine(T(s), ownerFor(s)), ...trials().vocabulary() })); }
  function apiTrialDecide(req, res, url, s, body, id) { if (signedIn(s, res, "decide a trial")) shopperCall(res, () => ({ trial: trials().decide(T(s), ownerFor(s), id, body.action) })); }
  function apiAdminTrials(req, res, url, s) { if (requireStaff(s, res)) shopperCall(res, () => ({ trials: trials().all(T(s)) })); }
  function apiCartTip(req, res, url, s, body) { try { require("../tips.js").setTip(T(s), ownerFor(s), body.amount); json(res, 200, cartPayload(s)); } catch (e) { engineFail(res, e); } }
  function apiAdminCharges(req, res, url, s) { if (requireStaff(s, res)) shopperCall(res, () => ({ rules: fees().rules(T(s)) })); }
  function apiAdminChargeSave(req, res, url, s, body) { if (requireAdmin(s, res)) shopperCall(res, () => ({ rule: fees().saveRule(T(s), body) })); }
  function apiAdminChargeDelete(req, res, url, s, body, code) { if (requireAdmin(s, res)) shopperCall(res, () => fees().removeRule(T(s), decodeURIComponent(code))); }
  function apiAdminTips(req, res, url, s) { if (requireStaff(s, res)) shopperCall(res, () => require("../tips.js").vocabulary(T(s))); }

  return [
    ["POST /api/cart/tip", apiCartTip],
    ["GET /api/trials", apiTrialsMine],
    ["POST /api/trials/:id", (r, re, u, s, b, p) => apiTrialDecide(r, re, u, s, b, p)],
    ["GET /api/admin/trials", apiAdminTrials],
    ["GET /api/admin/charges", apiAdminCharges],
    ["POST /api/admin/charges", apiAdminChargeSave],
    ["DELETE /api/admin/charges/:code", (r, re, u, s, b, p) => apiAdminChargeDelete(r, re, u, s, b, p)],
    ["GET /api/admin/tips", apiAdminTips],
    ["GET /api/cart", apiCartGet],
    ["POST /api/cart", apiCartAdd],
    ["PUT /api/cart", apiCartPut],
    ["DELETE /api/cart/:id", (r, re, u, s, b, p) => apiCartDel(r, re, u, s, b, p)],
    ["POST /api/checkout", apiCheckout],
    ["POST /api/checkout/quote", apiCheckoutQuote]
  ];
} };
