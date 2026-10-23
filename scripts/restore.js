#!/usr/bin/env node
/* LUXORA Platform — restore a backup made by scripts/backup.js.

   node scripts/restore.js <backup-dir> [--yes] [--keys] [--force]

   Stop the server first (systemctl stop luxora / docker compose stop luxora): restoring
   under a running process would have it keep writing to the replaced file. A server started
   by serve.sh is detected from its pid file and refused; --force skips that check (only for
   a server known to use a different database).

   - The backup's manifest checksums and SQLite integrity_check must pass, or nothing is
     touched.
   - The current database (and its -wal/-shm) is moved aside to
     <db>.pre-restore-<timestamp>, never deleted, so a restore can itself be undone.
   - --keys also restores data/master.json / data/registry.json from the backup (the current
     ones are moved aside the same way). Use it when restoring onto a new machine, or when
     the keyring was lost; without the matching keyring, sealed gateway credentials in the
     restored database cannot be decrypted.
   - Without --yes it prints what it would do and exits. */
"use strict";
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const { DatabaseSync } = require("node:sqlite");

const ROOT = path.join(__dirname, "..");
const DATA = path.join(ROOT, "data");
const DB = path.resolve(process.env.LX_DB || path.join(DATA, "luxora.db"));
const src = process.argv.slice(2).find(a => !a.startsWith("--"));
const yes = process.argv.includes("--yes"), keys = process.argv.includes("--keys"), force = process.argv.includes("--force");
const sha256 = file => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
const stamp = () => new Date().toISOString().replace(/[-:]/g, "").replace(/\..+/, "").replace("T", "-");
const die = m => { console.error("restore refused: " + m); process.exit(1); };

if (!src) die("usage: node scripts/restore.js <backup-dir> [--yes] [--keys]");
const dir = path.resolve(src);
const manifestFile = path.join(dir, "manifest.json");
if (!fs.existsSync(manifestFile)) die("no manifest.json in " + dir);
let manifest; try { manifest = JSON.parse(fs.readFileSync(manifestFile, "utf8")); } catch (e) { die("manifest.json is not valid JSON"); }
for (const [f, sum] of Object.entries(manifest.files || {})) {
  const p = path.join(dir, f);
  if (!fs.existsSync(p)) die("missing " + f);
  if (sha256(p) !== sum) die(f + " does not match its checksum — the backup is corrupt or was altered");
}
if (!manifest.files || !manifest.files["luxora.db"]) die("the manifest lists no database");
const backupDb = path.join(dir, "luxora.db");
const probe = new DatabaseSync(backupDb, { readOnly: true });
const check = probe.prepare("PRAGMA integrity_check").all().map(r => Object.values(r)[0]).join("; ");
probe.close();
if (check !== "ok") die("integrity_check: " + check);

/* a server holding the database would keep writing to the moved-aside file */
const pidFiles = force ? [] : fs.readdirSync(ROOT).filter(f => /^\.luxora.*\.pid$/.test(f));
for (const f of pidFiles) {
  const pid = Number(fs.readFileSync(path.join(ROOT, f), "utf8"));
  try { if (pid) { process.kill(pid, 0); die("a server is running (pid " + pid + ", " + f + ") — stop it first"); } } catch (e) { if (e.code !== "ESRCH") throw e; }
}

const plan = [`restore ${backupDb} (${manifest.created_at}, ${manifest.bytes} bytes, ${JSON.stringify(manifest.counts || {})})`, `  → ${DB}`];
const aside = "pre-restore-" + stamp();
if (fs.existsSync(DB)) plan.push(`  current database moved to ${DB}.${aside}`);
const keyFiles = keys ? ["master.json", "registry.json"].filter(k => manifest.files[k]) : [];
for (const k of keyFiles) plan.push(`  key file ${k} restored to ${path.join(DATA, k)}` + (fs.existsSync(path.join(DATA, k)) ? ` (current moved to ${k}.${aside})` : ""));
if (!keys && manifest.files["master.json"] && fs.existsSync(path.join(DATA, "master.json")) && sha256(path.join(DATA, "master.json")) !== manifest.files["master.json"])
  plan.push("  ⚠️  the current keyring differs from the backup's — add --keys if sealed credentials fail to decrypt after restoring");
console.log(plan.join("\n"));
if (!yes) { console.log("\n(dry run — add --yes to restore)"); process.exit(0); }

for (const suf of ["", "-wal", "-shm"]) if (fs.existsSync(DB + suf)) fs.renameSync(DB + suf, DB + "." + aside + suf);
fs.mkdirSync(path.dirname(DB), { recursive: true });
fs.copyFileSync(backupDb, DB);
fs.chmodSync(DB, 0o600);
for (const k of keyFiles) {
  const dest = path.join(DATA, k);
  if (fs.existsSync(dest)) fs.renameSync(dest, dest + "." + aside);
  fs.copyFileSync(path.join(dir, k), dest); fs.chmodSync(dest, 0o600);
}
console.log(JSON.stringify({ ok: true, restored: DB, from: dir, keys: keyFiles, previous: fs.existsSync(DB + "." + aside) ? DB + "." + aside : null }));
