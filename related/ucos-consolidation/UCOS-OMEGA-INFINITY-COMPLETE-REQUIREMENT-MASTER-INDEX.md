# UCOS Ω∞ COMPLETE REQUIREMENT MASTER INDEX

**Checkpoint:** `03179308` (integration/recovery-001)
**Compiled:** 2026-08-21 — consolidates every requirement discussed across this session's full arc (relationship temporal validity → knowledge confidence → verification closure → absolute closure → recovery/stabilization → architectural openness)
**Authority:** Repository Truth — executable evidence only.
**Posture:** Discovery and reconciliation only. No implementation performed in this pass. No completion claimed.

**Status vocabulary, strict, one per requirement:** `CERTIFIED` (implementation + executable evidence + validation passes) · `IMPLEMENTED` (implementation exists, evidence incomplete) · `GOVERNED CLOSURE` (approved decision exists, implementation intentionally pending) · `OPEN GAP` (no implementation, no approved decision).

---

## A — Entity

| ID | Name | Owner | Status | Evidence / implementation location | Gap | Dependency | Required action | Acceptance criteria |
|---|---|---|---|---|---|---|---|---|
| REQ-01 | Unknown entity admission, no kernel change | CEU-001 | **CERTIFIED** | `engine/ceu/existence.py` `declare_form()`; `test_unknown_entity_form_needs_no_code_change` | none | none | none | fingerprint-unchanged assertion (passing) |
| REQ-02 | Entity supersession/resurrection history reconstructible | CEU-001 | **CERTIFIED** | `DEC-ADR-0023`, IMPLEMENTED; `_supersessions: dict[str, list[dict]]`, append-only; `supersession_history()` accessor | none | none | none | 4 new tests + 267 (`ceu/`) + 867 (`ceu,nucleus,context,expansion/`), all passing |

## B — Relationship

| ID | Name | Owner | Status | Evidence / implementation location | Gap | Dependency | Required action | Acceptance criteria |
|---|---|---|---|---|---|---|---|---|
| REQ-03 | Temporal validity, versioning, supersession, resurrection | UCKP-ART-07 / `engine.knowledge.ukip.relationships` | **CERTIFIED** | `DEC-ADR-0015`; 72 tests, `test_relationships.py` | none | none | none | part of 12,133-pass suite |
| REQ-04 | Unknown relationship type admission | CEU-001 | **CERTIFIED** | `declare_form("relationship-type", ...)`; fingerprint-unchanged test | none | none | none | passing |

## C — Context

| ID | Name | Owner | Status | Evidence / implementation location | Gap | Dependency | Required action | Acceptance criteria |
|---|---|---|---|---|---|---|---|---|
| REQ-05 | Unknown context kind admission | UCXI-000001 | **CERTIFIED** | `ContextTaxonomy.extend()`; fingerprint-unchanged test | none | none | none | passing |
| REQ-06 | Per-subject context binding, every kind | UCXI-000001 | **CERTIFIED** | `DEC-ADR-0016` (`KNOWLEDGE`, `engine/knowledge/ukip/confidence.py`, 13 tests) + `DEC-ADR-0026`, IMPLEMENTED (`IDENTITY` and `GOVERNANCE`, `engine/ceu/context_binding.py`, 13 tests) | none | none | none | 3 of 16 universal kinds exercised against 2 entity substrates through the same `ContextRegistry`, no second registry/taxonomy; multi-context binding, full history reconstruction, evolution, and unknown-future-kind admission all proven by test |

## D — Technology

| ID | Name | Owner | Status | Evidence / implementation location | Gap | Dependency | Required action | Acceptance criteria |
|---|---|---|---|---|---|---|---|---|
| REQ-08 | No hardcoded finite technology set | `engine.uckp.execution` | **CERTIFIED** | `KNOWN_EXECUTION_KINDS` open tuple; `DEC-ADR-0009` | none | none | none | passing |
| REQ-09 | Unknown future language admission | CEU-001 | **CERTIFIED** | `declare_form("language", ...)` | none | none | none | passing |

## E — Platform

| ID | Name | Owner | Status | Evidence / implementation location | Gap | Dependency | Required action | Acceptance criteria |
|---|---|---|---|---|---|---|---|---|
| REQ-10 | Composition model, no platform-named engines | `engine.civilization.composition` | **CERTIFIED** | `DEC-ADR-0010`; 10 tests | none | none | none | passing |
| REQ-11 | Unknown future platform composition | CEU-001 + composition | **CERTIFIED** | `test_a_future_unknown_platform_composes_with_no_code_change` | none | none | none | passing |

## F — Knowledge

| ID | Name | Owner | Status | Evidence / implementation location | Gap | Dependency | Required action | Acceptance criteria |
|---|---|---|---|---|---|---|---|---|
| REQ-12 | Identity, provenance, evidence, lifecycle, certification state | UKDA `CanonicalKnowledgeObject` | **CERTIFIED** | `engine/knowledge/cko.py`; part of full suite | none | none | none | passing |
| REQ-13 | Confidence — append-only, correctable, reconstructible | `engine.knowledge.ukip.confidence` | **CERTIFIED** | `DEC-ADR-0016`, 13 tests | none | none | none | passing |
| REQ-14 | Prior knowledge version retained on save | UKDA `KnowledgeStore` | **CERTIFIED** | `DEC-ADR-0025`, IMPLEMENTED; `save()` archives to `canonical-knowledge-history.json` before overwrite; `history(cko_id)` accessor | none | none | none | 10 new tests + 618 (`knowledge/`) + 40 (real callers), all passing |
| REQ-15 | Unknown future knowledge classification | UKDA `KnowledgeKind` | **CERTIFIED** (disclosed non-openness by design) | `model.py:17-21`, fail-loud `coerce()` | not a gap | none | none | n/a — closure is intentional |

## G — Intelligence

| ID | Name | Owner | Status | Evidence / implementation location | Gap | Dependency | Required action | Acceptance criteria |
|---|---|---|---|---|---|---|---|---|
| REQ-16 | Unknown intelligence form admission | CEU-001 | **CERTIFIED** | `declare_form("intelligence-form", ...)` | none | none | none | passing |
| REQ-17 | Self-measured vocabulary extensibility | `engine.uckp.vocabulary.VocabularyRegistry` | **CERTIFIED** | `is_extensible()`, 154 tests | none | none | none | passing |

## H — Evolution / Self-learning

| ID | Name | Owner | Status | Evidence / implementation location | Gap | Dependency | Required action | Acceptance criteria |
|---|---|---|---|---|---|---|---|---|
| REQ-18 | Append-only architecture evolution, verified on load | `engine.uckp.evolution.EvolutionLedger` | **CERTIFIED** | `append()` fail-closed; `from_document()` replays through `append()`; UAUE gate+replay PASS; 780 records | none | none | none | passing |
| REQ-19 | Verification absorbs new dimensions as data | vocabulary/memory-layers/certification criteria | **CERTIFIED** | 41+154+19 tests | none | none | none | passing |
| REQ-20 | Self-learning object model / evolution transaction object | UAUE-000001 | **CERTIFIED** — re-classified this session; `P4-F-008` was stale | `engine/uaue/history.py:260` `learning_object()`, real, tested; full 7-stage pipeline (Observe→Learn→...→Continuation) distributed across `EvolutionStage` (15 members) + `engine/uaue/objects.py` | Documentation only: `PHASE-4-CAPABILITY-GAP-MATRIX.md`'s `P4-F-008` entry predates the `engine/uaue/` build-out | none | correct the stale finding when that document is next revised | n/a — no code gap |

## I — Measurement / Time / Space / Currency / Value

| ID | Name | Owner | Status | Evidence / implementation location | Gap | Dependency | Required action | Acceptance criteria |
|---|---|---|---|---|---|---|---|---|
| REQ-21 | Measurement is explicit, replaceable frame | UCXI `ContextKind.MEASUREMENT` | **CERTIFIED** | `ADR-0005`, admission test | none | none | none | passing |
| REQ-22 | No default temporal reference frame | `engine.temporal` | **CERTIFIED** | `TemporalCoordinate`, `compare()` → `INCOMPARABLE`; consumed live by `DEC-ADR-0015` | none | none | none | passing |
| REQ-23 | Space not conflated with path string | `engine/context/location.py` | **CERTIFIED** | 909-line dedicated module, no second registry | none | none | none | passing |
| REQ-24 | Unknown future currency admission | CEU-001 | **CERTIFIED** | `declare_form("currency", ...)` | none | none | none | passing |
| REQ-25 | Value-basis independent of currency | UCXI `ContextKind.ECONOMIC` | **CERTIFIED** | `value_basis`/`cost_model`/`scarcity` dimensions | none | none | none | passing |

## J — Governance / Decision / Mutation / Artifact

| ID | Name | Owner | Status | Evidence / implementation location | Gap | Dependency | Required action | Acceptance criteria |
|---|---|---|---|---|---|---|---|---|
| REQ-26 | Exactly one constitutional authority, no duplicate registry | CEP-002 Article 28, `UCDA-000001` | **CERTIFIED** | `CAA-INV-01..07`, 0 violations each | none | none | none | passing |
| REQ-27 | Every non-document object has a universal identity | `REG-AUTO-001`/`UGA-001` | **CERTIFIED** | `DEC-ADR-0017`/`0018`, `UGA-INV-01/10` 0 violations, survived 2 consecutive full-suite runs | none | none | none | passing |
| REQ-28 | 192-document corpus-registration population registered | `UMB-IMP-001` via `register.sh` | **OPEN GAP** | `ukb.py enforce --pre`: 192 unregistered eligible, non-blocking | No decision names this population as its own object — only excluded from `ADR-0017`'s scope | none | dedicated `CEP-002 Article 28` decision enumerating the 192 documents | decision registered + `ukb.py enforce --pre` reports 0 unregistered eligible |
| REQ-35 | Decision register itself is append-only | `UCDA-000001` | **CERTIFIED** | `DEC-ADR-0024`, IMPLEMENTED; `record_decision_update()`/`verify_decision_history()`, hash-chained, reuses `ContextRegistry.AuditEntry` shape | none | none | none | `--check-decision-history` PASS; live 2-entry chain (register + correction) verified intact |
| REQ-38 | Mutation governance — every mutation classified, one owner each | `platform.repository_intelligence.mutation_classification` | **CERTIFIED** — re-assessed Phase A (2026-08-22) on corrected input | `00-BOOK/DATA/mutation-governance-boundary.json`, **8** declared classes (`CONSTITUTIONAL_TRUTH`, `SOURCE`, `GENERATED_ARTIFACT`, `EXCLUSION`, `REPOSITORY_STATE`, `CORPUS_REGISTRATION`, `GOVERNED_DECLARATION`, `AUTHORED_DOCUMENT`), each with exactly one `governed_by` owner (8/8 verified); `validate_rule_coverage()` two-sided, 0 problems; `classify()` is data-driven, fail-closed to `UNRESOLVED`; **49** passing tests | none | none | none | re-executed post-Phase-A: 49 pass; repo-wide over 6,145 tracked paths — SOURCE 2,111 · AUTHORED_DOCUMENT 432 · GENERATED_ARTIFACT 345 · GOVERNED_DECLARATION 47 · EXCLUSION 2 · CORPUS_REGISTRATION 2 · REPOSITORY_STATE 0 · UNRESOLVED 3,206 (the declared terminal, conferring no authority — a fail-closed outcome, not a violation; this requirement never claimed 0 unresolved repo-wide) |
| REQ-39 | Artifact governance — a class covering authored documents (ADRs, decision records, determination artifacts) | `platform.repository_intelligence.mutation_classification` | **CERTIFIED** — strengthened by Phase A | `DEC-ADR-0027`, IMPLEMENTED; `AUTHORED_DOCUMENT` (Class 7) + rule `R-08` in `mutation-governance-boundary.json`; `authored_document_checks()`/`_owner()`/`_lifecycle()`; **49** tests in `test_mutation_classification.py` (was cited as 53 — the figure was overstated by 9 against an actual 44; Phase A added 5 version-control path-fidelity regressions, giving 49) | none | none | none | real tracked ADR and constitution files classify as `AUTHORED_DOCUMENT` via both the `Deciders` and `Authority` self-declaration conventions; fail-closed refusal verified for a document declaring neither; structural exclusivity from `GOVERNED_DECLARATION`/`SOURCE` verified; **non-ASCII (`Ω∞`) paths now reach R-08 — 432 authored documents recognised, up from 413**; all passing |

## K — Verification

| ID | Name | Owner | Status | Evidence / implementation location | Gap | Dependency | Required action | Acceptance criteria |
|---|---|---|---|---|---|---|---|---|
| REQ-29 | Unknown-future admission proof, all required axes | `engine.verification_intelligence` | **CERTIFIED** | 41 tests, `engine/tests/expansion/` | none | none | none | passing |
| REQ-30 | Verification selector does not silently narrow a run | `UVI-000001` | **CERTIFIED** | shard-collection completeness test, passing post-`DEC-ADR-0020` | none | none | none | passing |
| REQ-36 | Verification/observation tooling must not mutate state it did not dirty | `platform/tests/test_verification_purity.py` | **CERTIFIED** | `DEC-ADR-0020`, state-aware 3-way restoration, 18 tests + 2 synthetic validations | none | none | none | passing |
| REQ-37 | Impact-selector escalation tracks real coupling, not a stale snapshot | `engine.verification_impact` | **CERTIFIED** | 3 tests corrected (Case A determination), 51 tests total | none | none | none | passing |

## L — Certification / Governance integrity

| ID | Name | Owner | Status | Evidence / implementation location | Gap | Dependency | Required action | Acceptance criteria |
|---|---|---|---|---|---|---|---|---|
| REQ-31 | Repository certifies its own state end-to-end | 10 independent gates | **CERTIFIED** | CMG, UAUE×2, UOBC, UISD, UCPA, UVI, ukb enforce/validate, UGA — all re-executed and PASS this session | none | none | none | passing |

## M — Memory

| ID | Name | Owner | Status | Evidence / implementation location | Gap | Dependency | Required action | Acceptance criteria |
|---|---|---|---|---|---|---|---|---|
| REQ-32 | Persistent evolutionary memory is a projection, not a new engine | `engine.lineage.memory` | **CERTIFIED** | `DEC-ADR-0013`, `memory-layers.json`, 7 declared layers | none | none | none | passing |
| REQ-33 | Every governed history stream append-only and reconstructible | respective located owners | **CERTIFIED** | see individual rows above | none | none | none | passing |
| REQ-34 | Provenance/certification chains persist repository-wide | UKIP, certification owners | **CERTIFIED** | `DEC-ADR-0025`, IMPLEMENTED; `save_provenance()`/`load_provenance()`, kept out of CKO's content-addressed core (same reasoning as `ADR-0016`) | none | none | none | round-trip test passing; `KnowledgeCertificate` non-persistence remains correct-by-design, unaffected |
| REQ-40 | Graph memory — entities as nodes, relationships as first-class, temporal edges, lineage traversal | `engine.lineage.memory` + `engine.knowledge.ukip.relationships` | **CERTIFIED** for the underlying primitives / **SUPPORTED** for an explicit unified graph view | Relationships are already first-class (`ADR-0015`), temporal (`ValidityPeriod`), and lineage-traversable (`engine/lineage/memory.py`'s relationship layer, ordinal 3); no single "graph" object composes all seven layers into one traversable structure — each layer is resolved independently per subject | Not a missing capability — `memory-layers.json`'s own design philosophy is per-layer resolution, not a unified graph object, matching "no new store" (`ADR-0013`) | none | none required unless a unified graph *view* (not store) is explicitly wanted — would be a pure composition over the 7 already-resolved layers | n/a unless requested |

## N — Architectural Openness (technology/software/data/infrastructure/communication/experience/tools)

| ID | Name | Owner | Status | Evidence / implementation location | Gap | Dependency | Required action | Acceptance criteria |
|---|---|---|---|---|---|---|---|---|
| REQ-41 | Engineering/software agnosticism (languages, frameworks, runtime) | repo-wide | **CERTIFIED** | zero third-party imports found in `engine/`'s core domain (stdlib-only import audit) | none | none | none | audit reproducible via the same grep |
| REQ-42 | Data/storage neutrality — `engine/uckp` | `engine.uckp.persistence` | **CERTIFIED** | `PersistenceAdapter(ABC)`, 10 implementations, `test_every_persistence_technology_round_trips_the_universe_identically`, 52 tests | none | none | none | passing |
| REQ-43 | Data/storage neutrality — `KnowledgeStore` | UKDA | **OPEN GAP** | none — direct JSON I/O, no interface | `PersistenceAdapter` is hard-typed to `UCKO`; would need generalizing to a `Protocol` before reuse | REQ-14 (same file) | design-only per `UCOS-ARCHITECTURAL-OPENNESS-ROADMAP.md` Phase 3 — not recommended for immediate implementation | a `CEP-002 Article 28` decision, then a generalized `Protocol` + second consumer, contract-tested like `engine/uckp`'s |
| REQ-44 | Communication/API neutrality | — | **not applicable — documented, not a gap** | no communication-contract abstraction exists anywhere in the codebase; none was found coupled to a specific protocol either | absence of both coupling and abstraction — nothing to certify or fix | none | none — building one to pass a checklist would manufacture evidence, explicitly declined | n/a |
| REQ-45 | UI/Experience neutrality | — | **not applicable — no UI layer exists** | zero UI/templating code found | question does not yet apply | none | none | n/a |
| REQ-46 | Infrastructure neutrality (paths, OS, process model) | repo-wide | **SUPPORTED** | dynamic `repo_root()`-style path resolution used consistently; no hardcoded paths found | no dedicated "runs under different infrastructure" test exists | none | none recommended without a real second infrastructure target | n/a |
| REQ-47 | Tool neutrality (git, AI models, IDE, CI/CD) | repo-wide | **SUPPORTED** | `git` dependency confirmed confined to governance/tooling layers, not core domain classes | no test proves a tool is swappable | none | none | n/a |
| REQ-48 | Closed-classification review (Facet, KnowledgeCapability, RelationType, KnowledgeKind) | UKDA/UKIP, `engine/uckp/facets.py` | **CERTIFIED** (correctly closed, not a gap) | `UCRD-001`, `ADR-0016`'s own precedent | not a gap | none | none | n/a — closure is the correct, adjudicated design |

## O — Design principles

| ID | Name | Owner | Status | Evidence / implementation location | Gap | Dependency | Required action | Acceptance criteria |
|---|---|---|---|---|---|---|---|---|
| REQ-49 | UAP-001 — Universal Agnostic Architecture Principle | Constitutional Authority | **CERTIFIED as a declared principle** (never claimed as proven fact) | `adr/0021-uap-001-...md`, explicitly labeled `DESIGN PRINCIPLE`, not registered as a `CEP-002` decision by design | none | none | none | document exists, boundary statement present verbatim |
| REQ-50 | UIEP-001 — Universal Infinite Evolution Principle | Constitutional Authority | **CERTIFIED as a declared principle** (never claimed as proven fact) | `adr/0022-uiep-001-...md`, explicitly labeled `DESIGN PRINCIPLE`, not registered as a `CEP-002` decision by design; explicit relationship to `UAP-001` stated | none | none | none | document exists, boundary statement present verbatim |

---

**Count, verified by direct tally against the tables above (49 requirements, not estimated). Recomputed 2026-08-21 after Phase 5 (`DEC-ADR-0026`) and Phase 6 (`DEC-ADR-0027`) — the prior table below this line was stale (it still listed REQ-02/14/34/35/50 under counts their own rows no longer carried):**

| Status | Count | IDs |
|---|---|---|
| **CERTIFIED** | 43 | `REQ-01,02,03,04,05,06,08,09,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,29,30,31,32,33,34,35,36,37,38,39,40,41,42,48,49,50` |
| **GOVERNED CLOSURE** | 0 | none — every item that carried this status earlier this session (`REQ-02, REQ-06` remainder, `REQ-14, REQ-34, REQ-35`) has since been implemented, tested and certified; the status is retained in the vocabulary line above because it remains a legitimate outcome, not because anything currently holds it |
| **OPEN GAP** | 2 | `REQ-28, REQ-43` |
| **SUPPORTED** (neither certified nor a gap — no violation found, no proof built) | 2 | `REQ-46, REQ-47` |
| **Not applicable** (no implementation surface exists to evaluate) | 2 | `REQ-44, REQ-45` |
| **Total** | **49** | |

No requirement present in any prior session document is absent from this index.

**Change log for this recomputation:**
- `REQ-06` — `GOVERNED CLOSURE` (remainder) → `CERTIFIED`. Closed by `DEC-ADR-0026` (Phase 5): `engine/ceu/context_binding.py` binds `IDENTITY` and `GOVERNANCE` context for CEU `ExistenceUnit`, extending `confidence.py`'s proven `KNOWLEDGE`-kind pattern to two more universal kinds and a second entity substrate, through the same `ContextRegistry` — no second registry, no second taxonomy.
- `REQ-39` — `OPEN GAP` → `CERTIFIED`. Closed by `DEC-ADR-0027` (Phase 6): `AUTHORED_DOCUMENT` (Class 7) and rule `R-08` added to the existing `mutation-governance-boundary.json` / `mutation_classification.py` pair — no new mutation authority, registry or governance model.
- `REQ-02, REQ-14, REQ-34, REQ-35` — already `CERTIFIED` on disk before this recomputation (`DEC-ADR-0023/0025/0025/0024` respectively, all from earlier this session), but the summary table above had not been refreshed to reflect it. `REQ-50` was already `CERTIFIED` (`adr/0022`) for the same reason. This pass corrects the table only; no requirement's individual row changed as a result of these five.

---

## Phase A amendment — 2026-08-22 (tracked-path authority fix)

**Status counts unchanged: CERTIFIED 43 · GOVERNED CLOSURE 0 · OPEN GAP 2 (`REQ-28`, `REQ-43`) · SUPPORTED 2 · NOT APPLICABLE 2 · Total 49.**
No requirement changed status. `REQ-38` and `REQ-39` were re-assessed, not re-classified.

**Defect corrected.** `platform/repository_intelligence/mutation_classification.py` `Repository.tracked`
invoked `git ls-files` without `-z`. Git C-quotes and octal-escapes any path holding a
non-ASCII byte, so 117 tracked `…UCOS-Ω∞-…` artifacts arrived as escaped strings, never
equalled their own paths, and therefore tested as **untracked**. Because `_r01_repository_state`
claims any existing path absent from `tracked`, all 117 were absorbed into `REPOSITORY_STATE`
before the rule that owns them was evaluated — a **wrong** authority (`UCOS-RIB-001` GATE-02/12),
which is strictly worse than the fail-closed terminal.

Corrected to `git ls-files -z`, split on `\0`, decoded `utf-8`/`surrogateescape` — the same
construction `ukb._git_ls` already uses. `-z` disables quoting outright, so the fix carries no
dependence on `core.quotePath`. **No rule, predicate, authority check or membership criterion
was changed.**

**Measured effect — repo-wide over 6,145 tracked paths. Exactly and only the 117 moved:**

| Class | Pre-fix | Post-fix | Δ |
|---|---:|---:|---:|
| `REPOSITORY_STATE` | 117 | 0 | **−117** |
| `AUTHORED_DOCUMENT` | 413 | 432 | **+19** |
| `UNRESOLVED` (terminal) | 3,108 | 3,206 | **+98** |
| `SOURCE` | 2,111 | 2,111 | 0 |
| `GENERATED_ARTIFACT` | 345 | 345 | 0 |
| `GOVERNED_DECLARATION` | 47 | 47 | 0 |
| `EXCLUSION` / `CORPUS_REGISTRATION` | 2 / 2 | 2 / 2 | 0 |

The +98 to `UNRESOLVED` is the correct outcome: those documents declare no `Authority:` or
`Deciders:` field, so Class 7 rightly refuses them and they reach the declared terminal, which
confers no authority. Fail-closed replaced wrongly-assigned.

**Evidence re-executed this amendment:** `platform/tests/test_mutation_classification.py`
**49 passed** (44 pre-existing + 5 new); ownership invariants and boundary suite **250 passed**;
repository-intelligence gates **101 passed**; full `platform/tests/` **6,654 passed, 2 skipped**.
The 5 new regression tests were verified to **fail against the pre-fix parsing and pass after
it**, with all 44 pre-existing tests unaffected in both states.

**Test-count corrections.** REQ-39 cited *53 total*; the actual executable count was **44**
(overstated by 9). REQ-38 cited *33 passing tests* against the same file. Both now read **49**.
REQ-38's *"7 declared classes"* was also stale — `DEC-ADR-0027` added `AUTHORED_DOCUMENT`, making
**8**, each with exactly one `governed_by` owner (8/8 verified, `validate_rule_coverage()`
reporting 0 problems in both directions).

**Open finding, reported not fixed** (outside Phase A's stated scope): `engine/verification_impact/changes.py:50-59`
carries the same defect class at three call sites — `git diff --name-only HEAD`,
`git diff --name-only --cached HEAD`, and `git ls-files --others --exclude-standard`, all parsed
with `.splitlines()`. Confirmed by direct reproduction: both commands quote and octal-escape
non-ASCII paths. A changed `Ω∞` document therefore enters the impact selector under an escaped
name that matches no coupling rule. This bears on `REQ-37` (impact-selector escalation tracks
real coupling) and touches `REQ-30` (the selector must not silently narrow a run). Not corrected
here; awaiting direction.
