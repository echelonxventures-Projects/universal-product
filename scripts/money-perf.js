/* LUXORA Platform — how long migration money-0001 takes on a database of a given size (PR-016).
   Builds a throwaway database in the shape an install from before the migration has (a fresh
   boot, then its money columns, guard and money tables removed), fills it with N synthetic orders
   (two lines each), N payments and N/4 invoices in four currencies — mostly exact amounts, some
   float residue, some with more decimals than the currency, on purpose — then boots the platform
   on it in a child process and reports the migration's own timing, the peak memory and the
   result. Usage: node scripts/money-perf.js [N=200000] [--keep]. Never touches data/. */
"use strict";
const fs = require("fs"), os = require("os"), path = require("path");
const { spawnSync } = require("child_process");
const ROOT = path.join(__dirname, "..");
const N = Number(process.argv[2]) > 0 ? Number(process.argv[2]) : 200000;
const DIR = fs.mkdtempSync(path.join(os.tmpdir(), "money-perf-")), DB = path.join(DIR, "perf.db");
const env = { ...process.env, LX_TEST: "1", LX_DB: DB };
const first = spawnSync(process.execPath, ["-e", "require('./lib/db.js')"], { cwd: ROOT, env, encoding: "utf8" });
if (first.status !== 0) { console.error(first.stderr); process.exit(1); }
const { DatabaseSync } = require("node:sqlite");
const SPEC = require("../lib/seed/money.json").store;
const D = new DatabaseSync(DB);
for (const t of D.prepare("SELECT name FROM sqlite_master WHERE type='trigger' AND name LIKE 'money%'").all()) D.exec("DROP TRIGGER " + t.name);
for (const t of SPEC.tables) for (const c of [...t.amounts.map(c => c + "_minor"), "money_scale", "money_state", ...(t.refunds ? ["refunded_minor"] : []), ...(t.addCurrency ? ["currency"] : [])]) D.exec(`ALTER TABLE ${t.table} DROP COLUMN ${c}`);
for (const t of ["money_migrations", "money_quarantine", "refunds"]) D.exec("DROP TABLE " + t);
let seed = 7; const rnd = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;
const tid = D.prepare("SELECT id FROM tenants ORDER BY id LIMIT 1").get().id;
const io = D.prepare("INSERT INTO orders(tenant_id,owner,num,sub,ship_fee,gift_used,tax,total,currency,status) VALUES(?,'perf',?,?,0,0,?,?,?, 'delivered')");
const ii = D.prepare("INSERT INTO order_items(order_id,product_id,qty,price) VALUES(?,?,1,?)");
const ip = D.prepare("INSERT INTO payments(tenant_id,kind,order_id,gateway,method,amount,currency,fee,status,txn_ref) VALUES(?,'order',?,'perf','card',?,?,?,'captured',?)");
const iv = D.prepare("INSERT INTO invoices(tenant_id,number,amount,currency,status) VALUES(?,?,?,?,'paid')");
const curs = ["USD", "USD", "USD", "EUR", "JPY", "KWD"];
D.exec("BEGIN");
for (let i = 0; i < N; i++) {
  const cur = curs[i % curs.length], d = cur === "JPY" ? 0 : cur === "KWD" ? 3 : 2;
  const a = Math.floor(rnd() * 1e6) / 10 ** d, b = Math.floor(rnd() * 1e5) / 10 ** d, tax = Math.floor(rnd() * 1e4) / 10 ** d;
  const sub = i % 50 === 0 ? a + b * 0.001 : a;
  const total = i % 7 === 0 ? sub + tax + 0.1 + 0.2 - 0.30000000000000004 : sub + tax;
  const id = Number(io.run(tid, "PERF-" + i, sub, tax, total, cur).lastInsertRowid);
  ii.run(id, "P" + (i % 97), a / 2); ii.run(id, "Q" + (i % 89), sub - a / 2);
  ip.run(tid, id, total, cur, Math.round(total * 2.9) / 100, "perf_" + i);
  if (i % 4 === 0) iv.run(tid, "PERF-INV-" + i, b, cur);
}
D.exec("COMMIT"); D.close();
const run = spawnSync(process.execPath, ["-e", `const t=Date.now();const l=console.log;console.log=()=>{};const d=require('./lib/db.js');console.log=l;
  const rep=JSON.parse(d.get("SELECT report FROM money_migrations").report);const t2=Date.now();const v=require('./lib/money-store.js').verify();
  console.log(JSON.stringify({bootMs:Date.now()-t,migrationMs:rep.ms,verifyMs:Date.now()-t2,verifyOk:v.ok,openQuarantine:v.openQuarantine,peakRssMb:Math.round(process.resourceUsage().maxRSS/1024),report:rep}))`], { cwd: ROOT, env, encoding: "utf8", maxBuffer: 1 << 26 });
const out = (run.stdout || "").trim().split("\n").pop();
console.log(JSON.stringify({ node: process.version, platform: process.platform + "-" + process.arch, orders: N, items: 2 * N, payments: N, invoices: Math.ceil(N / 4), ...JSON.parse(out || "{}") }, null, 1));
if (!process.argv.includes("--keep")) fs.rmSync(DIR, { recursive: true, force: true }); else console.log("kept " + DB);
process.exit(run.status || 0);
