# UCOS Ω∞ — PHASE 1 MIGRATION PLAN
## Deliverable 7 — backwards compatibility, and the reversible path onward

**AUTHORITY = NONE (DERIVED TRUTH).** This document proposes. It decides nothing, certifies nothing
and seals nothing. Every step past Phase 1 requires an owner decision.

---

## 1. THE MIGRATION THAT HAS ALREADY HAPPENED: NONE

Phase 1 adds a layer and **replaces nothing**. `engine/universal_discovery` is untouched — same entry
points, same population, same dispositions, same ratchets, same sealed evidence.

Confirmed mechanically: the tracked-file state after this work is byte-identical to before it. The
change set is exactly three **new** paths:

```
engine/omega_infinite/          11 modules
engine/tests/omega_infinite/     9 modules, 159 tests
scripts/omega-infinite.sh        1 orchestration text
```

No existing file was edited. `pyproject.toml`, `verify.sh`, `.github/`, every ratchet and every
coverage setting: unmodified.

---

## 2. THE PROOF OBLIGATION, AND HOW IT IS DISCHARGED

If the abstraction is a genuine generalisation of Ω-1, then configuring it the way Ω-1 is configured
must produce Ω-1's answer **exactly**:

```python
discovery.tracked_python(root)
    ==
repository_space(root).discover(Selector(patterns=("*.py",))).locators()
```

Measured over the real repository:

```
IDENTICAL — 2197 artifacts, same order, same membership.
```

### Three deliberate strictnesses

| Choice | Why the weaker version would be worthless |
|---|---|
| **Tuple** equality, not set equality | A set comparison passes for a population containing the same files in a different sequence. Every digest in UCOS-OMEGA-001 is computed over an ordered structure |
| **Two-directional** difference | "Every file Ω-1 found is in my population" is true of a population containing every file in the universe, and would hide exactly the over-collection a widened default enumeration is most likely to introduce |
| Run over the **real** repository | A synthetic tree proves the code composes, not that Phase 1 changed nothing |

A generalisation that changed the answer would not be a generalisation — it would be a **second
population**, and this repository has already paid for four of those, with 619 artifacts sitting in
exactly one of them.

### Where the hard-coded assumption went

It did not disappear. It moved to a place where it can be named, inspected and overridden:

```python
# engine/omega_infinite/compat.py
PYTHON_ONLY = Selector(patterns=("*.py",))
```

| Before | After |
|---|---|
| the filter is a string literal inside the only enumeration mechanism there is | the filter is an argument, the mechanism is one provider among others, and both appear in the evidence document |

---

## 3. WHAT THE Ω-1 GATE SAYS ABOUT THE CHANGE SET

Measured with a **throwaway git index** (`GIT_INDEX_FILE` pointed at a copy), so the real index and
the concurrently running validation were never touched. The probe index has been deleted.

```
PASS — all five Ω criteria hold, and none of them consulted a list.

tracked python .............. 2217   (was 2197, +20)
measurable packages ......... 81     (was 80)
relocation invariance ....... holds for all 2217
authority coverage .......... 100.0%

IMPROVED   unmeasured_surface_density   0.096989 → 0.096236
IMPROVED   import_entropy               8.007283 → 7.997294
IMPROVED   statement_entropy            6.397527 → 6.382844
HELD       unreachable_artifacts        53.0
HELD       authority_of_last_resort      0.0
HELD       declared_exemptions          10.0
HELD       unresolved_dynamic_sites     22.0
JUSTIFIED  unexplained_exemptions        2.0   (declared floor)
JUSTIFIED  unnameable_exemptions        49.0   (declared floor)
```

**Three improved, six held, none regressed. Nothing resealed** — the gate was run read-only, without
`--seal`.

### How the ratchets were satisfied rather than dodged

| Ratchet | Constraint it imposed on this code | How it was met |
|---|---|---|
| `unreachable_artifacts` floor 53 | Every new module must be reachable, or the count rises to 54 and is refused | `scripts/omega-infinite.sh` names `python3 -m engine.omega_infinite`. `scripts/` is a declared orchestration plane kind, so the package sits on the `python` plane. **Zero unreachable artifacts added** |
| `authority_of_last_resort` 0 | No module may fall through to the unconditional Ω-A-07 rule | Reached by Ω-A-04 (execution graph) via the same orchestration text |
| `import_entropy` 8.007283 | New files must average ≤ 8 import statements | Averaged well below; the metric improved |
| `statement_entropy` 6.397527 | New code must average ≤ 6.39 statements per callable | Many small methods and 159 test functions; the metric improved |
| `unexplained_exemptions` floor 2 | New code must be `MEASURED`, not fall into Ω-C-07 | Placed under `engine/`, so `engine.omega_infinite` is derived into the denominator automatically |
| `unmeasured_surface_density` | Ungoverned statements over surface statements | New code is measured, so the denominator grew and the ratio fell |

### `scripts/omega-infinite.sh` — why a wrapper exists at all

Not convenience. `engine/omega_infinite/__main__.py` is a real execution surface, and Ω-3 measures
reachability from orchestration texts rather than from intention. A CLI that no orchestration text
invokes reads as dead code — **correctly**, because an entry point nothing invokes is
indistinguishable from dead code.

The wrapper registers the surface **without** wiring it into any gate: it is deliberately not a
`verify.sh` stage and not a CI job, because the directive forbids modifying `verify.sh` execution
order and CI workflow behaviour.

### The Ω-1 property, exercised on its own successor

`engine.omega_infinite` entered the coverage denominator with **zero edits to `pyproject.toml`**.
That is Ω-1's own success criterion — a new tree governed on the commit that creates it — discharged
by the commit that introduces Phase 1.

---

## 4. THE ADAPTER

`compat.as_universal(legacy)` lifts an Ω-1 artifact into the universal model. Nothing is discarded
and nothing Python-specific enters the universal shape: the four Python fields become `metadata`, the
type becomes a value, and the Ω-1 verdicts ride along as metadata.

The legacy import inside `compat.equivalence` is **local, not module-level**, and deliberately so:
this package must not make `engine.universal_discovery` an import-time dependency of the abstraction
layer. An abstraction that could not load without the thing it abstracts would have inverted the
dependency it exists to remove.

---

## 5. THE PATH ONWARD — PROPOSED, NOT DECIDED

Each step is independently reversible and independently valuable. **No step below has been taken.**

### Step A — consume the layer for reporting only (no verdict depends on it)

Emit a Phase 1 evidence document alongside the existing Ω surface. Nothing gates on it.

- **Reversible:** delete one artifact.
- **Risk:** none. No verdict changes.
- **Owner decision:** whether Phase 1 evidence belongs in a programme home. This would be the first
  point at which a governance artifact is created, so it is out of Phase 1 scope.

### Step B — route Ω-1's population through the provider

Replace the body of `discovery.tracked_python` with a call to a resolved `TRACKED_CONTENT` provider,
keeping the signature and the return type.

- **Guarded by:** `compat.equivalence`, already asserting tuple equality over the real repository.
- **Reversible:** revert one function body.
- **Risk:** low but **not** zero — it touches the function every Ω verdict depends on.
- **Owner decision required:** yes. This is the first change to a governing code path.

### Step C — classify the non-Python population

Extend the selector beyond `*.py` and classify the result. UCOS currently governs 2217 Python
artifacts; the repository holds thousands of documents, workflows and datasets that **no discovery
measurement sees at all**.

- **Measurement first:** report `unknown_population` before proposing any disposition for the new
  types. Classifying is not governing.
- **Risk:** the new population must **not** enter any existing denominator, or coverage percentages
  become numbers about a different question.
- **Owner decision required:** yes — this changes what UCOS considers to exist.

### Step D — replace `root: str` with `KnowledgeSpace` at entry points

Add `space: KnowledgeSpace | None = None` beside the existing `root: str`, defaulting to
`resolve_space(root)`. Both work; the string path is deprecated, not removed.

- **Reversible:** the parameter is additive.
- **Owner decision required:** yes, at the point the string form is finally removed.

### Step E — a provider beyond local storage

Only once A–D hold. This is where `REMOTE_STORAGE`, `BUCKET` and `FEDERATION` stop being registrations
and become real, and where `guarantees()` versus `capabilities()` starts carrying weight (see
`PHASE1_KNOWLEDGE_SPACE_MODEL.md` §5).

---

## 6. RISKS CARRIED FORWARD

| Risk | Status | Mitigation |
|---|---|---|
| The layer becomes a second population that disagrees with Ω-1 | **Closed for Phase 1** | `compat.equivalence` asserts tuple equality over the real repository, two-directionally |
| A future provider silently lacks the eligibility boundary | **Closed** | `RepositoryKnowledgeSpace.__init__` requires `TRACKED_CONTENT`; refused at construction |
| Vocabulary drift — two names for one property | **Closed** | Registries refuse conflicting re-declaration; `resolve()` raises on unknown names |
| Classification becomes a giant rule table | **Structurally prevented** | The tables are injected `TypeVocabulary` data; no classifier names a format or a language |
| A new artifact type quietly enters a coverage denominator | **Open — Step C** | Must be measured and reported before any disposition is proposed |
| `UNKNOWN` becomes a comfortable resting place | **Open** | It is a countable population today (`unknown_population`). It has **no ratchet yet**, and giving it one is a Phase 2 decision |
| The layer is unused and therefore rots | **Open** | It is reachable, tested at 100% and exercised by a CLI, but no gate depends on it. Step A is the cheapest way to close this |

---

## 7. VERIFICATION SUMMARY

| Check | Result |
|---|---|
| New tests | **159 passed** |
| Coverage of `engine.omega_infinite` | **100.00%** (909 stmts, 150 branches, 0 miss) |
| `ruff check` (E,F,I,B,UP,S @100) | **All checks passed** |
| `ruff format --check` | **20 files already formatted** |
| Phase 1 criteria Ω∞-1 … Ω∞-5 | **all PASS** |
| Ω-1 equivalence over real repository | **IDENTICAL, 2197 artifacts** |
| Ω-1 gate with change set tracked | **PASS**; 3 ratchets improved, 6 held, 0 regressed |
| Existing controls re-run with change set tracked | 14 real-repo `test_coverage_scope` tests + `test_the_real_repository_has_no_authority_free_artifact` **passed**; `test_surface_and_gate.py -k "real or gate or cli or scope or determin or relocat"` **30 passed, 1 skipped** |
| Existing files modified | **zero** |
| Governance artifacts sealed or resealed | **none** |
| Certification issued | **none** |

### Not verified, and stated as such

- The **full** existing suite was not re-run with the change set tracked. Fixture repositories in the
  existing suite call `git init` / `git add`, which under a `GIT_INDEX_FILE` override would write into
  the probe index. The real-repository controls — the ones whose verdicts the change set could
  actually affect — were run and passed; the fixture-repo tests are independent of it by construction.
- Nothing is staged. A validation run was active throughout, and in-flight tests call
  `gate.evaluate(".")` and `discovery.tracked_python()` against the real git index, so staging
  mid-run would change what a running test sees.

---

## 8. HANDOFF — STAGING, WHEN THE VALIDATION RUN COMPLETES

Confirm no pytest is running, then:

```bash
git add engine/omega_infinite engine/tests/omega_infinite scripts/omega-infinite.sh \
        PHASE1_ARCHITECTURE.md PHASE1_MIGRATION_PLAN.md PHASE1_PROVIDER_MODEL.md \
        PHASE1_ARTIFACT_MODEL.md PHASE1_KNOWLEDGE_SPACE_MODEL.md

python3 -m engine.universal_discovery      # expect PASS, 3 ratchets IMPROVED, 0 REGRESSED
python3 -m engine.omega_infinite           # expect PASS on all five Ω∞ criteria
```

**Do not run `--seal`.** Advancing the Ω ratchet on the improved values is a governance act and an
owner decision, and the Phase 1 directive forbids resealing.
