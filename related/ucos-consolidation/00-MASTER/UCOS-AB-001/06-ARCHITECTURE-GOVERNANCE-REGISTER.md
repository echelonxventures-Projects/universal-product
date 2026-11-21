# 06 — Architecture Governance Register

> PROGRAM **UCOS-AB-001** · PHASE-001 · ARCHITECTURE BASELINE v1.0
> BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED TRUTH — READ-ONLY)** · MODE = READ-ONLY · EVIDENCE-ONLY · FAIL-CLOSED.

---

## 0. Purpose

Register the governance authorities that govern the architecture at baseline v1.0 — who may authorize what — so Change Control (doc 07/14) routes each future change to the correct existing authority. This program **does not redesign governance** (mission constraint); it records the governance that already exists.

## 1. Governing Authorities (evidence)

| Authority | Scope | Evidence | State |
|---|---|---|:---:|
| **UKB** | Repository Truth / canonical registry (single) | CLOSURE-006 CONST-01/16 | ACTIVE — sole truth |
| **CEP (Constitutional Engineering)** | Constitutional constitutions, freeze (CEP-007), amendment/evolution (CEP-009), audit (CEP-010) | `00-CEP/CEP-000…010` | ACTIVE — governing |
| **Governance (UCGF / Operating Model / GOV-001…006)** | Repository governance, reconciliation, authority spine | `02-MASTER/UCOS-GOV-*`; AUTH-009 | ACTIVE — reconciliation |
| **Validation authority** | Structural/referential validation | CEP-004; EC-1 ValidationEngine | ACTIVE · PASS |
| **Certification authority** | CCE ten-gate, per-unit + program certification | CEP-005; per-band certs | ACTIVE · CERTIFIED |
| **Ratification authority** | Constitutional finality | CEP-006; DR-RAT-11 | **BLOCKED (out-of-corpus)** |
| **EC-3 lane governance (AP-1…AP-5)** | Per-band admission | `02-MASTER/EC-3-AP-*` | COMPLETE |
| **UMA (proposed)** | Measurement control plane | UCOS-UMA-001 doc 13 | PLANNED (design) |

## 2. Governance Hierarchy & Conflict Order (recorded, not redesigned)

Per `UAM-001` / AUTH-009 §6.2 (evidence): the governing hierarchy is an ordered spine (L0 Authority → … → Products), with a fixed conflict-resolution order — a higher frozen/governing instrument governs a lower one (the "CONFLICT RULE" stamped in MCP-002/005). This baseline **inherits** that order; it introduces no competing authority.

## 3. Separation of Powers (Analysis ≠ Authority)

| Function | Held by | Never held by |
|---|---|---|
| Truth | UKB | any derived tool |
| Measurement | closure engines (derived) → UMA (planned) | any decision authority |
| Decision (closure/validation/cert) | respective authorities | measurement |
| Governance decision / freeze / ratification | CEP / Governance | analysis programs |

Baseline v1.0 preserves this separation (evidence: CONST-01 §3 Prohibition of Conflation; UMA doc 01).

## 4. Architecture Governance Responsibilities at v1.0

| Responsibility | Owner authority |
|---|---|
| Approve an architectural change proposal | CEP + Governance (doc 07) |
| Amend a frozen constitution | CEP-009 amendment process |
| Freeze an ACTIVE component | CEP-007 Freeze Constitution |
| Certify a baseline / component | Certification authority (doc 15) |
| Authorize implementation entry | Governance (GOV-004 pattern; doc 10) |
| Ratify constitutional finality | Ratification authority — **BLOCKED at DR-RAT-11** |

## 5. Governance Readiness (honest)

- **Framework governance:** ACTIVE (~90% per MCP-005 §02); sufficient to govern implementation entry and change control.
- **Constitutional finality:** **BLOCKED** — DR-RAT-11 requires an out-of-corpus stakeholder act (MCP-004). No in-corpus authority can discharge it (fail-closed; recorded, not worked around).
- Consequence: baseline v1.0 and implementation entry are governable **now**; declaring *full constitutional finality* is **not** possible until DR-RAT-11 clears. Doc 20 reports this as a distinct determination.

## 6. Determination

**ARCHITECTURE GOVERNANCE IS REGISTERED AND ACTIVE; FINALITY IS BLOCKED.** Every governing authority is recorded with scope and evidence; separation of powers is preserved; no governance is redesigned. Governance is ready to operate Change Control and implementation entry; constitutional finality remains gated by DR-RAT-11.

*END — 06 · UCOS-AB-001 · AUTHORITY = NONE (READ-ONLY) · MODIFIES NOTHING.*
