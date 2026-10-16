/* LUXORA Platform - ISO 3166-2 subdivision registry: pure data manifest.
   A country's states/provinces/regions are MASTER DATA, children of the country master.
   This file is the corpus declaration — the same role providers.js plays for providers and
   meta.js for taxonomies. Adding a country's subdivisions is editing this DATA, never code;
   lib/registry.js's reconcileSubdivisions() materialises it into the `subdivisions` table
   for every country present, on every boot and the moment a country is added.

   Format: { CC: [ { code, name, level } ] }
     code  — ISO 3166-2, globally unique, the master key ("US-CA", "IN-MH")
     name  — the operator-facing label ("California", "Maharashtra")
     level — what this division is called in the country's own nomenclature
             (state / province / region / county / prefecture / emirate / territory / district)
   `parent` is omitted for a country's primary divisions (the top level is NULL in the table);
   a country that nests divisions declares a child with `parent: "<parent code>"`, and the
   materialiser resolves it to the parent's numeric id — the tree is DATA, the depth is unbounded.
*/
"use strict";
/* seed data (lib/seed/subdivisions.json): data, not code — the registries are seeded from it */
const SEED_SUBDIVISIONS = require("./seed/subdivisions.json");

const SUBDIVISIONS = SEED_SUBDIVISIONS.SUBDIVISIONS;

/* normalise into a uniform shape: every entry gets a globally-unique ISO 3166-2 code (the
   raw entry is authoritative; the `_code` aside is only how a few GB/FR children whose ISO
   code has no country prefix are spelled in the standard), and `parent` stays a code the
   materialiser resolves. Entries are returned in declaration order, so the corpus's own
   ordering is what the console renders. */
function forCountry(code) {
  const list = SUBDIVISIONS[String(code || "").toUpperCase()];
  if (!list) return [];
  return list.map(s => ({ code: String(s._code || s.code).toUpperCase(), name: s.name, level: s.level, parent: s.parent || null }));
}

module.exports = { SUBDIVISIONS, forCountry };
