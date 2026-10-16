/* LUXORA Platform — outbound integration dispatcher (zero per-provider code).
   A provider's protocol now lives in DATA (provider_defs.spec, or a custom provider manifest's
   `spec`) and is executed by lib/spec.js. connect.js only: checks offline/credentials, loads the
   spec, renders+executes it, maps the result. Nothing here hard-codes Stripe/Meta/Google/Twilio —
   adding a provider or changing an endpoint is a data edit. When offline / no credentials / no spec,
   callers fall back to their simulated path, so the app runs and tests never hit the network. */
"use strict";

const crypto = require("crypto");
let _db = null; const db = () => _db || (_db = require("./db.js"));
const spec = require("./spec.js");

let fetchFn = (...a) => fetch(...a);
function __setTransport(f) { const prev = fetchFn; fetchFn = f || ((...a) => fetch(...a)); return prev; }
function http(url, opts) {
  const ac = new AbortController(); const to = setTimeout(() => ac.abort(), opts && opts.timeoutMs || 12000);
  const o = Object.assign({ signal: ac.signal }, opts); delete o.timeoutMs;
  return fetchFn(url, o).then(async r => { const text = await r.text().catch(() => ""); let json = null; try { json = JSON.parse(text); } catch (e) { } return { ok: r.ok, status: r.status, text, json }; }).finally(() => clearTimeout(to));
}
function offline() { return process.env.LX_OFFLINE === "1"; }
/* spec from provider_defs (kind) or, if the caller passed one inline (custom provider) via opts.spec */
function specFor(id, kind, inlineSpec) {
  if (inlineSpec) return inlineSpec;
  const D = db();
  const r = D.get("SELECT spec FROM provider_defs WHERE id=? AND kind=?", id, kind);
  if (r && r.spec) { try { const j = JSON.parse(r.spec); if (j && j.url) return j; } catch (e) { } }
  return null;
}
/* every {{cfg.x}} the spec uses must be on file, except those it declares optional (a
   PayPal environment prefix is blank in live) */
function hasCreds(specDef, cfg, optional) {
  const refs = JSON.stringify(specDef).match(/\{\{cfg\.[a-zA-Z0-9_]+/g) || [];
  const opt = new Set(optional || specDef.optionalCfg || []);
  const keys = [...new Set(refs.map(r => r.replace("{{cfg.", "")))].filter(k => !opt.has(k));
  if (!keys.length) return true;
  return keys.every(k => cfg && cfg[k] && !String(cfg[k]).startsWith("••••"));
}

async function run(kind, o) {
  if (offline() || o.offline) return { live: false };
  const s = specFor(o.provider, kind, o.spec);
  if (!s) return { live: false, reason: "no spec" };
  if (!hasCreds(Object.assign({}, s, { webhook: undefined, lookup: undefined, capture: undefined, refund: undefined }), o.config, s.optionalCfg)) return { live: false, reason: "incomplete credentials" };
  try { const r = await spec.execute(s, o, http); return Object.assign({ live: true, ok: !!r.ok, id: r.id, status: r.status }, r.redirect ? { redirect: r.redirect } : {}, r.error ? { error: r.error } : {}); }
  catch (e) { return { live: true, ok: false, error: e.message }; }
}
const pay = (o) => run("payment", o);
const notify = (o) => run("notification", Object.assign({ to: o.to, subject: o.subject, text: o.text }, o));
const marketing = (o) => run("marketing", o);
/* a refund is the payment spec's own `refund` block, run against the provider's payment id */
async function refund(o) {
  if (offline() || o.offline) return { live: false };
  const s = specFor(o.provider, "payment", o.spec);
  if (!s || !s.refund) return { live: false, reason: "no refund spec" };
  if (!hasCreds(s.refund, o.config, s.optionalCfg)) return { live: false, reason: "incomplete credentials" };
  try { const r = await spec.execute(s.refund, o, http); return Object.assign({ live: true, ok: !!r.ok, id: r.id, status: r.status }, r.error ? { error: r.error } : {}); }
  catch (e) { return { live: true, ok: false, error: e.message }; }
}
/* where a payment stands now, asked of the provider: the payment spec's `lookup` block
   run against the reference checkout stored. When the provider reports it approved but not
   yet captured (an order-then-capture gateway) and the spec has a `capture` block, the
   capture runs — money is only ever "captured" on the provider's own word. */
async function lookup(o) {
  if (offline() || o.offline) return { live: false, reason: "offline" };
  const s = specFor(o.provider, "payment", o.spec);
  if (!s || !s.lookup) return { live: false, reason: "no lookup spec" };
  if (!hasCreds(s.lookup, o.config, s.optionalCfg)) return { live: false, reason: "incomplete credentials" };
  const call = async sub => { const r = await spec.execute(sub, Object.assign({}, o, { extra: Object.assign({ ref: o.ref }, o.extra || {}) }), http); return { live: true, ok: !!r.ok, status: r.status, paymentId: r.paymentId || null, amount: r.amount == null ? null : r.amount, error: r.error }; };
  try {
    let r = await call(s.lookup);
    if (r.ok && r.status === "approved" && s.capture) r = Object.assign(await call(s.capture), { captureRan: true });
    return Object.assign(r, { amountUnit: s.lookup.amountUnit || "minor" });
  } catch (e) { return { live: true, ok: false, error: e.message }; }
}
async function ping(o) {
  if (offline()) return { live: false, ok: false, error: "offline" };
  const s = specFor(o.provider, o.kind || "payment", o.spec);
  if (!s) return { live: false, ok: false, error: "no spec" };
  if (!hasCreds(s, o.config)) return { live: false, ok: false, error: "incomplete credentials" };
  if (s.ping) { try { const r = await spec.execute(s.ping, o, http); return { live: true, ok: !!r.ok, error: r.error }; } catch (e) { return { live: true, ok: false, error: e.message }; } }
  return { live: true, ok: true, note: "spec + credentials present (no read-only ping defined)" };
}

module.exports = { pay, refund, lookup, notify, marketing, ping, __setTransport, specFor, request: (url, opts) => http(url, opts), offline, _crypto: crypto };
