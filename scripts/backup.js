/* LUXORA Platform — consistent, verifiable backups of the SQLite store.
   The platform runs on one SQLite file in WAL mode (lib/db.js). Copying that file while the
   server writes is not a backup: the -wal holds committed pages the main file does not yet
   have. `VACUUM INTO` takes a read transaction and writes one self-contained, defragmented
   copy that is consistent at a single point in time, while the server keeps serving.

   Usage:
     node scripts/backup.js [--db FILE] [--out DIR] [--keep N] [--upload]
     npm run backup -- --out /backups

     --db      the database to snapshot (default LX_DB, else data/luxora.db)
     --out     where sets are written (default LX_BACKUP_DIR, else backups/); --dir is an alias
     --keep    keep only the newest N sets in that directory (or LX_BACKUP_KEEP). Without it
               nothing is ever deleted.
     --upload  also copy the set off the machine to S3-compatible storage (also on whenever
               LX_BACKUP_S3_BUCKET is set): LX_BACKUP_S3_BUCKET, LX_BACKUP_S3_REGION,
               LX_BACKUP_S3_ACCESS, LX_BACKUP_S3_SECRET, LX_BACKUP_S3_ENDPOINT (R2/MinIO/B2),
               LX_BACKUP_S3_PREFIX. Only an encrypted set leaves the machine, unless
               LX_BACKUP_ALLOW_PLAINTEXT_UPLOAD=1. An upload failure exits non-zero.

   Each run writes DIR/luxora-<UTC timestamp>/ with
     luxora.db[.enc]   the snapshot (encrypted when LX_BACKUP_PASSPHRASE is set)
     manifest.json     sha256 + bytes of the file written, per-table row counts, integrity result
   and prints a summary line, then one JSON line for a timer or cron job to read.

   The keyring (data/master.json) and the registry seal key (data/registry.json) are NOT
   included: a backup carrying the key that decrypts the secrets inside it protects nothing.
   Back those up once, separately, to a different store (see DATABASE_RECOVERY_RUNBOOK.md).

   Restore and verify with scripts/restore.js. A backup that was never restored is not a
   backup — the runbook's drill restores the latest one on a schedule. */
"use strict";
const fs = require("fs"), path = require("path"), crypto = require("crypto");
const { pipeline } = require("stream/promises");

const ROOT = path.join(__dirname, "..");
const MAGIC = Buffer.from("LXBK1\0");
const FORMAT = "luxora-backup/1";
const SET = /^luxora-\d{8}T\d{6}-\d{3}Z$/;

function arg(name, dflt) { const i = process.argv.indexOf(name); return i > 0 && process.argv[i + 1] && !process.argv[i + 1].startsWith("--") ? process.argv[i + 1] : dflt; }
function stamp() { return new Date().toISOString().replace(/[-:]/g, "").replace(".", "-"); }
async function sha256(file) {
  const h = crypto.createHash("sha256");
  await pipeline(fs.createReadStream(file), h);
  return h.digest("hex");
}
function tableCounts(db) {
  const out = {};
  for (const { name } of db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").all())
    out[name] = db.prepare(`SELECT COUNT(*) c FROM "${name.replace(/"/g, '""')}"`).get().c;
  return out;
}
/* AES-256-GCM, key from scrypt(passphrase, random salt). File layout:
   MAGIC(6) | salt(16) | iv(12) | ciphertext | tag(16). Streamed, so size is unbounded. */
async function encryptFile(src, dst, passphrase) {
  const salt = crypto.randomBytes(16), iv = crypto.randomBytes(12);
  const key = crypto.scryptSync(passphrase, salt, 32);
  const c = crypto.createCipheriv("aes-256-gcm", key, iv);
  const out = fs.createWriteStream(dst, { mode: 0o600 });
  out.write(Buffer.concat([MAGIC, salt, iv]));
  await pipeline(fs.createReadStream(src), c, out, { end: false });
  await new Promise((res, rej) => out.end(c.getAuthTag(), e => e ? rej(e) : res()));
}

async function backup({ source, outDir, passphrase }) {
  const { DatabaseSync } = require("node:sqlite");
  if (!fs.existsSync(source)) throw new Error("no database at " + source);
  fs.mkdirSync(outDir, { recursive: true, mode: 0o700 });
  const dir = path.join(outDir, "luxora-" + stamp());
  fs.mkdirSync(dir, { mode: 0o700 });
  const snap = path.join(dir, "luxora.db");
  const src = new DatabaseSync(source, { readOnly: true });
  try { src.exec("PRAGMA busy_timeout = 10000"); src.prepare("VACUUM INTO ?").run(snap); }
  finally { src.close(); }
  fs.chmodSync(snap, 0o600);
  /* verify the copy itself, not the live file: the manifest describes what was written */
  const copy = new DatabaseSync(snap, { readOnly: true });
  let integrity, tables;
  try {
    integrity = copy.prepare("PRAGMA integrity_check").all().map(r => Object.values(r)[0]).join("; ");
    tables = tableCounts(copy);
  } finally { copy.close(); }
  if (integrity !== "ok") throw new Error("snapshot failed integrity_check: " + integrity);
  const plainSha = await sha256(snap);
  let file = "luxora.db";
  if (passphrase) {
    file = "luxora.db.enc";
    await encryptFile(snap, path.join(dir, file), passphrase);
    fs.rmSync(snap);
  }
  const manifest = {
    format: FORMAT, created_at: new Date().toISOString(), source: path.resolve(source),
    file, encrypted: !!passphrase, bytes: fs.statSync(path.join(dir, file)).size,
    sha256: await sha256(path.join(dir, file)), plaintext_sha256: plainSha,
    integrity, table_count: Object.keys(tables).length, tables
  };
  fs.writeFileSync(path.join(dir, "manifest.json"), JSON.stringify(manifest, null, 2) + "\n", { mode: 0o600 });
  return { dir, manifest };
}

/* the newest `keep` sets stay. Only directories this tool wrote (its name pattern and a
   manifest of its format) are ever considered, and never the set just written. */
function prune(outDir, keep, current) {
  const sets = fs.readdirSync(outDir).filter(d => SET.test(d)).filter(d => {
    try { return JSON.parse(fs.readFileSync(path.join(outDir, d, "manifest.json"), "utf8")).format === FORMAT; } catch (e) { return false; }
  }).sort();
  const drop = sets.slice(0, Math.max(0, sets.length - keep)).filter(d => path.join(outDir, d) !== current);
  for (const d of drop) fs.rmSync(path.join(outDir, d), { recursive: true, force: true });
  return { kept: sets.length - drop.length, pruned: drop };
}

async function upload(dir, manifest, env) {
  const e = env || process.env;
  if (!e.LX_BACKUP_S3_BUCKET || !e.LX_BACKUP_S3_ACCESS || !e.LX_BACKUP_S3_SECRET) throw new Error("upload needs LX_BACKUP_S3_BUCKET, LX_BACKUP_S3_ACCESS and LX_BACKUP_S3_SECRET");
  /* the set holds every customer record; off the machine it travels only as ciphertext */
  if (!manifest.encrypted && e.LX_BACKUP_ALLOW_PLAINTEXT_UPLOAD !== "1") throw new Error("refusing to upload an unencrypted backup — set LX_BACKUP_PASSPHRASE (or LX_BACKUP_ALLOW_PLAINTEXT_UPLOAD=1)");
  const store = require(path.join(ROOT, "lib", "adapters.js")).storage("s3", { bucket: e.LX_BACKUP_S3_BUCKET, region: e.LX_BACKUP_S3_REGION, accessKey: e.LX_BACKUP_S3_ACCESS, secretKey: e.LX_BACKUP_S3_SECRET, endpoint: e.LX_BACKUP_S3_ENDPOINT });
  if (!store || store.kind !== "s3") throw new Error("S3 storage could not be configured");
  const prefix = (e.LX_BACKUP_S3_PREFIX || "luxora-backups").replace(/\/+$/, "") + "/" + path.basename(dir) + "/";
  /* the data file first, the manifest last: a set whose manifest is there is complete */
  for (const f of [manifest.file, "manifest.json"]) {
    const r = await store.put(prefix + f, fs.readFileSync(path.join(dir, f)), f.endsWith(".json") ? "application/json" : "application/octet-stream");
    if (!r.ok) throw new Error("upload of " + f + " failed (HTTP " + r.status + ")");
  }
  return prefix;
}

module.exports = { backup, prune, upload, MAGIC, FORMAT, sha256, tableCounts };

if (require.main === module) {
  const source = arg("--db", process.env.LX_DB || path.join(ROOT, "data", "luxora.db"));
  const outDir = path.resolve(arg("--out", arg("--dir", process.env.LX_BACKUP_DIR || path.join(ROOT, "backups"))));
  const keepRaw = arg("--keep", process.env.LX_BACKUP_KEEP || "");
  const keep = keepRaw === "" ? null : Number(keepRaw);
  if (keep !== null && !(Number.isInteger(keep) && keep >= 1)) { console.error("✗ backup failed: --keep must be a whole number ≥ 1"); process.exit(2); }
  const wantUpload = process.argv.includes("--upload") || !!process.env.LX_BACKUP_S3_BUCKET;
  (async () => {
    const { dir, manifest } = await backup({ source, outDir, passphrase: process.env.LX_BACKUP_PASSPHRASE || "" });
    const rows = Object.values(manifest.tables).reduce((a, b) => a + b, 0);
    console.log(`✓ backup ${dir}\n  ${manifest.file} · ${manifest.bytes} B · sha256 ${manifest.sha256.slice(0, 16)}… · ${manifest.table_count} tables · ${rows} rows · integrity ${manifest.integrity}${manifest.encrypted ? " · encrypted" : " · NOT encrypted (set LX_BACKUP_PASSPHRASE)"}`);
    const uploaded = wantUpload ? await upload(dir, manifest) : null;
    const kept = keep !== null ? prune(outDir, keep, dir) : null;
    console.log(JSON.stringify({ ok: true, backup: dir, file: manifest.file, bytes: manifest.bytes, encrypted: manifest.encrypted, rows, uploaded, kept: kept && kept.kept, pruned: kept ? kept.pruned.length : 0 }));
  })().catch(e => { console.error("✗ backup failed: " + e.message); process.exit(1); });
}
