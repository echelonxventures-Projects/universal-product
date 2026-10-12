/* LUXORA · tax single-source-of-truth regression suite.

   This suite exists because of a specific architectural smell: "Why are Default Tax Mode and
   Default Tax Rate on the New Country form, when Tax is an individual complete thing?"

   The answer was that they were leftovers from before the tax engine existed. A country master
   carried tax_mode/tax_rate, and the tax engine ALSO kept its own per-country taxRules registry
   — so one fact lived in two places. This suite proves that is no longer true, by checking the
   failure that used to happen:

     · DRIFT        — editing the tax master moved ONE rate and three surfaces disagreed
                       (legacy checkout read the country row, quote() read the registry,
                       billing read the country row again). Editing tax_rules must move every
                       consumer at once, because there is no second copy.
     · COMPLETENESS — every country the corpus seeds has a rule in the engine, so nothing is
                       resolved by falling back into another table (six countries used to have
                       no rule and silently inherited the country row).
     · OWNERSHIP    — the country master is geography: its entity declares no tax fields, so the
                       console cannot ask an operator for a tax rate while creating a country.
                       Tax is configured in the tax engine, by data.
     · CONFIGURABLE — the jurisdiction rate is a first-class entity (tax_rule) an operator
                       edits in the console, never code and never a JSON blob.

   Fast, no server, no port, own throwaway DB. */
"use strict";
const path = require("path");
const fs = require("fs");

const TMP = path.join(require("os").tmpdir(), "luxora-tax-" + process.pid + ".db");
process.env.LX_DB = TMP;
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }

const silence = console.log; console.log = () => { };
const db = require(path.join(__dirname, "..", "lib", "db.js"));
require(path.join(__dirname, "..", "lib", "registry.js")).seedRegistries();
console.log = silence;

const tax = require(path.join(__dirname, "..", "lib", "tax.js"));
const entity = require(path.join(__dirname, "..", "lib", "entity.js"));

let passed = 0, failed = 0;
const ok = (cond, name, extra) => { if (cond) { passed++; } else { failed++; console.log("  ✗ " + name + (extra ? "  → " + extra : "")); } };
const one = (sql, ...p) => { try { const r = db.all(sql, ...p) || []; return r.length ? r[0] : null; } catch (e) { return null; } };
const has = (sql, ...p) => !!one(sql, ...p);

console.log("\n▸ COMPLETENESS — every seeded country has a rule in the tax engine");

const seeded = db.all("SELECT code FROM countries WHERE code IN ('US','IN','GB','DE','FR','NL','BR','KE','AE','JP','SG','AU','CA')").map(r => r.code);
ok(seeded.length === 13, "the corpus's 13 countries are all present", seeded.length);
/* the six that used to be orphaned — no rule in the engine, silently resolved by the country row */
for (const cc of ["BR", "KE", "JP", "SG", "AU", "CA"]) {
  ok(has("SELECT 1 FROM tax_rules WHERE country=?", cc), cc + " has a rule in the engine (was previously orphaned)");
  const d = tax.defaultRateFor(cc);
  ok(d.mode !== "manual" || d.rate > 0, "  " + cc + " resolves a real rate, not a silent zero fallback", JSON.stringify(d));
}
/* nothing resolves through another table: every seeded country's default comes from tax_rules */
const noRule = seeded.filter(cc => !has("SELECT 1 FROM tax_rules WHERE country=?", cc));
ok(noRule.length === 0, "no seeded country is resolved by a fallback into another table", noRule.join(", "));

console.log("\n▸ DRIFT — one edit moves every consumer, because there is no second copy");

/* the country master used to carry this fact; verify it no longer does, so the two cannot
   disagree. The columns remain for compatibility with warm databases, but nothing authoritative
   reads them */
const cDef = entity.allEntities(0).country;
ok(!cDef.fields.some(f => f.key === "tax_mode" || f.key === "tax_rate"),
  "the country entity declares no tax fields — the New Country form cannot ask for a rate",
  cDef.fields.map(f => f.key).join(","));
/* the store's unconfigured tax resolves from the ENGINE, not the country row. Set the country
   row's rate to something unmistakable and confirm no tax consumer picks it up */
db.run("UPDATE countries SET tax_rate=0.99, tax_mode='gst' WHERE code='US'");
const dflt = tax.defaultRateFor("US");
ok(dflt.rate !== 0.99, "defaultRateFor ignores the country row's stale rate", JSON.stringify(dflt));
ok(dflt.mode === (one("SELECT mode FROM tax_rules WHERE country='US'") || {}).mode, "the mode comes from the engine's rule", JSON.stringify(dflt));
/* editing the ONE master moves every reader: quote, the default resolver, the config surface */
db.run("UPDATE tax_rules SET standard=0.0444 WHERE country='US'");
ok(tax.quote({ tenantId: 1, lines: [{ id: "x", class: "standard", amount: 100 }] }).tax === 4.44,
  "quote() follows the edited rate", tax.quote({ tenantId: 1, lines: [{ id: "x", class: "standard", amount: 100 }] }).tax);
ok(tax.defaultRateFor("US").rate === 0.0444, "defaultRateFor follows the edited rate", tax.defaultRateFor("US").rate);
ok((tax.configFor(1).rule || {}).standard === 0.0444, "configFor follows the edited rate", (tax.configFor(1).rule || {}).standard);
/* the class system still resolves against the same rule: reduced/digital/zero are data on it */
db.run("UPDATE tax_rules SET reduced=0.01, digital=0.02 WHERE country='US'");
const cls = tax.quote({ tenantId: 1, lines: [{ id: "a", class: "reduced", amount: 100 }, { id: "b", class: "digital", amount: 100 }, { id: "c", class: "zero", amount: 100 }] });
ok(cls.lines.length === 3 && cls.lines.every(l => l.rate === (l.class === "reduced" ? 0.01 : l.class === "digital" ? 0.02 : 0)),
  "rate classes (reduced/digital/zero) resolve from the same rule", cls.lines.map(l => l.class + ":" + l.rate).join(","));

console.log("\n▸ OWNERSHIP — tax is a first-class thing that owns tax");

/* the jurisdiction rate is its own master entity, so an operator configures it in the console
   with typed fields — not by editing a JSON blob or a geography row */
const rDef = entity.allEntities(0).tax_rule;
ok(!!rDef, "the tax_rule entity is declared, so the console surfaces typed CRUD on it");
ok(rDef && (rDef.platformOnly || rDef.noTenant), "a tax rule is platform-level master data, reused by every store", rDef && JSON.stringify({ p: rDef.platformOnly, n: rDef.noTenant }));
ok(rDef && rDef.fields.some(f => f.key === "country" && f.type === "ref:country"),
  "a tax rule references the country master — geography supplies the key, tax supplies the rates",
  rDef && rDef.fields.map(f => f.key).join(","));
/* and the engine reads the entity's table, so a console write IS the engine's source of truth.
   The rule's country must exist first — tax_rules.country REFERENCES countries(code), so a
   jurisdiction's rates key off a real geography row (the honest operator flow: add the country,
   then set its tax) */
ok(!entity.createEntity(0, "country", { code: "IT", name: "Italy", currency: "EUR", symbol: "€", locale: "it-IT", decimals: 2 }).error, "the country exists for the rule to key off");
const made = entity.createEntity(0, "tax_rule", { country: "IT", mode: "vat", standard: 0.22, reduced: 0.1, note: "Italy VAT" });
ok(!made.error, "a rule created through the entity layer is accepted", made.error);
ok((tax.ruleFor("IT") || {}).standard === 0.22, "the engine resolves a rule the console wrote", JSON.stringify(tax.ruleFor("IT")));
ok(tax.defaultRateFor("IT").rate === 0.22, "defaultRateFor resolves it too", JSON.stringify(tax.defaultRateFor("IT")));
/* seeding stays additive: re-seeding never clobbers an operator's rate */
db.run("UPDATE tax_rules SET standard=0.0777 WHERE country='IT'");
tax.seed();
ok((tax.ruleFor("IT") || {}).standard === 0.0777, "re-seeding never overwrites an operator's rate", (tax.ruleFor("IT") || {}).standard);

console.log("\n" + (failed ? "✗ " + failed + " FAILED, " + passed + " passed" : "✓ ALL GREEN — " + passed + " passed, 0 failed"));
if (failed) process.exitCode = 1;
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
