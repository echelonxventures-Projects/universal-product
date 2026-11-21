# PHASE-UCF-011 — PROVIDER CATEGORY INTEGRITY OBSERVATIONAL IMPLEMENTATION

## Document Identity

| Field | Value |
|---|---|
| Phase | PHASE-UCF-011-PROVIDER-CATEGORY-INTEGRITY-OBSERVATIONAL-IMPLEMENTATION |
| Mission | Implement the minimum observational capability that detects provider category integrity risks, per `PHASE-UCF-010`'s READY determination for the Observational stage |
| Mode | Implementation. Engine change + tests. Zero constitutional change, zero invariant change, zero registry mutation, zero ownership records, zero blocking enforcement. |
| Date | 2026-08-14 |
| Base | `1f869865`, working tree as recorded in `PHASE-UCF-010 § 4` |
| Files changed | `engine/uckp/intelligence.py` (+152/−1), `engine/tests/uckp/test_category_integrity.py` (new, 23 tests) |

## Purpose

`PHASE-UCF-005` added a fourth provider that populated `metadata`, `runtime` and `artifact` — three categories already exclusively populated by native providers. Nothing in the constitution refused it. It was caught by an unrelated assertion that happened to pin `by_category("metadata") == 33`. That is luck, not a gate, and `PHASE-UCF-007` through `010` established why: category population is a *discovery* fact that no invariant governs, and no concept of category ownership exists for one to check against.

This phase builds the detection half — the half `PHASE-UCF-010` determined does not depend on the missing ownership evidence. It answers: *are category assignments across providers potentially inconsistent, ambiguous, or requiring future ownership clarification?* It does not answer *who should own what*, and deliberately cannot.

## Scope

In scope: category usage discovery, category integrity reasoning over the discovered map, observation findings carrying their own evidence, and deterministic tests for the positive, contamination, unknown and canonical-safety cases.

Out of scope, per explicit instruction and per `PHASE-UCF-009`/`010`: ownership enforcement, advisory or blocking validation, ownership ledger creation or population, new registries, provider authority redesign, category taxonomy redesign, and any parallel reasoning system.

---

## Current Repository Truth

Measured before implementation, and again after (§ Validation Results):

| Check | Before | After |
|---|---|---|
| `verify_binding()` | `()` — PASS | `()` — PASS |
| `discover()` | 4 providers, 5,982 objects, 0 failures | 4 providers, 5,982 objects, 0 failures |
| `validate_universe()` | `certified`, `blocking_failures=()` | `certified`, `blocking_failures=()` |
| `ukb.py enforce --pre` | PASS | PASS |
| `ukb.py validate` | PASS — 1,233 artifacts | PASS — 1,233 artifacts |
| Categories populated | 21 | 21 |
| Categories with >1 provider | 0 | 0 |

---

## Implementation Decision

### Reuse path confirmed before any code was written

The mission required confirming reuse rather than assuming it. Each element was read directly:

| Element | Finding | Decision |
|---|---|---|
| `gap_reasoning()` | Already builds `{obj.taxonomy.category for obj in objects}` — the exact sweep needed. Already emits `OBSERVATION` findings at category grain, addressed as `category:{name}`. | **Extended.** No new reasoner. |
| `Finding` model | `(reasoning, severity, subject, statement)`, frozen, shared by all thirteen reasoners, serialised into the version-pinned `ucos-uckp-intelligence-report` schema. | **Reused unchanged.** |
| `ReasoningKind` | A **closed 13-member enum** with a fixed 13-entry dispatch dict, pinned by four assertions across two test files (`test_state_evolution_intelligence_governance.py:320,322,353`, `test_cli_and_package.py:116`). | **Not extended.** See below. |
| Provider metadata | `discovery.provider` (Facet 21), populated on **5,982 / 5,982** objects — measured, not assumed. | **Reused as-is.** |
| Category extraction | `taxonomy.category`, mandatory at mint, lawfulness already enforced at admission by `require_lawful()`. | **Reused as-is.** |
| Evidence path | `ReasoningResult.findings` → `report()` → `ucos-uckp reason --json` / `describe --json` / `to_document()["intelligence"]`. | **Reused.** No new surface. |

### Why no new ReasoningKind — stated rather than silently avoided

The mission required that a new reasoning classification be justified before introduction. It was evaluated and **rejected**:

- **Why the existing classification suffices.** The condition being reported is *a declared thing with no corresponding resolution* — structurally identical to `gap_reasoning()`'s existing statement form, *"a governed category with no canonical object yet"*. An undeclared category owner is a gap in exactly that sense.
- **Architectural impact of adding one.** `ReasoningKind` is a closed enum, the same architectural class as `Facet` and `UCKP_INVARIANTS` (`PHASE-UCF-009`, `PHASE-UCF-010` D11). Opening it for this would set a precedent that every new question earns a fourteenth, fifteenth kind.
- **Test impact.** Four assertions pin the count at 13. Changing them to 14 would edit tests whose entire purpose is to detect exactly that change — the anti-pattern this arc has refused since `PHASE-UCF-005 § 2`.

`PHASE-UCF-009` recommended extending `risk_reasoning()`'s concentration shape; `PHASE-UCF-010 § 8` refined the *host* to `gap_reasoning()` while preserving that shape, on the evidence that `risk_reasoning()`'s subjects are uniformly `obj.ucko_id` and hosting a category-grain finding there would break its own subject convention. This implementation follows `PHASE-UCF-010`.

---

## Architecture Impact

**None to the architecture; additive within one module.**

| Layer | Impact |
|---|---|
| Constitution (`law.py`) | **Untouched.** Articles 20, invariants 17, stop conditions 13 — all unchanged, which `verify_binding()` independently confirms since it checks those three counts against `ROOT_LAW`. |
| Invariants / `validation.py` | **Untouched.** No probe added, removed or altered. `validation.py` contains zero references to `intelligence`, so certification cannot be reached by anything built here. |
| Registries | **Untouched.** No file written. No ownership record created. |
| Vocabulary / taxonomy | **Untouched.** No term registered; category names are read, never defined. |
| Registry / admission | **Untouched.** No change to `register()`, `discover()`, or any admission rule. |
| `intelligence.py` | One new value type, one new method, one extended reasoner, four new observation keys. |

---

## Files Changed

### `engine/uckp/intelligence.py` (+152 / −1)

| Addition | Purpose |
|---|---|
| `CATEGORY_EVIDENCE` constant | Names the evidence source (`taxonomy.category x discovery.provider`) cited by every category-integrity finding |
| `CategoryPopulation` dataclass | Frozen value type: `category`, `by_provider` (provider → object count, provider-sorted), `unattributed`; with `providers`, `objects`, `cite()`, `to_dict()` |
| `_category_populations()` | One pass over the objects, building the map |
| `UniversalIntelligence.category_populations()` | Public accessor — makes the evidence recomputable by a reader rather than internal to a finding |
| `gap_reasoning()` extension | Emits the integrity observations; adds four observation metrics |
| `__all__` | Exports `CATEGORY_EVIDENCE`, `CategoryPopulation` |

### `engine/tests/uckp/test_category_integrity.py` (new, 417 lines, 23 tests)

A dedicated module rather than additions to the 1,000-line intelligence suite, matching the `test_uga_projection.py` pattern `PHASE-UCF-009` named for this capability.

### Not written by this phase

Four `intelligence/UCOS-RIE-*` / `UCOS-IMP-*` metrics files were regenerated by `./verify.sh`'s own prerequisite stage, reflecting this phase's source-line count. They are generated measurements, not registries; no code in this phase writes them. Detail in § Validation Results.

**No other file was touched.** No constitutional document, no invariant, no registry, no vocabulary, no ownership record.

---

## Category Discovery Model

**Input:** existing registry objects, via `self._registry.objects()` — the same read surface all thirteen reasoners use. Deliberately *not* `registry.by_category()`, so the existing `RegistryView` test double keeps working unmodified (`PHASE-UCF-010` D16).

**Output:** `tuple[CategoryPopulation, ...]`, provider-sorted and category-sorted, therefore deterministic.

```
CategoryPopulation(
    category="metadata",
    by_provider=(("engine.uckp.constitution", 33),),
    unattributed=0,
)
```

**Whole-population by necessity, not preference.** `register()` runs per object; two providers populating one category is a lawful admission twice over — the first admits cleanly and the collision exists only once the second lands. Nothing at admission time can see it. This is the mechanical reason the check lives where it does.

**What the model refuses to do**, each verified by test:

- **Does not infer ownership.** Population is a Facet 21 discovery fact. It is never read as Facet 5 (authority) or Facet 7 (accountability). `PHASE-UCF-008` established that treating a Provider fact as an Owner fact is precisely the substitution that let `PHASE-UCF-005`'s contamination through; `test_category_usage_discovery_infers_no_ownership` asserts the map carries no owner field and that an object's `ownership.owner` never appears in a category statement.
- **Does not modify canonical data.** `test_observing_category_integrity_mutates_no_canonical_state` samples registry ids, every object's semantic digest, and the graph fingerprint before and after a full reasoning pass, and asserts every seal still verifies.
- **Does not create category records.** No object is minted; no vocabulary term is registered.

---

## Integrity Reasoning Model

Three conditions, evaluated per category.

### Case 1 — Potential category contamination

**Condition:** more than one distinct provider populates the category, and no declared owner reconciles them.

**Today: 0 occurrences.** Every one of the 21 populated categories has exactly one provider.

### Case 2 — Unknown ownership state

**Condition:** the category is populated, uncontested, and no ownership evidence exists for it.

**Today: 21 occurrences** — every populated category.

Unknown is treated as a valid knowledge state, not an error, failure or corruption. This is the distinction the whole observational stage exists to preserve: one populating provider is evidence of one *populator*, not of authority. Reporting it as a pass would certify an undeclared default as a decision; reporting it as a failure would condemn every category in the repository for a condition that has never produced a defect. `PHASE-UCF-009 § Invariant Semantic Model` named this three-way split; this implementation is its first executable form.

### Case 3 — Unattributed population

**Condition:** objects in the category name no provider at all.

**Today: 0 occurrences.** This branch is defence in depth: `UCKO.mint` coerces an empty provider to `engine.uckp`, so nothing minted lawfully arrives without one — but the guarantee lives in that single coercion, not in the type. `DiscoveryDescriptor.provider` is an ordinary string defaulting to empty, and no facet check refuses a blank one, because `Facet.DISCOVERY` resolves to the descriptor rather than to the field (verified directly: `missing_facets()` returns `()` for a provider-less object). Skipping such objects would report a clean attribution for a population the reasoner had not attributed. The branch is proven through `RegistryView`, following the pattern `doubles.py` documents for exactly this situation — *"a branch that never executes is a claim rather than a check."*

Case 1 and Case 2 are mutually exclusive by construction; a contested category reports contamination, not merely undeclared ownership. Case 3 is independent and may accompany either.

---

## Observation Model

Every finding is an `OBSERVATION`. No violation is emitted by any path added in this phase.

| Field required by the mission | Where it is carried |
|---|---|
| Observation identity | `Finding.reasoning` (`"gap"`) + `Finding.subject`, which together identify the observation uniquely within a report |
| Subject identity | `Finding.subject` |
| Category reference | `Finding.subject`, as `category:{name}` — the convention `gap_reasoning()` already established |
| Provider references | `Finding.statement`, each provider with its object count |
| Source data reference | `Finding.statement`, citing `CATEGORY_EVIDENCE` |
| Evidence location | `CategoryPopulation.to_dict()["evidence"]`, and `category_populations()` as the recomputable source |
| Reasoning explanation | `Finding.statement` |
| Confidence | Structural, not numeric — see below |
| Validation state | `Finding.severity` = `OBSERVATION`, and the report's `clean` flag, which excludes observations by definition |

Live example:

```
subject:   category:artifact
statement: is populated only by [engine.uckp.capabilities (10)], and no owner is
           declared for it: an undeclared default, not a decision
           (per taxonomy.category x discovery.provider)
```

**On confidence.** No numeric confidence is emitted, and none is invented. The repository has no confidence primitive, and `PHASE-UCF-010 § 7.3` determined that inventing one is unjustified by any evidenced need. Confidence here is carried structurally and honestly: contamination is a *measured fact* over the full population, and unknown is a *measured absence of declaration*. Attaching a number to either would assert precision the measurement does not have — the same category error `semantic_reasoning()`'s own comment already refuses when it declines to report a similarity score as a violation.

**No anonymous findings.** Every observation names its subject, its category, its providers, its counts, and the source it was measured from. `test_every_category_finding_names_its_subject_category_and_evidence_source` asserts each of these on a real finding.

---

## Evidence Model

The evidence is the population map itself, and it is **recomputable by the reader** — the property that separates evidence from assertion. `category_populations()` is public for exactly this reason, and `test_the_population_map_can_be_recomputed_from_the_evidence_a_finding_cites` independently reconstructs the map using only the two facets `CATEGORY_EVIDENCE` names, then asserts it equals what the reasoner reported.

Four metrics are added to `gap_reasoning()`'s `observations`, all additive (no existing key changed, and no test anywhere asserts an exact observation key set):

| Metric | Live value | Meaning |
|---|---|---|
| `categories_populated` | 21.0 | Categories holding at least one object |
| `categories_multi_provider` | 0.0 | Categories populated by more than one provider |
| `categories_without_declared_owner` | 21.0 | Populated categories with no declared owner — the number that falls as the ledger is populated |
| `categories_unattributed` | 0.0 | Categories holding objects that name no provider |

No evidence artifact is written to disk. Registering evidence as a canonical record would require minting objects into the `evidence` category — creating exactly the ownership-adjacent records this phase is forbidden to create, and populating a category that is currently at zero. The evidence lives in the report, which is where the existing reasoning infrastructure already puts it.

---

## Test Coverage

23 tests in `engine/tests/uckp/test_category_integrity.py`, all passing.

| Required scenario | Tests |
|---|---|
| **Positive case** — valid relationship, no contamination finding | `test_one_provider_populating_a_category_many_times_is_not_contamination` (volume is not plurality), `test_one_provider_spanning_several_categories_is_not_contamination` |
| **Potential contamination** — multiple providers, observation generated | `test_two_providers_populating_one_category_are_reported`, `test_a_contaminated_category_is_not_also_reported_as_merely_undeclared`, `test_contamination_is_reported_for_each_contested_category_independently` |
| **Unknown ownership** — populated, no evidence, UNKNOWN observation | `test_an_uncontested_category_is_reported_as_undeclared_not_as_agreed`, `test_every_populated_category_counts_as_undeclared_while_no_owner_exists`, `test_an_unpopulated_governed_category_is_not_reported_as_undeclared` |
| **Canonical safety** — no mutation of registry, identity, objects, certification | `test_observing_category_integrity_mutates_no_canonical_state`, `test_contamination_does_not_move_the_universe_verdict`, `test_reasoning_twice_reports_identically`, `test_every_category_integrity_finding_is_an_observation` |
| **Evidence model** | `test_every_category_finding_names_its_subject_category_and_evidence_source`, `test_the_population_map_can_be_recomputed_from_the_evidence_a_finding_cites`, `test_the_population_map_is_deterministic_and_provider_sorted`, `test_category_usage_discovery_infers_no_ownership` |
| **Unattributed population** | `test_an_object_naming_no_provider_is_reported_rather_than_skipped`, `test_a_partly_attributed_category_reports_both_its_provider_and_its_shortfall` |
| **Live repository regression** | `test_no_category_in_this_repository_is_populated_by_two_providers`, `test_every_object_in_this_repository_names_the_provider_that_minted_it`, `test_the_live_population_map_is_what_the_reasoner_reports`, `test_no_declared_owner_exists_for_any_category_yet` |
| Determinism | `test_category_integrity_reasoning_is_deterministic` |

**The regression gate `PHASE-UCF-005` did not have.** `test_no_category_in_this_repository_is_populated_by_two_providers` measures the live population rather than pinning a snapshot literal: a fifth provider that contaminates an existing category fails it by construction, while legitimate growth that adds *new* categories does not. That is the distinction the accidental `by_category("metadata") == 33` assertion could not draw, and the reason it caught the defect only by coincidence.

**Deliberately absent:** the ownership-conflict scenario (two authorities claiming one category). It is not constructible today — it needs a `category_ownership_resolution` ledger, a Blocking-stage prerequisite. A mocked version would assert against a shape no determination has settled, so it is left out and named here rather than faked.

**No ownership enforcement tests, no blocking tests, no invariant changes were added.**

---

## Validation Results

| Check | Result |
|---|---|
| `verify_binding()` | `()` — **PASS** |
| `discover()` | 4 providers, **5,982** objects, **0** failures |
| `validate_universe()` | **`certified`**, `blocking_failures=()` |
| `ukb.py enforce --pre` | **PASS** |
| `ukb.py validate` | **PASS** — 1,233 artifacts, referential integrity OK |
| `engine/tests/uckp/test_category_integrity.py` | **23 passed** |
| `engine/tests/uckp/` (full directory, isolated run) | **633 passed**, 0 failed — the 610 recorded at `PHASE-UCF-005 § 4` plus this phase's 23, i.e. **zero regressions and zero pre-existing tests modified** |
| `ruff check` / `ruff format` | **PASS**, both changed files |
| `ucos-uckp reason --json` | schema `ucos-uckp-intelligence-report` **1.0.0** unchanged, 13 reasoners, `clean: true`, 0 violations, `Finding` keys unchanged |
| **`./verify.sh`** | **VERIFICATION PASSED — all 8 stages green** |

`./verify.sh`, run in full because executable repository logic changed:

| Stage | Result | Time |
|---|---|---|
| ruff lint + format-check (engine + platform) | **PASS** | 0s |
| prerequisite generation (knowledge · determinism · closure 1–3) | **PASS** | 30s |
| pytest + coverage gate (`--cov-fail-under=90`) | **PASS** | 2864s |
| coverage report | **PASS** | 3s |
| governance enforce `--pre` | **PASS** | 0s |
| registry validate (schema + integrity) | **PASS** | 6s |
| meta-constitutional conformance (`CMG-INV-01..12`) | **PASS** | 0s |
| universal object governance (`UGA-INV-01..10`) | **PASS** | 4s |

Every invariant family reported zero violations: `UGA-INV-01..10`, `OBS-INV-01..13`, `CAA-INV-01..07`, and — via the pytest stage — `UCKP-INV-01..17`. The UGA gate's own counts are unchanged from `PHASE-UCF-005`'s baseline (`CAA-INV-02` measured 107, `CAA-INV-04` measured 5,827, `CAA-INV-07` measured 16), confirming no registry drift.

### Generated artifacts touched by the pipeline, reported rather than glossed

`./verify.sh`'s prerequisite-generation stage regenerated four repository-intelligence metrics files — `intelligence/UCOS-RIE-HEALTH.json`, `UCOS-RIE-MODEL.json`, `UCOS-RIE-CAPABILITY-CATALOG.json`, `UCOS-IMP-BASELINE-001.rib.json` (13 insertions, 10 deletions total). These are generated measurements, not registries or canonical objects, and no phase code writes them.

The change is `engine` source LOC `87494 → 87645`, i.e. **+151 — exactly this phase's net source change** (+152/−1 in `intelligence.py`), plus the content hashes that follow from it. Their `test_files` and `test_functions` counts did *not* move despite 23 new test functions, which was checked rather than assumed: `intelligence/rie/census.py:30-39` discovers files through `reader.tracked()` — git-tracked paths only, with a filesystem walk as fallback only when nothing is tracked. `engine/tests/uckp/test_category_integrity.py` is still untracked, so the census correctly excludes it. This is the generator behaving as designed against a working tree, not staleness and not drift; those two counts will move when the new test file is committed.

**Observations generated against the live repository:** 21 UNKNOWN, 0 contamination, 0 unattributed, **0 violations**. Total `gap_reasoning()` findings: 35 (14 pre-existing unpopulated-category observations + 21 new). `report()["clean"]` remains `True`; certification is unchanged.

This matches `PHASE-UCF-010 § 14`'s prediction exactly ("21 UNKNOWN observations, 0 contamination findings, `clean` unchanged, `certified` unchanged") — the readiness determination's forecast is confirmed by measurement, not assumed.

---

## Remaining Gaps

| Gap | Classification | Note |
|---|---|---|
| `category_ownership_resolution` section does not exist | **Required** (Advisory stage) | `PHASE-UCF-010` B1 |
| The ledger is unpopulated for all **21** categories | **Required** (Advisory stage) | B2 |
| No production reader exposes the ledger to engine code | **Required** (Advisory stage) | B3 — no `engine/` path opens the alignment binding today; the single genuinely new piece of infrastructure remaining |
| PASS cannot be distinguished from UNKNOWN | **Required** (Advisory stage) | Direct consequence of B1–B3; collapsed into UNKNOWN by design, not by omission |
| No conflict-resolution rule for contested categories | **Deferred** | Zero categories are contested; specifying adjudication ahead of any evidenced conflict is speculative |
| No sibling invariant family inside `engine/uckp/` | **Required** (Blocking stage) | B7 |
| Ledger not covered by `verify_binding()` | **Required** (Blocking stage) | B8 |
| Ownership-conflict test scenario not constructible | **Observational** | Blocked on B1–B3, not on this phase |
| Semantic-duplicate category registration | **Deferred** | Unchanged since `UCF-007` |
| Provider certification / pre-flight checklist | **Deferred** | Unchanged |
| Onboarding documentation | **Deferred** | Unchanged |
| `ReasoningKind` is a closed enum | **Observational** | Structural fact; shaped this implementation (extend, don't add) |

**Closed by this phase:** the detection gap itself — provider category contamination is now detected by a designed check rather than by coincidence, and the regression gate that would have caught `PHASE-UCF-005` at the right moment exists.

---

## Future Promotion Path

| Stage | Entry criteria | Status |
|---|---|---|
| **Observational** | Detection reachable without ownership evidence; findings non-gating; evidence recomputable | **Complete — this phase** |
| **↓ Advisory** | B1 ledger section exists; B2 populated for all 21 categories; B3 production reader; B4 regression fixture pinning the live population | B4 **done** (this phase); B1–B3 outstanding |
| **↓ Blocking** | B5 UNKNOWN empty; B6 conflict-resolution rule; B7 sibling invariant family; B8 ledger under a verifier | All outstanding |

**The promotion signal is built in.** `test_no_declared_owner_exists_for_any_category_yet` asserts `categories_without_declared_owner > 0`. The day a `category_ownership_resolution` ledger is populated and read, that test fails first — deliberately. It is the tripwire that says the advisory stage has served its purpose and the promotion criteria are live, answering `uga_engine.py`'s own recorded warning that an exemption outliving the condition that justified it is *"exactly how a gate quietly stops gating."*

---

## Final Implementation Determination

The provider category integrity observational capability is implemented, tested and validated. It detects the `PHASE-UCF-005` contamination class through a designed check rather than an accidental assertion, reports every finding with the evidence needed to recompute it, and does so without touching the constitution, the invariants, any registry, the taxonomy, the provider authority model, or the admission path.

It reuses what already existed: the `Finding` model unchanged, the closed `ReasoningKind` enum unopened, `gap_reasoning()` extended rather than duplicated, `discovery.provider` and `taxonomy.category` read as they are, and the existing report path as the only output surface. One value type and one accessor were added — both because the evidence behind a finding must be recomputable by its reader, not because the architecture needed changing.

The capability infers no ownership, and is built so that it cannot: population is a discovery fact, and the three constitutional questions of discovery, authority and accountability are held apart here exactly as Article 6 holds them apart. What it reports today is 21 categories whose ownership has never been declared and 0 that are contested — an honest statement of an undeclared default, which is neither a pass nor a failure, and which becomes answerable only when the ownership evidence `PHASE-UCF-010` named as B1–B3 exists.

Certification is unchanged. The universe remains `certified`, with zero blocking failures and zero violations from any path added here.

### Unresolved questions, carried forward

1. Should the ledger reader (B3) live in `alignment.py` — which already owns the binding's contract and declares its path but is deliberately pure-functional over a caller-supplied mapping — or in a new module? Adding file I/O to `alignment.py` changes its character; unresolved since `PHASE-UCF-010`.
2. Should the ledger backfill (B1/B2) be its own phase or land with the Advisory implementation? Still open from `PHASE-UCF-008`/`009`/`010`. This phase adds one input: the live map in § Category Discovery Model is now machine-readable via `category_populations()`, so the backfill's source data no longer needs hand-computation.
3. Should the four `*_resolution` sections that have no machine reader (`existence`, `lifecycle`, `certification_authority`, `identity_namespace`) come under a verifier as a general repository concern, rather than solving reader coverage once for `category_ownership_resolution` alone? Raised in `PHASE-UCF-010 § 5.2`; still outside this arc's scope.
4. Does `Ownership.stewards` generalise to delegated category producers? Unresolved since `PHASE-UCF-008`; not needed by the Observational stage and untouched here.

---

Stopping after PHASE-UCF-011, as instructed.
