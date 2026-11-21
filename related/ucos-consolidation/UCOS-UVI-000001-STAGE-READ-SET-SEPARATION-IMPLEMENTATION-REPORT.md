# UCOS-UVI-000001 — Stage Read-Set Separation Implementation Report

**Artifact ID:** UCOS-UVI-000001-STAGE-READ-SET-SEPARATION-IMPL
**Programme:** UVI-000001 — Universal Verification Intelligence
**Step:** Implementation Sequence — **Step 3**
**Standing:** IMPLEMENTATION REPORT — records what changed and what was measured. Legislates nothing.
**Baseline:** branch `integration/recovery-001` at `b73ed34d`
**Date:** 2026-08-19
**Scope executed:** Step 3 only. No stage-level scheduling, no artifact closure integration, no scheduler change.

**Result:** **STEP 3 COMPLETE** — `./verify.sh --fast` PASSED, **14/14** UVI laws HOLD, 215 targeted tests green.

---

## 1. Problem

One field carried two independent facts.

`reuse_inputs` meant both **what a stage reads** — a dependency relation, always knowable — and **what may be answered from cache** — a deliberately restrictive policy. Because the two were fused in one declaration, a stage that must always run declared no inputs at all.

Measured at baseline: **8 of 15 stages declared `reuse_inputs`, and they were exactly the 8 declared `reusable`.** That correlation was not coincidence; it was the coupling.

The consequence is not a slow cache. It is that **seven stages were invisible to impact analysis**. `universal-object-governance` reads the whole version-controlled boundary — a perfectly declarable fact — and nothing could relate any change to it, because declaring what it reads would have implied it could be cached.

## 2. Existing Coupling

| Stage | `reuse_inputs` | `reusable` | Impact-visible |
|---|---|---|---|
| `ruff` | ✅ | ✅ | yes |
| `governance-pre` | ✅ | ✅ | yes |
| `registry-validate` | ✅ | ✅ | yes |
| `meta-constitutional` | ✅ | ✅ | yes |
| `autonomous-evolution` | ✅ | ✅ | yes |
| `evolution-replay` | ✅ | ✅ | yes |
| `object-birth` | ✅ | ✅ | yes |
| `verification-intelligence` | ✅ | ✅ | yes |
| `prerequisites` | ❌ | ❌ | **no** |
| `pytest` | ❌ | ❌ | **no** |
| `universal-object-governance` | ❌ | ❌ | **no** |
| `infinite-scope` | ❌ | ❌ | **no** |
| `primitive-alignment` | ❌ | ❌ | **no** |
| `coverage-report` | ❌ | ❌ | **no** |
| `registration-observation` | ❌ | ❌ | **no** |

The two columns are identical. That is the defect stated as data.

### 2.1 A second defect the coupling concealed

Because `reuse_inputs` was authored as a *cache* declaration, it was authored narrowly. Measured against the import closures the dependency graph already publishes:

| Stage | declared `reuse_inputs` | actual import closure roots | omitted |
|---|---|---|---|
| `object-birth` | `00-MASTER/UOBC-000001/`, `engine/object_birth/` | + `engine/uckp/`, `engine/foundation/` | **2** |
| `autonomous-evolution` | `00-MASTER/UAUE-000001/`, `engine/uaue/` | + `engine/uckp/`, `engine/nucleus/`, `engine/foundation/` | **3** |
| `evolution-replay` | same | same | **3** |
| `primitive-alignment` | *(none)* | `engine/root_ontology/`, `engine/uckp/`, `engine/foundation/` | all |

So a change to `engine/uckp/` did **not** invalidate `object-birth`'s cache, although `object-birth` imports it. That is a false-reuse vector of the same class as the two closed in Steps 1 and 2, and it was found by deriving read-sets from measurement rather than copying the old field.

## 3. New Declaration Model

Two independent declarations per stage:

```
read_set        a DEPENDENCY RELATION  — mandatory for every stage
                used for impact analysis AND for the evidence input digest
reusable        a CACHE POLICY         — unchanged, and still refused for certification
```

`StageSpec` gained `read_set` plus a `reads` property:

```python
@property
def reads(self) -> tuple[str, ...]:
    """The effective read-set: the declared one, or reuse_inputs in compatibility."""
    return self.read_set or self.reuse_inputs
```

**`reuse_inputs` was not removed.** A declaration written before the separation still resolves, through the fallback above, and `test_step3_reuse_inputs_still_resolves_without_a_read_set` measures that it does. Migration is by compatibility, as required.

### 3.1 The whole-boundary token

Four stages have a subject that genuinely is the tree. Enumerating roots for them would produce a list that silently fails to cover a root added later — the exact failure mode UISD-000001 refuses everywhere else. So the read-set vocabulary gained one declared token:

```
"**"   the whole version-controlled boundary
```

`resolve_prefix` expands it to every object in the universal registry (**6,113**). It is not a glob and no other wildcard exists; it is a single declared constant, `WHOLE_BOUNDARY`, documented at its definition.

### 3.2 What consumes the read-set

| Consumer | Uses | Note |
|---|---|---|
| `input_digest` | `stage.reads` | replaced `stage.reuse_inputs` |
| `stages_reading()` | `stage.reads` | **new** — the query the coupling hid |
| `decide()` | `stage.reusable` | unchanged; policy only |

`stages_reading(stages, substrates, paths)` answers *"which stages does this change reach"*. It is a **query, not a scheduler**: nothing decides what runs, and `./verify.sh` still executes exactly the stages its mode admits. Stage-level impact *selection* is a later step.

## 4. Migration

Every read-set was **derived**, never copied from the reuse policy. Python entry points were resolved through the UGA import graph; shell entry points were read; declaration homes were located from the engines' own constants.

| Stage | `read_set` | reusable |
|---|---|---|
| `ruff` | `engine/`, `platform/`, `pyproject.toml` | true |
| `prerequisites` | `scripts/`, `engine/knowledge/`, `engine/determinism/`, `intelligence/research/`, `intelligence/publication/`, `intelligence/realization/`, `00-MASTER/UAKOS-CLOSURE-002/`, `00-MASTER/UAKOS-PHASE-001B/`, `00-BOOK/DATA/` | false |
| `pytest` | `**` | false |
| `governance-pre` | `00-BOOK/`, `00-SOURCE/` | true |
| `registry-validate` | `00-BOOK/DATA/`, `00-BOOK/SCHEMAS/`, `00-BOOK/tools/` | true |
| `meta-constitutional` | `00-CMG/`, `00-BOOK/DATA/` | true |
| `universal-object-governance` | `**` | false |
| `autonomous-evolution` | `00-MASTER/UAUE-000001/`, `engine/uaue/`, `engine/uckp/`, `engine/nucleus/`, `engine/foundation/` | true |
| `evolution-replay` | same as above | true |
| `object-birth` | `00-MASTER/UOBC-000001/`, `engine/object_birth/`, `engine/uckp/`, `engine/foundation/` | true |
| `infinite-scope` | `**` | false |
| `primitive-alignment` | `00-MASTER/UCPA-000001/`, `engine/root_ontology/`, `engine/uckp/`, `engine/foundation/` | false |
| `verification-intelligence` | `00-MASTER/UVI-000001/`, `engine/verification_intelligence/`, `engine/verification_impact/`, `verify.sh` | true |
| `coverage-report` | `pyproject.toml` | false |
| `registration-observation` | `00-BOOK/`, `00-SOURCE/` | false |

The three combinations the brief asked for are all present and all populated: reusable-with-read-set (7), non-reusable-with-read-set (7), certification-admitted-non-reusable-with-read-set (`pytest`, `coverage-report`, `registration-observation`).

**Four evidence keys changed** as a direct result — `autonomous-evolution`, `evolution-replay`, `object-birth`, `verification-intelligence` — because their read-sets widened to the dependencies they actually import. This is a correctness change; those stages will now invalidate on changes that previously did not reach them.

## 5. Validation Laws

**11 → 14.** UVI-L-11 was retargeted from `reuse_inputs` to `reads`.

| Law | Title | Proves |
|---|---|---|
| **UVI-L-11** | Every Declared Read-Set Resolves | *(retargeted)* every prefix resolves to ≥1 registered object |
| **UVI-L-12** | Every Stage Declares A Read-Set | **A** — mandatory for all 15, not only the cacheable 8 |
| **UVI-L-13** | Read-Set Is Independent Of Reuse Policy | **B, C, E** — performed |
| **UVI-L-14** | Evidence Identity Depends On The Read-Set | **D** — performed |

UVI-L-13 computes three things rather than asserting them: read-sets exist on **both** sides of the reuse policy; every **non-reusable** stage resolves to a non-empty object population, so impact can reach a stage that may never be cached (**C**); and toggling `reusable` in memory changes neither the read-set nor its resolved population, on every stage (**E**).

UVI-L-14 widens and narrows each keyable stage's read-set in memory and requires the key to move in both directions (**D**). A read-set that did not reach the key would be a declaration with no consequence.

```
VERDICT: COHERENT (14/14 laws hold)
```

## 6. Mutation Proofs

Seven tests, all required mutations covered.

| Test | Mutation | Result |
|---|---|---|
| `test_step3_removing_a_read_set_is_refused` | strip `read_set` **and** `reuse_inputs` | **both** refusals fire — UVI-L-12 refuses the declaration, `input_digest` refuses the key |
| `test_step3_a_read_set_makes_a_previously_invisible_stage_reachable` | query the old coupled field vs the declared read-set | `coupled ⊂ declared` strictly, and the newly-reachable set contains non-reusable stages |
| `test_step3_toggling_reuse_leaves_the_dependency_relation_unchanged` | flip `reusable` on **all 15** | `stages_reading()` byte-identical; `reads` unchanged per stage |
| `test_step3_changing_the_read_set_changes_the_digest` | widen and narrow | key differs in both directions |
| `test_step3_every_stage_declares_a_read_set` | — | 0 stages missing a read-set |
| `test_step3_reuse_inputs_still_resolves_without_a_read_set` | blank `read_set` only | compatibility fallback keys successfully |
| `test_step3_the_whole_boundary_token_resolves_to_the_whole_boundary` | — | `**` = all 6,113 objects |

## 7. Governance Safety

| Must not create | Status |
|---|---|
| new registry | **none** |
| new authority | **none** |
| new lifecycle owner | **none** |
| new verification stage | **none — still 15** |

| Must reuse | How |
|---|---|
| UVI declaration | `read_set` added to the existing stage registry; no new document |
| existing dependency graph | read-sets derived from UGA import closures |
| canonical hashing | `hashlib.sha256` only, unchanged |
| evidence engine | `input_digest` modified in place; no parallel module |

**Identity ledger byte-identical:** `1eea1278…` → `1eea1278…`. `page_cursor` 9826, `volume_seq` 1, 117 categories, **no counter advanced**. Births **38**, supersessions **0**. UGA registries 4880 / 6113 unchanged.

**UVI-L-09 untouched.** `decide()` still refuses on `mode.evidence_reuse` before it reads the script, the store, or a digest. Nothing in this step adds a path by which anything becomes reusable that was not before; the only key movement is *widening*, which can produce misses, never hits.

## 8. Performance Impact

**No improvement is claimed, and none was observed.**

| Measure | Step 2 | Step 3 |
|---|---|---|
| `./verify.sh --fast` | 486s | **485s** — within variance |
| pytest stage | 453s | 451s |
| targeted UVI tests | 208 | **215** |

Step 3 changes **what is declared and what is queryable**, not what executes. `stages_reading()` is not wired into the plan, so no stage was added, removed, or reordered.

What *did* change is measurable, and it is visibility rather than speed:

| Changed path | stages reachable — before | after |
|---|---|---|
| `00-BOOK/SCHEMAS/artifact.schema.json` | 2 | **6** |
| `engine/uckp/facets.py` | 1 | **8** |
| `engine/verification_intelligence/evidence.py` | 2 | **5** |
| `scripts/ucos-env.sh` | **0** | **4** |
| `pyproject.toml` | 1 | **5** |

`scripts/ucos-env.sh` is the clearest case: a change to it previously related to **no stage at all**, and now relates to four.

Stages with a declared read-set: **8 → 15**. Non-reusable stages now impact-visible: **0 → 7**.

Four evidence keys widened, so those stages will miss more often than before. That is the intended direction: they were reusing across changes they actually depend on.

## 9. Readiness for Step 4

**READY.**

| Precondition | State |
|---|---|
| `./verify.sh --fast` | ✅ PASS, 485s |
| UVI laws | ✅ **14/14 HOLD** |
| ruff | ✅ clean |
| targeted UVI tests | ✅ 215 passed |
| all ten read-only gates | ✅ rc=0 |
| identity ledger | ✅ byte-identical |
| stage count | ✅ 15, unchanged |
| certification | ⏸ **not run, per instruction** |

### 9.1 What Step 3 deliberately did not do

`stages_reading()` exists and is measured, but **nothing consumes it in the plan**. Stage-level impact selection — running only the stages a change reaches, in developer modes — is the next step, and it is gated by UVI-L-04 and UVI-L-05: it may never apply to a certification-eligible mode.

### 9.2 Carried residuals

- **Stale-hash window** (from Step 2 validation): evidence keys use UGA's committed hashes, which lag between a content commit and the next registration transaction. Unchanged by this step, and unaffected by it — but note the `**` read-sets are only meaningful to impact analysis, not to caching, because all four stages carrying `**` are declared non-reusable.
- **The two prior reports remain untracked**, pending a REG-AUTO-001 identity transaction. This report joins them.

---

**Scope honoured:** Step 3 only. No new registry, authority, lifecycle owner, or verification stage. UVI declaration, dependency graph, canonical hashing and evidence engine all reused. `reuse_inputs` retained for compatibility and measured.

**STOP — STEP 3 COMPLETE. Step 4 not commenced.**
