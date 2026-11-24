/* LUXORA Platform — shipping domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the shipping domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "shipping", routes(kit) {
  const { platformDomain, CFG, T, bad, commerceOf, emitEvent, engineFail, get, isAdmin, json, logAction, logistics, money2, ownerFor, pickup, qcommerce, requireAdmin, requirePlatform, requireStaff, run, setTenantState, shippingMod, shopperCall, stIn, stIs, states } = kit;

  function apiZip(req, res, url, s, body) {
    const zip = String(body.zip || "").trim().slice(0, 12);
    if (!zip) return bad(res, "Location required");
    setTenantState(s.sid, T(s), { zip }); s.zip = zip;
    /* the quick-commerce promise is resolved on every location set so the storefront
       can show "delivery in N minutes" or fall back to standard days */
    const qc = qcommerce.promise(T(s), zip, body.lat != null ? +body.lat : null, body.lng != null ? +body.lng : null);
    json(res, 200, { ok: true, zip, quickCommerce: qc });
  }
  /* ---- Logistics & Supply-chain (fulfilment · tracking · 3PL · returns) ---- */
  function apiShipments(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    const f = {}; if (url.searchParams.get("status")) f.status = url.searchParams.get("status"); if (url.searchParams.get("order")) f.order_id = url.searchParams.get("order");
    json(res, 200, { shipments: logistics.list(T(s), f), statuses: logistics.STATUSES });
  }
  function apiShipment(req, res, url, s, body, id) {
    if (!requireStaff(s, res)) return;
    const sh = logistics.track(T(s), Number(id));
    if (!sh) return bad(res, "Unknown shipment", 404);
    json(res, 200, { shipment: sh });
  }
  function apiShipmentCreate(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const t = T(s);
    const sh = logistics.createShipment(t, Number(body.order_id) || 0, String(body.carrier || ""), Number(body.warehouse_id) || null, body.meta || {});
    logAction(s, "logistics.shipment.create", "shipment", sh.id, { order: body.order_id, carrier: body.carrier });
    json(res, 200, { shipment: logistics.track(t, sh.id) });
  }
  function apiShipmentStatus(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try {
      const sh = logistics.transition(T(s), Number(id), String(body.status), body);
      logAction(s, "logistics.shipment.transition", "shipment", sh.id, { to: body.status });
      json(res, 200, { shipment: logistics.track(T(s), sh.id) });
    } catch (e) { bad(res, e.message); }
  }
  function apiCarriers(req, res, url, s) {
    json(res, 200, { carriers: logistics.carriers(T(s)) });
  }
  /* ============================================================
     UNIVERSAL COMMERCE HANDLERS — each handler is a thin composition over
     the commerce engines (lib/qcommerce.js, lib/fintech.js,
     lib/marketplace-ext.js, lib/trade.js); validation and state come
     from registries so nothing is hardcoded here.
     ============================================================ */
  /* ---------- Quick-commerce ---------- */
  function apiQcPromise(req, res, url, s) {
    const zip = String(url.searchParams.get("zip") || s.zip || "");
    const lat = url.searchParams.get("lat") != null ? +url.searchParams.get("lat") : null;
    const lng = url.searchParams.get("lng") != null ? +url.searchParams.get("lng") : null;
    json(res, 200, qcommerce.promise(T(s), zip, lat, lng));
  }
  function apiQcStores(req, res, url, s) {
    /* riders' names and phone numbers are staff data — the public store listing omits them */
    json(res, 200, { stores: qcommerce.listStores(T(s)), riders: (s.platform_admin || isAdmin(s)) ? qcommerce.listRiders(T(s)) : undefined });
  }
  function apiQcSlots(req, res, url, s) {
    const storeId = Number(url.searchParams.get("store")) || null;
    const day = Number(url.searchParams.get("day")) || 0;
    json(res, 200, { slots: qcommerce.slotsFor(T(s), storeId, day) });
  }
  /* pinning reserves dark-store stock, so it only ever reserves what is in the CALLER'S cart, in
     whole positive quantities within the cart limit — it used to reserve any product, any
     quantity (including negative), for an anonymous caller, as often as it was called */
  function apiQcPin(req, res, url, s, body) {
    if (!Array.isArray(body.items)) return bad(res, "items[] required");
    const maxQ = Number(CFG(s).commerce.cartMaxQty) || 10;
    const staff = !!(s.platform_admin || isAdmin(s));
    const items = [];
    for (const i of body.items) {
      const pid = String(i.product_id || i.id || "");
      const want = Math.floor(Number(i.qty) || 1);
      if (!(want >= 1)) return json(res, 200, { ok: false, reason: "invalid_quantity", product_id: pid });
      const inCart = get("SELECT qty FROM cart_items WHERE owner=? AND product_id=?", ownerFor(s), pid);
      if (!inCart && !staff) return json(res, 200, { ok: false, reason: "not_in_cart", product_id: pid });
      items.push({ product_id: pid, sku_id: i.sku_id ? Number(i.sku_id) : null, qty: Math.min(want, maxQ, inCart ? inCart.qty : maxQ) });
    }
    const zip = String(body.zip || s.zip || "");
    try {
      const pin = qcommerce.pinCart(T(s), items, zip, body.lat != null ? +body.lat : null, body.lng != null ? +body.lng : null);
      if (pin.ok) run("UPDATE cart_items SET store_id=? WHERE owner=?", pin.store.id, ownerFor(s));
      json(res, 200, pin);
    } catch (e) { bad(res, e.message); }
  }
  function apiQcReserve(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    try {
      const ok = qcommerce.reserve(T(s), Number(body.store_id), String(body.product_id), body.sku_id ? Number(body.sku_id) : null, Number(body.qty) || 1);
      json(res, 200, { ok, sellable: qcommerce.sellable(T(s), Number(body.store_id), String(body.product_id), body.sku_id ? Number(body.sku_id) : null) });
    } catch (e) { bad(res, e.message); }
  }
  /* dispatch runs carry the proof-of-delivery OTP — the code the rider collects from the
     customer. Listing them publicly let anyone read the code and mark any run delivered. */
  function apiQcRuns(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    json(res, 200, { runs: qcommerce.listRuns(T(s), url.searchParams.get("status") || "") });
  }
  function apiQcRunCreate(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    try {
      const run = qcommerce.createRun(T(s), body);
      logAction(s, "qcommerce.run.create", "dispatch_run", run.id, { ref: run.ref }, req);
      json(res, 200, { run });
    } catch (e) { bad(res, e.message); }
  }
  function apiQcRunTransition(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try {
      const run = qcommerce.transitionRun(T(s), Number(id), String(body.status), body);
      logAction(s, "qcommerce.run." + body.status, "dispatch_run", run.id, {}, req);
      json(res, 200, { run });
    } catch (e) { bad(res, e.message); }
  }
  function apiQcPod(req, res, url, s, body, id) {
    try { json(res, 200, { run: qcommerce.confirmPod(T(s), Number(id), String(body.otp || "")) }); }
    catch (e) { bad(res, e.message); }
  }
  function apiQcRiders(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    json(res, 200, { riders: qcommerce.listRiders(T(s)) });
  }
  /* pickup points the shopper may choose at checkout, with what choosing one costs */
  function apiPickupPoints(req, res, url, s) {
    const cm = commerceOf(s);
    shopperCall(res, () => {
      const t = pickup.terms(T(s));
      return { fee: money2(cm, t.fee), free_shipping_applies: t.free_shipping_applies, hold_days: t.hold_days,
        points: pickup.available(T(s), url.searchParams.get("q") || "").map(p => ({ id: p.id, code: p.code, name: p.name, kind: p.kind_row, address: p.address, city: p.city, region: p.region, postcode: p.postcode, hours: p.hours, eta_days: p.eta, lat: p.lat, lng: p.lng })) };
    });
  }
  function apiAdminPickup(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    shopperCall(res, () => ({ points: pickup.points(T(s)), reservations: pickup.reservations(T(s), { tag: url.searchParams.get("tag") || "", point_id: url.searchParams.get("point") || "" }), ...pickup.vocabulary() }));
  }
  function apiAdminPickupSave(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    try { const p = pickup.savePoint(T(s), body); logAction(s, body.id ? "pickup.point.update" : "pickup.point.create", "pickup_point", p.id, { code: p.code }, req); json(res, 200, { point: p }); }
    catch (e) { engineFail(res, e); }
  }
  function apiAdminPickupDelete(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try { const r = pickup.removePoint(T(s), id); logAction(s, "pickup.point.remove", "pickup_point", id, r, req); json(res, 200, r); } catch (e) { engineFail(res, e); }
  }
  function apiAdminPickupAct(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try { const r = pickup.act(T(s), id, String(body.action || ""), body); logAction(s, "pickup." + String(body.action || ""), "pickup_reservation", id, { status: r.status }, req); json(res, 200, { reservation: r }); }
    catch (e) { engineFail(res, e); }
  }
  function apiAdminPickupSweep(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    shopperCall(res, () => pickup.expireDue(T(s)));
  }
  /* ========== Shipping & Tracking APIs ========== */
  /* carrier provider rows are platform-wide and hold credentials: listing is staff-only and
     never returns the config; configuring is a platform write. Tracking is per store. */
  function apiShippingProviders(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    json(res, 200, { providers: shippingMod.getProviders(T(s)) });
  }
  function apiShippingProviderConfig(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    const r = shippingMod.updateProviderConfig((body || {}).provider_id, (body || {}).config);
    if (r.error) return bad(res, r.error, r.code || 400);
    logAction(s, "shipping.provider_config", "shipping_provider", null, { provider: r.provider_id }, req);
    json(res, 200, { ok: true, provider: r });
  }
  /* the platform console's carrier accounts: every row, which keys are on file, and the
     public webhook address when one is configured (the console falls back to its own origin) */
  function apiPlatformShippingProviders(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    const base = platformDomain();
    json(res, 200, { providers: shippingMod.listProviders(), public_url: base ? "https://" + base : null });
  }
  function apiPlatformShippingDisconnect(req, res, url, s, body, providerId) {
    if (!requirePlatform(s, res)) return;
    const r = shippingMod.disconnectProvider(providerId);
    if (r.error) return bad(res, r.error, r.code || 400);
    logAction(s, "shipping.provider_disconnect", "shipping_provider", null, { provider: r.provider_id }, req);
    json(res, 200, { ok: true, provider: r });
  }
  function apiShippingTrack(req, res, url, s, body) {
    if (!requireStaff(s, res)) return;
    const r = shippingMod.createTracking(T(s), body || {});
    if (r.error) return bad(res, r.error, r.code || 400);
    json(res, 200, { tracking_number: r.tracking_number, tracking: r });
  }
  /* staff, or the customer whose order the parcel ships */
  function apiShippingTrackGet(req, res, url, s, body, trackingNumber) {
    const r = shippingMod.track(T(s), trackingNumber);
    if (r.error) return bad(res, 'tracking not found', 404);
    if (!s.platform_admin && !isAdmin(s)) {
      const o = r.order_id ? get("SELECT owner FROM orders WHERE id=? AND tenant_id=?", r.order_id, T(s)) : null;
      if (!o || o.owner !== ownerFor(s)) return bad(res, 'tracking not found', 404);
    }
    json(res, 200, { tracking: r });
  }
  /* staff rate a parcel: origin is the store's ship-from address (settings
     commerce.shipFrom) unless the request names one; the destination is the order's own
     shipping address when an order is given */
  async function apiShippingQuote(req, res, url, s, body) {
    if (!requireStaff(s, res)) return;
    const b = body || {};
    let to = b.to;
    if (!to && b.order_id != null) {
      const o = get("SELECT name, address, city, state, zip, status FROM orders WHERE id=? AND tenant_id=?", Number(b.order_id), T(s));
      if (!o) return bad(res, "Unknown order", 404);
      if (stIs("order", o.status, "not_shippable")) return bad(res, stIs("order", o.status, "aborted") ? "This order is cancelled" : "This order is not paid yet", 409);
      to = { name: o.name, street1: o.address, city: o.city, state: o.state, zip: o.zip, country: CFG(s).commerce.country.toUpperCase() };
    }
    const r = await shippingMod.getQuote(T(s), { ...b, to, from: b.from || CFG(s).commerce.shipFrom });
    if (r.error) return bad(res, r.error, r.code || 400);
    json(res, 200, r);
  }
  async function apiShippingLabel(req, res, url, s, body) {
    if (!requireStaff(s, res)) return;
    const r = await shippingMod.saveLabel(T(s), body || {});
    if (r.error) return bad(res, r.error, r.code || 400);
    logAction(s, "shipping.label", "order", r.order_num || null, { tracking: r.tracking_number, carrier: r.carrier, price: r.price }, req);
    if (r.order_id) {
      /* a label means the parcel is on its way: a processing order moves to shipped */
      const sh = stIn("order", "shippable");
      run("UPDATE orders SET status=? WHERE id=? AND tenant_id=? AND status IN " + sh.sql, states.first("order", "in_transit"), r.order_id, T(s), ...sh.args);
      const o = get("SELECT owner, num FROM orders WHERE id=? AND tenant_id=?", r.order_id, T(s));
      const uid = o && /^t\d+:u:(\d+)$/.exec(o.owner || "");
      const buyer = uid ? get("SELECT email FROM users WHERE id=? AND tenant_id=?", Number(uid[1]), T(s)) : null;
      if (buyer && buyer.email) require("../mailer.js").deliver({ tenantId: T(s), channel: "email", to: buyer.email, kind: "order_shipped",
        subject: `Order ${o.num} has shipped`, text: `Your order ${o.num} is on its way with ${r.carrier} (${r.service}).\nTracking number: ${r.tracking_number}` });
      emitEvent(T(s), "order.shipped", { num: o && o.num, tracking: r.tracking_number, carrier: r.carrier }, o && o.num);
    }
    json(res, 200, r);
  }
  /* the labels already bought for an order, so the console offers them instead of a second purchase */
  function apiShippingOrderLabels(req, res, url, s, body, orderId) {
    if (!requireStaff(s, res)) return;
    const o = get("SELECT id, num, status FROM orders WHERE id=? AND tenant_id=?", Number(orderId), T(s));
    if (!o) return bad(res, "Unknown order", 404);
    json(res, 200, { order: o, labels: shippingMod.listTracking(T(s), o.id).map(t => ({ tracking_number: t.tracking_number, carrier: t.carrier_type, service: t.service_type, status: t.status, label_url: t.label_url, created_at: t.created_at })) });
  }
  /* carrier tracking webhooks: signature first, then the parcel advances */
  function apiShippingWebhook(req, res, url, s, body, provider) {
    const raw = typeof req.rawBody === "string" ? req.rawBody : JSON.stringify(body || {});
    if (!shippingMod.verifyWebhook(provider, raw, req.headers)) return bad(res, "signature invalid", 401);
    const r = shippingMod.handleWebhook(provider, body || {});
    if (r.error) return json(res, 200, { ok: true, ignored: r.error });
    if (r.order_id && /^delivered$/.test(r.status)) emitEvent(r.tenant_id, "order.delivered", { order_id: r.order_id }, null);
    json(res, 200, { ok: true });
  }

  const DW = () => require("../delivery-windows.js"), SA = () => require("../serviceable-areas.js");
  /* the delivery times a shopper may choose now */
  function apiDeliverySlots(req, res, url, s) { shopperCall(res, () => ({ slots: DW().on(T(s)) ? DW().choices(T(s)).map(x => ({ ...x, fee: money2(commerceOf(s), x.fee) })) : [] })); }
  /* the store's weekly delivery windows and what is booked */
  function apiAdminWindows(req, res, url, s) { if (requireStaff(s, res)) shopperCall(res, () => ({ on: DW().on(T(s)), windows: DW().windows(T(s)), schedule: DW().schedule(T(s), url.searchParams.get("day")) })); }
  /* adds or changes a delivery window */
  function apiAdminWindowSave(req, res, url, s, body) { if (requireAdmin(s, res)) shopperCall(res, () => ({ windows: DW().save(T(s), body) })); }
  /* removes a delivery window */
  function apiAdminWindowDelete(req, res, url, s, body, id) { if (requireAdmin(s, res)) shopperCall(res, () => ({ windows: DW().remove(T(s), id) })); }
  /* whether the store delivers to a postcode */
  function apiServiceable(req, res, url, s) { shopperCall(res, () => SA().check(T(s), url.searchParams.get("zip"))); }
  /* the areas the store delivers to */
  function apiAdminAreas(req, res, url, s) { if (requireStaff(s, res)) shopperCall(res, () => ({ on: SA().on(T(s)), areas: SA().list(T(s)) })); }
  /* adds or changes an area */
  function apiAdminAreaSave(req, res, url, s, body) { if (requireAdmin(s, res)) shopperCall(res, () => ({ areas: SA().save(T(s), body) })); }
  /* removes an area */
  function apiAdminAreaDelete(req, res, url, s, body, id) { if (requireAdmin(s, res)) shopperCall(res, () => ({ areas: SA().remove(T(s), id) })); }

  return [
    ["GET /api/shipping/slots", apiDeliverySlots],
    ["GET /api/shipping/serviceable", apiServiceable],
    ["GET /api/admin/delivery-windows", apiAdminWindows],
    ["POST /api/admin/delivery-windows", apiAdminWindowSave],
    ["DELETE /api/admin/delivery-windows/:id", (r, re, u, s, b, p) => apiAdminWindowDelete(r, re, u, s, b, p)],
    ["GET /api/admin/serviceable-areas", apiAdminAreas],
    ["POST /api/admin/serviceable-areas", apiAdminAreaSave],
    ["DELETE /api/admin/serviceable-areas/:id", (r, re, u, s, b, p) => apiAdminAreaDelete(r, re, u, s, b, p)],
    ["GET /api/qc/promise", apiQcPromise],
    ["GET /api/qc/stores", apiQcStores],
    ["GET /api/qc/slots", apiQcSlots],
    ["POST /api/qc/pin", apiQcPin],
    ["POST /api/qc/reserve", apiQcReserve],
    ["GET /api/qc/runs", apiQcRuns],
    ["POST /api/qc/runs", apiQcRunCreate],
    ["POST /api/qc/runs/:id", (r, re, u, s, b, p) => apiQcRunTransition(r, re, u, s, b, p)],
    ["POST /api/qc/runs/:id/pod", (r, re, u, s, b, p) => apiQcPod(r, re, u, s, b, p)],
    ["GET /api/qc/riders", apiQcRiders],
    ["GET /api/pickup/points", apiPickupPoints],
    ["GET /api/admin/pickup", apiAdminPickup],
    ["POST /api/admin/pickup/points", apiAdminPickupSave],
    ["DELETE /api/admin/pickup/points/:id", (r, re, u, s, b, p) => apiAdminPickupDelete(r, re, u, s, b, p)],
    ["POST /api/admin/pickup/reservations/:id", (r, re, u, s, b, p) => apiAdminPickupAct(r, re, u, s, b, p)],
    ["POST /api/admin/pickup/sweep", apiAdminPickupSweep],
    ["POST /api/zip", apiZip],
    ["GET /api/shipments", apiShipments],
    ["GET /api/shipments/:id", (r, re, u, s, b, p) => apiShipment(r, re, u, s, b, p)],
    ["POST /api/admin/shipments", apiShipmentCreate],
    ["PUT /api/admin/shipments/:id/status", (r, re, u, s, b, p) => apiShipmentStatus(r, re, u, s, b, p)],
    ["GET /api/carriers", apiCarriers],
    ["GET /api/shipping/providers", apiShippingProviders],
    ["POST /api/shipping/providers/config", apiShippingProviderConfig],
    ["GET /api/platform/shipping/providers", apiPlatformShippingProviders],
    ["POST /api/platform/shipping/providers/:id/disconnect", (r, re, u, s, b, p) => apiPlatformShippingDisconnect(r, re, u, s, b, p)],
    ["POST /api/shipping/track", apiShippingTrack],
    ["GET /api/shipping/track/:trackingNumber", apiShippingTrackGet],
    ["POST /api/shipping/quote", apiShippingQuote],
    ["POST /api/shipping/label", apiShippingLabel],
    ["GET /api/shipping/orders/:id/labels", (r, re, u, s, b, p) => apiShippingOrderLabels(r, re, u, s, b, p)],
    ["POST /api/shipping/webhook/:provider", (r, re, u, s, b, p) => apiShippingWebhook(r, re, u, s, b, p)]
  ];
} };
