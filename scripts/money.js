/* LUXORA Platform — money at rest, for an operator (lib/money-store.js).
     node scripts/money.js verify                 every spine amount's projection equals its minor
                                                  units; refund totals agree; exits 1 if not
     node scripts/money.js quarantine [table]     the amounts the migration could not convert
     node scripts/money.js resolve <id> <minor> --by <name> [--currency XXX] [--note "…"]
   Run it against the database it names (LX_DB / LX_DB_DRIVER, as the server is) — after a
   restore, before an upgrade, and to clear the quarantine with a recorded decision. */
"use strict";
const args = process.argv.slice(2);
const flag = k => { const i = args.indexOf("--" + k); return i < 0 ? undefined : args[i + 1]; };
const quiet = console.log; console.log = () => { };
require("../lib/db.js");
console.log = quiet;
const MS = require("../lib/money-store.js");
const cmd = args[0];
if (cmd === "verify") {
  const v = MS.verify();
  console.log(JSON.stringify(v, null, 1));
  process.exit(v.ok ? 0 : 1);
} else if (cmd === "quarantine") {
  const rows = MS.quarantineList({ status: flag("status") || "open", table: args[1] && !args[1].startsWith("--") ? args[1] : "" });
  for (const r of rows) console.log(`#${r.id} ${r.table_name}[${r.row_key}].${r.column_name}  ${r.source_value} ${r.source_currency || "(no currency)"}  ${r.reason}  ${JSON.stringify(r.candidates)}`);
  console.log(rows.length + " entr" + (rows.length === 1 ? "y" : "ies"));
} else if (cmd === "resolve") {
  const out = MS.resolve(Number(args[1]), { minor: args[2], by: flag("by"), currency: flag("currency"), note: flag("note") });
  require("../lib/db.js").audit(null, "operator", null, String(flag("by")), "money.quarantine_resolve", "money_quarantine", String(args[1]), { decision: out.amount, table: out.table, key: out.key, column: out.column, note: flag("note") || "" }, "", null);
  console.log(JSON.stringify(out));
} else { console.log("usage: node scripts/money.js verify | quarantine [table] | resolve <id> <minor> --by <name> [--currency XXX] [--note …]"); process.exit(2); }
