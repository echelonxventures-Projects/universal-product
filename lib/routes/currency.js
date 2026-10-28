/* LUXORA Platform — currency domain routes (_registry/business-domains.json `currency`).
   Money at rest (lib/money-store.js): the platform's reconciliation of every payment-spine
   amount, and the amounts the money migration could not convert — each resolved by an operator
   with a recorded decision, never guessed. What it needs from the shared HTTP kit (lib/api.js)
   is passed in as `kit`. */
"use strict";

module.exports = { domain: "currency", routes(kit) {
  const { audit, bad, ipOf, json, requirePlatform, requirePlatformSection } = kit;
  const MS = () => require("../money-store.js");

  function apiPlatformMoney(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    json(res, 200, { verify: MS().verify(), quarantine: MS().quarantineList({ status: url.searchParams.get("status") || "open", table: url.searchParams.get("table") || "" }) });
  }
  function apiPlatformMoneyResolve(req, res, url, s, body, id) {
    if (!requirePlatformSection(s, res, "runtime", "write")) return;
    let out;
    try { out = MS().resolve(Number(id), { minor: body.minor, currency: body.currency, by: s.platform_admin.email, note: body.note }); }
    catch (e) { if (!e.status && !/money_|currency_/.test(e.code || "")) throw e; return bad(res, e.message, e.status || 400); }
    audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "money.quarantine_resolve", "money_quarantine", String(id), { decision: out.amount, table: out.table, key: out.key, column: out.column, note: String(body.note || "") }, ipOf(req));
    json(res, 200, out);
  }

  return [
    ["GET /api/platform/money", apiPlatformMoney],
    ["POST /api/platform/money/quarantine/:id/resolve", (r, re, u, s, b, p) => apiPlatformMoneyResolve(r, re, u, s, b, p)]
  ];
} };
