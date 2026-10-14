/* LUXORA Platform — Customer Trust & Commerce Content (UGC).
   Rich reviews (helpfulness votes, seller reply threads, photo media, moderation states)
   and product Q&A (questions, answers, votes, moderation). One vote per owner per target is
   enforced by the ugc_votes primary key; moderation states and author roles live in
   meta_lists (ugcStates, ugcRoles) so they are editable from Data Studio. */
"use strict";

const db = () => require("./db.js");
const J = (v, d) => { try { return v == null || v === "" ? (d == null ? [] : d) : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d == null ? [] : d; } };

const STATES = ["pending", "approved", "rejected"];
const ROLES = ["customer", "seller", "admin", "platform"];

function seed() {
  const D = db();
  const put = (name, label, items) => {
    const existing = D.get("SELECT items FROM meta_lists WHERE name=?", name);
    const cur = J(existing ? existing.items : "[]", []);
    for (const it of items) if (!cur.some(x => (x.key || x) === (it.key || it))) cur.push(it);
    if (existing) D.run("UPDATE meta_lists SET items=? WHERE name=?", JSON.stringify(cur), name);
    else D.run("INSERT INTO meta_lists(name,label,items) VALUES(?,?,?)", name, label, JSON.stringify(items));
  };
  put("ugcStates", "UGC · Moderation states", STATES.map(k => ({ key: k, name: k })));
  put("ugcRoles", "UGC · Author roles", ROLES.map(k => ({ key: k, name: k })));
}

/* ---------------- reviews ---------------- */
function addReview(tenantId, productId, owner, name, input, moderate) {
  const D = db();
  const rating = Math.max(1, Math.min(5, Number(input.rating) || 5));
  const media = (Array.isArray(input.media) ? input.media : []).filter(m => m && typeof m === "object").slice(0, 5);
  const state = moderate ? "pending" : "approved";
  const r = D.run("INSERT INTO reviews(tenant_id,product_id,user_id,name,rating,title,body,verified,state,media) VALUES(?,?,?,?,?,?,?,0,?,?)",
    tenantId, String(productId), null, String(name || "A customer").slice(0, 80), rating,
    String(input.title || "My review").slice(0, 120), String(input.body || "").slice(0, 4000), state, JSON.stringify(media));
  return { id: Number(r.lastInsertRowid), state, rating };
}

function reviewById(tenantId, id) {
  const D = db();
  const rv = D.get("SELECT * FROM reviews WHERE id=? AND tenant_id=?", Number(id), tenantId);
  if (!rv) return null;
  rv.media = J(rv.media, []);
  rv.replies = D.all("SELECT id, author, role, body, created_at FROM review_replies WHERE review_id=? ORDER BY id", rv.id);
  return rv;
}

function listReviews(tenantId, productId, opts) {
  const D = db(); opts = opts || {};
  let sql = "SELECT * FROM reviews WHERE tenant_id=? AND product_id=?";
  if (!opts.includePending) sql += " AND state='approved'";
  sql += " ORDER BY verified DESC, votes_helpful DESC, created_at DESC LIMIT 100";
  return D.all(sql, tenantId, String(productId)).map(rv => ({ ...rv, media: J(rv.media, []), replies: D.all("SELECT id, author, role, body, created_at FROM review_replies WHERE review_id=? ORDER BY id", rv.id) }));
}

function setReviewState(tenantId, id, state) {
  const D = db();
  if (!STATES.includes(state)) throw new Error("Unknown moderation state: " + state);
  D.run("UPDATE reviews SET state=? WHERE id=? AND tenant_id=?", state, Number(id), tenantId);
  return reviewById(tenantId, id);
}

function replyReview(tenantId, id, author, role, body) {
  const D = db();
  if (!D.get("SELECT id FROM reviews WHERE id=? AND tenant_id=?", Number(id), tenantId)) throw new Error("Unknown review");
  const r = D.run("INSERT INTO review_replies(tenant_id,review_id,author,role,body) VALUES(?,?,?,?,?)",
    tenantId, Number(id), String(author || "Store").slice(0, 80), ROLES.includes(role) ? role : "seller", String(body || "").slice(0, 2000));
  return D.get("SELECT * FROM review_replies WHERE id=?", Number(r.lastInsertRowid));
}

/* ---------------- votes (reviews + Q&A share one ledger) ---------------- */
function vote(tenantId, entity, entityId, owner, dir) {
  const D = db();
  if (dir !== "up" && dir !== "down") throw new Error("vote dir must be up|down");
  const table = entity === "review" ? "reviews" : entity === "question" ? "qna_questions" : "qna_answers";
  const col = entity === "answer" ? "question_id" : entity === "question" ? "id" : "id";
  const row = D.get(`SELECT id FROM ${table} WHERE id=? AND tenant_id=?`, Number(entityId), tenantId);
  if (!row) throw new Error("Unknown " + entity + " " + entityId);
  const prev = D.get("SELECT dir FROM ugc_votes WHERE entity=? AND entity_id=? AND owner=?", entity, Number(entityId), owner);
  if (prev && prev.dir === dir) return { changed: false, dir };                       /* same vote: idempotent */
  if (prev) D.run("UPDATE ugc_votes SET dir=?, at=datetime('now') WHERE entity=? AND entity_id=? AND owner=?", dir, entity, Number(entityId), owner);
  else D.run("INSERT INTO ugc_votes(entity,entity_id,tenant_id,owner,dir) VALUES(?,?,?,?,?)", entity, Number(entityId), tenantId, owner, dir);
  /* net change on helpfulness = new direction minus the previous one (0 → ±1, flip → ±2) */
  const prevDelta = prev ? (prev.dir === "up" ? 1 : -1) : 0;
  const net = (dir === "up" ? 1 : -1) - prevDelta;
  D.run(`UPDATE ${table} SET votes_helpful=MAX(0,votes_helpful+?), votes_total=votes_total+? WHERE id=?`, net, prev ? 0 : 1, Number(entityId));
  return { changed: true, dir };
}

/* ---------------- Q&A ---------------- */
function askQuestion(tenantId, productId, owner, name, text, moderate) {
  const D = db();
  const state = moderate ? "pending" : "approved";
  const r = D.run("INSERT INTO qna_questions(tenant_id,product_id,owner,name,body,state) VALUES(?,?,?,?,?,?)",
    tenantId, String(productId), owner, String(name || "A customer").slice(0, 80), String(text || "").slice(0, 600), state);
  return { id: Number(r.lastInsertRowid), state };
}

function answerQuestion(tenantId, questionId, owner, name, role, text, moderate) {
  const D = db();
  const q = D.get("SELECT id FROM qna_questions WHERE id=? AND tenant_id=?", Number(questionId), tenantId);
  if (!q) throw new Error("Unknown question");
  const state = moderate ? "pending" : "approved";
  const r = D.run("INSERT INTO qna_answers(tenant_id,question_id,owner,name,role,body,state) VALUES(?,?,?,?,?,?,?)",
    tenantId, Number(questionId), owner, String(name || "A customer").slice(0, 80), ROLES.includes(role) ? role : "customer",
    String(text || "").slice(0, 2000), state);
  D.run("UPDATE qna_questions SET answered_at=datetime('now') WHERE id=?", Number(questionId));
  return { id: Number(r.lastInsertRowid), state };
}

function listQuestions(tenantId, productId, opts) {
  const D = db(); opts = opts || {};
  let sql = "SELECT * FROM qna_questions WHERE tenant_id=? AND product_id=?";
  if (!opts.includePending) sql += " AND state='approved'";
  sql += " ORDER BY votes_helpful DESC, created_at DESC LIMIT 50";
  return D.all(sql, tenantId, String(productId)).map(q => {
    let aSql = "SELECT id,name,role,body,votes_helpful,created_at,state FROM qna_answers WHERE question_id=?";
    if (!opts.includePending) aSql += " AND state='approved'";
    return { ...q, answers: D.all(aSql + " ORDER BY votes_helpful DESC, id", q.id) };
  });
}

function setQnaState(tenantId, kind, id, state) {
  const D = db();
  if (!STATES.includes(state)) throw new Error("Unknown moderation state: " + state);
  const table = kind === "question" ? "qna_questions" : "qna_answers";
  D.run(`UPDATE ${table} SET state=? WHERE id=? AND tenant_id=?`, state, Number(id), tenantId);
  /* read back within the tenant — another store's row is "unknown", never returned */
  const row = D.get(`SELECT * FROM ${table} WHERE id=? AND tenant_id=?`, Number(id), tenantId);
  if (!row) throw new Error("Unknown " + kind + " " + id);
  return row;
}

/* ---------------- product summary (used by the product page) ---------------- */
function productUgc(tenantId, productId) {
  const D = db();
  const rr = D.get("SELECT COUNT(*) n, COALESCE(AVG(rating),0) avg FROM reviews WHERE tenant_id=? AND product_id=? AND state='approved'", tenantId, String(productId));
  const qq = D.get("SELECT COUNT(*) n FROM qna_questions WHERE tenant_id=? AND product_id=? AND state='approved'", tenantId, String(productId));
  return { reviews: rr.n, avg: +(rr.avg || 0).toFixed(2), questions: qq.n };
}

/* ---------------- moderation queue ---------------- */
function moderationQueue(tenantId) {
  const D = db();
  return {
    reviews: D.all("SELECT id,product_id,name,rating,title,body,state,created_at FROM reviews WHERE tenant_id=? AND state='pending' ORDER BY created_at DESC LIMIT 100", tenantId),
    questions: D.all("SELECT id,product_id,name,body,state,created_at FROM qna_questions WHERE tenant_id=? AND state='pending' ORDER BY created_at DESC LIMIT 100", tenantId),
    answers: D.all("SELECT a.id,a.question_id,a.name,a.role,a.body,a.state,a.created_at,q.product_id FROM qna_answers a JOIN qna_questions q ON q.id=a.question_id WHERE a.tenant_id=? AND a.state='pending' ORDER BY a.created_at DESC LIMIT 100", tenantId)
  };
}

module.exports = {
  seed, STATES, ROLES,
  addReview, reviewById, listReviews, setReviewState, replyReview,
  vote, askQuestion, answerQuestion, listQuestions, setQnaState,
  productUgc, moderationQueue
};
