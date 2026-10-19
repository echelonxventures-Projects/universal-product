/* LUXORA Platform — the kernel's change lifecycle (FOUNDATIONS K09; owner Evolution).

   A CHANGE is a list of kernel operations written as data — create a node, record attributes,
   place it, give it a shape, assign a value — that moves through declared states: drafted,
   validated (a dry run that leaves nothing behind), previewed (the same dry run, answering
   questions about the result), approved (by someone other than its author when the lifecycle
   says so), published now or at a scheduled time, and rolled back. A published change occupies
   a range of the event log; rolling it back closes everything it recorded and reopens
   everything it superseded, so the past stays queryable and nothing is erased.

   A NODE's own state is separate: hide is reversible, delete is archive, and only an archived
   node can be purged — with a separate permission, leaving a tombstone event and no values.

   The states, transitions, operations' names and the purge permission are data
   (lib/seed/kernel.json → lifecycle). */
"use strict";

const { run, get, all } = require("./db.js");
const K = require("./kernel.js");
const S = require("./kernel-shape.js");
const C = require("./kernel-context.js");
const { tx, dryRun, append, fail, instant, nowIso, ns, nodeRow, J } = K.internal;
const L = K.SEED.lifecycle;
const EV = K.SEED.events;

let ready = false;
function ensureTables() {
  if (ready) return;
  K.ensureTables(); S.ensureTables(); C.ensureTables();
  run(`CREATE TABLE IF NOT EXISTS k_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, namespace TEXT NOT NULL, title TEXT NOT NULL, ops TEXT NOT NULL,
    state TEXT NOT NULL, author TEXT, approver TEXT, publish_at TEXT, seq_from INTEGER, seq_to INTEGER,
    rolled_back_seq INTEGER, result TEXT, report TEXT, created_at TEXT NOT NULL)`);
  run(`CREATE INDEX IF NOT EXISTS ix_k_changes_state ON k_changes(state, publish_at)`);
  run(`CREATE TABLE IF NOT EXISTS k_node_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT, node TEXT NOT NULL, state TEXT NOT NULL, rec_from INTEGER NOT NULL, rec_to INTEGER)`);
  run(`CREATE INDEX IF NOT EXISTS ix_k_node_states ON k_node_states(node, rec_to)`);
  ready = true;
}

/* ---------- operations: each name is declared in the seed; each runs one kernel call ---------- */
/* an argument "$n" (or "$n" inside a list or record) is the result of operation n of the same change */
const OPS = {
  defineKind: (a, by) => K.defineKind(a[0], by),
  createNode: (a, by) => K.createNode(a[0], a[1], by),
  record: (a, by) => K.record(a[0], a[1], a[2], by),
  assignIdentifier: (a, by) => K.assignIdentifier(a[0], a[1], a[2], a[3], by),
  endIdentifier: (a, by) => K.endIdentifier(a[0], a[1], a[2], a[3], by),
  defineHierarchy: (a, by) => K.defineHierarchy(a[0], by),
  place: (a, by) => K.place(a[0], a[1], a[2], a[3], by),
  endPlacement: (a, by) => K.endPlacement(a[0], a[1], a[2], a[3], a[4], by),
  defineSystem: (a, by) => S.defineSystem(a[0], by),
  setShape: (a, by) => S.setShape(a[0], a[1], a[2], a[3], by),
  declareSetting: (a, by) => C.declareSetting(a[0], by),
  assign: (a, by) => C.assign(a[0], a[1], a[2], by),
  defineResolution: (a, by) => C.defineResolution(a[0], by),
  defineView: (a, by) => C.defineView(a[0], by)
};
const DECLARED_OPS = new Set(L.operations);
const ref = (v, results) => {
  if (typeof v === "string" && /^\$\d+$/.test(v)) { const i = Number(v.slice(1)); if (!(i in results)) fail("Operation result " + v + " is not available yet"); return results[i]; }
  if (Array.isArray(v)) return v.map(x => ref(x, results));
  if (v && typeof v === "object") return Object.fromEntries(Object.entries(v).map(([k, x]) => [ref(k, results), ref(x, results)]));
  return v;
};
function apply(ops, actor) {
  const results = [];
  ops.forEach((o, i) => {
    try { results.push(OPS[o.op](ref(o.args || [], results), actor)); }
    catch (e) { fail(`Operation ${i} (${o.op}): ${e.message}`); }
  });
  return results;
}
function checkOps(ops) {
  if (!Array.isArray(ops) || !ops.length) fail("A change needs at least one operation");
  ops.forEach((o, i) => {
    if (!o || !DECLARED_OPS.has(o.op) || !OPS[o.op]) fail(`Operation ${i}: unknown operation ${o && o.op}`);
    if (o.args != null && !Array.isArray(o.args)) fail(`Operation ${i}: args is a list`);
  });
  return ops.map(o => ({ op: o.op, args: o.args || [] }));
}

/* ---------- the change record ---------- */
const row = id => { ensureTables(); const r = get("SELECT * FROM k_changes WHERE id=?", Number(id)); if (!r) fail("Unknown change: " + id); return r; };
const view = r => ({ id: r.id, namespace: r.namespace, title: r.title, ops: J(r.ops, []), state: r.state, author: r.author, approver: r.approver,
  publishAt: r.publish_at, seqFrom: r.seq_from, seqTo: r.seq_to, rolledBackSeq: r.rolled_back_seq, result: J(r.result, null), report: J(r.report, null), createdAt: r.created_at });
function move(r, to, set, actor) {
  const allowed = (L.transitions[r.state] || []).includes(to);
  if (!allowed) fail(`A change cannot go from ${r.state} to ${to}`);
  const cols = Object.keys(set || {});
  run(`UPDATE k_changes SET state=?${cols.map(c => `, ${c}=?`).join("")} WHERE id=?`, to, ...cols.map(c => set[c]), r.id);
  append(EV.changeMoved, { namespace: r.namespace, subject: "change:" + r.id, actor, payload: { from: r.state, to } });
}

function draft(d, actor) {
  ensureTables();
  d = d || {};
  const namespace = ns(d.namespace);
  const ops = checkOps(d.ops);
  return tx(() => {
    const r = run("INSERT INTO k_changes(namespace,title,ops,state,author,created_at) VALUES(?,?,?,?,?,?)",
      namespace, String(d.title || "").slice(0, 200) || L.untitled, JSON.stringify(ops), L.initial, actor || null, nowIso());
    const id = Number(r.lastInsertRowid);
    append(EV.changeDrafted, { namespace, subject: "change:" + id, actor, payload: { ops: ops.map(o => o.op) } });
    return id;
  });
}
function edit(id, ops, actor) {
  const r = row(id);
  if (r.state !== L.initial) fail("Only a " + L.initial + " change can be edited");
  const clean = checkOps(ops);
  return tx(() => { run("UPDATE k_changes SET ops=?, report=NULL WHERE id=?", JSON.stringify(clean), r.id); append(EV.changeEdited, { namespace: r.namespace, subject: "change:" + r.id, actor, payload: { ops: clean.map(o => o.op) } }); return view(row(id)); });
}
/* a dry run: every operation is applied in a transaction that is always undone */
function validate(id, actor) {
  const r = row(id);
  const out = dryRun(() => apply(J(r.ops, []), actor));
  const report = { ok: out.ok, error: out.error || null, at: nowIso() };
  tx(() => {
    run("UPDATE k_changes SET report=? WHERE id=?", JSON.stringify(report), r.id);
    if (out.ok && r.state === L.initial) move(r, L.validated, null, actor);
  });
  return report;
}
/* the same dry run, then a question asked of the result before it is undone:
   preview(id, results => K.attributes(results[0])) */
function preview(id, ask, actor) {
  const r = row(id);
  return dryRun(() => { const results = apply(J(r.ops, []), actor); return ask ? ask(results) : results; });
}
function approve(id, actor) {
  const r = row(id);
  if (L.distinctApprover && (!actor || actor === r.author)) fail("A change is approved by someone other than its author");
  const check = validate(id, actor);
  if (!check.ok) fail("The change no longer validates: " + check.error);
  return tx(() => { move(row(id), L.approved, { approver: actor }, actor); return view(row(id)); });
}
/* publish now, or schedule for a time; a scheduled change is published by publishDue */
function publish(id, o, actor) {
  o = o || {};
  const r = row(id);
  const when = instant(o.at, "at");
  if (when && when > nowIso()) return tx(() => { move(r, L.scheduled, { publish_at: when }, actor); return view(row(id)); });
  return tx(() => {
    const from = (get("SELECT MAX(seq) AS s FROM k_events") || {}).s || 0;
    const results = apply(J(r.ops, []), actor);
    move(row(id), L.published, { result: JSON.stringify(results), seq_from: from + 1 }, actor);
    const to = get("SELECT MAX(seq) AS s FROM k_events").s;
    run("UPDATE k_changes SET seq_to=? WHERE id=?", to, r.id);
    return view(row(id));
  });
}
function publishDue(now, actor) {
  ensureTables();
  const t = instant(now, "now") || nowIso();
  return all("SELECT id FROM k_changes WHERE state=? AND publish_at<=? ORDER BY publish_at, id", L.scheduled, t)
    .map(x => { try { return { id: x.id, ok: true, change: publish(x.id, {}, actor) }; } catch (e) { return { id: x.id, ok: false, error: e.message }; } });
}
function discard(id, actor) { const r = row(id); return tx(() => { move(r, L.discarded, null, actor); return view(row(id)); }); }

/* every kernel table with recorded time, and its columns other than id and the recorded interval
   (declared here rather than read from the engine, so the same code runs on every database) */
const RECORDED = {
  k_versions: ["node", "attrs", "valid_from", "valid_to"],
  k_identifiers: ["node", "scheme", "value", "valid_from", "valid_to"],
  k_placements: ["hierarchy", "node", "parent", "valid_from", "valid_to"],
  k_shapes: ["node", "system", "geom", "valid_from", "valid_to"],
  k_assignments: ["namespace", "setting", "scope", "value", "valid_from", "valid_to"],
  k_node_states: ["node", "state"],
  k_kinds: ["namespace", "kind", "owner", "spec"],
  k_hierarchies: ["namespace", "hierarchy", "owner", "spec"],
  k_coord_systems: ["namespace", "system", "owner", "spec"],
  k_declarations: ["family", "namespace", "name", "owner", "spec"]
};
/* rolls a published change back: what it recorded is closed, what it superseded is reopened.
   A row the change recorded may since have been closed by a later change and reinstated (as an
   identical open copy) when that later change was rolled back; the copy is the row's
   continuation. A row closed later and NOT reinstated means a later change built on this one:
   the rollback is refused — roll the later one back first. */
const same = (cols, x, y) => cols.every(c => x[c] === y[c]);
function rollback(id, actor) {
  const r = row(id);
  if (r.state !== L.published) fail("Only a published change can be rolled back");
  const a = r.seq_from, b = r.seq_to;
  return tx(() => {
    const close = [];
    for (const [t, cols] of Object.entries(RECORDED)) {
      for (const x of all(`SELECT * FROM ${t} WHERE rec_from>=? AND rec_from<=? AND rec_to IS NOT NULL AND rec_to>?`, a, b, b)) {
        const copy = all(`SELECT * FROM ${t} WHERE rec_from>? AND rec_to IS NULL`, b).find(y => same(cols, x, y));
        if (!copy) fail(`A later change built on this one (${t}); roll that back first`);
        close.push([t, copy.id]);
      }
    }
    const seq = append(EV.changeRolledBack, { namespace: r.namespace, subject: "change:" + r.id, actor, payload: { seqFrom: a, seqTo: b } });
    for (const [t, cols] of Object.entries(RECORDED)) {
      const reopen = all(`SELECT * FROM ${t} WHERE rec_to>=? AND rec_to<=? AND rec_from<?`, a, b, a);
      run(`UPDATE ${t} SET rec_to=? WHERE rec_from>=? AND rec_from<=? AND rec_to IS NULL`, seq, a, b);
      for (const x of reopen) run(`INSERT INTO ${t}(${cols.join(",")},rec_from) VALUES(${cols.map(() => "?").join(",")},?)`, ...cols.map(c => x[c]), seq);
    }
    for (const [t, rid] of close) run(`UPDATE ${t} SET rec_to=? WHERE id=?`, seq, rid);
    move(row(id), L.rolledBack, { rolled_back_seq: seq }, actor);
    return view(row(id));
  });
}
const change = id => view(row(id));
function changes(q) {
  ensureTables();
  q = q || {};
  return all(`SELECT * FROM k_changes ${q.state ? "WHERE state=?" : ""} ORDER BY id DESC LIMIT 500`, ...(q.state ? [q.state] : [])).map(view);
}

/* ---------- a node's own state: hide (reversible), archive, purge ---------- */
function nodeState(uid, o) {
  ensureTables();
  const b = K.internal.believed(K.internal.recordedSeq(o && o.recorded));
  const r = get(`SELECT state FROM k_node_states WHERE node=? AND ${b.sql}`, uid, ...b.args);
  return r ? r.state : L.nodeStates.initial;
}
function setNodeState(uid, to, actor) {
  ensureTables();
  const n = nodeRow(uid); if (!n) fail("Unknown node: " + uid);
  const from = nodeState(uid);
  if (!(L.nodeStates.transitions[from] || []).includes(to)) fail(`A node cannot go from ${from} to ${to}`);
  return tx(() => {
    const seq = append(EV.nodeStateChanged, { namespace: n.namespace, subject: uid, actor, payload: { from, to } });
    run("UPDATE k_node_states SET rec_to=? WHERE node=? AND rec_to IS NULL", seq, uid);
    run("INSERT INTO k_node_states(node,state,rec_from) VALUES(?,?,?)", uid, to, seq);
    return to;
  });
}
const hide = (uid, actor) => setNodeState(uid, L.nodeStates.hidden, actor);
const unhide = (uid, actor) => setNodeState(uid, L.nodeStates.initial, actor);
const archive = (uid, actor) => setNodeState(uid, L.nodeStates.archived, actor);
/* purge removes an archived node and every recorded fact about it; it needs the separate purge
   permission, and leaves one tombstone event naming only the node. The event log itself is
   never edited, so codes written in earlier events' payloads (identifier events) remain there. */
function purge(uid, grants, actor) {
  ensureTables();
  if (!(grants || []).includes(L.purgePermission)) fail("Purging needs the " + L.purgePermission + " permission");
  const n = nodeRow(uid); if (!n) fail("Unknown node: " + uid);
  if (nodeState(uid) !== L.nodeStates.archived) fail("Only an archived node can be purged");
  const held = get("SELECT COUNT(*) AS n FROM k_placements WHERE parent=? AND rec_to IS NULL", uid).n;
  if (held) fail("Other nodes still sit under this node; move or purge them first");
  return tx(() => {
    for (const t of ["k_versions", "k_identifiers", "k_placements", "k_shapes", "k_node_states"]) run(`DELETE FROM ${t} WHERE node=?`, uid);
    run("DELETE FROM k_assignments WHERE scope=?", uid);
    run("DELETE FROM k_nodes WHERE uid=?", uid);
    return append(EV.nodePurged, { namespace: n.namespace, subject: uid, actor, payload: {} });
  });
}

module.exports = { ensureTables, draft, edit, validate, preview, approve, publish, publishDue, discard, rollback, change, changes, nodeState, hide, unhide, archive, purge };
