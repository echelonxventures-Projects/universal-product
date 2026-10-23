/* LUXORA Platform — minimal Postgres wire client (zero dependencies).
   Frontend/backend protocol: StartupMessage + (trust | cleartext | MD5) auth + simple Query,
   parsing RowDescription/DataRow/CommandComplete/ReadyForQuery/ErrorResponse. Selected via
   config `db=postgres`; the app's synchronous data layer (lib/db.js) stays SQLite by design, so
   this powers the async surfaces (workers, exports, reporting, future async handlers) — a full
   sync→async app migration on Postgres is the remaining, separately-scoped step (see README).
   TLS is negotiated when the URL asks for it (sslmode=require/prefer/allow) so managed Postgres
   (RDS/Cloud SQL/Neon/Supabase) connects instead of failing plaintext. SCRAM-SHA-256 is
   intentionally NOT half-implemented: if a server demands it, ping() reports "auth unsupported"
   — set the role to md5/trust for the migration, then SCRAM for app traffic. Pure encode/parse
   helpers are exported and unit-tested without a live server. */
"use strict";
const crypto = require("crypto"); const net = require("net"); const tls = require("tls");
const fs = require("fs");

let TR = { connect: (o) => net.connect(o) };
function __setTransport(t) { TR = Object.assign({}, TR, t || {}); }

function cstr(s) { return Buffer.from(String(s) + "\0", "utf8"); }
function int32(n) { const b = Buffer.alloc(4); b.writeInt32BE(n | 0, 0); return b; }
function fe(type, body) { const b = Buffer.from(body); return Buffer.concat([Buffer.from(type, "ascii"), int32(4 + b.length), b]); }
function cstring(buf, off) { let e = off; while (e < buf.length && buf[e] !== 0) e++; return { s: buf.toString("utf8", off, e), next: e + 1 }; }
function md5(user, password, salt) { const a = crypto.createHash("md5").update(String(password) + user).digest("hex"); return "md5" + crypto.createHash("md5").update(Buffer.concat([Buffer.from(a, "hex"), salt])).digest("hex"); }

/* M5: managed Postgres requires TLS, and sslmode=require in the URL was silently ignored. Offer
   an SSLRequest (the GSSENC/SSL negotiation the server answers with 'S' or 'N') when the URL asks
   for it, then upgrade the socket. Servers that answer 'N' keep working in plaintext. */
/* the URL's sslmode, as libpq reads it: require and verify-* insist on TLS (a server that refuses
   it is an error, never a quiet plaintext connection), verify-* also checks the certificate
   (verify-full its host name too), prefer and allow take TLS when the server offers it */
function sslMode(url) {
  try { const m = /[?&]sslmode=([^&]+)/i.exec(String(url || "")); return m ? decodeURIComponent(m[1]).toLowerCase() : "disable"; } catch (e) { return "disable"; }
}
function wantsSsl(url) { return ["require", "prefer", "allow", "verify-ca", "verify-full"].includes(sslMode(url)); }
function mustSsl(url) { return ["require", "verify-ca", "verify-full"].includes(sslMode(url)); }
function sslOptions(conn) {
  const mode = sslMode(conn.__url);
  const o = { host: conn.host, port: conn.port, rejectUnauthorized: mode.startsWith("verify-") };
  /* verify-ca trusts the chain without matching the host name */
  if (mode === "verify-ca") o.checkServerIdentity = () => undefined;
  /* servername must be a hostname — Node rejects an IP here (and the probe surfaced it).
     Only set it for real hostnames; IP-literal hosts use the host as-is. */
  if (conn.host && !/^\d{1,3}(\.\d{1,3}){3}$/.test(conn.host) && !conn.host.includes(":")) o.servername = conn.host;
  /* honour a CA path if the URL carries one (sslrootcert=/path) */
  try { const m = /[?&]sslrootcert=([^&]+)/i.exec(String(conn.__url || "")); if (m) { const ca = fs.readFileSync(decodeURIComponent(m[1]), "utf8"); o.ca = ca; o.rejectUnauthorized = true; } } catch (e) { }
  return o;
}
/* a plaintext socket is "ready" as soon as it is connected. net.connect() emits the connect
   event asynchronously, but a socket handed to us may already be connected (or the event may
   fire before this listener is attached in the transport shim) — so handle both states. */
/* The caller passes onData/onError; the socket is wired BEFORE the connect event is handled, so
   no server reply is lost between "connected" and "listener attached" (that window is exactly
   what made a deferred onReady drop the AuthenticationOk reply). */
function attachSock(s, onData, onError) {
  s.on("data", onData);
  s.on("error", onError);
}
function ready(s, onData, onError, writeStartup, conn) {
  attachSock(s, onData, onError);
  if (writeStartup) s.write(startupPacket(conn.user, conn.database));
}
function wirePlain(s, onData, onError, writeStartup, conn) {
  const go = () => ready(s, onData, onError, writeStartup, conn);
  if (!s.pending && s.readyState !== "opening") return go();
  s.once("connect", go);
  s.on("error", onError);
}

function openSocket(conn, onData, onError, writeStartup) {
  if (!wantsSsl(conn.__url)) {
    const s = TR.connect({ host: conn.host, port: conn.port });
    wirePlain(s, onData, onError, writeStartup, conn);
    return s;
  }
  /* plaintext probe first: send SSLRequest and read the single-byte reply. The caller holds a
     handle to whichever socket is live — the TLS socket after an upgrade, the fresh one after a
     refusal — so nothing is ever written past TLS or into the closed probe. */
  const probe = TR.connect({ host: conn.host, port: conn.port });
  let live = probe;
  const handle = { write: b => live.write(b), destroy: () => live.destroy() };
  let buf = Buffer.alloc(0), settled = false;
  const req = Buffer.concat([int32(8), int32(80877103)]);
  probe.write(req);
  const t = setTimeout(() => { try { probe.destroy(); } catch (e) { } onError(new Error("SSL negotiation timeout")); }, 5000);
  const done = fn => { if (!settled) { settled = true; clearTimeout(t); fn(); } };
  probe.on("data", d => {
    buf = Buffer.concat([buf, d]);
    if (buf.length < 1) return;
    done(() => {
      if (buf[0] === 83 /* 'S' — server accepts SSL */) {
        /* the TLS handshake runs on the socket that sent the SSLRequest: a fresh socket would
           open with a handshake Postgres is not expecting. A failed handshake must reject the
           query, not hang or throw out of band */
        probe.removeAllListeners("data");
        let tlsSock;
        try { tlsSock = live = tls.connect({ ...sslOptions(conn), socket: probe }, () => ready(tlsSock, onData, onError, writeStartup, conn)); }
        catch (e) { return onError(new Error("TLS upgrade failed: " + e.message)); }
        tlsSock.on("error", e => onError(new Error("TLS error: " + e.message)));
        return;
      }
      /* 'N' — server refuses SSL: continue in plaintext on a fresh socket, unless TLS is required */
      try { probe.destroy(); } catch (e) { }
      if (mustSsl(conn.__url)) return onError(new Error("the server does not accept TLS and sslmode=" + sslMode(conn.__url) + " requires it"));
      const s = live = TR.connect({ host: conn.host, port: conn.port });
      wirePlain(s, onData, onError, writeStartup, conn);
    });
  });
  probe.on("error", e => done(() => onError(e)));
  return handle;
}

function startupPacket(user, database) { const params = Buffer.concat([cstr("user"), cstr(user), cstr("database"), cstr(database), cstr("application_name"), cstr("luxora"), Buffer.from("\0")]); return Buffer.concat([int32(8 + params.length), int32(196608), params]); }

function parseMessages(buf, off = 0) {
  const out = []; let p = off;
  while (p + 5 <= buf.length) {
    const type = String.fromCharCode(buf[p]); const len = buf.readInt32BE(p + 1); // len counts the 4 size bytes + body (NOT the type byte)
    if (len < 4 || buf.length < p + 1 + len) break; // incomplete
    out.push({ type, body: buf.slice(p + 5, p + 1 + len) }); p += 1 + len;
    if (type === "X") break;
  }
  return { messages: out, rest: buf.slice(p) };
}
function parseRowDescription(body) { const n = body.readInt16BE(0); let p = 2; const cols = []; const oids = []; for (let i = 0; i < n; i++) { const nm = cstring(body, p); const oid = body.readInt32BE(nm.next + 6); p = nm.next + 18; cols.push(nm.s); oids.push(oid); } cols.oids = oids; return cols; }
function parseDataRow(body) { const n = body.readInt16BE(0); let p = 2; const vals = []; for (let i = 0; i < n; i++) { const l = body.readInt32BE(p); p += 4; if (l === -1) vals.push(null); else { vals.push(body.toString("utf8", p, p + l)); p += l; } } return vals; }
function parseError(body) { let p = 0, err = {}; while (p < body.length && body[p] !== 0) { const f = String.fromCharCode(body[p]); p++; const r = cstring(body, p); err[f] = r.s; p = r.next; } return err; }

function parseConn(url) { try { const x = new URL(url.replace(/^postgres(ql)?:/, "http:")); return { host: x.hostname || "127.0.0.1", port: Number(x.port) || 5432, user: decodeURIComponent(x.username || "postgres"), password: decodeURIComponent(x.password || ""), database: decodeURIComponent((x.pathname || "/").slice(1)) || "postgres" }; } catch (e) { return null; } }
/* accept a URL string, {connectionString|url}, or an already-parsed {host,port,user,password,database}.
   The raw URL is retained (conn.__url) so TLS negotiation can read sslmode/sslrootcert. */
function normalizeConn(cfg) {
  if (typeof cfg === "string") { const c = parseConn(cfg); if (c) c.__url = cfg; return c; }
  if (cfg && (cfg.connectionString || cfg.url)) { const c = parseConn(cfg.connectionString || cfg.url); if (c) c.__url = cfg.connectionString || cfg.url; return c; }
  return cfg;
}

function query(cfg, sql, { timeoutMs = 8000 } = {}) {
  const conn = normalizeConn(cfg);
  if (!conn) return Promise.resolve({ error: "invalid postgres connection" });
  return new Promise(resolve => {
    let sock = null, buf = Buffer.alloc(0), columns = [], rows = [], cmdTag = "", done = false, sentQuery = false;
    const finish = v => { if (!done) { done = true; clearTimeout(to); if (sock) { try { sock.write(fe("X", Buffer.alloc(0))); } catch (e) { } try { sock.destroy(); } catch (e) { } } resolve(v); } };
    const to = setTimeout(() => finish({ error: "timeout" }), timeoutMs);
    const onData = d => {
      buf = Buffer.concat([buf, d]); const { messages, rest } = parseMessages(buf); buf = rest;
      for (const m of messages) {
        if (m.type === "R") { const code = m.body.readInt32BE(0);
          if (code === 0) continue; // AuthenticationOk
          if (code === 3) { sock.write(fe("p", cstr(conn.password || ""))); continue; } // cleartext
          if (code === 5) { sock.write(fe("p", cstr(md5(conn.user, conn.password || "", m.body.slice(4, 8))))); continue; } // MD5
          return finish({ error: "auth method " + code + " not supported (needs SCRAM/GSS) — configure a trust/md5/cleartext role for LUXORA" }); }
        if (m.type === "E") { const err = parseError(m.body); return finish({ error: err.M || "postgres error", code: err.C, severity: err.S }); }
        if (m.type === "T") { columns = parseRowDescription(m.body); }
        if (m.type === "D") { rows.push(parseDataRow(m.body)); }
        if (m.type === "C") { cmdTag = m.body.toString("utf8").replace(/\0.*$/, ""); }
        if (m.type === "N") { continue; } // NoticeResponse — ignore
        if (m.type === "Z") { if (!sentQuery) { sentQuery = true; sock.write(fe("Q", Buffer.from(String(sql) + "\0", "utf8"))); continue; } return finish({ ok: true, columns, oids: columns.oids || [], rows, cmdTag }); }
      }
    };
    sock = openSocket(conn, onData, e => finish({ error: e.message }), true);
  });
}

/* ---- extended query with parameters ($1..$n), text format ---- */
function queryP(cfgObj, sqlText, params, opts) {
  params = params || []; const conn = normalizeConn(cfgObj);
  if (!conn) return Promise.resolve({ error: "invalid postgres connection" });
  opts = opts || {};
  return new Promise(resolve => {
    let sock = null, buf = Buffer.alloc(0), columns = [], rows = [], cmdTag = "", done = false, authPhase = 0;
    const finish = v => { if (!done) { done = true; clearTimeout(to); if (sock) { try { sock.write(fe("X", Buffer.alloc(0))); } catch (e) { } try { sock.destroy(); } catch (e) { } } resolve(v); } };
    const to = setTimeout(() => finish({ error: "timeout" }), opts.timeoutMs || 8000);
    const onData = d => {
      const send = m => sock.write(m);
      const ci32 = n => { const b = Buffer.alloc(4); b.writeInt32BE(n, 0); return b; };
      const msg = (type, body) => Buffer.concat([Buffer.from(type, "ascii"), ci32(4 + body.length), body]);
      const cstr2 = s => Buffer.concat([Buffer.from(String(s), "utf8"), Buffer.from("\0")]);
      function frame() {
        const i16 = n => { const b = Buffer.alloc(2); b.writeInt16BE(n, 0); return b; };
        const parse = msg("P", Buffer.concat([cstr2(""), cstr2(sqlText), i16(params.length), ...params.map(() => ci32(0))]));
        const fmt = Buffer.concat([i16(params.length), ...params.map(() => i16(0))]); // param format codes: all text
        const values = Buffer.concat([i16(params.length), ...params.map(p => { if (p == null) { const n = Buffer.alloc(4); n.writeInt32BE(-1, 0); return n; } const s = String(p); const l = Buffer.alloc(4); l.writeInt32BE(Buffer.byteLength(s), 0); return Buffer.concat([l, Buffer.from(s, "utf8")]); })]);
        const resultFmt = i16(0); // no result format codes => text
        const bind = msg("B", Buffer.concat([cstr2(""), cstr2(""), fmt, values, resultFmt]));
        const desc = msg("D", Buffer.concat([Buffer.from("S"), cstr2("")]));
        const exec = msg("E", Buffer.concat([cstr2(""), ci32(0)]));
        const sync = msg("S", Buffer.alloc(0));
        send(Buffer.concat([parse, bind, desc, exec, sync]));
      }
      buf = Buffer.concat([buf, d]); const { messages, rest } = parseMessages(buf); buf = rest;
      for (const m of messages) {
        if (m.type === "R") { const code = m.body.readInt32BE(0); if (code === 0) continue; if (code === 3) { send(msg("p", cstr(conn.password || ""))); continue; } if (code === 5) { send(msg("p", cstr(md5(conn.user, conn.password || "", m.body.slice(4, 8))))); continue; } return finish({ error: "auth method " + code + " unsupported" }); }
        if (m.type === "K" || m.type === "S" || m.type === "N") continue;
        if (m.type === "E") { const err = parseError(m.body); return finish({ error: err.M || "postgres error", code: err.C }); }
        if (m.type === "T") columns = parseRowDescription(m.body);
        if (m.type === "D") rows.push(parseDataRow(m.body));
        if (m.type === "C") cmdTag = m.body.toString("utf8").replace(/\0.*$/, "");
        if (m.type === "Z") { if (authPhase === 0) { authPhase = 1; frame(); continue; } return finish({ ok: true, columns, oids: columns.oids || [], rows, cmdTag }); }
      }
    };
    sock = openSocket(conn, onData, e => finish({ error: e.message }), true);
  });
}

/* ============================== a persistent connection ==============================
   One socket for the life of a caller (the db bridge's worker, a migration): it authenticates once
   (SCRAM-SHA-256 — Postgres's default since 14 and what managed services require — md5 or
   cleartext), upgrades to TLS in place when the URL asks for it, and runs one query at a time.
   A transaction is the connection's: BEGIN, its statements and COMMIT travel on the same socket.
   If the socket dies inside a transaction, every statement fails until the caller's ROLLBACK, so
   the rest of a broken transaction can never commit on a fresh connection by accident. */
function scram(password) {
  const nonce = crypto.randomBytes(18).toString("base64");
  const first = "n=,r=" + nonce;
  return {
    initial() { return Buffer.from("n,," + first, "utf8"); },
    next(serverFirst) {
      const f = Object.fromEntries(serverFirst.split(",").map(kv => [kv[0], kv.slice(2)]));
      if (!f.r || !f.r.startsWith(nonce) || !f.s || !f.i) throw new Error("SCRAM: unexpected server challenge");
      const salted = crypto.pbkdf2Sync(String(password || "").normalize("NFKC"), Buffer.from(f.s, "base64"), Number(f.i), 32, "sha256");
      const hmac = (k, d) => crypto.createHmac("sha256", k).update(d).digest();
      const clientKey = hmac(salted, "Client Key");
      const stored = crypto.createHash("sha256").update(clientKey).digest();
      const without = "c=biws,r=" + f.r;
      const auth = first + "," + serverFirst + "," + without;
      const sig = hmac(stored, auth);
      const proof = Buffer.from(clientKey.map((b, i) => b ^ sig[i]));
      this.expect = hmac(hmac(salted, "Server Key"), auth).toString("base64");
      return Buffer.from(without + ",p=" + proof.toString("base64"), "utf8");
    },
    verify(serverFinal) { const v = /(?:^|,)v=([^,]+)/.exec(serverFinal); if (!v || v[1] !== this.expect) throw new Error("SCRAM: the server's signature does not match"); }
  };
}
function connect(cfg, opts) {
  const conn = normalizeConn(cfg);
  if (!conn) return Promise.reject(new Error("invalid postgres connection"));
  const o = opts || {};
  return new Promise((resolveOpen, rejectOpen) => {
    let sock = null, buf = Buffer.alloc(0), opened = false, sasl = null;
    let status = "I", broken = false, dead = false;
    const queue = [];
    let cur = null;
    const api = {
      get dead() { return dead; }, get status() { return status; },
      query(sqlText, params, qo) { return enqueue({ kind: "ext", sql: sqlText, params: params || [], timeoutMs: (qo && qo.timeoutMs) || o.timeoutMs || 30000 }); },
      simple(sqlText, qo) { return enqueue({ kind: "simple", sql: sqlText, timeoutMs: (qo && qo.timeoutMs) || o.timeoutMs || 30000 }); },
      close() { if (!dead) { dead = true; try { sock.write(fe("X", Buffer.alloc(0))); } catch (e) { } try { sock.destroy(); } catch (e) { } } }
    };
    const fail = err => {
      if (!opened) { dead = true; try { sock && sock.destroy(); } catch (e) { } return rejectOpen(err); }
      /* a socket lost inside a transaction leaves the transaction broken, not silently gone */
      if (status !== "I") broken = true;
      dead = true;
      try { sock && sock.destroy(); } catch (e) { }
      if (cur) { const c = cur; cur = null; clearTimeout(c.timer); c.resolve({ error: "postgres connection lost: " + err.message }); }
      while (queue.length) queue.shift().resolve({ error: "postgres connection lost: " + err.message });
    };
    function enqueue(job) {
      return new Promise(resolve => {
        job.resolve = resolve;
        if (dead) return resolve({ error: "postgres connection closed", lost: true, broken });
        queue.push(job); pump();
      });
    }
    function pump() {
      if (cur || !queue.length || dead) return;
      cur = queue.shift();
      cur.res = { columns: [], oids: [], rows: [], cmdTag: "", error: null };
      cur.timer = setTimeout(() => fail(new Error("query timeout after " + cur.timeoutMs + "ms")), cur.timeoutMs);
      const ci32 = n => { const b = Buffer.alloc(4); b.writeInt32BE(n, 0); return b; };
      const i16 = n => { const b = Buffer.alloc(2); b.writeInt16BE(n, 0); return b; };
      if (cur.kind === "simple") return sock.write(fe("Q", Buffer.from(String(cur.sql) + "\0", "utf8")));
      const ps = cur.params;
      const values = Buffer.concat([i16(ps.length), ...ps.map(p => { if (p == null) return ci32(-1); const b = Buffer.from(typeof p === "object" ? JSON.stringify(p) : String(p), "utf8"); return Buffer.concat([ci32(b.length), b]); })]);
      sock.write(Buffer.concat([
        fe("P", Buffer.concat([cstr(""), cstr(cur.sql), i16(ps.length), ...ps.map(() => ci32(0))])),
        fe("B", Buffer.concat([cstr(""), cstr(""), i16(ps.length), ...ps.map(() => i16(0)), values, i16(0)])),
        fe("D", Buffer.concat([Buffer.from("P"), cstr("")])),
        fe("E", Buffer.concat([cstr(""), ci32(0)])),
        fe("S", Buffer.alloc(0))]));
    }
    function onMessage(m) {
      if (m.type === "R") {
        const code = m.body.readInt32BE(0);
        if (code === 0) return;
        if (code === 3) return sock.write(fe("p", cstr(conn.password || "")));
        if (code === 5) return sock.write(fe("p", cstr(md5(conn.user, conn.password || "", m.body.slice(4, 8)))));
        if (code === 10) {
          const mechs = m.body.slice(4).toString("utf8").split("\0").filter(Boolean);
          if (!mechs.includes("SCRAM-SHA-256")) return fail(new Error("no supported SASL mechanism: " + mechs.join(",")));
          sasl = scram(conn.password);
          const first = sasl.initial();
          return sock.write(fe("p", Buffer.concat([cstr("SCRAM-SHA-256"), int32(first.length), first])));
        }
        if (code === 11) { try { return sock.write(fe("p", sasl.next(m.body.slice(4).toString("utf8")))); } catch (e) { return fail(e); } }
        if (code === 12) { try { return sasl.verify(m.body.slice(4).toString("utf8")); } catch (e) { return fail(e); } }
        return fail(new Error("auth method " + code + " not supported"));
      }
      if (m.type === "E") {
        const err = parseError(m.body);
        if (!opened) return fail(new Error(err.M || "postgres error"));
        if (cur) { cur.res.error = err.M || "postgres error"; cur.res.code = err.C; }
        return;
      }
      if (m.type === "T") { if (cur) { cur.res.columns = parseRowDescription(m.body); cur.res.oids = cur.res.columns.oids || []; cur.res.rows = []; } return; }
      if (m.type === "D") { if (cur) cur.res.rows.push(parseDataRow(m.body)); return; }
      if (m.type === "C") { if (cur) cur.res.cmdTag = m.body.toString("utf8").replace(/\0.*$/, ""); return; }
      if (m.type === "Z") {
        status = String.fromCharCode(m.body[0]);
        if (!opened) { opened = true; return resolveOpen(api); }
        if (cur) {
          const c = cur; cur = null; clearTimeout(c.timer);
          const r = c.res;
          c.resolve(r.error ? { error: r.error, code: r.code } : { ok: true, columns: r.columns, oids: r.oids, rows: r.rows, cmdTag: r.cmdTag });
          pump();
        }
      }
      /* S (parameter status), K (backend key), N (notice), 1/2/n/t: nothing to do */
    }
    function onData(d) {
      buf = Buffer.concat([buf, d]);
      const { messages, rest } = parseMessages(buf); buf = rest;
      for (const m of messages) onMessage(m);
    }
    function start(s) {
      sock = s;
      s.on("data", onData);
      s.on("error", e => fail(e));
      s.on("close", () => { if (!dead) fail(new Error("socket closed")); });
      s.write(startupPacket(conn.user, conn.database));
    }
    const openTimer = setTimeout(() => fail(new Error("connect timeout")), o.connectTimeoutMs || 10000);
    const go = s => { clearTimeout(openTimer); start(s); };
    const plain = TR.connect({ host: conn.host, port: conn.port });
    plain.on("error", e => { clearTimeout(openTimer); fail(e); });
    plain.once("connect", () => {
      if (!wantsSsl(conn.__url)) return go(plain);
      /* SSLRequest on the plaintext socket, then upgrade that same socket */
      plain.write(Buffer.concat([int32(8), int32(80877103)]));
      plain.once("data", d => {
        if (d[0] !== 83) {
          if (!mustSsl(conn.__url)) return go(plain);
          clearTimeout(openTimer); return fail(new Error("the server does not accept TLS and sslmode=" + sslMode(conn.__url) + " requires it"));
        }
        const t = tls.connect({ ...sslOptions(conn), socket: plain }, () => go(t));
        t.on("error", e => { clearTimeout(openTimer); fail(new Error("TLS error: " + e.message)); });
      });
    });
  });
}

function adapter(params) {
  const url = (params && (params.url || params.connString)) || process.env.LX_PG_URL;
  if (!url) return { kind: "postgres", configured: false, async ping() { return { ok: false, error: "postgres not configured (set LX_PG_URL or runtime.db.params.url)" }; }, query: () => Promise.resolve({ error: "not configured" }) };
  return { kind: "postgres", configured: true, query: (sql) => query(url, sql), async ping() { const r = await query(url, "SELECT 1 AS ok"); return { ok: !!(r && r.ok), error: r && r.error }; } };
}

module.exports = { connect, scram, query, queryP, adapter, parseConn, normalizeConn, parseMessages, parseRowDescription, parseDataRow, parseError, startupPacket, md5, fe, int32, cstr, wantsSsl, mustSsl, sslMode, __setTransport };
