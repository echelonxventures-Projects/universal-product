# PHASE 7 — EXECUTION COMPLETION CLOSURE DETERMINATION

| Field | Value |
|---|---|
| Question | Can `EXECUTION-COMPLETED` be made reachable, unambiguous, falsifiable, fully evidenced and authorization-consistent under every admissible governance model, without introducing any new governance dependency? |
| Answer | **NO — on the package as it now stands, and the failure is decomposable.** Reachable: **YES**, after closure. Unambiguous: **NO** — the chain carries **two non-equivalent definitions** of the terminal state and they differ by **4 completion paths**. Falsifiable: **NO** — **4** reachable false-positive channels, only one of which Phase 6 found. Fully evidenced: **NO** — **3** unproducible evidence items (Phase 6 found 2). Authorization-consistent: **NO** — the re-run is not one manifest class but **three**, and Phase 6's closure `C-1` authorizes only one of them. No new governance dependency: **NO** — the re-run's authorization is axis-`D`-parameterized, so **6 of 12** models route it through `O-7`. |
| Hypothesis under test | *"Closing U-B and U-C leaves only execution-time unknowns (UK-1 and UK-2) between EXECUTION-AUTHORIZED and a terminal Phase-9 proof."* |
| Verdict on the hypothesis | **FALSIFIED — precisely, and by measurement.** Closing U-B and U-C leaves **7** items, not 2. Five are new here: `U-D` … `U-H`. All five are closable by determination, and §10.4 proves the set then reduces to exactly `{UK-1, UK-2}` over the enumerated surfaces. |
| Inputs | The eight named documents. All eight are `??` untracked and therefore `by_path`-ineligible (**P7-3**), so reading them perturbs no population. |
| Governance selected | **NONE.** No axis assigned. Every closure class in §4.5 and §5.5 is enumerated without preference, as the constraints require. |
| Permits issued · register created · mutating runs | **0 · 0 · 0.** `register.sh` was **not invoked in any mode**, including `--observe`. `ukb build --mint` was not invoked, in any mode, including `--plan`. `pytest` was not invoked. |
| Commands executed against this repository | **One**: `uga_engine.py gate` — declared *"Verify without mutating. Fails closed."* (`:2124`), measured read-only here (**P7-6**: ledger `sha256` and all three `.runtime` logs byte-identical before and after). |
| Repository files modified | **NONE.** This document is the only addition. Ledger `sha256 8471e709…c20b`; four guard directories **0** dirty; register absent; lock absent; `.runtime` **612 / 19 / 1**; `git ls-files --cached` **6804**; HEAD `77798202`. Re-verified at the close of every probe. |
| Probes | **13** — `P7-1 … P7-13`. One (`P7-5`) ran in a scratch directory outside this repository, created and destroyed within this phase. |

### Compliance with the stated constraints

| # | Constraint | Compliance |
|---|---|---|
| 1 | Determination only | The scope of §3–§11. No design, no task content, no code. |
| 2 | No governance selection | No axis assigned. Every result is quantified over the 12 admissible models, and where an axis value changes an answer both values are stated (§7.4, §4.5, §10.2). |
| 3 | No implementation | No source file modified, no source file proposed. |
| 4 | No permit issuance | No permit constructed, written, or verified against a live manifest. `00-BOOK/DATA/allocation-permits.json` re-verified **absent** (**P7-1**). |
| 5 | No register creation | As above. |
| 6 | No mutating run | `register.sh` **0** invocations in any mode. `ukb build --mint` **0** in any mode. `uga_engine run` **0** in any mode. The one command run (`uga_engine gate`) reaches no writer: `_dump` / `_write_text` are called only from `emit()` and `cmd_run` (**P7-6**), neither of which `cmd_gate` enters. |
| 7 | No repository modification | This document only. `pytest` deliberately not run — `addopts` carries `--cov-report=xml`, which writes `coverage.xml` (**P7-13**). Verified: no `__pycache__` entry appears in `git status` (`.gitignore`), tracked count unmoved at **6804**. |
| 8 | No recommendations | None. §4.5 enumerates **7** closure classes for U-B and §5.6b **6** for U-C; none is preferred, and each carries its cost rather than a verdict. |
| 9 | No model preference | None. §7 reports authorization accounting per model without ranking; the two axis-`D` halves are stated symmetrically. |
| 10 | No new governance assumptions | Every governance fact is cited to `PHASE2:§D.3` / `PHASE3:§A`. §10 identifies where the *package* introduces a governance dependency and does not resolve it. |

---

## 1. Executive determination

### 1.1 The headline

```
================================================================================
  CAN EXECUTION-COMPLETED BE MADE REACHABLE, UNAMBIGUOUS, FALSIFIABLE,
  FULLY EVIDENCED AND AUTHORIZATION-CONSISTENT UNDER ALL 12 MODELS,
  WITH NO NEW GOVERNANCE DEPENDENCY?                                     N O
================================================================================

  Clause by clause, because the conjunction hides which part fails.

  REACHABLE ................ YES, after closure.  0 paths reach it today.
  UNAMBIGUOUS .............. NO.  TWO non-equivalent definitions are live:
                             PHASE5 §0.4 "both runs landed AND both unknowns
                             retired" and PHASE6 §11.1 "A✓ ∧ B✓ ∧ EV-23 ∧ EV-24
                             ∧ EV-25".  The second omits EV-22, so PHASE6's own
                             T-1f is COMPLETED with UK-2 OPEN.  8 vs 12 paths.
  FALSIFIABLE .............. NO.  FOUR false-positive channels are reachable.
                             PHASE6 found one (the lock no-op).  Three are new.
  FULLY EVIDENCED .......... NO.  THREE evidence items are unproducible:
                             EV-1 by its named command, EV-23 in 2 of its 3
                             manifest classes, and EV-25 AT ALL — ledger_
                             authority.py contains ZERO print/logging
                             statements, so nothing can witness that a residual
                             control fired.  [MEASURED, P7-11]
  AUTHORIZATION-CONSISTENT . NO.  The re-run is THREE manifest classes, not one.
  NO NEW GOVERNANCE DEP .... NO.  The re-run's authorization is axis-D-bound.

  ── THE HYPOTHESIS ─────────────────────────────────────────────────────────

  "Closing U-B and U-C leaves only UK-1 and UK-2."          F A L S I F I E D

  Closing U-B and U-C leaves SEVEN items:

    U-D  [NEW] The by_object population is a function of the GIT INDEX, and
         today it is SET-IDENTICAL to the staged-new file set.  Measured:
         |anonymous| = 27, |{A-status paths}| = 27, and the two sets are EQUAL
         (P7-7).  UGA-INV-01 therefore measures the developer's staging area,
         not the repository.  `git restore --staged` clears it to zero with no
         mint.  EV-14's measurand is not a property of any commit.

    U-E  [NEW] Two non-equivalent definitions of the terminal state (above).

    U-F  [NEW] REG-AUTO-001 §7 — the constitutional completion law that
         register.sh:16 cites as its own authority — is consumed by NO phase in
         this chain.  It is an 8-REGISTER conjunction, not the 10-PHASE one the
         script enforces; its realization table names SIX phases where ten
         exist; it has NO vocabulary for a transaction that did not run; and
         its §8 invariant `count(artifacts.json) == in-scope files` is
         VIOLATED TODAY BY EXACTLY 9.  [MEASURED, P7-3, P7-10]

    U-G  [NEW] EV-1 / EV-24 bind a COUNT (>=77), not a set.  Removing a Phase-1
         test and adding a new one is undetectable by the stated condition.

    U-H  [NEW] The NO_ALLOCATION path performs NO actor binding, holds no
         permit_id and touches no register.  Under closure CB-1 the program's
         THIRD authorization event uses it, so that event is unissued,
         unconsumed, unrecorded and unattributable in all 12 models.

    UK-1 (6 components) and UK-2 (4) — execution-time, irreducible.  Carried.

  U-D … U-H are ALL closable by determination.  §10.4 proves that closing
  U-B … U-H reduces the set to exactly {UK-1, UK-2} over the enumerated
  surfaces, and states precisely what "enumerated" bounds.
================================================================================
```

### 1.2 The nine questions, one line each

| Q | Answer |
|---|---|
| **Q1 Completion definitions** | **30 definitions inventoried** across source, governing law, and the three packages. **12** machine-enforced, **18** documentary. **2** necessary-and-claimed-sufficient. **4** mutually contradictory pairs. **2** of the five names the task uses have **no referent anywhere**. §3 |
| **Q2 U-B** | Root cause is **not** the early return; it is that the authority has **two** admission modes and the re-run needs a **third**. The re-run partitions into **3** manifest classes; `C-1` authorizes **1**. **7** closure classes enumerated. U-B is specification-, implementation- **and** model-dependent — all three, not one. §4 |
| **Q3 U-C** | **4** reachable false-positive completion states, **6** false-negative. **10** lock states measured (Phase 6 found 7). Minimum discriminating evidence: **8** items. **0** redundant evidence items; **7** non-discriminating; **1** tautological. §5 |
| **Q4 Evidence soundness** | 27 items: **9 SAFE · 4 UNSAFE · 6 UNPROVEN · 1 TAUTOLOGICAL · 7 NON-DISCRIMINATING**. **3** unproducible (Phase 6 found 2). The only evidence that survives a full rollback (`EV-7`/`EV-26`) is also the only evidence with **no integrity binding of any kind**. §6 |
| **Q5 Authorization accounting** | **0 of 12** models reach COMPLETE. Across 6 dimensions × 12 models = **72 cells**: **18 COMPLETE · 42 PARTIAL · 12 AMBIGUOUS · 0 UNDEFINED**. Expiry is AMBIGUOUS in all 12 because modifier `T` is free and `expires_at` has no producer. §7 |
| **Q6 Terminal-state equivalence** | **NOT equivalent — pairwise, with 6 separating conditions, every one measured.** `EXECUTION-SUCCESSFUL` and `EXECUTION-VERIFIED` have **0 occurrences** in the chain and in the source; they are constructed here explicitly. `EXECUTION-CERTIFIED` has two readings, one of which is **provably empty**. §8 |
| **Q7 Path enumeration** | **106** distinct paths, correcting Phase 6's **58**. The gap is `EV-22`, omitted as a confirmation branch factor although Phase 6's own `T-1f` depends on it. **12** paths reach COMPLETED under Phase 6's definition, **8** under Phase 5's; **2** are genuine; **0** are reachable on the package as specified. §9 |
| **Q8 Closure sufficiency** | **NO.** {U-B, U-C} is insufficient. The residual set is **7**. §10 proves that {U-B…U-H} reduces it to **{UK-1, UK-2}** and nothing else, over the six enumerated surfaces. §10 |
| **Q9 Phase-9 feasibility** | **All three outcomes remain reachable.** **B is provable today without any run**, deductively, under the residual-freedom reading. **A** requires `T-1a` and is therefore hostage to U-A. **C** is the status quo. Phase 7 removes no outcome; what it removes is the possibility of reaching A or B **by accident**. §11 |

### 1.3 What this phase looked for and did not find

Stated first, because a phase that reports only defects has not been rigorous about the parts that hold.

| Checked | Result |
|---|---|
| Is `register.sh --guard` — which the lock defeats — invoked anywhere live? | **NO, and this bounds U-C.** **[MEASURED]** **P7-12**: `--guard` has **0** live call sites. The only two live invocations of `register.sh` anywhere in the repository are `--observe` (`verify.sh:799` and `.github/workflows/ucos-registration-gate.yml:60`), and **`--observe` returns at `:178`, before the lock guard at `:187`**. The read-only plane is structurally immune to U-C. `--guard` becomes reachable only through `--install-hooks`, which `PHASE5` `G-10` already prohibits. |
| Does the ledger sit at its snapshot fixed point, so that a re-run appends nothing to `history`? | **YES today — and this is what makes closure `C-1` viable at all.** **[MEASURED]** **P7-2**: for all **1597** projected artifacts, the last recorded snapshot agrees with `artifacts.json` on `content_hash`, `status`, `path` and `name` — **0** drift. The 36 `version` differences are the raw-token-versus-semver distinction `ukb.py:983` creates deliberately, not drift. |
| Is `uga_engine gate` genuinely read-only? | **YES, re-measured.** **[MEASURED]** **P7-6**: ledger `sha256` identical, all three `.runtime` logs byte-identical, guard directories unmoved. `cmd_gate` calls `build(mint=False)` and never reaches `emit()`. |
| Is the 30-invariant surface still 30, with the same two failures? | **YES, exactly.** **[MEASURED]** **P7-6**: 30 invariants, `UGA-INV-01 FAIL violations=27 measured=6804`, `UGA-INV-10 FAIL violations=27 measured=5207`, identical violation sets, `GATE FAILED — 2 blocking invariant(s)`. `PHASE4` **P4-4** confirmed without amendment. |
| Is the `by_path` gap still 9, and the same 9 files? | **YES.** **[MEASURED]** **P7-3**, computed in-process through `ukb._iter_files()`: eligible **1606**, registered **1597**, gap **9**, and the nine names are byte-for-byte Phase 6's list. All nine are **committed and clean** (**P7-3b**), so UK-1's population — unlike UK-2's — is a property of HEAD and is stable under index operations. |
| Does `EV-25` overreach by claiming a successful run can evidence `R-7w`? | **NO — Phase 4 and Phase 5 scoped it correctly.** `EV-25` names R-7's *document comparison* at `:920`, which does run on a successful write, not R-7w's *window* `:893`→`:921`, which only a refusal traverses. `PHASE4:§G.3` is exactly right and `PHASE5` `EV-25` inherits it faithfully. What `EV-25` lacks is a producer, not scope discipline (§6.3). |
| Do the two runs share an actor between `plan()` and `commit()`, so that `manifest_digest`'s actor term cannot silently diverge? | **YES.** **[MEASURED]** **P7-11**: `ukb.py:1287` binds `_actor` once and passes the same variable to `plan()` at `:1291` and `commit()` at `:1300`; `uga_engine.py` repeats the literal at `:2079` and `:2098` and they are identical strings. The actor is bound **twice over** — strictly at `:728` and again inside `manifest_digest` (`:558`) — which is defence in depth no prior phase recorded. |

**[INFERRED]** Every structural result of Phases 2–6 survives this audit: the 12 admissible models, the 13 forced tasks, the 2-mutating-run minimum, the disjointness of the two populations, the read-only character of Stage 0, the per-run and state-bound nature of authorization, the 14-condition gate, the 4 rollback procedures, the 3 residuals, and "no path produces a new blocker". What this phase overturns are **10 specific claims and 3 counts**, enumerated in §13.

---

## 2. Inputs

### 2.1 The eight input documents

| Document | What Phase 7 consumes from it |
|---|---|
| `PHASE0-GOVERNANCE-INDEPENDENT-DETERMINATION.md` | The blocker namespace `E-1`, `E-2`, `E-3`, `E-4A`; the declination precedent that `register.sh` is read, not run |
| `PHASE05-GOVERNANCE-INDEPENDENT-REMEDIATION.md` | `§E.0`'s verified `pytest` invocation — the basis of `EV-1`'s correction; `§F.4`'s bounding of the three residuals by authorization scope |
| `PHASE1-GOVERNANCE-INDEPENDENT-IMPLEMENTATION-REPORT.md` | `§R-7`'s five byte-identity restore tests; `§R-11`'s serializer inequality; the 77-test baseline |
| `PHASE2-GOVERNANCE-CLOSURE-DETERMINATION.md` | The 5 axes, the merges `M1…M5`, `CX-1…CX-6`, `NB-1…NB-6`, and `§D.3`'s 12 = `I-R × A3 × {B1,B2} × {D1,D2} × {Aud1,Aud2,Aud3}` |
| `PHASE3-IMPLEMENTATION-READINESS-DETERMINATION.md` | `Z-01…Z-12`; the 24-task register `F-1…F-13` / `O-1…O-11`; `§E.7`'s residual invariance |
| `PHASE4-EXECUTION-VALIDATION-DETERMINATION.md` | `V-1…V-14`; `E-1…E-7`; `T-0…T-9`; `R-A…R-C`; `§I.1`'s UK-1 five and `§I.2`'s UK-2 four |
| `PHASE5-EXECUTION-TRANSITION-DETERMINATION.md` | `GA-1…GA-9`, `IA-1…IA-11`, `EV-1…EV-27`, `G-1…G-14`, `S-0…S-9`, `R-D`, `X-1…X-4`; `§0.4`'s `EXECUTION-COMPLETE` definition |
| `PHASE6-EXECUTION-AUTHORIZATION-CLOSURE-DETERMINATION.md` | `U-A`/`U-B`/`U-C`; `IA-12`; `H-1…H-14`; the 17 terminal states; `§11.1`'s `EXECUTION-COMPLETED` definition; the object under audit |

### 2.2 Governing-law artifact read this phase — and not read by any prior phase

| Reference | Content established |
|---|---|
| `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-REG-AUTO-001-AUTOMATIC-ARTIFACT-REGISTRATION-STANDARD.md` **§7** | **The constitutional completion law.** `T` is COMPLETE iff **eight** register components succeed *as one unit*; on any failure, *"Transaction Status: INCOMPLETE · Artifact Status: UNREGISTERED · Completion Claim: INVALID"*. Realization table names **six** phases. |
| the same, **§5 P3** | *"Registration is a pure function of repository content + the append-only ledger + `config.py`. Re-running it on unchanged inputs yields byte-identical outputs (idempotence)."* — **the constitutional assertion of the property `EV-23` tests as an unknown** |
| the same, **`:126`** | *"The machine is re-entrant and idempotent (P3): re-running the transaction on an already-`REGISTERED` set is **a no-op** that re-proves synchronization."* |
| the same, **§8** | *"**Invariant:** `count(artifacts.json)` equals the number of in-scope files on disk. A mismatch is an unregistered-artifact defect and fails the guard (§16)."* |

### 2.3 Source read this phase

Every reference below was read against the working tree at `77798202`.

| Reference | Content established |
|---|---|
| `register.sh` — **full 282 lines** | Header `:14-19` (COMPLETE/INCOMPLETE, "safe to run repeatedly"); `--observe` plane `:99-179` **ending in `exit "$RC"` at `:178`**; re-entrancy guard `:187-195`; `fail()` `:201`; ten phases `:206-259`; `:216` passing **no** `--permit`; `TRANSACTION COMPLETE` `:260`; `rm -f "$LOCK"; trap - EXIT` `:262`; `--guard` block `:264-282` |
| `ledger_authority.py:91-115` | `IDENTITY_MAPS` (4 maps); `MONOTONIC_COUNTERS`; **`NON_ALLOCATION_KEYS` includes `history`** — the decisive fact of §4.2 |
| `:386-434` | `allocation_report` — `allocating = bool(total or advances or cursors or unmeasured)` |
| `:437-484` | `format_report` and `_moved_suffix` — `bytes_changed` as the real-versus-no-op discriminator |
| `:534-577` | `_canonical`; `manifest_digest` over **six** named fields including `actor`; `preimage_digest` over the **whole** pre-image document |
| `:580-598` | `git_head` — fail-closed on `OSError` / timeout / non-zero |
| `:601-631` | `load_permit_register` — missing register = empty register; accepts `{"permits": [...]}` **or** a bare list |
| `:634-662` | `build_manifest`, `plan()` |
| **`:684-707`** | The `NO_ALLOCATION` branch — refuses if `allocating`, **then requires whole-document equality `before == after`**. The second check is what §4.2 turns on. |
| `:709-804` | The permit path — **4 strict, 5 elective** bindings, confirmed |
| `:841-933` | `commit()` — 8 refusal points, the mutation point at `:893` |
| **whole module** | **[MEASURED] ZERO `print`, `logging` or `logger` statements** — the basis of `EV-25`'s unproducibility (§6.3) |
| `ukb.py:877-913` | **`allocate()`** — the early return at `:892-894`. **No function named `_path_identity` exists in this file** (§13, correction 3) |
| `ukb.py:314-342` | `record_snapshots` — appends to `ledger["history"]` iff `(content_hash, version, status, path, name)` differs from the last snapshot |
| `ukb.py:1232` | `record_snapshots` is called on **every** build, mint or not |
| `ukb.py:1286-1303` | The `--plan` early return; `_actor` bound once at `:1287` |
| `ukb.py:2369-2385` | The idempotent `exec declare` branch — the **existing** conditional-`NO_ALLOCATION` pattern |
| `ukb.py:737-848` | `_repo_artifact_paths` = `git ls-files --cached --exclude-standard`; `_iter_files` |
| `config.py` | `EXCLUDE_DIR_PREFIXES` **13**, `INCLUDE_EXTENSIONS` **4** |
| `uga_engine.py:178-193` | **`_git_ls` = `git ls-files -z --cached`** — the `by_object` boundary is the **index**, over **every** path, with no extension filter |
| `uga_engine.py:1331-1335`, `:2124-2161`, `:2073-2122` | `UGA-INV-10`; `cmd_gate`'s `GATE PASSED` / `GATE FAILED`; `cmd_run` and its two write sites |
| `platform/tests/test_ledger_authority.py:63-90` | `_issue` — the register's only writer; 8 keys; `head` bound; `expires_at: None`; `scope.max_allocations = total`; **`single_use: True`, read by nothing** |

### 2.4 Evidence classes

| Tag | Meaning |
|---|---|
| **[MEASURED]** | Established by execution or source read **this phase**, or by a named prior-phase probe. |
| **[INFERRED]** | Derived from measured facts by an argument stated at the point of use. |
| **[UNKNOWN]** | Not established, and stated as such. |
| **[GOV-REQ]** | Satisfiable only by a decision. |
| **[EXEC-REQ]** | Satisfiable only by an act. |
| **[DEFECT]** | A specification defect: an artifact, evidence item or definition that cannot do the job assigned to it. Closable by determination. |

---

## 3. Completion-definition matrix — Q1

### 3.0 Scope and method

Every place in the repository or in the eight input documents that states a condition under which something is **complete**, **passed**, **certified**, **sealed** or **valid** at the transaction level. Each is classified on six axes:

- **explicit / implicit** — is the completion condition stated, or only implied by control flow?
- **machine-enforced / documentary** — can a program decide it, or is it prose addressed to a reader?
- **necessary** — must it hold for `EXECUTION-COMPLETED`?
- **sufficient** — does it alone establish `EXECUTION-COMPLETED`?
- **contradictory** — does it conflict with another definition in the inventory?
- **incomplete** — does it leave a reachable state unclassified?

### 3.1 Class A — source code (`register.sh`)

| ID | Definition | Site | Expl. | Enforced | Nec. | Suff. | Contra. | Incomplete |
|---|---|---|---|---|---|---|---|---|
| **CD-1** | `TRANSACTION COMPLETE — every artifact on disk is registered, classified, validated, and synchronized` + exit 0 | `:259-260` | explicit | **machine** (exit 0) + documentary (the line) | **YES** | no | no | **YES** — silent on drift, on idempotence, and on the lock no-op |
| **CD-2** | `fail()`: `TRANSACTION INCOMPLETE — <reason>` · `Artifacts remain UNREGISTERED; completion claims INVALID` · nonzero exit | `:201` | explicit | **machine** | **YES** (negatively) | no | no | **YES** — **unreachable for lock states B, D, F and G**, which terminate before `fail()` is defined |
| **CD-3** | *"The transaction is COMPLETE only if every phase succeeds."* | `:14-16` | explicit | documentary | **YES** | **claims sufficiency** | **YES** — falsified by `:187-192`, a path that exits **0** having run **no** phase | — |
| **CD-4** | *"safe to run repeatedly"* — the idempotence claim | `:18-19` | explicit | documentary | — | — | no | **YES — this is precisely `UK-1` item 5 / `EV-23`, asserted rather than established** |
| **CD-5** | `OBSERVATION PASSED — registration state valid; nothing minted, nothing written` · `RC=0` | `:174` | explicit | **machine** (`RC` 0/2/3/4/5) | no | no | no | **YES** — `RC=0` accepts a **staged** register (`P5-1`), which `--guard` rejects |
| **CD-6** | `Guard PASSED — repository, registry, control tower, twin, and portal are in sync` · exit 3 on drift | `:274-281` | explicit | **machine** | no | no | no | **YES — defeated by a stale lock**, which exits 0 at `:191` before the guard block is reached (§5.2, FP-D) |

### 3.2 Class B — source code (the phase tools)

| ID | Definition | Site | Expl. | Enforced | Nec. | Suff. | Contra. | Incomplete |
|---|---|---|---|---|---|---|---|---|
| **CD-7** | `ENFORCEMENT PASSED — no unregistered or invalid artifact` · record `result: PASS\|FAIL` | `ukb.py:2092`, `:2137-2142` | explicit | **machine** | YES (phases 0, 9) | no | no | no |
| **CD-8** | `ukb validate` — append-only, no duplicate IDs/pages, referential integrity | phase 5 | implicit | **machine** | YES | no | no | no |
| **CD-9** | `ukbx validate` — signal-ledger integrity, provenance, secret-free | phase 6 | implicit | **machine** | YES | no | no | no |
| **CD-10** | `RESULT: CERTIFIED \| NOT-CERTIFIED` (digital-twin hard checks) | `ukbx.py:574-582` | explicit | **machine** | YES (phase 7) | no | no | no |
| **CD-11** | `verdict = "CERTIFIED" if passed == len(domains)`, 9 integrity domains; `CERTIFICATION FAILED` otherwise | `ukbx.py:1256`, `:1280-1284` | explicit | **machine** | YES (phase 8) | no | no | no |
| **CD-12** | `GATE PASSED — no anonymous, unowned, unregistered or unaudited object` · exit 0/1 | `uga_engine.py:2160` | explicit | **machine** | YES (for `UK-2`) | no | no | **YES — NON-DISCRIMINATING.** **[MEASURED]** §5.3: satisfied by an index operation as readily as by a mint |

### 3.3 Class C — source code (the authority)

| ID | Definition | Site | Expl. | Enforced | Nec. | Suff. | Contra. | Incomplete |
|---|---|---|---|---|---|---|---|---|
| **CD-13** | `report["authorization"] ∈ {"PERMIT", "NO_ALLOCATION"}` — the write was authorized | `:878-879` | explicit | **machine** | **YES** | no | no | **YES** — `NO_ALLOCATION` carries no `permit_id`, no actor check and no register entry (`U-H`, §7.6) |
| **CD-14** | `report["bytes_changed"]` — *"distinguishes a real allocation from an idempotent no-op rewrite"* | `:868`, `:476-484` | explicit | **machine** | **YES** | no | no | no — **this is the one field in the chain that discriminates a no-op correctly** |
| **CD-15** | `_refuse_unmoved_allocation`: `allocating ∧ bytes_changed is False` ⇒ refuse | `:825-838`, `:929` | implicit (a completion **negation**) | **machine** | — | — | no | **YES — structurally unreachable on the non-allocating re-run**, since `allocating` is False there (`PHASE6:§7.2`, confirmed) |
| **CD-16** | `assert_append_only` — removal, re-issue, record-body change and `history`-prefix loss are refused | `:283-383` | implicit | **machine** | YES | no | no | no |
| **CD-17** | `_verify_permit` — 9 bindings, 4 strict / 5 elective | `:709-804` | explicit | **machine** | **YES** | no | no | **YES** — the 5 elective bindings are unenforced unless the issuer elects to emit them (`IA-12`) |
| **CD-18** | `commit()` docstring: *"what make 'verified' and 'written' the same state rather than two states nothing compared"* | `:864-866` | explicit | documentary | — | — | no | no |

### 3.4 Class D — governing law (REG-AUTO-001), consumed by no phase in this chain

| ID | Definition | Site | Expl. | Enforced | Nec. | Suff. | Contra. | Incomplete |
|---|---|---|---|---|---|---|---|---|
| **CD-19** | **`T` is COMPLETE iff all EIGHT register components succeed as one unit** — Artifact File ⊕ Artifact Registry ⊕ Execution Registry ⊕ Control Tower ⊕ Digital Twin ⊕ Traceability ⊕ Dependencies ⊕ Page/ID Ledger | §7 | explicit | documentary | **YES — it is the cited authority for CD-2's *"completion claims INVALID"*** | **claims sufficiency** | **YES — not equivalent to CD-1.** CD-1 is a **10-phase** conjunction; CD-19 is an **8-register** conjunction. Phases 0, 2, 8 and 9 of the script are `\|\| fail` gates that correspond to **no** CD-19 component | **YES — CD-19 is two-valued (COMPLETE / INCOMPLETE) over a three-valued reality. It has no term for a transaction that was not attempted, which is exactly what `register.sh:187-192` produces.** |
| **CD-20** | **P3 — Deterministic derivation.** *"Re-running it on unchanged inputs yields byte-identical outputs (idempotence)."* | §5 P3 | explicit | documentary | — | — | **YES — asserts as a LAW the property `UK-1` item 5 treats as an UNKNOWN.** `EV-23` is therefore a falsification test of a declared law, not merely of an implementation | — |
| **CD-21** | *"re-running the transaction on an already-`REGISTERED` set is **a no-op** that re-proves synchronization"* | `:126` | explicit | documentary | — | — | **YES — the governing law's word for the CORRECT re-run is the same word `register.sh:190` prints for the PATHOLOGICAL one.** Two disjoint states share one name in one tool | — |
| **CD-22** | **§8 invariant:** `count(artifacts.json)` equals the number of in-scope files on disk | §8 | explicit | documentary (enforced in spirit by CD-7) | YES | no | no | **VIOLATED TODAY BY EXACTLY 9.** **[MEASURED]** **P7-3**: `count(artifacts.json) = 1597`, in-scope = **1606** |
| **CD-23** | **P5 — Atomicity.** *"Partial registration is a failed transaction, not a partial success."* | §5 P5 | explicit | documentary | YES | no | no | **YES** — `A✗` (a failure in phases 2…9) leaves tracked state **mutated and unsealed**, which is a partial registration the law says cannot exist |
| **CD-24** | §7 realization table — *"whose **six** phases map onto the components above"* | §7 | explicit | documentary | — | — | **YES — the script has TEN** | — |

### 3.5 Class E — the transition / validation / authorization packages

| ID | Definition | Site | Expl. | Enforced | Nec. | Suff. | Contra. | Incomplete |
|---|---|---|---|---|---|---|---|---|
| **CD-25** | `UK-1` retired by **5** evidence items (items 1–5) | `PHASE4:§I.1` | explicit | documentary | YES | **claimed sufficient** | no | **YES** — Phase 6 derives a **6th**; item 5 is falsifiable-by-accident |
| **CD-26** | `UK-2` retired by **4** evidence items | `PHASE4:§I.2` | explicit | documentary | YES | **claimed sufficient** | no | **YES** — item 2 is non-discriminating (§5.3) |
| **CD-27** | `T-1`: `A✓ ∧ B✓` ⇒ 0 blockers, 0 unknowns | `PHASE4:§H.2` | explicit | documentary | — | **claimed** | no | **YES** — no confirmation branch; Phase 6 splits it into six |
| **CD-28** | **`EXECUTION-COMPLETE` ≝ *"Both runs landed and both unknowns retired."*** | `PHASE5:§0.4` | explicit | documentary | YES | **YES by fiat** | **YES — contradicts CD-30** | — |
| **CD-29** | `S-9`: *"AUTHORIZATION STATE: EXECUTION-COMPLETE (only if both runs succeeded)"* | `PHASE5:§E.1` | explicit | documentary | YES | **weaker than CD-28 — omits unknown retirement** | **YES — contradicts CD-28 within the same document** | — |
| **CD-30** | **`EXECUTION-COMPLETED` ≝ `A✓ ∧ B✓ ∧ EV-23 ∧ EV-24 ∧ EV-25`** | `PHASE6:§11.1` | explicit | documentary | YES | **claimed** | **YES — `EV-22` is omitted, so `UK-2` may be OPEN in a state this definition calls COMPLETED** | — |
| **CD-31** | `T-1a`: *"0 blockers · 0 unknowns · complete"* | `PHASE6:§8.1` | explicit | documentary | — | — | consistent with CD-28; **not** derivable from CD-30 | — |
| **CD-32** | `T-1f`: *"complete; surface not reached"*, unknowns **1** (`UK-2`) | `PHASE6:§8.1` | explicit | documentary | — | — | **YES — reachable under CD-30, IMPOSSIBLE under CD-28** | — |
| **CD-33** | `AUTHORIZATION-WITHHELD` as a legitimate terminal state with 0 blockers | `PHASE5:§G.5`, `X-4` | explicit | documentary | — | — | no | no |

### 3.6 Class F — completion definitions present in the repository and consumed by nothing in this chain

| ID | Definition | Site | Note |
|---|---|---|---|
| **CD-34** | `engine/certification_integrity/gate.py` — *"exit 1 CLOSED a blocking law was measured and REFUSED · exit 2 FAULT no verdict could be reached"* | `gate.py:4-5` | A complete, machine-enforced, three-valued completion vocabulary — **including the third value CD-19 lacks**. Referenced by **no** phase in this chain. |
| **CD-35** | `.github/workflows/omega-gate.yml` — *"Exit 0 all five criteria hold, 1 a criterion refused, 2 FAULT (no verdict could be produced)"* | `omega-gate.yml:30-31` | Likewise three-valued; likewise unreferenced. |

### 3.7 Class G — names used by the Phase-7 task itself with no referent

| ID | Name | Occurrences in the eight inputs | Occurrences in the source tree | Consequence |
|---|---|---|---|---|
| **CD-36** | `EXECUTION-SUCCESSFUL` | **0** | **0** | Must be **constructed** before Q6 can be answered. §8.2 constructs it and labels the construction. |
| **CD-37** | `EXECUTION-VERIFIED` | **0** | **0** | As above. |

**[MEASURED]** **P7-9**: counted across all eight input documents and across `00-BOOK/tools`, `00-MASTER/UCOS-UGA-001`, `engine/` and `platform/`. For contrast: `EXECUTION-AUTHORIZED` **36**, `READY-FOR-EXECUTION` **40**, `EXECUTION-COMPLETE` **14**, `EXECUTION-COMPLETED` **11**, `EXECUTION-CERTIFIED` **5** — and all five of the last are Phase 6 saying it is undefined. **No terminal-state name in this vocabulary appears anywhere in the source tree.**

### 3.8 The contradictory pairs, isolated

**[INFERRED]** Four pairs, each measured, each with a consequence.

| # | Pair | Nature of the conflict | Consequence |
|---|---|---|---|
| **1** | **CD-3 vs the lock guard** | CD-3 says COMPLETE requires every phase to succeed. `register.sh:187-192` exits **0** having run no phase. | The script's own header is falsified by the script's own control flow. This is U-C's textual root. |
| **2** | **CD-19 vs CD-1** | An **8-register** conjunction versus a **10-phase** conjunction. Phases 0, 2, 8, 9 correspond to no CD-19 component; CD-19's "Execution Registry" and "Dependencies" components are satisfied inside phase 1. | **A transaction can be INCOMPLETE by CD-1 and COMPLETE by CD-19** — e.g. a `ukbx certify` failure (phase 8, `|| fail`, exit 2) leaves all eight CD-19 components satisfied. Nothing in the chain adjudicates. |
| **3** | **CD-28 vs CD-30** | *"both unknowns retired"* versus a conjunction that omits `EV-22`. | **Numeric**: 8 completion paths under CD-28, 12 under CD-30 (§9.4). `T-1f` exists under one and not the other. |
| **4** | **CD-21 vs `register.sh:190`** | The governing law calls the correct idempotent re-run *"a no-op"*; the script prints *"nested/concurrent call is a **no-op**"* for a run that did not happen. | An operator reading either in isolation cannot distinguish them, and `EV-23` as worded cannot either (§5.2). |

### 3.9 Q1 verdict

```
COMPLETION AND TERMINAL-STATE DEFINITIONS INVENTORIED .............. 35
    in source code ................................................. 18   CD-1 … CD-18
        register.sh ................................................  6   CD-1 … CD-6
        the phase tools ............................................  6   CD-7 … CD-12
        the authority ..............................................  6   CD-13 … CD-18
    in governing law (REG-AUTO-001) ................................  6   CD-19 … CD-24
    in the transition / validation / authorization packages ........  9   CD-25 … CD-33
    in the repository, consumed by NO phase of this chain ..........  2   CD-34, CD-35
                                                                    ─────
                                                                      35

  NAMES USED BY THE TASK WITH NO REFERENT ANYWHERE .................  2   CD-36, CD-37
      EXECUTION-SUCCESSFUL   0 occurrences in the 8 inputs, 0 in the source
      EXECUTION-VERIFIED     0 occurrences in the 8 inputs, 0 in the source
                                                    total IDs assigned .. 37

  BY ENFORCEMENT
    machine-enforced .............................................. 17
    documentary ................................................... 18
        of which documentary AND load-bearing (a named consumer
        depends on the prose) .....................................  9

  BY LOGICAL ROLE
    necessary for EXECUTION-COMPLETED ............................. 14
    claimed sufficient ............................................  6   CD-3, CD-19, CD-25,
                                                                          CD-26, CD-28, CD-30
    ACTUALLY sufficient ...........................................  0
    member of >=1 contradictory pair ..............................  8   CD-1, CD-3, CD-19,
                                                                          CD-21, CD-28, CD-29,
                                                                          CD-30, CD-32
    contradictory PAIRS ...........................................  4   §3.8
    incomplete (leave a reachable state unclassified) ............. 13
    non-discriminating (satisfied by a state they do not measure) .  2   CD-6, CD-12

  THE DECISIVE RESULT OF Q1
    The definition register.sh:16 names as its OWN AUTHORITY — REG-AUTO-001 §7 —
    is consumed by NO phase of this chain; is NOT equivalent to the condition the
    script enforces (8 registers vs 10 phases); carries a realization table stale
    by FOUR phases; has NO vocabulary for a transaction that did not run; and
    states an invariant (§8) that is VIOLATED TODAY BY EXACTLY 9.
    That is U-F, and it is new.
```

---

## 4. U-B analysis — Q2

Phase 6 established three things about U-B: permit reuse fails on the re-run, `EV-23` is unproducible, and run-2 authorization is inconsistent. This section determines the root cause, the minimum artifact set, the dependency class, and the complete space of closures. **It does not choose.**

### 4.1 The exact root cause — stated at three depths

**Depth 1 — the mechanical fact.** **[MEASURED]** `ukb.py:892-894`, inside `allocate()`:

```python
entry = ledger["by_path"].get(relpath)
if entry:
    return entry["universal_id"], entry["page_start"], entry["page_count"]
```

An already-allocated path consumes no sequence number, writes no ledger entry and reaches no clock (`_now()` is reached only at `:914`). After run A, all **1606** eligible paths are allocated (**P7-3**: 1597 today + the 9 run A mints), so the re-run's allocation manifest is `allocating=False`, `total_allocations=0`, `allocated={}`, and the run-1 permit fails `manifest_digest` (`:735`) **and** `preimage_digest` (`:743`).

**Depth 2 — why the sentinel is not simply the answer.** **[MEASURED]** `:698-707`. `NO_ALLOCATION` performs **two** checks, not one:

```python
if manifest["allocating"]:                       # check 1
    raise PermitRefused("... this write ALLOCATES ...")
if before is not None and after is not None and before != after:   # check 2
    raise PermitRefused("... this write MUTATES the ledger: top-level key(s) ... differ")
```

Check 2 is a **whole-document** equality, and **[MEASURED]** `NON_ALLOCATION_KEYS` (`:103-115`) includes `history`. So a `history` append leaves `allocating` **False** — it is not counted as an unmeasured map — while making `before != after` **True**. **A `history`-only delta is invisible to check 1 and fatal to check 2.**

**Depth 3 — the root cause proper.** **[INFERRED]** The authority admits exactly **two** kinds of write:

1. a write that allocates, authorized by a permit naming its manifest;
2. a write that changes **nothing at all**, authorized by the sentinel.

There is **no third mode for a write that allocates nothing and changes something**. That write class is exactly the subject of **axis `D`** (`PHASE2:§C.7`: *"`D1` a permit may authorize a non-allocating mutation · `D2` such writes are authorized by a distinct mechanism · `D3` such writes do not occur"*).

> **Root cause.** `IA-4` / `F-4` was specified — `PHASE3:§C.0`, *"A verified permit reaches `ukb build --mint`"* — as a **static** plumbing, with **no reference to axis `D`**, while the second `register.sh` run is a member of axis `D`'s subject class whenever the ledger document moves without allocating. U-B is not a defect in the early return; the early return is correct and documented. It is that **the second run was never classified against the axis that governs it**.

### 4.2 The three manifest classes of the re-run — the correction to Phase 6

**[INFERRED]** From §4.1 the re-run's manifest falls into exactly one of three classes, decidable at the instant of the re-run and **not before**.

| Class | Trigger | `allocating` | ledger document vs pre-image | run-1 permit | `NO_ALLOCATION` | a fresh permit | `EV-23` "zero byte changes" |
|---|---|---|---|---|---|---|---|
| **M1** | nothing changed | `False` | **equal** | **REFUSED** — 2 bindings | **ACCEPTED** | `D1`: issuable but authorizes nothing · `D2`: **not issuable** | **satisfied genuinely** |
| **M2** | any eligible artifact's `content_hash`, `version`, `status`, `path` or `name` changed since run A ⇒ `record_snapshots` appends to `history` | `False` | **differ** (`history`) | **REFUSED** — 2 bindings | **REFUSED** — check 2 | `D1`: issuable · `D2`: **requires `O-7`'s alternative branch** | **FAILS** — the ledger moved |
| **M3** | any new `by_path`-eligible path entered the index | **`True`** | differ | **REFUSED** — 2 bindings | **REFUSED** — check 1 | issuable in `D1` and `D2` (it allocates) | **FAILS** — an allocation landed |

**[MEASURED]** **P7-2** establishes which class obtains **today**: the ledger is at its snapshot fixed point. For all 1597 projected artifacts the last recorded snapshot agrees with `artifacts.json` on `content_hash`, `status`, `path` and `name` — **0 drift**. So a re-run today appends nothing to `history`, and **M1 obtains**.

**[MEASURED]** **P7-4** establishes how easily M3 is entered: **42** untracked files in this repository would become `by_path`-eligible on `git add` — every root-level `PHASE*.md`, `PHASE_OMEGA_*.md`, `IMPLEMENTATION_*.md` and `ARBITRATION_ACCEPTANCE_RECORD.md`. A single `git add -A` between run A and the re-run takes the population from **9** to **51** and puts the re-run in **M3**.

**[INFERRED] The correction to Phase 6.** `PHASE6:§3.6` treats U-B as one defect with two closures, `C-1` (conditional `IA-4` passing `NO_ALLOCATION`) and `C-2` (a third permit). **`C-1` authorizes M1 only.** In M2 the sentinel is refused by check 2; in M3 by check 1. `C-2` is worse: a permit issued in advance must name a manifest, and which manifest the re-run will present is not knowable in advance, because it depends on content changes that occur between the two runs. **Neither Phase-6 closure is complete.**

### 4.3 Minimum artifact set involved

**[INFERRED]** The set of package artifacts whose content changes if and only if U-B is closed.

| # | Artifact | Why it is in the set |
|---|---|---|
| 1 | **`IA-4`** | The plumbing itself. Must dispatch on the measured manifest, not carry a fixed value |
| 2 | **`IA-12`** | The issuer election record — a class-M2 or class-M3 re-run needs a permit, and a permit is not constructible without the actor literal and the 3 field elections (`PHASE6:§3.5`) |
| 3 | **`IA-2`** | **Under `D2` only** — `O-7`'s alternative authorization branch lives at `ledger_authority.py:714-804` |
| 4 | **`EV-3` / `EV-11`** | Permit A's manifest and the permit itself — the re-run's class is measured against the state permit A authorized |
| 5 | **`EV-23`** | The evidence item that cannot be produced |
| 6 | **`UK-1` item 5** | Unreachable while `EV-23` is |
| 7 | **`UK-1` item 6** | Phase 6's derived item — the re-run's own `commit()` report |
| 8 | **`GA-6`** | Adopts `UK-1`'s closure set; if the set changes, `GA-6`'s content changes |
| 9 | **`GA-9`** | Records the axis-parameterized conditions; §4.4 adds a fourth |

```
MINIMUM ARTIFACT SET FOR U-B ......................................  9
    required under all 12 models ..................................  8
    required under D2 only (6 of 12) ..............................  1   IA-2 / O-7
    NEW to this phase (not in PHASE6's U-B statement) .............  2   GA-9's 4th content item,
                                                                          and IA-2 under D2
```

### 4.4 Dependency classification — Phase 6 called U-B a specification defect; it is all three

| Class | Verdict | Proof |
|---|---|---|
| **Model-dependent?** | **YES — via axis `D`, and only via `D`.** | **[MEASURED]** `PHASE2:§C.7`. Under `D1` (6 of 12: `Z-01…Z-03`, `Z-07…Z-09`) a permit may authorize a non-allocating mutation, so class M2 is closable by issuance. Under `D2` (6 of 12: `Z-04…Z-06`, `Z-10…Z-12`) it may **not**, so class M2 must route through `O-7` — an implementation task that exists in the register **only for those 6 models**. **[MEASURED]** `PHASE3:§B.4` further records that `D2` *"must not re-kill `ukb.py:2380-2384"`* — the very branch closure `CB-1` depends on. Axis `B` and axis `Aud` are **not** implicated: the sentinel path reads no use record and no audit log. |
| **Implementation-dependent?** | **YES.** | **[MEASURED]** Closures `CB-1`, `CB-4` and `CB-7` (§4.5) are pure implementation and require no governance input. The pattern `CB-1` needs already exists at `ukb.py:2380-2384`, verbatim, with a comment stating why it is correct *"BY CONSTRUCTION, not by assumption"*. |
| **Specification-dependent?** | **YES.** | **[INFERRED]** The defect was **introduced** by a specification: `PHASE3:§C.0` `F-4` fixes `IA-4` as static. And closures `CB-5` and `CB-6` are specification changes — they alter what `EV-23` means rather than what the code does. |

**[INFERRED]** This is the **fourth** axis-parameterized content item beyond Phase 5's five and Phase 6's sixth — but unlike Phase 6's sixth it is not merely *which mechanism*, it is *whether a mechanism exists at all* for one of three reachable classes. `GA-9` must therefore record a fourth content item: **the re-run's authorization mechanism, per manifest class, per axis-`D` value.**

### 4.5 All logically possible closure classes — enumerated, not chosen

**[INFERRED]** The space is generated by asking, for each of the three classes M1/M2/M3, where the authorization can come from. Seven classes exhaust it. Each is stated with its mechanism, its coverage over {M1, M2, M3}, and its cost. **None is preferred; constraint 8 forbids it.**

| ID | Mechanism | Covers | Cost / consequence |
|---|---|---|---|
| **CB-1** | **Runtime authorization dispatch at the call site.** `register.sh` / `ukb.py` selects the `permit` argument from the manifest measured immediately beforehand: `NO_ALLOCATION` in M1, a permit in M2/M3. | **M1** always; **M2, M3** only if an issuance step is inserted between the measurement and the run | **[MEASURED]** the two-way form of the pattern exists at `ukb.py:2380-2384`. The three-way form does not. Preserves `PHASE5:§E.4`'s 2-authorization minimum **only in M1**; in M2/M3 it raises it to 3. |
| **CB-2** | **A third permit issued in advance**, before the re-run. (`PHASE6`'s `C-2`.) | **M1** vacuously (a permit for an empty manifest authorizes nothing); **M2, M3 not at all** | **[INFERRED] Structurally incomplete.** A permit binds `manifest_digest` and `preimage_digest`; the re-run's manifest is not knowable until the re-run's pre-image is fixed, and it is not fixed until every act between the two runs is complete. Axis-`D`-dependent: under `D2` an empty-manifest permit is not issuable at all. |
| **CB-3** | **Widen the sentinel's admissible domain** — a claim asserting "allocates nothing, and the only document delta is an append to `history`", checked against `NON_ALLOCATION_KEYS`. | **M1, M2**; **not M3** | Touches `ledger_authority.py:684-707` — the authority's admission logic. **[MEASURED]** under `D2` this *is* `O-7`, already a task in 6 of 12 models; under `D1` it is a new task in none of them. Weakens the sentinel's docstring claim that it *"can only ever permit less"*. |
| **CB-4** | **Close by precondition** — require the re-run to occur under a proven-unchanged corpus: index frozen and no eligible artifact's content changed since run A, both verified read-only immediately beforehand. | **M1**, by making M2 and M3 **unreachable** rather than authorized | No code. Adds a gate condition and two read-only checks. **[MEASURED]** the checks are computable: `git write-tree`-class index identity plus the `record_snapshots` comparison **P7-2** performs. Does not authorize M2/M3; it forbids the states that produce them. |
| **CB-5** | **Redefine `EV-23` as a read-only idempotence measurement** — re-derive and compare documents without executing the transaction. | Removes the authorization problem entirely; covers **none** of M1/M2/M3 because no re-run occurs | **[MEASURED]** `--plan` exists on `ukb build` and `uga_engine run` and **nowhere in `ukbx.py`** (`PHASE4` **P4-6**), so this closes phase **1 of 10** and re-opens the coverage question for phases 2, 3, 4 and 8 — which is `UK-1`'s entire content. Trades an authorization defect for an evidence defect. |
| **CB-6** | **Retire `UK-1` item 5**, accepting `UK-1` on items 1–4. | n/a | **[MEASURED]** `PHASE4:§I.1` states item 5 is *"required, not optional. Without it, `register.sh` completing once is compatible with the drift gate never being green."* Retiring it amends `GA-6`, so this closure is **[GOV-REQ]** — it is **not** a governance-independent closure, and it is the only one of the seven that is not. |
| **CB-7** | **Give the re-run a non-mutating mode by construction** — a plane in which the ledger writer is unreachable for all ten phases. | Removes the authorization problem; covers none of M1/M2/M3 | Equivalent in required work to adding `--plan` to `ukbx.py` — the same four phases `CB-5` needs, plus the routing. Larger than any task in the 24-task register. |

```
CLOSURE CLASSES FOR U-B ...........................................  7   CB-1 … CB-7
    covering all THREE manifest classes ...........................  0
    covering M1 and M2 ............................................  1   CB-3
    covering M1 only, by authorization ............................  2   CB-1, CB-2*
    covering M1 only, by PRECONDITION (M2/M3 made unreachable) ....  1   CB-4
    dissolving the problem by changing what EV-23 measures ........  2   CB-5, CB-7
    dissolving it by retiring the evidence item ...................  1   CB-6
      * CB-2 covers M1 only vacuously and is structurally
        incomplete for M2/M3 — see the table

    GOVERNANCE-INDEPENDENT (closable with no answer to FD-1…FD-5)..  5   CB-1, CB-3*, CB-4,
                                                                          CB-5, CB-7
        * CB-3 is governance-independent in MECHANISM but is
          axis-D-CONDITIONED in whether it is a new task or an
          existing one (O-7)
    GOVERNANCE-DEPENDENT ..........................................  2   CB-2 (axis D), CB-6 (GA-6)

    RAISING PHASE5's 2-AUTHORIZATION MINIMUM TO 3 .................  3   CB-1 in M2/M3, CB-2, CB-3
    LEAVING IT AT 2 ...............................................  2   CB-4, CB-6
    MAKING IT INDETERMINATE (depends on the class at run time) ....  2   CB-5, CB-7
```

### 4.6 Q2 verdict

```
EXACT ROOT CAUSE
    The authority admits TWO write modes — allocating-with-permit, and
    changes-nothing-with-sentinel — and the second register.sh run needs a THIRD:
    allocates-nothing-but-changes-something.  That class is axis D's subject.
    IA-4 was specified without reference to axis D.

MINIMUM ARTIFACT SET .............................................  9
MANIFEST CLASSES OF THE RE-RUN ...................................  3   M1, M2, M3
    authorizable by PHASE6's C-1 ..................................  1   M1 only
    obtaining today ...............................................  M1   [MEASURED] P7-2
    reachable by a single `git add -A` ............................  M3   [MEASURED] P7-4, 42 files

MODEL-DEPENDENT ..................................................  YES  axis D, and only D
IMPLEMENTATION-DEPENDENT .........................................  YES  CB-1, CB-4, CB-7
SPECIFICATION-DEPENDENT ..........................................  YES  PHASE3 §C.0 F-4;
                                                                         CB-5, CB-6
    => PHASE6's classification of U-B as "a specification defect" is
       INCOMPLETE.  It is all three at once, and the model-dependence is
       what makes the primary question's seventh clause — "no additional
       governance decision is required" — FALSE under 6 of 12 models.

CLOSURE CLASSES ..................................................  7
RECOMMENDED ......................................................  0
```

---

## 5. U-C analysis — Q3

Phase 6 established that execution may be reported complete when nothing executed, via three of seven measured lock states. This section re-measures the guard, enumerates every reachable false-positive and false-negative completion state, and determines the minimum discriminating evidence.

### 5.1 The guard, re-measured — ten states, not seven

**[MEASURED]** **P7-5**. The guard's arithmetic (`register.sh:187-192`) reproduced verbatim under `bash -euo pipefail` in a scratch directory outside this repository, with the lock age computed at each invocation so no timing race can distort the boundary. The directory was removed before this document was written.

```bash
LOCK="$HERE/.register.lock"
if [ -f "$LOCK" ]; then
  if [ "$(( $(date +%s) - $(cat "$LOCK" 2>/dev/null || echo 0) ))" -lt 3600 ]; then
    echo "register.sh already running (lock $LOCK) — nested/concurrent call is a no-op."
    exit 0
  fi
fi
```

| State | Lock content | Exit | Transaction runs? | stderr | Reachability |
|---|---|---|---|---|---|
| **A** | absent | 0 | **YES** | clean | normal |
| **B** | age 0 s | **0** | **NO** | clean | a `SIGKILL`ed or crashed run — the `EXIT` trap does not fire on `SIGKILL` |
| **D** | age 3599 s | **0** | **NO** | clean | any killed run inside the last hour |
| **I** | age **exactly 3600 s** | 0 | **YES** | clean | the boundary is **strict `<`** — **new, unpinned by Phase 6** |
| **C** | age 3601 s | 0 | **YES** | clean | stale reclamation, as designed |
| **F** | age **negative** (future timestamp) | **0** | **NO** | clean | clock stepped backward — NTP correction, VM suspend/restore, manual set |
| **E** | **empty** | 0 | **YES** | `bash: <n> -  : syntax error: operand expected` | a kill between `>` truncating the file and `date` writing it |
| **G** | **non-numeric** (`corrupt`) | **1** | **NO** | `bash: corrupt: unbound variable` — **no `TRANSACTION INCOMPLETE`**, because the abort is at `:189` and `fail()` is not defined until `:201` | partial write, disk-full, filesystem corruption |
| **H** | **multi-line** | 0 | **YES** | `bash: <n> - 1 2 : syntax error in expression` | **new** — not producible by the script's own writer (`date +%s` is single-line); requires external tampering |
| **J** | present but **unreadable** | 0 | **YES** | clean | **new** — `cat … \|\| echo 0` substitutes epoch 0, whose age exceeds 3600, so an unreadable lock **never** no-ops. Permission change, or a directory in the lock's place |

```
LOCK STATES MEASURED ............................................. 10   (PHASE6 P6-6 found 7)
    exit 0 having run NOTHING ....................................  3   B, D, F
    exit 1 with NO governance message ............................  1   G
    proceed with an alarming stderr, then run a REAL transaction ..  2   E, H   (PHASE6 found E)
    proceed cleanly ..............................................  4   A, C, I, J
    NEW in this phase ............................................  3   H, I, J
```

**[MEASURED] Two properties of the no-op path that no phase has recorded.**

1. **It is sticky.** States B, D and F `exit 0` at `:191`, *before* `date +%s > "$LOCK"` at `:194` and before `trap cleanup EXIT` at `:196`. The lock is therefore **not refreshed and not removed**. Every subsequent invocation within 3600 s of the original timestamp no-ops identically. A single killed run makes the transaction, `V-12` and every retry a no-op for up to an hour.
2. **The blast radius is bounded, and measurably so.** **[MEASURED]** **P7-12**: the `--observe` branch returns at `:178`, **nine lines before** the guard, so the read-only plane is structurally immune. The only two live invocations of `register.sh` anywhere in the repository are `--observe` — `verify.sh:799` and `.github/workflows/ucos-registration-gate.yml:60`. `--guard` has **0** live call sites and becomes reachable only through `--install-hooks`, which `PHASE5` `G-10` already prohibits for the transition window. **U-C therefore threatens `V-7`, `V-12` and a hypothetical `--guard`, and nothing else that exists today.**

### 5.2 Reachable false-positive completion states

A **false-positive completion state** is a reachable terminal state whose *reported* completion status is COMPLETE and whose *actual* status is not.

| ID | State | Mechanism | Causes | New? |
|---|---|---|---|---|
| **FP-A** | `EV-23` satisfied by a re-run that never ran | **[MEASURED]** lock states B, D, F. `EV-23`'s condition is *"a second `register.sh` produces **zero** byte changes across the four guard directories"*, which a run that never happened satisfies trivially. `UK-1` item 5 is retired on nothing. | **3** | Phase 6 `T-1b` |
| **FP-B** | `EV-22` satisfied by an index state that is not the minted set | **[MEASURED]** §5.3. `UGA-INV-01 violations=0` is satisfied by removing objects from the index as readily as by minting identities for them, and `UK-2` item 1 compares a **count**, never a **set**. | **3** — `git restore --staged`, `git reset`, `git stash` | **NEW** |
| **FP-C** | Completion asserted with `UK-2` open | **[INFERRED]** `CD-30` (`PHASE6:§11.1`) omits `EV-22` from the definition, so `T-1f` — *"complete; surface not reached"*, unknowns **1** — satisfies `EXECUTION-COMPLETED`. Under `CD-28` (`PHASE5:§0.4`) the same state is **not** complete. | **1** — the definitional conflict itself | **NEW** |
| **FP-D** | `register.sh --guard` reports green without checking drift | **[MEASURED]** `exit 0` at `:191` precedes the `--guard` block at `:264`. A caller reading the **exit code** sees success; the `Guard PASSED` line is absent, but no caller checks for it. | **1** | **NEW — latent**: 0 live call sites (**P7-12**) |

```
REACHABLE FALSE-POSITIVE COMPLETION STATES .......................  4
    live today ....................................................  3   FP-A, FP-B, FP-C
    latent (0 live call sites) ....................................  1   FP-D
    distinct CAUSES across the four ...............................  8   3 + 3 + 1 + 1
    identified by PHASE6 ..........................................  1   FP-A
    NEW in this phase .............................................  3
    caused by a MEASUREMENT defect ................................  3   FP-A, FP-B, FP-D
    caused by a DEFINITIONAL defect ...............................  1   FP-C
```

### 5.3 FP-B, established — the sharpest measurement of this phase

**[MEASURED]** **P7-6**, `uga_engine.py gate`, read-only, run once against this repository:

```
[FAIL] UGA-INV-01  EVERY_OBJECT_HAS_UNIVERSAL_ID   violations=27  measured=6804
[FAIL] UGA-INV-10  EVERY_MUTATION_HAS_AUDIT_EVENT  violations=27  measured=5207
30 invariants · 2 blocking · GATE FAILED
```

**[MEASURED]** **P7-8**: `uga_engine._git_ls` (`:178-193`) is `git ls-files -z --cached` — the **index**, over **every** path, with **no extension filter and no exclusion list**. `measured=6804` equals `git ls-files --cached | wc -l` exactly.

**[MEASURED]** **P7-7**, computed in-process through `uga.build(mint=False)`:

```
ANONYMOUS COUNT ...................... 27
STAGED-NEW (git status ^A) COUNT ..... 27
anonymous set == staged-new set ...... True
anonymous \ staged ................... []
staged \ anonymous ................... []
```

**The two sets are equal, element for element.** Every one of the 27 anonymous objects is a file that is staged and uncommitted: `.github/workflows/omega-gate.yml`, `00-BOOK/tools/ledger_authority.py`, `00-MASTER/UCI-000001/uci-ratchet.json`, three `00-MASTER/UCOS-OMEGA-001/` artifacts, eight `engine/tests/universal_discovery/` files, thirteen `engine/universal_discovery/` modules, and `platform/tests/test_ledger_authority.py`.

**[INFERRED] Four consequences.**

1. **`UGA-INV-01` measures the developer's staging area, not the repository.** Today `violations = |{paths with A-status}|`. The equality is not a definition — the criterion is *"in `--cached` and absent from `ledger["by_object"]`"* — but it holds exactly, because every **committed** path already carries an identity. It will cease to hold the moment any of the 27 is committed without being minted, and it holds now.
2. **`UK-2` item 2 is satisfiable with zero mints, zero permits and zero runs.** `git restore --staged` over the 27 removes them from `--cached`; they become untracked and are no longer UGA objects; `violations` goes to 0 and the gate prints `GATE PASSED`. This is FP-B.
3. **The false positive is co-detected, and that is the only thing that contains it.** The same operation makes `ledger_authority.py` untracked, so `G-9` / `EV-10` fail, and makes the register untracked, so `G-8` / `EV-9` fail. **[INFERRED]** `UK-2` item 1 — *"the `by_object` allocation count equals the count measured at issuance"* — is the intended discriminator, and it is a **count**: a mint of 28 followed by unstaging 2 and staging 2 others leaves item 1 satisfied and item 2 satisfied over a **different set**. Nothing in the chain compares the sets.
4. **`EV-14`'s measurand is not a property of any commit.** `PHASE4:§I.2` says *"the number cannot be fixed in advance"*; the reason is stronger than Phase 4 gave. It is not a function of HEAD at all. **[MEASURED]** and a `git add` of **any file whatsoever** — no extension filter, no exclusion list — grows it, which invalidates permit B on **both** `manifest_digest` and `scope.max_allocations` (`PHASE6` H-7: the cap has zero slack). This is **U-D**.

**[MEASURED] The contrast with `UK-1`, which is stable.** **P7-3b**: all nine `by_path` gap files are **committed and clean** — `git cat-file -e HEAD:<f>` succeeds and `git status --porcelain -- <f>` is empty for every one. `by_path` eligibility additionally filters to **4** extensions and excludes **13** directory prefixes. So:

```
UK-1's population   9   a function of HEAD          STABLE under index operations
UK-2's population  27   a function of the INDEX     CHANGES on any `git add` of ANY file
```

### 5.4 Reachable false-negative completion states

A **false-negative completion state** is a reachable state whose reported status reads as failure or as "nothing happened" while the actual state is materially different.

| ID | State | Why it reads as failed | What is actually true | New? |
|---|---|---|---|---|
| **FN-A** | Lock state **G** | **[MEASURED]** exit 1 with a raw `bash: corrupt: unbound variable` and **no** `TRANSACTION INCOMPLETE` line — indistinguishable by exit code from a mid-transaction failure | The abort is at `:189`, before Phase 0. Tracked state untouched, no allocation, **no rollback needed** — but an operator following `GA-8` would run `R-A`, which on a clean tree is a no-op that nonetheless consumes the rollback authorization | Phase 6 `Y-2` |
| **FN-B** | Lock states **E** and **H** | **[MEASURED]** a bash arithmetic error on stderr, which reads as a hard failure | `set -e` does not fire — the failure is inside an `if` condition — and the script **proceeds to a genuine, complete, irreversible ten-phase transaction**. An operator who aborts and rolls back would be rolling back a successful transaction | Phase 6 found **E**; **H is new** |
| **FN-C** | `EV-21` / `V-9` returning `RC=3` | reads as a drift failure | **[MEASURED]** `PHASE5` **P5-2** — the used permit's own uncommitted write into the register is a second, independent drift source, created deliberately two steps earlier. The remedy is the staging act, not a diagnosis | carried |
| **FN-D** | `EV-22` reporting `UGA-INV-01 > 0` | reads as a failed mint | **[INFERRED]** Two disjoint causes now, not one. **(i)** `UK-2` answered **negatively** — the population did not clear in one mint (`PHASE6:§9.2`). **(ii)** **NEW**: a `git add` of any file between the mint and `V-11` introduced a fresh anonymous object, which is not an answer to `UK-2` at all. **The two are indistinguishable from the violation count alone** | (ii) is **NEW** |
| **FN-E** | A `head`-bound permit refused because `git` is unavailable | reads as an authorization defect | **[MEASURED]** `git_head` `:580-598` returns `None` on `OSError` / timeout / non-zero; `:753-757` refuses *"rather than assuming a match"*. An **environmental** failure produced a **governance** refusal, with the ledger untouched | Phase 6 `§4.4` case 3 |
| **FN-F** | A post-writer refusal (`commit()` refusals 5–8) | reads as "nothing happened" — the ledger is byte-identical | **[MEASURED]** `PHASE1:§R-7` verified byte-identity on all five divergence tests. But `R-7w`'s window `:893`→`:921` **was traversed**, which is the one residual a successful run never exercises. The state under-reports **residual exercise**, not completion | **NEW as a false-negative class** |

```
REACHABLE FALSE-NEGATIVE COMPLETION STATES .......................  6
    identified by PHASE6 ..........................................  3   FN-A, FN-B(E only), FN-E
    carried from PHASE5 ...........................................  1   FN-C
    NEW or newly extended in this phase ...........................  3   FN-B(H), FN-D(ii), FN-F
    in which the repository is IRREVERSIBLY MUTATED while the
    operator is being told it failed ..............................  1   FN-B — the dangerous one
```

### 5.5 Minimum evidence required to distinguish

**[INFERRED]** Per false-positive class, the smallest set of observations that separates the true state from the false one.

| Class | Discriminating evidence | Count |
|---|---|---|
| **FP-A** | (i) the exact `TRANSACTION COMPLETE …` line from the re-run · (ii) the **absence** of `nested/concurrent call is a no-op` · (iii) `00-BOOK/tools/.register.lock` verified **absent** immediately before the re-run · (iv) the re-run's own `commit()` report showing `authorization` and `bytes_changed=False` | **4** |
| **FP-B** | (v) the minted **set** — `report["allocated"]["by_object"] ∪ ["by_observation"]` — compared against the anonymous **set** measured at `EV-14`, not the counts · (vi) index identity held constant across issuance → run B → `V-11`, verified by a tree-hash of `git ls-files --cached` at each point | **2** |
| **FP-C** | (vii) one definitional act fixing `CD-28` against `CD-30` — **not evidence; a determination** | **1** |
| **FP-D** | (viii) the `Guard PASSED …` line, rather than the exit code, as the guard's success condition | **1** |

```
MINIMUM DISCRIMINATING EVIDENCE ITEMS ............................  8
    already named by PHASE6 (as EV-23 additions + UK-1 item 6) ....  4   (i)-(iv)
    NEW in this phase .............................................  3   (v), (vi), (viii)
    not evidence at all — a determination .........................  1   (vii)
```

### 5.6 Redundant and non-discriminating evidence

**Redundant** — removable with no effect on any conclusion:

```
REDUNDANT EVIDENCE ITEMS .........................................  0
    [MEASURED] PHASE6 §5.4 classified all 21 pre-run items as EI / RI / EL with
    ZERO in the NE class.  Extended here to EV-22 … EV-27: each has a named
    consumer and a named condition that fails without it.  Confirmed, not corrected.

    One near-miss, checked and REJECTED: EV-19 (post-run ledger `sha256`) versus
    EV-16 (pre-image digest re-measured at B's issuance).  These are NOT the same
    quantity and neither is derivable from the other — EV-19 is sha256 over the
    FILE BYTES, EV-16 is sha256 over `_canonical(before)`, the sorted-key
    separator-normalized DOCUMENT (`:534-542`, `:570-577`).  [MEASURED] the two
    differ in length by 488 344 bytes over the live ledger (P7-13 / PHASE6 P6-5:
    canonical 1 790 825 vs file 2 279 169).  Both are required.
```

**Non-discriminating** — satisfied by a state they do not measure:

| Item | What it cannot distinguish | Basis |
|---|---|---|
| **EV-1**, **EV-24** | *"≥ 77 passed"* is a **count**, not a set. Removing a Phase-1 test and adding a new one keeps the count at 77 | **[INFERRED]** `PHASE5` `EV-1`'s stated purpose is *"a count below 77 means a Phase-1 test was removed"* — true, and it does not detect removal-plus-addition. This is **U-G** |
| **EV-2**, **EV-21** | `RC=0` accepts a **staged** register; `--guard` rejects it | **[MEASURED]** `PHASE5` **P5-1**: `A ` → `--observe` PASS / `--guard` DRIFT. `EV-21` can hold while the end-of-program `--guard` requirement cannot be met |
| **EV-5** | The permit **mechanism** works ≠ **permit A** is well-formed | **[MEASURED]** `_issue` writes to `permit_register_path(path)` for a **temp** ledger; the round trip never touches the production register |
| **EV-14** | Equal **counts** over **different sets** | **[MEASURED]** §5.3 |
| **EV-22** | A mint from an index-clearing operation | **[MEASURED]** §5.3 |
| **EV-23** | A byte-neutral re-run from a re-run that never happened | **[MEASURED]** §5.1 |

```
NON-DISCRIMINATING EVIDENCE ITEMS ................................  7
    across DEFECT CLASSES .........................................  5
        count-not-set ......................... EV-1, EV-24, EV-14  (3 items, 2 classes)
        staged-not-committed .................. EV-2, EV-21         (2 items, 1 class)
        temp-scope-not-production ............. EV-5                (1 item)
        index-not-mint ........................ EV-22               (1 item)
        no-op-not-neutral ..................... EV-23               (1 item)

TAUTOLOGICAL EVIDENCE ITEMS ......................................  1   EV-23, on the no-op path
    A run that did not happen changes no bytes.  The condition is true of the
    state it is meant to exclude, which is the definition of tautological.
```

### 5.6b Closure classes for U-C — enumerated, not chosen

**[INFERRED]** U-C is a *measurement* defect, not an authorization one, so its closure space is generated by asking what would make each false-positive channel unreachable or detectable. Six classes exhaust it.

| ID | Mechanism | Closes | Cost / consequence |
|---|---|---|---|
| **CC-1** | **Strengthen `EV-23`'s success condition** to the four discriminators of §5.5 (i)–(iv) | **FP-A** | No code. Amends `GA-6`'s adopted closure set, which is a documentary act on an artifact that does not yet exist. Exactly `PHASE6:§6.6`'s `[EXEC-REQ]` plus `UK-1` item 6 |
| **CC-2** | **Give the guard a third exit value** — distinguish *"did not run"* from *"ran and completed"* and from *"ran and failed"* | **FP-A, FP-D**, and **FN-A** | Touches `register.sh:187-195`. **[MEASURED]** the repository already has this vocabulary twice: `engine/certification_integrity/gate.py:4-5` and `.github/workflows/omega-gate.yml:30-31` both use `0 / 1 / 2 FAULT`. `CD-19` (REG-AUTO-001 §7) would need the matching third value, which is `U-F` |
| **CC-3** | **Make the lock a precondition rather than a short-circuit** — verify `.register.lock` absent before the run and refuse if present, instead of exiting 0 | **FP-A, FP-D** | Changes the script's concurrency contract: a genuine nested invocation becomes an error rather than a no-op, which is what the lock exists to prevent (`:181-186`). Trades one hazard for another; both are stated |
| **CC-4** | **Compare minted SETS, not counts** — carry `report["allocated"]` through `EV-22`'s evaluation and require set equality with `EV-14`'s anonymous set | **FP-B**, and **FN-D(ii)** | No code in the authority — `commit()` already returns the set (`:398-402`). It is an evidence-definition change in `GA-6` and `EV-22` |
| **CC-5** | **Freeze the index across `S-3` → `S-9`** — a tree-hash of `git ls-files --cached` recorded at `EV-3`/`EV-12` and re-verified before each run and before `V-11` | **FP-B, FN-D(ii)**, and — jointly with `CB-4` — **U-B's M3** | No code. Adds one gate condition and one read-only check. **[MEASURED]** computable today: `git ls-files --cached` is the exact boundary both engines use (`ukb.py:786`, `uga_engine.py:188`) |
| **CC-6** | **Adjudicate `CD-28` against `CD-30`** — fix one definition of the terminal state | **FP-C** | Not evidence and not code: a determination. **[INFERRED]** It is governance-independent — it touches no axis — but it is not closable by measurement either, because both readings are internally consistent and the chain simply asserts both |

```
CLOSURE CLASSES FOR U-C ..........................................  6   CC-1 … CC-6
    closing FP-A .................................................  3   CC-1, CC-2, CC-3
    closing FP-B .................................................  2   CC-4, CC-5
    closing FP-C .................................................  1   CC-6
    closing FP-D .................................................  2   CC-2, CC-3
    additionally closing a FALSE NEGATIVE ........................  3   CC-2 (FN-A),
                                                                        CC-4 / CC-5 (FN-D ii)
    requiring NO code change .....................................  4   CC-1, CC-4, CC-5, CC-6
    requiring a change to register.sh ............................  2   CC-2, CC-3
    GOVERNANCE-INDEPENDENT ....................................... 6 of 6
        [INFERRED] no axis value changes any cell above — unlike U-B, U-C is
        entirely governance-independent, which is the sharpest asymmetry
        between the two defects.
    RECOMMENDED ..................................................  0
```

### 5.7 Q3 verdict

```
REACHABLE FALSE-POSITIVE COMPLETION STATES .......................  4   (PHASE6: 1)
REACHABLE FALSE-NEGATIVE COMPLETION STATES .......................  6   (PHASE6: 2)
DISTINCT CAUSES ACROSS THE FALSE POSITIVES .......................  8
LOCK STATES MEASURED ............................................. 10   (PHASE6 P6-6: 7)
MINIMUM DISCRIMINATING EVIDENCE ITEMS ............................  8
REDUNDANT EVIDENCE ITEMS .........................................  0
NON-DISCRIMINATING EVIDENCE ITEMS ................................  7   in 5 defect classes
TAUTOLOGICAL EVIDENCE ITEMS ......................................  1

  U-C IS BROADER THAN PHASE6 STATES AND NARROWER IN BLAST RADIUS.
  Broader: the false-positive channel is not one mechanism but four, and only
  one of them is the lock.  Narrower: the lock channel cannot reach the two
  live invocations of register.sh, because --observe returns nine lines before
  the guard.  [MEASURED] P7-12.
```

---

## 6. Evidence-soundness matrix — Q4

### 6.0 The seven attributes, defined before they are applied

| Attribute | Question |
|---|---|
| **produced?** | Does a named producer exist that can actually emit it? |
| **consumed?** | Does a named consumer read it, mechanically or as a stated condition? |
| **machine-verifiable?** | Can a program decide whether it holds? |
| **forgeable?** | Can it be made to read as passing without the underlying fact being true? |
| **replayable?** | Can a stale copy pass a later check — i.e. is it bound to the state it describes? |
| **ambiguous?** | Does its wording admit two non-equivalent readings? |
| **model-dependent?** | Does an axis value change its content or its producibility? |

**Classification.** **SAFE** — produced, consumed, machine-verifiable, state-bound, unambiguous. **UNSAFE** — forgeable or replayable in a way that matters. **UNPROVEN** — no producer exists, or the producer is unnamed. **TAUTOLOGICAL** — true of the state it is meant to exclude. **NON-DISCRIMINATING** — satisfied by a state it does not measure.

### 6.1 Pre-run evidence, `EV-1 … EV-21`

| ID | prod | cons | m/v | forge | replay | ambig | model | **Class** | Decisive basis |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|---|---|
| **EV-1** | yes* | yes | yes | **YES** | **YES** | no | no | **NON-DISCRIMINATING** | *only with the `PHASE05:§E.0` invocation (`PHASE6` H-11). A count, not a set — **U-G** |
| **EV-2** | yes | yes | yes | no | **YES** | **YES** | no | **NON-DISCRIMINATING** | `RC=0` accepts staged; `--guard` does not (`P5-1`) |
| **EV-3** | yes | yes | yes | no | **no** | no | no | **SAFE** | digest-bound to the pre-image (`:735`, `:743`) |
| **EV-4** | yes | yes | yes | no | **YES** | no | no | **UNPROVEN** | *"a property of the present working tree, not a guarantee"* (`PHASE4:§F.2`); nothing holds it |
| **EV-5** | yes | **no** | yes | — | yes | no | no | **NON-DISCRIMINATING** | `_issue` writes a **temp** register; says nothing about permit A |
| **EV-6** | yes | yes | yes | no | no | no | no | **SAFE** | a hash of a live file at an instant |
| **EV-7** | yes | yes | yes | **YES** | **YES** | no | no | **UNSAFE** | **[MEASURED]** `.runtime/` is gitignored (`:12`), unsigned, per-clone, and freely editable. **The only evidence that survives `R-A` is the only evidence with no integrity binding of any kind** |
| **EV-8** | yes | yes | **no** | — | — | no | no | **UNPROVEN** | a designation, not a measurement. `PHASE6:§4.3` — `G-13` is among the 12 unenforceable conditions |
| **EV-9** | yes | yes | yes | no | no | no | no | **SAFE** | `git status --porcelain` is decidable |
| **EV-10** | yes | yes | yes | no | no | no | no | **SAFE** | `git cat-file -e HEAD:<path>` is decidable |
| **EV-11** | **no**† | yes | yes | **partly** | no | no | no‡ | **UNPROVEN** | †unconstructible until `IA-3` **and** `IA-12` exist. Forgeable in the **5 elective** bindings: omit `scope` and the authority enforces no bound (`PHASE6` H-4). ‡the requirement is model-invariant; the **field set** is `IA-12`-dependent |
| **EV-12** | yes | yes | yes | no | no | no | no | **SAFE** | as `EV-3` |
| **EV-13** | yes | yes | yes | no | **YES** | no | **YES** | **UNPROVEN** | **[MEASURED]** `P7-6`: the baseline is index-derived (`measured=6804` = `git ls-files --cached`), and the index moves. Model-dependent via `Aud3` → surface 29 |
| **EV-14** | yes | yes | yes | no | no | no | no | **NON-DISCRIMINATING** | **[MEASURED]** §5.3 — a **count** over a set nothing compares |
| **EV-15** | **no** | yes | yes | partly | no | no | no | **UNPROVEN** | as `EV-11` |
| **EV-16** | yes | yes | yes | no | no | no | no | **SAFE** | `preimage_digest` over `_canonical(before)` (`:570-577`) |
| **EV-17** | yes | yes | partly | **YES** | **YES** | no | no | **UNSAFE** | a transcript is a text file. **[INFERRED]** nothing binds it to a run: no digest, no timestamp the authority signs, no sequence. `UK-1` items 2–3 rest on it |
| **EV-18** | yes | yes | yes | **YES** | **YES** | no | no | **UNSAFE** | as `EV-17`, and **[MEASURED]** unrecoverable after `R-A` (`PHASE4:§E.3`) |
| **EV-19** | yes | yes | yes | no | no | no | no | **SAFE** | sha256 over file bytes; distinct from `EV-16` (§5.6) |
| **EV-20** | yes | yes | yes | no | no | no | no | **SAFE** | index state is decidable |
| **EV-21** | yes | yes | yes | no | **YES** | **YES** | no | **NON-DISCRIMINATING** | as `EV-2` |

### 6.2 Post-run evidence, `EV-22 … EV-27`

| ID | prod | cons | m/v | forge | replay | ambig | model | **Class** | Decisive basis |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|---|---|
| **EV-22** | yes | yes | yes | **YES** | no | no | **YES** | **NON-DISCRIMINATING** | **[MEASURED]** §5.3 — forgeable by an index operation. Model-dependent: surface **30** (`Aud1`/`Aud2`) or **29** (`Aud3`) |
| **EV-23** | **NO** | yes | yes | **YES** | — | **YES** | **YES** | **TAUTOLOGICAL** | **[MEASURED]** §4.2 — unproducible in M2 and M3; §5.1 — trivially true on the no-op path; **ambiguous** between a before/after byte **delta** and `git status` **emptiness**; model-dependent via axis `D` |
| **EV-24** | yes* | yes | yes | **YES** | **YES** | no | no | **NON-DISCRIMINATING** | as `EV-1` |
| **EV-25** | **NO** | yes | **no** | — | — | no | no | **UNPROVEN** | **[MEASURED]** **P7-11**: `ledger_authority.py` contains **ZERO** `print`, `logging` or `logger` statements. Nothing anywhere emits *"the lock was taken"*, *"the pre-write re-check ran"* or *"the document comparison ran"*. **The producer does not exist and no artifact names one** |
| **EV-26** | yes | yes | yes | **YES** | **YES** | no | no | **UNSAFE** | as `EV-7` |
| **EV-27** | yes | yes | yes | no | no | no | no | **SAFE** | as `EV-19` |

### 6.3 `EV-25` — the third unproducible item, and the one no phase has named

**[MEASURED]** **P7-11**: `grep -n "print(\|logging\|logger" 00-BOOK/tools/ledger_authority.py` returns **nothing**. The module is silent by construction — a deliberate property, since it is a library the callers report from, and `format_report` (`:437-478`) is the single line any caller prints. That line reports **allocation**: `actor`, `total_allocations`, `allocated`, `counter_advances`, `cursor_advances`, `unmeasured_maps`, `bytes_changed`. It reports **no control activation**.

**[INFERRED]** `EV-25` requires *"evidence that on a real write: the lock was taken (`_ledger_lock`), the pre-write byte re-check ran (R-2), and the post-write document comparison ran (R-7, `:920`) without firing a refusal."* All three run — `commit()`'s control flow guarantees it — and **none of the three leaves any trace an observer can read.** A successful `commit()` and a `commit()` in which all three controls were removed produce **byte-identical operator output**.

**[INFERRED]** So `EV-25` is unproducible **at all**, not merely by its named method. It joins `EV-1` (unproducible by the command Phase 4 names) and `EV-23` (unproducible in 2 of 3 classes). Phase 6 counted **2**; the count is **3**. And `EV-25` is the one that matters for `GA-5`, because `RES-3` and `RES-4` are *"REDUCED"* by execution (`PHASE4:§G`) only on evidence that the controls fired — which no run can supply.

### 6.4 Q4 aggregate

```
EVIDENCE ITEMS CLASSIFIED ........................................ 27   EV-1 … EV-27

  SAFE ...........................................................  9
      EV-3, EV-6, EV-9, EV-10, EV-12, EV-16, EV-19, EV-20, EV-27
      common property: every one is a DIGEST or an INDEX/HEAD predicate —
      state-bound, machine-decidable, and not restatable as text

  UNSAFE .........................................................  4
      EV-7, EV-17, EV-18, EV-26
      common property: every one is a TRANSCRIPT or a GITIGNORED LOG —
      forgeable and replayable, with no binding to the run it describes.
      [INFERRED] EV-7 and EV-26 are the ONLY evidence that survives a full
      tracked rollback (PHASE4 §F.3), and they are in this class.

  UNPROVEN .......................................................  6
      EV-4, EV-8, EV-11, EV-13, EV-15, EV-25
      of which NO PRODUCER EXISTS ANYWHERE ......................  1   EV-25
      of which the producer is an artifact not yet written ......  2   EV-11, EV-15 (need IA-3+IA-12)
      of which the measurand is not a property of any commit ....  1   EV-13
      of which it is a decision, not a measurement ..............  1   EV-8
      of which it is an instant, not a guarantee ................  1   EV-4

  TAUTOLOGICAL ...................................................  1   EV-23

  NON-DISCRIMINATING .............................................  7
      EV-1, EV-2, EV-5, EV-14, EV-21, EV-22, EV-24

  arithmetic check ....... 9 + 4 + 6 + 1 + 7 = 27                  ✓

UNPRODUCIBLE EVIDENCE ITEMS ......................................  3   (PHASE6: 2)
    EV-1   not producible by the command PHASE4 V-1 names       PHASE6 H-11
    EV-23  not producible in manifest classes M2 and M3         §4.2, this phase
    EV-25  not producible AT ALL — no producer exists           §6.3, NEW

ITEMS WHOSE CLASS DEPENDS ON AN AXIS VALUE .......................  3   EV-13, EV-22, EV-23
ITEMS THAT ARE SOUND WITHOUT QUALIFICATION .......................  9   the SAFE set
FRACTION OF THE EVIDENCE BASE THAT IS SAFE ....................... 33%
```

**[INFERRED] The structural reading.** The evidence base splits cleanly on one property: **items that are digests or version-control predicates are sound; items that are text are not.** Every SAFE item is a hash or a `git` predicate. Every UNSAFE item is a transcript or a gitignored log. The chain's most load-bearing narrative evidence — `EV-17`, the terminal transcript on which `UK-1` items 2 and 3 rest — is in the second class, and nothing in the package binds it to the run it purports to describe.

---

## 7. Authorization-accounting analysis — Q5

### 7.0 The six dimensions and the verdict vocabulary

| Dimension | Question the accounting must answer |
|---|---|
| **Issuance** | Who wrote this permit, with what fields, and can that be established afterwards? |
| **Consumption** | Has this permit been used, and is that determinable? |
| **Invalidation** | Is this permit still valid, and what invalidated it? |
| **Expiry** | Does it expire, and by what clock? |
| **Mismatch** | Which of its bindings are actually enforced? |
| **Replay** | Can it authorize a second write, and after a rollback? |

**COMPLETE** — every event is recorded or derivable, in every case. **PARTIAL** — recorded for some cases, not others. **AMBIGUOUS** — two admissible readings give different answers. **UNDEFINED** — the mechanism has no answer at all.

### 7.1 The measured substrate, common to all 12 models

| Fact | Basis |
|---|---|
| The register's only writer today is a **test helper**; `IA-3`/`F-1` — the producer — does not exist | **[MEASURED]** `P7-1` (register absent); `platform/tests/test_ledger_authority.py:63-90` |
| `_verify_permit` reads **9** fields: **4 strict** (`permit_id`, `actor`, `manifest_digest`, `preimage_digest`), **5 elective** (`head`, `scope`, `scope.maps`, `scope.max_allocations`, `expires_at`) | **[MEASURED]** `:709-804`; `PHASE6` **P6-1**, re-verified |
| No `issuer`, `signature`, `issued_at`, `revoked`, `uses` or `single_use` is read | **[MEASURED]** `P7-11` — `single_use` occurs **0** times in `ledger_authority.py`; `issued_at` appears only in a docstring at `:551` |
| `preimage_digest` covers the **whole** pre-image document, so **any** ledger write — allocating or not — invalidates **every** outstanding permit | **[MEASURED]** `:570-577`, `:743-749` |
| `manifest_digest` covers `actor`, so the actor is bound **twice**: strictly at `:728` and again inside the digest at `:558` | **[MEASURED]** `P7-11` — defence in depth, unrecorded by any prior phase |
| `expires_at` is **read** at `:785-797` and has **no producer anywhere in the repository** | **[MEASURED]** `PHASE2` **P2-6**; `_issue` writes `expires_at: None`, and `if expires_at:` skips a falsy value, so the binding is never exercised by the only writer |
| **The `NO_ALLOCATION` path performs NO actor check, holds no `permit_id`, and touches no register** | **[MEASURED]** `:684-707` returns `None` before any actor comparison; `commit :878-879` then sets `permit_id = None`, `authorization = "NO_ALLOCATION"` |
| A reused `permit_id` is **permanently** unusable and no rollback repairs it | **[MEASURED]** `:718-723`; `PHASE6` H-13 |
| **4** distinct production actor literals exist across **5** call sites | **[MEASURED]** `P7-11`: `ukb.py:1287`, `:2382`, `:2403`, `uga_engine.py:2079`/`:2098` |

### 7.2 The per-dimension, per-model matrix

Axes `I = I-R` and `A = A3` are fixed across all 12 (`PHASE3:§A`), so only `B`, `D` and `Aud` can differentiate. **[INFERRED]** `D` and `Aud` differentiate **no** cell below — the accounting reads the permit register and the sentinel, neither of which any `D` or `Aud` value touches. Only `B` differentiates, and only in one dimension.

| Dimension | `B1` — `Z-01 … Z-06` (6 models) | `B2` — `Z-07 … Z-12` (6 models) | Why |
|---|---|---|---|
| **Issuance** | **PARTIAL** | **PARTIAL** | **[MEASURED]** The producer is forced (`F-1`, all 12) but its **field elections are unrecorded** — `IA-12` does not exist. **5 of 9** bindings are elective, so two conforming issuers can produce permits that enforce different bounds. And **[MEASURED]** `M1`/`P2-6`: no `issuer` field is read, so *who* issued is unrecoverable **by design** — a merge Phase 2 proved, not a defect |
| **Consumption** | **COMPLETE** | **PARTIAL** | `B1`: consumption is **derived**, not recorded — `preimage_digest` moves when the write lands, and *"spent-ness is DERIVED from two artifacts that are already committed"* (`:570-577`). Nothing needs to be written, so nothing can be missing. `B2`: a use record is required (`O-3`, `ledger_authority.py:870-933`), **and `O-3` does not exist yet**; meanwhile `single_use: True` is written by the only writer and read by nothing — **[MEASURED]** a false affordance (`PHASE6:§3.7`, `E1-F3`) |
| **Invalidation** | **COMPLETE** | **COMPLETE** | **[MEASURED]** `:743-749` refuses on pre-image mismatch, and the pre-image covers the whole document. Every invalidation event is derivable from two committed artifacts. **[MEASURED]** `PHASE4` **P4-7** measured the movement `3a2a2532…` → `0b7a886d…`. This is the one dimension that is complete in every model, and it is complete because it is **derived rather than recorded** |
| **Expiry** | **AMBIGUOUS** | **AMBIGUOUS** | **[MEASURED]** modifier `T` is **free in all 12** (`PHASE3:§A`). Under `T-state` expiry is state-bound and ≡ *"never expires"* (`PHASE2` **M3**) ⇒ accounting is complete. Under `T-instant` a clock authority is required and **`expires_at` has no producer** ⇒ accounting is undefined. **Both readings are admissible in every one of the 12 models**, and `GA-2` is the artifact that would settle it. Until then the answer to *"does this permit expire?"* has two admissible values |
| **Mismatch** | **PARTIAL** | **PARTIAL** | **[MEASURED]** 4 of 9 bindings are unconditionally enforced; **5 are enforced only if the issuer emits them**. **[MEASURED]** `PHASE5:§B.7`'s claim that `GA-7`'s scope bound *"is enforced by the authority itself, not merely by policy"* is conditional on `isinstance(scope, dict)` (`PHASE6` H-4). So *"which bounds were enforced on this write?"* is answerable only by reading the permit, and the permit's shape is unrecorded |
| **Replay** | **PARTIAL** | **PARTIAL** | Defined for **permits** once `GA-9` records the axis-`B` consequence: under `B1` a restored pre-image **re-validates** the used permit (**[MEASURED]** `PHASE2` **P2-1**: replay ACCEPTED after a byte restore) and a retry needs none; under `B2` the permit stays spent while the allocation is undone. **UNDEFINED for the sentinel** — §7.6 |

```
CELLS ............................. 6 dimensions × 12 models = 72

  COMPLETE ....................... 18     invalidation ×12  ·  consumption ×6 (B1)
  PARTIAL ........................ 42     issuance ×12 · consumption ×6 (B2)
                                          · mismatch ×12 · replay ×12
  AMBIGUOUS ...................... 12     expiry ×12
  UNDEFINED ......................  0

  arithmetic check .... 18 + 42 + 12 + 0 = 72                     ✓

MODELS REACHING COMPLETE ACCOUNTING ON ALL SIX DIMENSIONS ........  0 of 12
MODELS REACHING COMPLETE ON >=2 DIMENSIONS .......................  6 of 12   (B1: invalidation
                                                                              + consumption)
MODELS REACHING COMPLETE ON EXACTLY 1 DIMENSION ..................  6 of 12   (B2: invalidation)

DIMENSIONS COMPLETE IN EVERY MODEL ...............................  1   invalidation
DIMENSIONS AMBIGUOUS IN EVERY MODEL ..............................  1   expiry
DIMENSIONS THAT AXIS B DIFFERENTIATES ............................  1   consumption
DIMENSIONS THAT AXES D OR Aud DIFFERENTIATE ......................  0
```

### 7.3 The counter-intuitive result, stated because it is load-bearing

**[INFERRED]** `B1` — the *reusable* permit model, the one that records nothing — has **strictly better** authorization accounting than `B2`, the model built to record consumption. The reason is measured: under `B1` consumption is **derived** from two already-committed artifacts (the ledger and the register), so there is no record that can be missing, stale or wrong. Under `B2` consumption is **asserted** by a record that `O-3` has not yet been written to produce, and the field that would carry it (`single_use`) is already present and already dead.

**[INFERRED]** This is not an argument for `B1` and is not offered as one — constraint 9 forbids it, and the two models differ on `E1-F3`'s closure quality, which this dimension does not speak to. It is stated because a reader who assumes "the model that records more accounts better" would mis-read §7.2, and because it identifies exactly where `B2`'s accounting becomes complete: **at `O-3`, and not before.**

### 7.4 What `GA-2`'s deferral costs, quantified

**[INFERRED]** Expiry is the only dimension AMBIGUOUS in all 12 models, and it is ambiguous for one reason: modifier `T` is unanswered. `PHASE2:§E.1` classifies `T` among the **8 closure-redundant** decisions — correctly, since neither value opens or closes a blocker. **[INFERRED]** But `PHASE5:§B.2` already found that **two** of the eight redundant decisions change the transition package anyway (`B2a`/`B2b` → `R-B`'s scope; `R` → `GA-3`). **`T` is a third**: it does not change a closure cell and it does decide whether the authorization accounting is complete or undefined on one of its six dimensions.

```
CLOSURE-REDUNDANT DECISIONS THAT NONETHELESS CHANGE THE PACKAGE ...  3
    B2a / B2b   -> R-B's rollback scope                    PHASE5 §B.2
    R           -> GA-3's attestation                      PHASE5 §B.2
    T           -> expiry accounting COMPLETE or UNDEFINED  THIS PHASE
```

### 7.5 The unaccountable authorization events

**[MEASURED]** Three classes of ledger write reach `commit()` and produce **no** accountable authorization record.

| # | Class | Why unaccountable |
|---|---|---|
| **1** | Every `NO_ALLOCATION` write | No `permit_id`, no register entry, **no actor check**. `report["permit_id"] = None`. The write is recorded in the ledger's own append-only history only insofar as it changed the ledger — and by construction it changed nothing |
| **2** | **Under closure `CB-1`, the program's third authorization event** — the re-run in class M1 | It is a `NO_ALLOCATION` write, so class 1 applies. **[INFERRED]** `PHASE5:§J.4` counts **2** machine-checkable approvals; `PHASE6:§10.4` revises that to *"2 or 3"*; this phase adds that **the third, under `CB-1`, is not machine-checkable in the accounting sense at all** — it is verified, and it is not recorded |
| **3** | A permit whose `permit_id` has been poisoned by reuse | **[MEASURED]** `:718-723` — *"an ambiguous authorization is no authorization"*. **[INFERRED]** and no rollback repairs it: `R-D` restores or discards the register wholesale and cannot de-duplicate an id that legitimate append-only issuance created twice |

### 7.6 `U-H`, stated exactly

> **`U-H`.** The sentinel authorization path (`ledger_authority.py:684-707`) performs **no actor binding**, allocates **no `permit_id`**, and writes **no register entry**. It is therefore issuance-less, consumption-less, unattributable and unrecorded. This is correct and deliberate for its designed use — `ukb.py exec declare`'s idempotent re-declaration, where the docstring records that the claim is correct *"BY CONSTRUCTION, not by assumption"*. It becomes an accounting gap **only** when a closure routes a *program* authorization event through it, which is exactly what `CB-1` does for the re-run. **[INFERRED]** The gap is therefore created by the closure, not by the authority, and it is closable by determination: the accounting requirement is that the re-run's `commit()` report be captured (`UK-1` item 6 already requires this), not that the sentinel be changed.

### 7.7 Q5 verdict

```
IS AUTHORIZATION ACCOUNTING COMPLETE FOR ANY ADMISSIBLE MODEL?         NO

  COMPLETE   ...  0 of 12 models
  PARTIAL    ... 12 of 12 models on at least 3 dimensions
  AMBIGUOUS  ... 12 of 12 models on expiry, because modifier T is free
  UNDEFINED  ...  0 of 12 as a whole-model verdict;
                  1 SUB-CASE undefined in all 12 — replay of the SENTINEL (U-H)

  THE ONE DIMENSION COMPLETE EVERYWHERE IS THE ONE THAT RECORDS NOTHING.
  Invalidation is complete in 12 of 12 because it is DERIVED from two committed
  artifacts.  Every dimension that depends on something being WRITTEN — issuance
  fields, consumption records, enforced-binding sets — is PARTIAL, and the
  artifact that would complete them (IA-12, and O-3 under B2) does not exist.
```

---

## 8. Terminal-state equivalence analysis — Q6

### 8.1 What each name refers to, before anything is compared

**[MEASURED]** **P7-9**, counted across all eight input documents and across `00-BOOK/tools`, `00-MASTER/UCOS-UGA-001`, `engine/` and `platform/`:

| Name | Occurrences in the 8 inputs | Occurrences in the source | Definitional status |
|---|---:|---:|---|
| `EXECUTION-AUTHORIZED` | **36** | 0 | **Defined**, twice consistently: `PHASE5:§0.4` and `§G.2` — `G-1 ∧ … ∧ G-13 ∧ G-14(R)`, per-run |
| `EXECUTION-COMPLETE` | **14** | 0 | **Defined** — `PHASE5:§0.4`: *"Both runs landed and both unknowns retired."* (`CD-28`) |
| `EXECUTION-COMPLETED` | **11** | 0 | **Defined differently** — `PHASE6:§11.1`: `A✓ ∧ B✓ ∧ EV-23 ∧ EV-24 ∧ EV-25` (`CD-30`) |
| `EXECUTION-SUCCESSFUL` | **0** | **0** | **No referent anywhere.** Constructed in §8.2 |
| `EXECUTION-VERIFIED` | **0** | **0** | **No referent anywhere.** Constructed in §8.2 |
| `EXECUTION-CERTIFIED` | **5** | 0 | **Undefined** — all five occurrences are `PHASE6` recording that it is undefined |

**[INFERRED]** So of the five states the question compares, **one is defined (`EXECUTION-AUTHORIZED`), one has two incompatible definitions, two have no definition, and one is expressly undefined.** An equivalence question over that set is not answerable without construction, and the constructions must be labelled as such so that no result rests on a definition this phase invented.

### 8.2 The constructions, stated and labelled

**[CONSTRUCTED, this phase]** Chosen to be the weakest reading under which each name is non-vacuous and the five form a chain. Each is stated so a reader can reject it and re-derive §8.3 under another.

| Name | Constructed definition | Why this reading |
|---|---|---|
| **`EXECUTION-SUCCESSFUL`** | `A✓ ∧ B✓` — both mutating runs landed and sealed, with no reference to confirmation | It is the only reading under which the name adds something to `EXECUTION-AUTHORIZED` and is weaker than `EXECUTION-COMPLETED`. Corresponds exactly to `PHASE4:§H.2` row `T-1` before Phase 6 split it |
| **`EXECUTION-VERIFIED`** | `EXECUTION-SUCCESSFUL ∧ EV-22 ∧ EV-23 ∧ EV-24 ∧ EV-25`, **each genuinely rather than falsely satisfied** | It is the only reading that distinguishes verification from completion. The distinction is not idle: §5.2 establishes **4** channels on which a confirmation item passes falsely |
| **`EXECUTION-CERTIFIED(a)`** | gate-greenness: `register.sh --guard` returns 0 **and** `uga_engine gate` reaches the model's target surface | `PHASE6:§11.1` candidate (a) |
| **`EXECUTION-CERTIFIED(b)`** | residual-freedom: `RES-3`, `RES-4` and `R-7w` all closed | `PHASE6:§11.1` candidate (b) |

### 8.3 The implication chain, and its six failures

**[INFERRED]** The five names form a chain of one-way implications. Every implication holds; **every converse fails, and each failure has a measured witness.**

```
  EXECUTION-CERTIFIED(a)  ⇒  EXECUTION-VERIFIED  ⇒  EXECUTION-COMPLETED
                                                 ⇒  EXECUTION-SUCCESSFUL
                                                 ⇒  was EXECUTION-AUTHORIZED

  EXECUTION-CERTIFIED(b)  ⇒  ∅        [MEASURED] the set is EMPTY — §8.4
```

| # | Non-implication | Separating condition | Witness | Basis |
|---|---|---|---|---|
| **S-1** | `AUTHORIZED ⇏ SUCCESSFUL` | any run outcome other than `A✓ ∧ B✓` | **`A∅`** — the lock no-op. Fully authorized, exits **0**, and no phase ran | **[MEASURED]** §5.1 states B, D, F |
| **S-2** | `SUCCESSFUL ⇏ COMPLETED` | `EV-23`, `EV-24` or `EV-25` fails | **`T-1c`** — both runs land, `V-12` genuinely fails, so the drift gate can never be green | **[MEASURED]** `PHASE4:§I.1` item 5's rationale |
| **S-3** | `COMPLETED(CD-30) ⇏ COMPLETED(CD-28)` | `EV-22` short of target | **`T-1f`** — *"complete; surface not reached"*, unknowns **1**. Complete under Phase 6's definition, **not** complete under Phase 5's | **[MEASURED]** `PHASE6:§8.1` row `T-1f` versus `PHASE5:§0.4`. **This is an internal contradiction of the chain, not a distinction between concepts** |
| **S-4** | `COMPLETED ⇏ VERIFIED` | any confirmation item passing **falsely** | **`T-1b`** — `EV-23` satisfied by a re-run that never ran; and **`FP-B`** — `EV-22` satisfied by an index operation | **[MEASURED]** §5.1, §5.3. **The separating condition is exactly U-C** |
| **S-5** | `VERIFIED ⇏ CERTIFIED(a)` | the register staged but not committed | **[MEASURED]** `PHASE5` **P5-1**: a staged register gives `--observe` **PASS** and `--guard` **DRIFT**. So `EV-21` (`RC=0`) holds while `--guard` returns **3**. Everything the program measures is green and the certification gate is red | `P5-1`, six states measured |
| **S-6** | `CERTIFIED(a) ⇏ CERTIFIED(b)` | `R-7w` | **[MEASURED]** `PHASE3:§E.7` — all three residuals survive **all 12** models. `PHASE1:§R-7` declined closing `R-7w` as *"a larger change than this phase covers."* `PHASE4:§G.3` — it is a property of the **failure** path, so no successful run even reduces it | **`CERTIFIED(b)` is not merely stronger; it is EMPTY** — §8.4 |

### 8.4 The proof that `EXECUTION-CERTIFIED(b)` is empty

**[INFERRED]** From three measured premises.

1. **[MEASURED]** `R-7w` is closable only by moving serialization inside the authority — `PHASE1:§R-7`, which declined it as out of scope.
2. **[MEASURED]** `PHASE3:§E.7` — `RES-3`, `RES-4` and `R-7w` are **LATENT → ACTIVE under all 12 models**, and **no model closes any of them**.
3. **[MEASURED]** `PHASE4:§G` — execution **REDUCES** `RES-3` and `RES-4` in evidence class and leaves `R-7w` **UNCHANGED**, because `R-7w` is the window `:893`→`:921` that only a refusal traverses (`PHASE6:§7.2`: exactly 4 of `commit()`'s 8 refusal points enter it; a successful run enters none).

**[INFERRED]** Therefore no admissible model, no execution outcome and no evidence item closes `R-7w`. `CERTIFIED(b)` requires it closed. **The set of states satisfying `CERTIFIED(b)` is empty**, and it is empty for a reason internal to the program's own scope decisions rather than for any reason execution could change. ∎

**[INFERRED]** This is stronger than *"the two readings differ"*. Under reading (b), `EXECUTION-CERTIFIED` is **unreachable in every admissible model and on every path**, so a Phase 9 that adopts reading (b) can decide the question **without executing anything**. §11 turns on this.

### 8.5 Q6 verdict

```
ARE THE FIVE TERMINAL STATES EQUIVALENT?                               NO

  PAIRWISE NON-EQUIVALENCE, WITH SEPARATING CONDITIONS ..........  6   S-1 … S-6
      of which the separating condition is a MEASURED DEFECT
      rather than a genuine conceptual distinction .............  1   S-3 (CD-28 vs CD-30)
      of which the separating condition is U-C .................  1   S-4
      of which the separating condition proves EMPTINESS .......  1   S-6

  DEFINITIONAL STATUS OF THE FIVE NAMES
      defined once, consistently ...............................  1   EXECUTION-AUTHORIZED
      defined TWICE, INCOMPATIBLY ..............................  1   EXECUTION-COMPLETE(D)
      undefined, flagged as such by PHASE6 .....................  1   EXECUTION-CERTIFIED
      NO REFERENT ANYWHERE — constructed here ..................  2   EXECUTION-SUCCESSFUL,
                                                                      EXECUTION-VERIFIED

  THE IMPLICATION CHAIN HOLDS LEFT TO RIGHT; ALL FIVE CONVERSES FAIL.
  CERTIFIED(a) ⇒ VERIFIED ⇒ COMPLETED ⇒ SUCCESSFUL ⇒ was AUTHORIZED
  CERTIFIED(b) = ∅, proved in §8.4 from three measured premises.
```

---

## 9. Completion-path enumeration — Q7

### 9.1 Run-outcome classes

**[MEASURED]** A run-outcome class is a distinct triple `(tracked-state effect, exit code, terminal governance line)`. On that definition the 10 lock states of §5.1 map onto **three** entry behaviours and run A has **six** classes — confirming `PHASE6:§7.1`, and now with the lock-state → class map complete.

| Code | Outcome | Tracked state | Exit | Terminal line | Lock states that reach it |
|---|---|---|---|---|---|
| **A✓** | all 10 phases complete, transaction sealed | mutated, sealed | 0 | `TRANSACTION COMPLETE …` | A, C, I, J, **E**, **H** |
| **A∅** | lock no-op | **untouched** | **0** | `nested/concurrent call is a no-op` | **B, D, F** |
| **A⊥** | lock content non-numeric | **untouched** | 1 | **none** — raw bash error before `fail()` exists | **G** |
| **A⊘p** | Phase 0 gate fails | untouched | 4 | `TRANSACTION INCOMPLETE …` | A, C, I, J, E, H |
| **A⊘a** | Phase 1 refused by the authority — 8 refusal points | **byte-identical** | 1 | `TRANSACTION INCOMPLETE — ukb build failed` | A, C, I, J, E, H |
| **A✗** | a phase in 2…9 fails | **mutated, unsealed** | 1/2/4 | `TRANSACTION INCOMPLETE …` | A, C, I, J, E, H |

**[INFERRED]** Lock states **E** and **H** are **not** a seventh class: they attach a spurious `bash` arithmetic error to stderr and then permit any of the five proceeding outcomes. They change **diagnosability**, not state — which is precisely why they are a false-*negative* channel (`FN-B`, §5.4) and not a distinct terminal state. Recording this explicitly is what keeps the class count at 6 rather than inflating it.

Run B, unchanged from `PHASE6:§7.3`: **B✓**, **B⊘**, **B✗** — **3** classes. **[MEASURED]** `uga_engine.py` has no re-entrancy lock of its own; the only lock is `_ledger_lock`, whose failure is `commit()` refusal 1, a genuine `LedgerWriteRefused`.

### 9.2 The correction to Phase 6's path count

**[MEASURED]** `PHASE6:§7.4` computes:

```
run-outcome paths       2 orderings × 6 × 3 .................... 36
of which A✓ ∧ B✓ ................................................  2
confirmation branches per ordering:
    V-12 / EV-23 ∈ {pass, FALSE-pass, fail} ..... 3
    V-13 / EV-24 ∈ {pass, fail} ................. 2
    V-14 / EV-25 ∈ {pass, fail} ................. 2      -> 12
TOTAL ........................................ 34 + (2 × 12) = 58
```

**[INFERRED] `V-11` / `EV-22` is absent from the branch factors.** But `PHASE6:§8.1` lists `T-1f` — *"`A✓ ∧ B✓`, `EV-22` gate short of target"*, unknowns **1** — as one of its 17 terminal states. **A terminal state that §8.1 counts cannot lie on a path §7.4 does not enumerate.** The two sections of Phase 6 are inconsistent, and the inconsistency is a factor of 2 in one dimension.

**[MEASURED]** §5.3 of this phase adds a second correction: `EV-22` has a **false-pass** channel (`FP-B`) exactly as `EV-23` does, so its branch is 3-valued, not 2-valued.

```
CORRECTED CONFIRMATION BRANCH FACTORS, per ordering

    V-11 / EV-22 ∈ {pass, FALSE-pass, fail} ..... 3     <- omitted by PHASE6 §7.4
    V-12 / EV-23 ∈ {pass, FALSE-pass, fail} ..... 3
    V-13 / EV-24 ∈ {pass, fail} ................. 2
    V-14 / EV-25 ∈ {pass, fail} ................. 2
                                                 ────
                                                  36

TOTAL DISTINCT PATHS ....................... 34 + (2 × 36) = 106

    PHASE6's figure ............................................  58
    restoring EV-22 as a 2-valued branch .......................  82
    adding EV-22's FALSE-pass channel (§5.3) ................... 106
```

### 9.3 The ten named path kinds, evaluated

The task names ten path kinds. Each is located in the enumeration and evaluated on the five properties.

| # | Path kind | Reachable? | Completion-valid? | Authorization-valid? | Evidence-valid? | Rollback-valid? |
|---|---|---|---|---|---|---|
| **1** | **Success** — `A✓ ∧ B✓`, all four confirmations genuinely pass | **YES**, 2 paths (one per ordering) | **YES** under both `CD-28` and `CD-30` | **YES** for runs 1 and 2; **the re-run's third event is valid only in M1** (§4.2) | **YES** — except `EV-25`, which no run can produce (§6.3) | n/a — none needed |
| **2** | **Refusal** — `A⊘a` and/or `B⊘`, any of `commit()`'s 8 points | **YES**, 8 paths with one run succeeding + 4 with both refused | **NO** — 1 or 2 unknowns remain | **YES** — a refusal *is* the authorization working. **[MEASURED]** every refusal restores the pre-image byte-for-byte (`PHASE1:§R-7`, five tests) | **YES** — and `T-6` (both refused) leaves **both permits still verifying**, since the pre-image never moved | **YES, vacuously** — nothing was written |
| **3** | **Rollback** — `A✗` or `B✗`, then `R-A + R-B + R-C` | **YES**, 5 terminal states require it | **NO** | **YES**, and with a measured side effect: **[MEASURED]** `PHASE2` **P2-1** — a byte restore **re-validates the used permit** under `B1`. The rollback procedure *is* the `E1-F3` replay vector | **CONDITIONAL** — `EV-18` must be captured **before** `R-A` or the changed-path set is unrecoverable (`PHASE4:§E.3`) | **YES if `checkout`-class**; **NO if `reset`-class** — **[MEASURED]** `PHASE5` **P5-3**: `reset --hard` deletes the `AM` `ledger_authority.py`, all twelve Phase-1 closures |
| **4** | **Partial execution** — `A✗`: a phase in 2…9 fails, tracked state mutated and unsealed | **YES** | **NO**, and **[INFERRED]** it is the state `REG-AUTO-001` §5 P5 says cannot exist: *"Partial registration is a failed transaction, not a partial success."* The law has the right verdict and the script produces the state anyway | **YES** — the write that landed was authorized | **YES** if `EV-18` captured first | **YES**, `checkout`-class only |
| **5** | **Interrupted execution** — the process is killed mid-transaction | **YES** | **NO** | **YES** for whatever landed | **PARTIAL** — stdout/stderr may be truncated, and `EV-17` is a transcript with no binding to the run (§6.1) | **YES**, **and it leaves lock state B** — so the *next* invocation, including `V-12`, silently no-ops for up to an hour (§5.1). **This is the single most reachable route into `FP-A`** |
| **6** | **Stale authorization** — a permit that lapsed before use | **YES**, 3 measured causes | **NO** | **NO — and correctly so.** `AUTHORIZATION-LAPSED` (`PHASE5:§0.4`). **[MEASURED]** three causes: any ledger write; any commit if `head`-bound; `git` unavailable ⇒ `head is None` ⇒ refuse rather than assume | **YES** — the refusal names the failing binding (`:797-802`) | **YES, vacuously** |
| **7** | **Stale evidence** — `EV-3`/`EV-12`/`EV-14`/`EV-16` measured before an intervening index change | **YES — and more easily than any phase has stated.** **[MEASURED]** **P7-4**: `git add` of any of **42** untracked files invalidates permit A; **[MEASURED]** **P7-8**: `git add` of **any file whatsoever** invalidates permit B | **NO** | **NO** — refused on `manifest_digest`, and independently on `scope.max_allocations`, which has **zero slack** (`PHASE6` H-7) | **YES** — the refusal is diagnostic | **YES, vacuously** |
| **8** | **Stale lock** — `.register.lock` present from a killed run | **YES**, 3 of 10 lock states | **NO — and it reports COMPLETE.** This is `FP-A` | **VACUOUSLY** — no `commit()` is reached, so no permit is consumed and none lapses | **NO — the evidence is tautological** (§6.2, `EV-23`) | **YES, vacuously** — nothing happened |
| **9** | **Stale register** — the permit register restored by `R-D` or reverted | **YES** | **NO** | **[MEASURED]** **DANGEROUS**: `R-D` can **resurrect a superseded permit**, creating a duplicate on the next append; `:718-723` then makes that `permit_id` **permanently unusable** (`PHASE6` H-13). **[INFERRED]** No rollback procedure repairs it | `EV-9`/`EV-20` fail | **PARTIAL — `R-D` is the one procedure that can create damage it cannot undo** |
| **10** | **Stale permit** — a permit whose bindings no longer match | **YES** | **NO** | **NO** — refused on 1–4 of the 4 strict bindings. **[MEASURED]** the re-run's run-1 permit fails **two**, in all three manifest classes | **YES** | **YES, vacuously** |

### 9.4 Paths reaching `EXECUTION-COMPLETED`

**[INFERRED]** The count depends on which definition is adopted, and that dependence is the numeric content of `U-E`.

```
UNDER CD-30 (PHASE6 §11.1)  —  A✓ ∧ B✓ ∧ EV-23 ∧ EV-24 ∧ EV-25, EV-22 FREE

    EV-22 ∈ {pass, FALSE-pass, fail} .......... 3     (unconstrained)
    EV-23 ∈ {pass, FALSE-pass} ................ 2
    EV-24 = pass · EV-25 = pass ............... 1
    per ordering .............................. 6
    PATHS REACHING EXECUTION-COMPLETED ....... 12

UNDER CD-28 (PHASE5 §0.4)  —  both runs landed AND BOTH UNKNOWNS RETIRED

    EV-22 ∈ {pass, FALSE-pass} ................ 2     (UK-2 must be retired)
    EV-23 ∈ {pass, FALSE-pass} ................ 2     (UK-1 item 5)
    EV-24 = pass · EV-25 = pass ............... 1
    per ordering .............................. 4
    PATHS REACHING EXECUTION-COMPLETE ......... 8

  THE DEFINITIONAL CONFLICT IS WORTH EXACTLY 4 PATHS.
  The 4 are the T-1f family: complete under Phase 6, not complete under Phase 5.

GENUINE COMPLETION (no confirmation item falsely satisfied) ......  2   one per ordering
FALSE COMPLETION ................................................  6 under CD-28
                                                                  10 under CD-30
PATHS REACHING COMPLETION ON THE PACKAGE AS SPECIFIED ...........  0
    [MEASURED] §4.2 — with IA-4 static the re-run's permit fails two strict
    bindings in ALL THREE manifest classes, so EV-23 cannot be genuinely
    satisfied on any path.  Only the FALSE variants remain reachable.
    [MEASURED] §6.3 — EV-25 has no producer, so even the genuine paths cannot
    be fully evidenced.  This is a SECOND, independent reason the count is 0,
    and PHASE6 identified only the first.
```

### 9.5 Path properties in aggregate

**[INFERRED]** The 106 decompose as `34 + (2 × 36)`: the 2 base combinations in which both runs succeed expand into 36 confirmation branches each; the other 34 do not branch on confirmation because at least one run did not land.

| Path class | Base combos / ordering | Count | Reachable | Auth-valid | Completion-valid | Evidence-valid | Rollback-valid |
|---|---:|---:|---|---|---|---|---|
| Both succeed, all four confirmations genuinely pass | *(within `A✓B✓`)* | **2** | yes | yes* | **yes** | **no** — `EV-25` unproducible | n/a |
| Both succeed, ≥1 confirmation **falsely** passes | *(within `A✓B✓`)* | **10** | yes | yes* | **yes — falsely** | no | n/a |
| Both succeed, ≥1 confirmation genuinely fails | *(within `A✓B✓`)* | **60** | yes | yes* | no | partial | n/a |
| One lands, the other **refused cleanly** — `A✓B⊘`, `A⊘pB✓`, `A⊘aB✓` | 3 | **6** | yes | yes | no | yes | yes — byte-identical |
| One lands, the other **fails mid-run** — `A✓B✗`, `A✗B✓` | 2 | **4** | yes | yes | no | conditional on `EV-18` | `checkout`-class only |
| One **refused**, the other **fails mid-run** — `A⊘pB✗`, `A⊘aB✗`, `A✗B⊘` | 3 | **6** | yes | yes | no | conditional | `checkout`-class only |
| **`A∅`** no-op paths — `A∅` × {`B✓`,`B⊘`,`B✗`} | 3 | **6** | yes | vacuously | **reports complete — falsely** | **tautological** | yes for A; per B otherwise |
| **`A⊥`** abort paths — `A⊥` × {`B✓`,`B⊘`,`B✗`} | 3 | **6** | yes | vacuously | no | **no** — no governance message at all | yes for A; per B otherwise |
| **Both refused cleanly** — `A⊘pB⊘`, `A⊘aB⊘` | 2 | **4** | yes | yes | no | yes — **both permits still verify** | yes, vacuously |
| **Both fail mid-run** — `A✗B✗` | 1 | **2** | yes | yes | no | conditional | both scopes |
| | **17 + `A✓B✓`** | **106** | | | | | |

`*` authorization-valid for runs 1 and 2; the **re-run's** third authorization event is valid only in manifest class **M1** (§4.2).

```
arithmetic check ..... 2 + 10 + 60 + 6 + 4 + 6 + 6 + 6 + 4 + 2 = 106        ✓
                       (72 from A✓B✓ expansion) + (34 non-branching)        ✓

PATHS REACHABLE ................................................. 106 of 106
PATHS AUTHORIZATION-VALID ....................................... 106 of 106   (A∅/A⊥ vacuously)

COMPLETION
    completion-valid under CD-30 (PHASE6 §11.1) .................  12
    completion-valid under CD-28 (PHASE5 §0.4) ..................   8
    completion-valid AND GENUINELY SO ...........................   2
    completion-valid ON THE PACKAGE AS SPECIFIED ................   0
        two independent reasons, and PHASE6 identified only the first:
        (a) IA-4 static => EV-23 unsatisfiable genuinely in ALL 3 classes
        (b) EV-25 has NO PRODUCER, so no path is fully evidenced (§6.3)

UNKNOWNS
    paths REPORTING 0 unknowns ..................................  32
        of which GENUINELY 0 ....................................   8
        of which FALSELY 0 ......................................  24
    paths leaving >=1 unknown open ..............................  74
    arithmetic check ..... 32 + 74 = 106                              ✓

EVIDENCE
    paths EVIDENCE-VALID .......................................    0
        [MEASURED] §6.3 — EV-25 is unproducible on EVERY path.  This is the
        first property in this chain that fails on all paths rather than on
        some, and it is why "fully evidenced" is answered NO in §1.1.

REVERSIBILITY   (criterion: SEMANTIC — has any allocation landed?)
    paths in which NO allocation lands ..........................   8
        exactly the four `<A-not-landed> × B⊘` combinations, both orderings:
        A∅B⊘ · A⊥B⊘ · A⊘pB⊘ · A⊘aB⊘
    paths in which >=1 allocation lands .........................  98
    arithmetic check ..... 8 + 98 = 106                               ✓
    [INFERRED] This is a correction to PHASE6 §7.5, which reports
    "FULLY REVERSIBLE 28 · SEMANTICALLY IRREVERSIBLE 30" over its 58.
    Under Phase 6's own stated criterion — "any landed allocation" — its
    figures do not decompose: 14 of each ordering's 18 base combinations
    land an allocation, giving 26 non-branching + 24 branching = 50
    irreversible and 8 reversible, not 30 and 28.  The 8 is invariant
    under the path-count correction, because the reversible set contains
    no A✓B✓ path and therefore does not expand.

BLOCKERS
    paths producing a NEW blocker ...............................   0   confirmed across 106
```

**[INFERRED]** *"No path produces a new blocker"* is confirmed across the enlarged space of 106, as it was across Phase 6's 58 and Phase 4's smaller space. The three consecutive confirmations are worth recording: the program **reveals** defects and does not **create** them, and that has now been checked at three different resolutions.

---

## 10. Closure-sufficiency determination — Q8

### 10.1 The question, stated so it can be answered

> Is closure of `U-B` and `U-C` sufficient to make execution completion fully determined? If NO, identify every remaining uncertainty. If YES, prove the uncertainty set reduces exactly to `UK-1` and `UK-2` and nothing else.

### 10.2 Answer — **NO**

**[INFERRED]** Closing `U-B` and `U-C` as Phase 6 specifies them leaves **seven** items, not two. Five are identified here for the first time.

| ID | Uncertainty | Class | Closable by determination? | Governance-dependent? | Basis |
|---|---|---|---|---|---|
| **U-D** | **The `by_object` population is a function of the git index, and today the anonymous set is EQUAL to the staged-new set.** `EV-14`'s measurand is not a property of any commit; a `git add` of **any file whatsoever** changes it; `UGA-INV-01 violations=0` is satisfiable with zero mints | **[DEFECT]** — evidence | **YES** — `CC-4` + `CC-5`, no code | **NO** | **[MEASURED]** **P7-6**, **P7-7**, **P7-8** |
| **U-E** | **Two non-equivalent definitions of the terminal completion state** — `CD-28` and `CD-30` — differing by **4 completion paths** and by whether `T-1f` is complete | **[DEFECT]** — definitional | **YES** — `CC-6`, an adjudication | **NO** — touches no axis | **[MEASURED]** §3.8 pair 3; §9.4 |
| **U-F** | **`REG-AUTO-001` §7 — the constitutional completion law `register.sh:16` cites as its own authority — is consumed by no phase; is an 8-register conjunction, not the 10-phase one enforced; names 6 phases where 10 exist; has no vocabulary for a transaction that did not run; and its §8 invariant is violated today by exactly 9** | **[DEFECT]** — specification | **YES** — an `IA-7`-class amendment plus adoption into the chain | **NO** | **[MEASURED]** **P7-3**, **P7-10** |
| **U-G** | **`EV-1` / `EV-24` bind a count (≥ 77), not a set.** Removing a Phase-1 test and adding a new one is undetectable by the stated condition | **[DEFECT]** — evidence | **YES** — restate the condition over the test **set** | **NO** | **[INFERRED]** from `PHASE5` `EV-1`'s own stated purpose |
| **U-H** | **The sentinel path performs no actor binding, holds no `permit_id` and writes no register entry.** Under closure `CB-1` the program's third authorization event uses it, so that event is unissued, unconsumed, unrecorded and unattributable in all 12 models | **[DEFECT]** — accounting | **YES** — capture the re-run's `commit()` report; `UK-1` item 6 already requires it | **NO** | **[MEASURED]** `:684-707`, `:878-879` |
| **UK-1** | `register.sh` end-to-end completion — **6** components (Phase 4's 5 + Phase 6's item 6) | **[UNKNOWN]** — execution-time | **NO** | — | carried |
| **UK-2** | post-mint clearance and gate greenness — **4** components | **[UNKNOWN]** — execution-time | **NO** | — | carried |

```
UNCERTAINTY SET AFTER CLOSING {U-B, U-C} .........................  7
    execution-time unknowns (irreducible) .........................  2   UK-1, UK-2
    defects closable by determination .............................  5   U-D … U-H
    of the five, GOVERNANCE-DEPENDENT .............................  0

=> THE HYPOTHESIS IS FALSIFIED.  Closing U-B and U-C does NOT leave only
   UK-1 and UK-2.  It leaves five further items, none of them execution-time
   unknowns and none of them governance-dependent.
```

### 10.3 Why the five were not visible to Phase 6

**[INFERRED]** Stated because a phase that finds five items its predecessor missed owes an account of why, or the finding reads as luck.

| Item | Why Phase 6 could not see it |
|---|---|
| **U-D** | Phase 6 declined to run `uga_engine gate`, correctly under its own Rule 4-equivalent, and therefore carried `PHASE4` **P4-4**'s figure of 27 without re-deriving *what* the 27 are. The set-identity with the staged-new files is invisible from the count alone |
| **U-E** | The two definitions live in **different documents**. Phase 6 wrote `CD-30` and did not compare it with `PHASE5:§0.4`, which it cites elsewhere. **[INFERRED]** The conflict is only detectable by holding both definitions side by side and asking whether `T-1f` satisfies each |
| **U-F** | `REG-AUTO-001` §7 is not in any phase's input list. It is reachable only by following `register.sh:16`'s own citation out of the script and into `00-BOOK/CONTROL-TOWER/` — a file in a **guard directory**, which every phase has been careful not to touch |
| **U-G** | `EV-1`'s condition is short and reads as a floor. That a floor is not a set is obvious once stated and invisible until it is |
| **U-H** | It is **created by Phase 6's own closure `C-1`**, not present before it. A defect introduced by a proposed remedy is not visible to the phase that proposes the remedy |

### 10.4 The reduction proof

**Claim.** Closing `{U-B, U-C, U-D, U-E, U-F, U-G, U-H}` reduces the uncertainty set to exactly `{UK-1, UK-2}` **over the enumerated surfaces**.

**Method.** The claim is checkable rather than assertable because every surface this chain reasons over is **finite and enumerated**. Six surfaces exhaust what stands between `EXECUTION-AUTHORIZED` and a terminal proof. For each, the proof obligation is that after the seven closures every cell is either resolved or tagged `UK-1`/`UK-2`.

| # | Surface | Cardinality | State after the seven closures |
|---|---|---:|---|
| **1** | **Completion definitions** (§3) | **35** | `U-E` fixes the `CD-28`/`CD-30` conflict; `U-F` fixes `CD-19`/`CD-21`/`CD-24` and supplies the third value `CD-3` lacks; `CC-1` fixes `CD-1`'s incompleteness and `CD-4`'s unverified claim; `CC-2` fixes `CD-6`. **4 contradictory pairs → 0.** Remaining open: `CD-4` (idempotence) and `CD-20` (P3) are **assertions the runs test** — that is `UK-1` item 5 |
| **2** | **Evidence items** (§6) | **27** | `CB-*` makes `EV-23` producible in its class; `CC-1` makes it discriminating; `CC-4`/`CC-5` make `EV-22` and `EV-14` discriminating; `U-G` makes `EV-1`/`EV-24` set-bound; `PHASE6` H-11 fixes `EV-1`'s invocation. **`EV-25` remains UNPROVEN** — and it is not an unknown, it is an **absent producer**, so its closure is an implementation act inside `U-H`'s scope. The 4 UNSAFE items (`EV-7`, `EV-17`, `EV-18`, `EV-26`) remain forgeable — **[INFERRED]** and that is a *property of transcripts*, not an uncertainty: nothing about them is unknown |
| **3** | **Authorization accounting** (§7) | **72 cells** | `IA-12` moves issuance and mismatch from PARTIAL to COMPLETE (12 + 12 cells); `O-3` moves `B2` consumption (6 cells); `GA-2`'s answer on modifier `T` moves expiry from AMBIGUOUS to COMPLETE (12 cells); `U-H` moves sentinel replay from UNDEFINED. **72 of 72 COMPLETE.** Note that `GA-2` is **[GOV-REQ]** — but it is one of `PHASE2`'s existing 13 decisions, so it is **not a new** governance dependency |
| **4** | **Lock states** (§5.1) | **10** | `CC-2` or `CC-3` makes B/D/F distinguishable from A✓; `CC-2` gives G a governance message; E/H/J remain diagnosability defects with no completion consequence once the terminal signal, not the exit code, is the success condition. **0 false-positive channels remain** |
| **5** | **Paths** (§9) | **106** | Completion-valid count becomes well-defined (one definition, `U-E`); false-completion paths **10 → 0**; genuine completion paths **2**; evidence-valid **0 → 2** once `EV-25` has a producer. **Whether the program reaches one of the 2 is `UK-1` ∧ `UK-2`** |
| **6** | **Terminal-state names** (§8) | **5** | `U-E` fixes `COMPLETED`; `U-F` supplies the third value; `EXECUTION-SUCCESSFUL` and `EXECUTION-VERIFIED` are constructed in §8.2 and can be adopted or discarded; **`EXECUTION-CERTIFIED` remains two readings, one of which is provably EMPTY (§8.4)** — and that emptiness is **proved, not unknown**, so it is a determination outstanding, not an uncertainty |

**[INFERRED] Conclusion of the proof.** After the seven closures, every cell on all six surfaces is either resolved or reduces to *"did `register.sh` complete end-to-end?"* (`UK-1`) or *"does the `by_object` population clear in one mint and does the gate go green?"* (`UK-2`). **No third question survives.** ∎

**[INFERRED] What the proof does and does not establish — stated because the limitation is the honest part.** The enumeration is exhaustive over the surfaces **Phases 0–6 name plus the four this phase adds**. It is not a proof that no seventh surface exists. The chain's own record argues against over-confidence here: Phase 6 found **14** hidden dependencies that Phases 2–5 did not name, and this phase found **5** further defects Phase 6 did not name, one of which (`U-H`) Phase 6's own remedy created. **[INFERRED]** The rate is decreasing — 14, then 5 — and the character has changed, from mechanical dependencies to definitional conflicts, which is what a converging audit looks like. But *decreasing* is not *zero*, and a Phase 8 conducted at this resolution should be expected to find between one and three more.

### 10.5 One thing the seven closures do **not** buy

**[INFERRED]** They do not make execution completion **determined in advance**. They make it **decidable when it happens**. `U-A` is untouched: **[MEASURED]** `--plan` exists on `ukb build` and `uga_engine run` and **nowhere in `ukbx.py`** (`PHASE4` **P4-6**), so `register.sh` phases 2, 3, 4 and 8 have no dry-run mode at all, and nothing short of running them establishes their behaviour against post-mint state.

**[INFERRED]** `PHASE6:§11.3` closes on the observation that *"a process whose every path is known and whose outcome is not is not an underdetermined process. It is a measurement."* That is correct and this phase does not disturb it — but it is only true once the measurement **discriminates**, and §5 establishes four channels on which it currently does not. The seven closures are what turn the program from a measurement that can return a false reading into one that cannot.

### 10.6 Q8 verdict

```
IS CLOSURE OF U-B AND U-C SUFFICIENT?                                  NO

  REMAINING UNCERTAINTY SET .....................................  7
      execution-time, irreducible .................................  2   UK-1, UK-2
      defects closable by determination ...........................  5   U-D … U-H
          evidence defects ........................................  2   U-D, U-G
          definitional defects ....................................  1   U-E
          specification defects ...................................  1   U-F
          accounting defects ......................................  1   U-H
      governance-dependent among the five .........................  0

  AFTER CLOSING ALL SEVEN, THE SET REDUCES TO EXACTLY {UK-1, UK-2}.
      proved by exhaustion over six enumerated surfaces:
      35 definitions · 27 evidence items · 72 accounting cells ·
      10 lock states · 106 paths · 5 terminal-state names
      exhaustive OVER THOSE SURFACES; not a proof that no seventh exists.

  U-B and U-C closures required for the reduction:  CB-1 or CB-3 or CB-4  (§4.5)
                                                    CC-1 and CC-4 and CC-6 (§5.6b)
      — enumerated, not selected.  Constraint 8.
```

---

## 11. Phase-9 feasibility determination — Q9

### 11.1 The three outcomes, and what each requires

| Outcome | What a Phase 9 must establish to reach it |
|---|---|
| **A — UNCONDITIONAL READY EXISTS** | That some state satisfies the adopted reading of *"unconditional ready"* **and** is reachable |
| **B — UNCONDITIONAL READY DOES NOT EXIST** | That **no** state satisfies it under **any** admissible model |
| **C — INSUFFICIENT INFORMATION** | That neither A nor B is establishable from what is known |

**[INFERRED]** The answer turns on a reading that no artifact in the chain fixes — the same defect as `EXECUTION-CERTIFIED` (§8.1), one level up. Two readings are live, and Phase 6 declined to choose between their analogues:

| Reading | *"Unconditional ready"* means |
|---|---|
| **(i) outcome-freedom** | 0 blockers ∧ 0 unknowns, with the 3 residuals **accepted** under `GA-5` |
| **(ii) residual-freedom** | 0 blockers ∧ 0 unknowns ∧ **0 residuals** |

### 11.2 Which outcomes remain reachable after Phase 7

**[INFERRED]** All three. Each is established separately.

**Outcome B is not merely reachable — it is PROVABLE TODAY, without any run, under reading (ii).**

Proof, from three measured premises already in the chain:

1. **[MEASURED]** `PHASE3:§E.7` — `RES-3`, `RES-4` and `R-7w` are invariant across **all 12** admissible models; no model closes any of them.
2. **[MEASURED]** `PHASE4:§G` — execution **REDUCES** `RES-3` and `RES-4` in evidence class and leaves `R-7w` **UNCHANGED**, because `R-7w` is the window `:893`→`:921` that only a refusal traverses. **[MEASURED]** `PHASE6:§7.2` supplies the enumeration: exactly **4 of `commit()`'s 8** refusal points enter it and a successful run enters **none**.
3. **[MEASURED]** `PHASE1:§R-7` — closing `R-7w` requires moving serialization inside the authority, declined as *"a larger change than this phase covers."*

**[INFERRED]** Therefore under reading (ii) the satisfying set is **empty**, for every model and on every path, and the emptiness is established by deduction from committed measurements. **A Phase 9 adopting reading (ii) can return B with zero mutating runs.** This is the same proof shape as §8.4 and is the strongest positive result of this phase: **one of the three terminal outcomes is already decided, and deciding it costs nothing.**

**Outcome A remains reachable, and only conditionally.** Under reading (i), A requires terminal state `T-1a` — `A✓ ∧ B✓` with all four confirmations **genuinely** satisfied. **[MEASURED]** §9.4: **2** of 106 paths reach it, and **0** are reachable on the package as specified. After the seven closures of §10, 2 become reachable. **[MEASURED]** whether the program traverses one of them is `UK-1 ∧ UK-2`, which is `U-A`: unmeasurable before the runs, because four of `register.sh`'s ten phases have no dry-run mode. **A is therefore reachable and cannot be established in advance by any determination.**

**Outcome C remains reachable, and is the status quo.** **[MEASURED]** No artifact in Phases 0–7 adopts reading (i) or (ii). Adopting one is a determination, and this phase is constrained against making it (constraints 1 and 8). **[INFERRED]** While the reading is undeclared, a Phase 9 that reports A or B is reporting a result whose premise it supplied itself. C is the correct outcome for a Phase 9 conducted before the reading is fixed.

### 11.3 Proof that Phase 7 removes no outcome

**[INFERRED]** An outcome is removed if this phase's findings make it unreachable.

| Outcome | Removed? | Argument |
|---|---|---|
| **A** | **NO** | The five new defects `U-D … U-H` are **all closable by determination** (§10.2) and **none is governance-dependent**. So none makes `T-1a` unreachable; each makes it unreachable *until closed*, which is a schedule, not a barrier. **[MEASURED]** `PHASE6:§8.1` establishes `T-1a`'s reachability and nothing here disturbs it |
| **B** | **NO** | Strengthened rather than removed: §8.4 supplies an independent proof of the same shape at the `EXECUTION-CERTIFIED` level, so the argument for B now has two witnesses instead of one |
| **C** | **NO** | Strengthened: this phase adds `U-E` — a definitional conflict inside the chain — to the reasons a reading must be fixed before A or B can be claimed |

### 11.4 What Phase 7 does remove

**[INFERRED]** Not an outcome — a **mode of reaching one**.

```
BEFORE THIS PHASE, a Phase 9 could have reported OUTCOME A on:
    - EV-23 satisfied by a re-run that never ran            (FP-A, PHASE6 found this)
    - EV-22 satisfied by an index operation, not a mint     (FP-B, NEW)
    - EXECUTION-COMPLETED asserted with UK-2 still open     (FP-C, NEW)
    - a >=77 test count that concealed a removed test       (U-G,  NEW)
    - EV-25 "evidence" that no producer can emit            (§6.3, NEW)

  Five channels.  PHASE6 closed one.  This phase names four more and, with
  §5.5's eight discriminators and §10's seven closures, makes all five
  detectable.  Phase 7 does not decide the Phase-9 question.  It makes the
  Phase-9 answer FALSIFIABLE, which it was not.
```

### 11.5 Q9 verdict

```
IS A PHASE-9 TERMINAL PROOF POSSIBLE?                                 YES

  OUTCOMES REACHABLE AFTER PHASE 7 .............................. 3 of 3
      A  UNCONDITIONAL READY EXISTS ...... reachable under reading (i) ONLY,
                                           via T-1a, and CONDITIONAL ON U-A —
                                           not establishable in advance by any
                                           determination
      B  DOES NOT EXIST .................. reachable AND PROVABLE TODAY under
                                           reading (ii), with ZERO mutating
                                           runs, from three measured premises
      C  INSUFFICIENT INFORMATION ........ reachable, and CORRECT while the
                                           reading is undeclared

  OUTCOMES REMOVED BY PHASE 7 ................................... 0
  OUTCOMES STRENGTHENED BY PHASE 7 .............................. 2   B and C
  FALSE ROUTES TO OUTCOME A CLOSED BY PHASE 7 ................... 4   of 5 total;
                                                                     PHASE6 closed the 5th

  THE DECIDING FACTOR IS NOT EVIDENCE.  It is which reading of
  "unconditional ready" is adopted — a determination this phase is
  constrained against making, and which no artifact in Phases 0-7 makes.
  Under reading (ii) the answer is B and costs nothing.  Under reading (i)
  the answer is A or C and costs two irreversible mutating runs.
  BOTH READINGS ARE STATED.  NEITHER IS PREFERRED.
```

---

## 12. Exact counts

### 12.1 Completion definitions

```
COMPLETION AND TERMINAL-STATE DEFINITIONS ........................ 35
    machine-enforced .............................................. 17
    documentary ................................................... 18
    necessary for EXECUTION-COMPLETED ............................. 14
    claimed sufficient .............................................  6
    ACTUALLY sufficient ............................................  0
    contradictory PAIRS ............................................  4
    members of a contradictory pair ................................  8
    incomplete (leave a reachable state unclassified) .............. 13
    non-discriminating .............................................  2
    present in the repository, consumed by NO phase of this chain ..  2
    named by the task with NO REFERENT ANYWHERE ....................  2
```

### 12.2 U-B

```
MANIFEST CLASSES OF THE RE-RUN ....................................  3   M1, M2, M3
    authorizable by PHASE6's closure C-1 ..........................  1   M1
    obtaining today ............................................... M1   [MEASURED] P7-2
    entered by a single `git add -A` .............................. M3   [MEASURED] P7-4
UNTRACKED FILES THAT WOULD BECOME by_path-ELIGIBLE ON `git add` ... 42
    by_path population today ......................................  9
    after `git add -A` ............................................ 51   (52 including this document)
MINIMUM ARTIFACT SET FOR U-B ......................................  9
CLOSURE CLASSES ...................................................  7   CB-1 … CB-7
    covering all three manifest classes ...........................  0
    governance-independent ........................................  5
    governance-dependent ..........................................  2   CB-2 (axis D), CB-6 (GA-6)
DEPENDENCY CLASS ................ specification AND implementation AND model
    the model-dependence is axis D, and ONLY axis D ...............  6 of 12 models route
                                                                      class M2 through O-7
```

### 12.3 U-C

```
LOCK STATES MEASURED .............................................. 10   (PHASE6 P6-6: 7)
    exit 0 having run nothing ......................................  3   B, D, F
    exit 1 with no governance message ..............................  1   G
    proceed with alarming stderr, then run a real transaction ......  2   E, H
    proceed cleanly ................................................  4   A, C, I, J
    NEW in this phase ..............................................  3   H, I, J

REACHABLE FALSE-POSITIVE COMPLETION STATES ........................  4
    distinct causes across the four ................................  8
    identified by PHASE6 ...........................................  1
    NEW ............................................................  3
    live today .....................................................  3
    latent (0 live call sites) .....................................  1   FP-D

REACHABLE FALSE-NEGATIVE COMPLETION STATES ........................  6
    NEW or newly extended ..........................................  3
    in which the repository is irreversibly mutated while the
    operator is told it failed .....................................  1   FN-B

MINIMUM DISCRIMINATING EVIDENCE ITEMS .............................  8
    NEW in this phase ..............................................  3
CLOSURE CLASSES ...................................................  6   CC-1 … CC-6
    governance-independent ....................................... 6 of 6

BLAST RADIUS, MEASURED
    live `register.sh` invocations in the repository ...............  2   both `--observe`
    of which vulnerable to the lock channel ........................  0   `--observe` returns
                                                                          at :178, before the
                                                                          guard at :187
    live `--guard` invocations .....................................  0
```

### 12.4 Evidence

```
EVIDENCE ITEMS CLASSIFIED ......................................... 27   EV-1 … EV-27
    SAFE ...........................................................  9
    UNSAFE .........................................................  4
    UNPROVEN .......................................................  6
    TAUTOLOGICAL ...................................................  1
    NON-DISCRIMINATING .............................................  7
    check .......... 9 + 4 + 6 + 1 + 7 = 27                              ✓

UNPRODUCIBLE EVIDENCE ITEMS .......................................  3   (PHASE6: 2)
    EV-1   by the command PHASE4 V-1 names
    EV-23  in manifest classes M2 and M3
    EV-25  AT ALL — no producer exists anywhere                          NEW
REDUNDANT EVIDENCE ITEMS ..........................................  0
NON-DISCRIMINATING DEFECT CLASSES .................................  5
ITEMS WHOSE CLASS DEPENDS ON AN AXIS VALUE ........................  3   EV-13, EV-22, EV-23
FRACTION OF THE EVIDENCE BASE THAT IS SAFE ........................ 33%
```

### 12.5 Authorization accounting

```
CELLS ............................... 6 dimensions × 12 models = 72
    COMPLETE ....................................................... 18
    PARTIAL ........................................................ 42
    AMBIGUOUS ...................................................... 12
    UNDEFINED ......................................................  0
    check .......... 18 + 42 + 12 + 0 = 72                              ✓

MODELS WITH COMPLETE ACCOUNTING ON ALL SIX DIMENSIONS .............  0 of 12
DIMENSIONS COMPLETE IN EVERY MODEL ................................  1   invalidation
DIMENSIONS AMBIGUOUS IN EVERY MODEL ...............................  1   expiry (modifier T free)
DIMENSIONS DIFFERENTIATED BY AXIS B ...............................  1   consumption
DIMENSIONS DIFFERENTIATED BY AXIS D OR Aud ........................  0
UNACCOUNTABLE AUTHORIZATION EVENT CLASSES .........................  3
CLOSURE-REDUNDANT DECISIONS THAT NONETHELESS CHANGE THE PACKAGE ...  3   B2a/B2b, R, and now T
```

### 12.6 Terminal states and paths

```
TERMINAL-STATE NAMES COMPARED .....................................  5
    defined once, consistently .....................................  1
    defined twice, INCOMPATIBLY ....................................  1
    undefined, flagged as such .....................................  1
    NO REFERENT ANYWHERE ...........................................  2
SEPARATING CONDITIONS .............................................  6   S-1 … S-6
    proving a reading is EMPTY .....................................  1   S-6

RUN-A OUTCOME CLASSES .............................................  6   confirming PHASE6
RUN-B OUTCOME CLASSES .............................................  3
RUN-OUTCOME PATHS ................................................. 36
CONFIRMATION BRANCH FACTORS, per ordering ......................... 36   3 × 3 × 2 × 2
TOTAL DISTINCT PATHS .............................................. 106  (PHASE6: 58)
    restoring EV-22 as a 2-valued branch ........................... 82
    adding EV-22's FALSE-pass channel .............................. 106

PATHS COMPLETION-VALID under CD-30 ................................ 12
PATHS COMPLETION-VALID under CD-28 ................................  8
    the definitional conflict is worth exactly ..................... 4 paths
PATHS COMPLETION-VALID AND GENUINELY SO ...........................  2
PATHS COMPLETION-VALID ON THE PACKAGE AS SPECIFIED ................  0
PATHS EVIDENCE-VALID ..............................................  0   EV-25 fails on all
PATHS REPORTING 0 UNKNOWNS ........................................ 32
    genuinely ......................................................  8
    falsely ........................................................ 24
PATHS LEAVING >=1 UNKNOWN OPEN .................................... 74
PATHS IN WHICH NO ALLOCATION LANDS ................................  8
PATHS IN WHICH >=1 ALLOCATION LANDS ............................... 98
PATHS PRODUCING A NEW BLOCKER .....................................  0
```

### 12.7 Closure sufficiency and Phase-9 feasibility

```
UNCERTAINTY SET AFTER CLOSING {U-B, U-C} ..........................  7
    execution-time, irreducible ....................................  2   UK-1, UK-2
    defects closable by determination ..............................  5   U-D … U-H
    governance-dependent among the five ............................  0
AFTER CLOSING ALL SEVEN ........................................... {UK-1, UK-2}
    proved by exhaustion over ......................................  6 surfaces
    35 definitions · 27 evidence items · 72 cells · 10 lock states ·
    106 paths · 5 names

UK-1 components ...................................................  6   (PHASE4: 5)
UK-2 components ...................................................  4
    obtainable from a failure path — UK-1 ..........................  0
    obtainable from a failure path — UK-2 ..........................  1   item 2, negatively
    and, NEW, item 2 has a SECOND cause that is not an answer at all
    (a `git add` between the mint and V-11) — §5.4 FN-D(ii)

PHASE-9 OUTCOMES REACHABLE ........................................  3 of 3
    provable TODAY, with zero runs, under reading (ii) .............  1   outcome B
    requiring both runs to succeed .................................  1   outcome A
    correct while the reading is undeclared ........................  1   outcome C
FALSE ROUTES TO OUTCOME A CLOSED BY THIS PHASE ....................  4   of 5
```

### 12.8 Blockers, unknowns, residuals — carried, unchanged

```
BLOCKERS
    today, artifact level ..........................................  5   E-4A, E1-F3, E-3,
                                                                          RES-1, RES-2
    after governance + implementation ..............................  0
    introduced by this determination ...............................  0
    introduced across all 106 paths ................................  0

UNKNOWNS
    named .......................................................... 2    UK-1, UK-2
    components ..................................................... 10   6 + 4
    dischargeable without a mutating run ...........................  0
    closable by any of the 12 models ...............................  0

RESIDUALS ......................................................... 3    RES-3, RES-4, R-7w
    closed by execution ............................................  0
    reduced (evidence class only) ..................................  2   — and [MEASURED] §6.3,
                                                                          the reduction requires
                                                                          EV-25, which has NO
                                                                          PRODUCER.  The two
                                                                          reductions are therefore
                                                                          UNOBTAINABLE as specified
    unchanged ......................................................  1   R-7w
    latent today ...................................................  3
    closable by any admissible model ...............................  0

DEFECTS
    found by PHASE6 ................................................  4
    found by this phase ............................................  5   U-D … U-H
    closable by determination ..................................... 9 of 9
    governance-dependent among the five new ........................  0
```

**[INFERRED] One consequence of §6.3 that belongs in the residual count and has not appeared before.** `PHASE4:§G` records `RES-3` and `RES-4` as **REDUCED** by execution. **[MEASURED]** that reduction is evidenced by `EV-25` alone, and `EV-25` has no producer. So *"reduced"* is a prediction the program cannot currently confirm. The residual **count** is unchanged at 3, as every phase has said; what changes is that **2 of the 3 reductions are unobtainable as specified**, which makes `GA-5`'s residual acceptance the operative instrument for all three rather than for one.

---

## 13. Corrections to prior phases

Ten corrections and three count changes. Each is measured, and each is stated with what it changes for an implementer.

| # | Claim | Correction | Consequence |
|---|---|---|---|
| **1** | `PHASE6:§7.4` — **58** distinct paths from `EXECUTION-AUTHORIZED` | **[INFERRED]** `V-11` / `EV-22` is absent from the confirmation branch factors, although `PHASE6:§8.1` counts `T-1f` — a terminal state that depends on it. Restoring it as a 2-valued branch gives **82**; adding its false-pass channel (§5.3) gives **106** | Every per-path figure in `PHASE6:§7.5` is scaled. The structural results — 0 new blockers, all paths reachable, all authorized — survive |
| **2** | `PHASE6:§7.5` — **28** fully reversible / **30** semantically irreversible | **[INFERRED]** Under Phase 6's own criterion (*"any landed allocation"*) the figures do not decompose. 14 of each ordering's 18 base combinations land an allocation, giving **8** reversible and **50** irreversible over 58, and **8 / 98** over 106 | The reversible set is far smaller than reported and does not grow with the path count, because it contains no `A✓B✓` path |
| **3** | `PHASE6:§3.6`, §12.4 **P6-8** — *"`ukb._path_identity` returns early for every already-allocated path (`ukb.py:892-894`)"* | **[MEASURED]** **P7-11**: the line numbers are exact and the function name is wrong. `ukb.py:892-894` is inside **`allocate()`** (`:877`). **No function named `_path_identity` exists in `ukb.py`** | Documentary. The measured fact stands unchanged |
| **4** | `PHASE6:§3.6` — U-B has two closures, `C-1` and `C-2`, and `C-1` preserves the 2-authorization minimum | **[MEASURED]** §4.2: the re-run partitions into **three** manifest classes. `C-1` authorizes **M1 only** — in M2 the sentinel is refused by the **whole-document** check at `:698-707` (because `history` is in `NON_ALLOCATION_KEYS`, so a `history` append leaves `allocating=False` and `before != after`), and in M3 by the allocating check. `C-2` is structurally incomplete for M2 and M3 | `IA-4` must **dispatch at run time**, not carry a fixed value; `GA-9` gains a fourth content item; the 2-authorization minimum holds only in M1 |
| **5** | `PHASE6:§1.1` — U-B is *"a SPECIFICATION DEFECT"* | **[MEASURED]** §4.4: it is specification-, implementation- **and** model-dependent. The model-dependence is axis `D`, and it is what makes the primary question's seventh clause false under **6 of 12** models | U-B cannot be closed governance-independently in every model |
| **6** | `PHASE6:§6.6` **P6-6** — the lock guard has **7** behaviours | **[MEASURED]** **P7-5**: **10**. New: **H** (multi-line content → syntax error, then proceeds), **J** (unreadable lock → the `\|\| echo 0` fallback substitutes epoch 0, so an unreadable lock **never** no-ops), and **I** (age exactly 3600 s → proceeds; the boundary is strict `<`) | `EV-23`'s third discriminator — *"`.register.lock` verified absent"* — is necessary and, per state J, not sufficient: a present-but-unreadable lock does not no-op |
| **7** | `PHASE4:§I.2`, `PHASE5` `EV-14`, `PHASE6:§8.4` — the `by_object` population is *"not stable"* and grows 27 → 28 when the register is versioned | **[MEASURED]** **P7-6**, **P7-7**, **P7-8**: it is a function of the **git index**, its boundary is **every** cached path with **no extension filter and no exclusion list** (`measured=6804` = `git ls-files --cached`), and **the anonymous set is EQUAL, element for element, to the staged-new set** — 27 = 27, set difference **empty in both directions** | `EV-14`'s measurand is not a property of any commit; `UGA-INV-01 violations=0` is satisfiable with zero mints; a `git add` of **any file whatsoever** invalidates permit B on **two** bindings. This is `U-D` |
| **8** | `PHASE6:§6.1` **H-1** — eligibility is a property of the index, for `by_path` | **[MEASURED]** **P7-8**: it holds for `by_object` too, and **more widely** — `by_path` filters to 4 extensions and 13 excluded prefixes; `by_object` filters **nothing**. And **[MEASURED]** **P7-4**: **42** untracked files in this repository would become `by_path`-eligible on `git add`, not the two determination documents `H-2` names | The staging hazard is 21× larger than recorded, and `git add -A` takes the run-A population from **9** to **51** |
| **9** | `PHASE2:§C.1` **M2** — *"the three production actor strings (`ukb.py:1287`, `:2382`, `:2403`, `uga_engine.py:2098`)"* | **[MEASURED]** **P7-11**: the parenthesis names **four** sites and there are **four** distinct literals — `UMB-IMP-001 :: ukb.py build --mint`, `EXEC-REG-001 :: ukb.py exec declare (idempotent)`, `EXEC-REG-001 :: ukb.py exec declare`, `UCOS-UGA-001 :: uga_engine.py run` | Documentary. `M2`'s substance — unconstrained string equality, no allow-list — is unaffected |
| **10** | **Phases 0–6 collectively** — the completion definition is `TRANSACTION COMPLETE` | **[MEASURED]** **P7-10**: `register.sh:16` cites **`REG-AUTO-001` §7 Atomic Creation Law** as its authority for *"completion claims INVALID"*. That artifact exists at `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-REG-AUTO-001-…md`, is consumed by **no** phase, defines `T` as an **8-register** conjunction rather than the **10-phase** one, names **six** phases in its realization table, has **no** vocabulary for a transaction that did not run, and states a §8 invariant that is **violated today by exactly 9** | This is `U-F`. A transaction can be INCOMPLETE by `CD-1` and COMPLETE by `CD-19` — e.g. a `ukbx certify` failure — and nothing in the chain adjudicates |

**Three count changes.**

| Count | Prior | Phase 7 | Basis |
|---|---|---|---|
| Distinct paths from `EXECUTION-AUTHORIZED` | **58** (Phase 6) | **106** | §9.2 |
| Unproducible evidence items | **2** (Phase 6) | **3** | §6.3 — `EV-25` |
| Fully reversible paths | **28** of 58 (Phase 6) | **8** of 106 | §9.5 |

**What was confirmed rather than corrected.**

| Confirmed | Basis |
|---|---|
| The `by_path` gap is **9**, and the same nine files | **[MEASURED]** **P7-3**, in-process through `ukb._iter_files()`: eligible **1606**, registered **1597**, `eligible ∩ by_path` = **1597** = `artifacts.json` count exactly |
| All nine are **committed and clean**, so `UK-1`'s population is a property of HEAD and stable under index operations | **[MEASURED]** **P7-3b** — the sharp contrast with `UK-2`'s index-derived population |
| The invariant surface is **30**, with `UGA-INV-01` and `UGA-INV-10` at **27** violations over identical sets | **[MEASURED]** **P7-6**, re-run this phase. `PHASE4` **P4-4** confirmed without amendment |
| **4 strict / 5 elective** permit bindings; `single_use` dead; `expires_at` producer-less | **[MEASURED]** **P7-11**. `PHASE6` **P6-1**, **P6-2** confirmed |
| The conditional-`NO_ALLOCATION` pattern exists at `ukb.py:2380-2384`, verbatim | **[MEASURED]** **P7-11**, with the comment *"correct HERE BY CONSTRUCTION, not by assumption"* |
| `--observe` returns at `:178`, before the lock guard — the read-only plane is structurally immune to U-C | **[MEASURED]** **P7-12**, and it is the finding that **bounds** U-C rather than widening it |
| `EV-25` is correctly **scoped** by Phases 4 and 5 — it names R-7's document comparison, not R-7w's window | **[MEASURED]** §6.3. Its defect is an absent producer, not overreach |
| `PHASE4:§G.3`'s claim that `R-7w` is a failure-path property | **[MEASURED]** re-derived here as the second premise of §8.4's emptiness proof |
| No path produces a new blocker | **[INFERRED]** confirmed across **106**, a third independent resolution after Phase 4's and Phase 6's |
| The 12 admissible models, the 13 forced tasks, the 2-run minimum, the disjoint populations, the 14-condition gate, the 4 rollback procedures, the 3 residuals | Every one re-checked against §§3–11 and unaffected |

---

## 14. Stop condition

### 14.1 The determinations

- **Q1 — 35 completion definitions**, 17 machine-enforced, 4 contradictory pairs, 6 claimed sufficient and **0 actually sufficient**. The definition `register.sh` names as its own authority is consumed by no phase in the chain.
- **Q2 — U-B's root cause is that the authority has two admission modes and the re-run needs a third.** That third mode is axis `D`'s subject, and `IA-4` was specified without reference to axis `D`. The re-run partitions into **3** manifest classes; Phase 6's `C-1` authorizes **1**. **7** closure classes enumerated, **0** recommended. U-B is specification-, implementation- **and** model-dependent.
- **Q3 — 4 reachable false-positive and 6 false-negative completion states**, from **10** measured lock states and three non-lock channels. **8** minimum discriminating evidence items. **0** redundant, **7** non-discriminating, **1** tautological. **6** closure classes for U-C, all governance-independent.
- **Q4 — 27 evidence items: 9 SAFE, 4 UNSAFE, 6 UNPROVEN, 1 TAUTOLOGICAL, 7 NON-DISCRIMINATING.** **3** unproducible. The evidence base splits on one property: **digests and version-control predicates are sound; transcripts are not.**
- **Q5 — 0 of 12 models reach complete authorization accounting.** 72 cells: 18 COMPLETE, 42 PARTIAL, 12 AMBIGUOUS. The one dimension complete everywhere is the one that **records nothing**.
- **Q6 — the five terminal states are pairwise non-equivalent, with 6 measured separating conditions.** Two of the five names have no referent anywhere. `EXECUTION-CERTIFIED(b)` is **provably empty**.
- **Q7 — 106 paths**, correcting **58**. **12** reach completion under one definition, **8** under the other, **2** genuinely, **0** on the package as specified, **0** evidence-valid.
- **Q8 — closure of U-B and U-C is NOT sufficient.** Seven items remain; five are new and none is governance-dependent. Closing all seven reduces the set to exactly `{UK-1, UK-2}`, proved by exhaustion over six enumerated surfaces.
- **Q9 — all three Phase-9 outcomes remain reachable.** Outcome **B is provable today with zero runs** under the residual-freedom reading. Outcome **A** is hostage to `U-A`. Outcome **C** is correct while the reading is undeclared. Phase 7 removes no outcome; it closes **4 of 5** false routes to A.

### 14.2 The hypothesis, answered

> **Closing U-B and U-C leaves only execution-time unknowns (UK-1 and UK-2) between EXECUTION-AUTHORIZED and a terminal Phase-9 proof.**

```
================================================================================
                            F A L S I F I E D
================================================================================

  Closing U-B and U-C leaves SEVEN items, not two:

      UK-1 · UK-2       execution-time, irreducible          CARRIED
      U-D               the by_object population is a        NEW, MEASURED
                        function of the git index, and the
                        anonymous set is EQUAL to the
                        staged-new set (27 = 27, both
                        set differences empty)
      U-E               two non-equivalent definitions of    NEW, MEASURED
                        the terminal state, worth 4 paths
      U-F               the constitutional completion law    NEW, MEASURED
                        is unconsumed, non-equivalent,
                        stale by four phases, has no term
                        for "did not run", and states an
                        invariant violated today by 9
      U-G               EV-1 / EV-24 bind a count, not a set NEW, INFERRED
      U-H               the sentinel path is unattributable, NEW, MEASURED
                        and PHASE6's own closure C-1 routes
                        the program's third authorization
                        event through it

  All five are closable by determination.  NONE is governance-dependent.
  NONE is an execution-time unknown.

  ── THE REFINED STATEMENT, WHICH THIS PHASE STRENGTHENS ────────────────────

  Closing U-B, U-C, U-D, U-E, U-F, U-G and U-H leaves ONLY UK-1 and UK-2 —
  proved in §10.4 by exhaustion over the six enumerated surfaces:
  35 definitions · 27 evidence items · 72 accounting cells · 10 lock states ·
  106 paths · 5 terminal-state names.

  That proof is exhaustive OVER THOSE SURFACES.  It is not a proof that no
  seventh surface exists, and the chain's own record — 14 hidden dependencies
  found by PHASE6, 5 further defects found here, one of them created by
  PHASE6's own remedy — argues that a PHASE8 at this resolution should expect
  to find between one and three more.  The rate is falling and the character
  has changed from mechanical to definitional, which is what convergence looks
  like.  It is not zero.
================================================================================
```

### 14.3 Constraint compliance

- **Determination only.** No implementation, no design, no task content. §§3–11 determine; they do not propose.
- **Governance selected: NONE.** Decisions taken: **0**. Models or axis values recommended, ranked or preferred: **0**. Where a defect admits several closures — **7** for U-B, **6** for U-C — every one is stated with its cost and **none is preferred**. Where two readings of a term are live — `EXECUTION-CERTIFIED`, *"unconditional ready"* — both are stated and neither is adopted.
- **Permits issued: 0. Register created: no.** `00-BOOK/DATA/allocation-permits.json` re-verified absent at the open and close of this phase.
- **Mutating runs: 0.** `register.sh` **not invoked in any mode, including `--observe`**. `ukb build --mint` not invoked, **including `--plan`**. `uga_engine run` not invoked in any mode. `pytest` not invoked. The single command run against this repository was `uga_engine.py gate`, whose docstring declares *"Verify without mutating"* and whose read-only character was re-measured here rather than assumed.
- **Repository modification: NONE.** This document is the only addition, and it is untracked, therefore `by_path`-ineligible, therefore perturbing no population — the same property **P7-3** measures for all eight inputs.
- **Recommendations: 0.** Every `[EXEC-REQ]` in this document states a requirement the package's own success criteria already imply. None proposes a design.
- **New governance assumptions: 0.** Every governance fact is cited to `PHASE2:§D.3` or `PHASE3:§A`. §4.4 and §10.2 **identify** where the package introduces a governance dependency and decline to resolve it.

### 14.4 Evidence — the thirteen probes

**No probe invoked `register.sh` in any mode, `ukb` in any mode, `uga_engine run` in any mode, or `pytest`.** **P7-5** ran in a scratch directory outside this repository, created and destroyed within this phase.

| ID | Established | Method | Repository touched |
|---|---|---|---|
| **P7-1** | Baseline unmoved: ledger `sha256 8471e709…c20b`, HEAD `77798202`, four guard dirs **0** dirty, register **absent**, lock **absent**, `.runtime` **612 / 19 / 1**, `git ls-files --cached` **6804** | `shasum`, `git status --porcelain`, `git rev-parse`, `ls`, JSON read of `.runtime/governance/*.json` | read-only |
| **P7-2** | **The ledger is at its snapshot fixed point** — 0 drift on `content_hash` / `status` / `path` / `name` across all **1597** projected artifacts; the 36 `version` differences are the raw-token-vs-semver distinction `ukb.py:983` creates. So a re-run appends nothing to `history` today, and manifest class **M1** obtains | in-process comparison of `id-ledger.json["history"][uid][-1]` against `artifacts.json` | read-only |
| **P7-3** | Eligibility **1606**, registered **1597**, `eligible ∩ by_path` **1597**, **by_path gap 9** with the nine names enumerated; `EXCLUDE_DIR_PREFIXES` **13**, `INCLUDE_EXTENSIONS` **4**; and (**P7-3b**) all nine gap files are **committed and clean** | `ukb._iter_files()` called in-process; `git cat-file -e HEAD:<f>`; `git status --porcelain -- <f>` | read-only |
| **P7-4** | **42** untracked files would become `by_path`-eligible on `git add`; **47** untracked entries total; all eight input documents are `??` and therefore ineligible. Re-measured after this document was written: **43** — this document is the 43rd, which is itself the demonstration that the population grows with the chain that measures it | `git status --porcelain` filtered through `config.EXCLUDE_DIR_PREFIXES` and `INCLUDE_EXTENSIONS` | read-only |
| **P7-5** | **10 lock states**, each with exit code, transaction-runs flag and stderr — including three not in `PHASE6` **P6-6** (multi-line, unreadable, and the exact-3600 boundary) | `register.sh:187-192`'s arithmetic reproduced verbatim under `bash -euo pipefail`, with the lock age computed at each invocation so no timing race distorts the boundary | **no** — a scratch directory outside this repository, since removed |
| **P7-6** | **30** invariants; `UGA-INV-01 FAIL violations=27 measured=6804`; `UGA-INV-10 FAIL violations=27 measured=5207`; `GATE FAILED — 2 blocking`; **and the run is read-only** — ledger `sha256` and all three `.runtime` logs byte-identical before and after | `python3 00-MASTER/UCOS-UGA-001/uga_engine.py gate`, bracketed by `shasum` of the ledger and of `.runtime/governance/*.json` | **read-only, verified** |
| **P7-7** | **The anonymous set is EQUAL to the staged-new set**: `\|anonymous\| = 27`, `\|{A-status}\| = 27`, `anonymous \ staged = ∅`, `staged \ anonymous = ∅`. Full list enumerated | `uga.build(mint=False)` in-process against `git status --porcelain` | read-only |
| **P7-8** | The `by_object` boundary is `git ls-files -z --cached` — the index, over **every** path, **no** extension filter, **no** exclusion list. `measured=6804` = `git ls-files --cached \| wc -l` exactly | source read `uga_engine.py:178-193`; `git ls-files --cached \| wc -l` | read-only |
| **P7-9** | Terminal-state vocabulary counts: `EXECUTION-AUTHORIZED` 36 · `READY-FOR-EXECUTION` 40 · `EXECUTION-COMPLETE` 14 · `EXECUTION-COMPLETED` 11 · `EXECUTION-CERTIFIED` 5 · **`EXECUTION-SUCCESSFUL` 0 · `EXECUTION-VERIFIED` 0**; and **0** occurrences of any of the seven in the source tree | `grep -c` over the eight inputs; `grep -rn` over `00-BOOK/tools`, `00-MASTER/UCOS-UGA-001`, `engine/`, `platform/` | read-only |
| **P7-10** | `REG-AUTO-001` §7's eight-component `T`; §7's **six**-phase realization table; §5 **P3**'s idempotence law; `:126`'s *"a no-op that re-proves synchronization"*; §8's `count(artifacts.json)` invariant | source read of `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-REG-AUTO-001-AUTOMATIC-ARTIFACT-REGISTRATION-STANDARD.md` | read-only |
| **P7-11** | **`ledger_authority.py` contains ZERO `print` / `logging` / `logger` statements**; `single_use` occurs **0** times; **4** actor literals across **5** sites; **3** `--permit` CLI flags; **1** `NO_ALLOCATION` call site at `ukb.py:2384`; `ukb.py:892-894` is inside `allocate()` and no `_path_identity` exists; `_actor` is bound once at `ukb.py:1287` and shared by `plan()` and `commit()` | source read and `grep` over `ledger_authority.py`, `ukb.py`, `uga_engine.py`, `platform/tests/test_ledger_authority.py` | read-only |
| **P7-12** | `register.sh` has exactly **2** live invocations in the repository, **both `--observe`** (`verify.sh:799`, `.github/workflows/ucos-registration-gate.yml:60`); **0** live `--guard` invocations; `--observe` returns at `:178`, nine lines before the guard at `:187` | `grep -rn` over `*.yml`, `*.sh`, `Makefile`, `*.py`; source read `register.sh:99-195` | read-only |
| **P7-13** | `addopts` = `-ra --strict-markers -p engine.universal_discovery.pytest_scope --cov-report=term-missing --cov-report=xml --cov-fail-under=90`; `coverage.xml` **present and gitignored** (`.gitignore:29`); interpreters **3.14.4** system / **3.12.13** `.ec1-venv`; installed pre-commit hook is `ucos_ruff_gate`, `core.hooksPath` unset | source read `pyproject.toml`, `.gitignore`, `.git/hooks/pre-commit`; `git config --get core.hooksPath` | read-only |

**Non-mutation, verified at the open and the close of this phase:**

```
$ shasum -a 256 00-BOOK/DATA/id-ledger.json
8471e709b178a9a09909bca55f2e8eccb78161db8423026d1d26e4f35c41c20b        (unchanged)
$ git rev-parse --short HEAD
77798202                                                                (unchanged)
$ git status --porcelain -- 00-BOOK/DATA 00-BOOK/REGISTRIES 00-BOOK/CONTROL-TOWER 00-BOOK/PORTAL
(0 lines)
$ ls 00-BOOK/DATA/allocation-permits.json      -> No such file or directory
$ ls 00-BOOK/tools/.register.lock              -> No such file or directory
$ .runtime/governance   enforcement 612 · sync 19 · certification 1     (unmoved)
$ git ls-files --cached | wc -l                -> 6804                  (unchanged)
```

### 14.5 The terminal position

```
POSITION ................. READY-CONDITIONAL-ON-GOVERNANCE-SELECTION   (unchanged)
AUTHORIZATION STATE ...... NOT-AUTHORIZABLE                            (unchanged)
PACKAGE STATUS ........... INCOMPLETE — 42 artifacts, 3 unsatisfied edges,
                           3 unproducible evidence items (was 2)
BLOCKERS ................. 5 artifact-level · 0 introduced
UNKNOWNS ................. 2, comprising 10 components, 2 unreachable
RESIDUALS ................ 3, all latent · 0 closable by any model
                           and 2 of the 3 REDUCTIONS are unobtainable, because
                           EV-25 has no producer
DEFECTS .................. 9 total — 4 from PHASE6, 5 new here
DEFECTS CLOSABLE BY DETERMINATION ... 9 of 9
GOVERNANCE-DEPENDENT AMONG THE 5 NEW  0
UNCERTAINTY IRREDUCIBLE BY DETERMINATION ... 1   U-A: the outcome of the runs
PHASE-9 OUTCOMES REACHABLE ... 3 of 3, one of them provable today at zero cost
```

**What this phase adds to the next act.** The next act is unchanged: `GA-1`, a governance decision on the five closure axes, followed by implementation, versioning, Stage 0, and then `GA-7` — the one artifact no phase of this chain can produce for itself. What Phase 6 added was that four specification defects should be closed first, all of them governance-independent. **What Phase 7 adds is that there are nine, that five of them were invisible until now, that one of the nine was created by Phase 6's own proposed remedy — and that one of the three Phase-9 outcomes can be decided today, deductively, for the cost of a determination and no runs at all.**

Phase 7 ends here.
