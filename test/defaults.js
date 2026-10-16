/* LUXORA Platform — defaults are data (lib/defaults.js, lib/seed/defaults.json).
   A value the caller did not give comes from the store (its currency), the platform (its
   default country's currency) or the row a registry flags `default` — never a literal in code.
   Editing the flag changes what every engine falls back to; the gate below fails if an engine
   writes `|| "<a declared default>"` or `|| "<a currency code>"` again. */
"use strict";
const path = require("path");
const fs = require("fs");
const os = require("os");
const TMP = path.join(os.tmpdir(), "defaults-" + process.pid + ".db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
process.env.LX_DB = TMP;
const silence = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = silence;
const reg = require("../lib/registry.js");
const dflt = require("../lib/defaults.js");
const SEED = require("../lib/seed/defaults.json");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const setList = (name, items) => db.run("UPDATE meta_lists SET items=? WHERE name=?", JSON.stringify(items), name);
const getList = name => JSON.parse(db.get("SELECT items FROM meta_lists WHERE name=?", name).items);

try {
  const tid = db.get("SELECT id FROM tenants ORDER BY id LIMIT 1").id;

  console.log("▸ EVERY DECLARED LIST FLAGS ITS DEFAULT ROW");
  const unflagged = [];
  for (const [list, key] of Object.entries(SEED.lists)) {
    const rows = reg.list(list);
    if (!Array.isArray(rows) || !rows.length) { unflagged.push(list + " (missing)"); continue; }
    const objs = rows.filter(r => r && typeof r === "object");
    if (objs.length && objs.filter(r => r.default).length !== 1) unflagged.push(list);
    if (dflt.of(list) !== key) unflagged.push(list + " → " + dflt.of(list));
  }
  ok(unflagged.length === 0, "each list in lib/seed/defaults.json has one flagged row, the declared one (" + Object.keys(SEED.lists).length + " lists)", unflagged);

  console.log("▸ MOVING THE FLAG MOVES THE DEFAULT");
  const chans = getList("offerChannels");
  const other = chans.find(c => !c.default).key;
  setList("offerChannels", chans.map(c => ({ ...c, default: c.key === other })));
  ok(dflt.of("offerChannels") === other, "flagging another channel makes it the default", dflt.of("offerChannels"));
  const offers = require("../lib/offers.js");
  offers.credit(tid, "t:defaults-test", 5, "deposit", "dflt-1");
  const e1 = db.get("SELECT channel, currency FROM wallet_entries WHERE tenant_id=? AND owner=? ORDER BY id DESC LIMIT 1", tid, "t:defaults-test");
  ok(e1 && e1.channel === other, "a wallet credit with no channel takes the flagged default", e1);
  setList("offerChannels", chans);

  console.log("▸ CURRENCY COMES FROM THE STORE, THEN THE PLATFORM");
  const settings = require("../lib/settings.js"), glob = require("../lib/global.js");
  const country = reg.country(settings.load(tid).commerce.country);
  ok(dflt.currency(tid) === country.currency || dflt.currency(tid) === String(settings.load(tid).commerce.currency || "").toUpperCase(), "a store's default currency is its own (its setting, else its country's)", dflt.currency(tid));
  ok(e1 && e1.currency === dflt.currency(tid), "a wallet credit with no currency is in the store's currency", e1);
  const before = dflt.currency(tid);
  const alt = db.get("SELECT code FROM currencies WHERE code<>? ORDER BY position LIMIT 1", before).code;
  glob.setTenantCurrency(tid, alt);
  offers.credit(tid, "t:defaults-test", 5, "deposit", "dflt-2");
  ok(db.get("SELECT currency FROM wallet_entries WHERE tenant_id=? AND owner=? ORDER BY id DESC LIMIT 1", tid, "t:defaults-test").currency === alt && glob.getTenantCurrency(tid) === alt, "set the store's currency and the default follows: " + alt);
  glob.setTenantCurrency(tid, before);
  const home = reg.country(require("../lib/security.js").defaultCountry());
  ok(dflt.currency(null) === home.currency && dflt.currency(999999) === home.currency, "with no store, the platform's default country decides: " + home.currency);
  ok(dflt.all().currency === home.currency && Object.keys(dflt.all().lists).length === Object.keys(SEED.lists).length, "the consoles are served every default");

  console.log("▸ THE GATE: NO LITERAL FALLBACK TO A DECLARED DEFAULT OR A CURRENCY");
  /* where a fallback literal is not the registry value it spells: the boot seeder (it runs
     before the registries exist) and the affiliate module's own tier, which has no registry
     and only shares its spelling with the tax class "standard" */
  const EXEMPT = { "db.js": ["physical"], "affiliate.js": ["standard"], "api.js": ["standard"] };
  const keys = new Set(Object.values(SEED.lists));
  const codes = new Set(db.all("SELECT code FROM currencies").map(r => r.code));
  const hits = [];
  const LIB = path.join(__dirname, "..", "lib");
  for (const f of fs.readdirSync(LIB).filter(f => f.endsWith(".js"))) {
    const src = fs.readFileSync(path.join(LIB, f), "utf8").replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/[^\n]*/g, "");
    const re = /(?:\|\||\?\?)\s*\(?\s*["']([A-Za-z_]+)["']/g; let m;
    while ((m = re.exec(src))) {
      const v = m[1];
      if ((keys.has(v) || codes.has(v)) && !(EXEMPT[f] || []).includes(v)) hits.push(f + ": || \"" + v + "\"");
    }
  }
  ok(hits.length === 0, "no engine falls back to a literal declared default or currency code", [...new Set(hits)]);
} catch (e) { failed++; console.log("  ✗ threw: " + (e && e.stack || e)); }
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
