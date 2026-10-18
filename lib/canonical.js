/* UCOS Ω∞ · the canonical registry — one compiled source of truth, sealed.
   --------------------------------------------------------------------------
   The platform's Law 002 (Knowledge Once) is now enforced by construction: the
   corpora AUTHOR the constitution, this module COMPILES it into one artifact,
   and the runtime reads ONLY that artifact. Nothing else is a declaration source.

     compile()   corpora + authored registry JSON + console navs
                 → one registry object (documents, parts, sections, articles,
                   concepts, registries, edges, universes, atoms, artifacts,
                   content, console sections, vocabularies) — deterministic, so
                 a re-compile diffs clean.
     seal()      AES-256-GCM envelope, HMAC-SHA256 authenticated, with a
                 per-input SHA-256 manifest. The master key lives in
                 data/registry.json (gitignored, 0600) or LX_REGISTRY_KEY.
                 Zero dependencies: node:crypto only. The envelope is a portable
                 versioned JSON wrapper ("agnostic") — no vendor format, no lock-in.
     load()      verify signature → check manifest → decrypt → expose. Tamper or
                 drift is detected; recovery is a re-compile from the sources,
                 which are the authority (a seal proves provenance, it is not the
                 authority). LX_REGISTRY_STRICT=1 refuses silent recovery and
                 makes a pinned registry a hard gate — the production posture.

   Why authentication matters more than secrecy here: the registry is constitutional
   content, not a secret. The seal's real job is that an on-disk edit — by an
   operator who skipped the compile, or by anyone else — can never change what the
   platform operates without being detected. Confidentiality comes with it. */

"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const REG = path.join(ROOT, "_registry");
const DATA = path.join(ROOT, "data");
const ENVELOPE = path.join(REG, "canonical.lxr");   /* the sealed SSOT — runtime reads only this */
const READABLE = path.join(REG, "canonical.json");  /* derived readable view for operators */
const KEYRING_FILE = path.join(DATA, "registry.json");
const SCHEMA = "https://ucos.io/registry/envelope.v1.json";
const CANONICAL_SCHEMA = "https://ucos.io/registry/canonical.v1.json";
const ALG = "aes-256-gcm";
const REGISTRY_ID = "UCOS-CANONICAL";
const VERSION = "Omega-Infinity";

try { fs.mkdirSync(DATA, { recursive: true, mode: 0o700 }); } catch (e) { }

/* ============================ L-key: the registry keyring ============================
    Separate from the customer-secret master key (data/master.json, L6) on purpose:
    least privilege — the key that seals the constitution is not the key that
    decrypts a store's gateway credentials, and compromising one does not
    compromise the other. Same pattern, own store. */
let keyring = {}, keyVersion = "";
function b64(buf) { return Buffer.from(buf).toString("base64"); }
function unb64(s) { return Buffer.from(s, "base64"); }

function loadKeyring() {
  if (process.env.LX_REGISTRY_KEY) {
    const v = "env";
    keyring[v] = crypto.createHash("sha256").update(String(process.env.LX_REGISTRY_KEY)).digest();
    keyVersion = v;
    return;
  }
  let state = { current: null, keys: {} };
  try { state = JSON.parse(fs.readFileSync(KEYRING_FILE, "utf8")); } catch (e) { }
  if (!state.current || !state.keys[state.current]) return rotateKey(true);
  keyVersion = state.current;
  for (const [v, k] of Object.entries(state.keys)) keyring[v] = Buffer.from(k, "hex");
}
function persistKeyring() {
  const out = { current: keyVersion, keys: {} };
  for (const [v, k] of Object.entries(keyring)) out.keys[v] = k.toString("hex");
  try { fs.writeFileSync(KEYRING_FILE, JSON.stringify(out), { mode: 0o600 }); } catch (e) { }
}
function rotateKey(initial) {
  const v = "k" + (Object.keys(keyring).length + 1);
  keyring[v] = crypto.randomBytes(32);
  keyVersion = v;
  persistKeyring();
  return v;
}
loadKeyring();
if (!Object.keys(keyring).length) rotateKey(true);
function masterKey(version) {
  const k = keyring[version || keyVersion];
  if (!k) throw new Error("canonical: unknown key version " + version);
  return k;
}

/* HKDF-SHA256 derivation: one master key → a distinct encryption and signing key
   per envelope, salted so two envelopes sealed on the same key never reuse keys. */
function derive(master, saltB64) {
  const salt = unb64(saltB64);
  const enc = crypto.hkdfSync("sha256", master, salt, "luxora.canonical.enc", 32);
  const sig = crypto.hkdfSync("sha256", master, salt, "luxora.canonical.sig", 32);
  return { enc: Buffer.from(enc), sig: Buffer.from(sig) };
}

/* ============================ the inputs (what may be compiled) ============================ */
/* the corpus sources are the documents the corpus parser reads (lib/seed/ucos.json → DOCS),
   so the seal hashes exactly what the compile parses. A hand-kept copy of this list once named
   a file that did not exist (UCOS-Zero-Hardcoding-Constitution.md for the UCRS constitution), so
   that constitution was never in the seal's manifest. The console navs are inputs too. */
const INPUT_FILES = require("./seed/ucos.json").DOCS.map(d => d.file).filter(f => !f.endsWith("/"))
  .concat(["public/js/platform.js", "public/js/admin.js"]);
const REGISTRY_INPUTS = [
  "_registry/primitives.json", "_registry/terminology.json", "_registry/domains.json",
  "_registry/manifest.json", "_registry/content-map.json",
  "_registry/content-core.json", "_registry/content-ext.json", "_registry/content-commerce.json",
  "_registry/content-twin-agent.json", "_registry/content-runtime-data.json", "_registry/content-sec-ops-dep-qlt.json",
  "_registry/content-platform.json", "_registry/codebase.json", "_registry/roadmap.json", "_registry/classification.json", "_registry/alignment.json", "_registry/documents.json"
];
function allInputs() { return INPUT_FILES.concat(REGISTRY_INPUTS).concat(COMPILER_INPUTS); }

/* the compiler itself is an input. The seal promises "this registry is exactly what
   these sources compile to" — but a change to the PARSE code changes the registry even
   when no source file moved. Without the compiler in the manifest, a code edit leaves
   the seal reporting clean while the runtime serves a registry the current code would
   not produce: the payload goes shape-stale silently (a payload field added by the new
   code is simply absent from the sealed one, and the manifest cannot see it). Hashing
   these files makes a compiler edit drift the seal, so load() re-compiles — and under
   LX_REGISTRY_STRICT it becomes a hard stop, which is the right deploy discipline for
   a pinned registry (ship the re-compile with the code). */
const COMPILER_INPUTS = ["lib/canonical.js", "lib/ucos.js", "lib/ucos-registry.js", "lib/ucos-universes.js"];

/* sha-256 over every input's BYTES — the same "did the source change?" question the
   old digest asked, now covering the console navs and the content registries too
   (they were silently outside the digest before). This is the drift oracle. */
function liveManifest() {
  const out = {};
  for (const rel of allInputs()) {
    const p = path.join(ROOT, rel);
    let body = null;
    try { body = fs.readFileSync(p); } catch (e) { out[rel] = { bytes: -1, sha256: null, missing: true }; continue; }
    out[rel] = { bytes: body.length, sha256: crypto.createHash("sha256").update(body).digest("hex") };
  }
  return out;
}
function manifestDigest(manifest) {
  const h = crypto.createHash("sha256");
  for (const rel of Object.keys(manifest).sort()) {
    const m = manifest[rel];
    h.update(rel + "|" + m.bytes + "|" + (m.sha256 || "MISSING"));
  }
  return h.digest("hex");
}
function manifestDelta(live, sealed) {
  const changed = [], missing = [], added = [];
  for (const rel of Object.keys(sealed)) if (!live[rel]) missing.push(rel);
  for (const rel of Object.keys(live)) {
    if (!sealed[rel]) { added.push(rel); continue; }
    if (live[rel].sha256 !== sealed[rel].sha256 || live[rel].bytes !== sealed[rel].bytes) changed.push(rel);
  }
  return { changed, missing, added, clean: !changed.length && !missing.length && !added.length };
}

/* ============================ the seal ============================ */
function seal(payload, manifest) {
  const master = masterKey();
  const salt = crypto.randomBytes(16);
  const { enc, sig } = derive(master, b64(salt));
  const iv = crypto.randomBytes(12);
  const body = Buffer.from(JSON.stringify(payload), "utf8");
  const header = {
    schema: SCHEMA, registryId: REGISTRY_ID, version: VERSION,
    sealedAt: new Date().toISOString(), keyVersion,
    alg: ALG, kdf: "hkdf-sha256", salt: b64(salt), iv: b64(iv)
  };
  const aad = Buffer.from(JSON.stringify(header));
  const cipher = crypto.createCipheriv(ALG, enc, iv);
  cipher.setAAD(aad);
  const ct = Buffer.concat([cipher.update(body), cipher.final()]);
  const tag = cipher.getAuthTag();
  const payloadB64 = b64(ct);
  /* authenticate the WHOLE envelope: header + manifest + ciphertext + iv + tag.
     GCM already authenticates the payload against the header as AAD; the HMAC
     makes the manifest (the drift oracle itself) non-repudiable, so an attacker
     cannot swap in a stale-but-valid manifest to hide that sources moved. */
  const sigInput = JSON.stringify(header) + JSON.stringify(manifest) + payloadB64 + b64(iv) + b64(tag);
  const signature = crypto.createHmac("sha256", sig).update(sigInput).digest("hex");
  return Object.assign({}, header, { manifest, payload: payloadB64, tag: b64(tag), signature });
}

/* throws on any tamper — never returns a partial or unverified registry */
function open(envelope) {
  if (!envelope || envelope.schema !== SCHEMA) throw new Error("canonical: not a sealed registry envelope");
  if (envelope.registryId !== REGISTRY_ID) throw new Error("canonical: envelope is for a different registry");
  const master = masterKey(envelope.keyVersion);
  const { enc, sig } = derive(master, envelope.salt);
  const header = JSON.parse(JSON.stringify(envelope));
  for (const k of ["manifest", "payload", "tag", "signature"]) delete header[k];
  const sigInput = JSON.stringify(header) + JSON.stringify(envelope.manifest) + envelope.payload + envelope.iv + envelope.tag;
  const expect = crypto.createHmac("sha256", sig).update(sigInput).digest("hex");
  const got = Buffer.from(String(envelope.signature || ""), "hex");
  if (got.length !== 32 || !crypto.timingSafeEqual(got, Buffer.from(expect, "hex")))
    throw new Error("canonical: envelope signature invalid — the sealed registry was tampered with");
  const decipher = crypto.createDecipheriv(ALG, enc, unb64(envelope.iv));
  decipher.setAAD(Buffer.from(JSON.stringify(header)));
  decipher.setAuthTag(unb64(envelope.tag));
  const plain = Buffer.concat([decipher.update(unb64(envelope.payload)), decipher.final()]).toString("utf8");
  const payload = JSON.parse(plain);
  if (!payload || payload.schema !== CANONICAL_SCHEMA) throw new Error("canonical: sealed payload is not the canonical registry");
  return payload;
}

/* ============================ the compile ============================
    Heavy machinery is required lazily and ONLY here, so requiring this module
    costs nothing at runtime: consumers get the compiled registry, never a parse. */
function parseSources() {
  const ucos = require("./ucos.js");
  const reg = require("./ucos-registry.js");
  const parsed = ucos.parseSources();      /* the 11 text corpora + ureg, one parse contract */
  const registryFiles = reg.readRegistryFiles();   /* the authored registry JSON, verbatim */
  return { parsed, registryFiles };
}

/* the console's grant surface is declared by the navs that RENDER it — a grant
   section and its nav button can never disagree when one is derived from the
   other. Extracted from the NAV literal itself (bracket-balanced, so nothing
   outside the nav array can masquerade as a view), so a new view is a nav edit
   and the section list follows with no second copy to maintain. */
function consoleSections() {
  const out = { platform: [], admin: [], adminLabels: {}, adminNavSec: {}, adminNavFit: {} };
  const leaf = /\[\s*"([a-z][a-z0-9_-]*)"\s*,\s*"/g;
  for (const which of [["platform", "public/js/platform.js"], ["admin", "public/js/admin.js"]]) {
    let src = null;
    try { src = fs.readFileSync(path.join(ROOT, which[1]), "utf8"); } catch (e) { continue; }
    /* locate the NAV literal and slice it with bracket balancing — the leaf regex
       alone would also match data arrays elsewhere in the bundle and invent views
       the console does not render (a Zero-Missing / No-Leakage violation). */
    const at = src.search(/const\s+NAV\s*=\s*\[/);
    if (at < 0) continue;
    let depth = 0, end = -1;
    for (let i = src.indexOf("[", at); i < src.length; i++) {
      const c = src[i];
      if (c === "[") depth++;
      else if (c === "]") { depth--; if (depth === 0) { end = i; break; } }
    }
    if (end < 0) continue;
    const block = src.slice(at, end);
    const seen = new Set();
    let m;
    while ((m = leaf.exec(block))) if (!seen.has(m[1])) { seen.add(m[1]); out[which[0]].push(m[1]); }
    /* the store console's leaf labels, so a screen that configures sections (platform
       kinds, roles) can name them as the menu does */
    if (which[0] === "admin") {
      const lab = /\[\s*"([a-z][a-z0-9_-]*)"\s*,\s*"([^"]*)"/g;
      while ((m = lab.exec(block))) out.adminLabels[m[1]] = m[2];
    }
  }
  /* the STORE console redirects several nav leaves to one shared GRANT section
     (promotions + goip → offers; structure → tenancy; sso → settings) through a
     NAVSEC map declared next to the nav. The grant surface must resolve through
     the same map the console's canSee() does, so the map is extracted here too —
     brace-balanced like the nav, so a stray brace in a string can't trip it. The
     platform console has no such indirection: its canSee() keys off the leaf. */
  {
    let src = null;
    try { src = fs.readFileSync(path.join(ROOT, "public/js/admin.js"), "utf8"); } catch (e) { src = null; }
    if (src) {
      const at = src.search(/const\s+NAVSEC\s*=\s*\{/);
      if (at >= 0) {
        let depth = 0, end = -1;
        for (let i = src.indexOf("{", at); i < src.length; i++) {
          const ch = src[i];
          if (ch === "{") depth++;
          else if (ch === "}") { depth--; if (depth === 0) { end = i; break; } }
        }
        if (end >= 0) {
          const pair = /([A-Za-z0-9_-]+)\s*:\s*"([^"]+)"/g;
          let m;
          while ((m = pair.exec(src.slice(at, end + 1)))) out.adminNavSec[m[1]] = m[2];
        }
      }
      /* NAVFIT — each store section's fitness to a tenant's deploy mode and
         industries (a section is not universal). A JSON object literal, harvested
         with the same brace balancing as NAVSEC so a stray brace in a string can't
         fool it; an unparseable map fails closed to "every section fits" rather
         than silently narrowing the grant surface */
      const fAt = src.search(/const\s+NAVFIT\s*=\s*\{/);
      if (fAt >= 0) {
        let depth = 0, fEnd = -1;
        for (let i = src.indexOf("{", fAt); i < src.length; i++) {
          const ch = src[i];
          if (ch === "{") depth++;
          else if (ch === "}") { depth--; if (depth === 0) { fEnd = i; break; } }
        }
        if (fEnd >= 0) {
          try { out.adminNavFit = JSON.parse(src.slice(src.indexOf("{", fAt), fEnd + 1)); }
          catch (e) { console.error("canonical: NAVFIT would not parse — no section fitness is enforced: " + e.message); }
        }
      }
    }
  }
  return out;
}

/* the concept register: every corpus concept, once, with its kind and (when it is a
   concept) its one owning domain. Derived at compile time from _registry/classification.json,
   so it is sealed with the registry and recomputed whenever a rule or a review changes.
     kind      identifier / statement / fragment by the declared patterns, else concept
     owner     an exact registry name (a domain, an owned name, a law or kernel part), else the
               owner its reviewed container was given (a majority across the containers that
               hold it), else the rules on its own name; a "Structural" container passes the
               decision to the concept's name. What is left is unplaced, and counted. */
function classifyRegister(parsed, universes, rf) {
  const cl = rf.classification;
  if (!cl) return null;
  const kinds = (cl.kinds || []).map(k => ({ kind: k.kind, re: new RegExp(k.pattern) }));
  const rules = (cl.owners || []).map(r => ({ owner: r.owner, re: new RegExp(r.pattern, "i") }));
  const subjects = cl.subjects ? { owner: cl.subjects.owner, re: new RegExp(cl.subjects.pattern, "i") } : null;
  const byRule = text => { for (const r of rules) if (r.re.test(text)) return r.owner; return subjects && subjects.re.test(text) ? subjects.owner : null; };
  const D = rf.domains;
  const exact = new Map();
  for (const d of D.domains) { exact.set(d.name.toLowerCase(), d.name); for (const o of d.owns || []) exact.set(o.toLowerCase(), d.name); }
  for (const l of D.laws || []) for (const n of [l.name].concat(l.aliases || [])) exact.set(n.toLowerCase(), "Constitutional Authority");
  for (const k of D.kernel || []) exact.set(k.name.toLowerCase(), k.owner);
  const reviewed = cl.containers || {};
  /* a concept reviewed on its own (it sits only in structural containers) */
  const conceptReview = cl.concepts || {};
  const containerOwner = id => {
    const r = reviewed[id];
    if (r) return r.owner === "Structural" ? { owner: null, basis: "structural" } : { owner: r.owner, basis: "reviewed" };
    return null;
  };
  const uniOf = new Map();
  for (const u of universes) for (const n of u.concepts || []) if (!uniOf.has(n.toLowerCase())) uniOf.set(n.toLowerCase(), "u:" + u.key);
  const seen = new Map();
  for (const doc of Object.keys(parsed)) for (const c of parsed[doc].concepts) {
    let e = seen.get(c.key);
    if (!e) { e = { key: c.key, name: c.name, containers: [] }; seen.set(c.key, e); }
    if (c.container_key) e.containers.push({ id: doc + ":" + c.container_key, name: c.container_name || "" });
  }
  const rows = [], counts = { concepts: 0, byKind: {}, byBasis: {}, byOwner: {}, unplaced: 0 };
  for (const e of seen.values()) {
    const name = String(e.name || "").trim();
    const kindRow = kinds.find(k => k.re.test(name));
    const cr = conceptReview[e.key];
    const kind = cr && cr.owner === "NotAConcept" ? "fragment" : kindRow ? kindRow.kind : "concept";
    counts.byKind[kind] = (counts.byKind[kind] || 0) + 1;
    if (kind !== "concept") { rows.push([e.key, kind, null, cr ? "reviewed-concept" : null]); continue; }
    counts.concepts++;
    let owner = exact.get(name.toLowerCase()) || null, basis = owner ? "exact" : null;
    if (!owner && cr) { owner = cr.owner; basis = "reviewed-concept"; }
    if (!owner) {
      const ids = e.containers.map(x => x.id);
      const u = uniOf.get(name.toLowerCase()); if (u) ids.unshift(u);
      const votes = new Map(); let structural = false, unreviewed = null;
      for (const id of ids) {
        const r = containerOwner(id);
        if (!r) { if (!unreviewed) unreviewed = e.containers.find(x => x.id === id); continue; }
        if (r.basis === "structural") { structural = true; continue; }
        votes.set(r.owner, (votes.get(r.owner) || 0) + 1);
      }
      if (votes.size) { owner = [...votes.entries()].sort((a, b) => b[1] - a[1])[0][0]; basis = "reviewed-container"; }
      else if (!structural && unreviewed && unreviewed.name) { owner = byRule(unreviewed.name); basis = owner ? "container-rule" : null; }
    }
    if (!owner) { owner = byRule(name); basis = owner ? "name-rule" : null; }
    if (!owner) { counts.unplaced++; basis = "unplaced"; }
    counts.byBasis[basis] = (counts.byBasis[basis] || 0) + 1;
    if (owner) counts.byOwner[owner] = (counts.byOwner[owner] || 0) + 1;
    rows.push([e.key, kind, owner, basis]);
  }
  counts.distinct = seen.size;
  /* the containers that matter are those holding a concept, and every declared universe */
  const held = new Set([...seen.values()].flatMap(e => e.containers.map(x => x.id)).concat(universes.map(u => "u:" + u.key)));
  counts.containers = held.size;
  counts.containersReviewed = [...held].filter(id => reviewed[id]).length;
  /* low-confidence reviews stay visible: the queue a person confirms or corrects */
  /* which confidence levels send a decision to the review queue is declared, not named here */
  const queued = new Set((cl.confidenceLevels || []).filter(l => l.queue).map(l => l.key));
  counts.reviewQueue = Object.keys(reviewed).filter(id => queued.has(reviewed[id].confidence)).sort()
    .concat(Object.keys(conceptReview).filter(k => queued.has(conceptReview[k].confidence)).sort().map(k => "c:" + k));
  counts.conceptsReviewed = Object.keys(conceptReview).length;
  return { counts, rows };
}

function compile() {
  const ucos = require("./ucos.js");
  const univ = require("./ucos-universes.js");
  const { parsed, registryFiles } = parseSources();
  /* universes: the corpus declaration walk — the same one the fold captured, now
     one step of the compile. Provenance (doc + line) rides every row. */
  const universes = univ.discoverFromCorpus().map(u => ({
    key: u.key, name: u.name, sourceDoc: u.sourceDoc, sourceLine: u.sourceLine || null,
    family: u.registry || null, concepts: (u.concepts || []).slice()
  })).sort((a, b) => a.key.localeCompare(b.key));
  const payload = {
    schema: CANONICAL_SCHEMA,
    registryId: REGISTRY_ID,
    version: VERSION,
    compiledAt: new Date().toISOString(),
    documents: ucos.DOCS.map(d => ({
      id: d.id, file: d.file, code: d.code, name: d.name, kind: d.kind,
      noUniverses: !!d.noUniverses, registry: !!d.registry
    })),
    parsed,
    universes,
    registryFiles,
    console: consoleSections(),
    vocabularies: {
      /* the corpus's own declarations, read from the documents at compile time —
         at runtime ucos.productUniverses() etc. return THESE compiled values */
      productUniverses: ucos.productUniversesSrc(),
      lifecycleStates: ucos.lifecycleStatesSrc(),
      transitionGrammar: ucos.transitionGrammarSrc()
    }
  };
  payload.register = classifyRegister(parsed, universes, registryFiles);
  payload.counts = {
    documents: payload.documents.length,
    universes: universes.length,
    concepts: Object.keys(parsed).reduce((a, k) => a + parsed[k].concepts.length, 0),
    sections: Object.keys(parsed).reduce((a, k) => a + parsed[k].sections.length, 0),
    articles: Object.keys(parsed).reduce((a, k) => a + parsed[k].articles.length, 0),
    registries: Object.keys(parsed).reduce((a, k) => a + parsed[k].registries.length, 0),
    parts: Object.keys(parsed).reduce((a, k) => a + parsed[k].parts.length, 0),
    productUniverses: payload.vocabularies.productUniverses.length,
    platformSections: payload.console.platform.length,
    adminSections: payload.console.admin.length
  };
  const manifest = liveManifest();
  payload.digest = manifestDigest(manifest);
  return { payload, manifest };
}

/* ============================ load: verify, decrypt, expose ============================ */
let _cache = null, _compiledAt = 0;
/* read at CALL time: an operator can flip a deployment into strict mode without a
   restart, and the test exercises both modes in one process */
const strict = () => !!process.env.LX_REGISTRY_STRICT;

function writeArtifacts(payload, envelope) {
  try { fs.writeFileSync(ENVELOPE, JSON.stringify(envelope, null, 1) + "\n"); } catch (e) { }
  try { fs.writeFileSync(READABLE, JSON.stringify(payload, null, 1) + "\n"); } catch (e) { }
}
function removeArtifacts() {
  for (const p of [ENVELOPE, READABLE]) { try { fs.unlinkSync(p); } catch (e) { } }
}

/* the only function the runtime calls. Returns the canonical registry, or throws —
   it NEVER returns a partial, unverified or stale registry. */
function load(force) {
  if (!force && _cache) return _cache;
  let envelope = null;
  try { envelope = JSON.parse(fs.readFileSync(ENVELOPE, "utf8")); } catch (e) { envelope = null; }
  const live = liveManifest();

  if (envelope) {
    let payload = null;
    try { payload = open(envelope); }
    catch (e) {
      /* the seal is broken. The sources are the authority, so recovery is a
         re-compile — but a strict deployment treats this as a hard stop, because
         a pinned registry that will not verify is an incident, not an inconvenience. */
      if (strict()) throw new Error("canonical: sealed registry failed verification and LX_REGISTRY_STRICT is set — refusing to recover: " + e.message);
      console.error("canonical: sealed registry would not verify, re-compiling from sources: " + e.message);
      envelope = null;
    }
    if (payload) {
      const delta = manifestDelta(live, envelope.manifest);
      if (delta.clean) { _cache = payload; _compiledAt = Date.now(); return payload; }
      const why = ["changed: " + delta.changed.join(", "), "missing: " + delta.missing.join(", "), "added: " + delta.added.join(", ")].join("; ");
      if (strict()) throw new Error("canonical: sources drifted from the sealed registry and LX_REGISTRY_STRICT is set — re-compile before booting: " + why);
      console.error("canonical: sources drifted from the sealed registry (" + why + ") — re-compiling");
      envelope = null;
    }
  }

  /* no usable seal: compile from the sources, then seal, so the runtime always
     operates a sealed artifact even when one had to be built on the way in. */
  const { payload, manifest } = compile();
  envelope = seal(payload, manifest);
  writeArtifacts(payload, envelope);
  _cache = payload; _compiledAt = Date.now();
  return payload;
}
function get() { return load(false); }
function refresh() { _cache = null; return load(true); }

/* ============================ read API ============================ */
function parsed() { return get().parsed; }
function documents() { return get().documents; }
function universes() { return get().universes; }
function registryFiles() { return get().registryFiles; }
function consoleSec() { return get().console; }
function vocab(name) { return get().vocabularies[name] || []; }
function counts() { return get().counts; }
function digest() { return manifestDigest(liveManifest()); }

/* searchable: any declaration, by key, name or alias, with its provenance and its place in
   the register (category, owning domain). Register entries (categories, domains,
   primitives, terms, artifacts) rank first — exact name, then prefix, then contains — so
   "time" finds the Time domain before every concept that mentions time. Filters narrow
   by facet: kind, category (id or name) and owner. */
function register() {
  const rf = registryFiles();
  const D = rf.domains, cats = D.categories || [], doms = D.domains || [];
  const catOf = id => cats.find(c => c.categoryId === id) || null;
  const domOf = name => doms.find(d => d.name === name) || null;
  const ownerOf = name => (doms.find(d => (d.owns || []).includes(name)) || {}).name || null;
  const rows = [];
  for (const c of cats) rows.push({ kind: "category", key: c.categoryId, name: c.name, aliases: [], text: c.covers, category: c, owner: null, provenance: "_registry/domains.json" });
  for (const d of doms) rows.push({ kind: "domain", key: d.domainId, name: d.name, aliases: d.owns || [], text: (d.responsible || []).join(" "), category: catOf(d.category), owner: d.name, provenance: "_registry/domains.json" });
  for (const p of rf.primitives.primitives) { const o = ownerOf(p.name); rows.push({ kind: "primitive", key: p.id, name: p.name, aliases: [], text: p.definition, category: catOf((domOf(o) || {}).category), owner: o, provenance: "_registry/primitives.json" }); }
  for (const t of rf.terminology.terms) { const o = ownerOf(t.canonicalName); rows.push({ kind: "term", key: t.termId, name: t.canonicalName, aliases: t.aliases || [], text: t.definition, category: catOf((domOf(o) || {}).category), owner: o, provenance: "_registry/terminology.json" }); }
  for (const l of D.laws || []) rows.push({ kind: "law", key: l.lawId, name: l.name, aliases: l.aliases || [], text: l.statement, category: catOf("C01"), owner: "Constitutional Authority", provenance: "_registry/domains.json" });
  for (const k of D.kernel || []) rows.push({ kind: "kernel", key: k.partId, name: k.name, aliases: [], text: k.statement, category: catOf((domOf(k.owner) || {}).category), owner: k.owner, provenance: "_registry/domains.json" });
  for (const m of (rf.codebase || {}).modules || []) for (const p of m.parts || [{ owner: m.owner, part: m.note || "" }]) rows.push({ kind: "module", key: m.path, name: m.path, aliases: [], text: p.part || "", category: catOf((domOf(p.owner) || {}).category), owner: p.owner, provenance: "_registry/codebase.json" });
  for (const st of (rf.roadmap || {}).steps || []) rows.push({ kind: "step", key: st.stepId, name: st.title, aliases: [], text: st.status, category: null, owner: null, provenance: "_registry/roadmap.json" });
  for (const dc of (rf.roadmap || {}).decisions || []) rows.push({ kind: "decision", key: dc.decisionId, name: dc.question, aliases: [], text: dc.decision, category: null, owner: null, provenance: "_registry/roadmap.json" });
  /* the parts of other structures that call themselves domains, each with its register owner */
  const fsAlign = require("fs");
  for (const sys of (rf.alignment || {}).systems || []) {
    if (!sys.owners) continue;
    let list = [];
    try { list = JSON.parse(fsAlign.readFileSync(path.join(ROOT, sys.source), "utf8"))[sys.list] || []; } catch (e) { }
    for (const it of list) { const o = sys.owners[it[sys.key]]; rows.push({ kind: "aligned", key: sys.system + ":" + it[sys.key], name: it.name || it[sys.key], aliases: [], text: sys.name, category: catOf((domOf(o) || {}).category), owner: o, provenance: "_registry/alignment.json" }); }
  }
  for (const doc of (rf.documents || {}).documents || []) rows.push({ kind: "doc", key: doc.path, name: doc.path, aliases: [], text: doc.status + " " + (doc.note || doc.supersededBy || doc.generatedBy || ""), category: catOf((domOf(doc.owner) || {}).category), owner: doc.owner, provenance: "_registry/documents.json" });
  for (const a of rf.manifest.artifacts) rows.push({ kind: "artifact", key: a.id, name: a.title, aliases: [], text: "", category: catOf((domOf(a.owner) || {}).category), owner: a.owner, provenance: "_registry/manifest.json" });
  return rows;
}
/* the concept register, joined to each concept's name and first source, built once per load */
let _conceptIndex = null, _conceptFor = null;
function conceptIndex() {
  const p = get();
  if (_conceptIndex && _conceptFor === p) return _conceptIndex;
  const first = new Map();
  for (const docId of Object.keys(p.parsed)) for (const c of p.parsed[docId].concepts) if (!first.has(c.key)) first.set(c.key, { name: c.name, where: docId + ":" + (c.line || "?") });
  _conceptIndex = ((p.register || {}).rows || []).map(([key, kind, owner, basis]) => {
    const f = first.get(key) || { name: key, where: "" };
    return { key, kind, owner, basis, name: f.name, lower: String(f.name).toLowerCase(), where: f.where };
  });
  _conceptFor = p;
  return _conceptIndex;
}
function catOfOwner(owner) {
  const D = registryFiles().domains, d = D.domains.find(x => x.name === owner);
  return d ? (D.categories || []).find(c => c.categoryId === d.category) || null : null;
}
function search(q, opts) {
  const o = opts || {};
  const needle = String(q || "").trim().toLowerCase();
  if (!needle) return [];
  const lim = o.limit || 50;
  const wantCat = o.category ? String(o.category).toLowerCase() : null;
  const out = [];
  const push = (kind, key, name, where, extra) => out.push(Object.assign({ kind, key, name, provenance: where }, extra || {}));

  const facetOk = r => (!o.kind || r.kind === o.kind)
    && (!wantCat || (r.category && (r.category.categoryId.toLowerCase() === wantCat || r.category.name.toLowerCase() === wantCat)))
    && (!o.owner || String(r.owner || "").toLowerCase() === String(o.owner).toLowerCase());
  const score = r => {
    const names = [r.name].concat(r.aliases).map(x => String(x).toLowerCase());
    if (names.includes(needle) || String(r.key).toLowerCase() === needle) return 3;
    if (names.some(n => n.startsWith(needle))) return 2;
    if (names.some(n => n.includes(needle)) || String(r.text || "").toLowerCase().includes(needle)) return 1;
    return 0;
  };
  register().map(r => ({ r, s: score(r) })).filter(x => x.s && facetOk(x.r))
    .sort((a, b) => b.s - a.s || a.r.name.localeCompare(b.r.name))
    .forEach(({ r }) => push(r.kind, r.key, r.name, r.provenance, {
      category: r.category ? r.category.categoryId + " " + r.category.name : null, owner: r.owner
    }));
  /* concepts come from the concept register, once each, with their kind, owner and
     category, so the owner and category facets narrow them too. Universes and documents
     carry no owner of their own and answer only when no facet narrows the search. */
  if (out.length <= lim && (!o.kind || o.kind === "concept")) {
    for (const c of conceptIndex()) {
      if (out.length > lim) break;
      if (!(c.key.includes(needle) || c.lower.includes(needle))) continue;
      const cat = c.owner ? catOfOwner(c.owner) : null;
      if (wantCat && !(cat && (cat.categoryId.toLowerCase() === wantCat || cat.name.toLowerCase() === wantCat))) continue;
      if (o.owner && String(c.owner || "").toLowerCase() !== String(o.owner).toLowerCase()) continue;
      push("concept", c.key, c.name, c.where, { category: cat ? cat.categoryId + " " + cat.name : null, owner: c.owner, conceptKind: c.kind, basis: c.basis });
    }
  }
  const corpus = !o.kind || ["universe", "document"].includes(o.kind);
  if (corpus && !wantCat && !o.owner) {
    for (const u of universes()) {
      if (out.length > lim) break;
      if ((!o.kind || o.kind === "universe") && (u.key.includes(needle) || String(u.name).toLowerCase().includes(needle)))
        push("universe", u.key, u.name, u.sourceDoc + ":" + (u.sourceLine || "?"));
    }
    if (out.length <= lim && (!o.kind || o.kind === "document"))
      for (const d of documents()) if (d.id.includes(needle) || String(d.name).toLowerCase().includes(needle)) push("document", d.id, d.name, d.file);
  }
  return out.slice(0, lim);
}

/* verify without loading the payload into the cache: the operator's pre-flight check. */
function verify() {
  let envelope = null;
  try { envelope = JSON.parse(fs.readFileSync(ENVELOPE, "utf8")); } catch (e) { return { ok: false, error: "no sealed registry on disk — run npm run registry" }; }
  let payload = null;
  try { payload = open(envelope); } catch (e) { return { ok: false, error: e.message }; }
  const delta = manifestDelta(liveManifest(), envelope.manifest);
  return {
    ok: delta.clean, registryId: envelope.registryId, version: envelope.version,
    sealedAt: envelope.sealedAt, keyVersion: envelope.keyVersion,
    digest: payload.digest, counts: payload.counts,
    drift: delta.clean ? null : delta
  };
}

module.exports = {
  ENVELOPE, READABLE, SCHEMA, CANONICAL_SCHEMA, REGISTRY_ID, allInputs,
  load, get, refresh, compile, seal, open, verify, search, register, classifyRegister,
  parsed, documents, universes, registryFiles, consoleSec, vocab, counts, digest,
  liveManifest, manifestDigest, manifestDelta, consoleSections, writeArtifacts, removeArtifacts
};
