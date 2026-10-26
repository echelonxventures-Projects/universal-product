/* LUXORA Platform — the grant registry: where a thing granted is issued.

   An incentive can grant a coupon, a voucher, a gift card, a membership tier, an asset. Each
   of those is a different domain, and each domain knows how to issue its own thing. The
   incentive kernel does not: it names the kind of grant and asks this registry for the writer
   that owns it.

   This is a shared registry with no dependencies of its own — the same shape as
   lib/lineterms.js — so a domain can register its writer without any of them depending on
   each other. Registering is idempotent: the last registration of a kind wins, so a domain
   that is reloaded (a test, a re-seed) does not leave two writers behind.

   Two kinds of registration live here:
     grant   the writer for a kind of grant ("coupon", "voucher", "gift_card")
     handler the math for an offer type ("gift_card_issue", "voucher_issue") — the one
              offers engine that every surface calls asks this registry for its handlers */
"use strict";

const GRANTS = new Map();
const HANDLERS = new Map();

/* the writer for a kind of grant */
function registerGrant(kind, fn) {
  if (typeof fn === "function") GRANTS.set(String(kind), fn);
  return GRANTS.size;
}
/* the math for an offer type */
function registerHandler(type, fn) {
  if (typeof fn === "function") HANDLERS.set(String(type), fn);
  return HANDLERS.size;
}
/* ask the writer that owns this kind; undefined when no domain owns it, and the caller
   issues it generically instead */
function grantTo(kind, tenantId, owner, grant, src) {
  const fn = GRANTS.get(String(kind == null ? "" : kind));
  if (!fn) return undefined;
  return fn(tenantId, owner, grant || {}, src || {});
}
/* every registered offer-type handler, for the one offers engine */
function handlers() { return HANDLERS; }
function grants() { return GRANTS; }

module.exports = { registerGrant, registerHandler, grantTo, handlers, grants };
