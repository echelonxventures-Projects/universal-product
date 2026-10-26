/* Context continuity · shared primitives.
   --------------------------------------------------------------------------
   Everything the continuity system computes has to be reproducible: the same
   knowledge in gives the same bytes out, so a re-build diffs clean and drift is
   a real signal. These helpers are the only place that decides how JSON is
   serialised, how content is hashed, how paths are resolved and how git is read.

   Zero dependencies (node:crypto / node:fs / node:child_process), like the rest
   of the platform. */
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const cp = require("child_process");

const GENERATOR_VERSION = "ctx-1.0.0";
const CONTEXT_DIR = "PROJECT-CONTEXT";

/* canonical JSON: object keys sorted at every depth, arrays kept in order. Two
   records that mean the same thing serialise to the same bytes. */
function canonical(v) {
  if (Array.isArray(v)) return "[" + v.map(canonical).join(",") + "]";
  if (v && typeof v === "object") {
    return "{" + Object.keys(v).sort().filter(k => v[k] !== undefined)
      .map(k => JSON.stringify(k) + ":" + canonical(v[k])).join(",") + "}";
  }
  return JSON.stringify(v === undefined ? null : v);
}
/* pretty, still deterministic: sorted keys, two-space indent, trailing newline */
function pretty(v) { return JSON.stringify(sortDeep(v), null, 2) + "\n"; }
function sortDeep(v) {
  if (Array.isArray(v)) return v.map(sortDeep);
  if (v && typeof v === "object") {
    const o = {};
    for (const k of Object.keys(v).sort()) if (v[k] !== undefined) o[k] = sortDeep(v[k]);
    return o;
  }
  return v;
}

function sha256(buf) { return crypto.createHash("sha256").update(buf).digest("hex"); }
function hashOf(v) { return sha256(canonical(v)); }
/* git's own blob id, computed without git: sha1("blob <n>\0" + bytes) */
function gitBlobId(buf) {
  return crypto.createHash("sha1").update("blob " + buf.length + "\0").update(buf).digest("hex");
}

function byId(a, b) { return a.id < b.id ? -1 : a.id > b.id ? 1 : 0; }
function uniqSorted(arr) { return [...new Set(arr.filter(Boolean))].sort(); }

/* ---------- paths: every repo path a record names is resolved through here ----------
   A record is imported data, not code. A locator like "../../etc/passwd" or an
   absolute path must never let the system read or write outside the repository. */
function safeJoin(root, rel) {
  if (typeof rel !== "string" || !rel || rel.includes("\0")) throw new Error("invalid path: " + JSON.stringify(rel));
  if (path.isAbsolute(rel)) throw new Error("absolute path refused: " + rel);
  const abs = path.resolve(root, rel);
  const r = path.resolve(root);
  if (abs !== r && !abs.startsWith(r + path.sep)) throw new Error("path escapes the repository: " + rel);
  return abs;
}
function exists(root, rel) { try { return fs.statSync(safeJoin(root, rel)).isFile(); } catch (e) { return false; } }
function readRel(root, rel) { return fs.readFileSync(safeJoin(root, rel)); }
function readJSON(abs) { return JSON.parse(fs.readFileSync(abs, "utf8")); }

/* write only when the bytes differ — the incremental build's "untouched" is literal */
function writeIfChanged(abs, body) {
  let cur = null;
  try { cur = fs.readFileSync(abs, "utf8"); } catch (e) { }
  if (cur === body) return false;
  fs.mkdirSync(path.dirname(abs), { recursive: true });
  fs.writeFileSync(abs, body);
  return true;
}

/* ---------- git (read-only, argv form — never a shell string) ---------- */
function git(root, args, opts) {
  try {
    return cp.execFileSync("git", args, Object.assign({ cwd: root, stdio: ["ignore", "pipe", "ignore"], maxBuffer: 256 << 20 }, opts || {}));
  } catch (e) { return null; }
}
function gitText(root, args) { const b = git(root, args); return b == null ? null : b.toString("utf8").trim(); }
function repoState(root) {
  const head = gitText(root, ["rev-parse", "HEAD"]);
  if (!head) return { git: false, branch: null, head: null, upstream: null, dirty: null, status: [] };
  const status = (gitText(root, ["status", "--porcelain"]) || "").split("\n").filter(Boolean);
  return {
    git: true,
    branch: gitText(root, ["rev-parse", "--abbrev-ref", "HEAD"]),
    head,
    upstream: gitText(root, ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"]),
    dirty: status.length > 0,
    status
  };
}

/* ---------- size estimates ----------
   No tokenizer ships with the repo, and token counts are model-specific. The budget
   is enforced in BYTES; the token figure shown next to it is an estimate at a
   conservative 3 bytes/token (English prose is usually ~4), labelled as such. */
const BYTES_PER_TOKEN_ESTIMATE = 3;
function estimateTokens(bytes) { return Math.ceil(bytes / BYTES_PER_TOKEN_ESTIMATE); }
function byteLen(s) { return Buffer.byteLength(s, "utf8"); }

/* ---------- secrets: never in a derived artifact ----------
   Derived context is broadly readable. A credential that reached a pack through a
   record would be published with it, so generation and verification both scan. */
const SECRET_PATTERNS = [
  { name: "private-key", re: /-----BEGIN [A-Z ]*PRIVATE KEY-----/ },
  { name: "aws-access-key", re: /\bAKIA[0-9A-Z]{16}\b/ },
  { name: "stripe-live-key", re: /\b(sk|rk)_live_[0-9A-Za-z]{8,}/ },
  { name: "github-token", re: /\bgh[pousr]_[0-9A-Za-z]{30,}\b/ },
  { name: "slack-token", re: /\bxox[abpr]-[0-9A-Za-z-]{10,}/ },
  { name: "anthropic-key", re: /\bsk-ant-[0-9A-Za-z_-]{20,}/ },
  { name: "assigned-secret", re: /\b(password|passwd|secret|api[_-]?key|token)\s*[:=]\s*["'][^"'\s]{8,}["']/i }
];
function findSecrets(text) {
  const hits = [];
  for (const p of SECRET_PATTERNS) if (p.re.test(text)) hits.push(p.name);
  return hits;
}

function slug(s, max) {
  return String(s).toLowerCase().normalize("NFKD").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, max || 48).replace(/-+$/, "");
}

module.exports = {
  GENERATOR_VERSION, CONTEXT_DIR, BYTES_PER_TOKEN_ESTIMATE,
  canonical, pretty, sortDeep, sha256, hashOf, gitBlobId, byId, uniqSorted,
  safeJoin, exists, readRel, readJSON, writeIfChanged,
  git, gitText, repoState, estimateTokens, byteLen, findSecrets, slug
};
