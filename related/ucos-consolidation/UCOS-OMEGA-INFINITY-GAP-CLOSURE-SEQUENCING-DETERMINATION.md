# UCOS Ω∞ — GAP CLOSURE SEQUENCING DETERMINATION

| Field | Value |
|---|---|
| ARTIFACT | `UCOS-OMEGA-INFINITY-GAP-CLOSURE-SEQUENCING-DETERMINATION.md` |
| CLASSIFICATION | `EVIDENCE` — derived closure ordering |
| AUTHORITY | **NONE — DERIVED TRUTH.** Legislates nothing, ratifies nothing, certifies nothing, assigns no ownership, allocates no identity, changes no certification state, creates no ADR. Sequencing is an **ordering of what a future authorized cycle would face**, not an authorization to execute any of it. Where this determination and a located instrument differ, **the located instrument governs.** |
| DISPOSITION | **SEQUENCING ONLY. NO IMPLEMENTATION.** No code, configuration, registry, ledger or declaration modified. No identity minted. No ADR created. No certification state altered. |
| CONTINUES FROM | `UCOS-OMEGA-INFINITY-ASSIMILATED-GAP-GOVERNANCE-DETERMINATION.md` (19 findings, nine gap classes, four root-cause patterns) |
| BASELINE | HEAD **`bae59755d7e2`** · branch `integration/recovery-001` · working tree 64 entries at open, unchanged at close |
| BASELINE NOTE | The predecessor's baseline and this one share HEAD `bae59755`, but seven commits landed between the earlier determination set and this pass (`8dc9a812` … `bae59755`), including EXECUTION and CERTIFICATION of `REQ-28`, `REQ-43`, Violation 4, `REQ-23`, and a UREE admission determination. **Every inherited finding was therefore re-measured rather than carried forward.** Two did not survive re-measurement (§1). |
| MODE | Read-only. Nine live measurements taken (§0). |
| REFUSES | Coining a gap id · assigning ownership · authorizing a fix · forcing a governed refusal closed · sequencing a reserved decision as if it were work |

> **Headline.** The optimal order is **not** the severity order, and it is close to the **inverse** of the stated priority list for one finding. `G-01` is classified as an implementation gap — the lowest of the seven stated priorities — yet it is the hard prerequisite for every other wave, because `classify()` returns `ERROR` for every subject in the repository at this HEAD, so **no mutation made while closing any other gap can be shown to have been permitted.** Nine waves are determined. Two inherited findings were **refuted by live measurement**: `G-10`'s claim that `UFC-16` has no source instrument and zero code references is false — it is located, implemented, populated and CI-gated — which moves it from an authority gap to a *population under-declaration* and makes `G-02` substantially cheaper to close than inherited.

---

## 0 — Live re-measurement at HEAD `bae59755`

Read-only. No mutation. Each row is the basis for a sequencing decision, not a restatement of the predecessor.

| # | Measurement | Command / file | Result | Effect on order |
|---|---|---|---|---|
| M-1 | R-09 predicate coverage | `validate_rule_coverage(boundary)` | `("rule 'R-09' is declared but no predicate implements it",)` | **G-01 confirmed live at new HEAD** → Wave 0 |
| M-2 | Implemented predicates | `RULE_PREDICATES.keys()` | `R-01 … R-08` — **8 of 9** | one function is the delta |
| M-3 | Rule declaration site | `mutation_classification.py:415-421` | rules read from `boundary["classification_rules"]["rules"]`; coverage refuses **in both directions** | fix must be two-sided |
| M-4 | Short-circuit position | `classify:427-436` | `validate_rule_coverage` evaluated **before** the precedence loop → `ERROR` returned for all | outage is total, not partial |
| M-5 | `UFC-16` article | `platform/universal_foundation/constitution.py:386-396` | **LOCATED** — `article_id="UFC-16"`, title *"One Subject, One Measurement"*, `gate="FG-16-ONE-MEASUREMENT"` | **G-10 refuted** (§1.1) |
| M-6 | `UFC-16` enforcement | `.github/workflows/ufc-gate.yml:66` | *"Convergence gate (FG-14 exactly-once · FG-15 no-parallel-authority · FG-16 one-measurement)"* | rule is **CI-gated** |
| M-7 | `UFC-16` declared population | `platform/universal_foundation/catalog/foundation-convergence.json` | **6 models** (TRUTH, OWNERSHIP, ASSIMILATION, MEASUREMENT, DEPENDENCY, IMPLEMENTATION); `grep -ic 'requirement\|principle'` → **0** | the diverging populations are **out of scope** of the gate that would catch them |
| M-8 | `TemporalCoordinate.from_dict` | `engine/temporal/coordinate.py` | **ABSENT** (`class TemporalCoordinate:170`, `class ValidityPeriod:258` present) | G-05 confirmed: one deserializer gates 3 planes |
| M-9 | `gate_mode` field | `grep -rl 'gate_mode'` | **0** in `*.json`, **0** in `*.py` | G-11 confirmed → Wave 1 |
| M-10 | Phantom lifecycle authority | `grep -rl 'Universal Recursive Constitutional Lifecycle Governance'` | 3 constitutional docs (`CMG-000008/9/10`) + 3 determinations discussing it | G-03 confirmed, bounded to 3 files |
| M-11 | Duplicate "generated" expression | `00-BOOK/tools/config.py:885` `EXCLUDE_DIR_PREFIXES`; registry `entries: 345`, `producer_homes: 31` | both present | G-06 confirmed |
| M-12 | Openness gate | `engine.infinite_scope.gate --quiet --json` | `OPEN` · 11/11 laws · `unintentional: ['ISD-CE-09']` · 11 disclosures · 11 axes | G-07 confirmed; `ISD-CE-09` still open |

---

## 1 — Corrections to inherited findings

Both corrections **reduce** work and **change order**. Neither is a criticism of the predecessor's method; both are consequences of re-measuring rather than carrying forward.

### 1.1 `G-10` is refuted as stated — reclassify and re-scope

The predecessor records `G-10` as *"`UFC-16` has no source instrument in tree; **zero `.py` references**"*, class **GOVERNANCE/AUTHORITY**, severity **HIGH**, owner *"cited to `UCOS-UFC-001`, **not located**"*.

Measured at this HEAD, each element is false:

| Claim | Measured |
|---|---|
| no source instrument in tree | `platform/universal_foundation/constitution.py:386` declares `article_id="UFC-16"` with its full mandate text and `gate="FG-16-ONE-MEASUREMENT"` |
| zero `.py` references | **11** `.py` files reference `UFC-16` |
| `UCOS-UFC-001` not located | `platform/universal_foundation/convergence.py:1` — *"`UCOS-UFC-001` — Constitutional model convergence (UFC-14, UFC-15, UFC-16)"*; `GATE_ONE_MEASUREMENT` at `:64` |
| unenforced | `ufc-gate.yml:66` runs the convergence gate; `make convergence-gate` exists |

The programme is implemented as a **package** (`platform/universal_foundation/`), not as a `00-MASTER/UCOS-UFC-001/` directory — which is why a directory-shaped search finds nothing.

**What is actually true, and it is a different and more useful finding.** `FG-16` measures convergence over its **declared population of six Foundation constitutional models**. Requirements (49 / 549 / 54) and principles (22 / 5) are **not members of that population** (M-7). So:

> `UFC-16` is located, implemented and enforced **exactly where it is declared**, and its declared population does not include the populations it is most often cited to refuse.

**Restated as `G-10′`: MEASUREMENT GAP — population under-declaration.** Severity **MEDIUM** (down from HIGH). Owner: `platform/universal_foundation/`. Closure is a **catalog entry in a JSON population an existing CI gate already reads**, not a new governing instrument.

**Order consequence, and it is the most valuable in this determination.** `G-10′` must precede `G-02` and `PA-G-04`, because it supplies the mechanical enforcement those findings need. The predecessor treats `G-02` as requiring a fresh governing determination under `CEP-002` 14.2; with `G-10′` closed first, the *owner decision* still stands but its **implementation collapses to declaring a relation into an already-gated population.** Zero enforcement machinery has to be built.

### 1.2 The `G-08`/`G-09` standing is confirmed, and constrains sequencing

Not a correction but a sequencing constraint worth restating: `G-08` and `G-09` are **governed positions**, not backlog. Sequencing them as work would breach the located instruments. They are placed in Wave 8 as *declaration* tasks, and their acceptance criterion is a recorded refusal to assess, never an assessment.

---

## 2 — Dependency graph

Arrows are **hard prerequisites** (the successor cannot be validly closed before the predecessor), not preferences.

```
WAVE 0   G-01  R-09 predicate + classify() consumer
           │      (nothing can be shown to be a permitted mutation until this holds)
           ▼
WAVE 1   G-11  gate_mode  ── (must know which gates mutate before running any to validate)
           │
           ├──────────────┬──────────────┐
           ▼              ▼              ▼
WAVE 2   G-03          G-10′          G-13
         phantom       UFC-16         GOVERNED CLOSURE /
         authority     population     OPEN GAP unrepresented
           │              │
           └──────┬───────┘
                  ▼
WAVE 3   Pattern A generalization  (convergence-gate model → supersession enforcement)
              │        └── G-06  duplicate "generated" expression
              ▼
WAVE 4   G-02 · PA-G-04 · G-19 · G-18      (measurement correctness; two RESERVED)
              │
              ▼
WAVE 5   G-07  discovery-bound closure  (observe-and-disclose first)
              │
              ▼
WAVE 6   G-05 → G-04                      (Pattern C propagation)
              │
              ▼
WAVE 7   G-14 · G-16                      (ownership / evidence voids)
              │
              ▼
WAVE 8   G-08 · G-09 · G-12 · G-17        (declare unassessability — NOT assessment)
              │
              ▼
WAVE 9   G-15                             (capability evolution loop — implementation last)
```

**Why the stated priority list inverts for `G-01`.** The directive orders implementation gaps **seventh**. `G-01` is an implementation gap. But its subject is the mutation-classification plane, and every wave below it performs mutations. Closing `G-03` while `classify()` returns `ERROR` produces a correction nobody can demonstrate was a permitted mutation. So the priority axes must be read **per finding as the reason for acting**, not as a global schedule: `G-01` qualifies under axis 1 (preventing incorrect future evolution) and axis 2 (restoring governance integrity), which are first, and its *class* is irrelevant to its position.

---

## 3 — The bootstrap paradox in Wave 0, and its disposition

Naming this explicitly because a future cycle will hit it immediately and it is not addressed in the predecessor.

Closing `G-01` requires editing `platform/repository_intelligence/mutation_classification.py` and possibly `mutation-governance-boundary.json`. Both edits are mutations. **Their own mutation class cannot be determined at the moment they are made**, because `classify()` returns `ERROR` until the fix lands. The plane cannot authorize its own repair.

Three dispositions are available. Only one is sound:

| Option | Assessment |
|---|---|
| Classify first, then fix | **Impossible.** Circular — classification is what is broken. |
| Fix, then classify retroactively | **Unsound as evidence.** Retroactive classification of one's own repair is the self-certification `CF-C4` voids, and echoes the fabricated-history defect `adr/0024` explicitly refused for `DEC-ADR-0015..0023`. |
| Fix under the **declaration's own superior authority**, then verify forward | **Sound.** The boundary document declares itself *"AUTHORED REPOSITORY TRUTH, HELD SUBORDINATE UNDER `UCKP-LAW-0001`"*. `UCKP-LAW-0001` (`engine/uckp/law.py`, `UCKP-ART-10`, `UCKP-ART-16`) is upstream of the classifier and unaffected by its outage. The repair is authorized by the superior, not by the broken subordinate, and the **first act after the fix** is to classify the repair's own changed paths and record the result. |

**The outage is therefore self-disclosing rather than self-authorizing**, and the sequencing must record that the Wave 0 edit is the one mutation in the entire programme whose class is established *after* the fact by necessity — with that necessity stated, not glossed.

A second Wave 0 caution: `P0-DECLARATION-001` records that `platform/repository_intelligence` *"is not a governed package… falls outside the scope of UFC-14, UFC-15 and UFC-16 entirely."* So the code plane being repaired sits **outside** the measurement law governing its own declaration. That asymmetry is part of `G-01`'s root cause and should be dispositioned in the same cycle, or the fix restores function without restoring governance.

---

## 4 — Wave sequencing, with the eight required determinations per finding

### WAVE 0 — Restore the disabled governance plane

**Rationale: axis 1 + axis 2.** Blocks all nine waves.

| Field | `G-01` — R-09 predicate absent |
|---|---|
| **Dependency order** | **1st. No predecessor. Hard prerequisite for every other finding.** |
| **Prerequisite decisions** | **D-1** (§5): is `extend_mutation_governance_boundary` the intended registration path, or vestigial? Must be answered *before* the predicate lands, or two registration paths coexist — a parallel authority the repository forbids. |
| **Canonical owner** | Declaration: `00-BOOK/DATA/mutation-governance-boundary.json`. Code: `platform/repository_intelligence/mutation_classification.py` (EX-016). |
| **Authority requirement** | `UCKP-LAW-0001` (`UCKP-ART-10`, `UCKP-ART-16`) as superior — see §3. **No new authority.** Owner authorization to edit the code plane. |
| **Reuse opportunity** | **Total. Nothing needs designing.** `mutation_class_extension.py` already carries `GOVERNED_ANALYSIS_CLASS:19` and `GOVERNED_ANALYSIS_RULE:65` (`"id": "R-09"`); the six `membership_criteria` are already declared on the class. The work is binding a predicate into `RULE_PREDICATES`, not authoring semantics. |
| **Implementation requirement** | One predicate satisfying the six declared criteria, registered into `RULE_PREDICATES`; **plus** a consumer that runs `classify_all` over changed paths and fails on non-`CLASSIFIED` (Pattern B — without it, recurrence is invisible). |
| **Validation requirement** | `validate_rule_coverage()` returns `()`; `classify()` returns `CLASSIFIED` with non-empty `rule_id` for ≥1 subject per declared class; `GOVERNED_ANALYSIS` for a determination document; a **non-vacuous** test asserting the predicate *rejects* a non-analysis subject. |
| **Certification requirement** | **None yet.** Certification is premature until the consumer gate exists; a classifier that works but is read by nothing is `G-01`'s own root cause recurring. |

### WAVE 1 — Make gate behaviour knowable before running gates

**Rationale: axis 1 + axis 2.** Sequenced second because Waves 2–9 must *run gates to validate*, and today it cannot be known which gates mutate.

| Field | `G-11` — no `gate_mode` field; PRODUCER-vs-OBSERVE is prose |
|---|---|
| **Dependency order** | 2nd. After `G-01` (so gate runs are classifiable). Before every wave that validates by running a gate. |
| **Prerequisite decisions** | None blocking. Optionally **D-4** if universal drift coverage is folded in. |
| **Canonical owner** | `UVI-000001`. |
| **Authority requirement** | Owner authorization. No new authority. Note `H-06-MUTATION-GOVERNANCE-OWNER-DECISION-RECORD.md` stands `OPTION B SELECTED — AWAITING RATIFICATION`, so the ratification question is already open and routes to the owner. |
| **Reuse opportunity** | High. `verify.sh` Stage 6d already byte-compares a replay; `uisd-gate.yml` already re-derives stage labels against a digest. The declaration pattern (`*-declaration.json` + fail-closed engine check) is the house shape. |
| **Implementation requirement** | A `gate_mode` field on gate declarations with a fail-closed check that a gate declaring OBSERVE writes nothing. Measured cost of *not* doing this is on record: `requirement_engine.py --gate` wrote 12 files and only a manual `git status` caught it. |
| **Validation requirement** | For each declared OBSERVE gate, tree byte-identical across a run; a declared PRODUCER that writes nothing, and an OBSERVE that writes, both fail. |
| **Certification requirement** | None. Enables later certification; claims none. |

### WAVE 2 — Correct the authority record and the measurement scope

**Rationale: axis 2 + axis 3 + axis 6.** Three independent items; may run in parallel.

| Field | `G-03` — `CMG-000008/9/10` inherit a non-existent authority |
|---|---|
| **Dependency order** | 3rd, parallel with `G-10′`/`G-13`. |
| **Prerequisite decisions** | Per-document target owner (`UCIC-001` / `UCL-000001` / Article 14) — a reading of each document's subject, not a new decision. |
| **Canonical owner** | `CMG` corpus; lifecycle owners `UCIC-001` (law) and `UCL-000001` (derived). |
| **Authority requirement** | `CEP-009` amendment path for constitutional text. **Explicitly forbidden:** creating a fifth lifecycle instrument to satisfy the citation. |
| **Reuse opportunity** | High. `04-LIFECYCLE-AUTHORITY-CROSSWALK-REGISTER.md` already crosswalks six owners — the correct targets are already enumerated. |
| **Implementation requirement** | Bounded reference correction in 3 files (M-10), plus a parser/gate that reads `LIFECYCLE METADATA` so the claim becomes falsifiable. **The parser is the substantive half** — without it the corrected claim is as unfalsifiable as the broken one. |
| **Validation requirement** | Zero occurrences of the phantom string outside historical evidence; each document names a locatable owner; a gate fails on an unlocatable lifecycle authority; `--check-no-parallel-authority` still passes. |
| **Certification requirement** | None. The current self-certifications are worthless-by-construction and must be *withdrawn or made falsifiable*, not re-issued. |

| Field | `G-10′` — `UFC-16` population under-declared *(restated, §1.1)* |
|---|---|
| **Dependency order** | 3rd. **Must precede Wave 4.** |
| **Prerequisite decisions** | Whether requirement and principle populations are in-scope subjects for Foundation convergence, or belong to a sibling measurement authority. |
| **Canonical owner** | `platform/universal_foundation/` (`UCOS-UFC-001`); population `catalog/foundation-convergence.json`. |
| **Authority requirement** | Owner authorization to extend a declared population. **No new instrument, no new gate** — this is the correction that `G-10`-as-inherited would have over-scoped. |
| **Reuse opportunity** | **Maximal.** Article, gate, engine, CI wiring and population file all exist (M-5, M-6, M-7). |
| **Implementation requirement** | Catalog entries extending the 6-model population to cover the diverging populations, with each subordinate declaring `DELEGATES` / `SUPERSEDED` / `PROJECTION` as `convergence.py` already verifies. |
| **Validation requirement** | `make convergence-gate` / `ufc-gate.yml` passes with the extended population; a synthetic competing measurement is **refused** (non-vacuity — the gate must be shown able to fail). |
| **Certification requirement** | None. Certification of "one measurement" belongs to the owner after Wave 4 declares the relations. |

| Field | `G-13` — `GOVERNED CLOSURE` / `OPEN GAP` have zero code representation |
|---|---|
| **Dependency order** | 3rd, parallel. |
| **Prerequisite decisions** | None. |
| **Canonical owner** | Master Index. |
| **Authority requirement** | Owner authorization. |
| **Reuse opportunity** | Moderate — the six coexisting verdict vocabularies are a **governed position** (independent vocabularies, taxonomy authority rejected), so this must add a representation **without** creating a translation layer. |
| **Implementation requirement** | A machine representation of the two states so a status transition is measurable rather than prose. |
| **Validation requirement** | Every index status resolves to a representable value; a status not in the vocabulary fails. |
| **Certification requirement** | None. |

### WAVE 3 — Generalize supersession enforcement (Pattern A)

**Rationale: axis 1 + axis 5.** The highest-leverage systemic item: it closes the *class* behind `G-02`, `G-03`, `G-06` rather than three instances.

| Field | Pattern A generalization + `G-06` |
|---|---|
| **Dependency order** | 4th. After `G-03` (supplies a concrete instance) and `G-10′` (supplies the measurement). |
| **Prerequisite decisions** | **D-4**: is universal byte-equality drift coverage required, or is per-owner coverage plus producer-invocability the governed sufficiency condition? |
| **Canonical owner** | `UCOS-GENERATED-ARTIFACT-REGISTRY-001` (register) · `UCOS-UGA-001` (invariants) · `00-BOOK` tooling plane (`config.py`). |
| **Authority requirement** | `UCKP-LAW-0001` (`UCKP-ART-04/11/13`). Owner authorization for the retirement or derivation. |
| **Reuse opportunity** | **The fix pattern already exists and is proven**: `make convergence-gate` *"fails if the retired homing module reappears"* — installed after two determinations over one population reported different numbers. The predecessor's key observation is that this precedent is **not generalised**; generalizing it is the work. |
| **Implementation requirement** | Exactly one authored expression of "this path is generated", or a declared derivation with a test asserting agreement (M-11: registry 345 entries + `config.py:885`); plus a supersession guard preventing the retired expression reappearing. |
| **Validation requirement** | Guard fails when the retired expression is reintroduced (non-vacuity); all 345 entries either byte-replay-covered or explicitly out of scope with a reason. |
| **Certification requirement** | None for the instance. A **governance certification is defensible only after** the guard is shown to fail on reintroduction. |

### WAVE 4 — Measurement correctness and reconciliation

**Rationale: axis 6 + axis 5.** Two items are **RESERVED** — sequenced as decisions, not work.

| Field | `G-02` — 49 / 549 / 54 requirement populations, no join |
|---|---|
| **Dependency order** | 5th. **After `G-10′`.** |
| **Prerequisite decisions** | **D-2** — reserved to a governing authority under `CEP-002` 14.2. **This determination does not resolve it and cannot.** |
| **Canonical owner** | Plane 1 `UAKOS-CLOSURE-009`; Plane 2 Master Index. **The join is unowned — that absence is the gap.** |
| **Authority requirement** | Owner decision. **Material caveat:** `UCAF-RC-01/02/03` record that no located authority in this corpus is competent to ratify, and `UCAF-F-003` holds that competence to ratify *"is not closable by measurement."* So D-2 routes to the **human owner**, not to a repository process. |
| **Reuse opportunity** | High and now higher than inherited: `engine/ceu/existence.py::relate()` already admits a declared relationship type, and after `G-10′` the relation lands in an already-gated population. |
| **Implementation requirement** | One registered relationship with a declared type (subset / projection / disjoint / equivalence) and cited basis; a stated rule for which plane answers "how many requirements exist". |
| **Validation requirement** | Every published requirement percentage carries denominator and plane; a second number for one population is refused by `FG-16`. |
| **Certification requirement** | `RU-G-01` moves `OPEN GAP → GOVERNED CLOSURE`, **not to `CERTIFIED`** — nothing is built. The `REQ-43` precedent governs. |

| Field | `PA-G-04` (22 vs 5 principle planes) · `G-19` (2 maturity models) · `G-18` (frozen-prefix duplicate) |
|---|---|
| **Dependency order** | 5th, parallel with `G-02`. |
| **Prerequisite decisions** | **D-3** for `PA-G-04` — reserved, same shape and same routing as D-2. `G-19`/`G-18` need none. |
| **Canonical owner** | `PA-G-04`: unowned join. `G-19`: `UAKOS-CLOSURE-009` / `universal_foundation`. `G-18`: `frozen_paths.py` / `policy.py`. |
| **Authority requirement** | Owner decision for `PA-G-04`; owner authorization only for `G-19`/`G-18`. |
| **Reuse opportunity** | `G-18` is a shared-constant extraction — pure reuse, no design. `G-19` reuses the same relation mechanism as `G-02`. |
| **Implementation requirement** | `G-18`: one shared constant. `G-19`: declare the relation between two maturity models sharing token names with different arity. `PA-G-04`: a declared relation. |
| **Validation requirement** | `G-18`: both modules resolve to one constant, and a divergence fails. `G-19`: arity collision detectable. |
| **Certification requirement** | None. |

### WAVE 5 — Enable automatic assimilation

**Rationale: axis 4.** The axis-4 item, and the one with a hard sequencing constraint recorded by its own owner.

| Field | `G-07` — closure detection declaration-bound, not discovery-bound |
|---|---|
| **Dependency order** | 6th. After `G-01` (its findings are mutations to be classified) and `G-11` (its gate mode must be declarable). |
| **Prerequisite decisions** | Confirmation that the first landing is **non-blocking**. This is not optional: the located source records that landing it blocking *"would fail the gate on legitimately-closed enumerations that have simply never been disclosed — converting a true finding into a false law, which the codebase's own doctrine says **gets disabled**."* |
| **Canonical owner** | `UISD-000001` = `engine/infinite_scope/`; disclosure home `uisd-declaration.json`; principles `adr/0007`, `adr/0022`. |
| **Authority requirement** | Owner authorization. **`--check-no-parallel-authority` makes a second detector a gate violation**, so this is closable *only* by extending this owner. |
| **Reuse opportunity** | **Very high.** The AST machinery already exists inside the detector: `_population_literals:657`, the permanence ratchet, and `ISD-L-06`'s live synthetic-member admission with two-way reconciliation. A new law enters `LAW_CHECKS` + declaration, not a new module. |
| **Implementation requirement** | Discovery sweep in observe-and-disclose mode; then blocking. Also `AD-G-02` (import-level check — the stdlib-only claim currently rests on a manual grep no gate re-runs), `AD-G-04` declared axes, and **`ISD-G-09`'s brittle `len(unintentional) == 1` assertion**, which today requires an engine edit to disclose a newly found closure — a meta-gap that would obstruct its own remedy. |
| **Validation requirement** | Sweep enumerates every closed vocabulary in declared roots and reports those absent from `closed_enumeration_disclosures`, two-way; `ISD-CE-09` (M-12, still `intentional: false`) either closed by owner act or re-disclosed unchanged; no second detector created. |
| **Certification requirement** | **No openness certification until the sweep is blocking.** Until then the guarantee is exactly as strong as human disclosure discipline — which `ISD-CE-09` proves has lapsed once. |

### WAVE 6 — Propagation (Pattern C)

**Rationale: axis 6 + axis 3.** Neither requires invention.

| Field | `G-05` — temporal validity in 1 of 4 relationship planes |
|---|---|
| **Dependency order** | 7th. `G-05` before `G-04` (both are propagation; `G-05`'s blocker is mechanical and unblocks three planes). |
| **Prerequisite decisions** | **D-5**: per plane, does validity belong there? CEU may legitimately conclude supersession lineage suffices for a unit-of-existence. **That is a determination, not a code task.** |
| **Canonical owner** | Primitives `CMG-000002` → `engine/temporal/`; relationship validity `UCKP-ART-07` (`adr/0015`); planes `CEU-001`, UKG, DATA. |
| **Authority requirement** | `engine/temporal` owner for the deserializer; per-plane owners for D-5. |
| **Reuse opportunity** | **Total.** `ValidityPeriod`, `TemporalCoordinate`, `Ordering`, `operations.compare()` failing closed on `INCOMPARABLE`, and the UKIP algebra (72 tests) as a working reference. |
| **Implementation requirement** | `TemporalCoordinate.from_dict` (M-8: absent), which unblocks `RelationDeclaration.from_dict`'s fail-closed refusal of non-null `validity`. **One function gates propagation to three planes.** |
| **Validation requirement** | `from_dict` round-trips; `RelationDeclaration.from_dict` accepts non-null validity; each of 4 planes carries validity or records a reasoned determination; a cross-plane conformance test exists. Note `ISD-G-04`: the relationship model has **no gate at all**, so absence is currently unenforceable either way. |
| **Certification requirement** | None until the cross-plane test exists. |

| Field | `G-04` — `ContextRegistry` unpersisted + 6 bypassing context types |
|---|---|
| **Dependency order** | 8th, after `G-05`. |
| **Prerequisite decisions** | Which existing owner holds context-binding durability. The memory doctrine (`ADR-0013`, `UCI-001` XVI.5) **forbids a new store** and permits a *record* held by an existing owner. |
| **Canonical owner** | `UCXI-000001` = `engine/context/`; binding statement `CMG-000012`. |
| **Authority requirement** | Owner authorization. `CXL-06` Context Once and `CAA-INV-07` forbid a rival model — the constraint is tight and self-enforcing. |
| **Reuse opportunity** | High. `engine/uckp/persistence.py::PersistenceAdapter` is an existing storage-agnostic seam **no context owner uses**. |
| **Implementation requirement** | Durable record for context bindings under a named existing owner; a disposition per bypassing type (assimilate or declare out of scope). |
| **Validation requirement** | A binding survives a process boundary; `bind_confidence` recoverable after restart; each ad-hoc type registered or declared out of scope; `P4-F-009` dispositioned; no second context authority. |
| **Certification requirement** | None. Confidence claims are currently unreproducible across processes and must not be certified until they are. |

### WAVE 7 — Ownership and evidence voids

**Rationale: axis 2 + axis 3.**

| Field | `G-14` (145 determinations lifecycle-unbound) · `G-16` (`Checkpoint`/`AuditLog` no durable sink) |
|---|---|
| **Dependency order** | 9th. `G-14` after Wave 0 — determination documents are the `GOVERNED_ANALYSIS` class R-09 governs, so binding them is only meaningful once that class classifies. |
| **Prerequisite decisions** | For `G-14`: confirm the governed outcome is a **lifecycle binding**, not identity minting. The 145 are `NON_CANONICAL` evidence which *is kept*; only their lifecycle binding is at issue. |
| **Canonical owner** | `G-14`: unowned. `G-16`: `EPIC-RTE-002`. |
| **Authority requirement** | Owner authorization. **Explicitly not** `REG-AUTO-001` minting — the directive and the located instruments both forbid identity allocation here. |
| **Reuse opportunity** | `G-14` reuses the R-09 `GOVERNED_ANALYSIS` class from Wave 0 — a direct dependency dividend. `G-16` reuses `PersistenceAdapter`. |
| **Implementation requirement** | `G-14`: lifecycle binding for the determination population. `G-16`: a durable sink. |
| **Validation requirement** | `G-14`: every determination resolves to a lifecycle state without minting an identity; ledger `by_path` count unchanged. `G-16`: checkpoint survives process boundary. |
| **Certification requirement** | None. |

### WAVE 8 — Declare unassessability (must NOT be forced closed)

**Rationale: axis 3.** These are **governed positions**. Their acceptance criterion is a recorded declaration, and forcing an assessment would breach the located instruments.

| Field | `G-08` · `G-09` · `G-12` · `G-17` |
|---|---|
| **Dependency order** | 10th. Independent of all technical waves; last because they are declarations, not repairs. |
| **Prerequisite decisions** | **D-6** (`G-09`): for each of Reason/Challenge/Predict/Simulate/Optimize — already covered by an existing UCL stage, admissible as new, or out of scope? |
| **Canonical owner** | `G-08`: unowned (**no subject exists**). `G-09`: stage graph `UCL-000001`, law `UCIC-001`. `G-12`: `adr/0021`. `G-17`: `UCOS-EG-001`. |
| **Authority requirement** | `CEP-009` for any stage admission. `adr/0011` stands as the decision that **no second evolution engine** may be built for `G-09`'s region. |
| **Reuse opportunity** | `G-08`: `PersistenceAdapter`'s 10-implementation pattern is the transferable template **when a surface eventually exists**. `G-09`: located partials — `superiority_engine.py` (Challenge, records `UNDECIDABLE`), `impact.py` (Simulate), `make verify-cost-model` (Optimize, deliberately ungated). |
| **Implementation requirement** | **None, and building any would be a defect.** `G-08` requires a *trigger condition* binding the first protocol/interface expression to a neutrality check. `G-09` requires a mapping determination. The located instrument is explicit: building an abstraction to pass a certification *"would be manufacturing evidence, not discovering it."* |
| **Validation requirement** | `G-08`: both categories recorded `NOT ASSESSABLE — NO SURFACE` with reason; the seven-category assessment reports **5 assessed + 2 declared-unassessable**, not 7 with 2 silent; trigger exists. `G-09`: each of five mapped, admitted, or out-of-scope; `ISD-L-05` still holds (no terminal stage); `verify_manifest_alignment()` passes with the engine unchanged. |
| **Certification requirement** | **Explicitly none.** Declaring `G-09`'s five `OPEN GAP` would be as unfounded as declaring them `CERTIFIED`. |

### WAVE 9 — Implementation gaps last

**Rationale: axis 7.**

| Field | `G-15` — capability evolution loop unbound; 7 band-local lifecycles; cert coverage of implementation 0% |
|---|---|
| **Dependency order** | 11th, last. Depends on Wave 0 (mutation classification), Wave 4 (`G-10′`/`G-02` fix the denominator that "0%" is measured against), and Wave 6 (`G-04` restores context durability the loop consumes). |
| **Prerequisite decisions** | Whether the 7 band-local lifecycles delegate or are superseded — the same `DELEGATES`/`SUPERSEDED`/`PROJECTION` question `convergence.py` already adjudicates. |
| **Canonical owner** | `UCIC-001` / `UAUE-000001`; acceptance `AEOS-001` AC-1…6. |
| **Authority requirement** | Owner authorization. |
| **Reuse opportunity** | High — `CapabilityRegistry` exists; `convergence.py`'s relation vocabulary applies directly to the 7 band-local lifecycles. |
| **Implementation requirement** | Bind the evolution loop to `CapabilityRegistry`; resolve the band-local lifecycles. |
| **Validation requirement** | `AEOS-001` AC-1…6 discharged by measurement; certification coverage of implementation reported with its denominator declared (Wave 4 dependency). |
| **Certification requirement** | The only wave where a **capability certification** is ultimately in scope — and only after its denominator is declared. A "0% → N%" claim is unreadable until Wave 4 closes. |

---

## 5 — Prerequisite decision register

Every decision that must be answered before the work it blocks. **None is answered here.**

| ID | Decision | Blocks | Type | Routes to |
|---|---|---|---|---|
| **D-1** | Is `extend_mutation_governance_boundary` the intended R-09 registration path, or vestigial? Its only caller is a test. | `G-01` (Wave 0) | Design disposition | Owner of `platform/repository_intelligence` |
| **D-2** | Relation between `REQ-NN` and `RR-*` populations: subset, projection, disjoint or equivalence | `G-02` (Wave 4) | **RESERVED** `CEP-002` 14.2 | **Human owner** — no located competent authority (`UCAF-RC-01/02/03`) |
| **D-3** | Principle population authority (22 vs 5) | `PA-G-04` (Wave 4) | **RESERVED**, same shape as D-2 | **Human owner** |
| **D-4** | Is universal byte-equality drift coverage required, or is per-owner coverage + producer-invocability the governed sufficiency condition? | `G-06`, Wave 3 | Governance sufficiency | Register owner + `UCOS-UGA-001` |
| **D-5** | Per relationship plane: does temporal validity belong there? | `G-05` completion (Wave 6) | Determination, not code | `CEU-001`, UKG, DATA owners |
| **D-6** | For each of Reason/Challenge/Predict/Simulate/Optimize: covered, admissible, or out of scope? | `G-09` (Wave 8) | Mapping determination | `UCL-000001` / `UCIC-001` |
| **D-7** | Whether requirement/principle populations are in-scope subjects for Foundation convergence | `G-10′` (Wave 2) | Scope declaration | `platform/universal_foundation/` owner |
| **D-8** | Disposition of the `platform/repository_intelligence` governance asymmetry (outside UFC-14/15/16 per `P0-DECLARATION-001`) | `G-01` completeness | Governance scope | Owner |

**Standing constraint on D-2, D-3 and every "reserved" item.** `UCAF` records three located instruments asserting no authority in this corpus is competent to ratify, classified `STANDING-CONSTITUTIONAL-CONFLICT` (`UCAF-F-002`), with `UCAF-F-003` holding that competence to ratify is *"not closable by measurement."* Reserved decisions are therefore **owner decisions awaiting a person**, not repository work awaiting a process. Sequencing them as backlog would misrepresent them.

---

## 6 — Special-focus items, mapped to position

| Focus item | Finding | Wave | Position rationale |
|---|---|---|---|
| **Mutation governance R-09** | `G-01` | **0** | Confirmed live (M-1..M-4). Total outage; one function; hard prerequisite for all waves. Bootstrap paradox dispositioned in §3. |
| **Fail-closed consumption path** | `G-01` consumer + `G-11` | **0–1** | Pattern B. A correct refusal read by nothing. Both are "verdict into a void"; the consumer is part of Wave 0's definition of done, not a follow-on. |
| **Supersession enforcement** | Pattern A (`G-02`, `G-03`, `G-06`) | **2–3** | Highest systemic leverage. `convergence-gate` already proves the enforcement pattern; generalizing it closes a class, not an instance. |
| **Measurement authority** | `G-10′`, `G-02`, `G-04` | **2, 4, 6** | **Re-sequenced by §1.1.** `UFC-16` is located and CI-gated; its population is under-declared. Fixing scope in Wave 2 makes Wave 4 a catalog declaration rather than new machinery. |
| **Requirement universe reconciliation** | `G-02` | **4** | Reserved decision D-2. Sequenced *after* `G-10′` so the relation lands in an already-gated population. |
| **Temporal propagation** | `G-05` | **6** | One absent deserializer (M-8) gates three planes. Pure propagation; per-plane belonging is D-5, a determination not a code task. |
| **Artifact relationship resolution** | `G-06` | **3** | Two expressions of one invariant (M-11). Closes with Pattern A's guard. |

---

## 7 — Risk assessment of the sequencing itself

| ID | Risk | Severity | Mitigation |
|---|---|---|---|
| SQ-R-01 | Waves 2–9 are executed while `classify()` returns `ERROR`, so no corrective mutation can be shown to have been permitted | **HIGH** | Wave 0 is a hard gate. No wave proceeds until `validate_rule_coverage()` returns `()`. |
| SQ-R-02 | Wave 0's own edit is treated as self-authorizing, or retroactively self-classified | **HIGH** | §3: authorize under `UCKP-LAW-0001`; verify forward; record the necessity rather than glossing it. |
| SQ-R-03 | `G-01` is closed without the consumer gate, so the identical outage recurs invisibly | **HIGH** | The consumer is inside Wave 0's definition of done. This is Pattern B recurring on its own fix. |
| SQ-R-04 | Gates are run to validate later waves without knowing which mutate — repeating the 12-file write | **HIGH** | Wave 1 before any gate-based validation. |
| SQ-R-05 | `G-07`'s discovery sweep lands blocking and is disabled instead of the gaps being closed | **HIGH** | Observe-and-disclose first; the constraint is recorded by the owner and is non-negotiable. Note `ISD-G-09` would obstruct its own remedy and must be fixed in the same cycle. |
| SQ-R-06 | Reserved decisions (D-2, D-3) are executed as work by an agent rather than decided by the owner | **HIGH** | §5 standing constraint. Reserved ≠ backlog. |
| SQ-R-07 | `G-08`/`G-09` are forced closed by building an abstraction or declaring stages missing | **HIGH** | Wave 8 acceptance is a recorded *refusal to assess*. Located instrument: building one *"would be manufacturing evidence."* |
| SQ-R-08 | `G-10′`'s correction is not adopted and Wave 4 is over-scoped into a new governing instrument | **MEDIUM** | §1.1 records the measurement. Re-verify M-5..M-7 before scoping Wave 4. |
| SQ-R-09 | Parallel Wave 2 items are run concurrently by different sessions and collide | **MEDIUM** | Real and observed this session: a concurrent session committed seven commits during the prior pass. Serialize per-owner or declare owners disjoint before parallelizing. |
| SQ-R-10 | This sequencing is read as authorization | **HIGH** | Header disposition; §10 refusals; no wave carries an authorization. |
| SQ-R-11 | The predecessor's `G-10` is cited downstream after being refuted here | **MEDIUM** | §1.1 states the correction explicitly with commands. Where this and the located instrument differ, the instrument governs — and here the instrument is `constitution.py:386`. |
| SQ-R-12 | Certification is claimed per wave, accumulating unfounded state | **HIGH** | Only Waves 3, 5 and 9 have any certification in scope, each conditional on a non-vacuity proof. Six waves certify nothing. |

---

## 8 — Validation approach for the sequencing

| Obligation | Measurement |
|---|---|
| Wave 0 gate holds | `validate_rule_coverage(boundary)` returns `()`; `classify()` returns `CLASSIFIED` for ≥1 subject per declared class |
| Every gate is non-vacuous | Each new check is shown to **fail** on a synthetic violation before being trusted to pass — the discipline `ISD-L-06` already applies by performing an extension every run |
| No wave creates a parallel authority | `--check-no-parallel-authority` passes after each wave; no new engine, register, detector, lifecycle or identifier scheme appears |
| No identity minted across the programme | `00-BOOK/DATA/id-ledger.json` `by_path` count and `category_seq` unchanged unless an explicit `--mint` act is separately authorized |
| Reserved items stay reserved | D-2/D-3 remain undischarged until an owner decision is recorded; no artifact silently resolves them |
| Dependency order is respected | For each wave, its predecessors' closure criteria are satisfied and measured before it opens |
| Ordering is falsifiable | If any wave can be shown closable without its declared predecessor, that arrow is wrong and this determination is amended |
| No cardinality assertion | No test asserts 19 findings, 9 waves, 345 entries or 11 laws unless cardinality is itself the invariant |

---

## 9 — Acceptance criteria for this determination

1. All **19 findings** are placed in exactly one wave, each carrying all eight required determinations — dependency order, prerequisite decisions, canonical owner, authority requirement, reuse opportunity, implementation requirement, validation requirement, certification requirement. **Holds: G-01..G-19 plus `PA-G-04` placed across 9 waves.**
2. Every arrow in §2 is a hard prerequisite with a stated reason, not a preference. **Holds.**
3. Each of the seven stated priority axes is the rationale for at least one wave, and any inversion of the stated order is explained. **Holds — the `G-01` inversion is explained in §2.**
4. Every special-focus item has a determined position and rationale. **Holds — §6, all seven.**
5. Every inherited finding was re-measured at HEAD `bae59755`, and any that failed re-measurement is corrected with the command that refutes it. **Holds — `G-10` refuted in §1.1 with M-5..M-7.**
6. No finding standing as a **governed position** is sequenced as work. **Holds — `G-08`, `G-09`, `G-17`, `G-12` are Wave 8 declarations; `G-02`/`PA-G-04` are decisions.**
7. The bootstrap paradox in Wave 0 is named and dispositioned rather than glossed. **Holds — §3.**
8. No wave is authorized, no code changed, no registry or ledger written, no identity minted, no ADR created, no certification state altered. **Verified at close.**
9. Working tree entry count unchanged from session open. **Verified: 64 at open and close.**

---

## 10 — Refusals

- **Implementing, remediating or authorizing any wave.** Not performed. Sequencing is an ordering, not an authorization.
- **Resolving D-1 … D-8.** All eight recorded; none answered.
- **Deciding D-2 or D-3.** Reserved under `CEP-002` 14.2, and per `UCAF-F-003` not closable by measurement. They route to the human owner.
- **Executing `classify()` against a live `Repository` object.** My first invocation passed a `str` where a `Repository` is required and raised `AttributeError` — **that was my call-site error, not a repository defect.** The `ERROR` outage is therefore evidenced by `validate_rule_coverage` (M-1) and by the code path at `classify:427-436` (M-3, M-4), not by a successful end-to-end `classify()` call in this pass. The predecessor's three-subject `ERROR` measurement is cited as its evidence, not reproduced as mine.
- **Running any `*-gate` target**, including `ufc-gate`, `convergence-gate`, `requirement_engine.py --gate` and `closure_engine.py`. Refused: they write tracked registers, and `G-11` means it cannot be known in advance which do.
- **Re-deriving the predecessor's `G-10` through `G-19`.** `G-10` was re-measured because it is a special-focus dependency and it failed. `G-12`…`G-19` are carried at their owner's classification; their underlying code was not audited in this pass, so their **severities are inherited, not re-verified**.
- **Reading `foundation-convergence.json` beyond its model list.** Six models and the zero requirement/principle matches were measured; per-model subordinate declarations were not inspected, so D-7's scope cost is unestimated.
- **Asserting that closing every wave yields completeness.** Part 50 makes completion a moving fixed point; a closed wave set is closure of *these nineteen findings at this HEAD*, nothing more.

---

## 11 — Determination

**NINE WAVES. ONE HARD GATE. ONE INHERITED FINDING REFUTED, AND THE REFUTATION MAKES THE EXPENSIVE WAVE CHEAP.**

The sequencing is governed by a single structural fact that overrides the stated priority order: **mutation classification is non-functional for every artifact at this HEAD.** `validate_rule_coverage` returns one problem, `RULE_PREDICATES` implements eight of nine declared rules, and `classify()` evaluates coverage before its precedence loop — so the failure is total and fail-closed by design. Until that predicate exists, every corrective mutation made anywhere in the programme is unclassifiable, which means a cycle that closes governance gaps would itself be unable to demonstrate that its own edits were permitted. `G-01` is an implementation gap, the last of the seven stated priorities by class, and it is unavoidably first by dependency. Priority axes describe *why* to act; they cannot order *when*.

Wave 0 carries a paradox that must be stated rather than absorbed: the plane cannot authorize its own repair. The sound disposition is to authorize under `UCKP-LAW-0001`, which is upstream and unaffected, and to classify the repair's own changed paths as the first act after the fix — self-disclosing, never self-authorizing. And `G-01` is not closed by the predicate alone. The outage exists because a correct refusal was read by nothing; closing it without a consumer that fails on a non-`CLASSIFIED` status would reproduce the exact defect on its own fix.

The most useful result of re-measurement is that **`G-10` does not survive it.** `UFC-16` is not an unlocated rule with zero code references: it is declared at `platform/universal_foundation/constitution.py:386` with the gate `FG-16-ONE-MEASUREMENT`, implemented by `convergence.py`, populated by a catalog, and wired into `ufc-gate.yml`. What is true is narrower and more actionable — its declared population is six Foundation constitutional models, and the populations that actually diverge, requirements and principles, are not in it. That converts the most-cited authority gap into a population under-declaration, and it means the requirement reconciliation everyone has been treating as a fresh governing instrument is, once scope is corrected, **a relation declared into a population an existing CI gate already reads.**

Beyond that, the shape of the work is not what a nineteen-finding register suggests. Only three findings are true implementation gaps and one of those is a single function; a second, `G-05`, is a single absent deserializer gating three planes. The dominant pattern is supersession declared but not enforced, and the repository already holds a working enforcement precedent in `convergence-gate` that has never been generalized — which is why Wave 3 closes a class rather than three instances. Four findings must not be closed at all in the ordinary sense: two are reserved owner decisions and two are governed refusals whose correct outcome is a recorded declaration of unassessability.

**VERDICT: `SEQUENCING-COMPLETE · 19 FINDINGS ORDERED ACROSS 9 WAVES · 1 REFUTED AND RESTATED · 8 PREREQUISITE DECISIONS OPEN · NO WAVE AUTHORIZED`**

## Preservation

No artifact deleted, renamed or merged. No code, configuration, registry, ledger or declaration modified. No identity minted — `id-ledger.json` `by_path` 1264 and `page_cursor` 9826, unchanged. No programme ID, requirement or ADR created. No certification state altered. No certification claimed. Working tree entry count 64 at open and 64 at close.

## Stop

**Sequencing complete. No implementation.** Awaiting explicit authorization before Wave 0 or any subsequent wave, and awaiting owner decisions on D-1 … D-8. The reserved items (D-2, D-3) require a person, not a process.

---

*END · `UCOS-OMEGA-INFINITY-GAP-CLOSURE-SEQUENCING-DETERMINATION.md` · AUTHORITY = NONE (DERIVED TRUTH) · Where this determination and a located instrument differ, the located instrument governs.*
