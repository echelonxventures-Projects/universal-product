/* LUXORA Platform — trade domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the trade domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "trade", routes(kit) {
  const { CFG, J, T, all, bad, get, isAdmin, json, logAction, newRef, notify, ownerFor, requireAdmin, rl, run, states, trade } = kit;

  function apiRfqCreate(req, res, url, s, body) {
    const p = get("SELECT id,title FROM products WHERE tenant_id=? AND id=?", T(s), body.product_id);
    if (!p) return bad(res, "Unknown product", 404);
    const ref = "RFQ-" + (1000 + get("SELECT COUNT(*) c FROM rfqs WHERE tenant_id=?", T(s)).c + 1);
    run("INSERT INTO rfqs(tenant_id,ref,product_id,buyer_name,buyer_email,qty,target_price,currency,status) VALUES(?,?,?,?,?,?,?,?, 'open')",
      T(s), ref, p.id, String(body.buyer_name || ""), String(body.buyer_email || ""), Number(body.qty) || 1, Number(body.target_price) || 0, CFG(s).commerce.currency);
    logAction(s, "rfq.create", "rfq", ref, { product: p.id, qty: body.qty });
    notify(T(s), `New ${ref}`, `${body.buyer_name} requests ${body.qty} × ${p.title}`);
    json(res, 200, { ok: true, ref });
  }
  function apiAdminRfqs(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { rfqs: all("SELECT * FROM rfqs WHERE tenant_id=? ORDER BY created_at DESC", T(s)).map(r => ({ ...r, quotes: J(r.quotes, []) })) });
  }
  function apiAdminRfqUpdate(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    const r = get("SELECT * FROM rfqs WHERE id=? AND tenant_id=?", Number(id), T(s));
    if (!r) return bad(res, "Unknown RFQ", 404);
    const quotes = J(r.quotes, []);
    if (body.quote) quotes.push({ ...body.quote, at: new Date().toISOString() });
    run("UPDATE rfqs SET status=?, quotes=? WHERE id=?", states.has("rfq", body.status) ? body.status : r.status, JSON.stringify(quotes), r.id);
    logAction(s, "rfq.update", "rfq", r.ref, { status: body.status });
    json(res, 200, { ok: true });
  }
  function apiAdminContractCreate(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    if (!body.buyer_name || !body.buyer_email) return bad(res, "Buyer name and email required");
    const inc = rl("incoterms"), pt = rl("paymentTerms"), cs = rl("contractStatuses");
    const ref = newRef("CT");
    run("INSERT INTO contracts(tenant_id,ref,buyer_name,buyer_email,buyer_org,supplier_id,product_ids,currency,pricing,min_qty,incoterms,payment_terms,valid_from,valid_to,status,notes) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
      T(s), ref, String(body.buyer_name), String(body.buyer_email), String(body.buyer_org || ""), body.supplier_id ? Number(body.supplier_id) : null,
      JSON.stringify(body.product_ids || []), String(body.currency || require("../defaults.js").currency(T(s))), JSON.stringify(body.pricing || {}), Number(body.min_qty) || 1,
      inc.includes(body.incoterms) ? body.incoterms : "EXW", pt.includes(body.payment_terms) ? body.payment_terms : "net30", body.valid_from || null, body.valid_to || null,
      cs.includes(body.status) ? body.status : "active", String(body.notes || ""));
    const id = Number(get("SELECT id FROM contracts WHERE tenant_id=? AND ref=?", T(s), ref).id);
    logAction(s, "contract.create", "contract", ref);
    json(res, 200, { ok: true, id, ref });
  }
  function apiAdminContractStatus(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    if (!rl("contractStatuses").includes(body.status)) return bad(res, "Invalid status");
    const r = run("UPDATE contracts SET status=? WHERE id=? AND tenant_id=?", body.status, Number(id), T(s));
    if (!r.changes) return bad(res, "Not found", 404);
    logAction(s, "contract.status", "contract", id, { status: body.status });
    json(res, 200, { ok: true });
  }
  function apiAdminTenderCreate(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    if (!body.title) return bad(res, "Title required");
    const ref = newRef("TDR");
    run("INSERT INTO tenders(tenant_id,ref,title,buyer_org,buyer_email,description,currency,budget,open_at,close_at,status,items) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
      T(s), ref, String(body.title), String(body.buyer_org || ""), String(body.buyer_email || ""), String(body.description || ""),
      String(body.currency || require("../defaults.js").currency(T(s))), Number(body.budget) || 0, body.open_at || null, body.close_at || null, "open", JSON.stringify(body.items || []));
    const id = Number(get("SELECT id FROM tenders WHERE tenant_id=? AND ref=?", T(s), ref).id);
    logAction(s, "tender.create", "tender", ref);
    json(res, 200, { ok: true, id, ref });
  }
  function apiAdminTenderAward(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    const t = get("SELECT * FROM tenders WHERE id=? AND tenant_id=?", Number(id), T(s));
    if (!t) return bad(res, "Unknown tender", 404);
    const items = J(t.items, []), product_ids = items.map(i => i.product_id).filter(Boolean);
    const ref = newRef("CT");
    const c = run("INSERT INTO contracts(tenant_id,ref,buyer_name,buyer_email,buyer_org,currency,product_ids,pricing,min_qty,valid_from,valid_to,status,notes) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
      T(s), ref, String(t.buyer_org || "Tender Winner"), String(t.buyer_email || ""), String(t.buyer_org || ""), String(t.currency || require("../defaults.js").currency(T(s))),
      JSON.stringify(product_ids), JSON.stringify({}), 1, t.open_at || null, t.close_at || null, "active", "Auto-generated from tender " + t.ref);
    run("UPDATE tenders SET status='awarded', awarded_seller_id=?, awarded_contract_id=? WHERE id=?", body.seller_id ? Number(body.seller_id) : null, Number(c.lastInsertRowid), t.id);
    logAction(s, "tender.award", "tender", t.ref, { contract: ref });
    json(res, 200, { ok: true, contract_ref: ref, contract_id: Number(c.lastInsertRowid) });
  }
  function apiAdminRfqToContract(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    const r = get("SELECT * FROM rfqs WHERE id=? AND tenant_id=?", Number(id), T(s));
    if (!r) return bad(res, "Unknown RFQ", 404);
    const ref = newRef("CT"), price = Number(body.price || r.target_price || 0);
    const c = run("INSERT INTO contracts(tenant_id,ref,buyer_name,buyer_email,currency,product_ids,pricing,min_qty,valid_from,status,notes) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
      T(s), ref, String(r.buyer_name || ""), String(r.buyer_email || ""), String(r.currency || require("../defaults.js").currency(T(s))), JSON.stringify(r.product_id ? [r.product_id] : []),
      JSON.stringify(price && r.product_id ? { fixed: { [r.product_id]: price } } : {}), Number(r.qty) || 1, new Date().toISOString().slice(0, 10), "active", "Converted from " + r.ref);
    run("UPDATE rfqs SET status='accepted' WHERE id=?", r.id);
    logAction(s, "rfq.to_contract", "rfq", r.ref, { contract: ref });
    json(res, 200, { ok: true, contract_ref: ref, contract_id: Number(c.lastInsertRowid) });
  }
  /* ---------- B2B trust & trade ---------- */
  function apiTradeAssure(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { assurance: trade.assure(T(s), body.order_id, ownerFor(s), String(body.seller || ""), body.amount, body.currency, body.milestones) }); }
    catch (e) { bad(res, e.message); }
  }
  function apiTradeMilestone(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { assurance: trade.advanceMilestone(T(s), Number(id), String(body.milestone || "")) }); }
    catch (e) { bad(res, e.message); }
  }
  /* confirming delivery releases the escrow to the seller, so only the BUYER (the owner the
     assurance — or its order — was opened for) or store staff may do it. It used to be open
     to anyone, and assurance ids are sequential. */
  function apiTradeConfirm(req, res, url, s, body, id) {
    const ta = get("SELECT buyer, order_id FROM trade_assurance WHERE id=? AND tenant_id=?", Number(id), T(s));
    if (!ta) return bad(res, "Trade-assurance order not found", 404);
    const me = ownerFor(s);
    const ord = ta.order_id ? get("SELECT owner FROM orders WHERE id=? AND tenant_id=?", ta.order_id, T(s)) : null;
    const isBuyer = (ta.buyer && ta.buyer === me) || (ord && ord.owner === me);
    if (!isBuyer && !s.platform_admin && !isAdmin(s)) return bad(res, "Only the buyer can confirm delivery", 403);
    try { json(res, 200, { assurance: trade.confirmDelivery(T(s), Number(id)) }); } catch (e) { bad(res, e.message); }
  }
  function apiTradeDispute(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { assurance: trade.disputeAssurance(T(s), Number(id), body.open === false ? false : true) }); }
    catch (e) { bad(res, e.message); }
  }
  function apiTradeGold(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { gold: trade.enrolGold(T(s), body) }); } catch (e) { bad(res, e.message); }
  }
  function apiTradeVerifySubmit(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { verification: trade.submitVerification(T(s), body) }); } catch (e) { bad(res, e.message); }
  }
  function apiTradeVerifyComplete(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { verification: trade.completeVerification(T(s), Number(id), body.reject ? false : true, s.platform_admin ? s.platform_admin.email : "admin", body.badges, body.notes) }); }
    catch (e) { bad(res, e.message); }
  }
  function apiTradeBadges(req, res, url, s, body, supplierId) {
    json(res, 200, trade.badgesFor(T(s), Number(supplierId)));
  }
  function apiTradeDoc(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { doc: trade.generateDoc(T(s), body) }); } catch (e) { bad(res, e.message); }
  }
  function apiTradeDocGet(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    const doc = get("SELECT * FROM export_documents WHERE id=? AND tenant_id=?", Number(id), T(s));
    if (!doc) return bad(res, "Document not found", 404);
    json(res, 200, { doc });
  }
  function apiTradeLc(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { lc: trade.issueLc(T(s), body) }); } catch (e) { bad(res, e.message); }
  }
  function apiTradeLcPresent(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { lc: trade.presentLc(T(s), Number(id), body.discrepant ? false : true) }); }
    catch (e) { bad(res, e.message); }
  }
  function apiTradeQuote(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { quote: trade.quoteRfq(T(s), { ...body, rfq_id: Number(id) }) }); } catch (e) { bad(res, e.message); }
  }
  function apiTradeQuoteAccept(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { quote: trade.acceptQuote(T(s), Number(id)) }); } catch (e) { bad(res, e.message); }
  }
  function apiTradeBid(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { bid: trade.bid(T(s), { ...body, tender_id: Number(id) }) }); } catch (e) { bad(res, e.message); }
  }
  function apiTradeAward(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { bid: trade.awardTender(T(s), Number(id), Number(body.bid_id)) }); } catch (e) { bad(res, e.message); }
  }
  function apiTradePrice(req, res, url, s) {
    const productId = String(url.searchParams.get("product") || "");
    const skuId = url.searchParams.get("sku") ? Number(url.searchParams.get("sku")) : null;
    const qty = Number(url.searchParams.get("qty")) || 1;
    const segment = url.searchParams.get("segment") || "";
    if (!productId) return bad(res, "product required");
    json(res, 200, { price: trade.priceFor(T(s), productId, skuId, qty, segment) });
  }
  function apiTradeMoqCheck(req, res, url, s) {
    const items = url.searchParams.get("items");
    try {
      const parsed = items ? JSON.parse(items) : [];
      json(res, 200, trade.checkCartMoq(T(s), parsed));
    } catch (e) { bad(res, "Invalid items JSON"); }
  }

  return [
    ["POST /api/trade/assurance", apiTradeAssure],
    ["POST /api/trade/assurance/:id/milestone", (r, re, u, s, b, p) => apiTradeMilestone(r, re, u, s, b, p)],
    ["POST /api/trade/assurance/:id/confirm", (r, re, u, s, b, p) => apiTradeConfirm(r, re, u, s, b, p)],
    ["POST /api/trade/assurance/:id/dispute", (r, re, u, s, b, p) => apiTradeDispute(r, re, u, s, b, p)],
    ["POST /api/trade/gold", apiTradeGold],
    ["POST /api/trade/verification", apiTradeVerifySubmit],
    ["POST /api/trade/verification/:id/complete", (r, re, u, s, b, p) => apiTradeVerifyComplete(r, re, u, s, b, p)],
    ["GET /api/trade/badges/:supplierId", (r, re, u, s, b, p) => apiTradeBadges(r, re, u, s, b, p)],
    ["POST /api/trade/docs", apiTradeDoc],
    ["GET /api/trade/docs/:id", (r, re, u, s, b, p) => apiTradeDocGet(r, re, u, s, b, p)],
    ["POST /api/trade/lc", apiTradeLc],
    ["POST /api/trade/lc/:id/present", (r, re, u, s, b, p) => apiTradeLcPresent(r, re, u, s, b, p)],
    ["POST /api/trade/rfq/:id/quote", (r, re, u, s, b, p) => apiTradeQuote(r, re, u, s, b, p)],
    ["POST /api/trade/quotes/:id/accept", (r, re, u, s, b, p) => apiTradeQuoteAccept(r, re, u, s, b, p)],
    ["POST /api/trade/tenders/:id/bid", (r, re, u, s, b, p) => apiTradeBid(r, re, u, s, b, p)],
    ["POST /api/trade/tenders/:id/award", (r, re, u, s, b, p) => apiTradeAward(r, re, u, s, b, p)],
    ["GET /api/trade/price", apiTradePrice],
    ["GET /api/trade/moq-check", apiTradeMoqCheck],
    ["POST /api/rfqs", apiRfqCreate],
    ["GET /api/admin/rfqs", apiAdminRfqs],
    ["PUT /api/admin/rfqs/:id", (r, re, u, s, b, p) => apiAdminRfqUpdate(r, re, u, s, b, p)],
    ["POST /api/admin/contracts", apiAdminContractCreate],
    ["PUT /api/admin/contracts/:id/status", (r, re, u, s, b, p) => apiAdminContractStatus(r, re, u, s, b, p)],
    ["POST /api/admin/tenders", apiAdminTenderCreate],
    ["POST /api/admin/tenders/:id/award", (r, re, u, s, b, p) => apiAdminTenderAward(r, re, u, s, b, p)],
    ["POST /api/admin/rfqs/:id/contract", (r, re, u, s, b, p) => apiAdminRfqToContract(r, re, u, s, b, p)]
  ];
} };
