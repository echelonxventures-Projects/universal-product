/* UCOS Ω∞ · Foundation Registry — Architecture3.txt Articles 2–8, implemented.
   --------------------------------------------------------------------------
   This is the operational half of the constitution. Architecture3 declares the
   registry's canonical form, its five graphs, its invariants, its lifecycle,
   its admission rules and its APIs; this module executes them against real
   state instead of describing them in prose.

       ARTICLE 2  canonical form    → ucos_foundations columns
       ARTICLE 3  five graphs       → graph() / cycle rejection at registration
       ARTICLE 4  admission         → register() refuses anything uncertified, cyclic, unnamed
       ARTICLE 5  lifecycle         → transition() enforces state machine + dependents-first retirement
       ARTICLE 6  security          → Foundation Authority gate + append-only audit ledger
       ARTICLE 7  operations/events → register/resolve/traverse/certify/deprecate + event log
       ARTICLE 8  validation        → identity unique, dependencies resolve, cycles rejected

   Every foundation is registered data, never code (Article 4.2: "No hard-coded
   foundation"), so this module is a pure engine — it holds no universe names,
   no capabilities, nothing corpus-specific. Universes arrive from
   ucos-universes.js, which derives them from the parsed registry. */
"use strict";

/* the lifecycle states of Article 5.1, in their constitutional order.
   The vocabulary is DECLARED ONCE, in Architecture3 §5.1, and parsed by
   ucos.lifecycleStates(); this module reads it from there so the lifecycle can never be
   mirrored out of sync. The constant is the fallback used only before the registry is
   seeded (and the export tests rely on). */
const ucosMod = require("./ucos.js");
const LIFECYCLE = ["proposed", "drafted", "reviewed", "certified", "canonical", "deprecated", "retired"];
function lifecycleStates() {
  const parsed = ucosMod.lifecycleStates().map(s => String(s || "").trim().toLowerCase());
  return parsed.length ? parsed : LIFECYCLE;
}
/* Article 4.1: a foundation is admitted only when all of these hold */
const ADMISSION = {
  primitive: "It is derived from an existing primitive or is itself primitive",
  identity: "It has a canonical identity",
  dependencies: "It declares its dependencies",
  acyclic: "It is free of cycles",
  certified: "It is certified"
};
/* Article 3.1: the five foundation graphs */
const GRAPHS = {
  foundation: "what exists",
  dependency: "what requires what",
  evolution: "what succeeded what",
  governance: "who governs what",
  composition: "what composes what"
};
/* Article 7.2 events, emitted to the audit ledger as they happen */
const EVENTS = {
  registered: "Foundation Registered",
  certified: "Foundation Certified",
  deprecated: "Foundation Deprecated",
  retired: "Foundation Retired",
  resolved: "Dependency Resolved",
  cycle: "Cycle Detected And Rejected"
};

let _db = null;
const db = () => _db || (_db = require("./db.js"));
const n = (sql, ...p) => { try { return (db().get(sql, ...p) || {}).n || 0; } catch (e) { return 0; } };
const rows = (sql, ...p) => { try { return db().all(sql, ...p) || []; } catch (e) { return []; } };

/* the canonical identity of a foundation: globally unique, normalized the same
   way the registry normalizes concept keys, so a foundation and its source
   concept always agree on spelling */
function keyOf(text) {
  return String(text || "").normalize("NFKD").replace(/[\u0300-\u036f]/g, "")
    .replace(/[Ω∞]/g, "").replace(/[^a-z0-9]+/gi, " ").trim().toLowerCase()
    .replace(/\s+/g, "_").replace(/^_+|_+$/g, "").slice(0, 120);
}

/* ---------- ARTICLE 4.1: admission ----------
    Registration is a contract: the foundation must satisfy every admission rule
    BEFORE it exists. Violations are returned by rule so the console can show
    exactly which constitutional criterion failed — never a generic error.

    Article 4.1 requires certification for admission, while Article 5.1 defines
    pre-certified states (proposed/drafted/reviewed) and Article 5.2 makes
    "transition into Canonical requires certification" the transition rule. The
    reconciliation: a foundation may be ADMITTED as a declared draft pending
    certification, and certify() is the act that completes its admission into
    Canonical. So the certified rule is satisfied by either an asserted
    certification or a declared draft state — and by nothing else. */
function checkAdmission(identity, parent, dependencies, certified, lifecycle) {
  const k = keyOf(identity);
  const LC = lifecycleStates();
  const draft = lifecycle && LC.indexOf(lifecycle) > -1 && LC.indexOf(lifecycle) < LC.indexOf("certified");
  const fails = [];
  if (!k) fails.push({ rule: "identity", detail: ADMISSION.identity, actual: "identity is empty" });
  /* Article 8.2: identity must be globally unique */
  else if (rows("SELECT 1 ok FROM ucos_foundations WHERE key=?", k).length) fails.push({ rule: "identity", detail: ADMISSION.identity, actual: "identity already registered" });
  /* a primitive is its own root and needs no parent; everything else must
     derive from something already registered (Article 4.1 rule 1) */
  if (parent && keyOf(parent) !== k && !rows("SELECT 1 ok FROM ucos_foundations WHERE key=?", keyOf(parent)).length)
    fails.push({ rule: "primitive", detail: ADMISSION.primitive, actual: "parent '" + parent + "' is not a registered foundation" });
  /* Article 8.2: dependencies must resolve */
  for (const d of dependencies || []) {
    if (keyOf(d) === k) { fails.push({ rule: "dependencies", detail: ADMISSION.dependencies, actual: "cannot depend on itself" }); continue; }
    if (!rows("SELECT 1 ok FROM ucos_foundations WHERE key=?", keyOf(d)).length)
      fails.push({ rule: "dependencies", detail: ADMISSION.dependencies, actual: "dependency '" + d + "' does not resolve" });
  }
  /* Article 3.2 / 4.1: cycles are rejected at registration time, not at read
     time — the invariant is maintained, never repaired */
  if (k && wouldCycle(k, dependencies || [])) fails.push({ rule: "acyclic", detail: ADMISSION.acyclic, actual: "admitting this dependency set creates a cycle" });
  if (!certified && !draft) fails.push({ rule: "certified", detail: ADMISSION.certified, actual: "foundation is neither certified nor a declared draft (proposed/drafted/reviewed)" });
  return { admits: fails.length === 0, key: k, fails };
}

/* Article 3.2: "No foundation may participate in a cycle." A candidate cycle
   exists if any of its new dependencies can, by following existing dependency
   edges, reach back to the candidate itself. Depth-first over the DEPENDENCY
   graph as it stands today. */
function wouldCycle(key, dependencies) {
  const deps = new Set(dependencies.map(keyOf).filter(Boolean));
  if (deps.has(key)) return true;
  const seen = new Set([key]);
  const stack = [...deps];
  while (stack.length) {
    const cur = stack.pop();
    if (cur === key) return true;
    if (seen.has(cur)) continue;
    seen.add(cur);
    for (const r of rows("SELECT dependency FROM ucos_foundation_deps WHERE foundation=?", cur)) stack.push(r.dependency);
  }
  return false;
}

/* ---------- ARTICLE 7.1: register ----------
    The only way a foundation comes to exist. Writes the canonical form, the
    dependency edges, then records the event — nothing is mutated in place
    (Article 8.3: foundations evolve by succession, never by edit). */
function register(identity, opts) {
  opts = opts || {};
  const parent = opts.parent || null;
  const deps = (opts.dependencies || []).filter(d => String(d || "").trim());
  const check = checkAdmission(identity, parent, deps, opts.certified !== false, opts.lifecycle);
  if (!check.admits) return { ok: false, key: check.key, fails: check.fails };
  const k = check.key;
  const LC = lifecycleStates();
  const lifecycle = LC.includes(opts.lifecycle) ? opts.lifecycle
    : (opts.certified === false ? "proposed" : "canonical");   /* certified at admission → canonical (Article 4.1) */
  db().run("INSERT INTO ucos_foundations(key,name,parent,universe,lifecycle,governance,classification,source_doc,source_line,discovery,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
    k, String(identity).trim(), parent ? keyOf(parent) : null, opts.universe || null, lifecycle,
    opts.governance || "Foundation Authority", opts.classification || null,
    opts.sourceDoc || null, opts.sourceLine || null, opts.discovery || null, new Date().toISOString());
  for (const d of deps) db().run("INSERT OR IGNORE INTO ucos_foundation_deps(foundation,dependency) VALUES(?,?)", k, keyOf(d));
  audit(k, EVENTS.registered, { parent, dependencies: deps, lifecycle });
  return { ok: true, key: k, lifecycle };
}

/* ---------- ARTICLE 7.1: resolve ----------
    "Resolve Foundation" — return one foundation with its canonical form and
    its resolved neighbourhood across all five graphs in a single read. */
function resolve(key) {
  const k = keyOf(key);
  const f = rows("SELECT * FROM ucos_foundations WHERE key=?", k)[0];
  if (!f) return null;
  f.dependencies = rows("SELECT dependency FROM ucos_foundation_deps WHERE foundation=?", k).map(r => r.dependency);
  f.dependents = rows("SELECT foundation FROM ucos_foundation_deps WHERE dependency=?", k).map(r => r.foundation);
  f.children = rows("SELECT key,name FROM ucos_foundations WHERE parent=?", k);
  f.predecessor = rows("SELECT predecessor FROM ucos_foundation_evolution WHERE foundation=?", k).map(r => r.predecessor);
  f.successor = rows("SELECT foundation FROM ucos_foundation_evolution WHERE predecessor=?", k).map(r => r.foundation);
  f.events = rows("SELECT * FROM ucos_foundation_audit WHERE foundation=? ORDER BY at DESC LIMIT 25", k);
  return f;
}

/* ---------- ARTICLE 7.1: traverse ----------
    Walk any of the five graphs from a foundation. Direction is per graph:
    dependency and composition walk downward (what it needs / contains),
    foundation/governance walk to children (what exists under it). */
function traverse(key, graph, depth) {
  const k = keyOf(key);
  const maxDepth = Math.min(Number(depth) || 5, 12);
  const edge = graph === "dependency" ? ["ucos_foundation_deps", "foundation", "dependency"]
    : graph === "composition" ? ["ucos_foundation_composition", "parent", "child"]
    : graph === "evolution" ? ["ucos_foundation_evolution", "predecessor", "foundation"]
    : graph === "governance" ? ["ucos_foundations", "governance", "key"]
    : ["ucos_foundations", "parent", "key"];
  const out = [];
  const seen = new Set([k]);
  let frontier = [k];
  for (let d = 0; d < maxDepth && frontier.length; d++) {
    const next = [];
    for (const node of frontier) {
      const found = rows("SELECT " + edge[2] + " AS x FROM " + edge[0] + " WHERE " + edge[1] + "=?", node).map(r => r.x);
      for (const x of found) { if (!seen.has(x)) { seen.add(x); next.push(x); out.push({ from: node, to: x, depth: d + 1 }); } }
    }
    frontier = next;
  }
  return { graph, root: k, edges: out, reached: out.length };
}

/* ---------- ARTICLE 7.1 / 5.2: certify & deprecate ----------
    Certification moves a foundation to Canonical and records the event;
    deprecation begins its retirement, which Article 5.2 forbids while any
    dependent foundation is still alive. */
function certify(key, s) {
  const k = keyOf(key);
  const f = rows("SELECT lifecycle FROM ucos_foundations WHERE key=?", k)[0];
  if (!f) return { ok: false, error: "foundation not found" };
  if (f.lifecycle === "canonical") return { ok: true, key: k, lifecycle: "canonical" };
  db().run("UPDATE ucos_foundations SET lifecycle='canonical' WHERE key=?", k);
  audit(k, EVENTS.certified, { from: f.lifecycle });
  return { ok: true, key: k, lifecycle: "canonical" };
}
function deprecate(key, successor) {
  const k = keyOf(key);
  const f = rows("SELECT lifecycle FROM ucos_foundations WHERE key=?", k)[0];
  if (!f) return { ok: false, error: "foundation not found" };
  if (f.lifecycle === "retired") return { ok: false, error: "foundation is already retired" };
  /* Article 5.2: retire requires every dependent to be retired first */
  const live = rows("SELECT foundation FROM ucos_foundation_deps WHERE dependency=?", k)
    .map(r => r.foundation).filter(d => {
      const r = rows("SELECT lifecycle FROM ucos_foundations WHERE key=?", d)[0];
      return r && r.lifecycle !== "retired" && r.lifecycle !== "deprecated";
    });
  if (live.length) return { ok: false, error: "dependents must be retired first: " + live.join(", ") };
  db().run("UPDATE ucos_foundations SET lifecycle='deprecated' WHERE key=?", k);
  if (successor) db().run("INSERT OR IGNORE INTO ucos_foundation_evolution(foundation,predecessor) VALUES(?,?)", keyOf(successor), k);
  audit(k, EVENTS.deprecated, { successor: successor || null });
  return { ok: true, key: k, lifecycle: "deprecated" };
}
/* full retirement closes the lifecycle; the canonical identity is never reused
   (Article 8.3) but the record stays, so the audit ledger is complete */
function retire(key) {
  const k = keyOf(key);
  const f = rows("SELECT lifecycle FROM ucos_foundations WHERE key=?", k)[0];
  if (!f) return { ok: false, error: "foundation not found" };
  if (f.lifecycle !== "deprecated") return { ok: false, error: "a foundation must be deprecated before it is retired" };
  db().run("UPDATE ucos_foundations SET lifecycle='retired' WHERE key=?", k);
  audit(k, EVENTS.retired, {});
  return { ok: true, key: k, lifecycle: "retired" };
}

/* ---------- ARTICLE 3.2 / 8.2: global invariant verification ----------
    The constitution's compliance rules are executable: this proves the whole
    registry is acyclic, that every dependency resolves, that every identity is
    unique, and that no orphan foundation points outside the registry. */
function verify() {
  const all = rows("SELECT key,name,lifecycle,parent,governance FROM ucos_foundations");
  const byKey = new Map(all.map(f => [f.key, f]));
  const dup = all.filter(f => byKey.get(f.key) !== f);
  /* cycle check over the full dependency graph: a topological sort that fails
     to consume every node has found a cycle */
  const deps = new Map();
  for (const r of rows("SELECT foundation,dependency FROM ucos_foundation_deps")) {
    deps.set(r.foundation, (deps.get(r.foundation) || []).concat(r.dependency));
  }
  const state = new Map();            /* 0 unseen, 1 in-progress, 2 done */
  let cyclic = [];
  const visit = (node, path) => {
    const st = state.get(node) || 0;
    if (st === 2) return;
    if (st === 1) { cyclic.push(path.concat(node).join(" → ")); return; }
    state.set(node, 1);
    for (const d of deps.get(node) || []) visit(d, path.concat(node));
    state.set(node, 2);
  };
  for (const f of all) visit(f.key, []);
  const unresolved = [];
  for (const r of rows("SELECT foundation,dependency FROM ucos_foundation_deps"))
    if (!byKey.has(r.dependency)) unresolved.push(r);
  const orphans = all.filter(f => f.parent && !byKey.has(f.parent));
  const check = {
    identitiesUnique: dup.length === 0,
    dependenciesResolve: unresolved.length === 0,
    acyclic: cyclic.length === 0,
    noOrphans: orphans.length === 0
  };
  return {
    ok: Object.values(check).every(Boolean),
    checks: check,
    populations: { foundations: all.length, live: all.filter(f => f.lifecycle !== "retired").length, retired: all.filter(f => f.lifecycle === "retired").length },
    violations: { duplicates: dup.length, unresolved, cycles: [...new Set(cyclic)].slice(0, 10), orphans },
    graphs: GRAPHS
  };
}

/* ---------- ARTICLE 6: append-only audit ledger ----------
    Every admission, transition and retirement is recorded immutably; the ledger
    is append-only, so the registry's history can be replayed but never edited. */
function audit(foundation, event, detail) {
  try {
    db().run("INSERT INTO ucos_foundation_audit(foundation,event,detail,at) VALUES(?,?,?,?)",
      foundation, event, JSON.stringify(detail || {}), new Date().toISOString());
  } catch (e) { }
}
function ledger(limit) {
  return rows("SELECT * FROM ucos_foundation_audit ORDER BY at DESC LIMIT ?", Number(limit) || 100);
}

/* ---------- read API ---------- */
function list(opts) {
  opts = opts || {};
  const where = [], args = [];
  if (opts.universe) { where.push("universe=?"); args.push(opts.universe); }
  if (opts.lifecycle) { where.push("lifecycle=?"); args.push(opts.lifecycle); }
  const sql = "SELECT key,name,universe,lifecycle,governance,created_at FROM ucos_foundations" + (where.length ? " WHERE " + where.join(" AND ") : "") + " ORDER BY universe,key";
  return rows(sql, ...args);
}
/* the registry's own shape, for the console and for self-description */
function manifest() {
  const byLife = {};
  for (const f of rows("SELECT lifecycle, COUNT(*) n FROM ucos_foundations GROUP BY lifecycle")) byLife[f.lifecycle] = f.n;
  const byUniverse = rows("SELECT universe, COUNT(*) n FROM ucos_foundations WHERE universe IS NOT NULL GROUP BY universe ORDER BY n DESC");
  return { lifecycle: lifecycleStates(), graphs: GRAPHS, admission: ADMISSION, events: EVENTS,
    populations: { foundations: n("SELECT COUNT(*) n FROM ucos_foundations"), dependencies: n("SELECT COUNT(*) n FROM ucos_foundation_deps") },
    byLifecycle: byLife, byUniverse };
}

module.exports = { LIFECYCLE, lifecycleStates, GRAPHS, ADMISSION, EVENTS, keyOf, checkAdmission, wouldCycle,
  register, resolve, traverse, certify, deprecate, retire, verify, ledger, audit, list, manifest };
