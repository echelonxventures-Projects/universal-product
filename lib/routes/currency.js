/* LUXORA Platform — currency domain routes (_registry/business-domains.json `currency`).
   Money at rest (lib/money-store.js): the platform's reconciliation of every payment-spine
   amount, and the amounts the money migration could not convert — each resolved by an operator
   with a recorded decision, never guessed. The governed money policy (lib/money-policy.js):
   drafted, validated, previewed, approved by a second operator, published and rolled back, each
   step by a holder of the policy section's write grant and each audited. What it needs from the
   shared HTTP kit (lib/api.js) is passed in as `kit`. */
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

  /* ---------- the money policy ---------- */
  const MP = () => require("../money-policy.js");
  const section = () => MP().SEED.section;
  /* a policy refusal (invalid, stale, past, unknown) or a lifecycle refusal is the caller's to
     fix; anything else is a fault and propagates */
  const policyCall = (res, fn) => {
    try { return fn(); }
    catch (e) { if (!e.status) throw e; bad(res, e.message, e.status); return undefined; }
  };
  function apiMoneyPolicy(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    json(res, 200, MP().overview());
  }
  function apiMoneyPolicyVersion(req, res, url, s, body, ref) {
    if (!requirePlatform(s, res)) return;
    const out = policyCall(res, () => MP().lookup(ref));
    if (out) json(res, 200, out);
  }
  function apiMoneyPolicyDraft(req, res, url, s, body) {
    if (!requirePlatformSection(s, res, section(), "write")) return;
    const out = policyCall(res, () => MP().propose(body || {}, s.platform_admin.email));
    if (!out) return;
    audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "money.policy_drafted", "money_policy_change", String(out.id), { proposed: out.proposed, validFrom: out.validFrom, basedOn: out.basedOn }, ipOf(req));
    json(res, 200, out);
  }
  /* each lifecycle step: the policy section's write grant; approving also carries the kernel's
     approve permission, and the kernel refuses an approval by the change's own author */
  const STEPS = {
    validate: (id, who) => MP().validate(id, who),
    preview: (id, who, body) => MP().preview(id, body, who),
    approve: (id, who) => MP().approve(id, who, [require("../kernel.js").SEED.lifecycle.approvePermission]),
    publish: (id, who) => MP().publish(id, who),
    rollback: (id, who) => MP().rollback(id, who),
    discard: (id, who) => MP().discard(id, who)
  };
  function apiMoneyPolicyStep(step, req, res, url, s, body, id) {
    if (!requirePlatformSection(s, res, section(), "write")) return;
    const out = policyCall(res, () => STEPS[step](Number(id), s.platform_admin.email, body || {}));
    if (!out) return;
    if (step !== "preview") audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "money.policy_" + step, "money_policy_change", String(id), { state: (out.change || out).state, policy: out.policy ? out.policy.ref : undefined }, ipOf(req));
    json(res, 200, out);
  }

  return [
    ["GET /api/platform/money/policy", apiMoneyPolicy],
    ["GET /api/platform/money/policy/versions/:id", (r, re, u, s, b, p) => apiMoneyPolicyVersion(r, re, u, s, b, p)],
    ["POST /api/platform/money/policy/changes", apiMoneyPolicyDraft],
    ["POST /api/platform/money/policy/changes/:id/validate", (r, re, u, s, b, p) => apiMoneyPolicyStep("validate", r, re, u, s, b, p)],
    ["POST /api/platform/money/policy/changes/:id/preview", (r, re, u, s, b, p) => apiMoneyPolicyStep("preview", r, re, u, s, b, p)],
    ["POST /api/platform/money/policy/changes/:id/approve", (r, re, u, s, b, p) => apiMoneyPolicyStep("approve", r, re, u, s, b, p)],
    ["POST /api/platform/money/policy/changes/:id/publish", (r, re, u, s, b, p) => apiMoneyPolicyStep("publish", r, re, u, s, b, p)],
    ["POST /api/platform/money/policy/changes/:id/rollback", (r, re, u, s, b, p) => apiMoneyPolicyStep("rollback", r, re, u, s, b, p)],
    ["POST /api/platform/money/policy/changes/:id/discard", (r, re, u, s, b, p) => apiMoneyPolicyStep("discard", r, re, u, s, b, p)],
    ["GET /api/platform/money", apiPlatformMoney],
    ["POST /api/platform/money/quarantine/:id/resolve", (r, re, u, s, b, p) => apiPlatformMoneyResolve(r, re, u, s, b, p)]
  ];
} };
