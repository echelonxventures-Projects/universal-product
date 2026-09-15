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
function buildCtx(spec, o) {
  return Object.assign({ cfg: o.config || {}, amount: Number(o.amount) || 0, amountCents: Math.round((Number(o.amount) || 0) * 100), money: (Number(o.amount) || 0).toFixed ? (Number(o.amount) || 0).toFixed(2) : o.amount, currency: o.currency, idempotency: o.idempotency || "", to: o.to, subject: o.subject, text: o.text, qty: o.qty, ts: Date.now(), iso: new Date().toISOString(), payload: o.payload || {} }, o.extra || {});
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
  let payload;
  if (spec.form) payload = new URLSearchParams(flatten(body)).toString();
  else payload = JSON.stringify(body);
  const r = await http(render(spec.url, ctx), { method: spec.method || "POST", headers, body: payload });
  const err = r.ok ? null : getPath(r.json, spec.errorPath || "error.message");
  const status = getPath(r.json, spec.id ? spec.statusPath || "status" : "status");
  const mapped = spec.statusMap ? (spec.statusMap[String(status)] || (r.ok ? "captured" : "failed")) : (r.ok ? (spec.okStatus || "captured") : "failed");
  return { ok: r.ok, id: getPath(r.json, spec.idPath || "id"), status: mapped, raw: r.json, error: err || (r.ok ? null : ("HTTP " + r.status)) };
}
function renderAll(obj, ctx) { if (!obj) return {}; const o = {}; for (const k of Object.keys(obj)) o[render(k, ctx)] = render(obj[k], ctx); return o; }
function flatten(o) { const out = {}; (function walk(p, v) { if (v && typeof v === "object" && !Array.isArray(v)) for (const k of Object.keys(v)) walk(p ? p + "[" + k + "]" : k, v[k]); else out[p] = v == null ? "" : String(v); })("", o); return out; }
function mapVals(o) { const out = {}; for (const k of Object.keys(o)) out[k] = o[k] == null ? "" : String(o[k]); return out; }

/* validate a draft spec enough to save it (cheap, no execution) */
function validate(spec) { if (!spec || typeof spec !== "object") return "spec required"; if (!spec.url) return "spec.url required"; const bad = JSON.stringify(spec).match(/\{\{\s*\}\}/); if (bad) return "empty template token"; return null; }

module.exports = { execute, render, getPath, validate, buildCtx, flatten };
