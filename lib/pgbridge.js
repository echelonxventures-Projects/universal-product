"use strict";
const { Worker } = require("node:worker_threads");
const path = require("path");

const DATA_BYTES = 16 * 1024 * 1024;

function open(url, opts) {
  opts = opts || {};
  const timeoutMs = opts.timeoutMs || 30000;
  const ctrlSab = new SharedArrayBuffer(16);
  const dataSab = new SharedArrayBuffer(DATA_BYTES);
  const ctrl = new Int32Array(ctrlSab);
  const worker = new Worker(path.join(__dirname, "pgworker.js"), { workerData: { url, ctrl: ctrlSab, data: dataSab } });

  let fatal = null, closed = false, seq = 0;
  worker.on("error", e => { fatal = e; Atomics.store(ctrl, 0, -1); Atomics.notify(ctrl, 0); });
  worker.on("exit", () => { closed = true; if (!fatal) fatal = new Error("pg bridge: worker exited"); Atomics.store(ctrl, 0, -1); Atomics.notify(ctrl, 0); });

  function call(payload) {
    if (fatal) throw fatal;
    /* M4: stamp every request with a monotonic id and echo it back. A late reply from a TIMED
       OUT request used to satisfy the next Atomics.wait and return the PREVIOUS query's result;
       now a mismatched id is detected and rejected instead of silently mis-paired. */
    const id = ++seq;
    Atomics.store(ctrl, 0, 0);
    worker.postMessage({ ...payload, id });
    const res = Atomics.wait(ctrl, 0, 0, timeoutMs);
    if (res === "timed-out") throw new Error("pg bridge: query timeout after " + timeoutMs + "ms");
    if (res === "not-equal") throw new Error("pg bridge: reply arrived for a different request");
    if (Atomics.load(ctrl, 0) === -1) throw (fatal || new Error("pg bridge: worker error"));
    const len = Atomics.load(ctrl, 1);
    const out = JSON.parse(Buffer.from(dataSab, 4, len).toString("utf8"));
    if (out.error) throw new Error(out.error);
    if (out.id != null && out.id !== id) throw new Error("pg bridge: stale reply " + out.id + " for request " + id);
    return out;
  }

  function zip(columns, rows) { return rows.map(r => { const o = {}; for (let i = 0; i < columns.length; i++) o[columns[i]] = r[i]; return o; }); }
  function tagCount(tag) { const m = /(\d+)\s*$/.exec(String(tag || "")); return m ? Number(m[1]) : 0; }

  const idCache = new Map();
  /* the column an INSERT's new row id comes from: the table's id, else the rowid column the
     migration gives a table that had SQLite's implicit rowid (lib/migrate.js) */
  function idColumn(t) {
    if (idCache.has(t)) return idCache.get(t);
    let v = null;
    /* L2: scope the probe to the current schema, or a same-named table in another schema
       yields a false positive and a spurious RETURNING id on a composite-PK table. */
    try { const r = call({ sql: "SELECT column_name FROM information_schema.columns WHERE table_name=? AND table_schema = current_schema() AND column_name IN ('id','rowid') ORDER BY column_name", params: [t] }); v = r.rows.length ? r.rows[0][0] : null; } catch (e) { v = null; }
    idCache.set(t, v); return v;
  }
  const tableHasId = t => !!idColumn(t);

  function all(sqlText, ...args) { const r = call({ sql: String(sqlText), params: args }); return zip(r.columns, r.rows); }
  function get(sqlText, ...args) { return all(sqlText, ...args)[0]; }
  function run(sqlText, ...args) {
    let s = String(sqlText), wantId = false;
    const m = /^\s*insert\s+into\s+"?(\w+)"?/i.exec(s);
    const idc = m && !/\breturning\b/i.test(s) && !/;\s*\S/.test(s) ? idColumn(m[1]) : null;
    if (idc) { s = s.replace(/;\s*$/, "") + ' RETURNING "' + idc + '"'; wantId = true; }
    /* an INSERT that skips a conflicting row (OR IGNORE, ON CONFLICT DO NOTHING) inserts nothing */
    const mayInsertNothing = /^\s*insert\s+or\s+ignore\b/i.test(s) || /\bon\s+conflict\b[^;]*\bdo\s+nothing\b/i.test(s);
    const r = call({ sql: s, params: args });
    const out = { changes: tagCount(r.cmdTag), lastInsertRowid: null };
    /* L1: RETURNING id was appended because the table HAS an id column, so a missing value means
       the row did not insert — returning null here would let ~30 Number(null) call sites read 0
       and write a wrong foreign key. Surface it instead of silently degrading. */
    if (wantId) {
      if (r.rows && r.rows[0]) out.lastInsertRowid = r.rows[0][0];
      else if (!mayInsertNothing) throw new Error("pg bridge: INSERT into \"" + m[1] + "\" returned no id (row not inserted)");
    }
    return out;
  }
  function exec(script) { call({ kind: "exec", sql: String(script) }); }
  function prepare(sqlText) { return { run: (...a) => run(sqlText, ...a), get: (...a) => get(sqlText, ...a), all: (...a) => all(sqlText, ...a) }; }

  async function ping() { try { const r = call({ sql: "SELECT 1 AS ok", params: [] }); return { ok: r.rows.length === 1 }; } catch (e) { return { ok: false, error: e.message }; } }
  function close() { try { worker.postMessage({ kind: "close" }); } catch (e) { } try { worker.terminate(); } catch (e) { } }

  return { url, call, all, get, run, exec, prepare, ping, close, tableHasId };
}

module.exports = { open, DATA_BYTES };