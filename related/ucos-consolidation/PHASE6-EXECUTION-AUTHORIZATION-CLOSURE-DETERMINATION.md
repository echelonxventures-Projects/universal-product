# PHASE 6 — EXECUTION AUTHORIZATION CLOSURE DETERMINATION

| Field | Value |
|---|---|
| Question | After governance selection, implementation, authorization and validation are complete, does any remaining **non-governance** uncertainty prevent execution completion from being a fully determined process? |
| Answer | **YES — three remain, and two of them are specification defects rather than unknowns.** (i) **UK-1/UK-2 are irreducibly unmeasurable before the runs** — carried, four of `register.sh`'s ten phases have no dry-run mode. (ii) **NEW: the second `register.sh` run cannot be authorized by the package as specified** — the run-1 permit fails **two** bindings on the re-run, so **EV-23 / UK-1 closure item 5 is unproducible**. (iii) **NEW: `register.sh` has a measured path that exits 0 having done nothing**, so EV-23 can *falsely pass* and UK-1 can be *falsely retired*. (ii) and (iii) are closable by determination; §3.6 and §8.4 specify exactly how. |
| Is the Phase 5 package complete? | **NO.** 1 missing artifact, 1 under-specified artifact, 1 unproducible evidence item, 1 produced-but-unconsumed field. §3.7. |
| Internally consistent? | **YES**, with 3 stale or over-strong claims corrected — §12.3. No inconsistency changes a count in Phase 5 §J except the two identified in §10.4. |
| Minimal? | **NO — it is 7× larger than the mechanical minimum, and correctly so.** Minimum to execute one run is **6** artifacts; minimum to be *authorized, determinate and recoverable* is **42**. The gap is the gate. §5.6. |
| Sufficient? | **NO.** All 14 gate conditions can hold while execution remains impossible (§4.4), and 12 of the 14 are **unenforceable by the machine** (§4.3). |
| Inputs | `PHASE0-GOVERNANCE-INDEPENDENT-DETERMINATION.md`, `PHASE05-GOVERNANCE-INDEPENDENT-REMEDIATION.md`, `PHASE1-GOVERNANCE-INDEPENDENT-IMPLEMENTATION-REPORT.md`, `PHASE2-GOVERNANCE-CLOSURE-DETERMINATION.md`, `PHASE3-IMPLEMENTATION-READINESS-DETERMINATION.md`, `PHASE4-EXECUTION-VALIDATION-DETERMINATION.md`, `PHASE5-EXECUTION-TRANSITION-DETERMINATION.md` |
| Governance selected | **NONE.** No axis assigned. Six axis-parameterized items are stated per value; the sixth is new — §6.8. |
| Permits issued · register created · mutating runs | **0 · 0 · 0.** `register.sh` was not invoked in any mode. `uga_engine run --mint` was not invoked. |
| Repository files modified | **NONE.** This document is the only addition. Ledger `sha256 8471e709…c20b`; four guard directories 0 dirty; register absent; `.runtime` sequences unmoved at **612 / 19 / 1**. |
| Probes | **12** — `P6-1 … P6-12`. Two reproduced in isolated `/tmp` scratch directories created and destroyed within this phase. |

### Compliance with the stated constraints

| # | Constraint | Compliance |
|---|---|---|
| 1 | No governance selection | No axis assigned. All results quantified over the 12 admissible models. |
| 2 | No implementation changes | No source file modified. |
| 3 | No permit issuance | No permit constructed, written or verified against a live manifest. |
| 4 | No register creation | `00-BOOK/DATA/allocation-permits.json` still absent — re-verified (**P6-12**). |
| 5 | No mutating execution of `register.sh` | **Not invoked at all** — not in transaction mode, not `--observe`, not `--guard`. §6.6's findings are from a full source read plus an isolated reproduction of the guard's shell arithmetic in `/tmp`. |
| 6 | No mutating execution of `uga_engine.py run --mint` | Not invoked. `--plan` also not invoked. |
| 7 | No repository modifications | This document only. **[MEASURED]** `pytest` deliberately **not** run: `addopts` includes `--cov-report=xml`, which writes `coverage.xml` (**P6-9**). |
| 8 | No recommendations | None. Where a defect admits two remedies, both are stated without preference (§3.6). No model preferred. |
| 9 | Determination only | The scope of §3–§11. |

---

## 1. Executive determination

### 1.1 The headline

```
================================================================================
  DOES NON-GOVERNANCE UNCERTAINTY PREVENT EXECUTION COMPLETION
  FROM BEING A FULLY DETERMINED PROCESS?                               Y E S
================================================================================

  THREE uncertainties remain.  Only ONE is irreducible.

  U-A  IRREDUCIBLE — UK-1 and UK-2 cannot be measured before the runs.
       [MEASURED] --plan exists on `ukb build` and `uga_engine run` and NOWHERE
       in ukbx.py, so register.sh phases 2, 3, 4 and 8 have no dry-run mode at
       all (PHASE4 P4-6).  No determination closes this.  Carried unchanged.

  U-B  SPECIFICATION DEFECT — the SECOND register.sh run is unauthorizable.
       [MEASURED, new] On a re-run, ukb._path_identity returns early for every
       already-allocated path (ukb.py:892-894), so the manifest is
       allocating=False, total_allocations=0, allocated={}.  The run-1 permit
       therefore fails TWO strict bindings: manifest_digest (:735) and
       preimage_digest (:743).  Only NO_ALLOCATION authorizes the re-run.
       IA-4 as specified in PHASE3 §C.0 is a STATIC plumbing and cannot supply it.
       => EV-23 is UNPRODUCIBLE => UK-1 closure item 5 is UNREACHABLE.

  U-C  SPECIFICATION DEFECT — execution completion can be FALSELY REPORTED.
       [MEASURED, new] register.sh:187-192 exits 0 having run nothing when a
       lock file younger than 3600 s exists.  Reproduced in 6 cases (P6-6).
       EV-23's success condition is "zero byte changes", which a run that never
       happened satisfies trivially.  Run A is protected because UK-1 item 3
       demands the exact TRANSACTION COMPLETE line; item 5 demands no such thing.
       => UK-1 can be retired on evidence that measured nothing.

  U-B and U-C are CLOSABLE BY DETERMINATION.  They are defects in the package,
  not gaps in knowledge.  §3.6 and §8.4 state the exact closures.
  U-A is not closable by anything except the runs.
================================================================================
```

### 1.2 The eight questions, answered in one line each

| Q | Answer |
|---|---|
| **Q1 Completeness** | **NO.** 1 artifact missing (`IA-12`, the issuer field-election record), 1 under-specified (`IA-4`), 1 evidence item unproducible by its named method (`EV-1`), 1 field produced but never consumed (`single_use`). §3.7 |
| **Q2 Sufficiency** | **NO.** 0 of 14 conditions are sufficient; **2** are necessary for the mechanical act (`G-7`, `G-14`); **12** are unenforceable by the machine. A gate can pass while execution is impossible **and** fail while execution remains possible. §4 |
| **Q3 Minimality** | **NO**, deliberately. One-run minimum **6**; both-runs **10**; unknowns-retired **33**; full package **42** (41 + `IA-12`). **32 of 42** items have **no** execution-impossibility consequence — they buy determinacy, rollback safety or the ability to retire an unknown. §5 |
| **Q4 Hidden dependencies** | **14 found**, all reproduced and measured: 9 consequential, 5 checked-and-benign. §6 |
| **Q5 Path enumeration** | **36** paths from EXECUTION-AUTHORIZED; **6** run-A outcome classes (Phase 4 had 3); **2** genuine completion paths and **2** false-completion paths. §7 |
| **Q6 Terminal states** | **17** reachable after authorization. **1** falsely appears successful, **2** falsely appear failed, **3** leave hidden damage, **11** leave authorization consumed. §8 |
| **Q7 Unknown closure** | UK-1: 5 items, **item 5 currently unreachable**; earliest measurability at the second run. UK-2: 4 items, and **UK-2 alone is resolvable from a failure path** — a negative answer is an answer. §9 |
| **Q8 Readiness** | 4 of 6 states reachable. `EXECUTION-COMPLETED` reachable in principle but **not on the package as specified**. `EXECUTION-CERTIFIED` is **undefined by every artifact in the chain** — itself a finding. §11 |

### 1.3 What this phase did not find

Stated first, because a review phase that reports only defects is not credible.

**[MEASURED]** Five candidate hazards were probed and are **benign**:

| Checked | Result |
|---|---|
| The program runs under **two different Python interpreters** — `register.sh` uses system `python3` **3.14.4**, the test suite uses `.ec1-venv` **3.12.13** | **BENIGN — measured.** `preimage_digest` is byte-identical under both: `3a2a2532e006c326…`, canonical length **1 790 825** under each (**P6-4**). The permit bindings are interpreter-invariant. |
| `plan()` might emit an abbreviated `head`, creating a transcription hazard | **BENIGN.** `ukb.py:1293-1297` prints the **full** 40-char sha. Phase 4's `head 77798202` was Phase 4's own prose abbreviation, not the tool's output (**P6-11**). |
| The determination documents at the repository root might grow the `by_path` population | **BENIGN while untracked.** Eligibility is `git ls-files --cached`; every determination document is `??` (**P6-3**). |
| `pytest`'s side effects might create drift | **BENIGN.** `.coverage*` and `coverage.xml` are both gitignored (`.gitignore:28-29`) (**P6-9**). |
| `.register.lock` might read as registration drift | **BENIGN, doubly.** `00-BOOK/tools/` is in `EXCLUDE_DIR_PREFIXES` **and** the lock is in `.gitignore:3`; the script's own comment states it lives there *"outside the scan and the guard set"* (**P6-6**). |

**[INFERRED]** Phase 4's and Phase 5's **structural** results all survive this audit: the 2-mutating-run minimum, the disjointness of the two populations, the read-only character of Stage 0, the per-run and state-bound nature of the authorization, and the 14-condition gate. Nothing in §3–§11 overturns them. What §3–§11 overturn are **four specific factual claims** and **two counts** — enumerated in §12.3.

---

## 2. Inputs

### 2.1 The seven input documents

| Document | What Phase 6 consumes from it |
|---|---|
`PHASE0-GOVERNANCE-INDEPENDENT-DETERMINATION.md` | The blocker namespace `E-1`, `E-2`, `E-3`, `E-4A`; the 15→3 reduction frame |
`PHASE05-GOVERNANCE-INDEPENDENT-REMEDIATION.md` | `§E.0`'s **verified** pytest invocation — the basis of §6.11; `§F.4`'s residual bounding by authorization scope |
`PHASE1-GOVERNANCE-INDEPENDENT-IMPLEMENTATION-REPORT.md` | `§R-7`'s five byte-identity restore tests; `§R-11`'s serializer inequality; the 77-test baseline |
`PHASE2-GOVERNANCE-CLOSURE-DETERMINATION.md` | The 5 axes, 12 admissible models, `CX-1…CX-6`, `CY-1…CY-3`, `NB-1…NB-6`, merges `M1…M5` |
`PHASE3-IMPLEMENTATION-READINESS-DETERMINATION.md` | The 24-task register, 13 forced, `F-1…F-13` / `O-1…O-11`; **and the claim §6.4 corrects** |
`PHASE4-EXECUTION-VALIDATION-DETERMINATION.md` | `V-1…V-14`; edges `E-1…E-7`; `T-0…T-9`; `R-A…R-C`; UK-1's 5 and UK-2's 4 closure items |
`PHASE5-EXECUTION-TRANSITION-DETERMINATION.md` | `GA-1…GA-9`, `IA-1…IA-11`, `EV-1…EV-27`, `G-1…G-14`, `S-0…S-9`, `R-D`, `X-1…X-4`; the object under audit |

### 2.2 Source read this phase

Every line reference below was read against the current tree at `77798202`.

| Reference | Content established |
|---|---|
| `ledger_authority.py:437-478` | `format_report` — the operator-facing line; renders `bytes_changed` only when present |
| `:536-548` | `_canonical` — `sort_keys=True`, `separators=(",",":")`, `ensure_ascii=False`; *"no wall clock"* |
| `:550-568` | `manifest_digest` — six named inputs; docstring: *"Deliberately excludes `head`, `preimage_digest`, `issued_at`"* |
| `:570-577` | `preimage_digest` — *"spent-ness is DERIVED from two artifacts that are already committed"* |
| `:580-598` | **`git_head`** — `git -C <dir> rev-parse HEAD`, `timeout=15`, `None` on `OSError`/`SubprocessError`/non-zero |
| `:601-631` | `permit_register_path`; `load_permit_register` — **missing register = EMPTY register, not an error**; fail-closed on unparseable; refuses to guess the shape |
| `:634-648` | `build_manifest` — *"THE measurement. `plan()` and `commit()` both call this and nothing else"*; sets `head` via `git_head` |
| `:650-662` | `plan()` — *"The returned manifest carries `digest`, `preimage_digest` and `head` — **exactly the three bindings a permit must quote**"* |
| `:664-707` | `_verify_permit`'s `NO_ALLOCATION` branch — refuses if `allocating`; then requires `before == after` (R-9) |
| **`:709-804`** | The permit path: **4 strict bindings, 5 elective** — §6.4 |
| `:825-838` | `_refuse_unmoved_allocation` — fires on `allocating and bytes_changed is False` |
| **`:841-933`** | `commit()` — the full ordering; **8 refusal points, 4 before the writer and 4 after** — §7.2 |
| `ukb.py:722-733`, `:790-800` | `_git_ls`; `git ls-files --others --exclude-standard`; `EligibilityBoundaryError` on failure |
| `ukb.py:802-845` | `_iter_files_walk` (degraded off-VCS fallback); **`_iter_files` — eligibility is `git ls-files --cached`, "tracked or staged"** |
| **`ukb.py:885-913`** | `_path_identity` — **`if entry: return …` — an already-allocated path allocates nothing and calls no clock** |
| `ukb.py:1286-1299` | The `--plan` block: `manifest_digest`, `preimage_digest`, **full** `head`, `PLAN ONLY`; actor literal `UMB-IMP-001 :: ukb.py build --mint` |
| `config.py:885-897` | **`EXCLUDE_DIR_PREFIXES`** — 13 entries, including `00-MASTER/` and `.kiro/` |
| `config.py:942` | **`INCLUDE_EXTENSIONS = (".md", ".txt", ".docx", ".json")`** |
| `governance_telemetry.py:187-207` | `forbid_data_telemetry` — `*-audit.json` under `00-BOOK/DATA` raises `TelemetryPathError` |
| `register.sh:178-192` | **The re-entrancy guard — `exit 0` on a lock younger than 3600 s** |
| `register.sh:99-176`, `:206-273` | The `--observe` plane; the ten phases; **the transaction itself performs NO drift check** |
| `uga_engine.py:2073-2100` | `cmd_run` — the `--plan` block; actor literal `UCOS-UGA-001 :: uga_engine.py run` |
| `platform/tests/test_ledger_authority.py` `_issue` | **The register's only writer** — 8 keys incl. `single_use: True` and `expires_at: None` |
| `pyproject.toml` `[tool.pytest.ini_options]` | `addopts` = `-p engine.universal_discovery.pytest_scope`, `--cov-report=xml`, `--cov-fail-under=90` |
| `.gitignore:3`, `:12`, `:28-29` | `.register.lock`; `.runtime/`; `.coverage*`, `coverage.xml` |

### 2.3 Evidence classes

| Tag | Meaning |
|---|---|
| **[MEASURED]** | Established by execution or source read **this phase**, or by a named prior-phase probe. |
| **[INFERRED]** | Derived from measured facts by an argument stated at the point of use. |
| **[UNKNOWN]** | Not established, and stated as such. |
| **[GOV-REQ]** | A requirement satisfiable only by a decision. |
| **[EXEC-REQ]** | A requirement satisfiable only by an act. |
| **[DEFECT]** | **New in this phase.** A specification defect in the transition package: an artifact, evidence item or condition that cannot do the job assigned to it. Distinct from an unknown — closable by determination. |

---

## 3. Dependency graph — Q1 Completeness

### 3.1 The producer → consumer graph

Read `X ──▶ Y` as *"X produces something Y consumes"*. Every edge is labelled with the object that crosses it.

```
  ┌──────────────────────────── GOVERNANCE (S-0) ────────────────────────────┐
  │                                                                           │
  │  GA-1 ─ 5 axis values ─┬──▶ IA-1   (which of 17-20 tasks to specify)      │
  │                        ├──▶ GA-9   (V-11 target · R-B scope · replay)     │
  │                        └──▶ GA-3   (is this one of the 12?)               │
  │  GA-2 ─ B2a|B2b ───────────▶ R-B   (rollback scope)                       │
  │       ─ R modifier ────────▶ GA-3                                          │
  │  GA-4 ─ 12|24 reading ─────▶ GA-1  (which admissible set)                 │
  │  GA-5 ─ residual acceptance ──▶ (nothing mechanical)      ◀── see §3.4    │
  │  GA-6 ─ UK closure sets ───▶ EV-17, EV-22, EV-23                          │
  │  GA-7 ─ mutation authorization ──▶ (nothing mechanical)   ◀── see §3.4    │
  │  GA-8 ─ rollback pre-auth ─▶ R-A, R-B, R-C, R-D                           │
  └───────────────────────────────────────────────────────────────────────────┘
                                     │
  ┌──────────────────────── IMPLEMENTATION (S-1) ────────────────────────────┐
  │  IA-1 ─ per-unit design ──▶ IA-2 … IA-11                                  │
  │  IA-2  ledger_authority.py (A3) ──▶ manifest_digest values ──▶ EV-3, EV-12│
  │  IA-3  the REGISTER ──────────────▶ load_permit_register :608-631         │
  │  IA-4  permit plumbing ───────────▶ ukb.py:1299 `permit=` argument        │
  │  IA-5  uga_engine.py:1331-1335 ───▶ EV-22 (UGA-INV-10 disposition)        │
  │  IA-6  uga-declaration.json ──────▶ EV-22 (declared surface 30|29)        │
  │  IA-7  claim amendments ──────────▶ (nothing mechanical)                  │
  │  IA-8  58-file citations ─────────▶ (nothing mechanical)                  │
  │  IA-9  test suite ────────────────▶ EV-1, EV-24                           │
  │  IA-10 invariant disposal test ───▶ EV-1, EV-24                           │
  │  IA-11 Aud1 log | B2b record ─────▶ EV-14 (population) · R-B · §6.7       │
  │  IA-C1 register staged ───────────▶ EV-2, EV-9, EV-21                     │
  │  IA-C2 ledger_authority committed ▶ EV-10, R-A safety                     │
  └───────────────────────────────────────────────────────────────────────────┘
                                     │
  ┌───────────────────── EVIDENCE + ISSUANCE (S-3, S-5, S-7) ─────────────────┐
  │  EV-3  plan A ──┬─ manifest_digest ─┐                                     │
  │                 ├─ preimage_digest ─┼──▶ EV-11 (permit A)                 │
  │                 ├─ head ────────────┤        │                            │
  │                 └─ allocated/total ─┘        │                            │
  │  ukb.py:1287 ─── actor literal ─────────────▶│   ◀── §3.5: NO PRODUCER    │
  │  ??? ─── head|scope|expires elections ──────▶│   ◀── §3.5: NO PRODUCER    │
  │                                              ▼                            │
  │  EV-11 ──▶ _verify_permit (9 reads, 4 strict) ──▶ run A authorized        │
  │  EV-12 plan B + uga_engine.py:2079 actor ──▶ EV-15 (permit B)             │
  │  EV-13 gate baseline ──────────────────────▶ EV-22 ("no V-5 pass regressed")│
  │  EV-14 re-measured population ─────────────▶ EV-15 scope.max_allocations  │
  │  EV-16 re-measured pre-image ──────────────▶ EV-15 preimage_digest        │
  │  EV-6, EV-7 ───────────────────────────────▶ EV-19, EV-26, EV-27 (deltas) │
  │  EV-8 destination ─────────────────────────▶ EV-17, EV-18 (where written) │
  │  EV-18 diff ───────────────────────────────▶ R-A (what to restore)        │
  │  ??? ─── re-run authorization ─────────────▶ EV-23   ◀── §3.6: NO PRODUCER│
  └───────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Edge count and closure

```
PRODUCER -> CONSUMER EDGES ......................................... 38
    governance -> implementation ...................................  4
    governance -> rollback .........................................  5
    governance -> evidence .........................................  3
    implementation -> implementation ...............................  1   (IA-1 -> IA-2..IA-11)
    implementation -> evidence ..................................... 10
    evidence -> evidence ........................................... 11
    evidence -> authority (machine-checked) ........................  2   EV-11, EV-15
    evidence -> rollback ...........................................  2   EV-18 -> R-A; EV-8
    UNSATISFIED EDGES (consumer with no producer) ..................  3   §3.5, §3.6
```

### 3.3 Consumed but never produced — three findings

| # | Consumed by | Object | Producer in the package | Class |
|---|---|---|---|---|
| **1** | `EV-11`, `EV-15` | the two **actor literals** | **NONE** | **[DEFECT]** |
| **2** | `EV-11`, `EV-15` | the **election** of `head` / `scope` / `expires_at` | **NONE** | **[DEFECT]** |
| **3** | `EV-23` | an **authorization for the non-allocating re-run** | **NONE** | **[DEFECT]** |

### 3.4 Two governance artifacts produce nothing mechanical — and that is correct

**[MEASURED]** `GA-5` (residual acceptance) and `GA-7` (irreversible-mutation authorization) have **out-degree 0 into the implementation**. Nothing in `ledger_authority.py`, `ukb.py`, `ukbx.py`, `uga_engine.py` or `register.sh` reads either.

**[INFERRED]** This is not a defect and it is not a redundancy. It is the same structural fact `PHASE2:§C.1` merges **M1** and **M2** established for FD-1 and FD-4 — *"OUT-DEGREE 0 into the implementation"* — now appearing for the authorization instrument itself. **The machine cannot tell whether `GA-7` exists.** That is the precise reason §4.3 finds 12 of 14 gate conditions unenforceable, and the precise reason `register.sh:150-153` states the requirement in prose addressed to an operator rather than encoding it in a predicate.

### 3.5 The issuer input gap — `IA-12`

**[MEASURED]** **P6-10**: the two mutating runs pass **different** actor strings, and the actor binding is **strict** (`permit.get("actor") != actor`, `:728-732`, no `None` guard):

```
run A   ukb.py:1287       actor = "UMB-IMP-001 :: ukb.py build --mint"
run B   uga_engine.py:2079/2098   actor = "UCOS-UGA-001 :: uga_engine.py run"
```

**[MEASURED]** **P6-1**: of the nine fields `_verify_permit` reads, **four are strict and five are elective**:

| Field | Site | Strict or elective | Consequence of omission |
|---|---|---|---|
| `permit_id` | `:715` | **STRICT** | not found → refused |
| `actor` | `:728` | **STRICT** | `None != actor` → refused |
| `manifest_digest` | `:735` | **STRICT** | `None != digest` → refused |
| `preimage_digest` | `:743` | **STRICT** | `None != digest` → refused |
| `head` | `:751` | **ELECTIVE** — `if bound_head is not None:` | repository binding silently **absent** |
| `scope` | `:767` | **ELECTIVE** — `if isinstance(scope, dict):` | **no scope check at all** |
| `scope.maps` | `:769` | **ELECTIVE** — `if isinstance(declared, list):` | map restriction absent |
| `scope.max_allocations` | `:778` | **ELECTIVE** — `if isinstance(cap, int):` | cap absent |
| `expires_at` | `:785` | **ELECTIVE** — `if expires_at:` | no expiry |

**[INFERRED]** So the issuer makes **three independent elections** that no artifact in the package records, and each has a measurable consequence (§6.4, §6.5). Phase 3 `§B.1` states the producer's *"output shape is **already fully determined** by the consumption set, so this is a construction task with **no design freedom**."* **That is measurably false for five of the nine fields.**

**[DEFECT] → the missing artifact:**

> **`IA-12` — Issuer specification record.** Fixes, before any permit is issued: the exact `actor` literal per run; whether `head` is bound; whether `scope` is emitted and with what `maps` and `max_allocations`; whether `expires_at` is set; and the `permit_id` allocation rule (§6.13).

`IA-12` is **[EXEC-REQ]**, model-invariant, and required under all 12 models.

### 3.6 The re-run authorization gap — the sharpest finding of this phase

**Premise, established at source rather than inferred.** **[MEASURED]** **P6-8**, `ukb.py:892-894`:

```python
entry = ledger["by_path"].get(relpath)
if entry:
    return entry["universal_id"], entry["page_start"], entry["page_count"]
```

An already-allocated path returns its existing identifier, consumes **no** sequence number, writes **no** ledger entry and calls **no** clock (`_now()` is reached only in the allocation branch at `:909`).

**[INFERRED]** Therefore on the **second** `register.sh`, Phase 1's manifest is:

```
allocating = False        total_allocations = 0        allocated = {}
```

**[MEASURED]** The run-1 permit was issued against `allocated = {"by_path": [9 ids]}`, `total_allocations = 9`. `manifest_digest` covers **both** fields (`:550-568`). And the ledger moved in run 1, so `preimage_digest` moved too (`PHASE4` P4-7).

**[INFERRED] The run-1 permit fails two strict bindings on the re-run** — `manifest_digest` at `:735` **and** `preimage_digest` at `:743`. It is not merely stale; it is refused twice over.

**[MEASURED]** The only authorization that succeeds is the sentinel. `_verify_permit`'s `NO_ALLOCATION` branch (`:684-707`): refuses if `manifest["allocating"]` — which is now False — then requires `before == after`, which holds **precisely because** `_path_identity` returns early and no clock is called. So:

```
second register.sh  Phase 1  +  permit=NO_ALLOCATION  ->  ACCEPTED
                                                          authorization="NO_ALLOCATION"
                                                          bytes_changed=False
second register.sh  Phase 1  +  permit=<run-1 id>     ->  REFUSED, 2 bindings
```

**[MEASURED]** `IA-4` / `F-4` is specified by `PHASE3:§C.0` as *"A verified permit reaches `ukb build --mint`"* — a **static** plumbing of one `permit_id` to `register.sh:216`. **[INFERRED]** A static plumbing cannot supply `NO_ALLOCATION` on the re-run, so **`EV-23` cannot be produced, and `UK-1` closure item 5 is unreachable.**

**[DEFECT] Two closures exist. Both are stated; neither is preferred** (constraint 8).

| Closure | Mechanism | Cost |
|---|---|---|
| **C-1** | `IA-4` becomes **conditional**: `register.sh`/`ukb.py` passes a `permit_id` when the manifest allocates and `NO_ALLOCATION` when it does not | **[MEASURED]** the pattern already exists in the tree — `ukb.py:2380-2384` passes `permit=LA.NO_ALLOCATION` on the idempotent exec-declare path, the dead branch `R-5a` revived. Not a new mechanism. |
| **C-2** | A **third permit** is issued for the empty manifest before the re-run | **[MEASURED]** axis-`D`-dependent: under `D1` an empty-manifest permit is issuable; under `D2` it is **not**, so the authorization must come through `O-7`'s alternative path. Adds a third machine-checkable authorization event, contradicting `PHASE5:§E.4`'s minimum of 2. |

**[INFERRED]** `C-1` preserves Phase 5's 2-authorization minimum; `C-2` raises it to 3. **Either way `PHASE5:§J.4`'s count of 2 machine-checkable approvals is conditional on a decision the package does not record.** This is the **sixth** axis-parameterized item (§6.8).

### 3.7 Listed but never consumed

| Object | Produced by | Consumed by | Class |
|---|---|---|---|
| **`single_use: True`** | `_issue` — **the register's only existing writer** | **NOTHING.** **[MEASURED]** `PHASE3` P3-2: `single_use` occurs **0** times in `ledger_authority.py` | **[MEASURED]** dead field |
| `IA-7` claim amendments | implementation | no mechanical consumer | correct — they close `CX-1`/`CX-2`/`CX-3`, which are contradictions in prose |
| `IA-8` 58-file citations | implementation | no mechanical consumer | correct — documentation coherence |
| `GA-5`, `GA-7` | governance | no mechanical consumer | correct — §3.4 |

**[INFERRED]** `single_use` is the one genuine orphan: a field the only producer writes and no reader reads. Under `B2` it becomes load-bearing — but then `O-3` must read it, and until `O-3` lands the field is a **false affordance**: a register inspector would conclude single-use semantics are enforced when **[MEASURED]** nothing enforces them (this is `E1-F3`).

### 3.8 Q1 verdict

```
DOES THE PHASE 5 PACKAGE CONTAIN EVERY ARTIFACT REQUIRED TO EXECUTE?   NO

  MISSING ARTIFACTS ................................................. 1
      IA-12  issuer specification record (actor literals + 3 elections)

  UNDER-SPECIFIED ARTIFACTS ......................................... 1
      IA-4   static plumbing cannot authorize the non-allocating re-run

  UNPRODUCIBLE EVIDENCE ITEMS ....................................... 2
      EV-1   not producible by the command PHASE4 V-1 names   (§6.11)
      EV-23  not producible at all as specified               (§3.6)

  PRODUCED BUT NEVER CONSUMED ....................................... 1 field
      single_use

  CORRECTED ARTIFACT COUNT .......................................... 42
      9 governance + 12 implementation + 21 evidence
```

---


## 4. Authorization sufficiency analysis — Q2

### 4.1 The question stated precisely

"Sufficient" needs a named consequent or the question is unanswerable. Three candidates, and the answers differ:

| Reading | Sufficient for … |
|---|---|
| **R1 — mechanical** | the two commands run to completion without refusal |
| **R2 — determinate** | the outcome is determinate, i.e. every failure is diagnosable and every success is trustworthy |
| **R3 — closing** | `UK-1` and `UK-2` are retired |

**[INFERRED]** All three are answered below. `R1` is what the authority enforces; `R2` is what the gate is *for*; `R3` is what the program is *for*.

### 4.2 Per-condition classification

Classified against **R1 — mechanical execution**, because that is the only reading under which "necessary" and "sufficient" have crisp truth conditions. The right-hand column records what the condition *is* necessary for, so that a `NEITHER` verdict is not read as "pointless".

| # | Condition | Necessary for R1? | Sufficient for R1? | Verdict | Necessary for what, then |
|---|---|---|---|---|---|
| **G-1** | GA-1 selection record | **no** | no | **NEITHER** | task content (`IA-1`); `GA-3`, `GA-9` |
| **G-2** | GA-2/3/4 | **no** | no | **NEITHER** | specification completeness; `R-B` scope |
| **G-3** | GA-5 residual acceptance | **no** | no | **NEITHER** | the legitimacy of activating 3 residuals |
| **G-4** | GA-6 UK closure sets | **no** | no | **NEITHER** | falsifiability of `EV-17`, `EV-22`, `EV-23` |
| **G-5** | **GA-7 mutation authorization** | **no** | no | **NEITHER** | the legitimacy of the act. **[MEASURED]** out-degree 0 into the implementation (§3.4) |
| **G-6** | GA-8/9 rollback + axis record | **no** | no | **NEITHER** | rollback executability; `V-11`'s success condition |
| **G-7** | **IA-1…IA-11 complete** | **YES** | no | **NECESSARY** | — **[MEASURED]** `PHASE3` P3-1: without `IA-3`+`IA-4` all three `permit` values are refused |
| **G-8** | register staged, worktree clean | **no** | no | **NEITHER** | `EV-2`, `EV-9`, `EV-21`. **[MEASURED]** §4.5 — the transaction runs no drift check |
| **G-9** | `ledger_authority.py` committed | **no** | no | **NEITHER** | `R-A` safety (`PHASE5` P5-3) |
| **G-10** | no `--install-hooks` | **no** | no | **NEITHER** | the 2-run minimum (`PHASE5` P5-4) |
| **G-11** | Stage 0 green (`V-1…V-6`) | **no** | no | **NEITHER** | **determinacy** — this is `R2`, not `R1` |
| **G-12** | zero-dirty over 4 guard dirs | **no** | no | **NEITHER** | `R-A` non-destructiveness |
| **G-13** | evidence destination designated | **no** | no | **NEITHER** | diagnosability of failure |
| **G-14** | **a verifying permit for run R** | **YES** | no | **NECESSARY** | — **[MEASURED]** `commit :841` `permit` is mandatory with no default |

```
NECESSARY for mechanical execution ...............  2   G-7, G-14
SUFFICIENT for mechanical execution ..............  0
BOTH .............................................  0
NEITHER (necessary for determinacy, rollback,
         evidence or legitimacy — not for the act) 12
```

### 4.3 The structural result: 12 of 14 conditions are unenforceable by the machine

**[MEASURED]** Only `G-7` and `G-14` have mechanical teeth, and only `G-14` is checked at run time. Nothing in the repository reads a governance record; nothing checks that Stage 0 ran; nothing verifies that an evidence destination was designated.

**[INFERRED]** Consequently the authorization gate is a **governance instrument, not a technical control**. An operator in possession of `IA-3`, `IA-4` and one valid permit can execute with **zero** governance artifacts, **zero** Stage-0 evidence and **zero** rollback preparation, and the authority will not object. What the authority enforces is narrow and exact: that the write matches an authorization naming that ledger state.

**[INFERRED]** This is not a weakness in `_verify_permit`. It is the separation the source states at `:490-497` — *"`commit()` ENFORCES an authorization it does not DECIDE"* — observed from the other side. But it does mean **the gate's 12 unenforceable conditions are the entirety of what protects the program from an undiagnosable failure**, and they are protected by discipline alone.

### 4.4 Can a gate pass while execution remains impossible? **YES — three ways, all measured**

| # | All 14 hold, yet | Basis |
|---|---|---|
| **1** | **`EV-23` is unproducible**, so the program cannot reach `EXECUTION-COMPLETED` | **[MEASURED]** §3.6 — `IA-4`'s static plumbing cannot authorize the re-run |
| **2** | **A `head`-bound permit lapses on any commit** between `G-14`'s satisfaction and the run | **[MEASURED]** `:751-762`; the only existing producer `_issue` **does** bind `head` (**P6-2**). `G-14` is evaluated at an instant; nothing holds it |
| **3** | **`git` becomes unavailable**, so `manifest["head"] is None` and a `head`-bound permit is refused *"rather than assuming a match"* | **[MEASURED]** `git_head` `:580-598` returns `None` on `OSError`/timeout; `:753-757` refuses — the fail-closed direction |

### 4.5 Can a gate fail while execution remains possible? **YES — two, measured**

| # | Condition fails, yet the runs still execute | Basis |
|---|---|---|
| **1** | **`G-8`** — the register left `??` untracked | **[MEASURED]** full read of `register.sh:206-259`: **the ten-phase transaction performs no drift check whatsoever.** The `--observe` filter is at `:125` and the `--guard` gate at `:265-273`; neither is in the transaction path. So an untracked register fails `EV-2`/`EV-21` and does **not** impede run A |
| **2** | **`G-12`** — a guard directory carrying uncommitted work | **[MEASURED]** `commit()` guards only `00-BOOK/DATA/id-ledger.json`. Dirty state elsewhere makes `R-A` destructive but does not refuse a write |

**[INFERRED]** So `G-8` and `G-12` are **evidence and safety conditions misfiled as execution preconditions**. They belong in the gate — a program that cannot produce `EV-21` cannot retire `UK-1` — but their failure mode is *loss of evidence or loss of rollback safety*, never *inability to execute*. Phase 5 does not draw that distinction; §4.2's right-hand column supplies it.

### 4.6 Q2 verdict

```
ASSUMING ALL 14 GATE CONDITIONS ARE SATISFIED, IS EXECUTION
GUARANTEED TO BE REACHABLE?                                            NO

  because  (a) EV-23 is unproducible as specified                    [DEFECT]
           (b) G-14 is instantaneous — a head-bound permit lapses
               on any intervening commit                            [MEASURED]
           (c) 8 refusal points inside commit() remain live even
               with a verifying permit — §7.2                       [MEASURED]

CAN A GATE PASS WHILE EXECUTION IS IMPOSSIBLE?                        YES  (3 ways)
CAN A GATE FAIL WHILE EXECUTION REMAINS POSSIBLE?                     YES  (G-8, G-12)
CONDITIONS ENFORCEABLE BY THE MACHINE ..............................  2 of 14
```

---

## 5. Minimality analysis — Q3

### 5.1 Classification scheme

For each artifact, removal causes exactly one of:

| Code | Meaning |
|---|---|
| **EI** | **Execution impossibility** — the runs cannot be performed or cannot be authorized |
| **AA** | **Authorization ambiguity** — the act can occur but its authorization is undefined, unfalsifiable or unattributable |
| **RI** | **Rollback incompleteness** — a failure becomes unrecoverable or its evidence is destroyed |
| **EL** | **Evidence loss** — an unknown cannot be retired, though execution and rollback are unaffected |
| **NE** | **No effect** |

**[INFERRED]** `EL` is added to the four the task names, because without it 11 evidence items would classify as `NE` — which would be true of execution and false of the program's purpose.

### 5.2 Governance artifacts

| ID | Removal effect | Reason |
|---|---|---|
| **GA-1** | **EI** | **[MEASURED]** `PHASE3:§C.4` — 4–7 tasks per model are axis-conditional; `IA-1` cannot be written, so `IA-3`/`IA-4` never exist |
| **GA-2** | **AA** | `R-B`'s scope undefined (`B2a`/`B2b`); `R` unpinned admits a 13th, non-admissible model |
| **GA-3** | **AA** | Whether the model is one of the 12 becomes unattested |
| **GA-4** | **AA** | **[MEASURED]** `PHASE3:§A` — the 12/24 readings are **not** in a superset relation; every count becomes unattributed |
| **GA-5** | **AA** | 3 residuals activate latent→live with no accepting party |
| **GA-6** | **EL** | **[INFERRED]** post-hoc closure criteria make the runs unfalsifiable — `PHASE4:§I.1` item 5 exists precisely to prevent this |
| **GA-7** | **AA** | The act occurs unauthorized. **[MEASURED]** mechanically undetectable (§3.4, §4.3) |
| **GA-8** | **RI** | Rollback needs approval *during* a failure, when `EV-18` must already have been captured |
| **GA-9** | **EL** + **RI** | `V-11` has no success condition (`EL`); `R-B` has no scope and the replay consequence is unknown (`RI`) |

```
GOVERNANCE:  EI 1 · AA 5 · RI 1 · EL 1 · EL+RI 1 · NE 0
```

### 5.3 Implementation artifacts

| ID | Removal effect | Reason |
|---|---|---|
| **IA-1** | **AA** | **[INFERRED]** 17–20 tasks can be written without a specification; what cannot be established is that they were written *as authorized*. Not `EI` — this is honest rather than convenient |
| **IA-2** | **EI** | **[MEASURED]** `A3` is the unique axis-`A` value closing `RES-1` (`PHASE2:§E.2`); without it no admissible model is realized |
| **IA-3** | **EI** | **[MEASURED]** `PHASE3` P3-1 — `load_permit_register` returns `[]`, so every `permit_id` yields *"is not in …"* |
| **IA-4** | **EI** | **[MEASURED]** `register.sh:216` passes no `--permit`; `ukb.py:1299` resolves `None`; `None` is refused at the type check |
| **IA-5** | **EL** | `UGA-INV-10` keeps failing → `EV-22` unobtainable → `UK-2` item 3 open. Execution unaffected |
| **IA-6** | **EL** | Declared surface diverges from measured; `EV-22` unobtainable |
| **IA-7** | **NE** | **[MEASURED]** no mechanical consumer. `CX-1`/`CX-2`/`CX-3` remain standing — a documentation defect, not an execution one |
| **IA-8** | **NE** | 58 stale citations; no mechanical consumer |
| **IA-9** | **EL** | `EV-1`, `EV-24` unobtainable → no regression baseline |
| **IA-10** | **EL** | **[MEASURED]** `PHASE3:§C.0` F-12 — under `Aud3` the invariant can silently return |
| **IA-11** | **NE** for execution; **EI** under `Aud1`/`B2b` | **[INFERRED]** the model *requires* it; and §6.7 measures that its **placement** changes run A's manifest |
| **IA-C1** | **EL** | **[MEASURED]** §4.5 — `??` fails `EV-2`/`EV-21`, does not impede the run |
| **IA-C2** | **RI** | **[MEASURED]** `PHASE5` P5-3 — a `reset`-class rollback deletes all twelve Phase-1 closures |
| **IA-12** *(new)* | **AA** | **[MEASURED]** §3.5 — wrong `actor` → refused; omitted `scope` → the authority enforces **no** bound, so `GA-7`'s scope limit is unenforced |

```
IMPLEMENTATION ARTIFACTS (IA-1 … IA-12, 12 items)
                 EI 3 · AA 2 · EL 4 · NE 3        (+1 conditional EI: IA-11 under Aud1/B2b)
PRE-GATE ACTS    (IA-C1, IA-C2 — acts, not artifacts; not counted in the 42)
                 IA-C1 EL · IA-C2 RI
```

### 5.4 Evidence items

| ID | Removal effect | Reason |
|---|---|---|
| **EV-1** | **EL** | No pre-mutation baseline; `EV-24` uninterpretable |
| **EV-2** | **EL** | The only pre-mutation check of gates 0/5/6/7 + drift + identity gap |
| **EV-3** | **EI** | **[MEASURED]** permit A cannot be constructed — `manifest_digest`/`preimage_digest` are unknown |
| **EV-4** | **RI** | `--plan`'s read-only property unconfirmed; `R-A`'s zero-dirty precondition unverified |
| **EV-5** | **EL** | `E-4A`'s closure becomes falsifiable only *by mutating* |
| **EV-6** | **RI** | No pre-image reference; a restore cannot be shown to have restored |
| **EV-7** | **RI** | **[MEASURED]** `PHASE4:§F.3` — the only evidence surviving `R-A` |
| **EV-8** | **RI** | **[MEASURED]** `PHASE4:§F.6` — evidence written inside the guard dirs reads as drift |
| **EV-9** | **EL** | = `IA-C1` |
| **EV-10** | **RI** | = `IA-C2` |
| **EV-11** | **EI** | The permit itself |
| **EV-12** | **EI** | Permit B cannot be constructed |
| **EV-13** | **EL** | **[MEASURED]** `PHASE4:§E.3` — `V-11`'s *"no invariant that passed at V-5 now fails"* is unstatable |
| **EV-14** | **EI** | **[MEASURED]** §6.7 — `scope.max_allocations` is set to the exact total by the only producer, so a stale count fails **two** bindings |
| **EV-15** | **EI** | Permit B |
| **EV-16** | **EI** | **[MEASURED]** `PHASE4` P4-7 — a stale pre-image is refused at `:743` |
| **EV-17** | **EL** | `UK-1` items 2–3 |
| **EV-18** | **RI** | **[MEASURED]** `PHASE4:§E.3` — unrecoverable after `R-A` |
| **EV-19** | **EL** | The first run's movement unattributable |
| **EV-20** | **EL** | **[MEASURED]** `PHASE5` P5-2 — `EV-21` returns `RC=3` on the permit's own write |
| **EV-21** | **EL** | `UK-1` item 4 |

```
EVIDENCE ITEMS (EV-1 … EV-21, 21 items)
                 EI 6  ..... EV-3, EV-11, EV-12, EV-14, EV-15, EV-16
                 RI 6  ..... EV-4, EV-6, EV-7, EV-8, EV-10, EV-18
                 EL 9  ..... EV-1, EV-2, EV-5, EV-9, EV-13, EV-17, EV-19, EV-20, EV-21
                 AA 0 · NE 0
```

### 5.5 Aggregate

```
                        EI      AA      RI      EL    EL+RI     NE     total
  GA-1 … GA-9            1       5       1       1       1        0        9
  IA-1 … IA-12           3       2       0       4       0        3       12
  EV-1 … EV-21           6       0       6       9       0        0       21
  ─────────────────────────────────────────────────────────────────────────
  TOTAL                 10       7       7      14       1        3       42
  ( + 2 pre-gate ACTS, not artifacts:  IA-C1 = EL · IA-C2 = RI )

  REMOVAL CAUSES EXECUTION IMPOSSIBILITY .......................... 10
  REMOVAL CAUSES AUTHORIZATION AMBIGUITY ..........................  7
  REMOVAL CAUSES ROLLBACK INCOMPLETENESS ..........................  7   (+GA-9, +IA-C2 = 9
                                                                         counting the EL+RI
                                                                         item and the act)
  REMOVAL CAUSES EVIDENCE LOSS (unknown cannot be retired) ........ 14   (+GA-9, +IA-C1 = 16)
  REMOVAL HAS NO EFFECT ...........................................  3   IA-7, IA-8, IA-11*
                                                                        *IA-11 = NE only outside
                                                                         Aud1 / B2b
  arithmetic check ....... 10 + 7 + 7 + 14 + 1 + 3 = 42            ✓
```

### 5.6 The true minimal execution package

**[INFERRED]** Three distinct minima exist, and reporting one number would be wrong.

```
  MINIMUM TO EXECUTE ONE RUN (R1 — the command runs and is authorized) ..... 6
      IA-2   A3 whole-document binding
      IA-3   the permit register
      IA-4   permit plumbing to ukb.py:1299            (conditional — §3.6)
      IA-12  issuer specification (actor literal + 3 elections)  ◀── or the
             permit is not CONSTRUCTIBLE at all
      EV-3   the plan manifest it binds
      EV-11  the permit itself
    [MEASURED] nothing else is read by any code path on the write route.

  MINIMUM TO EXECUTE BOTH RUNS ............................................ 10
      + EV-12  run B's plan manifest
      + EV-14  the re-measured by_object population
      + EV-15  permit B
      + EV-16  the re-measured pre-image

  MINIMUM TO REACH EXECUTION-COMPLETED WITH BOTH UNKNOWNS RETIRED ......... 33
        10   the above
      + 14   every EL-classified item — without them an unknown cannot be retired
             GA-6 · IA-5 · IA-6 · IA-9 · IA-10 · EV-1 · EV-2 · EV-5 · EV-9
             EV-13 · EV-17 · EV-19 · EV-20 · EV-21
      +  1   GA-9      — V-11 has no success condition without it
      +  8   every RI-classified item + IA-C2, or a mid-transaction failure is
             unrecoverable, which is not "completed" in any usable sense
             GA-8 · EV-4 · EV-6 · EV-7 · EV-8 · EV-10 · EV-18 · IA-C2
      ────
        33

  MINIMUM TRANSITION PACKAGE (authorized, determinate, recoverable) ....... 42
      all of GA-1…GA-9, IA-1…IA-12, EV-1…EV-21  (+ the 2 pre-gate acts)
```

**[INFERRED] Verdict: the Phase 5 package is not minimal, and it should not be.** The ratio is **7:1** against the mechanical minimum (42 against 6), and every item in the gap is classified `AA`, `RI` or `EL` — authorization legitimacy, recoverability, or the ability to retire an unknown. **[MEASURED]** Exactly **three** items (`IA-7`, `IA-8`, and `IA-11` outside `Aud1`/`B2b`) are `NE`, and all three are required by the *model* rather than by the execution. **So the package contains no item that is redundant on every axis** — which is the precise sense in which Phase 5's minimality claim survives, restated correctly: it is minimal with respect to *authorized, determinate, recoverable* execution, not with respect to execution.

---

## 6. Hidden dependency inventory — Q4

Fourteen dependencies present in none of Phase 2, 3, 4 or 5. Each is reproduced, measured and classified.

### 6.0 Classification

| Class | Meaning |
|---|---|
| **CONSEQUENTIAL** | Changes a count, a requirement, or the reachability of an evidence item |
| **BENIGN-MEASURED** | A real dependency, probed, with no consequence for the package |
| **CORRECTION** | A prior-phase claim that measurement contradicts |

### 6.1 H-1 — `git ls-files --cached` makes eligibility a property of the **index**, not the working tree

**CONSEQUENTIAL.** Category: git · staging.

**[MEASURED]** **P6-3**. `ukb._iter_files` (`:821-845`) derives eligibility from `_repo_artifact_paths()`, whose docstring states: *"Everything else that version control CARRIES (**tracked or staged**), and carries a registerable extension, is eligible."* `INCLUDE_EXTENSIONS = (".md", ".txt", ".docx", ".json")` (`config.py:942`).

Measured today:

```
eligible artifacts (tracked OR staged, minus excludes) ....... 1606
registered in artifacts.json ................................. 1597
BY_PATH GAP .................................................. 9   (matches PHASE4 P4-2)
    ENFORCEMENT-CLOSURE-GAPS.md          SELF-COVERAGE-GRAPH.md
    ENFORCEMENT-CLOSURE-MATRIX.md        UCOS-OMEGA-INFINITY-BLOCKER-…-DETERMINATION.md
    SELF-COVERAGE-GAPS.md                UCOS-UCON-000001-…-DETERMINATION.md
    coverage_100_plan.md                 final_certification_report.md
    missing_execution_surface_report.md
```

**[INFERRED]** The population of 9 is stable **only while no registerable file enters the index.** `git add` alone — without a commit — grows it. And **[MEASURED]** `scope.max_allocations` is set by the only producer to the *exact* total (**P6-2**), so a population change fails **two** bindings: `manifest_digest` and `scope`.

**[EXEC-REQ]** `EV-3` must be measured, and permit A issued, with **no staging of any registerable path in between**. Phase 5's `S-2`/`S-5` order satisfies this only because `IA-C1` and `IA-C2` target excluded directories (§6.2) — an accident of the exclusion list, not a stated property.

### 6.2 H-2 — the exclusion list is what makes Phase 5's staging refinement safe

**BENIGN-MEASURED.** Category: staging · register.

**[MEASURED]** `config.py:885-897`, the complete tuple — **13 entries**:

```
.git/   .github/   .kiro/
00-BOOK/tools/   00-BOOK/DATA/   00-BOOK/REGISTRIES/
00-BOOK/CONTROL-TOWER/   00-BOOK/VOLUMES/   00-BOOK/PORTAL/
00-MASTER/
MCP-001-MASTER-CONTEXT-AND-EXECUTION-SYSTEM.md
intelligence/UCOS-RIE-      intelligence/UCOS-IMP-BASELINE-001.
```

**[INFERRED]** `IA-C1` stages `00-BOOK/DATA/allocation-permits.json` → excluded. `IA-C2` commits `00-BOOK/tools/ledger_authority.py` → excluded. **Neither affects the `by_path` population.** Phase 5's staging refinement is therefore safe — and safe *for a reason Phase 5 does not state*.

**[EXEC-REQ]** The corollary is a live hazard: **the Phase-5 and Phase-6 determination documents are root-level `.md` files.** **[MEASURED]** both are `??`. Committing either **in the same commit as `IA-C2`** — the natural operator action — makes it eligible, grows the population to 10, and invalidates permit A on two bindings. Nothing in the package warns of this.

### 6.3 H-3 — `Aud1`/`B2b` can grow the **`by_path`** population, so "9 mints" is not model-invariant

**CONSEQUENTIAL + CORRECTION.** Category: invariant · register · ordering.

**[MEASURED]** `governance_telemetry.forbid_data_telemetry` (`:187-207`): a file whose basename ends `-audit.json` may **never** be written under `00-BOOK/DATA` — `TelemetryPathError`. The ban is name-scoped and directory-scoped; it does not restrict other locations.

**[INFERRED]** `IA-11` under `Aud1` therefore cannot live in `00-BOOK/DATA/` under its natural name. Its placement determines which populations it joins:

| Placement | `by_path` eligible? | `by_object` discovered? | Effect on run A's manifest |
|---|---|---|---|
| `00-BOOK/DATA/x.json` (not `*-audit.json`) | **no** — excluded | yes | none |
| `00-MASTER/…` | **no** — excluded | yes | none |
| `00-BOOK/DATA/x-audit.json` | n/a | n/a | **`TelemetryPathError`** — hard refusal |
| **anywhere else, `.md`/`.json`/`.txt`/`.docx`** | **YES** | yes | **population 9 → 10** |

**[INFERRED] Correction.** `PHASE4:§J.5` and `PHASE5:§J.5` both state *"RUN A `register.sh` → closes UK-1 → **9** `by_path` mints"* as a model-invariant figure. It is not: under `Aud1` (4 of 12 models) and under `B2b`, run A's population is **9 or 10 depending on a placement decision no artifact records.** `PHASE3:§B.5` names two hard constraints on `Aud1`'s log — the `-audit.json` ban and the no-wall-clock contract — and not this third one.

### 6.4 H-4 — five of nine permit bindings are elective

**CONSEQUENTIAL + CORRECTION.** Category: register · serialization. Established in §3.5 (**P6-1**).

**[INFERRED] Two corrections follow.**

1. `PHASE3:§B.1` — *"no design freedom"* — is false for `head`, `scope`, `scope.maps`, `scope.max_allocations`, `expires_at`.
2. `PHASE5:§B.7` claims `GA-7`'s scope bound *"is enforced by the authority itself, not merely by policy"*, citing `scope.maps` and `scope.max_allocations`. **[MEASURED]** that enforcement is conditional on `isinstance(scope, dict)`. **If the producer omits `scope`, the authority enforces no bound at all** and `GA-7`'s scope limit is policy only. This is a correction to Phase 5 by its own author.

### 6.5 H-5 — a `head`-bound permit is invalidated by any commit; `git` must be on `PATH`

**CONSEQUENTIAL.** Category: git · environment.

**[MEASURED]** `build_manifest` (`:634-648`) calls `git_head(path)` on **every** `plan()` and **every** `commit()`. `git_head` (`:580-598`) spawns `git -C <dir> rev-parse HEAD` with `timeout=15` and returns `None` on `OSError`, `SubprocessError`, non-zero exit or empty output. Its docstring: *"A permit that BINDS a head is refused when the head cannot be determined — the fail-closed direction — while a permit with `head: null` **declines** the binding."*

**[MEASURED]** `git --version` → **2.54.0**. `git_head` returns the **full** 40-char sha `77798202d2df43285760b3277f230ebde4b52bbc` (**P6-11**).

**[MEASURED]** The only existing producer binds it: `_issue` sets `"head": manifest["head"]` (**P6-2**).

**[INFERRED]** Three consequences: (i) **`git` is a hard runtime dependency of the write path**, not merely of the gates; (ii) a `head`-bound permit is invalidated by **any** intervening commit; (iii) losing `git` converts a valid permit into a refusal rather than into an unchecked pass — correct, and worth stating because it is the only place in the chain where an *environmental* failure produces a *governance* refusal.

### 6.6 H-6 — `register.sh` has a path that exits 0 having done nothing

**CONSEQUENTIAL.** Category: lock · environment · clock. **This is the finding behind §1.1's U-C.**

**[MEASURED]** `register.sh:187-192`:

```bash
LOCK="$HERE/.register.lock"
if [ -f "$LOCK" ]; then
  if [ "$(( $(date +%s) - $(cat "$LOCK" 2>/dev/null || echo 0) ))" -lt 3600 ]; then
    echo "register.sh already running (lock $LOCK) — nested/concurrent call is a no-op."
    exit 0
  fi
fi
```

**[MEASURED]** **P6-6** — the guard's logic reproduced verbatim under `bash` with `set -euo pipefail` in an isolated `/tmp` directory, since removed. Six cases:

| Case | Lock state | Behaviour | Exit |
|---|---|---|---|
| **A** | absent | proceeds to the transaction | — |
| **B** | written 0 s ago (a `SIGKILL`ed run) | **NO-OP — transaction never runs** | **0** |
| **C** | 3601 s ago | proceeds (stale reclaimed) | — |
| **D** | 3599 s ago | **NO-OP** | **0** |
| **E** | present but **empty** | `bash: 1788054239 -  : syntax error: operand expected` on stderr, **then proceeds** — `set -e` does not fire because the failure is inside an `if` condition | **0** |
| **F** | timestamp **in the future** (clock stepped backward) | **NO-OP** — negative delta is `< 3600` | **0** |

**[MEASURED]** A seventh case: non-numeric lock content (`corrupt`) → `set -u` treats it as an unbound variable → **exit 1**, and **[MEASURED]** this occurs at `:189`, *before* `fail()` is defined at `:201`, so there is **no `TRANSACTION INCOMPLETE` message** — only a raw bash error.

**[MEASURED]** The lock is absent today; `00-BOOK/tools/.register.lock` → *No such file or directory* (**P6-6**).

**[INFERRED] The consequence for the package.** `EV-23`'s success condition is **[MEASURED]** `PHASE4:§I.1` item 5: *"a second `register.sh` produces **zero** byte changes across the four guard directories."* Under cases **B**, **D** or **F** the transaction never runs, so zero byte changes is satisfied **trivially**. `EV-23` passes and measures nothing, and `UK-1` is retired on it.

**[INFERRED] Run A is protected; the re-run is not.** `UK-1` item 3 requires the exact line `TRANSACTION COMPLETE — every artifact on disk is registered, classified, validated, and synchronized` **and** exit 0, which the no-op path does not emit. Item 5 requires **only** byte-neutrality. **The asymmetry is the defect.**

**[EXEC-REQ]** `EV-23` must additionally require: (i) the `TRANSACTION COMPLETE` line; (ii) the **absence** of the line `nested/concurrent call is a no-op`; (iii) `00-BOOK/tools/.register.lock` verified absent immediately before the re-run.

### 6.7 H-7 — `scope.max_allocations` is set to the exact total, so it has zero slack

**CONSEQUENTIAL.** Category: register.

**[MEASURED]** **P6-2**, `_issue`:

```python
"scope": {"maps": sorted(manifest["allocated"]),
          "max_allocations": manifest["total_allocations"]},
```

**[INFERRED]** `cap == total`, and `:778` refuses when `total_allocations > cap`. So the cap is **exactly** tight: any increase in the population between issuance and the run fails `scope` *in addition to* `manifest_digest`. Two independent refusals for one cause — defence in depth, and it means `EV-14`'s re-measurement is load-bearing twice over.

**[INFERRED]** Also: `maps = sorted(manifest["allocated"])` — the **keys**, i.e. `["by_path"]` for run A and the `by_object`/`by_observation` set for run B. **[MEASURED]** `uga_engine.py:2098`'s comment records that the single `commit` *"ALSO persists the `by_observation` identities minted by `epoch_observation_universe`"*. **[INFERRED]** So run B's `scope.maps` must include `by_observation`, not only `by_object` — a field value no phase enumerated, and one that `EV-12`'s plan output supplies via `format_report`'s `[name+n, …]` rendering.

### 6.8 H-8 — the two runs carry different `actor` literals

**CONSEQUENTIAL.** Category: register. Established in §3.5 (**P6-10**).

### 6.9 H-9 — the sixth axis-parameterized item

**CONSEQUENTIAL.** Category: ordering · invariant.

**[INFERRED]** From §3.6: the re-run's authorization mechanism is axis-`D`-parameterized. Under `D1` an empty-manifest permit is issuable (closure `C-2` available) and the sentinel path is untouched (`C-1` available). Under `D2` empty-manifest permits are **not** issuable, so `C-2` requires `O-7`'s alternative branch, and **[MEASURED]** `PHASE3:§B.4` records that `D2` *"must not re-kill `ukb.py:2380-2384`"* — the very `NO_ALLOCATION` branch `C-1` depends on.

**[INFERRED]** `PHASE5:§J.7` lists **5** axis-parameterized content items. This is the **sixth**, and unlike the other five it changes a **count** — the number of machine-checkable authorization events (2 under `C-1`, 3 under `C-2`).

### 6.10 H-10 — two Python interpreters, measured invariant

**BENIGN-MEASURED.** Category: environment · serialization.

**[MEASURED]** `register.sh:52` — `PY="${PYTHON:-python3}"`. System `python3` is **3.14.4** (`/opt/homebrew/bin/python3`); `.ec1-venv/bin/python` is **3.12.13**. `PHASE05:§E.0`'s verified test command uses the venv. So the write path and the test path run under **different interpreters**.

**[MEASURED]** **P6-4** — the permit bindings are interpreter-invariant:

```
                         python3 3.14.4        .ec1-venv 3.12.13
  _canonical length        1 790 825             1 790 825      identical
  preimage_digest      3a2a2532e006c326…     3a2a2532e006c326…  identical
  git_head             77798202d2df4328…     77798202d2df4328…  identical
  ledger records             8 855                 8 855        identical
```

**[INFERRED]** `_canonical`'s `sort_keys=True, separators=(",",":"), ensure_ascii=False` is version-stable across 3.12 and 3.14, so a manifest measured under one interpreter verifies under the other. **Classified benign — this closes a risk rather than opening one.**

### 6.11 H-11 — `EV-1` cannot be produced by the command Phase 4 names

**CONSEQUENTIAL + CORRECTION.** Category: environment.

**[MEASURED]** **P6-9**, `pyproject.toml [tool.pytest.ini_options]`:

```toml
addopts = ["-ra", "--strict-markers",
           "-p", "engine.universal_discovery.pytest_scope",
           "--cov-report=term-missing", "--cov-report=xml", "--cov-fail-under=90"]
```

**[INFERRED]** So `pytest platform/tests/test_ledger_authority.py` — the command `PHASE4:§D.1` V-1 and `PHASE5` `EV-1` both name — fails twice over: the plugin `engine.universal_discovery.pytest_scope` is not importable without `PYTHONPATH=.`, and `--cov-fail-under=90` is evaluated over a denominator this single file cannot satisfy.

**[MEASURED]** `PHASE05:§E.0` already recorded the **verified working** invocation — *"verified working at `77798202` (40 tests, 0.80 s)"*:

```bash
PYTHONPATH=. .ec1-venv/bin/pytest platform/tests/test_ledger_authority.py \
    -q -p no:cacheprovider --no-cov
```

**[INFERRED]** The correction was available in Phase 0.5 and was lost between Phase 0.5 and Phase 4. **[EXEC-REQ]** `EV-1` must name the full invocation, not `pytest <file>`.

**[MEASURED]** Side effects are benign: `--cov-report=xml` writes `coverage.xml` and coverage writes `.coverage*`; both are gitignored (`.gitignore:28-29`). **[INFERRED]** This is also why this phase did not run the suite — constraint 7 forbids repository modification, and `coverage.xml` is a repository file even though it is ignored.

### 6.12 H-12 — the CX-6 byte figures are stale

**CORRECTION.** Category: serialization.

**[MEASURED]** **P6-5**, today:

```
LA._canonical over the live ledger .......... 1 790 825 bytes
the production writer's file on disk ........ 2 279 169 bytes
```

**[MEASURED]** `PHASE1:§R-11`, and quoted as current by `PHASE4:§G.3` and `PHASE5:§L.3`: **1 786 167** vs **2 274 511**.

**[INFERRED]** Both figures have drifted by ~4 658 bytes — the ledger grew between Phase 1 and Phase 3, and the `sha256 8471e709…` baseline has been constant only since Phase 3. **`CX-6`'s substance is unaffected**: the inequality holds, so `commit()` must compare documents rather than bytes, so `A4` remains CONTRADICTED. Only the numbers are stale, and they are quoted in two later documents as present-tense measurements.

### 6.13 H-13 — a reused `permit_id` poisons the register permanently

**CONSEQUENTIAL.** Category: register.

**[MEASURED]** `:718-723`:

```python
if len(matches) > 1:
    raise PermitRefused(f"permit {permit_ref!r} appears {len(matches)} times; an "
                        f"ambiguous authorization is no authorization")
```

**[INFERRED]** The register is described in source as *"A SINGLE append-only file"* (`:499-506`). If issuance appends and a `permit_id` is reused — the natural action after an `AUTHORIZATION-LAPSED` event, of which §4.4 identifies three causes — that id becomes **permanently unusable**, and no amount of re-issuance recovers it.

**[INFERRED]** Two further interactions no phase records: **R-D** (restoring the register) can **resurrect a superseded permit**, creating a duplicate on the next append; and **R-A** re-validates a *used* permit by restoring the pre-image (`PHASE4:§F.5`, `PHASE2` P2-1), so after a rollback the same id may be legitimately reusable under `B1` and must **not** be re-appended.

**[EXEC-REQ]** `IA-12` must fix the `permit_id` allocation rule, and it must be collision-free across issuance, lapse, re-issuance and rollback.

### 6.14 H-14 — the transaction runs no drift check

**CONSEQUENTIAL.** Category: git · staging.

**[MEASURED]** Full read of `register.sh`. The drift check exists in exactly two places: `:120-138` inside the `--observe` branch, and `:262-273` inside the `--guard` branch **after** the transaction has completed. **The ten-phase transaction at `:206-259` contains none.**

**[INFERRED]** This is the basis of §4.5: `G-8` and `G-12` cannot impede execution. It also means the `--guard` gate's protection is **post-hoc** — it detects that a transaction produced uncommitted registers, after that transaction has already allocated permanent identities.

### 6.15 Inventory summary

| ID | Dependency | Category | Class |
|---|---|---|---|
| **H-1** | eligibility = the git **index** (tracked *or staged*) | git · staging | CONSEQUENTIAL |
| **H-2** | the 13-entry exclusion list is what makes staging safe | staging · register | BENIGN-MEASURED |
| **H-3** | `Aud1`/`B2b` placement can grow the `by_path` population | invariant · ordering | CONSEQUENTIAL + CORRECTION |
| **H-4** | 5 of 9 permit bindings are **elective** | register | CONSEQUENTIAL + CORRECTION |
| **H-5** | `head`-bound permits die on any commit; `git` is a write-path dependency | git · environment | CONSEQUENTIAL |
| **H-6** | `register.sh` exits 0 having done nothing (3 of 7 lock states) | lock · clock | CONSEQUENTIAL |
| **H-7** | `scope.max_allocations` has zero slack; run B's `maps` include `by_observation` | register | CONSEQUENTIAL |
| **H-8** | the two runs carry different strict `actor` literals | register | CONSEQUENTIAL |
| **H-9** | the re-run's authorization is axis-`D`-parameterized — a 6th item | ordering · invariant | CONSEQUENTIAL |
| **H-10** | two Python interpreters — **digests measured invariant** | environment · serialization | BENIGN-MEASURED |
| **H-11** | `EV-1` unproducible by its named command | environment | CONSEQUENTIAL + CORRECTION |
| **H-12** | the `CX-6` byte figures are stale (substance intact) | serialization | CORRECTION |
| **H-13** | a reused `permit_id` poisons the register permanently | register | CONSEQUENTIAL |
| **H-14** | the transaction itself runs **no** drift check | git · staging | CONSEQUENTIAL |

```
HIDDEN DEPENDENCIES FOUND ...................................... 14
    CONSEQUENTIAL ..............................................  9
    BENIGN-MEASURED ............................................  2
    CORRECTION only ............................................  1   H-12
    CONSEQUENTIAL + CORRECTION .................................  3   H-3, H-4, H-11
                                                                     (counted once in the 9)
    reproduced in an isolated /tmp scratch directory ............  1   H-6
    measured read-only against this repository ................. 13
    by category:  git 4 · staging 4 · register 5 · environment 3
                  serialization 3 · lock 1 · clock 1 · invariant 2
                  ordering 2   (a dependency may carry two categories)
```

---


## 7. Execution-path enumeration — Q5

### 7.1 Run-A outcome classes — six, not three

**[MEASURED]** `PHASE4:§H.1` gives run A three outcomes (`A✓`, `A⊘`, `A✗`). The full source read plus **P6-6** and **P6-7** establish **six**.

| Code | Outcome | Where | Tracked state | Terminal line emitted |
|---|---|---|---|---|
| **A✓** | all 10 phases complete, transaction sealed | `:250-252` | mutated, sealed | `TRANSACTION COMPLETE …` |
| **A∅** | **lock younger than 3600 s, or clock stepped backward** | `:189-192` | **untouched** | `nested/concurrent call is a no-op` · **exit 0** |
| **A⊥** | **lock content non-numeric** | `:189` | **untouched** | **none** — raw bash error, `fail()` not yet defined · exit 1 |
| **A⊘p** | Phase 0 `ukb enforce --pre` fails | `:212` | untouched | `TRANSACTION INCOMPLETE …` · exit 4 |
| **A⊘a** | Phase 1 refused by the authority — **8 distinct refusal points** (§7.2) | `:216` | **byte-identical** | `TRANSACTION INCOMPLETE — ukb build failed` · exit 1 |
| **A✗** | a phase in 2…9 fails | `:221-259` | **mutated, unsealed** | `TRANSACTION INCOMPLETE …` · exit 1/2/4 |

**[INFERRED]** `A∅` and `A⊥` are new and neither is a subclass of Phase 4's three: `A∅` **exits 0** like `A✓` while doing nothing, and `A⊥` fails with no governance message at all.

### 7.2 The eight refusal points inside `commit()`

**[MEASURED]** **P6-7**, `commit()` `:870-933`, in order:

```
  with _ledger_lock(path):                                    <- REFUSAL 1  LedgerWriteRefused
      raw_before, before = read_preimage_bytes(path)              (contention, or fcntl None)
      assert_append_only(before, ledger)                       <- REFUSAL 2  removal / reissue /
      report = build_manifest(before, ledger, actor, path)         record-body / duplicate id
      used = _verify_permit(permit, report, actor, path, …)    <- REFUSAL 3  PermitRefused
      if _read_bytes_or_none(path) != raw_before:              <- REFUSAL 4  R-2 pre-write recheck
          raise LedgerWriteRefused(...)
      ══════════════════ writer(path, ledger)  ═══════════════════  THE MUTATION POINT
      raw_after = _read_bytes_or_none(path)
      if raw_after is None:        _restore(...)               <- REFUSAL 5  silent writer  E2-F2
      json.loads(raw_after) -> except: _restore(...)           <- REFUSAL 6  unparseable
      if persisted != ledger:     _restore(...)                <- REFUSAL 7  divergent writer E2-F1
      _refuse_unmoved_allocation(report) -> _restore(...)      <- REFUSAL 8  R-8 contradiction
      return report
```

**[INFERRED]** Refusals **1–4** occur before the writer: nothing was written. Refusals **5–8** occur after: bytes reached disk and `_restore` put the pre-image back. **[MEASURED]** `PHASE1:§R-7` verified `read_bytes() == original` on all five divergence tests, including the absent-pre-image case.

**[INFERRED] Two consequences.** (i) All eight end byte-identical, so `PHASE4`'s `A⊘` is **correct in outcome** for every one of them — the binary is sound and the taxonomy is richer. (ii) **Exactly four of the eight traverse R-7w's window** (`:893` → `:921`). This **confirms** `PHASE4:§G.3`: a *successful* run never enters it, and only a *failing* run does — *"which, if it happened, would be a defect to fix, not evidence to bank."* Phase 4 got this right, and §7.2 supplies the enumeration it asserted.

**[MEASURED]** Refusal 8 is reachable **without any writer defect**: `_refuse_unmoved_allocation` fires on `allocating and bytes_changed is False`. **[INFERRED]** But §3.6 shows the re-run's manifest is `allocating=False`, so refusal 8 is unreachable on the idempotent re-run — the contradiction it names cannot arise there. Its own docstring says as much: *"once the persisted document is compared against the authorized one, this state is unreachable through `commit()`."*

### 7.3 Run-B outcome classes

| Code | Outcome | Tracked state |
|---|---|---|
| **B✓** | `commit` returns; gate reaches the target surface | mutated |
| **B⊘** | `PermitRefused` or `LedgerWriteRefused` — the same 8 points | **untouched** |
| **B✗** | `commit` succeeded; a downstream surface emission or the gate failed | **mutated, inconsistent** |

**[INFERRED]** Run B has no `A∅`/`A⊥` analogue: `uga_engine.py` has no re-entrancy lock file of its own — only `_ledger_lock`, whose failure is refusal 1, a genuine `LedgerWriteRefused`.

### 7.4 Path enumeration

```
PATHS FROM EXECUTION-AUTHORIZED

  position orderings (A-first | B-first) ...................  2   [MEASURED] P4-1, P4-5: free
  run in position 1  x  run in position 2 ..................  6 x 3  (or 3 x 6)
  ───────────────────────────────────────────────────────────────
  RUN-OUTCOME PATHS ........................................ 36   2 x 18

  of which both runs succeed (A✓ ∧ B✓) .....................  2   one per ordering
      each then branches on confirmation:
          V-12 / EV-23  ∈ {pass, FALSE-pass, fail} .........  3   [MEASURED] §6.6
          V-13 / EV-24  ∈ {pass, fail} .....................  2
          V-14 / EV-25  ∈ {pass, fail} .....................  2
      confirmation branches per ordering ................... 12
  ───────────────────────────────────────────────────────────────
  TOTAL DISTINCT PATHS ..................................... 58   34 + (2 x 12)

  PATHS REACHING EXECUTION-COMPLETED .......................  4
      GENUINE  (V-12 truly passed) .........................  2   one per ordering
      FALSE    (V-12 falsely passed — §6.6 cases B / D / F) .  2   one per ordering

  PATHS REACHING EXECUTION-COMPLETED ON THE PACKAGE
  AS SPECIFIED (IA-4 static) ...............................  0
      [MEASURED] §3.6 — EV-23 is unproducible, so V-12 cannot
      be truly passed; only the FALSE variant is reachable.
```

### 7.5 Path properties

| Path class | Count | Reachable | Authorized | Reversible | Blocker-producing | Unknown-producing |
|---|---|---|---|---|---|---|
| Both succeed, confirmation clean | 2 | yes | yes | **no** (semantically) | no | **no** — both retired |
| Both succeed, `V-12` **falsely** passes | 2 | **yes** | yes | no | no | **no — falsely** |
| Both succeed, confirmation fails | 10 | yes | yes | no | no | 1 or 2 remain |
| One succeeds, other refused cleanly | 8 | yes | yes | **yes** — byte-identical | no | 1 remains |
| One succeeds, other fails mid-run | 8 | yes | yes | partial — `R-A`+`R-B` | no | 1 remains |
| **`A∅` no-op** paths | 6 | **yes** | vacuously | **yes** — nothing happened | no | 2 remain |
| **`A⊥` abort** paths | 6 | **yes** | vacuously | yes | no | 2 remain |
| Both refused cleanly | 4 | yes | yes | yes | no | 2 remain |
| Both fail mid-run | 4 | yes | yes | `R-A`+`R-B` both scopes | no | 2 remain |
| Pre-writer refusals | *(within the above)* | yes | yes | **yes** — nothing written | no | unchanged |
| Post-writer refusals (`_restore`) | *(within the above)* | yes | yes | **yes** — byte-identical, but **R-7w traversed** | no | unchanged |

```
PATHS THAT ARE REACHABLE ................................. 58 of 58
PATHS THAT ARE AUTHORIZED ................................ 58 of 58   (A∅/A⊥ vacuously)
PATHS THAT ARE FULLY REVERSIBLE .......................... 28
PATHS THAT ARE SEMANTICALLY IRREVERSIBLE ................. 30   any landed allocation
PATHS THAT PRODUCE A NEW BLOCKER .........................  0
PATHS THAT LEAVE >=1 UNKNOWN OPEN ........................ 54
PATHS THAT RETIRE BOTH UNKNOWNS ..........................  4   of which 2 do so FALSELY
```

**[INFERRED]** **No path produces a new blocker.** This confirms `PHASE4:§H.4` and `PHASE5:§H.0` across the enlarged space: the five governance-dependent blockers are closed by governance plus implementation, and validation *reveals* defects rather than creating them.

---

## 8. Terminal-state analysis — Q6

### 8.1 The seventeen terminal states reachable after authorization

`Y-1 … Y-3` are new to this phase. Residuals are **3** in every row; what varies is latent versus active.

| # | Reached by | Blockers | Unknowns | Residuals | Rollback available | Repository integrity |
|---|---|---|---|---|---|---|
| **Y-1** | `A∅` — lock no-op, exit 0 | 0+d | **2** | 3 · **latent** | not needed | **intact** |
| **Y-2** | `A⊥` — lock corrupt, exit 1 | 0+d | **2** | 3 · latent | not needed | **intact** |
| **Y-3** | `A⊘p` — Phase 0 gate fails | 0+d | 2 | 3 · latent | not needed | intact; `.runtime` seq +1 |
| **T-6** | `A⊘a ∧ B⊘` | 0+d | 2 | 3 · latent | not needed | **byte-identical** |
| **T-7** | `A✗ ∧ B⊘` | 0+d | 2 | 3 · **active** | `R-A`+`R-B`+`R-C` | **mutated, unsealed** |
| **T-8** | `A⊘a ∧ B✗` | 0+d | 2 | 3 · active | `R-A`+`R-B` | mutated, inconsistent |
| **T-9** | `A✗ ∧ B✗` | 0+d | 2 | 3 · active | both scopes | mutated, unsealed |
| **T-2** | `A✓ ∧ B⊘` | 0+d | **1** UK-2 | 3 · active | not needed | sealed; gate still red |
| **T-3** | `A✓ ∧ B✗` | 0+d | **1** UK-2 | 3 · active | `R-A`+`R-B` (B scope) | mutated, inconsistent |
| **T-4** | `A⊘a ∧ B✓` | 0+d | **1** UK-1 | 3 · active | not needed | intact + `by_object` minted |
| **T-5** | `A✗ ∧ B✓` | 0+d | **1** UK-1 | 3 · active | `R-A`+`R-B` (A scope) | mutated, unsealed |
| **T-1a** | `A✓ ∧ B✓`, confirmation clean | **0** | **0** | 3 · active | none | **complete** |
| **T-1b** | `A✓ ∧ B✓`, **`V-12` falsely passes** | **0** | **0 — falsely** | 3 · active | none | **complete but unverified** |
| **T-1c** | `A✓ ∧ B✓`, `V-12` genuinely fails | 0+d | 1 UK-1 | 3 · active | none | complete; drift gate can never be green |
| **T-1d** | `A✓ ∧ B✓`, `V-13` fails | 0+d | 0 | 3 · active | none | complete; authority regressed |
| **T-1e** | `A✓ ∧ B✓`, `V-14` fails | 0+d | 0 | 3 · active | none | complete; a residual control did not fire |
| **T-1f** | `A✓ ∧ B✓`, `EV-22` gate short of target | 0+d | 1 UK-2 | 3 · active | none | complete; surface not reached |

```
TERMINAL STATES REACHABLE AFTER AUTHORIZATION .................. 17
    carried from PHASE4 §H.2 / PHASE5 §I.1 ......................  9   T-2 … T-9 (+T-1 split)
    T-1 refined into six confirmation outcomes ..................  6   T-1a … T-1f
    new in this phase ...........................................  3   Y-1, Y-2, Y-3
    requiring rollback ..........................................  5   T-3, T-5, T-7, T-8, T-9
    with residuals still LATENT .................................  4   Y-1, Y-2, Y-3, T-6
    reaching 0 blockers AND 0 unknowns ..........................  2   T-1a, T-1b  <- one is FALSE
    reaching 0 blockers AND 0 unknowns GENUINELY ................  1   T-1a
```

### 8.2 Does any terminal state falsely appear successful? **YES — one**

**`T-1b`.** **[MEASURED]** §6.6. Reached when `A✓ ∧ B✓` and the `V-12` re-run hits lock case **B**, **D** or **F**: `register.sh` prints `nested/concurrent call is a no-op`, exits 0, and produces **zero byte changes across the four guard directories** — satisfying `EV-23`'s condition exactly as written.

**[INFERRED]** The state reports `0 blockers · 0 unknowns · EXECUTION-COMPLETED`, and `UK-1` has been retired on evidence that measured nothing. **This is the only false-success state, and it is reachable through an ordinary operational accident** — a `SIGKILL`ed first run, or a clock step — not through malice or an exotic sequence.

**[EXEC-REQ]** Closed by §6.6's three additions to `EV-23`. With them, `T-1b` becomes unreachable and collapses into `T-1c`.

### 8.3 Does any terminal state falsely appear failed? **YES — two**

| State | Why it appears failed | Why it is not |
|---|---|---|
| **`Y-2`** (`A⊥`) | **[MEASURED]** exit 1 with a raw `bash: corrupt: unbound variable` and **no** `TRANSACTION INCOMPLETE` line. Indistinguishable, from the exit code alone, from a genuine mid-transaction failure | **[MEASURED]** the abort occurs at `:189`, **before** Phase 0. Tracked state is untouched, no allocation occurred, and **no rollback is needed** — but an operator following `GA-8` would run `R-A` anyway, and `R-A` on a clean tree is a no-op that nonetheless consumes the rollback authorization |
| **lock case E** | **[MEASURED]** prints `bash: 1788054239 -  : syntax error: operand expected` to stderr, which reads as a hard failure | **[MEASURED]** the script then **proceeds normally and the transaction runs**. `set -e` does not fire because the failure is inside an `if` condition. The alarming output is followed by a genuine, complete transaction |

**[INFERRED]** Case E is the more dangerous of the two, because the operator sees an error and the machine performs a **real, irreversible allocation**. An operator who reacts to the stderr line by aborting and rolling back would be rolling back a *successful* transaction.

### 8.4 Does any terminal state leave hidden damage? **YES — three classes**

| Class | States | Measured basis |
|---|---|---|
| **The 28th anonymous object** | `Y-1`, `Y-2`, `Y-3`, `T-6`, and any abandonment past `S-2` | **[MEASURED]** `PHASE4` P4-10 + `PHASE5:§I.4` — the register is the 18th `00-BOOK/DATA/*.json`, all of which are in `by_object`, and **[MEASURED]** **P6-3** `0` of them are `by_path`-eligible, so `register.sh`'s mint can never clear it. `UGA-INV-01` sits at **28** rather than 27 |
| **`.runtime` sequence advance** | every state past `S-3` | **[MEASURED]** gitignored (`.gitignore:12`), not restorable, declared non-history. **612 / 19 / 1** today |
| **A poisoned `permit_id`** | any state reached after a lapse-and-reissue | **[MEASURED]** §6.13 — `len(matches) > 1` makes the id permanently unusable. **Not named in any prior phase**, and not repaired by `R-A`, `R-B`, `R-C` or `R-D` |

**[INFERRED]** The third is new and is the only hidden damage that **no rollback procedure addresses**. `R-D` restores or discards the register wholesale; it cannot de-duplicate a `permit_id` that legitimate append-only issuance created twice.

### 8.5 Does any terminal state leave authorization consumed? **YES — eleven**

**[MEASURED]** Authorization is consumed the moment a run lands, by two independent mechanisms: `preimage_digest` moves (`PHASE4` P4-7), and under `B2` a use record is written.

| Consumption count | States |
|---|---|
| **0 consumed** | `Y-1`, `Y-2`, `Y-3` — no `commit()` reached |
| **0 consumed, permits intact** | `T-6` — both refused; **[MEASURED]** every refusal restores the pre-image byte-for-byte, so both permits **still verify** |
| **1 consumed** | `T-2`, `T-4`, `T-7`, `T-8` |
| **2 consumed** | `T-3`, `T-5`, `T-9`, `T-1a … T-1f` |

```
STATES LEAVING >=1 AUTHORIZATION CONSUMED ...................... 11 of 17
STATES IN WHICH A CONSUMED AUTHORIZATION IS RE-VALIDATED BY
ROLLBACK (axis B1 only) ........................................  5   T-3, T-5, T-7, T-8, T-9
    [MEASURED] PHASE2 P2-1: replay ACCEPTED after a byte restore.
    Under B2 the permit stays SPENT while the allocation is UNDONE.
```

---

## 9. Unknown-closure analysis — Q7

### 9.1 UK-1 — `register.sh` end-to-end completion

| Item | Evidence required | Earliest measurable | Requires success? | Obtainable from a failure path? |
|---|---|---|---|---|
| **1** | Phase 1 `commit()` report: `authorization=PERMIT`, `bytes_changed=True`, 9 `by_path` allocations | during run A, phase 1/10 | **yes** | **no** |
| **2** | phases 2/10 … 9/10 each exited 0 | end of run A | **yes** | **no** — **[MEASURED]** structurally enforced: `fail()` `:201` exits and every phase is `\|\| fail` |
| **3** | terminal line `TRANSACTION COMPLETE …` **and** exit 0 | end of run A | **yes** | **no** |
| **4** | `register.sh --observe` → `RC=0` after the registers **and the permit's own register write** are staged | after run A + `EV-20` | **yes** | **no** |
| **5** | a second `register.sh` produces **zero** byte changes across the four guard dirs | **only at the second run** | **yes** | **no** |

**[INFERRED] Three findings.**

1. **`UK-1` cannot be closed from any failure path.** All five items require `A✓`. This is stronger than Phase 4 states and it is structural: item 2 is enforced by the `|| fail` chain, so a single phase failure removes items 2–5 simultaneously.
2. **Item 5 is currently unreachable** — §3.6. `EV-23` has no producer.
3. **Item 5 is falsifiable-by-accident** — §6.6, §8.2. Even once a producer exists, item 5 as worded is satisfied by a run that never happened.

**[EXEC-REQ] `UK-1`'s closure set must be amended in two places**, and the amendments are independent:

> **Item 5′** — a second `register.sh`, **authorized for a non-allocating manifest** (§3.6 `C-1` or `C-2`), emits `TRANSACTION COMPLETE`, does **not** emit `nested/concurrent call is a no-op`, and produces zero byte changes across the four guard directories, with `.register.lock` verified absent immediately beforehand.
>
> **Item 6 (new)** — the re-run's `commit()` report shows `authorization=NO_ALLOCATION` (or a fresh empty-manifest permit) and `bytes_changed=False`, establishing that the idempotence claim in `register.sh`'s own header — *"safe to run repeatedly"* — is **authorized**, not merely observed.

**[INFERRED]** Item 6 is a genuinely new closure requirement. Phase 4 treated the idempotent re-run as free; **[MEASURED]** §3.6 establishes it needs its own authorization, so `UK-1` has **six** components, not five.

### 9.2 UK-2 — post-mint clearance and gate greenness

| Item | Evidence required | Earliest measurable | Requires success? | Obtainable from a failure path? |
|---|---|---|---|---|
| **1** | `uga_engine run --mint` committed: `authorization=PERMIT`; `by_object` count equals the count measured at issuance (`EV-14`) | during run B | **yes** | **no** |
| **2** | `UGA-INV-01 violations=0` — down from **27** | after run B | **yes** for a *positive* answer | **[INFERRED] YES for a negative answer** — see below |
| **3** | `UGA-INV-10` at the model's target: surface **30** (`Aud1`/`Aud2`) or **29** (`Aud3`) | after run B | yes | no |
| **4** | no invariant that passed at `EV-13` fails at `EV-22`; **[MEASURED]** baseline 2 of 30 FAIL, so **28** must still pass | after run B | yes | no |

**[INFERRED] The asymmetry between UK-1 and UK-2, and it is the sharpest result of §9.** `UK-2` asks *"do the anonymous objects clear in one mint?"* That is a **question with two admissible answers**. A run that lands and leaves `UGA-INV-01 > 0` **answers it negatively** — and an unknown answered negatively is *resolved*, not still open. **[MEASURED]** `PHASE4:§B.2` predicted the mechanism: the population is not stable and grows as a consequence of the program's own steps.

**[INFERRED]** By contrast `UK-1` asks *"does the transaction complete?"* A failure does not answer it — it establishes that the transaction did not complete **on this attempt**, which is compatible with completion on the next. So:

```
UK-1  resolvable ONLY by success                    (0 of 6 items from a failure path)
UK-2  RESOLVABLE from a partial path                (item 2 admits a negative answer)
      but CLOSABLE FAVOURABLY only by success       (items 1, 3, 4 require B✓)
```

**[EXEC-REQ]** `GA-6` must therefore record `UK-2`'s **negative** closure condition as well as its positive one, or a negative result will be misfiled as an open unknown and a second mint attempted without a fresh determination.

### 9.3 Q7 summary

```
UK-1  components ...................  6   (PHASE4 states 5; item 6 derived §3.6)
      currently reachable ..........  4   items 1-4
      currently UNREACHABLE ........  2   item 5 (no producer) + item 6 (new)
      obtainable from failure ......  0
      earliest closure .............  the SECOND register.sh run

UK-2  components ...................  4
      currently reachable ..........  4
      obtainable from failure ....... 1 of 4  (item 2, negatively)
      earliest closure .............  immediately after run B's gate
      requires re-measurement before issuance ...... YES  (EV-14; the population
                                                     is 28 today, not 27)
```

---

## 10. Exact blocker / unknown / residual counts

### 10.1 Blockers

```
BLOCKERS
    today, artifact level ...........................  5   E-4A, E1-F3, E-3, RES-1, RES-2
    today, decision level ...........................  5   (0 once GA-1 exists)
    after governance + implementation ...............  0
    introduced by the transition package ............  0
    introduced by this determination .................  0
    revealed defects (not blockers) — new this phase .  4   §12.3
```

### 10.2 Unknowns

```
UNKNOWNS
    named by PHASE3 / PHASE4 / PHASE5 ...............  2   UK-1, UK-2
    components ......................................  10  UK-1: 6 (was 5) · UK-2: 4
    components currently unreachable ................  2   UK-1 items 5, 6
    after T-1a (genuine completion) .................  0
    after T-1b (false completion) ...................  0 reported · >=1 ACTUAL
    after any other terminal state ..................  1 or 2
    closable by any of the 12 models ................  0
    dischargeable without a mutating run ............  0
```

### 10.3 Residuals

```
RESIDUALS ..........................................  3   RES-3, RES-4, R-7w
    closed by execution .............................  0
    reduced (evidence class only) ...................  2   RES-3, RES-4
    unchanged .......................................  1   R-7w
    latent today ....................................  3
    activated latent -> live at the FIRST landed write  3
    states in which they remain latent ..............  4 of 17   Y-1, Y-2, Y-3, T-6

  CONFIRMED this phase, not corrected:
    R-7w is exercised ONLY by refusals 5-8 of the 8 in commit() (§7.2).
    A successful run never enters :893 -> :921.  PHASE4 §G.3 is exactly right,
    and §7.2 supplies the enumeration behind its assertion.
```

### 10.4 Two Phase 5 counts that change

| Count | Phase 5 | Phase 6 | Basis |
|---|---|---|---|
| Artifacts required before execution | **41** | **42** | `IA-12` — §3.5 |
| Implementation artifacts | **11** | **12** | `IA-12` |
| Machine-checkable approvals | **2** | **2 or 3** | §3.6 — 2 under closure `C-1`, 3 under `C-2`; axis-`D`-parameterized |
| Axis-parameterized content items | **5** | **6** | §6.9 |
| Terminal states after authorization | 10 (Phase 4) / 14 (Phase 5, whole program) | **17** after authorization | §8.1 |
| `by_path` mints for run A | **9**, stated invariant | **9 or 10** | §6.3 — `Aud1`/`B2b` placement |

**[INFERRED]** Every other count in `PHASE5:§J` is confirmed unchanged: 9 governance artifacts, 21 pre-run evidence items, 14 gate conditions, 10 stages, 2 mutating runs, 4 rollback procedures, 1 non-restorable class, 12 of 12 models.

---

## 11. Readiness classification — Q8

### 11.1 The six states and their boundaries

| State | Reachable? | Proof of the boundary |
|---|---|---|
| **NOT READY** | **not occupied** | **[MEASURED]** the twelve Phase-1 closures are in the tree and green: `PHASE1:§4` and `PHASE3` P3-8 — **77 passed**. `ledger_authority.py` 933 lines, re-verified. The boundary out of NOT READY was crossed by Phase 1. |
| **READY-CONDITIONAL-ON-GOVERNANCE-SELECTION** | **OCCUPIED TODAY** | **[MEASURED]** **P6-12**: register absent; ledger `sha256 8471e709…` unchanged; 0 of 17–20 tasks performed; no selection record exists. Boundary: `GA-1` does not exist, so `IA-1` cannot be written. |
| **READY-FOR-EXECUTION** | **reachable, 12/12** | **[MEASURED]** `PHASE4:§I.3` — every Stage-0 precondition is verifiable read-only. **Boundary sharpened this phase:** `EV-1`'s evidence requires the full `PHASE05:§E.0` invocation, not `pytest <file>` (§6.11). The boundary is unchanged; one of its evidence items was misnamed. |
| **EXECUTION-AUTHORIZED** | **reachable, 12/12 — twice** | **[MEASURED]** `PHASE5:§K.4`, confirmed. **Refined this phase:** it must be entered **twice for the two mutating runs and a third time for the re-run** (§3.6). The third entry has **no producer**, so the boundary into `EXECUTION-AUTHORIZED(re-run)` is **not crossable on the package as specified.** |
| **EXECUTION-COMPLETED** | **reachable in principle; NOT on the package as specified** | **[MEASURED]** requires `A✓ ∧ B✓ ∧ EV-23 ∧ EV-24 ∧ EV-25`. `EV-23` is unproducible (§3.6) and falsifiable (§6.6). **[INFERRED]** So of the 4 paths reaching it (§7.4), **0 are genuine** today and 2 are false. Boundary: crossable **iff** closure `C-1` or `C-2` is adopted **and** `EV-23` is strengthened. |
| **EXECUTION-CERTIFIED** | **UNDEFINED — and that is the finding** | **[MEASURED]** no artifact in Phases 0–5 defines it. Two candidate definitions give opposite answers: **(a) gate-greenness** — `register.sh --guard` returns 0 and `uga_engine gate` reaches its target ⇒ **reachable**, after committing the regenerated registers; **(b) residual-freedom** ⇒ **unreachable**, because **[MEASURED]** `R-7w` is closable only by moving serialization inside the authority, which `PHASE1:§R-7` declined as *"a larger change than this phase covers"*, and `PHASE3:§E.7` established all three residuals survive every one of the 12 models. |

### 11.2 The boundary map

```
  NOT READY
     │  crossed by PHASE1 — 12 closures landed, 77 tests green            [MEASURED]
     ▼
  READY-CONDITIONAL-ON-GOVERNANCE-SELECTION          ◀══ OCCUPIED TODAY
     │  requires GA-1 … GA-9  (9 artifacts, 7 new in PHASE5)              [GOV-REQ]
     │  requires IA-1 … IA-12 (12 artifacts, 1 new here)                  [EXEC-REQ]
     │  requires IA-C1 staged · IA-C2 COMMITTED                           [MEASURED]
     ▼
  READY-FOR-EXECUTION
     │  requires EV-1 … EV-10, EV-12 … EV-14, EV-16   (Stage 0 green)
     │  EV-1 needs the full PHASE05 §E.0 invocation   ◀── §6.11 correction
     ▼
  EXECUTION-AUTHORIZED (run 1)         ── G-1..G-13 ∧ G-14(run 1)
     │  lapses on any ledger write, and on any commit if head-bound       [MEASURED]
     ▼
  EXECUTION-AUTHORIZED (run 2)         ── re-measure, re-issue at the NEW pre-image
     │
     ▼
  EXECUTION-AUTHORIZED (re-run)        ══ NO PRODUCER ═══════════════════ [DEFECT]
     │  the run-1 permit fails TWO strict bindings on a non-allocating
     │  manifest; only NO_ALLOCATION or a fresh empty-manifest permit works
     ▼
  EXECUTION-COMPLETED                  ── 4 paths: 2 FALSE, 2 genuine-but-blocked
     │  reachable iff C-1 or C-2 adopted AND EV-23 strengthened
     ▼
  EXECUTION-CERTIFIED                  ══ UNDEFINED BY EVERY ARTIFACT ═══ [DEFECT]
        (a) gate-greenness   -> reachable
        (b) residual-freedom -> UNREACHABLE (R-7w is permanent)
```

```
STATES REACHABLE ..................................  4 of 6
    occupied today .................................  1   READY-CONDITIONAL-ON-GOV-SELECTION
    reachable with the package as specified ........  2   READY-FOR-EXECUTION,
                                                          EXECUTION-AUTHORIZED (runs 1 and 2)
    reachable only after closing U-B and U-C .......  1   EXECUTION-COMPLETED
    not defined by any artifact .....................  1   EXECUTION-CERTIFIED
    not occupied and not re-enterable ...............  1   NOT READY
```

### 11.3 The required answer

> **After governance selection, implementation, authorization and validation are complete, does any remaining non-governance uncertainty prevent execution completion from being a fully determined process?**

# **YES.**

```
  THREE uncertainties.  ONE irreducible.  TWO closable by determination.

  U-A  IRREDUCIBLE.  UK-1 and UK-2 cannot be measured before the runs.
       [MEASURED] --plan is absent from ukbx.py entirely, so register.sh
       phases 2, 3, 4 and 8 have no dry-run mode (PHASE4 P4-6).  No
       determination and no evidence closes this; only the runs do.
       => execution completion is not fully determined IN ADVANCE, and
          cannot be made so.

  U-B  CLOSABLE.  The second register.sh run is unauthorizable as specified.
       [MEASURED] ukb.py:892-894 returns early for allocated paths, so the
       re-run's manifest is allocating=False / total=0 / allocated={}, and the
       run-1 permit fails manifest_digest (:735) AND preimage_digest (:743).
       => EV-23 unproducible => UK-1 item 5 unreachable.
       CLOSURE: adopt C-1 (conditional IA-4, pattern already at ukb.py:2380-2384)
                or C-2 (a third permit; axis-D-dependent).  Neither preferred.

  U-C  CLOSABLE.  Execution completion can be falsely reported.
       [MEASURED] register.sh:189-192 exits 0 having run nothing in 3 of 7
       reproduced lock states (P6-6).  EV-23's condition — "zero byte changes" —
       is then satisfied trivially, and UK-1 is retired on nothing.
       CLOSURE: EV-23 must additionally require the TRANSACTION COMPLETE line,
                the ABSENCE of the no-op line, and .register.lock verified absent.

  ── WITH U-B AND U-C CLOSED ────────────────────────────────────────────────

  Execution completion becomes a fully determined process IN THE SENSE THAT
  MATTERS: every path is enumerated (58), every terminal state is enumerated
  (17), every failure is diagnosable, every success is verifiable, and no path
  produces a new blocker.  What remains undetermined is only U-A — the OUTCOME
  of the runs, which is precisely what the runs exist to determine.

  A process whose every path is known and whose outcome is not is not an
  underdetermined process.  It is a MEASUREMENT.
```

---

## 12. Stop condition

### 12.1 Determinations made

- **Q1 Completeness — NO.** 1 artifact missing (`IA-12`), 1 under-specified (`IA-4`), 2 evidence items unproducible (`EV-1` by its named method, `EV-23` at all), 1 field produced but never consumed (`single_use`). **38** producer→consumer edges, **3** unsatisfied. Corrected artifact count **42**.
- **Q2 Sufficiency — NO.** 0 of 14 conditions sufficient; **2** necessary for the mechanical act; **12 unenforceable by the machine**. A gate can pass while execution is impossible (3 ways) and fail while execution remains possible (`G-8`, `G-12`).
- **Q3 Minimality — NO, deliberately.** One-run minimum **6**; both-runs minimum **10**; unknowns-retired minimum **33**; authorized-determinate-recoverable minimum **42**. Only **3** items are `NE`, and all three are model-required.
- **Q4 Hidden dependencies — 14**, each reproduced and measured: **9** consequential, **2** benign-measured, **3** corrections.
- **Q5 Paths — 58**, from **6** run-A outcome classes (Phase 4 had 3) and **8** refusal points inside `commit()`. **4** reach `EXECUTION-COMPLETED`: 2 false, 2 genuine-but-currently-blocked. **0** produce a new blocker.
- **Q6 Terminal states — 17.** **1** falsely successful (`T-1b`), **2** falsely failed (`Y-2`, lock case E), **3** hidden-damage classes (one of which no rollback addresses), **11** leaving authorization consumed.
- **Q7 Unknowns.** `UK-1` has **6** components, not 5; **2** are unreachable; **0** obtainable from a failure path. `UK-2` has 4, and **item 2 is resolvable negatively from a partial path** — the only unknown component in the chain that a failure can answer.
- **Q8 Readiness — 4 of 6 states reachable.** `EXECUTION-COMPLETED` reachable only after closing U-B and U-C. `EXECUTION-CERTIFIED` **undefined by every artifact in the chain**.

### 12.2 What was confirmed rather than corrected

**[INFERRED]** Recorded because a review that reports only defects has not been rigorous about the parts that hold.

| Confirmed | Basis |
|---|---|
| The **2-mutating-run minimum** | `register.sh` never invokes `uga_engine` — re-verified by full read of all 282 lines, the only occurrence being prose at `:157`; populations disjoint; `DATA/` excluded from `by_path` (**P6-3**: `0` of 17 eligible) |
| **Stage 0 is read-only of tracked state** | Each of `V-1…V-6` traced to a non-writing path; `--plan` returns before any write in both tools (`ukb.py:1291-1298`, `uga_engine.py:2075-2085`) |
| **Authorization is per-run and state-bound** | `:743-749` + `PHASE4` P4-7; and §4.4 adds two further lapse causes Phase 5 did not name |
| **R-7w is exercised only by failure** | §7.2 — exactly 4 of 8 refusal points traverse `:893`→`:921`; a successful run enters none. `PHASE4:§G.3` is exactly right |
| **No path produces a new blocker** | §7.5 — across 58 paths and 17 terminal states |
| **`R-A` is complete and non-destructive** | tracked = on-disk, 0 dirty in all four guard directories (**P6-12**) |
| **All 12 models remain equally positioned** | Every count in §10 is model-invariant except the two in §10.4, and both of those vary by *axis value*, not by model quality |
| **`PHASE5` P5-1 / P5-2 / P5-3 / P5-4** | Independently re-derived here from source; §6.2 supplies the reason P5-1's staging refinement is safe |

### 12.3 Corrections to the inputs

| # | Claim | Correction | Consequence |
|---|---|---|---|
| **1** | `PHASE3:§B.1` — the register producer has *"no design freedom"*; its shape is *"already fully determined by the consumption set"* | **[MEASURED]** **5 of 9** fields are elective (`head`, `scope`, `scope.maps`, `scope.max_allocations`, `expires_at`) | `IA-12` required; `PHASE5:§B.7`'s claim that the authority enforces `GA-7`'s scope bound is **conditional on the producer emitting `scope`** |
| **2** | `PHASE3:§C.0` `F-4` — *"A verified permit reaches `ukb build --mint`"* | **[MEASURED]** a **static** plumbing cannot authorize the non-allocating re-run, which fails **two** strict bindings | `EV-23` unproducible; `UK-1` item 5 unreachable; `UK-1` gains item 6 |
| **3** | `PHASE4:§J.5`, `PHASE5:§J.5` — *"9 `by_path` mints"*, stated model-invariant | **[MEASURED]** **9 or 10**: under `Aud1`/`B2b`, `IA-11`'s placement decides, and the `-audit.json` ban forces it out of the one directory that would exclude it | run A's manifest is placement-dependent; `EV-3` must be measured **after** `IA-11` lands |
| **4** | `PHASE4:§D.1` V-1, `PHASE5` `EV-1` — *"`pytest platform/tests/test_ledger_authority.py`"* | **[MEASURED]** fails on the `pytest_scope` plugin import and on `--cov-fail-under=90`. `PHASE05:§E.0` recorded the verified invocation, which was lost between Phase 0.5 and Phase 4 | `EV-1` must name `PYTHONPATH=. .ec1-venv/bin/pytest … --no-cov` |
| **5** | `PHASE1:§R-11`, quoted as current by `PHASE4:§G.3` and `PHASE5:§L.3` — `_canonical` **1 786 167** vs writers **2 274 511** | **[MEASURED]** today **1 790 825** vs **2 279 169** | `CX-6`'s substance intact — the inequality holds, so document comparison remains forced and `A4` remains CONTRADICTED. Figures stale by the Phase-1 era |
| **6** | `PHASE4:§H.2` row `T-0` / `PHASE5:§I.1` — run A has 3 outcomes | **[MEASURED]** **6**, including two that Phase 4's taxonomy cannot express: `A∅` (**exit 0**, nothing done) and `A⊥` (exit 1, no governance message) | `T-1b` is a false-success state; `Y-1`, `Y-2` are new terminal states |

**[INFERRED]** Corrections 1–4 and 6 change what an implementer must do. Correction 5 changes only a cited number. **None overturns a structural result of Phases 2–5.**

### 12.4 Evidence — the twelve probes

**No probe invoked `register.sh` in any mode, `uga_engine` in any mode, or `pytest`.** Probes **P6-6** and the `git`-semantics element of **P6-3** ran in temporary directories under `/tmp` that are not this repository and were removed before this document was written.

| ID | Established | Method | Repository touched |
|---|---|---|---|
| **P6-1** | 4 strict / 5 elective permit bindings | source read `:709-804` | read-only |
| **P6-2** | `_issue`'s exact 8-key shape; `head` bound; `expires_at: None`; `scope.max_allocations = total`; `single_use` dead | source read `platform/tests/test_ledger_authority.py` | read-only |
| **P6-3** | eligibility = `git ls-files --cached` (tracked **or staged**); `INCLUDE_EXTENSIONS` = 4; `EXCLUDE_DIR_PREFIXES` = 13; **`by_path` gap = 9**, enumerated; determination docs `??` and therefore ineligible | `ukb._iter_files()` + `artifacts.json`, in-process, read-only | read-only |
| **P6-4** | **`preimage_digest` is interpreter-invariant**: `3a2a2532e006c326…`, canonical length **1 790 825**, under **3.14.4** and **3.12.13** | `LA.load_preimage` + `LA._canonical` under both interpreters | read-only |
| **P6-5** | `CX-6` figures today: **1 790 825** vs **2 279 169** | `wc -c` + P6-4 | read-only |
| **P6-6** | `register.sh`'s guard has **7** behaviours, **3** exiting 0 without running; empty lock → stderr error then proceeds; non-numeric → exit 1 before `fail()` exists; lock absent today | the guard's arithmetic reproduced verbatim under `bash -euo pipefail` in `/tmp`, since removed | **no** |
| **P6-7** | `commit()`'s **8** refusal points — 4 pre-writer, 4 post-writer, all `_restore`-backed | source read `:841-933` | read-only |
| **P6-8** | `_path_identity` returns early for allocated paths — the re-run allocates nothing and calls no clock | source read `ukb.py:885-913` | read-only |
| **P6-9** | `addopts` = `-p engine.universal_discovery.pytest_scope`, `--cov-report=xml`, `--cov-fail-under=90`; `.coverage*` and `coverage.xml` gitignored | source read `pyproject.toml`, `.gitignore` | read-only |
| **P6-10** | the two strict `actor` literals | source read `ukb.py:1287`, `uga_engine.py:2079`/`:2098` | read-only |
| **P6-11** | `git_head` = `git -C <dir> rev-parse HEAD`, `timeout=15`, `None` on failure → fail-closed; `--plan` prints the **full** 40-char sha; `git 2.54.0` | source read `:580-598`, `ukb.py:1293-1297` | read-only |
| **P6-12** | baseline unmoved | `shasum`, `git status --porcelain`, `git ls-files`, `.runtime` read | read-only |

**Non-mutation, verified before and after every probe:**

```
$ shasum -a 256 00-BOOK/DATA/id-ledger.json
8471e709b178a9a09909bca55f2e8eccb78161db8423026d1d26e4f35c41c20b        (unchanged)
$ git status --porcelain -- 00-BOOK/DATA 00-BOOK/REGISTRIES 00-BOOK/CONTROL-TOWER 00-BOOK/PORTAL
(0 lines)
$ ls 00-BOOK/DATA/allocation-permits.json
ls: No such file or directory
$ ls 00-BOOK/tools/.register.lock
ls: No such file or directory
$ .runtime/governance   enforcement 612 · sync 19 · certification 1        (unmoved)
```

### 12.5 Constraint compliance

- **Governance selected: none.** Decisions taken: **0.** Models or axis values recommended, ranked or preferred: **0.** Where a defect admits two closures (`C-1`, `C-2`), both are stated and neither preferred.
- **Implementation changes: none. Permits issued: 0. Register created: no.** `register.sh` invoked: **0 times, in any mode.** `uga_engine run --mint` invoked: **0 times.** `pytest` invoked: **0 times** — deliberately, because `--cov-report=xml` writes a repository file.
- **Repository files modified: none.** This document is the only addition. The two `/tmp` scratch directories were removed within the phase.
- **Recommendations: none.** Every `[EXEC-REQ]` states a requirement the package's own success criteria already imply; none proposes a design.

### 12.6 The terminal position

```
POSITION ................. READY-CONDITIONAL-ON-GOVERNANCE-SELECTION   (unchanged)
AUTHORIZATION STATE ...... NOT-AUTHORIZABLE                            (unchanged)
PACKAGE STATUS ........... INCOMPLETE — 42 artifacts, 3 unsatisfied edges,
                           2 unproducible evidence items
BLOCKERS ................. 5 artifact-level · 0 introduced
UNKNOWNS ................. 2, comprising 10 components, 2 unreachable
RESIDUALS ................ 3, all latent, 0 closable by any of the 12 models
DEFECTS FOUND ............ 4 specification defects · 14 hidden dependencies
DEFECTS CLOSABLE BY DETERMINATION ... 4 of 4
UNCERTAINTY IRREDUCIBLE BY DETERMINATION ... 1   (U-A: the outcome of the runs)
```

**The next act is unchanged and is now better specified.** `GA-1` — a governance decision on the five closure axes — remains the first act, and `GA-7` remains the artifact no phase of this chain can produce for itself. What this phase adds is that **before `GA-1` is taken, four specification defects should be closed**, because all four are closable without any governance input: `IA-12` must be written, `IA-4` must be made conditional, `EV-1` must name its real invocation, and `EV-23` must be made falsifiable. **[INFERRED]** All four are governance-independent in exactly the sense `PHASE05:§B` used the term — they can be closed with no answer to FD-1…FD-5 — which means they belong to the class of work the chain has already demonstrated it can complete.

Phase 6 ends here.
