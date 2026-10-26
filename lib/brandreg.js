/* LUXORA Platform — Brand registry.
   A seller proves it owns a brand (a trademark number and office, and any evidence); staff
   approve or reject the claim. An approved owner may then report offers that infringe its
   brand — counterfeits, trademark or copyright misuse, listing abuse (brandReportKinds rows) —
   and staff uphold or dismiss each report. Upholding moves the offending offer to the offer
   state the brand_registry capability names, and re-runs that product's buy-box so the offer
   stops winning. Whether a claim needs a trademark, whether a brand may have more than one
   owner, and whether product pages show a registered-brand badge are params too.

   Other engines ask ownerOf(): rich product content can be restricted to a brand's owner. */
"use strict";

const db = () => require("./db.js");
const caps = () => require("./capabilities.js");
const reg = () => require("./parity-registries.js");
const states = require("./states.js");
const J = (v, d) => { try { return v == null || v === "" ? (d == null ? [] : d) : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d == null ? [] : d; } };
const fail = (msg, status) => Object.assign(new Error(msg), { status: status || 400 });

const rows = name => reg().list(name).map(x => (typeof x === "string" ? { key: x, name: x } : x)).filter(x => x && x.key);
const inTag = (machine, tag) => { const xs = states.tagged(machine, tag); return { sql: "(" + (xs.length ? xs.map(() => "?").join(",") : "NULL") + ")", args: xs }; };

function params(tid) {
  const P = caps().cap(tid, "brand_registry");
  if (!Object.keys(P).length) throw fail("The brand registry is not available in this store", 403);
  return P;
}
/* a product's brand is a brands row's key or its label; the registry keys claims by the key */
function brandOf(tid, value) {
  const v = String(value == null ? "" : value).trim();
  if (!v) return null;
  return db().get("SELECT key, label FROM brands WHERE tenant_id=? AND (key=? OR lower(label)=lower(?))", Number(tid), v, v) || null;
}
/* the brand's approved owner (the claim in a state tagged owner), or null */
function ownerOf(tid, brandValue) {
  const b = brandOf(tid, brandValue);
  if (!b) return null;
  const own = inTag("brand_claim", "owner");
  return db().get("SELECT * FROM brand_claims WHERE tenant_id=? AND brand=? AND status IN " + own.sql + " ORDER BY id LIMIT 1", Number(tid), b.key, ...own.args) || null;
}
/* the product page's badge, where the store shows one */
function badge(tid, brandValue) {
  const P = caps().cap(tid, "brand_registry");
  if (!Object.keys(P).length || !P.badge) return null;
  const o = ownerOf(tid, brandValue);
  if (!o) return null;
  const b = brandOf(tid, brandValue);
  return { brand: b.key, label: b.label, since: o.reviewed_at };
}

/* ---------- claims ---------- */
function presentClaim(c) {
  const seller = c.seller_id ? db().get("SELECT id, name FROM sellers WHERE id=?", c.seller_id) : null;
  return { ...c, evidence: J(c.evidence, []), state: states.display("brand_claim", c.status), next: states.next("brand_claim", c.status), owner: states.is("brand_claim", c.status, "owner"), seller };
}
function claim(tid, input) {
  const P = params(tid);
  const i = input || {};
  const b = brandOf(tid, i.brand);
  if (!b) throw fail("Unknown brand — add it under Brands first", 404);
  const sellerId = Number(i.seller_id) || null;
  if (sellerId && !db().get("SELECT id FROM sellers WHERE id=? AND tenant_id=?", sellerId, Number(tid))) throw fail("Unknown seller", 404);
  const tm = String(i.trademark_number || "").trim().slice(0, 60);
  if (P.require_trademark && !tm) throw fail("A claim needs the brand's trademark number");
  if (P.one_owner_per_brand && ownerOf(tid, b.key)) throw fail(b.label + " is already registered to an owner", 409);
  const pend = inTag("brand_claim", "pending");
  if (db().get("SELECT id FROM brand_claims WHERE tenant_id=? AND brand=? AND COALESCE(seller_id,0)=? AND status IN " + pend.sql, Number(tid), b.key, sellerId || 0, ...pend.args))
    throw fail("A claim for " + b.label + " by this seller is already waiting for review", 409);
  const evidence = (Array.isArray(i.evidence) ? i.evidence : String(i.evidence || "").split(/\r?\n/)).map(x => String(x).trim().slice(0, 300)).filter(Boolean).slice(0, 10);
  const r = db().run("INSERT INTO brand_claims(tenant_id,brand,seller_id,claimant,trademark_number,trademark_office,evidence,status) VALUES(?,?,?,?,?,?,?,?)",
    Number(tid), b.key, sellerId, String(i.claimant || "").slice(0, 120), tm, String(i.trademark_office || "").trim().slice(0, 120),
    JSON.stringify(evidence), states.initial("brand_claim"));
  return presentClaim(db().get("SELECT * FROM brand_claims WHERE id=?", r.lastInsertRowid));
}
function decideClaim(tid, id, action, by, notes) {
  const P = params(tid);
  const D = db();
  const c = D.get("SELECT * FROM brand_claims WHERE id=? AND tenant_id=?", Number(id), Number(tid));
  if (!c) throw fail("Claim not found", 404);
  const to = states.actionTarget("brand_claim", action);
  if (!to) throw fail("Unknown action: " + action);
  if (!states.can("brand_claim", c.status, to)) throw fail("A claim that is " + states.display("brand_claim", c.status).label + " cannot be moved that way", 409);
  if (states.is("brand_claim", to, "owner") && P.one_owner_per_brand) {
    const other = ownerOf(tid, c.brand);
    if (other && other.id !== c.id) throw fail("This brand already has an approved owner — revoke that claim first", 409);
  }
  const mv = states.apply("brand_claim", { tenantId: tid, from: c.status, to, row: c });
  const patch = Object.assign({}, mv.patch, { reviewed_by: String(by || ""), notes: String(notes || c.notes || "").slice(0, 1000) });
  const cols = Object.keys(patch);
  D.run("UPDATE brand_claims SET " + cols.map(k => k + "=?").join(", ") + " WHERE id=?", ...cols.map(k => patch[k]), c.id);
  return presentClaim(D.get("SELECT * FROM brand_claims WHERE id=?", c.id));
}
function claims(tid) { return db().all("SELECT * FROM brand_claims WHERE tenant_id=? ORDER BY id DESC LIMIT 300", Number(tid)).map(presentClaim); }

/* ---------- infringement reports ---------- */
function presentReport(r) {
  const offer = r.offer_id ? db().get("SELECT id, product_id, seller_id, price, offer_status FROM seller_offers WHERE id=?", r.offer_id) : null;
  return { ...r, kind_row: rows("brandReportKinds").find(k => k.key === r.kind) || null, state: states.display("brand_report", r.status), next: states.next("brand_report", r.status), offer };
}
/* only a brand's approved owner reports (the claim is the proof), against an offer or a
   seller's offers of one of that brand's products */
function report(tid, input) {
  params(tid);
  const i = input || {};
  const D = db();
  const own = inTag("brand_claim", "owner");
  const c = D.get("SELECT * FROM brand_claims WHERE id=? AND tenant_id=? AND status IN " + own.sql, Number(i.claim_id), Number(tid), ...own.args);
  if (!c) throw fail("Only a brand's approved owner can report — name an approved claim", 403);
  const kind = rows("brandReportKinds").find(k => k.key === String(i.kind || ""));
  if (!kind) throw fail("Unknown kind of report");
  let offer = null, productId = i.product_id ? String(i.product_id) : null, sellerId = Number(i.seller_id) || null;
  if (i.offer_id) {
    offer = D.get("SELECT * FROM seller_offers WHERE id=? AND tenant_id=?", Number(i.offer_id), Number(tid));
    if (!offer) throw fail("Unknown offer", 404);
    productId = String(offer.product_id); sellerId = offer.seller_id;
  }
  if (!productId) throw fail("Name the offer or the product being reported");
  const p = D.get("SELECT id, brand FROM products WHERE tenant_id=? AND id=?", Number(tid), productId);
  if (!p) throw fail("Unknown product", 404);
  const pb = brandOf(tid, p.brand);
  if (!pb || pb.key !== c.brand) throw fail("That product is not listed under " + c.brand, 403);
  if (sellerId && c.seller_id && sellerId === Number(c.seller_id)) throw fail("A brand owner cannot report its own offer");
  const r = D.run("INSERT INTO brand_reports(tenant_id,brand,claim_id,kind,product_id,offer_id,seller_id,details,status) VALUES(?,?,?,?,?,?,?,?,?)",
    Number(tid), c.brand, c.id, kind.key, productId, offer ? offer.id : null, sellerId, String(i.details || "").slice(0, 2000), states.initial("brand_report"));
  return presentReport(D.get("SELECT * FROM brand_reports WHERE id=?", r.lastInsertRowid));
}
function decideReport(tid, id, action, by, outcome) {
  const P = params(tid);
  const D = db();
  const r = D.get("SELECT * FROM brand_reports WHERE id=? AND tenant_id=?", Number(id), Number(tid));
  if (!r) throw fail("Report not found", 404);
  const to = states.actionTarget("brand_report", action);
  if (!to) throw fail("Unknown action: " + action);
  if (!states.can("brand_report", r.status, to)) throw fail("A report that is " + states.display("brand_report", r.status).label + " cannot be moved that way", 409);
  let affected = 0;
  if (states.is("brand_report", to, "upheld")) {
    const target = String(P.offer_state_on_infringement || "");
    if (!states.has("seller_offer", target)) throw fail("The brand registry names an offer state (" + target + ") the seller-offer machine does not have — fix it under Capabilities", 409);
    const offers = r.offer_id ? D.all("SELECT * FROM seller_offers WHERE id=? AND tenant_id=?", r.offer_id, Number(tid))
      : r.seller_id ? D.all("SELECT * FROM seller_offers WHERE tenant_id=? AND product_id=? AND seller_id=?", Number(tid), r.product_id, r.seller_id) : [];
    for (const o of offers) { D.run("UPDATE seller_offers SET offer_status=? WHERE id=?", target, o.id); affected++; }
    if (affected) try { require("./marketplace-ext.js").recomputeBuybox(tid, r.product_id); } catch (e) { }
  }
  const mv = states.apply("brand_report", { tenantId: tid, from: r.status, to, row: r });
  const patch = Object.assign({}, mv.patch, { reviewed_by: String(by || ""), outcome: String(outcome || "").slice(0, 1000) });
  const cols = Object.keys(patch);
  D.run("UPDATE brand_reports SET " + cols.map(k => k + "=?").join(", ") + " WHERE id=?", ...cols.map(k => patch[k]), r.id);
  return Object.assign(presentReport(D.get("SELECT * FROM brand_reports WHERE id=?", r.id)), { offers_affected: affected });
}
function reports(tid) { return db().all("SELECT * FROM brand_reports WHERE tenant_id=? ORDER BY id DESC LIMIT 300", Number(tid)).map(presentReport); }
function vocabulary(tid) {
  const verbs = m => Object.entries(states.actions(m)).map(([verb, to]) => ({ verb, to, label: states.display(m, to).label }));
  return { reportKinds: rows("brandReportKinds"), claimActions: verbs("brand_claim"), reportActions: verbs("brand_report"), brands: db().all("SELECT key, label FROM brands WHERE tenant_id=? AND active=1 ORDER BY position, label", Number(tid)),
    sellers: db().all("SELECT id, name FROM sellers WHERE tenant_id=? ORDER BY name", Number(tid)) };
}

module.exports = { brandOf, ownerOf, badge, claim, decideClaim, claims, report, decideReport, reports, vocabulary };
