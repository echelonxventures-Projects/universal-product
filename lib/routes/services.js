/* LUXORA Platform — services domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the services domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "services", routes(kit) {
  const { T, bookings, engineFail, json, logAction, ownerFor, requireAdmin, requireStaff, sessionActor, sessions, shopperCall, signedIn } = kit;

  /* charged by the minute (lib/media-sessions.js, capability per_minute_billing) */
  function apiAdminPerMinute(req, res, url, s) { if (requireStaff(s, res)) shopperCall(res, () => require("../media-sessions.js").charges(T(s))); }
  function apiSessionsMine(req, res, url, s) { if (signedIn(s, res, "see your sessions")) shopperCall(res, () => ({ sessions: sessions().mine(T(s), sessionActor(s)), ...sessions().vocabulary(T(s)) })); }
  function apiSessionOpen(req, res, url, s, body) { if (signedIn(s, res, "start a session")) shopperCall(res, () => ({ session: sessions().forBooking(T(s), body.booking, sessionActor(s)) })); }
  function apiSessionJoin(req, res, url, s, body, id) { if (signedIn(s, res, "join a session")) shopperCall(res, () => sessions().join(T(s), id, sessionActor(s))); }
  function apiSessionSignal(req, res, url, s, body, id) { if (signedIn(s, res, "join a session")) shopperCall(res, () => sessions().signal(T(s), id, sessionActor(s), body)); }
  function apiSessionSignals(req, res, url, s, body, id) { if (signedIn(s, res, "join a session")) shopperCall(res, () => ({ signals: sessions().signals(T(s), id, sessionActor(s), url.searchParams.get("since")) })); }
  function apiSessionEnd(req, res, url, s, body, id) { if (signedIn(s, res, "end a session")) shopperCall(res, () => ({ session: sessions().end(T(s), id, sessionActor(s)) })); }
  /* bookings */
  function apiBookingAvailability(req, res, url, s) {
    const q = Object.fromEntries(url.searchParams.entries());
    shopperCall(res, () => ({ slots: bookings.availability(T(s), q.product, q) }));
  }
  function apiBookingHold(req, res, url, s, body) { if (signedIn(s, res, "book")) shopperCall(res, () => ({ booking: bookings.hold(T(s), ownerFor(s), body) })); }
  function apiBookingsMine(req, res, url, s) { if (signedIn(s, res, "see your bookings")) shopperCall(res, () => ({ bookings: bookings.mine(T(s), ownerFor(s)) })); }
  function apiBookingCancel(req, res, url, s, body, id) { if (signedIn(s, res, "manage bookings")) shopperCall(res, () => ({ booking: bookings.cancelMine(T(s), ownerFor(s), id) })); }
  function apiAdminBookings(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    shopperCall(res, () => ({ bookings: bookings.list(T(s), { resource_id: url.searchParams.get("resource"), from: url.searchParams.get("from"), to: url.searchParams.get("to") }),
      resources: bookings.resources(T(s)), ...bookings.vocabulary() }));
  }
  function apiAdminBookingResource(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    try { const r = bookings.saveResource(T(s), body); logAction(s, "bookings.resource.save", "booking_resource", r.id, { code: r.code }, req); json(res, 200, { resource: r }); } catch (e) { engineFail(res, e); }
  }
  function apiAdminBookingProduct(req, res, url, s, body, pid) {
    if (!requireAdmin(s, res)) return;
    shopperCall(res, () => (req.method === "DELETE" ? bookings.unconfigure(T(s), pid) : { config: bookings.configure(T(s), pid, body) }));
  }
  function apiAdminBookingProductGet(req, res, url, s, body, pid) { if (requireStaff(s, res)) shopperCall(res, () => ({ config: bookings.configOf(T(s), pid) })); }
  function apiAdminBookingAct(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try { const b = bookings.act(T(s), id, String(body.action || "")); logAction(s, "bookings." + String(body.action || ""), "booking", id, { status: b.status }, req); json(res, 200, { booking: b }); } catch (e) { engineFail(res, e); }
  }
  function apiAdminBookingSweep(req, res, url, s) { if (requireAdmin(s, res)) shopperCall(res, () => bookings.expireDue(T(s))); }

  return [
    ["GET /api/bookings/availability", apiBookingAvailability],
    ["POST /api/bookings/hold", apiBookingHold],
    ["GET /api/bookings", apiBookingsMine],
    ["POST /api/bookings/:id/cancel", (r, re, u, s, b, p) => apiBookingCancel(r, re, u, s, b, p)],
    ["GET /api/admin/per-minute", apiAdminPerMinute],
    ["GET /api/sessions", apiSessionsMine],
    ["POST /api/sessions", apiSessionOpen],
    ["POST /api/sessions/:id/join", (r, re, u, s, b, p) => apiSessionJoin(r, re, u, s, b, p)],
    ["POST /api/sessions/:id/signal", (r, re, u, s, b, p) => apiSessionSignal(r, re, u, s, b, p)],
    ["GET /api/sessions/:id/signals", (r, re, u, s, b, p) => apiSessionSignals(r, re, u, s, b, p)],
    ["POST /api/sessions/:id/end", (r, re, u, s, b, p) => apiSessionEnd(r, re, u, s, b, p)],
    ["GET /api/admin/bookings", apiAdminBookings],
    ["POST /api/admin/bookings/resources", apiAdminBookingResource],
    ["GET /api/admin/bookings/products/:pid", (r, re, u, s, b, p) => apiAdminBookingProductGet(r, re, u, s, b, p)],
    ["PUT /api/admin/bookings/products/:pid", (r, re, u, s, b, p) => apiAdminBookingProduct(r, re, u, s, b, p)],
    ["DELETE /api/admin/bookings/products/:pid", (r, re, u, s, b, p) => apiAdminBookingProduct(r, re, u, s, b, p)],
    ["POST /api/admin/bookings/sweep", apiAdminBookingSweep],
    ["POST /api/admin/bookings/:id", (r, re, u, s, b, p) => apiAdminBookingAct(r, re, u, s, b, p)]
  ];
} };
