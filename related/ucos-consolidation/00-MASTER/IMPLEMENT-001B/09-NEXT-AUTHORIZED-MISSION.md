# IMPLEMENT-001B · DELIVERABLE 09 — NEXT AUTHORIZED MISSION

| Field | Value |
|---|---|
| MISSION | `IMPLEMENT-001B` |
| AUTHORITY | `NONE — DERIVED TRUTH` — records a determination; authorizes nothing |
| SUPERSEDES | `IMPLEMENT-001A` Deliverable 05 |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT |

---

## 1. DETERMINATION

> ### NEXT AUTHORIZED MISSION: **`IMPLEMENT-001C` — Authorization Record & Atomic Commit**
>
> Scope: **one work-package record, one commit sequence, one 2-line guard correction.**
> No new capability. No new identifier family. No constitutional amendment. No file reverted.

`IMPLEMENT-001A` determined that no epic could begin and named `IMPLEMENT-001B` as a six-deliverable
closure mission requiring four dispositions. Three of those four dispositions turned out to be
unnecessary:

| `IMPLEMENT-001A` precondition | Status after disposition |
|---|---|
| **P-1** — `CEP-009` amendment for `RG-09-A`, or revert 14 files | **NOT REQUIRED.** CEP-009 II.2/II.5 disclaim freeze jurisdiction; V.1 eligibility unmet; `00-BOOK` is not X-1. Replaced by `RB-01` (~2 lines). |
| **P-2** — resolve the `EIP-018` citations | **NOT REQUIRED as framed.** `AC-4` governs allocation, not comments; nothing minted; HEAD already cites the unresolvable `CRAP-001` in `verify.sh:109`. Residue folded into `RB-02`. |
| **P-3** — author `IMPLEMENT-001` D02/D03/D04 | **STILL REQUIRED** — but not a commit blocker. |
| **P-4** — disclose the two known-red conditions | **REDUCED** to `RB-04` (record) + `RB-03` (existing `WP-UCCEP-004`). |

---

## 2. `IMPLEMENT-001C` — scope

| # | Deliverable | Backlog | Effort | Blocking |
|---|---|---|---|---|
| **1** | **Register the P-7 work package** for the freeze-gated `platform/**` gate corrections. Content per Deliverable 06 `RB-02`: a non-shadowing token, the `FP-1…FP-14` register, declared surfaces, located gate defects, negative-path evidence. | `RB-02` | **0 lines** | **YES — commit** |
| **2** | **Execute the five-commit sequence** of Deliverable 07 §6, then `EVOLUTION-001` §6 + `RELEASE-001` §3.2 version entries. Discharges `OA-1` (P0 suspensive), `CK-REG-DRIFT`/`G-07`, 13 stale `content_hash` values, `B-1`, RIB `GATE-12` + `GATE-04`/`VAL-02`, RFP `CLO-01`. | — | operator act | **YES** |
| **3** | **Reconcile the DP-03 guard** — narrow `frozen_paths.py:17` `FROZEN_PREFIXES` to the located scope, with a mandatory negative-path proof that it still fails closed on `00-SOURCE/`, `99-FREEZE/` and the authored `00-BOOK` canon. Itself a P-7 act. | `RB-01` | **~2 lines** | **YES — push** |
| **4** | **Author `IMPLEMENT-001` D02, D03, D04.** D04 must define `B-1`/`B-2` (the gate-prerequisites all 9 backlog items cite); D03 must define `W1-C3` (the `UCCEP-F-003` record discharge). | — | authoring | No |
| **5** | **Record the two disclosures** — `repo-ops.sh` `repository-acceptance` expected-FAIL with a named owner; `EVOLUTION-001` §2 classification of change-set groups A–F. | `RB-04` | 0 lines | No |
| **6** | **Correct the citation record.** `CAEM-001/03:72` and `/05:31` assert `00-BOOK/**` is protected area X-1 and requires a `CEP-009` route. Both are disproved. `CAEM-001` is untracked, so this is correctable **before** it enters Repository Truth. | — | record | No |

**Exit criteria:** `verify.sh` GREEN · `make uccep-gate` blocking=none · `make closure-gate`
`CLOSED` gaps=0 · **`make rib-gate` exit 0** · **`make rfp-gate` evaluable** · working tree clean ·
`EVOLUTION-001` §6 records `UCOS-EVO-001-W01`.

### 2.1 Immediately, in parallel, by the operator

**Configure a git remote and push** (`GG-4`, OPEN since `OAA-001` §5). `UCOS-BASELINE-001` and
112 uncommitted paths exist on **one disk**. `*.bundle` is now correctly gitignored, which removed
the local workaround without supplying the durable path. Highest exposure, lowest effort, gates
nothing. Sequence after `RB-01`, since the first push runs the DP-03 guard.

---

## 3. THEN — `WAVE-002`

Authorized once `IMPLEMENT-001C` exits green. Order is `IMPLEMENT-001` D01 §5's topological
order, re-confirmed and unchanged.

| Order | Item | Class | Priority | Scope | Why here |
|---|---|---|---|---|---|
| **1** | **`EB-07`** — measured phase-3 verdict | Enhancement | **HIGH** | **S** | Zero dependencies. `phase3_engine.py:546` `"repository_status": "NOT-CLOSED"` is a literal, so `closure-gate` (`CLOSED`) and `phase3 --gate` (`NOT-CLOSED`) contradict each other in one programme. Certifying new work behind a verdict that cannot vary produces evidence of unknown value. |
| **2** | **`EB-01`** — bind `UCOS-UAR-001` | Extension | **HIGH** | **S** | Establishes the enforcement-binding pattern later items copy. Must fix all **5** defects: the no-op `_check_write_scope` (`uar_engine.py:72-77`), the three hardcoded verdict literals (`:104-107`), the undetected `F401`, the seal-not-over-emitted-bytes, and the zero wiring. |
| **3** | **`EB-02`** — Metering & Billing (Part 13) | Extension | **HIGH** | **L** | The only item discharging two immutable directives (`D22` Meterable, `D23` Billable). Must declare the disjointness boundary against `platform/measurement/` (`UCOS-UMA-001`). |
| **4** | **`EB-04`** — Registers 8–11 (`GG-3`) | Infrastructure | MEDIUM | **M** | Reuse `change-ledger.json` as the basis for register 8 — a derived projection, not a discharge. Do not conflate `REG-08` (the Dependency spec) with register 8. |
| **5** | **`EB-03`** — Universal Idea Box | New capability | MEDIUM | **M** | The only green-field item. Must not become a second capability-state authority (`AEOS-001` deny-list #3). |
| **6** | **`EB-05`** — Twin dimensions & subjects | Extension | MEDIUM | **M** | Subjects are emergent (pure data); dimensions/sources are fail-closed allowlists at `connectors/base.py:38` needing one append-only edit. |
| **7** | **`EB-08`** — Traceability fill | Enhancement | MEDIUM | **L** | Cheapest after new-artifact creation settles. **2.2%** (348/15,509). Sole cause of `CK-HEALTH` RED. |
| **8** | **`EB-06`** — Industry Generation (Part 43) | Extension | MEDIUM | **XL** | Largest; last. `ACFV` **R-7**: registry content only, never a new numbered family. |
| **—** | **`EB-09`** | Enhancement | LOW | M | ⛔ **NOT ORDERABLE.** `UCIC-001` FROZEN v1.0; `CEP-008` VI.1 two-valued calculus (`ACFV` **AG-03**). Awaits `CEP-009` — which, note, **does** have jurisdiction here: `EB-09` seeks to amend a frozen, ratified instrument, which is exactly CEP-009 V.1's subject matter. |

### 3.1 Wave-002 additions from this mission

| Item | Source | Class | Priority | Scope |
|---|---|---|---|---|
| **Extend lint + test surface** to `00-MASTER/**/*_engine.py` and `00-BOOK/tools/` | `IMPLEMENT-001A` D04 §5.1 · risk R-4 | Infrastructure | **HIGH** | S |
| **`RB-05`** — make `rib.json` convergent | `C-5` · `CF-07` | Defect correction | **P1** | S |
| **`RB-03`** — mandatory schema validation | `C-3` · `WP-UCCEP-004` · `OA-3` | Enhancement | P2 | S |
| **Measure the 4 remaining coverage dimensions**, or amend `CoverageProfile.REQUIRED` via its owning route | `C-2.2` | Enhancement | P2 | M |

> **`RB-03` gates any unqualified release claim** under `RELEASE-001` §4 (*"Schema + referential
> integrity PASS"*) — conflict `CF-03`. It is P2 for certification but a prerequisite for release.

---

## 4. WHAT IS NOT AUTHORIZED

| Act | Why not |
|---|---|
| Beginning any `EB-*` item | `EVOLUTION-001` §4 wave entry: `IMPLEMENT-001` D04, which defines `B-1`/`B-2`, does not exist |
| Committing before `RB-02` | 7 `platform/**` files are an X-8 mutation; P-7 requires the work package to pre-exist |
| **Pushing** before `RB-01` | The CI DP-03 guard — made fail-closed by this very change set — will reject the branch |
| Reverting `00-BOOK/SCHEMAS/**` | Restores 539 schema violations; no instrument freezes them; four Control-Tower standards authorize additive deltas |
| Reverting `00-BOOK/tools/config.py` | Not a corpus artifact (`REG-AUTO-001` §2); a declared registration input (§3 P3) |
| Reverting `platform/repository_operations/**` | Restores two gates that cannot fail (`covered:1/total:1` × 6; `paths: []`) |
| Deleting the `EIP-018 (FP-N)` comments | `GOV-002` §6/`RA5` make code citations traceability evidence to **preserve** |
| Writing to `00-SOURCE/`, `99-FREEZE/`, `00-CEP/`, `00-BOOK/DATA/` ledgers | X-1, X-2, X-4, X-5 — genuinely protected, currently untouched |
| Re-opening `C-3` under a new identifier | `X-9` forbids cross-programme edits; carried as `RB-03` under `WP-UCCEP-004` |
| Escalating another programme's non-blocking finding | `X-9`. This was `IMPLEMENT-001A`'s error with C-3. |
| Certifying a new baseline | Deliverable 08: attainable, not yet attained. `UCOS-BASELINE-001` stands. |
| Force-push, history rewrite, artifact removal | `RELEASE-001` §2.2 · `EVOLUTION-001` §5 |

---

## 5. AUTHORIZATION CHAIN

```
UCOS-BASELINE-001  (df763bf9 · CERTIFIED-PROVISIONAL · 68/68 realized · X-1/X-2/X-4/X-5 intact)
        │
        ├── EVOLUTION-001   governance model ESTABLISHED
        ├── RELEASE-001     lifecycle ESTABLISHED
        ├── OAA-001         WP-IMR-001 AUTHORIZED (engineering realization)
        │
        └── IMPLEMENT-001   ⛔ INTERRUPTED — D00 ✓ D01 ✓ D02 ✗ D03 ✗ D04 ✗
                 │
                 ├── IMPLEMENT-001A  ✓ audited · 4 blocking findings raised · NOT CERTIFIED
                 │
                 └── IMPLEMENT-001B  ✓ THIS MISSION
                          │          8 findings · 8 dispositions · 0 blocking
                          │          3 citation errors found · 3 new findings discovered
                          │          commit AUTHORIZED · 0 fixes implemented
                          │
                          └── IMPLEMENT-001C   ◀── THE NEXT AUTHORIZED MISSION
                                   │            RB-02 (0 lines) → 5 commits → RB-01 (2 lines)
                                   │            + IMPLEMENT-001 D02/D03/D04 + 2 disclosures
                                   │
                                   └── WAVE-002   ◀── after 001C exits green
                                            EB-07 → EB-01 → EB-02 → EB-04
                                                  → EB-03 → EB-05 → EB-08 → EB-06
                                            + lint/test surface · RB-05 · RB-03 · C-2.2
                                            (EB-09 excluded — CEP-009/AG-03)
```

Standing constraints unchanged: **`AC-1`** every item traces to an existing backlog entry ·
**`AC-2`** work selection derived, never manual · **`AC-3`** additive-only, corpus-read-only,
trace-preserving · **`AC-4`** no parallel identifier system (**allocation**, per `NF-1`/`NF-3`) ·
**`AC-5`** `verify.sh` GREEN after every cycle · **`AC-7`** all determinations PROVISIONAL until
`VAC-01` closes.

---

## 6. THE STANDING LESSON

Three of `IMPLEMENT-001A`'s four blocking findings failed on the same defect: **a derived
document was treated as authority.**

- `CAEM-001` (`AUTHORITY = NONE — DERIVED TRUTH`) asserted `00-BOOK/**` is protected area X-1 and
  requires a `CEP-009` route. Neither is true. `IMPLEMENT-001A` inherited both without opening
  `UCCEP-000006` Output 6 or `CEP-009`.
- `AC-4` was applied to code comments without reading `IMR-0000/06` `NF-1`/`NF-3`, which exempt
  non-identity references from admission.
- `C-3` was escalated to BLOCKING without checking `uccep-bindings.json`, where its owner had
  already recorded `blocking: false`.

The repository's own defence against this is explicit and was available in every case: **every
derived instrument carries `AUTHORITY = NONE` in its own header**, and the universal residual
clause — *"where any statement conflicts with a higher instrument, the higher instrument
governs"* — appears verbatim in ~20 artifacts.

> **A finding is only as strong as the instrument it cites, read at its source.**
>
> This is also why `IMPLEMENT-001A` remains valuable rather than wasted: it found the real
> issues (uncommitted registration, the `platform/**` attribution gap, the UAR defects,
> traceability at 2.2%, no remote) and its own reports are what made this verification tractable.
> Its error was in the *grading*, not the *observing*.

---

## 7. DETERMINATION

> ### NEXT AUTHORIZED MISSION: **`IMPLEMENT-001C` — Authorization Record & Atomic Commit**
>
> Six deliverables. **~2 lines of code.** One work-package record. One five-commit sequence.
>
> `RB-02` (0 lines) unblocks the commit. The commit discharges nine standing conditions,
> including the registered **P0 suspensive** `OA-1`. `RB-01` (~2 lines) unblocks the push.
>
> **In parallel and immediately, by the operator:** configure a remote and push. The certified
> baseline exists on one disk.
>
> `WAVE-002` becomes authorized when `IMPLEMENT-001C` exits green, and it begins with `EB-07` —
> because in a repository governed by gates, the first thing to fix is a gate that cannot fail.
> Three remain.

---

*END — `IMPLEMENT-001B` Deliverable 09 · AUTHORITY = NONE · `CERTIFIED-PROVISIONAL` · Tier T1 VACANT*
