/* LUXORA Platform — customers domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the customers domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "customers", routes(kit) {
  const { T, all, bad, get, json, logAction, ownerFor, requireSection, rules, run } = kit;

  /* ---------------- address book ---------------- */
  function apiAddressList(req, res, url, s) {
    json(res, 200, { addresses: all("SELECT * FROM addresses WHERE tenant_id=? AND owner=? ORDER BY is_default DESC, id", T(s), ownerFor(s)) });
  }
  function apiAddressSave(req, res, url, s, body, id) {
    const name = String(body.name || "").trim(), address = String(body.address || "").trim(), city = String(body.city || "").trim();
    if (!name || !address || !city) return bad(res, "Name, address and city are required", 422);
    const label = String(body.label || "Home").slice(0, 40);
    const isDefault = body.is_default ? 1 : 0;
    if (isDefault) run("UPDATE addresses SET is_default=0 WHERE tenant_id=? AND owner=?", T(s), ownerFor(s));
    if (id) {
      const ex = get("SELECT id FROM addresses WHERE id=? AND tenant_id=? AND owner=?", Number(id), T(s), ownerFor(s));
      if (!ex) return bad(res, "Address not found", 404);
      run("UPDATE addresses SET label=?,name=?,address=?,city=?,state=?,zip=?,country=?,phone=?,is_default=? WHERE id=?",
        label, name, address, city, String(body.state || "").slice(0, 60), String(body.zip || "").slice(0, 20),
        String(body.country || "").slice(0, 2).toUpperCase(), String(body.phone || "").slice(0, 30), isDefault, Number(id));
    } else {
      run("INSERT INTO addresses(tenant_id,owner,label,name,address,city,state,zip,country,phone,is_default) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
        T(s), ownerFor(s), label, name, address, city, String(body.state || "").slice(0, 60), String(body.zip || "").slice(0, 20),
        String(body.country || "").slice(0, 2).toUpperCase(), String(body.phone || "").slice(0, 30), isDefault);
    }
    json(res, 200, { addresses: all("SELECT * FROM addresses WHERE tenant_id=? AND owner=? ORDER BY is_default DESC, id", T(s), ownerFor(s)) });
  }
  function apiAddressDel(req, res, url, s, body, id) {
    run("DELETE FROM addresses WHERE id=? AND tenant_id=? AND owner=?", Number(id), T(s), ownerFor(s));
    json(res, 200, { ok: true });
  }
  /* hand-assigned segment memberships, by the customer's email or their owner id */
  function apiAdminSegmentMemberAdd(req, res, url, s, body) {
    if (!requireSection(s, res, "applicability", "write", "applicability")) return;
    let owner = String(body && body.owner || "").trim();
    const email = String(body && body.email || "").trim().toLowerCase();
    if (email) { const u = get("SELECT id FROM users WHERE tenant_id=? AND lower(email)=?", T(s), email); if (!u) return bad(res, "No customer with that email on this platform", 404); owner = `t${T(s)}:u:${u.id}`; }
    if (!owner.startsWith("t" + T(s) + ":")) return bad(res, "owner must belong to this platform", 400);
    const r = rules.addMember(T(s), owner, body && body.segment);
    if (r.error) return bad(res, r.error, 400);
    logAction(s, "segment.member.add", "segment", String(body.segment), { owner }, req);
    json(res, 200, { ok: true, members: rules.members(T(s)) });
  }
  function apiAdminSegmentMemberDelete(req, res, url, s, body, id) {
    if (!requireSection(s, res, "applicability", "write", "applicability")) return;
    rules.removeMember(T(s), id);
    json(res, 200, { ok: true, members: rules.members(T(s)) });
  }

  return [
    ["GET /api/addresses", apiAddressList],
    ["POST /api/addresses", apiAddressSave],
    ["PUT /api/addresses/:id", (r, re, u, s, b, p) => apiAddressSave(r, re, u, s, b, p)],
    ["DELETE /api/addresses/:id", (r, re, u, s, b, p) => apiAddressDel(r, re, u, s, b, p)],
    ["POST /api/admin/segments/members", apiAdminSegmentMemberAdd],
    ["DELETE /api/admin/segments/members/:id", (r, re, u, s, b, p) => apiAdminSegmentMemberDelete(r, re, u, s, b, p)]
  ];
} };
