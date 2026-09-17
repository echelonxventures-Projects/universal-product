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
  if (json.length + 4 > data.length) json = Buffer.from(JSON.stringify({ error: "pg bridge: result exceeds shared buffer" }), "utf8");
  dv.setUint32(0, json.length, true);
  data.set(json, 4);
  Atomics.store(ctrl, 1, json.length);
  Atomics.store(ctrl, 0, 1);
  Atomics.notify(ctrl, 0);
}

parentPort.on("message", async msg => {
  try {
    let r;
    if (msg.kind === "exec") r = await pg.query(workerData.url, msg.sql, { timeoutMs: msg.timeoutMs || 60000 });
    else r = await pg.queryP(workerData.url, sql.toPg(msg.sql), msg.params || [], { timeoutMs: msg.timeoutMs || 60000 });
    if (r && r.error) return reply({ error: r.error });
    reply({ ok: true, rows: coerce((r && r.rows) || [], r && r.oids), columns: (r && r.columns) || [], cmdTag: (r && r.cmdTag) || "" });
  } catch (e) { reply({ error: e.message }); }
});