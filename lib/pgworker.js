"use strict";
const { parentPort, workerData } = require("node:worker_threads");
const pg = require("./pg.js");
const sql = require("./sql.js");

const ctrl = new Int32Array(workerData.ctrl);
const data = new Uint8Array(workerData.data);
const dv = new DataView(workerData.data);

const NUM_OIDS = new Set([20, 21, 23, 26, 700, 701, 790, 1700]);
const BOOL_OIDS = new Set([16]);
function coerce(rows, oids) {
  if (!oids || !oids.length) return rows;
  return rows.map(r => r.map((v, i) => {
    if (v === null || v === undefined) return v;
    const oid = oids[i];
    if (NUM_OIDS.has(oid)) { const n = Number(v); return Number.isNaN(n) ? v : n; }
    if (BOOL_OIDS.has(oid)) return v === "t" ? 1 : 0;
    return v;
  }));
}

function reply(obj) {
  let json = Buffer.from(JSON.stringify(obj), "utf8");
  if (json.length + 4 > data.length) json = Buffer.from(JSON.stringify({ error: "pg bridge: result exceeds shared buffer", id: obj.id }));
  dv.setUint32(0, json.length, true);
  data.set(json, 4);
  Atomics.store(ctrl, 1, json.length);
  Atomics.store(ctrl, 0, 1);
  Atomics.notify(ctrl, 0);
}

/* one connection for the life of the worker: the bridge sends one statement at a time, so a
   transaction's BEGIN, its statements and its COMMIT all travel on it (lib/pg.js connect). A
   connection lost inside a transaction leaves that transaction broken: every statement is refused
   until the caller's ROLLBACK, so nothing of it can commit on a fresh connection. */
let conn = null, broken = false;
async function connection(t) {
  if (conn && !conn.dead) return conn;
  if (conn && conn.dead && conn.status !== "I") broken = true;
  conn = await pg.connect(workerData.url, { timeoutMs: t });
  return conn;
}
parentPort.on("message", async msg => {
  try {
    let r;
    /* M4: honour the caller's timeout (the bridge passes its own; the old hardcoded 60000
       guaranteed the two would disagree). */
    const t = Number(msg.timeoutMs) || 30000;
    const text = msg.kind === "exec" ? msg.sql : sql.toPg(msg.sql);
    const c = await connection(t);
    if (broken) {
      if (/^\s*ROLLBACK\b/i.test(text)) { broken = false; return reply({ ok: true, rows: [], columns: [], cmdTag: "ROLLBACK", id: msg.id }); }
      return reply({ error: "postgres connection was lost inside a transaction; it was rolled back — roll back and retry", id: msg.id });
    }
    r = msg.kind === "exec" ? await c.simple(text, { timeoutMs: t }) : await c.query(text, msg.params || [], { timeoutMs: t });
    if (r && r.error) return reply({ error: r.error, id: msg.id });
    reply({ ok: true, rows: coerce((r && r.rows) || [], r && r.oids), columns: (r && r.columns) || [], cmdTag: (r && r.cmdTag) || "", id: msg.id });
  } catch (e) { reply({ error: e.message, id: msg.id }); }
});