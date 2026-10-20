/* LUXORA Platform — Buyer–seller conversations.
   A shopper messages whoever is on the other side of something — a product (its listing's
   owner, or the store), an order, a booking. What a conversation may be about is a
   conversationSubjects row naming the RESOLVER that finds that other side (this engine's own
   small vocabulary); a new subject is a row naming an existing resolver. The store's side is
   answered by its staff. Email addresses and phone numbers can be hidden so trades stay on
   the platform, and staff can read, flag and close any conversation. Capability: conversations. */
"use strict";

const db = () => require("./db.js");
const caps = () => require("./capabilities.js");
const reg = () => require("./parity-registries.js");
const states = require("./states.js");
const lineterms = require("./lineterms.js");
const fail = lineterms.fail;
const rows = name => reg().list(name).map(x => (typeof x === "string" ? { key: x, name: x } : x)).filter(x => x && x.key);
const subjectOf = key => rows("conversationSubjects").find(r => r.key === String(key == null ? "" : key)) || null;
const tellmod = () => require("./tell.js");

function params(tid) {
  const P = caps().cap(tid, "conversations");
  if (!Object.keys(P).length) throw fail("Messages are not available in this store", 403);
  return P;
}
/* the other side of a subject, and what it is called: an owner key, or "" for the store */
const RESOLVERS = {
  product: (tid, ref) => {
    const p = db().get("SELECT id, title FROM products WHERE tenant_id=? AND id=?", Number(tid), String(ref));
    if (!p) throw fail("Unknown product", 404);
    let owner = ""; try { owner = require("./listings.js").ownerOf(tid, p.id); } catch (e) { }
    return { counterpart: owner, title: p.title };
  },
  order: (tid, ref, buyer) => {
    const o = db().get("SELECT id, num, owner FROM orders WHERE tenant_id=? AND (num=? OR id=?)", Number(tid), String(ref), Number(ref) || -1);
    if (!o || o.owner !== buyer) throw fail("Unknown order", 404);
    return { counterpart: "", title: "Order " + o.num };
  },
  booking: (tid, ref, buyer) => {
    const b = db().get("SELECT id, ref, owner, product_id FROM bookings WHERE tenant_id=? AND (ref=? OR id=?)", Number(tid), String(ref), Number(ref) || -1);
    if (!b || b.owner !== buyer) throw fail("Unknown booking", 404);
    return { counterpart: "", title: "Booking " + b.ref };
  }
};
/* hide email addresses and phone numbers, where the store says so */
function scrub(P, text) {
  let t = String(text || "").replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, "").trim();
  if (P.hide_contact_details) t = t.replace(/[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+/g, "[hidden]").replace(/\+?\d[\d ()-]{7,}\d/g, "[hidden]");
  return t;
}
/* who the actor is in a conversation: its buyer, its counterpart, or staff answering for the store */
function sideOf(c, actor) {
  if (actor.owner && actor.owner === c.buyer) return "buyer";
  if (c.counterpart ? actor.owner === c.counterpart : !!actor.staff) return "seller";
  return null;
}
function present(c, actor) {
  const side = sideOf(c, actor);
  const unread = db().get("SELECT COUNT(*) n FROM conversation_messages WHERE conversation_id=? AND side<>? AND read_by_other=0 AND hidden=0", c.id, side || "").n;
  return { id: c.id, subject: subjectOf(c.subject_kind) || { key: c.subject_kind }, ref: c.subject_ref, title: c.title, status: c.status,
    state: states.display("conversation", c.status), side, last_at: c.last_at, unread,
    with: side === "buyer" ? (c.counterpart ? tellmod().nameOf(c.tenant_id, c.counterpart) || "Seller" : "the store") : tellmod().nameOf(c.tenant_id, c.buyer) || "Shopper" };
}

/* a shopper opens (or reopens) the conversation about a subject, with a first message */
function start(tid, actor, input) {
  const P = params(tid);
  const i = input || {};
  const subj = subjectOf(i.subject) || rows("conversationSubjects").find(r => r.default) || null;
  if (!subj || !RESOLVERS[subj.resolver]) throw fail("Unknown subject");
  const r = RESOLVERS[subj.resolver](tid, i.ref, actor.owner);
  if (r.counterpart && r.counterpart === actor.owner) throw fail("This is your own listing");
  const D = db();
  let c = D.get("SELECT * FROM conversations WHERE tenant_id=? AND subject_kind=? AND subject_ref=? AND buyer=?", Number(tid), subj.key, String(i.ref), actor.owner);
  if (!c) c = D.get("SELECT * FROM conversations WHERE id=?", D.run("INSERT INTO conversations(tenant_id,subject_kind,subject_ref,buyer,counterpart,title,status) VALUES(?,?,?,?,?,?,?)",
    Number(tid), subj.key, String(i.ref), actor.owner, r.counterpart, r.title, states.initial("conversation")).lastInsertRowid);
  if (i.body) post(tid, actor, c.id, i.body, P);
  return thread(tid, actor, c.id);
}
function post(tid, actor, id, body, P0) {
  const P = P0 || params(tid);
  const D = db();
  const c = D.get("SELECT * FROM conversations WHERE id=? AND tenant_id=?", Number(id), Number(tid));
  const side = c && sideOf(c, actor);
  if (!side) throw fail("Conversation not found", 404);
  if (!states.is("conversation", c.status, "writable")) throw fail("This conversation is closed", 409);
  const text = scrub(P, body).slice(0, Number(P.max_length) || 2000);
  if (!text) throw fail("Write a message");
  D.run("INSERT INTO conversation_messages(tenant_id,conversation_id,sender,side,body) VALUES(?,?,?,?,?)", Number(tid), c.id, actor.owner || "staff", side, text);
  D.run("UPDATE conversations SET last_at=datetime('now') WHERE id=?", c.id);
  const other = side === "buyer" ? c.counterpart : c.buyer;
  if (other) tellmod().tell(tid, other, "message", "New message: " + c.title, text.slice(0, 160), "messages.html?c=" + c.id, { email: true });
  return { ok: true };
}
/* a thread, marked read for the side reading it */
function thread(tid, actor, id) {
  const P = params(tid);
  const D = db();
  const c = D.get("SELECT * FROM conversations WHERE id=? AND tenant_id=?", Number(id), Number(tid));
  const side = c && sideOf(c, actor);
  const staffView = !side && actor.staff && P.staff_can_read;
  if (!side && !staffView) throw fail("Conversation not found", 404);
  if (side) D.run("UPDATE conversation_messages SET read_by_other=1 WHERE conversation_id=? AND side<>?", c.id, side);
  const msgs = D.all("SELECT id, side, body, hidden, at FROM conversation_messages WHERE conversation_id=? ORDER BY id", c.id)
    .filter(m => staffView || !m.hidden).map(m => ({ id: m.id, mine: m.side === side, side: m.side, body: m.hidden && !staffView ? "" : m.body, hidden: !!m.hidden, at: m.at }));
  return { conversation: present(c, actor), messages: msgs };
}
/* the shopper's conversations — as a buyer, and as the seller of their own listings */
function mine(tid, owner) {
  params(tid);
  return db().all("SELECT * FROM conversations WHERE tenant_id=? AND (buyer=? OR counterpart=?) ORDER BY last_at DESC LIMIT 200", Number(tid), String(owner), String(owner))
    .map(c => present(c, { owner: String(owner) }));
}
/* staff: the store's own conversations, or every one where staff may read them */
function forStaff(tid, all) {
  const P = params(tid);
  const D = db();
  const q = all && P.staff_can_read ? D.all("SELECT * FROM conversations WHERE tenant_id=? ORDER BY last_at DESC LIMIT 300", Number(tid))
    : D.all("SELECT * FROM conversations WHERE tenant_id=? AND counterpart='' ORDER BY last_at DESC LIMIT 300", Number(tid));
  return q.map(c => present(c, { staff: true }));
}
function act(tid, id, action) {
  params(tid);
  const c = db().get("SELECT * FROM conversations WHERE id=? AND tenant_id=?", Number(id), Number(tid));
  if (!c) throw fail("Conversation not found", 404);
  const to = states.actionTarget("conversation", action);
  if (!to || !states.can("conversation", c.status, to)) throw fail("That conversation cannot be moved that way", 409);
  const mv = states.apply("conversation", { tenantId: tid, from: c.status, to, row: c });
  const cols = Object.keys(mv.patch);
  db().run("UPDATE conversations SET " + cols.map(k => k + "=?").join(", ") + " WHERE id=?", ...cols.map(k => mv.patch[k]), c.id);
  return present(db().get("SELECT * FROM conversations WHERE id=?", c.id), { staff: true });
}
function hideMessage(tid, messageId, hidden) {
  params(tid);
  const m = db().get("SELECT m.id FROM conversation_messages m JOIN conversations c ON c.id=m.conversation_id WHERE m.id=? AND c.tenant_id=?", Number(messageId), Number(tid));
  if (!m) throw fail("Message not found", 404);
  db().run("UPDATE conversation_messages SET hidden=? WHERE id=?", hidden === false ? 0 : 1, m.id);
  return { ok: true };
}
function vocabulary() {
  return { subjects: rows("conversationSubjects").filter(s => RESOLVERS[s.resolver]),
    actions: Object.entries(states.actions("conversation")).map(([verb, to]) => ({ verb, to, label: states.display("conversation", to).label })) };
}

module.exports = { RESOLVERS, start, post, thread, mine, forStaff, act, hideMessage, vocabulary };
