# UCOS-RFP-001 — REPOSITORY FIXED-POINT GATE (G-15)

> GENERATED FROM `rfp-declaration.json` BY UCOS-RFP-001 — DO NOT EDIT BY HAND.
> Regenerate with `make rfp`. AUTHORITY = NONE (DERIVED TRUTH).
>
> This projection records the DECLARATION only. It carries no commit identity
> (RFP-2) and no observation of the working tree (RFP-3) — including the
> fixed-point verdict itself, which is carried by the gate's exit code and
> standard output. An artifact asserting "the repository is a fixed point"
> would falsify that sentence by being written.

## What the gate does

It executes the declared pipeline **2 times** over the committed HEAD and requires the repository to be byte-identical after every pass. Stability is an observation over repetitions: a fixed point seen once may be coincidence.

## Mandatory closure criteria

| ID | Criterion | Measure | Expect | Blocking |
|---|---|---|---|---|
| CLO-01 | the tree is clean before the fixed point is asserted | `initial_dirty_entries` | 0 | yes |
| CLO-02 | every required pipeline stage exits successfully | `stage_failures` | 0 | yes |
| CLO-03 | no tracked file is modified by any pass | `tracked_modifications` | 0 | yes |
| CLO-04 | no file is staged by any pass | `staged_entries` | 0 | yes |
| CLO-05 | no untracked entry appears outside a constitutionally excluded location | `untracked_outside_excluded` | 0 | yes |
| CLO-06 | the repository is byte-identical after every declared pass | `non_fixed_point_passes` | 0 | yes |
| CLO-07 | no self-reference cycle is detected | `cycles_detected` | 0 | yes |
| CLO-08 | all residue is attributable to a declared producer | `unattributed_paths` | 0 | yes |
| CLO-09 | every discovered producer is a declared pipeline stage | `undeclared_producers` | 0 | yes |
| CLO-10 | every path a producer writes lies inside a declared write zone | `producer_writes_outside_zones` | 0 | yes |
| CLO-11 | declared write zones are pairwise disjoint, so ownership is exactly one | `overlapping_write_zones` | 0 | yes |
| CLO-12 | no discovered producer candidate is left unprobed | `unprobed_producer_candidates` | 0 | yes |
| CLO-13 | no stage writes into another stage's declared write zone | `cross_zone_writes` | 0 | yes |

## The declared pipeline

| # | Stage | Owner | Heavy | Required | Re-entrant |
|---|---|---|---|---|---|
| 1 | `STAGE-PREREQUISITES` Declared prerequisite generation (knowledge · determinism · closure 1-3) | scripts/generate-prerequisites.sh | no | yes | yes |
| 2 | `STAGE-CERTIFICATION-INTEGRITY` Certification integrity gate | engine/certification_integrity | no | yes | yes |
| 3 | `STAGE-RECURSIVE-KNOWLEDGE` Recursive knowledge foundation gate | engine/recursive_knowledge | no | yes | yes |
| 4 | `STAGE-VERIFY` Verification and validation | verify.sh (CEP-004) | yes | yes | yes |
| 5 | `STAGE-REGISTER` Atomic registration transaction | 00-BOOK/tools/register.sh (REG-AUTO-001) | no | yes | yes |
| 6 | `STAGE-UIS` Universal identity conformance | 00-MASTER/UIS-001 | no | yes | yes |
| 7 | `STAGE-RIE` Repository intelligence | intelligence/rie (UCOS-RIE-001) | no | yes | yes |
| 8 | `STAGE-CLOSURE` Knowledge closure | 00-MASTER/UAKOS-CLOSURE-002 | no | no | yes |
| 9 | `STAGE-UCDA` Decision assimilation | 00-MASTER/UCDA-000001 | no | yes | yes |
| 10 | `STAGE-UEI` Evolution intelligence | 00-MASTER/UEI-000001 | no | yes | yes |
| 11 | `STAGE-UER` Execution resilience | 00-MASTER/UER-000001 | no | yes | yes |
| 12 | `STAGE-URRC` Repository reality matrices | 00-MASTER/URRC-000001 | no | yes | yes |
| 13 | `STAGE-UMK` Universal meta-kernel | 00-MASTER/UMK-000001 (PROGRAM-002) | no | yes | yes |
| 14 | `STAGE-UPF` Universal provider framework | 00-MASTER/UPF-000001 (PROGRAM-003) | no | yes | yes |
| 15 | `STAGE-MCOS` Universal Meta-Civilization Platform deliverables (PROGRAM-004) | 00-MASTER/MCOS-000001 | no | yes | yes |
| 16 | `STAGE-RIB` Repository integration blueprint | 00-MASTER/UCOS-RIB-001 | no | yes | yes |
| 17 | `STAGE-UKAP` Corpus currency | 00-MASTER/UKAP-001 | no | yes | yes |
| 18 | `STAGE-ASSIMILATE` Constitutional assimilation | 00-MASTER/UAKOS-CLOSURE-008 | no | yes | yes |
| 19 | `STAGE-URKE` Recursive knowledge declaration | 00-MASTER/URKE-000001 | no | yes | yes |
| 20 | `STAGE-NUCLEUS` Nucleus identifier dictionary | 00-MASTER/UCOS-NUCLEUS-001 | no | yes | yes |
| 21 | `STAGE-UAR` Analysis registry | 00-MASTER/UCOS-UAR-001 | no | yes | yes |
| 22 | `STAGE-UCAF` Constitutional authority | 00-MASTER/UCOS-UCAF-001 | no | yes | yes |
| 23 | `STAGE-BASELINE` Baseline inheritance | 00-MASTER/BASELINE-001 | no | yes | yes |
| 24 | `STAGE-URAT` Ratification registry | 00-MASTER/UCOS-URAT-001 | no | yes | yes |
| 25 | `STAGE-UTCE` Traceability closure | 00-MASTER/UCOS-UTCE-001 | no | yes | yes |
| 26 | `STAGE-UFEP` Freeze eligibility | 00-MASTER/UCOS-UFEP-001 | no | yes | yes |
| 27 | `STAGE-UAEP` Platform capability binding | 00-MASTER/UAEP-000001 | no | yes | yes |
| 28 | `STAGE-UAIE` Architectural intelligence | 00-MASTER/UAIE-000001 | no | yes | yes |
| 29 | `STAGE-UCEF` Constitutional evolution | 00-MASTER/UCEF-000001 | no | yes | yes |
| 30 | `STAGE-MXR` Master execution roadmap | 00-MASTER/UCOS-MXR-001 | no | yes | yes |
| 31 | `STAGE-PHASE3` Implementation gap baseline (operational memory) | 00-MASTER/UAKOS-PHASE-003 | no | yes | yes |
| 32 | `STAGE-PHASE3R` Realization correction (operational memory) | 00-MASTER/UAKOS-PHASE-003R | no | yes | yes |
| 33 | `STAGE-PHASE4` Implementation planning (operational memory) | 00-MASTER/UAKOS-PHASE-004 | no | yes | yes |
| 34 | `STAGE-PHASE5` Execution governance (operational memory) | 00-MASTER/UAKOS-PHASE-005 | no | yes | yes |
| 35 | `STAGE-PHASE6` Execution readiness certification (operational memory) | 00-MASTER/UAKOS-PHASE-006 | no | yes | yes |
| 36 | `STAGE-FREEZE-C4` Freeze C4 execution streams (operational memory) | 00-MASTER/UCOS-USIS-WAVE0 | no | yes | yes |
| 37 | `STAGE-UCL` Universal Constitutional Lifecycle (discover, order and execute the constitutional stage graph) | 00-MASTER/UCL-000001 | no | yes | yes |
| 38 | `STAGE-ACEE` Autonomous constitutional engineering (bind an engineering goal to the consumed lifecycle) | 00-MASTER/ACEE-000001 | no | yes | yes |
| 39 | `STAGE-LIFECYCLE-CLOSURE` Universal Constitutional Lifecycle realization measurement | 00-MASTER/P0-LIFECYCLE-CLOSURE-001 | yes | yes | yes |
| 40 | `STAGE-UCCEP` Aggregate constitutional certification | 00-MASTER/UCCEP-000000 | yes | yes | **no** |
| 41 | `STAGE-PHASE-001B` Constitutional provenance reconstruction registers | 00-MASTER/UAKOS-PHASE-001B | no | yes | yes |
| 42 | `STAGE-PHASE-001A-R1` Constitutional baseline re-certification registers | 00-MASTER/UAKOS-PHASE-001A-R1 | no | yes | yes |
| 43 | `STAGE-CLOSURE-009` Repository requirement closure registers | 00-MASTER/UAKOS-CLOSURE-009 | no | yes | yes |
| 44 | `STAGE-PHASE2` Repository reconciliation (operational memory) | 00-MASTER/UAKOS-PHASE-002 | no | yes | yes |

## Exit semantics

| Exit | Meaning |
|---|---|
| 0 | the repository is a Repository Fixed Point — gate OPEN |
| 1 | the repository is not a fixed point — gate CLOSED |
| 2 | fail-closed abort — declaration unusable, no verdict asserted |

## Why the gate records nothing

The verdict is an observation of the working tree. Persisting it would violate RFP-3 and make the record permanently false (Evidence Drift). The gate therefore reports through its exit code and standard output, and its generated artifacts carry the declaration alone.

---

*Enforce with `make rfp-gate`.*
