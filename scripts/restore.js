/* LUXORA Platform — restore a backup written by scripts/backup.js, and prove it is good.
   Usage:
     node scripts/restore.js <backup dir> --to <db path> [--force]
     node scripts/restore.js <backup dir> --verify-only

   Steps, each fatal on failure:
     1. the file's sha256 matches the manifest (nothing truncated or altered in storage)
     2. decrypt (LX_BACKUP_PASSPHRASE) when the backup is encrypted — GCM fails on a wrong
        passphrase or a tampered file, never yields garbage
     3. the plaintext sha256 matches, PRAGMA integrity_check is ok, and every table holds
        exactly the row count the manifest recorded
   Only then is the database moved into place. An existing target is never overwritten
   without --force; stop the server first (see DATABASE_RECOVERY_RUNBOOK.md). */
"use strict";
const fs = require("fs"), path = require("path"), crypto = require("crypto"), os = require("os");
const { pipeline } = require("stream/promises");
const { MAGIC, sha256, tableCounts } = require("./backup.js");

function arg(name, dflt) { const i = process.argv.indexOf(name); return i > 0 && process.argv[i + 1] ? process.argv[i + 1] : dflt; }

async function decryptFile(src, dst, passphrase) {
  const fd = fs.openSync(src, "r");
  const size = fs.fstatSync(fd).size;
  const head = Buffer.alloc(MAGIC.length + 28), tag = Buffer.alloc(16);
  fs.readSync(fd, head, 0, head.length, 0);
  fs.readSync(fd, tag, 0, 16, size - 16);
  fs.closeSync(fd);
  if (!head.subarray(0, MAGIC.length).equals(MAGIC)) throw new Error("not a LUXORA encrypted backup");
  const salt = head.subarray(MAGIC.length, MAGIC.length + 16), iv = head.subarray(MAGIC.length + 16);
  const d = crypto.createDecipheriv("aes-256-gcm", crypto.scryptSync(passphrase, salt, 32), iv);
  d.setAuthTag(tag);
  try { await pipeline(fs.createReadStream(src, { start: head.length, end: size - 17 }), d, fs.createWriteStream(dst, { mode: 0o600 })); }
  catch (e) { fs.rmSync(dst, { force: true }); throw new Error("decryption failed (wrong passphrase or tampered file)"); }
}

async function restore(dir, { to, force, verifyOnly, passphrase }) {
  const manifest = JSON.parse(fs.readFileSync(path.join(dir, "manifest.json"), "utf8"));
  if (manifest.format !== "luxora-backup/1") throw new Error("unknown backup format " + manifest.format);
  const file = path.join(dir, manifest.file);
  const got = await sha256(file);
  if (got !== manifest.sha256) throw new Error(`checksum mismatch: manifest ${manifest.sha256.slice(0, 16)}…, file ${got.slice(0, 16)}…`);
  const work = fs.mkdtempSync(path.join(to && !verifyOnly ? path.dirname(path.resolve(to)) : os.tmpdir(), ".lx-restore-"));
  const plain = path.join(work, "luxora.db");
  try {
    if (manifest.encrypted) {
      if (!passphrase) throw new Error("backup is encrypted — set LX_BACKUP_PASSPHRASE");
      await decryptFile(file, plain, passphrase);
    } else fs.copyFileSync(file, plain);
    if (await sha256(plain) !== manifest.plaintext_sha256) throw new Error("plaintext checksum mismatch");
    const { DatabaseSync } = require("node:sqlite");
    const d = new DatabaseSync(plain, { readOnly: true });
    let integrity, tables;
    try { integrity = d.prepare("PRAGMA integrity_check").all().map(r => Object.values(r)[0]).join("; "); tables = tableCounts(d); }
    finally { d.close(); }
    if (integrity !== "ok") throw new Error("integrity_check: " + integrity);
    const diff = Object.keys({ ...manifest.tables, ...tables }).filter(t => manifest.tables[t] !== tables[t]);
    if (diff.length) throw new Error("row counts differ from manifest: " + diff.slice(0, 5).map(t => `${t} ${manifest.tables[t]}≠${tables[t]}`).join(", "));
    const result = { verified: true, tables: Object.keys(tables).length, rows: Object.values(tables).reduce((a, b) => a + b, 0), created_at: manifest.created_at };
    if (verifyOnly) return result;
    const target = path.resolve(to);
    if (fs.existsSync(target) && !force) throw new Error(target + " exists — stop the server and pass --force to replace it");
    /* the old -wal/-shm belong to the old file; replaying them over the restored one corrupts it */
    for (const s of ["-wal", "-shm"]) fs.rmSync(target + s, { force: true });
    fs.renameSync(plain, target);
    return Object.assign(result, { restored_to: target });
  } finally { fs.rmSync(work, { recursive: true, force: true }); }
}

module.exports = { restore };

if (require.main === module) {
  const dir = process.argv[2];
  const verifyOnly = process.argv.includes("--verify-only");
  const to = arg("--to", "");
  if (!dir || (!verifyOnly && !to)) { console.error("usage: node scripts/restore.js <backup dir> (--to <db path> [--force] | --verify-only)"); process.exit(2); }
  restore(dir, { to, force: process.argv.includes("--force"), verifyOnly, passphrase: process.env.LX_BACKUP_PASSPHRASE || "" })
    .then(r => console.log(`✓ ${verifyOnly ? "verified" : "restored"} backup of ${r.created_at} · ${r.tables} tables · ${r.rows} rows · integrity ok${r.restored_to ? " → " + r.restored_to : ""}`))
    .catch(e => { console.error("✗ restore failed: " + e.message); process.exit(1); });
}
