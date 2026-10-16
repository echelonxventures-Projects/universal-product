/* LUXORA Platform — Universal Commerce registries.
   Every status, kind, type, tier and category the commerce entities reference is
   a row in meta_lists, editable at runtime from Data Studio. Nothing is an enum
   in code: add a quick-commerce store kind, a fintech payout status, a B2B
   document type or a buyer-claim state here (or in the console) and every
   dropdown, every validation option and every state machine that reads the
   registry follows on the next request. This is the platform's Knowledge-Once
   rule applied to the commerce capability set. No vendor name appears in any
   list — these are the platform's own vocabularies. */
"use strict";
/* seed data (lib/seed/parity-registries.json): data, not code — the registries are seeded from it */
const SEED_PARITY_REGISTRIES = require("./seed/parity-registries.json");

const db = () => require("./db.js");
const J = (v, d) => { try { return v == null || v === "" ? (d == null ? [] : d) : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d == null ? [] : d; } };

/* registries are { name, label, items[] }; items are plain strings or {key,name} */
/* notes that lived in the seed literal (now lib/seed/parity-registries.json): */
/* ---------- Quick-commerce ---------- */
/* ---------- Fintech ---------- */
/* ---------- Marketplace ---------- */
/* ---------- B2B trust & trade ---------- */
/* ---------- Shopper experience ---------- */
const REG = SEED_PARITY_REGISTRIES.REG;

/* seed: idempotent, preserves operator edits (a console edit is never clobbered;
   only lists that were seeded by this module and left untouched self-heal) */
function seed() {
  const D = db();
  const stamp = "parity_v1";
  for (const [name, def] of Object.entries(REG)) {
    const items = def.items.map(it => (typeof it === "string" ? { key: it, name: it } : it));
    const ex = D.get("SELECT items, seeded_from FROM meta_lists WHERE name=?", name);
    if (!ex) D.run("INSERT INTO meta_lists(name,label,items,seeded_from) VALUES(?,?,?,?)", name, def.label, JSON.stringify(items), stamp);
    else if (!ex.seeded_from) D.run("UPDATE meta_lists SET items=?, seeded_from=?, label=? WHERE name=?", JSON.stringify(items), stamp, def.label, name);
  }
}

/* read a registry as an array of {key,name} (or plain strings when flat) */
function list(name) {
  const row = db().get("SELECT items FROM meta_lists WHERE name=?", name);
  return J(row ? row.items : "[]", []);
}
/* read a registry as a plain array of keys (for select options + validation) */
function keys(name) { return list(name).map(x => x.key || x); }
/* registry membership test (used by the parity engines for state validation) */
function has(name, value) { return keys(name).includes(value); }

module.exports = { REG, seed, list, keys, has };
