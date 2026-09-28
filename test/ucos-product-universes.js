/* UCOS Ω∞ · product universe vocabulary & the global catalog.
   --------------------------------------------------------------------------
   UPIP §1 VISION declares what the platform shall support — Physical, Digital,
   OTT, Cloud, API, AI, Financial, Quantum, "Future Unknown Product Types"…
   That declaration is the constitution's OWN vocabulary, so it is read from the
   document rather than kept in a JS constant (Knowledge-Once, Article 4.2).

   This proves the whole chain:
     DERIVED      every universe comes from the parse, none from code
     SEEDED       the registry list is the source of truth the console reads
     PRESERVED    an operator's console addition survives a corpus re-parse
     TRANSACTABLE a global product carries its universe, and an unknown one is
                  refused rather than stored as a free string
   Fast, no server, no port, own throwaway DB. */
"use strict";
const path = require("path");
const fs = require("fs");

const TMP = path.join(require("os").tmpdir(), "ucos-pu-" + process.pid + ".db");
process.env.LX_DB = TMP;
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }

const silence = console.log; console.log = () => { };
const db = require(path.join(__dirname, "..", "lib", "db.js"));
const ucos = require(path.join(__dirname, "..", "lib", "ucos.js"));
const registry = require(path.join(__dirname, "..", "lib", "registry.js"));
const api = require(path.join(__dirname, "..", "lib", "api.js"));
ucos.seed(db);
registry.seedRegistries();
console.log = silence;

let passed = 0, failed = 0;
const ok = (cond, name, extra) => { if (cond) { passed++; } else { failed++; console.log("  ✗ " + name + (extra ? "  → " + extra : "")); } };
const list = name => { try { return JSON.parse((db.get("SELECT items i FROM meta_lists WHERE name=?", name) || {}).i || "[]"); } catch (e) { return []; } };

console.log("\n▸ DERIVED FROM THE CORPUS (Article 4.2 — no universe is hand-listed)");
const declared = ucos.productUniverses();
ok(declared.length === 26, "the constitution declares exactly 26 product universes", "n=" + declared.length);
ok(declared.every(u => u.key && u.name && u.icon && Number.isInteger(u.sourceLine)), "every universe carries a key, icon and document provenance");
ok(declared.every(u => u.key === ucos.keyOf(u.name)), "every key is the canonical form of its own name");
/* the vocabulary the platform shows must be the corpus's, not code's: the module holds
   only icon glyphs keyed by derived slugs — no corpus display name may appear in it */
const srcUcos = fs.readFileSync(path.join(__dirname, "..", "lib", "ucos.js"), "utf8");
ok(!/"Physical Products"|"Digital Products"|"Quantum Products"|"Future Unknown Product Types"/.test(srcUcos),
  "the module asserts none of the corpus's universe names (Article 4.2)");
/* the structurally-located declaration: it is read from the live document, so the icon
   map is a presentation fallback, never the vocabulary */
for (const name of ["Physical Products", "Digital Products", "OTT Platforms", "Quantum Products", "Future Unknown Product Types"]) {
  ok(declared.some(u => u.name === name), "UPIP §1 declares: " + name);
}

console.log("\n▸ THE REGISTRY IS THE SOURCE OF TRUTH (the console reads the DB, never code)");
ok(list("productUniverses").length === declared.length, "the product universe registry list is seeded", "n=" + list("productUniverses").length);
ok(list("productUniverses").every(u => declared.some(d => d.key === u.key)), "the seeded list is exactly the derived vocabulary");

console.log("\n▸ AN OPERATOR'S ADDITION SURVIVES A CORPUS RE-PARSE (zero loss)");
/* an operator extends the vocabulary from the console — a re-parse must keep it, because
   the seed merges additively and never clobbers what the corpus did not declare */
const custom = list("productUniverses").concat([{ key: "orbital_logistics", name: "Orbital Logistics", icon: "🛰️" }]);
db.run("UPDATE meta_lists SET items=? WHERE name='productUniverses'", JSON.stringify(custom));
/* force the re-parse path: clearing the digest makes the seed rebuild as if the corpus
   changed on disk (the only condition under which the vocabulary is legitimately refreshed) */
db.run("DELETE FROM platform_settings WHERE key='ucos_digest'");
console.log = () => { };
registry.seedRegistries();
console.log = silence;
const after = list("productUniverses");
ok(after.some(u => u.key === "orbital_logistics"), "an operator-added universe survives a corpus re-parse", JSON.stringify(after.map(u => u.key)));
ok(after.filter(u => u.key === "orbital_logistics").length === 1, "the operator addition is not duplicated by the merge");
ok(declared.every(d => after.some(a => a.key === d.key)), "every corpus-declared universe is still present after the re-parse");

console.log("\n▸ TRANSACTABLE: a global product carries its universe, and a bogus one is refused");
/* a minimal platform-admin session: every session resolves a tenant, so the audit ledger
   has a scope to chain against */
const s = { platform_admin: { id: 1, name: "P", email: "platform@luxora.shop" }, tenant: { id: 1 }, sid: "test-sid" };
const call = (method, urlStr, body) => {
  let out = {};
  const res = { writeHead: () => { }, end: s => { out = JSON.parse(s); } };
  api.handle({ method }, res, new URL(urlStr), s, body);
  return out;
};
const made = call("POST", "http://x/api/platform/global-products",
  { sku: "QBIT-1", name: "Qubit", universe: "quantum_products", price: 99, tax_class: "standard" });
ok(made.ok === true && made.id > 0, "a global product is created", JSON.stringify(made));
const row = db.get("SELECT universe, sku FROM global_products WHERE id=?", made.id);
ok(row.universe === "quantum_products", "the declared universe is persisted on the row", JSON.stringify(row));
/* an undeclared universe must not become a free string — it falls back to physical */
const bogus = call("POST", "http://x/api/platform/global-products",
  { sku: "NOPE-1", name: "Nope", universe: "this_universe_is_not_declared" });
ok(bogus.ok === true, "the product is still created");
ok(db.get("SELECT universe u FROM global_products WHERE sku='NOPE-1'").u === "physical_products",
  "an undeclared universe falls back to the default, never a free string");
/* the list response carries the vocabulary so the console's picker is registry-driven.
   The registry now holds the operator's orbital_logistics too (the merge above), so the
   exact count is "at least every declared universe" — the console never sees fewer */
const lst = call("GET", "http://x/api/platform/global-products");
ok(Array.isArray(lst.universes) && lst.universes.length >= declared.length && declared.every(d => lst.universes.some(x => x.key === d.key)),
  "the list response exposes the universe vocabulary to the console", "n=" + (lst.universes || []).length);
/* the platform catalogue is now AUTO-POPULATED (lib/gcatalog.js seeds one canonical
   archetype per declared universe, UPIP §1/§5), so the filter finds the operator's row
   alongside the archetype — the point is that it narrows to that universe, and the
   operator's own SKU is present in it */
const filtered = call("GET", "http://x/api/platform/global-products?universe=quantum_products");
ok(filtered.products.length >= 1 && filtered.products.some(p => p.sku === "QBIT-1"), "the universe filter narrows the catalog and finds the operator's row", JSON.stringify(filtered.products.map(p => p.sku)));
ok(filtered.products.every(p => p.universe === "quantum_products"), "every row in the filter belongs to that universe");
/* an universe with no archetype and no operator row still filters to nothing */
ok(call("GET", "http://x/api/platform/global-products?universe=cloud_services").products.every(p => p.universe === "cloud_services"), "the filter is exact even on an archetype universe");
/* the edit path carries the universe through an update */
const upd = call("PUT", "http://x/api/platform/global-products/" + made.id,
  { sku: "QBIT-2", name: "Qubit", universe: "digital_products", price: 99, tax_class: "standard", status: "draft" });
ok(upd.ok === true, "the product updates");
ok(db.get("SELECT universe u FROM global_products WHERE id=?", made.id).u === "digital_products", "the universe change is persisted");
/* a session without platform authority is refused — the vocabulary is platform-owned */
const denied = (() => {
  let out = {};
  api.handle({ method: "POST" }, { writeHead: () => { }, end: s => { out = JSON.parse(s); } },
    new URL("http://x/api/platform/global-products"), { tenant: { id: 1 }, sid: "t" }, { sku: "X", name: "X" });
  return out;
})();
ok(!!denied.error, "a non-platform session cannot write the global catalog", JSON.stringify(denied));

console.log("\n" + (failed ? "✗ " + failed + " check(s) failed" : "✓ all product-universe checks passed") + "  (" + passed + " passed)");
process.exit(failed ? 1 : 0);
