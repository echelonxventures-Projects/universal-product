/* LUXORA Platform — compliance domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the compliance domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "compliance", routes(kit) {
  const { T, actor, all, bad, compliance, consentSubject, events, fintech, ipOf, json, logAction, ownerFor, requireAdmin, stIs, states } = kit;

  /* ---------------- compliance & privacy (regulations as data) ---------------- */
  function apiAdminComplianceStatus(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, compliance.evaluate(T(s)));
  }
  function apiAdminComplianceCatalog(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { regulations: compliance.catalog(), controls: compliance.controlsFor(T(s)) });
  }
  function apiAdminComplianceControl(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const out = compliance.setControl(T(s), String(body.regulation || ""), String(body.control_id || ""),
      String(body.status || ""), body.evidence, s.platform_admin ? ("platform:" + s.platform_admin.email) : ("admin:" + s.user_id));
    logAction(s, "compliance.control", "compliance_controls", body.regulation + ":" + body.control_id, out, req);
    json(res, out.ok ? 200 : 400, out);
  }
  function apiAdminComplianceEvidence(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { evidence: compliance.evidenceFor(T(s), url.searchParams.get("regulation"), url.searchParams.get("control_id")) });
  }
  function apiConsentGet(req, res, url, s) {
    const asked = url.searchParams.get("subject");
    const subject = consentSubject(s, asked);
    if (asked && !subject) return bad(res, "You can only view your own consent", 403);
    if (!subject) return bad(res, "no subject in session", 401);
    json(res, 200, { subject, purposes: compliance.consentOf(T(s), subject) });
  }
  function apiConsentSet(req, res, url, s, body) {
    const asked = body && body.subject;
    const subject = consentSubject(s, asked);
    if (asked && !subject) return bad(res, "You can only change your own consent", 403);
    if (!subject) return bad(res, "no subject in session", 401);
    const out = compliance.grantConsent(T(s), subject, String(body.purpose || ""), {
      status: body.status, source: "api", ip: ipOf(req)
    });
    if (out.ok) logAction(s, "consent." + (stIs("consent", body.status, "withdrawal") ? "withdraw" : "grant"), "consent", subject + ":" + body.purpose, out, req);
    json(res, out.ok ? 200 : 400, out);
  }
  /* a data subject opens a rights request themselves (storefront) or an operator opens one */
  function apiPrivacyRequestOpen(req, res, url, s, body) {
    /* a person asks about their own data; only staff open a request for someone else */
    const asked = body && body.subject;
    const subject = asked ? consentSubject(s, asked) : ownerFor(s);
    if (asked && !subject) return bad(res, "You can only make a request about your own data", 403);
    if (!subject) return bad(res, "no subject in session", 401);
    const out = compliance.openRequest(T(s), subject, String(body.kind || require("../defaults.js").of("privacyRequestKinds")), { actor: s.platform_admin ? "platform" : (ownerFor(s) || "subject") });
    json(res, out.ok ? 200 : 400, out);
  }
  function apiAdminPrivacyRequests(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { requests: compliance.requestsFor(T(s)), states: compliance.REQUEST_STATES, kinds: compliance.REQUEST_KINDS });
  }
  function apiAdminPrivacyRequestTransition(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    const out = compliance.transitionRequest(T(s), String(id), String(body.status || ""), s.platform_admin ? ("platform:" + s.platform_admin.email) : ("admin:" + s.user_id), body.detail);
    logAction(s, "privacy.request", "privacy_requests", id, out, req);
    json(res, out.ok ? 200 : (out.code === 404 ? 404 : 409), out);
  }
  function apiAdminPrivacyRequestEvents(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    /* the request must belong to this store — events were read by request id alone */
    json(res, 200, { events: all("SELECT e.* FROM privacy_request_events e JOIN privacy_requests r ON CAST(r.id AS TEXT)=CAST(e.request_id AS TEXT) WHERE e.request_id=? AND r.tenant_id=? ORDER BY e.id", String(id), T(s)) });
  }
  function apiFinKycSubmit(req, res, url, s, body) {
    try { json(res, 200, { kyc: fintech.submitKyc(T(s), ownerFor(s), body) }); } catch (e) { bad(res, e.message); }
  }
  function apiFinKycVerify(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { kyc: fintech.verifyKyc(T(s), Number(id), body.level || "full", body.reject ? false : true) }); }
    catch (e) { bad(res, e.message); }
  }

  return [
    ["POST /api/fintech/kyc", apiFinKycSubmit],
    ["POST /api/fintech/kyc/:id/verify", (r, re, u, s, b, p) => apiFinKycVerify(r, re, u, s, b, p)],
    ["GET /api/admin/compliance/status", apiAdminComplianceStatus],
    ["GET /api/admin/compliance/catalog", apiAdminComplianceCatalog],
    ["POST /api/admin/compliance/control", apiAdminComplianceControl],
    ["GET /api/admin/compliance/evidence", apiAdminComplianceEvidence],
    ["GET /api/consent", apiConsentGet],
    ["POST /api/consent", apiConsentSet],
    ["POST /api/privacy/request", apiPrivacyRequestOpen],
    ["GET /api/admin/privacy/requests", apiAdminPrivacyRequests],
    ["POST /api/admin/privacy/requests/:id", (r, re, u, s, b, p) => apiAdminPrivacyRequestTransition(r, re, u, s, b, p)],
    ["GET /api/admin/privacy/requests/:id/events", (r, re, u, s, b, p) => apiAdminPrivacyRequestEvents(r, re, u, s, b, p)]
  ];
} };
