/* LUXORA Platform - REST API: multi-tenant, pluggable providers, billing, audit, monitoring */
"use strict";

const crypto = require("crypto");
const { run, get, all, newUser, verifyUser, newPlatformAdmin, verifyPlatformAdmin, hashPasswordFor, ownerFor, tenantState, setTenantState, audit, seedTenantCatalog, seedTenantDepartments, seedTenantHome, seedMeta, seedTaxonomy, DB_PATH, DEPT_TO_INDUSTRY } = require("./db.js");
const settings = require("./settings.js");
const registry = require("./registry.js");
const mods = require("./modules.js");
const sec = require("./security.js");
const ai = require("./ai.js");
const offers = require("./offers.js");
const connect = require("./connect.js");
const rtconfig = require("./config.js");
const adapters = require("./adapters.js");
const env = require("./env.js");
const taxmod = require("./tax.js");
const billing = require("./billing.js");
const events = require("./events.js");
const governance = require("./governance.js");
const { auditChainVerify, passwordReused, setUserPassword } = require("./db.js");
const fs = require("fs");

function json(res, code, obj) {
  res.writeHead(code, { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" });
  res.end(JSON.stringify(obj));
}
function bad(res, msg, code) { json(res, code || 400, { error: msg }); }

const CFG = s => settings.load(s.tenant.id);
const T = s => s.tenant.id;
function isAdmin(s) {
  if (!s.user_id) return false;
  const u = get("SELECT role FROM users WHERE id=? AND tenant_id=?", s.user_id, T(s));
  return !!(u && u.role === "admin");
}
function requireAdmin(s, res) { if (!isAdmin(s)) { bad(res, "Store administrator access required", 403); return false; } return true; }
function requirePlatform(s, res) { if (!s.platform_admin) { bad(res, "Platform access required", 403); return false; } return true; }
function actor(s) {
  if (s.platform_admin) return ["platform", s.platform_admin.id, s.platform_admin.email];
  if (s.user_id) { const u = get("SELECT name,email,role FROM users WHERE id=?", s.user_id); return [u && u.role === "admin" ? "admin" : "customer", s.user_id, u ? u.email : ""]; }
  return ["guest", null, s.sid];
}
function ipOf(req) { return (req && req.socket && req.socket.remoteAddress) || ""; }
function logAction(s, action, entity, entityId, meta, req) {
  const [type, id, name] = actor(s);
  audit(T(s), type, id, name, action, entity, entityId, meta || {}, ipOf(req), (s && s.trace) || (req && req.__trace));
}
function emitEvent(tenantId, event, data, uid) { try { events.emit(tenantId, event, data, { uid }); } catch (e) { console.error("emit:", e.message); } }

/* ---------------- provider registry (built-in + custom manifests) ---------------- */
function customProviders(tenantId, kind) {
  const rows = all("SELECT manifest FROM custom_providers WHERE kind=? AND (scope='platform' OR (scope='tenant' AND tenant_id=?))", kind, tenantId);
  return rows.map(r => { try { return JSON.parse(r.manifest); } catch (e) { return null; } }).filter(Boolean);
}
function paymentRegistry(tenantId) { return [...customProviders(tenantId, "payment"), ...registry.providerDefs("payment")]; }
function commerceOf(s) {
  const c = CFG(s); const co = registry.country(c.commerce.country || "US");
  const baseCur = registry.currency(co.currency) || { code: co.currency, symbol: co.symbol, decimals: co.decimals != null ? co.decimals : 2, usd: 1 };
  const want = c.commerce.currency ? registry.currency(c.commerce.currency) : null;
  const cur = want || baseCur;
  const fx = cur.code === baseCur.code ? 1 : registry.fxTo(baseCur.code, cur.code);
  return { ...c.commerce, country: co.code, currency: cur.code, symbol: cur.symbol, decimals: cur.decimals, fx, baseCurrency: baseCur.code, locale: c.commerce.locale || co.locale, taxMode: c.commerce.taxMode || co.tax_mode, taxRate: (c.commerce.taxRate == null ? co.tax_rate : c.commerce.taxRate) };
}
function money2(cm, n) { return n == null ? null : +(n * cm.fx).toFixed(cm.decimals); }
function storeView(p, cm) {
  const o = publicProduct(p);
  const pr = { ...o.pricing_rules };
  if (pr.tiers) pr.tiers = pr.tiers.map(t => ({ ...t, price: money2(cm, t.price) }));
  if (pr.bundle_price) pr.bundle_price = money2(cm, pr.bundle_price);
  return { ...o, p: money2(cm, o.p), l: o.l != null ? money2(cm, o.l) : null, pricing_rules: pr };
}
function enabledGateways(tenantId) {
  const reg = paymentRegistry(tenantId);
  return all("SELECT * FROM tenant_gateways WHERE tenant_id=? AND provider_id NOT LIKE 'ship:%' AND provider_id NOT LIKE 'notify:%' AND enabled=1 ORDER BY is_primary DESC, position", tenantId)
    .map(g => { const p = reg.find(x => x.id === g.provider_id); return p ? { ...p, mode: g.mode, is_primary: !!g.is_primary, configured: true } : null; })
    .filter(Boolean);
}
function enabledCarriers(tenantId) {
  return all("SELECT * FROM tenant_gateways WHERE tenant_id=? AND provider_id LIKE 'ship:%' AND enabled=1 ORDER BY is_primary DESC, position", tenantId)
    .map(g => { const id = g.provider_id.slice(5); const p = registry.providerDefs("shipping").find(x => x.id === id) || customProviders(tenantId, "shipping").find(x => x.id === id); return p ? { ...p, is_primary: !!g.is_primary } : null; })
    .filter(Boolean);
}
function enabledNotifiers(tenantId) {
  return all("SELECT * FROM tenant_gateways WHERE tenant_id=? AND provider_id LIKE 'notify:%' AND enabled=1 ORDER BY position", tenantId)
    .map(g => { const id = g.provider_id.slice(7); const p = registry.providerDefs("notification").find(x => x.id === id) || customProviders(tenantId, "notification").find(x => x.id === id); return p || null; })
    .filter(Boolean);
}
function simulateGateway(gw, amount) {
  const ref = `${gw.id}_sim_${crypto.randomBytes(7).toString("hex")}`;
  const fee = +((amount * (gw.feePct || 0) / 100 + (gw.feeFixed || 0)).toFixed(2));
  const pending = ["cod", "bank"].includes(gw.id) || (gw.methods || []).includes("cod");
  return { ref, fee, status: pending ? "pending" : "captured" };
}
function gatewaySecrets(tenantId, providerId) {
  const row = get("SELECT mode, config FROM tenant_gateways WHERE tenant_id=? AND provider_id=?", tenantId, providerId);
  if (!row) return null;
  let cfg = {}; try { cfg = JSON.parse(row.config || "{}"); } catch (e) { }
  cfg = sec.unsealConfig(tenantId, providerId, JSON.stringify(cfg));
  return { mode: row.mode, cfg };
}
/* Settle a payment. Real gateway only when outbound mode ≠ offline and the store's gateway is
   `live` + has credentials; otherwise the simulated path (identical to before). Outbound mode
   is a Runtime config (auto|offline|live) — no code. */
function outboundOffline() { return rtconfig.driverOf("outbound") === "offline" || process.env.LX_OFFLINE === "1"; }
async function settlePayment(tenantId, gw, amount, currency, idempotency) {
  const fee = +((amount * (gw.feePct || 0) / 100 + (gw.feeFixed || 0)).toFixed(2));
  const live = !outboundOffline() && gw.mode === "live" ? gatewaySecrets(tenantId, gw.id) : null;
  if (live && live.cfg && Object.keys(live.cfg).length) {
    const r = await connect.pay({ provider: gw.id, config: live.cfg, amount, currency, idempotency });
    if (r.live && r.ok) return { ref: r.ref || `${gw.id}_${Date.now()}`, fee, status: r.status === "pending" ? "pending" : "captured", live: true };
    if (r.live && !r.ok) return { ref: "failed_" + crypto.randomBytes(6).toString("hex"), fee: 0, status: "failed", live: true, error: r.error };
  }
  const sim = simulateGateway(gw, amount); sim.fee = fee; return sim;
}
function notify(tenantId, subject, body, to) {
  const offline = outboundOffline();
  const rows = all("SELECT * FROM tenant_gateways WHERE tenant_id=? AND provider_id LIKE 'notify:%' AND enabled=1 AND mode='live' ORDER BY position", tenantId);
  for (const g of rows) {
    const id = g.provider_id.slice(7);
    if (id === "log" || offline) { console.log(`  ✉️  [${id}${offline ? "·offline" : ""}] ${subject} — ${body}`); audit(tenantId, "system", null, "notifier", "notify.sent", "notification", id, { subject, channel: id, offline: !!offline }); continue; }
    let cfg = {}; try { cfg = JSON.parse(g.config || "{}"); } catch (e) { }
    cfg = sec.unsealConfig(tenantId, "notify:" + id, JSON.stringify(cfg));
    audit(tenantId, "system", null, "notifier", "notify.sent", "notification", id, { subject, channel: id });
    connect.notify({ provider: id, config: cfg, subject, text: body, to: to || cfg.to }).then(r => {
      if (r.live && !r.ok) audit(tenantId, "system", null, "notifier", "notify.failed", "notification", id, { subject, error: r.error });
    }).catch(() => { });
  }
}

/* ---------------- public config & providers ---------------- */
function apiStores(req, res) {
  json(res, 200, { stores: all("SELECT slug,name,domain FROM tenants WHERE status='active' ORDER BY id") });
}
function apiConfig(req, res, url, s) {
  const c = CFG(s); const cm = commerceOf(s);
  json(res, 200, {
    tenant: { id: s.tenant.id, slug: s.tenant.slug, name: s.tenant.name, mode: s.tenant.mode, industries: J(s.tenant.industries, []) },
    brand: c.brand, theme: c.theme, commerce: { ...cm, freeShipThreshold: money2(cm, c.commerce.freeShipThreshold), shipFee: money2(cm, c.commerce.shipFee), giftAmounts: (c.commerce.giftAmounts || []).map(x => money2(cm, x)), giftMax: money2(cm, c.commerce.giftMax) }, features: c.features, copy: c.copy,
    geo: { countries: registry.countries(), taxModes: registry.taxModes(), currencies: registry.currencies() },
    capabilities: [...mods.caps(T(s))],
    departments: all("SELECT key,label,icon FROM departments WHERE tenant_id=? AND active=1 ORDER BY position", T(s)),
    home: {
      banners: all("SELECT id,title,subtitle,cta,hue,dept FROM home_banners WHERE tenant_id=? AND active=1 ORDER BY position", T(s)),
      cards: all("SELECT id,title,dept,tiles FROM home_cards WHERE tenant_id=? AND active=1 ORDER BY position", T(s)).map(r => ({ ...r, tiles: JSON.parse(r.tiles || "[]") }))
    }
  });
}
function apiProviders(req, res, url, s) {
  const c = CFG(s);
  const country = registry.countryProfile(c.commerce.country || "US");
  const cm2 = commerceOf(s);
  const gws = enabledGateways(T(s)).filter(g => g.id === "cod" || g.id === "bank" || registry.supports(g.id, country.code)).map(g => ({ id: g.id, name: g.name, emoji: g.emoji, methods: g.methods, feePct: g.feePct, mode: g.mode, primary: g.is_primary }));
  json(res, 200, {
    country: { code: country.code, name: country.name, currency: country.currency, symbol: country.symbol, locale: country.locale },
    gateways: gws, carriers: enabledCarriers(T(s)).map(x => ({ id: x.id, name: x.name, emoji: x.emoji, eta: x.eta, baseFee: x.baseFee != null ? money2(cm2, x.baseFee) : undefined, freeOver: x.freeOver, primary: x.is_primary })),
    tax: { mode: commerceOf(s).taxMode, rate: commerceOf(s).taxRate }, taxModes: registry.taxModes()
  });
}

/* ---------------- session ---------------- */
function apiSession(req, res, url, s) {
  const owner = ownerFor(s);
  const cart = all("SELECT product_id, qty FROM cart_items WHERE owner=?", owner);
  const sub = cart.reduce((n, c) => { const p = get("SELECT price FROM products WHERE tenant_id=? AND id=?", T(s), c.product_id); return p ? n + p.price * c.qty : n; }, 0);
  json(res, 200, {
    user: s.user_id ? get("SELECT id,name,email,role FROM users WHERE id=? AND tenant_id=?", s.user_id, T(s)) : null,
    zip: s.zip, gift: mods.hasCap(T(s), "wallet") ? mods.walletBalance(T(s), mods.ownerFor(s)) : 0, coupon: s.coupon || "", capabilities: [...mods.caps(T(s))],
    cartCount: cart.reduce((n, c) => n + c.qty, 0), cartSubtotal: sub,
    saved: all("SELECT product_id FROM saved_items WHERE owner=?", owner).map(r => r.product_id),
    viewed: all("SELECT product_id FROM view_history WHERE owner=? ORDER BY seen_at DESC LIMIT 12", owner).map(r => r.product_id)
  });
}
function apiCoupon(req, res, url, s, body) {
  if (!sec.policy().provisioning.couponsAllowed) return bad(res, "Promo codes are disabled by platform policy", 403);
  if (!CFG(s).features.coupons) return bad(res, "Promo codes are disabled for this store", 403);
  const code = String(body.code || "").trim().toUpperCase();
  if (code) {
    const v = offers.validateCoupon(T(s), code, s.user_id ? ownerFor(s) : "");
    if (!v.ok) return bad(res, v.reason || "Invalid or expired promo code", 404);
  }
  run("UPDATE tenant_state SET coupon=? WHERE sid=? AND tenant_id=?", code, s.sid, T(s));
  s.coupon = code;
  logAction(s, code ? "coupon.apply" : "coupon.remove", "coupon", code);
  json(res, 200, cartPayload(s));
}
function apiZip(req, res, url, s, body) {
  const zip = String(body.zip || "").trim().slice(0, 12);
  if (!zip) return bad(res, "Location required");
  setTenantState(s.sid, T(s), { zip }); s.zip = zip;
  json(res, 200, { ok: true, zip });
}

/* ---------------- auth ---------------- */
function apiRegister(req, res, url, s, body) {
  const name = String(body.name || "").trim().slice(0, 60);
  const email = String(body.email || "").trim().toLowerCase();
  const password = String(body.password || "");
  if (!name || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return bad(res, "Please enter a valid name and email");
  const perr = sec.checkPassword(password, email);
  if (perr) return bad(res, perr);
  if (get("SELECT id FROM users WHERE tenant_id=? AND email=?", T(s), email)) return bad(res, "That email already has an account", 409);
  const uid = newUser(T(s), name, email, password, "customer");
  mergeOwner("t" + T(s) + ":s:" + s.sid, "t" + T(s) + ":u:" + uid);
  mods.walletMerge("t" + T(s) + ":s:" + s.sid, "t" + T(s) + ":u:" + uid);
  run("UPDATE sessions SET user_id=? WHERE sid=?", uid, s.sid);
  s.user_id = uid;
  logAction(s, "auth.register", "user", uid, { email });
  json(res, 200, { ok: true, user: { id: uid, name, email, role: "customer" } });
}
function apiLogin(req, res, url, s, body) {
  const email = String(body.email || "").trim();
  const lock = sec.lockState(email);
  if (lock.locked) return bad(res, "Account temporarily locked after failed attempts — retry in " + lock.retryAfterSec + "s", 423);
  const u = verifyUser(T(s), email, String(body.password || ""));
  if (!u) { sec.noteLoginFail(email); logAction(s, "auth.login_failed", "user", null, { email }, req);
    if (get("SELECT id FROM platform_admins WHERE email=?", email.toLowerCase())) return bad(res, "That is a Platform console account — sign in at /platform.html instead", 401);
    if (get("SELECT id FROM users WHERE tenant_id=? AND email=?", T(s), email.toLowerCase())) {
      const admin0 = get("SELECT email FROM users WHERE tenant_id=? AND role='admin' ORDER BY id LIMIT 1", T(s));
      return bad(res, "Wrong password for " + s.tenant.name + (admin0 ? " — this store's console admin is " + admin0.email : ""), 401);
    }
    if (get("SELECT id FROM users WHERE email=? LIMIT 1", email.toLowerCase())) return bad(res, "That account exists on a different store — open it first (add ?store=slug to the URL), then sign in", 401);
    const admin0 = get("SELECT email FROM users WHERE tenant_id=? AND role='admin' ORDER BY id LIMIT 1", T(s));
    return bad(res, "No store-admin match for " + s.tenant.name + (admin0 ? " — this store's console admin is " + admin0.email : "") + " (platform owner signs in at /platform.html)", 401);
  }
  sec.noteLoginOk(email);
  mergeOwner("t" + T(s) + ":s:" + s.sid, "t" + T(s) + ":u:" + u.id);
  mods.walletMerge("t" + T(s) + ":s:" + s.sid, "t" + T(s) + ":u:" + u.id);
  run("UPDATE sessions SET user_id=? WHERE sid=?", u.id, s.sid);
  s.user_id = u.id;
  logAction(s, "auth.login", "user", u.id, { email: u.email });
  json(res, 200, { ok: true, user: { id: u.id, name: u.name, email: u.email, role: u.role } });
}
function apiLogout(req, res, url, s) {
  run("UPDATE sessions SET user_id=NULL WHERE sid=?", s.sid);
  s.user_id = null;
  json(res, 200, { ok: true });
}
function apiTokenExchange(req, res, url, s, body) {
  const t = get("SELECT * FROM tokens WHERE token=? AND expires_at > datetime('now')", String(body.token || ""));
  if (!t) return bad(res, "Invalid or expired token", 401);
  if (t.tenant_id !== T(s)) return bad(res, "Token issued for a different store", 403);
  run("DELETE FROM tokens WHERE token=?", t.token);
  run("UPDATE sessions SET user_id=? WHERE sid=?", t.user_id, s.sid);
  s.user_id = t.user_id;
  const u = get("SELECT id,name,email,role FROM users WHERE id=?", t.user_id);
  json(res, 200, { ok: true, user: u });
}
function mergeOwner(from, to) {
  if (from === to) return;
  for (const t of ["cart_items", "saved_items", "view_history"]) {
    const rows = all(`SELECT * FROM ${t} WHERE owner=?`, from);
    for (const r of rows) {
      if (t === "cart_items") {
        const ex = get("SELECT qty FROM cart_items WHERE owner=? AND product_id=?", to, r.product_id);
        if (ex) run("UPDATE cart_items SET qty = qty + ? WHERE owner=? AND product_id=?", r.qty, to, r.product_id);
        else run("INSERT INTO cart_items(owner, product_id, qty) VALUES(?,?,?)", to, r.product_id, r.qty);
      } else run(`INSERT OR IGNORE INTO ${t}(owner, product_id) VALUES(?,?)`, to, r.product_id);
    }
    run(`DELETE FROM ${t} WHERE owner=?`, from);
  }
}

/* ---------------- products / search ---------------- */
function sortClause(sort) {
  switch (sort) {
    case "price-asc": return "price ASC";
    case "price-desc": return "price DESC";
    case "rating": return "rating DESC, ratings_count DESC";
    case "new": return "flags LIKE '%new%' DESC, position DESC";
    case "discount": return "deal_pct DESC";
    default: return "flags LIKE '%bs%' DESC, ratings_count DESC";
  }
}
function buildSearch(s, url) {
  const c = CFG(s);
  const q = (url.searchParams.get("q") || "").trim().toLowerCase();
  let dept = url.searchParams.get("dept") || "all";
  const valid = all("SELECT key FROM departments WHERE tenant_id=? AND active=1", T(s)).map(r => r.key);
  if (dept !== "all" && !valid.includes(dept)) dept = "all";
  const rating = Math.min(5, Number(url.searchParams.get("rating") || 0));
  const pmin = Number(url.searchParams.get("pmin") || 0);
  const pmax = Number(url.searchParams.get("pmax") || 0);
  const prio = url.searchParams.get("prio") === "1";
  const deal = url.searchParams.get("deal") === "1" && c.features.deals;
  const where = ["tenant_id=?", "lifecycle='published'", "deleted_at IS NULL"], args = [T(s)];
  const node = url.searchParams.get("node");
  if (node) { where.push("node_id IN (" + nodeDescendants(T(s), node).map(() => "?").join(",") + ")"); args.push(...nodeDescendants(T(s), node)); }
  const ptype = url.searchParams.get("type");
  if (ptype) { where.push("type = ?"); args.push(ptype); }
  if (dept !== "all") { where.push("dept = ?"); args.push(dept); }
  if (rating) { where.push("rating >= ?"); args.push(rating); }
  if (pmin) { where.push("price >= ?"); args.push(pmin); }
  if (pmax) { where.push("price <= ?"); args.push(pmax); }
  if (prio) where.push("priority = 1");
  if (deal) where.push("deal_pct >= 10");
  if (q) for (const t of q.split(/\s+/).filter(Boolean)) {
    where.push("(lower(title) LIKE ? OR lower(brand) LIKE ? OR lower(keywords) LIKE ?)");
    args.push(`%${t}%`, `%${t}%`, `%${t}%`);
  }
  return { sql: where.join(" AND "), args, q, dept };
}
function publicProduct(p) {
  return {
    id: p.id, t: p.title, b: p.brand, d: p.dept, p: p.price, l: p.list_price, r: p.rating, c: p.ratings_count,
    e: p.emoji, h: p.hue, pr: !!p.priority, st: p.stock, fl: p.flags || "", kw: p.keywords, about: p.about || [],
    type: p.type || "physical", node_id: p.node_id || null,
    identity: J(p.identity), attrs: J(p.attrs), vertical: J(p.vertical), media: J(p.media, []),
    seo: J(p.seo), pricing_rules: J(p.pricing_rules), logistics: J(p.logistics), tax_rule: J(p.tax_rule), uom: J(p.uom), packaging: J(p.packaging, [])
  };
}
function apiProducts(req, res, url, s) {
  const c = CFG(s);
  const { sql, args, dept, q } = buildSearch(s, url);
  const sort = url.searchParams.get("sort") || "featured";
  const per = Math.min(200, Number(url.searchParams.get("limit") || url.searchParams.get("per") || c.commerce.perPage));
  const page = Math.max(1, Number(url.searchParams.get("page") || 1));
  const total = get(`SELECT COUNT(*) c FROM products WHERE ${sql}`, ...args).c;
  const rows = all(`SELECT * FROM products WHERE ${sql} ORDER BY ${sortClause(sort)} LIMIT ? OFFSET ?`, ...args, per, (page - 1) * per);
  const cm = commerceOf(s);
  const items = rows.map(r => storeView({ ...r, about: [] }, cm));
  const noDept = new URL(url); noDept.searchParams.set("dept", "all");
  const facet = buildSearch(s, noDept);
  const deptCounts = {};
  all(`SELECT dept, COUNT(*) c FROM products WHERE ${facet.sql} GROUP BY dept`, ...facet.args).forEach(r => { deptCounts[r.dept] = (deptCounts[r.dept] || 0) + r.c; });
  json(res, 200, { q, dept, total, page, per, pages: Math.max(1, Math.ceil(total / per)), items, deptCounts });
}
function apiProduct(req, res, url, s, body, id) {
  const c = CFG(s);
  const p = get("SELECT * FROM products WHERE tenant_id=? AND id=? AND lifecycle='published' AND deleted_at IS NULL", T(s), id);
  if (!p) return bad(res, "Product not found", 404);
  p.about = all("SELECT text FROM product_bullets WHERE tenant_id=? AND product_id=? ORDER BY pos", T(s), id).map(r => r.text);
  const revs = c.features.reviews ? all("SELECT id,name,rating,title,body,verified,created_at FROM reviews WHERE tenant_id=? AND product_id=? ORDER BY verified DESC, created_at DESC LIMIT 30", T(s), id) : [];
  const cm = commerceOf(s);
  const related = all("SELECT * FROM products WHERE tenant_id=? AND dept=? AND id!=? AND lifecycle='published' ORDER BY position LIMIT 12", T(s), p.dept, id).map(r => storeView({ ...r, about: [] }, cm));
  const skus = all("SELECT * FROM skus WHERE tenant_id=? AND product_id=? AND active=1", T(s), id).map(k => ({ ...k, identity: J(k.identity), variant: J(k.variant) }));
  const rels = all("SELECT * FROM relationships WHERE tenant_id=? AND from_id=?", T(s), id).map(r => ({ type: r.type, to: get("SELECT id,title,price,emoji,hue,stock,type FROM products WHERE tenant_id=? AND id=? AND lifecycle='published'", T(s), r.to_id) })).filter(r => r.to);
  const hist = r => { const five = Math.min(92, Math.max(45, Math.round((r - 3) * 30 + 40))); const four = Math.round((100 - five) * 0.5); const three = Math.round((100 - five - four) * 0.5); const two = Math.round((100 - five - four - three) * 0.5); return { 5: five, 4: four, 3: three, 2: two, 1: 100 - five - four - three - two }; };
  const node0 = p.node_id ? get("SELECT key FROM taxonomy WHERE id=?", p.node_id) : null;
  const ivk = (node0 ? String(node0.key) : "").split(".")[0] || (DEPT_TO_INDUSTRY || {})[p.dept] || p.dept;
  const prof = (rl("verticalTypeOf") || {})[ivk] || {}; const vctx = rl("verticalContexts") || {};
  const contexts = { tax: (vctx.tax || []).filter(x => x.key === prof.tax), invoice: (vctx.invoice || []).filter(x => x.key === prof.invoice), payment: (vctx.payment || []).filter(x => (prof.payment || []).includes(x.key)) };
  /* localization + compliance + serialization + variant groups (universal model) */
  const locale = url.searchParams.get("locale") || cm.locale;
  const locRow = get("SELECT * FROM localizations WHERE tenant_id=? AND entity='product' AND ref_id=? AND locale=? AND active=1", T(s), id, locale);
  let pView = p, localized = false;
  if (locRow) {
    localized = true; pView = { ...p };
    if (locRow.name) pView.title = locRow.name;
    const bl = J(locRow.bullets, null); if (Array.isArray(bl) && bl.length) pView.about = bl;
    if (locRow.description) pView.seo = JSON.stringify({ ...J(pView.seo, {}), description: locRow.description });
  }
  const compliance = all("SELECT kind,code,issuer,jurisdiction,status,valid_from,valid_to,doc_media FROM compliance_records WHERE tenant_id=? AND scope='product' AND ref_id=? ORDER BY status,valid_to", T(s), id);
  const serRows = all("SELECT status, COUNT(*) n FROM serialized_items WHERE tenant_id=? AND product_id=? GROUP BY status", T(s), id);
  const serialized = serRows.length ? { total: serRows.reduce((n, r) => n + r.n, 0), by_status: serRows.reduce((o, r) => (o[r.status] = r.n, o), {}) } : null;
  const variant_groups = all("SELECT * FROM variant_groups WHERE tenant_id=? AND product_id=? AND active=1 ORDER BY position,id", T(s), id)
    .map(g => ({ id: g.id, name: g.name, axis: g.axis, attr_key: g.attr_key, options: all("SELECT id,code,name,price,stock,variant FROM skus WHERE tenant_id=? AND group_id=? AND active=1 ORDER BY id", T(s), g.id).map(k => ({ ...k, variant: J(k.variant, {}) })) }));
  const supplier_links = all("SELECT ps.id, ps.supplier_id, ps.supplier_sku, ps.price, ps.lead_days, ps.moq, ps.is_primary, ps.status, s.name supplier_name, s.party_role, s.country FROM product_suppliers ps JOIN suppliers s ON s.id=ps.supplier_id WHERE ps.tenant_id=? AND ps.product_id=? ORDER BY ps.is_primary DESC, ps.price ASC", T(s), id);
  const supplier = supplier_links.find(l => l.is_primary) || supplier_links[0] || null;
  const metaRow = get("SELECT tags, meta FROM entity_meta WHERE tenant_id=? AND entity='product' AND (ref_uid=? OR ref_uid=?)", T(s), p.uid || "", id);
  const tags = metaRow ? J(metaRow.tags, []) : [];
  const buyerEmail = s.user_id ? ((get("SELECT email FROM users WHERE id=?", s.user_id) || {}).email || "") : "";
  const buyerContract = contractPriceFor(T(s), buyerEmail, id, Number.MAX_SAFE_INTEGER);
  json(res, 200, { product: publicProduct(pView), histogram: hist(pView.rating), contexts, industry: ivk || null, reviews: revs.map(rv => ({ id: rv.id, name: rv.name, r: rv.rating, title: rv.title, body: rv.body, verified: !!rv.verified, date: rv.created_at })), related, fbt: related.slice(0, 3), skus, relationships: rels, node: p.node_id ? get("SELECT id,name,level FROM taxonomy WHERE id=?", p.node_id) : null, locale, localized, compliance, serialized, variant_groups, supplier: supplier || null, supplier_links, tags, contract_price: buyerContract != null ? money2(cm, buyerContract) : null });
}

/* ---------------- cart ---------------- */
function logisticsSurcharge(s, lines) {
  if (!mods.hasCap(T(s), "logisticsGuard")) return 0;
  const cfg = mods.moduleConfig(T(s), "logistics-guard");
  const cold = cfg.coldFee != null ? Number(cfg.coldFee) : 6.5, haz = cfg.hazmatFee != null ? Number(cfg.hazmatFee) : 12;
  let fee = 0;
  if (lines.some(i => (i.logistics || {}).shippingClass === "cold_chain")) fee += cold;
  if (lines.some(i => /haz|dangerous/i.test(String((i.logistics || {}).shippingClass || "")))) fee += haz;
  return +fee.toFixed(2);
}
function computeTax(s, c, lines, goodsBase, otherTaxable) {
  return taxmod.computeLegacy({ perLine: mods.hasCap(T(s), "taxPerLine"), taxRate: c.commerce.taxRate, lines, goodsBase, otherTaxable });
}
function cartPayload(s) {
  const cm = commerceOf(s); const c = { ...CFG(s), commerce: cm };
  const owner = ownerFor(s);
  const buyerEmail = s.user_id ? ((get("SELECT email FROM users WHERE id=?", s.user_id) || {}).email || "") : "";
  const rows = all("SELECT product_id, qty, sku_id FROM cart_items WHERE owner=? ORDER BY added_at", owner);
  const items = []; let sub = 0, count = 0; const lines = []; const promoItems = [];
  for (const r of rows) {
    const p = get("SELECT * FROM products WHERE tenant_id=? AND id=?", T(s), r.product_id);
    if (!p) continue;
    p.about = all("SELECT text FROM product_bullets WHERE tenant_id=? AND product_id=? ORDER BY pos", T(s), p.id).map(x => x.text);
    const sku = r.sku_id ? get("SELECT id, code, name, price FROM skus WHERE id=? AND tenant_id=? AND active=1", r.sku_id, T(s)) : null;
    const cp = buyerEmail ? contractPriceFor(T(s), buyerEmail, p.id, r.qty) : null;
    const unit = cp != null ? cp : (sku && sku.price != null ? Number(sku.price) : effectivePrice(p, r.qty));
    items.push({ product: storeView(p, c.commerce), qty: r.qty, sku_id: sku ? sku.id : null, sku: sku ? { id: sku.id, code: sku.code, name: sku.name } : null, unit: money2(c.commerce, unit), unitBase: unit });
    lines.push({ unitBase: unit, qty: r.qty, logistics: J(p.logistics), tax_rule: J(p.tax_rule) });
    promoItems.push({ product: publicProduct(p), qty: r.qty });
    sub += unit * r.qty; count += r.qty;
  }
  const saved = all("SELECT product_id FROM saved_items WHERE owner=? ORDER BY added_at", owner)
    .map(r => { const p = get("SELECT * FROM products WHERE tenant_id=? AND id=?", T(s), r.product_id); if (!p) return null; p.about = []; return storeView(p, c.commerce); }).filter(Boolean);
  const promo = applyPromos(T(s), promoItems, s.coupon, { owner, currency: c.commerce.currency });
  const freeShip = promo.applied.some(a => a.type === "free_ship");
  const afterPromo = Math.max(0, sub - promo.discount);
  const shipFee = afterPromo >= c.commerce.freeShipThreshold || freeShip ? 0 : (afterPromo > 0 ? c.commerce.shipFee : 0);
  const wBal = mods.hasCap(T(s), "wallet") ? mods.walletBalance(T(s), owner) : 0;
  const surcharge = logisticsSurcharge(s, lines);
  const gift = Math.min(wBal, afterPromo + shipFee + surcharge);
  const tax = computeTax(s, c, lines, afterPromo, shipFee + surcharge - gift);
  const total = +(afterPromo + shipFee + surcharge + tax - gift).toFixed(2);
  const m = c.commerce;
  return { items, saved, count, subBase: sub, sub: money2(m, sub), discountBase: promo.discount, discount: money2(m, promo.discount), creditsEarned: promo.credits || 0, redemptions: promo.redemptions || [], shipBase: shipFee, surchargeBase: surcharge, giftBase: gift, taxBase: tax, totalBase: total, promos: promo.applied, couponsOpen: !!(c.features && c.features.coupons) && !!sec.policy().provisioning.couponsAllowed, shipFee: money2(m, shipFee), gift: money2(m, gift), tax: money2(m, tax), total: money2(m, total), qualifies: afterPromo >= c.commerce.freeShipThreshold || freeShip, currency: { code: m.currency, symbol: m.symbol, decimals: m.decimals, fx: m.fx, base: m.baseCurrency, threshold: c.commerce.freeShipThreshold } };
}
function apiCartGet(req, res, url, s) { json(res, 200, cartPayload(s)); }
function apiCartAdd(req, res, url, s, body) {
  const c = CFG(s);
  const p = get("SELECT id, stock FROM products WHERE tenant_id=? AND id=?", T(s), body.id);
  if (!p) return bad(res, "Unknown product", 404);
  if (p.stock <= 0) return bad(res, "Item is sold out");
  let skuId = null;
  if (body.sku_id != null && body.sku_id !== "") { const sk = get("SELECT id FROM skus WHERE id=? AND product_id=? AND tenant_id=? AND active=1", Number(body.sku_id), p.id, T(s)); if (!sk) return bad(res, "Unknown variant for this product"); skuId = sk.id; }
  const owner = ownerFor(s);
  const qty = Math.max(1, Math.min(c.commerce.cartMaxQty, Number(body.qty) || 1));
  const ex = get("SELECT qty FROM cart_items WHERE owner=? AND product_id=?", owner, p.id);
  if (ex) run("UPDATE cart_items SET qty=?, sku_id=? WHERE owner=? AND product_id=?", Math.min(c.commerce.cartMaxQty, ex.qty + qty), skuId, owner, p.id);
  else run("INSERT INTO cart_items(owner,product_id,qty,sku_id) VALUES(?,?,?,?)", owner, p.id, qty, skuId);
  json(res, 200, cartPayload(s));
}
function apiCartPut(req, res, url, s, body) {
  const c = CFG(s);
  const owner = ownerFor(s);
  const qty = Number(body.qty);
  if (!(qty >= 1 && qty <= c.commerce.cartMaxQty)) return bad(res, "Invalid quantity");
  run("UPDATE cart_items SET qty=? WHERE owner=? AND product_id=?", qty, owner, body.id);
  json(res, 200, cartPayload(s));
}
function apiCartDel(req, res, url, s, body, id) {
  run("DELETE FROM cart_items WHERE owner=? AND product_id=?", ownerFor(s), id);
  json(res, 200, cartPayload(s));
}
function apiSavedAdd(req, res, url, s, body) {
  if (!CFG(s).features.saveForLater) return bad(res, "Save for later is disabled", 403);
  const owner = ownerFor(s);
  run("INSERT OR IGNORE INTO saved_items(owner,product_id) VALUES(?,?)", owner, body.id);
  run("DELETE FROM cart_items WHERE owner=? AND product_id=?", owner, body.id);
  json(res, 200, cartPayload(s));
}
function apiSavedDel(req, res, url, s, body, id) {
  run("DELETE FROM saved_items WHERE owner=? AND product_id=?", ownerFor(s), id);
  json(res, 200, cartPayload(s));
}
function apiSavedMove(req, res, url, s, body, id) {
  const owner = ownerFor(s);
  run("DELETE FROM saved_items WHERE owner=? AND product_id=?", owner, id);
  const ex = get("SELECT qty FROM cart_items WHERE owner=? AND product_id=?", owner, id);
  if (ex) run("UPDATE cart_items SET qty=qty+1 WHERE owner=? AND product_id=?", owner, id);
  else run("INSERT INTO cart_items(owner,product_id,qty) VALUES(?,?,1)", owner, id);
  json(res, 200, cartPayload(s));
}

/* ---------------- checkout (gateway-aware) ---------------- */
function planFor(tenantId) {
  const sub = get("SELECT p.* FROM subscriptions s JOIN plans p ON p.id=s.plan_id WHERE s.tenant_id=? AND s.status IN ('active','trialing') ORDER BY s.id DESC", tenantId);
  return sub || get("SELECT name, max_products, max_orders_month FROM plans ORDER BY position LIMIT 1") || { name: "none", max_products: 999999, max_orders_month: 999999 };
}
async function apiCheckout(req, res, url, s, body) {
  const c = { ...CFG(s), commerce: commerceOf(s) };
  const cart = cartPayload(s);
  if (!cart.items.length) return bad(res, "Bag is empty", 400);
  if (mods.hasCap(T(s), "identityPro") && mods.moduleConfig(T(s), "identity-pro").requireLoginCheckout === true && !s.user_id)
    return bad(res, "This store requires customers to sign in before checkout (Identity Pro module)", 403);
  const name = String(body.name || "").trim(), address = String(body.address || "").trim(), city = String(body.city || "").trim();
  if (!name || !address || !city) return bad(res, "Shipping address is incomplete", 422);
  const plan = planFor(T(s));
  const monthOrders = get("SELECT COUNT(*) c FROM orders WHERE tenant_id=? AND created_at >= date('now','start of month')", T(s)).c;
  if (monthOrders >= plan.max_orders_month) return bad(res, "Monthly order limit reached on the " + plan.name + " plan — upgrade to continue selling", 402);
  const gwId = String(body.gateway || "");
  const gw = enabledGateways(T(s)).find(g => g.id === gwId && (g.id === "cod" || g.id === "bank" || registry.supports(g.id, (CFG(s).commerce.country || "US").toUpperCase())));
  if (!gw) return bad(res, "Select a valid payment method available in your jurisdiction", 422);
  const method = String(body.method || (gw.methods || ["card"])[0]);
  const carrier = String(body.carrier || "house-std");
  const carrierObj = enabledCarriers(T(s)).find(x => x.id === carrier);
  const freeShip = cart.qualifies || cart.promos.some(a => a.type === "free_ship");
  const shipFee = freeShip ? 0 : (carrierObj ? (carrierObj.baseFee || c.commerce.shipFee) : c.commerce.shipFee);
  const eta = carrierObj && carrierObj.eta ? carrierObj.eta[1] : c.commerce.daysStandard;
  const lines = cart.items.map(x => ({ unitBase: x.unitBase, qty: x.qty, logistics: x.product.logistics, tax_rule: x.product.tax_rule }));
  const subBase = +lines.reduce((n, l) => n + l.unitBase * l.qty, 0).toFixed(2);
  const netBase = +(subBase - (cart.discountBase || 0)).toFixed(2);
  const surcharge = logisticsSurcharge(s, lines);
  const wBal = mods.hasCap(T(s), "wallet") ? mods.walletBalance(T(s), ownerFor(s)) : 0;
  const giftUsed = Math.min(wBal, netBase + shipFee + surcharge);
  const tax = computeTax(s, c, lines, netBase, shipFee + surcharge - giftUsed);
  const total = +(netBase + shipFee + surcharge + tax - giftUsed).toFixed(2);
  const num = `112-${Math.floor(1000000 + Math.random() * 8999999)}-${Math.floor(1000000 + Math.random() * 8999999)}`;
  const netSub = netBase;
  const m = c.commerce;
  const r = run(`INSERT INTO orders(tenant_id,owner,num,name,address,city,state,zip,ship_option,pay_method,sub,ship_fee,gift_used,tax,total,eta_days,status,currency,fx)
                 VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,'processing',?,?)`,
    T(s), ownerFor(s), num, name, address, city, String(body.state || ""), String(body.zip || s.zip), carrier, gw.id, money2(m, netSub), money2(m, shipFee), money2(m, giftUsed), money2(m, tax), money2(m, total), eta, m.currency, m.fx);
  const oid = Number(r.lastInsertRowid);
  for (const it of cart.items) run("INSERT INTO order_items(order_id,product_id,qty,price,sku_id) VALUES(?,?,?,?,?)", oid, it.product.id, it.qty, it.sku_id ? it.unit : it.product.p, it.sku_id || null);
  const sim = await settlePayment(T(s), gw, total, c.commerce.currency, num);
  run("INSERT INTO payments(tenant_id,kind,order_id,gateway,method,amount,currency,fee,status,txn_ref) VALUES(?,?,?,?,?,?,?,?,?,?)",
    T(s), "order", oid, gw.id, method, total, c.commerce.currency, sim.fee, sim.status, sim.ref);
  if (sim.status === "failed") { run("UPDATE orders SET status='cancelled' WHERE id=?", oid); return bad(res, "Payment was declined by the gateway: " + (sim.error || "declined"), 402); }
  const vtOf = rl("verticalTypeOf") || {}; const vctx = rl("verticalContexts") || {};
  const allow = { tax: null, invoice: null, payment: null };
  const explicit = body.contexts || {}; const cErrs = [];
  for (const it of cart.items) {
    const node = it.product.node_id ? get("SELECT key FROM taxonomy WHERE id=?", it.product.node_id) : null;
    const ivk = (node ? String(node.key) : "").split(".")[0] || (DEPT_TO_INDUSTRY || {})[it.product.d] || it.product.d;
    const prof = vtOf[ivk] || {};
    const sets = { tax: new Set(prof.tax ? [prof.tax] : []), invoice: new Set(prof.invoice ? [prof.invoice] : []), payment: new Set(prof.payment || []) };
    for (const g of ["tax", "invoice", "payment"]) {
      if (!sets[g].size) continue;
      allow[g] = allow[g] === null ? sets[g] : new Set([...allow[g]].filter(x => sets[g].has(x)));
      const want = String(explicit[g] || "");
      if (want && !sets[g].has(want)) cErrs.push(it.product.t.slice(0, 30) + ": " + g + " context " + want + " not valid for " + (ivk || "general"));
      if (want) { const def = (vctx[g] || []).find(x => x.key === want); if (def && def.type !== g) cErrs.push("context kind mismatch"); }
    }
  }
  const contexts = {};
  for (const g of ["tax", "invoice", "payment"]) {
    const want = String(explicit[g] || "");
    if (want) contexts[g] = [want];
    else if (allow[g] && allow[g].size) contexts[g] = [[...allow[g]].sort()[0]];
  }
  if (cErrs.length) return bad(res, [...new Set(cErrs)].slice(0, 3).join("; "), 422);
  run("UPDATE orders SET contexts=? WHERE id=?", JSON.stringify(contexts), oid);
  run("DELETE FROM cart_items WHERE owner=?", ownerFor(s));
  run("UPDATE tenant_state SET coupon='' WHERE sid=? AND tenant_id=?", s.sid, T(s)); s.coupon = "";
  if (giftUsed > 0) mods.walletSet(T(s), ownerFor(s), Math.max(0, wBal - giftUsed));
  try { offers.redeem({ tenantId: T(s), owner: ownerFor(s), channel: "commerce", currency: c.commerce.currency }, { credits: cart.creditsEarned || 0, redemptions: cart.redemptions || [] }, { order_id: oid, order_num: num }); } catch (e) { console.error("offer redeem:", e.message); }
  logAction(s, "checkout.complete", "order", num, { gateway: gw.id, method, total, txn: sim.ref }, req);
  notify(T(s), `New order ${num}`, `${name} — ${total} ${c.commerce.currency} via ${gw.name}`);
  try { run("UPDATE orders SET trace_id=? WHERE id=?", s.trace || null, oid); } catch (e) { }
  emitEvent(T(s), "order.created", { num, total: money2(m, total), currency: m.currency }, num);
  if (sim.status === "captured") emitEvent(T(s), "order.paid", { num, total: money2(m, total), txn_ref: sim.ref, gateway: gw.id }, num);
  json(res, 200, { order: { num, total: money2(m, total), currency: m.currency, fx: m.fx, sub: money2(m, netSub), discount: money2(m, cart.discountBase || 0), surcharge: money2(m, surcharge), promos: cart.promos, shipFee: money2(m, shipFee), tax: money2(m, tax), gift_used: money2(m, giftUsed), eta, contexts, gateway: gw.id, gateway_name: gw.name, txn_ref: sim.ref, payment_status: sim.status, date: new Date().toISOString(), addr: `${name}, ${address}, ${city}`, items: cart.items.map(x => ({ id: x.product.id, qty: x.qty, price: x.unit })) } });
}
function apiOrders(req, res, url, s) {
  const orders = all("SELECT * FROM orders WHERE owner=? ORDER BY created_at DESC", ownerFor(s));
  for (const o of orders) {
    o.items = all("SELECT product_id id, qty, price FROM order_items WHERE order_id=?", o.id).map(it => {
      const p = get("SELECT * FROM products WHERE tenant_id=? AND id=?", T(s), it.id);
      return { id: it.id, qty: it.qty, price: it.price, product: p ? publicProduct({ ...p, about: [] }) : null };
    });
    const pay = get("SELECT gateway, txn_ref, status FROM payments WHERE tenant_id=? AND order_id=?", T(s), o.id);
    if (pay) o.payment = pay;
  }
  json(res, 200, { orders });
}

/* ---------------- reviews / gifts / viewed ---------------- */
function apiReviewAdd(req, res, url, s, body, id) {
  if (!CFG(s).features.reviews) return bad(res, "Reviews are disabled", 403);
  if (!get("SELECT id FROM products WHERE tenant_id=? AND id=?", T(s), id)) return bad(res, "Unknown product", 404);
  const r = Math.max(1, Math.min(5, Number(body.rating) || 5));
  const name = s.user_id ? get("SELECT name FROM users WHERE id=?", s.user_id).name : "A customer";
  run("INSERT INTO reviews(tenant_id,product_id,user_id,name,rating,title,body,verified) VALUES(?,?,?,?,?,?,?,0)",
    T(s), id, s.user_id, name, r, String(body.title || "My review").slice(0, 80), String(body.body || "Exceptional.").slice(0, 2000));
  logAction(s, "review.create", "review", id, { rating: r });
  json(res, 200, { ok: true });
}
function apiGiftAdd(req, res, url, s, body) {
  const c = CFG(s);
  if (!c.features.giftCards) return bad(res, "Gift cards are disabled", 403);
  if (!mods.hasCap(T(s), "wallet")) return bad(res, "Wallets are not enabled for this store — purchase the Customer Wallets module (Platform → Modules)", 403);
  const amt = Number(body.amount);
  if (!(amt > 0 && amt <= c.commerce.giftMax)) return bad(res, "Invalid amount");
  mods.walletAdd(T(s), mods.ownerFor(s), amt);
  json(res, 200, { balance: mods.walletBalance(T(s), mods.ownerFor(s)) });
}
function apiViewed(req, res, url, s, body) {
  const owner = ownerFor(s);
  run("INSERT OR REPLACE INTO view_history(owner,product_id,seen_at) VALUES(?,?,datetime('now'))", owner, body.id);
  const ids = all("SELECT product_id FROM view_history WHERE owner=? ORDER BY seen_at DESC LIMIT 12", owner).map(r => r.product_id);
  if (ids.length) run(`DELETE FROM view_history WHERE owner=? AND product_id NOT IN ('${ids.join("','")}')`, owner);
  json(res, 200, { viewed: ids });
}

/* ================= DEMO HINTS (data-driven, no hardcoded creds; password shown only if it verifies) ================= */
function platSetting(key, dflt) { try { const r = get("SELECT value FROM platform_settings WHERE key=?", key); return r ? J(r.value, dflt) : dflt; } catch (e) { return dflt; } }
function apiPlatformHint(req, res) {
  if (!sec.policy().demoHints) return json(res, 200, { demo: false });
  const h = platSetting("demo_hint", { enabled: true, platformEmail: "platform@luxora.shop" });
  if (!h.enabled) return json(res, 200, { demo: false });
  const email = String(h.platformEmail || "");
  const cands = (platGet("demo_passwords", { list: [] }).list || []);
  const pw = cands.find(c => verifyPlatformAdmin(email, c)) || null;
  json(res, 200, { demo: true, email, password: pw });
}
function apiHint(req, res, url, s) {
  if (!sec.policy().demoHints) return json(res, 200, { demo: false });
  const h = platSetting("demo_hint", { enabled: true });
  if (!h.enabled) return json(res, 200, { demo: false });
  const adm = get("SELECT email FROM users WHERE tenant_id=? AND role='admin' ORDER BY id LIMIT 1", T(s));
  if (!adm) return json(res, 200, { demo: true, email: null });
  const cands = (platGet("demo_passwords", { list: [] }).list || []);
  const pw = cands.find(c => verifyUser(T(s), adm.email, c)) || null;
  json(res, 200, { demo: true, email: adm.email, password: pw, store: s.tenant.slug });
}

/* ================= MODULE MARKETPLACE (everything is a product) ================= */
/* store-facing marketplace: the store itself purchases modules */
function apiMarket(req, res, url, s) {
  const modules = all("SELECT id,name,category,summary,price,manifest,status FROM modules WHERE status='active' ORDER BY position").map(m => ({ id: m.id, name: m.name, category: m.category, summary: m.summary, price: m.price, capabilities: (J(m.manifest, {}).capabilities || []), fields: (J(m.manifest, {}).fields || []) }));
  json(res, 200, { modules, installed: mods.installed(T(s)).map(m => ({ id: m.module_id, capabilities: (m.manifest.capabilities || []), config: m.config })) });
}
function apiModulePurchase(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const m = mods.moduleRow(String(body.module_id || ""));
  if (!m || m.status !== "active") return bad(res, "Unknown module", 404);
  let invoice = null;
  const was = (mods.installedRow(T(s), m.id) || {}).status === "installed";
  if (!was && m.price > 0) {
    const number = "MOD-" + (1000 + get("SELECT COUNT(*) c FROM invoices").c + 1);
    const r = run("INSERT INTO invoices(tenant_id,number,period_start,period_end,amount,currency,status,paid_at,note) VALUES(?,?,date('now'),date('now'),?,'USD','paid',datetime('now'),?)", T(s), number, m.price, "Module: " + m.name);
    run("INSERT INTO payments(tenant_id,kind,invoice_id,gateway,method,amount,currency,fee,status,txn_ref) VALUES(?,?,?,?,?,?,?,?,?,?)",
      T(s), "module", Number(r.lastInsertRowid), "platform-billing", "invoice", m.price, "USD", 0, "captured", "mod_sim_" + crypto.randomBytes(6).toString("hex"));
    invoice = number;
  }
  mods.applyModule(T(s), m, body.config || {});
  logAction(s, "module.purchase", "tenant_module", T(s) + ":" + m.id, { invoice }, req);
  json(res, 200, { ok: true, invoice });
}
function apiModuleRelease(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const m = mods.moduleRow(String(body.module_id || "")); if (!m) return bad(res, "Unknown module", 404);
  if (mods.hasCap(T(s), "wallet") && m.id === "wallet") return bad(res, "Wallets module has live balances — clear them first", 409);
  mods.unapplyModule(T(s), m);
  logAction(s, "module.release", "tenant_module", T(s) + ":" + m.id, {}, req);
  json(res, 200, { ok: true });
}

function apiPlatformModules(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const modules = all("SELECT * FROM modules ORDER BY position").map(m => ({ ...m, manifest: J(m.manifest, {}) }));
  const installs = all("SELECT tenant_id, module_id, status, config, installed_at FROM tenant_modules");
  json(res, 200, { modules, installs, tenants: all("SELECT id, slug, name FROM tenants ORDER BY id") });
}
function apiModuleInstall(req, res, url, s, body, id) {
  if (!requirePlatform(s, res)) return;
  const m = mods.moduleRow(id);
  if (!m || m.status !== "active") return bad(res, "Unknown module", 404);
  const tid = Number(body.tenant_id);
  if (!get("SELECT id FROM tenants WHERE id=?", tid)) return bad(res, "Unknown store", 404);
  let invoice = null;
  const wasInstalled = (mods.installedRow(tid, id) || {}).status === "installed";
  if (!wasInstalled && m.price > 0) {
    const number = "MOD-" + (1000 + get("SELECT COUNT(*) c FROM invoices").c + 1);
    const r = run("INSERT INTO invoices(tenant_id,number,period_start,period_end,amount,currency,status,paid_at,note) VALUES(?,?,date('now'),date('now'),?,'USD','paid',datetime('now'),?)",
      tid, number, m.price, `Module: ${m.name}`);
    run("INSERT INTO payments(tenant_id,kind,invoice_id,gateway,method,amount,currency,fee,status,txn_ref) VALUES(?,?,?,?,?,?,?,?,?,?)",
      tid, "module", Number(r.lastInsertRowid), "platform-billing", "invoice", m.price, "USD", 0, "captured", `mod_sim_${crypto.randomBytes(6).toString("hex")}`);
    invoice = number;
  }
  const cfg = Object.assign({}, body.config || {});
  mods.applyModule(tid, m, cfg);
  audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "module.install", "tenant_module", `${tid}:${id}`, { invoice }, ipOf(req));
  json(res, 200, { ok: true, module: id, invoice });
}
function apiModuleUninstall(req, res, url, s, body, id) {
  if (!requirePlatform(s, res)) return;
  const m = mods.moduleRow(id); if (!m) return bad(res, "Unknown module", 404);
  mods.unapplyModule(Number(body.tenant_id), m);
  audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "module.uninstall", "tenant_module", `${body.tenant_id}:${id}`, {}, ipOf(req));
  json(res, 200, { ok: true });
}
function apiModuleConfigure(req, res, url, s, body, id) {
  if (!requirePlatform(s, res)) return;
  const m = mods.moduleRow(id); if (!m) return bad(res, "Unknown module", 404);
  const tid = Number(body.tenant_id);
  run("UPDATE tenant_modules SET config=? WHERE tenant_id=? AND module_id=?", JSON.stringify(body.config || {}), tid, id);
  mods.applyModule(tid, m, body.config || {});
  audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "module.configure", "tenant_module", `${tid}:${id}`, { config: Object.keys(body.config || {}) }, ipOf(req));
  json(res, 200, { ok: true });
}
function apiStoreModules(req, res, url, s) {
  json(res, 200, { installed: mods.installed(T(s)).map(m => ({ id: m.module_id, name: m.name, category: m.category, capabilities: (m.manifest.capabilities || []), config: m.config, installed_at: m.installed_at })), capabilities: [...mods.caps(T(s))] });
}
function apiSeoSitemap(req, res, url, s) {
  if (!mods.hasCap(T(s), "seoPro")) return bad(res, "SEO Pro module not installed", 403);
  const prods = all("SELECT id FROM products WHERE tenant_id=? AND lifecycle='published'", T(s)).map(r => `  <url><loc>/product.html?id=${r.id}</loc></url>`).join("\n");
  const deps = all("SELECT key FROM departments WHERE tenant_id=? AND active=1", T(s)).map(r => `  <url><loc>/results.html?dept=${r.key}</loc></url>`).join("\n");
  res.writeHead(200, { "Content-Type": "application/xml; charset=utf-8" });
  res.end(`<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url><loc>/</loc></url>\n${deps}\n${prods}\n</urlset>`);
}
function apiReco(req, res, url, s, body, id) {
  if (!mods.hasCap(T(s), "recoPro")) return bad(res, "Recommendation Engine module not installed", 403);
  let rows = all(`SELECT DISTINCT p.* FROM order_items oi
    JOIN order_items oi2 ON oi.order_id = oi2.order_id
    JOIN orders o ON o.id = oi.order_id AND o.tenant_id = ?
    JOIN products p ON p.tenant_id = o.tenant_id AND p.id = oi2.product_id
    WHERE oi.product_id = ? AND oi2.product_id != ? AND p.lifecycle='published' LIMIT 12`, T(s), id, id);
  if (rows.length < 4) {
    const cur = get("SELECT dept FROM products WHERE tenant_id=? AND id=?", T(s), id);
    rows = all("SELECT * FROM products WHERE tenant_id=? AND dept=? AND id!=? AND lifecycle='published' ORDER BY ratings_count DESC LIMIT 12", T(s), cur ? cur.dept : "", id);
  }
  const cm = commerceOf(s);
  json(res, 200, { items: rows.map(r => storeView({ ...r, about: [] }, cm)) });
}
function apiFacets(req, res, url, s) {
  if (!mods.hasCap(T(s), "listingPro")) return bad(res, "Listing Pro module not installed", 403);
  const { sql, args } = buildSearch(s, url);
  const rows = all(`SELECT brand, dept, price FROM products WHERE ${sql}`, ...args);
  const brands = {}, depts = {}; const buckets = { "0-25": 0, "25-50": 0, "50-100": 0, "100-250": 0, "250+": 0 };
  for (const r of rows) {
    brands[r.brand] = (brands[r.brand] || 0) + 1; depts[r.dept] = (depts[r.dept] || 0) + 1;
    const k = r.price < 25 ? "0-25" : r.price < 50 ? "25-50" : r.price < 100 ? "50-100" : r.price < 250 ? "100-250" : "250+";
    buckets[k]++;
  }
  json(res, 200, { brands: Object.entries(brands).sort((a, b) => b[1] - a[1]).slice(0, 20).map(([k, v]) => ({ brand: k, count: v })), depts: Object.entries(depts).map(([k, v]) => ({ dept: k, count: v })), price: Object.entries(buckets).map(([k, v]) => ({ range: k, count: v })) });
}
function apiBillingPay(req, res, url, s, body, id) {
  return (async () => {
  if (!requireAdmin(s, res)) return;
  if (!mods.hasCap(T(s), "billingPro")) return bad(res, "Billing Pro module not installed — request platform billing instead", 403);
  const inv = get("SELECT * FROM invoices WHERE id=? AND tenant_id=?", Number(id), T(s));
  if (!inv) return bad(res, "Unknown invoice", 404);
  if (inv.status === "paid") return bad(res, "Invoice already paid");
  const gws = enabledGateways(T(s));
  const g = gws.find(x => x.id === String(body.gateway || "")) || gws[0];
  if (!g) return bad(res, "No payment gateway configured", 422);
  const sim = await settlePayment(T(s), g, inv.amount, inv.currency || "USD", inv.number);
  if (sim.status === "failed") return bad(res, "Payment declined: " + (sim.error || "gateway error"), 402);
  run("UPDATE invoices SET status='paid', paid_at=datetime('now') WHERE id=?", inv.id);
  run("INSERT INTO payments(tenant_id,kind,invoice_id,gateway,method,amount,currency,fee,status,txn_ref) VALUES(?,?,?,?,?,?,?,?,?,?)",
    T(s), "invoice", inv.id, g.id, (g.methods || ["card"])[0], inv.amount, inv.currency || "USD", sim.fee, sim.status, sim.ref);
  logAction(s, "invoice.pay", "invoice", inv.number, { gateway: g.id, live: !!sim.live }, req);
  json(res, 200, { ok: true, number: inv.number });
  })();
}

/* ================= FX / CONVERSIONS ================= */
function platGet(key, dflt) { try { const r = get("SELECT value FROM platform_settings WHERE key=?", key); return r ? J(r.value, dflt) : dflt; } catch (e) { return dflt; } }
function platSet(key, val) { run("INSERT INTO platform_settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", key, JSON.stringify(val)); }
function fxRate(from, to) {
  const f = registry.currency(from), t = registry.currency(to);
  if (!f || !t) return null;
  return { from: f, to: t, rate: +((f.usd || 1) / (t.usd || 1)).toFixed(8) };
}
function applyRates(rates, source, note, s) {
  const applied = [], skipped = [];
  for (const [code, usd] of Object.entries(rates || {})) {
    const c = registry.currency(code);
    if (!c) { skipped.push(code); continue; }
    const v = Number(usd);
    if (!(v > 0)) { skipped.push(code); continue; }
    run("UPDATE currencies SET usd=? WHERE code=?", v, c.code);
    run("INSERT INTO fx_rates(currency,usd,source,note) VALUES(?,?,?,?)", c.code, v, source, String(note || "").slice(0, 120));
    applied.push(c.code);
  }
  if (s && s.platform_admin) audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "fx." + source, "currency", applied.join(","), { skipped });
  return { applied, skipped };
}
function httpGetJson(url) {
  return new Promise((resolve, reject) => {
    let u; try { u = new URL(url); } catch (e) { return reject(new Error("Invalid feed URL")); }
    if (!/^https?:$/.test(u.protocol)) return reject(new Error("Feed URL must be http(s)"));
    const lib = u.protocol === "https:" ? require("https") : require("http");
    const req = lib.get(url, res => {
      if (res.statusCode !== 200) { res.resume(); return reject(new Error("Feed returned HTTP " + res.statusCode)); }
      let data = "", len = 0;
      res.on("data", c => { len += c.length; if (len > 1e6) { req.destroy(); return reject(new Error("Feed too large")); } data += c; });
      res.on("end", () => { try { resolve(JSON.parse(data)); } catch (e) { reject(new Error("Feed is not valid JSON")); } });
    });
    req.on("error", e => reject(new Error("Feed fetch failed: " + e.message)));
    req.setTimeout(8000, () => req.destroy(new Error("Feed timeout")));
  });
}
function apiFxConvert(req, res, url, s) {
  const from = (url.searchParams.get("from") || "").toUpperCase(), to = (url.searchParams.get("to") || "").toUpperCase();
  const amount = Number(url.searchParams.get("amount") != null ? url.searchParams.get("amount") : 1);
  const r = fxRate(from, to);
  if (!r) return bad(res, "Unknown currency pair — both codes must exist in the currencies registry", 404);
  json(res, 200, { from, to, amount, rate: r.rate, result: +(amount * r.rate).toFixed(r.to.decimals), decimals: r.to.decimals, asOf: new Date().toISOString() });
}
function apiPlatformFx(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  json(res, 200, { currencies: registry.currencies(), provider: platGet("fx_provider", { provider: "manual", url: "" }), history: all("SELECT * FROM fx_rates ORDER BY id DESC LIMIT 60"), lastSync: platGet("fx_last_sync", null) });
}
function apiPlatformFxRates(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  if (!body || typeof body.rates !== "object") return bad(res, "rates object required, e.g. { \"EUR\": 1.08 }");
  const r = applyRates(body.rates, "manual", body.note, s);
  json(res, 200, { ...r, currencies: registry.currencies() });
}
function apiPlatformFxProvider(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  const provider = body.provider === "feed" ? "feed" : "manual";
  if (provider === "feed" && !/^https?:\/\//.test(String(body.url || ""))) return bad(res, "Feed provider needs an http(s) URL");
  platSet("fx_provider", { provider, url: String(body.url || "").slice(0, 300) });
  audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "fx.provider", "fx", provider, { url: String(body.url || "") });
  json(res, 200, { ok: true, provider: { provider, url: String(body.url || "") } });
}
async function apiPlatformFxSync(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const cfg = platGet("fx_provider", { provider: "manual", url: "" });
  if (cfg.provider !== "feed" || !cfg.url) return bad(res, "No feed provider configured — set it under FX feed first");
  try {
    const data = await httpGetJson(cfg.url);
    const rates = (data && data.rates) || data;
    if (!rates || typeof rates !== "object" || Array.isArray(rates)) return bad(res, "Feed JSON must be {CODE: usdValue} or {rates:{…}}");
    rates.USD = 1;
    const r = applyRates(rates, "feed", cfg.url, s);
    const stamp = new Date().toISOString();
    platSet("fx_last_sync", { at: stamp, applied: r.applied, skipped: r.skipped });
    json(res, 200, { ok: true, ...r, at: stamp });
  } catch (e) { bad(res, e.message, 502); }
}

/* ================= STORE ADMIN ================= */
function apiAdminStats(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  const revenue = get("SELECT COALESCE(SUM(total),0) t FROM orders WHERE tenant_id=?", t).t;
  const orders = get("SELECT COUNT(*) c FROM orders WHERE tenant_id=?", t).c;
  const pending = get("SELECT COUNT(*) c FROM orders WHERE tenant_id=? AND status IN ('processing','shipped')", t).c;
  const customers = get("SELECT COUNT(*) c FROM users WHERE tenant_id=? AND role='customer'", t).c;
  const products = get("SELECT COUNT(*) c FROM products WHERE tenant_id=?", t).c;
  const lowStock = all("SELECT id,title,brand,stock FROM products WHERE tenant_id=? AND stock<=10 ORDER BY stock ASC LIMIT 8", t);
  const recent = all("SELECT id,num,name,total,status,created_at FROM orders WHERE tenant_id=? ORDER BY created_at DESC LIMIT 8", t);
  const daily = all("SELECT date(created_at) d, COALESCE(SUM(total),0) t FROM orders WHERE tenant_id=? AND created_at >= datetime('now','-13 days') GROUP BY date(created_at) ORDER BY d", t);
  const topDepts = all("SELECT p.dept, SUM(oi.qty*oi.price) rev FROM order_items oi JOIN orders o ON o.id=oi.order_id AND o.tenant_id=? JOIN products p ON p.tenant_id=o.tenant_id AND p.id=oi.product_id GROUP BY p.dept ORDER BY rev DESC LIMIT 6", t);
  const payments = all("SELECT gateway, COUNT(*) c, COALESCE(SUM(amount),0) amt, COALESCE(SUM(fee),0) fee FROM payments WHERE tenant_id=? GROUP BY gateway", t);
  json(res, 200, { revenue, orders, pending, customers, products, lowStock, recent, daily, topDepts, payments, plan: planFor(t) });
}
function apiAdminProducts(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const q = (url.searchParams.get("q") || "").toLowerCase();
  let rows = all("SELECT * FROM products WHERE tenant_id=? ORDER BY position", T(s));
  if (q) rows = rows.filter(r => (r.title + " " + r.brand + " " + r.id).toLowerCase().includes(q));
  json(res, 200, { products: rows });
}
function writeBullets(tenantId, pid, arr) {
  run("DELETE FROM product_bullets WHERE tenant_id=? AND product_id=?", tenantId, pid);
  (arr || []).forEach((t, i) => run("INSERT INTO product_bullets(tenant_id,product_id,pos,text) VALUES(?,?,?,?)", tenantId, pid, i, String(t).slice(0, 300)));
}
function apiAdminProductCreate(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  const plan = planFor(t);
  const count = get("SELECT COUNT(*) c FROM products WHERE tenant_id=?", t).c;
  if (count >= plan.max_products) return bad(res, `Plan limit reached (${plan.name}: ${plan.max_products} products). Upgrade to add more.`, 402);
  const title = String(body.title || "").trim(), brand = String(body.brand || "").trim(), dept = String(body.dept || "").trim();
  const price = Number(body.price);
  if (!title || !brand || !(price > 0)) return bad(res, "Title, brand and price are required");
  const id = "LX" + crypto.randomBytes(4).toString("hex").toUpperCase();
  const list = Number(body.list) > price ? Number(body.list) : null;
  const pos = get("SELECT COALESCE(MAX(position),0) m FROM products WHERE tenant_id=?", t).m + 1;
  run(`INSERT INTO products(tenant_id,id,title,brand,dept,price,list_price,rating,ratings_count,emoji,hue,priority,stock,flags,keywords,deal_pct,position)
       VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`,
    t, id, title, brand, dept, price, list, Math.min(5, Math.max(0, Number(body.rating) || 4.5)), Math.max(0, Number(body.count) || 0),
    String(body.emoji || "🛍️").slice(0, 4), Math.floor(Math.random() * 360), body.priority ? 1 : 0, Math.max(0, Number(body.stock) || 0),
    String(body.flags || ""), String(body.keywords || title.toLowerCase()), list ? Math.round((1 - price / list) * 100) : 0, pos);
  writeBullets(t, id, body.about);
  logAction(s, "product.create", "product", id, { title, price });
  json(res, 200, { product: get("SELECT * FROM products WHERE tenant_id=? AND id=?", t, id) });
}
function apiAdminProductUpdate(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  const p = get("SELECT * FROM products WHERE tenant_id=? AND id=?", t, id);
  if (!p) return bad(res, "Unknown product", 404);
  const price = body.price != null ? Number(body.price) : p.price;
  const list = body.list != null ? (Number(body.list) > price ? Number(body.list) : null) : p.list_price;
  run(`UPDATE products SET title=?, brand=?, dept=?, price=?, list_price=?, rating=?, ratings_count=?, emoji=?, h=?, priority=?, stock=?, flags=?, keywords=?, deal_pct=? WHERE tenant_id=? AND id=?`,
    body.title != null ? String(body.title).trim() : p.title, body.brand != null ? String(body.brand).trim() : p.brand,
    body.dept != null ? String(body.dept) : p.dept, price, list,
    body.rating != null ? Math.min(5, Math.max(0, Number(body.rating))) : p.rating,
    body.count != null ? Math.max(0, Number(body.count)) : p.ratings_count,
    body.emoji != null ? String(body.emoji).slice(0, 4) : p.emoji,
    body.hue != null ? Number(body.hue) % 360 : p.hue,
    body.priority != null ? (body.priority ? 1 : 0) : p.priority,
    body.stock != null ? Math.max(0, Number(body.stock)) : p.stock,
    body.flags != null ? String(body.flags) : p.flags,
    body.keywords != null ? String(body.keywords) : p.keywords,
    list ? Math.round((1 - price / list) * 100) : 0, t, id);
  if (body.about) writeBullets(t, id, body.about);
  logAction(s, "product.update", "product", id, { fields: Object.keys(body) });
  json(res, 200, { product: get("SELECT * FROM products WHERE tenant_id=? AND id=?", t, id) });
}
function apiAdminProductDelete(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  if (!get("SELECT id FROM products WHERE tenant_id=? AND id=?", t, id)) return bad(res, "Unknown product", 404);
  run("DELETE FROM products WHERE tenant_id=? AND id=?", t, id);
  run("DELETE FROM product_bullets WHERE tenant_id=? AND product_id=?", t, id);
  run("DELETE FROM reviews WHERE tenant_id=? AND product_id=?", t, id);
  logAction(s, "product.delete", "product", id);
  json(res, 200, { ok: true });
}
function apiAdminOrders(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  const orders = all("SELECT * FROM orders WHERE tenant_id=? ORDER BY created_at DESC LIMIT 200", t);
  for (const o of orders) {
    o.items = all("SELECT product_id id, qty, price FROM order_items WHERE order_id=?", o.id).map(it => {
      const p = get("SELECT title,brand,emoji,hue FROM products WHERE tenant_id=? AND id=?", t, it.id);
      return { id: it.id, qty: it.qty, price: it.price, product: p || null };
    });
    const pay = get("SELECT gateway, method, txn_ref, status, fee FROM payments WHERE tenant_id=? AND order_id=?", t, o.id);
    if (pay) o.payment = pay;
  }
  json(res, 200, { orders });
}
function apiAdminOrderStatus(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const allowed = ["processing", "shipped", "delivered", "cancelled"];
  if (!allowed.includes(body.status)) return bad(res, "Invalid status");
  const r = run("UPDATE orders SET status=? WHERE id=? AND tenant_id=?", body.status, Number(id), T(s));
  if (!r.changes) return bad(res, "Unknown order", 404);
  logAction(s, "order.status", "order", id, { status: body.status });
  json(res, 200, { ok: true });
}
function apiAdminUsers(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  json(res, 200, { users: all(`SELECT id,name,email,role,created_at,(SELECT COUNT(*) FROM orders o WHERE o.owner='t${t}:u:'||users.id) orders,(SELECT COALESCE(SUM(total),0) FROM orders o WHERE o.owner='t${t}:u:'||users.id) spend FROM users WHERE tenant_id=? ORDER BY created_at DESC`, t) });
}
function apiAdminUserDelete(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const u = get("SELECT * FROM users WHERE id=? AND tenant_id=?", Number(id), T(s));
  if (!u) return bad(res, "Unknown user", 404);
  if (u.role === "admin") return bad(res, "Store admins cannot be deleted here");
  run("DELETE FROM users WHERE id=?", u.id);
  run("DELETE FROM cart_items WHERE owner=?", `t${T(s)}:u:${u.id}`);
  run("UPDATE sessions SET user_id=NULL WHERE user_id=?", u.id);
  logAction(s, "user.delete", "user", id, { email: u.email });
  json(res, 200, { ok: true });
}
function apiAdminReviews(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { reviews: all(`SELECT rv.id, rv.product_id, rv.name, rv.rating, rv.title, rv.body, rv.verified, rv.created_at, p.title product_title FROM reviews rv LEFT JOIN products p ON p.tenant_id=rv.tenant_id AND p.id=rv.product_id WHERE rv.tenant_id=? ORDER BY rv.created_at DESC LIMIT 100`, T(s)) });
}
function apiAdminReviewDelete(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  run("DELETE FROM reviews WHERE id=? AND tenant_id=?", Number(id), T(s));
  logAction(s, "review.delete", "review", id);
  json(res, 200, { ok: true });
}
function apiAdminSettingsGet(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { settings: CFG(s), defaults: settings.DEFAULTS, countries: registry.countries(), taxModes: registry.taxModes(), currencies: registry.currencies() });
}
function apiAdminSettingsPut(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  if (body.commerce) for (const k of ["currency", "symbol", "locale", "taxMode", "taxRate", "decimals"]) if (body.commerce[k] === "" || body.commerce[k] == null) body.commerce[k] = null;
  if (body.commerce && body.commerce.currency && !registry.currency(body.commerce.currency)) return bad(res, "Unknown currency — pick from the currencies registry (Geo console)");
  if (body.features) {
    const pol = sec.policy().provisioning;
    if (body.features.coupons === true && !pol.couponsAllowed) return bad(res, "Coupons are disabled by platform policy (Platform → Provisioning)", 403);
    if (body.features.fiscalSelection === true && !pol.fiscalContextsAllowed) return bad(res, "Customer-facing fiscal context selection is disabled by platform policy", 403);
  }
  if (body.commerce && body.commerce.currency && !sec.policy().provisioning.currencyOverridesAllowed) {
    const co = registry.country((CFG(s).commerce.country || "US"));
    if (body.commerce.currency !== co.currency) return bad(res, "Currency overrides are disabled by platform policy (allow under Platform → Provisioning)", 403);
  }
  const cur0 = CFG(s);
  const merged = {};
  for (const [k, v] of Object.entries(body || {})) merged[k] = settings.deepMerge(cur0[k], v);
  settings.save(T(s), merged);
  logAction(s, "settings.update", "settings", T(s), { sections: Object.keys(body || {}) });
  json(res, 200, { settings: CFG(s) });
}
function apiAdminSettingsReset(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  settings.reset(T(s));
  logAction(s, "settings.reset", "settings", T(s));
  json(res, 200, { settings: CFG(s) });
}
function apiAdminDepartments(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { departments: all("SELECT * FROM departments WHERE tenant_id=? ORDER BY position", T(s)) });
}
function apiAdminDeptSave(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  const key = String(body.key || "").trim().toLowerCase().replace(/[^a-z0-9_]/g, "");
  if (!key || !body.label) return bad(res, "Key and label required");
  const ex = get("SELECT key FROM departments WHERE tenant_id=? AND key=?", t, key);
  if (ex) run("UPDATE departments SET label=?, icon=?, active=?, position=? WHERE tenant_id=? AND key=?", String(body.label), String(body.icon || "🏷️"), body.active === 0 ? 0 : 1, Number(body.position) || 0, t, key);
  else run("INSERT INTO departments(tenant_id,key,label,icon,active,position) VALUES(?,?,?,?,?,?)", t, key, String(body.label), String(body.icon || "🏷️"), body.active === 0 ? 0 : 1, get("SELECT COALESCE(MAX(position),0) m FROM departments WHERE tenant_id=?", t).m + 1);
  logAction(s, "department.save", "department", key);
  json(res, 200, { departments: all("SELECT * FROM departments WHERE tenant_id=? ORDER BY position", t) });
}
function apiAdminDeptDelete(req, res, url, s, body, key) {
  if (!requireAdmin(s, res)) return;
  if (get("SELECT COUNT(*) c FROM products WHERE tenant_id=? AND dept=?", T(s), key).c > 0) return bad(res, "Department still has products — move them first");
  run("DELETE FROM departments WHERE tenant_id=? AND key=?", T(s), key);
  logAction(s, "department.delete", "department", key);
  json(res, 200, { ok: true });
}
function apiAdminBanners(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { banners: all("SELECT * FROM home_banners WHERE tenant_id=? ORDER BY position", T(s)) });
}
function apiAdminBannerSave(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  if (!body.title) return bad(res, "Title required");
  const t = T(s);
  const vals = [String(body.title), String(body.subtitle || ""), String(body.cta || "Discover"), Number(body.hue) || 210, String(body.dept || ""), body.active === 0 ? 0 : 1, Number(body.position) || 0];
  if (id) run("UPDATE home_banners SET title=?,subtitle=?,cta=?,hue=?,dept=?,active=?,position=? WHERE id=? AND tenant_id=?", ...vals, Number(id), t);
  else run("INSERT INTO home_banners(tenant_id,title,subtitle,cta,hue,dept,active,position) VALUES(?,?,?,?,?,?,?,?)", t, ...vals);
  logAction(s, "banner.save", "home_banner", id || "new");
  json(res, 200, { banners: all("SELECT * FROM home_banners WHERE tenant_id=? ORDER BY position", t) });
}
function apiAdminBannerDelete(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  run("DELETE FROM home_banners WHERE id=? AND tenant_id=?", Number(id), T(s));
  logAction(s, "banner.delete", "home_banner", id);
  json(res, 200, { ok: true });
}
function apiAdminCards(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { cards: all("SELECT * FROM home_cards WHERE tenant_id=? ORDER BY position", T(s)) });
}
function apiAdminCardSave(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  if (!body.title || !body.dept) return bad(res, "Title and department required");
  const tiles = Array.isArray(body.tiles) ? JSON.stringify(body.tiles.slice(0, 4)) : "[]";
  const vals = [String(body.title), String(body.dept), tiles, body.active === 0 ? 0 : 1, Number(body.position) || 0];
  if (id) run("UPDATE home_cards SET title=?,dept=?,tiles=?,active=?,position=? WHERE id=? AND tenant_id=?", ...vals, Number(id), t);
  else run("INSERT INTO home_cards(tenant_id,title,dept,tiles,active,position) VALUES(?,?,?,?,?,?)", t, ...vals);
  logAction(s, "card.save", "home_card", id || "new");
  json(res, 200, { cards: all("SELECT * FROM home_cards WHERE tenant_id=? ORDER BY position", t) });
}
function apiAdminCardDelete(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  run("DELETE FROM home_cards WHERE id=? AND tenant_id=?", Number(id), T(s));
  logAction(s, "card.delete", "home_card", id);
  json(res, 200, { ok: true });
}
function apiAdminAccount(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const u = get("SELECT * FROM users WHERE id=?", s.user_id);
  if (body.password) {
    const perr = sec.checkPassword(String(body.password), u.email);
    if (perr) return bad(res, perr);
    if (passwordReused(T(s), u.email, String(body.password))) return bad(res, "You cannot reuse a previous password", 422);
    setUserPassword(u.id, String(body.password), u.email);
    logAction(s, "account.password", "user", u.id, { upgraded: true });
  }
  if (body.email) {
    const email = String(body.email).trim().toLowerCase();
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return bad(res, "Invalid email");
    if (get("SELECT id FROM users WHERE tenant_id=? AND email=? AND id!=?", T(s), email, u.id)) return bad(res, "Email already in use", 409);
    run("UPDATE users SET email=? WHERE id=?", email, u.id);
    logAction(s, "account.email", "user", u.id, { email });
  }
  json(res, 200, { ok: true });
}

/* ---------------- store: gateways / payments / billing / audit / monitor ---------------- */
function maskConfig(g) {
  const cfg = { ...(g.config || {}) };
  return cfg;
}
function apiAdminGateways(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  const c = CFG(s);
  const country = registry.countryProfile(CFG(s).commerce.country || "US");
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
  const t = T(s);
  const list = Array.isArray(body.gateways) ? body.gateways : [];
  run("DELETE FROM tenant_gateways WHERE tenant_id=? AND provider_id NOT LIKE 'ship:%' AND provider_id NOT LIKE 'notify:%'", t);
  list.forEach((g, i) => {
    const cfg = {};
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
    detail = ping.live ? " live verified" : "";
  }
  logAction(s, "gateway.test", "gateway", id, { ok, mode: row && row.mode });
  json(res, 200, { ok, message: ok ? `✓ ${gw.name} ${row.mode === "live" ? "live" + detail : "sandbox"} connection verified` : `Missing credentials: ${missing.map(m => m.label).join(", ")}` });
  })();
}
function apiAdminPayments(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { payments: all("SELECT * FROM payments WHERE tenant_id=? ORDER BY created_at DESC LIMIT 200", T(s)) });
}
function apiAdminPaymentRefund(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const p = get("SELECT * FROM payments WHERE id=? AND tenant_id=?", Number(id), T(s));
  if (!p) return bad(res, "Unknown payment", 404);
  if (p.status !== "captured") return bad(res, "Only captured payments can be refunded");
  run("UPDATE payments SET status='refunded' WHERE id=?", p.id);
  let claw = null; if (p.order_id) { const ord = get("SELECT num FROM orders WHERE id=?", p.order_id); try { claw = offers.reverseRedemption(T(s), { order_id: p.order_id, order_num: ord && ord.num }); } catch (e) { console.error("clawback:", e.message); } }
  logAction(s, "payment.refund", "payment", p.id, { amount: p.amount, gateway: p.gateway, clawback: claw && claw.voided });
  if (p.order_id) { const onum = (get("SELECT num FROM orders WHERE id=?", p.order_id) || {}).num; emitEvent(T(s), "order.refunded", { payment_id: p.id, amount: p.amount, num: onum }, onum); }
  json(res, 200, { ok: true, clawback: claw && claw.voided || 0 });
}
function apiAdminBilling(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  json(res, 200, {
    subscription: get(`SELECT s.status, s.started_at, s.renews_at, p.name plan, p.price_month, p.currency, p.max_products, p.max_orders_month FROM subscriptions s JOIN plans p ON p.id=s.plan_id WHERE s.tenant_id=? ORDER BY s.id DESC`, t) || null,
    invoices: all("SELECT * FROM invoices WHERE tenant_id=? ORDER BY issued_at DESC", t),
    usage: { products: get("SELECT COUNT(*) c FROM products WHERE tenant_id=?", t).c, ordersMonth: get("SELECT COUNT(*) c FROM orders WHERE tenant_id=? AND created_at >= date('now','start of month')", t).c }
  });
}
function apiAdminAudit(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { entries: all("SELECT * FROM audit_log WHERE tenant_id=? ORDER BY created_at DESC LIMIT 200", T(s)) });
}
function apiAdminMonitor(req, res, url, s, body, metrics) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, metrics.snapshot(T(s)));
}
function apiAdminCustomProviders(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { providers: all("SELECT * FROM custom_providers WHERE scope='tenant' AND tenant_id=?", T(s)) });
}
function apiAdminCustomProviderAdd(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const m = body.manifest;
  if (!m || !m.id || !m.name) return bad(res, "Manifest needs id and name");
  const kind = rl("providerKinds").includes(body.kind) ? body.kind : "payment";
  run("INSERT INTO custom_providers(scope,tenant_id,kind,manifest) VALUES('tenant',?,?,?)", T(s), kind, JSON.stringify(m));
  logAction(s, "provider.add", "custom_provider", m.id, { kind });
  json(res, 200, { ok: true });
}
function apiAdminCustomProviderDelete(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  run("DELETE FROM custom_providers WHERE id=? AND scope='tenant' AND tenant_id=?", Number(id), T(s));
  json(res, 200, { ok: true });
}

/* ================= SECURITY: scorecard · chain · keys (L6/L7) ================= */
const POLICY_KEYS = ["minPasswordLength", "requireLetterDigit", "blockCommon", "lockoutThreshold", "lockoutBaseSec", "lockoutCapSec", "authPerMin", "apiPerMin", "csrfEnabled", "hsts", "demoHints", "cspInlineStyles"];
function apiPlatformConfigGet(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  json(res, 200, { policy: sec.policy(), defaults: sec.DEFAULT_POLICY, provisionedAt: platGet("provisioned_at", null), pepperConfigured: !!process.env.LUXORA_PEPPER, tlsBoot: process.env.LUX_TLS === "1", keyInfo: sec.keyInfo() });
}
function apiPlatformConfigPut(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  const patch = {};
  for (const k of POLICY_KEYS) if (body[k] !== undefined) patch[k] = body[k];
  if (body.kdfV2) patch.kdfV2 = { logN: Number(body.kdfV2.logN) || 17, r: Number(body.kdfV2.r) || 8, p: Number(body.kdfV2.p) || 2 };
  if (body.provisioning) patch.provisioning = { defaultPlanId: Number(body.provisioning.defaultPlanId) || 1, seedCatalogByDefault: !!body.provisioning.seedCatalogByDefault, sandboxGatewaysByDefault: body.provisioning.sandboxGatewaysByDefault !== false, currencyOverridesAllowed: !!body.provisioning.currencyOverridesAllowed, couponsAllowed: body.provisioning.couponsAllowed !== false, fiscalContextsAllowed: !!body.provisioning.fiscalContextsAllowed, globalOffersAllowed: body.provisioning.globalOffersAllowed !== false };
  const first = !platGet("provisioned_at", null);
  const p = sec.setPolicy(patch);
  if (first) run("INSERT INTO platform_settings(key,value) VALUES('provisioned_at',?)", JSON.stringify(new Date().toISOString()));
  logAction(s, "platform.provision", "policy", first ? "initial" : "update", { changed: Object.keys(patch).join(",") }, req);
  json(res, 200, { policy: p, provisionedAt: platGet("provisioned_at", null) });
}
function apiPlatformSecurity(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  json(res, 200, { layers: sec.scorecard({ tls: !!process.env.LUX_TLS, keyInfo: sec.keyInfo(), pepper: !!process.env.LUXORA_PEPPER }), keyInfo: sec.keyInfo(), chain: auditChainVerify(null).ok ? "intact" : "BROKEN" });
}
function apiPlatformChainVerify(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const tid = url.searchParams.get("tenant");
  json(res, 200, tid ? auditChainVerify(Number(tid)) : auditChainVerify(null));
}
function apiPlatformKeyRotate(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const v = sec.rotateKey();
  audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "keys.rotate", "platform", v, {});
  json(res, 200, { ok: true, version: v, keys: sec.keyInfo() });
}
function apiAdminChainVerify(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, auditChainVerify(T(s)));
}

/* ================= PLATFORM ================= */
function apiPlatformLogin(req, res, url, s, body) {
  const email = String(body.email || "").trim();
  const lock = sec.lockState(email);
  if (lock.locked) return bad(res, "Account temporarily locked — retry in " + lock.retryAfterSec + "s", 423);
  const a = verifyPlatformAdmin(email, String(body.password || ""));
  if (!a) { sec.noteLoginFail(email);
    if (get("SELECT id FROM users WHERE email=? LIMIT 1", email.toLowerCase())) return bad(res, "That is a store-console account — use /admin.html for that store", 401);
    return bad(res, "Invalid platform credentials", 401);
  }
  const ptid = crypto.randomBytes(20).toString("hex");
  run("INSERT INTO platform_sessions(ptid, admin_id, expires_at) VALUES(?,?,datetime('now','+12 hours'))", ptid, a.id);
  res.setHeader("Set-Cookie", `azp=${ptid}; Path=/; HttpOnly; SameSite=Lax; Max-Age=43200`);
  sec.noteLoginOk(email);
  audit(null, "platform", a.id, a.email, "platform.login", "platform", null, {});
  json(res, 200, { ok: true, admin: { id: a.id, name: a.name, email: a.email } });
}
function apiPlatformLogout(req, res, url, s) {
  if (s.ptid) run("DELETE FROM platform_sessions WHERE ptid=?", s.ptid);
  res.setHeader("Set-Cookie", "azp=; Path=/; Max-Age=0");
  json(res, 200, { ok: true });
}
function apiPlatformMe(req, res, url, s) {
  json(res, 200, { admin: s.platform_admin || null });
}
function apiPlatformTenants(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const tenants = all(`SELECT t.*, (SELECT COUNT(*) FROM products p WHERE p.tenant_id=t.id) products, (SELECT COUNT(*) FROM orders o WHERE o.tenant_id=t.id) orders,
    (SELECT COALESCE(SUM(o.total),0) FROM orders o WHERE o.tenant_id=t.id) gmv,
    (SELECT p.name FROM subscriptions s JOIN plans p ON p.id=s.plan_id WHERE s.tenant_id=t.id ORDER BY s.id DESC) plan,
    (SELECT s.status FROM subscriptions s WHERE s.tenant_id=t.id ORDER BY s.id DESC) sub_status
    FROM tenants t ORDER BY t.id`);
  tenants.forEach(t => { t.profile = J(t.profile, {}); });
  json(res, 200, { tenants });
}
function tenantPayload(body) {
  /* shared validation+normalization for create & update — jurisdiction, taxation, categories, owner, gateways, plan */
  const j = body.jurisdiction || {};
  const country = registry.country(String(j.country || body.country || "").toUpperCase());
  const industries = (Array.isArray(body.industries) ? body.industries : []).filter(k => registry.list("industries").some(i => i.key === k));
  const mode = rl("deployModes").some(m => m.key === body.mode) ? body.mode : "marketplace";
  let owner = body.owner || null;
  if (!owner && (body.ownerEmail || body.adminEmail)) owner = { name: body.ownerName || body.adminName || "Store Admin", email: body.ownerEmail || body.adminEmail, password: body.ownerPassword || body.adminPassword, phone: body.ownerPhone || "" };
  const tax = body.tax || null;
  const gateways = Array.isArray(body.gateways) && body.gateways.length ? body.gateways : null;
  const planId = body.plan_id != null ? Number(body.plan_id) : null;
  return { j, country, industries, mode, owner, tax, gateways, planId };
}
function applyCountryAndTax(tid, country, tax) {
  const c = settings.load(tid);
  const wantMode = tax && tax.mode ? String(tax.mode) : null;
  const taxMode = wantMode && get("SELECT key FROM tax_modes WHERE key=?", wantMode) ? wantMode : (tax && tax.mode ? null : null);
  const over = !!(tax && (tax.mode || (tax.rate != null && tax.rate !== "")));
  const taxRate = over && tax.rate != null && tax.rate !== "" ? Number(tax.rate) : null;
  settings.save(tid, { commerce: { ...c.commerce, country: country.code, currency: null, symbol: null, locale: null, decimals: null, taxMode: taxMode, taxRate: taxRate } });
  run("UPDATE tenants SET country=? WHERE id=?", country.code, tid);
}
function provisionGateways(tid, country, gateways) {
  let pays = gateways ? gateways.filter(p => registry.supports(p, country.code)) : registry.providersFor("payment", country.code).slice(0, 2).map(p => p.id).concat("cod");
  pays = [...new Set(pays)];
  if (!pays.length) pays = ["cod"];
  run("DELETE FROM tenant_gateways WHERE tenant_id=? AND provider_id NOT LIKE 'ship:%' AND provider_id NOT LIKE 'notify:%'", tid);
  const gmode = sec.policy().provisioning.sandboxGatewaysByDefault ? "sandbox" : "live";
  pays.forEach((p, i) => run("INSERT INTO tenant_gateways(tenant_id,provider_id,is_primary,mode,config,position) VALUES(?,?,?,?,'{}',?)", tid, p, i === 0 ? 1 : 0, gmode, i));
  const ships = [...new Set(["house-std"].concat(registry.providersFor("shipping", country.code).filter(x => !x.id.startsWith("house-")).slice(0, 2).map(x => x.id)))];
  run("DELETE FROM tenant_gateways WHERE tenant_id=? AND provider_id LIKE 'ship:%'", tid);
  ships.forEach((x, i) => run("INSERT INTO tenant_gateways(tenant_id,provider_id,is_primary,mode,config,position) VALUES(?,?,?,'live','{}',?)", tid, "ship:" + x, i === 0 ? 1 : 0, i));
  return pays;
}
function apiPlatformTenantCreate(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  const slug = String(body.slug || "").trim().toLowerCase().replace(/[^a-z0-9-]/g, "-").slice(0, 30);
  if (!slug || !body.name) return bad(res, "Store name and slug are required");
  if (get("SELECT id FROM tenants WHERE slug=?", slug)) return bad(res, "Slug already taken", 409);
  const p = tenantPayload(body);
  if (!p.country) return bad(res, "Pick a valid jurisdiction country — available: " + registry.countries().map(c => c.code).join(", "));
  if ((p.mode === "industry" || p.mode === "brand") && !p.industries.length) return bad(res, "Select at least one industry (product categories) for an industry/brand store");
  if (p.owner && p.owner.email) {
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(p.owner.email) || String(p.owner.password || "").length < 6 || String(p.owner.name || "").trim().length < 2)
      return bad(res, "Owner needs a full name, valid email and a password of 6+ characters");
  }
  const prov = sec.policy().provisioning;
  if (body.seedCatalog == null) body.seedCatalog = prov.seedCatalogByDefault;
  const planId = p.planId || prov.defaultPlanId;
  if (!get("SELECT id FROM plans WHERE id=?", planId)) return bad(res, "Unknown plan");
  const profile = {
    legalName: String(p.j.legalName || body.name).slice(0, 80), taxId: String(p.j.taxId || "").slice(0, 40),
    registrationAddress: String(p.j.registrationAddress || "").slice(0, 160), state: String(p.j.state || ""),
    ownerName: p.owner ? String(p.owner.name || "").trim() : "", ownerEmail: p.owner ? String(p.owner.email || "").toLowerCase() : "", ownerPhone: p.owner ? String(p.owner.phone || "") : ""
  };
  const r = run("INSERT INTO tenants(slug,name,domain,status,mode,industries,profile,country) VALUES(?,?,?,'active',?,?,?,?)",
    slug, String(body.name).slice(0, 60), String(body.domain || slug + ".localhost"), p.mode, JSON.stringify(p.industries), JSON.stringify(profile), p.country.code);
  const tid = Number(r.lastInsertRowid);
  settings.save(tid, { brand: { name: String(body.name).toUpperCase(), wordmark: String(body.name).toUpperCase(), tagline: String(body.tagline || "A new storefront on LUXORA Platform") }, features: { coupons: !!sec.policy().provisioning.couponsAllowed, fiscalSelection: !!sec.policy().provisioning.fiscalContextsAllowed } });
  applyCountryAndTax(tid, p.country, p.tax);
  seedTenantDepartments(tid, p.industries.length ? p.industries : null);
  seedTenantHome(tid, p.industries.length ? p.industries : null);
  seedMeta(tid, p.industries.length ? p.industries : null);
  if (body.seedCatalog) seedTenantCatalog(tid, p.industries.length ? p.industries : null);
  const pays = provisionGateways(tid, p.country, p.gateways);
  run("INSERT INTO tenant_gateways(tenant_id,provider_id,is_primary,mode,config,position) VALUES(?, 'notify:log', 1, 'live', '{}', 0)", tid);
  if (p.owner && p.owner.email) newUser(tid, profile.ownerName, profile.ownerEmail, String(p.owner.password), "admin");
  run("INSERT INTO subscriptions(tenant_id,plan_id,status) VALUES(?,?,'trialing')", tid, planId);
  run("INSERT INTO warehouses(tenant_id,name,code,country,region) VALUES(?,?,?,?,?)", tid, "Main DC-" + p.country.code, "DC-" + p.country.code, p.country.code, profile.state);
  mods.ensureBaselines();
  audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.create", "tenant", tid, { slug, country: p.country.code, industries: p.industries, gateways: pays });
  const t = get("SELECT * FROM tenants WHERE id=?", tid);
  json(res, 200, { tenant: { ...t, profile: J(t.profile, {}) }, storeUrl: "/index.html?store=" + slug, adminUrl: "/admin.html?store=" + slug });
}
function apiPlatformTenantUpdate(req, res, url, s, body, id) {
  if (!requirePlatform(s, res)) return;
  const t = get("SELECT * FROM tenants WHERE id=?", Number(id));
  if (!t) return bad(res, "Unknown tenant", 404);
  const tid = t.id;
  if (body.name != null) run("UPDATE tenants SET name=? WHERE id=?", String(body.name).slice(0, 60), tid);
  if (body.domain != null) run("UPDATE tenants SET domain=? WHERE id=?", String(body.domain), tid);
  if (body.status != null) {
    const st = ["active", "suspended"].includes(body.status) ? body.status : t.status;
    run("UPDATE tenants SET status=? WHERE id=?", st, tid);
    audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.status", "tenant", tid, { status: st });
  }
  const p = tenantPayload({ ...body, jurisdiction: body.jurisdiction || undefined });
  if (body.jurisdiction || body.tax != null || body.country) {
    if (!p.country) return bad(res, "Unknown jurisdiction country");
    applyCountryAndTax(tid, p.country, body.tax != null ? body.tax : null);
    if (body.jurisdiction) {
      const prof = J(t.profile, {});
      Object.assign(prof, { legalName: String(body.jurisdiction.legalName || prof.legalName || ""), taxId: String(body.jurisdiction.taxId != null ? body.jurisdiction.taxId : prof.taxId || ""), registrationAddress: String(body.jurisdiction.registrationAddress != null ? body.jurisdiction.registrationAddress : prof.registrationAddress || ""), state: String(body.jurisdiction.state != null ? body.jurisdiction.state : prof.state || "") });
      run("UPDATE tenants SET profile=? WHERE id=?", JSON.stringify(prof), tid);
    }
    audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.jurisdiction", "tenant", tid, { country: p.country.code, tax: body.tax || null });
  }
  if (Array.isArray(body.industries)) {
    const inds = body.industries.filter(k => registry.list("industries").some(i => i.key === k));
    run("UPDATE tenants SET industries=? WHERE id=?", JSON.stringify(inds), tid);
    inds.forEach((k, i) => { const ind = registry.list("industries").find(x => x.key === k); run("INSERT OR IGNORE INTO departments(tenant_id,key,label,icon,position) VALUES(?,?,?,?,?)", tid, k, ind.name, ind.icon, i); });
    seedTaxonomy(tid, inds);
    audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.industries", "tenant", tid, { industries: inds });
  }
  if (body.gateways && p.country) { const pays = provisionGateways(tid, registry.country(t.country) || p.country, body.gateways); audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.gateways", "tenant", tid, { gateways: pays }); }
  if (p.planId) {
    if (!get("SELECT id FROM plans WHERE id=?", p.planId)) return bad(res, "Unknown plan");
    const ex = get("SELECT id FROM subscriptions WHERE tenant_id=? ORDER BY id DESC LIMIT 1", tid);
    if (ex) run("UPDATE subscriptions SET plan_id=?, status='active' WHERE id=?", p.planId, ex.id);
    else run("INSERT INTO subscriptions(tenant_id,plan_id,status) VALUES(?,?,'active')", tid, p.planId);
    audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.plan", "tenant", tid, { plan_id: p.planId });
  }
  if (body.owner && body.owner.email) {
    const prof = J(get("SELECT profile FROM tenants WHERE id=?", tid).profile, {});
    const existing = get("SELECT id FROM users WHERE tenant_id=? AND role='admin' ORDER BY id LIMIT 1", tid);
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(body.owner.email) || String(body.owner.password || "").length < 6) return bad(res, "New owner password must be 6+ characters");
    if (existing) {
      setUserPassword(existing.id, String(body.owner.password), body.owner.email.toLowerCase());
      run("UPDATE users SET email=?, name=? WHERE id=?", body.owner.email.toLowerCase(), String(body.owner.name || prof.ownerName || "Store Admin"), existing.id);
    } else newUser(tid, String(body.owner.name || "Store Admin"), body.owner.email, String(body.owner.password), "admin");
    prof.ownerEmail = body.owner.email.toLowerCase(); prof.ownerName = String(body.owner.name || prof.ownerName || ""); prof.ownerPhone = String(body.owner.phone || prof.ownerPhone || "");
    run("UPDATE tenants SET profile=? WHERE id=?", JSON.stringify(prof), tid);
    audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.owner", "tenant", tid, { email: prof.ownerEmail });
  }
  const out = get("SELECT * FROM tenants WHERE id=?", tid);
  json(res, 200, { tenant: { ...out, profile: J(out.profile, {}) } });
}
function apiPlatformTenantDelete(req, res, url, s, body, id) {
  if (!requirePlatform(s, res)) return;
  const tid = Number(id);
  if (get("SELECT slug FROM tenants WHERE id=?", tid).slug === "luxora") return bad(res, "The default store cannot be deleted");
  for (const q of ["DELETE FROM products WHERE tenant_id=?", "DELETE FROM product_bullets WHERE tenant_id=?", "DELETE FROM departments WHERE tenant_id=?", "DELETE FROM home_banners WHERE tenant_id=?", "DELETE FROM home_cards WHERE tenant_id=?", "DELETE FROM settings WHERE tenant_id=?", "DELETE FROM tenant_gateways WHERE tenant_id=?", "DELETE FROM reviews WHERE tenant_id=?", "DELETE FROM payments WHERE tenant_id=?", "DELETE FROM invoices WHERE tenant_id=?", "DELETE FROM subscriptions WHERE tenant_id=?", "DELETE FROM users WHERE tenant_id=?", "DELETE FROM tenants WHERE id=?"]) run(q, tid);
  audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.delete", "tenant", tid);
  json(res, 200, { ok: true });
}
function apiPlatformImpersonate(req, res, url, s, body, id) {
  if (!requirePlatform(s, res)) return;
  const tid = Number(id);
  let admin = get("SELECT id FROM users WHERE tenant_id=? AND role='admin' ORDER BY id LIMIT 1", tid);
  if (!admin) { const uid = newUser(tid, "Platform Impersonator", "impersonate+" + tid + "@luxora.shop", crypto.randomBytes(8).toString("hex"), "admin"); admin = { id: uid }; }
  const token = crypto.randomBytes(16).toString("hex");
  run("INSERT INTO tokens(token,tenant_id,user_id,expires_at) VALUES(?,?,?,datetime('now','+10 minutes'))", token, tid, admin.id);
  const t = get("SELECT slug FROM tenants WHERE id=?", tid);
  audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.impersonate", "tenant", tid);
  json(res, 200, { url: `/admin.html?store=${t.slug}&token=${token}` });
}
function apiPlatformPlans(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  json(res, 200, { plans: all("SELECT * FROM plans ORDER BY position") });
}
function apiPlatformPlanSave(req, res, url, s, body, id) {
  if (!requirePlatform(s, res)) return;
  if (!body.name) return bad(res, "Name required");
  const vals = [String(body.name), Number(body.price_month) || 0, String(body.currency || "USD"), Math.max(1, Number(body.max_products) || 100), Math.max(1, Number(body.max_orders_month) || 100), Number(body.position) || 0];
  if (id) run("UPDATE plans SET name=?,price_month=?,currency=?,max_products=?,max_orders_month=?,position=? WHERE id=?", ...vals, Number(id));
  else run("INSERT INTO plans(name,price_month,currency,max_products,max_orders_month,position) VALUES(?,?,?,?,?,?)", ...vals);
  audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "plan.save", "plan", id || "new");
  json(res, 200, { plans: all("SELECT * FROM plans ORDER BY position") });
}
function apiPlatformSubscribe(req, res, url, s, body, id) {
  if (!requirePlatform(s, res)) return;
  const plan = get("SELECT * FROM plans WHERE id=?", Number(body.plan_id));
  if (!plan) return bad(res, "Unknown plan", 404);
  const ex = get("SELECT id FROM subscriptions WHERE tenant_id=? ORDER BY id DESC LIMIT 1", Number(id));
  if (ex) run("UPDATE subscriptions SET plan_id=?, status='active', renews_at=datetime('now','+1 month') WHERE id=?", plan.id, ex.id);
  else run("INSERT INTO subscriptions(tenant_id,plan_id,status) VALUES(?,?,'active')", Number(id), plan.id);
  audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "subscription.assign", "tenant", id, { plan: plan.name });
  json(res, 200, { ok: true });
}
function apiPlatformInvoices(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  json(res, 200, { invoices: all("SELECT i.*, t.slug tenant_slug, t.name tenant_name FROM invoices i JOIN tenants t ON t.id=i.tenant_id ORDER BY i.issued_at DESC") });
}
function apiPlatformInvoiceGenerate(req, res, url, s, body, id) {
  return (async () => {
  if (!requirePlatform(s, res)) return;
  const t = get("SELECT * FROM tenants WHERE id=?", Number(id));
  const sub = get("SELECT p.* FROM subscriptions s JOIN plans p ON p.id=s.plan_id WHERE s.tenant_id=? ORDER BY s.id DESC", t.id);
  if (!sub) return bad(res, "Tenant has no subscription", 400);
  let r; try { r = billing.issueInvoice(t.id, { tax: true, note: `${sub.name} plan — monthly` }); } catch (e) { console.error("billing:", e.message); return bad(res, "Billing engine error: " + e.message, 500); }
  audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "invoice.generate", "invoice", r.number, { tenant: t.slug, amount: r.amount });
  json(res, 200, { ok: true, invoice: r });
  })();
}
function apiPlatformInvoiceRefund(req, res, url, s, body, id) {
  if (!requirePlatform(s, res)) return;
  const inv = get("SELECT * FROM invoices WHERE id=?", Number(id)); if (!inv) return bad(res, "Unknown invoice", 404);
  const r = billing.creditNote(inv.tenant_id, inv.id, body.amount != null ? Number(body.amount) : inv.amount, String(body.reason || "refund"), { to_wallet: !!body.to_wallet, owner: body.owner || undefined });
  if (r.error) return bad(res, r.error);
  logAction(s, "invoice.credit_note", "invoice", inv.number, { amount: r.amount, to_wallet: !!body.to_wallet }, req);
  json(res, 200, { ok: true, credit_note: r });
}
function apiPlatformDunning(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return; const t = Number(body && body.tenant_id || 0);
  const r = billing.dunning(t); logAction(s, "billing.dunning", "billing", t || null, { actions: r.actions.length });
  json(res, 200, r);
}
function apiPlatformAging(req, res, url, s) { if (!requirePlatform(s, res)) return; json(res, 200, { aging: billing.aging(0), all: billing.list(0) }); }
function apiPlatformUsage(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  if (!body.tenant_id || !body.description) return bad(res, "tenant_id and description required");
  const id = billing.recordUsage(Number(body.tenant_id), String(body.kind || "manual"), String(body.description), Number(body.qty) || 1, Number(body.unit_amount) || 0, { currency: body.currency, ref: body.ref, period: body.period });
  logAction(s, "billing.usage", "usage_record", id, { tenant: body.tenant_id, amount: body.unit_amount });
  json(res, 200, { ok: true, id });
}
function apiAdminBillingDetail(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const data = billing.list(T(s)); data.aging = billing.aging(T(s)).buckets; data.usage = all("SELECT * FROM usage_records WHERE tenant_id=? ORDER BY id DESC LIMIT 100", T(s));
  json(res, 200, data);
}
function apiAdminTaxConfig(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const cfg = taxmod.configFor(T(s));
  const q = (url.searchParams.get("country") && url.searchParams.get("number")) ? taxmod.validateNumber(url.searchParams.get("country"), url.searchParams.get("number")) : null;
  json(res, 200, { country: cfg.country, rule: cfg.rule, classes: cfg.classes, storeRate: (CFG(s).commerce || {}).taxRate, taxNumber: q });
}
function apiAdminTaxQuote(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, taxmod.quote({ tenantId: T(s), country: body.country, lines: (body.lines || []).map(l => ({ id: l.id, class: l.class, amount: Number(l.amount) || 0, tax_rule: l.tax_rule || {} })), buyerVat: body.vatId, inclusive: !!body.inclusive })); } catch (e) { return bad(res, e.message); }
}
/* ---------- marketing / external integrations (specs are DATA: fill in the blanks) ---------- */
function marketingSpec(tenantId, id) {
  const rows = all("SELECT manifest FROM custom_providers WHERE kind='marketing' AND (scope='platform' OR (scope='tenant' AND tenant_id=?))", tenantId);
  for (const r of rows) { let m; try { m = J(r.manifest, null); } catch (e) { continue; } if (m && m.id === id && m.spec) return { spec: m.spec, fields: m.fields || [] }; }
  const def = get("SELECT spec, fields FROM provider_defs WHERE id=? AND kind='marketing'", id);
  if (def) return { spec: J(def.spec, null) || null, fields: J(def.fields, []) };
  return null;
}
function apiMarketingProviders(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const defs = registry.providerDefs("marketing").concat(customProviders(T(s), "marketing"));
  const list = defs.map(p => { const row = get("SELECT mode,config FROM tenant_gateways WHERE tenant_id=? AND provider_id=?", T(s), "marketing:" + p.id); let cfg = {}; try { cfg = J(row && row.config || "{}", {}); } catch (e) { } cfg = row ? sec.unsealConfig(T(s), "marketing:" + p.id, JSON.stringify(cfg)) : {}; const masked = {}; for (const [k, v] of Object.entries(cfg)) masked[k] = (p.fields || []).some(f => f.key === k && f.secret) ? (v ? "••••" + String(v).slice(-4) : "") : v; const sp = marketingSpec(T(s), p.id); return { id: p.id, name: p.name, emoji: p.emoji, desc: p.desc, fields: p.fields, mode: row ? row.mode : "sandbox", configured: row && Object.keys(cfg).length > 0, hasSpec: !!(sp && sp.spec), spec: sp && sp.spec, config: masked }; });
  json(res, 200, { providers: list });
}
function apiMarketingSend(req, res, url, s, body) {
  return (async () => {
    if (!requireAdmin(s, res)) return;
    const id = String(body.provider || ""); const sp = marketingSpec(T(s), id); if (!sp || !sp.spec) return bad(res, "Unknown or specless marketing provider: " + id, 404);
    const row = get("SELECT mode,config FROM tenant_gateways WHERE tenant_id=? AND provider_id=?", T(s), "marketing:" + id);
    let cfg = {}; try { cfg = J(row && row.config || "{}", {}); } catch (e) { } if (row) cfg = sec.unsealConfig(T(s), "marketing:" + id, JSON.stringify(cfg));
    if (!body.config && (!row || row.mode !== "live")) return json(res, 200, { ok: true, live: false, simulated: true, note: "provider not configured live — enable in Marketing & set live + credentials" });
    const r = await connect.marketing({ provider: id, spec: sp.spec, config: body.config || cfg, payload: body.payload || {}, currency: body.currency });
    logAction(s, "marketing.send", "marketing", id, { ok: !!r.ok, live: !!r.live, error: r.error }, req);
    json(res, 200, r);
  })();
}
function apiMarketingSave(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const list = Array.isArray(body.marketing) ? body.marketing : [];
  list.forEach((g, i) => { const cfg = {}; for (const [k, v] of Object.entries(g.config || {})) if (v && !String(v).startsWith("••••")) cfg[k] = sec.encryptSecret(String(v), T(s) + "|marketing:" + g.id + "|" + k); run(`INSERT INTO tenant_gateways(tenant_id,provider_id,enabled,is_primary,mode,config,position) VALUES(?,?,1,0,?,?,?)
     ON CONFLICT(tenant_id,provider_id) DO UPDATE SET enabled=1, mode=excluded.mode, config=excluded.config`, T(s), "marketing:" + g.id, g.mode === "live" ? "live" : "sandbox", JSON.stringify(cfg), i); });
  logAction(s, "marketing.save", "marketing", null, { count: list.length }, req); json(res, 200, { ok: true });
}
function apiPlatformInvoicePay(req, res, url, s, body, id) {
  return (async () => {
  if (!requirePlatform(s, res)) return;
  const inv = get("SELECT * FROM invoices WHERE id=?", Number(id));
  if (!inv) return bad(res, "Unknown invoice", 404);
  if (inv.status === "paid") return bad(res, "Already paid");
  const gwId = String(body.gateway || "stripe");
  const gw = registry.providerDefs("payment").find(p => p.id === gwId);
  if (!gw) return bad(res, "Unknown gateway", 422);
  const gs = gatewaySecrets(inv.tenant_id, gwId);
  const sim = await settlePayment(inv.tenant_id, Object.assign({}, gw, { mode: gs ? gs.mode : "sandbox" }), inv.amount, inv.currency, inv.number);
  if (sim.status === "failed") return bad(res, "Payment declined: " + (sim.error || "gateway error"), 402);
  run("UPDATE invoices SET status='paid', paid_at=datetime('now') WHERE id=?", inv.id);
  run("INSERT INTO payments(tenant_id,kind,invoice_id,gateway,method,amount,currency,fee,status,txn_ref) VALUES(?,?,?,?,?,?,?,?,?,?)",
    inv.tenant_id, "subscription", inv.id, gw.id, "card", inv.amount, inv.currency, sim.fee, sim.status, sim.ref);
  audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "invoice.pay", "invoice", inv.number, { gateway: gw.id, txn: sim.ref, live: !!sim.live });
  json(res, 200, { ok: true, txn_ref: sim.ref });
  })();
}
function apiPlatformMonitor(req, res, url, s, body, metrics) {
  if (!requirePlatform(s, res)) return;
  const snap = metrics.snapshot(null);
  const mem = process.memoryUsage();
  let dbSize = 0; try { dbSize = fs.statSync(DB_PATH).size; } catch (e) { }
  snap.system = { uptimeSec: Math.floor(process.uptime()), rssMB: +(mem.rss / 1048576).toFixed(1), dbKB: +(dbSize / 1024).toFixed(0), node: process.version };
  snap.tenants = all("SELECT id, slug, name, status FROM tenants ORDER BY id");
  json(res, 200, snap);
}
function apiPlatformAudit(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const t = url.searchParams.get("tenant");
  const rows = t ? all("SELECT * FROM audit_log WHERE tenant_id=? ORDER BY created_at DESC LIMIT 300", Number(t)) : all("SELECT * FROM audit_log ORDER BY created_at DESC LIMIT 300");
  json(res, 200, { entries: rows });
}
function apiPlatformRevenue(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  json(res, 200, {
    mrr: get("SELECT COALESCE(SUM(p.price_month),0) t FROM subscriptions s JOIN plans p ON p.id=s.plan_id WHERE s.status IN ('active','trialing')").t, /* plans priced in platform billing currency (USD) */
    collected: get("SELECT COALESCE(SUM(i.amount * COALESCE(c.usd,1)),0) t FROM invoices i LEFT JOIN currencies c ON c.code=i.currency WHERE i.status='paid'").t,
    outstanding: get("SELECT COALESCE(SUM(amount),0) t FROM invoices WHERE status!='paid'").t,
    gatewayFees: get("SELECT COALESCE(SUM(p.fee * COALESCE(c.usd,1)),0) t FROM payments p LEFT JOIN currencies c ON c.code=p.currency WHERE p.kind='order'").t,
    gmv: get("SELECT COALESCE(SUM(o.total * COALESCE(c.usd,1)),0) t FROM orders o LEFT JOIN currencies c ON c.code=o.currency").t,
    byMonth: all("SELECT strftime('%Y-%m', issued_at) m, SUM(CASE WHEN status='paid' THEN amount ELSE 0 END) paid FROM invoices GROUP BY m ORDER BY m")
  });
}
function apiPlatformCustomProviders(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  json(res, 200, {
    builtIn: { payment: registry.providerDefs("payment"), shipping: registry.providerDefs("shipping"), notification: registry.providerDefs("notification"), tax: registry.taxModes(), ai: registry.providerDefs("ai") },
    countries: registry.countries(), availability: all("SELECT * FROM provider_availability ORDER BY provider_id"),
    custom: all("SELECT * FROM custom_providers WHERE scope='platform'")
  });
}
function apiPlatformCustomProviderAdd(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  const m = body.manifest;
  if (!m || !m.id || !m.name) return bad(res, "Manifest needs id and name");
  const kind = rl("providerKinds").includes(body.kind) ? body.kind : "payment";
  run("INSERT INTO custom_providers(scope,kind,manifest) VALUES('platform',?,?)", kind, JSON.stringify(m));
  try {
    run(`INSERT INTO provider_defs(id,kind,name,emoji,description,methods,fee_pct,fee_fixed,fields,base_fee,position) VALUES(?,?,?,?,?,?,?,?,?,?,?)
         ON CONFLICT(id,kind) DO UPDATE SET name=excluded.name,emoji=excluded.emoji,description=excluded.description,methods=excluded.methods,fee_pct=excluded.fee_pct,fee_fixed=excluded.fee_fixed,fields=excluded.fields`,
      String(m.id), kind, String(m.name), String(m.emoji || "🔌"), String(m.desc || ""), JSON.stringify(m.methods || []), Number(m.feePct) || 0, Number(m.feeFixed) || 0, JSON.stringify(m.fields || []), Number(m.baseFee) || 0, 900);
    const codes = (m.countries || []).includes("*") ? all("SELECT code FROM countries").map(c => c.code) : (m.countries || []);
    for (const cc of codes) run("INSERT OR IGNORE INTO provider_availability(provider_id,country_code) VALUES(?,?)", String(m.id), cc);
  } catch (e) { console.error("provider_defs sync:", e.message); }
  audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "provider.add", "custom_provider", m.id, { kind });
  json(res, 200, { ok: true });
}
function apiPlatformCustomProviderDelete(req, res, url, s, body, id) {
  if (!requirePlatform(s, res)) return;
  run("DELETE FROM custom_providers WHERE id=? AND scope='platform'", Number(id));
  json(res, 200, { ok: true });
}

/* ================= META MODEL ================= */
const meta = require("./meta.js");
const rl = registry.list;
function J(v, d) { try { return JSON.parse(v == null || v === "" ? (d || "{}") : v); } catch (e) { return d || {}; } }
function apiMeta(req, res, url, s) {
  const c = CFG(s);
  const tInds = J(s.tenant.industries, []);
  const allowed = tInds.length ? tInds : null;
  const reg = meta.registry(customProviders(T(s), "registry").reduce((o, m) => ({ ...o, ...m }), {}));
  json(res, 200, {
    industries: allowed ? reg.industries.filter(i => allowed.includes(i.key)) : reg.industries,
    productTypes: reg.productTypes, lifecycle: rl("lifecycle"), lifecycleTransitions: rl("lifecycleTransitions"),
    relTypes: rl("relTypes"), mediaKinds: rl("mediaKinds"), packagingLevels: rl("packagingLevels"),
    uomUnits: rl("uomUnits"), uomConversions: rl("uomConversions"), sellerRoles: rl("sellerRoles"),
    promoTypes: rl("promoTypes"), identityFields: rl("identityFields"), shippingClasses: rl("shippingClasses"),
    serializedStatuses: rl("serializedStatuses"), serializedConditions: rl("serializedConditions"), variantAxes: rl("variantAxes"),
    complianceScopes: rl("complianceScopes"), complianceKinds: rl("complianceKinds"), complianceStatuses: rl("complianceStatuses"),
    supplierRoles: rl("supplierRoles"), supplierStatuses: rl("supplierStatuses"), paymentTerms: rl("paymentTerms"), incoterms: rl("incoterms"),
    localizationEntities: rl("localizationEntities"), contractStatuses: rl("contractStatuses"), tenderStatuses: rl("tenderStatuses"), linkStatuses: rl("linkStatuses"),
    providerKinds: rl("providerKinds"), aiCapabilityKeys: rl("aiCapabilityKeys"), aiCapabilities: rl("aiCapabilities"), aiPlans: rl("aiPlans"),
    offerTypes: rl("offerTypes"), offerScopes: rl("offerScopes"), offerChannels: rl("offerChannels"), offerDirections: rl("offerDirections"), offerFunders: rl("offerFunders"), couponKinds: rl("couponKinds"), stackingPolicies: rl("stackingPolicies"), offerStatuses: rl("offerStatuses"), couponStatuses: rl("couponStatuses"), walletEntryKinds: rl("walletEntryKinds"),
    verticals: reg.verticals, verticalFields: rl("verticalFields"), verticalTypes: rl("verticalTypes"), verticalContexts: rl("verticalContexts"), verticalTypeOf: rl("verticalTypeOf"),
    countries: registry.countries(), taxModes: registry.taxModes(),
    providers: { payment: registry.providerDefs("payment"), shipping: registry.providerDefs("shipping"), notification: registry.providerDefs("notification") },
    providersAi: registry.providerDefs("ai"),
    deployModes: rl("deployModes"),
    tenant: { id: s.tenant.id, slug: s.tenant.slug, name: s.tenant.name, mode: s.tenant.mode, industries: J(s.tenant.industries, []) }
  });
}
function apiTaxonomy(req, res, url, s) {
  const rows = all("SELECT * FROM taxonomy WHERE tenant_id=? AND active=1 ORDER BY position", T(s));
  const byParent = {};
  rows.forEach(r => { (byParent[r.parent_id || 0] = byParent[r.parent_id || 0] || []).push(r); });
  function build(pid) { return (byParent[pid] || []).map(r => ({ ...r, attrs: J(r.attrs), children: build(r.id) })); }
  json(res, 200, { tree: build(0), flat: rows });
}
function nodeDescendants(tenantId, id) {
  const out = [Number(id)];
  const rows = all("SELECT id,parent_id FROM taxonomy WHERE tenant_id=?", tenantId);
  let grew = true;
  while (grew) { grew = false; for (const r of rows) if (out.includes(r.parent_id) && !out.includes(r.id)) { out.push(r.id); grew = true; } }
  return out;
}
function apiAdminTaxonomy(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { nodes: all("SELECT * FROM taxonomy WHERE tenant_id=? ORDER BY level, position", T(s)) });
}
function apiAdminTaxSave(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  const level = ["domain", "industry", "category", "subcategory", "family", "model"].includes(body.level) ? body.level : "category";
  if (!body.name) return bad(res, "Name required");
  const key = String(body.key || (level + "-" + Date.now().toString(36)));
  if (id) run("UPDATE taxonomy SET parent_id=?,level=?,key=?,name=?,icon=?,active=?,position=? WHERE id=? AND tenant_id=?",
    body.parent_id || null, level, key, String(body.name), String(body.icon || ""), body.active === 0 ? 0 : 1, Number(body.position) || 0, Number(id), t);
  else run("INSERT INTO taxonomy(tenant_id,parent_id,level,key,name,icon,position) VALUES(?,?,?,?,?,?,?)",
    t, body.parent_id || null, level, key, String(body.name), String(body.icon || ""), Number(body.position) || 0);
  logAction(s, "taxonomy.save", "taxonomy", id || key, { level });
  json(res, 200, { ok: true });
}
function apiAdminTaxDelete(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  if (get("SELECT COUNT(*) c FROM taxonomy WHERE tenant_id=? AND parent_id=?", T(s), Number(id)).c > 0) return bad(res, "Remove children first");
  run("UPDATE products SET node_id=NULL WHERE tenant_id=? AND node_id=?", T(s), Number(id));
  run("DELETE FROM taxonomy WHERE id=? AND tenant_id=?", Number(id), T(s));
  logAction(s, "taxonomy.delete", "taxonomy", id);
  json(res, 200, { ok: true });
}
function apiAdminAttributes(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { attributes: all("SELECT * FROM attribute_defs WHERE tenant_id=? ORDER BY position", T(s)).map(a => ({ ...a, options: J(a.options, []), validation: J(a.validation) })) });
}
function apiAdminAttrSave(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const key = String(body.key || "").trim().toLowerCase().replace(/[^a-z0-9_]/g, "");
  if (!key || !body.label) return bad(res, "Key and label required");
  const ex = get("SELECT key FROM attribute_defs WHERE tenant_id=? AND key=?", T(s), key);
  const vals = [String(body.label), String(body.grp || "General"), String(body.type || "text"), String(body.unit || ""), JSON.stringify(body.options || []), JSON.stringify(body.validation || {}), String(body.industry || ""), Number(body.position) || 0];
  if (ex) run("UPDATE attribute_defs SET label=?,grp=?,type=?,unit=?,options=?,validation=?,industry=?,position=? WHERE tenant_id=? AND key=?", ...vals, T(s), key);
  else run("INSERT INTO attribute_defs(tenant_id,key,label,grp,type,unit,options,validation,industry,position) VALUES(?,?,?,?,?,?,?,?,?,?)", T(s), key, ...vals);
  logAction(s, "attribute.save", "attribute", key);
  json(res, 200, { ok: true });
}
function apiAdminAttrDelete(req, res, url, s, body, key) {
  if (!requireAdmin(s, res)) return;
  run("DELETE FROM attribute_defs WHERE tenant_id=? AND key=?", T(s), key);
  logAction(s, "attribute.delete", "attribute", key);
  json(res, 200, { ok: true });
}
function validateAttrs(tenantId, attrs) {
  const defs = all("SELECT * FROM attribute_defs WHERE tenant_id=?", tenantId);
  const errs = [];
  for (const d of defs) {
    const v = attrs[d.key];
    if (v == null || v === "") continue;
    if (d.type === "number" && isNaN(Number(v))) errs.push(d.label + " must be a number");
    if (d.type === "select" && !J(d.options, []).includes(v)) errs.push(d.label + " invalid option");
  }
  return errs;
}
function fullProductDoc(tenantId, p) {
  const skus = all("SELECT * FROM skus WHERE tenant_id=? AND product_id=?", tenantId, p.id).map(k => ({ ...k, identity: J(k.identity), variant: J(k.variant) }));
  for (const k of skus) k.inventory = all("SELECT i.*, w.name warehouse FROM inventory i LEFT JOIN warehouses w ON w.id=i.warehouse_id WHERE i.tenant_id=? AND i.sku_id=?", tenantId, k.id).map(i => ({ ...i, serial: J(i.serial, []) }));
  const rels = all("SELECT * FROM relationships WHERE tenant_id=? AND from_id=?", tenantId, p.id).map(r => ({ ...r, to: get("SELECT id,title,price,emoji,hue,stock,type FROM products WHERE tenant_id=? AND id=?", tenantId, r.to_id) }));
  return {
    ...publicProduct(p), type: p.type, node_id: p.node_id, lifecycle: p.lifecycle,
    identity: J(p.identity), attrs: J(p.attrs), vertical: J(p.vertical), media: J(p.media, []), seo: J(p.seo),
    tax_rule: J(p.tax_rule), geo_rules: J(p.geo_rules, []), pricing_rules: J(p.pricing_rules), logistics: J(p.logistics),
    packaging: J(p.packaging, []), docs: J(p.docs, []), uom: J(p.uom), supplier_id: p.supplier_id,
    skus, relationships: rels
  };
}
function apiAdminProductGet(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const p = get("SELECT * FROM products WHERE tenant_id=? AND id=?", T(s), id);
  if (!p) return bad(res, "Unknown product", 404);
  p.about = all("SELECT text FROM product_bullets WHERE tenant_id=? AND product_id=? ORDER BY pos", T(s), id).map(r => r.text);
  json(res, 200, { product: fullProductDoc(T(s), p) });
}
function apiAdminProductSaveMeta(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  const p = get("SELECT * FROM products WHERE tenant_id=? AND id=?", t, id);
  if (!p) return bad(res, "Unknown product", 404);
  const errs = body.attrs ? validateAttrs(t, body.attrs) : [];
  if (errs.length) return bad(res, errs.join("; "));
  const set = {
    type: body.type != null && rl("productTypes").some(x => x.key === body.type) ? body.type : p.type,
    node_id: body.node_id != null ? Number(body.node_id) || null : p.node_id,
    identity: body.identity != null ? JSON.stringify(body.identity) : p.identity,
    attrs: body.attrs != null ? JSON.stringify(body.attrs) : p.attrs,
    vertical: body.vertical != null ? JSON.stringify(body.vertical) : p.vertical,
    media: body.media != null ? JSON.stringify(body.media) : p.media,
    seo: body.seo != null ? JSON.stringify(body.seo) : p.seo,
    tax_rule: body.tax_rule != null ? JSON.stringify(body.tax_rule) : p.tax_rule,
    geo_rules: body.geo_rules != null ? JSON.stringify(body.geo_rules) : p.geo_rules,
    pricing_rules: body.pricing_rules != null ? JSON.stringify(body.pricing_rules) : p.pricing_rules,
    logistics: body.logistics != null ? JSON.stringify(body.logistics) : p.logistics,
    packaging: body.packaging != null ? JSON.stringify(body.packaging) : p.packaging,
    docs: body.docs != null ? JSON.stringify(body.docs) : p.docs,
    uom: body.uom != null ? JSON.stringify(body.uom) : p.uom,
    supplier_id: body.supplier_id != null ? Number(body.supplier_id) || null : p.supplier_id
  };
  run(`UPDATE products SET type=?,node_id=?,identity=?,attrs=?,vertical=?,media=?,seo=?,tax_rule=?,geo_rules=?,pricing_rules=?,logistics=?,packaging=?,docs=?,uom=?,supplier_id=? WHERE tenant_id=? AND id=?`,
    set.type, set.node_id, set.identity, set.attrs, set.vertical, set.media, set.seo, set.tax_rule, set.geo_rules, set.pricing_rules, set.logistics, set.packaging, set.docs, set.uom, set.supplier_id, t, id);
  logAction(s, "product.meta", "product", id, { fields: Object.keys(body) });
  json(res, 200, { ok: true });
}
function apiAdminLifecycle(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const p = get("SELECT lifecycle FROM products WHERE tenant_id=? AND id=?", T(s), id);
  if (!p) return bad(res, "Unknown product", 404);
  const to = String(body.to || "");
  if (!rl("lifecycle").includes(to)) return bad(res, "Unknown state");
  if (!((rl("lifecycleTransitions")[p.lifecycle] || []).includes(to))) return bad(res, `Cannot move ${p.lifecycle} → ${to}`);
  run("UPDATE products SET lifecycle=? WHERE tenant_id=? AND id=?", to, T(s), id);
  logAction(s, "product.lifecycle", "product", id, { from: p.lifecycle, to });
  json(res, 200, { ok: true, lifecycle: to });
}
function apiAdminSkuSave(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  const pid = String(body.product_id);
  if (id) {
    run("UPDATE skus SET code=?,name=?,identity=?,variant=?,price=?,mrp=?,stock=?,active=? WHERE id=? AND tenant_id=?",
      String(body.code), String(body.name || ""), JSON.stringify(body.identity || {}), JSON.stringify(body.variant || {}),
      Number(body.price), body.mrp ? Number(body.mrp) : null, Number(body.stock) || 0, body.active === 0 ? 0 : 1, Number(id), t);
    if (body.inventory) for (const inv of body.inventory) run("INSERT INTO inventory(tenant_id,sku_id,warehouse_id,qty,reserved,lot,batch,expiry,serial) VALUES(?,?,?,?,?,?,?,?,?)",
      t, Number(id), inv.warehouse_id || null, Number(inv.qty) || 0, Number(inv.reserved) || 0, inv.lot || "", inv.batch || "", inv.expiry || "", JSON.stringify(inv.serial || []));
  } else {
    const r = run("INSERT INTO skus(tenant_id,product_id,code,name,identity,variant,price,mrp,stock) VALUES(?,?,?,?,?,?,?,?,?)",
      t, pid, String(body.code), String(body.name || ""), JSON.stringify(body.identity || {}), JSON.stringify(body.variant || {}), Number(body.price), body.mrp ? Number(body.mrp) : null, Number(body.stock) || 0);
    logAction(s, "sku.create", "sku", r.lastInsertRowid, { product: pid });
    json(res, 200, { id: Number(r.lastInsertRowid) });
    return;
  }
  logAction(s, "sku.update", "sku", id);
  json(res, 200, { ok: true });
}
function apiAdminSkuDelete(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  run("DELETE FROM skus WHERE id=? AND tenant_id=?", Number(id), T(s));
  run("DELETE FROM inventory WHERE sku_id=? AND tenant_id=?", Number(id), T(s));
  logAction(s, "sku.delete", "sku", id);
  json(res, 200, { ok: true });
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
function apiAdminRelationshipAdd(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  if (!rl("relTypes").some(r => r.key === body.type)) return bad(res, "Unknown relationship type");
  if (!get("SELECT id FROM products WHERE tenant_id=? AND id=?", T(s), body.to_id)) return bad(res, "Target product unknown", 404);
  run("INSERT INTO relationships(tenant_id,from_id,to_id,type) VALUES(?,?,?,?)", T(s), id, String(body.to_id), String(body.type));
  logAction(s, "relationship.add", "relationship", id, { to: body.to_id, type: body.type });
  json(res, 200, { ok: true });
}
function apiAdminRelationshipDelete(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  run("DELETE FROM relationships WHERE id=? AND tenant_id=?", Number(id), T(s));
  json(res, 200, { ok: true });
}
function apiAdminWarehouses(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { warehouses: all("SELECT * FROM warehouses WHERE tenant_id=?", T(s)) });
}
function apiAdminWarehouseSave(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  if (!body.name) return bad(res, "Name required");
  if (id) run("UPDATE warehouses SET name=?,code=?,country=?,region=?,active=? WHERE id=? AND tenant_id=?", String(body.name), String(body.code || ""), String(body.country || "US"), String(body.region || ""), body.active === 0 ? 0 : 1, Number(id), T(s));
  else run("INSERT INTO warehouses(tenant_id,name,code,country,region) VALUES(?,?,?,?,?)", T(s), String(body.name), String(body.code || ""), String(body.country || "US"), String(body.region || ""));
  logAction(s, "warehouse.save", "warehouse", id || "new");
  json(res, 200, { ok: true });
}

/* ---------------- promotions engine ---------------- */
function activePromos(tenantId, coupon) {
  coupon = String(coupon || "").trim().toUpperCase();
  const now = new Date().toISOString().slice(0, 10);
  return all("SELECT * FROM promotions WHERE tenant_id=? AND status='active' AND (starts IS NULL OR starts<=?) AND (ends IS NULL OR ends>=?)", tenantId, now, now)
    .filter(p => !p.code || p.code.toUpperCase() === coupon)
    .map(p => ({ ...p, rules: J(p.rules), scope: J(p.scope) }));
}
function promoApplies(p, items, tenantId) {
  if (p.scope.node) {
    const ids = nodeDescendants(tenantId, get("SELECT id FROM taxonomy WHERE tenant_id=? AND key=?", tenantId, p.scope.node).id);
    if (!items.some(i => i.product.node_id && ids.includes(i.product.node_id))) return false;
  }
  if (p.scope.products && !items.some(i => p.scope.products.includes(i.product.id))) return false;
  if (p.rules.min && cartSubtotal(items) < p.rules.min) return false;
  return true;
}
function cartSubtotal(items) { return items.reduce((n, i) => n + i.product.p * i.qty, 0); }
function applyPromos(tenantId, items, coupon, opts) {
  opts = opts || {};
  const codesAllowed = sec.policy().provisioning.couponsAllowed;
  const amount = items.reduce((n, i) => n + i.product.p * i.qty, 0);
  const mapped = items.map(i => ({ id: i.product.id, dept: i.product.d, brand: i.product.b, node_id: i.product.node_id, price: i.product.p, qty: i.qty }));
  const res = offers.evaluate({ channel: "commerce", tenantId, items: mapped, amount, coupon: codesAllowed ? coupon : "", owner: opts.owner || null, currency: opts.currency || null, allowGlobal: sec.policy().provisioning.globalOffersAllowed !== false });
  return { discount: res.discount, applied: res.applied, credits: res.credits, freeShip: res.freeShip, redemptions: res.redemptions };
}
function contractPriceFor(tenantId, buyerEmail, productId, qty) {
  if (!buyerEmail) return null;
  const today = new Date().toISOString().slice(0, 10);
  const cts = all("SELECT * FROM contracts WHERE tenant_id=? AND status='active' AND lower(buyer_email)=?", tenantId, String(buyerEmail).toLowerCase());
  let best = null;
  for (const c of cts) {
    if (c.valid_from && c.valid_from > today) continue;
    if (c.valid_to && c.valid_to < today) continue;
    let pid = []; try { pid = JSON.parse(c.product_ids || "[]"); } catch (e) { }
    if (!pid.includes(productId) || qty < (c.min_qty || 1)) continue;
    let pr = {}; try { pr = JSON.parse(c.pricing || "{}"); } catch (e) { }
    let price = null;
    if (pr.fixed && pr.fixed[productId] != null) price = Number(pr.fixed[productId]);
    else if (Array.isArray(pr.tiers)) for (const t of pr.tiers) if ((t.product_id || t.product) === productId && qty >= (t.qty || 1)) price = Number(t.price);
    if (price != null && (best == null || price < best)) best = price;
  }
  return best;
}
function effectivePrice(p, qty) {
  const pr = J(p.pricing_rules);
  if (pr.tiers) { let price = p.price; for (const t of pr.tiers) if (qty >= t.qty) price = t.price; return price; }
  return p.price;
}
function apiPromos(req, res, url, s) {
  json(res, 200, { promotions: activePromos(T(s)).map(p => ({ id: p.id, name: p.name, type: p.type, value: p.value, code: p.code, scope: p.scope })) });
}
function apiAdminPromotions(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { promotions: all("SELECT * FROM promotions WHERE tenant_id=? ORDER BY id DESC", T(s)).map(p => ({ ...p, rules: J(p.rules), scope: J(p.scope) })) });
}
function apiAdminPromoSave(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  if (!body.name || !rl("promoTypes").some(t => t.key === body.type)) return bad(res, "Name and valid type required");
  const vals = [String(body.name), String(body.type), Number(body.value) || 0, JSON.stringify(body.rules || {}), JSON.stringify(body.scope || {}), body.starts || null, body.ends || null, body.status === "inactive" ? "inactive" : "active", String(body.code || "")];
  if (id) run("UPDATE promotions SET name=?,type=?,value=?,rules=?,scope=?,starts=?,ends=?,status=?,code=? WHERE id=? AND tenant_id=?", ...vals, Number(id), T(s));
  else run("INSERT INTO promotions(tenant_id,name,type,value,rules,scope,starts,ends,status,code) VALUES(?,?,?,?,?,?,?,?,?,?)", T(s), ...vals);
  logAction(s, "promo.save", "promotion", id || body.name);
  json(res, 200, { ok: true });
}
function apiAdminPromoDelete(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  run("DELETE FROM promotions WHERE id=? AND tenant_id=?", Number(id), T(s));
  logAction(s, "promo.delete", "promotion", id);
  json(res, 200, { ok: true });
}

/* ---------------- sellers / rfq / returns / settlements ---------------- */
function apiAdminSellers(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { sellers: all("SELECT * FROM sellers WHERE tenant_id=? ORDER BY id", T(s)), roles: rl("sellerRoles") });
}
function apiAdminSellerSave(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  if (!body.name || !rl("sellerRoles").includes(body.role)) return bad(res, "Name and valid role required");
  if (id) run("UPDATE sellers SET name=?,role=?,email=?,status=?,commission_pct=? WHERE id=? AND tenant_id=?", String(body.name), String(body.role), String(body.email || ""), String(body.status || "active"), Number(body.commission_pct), Number(id), T(s));
  else run("INSERT INTO sellers(tenant_id,name,role,email,status,commission_pct) VALUES(?,?,?,?,?,?)", T(s), String(body.name), String(body.role), String(body.email || ""), "active", Number(body.commission_pct) || 5);
  logAction(s, "seller.save", "seller", id || body.name);
  json(res, 200, { ok: true });
}
function apiAdminSellerDelete(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  run("DELETE FROM sellers WHERE id=? AND tenant_id=?", Number(id), T(s));
  logAction(s, "seller.delete", "seller", id);
  json(res, 200, { ok: true });
}
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
  run("UPDATE rfqs SET status=?, quotes=? WHERE id=?", ["open", "quoted", "accepted", "rejected", "closed"].includes(body.status) ? body.status : r.status, JSON.stringify(quotes), r.id);
  logAction(s, "rfq.update", "rfq", r.ref, { status: body.status });
  json(res, 200, { ok: true });
}
function apiReturnCreate(req, res, url, s, body) {
  const o = get("SELECT * FROM orders WHERE num=? AND owner=?", String(body.order_num || ""), ownerFor(s));
  if (!o) return bad(res, "Order not found", 404);
  const ref = "RET-" + (2000 + get("SELECT COUNT(*) c FROM returns WHERE tenant_id=?", T(s)).c + 1);
  run("INSERT INTO returns(tenant_id,ref,order_id,product_id,qty,reason,status) VALUES(?,?,?,?,?,?, 'requested')",
    T(s), ref, o.id, String(body.product_id || ""), Number(body.qty) || 1, String(body.reason || ""));
  logAction(s, "return.create", "return", ref, { order: o.num });
  json(res, 200, { ok: true, ref });
}
function apiAdminReturns(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { returns: all("SELECT r.*, o.num order_num FROM returns r LEFT JOIN orders o ON o.id=r.order_id WHERE r.tenant_id=? ORDER BY r.created_at DESC", T(s)) });
}
function apiAdminReturnUpdate(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const allowed = ["requested", "approved", "received", "refunded", "rejected"];
  if (!allowed.includes(body.status)) return bad(res, "Invalid status");
  const r = get("SELECT * FROM returns WHERE id=? AND tenant_id=?", Number(id), T(s));
  run("UPDATE returns SET status=? WHERE id=? AND tenant_id=?", body.status, Number(id), T(s));
  if (body.status === "refunded" && r && r.order_id) { const ord = get("SELECT num FROM orders WHERE id=?", r.order_id); try { offers.reverseRedemption(T(s), { order_id: r.order_id, order_num: ord && ord.num }); } catch (e) { console.error("clawback:", e.message); } }
  logAction(s, "return.update", "return", id, { status: body.status });
  json(res, 200, { ok: true });
}
function apiOffersAnalytics(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const a = offers.analytics(T(s));
  const redemptions = all("SELECT * FROM coupon_redemptions WHERE tenant_id=? ORDER BY id DESC LIMIT 200", T(s));
  json(res, 200, Object.assign({ redemptions }, a));
}
function apiAdminSettlements(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { settlements: all("SELECT st.*, se.name seller FROM settlements st LEFT JOIN sellers se ON se.id=st.seller_id WHERE st.tenant_id=? ORDER BY st.id DESC", T(s)) });
}
function apiAdminSettlementGenerate(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  const period = String(body.period || new Date().toISOString().slice(0, 7));
  const orders = all("SELECT o.*, oi.product_id FROM orders o JOIN order_items oi ON oi.order_id=o.id WHERE o.tenant_id=? AND strftime('%Y-%m', o.created_at)=?", t, period);
  let made = 0;
  const bySeller = {};
  for (const o of orders) {
    const p = get("SELECT supplier_id FROM products WHERE tenant_id=? AND id=?", t, o.product_id);
    if (!p || !p.supplier_id) continue;
    bySeller[p.supplier_id] = (bySeller[p.supplier_id] || 0) + o.price * o.qty;
  }
  for (const [sid, gross] of Object.entries(bySeller)) {
    const seller = get("SELECT * FROM sellers WHERE id=? AND tenant_id=?", Number(sid), t);
    if (!seller) continue;
    const comm = +(gross * seller.commission_pct / 100).toFixed(2);
    run("INSERT INTO settlements(tenant_id,ref,seller_id,gross,commission,net,status,period) VALUES(?,?,?,?,?,?, 'pending', ?)",
      t, "STL-" + (3000 + get("SELECT COUNT(*) c FROM settlements WHERE tenant_id=?", t).c + 1), seller.id, +gross.toFixed(2), comm, +(gross - comm).toFixed(2), period);
    made++;
  }
  logAction(s, "settlement.generate", "settlement", period, { count: made });
  json(res, 200, { ok: true, generated: made });
}
function apiAdminAnalytics(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  const byDay = all("SELECT date(created_at) d, COUNT(*) orders, COALESCE(SUM(total),0) revenue FROM orders WHERE tenant_id=? AND created_at>=datetime('now','-30 days') GROUP BY d ORDER BY d", t);
  const topProducts = all("SELECT oi.product_id, p.title, p.emoji, SUM(oi.qty) units, SUM(oi.qty*oi.price) rev FROM order_items oi JOIN orders o ON o.id=oi.order_id AND o.tenant_id=? JOIN products p ON p.tenant_id=o.tenant_id AND p.id=oi.product_id GROUP BY oi.product_id ORDER BY rev DESC LIMIT 8", t);
  const byIndustry = all("SELECT tx.name industry, SUM(oi.qty*oi.price) rev FROM order_items oi JOIN orders o ON o.id=oi.order_id AND o.tenant_id=? JOIN products p ON p.tenant_id=o.tenant_id AND p.id=oi.product_id JOIN taxonomy tx ON tx.id=p.node_id GROUP BY tx.name ORDER BY rev DESC", t);
  const byType = all("SELECT type, COUNT(*) c FROM products WHERE tenant_id=? GROUP BY type", t);
  const invValue = get("SELECT COALESCE(SUM(i.qty*s.price),0) v FROM inventory i JOIN skus s ON s.id=i.sku_id AND s.tenant_id=i.tenant_id WHERE i.tenant_id=?", t).v;
  const funnel = { views: get("SELECT COUNT(*) c FROM view_history WHERE tenant_id LIKE 't' || ? || '%'", String(t)).c, carts: get("SELECT COUNT(DISTINCT owner) c FROM cart_items WHERE owner LIKE 't" + t + ":%'").c, orders: get("SELECT COUNT(*) c FROM orders WHERE tenant_id=?", t).c };
  json(res, 200, { byDay, topProducts, byIndustry, byType, invValue, funnel, lowStock: all("SELECT id,title,stock FROM products WHERE tenant_id=? AND stock<=10 ORDER BY stock LIMIT 10", t) });
}
function apiAdminModePut(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const mode = rl("deployModes").some(m => m.key === body.mode) ? body.mode : "marketplace";
  const inds = Array.isArray(body.industries) ? JSON.stringify(body.industries) : "[]";
  run("UPDATE tenants SET mode=?, industries=? WHERE id=?", mode, inds, T(s));
  s.tenant.mode = mode; s.tenant.industries = inds;
  logAction(s, "tenant.mode", "tenant", T(s), { mode, industries: body.industries });
  json(res, 200, { ok: true, mode, industries: J(inds, []) });
}

/* ================= UNIVERSAL ENTITY ENGINE ================= */
const entity = require("./entity.js");
function entityPerm(s, def, write) {
  const roles = write ? (def.perm.write || []) : (def.perm.read || []);
  if (def.platformOnly) return roles.includes("platform") && !!s.platform_admin;
  if (roles.includes("platform") && s.platform_admin) return true;
  if (roles.includes("admin") && isAdmin(s)) return true;
  return false;
}
function apiEntities(req, res, url, s) {
  const defs = entity.allEntities(T(s));
  const out = {};
  for (const [k, d] of Object.entries(defs)) {
    if (!entityPerm(s, d, false)) continue;
    out[k] = { ...d, fields: d.fields.map(f => ({ ...f, options: Array.isArray(f.options) ? f.options : undefined })) };
  }
  json(res, 200, { entities: out });
}
function apiEntityList(req, res, url, s, body, key) {
  const defs = entity.allEntities(T(s));
  const def = defs[key];
  if (!def) return bad(res, "Unknown entity", 404);
  if (!entityPerm(s, def, false)) return bad(res, "Not permitted", 403);
  const hide = governance.isSoft(key) && url.searchParams.get("trash") !== "1";
  json(res, 200, { entity: key, rows: entity.listEntities(T(s), key, { hideDeleted: hide }) });
}
function apiEntityCreate(req, res, url, s, body, key) {
  const defs = entity.allEntities(T(s));
  const def = defs[key];
  if (!def) return bad(res, "Unknown entity", 404);
  if (!entityPerm(s, def, true)) return bad(res, "Not permitted", 403);
  const r = entity.createEntity(T(s), key, body || {});
  if (r.error) return bad(res, r.error);
  logAction(s, key + ".create", key, r.id, body);
  json(res, 200, { ok: true, id: r.id });
}
function apiEntityUpdate(req, res, url, s, body, key, id) {
  const defs = entity.allEntities(T(s));
  const def = defs[key];
  if (!def) return bad(res, "Unknown entity", 404);
  if (!entityPerm(s, def, true)) return bad(res, "Not permitted", 403);
  const r = entity.updateEntity(T(s), key, id, body || {});
  if (r.error) return bad(res, r.error, r.code || 400);
  logAction(s, key + ".update", key, id, body);
  json(res, 200, { ok: true });
}
function apiEntityDelete(req, res, url, s, body, key, id) {
  const defs = entity.allEntities(T(s));
  const def = defs[key];
  if (!def) return bad(res, "Unknown entity", 404);
  if (!entityPerm(s, def, true)) return bad(res, "Not permitted", 403);
  if (key === "currency") {
    if (get("SELECT 1 ok FROM countries WHERE currency=?", String(id))) return bad(res, "Currency is the official currency of a country entity — reassign that country first");
    if (all("SELECT value FROM settings WHERE key='commerce'").some(r => JSON.stringify(r).includes('"' + id + '"'))) return bad(res, "Currency in use by a store — switch that store's currency first");
  }
  if (governance.isSoft(key) && url.searchParams.get("hard") !== "1") {
    const t = governance.trash(T(s), key, id);
    if (t.error) return bad(res, t.error, t.code || 400);
    logAction(s, key + ".trash", key, id);
    return json(res, 200, { ok: true, trashed: true });
  }
  const r = entity.deleteEntity(T(s), key, id);
  if (r.error) return bad(res, r.error);
  logAction(s, key + ".delete", key, id);
  json(res, 200, { ok: true });
}
/* ---------- governance: trash, restore, purge, retention ---------- */
function apiTrashList(req, res, url, s) { if (!requireAdmin(s, res)) return; json(res, 200, { counts: governance.counts(T(s)), items: governance.listTrash(T(s), 100), retention: governance.getRetention(T(s)) }); }
function apiTrashRestore(req, res, url, s, body, key, id) {
  if (!requireAdmin(s, res)) return;
  const r = governance.restore(T(s), key, id); if (r.error) return bad(res, r.error, r.code || 400);
  logAction(s, key + ".restore", key, id, {}, req); json(res, 200, { ok: true });
}
function apiTrashPurge(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return; const r = governance.purge(T(s)); logAction(s, "governance.purge", "governance", null, { purged: r.purged }, req); json(res, 200, r);
}
function apiRetentionGet(req, res, url, s) { if (!requireAdmin(s, res)) return; json(res, 200, { retention: governance.getRetention(T(s)), defaults: governance.defaultRetention(), soft: [...governance.SOFT] }); }
function apiRetentionPut(req, res, url, s, body) { if (!requireAdmin(s, res)) return; governance.setRetention(T(s), body || {}); logAction(s, "governance.retention", "governance", null, { changed: Object.keys(body || {}).join(",") }, req); json(res, 200, { ok: true, retention: governance.getRetention(T(s)) }); }
function apiAdminPurgeExpired(req, res, url, s) { if (!requirePlatform(s, res)) return; let total = {}; for (const t of all("SELECT id FROM tenants")) { const r = governance.purge(t.id); Object.assign(total, r.purged); } logAction(s, "governance.purge_all", "governance", null, { purged: total }, req); json(res, 200, { ok: true, purged: total }); }
function apiEntityDefSave(req, res, url, s, body) {
  if (!requireAdmin(s, res) && !s.platform_admin) return bad(res, "Not permitted", 403);
  const key = String(body.key || "").trim().toLowerCase().replace(/[^a-z0-9_]/g, "");
  if (!key || !body.label || !Array.isArray(body.fields)) return bad(res, "key, label and fields[] required");
  const def = { table: null, storage: "json", pk: "id", label: String(body.label), icon: String(body.icon || "🧬"), perm: { read: ["admin", "platform"], write: ["admin", "platform"] }, fields: body.fields };
  const isPlat = s.platform_admin && body.scope === "platform";
  run("INSERT INTO entity_defs(key,scope,tenant_id,def) VALUES(?,?,?,?) ON CONFLICT(key,scope,tenant_id) DO UPDATE SET def=excluded.def",
    key, isPlat ? "platform" : "tenant", isPlat ? 0 : T(s), JSON.stringify(def));
  logAction(s, "entity_def.save", "entity_def", key);
  json(res, 200, { ok: true });
}
function apiEntityDefDelete(req, res, url, s, body, key) {
  if (!requireAdmin(s, res) && !s.platform_admin) return bad(res, "Not permitted", 403);
  run("DELETE FROM entity_defs WHERE key=? AND (scope='tenant' AND tenant_id=? OR scope='platform')", key, T(s));
  run("DELETE FROM entity_data WHERE entity=?", key);
  logAction(s, "entity_def.delete", "entity_def", key);
  json(res, 200, { ok: true });
}

/* ---------- contracts / tenders / serialized (B2B + unit serialization) ---------- */
const newRef = pre => pre + "-" + Date.now().toString(36).toUpperCase() + crypto.randomBytes(2).toString("hex").toUpperCase();
function apiAdminContractCreate(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  if (!body.buyer_name || !body.buyer_email) return bad(res, "Buyer name and email required");
  const inc = rl("incoterms"), pt = rl("paymentTerms"), cs = rl("contractStatuses");
  const ref = newRef("CT");
  run("INSERT INTO contracts(tenant_id,ref,buyer_name,buyer_email,buyer_org,supplier_id,product_ids,currency,pricing,min_qty,incoterms,payment_terms,valid_from,valid_to,status,notes) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
    T(s), ref, String(body.buyer_name), String(body.buyer_email), String(body.buyer_org || ""), body.supplier_id ? Number(body.supplier_id) : null,
    JSON.stringify(body.product_ids || []), String(body.currency || "USD"), JSON.stringify(body.pricing || {}), Number(body.min_qty) || 1,
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
    String(body.currency || "USD"), Number(body.budget) || 0, body.open_at || null, body.close_at || null, "open", JSON.stringify(body.items || []));
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
    T(s), ref, String(t.buyer_org || "Tender Winner"), String(t.buyer_email || ""), String(t.buyer_org || ""), String(t.currency || "USD"),
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
    T(s), ref, String(r.buyer_name || ""), String(r.buyer_email || ""), String(r.currency || "USD"), JSON.stringify(r.product_id ? [r.product_id] : []),
    JSON.stringify(price && r.product_id ? { fixed: { [r.product_id]: price } } : {}), Number(r.qty) || 1, new Date().toISOString().slice(0, 10), "active", "Converted from " + r.ref);
  run("UPDATE rfqs SET status='accepted' WHERE id=?", r.id);
  logAction(s, "rfq.to_contract", "rfq", r.ref, { contract: ref });
  json(res, 200, { ok: true, contract_ref: ref, contract_id: Number(c.lastInsertRowid) });
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

/* ---------- AI product layer (capabilities, run, usage, tasks) ---------- */
function apiAiOverview(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { capabilities: ai.capabilities(T(s)), plan: ai.planInfo(T(s)), usage: ai.usage(T(s)), settings: CFG(s).ai || {} });
}
function apiAiRun(req, res, url, s, body, capability) {
  if (!requireAdmin(s, res)) return;
  const [type, , name] = actor(s);
  const out = ai.run(T(s), capability, body || {}, name || type);
  if (out.error) return bad(res, out.error, out.code || 400);
  let offerDiscount = 0;
  try { const d = offers.discountFor("ai", T(s), out.cost || 0, { owner: ownerFor(s), coupon: s.coupon }); if (d.discount) { offerDiscount = d.discount; out.cost = +Math.max(0, out.cost - d.discount).toFixed(4); } if (d.credits) offers.credit(T(s), ownerFor(s), d.credits, "cashback", "ai:" + capability, "USD", "ai", "ai"); } catch (e) { }
  out.offer_discount = offerDiscount;
  try { if ((out.cost || 0) > 0) billing.recordUsage(T(s), "ai", capability + " · " + out.provider, out.units, (out.cost) / Math.max(1, out.units), { currency: "USD", period: billing.monthOf(), ref: "ai:" + capability }); } catch (e) { }
  logAction(s, "ai.run", "ai_usage", capability, { provider: out.provider, model: out.model, units: out.units, cost: out.cost, tier: out.tier }, req);
  emitEvent(T(s), "ai.usage", { capability, provider: out.provider, units: out.units, cost: out.cost, tier: out.tier }, null);
  json(res, 200, out);
}
function apiAiUsage(req, res, url, s) { if (!requireAdmin(s, res)) return; json(res, 200, ai.usage(T(s))); }
function apiAiTasks(req, res, url, s) { if (!requireAdmin(s, res)) return; json(res, 200, { tasks: ai.tasks(T(s)) }); }
function apiAiTaskCreate(req, res, url, s, body) {
  return (async () => {
  if (!requireAdmin(s, res)) return;
  if (!(ai.capabilities(T(s)).find(c => c.key === body.capability))) return bad(res, "Unknown capability");
  const id = ai.createTask(T(s), body.capability, body.params || {}, (actor(s)[2] || actor(s)[0]));
  let ran = null; if (body.runNow) ran = await queueNow().push({ type: "ai-task", id });
  logAction(s, "ai.task.create", "ai_task", id, { capability: body.capability });
  json(res, 200, { ok: true, id, queued: !!(ran && !ran.ran), tasks: ai.tasks(T(s)) });
  })();
}
function apiAiTaskRun(req, res, url, s, body, id) { return (async () => { if (!requireAdmin(s, res)) return; const r = await queueNow().push({ type: "ai-task", id: Number(id) }); json(res, 200, { result: r.out, tasks: ai.tasks(T(s)) }); })(); }
function apiPlatformAi(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const tenants = all("SELECT id,slug,name FROM tenants");
  const usage = all(`SELECT ai.tenant_id, t.slug, SUM(ai.cost) cost, COUNT(*) calls FROM ai_usage ai JOIN tenants t ON t.id=ai.tenant_id GROUP BY ai.tenant_id, t.slug`);
  json(res, 200, { providers: registry.providerDefs("ai"), capabilities: ai.AI_CAPABILITIES, plans: ai.AI_PLANS, tierByTenant: tenants.map(t => ({ id: t.id, slug: t.slug, name: t.name, ...ai.tierOf(t.id) })), usage });
}

/* ---------- runtime configuration + configurable storage/queue services ---------- */
const _svc = { q: null, s: null };
function queueNow() { if (!_svc.q) _svc.q = adapters.build("queue", rtconfig.get("queue")); return _svc.q; }
function storeNow() { if (!_svc.s) _svc.s = adapters.build("storage", rtconfig.get("storage")); return _svc.s; }
function csvOf(rows) { if (!rows.length) return ""; const cols = Object.keys(rows[0]); return [cols.join(",")].concat(rows.map(r => cols.map(c => { const v = r[c]; const s = v == null ? "" : (typeof v === "object" ? JSON.stringify(v) : String(v)); return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; }).join(","))).join("\n"); }
function buildExport(tenantId, kind) {
  if (kind === "products") return csvOf(all("SELECT id,title,brand,dept,type,price,list_price,stock,lifecycle FROM products WHERE tenant_id=? ORDER BY id", tenantId));
  if (kind === "orders") return csvOf(all("SELECT num,name,city,status,sub,tax,total,currency,created_at FROM orders WHERE tenant_id=? ORDER BY id DESC", tenantId));
  if (kind === "ai_usage") return csvOf(all("SELECT capability,provider,tier,units,cost,created_at FROM ai_usage WHERE tenant_id=? ORDER BY id DESC", tenantId));
  if (kind === "serialized") return csvOf(all("SELECT product_id,serial,status,batch,lot,expiry,warranty_end FROM serialized_items WHERE tenant_id=? ORDER BY id", tenantId));
  if (kind === "offers") return csvOf(all("SELECT name,code,type,direction,channel,funder,value,used,status FROM offers WHERE tenant_id=? OR tenant_id=0", tenantId));
  return "";
}
/* queue + storage handlers (registered once; the queue driver decides inline vs redis vs hook) */
adapters.registerHandler("ai-task", (job) => ai.processTask(job.id));
adapters.registerHandler("export", async (job) => { const csv = buildExport(job.tenantId, job.kind); const key = `${job.tenantId}-${job.kind}-${Date.now()}.csv`; const r = await storeNow().put(key, csv, "text/csv"); return r; });

function apiAdminExport(req, res, url, s, body, kind) {
  return (async () => {
    if (!requireAdmin(s, res)) return;
    if (!["products", "orders", "ai_usage", "serialized", "offers"].includes(kind)) return bad(res, "Unknown export kind");
    const r = await queueNow().push({ type: "export", tenantId: T(s), kind });
    json(res, 200, { ok: true, mode: r.mode || "inline", result: r.out || null, queued: !r.ran });
  })();
}
function apiPlatformRuntime(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const rt = rtconfig.runtime();
  const active = { cache: adapters.build("cache", rt.cache).kind, ratelimit: adapters.build("ratelimit", rt.ratelimit).kind, storage: storeNow().kind, queue: queueNow().kind };
  json(res, 200, { runtime: rt, catalog: rtconfig.describe(), active, offline: outboundOffline() });
}
function apiPlatformRuntimePut(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  try { rtconfig.saveRuntime(body || {}); } catch (e) { return bad(res, e.message); }
  _svc.q = null; _svc.s = null; /* rebuild adapters on next use with the new drivers */
  logAction(s, "platform.runtime", "runtime", "update", { changed: Object.keys(body || {}).join(",") }, req);
  json(res, 200, { ok: true, runtime: rtconfig.runtime() });
}
function apiPlatformRuntimeTest(req, res, url, s, body) {
  return (async () => {
    if (!requirePlatform(s, res)) return;
    const concern = String(body && body.concern || "");
    const cfg = rtconfig.get(concern) || {};
    try {
      if (concern === "db") { if (cfg.driver !== "postgres") return json(res, 200, { concern, kind: cfg.driver, ok: true, note: "sqlite is in-process" }); return json(res, 200, Object.assign({ concern }, await adapters.build("db", cfg).ping())); }
      if (cfg.driver === "redis") { const r = await adapters.redis((cfg.params || {}).url).call(["PING"]); return json(res, 200, { concern, kind: "redis", ok: !(r && r.__error), reply: r }); }
      if (cfg.driver === "webhook") { return json(res, 200, { concern, kind: "webhook", ok: !!(cfg.params && cfg.params.url) }); }
      return json(res, 200, { concern, kind: cfg.driver, ok: true, note: "in-process driver, no remote to test" });
    } catch (e) { return json(res, 200, { concern, ok: false, error: e.message }); }
  })();
}
function apiPlatformQueueDrain(req, res, url, s, body) {
  return (async () => {
    if (!requirePlatform(s, res)) return;
    const r = await queueNow().drain(Math.min(200, Number(body && body.batch) || 50));
    /* also flush any persisted AI tasks in-process (works for inline or redis backends) */
    let done = 0; for (const t of all("SELECT id FROM tenants")) { const ts = ai.tasks(t.id).filter(x => x.status === "queued"); for (const x of ts) { ai.processTask(x.id); done++; } }
    json(res, 200, { ok: true, queue: r, aiTasksProcessed: done });
  })();
}

/* ---------- environments + feature flags (unlimited named envs, all data) ---------- */
function resetRuntimeSvc() { _svc.q = null; _svc.s = null; }
function apiEnvList(req, res, url, s) { if (!requirePlatform(s, res)) return; const e = env.list(); json(res, 200, { environments: e, active: (e.find(x => x.active) || {}).name || null }); }
function apiEnvGet(req, res, url, s, body, name) { if (!requirePlatform(s, res)) return; const e = env.get(String(name || "")); if (!e) return bad(res, "Unknown environment", 404); json(res, 200, { environment: e }); }
function apiEnvUpsert(req, res, url, s, body, name) { if (!requirePlatform(s, res)) return; try { const e = env.upsert(name || body.name, body); logAction(s, "environment.save", "environment", name || body.name, { concerns: Object.keys(body.runtime || {}).join(",") }, req); json(res, 200, { ok: true, environment: e }); } catch (e) { return bad(res, e.message); } }
function apiEnvDelete(req, res, url, s, body, name) { if (!requirePlatform(s, res)) return; env.remove(String(name || "")); logAction(s, "environment.delete", "environment", name); json(res, 200, { ok: true }); }
function apiEnvActivate(req, res, url, s, body, name) {
  return (async () => {
    if (!requirePlatform(s, res)) return;
    try { const r = env.activate(String(name || "")); resetRuntimeSvc(); logAction(s, "environment.activate", "environment", r.active, {}, req); json(res, 200, r); } catch (e) { return bad(res, e.message); }
  })();
}
function apiEnvExport(req, res, url, s) { if (!requirePlatform(s, res)) return; json(res, 200, { bundle: env.exportAll() }); }
function apiEnvImport(req, res, url, s, body) { if (!requirePlatform(s, res)) return; try { const r = env.importAll(body && body.bundle, { activate: !!(body && body.activate) }); if (body && body.activate) resetRuntimeSvc(); logAction(s, "environment.import", "environment", null, { imported: r.imported }, req); json(res, 200, r); } catch (e) { return bad(res, e.message); } }
function apiFlags(req, res, url, s) { if (!requirePlatform(s, res)) return; json(res, 200, { flags: env.flags() }); }
function apiFlagSet(req, res, url, s, body, name) { if (!requirePlatform(s, res)) return; try { json(res, 200, { ok: true, flag: env.setFlag(name || body.name, body) }); } catch (e) { return bad(res, e.message); } }
function apiFlagDelete(req, res, url, s, body, name) { if (!requirePlatform(s, res)) return; env.delFlag(String(name || "")); json(res, 200, { ok: true }); }
function apiEnvTenant(req, res, url, s) { if (!requireAdmin(s, res)) return; json(res, 200, env.resolveFlags(T(s))); }

/* ---------- central offers / coupons / wallet ledger ---------- */
function mapOffer(r) { return { ...r, scope: J(r.scope_value, {}), rules: J(r.rules, {}) }; }
function apiOffersList(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const allowGlobal = sec.policy().provisioning.globalOffersAllowed !== false;
  const rows = all(`SELECT * FROM offers WHERE tenant_id=? ${allowGlobal ? "OR tenant_id=0" : ""} ORDER BY priority DESC, id DESC`, T(s)).map(mapOffer);
  json(res, 200, { offers: rows, active: rows.filter(o => o.status === "active" && (!o.starts || o.starts <= new Date().toISOString().slice(0, 10)) && (!o.ends || o.ends >= new Date().toISOString().slice(0, 10))) });
}
function apiOfferSave(req, res, url, s, body, id) {
  if (!isAdmin(s) && !s.platform_admin) return bad(res, "Not permitted", 403);
  const types = rl("offerTypes"), chans = rl("offerChannels"), dirs = rl("offerDirections"), scopes = rl("offerScopes"), funders = rl("offerFunders"), stacks = rl("stackingPolicies");
  if (!body.name || !types.some(t => t.key === body.type)) return bad(res, "Name and a valid offer type are required");
  const globalReq = (body.scope_level === "global" || Number(body.tenant_id) === 0) && s.platform_admin;
  const tid = globalReq ? 0 : T(s);
  const f = {
    tenant_id: tid, scope_level: globalReq ? "global" : "tenant",
    name: String(body.name), code: String(body.code || "").toUpperCase(),
    type: body.type, direction: dirs.includes(body.direction) ? body.direction : ((types.find(t => t.key === body.type) || {}).direction || "discount"),
    channel: chans.includes(body.channel) ? body.channel : "commerce",
    scope_type: scopes.includes(body.scope_type) ? body.scope_type : "store",
    funder: funders.includes(body.funder) ? body.funder : "self", funder_ref: String(body.funder_ref || ""), brand_ref: String(body.brand_ref || ""),
    value: Number(body.value) || 0, currency: String(body.currency || "USD"), min_amount: Number(body.min_amount) || 0, min_qty: Number(body.min_qty) || 0, max_discount: Number(body.max_discount) || 0,
    usage_limit: Number(body.usage_limit) || 0, per_owner_limit: Number(body.per_owner_limit) || 0, stack_group: String(body.stack_group || ""), stack_policy: stacks.includes(body.stack_policy) ? body.stack_policy : "stack_with_others",
    priority: Number(body.priority) || 0, scope_value: JSON.stringify(body.scope || {}), rules: JSON.stringify(body.rules || {}),
    starts: body.starts || null, ends: body.ends || null, status: rl("offerStatuses").includes(body.status) ? body.status : "active", summary: String(body.summary || "")
  };
  const K = Object.keys(f), V = K.map(k => f[k]);
  if (id) {
    const owns = get("SELECT id,tenant_id FROM offers WHERE id=?", Number(id)); if (!owns) return bad(res, "Not found", 404);
    if (owns.tenant_id !== tid && !(s.platform_admin && owns.tenant_id === 0)) return bad(res, "Not permitted", 403);
    run(`UPDATE offers SET ${K.map(k => k + "=?").join(",")} WHERE id=?`, ...V, Number(id));
  } else {
    run(`INSERT INTO offers(${K.join(",")}) VALUES(${K.map(() => "?").join(",")})`, ...V);
  }
  logAction(s, "offer.save", "offer", id || f.name, { type: f.type, channel: f.channel, funder: f.funder, global: globalReq });
  json(res, 200, { ok: true, id: id ? Number(id) : Number(get("SELECT id FROM offers ORDER BY id DESC LIMIT 1").id) });
}
function apiOfferDelete(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const o = get("SELECT id,tenant_id FROM offers WHERE id=?", Number(id)); if (!o) return bad(res, "Not found", 404);
  if (o.tenant_id !== T(s) && !(s.platform_admin && o.tenant_id === 0)) return bad(res, "Not permitted", 403);
  run("UPDATE offers SET status='inactive' WHERE id=?", Number(id)); logAction(s, "offer.retire", "offer", id); json(res, 200, { ok: true });
}
function apiOffersPreview(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const res2 = offers.evaluate({ channel: body.channel || "commerce", tenantId: T(s), items: body.items || [], amount: body.amount, coupon: body.coupon, owner: body.owner || (s.user_id ? ownerFor(s) : null), currency: body.currency || commerceOf(s).currency, allowGlobal: true });
  json(res, 200, res2);
}
function apiCouponsList(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { coupons: all("SELECT * FROM coupons WHERE tenant_id=? OR tenant_id=0 ORDER BY id DESC", T(s)), redemptions: all("SELECT * FROM coupon_redemptions WHERE tenant_id=? ORDER BY id DESC LIMIT 200", T(s)) });
}
function apiCouponCreate(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const kinds = rl("couponKinds");
  const prefix = (CFG(s).offers && CFG(s).offers.couponCodePrefix) || "";
  const code = String(body.code || (prefix + crypto.randomBytes(4).toString("hex"))).toUpperCase();
  try {
    run("INSERT INTO coupons(tenant_id,code,offer_id,funder,funder_ref,brand_ref,kind,value,currency,max_uses,per_owner_limit,issued_to,batch,starts,ends,status,note) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
      T(s), code, body.offer_id ? Number(body.offer_id) : null, rl("offerFunders").includes(body.funder) ? body.funder : "self", String(body.funder_ref || ""), String(body.brand_ref || ""), kinds.includes(body.kind) ? body.kind : "single_use", Number(body.value) || 0, String(body.currency || "USD"), Number(body.max_uses) || 1, Number(body.per_owner_limit) || 1, String(body.issued_to || ""), String(body.batch || ""), body.starts || null, body.ends || null, "active", String(body.note || ""));
  } catch (e) { return bad(res, "Duplicate code", 409); }
  logAction(s, "coupon.create", "coupon", code, { kind: body.kind, funder: body.funder });
  json(res, 200, { ok: true, code, id: Number(get("SELECT id FROM coupons WHERE tenant_id=? AND code=?", T(s), code).id) });
}
function apiCouponGenerate(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const n = Math.min(1000, Math.max(1, Number(body.count) || 1)); const prefix = String(body.prefix || (CFG(s).offers && CFG(s).offers.couponCodePrefix) || "CPN").toUpperCase();
  const batch = body.batch || ("B" + Date.now().toString(36)); const made = [];
  for (let i = 0; i < n; i++) { const code = (prefix + "-" + crypto.randomBytes(3).toString("hex")).toUpperCase(); try { run("INSERT INTO coupons(tenant_id,code,offer_id,funder,funder_ref,brand_ref,kind,value,currency,max_uses,per_owner_limit,batch,ends,status,note) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", T(s), code, body.offer_id ? Number(body.offer_id) : null, rl("offerFunders").includes(body.funder) ? body.funder : "self", String(body.funder_ref || ""), String(body.brand_ref || ""), kinds2(body.kind), Number(body.value) || 0, "USD", Number(body.max_uses) || 1, Number(body.per_owner_limit) || 1, batch, body.ends || null, "active", "bulk"); made.push(code); } catch (e) { i--; } }
  function kinds2(k) { return rl("couponKinds").includes(k) ? k : "single_use"; }
  logAction(s, "coupon.generate", "coupon", batch, { count: made.length });
  json(res, 200, { ok: true, batch, count: made.length, codes: made });
}
function apiCouponVoid(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const r = run("UPDATE coupons SET status='revoked' WHERE id=? AND tenant_id=?", Number(id), T(s)); if (!r.changes) return bad(res, "Not found", 404);
  logAction(s, "coupon.void", "coupon", id); json(res, 200, { ok: true });
}
function apiWalletLedger(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const owner = String(url.searchParams.get("owner") || (s.user_id ? ownerFor(s) : ""));
  json(res, 200, { owner, entries: offers.ledger(T(s), owner), balance: mods.walletBalance(T(s), owner) });
}
function apiPlatformOffers(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const global = all("SELECT * FROM offers WHERE tenant_id=0 ORDER BY id DESC").map(mapOffer);
  json(res, 200, { global, stats: offers.stats(), redemptions: all("SELECT * FROM coupon_redemptions WHERE 1=1 ORDER BY id DESC LIMIT 200") });
}

/* ---------- webhooks (outbound events) + universal entity metadata (tags/notes via global uid) ---------- */
function apiWebhooksList(req, res, url, s) { if (!requireAdmin(s, res)) return; json(res, 200, Object.assign({ events: events.webhookEvents() }, events.list(T(s)))); }
function apiWebhookCreate(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  if (!body.url || !/^https?:\/\//i.test(String(body.url))) return bad(res, "A valid https URL is required");
  const id = events.create(T(s), body); logAction(s, "webhook.create", "webhook", id, { url: body.url, events: body.events }, req);
  json(res, 200, { ok: true, id });
}
function apiWebhookUpdate(req, res, url, s, body, id) { if (!requireAdmin(s, res)) return; if (!events.update(Number(id), T(s), body)) return bad(res, "Not found", 404); logAction(s, "webhook.update", "webhook", id, {}, req); json(res, 200, { ok: true }); }
function apiWebhookDelete(req, res, url, s, body, id) { if (!requireAdmin(s, res)) return; if (!events.remove(Number(id), T(s))) return bad(res, "Not found", 404); logAction(s, "webhook.delete", "webhook", id); json(res, 200, { ok: true }); }
function apiWebhookTest(req, res, url, s, body, id) {
  return (async () => {
    if (!requireAdmin(s, res)) return;
    const did = events.emit(T(s), body && body.event || "store.test", { message: "LUXORA webhook test", at: new Date().toISOString() }, null);
    const ids = did.length ? did : [Number(events.create(T(s), { url: (get("SELECT url FROM webhooks WHERE id=? AND tenant_id=?", Number(id), T(s)) || {}).url || "", events: ["*"] }))];
    let resu = null; for (const d of ids) resu = await events.deliver(d);
    json(res, 200, { ok: true, delivery: ids[0], result: resu });
  })();
}
function apiWebhookDrain(req, res, url, s, body) { return (async () => { if (!requireAdmin(s, res)) return; json(res, 200, await events.drain(T(s), Number(body && body.batch) || 25)); })(); }
function apiEntityTags(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const entity = String(url.searchParams.get("entity") || ""), uid = String(url.searchParams.get("uid") || "");
  const row = get("SELECT tags, meta, notes FROM entity_meta WHERE tenant_id=? AND entity=? AND ref_uid=?", T(s), entity, uid);
  json(res, 200, { entity, uid, tags: row ? J(row.tags, []) : [], meta: row ? J(row.meta, {}) : {}, notes: row ? row.notes : "" });
}
function apiEntityTagsSave(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const entity = String(body.entity || ""), uid = String(body.uid || ""); if (!entity || !uid) return bad(res, "entity and uid required");
  run(`INSERT INTO entity_meta(tenant_id,entity,ref_uid,tags,meta,notes,updated_at) VALUES(?,?,?,?,?,?,datetime('now'))
       ON CONFLICT(tenant_id,entity,ref_uid) DO UPDATE SET tags=excluded.tags, meta=excluded.meta, notes=excluded.notes, updated_at=datetime('now')`,
    T(s), entity, uid, JSON.stringify(body.tags || []), JSON.stringify(body.meta || {}), String(body.notes || ""));
  logAction(s, "entity_meta.save", entity, uid); json(res, 200, { ok: true });
}

/* ---------- router ---------- */
const routes = [
  ["GET /api/config", apiConfig],
  ["GET /api/stores", apiStores],
  ["GET /api/providers", apiProviders],
  ["GET /api/meta", apiMeta],
  ["GET /api/meta/entities", apiEntities],
  ["GET /api/meta/entity/:key", (r, re, u, s, b, p) => apiEntityList(r, re, u, s, b, p)],
  ["GET /api/admin/trash", apiTrashList],
  ["POST /api/admin/trash/:key/:id/restore", (r, re, u, s, b, p, i) => apiTrashRestore(r, re, u, s, b, p, i)],
  ["POST /api/admin/trash/purge", apiTrashPurge],
  ["GET /api/admin/retention", apiRetentionGet],
  ["PUT /api/admin/retention", apiRetentionPut],
  ["POST /api/platform/purge-expired", apiAdminPurgeExpired],
  ["POST /api/meta/entity/:key", (r, re, u, s, b, p) => apiEntityCreate(r, re, u, s, b, p)],
  ["PUT /api/meta/entity/:key/:id", (r, re, u, s, b, p, i) => apiEntityUpdate(r, re, u, s, b, p, i)],
  ["DELETE /api/meta/entity/:key/:id", (r, re, u, s, b, p, i) => apiEntityDelete(r, re, u, s, b, p, i)],
  ["POST /api/meta/entity-def", apiEntityDefSave],
  ["DELETE /api/meta/entity-def/:key", (r, re, u, s, b, p) => apiEntityDefDelete(r, re, u, s, b, p)],
  ["GET /api/taxonomy", apiTaxonomy],
  ["GET /api/promos", apiPromos],
  ["POST /api/rfqs", apiRfqCreate],
  ["POST /api/returns", apiReturnCreate],
  ["GET /api/session", apiSession],
  ["POST /api/zip", apiZip],
  ["GET /api/fx", apiFxConvert],
  ["GET /api/platform/hint", apiPlatformHint],
  ["GET /api/hint", apiHint],
  ["GET /api/platform/fx", apiPlatformFx],
  ["POST /api/platform/fx/rates", apiPlatformFxRates],
  ["PUT /api/platform/fx/provider", apiPlatformFxProvider],
  ["POST /api/platform/fx/sync", (r, re, u, s, b) => apiPlatformFxSync(r, re, u, s)],
  ["POST /api/coupon", apiCoupon],
  ["POST /api/auth/register", apiRegister],
  ["POST /api/auth/login", apiLogin],
  ["POST /api/auth/logout", apiLogout],
  ["POST /api/auth/token-exchange", apiTokenExchange],
  ["GET /api/products", apiProducts],
  ["GET /api/products/:id", apiProduct],
  ["GET /api/cart", apiCartGet],
  ["POST /api/cart", apiCartAdd],
  ["PUT /api/cart", apiCartPut],
  ["DELETE /api/cart/:id", (r, re, u, s, b, p) => apiCartDel(r, re, u, s, b, p)],
  ["POST /api/saved", apiSavedAdd],
  ["DELETE /api/saved/:id", (r, re, u, s, b, p) => apiSavedDel(r, re, u, s, b, p)],
  ["POST /api/saved/:id/move", (r, re, u, s, b, p) => apiSavedMove(r, re, u, s, b, p)],
  ["GET /api/orders", apiOrders],
  ["POST /api/checkout", apiCheckout],
  ["POST /api/reviews/:id", (r, re, u, s, b, p) => apiReviewAdd(r, re, u, s, b, p)],
  ["POST /api/giftcard", apiGiftAdd],
  ["POST /api/viewed", apiViewed],
  ["GET /api/admin/stats", apiAdminStats],
  ["GET /api/admin/products", apiAdminProducts],
  ["GET /api/admin/products/:id", (r, re, u, s, b, p) => apiAdminProductGet(r, re, u, s, b, p)],
  ["POST /api/admin/products", apiAdminProductCreate],
  ["PUT /api/admin/products/:id", (r, re, u, s, b, p) => apiAdminProductUpdate(r, re, u, s, b, p)],
  ["PUT /api/admin/products/:id/meta", (r, re, u, s, b, p) => apiAdminProductSaveMeta(r, re, u, s, b, p)],
  ["POST /api/admin/products/:id/lifecycle", (r, re, u, s, b, p) => apiAdminLifecycle(r, re, u, s, b, p)],
  ["POST /api/admin/products/:id/relationships", (r, re, u, s, b, p) => apiAdminRelationshipAdd(r, re, u, s, b, p)],
  ["DELETE /api/admin/products/:id", (r, re, u, s, b, p) => apiAdminProductDelete(r, re, u, s, b, p)],
  ["GET /api/admin/taxonomy", apiAdminTaxonomy],
  ["POST /api/admin/taxonomy", (r, re, u, s, b, p) => apiAdminTaxSave(r, re, u, s, b, p)],
  ["PUT /api/admin/taxonomy/:id", (r, re, u, s, b, p) => apiAdminTaxSave(r, re, u, s, b, p)],
  ["DELETE /api/admin/taxonomy/:id", (r, re, u, s, b, p) => apiAdminTaxDelete(r, re, u, s, b, p)],
  ["GET /api/admin/attributes", apiAdminAttributes],
  ["POST /api/admin/attributes", apiAdminAttrSave],
  ["DELETE /api/admin/attributes/:key", (r, re, u, s, b, p) => apiAdminAttrDelete(r, re, u, s, b, p)],
  ["POST /api/admin/skus", (r, re, u, s, b, p) => apiAdminSkuSave(r, re, u, s, b, p)],
  ["PUT /api/admin/skus/:id", (r, re, u, s, b, p) => apiAdminSkuSave(r, re, u, s, b, p)],
  ["DELETE /api/admin/skus/:id", (r, re, u, s, b, p) => apiAdminSkuDelete(r, re, u, s, b, p)],
  ["PUT /api/admin/inventory/:id", (r, re, u, s, b, p) => apiAdminInventoryPut(r, re, u, s, b, p)],
  ["DELETE /api/admin/relationships/:id", (r, re, u, s, b, p) => apiAdminRelationshipDelete(r, re, u, s, b, p)],
  ["GET /api/admin/warehouses", apiAdminWarehouses],
  ["POST /api/admin/warehouses", (r, re, u, s, b, p) => apiAdminWarehouseSave(r, re, u, s, b, p)],
  ["PUT /api/admin/warehouses/:id", (r, re, u, s, b, p) => apiAdminWarehouseSave(r, re, u, s, b, p)],
  ["GET /api/admin/promotions", apiAdminPromotions],
  ["POST /api/admin/promotions", (r, re, u, s, b, p) => apiAdminPromoSave(r, re, u, s, b, p)],
  ["PUT /api/admin/promotions/:id", (r, re, u, s, b, p) => apiAdminPromoSave(r, re, u, s, b, p)],
  ["DELETE /api/admin/promotions/:id", (r, re, u, s, b, p) => apiAdminPromoDelete(r, re, u, s, b, p)],
  ["GET /api/admin/sellers", apiAdminSellers],
  ["POST /api/admin/sellers", (r, re, u, s, b, p) => apiAdminSellerSave(r, re, u, s, b, p)],
  ["PUT /api/admin/sellers/:id", (r, re, u, s, b, p) => apiAdminSellerSave(r, re, u, s, b, p)],
  ["DELETE /api/admin/sellers/:id", (r, re, u, s, b, p) => apiAdminSellerDelete(r, re, u, s, b, p)],
  ["GET /api/admin/rfqs", apiAdminRfqs],
  ["PUT /api/admin/rfqs/:id", (r, re, u, s, b, p) => apiAdminRfqUpdate(r, re, u, s, b, p)],
  ["GET /api/admin/returns", apiAdminReturns],
  ["PUT /api/admin/returns/:id", (r, re, u, s, b, p) => apiAdminReturnUpdate(r, re, u, s, b, p)],
  ["GET /api/admin/settlements", apiAdminSettlements],
  ["POST /api/admin/settlements/generate", apiAdminSettlementGenerate],
  ["GET /api/admin/analytics", apiAdminAnalytics],
  ["PUT /api/admin/mode", apiAdminModePut],
  ["GET /api/admin/orders", apiAdminOrders],
  ["PUT /api/admin/orders/:id/status", (r, re, u, s, b, p) => apiAdminOrderStatus(r, re, u, s, b, p)],
  ["GET /api/admin/users", apiAdminUsers],
  ["DELETE /api/admin/users/:id", (r, re, u, s, b, p) => apiAdminUserDelete(r, re, u, s, b, p)],
  ["GET /api/admin/reviews", apiAdminReviews],
  ["DELETE /api/admin/reviews/:id", (r, re, u, s, b, p) => apiAdminReviewDelete(r, re, u, s, b, p)],
  ["GET /api/admin/settings", apiAdminSettingsGet],
  ["PUT /api/admin/settings", apiAdminSettingsPut],
  ["POST /api/admin/settings/reset", apiAdminSettingsReset],
  ["GET /api/admin/departments", apiAdminDepartments],
  ["POST /api/admin/departments", apiAdminDeptSave],
  ["DELETE /api/admin/departments/:key", (r, re, u, s, b, p) => apiAdminDeptDelete(r, re, u, s, b, p)],
  ["GET /api/admin/banners", apiAdminBanners],
  ["POST /api/admin/banners", (r, re, u, s, b, p) => apiAdminBannerSave(r, re, u, s, b, p)],
  ["PUT /api/admin/banners/:id", (r, re, u, s, b, p) => apiAdminBannerSave(r, re, u, s, b, p)],
  ["DELETE /api/admin/banners/:id", (r, re, u, s, b, p) => apiAdminBannerDelete(r, re, u, s, b, p)],
  ["GET /api/admin/cards", apiAdminCards],
  ["POST /api/admin/cards", (r, re, u, s, b, p) => apiAdminCardSave(r, re, u, s, b, p)],
  ["PUT /api/admin/cards/:id", (r, re, u, s, b, p) => apiAdminCardSave(r, re, u, s, b, p)],
  ["DELETE /api/admin/cards/:id", (r, re, u, s, b, p) => apiAdminCardDelete(r, re, u, s, b, p)],
  ["PUT /api/admin/account", apiAdminAccount],
  ["GET /api/admin/gateways", apiAdminGateways],
  ["PUT /api/admin/gateways", apiAdminGatewaysPut],
  ["POST /api/admin/gateways/:id/test", (r, re, u, s, b, p) => apiAdminGatewayTest(r, re, u, s, b, p)],
  ["GET /api/admin/payments", apiAdminPayments],
  ["POST /api/admin/payments/:id/refund", (r, re, u, s, b, p) => apiAdminPaymentRefund(r, re, u, s, b, p)],
  ["GET /api/admin/billing", apiAdminBilling],
  ["GET /api/admin/audit", apiAdminAudit],
  ["GET /api/admin/monitor", (r, re, u, s, b, p, m, met) => apiAdminMonitor(r, re, u, s, b, met)],
  ["GET /api/admin/custom-providers", apiAdminCustomProviders],
  ["POST /api/admin/custom-providers", apiAdminCustomProviderAdd],
  ["DELETE /api/admin/custom-providers/:id", (r, re, u, s, b, p) => apiAdminCustomProviderDelete(r, re, u, s, b, p)],
  ["POST /api/admin/contracts", apiAdminContractCreate],
  ["PUT /api/admin/contracts/:id/status", (r, re, u, s, b, p) => apiAdminContractStatus(r, re, u, s, b, p)],
  ["POST /api/admin/tenders", apiAdminTenderCreate],
  ["POST /api/admin/tenders/:id/award", (r, re, u, s, b, p) => apiAdminTenderAward(r, re, u, s, b, p)],
  ["POST /api/admin/rfqs/:id/contract", (r, re, u, s, b, p) => apiAdminRfqToContract(r, re, u, s, b, p)],
  ["POST /api/admin/serialized/bulk", apiAdminSerializedBulk],
  ["GET /api/ai", apiAiOverview],
  ["POST /api/ai/run/:capability", (r, re, u, s, b, p) => apiAiRun(r, re, u, s, b, p)],
  ["GET /api/ai/usage", apiAiUsage],
  ["GET /api/ai/tasks", apiAiTasks],
  ["POST /api/ai/tasks", apiAiTaskCreate],
  ["POST /api/ai/tasks/:id/run", (r, re, u, s, b, p) => apiAiTaskRun(r, re, u, s, b, p)],
  ["GET /api/platform/ai", apiPlatformAi],
  ["GET /api/offers", apiOffersList],
  ["POST /api/offers", (r, re, u, s, b) => apiOfferSave(r, re, u, s, b, null)],
  ["PUT /api/offers/:id", (r, re, u, s, b, p) => apiOfferSave(r, re, u, s, b, p)],
  ["DELETE /api/offers/:id", (r, re, u, s, b, p) => apiOfferDelete(r, re, u, s, b, p)],
  ["POST /api/offers/preview", apiOffersPreview],
  ["GET /api/offers/analytics", apiOffersAnalytics],
  ["GET /api/offers/coupons", apiCouponsList],
  ["POST /api/offers/coupons", apiCouponCreate],
  ["POST /api/offers/coupons/generate", apiCouponGenerate],
  ["DELETE /api/offers/coupons/:id", (r, re, u, s, b, p) => apiCouponVoid(r, re, u, s, b, p)],
  ["GET /api/wallet/ledger", apiWalletLedger],
  ["GET /api/platform/offers", apiPlatformOffers],
  ["GET /api/platform/runtime", apiPlatformRuntime],
  ["PUT /api/platform/runtime", apiPlatformRuntimePut],
  ["POST /api/platform/runtime/test", apiPlatformRuntimeTest],
  ["POST /api/platform/queue/drain", apiPlatformQueueDrain],
  ["GET /api/platform/environments", apiEnvList],
  ["POST /api/platform/environments", (r, re, u, s, b, p) => apiEnvUpsert(r, re, u, s, b, (u.searchParams.get("name") || (b && b.name)))],
  ["GET /api/platform/environments/:name", (r, re, u, s, b, p) => apiEnvGet(r, re, u, s, b, p)],
  ["PUT /api/platform/environments/:name", (r, re, u, s, b, p) => apiEnvUpsert(r, re, u, s, b, p)],
  ["DELETE /api/platform/environments/:name", (r, re, u, s, b, p) => apiEnvDelete(r, re, u, s, b, p)],
  ["POST /api/platform/environments/:name/activate", (r, re, u, s, b, p) => apiEnvActivate(r, re, u, s, b, p)],
  ["GET /api/platform/environments-export", apiEnvExport],
  ["POST /api/platform/environments-import", apiEnvImport],
  ["GET /api/platform/flags", apiFlags],
  ["PUT /api/platform/flags/:name", (r, re, u, s, b, p) => apiFlagSet(r, re, u, s, b, p)],
  ["DELETE /api/platform/flags/:name", (r, re, u, s, b, p) => apiFlagDelete(r, re, u, s, b, p)],
  ["GET /api/env/tenant", apiEnvTenant],
  ["POST /api/admin/export/:kind", (r, re, u, s, b, p) => apiAdminExport(r, re, u, s, b, p)],
  ["POST /api/platform/login", apiPlatformLogin],
  ["POST /api/platform/logout", apiPlatformLogout],
  ["GET /api/platform/me", apiPlatformMe],
  ["GET /api/platform/security", apiPlatformSecurity],
  ["GET /api/platform/modules", apiPlatformModules],
  ["POST /api/platform/modules/:id/install", (r, re, u, s, b, p) => apiModuleInstall(r, re, u, s, b, p)],
  ["POST /api/platform/modules/:id/uninstall", (r, re, u, s, b, p) => apiModuleUninstall(r, re, u, s, b, p)],
  ["POST /api/platform/modules/:id/configure", (r, re, u, s, b, p) => apiModuleConfigure(r, re, u, s, b, p)],
  ["GET /api/modules", apiStoreModules],
  ["GET /api/market", apiMarket],
  ["POST /api/modules/purchase", apiModulePurchase],
  ["POST /api/modules/release", apiModuleRelease],
  ["GET /api/seo/sitemap.xml", apiSeoSitemap],
  ["GET /api/reco/:id", (r, re, u, s, b, p) => apiReco(r, re, u, s, b, p)],
  ["GET /api/facets", apiFacets],
  ["POST /api/billing/invoices/:id/pay", (r, re, u, s, b, p) => apiBillingPay(r, re, u, s, b, p)],
  ["GET /api/platform/config", apiPlatformConfigGet],
  ["PUT /api/platform/config", apiPlatformConfigPut],
  ["GET /api/platform/chain/verify", apiPlatformChainVerify],
  ["POST /api/platform/keys/rotate", apiPlatformKeyRotate],
  ["GET /api/admin/chain/verify", apiAdminChainVerify],
  ["GET /api/platform/tenants", apiPlatformTenants],
  ["POST /api/platform/tenants", apiPlatformTenantCreate],
  ["PUT /api/platform/tenants/:id", (r, re, u, s, b, p) => apiPlatformTenantUpdate(r, re, u, s, b, p)],
  ["DELETE /api/platform/tenants/:id", (r, re, u, s, b, p) => apiPlatformTenantDelete(r, re, u, s, b, p)],
  ["POST /api/platform/tenants/:id/impersonate", (r, re, u, s, b, p) => apiPlatformImpersonate(r, re, u, s, b, p)],
  ["GET /api/platform/plans", apiPlatformPlans],
  ["POST /api/platform/plans", (r, re, u, s, b, p) => apiPlatformPlanSave(r, re, u, s, b, p)],
  ["PUT /api/platform/plans/:id", (r, re, u, s, b, p) => apiPlatformPlanSave(r, re, u, s, b, p)],
  ["POST /api/platform/tenants/:id/subscribe", (r, re, u, s, b, p) => apiPlatformSubscribe(r, re, u, s, b, p)],
  ["GET /api/platform/invoices", apiPlatformInvoices],
  ["POST /api/platform/tenants/:id/invoice", (r, re, u, s, b, p) => apiPlatformInvoiceGenerate(r, re, u, s, b, p)],
  ["POST /api/platform/invoices/:id/refund", (r, re, u, s, b, p) => apiPlatformInvoiceRefund(r, re, u, s, b, p)],
  ["POST /api/platform/billing/dunning", apiPlatformDunning],
  ["GET /api/platform/billing/aging", apiPlatformAging],
  ["POST /api/platform/usage", apiPlatformUsage],
  ["GET /api/admin/billing/detail", apiAdminBillingDetail],
  ["GET /api/admin/tax", apiAdminTaxConfig],
  ["POST /api/admin/tax/quote", apiAdminTaxQuote],
  ["GET /api/marketing/providers", apiMarketingProviders],
  ["POST /api/marketing/save", apiMarketingSave],
  ["POST /api/marketing/send", apiMarketingSend],
  ["GET /api/admin/webhooks", apiWebhooksList],
  ["POST /api/admin/webhooks", apiWebhookCreate],
  ["PUT /api/admin/webhooks/:id", (r, re, u, s, b, p) => apiWebhookUpdate(r, re, u, s, b, p)],
  ["DELETE /api/admin/webhooks/:id", (r, re, u, s, b, p) => apiWebhookDelete(r, re, u, s, b, p)],
  ["POST /api/admin/webhooks/:id/test", (r, re, u, s, b, p) => apiWebhookTest(r, re, u, s, b, p)],
  ["POST /api/admin/webhooks/drain", apiWebhookDrain],
  ["GET /api/admin/entity-meta", apiEntityTags],
  ["PUT /api/admin/entity-meta", apiEntityTagsSave],
  ["POST /api/platform/invoices/:id/pay", (r, re, u, s, b, p) => apiPlatformInvoicePay(r, re, u, s, b, p)],
  ["GET /api/platform/monitor", (r, re, u, s, b, p, m, met) => apiPlatformMonitor(r, re, u, s, b, met)],
  ["GET /api/platform/audit", apiPlatformAudit],
  ["GET /api/platform/revenue", apiPlatformRevenue],
  ["GET /api/platform/custom-providers", apiPlatformCustomProviders],
  ["POST /api/platform/custom-providers", apiPlatformCustomProviderAdd],
  ["DELETE /api/platform/custom-providers/:id", (r, re, u, s, b, p) => apiPlatformCustomProviderDelete(r, re, u, s, b, p)]
];

function handle(req, res, url, session, body, metrics) {
  const method = req.method;
  const pathname = url.pathname.replace(/\/$/, "") || "/";
  const pathSegs = pathname.split("/").filter(Boolean);
  for (const [key, fn] of routes) {
    const [m, pattern] = key.split(" ");
    const parts = pattern.split("/").filter(Boolean);
    if (m !== method || parts.length !== pathSegs.length) continue;
    const params = [];
    let ok = true;
    for (let i = 0; i < parts.length; i++) {
      if (parts[i].startsWith(":")) params.push(decodeURIComponent(pathSegs[i] || ""));
      else if (parts[i] !== pathSegs[i]) { ok = false; break; }
    }
    if (!ok) continue;
    try { fn(req, res, url, session, body, params[0], params[1], metrics); } catch (e) {
      console.error(e); bad(res, "Server error: " + e.message, 500);
    }
    return true;
  }
  return false;
}

module.exports = { handle, json, bad };
