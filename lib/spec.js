/* LUXORA Platform — declarative integration spec engine.
   A "how to call this API" description is DATA (stored on provider_defs.spec / custom provider
   manifest), not JavaScript. This module renders a spec against a context and executes it with the
   injectable fetch — so adding Stripe/Meta/Google/TikTok/a custom gateway is "fill in the blanks",
   never a code change. A spec supports: optional token/auth exchange, method, url template, auth
   (basic|bearer|apikey header), form|json body templates, status mapping, and success/error paths. */
"use strict";

/* path "json.id" or "0.name" → value */
function getPath(obj, path) { if (!path) return obj; return String(path).split(/[.\[\]]+/).filter(Boolean).reduce((o, k) => (o == null ? o : o[k]), obj); }

/* {{...}} template render over ctx; a whole-string token returns the raw value (number/bool),
   otherwise string-interpolates. Helpers: __cents, __money (2dp), __now, __iso. */
function render(v, ctx) {
  if (v && typeof v === "object") { if (Array.isArray(v)) return v.map(x => render(x, ctx)); const o = {}; for (const k of Object.keys(v)) o[k] = render(v[k], ctx); return o; }
  if (typeof v !== "string") return v;
  const whole = /^\{\{([^}]+)\}\}$/.exec(v.trim());
  if (whole) return evalExpr(whole[1], ctx);
  return v.replace(/\{\{([^}]+)\}\}/g, (_, e) => { const r = evalExpr(e, ctx); return r == null ? "" : String(r); });
}
function evalExpr(expr, ctx) {
  expr = expr.trim();
  const m = /^([a-zA-Z0-9_.]+)(\s*([*+\-])\s*(\d+))?$/.exec(expr);
  let val = getPath(ctx, m ? m[1] : expr);
  if (m && m[3]) { const n = Number(m[4]); if (m[3] === "*") val = Number(val) * n; else if (m[3] === "+") val = Number(val) + n; else if (m[3] === "-") val = Number(val) - n; }
  return val;
}
/* ISO 4217 currencies with no minor unit: a gateway's "smallest unit" for these IS the
   major unit, so ¥1,500 is 1500, not 150000 */
const ZERO_DECIMAL = new Set(["BIF", "CLP", "DJF", "GNF", "JPY", "KMF", "KRW", "MGA", "PYG", "RWF", "UGX", "VND", "VUV", "XAF", "XOF", "XPF"]);
function minorUnits(amount, currency) { const n = Number(amount) || 0; return ZERO_DECIMAL.has(String(currency || "").toUpperCase()) ? Math.round(n) : Math.round(n * 100); }
function buildCtx(spec, o) {
  return Object.assign({ cfg: o.config || {}, amount: Number(o.amount) || 0, amountCents: minorUnits(o.amount, o.currency), currencyLower: String(o.currency || "").toLowerCase(), paymentId: o.paymentId || "", money: (Number(o.amount) || 0).toFixed ? (Number(o.amount) || 0).toFixed(2) : o.amount, currency: o.currency, idempotency: o.idempotency || "", to: o.to, subject: o.subject, text: o.text, qty: o.qty, ts: Date.now(), iso: new Date().toISOString(), payload: o.payload || {} }, o.extra || {});
}
function authHeader(auth, ctx) {
  if (!auth || !auth.type) return null;
  if (auth.type === "basic") { const u = render(auth.user, ctx), p = render(auth.pass, ctx); return { Authorization: "Basic " + Buffer.from(u + ":" + p).toString("base64") }; }
  if (auth.type === "bearer") return { Authorization: "Bearer " + render(auth.token, ctx) };
  if (auth.type === "apikey") return { [render(auth.header, ctx) || "Authorization"]: render(auth.value, ctx) };
  return null;
}
async function execute(spec, o, http) {
  const ctx = buildCtx(spec, o);
  /* optional two-step token exchange (e.g. PayPal OAuth) */
  if (spec.token) {
    const tr = await http(render(spec.token.url, ctx), { method: spec.token.method || "POST", headers: Object.assign({ "content-type": spec.token.form ? "application/x-www-form-urlencoded" : "application/json" }, authHeader(spec.token.auth, ctx) || {}), body: spec.token.body ? (spec.token.form ? new URLSearchParams(mapVals(render(spec.token.body, ctx))).toString() : JSON.stringify(render(spec.token.body, ctx))) : undefined });
    if (!tr.ok) throw new Error(getPath(tr.json, spec.token.errorPath || "error.message") || ("token " + tr.status));
    ctx.token = getPath(tr.json, spec.token.path || "access_token");
  }
  const body = render(spec.body || {}, ctx);
  const headers = Object.assign({ "content-type": spec.form ? "application/x-www-form-urlencoded" : "application/json" }, renderAll(spec.headers, ctx));
  const ah = authHeader(Object.assign({}, spec.auth, spec.auth && spec.auth.token && ctx.token ? { token: ctx.token } : {}), ctx);
  Object.assign(headers, ah || {});
  if (spec.idempotencyHeader) headers[spec.idempotencyHeader] = ctx.idempotency || String(Date.now());
  const method = String(spec.method || "POST").toUpperCase();
  let payload;
  if (method === "GET" || method === "HEAD") { payload = undefined; delete headers["content-type"]; }
  else if (spec.form) payload = new URLSearchParams(flatten(body)).toString();
  else payload = JSON.stringify(body);
  const r = await http(render(spec.url, ctx), { method, headers, body: payload });
  const err = r.ok ? null : getPath(r.json, spec.errorPath || "error.message");
  const status = getPath(r.json, spec.statusPath || "status");
  /* a status the map does not name is NOT money received: an accepted request whose state
     is unknown (a payment awaiting the customer's confirmation) stays pending until the
     provider's webhook says otherwise */
  let mapped = spec.statusMap ? (spec.statusMap[String(status)] || (r.ok ? "pending" : "failed")) : (r.ok ? (spec.okStatus || "captured") : "failed");
  /* a second field that also means "this will never be paid" (an expired session) */
  if (r.ok && spec.failWhen && (spec.failWhen.values || []).map(String).includes(String(getPath(r.json, spec.failWhen.path)))) mapped = "failed";
  const out = { ok: r.ok, id: getPath(r.json, spec.idPath || "id"), status: mapped, raw: r.json, error: err || (r.ok ? null : ("HTTP " + r.status)) };
  if (spec.paymentIdPath) out.paymentId = getPath(r.json, spec.paymentIdPath) || null;
  if (spec.amountPath) out.amount = getPath(r.json, spec.amountPath);
  if (spec.redirectPath) out.redirect = getPath(r.json, spec.redirectPath) || null;
  /* the redirect as the element of a list that matches, e.g. links[rel=approve].href */
  else if (spec.redirectFind) { const l = getPath(r.json, spec.redirectFind.path); const hit = Array.isArray(l) ? l.find(x => x && Object.entries(spec.redirectFind.match || {}).every(([k, v]) => String(x[k]) === String(v))) : null; out.redirect = hit ? getPath(hit, spec.redirectFind.field || "href") || null : null; }
  return out;
}
/* A provider's webhook signature, as data on the spec's `webhook.signature`:
     { header, algo: "sha256"|"sha1", encoding: "hex"|"base64", over: "body"|"url+body", prefix }
   an HMAC of the exact bytes received (optionally the notification URL first) with the
   store's signing secret. Returns null when the spec declares no HMAC scheme.
   A spec may instead name a `scheme` this engine knows (SIGNATURE_SCHEMES) — a provider's own
   signed-header format — and the header it arrives in. */
const SIGNATURE_SCHEMES = {
  /* "t=<unix>,v1=<hex>[,v1=…]" over "<t>.<body>", with a replay window */
  timestamped: (secret, rawBody, got) => require("./enterprise.js").verifyInbound(secret, rawBody, got)
};
function verifyHmac(sig, secret, rawBody, headers, url) {
  if (!sig || !sig.header || sig.api) return null;
  if (!secret) return false;
  const got = String((headers || {})[String(sig.header).toLowerCase()] || "");
  if (sig.scheme) return SIGNATURE_SCHEMES[sig.scheme] ? !!SIGNATURE_SCHEMES[sig.scheme](secret, rawBody, got) : false;
  const crypto = require("crypto");
  const data = (sig.over === "url+body" ? String(url || "") : "") + rawBody;
  const want = String(sig.prefix || "") + crypto.createHmac(sig.algo || "sha256", secret).update(data).digest(sig.encoding === "base64" ? "base64" : "hex");
  return got.length === want.length && crypto.timingSafeEqual(Buffer.from(got), Buffer.from(want));
}
/* a signature only the provider can check (it signs with a certificate): the spec's
   `webhook.signature.api` is an ordinary request spec run with the event and its headers
   in context; it verifies when `okPath` reads `okValue` */
async function verifyByApi(sig, o, http) {
  const r = await execute(Object.assign({ statusMap: undefined }, sig.api), o, http);
  return !!(r.ok && String(getPath(r.raw, sig.api.okPath || "verification_status")) === String(sig.api.okValue || "SUCCESS"));
}
function renderAll(obj, ctx) { if (!obj) return {}; const o = {}; for (const k of Object.keys(obj)) o[render(k, ctx)] = render(obj[k], ctx); return o; }
function flatten(o) { const out = {}; (function walk(p, v) { if (v && typeof v === "object" && !Array.isArray(v)) for (const k of Object.keys(v)) walk(p ? p + "[" + k + "]" : k, v[k]); else out[p] = v == null ? "" : String(v); })("", o); return out; }
function mapVals(o) { const out = {}; for (const k of Object.keys(o)) out[k] = o[k] == null ? "" : String(o[k]); return out; }

/* validate a draft spec enough to save it (cheap, no execution) */
function validate(spec) { if (!spec || typeof spec !== "object") return "spec required"; if (!spec.url) return "spec.url required"; const bad = JSON.stringify(spec).match(/\{\{\s*\}\}/); if (bad) return "empty template token"; return null; }

/* a provider's webhook event → { ref, status, paymentId, amount } using the spec's
   declarative `webhook` block; null when the event is not one the spec maps */
function webhookEvent(spec, evt) {
  const w = spec && spec.webhook; if (!w || !evt) return null;
  const type = String(getPath(evt, w.typePath || "type") || "");
  const rule = w.events && w.events[type]; if (!rule) return null;
  const status = rule.status || (rule.statusMap && rule.statusMap[String(getPath(evt, rule.statusPath))]) || null;
  if (!status) return null;
  return { type, status, ref: getPath(evt, rule.refPath || w.refPath), paymentId: getPath(evt, rule.paymentIdPath || w.paymentIdPath) || null,
    amount: (rule.amountPath || w.amountPath) ? getPath(evt, rule.amountPath || w.amountPath) : null, amountUnit: rule.amountUnit || w.amountUnit || "minor" };
}

module.exports = { execute, render, getPath, validate, buildCtx, flatten, webhookEvent, minorUnits, verifyHmac, verifyByApi };
