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
const INPUT_FILES = [
  "Architecture1.txt", "Architecture2.txt", "Architecture3.txt", "Architecture4.txt",
  "Architecture5.txt", "Architecture6.txt",
  "UCOS-Universal-Capability-Operating-System.md", "UCOS_Omega_Constitutional_Architecture_v1.0.md",
  "UCOS-Zero-Hardcoding-Constitution.md", "UCOS-Constitutional-Addendum.md", "UCOS-Constitutional-Master-Architecture.md",
  "public/js/platform.js", "public/js/admin.js"
];
const REGISTRY_INPUTS = [
  "_registry/primitives.json", "_registry/terminology.json", "_registry/domains.json",
  "_registry/manifest.json", "_registry/content-map.json",
  "_registry/content-core.json", "_registry/content-ext.json", "_registry/content-commerce.json",
  "_registry/content-twin-agent.json", "_registry/content-runtime-data.json", "_registry/content-sec-ops-dep-qlt.json"
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

/* searchable: any declaration, by key or label, with its provenance — so the
   registry is queryable, not just readable. */
function search(q, opts) {
  const o = opts || {};
  const needle = String(q || "").trim().toLowerCase();
  if (!needle) return [];
  const out = [];
  const push = (kind, key, name, where) => out.push({ kind, key, name, provenance: where });
  for (const u of universes()) {
    if (u.key.includes(needle) || String(u.name).toLowerCase().includes(needle))
      push("universe", u.key, u.name, u.sourceDoc + ":" + (u.sourceLine || "?"));
    if (out.length > 200) break;
  }
  if (out.length < 200) {
    const P = parsed();
    for (const docId of Object.keys(P)) {
      for (const c of P[docId].concepts) {
        if (c.key.includes(needle) || String(c.name).toLowerCase().includes(needle))
          push("concept", c.key, c.name, docId + ":" + (c.line || "?"));
        if (out.length > 200) break;
      }
      if (out.length > 200) break;
    }
  }
  if (out.length < 200) for (const d of documents()) if (d.id.includes(needle) || String(d.name).toLowerCase().includes(needle)) push("document", d.id, d.name, d.file);
  return out.slice(0, o.limit || 50);
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
  load, get, refresh, compile, seal, open, verify, search,
  parsed, documents, universes, registryFiles, consoleSec, vocab, counts, digest,
  liveManifest, manifestDigest, manifestDelta, consoleSections, writeArtifacts, removeArtifacts
};
