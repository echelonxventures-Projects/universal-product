/* LUXORA Platform — STORE RBAC (facade over the ONE authorization engine).
 *
 * lib/authz.js is now the single engine: it owns both grant surfaces (store and
 * platform) and namespaces every grant by scope, because the two consoles share
 * thirty section keys and a merged surface would have collided silently. This
 * file keeps the store console's original call shapes alive — rbac.can(user,
 * section, mode, tenantId), rbac.grant(user, tenantId), the per-tenant staff
 * role CRUD — so every call site, test and stored staffRoles row resolves
 * exactly as before. Only the resolver that reads them was unified.
 *
 * The store's sections are the store console's NAV leaf keys (public/js/admin.js);
 * '*' expands to the store surface only, never the platform one. See authz.js. */
"use strict";

const authz = require("./authz.js");

/* the grant surface the store console renders — unchanged keys, one source */
/* read live: a configured app's section joins the surface the moment it exists */
const ROLES = authz.STORE_ROLES;

/* delegate the per-tenant staff-role store; store roles take a tenantId,
   platform roles do not, so only the store-shaped arity is forwarded here */
function seed() { authz.seedScope("store"); }
function roles(tenantId) { return authz.roles("store", tenantId); }
function role(tenantId, key) { return authz.role("store", tenantId, key); }
function upsertRole(tenantId, role) { return authz.upsertRole("store", tenantId, role); }
function deleteRole(tenantId, key) { return authz.deleteRole("store", tenantId, key); }

/* expand() had one surface; the store's is the store surface */
function expand(sections) { return authz.expandScope("store", sections || {}); }

/* a staff member's effective grants, in the store scope only. The tenant is what
   makes a role mean what THIS store says it means; the user row's own tenant_id
   is the fallback so the grant follows the account, not the caller's whim. */
function grant(user, tenantId) { return authz.storeGrants(user, tenantId); }
function allowedSections(user, tenantId) { return authz.allowedSections({ store: user, tenantId }, "store"); }
function can(user, section, mode, tenantId) { return authz.canScope({ store: user, tenantId }, "store", section, mode); }

module.exports = {
  get SECTIONS() { return authz.SURFACES.store; }, ROLES, seed, roles, role, upsertRole, deleteRole,
  grant, allowedSections, can, expand,
  sectionForEntity: authz.sectionForEntity, KEY_SECTION: authz.KEY_SECTION,
  hasOwnSet: authz.hasOwnSet, resetToDefault: authz.resetToDefault,
  J: authz.J, authz
};
