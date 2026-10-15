/* LUXORA Platform - security core: defense-in-depth layers with real cryptography.
   L1 transport headers+TLS · L2 session CSRF · L3 credential KDF (scrypt+pepper) · L4 password policy
   L5 at-rest envelope encryption (AES-256-GCM) · L6 key hierarchy+rotation · L7 hash-chained audit
   L8 rate limiting+lockout (durable) · L9 SRI+input hardening · L10 least-privilege/tenant isolation */
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const DATA_DIR = path.join(__dirname, "..", "data");
/* L6 persists the keyring to data/master.json. A fresh checkout has no data/ directory and
   persistKeyring writes with a bare writeFileSync, so the store is created up front (0700:
   it holds the master key) rather than crashing at require time before anything can boot. */
try { fs.mkdirSync(DATA_DIR, { recursive: true, mode: 0o700 }); } catch (e) { }
const PEPPER = String(process.env.LUXORA_PEPPER || "");

/* db handle injected by db.js at load (avoids circular require) */
let DB = null;
function initDb(h) { DB = h; restoreState(); }
function g(...a) { if (!DB) throw new Error("security.initDb not called"); return DB.get(...a); }
function r(...a) { if (!DB) throw new Error("security.initDb not called"); return DB.run(...a); }
function q(...a) { if (!DB) throw new Error("security.initDb not called"); return DB.all(...a); }

function rewrapSecrets(enc) {
  let n = 0;
  for (const row of q("SELECT tenant_id, provider_id, config FROM tenant_gateways WHERE config LIKE '%lux.v1.%'")) {
    let cfg = {}; try { cfg = JSON.parse(row.config || "{}"); } catch (e) { continue; }
    const out = {};
    for (const [k, v] of Object.entries(cfg)) {
      const ctx = row.tenant_id + "|" + row.provider_id + "|" + k;
      if (typeof v === "string" && v.startsWith("lux.v1.")) { const plain = safeDecrypt(v, ctx); out[k] = plain ? enc(plain, ctx) : v; }
      else out[k] = v;
    }
    r("UPDATE tenant_gateways SET config=? WHERE tenant_id=? AND provider_id=?", JSON.stringify(out), row.tenant_id, row.provider_id);
    n++;
  }
  return n;
}
function platSetting(key, dflt) { try { const x = g("SELECT value FROM platform_settings WHERE key=?", key); return x ? JSON.parse(x.value) : dflt; } catch (e) { return dflt; } }
function platSet(key, val) { r("INSERT INTO platform_settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", key, JSON.stringify(val)); }

/* ================= L6: key hierarchy & rotation ================= */
let keyring = {};
let keyVersion = "";
function b64u(buf) { return buf.toString("base64url"); }
function loadKeyring() {
  let state = { current: null, keys: {} };
  try { state = JSON.parse(fs.readFileSync(path.join(DATA_DIR, "master.json"), "utf8")); } catch (e) { }
  if (process.env.LUXORA_MASTER_KEY) {
    const v = state.current || "k1";
    keyring[v] = Buffer.from(String(process.env.LUXORA_MASTER_KEY).padEnd(64, "0").slice(0, 64), "hex");
    keyVersion = v; return;
  }
  if (!state.current || !state.keys[state.current]) return rotateKey(true);
  for (const [v, k] of Object.entries(state.keys)) keyring[v] = Buffer.from(k, "hex");
  keyVersion = state.current;
}
function persistKeyring() {
  const out = { current: keyVersion, keys: {} };
  for (const [v, k] of Object.entries(keyring)) out.keys[v] = k.toString("hex");
  fs.writeFileSync(path.join(DATA_DIR, "master.json"), JSON.stringify(out), { mode: 0o600 });
}
function rotateKey(initial) {
  const v = "k" + (Object.keys(keyring).length + 1);
  keyring[v] = crypto.randomBytes(32);
  keyVersion = v;
  persistKeyring();
  if (!initial) rewrapAll();
  return v;
}
loadKeyring();
if (Object.keys(keyring).length === 0) rotateKey(true);
function masterKey() { return keyring[keyVersion]; }
let rewrapHook = null;
function onRewrap(fn) { rewrapHook = fn; }
function rewrapAll() { if (rewrapHook) try { rewrapHook(encryptSecret) } catch (e) { console.error("rewrap failed", e.message); } }

/* ================= L5: envelope encryption (AES-256-GCM, AAD-bound) ================= */
function encryptSecret(plaintext, context) {
  if (plaintext == null || plaintext === "") return plaintext;
  if (typeof plaintext === "string" && plaintext.startsWith("lux.v1.")) return plaintext;
  const iv = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv("aes-256-gcm", masterKey(), iv);
  cipher.setAAD(Buffer.from(String(context || "luxora")));
  const ct = Buffer.concat([cipher.update(String(plaintext), "utf8"), cipher.final()]);
  return ["lux", "v1", keyVersion, b64u(iv), b64u(cipher.getAuthTag()), b64u(ct)].join(".");
}
function decryptSecret(sealed, context) {
  if (sealed == null || sealed === "") return sealed;
  const parts = String(sealed).split(".");
  if (parts.length !== 6 || parts[0] !== "lux" || parts[1] !== "v1") return sealed;
  const [, , kv, iv, tag, ct] = parts;
  const key = keyring[kv];
  if (!key) throw new Error("Unknown key version in sealed value");
  const d = crypto.createDecipheriv("aes-256-gcm", key, Buffer.from(iv, "base64url"));
  d.setAAD(Buffer.from(String(context || "luxora")));
  d.setAuthTag(Buffer.from(tag, "base64url"));
  return Buffer.concat([d.update(Buffer.from(ct, "base64url")), d.final()]).toString("utf8");
}
function safeDecrypt(v, ctx) { try { return decryptSecret(v, ctx); } catch (e) { return ""; } }
function sealConfig(tenantId, providerId, config, secretKeys) {
  const out = {};
  for (const [k, v] of Object.entries(config || {})) out[k] = (secretKeys || []).includes(k) ? encryptSecret(v, tenantId + "|" + providerId + "|" + k) : v;
  return JSON.stringify(out);
}
function unsealConfig(tenantId, providerId, configJson) {
  let cfg = {}; try { cfg = JSON.parse(configJson || "{}"); } catch (e) { }
  const out = {};
  for (const [k, v] of Object.entries(cfg)) out[k] = typeof v === "string" && v.startsWith("lux.v1.") ? safeDecrypt(v, tenantId + "|" + providerId + "|" + k) : v;
  return out;
}

/* ================= PLATFORM POLICY ================= */
const DEFAULT_POLICY = {
  minPasswordLength: 8, requireLetterDigit: true, blockCommon: true,
  lockoutThreshold: 5, lockoutBaseSec: 30, lockoutCapSec: 900,
  authPerMin: 30, apiPerMin: 600,
  csrfEnabled: true, hsts: true, demoHints: true, cspInlineStyles: true,
  kdfV2: { logN: 17, r: 8, p: 2 },
  provisioning: { defaultPlanId: 1, seedCatalogByDefault: true, sandboxGatewaysByDefault: true, currencyOverridesAllowed: false, couponsAllowed: true, fiscalContextsAllowed: false, globalOffersAllowed: true }
};
let policyCache = null, policyTs = 0;
function policy(force) {
  if (!force && policyCache && Date.now() - policyTs < 5000) return policyCache;
  let saved = {}; try { saved = DB ? platSetting("policy", {}) : {}; } catch (e) { saved = {}; }
  policyCache = JSON.parse(JSON.stringify({ ...DEFAULT_POLICY, ...saved,
    kdfV2: { ...DEFAULT_POLICY.kdfV2, ...(saved.kdfV2 || {}) },
    provisioning: { ...DEFAULT_POLICY.provisioning, ...(saved.provisioning || {}) } }));
  policyTs = Date.now();
  return policyCache;
}
function setPolicy(patch) {
  let cur = {}; try { cur = DB ? platSetting("policy", {}) : {}; } catch (e) { }
  const merged = { ...cur, ...patch,
    kdfV2: { ...(cur.kdfV2 || {}), ...(patch.kdfV2 || {}) },
    provisioning: { ...(cur.provisioning || {}), ...(patch.provisioning || {}) } };
  try { platSet("policy", merged); } catch (e) { }
  policyCache = null; return policy(true);
}

/* ================= L3: credential KDF ================= */
const KDF = { v1: { N: 1 << 14, r: 8, p: 1 } };
function kdfParams(ver) {
  const pol = policy();
  return ver === "v2" ? { N: 1 << Math.max(14, Math.min(20, (pol.kdfV2 && pol.kdfV2.logN) || 17)), r: (pol.kdfV2 && pol.kdfV2.r) || 8, p: (pol.kdfV2 && pol.kdfV2.p) || 2 } : (KDF[ver] || KDF.v1);
}
function kdfInput(pw, context) { return Buffer.concat([Buffer.from(String(pw), "utf8"), Buffer.from(PEPPER + (context || ""), "utf8")]); }
function kdfHash(pw, salt, ver, context) {
  const p = kdfParams(ver);
  return crypto.scryptSync(kdfInput(pw, context), Buffer.from(salt, "hex"), 32, { N: p.N, r: p.r, p: p.p, maxmem: 512 * 1024 * 1024 }).toString("hex");
}
/* the same KDF on libuv's thread pool. scryptSync at login cost ~100ms+ of event loop per
   attempt — every anonymous login/registration/hint request stalled every other request.
   Request paths use these; boot-time seeding keeps the sync form. */
function kdfHashAsync(pw, salt, ver, context) {
  const p = kdfParams(ver);
  return new Promise((resolve, reject) => crypto.scrypt(kdfInput(pw, context), Buffer.from(salt, "hex"), 32, { N: p.N, r: p.r, p: p.p, maxmem: 512 * 1024 * 1024 },
    (err, key) => err ? reject(err) : resolve(key.toString("hex"))));
}
async function kdfVerifyAsync(pw, salt, expectedHex, ver, context) {
  const a = Buffer.from(await kdfHashAsync(pw, salt, ver, context), "hex");
  const b = Buffer.from(String(expectedHex || ""), "hex");
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}
function newSalt() { return crypto.randomBytes(16).toString("hex"); }
function currentKdf() { return "v2"; }
function kdfVerify(pw, salt, expectedHex, ver, context) {
  const a = Buffer.from(kdfHash(pw, salt, ver, context), "hex");
  const b = Buffer.from(expectedHex, "hex");
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

/* ================= L4: password policy ================= */
const COMMON = new Set(["password", "password1", "password12", "password123", "passw0rd", "qwerty", "123456", "12345678", "letmein", "welcome", "admin123", "changeme", "test1234", "iloveyou", "abc12345", "monkey123"]);
function checkPassword(pw, userContext) {
  const p = String(pw || ""); const pol = policy();
  if (p.length < pol.minPasswordLength) return "Password must be at least " + pol.minPasswordLength + " characters";
  if (pol.blockCommon && COMMON.has(p.toLowerCase())) return "Password is too common";
  if (pol.requireLetterDigit && (!/[A-Za-z]/.test(p) || !/[0-9]/.test(p))) return "Password needs at least one letter and one digit";
  if (userContext && p.toLowerCase() === String(userContext).toLowerCase()) return "Password must differ from your email";
  return null;
}

/* ================= L8: durable rate limiting + login lockout ================= */
const buckets = new Map();     /* key -> [tokens, ts] */
const loginAttempts = new Map(); /* email -> [fails, until] */
function takeBucket(key, capacity, refillPerSec, cost) {
  const now = Date.now();
  let b = buckets.get(key);
  if (!b) { b = [capacity, now]; buckets.set(key, b); }
  b[0] = Math.min(capacity, b[0] + (now - b[1]) / 1000 * refillPerSec); b[1] = now;
  const c = cost || 1;
  if (b[0] < c) return false;
  b[0] -= c; return true;
}
function RateLimiter(capacity, refillPerSec) {
  const cap = typeof capacity === "function" ? capacity : () => capacity;
  const ref = typeof refillPerSec === "function" ? refillPerSec : () => refillPerSec;
  return function (key, cost) { return takeBucket(key, cap(), ref(), cost); };
}
function noteLoginFail(email) {
  const e = String(email || "").toLowerCase();
  const cur = loginAttempts.get(e) || [0, 0];
  cur[0]++;
  const pol = policy();
  if (cur[0] >= pol.lockoutThreshold) cur[1] = Date.now() + Math.min(pol.lockoutCapSec, pol.lockoutBaseSec * Math.pow(2, cur[0] - pol.lockoutThreshold)) * 1000;
  loginAttempts.set(e, cur); schedulePersist();
  return cur;
}
function noteLoginOk(email) { loginAttempts.delete(String(email || "").toLowerCase()); schedulePersist(); }
function lockState(email) {
  const a = loginAttempts.get(String(email || "").toLowerCase());
  if (!a) return { locked: false };
  if (a[1] && Date.now() < a[1]) return { locked: true, retryAfterSec: Math.ceil((a[1] - Date.now()) / 1000) };
  if (a[1]) a[1] = 0;
  return { locked: false };
}
/* persistence: snapshot to security_state every 5s if dirty */
let dirty = false, persistTimer = null;
function schedulePersist() { dirty = true; if (!persistTimer) persistTimer = setInterval(persistState, 5000); if (persistTimer.unref) persistTimer.unref(); }
function persistState() {
  if (!DB || !dirty) return; dirty = false;
  try {
    const snap = { buckets: [...buckets.entries()].filter(([, b]) => b[0] < (policy().apiPerMin || 600)).slice(0, 2000), attempts: [...loginAttempts.entries()].filter(([, a]) => a[1] > Date.now() || a[0] > 0).slice(0, 2000), at: Date.now() };
    platSet("security_state", snap);
  } catch (e) { }
}
function restoreState() {
  if (!DB) return;
  try {
    const s = platSetting("security_state", null);
    if (!s) return;
    if (Date.now() - s.at < 15 * 60000) {
      for (const [k, v] of s.buckets || []) buckets.set(k, v);
      for (const [k, v] of s.attempts || []) loginAttempts.set(k, v);
    }
  } catch (e) { }
}

/* ================= L2: CSRF ================= */
function csrfToken() { return crypto.randomBytes(16).toString("hex"); }
function csrfOk(req, session) {
  const sent = req.headers["x-csrf"];
  return !!(sent && session.csrf && String(sent).length === String(session.csrf).length && crypto.timingSafeEqual(Buffer.from(String(sent)), Buffer.from(String(session.csrf))));
}

/* ================= L7: hash chain ================= */
function chainRow(prevHash, payload) {
  return crypto.createHash("sha256").update(String(prevHash || "GENESIS") + "|" + JSON.stringify(payload)).digest("hex");
}

/* ================= L1: headers & TLS ================= */
function securityHeaders(tls, pol) {
  const p = pol || policy();
  return {
    "Content-Security-Policy": "default-src 'self'; img-src 'self' data:; style-src 'self'" + (p.cspInlineStyles ? " 'unsafe-inline'" : "") + "; script-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "same-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
    "Cross-Origin-Resource-Policy": "same-origin",
    "Cross-Origin-Opener-Policy": "same-origin",
    "X-XSS-Protection": "0"
  };
}
function tlsReady() {
  if (process.env.LUX_TLS !== "1") return null;
  try {
    if (process.env.LUX_TLS_KEY && process.env.LUX_TLS_CERT && fs.existsSync(process.env.LUX_TLS_KEY) && fs.existsSync(process.env.LUX_TLS_CERT))
      return { key: fs.readFileSync(process.env.LUX_TLS_KEY), cert: fs.readFileSync(process.env.LUX_TLS_CERT) };
  } catch (e) { console.error("custom TLS material failed:", e.message); }
  const key = path.join(DATA_DIR, "tls-key.pem"), crt = path.join(DATA_DIR, "tls-cert.pem");
  if (fs.existsSync(key) && fs.existsSync(crt)) return { key: fs.readFileSync(key), cert: fs.readFileSync(crt) };
  try {
    const { execSync } = require("child_process");
    execSync(`openssl req -x509 -newkey rsa:2048 -nodes -keyout "${key}" -out "${crt}" -days 365 -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost,DNS:*.localhost" 2>/dev/null`, { stdio: "ignore" });
    fs.chmodSync(key, 0o600);
    return { key: fs.readFileSync(key), cert: fs.readFileSync(crt) };
  } catch (e) { console.error("TLS cert generation failed (openssl missing?) — HTTP only", e.message); return null; }
}

/* ================= L9: SRI ================= */
const sriCache = new Map(); /* abs path -> { mtimeMs, size, integrity, version } */
function sriFile(abs) {
  let st; try { st = fs.statSync(abs); } catch (e) { return null; }
  if (!st.isFile()) return null;
  const hit = sriCache.get(abs);
  if (hit && hit.mtimeMs === st.mtimeMs && hit.size === st.size) return hit; /* rehash only when the file changes */
  const buf = fs.readFileSync(abs);
  const integrity = "sha384-" + crypto.createHash("sha384").update(buf).digest("base64");
  const version = integrity.slice(7).replace(/[^A-Za-z0-9]/g, "").slice(0, 10);
  const ent = { mtimeMs: st.mtimeMs, size: st.size, integrity, version };
  sriCache.set(abs, ent);
  return ent;
}
function applySri(html, pubDir) {
  const root = path.normalize(pubDir) + path.sep;
  const inject = (tag, attr) => {
    if (/\bintegrity=/i.test(tag)) return tag; /* never double-inject */
    const m = new RegExp("\\b" + attr + "=\"([^\"]+)\"").exec(tag);
    if (!m) return tag;
    const raw = m[1].replace(/&amp;/g, "&");
    if (/^(https?:)?\/\//i.test(raw) || /^data:/i.test(raw)) return tag; /* leave external/data URIs alone */
    const clean = raw.split("?")[0].split("#")[0];
    const abs = path.normalize(path.join(pubDir, clean));
    if (abs.indexOf(root) !== 0) return tag;
    const ent = sriFile(abs);
    if (!ent) return tag;
    return tag.replace(m[0], attr + "=\"" + clean + "?v=" + ent.version + "\" integrity=\"" + ent.integrity + "\" crossorigin=\"anonymous\"");
  };
  return html
    .replace(/<script\b[^>]*\bsrc="[^"]+"[^>]*>/gi, t => inject(t, "src"))
    .replace(/<link\b[^>]*\bhref="[^"]+\.css"[^>]*>/gi, t => inject(t, "href"));
}

/* ================= scorecard ================= */
function scorecard(extra) {
  const p = policy();
  return [
    { n: 1, layer: "Transport", detail: `CSP (${p.cspInlineStyles ? "inline styles allowed via policy" : "inline styles FORBIDDEN via policy"}), frame-ancestors none, nosniff, TLS ${extra.tls ? "ENABLED" : "opt-in (LUX_TLS=1, optional LUX_TLS_KEY/CERT)"}`, status: "active" },
    { n: 2, layer: "Session integrity", detail: "CSRF double-submit " + (p.csrfEnabled ? "ENFORCED" : "policy-disabled") + ", timing-safe, tenant-pinned state", status: "active" },
    { n: 3, layer: "Credential KDF", detail: `scrypt v2 N=2^${p.kdfV2.logN} r=${p.kdfV2.r} p=${p.kdfV2.p}${p ? (extra.pepper ? " + pepper" : " (no pepper env)") : ""}, transparent v1→v2 upgrade`, status: "active" },
    { n: 4, layer: "Password policy", detail: `min ${p.minPasswordLength} chars, ${p.requireLetterDigit ? "letter+digit" : "classes off"}, ${p.blockCommon ? "common-blocklist on" : "blocklist off"}, reuse history`, status: "active" },
    { n: 5, layer: "At-rest encryption", detail: "AES-256-GCM envelope seals, AAD-bound tenant|provider|field, auth-tag tamper detection", status: "active" },
    { n: 6, layer: "Key management", detail: `versioned master keyring (${extra.keyInfo.count} keys, current ${extra.keyInfo.version}), rotation auto-rewraps`, status: "active" },
    { n: 7, layer: "Audit integrity", detail: "SHA-256 hash-chained audit log, verify endpoints, tamper detection", status: "active" },
    { n: 8, layer: "Abuse control", detail: `durable token-bucket (${p.authPerMin}/min auth, ${p.apiPerMin}/min api), lockout after ${p.lockoutThreshold} failures`, status: "active" },
    { n: 9, layer: "Supply chain & input", detail: "SRI sha384 on every JS/CSS, parameterized SQL, strict entity schema validation, HTML escaping", status: "active" },
    { n: 10, layer: "Isolation & least privilege", detail: "tenant-scoped rows, platformOnly entity guards, role gates, suspended-store block, policy gates (coupons/currency/fiscal)", status: "active" }
  ];
}

module.exports = { kdfHashAsync, kdfVerifyAsync,
  initDb, rewrapSecrets, platSetting, platSet, policy, setPolicy, DEFAULT_POLICY,
  encryptSecret, decryptSecret, safeDecrypt, sealConfig, unsealConfig, rotateKey, keyInfo: () => ({ version: keyVersion, count: Object.keys(keyring).length }),
  onRewrap, kdfHash, newSalt, currentKdf, kdfVerify, checkPassword,
  RateLimiter, noteLoginFail, noteLoginOk, lockState, persistState,
  csrfToken, csrfOk, chainRow, securityHeaders, tlsReady, applySri, scorecard
};
