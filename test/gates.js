/* LUXORA Platform — engines ask binding points, not each other's capabilities (lib/gates.js).
   Checkout asks `checkout.wallet`, AI asks `ai.premium`, the storefront asks
   `storefront.currency_switch`; the featureGates registry row says which capability opens each
   point. A storefront atom the platform policy must allow names its policy flag on its
   catalogue row. The gate below fails if an engine or console names a module capability. */
"use strict";
const path = require("path");
const fs = require("fs");
const os = require("os");
const TMP = path.join(os.tmpdir(), "gates-" + process.pid + ".db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
process.env.LX_DB = TMP;
const silence = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = silence;
const gates = require("../lib/gates.js");
const mods = require("../lib/modules.js");
const caps = require("../lib/capabilities.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const getList = name => JSON.parse(db.get("SELECT items FROM meta_lists WHERE name=?", name).items);
const setList = (name, items) => db.run("UPDATE meta_lists SET items=? WHERE name=?", JSON.stringify(items), name);

try {
  const tid = db.get("SELECT id FROM tenants ORDER BY id LIMIT 1").id;
  const moduleCaps = new Set(mods.MARKET.flatMap(m => m.capabilities || []));

  console.log("▸ EVERY BINDING POINT NAMES A CAPABILITY THAT EXISTS");
  const rows = getList("featureGates");
  const orphan = rows.filter(r => r.source === "capability" ? !caps.CATALOG.some(c => c.key === r.capability) : !moduleCaps.has(r.capability)).map(r => r.key);
  ok(rows.length >= 10 && orphan.length === 0, "the featureGates registry is seeded and every point resolves (" + rows.length + " points)", orphan);

  console.log("▸ A POINT OPENS WHEN ITS CAPABILITY IS INSTALLED");
  ok(gates.on(tid, "checkout.wallet") === false, "checkout.wallet is closed before the wallet module is installed");
  const wallet = mods.MARKET.find(m => (m.capabilities || []).includes(gates.capabilityOf("checkout.wallet")));
  mods.applyModule(tid, mods.moduleRow(wallet.id), {});
  ok(gates.on(tid, "checkout.wallet") === true && gates.all(tid)["checkout.wallet"] === true, "installing the module that provides it opens it");
  ok(gates.provides(mods.moduleRow(wallet.id), "checkout.wallet"), "the release guard finds the module that provides the point");

  console.log("▸ MOVING A POINT TO ANOTHER CAPABILITY IS A ROW EDIT");
  setList("featureGates", rows.map(r => r.key === "checkout.wallet" ? { ...r, capability: "loyaltyPro" } : r));
  ok(gates.on(tid, "checkout.wallet") === false, "pointing checkout.wallet at a capability the store lacks closes it");
  setList("featureGates", rows);
  ok(gates.on(tid, "checkout.wallet") === true, "restoring the row reopens it");

  console.log("▸ A MODULE SETTING IS READ THROUGH ITS POINT");
  const idp = mods.MARKET.find(m => (m.capabilities || []).includes(gates.capabilityOf("checkout.login_required")));
  ok(gates.setting(tid, "checkout.login_required") === undefined, "no providing module, no setting");
  mods.applyModule(tid, mods.moduleRow(idp.id), { [gates.row("checkout.login_required").config]: true });
  ok(gates.setting(tid, "checkout.login_required") === true, "the providing module's config answers the point's setting");

  console.log("▸ POLICY-GATED ATOMS AND STOREFRONT ATOMS ARE CATALOGUE ROWS");
  ok(caps.policyRefusal("coupons", { couponsAllowed: false }) && !caps.policyRefusal("coupons", { couponsAllowed: true }), "coupons are refused exactly when the policy flag its row names is off");
  ok(caps.policyRefusal("fiscalSelection", {}) && !caps.policyRefusal("reviews", {}), "a settings feature name maps to its atom; an atom with no policy row is never refused");
  const rv = caps.CATALOG.find(c => c.key === "reviews"); rv.policy = "reviewsAllowed";
  ok(!!caps.policyRefusal("reviews", {}) && caps.policyFeatures({ reviewsAllowed: true }).reviews === true, "a new policy-gated atom is one field on its row");
  delete rv.policy;
  ok(caps.STOREFRONT_KEYS.length === caps.CATALOG.filter(c => c.settings_atom).length && caps.STOREFRONT_KEYS.includes("coupons"), "the storefront atoms are the rows flagged settings_atom (" + caps.STOREFRONT_KEYS.length + ")");

  console.log("▸ THE GATE: NO ENGINE OR CONSOLE NAMES A MODULE CAPABILITY");
  /* identity: an engine naming the module it is (GOIP asking for its own module) */
  const IDENTITY = { "goip.js": ["goip"] };
  const hits = [];
  const scan = (dir, f) => {
    const src = fs.readFileSync(path.join(dir, f), "utf8").replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/[^\n]*/g, "");
    for (const re of [/hasCap\([^,()]+,\s*["']([A-Za-z_]+)["']\)/g, /capabilities[^;\n]{0,40}\.includes\(\s*["']([A-Za-z_]+)["']\s*\)/g]) {
      let m; while ((m = re.exec(src))) if (moduleCaps.has(m[1]) && !(IDENTITY[f] || []).includes(m[1])) hits.push(f + ": " + m[1]);
    }
  };
  for (const d of ["lib", "public/js"]) { const dir = path.join(__dirname, "..", d); for (const f of fs.readdirSync(dir).filter(f => f.endsWith(".js"))) scan(dir, f); }
  ok(hits.length === 0, "capability checks across engines go through binding points", [...new Set(hits)]);
} catch (e) { failed++; console.log("  ✗ threw: " + (e && e.stack || e)); }
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
