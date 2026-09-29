/* LUXORA Platform — Quick-commerce engine.
   Dark stores, delivery slots, pincode serviceability, store-inventory pinning,
   a delivery-promise engine, rider dispatch batching and proof-of-delivery.

   Every state, kind and threshold the engine consults is a registry row
   (meta_lists — see lib/parity-registries.js): the fulfilment state machine
   (`qcDispatchStatuses`), slot states, rider statuses and delivery kinds are
   data, so adding a new quick-commerce flow needs no code change here. The
   engines below are the small amount of logic that cannot be expressed as
   a table row: geo resolution, availability arithmetic and OTP generation. */
"use strict";

const db = () => require("./db.js");
const events = () => require("./events.js");
const reg = () => require("./parity-registries.js");
const crypto = require("crypto");

const J = (v, d) => { try { return v == null || v === "" ? (d == null ? [] : d) : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d == null ? [] : d; } };

/* ---------- serviceability: which stores can serve this pincode? ---------- */
/* resolution order: an explicit service_areas row (serviceable=1) → a store whose
   service_pincodes list contains the pincode → a store within radius when the
   request supplies coordinates. The result carries the promise the store advertises. */
function servingStores(tenantId, pincode, lat, lng) {
  const D = db();
  const stores = D.all("SELECT * FROM dark_stores WHERE tenant_id=? AND status='active'", Number(tenantId));
  if (!stores.length) return [];
  const scored = [];
  for (const s of stores) {
    const explicit = D.get("SELECT * FROM service_areas WHERE tenant_id=? AND store_id=? AND pincode=? AND serviceable=1 AND status='active'",
      Number(tenantId), s.id, String(pincode || ""));
    const pincodes = J(s.service_pincodes, []).map(String);
    const inList = pincodes.length && pincodes.includes(String(pincode || ""));
    let near = false, dist = null;
    if (lat != null && lng != null && s.lat != null && s.lng != null) {
      dist = haversine(+lat, +lng, +s.lat, +s.lng);
      near = dist <= (+s.service_radius_km || 3);
    }
    if (explicit) scored.push({ store: s, source: "service_area", eta: explicit.eta_minutes, fee: explicit.fee, minOrder: explicit.min_order, dist });
    else if (inList) scored.push({ store: s, source: "pincode_list", eta: s.promise_minutes, fee: s.delivery_fee, minOrder: s.min_order, dist });
    else if (near) scored.push({ store: s, source: "radius", eta: s.promise_minutes, fee: s.delivery_fee, minOrder: s.min_order, dist });
  }
  /* nearest / fastest first — the promise is the store's own advertised minutes */
  scored.sort((a, b) => ((a.eta || a.store.promise_minutes) - (b.eta || b.store.promise_minutes)) || ((a.dist == null ? 9e9 : a.dist) - (b.dist == null ? 9e9 : b.dist)));
  return scored;
}

/* great-circle distance in km (the only geo math the engine needs) */
function haversine(lat1, lon1, lat2, lon2) {
  const R = 6371, r = d => d * Math.PI / 180;
  const dLat = r(lat2 - lat1), dLon = r(lon2 - lon1);
  const a = Math.sin(dLat / 2) ** 2 + Math.cos(r(lat1)) * Math.cos(r(lat2)) * Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.asin(Math.min(1, Math.sqrt(a)));
}

/* ---------- delivery-promise engine ---------- */
/* A promise = the fastest serving store's promise minutes (or the slot's own
   promise override) + prep time. This is what the storefront shows as the
   delivery estimate, and what the checkout pins an order to. */
function promise(tenantId, pincode, lat, lng) {
  const stores = servingStores(tenantId, pincode, lat, lng);
  if (!stores.length) return { serviceable: false, minutes: null, store: null };
  const best = stores[0];
  const base = Number(best.eta != null ? best.eta : best.store.promise_minutes) || 10;
  const prep = Number(best.store.prep_minutes) || 0;
  return { serviceable: true, minutes: base + prep, store: best.store, source: best.source, fee: best.fee, minOrder: best.minOrder };
}

/* ---------- slot availability ---------- */
/* Slots are per store per day offset, each with a bookable capacity and a cutoff
   expressed in minutes before the window opens. A slot is bookable when it is
   open, the window has not passed, the cutoff has not passed, and capacity remains. */
function slotsFor(tenantId, storeId, dayOffset) {
  const D = db();
  const now = new Date();
  const mins = now.getHours() * 60 + now.getMinutes();
  return D.all("SELECT * FROM delivery_slots WHERE tenant_id=? AND store_id=? AND day_offset=? AND deleted_at IS NULL ORDER BY window_start",
    Number(tenantId), Number(storeId) || null, Number(dayOffset) || 0)
    .map(s => {
      const [h, m] = String(s.window_start).split(":").map(Number);
      const openAt = (h || 0) * 60 + (m || 0);
      const past = s.day_offset === 0 && openAt <= mins;
      const cutoffPassed = s.day_offset === 0 && (openAt - mins) < Number(s.cutoff_minutes || 0);
      const full = (s.booked || 0) >= (s.capacity || 0);
      return { ...s, bookable: s.status === "open" && !past && !cutoffPassed && !full, past, cutoffPassed, full };
    });
}
/* reserve one seat in a slot (capacity is the operator's own concurrency guard) */
function bookSlot(tenantId, slotId) {
  const D = db();
  const r = D.run("UPDATE delivery_slots SET booked=booked+1 WHERE id=? AND tenant_id=? AND status='open' AND booked < capacity",
    Number(slotId), Number(tenantId));
  return r.changes > 0;
}
function releaseSlot(tenantId, slotId) {
  db().run("UPDATE delivery_slots SET booked=MAX(0,booked-1) WHERE id=? AND tenant_id=?", Number(slotId), Number(tenantId));
}

/* ---------- store-inventory pinning ---------- */
/* quick-commerce must not oversell a dark store. Reserving decrements the
   sellable qty (qty − reserved − safety_stock) so a store can hold back buffer
   stock; pinning records which store an order will ship from. */
function sellable(tenantId, storeId, productId, skuId) {
  const D = db();
  const row = D.get("SELECT * FROM store_inventory WHERE tenant_id=? AND store_id=? AND product_id=? AND sku_id IS ?",
    Number(tenantId), Number(storeId), String(productId), skuId || null);
  if (!row) return 0;
  return Math.max(0, (row.qty || 0) - (row.reserved || 0) - (row.safety_stock || 0));
}
function reserve(tenantId, storeId, productId, skuId, qty) {
  const D = db();
  const n = Number(qty) || 1;
  if (sellable(tenantId, storeId, productId, skuId) < n) return false;
  D.run("UPDATE store_inventory SET reserved=reserved+? WHERE tenant_id=? AND store_id=? AND product_id=? AND sku_id IS ?",
    n, Number(tenantId), Number(storeId), String(productId), skuId || null);
  return true;
}
function release(tenantId, storeId, productId, skuId, qty) {
  db().run("UPDATE store_inventory SET reserved=MAX(0,reserved-?) WHERE tenant_id=? AND store_id=? AND product_id=? AND sku_id IS ?",
    Number(qty) || 1, Number(tenantId), Number(storeId), String(productId), skuId || null);
}
/* consume reserved stock at fulfilment (units leave the store) */
function consume(tenantId, storeId, productId, skuId, qty) {
  const D = db();
  const n = Number(qty) || 1;
  D.run("UPDATE store_inventory SET qty=MAX(0,qty-?), reserved=MAX(0,reserved-?) WHERE tenant_id=? AND store_id=? AND product_id=? AND sku_id IS ?",
    n, n, Number(tenantId), Number(storeId), String(productId), skuId || null);
}

/* pin a cart to a serving store: the promise resolves the store, then every line
   is checked for sellable qty; the caller gets back the pin or a per-line refusal */
function pinCart(tenantId, items, pincode, lat, lng) {
  const p = promise(tenantId, pincode, lat, lng);
  if (!p.serviceable) return { ok: false, reason: "not_serviceable", minutes: null };
  const short = [];
  if (p.minOrder && (Number(p.minOrder) || 0) > 0) {
    const cartValue = items.reduce((n, it) => n + (Number(it.price || it.amount || 0) || 0) * (Number(it.qty) || 1), 0);
    if (cartValue < Number(p.minOrder)) short.push({ min_order: p.minOrder, cart_value: cartValue });
  }
  const refused = [];
  for (const it of items) {
    const have = sellable(tenantId, p.store.id, it.product_id, it.sku_id);
    if (have < (it.qty || 1)) refused.push({ product_id: it.product_id, have, want: it.qty || 1 });
  }
  if (short.length) return { ok: false, reason: "below_min_order", store: p.store, minOrder: p.minOrder, short };
  if (refused.length) return { ok: false, reason: "insufficient_store_stock", store: p.store, refused };
  for (const it of items) reserve(tenantId, p.store.id, it.product_id, it.sku_id, it.qty || 1);
  return { ok: true, store: p.store, minutes: p.minutes, fee: p.fee, minOrder: p.minOrder };
}

/* ---------- dispatch: batching orders to riders + proof of delivery ---------- */
/* A dispatch run assigns a batch of orders to one rider for one slot. The OTP
   is the proof-of-delivery handshake. States come from the
   qcDispatchStatuses registry — the engine validates every transition. */
function createRun(tenantId, input) {
  const D = db();
  const status = reg().has("qcDispatchStatuses", input.status) ? input.status : "assigned";
  const orderIds = Array.isArray(input.order_ids) ? input.order_ids : J(input.order_ids, []);
  const ref = "DSP-" + Date.now().toString(36).toUpperCase().slice(-6);
  const otp = String(Math.floor(100000 + Math.random() * 900000));
  const r = D.run("INSERT INTO dispatch_runs(tenant_id,ref,store_id,slot_id,rider_id,order_ids,status,batch_count,pod_otp,notes) VALUES(?,?,?,?,?,?,?,?,?,?)",
    Number(tenantId), ref, Number(input.store_id) || null, Number(input.slot_id) || null, Number(input.rider_id) || null,
    JSON.stringify(orderIds), status, orderIds.length, otp, String(input.notes || ""));
  events().emit(tenantId, "qcommerce.dispatch.created", { ref, rider: input.rider_id, orders: orderIds.length });
  return D.get("SELECT * FROM dispatch_runs WHERE id=?", r.lastInsertRowid);
}
/* transition a run; only registry-declared states are accepted so a typo can never
   invent a fulfilment step */
function transitionRun(tenantId, runId, to, extra) {
  const D = db();
  if (!reg().has("qcDispatchStatuses", to)) throw new Error("Unknown dispatch status: " + to);
  const run = D.get("SELECT * FROM dispatch_runs WHERE id=? AND tenant_id=?", Number(runId), Number(tenantId));
  if (!run) throw new Error("Unknown dispatch run " + runId);
  D.run("UPDATE dispatch_runs SET status=? WHERE id=?", to, run.id);
  if (to === "delivered") {
    D.run("UPDATE dispatch_runs SET pod_at=datetime('now') WHERE id=?", run.id);
    const ids = J(run.order_ids, []);
    ids.forEach(id => D.run("UPDATE orders SET status='delivered' WHERE id=? AND tenant_id=?", Number(id), Number(tenantId)));
    if (run.rider_id) D.run("UPDATE riders SET deliveries=deliveries+?, status='online' WHERE id=? AND tenant_id=?", ids.length, run.rider_id, Number(tenantId));
    if (run.slot_id) ids.forEach(() => releaseSlot(tenantId, run.slot_id));
    ids.forEach(id => {
      const o = D.get("SELECT store_id FROM orders WHERE id=? AND tenant_id=?", Number(id), Number(tenantId));
      if (o && o.store_id) {
        for (const it of D.all("SELECT product_id,sku_id,qty FROM order_items WHERE order_id=?", Number(id)))
          consume(tenantId, o.store_id, it.product_id, it.sku_id, it.qty);
      }
    });
  }
  if (to === "out_for_delivery" && run.rider_id)
    D.run("UPDATE riders SET status='on_delivery' WHERE id=? AND tenant_id=?", run.rider_id, Number(tenantId));
  events().emit(tenantId, "qcommerce.dispatch." + to, { run: run.ref, otp: to === "delivered" ? undefined : run.pod_otp });
  return D.get("SELECT * FROM dispatch_runs WHERE id=?", run.id);
}
/* the customer (or the rider's device) supplies the OTP to close delivery */
function confirmPod(tenantId, runId, otp) {
  const D = db();
  const run = D.get("SELECT * FROM dispatch_runs WHERE id=? AND tenant_id=?", Number(runId), Number(tenantId));
  if (!run) throw new Error("Unknown dispatch run " + runId);
  if (run.status === "delivered") return run;
  if (!crypto.timingSafeEqual(Buffer.from(String(run.pod_otp || "").padEnd(6, "0")), Buffer.from(String(otp || "").padEnd(6, "0"))))
    throw new Error("Incorrect delivery OTP");
  return transitionRun(tenantId, runId, "delivered");
}

/* ---------- store CRUD thin layer (the generic entity API does the heavy work;
   these helpers serve the dedicated quick-commerce console views) ---------- */
function listStores(tenantId) {
  const D = db();
  return D.all("SELECT * FROM dark_stores WHERE tenant_id=? AND deleted_at IS NULL ORDER BY id DESC", Number(tenantId)).map(s => ({ ...s, service_pincodes: J(s.service_pincodes, []), service_days: J(s.service_days, []) }));
}
function listRiders(tenantId) {
  return db().all("SELECT * FROM riders WHERE tenant_id=? AND deleted_at IS NULL ORDER BY id DESC", Number(tenantId));
}
function listRuns(tenantId, status) {
  const D = db();
  const rows = status
    ? D.all("SELECT * FROM dispatch_runs WHERE tenant_id=? AND status=? ORDER BY id DESC", Number(tenantId), String(status))
    : D.all("SELECT * FROM dispatch_runs WHERE tenant_id=? ORDER BY id DESC LIMIT 200", Number(tenantId));
  return rows.map(r => ({ ...r, order_ids: J(r.order_ids, []) }));
}

/* seed a demonstration dark-store + slots so the capability is live on boot for
   the flagship store (idempotent; an operator's edits are never overwritten) */
function seedDemo(tenantId) {
  const D = db();
  if (D.get("SELECT 1 ok FROM dark_stores WHERE tenant_id=? AND code='QC-SEA-01'", Number(tenantId))) return;
  const pin = String((D.get("SELECT zip FROM tenant_state WHERE sid=(SELECT sid FROM tenant_state LIMIT 1) AND tenant_id=?", Number(tenantId)) || {}).zip || "98109");
  const r = D.run("INSERT INTO dark_stores(tenant_id,code,name,kind,city,region,pincode,country,service_radius_km,promise_minutes,prep_minutes,min_order,delivery_fee,service_pincodes,status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,'active')",
    Number(tenantId), "QC-SEA-01", "Capitol Hill Dark Store", "dark_store", "Seattle", "WA", pin, "US", 3.0, 10, 4, 15, 1.99, JSON.stringify([pin, "98101", "98102", "98112"]));
  const storeId = r.lastInsertRowid;
  /* two slots today + one tomorrow, so the storefront has a real picker */
  const now = new Date(); const mins = now.getHours() * 60 + now.getMinutes();
  const mk = (off, start, end) => D.run("INSERT INTO delivery_slots(tenant_id,store_id,day_offset,window_start,window_end,capacity,cutoff_minutes,fee,promise_minutes,status) VALUES(?,?,?,?,?,?,?,?,?,'open')",
    Number(tenantId), storeId, off, start, end, 20, 30, 1.99, 10);
  const fmt = m => String(Math.floor(m / 60) % 24).padStart(2, "0") + ":" + String(m % 60).padStart(2, "0");
  const s0 = Math.ceil((mins + 10) / 30) * 30;
  if (s0 < 22 * 60) { mk(0, fmt(s0), fmt(s0 + 30)); mk(0, fmt(s0 + 30), fmt(s0 + 60)); }
  mk(1, "09:00", "09:30"); mk(1, "18:00", "18:30");
  D.run("INSERT INTO service_areas(tenant_id,store_id,pincode,area_name,serviceable,eta_minutes,fee,min_order,cod_available,status) VALUES(?,?,?,?,?,?,?,?,1,'active')",
    Number(tenantId), storeId, pin, "Downtown", 1, 10, 1.99, 15);
  D.run("INSERT INTO riders(tenant_id,name,phone,vehicle,store_id,city,status,shift_start,shift_end,rating,deliveries) VALUES(?,?,?,?,?,?, 'online','09:00','21:00',4.8,1242)",
    Number(tenantId), "Maya Chen", "+1-555-0142", "scooter", storeId, "Seattle");
}

module.exports = {
  seedDemo, servingStores, haversine, promise,
  slotsFor, bookSlot, releaseSlot,
  sellable, reserve, release, consume, pinCart,
  createRun, transitionRun, confirmPod,
  listStores, listRiders, listRuns
};
