/* LUXORA Platform - in-memory request metrics (per tenant, per minute, per endpoint) */
"use strict";

const MINUTE = 60000;
const buckets = new Map();      // "minuteTs|tenant" -> {req, err, ms}
const endpoints = new Map();    // "tenant|METHOD path" -> {count, err, ms}
const totals = { req: 0, err: 0, ms: 0 };

function record(tenantId, method, path, status, ms) {
  const minute = Math.floor(Date.now() / MINUTE) * MINUTE;
  const bk = minute + "|" + (tenantId || 0);
  const b = buckets.get(bk) || { req: 0, err: 0, ms: 0 };
  b.req++; b.ms += ms; if (status >= 400) b.err++;
  buckets.set(bk, b);
  const ek = (tenantId || 0) + "|" + method + " " + path.replace(/\/[A-Za-z0-9_-]{6,}.*$/, "/:id");
  const e = endpoints.get(ek) || { count: 0, err: 0, ms: 0 };
  e.count++; e.ms += ms; if (status >= 400) e.err++;
  endpoints.set(ek, e);
  totals.req++; totals.ms += ms; if (status >= 400) totals.err++;
  if (buckets.size > 4000) { const cutoff = Date.now() - 60 * MINUTE; for (const k of buckets.keys()) if (Number(k.split("|")[0]) < cutoff) buckets.delete(k); }
}

function snapshot(tenantId) {
  const t = tenantId == null ? null : tenantId;
  const now = Date.now();
  const series = [];
  for (let i = 29; i >= 0; i--) {
    const minute = Math.floor(now / MINUTE) * MINUTE - i * MINUTE;
    let req = 0, err = 0, ms = 0;
    for (const [k, b] of buckets) {
      const [m, tid] = k.split("|");
      if (Number(m) === minute && (t == null || Number(tid) === t)) { req += b.req; err += b.err; ms += b.ms; }
    }
    series.push({ t: minute, req, err, avgMs: req ? +(ms / req).toFixed(1) : 0 });
  }
  const eps = [];
  for (const [k, e] of endpoints) {
    const [tid, label] = k.split("|");
    if (t == null || Number(tid) === t) eps.push({ endpoint: label, count: e.count, err: e.err, avgMs: +(e.ms / e.count).toFixed(1) });
  }
  eps.sort((a, b) => b.count - a.count);
  return { series, endpoints: eps.slice(0, 12), totals: { ...totals, avgMs: totals.req ? +(totals.ms / totals.req).toFixed(1) : 0 } };
}

module.exports = { record, snapshot };
