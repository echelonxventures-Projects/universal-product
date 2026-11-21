# UCOS Ω∞ — CLOSURE DEPENDENCY GRAPH DETERMINATION

| Field | Value |
|---|---|
| ARTIFACT | `UCOS-OMEGA-INFINITY-CLOSURE-DEPENDENCY-GRAPH-DETERMINATION.md` |
| KIND | `CMG-K-17` — Determination (derived truth) |
| STANDING | **DECLARATIVE** (`CMG-000001` XII.6) |
| AUTHORITY | **NONE — DERIVED TRUTH.** Derives ordering; asserts none. Creates no requirement, ADR, identifier, authority, form, law, gate or invariant. Mutates no code, configuration, registry or certification. Not registered in `CMG-REGISTRY.json`; **SHALL NOT be cited as constitutional authority** (`CMG-L-01`). |
| MODE | **OBSERVE.** Read-only over the corpus. |
| MUTATION | The single mutation is the creation of this file. Its measured consequence is disclosed in §13.2 rather than omitted. |
| BASELINE | HEAD `bae59755` · `integration/recovery-001` · 76 dirty working-tree paths · re-measured this session |
| SUBJECT | The 135 items of `UCOS-OMEGA-INFINITY-100-PERCENT-CLOSURE-MASTER-REGISTER.md`, plus derived nodes for populations the register does not carry |
| METHOD | **Edges are admitted only from cited evidence.** No edge is admitted from severity, priority, effort, discovery order, thematic adjacency or convenience. §1 states the admission rule and what it refuses. |
| PRIOR ORDERINGS | Five exist over five different populations. **None orders the 135 register items.** Verified mechanically (§2.3). This determination does not inherit any of them; it compares against them (§12). |
| VERDICT | `GRAPH-DERIVED · 11 WAVES + 1 VEST-ONLY CLASS · 6 INDEPENDENT ROOTS · 1 CERTIFICATION CYCLE DISCLOSED · 7 CONFLICTS REGISTERED · NOTHING AUTHORIZED` |

---

## SECTION 0 — WHAT THIS DOCUMENT IS, AND WHAT IT REFUSES TO BE

This document answers one question: **given only what the repository can be measured to say, what must precede what?**

It is not a plan. The plan is the companion artifact `UCOS-OMEGA-INFINITY-IMPLEMENTATION-SEQUENCE-MASTER-PLAN.md`, which consumes this graph. This document is the derivation; that one is the schedule.

Three things this document deliberately does not do:

1. **It does not order by importance.** The precedent is explicit and it is the repository's own: *"Priority axes describe why to act; they cannot order when"* — `UCOS-OMEGA-INFINITY-GAP-CLOSURE-SEQUENCING-DETERMINATION.md` §2. That determination found its first wave was an item ranked last by priority class, because dependency and priority are different relations. The same inversion recurs here (§8.1) and is derived, not assumed.
2. **It does not assert calendar time, effort, velocity or duration.** `PL-05` records that the repository's own sequencing engine measures effort *in points, never calendar time*, because *"the repository carries no velocity evidence"*, and `07-CRITICAL-PATH-ANALYSIS.md:5` refuses time estimates as *"an ASSUMPTION with no Repository-Truth basis"*. One prior document violates this (§12, `C-4`); this one does not.
3. **It does not treat any example as a boundary.** §11 validates this claim against the nine prohibitions in the governing directive, and applies the test to this document's own vocabulary.

---

## SECTION 1 — DERIVATION METHOD

### 1.1 The edge-admission rule

A directed edge `A → B` ("A must precede B") is admitted if and only if it has a source of one of exactly three kinds, and the source is cited at the edge:

| Kind | Source | What makes it binding |
|---|---|---|
| **E1** | A register row's residual-gap cell names another item, or names an external code that resolves to another item | The register states the blocking claim itself. Its rows are the only place the 135 items make claims about each other |
| **E2** | An external located determination states a hard prerequisite between the underlying findings | The determination is derived truth over measured state, and the register cites it as the row's evidence |
| **E3** | A measured mechanism makes the ordering unavoidable — the later act is not verifiable, not permissible, or not representable until the earlier one completes | Mechanism, not judgement. Falsifiable by exhibiting a counter-execution |

`{E1, E2, E3}` is a **closed enumeration, closed on purpose**, and its closure is disclosed here with its admission path: a fourth source kind may be admitted, and does so by amending this section and re-deriving §6. The closing invariant is that no edge may exist without a citable source. This follows the discipline at `engine/infinite_scope/contract.py:16-20` — a closed enumeration is not a defect; a *silently* closed one is, and each must name the invariant that closes it and the path by which a member is admitted.

### 1.2 What is refused as an edge

Refused, with the reason each would be wrong rather than merely unhelpful:

| Refused basis | Why |
|---|---|
| Severity or priority class | Different relation from dependency; the `G-01` inversion is the located proof |
| Effort, cost, or size | No velocity evidence exists (`PL-05`); an effort edge would be an invented measurement |
| Shared scope, section, or theme | The register's 17 sections are subject scopes, not order. Two items in one section are frequently independent (`§1`: `EX-01` is `CLOSED`, `EX-09` is `BLOCKED`) |
| Shared owner | Sharing an owner constrains parallelism, not order. Where it does constrain, it is recorded as a *serialization note* in the sequence plan, never as a graph edge |
| Discovery order | The register's own count-provenance note records a first draft that miscounted itself; order of discovery carries no dependency information |
| Convenience of narration | A wave that reads well is not a wave that is load-bearing |

### 1.3 Node classes

| Class | Meaning | Population |
|---|---|---|
| **REGISTER-ITEM** | One of the 135 item IDs in the closure master register | 135 |
| **DERIVED-NODE** | A required node the register does not carry, introduced here with its evidence of absence | 8 (`UEUF-00`…`UEUF-07`) |
| **VEST-ONLY** | Not reachable by any amount of repository work; discharged only by an act outside the corpus | 1 register item + 4 corpus-level conditions |

`{REGISTER-ITEM, DERIVED-NODE, VEST-ONLY}` is closed; a new class is admitted by naming its evidence source and its discharge mechanism.

### 1.4 What is *not* closed

The **wave set is not a closed enumeration.** Waves here are derived partitions of the node set by discharged precondition, recomputable from measured state. A new wave enters whenever a measured prerequisite is found to be load-bearing, without amending this document's structure. This is the property that keeps the model open under §11.

---

## SECTION 2 — NODE POPULATION

### 2.1 The 135 register items, re-extracted mechanically

Extracted from the register's item rows by pattern, not transcribed:

```
grep -oE '^\| `[A-Z]{2}-[0-9]+`.*\*\*(CLOSED|GOVERNED|OPEN|BLOCKED)\*\* \|$' \
  UCOS-OMEGA-INFINITY-100-PERCENT-CLOSURE-MASTER-REGISTER.md
→ 135 rows · 135 unique IDs · 0 duplicates
   14 BLOCKED · 41 CLOSED · 27 GOVERNED · 53 OPEN
```

This reconciles exactly with the register's own §19.1 rollup. The 17 ID prefixes and their counts: `AR` 6 · `AS` 14 · `CP` 5 · `CX` 7 · `EX` 11 · `GV` 6 · `ID` 8 · `IE` 10 · `IM` 7 · `IN` 12 · `ME` 8 · `MU` 7 · `PL` 7 · `RL` 7 · `RQ` 5 · `SC` 7 · `VF` 8.

**41 items are already `CLOSED` and are not scheduled.** They are carried in the graph as satisfied predecessors only. The remaining **94** are the schedulable population.

### 2.2 A referenced node with no defining row

The register cites `AU-01` twice — at `:354` (`MU-06`, *"No cross-class owner — see `AU-01`"*) and at `:453` (the leverage list, *"Cross-class transaction vesting | `AU-01`, `AS-01`, …"*) — and **defines it nowhere**. No `AU-` series exists in any of its 20 sections, and the ID appears in no other corpus file with that meaning. The tracked identifiers for that gap are `AT-1` (no declared authority owns a cross-class transaction boundary) and `AT-2` (an unresolved `constitutional-authority-alignment.json` delta), both from the H-06 transaction chain. A homonym `AU-01` exists at `02-MASTER/UCOS-Ω∞-IMPLEMENTATION-GOVERNANCE-BASELINE.md:173` and is an unrelated audit principle.

**Disposition:** this graph resolves the register's `AU-01` citations to `AT-1`/`AT-2` and registers the dangling reference as conflict `C-6`. It does not create an `AU-01` node, because creating a node to satisfy a citation would manufacture the population the citation was supposed to describe.

### 2.3 The 135 items have never been sequenced — verified, not assumed

The directive instructs that ordering be derived rather than assumed. The first thing to establish is whether an ordering already exists to inherit. It does not.

Grepping the register's item IDs across every `*.md` in the repository returns **exactly one file** for each — the master register itself. The `EX-*/IE-*/ID-*/CX-*/RL-*/AS-*/IN-*/SC-*/IM-*/CP-*/ME-*/RQ-*/GV-*/VF-*/AR-*/MU-*/PL-*` namespace exists nowhere else, including in the companion `UCOS-OMEGA-INFINITY-100-PERCENT-CLOSURE-ROADMAP.md`, whose execution-order table sequences nine `REQ-NN` requirements — a different population.

Five ordering systems do exist, over five different populations:

| System | Population | Structure |
|---|---|---|
| `UCOS-OMEGA-INFINITY-GAP-CLOSURE-SEQUENCING-DETERMINATION.md` | 19 findings `G-01`…`G-19` + `PA-G-04` | 9 waves, hard-prerequisite arrows, 12 live re-measurements, falsifiability clause |
| `…IMPLEMENTATION-ADMISSION-READINESS-DETERMINATION.md` | 28 items `R-1`…`R-20`, `T-1`…`T-5`, `H-1`…`H-3` | 4 independent roots; 10 READY, 5 conditional, 10 BLOCKED, 3 HOLD |
| `…ADMISSION-BLOCKER-CLOSURE-PREPARATION-DETERMINATION.md` | 6 blockers `B-1`…`B-6` | 4 roots + 1 derived + 1 unvestable; cost-ordered `B-6` sub-sequence |
| `CANONICAL-IMPLEMENTATION-DEPENDENCY-GRAPH-DETERMINATION.md` | 10 OPEN-GAP requirements | 5 tiers, 6 phases, **70-week calendar** (see `C-4`) |
| `03/04/05/07-…` (`IMG-001` quartet) | 90 unrealized CKOs at superseded baseline `ab78f35` | 5 constitutional layer-waves + additive pre-wave `W0-A` |

The register's 135 items are a **sixth population with no ordering at all.** Its nearest ordering-adjacent content, §19.4 *"the five things that would move the number most"*, is a leverage list: it has no arrows and states no prerequisites.

`MP2-C-05` already names this class of problem — four coexisting wave surfaces with four different units — and its remediation `P-7` is *"declare each wave surface's unit, or converge them onto one."* This determination adds a fifth surface and therefore **declares its unit** in §2.4, as `P-7` requires.

### 2.4 Unit declaration (`P-7` compliance)

> **Unit of this wave surface: ordinal dependency depth, measured in edges of this graph.**
> A wave index is the length of the longest admitted path terminating in that wave. It is not time, not effort, not points, not personnel, not calendar, and not priority. Two waves with adjacent indices carry no implication about relative size. Wave membership is a function of measured state and is recomputable; it is not a partition of fixed content.

---

## SECTION 3 — MEASURED BASELINE

Every figure below was produced by execution in this session, not read from a prior document. Commands and outputs are given so the derivation is falsifiable.

### 3.1 Repository state

```
git log --oneline -1   → bae59755 POST-CERTIFICATION: Code formatting cleanup (Phase 1B and Phase 2)
git branch --show-current → integration/recovery-001
git status --porcelain | wc -l → 76
```

76 dirty paths. This matters to the graph rather than being incidental colour: `evolution-replay` and the registration gate compare **committed** bytes, so a dirty tree is not a satisfied precondition for either.

### 3.2 Canonical ownership — re-measured

```
.ec1-venv/bin/python -m platform.universal_ownership.cli homing
  subjects:   549      declared:   151      contested:  0
  unresolved: 398      remediable: 195      coverage:   27.5046%
     186  EVIDENCE-NOT-IN-CANONICAL-HOME-ZONE
     212  NO-OWNERSHIP-EVIDENCE
       2  DIAGNOSED  LOCATOR-FORM-NOT-ADMITTED
      45  DIAGNOSED  LOCATOR-NOT-REGISTERED
     195  DIAGNOSED  ZONE-NOT-CANONICAL-HOME-ELIGIBLE
```

Identical to the register's figure. The register also records the trend: subjects rose 542 → 549 while declared owners stayed at 151, so coverage fell from 27.86% to 27.5046%. **Subjects enter faster than owners are declared.** This is the one measurement in the corpus that is moving in the wrong direction, and it produces a graph property, not merely a concern (§4.2).

### 3.3 The failing canonical validation stages — three of four re-executed

| Stage | Command | Exit | Measured output |
|---|---|---|---|
| `universal-object-governance` | `python 00-MASTER/UCOS-UGA-001/uga_engine.py gate` | **1** | `ANONYMOUS OBJECTS: 43 — run uga_engine.py run` / `GATE FAILED — 2 blocking invariant(s).` Blocking invariants are **`UGA-INV-01` and `UGA-INV-10`**, not all ten |
| `evolution-replay` | `python -m engine.uaue.gate --replay --quiet` | **1** | `REPLAY DRIFT — the committed history projection is not the product of the declaration (1316175 bytes committed, 1316175 bytes projected)`; plus `13-EVOLUTION-HISTORY-REGISTER.md` (1611/1611). Byte counts identical on both sides — **content drift at equal length** |
| `infinite-scope` | `python -m engine.infinite_scope.gate --quiet` | **1** | `laws measured / refused : 11 / 1`; `ISD-L-07` reported `[FAIL]`; `preserved freeze sites : 16`; `GATE CLOSED — 1 law(s) refused.` The two undeclared sites carry **3 occurrences between them** (2 + 1), not 2. The law's title is deliberately **not** reproduced here — see §13.2 |
| `pytest` | not executed here (long-running) | — | Coverage over the committed `.coverage` is **97%**, above the `--cov-fail-under=90` floor. The failure is **test failures** (23 node ids in `.pytest_cache`), not coverage |

Two corrections to the register's own summary follow from this and are registered as `C-5`: the failing stage is not a coverage breach, and the `ISD-L-07` count is three occurrences across two files. Both corrections make the work slightly *larger*, not smaller, which is why they are recorded rather than smoothed.

The two files that fail `ISD-L-07` are themselves Ω∞ determination documents. That fact has a consequence for this document, disclosed in §13.2.

### 3.4 Substrate measurements bearing on the evolution fabric

| Measurement | Command / path | Result |
|---|---|---|
| Declared CEU forms matching substrate terms | `engine/ceu/catalog.py` | Only `("dependency", "DEP", …, ("relationship","governance"))` at `:82` and `("architecture","ARCH", …, ("existence","evolution"))` at `:111`. **No form for software, library, framework, language, model, version or package** |
| Runtime dependency surface | `pyproject.toml:19` | `dependencies = []` |
| Language requirement | `pyproject.toml:15` | `requires-python = ">=3.12"` — a floor with no ceiling |
| Update / vulnerability automation | `.github/` | Contains **only** `workflows/`. No Dependabot, no renovate, no pip-audit, no SBOM, no lockfile |

---

## SECTION 4 — THE TWO UNIVERSAL IN-EDGES

Most edges in this graph are local. Two are universal, and they are of different kinds — a distinction the register's leverage list does not draw, and which changes the sequence materially.

### 4.1 Baseline → the *certification property* of every node (kind E3)

The register states it at `:55`: *"no item can reach certification evidence while the canonical gate exits non-zero."* This is mechanism, not policy. `verify.sh` records both PASS and FAIL into the evidence registry via `engine.verification_intelligence record`, and evidence keys are computed over stage id, label, argv and the content hashes of the stage's declared read prefixes (`engine/verification_intelligence/evidence.py`, `EVIDENCE_VERSION = "2.0"`). On a red baseline, a closure action's effect cannot be distinguished from the pre-existing failure, so the run produces no admissible evidence for it.

Two refinements the register does not make, both derived from `evidence.py`:

- The evidence store is a **cache, not a source of truth** — deleting it changes no verdict. So "green baseline" is a precondition for *producing* evidence, not for *holding* it.
- `decide()` refuses reuse outright for certification-eligible modes (`integration`, `full`). Certification therefore always re-executes. A wave whose exit criterion is certification cannot be discharged by a cached PASS.

**Consequence for the graph:** this edge lands on the *certification property* of all 135 nodes, not on their implementation. Implementation work on a red baseline is permissible and often necessary; only its certification is unreachable. Conflating the two would serialize the entire programme behind one wave, and the evidence does not support that.

### 4.2 Ownership → the *ownership property* of every node (kind E1)

The register's closure definition requires eight properties per item, of which canonical ownership is one. With coverage at 27.5046%, **no item touching an unowned subject can reach `CLOSED`**, whatever its implementation state. The register's §0.1 observes that measured closure (30.4%) and ownership coverage (27.5%) sit close together and that the proximity is not coincidence.

Again the edge is to a *property*, not to the work. And again there is a refinement: `OWN-REQ-002` (`UCOD-001:45`) is `EXACTLY-ONE-OWNER` — *at most one canonical owner per subject; multiple survivors are a contest, never a merge*. So ownership resolution cannot be parallelized by assigning provisional co-owners and reconciling later. Each of the 398 unresolved subjects needs one declaration, and `contested: 0` must be preserved.

**The trend produces a structural requirement, not just urgency.** Because subjects enter faster than owners are declared, a wave that resolves 195 remediable subjects without also making owner declaration a condition of subject entry will be overtaken. The graph therefore admits an edge from *"owner declaration is a condition of subject entry"* to the durability of every ownership gain — an `E3` edge, since it is arithmetic rather than preference.

---

## SECTION 5 — THE AUTHORITY CEILING AND THE VEST-ONLY CLASS

Some nodes are not reachable by work. Recognizing this is a graph property, not an excuse, and misclassifying them as backlog would misrepresent them — a caution the corpus states directly (`UCOS-OMEGA-INFINITY-GAP-CLOSURE-SEQUENCING-DETERMINATION.md:349`): *"Reserved decisions are therefore owner decisions awaiting a person, not repository work awaiting a process."*

### 5.1 The measured ceiling

| Condition | Evidence | Effect on the graph |
|---|---|---|
| Tier T1 is vacant | `00-CMG/CMG-REGISTRY.json:255` — `{"id":"T1","name":"Constitutional Authority","occupancy":"VACANT","vacancy":"VAC-01"}`; the declared superior *"exists in the repository only as frozen non-normative source material under `00-SOURCE/CONSTITUTIONS/` (.docx)"* | No wave may name a T1 ratifier |
| Every determination depending on T1 is provisional | `VAC-01.provisional_consequence` — *"including the standing of `CMG-000001` itself"* | Certification verdicts inherit `PROVISIONAL` |
| Maximum attainable verdict | `UCCEP-F-004` — *"Maximum attainable verdict anywhere in this repository is `CERTIFIED-PROVISIONAL`"* | No wave may declare an unqualified certification as its exit criterion |
| No competent ratifier | `MP2-C-04`, resting on three located instruments: `UCAF-RC-01` (`uccep-bindings.json`), `UCAF-RC-02` (`CMG-REGISTRY.json`), `UCAF-RC-03` (`00-CMG/README.md`); classified `UCAF-F-002` `STANDING-CONSTITUTIONAL-CONFLICT`, with `UCAF-F-003`: competence to ratify is *"not closable by measurement"* | `PL-07` is VEST-ONLY |
| Constituting T1 is not an in-repository act | `OA-6` — *"Constitute a Tier T1 authority competent to ratify | external constituent act | NOT ACTIONABLE IN-REPOSITORY"*; `CMG-OQ-01` remains OPEN | Four corpus-level conditions are VEST-ONLY |

### 5.2 Which authorities may actually be cited

This distinction is load-bearing for the sequence plan's *Required authority* column, and it is not the distinction the register's owner column makes.

**Registered in `00-CMG/CMG-REGISTRY.json` with a tier and a lifecycle state** — these may be cited as authority: `CMG-000001` (T1M, `DECLARED`), `CEP-000`…`CEP-010` including `CEP-002` (governance, `PROVISIONAL`), `CEP-003` (execution, `PROVISIONAL`), `CEP-007` (freeze, `PROVISIONAL`); `AUTH-INF-001`, `STATUS-001`, `REG-AUTO-001`, `UCI-001`, `GOV-INT-001`, `TECH-CONST-001`, `UCKP-LAW-0001` (T4, `engine/uckp/law.py`), `CONST-01`…`CONST-11`, the seven domain constitutions, `UCOS-BOOK-000000`, `CAT-000`, `REF-000`. Delegations route the concern: `CMG-DLG-02` → `CEP-002` (jurisdiction, ownership assignment, conflict resolution); `CMG-DLG-03` → `CEP-003` (execution and sequencing); `CMG-DLG-07` → `CEP-007` (freeze, supersession); `CMG-DLG-13` → `REG-AUTO-001` (registration, identity allocation, classification); `CMG-DLG-50` → `UCKP-LAW-0001`.

**Not in that registry** — these are programmes with a self-declared home and, in their own words, `authority: NONE`: `UCOS-CEU-001`, `UAUE-000001`, `UCXI-000001`, `UISD-000001`, `UVI-000001`, `UCOS-UGA-001`, `UCDA-000001`, `MCOS-000001`, `UCCEP-000000`, `UCOS-MXR-001`, `URRC-000001`, `UCOS-UTCE-001`, `UCIC-001`, `UCRD-001`, `UMB-IMP-001`. They are valid as **owner or executor**, never as **ratifier**.

**Cited but registered nowhere:** `ARCH-SECURITY-001`. It appears only in derived architecture data and in the register's leverage list as the authority that must answer the security enforce-versus-record question. A wave depending on it depends on an authority that must first be located or the decision routed to `CEP-002`. This is registered as an edge precondition in §6.6, not silently assumed away.

**`UCKP-ART-07`** is an article inside the registered `UCKP-LAW-0001`, not an authority in itself. The register uses it as an owner label for seven items; that usage is fine as ownership and wrong as authority.

### 5.3 The VEST-ONLY population

| Node | Discharge mechanism | Why work cannot reach it |
|---|---|---|
| `PL-07` plan ratification | External constituent act | Three located instruments record no competent ratifier; a correct `mip.json` would still be unratifiable |
| `VAC-01` T1 occupancy | External constituent act (`OA-6`) | Promotion of a lower instrument is forbidden (`CMG-000001` XVII.4; LXXXI.5 voids any reading that permits it) |
| `CMG-OQ-01` | Ratification | Open question referred, not resolvable by measurement |
| Unqualified certification | — | Ceiling is `CERTIFIED-PROVISIONAL` (`UCCEP-F-004`) |
| `AR-05` corpus scope (`H-03`) | Reserved human decision | `CONFLICT-04`: the certified corpus holds **0 `.py` files** across 1,233 artifacts with `executions: 0`; admitting code is a scope decision, not a registration task |

`AR-05` is the one hybrid: the decision is reserved, but the work that would follow it is ordinary. It is scheduled as decision-gated rather than vest-only, with the decision named.

---

## SECTION 6 — THE EDGE REGISTER

Each edge carries its source kind and its evidence. This is the graph.

### 6.1 Mutation permissibility precedes everything mutating (E3)

| Edge | Evidence |
|---|---|
| `MU-01` → every node whose closure involves a mutation | `mc.classify` returns `ERROR`, not `CLASSIFIED`, for a real subject (`engine/nucleus/lifecycle.py`). The measured cause is upstream of precedence: rule coverage is evaluated at `classify:427-436` **before** the precedence loop, and `validate_rule_coverage` returns *"rule 'R-09' is declared but no predicate implements it"* with `RULE_PREDICATES` holding R-01…R-08 — 8 of 9. **The classification outage is total, not partial.** While it stands, no mutation made in closing any other gap can be shown to have been permitted |
| `MU-01` → `MU-03` | Contradicts the intuitive reading that gate purity comes first. `G-01` (an implementation gap, ranked last of seven by priority class) is unavoidably first by dependency; `G-11` (`gate_mode`) is Wave 1 downstream of it. Declaring a mode is a mutation, and its permissibility is exactly what the classifier answers |
| `MU-01` → `MU-02` | `MU-02`'s chain (mutation → authority → evidence → execution → verification → certification) cannot be measured end-to-end while its first link returns `ERROR` |

**The bootstrap paradox, and its located disposition.** The mutation-classification plane cannot authorize its own repair. The corpus tables three options and finds one sound: repair under `UCKP-LAW-0001`, which is upstream and unaffected, then classify the repair's own changed paths as the first act after — *"self-disclosing rather than self-authorizing."* A second caution applies: `P0-DECLARATION-001` places `platform/repository_intelligence` outside `UFC-14/15/16` entirely, so the repair's governance route is not the one its file path suggests.

### 6.2 Baseline admissibility (E3)

| Edge | Evidence |
|---|---|
| `{AR-01, ME-01, ME-06, VF-06, EX-11, VF-08}` → certification property of all 135 | §4.1 |
| `VF-06` before `AR-01` before `ME-06` before `VF-08`-residual | Cost order derived in `…ADMISSION-BLOCKER-CLOSURE-PREPARATION-DETERMINATION.md` §7.5: `B-6c` `ISD-L-07` disclosure needs no authority beyond document owners; `B-6a` 43 mints needs a new `CEP-002` Article 28 decision; `B-6b` UAUE render needs the UAUE owner **and the delta captured before rendering**; `B-6d` WIP tests needs the owner of the modified files. This is the one place cost legitimately orders, because all four are independent and the order minimizes irreversible acts taken under uncertainty |
| Baseline → `ID-01` | The validated six-digit fix cannot be applied first. `id_shape` flows into the universe digest via `alignment.py:514`, and the replay stage already fails on drift, so the change would be unverifiable on a red baseline. The fix itself is measured sound: `{6,}` matches 6,185 of 6,187 ledger ids — identical to `{6}` — while admitting the 10⁶-th identifier |
| Baseline → `IE-09` and every other code-level closure | Same mechanism as §4.1 |

**A hazard specific to this wave.** `AR-01`'s remedy is `uga_engine.py run`, which mints 43 identifiers. The register records that this exact command *"minted 43 while observation was intended"* during its own session, and the corpus records a prior incident of 140 identifiers minted by a drift check and 11 tracked files written by a single `--gate` probe. So the cheapest path through Wave 1 runs through the precise mechanism Wave 4 exists to govern. That is not a contradiction, but it is the reason Wave 1's mints require a decision rather than an invocation.

### 6.3 Vocabulary coercion symmetry (E1)

| Edge | Evidence |
|---|---|
| `RL-02` → `VF-05` | `VF-05`'s row states openness is unproven *at the consuming layer*; `RL-02` is that layer. `RELATION_TYPE_VOCABULARY` (`vocabulary.py:282`) admits a new type; `RelationType(str, Enum)`'s 17 members and its raising `coerce()` (`knowledge/model.py:186-212`) reject it. A newly registered type passes the cross-check and fails coercion |
| `RL-02` → `IE-07`, `RL-07` | Both rows resolve their gap to `RL-02` explicitly (`IE-07`: *"See `RL-02`"*; `RL-07`: *"Blocked in practice by `RL-02` at the consuming layer"*) |
| `RL-02` → `RL-01` | `RL-01`'s closure criterion is one model carrying identity, owner, validity and history, or a declared crosswalk; a crosswalk across a type system whose coercer rejects registered members is not expressible |
| `CX-05` independent of `RL-02` | Same defect **shape** — openness at the registration surface, closure at the coercion surface (`taxonomy.py:42,82,516`) — at an unrelated site. Shape similarity is not an edge (§1.2) |
| `RL-02` **not** in the `uisd-declaration.json` disclosure register | The register notes this. So `RL-02` is simultaneously a coercion defect and an undisclosed closure, which places one leg of it in the disclosure wave |

### 6.4 Disclosure as closure (E1)

For a specific set of nodes the register's own closure criterion is disclosure, not capability: *"`ID-02`…`ID-05` entered in the assumption register (disclosure **is** the closure for these)."* The operative discipline is `contract.py:16-20` — `ISD-L-01` never fails a closed enumeration; it fails a *disclosure record*. Each disclosure needs a non-empty `closing_invariant`, a non-empty `admission` path, an existing `declared_at`, and either `intentional: true` or a named gap.

| Edge | Evidence |
|---|---|
| `VF-07` → the durability of every disclosure | `AD-G-01` (`ARCHITECTURAL-ASSUMPTION-DETECTION-DESIGN-ANALYSIS.md:72`, CONFIRMED, *"the single largest gap"*): detection is declaration-bound, not discovery-bound. `ISD-L-01` and `ISD-L-10` audit only the 11 closures the declaration already lists; nothing sweeps for an undeclared `Enum`, `frozenset` or literal tuple. A closure added tomorrow is invisible until a human discloses it — *"which inverts the intended direction of a detector."* Until `VF-07` lands, disclosure completeness cannot be asserted, only claimed |
| `VF-07` must land as disclosures, not failures | The same source: risk *"High — will find many; must land with disclosures, not with failures."* An `E3` edge from the sweep to its own disclosure batch |
| `ISD-G-09` constrains the disclosure act | `engine/tests/unit/test_infinite_scope.py` asserts `len(unintentional) == 1` over the live declaration. Disclosing a newly located closure therefore requires an engine-plane change even though the disclosure itself is data. Disclosure is cheap; it is not free |
| `IE-09` is a disclosure-or-generalise fork | `_CURRENCY_PATTERN = ^[A-Z]{3}$` enforced in `Money.__post_init__` (`contracts.py:53,165`) while `"currency"` sits in the kernel's `PROHIBITED_TOKENS`. A direct kernel contradiction, load-bearing across 6 modules. The closure criterion admits either generalising the pattern or declaring the bound — an owner's choice, recorded as a fork rather than resolved here |

### 6.5 Gate mode declaration (E2)

| Edge | Evidence |
|---|---|
| `MU-01` → `MU-03` | §6.1 |
| `MU-03` → `MU-04`, `MU-05` | `MU-04` universalises the `UGA-001` precedent (`run` mints and emits; `gate` verifies and mutates nothing; `stats` prints) from one engine to the rest; `MU-05` applies the proven injection technique — injecting `ucos_ensure_venv` fails `test_verify_does_not_ensure_the_environment_it_is_verifying:826`; injecting a bare tool fails `test_no_bare_tool_is_ever_in_command_position:887` — from one gate to the others. Neither is expressible before the mode field exists |
| `MU-03` → `GV-06` | `MI-10`: `GV-06`'s gate registry is hand-declared data. I verified this mechanically: `uccep-bindings.json` binds **26 gates and 48 checks**, each check carrying `id`, `name`, `owner`, `argv`, `write_scope`, `tier`, `fail_closed`, `advisory`, `exit_semantics` — and **no `mode` field on any gate or check**. What exists instead is `tier` (`boot` 25 · `standard` 19 · `full` 4). No code reads `.github/workflows/` to discover gates; a new workflow does not enter UCCEP automatically |
| `R-4` correction → `P-3` selection → the whole wave | The authority chain is measurably gated. `H-06-IADR-UPDATED` §8 is **signed** (entry `S-1`, 2026-08-16T20:10:00+05:30, package sha256 `22ce5142…`) and authorizes the §4 scope only. Its §8.1 Phase-0 table stands at **2 of 6**: `0.1` PASS; `0.2` P-3 unselected and *"blocked until R-4 is corrected per §3.2"*; `0.3` PASS; `0.4` unmeasured owner act; `0.5` `verify.sh` baseline never captured; `0.6` unrelated deltas not isolated. *"No phase begins until all six pass"* |
| The field name is settled | `H-06-R3` surveyed all 11 `*-declaration.json` and found no `gate_mode`, `execution_mode`, `mutation_mode` or semantic equivalent; verdict *"`gate_mode` ACCEPTABLE"*, `R-3 RESOLVED`, duplication risk none. `R-1`, `R-2` also RESOLVED; **`R-4` remains OPEN** and is the live blocker |
| A guard precedes any declaration | `H-06-IADR-UPDATED:211`: *"No mode may be declared on a surface whose owning engine carries no `--check-declaration`."* An `E3` edge inside the wave |
| The wave does not close gate purity | `H-06-IADR-UPDATED:363`: *"Executing the full authorized scope does not close gate purity."* `GP-1`, `GP-3`, `GP-11` terminate OPEN (residual). The wave's exit criterion must therefore be *mode declared and honoured*, not *purity closed* |

### 6.6 Admission-path composition (E2 + E3, with one registered conflict)

| Edge | Evidence |
|---|---|
| `MU-03` → `{SC-01, AS-08, IM-04}` | Structural, not preferential: *"Composing machinery into the admission path means running more machinery during admission. While ≥24 gate paths mutate undeclared, adding machinery to admission adds mutation to admission."* The demonstration is empirical — a diagnostic invocation minted 43 permanent identifiers |
| `GV-01` → `{SC-01, AS-08, IM-04}` | `A-3` gates every condition of the composition step; the security rollup cannot attribute a finding to an unowned subject |
| `ARCH-SECURITY-001` enforce-versus-record → `SC-01` | The register names this authority for the decision; §5.2 finds it registered nowhere. The edge's precondition is therefore *locate the authority or route the decision to `CEP-002`* |
| `MI-3` → `AS-06` via `MI-9` | `MI-9`: the fabric creates no relationships — `AssimilationRecord` names a destination and an owner, never an edge, so an assimilated object participates in nothing. Blocked on `MI-3`, because edges need resolvable endpoints. `MI-3` is an owner decision, and its substance is `ID-07`'s four disjoint mints |
| `ID-07` → `AS-04` | Same substance: allocating counter, 12-hex, UUID5/URN, and `content_hash[:16]`. The register is precise about why this is hard — allocated-versus-derived is *"a **philosophy** conflict, not a format one"*, and `CAA-INV-04` reports PASS at 5,874 because the invariant as written does not detect the split |
| `AS-14` — **conflict `C-1`** | The register calls it *"the cheapest closure in this scope; **not** blocked on authority."* `MI-10` routes the same finding as REGISTER, *blocked on the gate-purity mode decision `H-06`/`CR-09`*. Both are located; they disagree. Registered, not silently resolved; the conservative arc is taken and the permissive reading is recorded as falsifiable |
| `AS-09`, `IM-01` — **conflict `C-2`** | `MI-5` routes impact wiring as *"WIRE, no blocker"* and one of four mutually independent unblocked items. The register's leverage list groups `AS-09` and `IM-01` with the three security COMPOSE items behind gate purity. Same disagreement shape as `C-1`; same disposition |

### 6.7 Durability and lineage (E1 + E2)

| Edge | Evidence |
|---|---|
| `IN-11` → `IN-09` via `MI-1` | `MI-1` is the keystone: assimilation does not append to the evolution ledger. Article 14 stage 14 is `KNOWLEDGE_ASSIMILATION`; `EvolutionLedger` has one consumer (`engine/uaue/`) which never sees a fabric output. `MI-1` is *"blocked in part on `F-3`"*, and `F-3` is **narrower than first stated**: `to_document`/`from_document` exist and `engine/uaue/history.py` rehydrates through them. What is absent is a **production writer** — only a test writes the history file, to `tmp_path`. Missing writer, not missing serialization |
| `CX-03` → `RL-03`, `CX-04` | `RelationDeclaration.from_dict()` fail-closes on non-null validity because `TemporalCoordinate` has **no `from_dict`** — measured absent as `M-8`. Temporal context is construction-only, not deserializable, so validity and history cannot round-trip |
| `EX-03` is independent | `AuditEntry` omits the successor list, so `supersede → resurrect → supersede` is not reconstructible from the journal alone. A field-level widening, coupled to nothing else |
| `ME-05` is a sharing decision, not a capability | The evidence store is populated — 8 stage directories exist (`autonomous-evolution`, `evolution-replay`, `governance-pre`, `meta-constitutional`, `object-birth`, `registry-validate`, `ruff`, `verification-intelligence`), exactly the reusable stages, holding 44 PASS and 2 FAIL entries — and `.gitignore:222` excludes the path. Evidence is local, not shared. Given §4.1's finding that the store is a cache, the closure is a declaration of intent, not a persistence build |
| `ME-08` is independent | `engine/runtime` serialises to a string only — no file write, no path, no store. Cross-process replay of a real run has no on-disk input |
| `AR-02` is independent | 1,461 eligible · 1,233 registered · **228 unregistered** · 55 awaiting VCS binding |
| `AR-05` is decision-gated | `CONFLICT-04`, reserved as `H-03` (§5.3) |
| `MU-07` bounded by `ORL-15` | Rollback reverses completed universes in reverse dependency order using the recorded topological order verbatim, but *reverses records, not live effects*. `ORL-15` (`08-RUNTIME/RUNTIME-013:322`) forbids introducing an engine, scheduler, automation platform or executor. So the closure criterion cannot be *"roll back live effects"* — that would violate a located law. It must be a declared bound |

### 6.8 Cross-class transaction (E2)

The H-06 chain reaches a determination that changes the shape of this part of the graph, and the register's leverage list does not reflect it.

| Finding | Evidence |
|---|---|
| The category does not constitutionally exist | *"A cross-class transaction is not a constitutionally existing category."* `UCKP-ART-02`: *"Nothing exists constitutionally until it has become one."* Zero `atomic`/`transaction` tokens in `law.py` or the mutation-governance boundary artifact |
| All four candidate carriers rejected | `EvolutionRecord`/`EvolutionLedger` *cannot represent*; `change_event` *cannot represent, and its `commit` field is a trap*; `UAUE-000001` *cannot represent* — it is a measurement plane holding no authority, and it is *the cause* of the transaction under analysis; `ART-12` state transition — *right shape, wrong domain* |
| **A new authority is rejected** | The terminal determination selects **C — transaction orchestration capability under an existing framework**, with A as embedded precondition and **B (new authority) rejected on measured grounds**. It names the inference error directly: *"an invalid inference from 'no authority covers this' to 'a new authority is required.'"* The operative maxim: *"There is no transaction authority. Transaction orchestration holds no authority at all"* — role `EXECUTION` under `UCKP-ART-10`, `may_hold_authority: false` |
| It corrects its own predecessor | The earlier determination's step *"Designate its authority, scoped to sequencing only"* is *"unexecutable as written, twice over"* — no authority may be designated, and sequencing is already owned by `CEP-003` and delegated by `CMG-DLG-03` |
| Eight owner decisions gate it | `D-1` adopt disposition C2 (else `AT-1` stays OPEN and Phase 0 stays at 4 of 6) · `D-2` governed category (`GOVERNED_CATEGORIES` has 35 members, **no `transaction`**) · `D-3` repository serial prefix (`ukb.py` only, `CAA-INV-04`) · `D-4` which of the 33 closed facets carries the ordered path · `D-5` **prospective-only binding, else a bootstrap deadlock — *"the capability cannot lawfully be created by the act that creates it"*** · `D-6` ledger shape · `D-7` sequence of the four closure acts · `D-8` `AT-2` disposition. All eight OPEN; none opened as a record |
| `AIF-L14` bounds what exists today | `platform/foundation/admission.py:217` gives sealed admission plus projection re-verify, or abort leaving no orphan identity — **single-class only**. `AIF-L14` has no prose definition in the corpus; it is referenced as an existing law in `UIS-001` declarations and `IMR-003A` |

**Graph consequence:** this is not a *vesting* wave, contrary to the register's framing (*"an authority spanning 7 programmes — none exists"*). It is a **decision-then-capability** wave: the eight decisions precede a capability that explicitly holds no authority. `D-5`'s prospective-only binding is a hard internal edge — without it, the wave cannot lawfully perform its own first act.

### 6.9 Plan operand and requirement entity (E2)

| Edge | Evidence |
|---|---|
| `PL-01` → `{PL-02, PL-03, PL-04}` | `MP2-C-01`, CONFIRMED: *"No machine-readable plan state. `LAW P50-002` requires completion be measured; with prose-only success criteria there is nothing to measure over. Every arrow in the target chain presumes a measurable predecessor, so this blocks the whole model."* Its remediation `P-1` is the one item stated as *"unconditionally first"* — within its own chain. `mip.json` is re-verified absent. The register's disposition is precise: **derive and register, never amend** |
| `PL-01` → `PL-02` specifically | The sequencing engine already computes Kahn topological sort, cycle detection and effort-weighted critical path twice (in-corpus and ratification chain) — and **the MIP is not among its 8 `SRC` inputs**. The closure is wiring an existing engine to a derived operand, not building a planner |
| `PL-01` → `RQ-03` | `MP2-C-01`; the requirement → plan edge is absent in both directions |
| `RQ-01`/`EX-05` → `RQ-02` | The evolution vocabulary (creation, modification, refinement, merging, supersession, deprecation, reactivation, splitting) is **inert**: no writer, no link field, no gate. `SUPERSEDED`/`DEPRECATED` exist in a vocabulary nothing consumes. A writer needs an entity to write about, and requirement is not a declared CEU form |
| `PL-01` → `EX-09` | Plan-as-entity has no operand while `mip.json` is absent |
| `PL-07` is VEST-ONLY | §5.3. This is the one place where the register and this graph agree exactly |

### 6.10 Authority-plane reconciliation (E1)

`GV-03` is the deepest of the governance nodes and the register understates it. `D-2.1` (`CANONICAL-AUTHORITY-DETERMINATION.md:26`) states: *"the Canonical Ownership Principle is declared in one place and enforced in another, and the two do not share a key. **This is the root of every conflict in §5**"* — the ten registered `CONFLICT-01`…`CONFLICT-10`. The register's note that `contested: 0` *"does not mean the planes agree"* is exactly right and is the reason this node sits with ownership rather than with governance disclosure: sharing a key is a precondition for ownership resolution being *checkable*, not merely *recorded*.

---

## SECTION 7 — THE ROOT SET

Nodes with in-degree zero under §6. Derived, not chosen.

| Root | Content | Authority required | Blocked by |
|---|---|---|---|
| **R-A** | `MU-01` — R-09 predicate, classifier consumes its extension | `UCKP-LAW-0001` for the upstream repair; mutation-governance owner accepts the self-disclosure | Nothing |
| **R-B** | `VF-06`/`EX-11` — `ISD-L-07` site disclosure | Document owners only | Nothing. Cheapest node in the graph |
| **R-C** | `AR-01`/`ME-01` — 43 mints; `ME-06` — UAUE render; `VF-08` residual — 23 tests, 76 dirty paths | New `CEP-002` Article 28 decision (`ADR-0017` declined a standing blanket mint: *"A future anonymous object requires its own decision under this same Article"*); UAUE owner; owners of the modified files | Nothing, but see the §6.2 hazard |
| **R-D** | `GV-01`/`CP-05`/`AS-07`/`GV-03` — ownership | Each subject's owner; `CEP-002` via `CMG-DLG-02` for assignment and conflict resolution | Nothing. Highest leverage |
| **R-E** | `RL-02`/`CX-05` — coercion symmetry | Module owners (`UCRD-001`, `UCXI-000001`) | Nothing for implementation; R-A for permissibility |
| **R-F** | `PL-01` — derive `mip.json` | MIP owner; `CEP-003` via `CMG-DLG-03` for sequencing | Nothing. Ratification is separate and vest-only |

Two further roots are **decision-only**, and sequencing them as work would misrepresent them: the `H-06`/`CR-09` mode policy including `R-4` correction and `P-3` selection, and the eight transaction decisions `D-1`…`D-8`.

**No single action discharges more than one root.** Three prior determinations reach this same conclusion over their own populations, by independent derivation. That convergence is the strongest available evidence that the root count is a property of the repository rather than of any one analysis.

---

## SECTION 8 — TWO DERIVED FINDINGS THE PRIOR ORDERINGS DO NOT CARRY

### 8.1 `DG-F-01` — Wave 0 and Wave 1 are entangled on certification, and the cycle is broken by disclosure

Stated as a cycle:

- Certifying anything requires a green baseline (§4.1).
- Reaching a green baseline requires mutations — 43 mints, a render, a disclosure batch, test repairs.
- Knowing those mutations were permitted requires the classifier (§6.1).
- Certifying the classifier repair requires a green baseline.

This is a genuine cycle in the *certification* relation, and it is not present in the *implementation* relation — which is why §4.1 insists the baseline edge lands on the certification property alone. The corpus already disposes of this shape: repair upstream under `UCKP-LAW-0001`, then classify the repair's own changed paths as the first act after — **self-disclosing rather than self-authorizing.**

The consequence for sequencing is concrete and slightly uncomfortable: **Wave 0 completes before Wave 1 but is certified after it.** A plan that requires each wave to be certified before the next begins cannot execute this graph at all. The sequence plan therefore separates *wave exit* from *wave certification* explicitly.

### 8.2 `DG-F-02` — authoring Ω∞ determinations is itself a measured mutation, with two effects that differ in timing

`ISD-L-07` scans root-depth-zero `.md` files among its roots (`.`, `00-CEP`, `00-CMG`, `99-FREEZE`, `engine`, `platform`) for nine permanence phrases and a status-field pattern, and **any found path not in `preserved_sites` is a violation** — a ratchet. The two files currently failing it are Ω∞ determination documents. Separately, `UGA-INV-10` flags root-level `.md` determination and report files carrying no identifier, and that population is the 43.

The two effects differ in **when** they land, and the difference is measured rather than assumed:

- **`ISD-L-07` triggers on creation.** The scan walks the filesystem, so an untracked file is inside its scope immediately. Writing a determination can therefore re-open the law in the same session — and it did, on this document's first draft (§13.2).
- **`UGA-INV-10` triggers on commit.** UGA's population is `git ls-files --cached`, so an untracked file is outside the artifact boundary entirely. The anonymous-object count does not move until the file is version-controlled.

This asymmetry is a scheduling fact, not a curiosity: it means Wave 1's two sub-items respond to different events, and the Article 28 population must be enumerated after commit rather than before (§13.2).

---

## SECTION 9 — UNIVERSAL EVOLUTION UPDATE FABRIC

The governing directive requires dependencies for the evolution of the system's own technical substrate. **That fabric does not exist.** No entity, registry, gate, law or determination governs it as a population. Absence is the finding, and it is disclosed rather than filled by assumption.

### 9.1 Measured state of the six classes

| Class | State | Evidence |
|---|---|---|
| **(a) software / dependency updates** | Disclosure only; no update mechanism | `ISD-L-09` *"Technology Is An Evolutionary State"* is the only substrate law. `check_technology_is_evolutionary_state` (`engine/infinite_scope/contract.py:473-514`) requires `[project].dependencies` empty, `requires-python` present without `<`/`<=`/`==`, and every `==` pin in optional-dependencies present in `declared_pins` with a reason, bidirectionally. It **never asks whether a pin is current, supported or vulnerable, and emits no upgrade candidate.** It passes today. Five dev pins are disclosed by hand |
| **(b) language evolution** | A ceiling is illegal; no migration path exists | `requires-python = ">=3.12"`. Declaration rationale: *"A floor admits every future version; a ceiling forbids one… An upper bound, or an exact pin, would encode 'Technology X forever'."* But duplicate hardcoded floors exist (`engine/determinism/hermetic.py:61-63`, `engine/context/catalog.py:135`), and the Fabric determination records language neutrality as **unmeasured** |
| **(c) framework evolution** | Absent | No framework entity, registry, gate or determination. *"UI frameworks | NO ASSUMPTION AND NO CAPABILITY"* — the UI artifact schema governs zero instances |
| **(d) library evolution** | Absent | No form, no nucleus, no registry, no candidate class |
| **(e) architecture evolution** | Governed but not caused | `architecture` **is** a declared CEU form carrying the evolution primitive (`catalog.py:111`). It is declared frozen at the nucleus level, and nothing unfreezes it — change is by supersession under `CEP-007` (IX/XI: *"freeze preserves, never blocks"*) or amendment under `CEP-009`, with `CEP-007` XIII.5/XV.4 asserting unbounded successive evolution. But *"evolve architecture — **DECLARED, NOT CAUSED**"*, resting on the located finding that *"nothing in the repository causes capability to increase"* |
| **(f) AI model evolution** | Refused as an engine; admissible only as assimilated external state | *"AI models | **REFUSED BY DESIGN**."* The refusal is reasoned, not evasive: *"a predictive engine would produce an impact estimate that could not be falsified"* (`engine/uaue/simulation.py:1-25`). The declared route is to *"assimilate an arbitrary prediction from an arbitrary future source and route it through verification — not by containing a forecaster."* No model registry exists in code; `USIS-REG-006 model` is one of six registries in a 36-markdown, zero-code directory (`MI-12`) |

**Disclosed, not undetected.** `ISD-G-07` records it: *"ISD-L-09 measures `pyproject.toml` pins only, so technology identity is unmeasured on every axis."* Under the `contract.py:16-20` discipline, that makes the absence a governed gap rather than a hidden assumption — which is precisely the distinction the directive's infinite-scope test turns on.

### 9.2 The keystone constraint, and why it is not a code problem

`engine/uaue/discovery.py:1-22` is explicit: discovery *"turns a condition another owner already measured into an evolution candidate. It does **not** inspect the working tree… It reads the sealed derived-truth artifacts that located owners publish."* Its nine declared sources are repository capability and governance conditions. `pyproject.toml` is not among them, and no filesystem walk occurs.

But `candidate_class` is **pure data**: *"The engine does not know what a subject is… a source added to the declaration tomorrow needs no code here."*

The derivation follows directly, and it inverts the obvious reading:

> A `DEPENDENCY_UPDATE`, `LANGUAGE_VERSION` or `MODEL_VERSION` candidate class requires **no engine code**. It requires that some located owner first **publish a sealed artifact measuring the substrate.** No such owner and no such artifact exists. The fabric's true prerequisite is a measuring owner, not an engine.

This is why the fabric is last in the graph and not merely large: it depends on ownership (§4.2) at a threshold, on identity (the weakest scope in the register), and on an entity form that does not exist.

### 9.3 Derived nodes

| Node | Content | Prerequisites (all E3 unless noted) |
|---|---|---|
| `UEUF-00` | A substrate entity form — the class of thing a version belongs to | `EX-06` technology as entity (OPEN, **no owner**); `declare_form()` admits it as data with a byte-identical kernel fingerprint, so this is registration, not construction |
| `UEUF-01` | A measuring owner publishing a sealed substrate artifact | `UEUF-00`; ownership threshold (`GV-01`); §9.2 |
| `UEUF-02` | Candidate-class declaration admitting substrate subjects | `UEUF-01`; declaration edit only, no engine change |
| `UEUF-03` | Vulnerability / currency data source for `(a)` | `UEUF-01`; `SC-07` (pins verified installed, no vulnerability data source — *pin integrity ≠ pin safety*); `SC-05` (no sanitization, no untrusted-content quarantine, and *"UAUE trusts its declaration substrate absolutely"*), because an external feed is untrusted input entering a substrate that has no defence against it |
| `UEUF-04` | Language-version evolution path for `(b)` | `UEUF-02`; reconcile the duplicate hardcoded floors; a migration determination, which does not exist |
| `UEUF-05` | Architecture evolution causation for `(e)` | The `CEP-007`/`CEP-009` path exists; what is absent is causation. Depends on the plan operand (`PL-01`) — a cause requires something that measures whether capability increased |
| `UEUF-06` | AI-model evolution as assimilated external state for `(f)` | The assimilation fabric: `AS-01` (14 admission surfaces, 2 mutually invisible planes, terminus `AssimilationReport` → coverage number → ∅), `AS-14` (no evidence key, no proof it ever ran), `MI-1`. All BLOCKED or OPEN. The forecaster route stays refused |
| `UEUF-07` | Framework and library classes for `(c)`/`(d)` | `UEUF-00`, `UEUF-02`. Currently vacuous: `dependencies = []` means there is no runtime surface, so these classes would govern an empty population until one exists — which is a reason to declare the form and defer the population, not to build machinery |

### 9.4 The seven prerequisite analyses, mapped and measured

The directive requires that identity, ownership, security, impact analysis, validation, rollback and lineage precede autonomous evolution. Each maps onto register nodes with a measured state:

| Prerequisite | Register nodes | Measured state | Verdict |
|---|---|---|---|
| **Identity** | `ID-01`…`ID-08`, `AR-01`, `ID-07` | **0 of 8 `CLOSED`** — the register's weakest scope. Four disjoint mints; four undisclosed finite constraints; 43 anonymous objects | **NOT SATISFIED** |
| **Ownership** | `GV-01`, `CP-05`, `AS-07`, `GV-03` | 151/549 = 27.5046%, falling; 398 unresolved, 195 remediable; declaration and enforcement planes share no key (`D-2.1`) | **NOT SATISFIED** |
| **Security** | `SC-01`, `SC-02`, `SC-05`, `SC-06`, `SC-07`, `AS-08` | 2 of 7 `CLOSED`. 13 modules / 6,512 LOC built, **architecturally non-enforcing**, **zero CI references**. No sanitization, no injection defence, no dependency scan, no secret scan, no SAST. `14-SECURITY/` = 5 md, 0 code | **NOT SATISFIED** |
| **Impact analysis** | `IM-01`…`IM-07`, `AS-09`, `IN-10` | 3 of 7 `CLOSED`. Blast radius, certified-surface disturbance, bounded 0–100 risk and severity band all exist and are CI-run — and are **unreachable from any admission path**. Nothing computes blast radius before admitting | **BUILT, NOT REACHABLE** |
| **Validation** | `VF-08`, `AS-10`, `AS-11` | 15 executable stages, self-verifying (UAUE obligation #9 measures its own wiring); **4 fail**; `verify.sh --full` exits 1 | **EXECUTABLE, RED** |
| **Rollback** | `MU-07`, `MU-06`, `AT-1`/`AT-2` | Reverses records in reverse dependency order, **not live effects** (bounded by `ORL-15`). Atomicity is single-class only (`AIF-L14`). No cross-class transaction category exists constitutionally | **NOT SATISFIED** |
| **Lineage** | `AR-03`, `RL-04`, `ME-01`…`ME-08`, `IN-11` | Strongest of the seven: 6 read-only sources → 1 in-memory projection, 12,899 edges, **0 dangling**, and composition computed on demand rather than stored. But it is a projection with **zero persistence**, and the evolution ledger has no production writer | **PARTIAL** |

**Derived conclusion:** all seven prerequisites are incomplete; two are built-but-unreachable rather than absent; the weakest is identity, at zero closed items of eight. Autonomous evolution over the substrate is therefore not gated on one missing capability but on the joint completion of seven, and the graph places it last on that basis rather than on judgement.

---

## SECTION 10 — WAVE PARTITION

Derived from §6. Every one of the 94 schedulable items appears exactly once; the 41 `CLOSED` items are carried as satisfied predecessors and are not scheduled. Full per-wave detail is in the companion sequence plan.

| Wave | Precondition discharged | Items | n |
|---|---|---|---|
| **0** | Mutation permissibility is knowable | `MU-01`, `MU-02` | 2 |
| **1** | Evidence is distinguishable from pre-existing failure | `VF-08`, `AR-01`, `ME-01`, `ME-06`, `VF-06`, `EX-11` | 6 |
| **2** | Finite constraints are disclosed rather than hidden | `ID-01`…`ID-06`, `ID-08`, `IE-03`, `IE-04`, `IE-05`, `IE-09`, `IE-10`, `EX-04`, `EX-08`, `EX-10`, `GV-04`, `IN-04`, `PL-05`, `AR-04`, `CP-02`, `VF-02`, `VF-07`, `CX-07`, `ME-04`, `ME-05` | 25 |
| **3** | The consuming layer accepts what the registering layer admits | `RL-02`, `CX-05`, `VF-05`, `IE-07`, `RL-01`, `RL-07` | 6 |
| **4** | Every check declares one mode and honours it | `MU-03`, `MU-04`, `MU-05`, `GV-06` | 4 |
| **5** | The ownership property becomes satisfiable | `GV-01`, `CP-05`, `AS-07`, `GV-03` | 4 |
| **6** | Admission computes before it accepts | `AS-05`, `AS-06`, `AS-09`, `AS-14`, `AS-08`, `IM-01`, `IM-04`, `IM-05`, `IM-07`, `SC-01`, `SC-02`, `SC-05`, `SC-06`, `SC-07` | 14 |
| **7** | Every history class is durable and reconstructible | `IN-11`, `ME-02`, `ME-07`, `ME-08`, `CX-03`, `CX-04`, `RL-03`, `EX-03`, `AR-02`, `AR-05`, `RL-06`, `MU-07`, `CP-03` | 13 |
| **8** | A mutation may span classes atomically | `AS-01`, `AS-04`, `ID-07`, `IN-09`, `IN-10`, `MU-06` | 6 |
| **9** | Completion is measurable over a plan operand | `PL-01`, `PL-02`, `PL-03`, `PL-04`, `RQ-01`, `RQ-02`, `RQ-03`, `RQ-04`, `EX-05`, `EX-09` | 10 |
| **10** | The substrate is an evolvable governed population | `EX-06`, `EX-07`, `IN-12` + `UEUF-00`…`UEUF-07` | 3 + 8 |
| **VEST** | Not reachable by work | `PL-07` + `VAC-01`, `CMG-OQ-01`, `OA-6`, unqualified certification | 1 + 4 |

Reconciliation: 2+6+25+6+4+4+14+13+6+10+3+1 = **94**, matching the 53 OPEN + 27 GOVERNED + 14 BLOCKED partition exactly.

**Parallelism.** Waves 2, 3, 5 and 9 have disjoint prerequisite sets and may proceed concurrently after Wave 0, subject to serialization notes where they share a file. Waves 4, 6, 7, 8 and 10 are chained. The graph is therefore **breadth-heavy early and depth-bound late**, and the binding constraint on total depth is the chain `0 → 4 → 6 → 7 → 8 → 10`, of depth 6.

---

## SECTION 11 — INFINITE SCOPE VALIDATION OF THIS MODEL

The directive requires that the dependency model itself introduce no fixed boundary. Each prohibition is tested against this document's actual content.

| Prohibition | This model | Test |
|---|---|---|
| **Fixed entity categories** | Node classes are three and disclosed with an admission path (§1.3). The item population is *measured*, not enumerated: a 136th closure item enters by the same edge-admission rule with no structural change | Add an item; re-derive; structure unchanged |
| **Fixed realities** | No node names a reality. Reality is a resolved context axis in the corpus (`IE-06`, `CX-02`), and this model inherits that rather than restating it | No reality token appears in any node or edge |
| **Fixed locations** | No node names a location, jurisdiction or frame. Where location matters it is cited as a resolved axis with a derivation path | No location token appears |
| **Fixed calendars** | **No calendar, date, duration or velocity appears in any wave.** The unit is ordinal dependency depth (§2.4). This is a deliberate divergence from one prior ordering document, registered as `C-4` | Search for a duration; none exists |
| **Fixed units** | The only unit is edge depth, declared under `P-7`. No effort, points, personnel or size | §2.4 |
| **Fixed technologies** | Mechanisms are cited by located path — `engine/uaue/discovery.py`, `platform/universal_ownership.cli` — and each citation is a **current manifestation**, not a constraint. §9 treats technology explicitly as an evolutionary state per `ISD-L-09` | Substituting a mechanism changes a citation, not an edge |
| **Fixed languages** | No node requires a programming or natural language. §9.1(b) records the Python floor as a manifestation and a ceiling as illegal | `UEUF-04` exists precisely so language is not fixed |
| **Fixed APIs** | No node names an API contract as permanent. Commands are cited as evidence of current behaviour, and each is falsifiable by execution | §3 gives commands, not interfaces |
| **Fixed intelligence models** | No node presumes an intelligence model. `UEUF-06` admits model evolution as assimilated external state, and the refusal of an internal forecaster is preserved with its stated reason rather than overridden | §9.1(f) |

### 11.1 Self-application

This model is subject to its own rules. Three consequences, stated so they can be held against it:

1. **Its closed enumerations are disclosed with admission paths**: edge-source kinds `{E1, E2, E3}` (§1.1), node classes (§1.3), and the seven prerequisite analyses as given by the directive (§9.4). The wave set is deliberately **not** closed (§1.4). This follows `ISD-L-01` discipline as implemented: closure is not the defect; undisclosed closure is.
2. **It is an evolving entity.** Any measurement in §3 that changes changes the graph. The ownership figure, the failing-stage set, the dirty-path count and the anonymous-object count are all live, and each is reproducible by the command given.
3. **It carries no permanence declaration**, and was authored under the `ISD-L-07` phrase constraint deliberately, having measured that gate's current refusal (§3.3, §13.2).

### 11.2 Examples are not boundaries

Every list in this document is a **located population at a measured moment**, not a definition. The nine `ISD-L-07` phrases, the nine UAUE discovery sources, the 53 declared CEU forms, the 26 gates and 48 checks, the 33 facets, the 16 context axes, the 20 civilization dimensions, the 15 verification stages, the eight owner decisions: each is data with a declared admission path, and citing a count here is evidence of the current state rather than an assertion of the possible.

---

## SECTION 12 — CONFLICTS REGISTERED

Recorded rather than resolved, because resolving a located conflict by preference is how an assumption enters a graph.

| ID | Conflict | Disposition |
|---|---|---|
| `C-1` | `AS-14` evidence key: the register says *"not blocked on authority"*; `MI-10` routes it as blocked on the `H-06`/`CR-09` mode decision | Conservative arc taken (Wave 6). If the permissive reading holds, `AS-14` moves to Wave 1 and becomes the second-cheapest node in the graph. **Falsifiable by exhibiting an evidence-key registration that mutates nothing** |
| `C-2` | Impact wiring: `MI-5` routes `AS-09`/`IM-01` as *"WIRE, no blocker"* and mutually independent; the register groups them behind gate purity | Conservative arc taken (Wave 6). Same falsification test |
| `C-3` | `H-06-IADR-UPDATED` internal staleness: `:18` and §8 record a signed `AUTHORIZED` entry `S-1`; `:7` and `:441-444` say *"§8 unsigned"*; the owner-decision record still reports UNSIGNED | The signed §8 is later and governs the scope question. **Implementation remains gated either way** — Phase 0 stands at 2 of 6. Not resolved here; it is the owner's record to reconcile |
| `C-4` | `CANONICAL-IMPLEMENTATION-DEPENDENCY-GRAPH-DETERMINATION.md` asserts a 6-phase, ~70-week calendar; `PL-05` measures effort *in points, never calendar time* because *"the repository carries no velocity evidence"*, and `07-CRITICAL-PATH-ANALYSIS.md:5` refuses time estimates outright | This graph asserts no time. The prior document's schedule is not inherited. It additionally assumes constitutional decisions are schedulable, which `MP2-C-04` finds unsatisfiable as written |
| `C-5` | Register summary versus measurement: *"pytest + coverage"* implies a coverage breach, but coverage is 97% against a 90 floor and the failure is 23 tests; *"UGA-INV-01..10"* implies ten invariants, but 2 are blocking; *"2 permanence occurrences"* is 3 occurrences across 2 files | Corrected here with the measurements in §3.3. All three corrections make the work larger, not smaller |
| `C-6` | The register cites `AU-01` twice and defines it nowhere; the tracked identifiers are `AT-1`/`AT-2`; an unrelated `AU-01` audit principle exists elsewhere | Resolved by reference to `AT-1`/`AT-2` (§2.2). No node created |
| `C-7` | The register's header declares *"18 closure scopes"*; its §19.2 rollup lists 17 and sums to 135 | 17 substantive scopes are used. §18 is the final gate assessment, not a scope; the header appears to count it |

One further tension, recorded because it looks like a contradiction and is not: 41 items are `CLOSED` under a definition requiring canonical ownership, while ownership coverage is 27.5%. The register's own explanation holds — closed items concentrate in programmes whose ownership is declared.

---

## SECTION 13 — FALSIFIABILITY AND SELF-DISCLOSURE

### 13.1 How to refute this graph

Adopting the precedent set by `UCOS-OMEGA-INFINITY-GAP-CLOSURE-SEQUENCING-DETERMINATION.md` §8:

> **If any node can be shown to close without its declared predecessor, that edge is wrong and this determination is amended.**

Specific, cheap refutation tests:
- Register an evidence key for `ucos-assimilate` that mutates nothing → refutes `C-1`'s conservative arc and moves `AS-14` to Wave 1.
- Compose the impact engine into an admission path without any undeclared write → refutes `C-2`'s conservative arc.
- Produce admissible certification evidence for any closure while `verify.sh --full` exits 1 → refutes §4.1, the graph's most load-bearing edge.
- Reach `CLOSED` on any item whose subject is unowned → refutes §4.2.
- Declare a substrate candidate class that UAUE discovers without any owner publishing a sealed artifact → refutes §9.2 and collapses Wave 10.

### 13.2 What creating this file did — measured, including one error made and corrected

Three measured consequences, disclosed rather than omitted, consistent with the register's discipline of recording its own effects. The second is a mistake this document made and then corrected, recorded because a determination that hides its own defect is the exact failure it exists to prevent.

**1. `ISD-L-07` — this file's first draft violated the law it was describing.** Both new files are root-depth-zero `.md` files inside the scanned roots (`.`, `00-CEP`, `00-CMG`, `99-FREEZE`, `engine`, `platform`), and any found path not in `preserved_sites` is a violation — a ratchet. The first draft of §3.3 quoted the gate's own output verbatim, including the **title** of `ISD-L-07`. That title contains, as a substring, one of the nine phrases the law scans for. Measured result:

```
python -m engine.infinite_scope.gate --quiet   →  exit 1
  ISD-L-07 [FAIL] — 3 undeclared sites:
    …ASSIMILATION-INFINITE-INTELLIGENCE-INTEGRATION-DETERMINATION.md   2 occurrences
    UCOS-OMEGA-INFINITY-CLOSURE-DEPENDENCY-GRAPH-DETERMINATION.md      1 occurrence   ← this file
    …UNIVERSAL-EVOLUTIONARY-ENTITY-FABRIC-DETERMINATION.md             1 occurrence
```

This is precisely the trap `engine/infinite_scope/contract.py:24-28` documents: the check deliberately avoids the literal token it detects, *because a detector matching its own source would be its own first finding.* Citing the law by title reintroduced the token that citing it by ID avoids. Corrected by referring to `ISD-L-07` by identifier only. Re-measured after correction:

```
python -m engine.infinite_scope.gate --quiet   →  exit 1
  ISD-L-07 [FAIL] — 2 undeclared sites, both pre-existing. Neither new file appears.
```

**Neither of these two documents now adds an `ISD-L-07` violation.** The gate's refusal is unchanged from the baseline in §3.3. Two consequences worth carrying forward: the `AD-G-01` finding that detection is declaration-bound has a mirror — *citation* is also phrase-bound, so any Wave 2 disclosure batch that quotes law titles will trip the laws it discloses; and the finding predicted in §8.2 occurred on its own first instance, which is evidence for the mechanism rather than for the author.

**2. `UGA-INV-10` — the anonymous-object population does not rise now, and the earlier prediction in §8.2 was too eager.** Measured after creating both files:

```
python 00-MASTER/UCOS-UGA-001/uga_engine.py gate  →  exit 1
  ANONYMOUS OBJECTS: 43   (unchanged)   Neither new file appears.
```

The cause is a boundary this determination had not established when §8.2 was written: UGA's population is `git ls-files -z --cached --exclude-standard`, i.e. **version-controlled files only**. Untracked files are outside the artifact boundary entirely. So creation has no effect; **the population rises on commit.** The `-z` flag is load-bearing rather than stylistic — 116 paths in this repository carry `Ω`/`∞`, and git quotes non-ASCII paths, which would mint identities under names no lookup could match.

**Consequence for Wave 1, and it is not cosmetic.** The `CEP-002` Article 28 decision that Wave 1 requires must enumerate its population **as measured after any commit of new determination documents**, not from the standing figure of 43. Each committed determination adds to it. The register's own count was taken at a moment; the decision must be taken at its own.

**3. No other surface is affected.** No code, configuration, declaration, registry or certification was modified. `dependencies`, `requires-python`, the CEU form catalog, `uccep-bindings.json` and every `*-declaration.json` are byte-unchanged.

---

## SECTION 14 — VERDICT

| Field | Value |
|---|---|
| NODES | 135 register items · 8 derived (`UEUF-00`…`UEUF-07`) · 5 vest-only conditions |
| SCHEDULABLE | **94** (53 OPEN · 27 GOVERNED · 14 BLOCKED); 41 CLOSED carried as satisfied |
| WAVES | **11** derived partitions + 1 vest-only class; unit declared as ordinal dependency depth (`P-7`) |
| INDEPENDENT ROOTS | **6** actionable + 2 decision-only. No single action discharges more than one |
| CRITICAL CHAIN | `0 → 4 → 6 → 7 → 8 → 10`, depth 6 |
| UNIVERSAL IN-EDGES | 2 — baseline → certification property; ownership → ownership property. Both land on properties, not on work |
| CHEAPEST NODE | `VF-06`/`EX-11` — `ISD-L-07` site disclosure; document owners only |
| HIGHEST LEVERAGE | `GV-01` ownership — gates the ownership property of every item, and is currently regressing |
| DEEPEST NODE | `UEUF-06` AI-model evolution — requires all seven prerequisites plus a blocked assimilation fabric |
| EVOLUTION FABRIC | **ABSENT.** Disclosed as `ISD-G-07`, not undetected. Its keystone prerequisite is a measuring owner, not an engine |
| PRIOR ORDERINGS | 5, over 5 different populations. **None ordered these 135 items.** Verified mechanically |
| CONFLICTS | **7** registered, 0 resolved by preference |
| AUTHORITY CEILING | T1 vacant (`VAC-01`); maximum attainable verdict `CERTIFIED-PROVISIONAL` (`UCCEP-F-004`); no competent ratifier (`MP2-C-04`) |
| CREATE DISPOSITIONS | **0** by this document |
| VERDICT | `GRAPH-DERIVED · NOTHING AUTHORIZED · NOTHING IMPLEMENTED` |

---

## STOP

Dependency graph derived. No implementation performed. No code, configuration, registry, declaration or certification modified. No requirement, ADR, identifier, authority, form, law or gate created. No item certified. The single mutation is the creation of this file, whose two measured consequences are disclosed in §13.2.

**Awaiting explicit authorization. The companion sequence plan is `UCOS-OMEGA-INFINITY-IMPLEMENTATION-SEQUENCE-MASTER-PLAN.md`.**
