# 14 — Universal Completeness Matrix

**Anchor** `c6c20fb` · every percentage is measured, and its denominator is stated

---

## 1 · Completeness by mandated dimension

| # | Dimension | Complete | Denominator | Measurement |
|---|---|---|---|---|
| 1 | **Identity** | **100.0%** | 1,204 registered objects | unique `universal_id` 1,204/1,204; 0 duplicate/malformed node IDs |
| 1b | Identity — UUID | **0.0%** | 1,204 | 0 objects carry a UUID |
| 1c | Identity — native | **31.5%** | 1,204 | 379 populated, 825 null, 7 collision groups |
| 2 | **Registration** | **100.0%** | 1,204 eligible artifacts | 0 unregistered, 0 unclassified, 0 invalid — `CK-REG-ENFORCE` PASS |
| 2b | Registration — committed (drift-free) | **0.0%** | 1 atomic transaction | `register.sh --guard` exit 3 at pristine anchor (**B-1**) |
| 3 | **Documentation** | **0.0%** | 1,204 | `description` empty for every object |
| 3b | Documentation — corpus instruments | **100.0%** | 2,642 governance files | present and located; 433 certification, 206 architecture, 134 constitution, 134 determination |
| 4 | **Architecture** | **100.0%** | 15 progress dimensions | `architecture` dimension APPROVED, literal 1.0 |
| 4b | Architecture — band completeness | **85.7%** | 7 bands | 6 of 7 reach `-018`; `14-SECURITY` stops at `-004` |
| 4c | Architecture — layer implementation | **81.8%** | 11 layers | layers 1–9 exist; layer 5 spec-only; layers 10–11 absent |
| 5 | **Implementation** | **100.0%** | 15 progress dimensions | `implementation` dimension IMPLEMENTED, literal 1.0 (source: GIT, **stale**) |
| 5b | Implementation — capability | **97.0%** | 66 capabilities | 64 IMPLEMENTED/CERTIFIED, 2 PLANNED (CIOA, CCE) |
| 5c | Implementation — execution spine | **0.0%** | 12 declared gaps | `G-01`…`G-12` all absent |
| 6 | **Validation** | **94.11%** line / **90.06%** branch | 34 packages in coverage source | passes the 90% floor |
| 6b | Validation — repository scope (LOC) | **56.9%** | 246,066 LOC | 140,068 in gate scope (**B-4**) |
| 6c | Validation — repository scope (tests) | **52.5%** | 8,307 test functions | 4,364 in `testpaths` (**B-4**) |
| 6d | Validation — unit obligation | **12.3%** | 236 RIB units | `GAP-VERIFICATION` = 207 missing |
| 6e | Validation — dimensions at zero | **0.0%** | 4 test dimensions | functional, integration, performance testing + execution all NOT_STARTED |
| 7 | **Certification** | **100.0%** | 10 twin certification domains | verdict CERTIFIED, 10/10 domains |
| 7b | Certification — unit obligation | **28.0%** | 236 RIB units | `GAP-CERTIFICATION` = 170 missing |
| 7c | Certification — aggregate constitutional | **92.9%** | 14 UCCEP gates | 13/14 PASS; **verdict NOT-CERTIFIED** (single blocking failure) |
| 7d | Certification — programme | **87.5%** | 16 UCCEP programmes | 14/16 PASS |
| 7e | Certification — ratified | **0.0%** | whole corpus | Tier T1 VACANT; ceiling = PROVISIONAL (**B-5**) |
| 8 | **Repository Mapping** | **100.0%** | 4,895 tracked files | all mapped and classified; 1,204/1,204 paths resolve; 0 orphan units |
| 9 | **Knowledge Mapping** | **100.0%** | 437 repo-scope concepts | all homed, 0 duplicate homes, 0 orphans |
| 9b | Knowledge Mapping — true corpus scope | **82.8%** | **528 concepts** | 437 homed, **91 unhomed** (**B-2**) |
| 10 | **Traceability** | **2.2%** | 1,204 × 13 dimensions | 10 dimensions at 0.0% (**B-3**) |
| 10b | Traceability — chain links intact | **20.0%** | 10 mandated links | 2 intact, 8 broken |
| 10c | Traceability — any spine populated | **22.7%** | 1,199 artifacts | 272 per REG-AUTO-001 UMB-IMP-002 |
| 11 | **Dependencies** | **100.0%** | 12,851 edges | 0 unresolved, 0 dangling, 0 malformed, 0 cycles |
| 11b | Dependencies — artifact-level declaration | **15.8%** | 1,204 | 190 populated, 1,014 empty |
| 11c | Dependencies — inverse consistency | **98.4%** | 4,774 `Depends-On` | 77 lack an inverse |
| 11d | Dependencies — unit connectivity | **99.6%** | 236 units | 1 (`engine`) has no measured edge |
| 12 | **Lifecycle** | **100.0%** | 1,204 | every object carries a status (6-value vocabulary) |
| 12b | Lifecycle — reached FINAL/CERTIFIED | **1.3%** | 1,204 | 9 FINAL + 7 CERTIFIED; 1,103 still ACTIVE |
| 13 | **Versioning** | **100.0%** | 1,204 | every object versioned; 0 unversioned in graph validation |
| 13b | Versioning — differentiating | **0.0%** | 1,204 | all at `1.0.0`; real lineage only in `change-ledger.json` |
| 14 | **Evidence** | **100.0%** | 66 capabilities | `evidence_present` true for 66/66 |
| 14b | Evidence — unit binding | **3.4%** | 236 units | `GAP-EVIDENCE` = 228 missing |
| 14c | Evidence — determinism | **100.0%** | 3 determinism checks | double-build, RIE regeneration, UCCEP self-seal all PASS |

## 2 · Portfolio dimension index (canonical owner: `UCOS-RIE-PROGRESS.json`)

**Reconciled dimension index: 26.7%** over 15 dimensions. Unit-validation: 94.11%.

| Dimension | Score | Status | Source | Stale |
|---|---|---|---|---|
| architecture | **100%** | APPROVED | MANUAL | no |
| certification | **100%** | CERTIFIED | MANUAL | no |
| implementation | **100%** | IMPLEMENTED | GIT | **yes** |
| unit_testing | **94.11%** | — | coverage | no |
| deployment | 50% | IN_PROGRESS | KUBERNETES | **yes** |
| portfolio | 50% | IN_PROGRESS | MANUAL | no |
| execution | **0%** | NOT_STARTED | MANUAL | no |
| functional_testing | **0%** | NOT_STARTED | MANUAL | no |
| integration_testing | **0%** | NOT_STARTED | MANUAL | no |
| performance_testing | **0%** | NOT_STARTED | MANUAL | no |
| release | **0%** | NOT_STARTED | MANUAL | no |
| build | **0%** | **BLOCKED** | GITHUB_ACTIONS | **yes** |
| operational | **0%** | **BLOCKED** | PROMETHEUS | **yes** |
| production | **0%** | **BLOCKED** | PROMETHEUS | **yes** |
| security | **0%** | **BLOCKED** | TRIVY | **yes** |

**6 of 15 dimensions are stale** (cursors last advanced 2026-07-15). **4 are BLOCKED** — and all four
are blocked by connector staleness rather than by a measured failure, so their `0%` is an *absence of
measurement*, not a measured zero. `build` reporting 0%/BLOCKED while `ec1-ci.yml` exists and
`make build` works is the clearest instance.

## 3 · Aggregate roll-up

| Domain | Weighted completeness | Basis |
|---|---|---|
| **Repository & registration** | **~95%** | discovery, mapping, classification, ownership all 100%; drift-free commit 0% |
| **Architecture** | **~90%** | layered, acyclic, orphan-free, single-owner; one truncated band, control plane unbuilt |
| **Identity** | **~65%** | surrogate identity perfect; UUID absent, native 31.5%, version non-differentiating |
| **Capability & implementation** | **~85%** | 64/66 built, 246K LOC, 8,307 tests; spine 0% |
| **Dependency** | **~90%** | graph complete and valid; artifact-level declaration 15.8% |
| **Knowledge** | **~83%** | 437/528 concepts homed; no dictionary |
| **Validation** | **~55%** | 94% coverage over 57% of the code; 4 test dimensions at zero |
| **Certification** | **~50%** | 13/14 gates, 10/10 twin domains — but NOT-CERTIFIED and ratification impossible |
| **Traceability** | **~2%** | the binding constraint |
| **Runtime / production** | **~5%** | deployment 50% and stale; execution/release 0%; production/operational BLOCKED |

## 4 · The completeness profile in one sentence

**Everything that a gate enforces is complete; almost everything that no gate enforces is not.**

| Enforced by a gate | Completeness |
|---|---|
| Registration, classification, ownership | 100% |
| Graph validity, acyclicity, no orphans | 100% |
| Determinism (double-build, self-seal) | 100% |
| Coverage over the *declared* scope | 94.11% |
| Capability↔unit resolution | 100% |

| Not enforced by a blocking gate | Completeness |
|---|---|
| Traceability (advisory only) | 2.2% |
| Coverage over the *actual* repository | 56.9% |
| Artifact description | 0% |
| Version differentiation | 0% |
| Native-identifier uniqueness | 7 collisions |
| Programme-scope acyclicity | 2 cycles |
| Corpus-inclusive knowledge closure | 82.8% |
| Runtime / production dimensions | ~5% |

This is the actionable insight of Wave-1: the repository's engineering discipline is real and
demonstrably effective **wherever it is mechanised**. The remediation for every open blocker is
therefore the same in kind — extend the gate boundary, not the effort.
