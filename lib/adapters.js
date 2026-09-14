/* LUXORA Platform — pluggable infra adapters selected by lib/config (no code forks).
   Dependency-free: Redis via a real RESP client over net.Socket, S3 via SigV4 + fetch,
   webhooks via fetch, and a Postgres wire client (lib/pg.js). Queue/inline & local-disk /
   memory are the safe defaults so single-node + CI work with zero services. Every factory is
   transport-injectable (__setTransport) for deterministic tests. Chosen-but-unreachable or
   unconfigured backends fall back to the in-process default rather than break a request. */
"use strict";
const fs = require("fs"); const path = require("path"); const crypto = require("crypto"); const net = require("net");

let TR = { fetch: (...a) => fetch(...a), connect: (opts) => net.connect(opts) };
function __setTransport(t) { TR = Object.assign({}, TR, t || {}); }
const EXPORT_DIR = path.join(__dirname, "..", "data", "exports");

/* ================= Redis: real RESP client (connection-per-command, full reply parse) ============ */
function parseRedisUrl(u) { if (!u) return null; try { const x = new URL(u.replace(/^redis:/, "http:")); return { host: x.hostname || "127.0.0.1", port: Number(x.port) || 6379, password: decodeURIComponent(x.password || "") || undefined, db: x.pathname && x.pathname.length > 1 ? Number(x.pathname.slice(1)) : undefined }; } catch (e) { return null; } }
function encodeCmd(args) { return "*" + args.length + "\r\n" + args.map(a => { const s = String(a); return "$" + Buffer.byteLength(s) + "\r\n" + s + "\r\n"; }).join(""); }
/* parse one complete RESP reply from buf starting at pos; returns { value, next, complete } */
function parseReply(buf, pos) {
  if (pos >= buf.length) return { complete: false };
  const type = String.fromCharCode(buf[pos]);
  const nl = buf.indexOf("\r\n", pos + 1);
  if (nl < 0) return { complete: false };
  const line = buf.slice(pos + 1, nl).toString();
  const after = nl + 2;
  if (type === "+") return { value: line, next: after, complete: true };
  if (type === "-") return { value: { __error: line.slice(4) || line }, next: after, complete: true };
  if (type === ":") return { value: Number(line), next: after, complete: true };
  if (type === "$") { if (line === "-1") return { value: null, next: after, complete: true }; const len = Number(line); if (buf.length < after + len + 2) return { complete: false }; return { value: buf.slice(after, after + len).toString(), next: after + len + 2, complete: true }; }
  if (type === "*") { const n = Number(line); if (n === -1) return { value: null, next: after, complete: true }; const arr = []; let p = after; for (let i = 0; i < n; i++) { const r = parseReply(buf, p); if (!r.complete) return { complete: false }; arr.push(r.value); p = r.next; } return { value: arr, next: p, complete: true }; }
  return { value: buf.slice(pos, after).toString(), next: after, complete: true };
}
/* run several commands in order on one connection (AUTH/SELECT auto-prepended), return the LAST reply */
function redisBatch(conn, list, timeoutMs = 1500) {
  if (!conn) return Promise.resolve({ __error: "no redis conn" });
  return new Promise(resolve => {
    let sock; try { sock = TR.connect({ host: conn.host, port: conn.port }); } catch (e) { return resolve({ __error: e.message }); }
    const payload = list.map(args => encodeCmd(args)).join("");
    let buf = Buffer.alloc(0); const replies = []; let done = false;
    const finish = () => { if (!done) { done = true; clearTimeout(to); try { sock.destroy(); } catch (e) { } resolve(replies.length ? replies[replies.length - 1] : { __error: "empty" }); } };
    const to = setTimeout(finish, timeoutMs);
    sock.on("error", () => finish()); sock.on("end", finish);
    sock.on("data", d => {
      buf = Buffer.concat([buf, d]); let pos = 0;
      while (pos < buf.length) { const r = parseReply(buf, pos); if (!r.complete) break; replies.push(r.value); pos = r.next; }
      const want = list.length + (conn.password ? 1 : 0) + (conn.db ? 1 : 0);
      if (replies.length >= want) finish();
    });
    const pre = []; if (conn.password) pre.push(["AUTH", conn.password]); if (conn.db) pre.push(["SELECT", conn.db]);
    sock.write(pre.concat(list).map(encodeCmd).join(""));
  });
}
function redis(url) { const conn = typeof url === "string" ? parseRedisUrl(url) : url; return { conn, call: (args) => redisBatch(conn, [args]), ok: v => !(v && v.__error) }; }

/* ---- cache: memory authoritative; redis = distributed write-through + cross-node hydrate ---- */
function cache(driver, params) {
  const mem = new Map(); const url = driver === "redis" ? (params && params.url) : null; const conn = url ? parseRedisUrl(url) : null;
  const bcast = (op, key, val) => { if (conn) { const list = op === "del" ? [["DEL", "lx:" + key]] : [["SET", "lx:" + key, val]]; redisBatch(conn, list).catch(() => { }); } };
  return {
    kind: conn ? "redis(write-through)" : "memory",
    get(k) { return mem.get(k); },
    has(k) { return mem.has(k); },
    set(k, v) { mem.set(k, v); bcast("set", k, typeof v === "string" ? v : JSON.stringify(v)); },
    del(k) { mem.delete(k); bcast("del", k); }, delete(k) { return this.del(k); }, clear() { mem.clear(); },
    async hydrate(prefix) { if (!conn) return 0; const keys = await redisBatch(conn, [["KEYS", "lx:" + (prefix || "") + "*"]]); if (!keys || keys.__error || !Array.isArray(keys.value)) return 0; let n = 0; for (const key of keys.value) { const v = await redisBatch(conn, [["GET", key]]); if (v && !v.__error && v !== null) { try { mem.set(String(key).replace(/^lx:/, ""), JSON.parse(v)); n++; } catch (e) { } } } return n; }
  };
}

/* ---- kv / shared rate-limit state: memory default, redis shared ---- */
function kv(driver, params) {
  const mem = new Map(); const conn = (driver === "redis" && params && params.url) ? parseRedisUrl(params.url) : null;
  return {
    kind: conn ? "redis" : "memory",
    incr(k, by) { const n = (mem.get(k) || 0) + (by || 1); mem.set(k, n); if (conn) redisBatch(conn, [["INCRBY", "lx:" + k, String(by || 1)]]).catch(() => { }); return n; },
    async incrShared(k, by) { if (!conn) return this.incr(k, by); const v = await redisBatch(conn, [["INCRBY", "lx:" + k, String(by || 1)]]); return Number(v) || 0; },
    get(k) { return mem.get(k) || 0; },
    set(k, v) { mem.set(k, v); if (conn) redisBatch(conn, [["SET", "lx:" + k, String(v)]]).catch(() => { }); },
    async setShared(k, v) { if (conn) return redisBatch(conn, [["SET", "lx:" + k, String(v)]]); this.set(k, v); },
    async getShared(k) { if (!conn) return this.get(k); const v = await redisBatch(conn, [["GET", "lx:" + k]]); return v && !v.__error ? Number(v) : 0; },
    del(k) { mem.delete(k); if (conn) redisBatch(conn, [["DEL", "lx:" + k]]).catch(() => { }); }
  };
}

/* ---- storage: local | S3 (SigV4) | webhook ---- */
function sha256hex(b) { return crypto.createHash("sha256").update(b).digest("hex"); }
function hmac(k, s) { return crypto.createHmac("sha256", k).update(s).digest(); }
function sigv4({ method, host, region = "us-east-1", service = "s3", path: p, headers = {}, accessKey, secretKey, payload }) {
  const amzDate = new Date().toISOString().replace(/[:-]|\.\d{3}/g, ""); const dateStamp = amzDate.slice(0, 10);
  const allHeaders = Object.assign({ host, "x-amz-date": amzDate, "x-amz-content-sha256": sha256hex(payload) }, headers);
  const signed = Object.keys(allHeaders).map(k => k.toLowerCase()).sort();
  const canon = [method, p, "", signed.map(k => k + ":" + String(allHeaders[k]).trim() + "\n").join(""), signed.join(";"), sha256hex(payload)].join("\n");
  const scope = dateStamp + "/" + region + "/" + service + "/aws4_request";
  const cr = [service, amzDate, scope, sha256hex(Buffer.from(canon))].join("\n");
  let k = hmac("AWS4" + secretKey, dateStamp); k = hmac(k, region); k = hmac(k, service); k = hmac(k, "aws4_request");
  return Object.assign(allHeaders, { Authorization: "AWS4-HMAC-SHA256 Credential=" + accessKey + "/" + scope + ", Signed-Headers=" + signed.join(";") + ", Signature=" + crypto.createHmac("sha256", k).update(cr).digest("hex") });
}
function storage(driver, params) {
  if (driver === "s3" && params && params.bucket && params.accessKey && params.secretKey) {
    const region = params.region || "us-east-1"; const base = new URL(params.endpoint || `https://s3.${region}.amazonaws.com`);
    return { kind: "s3", async put(key, buf, ct) { const p = "/" + params.bucket + "/" + key.replace(/^\/+/, ""); const headers = sigv4({ method: "PUT", host: base.hostname, region, path: p, headers: { "content-type": ct || "application/octet-stream" }, accessKey: params.accessKey, secretKey: params.secretKey, payload: buf }); const r = await TR.fetch(base.origin + p, { method: "PUT", headers, body: Buffer.isBuffer(buf) ? buf : Buffer.from(String(buf)) }); return { ok: r.ok, url: base.origin + p, key, status: r.status }; }, async get(key) { const r = await TR.fetch(base.origin + "/" + params.bucket + "/" + key.replace(/^\/+/, "")); return { ok: r.ok, text: r.ok ? await r.text() : "" }; }, url(key) { return base.origin + "/" + params.bucket + "/" + key; } };
  }
  if (driver === "webhook" && params && params.url) {
    return { kind: "webhook", async put(key, buf, ct) { const r = await TR.fetch(params.url, { method: "POST", headers: Object.assign({ "content-type": "application/json" }, params.secret ? { Authorization: "Bearer " + params.secret } : {}), body: JSON.stringify({ key, contentType: ct, size: Buffer.byteLength(buf) }) }); return { ok: r.ok, key, url: params.url }; }, async get() { return { ok: false, text: "" }; }, url(key) { return params.url + "?key=" + key; } };
  }
  return { kind: "local", async put(key, buf, ct) { try { if (!fs.existsSync(EXPORT_DIR)) fs.mkdirSync(EXPORT_DIR, { recursive: true }); } catch (e) { } const file = path.join(EXPORT_DIR, key.replace(/[\/\\]/g, "_")); fs.writeFileSync(file, Buffer.isBuffer(buf) ? buf : Buffer.from(String(buf))); return { ok: true, key, file, url: "/exports/" + path.basename(file) }; }, async get(key) { const file = path.join(EXPORT_DIR, key.replace(/[\/\\]/g, "_")); return fs.existsSync(file) ? { ok: true, text: fs.readFileSync(file, "utf8") } : { ok: false, text: "" }; }, url(key) { return "/exports/" + key.replace(/[\/\\]/g, "_"); } };
}

/* ---- queue: inline | redis | webhook; redis also supports a real consumer/worker ---- */
const HANDLERS = {};
function registerHandler(type, fn) { HANDLERS[type] = fn; }
async function dispatch(job) { const fn = HANDLERS[job.type]; if (!fn) return { ran: false, skipped: "no-handler" }; try { const out = await fn(job, job.payload); return { ran: true, out }; } catch (e) { return { ran: true, error: e.message }; } }
function queue(driver, params) {
  if (driver === "redis" && params && params.url) {
    const conn = parseRedisUrl(params.url); const Q = "lx:queue";
    return { kind: "redis", async push(job) { const r = await redisBatch(conn, [["LPUSH", Q, JSON.stringify(job)]]); return { mode: "redis", ran: false, queued: !(r && r.__error) }; }, async drain(max) { let n = 0; for (let i = 0; i < (max || 50); i++) { const raw = await redisBatch(conn, [["RPOP", Q]]); if (!raw || raw.__error || raw === null) break; let job; try { job = JSON.parse(raw); } catch (e) { continue; } await dispatch(job); n++; } return { mode: "redis", drained: n }; } };
  }
  if (driver === "webhook" && params && params.url) return { kind: "webhook", async push(job) { const r = await TR.fetch(params.url, { method: "POST", headers: Object.assign({ "content-type": "application/json" }, params.secret ? { Authorization: "Bearer " + params.secret } : {}), body: JSON.stringify(job) }); return { mode: "webhook", ran: false, ok: r.ok }; }, async drain() { return { mode: "webhook" }; } };
  return { kind: "inline", async push(job) { const res = await dispatch(job); return Object.assign({ mode: "inline", ran: true }, res); }, async drain(max) { return { mode: "inline", drained: 0 }; } };
}
/* start a poller that drains a redis queue into local handlers (multi-node worker) */
function startWorker(cfg, { intervalMs = 3000, batch = 25 } = {}) {
  const q = queue((cfg && cfg.driver) || "inline", cfg && cfg.params);
  if (q.kind !== "redis") return { active: false, stop() { } };
  let stopped = false; const id = setInterval(() => { if (!stopped) q.drain(batch).catch(() => { }); }, intervalMs); if (id.unref) id.unref();
  return { active: true, kind: "redis", stop() { stopped = true; clearInterval(id); } };
}

function build(concern, cfg) {
  cfg = cfg || {}; const d = cfg.driver || ({ queue: "inline", storage: "local", session: "db", outbound: "auto", db: "sqlite" }[concern] || "memory"), p = cfg.params || {};
  if (concern === "cache") return cache(d, p);
  if (concern === "ratelimit") return kv(d, p);
  if (concern === "storage") return storage(d, p);
  if (concern === "queue") return queue(d, p);
  if (concern === "db") { try { return require("./pg.js").adapter(p); } catch (e) { return { kind: "memory", err: e.message }; } }
  return cache("memory", {});
}
module.exports = { build, cache, kv, storage, queue, redis, redisBatch, startWorker, registerHandler, dispatch, sigv4, parseRedisUrl, parseReply, encodeCmd, __setTransport, EXPORT_DIR };
