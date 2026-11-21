# 05 — TRACEABILITY

> **Mission:** IAC-001B · **Mode:** READ-ONLY · **Baseline:** HEAD `836475c`
> Trace: Knowledge Object → Repository Home → Canonical Owner → Constitutional Authority.

---

## 1. Traceability is authored canonical law

- `02-MASTER/UCOS-GOV-002-CONSTITUTION-TO-IMPLEMENTATION-TRACEABILITY-DETERMINATION.md` — the traceability determination.
- `00-CEP/CEP-008-CONSTITUTIONAL-EVIDENCE-TRACEABILITY-CONSTITUTION.md` — traceability constitution.
- Each CKO declares `GOVERNED BY … GOV-002 (traceability)`.

## 2. The four-link chain (established per artifact)

| Link | Established by | Verified for CKOs |
|---|---|---|
| **Knowledge Object** | `ARTIFACT ID` + identity block | 279/279 CKOs |
| ↓ **Repository Home** | tracked path + `CANONICAL FORM` | 279/279 (single home each) |
| ↓ **Canonical Owner** | `UCOS-PROGRAM` / `UCOS-FAMILY` | 279/279 |
| ↓ **Constitutional Authority** | `GOVERNED BY` / `DERIVES AUTHORITY FROM` → CEP-000..010 + GOV stack | 265/279 declare a governance line directly |

## 3. Worked example (USIS-001)

`USIS-001` → home `15-UNIVERSAL-SCIENCE-INTELLIGENCE/00-CONSTITUTION/…` → owner `UCOS-PROGRAM: USIS` (`UCOS-FAMILY: UNIVERSAL-SCIENCE-INTELLIGENCE`) → authority `GOVERNED BY UCIC-001 · GOV-001-T3 (No-Orphan) · GOV-002 (traceability) · REG-AUTO-001` and `DEPENDS-ON USIS-GOV-000` → parents to program root `USIS-GOV-000`, which chains to `LAW Ω∞-000` / MIP. Fully rooted-closed.

## 4. The 14 CKOs without a direct governance line

The 14 identity-block CKOs lacking an explicit `GOVERNED BY` line are numbered program-step / determination docs (e.g., `EIP-018D/01`, `UCOS-CRAT-001/00`, `UCOS-EKAP-001/01-02/04-05`, `UCOS-USIS-WAVE0/ACCEPTANCE/01`). Each is a **derived** program artifact that traces to its enclosing program charter (which itself is governed) and, for the derived ones (e.g. EIP-018D self-declares `AUTHORITY = NONE, DERIVED TRUTH`), is excluded as an establishing source. Their traceability is inherited, and none is orphaned (see `06`).

## 5. Determination

> **VERIFY 5 (Traceability): PASS.**
> Every CKO traces object → home → owner → constitutional authority, rooted-closed under `GOV-002` + `CEP-008`. No broken traceability chain found among canonical objects.

---
*End of 05-TRACEABILITY.md*
