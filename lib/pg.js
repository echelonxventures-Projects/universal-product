/* LUXORA Platform — minimal Postgres wire client (zero dependencies).
   Frontend/backend protocol: StartupMessage + (trust | cleartext | MD5) auth + simple Query,
   parsing RowDescription/DataRow/CommandComplete/ReadyForQuery/ErrorResponse. Selected via
   config `db=postgres`; the app's synchronous data layer (lib/db.js) stays SQLite by design, so
   this powers the async surfaces (workers, exports, reporting, future async handlers) — a full
   sync→async app migration on Postgres is the remaining, separately-scoped step (see README).
   Pure encode/parse helpers are exported and unit-tested without a live server. SCRAM-SHA-256 is
   intentionally NOT half-implemented: if a server demands it, ping() reports "auth unsupported". */
"use strict";
const crypto = require("crypto"); const net = require("net");

let TR = { connect: (o) => net.connect(o) };
function __setTransport(t) { TR = Object.assign({}, TR, t || {}); }

function cstr(s) { return Buffer.from(String(s) + "\0", "utf8"); }
function int32(n) { const b = Buffer.alloc(4); b.writeInt32BE(n | 0, 0); return b; }
function fe(type, body) { const b = Buffer.from(body); return Buffer.concat([Buffer.from(type, "ascii"), int32(4 + b.length), b]); }
function cstring(buf, off) { let e = off; while (e < buf.length && buf[e] !== 0) e++; return { s: buf.toString("utf8", off, e), next: e + 1 }; }
function md5(user, password, salt) { const a = crypto.createHash("md5").update(String(password) + user).digest("hex"); return "md5" + crypto.createHash("md5").update(Buffer.concat([Buffer.from(a, "hex"), salt])).digest("hex"); }

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
function parseRowDescription(body) { const n = body.readInt16BE(0); let p = 2; const cols = []; for (let i = 0; i < n; i++) { const nm = cstring(body, p); p = nm.next + 18; cols.push(nm.s); } return cols; }
function parseDataRow(body) { const n = body.readInt16BE(0); let p = 2; const vals = []; for (let i = 0; i < n; i++) { const l = body.readInt32BE(p); p += 4; if (l === -1) vals.push(null); else { vals.push(body.toString("utf8", p, p + l)); p += l; } } return vals; }
function parseError(body) { let p = 0, err = {}; while (p < body.length && body[p] !== 0) { const f = String.fromCharCode(body[p]); p++; const r = cstring(body, p); err[f] = r.s; p = r.next; } return err; }

function parseConn(url) { try { const x = new URL(url.replace(/^postgres(ql)?:/, "http:")); return { host: x.hostname || "127.0.0.1", port: Number(x.port) || 5432, user: decodeURIComponent(x.username || "postgres"), password: decodeURIComponent(x.password || ""), database: decodeURIComponent((x.pathname || "/").slice(1)) || "postgres" }; } catch (e) { return null; } }

function query(cfg, sql, { timeoutMs = 8000 } = {}) {
  const conn = typeof cfg === "string" ? parseConn(cfg) : cfg;
  if (!conn) return Promise.resolve({ error: "invalid postgres connection" });
  return new Promise(resolve => {
    let sock; try { sock = TR.connect({ host: conn.host, port: conn.port }); } catch (e) { return resolve({ error: e.message }); }
    let buf = Buffer.alloc(0), columns = [], rows = [], cmdTag = "", done = false, sentQuery = false;
    const finish = v => { if (!done) { done = true; clearTimeout(to); try { sock.write(fe("X", Buffer.alloc(0))); } catch (e) { } try { sock.destroy(); } catch (e) { } resolve(v); } };
    const to = setTimeout(() => finish({ error: "timeout" }), timeoutMs);
    sock.on("error", e => finish({ error: e.message }));
    sock.write(startupPacket(conn.user, conn.database));
    sock.on("data", d => {
      buf = Buffer.concat([buf, d]); const { messages, rest } = parseMessages(buf); buf = rest;
      for (const m of messages) {
        if (m.type === "R") { const code = m.body.readInt32BE(0);
          if (code === 0) continue; // AuthenticationOk
          if (code === 3) { sock.write(fe("p", cstr(conn.password || ""))); continue; } // cleartext
          if (code === 5) { sock.write(fe("p", cstr(md5(conn.user, conn.password || "", m.body.slice(4, 8))))); continue; } // MD5
          return finish({ error: "auth method " + code + " not supported (needs SCRAM/GSS) — configure a trust/md5/cleartext role for LUXORA" }); }
        if (m.type === "E") { const err = parseError(m.body); return finish({ error: err.M || "postgres error", code: err.C, severity: err.S }); }
        if (m.type === "t") { columns = parseRowDescription(m.body); }
        if (m.type === "d") { rows.push(parseDataRow(m.body)); }
        if (m.type === "C") { cmdTag = m.body.toString("utf8").replace(/\0.*$/, ""); }
        if (m.type === "N") { continue; } // NoticeResponse — ignore
        if (m.type === "Z") { if (!sentQuery) { sentQuery = true; sock.write(fe("Q", Buffer.from(String(sql) + "\0", "utf8"))); continue; } return finish({ ok: true, columns, rows, cmdTag }); }
      }
    });
  });
}

/* ---- extended query with parameters ($1..$n), text format ---- */
function queryP(cfgObj, sqlText, params, opts) {
  params = params || []; const conn = typeof cfgObj === "string" ? parseConn(cfgObj) : cfgObj;
  if (!conn) return Promise.resolve({ error: "invalid postgres connection" });
  opts = opts || {};
  return new Promise(resolve => {
    let sock; try { sock = TR.connect({ host: conn.host, port: conn.port }); } catch (e) { return resolve({ error: e.message }); }
    let buf = Buffer.alloc(0), columns = [], rows = [], cmdTag = "", done = false, authPhase = 0;
    const send = m => sock.write(m);
    const ci32 = n => { const b = Buffer.alloc(4); b.writeInt32BE(n, 0); return b; };
    const msg = (type, body) => Buffer.concat([Buffer.from(type, "ascii"), ci32(4 + body.length), body]);
    const cstr2 = s => Buffer.concat([Buffer.from(String(s), "utf8"), Buffer.from("\0")]);
    function frame() {
      const i16 = n => { const b = Buffer.alloc(2); b.writeInt16BE(n, 0); return b; };
      const parse = msg("P", Buffer.concat([cstr2(""), cstr2(sqlText), ci32(params.length), ...params.map(() => ci32(0))]));
      const fmt = Buffer.concat([i16(params.length), ...params.map(() => i16(0))]); // param format codes: all text
      const values = Buffer.concat([i16(params.length), ...params.map(p => { if (p == null) { const n = Buffer.alloc(4); n.writeInt32BE(-1, 0); return n; } const s = String(p); const l = Buffer.alloc(4); l.writeInt32BE(Buffer.byteLength(s), 0); return Buffer.concat([l, Buffer.from(s, "utf8")]); })]);
      const resultFmt = i16(0); // no result format codes => text
      const bind = msg("B", Buffer.concat([cstr2(""), cstr2(""), fmt, values, resultFmt]));
      const desc = msg("D", Buffer.concat([Buffer.from("S"), cstr2("")]));
      const exec = msg("E", Buffer.concat([cstr2(""), ci32(0)]));
      const sync = msg("S", Buffer.alloc(0));
      send(Buffer.concat([parse, bind, desc, exec, sync]));
    }
    const finish = v => { if (!done) { done = true; clearTimeout(to); try { send(msg("X", Buffer.alloc(0))); } catch (e) { } try { sock.destroy(); } catch (e) { } resolve(v); } };
    const to = setTimeout(() => finish({ error: "timeout" }), opts.timeoutMs || 8000);
    sock.on("error", e => finish({ error: e.message }));
    sock.write(startupPacket(conn.user, conn.database));
    sock.on("data", d => {
      buf = Buffer.concat([buf, d]); const { messages, rest } = parseMessages(buf); buf = rest;
      for (const m of messages) {
        if (m.type === "R") { const code = m.body.readInt32BE(0); if (code === 0) continue; if (code === 3) { send(msg("p", cstr(conn.password || ""))); continue; } if (code === 5) { send(msg("p", cstr(md5(conn.user, conn.password || "", m.body.slice(4, 8))))); continue; } return finish({ error: "auth method " + code + " unsupported" }); }
        if (m.type === "K" || m.type === "S" || m.type === "N") continue;
        if (m.type === "E") { const err = parseError(m.body); return finish({ error: err.M || "postgres error", code: err.C }); }
        if (m.type === "t") columns = parseRowDescription(m.body);
        if (m.type === "d") rows.push(parseDataRow(m.body));
        if (m.type === "C") cmdTag = m.body.toString("utf8").replace(/\0.*$/, "");
        if (m.type === "Z") { if (authPhase === 0) { authPhase = 1; frame(); continue; } return finish({ ok: true, columns, rows, cmdTag }); }
      }
    });
  });
}

function adapter(params) {
  const url = (params && (params.url || params.connString)) || process.env.LX_PG_URL;
  if (!url) return { kind: "postgres", configured: false, async ping() { return { ok: false, error: "postgres not configured (set LX_PG_URL or runtime.db.params.url)" }; }, query: () => Promise.resolve({ error: "not configured" }) };
  return { kind: "postgres", configured: true, query: (sql) => query(url, sql), async ping() { const r = await query(url, "SELECT 1 AS ok"); return { ok: !!(r && r.ok), error: r && r.error }; } };
}

module.exports = { query, queryP, adapter, parseConn, parseMessages, parseRowDescription, parseDataRow, parseError, startupPacket, md5, fe, int32, cstr, __setTransport };
