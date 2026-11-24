/* LUXORA Platform — catalog domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the catalog domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "catalog", routes(kit) {
  const { shopperCall, requireStaff, CFG, DEPT_TO_INDUSTRY, J, MCX, MPX, PMX, T, actor, alerts, all, bad, brandreg, buildSearch, by, byOf, commerceOf, compliance, contractPriceFor, crypto, freshTaxonomy, fullProductDoc, get, globalRecord, json, lists, logAction, logistics, money2, options, ownerFor, planFor, platformCategories, productExtras, profileFields, publicProduct, requireAdmin, requirePlatform, resolveProductType, richcontent, rl, run, search, sortClause, storeAccessRows, storeHolderOf, storeView, taxLevels, tryJson, ugc, validateAttrs, writeBullets } = kit;

  function apiProducts(req, res, url, s) {
    const c = CFG(s);
    const { sql, args, dept, q } = buildSearch(s, url);
    const sort = url.searchParams.get("sort") || require("../defaults.js").of("productSortOrders");
    const per = Math.max(1, Math.min(200, Math.floor(Number(url.searchParams.get("limit") || url.searchParams.get("per") || c.commerce.perPage)) || 24));
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
    const revs = c.features.reviews ? ugc.listReviews(T(s), id) : [];
    const questions = c.features.qna ? ugc.listQuestions(T(s), id) : [];
    const ugcSummary = c.features.reviews || c.features.qna ? ugc.productUgc(T(s), id) : { reviews: 0, avg: 0, questions: 0 };
    const cm = commerceOf(s);
    const related = all("SELECT * FROM products WHERE tenant_id=? AND dept=? AND id!=? AND lifecycle='published' ORDER BY position LIMIT 12", T(s), p.dept, id).map(r => storeView({ ...r, about: [] }, cm));
    const skus = all("SELECT * FROM skus WHERE tenant_id=? AND product_id=? AND active=1", T(s), id).map(k => ({ ...k, identity: J(k.identity), variant: J(k.variant) }));
    const rels = all("SELECT * FROM relationships WHERE tenant_id=? AND from_id=?", T(s), id).map(r => ({ type: r.type, to: get("SELECT id,title,price,emoji,hue,stock,type FROM products WHERE tenant_id=? AND id=? AND lifecycle='published'", T(s), r.to_id) })).filter(r => r.to);
    const hist = r => { const five = Math.min(92, Math.max(45, Math.round((r - 3) * 30 + 40))); const four = Math.round((100 - five) * 0.5); const three = Math.round((100 - five - four) * 0.5); const two = Math.round((100 - five - four - three) * 0.5); return { 5: five, 4: four, 3: three, 2: two, 1: 100 - five - four - three - two }; };
    const node0 = p.node_id ? get("SELECT key FROM taxonomy WHERE id=?", p.node_id) : null;
    const ivk = (node0 ? String(node0.key) : "").split(".")[0] || (DEPT_TO_INDUSTRY || {})[p.dept] || p.dept;
    const vtOf0 = rl("verticalTypeOf") || {};
    const prof = vtOf0[ivk] || vtOf0["*"] || {}; const vctx = rl("verticalContexts") || {};
    /* the context dimensions are the registry's own keys, not the three the platform shipped
       with — an operator adding a dimension (a new context group in Data Studio) renders here
       and at checkout with no code change. A dimension the vertical's profile doesn't name
       degrades to empty rather than erroring; payment stays a set, tax/invoice a single key */
    const contexts = {};
    for (const g of Object.keys(vctx)) {
      if (!(g in prof)) { contexts[g] = []; continue; }
      const pv = prof[g];
      contexts[g] = (vctx[g] || []).filter(x => Array.isArray(pv) ? pv.includes(x.key) : x.key === pv);
    }
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
    json(res, 200, { product: publicProduct(pView), histogram: hist(pView.rating), contexts, industry: ivk || null, reviews: revs.map(rv => ({ id: rv.id, name: rv.name, r: rv.rating, title: rv.title, body: rv.body, verified: !!rv.verified, date: rv.created_at, state: rv.state, helpful: rv.votes_helpful, votes: rv.votes_total, media: rv.media, replies: rv.replies })), questions, ugc: ugcSummary, related, fbt: related.slice(0, 3), skus, relationships: rels, node: p.node_id ? get("SELECT id,name,level FROM taxonomy WHERE id=?", p.node_id) : null, locale, localized, compliance, serialized, variant_groups, supplier: supplier || null, supplier_links, tags, contract_price: buyerContract != null ? money2(cm, buyerContract) : null,
      /* the shopper and brand layer: brand-authored content and the registered-brand badge,
         and — for a signed-in shopper — the lists holding this product and their live alerts */
      rich_content: richcontent.live(T(s), id), brand_registry: brandreg.badge(T(s), p.brand), ...productExtras(s, id),
      mine: s.user_id ? { lists: lists.holding(T(s), ownerFor(s), id), alerts: alerts.watching(T(s), ownerFor(s), id).map(w => ({ ...w, target_price: money2(cm, w.target_price) })) } : null });
  }
  function apiAdminProducts(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    const q = (url.searchParams.get("q") || "").toLowerCase();
    let rows = all("SELECT * FROM products WHERE tenant_id=? ORDER BY position", T(s));
    if (q) rows = rows.filter(r => (r.title + " " + r.brand + " " + r.id).toLowerCase().includes(q));
    json(res, 200, { products: rows });
  }
  function apiAdminProductCreate(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const t = T(s);
    const plan = planFor(t);
     /* the plan quota governs the merchant's OWN catalogue. Universes activated from the
        corpus AND products imported from the platform's global catalogue are
        platform-supplied offerings (the flagship ships with the whole corpus activated by
        default; a store may list a global product only when the platform permits it), so
        neither may consume the tenant's quota — otherwise a store on a Growth plan could
        not add a single product of its own while platform supply was on its shelf. */
     const count = get("SELECT COUNT(*) c FROM products WHERE tenant_id=? AND (source_kind IS NULL OR source_kind NOT IN ('universe','global'))", t).c;
    if (count >= plan.max_products) return bad(res, `Plan limit reached (${plan.name}: ${plan.max_products} products). Upgrade to add more.`, 402);
    const title = String(body.title || "").trim(), brand = String(body.brand || "").trim(), dept = String(body.dept || "").trim();
    const price = Number(body.price);
    if (!title || !brand || !(price > 0)) return bad(res, "Title, brand and price are required");
    const ptype = resolveProductType(body.type);
    if (ptype.error) return bad(res, ptype.error, 400);
    const id = "LX" + crypto.randomBytes(4).toString("hex").toUpperCase();
    const list = Number(body.list) > price ? Number(body.list) : null;
    const pos = get("SELECT COALESCE(MAX(position),0) m FROM products WHERE tenant_id=?", t).m + 1;
    run(`INSERT INTO products(tenant_id,id,title,brand,dept,type,price,list_price,rating,ratings_count,emoji,hue,priority,stock,flags,keywords,deal_pct,position)
         VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`,
      t, id, title, brand, dept, ptype, price, list, Math.min(5, Math.max(0, Number(body.rating) || 4.5)), Math.max(0, Number(body.count) || 0),
      String(body.emoji || "🛍️").slice(0, 4), Math.floor(Math.random() * 360), body.priority ? 1 : 0, Math.max(0, Number(body.stock) || 0),
      String(body.flags || ""), String(body.keywords || title.toLowerCase()), list ? Math.round((1 - price / list) * 100) : 0, pos);
    writeBullets(t, id, body.about);
    search.onCatalogChange(t);
    logAction(s, "product.create", "product", id, { title, price, type: ptype });
    json(res, 200, { product: get("SELECT * FROM products WHERE tenant_id=? AND id=?", t, id) });
  }
  function apiAdminProductUpdate(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    const t = T(s);
    const p = get("SELECT * FROM products WHERE tenant_id=? AND id=?", t, id);
    if (!p) return bad(res, "Unknown product", 404);
    const price = body.price != null ? Number(body.price) : p.price;
    const list = body.list != null ? (Number(body.list) > price ? Number(body.list) : null) : p.list_price;
    const ptype = resolveProductType(body.type, p.type);
    if (ptype.error) return bad(res, ptype.error, 400);
    run(`UPDATE products SET title=?, brand=?, dept=?, type=?, price=?, list_price=?, rating=?, ratings_count=?, emoji=?, hue=?, priority=?, stock=?, flags=?, keywords=?, deal_pct=? WHERE tenant_id=? AND id=?`,
      body.title != null ? String(body.title).trim() : p.title, body.brand != null ? String(body.brand).trim() : p.brand,
      body.dept != null ? String(body.dept) : p.dept, ptype, price, list,
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
    search.onCatalogChange(t);
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
    search.onCatalogChange(t);
    logAction(s, "product.delete", "product", id);
    json(res, 200, { ok: true });
  }
  function apiTaxonomy(req, res, url, s) {
    freshTaxonomy(T(s));
    const rows = all("SELECT * FROM taxonomy WHERE tenant_id=? AND active=1 ORDER BY position", T(s));
    const byParent = {};
    rows.forEach(r => { (byParent[r.parent_id || 0] = byParent[r.parent_id || 0] || []).push(r); });
    function build(pid) { return (byParent[pid] || []).map(r => ({ ...r, attrs: J(r.attrs), children: build(r.id) })); }
    json(res, 200, { tree: build(0), flat: rows, levels: taxLevels() });
  }
  function apiAdminTaxonomy(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    freshTaxonomy(T(s));
    json(res, 200, { nodes: all("SELECT * FROM taxonomy WHERE tenant_id=? ORDER BY level, position", T(s)) });
  }
  function apiAdminTaxSave(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    if (!body.name) return bad(res, "Name required");
    /* the store's own category is written on the master in its namespace; an edit to a master
       category is a contribution the global platform reviews (lib/store-taxonomy.js) */
    try { require("../store-taxonomy.js").save(T(s), id || null, body, byOf(s) || actor(s)[0]); } catch (e) { return bad(res, e.message, e.status || 400); }
    logAction(s, "taxonomy.save", "taxonomy", id || body.key || body.name, { level: body.level });
    json(res, 200, { ok: true });
  }
  function apiAdminTaxDelete(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try { require("../store-taxonomy.js").remove(T(s), id, byOf(s) || actor(s)[0]); } catch (e) { return bad(res, e.message, e.status || 400); }
    logAction(s, "taxonomy.delete", "taxonomy", id);
    json(res, 200, { ok: true });
  }
  function apiAdminAttributes(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    freshTaxonomy(T(s));
    json(res, 200, { attributes: all("SELECT * FROM attribute_defs WHERE tenant_id=? ORDER BY position", T(s)).map(a => ({ ...a, options: J(a.options, []), validation: J(a.validation) })) });
  }
  function apiAdminAttrSave(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const key = String(body.key || "").trim().toLowerCase().replace(/[^a-z0-9_]/g, "");
    if (!key || !body.label) return bad(res, "Key and label required");
    /* the store's own definition on the master, or a contribution to a master one (lib/store-attributes.js) */
    try { require("../store-attributes.js").save(T(s), { ...body, key }, byOf(s) || actor(s)[0]); } catch (e) { return bad(res, e.message, e.status || 400); }
    logAction(s, "attribute.save", "attribute", key);
    json(res, 200, { ok: true });
  }
  function apiAdminAttrDelete(req, res, url, s, body, key) {
    if (!requireAdmin(s, res)) return;
    try { require("../store-attributes.js").remove(T(s), key, byOf(s) || actor(s)[0]); } catch (e) { return bad(res, e.message, e.status || 400); }
    logAction(s, "attribute.delete", "attribute", key);
    json(res, 200, { ok: true });
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
  function apiAdminRelationshipAdd(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    if (!rl("relTypes").some(r => r.key === body.type)) return bad(res, "Unknown relationship type");
    if (!get("SELECT id FROM products WHERE tenant_id=? AND id=?", T(s), body.to_id)) return bad(res, "Target product unknown", 404);
    /* RELATIONSHIP OWNS RELATIONSHIP: the primitive is written first — the product projection the
       storefront reads is DERIVED from it (registry.reconcileLinks), exactly as a country's
       subdivisions are derived from the country master. Writing the projection first and mirroring
       here best-effort left the primitive optional, so an edge added from a product page existed
       only in that store's catalogue and in nothing else that relates two entities. Idempotent —
       re-adding the same edge is a no-op at the primitive, so the projection stays single too. */
    const fromUid = (get("SELECT uid FROM products WHERE tenant_id=? AND id=?", T(s), id) || {}).uid;
    const toUid = (get("SELECT uid FROM products WHERE tenant_id=? AND id=?", T(s), body.to_id) || {}).uid;
    if (!fromUid || !toUid) return bad(res, "Product universal IDs unresolved", 500);
    run("INSERT OR IGNORE INTO links(tenant_id,type,from_entity,from_uid,to_entity,to_uid,meta) VALUES(?,?,?,?,?,?,?)",
      T(s), String(body.type), "product", fromUid, "product", toUid, JSON.stringify({ via: "admin_relationship" }));
    try { require("../registry.js").reconcileLinks(); } catch (e) { console.error("link reconcile:", e.message); }
    logAction(s, "relationship.add", "relationship", id, { to: body.to_id, type: body.type });
    json(res, 200, { ok: true });
  }
  function apiAdminRelationshipDelete(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    const row = get("SELECT * FROM relationships WHERE id=? AND tenant_id=?", Number(id), T(s));
    if (!row) return bad(res, "Unknown relationship", 404);
    /* deleting the projection row alone would leave the primitive edge behind and reconcile would
       silently restore the projection on the next pass — the removal would not stick. Removing the
       PRIMITIVE edge is what makes the delete authoritative, and reconcileLinks withdraws the
       projection with it, so the two never drift in either direction */
    const fromUid = (get("SELECT uid FROM products WHERE tenant_id=? AND id=?", T(s), row.from_id) || {}).uid;
    const toUid = (get("SELECT uid FROM products WHERE tenant_id=? AND id=?", T(s), row.to_id) || {}).uid;
    if (fromUid && toUid) run("DELETE FROM links WHERE type=? AND from_uid=? AND to_uid=?",
      row.type, fromUid, toUid);
    try { require("../registry.js").reconcileLinks(); } catch (e) { console.error("link reconcile:", e.message); }
    logAction(s, "relationship.delete", "relationship", id, { to: row.to_id, type: row.type });
    json(res, 200, { ok: true });
  }
  function apiAttributeList(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    json(res, 200, { attributes: require("../store-attributes.js").platformList() });
  }
  function apiAttributeCreate(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    if (!body.key || !body.label) return bad(res, 'key and label required', 400);
    /* the platform's registry is the master's attribute definitions */
    try { require("../store-attributes.js").platformCreate({ ...body, key: String(body.key).replace(/[^a-z0-9_]/gi, "_").toLowerCase() }, byOf(s) || actor(s)[0]); } catch (e) { return bad(res, e.message, e.status || 400); }
    logAction(s, 'attribute.create', 'attribute', body.key);
    json(res, 200, { ok: true });
  }
  /* ========== Global Product Catalog API ==========
     The global catalogue is the platform master as the console edits it (lib/gcatalog.js projects
     a master item into a record and writes a record back as master writes). Every dropdown the
     form shows comes from the API: universes and media kinds from the registry, categories and
     lifecycle states from the master, the profile fields from the product entity. */
  function apiGlobalProductList(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    const gc = require("../gcatalog.js"), PM = require("../platform-master.js");
    const products = gc.globalListWithPermissions({ category: url.searchParams.get('category'), status: url.searchParams.get('status'), universe: url.searchParams.get('universe') });
    json(res, 200, { products, universes: rl("productUniverses"), mediaKinds: rl("mediaKinds"),
      taxClasses: rl("taxClasses"), categories: platformCategories(), universeProductTypes: gc.universeTypes(),
      lifecycles: PM.vocabulary(PM.ROLES.lifecycle).map(t => ({ key: t.name, name: require("../kernel.js").text(t.title, require("../expression.js").SEED.sourceLanguage) })),
      accessLevels: require("../master-permissions.js").levels().map(t => ({ key: t.name, name: require("../kernel.js").text(t.title, require("../expression.js").SEED.sourceLanguage), actions: t.actions || [] })),
      /* the console's "store catalogue details" section renders against THIS list, so the
         form can never offer a field the validator refuses */
      profileFields: profileFields().map(f => ({ key: f.key, label: f.label, type: f.type, hint: f.hint || "" })) });
  }
  function apiGlobalProductCreate(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    if (!body.sku || !body.name) return bad(res, 'sku and name required', 400);
    let id; try { id = require("../gcatalog.js").put(globalRecord(body), null, (byOf(s) || actor(s)[0])); } catch (e) { return bad(res, e.message, e.status || 400); }
    logAction(s, 'global_product.create', 'global_product', body.sku);
    json(res, 200, { ok: true, id });
  }
  function apiGlobalProductUpdate(req, res, url, s, body, id) {
    if (!requirePlatform(s, res)) return;
    const gc = require("../gcatalog.js");
    const cur = gc.find(id);
    if (!cur) return bad(res, 'Unknown global product', 404);
    try { gc.put(globalRecord({ ...body, sku: String(body.sku || "").trim() || cur.sku }), cur.id, (byOf(s) || actor(s)[0])); } catch (e) { return bad(res, e.message, e.status || 400); }
    logAction(s, 'global_product.update', 'global_product', body.sku || cur.sku);
    json(res, 200, { ok: true });
  }
  function apiGlobalProductDelete(req, res, url, s, body, id) {
    if (!requirePlatform(s, res)) return;
    try { require("../gcatalog.js").remove(id, (byOf(s) || actor(s)[0])); } catch (e) { return bad(res, e.message, e.status || 400); }
    logAction(s, 'global_product.delete', 'global_product', id);
    json(res, 200, { ok: true });
  }
  function apiStoreProductConfig(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    const tenantId = url.searchParams.get('tenant_id');
    json(res, 200, { configs: storeAccessRows(tenantId || null), levels: require("../master-permissions.js").levels() });
  }
  function apiStoreProductConfigSet(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    if (!body.tenant_id || !body.global_product_id) return bad(res, 'tenant_id and global_product_id required', 400);
    const MP = require("../master-permissions.js");
    const level = body.enabled === false || body.enabled === 0 ? (MP.levels().find(l => !(l.actions || []).length) || {}).name : body.permissions;
    try { MP.setAccess(MP.storeHolder(body.tenant_id), String(body.global_product_id), level, byOf(s) || actor(s)[0]); } catch (e) { return bad(res, e.message, e.status || 400); }
    logAction(s, 'store_access.set', 'global_product', `${body.tenant_id}:${body.global_product_id}`, { level });
    json(res, 200, { ok: true });
  }
  function apiStoreProductConfigDelete(req, res, url, s, body, tenantId, globalId) {
    if (!requirePlatform(s, res)) return;
    const MP = require("../master-permissions.js");
    try { MP.setAccess(MP.storeHolder(tenantId), String(globalId), (MP.levels().find(l => !(l.actions || []).length) || {}).name, byOf(s) || actor(s)[0]); } catch (e) { return bad(res, e.message, e.status || 400); }
    logAction(s, 'store_access.revoke', 'global_product', `${tenantId}:${globalId}`);
    json(res, 200, { ok: true });
  }
  function apiStoreProductPermissions(req, res, url, s) {
    json(res, 200, { configs: storeAccessRows(T(s)) });
  }
  function apiMasterTree(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    const under = url.searchParams.get("under");
    tryJson(res, () => ({ nodes: PMX().tree(under || null, { depth: Number(url.searchParams.get("depth")) || 1, hierarchy: url.searchParams.get("hierarchy") || undefined, lang: url.searchParams.get("lang") || undefined }) }));
  }
  function apiMasterVocabulary(req, res, url, s, body, key) {
    if (!requirePlatform(s, res)) return;
    tryJson(res, () => ({ key, terms: PMX().vocabulary(decodeURIComponent(key)) }));
  }
  function apiMasterPermissions(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    const holder = url.searchParams.get("holder");
    tryJson(res, () => ({ permissions: holder ? MPX().of(holder) : [], actions: MPX().actions(), objects: MPX().objects(), reviews: MPX().reviews(), levels: MPX().levels() }));
  }
  function apiMasterPermissionGrant(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    tryJson(res, () => { const uid = MPX().grant(body || {}, by(s)); logAction(s, "master.permission.grant", "master_permission", uid, { holder: body.holder }); return { ok: true, uid }; });
  }
  function apiMasterPermissionRevoke(req, res, url, s, body, id) {
    if (!requirePlatform(s, res)) return;
    tryJson(res, () => { MPX().revoke(decodeURIComponent(id), null, by(s)); logAction(s, "master.permission.revoke", "master_permission", id); return { ok: true }; });
  }
  function apiMasterContributions(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    tryJson(res, () => ({ contributions: MCX().list({ holder: url.searchParams.get("holder") || null, status: url.searchParams.get("status") || null, awaiting: url.searchParams.get("awaiting") === "1" }),
      placements: PMX().vocabulary(PMX().ROLES.placements) }));
  }
  function apiMasterContributionReview(req, res, url, s, body, id) {
    if (!requirePlatform(s, res)) return;
    tryJson(res, () => { const c = MCX().review(decodeURIComponent(id), body || {}, by(s)); logAction(s, "master.contribution.review", "master_contribution", id, { status: c.status, placement: c.placement }); return { ok: true, contribution: c }; });
  }
  function apiStoreMasterPermissions(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    tryJson(res, () => ({ permissions: MPX().of(storeHolderOf(s)), actions: PMX().vocabulary(PMX().ROLES.contributionActions), kinds: PMX().vocabulary(PMX().ROLES.itemKinds),
      statuses: require("../states.js").catalog()[PMX().ROLES.contributionMachine] || null }));
  }
  function apiStoreContributions(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    tryJson(res, () => ({ contributions: MCX().list({ holder: storeHolderOf(s) }) }));
  }
  function apiStoreContributionPropose(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    tryJson(res, () => { const c = MCX().propose(storeHolderOf(s), body || {}, by(s)); logAction(s, "master.contribution.propose", "master_contribution", c.uid, { action: c.action }); return { ok: true, contribution: c }; });
  }
  function apiStoreContributionWithdraw(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    tryJson(res, () => ({ ok: true, contribution: MCX().withdraw(storeHolderOf(s), decodeURIComponent(id), by(s)) }));
  }
  function apiStoreMasterItem(req, res, url, s, body, ref) {
    if (!requireAdmin(s, res)) return;
    tryJson(res, () => { const v = MCX().view(storeHolderOf(s), decodeURIComponent(ref), { lang: url.searchParams.get("lang") || undefined }); if (!v) { const e = new Error("Not visible to this store"); e.status = 404; throw e; } return { item: v }; });
  }
  /* ========== UPIP §1/§5 · Universal Global Catalog ==========
     The platform's catalogue is populated automatically (one canonical product per corpus
     universe) and manually (console rows). A store admin may pull a global product into
     their own catalogue ONLY when the platform has permitted it — the "if the Global
     Platform permits" clause, enforced by lib/gcatalog.js, never by the store. */
  function apiGlobalCatalog(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    json(res, 200, { products: require("../gcatalog.js").globalListWithPermissions(), universes: rl("productUniverses") });
  }
  function apiStoreCatalogImport(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const gid = body && body.global_product_id;
    if (!gid) return bad(res, 'global_product_id required', 400);
    const out = require("../gcatalog.js").importToStore(T(s), gid);
    if (!out.ok) return bad(res, out.error, 403);
    logAction(s, 'product.import_global', 'product', out.id, { global_product_id: gid, universe: out.universe });
    json(res, 200, out);
  }
  function apiStoreCatalogImportable(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    /* the store console's "add from platform" picker: every global product, annotated with
       whether THIS store may import it and whether it already listed — absent permissions
       are reported, so the merchant knows what to request rather than guessing */
    const gcat = require("../gcatalog.js");
    const t = T(s);
    const listed = new Set(all('SELECT source_global_id FROM products WHERE tenant_id=? AND source_global_id IS NOT NULL', t).map(r => String(r.source_global_id)));
    const items = gcat.list().filter(p => !p.retired).map(p => {
      const gate = gcat.mayList(t, p.id);
      return { id: p.id, sku: p.sku, name: p.name, universe: p.universe, category: p.category,
        price: p.price, is_service: p.is_service, status: p.status, type: p.type,
        permitted: gate.ok, reason: gate.ok ? null : gate.reason, listed: listed.has(p.id) };
    });
    json(res, 200, { items });
  }

  const SG = () => require("../size-guides.js"), PO = () => require("../preorders.js");
  /* the size guide an item shows */
  function apiSizeGuide(req, res, url, s, body, id) { shopperCall(res, () => ({ guide: SG().forProduct(T(s), id), label: SG().on(T(s)) ? require("../capabilities.js").cap(T(s), "size_guides").label : null })); }
  /* the store's size guides */
  function apiAdminGuides(req, res, url, s) { if (requireStaff(s, res)) shopperCall(res, () => ({ on: SG().on(T(s)), guides: SG().list(T(s)), scopes: SG().SCOPES })); }
  /* adds or changes a size guide */
  function apiAdminGuideSave(req, res, url, s, body) { if (requireAdmin(s, res)) shopperCall(res, () => ({ guides: SG().save(T(s), body) })); }
  /* removes a size guide */
  function apiAdminGuideDelete(req, res, url, s, body, id) { if (requireAdmin(s, res)) shopperCall(res, () => ({ guides: SG().remove(T(s), id) })); }
  /* the items on pre-order */
  function apiAdminPreorders(req, res, url, s) { if (requireStaff(s, res)) shopperCall(res, () => ({ on: PO().on(T(s)), preorders: PO().list(T(s)) })); }
  /* puts an item on pre-order, or changes its day and how many may be promised */
  function apiAdminPreorderSave(req, res, url, s, body) { if (requireAdmin(s, res)) shopperCall(res, () => ({ preorders: PO().save(T(s), body) })); }
  /* takes an item off pre-order */
  function apiAdminPreorderDelete(req, res, url, s, body, id) { if (requireAdmin(s, res)) shopperCall(res, () => ({ preorders: PO().remove(T(s), decodeURIComponent(id)) })); }

  return [
    ["GET /api/products/:id/size-guide", (r, re, u, s, b, p) => apiSizeGuide(r, re, u, s, b, p)],
    ["GET /api/admin/size-guides", apiAdminGuides],
    ["POST /api/admin/size-guides", apiAdminGuideSave],
    ["DELETE /api/admin/size-guides/:id", (r, re, u, s, b, p) => apiAdminGuideDelete(r, re, u, s, b, p)],
    ["GET /api/admin/preorders", apiAdminPreorders],
    ["POST /api/admin/preorders", apiAdminPreorderSave],
    ["DELETE /api/admin/preorders/:id", (r, re, u, s, b, p) => apiAdminPreorderDelete(r, re, u, s, b, p)],
    ["GET /api/platform/global-products", apiGlobalProductList],
    ["POST /api/platform/global-products", apiGlobalProductCreate],
    ["PUT /api/platform/global-products/:id", (r, re, u, s, b, p) => apiGlobalProductUpdate(r, re, u, s, b, p)],
    ["DELETE /api/platform/global-products/:id", (r, re, u, s, b, p) => apiGlobalProductDelete(r, re, u, s, b, p)],
    ["GET /api/platform/store-product-config", apiStoreProductConfig],
    ["GET /api/platform/master/tree", apiMasterTree],
    ["GET /api/platform/master/vocabulary/:key", (r, re, u, s, b, p) => apiMasterVocabulary(r, re, u, s, b, p)],
    ["GET /api/platform/master/permissions", apiMasterPermissions],
    ["POST /api/platform/master/permissions", apiMasterPermissionGrant],
    ["DELETE /api/platform/master/permissions/:id", (r, re, u, s, b, p) => apiMasterPermissionRevoke(r, re, u, s, b, p)],
    ["GET /api/platform/master/contributions", apiMasterContributions],
    ["POST /api/platform/master/contributions/:id/review", (r, re, u, s, b, p) => apiMasterContributionReview(r, re, u, s, b, p)],
    ["GET /api/tenant/master/permissions", apiStoreMasterPermissions],
    ["GET /api/tenant/master/contributions", apiStoreContributions],
    ["POST /api/tenant/master/contributions", apiStoreContributionPropose],
    ["POST /api/tenant/master/contributions/:id/withdraw", (r, re, u, s, b, p) => apiStoreContributionWithdraw(r, re, u, s, b, p)],
    ["GET /api/tenant/master/items/:ref", (r, re, u, s, b, p) => apiStoreMasterItem(r, re, u, s, b, p)],
    ["POST /api/platform/store-product-config", apiStoreProductConfigSet],
    ["DELETE /api/platform/store-product-config/:tenant_id/:global_id", (r, re, u, s, b, p, q) => apiStoreProductConfigDelete(r, re, u, s, b, p, q)],
    ["GET /api/tenant/products", apiStoreProductPermissions],
    ["GET /api/platform/global-catalog", apiGlobalCatalog],
    ["GET /api/tenant/catalog/importable", apiStoreCatalogImportable],
    ["POST /api/tenant/catalog/import", (r, re, u, s, b, p) => apiStoreCatalogImport(r, re, u, s, b, p)],
    ["GET /api/platform/attributes", apiAttributeList],
    ["POST /api/platform/attributes", apiAttributeCreate],
    ["GET /api/taxonomy", apiTaxonomy],
    ["GET /api/products", apiProducts],
    ["GET /api/products/:id", apiProduct],
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
    ["DELETE /api/admin/relationships/:id", (r, re, u, s, b, p) => apiAdminRelationshipDelete(r, re, u, s, b, p)]
  ];
} };
