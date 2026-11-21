# 07 — CONSTITUTIONAL COVERAGE

> **Mission:** IAC-001B · **Mode:** READ-ONLY · **Baseline:** HEAD `836475c`
> Determine whether every CKO is constitutionally governed; report any object outside constitutional governance.

---

## 1. The constitutional governance stack (authored, canonical)

| Instrument | Governs |
|---|---|
| `00-CEP/CEP-000` | Constitutional Engineering Charter (apex) |
| `CEP-001..003` | Engineering / Governance / Execution |
| `CEP-004 / CEP-005` | Validation / Certification |
| `CEP-006` | Ratification (finality authority) |
| `CEP-007` | Freeze |
| `CEP-008` | Evidence & Traceability |
| `CEP-009 / CEP-010` | Amendment-Evolution / Audit-Compliance-Assurance |
| `02-MASTER/UCOS-GOV-001..006` | Corpus authority + No-Orphan, Constitution→Implementation traceability, readiness, execution authorization, repository governance reconciliation |
| `REG-AUTO-001` | Registration authority |
| `UNIVERSAL-LAW-CANONICAL-HOMING` (UAKOS-CL003-W1) | Single canonical home |

## 2. Coverage result

- **265 / 279** CKOs declare a governance line (`GOVERNED BY` / `DERIVES AUTHORITY FROM` / `PARENT` / `DEPENDS-ON`) that chains into the stack above.
- **14 / 279** are derived program-step/determination docs whose governance is **inherited** from their enclosing program charter (which is itself governed). None asserts ungoverned canonical authority.
- Band CKOs (`08-…14-`) chain via their band program → EC-3 admission determinations (`02-MASTER/EC-3-AP-*`) → CEP stack.
- USIS chains via `USIS-GOV-000` → `LAW Ω∞-000` / MIP.

## 3. Objects outside constitutional governance

**None.** No canonical knowledge object was found that operates outside the constitutional governance stack. Every CKO is either directly governed (declared) or inherits governance from a governed program. Derived/generated artifacts (excluded as establishing) are separately bounded by the ignore authority (GOV-005 §5.3) per IAC-001A.

## 4. Determination

> **VERIFY 7 (Constitutional Coverage): PASS.**
> Every Canonical Knowledge Object is constitutionally governed; zero objects outside constitutional governance.

---
*End of 07-CONSTITUTIONAL-COVERAGE.md*
