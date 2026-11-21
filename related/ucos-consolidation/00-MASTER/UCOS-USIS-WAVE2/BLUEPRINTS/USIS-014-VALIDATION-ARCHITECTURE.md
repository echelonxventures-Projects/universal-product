# USIS-014 — Validation Architecture

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-014 (Validation Architecture) — Wave-2 area-tree architecture blueprint |
| NAMESPACE | AREA-TREE (Wave-2 architecture spine). Distinct from UCOS-USIS-001 foundation-deliverable doc numbering. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| UCOS-PROGRAM / CATEGORY | USIS / USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| META-MODEL TIER | Validation (USIS-004 tier 20) |
| CANONICAL HOME (on realization) | `15-…/15-VALIDATION/` (+ Validation Registry) |
| STATUS | AUTHORED · AWAITING UCIC AUTHORISATION · Wave 2 |
| PARENT | USIS-017 (API/SDK) via Implementation (referenced) |
| DEPENDS-ON | USIS-017 (API/SDK, via Implementation) · UCIC-001 (Stages 5–9) · USIS-001 (LAW USIS-07) · Proof-Obligations Register |
| CONSTITUTIONAL ANCHOR | LAW USIS-07 (explainable provenance); UCIC-001 Output-7; Proof Obligations 11/12/14/16 |
| AUTHORITY | NONE — DERIVED. Composes USIS-001 + UCIC-001 + Proof-Obligations Register. |
| CONFLICT RULE | Higher frozen/governing instruments prevail; void to extent of conflict. |

> **Purpose.** Define the architecture of the **Validation** tier — the science-intelligence specialization of how a realized capability is proven sound before certification: grounding, explanation coverage, and closure of the substrate's structural obligations. This blueprint binds UCIC-001 Stages 5–9 to the substrate's science-specific validation semantics without duplicating the universal lifecycle.

---

## 1 — Purpose
The Validation tier consumes an Implementation (the code realization of the API/SDK/Service/Engine chain) and produces a VALIDATED verdict for the substrate. It adds the science-intelligence validation semantics — grounding and explanation coverage — on top of the universal UCIC-001 validation stages.

## 2 — Responsibilities
- Own the **validation record shape** for science-intelligence capabilities.
- Define **grounding validation**: every model/inference is grounded in a Knowledge Object (Ontology Closure, Proof Obligation 11).
- Define **explanation-coverage validation**: every inference/analytic/learned change/decision emits an explanation trace (LAW USIS-07).
- Bind UCIC-001 Stages 5–9 (static/dynamic/test/coverage/evidence) as the universal substrate this tier specializes.

## 3 — Boundaries
- **Owns:** science-intelligence validation semantics and the validation-record shape.
- **Does not own:** the UCIC-001 lifecycle/gates (referenced), the evidence store (USIS-016), the certification decision (USIS-015), or the tests' concrete tooling (current binding of UCIC — referenced).
- Validation *produces a verdict*; it makes no certification decision (that is USIS-015).

## 4 — Interfaces
Exposes: `validate · prove · explain · observe · describe`. Consumes the Implementation and the capability's declared VALIDATION REQUIREMENTS (UCIC Output-2); emits a validation record to the Validation Registry and the Evidence tier.

## 5 — Dependencies
Downward-only (acyclic): `Depends-On` the Implementation of the USIS-017/012/013/011 chain (referenced) and UCIC-001 Stages 5–9. USIS-015 (Certification) `Depends-On` this tier — Validation founds Certification (meta-model).

## 6 — Registry model
Validation records are rows in the **Validation Registry** (target #6), homed under `15-VALIDATION/` with evidence in the evidence store. Append-only, deterministic; each record references the capability, the obligations checked, and the verdict.

## 7 — Relationship model
Parent edge → Implementation. Child edge → Certification (USIS-015). Reference edges → Proof-Obligations Register (the checked predicates), Knowledge/Ontology registries (grounding), Evidence (USIS-016). Validation Closure (Proof Obligation 16): every certified capability has validation evidence.

## 8 — Lifecycle
A validation follows UCIC-001 Stages 5–9: **static → dynamic → test → coverage → evidence**, terminating at Gate VALIDATED. The science-specific checks (grounding, explanation coverage) run within Stages 6–9. Failure returns to IMPLEMENTED (fix-forward); no skip.

## 9 — Validation model
This tier *is* the validation model for the substrate; recursively, its own artifacts are validated for completeness (all declared requirements checked) and determinism (same state ⇒ same verdict; UCIC Output-7). Absence of a required check ⇒ NOT-DONE (TRACK-001).

## 10 — Certification model
Referenced to USIS-015: a validation record is the required input to certification; certification (CCE 10 gates) cannot proceed without a VALIDATED verdict and its evidence.

## 11 — Evidence model
Referenced to USIS-016 using UCIC Output-5: static/dynamic/test/coverage reports, determinism verification, grounding records, and explanation-coverage traces. The consolidated evidence bundle gates VALIDATED.

## 12 — Failure model
Per UCIC Output-4. Any failed static/dynamic/test/coverage check ⇒ recoverable ⇒ revert to IMPLEMENTED gate, evidence preserved. Unproducible required evidence ⇒ non-recoverable. Missing grounding or explanation coverage ⇒ fail-closed (LAW USIS-07).

## 13 — Reuse model
Reuse-First (LAW USIS-02): the UCIC-001 universal validation stages and their tooling bindings are **referenced**, never re-implemented. This tier adds only grounding + explanation-coverage semantics specific to science-intelligence.

## 14 — Non-goals
- Not the certification decision (USIS-015) nor the evidence store (USIS-016).
- Not a replacement for UCIC-001 stages (references them).
- Names no test/coverage tool in the architecture (current bindings live in UCIC).

*END — USIS-014 · VALIDATION ARCHITECTURE · Wave-2 operational-memory blueprint · AUTHORITY = NONE (DERIVED).*
