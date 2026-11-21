# 10 — Implementation Entry Criteria

> PROGRAM **UCOS-AB-001** · PHASE-001 · ARCHITECTURE BASELINE v1.0
> BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED TRUTH — READ-ONLY)** · MODE = READ-ONLY · EVIDENCE-ONLY · FAIL-CLOSED.

---

## 0. Purpose

Define the conditions that MUST hold before governed implementation may begin against baseline v1.0. Each criterion is stated with its evidence and current status (fail-closed: an unmet criterion blocks entry for its scope).

## 1. Entry Criteria (with evidence & status)

| # | Criterion | Evidence | Status |
|---|---|---|:---:|
| E-1 | **Architecture Frozen** (baseline v1.0 established) | doc 01; docs 02/03 inventories | **MET** |
| E-2 | **Baseline Approved** | Control Tower `architecture = APPROVED`; Architecture Freeze gate PASSED (MCP-005 §04) | **MET** |
| E-3 | **Governance Active** | CEP-002; GOV-001…006; UCGF/Operating Model (doc 06) | **MET (framework)** |
| E-4 | **Measurement Authority Approved** | UMA design-complete (UCOS-UMA-001); interim measurement = closure engines (derived) | **PARTIAL** — UMA designed/approved, **not instantiated** |
| E-5 | **Repository Truth Stable** | UKB; CLOSURE-002 CLOSED (398, 0 gaps); guard 10/10 | **MET** |
| E-6 | **Knowledge Once Active** | CONST-01; `duplicate_canonical_homes=0` | **MET** |
| E-7 | **Dependency Graph Complete** | doc 05 (acyclic, complete) | **MET** |
| E-8 | **Realization Substrate Certified** | EC-1 CERTIFIED; EC-2 CLOSED+FROZEN; Bands 10–12 frozen/certified | **MET** |
| E-9 | **Change Control Established** | doc 07 (9-stage) | **MET** |
| E-10 | **Program Inventory Complete** (every completed program has successor/terminal state) | doc 04 §6 | **MET** |
| E-11 | **Constitutional Finality Ratified** | DR-RAT-11 | **NOT MET — BLOCKED (out-of-corpus)** |

## 2. Entry Determination (scoped, fail-closed)

Implementation entry is evaluated **per scope**, not as one global boolean:

| Scope | Governing criteria | Entry verdict |
|---|---|:---:|
| **Engineering realization** (continue EC-3 / Band-13 freeze / products along frozen spine) | E-1…E-10 | **AUTHORIZED** — all met; DR-RAT-11 is finality-only, non-blocking to engineering (MCP-002 §02) |
| **Measurement-dependent governance** (adopt UMA as measurement authority) | E-4 | **DEFERRED** — requires UMA instantiation (doc 04; UMA docs 17–19) |
| **Constitutional finality declaration** | E-11 | **BLOCKED** — DR-RAT-11 out-of-corpus act required |

## 3. The DR-RAT-11 Caveat (mandatory honesty)

E-11 is **not** met and cannot be met by any in-corpus action (evidence: MCP-004; MCP-002 §02 B-RAT-11). Its effect is bounded: it blocks *constitutional finality*, **not** engineering implementation along the already-approved, already-frozen spine. This baseline therefore authorizes implementation **within the engineering scope** while recording finality as blocked — it does not overstate readiness.

## 4. Interim Measurement Provision (E-4)

Until UMA is instantiated, measurement for implementation gating is supplied by the existing derived engines (`closure_engine.py`, guard, `verify.sh`, control-tower) — the same apparatus that produced all band certifications. This is an **explicitly interim** provision (UMA is the approved permanent authority). Implementation may proceed on this interim basis; measurement authority migrates to UMA per UMA docs 18–19 when instantiated.

## 5. Determination

**IMPLEMENTATION ENTRY IS AUTHORIZED FOR THE ENGINEERING SCOPE.** E-1…E-3, E-5…E-10 are MET; E-4 is PARTIAL (interim measurement in force, UMA pending); E-11 is BLOCKED (finality-only). No criterion is UNKNOWN. Full-finality entry awaits DR-RAT-11. See doc 16 (Implementation Readiness Assessment) and doc 20.

*END — 10 · UCOS-AB-001 · AUTHORITY = NONE (READ-ONLY) · MODIFIES NOTHING.*
