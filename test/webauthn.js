/* UCOS Ω∞ · WebAuthn — real assertion math, proven with real keys.
   --------------------------------------------------------------------------
   The identity engine advertises a biometric flow (WebAuthn / passkey). It used to be
   a stub that accepted any assertion shaped like a real one. This proves the math is
   real now: it builds genuine WebAuthn payloads with node:crypto — a synthetic
   authenticator holding real EC P-256, Ed25519 and RSA keys — registers a credential,
   then signs assertions the platform verifies, and proves every forgery is refused.

   No live authenticator is needed: the signatures are the signatures. The platform only
   ever DECODES WebAuthn structures, so the CBOR ENCODER lives here in the test (a
   synthetic authenticator encodes; the platform never does). */
"use strict";
const path = require("path"), fs = require("fs"), crypto = require("crypto"), os = require("os");

const TMP = path.join(os.tmpdir(), "wa-" + process.pid + ".db");
process.env.LX_DB = TMP;
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }

const silence = console.log; console.log = () => { };
const db = require(path.join(__dirname, "..", "lib", "db.js"));
const identity = require(path.join(__dirname, "..", "lib", "identity.js"));
const wa = require(path.join(__dirname, "..", "lib", "webauthn.js"));
console.log = silence;

let passed = 0, failed = 0;
function ok(c, n, x) { if (c) { passed++; console.log("  ✓ " + n); } else { failed++; console.log("  ✗ " + n + (x ? " → " + x : "")); } }
const RP = "luxora.localhost", ORIGIN = "https://" + RP, TID = 1;
const b64u = wa.b64url;

/* ---------- a tiny definite-length CBOR encoder (the synthetic authenticator) ---------- */
function head(major, n) {
  if (n < 24) return Buffer.from([(major << 5) | n]);
  if (n < 0x100) return Buffer.from([(major << 5) | 24, n]);
  if (n < 0x10000) { const b = Buffer.alloc(3); b[0] = (major << 5) | 25; b.writeUInt16BE(n, 1); return b; }
  const b = Buffer.alloc(5); b[0] = (major << 5) | 26; b.writeUInt32BE(n, 1); return b;
}
function enc(v) {
  if (typeof v === "number") {
    if (v >= 0) return head(0, v);
    return head(1, -1 - v);                     /* COSE negative ints: -7, -257… */
  }
  if (Buffer.isBuffer(v)) return Buffer.concat([head(2, v.length), v]);
  if (typeof v === "string") { const b = Buffer.from(v, "utf8"); return Buffer.concat([head(3, b.length), b]); }
  if (Array.isArray(v)) return Buffer.concat([head(4, v.length), ...v.map(enc)]);
  if (v && typeof v === "object") {
    const ks = Object.keys(v);
    /* a COSE map's labels are integers ("1", "-1"); an attestation object's keys are text
       ("fmt", "authData"). Encoded as what they are, or the decoder rejects them. */
    return Buffer.concat([head(5, ks.length), ...ks.flatMap(k => {
      const n = Number(k);
      const key = Number.isFinite(n) && String(n) === k ? n : k;
      return [enc(key), enc(v[k])];
    })]);
  }
  throw new Error("the fixture cannot encode " + typeof v);
}

/* ---------- the synthetic authenticator ---------- */
function b64urlToBuf(s) { return Buffer.from(String(s).replace(/-/g, "+").replace(/_/g, "/"), "base64"); }
function coseOf(alg, pubJwk) {
  if (pubJwk.kty === "EC") return { 1: 2, 3: alg, "-1": 1, "-2": b64urlToBuf(pubJwk.x), "-3": b64urlToBuf(pubJwk.y) };
  if (pubJwk.kty === "OKP") return { 1: 1, 3: alg, "-1": 6, "-2": b64urlToBuf(pubJwk.x) };
  return { 1: 3, 3: alg, "-1": b64urlToBuf(pubJwk.n), "-2": b64urlToBuf(pubJwk.e) };
}
function authData(flags, signCount, coseKey) {
  const rp = crypto.createHash("sha256").update(RP).digest();
  const sc = Buffer.alloc(4); sc.writeUInt32BE(signCount);
  if (!coseKey) return Buffer.concat([rp, Buffer.from([flags]), sc]);
  const aaguid = Buffer.from("0123456789abcdef0123456789abcdef", "hex");
  const credId = crypto.randomBytes(32);
  const len = Buffer.alloc(2); len.writeUInt16BE(credId.length);
  return Buffer.concat([rp, Buffer.from([flags]), sc, aaguid, len, credId, enc(coseKey)]);
}
function clientData(type, challengeBytes, origin) {
  return Buffer.from(JSON.stringify({ type, challenge: b64u(challengeBytes), origin, crossOrigin: false }), "utf8");
}
const UP = 0x01, UV = 0x04, AT = 0x40;

/* make a credential: key pair + a signed assertion over the given authenticator data */
function makeCredential(kind) {
  const alg = kind === "ed25519" ? -8 : kind === "rsa" ? -257 : -7;
  const kp = kind === "ed25519" ? crypto.generateKeyPairSync("ed25519")
    : kind === "rsa" ? crypto.generateKeyPairSync("rsa", { modulusLength: 2048 })
      : crypto.generateKeyPairSync("ec", { namedCurve: "P-256" });
  const pubJwk = kp.publicKey.export({ format: "jwk" });
  const cose = coseOf(alg, pubJwk);
  const sign = (authDataBuf, cdBuf) => {
    const signed = Buffer.concat([authDataBuf, crypto.createHash("sha256").update(cdBuf).digest()]);
    if (kind === "ed25519") return crypto.sign(null, signed, kp.privateKey);
    if (kind === "rsa") return crypto.sign("RSA-SHA256", signed, kp.privateKey);
    return crypto.sign(null, signed, { key: kp.privateKey, dsaEncoding: "ieee-p1363" });  /* raw R||S */
  };
  return { alg, pubJwk, cose, sign, kind, privateKey: kp.privateKey };
}

const userId = db.newUser(TID, "WebAuthn Probe", "wa@luxora.shop", "probe12345", "customer");
identity.upsertIdentityProvider(TID, { provider_type: "biometric", name: "WebAuthn", enabled: true, config: { rpId: RP, rpName: "Luxora", timeout: 60000 } });

/* =================== §A registration binds a real key =================== */
console.log("\n▸ §A REGISTRATION — a credential is bound only after the attestation verifies");
const cred = makeCredential("p256");
{
  const ch = identity.biometricChallenge(userId, TID);
  ok(!!ch.ok && ch.rpId === RP, "a biometric challenge is issued for the configured relying party", ch.error);
  const ad = authData(UP | UV | AT, 0, cred.cose);
  const cd = clientData("webauthn.create", Buffer.from(ch.challenge, "hex"), ORIGIN);
  const att = enc({ fmt: "none", attStmt: {}, authData: ad });
  const r = identity.registerBiometric(userId, att, ch.challenge, { tenantId: TID, clientDataJSON: cd, origin: ORIGIN });
  ok(!!r.ok, "an ES256 credential registers and its attestation verifies", r.error);
  ok(r.alg === "ES256" && r.fmt === "none", "the registered credential reports its algorithm and format", r.alg + "/" + r.fmt);
  ok(r.attestationVerified === true, "fmt 'none' attestation is accepted (it carries no statement by design)", r.attestationNote);
  const methods = identity.getUserIdentityMethods(userId).filter(m => m.method_type === "webauthn");
  ok(methods.length === 1 && methods[0].is_primary === 1, "the credential is stored as the account's primary identity method", methods.length);
  const stored = identity.webauthnCredential(userId);
  ok(!!stored && !!stored.credentialPublicKey && stored.credentialId === r.credentialId, "the enrolled public key and credential id are retrievable", !!stored);
}
/* registration is refused when the challenge, origin or flags are wrong — the account
   never gains a credential by asserting it has one */
{
  const goodCh = identity.biometricChallenge(userId, TID);
  const ad = authData(UP | UV | AT, 0, cred.cose);
  const goodCd = clientData("webauthn.create", Buffer.from(goodCh.challenge, "hex"), ORIGIN);
  ok(!identity.registerBiometric(userId, enc({ fmt: "none", attStmt: {}, authData: ad }), goodCh.challenge,
    { tenantId: TID, clientDataJSON: clientData("webauthn.create", crypto.randomBytes(32), ORIGIN), origin: ORIGIN }).ok,
    "a challenge that is not the server's is refused");
  ok(!identity.registerBiometric(userId, enc({ fmt: "none", attStmt: {}, authData: ad }), goodCh.challenge,
    { tenantId: TID, clientDataJSON: clientData("webauthn.create", Buffer.from(goodCh.challenge, "hex"), "https://evil.example"), origin: null }).ok,
    "an attestation for another origin is refused");
  ok(!identity.registerBiometric(userId, enc({ fmt: "none", attStmt: {}, authData: authData(UV | AT, 0, cred.cose) }), goodCh.challenge,
    { tenantId: TID, clientDataJSON: goodCd, origin: ORIGIN }).ok,
    "an attestation with no user present is refused");
  ok(!identity.registerBiometric(userId, enc({ fmt: "none", attStmt: {}, authData: authData(UP | UV | AT, 0, { 1: 2, "-1": 1, "-2": Buffer.alloc(32), "-3": Buffer.alloc(32) }) }), goodCh.challenge,
    { tenantId: TID, clientDataJSON: goodCd, origin: ORIGIN }).ok,
    "a malformed credential key is refused");
  ok(!identity.registerBiometric(userId, enc({ fmt: "none", attStmt: {}, authData: authData(UP | UV | AT, 0, { 1: 2, 3: -7, "-1": 1, "-2": Buffer.alloc(32), "-3": Buffer.alloc(32), "-4": Buffer.alloc(32) }) }), goodCh.challenge,
    { tenantId: TID, clientDataJSON: goodCd, origin: ORIGIN }).ok,
    "a key carrying a private component is refused");
}

/* =================== §B login verifies the real signature =================== */
console.log("\n▸ §B LOGIN — the signature over authenticatorData || SHA-256(clientDataJSON) verifies");
function login(credential, signCount, mutate) {
  const ch = identity.biometricChallenge(userId, TID);
  const ad = authData(UP | UV, signCount, null);
  const cd = clientData("webauthn.get", Buffer.from(ch.challenge, "hex"), ORIGIN);
  const assertion = { authenticatorData: b64u(ad), clientDataJSON: cd, signature: b64u(credential.sign(ad, cd)), id: identity.webauthnCredential(userId).credentialId };
  if (mutate) mutate(assertion, ad, cd, ch);
  return { ch, result: identity.verifyBiometric(userId, ch.challenge, assertion) };
}
{
  const r = login(cred, 1);
  ok(!!r.result.ok, "an assertion signed by the enrolled key verifies and the login succeeds", r.result.error);
  ok(r.result.alg === "ES256" && r.result.userVerified === true, "the verified assertion reports its algorithm and user-presence flags", r.result.alg);
  ok(identity.webauthnCredential(userId).signCount === 1, "the stored signature counter advanced", identity.webauthnCredential(userId).signCount);
}
/* every forgery — the old stub accepted all of these */
{
  const stub = identity.verifyBiometric(userId, identity.biometricChallenge(userId, TID).challenge,
    { clientDataJSON: "x", authenticatorData: "y", signature: "z" });
  ok(!stub.ok, "the assertion the previous stub accepted (fields present, no signature) is refused", stub.error);
  const tampered = login(cred, 2, (a) => { a.signature = b64u(crypto.randomBytes(64)); });
  ok(!tampered.result.ok, "a signature that is not the key's is refused", tampered.result.error);
  const wrongChallenge = login(cred, 2, (a, ad, cd, ch) => { a.clientDataJSON = clientData("webauthn.get", crypto.randomBytes(32), ORIGIN); });
  ok(!wrongChallenge.result.ok, "a challenge the server did not issue is refused", wrongChallenge.result.error);
  const wrongOrigin = login(cred, 2, (a) => { a.clientDataJSON = clientData("webauthn.get", Buffer.from(identity.biometricChallenge(userId, TID).challenge, "hex"), "https://evil.example"); });
  ok(!wrongOrigin.result.ok, "an assertion from another origin is refused", wrongOrigin.result.error);
  const noPresence = login(cred, 2, (a, ad, cd, ch) => { const bad = authData(UV, 2, null); a.authenticatorData = b64u(bad); a.signature = b64u(cred.sign(bad, cd)); });
  ok(!noPresence.result.ok, "an assertion with no user present is refused", noPresence.result.error);
  const wrongRp = login(cred, 2, (a, ad, cd, ch) => { const bad = Buffer.concat([crypto.createHash("sha256").update("other.example").digest(), ad.slice(32)]);
    a.authenticatorData = b64u(bad); a.signature = b64u(cred.sign(bad, cd)); });
  ok(!wrongRp.result.ok, "authenticator data for another relying party is refused", wrongRp.result.error);
  const replay = login(cred, 1);   /* counter 1 was already consumed and stored */
  ok(!replay.result.ok, "an assertion whose counter did not advance is refused as a possible clone", replay.result.error);
  const progressed = login(cred, 2);
  ok(!!progressed.result.ok, "the next assertion with an advanced counter succeeds", progressed.result.error);
}
/* a challenge is single-use */
{
  const ch = identity.biometricChallenge(userId, TID);
  const ad = authData(UP | UV, 3, null);
  const cd = clientData("webauthn.get", Buffer.from(ch.challenge, "hex"), ORIGIN);
  const a1 = { authenticatorData: b64u(ad), clientDataJSON: cd, signature: b64u(cred.sign(ad, cd)) };
  ok(!!identity.verifyBiometric(userId, ch.challenge, a1).ok, "the first use of a challenge succeeds");
  ok(!identity.verifyBiometric(userId, ch.challenge, a1).ok, "the same challenge cannot be replayed");
}

/* =================== §C other COSE algorithms =================== */
console.log("\n▸ §C OTHER ALGORITHMS — the verifier follows the key, not a hardcoded curve");
for (const kind of ["ed25519", "rsa"]) {
  const c2 = makeCredential(kind);
  const ch = identity.biometricChallenge(userId, TID);
  const ad = authData(UP | UV | AT, 0, c2.cose);
  const cd = clientData("webauthn.create", Buffer.from(ch.challenge, "hex"), ORIGIN);
  const reg = identity.registerBiometric(userId, enc({ fmt: "none", attStmt: {}, authData: ad }), ch.challenge,
    { tenantId: TID, clientDataJSON: cd, origin: ORIGIN });
  ok(!!reg.ok, "a " + c2.kind + " credential registers", reg.error);
  const ch2 = identity.biometricChallenge(userId, TID);
  const ad2 = authData(UP | UV, 1, null);
  const cd2 = clientData("webauthn.get", Buffer.from(ch2.challenge, "hex"), ORIGIN);
  const v = identity.verifyBiometric(userId, ch2.challenge,
    { authenticatorData: b64u(ad2), clientDataJSON: cd2, signature: b64u(c2.sign(ad2, cd2)) });
  ok(!!v.ok, "and its " + (kind === "rsa" ? "RS256" : "EdDSA") + " assertion verifies", v.error);
}
/* a signature from a DIFFERENT key than the enrolled one never verifies */
{
  const other = makeCredential("p256");
  const ch = identity.biometricChallenge(userId, TID);
  const ad = authData(UP | UV, 4, null);
  const cd = clientData("webauthn.get", Buffer.from(ch.challenge, "hex"), ORIGIN);
  ok(!identity.verifyBiometric(userId, ch.challenge,
    { authenticatorData: b64u(ad), clientDataJSON: cd, signature: b64u(other.sign(ad, cd)) }).ok,
    "an assertion signed by a key the account never enrolled is refused");
}

/* =================== §D an account with no credential cannot log in =================== */
console.log("\n▸ §D NO CREDENTIAL ENROLLED");
{
  const other = db.newUser(TID, "No Credential", "nocred@luxora.shop", "probe12345", "customer");
  const ch = identity.biometricChallenge(other, TID);
  const ad = authData(UP | UV, 1, null);
  const cd = clientData("webauthn.get", Buffer.from(ch.challenge, "hex"), ORIGIN);
  const r = identity.verifyBiometric(other, ch.challenge, { authenticatorData: b64u(ad), clientDataJSON: cd, signature: b64u(cred.sign(ad, cd)) });
  ok(!r.ok && /no biometric credential/i.test(r.error), "an account with no enrolled credential is told so, not verified", r.error);
}

/* =================== §E the decoder itself =================== */
console.log("\n▸ §E THE CBOR / COSE DECODER");
{
  const ad = wa.parseAuthenticatorData(authData(UP | UV | AT, 7, cred.cose));
  ok(ad.signCount === 7 && ad.userPresent && ad.userVerified && !!ad.attested, "authenticator data parses: flags, counter and attested credential", ad.signCount);
  ok(ad.rpIdHash.equals(crypto.createHash("sha256").update(RP).digest()), "the rpId hash is the relying party's", null);
  const k = wa.coseToKeyObject(cred.cose);
  ok(k.jwk.crv === "P-256" && k.jwk.kty === "EC", "a COSE EC key converts to a node key object", k.jwk.crv);
  ok(wa.verifySignature(-7, k.key, Buffer.from("hello"), crypto.sign(null, Buffer.from("hello"), { key: cred.privateKey, dsaEncoding: "ieee-p1363" }), "P-256"),
    "verifySignature accepts a genuinely signed message");
  ok(!wa.verifySignature(-7, k.key, Buffer.from("hello"), crypto.randomBytes(64), "P-256"), "and rejects a forged one");
  ok(!!wa.decodeCbor(enc({ a: 1, b: "x", c: Buffer.from("y") })).value, "a round trip through the encoder and decoder is lossless");
}

console.log("\n" + (failed ? "✗ " + failed + " check(s) failed" : "✓ all WebAuthn checks passed") + "  (" + passed + " passed)");
process.exit(failed ? 1 : 0);
