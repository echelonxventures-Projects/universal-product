# CERTIFICATION ARCHITECTURE DETERMINATION (DRAFT)

> **Mission:** Certification Taxonomy Consolidation Discovery — semantic ownership analysis
> **Mode:** Discovery draft only. No code changes, no taxonomy implementation, no artifact beyond this draft.
> **Date:** 2026-08-13
> **Scope of this pass:** the three named modules (`engine/certification`, `engine/universal_certification`, `platform/certification`), plus enough of their immediate neighborhood (`engine/knowledge/certification.py`, `00-BOOK/DATA/certification.json`, the validation/assurance modules) to place them correctly. The live, ad hoc governance-chain verdicts (RIB, AEE, CMG, Phase 8/9, UCEF) are named but not re-analyzed here — that comparison belongs in the full readiness determination this draft feeds.

---

## 1. Module Purpose Determination

### `engine/certification` — EC-1 Certification Layer (EPIC-008)

| | |
|---|---|
| **Purpose** | Deterministic, immutable, additive certifier that aggregates upstream Validation Reports/Evidence into a fail-closed decision |
| **Scope** | Specifically bound to "the Validation Layer (EPIC-007)" as its declared upstream |
| **Granularity** | Whole-subject (one Validation Report + Evidence → one Certification Decision) |
| **Inputs** | Validation Report, Validation Evidence (from EPIC-007 specifically) |
| **Outputs** | Certification Decision, immutable content-addressed Certification Record, Certification Evidence, hash-chained Ledger Entry, EC-1 Program Closure Report (A1–A10) |
| **Authority claim** | Explicit disclaimer: "invents no verdict (TP-01) — it only aggregates validation"; "confers no constitutional finality or authority (DE-05/IP-01)" |
| **Evidence model** | Content-addressed, deterministic — identical inputs yield byte-identical outputs |
| **Consumers** | `platform/certification` (confirmed by real imports: `facade.py`, `contracts.py`, `ledger.py`, `health.py`, `status.py`, `service.py` all contain live `from engine.certification.X import Y` statements) |

### `engine/universal_certification` — Universal Certification Engine (EPIC-006, Terminal T6)

| | |
|---|---|
| **Purpose** | A generalized certifier "that depends on no single producer" |
| **Scope** | Declared to accept any source supplying `ValidationInput`, `MeasurementInput`, and `RepositoryTruthInput` |
| **Granularity** | Whole-subject, same as EC-1, but with a third input dimension (Measurement) EC-1 does not take |
| **Inputs** | Validation, Measurement, Repository Truth (three normalized inputs) |
| **Outputs** | Compliance Report, Certification Decision, immutable Certificate, Certification Evidence, governed Approval Workflow, hash-chained Audit Ledger — orchestrated by a "Certification Pipeline" |
| **Authority claim** | Same disclaimer pattern as EC-1, near-verbatim: "sound... inventing none (TP-01)," "record-only," "`ENGINEERING-EXECUTION-ONLY`," "asserts no constitutional finality (DE-05/IP-01)" |
| **Evidence model** | Same determinism claim as EC-1 |
| **Consumers** | **None found.** Zero imports anywhere in the codebase outside its own tests. Not referenced by `platform/certification`, `Makefile`, or `verify.sh`. |

### `platform/certification` — EC-2 Platform Certification Console & Ledger Runtime (EPIC-011)

| | |
|---|---|
| **Purpose** | Makes EC-1's certified output "inspectable, searchable, ledger-navigable, and traceable" |
| **Scope** | Explicitly and narrowly: "a strictly additive, read/inspection-only layer over the certified EC-1 engine" |
| **Granularity** | Same subject granularity as EC-1, since it reproduces EC-1's output read-only, never re-decides |
| **Inputs** | EC-1's own published, versioned contract (`engine.certification.certify` v1) |
| **Outputs** | Surfaced/reproduced certification views, search, audit trail, ledger navigation — never a new decision |
| **Authority claim** | None claimed — explicit: "no new authority, no new capability group" |
| **Evidence model** | "Byte-for-byte the certified engine output (P6)" — a fidelity-checked mirror, not a re-derivation |
| **Consumers** | Authorized principals via the EC-2 Identity Layer's `certification-ledger` capability group |

---

## 2. Certification Responsibility Matrix

| Responsibility | `engine/certification` (EC-1) | `engine/universal_certification` (Universal) | `platform/certification` (EC-2 console) |
|---|---|---|---|
| Certification request | — (reactive, given inputs) | — (reactive, given inputs) | No — surfaces existing decisions only |
| Certification execution | **Yes** | **Yes** | No |
| Certification decision | **Yes** — `CertificationStatus.CERTIFIED`/`NOT_CERTIFIED` | **Yes** — its own `CertificationStatus.CERTIFIED`/`NOT_CERTIFIED` (identically named and valued) | No — reproduces EC-1's decision read-only |
| Certification approval | No | **Yes** — governed Approval Workflow (EC-1 has none) | No |
| Certification registry | Ledger (append-only, hash-chained) | Audit Ledger (append-only, hash-chained) | `CertificationRegistry` — indexes/searches EC-1's records, does not own them |
| Certification evidence | **Yes** — `CertificationEvidence` | **Yes** — `CertificationEvidence` (separate class) | Surfaces EC-1's evidence reference only |
| Certification projection | No | No | **Yes — this is its entire purpose** |
| Certification reporting | Program Closure Report (A1–A10) | Compliance Report | Search, audit, health, fidelity check |

---

## 3. Authority Analysis

| Module | Claims | Classification |
|---|---|---|
| `engine/certification` | C (execution capability only) — explicit "confers no constitutional finality or authority" | **EXECUTION / IMPLEMENTATION SERVICE**, with an EVIDENCE facet (produces its own evidence chain) |
| `engine/universal_certification` | C (execution capability only) — same disclaimer pattern | **EXECUTION / IMPLEMENTATION SERVICE**, with an EVIDENCE facet — **structurally indistinguishable from EC-1's claim** |
| `platform/certification` | D (evidence/projection capability only) — explicit "no new authority" | **PROJECTION** |

Neither `engine/certification` nor `engine/universal_certification` claims (A) supreme or (B) domain certification authority. Both claim exactly the same thing, in nearly the same words, about themselves.

---

## 4. Verdict Semantics Analysis (this pass's scope)

| Verdict/status | Meaning here | Lifecycle position | Scope | Owner |
|---|---|---|---|---|
| `CertificationStatus.CERTIFIED` / `NOT_CERTIFIED` | Binary fail-closed aggregation of upstream validation | Post-validation, pre-nothing (terminal for the subject) | Whole-subject | **Declared identically, independently, by both `engine/certification` and `engine/universal_certification`** |
| `CriterionStatus` (EC-1) / `RuleStatus` (Universal) | Per-criterion/per-rule pass state feeding the aggregate decision | Pre-aggregation | Criterion-level | Each engine's own, not shared |
| `ComplianceStatus` (Universal only) | A distinct concept EC-1 has no equivalent for — compliance is evaluated separately from certification in Universal's model | Parallel to certification, feeds the Compliance Report | Rule-framework level | Universal only |
| `CertificationClass` (EC-1) | Categorizes *what kind* of thing was certified | Descriptive, attached to the record | Record-level | EC-1 only |

No normalization is proposed here — this section only records what exists.

---

## 5. Duplication Test

Applying the stated test — *"two modules are duplicate only if they claim the same authority, represent the same truth, operate at the same lifecycle boundary, and produce interchangeable outputs"* — to the one pair worth testing (`platform/certification` fails the test trivially: it is an explicit, self-declared **projection**, not a candidate for duplication):

| Criterion | `engine/certification` vs. `engine/universal_certification` |
|---|---|
| Same authority claim? | **Yes** — both claim exactly none, in near-identical language |
| Same truth represented? | **Very likely yes** — identical `CertificationStatus` enum, same two values, same names |
| Same lifecycle boundary? | **Partially** — EC-1 is bound specifically to "the Validation Layer (EPIC-007)"; Universal is declared to accept validation from *any* producer, plus two additional input dimensions (Measurement, Repository Truth) EC-1 doesn't take |
| Interchangeable outputs? | **Not demonstrated** — nothing in the repository currently consumes both, or either one interchangeably; only EC-1 has a real consumer (`platform/certification`) |

**Result: fails full duplication on the fourth criterion (not currently interchangeable in practice), but passes the first two outright and the third partially.** This is not a clean "specialization" or "projection" either — Universal is not declared anywhere as EC-1's generalization, successor, or sibling, and EC-1's own docstring never acknowledges Universal exists. Both were last touched the same day (2026-07-31) with zero cross-reference between them, which is itself notable: every other pairing found across this and the prior Phase 0.7 discovery (CMG↔UCKP, RIE↔RPI, EC-1↔EC-2) is explicitly, extensively cross-referenced in its own docstrings. This pair is not.

**Classification: unresolved — closest to Gap Class B (duplicate capability), but not confirmed**, because "not currently interchangeable" could mean either (a) genuine accidental duplication that happened to never collide because nothing adopted the second one, or (b) a deliberately narrower EC-1 and a deliberately broader Universal that was built for future producers and simply hasn't been adopted yet. The evidence available from documentation and code structure cannot distinguish these two readings; only a history/design-intent check (git blame on the originating commits, or asking whoever built Universal) could.

---

## 6. Preliminary Determination

**"Does UCOS need one universal certification engine, or does UCOS need a governed certification ecosystem with shared semantics?"**

Based on repository truth gathered so far: **neither, as a first move.** The evidence does not support "consolidate into one engine" — `platform/certification` proves the EC-1↔EC-2 pairing already works exactly as a governed ecosystem should (one execution authority, one explicit projection, real imports, zero authority conflict, zero duplication). That pattern should be the model, not something to replace.

What the evidence *does* support:

1. **`engine/certification` (EC-1) and `platform/certification` (EC-2) require no governance work at all** — already correctly bound, already correctly disclaimed, already a clean AUTHORITY→PROJECTION pair.
2. **`engine/universal_certification`'s relationship to EC-1 is a genuine open question, not yet a confirmed duplicate and not yet confirmed as a deliberate specialization.** This is the one finding from this pass that needs resolution before any taxonomy work proceeds — attempting to build a "shared certification taxonomy" without first knowing whether Universal is dormant-duplicate or dormant-generalization risks encoding confusion into whatever taxonomy gets written.
3. **The live governance chain's own ad hoc verdicts** (RIB's `BLUEPRINT CERTIFIED`, AEE's `CONVERGED-PROVISIONAL`, CMG's `READY-PROVISIONAL`, Phase 8/9's `FIXED POINT CERTIFIED`/`REPRODUCIBILITY CERTIFIED`, UCEF's `CERTIFIED-PROVISIONAL`) **do not go through any of these three modules at all** — a separate, parallel vocabulary that this draft has not yet analyzed in depth. Whether that separation is correct (different lifecycle question — "is this measurement fixed-point stable" is not "is this subject validated-and-certified") or itself a gap is the larger question the full readiness determination still needs to answer.

**This draft does not recommend consolidation, and does not yet recommend governance-only binding either** — it recommends resolving finding #2 first, since it changes what "governance boundary" even means for that pair. No implementation follows from this draft. Feeding into the full `PHASE-CERTIFICATION-TAXONOMY-READINESS-DETERMINATION.md` next.
