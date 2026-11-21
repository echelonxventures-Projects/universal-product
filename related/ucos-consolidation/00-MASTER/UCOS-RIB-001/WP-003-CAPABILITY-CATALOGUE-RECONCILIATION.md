# WP-003 — Repository Capability Catalogue Reconciliation

| Field | Value |
|---|---|
| MISSION / PROMPT | `UCOS-IMP-MSN-000003` · `UCOS-PRM-IMP-000003` |
| PROGRAM / EPIC / WP | `Ω∞-001` · `EPIC-001` · `WP-003` |
| PREDECESSOR | `UCOS-PRM-IMP-000002` (WP-002, cycle elimination) — COMPLETED |
| AUTHORITY | **NONE — DERIVED TRUTH** |
| CATALOGUE OWNER RECONCILED | `intelligence/UCOS-RIE-CAPABILITY-CATALOG.json` (owner: `intelligence/rie`, UCOS-RIE-001) |
| ENTRY ANCHOR | `4712da5` · `integration/recovery-001` · working tree CLEAN |
| GENERATOR ANCHOR | `e8d70f3` — the commit whose generator produced the reconciled outputs |
| COMMIT ANCHOR | `b47f5b9` — the commit carrying the reconciled outputs |
| **GATE-07** | **FAIL (`uncatalogued_units=23`) → PASS (`uncatalogued_units=0`)** |
| VERDICT | **RECONCILED** — every mission success criterion met |

This document is the single record of the nine mandatory mission outputs. It legislates
nothing and owns no capability. Every number in it is read from a generated artefact or
from `git`, and each section names where.

---

## 001 · Repository Intelligence Reconciliation Report

### The finding was not an entry count

Mission-000001 reported 23 implementation units absent from the canonical capability
catalogue and Mission-000002 confirmed it independently. Both were correct, and both
described a symptom. The catalogue was not 23 entries behind the repository; the generator
that produces it was **structurally unable to see most of the repository**, so no amount of
regeneration could ever have closed GATE-07.

The catalogue is a generated output of `intelligence/rie`. Manual catalogue editing is
prohibited by this mission and, independently, would have been erased by the next
regeneration. The reconciliation therefore had to happen in the generator. Three defects,
each independently sufficient to keep the gate closed:

| # | Defect | Where | Units it hid |
|---|---|---|---|
| D1 | **Hardcoded code roots.** `code_roots` was the literal `("engine", "platform")`. Five of the repository's seven tracked Python code roots were invisible, so their packages could never be catalogued. | `intelligence/rie/config.py` | 5 |
| D2 | **Test packages filtered on sight.** `_subpackages` dropped any directory named `tests`, while the repository inventory counts each one as a tracked implementation unit. This made the coverage gap **permanent and uncloseable** — regeneration could not fix what discovery refused to look at. | `intelligence/rie/discovery.py` | 7 |
| D3 | **A code root was never itself a record.** Only sub-packages were catalogued, although the inventory discovers roots as units in their own right. | `intelligence/rie/discovery.py` | 6 |
| D4 | **Staleness.** The catalogue was last generated at `527485a` on branch `programme/evo-usis-005`; five packages created since then were simply not yet seen. This is the only one of the four that regeneration alone would have fixed. | — | 5 |

5 + 7 + 6 + 5 = **23** — the exact figure both prior missions reported, now decomposed
rather than restated.

A fourth defect was found while fixing the third, and is the most consequential for the
future: `CATEGORY_POLICY.get(root, CATEGORY_POLICY["engine"])` made an **undeclared category
inherit `engine`'s policy**. Any newly discovered code root would have silently claimed
`EC-1 CERTIFIED` authority and `replacement_prohibited = True` — a fabricated certification
claim, produced automatically, for code that had never been certified. The fallback is now
fail-closed (`UNCLASSIFIED` / `INDETERMINATE`).

### What was changed, and what was not

| File | Change |
|---|---|
| `intelligence/rie/config.py` | `discover_code_roots()` derives the roots from the tracked file set (`git ls-files`), with a deterministic filesystem fallback for a non-git checkout. `code_roots` remains overridable. |
| `intelligence/rie/discovery.py` | Units derived from the same two selectors the Repository Integration Blueprint discovers over — `*/__init__.py` and `*/*/__init__.py` — so catalogue and inventory now agree **by construction** rather than by coincidence. Roots included; `tests` no longer excluded. |
| `intelligence/rie/knowledge.py` | Category policy for the five previously invisible roots, each quoted from that root's own package docstring. `status` moved into the policy, removing the `if root == "engine"` special case. Fail-closed `UNCLASSIFIED_POLICY` fallback. |
| `intelligence/rie/evidence.py` | Generation provenance (§006). Coverage fingerprinted by consumed measurement, not file bytes (§006). |
| `intelligence/rie/engine.py` | The provenance block added to every artefact envelope. |
| `intelligence/rie/drift.py` | Drift keyed on canonical name, not on the ordinal `unique_id`. |

No repository code outside `intelligence/rie/` was modified. No capability was created. No
catalogue entry was written by hand. No orphan was remediated, no runtime refactored, no
registry or constitution touched.

### Category policy is derived from each root's own words

The five new policy entries are not invented. Each root states its own constitutional
posture in its package docstring, and the policy quotes it:

| Root | Its own docstring says | Recorded authority |
|---|---|---|
| `data/` | "Data Layer (EC-3 Band 10) realization surface" | `EC-3 BAND 10 (DATA) REALIZATION` |
| `service/` | "Service Layer (EC-3 Band 11) realization surface" | `EC-3 BAND 11 (SERVICE) REALIZATION` |
| `application/` | "Application Layer (EC-3 Band 12) realization surface" | `EC-3 BAND 12 (APPLICATION) REALIZATION` |
| `infrastructure/` | "Infrastructure Layer (EC-3 Band 13) realization surface" | `EC-3 BAND 13 (INFRASTRUCTURE) REALIZATION` |
| `intelligence/` | "additive intelligence subsystem (non-corpus, AUTHORITY=NONE)" | `ADDITIVE (AUTHORITY=NONE)` |

Note what these values deliberately do **not** say. The `BANDS-10-13-REALIZATION-LANE-CHARTER`
maps the bands to the corpus directories `10-DATA/` … `13-INFRASTRUCTURE/`, not to these code
roots, and it authorizes no implementation. The records therefore state the band each root
declares itself a realization of, and claim no admission, certification or freeze status that
no machine-readable evidence supports. `replacement_prohibited` is left `False` for all five
rather than asserted from a documentary reading.

---

## 002 · Updated Capability Catalogue

`intelligence/UCOS-RIE-CAPABILITY-CATALOG.json` — **42 → 66 records.**

| Category | Records | Authority recorded |
|---|---|---|
| `engine` | 17 | `EC-1 CERTIFIED` |
| `platform` | 28 | `EC-2 CLOSED/FROZEN` |
| `intelligence` | 7 | `ADDITIVE (AUTHORITY=NONE)` |
| `data` | 2 | `EC-3 BAND 10 (DATA) REALIZATION` |
| `service` | 2 | `EC-3 BAND 11 (SERVICE) REALIZATION` |
| `application` | 2 | `EC-3 BAND 12 (APPLICATION) REALIZATION` |
| `infrastructure` | 2 | `EC-3 BAND 13 (INFRASTRUCTURE) REALIZATION` |
| `automation` | 3 | `ACTIVE` |
| `operational_memory` | 1 | `ACTIVE (AUTHORITY=NONE)` |
| `orchestration_spec` | 2 | `SPEC (AUTHORITY=NONE)` |
| **Total** | **66** | |

60 of the 66 are the complete implementation universe (see §005); the remaining 6 are the
three automation tools, operational memory, and the two orchestration specifications, all
unchanged from the prior catalogue.

---

## 003 · Updated Repository Intelligence Outputs

Ten artefacts regenerated by `python -m intelligence.rie build`, anchored at `e8d70f3`,
committed in `b47f5b9`. Output hash = the artefact's own `content_hash` field.

| Artefact | Output hash |
|---|---|
| `UCOS-RIE-CAPABILITY-CATALOG.json` | `fc18b55eda0d7ebf…` |
| `UCOS-RIE-MODEL.json` | `7ac4d25f26412438…` |
| `UCOS-RIE-SNAPSHOT.json` | `9c9caf564f67785e…` |
| `UCOS-RIE-HEALTH.json` | `27d632f550b41ca7…` |
| `UCOS-RIE-PROGRESS.json` | `82f4b7b859502578…` |
| `UCOS-RIE-DEPENDENCY-GRAPH.json` | `b4a2db7634929728…` |
| `UCOS-RIE-DIGITAL-TWIN.json` | `c16197a3dc2c13b8…` |
| `UCOS-RIE-EXECUTION-FRONTIER.json` | `8cddf19042325080…` |
| `UCOS-RIE-AEOS-READINESS.json` | `7fab8a2910d4d833…` |
| `UCOS-IMP-BASELINE-001.rib.json` | `ead2f04765a3ae76…` |

The Repository Integration Blueprint (17 artefacts under `00-MASTER/UCOS-RIB-001/`) was then
regenerated against the reconciled catalogue at `b47f5b9`; seal `4f424a68c3ac4e19`.

### Mandated provenance (STEP-006)

Every regenerated artefact now carries a `generation` block:

| Required field | Where it is recorded | Value for this generation |
|---|---|---|
| Source Commit | `generation.source_commit` | `e8d70f33f72ec330b1bd3f13fa80f8e35edda08e` |
| Repository HEAD | `generation.repository_head` | `{ref: integration/recovery-001, commit: e8d70f3}` |
| Generator Version | `generation.generator_version` | `1.0.0` |
| Generation Timestamp | `generation.generation_timestamp` | `2026-07-28T00:56:57+05:30` |
| Input Hash | `generation.input_hash` | `f18038c0d6e8a86f5d71e7318892a4830f9bbf35d02f4fff05f14462d9fcc46b` |
| Output Hash | `generation.output_hash_field` → `content_hash` | per artefact, above |

Two decisions were forced by the requirement that generation also be **reproducible**:

**The timestamp is the source commit's committer date, never the wall clock.** A wall-clock
stamp would make every regeneration of an unchanged repository produce different bytes,
which would satisfy the letter of "Generation Timestamp" while destroying "Generation MUST be
reproducible". Provenance that cannot be reproduced is not provenance.

**Coverage is fingerprinted by measurement, not by file bytes.** `coverage.xml` embeds a
wall-clock `timestamp` attribute, so hashing its bytes made the emitted evidence state — and
with it the input hash — change on every test run with no change in repository state. The
fingerprint is now taken over the four values the engine actually reads (`line_pct`,
`branch_pct`, `lines_covered`, `lines_valid`) and says so in the artefact
(`evidence_state.coverage_measurement.basis`). This follows the WP-002 precedent of dropping
gratuitously volatile fields from emitted state.

One honest caveat: `coverage.xml` is gitignored, so the input hash depends on one local build
artefact rather than on version-controlled content alone. It is reproduced by running the
canonical test suite at the same commit — verified in §006 below.

---

## 004 · Registration Delta Report

Computed two ways that agree exactly: by diffing the committed catalogue against the
regenerated one, and independently from the engine's own drift record
(`UCOS-RIE-SNAPSHOT.json → drift.implementation_drift`, 24 entries, all `ADDED`).

| Class | Count | Members |
|---|---|---|
| **Registered (added)** | **24** | see below |
| Removed | 0 | — |
| Status changed on a retained record | 0 | — |
| Any field changed on a retained record | 0 | — |
| Duplicate capability | 0 | — |
| Duplicate identifier | 0 | — |
| Duplicate canonical location | 0 | — |
| Deprecated / superseded | 0 | no record carries either disposition |
| Unresolved catalogue record (location not tracked) | 0 | — |

The reconciliation is **purely additive**: nothing was removed and not one field changed on
any of the 42 records that were already there.

| # | Registered capability | Category | Status | Cause |
|---|---|---|---|---|
| 1 | `application` | application | IMPLEMENTED | D1 + D3 |
| 2 | `application.tests` | application | IMPLEMENTED | D1 + D2 |
| 3 | `data` | data | IMPLEMENTED | D1 + D3 |
| 4 | `data.tests` | data | IMPLEMENTED | D1 + D2 |
| 5 | `engine` | engine | CERTIFIED | D3 |
| 6 | `engine.context` | engine | CERTIFIED | D4 |
| 7 | `engine.tests` | engine | CERTIFIED | D2 |
| 8 | `infrastructure` | infrastructure | IMPLEMENTED | D1 + D3 |
| 9 | `infrastructure.tests` | infrastructure | IMPLEMENTED | D1 + D2 |
| 10 | `intelligence` | intelligence | IMPLEMENTED | D1 + D3 |
| 11 | `intelligence.kernel` | intelligence | IMPLEMENTED | D1 |
| 12 | `intelligence.publication` | intelligence | IMPLEMENTED | D1 |
| 13 | `intelligence.realization` | intelligence | IMPLEMENTED | D1 |
| 14 | `intelligence.research` | intelligence | IMPLEMENTED | D1 |
| 15 | `intelligence.rie` | intelligence | IMPLEMENTED | D1 |
| 16 | `intelligence.tests` | intelligence | IMPLEMENTED | D1 + D2 |
| 17 | `platform` | platform | IMPLEMENTED | D3 |
| 18 | `platform.commercial_intelligence` | platform | IMPLEMENTED | D4 |
| 19 | `platform.providers` | platform | IMPLEMENTED | D4 |
| 20 | `platform.repository_intelligence` | platform | IMPLEMENTED | D4 |
| 21 | `platform.tests` | platform | IMPLEMENTED | D2 |
| 22 | `platform.universal_provider` | platform | IMPLEMENTED | D4 |
| 23 | `service` | service | IMPLEMENTED | D1 + D3 |
| 24 | `service.tests` | service | IMPLEMENTED | D1 + D2 |

**23 of the 24 are exactly the units GATE-07 named.** The twenty-fourth is `engine` itself:
the inventory discovers it as a unit, but the coverage metric excused it because it owns no
source file directly (every `engine/*.py` lives in a sub-package). It is registered anyway —
Repository Truth does not stop at the boundary of what a metric happened to count.

### One consequence disclosed, not hidden

The ordinal `unique_id` of all 40 retained code records shifted (e.g. `engine.acceptance`
`RC-01 → RC-06`), because the sequence is assigned over the discovered set and 24 records
were inserted into it. Nothing outside these generated outputs cites those ordinals — the
`RC-NN` namespace is separately and differently used by `adr/0002` and by
`00-MASTER/IMR-0000/07`, so it was never a stable cross-reference. The canonical **name** is
the capability's identity, and drift detection now keys on it; keyed on the ordinal, as it
was, this regeneration would have reported ~40 fabricated status changes.

Recorded as an observation for a later work package, not fixed here: an insertion-stable
identifier scheme would be preferable to an ordinal, but replacing the identifier scheme is a
redesign and this mission is a reconciliation.

---

## 005 · Coverage Report

Catalogue coverage of the implementation universe. The universe is Repository Truth as the
Repository Integration Blueprint defines it: every tracked `*/__init__.py` and
`*/*/__init__.py`.

| Code root | Implementation units | Catalogued | Coverage |
|---|---|---|---|
| `application` | 2 | 2 | 100% |
| `data` | 2 | 2 | 100% |
| `engine` | 17 | 17 | 100% |
| `infrastructure` | 2 | 2 | 100% |
| `intelligence` | 7 | 7 | 100% |
| `platform` | 28 | 28 | 100% |
| `service` | 2 | 2 | 100% |
| **Total** | **60** | **60** | **100%** |

| Metric | Before | After |
|---|---|---|
| Catalogue records | 42 | 66 |
| Uncatalogued implementation units | 23 | **0** |
| Unresolved catalogue records | 0 | **0** |
| Implementation-universe coverage | 61.7% (37/60) | **100% (60/60)** |

### Code census now measures the whole repository

Because the census follows the same derived roots, `UCOS-RIE-HEALTH.json` stops describing
two-sevenths of the repository:

| Root | Source files | LOC | Test files | Test functions |
|---|---|---|---|---|
| `application` | 67 | 23,741 | 45 | 1,082 |
| `data` | 73 | 23,577 | 49 | 887 |
| `engine` | 236 | 52,668 | 174 | 1,567 |
| `infrastructure` | 67 | 22,599 | 45 | 821 |
| `intelligence` | 65 | 15,617 | 6 | 115 |
| `platform` | 336 | 87,400 | 266 | 2,797 |
| `service` | 79 | 20,464 | 53 | 1,038 |
| **Total** | **923** | **246,066** | **638** | **8,307** |

Reported LOC moves 101,499 → 246,066 and tests 3,852 → 8,307. Nothing was written; two
roots became seven. Line coverage reads 96.93% → 94.11% and branch 95.10% → 90.06% for a
different reason: the prior figures were measured at `527485a`, and these are measured at
this commit by the canonical suite (`4751 passed`, gate ≥90% met at 93.45%). The EC-1/EC-2
coverage gate scope in `pyproject.toml` is unchanged; only the reading is current.

---

## 006 · Verification Report

| # | Verification | Result | Evidence |
|---|---|---|---|
| V-01 | Capability count matches the discovered set | **PASS** | 66 records = 60 implementation units + 3 automation + 1 operational memory + 2 specifications |
| V-02 | Registration closure — every implementation unit has a record | **PASS** | `uncatalogued_units = 0`; set difference (truth − catalogue) is empty |
| V-03 | Reverse closure — every record resolves to a tracked location | **PASS** | `unresolved_catalogue_records = 0` |
| V-04 | Zero duplicate capability | **PASS** | `duplicate_findings = 0`; RIB `DUP-CAPABILITY` (blocking) reports nothing |
| V-05 | Zero duplicate registration / identifier / location | **PASS** | 66 records → 66 distinct ids, 66 distinct names, 66 distinct locations |
| V-06 | Ownership — one canonical owner per capability | **PASS** | `owner_collisions = 0`; RIB `DUP-RUNTIME` (blocking) reports nothing |
| V-07 | Zero ownership drift on retained records | **PASS** | 0 field changes across all 42 retained records (§004) |
| V-08 | Knowledge Once | **PASS** | GATE-08 PASS; `closure_duplicate_homes = 0`, `closure_gaps = 0`; UAKOS-CLOSURE-002 CLOSED, 437 concepts, 0 gaps |
| V-09 | Repository consistency — catalogue agrees with the inventory | **PASS** | both derived from the same two tracked selectors; `unit_total = 236` unchanged, so no phantom unit was introduced |
| V-10 | Deterministic regeneration | **PASS** | `intelligence.rie verify` → `deterministic: true`, `mismatches: []` across all 10 outputs |
| V-11 | Idempotent under the programme's own writes | **PASS** | three consecutive builds; passes 2 and 3 byte-identical (fixed point) |
| V-12 | Reproducible from a clean checkout | **PASS** | see below |
| V-13 | Stable across a fresh coverage measurement | **PASS** | see below |
| V-14 | Test suite green | **PASS** | `4751 passed`, coverage gate met (93.45% ≥ 90%); 122 `intelligence/tests` pass |
| V-15 | No new lint findings | **PASS** | `ruff check intelligence/rie` 22 → 16 pre-existing E501; none introduced. `make lint` (engine + platform) clean; pre-commit hook passed on both commits |

**V-12 — reproducible from a clean checkout.** A detached worktree was created at the
generator anchor `e8d70f3`, and the outputs regenerated there from scratch. All ten artefacts
reproduced **byte-identically** to the committed ones, except for two fields — `evidence_state.branch`
and `generation.repository_head.ref` — which record the ref name of the checkout (`HEAD` when
detached) and are a property of the checkout, not of repository content. With those two
normalized, nine of ten artefacts are exactly identical, including the entire capability
catalogue, the census, the coverage measurement, the generation timestamp and the source commit.

`UCOS-RIE-SNAPSHOT.json` differs, correctly and by contract: it carries `drift`, a diff
against the *previously persisted* model. In the fresh worktree the prior model was the stale
one, so drift reported the 24 additions; in the reconciled tree the prior is the reconciled
model, so drift is empty. The engine documents exactly this ("given the same evidence AND the
same prior, drift is likewise deterministic"). Its 24-entry reading is the independent
corroboration used in §004.

**V-13 — stable across a fresh coverage measurement.** The canonical test suite was re-run,
rewriting `coverage.xml` (and its embedded wall-clock timestamp), and the outputs regenerated.
The only differences were `head`, `source_commit` and `repository_head` advancing — because
the commit anchor had genuinely advanced — with the coverage fingerprint, LOC, test counts and
the whole catalogue unchanged. The volatility that the byte-hash would have introduced is gone;
this was also confirmed directly by rewriting only the `timestamp` attribute, which produced
byte-identical outputs.

---

## 007 · Validation Report

| # | Subject | Result | Basis |
|---|---|---|---|
| L-01 | Repository inventory | **VALID** | RIB `GATE-01` PASS; 8 discovery sources, none empty; `unit_total = 236` |
| L-02 | Capability catalogue | **VALID** | 66 records, all schema-complete, all locations tracked, no duplicates |
| L-03 | Capability graph | **VALID** | RIB `02-REPOSITORY-CAPABILITY-GRAPH.md` regenerated; `GATE-10` PASS, `architectural_cycles = 0` (WP-002's result holds) |
| L-04 | Dependency graph | **VALID** | RIB `GATE-06` PASS, `unresolved_dependency_edges = 0`; `UCOS-RIE-DEPENDENCY-GRAPH.json` regenerated, `depends_on_acyclic` true |
| L-05 | Repository Intelligence outputs | **VALID** | 10 artefacts sealed with self-describing `content_hash`; all valid JSON; all declare `authority = "NONE (derived truth)"` |
| L-06 | Coverage metrics | **VALID** | 100% catalogue coverage of 60 units; census over all 7 roots; code coverage read at this commit |
| L-07 | No ownership drift | **VALID** | 0 field changes on 42 retained records; `owner_collisions = 0` |
| L-08 | Owner binding not duplicated | **VALID** | RIB `--check-no-fabrication` PASS — the blueprint still emits a pointer and zero rows for the catalogue it binds; the reconciliation happened in the owner, not in the consumer |
| L-09 | Nothing enumerated | **VALID** | RIB `--check-no-enumeration` PASS; the RIE generator likewise names no unit — roots and packages come from `git ls-files` |
| L-10 | Write scope respected | **VALID** | RIB `--check-write-scope` PASS; `test_engine_writes_only_under_intelligence_dir` passes; no write to `engine/**`, `platform/**`, `00-BOOK/**`, `00-SOURCE/**`, `99-FREEZE/**` |

All eight RIB self-guards pass: `--check-declaration`, `--check-no-enumeration`,
`--check-write-scope`, `--check-determinism`, `--check-substrate`, `--check-no-fabrication`,
`--check-reuse-before-create`, `--check-totality`.

---

## 008 · Certification Report

### GATE-07 — closed

| Gate | Metric | Before | After | Verdict |
|---|---|---|---|---|
| `GATE-07` Capability Coverage | `uncatalogued_units` | 23 | **0** | **PASS** |
| | `unresolved_catalogue_records` | 0 | **0** | |

Twelve blocking gates, 9/12 → **10/12**:

| Gate | Before | After |
|---|---|---|
| `GATE-01` Repository Discovery | PASS | PASS |
| `GATE-02` Repository Integrity | PASS | PASS |
| `GATE-03` Repository Verification | **FAIL** | **FAIL** |
| `GATE-04` Repository Validation | PASS | PASS |
| `GATE-05` Repository Certification | PASS | PASS |
| `GATE-06` Dependency Closure | PASS | PASS |
| `GATE-07` Capability Coverage | **FAIL** | **PASS** |
| `GATE-08` Knowledge Once | PASS | PASS |
| `GATE-09` Zero Duplicate Capability | PASS | PASS |
| `GATE-10` Zero Circular Dependency | PASS | PASS |
| `GATE-11` Zero Orphan Capability | **FAIL** | **FAIL** |
| `GATE-12` Repository Clean | PASS | PASS |

### Observed automatic changes (STEP-009 — observe only, do not repair)

**`GATE-11` changed automatically — improved, still failing.** `orphan_units` **9 → 4**.
Five units stopped being orphans without anyone touching them:
`application.tests`, `data.tests`, `infrastructure.tests`, `service.tests`,
`platform.repository_intelligence`.

This is not an accident and not a repair. `RCH-CATALOGUE` is one of the blueprint's seven
pre-declared reachability dimensions — *"the canonical capability catalogue holds a record for
it"*. Registering these units in their canonical catalogue satisfied a rule that was already
declared before this mission began. The orphan count fell because the orphan finding was, in
part, a **restatement of the catalogue gap**: a unit invisible to the catalogue was
unreachable in that dimension by construction.

The 4 remaining orphans are all operational-memory programmes, not code, and are untouched:
`00-MASTER/UAKOS-PHASE-001A-R1`, `00-MASTER/UAKOS-PHASE-001B`,
`00-MASTER/UAKOS-PHASE-003R`, `00-MASTER/UCOS-USIS-WAVE0`.

**`GATE-03` did not change.** `verifications_failed = 2`, unchanged. `VER-09` (no orphan
capability) still fails because 4 orphans remain, and `VER-11` (no dead engine) still fails —
a programme engine not named by any declared entry point. Both were left alone as instructed.

### Blueprint determination

`BLUEPRINT NOT CERTIFIED — REPOSITORY MUST STOP`, gate exit 1, on `GATE-03` and `GATE-11`.

This is the correct and expected outcome. Both remaining failures are explicitly out of this
mission's scope ("Do NOT attempt to repair them. Observe only."), and lowering a threshold to
manufacture certification is precisely what the blueprint's fail-closed design forbids. The
mission's own quality gate — GATE-07 PASS, with a clean repository, complete registration, a
synchronized catalogue, regenerated intelligence, zero ownership drift and zero duplicate
registration — is fully met.

Per the mission's success criteria, **Mission-000004 is NOT started automatically.**

### Remaining remediation requirements (for the owners named, not for this mission)

| Finding | Gate | Owner of the act | What would discharge it |
|---|---|---|---|
| `orphan_units = 4` | `GATE-11` | the four operational-memory programmes | bind each to a consumer, publish an interface for it, or disposition it for removal |
| `VER-11` dead engine | `GATE-03` | `Makefile` / CI entry points | name the programme engine from a declared entry point, or disposition the engine |
| `VER-09` orphans | `GATE-03` | same as `GATE-11` | discharged when `orphan_units` reaches 0 |
| Ordinal capability identifiers | — | `intelligence/rie` | an insertion-stable identifier scheme (observation only; see §004) |

---

## 009 · Git Cleanliness Report

| Checkpoint | `git status --porcelain` | HEAD |
|---|---|---|
| Before execution (STEP-001) | empty — CLEAN | `4712da5` |
| After generator reconciliation | empty — CLEAN | `e8d70f3` |
| After intelligence regeneration | empty — CLEAN | `b47f5b9` |
| After blueprint regeneration + this report | empty — CLEAN | `b7431ca` |
| Mission close | empty — CLEAN | this commit |

Mission-owned commits, in order:

| Commit | Scope |
|---|---|
| `e8d70f3` | `intelligence/rie/` — 6 generator files. No generated output. |
| `b47f5b9` | `intelligence/UCOS-*.json` — 10 regenerated Repository Intelligence outputs. No code. |
| `b7431ca` | `00-MASTER/UCOS-RIB-001/` — 16 regenerated blueprint artefacts, the README catalogue count (42 → 66), and this report. |
| this commit | this report — the anchor-delta disclosure below. |

No unrelated modification is included in any of the three. The blueprint's own
`GATE-12` (Repository Clean) reads `dirty_entries = 0` and `working_tree = CLEAN` at
`b47f5b9`.

One property is inherent and disclosed rather than worked around: a generated artefact
records the commit whose state it describes, which is necessarily its **parent** — a file
cannot contain the hash of the commit that introduces it. The intelligence outputs are
anchored at `e8d70f3` and committed in `b47f5b9`; the blueprint is anchored at `b47f5b9` and
committed in `b7431ca`. This is the same "regenerate at the committed anchor" convention
WP-002 established, and it is why the working tree is clean at every checkpoint above.

Re-running `make rib` / `make rib-gate` after this mission therefore rewrites the blueprint
artefacts with a one-commit anchor delta. Verified: the only differences are
`repository.head` and `repository.tracked_files` (+1, this report). Every metric, every
verdict, all twelve gates and all 236 units are identical. That delta is the anchor moving,
not the repository drifting.
