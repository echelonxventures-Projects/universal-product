# PHASE 5 — EXECUTION TRANSITION DETERMINATION

| Field | Value |
|---|---|
| Question | What exact transition package moves **READY-FOR-EXECUTION** to **EXECUTION-AUTHORIZED**, under any of the 12 admissible governance models? |
| Answer | **YES — EXECUTION-AUTHORIZED is reachable, under all 12 admissible models**, at a cost of **41 artifacts**, **21 pre-run evidence items**, **10 sequenced stages**, **6 approval subjects** (4 human-level, 2 machine-checkable) and **4 rollback procedures**. The decisive structural result: **EXECUTION-AUTHORIZED is not a single state.** It is **per-run**, it must be entered **twice**, and it **lapses the instant the ledger pre-image moves** — measured, not asserted. |
| Inputs | `PHASE0-GOVERNANCE-INDEPENDENT-DETERMINATION.md`, `PHASE05-GOVERNANCE-INDEPENDENT-REMEDIATION.md`, `PHASE1-GOVERNANCE-INDEPENDENT-IMPLEMENTATION-REPORT.md`, `PHASE2-GOVERNANCE-CLOSURE-DETERMINATION.md`, `PHASE3-IMPLEMENTATION-READINESS-DETERMINATION.md`, `PHASE4-EXECUTION-VALIDATION-DETERMINATION.md` |
| Code changed | **NONE.** No repository file modified. This document is the only file written. |
| Governance selected | **NONE.** No axis assigned. Where an axis value changes a transition requirement it is stated per value without preference. |
| Model recommended | **NONE.** §J.7 states explicitly that the transition package is model-invariant in shape, which is precisely why no model is better positioned. |
| Validation runs executed | **NONE.** No member of V-1 … V-14 was run. `pytest` was not invoked. `register.sh` was not invoked in any mode. `uga_engine gate` was not invoked. |
| Live ledger | unchanged — `sha256 8471e709b178a9a09909bca55f2e8eccb78161db8423026d1d26e4f35c41c20b`, re-verified this phase; `git status --porcelain` over the four guard directories **0 lines** before and after every probe |
| Baseline | working tree at `77798202`; `ledger_authority.py` 933 lines, status `AM`, **absent from HEAD** (re-confirmed); register still absent; `.runtime` sequences 612 / 19 / 1 |
| New this phase | **4 refinements to Phase 4**, each measured in an isolated `/tmp` scratch repository that was created and destroyed within this phase: **P5-1** the drift filter accepts *staged*, so E-4 is sufficient but not necessary; **P5-2** permit issuance itself reads as drift — a required ordering act Phase 4 does not contain; **P5-3** the §F.2 rollback hazard attaches to `reset`-class, **not** `checkout`-class restores; **P5-4** the installed pre-commit hook is a ruff gate, not `register.sh --guard`, and `--install-hooks` is a live deadlock if ever run during the transition window. |

### Compliance with the stated rules

| Rule | Compliance |
|---|---|
| 1. No code changes | No source file modified. Every probe **P5-1 … P5-5** is read-only against this repository, or operates inside a temporary directory under `/tmp` that is not this repository and that was removed before this document was written. |
| 2. No repository mutation | This document is the only addition. Verified: ledger `sha256` identical, four guard directories 0 dirty, register still absent, `.runtime` sequences unmoved at 612 / 19 / 1. |
| 3. No governance selection | No axis assigned. Where axis `B` or `Aud` changes a transition requirement, every value is stated (§B.9, §D.4, §F.6, §G.4). |
| 4. No validation runs | **None of V-1 … V-14 was executed.** §D states what evidence each must produce; it does not produce any of it. Where a Phase-4 measurement is used it is cited to Phase 4's probe, not re-run. |
| 5. No model recommended | None. §J.7 records model-invariance as the reason a recommendation does not follow. |
| 6. Determine only artifacts / evidence / sequencing / approvals / rollback boundaries | The scope of §B–§J. No task content, no code, no design. |
| 7. Distinguish measured fact / inference / governance requirement / execution requirement | Four-way tagging defined in §0.2 and applied inline as **[MEASURED]**, **[INFERRED]**, **[GOV-REQ]**, **[EXEC-REQ]**. |

---

## 0. Frame

### 0.1 The distinction that determines the whole answer

Phase 4 defined **READY-FOR-EXECUTION** as *"the state in which every precondition of the mutating runs is satisfied and verified, so that execution may commence with a determinate outcome"* (`PHASE4:§0.2`). That is a statement about **capability and knowledge**. It says: if you run, you will get a determinate result.

**EXECUTION-AUTHORIZED is not a stronger capability claim. It is a different kind of claim.** It says: you **may** run. The two come apart, and the input chain is the proof that they do.

**[MEASURED]** Nothing in the repository prevented any prior phase from executing `register.sh`. Every phase from Phase 0 onward possessed the command, the interpreter and the working tree. Six consecutive phases declined, each recording the same reason, and none of the six reasons is a capability statement:

| Phase | Recorded declination |
|---|---|
| `PHASE0-E4A:§7` | *"`register.sh` was **not** executed — its behaviour is determined from source … not from a run that would have mutated the repository"* |
| `PHASE05:§F.3` | the register still has no producer; no unit records, marks or consumes a permit |
| `PHASE1:§5.1` | *"`commit()` was **never** called against the production ledger"* |
| `PHASE2:§H.1` | *"No new probe was run against the repository"* |
| `PHASE3:§F.5` | all eight probes read-only or in-memory |
| `PHASE4:§B.1` | *"This phase also declines."* |

**[INFERRED]** Six declinations for one consistent non-capability reason establish that the gate between READY-FOR-EXECUTION and execution is **deontic, not epistemic**. It is not closed by knowing more. It is closed by an authorization that no phase in the chain has held or claimed.

This is the frame for everything below. The transition package is therefore not a longer list of checks — Phase 4 already enumerated the checks. It is the set of artifacts, evidence, sequencing, approvals and rollback boundaries that make an **authorization act** well-founded, bounded and reversible-where-reversible.

```
   epistemic axis  ──────────────────────────────────────────────►

   ┌─────────────────────┐        ┌──────────────────────┐
   │ outcome             │        │ outcome DETERMINATE   │
   │ INDETERMINATE       │  ───►  │                       │
   │ (Phase 3 state)     │        │ READY-FOR-EXECUTION   │
   └─────────────────────┘        └───────────┬──────────┘
                                              │
       deontic axis                           │  ◄── THE GATE PHASE 5 DETERMINES
              │                               │      not reached by more analysis
              ▼                               ▼
                                  ┌──────────────────────┐
                                  │ EXECUTION-AUTHORIZED  │
                                  │ per-run · state-bound │
                                  └──────────────────────┘
```

### 0.2 Evidence classes

Rule 7 requires four distinct classes. Used literally throughout.

| Tag | Meaning |
|---|---|
| **[MEASURED]** | Established by execution or source read **this phase**, or by a named prior-phase probe. A fact. |
| **[INFERRED]** | Derived from measured facts by an argument stated at the point of use. Not itself measured. |
| **[GOV-REQ]** | A requirement on the **governance package** — an artifact, record or approval a deciding party must produce. Cannot be satisfied by code, evidence or analysis. |
| **[EXEC-REQ]** | A requirement on the **execution program** — an act that must be performed or a condition that must hold at run time. Not a fact about the present state. |

The distinction between the last two is the load-bearing one and it is applied strictly: **[GOV-REQ]** items are satisfied by a decision; **[EXEC-REQ]** items are satisfied by an act. No item is tagged both.

### 0.3 Identifier namespaces, disambiguated once

This chain already uses `E-n` for two different things, so this document mints a third prefix rather than overloading a fourth.

| Prefix | Namespace | Owner |
|---|---|---|
| `E-1`, `E-2`, `E-3`, `E-4A` | **blockers / work items** | `PHASE0:§2`; `PHASE1:§6.2` — `E-3` is the `UGA-INV-10` tautology, `E-4A` the absent issuance path |
| `E-1` … `E-7`, `E-4′` | **ordering edges** | `PHASE4:§C.2`; `E-4′` is this phase's refinement of `E-4` |
| `V-1` … `V-14` | **runtime validations** | `PHASE4:§D.1` |
| `F-1`…`F-13`, `O-1`…`O-11` | **implementation tasks** | `PHASE3:§C.0` |
| `T-0` … `T-9` | **terminal states** | `PHASE4:§H.2` |
| **`GA-1` … `GA-9`** | governance artifacts | this phase, §B |
| **`IA-1` … `IA-11`, `IA-C1`, `IA-C2`** | implementation artifacts and pre-gate acts | this phase, §C |
| **`EV-1` … `EV-27`** | **validation evidence items** | this phase, §D — deliberately **not** `E-n`, to avoid collision with the two namespaces above |
| **`S-0` … `S-9`** | sequenced stages | this phase, §E |
| **`R-A` … `R-D`** | rollback procedures | `PHASE4:§F.4` (R-A…R-C); `R-D` this phase |
| **`G-1` … `G-14`** | authorization-gate conditions | this phase, §G |
| **`X-1` … `X-4`** | terminal states new to this phase | this phase, §I |
| **`P5-1` … `P5-5`** | probes executed this phase | this phase, §L |

**[INFERRED]** Where `E-n` appears below without a prefix qualifier it is always an ordering edge or a blocker, never evidence; every evidence reference is `EV-n`.

### 0.4 Authorization-state vocabulary, defined before it is used

Phase 4's terminal-state matrix has no authorization column because Phase 4 had no authorization layer. Phase 5 adds one, and it needs a vocabulary that is not merely "authorized / not authorized", because **[MEASURED]** (`PHASE4` P4-7) the authorization is state-bound and can lapse without ever being used.

| State | Definition | Established by |
|---|---|---|
| **NOT-AUTHORIZABLE** | The gate's conditions cannot be *evaluated*, because governance or implementation is incomplete. Withholding is not a decision here; there is nothing to decide on. | §G.1 conditions unevaluable |
| **AUTHORIZATION-WITHHELD** | Every gate condition is met and authorization was **not** granted. A legitimate terminal state, and a new one — Phase 4 could not express it. | §G.5 |
| **EXECUTION-AUTHORIZED** | For **one named run**: the gate is satisfied and a permit verifying against that run's measured manifest exists. | §G.2 |
| **AUTHORIZATION-LAPSED** | A permit exists but the pre-image has moved, so `_verify_permit` refuses it. The authorization was never used and is now void. | **[MEASURED]** `ledger_authority.py:743-749`; `PHASE4` P4-7 |
| **AUTHORIZATION-CONSUMED** | The run landed. Under `B2` the permit is additionally marked spent; under `B1` it is merely lapsed by pre-image movement. | §F.6 |
| **EXECUTION-COMPLETE** | Both runs landed and both unknowns retired. | §I, row T-1 |

---

## A. Current terminal state

### A.1 What Phase 4 determined

`PHASE4:§J.3`, verbatim in substance:

```
READY-FOR-EXECUTION REACHABLE?  ......................... YES
  under ................................................. 12 of 12 admissible models
  mutating runs required to REACH it .................... 0
  conditions ............................................ 3
      1. governance selection on the 5 closure axes
      2. implementation of 17-20 tasks in E-2 / E-3 / E-7 order
      3. Stage 0 green (V-1 … V-6), with the register COMMITTED (E-4)
  state AT ready-for-execution .... 0 blockers · 3 residuals · 2 unknowns
```

Executing *from* that state: **2** mutating runs, **14** runtime validations, **3** rollback procedures, **10** reachable terminal states, best outcome `T-1` at 0 blockers / 3 residuals / 0 unknowns.

### A.2 The distinction that the task's premise requires

The task asks for the package that moves *from* READY-FOR-EXECUTION. **[MEASURED]** the repository does not occupy that state, and the gap is not marginal.

| Phase-4 condition | Satisfied today? | Evidence, re-verified this phase |
|---|---|---|
| 1. Governance selection on 5 axes | **NO** | No selection record exists. Phases 2, 3 and 4 each recorded *"Governance selected: none. Decisions taken: 0."* |
| 2. Implementation of 17–20 tasks | **NO — 0 of 17–20** | **P5-5**: register absent (`ls` → *No such file*); `ledger_authority.py` 933 lines, unchanged from the Phase-3/4 baseline; ledger `sha256 8471e709…c20b` |
| 3. Stage 0 green, register committed | **NO — unreachable** | **[INFERRED]** V-2 cannot pass while the register does not exist; V-6 has no permit to round-trip |

**[INFERRED]** Therefore Phase 4's terminal state is a **reachability determination, not an occupancy**. The chain's actual position is still `PHASE3`'s: **READY-CONDITIONAL-ON-GOVERNANCE-SELECTION**.

This is not a quibble, and stating it changes the deliverable. If READY-FOR-EXECUTION were occupied, the transition package would be §B.7–§B.9 plus §D.1 plus one approval. Because it is not, the package must carry the occupancy prerequisites as well. **§B, §C and §D therefore enumerate the full package**, and §E.6 marks precisely which stages are occupancy prerequisites (already determined by Phase 4) and which are the transition proper (determined here for the first time).

### A.3 Baseline re-verified this phase, read-only

**P5-5**, executed this phase. No mutation; no validation run.

```
$ shasum -a 256 00-BOOK/DATA/id-ledger.json
8471e709b178a9a09909bca55f2e8eccb78161db8423026d1d26e4f35c41c20b        (unchanged)

$ ls 00-BOOK/DATA/allocation-permits.json
ls: 00-BOOK/DATA/allocation-permits.json: No such file or directory

$ git status --porcelain -- 00-BOOK/DATA 00-BOOK/REGISTRIES 00-BOOK/CONTROL-TOWER 00-BOOK/PORTAL
(0 lines)

$ git rev-parse --short HEAD
77798202

$ git status --porcelain -- 00-BOOK/tools/ledger_authority.py
AM 00-BOOK/tools/ledger_authority.py

$ git cat-file -e HEAD:00-BOOK/tools/ledger_authority.py
fatal: path '00-BOOK/tools/ledger_authority.py' exists on disk, but not in 'HEAD'

tracked file counts   DATA 17 · REGISTRIES 6 · CONTROL-TOWER 12 · PORTAL 1604   (= 1639)
.runtime sequences    enforcement 612 · sync 19 · certification 1
line counts           ledger_authority.py 933 · uga_engine.py 2191 · ukb.py 2579 · register.sh 282
```

**[MEASURED]** Every load-bearing baseline fact in `PHASE4:§A` holds unchanged. Nothing has moved between Phase 4 and Phase 5.

### A.4 Terminal state, stated exactly

```
POSITION ................. READY-CONDITIONAL-ON-GOVERNANCE-SELECTION   (PHASE3 terminal)
DETERMINED REACHABLE ..... READY-FOR-EXECUTION, 12 of 12 models        (PHASE4 terminal)
AUTHORIZATION STATE ...... NOT-AUTHORIZABLE
    reason: gate conditions G-1 (governance) and G-2 (implementation) are
            unevaluable, not unmet — there is no selection record to evaluate
            and no artifact to evaluate it against

BLOCKERS   artifact level ......... 5   E-4A, E1-F3, E-3, RES-1, RES-2
           decision level ......... 5   (0 only after a selection record exists)
RESIDUALS .......................... 3   RES-3, RES-4, R-7w  — all latent
UNKNOWNS ........................... 2   UK-1, UK-2
MUTATING RUNS PERFORMED IN THE CHAIN  0
IDENTITIES ALLOCATED IN THE CHAIN ..  0
```

---

## B. Governance package inventory

Every governance artifact that must exist before execution authorization. All are **[GOV-REQ]**: none can be produced by code, by evidence, or by further determination. Each carries its forcing basis and whether it is model-invariant.

### B.0 What "governance artifact" means here, and what it excludes

**[INFERRED]** `PHASE2:§E.1` counts **13 decisions** for a complete governance specification, of which **5** determine closure and **8** are closure-redundant. Phase 5 needs artifacts, not decisions, and the two do not map one-to-one: several decisions can be carried by one record, and — the finding of this section — **two required governance artifacts correspond to no decision in Phase 2's 13.**

Excluded by construction, and each exclusion is a positive result rather than an omission:

| Not a governance artifact | Why |
|---|---|
| The permit register | An implementation artifact (§C, IA-3). Governance decides *that* permits exist and what they bind; it does not write one. |
| Any individual permit | An **execution** artifact issued at run time against a measured manifest (§D, EV-11 / EV-15). **[MEASURED]** it cannot be pre-issued: `PHASE4` P4-7 measured the pre-image moving, and `:743-749` refuses on the mismatch. |
| The specification artifact | Implementation (§C, IA-1). `PHASE3:§D.2` measured the delta from governance-complete to implementation-ready as *"1 specification artifact and zero code changes"* — so the specification sits on the far side of the governance boundary. |
| FD-1 / FD-4 assignments as *closure* inputs | **[MEASURED]** provably vacuous — `PHASE2` M1/M2, `PHASE3` P3-2/P3-7: `_verify_permit` reads no `issuer`, `signature`, `issued_at`, `revoked`, `uses` or `single_use`, and `:728-732` is unconstrained string equality with no allow-list. They appear below in **GA-2** as *completeness* requirements only. |

### B.1 GA-1 — Closure-model selection record

| Aspect | Determination |
|---|---|
| **Content** | An assignment to each of the 5 closure-determining axes: `I`, `A`, `B`, `D`, `Aud`, resolving to exactly one of `Z-01 … Z-12`. |
| **Forced values** | **[MEASURED]** `PHASE3:§A` — `I = I-R` and `A = A3` in all 12; every alternative either leaves a blocker UNRESOLVED or creates one of NB-1…NB-6. Free: `B ∈ {B1,B2}`, `D ∈ {D1,D2}`, `Aud ∈ {Aud1,Aud2,Aud3}`. |
| **Why it is the first artifact** | **[MEASURED]** `PHASE3:§C.4` — 4–7 of each model's 17–20 tasks are axis-conditional. Edge **E-1**. Implementation content is undefined without it. |
| **Model-invariant?** | The requirement is; the content is the selection itself. |
| **Basis** | `PHASE2:§E.1`, `§D.3`; `PHASE3:§A` |

### B.2 GA-2 — Redundant-decision completion record

| Aspect | Determination |
|---|---|
| **Content** | Answers to the **8** closure-redundant decisions: FD-1 issuer identity · FD-4 ledger-authority ownership · modifier `R` register trust · modifier `T` expiry instant · `B2a`/`B2b` use-record location · the `Aud1` pair selection among 6 sub-variants · the `I-R` issuance mechanism among 3 sub-variants · the bounded-reuse threshold `n`. |
| **Why required despite changing no cell** | **[MEASURED]** `PHASE2:§E.4` — *"A governance specification must answer 13 questions to be complete; 5 of those answers determine the closure outcome; 8 are redundant with respect to closure."* Two of the eight, however, **do** change the transition package even though they change no closure cell, and that is a Phase-5 finding: `B2a`/`B2b` changes **R-B's rollback scope** (§F.6), and the `R` modifier must be pinned to `R1` or the model is not one of the 12 (§B.3). |
| **Model-invariant?** | Yes — 8 answers required under all 12. |
| **Basis** | `PHASE2:§E.1`, `§E.4`, `§C.3` |

### B.3 GA-3 — Zero-new-blocker attestation

| Aspect | Determination |
|---|---|
| **Content** | An explicit statement that the selected model introduces none of NB-1 … NB-6: modifier `R = R1` (else **NB-2**, no trust anchor); `D ≠ D3` (else **NB-1**); `Aud ∉ {Aud4, Aud5}` (else **NB-3** / **NB-5**); `A ≠ A4` (**NB-4**, and CONTRADICTED by CX-6); `I ≠ I-D` (else **NB-6**); and that the `I-D × Aud4` pairing (CX-4) is not taken. |
| **Why a separate artifact from GA-1** | **[INFERRED]** GA-1 records five axis values. Whether those values constitute one of the 12 is a **derived property of the record**, not part of it — and it depends on a modifier (`R`) that is not one of the five axes. **[MEASURED]** `PHASE2:§D.3` puts `R = R1` outside the five-axis product, so a five-axis record is consistent with a 13th, non-admissible model. The attestation is what closes that gap. |
| **Model-invariant?** | Yes. |
| **Basis** | `PHASE2:§C.9`, `§D.3`; `PHASE3:§A` |

### B.4 GA-4 — Model-space reading declaration

| Aspect | Determination |
|---|---|
| **Content** | A declaration of whether the 12-model or the 24-model reading is adopted — i.e. whether `I-D`'s **NB-6** (a dead authorization interface) counts as a blocker. |
| **Why required** | **[MEASURED]** `PHASE2:§D.3` declined the judgment as *"itself a governance question"*; `PHASE3:§A` inherited the decline **and measured that the results are not transferable**: under the 24-model reading the forced set *changes shape* — `F-1`'s register producer is replaced by an admission-predicate rewrite of `:714-721` — *"It is therefore not a superset relation, and the 12-model results below do not transfer unchanged."* **[INFERRED]** So every count in Phase 3, Phase 4 and this document is conditional on this declaration, and it has been deferred three times. It cannot be deferred past the gate: the transition package's own contents depend on it. |
| **Model-invariant?** | Yes — required under all 12, and it is the artifact that *establishes* which set of 12 is in play. |
| **Basis** | `PHASE2:§D.3`; `PHASE3:§A` |

### B.5 GA-5 — Residual acceptance instrument

| Aspect | Determination |
|---|---|
| **Content** | Explicit acceptance of **RES-3** (the MW-3 read-to-lock window), **RES-4** (advisory, filesystem-dependent `flock`) and **R-7w** (post-hoc detection between `:893` and `:921`), as bounded properties that execution will **activate** and will not close. |
| **Why an acceptance is required, not merely a note** | **[MEASURED]** `PHASE3:§E.7` — all three are **LATENT → ACTIVE under all 12 models**: *"Today no production write reaches `writer`, so no write can land inside the window. `I-R` opens the path."* **[MEASURED]** `PHASE05:§F.4` and `PHASE1:§R-3`/`§R-6`/`§R-7` bounded all three **by authorization scope** — each was declined as *"a larger change than this phase covers."* **[INFERRED]** A bound whose justification is *"nobody authorized the fix"* is discharged only by the authorizing party. Executing converts three unexercised bounds into three live ones; the party that authorizes execution is the party that accepts them. |
| **What execution does to them** | **[MEASURED]** `PHASE4:§G` — RES-3 **REDUCED**, RES-4 **REDUCED**, R-7w **UNCHANGED**. R-7w is unchanged for a structural reason: it is a property of the *failure* path, and a successful run never enters it. The acceptance of R-7w is therefore permanent within this program. |
| **Model-invariant?** | Yes — `PHASE3:§E.7`: all three invariant across all 12. |
| **Basis** | `PHASE05:§F.4`; `PHASE1:§R-3`/`§R-6`/`§R-7`; `PHASE3:§E.1-E.3`, `§E.7`; `PHASE4:§G` |

### B.6 GA-6 — Unknown acknowledgment and closure-evidence definition

| Aspect | Determination |
|---|---|
| **Content** | Acknowledgment that **UK-1** and **UK-2** are open at the gate and will be closed only *by* execution, plus adoption of their closure-evidence sets: UK-1's **5** items (`PHASE4:§I.1`) and UK-2's **4** items plus the re-measurement requirement (`PHASE4:§I.2`). |
| **Why the evidence definition must be adopted in advance** | **[INFERRED]** and this is the sharpest point in §B. If the evidence set is chosen *after* the run, the run cannot fail. **[MEASURED]** `PHASE4:§I.1` establishes that item 5 — byte-stability on re-run — is *"required, not optional. Without it, `register.sh` completing once is compatible with the drift gate never being green."* A post-hoc definition would retire UK-1 on a one-shot success. Adopting the definition before the gate is what makes the run falsifiable. |
| **Model-invariant?** | The UK-1 set is. **One UK-2 item is axis-parameterized:** **[MEASURED]** `PHASE4:§I.2` item 3 — `UGA-INV-10`'s target is surface **30** under `Aud1`/`Aud2` and surface **29** under `Aud3`, where the invariant is retired. Stated per value, not chosen. |
| **Basis** | `PHASE3:§E.4`, `§E.5`; `PHASE4:§I.1`, `§I.2` |

### B.7 GA-7 — Irreversible-mutation authorization instrument

**This artifact corresponds to no decision in `PHASE2`'s 13, and it is the one the chain has never held.**

| Aspect | Determination |
|---|---|
| **Content** | An authorization to perform an irreversible act on the repository, naming: the two commands, the allocation populations (**9** `by_path`; the `by_object` count re-measured at issuance), the two irreversible side-effect classes, and the authorizing party. |
| **Why it is a distinct artifact** | **[MEASURED]** Six phases declined execution, none on capability grounds (§0.1). **[MEASURED]** the repository states the requirement in its own voice, in the one place that reports an identity gap — `register.sh:150-153`: *"Required action: obtain REG-AUTO-001 authorization to reconcile the gap; allocation is irreversible and is not a remediation this read-only report may authorize."* **[INFERRED]** That is the gate named by the artifact under determination, in source, addressed to exactly this act. It is not an inference from the chain's behaviour; the chain's behaviour is the *second* witness. |
| **Irreversible side effects it must name** | **[MEASURED]** `PHASE4:§I.5`, two classes. **(i)** Permanent identity allocation — append-only, and `assert_append_only` **refuses removal** (`:290-296`), so the allocation cannot be undone *through the authority*. **(ii)** `.runtime/governance` sequence advance — gitignored (`.gitignore:12`), not restorable by any rollback procedure, currently at **612 / 19 / 1** (**P5-5**). |
| **Scope bound it must carry** | **[EXEC-REQ]** the authorization must be bounded to the two named runs and their permit scopes. **[MEASURED]** the mechanism already exists and is enforced: `_verify_permit` reads `scope.maps` (`:769`) and `scope.max_allocations` (`:778`), so an over-broad run is refused by the authority itself, not merely by policy. |
| **Model-invariant?** | Yes. No axis value removes the irreversibility. |
| **Basis** | **derived this phase** from `register.sh:150-153` (read this phase) + the six recorded declinations + `PHASE4:§I.5` |

### B.8 GA-8 — Rollback authorization with scope bound

| Aspect | Determination |
|---|---|
| **Content** | Pre-authorization to execute **R-A**, **R-B**, **R-C** and **R-D** (§F), with the scope bounds and prohibitions of §F.3 attached. |
| **Why pre-authorization and not a decision at failure time** | **[MEASURED]** `PHASE4:§F.6` — restoration **destroys the evidence** of what failed, so V-8's capture must precede it. **[INFERRED]** If rollback needs an approval sought *after* a mid-transaction failure, the repository sits in a mutated-and-unsealed state for the duration of that approval, and the pressure to restore before capturing is at its maximum exactly when capture matters most. Pre-authorizing removes the decision from the failure path. |
| **The prohibition it must carry — corrected this phase** | **[MEASURED]** **P5-3**: `git checkout HEAD -- <path>` does **not** delete an `AM` file, whereas `git reset --hard` **does**. So the hazard is not scope-width; it is **primitive class**. See §F.3. |
| **Model-invariant?** | The requirement is. **R-B's scope is axis-parameterized**: **[MEASURED]** `PHASE4:§F.1` — `B2b` adds one tracked artifact and `Aud1` adds one; `B1`, `B2a`, `Aud2`, `Aud3` add none. |
| **Basis** | `PHASE4:§F.2`, `§F.4`, `§F.6`; **P5-3** this phase |

### B.9 GA-9 — Axis-parameterized condition record

| Aspect | Determination |
|---|---|
| **Content** | The values that the selected axes fix for three conditions that are otherwise unstatable. |
| **The three** | **(i) V-11's success condition.** **[MEASURED]** `PHASE4:§E.4` — target invariant surface **30** under `Aud1`/`Aud2`, **29** under `Aud3`. **(ii) R-B's scope.** Which new tracked artifacts exist to remove: `B2b` → +1, `Aud1` → +1. **(iii) The replay-after-rollback consequence.** **[MEASURED]** `PHASE4:§F.5` Interaction 1 — under `B1` the restored permit verifies again and a retry needs no new permit; under `B2` the permit stays **spent** while the allocation is **undone**, so a retry requires a fresh permit. |
| **Why recorded rather than derived at run time** | **[INFERRED]** Each is derivable from GA-1, but each is consumed by an **[EXEC-REQ]** under time pressure — (i) at V-11's evaluation, (ii) and (iii) inside a failure path. `PHASE4:§F.5` states it as a requirement in its own words: *"The program must record which of these applies once the axis is selected, because it determines whether a retry after rollback needs a fresh permit."* |
| **Model-invariant?** | The requirement is; all three contents are axis-determined. |
| **Basis** | `PHASE4:§E.4`, `§F.1`, `§F.5`, `§I.2` |

### B.10 Governance package summary

| ID | Artifact | Class | Corresponds to a `PHASE2` decision? | Axis-parameterized content? |
|---|---|---|---|---|
| **GA-1** | Closure-model selection record (5 axes → one `Z-nn`) | [GOV-REQ] | yes — the 5 closure decisions | is the selection |
| **GA-2** | Redundant-decision completion record (8 answers) | [GOV-REQ] | yes — the 8 redundant decisions | no |
| **GA-3** | Zero-new-blocker attestation (`R1`; NB-1…NB-6 avoided) | [GOV-REQ] | **no** — a derived property + a modifier | no |
| **GA-4** | Model-space reading declaration (12 vs 24) | [GOV-REQ] | **no** — declined 3 times | no |
| **GA-5** | Residual acceptance (RES-3, RES-4, R-7w) | [GOV-REQ] | no | no |
| **GA-6** | Unknown acknowledgment + closure-evidence adoption | [GOV-REQ] | no | **yes** — UK-2 item 3 |
| **GA-7** | Irreversible-mutation authorization | [GOV-REQ] | **no** — named in source at `register.sh:150-153` | no |
| **GA-8** | Rollback authorization + scope bound | [GOV-REQ] | no | **yes** — R-B's scope |
| **GA-9** | Axis-parameterized condition record | [GOV-REQ] | no | **yes** — all three contents |

```
GOVERNANCE ARTIFACTS REQUIRED BEFORE EXECUTION AUTHORIZATION ....  9
    corresponding to a PHASE2 decision ..........................  2   GA-1, GA-2
    identified for the first time in this phase ..................  7   GA-3 … GA-9
    with axis-parameterized content .............................  3   GA-6, GA-8, GA-9
    model-invariant in requirement .............................. 9 of 9
    satisfiable by code, evidence or further analysis ............  0
```

**[INFERRED]** Seven of nine are new because Phase 2 enumerated the decisions a *governance specification* needs, while this phase enumerates the artifacts an *authorization* needs. Those sets overlap in two places and are otherwise disjoint. **The single most consequential of the seven is GA-7**, because it is the only one whose absence has demonstrably stopped six consecutive phases.

---

## C. Implementation package inventory

Every implementation artifact required before execution authorization. Sites and counts are carried from `PHASE3:§C.0` and `§D`, re-grounded on the line counts re-verified this phase (`ledger_authority.py` 933, `uga_engine.py` 2191, `ukb.py` 2579, `register.sh` 282).

### C.1 The artifacts

| ID | Artifact | Tasks it carries | Kind | Models | New file? |
|---|---|---|---|---|---|
| **IA-1** | **Specification artifact** — a `PHASE05`-grade design for the 17–20 tasks | — | spec | 12 | **yes** |
| **IA-2** | `00-BOOK/tools/ledger_authority.py` modification | F-2 (`:548-568`), F-3 (`:648-661`), + O-3 (`:870-933`) under `B2`, O-7 (`:714-804`) under `D2`, O-11 under `B2 ∧ D2` | code | 12 | no |
| **IA-3** | **`00-BOOK/DATA/allocation-permits.json`** — the permit register | F-1 | code output | 12 | **yes** |
| **IA-4** | Permit plumbing: `register.sh:216` → `ukb.py:1299` | F-4 | code | 12 | no |
| **IA-5** | `00-MASTER/UCOS-UGA-001/uga_engine.py:1331-1335` — E-3 disposal | F-5 | code | 12 | no |
| **IA-6** | `uga-declaration.json` — invariant-surface update | F-6 | config | 12 | no |
| **IA-7** | Source-claim amendments | F-7 (≥1 of `:490-497`, `:519`, `:570-577`, `:763-766`), + O-1 under `B1`, O-5 under `D1` | doc | 12 | no |
| **IA-8** | `UGA-INV-10` citation reconciliation — **58 files** | F-8 | doc | 12 | no |
| **IA-9** | `platform/tests/test_ledger_authority.py` extension | F-9, F-10, F-11, + O-2/O-4/O-6/O-8/O-10 as selected | test | 12 | no |
| **IA-10** | UGA invariant test pinning the E-3 disposal | F-12 | test | 12 | no |
| **IA-11** | Conditional new tracked governance artifact | O-9 under `Aud1` (audit log); the `B2b` use record | code output | ≤10 | **yes** |

**[MEASURED]** `PHASE3:§F.3` — **0 migration artifacts** under all 12 models: the live ledger already satisfies every property Phase 1 added, `I-R` is purely additive, and `A3`'s digest churn invalidates nothing because zero permits have ever existed.

**F-13** (re-measure the 30-invariant surface) appears in no row above. **[INFERRED]** It is not an implementation artifact — it is validation evidence, and it appears in §D as **EV-13**.

### C.2 Two commits that are implementation requirements, not conveniences

**[EXEC-REQ]** Both are acts, not files, and both must occur before the gate.

| ID | Act | Forcing fact | Minimum sufficient state — **corrected this phase** |
|---|---|---|---|
| **IA-C1** | Bring `00-BOOK/DATA/allocation-permits.json` under version control | **[MEASURED]** `register.sh:125`'s `--observe` drift filter is `substr($0,1,2) == "??" \|\| substr($0,2,1) != " "`; an untracked register is `??` → DRIFT → `RC=3` | **[MEASURED]** **P5-1**: **staged with a clean worktree suffices** for `--observe`. `A ` → 0 drift lines. `git commit` is sufficient but **not necessary**. See §C.3. |
| **IA-C2** | **Commit** `00-BOOK/tools/ledger_authority.py` | **[MEASURED]** status `AM`, absent from HEAD (**P5-5**). It is the entire Phase-1 implementation — all twelve closures — and exists in no commit | **[MEASURED]** **P5-3**: staging is **insufficient**. `git reset --hard` deletes an `AM` file; the index does not protect it. Only a commit does. See §F.3. |

**[INFERRED]** The two acts have **opposite** minimum requirements, and this asymmetry is measured rather than argued: the register needs only the *index* because `--observe`'s filter reads the index column, while `ledger_authority.py` needs a *commit* because the rollback primitive that endangers it resets the index.

### C.3 P5-1 — the drift filter, measured across all six states

Executed this phase in an isolated `/tmp` scratch repository, against `register.sh:125`'s exact awk expression and `:265-267`'s bare `git status --porcelain`. The scratch repository was removed before this document was written. **No probe touched this repository.**

| Register / permit state | porcelain | `--observe` filter (V-2 / V-9) | `--guard` bare (drift gate) |
|---|---|---|---|
| untracked | `??` | **DRIFT** | **DRIFT** |
| staged, worktree clean | `A ` | **PASS** | **DRIFT** |
| staged + permit appended in worktree | `AM` | **DRIFT** | **DRIFT** |
| committed, clean | *(empty)* | **PASS** | **PASS** |
| committed + permit appended, unstaged | ` M` | **DRIFT** | **DRIFT** |
| committed + permit appended, staged | `M ` | **PASS** | **DRIFT** |

**Three consequences, each [INFERRED] from the table.**

1. **Phase 4's E-4 is sufficient but not necessary.** `PHASE4:§E.2` step 2 requires *"COMMIT the register"*, justified in `§E.3` by *"`register.sh:125` counts `??` as drift."* That justification establishes only that **untracked** fails. Staged passes. The correction matters because staging is materially more reversible than committing — it makes rollback procedure **R-D** (§F.5) unnecessary.

2. **`--guard` is strictly stricter than `--observe`**, and the difference is the index column. Any staged-but-uncommitted change under the four guard directories fails `--guard`. **[INFERRED]** So a program that stages rather than commits satisfies the authorization gate but leaves the `--guard` drift gate red — which `PHASE4:§I.1` item 5 correctly identifies as *"a permanent `exit 3` in CI and pre-commit."* **The two are not in conflict; they are different requirements at different times**: staged is the minimum for the gate, committed is the minimum for CI-consistency at the end of the program.

3. **Permit issuance itself reads as drift.** This is **P5-2**, and it is a required ordering act that appears nowhere in Phase 4. See §C.4.

### C.4 P5-2 — permit issuance dirties the register, and Phase 4's sequence does not stage it

**[MEASURED]** Issuing a permit writes into `00-BOOK/DATA/allocation-permits.json`. From the table above, the resulting state is ` M` (if the register was committed) or `AM` (if staged) — and **both are DRIFT under `--observe`**.

**[MEASURED]** `PHASE4:§E.2`'s step order is: step 6 `V-2 register.sh --observe` … step 9 *issue permit A* … step 10 run A … step 13 `V-9 register.sh --observe`. So V-2 runs before any permit exists and is unaffected. **V-9 runs after permit A has been issued and used.**

**[INFERRED]** Therefore V-9 fails with `RC=3` on the permit's own uncommitted write, independently of the regenerated registers. `PHASE4:§D.1` anticipated an `RC=3` at V-9 and attributed it to *"the regenerated registers are uncommitted"* — correct as far as it goes, and incomplete: the permit is a second, independent drift source in the same directory, and it is the one the program creates deliberately two steps earlier.

**[EXEC-REQ]** The remedy is one act, twice: **after each permit issuance, stage the register before the next `--observe` runs.** Two additional staging acts, inserted after Phase 4's steps 9 and 14. They allocate nothing, they mutate no ledger, and without them V-9 cannot return `RC=0` — which **[MEASURED]** is item 4 of UK-1's five-item closure set (`PHASE4:§I.1`).

**[INFERRED]** This is the only defect this phase found in Phase 4's 20-step program, and it is an omission of two index operations rather than an error in the program's shape. The 2 mutating runs, 14 validations and minimality argument are unaffected.

### C.5 Implementation package summary

```
IMPLEMENTATION ARTIFACTS REQUIRED BEFORE EXECUTION AUTHORIZATION .. 11   IA-1 … IA-11
    new files ..................................................... 3   IA-1, IA-3, IA-11
    existing files modified ....................................... 8
    required under all 12 models .................................. 10  (IA-11 ≤ 10 models)
    migration artifacts ........................................... 0

PRE-GATE ACTS (not files) .......................................... 2   IA-C1, IA-C2
    minimum state for IA-C1 (register) ............ STAGED, worktree clean   [P5-1]
    minimum state for IA-C2 (ledger_authority.py) . COMMITTED                [P5-3]
    additional staging acts derived this phase ..... 2                        [P5-2]

TASKS CARRIED BY THESE ARTIFACTS ............................... 17 - 20
    forced (all 12) ............................................... 13   F-1 … F-13
    conditional ................................................. 4 - 7   from O-1 … O-11
    required by exactly one model .................................. 0
    forced share ............................................. 65% - 76%

ORDERING EDGES INTERNAL TO IMPLEMENTATION .......................... 3
    E-2  A3 binding (F-2, F-3)  ->  register producer (F-1)     all 12
    E-3  F-1                    ->  F-4 permit plumbing        all 12
    E-7  F-1                    ->  O-9 Aud1 tracked log        4 of 12
```

---

## D. Validation package inventory

All evidence that must exist **before** each mutating run. Nothing in this section was produced by this phase: **[MEASURED]** Rule 4 forbids validation runs, and none of V-1 … V-14 was executed. Each row states what the evidence is, which Phase-4 validation produces it, and why the run cannot proceed without it.

### D.0 One structural correction to the framing

Phase 4 asks for evidence "before run A" and "before run B". **[MEASURED]** `PHASE4:§C.2` — the **A ↔ B order is FREE**: the populations are disjoint (P4-5, overlap 0) and neither command invokes the other (P4-1). **[MEASURED]** `PHASE4` edge **E-6** — permits must be issued sequentially, each after the prior run lands.

**[INFERRED]** Therefore the prerequisite set is not a property of *which command* runs, but of **which position it occupies**. Five evidence items attach to the second position regardless of which command fills it. §D.1 and §D.2 are stated per command as the task requires, with position-conditional items marked **[POS-2]**.

### D.1 Evidence required before `register.sh` validation

| ID | Evidence | Produced by | Shared with run B? | Why the run cannot proceed without it |
|---|---|---|---|---|
| **EV-1** | Authority-suite transcript, **≥ 77** passed | V-1 | **yes** | **[MEASURED]** 77 is the Phase-1 terminal baseline (`PHASE1:§4`, `PHASE3` P3-8). A count below 77 means a Phase-1 test was removed by the 17–20 tasks |
| **EV-2** | `register.sh --observe` → `RC=0`, *"OBSERVATION PASSED"* | V-2 | no | **[MEASURED]** the only pre-mutation check of gates 0/5/6/7 plus drift plus the identity-gap check. `RC=2` gate · `RC=3` drift · `RC=4` enforcement · `RC=5` undetermined gap |
| **EV-3** | `ukb build --mint --plan` transcript: `manifest_digest`, `preimage_digest`, `head`, `[by_path+9]`, *"PLAN ONLY — nothing written"* | V-3 | no | **[MEASURED]** edge **E-6** — permit A must bind **these** digests. `_verify_permit` refuses on `manifest_digest :735` and `preimage_digest :743` |
| **EV-4** | Post-plan zero-dirty proof over the four guard directories | V-3 | **yes** | **[MEASURED]** `PHASE4` P4-3 established `--plan` is read-only. **[EXEC-REQ]** it must be re-established, because `PHASE4:§F.2` requires the zero-dirty precondition to hold immediately before any restore, and it is *"a property of the present working tree, not a guarantee"* |
| **EV-5** | Permit round-trip transcript: one acceptance, plus **9** independent refusals | V-6 | no | **[MEASURED]** `PHASE3` P3-7 — `_verify_permit` performs exactly 9 permit reads. This is the last point at which E-4A's closure is falsifiable **without mutating** |
| **EV-6** | Ledger `sha256` immediately before issuance | — | **yes** | **[MEASURED]** `PHASE4:§F.6` — proves R-A returned the exact pre-image, closing the restore itself |
| **EV-7** | `.runtime` sequence triple before (currently **612 / 19 / 1**) | — | **yes** | **[MEASURED]** `PHASE4:§F.3` — the **only** evidence that survives a full tracked rollback intact |
| **EV-8** | Evidence-destination designation | — | **yes** | **[MEASURED]** `PHASE4:§F.6` — anything written inside the four guard directories reads as drift (`:265-267`). The destination must be outside them and outside version control |
| **EV-9** | Register at least **staged**, worktree clean | IA-C1 | **yes** | **[MEASURED]** **P5-1** — `??` → `RC=3`; `A ` → pass |
| **EV-10** | `ledger_authority.py` **committed** | IA-C2 | **yes** | **[MEASURED]** **P5-3** — until committed, a `reset`-class rollback deletes the entire Phase-1 implementation |
| **EV-11** | Permit A record — the **9** fields, bound to EV-3's digests | issuance | no | **[MEASURED]** `commit :841` — `permit` is mandatory with no default; `None` is refused at the type check (`PHASE3` P3-1) |

```
EVIDENCE ITEMS REQUIRED BEFORE register.sh VALIDATION ..... 11   EV-1 … EV-11
    shared with run B ..................................... 7   EV-1, EV-4, EV-6, EV-7, EV-8, EV-9, EV-10
    specific to register.sh ............................... 4   EV-2, EV-3, EV-5, EV-11
```

### D.2 Evidence required before `uga_engine` validation

| ID | Evidence | Produced by | Position | Why the run cannot proceed without it |
|---|---|---|---|---|
| **EV-1, EV-4, EV-6, EV-7, EV-8, EV-9, EV-10** | *(as §D.1 — shared)* | — | either | **[MEASURED]** EV-9 is required here for a second reason: **[INFERRED]** the register must exist for permit B to exist, and **[MEASURED]** P4-10 — bringing it under version control is what grows the `by_object` population 27 → 28 (edge **E-5**) |
| **EV-12** | `uga_engine.py run --plan` transcript — the `by_object` manifest | V-4 | either | **[MEASURED]** `--plan` exists at `uga_engine.py:2181`. Permit B must bind this manifest |
| **EV-13** | `uga_engine.py gate` **baseline**: 30 invariants with pre-mint violation counts | V-5 | either | **[MEASURED]** `PHASE4:§E.3` — V-11's condition *"no invariant that passed at V-5 now fails"* is **unstatable** without it. Baseline as measured by `PHASE4` P4-4: `UGA-INV-01 FAIL violations=27 measured=6804`; `UGA-INV-10 FAIL violations=27 measured=5207`; **2 of 30** FAIL, so **28 must still pass** |
| **EV-14** | **Re-measured** `by_object` population at issuance | V-4 | either | **[MEASURED]** `PHASE4:§I.2` — the population is **not** the 27 measured today; **[MEASURED]** P4-10 — all 17 `00-BOOK/DATA/*.json` are in `by_object` and **0** are `by_path`-eligible, so the register makes it the 18th and the population **28**. **[UNKNOWN]** whether `B2b` or `Aud1` adds a further one. *"The program must re-measure immediately before issuance; the number cannot be fixed in advance"* |
| **EV-15** | Permit B record, bound to EV-12 and EV-16 | issuance | either | as EV-11 |
| **EV-16** | Pre-image digest re-measured at B's issuance instant | V-4 | either | **[MEASURED]** `PHASE4` P4-7 — `preimage_digest` moved `3a2a2532…` → `0b7a886d…` while `manifest_digest` did **not**. `:743-749` refuses on pre-image mismatch |
| **EV-17** | First-run terminal transcript (`TRANSACTION COMPLETE`/`INCOMPLETE`, exit status) | V-7 | **[POS-2]** | **[MEASURED]** `PHASE4:§I.1` items 2–3 |
| **EV-18** | First-run `git status --porcelain` + full diff over the four guard paths | V-8 | **[POS-2]** | **[MEASURED]** `PHASE4:§E.3` — *"`git checkout` overwrites; the changed-path set is unrecoverable afterwards"* |
| **EV-19** | Ledger `sha256` after the first run | — | **[POS-2]** | **[INFERRED]** the arithmetic that makes EV-16's movement attributable to the first run rather than to anything else |
| **EV-20** | Regenerated registers staged or committed, **plus the permit's own register write staged** | IA-C1 + **P5-2** | **[POS-2]** | **[MEASURED]** **P5-2** — the used permit leaves the register ` M`/`AM`, which is DRIFT. Without staging it, EV-21 cannot return `RC=0` |
| **EV-21** | `register.sh --observe` → `RC=0` after the first run | V-9 | **[POS-2]** | **[MEASURED]** `PHASE4:§I.1` item 4 — UK-1's fourth closure item |

```
EVIDENCE ITEMS REQUIRED BEFORE uga_engine VALIDATION ...... 16
    shared with register.sh ............................... 7   EV-1, EV-4, EV-6, EV-7, EV-8, EV-9, EV-10
    specific to uga_engine ................................ 5   EV-12 … EV-16
    position-conditional [POS-2] .......................... 5   EV-17 … EV-21   (required only if
                                                                uga_engine runs SECOND; if it runs
                                                                first, the same 5 attach to register.sh)

DISTINCT PRE-RUN EVIDENCE ITEMS ........................... 21   EV-1 … EV-21
```

### D.3 Evidence produced after the runs

Not prerequisites; enumerated because §J's counts require the total and because two of the six are UK-1/UK-2 closure items.

| ID | Evidence | Produced by | Closes |
|---|---|---|---|
| **EV-22** | `uga_engine gate` at the model's target surface — `UGA-INV-01 violations=0`; `UGA-INV-10` per `Aud`; no V-5-passing invariant regressed | V-11 | **UK-2** items 2, 3, 4 |
| **EV-23** | A second `register.sh` produces **zero** byte changes across the four guard directories | V-12 | **UK-1** item 5 |
| **EV-24** | Authority-suite re-run, unchanged from EV-1 | V-13 | regression under real post-mint state |
| **EV-25** | Residual-control activation evidence: `_ledger_lock` taken, R-2's pre-write re-check ran, R-7's document comparison ran (`:920`) without a spurious refusal | V-14 | reduces RES-3, RES-4 |
| **EV-26** | `.runtime` sequence triple after | — | the irreversible-advance record |
| **EV-27** | Final ledger `sha256` | — | the mutation record |

### D.4 What no evidence can establish before the runs

**[UNKNOWN]** carried forward unchanged, and stated so the evidence inventory is not read as exhaustive.

| Item | Why no pre-run evidence exists |
|---|---|
| `register.sh` phases 2, 3, 4, 8 behaviour | **[MEASURED]** `PHASE4` P4-6 — `--plan` appears at `ukb.py:2501` and `uga_engine.py:2181` and **nowhere in `ukbx.py`**. Four of ten phases have **no dry-run mode at all**. This is the concrete content of UK-1 |
| Whether the `by_object` population clears in one mint | **[MEASURED]** `PHASE4:§B.2` — the population is **not stable**; it grows as a consequence of the program's own steps (27 → 28 at EV-9) |
| R-7w's window | **[MEASURED]** `PHASE4:§G.3` — it is a property of the **failure** path (`:893` → `:921`). A successful run never enters it, so **no successful run produces evidence about it** |

---


## E. Execution sequence

### E.1 The ten stages

Every stage is tagged with its class. `S-0` … `S-3` reach **occupancy** of READY-FOR-EXECUTION; `S-4` is the transition proper; `S-5` … `S-9` execute from it.

```
 ┌────────────────────────────────────────────────────────────────────────────────┐
 │ S-0   GOVERNANCE                                          [GOV-REQ]            │
 │       GA-1 … GA-9.  Repository mutations: 0.  Ledger writes: 0.                │
 └───────────────────────────────┬────────────────────────────────────────────────┘
                                 │ E-1  HARD — task content undefined without GA-1
                                 ▼
 ┌────────────────────────────────────────────────────────────────────────────────┐
 │ S-1   IMPLEMENTATION                                      [EXEC-REQ]           │
 │       IA-1 … IA-11, in E-2 / E-3 / E-7 order.                                  │
 │       Source mutations: yes.  Ledger writes: 0.  Identities allocated: 0.       │
 └───────────────────────────────┬────────────────────────────────────────────────┘
                                 │ E-4′ derived P5-1: the register must reach the INDEX
                                 ▼
 ┌────────────────────────────────────────────────────────────────────────────────┐
 │ S-2   PRE-GATE VERSIONING                                 [EXEC-REQ]           │
 │       IA-C1  stage the register        (minimum: `A `, worktree clean)          │
 │       IA-C2  COMMIT ledger_authority.py (staging insufficient — P5-3)          │
 │       Consequence, not a choice: by_object population 27 -> 28  (E-5, P4-10)    │
 └───────────────────────────────┬────────────────────────────────────────────────┘
                                 │
                                 ▼
 ┌────────────────────────────────────────────────────────────────────────────────┐
 │ S-3   STAGE 0 — PRE-MUTATION VERIFICATION                 [EXEC-REQ]           │
 │       V-1 … V-6  ->  EV-1 … EV-10, EV-12, EV-13, EV-14, EV-16                        │
 │       ENTIRELY READ-ONLY OF TRACKED STATE.  Mutating runs: 0.                   │
 │       ══════ READY-FOR-EXECUTION OCCUPIED HERE ══════                          │
 └───────────────────────────────┬────────────────────────────────────────────────┘
                                 │
                                 ▼
 ┌════════════════════════════════════════════════════════════════════════════════┐
 ║ S-4   AUTHORIZATION GATE                          [GOV-REQ] + [EXEC-REQ]       ║
 ║       §G's 14 conditions evaluated.  GA-7 and GA-8 must be IN HAND.            ║
 ║       Outcome: EXECUTION-AUTHORIZED  |  AUTHORIZATION-WITHHELD                 ║
 ║       Repository mutations: 0.                                                  ║
 └════════════════════════════════┬═══════════════════════════════════════════════┘
                                 │
                                 ▼
 ┌────────────────────────────────────────────────────────────────────────────────┐
 │ S-5   PERMIT ISSUANCE #1  at the CURRENT pre-image        [EXEC-REQ]           │
 │       -> EV-11 or EV-15.  Writes the register only; NOT the ledger.               │
 │       THEN STAGE THE REGISTER  ◄── derived this phase (P5-2)                    │
 │       AUTHORIZATION STATE: EXECUTION-AUTHORIZED (run in position 1)             │
 └───────────────────────────────┬────────────────────────────────────────────────┘
                                 │
                                 ▼
 ┌────────────────────────────────────────────────────────────────────────────────┐
 │ S-6   VALIDATION RUN, POSITION 1        ── MUTATING RUN 1 ──                    │
 │       register.sh (V-7, 9 by_path mints)  OR  uga_engine run --mint (V-10)      │
 │       order between them is FREE (P4-1, P4-5)                                   │
 │       -> EV-17, EV-18, EV-19;  then EV-20 stage;  then EV-21                         │
 │       AUTHORIZATION STATE: AUTHORIZATION-CONSUMED                               │
 └───────────────────────────────┬────────────────────────────────────────────────┘
                                 │ E-6  HARD SERIALIZATION (P4-7)
                                 │ preimage_digest MOVED -> permit #2 must be re-bound
                                 ▼
 ┌────────────────────────────────────────────────────────────────────────────────┐
 │ S-7   RE-MEASURE + PERMIT ISSUANCE #2  at the NEW pre-image  [EXEC-REQ]         │
 │       -> EV-16 re-measured, EV-14 re-measured, EV-15 or EV-11                       │
 │       THEN STAGE THE REGISTER  (P5-2, second occurrence)                        │
 │       AUTHORIZATION STATE: EXECUTION-AUTHORIZED (run in position 2)             │
 └───────────────────────────────┬────────────────────────────────────────────────┘
                                 │
                                 ▼
 ┌────────────────────────────────────────────────────────────────────────────────┐
 │ S-8   VALIDATION RUN, POSITION 2        ── MUTATING RUN 2 ──                    │
 │       whichever of the two did not run at S-6                                   │
 └───────────────────────────────┬────────────────────────────────────────────────┘
                                 │
                                 ▼
 ┌────────────────────────────────────────────────────────────────────────────────┐
 │ S-9   POST-MUTATION CONFIRMATION                          [EXEC-REQ]           │
 │       V-11 -> EV-22 · V-12 -> EV-23 · V-13 -> EV-24 · V-14 -> EV-25 · EV-26 · EV-27   │
 │       V-12 re-runs register.sh: MUTATING but BYTE-NEUTRAL by construction        │
 │       AUTHORIZATION STATE: EXECUTION-COMPLETE  (only if both runs succeeded)     │
 └────────────────────────────────────────────────────────────────────────────────┘
```

### E.2 Mapping to Phase 4's 20 steps

**[INFERRED]** Phase 5's 10 stages are a re-partition of Phase 4's 20 steps with an authorization stage inserted and two staging acts added, not a different program.

| Phase-5 stage | Phase-4 steps | Delta introduced by Phase 5 |
|---|---|---|
| S-0 | 0 | GA-1…GA-9 enumerated as 9 artifacts; 7 are new |
| S-1 | 1 | unchanged |
| S-2 | 2 | **split into IA-C1 (staging suffices — P5-1) and IA-C2 (commit required — P5-3)** |
| S-3 | 3–8 | unchanged; V-1…V-6 |
| **S-4** | **—** | **new: the authorization gate. Phase 4 has no step here.** |
| S-5 | 9 | **+ stage the register (P5-2)** |
| S-6 | 10–13 | **step 12 refined: staging the permit's own write is required, not only the regenerated registers** |
| S-7 | 14 | **+ stage the register (P5-2, second occurrence)** |
| S-8 | 15 | unchanged |
| S-9 | 16–19 | unchanged; V-11…V-14 |

### E.3 Minimality of the sequence

**Claim: 10 stages, and no stage is removable.** Each removal argument is stated with its class; six of the ten rest on a measurement.

| Stage | If removed | Class |
|---|---|---|
| **S-0** | Task content is undefined. **[MEASURED]** `PHASE3:§C.4` — 4–7 of 17–20 tasks are axis-conditional; `PHASE4:§E.4` — V-11 has no success condition and R-B no scope without GA-9 | **[MEASURED]** |
| **S-1** | **[MEASURED]** `PHASE3` P3-1 — all three admissible `permit` values are refused today on a real allocating manifest. E-4A is a total block on every identity-ledger write. No run can start | **[MEASURED]** |
| **S-2** | **[MEASURED]** **P5-1** — an untracked register is `??` → `RC=3` at V-2. **[MEASURED]** **P5-3** — an uncommitted `ledger_authority.py` is deleted by a `reset`-class rollback | **[MEASURED]** |
| **S-3** | Authorization would be granted over an act whose outcome is **indeterminate**. **[INFERRED]** That is the precise thing a gate exists to prevent, and it inverts Phase 4's definition of the state being authorized (`PHASE4:§0.2`) | **[INFERRED]** |
| **S-4** | **[MEASURED]** `commit :841` — `permit` is mandatory with no default, so the machine-authorization half cannot be skipped at all. **[MEASURED]** `register.sh:150-153` — the human half is demanded by the artifact itself: *"obtain REG-AUTO-001 authorization … allocation is irreversible and is not a remediation this read-only report may authorize"* | **[MEASURED]** |
| **S-5** | No permit exists; `permit=None` is refused at the type check (`PHASE3` P3-1) | **[MEASURED]** |
| **S-6** | UK-1 or UK-2 stays open. **[MEASURED]** `PHASE4:§E.1` — the populations are disjoint, overlap 0 | **[MEASURED]** |
| **S-7** | **[MEASURED]** `PHASE4` P4-7 — permit #2 issued before S-6 is refused on the pre-image binding after S-6 lands. Removing S-7 makes run 2 unauthorizable | **[MEASURED]** |
| **S-8** | The other unknown stays open | **[MEASURED]** |
| **S-9** | **[MEASURED]** `PHASE4:§I.1` item 5 and `§I.2` items 2–4 are closure conditions for UK-1 and UK-2. Removing S-9 retires both unknowns on a one-shot success | **[MEASURED]** |

### E.4 Two lower bounds, proved

**Bound 1 — minimum mutating runs = 2.** Carried from `PHASE4:§E.1`, unchanged, and re-checked against the source read this phase.

- **[MEASURED]** `register.sh` never invokes `uga_engine` — confirmed independently this phase by full read of the 282-line script: the only occurrence of the string is the prose note at `:157`; the ten phases at `:206-259` invoke `ukb.py` and `ukbx.py` only.
- **[MEASURED]** `PHASE4` P4-5 — the two allocation populations are disjoint, `|gap_by_path ∩ anonymous_by_object| = 0`.
- **[MEASURED]** `PHASE4` P4-10 — `ukb._iter_files` excludes `DATA/` from `by_path` eligibility (`ukb.py:828-833`, *"the registry must not list itself"*), while UGA discovery does not exclude it: **0 of 17** DATA files are `by_path`-eligible and all **17** are in `by_object`.

**[INFERRED]** No single command allocates into both maps and neither population is a subset of the other, so one run cannot close both unknowns. `≥ 2`. Each command discharges its unknown in one invocation, so `≤ 2`.

**Bound 2 — minimum authorization events = 2, and this is new.**

- **[MEASURED]** `commit :841` — `permit` is mandatory with no default. Every mutating run requires a permit.
- **[MEASURED]** `_verify_permit :743-749` refuses on `preimage_digest` mismatch. **[MEASURED]** `PHASE4` P4-7 — the pre-image **moves** when a run lands (`3a2a2532…` → `0b7a886d…`) while `manifest_digest` does not.
- **[INFERRED]** A permit is therefore an authorization for **exactly one** ledger state. Two runs occupy two distinct ledger states. So two permits are required, and the second **cannot exist** — not "should not be issued", cannot verify — before the first run lands.

```
MINIMUM MUTATING RUNS ................................. 2
MINIMUM MACHINE-CHECKABLE AUTHORIZATION EVENTS ........ 2   (one permit per run, serialized)
MINIMUM SEQUENCED STAGES .............................. 10
STAGES REMOVABLE ...................................... 0
```

**[INFERRED]** Bound 2 is what makes EXECUTION-AUTHORIZED a **per-run** state rather than a global one. It is not a policy choice about granularity; it is forced by a digest binding measured at `:743-749`.

### E.5 What is free

**[MEASURED]** Exactly one ordering is unconstrained: **which of the two commands occupies position 1**. Basis: P4-1 (neither invokes the other) and P4-5 (disjoint populations). **[INFERRED]** E-6's *measure → issue → run* serialization applies to whichever runs second, symmetrically, so the choice changes no count in §J — only which five **[POS-2]** evidence items attach to which command.

**[INFERRED]** Everything else is constrained. Seven ordering edges from `PHASE4:§C.2` (E-1 … E-7) plus one refinement (**E-4′**, §C.3) and one insertion (**P5-2**'s two staging acts) govern the rest. No cycle exists: E-1…E-5 form a chain, E-6 orders the two runs pairwise, E-7 attaches to one branch, and CY-1 is terminated at one file by construction (`:499-506`).

### E.6 Which stages are new determinations and which are carried

Stated because the task asks for the transition package, and honesty about provenance is part of the answer.

| Stage | Determined by |
|---|---|
| S-0 | `PHASE2` (the 5+8 decisions) — **but 7 of its 9 artifacts are determined here** |
| S-1 | `PHASE3:§C`, `§D` — carried unchanged |
| S-2 | `PHASE4` step 2 — **refined here**, split by minimum-state asymmetry (P5-1, P5-3) |
| S-3 | `PHASE4:§D.1` — carried unchanged |
| **S-4** | **this phase, entirely** |
| S-5, S-7 | `PHASE4` steps 9, 14 — **each extended by one staging act** (P5-2) |
| S-6, S-8 | `PHASE4` steps 10, 15 — carried unchanged |
| S-9 | `PHASE4` steps 16–19 — carried unchanged |

---

## F. Rollback boundaries

For every stage: reversible, irreversible, evidence retained, rollback scope. **[MEASURED]** facts about the mutation surface come from `PHASE4` P4-9, re-verified this phase (**P5-5**): 1639 tracked files across four directories, tracked = on-disk in all four, **0 dirty at HEAD**.

### F.1 Per-stage boundary table

| Stage | Reversible? | Irreversible component | Evidence retained after rollback? | Rollback scope | Procedure |
|---|---|---|---|---|---|
| **S-0** Governance | **fully** — a decision can be re-taken | none | yes — the record persists | the selection record | none needed |
| **S-1** Implementation | **fully** — source is under version control or newly added and removable | none | yes | source files, tests, spec artifact | ordinary VCS |
| **S-2** Pre-gate versioning | **mostly** — see below | **`by_object` population 27 → 28** persists while the register is under version control | yes | the index entry / the commit | **R-D** |
| **S-3** Stage 0 | **fully** of tracked state | **`.runtime` `enforcement-audit.json` `seq` advance** (V-2 appends `mode=pre`) | yes — and the advance **is** the evidence | none tracked | none for tracked; `.runtime` **not restored** |
| **S-4** Authorization gate | **fully** — a withheld or granted authorization is a record | none | yes | the instrument | none needed |
| **S-5 / S-7** Permit issuance | **reversible until used** — the permit is a register entry | **once used**: under `B2` the permit is marked spent and **[MEASURED]** `PHASE4:§F.5` the mark is **not** reverted by R-A | yes | the register entry | **R-B** or **R-D** |
| **S-6 / S-8** Mutating runs | **byte-reversible; semantically irreversible** — see F.4 | **permanent identity allocation**; **[MEASURED]** `assert_append_only` refuses removal (`:290-296`) · **`.runtime` seq advance** ×3 | **only if V-8 ran first** — R-A overwrites | 1639 tracked files in 4 dirs + untracked new artifacts + the lock | **R-A + R-B + R-C** |
| **S-9** Confirmation | **fully** — V-12 is **byte-neutral by construction** | `.runtime` seq advance | yes | none | none |

### F.2 The three mutation classes, and which rollback reaches each

**[MEASURED]** `PHASE4:§F.1`–`§F.3`, each re-grounded on this phase's reads.

| Class | Members | Reached by |
|---|---|---|
| **Tracked, at HEAD, clean** | 1639 files: `DATA` 17 · `REGISTRIES` 6 · `CONTROL-TOWER` 12 · `PORTAL` 1604 | **R-A** — complete and non-destructive, because tracked = on-disk and 0 dirty in all four (**P5-5**) |
| **New artifacts** | the register; a `B2b` use record; an `Aud1` audit log; `.register.lock` | **R-B** (removal) / **R-C** (lock) / **R-D** (index or commit) |
| **Gitignored, non-history** | `.runtime/governance/{enforcement,sync,certification}-audit.json` at **612 / 19 / 1** | **NOT RESTORED.** **[MEASURED]** `.gitignore:12`; `governance_telemetry.py:30-40` declares it *"per-clone operational state … NEVER a repository artifact"* and a fresh runtime at `seq = 1` *"CORRECT and EXPECTED — not a regression"* |

### F.3 P5-3 — the rollback hazard, corrected

`PHASE4:§F.2` states the hazard as a **path-scope** problem: *"`git checkout HEAD -- 00-BOOK/tools/` — or any broader restore that includes `00-BOOK/tools/` — would delete the entire Phase-1 implementation."*

**[MEASURED]** **P5-3**, executed this phase in an isolated `/tmp` scratch repository reproducing the exact `AM` status, since removed:

| Operation | Effect on the `AM` file | Effect on the scoped restore target |
|---|---|---|
| `git checkout HEAD -- tools/` | **survives** — still `AM` | n/a |
| `git checkout HEAD -- guard/` | **survives** | guard directory restored, 0 dirty |
| `git reset --hard HEAD` | **DELETED** | whole tree reset |

**[INFERRED]** The hazard is real and the consequence is exactly as Phase 4 described — the loss of all twelve Phase-1 closures, which exist in no commit. **But it does not attach to the command Phase 4 names.** `git checkout <tree-ish> -- <pathspec>` writes only paths present in the tree-ish; a path absent from HEAD is not touched, so widening R-A's scope to `00-BOOK/tools/` is **safe**. What realizes the hazard is a **`reset`-class** primitive, which takes no pathspec at all and therefore cannot be bounded by scope.

**Three consequences, each stronger than the original statement.**

1. **[EXEC-REQ]** **R-A must be a `checkout`-class restore. `git reset --hard` is categorically prohibited as a rollback primitive for the whole transition window**, and prohibiting it is not a matter of scope discipline — the primitive is unscopable.
2. **[INFERRED]** Phase 4's mitigation is nonetheless exactly right and becomes more important: **[EXEC-REQ]** committing `ledger_authority.py` (IA-C2) removes the hazard entirely, because a committed file survives `reset --hard`. Staging does **not** remove it — measured: the probe's file *was* staged and was deleted anyway.
3. **[EXEC-REQ]** `git clean -f`/`-fd` acquires the same status once IA-C2 is performed for the register: **[MEASURED]** an untracked register is `??`, and `clean` removes untracked files. Before IA-C1 the register is `??`; `clean` would remove it. That is R-B's *intended* behaviour, so the prohibition is on **unscoped** `clean`, not on `clean` as such.

### F.4 Byte-reversible versus semantically irreversible

**[INFERRED]** and this is the distinction the rollback analysis turns on, because the two answers to "is the mutating run reversible?" are both correct at different levels.

| Level | Reversible? | Basis |
|---|---|---|
| **Bytes on disk** | **YES** | **[MEASURED]** R-A is complete over the tracked surface: tracked = on-disk and 0 dirty at HEAD in all four directories (**P5-5**) |
| **Allocation semantics** | **NO** | **[MEASURED]** `assert_append_only` refuses removal (`:290-296`). An allocated identifier cannot be withdrawn *through the authority*; R-A restores the file **out-of-band**, which the authority never sanctions |

**[INFERRED]** So R-A does not "undo" an allocation; it **overwrites the record of one**. `PHASE4:§F.5` Interaction 1 measured the consequence precisely — the out-of-band restore returns the pre-image to its pre-run value, which **re-validates the permit that was just used**, and `PHASE2` probe P2-1 measured replay ACCEPTED after exactly such a restore. **The rollback procedure is the E1-F3 replay vector.**

**[EXEC-REQ]** GA-9 must therefore record the axis-`B` consequence before any rollback is performed:

| Axis `B` | After R-A |
|---|---|
| **`B1`** reusable | The restored permit verifies again. A retry needs no new permit. Consistent with the model's own ratified semantics. |
| **`B2`** consumed, durable | **[INFERRED]** the use record is a separate artifact and R-A restores only the four guard paths, so the permit stays **spent** while the allocation is **undone**. A retry requires a **fresh** permit. |

### F.5 The four rollback procedures

| ID | Scope | Procedure | Completeness | New this phase? |
|---|---|---|---|---|
| **R-A** | tracked mutation surface — 1639 files, 4 directories | **`checkout`-class** restore of the four guard paths to HEAD, by name. **Never a `reset`-class primitive** (§F.3) | **complete** — **[MEASURED]** P4-9 / P5-5 | scope-bound **corrected** |
| **R-B** | untracked new artifacts — the register, plus a `B2b` record or an `Aud1` log if the model takes them | **explicit removal.** **[INFERRED]** a checkout restores tracked paths and does not remove untracked files, so R-A alone leaves the register on disk as `??` DRIFT | complete **only if** §F.2's created-artifact set is enumerated first; size is axis-`B`/`Aud`-dependent | no |
| **R-C** | the re-entrancy lock `00-BOOK/tools/.register.lock` | **[MEASURED]** the script's own `EXIT` trap removes it (`register.sh:189`, read this phase); after an uncatchable kill it persists and is reclaimed at 3600 s (`:181-187`). Gitignored (`.gitignore:3`), and **[MEASURED]** the script's own comment states it lives under `tools/` *"outside the scan and the guard set"* so it never appears as drift | complete, 1-hour worst case | no |
| **R-D** | **pre-gate versioning of the register (S-2)** | **[MEASURED]** if IA-C1 was satisfied by **staging**: `git restore --staged` on the register — the index entry is discarded and the file returns to `??`, then R-B removes it. If satisfied by **committing**: the commit must be reverted. **[EXEC-REQ] R-D must never include IA-C2's commit of `ledger_authority.py`** — reverting that commit deletes the Phase-1 implementation by exactly the mechanism §F.3 measures | complete | **YES** |

**Why R-D is required and why Phase 4 does not have it.** **[MEASURED]** `PHASE4:§E.2` tags step 2 as mutating (`yes*`) but `PHASE4:§H.2` row `T-0` records *"no — no mutation occurred"* for a Stage-0 failure. **[INFERRED]** Those are inconsistent, and the inconsistency has a real consequence: Phase 4's rollback analysis is scoped to the two mutating **runs**, so the repository mutation at step 2 — which precedes the authorization gate — has no procedure attached to it.

**[INFERRED]** The consequence is measurable and it is the sharpest rollback finding of this phase. An abandoned transition that has passed S-2 but not S-8 leaves the register under version control with no `by_object` mint ever performed. **[MEASURED]** P4-10: all 17 `00-BOOK/DATA/*.json` are in `by_object` and **0** are `by_path`-eligible; **[MEASURED]** P4-4: `UGA-INV-01` is at **27** violations today. **[INFERRED]** The register becomes the 18th such file and the 28th anonymous object, and `register.sh`'s mint cannot clear it because `DATA/` is excluded from `by_path` eligibility (`ukb.py:828-833`).

```
ABANDONING THE TRANSITION AFTER S-2 WITHOUT R-D:
    UGA-INV-01 violations ....... 27  ->  28
    gate distance ............... FURTHER from green than before the program started
    cleared by register.sh? ..... NO  — DATA/ excluded from by_path (ukb.py:828-833)
    cleared by uga_engine only .. YES — which is the run that was abandoned
```

**[EXEC-REQ]** R-D is therefore required for **abandonment**, not for **deferral**. If the transition is paused with the intent to resume, the 28th violation is expected and correct. If it is abandoned, R-D must run or the invariant surface is left permanently worse. **[INFERRED]** Satisfying IA-C1 by staging rather than committing makes R-D a one-command index operation instead of a commit revert, which is why §C.3's correction has a rollback consequence and not merely a bookkeeping one.

### F.6 Evidence preservation

**[MEASURED]** `PHASE4:§F.6` — R-A overwrites, so evidence must be captured **before** restoration or it is lost. Four items, each with its destination constraint.

| Evidence | Destination constraint |
|---|---|
| stdout/stderr of all 10 phases + both runs | **[MEASURED]** outside the four guard directories — anything inside reads as drift (`register.sh:265-267`, read this phase) |
| `git status --porcelain` + full diff over the four guard paths (EV-18) | as above; **[MEASURED]** unrecoverable after R-A |
| the three `.runtime` `seq` values before and after (EV-7, EV-26) | already outside version control; **[INFERRED]** the only evidence that survives R-A intact |
| the ledger `sha256` before, after each run, and after restore (EV-6, EV-19, EV-27) | as above |

**[EXEC-REQ]** EV-8 must designate the destination **before** S-4, not at failure time. **[MEASURED]** the repository already declares suitable classes: `determinism-evidence/`, `*.bundle` and `.runtime/` are gitignored, and `.gitignore`'s bundle note states bundles *"belong in durable storage OUTSIDE the repository, never inside the tree they back up."*

### F.7 P5-4 — one prohibition for the transition window

**[MEASURED]** this phase, by reading `register.sh:69-96` and `.git/hooks/pre-commit`:

- `register.sh --install-hooks` writes a git pre-commit hook whose body is `exec … register.sh --guard`.
- **[MEASURED]** `--guard` is **not** a verification plane. It runs the **full ten-phase mutating transaction** first (`:206-259`), and only then checks drift (`:262-273`).
- **[MEASURED]** the drift check at `:265-267` is **bare** `git status --porcelain` over the four guard paths. Per **P5-1**, that flags `A ` and `M ` — i.e. **any staged change**.
- **[MEASURED]** the currently installed `.git/hooks/pre-commit` is **not** this hook. It is a ruff lint + format gate (`ucos_ruff_gate` in `scripts/ucos-env.sh:321`), scoped to **tracked Python files under `engine/` and `platform/`**. `core.hooksPath` is unset.

**[INFERRED]** Two consequences.

1. **The deadlock is not live, and must not be made live.** Were `--install-hooks` run, committing any change under the four guard directories would become impossible: staging the change makes `--guard`'s bare porcelain non-empty, so the hook exits 3 and blocks the commit that would have cleared it. **[EXEC-REQ]** `--install-hooks` is prohibited for the duration of the transition window.
2. **Worse than a deadlock: every commit would become a mutating run.** **[INFERRED]** With the hook installed, IA-C1 and EV-20 — both ordinary commits — would each trigger a full `ukb build --mint`. The minimum of **2** mutating runs proved in §E.4 would no longer hold, and the program's mutation count would become a function of how many times it commits.
3. **A live precondition that Phase 4 does not name.** **[MEASURED]** the ruff gate that *is* installed is scoped to `engine/` and `platform/`, and **[MEASURED]** IA-9 modifies `platform/tests/test_ledger_authority.py`. **[EXEC-REQ]** therefore the test-suite changes must be ruff lint- and format-clean before any commit in the sequence succeeds. `00-BOOK/tools/ledger_authority.py` is **out** of the gate's scope, so IA-C2 is unaffected.

```
ROLLBACK PROCEDURES REQUIRED ...................... 4   R-A, R-B, R-C, R-D
    new this phase ................................ 1   R-D
    scope-bound corrected this phase .............. 1   R-A  (primitive class, not path width)
NON-RESTORABLE CLASSES ............................ 1   .runtime/governance — by declaration
PROHIBITED PRIMITIVES FOR THE WINDOW .............. 2   reset-class restore; unscoped clean
PROHIBITED OPERATIONS FOR THE WINDOW .............. 1   register.sh --install-hooks
```

---


## G. Authorization gate

### G.1 The exact conditions

**EXECUTION-AUTHORIZED (run R)** may be declared if and only if all **14** conditions below hold. The conjunction is the gate. Conditions are grouped by what satisfies them, and each carries its class and its falsification test — a condition with no falsification test is not a gate condition but a wish, and none appears below.

#### Group I — Governance conditions (satisfied by a decision)

| # | Condition | Class | Falsified by |
|---|---|---|---|
| **G-1** | GA-1 exists and assigns all five closure axes to one of `Z-01 … Z-12` | [GOV-REQ] | any axis unassigned, or an assignment outside the admissible sets of `PHASE3:§A` |
| **G-2** | GA-2, GA-3, GA-4 exist: 8 redundant answers recorded; `R = R1` and NB-1…NB-6 all avoided; the 12-vs-24 reading declared | [GOV-REQ] | any of the three absent; `R2` taken; the CX-4 pairing taken |
| **G-3** | GA-5 exists: RES-3, RES-4 and R-7w explicitly accepted as bounds that execution activates and does not close | [GOV-REQ] | acceptance absent, or conditioned on execution closing any of them — **[MEASURED]** `PHASE4:§G.3` proves R-7w cannot even be reduced |
| **G-4** | GA-6 exists and adopts UK-1's 5 and UK-2's 4 closure-evidence items, with UK-2 item 3's target surface fixed at **30** (`Aud1`/`Aud2`) or **29** (`Aud3`) | [GOV-REQ] | evidence set undefined, or defined after the run |
| **G-5** | **GA-7 exists** — an irreversible-mutation authorization naming the two commands, both allocation populations, both irreversible side-effect classes, and the authorizing party | [GOV-REQ] | absent; or scoped beyond the two runs; or issued by a party that `register.sh:150-153` does not admit as authorizing |
| **G-6** | GA-8 and GA-9 exist: rollback pre-authorized with the `reset`-class prohibition attached; the three axis-parameterized conditions recorded | [GOV-REQ] | rollback unauthorized at gate time; `reset`-class not prohibited; V-11's target or R-B's scope unrecorded |

#### Group II — Implementation conditions (satisfied by an artifact)

| # | Condition | Class | Falsified by |
|---|---|---|---|
| **G-7** | IA-1 … IA-11 complete for the selected model — 17–20 tasks, in E-2 / E-3 / E-7 order | [EXEC-REQ] | any task incomplete; **[MEASURED]** `A3` landing **after** the first permit is issued invalidates it (`:548-568`, `PHASE1:§4.2`) |
| **G-8** | The register exists and is **at least staged with a clean worktree** | [EXEC-REQ] | **[MEASURED]** **P5-1** — `??` or `AM` or ` M` → `RC=3` at V-2 |
| **G-9** | `00-BOOK/tools/ledger_authority.py` is **committed** | [EXEC-REQ] | **[MEASURED]** **P5-3** — while `AM`, a `reset`-class rollback deletes all twelve Phase-1 closures |
| **G-10** | `register.sh --install-hooks` has not been run; `.git/hooks/pre-commit` is not `register.sh --guard` | [EXEC-REQ] | **[MEASURED]** **P5-4** — otherwise every commit becomes a mutating run and the 2-run minimum fails |

#### Group III — Evidence conditions (satisfied by a validation result)

| # | Condition | Class | Falsified by |
|---|---|---|---|
| **G-11** | Stage 0 green: **V-1 … V-6** all pass, producing EV-1 … EV-10 and EV-12 … EV-14, EV-16 | [EXEC-REQ] | any failure. `RC` 2/3/4/5 at V-2; a write during V-3 or V-4; a wrong-binding acceptance or correct-permit refusal at V-6 |
| **G-12** | The zero-dirty precondition holds **now** over all four guard directories | [EXEC-REQ] | **[MEASURED]** any dirty entry — `PHASE4:§F.2`: *"If any guard directory acquires uncommitted work before execution, `git checkout` becomes destructive over that work"* |
| **G-13** | EV-8's evidence destination is designated, and lies outside the four guard directories and outside version control | [EXEC-REQ] | destination inside a guard directory (reads as drift) or untracked-inside-the-tree |

#### Group IV — The per-run condition

| # | Condition | Class | Falsified by |
|---|---|---|---|
| **G-14** | A permit exists for run **R**, verifying against the manifest and pre-image measured **at this instant**, within `scope.maps` and `scope.max_allocations` | [EXEC-REQ] | **[MEASURED]** `_verify_permit` refuses on any of **9** bindings (`PHASE3` P3-7): `permit_id :715`, `actor :728`, `manifest_digest :735`, `preimage_digest :743`, `head :751`, `scope :767`, `scope.maps :769`, `scope.max_allocations :778`, `expires_at :785` |

### G.2 The declaration

```
EXECUTION-AUTHORIZED (run R)  ⇔  G-1 ∧ G-2 ∧ … ∧ G-13  ∧  G-14(R)

    G-1 … G-6    governance   — satisfied ONCE, hold for both runs
    G-7 … G-10   artifact     — satisfied ONCE, hold for both runs
    G-11 … G-13  evidence     — satisfied ONCE at Stage 0; G-12 re-verified before any restore
    G-14         per-run      — satisfied TWICE, and CANNOT be satisfied twice simultaneously
```

**[MEASURED]** The asymmetry in the last line is the gate's defining property, and it is measured at `:743-749` plus `PHASE4` P4-7, not chosen: `preimage_digest` moves when a run lands (`3a2a2532…` → `0b7a886d…`) while `manifest_digest` does not. **[INFERRED]** So G-14 is satisfiable for exactly one run at a time. There is no state in which both runs are simultaneously authorized.

### G.3 Three properties of the gate, each derived

**Property 1 — the gate is state-bound and lapses without being used.**

**[MEASURED]** `PHASE2:§C.1` merge M3 established that *"expiry is repository-state-bound"* ≡ *"a permit never expires"*, because **[MEASURED]** `:742-749` refuses on pre-image movement, so a permit is valid exactly while the pre-image is unchanged. **[INFERRED]** Applied to the gate: **EXECUTION-AUTHORIZED has measured expiry semantics.** It lapses the instant **any** write to the ledger lands — including a write nobody in the program performed. The state **AUTHORIZATION-LAPSED** (§0.4) is reachable without any act by the authorized party.

**[EXEC-REQ]** Consequently the interval between S-5 and S-6, and between S-7 and S-8, must be minimized and must exclude any other ledger writer. **[MEASURED]** the repository already provides partial protection: `register.sh`'s re-entrancy lock (`:178-190`) makes a concurrent or nested invocation an immediate no-op, and `_ledger_lock :216-268` takes an exclusive `flock` on the ledger's directory. **[MEASURED]** neither covers the gap: `PHASE3:§E.1` — the caller's read at `uga_engine.py:2097` precedes `commit`'s lock at `:870`, which **is** RES-3.

**Property 2 — the gate cannot be reached without repository mutation, but can be reached without any ledger write.**

**[INFERRED]** Phase 4 measured **0 mutating runs** to reach READY-FOR-EXECUTION, where "mutating run" means a run that allocates identity. The further step to EXECUTION-AUTHORIZED costs:

```
IDENTITY ALLOCATIONS to reach EXECUTION-AUTHORIZED .......... 0
LEDGER WRITES ............................................... 0
REGISTER WRITES ............................................. 1   (permit issuance, S-5)
INDEX / COMMIT OPERATIONS ................................... 3   IA-C1, IA-C2, + 1 staging (P5-2)
SOURCE FILE MUTATIONS ................................... 17-20 tasks' worth
```

**[MEASURED]** the permit register is not the identity ledger: `commit()` guards `00-BOOK/DATA/id-ledger.json`, and **[MEASURED]** `load_permit_register :608-631` is the **only** register access inside the authority and it is **read-only**. **[INFERRED]** So issuing a permit is not an allocating act, and reaching EXECUTION-AUTHORIZED allocates nothing. That is why the gate is a real gate: everything before it is undoable at the level that matters.

**Property 3 — the gate is model-invariant in structure.**

**[INFERRED]** All 14 conditions apply under all 12 models. **[MEASURED]** three have axis-parameterized *content*: G-4 (UK-2's target surface, axis `Aud`), G-6 (R-B's scope, axis `B`; and GA-9's replay consequence, axis `B`), and G-7's task set (17–20, all axes). **[INFERRED]** No axis value adds, removes or weakens a condition. This is `PHASE3:§C.3`'s structural result — nothing stranded on a single governance outcome — appearing a third time, now at the authorization layer.

### G.4 What the gate does not require

Stated because omissions are load-bearing, and each is a positive measured finding.

| Not required | Why |
|---|---|
| **UK-1 or UK-2 closed** | **[MEASURED]** `PHASE4:§0.2` — they are closed **by** execution, not before it. Requiring them would make the gate self-defeating |
| **Any residual closed** | **[MEASURED]** `PHASE3:§E.7` — none of the three is closable by any of the 12 models. **[MEASURED]** `PHASE4:§G.3` — R-7w is not even reducible by execution |
| **`register.sh --guard` green** | **[MEASURED]** **P5-1** — `--guard` flags any staged change, so it cannot be green while the register is staged-not-committed. It is an **end-of-program** requirement (`PHASE4:§I.1` item 5's context), not a gate condition |
| **A new authority, actor or allow-list** | **[MEASURED]** `PHASE3:§D.1` — FD-1 and FD-4 are provably vacuous; `:728-732` is unconstrained string equality with no allow-list |
| **Any data migration** | **[MEASURED]** `PHASE3:§F.3` — 0 migration tasks under all 12 models |
| **A clock authority** | **[MEASURED]** `PHASE2:§C.3` — `expires_at` is read at `:785-797` and has **no producer anywhere in the repository**. G-14 lists it among the 9 bindings because `_verify_permit` reads it, not because a value must be supplied |

### G.5 AUTHORIZATION-WITHHELD is a legitimate terminal state

**[INFERRED]** and it is the state Phase 4 could not express. If G-1 … G-13 all hold and G-5's authorization is not granted, the repository sits at:

```
POSITION ................ READY-FOR-EXECUTION  (occupied, verified)
AUTHORIZATION STATE ..... AUTHORIZATION-WITHHELD
BLOCKERS ................ 0
RESIDUALS ............... 3   all still LATENT — no write path was ever opened
UNKNOWNS ................ 2   UK-1, UK-2
ROLLBACK OBLIGATION ..... none of R-A / R-B / R-C;  R-D iff the transition is ABANDONED
IRREVERSIBLE EFFECTS .... 1 class only — .runtime seq advance from V-2's `mode=pre` append
                              by_object population sits at 28 (E-5), cleared by no run
```

**[INFERRED]** This is a strictly better state than today's on every axis except one: blockers 5 → 0, implementation 0 → complete, unknowns unchanged at 2, residuals unchanged at 3 **and still latent**. The one regression is the 28th anonymous object, and it is exactly what R-D exists to reverse (§F.5).

---

## H. Failure matrix

For each stage: failure condition, recovery path, whether a blocker is created, whether rollback is required.

### H.0 The classification, stated once

**[INFERRED]** `PHASE4:§H.4` established that a validation failure means the implementation is wrong — a **revealed defect**, a pre-existing error surfaced by validation, not a new blocker introduced by the program. Phase 5 adopts this and extends it: **[INFERRED]** a *governance* failure at S-0 is likewise not a new blocker — it is the **existing** decision-level blocker count of 5, unchanged, because `PHASE3:§G.2` measured that governance closure moves the decision count to 0 and leaves the artifact count at 5.

**[INFERRED]** Therefore: **no stage in this program creates a blocker.** Two stages can leave the repository *worse* than it started without creating a blocker, and both are identified below (S-2 and S-6/S-8).

### H.1 The matrix

| Stage | Failure condition | Recovery path | Blocker created? | Rollback required? |
|---|---|---|---|---|
| **S-0** Governance | No selection made; a non-admissible axis value; `R2` taken; the CX-4 pairing taken; GA-4 deferred a fourth time | Re-decide. **[MEASURED]** all 12 admissible values enumerated in `PHASE3:§A`, so the satisfying set is known and finite | **no** — the 5 artifact-level blockers are unchanged, not increased | **no** — 0 repository mutations |
| **S-1** Implementation | Any of 17–20 tasks incomplete or wrong. **Worst case measured:** `A3` (F-2/F-3) lands **after** F-1 issues a permit | **[MEASURED]** ordering violation is **free to avoid today and only today** — zero permits exist (`PHASE3` P3-1). If violated after issuance, every issued permit is invalidated by the digest change at `:548-568` and must be re-issued | **no** — revealed defect | **no** ledger rollback; ordinary VCS revert of source |
| **S-2** Versioning | Register left `??` (V-2 → `RC=3`); or `ledger_authority.py` left uncommitted (G-9 fails) | Stage the register; commit `ledger_authority.py`. Both are single operations | **no** | **R-D iff abandoned.** **[INFERRED]** the 28th anonymous object persists otherwise (§F.5) |
| **S-3** Stage 0 | **V-1**: any test fails, or count < 77 · **V-2**: `RC` 2/3/4/5 · **V-3/V-4**: a write occurs, or no digest is emitted · **V-5**: the gate cannot run, or the surface is not 30 · **V-6**: a wrong binding accepted, or a correct permit refused | Fix the revealed defect; re-run Stage 0. **[MEASURED]** every one of V-1…V-6 is read-only of tracked state (`PHASE4:§I.3`), so the loop is free | **no** — revealed defect | **no** — **[MEASURED]** 0 tracked mutation. `.runtime` `seq` advances and is not restored |
| **S-4** Gate | Any of G-1 … G-13 unsatisfied → **NOT-AUTHORIZABLE**. All satisfied and authorization not granted → **AUTHORIZATION-WITHHELD** | Satisfy the condition, or accept the terminal state of §G.5 | **no** | **no**; R-D iff abandoned |
| **S-5 / S-7** Issuance | The issued permit does not verify at V-6 / at the run — any of the 9 bindings mismatches. **Most likely measured cause:** the pre-image moved between measurement and issuance | Re-measure, re-issue. **[MEASURED]** `PHASE4` P4-7 — this is E-6 operating as designed, not a defect | **no** | **no** — **[MEASURED]** `_verify_permit` writes nothing (`PHASE0` EV-13, `PHASE3` P3-1) |
| **S-6 / S-8** `register.sh` | **A⊘** Phase 0 fails, or Phase 1 refused by the authority → tracked state **untouched**. **A✗** a phase in 2…9 fails → tracked state **mutated and unsealed** | **A⊘**: fix and retry; **[MEASURED]** every `commit()` refusal path restores the pre-image byte-for-byte (`_restore :807-822`; `PHASE1:§R-7` verified `read_bytes() == original` on all five divergence tests). **A✗**: capture EV-18 **first**, then R-A + R-B + R-C, then diagnose | **no** — revealed defect | **A⊘ no** · **A✗ YES** — R-A + R-B + R-C |
| **S-6 / S-8** `uga_engine` | **B⊘** `PermitRefused` or `LedgerWriteRefused` (R-2 / R-7 fired) → untouched. **B✗** `commit` succeeds but a downstream surface emission or the gate fails → **mutated, inconsistent** | as above | **no** — revealed defect | **B⊘ no** · **B✗ YES** |
| **S-9** Confirmation | **V-11**: `UGA-INV-01 > 0`, or a V-5-passing invariant regressed · **V-12**: any byte change with no content change · **V-13**: a V-1-passing test now fails · **V-14**: a residual control did not execute, or fired spuriously | Diagnose. **[MEASURED]** V-11's failure mode *"the population did not clear in one mint"* is UK-2 answering **negatively** — a measurement, not a defect, and `PHASE4:§B.2` predicted the mechanism (the population is not stable) | **no** — a negative answer to an unknown is an answer | **no** for V-11/V-13/V-14 (all read-only). **V-12 is byte-neutral by construction**, so a V-12 failure is itself the finding |

### H.2 Two failure modes that are not defects

**[INFERRED]** Stated separately because treating either as a defect would misdirect the recovery.

| Mode | Why it is not a defect |
|---|---|
| **A permit refused because the pre-image moved** | **[MEASURED]** this is edge E-6 working. `PHASE4` P4-7 measured the movement; `:743-749` measured the refusal. The recovery is re-measurement, which §E.2's step 14 already mandates |
| **V-11 reporting that the population did not clear in one mint** | **[MEASURED]** `PHASE4:§B.2` — the population **grows as a consequence of the program's own steps** (27 → 28 at EV-9), and `B2b`/`Aud1` may add more. A second mint is a further authorization event, not a repair |

### H.3 The one failure mode that destroys evidence

**[MEASURED]** `PHASE4:§F.6` and `§E.3` — R-A overwrites, and the changed-path set is unrecoverable afterwards.

**[EXEC-REQ]** In every rollback-requiring state (`A✗`, `B✗`), §F.6's four evidence items must be captured **before** R-A runs. **[INFERRED]** GA-8's pre-authorization exists precisely to remove the approval latency from this path, because the pressure to restore is maximal at the moment capture matters most.

---

## I. Terminal-state matrix

### I.1 Reachable terminal states

Rows are success/failure combinations across the gate chain. `T-0 … T-9` are `PHASE4:§H.2`'s ten rows, carried with their triples unchanged and annotated with authorization state. `X-1 … X-4` are new to Phase 5, because Phase 4 treated governance, implementation, versioning and authorization as **preconditions** rather than as stages that can terminate.

Residuals are **3** in every row: **[MEASURED]** `PHASE3:§E.7` and `PHASE4:§G` — no failure creates or closes one, and no model closes one. "+d" denotes revealed defects, which **[INFERRED]** §H.0 establishes are not blockers.

| # | Terminated at | Blockers | Unknowns | Residuals | Authorization state | Rollback |
|---|---|---|---|---|---|---|
| **X-1** | S-0 governance incomplete | **5** artifact-level | 2 | 3 · latent | **NOT-AUTHORIZABLE** | no |
| **X-2** | S-1 implementation incomplete | **5** artifact-level | 2 | 3 · latent | **NOT-AUTHORIZABLE** | no |
| **X-3** | S-2 versioning not performed | 0 + d | 2 | 3 · latent | **NOT-AUTHORIZABLE** | no |
| **T-0** | S-3 Stage 0 fails | 0 + d | 2 | 3 · latent | **NOT-AUTHORIZABLE** | no; R-D iff abandoned |
| **X-4** | S-4 authorization withheld | **0** | 2 | 3 · **latent** | **AUTHORIZATION-WITHHELD** | no; R-D iff abandoned |
| **T-6** | both runs refused cleanly (A⊘ B⊘) | 0 + d | 2 | 3 · latent | AUTHORIZATION-CONSUMED ×0 | no |
| **T-7** | A✗ B⊘ | 0 + d | 2 | 3 · **active** | consumed ×1 | **YES** |
| **T-8** | A⊘ B✗ | 0 + d | 2 | 3 · **active** | consumed ×1 | **YES** |
| **T-9** | A✗ B✗ | 0 + d | 2 | 3 · **active** | consumed ×2 | **YES** — both scopes |
| **T-2** | A✓ B⊘ | 0 + d | **1** — UK-2 | 3 · active | consumed ×1 | no |
| **T-3** | A✓ B✗ | 0 + d | **1** — UK-2 | 3 · active | consumed ×2 | **YES** — run B's scope |
| **T-4** | A⊘ B✓ | 0 + d | **1** — UK-1 | 3 · active | consumed ×1 | no |
| **T-5** | A✗ B✓ | 0 + d | **1** — UK-1 | 3 · active | consumed ×2 | **YES** — run A's scope |
| **T-1** | A✓ B✓ | **0** | **0** | 3 · active | **EXECUTION-COMPLETE** | **no** |

```
REACHABLE TERMINAL STATES ...................................... 14
    carried unchanged from PHASE4 §H.2 .......................... 10   T-0 … T-9
    new in this phase .......................................... 4    X-1 … X-4
    requiring rollback ......................................... 5    T-3, T-5, T-7, T-8, T-9
    requiring R-D iff abandoned ................................ 3    X-3, T-0, X-4
    with residuals still LATENT ................................ 5    X-1, X-2, X-3, T-0, X-4
    with 0 blockers AND 0 unknowns ............................. 1    T-1
    with 0 blockers ............................................ 2    X-4, T-1
    reachable WITHOUT any identity allocation .................. 5    X-1 … X-4, T-0
```

### I.2 Collapse to distinct signatures

**[INFERRED]** On `(blockers, unknowns, residuals)` alone the 14 rows collapse to **4** signatures: `(5,2,3)`, `(0+d,2,3)`, `(0+d,1,3)`, `(0,0,3)` — with `(0,2,3)` at X-4 distinguishing itself from `(0+d,2,3)` only because no defect was revealed. Adding the **authorization state** column separates them into **6** classes, and adding **rollback obligation** recovers all 14 as individually reachable.

**[INFERRED]** This is why the authorization column is not decoration. Phase 4's 3 distinct triples over 10 states understated the state space by exactly the amount the authorization layer contributes: 4 new states and 3 new distinguishing classes.

### I.3 Three invariants across every terminal state

**[INFERRED]** each, from the measurements cited.

1. **Blockers never exceed 5 and never increase.** **[MEASURED]** `PHASE3:§G.2` — 5 artifact-level today; 0 after implementation. **[MEASURED]** `PHASE4:§I.6` — a validation failure *"reveals a defect in how a task was implemented; it does not reopen E-4A, E1-F3, E-3, RES-1 or RES-2."*
2. **Residuals are 3 in every row.** What varies is **latent versus active**, and the transition happens at the **first** mutating run. **[MEASURED]** `PHASE3:§E.7` — all three go LATENT → ACTIVE under all 12 models, because `I-R` opens a write path that has never been open. **[INFERRED]** So the five states reachable without any allocation (X-1…X-4, T-0) are the only ones in which the residuals remain unexercised.
3. **No terminal state is unrecoverable.** **[MEASURED]** R-A is complete over the tracked surface — tracked = on-disk and 0 dirty at HEAD in all four directories (**P5-5**) — **provided** the `reset`-class prohibition of §F.3 holds. **[INFERRED]** That proviso is the single point at which a recoverable state becomes unrecoverable, and it is why G-9 is a gate condition rather than a recommendation.

### I.4 One state that is worse than the start

**[INFERRED]** Stated because "no new blockers" is true and is not the whole picture.

X-3, T-0 and X-4 leave the `by_object` anonymous population at **28** rather than **27**, with no mint performed. **[MEASURED]** `PHASE4` P4-4 — today's count is 27 and `UGA-INV-01` FAILs on it; `PHASE4` P4-10 — the register becomes the 18th `00-BOOK/DATA/*.json`, all of which are in `by_object`, and **0** of which are `by_path`-eligible.

**[INFERRED]** So the gate can be reached, authorization withheld, and the repository left one violation **further** from a green gate than before the program began — with no blocker created and no residual activated. That is not a contradiction of §H.0; it is the precise reason **R-D** exists (§F.5) and the reason §C.3's staging refinement matters operationally.

---


## J. Exact counts

### J.1 Governance artifacts

```
GOVERNANCE ARTIFACTS REQUIRED BEFORE EXECUTION AUTHORIZATION ........  9
    GA-1  closure-model selection record (5 axes -> one Z-nn)
    GA-2  redundant-decision completion record (8 answers)
    GA-3  zero-new-blocker attestation (R1; NB-1…NB-6 avoided; CX-4 avoided)
    GA-4  model-space reading declaration (12 vs 24)
    GA-5  residual acceptance (RES-3, RES-4, R-7w)
    GA-6  unknown acknowledgment + UK-1/UK-2 closure-evidence adoption
    GA-7  irreversible-mutation authorization              <- named in source at
                                                              register.sh:150-153
    GA-8  rollback authorization + reset-class prohibition
    GA-9  axis-parameterized condition record

    corresponding to a PHASE2 decision .............................  2   GA-1, GA-2
    identified for the first time in this phase .....................  7   GA-3 … GA-9
    with axis-parameterized content .................................  3   GA-6, GA-8, GA-9
    model-invariant in requirement .............................. 9 of 9
    satisfiable by code, evidence or further determination ..........  0

UNDERLYING GOVERNANCE DECISIONS (PHASE2 §E.1) ....................... 13
    determining a closure value ....................................  5   axes I, A, B, D, Aud
    closure-redundant ..............................................  8
        of which redundant for the IMPLEMENTATION entirely .........  2   FD-1, FD-4
        of which CHANGE THE TRANSITION PACKAGE anyway ..............  2   B2a/B2b -> R-B scope
                                                                          R modifier -> GA-3
```

### J.2 Implementation artifacts

```
IMPLEMENTATION ARTIFACTS REQUIRED BEFORE EXECUTION AUTHORIZATION .... 11
    IA-1   specification artifact (PHASE05-grade, 17-20 tasks)     NEW FILE
    IA-2   ledger_authority.py            F-2, F-3 (+O-3/O-7/O-11)
    IA-3   allocation-permits.json        F-1                       NEW FILE
    IA-4   register.sh:216 -> ukb.py:1299 F-4
    IA-5   uga_engine.py:1331-1335        F-5
    IA-6   uga-declaration.json           F-6
    IA-7   source-claim amendments        F-7 (+O-1/O-5)
    IA-8   UGA-INV-10 citations, 58 files F-8
    IA-9   test_ledger_authority.py       F-9, F-10, F-11 (+O-2/4/6/8/10)
    IA-10  UGA invariant disposal test    F-12
    IA-11  conditional tracked artifact   O-9 (Aud1) / B2b use record   NEW FILE, <=10 models

    new files ......................................................  3
    existing files modified ........................................  8
    required under all 12 models ................................... 10
    MIGRATION ARTIFACTS ............................................  0

PRE-GATE VERSIONING ACTS ............................................  2
    IA-C1  register        -> minimum STAGED, worktree clean       [P5-1]
    IA-C2  ledger_authority.py -> minimum COMMITTED                [P5-3]
    additional staging acts derived this phase ......................  2   after each issuance [P5-2]

TASKS CARRIED .................................................. 17 - 20
    forced (all 12) ................................................ 13
    conditional .................................................. 4 - 7
    required by exactly one model ..................................  0
    minimum task multiplicity ......................................  3   O-11 (B2 & D2)
```

### J.3 Validation artifacts

```
DISTINCT VALIDATION ARTIFACTS ....................................... 27
    required BEFORE the runs ......................................... 21   EV-1 … EV-21
        before register.sh validation ................................ 11   EV-1 … EV-11
            shared with uga_engine ...................................  7   EV-1, EV-4, EV-6, EV-7,
                                                                            EV-8, EV-9, EV-10
            specific to register.sh ..................................  4   EV-2, EV-3, EV-5, EV-11
        before uga_engine validation ................................. 16
            shared ...................................................  7   as above
            specific to uga_engine ...................................  5   EV-12 … EV-16
            position-conditional [POS-2] .............................  5   EV-17 … EV-21
    produced AFTER the runs ..........................................  6   EV-22 … EV-27

RUNTIME VALIDATIONS (carried from PHASE4 §D.1, unchanged) ............ 14
    Stage 0  pre-mutation, read-only .................................  6   V-1 … V-6
    Stage 1  run A ...................................................  3   V-7, V-8, V-9
    Stage 2  run B ...................................................  2   V-10, V-11
    Stage 3  confirmation ............................................  3   V-12, V-13, V-14
    read-only of tracked state ....................................... 11
    mutating .........................................................  3   V-7, V-10, V-12
                                                                            (V-12 byte-neutral)

EVIDENCE THAT SURVIVES A FULL TRACKED ROLLBACK ......................  1   the .runtime seq triple
                                                                            612 / 19 / 1 today
EVIDENCE DESTROYED BY R-A IF NOT CAPTURED FIRST .....................  4   §F.6
```

### J.4 Required approvals

```
DISTINCT APPROVAL SUBJECTS ..........................................  6
    human-level ......................................................  4
        1. closure-model ratification            GA-1 + GA-2 + GA-3 + GA-4
        2. residual and unknown acceptance       GA-5 + GA-6
        3. irreversible-mutation authorization   GA-7
        4. rollback authorization                GA-8 (+ GA-9's record)
    machine-checkable ................................................  2
        5. permit for the run in position 1      verified on 9 bindings
        6. permit for the run in position 2      verified on 9 bindings, at a MOVED pre-image

MINIMUM NUMBER OF INSTRUMENTS ........................................  3
    1 bundled governance instrument carrying subjects 1-4
    2 permits — CANNOT be bundled.  [MEASURED] PHASE4 P4-7: the pre-image moves
      (3a2a2532… -> 0b7a886d…) and :743-749 refuses on the mismatch, so the second
      permit cannot exist while the first run is unlanded.

APPROVALS THAT CAN BE GRANTED SIMULTANEOUSLY .........................  4   the human-level ones
APPROVALS THAT CANNOT ................................................  2   the two permits
```

### J.5 Required execution runs

```
MUTATING RUNS REQUIRED ...............................................  2
    position 1 and position 2, order FREE between them
        register.sh                 -> closes UK-1   ->  9 by_path mints
        uga_engine.py run --mint    -> closes UK-2   -> by_object mints, population
                                                        28 AT ISSUANCE (re-measure: EV-14)
    proved minimal from three measured facts (§E.4):
        register.sh never invokes uga_engine                (P4-1; re-read this phase)
        allocation populations disjoint, overlap = 0         (P4-5)
        00-BOOK/DATA excluded from by_path eligibility       (P4-10; ukb.py:828-833)

TOTAL COMMAND INVOCATIONS THAT MUTATE ................................  3
    the 2 allocating runs + V-12's byte-neutral re-run of register.sh
    V-12 adds no allocation and no rollback surface — [MEASURED] all four writers are
    stamp-neutralized and skip no-op rewrites (ukb._dump_json :135-146, ukb._write
    :1658-1664, ukbx._dump :66-76, ukbx._dump_text :692-698)

RUNS REQUIRED TO REACH EXECUTION-AUTHORIZED ..........................  0
IDENTITY ALLOCATIONS REQUIRED TO REACH EXECUTION-AUTHORIZED ..........  0
LEDGER WRITES REQUIRED TO REACH EXECUTION-AUTHORIZED .................  0
REGISTER WRITES REQUIRED TO REACH EXECUTION-AUTHORIZED ...............  1
```

### J.6 Rollback procedures and terminal states

```
ROLLBACK PROCEDURES REQUIRED .........................................  4
    R-A  tracked mutation surface — 1639 files, 4 directories, CHECKOUT-class only
    R-B  untracked new artifacts — the register (+ B2b / Aud1 artifacts if taken)
    R-C  the re-entrancy lock — EXIT trap; 3600 s stale reclamation
    R-D  pre-gate versioning of the register                          <- NEW THIS PHASE

    new this phase ...................................................  1   R-D
    scope-bound CORRECTED this phase .................................  1   R-A
    non-restorable classes ...........................................  1   .runtime/governance
    prohibited primitives for the window .............................  2   reset-class; unscoped clean
    prohibited operations for the window .............................  1   register.sh --install-hooks

REACHABLE TERMINAL STATES ............................................ 14
    carried from PHASE4 §H.2 ......................................... 10
    new this phase ...................................................  4   X-1 … X-4
    distinct (blockers, unknowns, residuals) signatures ..............  4
    distinct with the authorization column ...........................  6
    requiring rollback ...............................................  5
    requiring R-D iff abandoned ......................................  3
    with residuals still LATENT ......................................  5
    reaching 0 blockers AND 0 unknowns ...............................  1   T-1
```

### J.7 The aggregate, and model-invariance

```
TOTAL ARTIFACTS REQUIRED BEFORE EXECUTION ............................ 41
     9  governance      GA-1 … GA-9
    11  implementation  IA-1 … IA-11
    21  validation      EV-1 … EV-21
TOTAL ACROSS THE WHOLE PROGRAM ....................................... 47
    +6  post-run validation evidence  EV-22 … EV-27

SEQUENCED STAGES ..................................................... 10   S-0 … S-9
    removable ..........................................................  0
    reaching occupancy of READY-FOR-EXECUTION ..........................  4   S-0 … S-3
    the transition proper ..............................................  1   S-4
    executing from it ..................................................  5   S-5 … S-9

ORDERING CONSTRAINTS .................................................  9
    carried from PHASE4 §C.2 ..........................................  7   E-1 … E-7
    refined this phase ................................................  1   E-4' — INDEX, not
                                                                              commit, for V-2
    derived this phase ................................................  1   P5-2 — stage after
                                                                              each issuance
    free ....................................................... which command occupies position 1

BLOCKERS
    at EXECUTION-AUTHORIZED ...........................................  0
    NEW blockers introduced by this transition package ................  0
    NEW blockers introduced by this determination .....................  0

MODEL-INVARIANCE
    governance artifacts required ..................... 9 under all 12
    implementation artifacts required ............. 10-11 under all 12
    validation artifacts required ..................... 21 under all 12
    approvals required ................................  6 under all 12
    mutating runs required ............................  2 under all 12
    rollback procedures required ......................  4 under all 12
    sequenced stages .................................. 10 under all 12
    reachable terminal states ......................... 14 under all 12

    axis-parameterized CONTENT (not counts) ...........  5 items
        V-11 target surface .................... 30 (Aud1/Aud2) | 29 (Aud3)
        R-B scope .............................. +1 artifact (B2b) | +1 (Aud1) | +0
        replay-after-rollback consequence ...... permit reusable (B1) | spent (B2)
        task set ............................... 17-20
        UK-2 closure item 3 .................... follows V-11's target
```

**[INFERRED]** **No count above varies with the governance model.** That is the third appearance of the same structural result — `PHASE3:§C.3` at the task layer, `PHASE4:§I.4` at the validation layer, and here at the authorization layer. **[INFERRED]** It is also exactly why Rule 5's prohibition on recommending a model costs nothing: no model is better or worse positioned to reach EXECUTION-AUTHORIZED, so no analysis in this document could support a preference even if one were permitted.

---

## K. Final determination

### K.1 What is the minimum artifact set required before execution?

**41 artifacts**, in three packages, none removable.

```
  9  GOVERNANCE      GA-1 … GA-9     — 2 correspond to a PHASE2 decision; 7 are new
                                        GA-7 is the one whose absence stopped 6 phases
 11  IMPLEMENTATION  IA-1 … IA-11    — 3 new files, 8 modifications, 0 migration
                                        + 2 pre-gate versioning acts, + 2 staging acts
 21  VALIDATION      EV-1 … EV-21      — 11 before register.sh, 16 before uga_engine,
                                        7 shared, 5 position-conditional
────
 41
```

**[INFERRED]** Minimality: every governance artifact is unsatisfiable by code, evidence or further determination (§B); every implementation artifact carries at least one of the 13 forced tasks or a task the selected model forces (§C); every evidence item has a named validation that produces it and a named condition that fails without it (§D).

### K.2 What is the minimum evidence set required before execution?

**21 items.** Split by gate, as the task asks:

```
BEFORE register.sh VALIDATION ....... 11    EV-1 … EV-11
    authority suite >=77 · observe RC=0 · run-A plan manifest · post-plan zero-dirty ·
    permit round trip (1 acceptance + 9 refusals) · ledger sha256 · .runtime seq triple ·
    evidence destination · register STAGED · ledger_authority.py COMMITTED · permit A

BEFORE uga_engine VALIDATION ........ 16    7 shared + 5 specific + 5 position-conditional
    + run-B plan manifest · 30-invariant BASELINE · RE-MEASURED by_object population ·
      permit B · pre-image RE-MEASURED at B's issuance instant
    + [POS-2] first-run transcript · first-run diff · post-run sha256 ·
      registers AND the permit's own write staged · post-run observe RC=0
```

**[MEASURED]** Two items cannot be carried from any prior document and must be measured in the moment: **EV-14** the `by_object` population (`PHASE4:§I.2` — *"the number cannot be fixed in advance"*) and **EV-16** the pre-image digest (`PHASE4` P4-7 — it moves).

### K.3 What is the minimum sequence required before execution?

**10 stages, 0 removable.**

```
S-0 GOVERNANCE ──► S-1 IMPLEMENTATION ──► S-2 VERSIONING ──► S-3 STAGE 0
                                                                   │
                          ══════ READY-FOR-EXECUTION OCCUPIED ═════╪══════
                                                                   ▼
                                                    S-4 AUTHORIZATION GATE
                                                                   │
                       ┌───────────────────────────────────────────┘
                       ▼
S-5 PERMIT #1 ──► S-6 RUN, POSITION 1 ──► S-7 RE-MEASURE + PERMIT #2 ──►
S-8 RUN, POSITION 2 ──► S-9 CONFIRMATION

  order between the two runs: FREE          (P4-1, P4-5)
  order everything else:      FORCED        9 ordering constraints
  permits: CANNOT be issued together        (P4-7 — the pre-image moves)
```

**[MEASURED]** Four of the ten stages precede the gate and mutate no ledger. **[MEASURED]** two are the mutating runs. **[MEASURED]** the two permit-issuance stages must be separated by a landed run — this is the hard serialization, not a precaution.

### K.4 Can EXECUTION-AUTHORIZED be reached?

# **YES.**

**[INFERRED]** from the measured facts of §G.3, with the qualification that changes how the answer must be used:

```
  EXECUTION-AUTHORIZED is reachable, and it is:

    PER-RUN        — not a global state.  [MEASURED] :743-749 + P4-7: a permit
                     authorizes exactly one ledger state, and two runs occupy two.
                     It must be entered TWICE and can never hold for both at once.

    STATE-BOUND    — it LAPSES the instant any ledger write lands, including one
                     the program did not perform.  [MEASURED] PHASE2 §C.1 M3:
                     state-bound expiry is already implemented and is what
                     "no expiry" means operationally.

    ALLOCATION-FREE TO REACH — 0 identity allocations, 0 ledger writes, 1 register
                     write.  [MEASURED] load_permit_register :608-631 is the only
                     register access inside the authority and it is READ-ONLY, so
                     issuing a permit is not an allocating act.

    NOT SATISFIABLE BY ANALYSIS — G-5 (GA-7) is a decision by a party outside the
                     determination chain.  [MEASURED] the artifact says so in its
                     own voice at register.sh:150-153, and 6 phases have declined
                     on exactly this ground.
```

### K.5 Under how many admissible models?

```
ADMISSIBLE MODELS ................................................. 12
REACHING EXECUTION-AUTHORIZED ..................................... 12   (all)
REACHING TERMINAL STATE T-1 (0 blockers, 0 unknowns) .............. 12   (all, conditional
                                                                         on both runs succeeding)
BETTER OR WORSE POSITIONED ........................................  0
```

**[INFERRED]** All 12, because every count in §J.7 is model-invariant. Five items have axis-parameterized *content*; none changes reachability, and none changes a count.

### K.6 What remains after authorization?

At the moment EXECUTION-AUTHORIZED is declared for the first run:

```
REMAINING TO EXECUTE
    mutating runs .....................................  2
    runtime validations ............................... 14   (6 already discharged at Stage 0;
                                                              8 remain: V-7 … V-14)
    permit issuances ..................................  1   the second, at a pre-image that
                                                              does not yet exist
    staging acts ......................................  2
    reachable terminal states from here ...............  9   T-1 … T-9

REMAINING REGARDLESS OF OUTCOME
    blockers ..........................................  0
    residuals .........................................  3
        RES-3  MW-3 read-to-lock window       -> REDUCED by execution, never closed
        RES-4  advisory, fs-dependent flock    -> REDUCED by execution, never closed
        R-7w   post-hoc detection window       -> UNCHANGED — [MEASURED] a property of
                                                  the FAILURE path (:893 -> :921); a
                                                  successful run never enters it
        all three transition LATENT -> ACTIVE at the FIRST mutating run
    unknowns ..........................................  2   until the runs land; then 0, 1 or 2
    irreversible side-effect classes ..................  2
        permanent identity allocation — append-only; :290-296 refuses removal
        .runtime seq advance — gitignored, declared non-history, 612 / 19 / 1 today
    rollback procedures on standby ....................  4   R-A, R-B, R-C, R-D
    non-restorable classes ............................  1

REMAINING BEYOND THIS PROGRAM ENTIRELY
    closing RES-3   requires uga_engine.build's discovery pass under exclusion
    closing R-7w    requires serialization inside the authority
    closing RES-4   requires a guarantee no filesystem provides
        [MEASURED] all three were bounded by AUTHORIZATION SCOPE, not by uncertainty
        (PHASE05 §F.4; PHASE1 §R-3 / §R-6 / §R-7), and PHASE3 §E.7 established all
        three are invariant across all 12 models.
```

### K.7 The answer

```
================================================================================
  EXECUTION-AUTHORIZED REACHABLE?                                     Y E S
================================================================================

  Reachable under ....... 12 of 12 admissible closure models
  Identity allocations to REACH it ............................... 0
  Ledger writes to REACH it ...................................... 0

  TRANSITION PACKAGE ............................................ 41 artifacts
        9  governance      GA-1 … GA-9      7 identified for the first time here
       11  implementation  IA-1 … IA-11     0 migration
       21  validation      EV-1 … EV-21       2 unmeasurable in advance (EV-14, EV-16)

  AUTHORIZATION GATE ........................................... 14 conditions
        6  governance   G-1 … G-6      satisfied once, hold for both runs
        4  artifact     G-7 … G-10     satisfied once, hold for both runs
        3  evidence     G-11 … G-13    Stage 0; G-12 re-verified before any restore
        1  per-run      G-14           satisfied TWICE, never simultaneously

  APPROVALS ...................................................... 6 subjects
        4  human-level        can be carried by 1 instrument
        2  machine-checkable  CANNOT be bundled — the pre-image moves (P4-7)

  SEQUENCE ....................................................... 10 stages
        S-0 governance · S-1 implementation · S-2 versioning · S-3 Stage 0
        ══ READY-FOR-EXECUTION ══
        S-4 AUTHORIZATION GATE
        S-5 permit #1 · S-6 run 1 · S-7 re-measure + permit #2 · S-8 run 2
        S-9 confirmation
        removable: 0 · free: which command occupies position 1

  ROLLBACK ....................................................... 4 procedures
        R-A tracked (1639 files, CHECKOUT-class ONLY)
        R-B untracked-new · R-C lock · R-D pre-gate versioning  [NEW]
        + 1 non-restorable class · 2 prohibited primitives · 1 prohibited operation

  TERMINAL STATES ................................................ 14
        1 reaches 0 blockers AND 0 unknowns .................. T-1
        1 reaches 0 blockers with residuals still LATENT ..... X-4 (withheld)
        5 require rollback · 3 require R-D iff abandoned

  ── THE THREE STRUCTURAL RESULTS ───────────────────────────────────────────

  1. THE GATE IS DEONTIC, NOT EPISTEMIC.  Six phases declined execution and not
     one declined on capability grounds.  The artifact states the requirement in
     its own voice — register.sh:150-153: "obtain REG-AUTO-001 authorization …
     allocation is irreversible and is not a remediation this read-only report
     may authorize."  GA-7 is therefore not a document this chain can produce.

  2. EXECUTION-AUTHORIZED IS PER-RUN AND LAPSES.  Measured, not chosen:
     :743-749 refuses on preimage_digest mismatch, and P4-7 measured the pre-image
     moving 3a2a2532… -> 0b7a886d… when a run lands while manifest_digest does not.
     A permit authorizes ONE ledger state.  Two runs, two states, two permits,
     and the second cannot exist before the first run lands.

  3. THE GATE CAN BE REACHED AND THE REPOSITORY LEFT WORSE.  X-4 has 0 blockers
     and 3 still-latent residuals — better than today on every axis but one:
     the by_object anonymous population sits at 28 rather than 27, because the
     register is the 18th 00-BOOK/DATA/*.json and DATA/ is excluded from by_path
     eligibility (ukb.py:828-833), so register.sh's mint can never clear it.
     That is what R-D exists to reverse, and it is why staging the register
     rather than committing it (P5-1) is a rollback decision, not bookkeeping.
================================================================================
```

---

## L. Evidence

### L.1 Probes executed this phase

**None is a validation run.** No member of V-1 … V-14 was executed. `pytest` was not invoked. `register.sh` was not invoked in any mode. `uga_engine` was not invoked. P5-1 through P5-4 operate inside a temporary directory under `/tmp` that is **not this repository** and that was removed before this document was written; P5-5 is read-only against this repository.

| ID | Claim established | Method | Outcome | Touched this repository? |
|---|---|---|---|---|
| **P5-1** | `register.sh:125`'s `--observe` drift filter accepts **staged**; `:265-267`'s `--guard` does not | the exact awk expression and the bare porcelain, applied to all six register/permit states in a `/tmp` scratch repo | `??` DRIFT/DRIFT · `A ` **PASS**/DRIFT · `AM` DRIFT/DRIFT · committed-clean PASS/PASS · ` M` DRIFT/DRIFT · `M ` **PASS**/DRIFT | **no** — read-only |
| **P5-2** | Permit issuance itself reads as drift, so the register must be staged after each issuance | derived from **P5-1** rows `AM` and ` M`, applied to `PHASE4:§E.2`'s step order (V-2 at step 6, issuance at step 9, V-9 at step 13) | V-9 returns `RC=3` on the permit's own uncommitted write, independently of the regenerated registers. Two staging acts required | **no** — derivation |
| **P5-3** | `PHASE4:§F.2`'s rollback hazard attaches to **`reset`-class**, not `checkout`-class, restores | an `AM` file reproduced in a `/tmp` scratch repo, then `git checkout HEAD -- tools/`, a scoped restore, and `git reset --hard HEAD` | `checkout HEAD -- tools/` → **file survives, still `AM`** · scoped restore → target restored, file survives · `reset --hard` → **file DELETED** | **no** |
| **P5-4** | `--install-hooks` is a live deadlock and a mutation multiplier; the installed hook is something else | read `register.sh:69-96`, `:262-273`; read `.git/hooks/pre-commit`; read `scripts/ucos-env.sh:321-339`; `git config --get core.hooksPath` | `--guard` runs the **full mutating transaction** then a bare-porcelain drift check. Installed hook is **`ucos_ruff_gate`**, scoped to tracked `.py` under `engine/` and `platform/`. `core.hooksPath` unset | **read-only** |
| **P5-5** | The Phase-4 baseline is unmoved | `shasum`, `ls`, `git status --porcelain`, `git ls-files`, `git rev-parse`, `git cat-file -e`, read of `.runtime/governance/*.json` | ledger `sha256 8471e709…c20b` · register **absent** · four guard dirs **0 dirty** · HEAD `77798202` · `ledger_authority.py` `AM`, *"exists on disk, but not in HEAD"* · tracked 17/6/12/1604 = 1639 · `.runtime` 612/19/1 · LA 933 / uga 2191 / ukb 2579 / register.sh 282 lines | **read-only** |

**Non-mutation, verified before and after every probe:**

```
$ shasum -a 256 00-BOOK/DATA/id-ledger.json
8471e709b178a9a09909bca55f2e8eccb78161db8423026d1d26e4f35c41c20b
$ git status --porcelain -- 00-BOOK/DATA 00-BOOK/REGISTRIES 00-BOOK/CONTROL-TOWER 00-BOOK/PORTAL
(0 lines)
$ ls 00-BOOK/DATA/allocation-permits.json
ls: No such file or directory
$ .runtime/governance  enforcement 612 · sync 19 · certification 1   (unmoved)
```

### L.2 Source read this phase

| Reference | Content confirmed |
|---|---|
| `register.sh` — **full 282 lines** | `set -euo pipefail :48` · `--install-hooks` writer `:69-96` · the `--observe` plane `:99-176` and its header claim *"this command allocates no identity and writes nothing under version control"* `:101` · the drift filter `:125` · the identity-gap block `:143-167` · **`:150-153`** *"obtain REG-AUTO-001 authorization … allocation is irreversible and is not a remediation this read-only report may authorize"* — **the basis of GA-7** · the re-entrancy lock `:178-190` and its *"outside the scan and the guard set"* rationale · `fail()` `:201` · the ten phases `:206-259`, `:216` passing **no** `--permit`, nine `\|\| fail` gates · the `--guard` drift gate `:262-273` · **[MEASURED]** the string `uga_engine` occurs once, as prose at `:157` |
| `.git/hooks/pre-commit` | `UCOS-MANAGED-HOOK`, `ucos_ruff_gate` — **not** `register.sh --guard` |
| `scripts/ucos-env.sh:321-339` | `ucos_ruff_gate` scope: tracked `.py` under `engine/` and `platform/` |
| `.gitignore:3`, `:12` | `.register.lock`; `.runtime/` |
| `.runtime/governance/*.json` | enforcement 612 runs / last seq 612 · sync 19 / 19 · certification 1 / 1 |

### L.3 Prior-phase measurements relied on, each named

| Claim | Source |
|---|---|
| The 12 admissible models, forced `I-R` and `A3`, the excluded values and their new blockers | `PHASE2:§D.3`, `§C.9`; `PHASE3:§A` |
| 13 governance decisions · 5 closure-determining · 8 redundant · FD-1/FD-4 vacuous | `PHASE2:§E.1`, `§E.4`, M1/M2 |
| M3: state-bound expiry ≡ no expiry — **the basis of the gate's lapse semantics** | `PHASE2:§C.1` |
| 24 tasks · 13 forced · 0 single-model · 17–20 per model · 0 migration | `PHASE3:§C`, `§F.3`, `§G.1` |
| Delta governance-complete → implementation-ready = 1 specification artifact, 0 code | `PHASE3:§D.2` |
| Blockers 5 artifact-level / 0 decision-level after governance | `PHASE3:§G.2` |
| RES-3 / RES-4 / R-7w definitions, model-invariance, LATENT → ACTIVE under all 12 | `PHASE05:§F.4`; `PHASE1:§R-3`/`§R-6`/`§R-7`; `PHASE3:§E.1-E.3`, `§E.7` |
| Residuals bounded by **authorization scope**, not uncertainty — **the basis of GA-5** | `PHASE05:§F.3`, `§F.4`; `PHASE1:§R-7`'s *"a larger change than this phase covers"* |
| E-4A open: all three `permit` values refused on a real allocating manifest | `PHASE3` P3-1 |
| `_verify_permit`'s **9**-field binding surface | `PHASE3` P3-7 |
| 77-test authority baseline | `PHASE1:§4`; `PHASE3` P3-8 |
| Zero permits exist, so `A3`'s digest churn is free — today only | `PHASE2` P2-5; `PHASE3` P3-1 |
| `register.sh` never invokes `uga_engine`; populations disjoint; `DATA/` excluded from `by_path` | `PHASE4` P4-1, P4-5, P4-10 |
| **`preimage_digest` moves while `manifest_digest` does not** — the basis of per-run authorization | `PHASE4` **P4-7** |
| Mutation classification of all ten `register.sh` phases; four fully read-only | `PHASE4:§D.0` |
| The 14 runtime validations with their success and failure conditions | `PHASE4:§D.1` |
| `--plan` absent from `ukbx.py` — four phases with no dry-run | `PHASE4` P4-6 |
| Tracked = on-disk, 0 dirty, 1639 files in 4 directories | `PHASE4` P4-9; re-verified **P5-5** |
| `ledger_authority.py` absent from HEAD | `PHASE4` P4-11; re-verified **P5-5** |
| Rollback is the E1-F3 replay vector; replay ACCEPTED after a byte restore | `PHASE2` P2-1; `PHASE4:§F.5` |
| Every `commit()` refusal restores the pre-image byte-for-byte | `PHASE1:§R-7` — `read_bytes() == original` on all five tests |
| R-7w is a property of the failure path; a successful run never enters it | `PHASE4:§G.3` |
| UK-1's 5 and UK-2's 4 closure-evidence items | `PHASE4:§I.1`, `§I.2` |

**No claim in this document rests on unexecuted reasoning without being tagged [INFERRED], and no unresolved question is presented as anything but [UNKNOWN].**

### L.4 Corrections to the inputs, stated plainly

Four, each measured, each affecting what an implementer must do.

| # | Input claim | Correction | Consequence |
|---|---|---|---|
| **1** | `PHASE4:§E.2` step 2 / `§E.3`: *"COMMIT the register"*, because *"`register.sh:125` counts `??` as drift"* | **[MEASURED] P5-1** — the justification establishes only that untracked fails. **Staged with a clean worktree passes `--observe`.** Committing is sufficient, not necessary | Staging is materially more reversible. It makes **R-D** a one-command index operation instead of a commit revert (§F.5) |
| **2** | `PHASE4:§D.1` V-9: an `RC=3` is expected because *"the regenerated registers are uncommitted"* | **[MEASURED] P5-2** — correct but incomplete. **The used permit is a second, independent drift source** in the same directory, created deliberately two steps earlier | **Two staging acts** must be inserted after Phase 4's steps 9 and 14, or V-9 cannot return `RC=0` — which is UK-1's fourth closure item |
| **3** | `PHASE4:§F.2`: *"`git checkout HEAD -- 00-BOOK/tools/` … would delete the entire Phase-1 implementation"* | **[MEASURED] P5-3** — `checkout` does **not** delete an `AM` file; **`reset --hard` does**. The hazard is **primitive class**, not path width | R-A may safely be `checkout`-class at any scope; **`reset`-class is categorically prohibited** and cannot be bounded by scope, because it takes no pathspec |
| **4** | `PHASE4:§H.2` row T-0: *"no — no mutation occurred"* for a Stage-0 failure, while `§E.2` tags step 2 as mutating | **[INFERRED]** inconsistent. Step 2 is a repository mutation preceding the gate and has no rollback procedure in Phase 4 | **R-D** is required, and an abandoned transition past S-2 leaves `UGA-INV-01` at **28** violations rather than 27 — further from green than before the program began (§F.5, §I.4) |

**[INFERRED]** None of the four changes Phase 4's shape: the 2 mutating runs, the 14 validations, the minimality proof and the 10 carried terminal states all stand. Corrections 1–3 refine three specific acts; correction 4 adds one rollback procedure and four terminal states.

---

## M. Stop condition

Phase 5 ends here.

- **The target state was defined before it was answered** — §0.1. **EXECUTION-AUTHORIZED is deontic, not epistemic.** READY-FOR-EXECUTION says *the outcome is determinate*; EXECUTION-AUTHORIZED says *you may run*. Six phases possessed the first and declined on the second, none on capability grounds, and the artifact states the requirement in its own voice at `register.sh:150-153`.
- **EXECUTION-AUTHORIZED reachable: YES**, under **12 of 12** models, with **0 identity allocations** and **0 ledger writes** to reach it.
- **Transition package: 41 artifacts** — 9 governance (7 identified here for the first time), 11 implementation (0 migration), 21 pre-run validation (2 of which are unmeasurable in advance).
- **Authorization gate: 14 conditions**, each with a falsification test — 6 governance, 4 artifact, 3 evidence, 1 per-run.
- **The per-run finding, which is the sharpest of this phase and is measured:** G-14 is satisfiable for **exactly one run at a time**. `_verify_permit :743-749` refuses on `preimage_digest` mismatch and `PHASE4` P4-7 measured the pre-image moving `3a2a2532…` → `0b7a886d…` when a run lands while `manifest_digest` does not. **A permit authorizes one ledger state. There is no state in which both runs are authorized.**
- **The lapse finding:** authorization is **state-bound** and can expire without being used — `PHASE2:§C.1` M3 established that state-bound expiry is already implemented and is what "no expiry" means operationally. **AUTHORIZATION-LAPSED** is reachable with no act by the authorized party.
- **Sequence: 10 stages**, 0 removable, 9 ordering constraints, exactly one freedom — which command occupies position 1.
- **Approvals: 6 subjects** — 4 human-level (bundleable into 1 instrument), **2 machine-checkable permits that cannot be bundled**.
- **Rollback: 4 procedures + 1 non-restorable class.** **R-D is new.** R-A's bound is corrected from path width to **primitive class**: `checkout` is safe at any scope, `reset` is categorically prohibited until `ledger_authority.py` is committed.
- **Terminal states: 14** — 10 carried from Phase 4 with their triples intact, **4 new** because Phase 5 adds gates Phase 4 treated as preconditions. **1** reaches 0 blockers and 0 unknowns; **1** reaches 0 blockers with all three residuals still **latent**; **5** leave the residuals unexercised because no allocation occurred.
- **One state is worse than the start and creates no blocker:** X-3, T-0 and X-4 leave `UGA-INV-01` at **28** violations, because the register is the 18th `00-BOOK/DATA/*.json` and `DATA/` is excluded from `by_path` eligibility, so `register.sh`'s mint can never clear it. That is what **R-D** exists to reverse.
- **Residuals: 3 before, 3 after.** Two reducible in evidence class, one (**R-7w**) structurally unreachable by validation. All three transition **latent → active at the first mutating run**, and all three were bounded by **authorization scope** — which is why **GA-5** is required and why the party that authorizes execution is the party that accepts them.
- **New blockers introduced by this transition package: 0.** New blockers introduced by this determination: **0.**
- **Governance selected: none.** Decisions taken: **0.** Models or axis values recommended, ranked or preferred: **0.** Implementation content proposed: **0.** Validation runs executed: **0.**
- **Code changed: none. Repository files modified: none.** Ledger byte-identical, `sha256 8471e709…c20b`; four guard directories 0 dirty; register still absent; `.runtime` sequences unmoved at 612 / 19 / 1. The `/tmp` scratch repository used by P5-1, P5-3 and P5-4 was removed before this document was written.

**Every count in §J is model-invariant.** That result appears for the third time in this chain — at the task layer (`PHASE3:§C.3`), the validation layer (`PHASE4:§I.4`) and now the authorization layer. It is stated precisely so it cannot be read as an argument for any particular model: **nothing is stranded on a single governance outcome, and therefore nothing in this document could support a preference even if Rule 5 permitted one.**

The next act is not an analysis. It is **GA-1** — a governance decision on the five closure axes — followed by implementation, versioning, Stage 0, and then **GA-7**, the one artifact in the transition package that no phase of this chain can produce for itself.
