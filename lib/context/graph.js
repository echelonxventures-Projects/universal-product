/* Context continuity · the typed traceability graph.
   --------------------------------------------------------------------------
   Edges are not authored separately: they are DERIVED from the fields records
   already carry (sources, dependsOn, affects, supersededBy, …), through the field
   map in schemas/relations.json. One fact, one place — a dependency written on a
   requirement IS the edge, so the two can never disagree.

   Every edge is checked: both endpoints exist, both kinds are allowed for the
   relation, and an acyclic relation has no cycle. A legitimate cycle needs the
   relation to be declared acyclic:false in the registry — never a silent skip.

   The queries walk the graph so a small agent can ask "what does X depend on"
   and get ids back, instead of loading the graph into its prompt. */
"use strict";

const { diag } = require("./store");

function getField(rec, dotted) {
  let v = rec;
  for (const p of dotted.split(".")) { if (v == null) return undefined; v = v[p]; }
  return v;
}
function refsOf(v) {
  if (v == null) return [];
  const arr = Array.isArray(v) ? v : [v];
  return arr.map(x => (x && typeof x === "object") ? x.ref : x).filter(x => typeof x === "string");
}

function build(K) {
  const edges = [];
  const diags = [];
  const seen = new Set();
  const R = K.relations.relations || {};
  for (const rel of Object.keys(R).sort()) {
    for (const f of R[rel].fields || []) {
      for (const n of K.nodes.values()) {
        if (f.kind !== "*" && f.kind !== n.kind) continue;
        for (const ref of refsOf(getField(n.rec, f.field))) {
          const from = f.reverse ? ref : n.id, to = f.reverse ? n.id : ref;
          const key = from + "|" + rel + "|" + to;
          if (seen.has(key)) continue;
          seen.add(key);
          edges.push({ from, rel, to, field: n.kind + "." + f.field, declaredOn: n.id });
        }
      }
    }
  }
  edges.sort((a, b) => (a.from + a.rel + a.to < b.from + b.rel + b.to ? -1 : 1));

  /* endpoint + kind validation */
  const kindOk = (allowed, kind) => !allowed || allowed.includes("*") || allowed.includes(kind);
  for (const e of edges) {
    const a = K.nodes.get(e.from), b = K.nodes.get(e.to);
    const missing = !a ? e.from : !b ? e.to : null;
    if (missing) {
      diags.push(diag("error", "broken-reference", e.declaredOn + " (" + e.field + ") references '" + missing + "', which does not exist", { id: e.declaredOn, remedy: "add the record, fix the id, or remove the reference" }));
      continue;
    }
    const r = R[e.rel];
    if (!kindOk(r.from, a.kind) || !kindOk(r.to, b.kind)) {
      diags.push(diag("error", "edge-kind", e.from + " (" + a.kind + ") -" + e.rel + "-> " + e.to + " (" + b.kind + ") is not allowed by relations.json", { id: e.declaredOn }));
    }
  }

  /* cycle detection per acyclic relation (iterative DFS, colour marking) */
  for (const rel of Object.keys(R).sort()) {
    if (!R[rel].acyclic) continue;
    const adj = new Map();
    for (const e of edges) if (e.rel === rel) { if (!adj.has(e.from)) adj.set(e.from, []); adj.get(e.from).push(e.to); }
    const colour = new Map();
    for (const start of [...adj.keys()].sort()) {
      if (colour.get(start)) continue;
      const stack = [[start, 0]], pathIds = [];
      colour.set(start, 1); pathIds.push(start);
      while (stack.length) {
        const top = stack[stack.length - 1];
        const next = (adj.get(top[0]) || [])[top[1]++];
        if (next === undefined) { colour.set(top[0], 2); stack.pop(); pathIds.pop(); continue; }
        const c = colour.get(next);
        if (c === 1) {
          const cyc = pathIds.slice(pathIds.indexOf(next)).concat(next);
          diags.push(diag("error", "cycle", "acyclic relation '" + rel + "' has a cycle: " + cyc.join(" → "), { remedy: "break the cycle, or declare the relation acyclic:false in schemas/relations.json with a reason" }));
        } else if (!c) { colour.set(next, 1); pathIds.push(next); stack.push([next, 0]); }
      }
    }
  }

  const out = new Map(), inc = new Map();
  for (const e of edges) {
    if (!out.has(e.from)) out.set(e.from, []); out.get(e.from).push(e);
    if (!inc.has(e.to)) inc.set(e.to, []); inc.get(e.to).push(e);
  }
  return { edges, diags, out: id => out.get(id) || [], in: id => inc.get(id) || [] };
}

/* transitive closure along the given relations (outgoing). Returns sorted ids,
   excluding the start node. Cycle-safe. */
function closure(G, start, rels, dir) {
  const seen = new Set([start]);
  const queue = [start];
  while (queue.length) {
    const id = queue.shift();
    const es = dir === "in" ? G.in(id) : G.out(id);
    for (const e of es) {
      if (rels && !rels.includes(e.rel)) continue;
      const nxt = dir === "in" ? e.from : e.to;
      if (!seen.has(nxt)) { seen.add(nxt); queue.push(nxt); }
    }
  }
  seen.delete(start);
  return [...seen].sort();
}

/* ---------- the named queries (CLI: context query <name> [arg]) ---------- */
function queries(K, G, extra) {
  extra = extra || {};
  const isActive = id => K.active(id);
  const kind = id => (K.nodes.get(id) || {}).kind;
  const ownerResolves = owner => !!owner && (K.nodes.has(owner) || require("./util").exists(K.root, owner.split("#")[0]));
  const Q = {
    /* every knowledge record and pack downstream of a source (or any node) */
    "affected-by": id => {
      const direct = G.in(id).filter(e => ["derived-from", "supports", "depends-on", "verifies", "implements"].includes(e.rel)).map(e => e.from);
      const all = new Set(direct);
      for (const d of direct) for (const x of closure(G, d, ["depends-on", "derived-from"], "in")) all.add(x);
      for (const x of [...all]) for (const e of G.out(x)) if (e.rel === "included-in") all.add(e.to);
      for (const e of G.out(id)) if (e.rel === "included-in") all.add(e.to);
      return [...all].sort().map(x => ({ id: x, kind: kind(x) }));
    },
    "decisions-for-task": id => {
      const t = K.nodes.get(id); if (!t) return [];
      const direct = (t.rec.decisions || []).slice();
      for (const r of t.rec.requirements || []) for (const e of G.in(r)) if (e.rel === "constrains" && kind(e.from) === "decision") direct.push(e.from);
      return [...new Set(direct)].sort().map(x => ({ id: x, status: (K.nodes.get(x) || { rec: {} }).rec.status }));
    },
    "prerequisites": id => closure(G, id, ["depends-on"]).map(x => ({ id: x, kind: kind(x) })),
    "tests-for": id => G.in(id).filter(e => e.rel === "verifies").map(e => ({ id: e.from, path: (K.nodes.get(e.from) || { rec: {} }).rec.path })),
    "active-without-owner": () => [...K.nodes.values()].filter(n => isActive(n.id) && ["requirement", "constraint", "artifact"].includes(n.kind) && !ownerResolves(n.rec.owner)).map(n => ({ id: n.id, owner: n.rec.owner || null })),
    "stale-contexts": () => (extra.packStatus || []).filter(p => !p.fresh).map(p => ({ id: p.id, reason: p.reason })),
    "requirements-lacking-implementation": () => K.of("requirement").filter(n => isActive(n.id) && !G.in(n.id).some(e => e.rel === "implements")).map(n => ({ id: n.id })),
    "requirements-lacking-verification": () => K.of("requirement").filter(n => isActive(n.id) && !G.in(n.id).some(e => e.rel === "verifies")).map(n => ({ id: n.id, method: n.rec.verification.method })),
    "superseded-in-active-contexts": () => {
      const out = [];
      for (const c of K.of("context")) {
        if (!isActive(c.id)) continue;
        for (const e of G.in(c.id)) if (e.rel === "included-in") {
          const n = K.nodes.get(e.from);
          if (n && ["superseded", "retired"].includes(n.rec.lifecycle)) out.push({ context: c.id, id: n.id, lifecycle: n.rec.lifecycle });
        }
      }
      return out;
    },
    "unaccounted-segments": () => (extra.coverage ? extra.coverage.unaccounted : []),
    "tasks-blocked-by-decisions": () => {
      const out = [];
      for (const t of K.of("task")) {
        if (["done", "abandoned"].includes(t.rec.state)) continue;
        const ds = (t.rec.decisions || []).filter(d => { const n = K.nodes.get(d); return n && n.rec.status === "proposed"; });
        const issues = G.in(t.id).filter(e => e.rel === "blocks").map(e => K.nodes.get(e.from)).filter(n => n && n.rec.status === "open").map(n => n.id);
        if (ds.length || issues.length) out.push({ task: t.id, unapprovedDecisions: ds, openBlockers: issues });
      }
      return out;
    }
  };
  return Q;
}

module.exports = { build, closure, queries };
