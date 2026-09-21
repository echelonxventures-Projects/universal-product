/* LUXORA Platform — Supply-chain planning (Roadmap II · domain E).
   Per-SKU demand forecasting from real order history (moving average + trend), reorder point /
   safety-stock / min-max computation with lead-time awareness from product_suppliers, and
   suggested purchase orders to the primary supplier. Reads existing skus/inventory/order_items/
   product_suppliers — writes replenishments. Statuses & priorities are meta_lists registries
   (planStatuses, planPriorities) so they are editable from Data Studio. Feature-gated by
   settings.features.planning. */
"use strict";

const db = () => require("./db.js");
const { stamp } = require("./db.js");
const J = (v, d) => { try { return v == null || v === "" ? (d == null ? {} : d) : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d == null ? {} : d; } };

const STATUSES = ["suggested", "approved", "ordered", "received", "skipped"];
const PRIORITIES = ["low", "normal", "high", "urgent"];
const HORIZON_DAYS = 90;          /* how much order history feeds the forecast */
const TARGET_DAYS = 30;           /* the forecast horizon (replenish to cover N days) */
const SERVICE_FACTOR = 1.5;       /* safety stock = factor × lead-time demand (Z≈1.5 ≈ 93%) */
const MIN_REORDER_QTY = 1;

function seed() {
  const D = db();
  const put = (name, label, items) => {
    const existing = D.get("SELECT items FROM meta_lists WHERE name=?", name);
    const cur = J(existing ? existing.items : "[]", []);
    for (const it of items) if (!cur.some(x => (x.key || x) === (it.key || it))) cur.push(it);
    if (existing) D.run("UPDATE meta_lists SET items=? WHERE name=?", JSON.stringify(cur), name);
    else D.run("INSERT INTO meta_lists(name,label,items) VALUES(?,?,?)", name, label, JSON.stringify(items));
  };
  put("planStatuses", "Planning · Replenishment statuses", STATUSES.map(k => ({ key: k, name: k })));
  put("planPriorities", "Planning · Priorities", PRIORITIES.map(k => ({ key: k, name: k })));
}

/* ---------------- demand ---------------- */
/* Daily units sold for a SKU over the horizon, indexed 0..N-1 (oldest first). order_items has no
   tenant_id, so it is joined through orders. A SKU captures demand both when the order line points
   at the SKU directly (sku_id) and when it points only at the product (product_id) — checkout
   records whichever is known, so both are counted to avoid under-forecasting. */
function dailyDemand(tenantId, skuId, days) {
  const D = db();
  const sku = D.get("SELECT product_id FROM skus WHERE id=? AND tenant_id=?", skuId, tenantId);
  const productId = sku ? sku.product_id : null;
  const rows = D.all(`SELECT date(o.created_at) d, SUM(oi.qty) q
                      FROM order_items oi JOIN orders o ON o.id = oi.order_id
                      WHERE o.tenant_id=? AND (oi.sku_id=? ${productId ? "OR oi.product_id=?" : ""})
                      AND o.status NOT IN ('cancelled','refunded')
                      GROUP BY date(o.created_at) ORDER BY date(o.created_at)`,
    tenantId, skuId, ...(productId ? [productId] : []));
  const byDay = new Map();
  for (const r of rows) byDay.set(r.d.slice(0, 10), r.q);
  const out = [];
  for (let i = days - 1; i >= 0; i--) {
    const key = new Date(Date.now() - i * 86400e3).toISOString().slice(0, 10);
    out.push(Number(byDay.get(key) || 0));
  }
  return out;
}

/* weighted moving average + linear trend slope. Recent weeks weigh more (exponential-ish decay
   via a triangular window) so a sudden spike or a dead SKU both move the plan. */
function forecast(series) {
  const n = series.length;
  if (!n) return { avg_daily: 0, forecast_30d: 0, trend: 0 };
  let wsum = 0, num = 0;
  for (let i = 0; i < n; i++) { const w = i + 1; wsum += w; num += series[i] * w; }
  const avg_daily = num / wsum;
  /* ordinary-least-squares slope of daily demand (units/day per day) over the horizon */
  const xs = series.map((_, i) => i);
  const xm = xs.reduce((a, b) => a + b, 0) / n;
  const ym = series.reduce((a, b) => a + b, 0) / n;
  let sxy = 0, sxx = 0;
  for (let i = 0; i < n; i++) { sxy += (xs[i] - xm) * (series[i] - ym); sxx += (xs[i] - xm) ** 2; }
  const trend = sxx ? sxy / sxx : 0;
  const projected = Math.max(0, Math.round(avg_daily * TARGET_DAYS + trend * TARGET_DAYS));
  return { avg_daily: +avg_daily.toFixed(2), forecast_30d: projected, trend: +trend.toFixed(3) };
}

/* ---------------- stock state ---------------- */
function stockOf(tenantId, skuId) {
  const D = db();
  const inv = D.all("SELECT COALESCE(SUM(qty),0) on_hand, COALESCE(SUM(reserved),0) reserved FROM inventory WHERE tenant_id=? AND sku_id=?", tenantId, skuId);
  const r = inv[0] || {};
  return { on_hand: r.on_hand || 0, reserved: r.reserved || 0, available: Math.max(0, (r.on_hand || 0) - (r.reserved || 0)) };
}

function supplierOf(tenantId, productId) {
  const D = db();
  const r = D.get(`SELECT ps.supplier_id, ps.lead_days, ps.moq, ps.price, s.name supplier_name
                   FROM product_suppliers ps LEFT JOIN suppliers s ON s.id=ps.supplier_id
                   WHERE ps.tenant_id=? AND ps.product_id=? AND (ps.is_primary=1 OR ps.status='active')
                   ORDER BY ps.is_primary DESC, ps.id LIMIT 1`, tenantId, productId);
  return r || { supplier_id: null, lead_days: 7, moq: 1, price: null, supplier_name: "" };
}

/* ---------------- the plan ---------------- */
/* Recompute every active SKU and upsert one replenishment row per SKU. Pure function of the
   live tables — safe to run on a schedule or on demand. Returns the rows it wrote. */
function runPlan(tenantId) {
  const D = db();
  const skus = D.all("SELECT id, product_id, code, name, stock, active FROM skus WHERE tenant_id=? AND active=1", tenantId);
  const written = [];
  for (const sk of skus) {
    const st = stockOf(tenantId, sk.id);
    const sup = supplierOf(tenantId, sk.product_id);
    const fc = forecast(dailyDemand(tenantId, sk.id, HORIZON_DAYS));
    const lead = Number(sup.lead_days) || 7;
    const moq = Math.max(MIN_REORDER_QTY, Number(sup.moq) || 1);
    const leadDemand = Math.ceil(fc.avg_daily * lead);
    const safety = Math.max(0, Math.ceil(fc.avg_daily * lead * (SERVICE_FACTOR - 1)));
    const reorderPoint = leadDemand + safety;
    const target = Math.max(safety + Math.ceil(fc.forecast_30d), reorderPoint);
    const need = Math.max(0, target - st.available);
    const minQty = Math.max(moq, Math.ceil(fc.avg_daily * lead));
    const maxQty = Math.max(target, minQty);
    /* reorder qty covers the gap, rounded up to the MOQ; nothing to buy if stock is healthy */
    const reorderQty = need > 0 ? Math.max(minQty, Math.ceil(need / moq) * moq) : 0;
    const urgent = st.available <= Math.max(1, Math.floor(reorderPoint / 2));
    const priority = reorderQty === 0 ? "low" : urgent ? "urgent" : need > reorderPoint ? "high" : "normal";
    const exists = D.get("SELECT id, status, po_ref FROM replenishments WHERE tenant_id=? AND sku_id=?", tenantId, sk.id);
    /* never overwrite a row that is already in the purchasing pipeline */
    if (exists && ["ordered", "received"].includes(exists.status)) continue;
    const row = {
      sku_id: sk.id, product_id: sk.product_id, on_hand: st.on_hand, reserved: st.reserved, available: st.available,
      avg_daily: fc.avg_daily, forecast_30d: fc.forecast_30d, trend: fc.trend,
      lead_days: lead, safety_stock: safety, reorder_point: reorderPoint, reorder_qty: reorderQty,
      min_qty: minQty, max_qty: maxQty,
      supplier_id: sup.supplier_id, supplier_name: sup.supplier_name || "",
      unit_cost: sup.price == null ? 0 : sup.price,
      status: reorderQty > 0 ? "suggested" : "skipped",
      priority
    };
    if (exists) {
      D.run(`UPDATE replenishments SET on_hand=?, reserved=?, available=?, avg_daily=?, forecast_30d=?, trend=?,
             lead_days=?, safety_stock=?, reorder_point=?, reorder_qty=?, min_qty=?, max_qty=?,
             supplier_id=?, supplier_name=?, unit_cost=?, status=?, priority=?, updated_at=?
             WHERE id=?`,
        row.on_hand, row.reserved, row.available, row.avg_daily, row.forecast_30d, row.trend,
        row.lead_days, row.safety_stock, row.reorder_point, row.reorder_qty, row.min_qty, row.max_qty,
        row.supplier_id, row.supplier_name, row.unit_cost, row.status, row.priority, stamp(), exists.id);
    } else {
      D.run(`INSERT INTO replenishments(tenant_id,sku_id,product_id,on_hand,reserved,available,avg_daily,
             forecast_30d,trend,lead_days,safety_stock,reorder_point,reorder_qty,min_qty,max_qty,
             supplier_id,supplier_name,unit_cost,status,priority,generated_at)
             VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`,
        tenantId, row.sku_id, row.product_id, row.on_hand, row.reserved, row.available, row.avg_daily,
        row.forecast_30d, row.trend, row.lead_days, row.safety_stock, row.reorder_point, row.reorder_qty,
        row.min_qty, row.max_qty, row.supplier_id, row.supplier_name, row.unit_cost, row.status,
        row.priority, stamp());
    }
    written.push({ ...row, id: exists ? exists.id : Number(D.get("SELECT last_insert_rowid() c").c), product_code: sk.code, product_name: sk.name });
  }
  return written;
}

/* ---------------- reads ---------------- */
function listReplenishments(tenantId, f) {
  const D = db(); f = f || {};
  let sql = `SELECT r.*, s.code sku_code, s.name sku_name, p.title product_title
             FROM replenishments r
             LEFT JOIN skus s ON s.id=r.sku_id AND s.tenant_id=r.tenant_id
             LEFT JOIN products p ON p.id=r.product_id AND p.tenant_id=r.tenant_id
             WHERE r.tenant_id=?`;
  const a = [tenantId];
  if (f.status) { sql += " AND r.status=?"; a.push(f.status); }
  if (f.priority) { sql += " AND r.priority=?"; a.push(f.priority); }
  sql += " ORDER BY CASE r.priority WHEN 'urgent' THEN 0 WHEN 'high' THEN 1 WHEN 'normal' THEN 2 ELSE 3 END, r.reorder_qty DESC, r.id DESC LIMIT 300";
  return D.all(sql, ...a);
}

/* buy list = SKUs that actually need purchasing now */
function buyList(tenantId) {
  return listReplenishments(tenantId, {}).filter(r => r.reorder_qty > 0 && !["ordered", "received"].includes(r.status));
}

/* one suggested PO per supplier, from the current buy list */
function purchaseOrders(tenantId) {
  const bySupplier = new Map();
  for (const r of buyList(tenantId)) {
    const key = r.supplier_id || ("none-" + r.id);
    if (!bySupplier.has(key)) bySupplier.set(key, { supplier_id: r.supplier_id, supplier_name: r.supplier_name || "Unassigned supplier", lines: [], units: 0, cost: 0 });
    const po = bySupplier.get(key);
    po.lines.push({ sku_id: r.sku_id, sku_code: r.sku_code, product_title: r.product_title, qty: r.reorder_qty, unit_cost: r.unit_cost || 0, ext: +(((r.unit_cost || 0) * r.reorder_qty).toFixed(2)) });
    po.units += r.reorder_qty;
    po.cost = +(po.cost + (r.unit_cost || 0) * r.reorder_qty).toFixed(2);
  }
  return [...bySupplier.values()];
}

function summary(tenantId) {
  const D = db();
  const row = D.get(`SELECT COUNT(*) n,
    SUM(CASE WHEN reorder_qty>0 AND status NOT IN ('ordered','received') THEN 1 ELSE 0 END) open,
    SUM(CASE WHEN status='suggested' THEN 1 ELSE 0 END) suggested,
    SUM(CASE WHEN status='ordered' THEN 1 ELSE 0 END) ordered,
    SUM(CASE WHEN priority='urgent' AND reorder_qty>0 THEN 1 ELSE 0 END) urgent,
    SUM(CASE WHEN available<=reorder_point AND reorder_qty>0 THEN 1 ELSE 0 END) below_reorder
    FROM replenishments WHERE tenant_id=?`, tenantId);
  const health = D.get(`SELECT COUNT(*) skus, SUM(CASE WHEN active=1 THEN 1 ELSE 0 END) active_skus FROM skus WHERE tenant_id=?`, tenantId);
  return {
    total: row.n || 0, open: row.open || 0, suggested: row.suggested || 0, ordered: row.ordered || 0,
    urgent: row.urgent || 0, below_reorder: row.below_reorder || 0,
    skus: health.skus || 0, active_skus: health.active_skus || 0
  };
}

/* ---------------- mutations ---------------- */
function setStatus(tenantId, id, status, poRef) {
  const D = db();
  if (!STATUSES.includes(status)) throw new Error("Unknown replenishment status: " + status);
  const r = D.get("SELECT id FROM replenishments WHERE id=? AND tenant_id=?", Number(id), tenantId);
  if (!r) throw new Error("Unknown replenishment " + id);
  const patch = { status };
  if (poRef !== undefined) patch.po_ref = String(poRef || "");
  /* approving/advancing a suggestion without a PO ref mints a stable draft number */
  if (status === "approved" || status === "ordered") {
    patch.po_status = status === "ordered" ? "issued" : "draft";
    if (!patch.po_ref && !D.get("SELECT po_ref p FROM replenishments WHERE id=?", Number(id)).p) patch.po_ref = "PO-" + tenantId + "-" + (1000 + Number(id));
  }
  if (status === "received") { patch.po_status = "received"; patch.closed_at = stamp(); }
  if (status === "skipped") { patch.po_status = "skipped"; patch.closed_at = stamp(); }
  const sets = Object.keys(patch).map(k => k + "=?").join(", ");
  D.run("UPDATE replenishments SET " + sets + ", updated_at=? WHERE id=?", ...Object.values(patch), stamp(), Number(id));
  return D.get("SELECT * FROM replenishments WHERE id=?", Number(id));
}

/* promote a whole buy list to approved POs in one call (the "approve all" action) */
function approveAll(tenantId) {
  const D = db();
  const out = [];
  for (const r of buyList(tenantId)) out.push(setStatus(tenantId, r.id, "approved"));
  return out;
}

module.exports = {
  seed, STATUSES, PRIORITIES, HORIZON_DAYS, TARGET_DAYS,
  dailyDemand, forecast, stockOf, supplierOf,
  runPlan, listReplenishments, buyList, purchaseOrders, summary,
  setStatus, approveAll
};
