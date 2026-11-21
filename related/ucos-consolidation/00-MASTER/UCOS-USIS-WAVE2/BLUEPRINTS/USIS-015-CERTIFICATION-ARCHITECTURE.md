# USIS-015 — Certification Architecture

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-015 (Certification Architecture) — Wave-2 area-tree architecture blueprint |
| NAMESPACE | AREA-TREE (Wave-2 architecture spine). Distinct from UCOS-USIS-001 foundation-deliverable doc numbering. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| UCOS-PROGRAM / CATEGORY | USIS / USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| META-MODEL TIER | Certification (USIS-004 tier 21) |
| CANONICAL HOME (on realization) | `15-…/16-CERTIFICATION/` (+ Certification Registry) |
| STATUS | AUTHORED · AWAITING UCIC AUTHORISATION · Wave 2 |
| PARENT | USIS-014 (Validation) |
| DEPENDS-ON | USIS-014 (Validation) · UCIC-001 (Stage 10, CCE 10 gates) · USIS-001 · Architectural-Properties Certification (referenced) |
| CONSTITUTIONAL ANCHOR | LAW USIS-06/07 (bounded autonomy, explainability); UCIC-001 Stage 10; Proof Obligation 17 |
| AUTHORITY | NONE — DERIVED. Composes USIS-001 + UCIC-001 (CCE). |
| CONFLICT RULE | Higher frozen/governing instruments prevail; void to extent of conflict. |

> **Purpose.** Define the architecture of the **Certification** tier — how a VALIDATED science-intelligence capability is certified as explainable, bounded-autonomous, and reproducible, under separation of duties. This blueprint binds UCIC-001 Stage 10 (CCE 10 fail-closed gates) to the substrate's certification semantics without duplicating the universal certification engine.

---

## 1 — Purpose
The Certification tier consumes a VALIDATED verdict (USIS-014) and issues a CERTIFIED decision for the substrate, confirming the science-intelligence certification properties on top of the universal CCE gates. Certification is the authority that a capability may advance to commit/production.

## 2 — Responsibilities
- Own the **certification-record shape** for science-intelligence capabilities.
- Define the substrate certification properties: **explainability** (LAW USIS-07), **bounded autonomy** (LAW USIS-06), and **reproducibility** (determinism, UCIC Output-7).
- Enforce **separation of duties**: certifier ≠ executor ≠ CIOA/CCE (UCIC Stage 3/10).
- Bind UCIC-001 Stage 10 (CCE 10 fail-closed gates) as the universal certification substrate.

## 3 — Boundaries
- **Owns:** science-intelligence certification semantics and the certification-record shape.
- **Does not own:** the validation verdict (USIS-014), the evidence bundle (USIS-016), the CCE gate engine (UCIC — referenced), or the Architectural-Properties Certification of the substrate itself (foundation deliverable — referenced).
- Certification *decides*; it produces no new validation and no new evidence.

## 4 — Interfaces
Exposes: `certify · prove · comply · explain · describe`. Consumes the VALIDATED capability + evidence bundle and the capability's CERTIFICATION REQUIREMENTS (UCIC Output-2); emits a certification record to the Certification Registry.

## 5 — Dependencies
Downward-only (acyclic): `Depends-On` USIS-014 (Validation) and UCIC-001 Stage 10 / CCE. USIS-016 (Evidence) is referenced as the required input bundle; Certification founds no further Wave-2 tier (Evidence attaches beneath it in the meta-model as tier 22).

## 6 — Registry model
Certification records are rows in the **Certification Registry** (target #7), homed under `16-CERTIFICATION/`. Append-only, deterministic; each record references the capability, the validation record, the CCE gate outcomes, the certifier identity (SoD), and the certified properties.

## 7 — Relationship model
Parent edge → Validation (USIS-014). Child edge → Evidence (USIS-016, the certification's evidentiary basis). Reference edges → CCE (gate engine), Architectural-Properties Certification (substrate-level properties). Certification Closure (Proof Obligation 17): every completed capability is CCE-certified.

## 8 — Lifecycle
Certification is UCIC-001 Stage 10: CCE 10 fail-closed gates PASS with certifier ≠ executor ⇒ Gate CERTIFIED. Any gate failure ⇒ non-recoverable for the attempt ⇒ REOPEN to ACTIVE with evidence preserved. Certification is monotonic; the sole reversal is defect-driven REOPEN.

## 9 — Validation model
Referenced to USIS-014: certification cannot begin without a VALIDATED verdict and complete evidence. Recursively, certification records are themselves validated for SoD compliance and gate-completeness.

## 10 — Certification model
This tier *is* the certification model for the substrate. Its own conformance is asserted by the CCE gate set and confirmed against the substrate Architectural-Properties Certification. A certification lacking SoD or any CCE gate is void (fail-closed).

## 11 — Evidence model
Referenced to USIS-016 using UCIC Output-5: the certification record itself, CCE gate outcomes, certifier identity, and traceability edges (Vision→Certification). Absence ⇒ NOT-DONE (TRACK-001).

## 12 — Failure model
Per UCIC Output-4. Any failed CCE gate ⇒ non-recoverable for the attempt ⇒ REOPEN, evidence preserved. Certifier = executor ⇒ SoD violation ⇒ certification void. Missing explainability/bounded-autonomy/reproducibility property ⇒ fail-closed.

## 13 — Reuse model
Reuse-First (LAW USIS-02): the UCIC-001 CCE 10-gate engine and the SoD model are **referenced**, never re-implemented. This tier adds only the explainability/bounded-autonomy/reproducibility certification semantics for science-intelligence.

## 14 — Non-goals
- Not the validation verdict (USIS-014) nor the evidence store (USIS-016).
- Not a new certification engine (references CCE).
- Names no tooling in the architecture (current bindings live in UCIC/CCE).

*END — USIS-015 · CERTIFICATION ARCHITECTURE · Wave-2 operational-memory blueprint · AUTHORITY = NONE (DERIVED).*
