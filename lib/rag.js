/* LUXORA Platform — the knowledge base (retrieval for the AI assistant and any app): collections
   of entries that any platform type can keep — astrology, consultancy, legal, product help — each
   with its own way of growing (its MODE, lib/seed/rag.json), set in Store console → Knowledge.

   An entry is a titled body with tags ("planet:mars", "house:7", "topic:remedy"…). Its life is a
   status (draft → review → approved → retired, or rejected); only approved entries are retrieved.
   Every change is a new version (kb_versions) and any version can be restored. Who is an expert is
   the collection's setting: store role keys (Store console → Team), so an "astrologer" role can own
   the astrology collection and nobody else approves it.

   Retrieval: SQLite's FTS5 full-text index (BM25) on the default datastore, a portable word-match
   score elsewhere; tags narrow and boost. Feedback (ratings, corrections) is recorded per entry or
   per answer; in a learning mode a correction becomes a proposed revision, and in auto-evolving a
   proposal goes live by itself once it passes the collection's thresholds. */
"use strict";
const SEED = require("./seed/rag.json");
const db = () => require("./db.js");
const J = (v, d) => { try { return v == null || v === "" ? d : JSON.parse(v); } catch (e) { return d; } };
const live = st => !!(SEED.STATUSES[st] || {}).live;
const modeOf = key => SEED.MODES.find(m => m.key === key) || null;
const sourceOf = key => SEED.SOURCES.find(x => x.key === key) || null;
const sourceKeys = SEED.SOURCES.map(x => x.key);

/* ---------- full-text index (the default datastore's FTS5; nothing elsewhere) ---------- */
let ftsReady = null;
function fts() {
  if (ftsReady !== null) return ftsReady;
  if (db().USE_PG) return (ftsReady = false);
  try { db().run("CREATE VIRTUAL TABLE IF NOT EXISTS kb_fts USING fts5(title, body, tags, tokenize='unicode61')"); ftsReady = true; }
  catch (e) { ftsReady = false; }
  return ftsReady;
}
function index(entry) {
  if (!fts()) return;
  db().run("DELETE FROM kb_fts WHERE rowid=?", entry.id);
  if (live(entry.status)) db().run("INSERT INTO kb_fts(rowid,title,body,tags) VALUES(?,?,?,?)", entry.id, entry.title, entry.body, (J(entry.tags, []) || []).join(" "));
}

/* ---------- collections ---------- */
function collection(tenantId, key) {
  const k = cleanKey(key);
  const r = db().get("SELECT * FROM kb_collections WHERE tenant_id=? AND key=?", Number(tenantId), k);
  const s = r ? J(r.settings, {}) : {};
  return { key: k, label: r ? r.label : k, exists: !!r, mode: (r && r.mode) || SEED.DEFAULTS.mode,
    expertRoles: s.expertRoles || SEED.DEFAULTS.expertRoles, thresholds: Object.assign({}, SEED.DEFAULTS.thresholds, s.thresholds || {}),
    searchLimit: s.searchLimit || SEED.DEFAULTS.searchLimit };
}
function collections(tenantId) {
  return db().all("SELECT key FROM kb_collections WHERE tenant_id=? ORDER BY key", Number(tenantId)).map(r => Object.assign(collection(tenantId, r.key), {
    counts: Object.fromEntries(db().all("SELECT status, COUNT(*) n FROM kb_entries WHERE tenant_id=? AND collection=? GROUP BY status", Number(tenantId), r.key).map(x => [x.status, x.n])) }));
}
function cleanKey(k) { const v = String(k || "").trim().toLowerCase(); if (!/^[a-z][a-z0-9_]{0,40}$/.test(v)) throw httpErr("A collection key is a-z, 0-9 and _, starting with a letter", 400); return v; }
function saveCollection(tenantId, key, o, roleKeys) {
  const k = cleanKey(key), cur = collection(tenantId, k), x = o || {};
  const mode = x.mode != null ? String(x.mode) : cur.mode;
  if (!modeOf(mode)) throw httpErr("Unknown mode: " + mode + " (" + SEED.MODES.map(m => m.key).join(", ") + ")", 400);
  const expertRoles = x.expertRoles != null ? [].concat(x.expertRoles).map(String) : cur.expertRoles;
  const unknown = roleKeys ? expertRoles.filter(r => !roleKeys.includes(r)) : [];
  if (unknown.length) throw httpErr("Unknown role: " + unknown.join(", "), 400);
  const thresholds = Object.assign({}, cur.thresholds);
  for (const [t, v] of Object.entries(x.thresholds || {})) { if (!(t in SEED.DEFAULTS.thresholds) || !isFinite(Number(v))) throw httpErr("Unknown or invalid threshold: " + t, 400); thresholds[t] = Number(v); }
  const settings = { expertRoles, thresholds, searchLimit: Math.max(1, Math.min(50, Number(x.searchLimit) || cur.searchLimit)) };
  db().run("INSERT INTO kb_collections(tenant_id,key,label,mode,settings) VALUES(?,?,?,?,?) ON CONFLICT(tenant_id,key) DO UPDATE SET label=excluded.label, mode=excluded.mode, settings=excluded.settings",
    Number(tenantId), k, String(x.label || cur.label || k).slice(0, 120), mode, JSON.stringify(settings));
  return collection(tenantId, k);
}

/* ---------- entries ---------- */
function httpErr(m, status) { const e = new Error(m); e.status = status; return e; }
function cleanTags(tags) { return [...new Set([].concat(tags || []).map(t => String(t).trim().toLowerCase()).filter(t => /^[a-z0-9_]+(:[a-z0-9_.\-]+)?$/.test(t)))].slice(0, 40); }
const view = r => r && { id: r.id, collection: r.collection, title: r.title, body: r.body, tags: J(r.tags, []), lang: r.lang, status: r.status, source: r.source,
  confidence: r.confidence, rating: r.rating_n ? +(r.rating_sum / r.rating_n).toFixed(2) : null, votes: r.rating_n, confirmations: r.confirmations,
  version: r.version, author: r.author, approved_by: r.approved_by, updated_at: r.updated_at };
const row = (tenantId, id) => db().get("SELECT * FROM kb_entries WHERE tenant_id=? AND id=?", Number(tenantId), Number(id));
function snapshot(r, by, reason) {
  db().run("INSERT INTO kb_versions(entry_id,version,title,body,tags,status,changed_by,reason) VALUES(?,?,?,?,?,?,?,?)", r.id, r.version, r.title, r.body, r.tags, r.status, String(by || ""), String(reason || "").slice(0, 300));
}
/* the status a new or revised entry starts in, from who wrote it and the collection's mode */
function startingStatus(c, source, isExpert) {
  const m = modeOf(c.mode), src = sourceOf(source) || {};
  if (src.drafted && !m.aiDrafts) throw httpErr("This collection is in " + m.label + " mode: the AI does not draft entries", 409);
  if (src.learned && !m.learnFromFeedback) throw httpErr("This collection is in " + m.label + " mode: feedback does not change the knowledge", 409);
  return isExpert && src.trusted ? SEED.STATUS_ON_SAVE.trusted : SEED.STATUS_ON_SAVE.otherwise;
}
const authorship = expert => expert ? SEED.AUTHORSHIP.expert : SEED.AUTHORSHIP.other;
function addEntry(tenantId, collectionKey, e, actor) {
  const c = collection(tenantId, collectionKey); if (!c.exists) throw httpErr("No collection " + c.key + " — create it first", 404);
  const x = e || {}, title = String(x.title || "").trim().slice(0, 200), body = String(x.body || "").trim().slice(0, 20000);
  if (!title || !body) throw httpErr("An entry needs a title and a body", 400);
  const expert = isExpert(c, actor);
  const source = sourceKeys.includes(x.source) ? x.source : authorship(expert);
  const status = startingStatus(c, source, expert);
  const r = db().run("INSERT INTO kb_entries(tenant_id,collection,title,body,tags,lang,status,source,confidence,author,approved_by,version) VALUES(?,?,?,?,?,?,?,?,?,?,?,1)",
    Number(tenantId), c.key, title, body, JSON.stringify(cleanTags(x.tags)), String(x.lang || SEED.DEFAULTS.lang).slice(0, 12), status, source,
    x.confidence != null ? Math.max(0, Math.min(1, Number(x.confidence))) : null, actorName(actor), live(status) ? actorName(actor) : null);
  const created = row(tenantId, Number(r.lastInsertRowid));
  snapshot(created, actorName(actor), "created"); index(created);
  return view(created);
}
/* a revision: an expert's lands at once; anyone else's (or a learned or AI one) is proposed for
   review — in auto-evolving mode a proposal that meets the thresholds lands by itself */
function revise(tenantId, id, patch, actor, reason) {
  const r = row(tenantId, id); if (!r) throw httpErr("Not found", 404);
  const c = collection(tenantId, r.collection), p = patch || {};
  const next = { title: p.title != null ? String(p.title).trim().slice(0, 200) : r.title, body: p.body != null ? String(p.body).trim().slice(0, 20000) : r.body,
    tags: p.tags != null ? JSON.stringify(cleanTags(p.tags)) : r.tags };
  const expert = isExpert(c, actor), source = p.source && sourceKeys.includes(p.source) ? p.source : authorship(expert), src = sourceOf(source);
  if (!expert || !src.trusted) {
    startingStatus(c, source, false);
    const pr = db().run("INSERT INTO kb_proposals(tenant_id,entry_id,title,body,tags,source,confidence,reason,author,state) VALUES(?,?,?,?,?,?,?,?,?,'open')",
      Number(tenantId), r.id, next.title, next.body, next.tags, source, p.confidence != null ? Number(p.confidence) : null, String(reason || "").slice(0, 300), actorName(actor));
    const prop = db().get("SELECT * FROM kb_proposals WHERE id=?", Number(pr.lastInsertRowid));
    return { proposed: true, proposal: proposalView(prop), applied: maybeAutoApply(tenantId, prop.id) };
  }
  db().run("UPDATE kb_entries SET title=?, body=?, tags=?, version=version+1, updated_at=datetime('now') WHERE id=?", next.title, next.body, next.tags, r.id);
  const now = row(tenantId, r.id); snapshot(now, actorName(actor), reason || "revised"); index(now);
  return { proposed: false, entry: view(now) };
}
function review(tenantId, id, decision, actor, reason) {
  const r = row(tenantId, id); if (!r) throw httpErr("Not found", 404);
  const c = collection(tenantId, r.collection);
  if (!isExpert(c, actor)) throw httpErr("Only the collection's experts (" + c.expertRoles.join(", ") + ") review its entries", 403);
  const to = SEED.DECISIONS[decision];
  if (!to) throw httpErr("decision is " + Object.keys(SEED.DECISIONS).join(", "), 400);
  db().run("UPDATE kb_entries SET status=?, approved_by=?, version=version+1, updated_at=datetime('now') WHERE id=?", to, live(to) ? actorName(actor) : r.approved_by, r.id);
  const now = row(tenantId, r.id); snapshot(now, actorName(actor), reason || decision); index(now);
  return view(now);
}
function rollback(tenantId, id, version, actor) {
  const r = row(tenantId, id); if (!r) throw httpErr("Not found", 404);
  const c = collection(tenantId, r.collection);
  if (!isExpert(c, actor)) throw httpErr("Only the collection's experts roll entries back", 403);
  const v = db().get("SELECT * FROM kb_versions WHERE entry_id=? AND version=?", r.id, Number(version)); if (!v) throw httpErr("No version " + version, 404);
  db().run("UPDATE kb_entries SET title=?, body=?, tags=?, status=?, version=version+1, updated_at=datetime('now') WHERE id=?", v.title, v.body, v.tags, v.status, r.id);
  const now = row(tenantId, r.id); snapshot(now, actorName(actor), "rolled back to version " + version); index(now);
  return view(now);
}
const history = (tenantId, id) => { const r = row(tenantId, id); if (!r) throw httpErr("Not found", 404); return db().all("SELECT version,title,status,changed_by,reason,at FROM kb_versions WHERE entry_id=? ORDER BY version DESC", r.id); };
function entries(tenantId, collectionKey, status) {
  const c = collection(tenantId, collectionKey);
  return db().all("SELECT * FROM kb_entries WHERE tenant_id=? AND collection=?" + (status ? " AND status=?" : "") + " ORDER BY updated_at DESC LIMIT 500", Number(tenantId), c.key, ...(status ? [status] : [])).map(view);
}

/* ---------- proposals (revisions waiting, from staff, the AI or feedback) ---------- */
const proposalView = p => p && { id: p.id, entry_id: p.entry_id, title: p.title, body: p.body, tags: J(p.tags, []), source: p.source, confidence: p.confidence,
  confirmations: p.confirmations, reason: p.reason, author: p.author, state: p.state, created_at: p.created_at };
function proposals(tenantId, collectionKey) {
  return db().all("SELECT p.* FROM kb_proposals p JOIN kb_entries e ON e.id=p.entry_id WHERE p.tenant_id=? AND e.collection=? AND p.state='open' ORDER BY p.id DESC", Number(tenantId), cleanKey(collectionKey)).map(proposalView);
}
function applyProposal(tenantId, pid, by, why) {
  const p = db().get("SELECT * FROM kb_proposals WHERE id=? AND tenant_id=? AND state='open'", Number(pid), Number(tenantId)); if (!p) throw httpErr("No open proposal " + pid, 404);
  db().run("UPDATE kb_entries SET title=?, body=?, tags=?, version=version+1, updated_at=datetime('now') WHERE id=?", p.title, p.body, p.tags, p.entry_id);
  db().run("UPDATE kb_proposals SET state=?, decided_by=? WHERE id=?", SEED.PROPOSAL_DECISIONS.approve, String(by), p.id);
  const now = row(tenantId, p.entry_id); snapshot(now, by, why); index(now);
  return view(now);
}
function decideProposal(tenantId, pid, decision, actor) {
  const p = db().get("SELECT * FROM kb_proposals WHERE id=? AND tenant_id=?", Number(pid), Number(tenantId)); if (!p) throw httpErr("Not found", 404);
  const c = collection(tenantId, row(tenantId, p.entry_id).collection);
  if (!isExpert(c, actor)) throw httpErr("Only the collection's experts decide proposals", 403);
  const to = SEED.PROPOSAL_DECISIONS[decision];
  if (!to) throw httpErr("decision is " + Object.keys(SEED.PROPOSAL_DECISIONS).join(" or "), 400);
  if (to === SEED.PROPOSAL_DECISIONS.approve) return applyProposal(tenantId, p.id, actorName(actor), "proposal " + p.id + " " + decision);
  db().run("UPDATE kb_proposals SET state=?, decided_by=? WHERE id=?", to, actorName(actor), p.id);
  return { [to]: p.id };
}
/* auto-evolving: a proposal lands by itself when its confidence and confirmations, and the entry's
   rating, meet the collection's thresholds — recorded as the engine's own change */
function maybeAutoApply(tenantId, pid) {
  const p = db().get("SELECT * FROM kb_proposals WHERE id=? AND state='open'", Number(pid)); if (!p) return null;
  const e = row(tenantId, p.entry_id), c = collection(tenantId, e.collection), m = modeOf(c.mode), t = c.thresholds;
  if (!m.autoApprove) return null;
  const rating = e.rating_n ? e.rating_sum / e.rating_n : null;
  const okConf = p.confidence != null && p.confidence >= t.minConfidence;
  const okConfirm = (p.confirmations || 0) >= t.minConfirmations;
  const okRating = e.rating_n >= t.minVotes && rating >= t.minRating;
  if (!(okConf && (okConfirm || okRating))) return null;
  return applyProposal(tenantId, p.id, "auto-evolving", "auto-applied: confidence " + p.confidence + ", " + (p.confirmations || 0) + " confirmations, rating " + (rating == null ? "—" : rating.toFixed(2)));
}
function confirmProposal(tenantId, pid) {
  db().run("UPDATE kb_proposals SET confirmations=confirmations+1 WHERE id=? AND tenant_id=? AND state='open'", Number(pid), Number(tenantId));
  return { applied: maybeAutoApply(tenantId, pid) };
}

/* ---------- feedback ---------- */
function feedback(tenantId, f, actor) {
  const x = f || {}, rating = Number(x.rating);
  if (!(rating >= 1 && rating <= 5)) throw httpErr("rating is 1 to 5", 400);
  const e = x.entry_id != null ? row(tenantId, x.entry_id) : null;
  if (x.entry_id != null && !e) throw httpErr("Not found", 404);
  db().run("INSERT INTO kb_feedback(tenant_id,entry_id,answer_ref,rating,correction,by_whom) VALUES(?,?,?,?,?,?)", Number(tenantId), e ? e.id : null, String(x.answer_ref || "").slice(0, 80) || null, rating, String(x.correction || "").slice(0, 4000) || null, actorName(actor));
  if (!e) return { ok: true };
  db().run("UPDATE kb_entries SET rating_sum=rating_sum+?, rating_n=rating_n+1 WHERE id=?", rating, e.id);
  const c = collection(tenantId, e.collection), m = modeOf(c.mode);
  /* a correction in a learning mode becomes a proposed revision of the entry */
  if (x.correction && m.learnFromFeedback) {
    const r = revise(tenantId, e.id, { body: e.body + "\n\nCorrection proposed from feedback: " + String(x.correction).slice(0, 2000), source: "learned", confidence: x.confidence }, actor, "learned from feedback");
    return { ok: true, proposed: r.proposal && r.proposal.id, applied: !!r.applied };
  }
  /* in auto-evolving mode a new rating can carry an open proposal over its threshold */
  const open = db().all("SELECT id FROM kb_proposals WHERE entry_id=? AND state='open'", e.id);
  const applied = open.map(p => maybeAutoApply(tenantId, p.id)).filter(Boolean);
  return { ok: true, applied: applied.length };
}

/* ---------- retrieval ---------- */
/* the approved entries that best answer a question and/or carry the given tags */
function search(tenantId, collectionKey, o) {
  const c = collection(tenantId, collectionKey), x = o || {};
  const limit = Math.max(1, Math.min(50, Number(x.limit) || c.searchLimit));
  const tags = cleanTags(x.tags), q = String(x.q || "").trim();
  const words = q.toLowerCase().match(/[\p{L}\p{N}]{2,}/gu) || [];
  let scored = [];
  if (words.length && fts()) {
    const match = words.map(w => '"' + w.replace(/"/g, "") + '"').join(" OR ");
    const hits = db().all("SELECT rowid id, bm25(kb_fts) s FROM kb_fts WHERE kb_fts MATCH ? ORDER BY s LIMIT 200", match);
    const ids = hits.map(h => h.id);
    const rows = ids.length ? db().all("SELECT * FROM kb_entries WHERE tenant_id=? AND collection=? AND status='approved' AND id IN (" + ids.map(() => "?").join(",") + ")", Number(tenantId), c.key, ...ids) : [];
    const bm = Object.fromEntries(hits.map(h => [h.id, -h.s]));
    scored = rows.map(r => ({ r, s: (bm[r.id] || 0) }));
  } else {
    const rows = db().all("SELECT * FROM kb_entries WHERE tenant_id=? AND collection=? AND status='approved' LIMIT 2000", Number(tenantId), c.key);
    scored = rows.map(r => { const text = (r.title + " " + r.body).toLowerCase(); return { r, s: words.reduce((n, w) => n + (text.includes(w) ? 1 : 0), 0) }; })
      .filter(x2 => !words.length || x2.s > 0);
  }
  if (tags.length) {
    scored = scored.map(x2 => { const have = J(x2.r.tags, []); const overlap = tags.filter(t => have.includes(t)).length; return { r: x2.r, s: x2.s + overlap * 10, overlap }; })
      .filter(x2 => x2.overlap > 0);
  }
  scored.sort((a, b) => b.s - a.s || ((b.r.rating_sum / (b.r.rating_n || 1)) - (a.r.rating_sum / (a.r.rating_n || 1))));
  return scored.slice(0, limit).map(x2 => Object.assign(view(x2.r), { score: +x2.s.toFixed(3) }));
}

/* ---------- who ---------- */
function actorName(a) { return a ? String(a.name || a.email || a.roleKey || SEED.AUTHORSHIP.other) : "system"; }
function isExpert(c, a) { return !!(a && (a.platform || (a.roleKey && c.expertRoles.includes(a.roleKey)))); }

module.exports = { MODES: SEED.MODES, STATUSES: SEED.STATUSES, collection, collections, saveCollection, addEntry, revise, review, rollback, history, entries,
  proposals, decideProposal, confirmProposal, feedback, search, isExpert };
