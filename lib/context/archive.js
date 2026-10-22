/* Context continuity · Layer A, the source evidence archive.
   --------------------------------------------------------------------------
   Original evidence is preserved by BYTES, independent of any summary:

     git-blob     a file in this repository, pinned by git blob id + sha256. Git's
                  object store is the append-only archive: when the live file is
                  later edited, the pinned version is still restorable by blob id.
     git-history  the commit list up to a pinned commit (reproducible, hashed).
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
    const out = U.gitText(K.root, ["rev-list", "--reverse", "--format=%H %ad %s", "--date=short", s.commit]);
    if (out == null) return null;
    const lines = out.split("\n").filter(l => !l.startsWith("commit "));
    return { buf: Buffer.from(lines.join("\n") + "\n"), via: "git-rev-list" };
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
  const res = (level, status, detail) => ({ id: n.id, level, ok: level !== "error", status, detail });
  if (r.preservation !== "preserved") {
    if (s.kind !== "none" && s.kind !== "external" && s.sha256) return res("warn", "not-preserved-but-bytes-recorded", "preservation is '" + r.preservation + "' but storage records bytes");
    return res("info", r.preservation, (r.omissions || []).join("; ") || "recorded as " + r.preservation);
  }
  if (s.kind === "none" || s.kind === "external") return res("error", "unverifiable", "marked preserved but storage kind '" + s.kind + "' holds no verifiable bytes");
  if (!s.sha256) return res("error", "no-checksum", "preserved source has no sha256");
  const got = bytesOf(K, n, opts);
  if (!got && s.kind === "store") return res("warn", "store-unavailable", "archive store not reachable here (" + storeDir(K, opts && opts.store) + "); expected on machines without access");
  if (!got && isShallow(K)) return res("warn", "shallow-clone", "this checkout is shallow; " + s.kind + " evidence is verifiable only in a full clone (git fetch --unshallow)");
  if (got && s.kind === "git-history" && U.sha256(got.buf) !== s.sha256 && isShallow(K)) return res("warn", "shallow-clone", "history truncated by a shallow clone; verify in a full clone (git fetch --unshallow)");
  if (!got) {
    return res("error", "unrestorable", "archived bytes cannot be retrieved (blob " + (s.blob || "none") + " not in the object store and the live file differs)");
  }
  const sha = U.sha256(got.buf);
  if (sha !== s.sha256 || (s.bytes != null && got.buf.length !== s.bytes)) return res("error", "checksum-mismatch", "archived bytes via " + got.via + " hash to " + sha.slice(0, 16) + "…, manifest says " + s.sha256.slice(0, 16) + "…");
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
  const dupes = [...bySha.values()].filter(v => v.length > 1);
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
  if (seg.rule === "commits") return lines.map((l, i) => ({ id: pad(i + 1), title: l.slice(0, 80), start: i + 1, end: i + 1 }));
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

/* ---------- restore-check: restore every preserved source into an ISOLATED dir ---------- */
function restoreCheck(K, opts) {
  opts = opts || {};
  const dest = path.resolve(opts.dest || fs.mkdtempSync(path.join(os.tmpdir(), "ctx-restore-")));
  const root = path.resolve(K.root);
  if (dest === root || dest.startsWith(root + path.sep)) throw new Error("restore destination must be outside the repository: " + dest);
  fs.mkdirSync(dest, { recursive: true });
  if (fs.readdirSync(dest).length && !opts.allowNonEmpty) throw new Error("restore destination is not empty: " + dest);
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
  if (!opts.keep) fs.rmSync(dest, { recursive: true, force: true });
  return {
    schema: "ctx-restore-check/1",
    ok: failed.length === 0,
    restored: results.filter(r => r.status === "restored").length,
    unavailable: results.filter(r => r.status === "unavailable").length,
    skipped: results.filter(r => r.status === "skipped").length,
    failed: failed.length,
    liveRepositoryTouched: false,
    results
  };
}

module.exports = { verifyAll, verifyOne, bytesOf, segments, importFile, captureRepoFile, restoreCheck, storeDir, diag };
