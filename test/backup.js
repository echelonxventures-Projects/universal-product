/* LUXORA Platform — backups are taken online, verified, and actually restore.
   A server runs and takes writes; a backup is made while it is up; more writes happen; the
   server stops and the backup is restored — the restored database holds exactly what existed
   at backup time, the replaced one is kept aside, and a corrupted backup is refused. */
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
  if (!(await alive())) { console.error("server failed to boot\n" + stderr); process.exit(1); }
  try {
    console.log("▸ AN ONLINE BACKUP");
    ok(await register("before@example.com") === 200, "a customer registers before the backup");
    const b = node("backup.js", ["--dir", DIR, "--keep", "2"]);
    const res = (() => { try { return JSON.parse(b.out.trim().split("\n").pop()); } catch (e) { return {}; } })();
    ok(b.code === 0 && res.ok && fs.existsSync(path.join(res.backup || "", "luxora.db")), "a backup is taken while the server is running", b.out);
    const set = res.backup || "";
    const man = (() => { try { return JSON.parse(fs.readFileSync(path.join(set, "manifest.json"), "utf8")); } catch (e) { return {}; } })();
    ok(man.integrity === "ok" && man.counts && man.counts.users >= 1 && /^[0-9a-f]{64}$/.test((man.files || {})["luxora.db"] || ""), "it is integrity-checked and checksummed", man);
    ok(!!(man.files || {})["master.json"] || !fs.existsSync(path.join(ROOT, "data", "master.json")), "the keyring that unlocks sealed credentials is in the set", Object.keys(man.files || {}));
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
    const dry = node("restore.js", [keepSet, "--force"]);
    ok(dry.code === 0 && /dry run/.test(dry.out) && users().includes("late@example.com"), "without --yes it only shows the plan", dry.out);
    const tampered = path.join(DIR, "tampered"); fs.cpSync(keepSet, tampered, { recursive: true });
    fs.appendFileSync(path.join(tampered, "luxora.db"), "garbage");
    const bad = node("restore.js", [tampered, "--yes", "--force"]);
    ok(bad.code !== 0 && /checksum/.test(bad.out) && users().includes("late@example.com"), "a backup that fails its checksum is refused and nothing changes", bad.out);
    const go = node("restore.js", [keepSet, "--yes", "--force"]);
    ok(go.code === 0, "the restore runs", go.out);
    const after = users();
    ok(after.includes("before@example.com") && after.includes("after@example.com") && !after.includes("late@example.com"), "the database is exactly the backed-up state", after);
    const aside = fs.readdirSync(__dirname).find(f => /^backup\.db\.pre-restore-\d{8}-\d{6}$/.test(f));
    ok(!!aside, "the replaced database is kept aside, not deleted");

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
