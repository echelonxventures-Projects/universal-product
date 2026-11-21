# PHASE A — RESIDUAL ELIMINATION DESIGN DETERMINATION

| Field | Value |
|---|---|
| Objective | Determine whether the residuals can be eliminated **completely**, without assuming permanence from prior classification. |
| Premise correction | **Two of the three items the task names are not residuals.** `RES-1` and `RES-2` are **artifact-level blockers** (`PHASE1:§6.2`), and both are **CLOSED in all 12 admissible models** (`PHASE2:§D.2`). The chain's residual set is `{RES-3, RES-4, R-7w}` (`PHASE3:§E.7`). §0.1. |
| Answer, over the task's named set `{RES-1, RES-2, R-7w}` | **All three eliminable, with no new blocker.** |
| Answer, over the chain's actual residual set `{RES-3, RES-4, R-7w}` | **NOT eliminable — for exactly one reason, and it is not the reason the chain expected.** |
| The finding | **`R-7w` is closable.** It is **UNIMPLEMENTED, not impossible.** A mechanism exists that closes it completely, touches **zero writers**, preserves every Phase-1 closure, introduces **zero** new blockers, and uses a primitive the architecture already **names in its own write-sink detection list** (`uga_engine.py:1099`) and **no writer uses** (**[MEASURED]**, §3.1). |
| The obstruction | **`RES-4`** — `flock` is advisory. Closing it requires **mandatory** file locking, which no platform the repository targets provides. This is the sole irreducible item, and no phase before this one identified it as the binding constraint. |
| Consequence for Phase 9 | **Phase 9's conclusion survives; its proof does not.** Premise **π4** — *"Closing `R-7w` requires moving serialization inside the authority"* — is **false**. Outcome B must be re-derived on `RES-4`. §8. |
| Terminal verdict | **A — Residual-free architecture impossible.** §9. |
| Repository files modified | **NONE.** This document is the only addition. Baseline verified at open and close. |

### 0.1 The premise correction, stated before anything rests on it

**[MEASURED]** `PHASE1:§6.2` — *"REMAINING BLOCKERS ... 5: `E1-F3`, `E-3`, `E-4A`, **`RES-1`** permit binds a projection not the doc, **`RES-2`** empty-manifest permits not refused"*. All five are labelled **GOVERNANCE-DEPENDENT blockers**.

**[MEASURED]** `PHASE3:§E.7` — the residual table has exactly three residual rows: **`RES-3`** (MW-3 window), **`RES-4`** (advisory `flock`), **`R-7w`** (post-hoc detection), plus two unknown rows (`UK-1`, `UK-2`).

**[MEASURED]** `PHASE2:§D.2`, the closure matrix, rows `RES-1` and `RES-2`:

| Blocker | G-1 | G-2 | G-3 | **G-4** | **G-5** | **G-6** | **G-7** | **G-8** | G-9 | **G-10** | G-11 | G-12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `RES-1` | PARTIAL | PARTIAL | PARTIAL | **CLOSED** | **CLOSED** | **CLOSED** | **CLOSED** | **CLOSED** | CLOSED | **CLOSED** | PARTIAL | CONTRADICTED |
| `RES-2` | CLOSED | CLOSED | CLOSED | **CLOSED** | **CLOSED** | **CLOSED** | **CLOSED** | **CLOSED** | CLOSED | **CLOSED** | CLOSED | CLOSED |

**[DERIVED]** `RES-1` is CLOSED for every column with `A = A3`; `RES-2` is CLOSED in every column. **[MEASURED]** `PHASE3:§A` fixes `A = A3` and `D ∈ {D1, D2}` in **all 12** admissible models. Therefore **`RES-1` and `RES-2` are CLOSED in 12 of 12 admissible models**, and `PHASE3:§G.1` records the consequence: *"REMAINING BLOCKERS … after implementation completion … **0**."*

**[INFERRED]** The `RES-` prefix is the source of the confusion: `PHASE05:§F.4` derived `RES-1 … RES-4` as one numbered batch and then classified them into two different kinds — `RES-1`/`RES-2` as governance-dependent **blockers**, `RES-3`/`RES-4` as **bounds**. The prefix survived the split. This phase answers the question for **both** sets and states which set each answer belongs to.

### 0.2 Compliance

| # | Constraint | Compliance |
|---|---|---|
| 1 | Read-only investigation | **MET.** 8 read-only probes: `grep`, `sed`, `awk`, and one in-process JSON read of `id-ledger.json`. No write of any kind. |
| 2 | No repository modification | **MET.** This document only. |
| 3 | No mutating command | **MET.** No engine invoked in any mode. |
| 4 | No governance selection | **MET.** No axis assigned. Every closure mechanism below is **governance-independent** in the sense `PHASE05:§B.0(iii)` fixed — its refusal predicate remains a function of `(before, ledger, persisted_bytes)` — and §6 verifies that for each. |
| 5 | No implementation recommendations unless derived | **MET.** §4 catalogues mechanisms **derived from the chain's own measured facts**; §7 identifies minimum-change and minimum-risk architectures because Q6 requires them. No mechanism is preferred beyond what the feasibility question forces, and §7.4 states explicitly what is *not* decided here. |
| 6 | Every statement classified | **MET.** `[MEASURED]` / `[DERIVED]` / `[INFERRED]` throughout. |
| 7 | Distinguish impossible / unimplemented / unanalysed / architecturally incompatible | **MET.** §3 applies all four labels, one per mechanism, with the discriminating test stated. |
| — | No unrelated defects · no reopening closed findings · no governance recommendation · no implementation planning beyond feasibility | **MET on all four.** §3.4 records two refinements to `R-7w`'s own mechanism and explains why they are refinements of the item under study rather than new defects. |

---

## 1. Executive determination

```
================================================================================
  DOES A RESIDUAL-FREE ARCHITECTURE EXIST?
================================================================================

  OVER THE TASK'S NAMED SET  { RES-1, RES-2, R-7w }          Y E S
      RES-1  CLOSED in 12 of 12 models by A3        [MEASURED PHASE2 §D.2]
      RES-2  CLOSED in 12 of 12 models by D1|D2     [MEASURED PHASE2 §D.2]
      R-7w   CLOSABLE by mechanism M1c              [DERIVED  §4.1]
      new blockers introduced ....................... 0
      => the task's stated objective is achievable.

  OVER THE CHAIN'S ACTUAL RESIDUAL SET  { RES-3, RES-4, R-7w }   N O
      R-7w   CLOSABLE      -- UNIMPLEMENTED             §3.1
      RES-3  CLOSABLE      -- UNIMPLEMENTED             §3.2
      RES-4  NOT CLOSABLE  -- IMPOSSIBLE on every       §3.3
                              platform in scope
      => minimum achievable residual count = 1.

  ── THE FINDING ────────────────────────────────────────────────────────────

  R-7w IS NOT PERMANENT.  EVERY PHASE FROM 3 TO 9 TREATED IT AS THE
  IRREDUCIBLE RESIDUAL, AND PHASE 9 BUILT ITS ENTIRE TERMINAL PROOF ON IT.

  The chain's stated ground for its permanence, PHASE3 §E.3:
      "Closing it requires moving serialization inside the authority, which
       PHASE1 §R-7 explicitly declined as 'a larger change than this phase
       covers.'"

  That states ONE mechanism and declines it.  It does not enumerate the
  mechanism space.  A second mechanism exists:

      M1c  ATOMIC STAGING.  The authority copies the pre-image to a temp
           path inside the held lock, invokes the UNCHANGED writer against
           the temp path, parses and compares the temp file as a DOCUMENT,
           and only then performs os.replace(tmp, path).
           Divergent bytes NEVER reach the ledger path.

      writers changed .................. 0
      serializers moved ................ 0        (CX-6 untouched)
      Phase-1 closures preserved ....... 12 of 12
      E1-F* / E2-F* / E-3 / E-4A reintroduced ... 0
      new blocker classes .............. 0
      _restore's own non-atomic write on the post-writer path .. ELIMINATED

  AND THE ARCHITECTURE ALREADY NAMES THE PRIMITIVE.
      [MEASURED] `os.replace` occurs EXACTLY ONCE in the entire write path:
      uga_engine.py:1099, inside LEDGER-INV-01's _PARAM_WRITE_SINKS -- the
      list of write sinks the invariant WATCHES FOR.  No writer uses it.
      PHASE0 EV-2 grepped for `os.replace|os.rename|fsync` and recorded
      "zero ledger matches".  The chain searched for this primitive,
      recorded its absence, and never proposed adding it.

  ── THE OBSTRUCTION, WHICH IS SOMEWHERE ELSE ENTIRELY ──────────────────────

  RES-4.  flock is ADVISORY: a process that never asks is not excluded.
  Closing it requires MANDATORY file locking.

      Linux ....... mandatory locking REMOVED in kernel 5.15
      Darwin ...... never provided it; this repository runs Darwin 27.0.0
      POSIX ....... does not specify it

  PHASE3 §F.1 stated this in its own words and nobody carried it forward:
      "RES-4 needs a guarantee NO FILESYSTEM PROVIDES."

  => RESIDUAL-FREE ARCHITECTURE: IMPOSSIBLE.  Verdict A.
     Minimum achievable residual count: 1.
     The binding constraint is RES-4, and it always was.
================================================================================
```

### 1.1 The eight questions, one line each

| Q | Answer |
|---|---|
| **Q1** | 5 items inventoried — 3 residuals + the 2 blockers the task misnames as residuals — with definitions, origins, open-reasons and a dependency graph. §2 |
| **Q2** | `R-7w` **assumed** permanent (not proven) · `RES-3` **assumed** permanent · `RES-4` **PROVEN** permanent · `RES-1`/`RES-2` **neither** — model-dependent and closed in all 12. §3 |
| **Q3** | **9** closure mechanisms discoverable from the chain: 4 for `R-7w`, 3 for `RES-3`, 2 for `RES-4`. §4 |
| **Q4** | 2 compatible with the current architecture · 3 require local redesign · 2 require authority redesign · 1 requires execution redesign · 1 architecturally incompatible. §5 |
| **Q5** | New blockers introduced: **0** by `M1c`, **0** by `N2`, **1 availability hazard (not a blocker)** by `N1`, **1 blocker** by `M2`. New unknowns **0**. New governance questions **0**. §6 |
| **Q6** | Zero-residual architecture **does not exist**. Minimum achievable = **1**. **4** architectures enumerated; minimum-change and minimum-risk coincide at `ARCH-2`. §7 |
| **Q7** | Phase 9's **conclusion survives**; its **proof fails at π4**. The load-bearing residual changes from `R-7w` to `RES-4`. §8 |
| **Q8** | **A — Residual-free architecture impossible.** §9 |

---

## 2. Residual inventory — Q1

### 2.1 The five items

| ID | Exact definition | Origin | Why it remained open | Class |
|---|---|---|---|---|
| **`RES-1`** | *"A permit binds a **six-field projection**, not the document. For a fixed pre-image and actor, the permit cannot distinguish members of an equivalence class with **five** free dimensions."* | `PHASE05:§F.4` (derived); carried `PHASE1:§6.2`, `PHASE2:§A.1` | **[MEASURED]** *"the remedy — widening `manifest_digest` — changes what a permit **binds** … Constraint 3 forbids introducing permit semantics."* Governance-dependent, and Phase 0.5 was forbidden to touch it | **BLOCKER**, not a residual |
| **`RES-2`** | *"`_verify_permit` does not refuse a permit over an all-empty manifest, while the sentinel's docstring (`:519`) states such a permit 'must not be issuable.' The empty-manifest digest is **one universal value** per `(actor, pre-image)`."* | `PHASE05:§F.4`; `PHASE2:§A.1` | **[MEASURED]** *"refusing a class of permit is a permit rule. **GOVERNANCE-DEPENDENT**."* | **BLOCKER**, not a residual |
| **`RES-3`** | *"The caller's own ledger read precedes `commit()`, therefore precedes `_ledger_lock`."* **[MEASURED]** `uga_engine.py:2097` calls `LA.commit(LEDGER_PATH, st["ledger"], …)` where `st` came from the whole `build()` discovery pass; `commit` takes the lock only on entry (`:237`, `:244`) | `PHASE05:§F.4`; `PHASE3:§E.1` | **[MEASURED]** *"Closing MW-3 entirely requires running `uga_engine.build`'s discovery pass under exclusion … an architecture and performance change **beyond any authorization in the input chain**."* | **RESIDUAL** |
| **`RES-4`** | *"`_ledger_lock` takes `fcntl.flock(fd, LOCK_EX\|LOCK_NB)` on the ledger's **containing directory**. Advisory: a process that never asks is not excluded. On a filesystem that does not honour `flock`, the control silently degrades."* | `PHASE05:§F.4`; `PHASE3:§E.2` | **[MEASURED]** `PHASE3:§F.1` — *"`RES-4` needs a guarantee **no filesystem provides**."* | **RESIDUAL** |
| **`R-7w`** | *"`R-7`'s detection is **post-hoc, by construction**."* **[MEASURED]** exact sequence inside `commit()` under the held lock: `writer(path, ledger)` **`:893`** → `raw_after = _read_bytes_or_none(path)` **`:895`** → `if persisted != ledger` **`:920`** → `_restore(path, raw_before)` **`:921`**. *"Divergent bytes therefore **reach disk** before the comparison runs, and a crash between `:893` and `:921` leaves them there."* | `PHASE1:§R-7`; `PHASE3:§E.3` | **[MEASURED]** *"Closing it requires moving serialization inside the authority, which `PHASE1:§R-7` explicitly declined as 'a larger change than this phase covers.'"* | **RESIDUAL** |

### 2.2 Deliverable 1 — the residual dependency graph

```
  ┌───────────────────────── GOVERNANCE LAYER ──────────────────────────────┐
  │   axis A ──► A3 ──────────────────────────────► RES-1  CLOSED, 12/12    │
  │   axis D ──► D1 | D2 ─────────────────────────► RES-2  CLOSED, 12/12    │
  │        [MEASURED PHASE2 §D.2, PHASE3 §A — no residual depends on these]  │
  └──────────────────────────────────────────────────────────────────────────┘
                    (RES-1 and RES-2 have NO edge into the residual set)

  ┌───────────────────────── THE THREE RESIDUALS ───────────────────────────┐
  │                                                                          │
  │   RES-4  advisory flock                                                  │
  │     │  (a) a non-asking process is not excluded ─── IRREDUCIBLE          │
  │     │  (b) fs may not honour flock ─────────────── verification task      │
  │     │                                                                     │
  │     ├──────────► RES-3   the lock RES-3 would need to span is the        │
  │     │                    same advisory lock.  Closing RES-3 by N1        │
  │     │                    INHERITS RES-4 and does not widen it.           │
  │     │                    [MEASURED PHASE3 §E.2: "B2 records consumption  │
  │     │                     under the existing lock and so INHERITS this   │
  │     │                     residual without widening it"]                 │
  │     │                                                                     │
  │     └──────────► R-7w    R-7w's window is "two file operations wide,     │
  │                          UNDER A HELD EXCLUSIVE LOCK" (PHASE3 §E.3).     │
  │                          Its containment depends on the same lock.       │
  │                                                                          │
  │   RES-3 ◄──no edge──► R-7w                                               │
  │        RES-3 is a window BEFORE the lock; R-7w is a window INSIDE it.    │
  │        Disjoint in time, disjoint in mechanism, independently closable.  │
  │        [DERIVED from PHASE3 §E.1 and §E.3]                               │
  └──────────────────────────────────────────────────────────────────────────┘

  ┌───────────────── SHARED STRUCTURAL DEPENDENCY: CX-6 ────────────────────┐
  │   Three serializers over one document are NOT byte-equivalent           │
  │   [MEASURED PHASE1 §R-11; PHASE7 §5.6: canonical 1 790 825 bytes vs     │
  │    the production writers' 2 279 169]                                    │
  │        │                                                                 │
  │        ├──► forbids A4 (bytes binding)         -> NB-4                   │
  │        ├──► forbids closing R-7w by BYTE comparison                      │
  │        └──► forbids mechanism M2 (serialization inside the authority)    │
  │             ...but does NOT forbid M1c, which never compares bytes and   │
  │                never moves a serializer.          [DERIVED, §4.1]        │
  └──────────────────────────────────────────────────────────────────────────┘

  IN-DEGREE 0 .......... RES-4          (nothing must close before it)
  DEPENDENT ............ RES-3, R-7w    (both inherit RES-4's lock)
  INDEPENDENT PAIR ..... RES-3 ⊥ R-7w   (no edge in either direction)
  EDGES FROM RES-1/RES-2 INTO THE RESIDUAL SET .......... 0
```

**[DERIVED]** The graph's shape is the answer to Q6 in miniature: `RES-3` and `R-7w` are independently closable leaves; `RES-4` is the root, and nothing closes it.

---

## 3. Permanence analysis — Q2

**Discriminating test applied to each item**, per constraint 7:

| Label | Test |
|---|---|
| **IMPOSSIBLE** | No mechanism exists on any platform the repository targets or the chain contemplates |
| **UNIMPLEMENTED** | A mechanism exists and has not been built |
| **UNANALYSED** | The mechanism space was not enumerated |
| **ARCHITECTURALLY INCOMPATIBLE** | A mechanism exists and cannot coexist with a property the architecture guarantees |

### 3.1 `R-7w` — **assumed permanent. Actually UNIMPLEMENTED.** Proof.

**The chain's ground for permanence, quoted in full.** **[MEASURED]** `PHASE3:§E.3`:

> *"Closing it requires moving serialization inside the authority, which `PHASE1:§R-7` explicitly declined as 'a larger change than this phase covers.'"*

**[DERIVED] That sentence contains two claims and only the second is established.** *"`PHASE1` declined it"* is a fact about Phase 1. *"Closing it **requires** moving serialization inside the authority"* is a universal claim over the mechanism space, and **the chain never enumerates that space.** `PHASE3:§E.3` names one mechanism, `PHASE1:§R-7` declines that one mechanism, and every later phase inherits the universal.

**The falsifying mechanism.** **[DERIVED]** `M1c` — atomic staging — closes `R-7w` without moving serialization anywhere:

```
  under the held lock, replacing lines :893-:930:

      copy raw_before -> tmp                       (authority; preserves the
                                                    writer's own skip logic)
      writer(tmp, ledger)                          (UNCHANGED writer, UNCHANGED
                                                    serializer, new path arg)
      raw_after = read(tmp)
      persisted = json.loads(raw_after)
      if persisted != ledger:   remove(tmp); REFUSE      <- ledger NEVER touched
      _refuse_unmoved_allocation(report)                 <- unchanged
      os.replace(tmp, path)                              <- ATOMIC
```

**[MEASURED] Five facts that make `M1c` work, each verified this phase:**

| # | Fact | Probe |
|---|---|---|
| **1** | **Every writer already takes `path` as its first parameter** — `ukb._dump_json(path, obj)`, `ukb._write(path, lines)`, `ukbx._dump(path, obj)`, `ukbx._dump_text(path, text)`, `uga._dump(path, obj)`, `uga._write_text(path, text)`. Passing a temp path costs **zero writer changes** | **P-A4** |
| **2** | **`_ledger_lock` locks the containing DIRECTORY, not the file** — `directory = os.path.dirname(...)` `:237`, `fd = os.open(directory, os.O_RDONLY)` `:244`. Replacing the file inside that directory **does not disturb the lock** | **P-A6** |
| **3** | **The ledger carries no generation stamp** — top-level keys are `version, by_path, page_cursor, category_seq, discovered_volumes, volume_seq, history, by_object, by_observation`; **`generated_at` absent**. So `_stamp_eq_json`'s neutralization is the identity on this document and the writer's skip reduces to plain content equality — which the pre-image copy preserves exactly | **P-A7** |
| **4** | **`os.replace` appears exactly ONCE in the whole write path**, at `uga_engine.py:1099` in `LEDGER-INV-01`'s `_PARAM_WRITE_SINKS` — the list of sinks the invariant **watches for**. **No writer uses it.** The architecture already has the vocabulary and none of the practice | **P-A2** |
| **5** | **`PHASE0` EV-2 searched for exactly this primitive** — *"`grep` for … `os.replace\|os.rename\|fsync` … — **zero ledger matches**"* — recorded its absence, and no phase proposed adding it | `PHASE0:§3` EV-2 |

**[DERIVED] Why `CX-6` does not block `M1c`.** `CX-6` forbids **byte** comparison because the three serializers disagree byte-for-byte. `M1c` performs the **same document comparison at `:920`** that exists today; it changes only *where the candidate bytes live while that comparison runs*. No serializer moves; no byte comparison is introduced. **`CX-6` is untouched, and `A4` remains CONTRADICTED for the reasons `PHASE2:§C.6` gives.**

**[DERIVED] `R-7w` is UNIMPLEMENTED.** A mechanism exists, it is compatible with every property the architecture guarantees (§5), and it has not been built. ∎

### 3.2 `RES-3` — **assumed permanent. Actually UNIMPLEMENTED.** Proof.

**[MEASURED]** `PHASE3:§E.1`: *"Closing MW-3 entirely requires running `uga_engine.build`'s discovery pass under exclusion — governance-independent, and an architecture and performance change **beyond any authorization in the input chain**."*

**[DERIVED]** *"Beyond any authorization"* is a statement about **permission**, not about **possibility**. `PHASE3` labels the mechanism **governance-independent** in the same sentence, which is the chain's own term for *closable without any governance answer*. The mechanism `N1` — take the lock before the discovery pass and release it after `commit()` — is implementable and requires no new primitive.

**[MEASURED]** The cost is bounded and known: `LEDGER_LOCK_TIMEOUT_SECONDS = 60.0` (`:212`). A second writer waits up to 60 s and is then **REFUSED** — `LedgerWriteRefused`, the fail-closed direction (`:249-254`). So `N1` degrades **availability**, not correctness.

**[DERIVED] `RES-3` is UNIMPLEMENTED**, at a measurable availability cost. §6 classifies that cost.

### 3.3 `RES-4` — **PROVEN permanent.** Proof.

**[MEASURED]** `PHASE3:§E.2` defines it in two limbs:

- **(a)** *"Advisory: a process that never asks is not excluded."*
- **(b)** *"On a filesystem that does not honour `flock`, the control silently degrades."*

**Limb (b) is not permanent.** **[MEASURED]** `PHASE3:§E.2` classes it as a **verification task**: *"Confirm `flock` is honoured on every filesystem the ledger will live on. Determinate, environmental, outside the repository."* A verification task is dischargeable.

**Limb (a) is permanent.** **[DERIVED]** Excluding a process that does not request the lock requires **mandatory** locking. The facts:

| Platform | Mandatory file locking |
|---|---|
| **POSIX** | Not specified |
| **Linux** | Provided via `mount -o mand`; deprecated, then **removed in kernel 5.15** |
| **Darwin** | **Never provided.** **[MEASURED]** this repository runs Darwin 27.0.0 (`PHASE7:§2.4` environment) |

**[DERIVED] The dissolution route also fails.** One might hope to remove the *need* for exclusion rather than strengthen it — if every ledger update were a single atomic act, concurrent writers could not interleave destructively. Under `M1c` the final act **is** a single atomic `os.replace`. But two concurrent commits both read pre-image `P0`, both build a temp, and both rename: the second rename wins and the first's allocation is **silently lost**. Detecting that requires an atomic **compare-and-swap on file content**, which POSIX does not provide (`renameat2(RENAME_EXCHANGE)` is Linux-only and exchanges names, not contents). **[MEASURED]** `PHASE3:§E.2` already identifies the surviving detector — *"`R-2`'s pre-write byte re-check … is the remaining detector"* — and correctly calls the result *"a degradation of defence depth from two layers to one, not a hole."* A depth degradation is precisely a residual.

**[DERIVED] `RES-4` limb (a) is IMPOSSIBLE** — no mechanism exists on any platform in scope. **[INFERRED]** It is not *logically* impossible: a hypothetical platform with mandatory locking would close it. No such platform is in the repository's target set, and `PHASE3:§F.1` states the chain's own finding in its own words — *"`RES-4` needs a guarantee **no filesystem provides**."* ∎

### 3.4 Two refinements to `R-7w`'s own mechanism

**[INFERRED]** Recorded because they are properties of the item under study, not unrelated defects, and because they strengthen rather than complicate the case.

| # | Refinement | Basis |
|---|---|---|
| **1** | **The window admits truncation, not only divergence.** **[MEASURED]** every writer opens with `open(path, "w")` — truncate-then-write (`ukb.py:143`, `uga_engine.py:156`). A crash **during** the writer leaves a **truncated** ledger, which `PHASE3:§E.3`'s characterisation ("divergent bytes") does not name. Under `M1c` the truncation lands in the temp file and the ledger is untouched |
| **2** | **`_restore` has the same window.** **[MEASURED]** `_restore` (`:807-822`) writes with `open(path, "wb")` — also non-atomic. A crash during the restore leaves a **partially restored** ledger. Under `M1c` the post-writer `_restore` calls at `:906`, `:915`, `:921`, `:930` become **unreachable**, because nothing was written to `path` |

**[DERIVED]** Both refinements point the same way: `M1c` closes strictly more than `R-7w` as defined.

### 3.5 Q2 verdict

```
                        proven      assumed     model-        implementation-
                        permanent   permanent   dependent     dependent
  RES-1  ..............    no          no        YES (A3)         yes
  RES-2  ..............    no          no        YES (D)          yes
  RES-3  ..............    no          YES        no              YES
  RES-4  ..............   YES          --         no              no
  R-7w   ..............    no          YES        no              YES

  PROVEN PERMANENT ....................................  1   RES-4
  ASSUMED PERMANENT, ACTUALLY UNIMPLEMENTED ...........  2   RES-3, R-7w
  MODEL-DEPENDENT AND ALREADY CLOSED IN ALL 12 ........  2   RES-1, RES-2
```

---

## 4. Deliverable 2 — closure-mechanism catalog — Q3

Nine mechanisms, each discoverable from a fact the chain already records.

### 4.1 Mechanisms for `R-7w`

| ID | Mechanism | Artifact changes | Semantic changes | Implementation changes | Affected invariants | Affected permits | Governance assumptions |
|---|---|---|---|---|---|---|---|
| **M1c** | **Atomic staging.** Authority copies pre-image → tmp inside the lock, invokes the unchanged writer against tmp, parses and compares as a document, then `os.replace(tmp, path)` | **0 artifacts.** One transient untracked temp under `00-BOOK/DATA/` | **0.** The refusal predicate remains a function of `(before, ledger, persisted_bytes)` | `ledger_authority.commit()` `:886-931` only. **0 writers** | **`LEDGER-INV-01`** — `os.replace` is already in `_PARAM_WRITE_SINKS` (`uga_engine.py:1099`), so the new call site is **detected by design**, not a blind spot | **none.** `_verify_permit` untouched; every binding preserved | **none** |
| **M2** | **Serialization inside the authority** — the mechanism `PHASE1:§R-7` declined | Every register's bytes change | The authority acquires a canonical on-disk format | All four writers lose their serializers | `UKB-ADV-INV-07` deterministic reproducibility; the `--guard` drift gate | none | **none, but see §5** |
| **M4** | **Writer returns bytes** — `writer(ledger) -> bytes`; the authority compares and writes | 0 | writer contract changes | All four writers, plus relocation of their stamp-skip logic | `LEDGER-INV-01`'s parameter-indirection measurement (`R-10`) | none | none |
| **M3** | **Write-ahead journal** — record intent, write, verify, clear | +1 journal artifact | recovery semantics added | authority + a recovery path | `CY-1` — a new tracked artifact re-enters the identity regress | none | none |

### 4.2 Mechanisms for `RES-3`

| ID | Mechanism | Artifact changes | Semantic changes | Implementation changes | Affected invariants | Affected permits | Governance assumptions |
|---|---|---|---|---|---|---|---|
| **N1** | **Discovery under exclusion** — take `_ledger_lock` before `build()`, release after `commit()` | 0 | 0 | `uga_engine.cmd_run` and `ukb.cmd_build` restructured to hold the lock across the pass | none | none | none |
| **N2** | **Prove the two-refusal coverage total** — establish that every reachable divergence between the caller's read and the lock is refused | 0 | 0 | **0 code.** A proof plus tests | none | none | none |
| **N3** | **Re-derive inside the lock** — the authority recomputes what the caller computed | 0 | the authority learns discovery | authority + engines | violates *"`commit()` ENFORCES an authorization it does not DECIDE"* (`:490-497`) | none | none |

### 4.3 Mechanisms for `RES-4`

| ID | Mechanism | Verdict |
|---|---|---|
| **O1** | **Mandatory locking** | **[DERIVED] NON-EXISTENT** on every platform in scope — §3.3 |
| **O2** | **Atomic compare-and-swap on file content**, removing the need for exclusion | **[DERIVED] NON-EXISTENT** in POSIX — §3.3 |

### 4.4 `N2` — the mechanism that closes `RES-3`'s harm at zero code cost

**[MEASURED]** `PHASE3:§E.1`: *"After `R-6`, MW-3 is covered by **two independent refusals** — key removal (`assert_append_only`) and cross-map identifier uniqueness … The window persists; the exploit does not."*

**[DERIVED]** The divergence space is enumerable, and every member is already refused:

| Interleaving between the caller's read `P0` and the lock | Refused by |
|---|---|
| the interleaved commit **added a key** the caller's `ledger` lacks | `assert_append_only` — key removal |
| it added a key the caller also has, with a different identifier | `R-6` cross-map identifier uniqueness |
| it appended only to `history` | `assert_append_only`'s history-prefix check (`R-5b`) |
| it advanced only a counter | `MONOTONIC_COUNTERS` regression check (`:350-353`) |

**[DERIVED]** The four cases exhaust the top-level mutation classes the ledger admits — `IDENTITY_MAPS` (4), `MONOTONIC_COUNTERS` (2), `NON_ALLOCATION_KEYS` (`version`, `category_seq`, `discovered_volumes`, `history`) — and each is refused. **[INFERRED]** So `N2` closes `RES-3` **as a harm** while leaving it open **as a structure**, and `PHASE3:§E.0`'s definition of a residual — *"a bounded, known, accepted **property**"* — is about the structure. **`N2` therefore does not reduce the residual count under the chain's own definition.** It is catalogued because it is a real mechanism and because the structure-versus-harm distinction is exactly the `U-M` species Phase 9 settled.

---

## 5. Compatibility analysis — Q4

| Mechanism | Compatible as-is | Local redesign | Authority redesign | Permit redesign | Execution redesign | Verdict |
|---|---|---|---|---|---|---|
| **M1c** | **YES** | authority write block only | no | **no** | no | **COMPATIBLE** |
| **M2** | no | no | **YES — total** | no | no | **ARCHITECTURALLY INCOMPATIBLE** — §5.1 |
| **M4** | no | **YES — 4 writers** | partial | no | no | requires local redesign |
| **M3** | no | yes | yes | no | no | requires local redesign + a new tracked artifact |
| **N1** | no | **YES — 2 callers** | no | no | **YES** — lock held across the run | requires execution redesign |
| **N2** | **YES** | no | no | no | no | **COMPATIBLE** — proof only |
| **N3** | no | no | **YES** | no | no | **ARCHITECTURALLY INCOMPATIBLE** — §5.2 |
| **O1**, **O2** | — | — | — | — | — | **NON-EXISTENT** |

### 5.1 Why `M2` is architecturally incompatible — and why Phase 1 was right to decline it

**[MEASURED]** `PHASE4:§D.0`: *"All four writers are stamp-neutralized and skip no-op rewrites: `ukb._dump_json` (`:135-146`, guarded by `_stamp_eq_json`), `ukb._write` (`:1658-1664`), `ukbx._dump` (`:66-76`), `ukbx._dump_text` (`:692-698`). Each returns without writing when only the generation stamp would change. **Therefore a second identical run produces zero byte changes in tracked registers, which is the property `V-12` tests.**"*

**[DERIVED]** `M2` moves serialization into the authority and therefore destroys the writers' skip logic for the ledger — and `PHASE1:§R-11` measured that `LA._canonical` and the production writers produce **different bytes** for the same document. So `M2` rewrites the ledger's on-disk form, which **breaks byte-stability**, which is `UK-1` item 5 / `EV-23`. **[INFERRED] `PHASE1:§R-7`'s decline of `M2` was correct on grounds stronger than the "larger change" it gave.** What the chain then did wrong was to generalise a correct rejection of `M2` into a universal about the mechanism space.

### 5.2 Why `N3` is architecturally incompatible

**[MEASURED]** `ledger_authority.py:490-497`: *"`commit()` ENFORCES an authorization it does not DECIDE … Moving the issuing decision here would create the second governance authority this module exists to avoid."* **[DERIVED]** `N3` requires the authority to know how objects are discovered, which is the same boundary violation one layer down.

---

## 6. Deliverable 3 — new-blocker matrix — Q5

| Mechanism | New blocker classes | New unknowns | New governance questions | New environmental dependencies | Net effect |
|---|---:|---:|---:|---:|---|
| **M1c** | **0** | **0** | **0** | **1** — `os.replace` atomicity, same class as `RES-4(b)` | **closes `R-7w`; eliminates 2 further crash windows (§3.4)** |
| **N1** | **0** | **0** | **0** | 0 | closes `RES-3`; **1 availability hazard** — §6.2 |
| **N2** | **0** | **0** | **0** | 0 | closes `RES-3`'s harm, not its structure |
| **M4** | **0** | **0** | **0** | 1 | closes `R-7w`; 4 writers changed |
| **M3** | **1** | **0** | **0** | 0 | **CY-1 re-entry** — a new tracked artifact re-opens the identity regress (`:499-506`) |
| **M2** | **1** | **0** | **0** | 0 | **breaks byte-stability ⇒ `UK-1` item 5 unclosable** — §5.1 |
| **N3** | **1** | **0** | **0** | 0 | **second governance authority inside the module** (`:490-497`) |

```
CANDIDATE CLOSURES EVALUATED ......................................  7
    introducing ZERO new blockers ..................................  4   M1c, N1, N2, M4
    introducing ONE new blocker ....................................  3   M2, M3, N3
    introducing a new UNKNOWN ......................................  0
    introducing a new GOVERNANCE QUESTION ..........................  0
    introducing a new ENVIRONMENTAL DEPENDENCY .....................  2   M1c, M4
```

### 6.1 `M1c` — the five preservation checks, individually

**[DERIVED]** Each of the properties the primary question requires preserved:

| Property required preserved | Preserved under `M1c`? | Why |
|---|---|---|
| **Append-only guarantees** | **YES** | `assert_append_only(before, ledger)` runs at `:872`, before the writer, untouched |
| **Authorization guarantees** | **YES** | `_verify_permit` runs at `:877`, before the writer, untouched. All 9 bindings preserved |
| **Permit validation guarantees** | **YES** | The permit path `:709-804` is not touched at all |
| **The 12 Phase-1 closures** | **YES — all 12.** `R-1` single read: unaffected. `R-2` pre-write re-check: retained, now immediately before the rename. `R-3` lock: unaffected — the lock is on the **directory** (`:237`). `R-4`, `R-5`, `R-6`: pre-writer, unaffected. **`R-7` document comparison: retained verbatim; only the candidate's location moves.** `R-8` `bytes_changed`: computed from the temp content, semantically identical. `R-9` `NO_ALLOCATION`: unaffected. `R-10`, `R-11`: unaffected | **[DERIVED]** each traced to its site |
| **Zero reintroduction of `E1-F*`, `E2-F*`, `E-3`, `E-4A`** | **YES.** `E2-F1` (divergent writer) and `E2-F2` (silent writer) are **more strongly** closed: the divergent document is refused **before** it can reach `path`, rather than after | **[DERIVED]** |
| **Zero new blocker class** | **YES.** The only new on-disk object is a transient untracked temp. **[MEASURED]** `PHASE7` **P7-8**: the UGA object boundary is `git ls-files --cached`, so an untracked file is **not** a UGA object. **No `CY-1` re-entry** | **[DERIVED]** |

**[DERIVED] The one residual failure mode `M1c` introduces, and its comparison.** A crash between the writer and the rename leaves a stray temp file under `00-BOOK/DATA/` — an untracked `??` entry, which `register.sh --observe` reports as **DRIFT (`RC=3`)**. That is an **existing, recognised, detected class**, and it replaces a state in which the **ledger itself** holds unauthorized or truncated bytes. **[INFERRED]** The failure mode strictly improves.

### 6.2 `N1`'s availability hazard, stated precisely

**[MEASURED]** `LEDGER_LOCK_TIMEOUT_SECONDS = 60.0` (`:212`), and `PHASE05:§F.4` characterises `uga_engine.build`'s discovery as a *"60-second discovery pass"*.

**[DERIVED]** Under `N1` the lock is held for approximately the pass duration, which is approximately the timeout. A concurrent `commit()` therefore waits and is **refused** — `LedgerWriteRefused`, fail-closed (`:249-254`). **[INFERRED]** This is an availability property, not a correctness one, and it is **not a blocker** under `PHASE3:§E.0`'s definition (*"Prevents a required operation from completing"*) because the refused operation is a **concurrent second** run, and `PHASE5:§E.4` proves the program requires the two runs to be **serialized** in any case.

---

## 7. Full-elimination search — Q6

### 7.1 Deliverable 4 — residual-elimination feasibility matrix

| Item | Closable? | By | Classification | New blockers | Residual after |
|---|---|---|---|---|---|
| **`RES-1`** | **YES** | axis `A = A3` — governance, already forced in all 12 | model-dependent, **already CLOSED 12/12** | 0 | — |
| **`RES-2`** | **YES** | axis `D ∈ {D1, D2}` — already forced in all 12 | model-dependent, **already CLOSED 12/12** | 0 | — |
| **`R-7w`** | **YES** | **`M1c`** (also `M4`) | **UNIMPLEMENTED** | **0** | closed |
| **`RES-3`** | **YES** | **`N1`** (structure); `N2` (harm only) | **UNIMPLEMENTED** | **0** | closed |
| **`RES-4`** | **NO** | — | **IMPOSSIBLE** on every platform in scope | — | **PERMANENT** |

### 7.2 Deliverable 5 — zero-residual architecture inventory

```
ARCHITECTURES SATISFYING  Residuals = 0 ∧ Blockers = 0 ∧ Unknowns = 0 ......  0

    OBSTRUCTION: exactly one item, RES-4, limb (a).
    No mechanism closes it (§3.3, §4.3).  Therefore no architecture in the
    search space reaches Residuals = 0, and the search terminates here.
```

**[DERIVED] Two further obstructions, recorded for completeness and not load-bearing.** Even were `RES-4` closable, `Unknowns = 0` requires `UK-1` and `UK-2` discharged, and **[MEASURED]** `PHASE3:§G.1` — *"dischargeable without an irreversible mutating run … **0**"* — so `Unknowns = 0` is unreachable by any determination; and `Blockers = 0` requires `GA-1 … GA-9` plus `IA-1 … IA-12`, of which **[MEASURED]** `GA-7` is *"the one artifact no phase of this chain can produce for itself"* (`PHASE5:§K.4`). **The conjunction fails three times over; `RES-4` is merely the first.**

### 7.3 The minimum-residual architecture inventory

**[DERIVED]** Since `Residuals = 0` is unreachable, the search reduces to the minimum achievable count. Four architectures span the space:

| ID | Composition | Residuals | Change surface | New env. dependencies | Availability hazard |
|---|---|---:|---|---:|---|
| **ARCH-0** | baseline | **3** | — | 0 | none |
| **ARCH-2** | baseline + `M1c` | **2** | **1 function** — `commit()` `:886-931` | 1 | none |
| **ARCH-3** | baseline + `N1` | **2** | **2 callers** restructured | 0 | **yes** |
| **ARCH-1** | baseline + `M1c` + `N1` | **1** | 1 function + 2 callers | 1 | **yes** |

```
MINIMUM ACHIEVABLE RESIDUAL COUNT ................................. 1   ARCH-1
ARCHITECTURES ACHIEVING IT ........................................ 1   ARCH-1
ARCHITECTURES STRICTLY REDUCING THE COUNT ......................... 3   ARCH-1, ARCH-2, ARCH-3
```

### 7.4 Deliverables 6 and 7 — minimum-change and minimum-risk

**Deliverable 6 — minimum-change architecture achieving a strict residual reduction: `ARCH-2`.**
**[DERIVED]** One function body, zero writers, zero artifacts, zero semantic changes. Every other reducing architecture requires at least that plus a caller restructure.

**Deliverable 7 — minimum-risk architecture achieving a strict residual reduction: `ARCH-2`.**
**[DERIVED]** It is the only candidate whose net risk is **negative**: it introduces one environmental dependency of a class the system already carries (`RES-4(b)`) and removes three failure modes — `R-7w`'s divergence window, the truncation window (§3.4 refinement 1), and `_restore`'s own non-atomic write (refinement 2). `ARCH-3` and `ARCH-1` both take on `N1`'s availability hazard.

**[INFERRED]** Minimum-change and minimum-risk **coincide** at `ARCH-2`, and the minimum-residual architecture `ARCH-1` is neither. That divergence is the honest shape of the trade-off and is stated rather than resolved: **this phase determines feasibility and does not select an architecture.** Choosing among `ARCH-0 … ARCH-3` is an authorization act of exactly the kind `PHASE1:§R-7` and `PHASE3:§E.1` recorded as outstanding, and it remains outstanding.

---

## 8. Readiness reclassification — Q7

### 8.1 Does Phase 9's conclusion remain valid? **YES. Does its proof? NO.**

**[MEASURED]** `PHASE9:§7` states the deduction over five premises. The relevant two:

| # | Premise, as Phase 9 stated it | Status after this phase |
|---|---|---|
| **π3** | *"Execution leaves `R-7w` **UNCHANGED**, because it is a failure-path property; 4 of `commit()`'s 8 refusal points enter the window and a successful run enters none"* | **STANDS.** A statement about execution, unaffected |
| **π4** | *"**Closing `R-7w` requires moving serialization inside the authority**, declined as 'a larger change than this phase covers'"* | **FAILS.** `M1c` closes `R-7w` without moving serialization anywhere — §3.1 |

**[DERIVED] π4 is the premise that fails, and it is the only one.** Phase 9's `N9` — *"no authorized act closes `R-7w`"* — was true of **authorization** and false of **possibility**, and Phase 9's own §7.1 hedge (*"`R-7w` is permanent within this architecture and this authorization scope"*) was closer to correct than its proof-tree premise.

### 8.2 The conclusion survives on a different residual

**[DERIVED]** Phase 9's Lemma 3 requires only that **some** residual be unclosable in every model and on every path. Substituting `RES-4` for `R-7w`:

| Lemma 2 premise | Instantiated at `RES-4` | Source |
|---|---|---|
| **(P1)** invariant across all 12 models | **[MEASURED]** `PHASE3:§E.7` — `RES-4` row, *"no — all 12 identical"* | `PHASE3:§E.7` |
| **(P2)** not closed by execution | **[MEASURED]** `PHASE4:§G` — `RES-4` **REDUCED**, never closed; and **[MEASURED]** `PHASE7:§6.3` — the reduction's evidence `EV-25` **has no producer**, so even the reduction is unobtainable | `PHASE4:§G`; `PHASE7:§6.3` |
| **(P3)** not closable by any available act | **[DERIVED]** §3.3 — mandatory locking exists on no platform in scope | this phase |

**[DERIVED] Therefore `|R| ≥ 1` in every model and on every path, and `PHASE9`'s Outcome B — UNCONDITIONAL READY DOES NOT EXIST — stands.** ∎

### 8.3 What changes, and why it matters

**[INFERRED]** The conclusion is unchanged and its **content** is not. Before this phase, the chain believed its irreducible residual was a **two-file-operation window inside a held lock on a failure path that a successful run never enters** (`PHASE4:§G.3`) — an item of almost no operational consequence. After this phase, the irreducible residual is that **the ledger's mutual exclusion is advisory**, which is an item of real operational consequence and which no amount of implementation can remove.

**[DERIVED]** And the reachable ceiling improves. `PHASE4:§0.2`'s `EXECUTED` column reads `0 blockers · 3 residuals · 0 unknowns`. Under `ARCH-1` it reads **`0 blockers · 1 residual · 0 unknowns`** — a strictly better honest claim than any phase has recorded, reached with **zero** new blockers, **zero** new unknowns and **zero** governance questions.

---

## 9. Terminal verdict — Q8

# **A. Residual-free architecture impossible.**

### 9.1 Deliverable 8 — the formal proof

**Theorem.** No architecture satisfies `Residuals = 0` while preserving the properties the primary question names.

**Definitions.** `R = {RES-3, RES-4, R-7w}`, the chain's residual set (**[MEASURED]** `PHASE3:§E.7`). *Closable* means: a mechanism exists on a platform the repository targets, which preserves append-only, authorization and permit-validation guarantees, preserves all 12 Phase-1 closures, reintroduces no `E1-F*`/`E2-F*`/`E-3`/`E-4A` defect, and creates no new blocker class.

**Lemma A — `R-7w` is closable.** `M1c` (§3.1) closes it. §6.1 verifies all six preservation conditions individually. **[DERIVED]** ∎

**Lemma B — `RES-3` is closable.** `N1` (§4.2) closes it, at an availability cost §6.2 shows is not a blocker under `PHASE3:§E.0`'s definition. **[DERIVED]** ∎

**Lemma C — `RES-4` is not closable.** Limb (a) requires excluding a process that does not request the lock. That requires mandatory locking, which is unspecified in POSIX, removed from Linux at 5.15, and absent from Darwin, on which this repository runs. The dissolution route — removing the need for exclusion — requires atomic compare-and-swap on file content, which POSIX does not provide. **[MEASURED]** `PHASE3:§F.1` states the same finding: *"`RES-4` needs a guarantee no filesystem provides."* **[DERIVED]** ∎

**Theorem, proved.** By Lemma C, `RES-4 ∈ R` in every architecture in the search space. Hence `|R| ≥ 1` and `Residuals = 0` is unsatisfiable. **A residual-free architecture is impossible.** ∎

**Corollary 1.** The minimum achievable residual count is **1**, attained by `ARCH-1` and by no other architecture (Lemmas A and B supply the two closures; Lemma C supplies the floor). **[DERIVED]**

**Corollary 2.** The obstruction is **not** the item the chain identified. `R-7w`, on which `PHASE9` built its terminal proof, is closable; `RES-4`, which no phase named as binding, is not. **[DERIVED]**

**Corollary 3.** `PHASE9`'s Outcome B stands, on `RES-4` rather than on `R-7w`; its premise **π4** is false. **[DERIVED]** §8.

### 9.2 Why the verdict is A and not B, C or D

**[DERIVED]**

| Option | Rejected because |
|---|---|
| **B** — possible but introduces new blockers | Would require a residual-free architecture to exist. Lemma C forbids it. And the closures that *do* exist introduce **0** new blockers (§6), so B mischaracterises them in both directions |
| **C** — possible with no new blockers | **True of the task's named set `{RES-1, RES-2, R-7w}`** and false of the chain's residual set. §0.1 states why the sets differ; Q6's *"Residuals = 0"* is meaningful only over the chain's set |
| **D** — insufficient evidence | Every step of Lemmas A, B and C rests on a `[MEASURED]` fact from an input document or a probe recorded in §3. Nothing is left open |

---

## 10. Stop condition

The stop condition is met: the existence of a `0 blockers · 0 unknowns · 0 residuals` architecture has been **disproved**, at Lemma C.

### 10.1 Determinations

- **Q1** — 5 items inventoried; 2 are blockers the task misnames as residuals and both are **CLOSED in 12 of 12 models**; dependency graph in §2.2 with `RES-4` as the unique in-degree-0 root.
- **Q2** — **1** proven permanent (`RES-4`) · **2** assumed permanent but actually **UNIMPLEMENTED** (`RES-3`, `R-7w`) · **2** model-dependent and already closed.
- **Q3** — **9** closure mechanisms catalogued: 4 for `R-7w`, 3 for `RES-3`, 2 for `RES-4` (both non-existent).
- **Q4** — 2 compatible as-is · 3 requiring local redesign · 2 architecturally incompatible · 2 non-existent.
- **Q5** — new blockers **0** for `M1c`, `N1`, `N2`, `M4`; **1** each for `M2`, `M3`, `N3`. New unknowns **0**. New governance questions **0**.
- **Q6** — zero-residual architecture **does not exist**; minimum achievable **1**; **4** architectures enumerated; minimum-change = minimum-risk = **`ARCH-2`**; minimum-residual = **`ARCH-1`**.
- **Q7** — `PHASE9`'s conclusion **survives**; premise **π4 fails**; the load-bearing residual moves from `R-7w` to `RES-4`.
- **Q8** — **A. Residual-free architecture impossible.**

### 10.2 Corrections to the chain

| # | Claim | Correction |
|---|---|---|
| **1** | `PHASE3:§E.3` (inherited by Phases 4–9) — *"Closing [`R-7w`] **requires** moving serialization inside the authority"* | **A universal over a mechanism space the chain never enumerated.** `M1c` closes it without moving any serializer. `PHASE1:§R-7`'s rejection of `M2` was correct — and on **stronger** grounds than it gave (§5.1) — and was generalised into a universal it does not support |
| **2** | `PHASE9:§7` premise **π4** and `§9` node **N9** | **π4 is false.** Outcome B survives on `RES-4`; §8.2 supplies the substituted lemma |
| **3** | `PHASE3:§E.3`'s characterisation of the window as *"divergent bytes"* | **[MEASURED]** every writer opens with `"w"` — the window also admits **truncation**; and `_restore` (`:807-822`) has the **same** window. Both are refinements of `R-7w`, both closed by `M1c` (§3.4) |
| **4** | The task's own premise — *"the three residuals … `RES-1`, `RES-2`, `R-7w`"* | **[MEASURED]** `RES-1` and `RES-2` are **blockers** (`PHASE1:§6.2`) and are **CLOSED in 12 of 12 models** (`PHASE2:§D.2`). The residual set is `{RES-3, RES-4, R-7w}` (`PHASE3:§E.7`) |

**[INFERRED]** Correction 1 has the same shape as the error Phase 9 corrected in Phases 7–8: a phase recorded *"X was declined"*, a later phase read it as *"X is impossible"*, and no phase re-tested it. The chain audits forward reliably and re-reads its own conclusions poorly.

### 10.3 Constraint compliance and non-mutation

- **Read-only. No repository modification. No mutating command. No governance selection. Every statement classified.** Confirmed. No engine was invoked in any mode; the eight probes were `grep`, `sed`, `awk`, `wc` and one in-process JSON read.
- **No implementation recommendations beyond feasibility.** §7.4 states explicitly that this phase determines feasibility and selects no architecture.
- **No unrelated defects, no reopened findings, no governance proposals.** §3.4's two items are refinements of `R-7w`'s own mechanism, labelled as such.

```
$ shasum -a 256 00-BOOK/DATA/id-ledger.json
8471e709b178a9a09909bca55f2e8eccb78161db8423026d1d26e4f35c41c20b        (unchanged)
$ git rev-parse --short HEAD                   -> 77798202              (unchanged)
$ git status --porcelain -- 00-BOOK/DATA 00-BOOK/REGISTRIES \
                            00-BOOK/CONTROL-TOWER 00-BOOK/PORTAL        (0 lines)
$ git ls-files --cached | wc -l                -> 6804                  (unchanged)
$ ls 00-BOOK/DATA/allocation-permits.json      -> No such file or directory
```

### 10.4 The terminal position

```
RESIDUAL-FREE ARCHITECTURE ....... IMPOSSIBLE          verdict A
MINIMUM ACHIEVABLE RESIDUALS ..... 1                   ARCH-1
THE SOLE OBSTRUCTION ............. RES-4, limb (a) — advisory flock

CLOSABLE, AND NOT PREVIOUSLY KNOWN TO BE
    R-7w   by M1c   0 writers · 0 new blockers · 0 new unknowns ·
                    0 new governance questions · 12 of 12 Phase-1
                    closures preserved · 2 further crash windows removed
    RES-3  by N1    0 new blockers; 1 availability hazard

IMPROVED CEILING, if ARCH-1 were authorized
    from   0 blockers · 3 residuals · 0 unknowns     PHASE4 §0.2
    to     0 blockers · 1 residual  · 0 unknowns

PHASE9's OUTCOME B ............... STANDS, on RES-4
PHASE9's PREMISE π4 .............. FALSE

WHAT THIS PHASE DOES NOT DECIDE
    which of ARCH-0 … ARCH-3 to adopt.  That is an authorization act of
    exactly the kind PHASE1 §R-7 and PHASE3 §E.1 recorded as outstanding,
    and it remains outstanding.
```

Phase A ends here.
