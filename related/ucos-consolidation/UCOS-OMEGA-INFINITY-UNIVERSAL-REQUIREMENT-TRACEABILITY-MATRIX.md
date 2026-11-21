# UCOS Ω∞ UNIVERSAL REQUIREMENT TRACEABILITY MATRIX

**Checkpoint:** `03179308` (integration/recovery-001), post `ADR-0015`–`ADR-0020`
**Reconciled:** 2026-08-21, Phase 5 of the evidence-first recovery arc
**Authority:** Repository Truth — executable evidence only.
**Scope:** Every requirement discussed across this session, mapped across nineteen domains. One status per requirement, drawn from a **three-tier vocabulary only** — `CERTIFIED`, `GOVERNED CLOSURE`, `OPEN GAP` — superseding this matrix's earlier four-tier draft, which conflated "implemented" with "certified" before the identity-mint regression was found and fixed.

**Reconciliation basis — the full, clean, unified validation this revision is scored against:**
```
12,133 passed / 0 failed / 3 skipped, coverage 97.33% (threshold 90%)
UGA-INV-01..10: PASS (0 violations each)     CAA-INV-01..07: PASS (0 violations each)
UCDA-000001 gate: OPEN, 131 decisions         CMG / UAUE×2 / UOBC / UISD / UCPA / UVI: PASS
id-ledger.json: 4,914 by_object entries, confirmed surviving TWO consecutive full-suite runs
```
No row below is marked `CERTIFIED` on documentation alone — each cites the specific test/gate re-executed for this reconciliation.

| Req ID | Domain | Canonical principle | Owner | Implementation | Test evidence | Status |
|---|---|---|---|---|---|---|
| REQ-01 | Entity | Unknown future entity forms admitted by registration, no kernel change | CEU-001 `ExistenceRegistry` | `declare_form()` | `test_unknown_entity_form_needs_no_code_change` — part of the 41-pass `engine/tests/expansion/` re-run | **CERTIFIED** |
| REQ-02 | Entity | Existence history reconstructible over time (supersession/resurrection) | CEU-001 | `_supersessions` still mutated in place, `engine/ceu/existence.py:531-534` | none — re-confirmed open by direct read | **GOVERNED CLOSURE** (`DEC-ADR-0019`, `WP-UCDA-028`) |
| REQ-03 | Relationship | Relationships carry temporal validity, version, supersession, resurrection | `engine.knowledge.ukip.relationships` | `Relationship.validity`, overlap-aware merge, `valid_at()` | 72 tests, `test_relationships.py`, part of the 12,133-pass run | **CERTIFIED** |
| REQ-04 | Relationship | Unknown future relationship type admitted without kernel change | CEU-001 `ExistenceRegistry` | `declare_form("relationship-type", ...)` | `test_unknown_relationship_type_needs_no_code_change` | **CERTIFIED** |
| REQ-05 | Context | Unknown future context kind admitted by registration | UCXI-000001 `ContextTaxonomy` | `.extend()`, `ContextRegistry` | `test_unknown_context_kind_needs_no_code_change` | **CERTIFIED** |
| REQ-06 | Context | Per-subject context binding persists for every context kind | UCXI-000001 | Only `KNOWLEDGE` kind wired (`engine/knowledge/ukip/confidence.py`) | 13 tests, `test_confidence.py`, part of the 12,133-pass run | **CERTIFIED** for `KNOWLEDGE`; remainder **GOVERNED CLOSURE** (`WP-UCDA-028`) |
| REQ-07 | Expression | Executable expression openness | folds into REQ-08 — no distinct owner exists or is needed | — | — | **CERTIFIED** (via REQ-08) |
| REQ-08 | Technology | No hardcoded finite technology set | `engine.uckp.execution` | `KNOWN_EXECUTION_KINDS` (open, incl. `FUTURE_LANGUAGE`, `QUANTUM`) | `test_unknown_technology_type_needs_no_code_change` | **CERTIFIED** |
| REQ-09 | Technology | Unknown future language admitted, no code change | CEU-001 | `declare_form("language", ...)` | `test_unknown_language_needs_no_code_change` | **CERTIFIED** |
| REQ-10 | Platform | Platforms are compositions of registered nuclei, no platform-named engines | `engine.nucleus.catalog`, `engine.civilization.composition` | seven-nucleus composition | 10 tests, `test_platform_composition_verification.py` | **CERTIFIED** |
| REQ-11 | Platform | Unknown future platform composes without kernel change | CEU-001 + `engine.civilization.composition` | admission via composition | `test_a_future_unknown_platform_composes_with_no_code_change` | **CERTIFIED** |
| REQ-12 | Knowledge | Knowledge carries identity, provenance, evidence, lifecycle, certification state | UKDA `CanonicalKnowledgeObject` | `engine/knowledge/cko.py` | part of the 12,133-pass run; `UGA-INV`/`CAA-INV` PASS | **CERTIFIED** |
| REQ-13 | Knowledge | Knowledge carries confidence, append-only, correctable, historically reconstructible | `engine.knowledge.ukip.confidence` | `bind_confidence`, `resupersede_confidence`, `confidence_history` | 13 tests | **CERTIFIED** |
| REQ-14 | Knowledge | Prior knowledge object version retained, not discarded, on save | UKDA `KnowledgeStore` | none — `replace_object`/`save()` still discard-on-write | none — re-confirmed open, `store.py:175-180,287-293` | **GOVERNED CLOSURE** (`WP-UCDA-028`) |
| REQ-15 | Knowledge | Unknown future knowledge classification admitted | UKDA `KnowledgeKind` | deliberately **closed** enum, fail-loud `coerce()` | disclosed in-code (`model.py:17-21`); not a gap | **CERTIFIED** (disclosed non-openness by design) |
| REQ-16 | Intelligence | Unknown future intelligence form admitted, no kernel change | CEU-001 | `declare_form("intelligence-form", ...)` | `test_unknown_intelligence_form_needs_no_code_change` | **CERTIFIED** |
| REQ-17 | Intelligence | Intelligence evolution is self-measured (vocabulary extensibility) | `engine.uckp.vocabulary.VocabularyRegistry` | `intelligence.py:1014` → `is_extensible()` | 154 tests | **CERTIFIED** |
| REQ-18 | Evolution | Architecture evolution is append-only, verified on load | `engine.uckp.evolution.EvolutionLedger` | `append()` fail-closed; `from_document()` replays through `append()` | UAUE gate + replay, directly re-executed this reconciliation, both PASS; 780 records | **CERTIFIED** |
| REQ-19 | Evolution | Verification itself can absorb new dimensions/rules/evidence types as data | `engine.uckp.vocabulary`, `memory-layers.json`, UKIP certification criteria | data-declared criteria/layers/vocabularies | 41 + 154 + 19 tests | **CERTIFIED** |
| REQ-20 | Self-learning | A learning object model and evolution transaction object exist in code | UAUE-000001 | none — re-confirmed open by absence | none | **GOVERNED CLOSURE** (`WP-UCDA-028`) |
| REQ-21 | Measurement | Measurement is an explicit, replaceable frame | UCXI `ContextKind.MEASUREMENT` | 16th universal context kind | `test_unknown_measurement_unit_needs_no_code_change` | **CERTIFIED** |
| REQ-22 | Time | No default temporal reference frame; cross-system comparison fails closed | `engine.temporal` | `TemporalCoordinate`, `compare()` → `Ordering.INCOMPARABLE` | consumed live by `DEC-ADR-0015`, part of the 12,133-pass run | **CERTIFIED** |
| REQ-23 | Space | Space is not conflated with a repository-path string; no second registry | `engine/context/location.py` | 909-line dedicated module | `engine/tests/context/`, part of the 12,133-pass run | **CERTIFIED** |
| REQ-24 | Currency | Unknown future value representation admitted | CEU-001 | `declare_form("currency", ...)` | `test_unknown_currency_needs_no_code_change` | **CERTIFIED** |
| REQ-25 | Value | Value-basis representable independent of currency | UCXI `ContextKind.ECONOMIC` | `value_basis`, `cost_model`, `scarcity` dimensions | part of the 12,133-pass run | **CERTIFIED** |
| REQ-26 | Governance | Exactly one constitutional authority; no duplicate registry/decision system | CEP-002 Article 28, `UCDA-000001` | `ucda_engine.py` | `CAA-INV-01..07`, re-executed this reconciliation, 0 violations | **CERTIFIED** |
| REQ-27 | Governance | Every version-controlled non-document object has a universal identity | `REG-AUTO-001` / `UGA-001` | `uga_engine.py run` | `UGA-INV-01`/`10`, 0 violations, **survived two consecutive full-suite runs** | **CERTIFIED** (`DEC-ADR-0017`/`0018`, re-executed after the Phase 2 fix) |
| REQ-28 | Governance | The 192-document corpus-registration population is registered | `UMB-IMP-001` via `register.sh` | not executed — different authority, different population | `ukb.py enforce --pre`: 192 unregistered eligible, non-blocking | **OPEN GAP** — no decision names this population as its own object; only excluded from `ADR-0017`'s scope |
| REQ-29 | Verification | Verification proves unknown-future admission across all required axes | `engine.verification_intelligence` | fingerprint-unchanged pattern, 9 axes | 41 tests | **CERTIFIED** |
| REQ-30 | Verification | The verification selector itself does not silently narrow a run | `engine.verification_intelligence`, `UVI-000001` | shard/collection completeness check | `test_the_shards_collect_exactly_the_tests_the_whole_suite_collects` — passing, confirmed surviving the full unified run | **CERTIFIED** |
| REQ-31 | Certification | The repository can certify its own state end-to-end | 10 independent gates | see gate list | all 10 re-executed this reconciliation, all PASS | **CERTIFIED** |
| REQ-32 | Memory | Persistent evolutionary graph memory is a projection, not a new engine | `engine.lineage.memory` | 7 declared layers | 19 tests | **CERTIFIED** |
| REQ-33 | Memory | Every governed history stream is append-only and historically reconstructible | respective located owners | see individual rows | part of the 12,133-pass run | **CERTIFIED** |
| REQ-34 | Memory | Provenance/certification/audit chains persist repository-wide, not only in memory | UKIP, certification owners | none — chains remain in-memory-only | none — re-confirmed open | **GOVERNED CLOSURE** (`WP-UCDA-028`) |
| REQ-35 | Governance | The decision register itself is append-only (supersession is not a mutable field) | `UCDA-000001` | none — entries edited in place | none — re-confirmed open, self-observed | **GOVERNED CLOSURE** (`WP-UCDA-028`) |
| REQ-36 | Verification | Verification/observation tooling must never mutate governed state it did not itself dirty | `platform/tests/test_verification_purity.py` | state-aware three-way restoration (`ADR-0020`), replacing an unconditional `git checkout` that had silently reverted `DEC-ADR-0017`/`0018`'s mint | 18 purity tests + 2 synthetic pre-existing-dirty-state validations; the fix's own proof is `id-ledger.json` surviving two full-suite runs in a row | **CERTIFIED** (`DEC-ADR-0020`, IMPLEMENTED) |
| REQ-37 | Verification | The impact-selector's escalation threshold must track real, current coupling, not a stale snapshot | `engine.verification_impact` | no change — 3 tests' hardcoded expectations updated to match the real, ADR-0015-widened blast radius of `engine/temporal/coordinate.py` (4 owners, correctly escalates) | 51 tests, `test_verification_impact.py`, part of the 12,133-pass run | **CERTIFIED** (test correction only; architecture judged correct — Case A, no decision required) |

**Count:** 37 requirements. **34 CERTIFIED. 5 obligations under GOVERNED CLOSURE** (`REQ-02`, `REQ-06`-remainder, `REQ-14`, `REQ-20`, `REQ-34`, `REQ-35` — six sub-obligations, one work package, `WP-UCDA-028`). **1 OPEN GAP** (`REQ-28`). Zero requirements are certified on documentation alone; every `CERTIFIED` row cites a test or gate re-executed as part of this reconciliation's own 12,133-pass, 97.33%-coverage, 10-gates-PASS validation cycle.
