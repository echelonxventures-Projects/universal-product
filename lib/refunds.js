/* LUXORA Platform — refunds, full and partial, exactly (PR-016, PR-029).

   A refund is its own record (`refunds`): an exact amount of the payment's currency, at the
   payment's scale, with its source (console or provider), its idempotency key and, once the
   provider names it, the provider's refund id. Its life is the `refund` machine
   (lib/seed/states.json), asked by meaning:
     reserved   pending, unknown or succeeded — counted against what can still be refunded
     open       pending or unknown — not finished
     success    the money went back
     failure    it did not; nothing is reserved
   payments.refunded_minor is the sum of the reserved refunds. It is claimed by ONE conditional
   UPDATE (amount_minor − refunded_minor must cover the refund), so two requests racing for the
   last of a payment can never both succeed, and a refund can never exceed what was captured.

   A provider call that fails releases the reservation; one whose outcome is not known (it threw
   or timed out) keeps it as `unknown` — the money may have moved, so it is neither reported as
   refunded nor released, and an operator or the provider's own event settles it. A simulated
   payment is refunded without a call; a live one only through its provider (or recorded as
   refunded elsewhere with manual: true). Nothing here reports a simulated provider refund as a
   real one.

   When the reserved refunds reach the whole amount and all have succeeded the payment moves to
   its `reversed` state and the full-refund effects run (offer redemptions reversed,
   order.refunded). A partial refund leaves the payment refundable for the rest. Tax and offer
   effects of a PARTIAL refund are not apportioned here — that is the owner's decision
   (PRODUCTION_READINESS.md PR-029); the refund records its amount only. */
"use strict";
const M = require("./money.js");
const MS = require("./money-store.js");
const states = require("./states.js");
let _db = null;
const db = () => _db || (_db = require("./db.js"));
const fail = (m, status, code) => Object.assign(new Error(m), { status: status || 400, code: code || "refund_invalid" });
const inList = (machine, tag) => { const xs = states.tagged(machine, tag); return { sql: "(" + (xs.length ? xs.map(() => "?").join(",") : "NULL") + ")", args: xs }; };
const is = (machine, s, tag) => states.has(machine, s) && states.is(machine, s, tag);
const first = tag => states.first("refund", tag);

/* one write transaction on either engine, nesting into a caller's (lib/kernel.js) */
const tx = fn => require("./kernel.js").internal.tx(() => fn(db()));
const view = r => r && ({ ...r, amount: M.toNumber(M.ofMinor(r.amount_minor, r.currency, r.money_scale)), money: M.toJSON(M.ofMinor(r.amount_minor, r.currency, r.money_scale)) });
const ofPayment = paymentId => db().all("SELECT * FROM refunds WHERE payment_id=? ORDER BY id", Number(paymentId)).map(view);
function summary(p) {
  const amount = MS.amountOf("payments", p, "amount");
  const refunded = M.ofMinor(p.refunded_minor || 0, amount.currency, amount.scale);
  return { amount: M.toJSON(amount), refunded: M.toJSON(refunded), refundable: M.toJSON(M.sub(amount, refunded)) };
}

/* reserve `amount` of payment p for a new refund row, atomically; the existing row when the
   same key was used for the same request */
function reserve(p, amount, o) {
  return tx(D => {
    const prior = D.get("SELECT * FROM refunds WHERE tenant_id=? AND idem_key=?", p.tenant_id, o.idem);
    if (prior && (Number(prior.payment_id) !== Number(p.id) || Number(prior.amount_minor) !== M.minorOf(amount))) throw fail("This idempotency key was used for a different refund", 422, "idempotency_conflict");
    /* the same request again: its outcome, unless it definitely failed — then it is tried again */
    if (prior && !is("refund", prior.status, "failure")) return { row: prior, replay: true };
    const rf = inList("payment", "refundable");
    const claim = D.run("UPDATE payments SET refunded_minor = refunded_minor + ? WHERE id=? AND tenant_id=? AND money_state IS NULL AND status IN " + rf.sql + " AND amount_minor - refunded_minor >= ?",
      M.minorOf(amount), p.id, p.tenant_id, ...rf.args, M.minorOf(amount));
    if (!claim.changes) {
      const now = D.get("SELECT * FROM payments WHERE id=?", p.id);
      if (!is("payment", now.status, "refundable")) throw fail("Only captured payments can be refunded", 409, "not_refundable");
      throw fail("A refund of " + M.toString(amount) + " " + amount.currency + " is more than the " + summary(now).refundable.amount + " " + amount.currency + " still refundable", 409, "exceeds_refundable");
    }
    if (prior) {
      D.run("UPDATE refunds SET status=?, error=NULL, attempts=attempts+1, settled_at=NULL WHERE id=?", o.status || first("open"), prior.id);
      return { row: D.get("SELECT * FROM refunds WHERE id=?", prior.id), replay: false };
    }
    /* the refund records the money policy version in force (lib/money-policy.js) */
    const id = Number(D.run("INSERT INTO refunds(tenant_id,payment_id,amount_minor,currency,money_scale,status,source,reason,idem_key,provider_refund_id,actor,money_policy) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
      p.tenant_id, p.id, M.minorOf(amount), amount.currency, amount.scale, o.status || first("open"), o.source || "console", String(o.reason || ""), o.idem, o.providerRefundId || null, String(o.actor || ""), require("./money-policy.js").ref()).lastInsertRowid);
    return { row: D.get("SELECT * FROM refunds WHERE id=?", id), replay: false };
  });
}
/* a refund finished: succeeded keeps its reservation, failed gives it back */
function finish(r, outcome, extra) {
  return tx(D => {
    const cur = D.get("SELECT * FROM refunds WHERE id=?", r.id);
    if (!is("refund", cur.status, "open")) return cur;
    /* a provider that answers with the id of a refund already recorded did not make a new one
       (it replayed the earlier): this refund is not known to have happened — kept, reserved, for review */
    const pid = extra && extra.providerRefundId;
    const clash = pid ? D.get("SELECT id FROM refunds WHERE payment_id=? AND provider_refund_id=? AND id<>?", cur.payment_id, String(pid), cur.id) : null;
    if (clash) {
      D.run("UPDATE refunds SET status=?, error=? WHERE id=?", first("unresolved"), "the provider answered with refund " + pid + ", already recorded as refund #" + clash.id, cur.id);
      return D.get("SELECT * FROM refunds WHERE id=?", cur.id);
    }
    const to = first(outcome);
    D.run("UPDATE refunds SET status=?, provider_refund_id=COALESCE(?, provider_refund_id), error=?, settled_at=datetime('now') WHERE id=?", to, (extra && extra.providerRefundId) || null, (extra && extra.error) || null, cur.id);
    if (outcome === "failure") D.run("UPDATE payments SET refunded_minor = refunded_minor - ? WHERE id=?", cur.amount_minor, cur.payment_id);
    return D.get("SELECT * FROM refunds WHERE id=?", cur.id);
  });
}
/* when every reserved minor unit has gone back, the payment is reversed (once) */
function settleIfFull(p, onFull) {
  const D = db(), fresh = D.get("SELECT * FROM payments WHERE id=?", p.id);
  if (Number(fresh.refunded_minor) !== Number(fresh.amount_minor)) return { full: false, payment: fresh };
  const open = inList("refund", "open");
  if (D.get("SELECT COUNT(*) c FROM refunds WHERE payment_id=? AND status IN " + open.sql, p.id, ...open.args).c) return { full: false, payment: fresh, awaiting: true };
  const rf = inList("payment", "refundable");
  const claim = D.run("UPDATE payments SET status=? WHERE id=? AND status IN " + rf.sql, states.first("payment", "reversed"), p.id, ...rf.args);
  if (claim.changes && onFull) onFull(fresh);
  return { full: !!claim.changes, payment: D.get("SELECT * FROM payments WHERE id=?", p.id) };
}

/* refund a payment from the console. o: { amount (a decimal in the payment's currency; absent =
   all that is still refundable), currency (optional, must be the payment's), idem, reason,
   actor, manual, refundAt (async provider call), onFull } */
async function refund(p, o) {
  o = o || {};
  if (MS.quarantined(p)) throw fail("This payment's amounts are under money review; resolve them before refunding", 409, "money_review");
  if (!is("payment", p.status, "refundable")) throw fail("Only captured payments can be refunded", 409, "not_refundable");
  const total = MS.amountOf("payments", p, "amount");
  if (o.currency && String(o.currency).toUpperCase() !== total.currency) throw fail("This payment is in " + total.currency + ", not " + o.currency, 400, "currency_mismatch");
  let amount;
  try { amount = o.amount == null || o.amount === "" ? MS.refundable(p) : M.of(o.amount, total.currency); }
  catch (e) { throw fail(e.message, 400, e.code); }
  if (M.cmp(amount, M.zero(total.currency)) <= 0) throw fail("A refund is a positive amount", 400, "amount_invalid");
  /* a full refund can only happen once (the reservation covers the whole amount), so it may come
     without a key; a part of a payment needs one, or a retried request would refund it twice */
  const whole = M.eq(amount, MS.refundable(p));
  const idem = String(o.idem || (whole ? "full:" + p.id + ":" + require("crypto").randomBytes(6).toString("hex") : "")).slice(0, 120);
  if (!idem) throw fail("A partial refund needs an idempotency key (Idempotency-Key)", 400, "idempotency_required");
  if (p.live && !o.manual && !whole && !o.partialAtProvider) throw fail("This payment's provider connector refunds whole payments only (its refund request sends no amount); refund part of it at the provider and record it with manual: true", 409, "partial_unsupported");
  const { row, replay } = reserve(p, amount, { idem, reason: o.reason, actor: o.actor, source: o.manual ? "manual" : "console" });
  if (replay) return { replay: true, refund: view(row), ...summary(db().get("SELECT * FROM payments WHERE id=?", p.id)) };
  let done = row, gateway = null;
  if (p.live && !o.manual) {
    let r;
    /* the provider's key names this refund and this attempt: a retry after an unknown outcome
       reuses it (the provider dedupes), one after a definite failure is a new attempt */
    try { r = await o.refundAt({ amount: M.toString(amount), currency: amount.currency, idempotency: "refund-" + p.id + "-" + row.id + (row.attempts > 1 ? "-" + row.attempts : "") }); }
    catch (e) { r = { live: true, unknown: true, error: e.message }; }
    if (!r || r.unknown) { done = tx(D => { D.run("UPDATE refunds SET status=?, error=? WHERE id=?", first("unresolved"), String((r && r.error) || "no answer"), row.id); return D.get("SELECT * FROM refunds WHERE id=?", row.id); }); return { pending: true, unknown: true, refund: view(done), ...summary(db().get("SELECT * FROM payments WHERE id=?", p.id)) }; }
    if (!r.live) { finish(row, "failure", { error: r.reason || "gateway offline" }); throw fail("Refund not sent (" + (r.reason || "gateway offline") + ")", 503, "gateway_offline"); }
    if (!r.ok || is("payment", r.status, "failure")) { finish(row, "failure", { error: r.error || r.status }); throw fail("The gateway refused the refund: " + (r.error || r.status), 502, "gateway_refused"); }
    gateway = { id: r.id, status: r.status };
    /* accepted but still processing at the provider: reserved and open until its event */
    if (!is("payment", r.status, "reversed")) {
      done = tx(D => { D.run("UPDATE refunds SET provider_refund_id=COALESCE(?, provider_refund_id) WHERE id=?", r.id || null, row.id); return D.get("SELECT * FROM refunds WHERE id=?", row.id); });
      return { pending: true, refund: view(done), gateway_refund: gateway, ...summary(db().get("SELECT * FROM payments WHERE id=?", p.id)) };
    }
    done = finish(row, "success", { providerRefundId: r.id });
    if (!is("refund", done.status, "success")) return { pending: true, unknown: true, refund: view(done), gateway_refund: gateway, ...summary(db().get("SELECT * FROM payments WHERE id=?", p.id)) };
  } else done = finish(row, "success");
  const s = settleIfFull(p, o.onFull);
  return { refund: view(done), full: s.full, gateway_refund: gateway, ...summary(s.payment) };
}

/* a refund the provider reports. Its rule says what the amount means: `refund` (this one
   refund, named by its id) or `cumulative` (all refunded so far on the payment). Applied once:
   a refund id already recorded, or a cumulative total already covered, changes nothing. */
function applyProvider(p, e, o) {
  o = o || {};
  if (MS.quarantined(p)) return { ok: true, applied: false, review: true, reason: "payment under money review" };
  const total = MS.amountOf("payments", p, "amount");
  const D = db();
  if (e.amount == null || e.amount === "") return { ok: true, applied: false, review: true, reason: "the event states no amount" };
  let got;
  try { got = M.ofMinor(o.minor(e, total.currency), total.currency, total.scale); } catch (x) { return { ok: true, applied: false, review: true, reason: "unreadable amount" }; }
  const reserved = inList("refund", "reserved"), open = inList("refund", "open");
  let row = null;
  if ((e.amountMeaning || "cumulative") === "cumulative") {
    const settled = M.ofMinor(D.get("SELECT COALESCE(SUM(amount_minor),0) s FROM refunds WHERE payment_id=? AND status IN " + inList("refund", "success").sql, p.id, ...inList("refund", "success").args).s, total.currency, total.scale);
    const all = M.ofMinor(p.refunded_minor || 0, total.currency, total.scale);
    /* the provider has refunded at least what we reserved: our open refunds are done */
    if (M.cmp(got, all) >= 0) for (const r of D.all("SELECT * FROM refunds WHERE payment_id=? AND status IN " + open.sql, p.id, ...open.args)) finish(r, "success");
    const extra = M.sub(got, M.max(all, settled));
    if (M.cmp(extra, M.zero(total.currency)) > 0) row = reserve(D.get("SELECT * FROM payments WHERE id=?", p.id), extra, { idem: "provider:" + (e.id || e.type) + ":" + M.minorOf(got), source: "provider", status: first("success"), reason: e.type }).row;
  } else {
    if (!e.refundId) return { ok: true, applied: false, review: true, reason: "a per-refund event without the provider's refund id" };
    const known = D.get("SELECT * FROM refunds WHERE payment_id=? AND provider_refund_id=?", p.id, String(e.refundId));
    if (known) { if (is("refund", known.status, "open")) finish(known, "success"); }
    else row = reserve(p, got, { idem: "provider:" + e.refundId, source: "provider", status: first("success"), providerRefundId: String(e.refundId), reason: e.type }).row;
  }
  const s = settleIfFull(p, o.onFull);
  return { ok: true, applied: true, refund: row ? view(row) : null, full: s.full, ...summary(s.payment) };
}

/* an operator settles an open refund (pending, or unknown after a provider call gave no answer)
   from the provider's own record: succeeded keeps the reservation, failed gives it back */
function resolve(r, outcome, o) {
  o = o || {};
  /* the outcome is a state of the refund machine that means success or failure */
  const tag = is("refund", outcome, "success") ? "success" : is("refund", outcome, "failure") ? "failure" : null;
  if (!tag) throw fail("The outcome is the refund state that means success (" + first("success") + ") or failure (" + first("failure") + ")", 400);
  if (!is("refund", r.status, "open")) throw fail("This refund is already " + r.status, 409, "refund_closed");
  if (!o.by) throw fail("A resolution names who decided it", 400);
  const done = finish(r, tag, { providerRefundId: o.providerRefundId || null, error: tag === "failure" ? "resolved as failed by " + o.by + (o.note ? ": " + o.note : "") : null });
  if (!is("refund", done.status, tag)) throw fail("Not resolved: " + (done.error || done.status), 409);
  const p = db().get("SELECT * FROM payments WHERE id=?", r.payment_id);
  const s = tag === "success" ? settleIfFull(p) : { full: false, payment: p };
  return { refund: view(done), full: s.full, ...summary(s.payment) };
}

module.exports = { refund, applyProvider, resolve, ofPayment, summary };
