/* duties at checkout: an order to another country pays its import duty up front. A rate is for a
   destination and the beginning of an item's customs code; the most particular one counts. */
"use strict";
const F = () => require("../features.js"), db = () => require("../db.js");
const code = (tid, id) => { const p = db().get("SELECT identity FROM products WHERE tenant_id=? AND id=?", Number(tid), id); try { const i = JSON.parse((p || {}).identity || "{}"); return String(i.hs || i.hsn || "").replace(/\D/g, ""); } catch (e) { return ""; } };
const home = tid => String(require("../settings.js").load(tid).commerce.country || "").toUpperCase();
function rate(tid, to, hs) { return F().rows(tid, "duties_at_checkout").filter(r => r.country.toUpperCase() === to && (!r.code || hs.startsWith(String(r.code).replace(/\D/g, "")))).sort((a, b) => String(b.code || "").length - String(a.code || "").length)[0] || null; }
function due(tid, to, items, net) {
  if (!to || to === home(tid)) return null;
  let duty = 0; const sub = items.reduce((n, i) => n + i.unitBase * i.qty, 0) || 1;
  for (const i of items) { const r = rate(tid, to, code(tid, i.product.id)); if (r && net >= Number(r.threshold || 0)) duty += net * (i.unitBase * i.qty / sub) * r.percent / 100; }
  return duty;
}
module.exports = {
  check: r => { if (!/^[A-Za-z]{2}$/.test(r.country)) throw F().fail("Give the country's two-letter code"); },
  charges: ({ tid, net, items, body }) => { const d = due(tid, String((body || {}).country || "").toUpperCase(), items || [], net); return d > 0 ? [{ name: "Import duty", amount: d }] : []; },
  open: ({ tid }) => ({ home: home(tid), countries: [...new Set(F().rows(tid, "duties_at_checkout").map(r => r.country.toUpperCase()))] })
};
