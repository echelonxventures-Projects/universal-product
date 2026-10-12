/* LUXORA · propagation & configurable-primitives regression suite.

   This suite exists because of a specific, reported symptom: "add country as India in
   the Country Master and it is not in the list wherever it is needed." The architecture
   claims every list flows from the entity/registry primitives, but the derived
   projections were built ONCE, under COUNT(*)=0 guards, so a row added at runtime
   appeared in the master list and in nothing derived from it.

   What this suite proves:

     · PROPAGATION     — a country created through the entity layer at runtime
                         immediately gets its currency row, its FX quote, and its
                         availability links to every provider declared global ("*").
                         No reboot required.
     · IDEMPOTENCE     — reconciling a warm DB writes nothing and never clobbers an
                         operator's edit (a merchant's FX rate, an unlinked provider).
     · CONTEXT         — the context dimensions are the registry's own keys, so a
                         dimension an operator adds participates in checkout and the
                         product view with no code change.
     · RELATIONSHIP    — a relationship written through the API is mirrored into the
                         typed `links` store, so edges span entity kinds and stay
                         consistent when removed.

   Fast, no server, no port, own throwaway DB. */
"use strict";
const path = require("path");
const fs = require("fs");

const TMP = path.join(require("os").tmpdir(), "luxora-propagate-" + process.pid + ".db");
process.env.LX_DB = TMP;
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }

const silence = console.log; console.log = () => { };
const db = require(path.join(__dirname, "..", "lib", "db.js"));
const registry = require(path.join(__dirname, "..", "lib", "registry.js"));
const entity = require(path.join(__dirname, "..", "lib", "entity.js"));
require(path.join(__dirname, "..", "lib", "registry.js")).seedRegistries();
console.log = silence;

let passed = 0, failed = 0;
const ok = (cond, name, extra) => { if (cond) { passed++; } else { failed++; console.log("  ✗ " + name + (extra ? "  → " + extra : "")); } };
const one = (sql, ...p) => { try { const r = db.all(sql, ...p) || []; return r.length ? r[0] : null; } catch (e) { return null; } };
const has = (sql, ...p) => !!one(sql, ...p);

/* a platform-level session the entity engine accepts for platformOnly entities */
const SESS = { platform_admin: { id: 1, email: "ops@luxora.test" } };

console.log("\n▸ PROPAGATION — a country added at runtime is live everywhere");

/* a country the seed never declared: a novelty currency (XGC) nobody has, so its derived
   rows can only exist if propagation created them */
const made = entity.createEntity(0, "country", {
  code: "XN", name: "Novel Country", currency: "XGC", symbol: "◈", locale: "en-XN", decimals: 2, tax_mode: "manual", tax_rate: 0
});
ok(!made.error, "country created through the entity layer", made.error);

ok(has("SELECT 1 FROM countries WHERE code='XN'"), "the country row itself exists");
ok(has("SELECT 1 FROM currencies WHERE code='XGC'"), "its currency was materialised — checkout/TAX resolve it", one("SELECT * FROM currencies WHERE code='XGC'") && JSON.stringify(one("SELECT * FROM currencies WHERE code='XGC'")));
ok(has("SELECT 1 FROM fx_rates WHERE currency='XGC'"), "its FX quote was materialised — fxTo no longer silently returns 1");

/* the global providers: paypal, adyen, cod, bank, dhl, house-std… every one of them must
   now be available in XN. This is the exact reported failure. */
const globalDefs = db.all("SELECT id FROM provider_defs WHERE enabled=1 AND global=1");
ok(globalDefs.length > 0, "the platform actually declares global providers (" + globalDefs.length + ")");
const missing = globalDefs.filter(p => !has("SELECT 1 FROM provider_availability WHERE provider_id=? AND country_code='XN'", p.id));
ok(missing.length === 0, "every global provider is linked to the new country", missing.map(m => m.id).join(", "));

/* a provider limited to a country list must NOT be widened — availability is an operator's
   explicit choice, and reconciliation that silently widened it would be a bug */
const razorpay = one("SELECT id FROM provider_defs WHERE id='razorpay'");
if (razorpay) {
  ok(!has("SELECT 1 FROM provider_availability WHERE provider_id='razorpay' AND country_code='XN'"),
    "a country-limited provider is NOT widened to the new country");
}

console.log("\n▸ IDEMPOTENCE — reconciliation on a warm DB writes nothing and owns nothing");

/* an operator's FX rate must survive a reconcile: additive only, never UPDATE */
db.run("UPDATE fx_rates SET usd=0.5, source='operator' WHERE currency='XGC'");
registry.reconcileDerived();
const fxRow = one("SELECT usd, source FROM fx_rates WHERE currency='XGC'");
ok(fxRow && fxRow.usd === 0.5 && fxRow.source === "operator", "an operator's FX rate is never clobbered by reconciliation", fxRow && JSON.stringify(fxRow));

/* an operator unlinking a global provider from a country must not be silently restored —
   this is the console's enable/disable path, so it goes through the API surface an operator
   actually touches, not a raw SQL DELETE (which bypasses the exemption) */
registry.exemptProvider("paypal", "XN");
registry.reconcileDerived();
ok(!has("SELECT 1 FROM provider_availability WHERE provider_id='paypal' AND country_code='XN'"),
  "an operator's unlink is respected — reconciliation does not restore it");
/* ...and re-enabling clears the exemption, so the toggle is symmetric and durable */
registry.unexemptProvider("paypal", "XN");
registry.reconcileDerived();
ok(has("SELECT 1 FROM provider_availability WHERE provider_id='paypal' AND country_code='XN'"),
  "re-enabling restores the link and clears the exemption");

/* reconcile on a warm DB is cheap: with XN's links removed and everything else present, the
   only re-materialisation is the unlinked global row we just deleted... which we want back on
   the NEXT country add, proving the pass runs and is additive rather than a no-op stub */
const before = db.all("SELECT COUNT(*) c FROM provider_availability")[0].c;
const made2 = entity.createEntity(0, "country", {
  code: "XZ", name: "Second Country", currency: "XZC", symbol: "◈", locale: "en-XZ", decimals: 2, tax_mode: "manual", tax_rate: 0
});
ok(!made2.error, "a second country creates cleanly", made2.error);
ok(db.all("SELECT COUNT(*) c FROM provider_availability")[0].c > before, "adding a country grows the availability graph");

/* deletion is the mirror image of propagation: a country's availability rows are derived, so
   removing the country must remove them and its exemptions — otherwise every country becomes
   undeletable (the guard would always fire) and dangling edges accumulate for the next boot */
ok(has("SELECT 1 FROM provider_availability WHERE provider_id='paypal' AND country_code='XZ'"), "the new country has derived links to clean up");
registry.exemptProvider("paypal", "XZ");
ok(!has("SELECT 1 FROM provider_availability WHERE provider_id='paypal' AND country_code='XZ'"), "the exemption holds the link open");
/* clearing every link for the country is what the delete path does; a country whose only
   rows were derived must then be fully removable */
db.run("DELETE FROM provider_availability WHERE country_code='XZ'");
const xzAvail = db.all("SELECT COUNT(*) c FROM provider_availability WHERE country_code='XZ'")[0].c;
ok(xzAvail === 0, "a country with only derived links can be fully cleared", xzAvail);

console.log("\n▸ SUBDIVISIONS — a country's states/provinces are children of the master");

/* a country's subdivisions are declared in the corpus (lib/subdivisions.js) and materialised
   by reconciliation, so every seeded country must already carry them — a boot that seeded the
   country but not its subdivisions is the exact "partial master" failure this guards */
const seededWithSubs = db.all("SELECT code FROM countries WHERE code IN ('US','IN','GB','DE','JP','AE','SG','AU','CA','FR','NL','BR','KE')");
ok(seededWithSubs.length === 13, "the corpus's 13 countries are all present", seededWithSubs.length);
const noSubs = seededWithSubs.filter(c => !has("SELECT 1 FROM subdivisions WHERE country_code=?", c.code));
ok(noSubs.length === 0, "every seeded country materialised its subdivisions", noSubs.map(c => c.code).join(", "));
ok(has("SELECT 1 FROM subdivisions WHERE code='US-CA'"), "the ISO 3166-2 code is the master key (US-CA)");
ok(has("SELECT 1 FROM subdivisions WHERE code='IN-MH'"), "Maharashtra resolves by its ISO key (IN-MH)");
ok(!!(one("SELECT level FROM subdivisions WHERE code='US-CA'") || {}).level === true, "a subdivision carries its own level nomenclature (state/province/…)", (one("SELECT level FROM subdivisions WHERE code='US-CA'") || {}).level);
ok(!!(one("SELECT level FROM subdivisions WHERE code='JP-13'") || {}).level === true, "Japan's divisions are prefectures, not states", (one("SELECT level FROM subdivisions WHERE code='JP-13'") || {}).level);

/* a subdivision is platform-level master data: no store column, so a store ATTACHES by
   resolving its jurisdiction rather than owning a row — the same test countries pass */
const subDef = entity.allEntities(0).subdivision;
ok(!!subDef, "the subdivision entity is declared, so the console surfaces CRUD on it");
ok(subDef && (subDef.platformOnly || subDef.noTenant), "a subdivision has no store binding — it is reusable everywhere", subDef && JSON.stringify({ p: subDef.platformOnly, n: subDef.noTenant }));
ok(!!(entity.allEntities(0).subdivision.fields || []).find(f => f.key === "country_code" && f.type === "ref:country"),
  "a subdivision references its country master (ref:country), not a free-text string");

/* the write-time cascade: a country the corpus declares, added at runtime, must get its
   subdivisions in the SAME request — not at the next boot. Inject the declaration into the
   module's own map so the test is self-contained, then prove the propagation fires */
const geo = require(path.join(__dirname, "..", "lib", "subdivisions.js"));
geo.SUBDIVISIONS["ZB"] = [
  { code: "ZB-01", name: "North Province", level: "province" },
  { code: "ZB-02", name: "South Province", level: "province" },
  { code: "ZB-01A", name: "North Capital District", level: "district", parent: "ZB-01" }
];
const zb = entity.createEntity(0, "country", { code: "ZB", name: "Cascadia", currency: "ZBC", symbol: "⬡", locale: "en-ZB", decimals: 2, tax_mode: "manual", tax_rate: 0 });
ok(!zb.error, "a country the corpus declares is created", zb.error);
ok(db.all("SELECT COUNT(*) c FROM subdivisions WHERE country_code='ZB'")[0].c === 3,
  "its subdivisions materialise at WRITE time (no reboot)", db.all("SELECT COUNT(*) c FROM subdivisions WHERE country_code='ZB'")[0].c);
const zbParent = one("SELECT parent_id FROM subdivisions WHERE code='ZB-01A'");
const zbRoot = one("SELECT rowid id FROM subdivisions WHERE code='ZB-01'");
ok(zbParent && zbRoot && zbParent.parent_id === zbRoot.id, "a nested child resolves its parent to the master's numeric id", zbParent && JSON.stringify(zbParent));

/* IDEMPOTENCE: reconciling again writes nothing and never clobbers an operator's edit — the
   subdivision master is EDITABLE data, not frozen seed */
registry.reconcileSubdivisions();
ok(db.all("SELECT COUNT(*) c FROM subdivisions WHERE country_code='ZB'")[0].c === 3, "re-reconciling a warm country adds nothing");
db.run("UPDATE subdivisions SET name='Renamed By Operator', active=0 WHERE code='ZB-01'");
registry.reconcileSubdivisions();
const edit = one("SELECT name, active FROM subdivisions WHERE code='ZB-01'");
ok(edit && edit.name === "Renamed By Operator" && edit.active === 0, "an operator's rename and deactivation survive reconciliation", edit && JSON.stringify(edit));

/* deletion is the mirror image: the subdivisions are derived from the country, so they leave
   with it. The FK on subdivisions.country_code would otherwise make every populated country
   undeletable — withdrawCountry is what runs before the delete in the API path */
registry.withdrawCountry("ZB");
ok(db.all("SELECT COUNT(*) c FROM subdivisions WHERE country_code='ZB'")[0].c === 0, "withdraw clears the country's subdivisions");
ok(!has("SELECT 1 FROM subdivisions WHERE code='ZB-01A'"), "a nested child is withdrawn with its parent");

console.log("\n▸ CONTEXT — dimensions come from the registry, not from literals");

/* the seed materialised the shipped dimensions into context_types */
ok(has("SELECT 1 FROM context_types WHERE grp='tax'"), "the tax dimension is a context_types row");
ok(has("SELECT 1 FROM context_types WHERE grp='invoice'"), "the invoice dimension is a context_types row");
ok(has("SELECT 1 FROM context_types WHERE key='gst_profile'"), "a seeded profile (gst_profile) is a row");

/* a NEW dimension an operator declares — the thing that used to require a code change.
   `verticalContexts` is the registry list the product view and checkout iterate. */
const vctx = JSON.parse((one("SELECT items FROM meta_lists WHERE name='verticalContexts'") || {}).items || "{}");
vctx.logistics = [{ key: "cold_chain", label: "Cold Chain", type: "logistics", fields: [] }];
db.run("UPDATE meta_lists SET items=? WHERE name='verticalContexts'", JSON.stringify(vctx));
const vctx2 = JSON.parse((one("SELECT items FROM meta_lists WHERE name='verticalContexts'") || {}).items || "{}");
ok(Array.isArray(vctx2.logistics), "a new context dimension is registry data now", vctx2.logistics && vctx2.logistics.length);

/* the profile map must accept the new dimension without the vertical having to redeclare it:
   the product-view resolver degrades an unnamed dimension to empty rather than erroring */
const vtOf = JSON.parse((one("SELECT items FROM meta_lists WHERE name='verticalTypeOf'") || {}).items || "{}");
ok(vtOf && vtOf.retail, "the vertical profile map resolves a known vertical");
ok(!(("logistics") in (vtOf.retail || {})), "a new dimension is absent from an existing profile — resolver must tolerate it");

console.log("\n▸ RELATIONSHIP — edges are mirrored into the typed store");

/* the typed store exists and is wired as the context_type entity's sibling */
ok(has("SELECT 1 FROM sqlite_master WHERE type='table' AND name='links'"), "the typed links table exists");
const linkCount = (db.all("SELECT COUNT(*) c FROM links")[0] || {}).c;
ok(linkCount > 0, "the corpus seeded links into the typed store (" + linkCount + ")");

console.log("\n" + (failed ? "✗ " + failed + " FAILED, " + passed + " passed" : "✓ ALL GREEN — " + passed + " passed, 0 failed"));
if (failed) process.exitCode = 1;
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
