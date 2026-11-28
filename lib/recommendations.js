/* LUXORA Platform — recommendations (owner Search & Discovery).

   Suggestions learned from what shoppers view and buy together (lib/seed/recommendations.json).
   Two products viewed in the same visit, or bought in the same order (or by the same customer within
   a few weeks), become a pair (rec_pairs) whose weight fades with time, so what sells together this
   season counts more than last year. How often each product is viewed or bought on its own
   (rec_items) scales a pair down, so a best-seller does not crowd out everything else. Pairs and
   counts hold no person: a shopper's history is read only to choose that shopper's picks.

   A product page gets what is bought together, what else was viewed and what is like it (the
   catalogue's own department, brand and price, for a product nobody has bought yet). The home page
   gets picks for the shopper, each with its reason, what they viewed recently and what is popular
   now; the cart gets what goes with it. The products viewed in this visit always shape the picks;
   a signed-in shopper's past orders shape them only with a live grant for the purpose (or, where the
   store sets basis optout, until the shopper withdraws it). Each shelf counts what it showed, what
   was clicked and what was then bought (rec_stats), and the store blocks or boosts products. View
   pairs are learnt as views happen; purchase pairs as orders are placed, and rebuilt in full by
   train on the sweep, which also forgets clicks past the attribution window. */
"use strict";

const db = () => require("./db.js");
const states = require("./states.js");
const SEED = require("./seed/recommendations.json");
const KIND = SEED.kinds, SLOTS = SEED.slots;
const N = Number;
const fail = (msg, status) => { const e = new Error(msg); e.status = status || 400; throw e; };
const str = (v, n) => String(v == null ? "" : v).trim().slice(0, n || 200);
const ph = xs => "(" + (xs.length ? xs.map(() => "?").join(",") : "NULL") + ")";
const at = ms => new Date(ms).toISOString().slice(0, 19).replace("T", " ");
const msOf = s => { const t = Date.parse(String(s || "").replace(" ", "T") + (String(s || "").length <= 19 ? "Z" : "")); return isFinite(t) ? t : 0; };
const DAY = 86400000;
const tx = fn => require("./kernel.js").internal.tx(fn);
const own = tid => { try { return require("./settings.js").get(N(tid), "recommendations") || {}; } catch (e) { return {}; } };
/* the store's values over the seed's, one level deep for the grouped ones */
function cfg(tid) {
  const o = own(tid), out = { ...SEED, ...o };
  for (const k of ["weights", "seedWeights", "minSupport", "shelves"]) out[k] = { ...SEED[k], ...(o[k] || {}) };
  out.block = Array.isArray(o.block) ? o.block : []; out.boost = Array.isArray(o.boost) ? o.boost : [];
  return out;
}
const tenantOf = owner => { const m = /^t(\d+):/.exec(String(owner || "")); return m ? N(m[1]) : 0; };
const fade = (w, when, now, c) => N(w) * Math.pow(0.5, Math.max(0, now - msOf(when)) / (c.halfLifeDays * DAY));

/* ============================== learning ============================== */
function bumpItem(tid, kind, pid, inc, now, c) {
  const r = db().get("SELECT weight, at FROM rec_items WHERE tenant_id=? AND kind=? AND product_id=?", tid, kind, pid);
  const w = (r ? fade(r.weight, r.at, now, c) : 0) + inc;
  db().run("INSERT INTO rec_items(tenant_id, kind, product_id, weight, at) VALUES(?,?,?,?,?) ON CONFLICT(tenant_id, kind, product_id) DO UPDATE SET weight=excluded.weight, at=excluded.at", tid, kind, pid, w, at(now));
}
function bumpPair(tid, kind, a, b, inc, now, c) {
  for (const [x, y] of [[a, b], [b, a]]) {
    const r = db().get("SELECT weight, n, at FROM rec_pairs WHERE tenant_id=? AND kind=? AND a=? AND b=?", tid, kind, x, y);
    const w = (r ? fade(r.weight, r.at, now, c) : 0) + inc;
    db().run("INSERT INTO rec_pairs(tenant_id, kind, a, b, weight, n, at) VALUES(?,?,?,?,?,?,?) ON CONFLICT(tenant_id, kind, a, b) DO UPDATE SET weight=excluded.weight, n=excluded.n, at=excluded.at", tid, kind, x, y, w, (r ? N(r.n) : 0) + 1, at(now));
  }
}
const published = (tid, ids) => ids.length ? new Set(db().all(`SELECT id FROM products WHERE tenant_id=? AND id IN ${ph(ids)} AND lifecycle='published' AND deleted_at IS NULL`, tid, ...ids).map(r => r.id)) : new Set();

/* a product page was opened: called before the view is written to view_history, so the products this
   owner opened within coViewWithinHours are the ones it pairs with. A product opened again inside the
   window is not counted twice, so reloading a page does not teach anything. */
function learnView(tid, owner, pid, nowMs) {
  tid = N(tid); pid = str(pid, 80);
  if (!pid || tenantOf(owner) !== tid) return { learnt: false };
  const c = cfg(tid), now = nowMs || Date.now(), since = now - c.coViewWithinHours * 3600000;
  const hist = db().all("SELECT product_id, seen_at FROM view_history WHERE owner=?", owner).filter(r => msOf(r.seen_at) >= since);
  if (hist.some(r => r.product_id === pid)) return { learnt: false };
  if (!published(tid, [pid]).size) return { learnt: false };
  const others = [...published(tid, hist.map(r => r.product_id).filter(x => x !== pid))];
  tx(() => {
    bumpItem(tid, KIND.view, pid, 1, now, c);
    for (const q of others) bumpPair(tid, KIND.view, pid, q, 1, now, c);
  });
  return { learnt: true, paired: others.length };
}
/* the distinct products of an order, at most maxLines of them */
const linesOf = (orderIds, c) => {
  const out = new Map();
  for (let i = 0; i < orderIds.length; i += 500) {
    const part = orderIds.slice(i, i + 500);
    for (const r of db().all(`SELECT order_id, product_id FROM order_items WHERE order_id IN ${ph(part)}`, ...part)) {
      const s = out.get(r.order_id) || new Set(); if (s.size < c.maxLines) s.add(r.product_id); out.set(r.order_id, s);
    }
  }
  return out;
};
/* an order was placed: its products pair at once, and a shelf click it came from is counted as bought */
function onEvent(tid, event, data) {
  if (event !== SEED.attributeOn) return null;
  tid = N(tid);
  const o = db().get("SELECT id, owner FROM orders WHERE tenant_id=? AND num=?", tid, str((data || {}).num, 80));
  if (!o) return null;
  const c = cfg(tid), now = Date.now();
  const lines = db().all("SELECT product_id, qty, price FROM order_items WHERE order_id=?", o.id);
  const ids = [...new Set(lines.map(l => l.product_id))].slice(0, c.maxLines);
  let attributed = 0;
  tx(() => {
    for (const p of ids) bumpItem(tid, KIND.buy, p, 1, now, c);
    for (let i = 0; i < ids.length; i++) for (let j = i + 1; j < ids.length; j++) bumpPair(tid, KIND.buy, ids[i], ids[j], 1, now, c);
    const clicks = db().all(`SELECT product_id, slot, at FROM rec_clicks WHERE tenant_id=? AND owner=? AND product_id IN ${ph(ids)}`, tid, o.owner, ...ids);
    for (const k of clicks) {
      if (msOf(k.at) < now - c.attributionDays * DAY || !SLOTS[k.slot]) continue;
      const rev = lines.filter(l => l.product_id === k.product_id).reduce((n, l) => n + N(l.price) * N(l.qty), 0);
      bump(tid, k.slot, { bought: 1, revenue: rev }, now); attributed++;
    }
    if (clicks.length) db().run(`DELETE FROM rec_clicks WHERE tenant_id=? AND owner=? AND product_id IN ${ph(ids)}`, tid, o.owner, ...ids);
  });
  return { paired: ids.length, attributed };
}

/* the purchase pairs rebuilt from the orders of the last windowDays: products in one order pair at
   full weight, products a customer bought in orders within basketDays of each other at
   crossOrderWeight; each order's weight fades with its age. Each product keeps its maxNeighbours
   strongest partners. View pairs older than the window are forgotten. */
function train(tid, nowMs) {
  tid = N(tid);
  const c = cfg(tid), now = nowMs || Date.now(), t0 = Date.now();
  const orders = db().all("SELECT id, owner, created_at FROM orders WHERE tenant_id=? AND created_at>=? ORDER BY id DESC LIMIT ?", tid, at(now - c.windowDays * DAY), c.maxOrders);
  const lines = linesOf(orders.map(o => o.id), c);
  const pairs = new Map(), items = new Map();
  const add = (a, b, w) => { if (a === b) return; for (const k of [a + "\u0001" + b, b + "\u0001" + a]) { const x = pairs.get(k) || [0, 0]; x[0] += w; x[1]++; pairs.set(k, x); } };
  const wOf = o => Math.pow(0.5, Math.max(0, now - msOf(o.created_at)) / (c.halfLifeDays * DAY));
  const byOwner = new Map();
  for (const o of orders) {
    const ids = [...(lines.get(o.id) || [])], w = wOf(o);
    for (const p of ids) items.set(p, (items.get(p) || 0) + w);
    for (let i = 0; i < ids.length; i++) for (let j = i + 1; j < ids.length; j++) add(ids[i], ids[j], w);
    const xs = byOwner.get(o.owner) || []; xs.push(o); byOwner.set(o.owner, xs);
  }
  for (const xs of byOwner.values()) {
    xs.sort((x, y) => msOf(x.created_at) - msOf(y.created_at));
    for (let i = 0; i < xs.length; i++) for (let j = i + 1; j < Math.min(xs.length, i + 10); j++) {
      if (msOf(xs[j].created_at) - msOf(xs[i].created_at) > c.basketDays * DAY) break;
      const w = Math.min(wOf(xs[i]), wOf(xs[j])) * c.crossOrderWeight;
      for (const a of lines.get(xs[i].id) || []) for (const b of lines.get(xs[j].id) || []) if (a !== b && !(lines.get(xs[i].id) || new Set()).has(b)) add(a, b, w);
    }
  }
  const byA = new Map();
  for (const [k, w] of pairs) { const [a, b] = k.split("\u0001"); const xs = byA.get(a) || []; xs.push([b, w[0], w[1]]); byA.set(a, xs); }
  let kept = 0;
  tx(() => {
    db().run("DELETE FROM rec_pairs WHERE tenant_id=? AND kind=?", tid, KIND.buy);
    db().run("DELETE FROM rec_items WHERE tenant_id=? AND kind=?", tid, KIND.buy);
    const when = at(now);
    for (const [a, xs] of byA) for (const [b, w, k] of xs.sort((x, y) => y[1] - x[1]).slice(0, c.maxNeighbours)) { db().run("INSERT INTO rec_pairs(tenant_id, kind, a, b, weight, n, at) VALUES(?,?,?,?,?,?,?)", tid, KIND.buy, a, b, w, k, when); kept++; }
    for (const [p, w] of items) db().run("INSERT INTO rec_items(tenant_id, kind, product_id, weight, at) VALUES(?,?,?,?,?)", tid, KIND.buy, p, w, when);
    const old = at(now - c.windowDays * DAY);
    db().run("DELETE FROM rec_pairs WHERE tenant_id=? AND kind=? AND at<?", tid, KIND.view, old);
    db().run("DELETE FROM rec_items WHERE tenant_id=? AND kind=? AND at<?", tid, KIND.view, old);
  });
  const run = { orders: orders.length, pairs: kept, products: byA.size, ms: Date.now() - t0 };
  db().run("INSERT INTO rec_runs(tenant_id, at, orders, pairs, products, ms) VALUES(?,?,?,?,?,?)", tid, at(now), run.orders, run.pairs, run.products, run.ms);
  return run;
}

/* ============================== scoring ============================== */
function popOf(tid, kind, ids, now, c) {
  const m = new Map();
  if (ids.length) for (const r of db().all(`SELECT product_id, weight, at FROM rec_items WHERE tenant_id=? AND kind=? AND product_id IN ${ph(ids)}`, tid, kind, ...ids)) m.set(r.product_id, fade(r.weight, r.at, now, c));
  return m;
}
/* the products learnt to go with `a`, each scored by its pair weight against how popular both are; a pair
   counts once it has been seen together minSupport times (its weight still fades) */
function partners(tid, a, now, c) {
  const out = new Map();
  for (const kind of [KIND.buy, KIND.view]) {
    const rows = db().all("SELECT b, weight, at FROM rec_pairs WHERE tenant_id=? AND kind=? AND a=? AND n>=? ORDER BY weight DESC LIMIT ?", tid, kind, a, c.minSupport[kind], c.maxListed)
      .map(r => ({ b: r.b, w: fade(r.weight, r.at, now, c) }));
    if (!rows.length) continue;
    const pop = popOf(tid, kind, [a, ...rows.map(r => r.b)], now, c), pa = pop.get(a) || 1;
    for (const r of rows) {
      const s = r.w / (Math.sqrt(pa * (pop.get(r.b) || 1)) + c.shrink);
      const x = out.get(r.b) || { score: 0, buy: 0, view: 0 };
      x.score += c.weights[kind] * s; x[kind] += s; out.set(r.b, x);
    }
  }
  return out;
}
const PCOLS = "id, title, brand, dept, node_id, type, price, rating, ratings_count, stock, emoji, hue, position";
/* the products a shelf may show, in stock, published and not blocked by the store */
function shelfRows(tid, ids, c, anyStock) {
  const xs = ids.filter(x => !c.block.includes(x));
  if (!xs.length) return new Map();
  return new Map(db().all(`SELECT * FROM products WHERE tenant_id=? AND id IN ${ph(xs)} AND lifecycle='published' AND deleted_at IS NULL${anyStock ? "" : " AND stock>0"}`, tid, ...xs).map(r => [r.id, r]));
}
/* a reason names the product by its name, without the long description after a dash */
const short = t => { const x = String(t || "").split(/\s+[—–-]\s+/)[0].trim(); return x.length > 60 ? x.slice(0, 57).trimEnd() + "…" : x; };
const why = (key, title) => SEED.reasons[key].replace("{title}", short(title));
/* the best `n` of scored candidates, at most perDept from one department, boosted ones lifted */
function pick(cands, rows, n, c) {
  const scored = [...cands].map(([id, x]) => ({ id, ...x, row: rows.get(id) })).filter(x => x.row)
    .map(x => ({ ...x, score: x.score * (c.boost.includes(x.id) ? c.weights.boost : 1) })).sort((a, b) => b.score - a.score);
  const per = new Map(), out = [];
  for (const x of scored) { const d = x.row.dept; if ((per.get(d) || 0) >= c.perDept) continue; per.set(d, (per.get(d) || 0) + 1); out.push(x); if (out.length >= n) break; }
  for (const x of scored) { if (out.length >= n) break; if (!out.includes(x)) out.push(x); }
  return out;
}
/* like a product by what the catalogue says: same category, department, brand and price */
function alike(tid, p, exclude, n, c) {
  const rows = db().all(`SELECT * FROM products WHERE tenant_id=? AND dept=? AND id<>? AND lifecycle='published' AND deleted_at IS NULL AND stock>0 ORDER BY ratings_count DESC LIMIT ?`, tid, p.dept, p.id, c.maxListed)
    .filter(r => !exclude.has(r.id) && !c.block.includes(r.id));
  const price = N(p.price) || 1;
  const m = new Map(rows.map(r => [r.id, { score: (r.node_id && r.node_id === p.node_id ? 3 : 1) + (r.brand && r.brand === p.brand ? 1.5 : 0) + Math.max(0, 1 - Math.abs(Math.log((N(r.price) || 1) / price)) / Math.log(3)) + N(r.rating || 0) / 10, why: why("like", p.title) }]));
  return pick(m, new Map(rows.map(r => [r.id, r])), n, c);
}
const slotOn = (c, slot) => !!c.shelves[slot];

/* a product page's shelves */
function forProduct(tid, pid, nowMs) {
  tid = N(tid);
  const c = cfg(tid), now = nowMs || Date.now();
  const p = db().get("SELECT * FROM products WHERE tenant_id=? AND id=? AND deleted_at IS NULL", tid, str(pid, 80));
  const out = { bought_together: [], also_viewed: [], similar: [] };
  if (!p) return out;
  const nb = partners(tid, p.id, now, c), rows = shelfRows(tid, [...nb.keys()], c);
  const used = new Set([p.id]);
  if (slotOn(c, "bought_together")) {
    const buy = new Map([...nb].filter(([, x]) => x.buy > 0).map(([id, x]) => [id, { score: x.buy, why: why("bought_with", p.title) }]));
    out.bought_together = pick(buy, rows, c.boughtTogether, c); out.bought_together.forEach(x => used.add(x.id));
  }
  if (slotOn(c, "also_viewed")) {
    const seen = new Map([...nb].filter(([id, x]) => x.view > 0 && !used.has(id)).map(([id, x]) => [id, { score: x.score, why: why("viewed_with", p.title) }]));
    out.also_viewed = pick(seen, rows, c.shelfSize, c); out.also_viewed.forEach(x => used.add(x.id));
  }
  if (slotOn(c, "similar")) out.similar = alike(tid, p, used, c.shelfSize, c);
  return out;
}

/* whether a shopper's past orders may shape their picks: the store's basis for the purpose. A grant is
   held under the shopper's account (the privacy choices) or their email (registration); with optout,
   a withdrawal under either stops it. */
const MAY = {
  consent: rows => rows.some(r => states.is("consent", r.status, "live")),
  optout: rows => rows.every(r => states.is("consent", r.status, "live"))
};
/* on which basis the shopper is asked for the grant (with optout they are in until they withdraw) */
const ASKS = { consent: true, optout: false };
const emailOf = (tid, owner) => { const m = /^t(\d+):u:(\d+)$/.exec(String(owner || "")); const u = m && N(m[1]) === tid ? db().get("SELECT email FROM users WHERE id=? AND tenant_id=?", N(m[2]), tid) : null; return u ? u.email : ""; };
function personal(tid, owner, c) {
  const email = emailOf(tid, owner);
  if (!email) return { email, on: false };
  const rows = db().all("SELECT status FROM consents WHERE tenant_id=? AND subject IN (?,?) AND purpose=?", tid, owner, email, SEED.purpose).filter(r => states.has("consent", r.status));
  return { email, on: (MAY[c.basis] || MAY.consent)(rows) };
}

/* what the shopper is looking at, has in the cart and (with leave) has bought: the seeds of their picks */
function seedsOf(tid, owner, now, c, withOrders) {
  const seeds = [], sw = c.seedWeights;
  db().all("SELECT product_id, seen_at FROM view_history WHERE owner=? ORDER BY seen_at DESC", owner).slice(0, 12)
    .forEach((r, i) => seeds.push({ id: r.product_id, w: sw.recent * Math.pow(sw.recentDecay, i), key: "viewed", recent: true }));
  db().all("SELECT product_id FROM cart_items WHERE owner=?", owner).forEach(r => seeds.push({ id: r.product_id, w: sw.cart, key: "cart" }));
  if (withOrders) db().all("SELECT oi.product_id, MAX(o.created_at) last FROM order_items oi JOIN orders o ON o.id=oi.order_id WHERE o.tenant_id=? AND o.owner=? AND o.created_at>=? GROUP BY oi.product_id ORDER BY last DESC LIMIT 20", tid, owner, at(now - c.windowDays * DAY))
    .forEach(r => seeds.push({ id: r.product_id, w: sw.bought * Math.pow(0.5, Math.max(0, now - msOf(r.last)) / (c.halfLifeDays * DAY)), key: "bought" }));
  return seeds;
}
/* what is popular now: views and purchases, faded by age */
function trending(tid, exclude, n, now, c) {
  const m = new Map();
  for (const kind of [KIND.buy, KIND.view]) for (const r of db().all("SELECT product_id, weight, at FROM rec_items WHERE tenant_id=? AND kind=? ORDER BY weight DESC LIMIT ?", tid, kind, c.maxListed)) {
    if (exclude.has(r.product_id)) continue;
    const x = m.get(r.product_id) || { score: 0, why: why("popular") }; x.score += c.weights[kind] * fade(r.weight, r.at, now, c); m.set(r.product_id, x);
  }
  if (m.size < n) for (const r of db().all("SELECT id, ratings_count FROM products WHERE tenant_id=? AND lifecycle='published' AND deleted_at IS NULL AND stock>0 ORDER BY ratings_count DESC LIMIT ?", tid, n * 3))
    if (!exclude.has(r.id) && !m.has(r.id)) m.set(r.id, { score: 1e-6 * N(r.ratings_count || 0), why: why("popular") });
  return pick(m, shelfRows(tid, [...m.keys()], c), n, c);
}

/* the home page's shelves for a shopper (by the owner key of their session) */
function forShopper(tid, owner, nowMs) {
  tid = N(tid);
  const c = cfg(tid), now = nowMs || Date.now();
  const me = tenantOf(owner) === tid ? personal(tid, owner, c) : { email: "", on: false };
  const seeds = tenantOf(owner) === tid ? seedsOf(tid, owner, now, c, me.on) : [];
  const seen = new Set(seeds.map(s => s.id));
  const titles = new Map(db().all(`SELECT id, title, dept FROM products WHERE tenant_id=? AND id IN ${ph([...seen])}`, tid, ...seen).map(r => [r.id, r]));
  const out = { for_you: [], recent: [], trending: [], personal: me.on, signedIn: !!me.email, basis: c.basis, purpose: SEED.purpose, ask: !!me.email && !me.on && !!ASKS[c.basis] };
  if (slotOn(c, "recent")) {
    const ids = seeds.filter(s => s.recent).map(s => s.id), rows = shelfRows(tid, ids, c, true);
    out.recent = ids.filter(id => rows.has(id)).map(id => ({ id, row: rows.get(id), score: 0, why: "" }));
  }
  if (slotOn(c, "for_you") && seeds.length) {
    const cands = new Map(), depts = new Map();
    for (const s of seeds) {
      const t = titles.get(s.id); if (t) depts.set(t.dept, (depts.get(t.dept) || 0) + s.w);
      for (const [id, x] of partners(tid, s.id, now, c)) {
        if (seen.has(id)) continue;
        const y = cands.get(id) || { score: 0, best: 0, why: "" }, part = s.w * x.score;
        y.score += part; if (part > y.best) { y.best = part; y.why = why(s.key, t ? t.title : ""); }
        cands.set(id, y);
      }
    }
    const rows = shelfRows(tid, [...cands.keys()], c), total = [...depts.values()].reduce((a, b) => a + b, 0) || 1;
    for (const [id, y] of cands) { const r = rows.get(id); if (r) y.score += c.weights.affinity * (depts.get(r.dept) || 0) / total; }
    out.for_you = pick(cands, rows, c.shelfSize, c);
    /* too little learnt yet: filled from what is popular in the departments the shopper looks at */
    if (out.for_you.length < c.shelfSize && depts.size) {
      const have = new Set([...seen, ...out.for_you.map(x => x.id)]);
      const top = [...depts].sort((a, b) => b[1] - a[1]).map(d => d[0]);
      const fill = trending(tid, have, c.shelfSize * 3, now, c).filter(x => top.includes(x.row.dept))
        .sort((a, b) => top.indexOf(a.row.dept) - top.indexOf(b.row.dept) || b.score - a.score);
      out.for_you = out.for_you.concat(fill.slice(0, c.shelfSize - out.for_you.length));
    }
  }
  if (slotOn(c, "trending")) out.trending = trending(tid, new Set([...seen, ...out.for_you.map(x => x.id)]), c.shelfSize, now, c);
  return out;
}
/* the cart's shelf: what is bought (then viewed) with what is in it */
function forCart(tid, owner, nowMs) {
  tid = N(tid);
  const c = cfg(tid), now = nowMs || Date.now();
  if (!slotOn(c, "goes_with") || tenantOf(owner) !== tid) return { goes_with: [] };
  const inCart = db().all("SELECT product_id FROM cart_items WHERE owner=?", owner).map(r => r.product_id), have = new Set(inCart);
  const titles = new Map(db().all(`SELECT id, title FROM products WHERE tenant_id=? AND id IN ${ph(inCart)}`, tid, ...inCart).map(r => [r.id, r.title]));
  const cands = new Map();
  for (const a of inCart) for (const [id, x] of partners(tid, a, now, c)) {
    if (have.has(id)) continue;
    const y = cands.get(id) || { score: 0, best: 0, why: "" }, part = x.buy * c.weights.buy + x.view * c.weights.view;
    y.score += part; if (part > y.best) { y.best = part; y.why = why(x.buy > 0 ? "bought_with" : "viewed_with", titles.get(a)); }
    cands.set(id, y);
  }
  let goes = pick(cands, shelfRows(tid, [...cands.keys()], c), c.shelfSize, c);
  if (goes.length < c.shelfSize) goes = goes.concat(trending(tid, new Set([...have, ...goes.map(x => x.id)]), c.shelfSize - goes.length, now, c));
  return { goes_with: goes };
}

/* ============================== measuring ============================== */
const dayOf = ms => at(ms).slice(0, 10);
function bump(tid, slot, d, nowMs) {
  const f = { shown: 0, clicked: 0, bought: 0, revenue: 0, ...d };
  db().run(`INSERT INTO rec_stats(tenant_id, day, slot, shown, clicked, bought, revenue) VALUES(?,?,?,?,?,?,?)
    ON CONFLICT(tenant_id, day, slot) DO UPDATE SET shown=rec_stats.shown+excluded.shown, clicked=rec_stats.clicked+excluded.clicked, bought=rec_stats.bought+excluded.bought, revenue=rec_stats.revenue+excluded.revenue`,
    N(tid), dayOf(nowMs || Date.now()), slot, f.shown, f.clicked, f.bought, f.revenue);
}
/* the storefront says what a page showed: { slot: how many } */
function shown(tid, counts) {
  let n = 0;
  for (const [slot, k] of Object.entries(counts || {})) { if (!SLOTS[slot]) continue; const v = Math.max(0, Math.min(SEED.maxShownPerCall, Math.floor(N(k) || 0))); if (v) { bump(tid, slot, { shown: v }); n += v; } }
  return { counted: n };
}
/* a shopper opened a product from a shelf: counted, and remembered for attributionDays so an order of it counts as bought */
function clicked(tid, owner, pid, slot, nowMs) {
  tid = N(tid);
  if (!SLOTS[slot] || tenantOf(owner) !== tid || !published(tid, [str(pid, 80)]).size) return { counted: false };
  const now = nowMs || Date.now();
  tx(() => {
    bump(tid, slot, { clicked: 1 }, now);
    db().run("INSERT INTO rec_clicks(tenant_id, owner, product_id, slot, at) VALUES(?,?,?,?,?) ON CONFLICT(tenant_id, owner, product_id) DO UPDATE SET slot=excluded.slot, at=excluded.at", tid, owner, str(pid, 80), slot, at(now));
  });
  return { counted: true };
}
/* a guest who signs in keeps the clicks of the visit */
function mergeOwner(from, to) {
  const t = tenantOf(to);
  for (const r of db().all("SELECT * FROM rec_clicks WHERE tenant_id=? AND owner=?", t, from))
    db().run("INSERT INTO rec_clicks(tenant_id, owner, product_id, slot, at) VALUES(?,?,?,?,?) ON CONFLICT(tenant_id, owner, product_id) DO UPDATE SET slot=excluded.slot, at=excluded.at", t, to, r.product_id, r.slot, r.at);
  db().run("DELETE FROM rec_clicks WHERE tenant_id=? AND owner=?", t, from);
}
function performance(tid, days) {
  const since = dayOf(Date.now() - (N(days) || 30) * DAY);
  const rows = db().all("SELECT slot, SUM(shown) shown, SUM(clicked) clicked, SUM(bought) bought, SUM(revenue) revenue FROM rec_stats WHERE tenant_id=? AND day>=? GROUP BY slot", N(tid), since);
  const by = new Map(rows.map(r => [r.slot, r]));
  return Object.entries(SLOTS).map(([slot, s]) => {
    const r = by.get(slot) || {}, sh = N(r.shown || 0), cl = N(r.clicked || 0), bo = N(r.bought || 0);
    return { slot, label: s.label, page: s.page, shown: sh, clicked: cl, bought: bo, revenue: Math.round(N(r.revenue || 0) * 100) / 100,
      clickRate: sh ? Math.round(cl / sh * 1000) / 10 : null, buyRate: cl ? Math.round(bo / cl * 1000) / 10 : null };
  });
}

/* ============================== the store's view ============================== */
function overview(tid) {
  tid = N(tid);
  const c = cfg(tid);
  const count = kind => N(db().get("SELECT COUNT(*) n FROM rec_pairs WHERE tenant_id=? AND kind=?", tid, kind).n);
  const covered = N(db().get("SELECT COUNT(*) n FROM (SELECT a FROM rec_pairs WHERE tenant_id=? GROUP BY a) x", tid).n);
  const titles = ids => new Map(ids.length ? db().all(`SELECT id, title FROM products WHERE tenant_id=? AND id IN ${ph(ids)}`, tid, ...ids).map(r => [r.id, r.title]) : []);
  const tb = titles([...c.block, ...c.boost]);
  return {
    model: { pairs: { buy: count(KIND.buy), view: count(KIND.view) }, products: covered,
      runs: db().all("SELECT at, orders, pairs, products, ms FROM rec_runs WHERE tenant_id=? ORDER BY id DESC LIMIT 5", tid) },
    performance: performance(tid, 30),
    settings: { basis: c.basis, halfLifeDays: c.halfLifeDays, perDept: c.perDept, shelfSize: c.shelfSize, attributionDays: c.attributionDays, shelves: c.shelves,
      block: c.block.map(id => ({ id, title: tb.get(id) || id })), boost: c.boost.map(id => ({ id, title: tb.get(id) || id })) },
    slots: SLOTS, bases: SEED.bases, purpose: SEED.purpose
  };
}
const within = (v, lo, hi, what) => { const n = Math.floor(N(v)); if (!(n >= lo && n <= hi)) fail(`${what} is ${lo} to ${hi}`); return n; };
function saveSettings(tid, input) {
  tid = N(tid);
  const i = input || {}, o = { ...own(tid) };
  if (i.basis !== undefined) o.basis = SEED.bases.includes(i.basis) ? i.basis : fail("The basis is one of " + SEED.bases.join(", "));
  if (i.halfLifeDays !== undefined) o.halfLifeDays = within(i.halfLifeDays, 1, 3650, "How long a signal lasts (days)");
  if (i.perDept !== undefined) o.perDept = within(i.perDept, 1, 24, "The most from one department");
  if (i.shelfSize !== undefined) o.shelfSize = within(i.shelfSize, 4, 24, "A shelf's size");
  if (i.attributionDays !== undefined) o.attributionDays = within(i.attributionDays, 1, 30, "Days a click counts toward an order");
  if (i.shelves !== undefined) { const sh = {}; for (const k of Object.keys(SLOTS)) if (i.shelves[k] !== undefined) sh[k] = !!i.shelves[k]; o.shelves = { ...(o.shelves || {}), ...sh }; }
  for (const k of ["block", "boost"]) if (i[k] !== undefined) {
    const ids = [...new Set((Array.isArray(i[k]) ? i[k] : fail("Send " + k + " as a list")).map(x => str(x, 80)).filter(Boolean))].slice(0, SEED.maxListed);
    const known = ids.length ? new Set(db().all(`SELECT id FROM products WHERE tenant_id=? AND id IN ${ph(ids)}`, tid, ...ids).map(r => r.id)) : new Set();
    const bad = ids.filter(x => !known.has(x)); if (bad.length) fail("No such product: " + bad.slice(0, 3).join(", "));
    o[k] = ids;
  }
  if (o.block && o.boost && o.block.some(x => o.boost.includes(x))) fail("A product cannot be both blocked and boosted");
  require("./settings.js").save(tid, { recommendations: o });
  return overview(tid);
}
/* what a customer (by email) or a product page would be shown now, with each pick's score and reason */
function preview(tid, input) {
  tid = N(tid);
  const i = input || {}, out = {};
  const view = xs => xs.map(x => ({ id: x.id, title: x.row.title, dept: x.row.dept, score: Math.round(x.score * 10000) / 10000, why: x.why }));
  if (i.email) {
    const u = db().get("SELECT id FROM users WHERE tenant_id=? AND lower(email)=lower(?)", tid, str(i.email, 200)) || fail("No customer with that email", 404);
    const r = forShopper(tid, `t${tid}:u:${u.id}`);
    out.shopper = { personal: r.personal, for_you: view(r.for_you), recent: view(r.recent), trending: view(r.trending), goes_with: view(forCart(tid, `t${tid}:u:${u.id}`).goes_with) };
  }
  if (i.product) {
    const r = forProduct(tid, i.product);
    out.product = { bought_together: view(r.bought_together), also_viewed: view(r.also_viewed), similar: view(r.similar) };
  }
  if (!i.email && !i.product) fail("Give a customer's email or a product");
  return out;
}

/* ============================== the sweep ============================== */
function sweep(tid, nowMs) {
  tid = N(tid);
  const c = cfg(tid), now = nowMs || Date.now();
  const last = db().get("SELECT at FROM rec_runs WHERE tenant_id=? ORDER BY id DESC LIMIT 1", tid);
  const run = !last || now - msOf(last.at) >= c.trainEveryHours * 3600000 ? train(tid, now) : null;
  const gone = db().run("DELETE FROM rec_clicks WHERE tenant_id=? AND at<?", tid, at(now - c.attributionDays * DAY)).changes;
  db().run("DELETE FROM rec_stats WHERE tenant_id=? AND day<?", tid, dayOf(now - 400 * DAY));
  return { trained: run, forgot: gone };
}
function sweepAll() {
  let n = 0;
  for (const r of db().all("SELECT DISTINCT tenant_id FROM orders UNION SELECT DISTINCT tenant_id FROM rec_items")) { try { if (sweep(r.tenant_id).trained) n++; } catch (e) { console.error("recommendations sweep:", e.message); } }
  return n;
}

module.exports = { learnView, onEvent, train, forProduct, forShopper, forCart, shown, clicked, mergeOwner, performance, overview, saveSettings, preview, sweep, sweepAll, cfg, SEED };
