/* LUXORA Platform — material requirements planning (owner Commerce).

   What to make and buy, and by when. A finished item has a bill of materials (boms): the components
   one unit takes, with the share lost in making it; a component may have its own, to any depth,
   but never itself. Each item may set its lead time, safety stock and smallest lot (mrp_items).
   Demand is the master schedule — what must be ready by a date (mrp_demand) — and what open work
   orders still need of their components. A run takes items level by level, from the finished goods
   down: what is needed, plus the safety stock, less what is on the shelf (lib/stock.js) and what
   open purchase orders and work orders will bring, is the net requirement. An item with a bill of
   materials is made — a planned work order whose components become demand on the next level, due
   when it must start; an item without one is bought from its primary supplier. Each suggestion says
   when it must be ordered or started, from the lead time, and is late when that day has passed.
   Suggestions become draft purchase orders, one per supplier (lib/purchasing.js), or planned work
   orders (lib/operations.js); each is turned into one only once. A new run supersedes what the last
   one suggested and nobody acted on. Policy is data (lib/seed/mrp.json). */
"use strict";

const db = () => require("./db.js");
const K = require("./kernel.js");
const states = require("./states.js");
const SEED = require("./seed/mrp.json");
const MS = SEED.machines;
const fail = (msg, status, code) => { const e = new Error(msg); e.status = status || 400; if (code) e.code = code; throw e; };
const N = Number;
const r2 = n => +Number(n || 0).toFixed(2);
const str = (v, n) => String(v == null ? "" : v).trim().slice(0, n || 200);
const tx = fn => K.internal.tx(fn);
const ph = xs => "(" + (xs.length ? xs.map(() => "?").join(",") : "NULL") + ")";
const today = () => new Date().toISOString().slice(0, 10);
const isDate = d => /^\d{4}-\d{2}-\d{2}$/.test(String(d || "")) && !isNaN(Date.parse(d + "T00:00:00Z"));
const addDays = (d, n) => { const x = new Date(d + "T00:00:00Z"); x.setUTCDate(x.getUTCDate() + n); return x.toISOString().slice(0, 10); };
const product = (tid, id) => db().get("SELECT * FROM products WHERE tenant_id=? AND id=? AND deleted_at IS NULL", N(tid), String(id)) || fail("No such product: " + id, 404);
const [MAKE, BUY] = Object.keys(SEED.actions);

/* ============================== bills of materials ============================== */
const componentsOf = (tid, pid) => db().all("SELECT component_id, qty, scrap_pct FROM boms WHERE tenant_id=? AND product_id=? ORDER BY component_id", N(tid), String(pid));
/* everything below an item, at any depth */
function below(tid, pid, seen) {
  const s = seen || new Set();
  for (const c of componentsOf(tid, pid)) if (!s.has(c.component_id)) { s.add(c.component_id); below(tid, c.component_id, s); }
  return s;
}
/* an item's bill of materials, replaced as a whole: [{ component_id, qty, scrap_pct? }] (an empty list removes it) */
function setBom(tid, pid, list) {
  const t = N(tid), p = product(t, pid);
  if (!Array.isArray(list)) fail("Send the components as a list");
  const seen = new Set(), rows = list.map(raw => {
    const c = raw || {}, cp = product(t, c.component_id), qty = N(c.qty), scrap = N(c.scrap_pct || 0);
    if (cp.id === p.id) fail("An item is not a component of itself");
    if (seen.has(cp.id)) fail(cp.id + " is listed twice"); seen.add(cp.id);
    if (!(qty > 0)) fail("A component's quantity is more than zero");
    if (!(scrap >= 0 && scrap < 100)) fail("A component's loss is 0 to under 100 percent");
    if (below(t, cp.id).has(p.id)) fail(cp.id + " is made from " + p.id + ": that would go round in a circle", 409, "bom_cycle");
    return { component_id: cp.id, qty: +qty.toFixed(6), scrap_pct: r2(scrap) };
  });
  return tx(() => {
    db().run("DELETE FROM boms WHERE tenant_id=? AND product_id=?", t, p.id);
    for (const r of rows) db().run("INSERT INTO boms(tenant_id, product_id, component_id, qty, scrap_pct) VALUES(?,?,?,?,?)", t, p.id, r.component_id, r.qty, r.scrap_pct);
    return bom(t, p.id);
  });
}
/* an item's components, with theirs beneath them */
function bom(tid, pid, depth) {
  const d = depth || 0; if (d > SEED.maxLevels) fail("A bill of materials deeper than " + SEED.maxLevels + " levels");
  const p = product(tid, pid);
  return { product_id: p.id, title: p.title, components: componentsOf(tid, p.id).map(c => ({ ...c, ...bom(tid, c.component_id, d + 1) })) };
}
function boms(tid) {
  return db().all("SELECT b.product_id, p.title, COUNT(*) components FROM boms b LEFT JOIN products p ON p.tenant_id=b.tenant_id AND p.id=b.product_id WHERE b.tenant_id=? GROUP BY b.product_id, p.title ORDER BY b.product_id", N(tid));
}
/* an item's lead time (days), safety stock and smallest lot; a null lead time takes its supplier's, or the default */
function setItem(tid, pid, input) {
  const p = product(tid, pid), i = input || {};
  const lead = i.lead_days === null || i.lead_days === "" || i.lead_days === undefined ? null : N(i.lead_days);
  if (lead !== null && !(Number.isInteger(lead) && lead >= 0 && lead <= 365)) fail("A lead time is 0 to 365 whole days");
  const safety = N(i.safety_stock || 0), lot = N(i.min_lot || 1);
  if (!(Number.isInteger(safety) && safety >= 0)) fail("Safety stock is a whole number of zero or more");
  if (!(Number.isInteger(lot) && lot >= 1)) fail("The smallest lot is a whole number of at least 1");
  db().run("INSERT INTO mrp_items(tenant_id, product_id, lead_days, safety_stock, min_lot) VALUES(?,?,?,?,?) ON CONFLICT(tenant_id, product_id) DO UPDATE SET lead_days=excluded.lead_days, safety_stock=excluded.safety_stock, min_lot=excluded.min_lot",
    N(tid), p.id, lead, safety, lot);
  return db().get("SELECT * FROM mrp_items WHERE tenant_id=? AND product_id=?", N(tid), p.id);
}
const itemOf = (tid, pid) => db().get("SELECT * FROM mrp_items WHERE tenant_id=? AND product_id=?", N(tid), pid) || { lead_days: null, safety_stock: 0, min_lot: 1 };

/* ============================== the master schedule ============================== */
/* { product_id, qty, due_date, note? } — what must be ready by a date */
function addDemand(tid, input, actor) {
  const i = input || {}, p = product(tid, i.product_id), qty = N(i.qty), due = str(i.due_date, 10);
  if (!(Number.isInteger(qty) && qty >= 1)) fail("Demand is a whole number of at least 1");
  if (!isDate(due)) fail("Say when it must be ready, YYYY-MM-DD");
  const w = db().run("INSERT INTO mrp_demand(tenant_id, product_id, qty, due_date, note, created_by) VALUES(?,?,?,?,?,?)", N(tid), p.id, qty, due, str(i.note, 300), str(actor, 120));
  return db().get("SELECT * FROM mrp_demand WHERE id=?", N(w.lastInsertRowid));
}
function removeDemand(tid, id) {
  if (!db().run("DELETE FROM mrp_demand WHERE id=? AND tenant_id=?", N(id), N(tid)).changes) fail("No such demand", 404);
  return { ok: true };
}
function demand(tid) {
  return db().all("SELECT d.*, p.title FROM mrp_demand d LEFT JOIN products p ON p.tenant_id=d.tenant_id AND p.id=d.product_id WHERE d.tenant_id=? ORDER BY d.due_date, d.id LIMIT 500", N(tid));
}

/* ============================== supply ============================== */
/* on the shelf now; null for an item that is not counted (never short) */
function onHand(tid, p) {
  const a = require("./stock.js").available(tid, p, null);
  return a === Infinity ? null : Math.max(0, N(a) || 0);
}
/* what open purchase orders and work orders will still bring */
function incoming(tid, pid) {
  const po = [...new Set(["receivable", "editable"].flatMap(tag => states.tagged(MS.purchaseOrder, tag)))];
  const wo = states.vocab(MS.workOrder).filter(s => !states.is(MS.workOrder, s, "terminal"));
  const fromPo = db().get(`SELECT COALESCE(SUM(l.qty - l.received),0) q FROM purchase_order_lines l JOIN purchase_orders o ON o.id=l.po_id WHERE o.tenant_id=? AND l.product_id=? AND o.status IN ${ph(po)}`, N(tid), pid, ...po).q;
  const fromWo = db().get(`SELECT COALESCE(SUM(qty - completed_qty),0) q FROM work_orders WHERE tenant_id=? AND product_id=? AND status IN ${ph(wo)}`, N(tid), pid, ...wo).q;
  return Math.max(0, N(fromPo)) + Math.max(0, N(fromWo));
}
/* the supplier an item is bought from: its primary one, else any active */
const supplierFor = (tid, pid) => db().get("SELECT ps.*, s.name FROM product_suppliers ps JOIN suppliers s ON s.id=ps.supplier_id WHERE ps.tenant_id=? AND ps.product_id=? AND COALESCE(ps.status,'active')<>'inactive' ORDER BY ps.is_primary DESC, ps.price LIMIT 1", N(tid), pid);

/* ============================== the run ============================== */
/* how deep each item sits below the finished goods (its lowest level), so a run plans an item only after everything that uses it */
function levels(tid, roots) {
  const lvl = new Map();
  const walk = (pid, d) => {
    if (d > SEED.maxLevels) fail("A bill of materials deeper than " + SEED.maxLevels + " levels");
    if ((lvl.get(pid) ?? -1) >= d) return;
    lvl.set(pid, d);
    for (const c of componentsOf(tid, pid)) walk(c.component_id, d + 1);
  };
  for (const r of roots) walk(r, 0);
  return lvl;
}
/* { horizon_days? } — plans everything due within the horizon */
function run(tid, input, actor) {
  const t = N(tid), i = input || {}, horizon = N(i.horizon_days || SEED.horizonDays);
  if (!(Number.isInteger(horizon) && horizon >= 1 && horizon <= 730)) fail("A horizon is 1 to 730 days");
  const through = addDays(today(), horizon), gross = new Map(), needBy = new Map();
  const want = (pid, qty, date) => { gross.set(pid, (gross.get(pid) || 0) + qty); if (!needBy.has(pid) || date < needBy.get(pid)) needBy.set(pid, date); };
  for (const d of db().all("SELECT product_id, qty, due_date FROM mrp_demand WHERE tenant_id=? AND due_date<=?", t, through)) want(d.product_id, d.qty, d.due_date < today() ? today() : d.due_date);
  /* what open work orders still need of their components */
  const wo = states.vocab(MS.workOrder).filter(s => !states.is(MS.workOrder, s, "terminal"));
  for (const w of db().all(`SELECT product_id, qty, completed_qty, planned_start FROM work_orders WHERE tenant_id=? AND status IN ${ph(wo)}`, t, ...wo)) {
    const left = N(w.qty) - N(w.completed_qty);
    if (left > 0) for (const c of componentsOf(t, w.product_id)) want(c.component_id, Math.ceil(left * c.qty / (1 - c.scrap_pct / 100)), w.planned_start && w.planned_start > today() ? w.planned_start : today());
  }
  /* items kept at a safety stock are planned even without demand */
  for (const it of db().all("SELECT product_id FROM mrp_items WHERE tenant_id=? AND safety_stock>0", t)) if (!gross.has(it.product_id)) { gross.set(it.product_id, 0); needBy.set(it.product_id, today()); }
  const lvl = levels(t, [...gross.keys()]), order = [...lvl.keys()].sort((a, b) => lvl.get(a) - lvl.get(b) || (a < b ? -1 : 1));
  const out = [];
  for (const pid of order) {
    const p = db().get("SELECT * FROM products WHERE tenant_id=? AND id=? AND deleted_at IS NULL", t, pid); if (!p) continue;
    const have = onHand(t, p); if (have === null) continue;
    const it = itemOf(t, pid), g = gross.get(pid) || 0, inc = incoming(t, pid), safety = N(it.safety_stock) || 0;
    const net = g + safety - have - inc;
    if (net <= 0) continue;
    const comps = componentsOf(t, pid), make = comps.length > 0, sup = make ? null : supplierFor(t, pid);
    const qty = Math.max(net, N(it.min_lot) || 1, sup ? N(sup.moq) || 1 : 1);
    const lead = it.lead_days != null ? N(it.lead_days) : make ? SEED.defaultMakeLeadDays : sup && sup.lead_days != null ? N(sup.lead_days) : SEED.defaultBuyLeadDays;
    const need = needBy.get(pid) || today(), start = addDays(need, -lead);
    out.push({ product_id: pid, title: p.title, action: make ? MAKE : BUY, level: lvl.get(pid), qty, gross: g, available: have, incoming: inc, safety, need_by: need, order_by: start, late: start < today() ? 1 : 0,
      supplier_id: sup ? sup.supplier_id : null, supplier: sup ? sup.name : null, unit_cost: sup && sup.price != null ? N(sup.price) : null });
    /* a planned work order needs its components when it starts */
    for (const c of comps) want(c.component_id, Math.ceil(qty * c.qty / (1 - c.scrap_pct / 100)), start < today() ? today() : start);
  }
  return tx(() => {
    const open = states.tagged(MS.suggestion, "open");
    db().run(`UPDATE mrp_suggestions SET status=? WHERE tenant_id=? AND status IN ${ph(open)}`, states.first(MS.suggestion, "superseded"), t, ...open);
    const ref = `${SEED.ref}-${t}-${String(db().get("SELECT COUNT(*) c FROM mrp_runs WHERE tenant_id=?", t).c + 1).padStart(5, "0")}`;
    const r = db().run("INSERT INTO mrp_runs(tenant_id, ref, horizon_days, through, suggestions, late, ran_by) VALUES(?,?,?,?,?,?,?)", t, ref, horizon, through, out.length, out.filter(x => x.late).length, str(actor, 120));
    const runId = N(r.lastInsertRowid);
    for (const s of out) db().run("INSERT INTO mrp_suggestions(tenant_id, run_id, product_id, action, level, qty, gross, available, incoming, safety, need_by, order_by, late, supplier_id, unit_cost, status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
      t, runId, s.product_id, s.action, s.level, s.qty, s.gross, s.available, s.incoming, s.safety, s.need_by, s.order_by, s.late, s.supplier_id, s.unit_cost, states.initial(MS.suggestion));
    return latest(t);
  });
}
function latest(tid) {
  const r = db().get("SELECT * FROM mrp_runs WHERE tenant_id=? ORDER BY id DESC LIMIT 1", N(tid));
  if (!r) return { run: null, suggestions: [] };
  return { run: r, suggestions: db().all(`SELECT s.*, p.title, sp.name supplier FROM mrp_suggestions s LEFT JOIN products p ON p.tenant_id=s.tenant_id AND p.id=s.product_id LEFT JOIN suppliers sp ON sp.id=s.supplier_id
     WHERE s.run_id=? ORDER BY s.late DESC, s.order_by, s.level, s.product_id`, r.id).map(s => ({ ...s, open: states.is(MS.suggestion, s.status, "open") })) };
}
/* the variant an item's stock lives on, when it has only one (a work order counts against it) */
const onlySku = (tid, pid) => { const xs = db().all("SELECT id FROM skus WHERE tenant_id=? AND product_id=? AND active=1 ORDER BY id LIMIT 2", N(tid), pid); return xs.length === 1 ? xs[0].id : null; };
/* the suggestions (`ids`, or every open one of the latest run) turned into draft purchase orders, one per supplier, and planned work orders */
function convert(tid, input, actor) {
  const t = N(tid), i = input || {}, open = states.tagged(MS.suggestion, "open"), last = latest(t).run;
  const ids = Array.isArray(i.ids) && i.ids.length ? i.ids.map(N) : last ? db().all(`SELECT id FROM mrp_suggestions WHERE run_id=? AND status IN ${ph(open)}`, last.id, ...open).map(r => r.id) : [];
  if (!ids.length) fail("Nothing to act on — run planning first", 409);
  const rows = db().all(`SELECT * FROM mrp_suggestions WHERE tenant_id=? AND id IN ${ph(ids)} AND status IN ${ph(open)}`, t, ...ids, ...open);
  if (rows.length !== ids.length) fail("Some of these have already been acted on or superseded — reload", 409);
  const noSupplier = rows.filter(s => s.action === BUY && !s.supplier_id);
  if (noSupplier.length) fail("No supplier is set for " + noSupplier.map(s => s.product_id).join(", ") + " — add one, or leave it out", 409, "no_supplier");
  return tx(() => {
    /* each suggestion is claimed before anything is made from it, so two people acting at once make it once */
    const claimed = db().run(`UPDATE mrp_suggestions SET status=? WHERE tenant_id=? AND id IN ${ph(ids)} AND status IN ${ph(open)}`, states.first(MS.suggestion, "converted"), t, ...ids, ...open);
    if (claimed.changes !== ids.length) fail("Some of these were acted on a moment ago — reload", 409);
    const made = [], P = require("./purchasing.js"), O = require("./operations.js"), runRef = (db().get("SELECT ref FROM mrp_runs WHERE id=?", rows[0].run_id) || {}).ref;
    const bySupplier = {};
    for (const s of rows.filter(x => x.action === BUY)) (bySupplier[s.supplier_id] = bySupplier[s.supplier_id] || []).push(s);
    for (const [sid, list] of Object.entries(bySupplier)) {
      const po = P.createOrder(t, { supplier_id: N(sid), expected_at: list.map(s => s.need_by).sort()[0], note: "From planning run " + runRef, lines: list.map(s => ({ product_id: s.product_id, qty: s.qty, unit_cost: s.unit_cost || 0 })) }, actor);
      for (const s of list) db().run("UPDATE mrp_suggestions SET made_ref=? WHERE id=?", po.ref, s.id);
      made.push({ kind: BUY, ref: po.ref, lines: list.length });
    }
    for (const s of rows.filter(x => x.action === MAKE)) {
      /* the work order consumes its components from the shelf when it is completed (lib/operations.js) */
      const skuBom = {};
      for (const c of componentsOf(t, s.product_id)) { const sk = onlySku(t, c.component_id); if (sk) skuBom[sk] = +(c.qty / (1 - c.scrap_pct / 100)).toFixed(6); }
      const w = O.upsertWorkOrder(t, { product_id: s.product_id, sku_id: onlySku(t, s.product_id), qty: s.qty, bom: skuBom, planned_start: s.order_by, planned_end: s.need_by });
      db().run("UPDATE mrp_suggestions SET made_ref=? WHERE id=?", w.ref, s.id);
      made.push({ kind: MAKE, ref: w.ref, lines: 1 });
    }
    return { made, ...latest(t) };
  });
}
function dismiss(tid, id) {
  const open = states.tagged(MS.suggestion, "open");
  if (!db().run(`UPDATE mrp_suggestions SET status=? WHERE id=? AND tenant_id=? AND status IN ${ph(open)}`, states.first(MS.suggestion, "dismissed"), N(id), N(tid), ...open).changes) fail("This suggestion is no longer open", 409);
  return latest(tid);
}
module.exports = { setBom, bom, boms, setItem, addDemand, removeDemand, demand, incoming, run, latest, convert, dismiss, SEED };
