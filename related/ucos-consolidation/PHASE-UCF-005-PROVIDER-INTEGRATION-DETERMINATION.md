# PHASE-UCF-005 — PROVIDER INTEGRATION DETERMINATION

> **Mission:** Implement the UGA → UCKP existence projection declared in `existence_resolution`, through the existing `ucko_objects()` provider protocol.
> **Mode:** Provider implementation. No new engine, registry, authority, or duplicate completeness model.
> **Date:** 2026-08-13
> **Files touched:** `engine/uckp/uga_projection.py` (new), `engine/tests/uckp/test_uga_projection.py` (new), `engine/tests/uckp/conftest.py`, `engine/tests/uckp/test_assimilation.py`, `engine/tests/uckp/test_cli_and_package.py` (three existing test files updated to reflect the intentional extension). No engine, registry, or completeness-model file was modified.

---

## 1. What Was Implemented

`engine/uckp/uga_projection.py` — a fourth `ucko_objects()` provider, discovered automatically by `UniversalKnowledgeRegistry.discover()`'s existing default root (`engine.uckp`), with **zero changes to `discover()` itself**. It reads `00-MASTER/UCOS-UGA-001/02-UNIVERSAL-OBJECT-REGISTRY.json` — UGA's own generated, canonical output, never `uga_engine.py`'s classification functions directly — and projects each of its 5,789 entries into a `UCKO` via `UCKO.mint()` (the existing, established construction path every native provider already uses), populating:

- **Identity** — minted through `REPOSITORY_NAMESPACE` (`"ucos-repository"`), the exact namespace `identity_authority_resolution.derivation` already declares, with UGA's `universal_id` carried through verbatim as the local name.
- **Ownership** — UGA's `owner` field, unmodified.
- **Lifecycle** — UGA's two observed values (`AUTHORED`, `GENERATED`) mapped onto the registered `uckp.lifecycle-stage` vocabulary (`draft`, `implemented` respectively), total and fail-closed on any unrecognized third value.
- Category, authority tier, and knowledge-kind, each deterministically mapped from UGA's `object_class` — required by `UCKO.mint()`'s signature, not optional.

**UCKP Article 6 is unmodified and remains the only completeness authority** — `require_complete()`, `missing_facets()`, and the 33-facet definition were not touched. This provider supplies facts *into* that model; it does not redefine what "complete" means.

---

## 2. Three Real Defects Found by the Test Suite — Not Assumed Away

The implementation did not pass on the first attempt. Rather than adjust the tests to match a broken implementation, each failure was traced to its root cause and the *provider* was fixed. Reported here in full because this session's discipline is to report what actually happened, not what was planned:

### 2.1 `derives_from` cited a bare article ID, not a real graph node

First attempt used `derives_from="UCKP-ART-08"`. `engine/uckp/graph.py:80-82` turns every object's `authority.derives_from` into a `-derived-from->` graph edge unconditionally; `engine/uckp/universe.py`'s `require_coherent()` then refuses any edge whose target is not itself a minted UCKO. An article ID is text, not a node — this produced 5,789 dangling edges and crashed every test that builds the assimilated universe (`engine/tests/uckp/conftest.py`'s `assimilated` fixture), not merely failed an assertion. **Fixed** by deriving from `engine.uckp.constitution.root_law_urn()` — the same public function `engine/tests/uckp/test_alignment.py` already imports, pointing at the Root Law's own UCKO node, which `constitution.py` (always among the discovered providers) actually mints.

### 2.2 Category mapping contaminated a closed, one-per-facet category

First attempt mapped `CONFIGURATION_OBJECT → "metadata"`, `TOOLING_OBJECT → "runtime"`, and both document classes `→ "artifact"`. `test_every_facet_and_every_capability_has_a_canonical_object` asserts `by_category("metadata") == 33` exactly — one native object per `Facet` member, a closed invariant this provider had no way to know about except by running the test that already existed to catch exactly this. Measured the native providers' actual category histogram directly (`artifact=10, authority=17, capability=10, constraint=17, governance=20, identity=1, law=1, metadata=33, observation=13, principle=20, runtime=10, taxonomy=13, transition=15, validation=13`) and remapped every UGA object class to a category confirmed absent from that histogram (`policy`, `engine`, `verification`, `workflow`, `state`, `knowledge`, `concept`). Re-measured: `metadata` category count is exactly 33 again.

### 2.3 `mint()`'s default `runtime_bindings=()` violates UCKP-INV-12

`missing_facets()` does not flag an empty tuple as missing (only `None` and empty strings), so the objects were structurally facet-complete but still failed live validation: `UCKP-INV-12` (zero-runtime-lock-in) requires at least one bound runtime, and `constitution.py`'s own docstring explains why two is the actual minimum that proves the abstraction real. **Fixed** by passing `runtime_bindings=UNIVERSAL_RUNTIMES` — reused verbatim from `engine.uckp.constitution`, the identical triple every native object already binds, not a new declaration.

None of these three defects were visible from reading `ucko.py`'s dataclass alone; each was found only by running the actual, pre-existing validation suite against the real, growing universe — which is the reason the mission required deterministic tests before declaring this done, not after.

---

## 3. Deterministic Tests — 16 in `test_uga_projection.py`, All Passing

| Required property | Tests |
|---|---|
| Identity preservation | `test_every_urn_carries_the_uga_universal_id_verbatim`, `test_identity_is_injective_no_two_entries_derive_one_urn`, `test_minting_is_pure_same_entry_same_identity_every_call` |
| Ownership mapping | `test_ownership_is_carried_through_unmodified` |
| Lifecycle mapping | `test_lifecycle_map_is_total_over_every_value_uga_actually_emits`, `test_lifecycle_mapping_is_applied_consistently`, `test_unmapped_lifecycle_fails_closed_rather_than_guessing`, `test_unmapped_object_class_fails_closed_rather_than_guessing`, `test_category_map_is_total_over_every_object_class_uga_actually_emits` |
| Facet evaluation | `test_every_projected_object_answers_all_thirty_three_facets`, `test_require_complete_raises_for_none_of_them`, `test_certification_validation_verification_are_present_but_honestly_unattested` |
| Zero duplicate objects | `test_registry_admits_every_projected_object_with_zero_refusals`, `test_projection_count_matches_the_uga_registry_exactly` |
| Zero canonical contamination | `test_reading_the_uga_registry_does_not_mutate_it`, `test_projection_writes_no_file_anywhere` |

One correction from `PHASE-UCF-004`'s prediction, reported honestly: that document stated the projection would leave objects "short of `require_complete()`" (partial coverage). Direct measurement shows every projected object is in fact facet-**complete** (structurally — `missing_facets() == ()` for all 5,789), correctly `unattested` (not missing) on `certification`/`validation`/`verification`, since no authority has certified, validated, or verified them. This is a *better* outcome than predicted, and the discrepancy is noted rather than silently absorbed.

---

## 4. Validation

Run in full, in order:

| Check | Result |
|---|---|
| `verify_binding()` | **PASS** — `()`, zero findings |
| `uga_engine.py gate` — `CAA-INV-01` through `07` | **PASS**, 0 violations each, every count identical to before (10, 107, 9, 5827, 6, 5, 16) |
| `engine/tests/uckp/test_uga_projection.py` (16 new tests) | **PASS**, all 16 |
| `engine/tests/uckp/` (full directory, 610 tests) | **PASS**, all 610, zero regressions after the two legitimate test updates below |
| `discover()` live | `providers_found` includes `engine.uckp.uga_projection`; `objects_admitted: 5982` (193 native + 5,789 projected); `failures: ()` |
| `validate_universe()` (all 17 UCKP-INV) | **`verdict: certified`** |
| `./verify.sh` (full pipeline: ruff, 71,640-line coverage-instrumented pytest suite, governance enforce, registry validate, CMG gate, UGA gate) | **VERIFICATION PASSED — all 8 stages green** |

Two pre-existing tests were updated, both legitimately, not to paper over a bug:

- `test_discovery_finds_exactly_the_declarative_providers` — its whole purpose is to lock down the *known* provider set; a fourth, intentionally-added provider is exactly the change this test exists to surface, so its expectation was extended from three providers to four.
- `test_the_assimilated_universe_holds_the_constitution_and_the_corpus` / `test_certify_covers_validation_assimilation_and_the_universe` — both asserted `constitution_object_count + corpus_size` as the total universe size. A third, **live-measured** fixture (`uga_projection_size`, added to `conftest.py`, reading the same UGA registry file the provider itself reads — never a hardcoded literal) was added, following the exact pattern `corpus_size` already established and documents in its own comment (`P0-BLOCKER-ERADICATION-001`: snapshot literals broke this suite on every legitimate corpus growth; measuring live retired that recurrence class). The new fixture extends that same discipline to the new population rather than reintroducing the problem it was designed to prevent.

---

## 5. Non-Goals

- No new engine, registry, or authority was created. `engine/uckp/uga_projection.py` is one provider module inside the existing `engine.uckp` package, discovered through the existing protocol.
- UCKP Article 6, `Facet`, `require_complete()`, and `UniversalKnowledgeRegistry.discover()` were not modified.
- UGA's own classification logic (`classify_object`, `derive_owner`) was not touched, imported as a library, or re-derived — only its generated output was read.
- No lifecycle engine was modified — the `_LIFECYCLE_MAP` is a projection-local translation table, not a change to `engine.knowledge.model.Lifecycle` or `UCL-000001`.
- The Evolution History open item (`lifecycle_resolution`) remains unresolved, as recorded — this phase did not touch it.
- `RIB`, `AEE`, `Phase-8`, `Phase-9` were not run — not requested for this phase and outside the "before further evolution work" boundary the mission set.

---

Stopping before any further evolution work, as instructed.
