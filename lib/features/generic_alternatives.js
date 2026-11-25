/* generic alternatives: medicines with the same composition, strength and form, cheapest first */
"use strict";
const F = () => require("../features.js"), db = () => require("../db.js"), K = "generic_alternatives";
const J = v => { try { return JSON.parse(v || "{}"); } catch (e) { return {}; } };
const norm = v => String(v || "").toLowerCase().split(/[+,;/]+/).map(x => x.replace(/\s+/g, " ").trim()).filter(Boolean).sort().join("+");
function like(tid, id) {
  const P = F().params(tid, K), keys = String(P.attrs || "").split(/[\s,]+/).filter(Boolean), p = db().get("SELECT id, price, attrs, dept FROM products WHERE tenant_id=? AND id=?", Number(tid), id);
  if (!p || !keys.length) return [];
  const want = keys.map(k => norm(J(p.attrs)[k])); if (!want[0]) return [];
  return db().all("SELECT id, title, brand, price, attrs FROM products WHERE tenant_id=? AND dept=? AND id<>? AND lifecycle='published' AND deleted_at IS NULL AND stock>0 AND price<? ORDER BY price LIMIT 500", Number(tid), p.dept, p.id, p.price).filter(x => { const a = J(x.attrs); return keys.every((k, i) => norm(a[k]) === want[i]); }).slice(0, 8).map(x => ({ id: x.id, title: x.title, brand: x.brand, price: x.price, saves: Math.round((1 - x.price / p.price) * 100) }));
}
module.exports = { block: ({ tid, product }) => { const l = like(tid, product.id); return l.length ? { title: "Same medicine, for less", products: l } : null; }, open: ({ tid, query }) => ({ alternatives: like(tid, String(query.product || "")) }) };
