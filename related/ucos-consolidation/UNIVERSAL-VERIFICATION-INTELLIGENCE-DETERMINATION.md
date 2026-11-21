# Universal Verification Intelligence — Determination

**Artifact:** UVI-000001
**Authority:** NONE — DERIVED TRUTH
**Declaration:** `00-MASTER/UVI-000001/uvi-declaration.json`
**Realization:** `engine/verification_intelligence/`
**Gate:** `./verify.sh` Stage 6g · `make uvi-gate` · exit 0 COHERENT / 1 INCOHERENT / 2 FAULT

---

## 1. The condition

`./verify.sh` executed one plan for every caller. Measured on the certification baseline:

| Measure | Value |
|---|---|
| tests | 11 628 passed, 3 skipped |
| coverage | 97.61% against a 90% floor |
| governance gates | all green |
| pytest + coverage | 2 814 s |
| every other stage combined | ~40 s |

A developer changing one module paid all of it. The cost was not distributed across the
verification — **98.6% of it was one stage**, and that stage ran the whole suite whatever
the change was.

Two further measurements taken while building this programme sharpened the picture, and
both contradicted a reasonable assumption:

* **Coverage instrumentation, not the tests, is most of the cost.** The same suite runs
  in **1 588 s without coverage** and 2 814 s with it. The tests are 56% of the bill.
* **One file is 46% of the suite.** `engine/tests/uckp/test_universe_and_validation.py`
  measures **738 s** of a 1 588 s suite. No number of parallel workers can finish sooner
  than that one file, so any plan that treats a file as indivisible has a 738 s floor
  before it has scheduled anything else.

## 2. What was refused

The cheap answers were all available and all rejected:

| Refused | Because |
|---|---|
| Lower the coverage floor | The floor is the obligation. Moving it is not optimisation, it is a smaller claim. |
| Drop gates from the developer path | A commit is exactly where an ungoverned change enters. |
| Skip "slow" tests | That is a hand-maintained selection, and the thing it selects away is by construction the thing nobody is watching. |
| Cache the pytest result | The one stage whose result IS the run. |
| Add `pytest-xdist` | An unpinned distributed-execution dependency, and it moves shard assignment into a scheduler this repository does not own and cannot reproduce. |

## 3. The determination

**Verification is a function of the change, not of the caller.** The obligations are
constant; the execution required to discharge them is derived.

Nothing below removes a gate, lowers a threshold, or narrows a denominator. The whole of
the change is in **selection**, **scheduling** and **reuse**.

### 3.1 The default changed, explicitly

`./verify.sh` was the certification contract. It is now `--change`. Certification did not
become weaker — it became **named**: `.github/workflows/ec1-ci.yml` invokes
`./verify.sh --full`, and `--full` runs every stage the old default ran, under the same
floor, over the same suite, plus the registration observation.

A 47-minute default is a default people route around, and a gate that is routed around is
not a gate.

### 3.2 Selection derives from five substrates

No test path is authored anywhere — not in the declaration, not in the engine. UVI-L-06
measures that over the engine's *evaluated string constants*, so a docstring may discuss a
test file and a code path may not name one.

| Layer | Substrate | Contribution |
|---|---|---|
| IDENTITY | executable object registry | every changed path resolves to a record, or escalates |
| DEPENDENCY | resolved import edges, inverted | transitive reverse closure — everything that can reach the change |
| OWNERSHIP | the recorded owner of every object | the join key between the dependency graph and the capability catalogue |
| CAPABILITY | `UCOS-RIE-CAPABILITY-CATALOG` | the catalogued test mirror (`engine/uckp` → `engine/tests/uckp`); an uncatalogued owner at the change site escalates |
| RELATIONSHIP | relationship graph `produces` | a generated artifact reaches the engine that renders it — an edge no import graph can see |

Impact discovery itself is **not re-implemented**: `engine.verification_impact` remains the
owner of the fail-closed diff-base chain, the unbounded-path policy and the reverse import
closure.

**One inherited decision was overridden, and it is the only behavioural change to that
engine.** `analyse` widens to INTEGRATION when a change reaches more than three owners,
because with only an import graph to reason from, breadth is the best available proxy for
state that imports do not show. Measured on this repository, that proxy escalates almost
every real change — a one-line edit to a widely imported module reaches 50 owners. This
engine has the thing the proxy was proxying for, so it supersedes it and **carries the
superseded reason in the plan** rather than discarding it. What is never overridden is
`unbounded`: a path no graph here can bound. That distinction was added to
`ImpactReport.is_computable`, additively; no existing behaviour or test changed.

Measured selection, on real single-file changes:

| Change | Tests selected (of 568) |
|---|---|
| `engine/uaue/gate.py` | 4 |
| `platform/universal_control_plane/cli.py` | 2 |
| `engine/nucleus/law.py` | 16 |
| `engine/uckp/facets.py` | 37 |
| `platform/identity/policy.py` | 97 |
| `engine/foundation/guards/frozen_paths.py` | 240 |
| any declaration, registry, schema, document, unregistered file, or the selector itself | **568 — with coverage** |

### 3.3 Execution topology is neutral, and that is computed

Shards are assigned by longest-processing-time over a measured cost table, ties broken by
path — a pure function of (selection, costs, worker count), so two machines produce
identical shards. Each shard is a separate process with its own `COVERAGE_FILE`; the data
is combined and **the floor is evaluated exactly once, over the union, by the coverage
tool itself**. Every shard keeps `addopts` intact, so the `--cov` denominator cannot
depend on how the run was scheduled.

An object above the declared 60 s threshold is placed as its individual **nodes**, which
is what removes the 738 s floor. Node ids are only usable while they are current, so each
split entry records the object's `content_hash` as UCOS-UGA-001 published it; a changed
file falls back to whole-file placement — slower, always correct.

UVI-L-08 partitions the suite at six worker counts and refuses any partition that loses,
duplicates or invents a test object. `run_tests` re-asserts it before spawning anything.

### 3.4 Evidence reuse, and its honest size

A reusable stage is keyed by a digest over the `content_hash` values UCOS-UGA-001 already
publishes for its declared inputs. **Certification never reaches a reuse decision at all**
(UVI-L-09) — a certification that reuses a result certifies a cache.

It should be said plainly that reuse is the *smallest* of the three mechanisms here. Every
governance gate in this repository measures in under seven seconds; reuse saves seconds,
and selection and sharding save tens of minutes. Two stages were also measured to be
**unable** to take an honest key at all — `00-BOOK/` contains a self-referential object
whose content hash is declared withheld, so no digest over that boundary can be taken, and
those stages are declared non-reusable rather than given a key that covers less than they
read.

### 3.5 The ratchet

`no_assurance_reduction.baseline_stages` records the twelve stage labels `./verify.sh`
declared before this programme existed. UVI-L-04 measures that every one is still a
declared stage **and** still admitted by every certification-eligible mode. Removing a gate,
or quietly dropping one from `--full`, fails here.

## 4. Defects found and fixed while measuring

Seven, none hypothetical, and the first is the one worth reading.

1. **Node-level sharding silently dropped 54 tests.** An object above the split threshold
   is placed as its measured nodes — but `--durations` hides anything under 0.005s, so a
   fast test inside a slow file appeared in no shard at all. The run reported **11 706 of
   11 760 tests** and called it a pass. The file-level neutrality check passed throughout,
   because at file level the union *was* exact.

   The fix is structural rather than a better cost model: the lowest-indexed shard holding
   any part of a split file receives **the file**, and is told to `--deselect` exactly the
   nodes its neighbours hold. It is the remainder, so it runs everything nobody else took
   — including nodes nothing ever measured. Coverage of the file is then true by
   construction rather than by the model being complete.

   The lesson is in the test that now guards it: `test_the_shards_collect_exactly_the_tests
   _the_whole_suite_collects` asks **pytest** to collect the whole suite and every shard,
   and requires set equality. No amount of reasoning about the cost model would have found
   this; only asking the collector did. Measured after the fix: union 11 760, serial
   11 760, duplicates 0.

2. **The test stage could not safely overlap the whole-tree gates.** It was classified
   `MAIN` on the grounds that the gates are READ_ONLY. Read-only is not sufficient for
   concurrency: the gates measure the entire version-controlled boundary, while the suite
   regenerates derived views and takes the git index lock. Run together, UCOS-UGA-001 read
   a torn tree and took **491 s instead of 5 s** on lock contention, and failed. The test
   stage now has a phase of its own; the gates cost eight seconds between them, so the
   serialisation costs nothing measurable.

3. **An isolated object must run first, not last.** `test_verification_purity.py` asserts a
   property of the whole working tree. Scheduled last, it reached a different verdict
   depending on what eleven thousand tests had left behind. It now runs alone and **before**
   the concurrent body, so it observes the tree as verification found it — the fixed point
   the preflight phase just established.

4. **Shard working directories were created inside the repository.** An interrupted run
   left `uvi-logs-*` in the tree, which UCOS-UGA-001 then measured as unidentified objects —
   a verification run able to dirty the thing it verifies, even by dying. They are now
   created outside it.

5. **The evidence store was not excluded from the tracked tree.** The declaration said it
   was untracked; nothing made that true, and UCOS-UGA-001 measured every cache entry as an
   unidentified object. The `.gitignore` rule exists, and UVI-L-06 now measures the claim
   rather than believing it.

6. **`coverage combine` inherited an ambient `COVERAGE_FILE`.** Run under a parent that had
   already set it, the combine wrote its result into the parent's data file and corrupted
   it. Every coverage subprocess is now given the canonical path explicitly.

7. **`coverage xml` applies the configured `fail_under`.** A run below the floor exited
   non-zero at the xml step and was reported as "coverage xml failed" — a true verdict
   behind a false explanation. The floor is now evaluated by exactly one command.

And one pre-existing hazard, found but deliberately **not** changed: the autouse fixture in
`platform/tests/test_verification_purity.py` runs `git checkout -- 00-BOOK/DATA/
00-BOOK/REGISTRIES/ 00-BOOK/CONTROL-TOWER/` after every test in that module, which discards
any *unstaged* work under those paths. It is correct for what that module is doing and it is
outside this programme's scope, but anyone minting identities into `00-BOOK/DATA/id-ledger.json`
should stage them before running the suite, or the mint will be silently reverted.

## 5. The laws

Ten, each computed and none asserted. UVI-L-07 and UVI-L-08 are *performed*: the gate puts
three synthetic unbounded changes through the real selector and partitions the real suite
at six worker counts. A law about behaviour that is checked by reading a docstring is not
checked.

| Law | Statement |
|---|---|
| UVI-L-01 | The script and the constitution admit exactly the same modes, in both directions |
| UVI-L-02 | Exactly one declared default, and the bare invocation resolves to it |
| UVI-L-03 | The stage registry and `verify.sh` declare the same stages, in the same order |
| UVI-L-04 | Every baseline gate is still declared and still admitted by every certifying mode |
| UVI-L-05 | No mode claims more than it measures |
| UVI-L-06 | Selection is derived, never authored |
| UVI-L-07 | Fail wide — every unbounded change widens, and names why |
| UVI-L-08 | Topology neutrality — sharding changes no measured obligation |
| UVI-L-09 | Evidence reuse integrity — and certification never reuses |
| UVI-L-10 | Deterministic planning — identical bytes, no clock, no machine path |

## 6. What this programme is not

It legislates nothing. It is not superior to CMG-000001 (law owner), UCIC-001 (lifecycle
owner) or CEP-009 (evolution authority). It declares no lifecycle stage, opens no registry
that allocates, holds no counter, issues no identifier, and declares no rival object model.
The Test Object Registry and the Verification Evidence Registry are both derived
projections: deleting either changes no verdict, only the cost of reaching one.

It is also **subject to its own laws**. A change to `engine/verification_intelligence/`
escalates to the whole suite, because a change to the thing that decides what to verify
cannot be verified by asking it what to verify.
