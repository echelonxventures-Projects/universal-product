/* LUXORA Platform — Rich product content (brand-authored modules below a product's details).
   A product may carry a stack of modules — a banner, image-and-text, a feature list, a
   comparison table, questions and answers. Which modules exist and which fields each holds
   are contentModules registry rows: a field declares only its TYPE (text, textarea, image,
   list, table) and its limits, so a new module — a size guide, a "what's in the box" — is a
   row, and both this engine's validation and the storefront's renderer follow it.

   Content moves through the rich_content state machine (draft → in review → live, or back
   for changes); a newly approved version retires the one it replaces. Whether content is
   reviewed at all, how many modules a product carries and whether only the brand's
   registered owner may publish are the rich_content capability's params. */
"use strict";

const db = () => require("./db.js");
const caps = () => require("./capabilities.js");
const reg = () => require("./parity-registries.js");
const states = require("./states.js");
const J = (v, d) => { try { return v == null || v === "" ? (d == null ? [] : d) : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d == null ? [] : d; } };
const fail = (msg, status) => Object.assign(new Error(msg), { status: status || 400 });

const rows = name => reg().list(name).map(x => (typeof x === "string" ? { key: x, name: x } : x)).filter(x => x && x.key);
const moduleOf = key => rows("contentModules").find(r => r.key === String(key == null ? "" : key)) || null;
const inTag = tag => { const xs = states.tagged("rich_content", tag); return { sql: "(" + (xs.length ? xs.map(() => "?").join(",") : "NULL") + ")", args: xs }; };

function params(tid) {
  const P = caps().cap(tid, "rich_content");
  if (!Object.keys(P).length) throw fail("Rich product content is not available in this store", 403);
  return P;
}

/* ---------- field types: how a value is cleaned, and what it must satisfy ----------
   The engine's own vocabulary. Every type answers the cleaned value or throws; a field a
   module row declares with a type this engine does not know is refused, never guessed. */
const str = (v, max) => String(v == null ? "" : v).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, "").trim().slice(0, Math.max(1, Number(max) || 200));
const linesOf = v => (Array.isArray(v) ? v : String(v == null ? "" : v).split(/\r?\n/)).map(x => String(x == null ? "" : x)).filter(x => x.trim());
function textField(v, f) { return str(v, f.max || 200); }
function textareaField(v, f) { return str(v, f.max || 2000); }
/* an image is this store's own (a path such as /media/…) or an https address on a host the
   platform policy lets the storefront load images from (the CSP's img-src) — anything else
   the browser would refuse to show */
function imageField(v, f) {
  const s = str(v, 500);
  if (!s) return "";
  if (/^\/(?!\/)[^\s"'<>]*$/.test(s)) return s;
  let u; try { u = new URL(s); } catch (e) { throw fail(f.label + ": not a web address"); }
  if (u.protocol !== "https:") throw fail(f.label + ": images must be served over https");
  const sec = require("./security.js");
  const hosts = sec.imgHosts(sec.policy());
  const allowed = hosts.some(h => (h.startsWith("*.") ? u.hostname.endsWith(h.slice(1)) : u.hostname === h));
  if (!allowed) throw fail(f.label + ": " + u.hostname + " is not an image host this platform allows (Platform → Security → image hosts)" + (hosts.length ? "; allowed: " + hosts.join(", ") : ""));
  return u.toString();
}
function listField(v, f) {
  const xs = linesOf(v).map(x => str(x, f.max || 200));
  if (xs.length > (Number(f.max_items) || 10)) throw fail(f.label + ": at most " + (Number(f.max_items) || 10) + " entries");
  return xs;
}
/* a table is rows of cells: an array of arrays, or lines whose cells are separated by | */
function tableField(v, f) {
  const raw = Array.isArray(v) ? v : linesOf(v).map(l => l.split("|"));
  const maxR = Number(f.max_rows) || 12, maxC = Number(f.max_cols) || 6;
  const out = raw.map(r => (Array.isArray(r) ? r : [r]).map(c => str(c, f.max || 200))).filter(r => r.some(c => c));
  if (out.length > maxR) throw fail(f.label + ": at most " + maxR + " rows");
  if (out.some(r => r.length > maxC)) throw fail(f.label + ": at most " + maxC + " columns");
  return out;
}
const FIELD_TYPES = { text: textField, textarea: textareaField, image: imageField, list: listField, table: tableField };
const empty = v => v == null || v === "" || (Array.isArray(v) && !v.length);
/* one module, cleaned against its row: only declared fields survive */
function cleanModule(m, P, at) {
  const row = moduleOf(m && m.kind);
  if (!row) throw fail("Module " + at + ": unknown kind " + (m && m.kind));
  const out = { kind: row.key };
  for (const f of Array.isArray(row.fields) ? row.fields : []) {
    const t = FIELD_TYPES[f.type];
    if (!t) throw fail("Module " + row.name + ": field " + f.key + " has a type this store cannot show (" + f.type + ")");
    const v = t(m[f.key], f, P);
    if (f.required && empty(v)) throw fail(row.name + ": " + f.label + " is required");
    if (!empty(v)) out[f.key] = v;
  }
  return out;
}
function cleanModules(list, P) {
  const xs = Array.isArray(list) ? list : J(list, []);
  if (!xs.length) throw fail("Add at least one module");
  if (xs.length > Number(P.max_modules)) throw fail("A product carries at most " + P.max_modules + " modules");
  return xs.map((m, i) => cleanModule(m, P, i + 1));
}

/* ---------- authoring ---------- */
const productOf = (tid, id) => db().get("SELECT id, title, brand FROM products WHERE tenant_id=? AND id=? AND deleted_at IS NULL", Number(tid), String(id || ""));
function present(r) {
  const p = productOf(r.tenant_id, r.product_id);
  return { ...r, modules: J(r.modules, []), state: states.display("rich_content", r.status), next: states.next("rich_content", r.status),
    editable: states.is("rich_content", r.status, "editable"), product: p || null };
}
/* save a draft: the product's editable version is rewritten, or a new version starts from it */
function save(tid, input, by) {
  const P = params(tid);
  const i = input || {};
  const p = productOf(tid, i.product_id);
  if (!p) throw fail("Unknown product", 404);
  const sellerId = Number(i.seller_id) || null;
  if (P.brand_owner_only) {
    const owner = require("./brandreg.js").ownerOf(tid, p.brand);
    if (!owner || !sellerId || Number(owner.seller_id) !== sellerId) throw fail("Only " + (p.brand || "the brand") + "'s registered owner may publish content for this product", 403);
  }
  const modules = cleanModules(i.modules, P);
  const D = db();
  const ed = inTag("editable");
  const ex = D.get("SELECT * FROM rich_content WHERE tenant_id=? AND product_id=? AND status IN " + ed.sql + " ORDER BY version DESC LIMIT 1", Number(tid), p.id, ...ed.args);
  if (ex) {
    D.run("UPDATE rich_content SET modules=?, seller_id=?, author=?, updated_at=datetime('now') WHERE id=?", JSON.stringify(modules), sellerId, String(by || ""), ex.id);
    return present(D.get("SELECT * FROM rich_content WHERE id=?", ex.id));
  }
  const v = (D.get("SELECT MAX(version) m FROM rich_content WHERE tenant_id=? AND product_id=?", Number(tid), p.id).m || 0) + 1;
  const r = D.run("INSERT INTO rich_content(tenant_id,product_id,seller_id,author,modules,status,version) VALUES(?,?,?,?,?,?,?)",
    Number(tid), p.id, sellerId, String(by || ""), JSON.stringify(modules), states.initial("rich_content"), v);
  return present(D.get("SELECT * FROM rich_content WHERE id=?", r.lastInsertRowid));
}
/* a move is one of the machine's verbs. Submitting where the store reviews nothing goes
   straight live; approving retires the live version it replaces. */
function act(tid, id, action, by, notes) {
  const P = params(tid);
  const D = db();
  const r = D.get("SELECT * FROM rich_content WHERE id=? AND tenant_id=?", Number(id), Number(tid));
  if (!r) throw fail("Content not found", 404);
  let to = states.actionTarget("rich_content", action);
  if (!to) throw fail("Unknown action: " + action);
  if (states.is("rich_content", to, "in_review") && !P.require_approval) to = states.first("rich_content", "live");
  if (!states.can("rich_content", r.status, to)) throw fail("Content that is " + states.display("rich_content", r.status).label + " cannot be moved that way", 409);
  const mv = states.apply("rich_content", { tenantId: tid, from: r.status, to, row: r });
  const patch = Object.assign({}, mv.patch);
  if (states.is("rich_content", to, "decision")) Object.assign(patch, { reviewed_by: String(by || ""), review_notes: String(notes || "").slice(0, 1000) });
  const cols = Object.keys(patch);
  D.run("UPDATE rich_content SET " + cols.map(c => c + "=?").join(", ") + ", updated_at=datetime('now') WHERE id=?", ...cols.map(c => patch[c]), r.id);
  if (states.is("rich_content", to, "live")) {
    const lv = inTag("live");
    const retired = states.first("rich_content", "terminal");
    for (const old of D.all("SELECT * FROM rich_content WHERE tenant_id=? AND product_id=? AND id<>? AND status IN " + lv.sql, Number(tid), r.product_id, r.id, ...lv.args)) {
      const m2 = states.apply("rich_content", { tenantId: tid, from: old.status, to: retired, row: old, force: true });
      const c2 = Object.keys(m2.patch);
      D.run("UPDATE rich_content SET " + c2.map(c => c + "=?").join(", ") + " WHERE id=?", ...c2.map(c => m2.patch[c]), old.id);
    }
  }
  return present(D.get("SELECT * FROM rich_content WHERE id=?", r.id));
}
/* what the product page shows: the live version, when the store has the capability on */
function live(tid, productId) {
  if (!caps().on(tid, "rich_content")) return null;
  const lv = inTag("live");
  const r = db().get("SELECT * FROM rich_content WHERE tenant_id=? AND product_id=? AND status IN " + lv.sql + " ORDER BY version DESC LIMIT 1", Number(tid), String(productId), ...lv.args);
  return r ? { version: r.version, modules: J(r.modules, []), kinds: rows("contentModules") } : null;
}
function list(tid, filter) {
  const f = filter || {};
  const where = ["tenant_id=?"], args = [Number(tid)];
  if (f.tag) { const t = inTag(f.tag); where.push("status IN " + t.sql); args.push(...t.args); }
  if (f.product_id) { where.push("product_id=?"); args.push(String(f.product_id)); }
  return db().all("SELECT * FROM rich_content WHERE " + where.join(" AND ") + " ORDER BY id DESC LIMIT 200", ...args).map(present);
}
function vocabulary() {
  return { modules: rows("contentModules"), types: Object.keys(FIELD_TYPES),
    actions: Object.entries(states.actions("rich_content")).map(([verb, to]) => ({ verb, to, label: states.display("rich_content", to).label })) };
}

module.exports = { FIELD_TYPES, cleanModules, save, act, live, list, vocabulary };
