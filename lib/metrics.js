/* LUXORA Platform — request metrics.

   Every request is recorded: server.js calls `record(tenant, method, pathname,
   status, latency)` on the response's `finish` event, and that call is
   unconditional. Both consoles read the SAME accumulator — the store console's
   Monitor view (`m.totals` / `m.series` / `m.endpoints`) and the platform
   command dashboard (`mon.totals`) — so Monitor is a live feature on every
   deployment rather than a production-only stub that returns an empty object.
   The Prometheus text export stays production-gated (prom-client is a
   production-only dependency); the accumulator it reads is always on.

   Shape both consoles render:
     totals:    { req, err, avgMs }                  — over the retained window
     series:    [{ t, req, err }]                    — 30 one-minute buckets
     endpoints: [{ endpoint, count, err, avgMs }]    — per route, busiest first

   `snapshot(tenantId)` scopes to one tenant; `snapshot(null)` folds every tenant
   together, which is what the platform's own front door renders. */

"use strict";

const isProd = process.env.NODE_ENV === "production";

const MIN_MS = 60_000;
const BUCKETS = 30;        // a 30-minute window, one bucket per minute
const EP_KEEP = 100;       // per-scope endpoint table cap (busiest survive)

/* scope key → accumulator. A scope is a tenant id, or 0 for requests that
   resolved no tenant (static assets, /healthz). The platform aggregate folds 0
   in: it is still traffic this server served. */
const scopes = new Map();

function acc(key) {
  let a = scopes.get(key);
  if (!a) { a = { buckets: [], endpoints: new Map() }; scopes.set(key, a); }
  return a;
}
const keyOf = tenant => (tenant === null || tenant === undefined) ? 0 : (Number(tenant) || 0);

/* the newest bucket is last; the window is a fixed 30 minutes so a console
   always renders a full chart — zero-filled before the first request and after
   a quiet spell, never a ragged stub */
function bucket(a, now) {
  const minute = Math.floor(now / MIN_MS) * MIN_MS;
  let b = a.buckets[a.buckets.length - 1];
  if (!b || b.t !== minute) {
    b = { t: minute, req: 0, err: 0, ms: 0 };
    a.buckets.push(b);
    while (a.buckets.length > BUCKETS) a.buckets.shift();
  }
  return b;
}

function record(tenant, method, pathname, status, latency) {
  const a = acc(keyOf(tenant));
  const isError = status >= 400;
  const b = bucket(a, Date.now());
  b.req++; if (isError) b.err++; b.ms += Math.max(0, Number(latency) || 0);
  /* collapse ids to the route: /api/products/42 → /api/products, so the table
     is a bounded set of real routes, not a row per object */
  const route = String(pathname || "").split("/").slice(0, 3).join("/") || "/";
  const ep = (String(method || "GET").toUpperCase()) + " " + route;
  const v = a.endpoints.get(ep);
  if (v) { v.count++; if (isError) v.err++; v.ms += Math.max(0, Number(latency) || 0); }
  else a.endpoints.set(ep, { count: 1, err: isError ? 1 : 0, ms: Math.max(0, Number(latency) || 0) });
  if (a.endpoints.size > EP_KEEP * 1.5) {
    const keep = [...a.endpoints.entries()].sort((x, y) => y[1].count - x[1].count).slice(0, EP_KEEP);
    a.endpoints = new Map(keep);
  }
}

/* exactly BUCKETS buckets ending at the current minute, oldest first — the
   console's bar chart and `series.length === 30` both rely on the fixed width */
function fillSeries(byMinute) {
  const now = Math.floor(Date.now() / MIN_MS) * MIN_MS;
  const out = [];
  for (let i = BUCKETS - 1; i >= 0; i--) {
    const t = now - i * MIN_MS;
    const b = byMinute.get(t);
    out.push({ t, req: b ? b.req : 0, err: b ? b.err : 0 });
  }
  return out;
}

function snapshot(tenantId) {
  const scoped = tenantId !== null && tenantId !== undefined;
  const keys = scoped ? [keyOf(tenantId)] : [...scopes.keys()];
  const byMinute = new Map();
  const eps = new Map();
  let req = 0, err = 0, ms = 0;
  for (const k of keys) {
    const a = scopes.get(k);
    if (!a) continue;
    for (const b of a.buckets) {
      req += b.req; err += b.err; ms += b.ms;
      const m = byMinute.get(b.t);
      if (m) { m.req += b.req; m.err += b.err; }
      else byMinute.set(b.t, { t: b.t, req: b.req, err: b.err });
    }
    for (const [ep, v] of a.endpoints) {
      const cur = eps.get(ep);
      if (cur) { cur.count += v.count; cur.err += v.err; cur.ms += v.ms; }
      else eps.set(ep, { endpoint: ep, count: v.count, err: v.err, ms: v.ms });
    }
  }
  const endpoints = [...eps.values()]
    .map(x => ({ endpoint: x.endpoint, count: x.count, err: x.err, avgMs: x.count ? +(x.ms / x.count).toFixed(1) : 0 }))
    .sort((a, b) => (b.count - a.count) || a.endpoint.localeCompare(b.endpoint))
    .slice(0, EP_KEEP);
  return {
    totals: { req, err, avgMs: req ? +(ms / req).toFixed(1) : 0 },
    series: fillSeries(byMinute),
    endpoints
  };
}

let getMetrics = () => "";
let trackRequest = () => {};
if (isProd) {
  try {
    const client = require("prom-client");
    client.collectDefaultMetrics();
    const apiRequests = new client.Counter({
      name: "luxora_api_requests_total",
      help: "Total number of API requests",
      labelNames: ["endpoint", "status"]
    });
    /* the scrape is a Prometheus read of the same accumulator the consoles use —
       one source of truth, exported in the Prometheus text format */
    getMetrics = () => {
      const snap = snapshot(null);
      const out = [];
      out.push("# HELP luxora_http_requests_total Total HTTP requests");
      out.push("# TYPE luxora_http_requests_total counter");
      out.push("luxora_http_requests_total " + snap.totals.req);
      out.push("# HELP luxora_http_errors_total Total error responses");
      out.push("# TYPE luxora_http_errors_total counter");
      out.push("luxora_http_errors_total " + snap.totals.err);
      out.push("# HELP luxora_http_duration_ms_avg Average handler duration");
      out.push("# TYPE luxora_http_duration_ms_avg gauge");
      out.push("luxora_http_duration_ms_avg " + snap.totals.avgMs);
      snap.series.slice(-3).forEach(s => {
        out.push("# HELP luxora_http_requests Recent per-minute requests");
        out.push("# TYPE luxora_http_requests gauge");
        out.push("luxora_http_requests{minute=\"" + new Date(s.t).toISOString() + "\"} " + s.req);
      });
      snap.endpoints.slice(0, 10).forEach(e =>
        out.push("luxora_http_endpoint_requests{endpoint=\"" + e.endpoint + "\"} " + e.count));
      try { out.push(require("./ucos-monitor.js").promMetrics("luxora_ucos")); } catch (e) { }
      return out.join("\n") + "\n";
    };
    trackRequest = (tenant, method, pathname, status) => {
      const endpoint = String(pathname || "").split("/").slice(0, 3).join("/");
      apiRequests.inc({ endpoint, status: String(status) });
    };
  } catch (e) {
    console.error("Metrics init failed:", e.message);
  }
}

module.exports = { trackRequest, getMetrics, snapshot, record };
