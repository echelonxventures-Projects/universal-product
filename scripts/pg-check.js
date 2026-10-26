/* LUXORA Platform — the platform on Postgres, end to end.

   Given a Postgres server (PG_CHECK_URL, an admin connection such as
   postgres://postgres@127.0.0.1:5432/postgres), this:
     1. creates a throwaway database on it,
     2. boots a fresh install on SQLite and migrates it there (lib/migrate.js, one transaction),
     3. boots the platform on Postgres and checks the kernel's transactions, places, stores, time,
        expression and Value on it — a write the row refuses must leave the kernel untouched,
     4. runs the real-browser check (every page and console section) with the server on Postgres,
     5. drops the database.
   It exits non-zero on any failure. Usage: PG_CHECK_URL=postgres://… node scripts/pg-check.js [--no-browser] */
"use strict";
const path = require("path");
const os = require("os");
const fs = require("fs");
const { spawnSync } = require("child_process");
const ROOT = path.join(__dirname, "..");
const ADMIN = process.env.PG_CHECK_URL;
if (!ADMIN) { console.error("PG_CHECK_URL is required (an admin connection to a Postgres server)"); process.exit(2); }
const pg = require(path.join(ROOT, "lib", "pg.js"));
const NAME = "lx_check_" + process.pid;
const target = (() => { const u = new URL(ADMIN); u.pathname = "/" + NAME; return u.toString(); })();
const node = (code, env) => spawnSync(process.execPath, ["-e", code], { cwd: ROOT, env: { ...process.env, ...env }, encoding: "utf8", timeout: 900000 });

(async () => {
  let failed = 0;
  const admin = await pg.connect(ADMIN);
  const step = (ok, name, detail) => { console.log((ok ? "  ✓ " : "  ✗ ") + name + (ok || detail == null ? "" : " → " + String(detail).slice(0, 400))); if (!ok) failed++; };
  try {
    const mk = await admin.simple(`CREATE DATABASE "${NAME}"`);
    step(!mk.error, "a throwaway database " + NAME, mk.error);

    /* 2 · a fresh install, migrated in one transaction */
    const sqlite = path.join(os.tmpdir(), NAME + ".db");
    const mig = node(`
      process.env.LX_DB = ${JSON.stringify(sqlite)};
      const s = console.log; console.log = () => {}; require("./lib/db.js"); console.log = s;
      const M = require("./lib/migrate.js"); const st = M.plan();
      M.apply(st, { connectionString: ${JSON.stringify(target)} }).then(o => { console.log(JSON.stringify({ ok: o.ok, failed: o.failed.slice(0, 3), tables: M.summary(st).tables })); process.exit(o.failed.length ? 1 : 0); });`, {});
    for (const x of ["", "-wal", "-shm"]) { try { fs.rmSync(sqlite + x, { force: true }); } catch (e) { } }
    const mo = (mig.stdout.trim().split("\n").pop() || "");
    step(mig.status === 0, "a fresh install migrates to Postgres in one transaction " + mo, mig.stderr.split("\n").filter(l => !/Experimental|trace-warn/.test(l)).join(" ").slice(0, 400) || mo);

    /* 3 · the platform booted on Postgres */
    const boot = node(`
      const errs = []; const s = console.log; console.log = () => {}; const ce = console.error; console.error = (...a) => errs.push(a.join(" "));
      const out = []; const ok = (c, n, x) => out.push({ ok: !!c, n, x });
      try {
        const db = require("./lib/db.js"); console.log = s;
        ok(errs.length === 0, "the boot logs no error", errs.slice(0, 3));
        const K = require("./lib/kernel.js"), P = require("./lib/places.js"), St = require("./lib/stores.js"), E = require("./lib/entity.js"), R = require("./lib/registry.js"), T = require("./lib/time.js"), X = require("./lib/expression.js");
        ok(K.verifyEvents().ok, "the kernel's event chain verifies");
        const c = db.get("SELECT code FROM countries WHERE active=1 ORDER BY position LIMIT 1").code;
        ok(P.country(c) && P.pathOf(P.country(c)), "a country is a place with a path", c);
        ok(R.country(c).currency, "its currency is the kernel's setting", R.country(c));
        const tid = db.get("SELECT id FROM tenants ORDER BY id LIMIT 1").id;
        ok(St.country(tid), "a store's country is its jurisdiction", St.country(tid));
        ok(T.zoneAt(P.country(c)), "a country has a time zone");
        ok(X.available().length > 1, "the storefront speaks several languages");
        ok(R.units().length > R.currencies().length, "Value's master holds units beyond the active currencies");
        const cur = db.get("SELECT code FROM currencies WHERE active=1 LIMIT 1").code;
        const made = E.createEntity(0, "country", { code: "QZ", name: "Testland", currency: cur, locale: "en-IE" });
        ok(!made.error && P.country("QZ"), "a country is created through the write path", made.error);
        const ev = db.get("SELECT COUNT(*) AS n FROM k_events").n;
        const dup = E.createEntity(0, "country", { code: "QZ", name: "Again", currency: cur, locale: "en-IE" });
        ok(dup.error && K.attributes(P.country("QZ")).name === "Testland" && db.get("SELECT COUNT(*) AS n FROM k_events").n === ev, "a write the row refuses leaves the kernel untouched (a real transaction)", dup);
        const orphan = E.createEntity(0, "subdivision", { code: "QQ-01", country_code: "QQ", name: "Nowhere", level: "region" });
        ok(orphan.error && !db.get("SELECT 1 AS x FROM subdivisions WHERE code='QQ-01'"), "a write the kernel refuses never reaches the row", orphan);
        const sd = E.createEntity(0, "subdivision", { code: "QZ-01", country_code: "QZ", name: "North", level: "region" });
        const nested = E.createEntity(0, "subdivision", { code: "QZ-01A", country_code: "QZ", name: "North A", level: "district", parent_id: db.get("SELECT rowid AS id FROM subdivisions WHERE code='QZ-01'").id });
        ok(!sd.error && !nested.error && K.parents(P.HIERARCHY, P.subdivision("QZ-01A")).join() === P.subdivision("QZ-01"), "a nested subdivision finds its parent by the row id Postgres keeps", nested.error);
        ok(K.verifyEvents().ok, "the event chain still verifies");
      } catch (e) { console.log = s; out.push({ ok: false, n: "threw", x: e.stack }); }
      console.log(JSON.stringify(out)); process.exit(0);`, { LX_DB_DRIVER: "postgres", LX_PG_URL: target });
    let checks = [];
    try { checks = JSON.parse(boot.stdout.trim().split("\n").pop()); } catch (e) { checks = [{ ok: false, n: "boot produced no result", x: (boot.stderr || "").slice(0, 600) }]; }
    for (const c of checks) step(c.ok, "Postgres: " + c.n, c.x === undefined ? null : JSON.stringify(c.x));

    /* 4 · every page and console section, with the server on Postgres */
    if (!process.argv.includes("--no-browser")) {
      const br = spawnSync(process.execPath, [path.join(ROOT, "scripts", "browser-check.js")], { cwd: ROOT, env: { ...process.env, LX_DB_DRIVER: "postgres", LX_PG_URL: target, CHECK_PORT: process.env.CHECK_PORT || "8869" }, encoding: "utf8", timeout: 1800000 });
      const lines = (br.stdout || "").split("\n");
      /* each failing page with what went wrong on it */
      lines.forEach((l, i) => { if (/✗/.test(l)) console.log("    " + l.trim() + (lines[i + 1] && !/✓|✗/.test(lines[i + 1]) ? "\n      " + lines[i + 1].trim() : "")); else if (/page loads/.test(l)) console.log("    " + l.trim()); });
      for (const l of (br.stdout || "").split("\n").filter(l => /^\[[0-9a-f-]{36}\]/.test(l)).slice(0, 5)) console.log("      server: " + l.slice(0, 300));
      const why = lines.filter(l => /✗/.test(l)).slice(0, 5).join(" | ") || ("exit " + br.status + (br.signal ? " " + br.signal : "") + (br.error ? " " + br.error.message : "") + ": " + String(br.stderr || "").split("\n").filter(l => l && !/Experimental|trace-warn/.test(l)).slice(-6).join(" / "));
      step(br.status === 0, "Postgres: every page and console section loads clean", why);
    }
  } finally {
    /* a fresh connection: the first one sat idle through the browser run */
    admin.close();
    try { const a2 = await pg.connect(ADMIN); const dr = await a2.simple(`DROP DATABASE IF EXISTS "${NAME}" WITH (FORCE)`); if (dr.error) console.log("  (could not drop " + NAME + ": " + dr.error + ")"); a2.close(); }
    catch (e) { console.log("  (could not drop " + NAME + ": " + e.message + ")"); }
  }
  console.log(failed ? `\n✗ ${failed} failed` : "\n✓ the platform runs on Postgres");
  process.exit(failed ? 1 : 0);
})();
