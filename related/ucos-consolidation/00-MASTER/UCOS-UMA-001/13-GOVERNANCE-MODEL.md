# 13 — Governance Model

> PROGRAM **UCOS-UMA-001** · PHASE-001 · UNIVERSAL MEASUREMENT AUTHORITY
> BASELINE `b67a720` · AUTHORITY = **NONE (DESIGN ONLY)** · MODE = DESIGN-ONLY · NON-IMPLEMENTING · FAIL-CLOSED.

---

## 0. Purpose

Define how UMA itself is governed: who may change its control plane (registries, adapters, metric definitions, manifests), how those changes are authorized and audited, and how UMA's governance stays subordinate to the existing frozen governance authority (CEP/CONST) without competing with it.

## 1. Governance Principles

| Principle | UMA application |
|---|---|
| Single Governance Authority | UMA does not create a new governance authority. Control-plane changes are authorized under the existing CEP/CONST governance. |
| Analysis ≠ Authority | UMA governs *how it measures*; it never governs the *meaning of truth* (UKB) or *decisions* (consumers). |
| Fail-Closed | An unauthorized or malformed control-plane change is rejected; the prior snapshot remains in force. |
| Evidence Before Conclusion | Every control-plane change carries rationale + evidence and is auditable. |
| Everything Versioned | No in-place edits; each change mints a new registry/metric version. |

## 2. What is Governed (the control plane)

| Governed object | Change type | Authorization |
|---|---|---|
| Namespace Descriptor (doc 05) | add / deprecate / reclassify / exclude | Governed event + rationale |
| Identifier Family (doc 06) | add / amend rule / deprecate | Governed event + test vectors |
| Source Adapter (doc 07) | register / amend / retire | Governed event + determinism note |
| Metric Definition (doc 04/08) | register / amend / retire | Governed event + formula review |
| Ontology class (doc 08) | add / amend | Governed event |
| Manifest (doc 04) | create / designate Canonical | Governed event |
| Exclusion / Assumption record (MA-7) | add / retire | Governed event + rationale (mandatory) |

Data-plane execution (running measurements) is **not** governed per-call — it is open to all consumers, because it is read-only and deterministic. Only *what can be measured* is governed.

## 3. Change Lifecycle (fail-closed, audited)

```
PROPOSED ─► REVIEWED ─► AUTHORIZED ─► VERSIONED(new snapshot) ─► ACTIVE
    │           │            │
 auto from   rationale +  under CEP/CONST
 Discovery   evidence     governance authority
 (UNCOVERED)  required
    └────────── rejected / deferred ──► prior snapshot remains in force
```

- **Discovery-originated proposals** (UNCOVERED-NAMESPACE/IDENTIFIER/SOURCE) enter as `PROPOSED`; they are **never auto-accepted** (fail-closed). This is the governed answer to "how does a new namespace enter UMA?" — by review, not by code edit and not by silent inclusion.
- Every authorized change is stamped with author authority, baseline, rationale, and produces a new immutable registry version. Prior sealed measurements remain reproducible against their pinned version (replayability).

## 4. Roles (RACI-style, mapped to existing authorities)

| Role | Held by | Responsibility |
|---|---|---|
| Measurement Operator | any consumer (Closure/Validation/etc.) | request runs (data plane) |
| Registry Steward | UMA platform role | curate proposals, prepare change sets |
| Governance Authority | **existing CEP/CONST** | authorize/reject control-plane changes |
| Truth Authority | **UKB** | owns canonical truth (out of UMA scope) |
| Auditor | Governance / Certification | verify audit chain, replay results |

UMA introduces the *Registry Steward* operational role but places the *authorization* right with the pre-existing governance authority — preserving Single Governance Authority.

## 5. Audit & Non-Repudiation

- Every control-plane change and every sealed measurement is append-only and content-addressed.
- A `GovernanceLedger` records: what changed, by whom, under what authority, with what rationale, at what baseline.
- Any determination consumed downstream can be traced to the exact registry version + manifest + evidence that produced it (full provenance).

## 6. Relationship to Frozen Governance (no redesign)

Per mission constraints, UMA does **not** redesign governance, closure, lifecycle, UKB, Repository Truth, or canonical registries. UMA governance is *scoped strictly to the measurement control plane* and operates **under** the frozen CEP/CONST regime. Where UMA needs authorization, it defers to that regime. This document proposes governance *for UMA's own knobs only*.

## 7. Self-Measurement (governance metric)

UMA measures its own governance posture via metric 3.8 (Governance Posture) and 3.14 (Truth Uniqueness), applied reflexively: exactly one Namespace Registry, one Identifier Registry, one Canonical Manifest per constitutional measurement, no competing measurement authority. A FAIL here means UMA itself is misconfigured and blocks constitutional claims (fail-closed, self-applied).

## 8. Dependency Determination

- Authorization for UMA control-plane changes **RETAINS** with CEP/CONST governance (no new authority). UMA adds only the Registry Steward operational function and the Governance Ledger (NEW, owned by UMA).

*END — 13 · UCOS-UMA-001 · AUTHORITY = NONE (DESIGN ONLY) · MODIFIES NOTHING.*
