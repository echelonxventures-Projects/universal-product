/* LUXORA Platform — the country and currency master is real geography (international item 1).
   The country seed is data (lib/seed/providers.json COUNTRIES): code, name, currency, symbol,
   locale. A country's decimals are its currency's. A provider is linked only to declared
   countries — boot no longer invents "SE (auto-registered)" with currency "SE" — and an install
   that has such rows is repaired from the seed. A country the seed gains reaches an existing
   install once, switched off. Every write of a country or currency is checked by the field
   declarations on its entity (pattern, format, bounds). A country naming a currency nobody
   has still creates it, with its FX row (test/propagate.js). */
"use strict";
const path = require("path");
const fs = require("fs");
const os = require("os");
const TMP = path.join(os.tmpdir(), "geo-" + process.pid + ".db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
process.env.LX_DB = TMP;
const silence = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = silence;
const providers = require("../lib/providers.js");
const registry = require("../lib/registry.js");
const globalmod = require("../lib/global.js");
const entity = require("../lib/entity.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
/* removes a country the way an operator's delete does: every row that references it first */
const dropCountry = cc => {
  for (const t of db.all("SELECT name FROM sqlite_master WHERE type='table'").map(r => r.name))
    for (const fk of db.all(`PRAGMA foreign_key_list("${t}")`)) if (fk.table === "countries") db.run(`DELETE FROM "${t}" WHERE "${fk.from}"=?`, cc);
  db.run("DELETE FROM countries WHERE code=?", cc);
};
const canonical = l => { try { return Intl.getCanonicalLocales(l)[0] === l; } catch (e) { return false; } };

try {
  console.log("▸ THE SEED IS REAL GEOGRAPHY");
  const C = providers.COUNTRIES, cur = new Map(providers.CURRENCIES.map(c => [c.code, c]));
  ok(Array.isArray(C) && C.length >= 40 && new Set(C.map(c => c.code)).size === C.length, "the country seed is data with unique codes (" + C.length + ")");
  ok(C.every(c => /^[A-Z]{2}$/.test(c.code) && c.name && c.symbol), "every code is ISO 3166-1 alpha-2 and every country has a name and symbol", C.filter(c => !/^[A-Z]{2}$/.test(c.code) || !c.name || !c.symbol));
  ok(C.every(c => cur.has(c.currency)), "every country's currency is a declared currency", C.filter(c => !cur.has(c.currency)).map(c => c.code));
  ok(C.every(c => canonical(c.locale)), "every locale is a canonical BCP 47 tag", C.filter(c => !canonical(c.locale)).map(c => c.code + ":" + c.locale));
  ok(providers.CURRENCIES.every(c => /^[A-Z]{3}$/.test(c.code) && c.usd > 0 && c.decimals >= 0 && c.decimals <= 4), "every currency is ISO 4217 with a rate and minor units");
  const declared = new Set(C.map(c => c.code)), undeclared = [];
  for (const p of providers.PAYMENT_PROVIDERS.concat(providers.SHIPPING_PROVIDERS, providers.NOTIFICATION_PROVIDERS, providers.MARKETING_PROVIDERS))
    for (const cc of p.countries || []) if (cc !== "*" && !declared.has(cc)) undeclared.push(p.id + ":" + cc);
  ok(undeclared.length === 0, "every country a provider names is a declared country", undeclared);

  console.log("▸ A FRESH INSTALL");
  ok(db.get("SELECT COUNT(*) n FROM countries").n === C.length, "boot seeds every declared country");
  ok(!db.get("SELECT 1 ok FROM countries WHERE name LIKE '%auto-registered%'") && !db.get("SELECT 1 ok FROM currencies WHERE length(code)<>3"), "no invented country or currency");
  const wrongDec = db.all("SELECT c.code, c.decimals, k.decimals kd FROM countries c JOIN currencies k ON k.code=c.currency WHERE c.decimals<>k.decimals");
  ok(wrongDec.length === 0, "a country's decimals are its currency's", wrongDec);
  ok(db.get("SELECT COUNT(*) n FROM provider_availability pa LEFT JOIN countries c ON c.code=pa.country_code WHERE c.code IS NULL").n === 0, "every provider link points at a declared country");

  console.log("▸ AN EXISTING INSTALL IS REPAIRED FROM THE SEED");
  const sample = C.find(c => c.currency !== c.code && !C.some(x => x.currency === c.code));
  dropCountry(sample.code);
  db.run("INSERT OR IGNORE INTO currencies(code,name,symbol,decimals,usd,position) VALUES(?,?,?,2,1,100)", sample.code, sample.code, sample.code + " ");
  db.run("INSERT INTO countries(code,name,currency,symbol,locale,decimals,position) VALUES(?,?,?,?,?,2,100)", sample.code, sample.code + " (auto-registered)", sample.code, sample.code + " ", "en-" + sample.code);
  db.run("INSERT OR IGNORE INTO fx_rates(currency,usd,source,note) VALUES(?,1,'derived','x')", sample.code);
  registry.repairCountries();
  const fixed = db.get("SELECT * FROM countries WHERE code=?", sample.code);
  ok(fixed.name === sample.name && fixed.currency === sample.currency && fixed.locale === sample.locale, "an auto-registered row takes the seed's geography: " + sample.code + " → " + fixed.name + ", " + fixed.currency);
  ok(!db.get("SELECT 1 ok FROM currencies WHERE code=?", sample.code) && !db.get("SELECT 1 ok FROM fx_rates WHERE currency=?", sample.code), "the invented currency and its rate are gone");
  const opName = "Operator-named " + sample.code;
  ok(globalmod.updateCountry(sample.code, { name: opName }).ok, "an operator renames the repaired country");
  registry.repairCountries();
  ok(db.get("SELECT name FROM countries WHERE code=?", sample.code).name === opName, "a row an operator named is never touched");

  console.log("▸ A COUNTRY THE SEED GAINS ARRIVES ONCE, SWITCHED OFF");
  const gained = C[C.length - 1];
  dropCountry(gained.code);
  const seen = JSON.parse(db.get("SELECT value v FROM platform_settings WHERE key='seed_countries_seen'").v).filter(c => c !== gained.code);
  db.run("UPDATE platform_settings SET value=? WHERE key='seed_countries_seen'", JSON.stringify(seen));
  registry.repairCountries();
  const arrived = db.get("SELECT * FROM countries WHERE code=?", gained.code);
  ok(arrived && arrived.active === 0 && arrived.currency === gained.currency, "a newly declared country is added inactive: " + gained.code);
  dropCountry(gained.code);
  registry.repairCountries();
  ok(!db.get("SELECT 1 ok FROM countries WHERE code=?", gained.code), "a country the operator deleted is not added back");

  console.log("▸ EVERY WRITE IS CHECKED BY THE ENTITY'S DECLARATIONS");
  const good = { code: "QZ", name: "Testland", currency: "EUR", symbol: "€", locale: "en-IE" };
  ok(!globalmod.createCountry({ ...good, currency: "EURO" }).ok, "a currency code that is not three letters is refused");
  ok(!globalmod.createCountry({ ...good, code: "Q1" }).ok, "a code that is not two letters is refused");
  ok(!globalmod.createCountry({ ...good, locale: "not a locale!" }).ok, "a locale that is not BCP 47 is refused");
  ok(!globalmod.createCountry({ ...good, name: "" }).ok, "a country with no name is refused");
  const made = globalmod.createCountry({ ...good, code: "qz" });
  ok(made.ok && db.get("SELECT code FROM countries WHERE code='QZ'"), "a valid country is created (code upper-cased)", made);
  ok(globalmod.createCountry({ ...good, code: "QY", currency: "JPY", symbol: "¥", locale: "ja-JP" }).ok && db.get("SELECT decimals d FROM countries WHERE code='QY'").d === 0, "a new country takes its currency's decimals (JPY: 0)");
  ok(!globalmod.updateCountry("QZ", { locale: "??" }).ok && globalmod.updateCountry("QZ", { name: "Testland II" }).ok, "a partial update is checked on the fields it sends");
  ok(!globalmod.createCurrency({ code: "QZ", name: "Q", symbol: "q", decimals: 2, usd: 1 }).ok, "a currency code that is not three letters is refused");
  ok(!globalmod.createCurrency({ code: "QZQ", name: "Q", symbol: "q", decimals: 2, usd: 0 }).ok, "a currency with no value is refused");
  ok(!globalmod.createCurrency({ code: "QZQ", name: "Q", symbol: "q", decimals: 9, usd: 1 }).ok, "minor units outside 0–4 are refused");
  const pv = db.get("SELECT id, kind FROM provider_defs ORDER BY position LIMIT 1"), pl = db.get("SELECT id FROM plans ORDER BY id LIMIT 1");
  ok(globalmod.updateProvider(pv.id, pv.kind, { position: 7 }).ok && (!pl || globalmod.updatePlan(pl.id, { position: 3 }).ok), "provider and plan edits write (they stamped a column the tables do not have)");
  ok(entity.validate(entity.ENTITY_DEFS.country, { ...good, locale: "not a locale!" }).length > 0, "Data Studio's entity path runs the same check");

  console.log("▸ THE STOREFRONT AND THE API");
  const api = fs.readFileSync(path.join(__dirname, "..", "lib", "api.js"), "utf8");
  ok(/geo: \{ countries: registry\.countries\(\)\.filter\(c => c\.active !== 0\)/.test(api), "the storefront is served active countries only");
  ok(["apiGlobalCountryPut", "apiGlobalCurrencyPut"].every(f => new RegExp("function " + f + "\\([^)]*\\) \\{ if \\(!requirePlatformSection\\(s, res, \"geo\", \"write\"\\)\\)").test(api)), "editing a country or currency needs the geo write permission, as creating one does");
} catch (e) { failed++; console.log("  ✗ threw: " + (e && e.stack || e)); }
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
