/* LUXORA Platform — Product options: modifiers, add-ons and personalisation.
   An option group (a size, a crust, extra toppings, an engraving) is defined once and attached
   to any number of products. A group either offers values to choose from — each with its own
   price change — or takes the shopper's own text; what a kind of group does is its optionKinds
   registry row (`takes_text`). How many values a shopper must or may choose are the group's
   min and max. The shopper's choice rides on the bag line as its `options` term
   (lib/lineterms.js), adds its price changes to the line, and is kept on the order line, so a
   meal, a made-to-order item or a personalised gift is one product with options — not a
   product per combination. What a kind of group does with an order is its row too: a service
   done for the item (installation, assembly) leaves a visit to schedule, a plan (a warranty, a
   protection plan) runs for the months its value declares, the shopper's own artwork is proofed
   before making (`follow_up`); a sample sets the line's price and limits how many a bag holds
   (`sets_price`, `limits_qty`). Each follow-up is the `option_follow_up` state machine.
   Capability: product_options. */
"use strict";

const db = () => require("./db.js");
const caps = () => require("./capabilities.js");
const reg = () => require("./parity-registries.js");
const lineterms = require("./lineterms.js");
const states = require("./states.js");
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };
const fail = lineterms.fail;

const rows = name => reg().list(name).map(x => (typeof x === "string" ? { key: x, name: x } : x)).filter(x => x && x.key);
const kindOf = key => rows("optionKinds").find(r => r.key === String(key == null ? "" : key)) || null;
const CODE_RE = /^[a-z0-9][a-z0-9_-]{0,39}$/;
const num = (v, d) => (v === "" || v == null || !isFinite(Number(v)) ? d : Number(v));

function params(tid) {
  const P = caps().cap(tid, "product_options");
  if (!Object.keys(P).length) throw fail("Product options are not available in this store", 403);
  return P;
}

/* ---------- groups and their values ---------- */
function present(g) {
  const values = db().all("SELECT * FROM option_values WHERE group_id=? ORDER BY position, id", g.id).map(v => ({ ...v, extra: J(v.extra, {}) }));
  return { ...g, kind_row: kindOf(g.kind), values };
}
function groups(tid) { return db().all("SELECT * FROM option_groups WHERE tenant_id=? ORDER BY position, name", Number(tid)).map(present); }
function saveGroup(tid, input) {
  const P = params(tid);
  const i = input || {};
  const D = db();
  const code = String(i.code || "").trim().toLowerCase();
  if (!CODE_RE.test(code)) throw fail("A group needs a short code: lowercase letters, digits, - or _");
  const name = String(i.name || "").trim().slice(0, 80);
  if (!name) throw fail("A group needs a name");
  const kind = kindOf(i.kind) || rows("optionKinds").find(r => r.default) || rows("optionKinds")[0];
  if (!kind) throw fail("No kinds of option group are configured");
  const minSel = Math.max(0, Math.floor(num(i.min_select, 0)));
  const maxSel = Math.max(minSel || 1, Math.floor(num(i.max_select, 1)));
  const maxLen = Math.max(1, Math.min(500, Math.floor(num(i.max_length, P.max_text_length))));
  const clash = D.get("SELECT id FROM option_groups WHERE tenant_id=? AND code=?", Number(tid), code);
  let id = Number(i.id) || null;
  if (id && !D.get("SELECT id FROM option_groups WHERE id=? AND tenant_id=?", id, Number(tid))) throw fail("Option group not found", 404);
  if (clash && clash.id !== id) throw fail("Another group already uses the code " + code, 409);
  const vals = [name, kind.key, minSel, maxSel, maxLen, Math.floor(num(i.position, 0)), i.active === false || i.active === 0 ? 0 : 1];
  if (id) D.run("UPDATE option_groups SET code=?, name=?, kind=?, min_select=?, max_select=?, max_length=?, position=?, active=? WHERE id=?", code, ...vals, id);
  else id = Number(D.run("INSERT INTO option_groups(tenant_id,code,name,kind,min_select,max_select,max_length,position,active) VALUES(?,?,?,?,?,?,?,?,?)", Number(tid), code, ...vals).lastInsertRowid);
  /* values are upserted by code; a value left out is switched off (orders that chose it keep its name) */
  if (Array.isArray(i.values) && !kind.takes_text) {
    const seen = new Set();
    i.values.forEach((v, pos) => {
      const vc = String(v.code || "").trim().toLowerCase();
      if (!CODE_RE.test(vc)) throw fail("Each value needs a short code: lowercase letters, digits, - or _");
      if (seen.has(vc)) throw fail("Two values use the code " + vc);
      seen.add(vc);
      const vn = String(v.name || "").trim().slice(0, 80) || vc;
      const delta = +num(v.price_delta, 0).toFixed(4);
      /* a plan's value declares how many months it runs */
      const extra = JSON.stringify(kind.runs_months ? { months: Math.max(1, Math.floor(num(v.months != null ? v.months : (v.extra || {}).months, 12))) } : {});
      const ex = D.get("SELECT id FROM option_values WHERE group_id=? AND code=?", id, vc);
      if (ex) D.run("UPDATE option_values SET name=?, price_delta=?, position=?, active=1, extra=? WHERE id=?", vn, delta, pos, extra, ex.id);
      else D.run("INSERT INTO option_values(tenant_id,group_id,code,name,price_delta,position,active,extra) VALUES(?,?,?,?,?,?,1,?)", Number(tid), id, vc, vn, delta, pos, extra);
    });
    for (const v of D.all("SELECT id, code FROM option_values WHERE group_id=?", id)) if (!seen.has(v.code)) D.run("UPDATE option_values SET active=0 WHERE id=?", v.id);
  }
  return present(D.get("SELECT * FROM option_groups WHERE id=?", id));
}
function removeGroup(tid, id) {
  params(tid);
  const D = db();
  const g = D.get("SELECT * FROM option_groups WHERE id=? AND tenant_id=?", Number(id), Number(tid));
  if (!g) throw fail("Option group not found", 404);
  D.run("DELETE FROM product_option_groups WHERE tenant_id=? AND group_id=?", Number(tid), g.id);
  D.run("DELETE FROM option_values WHERE group_id=?", g.id);
  D.run("DELETE FROM option_groups WHERE id=?", g.id);
  return { ok: true };
}
/* which groups a product offers, in order — replacing what it had */
function attach(tid, productId, groupIds) {
  params(tid);
  const D = db();
  if (!D.get("SELECT id FROM products WHERE tenant_id=? AND id=?", Number(tid), String(productId))) throw fail("Unknown product", 404);
  const ids = (Array.isArray(groupIds) ? groupIds : []).map(Number).filter(Boolean);
  for (const gid of ids) if (!D.get("SELECT id FROM option_groups WHERE id=? AND tenant_id=?", gid, Number(tid))) throw fail("Unknown option group " + gid, 404);
  D.run("DELETE FROM product_option_groups WHERE tenant_id=? AND product_id=?", Number(tid), String(productId));
  ids.forEach((gid, pos) => D.run("INSERT INTO product_option_groups(tenant_id,product_id,group_id,position) VALUES(?,?,?,?)", Number(tid), String(productId), gid, pos));
  return forProduct(tid, productId, true);
}
/* what the product page offers: the attached, active groups and their active values */
function forProduct(tid, productId, all) {
  if (!caps().on(tid, "product_options")) return [];
  return db().all("SELECT g.* FROM product_option_groups pg JOIN option_groups g ON g.id=pg.group_id WHERE pg.tenant_id=? AND pg.product_id=?" + (all ? "" : " AND g.active=1") + " ORDER BY pg.position",
    Number(tid), String(productId)).map(present).map(g => ({ ...g, values: all ? g.values : g.values.filter(v => v.active) }));
}
function attachedTo(tid) {
  return db().all("SELECT pg.product_id, pg.group_id, p.title FROM product_option_groups pg LEFT JOIN products p ON p.tenant_id=pg.tenant_id AND p.id=pg.product_id WHERE pg.tenant_id=? ORDER BY pg.product_id, pg.position", Number(tid));
}

/* ---------- the line term ---------- */
/* a choice: { <group code>: [<value code>…] } for a list, or { <group code>: "<text>" } */
function cleanChoice(ctx, value) {
  const P = params(ctx.tid);
  const offered = forProduct(ctx.tid, ctx.product.id);
  const v = value && typeof value === "object" && !Array.isArray(value) ? value : {};
  for (const k of Object.keys(v)) if (!offered.some(g => g.code === k)) throw fail("This product has no option " + k);
  const out = {};
  for (const g of offered) {
    const raw = v[g.code];
    if (g.kind_row && g.kind_row.takes_text) {
      const t = String(raw == null ? "" : raw).replace(/[\u0000-\u001F]/g, "").trim();
      if (!t) { if (g.min_select > 0) throw fail(g.name + " is required"); continue; }
      const max = Math.min(Number(g.max_length) || Number(P.max_text_length), Number(P.max_text_length) || 500);
      if (t.length > max) throw fail(g.name + ": at most " + max + " characters");
      out[g.code] = t;
      continue;
    }
    const picks = [...new Set((Array.isArray(raw) ? raw : raw == null || raw === "" ? [] : [raw]).map(String))];
    for (const c of picks) if (!g.values.some(x => x.code === c)) throw fail(g.name + ": no choice " + c);
    if (picks.length < g.min_select) throw fail(g.name + ": choose " + (g.min_select === 1 ? "one" : "at least " + g.min_select));
    if (picks.length > g.max_select) throw fail(g.name + ": choose at most " + g.max_select);
    if (picks.length) out[g.code] = picks;
  }
  for (const g of offered) if (g.min_select > 0 && out[g.code] == null) throw fail(g.name + " is required");
  return Object.keys(out).length ? out : null;
}
function priceChoice(ctx, value) {
  const offered = forProduct(ctx.tid, ctx.product.id, true);
  let add = 0, set = null;
  const parts = [];
  for (const [code, picked] of Object.entries(value || {})) {
    const g = offered.find(x => x.code === code);
    if (!g) throw fail("an option on this line was withdrawn");
    if (typeof picked === "string") { parts.push(g.name + ": “" + picked + "”"); continue; }
    const names = [];
    for (const c of picked) {
      const val = g.values.find(x => x.code === c);
      if (!val || !val.active) throw fail(g.name + ": " + c + " is no longer offered");
      /* a kind that sets the price (a sample) prices the line at its value; others add to it */
      if (g.kind_row && g.kind_row.sets_price) set = Number(val.price_delta) || 0; else add += Number(val.price_delta) || 0;
      names.push(val.name);
    }
    parts.push(g.name + ": " + names.join(", "));
  }
  return { ...(set != null ? { set } : {}), add, label: parts.join(" · ") };
}
/* a kind that limits how many a bag holds (a sample) caps the line at the capability's param */
function maxChoice(ctx, value) {
  const offered = forProduct(ctx.tid, ctx.product.id, true);
  const limits = Object.keys(value || {}).some(code => { const g = offered.find(x => x.code === code); return g && g.kind_row && g.kind_row.limits_qty; });
  return limits ? Number(params(ctx.tid).sample_max_qty) || 1 : Infinity;
}
/* once the order exists: every chosen option whose kind leaves something to do becomes a follow-up */
function placeChoice(ctx, value) {
  const offered = forProduct(ctx.tid, ctx.product.id, true);
  for (const [code, picked] of Object.entries(value || {})) {
    const g = offered.find(x => x.code === code);
    const kind = g && g.kind_row;
    if (!kind || !kind.follow_up) continue;
    for (const c of typeof picked === "string" ? [""] : picked) {
      const val = g.values.find(x => x.code === c);
      const months = val && val.extra && val.extra.months;
      const ends = months ? (() => { const d = new Date(); d.setUTCMonth(d.getUTCMonth() + Number(months)); return d.toISOString().slice(0, 19).replace("T", " "); })() : null;
      db().run("INSERT INTO option_follow_ups(tenant_id,order_id,product_id,owner,group_code,value_code,kind,detail,ends_at,status) VALUES(?,?,?,?,?,?,?,?,?,?)",
        Number(ctx.tid), Number(ctx.orderId), ctx.product.id, String(ctx.owner || ""), code, c, kind.key, typeof picked === "string" ? picked : (val ? val.name : ""), ends,
        kind.settled ? states.actionTarget("option_follow_up", "complete") : states.initial("option_follow_up"));
    }
  }
}
lineterms.register("options", { atom: "product_options", clean: cleanChoice, price: priceChoice, maxQty: maxChoice, place: placeChoice });

/* ---------- follow-ups: staff schedule visits and send proofs; the shopper approves a proof ---------- */
const presentFollowUp = f => ({ ...f, state: states.display("option_follow_up", f.status), next: states.next("option_follow_up", f.status),
  awaiting: states.is("option_follow_up", f.status, "awaiting_shopper") });
function followUps(tid, o) {
  params(tid);
  return db().all("SELECT * FROM option_follow_ups WHERE tenant_id=?" + (o && o.orderId ? " AND order_id=?" : "") + (o && o.owner ? " AND owner=?" : "") + " ORDER BY id DESC LIMIT 300",
    Number(tid), ...(o && o.orderId ? [Number(o.orderId)] : []), ...(o && o.owner ? [String(o.owner)] : [])).map(presentFollowUp);
}
function moveFollowUp(tid, id, action, input, byShopper) {
  params(tid);
  const f = db().get("SELECT * FROM option_follow_ups WHERE id=? AND tenant_id=?", Number(id), Number(tid));
  if (!f || (byShopper && f.owner !== String(byShopper))) throw fail("Follow-up not found", 404);
  const to = states.actionTarget("option_follow_up", action);
  if (!to || !states.can("option_follow_up", f.status, to)) throw fail("That cannot be done to this follow-up now", 409);
  /* a shopper may only answer a proof sent to them */
  if (byShopper && !states.is("option_follow_up", f.status, "awaiting_shopper")) throw fail("Nothing awaits your answer here", 409);
  const i = input || {};
  const mv = states.apply("option_follow_up", { tenantId: tid, from: f.status, to, row: f });
  const patch = { ...mv.patch, ...(i.scheduled_for ? { scheduled_for: String(i.scheduled_for) } : {}), ...(i.proof_url ? { proof_url: String(i.proof_url).slice(0, 500) } : {}), ...(i.note != null ? { note: String(i.note).slice(0, 500) } : {}) };
  const cols = Object.keys(patch);
  db().run("UPDATE option_follow_ups SET " + cols.map(c => c + "=?").join(", ") + " WHERE id=?", ...cols.map(c => patch[c]), f.id);
  if (!byShopper && states.is("option_follow_up", to, "awaiting_shopper")) require("./tell.js").tell(tid, f.owner, "option_follow_up", "A proof to approve", "Your " + f.group_code + " proof is ready — approve it or ask for changes in Your Orders.", "orders.html");
  return presentFollowUp(db().get("SELECT * FROM option_follow_ups WHERE id=?", f.id));
}

function vocabulary() {
  return { kinds: rows("optionKinds"), followUpActions: Object.entries(states.actions("option_follow_up")).map(([verb, to]) => ({ verb, to, label: states.display("option_follow_up", to).label })) };
}

module.exports = { groups, saveGroup, removeGroup, attach, forProduct, attachedTo, vocabulary, followUps, moveFollowUp };
