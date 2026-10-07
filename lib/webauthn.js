/* UCOS Ω∞ · WebAuthn — real assertion math, zero dependencies (node:crypto only).
   --------------------------------------------------------------------------
   The identity engine advertises a biometric flow (WebAuthn / passkey). For a long
   time that was a documented stub: the "verification" checked only that an assertion
   HAD the two fields a real one has, and accepted anything that did — so a login
   method was advertised that no cryptography backed. This module is the math.

   What the platform needs, and no more:
     decodeCbor             definite-length CBOR. attestationObject, attStmt and
                            COSE_Key are all definite-length; clientDataJSON is JSON
                            and authenticatorData is a fixed binary struct, so a
                            streaming/indefinite decoder is not required (and would
                            be dead code).
     parseAuthenticatorData the binary struct: rpIdHash · flags · signCount ·
                            attestedCredentialData · extensions.
     coseToKeyObject        COSE_Key -> a node KeyObject (ES256/384/512 · RS256 ·
                            PS256 · EdDSA), so verification uses the platform's own
                            signature primitives instead of an ad-hone one.
     verifyAttestation      registration: binds a credential public key to an account
                            after checking the client data and (for packed / fido-u2f)
                            the attestation certificate's own signature.
     verifyAssertion        login: the security property. Proves the caller holds the
                            credential's private key by verifying its signature over
                            authenticatorData || SHA-256(clientDataJSON), after
                            checking the challenge the server issued, the origin and
                            the authenticator flags.

   The platform never ENCODES CBOR — it only consumes what an authenticator produced,
   so there is no encoder here. Test vectors are built by the test suite. */
"use strict";

const crypto = require("crypto");

/* ---------- base64url + buffer normalisation (a browser sends base64url strings) ---------- */
const b64url = buf => Buffer.from(buf).toString("base64").replace(/=/g, "").replace(/\+/g, "-").replace(/\//g, "_");
const fromB64url = s => {
  const t = String(s || "");
  if (Buffer.isBuffer(s) || s instanceof ArrayBuffer || s instanceof Uint8Array) return Buffer.from(s);
  return Buffer.from(t.replace(/-/g, "+").replace(/_/g, "/"), "base64");
};
function toBuf(v) {
  if (Buffer.isBuffer(v)) return v;
  if (v instanceof ArrayBuffer) return Buffer.from(v);
  if (ArrayBuffer.isView(v)) return Buffer.from(v.buffer, v.byteOffset, v.byteLength);
  return fromB64url(v);
}
function safeEqual(a, b) {
  const x = toBuf(a), y = toBuf(b);
  return x.length === y.length && crypto.timingSafeEqual(x, y);
}

/* ---------- CBOR (definite-length) ----------
    Each item: major type in the top 3 bits, "additional information" in the low 5.
    Returns { value, next } so a caller knows where the next item starts — that is how
    the credential public key's end is found inside authenticator data. Throws on
    anything this platform does not need to consume. */
function decodeCbor(buf, offset) {
  const b = toBuf(buf);
  const i = offset || 0;
  if (i >= b.length) throw new Error("cbor: unexpected end of input");
  const head = b[i];
  const major = head >> 5;
  const ai = head & 0x1f;
  let n = ai, len = 1;
  if (ai < 24) { /* inline */ }
  else if (ai === 24) { n = b[i + 1]; len = 2; }
  else if (ai === 25) { n = b.readUInt16BE(i + 1); len = 3; }
  else if (ai === 26) { n = b.readUInt32BE(i + 1); len = 5; }
  else if (ai === 27) { n = Number(b.readBigUInt64BE(i + 1)); len = 9; }
  else if (ai === 31) throw new Error("cbor: indefinite-length items are not used by WebAuthn");
  else throw new Error("cbor: unsupported additional info " + ai);

  const at = i + len;
  if (major === 0) return { value: n, next: at };                                  /* unsigned int */
  if (major === 1) return { value: -1 - n, next: at };                             /* negative int */
  if (major === 2) {                                                               /* byte string */
    if (at + n > b.length) throw new Error("cbor: byte string overruns the input");
    return { value: b.slice(at, at + n), next: at + n };
  }
  if (major === 3) {                                                               /* text string */
    if (at + n > b.length) throw new Error("cbor: text string overruns the input");
    return { value: b.slice(at, at + n).toString("utf8"), next: at + n };
  }
  if (major === 4) {                                                               /* array */
    const out = [];
    let p = at;
    for (let k = 0; k < n; k++) { const r = decodeCbor(b, p); out.push(r.value); p = r.next; }
    return { value: out, next: p };
  }
  if (major === 5) {                                                               /* map */
    const out = {};
    let p = at;
    for (let k = 0; k < n; k++) {
      const rk = decodeCbor(b, p); p = rk.next;
      const rv = decodeCbor(b, p); p = rv.next;
      out[String(rk.value)] = rv.value;   /* COSE labels are ints; string keys are stable */
    }
    return { value: out, next: p };
  }
  if (major === 6) { return decodeCbor(b, at); }                                   /* tag: the content is the value */
  if (major === 7) {                                                               /* simple / float */
    if (ai === 20) return { value: false, next: at };
    if (ai === 21) return { value: true, next: at };
    if (ai === 22) return { value: null, next: at };
    if (ai === 23) return { value: undefined, next: at };
    if (ai === 25) { /* half-precision — not used by WebAuthn attestation, decoded for completeness */
      const half = b.readUInt16BE(at); const exp = (half >> 10) & 0x1f, frac = half & 0x3ff, sign = half >> 15;
      const val = exp === 0 ? frac * Math.pow(2, -24) : exp === 31 ? (frac ? NaN : sign * Infinity) : (frac + 1024) * Math.pow(2, exp - 25);
      return { value: sign ? -val : val, next: at + 2 };
    }
    if (ai === 26) return { value: b.readFloatBE(at), next: at + 4 };
    if (ai === 27) return { value: b.readDoubleBE(at), next: at + 8 };
    throw new Error("cbor: unsupported simple value " + ai);
  }
  throw new Error("cbor: unsupported major type " + major);
}

/* ---------- authenticator data (the fixed binary struct, not CBOR) ---------- */
const FLAG = { UP: 0x01, UV: 0x04, BE: 0x08, BS: 0x10, AT: 0x40, ED: 0x80 };
function parseAuthenticatorData(buf) {
  const b = toBuf(buf);
  if (b.length < 37) throw new Error("authenticator data is too short");
  const rpIdHash = b.slice(0, 32);
  const flags = b[32];
  const signCount = b.readUInt32BE(33);
  const out = { rpIdHash, flags, signCount, userPresent: !!(flags & FLAG.UP), userVerified: !!(flags & FLAG.UV),
    backupEligible: !!(flags & FLAG.BE), backupState: !!(flags & FLAG.BS), attested: null, extensions: null };
  let p = 37;
  if (flags & FLAG.AT) { /* attested credential data: aaguid · 2-byte length · id · COSE public key */
    if (p + 18 > b.length) throw new Error("attested credential data is truncated");
    const aaguid = b.slice(p, p + 16);
    const idLen = b.readUInt16BE(p + 16);
    p += 18;
    if (p + idLen > b.length) throw new Error("credential id overruns the input");
    const credentialId = b.slice(p, p + idLen);
    p += idLen;
    const key = decodeCbor(b, p);                                                 /* where the key ends = where extensions begin */
    out.attested = { aaguid, credentialId, credentialIdLength: idLen, credentialPublicKey: key.value, credentialPublicKeyBytes: b.slice(p, key.next) };
    p = key.next;
  }
  if (flags & FLAG.ED) {
    try { const ext = decodeCbor(b, p); out.extensions = ext.value; } catch (e) { out.extensions = null; }
  }
  return out;
}

/* ---------- COSE_Key -> node KeyObject ---------- */
const COSE_ALG = { "-7": { kty: "EC2", crv: "P-256", hash: null }, "-35": { kty: "EC2", crv: "P-384", hash: null },
  "-36": { kty: "EC2", crv: "P-521", hash: null }, "-257": { kty: "RSA", crv: null, hash: "RSA-SHA256" },
  "-37": { kty: "RSA", crv: null, hash: "RSA-SHA256", pss: true }, "-8": { kty: "OKP", crv: "Ed25519", hash: null } };
const COSE_CRV_EC2 = { 1: "P-256", 2: "P-384", 3: "P-521" };
const COSE_CRV_OKP = { 6: "Ed25519", 7: "Ed448" };
const b64uBytes = b => b64url(toBuf(b));

/* a COSE public key may arrive as the decoded CBOR map or as raw bytes */
function coseKeyToObject(key) {
  const map = Buffer.isBuffer(key) || typeof key === "string" ? decodeCbor(key).value : key;
  if (!map || typeof map !== "object") throw new Error("COSE key is not a map");
  const kty = Number(map[1]);
  const alg = map[3] != null ? String(map[3]) : null;
  const spec = alg != null && COSE_ALG[alg] ? COSE_ALG[alg] : null;
  const jwk = {};
  if (kty === 2) { /* EC2 */
    jwk.kty = "EC";
    jwk.crv = (spec && spec.crv) || COSE_CRV_EC2[Number(map[-1])];
    if (!jwk.crv) throw new Error("COSE EC key names no curve");
    if (!map[-2] || !map[-3]) throw new Error("COSE EC key is missing a coordinate");
    jwk.x = b64uBytes(map[-2]); jwk.y = b64uBytes(map[-3]);
  } else if (kty === 1) { /* OKP */
    jwk.kty = "OKP";
    jwk.crv = (spec && spec.crv) || COSE_CRV_OKP[Number(map[-1])];
    if (!jwk.crv) throw new Error("COSE OKP key names no curve");
    if (!map[-2]) throw new Error("COSE OKP key is missing its public point");
    jwk.x = b64uBytes(map[-2]);
  } else if (kty === 3) { /* RSA */
    jwk.kty = "RSA";
    if (!map[-1] || !map[-2]) throw new Error("COSE RSA key is missing a modulus or exponent");
    jwk.n = b64uBytes(map[-1]); jwk.e = b64uBytes(map[-2]);
  } else throw new Error("unsupported COSE key type " + kty);
  if (map[-4] != null) throw new Error("a public key must not carry a private component");
  return { jwk, alg: alg != null ? Number(alg) : null, spec };
}

function coseToKeyObject(key) {
  const { jwk, alg, spec } = coseKeyToObject(key);
  const pub = crypto.createPublicKey({ key: jwk, format: "jwk" });
  return { key: pub, jwk, alg, spec };
}

/* ---------- signatures ---------- */
/* WebAuthn ECDSA signatures are raw R||S (IEEE P1363); node's verifier wants DER. */
function derInt(buf) {
  let i = 0;
  while (i < buf.length - 1 && buf[i] === 0) i++;           /* strip leading zeros */
  const v = buf.slice(i);
  const pad = (v[0] & 0x80) ? Buffer.from([0]) : Buffer.alloc(0);   /* keep it positive */
  return Buffer.concat([Buffer.from([0x02]), Buffer.from([pad.length + v.length]), pad, v]);
}
function ecdsaRawToDer(sig, byteLen) {
  const s = toBuf(sig);
  if (s.length !== 2 * byteLen) throw new Error("the ECDSA signature is not " + 2 * byteLen + " bytes (got " + s.length + ")");
  const r = derInt(s.slice(0, byteLen)), t = derInt(s.slice(byteLen));
  const body = Buffer.concat([r, t]);
  return Buffer.concat([Buffer.from([0x30]), Buffer.from([body.length]), body]);
}
function ecByteLen(crv) { return crv === "P-256" ? 32 : crv === "P-384" ? 48 : 66; }

/* verify a signature over `data` per the COSE alg. Returns true/false; never throws on
   a malformed signature — a bad signature is a failed verification, not an exception */
function verifySignature(alg, keyObject, data, sig, crv) {
  try {
    const s = toBuf(sig);
    if (alg === -7 || alg === -35 || alg === -36) {
      return crypto.verify(null, toBuf(data), keyObject, ecdsaRawToDer(s, ecByteLen(crv || "P-256")));
    }
    if (alg === -8) return crypto.verify(null, toBuf(data), keyObject, s);
    if (alg === -257) return crypto.verify("RSA-SHA256", toBuf(data), keyObject, s);
    if (alg === -37) return crypto.verify("RSA-SHA256", toBuf(data), { key: keyObject, padding: crypto.constants.RSA_PKCS1_PSS_PADDING, saltLength: crypto.constants.RSA_PSS_SALTLEN_DIGEST }, s);
    return false;
  } catch (e) { return false; }
}
const algName = a => ({ "-7": "ES256", "-35": "ES384", "-36": "ES512", "-257": "RS256", "-37": "PS256", "-8": "EdDSA" }[String(a)] || ("alg " + a));

/* ---------- the origin check ----------
   The relying party is identified by its origin (scheme://host[:port]). A caller that
   knows the exact origin passes it; otherwise the host must equal the configured rpId. */
function originOk(clientOrigin, expected, rpId) {
  if (typeof clientOrigin !== "string" || !clientOrigin) return false;
  if (expected != null) return clientOrigin === expected;
  if (!rpId) return false;
  let host;
  try { host = new URL(clientOrigin).hostname; } catch (e) { return false; }
  return host === rpId;
}
function challengeOk(clientChallenge, serverChallengeBytes) {
  let got;
  try { got = fromB64url(clientChallenge); } catch (e) { return false; }
  return safeEqual(got, serverChallengeBytes);
}

/* ---------- registration (attestation) ----------
   Returns the credential the platform must bind to the account — never trusts the
   client's word about the key, it decodes the key out of the authenticator data the
   authenticator itself signed (for packed/u2f) or out of the attested credential data
   (fmt "none", where trust is established at assertion time). */
function verifyAttestation(attestationObject, clientDataJSON, serverChallengeBytes, opts) {
  const o = opts || {};
  const att = Buffer.isBuffer(attestationObject) || typeof attestationObject === "string"
    ? decodeCbor(attestationObject).value : attestationObject;
  if (!att || typeof att !== "object") return { ok: false, error: "the attestation is not a CBOR map" };
  const fmt = String(att.fmt || "");
  const authData = toBuf(att.authData);
  const attStmt = att.attStmt && typeof att.attStmt === "object" ? att.attStmt : {};
  if (!fmt || !authData.length) return { ok: false, error: "the attestation is missing its format or authenticator data" };

  const cdRaw = toBuf(clientDataJSON);
  let cd;
  try { cd = JSON.parse(cdRaw.toString("utf8")); } catch (e) { return { ok: false, error: "clientDataJSON is not valid JSON" }; }
  if (cd.type !== "webauthn.create") return { ok: false, error: "clientDataJSON is not a registration response" };
  if (!challengeOk(cd.challenge, serverChallengeBytes)) return { ok: false, error: "the challenge does not match the one the server issued" };
  if (!originOk(cd.origin, o.origin, o.rpId)) return { ok: false, error: "the registration origin is not this relying party" };

  let ad;
  try { ad = parseAuthenticatorData(authData); } catch (e) { return { ok: false, error: "authenticator data would not parse: " + e.message }; }
  if (!ad.userPresent) return { ok: false, error: "the authenticator reports no user present" };
  if (!ad.attested) return { ok: false, error: "the attestation carries no credential (attested credential data absent)" };

  const cose = ad.attested.credentialPublicKey;
  let parsed;
  try { parsed = coseKeyToObject(cose); } catch (e) { return { ok: false, error: "the credential public key would not decode: " + e.message }; }
  const alg = parsed.alg != null ? parsed.alg : (parsed.spec ? Number(Object.keys(COSE_ALG).find(k => COSE_ALG[k].kty === parsed.spec.kty)) : null);
  if (alg == null) return { ok: false, error: "the credential public key names no algorithm" };

  /* attestation is authenticator TRUST metadata — the login security property does not
     depend on it (the assertion proves possession regardless), so formats whose
     certificate chains this zero-dependency build cannot walk are accepted with the
     fact reported, never silently. "none" carries no attestation at all by design. */
  let attestationVerified = false, attestationNote = null;
  const data = Buffer.concat([authData, crypto.createHash("sha256").update(cdRaw).digest()]);
  if (fmt === "none") {
    if (Object.keys(attStmt).length) attestationNote = "fmt 'none' carried an attestation statement, which is ignored";
    attestationVerified = true;
  } else if (fmt === "packed") {
    const sig = attStmt.sig, x5c = attStmt.x5c, a = attStmt.alg != null ? Number(attStmt.alg) : alg;
    try {
      if (Array.isArray(x5c) && x5c.length) {
        const cert = new crypto.X509Certificate(toBuf(x5c[0]));
        if (!verifySignature(a, cert.publicKey, data, sig, parsed.jwk.crv)) return { ok: false, error: "the packed attestation signature would not verify" };
        attestationVerified = true;
      } else if (attStmt.ecdaaKeyId) {
        attestationNote = "ECDAA attestation is not chain-verified in this build";
      } else { /* self-attestation: signed with the credential's own key */
        if (!verifySignature(a, crypto.createPublicKey({ key: parsed.jwk, format: "jwk" }), data, sig, parsed.jwk.crv))
          return { ok: false, error: "the packed self-attestation signature would not verify" };
        attestationVerified = true;
      }
    } catch (e) { return { ok: false, error: "packed attestation could not be verified: " + e.message }; }
  } else if (fmt === "fido-u2f") {
    const sig = attStmt.sig, x5c = attStmt.x5c;
    if (!Array.isArray(x5c) || !x5c.length || !sig) return { ok: false, error: "the U2F attestation is missing its certificate or signature" };
    if (parsed.jwk.kty !== "EC" || parsed.jwk.crv !== "P-256") return { ok: false, error: "a U2F credential must be an EC P-256 key" };
    /* the U2F signed bytes: 0x00 · rpIdHash · clientDataHash · credentialId · 0x04||x||y */
    const pubU2F = Buffer.concat([Buffer.from([0x04]), toBuf(cose[-2]), toBuf(cose[-3])]);
    const signed = Buffer.concat([Buffer.from([0]), ad.rpIdHash, crypto.createHash("sha256").update(cdRaw).digest(),
      ad.attested.credentialId, pubU2F]);
    try {
      const cert = new crypto.X509Certificate(toBuf(x5c[0]));
      if (!crypto.verify(null, signed, cert.publicKey, toBuf(sig))) return { ok: false, error: "the U2F attestation signature would not verify" };
      attestationVerified = true;
    } catch (e) { return { ok: false, error: "U2F attestation could not be verified: " + e.message }; }
  } else {
    attestationNote = "attestation format '" + fmt + "' is recorded, not chain-verified in this build";
  }

  return { ok: true, fmt, alg, algName: algName(alg), aaguid: ad.attested.aaguid,
    credentialId: b64url(ad.attested.credentialId),
    credentialPublicKey: b64url(ad.attested.credentialPublicKeyBytes),   /* COSE bytes — stored, verified later */
    publicKeyJwk: parsed.jwk, signCount: ad.signCount, userVerified: ad.userVerified,
    attestationVerified, attestationNote, transports: Array.isArray(cd.transports) ? cd.transports : null };
}

/* ---------- login (assertion) — the security property ----------
   Proves the caller holds the credential's private key. Every input is untrusted: the
   challenge, origin and flags are checked before the signature, and the signature is
   checked against the key bound at registration — never a key the client supplied. */
function verifyAssertion(assertion, credential, opts) {
  const o = opts || {};
  if (!assertion || typeof assertion !== "object") return { ok: false, error: "no assertion supplied" };
  if (!credential || !credential.credentialPublicKey) return { ok: false, error: "no credential public key is enrolled for this account" };

  const cdRaw = toBuf(assertion.clientDataJSON);
  let cd;
  try { cd = JSON.parse(cdRaw.toString("utf8")); } catch (e) { return { ok: false, error: "clientDataJSON is not valid JSON" }; }
  if (cd.type !== "webauthn.get") return { ok: false, error: "clientDataJSON is not an assertion response" };
  if (!challengeOk(cd.challenge, toBuf(o.challenge))) return { ok: false, error: "the challenge does not match the one the server issued" };
  if (!originOk(cd.origin, o.origin, o.rpId)) return { ok: false, error: "the login origin is not this relying party" };

  const authData = toBuf(assertion.authenticatorData);
  let ad;
  try { ad = parseAuthenticatorData(authData); } catch (e) { return { ok: false, error: "authenticator data would not parse: " + e.message }; }
  if (!ad.userPresent) return { ok: false, error: "the authenticator reports no user present" };
  if (o.requireUserVerified && !ad.userVerified) return { ok: false, error: "the authenticator did not verify the user" };
  if (o.rpId && !safeEqual(ad.rpIdHash, crypto.createHash("sha256").update(String(o.rpId)).digest()))
    return { ok: false, error: "the authenticator data is for a different relying party" };
  if (credential.credentialId && assertion.id != null && !safeEqual(assertion.id, credential.credentialId))
    return { ok: false, error: "the assertion is from a different credential than the one enrolled" };

  let parsed;
  try { parsed = coseKeyToObject(credential.credentialPublicKey); } catch (e) { return { ok: false, error: "the enrolled public key would not decode: " + e.message }; }
  const alg = parsed.alg != null ? parsed.alg : (parsed.spec ? Number(Object.keys(COSE_ALG).find(k => COSE_ALG[k].kty === parsed.spec.kty)) : null);
  if (alg == null) return { ok: false, error: "the enrolled public key names no algorithm" };

  const signed = Buffer.concat([authData, crypto.createHash("sha256").update(cdRaw).digest()]);
  if (!verifySignature(alg, crypto.createPublicKey({ key: parsed.jwk, format: "jwk" }), signed, assertion.signature, parsed.jwk.crv))
    return { ok: false, error: "the assertion signature would not verify" };

  /* clone detection: a counter that does not advance means the credential may have been
     cloned. Reported, and enforced when the platform has a counter to compare against */
  const stored = Number(credential.signCount || 0);
  const replay = stored > 0 && ad.signCount > 0 && ad.signCount <= stored;
  if (replay) return { ok: false, error: "the credential's counter did not advance — possible clone" };

  return { ok: true, alg, algName: algName(alg), signCount: ad.signCount, userVerified: ad.userVerified,
    userPresent: true, credentialId: credential.credentialId, transports: Array.isArray(cd.transports) ? cd.transports : null };
}

module.exports = { decodeCbor, parseAuthenticatorData, coseToKeyObject, coseKeyToObject,
  verifyAttestation, verifyAssertion, verifySignature, b64url, fromB64url, toBuf, safeEqual, FLAG, algName };
