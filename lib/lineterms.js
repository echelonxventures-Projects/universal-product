/* LUXORA Platform — line terms: what makes one bag line differ from the product's list price,
   and what must happen when it is ordered.

   A line may carry chosen options, a price a seller agreed to, a won auction, a booking, a
   place in a group buy, a substitution preference… Each is owned by its engine, which
   registers a PROVIDER under a term key:

     atom       the capability that must be on for the term to be accepted
     clean      (ctx, value) → the value to keep, or throws an error carrying its status
     price      (ctx, value) → { set?: unit in base currency, add?: per-unit amount, label }
                — `set` replaces the list price (at most one term on a line may set it),
                `add` is added after; `label` is what the bag and the order show
     maxQty     (ctx, value) → the most of this line one bag may hold (optional)
     place      (ctx, value) → called once the order exists, ctx.orderId / ctx.orderNum set

   An engine may also register an ORDER HOOK — (ctx, items) after every order — for what an
   order means to it even without a term (a listed item sold, a seller to pay).

   The cart and checkout know only this module; a new kind of term is a new provider. */
"use strict";

const crypto = require("crypto");
const caps = () => require("./capabilities.js");
const fail = (msg, status) => Object.assign(new Error(msg), { status: status || 400 });

const PROVIDERS = new Map();
const HOOKS = [];
function register(key, provider) { PROVIDERS.set(String(key), provider); }
function onOrder(hook) { HOOKS.push(hook); }

/* a line's key: '' for a plain line, else a short digest of its terms, so the same product
   with different terms is a different line and the same terms add to one line */
const canon = v => (Array.isArray(v) ? "[" + v.map(canon).join(",") + "]" : v && typeof v === "object" ? "{" + Object.keys(v).sort().map(k => JSON.stringify(k) + ":" + canon(v[k])).join(",") + "}" : JSON.stringify(v));
function keyOf(terms) {
  const t = terms || {};
  return Object.keys(t).length ? crypto.createHash("sha256").update(canon(t)).digest("hex").slice(0, 16) : "";
}

/* the terms a shopper sent, each checked by its provider; an unknown key or a term whose
   capability is off is refused, never silently dropped */
function clean(ctx, terms) {
  const t = terms && typeof terms === "object" && !Array.isArray(terms) ? terms : {};
  const out = {};
  let sets = 0;
  for (const [k, v] of Object.entries(t)) {
    if (v == null || v === "") continue;
    const p = PROVIDERS.get(k);
    if (!p) throw fail("Unknown line term: " + k);
    if (p.atom && !caps().on(ctx.tid, p.atom)) throw fail("This store does not offer " + k, 403);
    const kept = p.clean(ctx, v);
    if (kept == null) continue;
    out[k] = kept;
    const pr = p.price ? p.price(ctx, kept) : null;
    if (pr && pr.set != null) sets++;
  }
  if (sets > 1) throw fail("A line can carry only one agreed price (an offer, an auction or a group buy)");
  return out;
}
/* the line's unit price in base currency, its labels, and the most it may hold. A term that
   no longer holds (an offer expired, a hold lapsed) makes the line invalid with its reason. */
function priceLine(ctx, terms, listUnit) {
  let unit = Number(listUnit) || 0, add = 0, maxQty = Infinity;
  const labels = [], problems = [];
  for (const [k, v] of Object.entries(terms || {})) {
    const p = PROVIDERS.get(k);
    if (!p) { problems.push("unknown term " + k); continue; }
    try {
      if (p.atom && !caps().on(ctx.tid, p.atom)) throw fail("no longer offered");
      const pr = p.price ? p.price(ctx, v) : {};
      if (pr.set != null) unit = Number(pr.set);
      if (pr.add) add += Number(pr.add);
      if (pr.label) labels.push(pr.label);
      if (p.maxQty) maxQty = Math.min(maxQty, Number(p.maxQty(ctx, v)) || Infinity);
    } catch (e) { problems.push(e.message); }
  }
  return { unit: +(unit + add).toFixed(4), labels, maxQty, problems };
}
/* after an order is written: every termed line's providers, then the order hooks */
function place(ctx, items) {
  for (const it of items) for (const [k, v] of Object.entries(it.terms || {})) {
    const p = PROVIDERS.get(k);
    if (p && p.place) p.place({ ...ctx, product: it.product, qty: it.qty, unit: it.unit, line: it.line }, v);
  }
  for (const h of HOOKS) { try { h(ctx, items); } catch (e) { console.error("order hook:", e.message); } }
}
const known = () => [...PROVIDERS.keys()];

module.exports = { register, onOrder, keyOf, clean, priceLine, place, known, fail };
