/* LUXORA Platform — pluggable infra adapters selected by lib/config (no code forks).
   Dependency-free: Redis via minimal RESP over net.Socket, S3 via SigV4 + global fetch,
   webhooks via fetch, queue/inline & local-disk as the safe defaults. Every factory is
   transport-injectable (__setTransport) so tests never touch the network. All backends
   degrade gracefully: if a chosen driver has no connection info it falls back to the
   in-process default rather than breaking a request. */
"use strict";
const fs = require("fs"); const path = require("path"); const crypto = require("crypto"); const net = require("net");

let TR = {
  fetch: (...a) => fetch(...a),
  connect: (opts) => net.connect(opts)
};
function __setTransport(t) { TR = Object.assign({}, TR, t || {}); }

const EXPORT_DIR = path.join(__dirname, "..", "data", "exports");

/* ---------- cache (memory authoritative; redis = distributed write-through mirror) ---------- */
function parseRedisUrl(u) { try { const x = new URL(u); return { host: x.hostname, port: Number(x.port) || 6379, password: x.password || undefined, db: x.pathname && x.pathname.length > 1 ? x.pathname.slice(1) : undefined }; } catch (e) { return null; } }
function redisCall(conn, args) {
  return new Promise(resolve => {
    let sock; try { sock = TR.connect({ host: conn.host, port: conn.port }); } catch (e) { return resolve({ error: e.message }); }
    const cmd = "*" + args.length + "\r\n" + args.map(a => "$" + Buffer.byteLength(String(a)) + "\r\n" + a + "\r\n").join("");
    let buf = ""; let done = false; const finish = v => { if (!done) { done = true; try { sock.destroy(); } catch (e) { } resolve(v); } };
    sock.setTimeout(1500, () => finish({ error: "timeout" }));
    sock.on("error", e => finish({ error: e.message }));
    sock.on("data", d => { buf += d.toString(); if (/\r\n$/.test(buf)) { const m = /\+([^\r]*)|:([^\r]*)|\$\d+\r\n([^\r]*)/.exec(buf); finish({ value: m ? (m[1] != null ? m[1] : m[2] != null ? m[2] : m[3]) : buf.trim() }); } });
    if (conn.password) sock.write("*2\r\n$4\r\nAUTH\r\n$" + Buffer.byteLength(conn.password) + "\r\n" + conn.password + "\r\n");
    sock.write(cmd);
  });
}
function cache(driver, params) {
  const mem = new Map();
  const rconn = driver === "redis" ? parseRedisUrl((params && params.url) || "") : null;
  const writeThrough = (op, args) => { if (rconn) redisCall(rconn, args).catch(() => { }); };
  return {
    kind: rconn ? "redis(write-through)" : "memory",
    get(k) { return mem.get(k); },
    has(k) { return mem.has(k); },
    set(k, v) { mem.set(k, v); writeThrough("set", ["SET", "lx:" + k, typeof v === "string" ? v : JSON.stringify(v)]); },
    del(k) { mem.delete(k); writeThrough("del", ["DEL", "lx:" + k]); },
    delete(k) { return this.del(k); },
    clear() { mem.clear(); }
  };
}

/* ---------- rate-limit / KV store (memory token-buckets; redis mirrors shared counts) ---------- */
function kv(driver, params) {
  const mem = new Map(); const rconn = driver === "redis" ? parseRedisUrl((params && params.url) || "") : null;
  return {
    kind: rconn ? "redis" : "memory",
    incr(k, by) { const n = (mem.get(k) || 0) + (by || 1); mem.set(k, n); if (rconn) redisCall(rconn, ["INCRBY", "lx:" + k, String(by || 1)]).catch(() => { }); return n; },
    get(k) { return mem.get(k) || 0; },
    set(k, v) { mem.set(k, v); if (rconn) redisCall(rconn, ["SET", "lx:" + k, String(v)]).catch(() => { }); },
    del(k) { mem.delete(k); if (rconn) redisCall(rconn, ["DEL", "lx:" + k]).catch(() => { }); }
  };
}

/* ---------- storage: local disk | S3 (SigV4) | webhook ---------- */
function awsRegionFrom(bucket) { return "us-east-1"; }
function sha256hex(b) { return crypto.createHash("sha256").update(b).digest("hex"); }
function hmac(k, s) { return crypto.createHmac("sha256", k).update(s).digest(); }
function sigv4({ method, host, region, service, path: p, query, headers, accessKey, secretKey, payload }) {
  const amzDate = new Date().toISOString().replace(/[:-]|\.\d{3}/g, ""); const dateStamp = amzDate.slice(0, 10);
  const allHeaders = Object.assign({ host, "x-amz-date": amzDate, "x-amz-content-sha256": sha256hex(payload) }, headers || {});
  const signedKeys = Object.keys(allHeaders).map(k => k.toLowerCase()).sort();
  const canonicalHeaders = signedKeys.map(k => k + ":" + String(allHeaders[k]).trim() + "\n").join("");
  const canonical = [method, p, query || "", canonicalHeaders, signedKeys.join(";"), sha256hex(payload)].join("\n");
  const scope = dateStamp + "/" + region + "/" + service + "/aws4_request";
  const cr = [service, amzDate, scope, sha256hex(Buffer.from(canonical))].join("\n");
  let k = hmac("AWS4" + secretKey, dateStamp); k = hmac(k, region); k = hmac(k, service); k = hmac(k, "aws4_request");
  const signature = crypto.createHmac("sha256", k).update(cr).digest("hex");
  const auth = "AWS4-HMAC-SHA256 Credential=" + accessKey + "/" + scope + ", Signed-Headers=" + signedKeys.join(";") + ", Signature=" + signature;
  return Object.assign(allHeaders, { Authorization: auth });
}
function storage(driver, params) {
  if (driver === "s3" && params && params.bucket && params.accessKey && params.secretKey) {
    const region = params.region || "us-east-1"; const endpoint = params.endpoint || `https://s3.${region}.amazonaws.com`;
    const base = new URL(endpoint);
    return {
      kind: "s3",
      async put(key, buf, contentType) {
        const p = "/" + (params.bucket) + "/" + key.replace(/^\/+/, "");
        const host = base.hostname;
        const headers = sigv4({ method: "PUT", host, region, service: "s3", path: p, headers: { "content-type": contentType || "application/octet-stream" }, accessKey: params.accessKey, secretKey: params.secretKey, payload: buf });
        const url = base.origin + p;
        const r = await TR.fetch(url, { method: "PUT", headers, body: Buffer.isBuffer(buf) ? buf : Buffer.from(String(buf)) });
        return { ok: r.ok, url, key, status: r.status };
      },
      async get(key) { const p = "/" + params.bucket + "/" + key.replace(/^\/+/, ""); const r = await TR.fetch(base.origin + p); return { ok: r.ok, text: r.ok ? await r.text() : "" }; },
      url(key) { return base.origin + "/" + params.bucket + "/" + key.replace(/^\/+/, ""); }
    };
  }
  if (driver === "webhook" && params && params.url) {
    return {
      kind: "webhook",
      async put(key, buf, contentType) { const r = await TR.fetch(params.url, { method: "POST", headers: Object.assign({ "content-type": "application/json" }, params.secret ? { Authorization: "Bearer " + params.secret } : {}), body: JSON.stringify({ key, contentType, size: Buffer.byteLength(buf), data: String(buf).slice(0, 4096) }) }); return { ok: r.ok, key, url: params.url }; },
      async get() { return { ok: false, text: "" }; }, url(key) { return params.url + "?key=" + key; }
    };
  }
  return { /* local default */
    kind: "local",
    async put(key, buf, contentType) { try { if (!fs.existsSync(EXPORT_DIR)) fs.mkdirSync(EXPORT_DIR, { recursive: true }); } catch (e) { } const file = path.join(EXPORT_DIR, key.replace(/[\/\\]/g, "_")); fs.writeFileSync(file, Buffer.isBuffer(buf) ? buf : Buffer.from(String(buf))); return { ok: true, key, file, url: "/exports/" + path.basename(file) }; },
    async get(key) { const file = path.join(EXPORT_DIR, key.replace(/[\/\\]/g, "_")); return fs.existsSync(file) ? { ok: true, text: fs.readFileSync(file, "utf8") } : { ok: false, text: "" }; },
    url(key) { return "/exports/" + key.replace(/[\/\\]/g, "_"); }
  };
}

/* ---------- queue: inline (runs now) | redis (LPUSH) | webhook (POST job) ---------- */
const HANDLERS = {};
function registerHandler(type, fn) { HANDLERS[type] = fn; }
async function dispatch(job) { const fn = HANDLERS[job.type]; if (!fn) return { ran: false, skipped: "no-handler" }; try { const out = await fn(job, job.payload); return { ran: true, out }; } catch (e) { return { ran: true, error: e.message }; } }
function queue(driver, params) {
  if (driver === "redis") { const rconn = parseRedisUrl((params && params.url) || ""); if (rconn) return { kind: "redis", async push(job) { const r = await redisCall(rconn, ["LPUSH", "lx:queue", JSON.stringify(job)]); return { mode: "redis", ran: false, queued: !r.error }; }, drain: async () => ({ mode: "redis" }) }; }
  if (driver === "webhook" && params && params.url) return { kind: "webhook", async push(job) { const r = await TR.fetch(params.url, { method: "POST", headers: Object.assign({ "content-type": "application/json" }, params.secret ? { Authorization: "Bearer " + params.secret } : {}), body: JSON.stringify(job) }); return { mode: "webhook", ran: false, ok: r.ok }; }, drain: async () => ({ mode: "webhook" }) };
  return { kind: "inline", async push(job) { const res = await dispatch(job); return Object.assign({ mode: "inline", ran: true }, res); }, drain: async () => ({ mode: "inline" }) };
}

/* factories keyed by config concern */
function build(concern, cfg) {
  cfg = cfg || { driver: (concern === "queue" ? "inline" : concern === "storage" ? "local" : "memory"), params: {} };
  const d = cfg.driver, p = cfg.params || {};
  if (concern === "cache") return cache(d, p);
  if (concern === "ratelimit") return kv(d, p);
  if (concern === "storage") return storage(d, p);
  if (concern === "queue") return queue(d, p);
  return cache("memory", {});
}
module.exports = { build, cache, kv, storage, queue, registerHandler, dispatch, sigv4, parseRedisUrl, __setTransport, EXPORT_DIR };
