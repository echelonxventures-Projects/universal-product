/* LUXORA Platform — the constitutional laws, each with its check (LAW-026: a law without a check is
   not finished). A law is marked `enforced` in _registry/domains.json only when its check here passes
   with nothing outstanding; the register names this file in the law's enforcedBy.
   Usage: node test/laws.js */
"use strict";
const fs = require("fs"), path = require("path"), os = require("os");
const ROOT = path.join(__dirname, "..");
const DB = path.join(os.tmpdir(), "luxora-laws-" + process.pid + ".db");
process.env.LX_DB = DB; process.env.LX_QUIET = "1";
let pass = 0, fail = 0;
function ok(c, msg, extra) { if (c) { pass++; console.log("  ✓ " + msg); } else { fail++; console.log("  ✗ " + msg + (extra !== undefined ? " → " + JSON.stringify(extra).slice(0, 600) : "")); } }
const cleanup = () => { for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } } };

(async () => {
  const db = require(path.join(ROOT, "lib", "db.js"));
  await new Promise(r => setImmediate(r)); // the bootstrap has run
  const sec = require(path.join(ROOT, "lib", "security.js"));
  const schema = fs.readFileSync(path.join(ROOT, "schema.sql"), "utf8");
  /* each table's column list, read by balanced parentheses (a column default may hold its own) */
  const tables = {};
  for (const m of schema.matchAll(/CREATE TABLE (?:IF NOT EXISTS )?"?(\w+)"?\s*\(/g)) {
    let d = 1, i = m.index + m[0].length;
    for (; i < schema.length && d; i++) { const c = schema[i]; if (c === "(") d++; else if (c === ")") d--; else if (c === "'") i = schema.indexOf("'", i + 1); }
    tables[m[1]] = schema.slice(m.index + m[0].length, i - 1);
  }

  console.log("▸ LAW-017 · PLATFORM-OWNED MASTER DATA — tenants select it, never copy it");
  {
    const master = Object.keys(tables).filter(t => !/\btenant_id\b/.test(tables[t]));
    const tenant = Object.keys(tables).filter(t => /\btenant_id\b/.test(tables[t]));
    /* a copy repeats the master's own descriptive columns; a selection (tenant_modules: module_id, the
       store's status and config) references the master and holds only the tenant's choice */
    const cols = t => [...tables[t].matchAll(/(?:^|,)\s*([a-z_]+)\s+(?:TEXT|INTEGER|REAL|NUMERIC|BLOB)/gi)].map(m => m[1].toLowerCase());
    const OWN = new Set(["id", "uid", "tenant_id", "status", "position", "config", "created_at", "updated_at", "enabled", "active"]);
    const named = tenant.map(t => [t, master.find(m => [`tenant_${m}`, `store_${m}`, `${m}_overrides`, `${m}_copy`].includes(t))]).filter(x => x[1]);
    const copies = named.filter(([t, m]) => cols(m).filter(c => !OWN.has(c) && cols(t).includes(c)).length >= 2).map(([t, m]) => t + " copies " + m);
    ok(master.length > 0 && copies.length === 0, "no tenant-scoped table repeats a platform master's columns (a selection references it)", copies);
    const geoValue = ["countries", "subdivisions", "currencies", "fx_rates", "messages"].filter(t => tables[t]);
    ok(geoValue.length >= 4 && geoValue.every(t => !/\btenant_id\b/.test(tables[t])), "the place, value and language masters carry no tenant column", geoValue.filter(t => /\btenant_id\b/.test(tables[t])));
  }

  console.log("▸ LAW-023 · SECURITY FLOOR — a policy may tighten the baseline, never weaken it");
  {
    const base = sec.DEFAULT_POLICY;
    const weakening = { minPasswordLength: base.minPasswordLength - 4, requireLetterDigit: false, blockCommon: false, lockoutThreshold: base.lockoutThreshold * 10,
      lockoutBaseSec: 1, lockoutCapSec: 1, csrfEnabled: false, hsts: false, kdfV2: { logN: base.kdfV2.logN - 3 } };
    const breaches = sec.floorBreaches(weakening);
    ok(Object.keys(sec.FLOOR).every(k => breaches.includes(k)) && breaches.includes("kdfV2.logN"), "every floor key is detected when weakened", breaches);
    const after = sec.setPolicy(weakening);
    ok(Object.keys(sec.FLOOR).every(k => after[k] === base[k]) && after.kdfV2.logN === base.kdfV2.logN, "a weakening patch saves at the baseline, not below it",
      Object.fromEntries(Object.keys(sec.FLOOR).map(k => [k, after[k]])));
    db.run("INSERT INTO platform_settings(key,value) VALUES('policy',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", JSON.stringify({ minPasswordLength: 3, blockCommon: false }));
    const eff = sec.policy(true);
    ok(eff.minPasswordLength === base.minPasswordLength && eff.blockCommon === true, "a weaker policy written straight to storage never takes effect", { minPasswordLength: eff.minPasswordLength, blockCommon: eff.blockCommon });
    const tight = sec.setPolicy({ minPasswordLength: base.minPasswordLength + 6, lockoutThreshold: 3, kdfV2: { logN: base.kdfV2.logN + 1 } });
    ok(tight.minPasswordLength === base.minPasswordLength + 6 && tight.lockoutThreshold === 3 && tight.kdfV2.logN === base.kdfV2.logN + 1, "tightening is kept");
    const rules = fs.readFileSync(path.join(ROOT, "lib", "routes", "rules.js"), "utf8");
    ok(/sec\.floorBreaches\(/.test(rules) && /422\)/.test(rules), "the platform's policy route refuses a patch below the baseline (422)");
    sec.setPolicy({ minPasswordLength: base.minPasswordLength, lockoutThreshold: base.lockoutThreshold, kdfV2: { logN: base.kdfV2.logN } });
  }

  console.log("▸ LAW-009 · DEPENDENCY LAW — no circular dependency, no mutual ownership");
  {
    /* every module, loaded first in a fresh process, finds every module it reads finished: a read of
       a module still loading is Node's "inside circular dependency" warning, or a seed that finds
       its target's function missing */
    const { spawn } = require("child_process");
    const mods = fs.readdirSync(path.join(ROOT, "lib")).filter(f => f.endsWith(".js")).map(f => "lib/" + f)
      .concat(fs.readdirSync(path.join(ROOT, "lib", "routes")).filter(f => f.endsWith(".js")).map(f => "lib/routes/" + f));
    /* each probe starts from a clone of this run's seeded database: seeding again runs the same
       seed code (the reads under test) without rebuilding 35 MB from nothing each time */
    db.run("PRAGMA wal_checkpoint(TRUNCATE)");
    const probe = m => new Promise(res => {
      const dbf = path.join(os.tmpdir(), "luxora-law9-" + process.pid + "-" + m.replace(/\W/g, "_") + ".db");
      fs.copyFileSync(DB, dbf, fs.constants.COPYFILE_FICLONE);
      const p = spawn(process.execPath, ["--trace-warnings", "-e", `require(${JSON.stringify(path.join(ROOT, m))}); setTimeout(() => process.exit(0), 100)`],
        { env: { ...process.env, LX_DB: dbf, LX_QUIET: "1" }, stdio: ["ignore", "pipe", "pipe"] });
      let out = ""; p.stdout.on("data", d => out += d); p.stderr.on("data", d => out += d);
      const t = setTimeout(() => p.kill("SIGKILL"), 120000);
      p.on("exit", () => { clearTimeout(t); for (const x of ["", "-wal", "-shm"]) { try { fs.rmSync(dbf + x, { force: true }); } catch (e) { } }
        const bad = /inside circular dependency|is not a function|seed failed|tables failed|import failed/.test(out);
        res(bad ? m + ": " + (out.match(/(Accessing non-existent property '\w+'|[\w.]+ is not a function|\w+ (seed|tables|import) failed: [^\n]{0,80})/) || [""])[0] : null); });
    });
    const found = [];
    for (let i = 0; i < mods.length; i += 8) found.push(...(await Promise.all(mods.slice(i, i + 8).map(probe))).filter(Boolean));
    ok(found.length === 0, "every module (" + mods.length + "), loaded first, reads no module that is still loading", found);
    const map = require(path.join(ROOT, "scripts", "domain-map.js")).map();
    const doubles = Object.entries(map.kinds).flatMap(([k, v]) => (v.double || []).map(d => k + ": " + (d.artifact || d)));
    ok(doubles.length === 0, "no artifact is owned by two domains (no mutual ownership)", doubles);
  }

  console.log("▸ LAW-015 · TECHNOLOGY AGNOSTIC — a vendor, database or driver lives in its adapter");
  {
    /* the vendor words are read from the data, never listed here: every provider spec that calls an
       external host (its id and the host's name), every carrier adapter, every runtime driver that is
       not a mode of the platform's own */
    const prov = JSON.parse(fs.readFileSync(path.join(ROOT, "lib", "seed", "providers.json"), "utf8")).PROVIDER_SPECS || {};
    const words = new Set();
    for (const [k, v] of Object.entries(prov)) {
      const m = /^https:\/\/([^/:]+)/.exec(String(v.base || v.baseUrl || v.url || v.endpoint || ""));
      if (!m) continue;
      const id = k.split(":").pop().toLowerCase();
      if (/^[a-z][a-z0-9-]{3,}$/.test(id) && id !== "meta") words.add(id); // "meta" is also the platform's own module
      const labels = m[1].toLowerCase().replace(/\{\{[^}]*\}\}/g, "").split(".").filter(l => l && !/^(api|api-m|www|connect|business-api|graph|v\d+|com|net|io|org)$/.test(l));
      if (labels.length) words.add(labels[labels.length - 1]);
    }
    const carrierFiles = fs.readdirSync(path.join(ROOT, "lib")).filter(f => /^carrier-[a-z0-9_]+\.js$/.test(f));
    for (const f of carrierFiles) words.add(require(path.join(ROOT, "lib", f)).row.provider_id);
    const MODES = new Set(["memory", "inline", "local", "db", "auto", "webhook", "hook", "none", "file", "sqlite", "live", "offline", "token"]);
    for (const c of Object.values(require(path.join(ROOT, "lib", "config.js")).RUNTIME_CATALOG)) for (const d of c.drivers || []) if (!MODES.has(d)) words.add(String(d).toLowerCase());
    ok(words.size >= 10 && words.has("postgres") && carrierFiles.length >= 1, "the vendor words come from the provider specs, the carrier adapters and the runtime drivers (" + words.size + ")", [...words]);
    /* the adapter layer, where they may be named: runtime adapters and their catalogue, the provider
       spec engine and outbound transport, the persistence layer, and each carrier's own file */
    const ADAPTER = /^lib\/(adapters|config|spec|connect|db|pg|pgbridge|pgworker|dbpool|migrate|queue|providers|carrier-[a-z0-9_]+)\.js$/;
    const { tokenize } = (() => { /* comments say why; only code and its strings are a dependency */
      const strip = src => src.replace(/\/\*[\s\S]*?\*\//g, m => m.replace(/[^\n]/g, " ")).replace(/(^|[^:"'`\\])\/\/[^\n]*/g, (m, p) => p + " ".repeat(m.length - p.length));
      return { tokenize: strip };
    })();
    const files = fs.readdirSync(path.join(ROOT, "lib")).filter(f => f.endsWith(".js")).map(f => "lib/" + f)
      .concat(fs.readdirSync(path.join(ROOT, "lib", "routes")).filter(f => f.endsWith(".js")).map(f => "lib/routes/" + f)).filter(f => !ADAPTER.test(f));
    const res = [...words].map(w => [w, new RegExp("(^|[^a-z0-9_-])" + w.replace(/-/g, "\\-") + "([^a-z0-9_]|$)", "i")]);
    const hits = [];
    for (const f of files) tokenize(fs.readFileSync(path.join(ROOT, f), "utf8")).split("\n").forEach((line, i) => { for (const [w, r] of res) if (r.test(line)) hits.push(f + ":" + (i + 1) + " " + w); });
    ok(hits.length === 0, "no platform module outside the adapter layer names a vendor, database or driver (" + files.length + " modules)", hits.slice(0, 20));
  }

  /* the laws with work outstanding hold a ratchet: the count may only fall
     (_registry/register-baseline.json → lawRatchets; lower it once the work is done) */
  const RB = JSON.parse(fs.readFileSync(path.join(ROOT, "_registry", "register-baseline.json"), "utf8")).lawRatchets || {};
  const UPDATE = process.argv.includes("--update"), now = {};
  const ratchet = (key, n, what, sample) => {
    now[key] = n;
    const base = RB[key];
    ok(base != null && n <= base, what + ": " + n + (base != null ? " (baseline " + base + ")" : " (no baseline — run node test/laws.js --update)"), n > (base || 0) ? sample : undefined);
    if (base != null && n < base) console.log("    ↓ below the baseline — node test/laws.js --update holds the lower count");
  };
  const stripComments = src => src.replace(/\/\*[\s\S]*?\*\//g, m => m.replace(/[^\n]/g, " ")).replace(/(^|[^:"'`\\])\/\/[^\n]*/g, (m, p) => p + " ".repeat(m.length - p.length));
  const libFiles = fs.readdirSync(path.join(ROOT, "lib")).filter(f => f.endsWith(".js")).map(f => "lib/" + f)
    .concat(fs.readdirSync(path.join(ROOT, "lib", "routes")).filter(f => f.endsWith(".js")).map(f => "lib/routes/" + f));

  console.log("▸ LAW-010 · RUNTIME RESPONSIBILITY — a domain writes only the truth it owns");
  {
    const dm = require(path.join(ROOT, "scripts", "domain-map.js")).map();
    const tOwn = dm.kinds.tables.owned, fOwn = dm.kinds.files.owned;
    const cross = [];
    for (const f of Object.keys(fOwn).filter(f => f.endsWith(".js"))) {
      const src = stripComments(fs.readFileSync(path.join(ROOT, f), "utf8"));
      for (const m of src.matchAll(/\b(?:INSERT(?:\s+OR\s+\w+)?\s+INTO|UPDATE|DELETE\s+FROM)\s+"?([a-z_][a-z0-9_]*)"?/gi)) {
        const o = tOwn[m[1]]; if (o && o !== fOwn[f]) cross.push(f + " (" + fOwn[f] + ") writes " + m[1] + " (" + o + ")");
      }
    }
    ratchet("crossDomainWrites", cross.length, "statements in one domain's code that write another domain's table", cross.slice(0, 10));
  }

  console.log("▸ LAW-014 · INFINITE EXTENSIBILITY — no country, currency, calendar or direction is assumed");
  {
    const cc = new Set(db.all("SELECT code FROM countries").map(r => r.code)), cur = new Set(db.all("SELECT code FROM currencies").map(r => r.code));
    const EARTH = new Set(["gregorian", "ltr", "rtl", "en-US", "en_US"]);
    const hits = [];
    for (const f of libFiles) {
      const src = stripComments(fs.readFileSync(path.join(ROOT, f), "utf8"));
      for (const m of src.matchAll(/["'`]([A-Za-z_-]{2,9})["'`]/g)) { const v = m[1]; if (cur.has(v) || (cc.has(v) && v.length === 2 && v === v.toUpperCase()) || EARTH.has(v)) hits.push(f + " " + v); }
    }
    ratchet("earthLiterals", hits.length, "literal countries, currencies, calendars and directions in platform code", hits.slice(0, 10));
  }

  console.log("▸ LAW-018 · SELECTION FROM OWNERS — every choice is read from the domain that owns it");
  {
    const E = JSON.parse(fs.readFileSync(path.join(ROOT, "lib", "seed", "entity.json"), "utf8"));
    const defs = E.ENTITY_DEFS || E.defs || E;
    const inline = [];
    for (const [k, d] of Object.entries(defs)) for (const f of (d && d.fields) || []) if (Array.isArray(f.options) && f.options.length) inline.push(k + "." + f.key);
    const js = path.join(ROOT, "public", "js");
    const consoles = ["admin.js", "platform.js"].map(f => path.join(js, f)).concat(fs.existsSync(path.join(js, "admin")) ? fs.readdirSync(path.join(js, "admin")).filter(f => f.endsWith(".js")).map(f => path.join(js, "admin", f)) : []);
    let tags = 0; for (const f of consoles) tags += (fs.readFileSync(f, "utf8").match(/<option value="[a-z_]*">/g) || []).length;
    ratchet("inlineChoices", inline.length + tags, "choices written in place instead of read from their owner (" + inline.length + " entity fields, " + tags + " console options)", inline.slice(0, 10));
  }

  if (UPDATE) {
    const p = path.join(ROOT, "_registry", "register-baseline.json"), cur = JSON.parse(fs.readFileSync(p, "utf8"));
    cur.lawRatchets = Object.fromEntries(Object.entries(now).map(([k, v]) => [k, Math.min(v, (cur.lawRatchets || {})[k] ?? v)]));
    fs.writeFileSync(p, JSON.stringify(cur, null, 2) + "\n"); console.log("  law ratchets written: " + JSON.stringify(cur.lawRatchets));
  }

  console.log("▸ LAW-026 · EVERY ENFORCED LAW NAMES ITS CHECK");
  {
    const laws = JSON.parse(fs.readFileSync(path.join(ROOT, "_registry", "domains.json"), "utf8")).laws;
    const here = fs.readFileSync(__filename, "utf8");
    const claimed = laws.filter(l => (l.enforcedBy || []).some(e => /test\/laws\.js/.test(e)));
    ok(claimed.every(l => here.includes("▸ " + l.lawId + " ")), "every law that names test/laws.js has its section here", claimed.filter(l => !here.includes("▸ " + l.lawId + " ")).map(l => l.lawId));
    ok(laws.filter(l => l.status === "enforced").every(l => (l.enforcedBy || []).length > 0), "no law is marked enforced without a check");
  }

  cleanup();
  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); cleanup(); process.exit(1); });
