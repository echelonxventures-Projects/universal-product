/* LUXORA Platform — Search & Discovery at scale.
   In-memory inverted index over `products` per tenant, rebuilt lazily and invalidated on catalog
   write. Faceted query, synonym expansion (registry-driven), boost rules (registry-driven),
   and a co-occurrence recommendation engine backed by the orders + view_history graph. All
   configuration lives in meta_lists so new facets / boosts / synonyms are added from Data Studio. */
"use strict";

const db = () => require("./db.js");
const J = (v, d) => { try { return v == null || v === "" ? (d == null ? {} : d) : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d == null ? {} : d; } };

const _idx = new Map();        // tenant_id -> { builtAt, docs: Map<id, fields>, invert: Map<token, Set<id>>, facets, boosts, synonyms }

/* ---------- build / invalidate ---------- */
function invalidate(tenantId) { _idx.delete(Number(tenantId)); }

function _norm(s) { return String(s == null ? "" : s).toLowerCase().replace(/[^\p{L}\p{N}\s]/gu, " ").replace(/\s+/g, " ").trim(); }
function _toks(s) { return _norm(s).split(" ").filter(Boolean); }
function _lev(a, b) {
  // classic Damerau-Levenshtein capped at 2 (only short words are compared)
  if (a === b) return 0;
  const m = a.length, n = b.length; if (Math.abs(m - n) > 1) return m; // can't be within 1 edit
  const d = Array.from({ length: m + 1 }, (_, i) => Array.from({ length: n + 1 }, (_, j) => i === 0 ? j : j === 0 ? i : 0));
  for (let i = 1; i <= m; i++) for (let j = 1; j <= n; j++)
    d[i][j] = a[i - 1] === b[j - 1] ? d[i - 1][j - 1] : 1 + Math.min(d[i - 1][j], d[i][j - 1], d[i - 1][j - 1]);
  return d[m][n];
}

function _registry(tenantId, key, fallback) {
  try {
    const rows = db().all("SELECT items FROM meta_lists WHERE name=?", key);
    if (rows.length) {
      const v = J(rows[0].items, null);
      if (v != null && (Array.isArray(v) ? v.length : Object.keys(v).length)) return v;
    }
  } catch (e) { }
  return fallback;
}

function build(tenantId) {
  const D = db();
  const rows = D.all("SELECT id, title, brand, dept, keywords, type, price, rating, ratings_count, flags, priority, node_id FROM products WHERE tenant_id=? AND lifecycle='published' AND deleted_at IS NULL", tenantId);
  const invert = new Map();
  const docs = new Map();
  for (const p of rows) {
    const text = [p.title, p.brand, p.keywords, p.dept, p.type].join(" ");
    docs.set(p.id, p);
    for (const t of _toks(text)) {
      if (!invert.has(t)) invert.set(t, new Set());
      invert.get(t).add(p.id);
    }
    // attribute tokens (attribute_defs keys + product attrs JSON is too heavy; use keywords + title)
  }
  const boosts = _registry(tenantId, "searchBoosts", []); // [{id, reason, weight}]
  const synonyms = _registry(tenantId, "searchSynonyms", {}); // { token: [aliases] }
  const st = { docs, invert, boosts, synonyms, builtAt: Date.now() };
  _idx.set(Number(tenantId), st);
  return st;
}

function _idxFor(tenantId) {
  let st = _idx.get(Number(tenantId));
  if (!st || Date.now() - st.builtAt > 60_000) st = build(tenantId);
  return st;
}

/* ---------- faceted query ---------- */
function search(tenantId, opts) {
  opts = opts || {};
  const st = _idxFor(tenantId);
  const q = _norm(opts.q || "");
  const tokens = _toks(q);
  const expanded = new Set();
  for (const t of tokens) {
    expanded.add(t);
    const aliases = st.synonyms && st.synonyms[t];
    if (Array.isArray(aliases)) aliases.forEach(a => expanded.add(a));
    // typo tolerance: find index tokens within 1 edit (only short words, and only when it's the whole token)
    for (const k of st.invert.keys()) {
      if (k.length < 3 || k.length > 20) continue;
      if (Math.abs(k.length - t.length) > 1) continue;
      if (k !== t && _lev(k, t) <= 1) expanded.add(k);
    }
  }

  let ids;
  if (expanded.size) {
    const matches = new Set();
    for (const t of expanded) {
      const s = st.invert.get(t);
      if (s) for (const id of s) matches.add(id);
    }
    ids = [...matches];
  } else {
    ids = [...st.docs.keys()];
  }

  // faceted filters
  const facets = opts.facets || {}; // { dept: "home", type: "physical", pmin, pmax, rating, brand, ... }
  const filtered = ids.filter(id => {
    const d = st.docs.get(id); if (!d) return false;
    if (facets.dept && d.dept !== facets.dept) return false;
    if (facets.type && d.type !== facets.type) return false;
    if (facets.brand && String(d.brand).toLowerCase() !== String(facets.brand).toLowerCase()) return false;
    if (facets.pmin != null && d.price < Number(facets.pmin)) return false;
    if (facets.pmax != null && d.price > Number(facets.pmax)) return false;
    if (facets.rating != null && d.rating < Number(facets.rating)) return false;
    return true;
  });

  // scoring: relevance (coverage of expanded tokens) + boost rules
  const boostBy = new Map();
  for (const b of st.boosts || []) if (b && b.id && b.weight) boostBy.set(b.id, Number(b.weight));
  const scored = filtered.map(id => {
    const d = st.docs.get(id);
    let score = 0;
    if (expanded.size) {
      let hits = 0;
      const hay = _norm([d.title, d.brand, d.keywords].join(" "));
      for (const t of expanded) if (hay.includes(t)) hits++;
      score = hits / expanded.size;
    }
    if (boostBy.has(id)) score += boostBy.get(id);
    if (d.priority) score += 0.1;
    if (d.ratings_count) score += Math.min(0.2, Number(d.ratings_count) / 1000);
    return { id, score: score, d };
  });

  const sort = opts.sort || "relevance";
  const cmp = {
    "relevance": (a, b) => b.score - a.score,
    "price-asc": (a, b) => a.d.price - b.d.price,
    "price-desc": (a, b) => b.d.price - a.d.price,
    "rating": (a, b) => b.d.rating - a.d.rating,
    "new": (a, b) => (b.d.flags || "").includes("new") - (a.d.flags || "").includes("new")
  }[sort] || ((a, b) => b.d.ratings_count - a.d.ratings_count);
  scored.sort(cmp);

  // facet counts (from filtered set)
  const facetCounts = {};
  const count = (key, val) => { const k = key + ":" + val; facetCounts[k] = (facetCounts[k] || 0) + 1; };
  for (const { id } of scored.slice(0, 500)) { const d = st.docs.get(id); count("dept", d.dept); count("type", d.type); if (d.brand) count("brand", d.brand); }

  const per = Math.max(1, Math.min(200, Number(opts.limit) || 20));
  const page = Math.max(1, Number(opts.page) || 1);
  const slice = scored.slice((page - 1) * per, page * per);

  const D = db();
  const items = slice.map(x => {
    const p = D.get("SELECT * FROM products WHERE id=? AND tenant_id=?", x.id, tenantId);
    return p ? { id: p.id, score: +x.score.toFixed(4), title: p.title, brand: p.brand, dept: p.dept, type: p.type, price: p.price, rating: p.rating, stock: p.stock, flags: p.flags, reason: boostBy.get(x.id) ? (st.boosts.find(b => b.id === x.id) || {}).reason || "boosted" : undefined } : null;
  }).filter(Boolean);

  return { q, matched: scored.length, page, per, items, facets: facetCounts, sort };
}

/* ---------- autocomplete ---------- */
function suggest(tenantId, prefix, limit) {
  limit = Math.min(20, Number(limit) || 10);
  const st = _idxFor(tenantId);
  const p = _norm(prefix);
  if (!p) return [];
  const out = [];
  for (const t of st.invert.keys()) {
    if (t.startsWith(p)) out.push({ token: t, count: st.invert.get(t).size });
    if (out.length >= limit * 3) break;
  }
  out.sort((a, b) => b.count - a.count);
  return out.slice(0, limit).map(x => x.token);
}

/* ---------- recommendations (co-occurrence over orders + view_history) ---------- */
function recommend(tenantId, opts) {
  opts = opts || {};
  const D = db();
  const anchor = String(opts.anchor || "").trim();
  const owner = String(opts.owner || "");
  const n = Math.min(40, Number(opts.limit) || 12);
  const co = {};

  // co-purchased: products bought in the same orders as the anchor
  if (anchor) {
    const same = D.all("SELECT oi2.product_id, COUNT(*) c FROM order_items oi1 JOIN orders o ON o.id=oi1.order_id JOIN order_items oi2 ON o.id=oi2.order_id WHERE oi1.product_id=? AND o.tenant_id=? GROUP BY oi2.product_id", anchor, tenantId);
    for (const r of same) co[r.product_id] = (co[r.product_id] || 0) + Number(r.c || 0);
    // co-viewed via view_history: owners who viewed the anchor also viewed X
    const viewers = D.all("SELECT owner FROM view_history WHERE product_id=?", anchor);
    if (viewers.length) {
      const owners = viewers.map(v => v.owner).filter(Boolean);
      if (owners.length) {
        const ph = owners.map(() => "?").join(",");
        D.all(`SELECT product_id, COUNT(*) c FROM view_history WHERE product_id<>? AND owner IN (${ph}) GROUP BY product_id`, anchor, ...owners)
          .forEach(r => co[r.product_id] = (co[r.product_id] || 0) + Number(r.c || 0));
      }
    }
  }
  // owner-history: top products viewed by this owner (excluding anchor)
  if (owner) D.all("SELECT product_id FROM view_history WHERE owner=? AND product_id<>?", owner, anchor || "\u0000")
    .forEach(r => co[r.product_id] = (co[r.product_id] || 0) + 2);

  const ranked = Object.entries(co).sort((a, b) => b[1] - a[1]).slice(0, n * 2).map(([id, w]) => ({ id, w }));
  if (!ranked.length) return [];
  const ids = ranked.map(r => r.id);
  const rows = D.all("SELECT id, title, brand, dept, type, price, rating, stock FROM products WHERE tenant_id=? AND id IN (" + ids.map(() => "?").join(",") + ") AND lifecycle='published' AND deleted_at IS NULL", tenantId, ...ids);
  const map = new Map(rows.map(r => [r.id, r]));
  const out = [];
  for (const r of ranked) { const p = map.get(r.id); if (p && p.stock > 0) out.push({ id: p.id, title: p.title, brand: p.brand, dept: p.dept, type: p.type, price: p.price, rating: p.rating, weight: r.w }); if (out.length >= n) break; }
  return out;
}

/* ---------- write hooks (attach to catalog mutations from api.js / admin.js) ---------- */
function onCatalogChange(tenantId) { invalidate(tenantId); }

module.exports = { invalidate, onCatalogChange, search, suggest, recommend, build };
