/* LUXORA Platform — wallet domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the wallet domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "wallet", routes(kit) {
  const { T, Wal, actor, bad, byOf, fintech, idemOf, json, mods, offers, ownerFor, requireAdmin, requirePlatform, settings, shopperCall, signedIn, walletsOn } = kit;

  /* staff read an owner's statement lines and balance (the older single-balance view of the default wallet) */
  function apiWalletLedger(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    const owner = String(url.searchParams.get("owner") || (s.user_id ? ownerFor(s) : ""));
    json(res, 200, { owner, entries: offers.ledger(T(s), owner), balance: mods.walletBalance(T(s), owner) });
  }
  /* a signed-in shopper's wallets with their balances, and the definitions they may open */
  function apiWalletsMine(req, res, url, s) { if (walletsOn(s, res) && signedIn(s, res, "see your wallets")) shopperCall(res, () => ({ wallets: Wal().walletsOf(T(s), ownerFor(s)), definitions: Wal().definitions(T(s)).filter(d => d.spec.openable).map(d => ({ key: d.key, parent: d.parent, name: d.spec.name, aliases: d.spec.aliases, classes: d.spec.classes })) })); }
  /* a shopper opens a wallet of a definition, in a unit, named as they like */
  function apiWalletOpen(req, res, url, s, body) { if (walletsOn(s, res) && signedIn(s, res, "open a wallet")) shopperCall(res, () => ({ wallet: Wal().open(T(s), ownerFor(s), { definition: body.definition, unit: body.unit, name: body.name, lang: body.lang }, ownerFor(s)) })); }
  /* one of the shopper's wallets: its balances, its holds and every name it has had */
  function apiWalletGet(req, res, url, s, body, id) { if (walletsOn(s, res) && signedIn(s, res, "see a wallet")) shopperCall(res, () => ({ wallet: Wal().balances(T(s), ownerFor(s), id), holds: Wal().holds(T(s), ownerFor(s), id), names: Wal().names(id) })); }
  /* the movements of one of the shopper's wallets, newest first */
  function apiWalletStatement(req, res, url, s, body, id) { if (walletsOn(s, res) && signedIn(s, res, "see a statement")) shopperCall(res, () => ({ lines: Wal().statement(T(s), ownerFor(s), id, url.searchParams.get("limit")) })); }
  /* the shopper renames a wallet, or adds an alias, in a language */
  function apiWalletRename(req, res, url, s, body, id) { if (walletsOn(s, res) && signedIn(s, res, "rename a wallet")) shopperCall(res, () => ({ wallet: Wal().rename(T(s), ownerFor(s), id, { name: body.name, lang: body.lang, alias: !!body.alias }, ownerFor(s)) })); }
  /* the shopper moves value between two of their own wallets of one unit (Idempotency-Key) */
  function apiWalletTransfer(req, res, url, s, body) { if (walletsOn(s, res) && signedIn(s, res, "move value")) shopperCall(res, () => Wal().transfer(T(s), { owner: ownerFor(s), from: body.from, to: body.to, amount: body.amount, idem: idemOf(req, body), actor: ownerFor(s), ref: "self" })); }
  /* staff: an owner's wallets, a wallet's life, adjustments with a reason, reversals, definitions, verification */
  /* staff list an owner's wallets, with the wallet and hold actions */
  function apiAdminWallets(req, res, url, s) { if (requireAdmin(s, res) && walletsOn(s, res)) shopperCall(res, () => ({ wallets: Wal().walletsOf(T(s), String(url.searchParams.get("owner") || "")), ...Wal().vocabulary() })); }
  /* staff restrict, suspend, reactivate or close a wallet, with a reason */
  function apiAdminWalletMove(req, res, url, s, body, id) { if (requireAdmin(s, res) && walletsOn(s, res)) shopperCall(res, () => ({ wallet: Wal().move(T(s), id, body.action, byOf(s) || actor(s)[0], body.reason) })); }
  /* staff adjust a wallet up or down, with a reason (Idempotency-Key) */
  function apiAdminWalletAdjust(req, res, url, s, body, id) { if (requireAdmin(s, res) && walletsOn(s, res)) shopperCall(res, () => Wal().post(T(s), { op: "adjust", wallet: id, amount: body.amount, reason: body.reason, idem: idemOf(req, body), actor: byOf(s) || actor(s)[0], ref: "staff" })); }
  /* staff reverse a journal with a reason — a linked mirror, once */
  function apiAdminJournalReverse(req, res, url, s, body, id) { if (requireAdmin(s, res) && walletsOn(s, res)) shopperCall(res, () => ({ journal: Wal().reverse(T(s), id, byOf(s) || actor(s)[0], body.reason, idemOf(req, body)) })); }
  /* staff read any wallet of the store: balances, movements, holds and names */
  function apiAdminWalletStatement(req, res, url, s, body, id) { if (requireAdmin(s, res) && walletsOn(s, res)) shopperCall(res, () => ({ wallet: Wal().balances(T(s), null, id), lines: Wal().statement(T(s), null, id, url.searchParams.get("limit")), holds: Wal().holds(T(s), null, id), names: Wal().names(id) })); }
  /* the ledger check: unbalanced journals, drift between the log and the ledger, and the event chain */
  function apiAdminLedgerVerify(req, res, url, s) { if (requireAdmin(s, res)) shopperCall(res, () => Wal().verify(T(s))); }
  /* every wallet definition, resolved for this store, with the operations, accounts and settings declared */
  function apiWalletDefinitions(req, res, url, s) { shopperCall(res, () => ({ definitions: Wal().definitions(T(s)), ...Wal().vocabulary() })); }
  /* a store sets its own values for a definition's settings, over the platform's */
  function apiAdminWalletDefinitionSettings(req, res, url, s, body, key) { if (requireAdmin(s, res) && walletsOn(s, res)) shopperCall(res, () => ({ definition: Wal().define({ key, settings: body.settings || {} }, byOf(s) || actor(s)[0], { namespace: "tenant:" + T(s) }) })); }
  /* a store chooses the definition its owners' money lands in */
  function apiAdminWalletDefault(req, res, url, s, body) { if (requireAdmin(s, res) && walletsOn(s, res)) shopperCall(res, () => { Wal().chooseDefault(T(s), body.key, byOf(s) || actor(s)[0]); return { definitions: Wal().definitions(T(s)) }; }); }
  /* the platform declares a wallet definition, or changes one — only what it states is assigned, the rest inherited */
  function apiPlatformWalletDefine(req, res, url, s, body) { if (requirePlatform(s, res)) shopperCall(res, () => ({ definition: Wal().define(body, "platform:" + (s.platform_admin_id || s.user_id || "")) })); }
  /* one person sends value to another, wallet to wallet, as one transfer journal */
  function apiFinTransfer(req, res, url, s, body) {
    try { json(res, 200, fintech.transfer(T(s), ownerFor(s), String(body.to || ""), body.amount, body.note)); }
    catch (e) { bad(res, e.message); }
  }

  return [
    ["POST /api/fintech/transfer", apiFinTransfer],
    ["GET /api/wallet/ledger", apiWalletLedger],
    ["GET /api/wallets", apiWalletsMine],
    ["POST /api/wallets", apiWalletOpen],
    ["POST /api/wallets/transfer", apiWalletTransfer],
    ["GET /api/wallets/:id", (r, re, u, s, b, p) => apiWalletGet(r, re, u, s, b, p)],
    ["GET /api/wallets/:id/statement", (r, re, u, s, b, p) => apiWalletStatement(r, re, u, s, b, p)],
    ["POST /api/wallets/:id/name", (r, re, u, s, b, p) => apiWalletRename(r, re, u, s, b, p)],
    ["GET /api/wallet-definitions", apiWalletDefinitions],
    ["GET /api/admin/wallets", apiAdminWallets],
    ["GET /api/admin/wallets/:id", (r, re, u, s, b, p) => apiAdminWalletStatement(r, re, u, s, b, p)],
    ["POST /api/admin/wallets/:id/move", (r, re, u, s, b, p) => apiAdminWalletMove(r, re, u, s, b, p)],
    ["POST /api/admin/wallets/:id/adjust", (r, re, u, s, b, p) => apiAdminWalletAdjust(r, re, u, s, b, p)],
    ["POST /api/admin/journals/:id/reverse", (r, re, u, s, b, p) => apiAdminJournalReverse(r, re, u, s, b, p)],
    ["GET /api/admin/ledger/verify", apiAdminLedgerVerify],
    ["POST /api/platform/wallet-definitions", apiPlatformWalletDefine],
    ["POST /api/admin/wallet-definitions/:key", (r, re, u, s, b, p) => apiAdminWalletDefinitionSettings(r, re, u, s, b, p)],
    ["POST /api/admin/wallet-default", apiAdminWalletDefault]
  ];
} };
