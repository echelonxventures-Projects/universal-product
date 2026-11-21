# 12 — Security Compliance Rules

> PROGRAM **UCOS-EG-001** · PHASE-001 · IMPLEMENTATION CONFORMANCE FRAMEWORK
> BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED — READ-ONLY)** · MODE = READ-ONLY · EVIDENCE-ONLY · FAIL-CLOSED.

---

## 0. Purpose

Define security-compliance rules an implementation SHALL satisfy (Security Review R-5; CG-11). Consumes the Universal Security Architecture Constitution + PHASE-008 Universal Security domain (`UCOS-SEC-000001…4`) + DATA-014/SERVICE-014 data-security classifications; adds no new security model.

## 1. Security Rules (SC)

| # | Rule | Basis | Evidence |
|---|---|---|---|
| SC-1 | Security is **evaluative and non-enforcing** at the model level (classify; decide via RUNTIME-010 by reference) | band precedent (SEC/SSE laws) | security-assessment record |
| SC-2 | The implementation **enacts no protection** itself — no access grant, credential issuance, encryption, or conferred authority | Universal Security Constitution | non-enactment check |
| SC-3 | Authentication/authorization/confidentiality/integrity concerns are **classified**, informing policy by reference | DATA-014/SERVICE-014 | classification record |
| SC-4 | Secrets are **never embedded** (technology/secret markers clean) | band precedent (UIL/UAL-15) | secret-scan clean |
| SC-5 | Security-relevant data presented is **DF-2/DATA-014 classified by reference** | band precedent | data-security ref |
| SC-6 | A **coverage/posture map** records facets present/absent per boundary (records only) | band precedent (§12 coverage) | posture map |
| SC-7 | Network-exposed surfaces declare **auth/access posture explicitly** (no silent unauthenticated surface) | Security Constitution | exposure declaration |

## 2. Evaluative, Non-Enforcing Discipline

Consistent with the frozen application/service Security constructs (AMC-09 / SMC-10), an implementation's security layer *evaluates and records* (`SATISFIED/VIOLATED/INAPPLICABLE`); the *act* of enforcing is RUNTIME-010 by reference. EG requires this separation — an implementation that embeds enforcement re-founds runtime (RC-2) and fails CG-11.

## 3. Secret & Exposure Hygiene

- **No embedded secrets** (SC-4): source is scanned; markers clean (inherited "names no secret" discipline).
- **Explicit exposure posture** (SC-7): any network-exposed endpoint must declare authentication/authorization posture; a silent unauthenticated surface is a security-conformance FAIL (fail-closed, aligned with the security-awareness mandate).

## 4. Fail-Closed Conditions

| Condition | Result |
|---|---|
| Enacts protection / embeds enforcement | CG-11 FAIL → DENY |
| Embedded secret detected | SC-4 FAIL → DENY |
| Undeclared exposed surface | SC-7 FAIL → DENY |
| Security data not classified by reference | SC-5 FAIL → DENY |

## 5. Determination

**SECURITY COMPLIANCE RULES ARE DEFINED (SC-1…SC-7, fail-closed).** They require evaluative/non-enforcing security, no embedded secrets, explicit exposure posture, and reference-only data-security classification — consuming the frozen security architecture without redefining it.

*END — 12 · UCOS-EG-001 · AUTHORITY = NONE (READ-ONLY) · MODIFIES NOTHING.*
