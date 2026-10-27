/* LUXORA Platform — backups are taken online, verified, and actually restore (the CLI end to end;
   test/production.js covers encryption and the module API).
   A server runs and takes writes; a backup is made while it is up; more writes happen; the
   server stops and the backup is restored — the restored database holds exactly what existed
   at backup time, the replaced one is kept aside, a corrupted backup is refused, and no set
   ever carries the keyring that decrypts it. */
"use strict";
const path = require("path");
const fs = require("fs");
const os = require("os");
const { spawn, execFileSync } = require("child_process");
const { DatabaseSync } = require("node:sqlite");
const ROOT = path.join(__dirname, "..");
const DB = path.join(__dirname, "backup.db");
const DIR = fs.mkdtempSync(path.join(os.tmpdir(), "luxora-backups-"));
const PORT = 8878;
const BASE = `http://localhost:${PORT}`;
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const alive = async () => { try { return (await fetch(BASE + "/healthz")).ok; } catch (e) { return false; } };
const env = { ...process.env, LX_DB: DB, PORT: String(PORT), LX_LOG: "" };
const node = (script, args, extra) => {
  try { return { code: 0, out: execFileSync(process.execPath, [path.join(ROOT, "scripts", script), ...args], { env: { ...env, ...(extra || {}) }, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] }) }; }
  catch (e) { return { code: e.status, out: String(e.stdout || "") + String(e.stderr || "") }; }
};
const users = () => { const d = new DatabaseSync(DB, { readOnly: true }); try { return d.prepare("SELECT email FROM users ORDER BY id").all().map(r => r.email); } finally { d.close(); } };
const register = async email => {
  const c = new Map();
  const call = async (p, m, b) => { const r = await fetch(BASE + p, { method: m || "GET", headers: Object.assign({ Cookie: [...c].map(x => x[0] + "=" + x[1]).join("; ") }, m ? { "x-csrf": c.get("azc") || "", Origin: BASE, "Content-Type": "application/json" } : {}), body: b ? JSON.stringify(b) : undefined });
    (r.headers.getSetCookie ? r.headers.getSetCookie() : []).forEach(k => { const kv = k.split(";")[0], i = kv.indexOf("="); c.set(kv.slice(0, i).trim(), kv.slice(i + 1).trim()); }); return r.status; };
  await call("/api/session?store=luxora");
  return call("/api/auth/register?store=luxora", "POST", { name: "Backup Person", email, password: "Backup-Pass-123" });
};

(async () => {
  const clean = () => { for (const f of fs.readdirSync(__dirname)) if (f.startsWith("backup.db")) fs.rmSync(path.join(__dirname, f), { force: true }); };
  clean();
  const srv = spawn(process.execPath, [path.join(ROOT, "server.js")], { env, stdio: ["ignore", "ignore", "pipe"] });
  let stderr = ""; srv.stderr.on("data", d => { stderr += d; });
  for (let i = 0; i < 120 && !(await alive()); i++) await sleep(500);
  /* a server still booting when the wait gives up must not outlive the test: an orphan keeps the
     port and the database, and every later run talks to it instead of its own server */
  if (!(await alive())) { srv.kill("SIGKILL"); console.error("server failed to boot\n" + stderr); process.exit(1); }
  try {
    console.log("▸ AN ONLINE BACKUP");
    ok(await register("before@example.com") === 200, "a customer registers before the backup");
    const b = node("backup.js", ["--dir", DIR, "--keep", "2"]);
    const res = (() => { try { return JSON.parse(b.out.trim().split("\n").pop()); } catch (e) { return {}; } })();
    ok(b.code === 0 && res.ok && fs.existsSync(path.join(res.backup || "", "luxora.db")), "a backup is taken while the server is running", b.out);
    const set = res.backup || "";
    const man = (() => { try { return JSON.parse(fs.readFileSync(path.join(set, "manifest.json"), "utf8")); } catch (e) { return {}; } })();
    ok(man.integrity === "ok" && man.tables && man.tables.users >= 1 && /^[0-9a-f]{64}$/.test(man.sha256 || ""), "it is integrity-checked and checksummed", man);
    ok(!fs.readdirSync(set).some(f => /master|registry|key/i.test(f)) && fs.readdirSync(set).sort().join(",") === "luxora.db,manifest.json", "the set holds no keyring: the key that decrypts its secrets is kept apart", fs.readdirSync(set));
    ok((fs.statSync(set).mode & 0o077) === 0 && (fs.statSync(path.join(set, "luxora.db")).mode & 0o077) === 0, "the set is readable by its owner only");
    ok(await register("after@example.com") === 200 && users().includes("after@example.com"), "the server keeps taking writes after the backup");

    for (let i = 0; i < 2; i++) { await sleep(1100); node("backup.js", ["--dir", DIR, "--keep", "2"]); }
    ok(fs.readdirSync(DIR).filter(d => d.startsWith("luxora-")).length === 2 && !fs.existsSync(set), "only the newest --keep sets are kept", fs.readdirSync(DIR));
    /* restore the oldest surviving set, which (like the first) predates nothing after it */
    const keepSet = path.join(DIR, fs.readdirSync(DIR).filter(d => d.startsWith("luxora-")).sort()[0]);

    console.log("▸ RESTORE");
    srv.kill("SIGTERM"); await sleep(800);
    /* make the live db differ from the set: a write after the backups */
    const live = new DatabaseSync(DB); live.prepare("INSERT INTO users(tenant_id,name,email,salt,hash) VALUES(1,'Late','late@example.com','x','y')").run(); live.close();
    const noForce = node("restore.js", [keepSet, "--to", DB]);
    ok(noForce.code !== 0 && /exists/.test(noForce.out) && users().includes("late@example.com"), "an existing database is not replaced without --force", noForce.out);
    const dry = node("restore.js", [keepSet, "--to", DB, "--force", "--dry-run"]);
    ok(dry.code === 0 && /dry run/.test(dry.out) && users().includes("late@example.com"), "--dry-run verifies and shows the plan, and changes nothing", dry.out);
    const tampered = path.join(DIR, "tampered"); fs.cpSync(keepSet, tampered, { recursive: true });
    fs.appendFileSync(path.join(tampered, "luxora.db"), "garbage");
    const bad = node("restore.js", [tampered, "--to", DB, "--force"]);
    ok(bad.code !== 0 && /checksum/.test(bad.out) && users().includes("late@example.com"), "a backup that fails its checksum is refused and nothing changes", bad.out);
    const go = node("restore.js", [keepSet, "--to", DB, "--force"]);
    ok(go.code === 0, "the restore runs", go.out);
    const after = users();
    ok(after.includes("before@example.com") && after.includes("after@example.com") && !after.includes("late@example.com"), "the database is exactly the backed-up state", after);
    const aside = fs.readdirSync(__dirname).find(f => /^backup\.db\.pre-restore-\d{8}-\d{6}$/.test(f));
    ok(!!aside, "the replaced database is kept aside, not deleted");

    console.log("▸ OFF-HOST COPIES ARE CIPHERTEXT, AND KEYS NEVER COME BACK FROM A BACKUP");
    {
      const { upload } = require("../scripts/backup.js");
      const s3 = { LX_BACKUP_S3_BUCKET: "b", LX_BACKUP_S3_ACCESS: "a", LX_BACKUP_S3_SECRET: "s" };
      let refused = null; try { await upload(keepSet, JSON.parse(fs.readFileSync(path.join(keepSet, "manifest.json"), "utf8")), s3); } catch (e) { refused = e.message; }
      ok(/refusing to upload an unencrypted backup/.test(refused || ""), "an unencrypted set is never uploaded off the machine", refused);
      /* a set from the earlier tool: a files checksum map and the keyring beside the database */
      const old = path.join(DIR, "legacy-set"); fs.mkdirSync(old);
      fs.copyFileSync(path.join(keepSet, "luxora.db"), path.join(old, "luxora.db"));
      fs.writeFileSync(path.join(old, "master.json"), JSON.stringify({ current: "k9", keys: { k9: "00".repeat(32) } }));
      const sum = f => require("crypto").createHash("sha256").update(fs.readFileSync(path.join(old, f))).digest("hex");
      fs.writeFileSync(path.join(old, "manifest.json"), JSON.stringify({ name: "legacy", created_at: new Date().toISOString(), files: { "luxora.db": sum("luxora.db"), "master.json": sum("master.json") } }));
      const liveKeys = path.join(ROOT, "data", "master.json"), before = fs.existsSync(liveKeys) ? fs.readFileSync(liveKeys, "utf8") : null;
      const lg = node("restore.js", [old, "--to", DB, "--force"]);
      ok(lg.code === 0 && /keys are never restored/.test(lg.out) && (fs.existsSync(liveKeys) ? fs.readFileSync(liveKeys, "utf8") : null) === before, "an older set restores its database; the keyring inside it is reported, never restored", lg.out);
      const lgBad = path.join(DIR, "legacy-bad"); fs.cpSync(old, lgBad, { recursive: true }); fs.appendFileSync(path.join(lgBad, "luxora.db"), "x");
      ok(node("restore.js", [lgBad, "--to", DB, "--force"]).code !== 0, "…and an older set that fails its checksum is refused too");
      /* put the verified modern set back for the serving check below */
      ok(node("restore.js", [keepSet, "--to", DB, "--force"]).code === 0, "the modern set restores again");
    }

    console.log("▸ THE RESTORED DATABASE SERVES");
    const srv2 = spawn(process.execPath, [path.join(ROOT, "server.js")], { env, stdio: ["ignore", "ignore", "pipe"] });
    for (let i = 0; i < 120 && !(await alive()); i++) await sleep(500);
    const c = new Map();
    const s0 = await fetch(BASE + "/api/session?store=luxora"); (s0.headers.getSetCookie() || []).forEach(k => { const kv = k.split(";")[0], i = kv.indexOf("="); c.set(kv.slice(0, i), kv.slice(i + 1)); });
    const li = await fetch(BASE + "/api/auth/login?store=luxora", { method: "POST", headers: { Cookie: [...c].map(x => x[0] + "=" + x[1]).join("; "), "x-csrf": c.get("azc") || "", Origin: BASE, "Content-Type": "application/json" }, body: JSON.stringify({ email: "before@example.com", password: "Backup-Pass-123" }) });
    ok(li.status === 200, "a customer from before the backup signs in on the restored server", li.status);
    srv2.kill("SIGTERM"); await sleep(500);
  } catch (e) {
    failed++; console.error("  ✗ harness error:", e && e.stack || e);
  } finally {
    try { srv.kill("SIGTERM"); } catch (e) { }
    await sleep(300); clean(); fs.rmSync(DIR, { recursive: true, force: true });
  }
  console.log(`\n${passed} passed, ${failed} failed`);
  process.exit(failed ? 1 : 0);
})();
