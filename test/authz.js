/* UCOS Ω∞ · authz — the ONE authorization engine.
   --------------------------------------------------------------------------
   Two consoles used to run two RBAC engines with two grant surfaces that share
   thirty section keys. Merging the engines naively would have blended the two
   surfaces: a store manager's "orders" grant would have opened the platform's
   global order view. authz.js is one engine with two NAMESPACED surfaces, and
   this proves the scope is the boundary:

     · a store role can only ever produce store:* grants
     · a platform role can only ever produce platform:* grants
     · one identity may hold both authorities, and the grants stay scoped
     · a bare key never crosses scopes by accident
     · the two facades still answer exactly as the two engines did

   The stored role rows are unchanged data; only the resolver was unified, so
   every grant a store or operator already has resolves identically. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os");
const TMP = path.join(os.tmpdir(), "authz-" + process.pid + ".db");
process.env.LX_DB = TMP;
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
const silence = console.log; console.log = () => { };
const db = require(path.join(__dirname, "..", "lib", "db.js"));
console.log = silence;

const authz = require(path.join(__dirname, "..", "lib", "authz.js"));
const rbac = require(path.join(__dirname, "..", "lib", "rbac.js"));
const prbac = require(path.join(__dirname, "..", "lib", "prbac.js"));

let passed = 0, failed = 0;
function ok(c, n, x) { if (c) { passed++; console.log("  ✓ " + n); } else { failed++; console.log("  ✗ " + n + (x ? " → " + x : "")); } }
const TID = 1;
authz.seed();

console.log("\n▸ §A THE SURFACES ARE NAMESPACED AND DISJOINT");
{
  ok(authz.SURFACES.store.length > 0 && authz.SURFACES.platform.length > 0,
    "both surfaces derive from the compiled canonical nav", authz.SURFACES.store.length + "/" + authz.SURFACES.platform.length);
  /* the thirty keys both consoles share are exactly the collision this engine exists to prevent */
  const shared = authz.SURFACES.store.filter(s => authz.SURFACES.platform.includes(s));
  ok(shared.length > 0, "the two surfaces genuinely share bare keys — the collision authz must prevent", shared.length);
  ok(!authz.SURFACES.store.includes("gorders") && authz.SURFACES.platform.includes("gorders"),
    "a platform-only leaf stays off the store surface");
  /* the store surface is closed under the entity router (privacy/compose are grantable though no nav leaf names them) */
  ok(authz.SURFACES.store.includes("privacy") && authz.SURFACES.store.includes("compose"),
    "the store surface is closed under the entity router (privacy + compose)");
  ok(rbac.SECTIONS.every(s => authz.SURFACES.store.includes(s)) && prbac.SECTIONS.every(s => authz.SURFACES.platform.includes(s)),
    "each facade exposes exactly its own surface");
}

console.log("\n▸ §B A STORE ROLE NEVER ESCAPES THE STORE SCOPE");
{
  const mgr = { role: "admin", staff_role: "manager", tenant_id: TID };
  const g = authz.grant(mgr);
  ok(Object.keys(g).every(k => k.startsWith("store:")), "a store role produces only store:* grants", Object.keys(g).slice(0, 3).join(","));
  ok(g["store:orders"] === "write", "a store manager can act on this store's orders");
  ok(g["store:team"] === false, "the manager role's team exclusion is honoured");
  ok(g["platform:tenants"] === undefined, "and grants nothing on the platform surface", JSON.stringify(g["platform:tenants"]));
  ok(!authz.canScope(mgr, "platform", "tenants", "read"), "canScope refuses a platform ask from a store-only identity");
  ok(authz.canScope(mgr, "store", "orders", "write"), "canScope grants the store ask the same role does");
}

console.log("\n▸ §C A PLATFORM ROLE NEVER ESCAPES THE PLATFORM SCOPE");
{
  const sup = { role: "support" };
  const g = authz.grant(sup);
  ok(Object.keys(g).every(k => k.startsWith("platform:")), "a platform role produces only platform:* grants", Object.keys(g).slice(0, 3).join(","));
  ok(g["platform:tenants"] === "write", "platform support may operate tenants");
  ok(g["platform:security"] === undefined, "but cannot touch the platform's own security surface", JSON.stringify(g["platform:security"]));
  ok(g["store:orders"] === undefined, "and grants nothing on the store surface");
  ok(authz.canScope(sup, "platform", "gorders", "write") && !authz.canScope(sup, "platform", "security", "read"),
    "the platform role's own grants resolve, its exclusions do not");
}

console.log("\n▸ §D ONE IDENTITY MAY HOLD BOTH AUTHORITIES — AND THE SCOPES DO NOT BLEND");
{
  const both = { store: { role: "admin", staff_role: "manager", tenant_id: TID }, platform: { role: "support" } };
  const g = authz.grant(both);
  ok(g["store:orders"] === "write" && g["platform:tenants"] === "write",
    "one identity carries both scoped authorities", JSON.stringify(Object.keys(g).length));
  ok(g["store:team"] === false && g["platform:security"] === undefined,
    "each authority's exclusions survive the merge — the map holds two scoped capabilities, not one blended one");
  ok(authz.can(both, "store:orders", null, "write") && authz.can(both, "platform:tenants", null, "write"),
    "a namespaced key resolves regardless of which authority supplied it");
  ok(!authz.can(both, "store:gorders", null, "read"),
    "a store-scoped ask for a platform-only section is refused");
  ok(authz.hasScope(both, "store") && authz.hasScope(both, "platform"),
    "hasScope reports each authority the identity holds");
}

console.log("\n▸ §E THE OWNERS' '*' EXPANDS ONLY WITHIN ITS OWN SURFACE");
{
  const so = { role: "admin", staff_role: "owner", tenant_id: TID };
  const po = { role: "owner" };
  ok(Object.keys(authz.grant(so)).every(k => k.startsWith("store:")), "a store owner's '*' reaches every STORE section and no platform one");
  ok(Object.keys(authz.grant(po)).every(k => k.startsWith("platform:")), "a platform owner's '*' reaches every PLATFORM section and no store one");
  ok(authz.canScope(so, "store", "privacy", "write"), "the store '*' is closed under the entity router (privacy)");
  ok(!authz.canScope(so, "platform", "security", "read"), "the store '*' never crosses to the platform surface");
  ok(!authz.canScope(po, "store", "orders", "read"), "the platform '*' never crosses to the store surface");
}

console.log("\n▸ §F THE FACADES ANSWER EXACTLY AS THE TWO ENGINES DID");
{
  /* every existing call site, test and stored meta_lists row keeps its shape */
  ok(rbac.can({ role: "admin", staff_role: "manager" }, "orders", "write", TID), "rbac.can(store user, section, mode, tenant) still grants");
  ok(!rbac.can({ role: "admin", staff_role: "manager" }, "team", "read", TID), "and still honours a role exclusion");
  ok(rbac.can({ role: "admin", staff_role: "owner" }, "privacy", "write", TID), "rbac's owner still reaches the router-only section");
  ok(prbac.can({ role: "support" }, "tenants", "write"), "prbac.can(admin, section, mode) still grants");
  ok(!prbac.can({ role: "support" }, "security", "read"), "and still honours a platform exclusion");
  ok(prbac.can({ role: "owner" }, "security", "write"), "prbac's owner still has the whole platform surface");
  /* the shipped role sets are the same vocabulary the two engines seeded */
  ok(rbac.ROLES.some(r => r.key === "support") && prbac.ROLES.some(r => r.key === "auditor"),
    "both shipped role sets are served from one engine");
  ok(rbac.roles(TID).length > 0 && prbac.roles().length > 0, "both role stores read through the facades");
  ok(rbac.sectionForEntity("consent") === "privacy" && prbac.sectionForRoute("/api/platform/tenants") === "tenants",
    "both section maps resolve through the facades");
}

console.log("\n▸ §G THE SCOPE INVARIANT SURVIVES A ROLE EDIT");
{
  /* an operator re-scoping a store role cannot widen it onto the platform
     surface — validateRole rejects any section outside the role's own scope */
  const bad = authz.upsertRole("store", TID, { key: "spy", name: "Spy", sections: { tenants: "write" } });
  ok(!bad.ok, "a store role naming a platform section is refused", JSON.stringify(bad.fails));
  const bad2 = authz.upsertRole("platform", 0, { key: "spy2", name: "Spy", sections: { orders: "write" } });
  ok(!bad2.ok, "a platform role naming a store section is refused", JSON.stringify(bad2.fails));
  const good = authz.upsertRole("store", TID, { key: "local", name: "Local", sections: { orders: "write" } });
  ok(!!good.ok, "a store role naming its own section is accepted");
  ok(Object.keys(authz.grant({ role: "admin", staff_role: "local", tenant_id: TID })).every(k => k.startsWith("store:")),
    "and the new role still cannot escape the store scope");
  authz.deleteRole("store", TID, "local");
}

console.log("\n" + (failed ? "✗ " + failed + " check(s) failed" : "✓ all authz checks passed") + "  (" + passed + " passed)");
process.exit(failed ? 1 : 0);
