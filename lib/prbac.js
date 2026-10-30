/* LUXORA Platform — PLATFORM RBAC (facade over the ONE authorization engine).
 *
 * lib/authz.js is now the single engine: it owns both grant surfaces (store and
 * platform) and namespaces every grant by scope, because the two consoles share
 * thirty section keys and a merged surface would have collided silently. This
 * file keeps the platform console's original call shapes alive — prbac.can(admin,
 * section, mode), prbac.grant(admin), the global operator-role CRUD — so every
 * call site, test and stored platformRoles row resolves exactly as before. Only
 * the resolver that read them was unified.
 *
 * The platform's sections are the platform console's NAV leaf keys
 * (public/js/platform.js); '*' expands to the platform surface only. See authz.js. */
"use strict";

const authz = require("./authz.js");

/* read live: a configured app's section joins the surface the moment it exists */
const ROLES = authz.PLATFORM_ROLES;
const PBAC_STAMP = authz.STAMP.platform;

/* platform roles are GLOBAL (one row, no tenant) — the store's per-tenant arity
   is not forwarded here, so the two shapes cannot be crossed by accident */
function seed() { authz.seedScope("platform"); }
function roles() { return authz.roles("platform", 0); }
function role(key) { return authz.role("platform", 0, key); }
function upsertRole(role) { return authz.upsertRole("platform", 0, role); }
function deleteRole(key) { return authz.deleteRole("platform", 0, key); }

function expand(sections) { return authz.expandScope("platform", sections || {}); }

/* an operator's effective grants, in the platform scope only. A platform role
   can never produce a store:* grant — that is the invariant that makes it safe
 * for one person to hold both authorities in the merged console. */
function grant(admin) { return authz.platformGrants(admin); }
function allowedSections(admin) { return authz.allowedSections({ platform: admin }, "platform"); }
function can(admin, section, mode) { return authz.canScope({ platform: admin }, "platform", section, mode); }

module.exports = {
  get SECTIONS() { return authz.SURFACES.platform; }, ROLES, PBAC_STAMP, seed, roles, role, upsertRole, deleteRole,
  grant, allowedSections, can, expand,
  sectionForRoute: authz.sectionForRoute, J: authz.J, authz
};
