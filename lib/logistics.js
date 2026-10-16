/* LUXORA Platform — Logistics & Supply-Chain.
   Fulfilment state machine, shipment tracking events, 3PL carrier abstraction (reuses the
   declarative provider_defs.kind=shipping specs + lib/connect.js, no per-carrier code), multi-warehouse
   routing, and return disposition. All configuration lives in meta_lists so new 3PLs, fulfilment
   states, or SLA tiers are added from Data Studio with zero code. */
"use strict";

const db = () => require("./db.js");
/* a shipment is a state machine (lib/states.js): this engine asks what a state means and
   registers the side effects a transition's registry row names */
const states = require("./states.js");
const inList = (machine, tag) => { const xs = states.tagged(machine, tag); return { sql: "(" + (xs.length ? xs.map(() => "?").join(",") : "NULL") + ")", args: xs }; };
const connect = () => require("./connect.js");
const events = () => require("./events.js");
const registry = () => require("./registry.js");
const J = (v, d) => { try { return v == null || v === "" ? (d == null ? [] : d) : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d == null ? [] : d; } };

const STATUSES = ["pending", "picked", "packed", "label", "dispatched", "in_transit", "out_for_delivery", "delivered", "failed"];
const DISPOSITIONS = ["refund", "replace", "restock", "credit", "reject"];

/* ---------- schema seed (idempotent) ---------- */
function seed() {
  const D = db();
  const cur = J(D.get("SELECT items FROM meta_lists WHERE name='logisticsStates'") ? D.get("SELECT items FROM meta_lists WHERE name='logisticsStates'").items : "[]", []);
  if (!cur.length) D.run("INSERT OR IGNORE INTO meta_lists(name,label,items) VALUES('logisticsStates','Logistics · Fulfilment states',?)", JSON.stringify(STATUSES.map(s => ({ key: s, name: s }))));
  const disp = J(D.get("SELECT items FROM meta_lists WHERE name='logisticsDispositions'") ? D.get("SELECT items FROM meta_lists WHERE name='logisticsDispositions'").items : "[]", []);
  if (!disp.length) D.run("INSERT OR IGNORE INTO meta_lists(name,label,items) VALUES('logisticsDispositions','Logistics · Return dispositions',?)", JSON.stringify(DISPOSITIONS.map(s => ({ key: s, name: s }))));
}

/* ---------- fulfilment ---------- */
function createShipment(tenantId, orderId, carrier, warehouseId, meta) {
  const D = db();
  const ref = "SHP-" + orderId + "-" + Date.now().toString(36).toUpperCase().slice(-6);
  const r = D.run("INSERT INTO shipments(tenant_id,order_id,tracking_ref,carrier,warehouse_id,status,meta) VALUES(?,?,?,?,?,?,?)",
    tenantId, orderId, ref, String(carrier || ""), warehouseId || null, states.initial("shipment"), JSON.stringify(meta || {}));
  event(tenantId, Number(r.lastInsertRowid), states.initial("shipment"), "Created", "Shipment created", ref, "system");
  return D.get("SELECT * FROM shipments WHERE id=?", r.lastInsertRowid);
}

function event(tenantId, shipmentId, status, location, note, ref, actor) {
  const D = db();
  D.run("INSERT INTO shipment_events(shipment_id,tenant_id,status,location,note,ref,actor) VALUES(?,?,?,?,?,?,?)", shipmentId, tenantId, status, location || "", note || "", ref || "", actor || "system");
  /* the status, and the time column the state declares, come from the machine */
  const cur = D.get("SELECT * FROM shipments WHERE id=? AND tenant_id=?", shipmentId, tenantId) || {};
  const { patch } = states.apply("shipment", { tenantId, from: cur.status, to: status, row: cur, force: true });
  D.run("UPDATE shipments SET " + Object.keys(patch).map(k => k + "=?").join(", ") + " WHERE id=? AND tenant_id=?", ...Object.values(patch), shipmentId, tenantId);
  events().emit(tenantId, "logistics." + status, { shipmentId, status, location, note });
}

/* 3PL outbound push (declarative; no-op when the provider is not configured), run where the
   transition's row names it */
states.handle("shipment", "push_3pl", ctx => {
  const s = ctx.row; if (!s.carrier) return;
  try {
    const gateway = db().get("SELECT id FROM tenant_gateways WHERE tenant_id=? AND provider_id=? AND enabled=1", ctx.tenantId, "ship:" + s.carrier);
    if (gateway) connect().notify(ctx.tenantId, "ship:" + s.carrier, { event: "shipment.dispatched", shipment: s.id, ref: s.tracking_ref, carrier: s.carrier });
  } catch (e) { /* offline / unconfigured — event still recorded locally */ }
});
function transition(tenantId, shipmentId, toStatus, extra) {
  const D = db();
  if (!states.has("shipment", toStatus)) throw new Error("Unknown shipment status: " + toStatus);
  const s = D.get("SELECT * FROM shipments WHERE id=? AND tenant_id=?", shipmentId, tenantId);
  if (!s) throw new Error("Unknown shipment " + shipmentId);
  event(tenantId, s.id, toStatus, (extra && extra.location) || "", (extra && extra.note) || "", (extra && extra.ref) || s.tracking_ref, (extra && extra.actor) || "system");
  return D.get("SELECT * FROM shipments WHERE id=?", s.id);
}

function track(tenantId, shipmentId) {
  const D = db();
  const s = D.get("SELECT * FROM shipments WHERE id=? AND tenant_id=?", shipmentId, tenantId);
  if (!s) return null;
  const evs = D.all("SELECT status,location,note,ref,actor,at FROM shipment_events WHERE shipment_id=? ORDER BY id", shipmentId).map(e => ({ status: e.status, location: e.location, note: e.note, ref: e.ref, actor: e.actor, at: e.at }));
  return { ...s, meta: J(s.meta, {}), events: evs };
}

function list(tenantId, f) {
  const D = db();
  f = f || {};
  let sql = "SELECT * FROM shipments WHERE tenant_id=?", a = [tenantId];
  if (f.status) { sql += " AND status=?"; a.push(f.status); }
  if (f.order_id) { sql += " AND order_id=?"; a.push(Number(f.order_id)); }
  sql += " ORDER BY id DESC LIMIT 200";
  const rows = D.all(sql, ...a);
  return rows.map(r => ({ ...r, meta: J(r.meta, {}) }));
}

/* ---------- multi-warehouse routing ---------- */
function route(tenantId, warehouseId) {
  const D = db();
  const whs = D.all("SELECT id,name,code,country,region FROM warehouses WHERE tenant_id=? AND active=1", Number(tenantId));
  if (!whs.length) return { primary: null, all: [] };
  const avail = wh => { const r = D.get("SELECT COALESCE(SUM(qty - reserved),0) a FROM inventory WHERE warehouse_id=?", Number(wh.id)); return r ? Number(r.a) : 0; };
  whs.forEach(w => w.available = avail(w.id));
  whs.sort((a, b) => b.available - a.available);
  const primary = whs.find(w => Number(w.id) === Number(warehouseId)) || whs[0];
  return { primary: { ...primary, preferred: whs[0].id === primary.id }, all: whs };
}

/* ---------- SLA ---------- */
function slaBreaches(tenantId, days) {
  const D = db();
  const n = Number(days) || 3;
  const done = inList("shipment", "terminal");
  return D.all("SELECT * FROM shipments WHERE tenant_id=? AND status NOT IN " + done.sql + " AND created_at < datetime('now', ?) ORDER BY created_at", tenantId, ...done.args, "-" + n + " days").map(r => ({ ...r, meta: J(r.meta, {}), breachDays: n }));
}

/* ---------- return disposition ---------- */
function returnDisposition(tenantId, returnId, disposition, extra) {
  const D = db();
  const r = D.get("SELECT * FROM returns WHERE id=? AND tenant_id=?", returnId, tenantId);
  if (!r) throw new Error("Unknown return " + returnId);
  const d = String(disposition || "refund");
  if (!DISPOSITIONS.includes(d)) throw new Error("Unknown return disposition: " + d);
  D.run("UPDATE returns SET status=?, note=? WHERE id=? AND tenant_id=?", d, JSON.stringify(extra || {}), returnId, tenantId);
  if (d === "restock" && r.product_id) {
    // move back to the primary warehouse
    const wh = D.get("SELECT id FROM warehouses WHERE tenant_id=? AND active=1 ORDER BY id LIMIT 1", tenantId);
    if (wh) D.run("INSERT INTO inventory(tenant_id,sku_id,warehouse_id,qty) VALUES(?,?,?,?) ON CONFLICT DO NOTHING", tenantId, null, wh.id, Number(r.qty) || 1);
  }
  events().emit(tenantId, "logistics.return." + d, { returnId, disposition: d });
  return D.get("SELECT * FROM returns WHERE id=?", returnId);
}

/* ---------- 3PL abstraction (registry-driven; zero per-carrier code) ---------- */
function carriers(tenantId) {
  return registry().providerDefs("shipping");
}

module.exports = {
  seed, STATUSES, DISPOSITIONS,
  createShipment, transition, track, list,
  route, slaBreaches, returnDisposition,
  carriers
};
