/* LUXORA Platform — gift cards (the Offers domain), on the kernel.

   A card is a code with a value. It comes to be in one of three ways — its `source`:
     bought      an item whose facts carry the capability's `fact` is ordered; each unit becomes a
                 card for the amount its `gift_card` line term chose (a denomination or any amount
                 within the store's minimum and maximum), addressed to the recipient the line names
     issued      staff issue one (a goodwill gesture, a prize, a refund as a card)
     granted     an incentive grants one (the incentive engine's gift-card benefit)
   The card is a kernel node: amount, unit, state, occasion and dates are attributes in time; the
   code, recipient, address, message, buyer and redeemer are sealed; it is found by a keyed blind
   index of its code. Whoever bought or was given it holds it (the held hierarchy) and sees its code.
   Redeeming moves the value into the redeemer's wallet of the definition the capability names
   (the gift balance), which checkout spends first. A card may be checked for its balance by code,
   voided by staff with a reason, and expires after the store's validity — the gift_card machine.
   Capability: gift_cards. */
"use strict";

const crypto = require("crypto");
const SEED = require("./seed/giftcards.json");
const states = require("./states.js");
const lineterms = require("./lineterms.js");
const K = () => require("./kernel.js");
const W = () => require("./wallet.js");
const caps = () => require("./capabilities.js");
const sec = () => require("./security.js");
const KEY = SEED.keys, EVT = SEED.events, M = KEY.machine;
const fail = (msg, status, code) => Object.assign(new Error(msg), { status: status || 400, code: code || "" });
const tx = fn => K().internal.tx(fn);
const tenantNs = tid => KEY.tenantNamespace + ":" + Number(tid);
const nowIso = () => new Date().toISOString();
const tell = (...a) => require("./tell.js").tell(...a);

/* ---------- declarations ---------- */
function declare() {
  const k = K();
  const cur = k.kindOf(SEED.kind.kind, SEED.namespace);
  if (!cur || SEED.kind.attributes.some(a => !cur.attributes.some(x => x.key === a.key && x.type === a.type && !!x.sensitive === !!a.sensitive))) k.defineKind({ ...SEED.kind, namespace: SEED.namespace }, "giftcards.seed");
  if (!k.hierarchyOf(SEED.hierarchy.hierarchy, SEED.namespace)) k.defineHierarchy({ ...SEED.hierarchy, namespace: SEED.namespace }, "giftcards.seed");
}
function params(tid) {
  if (!caps().on(Number(tid), KEY.capability)) throw fail("Gift cards are not offered by this store", 403, "feature_off");
  return caps().cap(Number(tid), KEY.capability);
}

/* ---------- codes ---------- */
const ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";   /* no 0/O, 1/I — read off a card */
const newCode = len => Array.from(crypto.randomBytes(Math.max(8, Number(len) || 16)), b => ALPHABET[b % ALPHABET.length]).join("");
const normal = code => String(code || "").toUpperCase().replace(/[^A-Z0-9]/g, "");
const indexOf = (tid, code) => sec().blindIndex(normal(code), tenantNs(tid) + "/" + KEY.kind);
function nodeOf(tid, code) {
  const uid = K().resolveIdentifier(KEY.codeScheme, indexOf(tid, code));
  if (!uid) return null;
  const a = K().attributes(uid);
  return Number(a.tenant) === Number(tid) ? { uid, a } : null;
}

/* ---------- what a card is shown as: the code only to whoever holds it ---------- */
function present(uid, a, withCode) {
  const u = W().unitOf(a.unit);
  return { id: uid, amount: W().toMajor(a.amount, u.decimals), unit: a.unit, state: states.display(M, a.status), redeemable: states.is(M, a.status, "redeemable"),
    source: a.source, occasion: a.occasion || "", order_ref: a.order_ref || "", expires_at: a.expires_at || null, last4: a.last4,
    recipient: a.recipient || "", recipient_email: a.recipient_email || "", message: a.message || "", redeemed_at: a.redeemed_at || null,
    ...(withCode ? { code: a.code } : {}) };
}
function move(uid, a, action, patch, actor) {
  const to = states.actionTarget(M, action);
  if (!to || !states.can(M, a.status, to)) throw fail("That cannot be done to this card now", 409, "card_state");
  const mv = states.apply(M, { tenantId: Number(a.tenant), from: a.status, to, row: a });
  K().record(uid, { status: to, ...(mv.patch.decided_at ? { decided_at: String(mv.patch.decided_at) } : {}), ...(patch || {}) }, {}, String(actor || ""));
  K().append(EVT.moved, { namespace: tenantNs(a.tenant), subject: uid, actor: String(actor || ""), payload: { from: a.status, to } });
  return K().attributes(uid);
}
/* a card past its validity lapses the moment it is looked at, as well as by the sweep */
function lapse(uid, a) {
  if (a.expires_at && a.expires_at < nowIso() && states.is(M, a.status, "redeemable")) return move(uid, a, "expire", null, "expiry");
  return a;
}

/* ---------- issuing ---------- */
function issue(tid, input, actor) {
  const P = params(tid);
  const i = input || {};
  const unit = W().unitOf(i.unit || require("./defaults.js").currency(tid));
  const minor = W().toMinor(i.amount, unit.decimals);
  if (minor < W().toMinor(P.min_amount, unit.decimals) || minor > W().toMinor(P.max_amount, unit.decimals)) throw fail(`A card is worth between ${P.min_amount} and ${P.max_amount}`, 400, "amount_range");
  const sources = require("./registry.js").list("giftCardSources").map(x => x.key || x);
  if (!sources.includes(i.source)) throw fail("Say how the card came to be: " + sources.join(", "));
  const source = i.source;
  const occasion = String(i.occasion || "");
  if (occasion && !require("./registry.js").list("giftCardOccasions").some(o => (o.key || o) === occasion)) throw fail("Unknown occasion: " + occasion);
  const email = String(i.recipient_email || "").trim();
  if (email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) throw fail("That is not an email address");
  const code = newCode(P.code_length);
  const days = Number(P.validity_days) || 0;
  return tx(() => {
    const uid = K().createNode(KEY.kind, { namespace: tenantNs(tid), identifiers: { [KEY.codeScheme]: indexOf(tid, code) }, attributes: {
      tenant: Number(tid), amount: minor, unit: unit.code, status: states.initial(M), source, occasion, order_ref: String(i.order_ref || ""),
      expires_at: days ? new Date(Date.now() + days * 86400000).toISOString() : "", last4: code.slice(-4), code,
      recipient: String(i.recipient || "").slice(0, 80), recipient_email: email.slice(0, 200), message: String(i.message || "").slice(0, 500), buyer: String(i.buyer || "") } }, String(actor || "system"));
    if (i.buyer) K().place(KEY.held, uid, W().holderOf(tid, String(i.buyer), true, actor), { namespace: tenantNs(tid) }, String(actor || "system"));
    K().append(EVT.issued, { namespace: tenantNs(tid), subject: uid, actor: String(actor || "system"), payload: { source, amount: minor, unit: unit.code } });
    if (i.buyer) tell(tid, String(i.buyer), "gift_card", "Your gift card is ready", `${W().toMajor(minor, unit.decimals)} ${unit.code}${i.recipient ? " for " + i.recipient : ""} — its code is under Your activity`, "orders.html");
    return present(uid, K().attributes(uid), true);
  });
}

/* ---------- redeeming, checking, voiding ---------- */
function redeem(tid, code, owner) {
  const P = params(tid);
  const n = nodeOf(tid, code);
  if (!n) throw fail("No card has that code", 404, "card_unknown");
  const a = lapse(n.uid, n.a);
  if (!states.is(M, a.status, "redeemable")) throw fail("This card has been " + states.display(M, a.status).label.toLowerCase(), 409, "card_state");
  return tx(() => {
    const w = W().walletOf(tid, owner, a.unit, P.wallet_definition);
    const u = W().unitOf(a.unit);
    const out = W().post(tid, { op: W().defaultOp("in"), wallet: w.id, amount: W().toMajor(a.amount, u.decimals).toFixed(u.decimals), ref: "gift_card:" + n.uid, idem: "gift_card:" + n.uid, actor: String(owner) });
    move(n.uid, a, "redeem", { redeemed_by: String(owner), redeemed_at: nowIso() }, owner);
    /* the redeemer holds the card too, so it shows among their cards */
    const holder = W().holderOf(tid, String(owner), true, owner);
    if (!K().parents(KEY.held, n.uid).includes(holder)) K().place(KEY.held, n.uid, holder, { namespace: tenantNs(tid) }, String(owner));
    K().append(EVT.redeemed, { namespace: tenantNs(tid), subject: n.uid, actor: String(owner), payload: { journal: out.journal.id } });
    return { card: present(n.uid, K().attributes(n.uid), false), wallet: out.wallet };
  });
}
/* what a code is worth — nothing about who bought or holds it */
function check(tid, code) {
  params(tid);
  const n = nodeOf(tid, code);
  if (!n) throw fail("No card has that code", 404, "card_unknown");
  const a = lapse(n.uid, n.a);
  const c = present(n.uid, a, false);
  return { amount: c.amount, unit: c.unit, state: c.state, redeemable: c.redeemable, expires_at: c.expires_at, last4: c.last4 };
}
function voidCard(tid, id, reason, actor) {
  params(tid);
  if (!String(reason || "").trim()) throw fail("Say why", 400, "reason_required");
  const a = K().attributes(String(id));
  if (Number(a.tenant) !== Number(tid)) throw fail("Card not found", 404, "card_unknown");
  return present(String(id), move(String(id), a, "void", { reason: String(reason).slice(0, 300) }, actor), false);
}

/* ---------- listing ---------- */
const cardsIn = tid => K().nodes(KEY.kind, tenantNs(tid)).map(n => (typeof n === "string" ? n : n.uid));
function list(tid) { params(tid); return cardsIn(tid).map(uid => present(uid, lapse(uid, K().attributes(uid)), false)).reverse(); }
/* a party's own cards — bought, given, redeemed — with their codes */
function mine(tid, owner) {
  params(tid);
  const h = W().holderOf(tid, String(owner), false);
  return h ? K().children(KEY.held, h, { namespace: tenantNs(tid) }).map(uid => present(uid, lapse(uid, K().attributes(uid)), true)) : [];
}
function sweepAll() {
  let n = 0;
  for (const t of require("./db.js").all("SELECT id FROM tenants")) {
    if (!caps().on(t.id, KEY.capability)) continue;
    for (const uid of cardsIn(t.id)) { const a = K().attributes(uid); if (lapse(uid, a) !== a) n++; }
  }
  return n;
}
function vocabulary(tid) {
  const P = params(tid);
  /* the store's gift-card items: published items whose facts carry the capability's fact */
  const D = require("./db.js");
  const items = D.all("SELECT id, title, attrs FROM products WHERE tenant_id=? AND lifecycle='published' AND attrs LIKE ?", Number(tid), "%\"" + P.fact + "\"%")
    .filter(p => { try { return !!JSON.parse(p.attrs || "{}")[P.fact]; } catch (e) { return false; } }).map(p => ({ id: p.id, title: p.title }));
  return { items, denominations: P.denominations, min_amount: P.min_amount, max_amount: P.max_amount, validity_days: P.validity_days, occasions: require("./registry.js").list("giftCardOccasions"),
    actions: Object.entries(states.actions(M)).map(([verb, to]) => ({ verb, to, label: states.display(M, to).label })) };
}

/* ---------- buying one: the line term and the order ---------- */
/* { amount, recipient, recipient_email, message, occasion } on a gift-card item's line */
lineterms.register("gift_card", {
  atom: KEY.capability,
  clean: (ctx, v) => {
    const P = params(ctx.tid);
    const facts = typeof ctx.product.attrs === "string" ? JSON.parse(ctx.product.attrs || "{}") : (ctx.product.attrs || {});
    if (!facts[P.fact]) throw fail("This item is not a gift card");
    const x = v && typeof v === "object" ? v : {};
    const amount = Number(x.amount);
    if (!(amount >= Number(P.min_amount) && amount <= Number(P.max_amount))) throw fail(`Choose a value between ${P.min_amount} and ${P.max_amount}`);
    const email = String(x.recipient_email || "").trim();
    if (email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) throw fail("That is not an email address");
    return { amount, recipient: String(x.recipient || "").slice(0, 80), recipient_email: email.slice(0, 200), message: String(x.message || "").slice(0, 500), occasion: String(x.occasion || "") };
  },
  price: (ctx, v) => ({ set: Number(v.amount), label: "Gift card" + (v.recipient ? " for " + v.recipient : "") })
});
lineterms.onOrder((ctx, items) => {
  if (!caps().on(Number(ctx.tid), KEY.capability)) return;
  const P = caps().cap(Number(ctx.tid), KEY.capability);
  for (const it of items) {
    const facts = (() => { try { const r = require("./db.js").get("SELECT attrs FROM products WHERE tenant_id=? AND id=?", Number(ctx.tid), it.product.id); return JSON.parse((r && r.attrs) || "{}"); } catch (e) { return {}; } })();
    if (!facts[P.fact]) continue;
    const t = (it.terms || {}).gift_card || {};
    for (let k = 0; k < (Number(it.qty) || 1); k++)
      issue(ctx.tid, { amount: t.amount != null ? t.amount : it.unit, source: "bought", buyer: ctx.owner, order_ref: ctx.orderNum, recipient: t.recipient, recipient_email: t.recipient_email, message: t.message, occasion: t.occasion }, ctx.owner);
  }
});

/* ---------- the incentive kernel asks this domain to issue a card ---------- */
/* A grant of kind "gift_card" is issued by the gift-card engine, not by the incentive
   kernel: the kernel names the kind and asks for the writer that owns it. The card's
   value, its code and its holder all belong here; the kernel never learns what a card is. */
function issueAsGrant(tenantId, owner, grant, src) {
  const c = issue(tenantId, { amount: Number(grant.qty) || 0, unit: grant.unit, source: "granted", buyer: owner || "" }, "goip");
  return { kind: "gift_card", entity: "gift_card", last4: c.last4, amount: c.amount };
}

/* ---------- the offer that issues a card when it is bought ---------- */
/* An offer of type gift_card_issue grants a card worth the offer's value, once the cart has
   reached the offer's minimum. The math is here, with the rest of the gift-card domain: the
   incentive kernel registers this handler into the one offers engine, and never learns what
   a gift card is. */
const rowOf = o => (o && o._row) || {};
const unitOf = o => String(rowOf(o).economic_unit || o.currency || require("./defaults.js").currency(o.tenant_id)).toUpperCase();
function grantOf(o) {
  const r = o.rules || {};
  return { benefit: "gift_card", unit: unitOf(o), qty: Number(r.qty != null ? r.qty : o.value) || 0, tier: r.tier || "", days: Number(r.days || 0) || 0, scope: o.scope || {}, ref: r.ref || o.code || "" };
}
function offerHandler(o, its, amt) {
  if (amt < (Number(o.min_amount) || 0)) return {};
  return { grant: Object.assign(grantOf(o), { kind: "gift_card" }) };
}

/* ---------- buying one: the line term and the order ---------- */
function port() {
  const D = require("./db.js");
  if (!D.get("SELECT name FROM sqlite_master WHERE type='table' AND name='gift_vouchers'")) return 0;
  let n = 0;
  const live = states.initial(M);
  for (const v of D.all("SELECT * FROM gift_vouchers")) {
    try {
      tx(() => {
        const unit = W().unitOf(v.currency || require("./defaults.js").currency(v.tenant_id));
        const redeemed = !!v.redeemed_by;
        const uid = K().createNode(KEY.kind, { namespace: tenantNs(v.tenant_id), identifiers: { [KEY.codeScheme]: indexOf(v.tenant_id, v.code) }, attributes: {
          tenant: Number(v.tenant_id), amount: W().toMinor(Number(v.amount).toFixed(unit.decimals), unit.decimals), unit: unit.code,
          status: redeemed ? states.actionTarget(M, "redeem") : live, source: "issued", occasion: "", order_ref: "",
          expires_at: v.expires_at && v.expires_at !== "null" ? new Date(String(v.expires_at).replace(" ", "T")).toISOString() : "", last4: normal(v.code).slice(-4), code: normal(v.code),
          recipient: v.recipient || "", recipient_email: v.recipient_email || "", message: v.message || "", buyer: v.buyer || "", redeemed_by: v.redeemed_by || "" } }, "port");
        if (v.buyer) K().place(KEY.held, uid, W().holderOf(v.tenant_id, v.buyer, true, "port"), { namespace: tenantNs(v.tenant_id) }, "port");
        K().append(EVT.ported, { namespace: tenantNs(v.tenant_id), subject: uid, actor: "port", payload: { from: v.id } });
      });
      n++;
    } catch (e) { console.error("gift card port:", v.id, e.message); }
  }
  D.run("DROP TABLE gift_vouchers");
  return n;
}
/* what the store's settings and the first gift-voucher switch carried move into the gift_cards
   capability, once: a store's own gift amounts become its denominations and maximum */
function portSettings() {
  const D = require("./db.js");
  for (const r of D.all("SELECT * FROM capability_values WHERE capability='gift_vouchers'")) {
    if (!D.get("SELECT id FROM capability_values WHERE tenant_id=? AND capability=?", r.tenant_id, KEY.capability)) D.run("UPDATE capability_values SET capability=? WHERE id=?", KEY.capability, r.id);
    else D.run("DELETE FROM capability_values WHERE id=?", r.id);
  }
  for (const r of D.all("SELECT tenant_id, value FROM settings WHERE key='commerce'")) {
    let v; try { v = JSON.parse(r.value); } catch (e) { continue; }
    if (!v || (v.giftAmounts == null && v.giftMax == null)) continue;
    const row = D.get("SELECT * FROM capability_values WHERE tenant_id=? AND capability=?", r.tenant_id, KEY.capability);
    const p = Object.assign({}, row && row.params ? JSON.parse(row.params) : {});
    if (p.denominations == null && Array.isArray(v.giftAmounts)) p.denominations = v.giftAmounts;
    if (p.max_amount == null && v.giftMax != null) p.max_amount = Number(v.giftMax);
    if (row) D.run("UPDATE capability_values SET params=? WHERE id=?", JSON.stringify(p), row.id);
    else D.run("INSERT INTO capability_values(tenant_id,capability,enabled,params) VALUES(?,?,?,?)", r.tenant_id, KEY.capability, caps().on(r.tenant_id, KEY.capability) ? 1 : 0, JSON.stringify(p));
    delete v.giftAmounts; delete v.giftMax;
    D.run("UPDATE settings SET value=? WHERE tenant_id=? AND key='commerce'", JSON.stringify(v), r.tenant_id);
  }
}
function seed() { declare(); port(); portSettings(); }
/* the incentive kernel asks for this domain's writer when a gift card is granted, and this
   domain's offer type registers its math into the one offers engine */
function register() {
  const g = require("./grants.js");
  g.registerGrant("gift_card", issueAsGrant);
  g.registerHandler("gift_card_issue", offerHandler);
  return 1;
}

module.exports = { seed, register, issue, issueAsGrant, offerHandler, redeem, check, voidCard, list, mine, sweepAll, vocabulary };

/* this domain registers itself the moment it is loaded */
register();
