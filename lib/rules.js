/* LUXORA Platform - applicability rules: WHERE, FOR WHOM and FOR WHAT anything applies.

   One engine answers "may this subject be used in this context?" for every registered thing,
   and every engine that makes a choice asks it. This file is the kernel only — Rule, Decision,
   Context, Registry. It names no provider, country, service, segment, channel or subject
   type: every vocabulary is a registry row (meta_lists), seeded once from lib/seed/rules.json
   and edited in the console from then on.

     ruleSubjectTypes   what a rule can name, and the SOURCE its subjects are enumerated from
     ruleDimensions     what a rule can be scoped by: the fact it reads, how it matches, where
                        the fact comes from (the platform's row, the request, a binding, a
                        computed provider), and the source of its options
     ruleBindings       the decision points engines call by name: which subject type a point
                        chooses, the facts it sets (its service…), the checks a guarded entry
                        point runs and which input fields feed which facts
     services · segments · channels · banks · bankIdentifiers · countryGroups · paymentMethods

   A rule  = subject (type + id, or "*") + scope (any dimension; empty = any; plus an amount
             range and a date window) + effect (allow · deny · prefer) + priority + params.
   Decision, per layer: the most specific matching rule wins (a named subject beats "*", then
   more dimensions); at a tie deny wins. A subject with allow rules is allow-listed. A context
   that does not know a fact is optimistic for allow rules and never fires a deny on it.
   Layers: the platform owner's rules (tenant_id NULL) bound every platform; a platform's own
   rules can only narrow inside them — both must permit.

   Sources, one grammar for subjects and dimension options, joined with "+":
     list:<registry list> · rows:<table>:<id>:<label>[:<col>=<value>]
     values:<table>:<json column>[.<path>][:<col>=<value>] · entity:<Data Studio entity> */
"use strict";

const { AsyncLocalStorage } = require("async_hooks");
const db = () => require("./db.js");
const registry = () => require("./registry.js");
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };
const arr = v => Array.isArray(v) ? v : (v == null || v === "" ? [] : [v]);
const S = v => String(v == null ? "" : v);
const EFFECTS = ["allow", "deny", "prefer"];

/* the seed: registry rows on first boot (lib/registry.js), never read at decision time
   except as the fallback for a list the registry does not hold yet */
const SEED = (() => { try { const s = require("./seed/rules.json"); const o = {}; for (const k of Object.keys(s)) if (!k.startsWith("$")) o[k] = s[k]; return o; } catch (e) { return {}; } })();
const LISTS = SEED;

const TTL = 5000;
/* the vocabularies are remembered for one request only (the request's context store), so a
   console edit is read on the very next call */
const LIST_CACHE = { clear() { } };
function list(name) {
  const st = als.getStore();
  const memo = st ? (st.ruleLists = st.ruleLists || new Map()) : null;
  if (memo && memo.has(name)) return memo.get(name);
  let v = null;
  try { const l = registry().list(name); if (Array.isArray(l) && l.length) v = l; } catch (e) { }
  v = v || SEED[name] || [];
  if (memo) memo.set(name, v);
  return v;
}
const keyOf = x => S(x && typeof x === "object" ? x.key : x);
const dims = () => list("ruleDimensions");
const typeRow = key => list("ruleSubjectTypes").find(x => keyOf(x) === key) || null;
const binding = key => list("ruleBindings").find(x => keyOf(x) === key) || null;
/* a dimension a platform's own rules may not use: a fact of the platform itself that no
   request can change (its kind, its identity) */
const platformOnly = d => d.source === "platform" && !d.overridable;
/* a fact that can differ between buyers of one platform */
const buyerDim = d => d.source !== "platform" || !!d.overridable;
const norm1 = (d, v) => d && d.upper ? S(v).toUpperCase() : v;

/* ---------------- storage + cache ---------------- */
let CACHE = null;
/* a rule change reaches every cached answer at once: the settings snapshot caches the
   platform-level capability decisions, so it is dropped for every platform too */
function bust() { CACHE = null; FACTS.clear(); LIST_CACHE.clear(); try { require("./settings.js").bust(); } catch (e) { } }
function rows() {
  if (CACHE && Date.now() - CACHE.at < TTL) return CACHE.rows;
  let raw = [];
  try { raw = db().all("SELECT * FROM applicability_rules WHERE active=1 ORDER BY id"); } catch (e) { raw = []; }
  const out = raw.map(normRow);
  CACHE = { at: Date.now(), rows: out, buyerTypes: new Set(out.filter(buyerScoped).map(r => r.subject_type)) };
  return out;
}
function normRow(r) {
  const scope = J(r.scope, {}) || {};
  return { id: r.id, tenant_id: r.tenant_id == null ? null : Number(r.tenant_id), subject_type: S(r.subject_type), subject: S(r.subject || "*"),
    effect: EFFECTS.includes(r.effect) ? r.effect : "allow", priority: Number(r.priority) || 0, scope, params: J(r.params, {}) || {},
    note: S(r.note), active: r.active == null ? 1 : Number(r.active), created_by: r.created_by || null, created_at: r.created_at, updated_at: r.updated_at };
}
/* a rule that depends on who is buying — it can only decide once a buyer context exists */
function buyerScoped(r) {
  const sc = r.scope || {};
  if (sc.min_amount != null || sc.max_amount != null) return true;
  return dims().some(d => buyerDim(d) && arr(sc[d.key]).length);
}

/* ---------------- request context (the buyer behind this request) ---------------- */
const als = new AsyncLocalStorage();
function run(store, fn) { return als.run(store || {}, fn); }
function current() { return als.getStore() || null; }

/* the platform's own facts, as its dimensions declare them: a setting the platform saved
   (read from the settings table directly — the settings snapshot itself asks this engine),
   else a column of its tenant row, else a value derived from another fact through a lookup.
   Remembered for one request only, so an edit is seen at once. */
const IDENT = /^[A-Za-z_][A-Za-z0-9_]{0,63}$/;
const FACTS = { clear() { } };
function settingOf(tid, spec) {
  const [key, ...path] = S(spec).split(".");
  if (!key) return undefined;
  try {
    const r = db().get("SELECT value FROM settings WHERE tenant_id=? AND key=?", tid, key);
    let v = r ? J(r.value, null) : null;
    for (const p of path) v = v && typeof v === "object" ? v[p] : undefined;
    return v === null || v === "" ? undefined : v;
  } catch (e) { return undefined; }
}
/* a platform fact the kernel answers, named by a platform dimension's `provider` */
const PLATFORM_FACTS = {
  /* the country of the store's jurisdiction (lib/stores.js) */
  jurisdiction: tid => require("./stores.js").country(tid)
};
function platformFacts(tenantId) {
  const tid = Number(tenantId) || 0;
  if (!tid) return {};
  const st = current();
  if (st && st.facts && st.facts[tid]) return st.facts[tid];
  let t = null; try { t = db().get("SELECT * FROM tenants WHERE id=?", tid); } catch (e) { }
  const f = { tenant_id: tid };
  if (t) {
    const ds = dims().filter(d => d.source === "platform");
    for (const d of ds) {
      const v = d.provider && PLATFORM_FACTS[d.provider] ? PLATFORM_FACTS[d.provider](tid) : d.setting ? settingOf(tid, d.setting) : undefined;
      if (v !== undefined) f[d.fact] = norm1(d, v);
      else if (d.column && t[d.column] != null && t[d.column] !== "") f[d.fact] = norm1(d, t[d.column]);
    }
    for (const d of ds.filter(d => d.derive && f[d.fact] === undefined)) {
      const x = d.derive;
      if (![x.table, x.key, x.value].every(v => IDENT.test(S(v))) || f[x.from] == null) continue;
      try { const r = db().get("SELECT " + x.value + " v FROM " + x.table + " WHERE " + x.key + "=?", f[x.from]); if (r && r.v != null) f[d.fact] = norm1(d, r.v); } catch (e) { }
    }
  }
  if (st) (st.facts = st.facts || {})[tid] = f;
  return f;
}
/* computed facts: each is a provider the kernel knows how to compute, named by a dimension */
const PROVIDERS = {
  /* explicit memberships, the automatic ones the segments registry declares, and the offers
     engine's computed audiences (new / returning / high value …) */
  segments(tenantId, owner) {
    const out = new Set();
    const signed = /:u:\d+$/.test(S(owner));
    for (const sg of list("segments")) {
      if (sg && sg.auto === "guest" && owner && !signed) out.add(sg.key);
      if (sg && sg.auto === "signed_in" && signed) out.add(sg.key);
    }
    if (owner) {
      try { for (const r of db().all("SELECT segment FROM segment_members WHERE tenant_id=? AND owner=?", Number(tenantId), S(owner))) out.add(r.segment); } catch (e) { }
      try {
        const o = db().get("SELECT COUNT(*) n, COALESCE(SUM(total),0) v FROM orders WHERE tenant_id=? AND owner=?", Number(tenantId), S(owner)) || {};
        for (const k of require("./goip.js").personalize(Number(tenantId), owner, { orders: o.n || 0, lifetime: o.v || 0 })) out.add(k);
      } catch (e) { }
    }
    return [...out];
  }
};
function segmentsOf(tenantId, owner) { return PROVIDERS.segments(tenantId, owner); }
/* the facts a request may state: request-sourced and overridable dimensions (never the
   platform's identity, never a computed fact such as a buyer's segments) */
/* a dimension that declares no source is an operator's own, stated by the request */
const requestable = d => !d.source || d.source === "request" || !!d.overridable;
function fromRequest(st, d) {
  const hdr = st.req && st.req.headers ? st.req.headers : {};
  const bctx = st.body && typeof st.body === "object" && st.body.context && typeof st.body.context === "object" ? st.body.context : {};
  const k = S(d.fact);
  let v = bctx[k] != null ? bctx[k] : (hdr[S(d.header || ("x-ctx-" + k)).toLowerCase()] || (st.url && st.url.searchParams ? st.url.searchParams.get("ctx_" + k) : null));
  if (v == null || v === "") return undefined;
  v = Array.isArray(v) ? v.map(S) : S(v).slice(0, 120);
  const opts = d.options ? dimensionOptions(d) : [];
  if (opts.length && !Array.isArray(v)) { const o = opts.find(o => S(o.key).toLowerCase() === S(v).toLowerCase()); if (!o) return undefined; v = o.key; }
  return norm1(d, v);
}
/* buyer facts from the current request, when it is a shopper's (not staff, not the platform) */
function buyerFacts(tenantId) {
  const st = current();
  if (!st || !st.s) return {};
  const s = st.s;
  if (s.platform_admin || st.staff) return {};
  if (s.tenant && Number(s.tenant.id) !== Number(tenantId)) return {};
  const f = {};
  const owner = s.user_id ? `t${tenantId}:u:${s.user_id}` : (s.sid ? `t${tenantId}:s:${s.sid}` : "");
  for (const d of dims()) {
    if (requestable(d)) {
      const v = fromRequest(st, d);
      if (v !== undefined) f[d.fact] = v;
      else if (d.default === "first") { const o = dimensionOptions(d)[0]; if (o) f[d.fact] = o.key; }
    }
    if (d.source === "computed" && PROVIDERS[d.provider]) {
      const prov = PROVIDERS[d.provider], k = d.fact;
      Object.defineProperty(f, k, { enumerable: true, configurable: true, get() { const v = prov(tenantId, owner); Object.defineProperty(this, k, { value: v, enumerable: true, configurable: true }); return v; } });
    }
  }
  return f;
}
/* the full context a decision is made in. `extra` wins over everything (an explicit country,
   amount…); `buyer: false` evaluates the platform alone (cached settings, menus). */
function context(tenantId, extra) {
  const x = extra || {};
  const ctx = { ...platformFacts(tenantId) };
  if (x.buyer !== false) {
    const b = buyerFacts(tenantId);
    for (const k of Object.keys(b)) Object.defineProperty(ctx, k, Object.getOwnPropertyDescriptor(b, k));
  }
  const byFact = Object.fromEntries(dims().map(d => [d.fact, d]));
  for (const [k, v] of Object.entries(x)) if (k !== "buyer" && v !== undefined && v !== null && v !== "") ctx[k] = norm1(byFact[k], v);
  if (!ctx.at) ctx.at = new Date().toISOString();
  return ctx;
}
/* what a caller outside the console may state about the context (the generic check API) */
function requestFacts(raw) {
  const out = {};
  const c = raw && typeof raw === "object" ? raw : {};
  for (const d of dims()) if ((requestable(d) || d.source === "binding") && c[d.fact] != null && c[d.fact] !== "") out[d.fact] = c[d.fact];
  if (c.amount != null && c.amount !== "" && isFinite(Number(c.amount))) out.amount = Number(c.amount);
  if (c.at) out.at = S(c.at);
  return out;
}

/* ---------------- matching ---------------- */
function groupMembers(d, key) { const g = list(d.groups).find(x => keyOf(x).toUpperCase() === S(key).toUpperCase()); return g ? arr(g.countries || g.members).map(c => S(c).toUpperCase()) : null; }
/* "yes" · "no" · "maybe" (the context does not know this fact) */
function dimMatch(d, want, fact) {
  if (!want.length) return "yes";
  if (fact === undefined || fact === null || fact === "") return "maybe";
  const W = want.map(S);
  switch (d.match) {
    case "any": { const have = arr(fact).map(S); return W.some(w => have.includes(w)) ? "yes" : "no"; }
    case "prefix": { const f = S(fact).toUpperCase(); return W.some(w => f === w.toUpperCase() || f.startsWith(w.toUpperCase() + ".") || f.startsWith(w.toUpperCase() + "-")) ? "yes" : "no"; }
    case "group": { const f = S(fact).toUpperCase(); return W.some(w => w.toUpperCase() === f || (groupMembers(d, w) || []).includes(f)) ? "yes" : "no"; }
    default: return W.map(w => w.toLowerCase()).includes(S(fact).toLowerCase()) ? "yes" : "no";
  }
}
function amountIn(sc, ctx) {
  if (sc.min_amount == null && sc.max_amount == null) return "yes";
  if (ctx.amount == null || ctx.amount === "") return "maybe";
  let amt = Number(ctx.amount);
  const cur = S(sc.amount_currency).toUpperCase();
  if (cur && ctx.currency && cur !== S(ctx.currency).toUpperCase()) { try { amt = amt * registry().fxTo(ctx.currency, cur); } catch (e) { } }
  if (sc.min_amount != null && sc.min_amount !== "" && amt < Number(sc.min_amount)) return "no";
  if (sc.max_amount != null && sc.max_amount !== "" && amt > Number(sc.max_amount)) return "no";
  return "yes";
}
function windowIn(sc, ctx) {
  const at = S(ctx.at).slice(0, 19);
  if (sc.from && at < S(sc.from).slice(0, 19)) return "no";
  if (sc.to && at > (S(sc.to).length <= 10 ? S(sc.to) + "T23:59:59" : S(sc.to).slice(0, 19))) return "no";
  return "yes";
}
function match(rule, ctx) {
  const sc = rule.scope || {};
  let out = "yes";
  const fold = r => { if (r === "no") out = "no"; else if (r === "maybe" && out === "yes") out = "maybe"; };
  /* a fact is read only when the rule constrains it — a computed fact costs a lookup */
  for (const d of dims()) { const want = arr(sc[d.key]); if (!want.length) continue; fold(dimMatch(d, want, ctx[d.fact])); if (out === "no") return out; }
  fold(amountIn(sc, ctx)); if (out === "no") return out;
  fold(windowIn(sc, ctx));
  return out;
}
function specificity(rule) {
  const sc = rule.scope || {};
  let n = rule.subject === "*" ? 0 : 100;
  for (const d of dims()) if (arr(sc[d.key]).length) n++;
  if (sc.min_amount != null || sc.max_amount != null) n++;
  if (sc.from || sc.to) n++;
  return n;
}
function describe(rule) {
  const sc = rule.scope || {}; const bits = [];
  for (const d of dims()) if (arr(sc[d.key]).length) bits.push(S(d.name).toLowerCase() + " " + arr(sc[d.key]).join("/"));
  if (sc.min_amount != null && sc.min_amount !== "") bits.push("amount ≥ " + sc.min_amount + (sc.amount_currency ? " " + sc.amount_currency : ""));
  if (sc.max_amount != null && sc.max_amount !== "") bits.push("amount ≤ " + sc.max_amount + (sc.amount_currency ? " " + sc.amount_currency : ""));
  if (sc.from) bits.push("from " + sc.from); if (sc.to) bits.push("until " + sc.to);
  return "#" + rule.id + " " + rule.effect + " " + (rule.subject === "*" ? "every " + rule.subject_type : rule.subject) + (bits.length ? " · " + bits.join(" · ") : " · everywhere");
}

/* one layer's verdict for one subject */
const OPEN_LAYER = () => ({ ok: true, open: true, matched: [], params: {}, priority: 0, reasons: [] });
function layer(rules, type, id, ctx, label) {
  const mine = rules.filter(r => r.subject_type === type && (r.subject === "*" || r.subject === S(id)));
  if (!mine.length) return OPEN_LAYER();
  const scored = mine.map(r => ({ r, m: match(r, ctx), sp: specificity(r) }));
  const yes = scored.filter(x => x.m === "yes").sort((a, b) => b.sp - a.sp || (a.r.effect === "deny" ? -1 : 1) - (b.r.effect === "deny" ? -1 : 1));
  const params = {}; let priority = 0;
  for (const x of yes.slice().reverse()) if (x.r.effect !== "deny") Object.assign(params, x.r.params || {});
  for (const x of yes) if (x.r.effect === "prefer") priority = Math.max(priority, x.r.priority || 0);
  if (yes.length) {
    const top = yes[0];
    if (top.r.effect === "deny") return { ok: false, matched: [top.r.id], params: {}, priority: 0, reasons: [label + " " + describe(top.r)] };
    return { ok: true, matched: yes.filter(x => x.r.effect !== "deny").map(x => x.r.id), params, priority, reasons: [label + " " + describe(top.r)] };
  }
  const allows = scored.filter(x => x.r.effect !== "deny");
  if (!allows.length) return OPEN_LAYER();
  const maybe = allows.filter(x => x.m === "maybe");
  if (maybe.length) return { ok: true, conditional: true, matched: maybe.map(x => x.r.id), params: {}, priority: 0, reasons: [label + " depends on " + describe(maybe[0].r)] };
  return { ok: false, matched: [], params: {}, priority: 0, reasons: [label + " outside every allow rule: " + allows.map(x => describe(x.r)).join("; ")] };
}
/* THE question */
function decide(type, id, ctx) {
  const c = ctx || {};
  const all = rows();
  if (!type || !all.some(r => r.subject_type === type)) return { ok: true, verdict: "open", reasons: [], matched: [], params: {}, priority: 0 };
  const plat = layer(all.filter(r => r.tenant_id == null), type, id, c, "platform rule");
  const own = c.tenant_id ? layer(all.filter(r => r.tenant_id === Number(c.tenant_id)), type, id, c, "this platform's rule") : OPEN_LAYER();
  const ok = plat.ok && own.ok;
  return {
    ok, verdict: !ok ? "blocked" : (plat.conditional || own.conditional) ? "conditional" : (plat.open && own.open) ? "open" : "allowed",
    reasons: [...plat.reasons, ...own.reasons], matched: [...plat.matched, ...own.matched],
    params: ok ? { ...plat.params, ...own.params } : {}, priority: ok ? Math.max(plat.priority, own.priority) : 0
  };
}
function permits(type, id, ctx) { return decide(type, id, ctx).ok; }
function filter(type, items, ctx, idOf) {
  const f = idOf || (x => (x && typeof x === "object" ? x.id : x));
  return (items || []).map((it, i) => ({ it, i, d: decide(type, f(it), ctx) })).filter(x => x.d.ok)
    .sort((a, b) => b.d.priority - a.d.priority || a.i - b.i).map(x => ({ it: x.it, d: x.d }));
}
function label(type) { const t = typeRow(type); return t ? S(t.name) : type; }

/* ---------------- binding points: how an engine asks without naming anything ----------------
   An engine names only its own decision point ("checkout.gateways", "fintech.payout"); the
   ruleBindings row says what that point decides (a subject type, maybe a fixed subject), the
   facts it sets (its service…), and for a guarded entry point the checks it runs and which of
   the caller's input fields feed which facts. An unbound point is open. */
function at(point, tenantId, extra) {
  const b = binding(point) || {};
  return context(tenantId, { ...(b.facts || {}), ...(extra || {}) });
}
function decideAt(point, id, ctx) {
  const b = binding(point);
  if (!b || !b.subject_type) return { ok: true, verdict: "open", reasons: [], matched: [], params: {}, priority: 0 };
  return decide(b.subject_type, id !== undefined && id !== null ? id : b.subject, ctx);
}
function permitsAt(point, id, ctx) { return decideAt(point, id, ctx).ok; }
function filterAt(point, items, ctx) {
  const b = binding(point);
  if (!b || !b.subject_type) return (items || []).map(it => ({ it, d: { ok: true, verdict: "open", reasons: [], params: {}, priority: 0 } }));
  const idf = b.id || "id";
  return filter(b.subject_type, items, ctx, x => (x && typeof x === "object" ? x[idf] : x));
}
/* a rule's params onto the item an engine offers: the subject type maps a param to the
   item's field (fee_pct → feePct); a param that already names a field applies as itself */
function applyParams(point, item, params) {
  const b = binding(point); const t = b ? typeRow(b.subject_type) : null;
  const map = (t && t.params) || {};
  const out = { ...item };
  for (const [k, v] of Object.entries(params || {})) {
    const field = map[k] || (Object.prototype.hasOwnProperty.call(item, k) ? k : null);
    if (!field) continue;
    const cur = item[field];
    if (typeof cur === "number" || (cur == null && v !== "" && isFinite(Number(v)) && typeof v !== "object")) { if (isFinite(Number(v))) out[field] = Number(v); }
    else if (Array.isArray(cur) && Array.isArray(v)) out[field] = v.map(n => (isFinite(Number(n)) ? Number(n) : n));
    else out[field] = v;
  }
  return out;
}
/* a binding may exempt roles (a platform's own staff are never locked out of their console
   by a customer-facing rule) */
function exempt(point, role) { const b = binding(point); return !!(b && arr(b.exemptRoles).includes(S(role))); }
/* the input field(s) a binding names, "a|b" taking the first present */
function pick(input, spec) { for (const f of S(spec).split("|").filter(Boolean)) { const v = input[f]; if (v !== undefined && v !== null && v !== "") return v; } return undefined; }
const RESOLVERS = { bank: input => bankOf(input) };
/* a guarded entry point: throws (status 403) when its service or an instrument it would use
   is not permitted; the API wrappers report the reason */
function guardAt(point, tenantId, input) {
  const b = binding(point);
  const i = input || {};
  const extra = {};
  for (const [fact, spec] of Object.entries((b && b.inputs) || {})) { const v = pick(i, spec); if (v !== undefined) extra[fact] = fact === "amount" ? Number(v) : v; }
  const ctx = at(point, tenantId, extra);
  if (!b) return ctx;
  for (const c of arr(b.checks)) {
    if (c.when && (i[c.when] == null || i[c.when] === "")) continue;
    if (c.unless && i[c.unless] != null && i[c.unless] !== "") continue;
    let id = c.value !== undefined ? c.value : c.resolve && RESOLVERS[c.resolve] ? RESOLVERS[c.resolve](i) : c.from ? pick(i, c.from) : undefined;
    if ((id === undefined || id === null || id === "") && c.default !== undefined) id = c.default;
    if (id === undefined || id === null || id === "") continue;
    const d = decide(c.type, S(id), ctx);
    if (!d.ok) { const e = new Error(label(c.type) + " " + id + " is not available here — " + d.reasons.join("; ")); e.status = 403; e.rule = d; throw e; }
  }
  return ctx;
}
/* does any rule on this point's subject type depend on the buyer? (lets hot paths skip work) */
function contextualAt(point) { rows(); const b = binding(point); return !!(b && CACHE && CACHE.buyerTypes.has(b.subject_type)); }

/* a bank from its key, or recognised from any registered identifier (IFSC, SWIFT …) */
function bankOf(input) {
  const i = input || {};
  const banks = list("banks");
  if (i.bank) { const k = S(i.bank).toLowerCase(); const b = banks.find(x => keyOf(x).toLowerCase() === k); if (b) return keyOf(b); }
  for (const idf of list("bankIdentifiers")) {
    const names = [keyOf(idf)].concat(arr(idf.aliases));
    const raw = names.map(n => i[n]).find(v => v != null && v !== "");
    if (!raw) continue;
    const pre = S(raw).toUpperCase().slice(0, Number(idf.length) || 4);
    const b = banks.find(x => x[keyOf(idf)] && S(x[keyOf(idf)]).toUpperCase() === pre);
    if (b) return keyOf(b);
  }
  return i.bank ? S(i.bank).toLowerCase() : null;
}

/* ---------------- sources: what a rule can name, and a dimension's options ---------------- */
function whereOf(spec) { const m = /^([A-Za-z_][A-Za-z0-9_]*)=(.*)$/.exec(S(spec)); return m ? { col: m[1], val: m[2] } : null; }
function sourceItems(src, tenantId) {
  const out = []; const seen = new Set();
  const tid = tenantId ? Number(tenantId) : null;
  const add = (k, n) => { k = S(k); if (!k || seen.has(k)) return; seen.add(k); out.push({ key: k, name: S(n == null || n === "" ? k : n) }); };
  const D = db();
  for (const part of S(src).split("+").map(x => x.trim()).filter(Boolean)) {
    try {
      if (part.startsWith("list:")) { for (const x of list(part.slice(5))) add(keyOf(x), (x && (x.name || x.label)) || keyOf(x)); continue; }
      if (part.startsWith("entity:")) {
        const key = part.slice(7); const ent = require("./entity.js");
        const def = ent.allEntities(tid)[key]; if (!def) continue;
        const pk = def.pk || "id";
        const lab = ["name", "label", "title", "code", "key"].find(f => (def.fields || []).some(x => x.key === f)) || pk;
        const got = tid ? ent.listEntities(tid, key, { limit: 500 }) : ent.listEntitiesGlobal(key, { limit: 500 });
        for (const r of (Array.isArray(got) ? got : (got && (got.rows || got.items)) || [])) add(r[pk], S(r[lab] != null ? r[lab] : r[pk]) + (!tid && r.tenant_id ? " · platform " + r.tenant_id : ""));
        continue;
      }
      if (part.startsWith("rows:") || part.startsWith("values:")) {
        const isRows = part.startsWith("rows:");
        const bits = part.slice(isRows ? 5 : 7).split(":");
        const table = bits[0];
        const colSpec = bits[1] || "";
        const [col, ...path] = colSpec.split(".");
        const labc = isRows ? (bits[2] && !whereOf(bits[2]) ? bits[2] : col) : null;
        const w = whereOf(isRows ? (whereOf(bits[2]) ? bits[2] : bits[3]) : bits[2]);
        if (![table, col].concat(labc ? [labc] : []).every(x => IDENT.test(S(x))) || (w && !IDENT.test(w.col))) continue;
        const cols = D.all("PRAGMA table_info(" + table + ")").map(c => c.name);
        if (!cols.includes(col) || (labc && !cols.includes(labc)) || (w && !cols.includes(w.col))) continue;
        const conds = [], args = [];
        if (w) { conds.push(w.col + "=?"); args.push(w.val); }
        if (cols.includes("tenant_id") && tid) { conds.push("tenant_id IN (?, 0)"); args.push(tid); }
        const sel = "SELECT " + col + " k" + (labc ? ", " + labc + " n" : "") + (cols.includes("tenant_id") ? ", tenant_id t" : "") + " FROM " + table + (conds.length ? " WHERE " + conds.join(" AND ") : "") + (cols.includes("position") ? " ORDER BY position" : "") + " LIMIT 2000";
        for (const r of D.all(sel, ...args)) {
          if (isRows) { add(r.k, S(r.n) + (!tid && r.t ? " · platform " + r.t : "")); continue; }
          let v = J(r.k, null); for (const p of path) v = v && typeof v === "object" ? v[p] : undefined;
          for (const m of arr(v)) if (typeof m !== "object") add(m, S(m).replace(/_/g, " "));
        }
      }
    } catch (e) { }
  }
  return out;
}
function subjects(type, tenantId) { const t = typeRow(type); return t ? sourceItems(t.source, tenantId) : []; }
function dimensionOptions(d) { return d && d.options ? sourceItems(d.options, null) : []; }
function schema(opts) {
  const forTenant = !!(opts && opts.tenant);
  return {
    effects: EFFECTS,
    subjectTypes: list("ruleSubjectTypes").map(t => ({ key: keyOf(t), name: S(t.name || keyOf(t)), source: t.source })),
    dimensions: dims().filter(d => !(forTenant && platformOnly(d))).map(d => ({ key: d.key, name: d.name, fact: d.fact, match: d.match, source: d.source, overridable: !!d.overridable, options: dimensionOptions(d) })),
    segmentOptions: segmentOptions()
  };
}
/* the segments a membership can name: the options of the dimension(s) computed by the
   segment provider */
function segmentOptions() {
  const seen = new Set(); const out = [];
  for (const d of dims().filter(d => d.source === "computed" && d.provider === "segments")) for (const o of dimensionOptions(d)) if (!seen.has(o.key)) { seen.add(o.key); out.push(o); }
  return out;
}

/* ---------------- authoring ---------------- */
function validate(input, tenantId) {
  const i = input || {};
  const types = list("ruleSubjectTypes").map(keyOf);
  const type = S(i.subject_type);
  if (!types.includes(type)) return { error: "Unknown subject type: " + type + " (one of " + types.join(", ") + ")" };
  const subject = S(i.subject || "*").trim() || "*";
  if (subject !== "*" && !subjects(type).some(x => x.key === subject)) return { error: "Unknown " + label(type).toLowerCase() + ": " + subject };
  const effect = S(i.effect || "allow");
  if (!EFFECTS.includes(effect)) return { error: "Effect must be one of " + EFFECTS.join(", ") };
  const raw = i.scope && typeof i.scope === "object" ? i.scope : {};
  const scope = {};
  for (const d of dims()) {
    /* a platform narrows itself only: its rules never name another platform's identity */
    if (tenantId && platformOnly(d)) continue;
    const v = arr(raw[d.key]).map(x => S(x).trim()).filter(Boolean);
    if (!v.length) continue;
    const opts = dimensionOptions(d);
    if (opts.length) { const bad = v.filter(x => !opts.some(o => S(o.key).toLowerCase() === x.toLowerCase())); if (bad.length) return { error: d.name + ": unknown " + bad.join(", ") }; }
    scope[d.key] = [...new Set(v.map(x => { const o = opts.find(o => S(o.key).toLowerCase() === x.toLowerCase()); return o ? o.key : norm1(d, x); }))];
  }
  for (const k of ["min_amount", "max_amount"]) if (raw[k] != null && raw[k] !== "") { const n = Number(raw[k]); if (!isFinite(n) || n < 0) return { error: k + " must be a non-negative number" }; scope[k] = n; }
  if (scope.min_amount != null && scope.max_amount != null && scope.min_amount > scope.max_amount) return { error: "min_amount is above max_amount" };
  if (raw.amount_currency) { const c = S(raw.amount_currency).toUpperCase(); if (!registry().currency(c)) return { error: "Unknown currency " + c }; scope.amount_currency = c; }
  for (const k of ["from", "to"]) if (raw[k]) { const v = S(raw[k]).trim(); if (isNaN(Date.parse(v))) return { error: k + " is not a date" }; scope[k] = v; }
  const params = i.params && typeof i.params === "object" && !Array.isArray(i.params) ? i.params : {};
  return { rule: { subject_type: type, subject, effect, priority: Math.max(-1000, Math.min(1000, Number(i.priority) || 0)), scope, params, note: S(i.note).slice(0, 300), active: i.active === false || i.active === 0 ? 0 : 1 } };
}
function listRules(tenantId, opts) {
  const o = opts || {};
  const D = db();
  const where = tenantId === null || tenantId === undefined ? "tenant_id IS NULL" : "tenant_id=?";
  const args = tenantId === null || tenantId === undefined ? [] : [Number(tenantId)];
  let out = D.all("SELECT * FROM applicability_rules WHERE " + where + " ORDER BY subject_type, subject, id", ...args).map(normRow);
  if (o.subject_type) out = out.filter(r => r.subject_type === o.subject_type);
  return out.map(r => ({ ...r, summary: describe(r) }));
}
/* the platform owner's rules that can reach one platform: every platform-identity dimension
   they set includes this platform */
function inheritedBy(tenantId) {
  const f = platformFacts(tenantId);
  return listRules(null).filter(r => dims().filter(platformOnly).every(d => dimMatch(d, arr(r.scope[d.key]), f[d.fact]) !== "no"));
}
function save(input, tenantId, actor) {
  const v = validate(input, tenantId);
  if (v.error) return v;
  const r = v.rule; const D = db();
  const tid = tenantId ? Number(tenantId) : null;
  if (input.id) {
    const ex = D.get("SELECT * FROM applicability_rules WHERE id=?", Number(input.id));
    if (!ex || (ex.tenant_id == null ? null : Number(ex.tenant_id)) !== tid) return { error: "No such rule", status: 404 };
    D.run("UPDATE applicability_rules SET subject_type=?, subject=?, effect=?, priority=?, scope=?, params=?, note=?, active=?, updated_at=datetime('now') WHERE id=?",
      r.subject_type, r.subject, r.effect, r.priority, JSON.stringify(r.scope), JSON.stringify(r.params), r.note, r.active, ex.id);
    bust(); return { rule: get(ex.id) };
  }
  const x = D.run("INSERT INTO applicability_rules(tenant_id,subject_type,subject,effect,priority,scope,params,note,active,created_by) VALUES(?,?,?,?,?,?,?,?,?,?)",
    tid, r.subject_type, r.subject, r.effect, r.priority, JSON.stringify(r.scope), JSON.stringify(r.params), r.note, r.active, actor ? S(actor) : null);
  bust(); return { rule: get(Number(x.lastInsertRowid)) };
}
function get(id) { const r = db().get("SELECT * FROM applicability_rules WHERE id=?", Number(id)); return r ? { ...normRow(r), summary: describe(normRow(r)) } : null; }
function remove(id, tenantId) {
  const D = db(); const ex = D.get("SELECT tenant_id FROM applicability_rules WHERE id=?", Number(id));
  const tid = tenantId ? Number(tenantId) : null;
  if (!ex || (ex.tenant_id == null ? null : Number(ex.tenant_id)) !== tid) return { error: "No such rule", status: 404 };
  D.run("DELETE FROM applicability_rules WHERE id=?", Number(id)); bust(); return { ok: true };
}
/* every subject of a type, decided in one context — the console's "why" view */
function explain(type, ctx) {
  return subjects(type).map(x => { const d = decide(type, x.key, ctx); return { key: x.key, name: x.name, ok: d.ok, verdict: d.verdict, reasons: d.reasons, priority: d.priority, params: d.params }; });
}
/* an explicit context for the console: platform-identity facts only for the platform owner */
function explainContext(tenantId, raw, opts) {
  const c = raw && typeof raw === "object" ? raw : {};
  const x = { buyer: false };
  for (const d of dims()) {
    if (c[d.fact] == null || c[d.fact] === "" || (Array.isArray(c[d.fact]) && !c[d.fact].length)) continue;
    if (opts && opts.tenant && platformOnly(d)) continue;
    x[d.fact] = d.match === "any" ? arr(typeof c[d.fact] === "string" ? c[d.fact].split(",") : c[d.fact]).map(v => S(v).trim()).filter(Boolean) : c[d.fact];
  }
  if (c.amount != null && c.amount !== "" && isFinite(Number(c.amount))) x.amount = Number(c.amount);
  if (c.at) x.at = S(c.at);
  let t = tenantId;
  /* the platform owner names a platform by any platform-identity fact (its slug) */
  if (!t) for (const d of dims().filter(d => platformOnly(d) && d.column && IDENT.test(S(d.column)))) {
    if (x[d.fact] == null || Array.isArray(x[d.fact])) continue;
    try { const r = db().get("SELECT id FROM tenants WHERE " + d.column + "=?", x[d.fact]); if (r) { t = r.id; break; } } catch (e) { }
  }
  return context(t || 0, x);
}
/* segment memberships a platform assigns by hand (computed audiences need no rows) */
function members(tenantId) { try { return db().all("SELECT * FROM segment_members WHERE tenant_id=? ORDER BY segment, owner", Number(tenantId)); } catch (e) { return []; } }
function addMember(tenantId, owner, segment) {
  const seg = S(segment).trim();
  if (!segmentOptions().some(o => o.key === seg)) return { error: "Unknown segment " + seg };
  if (!S(owner)) return { error: "owner required" };
  db().run("INSERT OR IGNORE INTO segment_members(tenant_id,owner,segment) VALUES(?,?,?)", Number(tenantId), S(owner), seg);
  return { ok: true };
}
function removeMember(tenantId, id) { db().run("DELETE FROM segment_members WHERE tenant_id=? AND id=?", Number(tenantId), Number(id)); return { ok: true }; }

module.exports = {
  LISTS, EFFECTS, run, current, context, platformFacts, segmentsOf, requestFacts, decide, permits, filter, bankOf,
  at, decideAt, permitsAt, filterAt, applyParams, exempt, guardAt, contextualAt, binding,
  subjects, schema, segmentOptions, dimensionOptions, validate, listRules, inheritedBy, save, get, remove, explain, explainContext,
  members, addMember, removeMember, bust, describe
};
