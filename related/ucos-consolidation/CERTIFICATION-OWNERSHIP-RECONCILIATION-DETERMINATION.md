# CERTIFICATION OWNERSHIP RECONCILIATION DETERMINATION

> **Mission:** Certification Taxonomy Consolidation Discovery — final reconciliation of the `engine/certification` vs. `engine/universal_certification` finding
> **Mode:** Discovery only. No code changes, no deletion, no renaming, no migration.
> **Date:** 2026-08-13

---

## 1. Certification Concept Ownership Matrix

| | `engine/certification` (EC-1) | `engine/universal_certification` (Universal) |
|---|---|---|
| **Concepts owned** | Criterion-level validation aggregation → single-subject `CertificationRecord`; `CertificationClass = ENGINEERING_READINESS` specifically | Rule-level validation aggregation **plus** Compliance framing **plus** quantified Measurement, over a 3-input-normalized `UniversalCertificationSubject` → `Certificate`; `CertificationClass = UNIVERSAL_READINESS` specifically |
| **Authority claim** | None (`ENGINEERING-EXECUTION-ONLY`, confers no constitutional finality) | None — identical disclaimer pattern |
| **Lifecycle boundary** | Bound specifically to "the Validation Layer (EPIC-007)" as upstream | Declared open to *any* producer supplying Validation + Measurement + RepositoryTruth |
| **Consumers** | `platform/certification` — real, multi-file imports (`facade.py`, `contracts.py`, `ledger.py`, `health.py`, `status.py`, `service.py`) | **None found outside its own test suite** |
| **Evidence** | `CertificationEvidence`, deterministic, content-addressed | Own `CertificationEvidence` (separate class), same determinism guarantee |
| **Own dedicated tests** | `engine/tests/certification/` | `engine/tests/universal_certification/` — **both independently, currently maintained; neither is abandoned** |
| **Canonical candidate for "what does CERTIFIED mean" at the object-validation grain** | **Yes, in practice** — it's the one actually load-bearing (an EC-2 platform layer depends on it) | Not currently canonical for anything, since nothing consumes it yet — but not disqualified either |
| **Reason** | Real, active consumer | Complete, tested, deliberately broader scope, simply not yet adopted by any consumer |

**A. Which one defines the canonical certification concept?** Neither claims to define "the" certification concept in general — each defines its own scoped concept (engineering-readiness of a validated subject vs. universal-readiness of any producer's normalized output). In *practice*, EC-1 is the one that matters today, because it's the one something else actually reads.

**B. Which one is an implementation engine?** Both — both are `AUTHORITY` class per the earlier draft's classification (execution capability, not projection).

**C. Which one is a platform service?** Neither — `platform/certification` is the platform service, and it wraps EC-1 specifically, not Universal.

**D. Are both actually required at different architectural layers?** Not "required" in the sense of both being load-bearing today — only EC-1 is. But they are not redundant with each other either: Universal answers a *broader* question (compliance-aware, measurement-quantified, multi-producer) that EC-1's narrower model cannot answer even in principle, since EC-1 has no `ComplianceStatus` or `Measurement` concept at all.

---

## 2. Contract Compatibility Analysis

| Element | EC-1 | Universal | Compatible / same? |
|---|---|---|---|
| Terminal verdict enum | `CertificationStatus.CERTIFIED` / `.NOT_CERTIFIED` | `CertificationStatus.CERTIFIED` / `.NOT_CERTIFIED` | **Identical name and values** |
| "What was attested" enum | `CertificationClass.ENGINEERING_READINESS = "engineering-readiness"` | `CertificationClass.UNIVERSAL_READINESS = "universal-readiness"` | **Same class name, genuinely different member and value** — corrected from the prior draft's assumption |
| Per-criterion status | `CriterionStatus` | `RuleStatus` | Different name for an analogous concept — independently invented vocabulary |
| Per-criterion severity | `CriterionSeverity` | `RuleSeverity` | Same pattern — different name, analogous role |
| Input model | Single `CertificationSubject` | Three separate types (`ValidationInput`, `MeasurementInput`, `RepositoryTruthInput`) composed into `UniversalCertificationSubject` | **Not compatible — structurally different, Universal strictly more general** |
| Compliance | *No equivalent* | `ComplianceStatus`, `ComplianceFinding` | **Universal-only concept, no EC-1 analog** |
| Measurement | *No equivalent* | `Measurement`, `MeasurementComparator` | **Universal-only concept, no EC-1 analog** |
| Final output artifact | `CertificationRecord` | `Certificate` | Different name, analogous role, different fields (Universal's carries Compliance + Measurement provenance EC-1's cannot) |

**Determination for this section: (B) similar but different bounded contexts, with one small area of (D) accidental shared vocabulary** — specifically and only the `CertificationStatus` enum's two members (`CERTIFIED`/`NOT_CERTIFIED`) are identical between them. Every other compared element either differs meaningfully or exists in only one of the two. This is not (A) exact duplicate models, and not (C) one deriving from the other — nothing imports or subclasses across the boundary.

---

## 3. Dependency Graph Analysis

- **EC-1 consumers:** `platform/certification/facade.py`, `contracts.py`, `ledger.py`, `health.py`, `status.py`, `service.py` — six files with live `from engine.certification.X import Y` statements, each cited in this session's earlier investigation.
- **Universal consumers:** none, outside `engine/tests/universal_certification/` itself.

**"What would break if either disappeared?"**

- **If `engine/certification` disappeared:** `platform/certification`'s facade, ledger, health check, status reporting, and service layer would all fail to import — the entire EC-2 Certification Console would be non-functional. This is a real, load-bearing dependency.
- **If `engine/universal_certification` disappeared:** only its own dedicated test suite (`engine/tests/universal_certification/`) would fail. No other module, engine, platform service, or live gate (`verify.sh`, `make rib-gate`, `make aee-gate`, `final_closure_engine.py`) references it anywhere.

This asymmetry is the clearest fact in this investigation: **one module is in active use; the other is complete, tested, and currently unused by anything else.**

---

## 4. Duplication Classification

Per the requested four-way test:

- **(A) True duplicate capability** — requires same truth, same authority, same lifecycle boundary. **Not met.** Lifecycle boundaries differ (EC-1 bound to EPIC-007's Validation Layer specifically; Universal open to any producer), and the two are not remotely interchangeable in scope (Compliance and Measurement exist only in Universal).
- **(B) Valid specialization** — different purpose, different lifecycle, different consumers. **Substantially met** — Universal is a genuine generalization with real additional scope (Compliance, Measurement, multi-input normalization) that EC-1 was never designed to cover; EC-1 is genuinely narrower and is the one thing actually wired into a consumer.
- **(C) Governance gap** — valid systems, ownership relationship missing. **Also met, narrowly** — nothing in either module's documentation states whether Universal is intended to eventually supersede EC-1, sit alongside it as a peer for different future producers, or something else. That relationship is genuinely undocumented.
- **(D) Taxonomy gap** — same concept, vocabulary ungoverned. **Met only for the single `CertificationStatus` enum**, not for the modules as a whole.

**Overall classification: primarily (B), with a narrow (C) — not (A), and (D) only at the single-enum level, not the module level.**

---

## 5. Recommended Architecture

### Option A — One canonical Certification model with projections

- **Benefits:** Would remove the one narrow vocabulary overlap entirely.
- **Risks:** Would require either deleting Universal's genuinely broader scope (Compliance, Measurement — real capability loss) or absorbing it into EC-1's narrower model (a real migration, not a governance act, and out of scope per this phase's constraints regardless).
- **Migration impact:** High, and explicitly forbidden by this phase's constraints ("no migration").
- **Governance impact:** Would need a new authority decision about which model wins.
- **Not viable within this phase's constraints, and not clearly justified even outside them** — Option A would destroy real, working, differently-scoped capability to fix a one-enum overlap.

### Option B — Two bounded certification domains with explicit ownership

- **Benefits:** Matches the evidence exactly: two genuinely different-scoped, both-currently-maintained engines, one load-bearing and one not yet adopted.
- **Risks:** Low — mainly the risk of stating the boundary incorrectly if done hastily.
- **Migration impact:** None.
- **Governance impact:** A single, explicit statement of each module's scope and of Universal's not-yet-adopted status would resolve the only real open question (Gap Class C) without touching either module.
- **Recommended.**

### Option C — Keep both but introduce semantic relationship binding

- **Benefits:** Nearly identical to Option B in substance; frames the fix as "bind the relationship" rather than "declare two domains," which is arguably the more accurate framing since the two modules are not fully independent — Universal is, at minimum, aware of validation and measurement in a way that overlaps EC-1's validation input.
- **Risks:** Low, same as B.
- **Migration impact:** None.
- **Governance impact:** Same mechanism this session has now used three times (CMG↔UCKP, dependency projections) — a recognition binding, not a new authority.
- **Also recommended — effectively the same action as Option B, described from the relationship side rather than the domain side.**

**Options B and C are not meaningfully different in this case and should be implemented together**: declare both domains explicitly (B) *and* record their relationship as "distinct scope, not yet a producer/consumer pair, Universal not currently adopted by anything" (C) in the same binding.

---

## 6. Final Determination

**"Is `CertificationStatus` one canonical truth that accidentally exists twice, or two valid concepts that happen to share vocabulary?"**

**The latter, with a precise qualification.** `CertificationStatus`'s two members (`CERTIFIED`/`NOT_CERTIFIED`) are the one piece of genuinely shared vocabulary — but they are shared because that is close to the only sensible pair of words for a binary certification outcome in English, not because one module copied or was meant to align with the other. Every other compared element — the criterion vocabulary (`Criterion*` vs `Rule*`), the `CertificationClass` values (genuinely different: `engineering-readiness` vs `universal-readiness`), the input models (single-input vs. three-input-normalized), the presence of Compliance and Measurement (Universal only) — diverges meaningfully. Both modules are independently, currently maintained with their own dedicated test suites; neither reads as abandoned. Only one (EC-1) is currently consumed by anything else in the repository.

**This is Gap Classification (B) Valid Specialization, with a narrow (C) Governance Gap** — not (A) true duplication, and not a module-wide (D) taxonomy problem. The correct remediation, when this phase's findings are acted on, is a governance recognition binding (Options B/C combined) stating each module's actual scope and Universal's currently-unconsumed status — not consolidation, not deletion, not renaming.

This closes the one blocking precondition identified in `PHASE-CERTIFICATION-TAXONOMY-READINESS-DETERMINATION.md` §9. The ~10 other certification surfaces in that determination's inventory were never blocked by this question and remain ready for the same governance-binding treatment independent of this finding.

No code was changed, nothing was deleted, nothing was renamed, nothing was migrated. Discovery only, as instructed.
