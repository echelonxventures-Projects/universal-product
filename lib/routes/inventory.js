/* LUXORA Platform — inventory domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the inventory domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "inventory", routes(kit) {
  const { CFG, T, all, bad, enterprise, get, json, logAction, logistics, requireAdmin, requireSection, run } = kit;

  function apiWarehouseRoute(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, logistics.route(T(s), Number(body.warehouse_id) || url.searchParams.get("warehouse_id") || null));
  }
  function apiAdminInventoryPut(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    const t = T(s);
    const inv = get("SELECT * FROM inventory WHERE id=? AND tenant_id=?", Number(id), t);
    if (!inv) return bad(res, "Unknown inventory row", 404);
    run("UPDATE inventory SET qty=?,reserved=?,lot=?,batch=?,expiry=?,serial=? WHERE id=?",
      Number(body.qty), Number(body.reserved) || 0, String(body.lot || ""), String(body.batch || ""), String(body.expiry || ""), JSON.stringify(body.serial || []), inv.id);
    const total = get("SELECT COALESCE(SUM(qty),0) q FROM inventory WHERE tenant_id=? AND sku_id=?", t, inv.sku_id).q;
    run("UPDATE skus SET stock=? WHERE id=?", total, inv.sku_id);
    logAction(s, "inventory.update", "inventory", id, { qty: body.qty });
    json(res, 200, { ok: true });
  }
  function apiAdminWarehouses(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { warehouses: all("SELECT * FROM warehouses WHERE tenant_id=?", T(s)) });
  }
  function apiAdminWarehouseSave(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    if (!body.name) return bad(res, "Name required");
    if (id) run("UPDATE warehouses SET name=?,code=?,country=?,region=?,active=? WHERE id=? AND tenant_id=?", String(body.name), String(body.code || ""), String(body.country || CFG(s).commerce.country), String(body.region || ""), body.active === 0 ? 0 : 1, Number(id), T(s));
    else run("INSERT INTO warehouses(tenant_id,name,code,country,region) VALUES(?,?,?,?,?)", T(s), String(body.name), String(body.code || ""), String(body.country || CFG(s).commerce.country), String(body.region || ""));
    logAction(s, "warehouse.save", "warehouse", id || "new");
    json(res, 200, { ok: true });
  }
  function apiAdminSerializedBulk(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const t = T(s), pid = String(body.product_id || ""), count = Math.min(500, Math.max(1, Number(body.count) || 1));
    if (!pid) return bad(res, "product_id required");
    const p = get("SELECT * FROM products WHERE tenant_id=? AND id=?", t, pid); if (!p) return bad(res, "Unknown product", 404);
    const skuId = (get("SELECT id FROM skus WHERE tenant_id=? AND product_id=? ORDER BY id LIMIT 1", t, pid) || {}).id || null;
    const whId = (get("SELECT id FROM warehouses WHERE tenant_id=? ORDER BY id LIMIT 1", t) || {}).id || null;
    const prefix = String(body.prefix || p.id + "-SN"); let made = 0;
    for (let i = 0; i < count; i++) { const serial = prefix + "-" + Date.now().toString(36) + "-" + i; try { run("INSERT INTO serialized_items(tenant_id,product_id,sku_id,warehouse_id,serial,status,condition,purchase_date) VALUES(?,?,?,?,?,?,?,?)", t, pid, skuId, whId, serial, "in_stock", "new", new Date().toISOString().slice(0, 10)); made++; } catch (e) { } }
    logAction(s, "serialized.bulk", "serialized", pid, { count: made });
    json(res, 200, { ok: true, created: made });
  }
  function apiTransfers(req, res, url, s, body) { if (!requireAdmin(s, res)) return; json(res, 200, { transfers: all("SELECT * FROM stock_transfers WHERE tenant_id=? AND deleted_at IS NULL ORDER BY id DESC LIMIT 100", T(s)) }); }
  function apiTransferCreate(req, res, url, s, body) { if (!requireAdmin(s, res)) return; if (!requireSection(s, res, "skus", "write")) return; const r = enterprise.stockTransfer(T(s), body || {}); if (r.error) return bad(res, r.error, 422); logAction(s, "stock.transfer", "stock_transfer", r.id, { from: body.from_warehouse, to: body.to_warehouse, qty: body.qty }, req); json(res, 200, r); }

  return [
    ["POST /api/admin/warehouses/route", (r, re, u, s, b) => apiWarehouseRoute(r, re, u, s, b)],
    ["PUT /api/admin/inventory/:id", (r, re, u, s, b, p) => apiAdminInventoryPut(r, re, u, s, b, p)],
    ["GET /api/admin/warehouses", apiAdminWarehouses],
    ["POST /api/admin/warehouses", (r, re, u, s, b, p) => apiAdminWarehouseSave(r, re, u, s, b, p)],
    ["PUT /api/admin/warehouses/:id", (r, re, u, s, b, p) => apiAdminWarehouseSave(r, re, u, s, b, p)],
    ["POST /api/admin/serialized/bulk", apiAdminSerializedBulk],
    ["GET /api/admin/transfers", apiTransfers],
    ["POST /api/admin/transfers", apiTransferCreate]
  ];
} };
