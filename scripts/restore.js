/* LUXORA Platform — restore a backup written by scripts/backup.js, and prove it is good.
   Usage:
     node scripts/restore.js <backup dir> --to <db path> [--force] [--dry-run]
     node scripts/restore.js <backup dir> --verify-only

   Steps, each fatal on failure:
     1. the file's sha256 matches the manifest (nothing truncated or altered in storage)
     2. decrypt (LX_BACKUP_PASSPHRASE) when the backup is encrypted — GCM fails on a wrong
        passphrase or a tampered file, never yields garbage
     3. the plaintext sha256 matches, PRAGMA integrity_check is ok, and every table holds
        exactly the row count the manifest recorded
   Only then is the database moved into place. An existing target is never overwritten
   without --force, and even then it is not deleted: it moves aside, with its -wal/-shm, to
   <db>.pre-restore-<timestamp>, so a restore can itself be undone. --dry-run verifies and
   prints the plan without touching the target.

   Stop the server first (see DATABASE_RECOVERY_RUNBOOK.md): a process still holding the
   database would keep writing to the file that moved aside. A server started by serve.sh is
   detected from its pid file and the restore is refused.

   Keys are never restored from a backup: sets carry no keyring. A set written by the earlier
   tool (no `format`, a `files` checksum map, possibly with master.json/registry.json) has its
   database verified and restored the same way; any key files in it are left where they are
   and reported, for the operator to handle by the key-recovery procedure. */
"use strict";
const fs = require("fs"), path = require("path"), crypto = require("crypto"), os = require("os");
const { pipeline } = require("stream/promises");
const { MAGIC, FORMAT, sha256, tableCounts } = require("./backup.js");

const ROOT = path.join(__dirname, "..");
function arg(name, dflt) { const i = process.argv.indexOf(name); return i > 0 && process.argv[i + 1] && !process.argv[i + 1].startsWith("--") ? process.argv[i + 1] : dflt; }
const stamp = () => new Date().toISOString().replace(/[-:]/g, "").replace(/\..+/, "").replace("T", "-");

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

/* a server started by serve.sh leaves a pid file in the repository root */
function runningServer() {
  for (const f of fs.readdirSync(ROOT).filter(n => /^\.luxora.*\.pid$/.test(n))) {
    const pid = Number(fs.readFileSync(path.join(ROOT, f), "utf8"));
    try { if (pid) { process.kill(pid, 0); return { pid, file: f }; } } catch (e) { if (e.code !== "ESRCH") throw e; }
  }
  return null;
}

async function restore(dir, { to, force, verifyOnly, dryRun, passphrase }) {
  const manifest = JSON.parse(fs.readFileSync(path.join(dir, "manifest.json"), "utf8"));
  const legacy = !manifest.format && manifest.files && manifest.files["luxora.db"];
  if (manifest.format !== FORMAT && !legacy) throw new Error("unknown backup format " + manifest.format);
  const file = path.join(dir, legacy ? "luxora.db" : manifest.file);
  const want = legacy ? manifest.files["luxora.db"] : manifest.sha256;
  const got = await sha256(file);
  if (got !== want) throw new Error(`checksum mismatch: manifest ${want.slice(0, 16)}…, file ${got.slice(0, 16)}…`);
  const legacyKeys = legacy ? Object.keys(manifest.files).filter(f => f !== "luxora.db") : [];
  const work = fs.mkdtempSync(path.join(to && !verifyOnly && !dryRun ? path.dirname(path.resolve(to)) : os.tmpdir(), ".lx-restore-"));
  const plain = path.join(work, "luxora.db");
  try {
    if (manifest.encrypted) {
      if (!passphrase) throw new Error("backup is encrypted — set LX_BACKUP_PASSPHRASE");
      await decryptFile(file, plain, passphrase);
    } else fs.copyFileSync(file, plain);
    if (!legacy && await sha256(plain) !== manifest.plaintext_sha256) throw new Error("plaintext checksum mismatch");
    const { DatabaseSync } = require("node:sqlite");
    const d = new DatabaseSync(plain, { readOnly: true });
    let integrity, tables;
    try { integrity = d.prepare("PRAGMA integrity_check").all().map(r => Object.values(r)[0]).join("; "); tables = tableCounts(d); }
    finally { d.close(); }
    if (integrity !== "ok") throw new Error("integrity_check: " + integrity);
    if (!legacy) {
      const diff = Object.keys({ ...manifest.tables, ...tables }).filter(t => manifest.tables[t] !== tables[t]);
      if (diff.length) throw new Error("row counts differ from manifest: " + diff.slice(0, 5).map(t => `${t} ${manifest.tables[t]}≠${tables[t]}`).join(", "));
    }
    const result = { verified: true, legacy: !!legacy, tables: Object.keys(tables).length, rows: Object.values(tables).reduce((a, b) => a + b, 0), created_at: manifest.created_at, keys_not_restored: legacyKeys };
    if (verifyOnly) return result;
    const target = path.resolve(to);
    /* a unique name: two restores within a second must not overwrite the first file set aside */
    let aside = null;
    if (fs.existsSync(target)) { const b = target + ".pre-restore-" + stamp(); aside = b; for (let i = 1; ["", "-wal", "-shm"].some(s => fs.existsSync(aside + s)); i++) aside = b + "-" + i; }
    if (aside && !force) throw new Error(target + " exists — stop the server and pass --force to replace it (the current file is moved aside, not deleted)");
    const srv = runningServer();
    if (srv) throw new Error("a server is running (pid " + srv.pid + ", " + srv.file + ") — stop it first");
    if (dryRun) return Object.assign(result, { dry_run: true, would_restore_to: target, would_move_aside: aside });
    /* the old -wal/-shm belong to the old file: they move aside with it, never replay over
       the restored one */
    if (aside) for (const s of ["", "-wal", "-shm"]) if (fs.existsSync(target + s)) fs.renameSync(target + s, aside + s);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.renameSync(plain, target);
    return Object.assign(result, { restored_to: target, previous: aside });
  } finally { fs.rmSync(work, { recursive: true, force: true }); }
}

module.exports = { restore };

if (require.main === module) {
  const dir = process.argv[2];
  const verifyOnly = process.argv.includes("--verify-only");
  const to = arg("--to", "");
  if (!dir || dir.startsWith("--") || (!verifyOnly && !to)) { console.error("usage: node scripts/restore.js <backup dir> (--to <db path> [--force] [--dry-run] | --verify-only)"); process.exit(2); }
  restore(dir, { to, force: process.argv.includes("--force"), verifyOnly, dryRun: process.argv.includes("--dry-run"), passphrase: process.env.LX_BACKUP_PASSPHRASE || "" })
    .then(r => {
      const verb = verifyOnly ? "verified" : r.dry_run ? "verified (dry run — nothing changed)" : "restored";
      console.log(`✓ ${verb} backup of ${r.created_at} · ${r.tables} tables · ${r.rows} rows · integrity ok${r.restored_to ? " → " + r.restored_to : ""}${r.would_restore_to ? " · would restore to " + r.would_restore_to : ""}${r.previous || r.would_move_aside ? " · previous file " + (r.previous ? "moved to " : "would move to ") + (r.previous || r.would_move_aside) : ""}`);
      if (r.keys_not_restored.length) console.log(`  ⚠️  this older set also holds ${r.keys_not_restored.join(", ")} — keys are never restored from a backup; follow the key-recovery procedure in DATABASE_RECOVERY_RUNBOOK.md`);
      console.log(JSON.stringify(Object.assign({ ok: true }, r)));
    })
    .catch(e => { console.error("✗ restore failed: " + e.message); process.exit(1); });
}
