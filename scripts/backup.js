#!/usr/bin/env node
/* LUXORA Platform — consistent online backup of the database, with the keys that unlock it.

   node scripts/backup.js [--dir <path>] [--keep <n>] [--upload]

   - The database is copied with SQLite's VACUUM INTO: a transactionally consistent snapshot
     taken while the server keeps running (no stop, no torn copy of a WAL-mode file).
   - The keyring (data/master.json) and registry seal key (data/registry.json) are copied
     with it. Without the keyring a restored database cannot decrypt a single stored gateway
     credential, so a backup that omits it is not a backup. Treat the backup directory as
     secret (it is created 0700, files 0600).
   - Each backup is verified (PRAGMA integrity_check on the copy) and gets a manifest with
     SHA-256 checksums that scripts/restore.js checks before restoring.
   - Old backups beyond --keep (default 14, or LX_BACKUP_KEEP) are pruned.
   - --upload (or LX_BACKUP_S3_BUCKET set) also copies the set to S3-compatible storage:
     LX_BACKUP_S3_BUCKET, LX_BACKUP_S3_REGION, LX_BACKUP_S3_ACCESS, LX_BACKUP_S3_SECRET,
     LX_BACKUP_S3_ENDPOINT (optional, for R2/MinIO/B2). An upload failure exits non-zero.

   Defaults: LX_DB (else data/luxora.db) → LX_BACKUP_DIR (else data/backups). Exit 0 on
   success; any failure exits 1 so a timer/cron surfaces it. */
"use strict";
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const { DatabaseSync } = require("node:sqlite");

const ROOT = path.join(__dirname, "..");
const DATA = path.join(ROOT, "data");
const arg = (name, dflt) => { const i = process.argv.indexOf("--" + name); return i > 0 && process.argv[i + 1] && !process.argv[i + 1].startsWith("--") ? process.argv[i + 1] : dflt; };
const flag = name => process.argv.includes("--" + name);

const DB = path.resolve(process.env.LX_DB || path.join(DATA, "luxora.db"));
const DIR = path.resolve(arg("dir", process.env.LX_BACKUP_DIR || path.join(DATA, "backups")));
const KEEP = Math.max(1, Number(arg("keep", process.env.LX_BACKUP_KEEP || 14)) || 14);
const KEY_FILES = ["master.json", "registry.json"];
const sha256 = file => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
const stamp = () => new Date().toISOString().replace(/[-:]/g, "").replace(/\..+/, "").replace("T", "-");

async function main() {
  if (!fs.existsSync(DB)) throw new Error("no database at " + DB + " (set LX_DB)");
  fs.mkdirSync(DIR, { recursive: true, mode: 0o700 });
  const name = "luxora-" + stamp();
  const dest = path.join(DIR, name);
  fs.mkdirSync(dest, { mode: 0o700 });
  const out = path.join(dest, "luxora.db");

  /* VACUUM INTO writes a fresh, compacted, consistent copy; it works on a database another
     process has open and writing (it reads one snapshot) */
  const src = new DatabaseSync(DB, { readOnly: true });
  try { src.exec("PRAGMA busy_timeout = 10000"); src.prepare("VACUUM INTO ?").run(out); }
  finally { src.close(); }
  fs.chmodSync(out, 0o600);

  const copy = new DatabaseSync(out, { readOnly: true });
  let check, counts;
  try {
    check = copy.prepare("PRAGMA integrity_check").all().map(r => Object.values(r)[0]).join("; ");
    counts = {};
    for (const t of ["tenants", "users", "orders", "payments", "products"]) { try { counts[t] = copy.prepare("SELECT COUNT(*) c FROM " + t).get().c; } catch (e) { } }
  } finally { copy.close(); }
  if (check !== "ok") throw new Error("backup failed integrity_check: " + check);

  const files = { "luxora.db": sha256(out) };
  for (const k of KEY_FILES) {
    const f = path.join(DATA, k); /* the keyring always lives in data/ (lib/security.js) */
    if (fs.existsSync(f)) { fs.copyFileSync(f, path.join(dest, k)); fs.chmodSync(path.join(dest, k), 0o600); files[k] = sha256(path.join(dest, k)); }
  }
  if (!files["master.json"] && !process.env.LUXORA_MASTER_KEY)
    console.warn("  ⚠️  no data/master.json and no LUXORA_MASTER_KEY — sealed credentials in this backup will not be decryptable");
  const manifest = { name, created_at: new Date().toISOString(), source: DB, bytes: fs.statSync(out).size, integrity: check, counts, files, node: process.version };
  fs.writeFileSync(path.join(dest, "manifest.json"), JSON.stringify(manifest, null, 2), { mode: 0o600 });

  /* prune: newest KEEP sets stay */
  const sets = fs.readdirSync(DIR).filter(d => /^luxora-\d{8}-\d{6}$/.test(d)).sort();
  const pruned = sets.slice(0, Math.max(0, sets.length - KEEP));
  for (const d of pruned) fs.rmSync(path.join(DIR, d), { recursive: true, force: true });

  let uploaded = null;
  if (flag("upload") || process.env.LX_BACKUP_S3_BUCKET) uploaded = await upload(dest, name, Object.keys(files).concat("manifest.json"));

  console.log(JSON.stringify({ ok: true, backup: dest, bytes: manifest.bytes, counts, kept: Math.min(sets.length, KEEP), pruned: pruned.length, uploaded }));
}

async function upload(dest, name, files) {
  const e = process.env;
  if (!e.LX_BACKUP_S3_BUCKET || !e.LX_BACKUP_S3_ACCESS || !e.LX_BACKUP_S3_SECRET) throw new Error("--upload needs LX_BACKUP_S3_BUCKET, LX_BACKUP_S3_ACCESS and LX_BACKUP_S3_SECRET");
  const store = require(path.join(ROOT, "lib", "adapters.js")).storage("s3", { bucket: e.LX_BACKUP_S3_BUCKET, region: e.LX_BACKUP_S3_REGION, accessKey: e.LX_BACKUP_S3_ACCESS, secretKey: e.LX_BACKUP_S3_SECRET, endpoint: e.LX_BACKUP_S3_ENDPOINT });
  if (!store || store.kind !== "s3") throw new Error("S3 storage could not be configured");
  const prefix = (e.LX_BACKUP_S3_PREFIX || "luxora-backups").replace(/\/+$/, "") + "/" + name + "/";
  for (const f of files) {
    const r = await store.put(prefix + f, fs.readFileSync(path.join(dest, f)), f.endsWith(".json") ? "application/json" : "application/octet-stream");
    if (!r.ok) throw new Error("upload of " + f + " failed (HTTP " + r.status + ")");
  }
  return prefix;
}

main().catch(err => { console.error("backup failed: " + err.message); process.exit(1); });
