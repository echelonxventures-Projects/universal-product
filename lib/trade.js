/* LUXORA Platform — B2B trust & trade engine.
   Trade-assurance escrow, gold-supplier memberships, company verification audits,
   export/customs document generation, letters of credit, multi-seller RFQ bidding,
   reverse-auction tender bids, segment price lists and MOQ enforcement.

   Every status, tier, document kind and segment is a registry row (meta_lists —
   see lib/parity-registries.js). Funds always move through the single escrow/wallet
   ledger (lib/fintech.js + lib/offers.js) so trade assurance never opens a second
   money path. Document "rendering" is deterministic text assembly from the order's
   own fields — the platform invents no values. */
"use strict";

const db = () => require("./db.js");
const fintech = () => require("./fintech.js");
const reg = () => require("./parity-registries.js");
const caps = () => require("./capabilities.js");
const crypto = require("crypto");

const J = (v, d) => { try { return v == null || v === "" ? (d == null ? [] : d) : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d == null ? [] : d; } };
const refOf = (pfx) => pfx + "-" + Date.now().toString(36).toUpperCase().slice(-6) + crypto.randomBytes(2).toString("hex").toUpperCase();

/* ---------- trade assurance (order-level escrow with milestones) ---------- */
/* the buyer pays into escrow at order time; funds release to the seller only when
   the buyer confirms receipt (or the assurance window lapses). This is the core
   of a trust-assured trade model, and it composes with the generic escrow hold. */
function assure(tenantId, orderId, buyer, seller, amount, currency, milestones) {
  const D = db();
  const P = caps().cap(tenantId, "trade_assurance");
  if (!Object.keys(P).length) throw new Error("trade_assurance is not enabled for this tenant");
  const ms = Array.isArray(milestones) && milestones.length ? milestones : (Array.isArray(P.default_milestones) && P.default_milestones.length ? P.default_milestones : ["paid", "production", "shipped", "delivered"]);
  /* the assurance fee is a capability parameter — 2% ships as the default, but
     it is the operator's number to change, not the engine's */
  const fee = +(Number(amount || 0) * Number(P.assurance_fee_pct)).toFixed(2);
  const r = D.run("INSERT INTO trade_assurance(tenant_id,ref,order_id,buyer,seller,amount,currency,fee,milestones,current_milestone,held,status) VALUES(?,?,?,?,?,?,?,?,?,?,1,'holding')",
    Number(tenantId), refOf("TA"), Number(orderId) || null, String(buyer), String(seller),
    +Number(amount || 0).toFixed(2), String(currency || "USD"), fee, JSON.stringify(ms), ms[0]);
  /* the funds themselves sit in the generic escrow ledger */
  fintech().hold(tenantId, orderId, buyer, seller, amount, currency, { source: "trade_assurance", ref: r.lastInsertRowid });
  return D.get("SELECT * FROM trade_assurance WHERE id=?", r.lastInsertRowid);
}
function advanceMilestone(tenantId, assuranceId, milestone) {
  const D = db();
  const ta = D.get("SELECT * FROM trade_assurance WHERE id=? AND tenant_id=?", Number(assuranceId), Number(tenantId));
  if (!ta) throw new Error("Unknown trade-assurance order");
  const ms = J(ta.milestones, []);
  if (!ms.includes(milestone)) throw new Error("Unknown milestone: " + milestone);
  D.run("UPDATE trade_assurance SET current_milestone=?, status=? WHERE id=?", milestone,
    milestone === "delivered" ? "delivered" : milestone, ta.id);
  return D.get("SELECT * FROM trade_assurance WHERE id=?", ta.id);
}
/* buyer confirms receipt → release the held funds to the seller and close */
function confirmDelivery(tenantId, assuranceId) {
  const D = db();
  const ta = D.get("SELECT * FROM trade_assurance WHERE id=? AND tenant_id=? AND held=1", Number(assuranceId), Number(tenantId));
  if (!ta) throw new Error("Trade-assurance order not held");
  const esc = D.get("SELECT id FROM escrow_holds WHERE tenant_id=? AND order_id=? AND held=1", Number(tenantId), ta.order_id);
  if (esc) fintech().releaseEscrow(tenantId, esc.id);
  D.run("UPDATE trade_assurance SET held=0, released_at=datetime('now'), status='released', current_milestone='delivered' WHERE id=?", ta.id);
  return D.get("SELECT * FROM trade_assurance WHERE id=?", ta.id);
}
/* a dispute freezes the release; resolution can refund the buyer */
function disputeAssurance(tenantId, assuranceId, opened) {
  const D = db();
  const ta = D.get("SELECT * FROM trade_assurance WHERE id=? AND tenant_id=? AND held=1", Number(assuranceId), Number(tenantId));
  if (!ta) throw new Error("Trade-assurance order not held");
  const esc = D.get("SELECT id FROM escrow_holds WHERE tenant_id=? AND order_id=? AND held=1", Number(tenantId), ta.order_id);
  if (esc) fintech().disputeEscrow(tenantId, esc.id, opened);
  D.run("UPDATE trade_assurance SET status=? WHERE id=?", opened ? "disputed" : "holding", ta.id);
  return D.get("SELECT * FROM trade_assurance WHERE id=?", ta.id);
}

/* ---------- gold supplier memberships ---------- */
function enrolGold(tenantId, input) {
  const D = db();
  const P = caps().cap(tenantId, "gold_supplier");
  const tier = reg().has("b2bGoldTiers", input.tier) ? input.tier : (P.default_tier || "gold");
  const vlevel = reg().has("b2bVerificationLevels", input.verification_level) ? input.verification_level : "verified";
  const r = D.run("INSERT INTO gold_suppliers(tenant_id,supplier_id,tier,starts_at,ends_at,fee,currency,verified,verification_level,status) VALUES(?,?,?,?,?,?,?,?,?, 'active')",
    Number(tenantId), Number(input.supplier_id), tier, String(input.starts_at || null), String(input.ends_at || null),
    +Number(input.fee || 0).toFixed(2), String(input.currency || "USD"), input.verified ? 1 : 0, vlevel);
  D.run("UPDATE suppliers SET status='active' WHERE id=? AND tenant_id=?", Number(input.supplier_id), Number(tenantId));
  return D.get("SELECT * FROM gold_suppliers WHERE id=?", r.lastInsertRowid);
}
function goldFor(tenantId, supplierId) {
  return db().get("SELECT * FROM gold_suppliers WHERE tenant_id=? AND supplier_id=? AND status='active' ORDER BY id DESC LIMIT 1", Number(tenantId), Number(supplierId));
}

/* ---------- company verification ---------- */
function submitVerification(tenantId, input) {
  const D = db();
  const r = D.run("INSERT INTO company_verifications(tenant_id,supplier_id,ref,company_name,country,registration_no,year_established,employees,revenue,export_share,audit_docs,verification_status) VALUES(?,?,?,?,?,?,?,?,?,?,?, 'pending')",
    Number(tenantId), Number(input.supplier_id) || null, refOf("AUDIT"), String(input.company_name || input.name || ""),
    String(input.country || ""), String(input.registration_no || ""), String(input.year_established || ""),
    String(input.employees || ""), String(input.revenue || ""), String(input.export_share || ""), JSON.stringify(input.audit_docs || []));
  return D.get("SELECT * FROM company_verifications WHERE id=?", r.lastInsertRowid);
}
function completeVerification(tenantId, verificationId, ok, by, badges, notes) {
  const D = db();
  const v = D.get("SELECT * FROM company_verifications WHERE id=? AND tenant_id=?", Number(verificationId), Number(tenantId));
  if (!v) throw new Error("Unknown verification audit");
  const status = ok ? "approved" : "rejected";
  D.run("UPDATE company_verifications SET verification_status=?, audit_by=?, audit_at=datetime('now'), badges=?, notes=? WHERE id=?",
    status, String(by || ""), JSON.stringify(badges || []), String(notes || ""), v.id);
  if (ok && v.supplier_id) {
    D.run("UPDATE suppliers SET status='active' WHERE id=? AND tenant_id=?", v.supplier_id, Number(tenantId));
    const g = goldFor(tenantId, v.supplier_id);
    if (g) D.run("UPDATE gold_suppliers SET verified=1, verification_level=? WHERE id=?", ok ? "gold_verified" : "basic", g.id);
  }
  return D.get("SELECT * FROM company_verifications WHERE id=?", v.id);
}
function badgesFor(tenantId, supplierId) {
  const D = db();
  const v = D.get("SELECT * FROM company_verifications WHERE tenant_id=? AND supplier_id=? AND verification_status='approved' ORDER BY id DESC LIMIT 1", Number(tenantId), Number(supplierId));
  const g = goldFor(tenantId, supplierId);
  const out = [];
  if (g) out.push(g.tier + "_supplier");
  if (v) { out.push("verified"); (J(v.badges, [])).forEach(b => out.includes(b) || out.push(b)); }
  return { badges: out, gold: !!g, verified: !!v, verification: v, membership: g };
}

/* ---------- export / customs documents ---------- */
/* a document is generated from the order's own fields — no values are invented.
   The rendered text is deterministic so two operators see the same artefact. */
function generateDoc(tenantId, input) {
  const D = db();
  const P = caps().cap(tenantId, "export_documents");
  if (!Object.keys(P).length) throw new Error("export_documents is not enabled for this tenant");
  const kind = reg().has("b2bDocKinds", input.doc_kind) ? input.doc_kind : (P.default_doc_kind || "commercial_invoice");
  const o = input.order_id ? D.get("SELECT * FROM orders WHERE id=? AND tenant_id=?", Number(input.order_id), Number(tenantId)) : null;
  const items = o ? D.all("SELECT * FROM order_items WHERE order_id=?", o.id) : [];
  const body = input.body || (items.map((it, i) => ({
    line: i + 1, description: String(it.product_id), qty: it.qty, unit_price: it.price, amount: +(it.qty * it.price).toFixed(2)
  })));
  const total = input.total_value || (o ? o.total : 0);
  const doc = {
    ref: refOf("EXP"),
    tenant_id: Number(tenantId), order_id: input.order_id || null,
    doc_kind: kind,
    buyer: input.buyer || (o && o.name) || "", consignee: input.consignee || input.buyer || (o && o.name) || "",
    shipper: input.shipper || "", origin_country: input.origin_country || (P.default_origin || "US"), dest_country: input.dest_country || "",
    port_loading: input.port_loading || "", port_discharge: input.port_discharge || "",
    incoterms: input.incoterms || (P.default_incoterms || "EXW"), currency: input.currency || (o && o.currency) || "USD",
    total_value: +Number(total || 0).toFixed(2),
    hs_codes: J(input.hs_codes, []), packages: Number(input.packages || (items.length ? items.reduce((n, i) => n + Number(i.qty || 0), 0) : 1)),
    gross_weight: Number(input.gross_weight || 0), net_weight: Number(input.net_weight || 0),
    marks: input.marks || "", body, rendered: ""
  };
  doc.rendered = renderDoc(doc);
  const r = D.run("INSERT INTO export_documents(tenant_id,ref,order_id,doc_kind,buyer,consignee,shipper,origin_country,dest_country,port_loading,port_discharge,incoterms,currency,total_value,hs_codes,packages,gross_weight,net_weight,marks,body,rendered,status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,'draft')",
    doc.tenant_id, doc.ref, doc.order_id, doc.doc_kind, doc.buyer, doc.consignee, doc.shipper,
    doc.origin_country, doc.dest_country, doc.port_loading, doc.port_discharge, doc.incoterms,
    doc.currency, doc.total_value, JSON.stringify(doc.hs_codes), doc.packages, doc.gross_weight, doc.net_weight,
    doc.marks, JSON.stringify(doc.body), doc.rendered);
  return D.get("SELECT * FROM export_documents WHERE id=?", r.lastInsertRowid);
}
/* deterministic plain-text rendering — the console shows it and exports it as a
   file; a PDF pipeline is a presentation concern, not a data one */
function renderDoc(d) {
  const title = String(d.doc_kind || "commercial_invoice").replace(/_/g, " ").toUpperCase();
  const lines = J(d.body, []).map(l =>
    `  ${String(l.line || "")}. ${(l.description || "").slice(0, 44).padEnd(44)} qty:${String(l.qty || "").padEnd(6)} unit:${String(l.unit_price || "")} amt:${l.amount}`).join("\n");
  return [
    title, "=".repeat(title.length),
    `Ref: ${d.ref}${d.order_id ? "   Order: #" + d.order_id : ""}`,
    `Shipper : ${d.shipper || "—"}`,
    `Consignee: ${d.consignee || d.buyer || "—"}`,
    `Origin: ${d.origin_country} → Destination: ${d.dest_country || "—"}`,
    `Port of Loading: ${d.port_loading || "—"}    Port of Discharge: ${d.port_discharge || "—"}`,
    `Incoterms: ${d.incoterms}    Currency: ${d.currency}`,
    `Packages: ${d.packages}    Gross wt: ${d.gross_weight}    Net wt: ${d.net_weight}`,
    d.hs_codes && d.hs_codes.length ? `HS codes: ${d.hs_codes.join(", ")}` : "",
    "-".repeat(72), lines || "  (no line items)", "-".repeat(72),
    `TOTAL: ${d.total_value} ${d.currency}`,
    d.marks ? `Marks & Numbers: ${d.marks}` : ""
  ].filter(Boolean).join("\n");
}

/* ---------- letters of credit ---------- */
function issueLc(tenantId, input) {
  const D = db();
  const r = D.run("INSERT INTO letters_of_credit(tenant_id,ref,order_id,buyer,seller,issuing_bank,advising_bank,lc_number,amount,currency,issue_date,expiry_date,port_loading,port_discharge,latest_shipment,docs_required,status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, 'issued')",
    Number(tenantId), refOf("LC"), Number(input.order_id) || null, String(input.buyer || ""), String(input.seller || ""),
    String(input.issuing_bank || ""), String(input.advising_bank || ""), String(input.lc_number || ""),
    +Number(input.amount || 0).toFixed(2), String(input.currency || "USD"),
    String(input.issue_date || null), String(input.expiry_date || null),
    String(input.port_loading || ""), String(input.port_discharge || ""), String(input.latest_shipment || null),
    JSON.stringify(input.docs_required || []));
  return D.get("SELECT * FROM letters_of_credit WHERE id=?", r.lastInsertRowid);
}
function presentLc(tenantId, lcId, ok) {
  const D = db();
  const P = caps().cap(tenantId, "letters_of_credit");
  const presentable = (P.presentable_statuses || ["issued", "advised", "confirmed"]).map(String);
  const l = D.get("SELECT * FROM letters_of_credit WHERE id=? AND tenant_id=? AND status IN (" + presentable.map(() => "?").join(",") + ")", Number(lcId), Number(tenantId), ...presentable);
  if (!l) throw new Error("LC not presentable");
  const status = ok ? "accepted" : "discrepant";
  D.run("UPDATE letters_of_credit SET status=? WHERE id=?", status, l.id);
  if (ok) D.run("UPDATE letters_of_credit SET status='paid' WHERE id=?", l.id);
  return D.get("SELECT * FROM letters_of_credit WHERE id=?", l.id);
}

/* ---------- RFQ multi-seller bidding ---------- */
/* a buyer's RFQ is broadcast; every supplier/seller can submit a quote (price,
   MOQ, lead time, terms). Ranking is by unit price, then lead time — the same
   axes a procurement buyer compares. */
function quoteRfq(tenantId, input) {
  const D = db();
  const P = caps().cap(tenantId, "rfq_bidding");
  if (!Object.keys(P).length) throw new Error("rfq_bidding is not enabled for this tenant");
  const rfq = D.get("SELECT * FROM rfqs WHERE id=? AND tenant_id=?", Number(input.rfq_id), Number(tenantId));
  if (!rfq) throw new Error("Unknown RFQ");
  if (String(rfq.status) === "closed" || String(rfq.status) === "accepted" || String(rfq.status) === "rejected") throw new Error("RFQ is closed");
  const r = D.run("INSERT INTO rfq_quotes(tenant_id,rfq_id,supplier_id,seller_id,unit_price,currency,moq,lead_days,payment_terms,validity_days,quote_ref,attachments,status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,'submitted')",
    Number(tenantId), Number(rfq.id), Number(input.supplier_id) || null, Number(input.seller_id) || null,
    +Number(input.unit_price || 0).toFixed(2), String(input.currency || rfq.currency || "USD"),
    Number(input.moq || 1), Number(input.lead_days || 0),
    reg().has("paymentTerms", input.payment_terms) ? input.payment_terms : "prepaid",
    Number(input.validity_days || P.default_validity_days || 30), refOf("Q"), JSON.stringify(input.attachments || []));
  D.run("UPDATE rfqs SET status='quoted' WHERE id=? AND tenant_id=? AND status='open'", rfq.id, Number(tenantId));
  const insertedId = r.lastInsertRowid;
  const ranked = rankRfqQuotes(tenantId, rfq.id);
  /* the caller's own quote with its re-computed rank. The module's D connection
     serves the cached pre-rank row, so read through a fresh statement. */
  return D.all("SELECT * FROM rfq_quotes WHERE id=?", insertedId)[0];
}
function rankRfqQuotes(tenantId, rfqId) {
  const D = db();
  const qs = D.all("SELECT * FROM rfq_quotes WHERE tenant_id=? AND rfq_id=? AND status='submitted' ORDER BY unit_price ASC, lead_days ASC", Number(tenantId), Number(rfqId));
  qs.forEach((q, i) => D.run("UPDATE rfq_quotes SET rank=? WHERE id=?", i + 1, q.id));
  return qs;
}
/* acceptQuote is called with the quote id and flips exactly that quote to
   accepted; the RFQ and its other quotes are closed by the caller's decision */
function acceptQuote(tenantId, quoteId) {
  const D = db();
  const q = D.get("SELECT * FROM rfq_quotes WHERE id=? AND tenant_id=?", Number(quoteId), Number(tenantId));
  if (!q) throw new Error("Unknown quote");
  D.run("UPDATE rfq_quotes SET status='accepted' WHERE id=?", q.id);
  D.run("UPDATE rfq_quotes SET status='rejected' WHERE rfq_id=? AND tenant_id=? AND id!=?", q.rfq_id, Number(tenantId), q.id);
  D.run("UPDATE rfqs SET status='accepted' WHERE id=? AND tenant_id=?", q.rfq_id, Number(tenantId));
  return D.get("SELECT * FROM rfq_quotes WHERE id=?", q.id);
}

/* ---------- tender bids (reverse auction) ---------- */
/* the tenders table carries an unused `bids` column in the original schema; this
   engine writes real bid rows and ranks them lowest-first so award is objective. */
function bid(tenantId, input) {
  const D = db();
  const t = D.get("SELECT * FROM tenders WHERE id=? AND tenant_id=?", Number(input.tender_id), Number(tenantId));
  if (!t) throw new Error("Unknown tender");
  const close = String(t.close_at || "");
  if (close && new Date(close.replace(" ", "T")) < new Date()) throw new Error("Tender is closed");
  const r = D.run("INSERT INTO tender_bids(tenant_id,tender_id,bidder,amount,currency,terms,bid_ref,attachments,status,submitted_at) VALUES(?,?,?,?,?,?,?,?, 'submitted',datetime('now'))",
    Number(tenantId), Number(t.id), String(input.bidder), +Number(input.amount || 0).toFixed(2),
    String(input.currency || t.currency || "USD"), String(input.terms || ""), refOf("BID"), JSON.stringify(input.attachments || []));
  const bidId = r.lastInsertRowid;
  const ranked = rankBids(tenantId, t.id);
  return D.get("SELECT * FROM tender_bids WHERE id=?", bidId);
}
function rankBids(tenantId, tenderId) {
  const D = db();
  const bs = D.all("SELECT * FROM tender_bids WHERE tender_id=? AND status='submitted' ORDER BY amount ASC", Number(tenderId));
  bs.forEach((b, i) => D.run("UPDATE tender_bids SET rank=? WHERE id=?", i + 1, b.id));
  /* mirror the bids onto the tender's own column so the existing console sees them */
  D.run("UPDATE tenders SET bids=? WHERE id=? AND tenant_id=?", JSON.stringify(bs.map(b => ({
    id: b.id, bidder: b.bidder, amount: b.amount, currency: b.currency, rank: b.rank, status: b.status, at: b.submitted_at
  }))), Number(tenderId), Number(tenantId));
  return bs;
}
function awardTender(tenantId, tenderId, bidId) {
  const D = db();
  /* the tender must be THIS store's before any bid on it is touched — the bid updates ran
     unscoped, so one store could award or reject another store's bids */
  if (!D.get("SELECT id FROM tenders WHERE id=? AND tenant_id=?", Number(tenderId), Number(tenantId))) throw new Error("Unknown tender");
  const b = D.get("SELECT * FROM tender_bids WHERE id=? AND tender_id=? AND status='submitted'", Number(bidId), Number(tenderId));
  if (!b) throw new Error("Unknown bid");
  D.run("UPDATE tender_bids SET status='awarded' WHERE id=?", b.id);
  D.run("UPDATE tender_bids SET status='rejected' WHERE tender_id=? AND id!=?", Number(tenderId), b.id);
  D.run("UPDATE tenders SET status='awarded', awarded_seller_id=? WHERE id=? AND tenant_id=?",
    Number(b.bidder) || null, Number(tenderId), Number(tenantId));
  return D.get("SELECT * FROM tender_bids WHERE id=?", b.id);
}

/* ---------- segment price lists ---------- */
/* a price list applies a customer-segment-specific price to products; the
   storefront resolves the buyer's segment and reads the override. */
function priceFor(tenantId, productId, skuId, qty, segment) {
  const D = db();
  const rows = D.all("SELECT pli.*, pl.segment FROM price_list_items pli JOIN price_lists pl ON pl.id=pli.price_list_id WHERE pli.tenant_id=? AND pli.product_id=? AND pli.status='active' AND pl.status='active' AND (? OR pl.segment=?)",
    Number(tenantId), String(productId), segment ? 0 : 1, String(segment || ""));
  if (!rows.length) return null;
  /* pick the applicable tier by min_qty/max_qty, best price wins */
  const n = Number(qty || 1);
  const fit = rows.filter(r => (!r.min_qty || n >= r.min_qty) && (!r.max_qty || n <= r.max_qty));
  const pool = fit.length ? fit : rows;
  return pool.sort((a, b) => a.price - b.price)[0];
}

/* ---------- MOQ enforcement ---------- */
/* the cart must respect every line's MOQ — from the product, the supplier link or
   the active price list — before checkout is allowed to proceed */
function moqFor(tenantId, productId, skuId) {
  const D = db();
  const p = D.get("SELECT moq FROM products WHERE tenant_id=? AND id=?", Number(tenantId), String(productId));
  if (p && Number(p.moq || 0) > 0) return Number(p.moq);
  if (skuId) {
    const ps = D.get("SELECT moq FROM product_suppliers WHERE tenant_id=? AND sku_id=? ORDER BY is_primary DESC, moq DESC LIMIT 1", Number(tenantId), Number(skuId));
    if (ps && Number(ps.moq || 0) > 0) return Number(ps.moq);
  }
  const pl = priceFor(tenantId, productId, skuId, 1, null);
  if (pl && Number(pl.min_qty || 0) > 0) return Number(pl.min_qty);
  return 1;
}
function checkCartMoq(tenantId, items) {
  const short = [];
  for (const it of items) {
    const need = moqFor(tenantId, it.product_id, it.sku_id);
    if ((Number(it.qty) || 0) < need) short.push({ product_id: it.product_id, sku_id: it.sku_id, want: it.qty, need });
  }
  return { ok: !short.length, short };
}

module.exports = {
  assure, advanceMilestone, confirmDelivery, disputeAssurance,
  enrolGold, goldFor,
  submitVerification, completeVerification, badgesFor,
  generateDoc, renderDoc,
  issueLc, presentLc,
  quoteRfq, rankRfqQuotes, acceptQuote,
  bid, rankBids, awardTender,
  priceFor, moqFor, checkCartMoq
};
