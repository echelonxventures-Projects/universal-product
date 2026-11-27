/* LUXORA Platform — books domain routes (lib/books.js; _registry/business-domains.json).
   A store's chart of accounts, its entries, and the reports read from them. Every route belongs
   to the store's books section (the Finance role holds it): a role reads them with a books read
   grant, and posts or reverses an entry, or adds an account, with a books write grant. */
"use strict";

module.exports = { domain: "books", routes(kit) {
  const { T, actor, bad, json, logAction, requireAdmin } = kit;
  const B = () => require("../books.js");
  const period = url => ({ from: url.searchParams.get("from") || "", to: url.searchParams.get("to") || "", currency: (url.searchParams.get("currency") || "").toUpperCase() });
  /* every handler: the books section's grant, then the answer or the reason it was refused */
  const answer = (s, res, fn) => { if (!requireAdmin(s, res)) return; try { fn(); } catch (e) { bad(res, e.message, e.status || 400); } };

  /* The store's chart of accounts — the platform's accounts and the store's own, each with its group and type — and the account types. */
  function apiBooksAccounts(req, res, url, s) { answer(s, res, () => json(res, 200, { accounts: B().accounts(T(s)), types: B().SEED.types })); }
  /* Adds one of the store's own accounts under a group (`parent`, `code`, `name`); it takes the group's type. */
  function apiBooksAccountAdd(req, res, url, s, body) { answer(s, res, () => { const a = B().define(T(s), body || {}, actor(s)); logAction(s, "books.account", "account", a.code, { name: a.name }); json(res, 200, { account: a }); }); }
  /* The latest entries, newest first, with their lines; `from`, `to` and `ref` (the record an entry came from) narrow them. */
  function apiBooksEntries(req, res, url, s) { answer(s, res, () => json(res, 200, { entries: B().entries(T(s), { ...period(url), ref: url.searchParams.get("ref") || "", limit: url.searchParams.get("limit") }) })); }
  /* Posts an accountant's entry: `memo`, `currency` and `lines` of `{ account, debit | credit }` that must balance. */
  function apiBooksEntryPost(req, res, url, s, body) { answer(s, res, () => { const e = B().manual(T(s), body || {}, actor(s)); logAction(s, "books.entry", "entry", e.id, { memo: e.memo }); json(res, 200, { entry: e }); }); }
  /* Reverses an entry with a `reason`: a mirror entry linked to it, allowed once; posted entries are never edited. */
  function apiBooksEntryReverse(req, res, url, s, body, id) { answer(s, res, () => { const e = B().reverse(T(s), id, actor(s), (body || {}).reason); logAction(s, "books.reverse", "entry", id, { reason: (body || {}).reason }); json(res, 200, { entry: e }); }); }
  /* The trial balance per currency over `from`–`to`: each account's debits, credits and balance, and the totals, which are equal. */
  function apiBooksTrialBalance(req, res, url, s) { answer(s, res, () => json(res, 200, { trialBalance: B().trialBalance(T(s), period(url)) })); }
  /* Profit and loss per currency over `from`–`to`: income, expenses and the profit. */
  function apiBooksProfitAndLoss(req, res, url, s) { answer(s, res, () => json(res, 200, { profitAndLoss: B().profitAndLoss(T(s), period(url)) })); }
  /* The balance sheet per currency `at` an instant: assets against liabilities, equity and earnings to date, which are equal. */
  function apiBooksBalanceSheet(req, res, url, s) { answer(s, res, () => json(res, 200, { balanceSheet: B().balanceSheet(T(s), { at: url.searchParams.get("at") || "" }) })); }
  /* One account's ledger over `from`–`to`: every entry that moved it, in order. */
  function apiBooksLedger(req, res, url, s, body, id) { answer(s, res, () => json(res, 200, { ledger: B().ledger(T(s), id, period(url)) })); }
  /* Whether the books are whole: payments and invoices not yet posted, and any entry that does not balance or match the tamper-evident log. */
  function apiBooksHealth(req, res, url, s) { answer(s, res, () => json(res, 200, B().health(T(s)))); }

  return [
    ["GET /api/admin/books/accounts", apiBooksAccounts],
    ["POST /api/admin/books/accounts", apiBooksAccountAdd],
    ["GET /api/admin/books/entries", apiBooksEntries],
    ["POST /api/admin/books/entries", apiBooksEntryPost],
    ["POST /api/admin/books/entries/:id/reverse", (r, re, u, s, b, p) => apiBooksEntryReverse(r, re, u, s, b, p)],
    ["GET /api/admin/books/trial-balance", apiBooksTrialBalance],
    ["GET /api/admin/books/profit-and-loss", apiBooksProfitAndLoss],
    ["GET /api/admin/books/balance-sheet", apiBooksBalanceSheet],
    ["GET /api/admin/books/accounts/:id/ledger", (r, re, u, s, b, p) => apiBooksLedger(r, re, u, s, b, p)],
    ["GET /api/admin/books/health", apiBooksHealth]
  ];
} };
