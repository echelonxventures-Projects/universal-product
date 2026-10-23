/* LUXORA Platform — feature gates: an engine asks a binding point, never another engine's
   capability by name.
   Checkout does not ask "is the `wallet` module capability on?"; it asks `checkout.wallet`,
   and the featureGates registry row says which capability opens that point and where it
   comes from (`source: "module"` — an installed module's capability, through the rules
   engine's module.cap gate — or `"capability"` — the capability catalogue). A row may also
   carry the setting it reads from the providing module's config (`config`) and the message a
   refusal shows. Moving a feature to another module, or splitting a Pro bundle, is a row edit.
   An engine naming the capability it *is* (the ride engine's `ride_hailing`) is identity, not
   a gate, and stays as it is. */
"use strict";
/* seed data (lib/seed/gates.json): data, not code — the registries are seeded from it */
const SEED_GATES = require("./seed/gates.json");
const db = () => require("./db.js");
const mods = () => require("./modules.js");
const caps = () => require("./capabilities.js");

function rows() {
  try { const l = require("./registry.js").list("featureGates"); if (Array.isArray(l) && l.length) return l; } catch (e) { }
  return SEED_GATES.featureGates;
}
function row(point) { return rows().find(r => r && r.key === String(point)) || null; }
function capabilityOf(point) { const r = row(point); return r ? r.capability : null; }

function on(tenantId, point) {
  const r = row(point); if (!r || !r.capability) return false;
  try { return r.source === "capability" ? !!caps().on(tenantId, r.capability) : !!mods().hasCap(tenantId, r.capability); } catch (e) { return false; }
}
/* the installed module that provides the point's capability (for its config) */
function providerOf(tenantId, point) {
  const c = capabilityOf(point); if (!c) return null;
  try { return mods().installed(tenantId).find(m => ((m.manifest || {}).capabilities || []).includes(c)) || null; } catch (e) { return null; }
}
/* the setting the row names, read from the providing module's config */
function setting(tenantId, point) {
  const r = row(point); if (!r || !r.config || !on(tenantId, point)) return undefined;
  const m = providerOf(tenantId, point); if (!m) return undefined;
  const cfg = typeof m.config === "string" ? (() => { try { return JSON.parse(m.config); } catch (e) { return {}; } })() : (m.config || {});
  return cfg[r.config];
}
/* does this module provide the point (a module manifest, as stored) */
function provides(module, point) {
  const c = capabilityOf(point); if (!c || !module) return false;
  let man = module.manifest; if (typeof man === "string") { try { man = JSON.parse(man); } catch (e) { man = {}; } }
  return ((man || {}).capabilities || []).includes(c);
}
function message(point, fallback) { const r = row(point); return (r && r.message) || fallback || ((r && r.name) || String(point)) + " is not enabled for this store"; }
/* every point, open or closed, for one store — what the consoles and storefront read */
function all(tenantId) { const out = {}; for (const r of rows()) if (r && r.key) out[r.key] = on(tenantId, r.key); return out; }

/* the seed's rows reach an install: the list is created, and a point a release adds is appended
   (an operator's edit to an existing row is never overwritten) */
function seed() {
  const D = db();
  const cur = D.get("SELECT items FROM meta_lists WHERE name='featureGates'");
  if (!cur) { D.run("INSERT INTO meta_lists(name,label,items) VALUES('featureGates','Feature gates · binding point → capability',?)", JSON.stringify(SEED_GATES.featureGates)); return SEED_GATES.featureGates.length; }
  let items = []; try { items = JSON.parse(cur.items || "[]"); } catch (e) { }
  const have = new Set(items.map(x => x && x.key));
  const add = SEED_GATES.featureGates.filter(r => !have.has(r.key));
  if (add.length) D.run("UPDATE meta_lists SET items=? WHERE name='featureGates'", JSON.stringify(items.concat(add)));
  return add.length;
}

module.exports = { on, all, row, capabilityOf, providerOf, setting, provides, message, seed };
