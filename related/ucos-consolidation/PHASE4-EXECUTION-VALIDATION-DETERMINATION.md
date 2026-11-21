# PHASE 4 — EXECUTION VALIDATION DETERMINATION

| Field | Value |
|---|---|
| Question | What exact execution program transforms **READY-CONDITIONAL-ON-GOVERNANCE-SELECTION** into **READY-FOR-EXECUTION**, without introducing any new blocker? |
| Answer | **YES — READY-FOR-EXECUTION is reachable, under all 12 admissible models, with ZERO mutating runs**, because every precondition for execution is verifiable read-only. Executing *from* that state and closing UK-1/UK-2 then requires **exactly 2 mutating runs**, **14 runtime validations** and **3 rollback procedures**. |
| Inputs | `PHASE0-GOVERNANCE-INDEPENDENT-DETERMINATION.md`, `PHASE05-GOVERNANCE-INDEPENDENT-REMEDIATION.md`, `PHASE1-GOVERNANCE-INDEPENDENT-IMPLEMENTATION-REPORT.md`, `PHASE2-GOVERNANCE-CLOSURE-DETERMINATION.md`, `PHASE3-IMPLEMENTATION-READINESS-DETERMINATION.md` |
| Code changed | **NONE.** No repository file modified. This document is the only file written. |
| Governance selected | **NONE.** Rule 4 assumed satisfied abstractly: results hold for **any** of the 12, and where an axis value changes an execution requirement it is recorded per-value without preference. |
| Implementation content | **NONE recommended.** §D and §E state what must be *executed and verified*, never how any task should be written. |
| Live ledger | unchanged — `sha256 8471e709b178a9a09909bca55f2e8eccb78161db8423026d1d26e4f35c41c20b`; `git status --porcelain 00-BOOK/DATA/` empty before and after every probe |
| Baseline | working tree at `77798202`; `ledger_authority.py` 933 lines, **`AM` — staged, never committed, absent from HEAD** (§F.2 makes this load-bearing) |

### Compliance with the stated rules

| Rule | Compliance |
|---|---|
| 1. Do not implement code | No source file modified. Every probe **P4-1 … P4-11** is read-only or operates on in-memory `deepcopy` objects. |
| 2. Do not modify repository files | This document is the only addition. Verified: ledger sha256 identical, all four guard directories `0` dirty entries, register still absent. |
| 3. Do not select a governance model | No axis assigned. Where axis `B` or `Aud` changes an execution or rollback requirement, both/all values are stated (§D.4, §F.4, §G). |
| 4. Assume one of the 12 chosen | Assumed abstractly. §C.0 states which requirements are model-invariant (the majority) and which are axis-parameterized. |
| 5. Separate measured fact / inference / unknown / execution requirement | Four-way tagging defined in §0.1 and applied inline as **[MEASURED]**, **[INFERRED]**, **[UNKNOWN]**, **[EXEC-REQ]**. |
| 6. Every statement traceable | §K maps every load-bearing claim to a `file:line` read this phase, to a probe **P4-n** executed this phase, or to a named prior-phase measurement. |
| 7. Do not recommend governance | None. No axis value is preferred, ranked or described as better. |
| 8. Do not recommend implementation content | §D and §E enumerate validations and their pass/fail conditions. No task's content, design or code is proposed. |
| 9. Determine only what must be executed and verified | The scope of §C–§J. |

---

## 0. Frame

### 0.1 Evidence classes

Rule 5 requires four distinct classes. Used literally throughout:

| Tag | Meaning |
|---|---|
| **[MEASURED]** | Established by execution or source read **this phase**, or by a named prior-phase measurement. A fact. |
| **[INFERRED]** | Derived from measured facts by an argument stated at the point of use. Not itself measured. |
| **[UNKNOWN]** | Not established, and stated as such. No inference is offered as a substitute. |
| **[EXEC-REQ]** | A thing that must be run or verified. Not a fact about the present state — a requirement on the program. |

### 0.2 What "READY-FOR-EXECUTION" is, stated before it is answered

The target state must be defined before reachability can be determined, and the obvious reading is wrong in a way that changes the answer.

**Wrong reading:** READY-FOR-EXECUTION = UK-1 and UK-2 closed. Under this reading the question is trivially self-defeating, because closing them *is* the execution.

**Correct reading, and the one used here:** READY-FOR-EXECUTION is the state in which **every precondition of the mutating runs is satisfied and verified**, so that execution may commence with a determinate outcome. UK-1 and UK-2 are closed **by** execution, not **before** it.

This distinction is what separates Phase 4's **YES** from Phase 3's **NO**. Phase 3 asked whether readiness could be *unconditional* and answered NO, on three grounds of which two were UK-1 and UK-2. Phase 4 asks whether the *execution gate* can be reached — a weaker and, as §I.3 determines, achievable target. **The two answers do not conflict; they answer different questions.**

```
  PHASE 3 terminal state            PHASE 4 target                  PHASE 4 outcome
  ────────────────────────          ──────────────────              ───────────────
  READY-CONDITIONAL-ON-      ──►    READY-FOR-EXECUTION      ──►    EXECUTED
  GOVERNANCE-SELECTION              (all preconditions               (UK-1, UK-2
                                     verified; 0 mutating             closed; 2
  0 blockers                         runs to reach)                   mutating runs)
  3 residuals                        0 blockers                      0 blockers
  2 unknowns                         3 residuals                     3 residuals
                                     2 unknowns                      0 unknowns
```

---

## A. Current state recap

Exact counts carried from `PHASE3:§G.1`, each re-verified open this phase.

```
CLOSURE MODELS (admissible) ...................................  12
    I-R × A3 × {B1,B2} × {D1,D2} × {Aud1,Aud2,Aud3}      (Z-01 … Z-12)

IMPLEMENTATION TASKS
    distinct across all 12 .................................... 24
    forced (all 12) ........................................... 13
    optional (3–6 models each) ................................ 11
    required by exactly one model ..............................  0
    per-model ............................................. 17 – 20
    migration ..................................................  0

BLOCKERS
    today, artifact level ......................................  5   E-4A, E1-F3, E-3, RES-1, RES-2
    after governance closure, decision level ...................  0
    after governance closure, artifact level ...................  5
    after implementation completion ............................  0

RESIDUALS ......................................................  3   RES-3, RES-4, R-7w
    closed by any of the 12 ....................................  0
    activated (latent → live) by all 12 ........................  3

UNKNOWNS .......................................................  2   UK-1, UK-2
```

**Re-verified this phase, read-only, ledger byte-identical throughout:**

| Fact | Evidence |
|---|---|
| Register absent; all three `permit` values refused on a real allocating manifest | **[MEASURED]** `PHASE3` P3-1, re-confirmed: `ls 00-BOOK/DATA/allocation-permits.json` → *No such file* |
| `UGA-INV-01` and `UGA-INV-10` both FAIL at **violations=27**, identical sets; **2 of 30** invariants FAIL; `GATE FAILED` | **[MEASURED]** **P4-4**, `uga_engine.py gate` executed this phase |
| Phase-1 authority suite green | **[MEASURED]** `PHASE3` P3-8 — 77 passed |
| All four guard directories clean at HEAD | **[MEASURED]** **P4-9** — `00-BOOK/DATA` 0, `REGISTRIES` 0, `CONTROL-TOWER` 0, `PORTAL` 0 dirty entries |

---

## B. Unknown inventory

### B.1 UK-1 — `register.sh` end-to-end completion

| Aspect | Determination |
|---|---|
| **Definition** | Whether `register.sh` Phase 1 (`ukb build --mint`) completes once a permit verifies, and whether the nine subsequent `\|\| fail`-gated phases then pass, sealing the REG-AUTO-001 transaction. |
| **Source** | `PHASE0-E4A-ISSUANCE-PATH-REPORT.md:§7`; carried by `PHASE2:§F.6` and `PHASE3:§E.4`. |
| **What is established** | **[MEASURED]** `00-BOOK/tools/register.sh:216` is `"$PY" "$HERE/ukb.py" build --mint \|\| fail "ukb build failed" 1` — **no `--permit`**. `fail()` at `:201` ends in `exit "${2:-1}"`. Phases 2/10–9/10 at `:221`–`:259` are each `… \|\| fail …`. `set -euo pipefail` at `:48`. So a Phase-1 failure terminates the transaction and **nine** phases never execute. |
| | **[MEASURED]** the population Phase 1 would mint: **9 `by_path` identifiers**, all root-level `.md` files (**P4-2**), with `page_cursor:12507->12612` and 7 `category_seq` advances (**P4-3**). |
| **What is unknown** | **[UNKNOWN]** Everything downstream of a successful Phase 1: whether `ukbx sync --due`, `ukbx twin`, `ukbx portal`, `ukb validate`, `ukbx validate`, `ukbx twin --check`, `ukbx certify` and `ukb enforce` all pass against the post-mint state. |
| **Why unresolved** | Declined four consecutive times for one consistent reason — the run mutates. `PHASE0-E4A:§7` (*"`register.sh` was **not** executed"*), `PHASE1:§5.1` (*"`commit()` was **never** called against the production ledger"*), `PHASE2:§H.1` (*"No new probe was run"*), `PHASE3:§H.1`. This phase also declines. |
| **Why static analysis cannot close it** | Three independent reasons, each measured rather than asserted. **(i) The gate predicates read post-mutation state.** Phase 5 `ukb validate` asserts *"append-only page ledger intact, referential integrity OK"* over `artifacts.json` **as written by Phase 1**; that document does not exist in its post-mint form until Phase 1 writes it. **(ii) Nine phases are transitively gated.** Whether Phase 6 passes is a function of what Phase 2 wrote, which is a function of what Phase 1 wrote. Static analysis can establish each predicate's *form*, never the *value* of an input that no artifact holds. **(iii) `--plan` covers exactly one of the ten phases.** **[MEASURED]** `--plan` exists on `ukb build` (`ukb.py:2501`) and `uga_engine run` (`uga_engine.py:2181`) and **nowhere in `ukbx.py`** (**P4-6**) — so phases 2, 3, 4 and 8 have no dry-run mode at all. |

### B.2 UK-2 — post-mint anonymous-object clearance and gate greenness

| Aspect | Determination |
|---|---|
| **Definition** | Whether the anonymous-object population clears in one mint and `cmd_gate` reaches PASS on all 30 invariants. |
| **Source** | Premise from `PHASE2:§F.1` and CY-3; named as a distinct unknown in `PHASE3:§E.5`. |
| **What is established** | **[MEASURED]** **P4-4**, this phase: `UGA-INV-01 FAIL violations=27 measured=6804`; `UGA-INV-10 FAIL violations=27 measured=5207`; identical violation sets; **2 of 30** FAIL; `GATE FAILED — 2 blocking invariant(s)`. `cmd_gate` blocks on every failing invariant (`uga_engine.py:2128-2136`). |
| | **[MEASURED]** `00-BOOK/tools/ledger_authority.py` — Phase 1's own deliverable — is itself one of the 27. CY-1 observed live. |
| **What is unknown** | **[UNKNOWN]** Whether one mint clears all of them, and whether the remaining 28 passing invariants stay passing after the ledger moves. |
| **Why unresolved** | Same mutating-run requirement, plus a second reason established this phase: **the population is not stable.** |
| **Why static analysis cannot close it** | **The decisive reason is measured, and it is stronger than "requires a run."** **[MEASURED]** **P4-10**: all **17** files under `00-BOOK/DATA/*.json` are in `by_object`, and **0** of them are eligible for `by_path` — `ukb._iter_files` excludes the generator's own machinery and outputs (`tools/`, `DATA/`, `REGISTRIES/`, `CONTROL-TOWER/`, `VOLUMES/`, `PORTAL/`) because *"the registry must not list itself"* (`ukb.py:828-833`). The permit register is a new `00-BOOK/DATA/*.json`. **[INFERRED]** Therefore committing it makes it the 18th such file and grows the anonymous population from **27 to 28** — while leaving Phase 1's population at **9**. The number a static analysis would predict is a function of an implementation artifact that does not exist yet, and it changes as a *consequence of the program's own steps*. |

### B.3 The two unknowns are discharged by two different commands

This is the sharpest finding of this phase and it is measured, not inferred.

| | UK-1 | UK-2 |
|---|---|---|
| **Discharging command** | `00-BOOK/tools/register.sh` | `00-MASTER/UCOS-UGA-001/uga_engine.py run --mint` |
| **Ledger map allocated** | `by_path` | `by_object` |
| **Population** | **9** (→ 9; register excluded) | **27** (→ 28 once the register is committed) |
| **Invoked by `register.sh`?** | yes, Phase 1 | **NO** |

**[MEASURED] `register.sh` never invokes `uga_engine`** (**P4-1**): the only occurrence of the string in the file is a prose note at `:157`, and neither `ukb.py` nor `ukbx.py` imports it — the sole mention is a docstring cross-reference at `ukb.py:884`.

**[MEASURED] The two populations are disjoint** (**P4-5**): `|ukb_by_path_gap ∩ uga_anonymous| = 0`.

**[INFERRED] Consequence:** neither run clears the other's gap; **neither is redundant; both are required.** Any execution program with fewer than two mutating runs cannot close both unknowns. This is the basis of the minimum in §E.

---

## C. Execution dependency graph

### C.0 Model-invariance of the graph

**[INFERRED]** from `PHASE3:§C` and `§D`: the graph below is **identical under all 12 admissible models**, because every node is either a forced task (13, present in all 12), a governance-selection node, or a validation over a surface no axis value relocates. Axis values change **task content**, not graph topology — with one exception, recorded at edge **E-7**.

### C.1 The graph

```
                        ┌───────────────────────────┐
                        │ G  GOVERNANCE SELECTION   │  5 closure axes
                        │    (Rule 3: not made here)│  → one of Z-01 … Z-12
                        └─────────────┬─────────────┘
                                      │ E-1  hard: task content is undefined until selected
              ┌───────────────────────┼───────────────────────┐
              ▼                       ▼                       ▼
   ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐
   │ F-2 · F-3          │  │ F-5 · F-6 · F-12   │  │ O-1…O-8, O-10, O-11│
   │ A3 document        │  │ E-3 disposal       │  │ axis-conditional    │
   │ binding            │  │ (uga_engine        │  │ (4–7 per model)     │
   │ (manifest_digest,  │  │  :1331-1335,       │  └──────────┬─────────┘
   │  plan)             │  │  declaration)      │             │
   └─────────┬──────────┘  └─────────┬──────────┘             │
             │ E-2  HARD                                       │
             │ A3 changes every manifest_digest (:548-568)      │
             │ and what plan() emits (:648-661).  Issuing       │
             │ permits first invalidates them.                  │
             ▼                                                  │
   ┌────────────────────┐                                       │
   │ F-1  REGISTER      │                                       │
   │      PRODUCER      │                                       │
   └─────────┬──────────┘                                       │
             │ E-3  hard: nothing to plumb until it exists       │
             ▼                                                  │
   ┌────────────────────┐        ┌──────────────────────────┐   │
   │ F-4  register.sh   │        │ E-7  O-9 (Aud1 tracked   │   │
   │      permit        │        │      audit log) MUST     │◄──┘
   │      plumbing      │        │      follow F-1  (CY-1)  │
   └─────────┬──────────┘        └────────────┬─────────────┘
             │                                │
             │        E-4  HARD, DERIVED THIS PHASE
             ▼        commit the register before the drift gate can pass
   ┌──────────────────────────────────────────────────────────┐
   │ C-1  COMMIT the register (and any new tracked artifact)   │
   │      [EXEC-REQ]  register.sh's drift check counts `??`    │
   │      untracked entries under 00-BOOK/DATA as DRIFT        │
   └─────────────────────────┬────────────────────────────────┘
                             │ E-5  consequence: UGA population 27 → 28
                             ▼
   ┌──────────────────────────────────────────────────────────┐
   │ STAGE 0 — PRE-MUTATION VERIFICATION      V-1 … V-6        │
   │ entirely read-only.  Reaching the end of this stage IS    │
   │ READY-FOR-EXECUTION.                                      │
   └─────────────────────────┬────────────────────────────────┘
                             │ E-6  HARD SERIALIZATION, MEASURED (P4-7)
                             │ preimage_digest is a digest of the WHOLE ledger,
                             │ so run A landing moves run B's binding.
                             │ Permits CANNOT both be issued up front.
              ┌──────────────┴──────────────┐
              ▼                             ▼
   ┌────────────────────┐        ┌────────────────────┐
   │ STAGE 1  RUN A     │        │ STAGE 2  RUN B     │   order between A and B
   │ register.sh        │───────►│ uga_engine run     │   is FREE; each must be
   │ 10 phases, 9 mints │ E-6    │ --mint, 28 mints   │   measure→issue→run
   │ → closes UK-1      │        │ → closes UK-2      │
   └─────────┬──────────┘        └─────────┬──────────┘
             └───────────┬──────────────────┘
                         ▼
   ┌──────────────────────────────────────────────────────────┐
   │ STAGE 3 — POST-MUTATION CONFIRMATION     V-12 … V-14      │
   └──────────────────────────────────────────────────────────┘
```

### C.2 Ordering constraints, each with its basis

| Edge | Constraint | Class | Basis |
|---|---|---|---|
| **E-1** | Governance selection precedes every task | hard | `PHASE3:§C` — 4–7 of 17–20 tasks per model are axis-conditional |
| **E-2** | `A3` binding (F-2, F-3) precedes register production (F-1) | hard | `PHASE2:§E.2`; `PHASE3:§C.5`. `:548-568`, `:648-661`. **[MEASURED]** free of cost today — zero permits exist |
| **E-3** | F-1 precedes F-4 | hard | **[INFERRED]** trivially: a permit cannot be routed to a call site before any permit can exist |
| **E-4** | The register must be **committed** before the drift gate can pass | hard, **derived this phase** | **[MEASURED]** `register.sh:125` — the `--observe` drift filter is `substr($0,1,2) == "??" \|\| substr($0,2,1) != " "`, so an untracked new file under `00-BOOK/DATA` is DRIFT → `RC=3`. `--guard` at `:265-267` uses bare `git status --porcelain` over the same four paths, which also lists `??` |
| **E-5** | Committing the register grows the UGA population 27 → 28 | consequence, not a choice | **[MEASURED]** **P4-10**; **[INFERRED]** as stated in §B.2 |
| **E-6** | Permits must be issued **sequentially**, one per mutating run, each after the prior run lands | hard | **[MEASURED]** **P4-7**: `preimage_digest(P0)=3a2a2532…` → `preimage_digest(P1)=0b7a886d…` after the 9 `by_path` allocations land, while `manifest_digest` does **not** move. `_verify_permit :743-749` refuses on pre-image mismatch. So a permit issued for run B at P0 is refused after run A lands, on the pre-image binding alone |
| **E-7** | Under `Aud1` only, O-9's tracked audit log must follow F-1 | hard, 4 of 12 models | `PHASE3:§C.5`; CY-1 terminated at one file at `:499-506` |
| **A ↔ B** | The order of run A and run B relative to each other | **FREE** | **[MEASURED]** **P4-5** — populations disjoint (overlap 0), and **P4-1** — neither command invokes the other. Only E-6's serialization applies |

**No cycle exists in the graph.** **[INFERRED]** E-1…E-5 form a chain, E-6 orders the two runs pairwise, E-7 attaches to one branch. CY-1 is terminated at one file by construction (`:499-506`) and E-4/E-5 record its one traversal rather than a loop.


---

## D. Validation inventory

### D.0 Mutation classification of every `register.sh` phase — measured

This table is the foundation of §E's minimality argument and §F's rollback scope. Every cell was established by source read this phase.

| Phase | Command | Writes **tracked** state | Writes **untracked runtime** state | Evidence |
|---|---|---|---|---|
| **0/10** | `ukb enforce --pre` | **no** | **yes** — `enforcement-audit.json`, `mode=pre` | `cmd_enforce` → `_enforcement_audit` → `T.append_audit` (`ukb.py:1947-1961`) |
| **1/10** | `ukb build --mint` | **YES** — `id-ledger.json`, `artifacts.json`, `volumes.json`, `relationships.json`, `control-tower.json`, `change-ledger.json` + **6** `.md` registries | no | `_dump_json` at `ukb.py:1304-1314`; `_write` at `:1484`, `:1520`, `:1541`, `:1560`, `:1594`, `:1638` |
| **2/10** | `ukbx sync --due` | **YES** — signal ledger + cursors, `twin.json`, `control-tower.json` | **yes** — `sync-audit.json` | `ukbx.py:392`, `:464` (via `_refresh_control_tower`), `:233` |
| **3/10** | `ukbx twin` | **YES** — `twin.json`, `control-tower.json` | no | `ukbx.py:472`, `:464` |
| **4/10** | `ukbx portal` | **YES** — `00-BOOK/PORTAL/*.md` (**1604** tracked files) | no | `cmd_portal` `ukbx.py:1289-1347`, `PORTAL_DIR` |
| **5/10** | `ukb validate` | **no** | no | read-only; `ukb.py` validate path |
| **6/10** | `ukbx validate` | **no** | no | `cmd_validate` `ukbx.py:1348+` — no write call |
| **7/10** | `ukbx twin --check` | **no** | no | **[MEASURED]** `cmd_twin` delegates to `_cmd_certify` (`ukbx.py:469`); grep over `_cmd_certify` `:486-650` finds **zero** `_dump` / `append_audit` / `write` calls |
| **8/10** | `ukbx certify` | **YES** — cert evidence + cert report `.md` | **yes** — `certification-audit.json` | `ukbx.py:1264`, `:1249`, `_write_cert_report` |
| **9/10** | `ukb enforce` | **no** | **yes** — `enforcement-audit.json`, `mode=post` | as Phase 0 |

**Four of ten phases are fully read-only: 5, 6, 7 and — of tracked state — 0 and 9.** **[INFERRED]** This is why a substantial pre-mutation validation stage exists at all, and it is why `register.sh --observe` can exist as a genuine verification plane rather than a euphemism.

**One property makes re-runs cheap and the drift gate meaningful.** **[MEASURED]** All four writers are stamp-neutralized and skip no-op rewrites: `ukb._dump_json` (`:135-146`, guarded by `_stamp_eq_json :75-106`), `ukb._write` (`:1658-1664`, `_stamp_eq_text`), `ukbx._dump` (`:66-76`), `ukbx._dump_text` (`:692-698`). Each returns without writing when only the generation stamp would change. **[INFERRED]** Therefore a second identical run produces **zero byte changes** in tracked registers, which is the property V-12 tests.

### D.1 The 14 runtime validations

#### Stage 0 — pre-mutation verification (read-only; completing this stage **is** READY-FOR-EXECUTION)

| ID | Objective | Prerequisite state | Mutation? | Rollback? | Success condition | Failure condition |
|---|---|---|---|---|---|---|
| **V-1** | The Phase-1 authority is intact after 17–20 further tasks | implementation complete | **no** | no | `pytest platform/tests/test_ledger_authority.py` → all pass; count ≥ 77 plus the tasks' new tests | any failure, or a count below 77 (a Phase-1 test was removed) |
| **V-2** | The four read-only registration gates pass and no drift exists | V-1; register **committed** (E-4) | **no tracked**; appends `enforcement-audit.json` `mode=pre` | no | `register.sh --observe` → `RC=0`, *"OBSERVATION PASSED"* | `RC=2` gate failure · `RC=3` drift · `RC=4` enforcement · `RC=5` undetermined identity gap |
| **V-3** | Run A's manifest is measurable and its digest transcribable | V-1 | **no** — `--plan` writes nothing | no | `ukb build --mint --plan` prints `manifest_digest`, `preimage_digest`, `head`; **working tree unchanged** | any write; absent digest; a refusal before the plan |
| **V-4** | Run B's manifest is measurable and its digest transcribable | V-1 | **no** | no | `uga_engine.py run --plan` prints the manifest for the `by_object` allocation; working tree unchanged | as V-3 |
| **V-5** | The invariant surface baseline is recorded before mutation | V-1 | **no** | no | `uga_engine.py gate` runs and reports 30 invariants with the pre-mint violation counts recorded as the baseline | the gate cannot run; the surface is not 30 |
| **V-6** | A permit issued from the register **verifies** against the measured manifest — the round trip E-4A closes | F-1, F-4, V-3, V-4 | **no** — `_verify_permit` writes nothing | no | `_verify_permit` returns the permit for a correctly-issued permit **and refuses** on each of the 9 read bindings independently | acceptance of a wrong binding, or refusal of a correct permit |

**[MEASURED]** V-3's read-only property, this phase (**P4-3**): `ukb build --mint --plan` printed the manifest, `PLAN ONLY — nothing written, no identity allocated`, and `git status --porcelain` over all four guard directories was empty afterwards.

**[MEASURED]** V-6's binding surface is exactly **9** fields — `permit_id`, `actor`, `manifest_digest`, `preimage_digest`, `head`, `scope`, `scope.maps`, `scope.max_allocations`, `expires_at` (`PHASE3` P3-7, `:714-804`).

#### Stage 1 — Run A (mutating): `register.sh`

| ID | Objective | Prerequisite state | Mutation? | Rollback? | Success condition | Failure condition |
|---|---|---|---|---|---|---|
| **V-7** | **Close UK-1.** All 10 phases complete; the transaction seals | Stage 0 green; a permit issued **at the current pre-image** (E-6) | **YES** — tracked: ledger + 5 DATA docs + 6 `.md` registries + `twin.json` + control tower + 1604 PORTAL pages + cert evidence/report; untracked: 3 runtime logs | **YES** | `TRANSACTION COMPLETE — every artifact on disk is registered, classified, validated, and synchronized` and exit 0 | any `TRANSACTION INCOMPLETE — …` with exit 1/2/4. **Note the asymmetry:** a Phase-0 or Phase-1 refusal leaves tracked state untouched; a failure at 2/3/4/5/6/7/8/9 leaves it **mutated and unsealed** |
| **V-8** | Establish exactly what the run changed, before anything is restored | V-7 terminated (either way) | **no** | no | `git status --porcelain` over the four guard directories, plus a captured diff, enumerates every changed path | the inspection is not performed before a restore — after which the evidence is gone |
| **V-9** | The post-mint state re-verifies under the read-only plane | V-7 = COMPLETE | **no tracked** | no | `register.sh --observe` → `RC=0` **after** the registers are committed | `RC=3` if the regenerated registers are uncommitted — expected, and resolved by committing, not by re-running |

#### Stage 2 — Run B (mutating): `uga_engine.py run --mint`

| ID | Objective | Prerequisite state | Mutation? | Rollback? | Success condition | Failure condition |
|---|---|---|---|---|---|---|
| **V-10** | Mint the `by_object` population | Stage 0 green; a permit issued **at the then-current pre-image** (E-6) | **YES** — ledger + the UGA surface set | **YES** | `LA.commit` returns a report with `authorization=PERMIT`, `bytes_changed=True`, and the expected `by_object` count | `PermitRefused` (pre-image moved, binding mismatch) or `LedgerWriteRefused` (R-2/R-7 fired) |
| **V-11** | **Close UK-2.** The invariant surface reaches its target | V-10 | **no** | no | `uga_engine.py gate` → `UGA-INV-01 violations=0`; `UGA-INV-10` per the model's `Aud` disposition; **no invariant that passed at V-5 now fails** | `UGA-INV-01 > 0` (the population did not clear in one mint) or any V-5-passing invariant regressed |

**[MEASURED]** V-11's `UGA-INV-10` success condition is axis-dependent and cannot be stated model-independently. Under `Aud3` the invariant is absent, so the target surface is **29**, not 30 (`PHASE3:§B.5`). Under `Aud1`/`Aud2` it is 30. Stated per value, not chosen.

#### Stage 3 — post-mutation confirmation

| ID | Objective | Prerequisite state | Mutation? | Rollback? | Success condition | Failure condition |
|---|---|---|---|---|---|---|
| **V-12** | Idempotence: the transaction is safe to re-run, as its header claims | V-7 COMPLETE, registers committed | **YES** (a second run) but **byte-neutral** | no | a second `register.sh` produces **zero** byte changes across the four guard directories — the property `_stamp_eq_json`/`_stamp_eq_text` exist to provide | any byte change with no content change ⇒ the drift gate can never be green |
| **V-13** | No regression in the authority under real post-mint state | V-7, V-10 | **no** | no | `pytest platform/tests/test_ledger_authority.py` → all pass, unchanged from V-1 | any test that passed at V-1 now fails |
| **V-14** | **First live exercise of the three residuals' controls** | V-7 or V-10 completed a real write | **no** (inspection) | no | evidence that on a real write: the lock was taken (`_ledger_lock`), the pre-write byte re-check ran (R-2), and the post-write document comparison ran (R-7, `:920`) without firing a refusal | any of the three did not execute, or fired spuriously — see §G |

```
RUNTIME VALIDATIONS ................. 14
    Stage 0  pre-mutation, read-only ...  6   V-1 … V-6
    Stage 1  Run A .....................  3   V-7 … V-9
    Stage 2  Run B .....................  2   V-10, V-11
    Stage 3  confirmation ..............  3   V-12 … V-14

    of which MUTATING ..................  3   V-7, V-10, V-12
    of which distinct MUTATING RUNS ....  2   V-7 (run A), V-10 (run B)
        V-12 re-runs A and is byte-neutral by construction, so it adds no
        new allocation and no new rollback surface
```

### D.2 What cannot be validated at all

**[UNKNOWN]** Phases 2, 3, 4 and 8 have **no dry-run mode** (**P4-6** — `--plan` appears nowhere in `ukbx.py`). Their behaviour against post-mint state is therefore unobservable until V-7 runs them. This is not a gap in the program; it is the reason the program requires a mutating run, and it is the concrete content of UK-1.

---

## E. Minimum execution set

### E.1 The lower bound, proved

**Claim: the minimum is exactly 2 mutating runs.**

**Lower bound ≥ 2** — **[MEASURED]**, three independent facts:

1. `register.sh` never invokes `uga_engine` (**P4-1**).
2. The two allocation populations are disjoint: `|gap_by_path ∩ anonymous_by_object| = 0` (**P4-5**).
3. `by_path` and `by_object` are distinct ledger maps, and `ukb._iter_files` structurally excludes `00-BOOK/DATA` — the register's own home — from `by_path` eligibility, while UGA discovery does not exclude it (**P4-10**).

**[INFERRED]** So no single command allocates into both maps, and neither population is a subset of the other. One mutating run therefore cannot close both unknowns.

**Upper bound ≤ 2** — **[INFERRED]** from §D.0: UK-1 is discharged entirely by `register.sh` (a single invocation runs all ten phases) and UK-2 entirely by `uga_engine run --mint` (a single invocation). No third command is required by either.

```
MINIMUM MUTATING RUNS = 2
```

### E.2 The minimum program

Each step is tagged **[EXEC-REQ]**. No step is redundant; the justification for each is that removing it either leaves an unknown open or violates a measured constraint.

```
 #  STEP                                                MUTATES  CLOSES / WHY NOT REMOVABLE
──  ──────────────────────────────────────────────────  ───────  ─────────────────────────────────
 0  Governance selection (5 axes)                          no    E-1; task content undefined without it
 1  Implement the 17–20 tasks, in E-2/E-3/E-7 order        yes*   *source only; no ledger write
 2  COMMIT the register (+ any new tracked artifact)       yes*   E-4: an untracked DATA file is DRIFT
                                                                 (register.sh:125, :265)
 3  V-1  authority suite                                    no    the tasks may have broken Phase 1
 4  V-3  `ukb build --mint --plan`                          no    E-6: run A's permit needs THIS digest
 5  V-5  `uga_engine gate` — baseline                       no    V-11 has no success condition without it
 6  V-2  `register.sh --observe`                            no    the only pre-mutation check of gates
                                                                 0/5/6/7 + drift + identity gap
 7  V-4  `uga_engine run --plan`                            no    run B's manifest
 8  V-6  permit round trip (read-only verify)               no    proves E-4A closed BEFORE mutating
    ══════ READY-FOR-EXECUTION REACHED HERE — 0 mutating runs so far ══════
 9  Issue permit A at the current pre-image                yes*   *the register only; not the ledger
10  V-7  `register.sh`            ── MUTATING RUN 1 ──     YES    closes UK-1
11  V-8  capture the diff BEFORE any restore                no    §F.4: restoration destroys the evidence
12  Commit the regenerated registers                        yes*   V-9 cannot pass otherwise
13  V-9  `register.sh --observe`                             no    confirms the post-mint state re-verifies
14  Re-measure; issue permit B at the NEW pre-image         yes*   E-6: permit B at the old pre-image is
                                                                 REFUSED on the pre-image binding (P4-7)
15  V-10 `uga_engine run --mint`  ── MUTATING RUN 2 ──     YES    closes UK-2 (first half)
16  V-11 `uga_engine gate`                                  no    closes UK-2 (second half)
17  V-12 second `register.sh` — byte-neutrality             YES†  †byte-neutral by construction (D.0)
18  V-13 authority suite re-run                             no    regression under real post-mint state
19  V-14 residual-control activation evidence                no    §G — first live exercise of R-2/R-3/R-7
```

**Steps 10 and 15 may be exchanged.** **[MEASURED]** the A↔B order is free (**P4-1**, **P4-5**); only E-6's *measure → issue → run* serialization is binding, and it applies to whichever runs second.

### E.3 Why no activity is redundant

| Candidate for removal | Why it cannot be removed |
|---|---|
| Step 2 (commit the register) | **[MEASURED]** `register.sh:125` counts `??` as drift; V-2 returns `RC=3` with the register uncommitted |
| Step 5 (baseline gate) | **[INFERRED]** V-11's condition *"no invariant that passed at V-5 now fails"* is unstatable without V-5 |
| Step 8 (permit round trip) | **[INFERRED]** it is the last point at which E-4A's closure is falsifiable **without mutating**. Deferring it to step 10 converts a read-only failure into a mutating one |
| Step 11 (capture the diff) | **[MEASURED]** §F.4 — `git checkout` overwrites; the changed-path set is unrecoverable afterwards |
| Step 14 (re-measure) | **[MEASURED]** **P4-7** — `preimage_digest` moved `3a2a2532…` → `0b7a886d…`; permit B issued earlier is refused |
| Step 17 (V-12) | **[INFERRED]** the header claims *"safe to run repeatedly"*; the four stamp-neutralizing writers exist to make it true. Untested, the claim is unverified and the drift gate's greenness is unestablished |
| Either mutating run | **[MEASURED]** §E.1 — disjoint populations |

### E.4 Governance-dependence of the program

**[INFERRED]** The program's **shape** — 20 steps, 2 mutating runs, 14 validations, 3 rollback procedures — is **identical under all 12 models**. Two step *contents* are axis-parameterized:

| Step | Parameterized by | Values |
|---|---|---|
| **V-11**'s success condition | axis `Aud` | `Aud1`/`Aud2` → target surface 30; `Aud3` → target surface **29** (`UGA-INV-10` retired) |
| **Rollback R-B**'s scope | axis `B` | `B2b` adds a second tracked artifact to remove; `B1` and `B2a` do not (§F.4) |

Neither changes the count of anything in §J.

---

## F. Rollback analysis

### F.1 Artifacts created

| Artifact | Created by | Tracked? | Restorable by `git checkout`? |
|---|---|---|---|
| `00-BOOK/DATA/allocation-permits.json` | F-1, before execution | tracked after step 2 | **no** if untracked at rollback time; **yes** once committed |
| A `B2b` use-record artifact | O-3 under `B2b` only | tracked | as above; **axis-`B`-dependent** |
| An `Aud1` tracked audit log | O-9 under `Aud1` only | tracked | as above; **axis-`Aud`-dependent** |
| `00-BOOK/tools/.register.lock` | `register.sh` re-entrancy guard | **gitignored** (`.gitignore:3`) | n/a — removed by the script's own `EXIT` trap; a stale lock is reclaimed after 3600 s (`register.sh:181-187`) |
| `.runtime/governance/{enforcement,sync,certification}-audit.json` | phases 0, 2, 8, 9 | **gitignored** (`.gitignore:12`) | **NO — see §F.3** |

### F.2 Artifacts modified — and the one path a rollback must never touch

**[MEASURED]** **P4-9**: the tracked mutation surface is exactly the four guard directories, and **every file in each is tracked**:

| Directory | Tracked | On disk | Dirty at HEAD |
|---|---|---|---|
| `00-BOOK/DATA` | 17 | 17 | **0** |
| `00-BOOK/REGISTRIES` | 6 | 6 | **0** |
| `00-BOOK/CONTROL-TOWER` | 12 | 12 | **0** |
| `00-BOOK/PORTAL` | 1604 | 1604 | **0** |
| **total** | **1639** | **1639** | **0** |

**[INFERRED]** Because tracked = on-disk in all four and all four are clean at HEAD, `git checkout -- <the four paths>` is a **complete and non-destructive** restoration of the tracked mutation surface. It cannot destroy uncommitted work, because there is none in scope.

**[EXEC-REQ] The zero-dirty precondition must be re-verified immediately before any restore.** It is a property of the present working tree, not a guarantee. If any guard directory acquires uncommitted work before execution, `git checkout` becomes destructive over that work.

**One path a rollback must never include, and this is the sharpest rollback finding.**

**[MEASURED]** `git cat-file -e HEAD:00-BOOK/tools/ledger_authority.py` → *fatal: path … exists on disk, but not in `HEAD`*. Its status is `AM`: staged as an addition, **never committed**.

**[INFERRED]** Therefore `git checkout HEAD -- 00-BOOK/tools/` — or any broader restore that includes `00-BOOK/tools/` — would **delete the entire Phase-1 implementation**, all twelve closures, which exists in no commit. The rollback scope must be bounded to the four guard directories by name. **[EXEC-REQ]** Committing `ledger_authority.py` before execution removes this hazard; until then it is a live one.

### F.3 The one class that cannot be restored

**[MEASURED]** `.runtime/governance/` is gitignored (`.gitignore:12`, confirmed by `git check-ignore -v .runtime`). Current state, this phase (**P4-8**):

```
enforcement-audit.json      612 runs, last seq 612
sync-audit.json              19 runs, last seq  19
certification-audit.json      1 run,  last seq   1
```

**[MEASURED]** `append_audit` (`governance_telemetry.py:133-159`) assigns the monotonic `seq` *"HERE and only here"* and appends. **[INFERRED]** `git` cannot restore an ignored path, so a rollback leaves the advanced sequences in place. The advance is **irreversible by the rollback procedure**.

**Why this is bounded rather than a defect.** Two measured mitigations:

1. **Declared non-history.** `governance_telemetry.py:30-40` states this is *"per-clone **operational** state, git-ignored, and … NEVER a repository artifact"*, and that a fresh runtime starting at `seq = 1` is *"CORRECT and EXPECTED — not a regression."* So the sequence is not repository truth, and restoring it is not required for correctness.
2. **Deduplicated.** `append_audit` takes a `dedup` policy; `_enforcement_audit` uses `fingerprint_dedup(fp_keys, mode_key="mode")` (`ukb.py:1955-1960`) so *"an idempotent re-run → no append, no write, so the log never grows."* **[INFERRED]** Repeated identical runs do not grow the logs without bound; a full transaction appends at most one `pre` and one `post` record.

**[EXEC-REQ]** Record the three `seq` values before and after execution. The delta is durable evidence of what ran, and it is the **only** evidence that survives a full tracked rollback.

### F.4 Restoration procedure

Three procedures, each with a distinct scope. Stated as requirements on the program, not as commands to run now.

| ID | Scope | Procedure | Completeness |
|---|---|---|---|
| **R-A** | tracked mutation surface — 1639 files in 4 directories | restore the four guard paths to HEAD, **by name**, never a broader path | **complete** — **[MEASURED]** tracked = on-disk and 0 dirty at HEAD in all four (**P4-9**) |
| **R-B** | untracked new artifacts — the register, plus a `B2b` record or an `Aud1` log if the model takes them | **explicit removal.** **[INFERRED]** a checkout restores tracked paths and does **not** remove untracked files, so R-A alone leaves the register on disk, where it then reads as `??` DRIFT under `register.sh:125` | complete **only if** the created-artifact set from §F.1 is enumerated first; its size is axis-`B`/`Aud`-dependent |
| **R-C** | the re-entrancy lock | `register.sh`'s own `EXIT` trap (`:189`) removes it; after an uncatchable kill it persists and is reclaimed at 3600 s (`:181-187`) | complete, with a 1-hour worst case |
| **— (not a procedure)** | `.runtime/governance/*.json` | **NOT RESTORED.** Declared per-clone operational state (§F.3) | n/a by declaration |

### F.5 Two rollback interactions that are not obvious

**Interaction 1 — the rollback procedure *is* the E1-F3 replay vector.**

**[MEASURED]** `PHASE2` probe P2-1: replay was ACCEPTED after a byte restore of the ledger, and REFUSED when the restore was attempted *through* the chokepoint. **[MEASURED]** `_verify_permit :743-749` refuses only on `preimage_digest` mismatch.

**[INFERRED]** R-A restores the ledger's bytes out-of-band, returning the pre-image to its pre-run value — which re-validates the permit that was just used. The consequence differs by axis `B`, and both are stated because Rule 3 forbids choosing:

| Axis `B` | Consequence of R-A |
|---|---|
| **`B1`** reusable | The restored permit verifies again. Re-running requires no new permit. Consistent with the model's own ratified semantics. |
| **`B2`** consumed, durable | **[INFERRED]** the use record is a *separate* artifact from the ledger, and R-A restores only the four guard paths. Under `B2a` the mark lives in the register — untracked at rollback time, so R-A does not revert it; under `B2b` in a separate artifact, likewise. So the permit stays **spent** while the allocation is **undone**. Re-running requires issuing a **new** permit. |

**[EXEC-REQ]** The program must record which of these applies once the axis is selected, because it determines whether a retry after rollback needs a fresh permit.

**Interaction 2 — a mid-transaction failure is the only state that requires rollback.**

**[MEASURED]** `register.sh` phase order (§D.0) and `fail()` at `:201`. **[INFERRED]** three distinct failure shapes:

| Failure point | Tracked state | Rollback |
|---|---|---|
| Phase 0 (`enforce --pre`) | untouched | **not required** — only a runtime `seq` advanced |
| Phase 1 refused by the authority | untouched — **[MEASURED]** every `commit()` refusal path restores the pre-image byte-for-byte (`_restore :807-822`; `PHASE1:§R-7` verified `read_bytes() == original` on all five divergence tests) | **not required** |
| Phases 2–9 | **mutated and unsealed** — Phase 1's writes landed; the transaction reports INCOMPLETE | **REQUIRED** — R-A + R-B |

```
ROLLBACK PROCEDURES REQUIRED ..... 3   (R-A tracked, R-B untracked-new, R-C lock)
NON-RESTORABLE CLASSES ........... 1   (.runtime/governance — by declaration)
```

### F.6 Evidence preservation procedure

**[INFERRED]** R-A overwrites, so evidence must be captured **before** restoration or it is lost. Four items, with where each must be written.

| Evidence | Why it must be preserved | Destination constraint |
|---|---|---|
| **stdout/stderr of all 10 phases + both runs** | The only record of *which* phase failed and with what message. Transient. | **Outside the four guard directories.** **[MEASURED]** anything written inside them reads as drift (`register.sh:265-267`) |
| **`git status --porcelain` + full diff over the four guard paths** | The changed-path set; unrecoverable after R-A (V-8) | as above |
| **The three `.runtime` `seq` values, before and after** | **[INFERRED]** the only evidence that survives R-A intact (§F.3) | already outside version control |
| **The ledger `sha256` before, after each run, and after restore** | Proves R-A returned the exact pre-image, closing the restore itself | as above |

**[EXEC-REQ]** A capture destination must be chosen that is neither inside the four guard directories nor an untracked file that would itself read as drift. **[MEASURED]** the repository already declares such classes: `determinism-evidence/`, `*.bundle` and `.runtime/` are gitignored, and `.gitignore`'s bundle note states bundles *"belong in durable storage OUTSIDE the repository, never inside the tree they back up."*


---

## G. Residual analysis

Re-evaluated against what execution evidence can establish. The question per item is narrow: **can a real write close, reduce, or leave unchanged the residual?**

### G.1 RES-3 — MW-3 is bounded, not closed

**Determination: execution evidence can REDUCE it. It cannot close it.**

| Aspect | Determination |
|---|---|
| **What it is** | The caller's ledger read precedes `commit()`, therefore precedes the lock. **[MEASURED]** `uga_engine.py:2097` passes `st["ledger"]`, built by the whole `build()` discovery pass; `commit` takes the lock at `:870`, on entry. |
| **Why execution cannot close it** | **[INFERRED]** Closing it requires the caller's read to occur *inside* the lock. No validation changes where a read happens. `PHASE05:§F.4` names the fix — running the discovery pass under exclusion — and classes it as an architecture change outside any authorization in the chain. Executing the program does not perform it. |
| **What execution DOES establish** | **[INFERRED]** V-7 and V-10 are the **first** real writes to traverse the window. Success is positive evidence that the window was not exploited on this traversal, and that R-6's two refusal legs did not spuriously fire on a real 7009-record ledger. |
| **Reduction, precisely** | From *"bounded by two refusals, never exercised end-to-end"* to *"bounded by two refusals, exercised on N real traversals without a false refusal."* **[INFERRED]** That is a reduction in **epistemic** risk, not in the window's width. The width is unchanged and measurable at `:2097` versus `:870` after execution exactly as before. |
| **Verdict** | **REDUCED** — evidence class improves; the defect is untouched. |

### G.2 RES-4 — `flock` is advisory and filesystem-dependent

**Determination: execution evidence can REDUCE it, for one filesystem only.**

| Aspect | Determination |
|---|---|
| **What it is** | **[MEASURED]** `_ledger_lock :216-268` takes `fcntl.flock(fd, LOCK_EX\|LOCK_NB)` on the ledger's containing directory. Advisory: a process that never asks is not excluded. On a filesystem that does not honour `flock`, the control silently degrades and R-2's pre-write byte re-check (`commit :887-893`) is the sole detector. |
| **Why execution cannot close it** | **[INFERRED]** The residual is a statement about *the set of filesystems*, universally quantified. A run on one filesystem is one instance. No finite number of runs closes a universal claim about environments. |
| **What execution DOES establish** | **[INFERRED]** That `flock` was honoured **on the filesystem the run used**, and that the fail-closed branch was not triggered. **[MEASURED]** already verified on macOS/APFS by `PHASE1:§R-3` — two subprocesses serialized; contention refused. Execution extends that to the production ledger's own directory rather than a temp dir. |
| **Reduction, precisely** | From *"verified on a temp dir on this platform"* to *"verified on the production ledger's directory on this filesystem."* The universal claim is untouched. |
| **Verdict** | **REDUCED** — scope of verified instances widens by one; the environmental dependency is unchanged. |

### G.3 R-7w — post-hoc detection window

**Determination: execution evidence LEAVES IT UNCHANGED. This is the one residual execution cannot even reduce.**

| Aspect | Determination |
|---|---|
| **What it is** | **[MEASURED]** the exact sequence inside `commit()`, re-read this phase: `writer(path, ledger)` at **`:893`** → `raw_after = _read_bytes_or_none(path)` at **`:895`** → `if persisted != ledger` at **`:920`** → `_restore(path, raw_before)` at **`:921`**. Divergent bytes **reach disk** before the comparison, and a crash between `:893` and `:921` leaves them there. |
| **Why execution cannot close it** | **[INFERRED]** Closing it requires moving serialization inside the authority — `PHASE1:§R-7` declined it as *"a larger change than this phase covers."* And **[MEASURED]** it cannot be closed by comparing bytes instead: `LA._canonical` produces 1 786 167 bytes against both production writers' 2 274 511 (`PHASE1:§R-11`), which is why `:920` compares documents and why `A4` is CONTRADICTED (CX-6). |
| **Why execution cannot even REDUCE it** | **[INFERRED]**, and this is the distinction from G.1 and G.2. RES-3 and RES-4 are risks that a **successful** run provides evidence against — the window was not exploited, the lock held. R-7w is different: it is a property of the **failure** path. A successful run never enters the window between `:893` and `:921`, because `persisted == ledger` and `_restore` is never called. **A successful execution therefore produces no evidence about R-7w at all.** The only run that would exercise it is one where the writer diverges — which, if it happened, would be a defect to fix, not evidence to bank. |
| **What execution DOES establish** | **[INFERRED]** Only that R-7's *comparison* executed and passed — which is V-14's scope. That is evidence about the check, not about the window. |
| **Verdict** | **UNCHANGED** — and unchanged for a structural reason, not for want of a better program. |

### G.4 Summary

| Residual | Close? | Reduce? | Unchanged? | Why |
|---|---|---|---|---|
| **RES-3** MW-3 window | no | **YES** | — | success evidences non-exploitation on N traversals; width unmoved |
| **RES-4** advisory `flock` | no | **YES** | — | one more verified filesystem instance; universal claim unmoved |
| **R-7w** post-hoc detection | no | **no** | **YES** | it is a property of the failure path; a successful run never enters it |

```
RESIDUALS BEFORE EXECUTION ....... 3
RESIDUALS CLOSED BY EXECUTION .... 0
RESIDUALS REDUCED ................ 2   (RES-3, RES-4 — evidence class only)
RESIDUALS UNCHANGED .............. 1   (R-7w)
RESIDUALS AFTER EXECUTION ........ 3
```

**[INFERRED]** No execution program can do better, because all three were classified as bounds by authorization scope rather than by uncertainty (`PHASE05:§F.4`, `PHASE1:§R-3`/`§R-6`/`§R-7`), and `PHASE3:§E.7` established all three are invariant across all 12 models. Execution changes what is *known* about two of them and nothing about the third.

---

## H. Terminal-state matrix

### H.1 Per-run outcome classes

**[MEASURED]** from §D.0 and §F.5, Run A has **three** distinguishable outcomes, not two:

| Code | Run A outcome | Tracked state |
|---|---|---|
| **A✓** | all 10 phases complete; transaction sealed | mutated, sealed |
| **A⊘** | Phase 0 fails, or Phase 1 refused by the authority | **untouched** — `_restore` guarantees byte-identity |
| **A✗** | a phase in 2…9 fails | **mutated, unsealed** — rollback required |

Run B likewise:

| Code | Run B outcome | Tracked state |
|---|---|---|
| **B✓** | `commit` returns; the gate reaches its target surface | mutated |
| **B⊘** | `PermitRefused` or `LedgerWriteRefused` | **untouched** |
| **B✗** | `commit` succeeds but a downstream surface emission or the gate fails | **mutated, inconsistent** — rollback required |

### H.2 The matrix — every reachable end state

Residuals are **3** in every row (§G). "Defects" are implementation errors that validation *reveals*; they are not new blockers created by the program (§H.4).

| # | Stage 0 | Run A | Run B | **Blockers** | **Residuals** | **Unknowns** | Rollback needed |
|---|---|---|---|---|---|---|---|
| **T-0** | ✗ fails | — | — | 0 + revealed defects | 3 | **2** — UK-1, UK-2 | **no** — no mutation occurred |
| **T-1** | ✓ | **A✓** | **B✓** | **0** | **3** | **0** | **no** |
| **T-2** | ✓ | A✓ | B⊘ | 0 + revealed | 3 | **1** — UK-2 | no |
| **T-3** | ✓ | A✓ | B✗ | 0 + revealed | 3 | **1** — UK-2 | **yes** — R-A + R-B, run B's scope |
| **T-4** | ✓ | A⊘ | B✓ | 0 + revealed | 3 | **1** — UK-1 | no |
| **T-5** | ✓ | A✗ | B✓ | 0 + revealed | 3 | **1** — UK-1 | **yes** — R-A + R-B, run A's scope |
| **T-6** | ✓ | A⊘ | B⊘ | 0 + revealed | 3 | **2** | no |
| **T-7** | ✓ | A✗ | B⊘ | 0 + revealed | 3 | **2** | **yes** |
| **T-8** | ✓ | A⊘ | B✗ | 0 + revealed | 3 | **2** | **yes** |
| **T-9** | ✓ | A✗ | B✗ | 0 + revealed | 3 | **2** | **yes** — both scopes |

```
REACHABLE TERMINAL STATES ...................... 10
    requiring rollback ..........................  5   T-3, T-5, T-7, T-8, T-9
    with 0 unknowns .............................  1   T-1
    with 1 unknown ..............................  4   T-2, T-3, T-4, T-5
    with 2 unknowns .............................  5   T-0, T-6, T-7, T-8, T-9
    with 0 blockers AND 0 unknowns ..............  1   T-1
```

### H.3 Collapse to distinct triples

**[INFERRED]** On the `(blockers, residuals, unknowns)` triple alone the ten rows collapse to **three** classes: `(0,3,0)`, `(0+d,3,1)`, `(0+d,3,2)`. The rows remain individually reachable and distinct because they differ in **rollback obligation**, which the triple does not express. Both counts are reported: **10** reachable states, **3** distinct triples.

### H.4 One classification stated explicitly

**[INFERRED]** A validation failure means the implementation is wrong. That is a **revealed defect** — a pre-existing implementation error surfaced by validation — not a new blocker introduced by this determination. Rule 0's *"without introducing any new blocker"* is satisfied: the program **introduces** none and **reveals** whatever exists. A program that could not reveal defects would not be a validation program.

**[INFERRED]** `T-1` is the only terminal state that reaches 0 unknowns, and it requires **both** runs to succeed. There is no partial path to full closure, because §E.1 established the two populations are disjoint.

---

## I. Readiness determination

### I.1 What evidence is required to retire UK-1?

**[EXEC-REQ]** Five items. All five are necessary; **[INFERRED]** the set is sufficient because UK-1's definition is exactly *"Phase 1 completes and the nine dependent phases pass."*

| # | Required evidence | Established by |
|---|---|---|
| 1 | Phase 1 completed: a `commit()` report with `authorization=PERMIT`, `bytes_changed=True`, and the **9** `by_path` allocations | V-7 phase 1 |
| 2 | Each of phases 2/10 … 9/10 exited 0 — **[MEASURED]** enforced structurally, since `fail()` at `:201` exits and every phase is `\|\| fail` | V-7 phases 2–9 |
| 3 | The terminal line `TRANSACTION COMPLETE — every artifact on disk is registered, classified, validated, and synchronized` and exit status 0 | V-7 |
| 4 | The post-mint state re-verifies read-only: `register.sh --observe` → `RC=0` after the regenerated registers are committed | V-9 |
| 5 | The transaction is byte-stable on re-run: a second `register.sh` produces **zero** byte changes across the four guard directories | V-12 |

**[INFERRED]** Item 5 is required, not optional. Without it, `register.sh` completing once is compatible with the drift gate never being green — and `register.sh:265-267` makes an ungreen drift gate a permanent `exit 3` in CI and pre-commit. A UK-1 retired on items 1–4 alone would be retired on a one-shot success.

### I.2 What evidence is required to retire UK-2?

**[EXEC-REQ]** Four items.

| # | Required evidence | Established by |
|---|---|---|
| 1 | `uga_engine run --mint` committed: `authorization=PERMIT`, and the `by_object` allocation count equals the population measured at issuance | V-10 |
| 2 | `UGA-INV-01 violations=0` — down from the measured **27** | V-11 |
| 3 | `UGA-INV-10` at its model-determined target: **[MEASURED]** axis-dependent — surface **30** under `Aud1`/`Aud2`, surface **29** under `Aud3` where the invariant is retired | V-11 |
| 4 | **No invariant that passed at V-5 fails at V-11.** **[MEASURED]** baseline: 2 of 30 FAIL, so 28 must still pass | V-5 → V-11 |

**[EXEC-REQ] One item must be settled before issuance, and it is measured, not speculative.** The population at issuance is **not** the 27 measured today. **[MEASURED]** **P4-10**: all 17 `00-BOOK/DATA/*.json` files are in `by_object`; **[INFERRED]** committing the permit register makes it the 18th, so the population at issuance is **28**. Item 2's condition is `violations=0` regardless, but item 1's count must be measured **after** step 2 of §E.2, never carried from this document.

**[UNKNOWN]** Whether any further tracked artifact is created between measurement and mint. `B2b` and `Aud1` each add one (§F.1). The program must re-measure immediately before issuance; the number cannot be fixed in advance.

### I.3 Can READY-FOR-EXECUTION be reached?

# **YES.**

**[INFERRED]** from the measured facts in §D.0 and §D.1: every precondition of the mutating runs is verifiable **without mutating tracked state**.

```
  Stage 0 = V-1 … V-6, ALL READ-ONLY OF TRACKED STATE:

    V-1  pytest                          temp dirs only
    V-2  register.sh --observe           MEASURED read-only plane; the header states
                                         "this command allocates no identity and writes
                                         nothing under version control" (register.sh:99)
                                         — and the claim is exact, not loose: it appends
                                         only to the gitignored runtime log
    V-3  ukb build --mint --plan          MEASURED this phase (P4-3): "PLAN ONLY —
                                         nothing written"; all four guard dirs clean after
    V-4  uga_engine run --plan            same mechanism, uga_engine.py:2181
    V-5  uga_engine gate                  MEASURED this phase (P4-4): cmd_gate docstring
                                         "Verify without mutating. Fails closed."
                                         Ledger sha256 identical after
    V-6  _verify_permit round trip        MEASURED: writes nothing (PHASE0 EV-13, P3-1)

  ⇒ MUTATING RUNS REQUIRED TO REACH READY-FOR-EXECUTION ............ 0
```

**[INFERRED]** Three conditions, all determinate, none open-ended:

1. **Governance selection** on the 5 closure axes — the same single precondition Phase 3 identified, with all 12 satisfying values enumerated.
2. **Implementation** of the 17–20 tasks in E-2/E-3/E-7 order.
3. **Stage 0 green**, including the register **committed** (E-4).

**Contrast with Phase 3, stated so the two are not read as contradicting.** Phase 3 answered **NO** to *unconditional* readiness on three grounds. Two of them — UK-1 and UK-2 — are **not** obstacles to READY-FOR-EXECUTION, because that state is defined as the point at which execution may commence, and the unknowns are what execution resolves. The third ground — three residuals surviving every model — remains true and is carried into the target state, which is why READY-FOR-EXECUTION carries 3 residuals rather than 0.

### I.4 Under how many admissible governance models?

```
ADMISSIBLE MODELS ................................................ 12
REACHING READY-FOR-EXECUTION ..................................... 12   (all)
REACHING TERMINAL STATE T-1 (0 blockers, 0 unknowns) ............. 12   (all, conditional
                                                                        on both runs succeeding)
```

**[INFERRED]** All 12, because the program's shape is model-invariant (§E.4): the graph topology, the 14 validations, the 2 mutating runs and the 3 rollback procedures are identical across the set. Only two step *contents* are axis-parameterized — V-11's target surface (axis `Aud`) and R-B's scope (axis `B`) — and neither changes reachability.

**[INFERRED]** No model is better or worse positioned. That is the same structural result `PHASE3:§C.3` established for implementation tasks, appearing again at the execution layer: nothing is stranded on a single governance outcome.

### I.5 What remains after successful validation?

Terminal state **T-1**:

```
BLOCKERS ......................... 0
RESIDUALS ........................ 3
    RES-3  MW-3 bounded, not closed          REDUCED  (N traversals, no false refusal)
    RES-4  flock advisory, fs-dependent      REDUCED  (one more verified filesystem)
    R-7w   post-hoc detection window         UNCHANGED (a property of the failure path)
UNKNOWNS ......................... 0
    UK-1  retired by I.1's five evidence items
    UK-2  retired by I.2's four evidence items
ROLLBACK OBLIGATION .............. none
IRREVERSIBLE SIDE EFFECTS ........ 2 classes
    permanent identities allocated: 9 by_path + the by_object population
        MEASURED: append-only; assert_append_only refuses removal (:290-296)
    .runtime seq advance: enforcement, sync, certification
        MEASURED: 612 / 19 / 1 before; not restorable; declared non-history
```

**[INFERRED]** T-1 is not "everything closed." It is **0 blockers, 0 unknowns, 3 accepted residuals** — and the residuals are accepted on grounds recorded before governance entered the problem, by `PHASE05:§F.4` and `PHASE1:§R-3`/`§R-6`/`§R-7`.

### I.6 What remains after failed validation?

**[INFERRED]** Nine of the ten terminal states are failure states, and they differ in three respects, not one.

| | Unknowns remaining | Rollback obligation | Revealed defects |
|---|---|---|---|
| **T-0** Stage 0 fails | **2** | **none** — nothing mutated | in the implementation, caught before any write |
| **T-2 / T-4** one run refused cleanly | **1** | **none** — **[MEASURED]** a refusal restores the pre-image byte-for-byte (`_restore :807-822`; `PHASE1:§R-7`) | in permit issuance or a binding |
| **T-6** both refused cleanly | **2** | none | as above |
| **T-3 / T-5** one run failed mid-transaction | **1** | **R-A + R-B** | in a phase downstream of the first write |
| **T-7 / T-8 / T-9** at least one failed mid-transaction | **2** | **R-A + R-B** | as above |

**[INFERRED] Three properties hold in every failure state:**

1. **Blockers do not return to 5.** The five governance-dependent blockers are closed by governance + implementation, not by execution. A validation failure reveals a defect in *how* a task was implemented; it does not reopen E-4A, E1-F3, E-3, RES-1 or RES-2.
2. **Residuals stay at 3.** No failure creates or closes one.
3. **The failure is recoverable.** **[MEASURED]** R-A is complete over the tracked surface (**P4-9**: tracked = on-disk, 0 dirty at HEAD in all four directories), so no failure state is terminal in the sense of being unrecoverable — subject to R-A never being widened to include `00-BOOK/tools/`, which **[MEASURED]** would delete `ledger_authority.py`, absent from HEAD (§F.2).

**[EXEC-REQ]** In every failure state, §F.6's four evidence items must be captured **before** R-A runs, or the diagnosis of the failure is destroyed along with its effects.


---

## J. Exact counts

### J.1 The requested counts

```
UNKNOWNS
    before validation ..............................................  2   UK-1, UK-2
    after SUCCESSFUL validation (T-1) ..............................  0
    after FAILED validation ........................................  1  or  2
        1  — one run closed, the other did not     (T-2, T-3, T-4, T-5)
        2  — neither closed, or Stage 0 aborted    (T-0, T-6, T-7, T-8, T-9)

RUNTIME VALIDATIONS REQUIRED ....................................... 14
    Stage 0  pre-mutation, read-only ...............................  6   V-1 … V-6
    Stage 1  Run A .................................................  3   V-7, V-8, V-9
    Stage 2  Run B .................................................  2   V-10, V-11
    Stage 3  post-mutation confirmation ............................  3   V-12, V-13, V-14

    read-only of tracked state ..................................... 11
    mutating .......................................................  3   V-7, V-10, V-12
                                                                          (V-12 byte-neutral
                                                                           by construction)

MUTATING RUNS REQUIRED .............................................  2
    RUN A  register.sh                  ->  closes UK-1   ->  9 by_path mints
    RUN B  uga_engine.py run --mint     ->  closes UK-2   ->  by_object mints,
                                                              population 28 at issuance
    minimum PROVED at 2 (§E.1):
        register.sh never invokes uga_engine                     (P4-1)
        allocation populations disjoint, overlap = 0             (P4-5)
        00-BOOK/DATA excluded from by_path eligibility, 0 of 17  (P4-10)
    to REACH READY-FOR-EXECUTION ...................................  0

ROLLBACK PROCEDURES REQUIRED .......................................  3
    R-A  tracked mutation surface — 1639 files in 4 directories, restore BY NAME
    R-B  untracked new artifacts — the register (+ B2b / Aud1 artifacts if taken)
    R-C  the re-entrancy lock — script EXIT trap; 3600 s stale reclamation
    non-restorable classes .........................................  1
    R-A  .runtime/governance/*.json — gitignored, append-only, declared non-history

REACHABLE TERMINAL STATES .......................................... 10
    distinct (blockers, residuals, unknowns) triples ...............  3
    requiring rollback .............................................  5   T-3, T-5, T-7, T-8, T-9
    reaching 0 blockers AND 0 unknowns .............................  1   T-1

RESIDUALS
    before execution ...............................................  3
    closed by execution ............................................  0
    reduced (evidence class only) ..................................  2   RES-3, RES-4
    unchanged ......................................................  1   R-7w
    after execution ................................................  3

BLOCKERS
    at READY-FOR-EXECUTION .........................................  0
    after successful validation ....................................  0
    after failed validation ........................................  0  + revealed defects
    NEW blockers introduced by this program ........................  0

ORDERING CONSTRAINTS ...............................................  7   E-1 … E-7
    hard, all 12 models ............................................  6   E-1 … E-6
    hard, 4 models (Aud1 only) .....................................  1   E-7
    free .......................................................... run A ↔ run B order

MODELS REACHING READY-FOR-EXECUTION ................................ 12  of 12
```

### J.2 Success criteria

| Criterion | Discharge |
|---|---|
| **Exact execution program identified** | **20 steps** (0–19), §E.2, with the removability argument for each in §E.3. 2 mutating runs, 14 validations, 7 ordering constraints. |
| **Exact validation evidence identified** | **14 validations**, §D.1, each with objective, prerequisite, mutation flag, rollback flag, success condition and failure condition. Mutation classification of all 10 `register.sh` phases measured in §D.0. |
| **Exact closure conditions for UK-1 and UK-2** | UK-1: **5** evidence items, §I.1. UK-2: **4** evidence items plus a re-measurement requirement, §I.2. |
| **Exact path from READY-CONDITIONAL-ON-GOVERNANCE-SELECTION to READY-FOR-EXECUTION** | Steps **0–8** of §E.2. **0 mutating runs.** Three conditions: governance selection, implementation in E-2/E-3/E-7 order, Stage 0 green with the register committed. |
| **Explicit YES/NO on READY-FOR-EXECUTION reachability** | **YES** — §I.3 and §J.3. |
| No code implemented | No source file modified. |
| No repository files modified | This document is the only addition; ledger sha256 identical; four guard directories 0 dirty; register still absent. |
| No governance selected | No axis assigned. Axis-dependent items stated per value (V-11's target surface, R-B's scope, F.5's replay consequence). |
| No implementation content recommended | §D and §E state what must be run and what must hold. No task's design appears. |
| Four-way separation applied | **[MEASURED]** / **[INFERRED]** / **[UNKNOWN]** / **[EXEC-REQ]** tagged inline throughout, defined in §0.1. |
| Every statement traceable | §K — 11 probes executed this phase, every `file:line` re-read this phase, every prior-phase claim named by section. |

### J.3 The answer

```
================================================================================
  READY-FOR-EXECUTION REACHABLE?                                      Y E S
================================================================================

  Reachable under ....... 12 of 12 admissible closure models
  Mutating runs to REACH it ...................................... 0
  Conditions ..................................................... 3
      1. governance selection on the 5 closure axes
      2. implementation of 17-20 tasks in E-2 / E-3 / E-7 order
      3. Stage 0 green (V-1 … V-6), with the register COMMITTED (E-4)

  State AT ready-for-execution ...... 0 blockers · 3 residuals · 2 unknowns

  ── executing FROM that state ──────────────────────────────────────────────

  Mutating runs required ......................................... 2
      RUN A  register.sh               -> UK-1     9  by_path mints
      RUN B  uga_engine.py run --mint  -> UK-2    28  by_object mints
      proved minimal: the two populations are DISJOINT (overlap 0), and
      register.sh never invokes uga_engine.  Neither run is redundant;
      neither substitutes for the other.

  Runtime validations ........................................... 14
  Rollback procedures ............................................ 3   (+1 class
                                                                       not restorable)
  Reachable terminal states ..................................... 10   (3 distinct triples)

  Best terminal state  T-1 ......... 0 blockers · 3 residuals · 0 unknowns

  Why 3 residuals survive, and why no better program exists:

    RES-3  REDUCED   -- success evidences non-exploitation of the MW-3 window
                        on N real traversals; the window's WIDTH is unmoved.
    RES-4  REDUCED   -- one more verified filesystem; the residual is a
                        universally quantified claim about environments, which
                        no finite number of runs closes.
    R-7w   UNCHANGED -- structurally unreachable by validation: it is a property
                        of the FAILURE path (:893 -> :921), and a SUCCESSFUL run
                        never enters it.  A run that did would be a defect to
                        fix, not evidence to bank.

  All three were bounded by AUTHORIZATION SCOPE, not by uncertainty
  (PHASE05 §F.4; PHASE1 §R-3 / §R-6 / §R-7), and PHASE3 §E.7 established all
  three are invariant across all 12 models.  Execution changes what is KNOWN
  about two of them and nothing about the third.
================================================================================
```

---

## K. Evidence

### K.1 Probes executed this phase

All read-only or operating on in-memory `deepcopy` objects. No `commit()` call, no register creation, no repository mutation.

| ID | Claim established | Method | Outcome | Mutating? |
|---|---|---|---|---|
| **P4-1** | `register.sh` never invokes `uga_engine`; neither `ukb.py` nor `ukbx.py` imports it | `grep` over `register.sh`, `ukb.py`, `ukbx.py` | the only occurrences are prose: `register.sh:157`, `ukb.py:884` | no |
| **P4-2** | Run A's population: **9** `by_path` identifiers, all root `.md` | `ukb._iter_files()` ∖ `by_path`, in memory | 9 files enumerated | no |
| **P4-3** | `ukb build --mint --plan` is read-only and emits the transcribable manifest | executed | `[by_path+9]`, `manifest_digest a6827d8a…`, `preimage_digest 3a2a2532…`, `head 77798202`, `PLAN ONLY — nothing written`; all four guard dirs clean after | **no** |
| **P4-4** | UK-2's premise, and V-5's baseline | `uga_engine.py gate` executed | `UGA-INV-01 FAIL violations=27 measured=6804`; `UGA-INV-10 FAIL violations=27 measured=5207`; identical sets; **2 of 30** FAIL; `GATE FAILED`; `ledger_authority.py` among the 27 | **no** — `cmd_gate`: *"Verify without mutating. Fails closed."* Ledger sha verified identical after |
| **P4-5** | The two allocation populations are **disjoint** | set intersection of P4-2's 9 with `UGA-INV-01`'s violation set | `OVERLAP = 0`, `[]` | no |
| **P4-6** | Phases 2, 3, 4, 8 have **no** dry-run | `grep '"--plan"'` across all three tools | present at `ukb.py:2501` and `uga_engine.py:2181`; **absent from `ukbx.py`** | no |
| **P4-7** | **E-6**: permits cannot both be issued up front | in-memory simulation of run A landing, then re-derivation | `preimage_digest` `3a2a2532…` → `0b7a886d…` (**moved**); `manifest_digest` **unmoved**. `_verify_permit :743-749` refuses on pre-image mismatch | **no** |
| **P4-8** | The non-restorable class and its current state | read `.runtime/governance/*.json` | enforcement 612 runs / seq 612; sync 19 / 19; certification 1 / 1. `git check-ignore -v .runtime` → `.gitignore:12` | no |
| **P4-9** | R-A is complete and non-destructive | `git ls-files` and `git status --porcelain` per guard directory | DATA 17/17, REGISTRIES 6/6, CONTROL-TOWER 12/12, PORTAL 1604/1604 tracked=on-disk; **0 dirty in all four** | no |
| **P4-10** | UK-2's population growth, and the by_path/by_object asymmetry | ledger membership + `ukb._iter_files()` | all **17** `00-BOOK/DATA/*.json` in `by_object`; **0** eligible for `by_path`; mechanism `ukb.py:828-833` — `EXCLUDE_DIR_PREFIXES` names `tools/`, `DATA/`, `REGISTRIES/`, `CONTROL-TOWER/`, `VOLUMES/`, `PORTAL/` because *"the registry must not list itself"* | no |
| **P4-11** | §F.2's hazard: the Phase-1 implementation is absent from HEAD | `git cat-file -e HEAD:00-BOOK/tools/ledger_authority.py` | *fatal: path … exists on disk, but not in `HEAD`*; status `AM` | no |

**Non-mutation, verified before and after every probe:**

```
$ shasum -a 256 00-BOOK/DATA/id-ledger.json
8471e709b178a9a09909bca55f2e8eccb78161db8423026d1d26e4f35c41c20b
$ git status --porcelain -- 00-BOOK/DATA 00-BOOK/REGISTRIES 00-BOOK/CONTROL-TOWER 00-BOOK/PORTAL
(0 lines)
$ ls 00-BOOK/DATA/allocation-permits.json
ls: No such file or directory
```

### K.2 Source references read this phase

| Reference | Content confirmed |
|---|---|
| `register.sh:48` | `set -euo pipefail` |
| `register.sh:99-176` | the `--observe` read-only plane: 4 gates, the drift check, the identity-gap check, RC 0/2/3/4/5 |
| `register.sh:125` | the drift filter — `substr($0,1,2) == "??"` counts untracked as DRIFT (**E-4**) |
| `register.sh:178-190` | the re-entrancy lock, 3600 s stale reclamation, the `EXIT` trap (**R-C**) |
| `register.sh:201` | `fail()` ends in `exit "${2:-1}"` |
| `register.sh:206-259` | the ten phases; `:216` passes no `--permit`; nine `\|\| fail` gates |
| `register.sh:262-273` | the `--guard` drift gate over the four paths |
| `ukb.py:64-65`, `:75-133` | `_now()` wall clock; `_stamp_eq_json` / `_stamps_of` / `_neutralize_stamps` |
| `ukb.py:135-146` | `_dump_json` — `forbid_data_telemetry` + idempotent skip |
| `ukb.py:795`, `:814`, `:821-833` | `EXCLUDE_DIR_PREFIXES`; *"the registry must not list itself"* |
| `ukb.py:1299-1314` | the Phase-1 `LA.commit` call site + 6 `_dump_json` targets |
| `ukb.py:1484-1638` | the six `.md` registry writers |
| `ukb.py:1658-1664` | `_write` — idempotent skip |
| `ukb.py:1947-1961` | `_enforcement_audit` → `T.append_audit` with `fingerprint_dedup` |
| `ukb.py:cmd_enforce` | both `--pre` and post modes call `_enforcement_audit` |
| `ukb.py:2380-2384`, `:2401` | the two further `LA.commit` call sites |
| `ukb.py:2501` | `--plan` on `build` |
| `ukbx.py:55-76`, `:692-698` | `_now`, `_dump`, `_dump_text` — all idempotent |
| `ukbx.py:233`, `:1249` | `append_audit` for sync and certification |
| `ukbx.py:297-430` | `cmd_sync` — signal ledger, cursors, `twin.json :392`, control tower |
| `ukbx.py:445-484` | `_refresh_control_tower :464`, `cmd_twin :472`, the `--check` delegation `:469` |
| `ukbx.py:486-650` | `_cmd_certify` — **zero** write calls; Phase 7 is read-only |
| `ukbx.py:1252-1284` | `cmd_certify` — evidence, audit, report |
| `ukbx.py:1289-1347` | `cmd_portal` — the 1604-page regeneration |
| `ukbx.py:1348+` | `cmd_validate` — no write call |
| `governance_telemetry.py:30-52`, `:79`, `:133-159` | the one location, one writer, one sequence; *"per-clone operational state"*; `append_audit` and the dedup contract |
| `ledger_authority.py:743-749` | the pre-image binding refusal (**E-6**) |
| `ledger_authority.py:216-268` | `_ledger_lock` — directory `flock`, `fcntl is None` → refuse (**RES-4**) |
| `ledger_authority.py:807-822`, `:870`, `:887-893`, `:893`, `:895`, `:920`, `:921` | `_restore`; lock entry; R-2 re-check; `writer`; `raw_after`; the document comparison; the restore (**R-7w**) |
| `ledger_authority.py:290-296`, `:499-506` | append-only removal refusal; CY-1 terminated at one file |
| `uga_engine.py:2097`, `:2125-2161`, `:2181` | the `LA.commit` call site (**RES-3**); `cmd_gate`; `--plan` |
| `.gitignore:3`, `:12` | `.register.lock`; `.runtime/` |
| `platform/tests/test_ledger_authority.py` | `_issue` — the register's only writer, emitting the 9 consumed fields |

### K.3 Prior-phase measurements relied on

| Claim | Source, named |
|---|---|
| The 12 admissible models and their axis values | `PHASE2:§D.3`; `PHASE3:§A` |
| 24 tasks / 13 forced / 0 single-model / 17–20 per model / 0 migration | `PHASE3:§G.1` |
| The `A3 → I-R` and `I-R → Aud1` orderings | `PHASE3:§C.5`; `PHASE2:§E.2` |
| UK-1's structure and prior declination | `PHASE0-E4A:§7`; `PHASE3:§E.4` |
| UK-2's premise and set-growth risk | `PHASE2:§F.1`; `PHASE3:§E.5` |
| RES-3, RES-4, R-7w definitions and model-invariance | `PHASE05:§F.4`; `PHASE1:§R-3`/`§R-6`/`§R-7`; `PHASE3:§E.1-E.3`, `§E.7` |
| Replay accepted after byte restore; refused through the chokepoint | `PHASE2` probe P2-1 |
| Serializer byte inequality forcing document comparison | `PHASE1:§R-11` — 1 786 167 vs 2 274 511 |
| `_verify_permit`'s 9-field binding surface | `PHASE3` P3-7 |
| Every refusal restores the pre-image byte-for-byte | `PHASE1:§R-7` — `read_bytes() == original` on all five tests |
| 77-test authority baseline | `PHASE1:§4`; `PHASE3` P3-8 |
| Zero permits exist, so digest churn is free | `PHASE2` P2-5; `PHASE3` P3-1 |

**No claim rests on unexecuted reasoning without being tagged [INFERRED], and no unresolved question is presented as anything but [UNKNOWN].**

---

## L. Stop condition

Phase 4 ends here.

- **Target state defined before it was answered** — §0.2. READY-FOR-EXECUTION is the point at which execution may commence, not the point at which UK-1/UK-2 are closed. Phase 3's **NO** and Phase 4's **YES** answer different questions and do not conflict.
- **READY-FOR-EXECUTION reachable: YES**, under **12 of 12** models, with **0 mutating runs**, on **3** determinate conditions.
- **Execution program: 20 steps** (0–19), every one shown non-removable — §E.2, §E.3.
- **Runtime validations: 14**, across 4 stages, each with objective / prerequisite / mutation / rollback / success / failure — §D.1.
- **Mutating runs: 2**, proved minimal from three measured facts — `register.sh` never invokes `uga_engine`; the two allocation populations are disjoint (overlap 0); `00-BOOK/DATA` is excluded from `by_path` eligibility while UGA discovery does not exclude it.
- **The two unknowns are discharged by two different commands** — the sharpest finding of this phase, and measured, not inferred.
- **Rollback: 3 procedures + 1 non-restorable class.** R-A is complete and non-destructive over 1639 tracked files in 4 clean directories, **provided it is never widened to `00-BOOK/tools/`** — which would delete `ledger_authority.py`, measured absent from HEAD.
- **Residuals: 3 before, 3 after.** 2 reduced in evidence class, 1 (**R-7w**) structurally unreachable by validation because it is a property of the failure path.
- **Terminal states: 10 reachable**, 3 distinct triples, 5 requiring rollback, **1** reaching 0 blockers and 0 unknowns.
- **Unknowns: 2 before · 0 after success · 1 or 2 after failure.**
- **New blockers introduced by this program: 0.** Validation *reveals* defects; it does not create blockers — §H.4.
- **Governance selected: none.** Decisions taken: **0.** Models or axis values recommended: **0.** Implementation content proposed: **0.**
- **Code changed: none. Repository files modified: none.** Ledger byte-identical, `sha256 8471e709…c20b`; four guard directories 0 dirty; register still absent.

The next act is a governance decision on the five closure axes, followed by implementation, followed by Stage 0. Nothing here prejudges which value any axis takes; §I.4's result — that all 12 models reach the execution gate identically — is stated precisely so it cannot be read as an argument for any one of them.
