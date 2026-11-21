/* LUXORA Platform — payments domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the payments domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "payments", routes(kit) {
  const { CFG, T, all, applyPaymentStatus, bad, connect, emitEvent, enabledCarriers, enabledNotifiers, enterprise, fintech, gatewaySecrets, get, handle, json, logAction, offers, ownerFor, paymentRegistry, reconcilePayment, registry, requireAdmin, requireSection, run, sec, stIn, stIs, states } = kit;

  function apiAdminGateways(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    const t = T(s);
    const c = CFG(s);
    const country = registry.countryProfile(CFG(s).commerce.country);
    const reg = paymentRegistry(t);
    const rows = all("SELECT * FROM tenant_gateways WHERE tenant_id=? AND provider_id NOT LIKE 'ship:%' AND provider_id NOT LIKE 'notify:%' ORDER BY position", t);
    const known = new Set(rows.map(r => r.provider_id));
    const list = rows.map(r => {
      const p = reg.find(x => x.id === r.provider_id) || { id: r.provider_id, name: r.provider_id, emoji: "🔌", methods: ["card"], feePct: 0, fields: [] };
      let cfg = {}; try { cfg = JSON.parse(r.config || "{}"); } catch (e) { }
      cfg = sec.unsealConfig(t, r.provider_id, JSON.stringify(cfg));
      const masked = {};
      for (const [k, v] of Object.entries(cfg)) masked[k] = (p.fields || []).some(f => f.key === k && f.secret) ? (v ? "••••" + String(v).slice(-4) : "") : v;
      return { id: p.id, name: p.name, emoji: p.emoji, desc: p.desc, methods: p.methods, feePct: p.feePct, feeFixed: p.feeFixed, fields: p.fields, enabled: !!r.enabled, primary: !!r.is_primary, mode: r.mode, config: masked, available: registry.supports(p.id, country.code) };
    });
    for (const p of reg) if (!known.has(p.id) && registry.supports(p.id, country.code))
      list.push({ id: p.id, name: p.name, emoji: p.emoji, desc: p.desc, methods: p.methods, feePct: p.feePct, feeFixed: p.feeFixed, fields: p.fields, enabled: false, primary: false, mode: "sandbox", config: {}, available: true });
    json(res, 200, { gateways: list, country: { code: country.code, name: country.name, currency: country.currency }, carriers: enabledCarriers(t), notifiers: enabledNotifiers(t).map(n => ({ id: n.id, name: n.name, emoji: n.emoji })) });
  }
  function apiAdminGatewaysPut(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    if (!requireSection(s, res, "payments", "write")) return;
    const t = T(s);
    const list = Array.isArray(body.gateways) ? body.gateways : [];
    /* the console only ever holds masked secrets; a masked (or omitted) value on save keeps
       the stored one — deleting and re-inserting the list used to drop every key on re-save */
    const prior = {};
    for (const r of all("SELECT provider_id, config FROM tenant_gateways WHERE tenant_id=? AND provider_id NOT LIKE 'ship:%' AND provider_id NOT LIKE 'notify:%'", t)) { try { prior[r.provider_id] = JSON.parse(r.config || "{}"); } catch (e) { prior[r.provider_id] = {}; } }
    run("DELETE FROM tenant_gateways WHERE tenant_id=? AND provider_id NOT LIKE 'ship:%' AND provider_id NOT LIKE 'notify:%'", t);
    list.forEach((g, i) => {
      const cfg = {};
      const was = prior[String(g.id)] || {};
      for (const [k, v] of Object.entries(was)) if (!(g.config && k in g.config && g.config[k] !== "" && !String(g.config[k]).startsWith("••••"))) cfg[k] = v;
      for (const [k, v] of Object.entries(g.config || {})) if (v && !String(v).startsWith("••••") && !String(v).startsWith("lux.v1.")) cfg[k] = sec.encryptSecret(v, T(s) + "|" + g.id + "|" + k);
      const defP = paymentRegistry(t).find(x => x.id === g.id) || { fields: [] };
    const secretKeys = (defP.fields || []).filter(f => f.secret).map(f => f.key);
    for (const k of secretKeys) if (cfg[k] && !String(cfg[k]).startsWith("lux.v1.")) cfg[k] = sec.encryptSecret(cfg[k], t + "|" + g.id + "|" + k);
    run("INSERT INTO tenant_gateways(tenant_id,provider_id,enabled,is_primary,mode,config,position) VALUES(?,?,?,?,?,?,?)",
      t, String(g.id), g.enabled ? 1 : 0, g.primary ? 1 : 0, g.mode === "live" ? "live" : "sandbox", JSON.stringify(cfg), i);
    });
    logAction(s, "gateways.update", "gateway", null, { count: list.length });
    json(res, 200, { ok: true });
  }
  function apiAdminGatewayTest(req, res, url, s, body, id) {
    return (async () => {
    if (!requireAdmin(s, res)) return;
    const gw = paymentRegistry(T(s)).find(x => x.id === id);
    if (!gw) return bad(res, "Unknown gateway", 404);
    const row = get("SELECT * FROM tenant_gateways WHERE tenant_id=? AND provider_id=?", T(s), id);
    let cfg = sec.unsealConfig(T(s), id, (row && row.config) || "{}");
    const missing = (gw.fields || []).filter(f => !cfg[f.key] || String(cfg[f.key]).startsWith("••••"));
    const ok = missing.length === 0;
    let detail = "";
    if (ok && row.mode === "live") {
      const ping = await connect.ping({ provider: id, config: cfg });
      if (ping.live && !ping.ok) return json(res, 200, { ok: false, message: `Live verification failed: ${ping.error}` });
      detail = ping.live ? " (checked with the provider)" : "";
    }
    logAction(s, "gateway.test", "gateway", id, { ok, mode: row && row.mode });
    json(res, 200, { ok, message: ok ? `✓ ${gw.name} ${row.mode === "live" ? "live" : "sandbox"} connection verified${detail}` : `Missing credentials: ${missing.map(m => m.label).join(", ")}` });
    })();
  }
  function apiAdminPayments(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    /* each row says what can be done with it: a live pending payment can be checked with its
       gateway, one settled offline (the offlinePaymentMethods registry) recorded as received */
    const offline = registry.list("offlinePaymentMethods").map(m => typeof m === "string" ? m : m.key);
    const rows = all("SELECT p.*, o.num order_num, o.status order_status FROM payments p LEFT JOIN orders o ON o.id=p.order_id WHERE p.tenant_id=? ORDER BY p.created_at DESC, p.id DESC LIMIT 200", T(s));
    json(res, 200, { payments: rows.map(p => ({ ...p, offline: !p.live && offline.includes(String(p.method)) })) });
  }
  async function apiAdminPaymentRefund(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    const p = get("SELECT * FROM payments WHERE id=? AND tenant_id=?", Number(id), T(s));
    if (!p) return bad(res, "Unknown payment", 404);
    if (!stIs("payment", p.status, "refundable")) return bad(res, "Only captured payments can be refunded");
    /* money taken by a real gateway goes back through that gateway; only a simulated (or an
       explicitly manual, refunded-elsewhere) payment is marked refunded without a call */
    let gatewayRefund = null;
    if (p.live && !body.manual) {
      const live = gatewaySecrets(T(s), p.gateway);
      if (!live || !p.provider_payment_id) return bad(res, "This payment can't be refunded through " + p.gateway + " from here — refund it in the gateway's dashboard, then record it with manual: true", 409);
      const r = await connect.refund({ provider: p.gateway, config: live.cfg, paymentId: p.provider_payment_id, amount: p.amount, currency: p.currency, idempotency: "refund-" + p.id });
      if (!r.live) return bad(res, "Refund not sent (" + (r.reason || "gateway offline") + ")", 503);
      if (!r.ok || stIs("payment", r.status, "failure")) return bad(res, "The gateway refused the refund: " + (r.error || r.status), 502);
      gatewayRefund = { id: r.id, status: r.status };
    }
    const rf = stIn("payment", "refundable");
    const claim = run("UPDATE payments SET status=? WHERE id=? AND status IN " + rf.sql, states.first("payment", "reversed"), p.id, ...rf.args);
    if (!claim.changes) return bad(res, "Only captured payments can be refunded", 409);
    let claw = null; if (p.order_id) { const ord = get("SELECT num FROM orders WHERE id=?", p.order_id); try { claw = offers.reverseRedemption(T(s), { order_id: p.order_id, order_num: ord && ord.num }); } catch (e) { console.error("clawback:", e.message); } }
    logAction(s, "payment.refund", "payment", p.id, { amount: p.amount, gateway: p.gateway, clawback: claw && claw.voided, gateway_refund: gatewayRefund, manual: !!(p.live && body.manual) });
    if (p.order_id) { const onum = (get("SELECT num FROM orders WHERE id=?", p.order_id) || {}).num; emitEvent(T(s), "order.refunded", { payment_id: p.id, amount: p.amount, num: onum }, onum); }
    json(res, 200, { ok: true, clawback: claw && claw.voided || 0, gateway_refund: gatewayRefund });
  }
  function apiGatewayPreview(req, res, url, s, body, id) { if (!requireAdmin(s, res)) return; json(res, 200, enterprise.gatewayPreview(String(id || ""), T(s))); }
  /* staff: ask the gateway now (live), or record money received offline (cash, a transfer) */
  async function apiAdminPaymentReconcile(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    if (!requireSection(s, res, "payments", "write")) return;
    const p = get("SELECT * FROM payments WHERE id=? AND tenant_id=?", Number(id), T(s));
    if (!p) return bad(res, "Unknown payment", 404);
    if (!p.live) return bad(res, "This payment was not taken through a live gateway — record it as received if the money arrived", 409);
    const r = await reconcilePayment(p, "console");
    logAction(s, "payment.reconcile", "payment", p.id, { gateway: p.gateway, result: r.status || r.reason }, req);
    if (!r.ok && r.reason) return bad(res, "Could not check with " + p.gateway + ": " + r.reason, 502);
    json(res, 200, { ok: true, result: r, payment: get("SELECT * FROM payments WHERE id=?", p.id) });
  }
  function apiAdminPaymentReceived(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    if (!requireSection(s, res, "payments", "write")) return;
    const p = get("SELECT * FROM payments WHERE id=? AND tenant_id=?", Number(id), T(s));
    if (!p) return bad(res, "Unknown payment", 404);
    const offline = registry.list("offlinePaymentMethods").map(m => typeof m === "string" ? m : m.key);
    if (p.live || !offline.includes(String(p.method))) return bad(res, "Only a payment settled offline (" + offline.join(", ") + ") is recorded by hand — a gateway payment is confirmed by its gateway", 409);
    const r = applyPaymentStatus(p, { status: states.first("payment", "settled") }, p.gateway, "manual");
    if (r.unchanged) return bad(res, "This payment is already " + r.status, 409);
    logAction(s, "payment.received", "payment", p.id, { method: p.method, amount: p.amount, note: String((body && body.note) || "").slice(0, 200) }, req);
    json(res, 200, { ok: true, payment: get("SELECT * FROM payments WHERE id=?", p.id) });
  }
  /* ---------- Fintech ---------- */
  function apiFinUpi(req, res, url, s) {
    json(res, 200, fintech.upi(T(s), ownerFor(s)));
  }
  function apiFinUpiAdd(req, res, url, s, body) {
    if (!body.vpa) return bad(res, "VPA required");
    json(res, 200, { handle: fintech.addUpi(T(s), ownerFor(s), String(body.vpa), body.name) });
  }
  function apiFinUpiCollect(req, res, url, s, body) {
    try { json(res, 200, { collect: fintech.collectUpi(T(s), ownerFor(s), String(body.payer_vpa || ""), body.amount, body.currency, body.note) }); }
    catch (e) { bad(res, e.message); }
  }
  function apiFinUpiSettle(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { collect: fintech.settleCollect(T(s), Number(id), body.failed ? false : true) }); }
    catch (e) { bad(res, e.message); }
  }
  function apiFinQrCreate(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { qr: fintech.createQr(T(s), body) }); } catch (e) { bad(res, e.message); }
  }
  function apiFinQrScan(req, res, url, s, body, id) {
    try { json(res, 200, { qr: fintech.scanQr(T(s), Number(id)) }); } catch (e) { bad(res, e.message); }
  }
  function apiFinLinkCreate(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { link: fintech.createLink(T(s), body) }); } catch (e) { bad(res, e.message); }
  }
  function apiFinLinkPay(req, res, url, s, body, token) {
    try { json(res, 200, { link: fintech.payLink(T(s), String(token)) }); } catch (e) { bad(res, e.message); }
  }
  function apiFinMandateRegister(req, res, url, s, body) {
    try { json(res, 200, { mandate: fintech.registerMandate(T(s), { ...body, owner: ownerFor(s) }) }); }
    catch (e) { bad(res, e.message); }
  }
  function apiFinMandateCharge(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { mandate: fintech.chargeMandate(T(s), Number(id), body.amount) }); }
    catch (e) { bad(res, e.message); }
  }
  function apiFinEscrowHold(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { escrow: fintech.hold(T(s), body.order_id, ownerFor(s), String(body.seller || ""), body.amount, body.currency, body.meta) }); }
    catch (e) { bad(res, e.message); }
  }
  function apiFinEscrowRelease(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { escrow: fintech.releaseEscrow(T(s), Number(id)) }); } catch (e) { bad(res, e.message); }
  }
  function apiFinEscrowDispute(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { escrow: fintech.disputeEscrow(T(s), Number(id), body.open === false ? false : true) }); }
    catch (e) { bad(res, e.message); }
  }
  function apiFinSplit(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { split: fintech.splitPayment(T(s), body.payment_id, body.order_id, body.amount, body.splits) }); }
    catch (e) { bad(res, e.message); }
  }

  return [
    ["GET /api/fintech/upi", apiFinUpi],
    ["POST /api/fintech/upi", apiFinUpiAdd],
    ["POST /api/fintech/upi/collect", apiFinUpiCollect],
    ["POST /api/fintech/upi/collect/:id", (r, re, u, s, b, p) => apiFinUpiSettle(r, re, u, s, b, p)],
    ["POST /api/fintech/qr", apiFinQrCreate],
    ["POST /api/fintech/qr/:id/scan", (r, re, u, s, b, p) => apiFinQrScan(r, re, u, s, b, p)],
    ["POST /api/fintech/links", apiFinLinkCreate],
    ["POST /api/fintech/links/:token/pay", (r, re, u, s, b, p) => apiFinLinkPay(r, re, u, s, b, p)],
    ["POST /api/fintech/mandates", apiFinMandateRegister],
    ["POST /api/fintech/mandates/:id/charge", (r, re, u, s, b, p) => apiFinMandateCharge(r, re, u, s, b, p)],
    ["POST /api/fintech/escrow", apiFinEscrowHold],
    ["POST /api/fintech/escrow/:id/release", (r, re, u, s, b, p) => apiFinEscrowRelease(r, re, u, s, b, p)],
    ["POST /api/fintech/escrow/:id/dispute", (r, re, u, s, b, p) => apiFinEscrowDispute(r, re, u, s, b, p)],
    ["POST /api/fintech/splits", apiFinSplit],
    ["GET /api/admin/gateways", apiAdminGateways],
    ["PUT /api/admin/gateways", apiAdminGatewaysPut],
    ["POST /api/admin/gateways/:id/test", (r, re, u, s, b, p) => apiAdminGatewayTest(r, re, u, s, b, p)],
    ["GET /api/admin/payments", apiAdminPayments],
    ["POST /api/admin/payments/:id/refund", (r, re, u, s, b, p) => apiAdminPaymentRefund(r, re, u, s, b, p)],
    ["POST /api/admin/payments/:id/reconcile", (r, re, u, s, b, p) => apiAdminPaymentReconcile(r, re, u, s, b, p)],
    ["POST /api/admin/payments/:id/received", (r, re, u, s, b, p) => apiAdminPaymentReceived(r, re, u, s, b, p)],
    ["POST /api/admin/gateway/preview/:id", (r, re, u, s, b, p) => apiGatewayPreview(r, re, u, s, b, p)]
  ];
} };
