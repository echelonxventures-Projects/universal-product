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
function hasCreds(specDef, cfg) {
  const refs = JSON.stringify(specDef).match(/\{\{cfg\.[a-zA-Z0-9_]+/g) || [];
  const keys = [...new Set(refs.map(r => r.replace("{{cfg.", "")))];
  if (!keys.length) return true;
  return keys.every(k => cfg && cfg[k] && !String(cfg[k]).startsWith("••••"));
}

async function run(kind, o) {
  if (offline() || o.offline) return { live: false };
  const s = specFor(o.provider, kind, o.spec);
  if (!s) return { live: false, reason: "no spec" };
  if (!hasCreds(s, o.config)) return { live: false, reason: "incomplete credentials" };
  try { const r = await spec.execute(s, o, http); return Object.assign({ live: true, ok: !!r.ok, id: r.id, status: r.status }, r.error ? { error: r.error } : {}); }
  catch (e) { return { live: true, ok: false, error: e.message }; }
}
const pay = (o) => run("payment", o);
const notify = (o) => run("notification", Object.assign({ to: o.to, subject: o.subject, text: o.text }, o));
const marketing = (o) => run("marketing", o);
async function ping(o) {
  if (offline()) return { live: false, ok: false, error: "offline" };
  const s = specFor(o.provider, o.kind || "payment", o.spec);
  if (!s) return { live: false, ok: false, error: "no spec" };
  if (!hasCreds(s, o.config)) return { live: false, ok: false, error: "incomplete credentials" };
  if (s.ping) { try { const r = await spec.execute(s.ping, o, http); return { live: true, ok: !!r.ok, error: r.error }; } catch (e) { return { live: true, ok: false, error: e.message }; } }
  return { live: true, ok: true, note: "spec + credentials present (no read-only ping defined)" };
}

module.exports = { pay, notify, marketing, ping, __setTransport, specFor, _crypto: crypto };
