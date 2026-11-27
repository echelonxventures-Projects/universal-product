/* The ERP gaps: leave (lib/leave.js) — balances, overlap, approval by someone else, attendance that
   payroll reads, cancellation, capacity off the resource plan; fixed assets (lib/assets.js) — bought
   onto the books, depreciated month by month once, straight line and declining balance, sold with a
   gain; budgets (lib/budgets.js) — a year per account, approved once, against the books; material
   requirements planning (lib/mrp.js) — bills of materials without cycles, netting level by level,
   lead times and lateness, turned once into purchase orders and work orders. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os");
const TMP = path.join(os.tmpdir(), "erp-" + process.pid + ".db");
const wipe = () => { for (const s of ["", "-wal", "-shm"]) try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } };
wipe(); process.env.LX_DB = TMP;
const log = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = log;
const K = require("../lib/kernel.js"), RR = require("../lib/row-records.js"), O = require("../lib/operations.js"), B = require("../lib/books.js");
const L = require("../lib/leave.js"), FA = require("../lib/assets.js"), BU = require("../lib/budgets.js"), MRP = require("../lib/mrp.js"), CS = require("../lib/consulting.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x).slice(0, 500) : ""))); };
const throws = (fn, re) => { try { fn(); return false; } catch (e) { return re.test(e.message) || (console.log("    (threw: " + e.message + ")"), false); } };
const today = () => new Date().toISOString().slice(0, 10);
const addDays = (d, n) => { const x = new Date(d + "T00:00:00Z"); x.setUTCDate(x.getUTCDate() + n); return x.toISOString().slice(0, 10); };
const month = (d, n) => { const x = new Date(d.slice(0, 7) + "-01T00:00:00Z"); x.setUTCMonth(x.getUTCMonth() + n); return x.toISOString().slice(0, 7); };
try {
  const t = 1, cur = require("../lib/defaults.js").currency(t);
  const bal = code => { const tb = B.trialBalance(t).find(x => x.currency === cur); const r = tb && tb.rows.find(x => x.account === code); return r ? r.balance : 0; };
  const Y = Number(today().slice(0, 4)) + 1;

  console.log("▸ LEAVE");
  const ana = O.upsertEmployee(t, { code: "L-ANA", name: "Ana Leave", email: "ana@erp.example" });
  const mon = (() => { let d = `${Y}-03-01`; while (new Date(d + "T00:00:00Z").getUTCDay() !== 1) d = addDays(d, 1); return d; })();
  const b0 = L.balance(t, ana.id, Y).find(x => x.type === "annual");
  ok(b0.entitled === 20 && b0.carried === 5 && b0.left === 25, "a year's annual leave, with what is left of last year carried in", b0);
  const r1 = L.request(t, { employee_id: ana.id, type: "annual", from_date: mon, to_date: addDays(mon, 6), reason: "Family visit" }, "ana@erp.example");
  ok(r1.days === 5 && r1.status === "submitted" && K.internal.nodeRow(r1.uid).kind === "operations.leave_request", "a week off counts its five working days, and is on the master", r1);
  ok(!db.all("SELECT attrs FROM k_versions WHERE node=?", r1.uid).some(v => /Family/.test(v.attrs)), "why it was asked for stays in the table");
  ok(L.balance(t, ana.id, Y).find(x => x.type === "annual").left === 20, "waiting for approval, it already comes off what is left");
  ok(throws(() => L.request(t, { employee_id: ana.id, type: "sick", from_date: addDays(mon, 2) }), /overlaps/), "leave that overlaps is refused");
  ok(throws(() => L.request(t, { employee_id: ana.id, type: "annual", from_date: addDays(mon, 5), to_date: addDays(mon, 6) }), /no working days|overlaps/), "a weekend holds no working days");
  ok(throws(() => L.approve(t, r1.id, "ana@erp.example"), /Someone other/), "nobody approves their own leave");
  L.approve(t, r1.id, "boss@erp.example", "Enjoy");
  const att = db.all("SELECT date, status FROM attendance WHERE tenant_id=? AND employee_id=? ORDER BY date", t, ana.id);
  ok(att.length === 5 && att.every(a => a.status === "leave"), "approved: each working day shows as paid leave in attendance, which payroll pays", att);
  const half = L.request(t, { employee_id: ana.id, type: "unpaid", from_date: addDays(mon, 7), half_day: true }, "ana@erp.example");
  L.approve(t, half.id, "boss@erp.example");
  ok(half.days === 0.5 && db.get("SELECT status FROM attendance WHERE employee_id=? AND date=?", ana.id, addDays(mon, 7)).status === "absent", "unpaid leave shows as absent, so payroll deducts it; half a day is half");
  const left = L.balance(t, ana.id, Y).find(x => x.type === "annual").left;
  let end = addDays(mon, 14), n = 0; const start = end;
  for (let d = start; n <= left; d = addDays(d, 1)) { if (L.daysIn(t, d, d).length) n++; end = d; }
  ok(throws(() => L.request(t, { employee_id: ana.id, type: "annual", from_date: start, to_date: end }), /days of annual leave are left/), "a request for more than is left is refused");
  L.setAllowance(t, ana.id, Y, "annual", 40);
  const big = L.request(t, { employee_id: ana.id, type: "annual", from_date: start, to_date: end });
  ok(big.days === left + 1, "a person's own allowance for a year raises what they may take");
  ok(L.cancel(t, big.id).status === "cancelled", "a request not yet decided is withdrawn");
  /* capacity: the week off leaves nothing to book */
  CS.setPerson(t, ana.id, { capacity_hours: 40 });
  const proj = O.upsertProject(t, { name: "Leave-aware project", status: "active" });
  const bk = CS.allocate(t, { employee_id: ana.id, project_id: proj.id, week: mon, hours: 8 });
  ok(bk.capacity === 0 && bk.over, "the resource plan takes approved leave off the week's capacity", bk);
  ok(L.hoursOff(t, ana.id, addDays(mon, 7), addDays(mon, 7), 40) === 4, "half a day off is half a day's hours");
  L.cancel(t, r1.id);
  ok(db.get("SELECT COUNT(*) n FROM attendance WHERE employee_id=? AND status='leave'", ana.id).n === 0 && L.balance(t, ana.id, Y).find(x => x.type === "annual").taken === 0, "approved leave not yet started is cancelled: its days come back and attendance is cleared");
  ok(L.calendar(t, addDays(mon, 7), addDays(mon, 7))[0].away.length === 1, "the calendar shows who is away each day");

  console.log("▸ FIXED ASSETS AND DEPRECIATION");
  const fa0 = bal("1500"), bank0 = bal("1000"), dep0 = bal("6600");
  const lap = FA.register(t, { name: "Laptops for the studio", category: "it", cost: 3600, acquired_on: "2026-01-15", serial: "SN-1" }, "fin@erp.example");
  ok(lap.life_months === 36 && lap.in_service === "2026-01" && lap.method === "straight_line" && K.internal.nodeRow(lap.uid).kind === "value.fixed_asset", "an asset takes its category's life, comes into service in its month, and is on the master", lap);
  ok(bal("1500") - fa0 === 3600 && bank0 - bal("1000") === 3600, "bought: its cost is on the books, paid from the bank");
  ok(throws(() => FA.register(t, { name: "x", category: "it", cost: 100, residual: 100 }), /residual/), "the residual value is below the cost");
  ok(throws(() => FA.depreciate(t, month(today(), 2)), /once it has begun/), "a month to come is not depreciated");
  const d1 = FA.depreciate(t, "2026-10");
  ok(d1.months === 10 && FA.view(t, lap.id).accumulated === 1000 && +(bal("6600") - dep0).toFixed(2) === 1000 && bal("1510") === -1000, "ten months straight line: 100 a month, the expense and the depreciation to date on the books", { d1, a: FA.view(t, lap.id) });
  ok(FA.depreciate(t, "2026-10").months === 0, "a month is posted once");
  const van = FA.register(t, { name: "Delivery van", category: "vehicles", cost: 10000, residual: 1000, method: "declining_balance", acquired_on: "2026-06-01" });
  const sch = FA.schedule(t, van.id);
  ok(sch[0].amount === 333.33 && sch.length <= 60 && sch[sch.length - 1].book === 1000 && +sch.reduce((s, x) => s + x.amount, 0).toFixed(2) === 9000, "declining balance: a fixed share of what is left, ending exactly at the residual value", { first: sch[0], last: sch[sch.length - 1], n: sch.length });
  const swept = FA.sweepAll();
  ok(swept >= 5 && FA.view(t, van.id).last_period === month(today(), -1), "when a month ends, the sweep posts every month not yet posted", { swept, v: FA.view(t, van.id) });
  ok(throws(() => FA.dispose(t, lap.id, { proceeds: 3000 }), /Say why/), "selling an asset says why");
  const gain0 = bal("4950");
  const sold = FA.dispose(t, lap.id, { date: today(), proceeds: 3000, reason: "Replaced by new machines" });
  const months = 1 + (Number(today().slice(0, 4)) - 2026) * 12 + Number(today().slice(5, 7)) - 1;
  ok(sold.status === "disposed" && sold.accumulated === r(months * 100) && sold.gain === r(3000 - (3600 - months * 100)) && r(bal("4950") - gain0) === sold.gain, "sold: depreciated to the month it went, the gain or loss posted", sold);
  ok(throws(() => FA.dispose(t, lap.id, { reason: "again" }), /already gone/), "an asset goes once");
  ok(FA.totals(t).some(x => x.category === "vehicles" && x.book < 10000), "the register totals cost, depreciation and book value by category");

  console.log("▸ BUDGETS");
  const yr = Number(today().slice(0, 4)), m = Number(today().slice(5, 7));
  const bud = BU.create(t, { name: "Operating budget", year: yr }, "fin@erp.example");
  ok(throws(() => BU.setLines(t, bud.id, [{ account: "1000", annual: 100 }]), /income and expense accounts/), "a budget plans income and expense accounts only");
  BU.setLines(t, bud.id, [{ account: "6500", month: m, amount: 200 }, { account: "4300", month: m, amount: 5000 }, { account: "6400", annual: 1000 }]);
  const v = BU.view(t, bud.id);
  ok(v.total === 6200 && v.lines.find(l => l.account === "6400").months[12] === 83.37 && K.internal.nodeRow(v.uid).kind === "value.budget", "a year's amount is spread evenly, the remainder in the last month; on the master", v.lines.find(l => l.account === "6400"));
  BU.approve(t, bud.id, "boss@erp.example");
  const bud2 = BU.create(t, { name: "Second", year: yr }); BU.setLines(t, bud2.id, [{ account: "6500", annual: 10 }]);
  ok(throws(() => BU.approve(t, bud2.id), /already the approved budget/), "one approved budget per year and currency");
  ok(throws(() => BU.setLines(t, bud.id, [{ account: "6500", annual: 1 }]), /Only a draft/), "an approved budget is changed only after it is reopened");
  B.manual(t, { currency: cur, memo: "Team offsite", lines: [{ account: "6500", debit: 300 }, { account: "1000", credit: 300 }] }, "fin");
  const rep = BU.report(t, bud.id, { through: m });
  const s65 = rep.rows.find(x => x.account === "6500"), s43 = rep.rows.find(x => x.account === "4300"), s66 = rep.rows.find(x => x.account === "6600");
  ok(s65.budget === 200 && s65.actual === 300 && s65.off && s65.usedPct === 150, "an expense over budget to date is flagged", s65);
  ok(s43.income && s43.off && s43.actual < s43.budget, "income below budget is flagged");
  ok(s66 && !s66.budgeted && s66.off, "spending on an account with no budget is shown", s66);
  const next = BU.create(t, { name: "Next year", year: yr + 1 });
  const filled = BU.fromActuals(t, next.id, { year: yr, uplift_pct: 10 });
  ok(filled.lines.find(l => l.account === "6500").months[m] === 330, "a draft starts from a year's actuals, with an uplift", filled.lines.find(l => l.account === "6500"));

  console.log("▸ MATERIAL REQUIREMENTS PLANNING");
  const items = db.all("SELECT p.id, (SELECT id FROM skus k WHERE k.tenant_id=p.tenant_id AND k.product_id=p.id) sku FROM products p WHERE p.tenant_id=? AND p.type='physical' AND p.deleted_at IS NULL AND (SELECT COUNT(*) FROM skus k WHERE k.tenant_id=p.tenant_id AND k.product_id=p.id)=1 ORDER BY p.id LIMIT 4", t);
  const [FG, C1, SUB, C2] = items;
  const setStock = (p, n) => { db.run("UPDATE products SET stock=? WHERE tenant_id=? AND id=?", n, t, p.id); db.run("UPDATE skus SET stock=? WHERE id=?", n, p.sku); };
  setStock(FG, 5); setStock(C1, 30); setStock(SUB, 0); setStock(C2, 0);
  const sup = db.get("SELECT id FROM suppliers WHERE tenant_id=? ORDER BY id LIMIT 1", t);
  for (const [p, lead, price, moq] of [[C1, 10, 2, 50], [C2, 3, 1.5, 1]]) db.run("INSERT INTO product_suppliers(tenant_id, product_id, supplier_id, price, lead_days, moq, is_primary) VALUES(?,?,?,?,?,?,1) ON CONFLICT(tenant_id, product_id, supplier_id) DO UPDATE SET price=excluded.price, lead_days=excluded.lead_days, moq=excluded.moq, is_primary=1", t, p.id, sup.id, price, lead, moq);
  db.run("DELETE FROM product_suppliers WHERE tenant_id=? AND product_id IN (?,?,?,?) AND supplier_id<>?", t, FG.id, C1.id, SUB.id, C2.id, sup.id);
  MRP.setBom(t, FG.id, [{ component_id: C1.id, qty: 2 }, { component_id: SUB.id, qty: 1 }]);
  MRP.setBom(t, SUB.id, [{ component_id: C2.id, qty: 3 }]);
  ok(throws(() => MRP.setBom(t, C2.id, [{ component_id: FG.id, qty: 1 }]), /circle/), "a bill of materials never goes round in a circle");
  ok(MRP.bom(t, FG.id).components.find(c => c.component_id === SUB.id).components[0].component_id === C2.id, "a component has its own bill beneath it");
  MRP.setItem(t, C2.id, { lead_days: 30, safety_stock: 5 });
  const due = addDays(today(), 20);
  MRP.addDemand(t, { product_id: FG.id, qty: 25, due_date: due }, "plan@erp.example");
  const res = MRP.run(t, {}, "plan@erp.example"), S = id => res.suggestions.find(x => x.product_id === id);
  ok(S(FG.id).action === "make" && S(FG.id).qty === 20 && S(FG.id).order_by === addDays(due, -3), "the finished item: 25 needed less 5 on the shelf, made, started its lead time before it is due", S(FG.id));
  ok(S(SUB.id).action === "make" && S(SUB.id).qty === 20 && S(SUB.id).need_by === addDays(due, -3), "a made component is needed when the item using it starts", S(SUB.id));
  ok(S(C1.id).action === "buy" && S(C1.id).qty === 50 && S(C1.id).gross === 40 && S(C1.id).order_by === addDays(due, -13), "a bought component: 40 needed less 30 in stock, raised to the supplier's smallest order, ordered its lead time ahead", S(C1.id));
  ok(S(C2.id).qty === 65 && S(C2.id).late === 1, "level by level: 60 for the sub-assembly plus safety stock; its lead time makes it late already", S(C2.id));
  const conv = MRP.convert(t, {}, "plan@erp.example");
  const po = db.get("SELECT * FROM purchase_orders WHERE ref=?", conv.made.find(x => x.kind === "buy").ref);
  ok(conv.made.filter(x => x.kind === "buy").length === 1 && db.all("SELECT * FROM purchase_order_lines WHERE po_id=?", po.id).length === 2 && conv.made.filter(x => x.kind === "make").length === 2, "turned into one draft purchase order for the supplier and two planned work orders", conv.made);
  const wo = db.get("SELECT * FROM work_orders WHERE ref=?", conv.made.find(x => x.kind === "make").ref);
  ok(wo && wo.planned_start && Object.keys(JSON.parse(wo.bom)).length >= 1, "a work order carries its components, to consume when it is completed", wo);
  ok(throws(() => MRP.convert(t, {}), /Nothing to act on|already been acted/), "each suggestion is acted on once");
  const again = MRP.run(t, {});
  ok(again.suggestions.length === 0, "the next run counts what the orders will bring: nothing more is needed", again.suggestions);
  db.run("DELETE FROM product_suppliers WHERE tenant_id=? AND product_id=?", t, C1.id);
  MRP.addDemand(t, { product_id: C1.id, qty: 500, due_date: due });
  const third = MRP.run(t, {});
  ok(throws(() => MRP.convert(t, { ids: third.suggestions.map(s => s.id) }), /No supplier/), "an item with no supplier is not ordered blind");

  console.log("▸ THE BOOKS STAY WHOLE");
  const h = B.health(t);
  ok(!h.missing.length && !h.unbalanced.length, "every entry balances", h);
} catch (e) { failed++; console.log("  ✗ threw: " + e.stack); }
console.log(`\n${passed} passed, ${failed} failed`);
wipe();
process.exit(failed ? 1 : 0);
function r(n) { return +Number(n).toFixed(2); }
