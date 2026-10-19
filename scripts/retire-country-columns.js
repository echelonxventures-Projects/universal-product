/* LUXORA Platform — retire the country columns an install from before the place tree still has
   (currency, symbol, locale, decimals, tax_mode, tax_rate; lib/seed/places.json retiredColumns).

   Nothing reads them: a country's currency and locale are settings at its place on the kernel,
   its symbol and decimals its currency's, its tax the tax engine's. The boot imports their values
   onto the kernel but never drops them; this script does, when an operator runs it.

   It refuses unless every country's settings are on the kernel, and on SQLite it first writes a
   copy of the database next to it.

   Usage: node scripts/retire-country-columns.js --yes      (uses LX_DB, as the server does) */
"use strict";
const path = require("path");
if (!process.argv.includes("--yes")) {
  console.log("Drops the retired country columns after importing their values onto the kernel.\nRun again with --yes to proceed.");
  process.exit(2);
}
const db = require(path.join(__dirname, "..", "lib", "db.js"));
const P = require(path.join(__dirname, "..", "lib", "places.js"));
const present = P.RETIRED.filter(c => P.hasColumn(c, P.TABLE));
if (!present.length) { console.log("Nothing to retire: the country table has none of " + P.RETIRED.join(", ")); process.exit(0); }
if (!db.USE_PG) {
  const copy = db.DB_PATH + ".before-retire-" + new Date().toISOString().replace(/[:.]/g, "-");
  db.exec(`VACUUM INTO '${copy.replace(/'/g, "''")}'`);
  console.log("Copy written: " + copy);
}
const dropped = P.retireColumns();
console.log("Retired: " + dropped.join(", "));
