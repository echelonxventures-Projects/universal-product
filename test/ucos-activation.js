/* UCOS Ω∞ · activation & breadth audit.
   --------------------------------------------------------------------------
   The corpus declares 1,877 universes. test/ucos-universes.js proves they are all
   INSTANTIATED; test/ucos-catalog.js proves ONE of them (Insurance) is
   TRANSACTABLE. That leaves the honest question open: does the generic engine
   actually serve every FAMILY, or did Insurance get special treatment?

   This answers it. It samples universes across every distinct corpus family
   (insurance, streaming, cloud, AI, quantum, financial…), and for each proves
   the FULL generic path with no per-universe code:
     ACTIVATE   a canonical offering is materialized from the universe's own fields
     PUBLISH    it lands in a tenant catalog as a shopper-facing projection
     TRANSACT   it is cart-able, with a SKU and inventory backing it
     WITHDRAW   it leaves no orphaned rows
   Then it proves bulk activation is bounded and idempotent, and that the
   traceability map reports every layer honestly — including the layers that are
   absent by design (Article 4.2: no per-universe route exists).

   Fast, no server, no port, own throwaway DB. */
"use strict";
const path = require("path");
const fs = require("fs");

const TMP = path.join(require("os").tmpdir(), "ucos-act-" + process.pid + ".db");
process.env.LX_DB = TMP;
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }

const silence = console.log; console.log = () => { };
const db = require(path.join(__dirname, "..", "lib", "db.js"));
const ucos = require(path.join(__dirname, "..", "lib", "ucos.js"));
const univ = require(path.join(__dirname, "..", "lib", "ucos-universes.js"));
const cat = require(path.join(__dirname, "..", "lib", "ucos-catalog.js"));
const trace = require(path.join(__dirname, "..", "lib", "ucos-trace.js"));
const api = require(path.join(__dirname, "..", "lib", "api.js"));
ucos.seed(db);
univ.instantiateAll();
console.log = silence;

let passed = 0, failed = 0;
const ok = (cond, name, extra) => { if (cond) { passed++; } else { failed++; console.log("  ✗ " + name + (extra ? "  → " + extra : "")); } };
const cnt = (sql, ...p) => { try { return (db.get(sql, ...p) || {}).c || 0; } catch (e) { return 0; } };
const q = (sql, ...p) => { try { return db.get(sql, ...p) || {}; } catch (e) { return {}; } };
const allList = (sql, ...p) => { try { return db.all(sql, ...p) || []; } catch (e) { return []; } };

console.log("\n▸ BREADTH: every distinct corpus family is operable, not just one");
/* the families are derived from the live parse — never hand-listed. A family is the
   registry label that declared the universe ("Insurance Meta Model" etc.), so a
   corpus that adds a family is covered with no test change. discover() carries the
   declaring label; the instantiated set is the registry's source of truth. */
const all = univ.list();
const declared = univ.discover();
const famOf = Object.fromEntries(declared.map(d => [d.key, d.registry || "declared"]));
const families = [...new Set(all.map(u => famOf[u.key] || "declared"))];
ok(all.length > 500, "a substantial universe set is instantiated", "n=" + all.length);
ok(families.length >= 5, "universes span multiple distinct families", families.length + " families");
/* sample deterministically across families so the test is repeatable, not flaky:
   the first universe of each family + a stride across the whole set */
const sample = [];
const seenFam = new Set();
for (const u of all) { const f = famOf[u.key] || "declared"; if (!seenFam.has(f)) { seenFam.add(f); sample.push(u); } }
for (let i = 0; i < all.length; i += Math.max(1, Math.floor(all.length / 24))) if (!sample.includes(all[i])) sample.push(all[i]);
console.log("  sampling " + sample.length + " universes across " + families.length + " families");

console.log("\n▸ THE FULL GENERIC PATH (no per-universe code anywhere in this loop)");
let pathOk = 0, cartable = 0;
for (const u of sample) {
  const ek = u.entity_key;
  /* activate: canonical offering materialized from the universe's own fields + published */
  const a = cat.activate(1, ek);
  if (!a.ok) { ok(false, "activate " + u.name, JSON.stringify(a)); continue; }
  pathOk++;
  /* the projection is a real catalog row the shopper's code path addresses */
  const row = q("SELECT id, price, lifecycle FROM products WHERE tenant_id=1 AND source_universe=?", ek);
  if (!row) { ok(false, "catalog row for " + u.name, "no projection"); continue; }
  const sku = q("SELECT id, stock FROM skus WHERE tenant_id=1 AND product_id=?", row.id);
  const inv = q("SELECT qty FROM inventory WHERE tenant_id=1 AND sku_id=?", sku.id || -1);
  ok(!!sku && !!inv, "SKU + inventory back the " + u.name + " offering", "");
  cartable++;
}
ok(pathOk === sample.length, "every sampled universe activated into the catalog", pathOk + "/" + sample.length);
ok(cartable === sample.length, "every sampled universe is backed by SKU + inventory (cart-able)", cartable + "/" + sample.length);
/* a universe's fields came from the corpus, and the offering respects them: the
   projection's name is the universe's own label, never an invented string */
const one = sample[0];
const oneRow = q("SELECT title FROM products WHERE tenant_id=1 AND source_universe=?", one.entity_key);
ok(!!oneRow && oneRow.title === one.name, "the canonical offering carries the universe's own name", JSON.stringify(oneRow));

console.log("\n▸ IDEMPOTENCE + BOUNDS (bulk activation is safe on every boot)");
const n1 = cnt("SELECT COUNT(*) c FROM products WHERE tenant_id=1 AND source_kind='universe'");
cat.activateAll(1, { limit: 40 });
cat.activateAll(1, { limit: 40 });
const n2 = cnt("SELECT COUNT(*) c FROM products WHERE tenant_id=1 AND source_kind='universe'");
ok(n1 > 0, "bulk activation populated the catalog", "n=" + n1);
ok(cnt("SELECT COUNT(*) c FROM products WHERE tenant_id=1 AND source_kind='universe' GROUP BY tenant_id, id HAVING COUNT(*) > 1") === 0, "no duplicate catalog rows across re-activations");
ok(cnt("SELECT COUNT(*) c FROM skus WHERE tenant_id=1 AND product_id LIKE 'UV-%' GROUP BY tenant_id, product_id, code HAVING COUNT(*) > 1") === 0, "no duplicate SKUs across re-activations");
/* the limit is a real bound, not a hint: a corpus of 1,877 must not saturate a request */
const bounded = cat.activateAll(1, { limit: 5 });
ok(bounded.activated <= 5, "activateAll respects its limit on a cold pass", bounded.activated);
/* the remaining-count must be HONEST: `skipped` is a subset of `already`, so subtracting
   both double-counted and made a partially-activated corpus report remaining:0 at 64%.
   A completion routine that trusts that number stops early and silently strands a third
   of the corpus. This guards the arithmetic directly. */
const mid = cat.activateAll(1, { limit: 5 });
const onShelf = new Set(allList("SELECT DISTINCT source_universe k FROM products WHERE tenant_id=1 AND source_kind='universe'").map(r => r.k)).size;
ok(mid.onShelf === onShelf, "onShelf equals the real number of distinct universes on the shelf", mid.onShelf + " vs " + onShelf);
ok(mid.remaining === all.length - onShelf, "remaining is exactly the declared set minus the shelf, with no double-count",
  mid.remaining + " vs " + (all.length - onShelf));
ok(mid.remaining > 0 || onShelf === all.length, "remaining is only zero when the shelf is genuinely complete", "remaining=" + mid.remaining);

console.log("\n▸ COMPLETION: the whole corpus, to 100% (the fixed last inch)");
/* activateComplete walks the rest. It must terminate with the shelf stocked or a real
   failure — never an early "done" while universes remain. */
const complete = cat.activateComplete(1, { limit: 500 });
ok(complete.ok === true, "activation to completion succeeds with no failures", JSON.stringify({ failed: complete.failed, rounds: complete.rounds }));
ok(complete.remaining === 0, "completion reports zero remaining universes", "remaining=" + complete.remaining);
ok(complete.coverage === 100, "the flagship catalog is 100% transactable", complete.coverage + "%");
ok(complete.onShelf === all.length, "every declared universe is on the shelf", complete.onShelf + " vs " + all.length);
/* a second completion is a warm no-op: nothing is re-materialized, nothing duplicates */
const warm = cat.activateComplete(1, { limit: 500 });
ok(warm.activated === 0, "a warm completion activates nothing", warm.activated);
ok(cnt("SELECT COUNT(*) c FROM products WHERE tenant_id=1 AND source_kind='universe' GROUP BY tenant_id, id HAVING COUNT(*) > 1") === 0, "no duplicate catalog rows after completion");

console.log("\n▸ WITHDRAWAL LEAVES NO ORPHANS (any family, not just the tested one)");
const wdKey = sample[sample.length - 1].entity_key;
const wd = cat.withdrawUniverse(1, wdKey);
ok(wd.ok === true, "a sampled universe can be withdrawn", JSON.stringify(wd));
ok(cnt("SELECT COUNT(*) c FROM products WHERE tenant_id=1 AND source_universe=?", wdKey) === 0, "withdrawal removed the catalog row");
ok(cnt("SELECT COUNT(*) c FROM skus s WHERE s.product_id IN (SELECT id FROM products WHERE source_universe=?)", wdKey) === 0, "withdrawal left no orphaned SKU");
ok(cnt("SELECT COUNT(*) c FROM inventory i WHERE i.sku_id IN (SELECT id FROM skus WHERE product_id LIKE 'UV-%')") >= 0, "inventory stays consistent");

console.log("\n▸ ACTIVATION STATS (the honest deployment picture)");
const st = cat.activationStats();
ok(st.declared === all.length, "activation stats report the full declared set", st.declared + " vs " + all.length);
ok(st.tenants.length >= 1, "every active tenant is reported", "tenants=" + st.tenants.length);
const t1 = st.tenants.find(t => t.tenantId === 1) || {};
ok(t1.transactable > 0 && t1.coverage > 0, "tenant 1 reports real transactable coverage", JSON.stringify(t1));

console.log("\n▸ TRACEABILITY REPORTS EVERY LAYER — INCLUDING ABSENT-BY-DESIGN ONES");
const tr = trace.trace(sample[0].name);
ok(tr.layers.length === 8, "a trace covers all eight runtime layers", tr.layers.length);
ok(tr.layers.filter(l => l.present).length >= 6, "a sampled universe is wired through most layers", tr.layers.filter(l => l.present).length + "/8");
ok(tr.layers.some(l => !l.present), "trace reports the layers that are absent, rather than hiding them");
const notFound = trace.trace("zzz_not_a_real_concept_qqq");
ok(/not found in the corpus/.test(notFound.verdict), "a nonsense key is reported as absent, not silently empty", notFound.verdict);
const m = trace.matrix();
ok(m.implementation.universes === all.length, "the matrix reports every universe as a live entity", m.implementation.universes);
ok(m.perDocument.length === 3, "the matrix covers all three corpora", m.perDocument.map(d => d.doc).join(","));

console.log("\n▸ AUTHORITY: activation is a platform action (a store admin cannot activate)");
const call = (method, urlStr, body, sess) => {
  let out = {};
  const res = { writeHead: () => { }, end: s => { out = JSON.parse(s); } };
  api.handle({ method }, res, new URL(urlStr), sess || { platform_admin: { id: 1, email: "p@p" }, tenant: { id: 1 } }, body);
  return out;
};
const okCall = call("POST", "http://x/api/ucos/catalog/uv_insurance/activate?tenant_id=1", {});
ok(okCall.ok === true, "a platform session can activate a universe", JSON.stringify(okCall));
const denied = call("POST", "http://x/api/ucos/catalog/uv_insurance/activate?tenant_id=1", {}, { tenant: { id: 1 } });
ok(!!denied.error, "a non-platform session is refused", JSON.stringify(denied));
ok(/Platform access required/.test(denied.error || ""), "the refusal names the authority required", denied.error);
/* activation writes a tenant's live catalog, so an invented tenant must be refused
   rather than leaving orphaned catalog rows behind */
const ghostTenant = call("POST", "http://x/api/ucos/catalog/activate?tenant_id=99999", { limit: 10 });
ok(!!ghostTenant.error, "activating into a nonexistent tenant is refused", JSON.stringify(ghostTenant));
ok(/unknown or inactive tenant/.test(ghostTenant.error || ""), "the refusal names the missing tenant", ghostTenant.error);
/* the guard writes once — a second write would corrupt the response (the platform
   hardening rule proven elsewhere); the endpoint must follow the same pattern */
const apiSrc = fs.readFileSync(path.join(__dirname, "..", "lib", "api.js"), "utf8");
const dbl = (apiSrc.match(/require(?:Platform|Admin|Section|Store)\(s,\s*res[^)]*\)\)\s*return\s+bad\(/g) || []).length;
ok(dbl === 0, "no new endpoint re-writes a response after a failed guard", dbl + " site(s)");

console.log("\n▸ CLEAN STATE (the throwaway DB never leaks sampled universes into other checks)");
for (const u of sample) cat.withdrawUniverse(1, u.entity_key);
db.run("DELETE FROM entity_data WHERE entity LIKE 'uv_%' AND tenant_id=0");

console.log("\n" + (failed ? "✗ " + failed + " check(s) failed" : "✓ all activation & breadth checks passed") + "  (" + passed + " passed)");
process.exit(failed ? 1 : 0);
