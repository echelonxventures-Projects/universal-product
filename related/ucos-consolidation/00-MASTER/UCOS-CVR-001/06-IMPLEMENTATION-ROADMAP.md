# UCOS-CVR-001 · 06 — IMPLEMENTATION ROADMAP

> **Satisfies:** Task 8. **Status:** PLAN ONLY — nothing in this roadmap has been executed.
> **Anchor:** commit `898ef8d`.
> **Constraint honoured:** no wave modifies `verify.sh`, `pyproject.toml`, CI, tests or thresholds
> **before** the wave in which that change is itself the ratified deliverable.

---

## PART A — THE MANDATORY LIFECYCLE

Every wave executes the same ten steps, in this order, with no step skipped:

```
 1 Repository Discovery   → derive U0, publish universe digest
 2 Classification         → derive U1, assert count(Unknown) == 0
 3 Registration           → bind results to registered owners; assert no drift
 4 Verification           → execute every mandatory obligation for the wave's scope
 5 Coverage               → measure U3; aggregate floor + per-unit floor + declared==measured
 6 Certification          → emit hash-chained certificate over 4 ∪ 5
 7 Digital Twin           → update the twin; assert twin == derivation
 8 Repository Clean       → `git status --porcelain` empty except declared outputs
 9 Commit                 → one wave, one commit, message names the wave and its exit criteria
10 Release                → tag only when the aggregate gate is green at the tier `full`
```

A wave that cannot complete step 8 is rolled back, not patched forward.

---

## PART B — WAVES

### W0 · RATIFICATION (no code)

| | |
|---|---|
| Deliverable | `05-VERIFICATION-CONSTITUTION.md` ratified; the five approval questions in `08` §3 answered |
| Touches | `00-MASTER/UCOS-CVR-001/` only |
| Exit | Constitution status `RATIFIED`; migration option chosen under Article XII.3 |
| Rollback | discard the package |
| Blocked by | nothing |

**Nothing else may start.** Every later wave changes ratified files (`pyproject.toml`, `verify.sh`,
CI), which the current mission explicitly forbids without approval.

---

### W1 · TRUTH & CLASSIFICATION (derive, do not enforce)

| | |
|---|---|
| Deliverable | the verification declaration (`02` §C.4 shape) + a discovery/classification engine in its own home, plus the seven self-guards (`02` §C.5) |
| Reuses | `ukb.py::eligibility_universe()` / `classify()` (pattern + boundary), `platform/repository_intelligence`, the `UCCEP/URRC` declaration-engine pattern |
| Produces | `U0`, `U1`, universe digest, class census, `Unknown` register |
| Enforces | **nothing yet** — reporting only |
| Exit | `count(Unknown) == 0` over all 4 862 artifacts; local digest == CI digest; `--check-no-enumeration` passes |
| Fixes | D-1 (mechanism), part of V-3 |
| Rollback | delete the engine home; no existing file changed |

W1 is deliberately non-enforcing. It must be possible to *see* the whole classified repository
before any gate acts on it.

---

### W2 · TEST UNIVERSE (the largest single gain)

| | |
|---|---|
| Deliverable | `testpaths` and lint scope become **derived** (`class == Tests` / code classes); the 4 117 orphan tests enter the canonical suite |
| Prerequisite | W1 exit; D-11 resolved — `intelligence/tests` writes into `intelligence/` and must be sandboxed (tmp_path/fixture isolation) before admission |
| Measured effect | canonical suite 4 751 → **8 868** collected; 8 746 currently pass (`intelligence/tests` excluded from that figure); 585 previously unlinted `.py` files enter the lint gate |
| Risk | lint failures in the 585 newly-scoped files are **unknown and unmeasured** — W2 must begin by measuring them, and `ruff format --check` is likely to require a formatting pass |
| Exit | one command runs every test in the repository; lint scope == code classes; no test is orphaned |
| Fixes | D-4, D-5, O-1, O-2, V-3 |
| Rollback | revert the two derived-scope changes; the declaration stays |

---

### W3 · COVERAGE UNIVERSE (the decision wave)

| | |
|---|---|
| Deliverable | `--cov` enumeration replaced by `σ`-derived scope; `declared == measured` guard; per-unit floor mechanism (value set by W0's ratified choice) |
| Measured effect | coverage universe 37 451 → **81 680** statements; reported coverage **94.11 % → 85.85 %** (branch-inclusive) against a floor of 90 |
| Decision required | Article XII.3, chosen in W0: (a) raise coverage first, (b) admit with a counted, shrinking, owner-attributed exemption register, or (c) reclassify honestly |
| Exit | zero declared-but-unmeasured units; every entry point is a unit; threshold declared exactly once |
| Fixes | D-2, D-3, D-9, CR-1..CR-7 |
| Rollback | restore the enumerated `--cov` block from git |

**This is the only wave that can fail for reasons outside engineering control**, because it exposes
a ratified threshold to a wider universe. Sequencing it after W2 is deliberate: W2 admits the
29 970 statements at 98.45 %, which absorbs part of the drop before the floor is applied.

---

### W4 · OBLIGATION EXECUTION

| | |
|---|---|
| Deliverable | the 15 × 22 policy becomes executable: each mandatory `(class, type)` maps to a located authority and runs under a tier |
| Reuses | `platform/universal_assurance` (policy/obligation/criterion/gate vocabulary already exists and is data-driven — O-3 resolves by *binding* it, not by writing a new engine), `platform/universal_validation`, `platform/validation_intelligence`, `engine/graph/architecture`, `engine/context`, `engine/knowledge` |
| Exit | every MANDATORY cell executes in some blocking tier; every `X*` cell appears in the Absence Register with a named owner-to-be; no obligation is silently skipped (Article X.6) |
| Fixes | O-3, O-4, D-12 |

---

### W5 · TEMPORAL PLANE SPLIT (verification's own scope only)

| | |
|---|---|
| Deliverable | dual-plane emission for the 4 entangled artifact families (`engine/graph/evidence.py`, `engine/graph/architecture/evidence.py`, `engine/registry/universal/audit.py`, the 9 `00-MASTER/*_engine.py` `NOW` constants); temporal-record **schema and obligation** declared; sidecar emitted in the degenerate interim form, labelled interim |
| Explicitly out of scope | implementing calendars, time standards, reference systems, bodies, locations, coordinates or conversion — owners are `UNI-006` / `DOM-0021`, six of nine requirements are `[N]` net-new (`04` Part F) |
| Exit | zero temporal values in any deterministic plane; existing `--check-determinism` guards still pass **unmodified**; every verification artifact resolves to a temporal record; `_neutralize_stamps` is no longer load-bearing |
| Fixes | D-8 partially (entanglement), T-1..T-5 |
| Does **not** fix | D-7 — that requires a separate commission to `UNI-006`/`DOM-0021` |

---

### W6 · CERTIFICATION & TWIN INTEGRITY

| | |
|---|---|
| Deliverable | hand-authored facts removed from `repo-operations.json` (cutting the prohibited L5 → L3 edge); `architecture-freeze` gains a derived path set instead of `paths: []`; certificates carry universe digest + policy digest; twin asserts `twin == derivation` |
| Exit | no acceptance input is hand-authored; no vacuous stage; stale certificates fail |
| Fixes | D-6, B.1 prohibited edge |

---

### W7 · BINDING & INHERITANCE

| | |
|---|---|
| Deliverable | the architecture is bound into `uccep-bindings.json` as a blocking check, so it is executed by the aggregate gate and by every future programme automatically; `.kiro` hook parity |
| Exit | a *new* package added in a scratch commit acquires lint + tests + coverage + registration obligations **with zero configuration change** — the executable proof of VP-12 |
| Fixes | the mission's stated purpose: *"every future implementation shall automatically inherit the same verification architecture"* |

---

## PART C — DEPENDENCY ORDER

```
W0 ratification
   └─► W1 truth + classification (non-enforcing)
          ├─► W2 test universe ──┐
          │                      ├─► W3 coverage universe ──► W6 certification + twin ──► W7 binding
          └─► W4 obligations ────┘                                    ▲
                 └─► W5 temporal plane split ───────────────────────┘
```

W2 and W4 are parallelizable after W1. W3 must follow W2. W5 is independent of W2/W3 but must
precede W6 (certificates must reference temporal records). W7 is last by definition.

---

## PART D — WHAT IS DELIBERATELY NOT IN THIS ROADMAP

| Excluded | Reason |
|---|---|
| Writing tests to raise coverage | out of mission scope (`Do NOT write tests`); it is also the wrong instrument — W3's decision comes first |
| Changing the `90` threshold | forbidden by the mission; forbidden downward by VP-11 |
| Implementing the Universal Temporal Framework | duplicate authority; owners are `UNI-006` / `DOM-0021`; six `[N]` items |
| Admitting performance / mutation / dynamic / supply-chain tooling | Article XI.3 requires tool + authority + threshold + wave; none exist |
| Refactoring `engine/graph` (54.5 %) or `engine/knowledge` (80.8 %) | consequences of W3's decision, not prerequisites of it |
| Merging `platform/coverage`'s architectural coverage into execution coverage | they are distinct dimensions (Article IV.1); binding ≠ merging |

*End of 06-IMPLEMENTATION-ROADMAP.md*
