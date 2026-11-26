/* LUXORA Platform — access domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the access domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "access", routes(kit) {
  const { T, _userRow, all, appInfo, authz, bad, branding, crypto, get, json, logAction, newUser, platformSections, policies, prbac, rbac, requireAdmin, requirePlatform, requirePlatformSection, requireSection, run, storeSections } = kit;

  /* the platform role catalog + the caller's own grants — the console reads this to
     filter its nav and to render the role picker. Owner-only writes stay open to every
     admin so a role can never lock the console's own user management. */
  function apiPlatformRoles(req, res, url, s) {
    if (!requirePlatformSection(s, res, "padmins", "read")) return;
    json(res, 200, { roles: prbac.roles(), sections: platformSections(), apps: authz.configuredApps().filter(a => !a.tenant_id).map(appInfo), me: { admin: s.platform_admin, allowed: prbac.allowedSections(s.platform_admin) } });
  }
  /* ---------- role management ----------
     Both grant surfaces the platform enforces are DATA in meta_lists, so defining a role
     and its rights is a console operation, never a deploy. One pair of handlers per
     surface, sharing a shape: the platform surface ('roles') governs this console's own
     operators (prbac); the staff surface ('roles/staff') governs every store's team
     (rbac). Both write through the engines, which validate against that surface's own
     section list and stamp the row edited so the seed's self-heal never reverts an
     operator's intent. Gated on roles:write — reading is the padmins read grant the
     console already needed, writing the roles themselves is a distinct trust. */
  function apiPlatformRoleSave(req, res, url, s, body) {
    if (!requirePlatformSection(s, res, "roles", "write")) return;
    const r = prbac.upsertRole(body || {});
    if (!r.ok) return bad(res, (r.fails || []).join("; "), 400);
    logAction(s, "platform.role.save", "role", r.role.key, { name: r.role.name });
    json(res, 200, { ok: true, role: r.role, roles: prbac.roles() });
  }
  function apiPlatformRoleDelete(req, res, url, s, body, key) {
    if (!requirePlatformSection(s, res, "roles", "write")) return;
    const r = prbac.deleteRole(key);
    if (!r.ok) return bad(res, (r.fails || []).join("; "), 400);
    logAction(s, "platform.role.delete", "role", key, {});
    json(res, 200, { ok: true, roles: prbac.roles() });
  }
  /* the store-staff surface. Each store may carry its OWN role set (rbac 'staffRoles:t<id>'),
     so the platform console edits the set the selected store actually enforces: name a store
     in the body to fork/edit that store's set, or omit it to edit the shared default every
     un-forked store inherits. rbac.upsertRole takes (tenantId, role) — the store first, the
     role second — and the first save to a store forks the full inherited set, so a store
     never starts empty. */
  function apiStaffRoleSave(req, res, url, s, body) {
    if (!requirePlatformSection(s, res, "roles", "write")) return;
    const tid = body && body.tenant_id ? Number(body.tenant_id) : 0;
    if (tid && !get("SELECT id FROM tenants WHERE id=?", tid)) return bad(res, "Unknown store", 400);
    const r = rbac.upsertRole(tid, body || {});
    if (!r.ok) return bad(res, (r.fails || []).join("; "), 400);
    logAction(s, "platform.role.save", tid ? "staffRole:t" + tid : "staffRole", r.role.key, { name: r.role.name, tenant_id: tid || null });
    json(res, 200, { ok: true, role: r.role, roles: rbac.roles(tid), tenant_id: tid || null, ownSet: tid ? true : false });
  }
  function apiStaffRoleDelete(req, res, url, s, body, key) {
    if (!requirePlatformSection(s, res, "roles", "write")) return;
    const tid = body && body.tenant_id ? Number(body.tenant_id) : 0;
    if (tid && !get("SELECT id FROM tenants WHERE id=?", tid)) return bad(res, "Unknown store", 400);
    const r = rbac.deleteRole(tid, key);
    if (!r.ok) return bad(res, (r.fails || []).join("; "), 400);
    logAction(s, "platform.role.delete", tid ? "staffRole:t" + tid : "staffRole", key, { tenant_id: tid || null });
    json(res, 200, { ok: true, roles: rbac.roles(tid) });
  }
  /* ---------- team & roles (RBAC) ---------- */
  /* the store console reads ITS OWN role set (rbac.roles(tenant)) — a store that forked
     the platform default edits what it forked, and a store that never forked reads the
     inherited default through the same call. hasOwnSet tells the console which it is
     looking at, so the "reset to platform default" control only appears when there is a
     fork to undo. */
  function apiRoles(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { roles: rbac.roles(T(s)), defaultRole: require("../defaults.js").of("staffRoles"), sections: storeSections(T(s)), apps: authz.appsFor(T(s)).map(appInfo), ownSet: rbac.hasOwnSet(T(s)),
      me: { user: _userRow(s), allowed: rbac.allowedSections(_userRow(s), T(s)) } });
  }
  /* a store defines and re-scopes its OWN roles from its own console — the per-tenant
     fork. The first save forks the full inherited set (the store keeps every role it had
     and diverges from there), and a fork can be dissolved back to the platform default.
     Gated on team:write: scoping who on this team may do what is the team trust. */
  function apiRoleSave(req, res, url, s, body) {
    if (!requireSection(s, res, "team", "write")) return;
    const r = rbac.upsertRole(T(s), body || {});
    if (!r.ok) return bad(res, (r.fails || []).join("; "), 400);
    logAction(s, "staff.role.save", "role", r.role.key, { name: r.role.name }, req);
    json(res, 200, { ok: true, role: r.role, roles: rbac.roles(T(s)), ownSet: true });
  }
  function apiRoleDelete(req, res, url, s, body, key) {
    if (!requireSection(s, res, "team", "write")) return;
    const r = rbac.deleteRole(T(s), key);
    if (!r.ok) return bad(res, (r.fails || []).join("; "), 400);
    logAction(s, "staff.role.delete", "role", key, {}, req);
    json(res, 200, { ok: true, roles: rbac.roles(T(s)) });
  }
  /* dissolve this store's fork back to the shared platform default */
  function apiRoleReset(req, res, url, s) {
    if (!requireSection(s, res, "team", "write")) return;
    const r = rbac.resetToDefault(T(s));
    if (!r.ok) return bad(res, (r.fails || []).join("; "), 400);
    logAction(s, "staff.role.reset", "roles", T(s), {}, req);
    json(res, 200, { ok: true, roles: rbac.roles(T(s)), ownSet: false });
  }
  function apiStaffList(req, res, url, s) {
    if (!requireAdmin(s, res)) return; if (!requireSection(s, res, "team", "read")) return;
    json(res, 200, { staff: all("SELECT id,name,email,role,staff_role,disabled,last_login,created_at FROM users WHERE tenant_id=? AND role='admin' ORDER BY id", T(s)) });
  }
  function apiStaffCreate(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return; if (!requireSection(s, res, "team", "write")) return;
    const email = String(body.email || "").toLowerCase().trim(); if (!email || !body.name) return bad(res, "name and email required");
    if (rbac.role(T(s), body.staff_role || require("../defaults.js").of("staffRoles")) === null) return bad(res, "Unknown role");
    const existing = get("SELECT id FROM users WHERE tenant_id=? AND email=?", T(s), email);
    const pw = String(body.password || crypto.randomBytes(9).toString("hex"));
    let id;
    if (existing) { require("../parties.js").set(existing.id, { name: String(body.name), role: "admin", staff_role: body.staff_role || require("../defaults.js").of("staffRoles"), disabled: 0 }, "staff:" + s.user_id); id = existing.id; }
    else id = newUser(T(s), String(body.name), email, pw, "admin");
    require("../parties.js").set(id, { staff_role: body.staff_role || require("../defaults.js").of("staffRoles") }, "staff:" + s.user_id);
    run("UPDATE users SET perms=? WHERE id=?", JSON.stringify(body.perms || {}), id);
    logAction(s, "staff.create", "user", id, { email, role: body.staff_role || require("../defaults.js").of("staffRoles") }, req);
    json(res, 200, { ok: true, id, generated: !existing && !body.password ? pw : undefined });
  }
  function apiStaffUpdate(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return; if (!requireSection(s, res, "team", "write")) return;
    const u = get("SELECT id FROM users WHERE id=? AND tenant_id=? AND role='admin'", Number(id), T(s)); if (!u) return bad(res, "Not found", 404);
    if (Number(id) === Number(s.user_id) && body.disabled) return bad(res, "You cannot disable your own account");
    /* no self-promotion, and only an owner assigns or edits the owner role */
    if (Number(id) === Number(s.user_id) && (body.staff_role != null || body.perms != null)) return bad(res, "You cannot change your own role or permissions", 403);
    const me = get("SELECT staff_role FROM users WHERE id=?", s.user_id) || {};
    const target = get("SELECT staff_role FROM users WHERE id=?", u.id) || {};
    if ((me.staff_role || "owner") !== "owner" && (body.staff_role === "owner" || (target.staff_role || "owner") === "owner" || body.perms != null))
      return bad(res, "Only an owner can grant the owner role or custom permissions", 403);
    if (body.staff_role != null) { if (!rbac.role(T(s), body.staff_role)) return bad(res, "Unknown role"); require("../parties.js").set(u.id, { staff_role: body.staff_role }, "staff:" + s.user_id); }
    if (body.perms != null) run("UPDATE users SET perms=? WHERE id=?", JSON.stringify(body.perms), u.id);
    if (body.disabled != null) require("../parties.js").set(u.id, { disabled: body.disabled ? 1 : 0 }, "staff:" + s.user_id);
    if (body.disabled) run("UPDATE sessions SET user_id=NULL WHERE user_id=?", u.id);
    logAction(s, "staff.update", "user", id, { role: body.staff_role, disabled: body.disabled }, req);
    json(res, 200, { ok: true });
  }
  function apiStaffDelete(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return; if (!requireSection(s, res, "team", "write")) return;
    if (Number(id) === Number(s.user_id)) return bad(res, "Cannot remove yourself");
    const admins = get("SELECT COUNT(*) c FROM users WHERE tenant_id=? AND role='admin' AND disabled=0", T(s)).c;
    if (admins <= 1) return bad(res, "A store must keep at least one active admin");
    if (get("SELECT id FROM users WHERE id=? AND tenant_id=? AND role='admin'", Number(id), T(s))) require("../parties.js").set(Number(id), { disabled: 1 }, "staff:" + s.user_id);
    /* removal takes effect now, not when the removed person's session expires */
    run("UPDATE sessions SET user_id=NULL WHERE user_id=?", Number(id));
    logAction(s, "staff.disable", "user", id, {}, req); json(res, 200, { ok: true });
  }
  function apiPlatformBrandingPerms(req, res, url, s, body) {
    body = body || {};
    if (!requirePlatform(s, res)) return;
    const tenantId = url.pathname.match(/\/branding-permissions\/(\d+)/)?.[1];
    if (!tenantId) return bad(res, 'tenant_id required', 400);
    if (req.method === 'GET') return json(res, 200, { perms: branding.getStorePermissions(tenantId) });
    if (req.method === 'PUT') return json(res, 200, { perms: branding.setStorePermissions(tenantId, body) });
    return bad(res, 'Method not allowed', 405);
  }
  /* ========== Dynamic Policy Management APIs ========== */
  function apiPlatformPolicies(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    if (req.method === 'GET') return json(res, 200, { policies: policies.getPolicies() });
    return bad(res, 'Method not allowed', 405);
  }
  function apiPlatformPolicy(req, res, url, s, body) {
    if (!requirePlatformSection(s, res, "policies", req.method === "GET" ? "read" : "write")) return;
    const category = url.pathname.match(/\/policies\/([^.]+)/)?.[1];
    if (!category) return bad(res, 'category required', 400);
    if (req.method === 'GET') return json(res, 200, { policy: policies.getPolicy(category) });
    if (req.method === 'PUT') { const result = policies.setPolicy(category, body || {}); return json(res, 200, { policy: result }); }
    if (req.method === 'DELETE') { const result = policies.deletePolicy(category); if (!result.ok) return bad(res, result.error, 404); return json(res, 200, result); }
    return bad(res, 'Method not allowed', 405);
  }

  return [
    ["GET /api/admin/roles", apiRoles],
    ["POST /api/admin/roles", apiRoleSave],
    ["DELETE /api/admin/roles/:key", (r, re, u, s, b, p) => apiRoleDelete(r, re, u, s, b, p)],
    ["POST /api/admin/roles/reset", apiRoleReset],
    ["GET /api/admin/staff", apiStaffList],
    ["POST /api/admin/staff", apiStaffCreate],
    ["PUT /api/admin/staff/:id", (r, re, u, s, b, p) => apiStaffUpdate(r, re, u, s, b, p)],
    ["DELETE /api/admin/staff/:id", (r, re, u, s, b, p) => apiStaffDelete(r, re, u, s, b, p)],
    ["GET /api/platform/branding-permissions/:id", apiPlatformBrandingPerms],
    ["GET /api/platform/policies", apiPlatformPolicies],
    ["GET /api/platform/policies/:category", apiPlatformPolicy],
    ["PUT /api/platform/policies/:category", apiPlatformPolicy],
    ["DELETE /api/platform/policies/:category", apiPlatformPolicy],
    ["PUT /api/platform/branding-permissions/:id", apiPlatformBrandingPerms],
    ["GET /api/platform/roles", apiPlatformRoles],
    ["POST /api/platform/roles", apiPlatformRoleSave],
    ["DELETE /api/platform/roles/:key", (r, re, u, s, b, p) => apiPlatformRoleDelete(r, re, u, s, b, p)],
    ["POST /api/platform/roles/staff", apiStaffRoleSave],
    ["DELETE /api/platform/roles/staff/:key", (r, re, u, s, b, p) => apiStaffRoleDelete(r, re, u, s, b, p)]
  ];
} };
