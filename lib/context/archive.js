/* Context continuity · Layer A, the source evidence archive.
   --------------------------------------------------------------------------
   Original evidence is preserved by BYTES, independent of any summary:

     git-blob     a file in this repository, pinned by git blob id + sha256. Git's
                  object store is the append-only archive: when the live file is
                  later edited, the pinned version is still restorable by blob id.
     git-history  the commit history behind a pinned commit. Two formats:
                    ctx-git-history/1  the canonical serialization (below) — the
                                       same function captures, verifies, restores
                    (no format)        LEGACY: `rev-list --format` output whose
                                       content depends on the clone's shallow
                                       boundary. Kept only so old records can be
                                       diagnosed; never trusted, never captured.
     store        a content-addressed, write-once store OUTSIDE git
                  (CONTEXT_ARCHIVE_DIR, default .context-archive/, gitignored):
                  where private exports and attachments go. Never committed.
     external     known to exist elsewhere, not held here (no bytes to verify).
     none         known to have existed, not available at all.

   A checksum proves the captured bytes are intact. It does NOT prove every
   conversation or attachment was captured — completeness is reported separately
   (coverage.js), and missing sources are recorded as missing, never implied. */
"use strict";

const fs = require("fs");
const os = require("os");
const path = require("path");
const U = require("./util");
const { diag, saveKind } = require("./store");

function storeDir(K, override) {
  const env = K.config.archive && K.config.archive.storeEnv;
  const dir = override || (env && process.env[env]) || path.join(K.root, (K.config.archive && K.config.archive.defaultStore) || ".context-archive");
  return path.resolve(dir);
}
function storePath(dir, sha) {
  if (!/^[0-9a-f]{64}$/.test(sha)) throw new Error("invalid sha256");
  return path.join(dir, "objects", sha.slice(0, 2), sha);
}

/* the archived bytes of a source, from the archive (not the live file) when possible */
/* ---------- the canonical git-history serialization: ctx-git-history/1 ----------
   Selection  every commit reachable from the pinned commit (its full ancestry,
              merge parents included), read with replace objects disabled so a
              `git replace`/graft cannot alter the history being archived.
   Fail closed  a shallow repository, a missing pinned commit, or any reachable
              commit whose parent is absent (missing objects / truncated graph)
              is an error — never a partial archive.
   Order      topological, parents before children; ties broken by ascending
              commit hash (computed here, independent of git's own ordering).
   Bytes      UTF-8, LF line endings, one trailing LF, no other whitespace:
                "# ctx-git-history/1 pinned=<40-hex> commits=<n>\n"
                then per commit "<hash>\t<parents space-separated or ->\t<author unix time>\t<subject>\n"
              where subject is %s with "\\" → "\\\\", TAB → "\\t", CR → "\\r".
   sha256/bytes/commits in a record are derived from exactly these bytes. */
const GIT_HISTORY_FORMAT = "ctx-git-history/1";
function gitNoReplace(root, args) { return U.git(root, args, { env: Object.assign({}, process.env, { GIT_NO_REPLACE_OBJECTS: "1" }) }); }
function serializeGitHistory(root, commit) {
  const fail = (code, detail) => ({ error: code, detail });
  if (!/^[0-9a-f]{40}$/.test(String(commit || ""))) return fail("malformed-metadata", "pinned commit must be a full 40-hex commit id, got " + JSON.stringify(commit));
  if (U.gitText(root, ["rev-parse", "--is-shallow-repository"]) === "true") return fail("shallow-repository", "this clone is shallow: the ancestry of " + commit.slice(0, 12) + " is truncated, so no complete history can be serialized — run `git fetch --unshallow` (CI: actions/checkout with fetch-depth: 0)");
  if (gitNoReplace(root, ["cat-file", "-e", commit + "^{commit}"]) == null) return fail("missing-pinned-commit", "pinned commit " + commit.slice(0, 12) + " is not in this repository's object store — fetch it, or the archive cannot be reproduced here");
  const graph = gitNoReplace(root, ["rev-list", "--parents", commit]);
  const meta = gitNoReplace(root, ["log", "--format=%H%x09%at%x09%s", "--encoding=UTF-8", "--no-show-signature", commit]);
  if (graph == null || meta == null) return fail("incomplete-history", "git could not walk the ancestry of " + commit.slice(0, 12) + " (missing or corrupt objects) — fetch the full history and re-verify");
  const parents = new Map();
  for (const line of graph.toString("utf8").split("\n").filter(Boolean)) { const [h, ...ps] = line.split(" "); parents.set(h, ps); }
  for (const [h, ps] of parents) for (const p of ps) if (!parents.has(p)) return fail("incomplete-history", "commit " + h.slice(0, 12) + " names parent " + p.slice(0, 12) + " which is not reachable here — the history is incomplete");
  const fields = new Map();
  for (const line of meta.toString("utf8").split("\n")) { if (!line) continue; const i = line.indexOf("\t"), j = line.indexOf("\t", i + 1); fields.set(line.slice(0, i), { at: line.slice(i + 1, j), subject: line.slice(j + 1) }); }
  if (fields.size !== parents.size) return fail("incomplete-history", "commit metadata count " + fields.size + " differs from the graph's " + parents.size);
  /* Kahn's algorithm: parents first, ready set kept sorted by hash */
  const children = new Map(), indeg = new Map();
  for (const [h, ps] of parents) { indeg.set(h, ps.length); for (const p of ps) { if (!children.has(p)) children.set(p, []); children.get(p).push(h); } }
  const ready = [...indeg].filter(([, d]) => d === 0).map(([h]) => h).sort();
  const order = [];
  while (ready.length) {
    const h = ready.shift(); order.push(h);
    for (const c of (children.get(h) || []).sort()) { indeg.set(c, indeg.get(c) - 1); if (indeg.get(c) === 0) { let k = 0; while (k < ready.length && ready[k] < c) k++; ready.splice(k, 0, c); } }
  }
  if (order.length !== parents.size) return fail("incomplete-history", "the commit graph is not acyclic over its parents");
  const esc = t => t.replace(/\\/g, "\\\\").replace(/\t/g, "\\t").replace(/\r/g, "\\r");
  let out = "# " + GIT_HISTORY_FORMAT + " pinned=" + commit + " commits=" + order.length + "\n";
  for (const h of order) { const f = fields.get(h), ps = parents.get(h); out += h + "\t" + (ps.length ? ps.slice().sort().join(" ") : "-") + "\t" + f.at + "\t" + esc(f.subject) + "\n"; }
  return { buf: Buffer.from(out, "utf8"), commits: order.length };
}
/* the legacy (pre-format) serializer, reproduced only to DIAGNOSE old records */
function legacyGitHistory(root, commit) {
  const out = U.gitText(root, ["rev-list", "--reverse", "--format=%H %ad %s", "--date=short", commit]);
  if (out == null) return null;
  const lines = out.split("\n").filter(l => !l.startsWith("commit "));
  return Buffer.from(lines.join("\n") + "\n");
}
function gitHistoryBytes(root, s) {
  if (s.format === GIT_HISTORY_FORMAT) { const r = serializeGitHistory(root, s.commit); return r.error ? r : { buf: r.buf, commits: r.commits, via: GIT_HISTORY_FORMAT }; }
  return { error: "legacy-format", detail: "this record has no storage.format: its bytes came from the legacy rev-list serializer, whose output depends on the clone's shallow boundary and cannot be reproduced reliably" };
}

function bytesOf(K, n, opts) {
  const s = n.rec.storage;
  if (s.kind === "git-blob") {
    if (s.blob) { const b = U.git(K.root, ["cat-file", "blob", s.blob]); if (b) return { buf: b, via: "git-object" }; }
    if (n.rec.locator) {
      try { const live = U.readRel(K.root, n.rec.locator); if (U.sha256(live) === s.sha256) return { buf: live, via: "live-file" }; } catch (e) { }
    }
    return null;
  }
  if (s.kind === "git-history") {
    const r = gitHistoryBytes(K.root, s);
    return r.error ? null : { buf: r.buf, via: r.via };
  }
  if (s.kind === "store") {
    if (opts && opts.offlineStore) return null;
    try { return { buf: fs.readFileSync(storePath(storeDir(K, opts && opts.store), s.sha256)), via: "store" }; } catch (e) { return null; }
  }
  return null;
}

const shallowCache = new Map();
function isShallow(K) {
  if (!shallowCache.has(K.root)) shallowCache.set(K.root, U.gitText(K.root, ["rev-parse", "--is-shallow-repository"]) === "true");
  return shallowCache.get(K.root);
}

/* verify one source; returns { id, ok, status, detail, level } */
function verifyOne(K, n, opts) {
  const r = n.rec, s = r.storage;
  const res = (level, status, detail, extra) => Object.assign({ id: n.id, level, ok: level !== "error", status, detail }, extra || {});
  /* a record that no longer claims its bytes are preserved may still carry the checksum
     it was captured with (its historical identity). It is never "verified"; if another
     source recovers it, that copy must hash to the recorded value. */
  if (r.preservation !== "preserved") {
    const copies = K.of("source").filter(x => (x.rec.recovers || []).includes(n.id));
    const legacy = s.kind === "git-history" && !s.format && s.commit ? legacyGitHistory(K.root, s.commit) : null;
    const legacyCheck = s.kind === "git-history" && !s.format ? (legacy ? (U.sha256(legacy) === s.sha256 ? "match" : "mismatch") : "unavailable") : undefined;
    const legacyNote = legacyCheck ? " Its legacy procedure here yields " + (legacy ? legacy.toString("utf8").split("\n").filter(Boolean).length + " lines / " + legacy.length + " B / sha256 " + U.sha256(legacy).slice(0, 16) + "… (" + legacyCheck + " vs recorded " + String(s.sha256).slice(0, 16) + "…, " + s.bytes + " B)" : "no output") + "." : "";
    if (copies.length && s.sha256) {
      for (const c of copies) {
        if (c.rec.storage.sha256 !== s.sha256) return res("error", "recovery-mismatch", c.id + " claims to recover this source but its sha256 differs from the recorded one", { legacyCheck });
        const cv = verifyOne(K, c, opts);
        if (cv.status === "verified" || cv.status === "live-diverged" || cv.status === "live-missing") return res("warn", "recovered-copy", "not preserved by its own storage (" + r.preservation + "); the recorded bytes were recovered as " + c.id + ", which verifies and hashes to the recorded sha256. This record itself stays unverified." + legacyNote, { legacyCheck, recoveredBy: c.id });
      }
      return res("warn", "recovered-copy-unverified", "a recovered copy exists (" + copies.map(c => c.id).join(", ") + ") but it does not verify here." + legacyNote, { legacyCheck });
    }
    if (s.kind !== "none" && s.kind !== "external" && s.sha256) return res("warn", "not-preserved-but-bytes-recorded", "preservation is '" + r.preservation + "': the recorded checksum is historical identity only, not verified bytes." + legacyNote, { legacyCheck });
    return res("info", r.preservation, (r.omissions || []).join("; ") || "recorded as " + r.preservation);
  }
  if (s.kind === "none" || s.kind === "external") return res("error", "unverifiable", "marked preserved but storage kind '" + s.kind + "' holds no verifiable bytes");
  if (!s.sha256) return res("error", "malformed-metadata", "preserved source has no sha256");
  if (s.kind === "git-history") {
    if (!s.commit) return res("error", "malformed-metadata", "git-history record has no pinned commit");
    if (!s.format) {
      const legacy = legacyGitHistory(K.root, s.commit);
      return res("error", "legacy-unverifiable", "claims preserved with the legacy git-history serialization, which depends on the clone's shallow boundary and is not a verifiable archive" + (legacy && U.sha256(legacy) !== s.sha256 ? " (here it yields sha256 " + U.sha256(legacy).slice(0, 16) + "…, not the recorded " + s.sha256.slice(0, 16) + "…)" : "") + " — mark it not-retained and capture a canonical one with `npm run context:capture-history -- " + s.commit.slice(0, 12) + "`", { legacyCheck: legacy ? (U.sha256(legacy) === s.sha256 ? "match" : "mismatch") : "unavailable" });
    }
    if (s.format !== GIT_HISTORY_FORMAT) return res("error", "unsupported-format", "unknown git-history format '" + s.format + "'");
    const g = gitHistoryBytes(K.root, s);
    if (g.error) return res("error", g.error, g.detail);
    const sha = U.sha256(g.buf);
    /* precedence: different content first; then metadata that disagrees with matching content */
    if (sha !== s.sha256) return res("error", "checksum-mismatch", "canonical serialization (" + g.commits + " commits, " + g.buf.length + " B) hashes to " + sha.slice(0, 16) + "…, manifest says " + s.sha256.slice(0, 16) + "… (" + s.commits + " commits, " + s.bytes + " B) — the history behind " + s.commit.slice(0, 12) + " differs from what was captured");
    if (s.bytes != null && g.buf.length !== s.bytes) return res("error", "byte-count-mismatch", "content matches the recorded sha256 but is " + g.buf.length + " B, manifest says " + s.bytes + " B — the record's metadata is wrong");
    if (s.commits != null && g.commits !== s.commits) return res("error", "commit-count-mismatch", "content matches the recorded sha256 but holds " + g.commits + " commits, manifest says " + s.commits + " — the record's metadata is wrong");
    return res("ok", "verified", "via " + GIT_HISTORY_FORMAT + " (" + g.commits + " commits)");
  }
  const got = bytesOf(K, n, opts);
  if (!got && s.kind === "store") return res("warn", "store-unavailable", "archive store not reachable here (" + storeDir(K, opts && opts.store) + "); expected on machines without access");
  if (!got && isShallow(K)) return res("warn", "shallow-clone", "this checkout is shallow; " + s.kind + " evidence is verifiable only in a full clone (git fetch --unshallow)");
  if (!got) {
    return res("error", "unrestorable", "archived bytes cannot be retrieved (blob " + (s.blob || "none") + " not in the object store and the live file differs)");
  }
  const sha = U.sha256(got.buf);
  if (sha !== s.sha256) return res("error", "checksum-mismatch", "archived bytes via " + got.via + " (" + got.buf.length + " B) hash to " + sha.slice(0, 16) + "…, manifest says " + s.sha256.slice(0, 16) + "… (" + s.bytes + " B)");
  if (s.bytes != null && got.buf.length !== s.bytes) return res("error", "byte-count-mismatch", "archived bytes match the recorded sha256 but are " + got.buf.length + " B, manifest says " + s.bytes + " B — the record's metadata is wrong");
  if (s.kind === "git-blob" && s.blob && U.gitBlobId(got.buf) !== s.blob) return res("error", "blob-mismatch", "content does not match the recorded git blob id");
  if (s.kind === "git-blob" && r.locator && !(r.supersededBy || []).length) {
    let live = null;
    try { live = U.readRel(K.root, r.locator); } catch (e) { }
    if (!live) return res("warn", "live-missing", "archived version verified via " + got.via + "; the live file " + r.locator + " no longer exists");
    if (U.sha256(live) !== s.sha256) return res("warn", "live-diverged", "archived version verified via " + got.via + "; the live file has changed since capture — run `npm run context:capture -- " + r.locator + "` to archive the new version as a new source");
  }
  return res("ok", "verified", "via " + got.via);
}

/* opts.offlineStore: treat the private store as unreachable, so a report that is
   committed (the quality view) does not depend on which machine generated it */
function verifyAll(K, opts) {
  const results = K.of("source").map(n => verifyOne(K, n, opts));
  /* the same bytes captured under two ids is suspicious, not fatal */
  const bySha = new Map();
  for (const n of K.of("source")) { const h = n.rec.storage.sha256; if (!h) continue; if (!bySha.has(h)) bySha.set(h, []); bySha.get(h).push(n.id); }
  /* a declared recovery (X recovers Y) shares Y's checksum on purpose; any other shared bytes are reported */
  const recovers = new Set();
  for (const n of K.of("source")) for (const r of n.rec.recovers || []) recovers.add(r + "|" + n.id);
  const dupes = [...bySha.values()].filter(v => v.length > 1 && !(v.length === 2 && (recovers.has(v[0] + "|" + v[1]) || recovers.has(v[1] + "|" + v[0]))));
  return { results, duplicateBytes: dupes };
}

/* ---------- segments: stable boundaries over the ARCHIVED bytes ----------
   Ids are ordinal (S0001…) over an immutable byte sequence: the source record pins
   the bytes, so the ids never move. A new version of the file is a new source. */
function segments(n, buf) {
  const seg = n.rec.segmentation;
  if (!buf || seg.rule === "none") return [];
  const text = buf.toString("utf8");
  const lines = text.split("\n");
  if (lines.length && lines[lines.length - 1] === "") lines.pop();
  const pad = i => "S" + String(i).padStart(4, "0");
  if (seg.rule === "whole") return [{ id: pad(1), title: n.rec.title, start: 1, end: lines.length }];
  if (seg.rule === "commits") return lines.map((l, i) => ({ l, i })).filter(x => !x.l.startsWith("# ")).map((x, k) => ({ id: pad(k + 1), title: x.l.slice(0, 80), start: x.i + 1, end: x.i + 1 }));
  if (seg.rule === "lines") {
    const size = seg.lines || 500, out = [];
    for (let i = 0; i < lines.length; i += size) out.push({ id: pad(out.length + 1), title: "lines " + (i + 1) + "–" + Math.min(lines.length, i + size), start: i + 1, end: Math.min(lines.length, i + size) });
    return out;
  }
  /* headings: a segment starts at each heading of level <= maxLevel (outside code fences) */
  const max = seg.maxLevel || 2, re = new RegExp("^#{1," + max + "}\\s+(.*)$");
  const out = [];
  let fence = false, cur = null;
  lines.forEach((l, i) => {
    if (/^\s*```/.test(l)) fence = !fence;
    const m = !fence && re.exec(l);
    if (m || i === 0) {
      if (cur) { cur.end = i; out.push(cur); }
      cur = { title: m ? m[1].trim().slice(0, 100) : "(preamble)", start: i + 1 };
    }
  });
  if (cur) { cur.end = lines.length; out.push(cur); }
  return out.filter(s => s.end >= s.start).map((s, i) => Object.assign({ id: pad(i + 1) }, s));
}

/* ---------- import: copy a file into the write-once store and register it ---------- */
function importFile(K, file, opts) {
  opts = opts || {};
  if (!opts.id || !/^SRC-[A-Z0-9-]+$/.test(opts.id)) throw new Error("--id must look like SRC-EXAMPLE-001");
  if (K.nodes.has(opts.id)) throw new Error("source id " + opts.id + " already exists — ids are never reused; choose a new id (a new version is a new source)");
  const abs = path.resolve(file);
  const st = fs.lstatSync(abs);
  if (!st.isFile()) throw new Error("not a regular file (symlinks are refused): " + file);
  const buf = fs.readFileSync(abs);
  const sha = U.sha256(buf);
  const dir = storeDir(K, opts.store);
  const dest = storePath(dir, sha);
  if (fs.existsSync(dest)) {
    if (U.sha256(fs.readFileSync(dest)) !== sha) throw new Error("store object " + sha + " exists with different content — the store is corrupt; refusing to overwrite");
  } else {
    fs.mkdirSync(path.dirname(dest), { recursive: true, mode: 0o700 });
    fs.writeFileSync(dest, buf, { mode: 0o400, flag: "wx" });
  }
  const now = opts.now || new Date().toISOString();
  const rec = {
    id: opts.id,
    title: opts.title || (opts.redactName ? "imported source " + opts.id : path.basename(abs)),
    category: opts.category || "conversation-export",
    origin: opts.origin || "imported by context:import",
    locator: "store:" + sha,
    storage: { kind: "store", sha256: sha, bytes: buf.length },
    createdAt: opts.createdAt || null,
    capturedAt: opts.capturedAt || null,
    importedAt: now,
    segmentation: { rule: opts.segmentation || "headings", maxLevel: 2 },
    sensitivity: opts.sensitivity || "private",
    preservation: "preserved",
    omissions: [],
    lifecycle: "historical-evidence",
    owner: "PROJECT-CONTEXT/knowledge/sources.json"
  };
  if (opts.attachmentOf) rec.attachmentOf = [opts.attachmentOf];
  if (!opts.dryRun) saveKind(K.root, "source", recs => recs.push(rec));
  return { record: rec, stored: dest };
}

/* capture a repository file (a new version → a new source id, superseding the old) */
function captureRepoFile(K, rel, opts) {
  opts = opts || {};
  const buf = U.readRel(K.root, rel);
  const sha = U.sha256(buf);
  const prev = K.of("source").filter(n => n.rec.locator === rel && n.rec.storage.kind === "git-blob");
  if (prev.some(n => n.rec.storage.sha256 === sha)) return { unchanged: true, id: prev.find(n => n.rec.storage.sha256 === sha).id };
  const base = opts.id || ("SRC-" + U.slug(path.basename(rel), 30).toUpperCase());
  let id = base, v = 2;
  while (K.nodes.has(id)) id = base.replace(/-V\d+$/, "") + "-V" + v++;
  const latest = prev[prev.length - 1];
  const rec = {
    id, title: (latest && latest.rec.title.replace(/ \(v\d+\)$/, "") || rel) + (latest ? " (v" + (v - 1) + ")" : ""),
    category: (latest && latest.rec.category) || opts.category || "project-doc",
    origin: "repository file " + rel, locator: rel,
    storage: { kind: "git-blob", blob: U.gitBlobId(buf), sha256: sha, bytes: buf.length },
    createdAt: null, capturedAt: opts.now || new Date().toISOString(), importedAt: null,
    segmentation: (latest && latest.rec.segmentation) || { rule: "headings", maxLevel: 2 },
    sensitivity: (latest && latest.rec.sensitivity) || "public", preservation: "preserved", omissions: [],
    lifecycle: (latest && latest.rec.lifecycle) || "historical-evidence", owner: "PROJECT-CONTEXT/knowledge/sources.json"
  };
  if (!opts.dryRun) saveKind(K.root, "source", recs => {
    recs.push(rec);
    if (latest) {
      const old = recs.find(x => x.id === latest.id);
      old.supersededBy = U.uniqSorted((old.supersededBy || []).concat(id));
    }
  });
  return { record: rec, supersedes: latest ? latest.id : null, note: "commit the file so the blob is in git's object store; until then the archive is the working tree only" };
}

/* ---------- capture a git history with the canonical serializer (fail closed) ---------- */
function captureGitHistory(K, commit, opts) {
  opts = opts || {};
  const full = U.gitText(K.root, ["rev-parse", "--verify", String(commit) + "^{commit}"]);
  if (!full) throw new Error("commit " + commit + " is not in this repository");
  const id = opts.id || ("SRC-GIT-HISTORY-" + full.slice(0, 7).toUpperCase() + "-V1");
  if (!/^SRC-[A-Z0-9-]+$/.test(id)) throw new Error("--id must look like SRC-EXAMPLE-001");
  if (K.nodes.has(id)) throw new Error("source id " + id + " already exists — ids are never reused and a recorded checksum is never recalculated; capture under a new id");
  const r = serializeGitHistory(K.root, full);
  if (r.error) throw new Error("refusing to capture: " + r.error + " — " + r.detail);
  const rec = {
    id, title: "Git history behind " + full.slice(0, 7) + " (" + r.commits + " commits, " + GIT_HISTORY_FORMAT + ")",
    category: "vcs-history", origin: "canonical serialization of the full ancestry of " + full, locator: "git:" + full,
    storage: { kind: "git-history", format: GIT_HISTORY_FORMAT, commit: full, sha256: U.sha256(r.buf), bytes: r.buf.length, commits: r.commits },
    createdAt: null, capturedAt: opts.now || new Date().toISOString(), importedAt: null,
    segmentation: { rule: "commits" }, capturedBy: ["ART-GIT-OBJECT-STORE"], sensitivity: "public", preservation: "preserved",
    omissions: ["Commit ids, parents, author times and subjects only; diffs live in git itself. Verifiable only in a full (non-shallow) clone."],
    lifecycle: "historical-evidence", owner: "PROJECT-CONTEXT/knowledge/sources.json"
  };
  if (!opts.dryRun) saveKind(K.root, "source", recs => recs.push(rec));
  return { record: rec, bytes: r.buf };
}

/* ---------- append-only source identity ----------
   A source's identity (storage kind, format, pinned commit/blob, sha256, bytes,
   commits) is fixed when it is first committed. Any later change — committed or in
   the working tree — is reported, so a checksum can never be quietly recalculated
   to "bless" bytes that do not match. A changed file is a NEW source. */
const IDENTITY_FIELDS = ["kind", "format", "commit", "blob", "sha256", "bytes", "commits"];
function identityOf(rec) { const o = {}; for (const f of IDENTITY_FIELDS) if (rec.storage && rec.storage[f] !== undefined) o[f] = rec.storage[f]; return o; }
function identityAudit(K) {
  const rel = U.CONTEXT_DIR + "/knowledge/sources.json";
  const log = U.gitText(K.root, ["log", "--reverse", "--format=%H", "--", rel]);
  const first = new Map(), problems = [];
  for (const c of (log || "").split("\n").filter(Boolean)) {
    const body = U.git(K.root, ["show", c + ":" + rel]);
    if (!body) continue;
    let doc; try { doc = JSON.parse(body.toString("utf8")); } catch (e) { continue; }
    for (const r of doc.records || []) {
      if (!first.has(r.id)) { first.set(r.id, { commit: c, identity: identityOf(r) }); continue; }
      const f = first.get(r.id);
      if (U.canonical(identityOf(r)) !== U.canonical(f.identity)) problems.push({ id: r.id, where: "commit " + c.slice(0, 12), since: f.commit.slice(0, 12) });
    }
  }
  for (const n of K.of("source")) {
    const f = first.get(n.id);
    if (f && U.canonical(identityOf(n.rec)) !== U.canonical(f.identity)) problems.push({ id: n.id, where: "working tree", since: f.commit.slice(0, 12), was: f.identity, now: identityOf(n.rec) });
  }
  const seen = new Set();
  return problems.filter(p => { const k = p.id + "|" + p.where; if (seen.has(k)) return false; seen.add(k); return true; });
}

/* ---------- restore-check: restore every preserved source into an ISOLATED dir ---------- */
function restoreCheck(K, opts) {
  opts = opts || {};
  const dest = path.resolve(opts.dest || fs.mkdtempSync(path.join(os.tmpdir(), "ctx-restore-")));
  const root = path.resolve(K.root);
  if (dest === root || dest.startsWith(root + path.sep)) throw new Error("restore destination must be outside the repository: " + dest);
  fs.mkdirSync(dest, { recursive: true });
  if (fs.readdirSync(dest).length && !opts.allowNonEmpty) throw new Error("restore destination is not empty: " + dest);
  const statusBefore = U.gitText(K.root, ["status", "--porcelain", "--untracked-files=all"]);
  const results = [];
  for (const n of K.of("source")) {
    if (n.rec.preservation !== "preserved") { results.push({ id: n.id, status: "skipped", detail: "preservation " + n.rec.preservation }); continue; }
    const got = bytesOf(K, n, opts);
    if (!got) { results.push({ id: n.id, status: n.rec.storage.kind === "store" ? "unavailable" : "failed", detail: "bytes not retrievable" }); continue; }
    const name = n.id + "__" + (n.rec.locator && !n.rec.locator.startsWith("store:") ? path.basename(n.rec.locator) : "content");
    const out = path.join(dest, name);
    fs.writeFileSync(out, got.buf, { flag: "wx" });
    const sha = U.sha256(fs.readFileSync(out));
    results.push({ id: n.id, status: sha === n.rec.storage.sha256 ? "restored" : "mismatch", via: got.via, bytes: got.buf.length });
  }
  const failed = results.filter(r => r.status === "failed" || r.status === "mismatch");
  const touched = U.gitText(K.root, ["status", "--porcelain", "--untracked-files=all"]) !== statusBefore;
  if (touched) failed.push({ id: "live-repository", status: "failed", detail: "git status changed during restore" });
  if (!opts.keep) fs.rmSync(dest, { recursive: true, force: true });
  return {
    schema: "ctx-restore-check/1",
    ok: failed.length === 0,
    restored: results.filter(r => r.status === "restored").length,
    unavailable: results.filter(r => r.status === "unavailable").length,
    skipped: results.filter(r => r.status === "skipped").length,
    failed: failed.length,
    liveRepositoryTouched: touched,
    results
  };
}

module.exports = { verifyAll, verifyOne, bytesOf, segments, importFile, captureRepoFile, captureGitHistory, serializeGitHistory, legacyGitHistory, identityAudit, restoreCheck, storeDir, diag, GIT_HISTORY_FORMAT };
