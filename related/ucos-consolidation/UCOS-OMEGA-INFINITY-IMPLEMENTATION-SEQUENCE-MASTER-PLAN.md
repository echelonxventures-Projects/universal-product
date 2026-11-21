# UCOS Ω∞ — IMPLEMENTATION SEQUENCE MASTER PLAN

| Field | Value |
|---|---|
| ARTIFACT | `UCOS-OMEGA-INFINITY-IMPLEMENTATION-SEQUENCE-MASTER-PLAN.md` |
| KIND | `CMG-K-17` — Plan (derived truth) |
| STANDING | **DECLARATIVE** (`CMG-000001` XII.6) |
| AUTHORITY | **NONE — DERIVED TRUTH.** Sequences; authorizes nothing. Creates no requirement, ADR, identifier, authority, form, law or gate. Mutates no code, configuration, registry or certification. Not registered in `CMG-REGISTRY.json`; **SHALL NOT be cited as constitutional authority** (`CMG-L-01`). |
| MODE | **OBSERVE.** |
| MUTATION | The single mutation is the creation of this file. Consequence disclosed in §5.2. |
| BASELINE | HEAD `bae59755` · `integration/recovery-001` · 76 dirty paths · ownership 151/549 = 27.5046% · `verify.sh --full` exits 1 |
| DERIVED FROM | `UCOS-OMEGA-INFINITY-CLOSURE-DEPENDENCY-GRAPH-DETERMINATION.md` (companion). Every wave boundary here is an edge there; no ordering originates in this document |
| POPULATION | 94 schedulable items of 135; 41 already `CLOSED` and carried as satisfied predecessors |
| UNIT | **Ordinal dependency depth, measured in graph edges.** Not time, not effort, not points, not personnel, not priority. Declared under `MP2-C-05`/`P-7` |
| RATIFICATION | **None sought and none available.** `MP2-C-04`: three located instruments record no authority in the corpus competent to ratify. Maximum attainable verdict anywhere is `CERTIFIED-PROVISIONAL` (`UCCEP-F-004`) |
| VERDICT | `SEQUENCE-DERIVED · 11 WAVES + 1 VEST-ONLY CLASS · 6 ACTIONABLE ROOTS · NO WAVE AUTHORIZED` |

---

## SECTION 0 — HOW TO READ THIS PLAN

### 0.1 Nine fields per wave

Each wave carries exactly the nine fields the governing directive requires: **Wave · Objective · Included closure items · Dependencies satisfied · Dependencies remaining · Required authority · Validation criteria · Evidence criteria · Certification criteria.**

### 0.2 Three reading rules that change the plan's meaning

**Rule 1 — wave exit and wave certification are different events.** The dependency graph finds a cycle in the certification relation (`DG-F-01`): certifying anything needs a green baseline; reaching a green baseline needs mutations; knowing those mutations were permitted needs Wave 0; certifying Wave 0 needs a green baseline. The cycle exists only in certification, never in implementation. **Wave 0 therefore completes before Wave 1 and is certified after it.** A plan requiring each wave to be certified before the next begins cannot execute this sequence at all.

**Rule 2 — no certification criterion may exceed the ceiling.** Tier T1 is vacant (`VAC-01`), every determination depending on it is provisional, and the maximum attainable verdict is `CERTIFIED-PROVISIONAL`. Every certification field below is bounded accordingly. A field promising unqualified certification would be unsatisfiable by construction.

**Rule 3 — "Required authority" distinguishes registered authority from owner and executor.** Only artifacts registered in `00-CMG/CMG-REGISTRY.json` with a tier and lifecycle state may be cited as authority: `CMG-000001`, `CEP-000`…`CEP-010`, `REG-AUTO-001`, `UCKP-LAW-0001`, `AUTH-INF-001`, `STATUS-001`, `UCI-001`, `GOV-INT-001`, `TECH-CONST-001`, `CONST-01`…`CONST-11`, the seven domain constitutions. The programmes the closure register names as owners — `UAUE-000001`, `UCXI-000001`, `UISD-000001`, `UCOS-UGA-001`, `UCOS-CEU-001`, `UCRD-001`, `UCCEP-000000`, `MCOS-000001`, `UVI-000001`, `UCDA-000001`, `UCOS-MXR-001`, `UCIC-001`, `URRC-000001`, `UCOS-UTCE-001`, `UMB-IMP-001` — each declare `authority: NONE` and are cited as **owner or executor**, never as ratifier. `ARCH-SECURITY-001` is registered nowhere and is flagged wherever a wave depends on it.

### 0.3 What "dependencies remaining" means

A dependency is **remaining** if it is unsatisfied at the moment the wave is read, whether or not an earlier wave is expected to satisfy it. Nothing is marked satisfied on the strength of a plan; only on measurement.

### 0.4 Parallelism and serialization

Waves **2, 3, 5 and 9** have disjoint prerequisite sets and may run concurrently after Wave 0. Waves **4, 6, 7, 8, 10** are chained. Serialization notes appear where two items in different waves touch one file — a file collision constrains concurrency, and is never treated as a dependency edge.

Critical chain: `0 → 4 → 6 → 7 → 8 → 10`, depth 6.

---

## WAVE 0 — MUTATION PERMISSIBILITY

| Field | Content |
|---|---|
| **Wave** | 0 — root. In-degree zero |
| **Objective** | Make it knowable whether any subsequent mutation was permitted. Not to govern mutation, which is Wave 4 — only to restore the classifier that answers the question at all |
| **Included closure items** | `MU-01` mutation classification · `MU-02` mutation → authority → evidence → execution → verification → certification chain |
| **Dependencies satisfied** | None required. `UCKP-LAW-0001` is registered (T4, `engine/uckp/law.py`), upstream of the defect and unaffected by it |
| **Dependencies remaining** | None blocking entry. Two constraints bind execution: the **bootstrap paradox** — the mutation-classification plane cannot authorize its own repair, dispositioned as *repair upstream, then classify the repair's own changed paths as the first act after*, i.e. self-disclosing rather than self-authorizing; and `P0-DECLARATION-001` places `platform/repository_intelligence` **outside** `UFC-14/15/16`, so the governance route is not the one the file path suggests |
| **Required authority** | `UCKP-LAW-0001` for the upstream repair (registered, delegated by `CMG-DLG-50`). The **mutation governance owner** to accept the self-disclosure of the repair's own changed paths. No `CEP-002` Article 28 act — no identifier is minted |
| **Validation criteria** | `validate_rule_coverage()` returns empty, where it currently returns *"rule 'R-09' is declared but no predicate implements it"* · `RULE_PREDICATES` holds R-01…R-09, where it currently holds R-01…R-08 · `mc.classify` returns `CLASSIFIED`, not `ERROR`, for `engine/nucleus/lifecycle.py` · the classifier consumes `mutation_class_extension.py` (206 lines, present and importing, currently not consumed) · **49 of 49 tests pass**, where 26 currently fail |
| **Evidence criteria** | Test node ids and results before and after · `classify()` output on a named real subject, showing the transition from `ERROR` to a class · the repair's own changed paths, classified by the repaired classifier, recorded as the first post-repair act |
| **Certification criteria** | **Deferred to after Wave 1** — `BLOCKED BY BASELINE` while `verify.sh --full` exits 1. This is `DG-F-01` and is the single most important scheduling consequence in this plan. Certification bound: `CERTIFIED-PROVISIONAL` |

**Why first, against intuition.** An implementation gap ranked last of seven by priority class is unavoidably first by dependency. The located precedent states it plainly: *"Priority axes describe why to act; they cannot order when."* Until `classify()` returns a class, no mutation made in closing any other item can be shown to have been permitted — and the classification outage is **total, not partial**, because rule coverage is evaluated at `classify:427-436` before the precedence loop runs.

---

## WAVE 1 — BASELINE ADMISSIBILITY

| Field | Content |
|---|---|
| **Wave** | 1 — root. In-degree zero; runs concurrently with Wave 0 |
| **Objective** | Make the effect of a closure action distinguishable from pre-existing failure, so that any later wave can produce admissible evidence. This is a precondition, not a priority |
| **Included closure items** | `VF-08` executable canonical validation · `AR-01` artifact identity (43 anonymous objects) · `ME-01` identity history · `ME-06` certification history (replay drift) · `VF-06` openness self-application · `EX-11` no permanent enumeration |
| **Dependencies satisfied** | The 15 stages are executable and self-verifying — UAUE obligation #9 measures its own wiring. The `ISD-L-07` fix is data plus a class and a count. The six-digit identity fix is measured sound: `{6,}` matches 6,185 of 6,187 ledger ids, identical to `{6}`, while admitting the 10⁶-th identifier |
| **Dependencies remaining** | Four sub-items, ordered by irreversibility rather than size, following the located `B-6` sub-sequence: **(1) `VF-06`/`EX-11`** — disclose 2 undeclared `ISD-L-07` sites carrying 3 occurrences, in `freeze_scan.preserved_sites` with a class and an occurrence count. Constraint `ISD-G-09`: `test_infinite_scope.py` asserts `len(unintentional) == 1` over the live declaration, so a disclosure requires an engine-plane change even though the disclosure is data. **(2) `AR-01`/`ME-01`** — mint 43 (`EXDOC` +36, `ENGINE` +2, `TESTOBJ` +5), a population that **grows on each commit of a new determination document**, since UGA's boundary is `git ls-files --cached` (§5.2). **(3) `ME-06`** — capture the drift delta **before** rendering; the render destroys the evidence of what drifted. **(4) `VF-08` residual** — 23 failing tests and 76 dirty working-tree paths, including `verify.sh` +45/−0 and `generated-artifact-registry.json` +864/−0, which require the owning programmes to commit their own work |
| **Required authority** | **(1)** document owners only — the cheapest node in the graph, needing no external authority. **(2)** a **new `CEP-002` Article 28 decision** under `REG-AUTO-001`/`CMG-DLG-13`; no standing blanket mint exists, because `ADR-0017` explicitly declined one: *"A future anonymous object requires its own decision under this same Article, not a standing blanket authorization."* Repository serials are minted by `ukb.py` only (`CAA-INV-04`). **(3)** the UAUE owner. **(4)** the owner of each modified file |
| **Validation criteria** | `python -m engine.infinite_scope.gate --quiet` exits 0 with `laws measured / refused : 11 / 0`, where it now reports `11 / 1` and `GATE CLOSED` · `uga_engine.py gate` exits 0 with `ANONYMOUS OBJECTS: 0`, where it now reports 43 and `GATE FAILED — 2 blocking invariant(s)` on `UGA-INV-01` and `UGA-INV-10` · `engine.uaue.gate --replay` exits 0, where it now reports drift at 1,316,175 bytes on both sides plus `13-EVOLUTION-HISTORY-REGISTER.md` at 1,611/1,611 · pytest reports 0 failures, where 23 fail; **coverage is already 97% against a 90 floor and is not the defect** · `./verify.sh --full` exits 0 |
| **Evidence criteria** | Stage-by-stage exit codes for all 15 stages before and after · the captured replay delta, retained as an artifact in its own right · the minted-identifier ledger diff against `id-ledger.json` · the Article 28 decision record enumerating the exact population **as measured at mint time**, not as previously reported · two consecutive full-suite runs, the standing bar `ADR-0017` met |
| **Certification criteria** | This wave **is** the certification precondition for every other wave. Its own criterion: `verify.sh --full` exits 0 on two consecutive runs from a clean tree, with the evidence store re-executing rather than reusing — `decide()` refuses reuse for `integration` and `full` modes by construction. Certification bound: `CERTIFIED-PROVISIONAL` |

**Recorded hazard.** `AR-01`'s remedy is `uga_engine.py run`, which mints. The register documents this exact command minting 43 identifiers *while observation was intended*, and the corpus documents a prior drift check minting 140 and a single `--gate` probe writing 11 tracked files, two operators' uncommitted bytes unrecoverable. **The cheapest path through Wave 1 runs through the precise mechanism Wave 4 exists to govern.** That is why sub-item (2) requires a decision rather than an invocation, and why the Article 28 record must enumerate the population rather than delegate enumeration to the tool.

---

## WAVE 2 — DISCLOSURE IS CLOSURE

| Field | Content |
|---|---|
| **Wave** | 2 — depth 1. Concurrent with Waves 3, 5, 9 |
| **Objective** | Convert undisclosed finite constraints into disclosed evolutionary states. **No new capability is built in this wave.** For most of these items the register's own closure criterion is disclosure: *"`ID-02`…`ID-05` entered in the assumption register (disclosure **is** the closure for these)"* |
| **Included closure items** | 25. Identity: `ID-01` numeric width ceiling · `ID-02` fixed prefix · `ID-03` fixed digest width · `ID-04` parse arity · `ID-05` namespace charset/length · `ID-06` registry kind openness · `ID-08` seven-property identity. Expansion: `IE-03` temporal emissions · `IE-04` spatial axis tuple · `IE-05` measurement seed tuples · `IE-09` currency pattern · `IE-10` technology neutrality scope. Declared bounds: `EX-04` constitution as entity · `EX-08` UI/UX as entity · `EX-10` decision as entity · `GV-04` nine lifecycle models · `IN-04` learning non-adaptive by design · `PL-05` priority ladder · `AR-04` artifact lifecycle · `CP-02` capability lifecycle · `VF-02` unknown technology · `CX-07` unknown future contexts · `ME-04` decision history (UNMEASURED) · `ME-05` evidence retention. Sweep: `VF-07` undeclared-closure discovery |
| **Dependencies satisfied** | The disclosure surface exists and is machine-checked. `ISD-L-01` never fails a closed enumeration — it fails a *disclosure record*, requiring a non-empty `closing_invariant`, a non-empty `admission` path, an existing `declared_at`, and either `intentional: true` or a named gap. `UCOS-OMEGA-INFINITY-UNIVERSAL-ASSUMPTION-REGISTER.md` exists as a destination |
| **Dependencies remaining** | Wave 0 for the permissibility of the code-touching members (`ID-01`, `IE-03`, `IE-09`). Wave 1 for `ID-01` specifically — `id_shape` flows into the universe digest via `alignment.py:514` and the replay stage already fails on drift, so the validated fix is unverifiable on a red baseline. `ME-04` needs measurement before disposition; the register marks it UNMEASURED rather than claiming either way. `IE-09` is a **fork, not a task**: generalise `_CURRENCY_PATTERN = ^[A-Z]{3}$` (enforced at `contracts.py:53,165`, load-bearing across 6 modules) or declare the bound — an owner's choice. It is a direct kernel contradiction, since `"currency"` sits in the kernel's `PROHIBITED_TOKENS`. `VF-07` must land **as disclosures, not as failures**, per `AD-G-01`'s own risk note |
| **Required authority** | Programme owners for their own declaration surfaces (`UISD-000001`, `UCOS-CEU-001`, `UCXI-000001`, `UCKP` — owners, not authorities). `platform/commercial_intelligence`'s owner for the `IE-09` fork. `ukb.py` alone for anything touching identifier shape (`CAA-INV-04`). **No new authority, no Article 28 act, no minting** — with one exception: if the `VF-07` sweep locates a closure whose disclosure requires a new declaration file, that file is an artifact and enters the registration path |
| **Validation criteria** | `infinite-scope` gate reports every disclosure with a `closing_invariant`, an `admission` path and an existing `declared_at` · `check_scope_expansion_capacity` passes with the disclosure list non-empty (an empty list is itself a violation, since it would make the law vacuous rather than satisfied) · the six-digit validator admits a 7-digit identifier while **zero existing identifiers change** · zero unqualified timestamp emissions remain at `obs/logging.py:59` and `registry/universal/audit.py:51` · the `VF-07` AST sweep for undeclared `Enum`/`frozenset`/literal tuples reconciles **two-way** against `closed_enumeration_disclosures` |
| **Evidence criteria** | Disclosure register diff, one entry per constraint, each naming its closing invariant and admission path · for `ID-01`, the measurement over all 6,187 ledger ids showing `{6,}` and `{6}` are currently equivalent · the `VF-07` sweep output as a disclosure batch with a per-finding classification, explicitly **not** as a failure list · for `ME-04`, the measurement that resolves the UNMEASURED marking either way |
| **Certification criteria** | Each disclosure is certified by the gate that reads it, at `CERTIFIED-PROVISIONAL`. `VF-07` cannot be certified complete by construction until it exists — `AD-G-01` guarantees that before the sweep lands, undeclared closures remain invisible, so completeness of §2 is claimable only after §2 builds the thing that would detect its own incompleteness |

**Note on the disclosure discipline.** The remediation for a closed enumeration here is never to open it. `engine/uckp/facets.py` closes 33 facets *on purpose*, so that every vocabulary inside them can stay open. Closure is not the defect; undisclosed closure is.

---

## WAVE 3 — VOCABULARY COERCION SYMMETRY

| Field | Content |
|---|---|
| **Wave** | 3 — depth 1. Concurrent with Waves 2, 5, 9 |
| **Objective** | Make the consuming layer accept everything the registering layer admits. Today a registered member passes the cross-check and then fails coercion, which means openness is asserted at one surface and refused at another |
| **Included closure items** | `RL-02` relationship type taxonomy · `CX-05` context kind openness · `VF-05` unknown relationship type · `IE-07` unlimited relationships · `RL-01` relationship identity · `RL-07` unknown future relations |
| **Dependencies satisfied** | Both defect sites are located precisely. `RELATION_TYPE_VOCABULARY` (`vocabulary.py:282`) is open; `RelationType(str, Enum)` has 17 members and a raising `coerce()` (`knowledge/model.py:186-212`). `ContextTaxonomy.extend()` admits taxa that then fail `coerce()` (`taxonomy.py:42,82,516`). `CEU` already admits `relationship-type` as a form, open as data (`catalog.py:50`) |
| **Dependencies remaining** | Wave 0 for permissibility. Wave 1 for certification. `RL-02` has a **second leg**: it is *not* in `uisd-declaration.json`'s disclosure register, so it is simultaneously a coercion defect and an undisclosed closure — the disclosure leg belongs to Wave 2 and the coercion leg here. `RL-01` needs a decision: one model carrying identity, owner, validity and history, **or** a declared crosswalk across the three existing models. `CX-05` is an independent site with the same defect shape; shape similarity is not a dependency |
| **Required authority** | `UCRD-001` and `UCXI-000001` as owners of their vocabularies (neither is a registered authority). `UCKP-LAW-0001` if the coercion contract is expressed as law rather than as module behaviour. `OWN-REQ-002` `EXACTLY-ONE-OWNER` constrains `RL-01`'s option space: ownership is deliberately not a relationship field, because 15 ownership dimensions would need 15 owners per subject, which the exactly-one-owner rule forbids structurally |
| **Validation criteria** | A newly registered relation type round-trips through `coerce()` without raising · a newly registered context taxon round-trips through `coerce()` without raising · `VF-05` proven **at the consuming layer**, not only at the registration layer · the existing 72 relationship tests pass unchanged |
| **Evidence criteria** | A registration-then-coercion round-trip for a type that did not exist before the test, at both sites · the diff showing the coercer now derives its admissible set from the registry rather than from an enum literal · for `RL-01`, either one model or a written crosswalk with a resolution rule |
| **Certification criteria** | `CERTIFIED-PROVISIONAL` on the round-trip evidence. `IE-07` and `RL-07` certify as consequences of `RL-02` rather than independently, since both rows resolve their gap to `RL-02` explicitly |

---

## WAVE 4 — GATE MODE DECLARATION

| Field | Content |
|---|---|
| **Wave** | 4 — depth 2 (after Wave 0). On the critical chain |
| **Objective** | Every check declares exactly one mode and honours it, proven by an injected violation. **Not** to close gate purity — the located determination is explicit that *"executing the full authorized scope does not close gate purity"* |
| **Included closure items** | `MU-03` no uncontrolled mutation · `MU-04` declared mode separation · `MU-05` observe-mode purity proof · `GV-06` gate registry completeness |
| **Dependencies satisfied** | The field name is settled: `H-06-R3` surveyed all 11 `*-declaration.json` and found no `gate_mode`, `execution_mode`, `mutation_mode` or semantic equivalent; verdict *"`gate_mode` ACCEPTABLE"*, `R-3 RESOLVED`, duplication risk none. No new registry, authority or schema family is needed — the mode belongs in the existing `*-declaration.json` beside `forbidden_write_prefixes`. Two positive precedents exist: `UGA-001`'s three declared modes (`run` mints and emits · `gate` verifies and mutates nothing · `stats` prints), and `UEG-000001`'s mutation-tested purity guard — injecting `ucos_ensure_venv` fails `test_verify_does_not_ensure_the_environment_it_is_verifying:826`; injecting a bare tool fails `test_no_bare_tool_is_ever_in_command_position:887` |
| **Dependencies remaining** | **Wave 0**, because declaring a mode is a mutation and its permissibility is exactly what the classifier answers. The authority chain is measurably gated: `R-4` must be corrected before `P-3` can be validly selected, and Phase 0 stands at **2 of 6** — `0.2` P-3 unselected, `0.5` `verify.sh` baseline never captured, `0.6` unrelated deltas not isolated, `0.4` unmeasured owner act. *"No phase begins until all six pass."* An internal guard also binds: *"No mode may be declared on a surface whose owning engine carries no `--check-declaration`."* And the measured scale: **4 of 46 `*-gate` targets declare a mode**, ≥24 gate paths mutate undeclared, and `GP-1`/`GP-3`/`GP-11` terminate OPEN (residual) even after the authorized scope executes |
| **Required authority** | **Mutation Governance Owner under `H-06`/`CR-09`** — the choice between *require `--gate` to be write-free* and *reclassify these gate modes as producers* is an act of that owner, not a measurement. Four decisions remain: the Option A/B mode policy, the `R-4` grandfathering window (`P-3`), confirmation of `gate_mode` as canonical, and the standing of an `OBSERVE_WITH_DECLARED_AUDIT_EMISSION` sub-class. `CEP-002` via `CMG-DLG-02` for the governance operation. Mode values point into named surfaces: `PRODUCER` → `generated-artifact-registry.json`, `EXECUTION` → `mutation-governance-boundary.json`, `OBSERVE` → no external reference. **`H-06` §5 forbids modifying `generated-artifact-registry.json` and `mutation-governance-boundary.json` under `H-06` at all** — a wave that needs to write them needs a different authorization |
| **Validation criteria** | Every `*-gate` target declares exactly one mode in its declaration surface · an injected violation fails, at each of the 49 targets, by the technique already proven at one · `GV-06`'s gate registry is **derived** rather than hand-declared: measured today, `uccep-bindings.json` binds 26 gates and 48 checks carrying `id`, `name`, `owner`, `argv`, `write_scope`, `tier`, `fail_closed`, `advisory`, `exit_semantics` — and **no `mode` field on any of them**; the discriminator present is `tier` (`boot` 25 · `standard` 19 · `full` 4). No code reads `.github/workflows/`, so a new workflow does not enter the registry automatically |
| **Evidence criteria** | Per-target declared mode, machine-readable · per-target injected-violation result · a before/after write-set measurement per gate invocation, including the 11 tracked files and 47 tracked files the corpus records as prior harm · gate enumeration derived from `.github/workflows/` reconciled two-way against the bindings |
| **Certification criteria** | `CERTIFIED-PROVISIONAL` on injected-violation evidence per target. **The wave's exit criterion is *mode declared and honoured*, never *purity closed*** — asserting the latter would contradict the located determination. `GP-1`, `GP-3`, `GP-11` remain disclosed residuals after this wave and must be carried forward rather than reported as closed |

---

## WAVE 5 — OWNERSHIP THRESHOLD

| Field | Content |
|---|---|
| **Wave** | 5 — root. In-degree zero; concurrent with Waves 2, 3, 9. **Highest leverage in the graph** |
| **Objective** | Raise canonical ownership to a declared threshold so the ownership property becomes satisfiable at all, and make owner declaration a condition of subject entry so the gain does not decay |
| **Included closure items** | `GV-01` every entity has an owner · `CP-05` no orphan capability · `AS-07` ownership discovery · `GV-03` no hidden authority |
| **Dependencies satisfied** | The engine is sound and the measurement is live and reproducible: `python -m platform.universal_ownership.cli homing` → `subjects 549 · declared 151 · contested 0 · unresolved 398 · remediable 195 · coverage 27.5046%`, with per-diagnosis residue `186 EVIDENCE-NOT-IN-CANONICAL-HOME-ZONE`, `212 NO-OWNERSHIP-EVIDENCE`, `45 LOCATOR-NOT-REGISTERED`, `2 LOCATOR-FORM-NOT-ADMITTED`, `195 ZONE-NOT-CANONICAL-HOME-ELIGIBLE`. `contested: 0` today. `homing-recommend` and `homing-draft` targets exist |
| **Dependencies remaining** | 398 owner declarations, of which **195 are diagnosed remediable** — the remaining 203 need something other than remediation. Two structural constraints: `OWN-REQ-002` `EXACTLY-ONE-OWNER` means this cannot be parallelized by assigning provisional co-owners and reconciling later, since *multiple survivors are a contest, never a merge*; and `GV-03`/`D-2.1` — *"the Canonical Ownership Principle is declared in one place and enforced in another, and the two do not share a key. This is the root of every conflict in §5"* (the ten registered `CONFLICT-01`…`CONFLICT-10`). `contested: 0` means no intra-plane clash; **it does not mean the planes agree.** A **hard arithmetic constraint**: subjects rose 542 → 549 while declared owners stayed at 151, so coverage is *falling*. A wave that resolves 195 subjects without making owner declaration a condition of subject entry will be overtaken |
| **Required authority** | Each subject's own owner declares — no central authority can declare on their behalf without creating the parallel-authority defect `GV-02` currently prevents. `CEP-002` via `CMG-DLG-02` for *"jurisdiction, ownership assignment, escalation and conflict resolution"*. The threshold itself is an owner decision: the register's closure criterion for §13 is *"ownership closed **or at a declared threshold**"*, and no threshold is currently declared |
| **Validation criteria** | `homing --gate` exits 0, or coverage reaches a **declared and recorded** threshold with the residue enumerated per diagnosis · `contested: 0` preserved throughout · coverage measured as **non-decreasing across two consecutive subject-population changes** — the only validation that tests the trend rather than the level · `GV-03`: the declaration and enforcement planes share a key, demonstrated by a query answerable in both |
| **Evidence criteria** | Per-subject owner declaration diff · `homing` output before and after, with the full per-diagnosis residue · the entry-condition mechanism that binds a new subject to a declaration at admission time, and a demonstration that a subject cannot enter without one · for `GV-03`, the shared key exhibited across both planes |
| **Certification criteria** | `CERTIFIED-PROVISIONAL` at the declared threshold, with the residue disclosed rather than omitted. **Full closure of `GV-01` is not a precondition for Waves 6–10**, but the ownership *property* of every item in them remains unsatisfied until the threshold is met — which is why this wave is a root and not a gate |

---

## WAVE 6 — ADMISSION-PATH COMPOSITION

| Field | Content |
|---|---|
| **Wave** | 6 — depth 3 (after Waves 4 and 5). On the critical chain |
| **Objective** | Make identity, context, relationship, ownership, security and impact **reachable from the admission path, with reachability measured**. Every one of these engines already exists; none is reachable from any door through which a subject actually enters |
| **Included closure items** | 14. Assimilation: `AS-05` context resolution · `AS-06` relationship discovery · `AS-08` security analysis · `AS-09` impact analysis · `AS-14` assimilation evidence key. Impact: `IM-01` architectural · `IM-04` security · `IM-05` knowledge · `IM-07` operational. Security: `SC-01` security at admission · `SC-02` authenticity/provenance · `SC-05` malicious input · `SC-06` cyber risk detection · `SC-07` supply-chain risk |
| **Dependencies satisfied** | The machinery exists and is measured. Impact: union blast radius, propagation ranking, layers and capabilities reached, certified-surface disturbance, bounded 0–100 risk with a severity band, read-only over the certified graph, CI-run. Context: 16-axis derivation with no default, no fallback and no branch on an axis, reporting `UNRESOLVED` with a derivation path. Relationship: graph plus composition, 72 tests. Security: 13 modules / 6,512 LOC built. Knowledge: 13 reasoners |
| **Dependencies remaining** | **Wave 4**, on a structural argument rather than a preference: *"Composing machinery into the admission path means running more machinery during admission. While ≥24 gate paths mutate undeclared, adding machinery to admission adds mutation to admission."* The demonstration is empirical — a diagnostic invocation minted 43 permanent identifiers. **Wave 5**, because `A-3` gates every condition of the composition step and a security rollup cannot attribute a finding to an unowned subject. **`AS-01`'s structural fact** bounds what "the admission path" even means: 14 admission surfaces, 2 mutually invisible planes, `platform/universal_assimilation/` importing `engine/` exactly once for an exception type only, no `engine/` module importing it, terminus `AssimilationReport` → coverage number → ∅. **`MI-3`** blocks `AS-06` via `MI-9` — the fabric creates no relationships, and edges need resolvable endpoints; `MI-3` is an owner decision whose substance is `ID-07`. Security is **architecturally non-enforcing with zero CI references**, so `SC-01` is a governance change before it is a code change. `SC-05` has no sanitization, no injection defence and no untrusted-content quarantine, and *UAUE trusts its declaration substrate absolutely*. `SC-06` has only ruff `S`; no dependency scan, no CI secret scan, no SAST; `14-SECURITY/` is 5 md, 0 code. `SC-07` has verified pins but no vulnerability data source — *pin integrity is not pin safety*. `IM-07` has no located surface at all |
| **Required authority** | **`ARCH-SECURITY-001` must answer enforce-versus-record** — and this authority is **registered nowhere**. It appears only in derived architecture data and in the register's leverage list. The wave's precondition is therefore *locate the authority or route the decision to `CEP-002` via `CMG-DLG-02`*. `CEP-003` via `CMG-DLG-03` for the execution/sequencing change to the admission path. `UVI-000001` as owner for the `AS-14` evidence-key registration. **Registered conflict `C-1`**: the closure register calls `AS-14` *"the cheapest closure in this scope; not blocked on authority"*, while `MI-10` routes the same finding as blocked on the `H-06`/`CR-09` mode decision. Both are located and they disagree; the conservative arc places it here, and the permissive reading would move it to Wave 1. **Registered conflict `C-2`**: `MI-5` routes impact wiring as *"WIRE, no blocker"*, against the register's grouping behind gate purity. Same disposition |
| **Validation criteria** | **Reachability measured, not asserted** — an import-graph or call-graph proof that each engine is invoked from the admission path, since the current defect is precisely that existence was mistaken for reachability · blast radius computed **before** acceptance, with a subject whose admission is refused on the computed value · `AS-14`: `ucos-assimilate` has a `uccep-bindings.json` entry and a `verify.sh` stage, therefore an evidence key, therefore proof it ran — today `.ucos-verification-evidence/` holds 8 stage directories and **none for assimilation** · security findings block or record according to the owner's answer, with the chosen semantics declared |
| **Evidence criteria** | Import-graph measurement before and after · an admission run producing a blast-radius artifact with a risk score and severity band · a new `.ucos-verification-evidence/assimilation/` directory with at least one entry keyed under `EVIDENCE_VERSION 2.0` over stage id, label, argc, ordered argv and sorted read-prefix content hashes · a refused admission with the refusal attributed to a named computed finding |
| **Certification criteria** | `CERTIFIED-PROVISIONAL` on reachability evidence. `SC-06` and `SC-07` cannot certify without an external data source, which is itself untrusted input entering a substrate with no defence against it — so their certification depends on `SC-05` landing first. This ordering is internal to the wave and is stated so it is not discovered late |

---

## WAVE 7 — DURABILITY AND LINEAGE

| Field | Content |
|---|---|
| **Wave** | 7 — depth 4. On the critical chain |
| **Objective** | Every history class durably persisted and reconstructible, and the corpus scope question answered. Lineage is the strongest of the seven autonomous-evolution prerequisites and is still a projection rather than a store |
| **Included closure items** | 13. `IN-11` evolution ledger durability · `ME-02` relationship history · `ME-07` knowledge version retention · `ME-08` runtime state durability · `CX-03` temporal validity · `CX-04` historical reconstruction · `RL-03` relationship validity · `EX-03` supersession + resurrection · `AR-02` artifact registration · `AR-05` code artifacts certified · `RL-06` relationship transformation · `MU-07` rollback · `CP-03` capability lifecycle stages |
| **Dependencies satisfied** | Lineage measures well where it is measured: 6 read-only sources → 1 in-memory projection, 12,899 edges, **0 dangling**, composition computed on demand rather than stored, `ACYCLIC_FAMILIES` detecting cycles. `IN-11` is narrower than first stated — `to_document`/`from_document` **exist** and `engine/uaue/history.py` rehydrates through them; what is absent is a **production writer**, since only a test writes the history file, to `tmp_path`. This is a located correction to an earlier finding and it shrinks the work |
| **Dependencies remaining** | Waves 0, 1, 4. `CX-03` is the internal root: `RelationDeclaration.from_dict()` fail-closes on non-null validity because `TemporalCoordinate` has **no `from_dict`** (measured absent as `M-8`), so temporal context is construction-only and not deserializable — which makes `RL-03` and `CX-04` unreachable until it lands. `MU-07` is **bounded by a located law**: rollback reverses records in reverse dependency order using the recorded topological order verbatim, but not live effects, and `ORL-15` forbids introducing an engine, scheduler, automation platform or executor — so *"roll back live effects"* is not an admissible closure criterion and a declared bound is. `AR-05` is **decision-gated**: `CONFLICT-04` measures the certified corpus at 1,233 artifacts, **0 `.py` files**, `executions: 0`, against 328,628 LOC across 1,795 source files — *"the only certification authority that returns CERTIFIED certifies a population containing none of the code"* — reserved as human decision `H-03`. `AR-02` is 228 unregistered eligible artifacts plus 55 awaiting VCS binding. `ME-05`'s closure is a **sharing decision, not a build**: the store is populated (8 stage directories, 44 PASS, 2 FAIL) and `.gitignore:222` excludes it, and since the store is a cache rather than a source of truth, the closure is a declaration of intent |
| **Required authority** | `CEP-007` via `CMG-DLG-07` for supersession and baseline mechanics on the history surfaces. `REG-AUTO-001` via `CMG-DLG-13` plus a `CEP-002` Article 28 act for `AR-02`'s 228 — at roughly 7–8× `ADR-0017`'s scale, and the corpus flags this as the highest-risk registration in the programme because `register.sh --guard`'s full transaction is implicated, not identity minting alone. **`H-03` for `AR-05`** — a reserved human decision. Programme owners for the rest |
| **Validation criteria** | A production writer emits the evolution ledger and `--replay` reproduces it byte-identically · `TemporalCoordinate.from_dict` exists and a validity-bearing declaration round-trips · a per-entity state query answers *"what state was X in at time T"*, which no event store answers today · runtime state persists to a path and a **cross-process** replay consumes it, where today it serialises to a string with no file write, no path and no store · `ukb.py enforce --pre` reports 0 unregistered eligible · `EX-03`: `supersede → resurrect → supersede` is reconstructible from the journal alone, which the current `AuditEntry` cannot do because it omits the successor list |
| **Evidence criteria** | Persist → simulated restart → recover byte-identical, per history class · the `AR-02` Article 28 record enumerating the population or its deterministic enumeration mechanism, with an explicit irreversibility disclosure · full-suite survival across two consecutive runs after registration, the bar `ADR-0017` met · for `MU-07`, the declared bound recorded rather than a live-effect capability built |
| **Certification criteria** | `CERTIFIED-PROVISIONAL` per class on round-trip evidence. `AR-05` cannot certify at all until `H-03` is decided; if code is admitted, the certified population changes by 1,795 files and every prior certification's scope statement is affected — which is why it is a decision and not a task |

---

## WAVE 8 — CROSS-CLASS TRANSACTION

| Field | Content |
|---|---|
| **Wave** | 8 — depth 5. On the critical chain |
| **Objective** | Admit a mutation spanning more than one governed class as one transaction. **This is a decision-then-capability wave, not a vesting wave** — a distinction derived from the located determinations and one the closure register's framing does not carry |
| **Included closure items** | `AS-01` single governed path · `AS-04` identity resolution · `ID-07` single identity authority · `IN-09` assimilation → intelligence edge · `IN-10` intelligence → assimilation edge · `MU-06` atomic mutation (cross-class) |
| **Dependencies satisfied** | The disposition is settled and the option space is closed by measurement. The terminal determination selects **C — transaction orchestration capability under an existing constitutional framework**, with A as embedded precondition and **B, a new authority, rejected on measured grounds**. It names the reasoning error directly: *"an invalid inference from 'no authority covers this' to 'a new authority is required.'"* The operative maxim: *"There is no transaction authority. Transaction orchestration holds no authority at all"* — role `EXECUTION` under `UCKP-ART-10`, `may_hold_authority: false`. All four candidate carriers were tested and rejected: `EvolutionRecord`/`EvolutionLedger` cannot represent; `change_event` cannot represent and *"its `commit` field is a trap"*; `UAUE-000001` cannot represent, being a measurement plane holding no authority **and the cause of the transaction under analysis**; `ART-12` state transition is *"right shape, wrong domain"*. It also corrects its own predecessor: *"Designate its authority, scoped to sequencing only"* is *"unexecutable as written, twice over"* — no authority may be designated, and sequencing is already owned by `CEP-003` and delegated by `CMG-DLG-03` |
| **Dependencies remaining** | Waves 0, 4, 7 — `IN-11`'s production writer specifically, since `MI-1` (the keystone: assimilation does not append to the evolution ledger) is *"blocked in part on `F-3`"*, and `F-3` reduces to the missing writer. **Eight owner decisions, all OPEN, none opened as a record**: `D-1` adopt disposition C2 (else `AT-1` stays OPEN and Phase 0 stays at 4 of 6) · `D-2` a governed category, where `GOVERNED_CATEGORIES` has 35 members and **no `transaction`** · `D-3` repository serial prefix, `ukb.py` only per `CAA-INV-04` · `D-4` which of the 33 closed facets carries the ordered path population · **`D-5` prospective-only binding, without which there is a bootstrap deadlock — *"the capability cannot lawfully be created by the act that creates it"*** · `D-6` ledger shape · `D-7` sequence of the four closure acts · `D-8` `AT-2` disposition. Constitutionally, *"a cross-class transaction is not a constitutionally existing category"*, and under `UCKP-ART-02` *"nothing exists constitutionally until it has become one"* — zero `atomic`/`transaction` tokens exist in `law.py` or the boundary artifact. `AIF-L14` bounds today's atomicity to **single-class only**. `ID-07`'s split is *"a **philosophy** conflict, not a format one"* — allocated versus derived identity — and `CAA-INV-04` reports PASS at 5,874 because the invariant as written does not detect it |
| **Required authority** | **Mutation Governance Owner** for `D-1`, `D-5`, `D-7`. **`UCKP` owner** for `D-2`, `D-4`, `D-6`. **`ukb.py` identity authority alone** for `D-3` (`CAA-INV-04`). **`CEP-002` via `CMG-DLG-02`** for the governed-category minting, and **`UCKP-LAW-0001` via `CMG-DLG-50`** for the invariant. **No cross-class transaction authority is to be created** — creating one is the rejected option, and this plan does not schedule it |
| **Validation criteria** | The proposed invariant holds: *"Every mutation spanning more than one class belongs to exactly one declared transaction, and no transaction claims a class as primary"* · a multi-class mutation either commits atomically or aborts leaving no orphan identity, extending `AIF-L14`'s single-class guarantee without amending it · `ID-07` reconciled, **or** the coexistence rule declared with a resolution rule — the register's closure criterion admits both · assimilation appends to the evolution ledger and intelligence reasons over the appended population, measured by import graph rather than asserted |
| **Evidence criteria** | The eight owner decisions recorded as records, not as intentions · an abort trace showing no orphan identity across classes · a ledger append originating from an assimilation, traced end to end · the `D-5` prospective-only binding recorded **before** the first act it governs, since retroactive binding is the deadlock |
| **Certification criteria** | `CERTIFIED-PROVISIONAL`. The capability is certified as a capability holding **no authority**; a certification asserting transaction authority would contradict the located determination and must be refused |

---

## WAVE 9 — PLAN OPERAND AND REQUIREMENT ENTITY

| Field | Content |
|---|---|
| **Wave** | 9 — root for its own chain. Concurrent with Waves 2, 3, 5 |
| **Objective** | Give `LAW P50-002` a measured operand, and make requirement a first-class entity with a writer and a gate. `MP2-C-01`: *"Every arrow in the target chain presumes a measurable predecessor, so this blocks the whole model"* |
| **Included closure items** | `PL-01` machine-readable plan state · `PL-02` dependency discovery · `PL-03` readiness discovery · `PL-04` risk/blocker discovery · `RQ-01` requirement as entity · `RQ-02` requirement evolution vocabulary · `RQ-03` requirement → plan edge · `RQ-04` requirement admission process · `EX-05` requirement as CEU form · `EX-09` implementation plan as entity |
| **Dependencies satisfied** | The consuming engine already exists and is better than the gap suggests: Kahn topological sort, cycle detection, and an effort-weighted critical path computed **twice** (in-corpus and ratification chain), a 7-state readiness lattice where `apply_readiness_closure()` propagates BLOCKED transitively so that BLOCKED is a *measured consequence*, a risk reasoner and 12 executability gates. `declare_form()` admits `requirement` as data with a byte-identical kernel fingerprint. Traceability is closed: 1,233 artifacts, 12,899 edges, **0 dangling** |
| **Dependencies remaining** | `PL-01` is the internal root and is stated as *unconditionally first* within its own chain. `mip.json` is re-verified absent, so `LAW P50-002` has **no operand**. The disposition is precise and constrains the method: **derive and register, never amend.** The MIP is **not among the sequencing engine's 8 `SRC` inputs**, so the closure is wiring an existing engine to a derived operand rather than building a planner. `RQ-02`'s vocabulary is **inert** — creation, modification, refinement, merging, supersession, deprecation, reactivation and splitting are declared with **no writer, no link field, no gate**; `SUPERSEDED` and `DEPRECATED` exist in a vocabulary nothing consumes. `RQ-04` is a process document, not executable code. Wave 1 for certification |
| **Required authority** | MIP owner to derive. `CEP-003` via `CMG-DLG-03` for sequencing. `UCKP-LAW-0001` for the requirement form and its invariant. `REG-AUTO-001` if `mip.json` is registered as an artifact. **`PL-07` ratification is explicitly out of scope for this wave and belongs to VEST** — `MP2-C-04` records that a correct `mip.json` would still be unratifiable, so this wave targets **measurability, not ratification.** Conflating them would make the wave unclosable |
| **Validation criteria** | `LAW P50-002` returns a **measured** value where it currently has no operand · `mip.json` is derivable from located sources and re-derives byte-identically, since a derived operand that cannot be re-derived is an amendment in disguise · the MIP appears among the sequencing engine's inputs and the engine's drift and derivability checks pass over it · a requirement round-trips as a CEU form · a supersession recorded through `RQ-02`'s vocabulary is readable by a gate |
| **Evidence criteria** | `mip.json` plus its derivation record naming every source · two consecutive derivations producing identical bytes · `roadmap-gate` drift and derivability output with the MIP included · a written requirement-evolution event, and the gate reading it |
| **Certification criteria** | `CERTIFIED-PROVISIONAL` on derivability and measurability. **Ratification is not attempted.** The register's closure criterion for §17 asks for *"a competent ratifier named"* — no wave can satisfy that, and the honest disposition is to carry it as VEST rather than to schedule it |

---

## WAVE 10 — UNIVERSAL EVOLUTION UPDATE FABRIC

| Field | Content |
|---|---|
| **Wave** | 10 — depth 6. Terminal on the critical chain |
| **Objective** | Admit the system's own technical substrate — software updates, language evolution, framework evolution, library evolution, architecture evolution, AI-model evolution — as an evolvable, governed population. **The fabric does not currently exist**, and its absence is disclosed rather than undetected |
| **Included closure items** | Register items: `EX-06` technology as entity · `EX-07` runtime/environment as entity · `IN-12` Universal Science Intelligence. Derived nodes: `UEUF-00` substrate entity form · `UEUF-01` measuring owner publishing a sealed artifact · `UEUF-02` candidate-class declaration · `UEUF-03` vulnerability/currency data source · `UEUF-04` language-version evolution path · `UEUF-05` architecture evolution causation · `UEUF-06` AI-model evolution as assimilated external state · `UEUF-07` framework and library classes |
| **Dependencies satisfied** | More than the absence suggests. `ISD-L-09` *"Technology Is An Evolutionary State"* is law and passes: `check_technology_is_evolutionary_state` requires `[project].dependencies` empty (measured `dependencies = []`), requires `requires-python` present without `<`/`<=`/`==` (measured `>=3.12`, a floor with no ceiling), and requires every `==` pin to be disclosed with a reason bidirectionally. `architecture` **is** a declared CEU form carrying the evolution primitive. `declare_form()` admits a new form as data with a byte-identical kernel fingerprint, so `UEUF-00` is registration rather than construction. **And the keystone finding is favourable**: `candidate_class` in `engine/uaue/discovery.py` is pure data — *"a source added to the declaration tomorrow needs no code here"* — so `UEUF-02` requires **no engine code** |
| **Dependencies remaining** | **All seven autonomous-evolution prerequisites, none satisfied**: identity (0 of 8 items closed — the register's weakest scope), ownership (27.5046% and falling), security (built, architecturally non-enforcing, zero CI references), impact analysis (built, unreachable from admission), validation (executable, 4 stages red), rollback (records not live effects; single-class only), lineage (projection with zero persistence; no production writer). **The true keystone is a measuring owner, not an engine**: discovery *"does not inspect the working tree… It reads the sealed derived-truth artifacts that located owners publish"*, and none of its nine declared sources measures a pin, a language version or a model version. No owner publishes such an artifact. Per class: **(a)** no vulnerability data source, no Dependabot, no renovate, no pip-audit, no SBOM, no lockfile — `.github/` contains only `workflows/`; **(b)** duplicate hardcoded language floors at `engine/determinism/hermetic.py:61-63` and `engine/context/catalog.py:135`, and language neutrality recorded as unmeasured; **(c)/(d)** no form, no registry, no candidate class, and currently an empty population since there is no runtime dependency surface; **(e)** the `CEP-007` supersession and `CEP-009` amendment path exists, but *"evolve architecture — **DECLARED, NOT CAUSED**"*, resting on *"nothing in the repository causes capability to increase"*; **(f)** an internal forecaster is **refused by design**, for a stated reason — *"a predictive engine would produce an impact estimate that could not be falsified"* — leaving only the assimilation route, which depends on Waves 6 and 8. `IN-12` is 36 markdown files and 0 code, six of whose registries (`USIS-REG-005` algorithm, `-006` model, `-008` insight, `-009` reasoning trace, `-011` learned change, `-012` self-evolution) are the Infinite Intelligence registries with no mechanism (`MI-12`) — the single largest documented-only surface |
| **Required authority** | `UCOS-CEU-001` as owner to declare the substrate form (`declare_form()` needs no authority beyond the form owner). **A located owner must be named for `EX-06`, which currently has none** — this is the wave's first blocker and it is an ownership act, not an engineering one. `UISD-000001` owner for the `ISD-L-09` and `ISD-G-07` extension. `CEP-007` via `CMG-DLG-07` for architecture supersession; `CEP-009` for amendment. `CEP-002` for the `IN-12` programme-scope decision — realize or declare the documented-only standing with an owner. **`UEUF-06` must not create a forecaster**; the refusal is preserved and the route is assimilation |
| **Validation criteria** | A substrate subject — a dependency pin, a language version, a framework version, a model version — is **discovered** by the existing loop with **no engine code change**, proving `UEUF-02` · UAUE obligation #6 conducts its open-world proof on that subject: in no registry, of no declared class, owned by nobody, reaching a settled certified run with no new registry, authority, engine or schema · `ISD-L-09` continues to pass with the new disclosures · a substrate update traverses identity → ownership → security → impact → validation → rollback → lineage with each step **measured**, not assumed · `ISD-G-07`'s disclosure is discharged: technology identity becomes measured on at least one axis beyond `pyproject.toml` pins |
| **Evidence criteria** | The sealed artifact published by the measuring owner, and the declaration edit that admits its candidate class, shown **separately** so the no-engine-change claim is falsifiable · an end-to-end trace of one substrate update through all seven prerequisites · for `(f)`, an externally-sourced model assessment assimilated and routed through verification, with the absence of an internal forecaster preserved as evidence · for `(e)`, a supersession record under `CEP-007` |
| **Certification criteria** | `CERTIFIED-PROVISIONAL` per class. **No class certifies before its prerequisite closes**, and the binding prerequisite is identity, at 0 of 8. `UEUF-07` should certify as *form declared, population empty*, not as a capability — certifying machinery over an empty population would manufacture evidence rather than discover it, which is the failure mode the closure roadmap already declines to schedule elsewhere |

---

## WAVE VEST — NOT REACHABLE BY WORK

| Field | Content |
|---|---|
| **Wave** | VEST — outside the depth ordering. **Not backlog** |
| **Objective** | Record what no amount of repository work discharges, so that it is not mistaken for pending work. The located instruction is direct: *"Reserved decisions are therefore owner decisions awaiting a person, not repository work awaiting a process. Sequencing them as backlog would misrepresent them"* |
| **Included closure items** | `PL-07` plan ratification. Corpus-level conditions: `VAC-01` T1 occupancy · `CMG-OQ-01` *"which authority is competent to ratify `CMG-000001`?"* · `OA-6` constitute a T1 authority · the unqualified-certification ceiling |
| **Adjacent, not included** | `AR-05` is decision-gated by `H-03` but its *work* is ordinary once decided, so it is scheduled in Wave 7 with its decision named rather than counted here. This keeps the wave fields disjoint: every register item appears in exactly one *Included closure items* field |
| **Dependencies satisfied** | The vacancy is fully documented rather than latent. `CMG-REGISTRY.json:255` declares T1 `VACANT` with vacancy `VAC-01`, the declared superior existing *"only as frozen non-normative source material under `00-SOURCE/CONSTITUTIONS/` (.docx)"*, and *"no ratified normative artifact occupies the tier"* |
| **Dependencies remaining** | An act outside the corpus. `MP2-C-04` rests on three located instruments: `UCAF-RC-01` (`uccep-bindings.json`) *"no located authority is competent to ratify"*; `UCAF-RC-02` (`CMG-REGISTRY.json`) *"no ratified normative artifact occupies the vacant constitutional tier"*; `UCAF-RC-03` (`00-CMG/README.md`) *"the corpus contains no authority competent to ratify anything"*. Classified `UCAF-F-002` `STANDING-CONSTITUTIONAL-CONFLICT`, with `UCAF-F-003`: competence to ratify and the ratifying act are distinct, and *"only the first is closable by measurement."* `OA-6` is *"NOT ACTIONABLE IN-REPOSITORY"*. Promotion of a lower instrument is forbidden — `CMG-000001` XVII.4 forbids it, LXXXI.5 voids any reading that permits it |
| **Required authority** | **An external constituent act.** No in-repository instrument may be cited, and citing one would be the specific error `UCAF` was written to prevent |
| **Validation criteria** | Not applicable. There is no executable check for competence to ratify, and constructing one would assert the answer it purports to measure |
| **Evidence criteria** | The three located instruments, already recorded, and the vacancy declaration. This wave's evidence is complete; only its discharge is absent |
| **Certification criteria** | **None available.** `UCCEP-F-004` sets the standing ceiling: *"Maximum attainable verdict anywhere in this repository is `CERTIFIED-PROVISIONAL`."* Every certification criterion in every wave above inherits this bound, and a plan promising more would be unsatisfiable by construction |

---

## SECTION 1 — SEQUENCE SUMMARY

| Wave | Precondition discharged | n | Depth | Root | Authority class |
|---|---|---|---|---|---|
| 0 | Mutation permissibility is knowable | 2 | 0 | ✅ | Registered law + owner acceptance |
| 1 | Evidence distinguishable from pre-existing failure | 6 | 0 | ✅ | Article 28 decision + programme owners |
| 2 | Finite constraints disclosed | 25 | 1 | — | Programme owners; no minting |
| 3 | Consuming layer accepts what registration admits | 6 | 1 | — | Module owners |
| 4 | Every check declares one mode | 4 | 2 | — | Mutation governance owner (`H-06`/`CR-09`) |
| 5 | Ownership property satisfiable | 4 | 0 | ✅ | Each subject's owner + `CEP-002` |
| 6 | Admission computes before it accepts | 14 | 3 | — | `ARCH-SECURITY-001` — **unregistered** |
| 7 | Every history class durable | 13 | 4 | — | `CEP-007`, Article 28, `H-03` |
| 8 | Mutation may span classes atomically | 6 | 5 | — | 8 owner decisions; **no new authority** |
| 9 | Completion measurable over a plan operand | 10 | 0 | ✅ | MIP owner + `CEP-003` |
| 10 | Substrate is an evolvable governed population | 3 + 8 | 6 | — | Form owner; **`EX-06` has none** |
| VEST | — | 1 + 4 | — | — | **External constituent act** |

Reconciliation: 2+6+25+6+4+4+14+13+6+10+3+1 = **94**, matching the register's 53 OPEN + 27 GOVERNED + 14 BLOCKED exactly. 41 `CLOSED` items are carried as satisfied predecessors and are not scheduled.

**Actionable roots: 6** — Wave 0, Wave 1 (four independent sub-items), Wave 5, Wave 9, and within Wave 2 and Wave 3 the disclosure and coercion legs. **Decision-only roots: 2** — the `H-06`/`CR-09` mode policy, and the eight transaction decisions. **No single action discharges more than one root.** Three prior determinations reach the same conclusion over their own populations by independent derivation.

---

## SECTION 2 — WHAT THIS SEQUENCE REFUSES TO SCHEDULE

| Refused | Reason |
|---|---|
| Any calendar, duration or velocity | `PL-05` measures effort in points, never calendar time, because *"the repository carries no velocity evidence"*; `07-CRITICAL-PATH-ANALYSIS.md:5` refuses time estimates as an assumption with no Repository-Truth basis. One prior document asserts a 70-week schedule; it is not inherited (`C-4`) |
| Ratification of anything | No competent ratifier exists. Scheduling ratification would present an external act as internal work |
| A cross-class transaction **authority** | The located determination rejects that option on measured grounds and selects a capability holding no authority |
| An internal forecaster for AI-model evolution | Refused by design with a stated reason; the assimilation route is scheduled instead |
| Live-effect rollback | `ORL-15` forbids introducing an engine, scheduler, automation platform or executor. A declared bound is scheduled instead |
| Machinery over an empty population | `UEUF-07` certifies as *form declared, population empty*. Building an abstraction to move a status would manufacture evidence rather than discover it |
| Any wave "authorized" by this document | This document has `authority: NONE` |

---

## SECTION 3 — SERIALIZATION NOTES

File collisions constrain concurrency without creating dependency edges:

- `engine/uckp/store.py` — `ME-07` (Wave 7) and any knowledge-persistence work share it. Sequence within the wave rather than overlapping two changes to one file, following the located `REQ-14`/`REQ-34` precedent: *"shares an owner and a file… sequencing them together is more efficient than two separate passes."*
- `00-MASTER/UISD-000001/uisd-declaration.json` — Wave 1's `ISD-L-07` `preserved_sites` edit and Wave 2's `closed_enumeration_disclosures` edits touch one file in two waves. `ISD-G-09` adds that either may require an engine-plane test change.
- `engine/verification_intelligence/` — Wave 1's stage repairs and Wave 6's `AS-14` stage registration touch the same declaration.
- `00-MASTER/UCCEP-000000/uccep-bindings.json` — Wave 4's mode field and Wave 6's `AS-14` binding. Note that `H-06` §5 forbids modifying `generated-artifact-registry.json` and `mutation-governance-boundary.json` under `H-06` at all.
- The 76 dirty working-tree paths, including `verify.sh` +45/−0 and `generated-artifact-registry.json` +864/−0, must be isolated by their owning programmes before Wave 1 can measure anything cleanly. This is Phase 0 condition `0.6`, currently failing.

---

## SECTION 4 — FALSIFIABILITY

Inheriting the located precedent: **if any wave can be shown closable without its declared predecessor, that edge is wrong and both this plan and the companion graph are amended.**

The cheapest refutations, in order of cost:

1. Register an evidence key for `ucos-assimilate` that mutates nothing → moves `AS-14` from Wave 6 to Wave 1 and refutes `C-1`'s conservative arc.
2. Compose the impact engine into an admission path with no undeclared write → moves `AS-09`/`IM-01` earlier and refutes `C-2`.
3. Produce admissible certification evidence for any closure while `verify.sh --full` exits 1 → refutes the plan's most load-bearing edge and collapses Wave 1 from a precondition to a peer.
4. Reach `CLOSED` on any item whose subject is unowned → refutes the ownership property edge and demotes Wave 5.
5. Have UAUE discover a substrate candidate class with no owner publishing a sealed artifact → refutes the Wave 10 keystone and collapses that wave.

---

## SECTION 5 — VERDICT AND SELF-DISCLOSURE

### 5.1 Verdict

| Field | Value |
|---|---|
| WAVES | **11** + 1 vest-only class |
| ITEMS SEQUENCED | **94** of 135; 41 carried as `CLOSED` |
| UNIT | Ordinal dependency depth (`P-7` declared) |
| CRITICAL CHAIN | `0 → 4 → 6 → 7 → 8 → 10`, depth 6 |
| ACTIONABLE ROOTS | 6; **decision-only roots** 2 |
| CONCURRENT AFTER WAVE 0 | Waves 2, 3, 5, 9 |
| CHEAPEST ACTION | Wave 1 sub-item (1) — `ISD-L-07` site disclosure; document owners only |
| HIGHEST LEVERAGE | Wave 5 — ownership; gates the ownership property of all 135 items, and is regressing |
| DEEPEST DEPENDENCY | Wave 10 `UEUF-06` — all seven prerequisites plus a blocked assimilation fabric |
| CERTIFICATION CEILING | `CERTIFIED-PROVISIONAL` everywhere (`UCCEP-F-004`) |
| CERTIFICATION CYCLE | Disclosed as `DG-F-01`. Wave 0 completes before Wave 1 and is certified after it |
| AUTHORITY GAPS | `ARCH-SECURITY-001` registered nowhere (Wave 6) · `EX-06` has no owner (Wave 10) · no competent ratifier (VEST) |
| CONFLICTS CARRIED | 7, from the companion graph. None resolved by preference |
| CREATE DISPOSITIONS | **0** by this document |
| AUTHORIZATION STATE | `H-06` IADR §8 signed for its §4 scope; **Phase 0 stands at 2 of 6**; no wave here is authorized by anything |
| VERDICT | `SEQUENCE-DERIVED · NO WAVE AUTHORIZED · NOTHING IMPLEMENTED` |

### 5.2 What creating this file did — measured, including one error made and corrected

Disclosed rather than omitted, following the register's discipline of recording its own effects. Full detail, including the error, is in the companion graph §13.2.

- **`ISD-L-07` — the companion graph's first draft violated the law it was describing**, by quoting the law's *title*, which contains as a substring one of the nine phrases the law scans for. This is the trap `engine/infinite_scope/contract.py:24-28` documents: a detector matching its own source would be its own first finding. Corrected by citing `ISD-L-07` by identifier only. **Re-measured: the gate now refuses on the two pre-existing files only; neither of these documents appears.** Carry-forward for Wave 2: any disclosure batch that quotes law titles will trip the laws it discloses.
- **`UGA-INV-10` — the anonymous-object population does not rise on creation.** Measured after writing both files: `ANONYMOUS OBJECTS: 43`, unchanged, with neither file appearing. UGA's population is `git ls-files -z --cached --exclude-standard`, i.e. **version-controlled files only**, so untracked files are outside the artifact boundary. **The population rises on commit.** This corrects the more eager claim made in the plan's first draft.

**Consequence for Wave 1, restated because it survives the correction:** the `CEP-002` Article 28 decision must enumerate its population **as measured after any commit of new determination documents**, not from the standing figure of 43. That instruction appears in Wave 1's evidence criteria and remains correct; only its cause has changed from *creation* to *commit*.

---

## STOP

Sequence derived. No implementation performed. No fix applied. No refactor. No optimization. No certification issued. No code, configuration, registry, declaration or gate modified. No requirement, ADR, identifier, authority, form or law created. No wave authorized, entered or begun. The single mutation is the creation of this file, whose two measured consequences are disclosed in §5.2.

**Awaiting explicit authorization.**
