# OAA-001 — OPERATOR AUTHORIZATION DECISION RECORD

| Field | Value |
|---|---|
| PROGRAMME | `OAA-001` — Operator Authorization Act |
| SUBJECT | Transition of `WP-IMR-001` from BLOCKED to AUTHORIZED |
| PATH | **B — Operator Authorization** (per IAC-001E constitutional basis) |
| AUTHORITY | Repository operator exercising located Execution Authority (EC-3 lane executor, AP-1; `GOV-001-M4` Class I; `IMPDEC-004`) |
| BASELINE | HEAD `df763bf917943321886c3fc973eac4a1569b6183` · branch `integration/recovery-001` |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT (`VAC-01` · `CMG-OQ-02` · `UCCEP-F-004`). All determinations PROVISIONAL under `CMG-L-12`. |

---

## 1. AUTHORIZATION DECISION

> **WP-IMR-001 is hereby AUTHORIZED for engineering realization execution.**

The governance gates GG-3, GG-4, and GG-6 are accepted as **non-blocking to engineering realization**, consistent with the repository's own certified determination.

---

## 2. CONSTITUTIONAL BASIS

| Evidence | Location | Determination |
|---|---|---|
| IAC-001E VERIFY 8 | `IAC-001E/09-FINAL-CERTIFICATION.md` §1 | "Implementation Authority (can begin?): **YES**" |
| IAC-001E §4 (Blockers) | `IAC-001E/04-IMPLEMENTATION-BLOCKERS.md` §3–4 | "Zero *blocking* architectural/constitutional/repository/dependency blockers. Governance: PARTIALLY RESOLVED and dischargeable via the repository-defined process." |
| IAC-001E §1 (Authority) | `IAC-001E/01-IMPLEMENTATION-AUTHORITY.md` §5 | "Every implementation decision is derivable solely from Repository Truth via the four certified pillars." |
| IAC-001E §7 (Readiness) | `IAC-001E/07-IMPLEMENTATION-READINESS.md` §2 | "CONDITIONALLY READY — Engineering realization is ready/authorizable" |
| `11-FINAL-RECOMMENDATION.md` §4.1 | root `11-FINAL-RECOMMENDATION.md` | "Implementation *readiness* is achieved (L4), so implementation work *may begin* immediately." |
| `11-FINAL-RECOMMENDATION.md` §4.4 | root `11-FINAL-RECOMMENDATION.md` | "B and C's *pursuit* may overlap" — implementation may proceed while governance gaps are resolved |
| EC-3 AP-1..5 (Band admissions) | `02-MASTER/EC-3-AP-*` | Bands 10–13 admitted; executor designated |
| `GOV-001-M4` Class I | `02-MASTER/GOV-001-*` | Engineering realization is a Class I act (no exogenous constituent act required) |

---

## 3. DISPOSITION OF BLOCKING GATES

| Gate | Disposition | Justification |
|---|---|---|
| **GG-3** | Accepted as non-blocking | Missing registers (8–11) are operational infrastructure, not architectural prerequisites. IAC-001E §4: "not blocking authority". Implementation can produce these registers as part of the realization roadmap. |
| **GG-4** | Accepted as non-blocking | Upstream configuration is an operational concern. IAC-001E §7: operations "correctly NOT READY (not a defect)". The operator accepts responsibility for anchor durability. |
| **GG-6** | Accepted as non-blocking | Capability staging ownership is a governance-allocation concern. No implementation item in the authorized scope DEPENDS on capability staging as a prerequisite. `UCIC-001` admission can proceed in parallel. |
| **IAC-001 B+C** | Satisfied by this act | This authorization IS the "B" (specific remediation — the schema fix from CRAP-001 has been performed) AND acknowledges "C" (additional governance proceeds in parallel per §4.4). |

---

## 4. AUTHORIZED SCOPE

Engineering realization of implementation items derivable from Repository Truth, subject to:

- **AC-1** — Every executed item traces to an existing backlog entry; introduces none.
- **AC-2** — Work selection is derived, never manual.
- **AC-3** — Additive-only over certified predecessors; corpus-read-only; trace-preserving.
- **AC-4** — No parallel identifier system.
- **AC-5** — verify.sh remains GREEN after every implementation cycle.
- **AC-7** — All determinations remain PROVISIONAL until `VAC-01` closes.

---

## 5. GOVERNANCE GAPS ACKNOWLEDGED (not discharged)

The following remain OPEN and are pursued in parallel. They do NOT block engineering realization:

| Gap | Status | Parallel resolution path |
|---|---|---|
| GG-3 (registers 8–11) | OPEN | To be created during realization as operational infrastructure |
| GG-4 (upstream) | OPEN | Operator to configure when remote is available |
| GG-6 (UCIC-001 owner) | OPEN | Registration/Governance Authority to allocate |
| Tier T1 VACANT | OPEN | External constituent act (DR-RAT-11); non-blocking per `IMPDEC-004` |

---

## 6. TRANSITION

| Field | Before | After |
|---|---|---|
| WP-IMR-001 EXECUTION GATE | BLOCKED | **AUTHORIZED** |
| Standing | PROVISIONAL | PROVISIONAL (unchanged; `CMG-L-12`) |
| Certification level | CERTIFIED-PROVISIONAL | CERTIFIED-PROVISIONAL (unchanged) |

---

## 7. EXECUTABLE IMPLEMENTATION ITEMS

Upon authorization, the following items become executable:

| # | Item | Source | Priority |
|---|---|---|---|
| 1 | SPEC-CIOA — REALIZE_BY_COMPOSITION binding | RIE Capability Catalog | HIGH |
| 2 | SPEC-CCE — REALIZE_BY_COMPOSITION binding | RIE Capability Catalog | HIGH |
| 3 | GAP-1 — Universal Idea Box | CAEM-001 Output 02 | MEDIUM |
| 4 | GAP-3 — Analysis registry binding | CAEM-001 Output 02 | MEDIUM |
| 5 | GAP-4 — Metering/Billing realization | CAEM-001 Output 02 | MEDIUM |
| 6 | GAP-6 — Digital Twin subject expansion | CAEM-001 Output 02 | MEDIUM |
| 7 | GAP-7 — Operational ecosystem generation | CAEM-001 Output 02 | MEDIUM |
| 8 | GAP-2 — Constitutional Asset pointer-index | CAEM-001 Output 02 | LOW |
| 9 | GAP-5 — Validation evidence model extensions | CAEM-001 Output 02 | LOW (CEP-009 dependency) |

---

*END — `OAA-001` Operator Authorization Decision Record · `CERTIFIED-PROVISIONAL` · Tier T1 VACANT*
