/* LUXORA Platform — deliverables: what an order hands the shopper beyond the goods.

   Each kind is its own feature: a deliverableKinds registry row names the capability that switches
   it on (whose params are the kind's settings — `fact`, the item fact that makes an item deliver
   it), the section and screen it is run from, and what it does:
     pooled      taken from the store's pool for the item at once; staff are told below `low_stock`
                 (licence keys)
     uploaded    awaited until staff upload it, late after `due_days` (lab reports)
     access      a grant of access, opened at `access_url`, whose steps — the item fact `steps_fact`
                 — the shopper counts (a course and its lessons)
   One deliverable per unit ordered. Its life is the `deliverable` state machine (awaited →
   delivered, or revoked). This module is the shared machinery; every kind is switched on, set up
   and shown on its own. */
"use strict";

const db = () => require("./db.js");
const caps = () => require("./capabilities.js");
const reg = () => require("./parity-registries.js");
const states = require("./states.js");
const lineterms = require("./lineterms.js");
const fail = lineterms.fail;
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };
const rows = name => reg().list(name).map(x => (typeof x === "string" ? { key: x, name: x } : x)).filter(x => x && x.key);
const kindOf = key => rows("deliverableKinds").find(r => r.key === String(key == null ? "" : key)) || null;
const sqlIn = days => new Date(Date.now() + Number(days) * 86400000).toISOString().slice(0, 19).replace("T", " ");
const sqlNow = () => new Date().toISOString().slice(0, 19).replace("T", " ");
const tell = (...a) => require("./tell.js").tell(...a);

/* the kinds a store has switched on */
const kindsOn = tid => rows("deliverableKinds").filter(k => caps().on(Number(tid), k.atom));
function kindOn(tid, key) {
  const k = kindOf(key);
  if (!k || !caps().on(Number(tid), k.atom)) throw fail("That is not available in this store", 403);
  return k;
}
const settings = (tid, k) => caps().cap(Number(tid), k.atom);
const factsOf = (tid, productId) => J((db().get("SELECT attrs FROM products WHERE tenant_id=? AND id=?", Number(tid), String(productId)) || {}).attrs, {});
/* the kind an item delivers: the first switched-on kind whose fact the item's facts hold */
const kindForProduct = (tid, productId) => {
  const ks = kindsOn(tid);
  if (!ks.length) return null;
  const facts = factsOf(tid, productId);
  return ks.find(k => facts[settings(tid, k).fact]) || null;
};
function present(d) {
  const k = kindOf(d.kind) || {};
  const P = k.atom ? settings(d.tenant_id, k) : {};
  const late = !!(k.uploaded && !d.delivered_at && Number(P.due_days) > 0 && d.created_at < new Date(Date.now() - Number(P.due_days) * 86400000).toISOString().slice(0, 19).replace("T", " "));
  return { ...d, kind_row: k, late, state: states.display("deliverable", d.status), delivered: states.is("deliverable", d.status, "delivered"),
    /* what it holds shows once delivered, and only to its owner (the caller decides who sees it) */
    value: states.is("deliverable", d.status, "delivered") ? d.value : null };
}
function write(d, action, patch) {
  const to = states.actionTarget("deliverable", action);
  if (!to || !states.can("deliverable", d.status, to)) throw fail("That cannot be done to this deliverable now", 409);
  const mv = states.apply("deliverable", { tenantId: d.tenant_id, from: d.status, to, row: d });
  const p = { ...mv.patch, ...(patch || {}) };
  const cols = Object.keys(p);
  db().run("UPDATE deliverables SET " + cols.map(c => c + "=?").join(", ") + " WHERE id=?", ...cols.map(c => p[c]), d.id);
  return db().get("SELECT * FROM deliverables WHERE id=?", d.id);
}

/* ---------- the store's pool (pooled kinds) ---------- */
function stock(tid, kind, productId, codes) {
  const k = kindOn(tid, kind);
  if (!k.pooled) throw fail("A " + k.name.toLowerCase() + " is not delivered from a pool");
  if ((kindForProduct(tid, productId) || {}).key !== k.key) throw fail("This item does not deliver a " + k.name.toLowerCase());
  let n = 0;
  for (const c of (Array.isArray(codes) ? codes : String(codes || "").split(/\s+/)).map(x => String(x).trim()).filter(Boolean))
    n += db().run("INSERT OR IGNORE INTO deliverable_pool(tenant_id,product_id,code) VALUES(?,?,?)", Number(tid), String(productId), c.slice(0, 500)).changes;
  return { added: n, left: left(tid, productId) };
}
const left = (tid, productId) => db().get("SELECT COUNT(*) n FROM deliverable_pool WHERE tenant_id=? AND product_id=? AND taken_by IS NULL", Number(tid), String(productId)).n;

/* ---------- an order hands over its deliverables ---------- */
lineterms.onOrder((ctx, items) => {
  for (const it of items) {
    const k = kindForProduct(ctx.tid, it.product.id);
    if (!k) continue;
    for (let i = 0; i < (Number(it.qty) || 1); i++) {
      /* an access kind counts the steps the item's facts declare (a course's lessons) */
      const P = settings(ctx.tid, k);
      const r = db().run("INSERT INTO deliverables(tenant_id,order_id,product_id,owner,kind,status,steps_total) VALUES(?,?,?,?,?,?,?)",
        Number(ctx.tid), Number(ctx.orderId), it.product.id, String(ctx.owner || ""), k.key, states.initial("deliverable"), k.access ? Number(factsOf(ctx.tid, it.product.id)[P.steps_fact]) || 0 : 0);
      const d = db().get("SELECT * FROM deliverables WHERE id=?", r.lastInsertRowid);
      /* a pooled kind is delivered at once from the pool; an access kind at once as a grant */
      if (k.pooled) {
        const code = db().get("SELECT id, code FROM deliverable_pool WHERE tenant_id=? AND product_id=? AND taken_by IS NULL ORDER BY id LIMIT 1", Number(ctx.tid), it.product.id);
        if (code) {
          db().run("UPDATE deliverable_pool SET taken_by=? WHERE id=?", d.id, code.id); write(d, "deliver", { value: code.code, delivered_at: sqlNow() });
          const n = left(ctx.tid, it.product.id);
          if (n < Number(P.low_stock)) tell(ctx.tid, "", "deliverable", "A pool is running low", n + " " + k.name.toLowerCase() + "s left for " + it.product.id, "admin.html#" + k.section);
        } else tell(ctx.tid, "", "deliverable", "A pool ran out", "Order " + ctx.orderNum + " is waiting for a " + k.name.toLowerCase() + " for " + it.product.id, "admin.html#" + k.section);
      } else if (k.access) write(d, "deliver", { value: String(P.access_url || "").replace("{id}", d.id), delivered_at: sqlNow() });
    }
  }
});
/* staff hand over what a kind awaits: the report an uploaded kind waits for, or a code for a pooled
   kind whose pool ran out */
function upload(tid, id, value, actor) {
  const d = db().get("SELECT * FROM deliverables WHERE tenant_id=? AND id=?", Number(tid), Number(id));
  if (!d) throw fail("Deliverable not found", 404);
  const k = kindOn(tid, d.kind);
  if (k.access) throw fail("A " + k.name.toLowerCase() + " is granted, not uploaded");
  const v = String(value || "").trim();
  if (!v) throw fail("Give what is delivered");
  if (k.uploaded && !/^https?:\/\//i.test(v)) throw fail("Give a link to the file");
  const out = write(d, "deliver", { value: v.slice(0, 2000), delivered_at: sqlNow(), delivered_by: String(actor || "") });
  tell(tid, d.owner, "deliverable", "Your " + ((kindOf(d.kind) || {}).name || "item").toLowerCase() + " is ready", "", "account.html");
  return present(out);
}
/* the shopper records a step done on an access deliverable (a lesson finished) */
function step(tid, owner, id) {
  const d = db().get("SELECT * FROM deliverables WHERE tenant_id=? AND id=? AND owner=?", Number(tid), Number(id), String(owner));
  if (!d || !states.is("deliverable", d.status, "delivered")) throw fail("Deliverable not found", 404);
  if (!(d.steps_total > 0)) throw fail("This has no steps to count");
  db().run("UPDATE deliverables SET steps_done=MIN(steps_total, steps_done+1) WHERE id=?", d.id);
  return present(db().get("SELECT * FROM deliverables WHERE id=?", d.id));
}

/* one kind's deliverables, for its own screen */
function forStaff(tid, kind) {
  const k = kindOn(tid, kind);
  return { kind: k, settings: settings(tid, k), deliverables: db().all("SELECT * FROM deliverables WHERE tenant_id=? AND kind=? ORDER BY id DESC LIMIT 300", Number(tid), k.key).map(present),
    pools: k.pooled ? pools(tid, k) : [] };
}
/* what the shopper's orders delivered, of the kinds the store has on */
function mine(tid, owner) {
  const ks = kindsOn(tid).map(k => k.key);
  if (!ks.length) return [];
  return db().all(`SELECT * FROM deliverables WHERE tenant_id=? AND owner=? AND kind IN (${ks.map(() => "?").join(",")}) ORDER BY id DESC LIMIT 200`, Number(tid), String(owner), ...ks).map(present);
}
/* how many codes each item of a pooled kind has left */
function pools(tid, k) {
  return db().all("SELECT product_id, SUM(taken_by IS NULL) n, COUNT(*) total FROM deliverable_pool WHERE tenant_id=? GROUP BY product_id", Number(tid))
    .filter(r => (kindForProduct(tid, r.product_id) || {}).key === k.key);
}
function kinds() { return rows("deliverableKinds").map(k => ({ key: k.key, name: k.name, atom: k.atom, section: k.section, screen: k.screen, pooled: !!k.pooled, uploaded: !!k.uploaded, access: !!k.access })); }

/* the section a staff route belongs to: the named kind's, or the kind of the deliverable named */
function sectionOf(key, id) {
  const k = kindOf(key) || kindOf((db().get("SELECT kind FROM deliverables WHERE id=?", Number(id)) || {}).kind);
  return k ? k.section : undefined;
}

module.exports = { kinds, stock, left, upload, step, mine, forStaff, sectionOf };
