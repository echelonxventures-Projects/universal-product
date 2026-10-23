/* LUXORA Platform — health records: the shopper's own vault.

   A shopper keeps their records (a prescription, a past report, a scan) and finds beside them what
   their orders delivered. A record is private: the shopper may share it with a party (a
   practitioner, a store) for a number of days and take it back — every share is recorded, and a
   party sees only what is shared with it while the share lasts. Capability: health_records. */
"use strict";

const db = () => require("./db.js");
const caps = () => require("./capabilities.js");
const fail = (msg, status) => Object.assign(new Error(msg), { status: status || 400 });
const sqlIn = days => new Date(Date.now() + Number(days) * 86400000).toISOString().slice(0, 19).replace("T", " ");
const sqlNow = () => new Date().toISOString().slice(0, 19).replace("T", " ");
function params(tid) {
  if (!caps().on(Number(tid), "health_records")) throw fail("Health records are not available in this store", 403);
  return caps().cap(Number(tid), "health_records");
}
function keep(tid, owner, input) {
  const P = params(tid);
  const i = input || {};
  const url = String(i.url || "").trim();
  if (!/^https?:\/\//i.test(url)) throw fail("Give a link to the file");
  const title = String(i.title || "").trim().slice(0, 120);
  if (!title) throw fail("Name the record");
  if (db().get("SELECT COUNT(*) n FROM vault_records WHERE tenant_id=? AND owner=?", Number(tid), String(owner)).n >= Number(P.vault_limit)) throw fail("Your vault is full");
  const r = db().run("INSERT INTO vault_records(tenant_id,owner,title,url,kind) VALUES(?,?,?,?,?)", Number(tid), String(owner), title, url.slice(0, 2000), String(i.kind || "").slice(0, 40));
  return db().get("SELECT * FROM vault_records WHERE id=?", r.lastInsertRowid);
}
function vault(tid, owner) {
  params(tid);
  return { delivered: require("./deliverables.js").mine(tid, owner),
    records: db().all("SELECT * FROM vault_records WHERE tenant_id=? AND owner=? ORDER BY id DESC", Number(tid), String(owner)),
    shares: db().all("SELECT * FROM vault_shares WHERE tenant_id=? AND owner=? ORDER BY id DESC", Number(tid), String(owner)) };
}
/* what a vault holds: whose an entry is, and what a party it is shared with is shown */
const VAULT = {
  record: { owns: (tid, owner, ref) => db().get("SELECT id FROM vault_records WHERE id=? AND tenant_id=? AND owner=?", ref, Number(tid), String(owner)), show: ref => db().get("SELECT title, url FROM vault_records WHERE id=?", ref) },
  deliverable: { owns: (tid, owner, ref) => db().get("SELECT id FROM deliverables WHERE id=? AND tenant_id=? AND owner=?", ref, Number(tid), String(owner)), show: ref => (x => x && { title: x.kind, url: x.value })(db().get("SELECT kind, value FROM deliverables WHERE id=?", ref)) }
};
/* shares a record (or a delivered item) with another party for some days; the share is recorded */
function share(tid, owner, input) {
  const P = params(tid);
  const i = input || {};
  const what = String(i.what || ""), ref = Number(i.ref);
  if (!VAULT[what] || !VAULT[what].owns(tid, owner, ref)) throw fail("Not in your vault", 404);
  const party = String(i.party || "").trim();
  if (!party) throw fail("Say who may see it");
  const days = Math.max(1, Math.min(Number(P.max_share_days), Number(i.days) || Number(P.max_share_days)));
  const r = db().run("INSERT INTO vault_shares(tenant_id,owner,what,ref,party,until) VALUES(?,?,?,?,?,?)", Number(tid), String(owner), what, ref, party.slice(0, 200), sqlIn(days));
  return db().get("SELECT * FROM vault_shares WHERE id=?", r.lastInsertRowid);
}
function unshare(tid, owner, id) {
  if (!db().run("UPDATE vault_shares SET until=? WHERE id=? AND tenant_id=? AND owner=?", sqlNow(), Number(id), Number(tid), String(owner)).changes) throw fail("Not your share", 404);
  return { ok: true };
}
/* what a party has been shown and may still see */
function sharedWith(tid, party) {
  params(tid);
  return db().all("SELECT * FROM vault_shares WHERE tenant_id=? AND party=? AND until>?", Number(tid), String(party), sqlNow()).map(s => ({ ...s, item: VAULT[s.what] ? VAULT[s.what].show(s.ref) : null }));
}

module.exports = { keep, vault, share, unshare, sharedWith };
