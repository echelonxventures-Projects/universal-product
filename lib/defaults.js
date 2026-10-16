/* LUXORA Platform — defaults are data.
   An engine that needs a value the caller did not give asks here instead of writing
   `|| "USD"` or `|| "commerce"`:
     currency(tenantId)  the store's chosen currency, else its country's, else the currency of
                         the platform's default country (security policy → countries master)
     of(list)            the row the registry flags `default: true`, else the row the seed
                         declares, else the list's first row
   lib/seed/defaults.json declares which row is each list's default; seed() stamps that flag
   onto an install whose list flags none, so changing a default is a registry edit. */
"use strict";
/* seed data (lib/seed/defaults.json): data, not code — the registries are seeded from it */
const SEED_DEFAULTS = require("./seed/defaults.json");
const reg = () => require("./registry.js");
const db = () => require("./db.js");
const keyOf = x => (x && typeof x === "object" ? x.key : x);

function rows(list) { try { const l = reg().list(list); return Array.isArray(l) ? l : []; } catch (e) { return []; } }

function of(list) {
  const rs = rows(list);
  const flagged = rs.find(r => r && typeof r === "object" && r.default);
  if (flagged) return String(flagged.key);
  const declared = SEED_DEFAULTS.lists[list];
  if (declared != null && (!rs.length || rs.some(r => String(keyOf(r)) === declared))) return declared;
  return rs.length ? String(keyOf(rs[0])) : undefined;
}

function platformCurrency() {
  try { const c = reg().country(require("./security.js").defaultCountry()); if (c && c.currency) return String(c.currency).toUpperCase(); } catch (e) { }
  return SEED_DEFAULTS.currency;
}
/* a store's currency is the one its commerce settings choose (when the currency master knows
   it), else its country's — the same rule the storefront's commerce block resolves by */
function currency(tenantId) {
  const tid = Number(tenantId) || 0;
  if (tid > 0) {
    try {
      if (db().get("SELECT id FROM tenants WHERE id=?", tid)) {
        const c = require("./settings.js").load(tid).commerce || {};
        const own = c.currency && reg().currency(c.currency); if (own) return String(own.code).toUpperCase();
        const co = reg().country(c.country); if (co && co.currency) return String(co.currency).toUpperCase();
      }
    } catch (e) { }
  }
  return platformCurrency();
}

/* the seed's declared default reaches an install whose list flags none; an operator's own
   flag (on any row) is never moved */
function seed() {
  let n = 0;
  for (const [list, key] of Object.entries(SEED_DEFAULTS.lists)) {
    try {
      const row = db().get("SELECT items FROM meta_lists WHERE name=?", list); if (!row) continue;
      const cur = JSON.parse(row.items || "[]"); if (!Array.isArray(cur) || cur.some(r => r && typeof r === "object" && r.default)) continue;
      /* a list of plain names keeps its shape: of() reads the seed declaration for it */
      const i = cur.findIndex(r => r && typeof r === "object" && String(r.key) === key); if (i < 0) continue;
      cur[i] = Object.assign({}, cur[i], { default: true });
      db().run("UPDATE meta_lists SET items=? WHERE name=?", JSON.stringify(cur), list); n++;
    } catch (e) { }
  }
  return n;
}

/* what the consoles read (/api/meta): every declared list's default, and the platform currency */
function all() { const out = { currency: platformCurrency(), lists: {} }; for (const l of Object.keys(SEED_DEFAULTS.lists)) out.lists[l] = of(l); return out; }

module.exports = { of, currency, platformCurrency, seed, all, LISTS: Object.keys(SEED_DEFAULTS.lists) };
