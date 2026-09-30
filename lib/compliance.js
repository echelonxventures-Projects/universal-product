/* LUXORA Platform — Compliance-as-Data: named regulations, control framework, evidence,
   privacy & consent, and data-subject rights.
   --------------------------------------------------------------------------
   The corpus declares a COMPLIANCE UNIVERSE whose items are the regulations themselves
   (GDPR · CCPA · DPDP · HIPAA · PCI-DSS · SOC 2 · ISO 27001 · NIST · FedRAMP · SEBI ·
   RBI · TRAI · future). Before this engine those names existed nowhere in the runtime —
   the platform had a generic `compliance_records` table but no regulation was modeled, so
   "continuous compliance validation" was impossible to even ask about.

   Everything here is DATA: the regulation catalog, its control set, the consent purposes
   and the request lifecycle are meta_lists registries + rows, so an operator adds a
   regulation or a control in the console and the platform enforces it with no code change.
   The engine is a pure evaluator over those rows — it holds no regulation name in a branch.

   Two concerns:
     compliance  — per-tenant control status + evidence → a regulation verdict
                   (satisfied / partial / violated / not-applicable), computed, never asserted
     privacy     — consent per subject+purpose (the lawful-basis record), plus a
                   data-subject-rights request workflow (access · erasure · portability ·
                   rectification) with an append-only state machine, and retention windows
                   that schedule erasure when a consent is withdrawn. */
"use strict";

const db = () => require("./db.js");
const crypto = require("crypto");

/* ---------- the seeded regulation catalog ----------
   Each regulation declares the controls that constitute it. A control is a named
   obligation the platform can evidence (e.g. PCI-DSS "cardholder data encrypted at rest" →
   the security L3 envelope). The seed is a floor, not a ceiling: an operator adds rows in
   Data Studio and a new regulation is enforceable immediately. */
const REGULATIONS = [
  { key: "gdpr", name: "GDPR", jurisdiction: "EU", kind: "privacy",
    desc: "General Data Protection Regulation — lawful processing, consent, data-subject rights",
    controls: [
      { id: "gdpr-6.1", name: "Lawful basis recorded for each processing purpose", evidence: "consent registry" },
      { id: "gdpr-7.1", name: "Consent captured, withdrawable, and honored on withdrawal", evidence: "consent ledger" },
      { id: "gdpr-15.1", name: "Data-subject access requests fulfilled within the deadline", evidence: "privacy request workflow" },
      { id: "gdpr-17.1", name: "Erasure executed on lawful request or retention expiry", evidence: "erasure ledger" },
      { id: "gdpr-32.1", name: "Personal data encrypted at rest and in transit", evidence: "security L3/L6 envelope" }] },
  { key: "ccpa", name: "CCPA", jurisdiction: "US-CA", kind: "privacy",
    desc: "California Consumer Privacy Act — notice, opt-out of sale, deletion rights",
    controls: [
      { id: "ccpa-1798.100", name: "Notice at collection published", evidence: "privacy policy record" },
      { id: "ccpa-1798.105", name: "Deletion requests honored", evidence: "erasure ledger" },
      { id: "ccpa-1798.120", name: "Opt-out of sale / sharing enforced", evidence: "consent ledger" }] },
  { key: "dpdp", name: "DPDP", jurisdiction: "IN", kind: "privacy",
    desc: "Digital Personal Data Protection Act (India) — consent, data-principal rights",
    controls: [
      { id: "dpdp-6", name: "Consent obtained for a specified, lawful purpose", evidence: "consent ledger" },
      { id: "dpdp-11", name: "Data-principal rights (access, correction, erasure) actionable", evidence: "privacy request workflow" },
      { id: "dpdp-8.5", name: "Data breaches notified to the authority", evidence: "incident log" }] },
  { key: "hipaa", name: "HIPAA", jurisdiction: "US", kind: "health",
    desc: "Health Insurance Portability and Accountability Act — PHI safeguards",
    controls: [
      { id: "hipaa-164.312.a", name: "Access to PHI controlled and audited", evidence: "audit chain" },
      { id: "hipaa-164.312.e", name: "PHI encrypted in transit and at rest", evidence: "security L3/L6 envelope" },
      { id: "hipaa-164.530.c", name: "Audit controls record PHI access", evidence: "audit chain" }] },
  { key: "pci-dss", name: "PCI-DSS", jurisdiction: "global", kind: "payments",
    desc: "Payment Card Industry Data Security Standard — cardholder data protection",
    controls: [
      { id: "pci-3.4", name: "Cardholder data rendered unreadable wherever stored", evidence: "tokenization + envelope" },
      { id: "pci-4.1", name: "Strong cryptography on transmission over open networks", evidence: "TLS config" },
      { id: "pci-10.1", name: "Audit trails for all access to cardholder data", evidence: "audit chain" },
      { id: "pci-12.3", name: "Payment gateway credentials sealed, not logged", evidence: "sealed gateway config" }] },
  { key: "soc2", name: "SOC 2", jurisdiction: "global", kind: "assurance",
    desc: "System and Organization Controls — trust services criteria",
    controls: [
      { id: "soc2-cc6.1", name: "Logical and physical access controls", evidence: "RBAC + audit chain" },
      { id: "soc2-cc7.1", name: "System monitoring and anomaly detection", evidence: "monitoring + audit" },
      { id: "soc2-cc8.1", name: "Change management with approvals", evidence: "audit chain" }] },
  { key: "iso27001", name: "ISO 27001", jurisdiction: "global", kind: "assurance",
    desc: "Information security management system controls",
    controls: [
      { id: "iso-a.5.15", name: "Access control policy enforced", evidence: "RBAC" },
      { id: "iso-a.5.34", name: "Privacy and protection of PII", evidence: "consent + retention" },
      { id: "iso-a.8.16", name: "Monitoring and logging of activities", evidence: "audit chain" }] },
  { key: "nist", name: "NIST CSF", jurisdiction: "US", kind: "framework",
    desc: "NIST Cybersecurity Framework — identify, protect, detect, respond, recover",
    controls: [
      { id: "nist-pr.ac", name: "Identity management and access control", evidence: "RBAC + sessions" },
      { id: "nist-pr.ds", name: "Data security at rest and in transit", evidence: "security envelope" },
      { id: "nist-de.ae", name: "Adverse event detection", evidence: "risk + anomaly signals" }] },
  { key: "fedramp", name: "FedRAMP", jurisdiction: "US", kind: "government",
    desc: "Federal Risk and Authorization Management Program — cloud service baseline",
    controls: [
      { id: "fedramp-ac", name: "Access control and separation of duties", evidence: "RBAC + roles" },
      { id: "fedramp-au", name: "Audit logging, protection and review", evidence: "hash-chained audit" },
      { id: "fedramp-sc", name: "System and communications protection", evidence: "TLS + envelope" }] },
  { key: "sebi", name: "SEBI", jurisdiction: "IN", kind: "financial",
    desc: "Securities and Exchange Board of India — market intermediary obligations",
    controls: [
      { id: "sebi-kyc", name: "KYC completed before granting credit or market access", evidence: "KYC gate" },
      { id: "sebi-audit", name: "Transaction audit trail retained and immutable", evidence: "audit chain" }] },
  { key: "rbi", name: "RBI", jurisdiction: "IN", kind: "financial",
    desc: "Reserve Bank of India — payment data storage and tokenization directives",
    controls: [
      { id: "rbi-tokenization", name: "Card data tokenized; raw PAN not stored", evidence: "tokenization" },
      { id: "rbi-storage", name: "Payment data localisation and retention limits", evidence: "retention config" }] },
  { key: "trai", name: "TRAI", jurisdiction: "IN", kind: "telecom",
    desc: "Telecom Regulatory Authority of India — commercial communication consent",
    controls: [
      { id: "trai-consent", name: "Marketing communication sent only with registered consent", evidence: "consent ledger" },
      { id: "trai-pref", name: "Preference registry honored for marketing channels", evidence: "consent purposes" }] }
];

/* the lawful-basis / purpose vocabulary — an operator extends this to add a purpose, and
   every consent and marketing send keys off it */
const PURPOSES = [
  { key: "order", name: "Order fulfilment", lawful: "contract", retention_days: 2555, required: true,
    desc: "Processing required to fulfil a purchase (Art. 6(1)(b) equivalent)" },
  { key: "payments", name: "Payments & billing", lawful: "contract", retention_days: 2555, required: true,
    desc: "Payment processing, invoicing and reconciliation" },
  { key: "shipping", name: "Shipping & delivery", lawful: "contract", retention_days: 365, required: true,
    desc: "Delivery, tracking and returns logistics" },
  { key: "support", name: "Customer support", lawful: "contract", retention_days: 1095, required: false,
    desc: "Tickets, correspondence and service history" },
  { key: "marketing", name: "Marketing & promotions", lawful: "consent", retention_days: 730, required: false,
    desc: "Campaigns, offers and newsletters — opt-in, withdrawable at any time" },
  { key: "analytics", name: "Analytics & personalization", lawful: "consent", retention_days: 730, required: false,
    desc: "Behavioural analytics, recommendations and experiments" },
  { key: "fraud", name: "Fraud prevention & security", lawful: "legitimate_interest", retention_days: 1095, required: true,
    desc: "Risk screening and security monitoring" },
  { key: "legal", name: "Legal & regulatory records", lawful: "legal_obligation", retention_days: 2555, required: true,
    desc: "Audit trail and records the law requires the platform to keep" }
];

/* the data-subject-rights request lifecycle — a state machine the corpus's own
   domain grammar describes; the states are a registry row, so a jurisdiction that adds a
   review step inserts a state with no code change */
const REQUEST_STATES = ["received", "verified", "in_progress", "fulfilled", "rejected", "closed"];
const REQUEST_KINDS = [
  { key: "access", name: "Data access", deadline_days: 30 },
  { key: "erasure", name: "Erasure (right to be forgotten)", deadline_days: 30 },
  { key: "portability", name: "Data portability", deadline_days: 30 },
  { key: "rectification", name: "Rectification", deadline_days: 30 },
  { key: "objection", name: "Objection to processing", deadline_days: 30 }
];

function seed() {
  const D = db();
  const putList = (name, label, items, from) => {
    const ex = D.get("SELECT items FROM meta_lists WHERE name=?", name);
    const cur = ex ? JSON.parse(ex.items || "[]") : [];
    for (const it of items) if (!cur.some(x => (x.key || x) === (it.key || it))) cur.push(it);
    if (ex) D.run("UPDATE meta_lists SET items=? WHERE name=?", JSON.stringify(cur), name);
    else D.run("INSERT INTO meta_lists(name,label,items,seeded_from) VALUES(?,?,?,?)", name, label, JSON.stringify(cur), from || "comp_v1");
  };
  putList("regulations", "Compliance · Regulations", REGULATIONS.map(r => ({ key: r.key, name: r.name, jurisdiction: r.jurisdiction, kind: r.kind, desc: r.desc })));
  putList("privacyPurposes", "Privacy · Processing purposes", PURPOSES.map(p => ({ key: p.key, name: p.name, lawful: p.lawful, retention_days: p.retention_days, required: !!p.required, desc: p.desc })));
  putList("privacyRequestStates", "Privacy · Request states", REQUEST_STATES.map(s => ({ key: s, name: s })));
  putList("privacyRequestKinds", "Privacy · Request kinds", REQUEST_KINDS.map(k => ({ key: k.key, name: k.name, deadline_days: k.deadline_days })));
  putList("controlStatuses", "Compliance · Control statuses", [
    { key: "satisfied", name: "Satisfied" }, { key: "partial", name: "Partially satisfied" },
    { key: "violated", name: "Violated" }, { key: "not_applicable", name: "Not applicable" },
    { key: "pending_evidence", name: "Pending evidence" }]);
  /* seed the control catalog ONCE per regulation, idempotently; an operator's status/evidence
     on a control row is never overwritten (the seed only writes rows that do not exist) */
  for (const reg of REGULATIONS) {
    for (const c of reg.controls) {
      const ex = D.get("SELECT id FROM compliance_controls WHERE tenant_id IS NULL AND regulation=? AND control_id=?", reg.key, c.id);
      if (!ex) D.run("INSERT OR IGNORE INTO compliance_controls(tenant_id,regulation,control_id,name,evidence,status) VALUES(?,?,?,?,?,?)",
        null, reg.key, c.id, c.name, c.evidence, "pending_evidence");
    }
  }
}

/* ---------- compliance: the control catalog ---------- */
function catalog() {
  return REGULATIONS.map(r => {
    const rows = db().all("SELECT control_id,name,evidence,status,tenant_id FROM compliance_controls WHERE regulation=? ORDER BY control_id", r.key);
    return { ...r, controls: rows };
  });
}
/* a tenant's control overrides sit alongside the platform template (tenant_id NULL);
   the tenant row wins when it exists, so each store can mark a control not-applicable */
function controlsFor(tenantId) {
  const plat = db().all("SELECT * FROM compliance_controls WHERE tenant_id IS NULL ORDER BY regulation, control_id");
  const mine = db().all("SELECT * FROM compliance_controls WHERE tenant_id=? ORDER BY regulation, control_id", tenantId);
  const byKey = new Map();
  for (const r of plat) byKey.set(r.regulation + "|" + r.control_id, { ...r, overridden: false });
  for (const r of mine) byKey.set(r.regulation + "|" + r.control_id, { ...r, overridden: true });
  return [...byKey.values()];
}
/* setControl: an operator's assessment of one control — writes a tenant-scoped row, never
   the platform template (the template is the shared definition, the tenant row is the verdict) */
function setControl(tenantId, regulation, controlId, status, evidenceNote, actor) {
  if (!/^(satisfied|partial|violated|not_applicable|pending_evidence)$/.test(status)) return { ok: false, error: "unknown control status" };
  const D = db();
  /* the tenant row inherits the template's name + evidence so the verdict stays readable
     without a join back to the platform template */
  const tpl = D.get("SELECT name, evidence FROM compliance_controls WHERE tenant_id IS NULL AND regulation=? AND control_id=?", regulation, controlId);
  const ex = D.get("SELECT id FROM compliance_controls WHERE tenant_id=? AND regulation=? AND control_id=?", tenantId, regulation, controlId);
  let cid;
  if (ex) {
    D.run("UPDATE compliance_controls SET status=?, updated_at=datetime('now') WHERE id=?", status, ex.id);
    cid = ex.id;
  } else {
    const r = D.run("INSERT INTO compliance_controls(tenant_id,regulation,control_id,name,evidence,status) VALUES(?,?,?,?,?,?)",
      tenantId, regulation, controlId, tpl ? tpl.name : controlId, tpl ? tpl.evidence : "", status);
    cid = Number(r.lastInsertRowid);
  }
  if (evidenceNote) D.run("INSERT INTO compliance_evidence(control_id,tenant_id,note,provided_by) VALUES(?,?,?,?)",
    cid, tenantId, String(evidenceNote).slice(0, 2000), actor || "operator");
  return { ok: true, id: cid };
}
/* evidence history for one control */
function evidenceFor(tenantId, regulation, controlId) {
  const row = db().get("SELECT id FROM compliance_controls WHERE COALESCE(tenant_id,?)=? AND regulation=? AND control_id=?", tenantId, tenantId, regulation, controlId);
  if (!row) return [];
  return db().all("SELECT note, provided_by, created_at FROM compliance_evidence WHERE control_id=? ORDER BY id DESC LIMIT 50", row.id);
}

/* ---------- continuous compliance validation ----------
   The verdict is COMPUTED from the control rows every call — never stored as an assertion —
   so it cannot drift from the evidence. A regulation is:
     satisfied      every non-excluded control is satisfied
     partial        some controls satisfied, none violated, or evidence still pending
     violated       any control violated
     not_applicable every control is not-applicable
   The "continuous" half: a control left on pending_evidence past its review date is partial,
   so an unaudited posture can never read as compliant. */
function evaluate(tenantId) {
  const rows = controlsFor(tenantId);
  const byReg = {};
  for (const r of rows) {
    if (!byReg[r.regulation]) byReg[r.regulation] = { regulation: r.regulation, controls: [], statuses: {} };
    byReg[r.regulation].controls.push(r);
    const st = r.status || "pending_evidence";
    byReg[r.regulation].statuses[st] = (byReg[r.regulation].statuses[st] || 0) + 1;
  }
  const regulations = Object.values(byReg).map(g => {
    const s = g.statuses, total = g.controls.length;
    const na = s.not_applicable || 0, sat = s.satisfied || 0, vio = s.violated || 0, pend = s.pending_evidence || 0, part = s.partial || 0;
    const applicable = total - na;
    let verdict;
    if (applicable === 0) verdict = "not_applicable";
    else if (vio > 0) verdict = "violated";
    else if (sat === applicable) verdict = "satisfied";
    else if (pend > 0 || part > 0) verdict = "partial";
    else verdict = "partial";
    return { regulation: g.regulation, total, applicable, satisfied: sat, violated: vio, pending: pend, partial: part, not_applicable: na, verdict };
  });
  const failures = regulations.filter(r => r.verdict === "violated");
  return {
    ok: failures.length === 0,
    verdict: failures.length ? ("COMPLIANCE VIOLATIONS: " + failures.map(f => f.regulation).join(", ")) : "no violated regulations",
    regulations,
    summary: {
      regulations: regulations.length,
      satisfied: regulations.filter(r => r.verdict === "satisfied").length,
      partial: regulations.filter(r => r.verdict === "partial").length,
      violated: failures.length,
      controls: rows.length
    },
    evaluatedAt: new Date().toISOString()
  };
}

/* ---------- privacy: consent ----------
   Consent is the lawful-basis record: subject + purpose + status. Required purposes cannot
   be refused (fulfilment has a contractual basis) but are still recorded; optional purposes
   are grant/withdraw per subject. Withdrawal schedules erasure of that purpose's data once
   its retention window closes, and immediately suppresses the purpose's channel. */
function grantConsent(tenantId, subject, purpose, opts) {
  const p = PURPOSES.find(x => x.key === purpose);
  if (!p) return { ok: false, error: "unknown purpose" };
  const status = p.required && !(opts && opts.force) ? "granted" : ((opts && opts.status) || "granted");
  if (!/^(granted|withdrawn|denied)$/.test(status)) return { ok: false, error: "unknown consent status" };
  const D = db();
  const ex = D.get("SELECT id FROM consents WHERE tenant_id=? AND subject=? AND purpose=?", tenantId, subject, purpose);
  if (ex) {
    D.run("UPDATE consents SET status=?, updated_at=datetime('now'), withdrawn_at=? WHERE id=?",
      status, status === "withdrawn" ? new Date().toISOString() : null, ex.id);
    return { ok: true, id: ex.id, status };
  }
  const r = D.run("INSERT INTO consents(tenant_id,subject,purpose,status,lawful_basis,source,ip) VALUES(?,?,?,?,?,?,?)",
    tenantId, subject, purpose, status, p.lawful, (opts && opts.source) || "console", (opts && opts.ip) || "");
  return { ok: true, id: Number(r.lastInsertRowid), status };
}
function consentOf(tenantId, subject) {
  const rows = db().all("SELECT purpose,status,lawful_basis,granted_at,updated_at,withdrawn_at FROM consents WHERE tenant_id=? AND subject=? ORDER BY purpose", tenantId, subject);
  const have = new Map(rows.map(r => [r.purpose, r]));
  return PURPOSES.map(p => {
    const c = have.get(p.key);
    return { purpose: p.key, name: p.name, required: !!p.required, lawful: p.lawful,
      status: c ? c.status : (p.required ? "granted" : "pending"),
      granted_at: c && c.granted_at, withdrawn_at: c && c.withdrawn_at };
  });
}
/* mayProcess: the gate every marketing/analyst send keys off — required purposes pass on
   their contractual basis, optional ones need a live grant */
function mayProcess(tenantId, subject, purpose) {
  const p = PURPOSES.find(x => x.key === purpose);
  if (!p) return false;
  if (p.required) return true;
  const c = db().get("SELECT status FROM consents WHERE tenant_id=? AND subject=? AND purpose=?", tenantId, subject, purpose);
  return !!c && c.status === "granted";
}
function withdrawAll(tenantId, subject) {
  const D = db();
  const now = new Date().toISOString();
  /* only OPTIONAL purposes withdraw — the required ones have a contractual basis that
     outlives a marketing opt-out. Filtering in JS keeps the statement driver-portable. */
  const optional = PURPOSES.filter(p => !p.required).map(p => p.key);
  for (const k of optional) {
    D.run("UPDATE consents SET status='withdrawn', withdrawn_at=? WHERE tenant_id=? AND subject=? AND purpose=? AND status='granted'", now, tenantId, subject, k);
  }
  return { ok: true, withdrawn: optional };
}

/* ---------- privacy: data-subject-rights requests ---------- */
function openRequest(tenantId, subject, kind, opts) {
  const k = REQUEST_KINDS.find(x => x.key === kind);
  if (!k) return { ok: false, error: "unknown request kind" };
  const D = db();
  const id = "DSR-" + Date.now().toString(36).toUpperCase() + crypto.randomBytes(2).toString("hex").toUpperCase();
  D.run("INSERT INTO privacy_requests(id,tenant_id,subject,kind,status,due_at) VALUES(?,?,?,?,?,?)",
    id, tenantId, subject, kind, "received",
    new Date(Date.now() + k.deadline_days * 86400000).toISOString());
  D.run("INSERT INTO privacy_request_events(request_id,from_state,to_state,actor,detail) VALUES(?,?,?,?,?)",
    id, null, "received", (opts && opts.actor) || "subject", "request received");
  return { ok: true, id };
}
function transitionRequest(tenantId, id, to, actor, detail) {
  if (!REQUEST_STATES.includes(to)) return { ok: false, error: "unknown state" };
  const D = db();
  const r = D.get("SELECT * FROM privacy_requests WHERE id=? AND tenant_id=?", id, tenantId);
  if (!r) return { ok: false, error: "not found", code: 404 };
  const from = r.status;
  const idx = (a) => REQUEST_STATES.indexOf(a);
  /* terminal states are terminal; verification must precede fulfilment (identity first) */
  if (from === "closed" || from === "fulfilled") return { ok: false, error: "request is already " + from };
  if (idx(to) < idx(from) && to !== "rejected") return { ok: false, error: "cannot move backwards through the request lifecycle" };
  if ((from === "received") && !["verified", "rejected"].includes(to)) return { ok: false, error: "identity must be verified before the request proceeds" };
  D.run("UPDATE privacy_requests SET status=?, updated_at=datetime('now'), fulfilled_at=? WHERE id=?", to, (to === "fulfilled" || to === "closed") ? new Date().toISOString() : null, id);
  D.run("INSERT INTO privacy_request_events(request_id,from_state,to_state,actor,detail) VALUES(?,?,?,?,?)", id, from, to, actor || "operator", String(detail || "").slice(0, 1000));
  /* erasure is executed on fulfilment: the subject's optional-purpose data is expunged and
     the erasure is recorded as the evidence GDPR 17 / DPDP 11 requires */
  if (to === "fulfilled" && r.kind === "erasure") eraseSubject(tenantId, r.subject, actor);
  return { ok: true, id, from, to };
}
function eraseSubject(tenantId, subject, actor) {
  const D = db();
  const removed = [];
  /* personal data the platform holds per subject: profile fields, addresses, consent records
     for optional purposes, support tickets and reviews authored by the subject. Retained
     records (orders, payments, the audit chain) are KEPT — the law obliges the platform to
     keep them, and erasing the audit trail would itself be a compliance violation. */
  const stmts = [
    ["users", "email = ?", [subject]],
    ["addresses", "owner_email = ?", [subject]],
    ["reviews", "author_email = ?", [subject]],
    ["questions", "author_email = ?", [subject]],
    ["tickets", "customer_email = ?", [subject]]
  ];
  for (const [table, where, args] of stmts) {
    try {
      const n = D.run(`DELETE FROM ${table} WHERE tenant_id=? AND ${where}`, tenantId, ...args);
      if (n.changes) removed.push(table + ":" + n.changes);
    } catch (e) { /* a table this tenant doesn't use is not a failure */ }
  }
  for (const p of PURPOSES.filter(p => !p.required)) {
    const n = D.run("DELETE FROM consents WHERE tenant_id=? AND subject=? AND purpose=?", tenantId, subject, p.key);
    if (n.changes) removed.push("consent:" + p.key);
  }
  D.run("INSERT INTO erasure_log(tenant_id,subject,removed,executed_by) VALUES(?,?,?,?)",
    tenantId, subject, JSON.stringify(removed), actor || "operator");
  return { ok: true, removed };
}
function requestsFor(tenantId, filter) {
  const q = "SELECT r.*, (SELECT COUNT(*) FROM privacy_request_events e WHERE e.request_id=r.id) events FROM privacy_requests r WHERE r.tenant_id=? ORDER BY r.created_at DESC LIMIT 200";
  return db().all(q, tenantId);
}

module.exports = {
  seed, catalog, controlsFor, setControl, evidenceFor, evaluate,
  grantConsent, consentOf, mayProcess, withdrawAll,
  openRequest, transitionRequest, requestsFor, eraseSubject,
  REGULATIONS, PURPOSES, REQUEST_STATES, REQUEST_KINDS
};
