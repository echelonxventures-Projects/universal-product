/* LUXORA Platform — consistent, verifiable backups of the SQLite store.
   The platform runs on one SQLite file in WAL mode (lib/db.js). Copying that file while the
   server writes is not a backup: the -wal holds committed pages the main file does not yet
   have. `VACUUM INTO` takes a read transaction and writes one self-contained, defragmented
   copy that is consistent at a single point in time, while the server keeps serving.

   Usage:
     node scripts/backup.js [--out DIR]          snapshot LX_DB (default data/luxora.db)
     npm run backup -- --out /backups

   Each run writes DIR/luxora-<UTC timestamp>/ with
     luxora.db[.enc]   the snapshot (encrypted when LX_BACKUP_PASSPHRASE is set)
     manifest.json     sha256 + bytes of the file written, per-table row counts, integrity result

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

function arg(name, dflt) { const i = process.argv.indexOf(name); return i > 0 && process.argv[i + 1] ? process.argv[i + 1] : dflt; }
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
  const dir = path.join(outDir, "luxora-" + stamp());
  fs.mkdirSync(dir, { recursive: true, mode: 0o700 });
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
    format: "luxora-backup/1", created_at: new Date().toISOString(), source: path.resolve(source),
    file, encrypted: !!passphrase, bytes: fs.statSync(path.join(dir, file)).size,
    sha256: await sha256(path.join(dir, file)), plaintext_sha256: plainSha,
    integrity, table_count: Object.keys(tables).length, tables
  };
  fs.writeFileSync(path.join(dir, "manifest.json"), JSON.stringify(manifest, null, 2) + "\n", { mode: 0o600 });
  return { dir, manifest };
}

module.exports = { backup, MAGIC, sha256, tableCounts };

if (require.main === module) {
  const source = arg("--db", process.env.LX_DB || path.join(ROOT, "data", "luxora.db"));
  const outDir = arg("--out", process.env.LX_BACKUP_DIR || path.join(ROOT, "backups"));
  backup({ source, outDir, passphrase: process.env.LX_BACKUP_PASSPHRASE || "" }).then(({ dir, manifest }) => {
    const rows = Object.values(manifest.tables).reduce((a, b) => a + b, 0);
    console.log(`✓ backup ${dir}\n  ${manifest.file} · ${manifest.bytes} B · sha256 ${manifest.sha256.slice(0, 16)}… · ${manifest.table_count} tables · ${rows} rows · integrity ${manifest.integrity}${manifest.encrypted ? " · encrypted" : " · NOT encrypted (set LX_BACKUP_PASSPHRASE)"}`);
  }).catch(e => { console.error("✗ backup failed: " + e.message); process.exit(1); });
}
