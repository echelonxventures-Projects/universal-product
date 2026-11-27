/* Business records on the kernel through one engine (lib/row-records.js): invoices and support cases,
   alongside the returns and payments test/orders.js covers — each a node with its facts in time and
   what it belongs to, written in one transaction with its row, with no personal data copied. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os");
const TMP = path.join(os.tmpdir(), "row-records-" + process.pid + ".db");
const wipe = () => { for (const s of ["", "-wal", "-shm"]) try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } };
wipe(); process.env.LX_DB = TMP;
const log = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = log;
const K = require("../lib/kernel.js"), RR = require("../lib/row-records.js"), H = require("../lib/helpdesk.js"), B = require("../lib/billing.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x).slice(0, 300) : ""))); };
try {
  console.log("▸ DECLARED AS DATA");
  ok(["goods_receipt", "invoice", "payment", "purchase_order", "return", "supplier_bill", "ticket"].every(k => RR.SEED.records[k]) && Object.values(RR.SEED.records).every(r => r.table && r.kind && r.facts), "each table on the master is an entry of lib/seed/row-records.json", Object.keys(RR.SEED.records));
  for (const [name, sp] of Object.entries(RR.SEED.records)) {
    const rows = db.all(`SELECT id, uid, tenant_id FROM ${sp.table}`);
    ok(rows.every(r => K.internal.nodeRow(r.uid) && K.internal.nodeRow(r.uid).kind === sp.kind.kind && K.internal.nodeRow(r.uid).namespace === "tenant:" + r.tenant_id), `every ${name} row is a ${sp.kind.kind} in its store's namespace (${rows.length})`);
  }
  const seq = K.lastSeq(); ok(RR.importRows() === 0 && K.lastSeq() === seq, "a warm pass writes nothing");

  console.log("▸ SUPPORT CASES");
  const t1 = db.get("SELECT id FROM tenants ORDER BY id LIMIT 1").id;
  const u = db.get("SELECT id, uid FROM users WHERE tenant_id=? AND role='customer' ORDER BY id LIMIT 1", t1);
  const tk = H.openTicket(t1, { subject: "Where is my parcel, Priya?", reason: "delivery", priority: "high", name: "Priya Secret", email: "priya@secret.example", owner: `t${t1}:u:${u.id}`, body: "My flat is 4B" });
  const tid = tk.id || db.get("SELECT id FROM tickets WHERE owner_email='priya@secret.example'").id;
  H.transition(db, t1, tid, "open", "Agent A");
  H.transition(db, t1, tid, "resolved");
  H.rateCsat(t1, tid, 4, "fine");
  const rec = RR.at("ticket", tid);
  ok(rec && rec.priority === "high" && rec.status === "resolved" && rec.assignee === "Agent A" && rec.csat === 4, "a case is on the master with how it went", rec);
  ok(RR.history("ticket", tid, "status").map(h => h.value).join() === "new,open,resolved", "with its status history", RR.history("ticket", tid, "status"));
  ok(rec.belongsTo === u.uid && RR.of("ticket", u.uid).includes(rec.uid), "belonging to the person who raised it");
  ok(!db.all("SELECT attrs FROM k_versions WHERE node=?", rec.uid).some(v => /Priya|secret|4B|fine/.test(v.attrs)), "its subject, message, the customer's name, email and comment are not copied");
  const guest = H.openTicket(t1, { subject: "Hello", name: "Guest", email: "g@example.com" });
  ok(RR.at("ticket", guest.id || db.get("SELECT id FROM tickets WHERE owner_email='g@example.com'").id).belongsTo === null, "a guest's case belongs to no one");

  console.log("▸ INVOICES");
  const inv = B.issueInvoice(t1, { lines: [{ kind: "usage", description: "Test usage", qty: 1, unit_amount: 12.5, amount: 12.5 }], note: "test" });
  const iid = (inv && (inv.id || inv.invoice_id)) || db.get("SELECT id FROM invoices WHERE note='test' ORDER BY id DESC").id;
  const ir = db.get("SELECT * FROM invoices WHERE id=?", iid), ri = RR.at("invoice", iid);
  ok(ri && ri.number === ir.number && ri.amount === Number(ir.amount) && ri.status === ir.status, "an issued invoice is on the master", [ri, ir]);
  db.run("UPDATE invoices SET period_end=date('now','-20 days') WHERE id=?", iid);
  B.dunning(t1);
  const late = db.get("SELECT status FROM invoices WHERE id=?", iid).status;
  ok(RR.at("invoice", iid).status === late && RR.history("invoice", iid, "status").length >= 2, "and when it falls overdue, so does its record", [late, RR.history("invoice", iid, "status")]);

  console.log("▸ A WRITE THAT IS NOT RECORDED IS REFUSED");
  let threw = null; try { RR.change("invoice", iid, () => db); } catch (e) { threw = e.message; }
  ok(/wrap the statement/.test(threw || ""), "wrapping the database instead of the statement is refused", threw);
} catch (e) { failed++; console.log("  ✗ threw: " + e.stack); }
finally { wipe(); console.log(`\n${passed} passed, ${failed} failed`); process.exit(failed ? 1 : 0); }
