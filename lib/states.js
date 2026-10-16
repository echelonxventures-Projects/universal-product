/* LUXORA Platform - the state-machine kernel: what a state MEANS and what entering it DOES.

   Engines used to branch on state names (`status === "paid"`, `if (to === "completed")`),
   so adding, renaming or re-sequencing a state meant editing every engine that named it. A
   state machine is now a registry row (stateMachines, seeded from lib/seed/states.json):

     states        the vocabulary — a registry list (list:<name>) or an inline array
     transitions   the legal moves — a registry list of "from>to" keys, a { from: [to…] } map,
                   a { from: to } sequence, or `free: true` (any move between known states);
                   "*" matches any state
     initial       the state a new record starts in
     clock         how a stamp is written: "sql" (YYYY-MM-DD HH:MM:SS, the default) or "iso"
     meta          per state: tags (what it MEANS — terminal, success, failure, rateable…) and
                   stamps ([{ col, once }] — time columns written on entering it)
     on            per transition ("from>to", "*>to", "from>*", "*>*"): guards and effects
                     { set: { col: value } }            write fields
                     { stamp: col, once: true }          write a time
                     { run: "<handler>", ...args }       call a handler the engine registered
                     { guard: "<handler>", ...args }     a handler that may refuse the move

   Engines ask meaning, never names: `is(machine, state, "rateable")`, `first(machine,
   "success")`, and run a move with `apply(machine, …)`. They register handlers by name
   (the engine's own vocabulary of side effects); which transition runs which handler is data. */
"use strict";

const registry = () => require("./registry.js");
const arr = v => Array.isArray(v) ? v : (v == null || v === "" ? [] : [v]);
const S = v => String(v == null ? "" : v);
const keyOf = x => S(x && typeof x === "object" ? x.key : x);

const SEED = (() => { try { const s = require("./seed/states.json"); const o = {}; for (const k of Object.keys(s)) if (!k.startsWith("$")) o[k] = s[k]; return o; } catch (e) { return {}; } })();
/* registry reads are remembered for one request only (the request's own context store), so
   an operator's edit is read on the very next call — never a stale enum */
const reqStore = () => { try { return require("./rules.js").current(); } catch (e) { return null; } };
function list(name) {
  const st = reqStore();
  const memo = st ? (st.stateLists = st.stateLists || new Map()) : null;
  if (memo && memo.has(name)) return memo.get(name);
  let v = null;
  try { const l = registry().list(name); if ((Array.isArray(l) && l.length) || (l && typeof l === "object" && !Array.isArray(l) && Object.keys(l).length)) v = l; } catch (e) { }
  v = v || SEED[name] || [];
  if (memo) memo.set(name, v);
  return v;
}
function bust() { const st = reqStore(); if (st && st.stateLists) st.stateLists.clear(); }

function machine(key) {
  const m = arr(list("stateMachines")).find(x => keyOf(x) === key);
  if (!m) throw new Error("Unknown state machine: " + key);
  return m;
}
/* a "list:<name>" reference or an inline value */
function resolve(ref) { return typeof ref === "string" && ref.startsWith("list:") ? list(ref.slice(5)) : ref; }
function vocab(key) { return arr(resolve(machine(key).states)).map(keyOf).filter(Boolean); }
function has(key, state) { return vocab(key).includes(S(state)); }
function metaOf(key, state) { const m = machine(key).meta || {}; return m[S(state)] || {}; }
function tags(key, state) { return arr(metaOf(key, state).tags).map(S); }
/* does this state MEAN this? */
function is(key, state, tag) { return tags(key, state).includes(S(tag)); }
/* every state that means this, and the first of them (the one an engine moves a record to) */
function tagged(key, tag) { return vocab(key).filter(s => is(key, s, tag)); }
function first(key, tag) { const t = tagged(key, tag); if (!t.length) throw new Error("State machine " + key + " declares no state tagged " + tag); return t[0]; }
function initial(key) { const m = machine(key); return S(m.initial || vocab(key)[0]); }

/* the legal moves, whatever shape the registry holds them in */
function moves(key) {
  const m = machine(key);
  if (m.free) return null;
  const t = resolve(m.transitions);
  const out = [];
  if (Array.isArray(t)) for (const x of t) { const k = keyOf(x); const i = k.indexOf(">"); if (i > 0) out.push([k.slice(0, i), k.slice(i + 1)]); }
  else if (t && typeof t === "object") for (const [from, to] of Object.entries(t)) for (const x of arr(to)) out.push([from, S(x)]);
  return out;
}
function can(key, from, to) {
  if (!has(key, to)) return false;
  const mv = moves(key);
  if (mv === null) return true;
  return mv.some(([f, t]) => (f === "*" || f === S(from)) && (t === "*" || t === S(to)));
}
function next(key, from) { const mv = moves(key); return mv === null ? vocab(key).filter(s => s !== S(from)) : mv.filter(([f]) => f === "*" || f === S(from)).map(([, t]) => t).filter(t => t !== "*"); }

function clock(key) { const c = machine(key).clock; const d = new Date(); return c === "iso" ? d.toISOString() : d.toISOString().slice(0, 19).replace("T", " "); }
/* the effects declared on this move, most general first ("*>*", "from>*", "*>to", "from>to") */
function onMove(key, from, to) {
  const on = machine(key).on || {};
  return ["*>*", S(from) + ">*", "*>" + S(to), S(from) + ">" + S(to)].filter((k, i, a) => a.indexOf(k) === i).flatMap(k => arr(on[k]));
}

/* named handlers, registered by the engine that owns the machine */
const HANDLERS = new Map();
function handle(key, name, fn) { HANDLERS.set(key + "." + name, fn); }

/* plan and run a move: validate, refuse if a guard does, build the patch (status column,
   declared stamps and sets), then run the declared handlers. The engine writes the patch to
   its own table — the kernel never assumes where a record lives. */
function apply(key, opts) {
  const o = opts || {};
  const m = machine(key);
  const from = S(o.from), to = S(o.to);
  if (!has(key, to)) throw new Error("Unknown " + S(m.name || key).toLowerCase() + " state: " + to);
  if (!o.force && from && !can(key, from, to)) throw new Error("Illegal transition: " + from + " → " + to + (next(key, from).length ? " (next: " + next(key, from).join(" / ") + ")" : ""));
  const row = o.row || {};
  const patch = { [m.column || "status"]: to };
  const now = clock(key);
  const ctx = { tenantId: o.tenantId, row, from, to, patch, extra: o.extra || {}, now };
  const effects = onMove(key, from, to);
  for (const e of effects.filter(e => e.guard)) {
    const fn = HANDLERS.get(key + "." + e.guard);
    if (!fn) throw new Error("State machine " + key + ": no guard handler " + e.guard);
    fn(ctx, e);
  }
  const stampCol = (col, once) => { if (once && (row[col] || patch[col])) return; patch[col] = now; };
  for (const s of arr(metaOf(key, to).stamps)) typeof s === "string" ? stampCol(s, false) : stampCol(s.col, !!s.once);
  for (const e of effects) {
    if (e.stamp) stampCol(e.stamp, !!e.once);
    if (e.set && typeof e.set === "object") for (const [c, v] of Object.entries(e.set)) if (!(e.once && (row[c] || patch[c]))) patch[c] = v === "$now" ? now : v;
  }
  const ran = [];
  for (const e of effects.filter(e => e.run)) {
    const fn = HANDLERS.get(key + "." + e.run);
    if (!fn) throw new Error("State machine " + key + ": no handler " + e.run);
    ran.push(e.run); fn(ctx, e);
  }
  return { patch, ran, from, to };
}

/* how a state shows: the label, icon and tone its row declares (the name, otherwise) */
function display(key, state) { const m = metaOf(key, state); return { key: S(state), label: S(m.label || state), icon: S(m.icon || ""), tone: S(m.tone || "") }; }
/* the legal moves with the names their registry rows give them ("Driver accepts") */
function labelledMoves(key) {
  const m = machine(key);
  const t = resolve(m.transitions);
  const names = {};
  if (Array.isArray(t)) for (const x of t) if (x && typeof x === "object" && x.name) names[keyOf(x)] = S(x.name);
  const mv = moves(key);
  return mv === null ? null : mv.map(([f, to]) => ({ from: f, to, label: names[f + ">" + to] || S((metaOf(key, to).label) || to) }));
}
/* what a console needs to ask by meaning: every machine's states (tags + display) and moves */
function catalog() {
  const out = {};
  for (const m of arr(list("stateMachines"))) {
    const k = keyOf(m);
    try { out[k] = { initial: initial(k), free: !!m.free, states: Object.fromEntries(vocab(k).map(s => [s, { tags: tags(k, s), ...display(k, s) }])), moves: labelledMoves(k) }; } catch (e) { }
  }
  return out;
}
/* the console's view of every machine */
function describe() {
  return arr(list("stateMachines")).map(m => {
    const k = keyOf(m);
    let states = []; try { states = vocab(k).map(s => ({ key: s, tags: tags(k, s), next: next(k, s) })); } catch (e) { }
    return { key: k, name: S(m.name || k), initial: S(m.initial || ""), free: !!m.free, states, on: m.on || {} };
  });
}

module.exports = { SEED, machine, vocab, has, tags, is, tagged, first, initial, moves, can, next, apply, handle, display, labelledMoves, catalog, describe, bust };
