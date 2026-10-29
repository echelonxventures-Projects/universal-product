/* LUXORA Platform — technology governance (PR-053).
   Any technology the platform uses or may use is governed here, on the kernel: a category, an
   item and each of its releases are kernel nodes whose facts are versioned in k_versions, and
   every production-affecting move is a kernel change (lib/kernel-lifecycle.js) — drafted,
   validated, approved by someone other than its author, published, rolled back. Nothing in this
   file names a category, a technology or a version: lib/seed/technology.json declares them.

     CATEGORY   an open-ended kind of technology with a version scheme and a metadata contract
                (the attributes its releases' facts must carry, checked by the kernel's own value
                checks). A new category is a node — no core change, no new table, no new kind
     DISCOVERY  an adapter (lib/technology-adapters.js) turns what a source published into entries;
                ingest checks each against the source's trust level, the item's allowed sources, the
                category's contract, the digest formats and the size limits, and records it as
                DISCOVERED with its provenance. A changed artifact digest for a known release is
                refused as tampering. Discovery never confers compatibility
     EVALUATION computed, never declared: identity, provenance, integrity, licence, advisories, the
                capabilities each requirement needs, the engine ranges of the libraries in scope,
                dependencies, and the evidence each use requires. The report is recorded on the
                release, and moves it automatically through candidate, under evaluation, compatible
                and verified — or rejected
     GOVERNED   approved, active, deprecated and prohibited are reached only by a published kernel
                change; so is a RESOLUTION, which binds a use to the releases it runs (with their
                artifact identity, provenance and evidence) and makes those releases active
     EVOLUTION  proposals() finds what moved: a newer eligible release in a line (an evaluation lane,
                or an upgrade once verified), a resolved release a security advisory or a
                deprecation now affects, a line near its end of life. autoPropose drafts the
                upgrades; approving them is still a person's decision
   The repository's own toolchain is the registry's first state (the seed's baseline, imported as
   the money policy's first version was) and is resolved into technology.lock.json by lock(). */
"use strict";

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const SEED = require("./seed/technology.json");
const AD = require("./technology-adapters.js");

const K = () => require("./kernel.js");
const L = () => require("./kernel-lifecycle.js");
const D = () => require("./db.js");
const ROOT = path.join(__dirname, "..");
const bad = (m, status, code) => { throw Object.assign(new Error(m), { status: status || 400, code: code || "technology_invalid" }); };
const J = v => JSON.stringify(v);
const by = f => (a, b) => (f(a) < f(b) ? -1 : f(a) > f(b) ? 1 : 0);

/* ============================== version schemes ============================== */
/* how a category's versions are told apart and ordered; a scheme is registered, and a category
   names one. dotted: numeric parts (with npm-style ranges); opaque: a label that is only equal */
const SCHEMES = new Map();
function registerScheme(key, s) {
  if (!s || typeof s.valid !== "function" || typeof s.satisfies !== "function") bad("A version scheme has valid(v) and satisfies(v, range)");
  SCHEMES.set(key, s);
}
const nums = v => { const m = /^v?(\d+|[xX*])(?:\.(\d+|[xX*]))?(?:\.(\d+|[xX*]))?(?:[-+][0-9A-Za-z.-]+)?$/.exec(String(v).trim()); return m ? [m[1], m[2], m[3]].map(x => x == null || /[xX*]/.test(x) ? null : Number(x)) : null; };
const cmp3 = (a, b) => { for (let i = 0; i < 3; i++) { const x = a[i] || 0, y = b[i] || 0; if (x !== y) return x < y ? -1 : 1; } return 0; };
function comparator(v, c) {
  const m = /^(\^|~>?|>=|<=|>|<|=)?\s*(.+)$/.exec(c.trim());
  if (!m) return false;
  const op = m[1] || "", p = nums(m[2]);
  if (!p || p[0] == null) return op === "" || op === "=" ? true : false;
  const [M, n, q] = p, lo = [M, n || 0, q || 0];
  const ge = x => cmp3(v, x) >= 0, lt = x => cmp3(v, x) < 0;
  switch (op) {
    case "^": return ge(lo) && lt(M > 0 || n == null ? [M + 1, 0, 0] : n > 0 || q == null ? [M, n + 1, 0] : [M, n, q + 1]);
    case "~": case "~>": return ge(lo) && lt(n == null ? [M + 1, 0, 0] : [M, n + 1, 0]);
    case ">=": return ge(lo);
    case ">": return n == null ? ge([M + 1, 0, 0]) : q == null ? ge([M, n + 1, 0]) : cmp3(v, lo) > 0;
    case "<": return lt(lo);
    case "<=": return n == null ? lt([M + 1, 0, 0]) : q == null ? lt([M, n + 1, 0]) : cmp3(v, lo) <= 0;
    default: return n == null ? ge(lo) && lt([M + 1, 0, 0]) : q == null ? ge(lo) && lt([M, n + 1, 0]) : cmp3(v, lo) === 0;
  }
}
registerScheme("dotted", {
  valid: v => typeof v === "string" && v.length <= 64 && /^v?\d+(\.\d+)*([-+][0-9A-Za-z.-]+)?$/.test(v),
  compare: (a, b) => cmp3(nums(a) || [], nums(b) || []),
  line: v => String((nums(v) || [])[0]),
  satisfies(v, range) {
    const x = nums(v); if (!x) return false;
    return String(range).split("||").some(alt => {
      const a = alt.trim();
      if (!a || a === "*" || a.toLowerCase() === "x") return true;
      const h = /^(\S+)\s+-\s+(\S+)$/.exec(a);
      if (h) return comparator(x, ">=" + h[1]) && comparator(x, "<=" + h[2]);
      return a.replace(/(>=|<=|>|<|=|\^|~)\s+/g, "$1").split(/\s+/).every(c => comparator(x, c));
    });
  }
});
registerScheme("opaque", {
  valid: v => typeof v === "string" && v.length > 0 && v.length <= 128 && /^[\x21-\x7e]+$/.test(v),
  compare: null, line: () => null, satisfies: (v, range) => v === range
});
const schemeOf = categoryKey => { const c = category(categoryKey); const s = c && SCHEMES.get(c.scheme); if (!s) bad("No version scheme for category " + categoryKey); return s; };

/* ============================== declarations ============================== */
const STATE = Object.fromEntries(SEED.states.list.map(s => [s.key, s]));
const N = SEED.states.named;
const ROLES = Object.keys(SEED.kinds);
const kindName = role => SEED.kinds[role].kind;
function kindSpec(role) {
  const d = SEED.kinds[role];
  const attributes = d.attributes.map(a => a.lifecycle ? { ...a, constraints: { oneOf: SEED.states.list.map(s => s.key) } } : a);
  return { namespace: SEED.namespace, kind: d.kind, owner: SEED.owner, label: d.label, root: true, schemes: [d.scheme], attributes };
}
const signature = attrs => J(attrs.map(a => [a.key, a.type, !!a.required, a.constraints || {}]));
const source = key => SEED.sources.find(s => s.key === key) || null;
const trustOf = key => SEED.trust.levels.find(t => t.key === key) || null;
const use = key => { const u = SEED.uses.find(x => x.key === key); if (!u) bad("Unknown use: " + key, 404, "technology_unknown"); return u; };
const requirement = key => { const r = SEED.requirements.find(x => x.key === key); if (!r) bad("Unknown requirement: " + key); return r; };
const releaseKey = (item, version) => item + "@" + version;

/* ============================== reading the registry ============================== */
function uidOf(role, key) {
  const r = D().get("SELECT node FROM k_identifiers WHERE scheme=? AND value=? AND rec_to IS NULL ORDER BY id LIMIT 1", SEED.kinds[role].scheme, String(key));
  return r ? r.node : null;
}
/* the facts of every node of a role, as believed and valid now */
function rows(role) {
  const now = new Date().toISOString();
  return D().all(`SELECT n.uid AS uid, v.attrs AS attrs FROM k_nodes n JOIN k_versions v ON v.node=n.uid
    WHERE n.kind=? AND n.namespace=? AND v.rec_to IS NULL AND v.valid_from<=? AND (v.valid_to IS NULL OR v.valid_to>?) ORDER BY n.uid`, kindName(role), SEED.namespace, now, now)
    .map(r => ({ uid: r.uid, ...JSON.parse(r.attrs) }));
}
function one(role, key) {
  const uid = uidOf(role, key);
  if (!uid) return null;
  return { uid, ...(K().attributes(uid) || {}) };
}
const category = key => one("category", key);
const item = key => one("item", key);
const release = key => one("release", key);
const resolution = key => one("resolution", key);
const categories = () => rows("category").sort(by(c => c.key));
const items = () => rows("item").sort(by(i => i.key));
function releases(q) {
  q = q || {};
  return rows("release").filter(r => (!q.item || r.item === q.item) && (!q.state || r.state === q.state)).sort(by(r => r.key));
}
const resolutions = () => rows("resolution").sort(by(r => r.use));
/* every version a node ever had (superseded and rolled back ones included), with who recorded it */
function history(role, key) {
  const uid = uidOf(role, key);
  if (!uid) bad("Unknown " + role + ": " + key, 404, "technology_unknown");
  return D().all("SELECT v.*, e.at AS recorded_at, e.actor AS recorded_by FROM k_versions v LEFT JOIN k_events e ON e.seq=v.rec_from WHERE v.node=? ORDER BY v.rec_from, v.valid_from", uid)
    .map(r => ({ attributes: JSON.parse(r.attrs), validFrom: r.valid_from, validTo: r.valid_to, recordedFrom: r.rec_from, recordedTo: r.rec_to, recordedAt: r.recorded_at, recordedBy: r.recorded_by, current: r.rec_to == null }));
}

/* ============================== registration ============================== */
function ensureKinds() {
  const k = K();
  L().ensureTables();
  for (const role of ROLES) {
    const want = kindSpec(role), cur = k.kindOf(want.kind, SEED.namespace);
    if (!cur || signature(cur.attributes) !== signature(want.attributes.map(a => ({ ...a, constraints: a.constraints || {} })))) k.defineKind(want, SEED.actors.seed);
  }
}
const KEY = /^[a-z0-9][a-z0-9_.:@/+-]{0,127}$/;
function checkContract(contract) {
  if (contract == null) return { integrity: "optional", attributes: [] };
  if (typeof contract !== "object" || Array.isArray(contract)) bad("A category's contract is { attributes, integrity }");
  const attributes = Array.isArray(contract.attributes) ? contract.attributes : [];
  const types = K().internal.VALUE_TYPES;
  for (const a of attributes) {
    if (!a || typeof a.key !== "string" || !/^[a-z][A-Za-z0-9]{0,63}$/.test(a.key)) bad("A contract attribute has a key: " + J(a));
    if (!types.has(a.type)) bad(`Contract attribute ${a.key}: unknown value type ${a.type}`);
  }
  if (contract.integrity != null && !["required", "optional"].includes(contract.integrity)) bad("A contract's integrity is required or optional");
  return { integrity: contract.integrity || "optional", attributes };
}
/* a category is a node: registering one is data, the same call for any category ever named */
function defineCategory(d, actor) {
  d = d || {};
  if (typeof d.key !== "string" || !KEY.test(d.key)) bad("A category key is lower-case: " + d.key);
  if (!SCHEMES.has(d.scheme)) bad(`Unknown version scheme ${d.scheme}; registered: ${[...SCHEMES.keys()].join(", ")}`);
  const attrs = { key: d.key, label: String(d.label || d.key).slice(0, 200), scheme: d.scheme, contract: checkContract(d.contract), ...(d.note ? { note: String(d.note).slice(0, 500) } : {}) };
  const uid = uidOf("category", d.key);
  if (uid) { const cur = category(d.key); if (J({ ...cur, uid: undefined }) !== J({ ...cur, ...attrs, uid: undefined })) K().record(uid, attrs, {}, actor); return uid; }
  return K().createNode(kindName("category"), { namespace: SEED.namespace, attributes: attrs, identifiers: { [SEED.kinds.category.scheme]: d.key } }, actor);
}
const ITEM_FIELDS = SEED.kinds.item.attributes.map(a => a.key);
function defineItem(d, actor) {
  d = d || {};
  if (typeof d.key !== "string" || !KEY.test(d.key)) bad("An item key is lower-case: " + d.key);
  if (!category(d.category)) bad(`Item ${d.key}: unknown category ${d.category}`);
  for (const s of d.sources || []) if (!source(s)) bad(`Item ${d.key}: unknown source ${s}`);
  const attrs = {};
  for (const f of ITEM_FIELDS) if (d[f] != null) attrs[f] = d[f];
  attrs.label = String(d.label || d.key).slice(0, 200);
  const uid = uidOf("item", d.key);
  if (uid) { const cur = item(d.key); const next = { ...cur, ...attrs }; delete cur.uid; delete next.uid; if (J(cur) !== J(next)) K().record(uid, attrs, {}, actor); return uid; }
  return K().createNode(kindName("item"), { namespace: SEED.namespace, attributes: attrs, identifiers: { [SEED.kinds.item.scheme]: d.key } }, actor);
}

/* a source is declared before anything it reports is read: its protocol must have an adapter
   and its trust level must be declared. The same contract for a source in the seed and one added
   at run time */
function registerSource(d) {
  d = d || {};
  if (typeof d.key !== "string" || !KEY.test(d.key)) bad("A source key is lower-case: " + d.key);
  if (source(d.key)) bad("A source " + d.key + " is already declared");
  if (!AD.adapter(d.protocol)) bad(`No adapter speaks ${d.protocol}; register one first`, 400, "technology_untrusted");
  if (!trustOf(d.trust)) bad("Unknown trust level " + d.trust, 400, "technology_untrusted");
  const clean = { key: d.key, protocol: d.protocol, trust: d.trust, ...(d.location ? { location: String(d.location) } : {}), ...(d.item ? { item: String(d.item) } : {}), ...(d.items ? { items: { ...d.items } } : {}), ...(d.category ? { category: String(d.category) } : {}), ...(d.bundles ? { bundles: String(d.bundles) } : {}) };
  SEED.sources.push(clean);
  return clean;
}

/* ============================== discovery ============================== */
function deepKeys(v, out, depth) {
  if (depth > 12) bad("Metadata nests too deep");
  if (v && typeof v === "object") for (const k of Object.keys(v)) { out.push(k); deepKeys(v[k], out, depth + 1); }
  return out;
}
const DIGESTS = Object.fromEntries(Object.entries(SEED.trust.digest).map(([k, p]) => [k, new RegExp(p)]));
const DIGEST_FIELDS = Object.keys(DIGESTS);
/* one entry an adapter returned, checked before anything is written. Returns the clean entry */
function checkEntry(e, src) {
  if (!e || typeof e !== "object" || Array.isArray(e)) bad("An entry is a record");
  if (Buffer.byteLength(J(e)) > SEED.trust.maxEntryBytes) bad("An entry is larger than " + SEED.trust.maxEntryBytes + " bytes");
  const forbidden = deepKeys(e, [], 0).find(k => SEED.trust.forbiddenKeys.includes(k));
  if (forbidden) bad("An entry carries the forbidden key " + forbidden);
  const it = item(e.item);
  if (!it) bad("Unknown item " + e.item + " (register it, or a source that introduces items, first)");
  if (!(it.sources || []).includes(src.key)) bad(`The source ${src.key} is not allowed to report releases of ${it.key}`);
  const cat = category(it.category);
  const scheme = schemeOf(it.category);
  if (!scheme.valid(e.version)) bad(`${e.version} is not a ${cat.scheme} version (${it.key})`);
  const artifacts = (e.artifacts || []).map(a => {
    if (!a || typeof a.name !== "string" || !a.name) bad("An artifact has a name");
    const fields = DIGEST_FIELDS.filter(f => a[f] != null);
    for (const f of fields) if (typeof a[f] !== "string" || !DIGESTS[f].test(a[f])) bad(`Artifact ${a.name}: ${f} is not a valid digest`);
    return { name: a.name, ...(a.platform ? { platform: String(a.platform) } : {}), ...Object.fromEntries(fields.map(f => [f, a[f]])) };
  });
  const meta = e.metadata || {};
  if (typeof meta !== "object" || Array.isArray(meta)) bad("metadata is a record");
  const declared = new Map((cat.contract.attributes || []).map(a => [a.key, a]));
  for (const [k, v] of Object.entries(meta)) {
    if (k.startsWith(SEED.trust.extensionPrefix)) continue;
    const a = declared.get(k);
    if (!a) bad(`${it.category} declares no metadata ${k} (an extension is named ${SEED.trust.extensionPrefix}<name>)`);
    K().internal.checkValue(a.type, a.constraints || {}, v, { label: `${it.key}@${e.version} ${k}` });
  }
  for (const d of e.dependencies || []) if (!d || typeof d.item !== "string" || (d.version == null && d.range == null)) bad("A dependency is { item, version | range }");
  for (const a of e.advisories || []) if (!a || typeof a.key !== "string" || typeof a.severity !== "string") bad("An advisory is { key, severity }");
  return { item: it.key, version: e.version, channel: e.channel || null, artifacts, metadata: meta, dependencies: e.dependencies || [], advisories: e.advisories || [] };
}
const EMPTY = Object.fromEntries(SEED.kinds.release.attributes.filter(a => a.type === "record").map(a => [a.key, {}]));
const mergeBy = (a, b, f) => { const m = new Map((a || []).map(x => [f(x), x])); for (const x of b || []) m.set(f(x), { ...(m.get(f(x)) || {}), ...x }); return [...m.values()].sort(by(f)); };
/* ingest(sourceKey, { entries | payload, location, fetchedAt, payloadSha256, selection }) — runs the
   source's adapter and records what it reports. Returns what was accepted, unchanged and refused */
function ingest(sourceKey, snapshot, actor) {
  const src = source(sourceKey);
  if (!src) bad("Unknown source " + sourceKey + "; a source is declared before it is read", 400, "technology_untrusted");
  const trust = trustOf(src.trust);
  if (!trust || !trust.mayDiscover) bad(`The source ${src.key} is not trusted to report anything (${src.trust})`, 400, "technology_untrusted");
  const ad = AD.adapter(src.protocol);
  if (!ad) bad(`No adapter speaks ${src.protocol}; register one in lib/technology-adapters.js`, 400, "technology_untrusted");
  const s = snapshot || {};
  const payload = s.entries !== undefined ? s.entries : s.payload;
  const found = ad.discover(payload, src);
  if (found.length > SEED.trust.maxEntries) bad(`${src.key} reported ${found.length} entries; the limit is ${SEED.trust.maxEntries}`);
  const provenance = { source: src.key, protocol: src.protocol, trust: src.trust, location: s.location || src.location || null, fetchedAt: s.fetchedAt || null, payloadSha256: s.payloadSha256 || null, ...(s.selection ? { selection: s.selection } : {}) };
  const out = { source: src.key, accepted: [], unchanged: [], rejected: [] };
  const by_ = actor || SEED.actors.discovery;
  K().internal.tx(() => {
    for (const raw of found) {
      const label = raw && raw.item ? releaseKey(raw.item, raw.version) : "(unnamed)";
      try {
        if (raw.newItem && !item(raw.item)) {
          if (!src.category || raw.newItem.category !== src.category) bad(`${src.key} may not introduce items of category ${raw.newItem.category}`);
          defineItem(raw.newItem, by_);
        }
        const e = checkEntry(raw, src);
        const key = releaseKey(e.item, e.version);
        const cur = release(key);
        if (!cur) {
          K().createNode(kindName("release"), { namespace: SEED.namespace, identifiers: { [SEED.kinds.release.scheme]: key },
            attributes: { key, item: e.item, version: e.version, state: SEED.states.initial, ...(e.channel ? { channel: e.channel } : {}), artifacts: e.artifacts,
              metadata: e.metadata, dependencies: e.dependencies, advisories: e.advisories, provenance: [provenance], evidence: [] } }, by_);
          out.accepted.push(key); continue;
        }
        /* the same artifact with another digest is not news, it is tampering (or a re-tag) */
        for (const a of e.artifacts) {
          const was = (cur.artifacts || []).find(x => x.name === a.name);
          if (was) for (const f of DIGEST_FIELDS) if (was[f] && a[f] && was[f] !== a[f]) bad(`${key}: artifact ${a.name} changed its ${f} (${was[f]} → ${a[f]}); refused`, 409, "technology_tampered");
        }
        const next = {
          artifacts: mergeBy(cur.artifacts, e.artifacts, a => a.name),
          metadata: { ...(cur.metadata || {}), ...e.metadata },
          dependencies: mergeBy(cur.dependencies, e.dependencies, d => d.item),
          advisories: mergeBy(cur.advisories, e.advisories, a => a.key),
          provenance: mergeBy(cur.provenance, [provenance], p => p.source + "\u0001" + (p.payloadSha256 || p.fetchedAt || ""))
        };
        if (e.channel && !cur.channel) next.channel = e.channel;
        const changed = Object.keys(next).filter(k => J(next[k]) !== J(cur[k] == null ? (EMPTY[k] !== undefined ? EMPTY[k] : []) : cur[k]));
        if (!changed.length) { out.unchanged.push(key); continue; }
        K().record(cur.uid, Object.fromEntries(changed.map(k => [k, next[k]])), {}, by_);
        out.accepted.push(key);
      } catch (err) {
        out.rejected.push({ entry: label, reason: err.message, code: err.code || "technology_invalid" });
      }
    }
    /* every ingest is an event in the kernel's hash-chained log: what was read, from where, and each
       entry refused with its reason — held for review, never silently dropped */
    if (out.accepted.length || out.rejected.length)
      K().append(SEED.events.ingested, { namespace: SEED.namespace, subject: "source:" + src.key, actor: by_, payload: { provenance, accepted: out.accepted.length, unchanged: out.unchanged.length, rejected: out.rejected } });
  });
  return out;
}
/* the entries discovery refused, newest first, with the reason recorded at the time */
function rejections(limit) {
  return D().all("SELECT seq, at, subject, actor, payload FROM k_events WHERE type=? ORDER BY seq DESC LIMIT ?", SEED.events.ingested, limit || 200)
    .flatMap(e => (JSON.parse(e.payload).rejected || []).map(r => ({ ...r, source: e.subject.replace(/^source:/, ""), at: e.at, seq: e.seq })));
}
/* evidence is appended, never edited: a later failure stands beside an earlier pass */
function addEvidence(key, ev, actor) {
  const r = release(key);
  if (!r) bad("Unknown release " + key, 404, "technology_unknown");
  if (!ev || typeof ev.kind !== "string" || !["pass", "fail"].includes(ev.outcome) || typeof ev.ref !== "string" || !ev.ref) bad("Evidence is { kind, outcome: pass|fail, ref, commit?, at? }");
  const clean = { kind: ev.kind, outcome: ev.outcome, ref: ev.ref.slice(0, 300), ...(ev.commit ? { commit: String(ev.commit) } : {}), ...(ev.at ? { at: K().internal.instant(ev.at, "at") } : {}), by: actor || null };
  if ((r.evidence || []).some(x => x.kind === clean.kind && x.ref === clean.ref && x.outcome === clean.outcome)) return r.evidence;
  const evidence = [...(r.evidence || []), clean];
  K().record(r.uid, { evidence }, {}, actor);
  return evidence;
}

/* a downloaded artifact is the one the registry recorded: its digest, recomputed */
function verifyArtifact(key, name, file) {
  const r = release(key);
  if (!r) bad("Unknown release " + key, 404, "technology_unknown");
  const a = (r.artifacts || []).find(x => x.name === name);
  if (!a) bad(`${key} records no artifact ${name}`, 404, "technology_unknown");
  const bytes = fs.readFileSync(file);
  const h = alg => crypto.createHash(alg).update(bytes).digest("hex");
  if (a.sha256) return { ok: h("sha256") === a.sha256, algorithm: "sha256", expected: a.sha256, actual: h("sha256") };
  if (a.sha512) return { ok: h("sha512") === a.sha512, algorithm: "sha512", expected: a.sha512, actual: h("sha512") };
  if (a.integrity) { const [alg, b64] = a.integrity.split("-"); const got = crypto.createHash(alg).update(bytes).digest("base64"); return { ok: got === b64, algorithm: alg, expected: b64, actual: got }; }
  bad(`${key} ${name} records no file digest (a ${a.digest ? "registry digest" : a.commit ? "commit" : "nothing"} is verified by its own client)`);
}

/* ============================== evaluation ============================== */
const satisfies = (it, version, range) => schemeOf(it.category).satisfies(version, range);
/* the release of `want` that a release is, or depends on (directly or one step down) */
function reach(r, want) {
  if (r.item === want) return r;
  for (const d of r.dependencies || []) {
    if (d.item === want && d.version) return release(releaseKey(d.item, d.version)) || { missing: releaseKey(d.item, d.version) };
    if (d.version) { const sub = release(releaseKey(d.item, d.version)); if (sub) for (const d2 of sub.dependencies || []) if (d2.item === want && d2.version) return release(releaseKey(d2.item, d2.version)) || { missing: releaseKey(d2.item, d2.version) }; }
  }
  return null;
}
/* the libraries: releases of the categories a package manager's resolution introduces (the uses
   resolved `from` a source), whichever ecosystem they come from */
const LIBRARY = new Set(SEED.uses.filter(u => u.from).map(u => u.category));
const categoryOf = () => new Map(items().map(i => [i.key, i.category]));
function libraryReleases(cats) { cats = cats || categoryOf(); return releases().filter(x => LIBRARY.has(cats.get(x.item))); }
function libraries(scope) { return libraryReleases().filter(x => x.metadata && x.metadata.scope === scope); }
/* a requirement against a release: the capabilities it needs (from the item, by version), the
   engine ranges of the libraries in its scope. Returns [{ check, ok, detail }] */
function meets(r, req, cache) {
  const out = [];
  const target = reach(r, req.via || req.item);
  if (!target) return [{ check: req.key, ok: true, detail: "not applicable" }];
  if (target.missing) return [{ check: req.key, ok: false, detail: "depends on " + target.missing + ", which the registry does not know" }];
  const it = item(target.item);
  for (const capKey of req.capabilities || []) {
    const c = (it.capabilities || []).find(x => x.key === capKey);
    const ok = !!c && (!c.since || schemeOf(it.category).compare(target.version, c.since) >= 0) && (!c.until || schemeOf(it.category).compare(target.version, c.until) < 0);
    out.push({ check: req.key + " · " + capKey, ok, detail: c ? `${target.key} ${ok ? "provides it" : "predates it"} (since ${c.since})` : `${it.key} declares no capability ${capKey}` });
  }
  if (req.libraries) {
    const libs = cache[req.libraries] || (cache[req.libraries] = libraries(req.libraries));
    const outside = libs.filter(l => l.metadata.engines && l.metadata.engines[target.item] && !satisfies(it, target.version, l.metadata.engines[target.item]));
    out.push({ check: req.key + " · engine ranges", ok: !outside.length, detail: outside.length ? `${outside.length} ${req.libraries} libraries declare ranges ${target.version} is outside: ` + outside.slice(0, 6).map(l => `${l.key} (${l.metadata.engines[target.item]})`).join(", ") + (outside.length > 6 ? ", …" : "") : `every ${req.libraries} library admits ${target.version}` });
  }
  return out;
}
const appliesTo = (u, r, it) => (u.item ? u.item === r.item : true) && (u.category ? u.category === it.category : true) && !u.from;
const passed = (r, kind) => { const xs = (r.evidence || []).filter(e => e.kind === kind); return xs.length > 0 && xs.every(e => e.outcome === "pass"); };
/* the report: generic checks, then a verdict per use the release could serve */
function report(r, cache) {
  cache = cache || {};
  const it = item(r.item), cat = it && category(it.category);
  const checks = [];
  const c = (check, ok, detail, hard) => checks.push({ check, ok: !!ok, detail, ...(hard ? { hard: true } : {}) });
  c("identity", it && cat && schemeOf(it.category).valid(r.version), it ? `${r.key} is a ${cat.scheme} version of ${it.key} (${it.category})` : "unknown item", true);
  const trusts = (r.provenance || []).map(p => trustOf(p.trust)).filter(Boolean);
  c("provenance", trusts.some(t => t.mayDiscover), (r.provenance || []).map(p => p.source + (p.fetchedAt ? " " + p.fetchedAt : "")).join("; ") || "no source");
  const declaredOnly = trusts.length && trusts.every(t => t.warn);
  const needsDigest = cat && cat.contract && cat.contract.integrity === "required";
  const digested = (r.artifacts || []).filter(a => DIGEST_FIELDS.some(f => a[f]));
  c("integrity", !needsDigest || digested.length > 0, digested.length ? digested.length + " artifact digest(s)" : needsDigest ? "the category needs an artifact digest and none was reported" : "not required for " + it.category);
  const missingRequired = cat ? (cat.contract.attributes || []).filter(a => a.required && (r.metadata || {})[a.key] == null).map(a => a.key) : [];
  c("contract", !missingRequired.length, missingRequired.length ? "missing " + missingRequired.join(", ") : "metadata meets the " + (cat ? cat.key : "?") + " contract");
  const lic = (r.metadata && r.metadata.licence) || (it && it.licence) || null;
  if (it && SEED.policy.licensed.includes(it.category)) c("licence", lic && SEED.policy.licences.includes(lic), lic ? lic + (SEED.policy.licences.includes(lic) ? " is allowed" : " is not an allowed licence") : "no licence declared", lic && !SEED.policy.licences.includes(lic));
  /* a release's own advisories and those of the releases it directly depends on (an image's runtime) */
  const deps = (r.dependencies || []).filter(d => d.version).map(d => release(releaseKey(d.item, d.version))).filter(Boolean);
  const blocking = [r, ...deps].flatMap(x => (x.advisories || []).filter(a => SEED.policy.blockingSeverities.includes(a.severity)).map(a => ({ ...a, on: x.key })));
  const generic = checks.every(x => x.ok);
  const uses = SEED.uses.filter(u => it && appliesTo(u, r, it)).map(u => {
    const results = [];
    for (const k of u.requires || []) results.push(...meets(r, requirement(k), cache));
    const advisory = [];
    for (const k of u.advisory || []) advisory.push(...meets(r, requirement(k), cache));
    if (u.platform) results.push({ check: "artifact · " + u.platform, ok: (r.artifacts || []).some(a => a.platform === u.platform && a.sha256), detail: `an archive for ${u.platform} with its digest` });
    if (u.production) results.push({ check: "advisories", ok: !blocking.length, detail: blocking.length ? blocking.map(a => `${a.on}: ${a.key} (${a.note})`).join("; ") : "none blocking" });
    const compatible = generic && results.every(x => x.ok);
    const evidence = (u.evidence || []).map(kind => ({ kind, ok: passed(r, kind) }));
    return { use: u.key, compatible, verified: compatible && evidence.every(e => e.ok), checks: results, advisory: advisory.filter(x => !x.ok), evidence,
      warnings: [...(!u.production && blocking.length ? ["advisory: " + blocking.map(a => a.key).join(", ")] : []), ...(declaredOnly ? [declaredOnly && trusts[0].warn] : [])] };
  });
  return { release: r.key, checks, uses, compatible: generic && (uses.length ? uses.some(u => u.compatible) : true), verified: uses.some(u => u.verified),
    rejected: checks.some(x => x.hard && !x.ok), warnings: declaredOnly ? [trusts[0].warn] : [] };
}
/* the automatic part of the lifecycle: the state the report entitles a release to, reached one
   declared transition at a time. A governed state is never moved by evaluation */
function target(rep) {
  if (rep.rejected) return N.rejected;
  if (!rep.checks.find(x => x.check === "provenance").ok) return N.discovered;
  return rep.verified ? N.verified : rep.compatible ? N.compatible : N.underEvaluation;
}
/* the shortest path of declared transitions through automatic states */
function stepsTo(from, to) {
  if (from === to) return [];
  const T = SEED.states.transitions, auto = s => STATE[s] && STATE[s].automatic;
  const prev = new Map([[from, null]]), q = [from];
  while (q.length) {
    const s = q.shift();
    for (const n of T[s] || []) {
      if (!auto(n) || prev.has(n)) continue;
      prev.set(n, s);
      if (n === to) { const p = []; for (let x = n; x !== from; x = prev.get(x)) p.unshift(x); return p; }
      q.push(n);
    }
  }
  return null;
}
function evaluate(key, actor, cache) {
  const r = release(key);
  if (!r) bad("Unknown release " + key, 404, "technology_unknown");
  const rep = report(r, cache);
  const by_ = actor || SEED.actors.evaluator;
  let state = r.state;
  if ((STATE[r.state] || {}).automatic) for (const s of stepsTo(r.state, target(rep)) || []) { K().record(r.uid, { state: s, evaluation: rep }, {}, by_); state = s; }
  if (state === r.state && J(r.evaluation) !== J(rep)) K().record(r.uid, { evaluation: rep }, {}, by_);
  return { ...rep, from: r.state, state };
}
function evaluateAll(actor) {
  const cache = {};
  return K().internal.tx(() => releases().map(r => evaluate(r.key, actor, cache)));
}

/* ============================== governed changes ============================== */
const TECH_KINDS = new Set(ROLES.map(kindName));
const opKind = o => o.op === "createNode" ? o.args[0] : (() => { const n = D().get("SELECT kind FROM k_nodes WHERE uid=?", o.args[0]); return n && n.kind; })();
function marker(c) { const first = c.ops[0]; const w = first && (first.op === "createNode" ? first.args[1] : first.args[2]); return w && w.technology; }
const ownChange = c => c && c.ops.length > 0 && c.ops.every(o => (o.op === "record" || o.op === "createNode") && TECH_KINDS.has(opKind(o))) && !!marker(c);
function own(id) {
  let c; try { c = L().change(id); } catch (e) { bad("Unknown technology change: " + id, 404, "technology_unknown"); }
  if (!ownChange(c)) bad("Change " + id + " is not a technology change", 404, "technology_unknown");
  return { ...c, technology: marker(c) };
}
const baseOf = uid => { if (!uid) return null; const r = D().get("SELECT MAX(rec_from) AS s FROM k_versions WHERE node=? AND rec_to IS NULL", uid); return r && r.s != null ? r.s : null; };
function fresh(c) {
  const m = c.technology;
  const uid = m.type === "resolution" ? uidOf("resolution", m.use) : uidOf("release", m.release);
  if (baseOf(uid) !== m.basedOn) bad(`What change ${c.id} was drafted against has moved on; draft it again`, 409, "technology_stale");
}
/* the conditions a governed move must meet when it is drafted, approved and published */
function precheck(m) {
  if (m.type === "transition") {
    const r = release(m.release);
    if (!r) bad("Unknown release " + m.release, 404, "technology_unknown");
    if (!STATE[m.to] || !STATE[m.to].governed) bad(`${m.to} is not a governed state; evaluation moves releases there`, 409, "technology_state");
    if (!(SEED.states.transitions[r.state] || []).includes(m.to)) bad(`A release cannot go from ${r.state} to ${m.to}`, 409, "technology_state");
    if (m.to === N.approved && !SEED.states.approvable.includes(r.state) && r.state !== N.active) bad(`Only a ${SEED.states.approvable.join(" or ")} release is approved; ${r.key} is ${r.state}`, 409, "technology_state");
    if (m.to === N.active && !resolutions().some(x => (x.releases || []).some(y => y.key === r.key))) bad(`A release becomes active by being resolved for a use; ${r.key} is in no resolution`, 409, "technology_state");
    if (SEED.states.needsReason.includes(m.to) && !m.reason) bad(`Moving a release to ${m.to} needs a reason`);
    if (m.replacedBy && !release(m.replacedBy)) bad("Unknown replacement " + m.replacedBy);
    return;
  }
  const u = use(m.use);
  if (!Array.isArray(m.releases) || !m.releases.length) bad("A resolution names at least one release");
  if (u.count && m.releases.length !== u.count) bad(`${u.key} resolves exactly ${u.count} release(s)`);
  for (const key of m.releases) {
    const r = release(key);
    if (!r) bad("Unknown release " + key, 404, "technology_unknown");
    if (!SEED.states.resolvable.includes(r.state)) bad(`${key} is ${r.state}; only an ${SEED.states.resolvable.join(", ")} release is resolved`, 409, "technology_state");
    const v = (report(r).uses || []).find(x => x.use === u.key);
    if (!v) bad(`${key} cannot serve ${u.key}`, 409, "technology_incompatible");
    if (!v.compatible) bad(`${key} does not meet ${u.key}: ` + v.checks.filter(x => !x.ok).map(x => x.check + " — " + x.detail).join("; "), 409, "technology_incompatible");
    if (!v.verified) bad(`${key} lacks the evidence ${u.key} requires: ` + v.evidence.filter(e => !e.ok).map(e => e.kind).join(", "), 409, "technology_unverified");
  }
}
function entryOf(r, u) {
  const v = (r.evaluation && r.evaluation.uses || []).find(x => x.use === u.key);
  const keep = u.platform ? (r.artifacts || []).filter(a => !a.platform || a.platform === u.platform) : (r.artifacts || []);
  return { key: r.key, item: r.item, version: r.version, artifacts: keep, ...(r.metadata && r.metadata.reference ? { reference: r.metadata.reference } : {}),
    provenance: [...new Set((r.provenance || []).map(p => p.source))].sort(), evidence: (r.evidence || []).filter(e => (u.evidence || []).includes(e.kind)).map(e => e.ref), verified: !!(v && v.verified) };
}
function draftOps(m) {
  const opt = extra => ({ ...extra, technology: m });
  if (m.type === "transition") {
    const r = release(m.release);
    return [{ op: "record", args: [r.uid, { state: m.to, reason: m.reason || null, replaced_by: m.replacedBy || null }, opt({})] }];
  }
  const u = use(m.use);
  const list = m.releases.map(k => entryOf(release(k), u));
  const attrs = { use: u.key, releases: list, basis: m.reason || null };
  const uid = uidOf("resolution", u.key);
  const ops = [uid ? { op: "record", args: [uid, attrs, opt({})] }
    : { op: "createNode", args: [kindName("resolution"), opt({ namespace: SEED.namespace, attributes: attrs, identifiers: { [SEED.kinds.resolution.scheme]: u.key } })] }];
  /* resolving an approved release makes it active, in the same change */
  for (const k of m.releases) { const r = release(k); if (r.state === N.approved) ops.push({ op: "record", args: [r.uid, { state: N.active }] }); }
  return ops;
}
function draft(m, actor) {
  L().ensureTables();
  precheck(m);
  const subjectUid = m.type === "resolution" ? uidOf("resolution", m.use) : uidOf("release", m.release);
  const mark = { ...m, basedOn: baseOf(subjectUid) };
  const title = String(m.title || (m.type === "resolution" ? `Resolve ${m.use}: ${m.releases.join(", ")}` : `${m.release} → ${m.to}`)).slice(0, SEED.titleMax);
  return own(L().draft({ namespace: SEED.namespace, title, ops: draftOps(mark) }, actor).toString());
}
/* proposeTransition(release, to, { reason, replacedBy }) — approved, active, deprecated, prohibited */
const proposeTransition = (key, to, o, actor) => draft({ type: "transition", release: key, to, reason: o && o.reason, replacedBy: o && o.replacedBy, title: o && o.title }, actor);
/* proposeResolution(use, [release keys], { reason }) — what a use runs */
const proposeResolution = (useKey, keys, o, actor) => draft({ type: "resolution", use: useKey, releases: [...keys], reason: o && o.reason, title: o && o.title }, actor);
function recheck(c) { precheck(c.technology); fresh(c); }
function approve(id, actor, grants) { const c = own(id); recheck(c); return own(L().approve(id, actor, grants).id); }
function publish(id, actor) {
  const c = own(id);
  if (c.state !== K().SEED.lifecycle.approved) bad("Only an approved change is published; this one is " + c.state, 409, "technology_state");
  K().internal.tx(() => { const cc = own(id); recheck(cc); L().publish(id, {}, actor); });
  return own(id);
}
const rollback = (id, actor) => { own(id); L().rollback(id, actor); return own(id); };
const discard = (id, actor) => { own(id); return own(L().discard(id, actor).id); };
const changes = () => L().changes().filter(ownChange).map(c => ({ ...c, technology: marker(c) }));

/* ============================== resolution, evolution ============================== */
const resolved = useKey => { const r = resolution(useKey); return r ? r.releases : []; };
/* the derived values: the runtime the production image carries */
function derivedRelease(name) {
  const d = SEED.derived[name];
  const img = resolved(d.from)[0];
  if (!img) return null;
  const r = release(img.key);
  const dep = (r.dependencies || []).find(x => x.item === d.dependency);
  return dep ? release(releaseKey(dep.item, dep.version)) : null;
}
/* the requirement floors: the highest `since` among the capabilities a requirement needs */
function floors() {
  const out = {};
  for (const req of SEED.requirements.filter(r => (r.capabilities || []).length)) {
    const it = item(req.item);
    const caps = req.capabilities.map(k => (it.capabilities || []).find(c => c.key === k)).filter(Boolean);
    const s = schemeOf(it.category);
    const top = caps.filter(c => c.since).sort((a, b) => s.compare(a.since, b.since)).pop();
    out[req.key] = { item: req.item, floor: top ? top.since : null, from: caps.map(c => ({ capability: c.key, since: c.since })) };
  }
  return out;
}
/* evaluation lanes: per line the item supports, the highest release eligible for the use that is
   compatible but not resolved yet. Running them is how a new release earns its evidence */
function lanes(useKey) {
  const u = use(useKey), it = item(u.item);
  if (!u.evaluate) return [];
  const s = schemeOf(it.category);
  const have = new Set(resolved(useKey).map(r => r.key));
  const floor = (floors()[(u.requires || [])[0]] || {}).floor;
  const out = [];
  for (const line of Object.keys(it.lines || {}).sort((a, b) => Number(a) - Number(b))) {
    const pool = releases({ item: it.key }).filter(r => s.line(r.version) === line && SEED.states.evaluable.includes(r.state)
      && Object.entries(u.evaluate.eligible || {}).every(([k, vs]) => vs.includes((r.metadata || {})[k])) && (!floor || s.compare(r.version, floor) >= 0));
    const top = pool.sort((a, b) => s.compare(a.version, b.version)).pop();
    const resolvedInLine = resolved(useKey).filter(r => s.line(r.version) === line).map(r => r.version).sort(s.compare).pop();
    if (top && !have.has(top.key) && (!resolvedInLine || s.compare(top.version, resolvedInLine) > 0)) out.push(top);
  }
  return out.slice(0, u.evaluate.max || 3);
}
function proposals(o) {
  o = o || {};
  const now = o.now || new Date().toISOString();
  const out = [];
  for (const u of SEED.uses.filter(x => x.item && !x.from)) {
    const it = item(u.item);
    if (!it) continue;
    for (const r of lanes(u.key)) out.push({ kind: SEED.states.upgradable.includes(r.state) ? "upgrade" : "evaluate", use: u.key, release: r.key, state: r.state,
      detail: SEED.states.upgradable.includes(r.state) ? "verified; resolving it is a governed change" : "compatible; run it as an evaluation lane to earn the evidence " + (u.evidence || []).join(", ") });
    for (const e of resolved(u.key)) {
      const r = release(e.key);
      if (!r) continue;
      const blocking = (r.advisories || []).filter(a => SEED.policy.blockingSeverities.includes(a.severity));
      if (blocking.length && u.production) out.push({ kind: "security", use: u.key, release: r.key, state: r.state, detail: blocking.map(a => a.key + ": " + a.note).join("; ") });
      else if (blocking.length) out.push({ kind: "advisory", use: u.key, release: r.key, state: r.state, detail: "non-production use; " + blocking.map(a => a.key).join(", ") });
      if (SEED.states.replaceable.includes(r.state)) out.push({ kind: "replace", use: u.key, release: r.key, state: r.state, detail: (r.reason || "") + (r.replaced_by ? " → " + r.replaced_by : "") });
      const line = schemeOf(it.category).line(r.version), eol = it.lines && it.lines[line] && it.lines[line].endOfLife;
      if (eol) {
        const days = Math.floor((Date.parse(eol) - Date.parse(now)) / 86400000);
        if (days < SEED.policy.endOfLifeWarningDays) out.push({ kind: "end-of-life", use: u.key, release: r.key, state: r.state, detail: days < 0 ? `line ${line} ended ${eol}` : `line ${line} ends ${eol} (${days} days)` });
      }
    }
  }
  return out;
}
/* drafts the upgrades that are ready; approving and publishing them is still a person's decision */
function autoPropose(actor) {
  const drafted = [];
  for (const p of proposals().filter(x => x.kind === "upgrade")) {
    const r = release(p.release);
    const ready = r.state === N.approved ? r : null;
    if (!ready) { drafted.push({ ...p, drafted: proposeTransition(r.key, N.approved, { reason: "verified for " + p.use + "; proposed by the governance cycle" }, actor).id }); continue; }
    const keep = resolved(p.use).map(x => x.key);
    drafted.push({ ...p, drafted: proposeResolution(p.use, [...keep, r.key], { reason: "add " + r.key + " (proposed by the governance cycle)" }, actor).id });
  }
  return drafted;
}

/* ============================== the seed, the lock ============================== */
const fileSha = f => crypto.createHash("sha256").update(fs.readFileSync(path.join(ROOT, f))).digest("hex");
function snapshotsDoc() { return JSON.parse(fs.readFileSync(path.join(ROOT, SEED.snapshots), "utf8")); }
/* imports the declaration once per process: categories, items, what the sources reported, the
   declared observations, the baseline's evidence and resolutions, then the recorded changes in
   order. Each step is idempotent; a baseline that no longer evaluates fails the import */
let imported = false;
function ensure() {
  if (imported) return;
  K().ensureTables();
  ensureKinds();
  const seed = SEED.actors.seed;
  const report_ = { ingested: [] };
  K().internal.tx(() => {
    for (const c of SEED.categories) defineCategory(c, seed);
    for (const i of SEED.items) defineItem(i, seed);
    for (const s of snapshotsDoc().snapshots) report_.ingested.push(ingest(s.source, s, SEED.actors.discovery));
    /* a source that is a file of the repository (a package manager's lockfile) is read as committed */
    for (const s of SEED.sources.filter(x => x.file)) {
      if (fs.existsSync(path.join(ROOT, s.location))) report_.ingested.push(ingest(s.key, { payload: JSON.parse(fs.readFileSync(path.join(ROOT, s.location), "utf8")), location: s.location, payloadSha256: fileSha(s.location) }, SEED.actors.discovery));
    }
    report_.ingested.push(ingest("declaration", { entries: SEED.declared, location: "lib/seed/technology.json" }, SEED.actors.discovery));
    for (const ev of SEED.baseline.evidence) addEvidence(ev.release, ev, seed);
    evaluateAll();
    for (const [useKey, keys] of Object.entries(SEED.baseline.resolutions)) {
      if (resolution(useKey)) continue;
      const u = use(useKey);
      for (const k of keys) {
        const r = release(k);
        if (!r) bad(`The baseline resolves ${k} for ${useKey}, which no source reported`, 409, "technology_baseline");
        const v = (r.evaluation && r.evaluation.uses || []).find(x => x.use === useKey);
        if (!v || !v.verified) bad(`The baseline resolves ${k} for ${useKey}, but it does not evaluate as verified: ` + J(v ? { checks: v.checks.filter(x => !x.ok), evidence: v.evidence.filter(e => !e.ok) } : "no verdict"), 409, "technology_baseline");
        if (r.state !== N.active) { K().record(r.uid, { state: N.approved, reason: "baseline: " + SEED.baseline.basis }, {}, seed); K().record(r.uid, { state: N.active }, {}, seed); }
      }
      K().createNode(kindName("resolution"), { namespace: SEED.namespace, identifiers: { [SEED.kinds.resolution.scheme]: useKey },
        attributes: { use: useKey, releases: keys.map(k => entryOf(release(k), u)), basis: "baseline: " + SEED.baseline.basis } }, seed);
    }
  });
  /* the recorded governed changes, replayed through the lifecycle: drafted by their author,
     approved by their approver (who must differ), published */
  for (const ch of SEED.changes) {
    if (changes().some(c => c.title === ch.title && c.state === K().SEED.lifecycle.published)) continue;
    const c = ch.type === "resolution" ? proposeResolution(ch.use, ch.releases, { reason: ch.reason, title: ch.title }, ch.proposer)
      : proposeTransition(ch.release, ch.to, { reason: ch.reason, replacedBy: ch.replacedBy, title: ch.title }, ch.proposer);
    approve(c.id, ch.approver, [K().SEED.lifecycle.approvePermission]);
    publish(c.id, ch.approver);
  }
  imported = true;
  return report_;
}
const reset = () => { imported = false; };

/* the repository's resolution, as data with no timestamps: the same registry gives the same bytes */
function lock() {
  ensure();
  const libUse = SEED.uses.find(u => u.from), libSource = source(libUse.from);
  const out = {
    $comment: "Generated by node scripts/technology.js lock from lib/seed/technology.json, lib/seed/technology-discovered.json and package-lock.json through the kernel registry (lib/technology.js). Do not edit: change the declaration, then regenerate; node scripts/technology.js check fails when this file, CI, the Dockerfile or package.json drift from it.",
    generatedFrom: { declaration: fileSha("lib/seed/technology.json"), snapshots: fileSha(SEED.snapshots), lockfile: fileSha(libSource.location) },
    bootstrap: SEED.bootstrap,
    constraints: floors(),
    resolutions: {},
    libraries: null,
    evaluation: [],
    ci: {}
  };
  for (const u of SEED.uses) {
    if (u.from) continue;
    const r = resolution(u.key);
    out.resolutions[u.key] = { label: u.label, production: !!u.production, basis: r ? r.basis : null, releases: r ? r.releases : [] };
  }
  const libs = libraryReleases();
  const scope = s => libs.filter(l => l.metadata.scope === s);
  const unfit = s => scope(s).filter(l => !(l.evaluation && l.evaluation.compatible)).map(l => ({ key: l.key, state: l.state, failing: (l.evaluation ? l.evaluation.checks : []).filter(c => !c.ok).map(c => c.check) }));
  out.libraries = { source: libSource.location, sha256: out.generatedFrom.lockfile, packages: libs.length, runtime: scope("runtime").length, development: scope("development").length,
    runtimeUnfit: unfit("runtime"), developmentUnfit: unfit("development").map(x => x.key) };
  const rt = derivedRelease("ci.runtime");
  const test = resolved("ci.test").map(e => ({ lane: e.version, release: e.key, version: e.version, primary: !!rt && e.key === rt.key, evaluation: false }));
  for (const r of lanes("ci.test")) { test.push({ lane: r.version + " (evaluation)", release: r.key, version: r.version, primary: false, evaluation: true }); out.evaluation.push({ use: "ci.test", release: r.key, state: r.state }); }
  const db = resolved("ci.database")[0];
  out.ci = {
    test, node: rt ? rt.version : null, postgres: db ? db.reference : null,
    runner: (resolved("ci.runner")[0] || {}).version || null,
    actions: Object.fromEntries(resolved("ci.actions").map(e => { const a = e.artifacts[0]; return [a.name, a.name.replace(/@.*$/, "") + "@" + a.commit]; }).sort()),
    container: (resolved("deploy.container")[0] || {}).reference || null
  };
  return out;
}
const lockText = () => JSON.stringify(lock(), null, 1) + "\n";

/* what an administration screen or the CLI shows */
function overview() {
  ensure();
  return { categories: categories(), items: items().length, releases: SEED.states.list.map(s => ({ state: s.key, count: releases({ state: s.key }).length })),
    resolutions: resolutions(), proposals: proposals(), changes: changes(), states: SEED.states, schemes: [...SCHEMES.keys()], protocols: AD.protocols() };
}

module.exports = {
  SEED, registerScheme, registerAdapter: AD.register, schemes: () => [...SCHEMES.keys()],
  ensure, reset, defineCategory, defineItem, registerSource, ingest, rejections, verifyArtifact, addEvidence, evaluate, evaluateAll, report,
  category, categories, item, items, release, releases, resolution, resolutions, history,
  proposeTransition, proposeResolution, approve, publish, rollback, discard, changes,
  floors, lanes, proposals, autoPropose, lock, lockText, overview
};
