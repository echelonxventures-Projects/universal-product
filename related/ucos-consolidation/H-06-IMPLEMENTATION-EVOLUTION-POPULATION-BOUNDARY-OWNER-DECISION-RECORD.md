# H-06 IMPLEMENTATION EVOLUTION POPULATION BOUNDARY OWNER DECISION RECORD

| Field | Value |
|---|---|
| **ID** | H-06-IEPBODR |
| **Authority** | OWNER DECISION PREPARATION ONLY. No option selected herein. No population adopted. No commit. No push. No staging change. No registry mutation. |
| **Phase** | Foundation Closure — Gate Purity — first implementation evolution population |
| **Decision Authority** | Mutation Governance Owner |
| **Resolves** | **P-1** — the committed population for the atomic evolution transaction |
| **Baseline** | HEAD `1f869865d5ff709c03cb4eb595524820d55d0be6` · branch `integration/recovery-001` · 0 commits |
| **Produced** | 2026-08-16 |
| **Status** | **DECISION ENTRY OPEN — NO SELECTION RECORDED — ONE FIELD UNMARKED** |

---

## 0. Measurement Correction Before the Decision Is Framed

**The second option must be labelled 88 paths, not 89.** The request names it the *"89-PATH FULL CAPABILITY
INTRODUCTION BOUNDARY"*. Direct set measurement returns **88**:

```
MIN boundary paths  : 74
FULL boundary paths : 88
delta               : 14   (11 UCKP + 3 UCF)
```

**Source of the error, disclosed.** Two prior determinations tabulated
`00-MASTER/UAUE-000001/` as **21** files. It carries **20** in the working-tree delta — 18 registers
(`00`–`17`) plus `UAUE-EVOLUTION-HISTORY.json` and `uaue-evolution.json`. UAUE's total is therefore **51**,
which those determinations also stated correctly elsewhere; the group table double-counted one file and
carried +1 into the aggregate. `H-06-UAIE-UAUE-RIB-ATOMIC-EVOLUTION-BOUNDARY-DETERMINATION.md` and
`H-06-IMPLEMENTATION-COMMIT-BOUNDARY-RECONCILIATION-DETERMINATION.md` both require this correction.

**Nothing else changes.** The delta between the options is exactly 14 paths, and every conclusion about
dependency closure, cycles, and intermediate states is unaffected. **§7.2 presents the option under its
measured count of 88.** No option is renamed to avoid the discrepancy — the discrepancy is reported.

---

## 1. The Two Populations, Measured

### 1.1 Common Core — 74 Paths, in Both Options

| Programme | Paths | Content |
|---|--:|---|
| **UAUE-000001** | **51** | 19 `engine/uaue/` modules · 20 `00-MASTER/UAUE-000001/` files · 6 `test_uaue_*` suites · `.github/workflows/uaue-gate.yml` · 2 root determinations · `verify.sh` · `Makefile` · `pyproject.toml` |
| **UCKP** | **1** | `engine/tests/uckp/test_evolution_rehydration.py` — run by UAUE's own workflow, **absent at HEAD** |
| **UAIE-000001** | **6** | 5 regenerated registers + `uaie.json` |
| **UCOS-RIB-001** | **5** | `UCOS-RIE-{CAPABILITY-CATALOG,MODEL,SNAPSHOT,HEALTH}.json` · `UCOS-IMP-BASELINE-001.rib.json` |
| **UCOS-UGA-001** | **9** | 7 JSON registers + dashboard + existence inventory |
| **Projections** | **2** | `generated-artifact-registry.json` · `id-ledger.json` |
| **Total** | **74** | |

### 1.2 The 14-Path Delta — In the 88 Option Only

| Owner | Paths | Files |
|---|--:|---|
| **UCKP** | **11** | `engine/uckp/__init__.py` · `evolution.py` · `intelligence.py` · `resolution.py` · `uga_projection.py` · `engine/tests/uckp/conftest.py` · `test_assimilation.py` · `test_category_integrity.py` · `test_category_ownership_resolution.py` · `test_cli_and_package.py` · `test_uga_projection.py` |
| **UCF / provider** | **3** | `platform/tests/test_{commercial,repository_intelligence,universal_provider}_cli.py` |

### 1.3 Excluded From Both Options

| Excluded | Count | Reason |
|---|--:|---|
| H-06 governance documents | 68 | **0 of the 59 registered objects.** Separate H-06-owned commit |
| `…OWNER-DECISION-RECORD.md.save` | 1 | editor artifact — delete, never commit |
| `constitutional-authority-alignment.json` | 1 | **AT-2 unresolved** — 2 of the 59 in its delta, bulk unrelated |
| `canonical-observation-audit.json` · `ucaf-authority.json` | 2 | 0 uaue tokens · 0 of the 59 |
| `00-MASTER/UAKOS-CLOSURE-008/` | 3 | 0 of the 59 |
| Other root governance `.md` | ~33 | separate programmes; several pending rebase under finding F-1 |
| UICM · UICO · `engine/uicm/` | 3 entries / 44 files | separate programmes; 0 of the 59 |

---

## 2. Criterion 1 — Dependency Closure

| Edge | Requirement | 74 | 88 |
|---|---|:--:|:--:|
| E1 `engine/uaue` → RIB catalog | catalog regenerated with `engine.uaue` present | **YES** | **YES** |
| E2 catalog → UAIE `UAIE-REG-09` | `121 → 122`, seal rotation | **YES** | **YES** |
| E3 UAIE → O1 → Epoch 6 B→A | UAIE registers committed | **YES** | **YES** |
| E5 paths → id-ledger | identity minted for committed paths | **YES** | **YES** |
| E6 paths → UGA registries | objects admitted | **YES** | **YES** |
| E7 UAUE surface → artifact registry | 19 entries | **YES** | **YES** |
| E9 UAUE CI → `test_evolution_rehydration.py` | test present at that HEAD | **YES** | **YES** |
| E10 UAUE → `verify.sh` · `Makefile` · `pyproject.toml` | UAUE-GATE-09 satisfiable | **YES** | **YES** |
| **E8 UAUE → UCKP stage set** | symbols UAUE imports must resolve | **SATISFIED AT HEAD** | **YES** |

**E8 measured at HEAD.** Every symbol `engine/uaue` imports from UCKP already exists in HEAD:
`EVOLUTION_CYCLE`, `EvolutionLedger`, `EvolutionRecord`, `is_terminal`, `next_stage` in `evolution.py`;
`content_hash`, `canonical_json` in `canonical.py` (**clean**); `LIFECYCLE_STAGE_VOCABULARY`, `Term` in
`vocabulary.py` (**clean**). The `evolution.py` delta adds only `LEDGER_SCHEMA` and `LEDGER_VERSION`, which
UAUE does not import.

**Both options achieve dependency closure. This criterion does not discriminate.**

---

## 3. Criterion 2 — Canonical Registry Consistency

This is the criterion on which the options differ most.

### 3.1 The 59 Registered Objects Against Each Boundary

| Boundary | Objects inside | Objects registered but **not committed** |
|---|--:|--:|
| **74** | 47 | **12** — 4 legitimate back-registrations + **8 that would be defects** |
| **88** | 55 | **4** — back-registrations only |

### 3.2 The Eight

Under the 74 option these are registered by the current projections but excluded from the commit:

```
engine/uckp/resolution.py
engine/uckp/uga_projection.py
engine/tests/uckp/test_category_integrity.py
engine/tests/uckp/test_category_ownership_resolution.py
engine/tests/uckp/test_uga_projection.py
platform/tests/test_commercial_cli.py
platform/tests/test_repository_intelligence_cli.py
platform/tests/test_universal_provider_cli.py
```

### 3.3 The Four — Legitimate Under Both

```
PHASE-P0-CLOSURE-DETERMINATION.md
PHASE-P0-CLOSURE-REMEDIATION-DETERMINATION.md
PHASE-P0-FINAL-CLOSURE-DETERMINATION.md
PHASE-POST-FREEZE-EVOLUTION-READINESS-DETERMINATION.md
```

All four are **present in HEAD and clean in the working tree** — back-registration for already-committed
files, correct in either option.

| | 74 | 88 |
|---|---|---|
| Registry consistency as the tree stands | **NO — regeneration mandatory** | **YES — projections already correct** |
| Additional producer runs required | **`ukb.py` and UGA regeneration** | **none** |

---

## 4. Criterion 3 — `id-ledger` Correctness

| Property | 74 | 88 |
|---|---|---|
| Current `by_object` delta | +59 — **8 too many** | +59 — **exactly right** |
| Correct delta for the option | **+51** | **+59** |
| Action required | **regenerate**, then re-verify `by_path` still byte-identical and `category_seq` monotonic | **none** |
| Append-only compliance | preserved by regeneration (`ukb.py` appends; retired identities remain `RETAINED-BUT-RETIRED`) | already compliant — **0 removals** |
| Risk | a regeneration that produced 51 must be re-measured; the five `category_seq` counters (`CONFIG 29→30` · `DATAOBJ 109→111` · `ENGINE 1187→1208` · `EXDOC 2390→2412` · `TESTOBJ 801→814`) will differ | none |

**Neither option breaches append-only.** Regeneration under the 74 option appends fewer identities; it does
not remove any.

---

## 5. Criterion 4 — UGA Object Registry Correctness

| Property | 74 | 88 |
|---|---|---|
| Current deltas | executable `4552 → 4611` (+59) · universal `5785 → 5844` (+59) · existence `5785 → 5844` (+59) | same |
| Correct for the option | **+51 in all three** | **+59 in all three — as measured** |
| Action required | **regenerate all three** | **none** |
| Ledger↔UGA set identity | must be **re-established** at 51 | **already holds at 59 — symmetric difference 0** |

**The set identity is the strongest single piece of evidence in this chain, and the 88 option preserves it
as measured.** Under the 74 option it must be re-proved after regeneration.

---

## 6. Criteria 5–7

### 6.1 Criterion 5 — Replay Determinism

| Programme | Mechanism | 74 | 88 |
|---|---|:--:|:--:|
| UAUE | `--replay`, read-only | **exit 0 today** | **exit 0 today** |
| UAIE | `make uaie-replay` — renders then diffs | **unproven (U-3)** | **unproven (U-3)** |
| RIB catalog | `make rib` | reproducible once `engine/uaue` is committed | same |
| UGA | regeneration | **must be re-run** | as measured |

Carried defects, identical under both: **U-1** UAIE's `input_closure` names only its declaration and omits
the catalog that drives its output; **U-2** the catalog's closure says *"tracked corpus at HEAD"* while
`git ls-files` reads the **index**.

**Discriminator: the 74 option adds two further producer runs (ledger, UGA) whose outputs are not yet
measured, so its determinism is asserted rather than observed. The 88 option's projections have been
measured in their committed-candidate form.**

### 6.2 Criterion 6 — Ownership Boundaries

| | 74 | 88 |
|---|---|---|
| Programmes in the commit | **6** — UAUE · UCKP(1) · UAIE · RIB · UGA · projection producers | **7** — adds UCF |
| Attribution clarity | **stronger** — only the paths UAUE's gate actually requires | weaker — carries UCKP and UCF work with no causal link to `engine/uaue` |
| Does it commit another programme's unrelated work? | **NO** | **YES** — 11 UCKP paths and 3 UCF paths, none required by any edge |
| Split-programme hazard | UCKP remains split: 5 of its 6 staged paths deferred, `__init__.py` unstaged | **resolved** — UCKP lands whole, `__init__.py` with the `resolution.py` it exports |

**This criterion favours the 74 option on attribution and the 88 option on internal coherence of UCKP.**
The `__init__.py` coupling is the concrete cost of the 74 option: it leaves UCKP staged-but-partial, which
its owner must then unstage or complete separately.

### 6.3 Criterion 7 — Future Evolution Impact

| | 74 | 88 |
|---|---|---|
| Precedent set | *the committed population is the causal closure of the capability, nothing more* | *the committed population is whatever the projections happened to observe* |
| Effect on the 46-target denominator | **identical** — `9 + 14 + 23 = 46` either way; `uaue-gate` is the only new `*-gate` target | identical |
| Effect on Freeze F-5 | **identical** — disposition recorded at delta E-4 |
| Deferred work | 14 paths remain uncommitted, needing a later UCKP/UCF commit and a further ledger/UGA regeneration | none deferred |
| Number of future regenerations | **more** — every deferred commit re-triggers the projections | **fewer** |
| Risk of recurrence of this exact situation | **higher** — a partially-registered corpus is the condition that produced this transaction | **lower** |

**The 88 option reduces future regeneration churn; the 74 option sets the tighter precedent for what a
capability commit is allowed to contain.** Both leave the denominator and F-5 untouched.

---

## 7. Owner Decision Field

**ENTRY STATE: NO SELECTION RECORDED.** The field is unmarked. No value has been pre-filled, inferred,
defaulted, or derived. **No section of this record states a preferred option** — §§2–6 present measured
evidence on both sides, and the criteria split: 2 and 3 and 4 and 5 favour 88; 6 splits; 7 splits.

### 7.1 Decision 1 — Implementation Evolution Population

Exactly one option. Basis: §1–§6.

**Selection:**
```
[ ] 74-PATH MINIMUM EXECUTION BOUNDARY — the causal closure of engine/uaue only; requires regeneration of
    id-ledger.json and the UGA registers to a +51 population before commit

[ ] 88-PATH FULL CAPABILITY INTRODUCTION BOUNDARY — adds 11 UCKP paths and 3 UCF paths; the current
    projections are already correct for it and require no regeneration
```

**§7.2 — Note on the option label.** The request named the second option *"89-PATH"*. The measured count is
**88** (§0). The field above uses the measured figure. **If the owner intends a population of 89 paths,
that is a third population and must be transmitted with its 89th path named** — it will not be inferred.

### 7.3 Rationale — owner's own words, required

________________

### 7.4 Included Programmes — as understood by the owner

________________

### 7.5 Excluded Programmes — as understood by the owner

________________

### 7.6 Migration Implications — actions the owner accepts as consequent

________________

---

## 8. Mandatory Acknowledgements

```
[ ] Selecting a population resolves P-1 only. It authorizes no commit, no push, and no staging change.
    The commit remains gated on P-2 restaging, P-3 projection regeneration, P-4 the UAIE replay proof,
    P-5 the push strategy, and P-8 the transaction authority.

[ ] AT-1 remains OPEN: no declared authority owns a cross-class transaction boundary. Per UCKP-ART-02 the
    transaction category has no constitutional existence, so closure requires a canonical object minted
    through the Constitutional Mutation Gateway — an owner act outside H-06's scope.

[ ] If the 74-path option is selected, id-ledger.json and the UGA registers as they currently stand are
    INCORRECT for it: they register 8 objects that would not be committed. Regeneration is mandatory
    before any commit, and the ledger↔UGA set identity must be re-proved at the new population.

[ ] Neither option clears any CIEP v2 Phase 0 condition. 0.5 and 0.6 remain FAIL, and 0.3 fails when the
    transaction lands until re-confirmed under B-1.

[ ] The accepted denominator 9 + 14 + 23 = 46 and the Freeze F-5 disposition for uaue-gate are identical
    under both options and are unaffected by this selection.

[ ] The 68 H-06 governance documents are excluded from both populations and belong to a separate
    H-06-owned commit; the .save artifact is to be deleted, not committed.
```

---

## 9. Signature Fields

**Decision Authority:** Mutation Governance Owner

**Selected By:**
________________

**Date:**
________________

**Signature:**
________________

**Evidence Reference:** `H-06-IMPLEMENTATION-COMMIT-BOUNDARY-RECONCILIATION-DETERMINATION.md` ·
`H-06-UAIE-UAUE-RIB-ATOMIC-EVOLUTION-BOUNDARY-DETERMINATION.md` ·
`H-06-ATOMIC-EVOLUTION-TRANSACTION-AUTHORITY-DETERMINATION.md` — **each requiring the §0 correction from
89 to 88.**

**Constraint:** No mark in §7 and no signature here authorizes a commit, a push, a staging change, a
registry mutation, or implementation.

### 9.1 Completion Requirement

| # | Condition | Current |
|---|---|--:|
| 1 | §7.1 carries exactly one mark | **0 of 1** |
| 2 | §7.3 rationale populated | **blank** |
| 3 | §7.4 included programmes populated | **blank** |
| 4 | §7.5 excluded programmes populated | **blank** |
| 5 | §7.6 migration implications populated | **blank** |
| 6–11 | Six §8 acknowledgements marked | **0 of 6** |
| 12 | `Selected By` populated | **blank** |
| 13 | `Date` populated | **blank** |
| 14 | `Signature` populated | **blank** |

**0 of 14 satisfied.** A partially marked entry records no decision; mixed states are not interpolated, and
no determination may populate any field. **Transmit a literal value for every field — a placeholder or an
option pair in a value position will be rejected and nothing will be inferred**, per entries E-1, E-2 and
E-3 on the UAUE denominator delta record.

---

## 10. Decision Entry Log

| # | Date | Authority | Fields transmitted | Marks received | Recorded | Entry state |
|---|---|---|---|---|---|---|
| — | — | — | — | — | **NO ENTRY PROCESSED** | — |

**Cumulative: 0 entries · 0 marks · 0 of 1 fields selected · entry OPEN.** No decision is inferred; an
unpopulated field is not a decision, per the IADR §8 precedent applied throughout this chain.

### 10.1 Non-Entry Actions

| # | Date | Authority | Action | Fields touched | Marks changed |
|---|---|---|---|---|---|
| P-1 | 2026-08-16 | "OWNER DECISION PREPARATION ONLY" | Record prepared; both populations measured by direct set arithmetic; the 89→88 correction disclosed; one field presented unmarked | **NONE** | **NONE — 0 before, 0 after** |

---

## 11. Record State Attestation

| Property | State |
|---|---|
| Fields presented | 1 decision · 4 narrative · 6 acknowledgements · 3 signature |
| Decision fields marked | **0 of 1** |
| Acknowledgements marked | **0 of 6** |
| Narrative fields populated | **0 of 4** |
| `Selected By` · `Date` · `Signature` | **blank · blank · blank** |
| Entries processed | **0** |
| Decision entry state | **OPEN** |
| Recommendations stated in this record | **NONE** — the criteria split, and §§2–6 report that split without resolving it |
| Population adopted | **NONE** |
| Measured populations | **74** and **88** — delta **14** (11 UCKP + 3 UCF) |
| Prior "89" figure | **CORRECTED to 88** — §0; three determinations require the correction |
| Commit authorized | **NO** |
| Phase 0 | **4 of 6 — 0.5 and 0.6 FAIL, unaffected by this record** |
| Open items not addressed here | **AT-1** transaction authority · **AT-2** `constitutional-authority-alignment.json` · **P-2** restaging · **P-3** projection regeneration · **P-4** UAIE replay proof · **P-5** push strategy · **U-1 · U-2 · U-3** · **F-1** R-1/R-2 rebase · **CN-1** R-4 §7 annotation |
| Repository mutation performed | **NONE** — 0 commits · 0 pushes · 0 staging changes · no registry, declaration, or engine write · `verify.sh` not run · no producer run |

*This document is an owner decision preparation artifact. It selects no population, states no
recommendation, and confers no authority. It measures both candidate boundaries by direct set arithmetic,
corrects the prior 89-path figure to 88 with the source of the error named, evaluates all seven criteria and
reports that they split — registry consistency, ledger and UGA correctness and observed determinism favour
the larger population, while attribution favours the smaller — and presents one empty field for the
Mutation Governance Owner. Until §7.1 carries a mark, §§7.3–7.6 are populated, §8 carries six
acknowledgements and §9 attribution, date and signature, no population is adopted and the commit boundary
remains open. HEAD remains `1f869865` on `integration/recovery-001`.*

---

Implementation evolution population boundary prepared.
Two populations measured: **74** and **88**.
No selection recorded.
No commit executed.
No push executed.
No staging change performed.
No registry mutation performed.
