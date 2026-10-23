/* LUXORA Platform — Price & stock alerts.
   A signed-in shopper watches a product and is told when something they care about happens
   to it. What can happen is the engine's own small vocabulary of TRIGGERS (a price below the
   price they watched at, a price at or below a target, stock coming back); which triggers
   exist as alerts a shopper can choose, what each is called, when it may be set and what its
   message says are alertKinds registry rows — so "tell me when it is 30% off" is a row naming
   a trigger, not code. The thresholds (how big a drop counts, how often one watch may fire)
   are the product_alerts capability's params.

   Watches are checked whenever the catalogue changes (search.onCatalogChange) and on a
   timer (server.js), so a price an operator edits or an import rewrites both alert. Each
   watch is a state machine (product_watch): it is ASKED what a state means, never named. */
"use strict";

const db = () => require("./db.js");
const caps = () => require("./capabilities.js");
const reg = () => require("./parity-registries.js");
const states = require("./states.js");
const fail = (msg, status) => Object.assign(new Error(msg), { status: status || 400 });

const rows = name => reg().list(name).map(x => (typeof x === "string" ? { key: x, name: x } : x)).filter(x => x && x.key);
const kindOf = key => rows("alertKinds").find(r => r.key === String(key == null ? "" : key)) || null;
const inTag = tag => { const xs = states.tagged("product_watch", tag); return { sql: "(" + (xs.length ? xs.map(() => "?").join(",") : "NULL") + ")", args: xs }; };

/* the engine's vocabulary: what a trigger tests, and how a watch re-bases once it fired.
   A kind names one of these; an unknown trigger never fires (and is reported by kinds()). */
const TRIGGERS = {
  price_below_baseline: {
    fires: (p, w, P) => Number(w.baseline_price) > 0 && Number(p.price) <= Number(w.baseline_price) * (1 - (Number(P.min_drop_pct) || 0) / 100),
    rebase: p => ({ baseline_price: Number(p.price) })
  },
  price_at_or_below_target: {
    fires: (p, w) => Number(w.target_price) > 0 && Number(p.price) <= Number(w.target_price),
    rebase: () => ({})
  },
  stock_restored: {
    fires: (p, w) => Number(w.baseline_stock) <= 0 && Number(p.stock) > 0,
    rebase: p => ({ baseline_stock: Number(p.stock) })
  }
};
/* when a kind may be set, by what the product is now */
const WATCHABLE = { any: () => true, out_of_stock: p => Number(p.stock) <= 0, in_stock: p => Number(p.stock) > 0 };

function params(tid) {
  const P = caps().cap(tid, "product_alerts");
  if (!Object.keys(P).length) throw fail("Alerts are not available in this store", 403);
  return P;
}
const product = (tid, id) => db().get("SELECT * FROM products WHERE tenant_id=? AND id=? AND lifecycle='published' AND deleted_at IS NULL", Number(tid), String(id || ""));

/* amounts are stored in the store's base currency; a message shows them as the store does */
function money(tid, n) {
  try {
    const registry = require("./registry.js");
    const c = require("./settings.js").load(Number(tid)).commerce || {};
    const co = registry.country(c.country) || {};
    const base = co.currency, cur = (c.currency && registry.currency(c.currency)) ? c.currency : base;
    const fx = !base || cur === base ? 1 : registry.fxTo(base, cur);
    const curRow = registry.currency(cur) || {};
    const dec = curRow.decimals != null ? Number(curRow.decimals) : 2;
    return (Number(n) * fx).toFixed(dec) + (cur ? " " + cur : "");
  } catch (e) { return String(n); }
}
const fill = (tpl, vars) => String(tpl || "").replace(/\{(\w+)\}/g, (m, k) => (vars[k] != null ? String(vars[k]) : m));

/* the kinds a shopper can choose for this product right now (with why not, for the others) */
function kinds(tid, productId) {
  params(tid);
  const p = productId ? product(tid, productId) : null;
  return rows("alertKinds").map(k => {
    const known = !!TRIGGERS[k.trigger];
    const when = WATCHABLE[k.watchable] || WATCHABLE.any;
    return { ...k, available: known && (!p || when(p)) };
  });
}

function watch(tid, owner, input) {
  const P = params(tid);
  const i = input || {};
  const p = product(tid, i.product_id);
  if (!p) throw fail("That product is not available", 404);
  const k = kindOf(i.kind);
  if (!k || !TRIGGERS[k.trigger]) throw fail("Unknown kind of alert");
  if (!(WATCHABLE[k.watchable] || WATCHABLE.any)(p)) throw fail(k.name + " cannot be set on this product right now");
  const target = Number(i.target_price);
  if (k.needs_target && !(target > 0)) throw fail("Enter the price you want to be told about");
  const D = db();
  const live = inTag("watching");
  const ex = D.get("SELECT * FROM product_watches WHERE tenant_id=? AND owner=? AND product_id=? AND kind=? AND status IN " + live.sql,
    Number(tid), String(owner), p.id, k.key, ...live.args);
  if (ex) {
    D.run("UPDATE product_watches SET target_price=?, baseline_price=?, baseline_stock=? WHERE id=?", k.needs_target ? target : null, Number(p.price), Number(p.stock), ex.id);
    return one(tid, owner, ex.id);
  }
  const n = D.get("SELECT COUNT(*) c FROM product_watches WHERE tenant_id=? AND owner=? AND status IN " + live.sql, Number(tid), String(owner), ...live.args).c;
  if (n >= Number(P.max_watches)) throw fail("You can keep up to " + P.max_watches + " alerts");
  const r = D.run("INSERT INTO product_watches(tenant_id,owner,product_id,kind,target_price,baseline_price,baseline_stock,status) VALUES(?,?,?,?,?,?,?,?)",
    Number(tid), String(owner), p.id, k.key, k.needs_target ? target : null, Number(p.price), Number(p.stock), states.initial("product_watch"));
  return one(tid, owner, r.lastInsertRowid);
}
function one(tid, owner, id) {
  const w = db().get("SELECT * FROM product_watches WHERE id=? AND tenant_id=? AND owner=?", Number(id), Number(tid), String(owner));
  if (!w) throw fail("Alert not found", 404);
  return present(w);
}
function present(w) {
  const p = product(w.tenant_id, w.product_id);
  return { ...w, kind_row: kindOf(w.kind), state: states.display("product_watch", w.status), watching: states.is("product_watch", w.status, "watching"),
    product: p ? { id: p.id, title: p.title, price: p.price, stock: p.stock, emoji: p.emoji, hue: p.hue } : null };
}
function mine(tid, owner) {
  params(tid);
  return db().all("SELECT * FROM product_watches WHERE tenant_id=? AND owner=? ORDER BY id DESC LIMIT 200", Number(tid), String(owner)).map(present);
}
/* the owner's live watches on one product (the product page's "you're watching this") */
function watching(tid, owner, productId) {
  if (!caps().on(tid, "product_alerts")) return [];
  const live = inTag("watching");
  return db().all("SELECT id, kind, target_price FROM product_watches WHERE tenant_id=? AND owner=? AND product_id=? AND status IN " + live.sql,
    Number(tid), String(owner), String(productId), ...live.args);
}
function cancel(tid, owner, id) {
  params(tid);
  const w = db().get("SELECT * FROM product_watches WHERE id=? AND tenant_id=? AND owner=?", Number(id), Number(tid), String(owner));
  if (!w) throw fail("Alert not found", 404);
  const to = states.actionTarget("product_watch", "cancel");
  const mv = states.apply("product_watch", { tenantId: tid, from: w.status, to, row: w });
  write(w.id, mv.patch);
  return one(tid, owner, w.id);
}
function write(id, patch) {
  const cols = Object.keys(patch);
  if (cols.length) db().run("UPDATE product_watches SET " + cols.map(c => c + "=?").join(", ") + " WHERE id=?", ...cols.map(c => patch[c]), id);
}

/* ---------- checking ---------- */
/* every live watch on this tenant's products (or the listed ones) is tested; a watch that
   fires tells its owner (in-app, and by email when the store says so), then either keeps
   watching from the new price (rearm) or moves to the state tagged fired */
function check(tid, productIds) {
  if (!caps().on(Number(tid), "product_alerts", { buyer: false })) return { checked: 0, fired: 0 };
  const P = caps().cap(Number(tid), "product_alerts");
  const D = db();
  const live = inTag("watching");
  const only = Array.isArray(productIds) && productIds.length ? " AND w.product_id IN (" + productIds.map(() => "?").join(",") + ")" : "";
  const ws = D.all("SELECT w.* FROM product_watches w WHERE w.tenant_id=? AND w.status IN " + live.sql + only,
    Number(tid), ...live.args, ...(only ? productIds.map(String) : []));
  const coolMs = Math.max(0, Number(P.cooldown_hours) || 0) * 3600e3;
  let fired = 0;
  for (const w of ws) {
    const k = kindOf(w.kind);
    const tr = k && TRIGGERS[k.trigger];
    const p = product(tid, w.product_id);
    if (!tr || !p) continue;
    /* a stock watch whose product sold out again starts waiting for it to come back */
    if (Number(p.stock) <= 0 && Number(w.baseline_stock) > 0) D.run("UPDATE product_watches SET baseline_stock=0 WHERE id=?", w.id), w.baseline_stock = 0;
    if (!tr.fires(p, w, P)) continue;
    if (w.fired_at && coolMs && Date.now() - new Date(String(w.fired_at).replace(" ", "T") + "Z").getTime() < coolMs) continue;
    notify(tid, w, k, p, P);
    fired++;
    const now = new Date().toISOString().slice(0, 19).replace("T", " ");
    if (P.rearm) write(w.id, Object.assign({ fired_at: now, fired_price: Number(p.price), fires: (w.fires || 0) + 1 }, tr.rebase(p)));
    else {
      const mv = states.apply("product_watch", { tenantId: tid, from: w.status, to: states.first("product_watch", "fired"), row: w });
      write(w.id, Object.assign({}, mv.patch, { fired_price: Number(p.price), fires: (w.fires || 0) + 1 }));
    }
  }
  return { checked: ws.length, fired };
}
function notify(tid, w, k, p, P) {
  const D = db();
  const vars = { title: p.title, price: money(tid, p.price), was: money(tid, w.baseline_price), target: w.target_price != null ? money(tid, w.target_price) : "" };
  const title = fill(k.title || k.name, vars).slice(0, 200), body = fill(k.body || "", vars).slice(0, 1000);
  /* the notification kind is the one the alert kind's row names */
  require("./tell.js").tell(tid, w.owner, k.notification_kind, title, body, "product.html?id=" + encodeURIComponent(p.id), { email: !!P.email, meta: { watch: w.id, product: p.id } });
}
/* the timer's pass: every tenant that has live watches */
function sweepAll() {
  const live = inTag("watching");
  let fired = 0;
  for (const t of db().all("SELECT DISTINCT tenant_id FROM product_watches WHERE status IN " + live.sql, ...live.args)) {
    try { fired += check(t.tenant_id).fired; } catch (e) { console.error("alerts sweep (tenant " + t.tenant_id + "):", e.message); }
  }
  return { fired };
}
/* the console's view: how many shoppers watch what */
function summary(tid) {
  const live = inTag("watching");
  return db().all("SELECT w.product_id, w.kind, COUNT(*) watchers, p.title FROM product_watches w LEFT JOIN products p ON p.tenant_id=w.tenant_id AND p.id=w.product_id WHERE w.tenant_id=? AND w.status IN " + live.sql + " GROUP BY w.product_id, w.kind, p.title ORDER BY watchers DESC LIMIT 50",
    Number(tid), ...live.args);
}

module.exports = { TRIGGERS, kinds, watch, mine, watching, cancel, check, sweepAll, summary };
