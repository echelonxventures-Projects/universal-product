# IMPLEMENT-001C · DELIVERABLE 08 — NEXT AUTHORIZED MISSION

| Field | Value |
|---|---|
| MISSION | `IMPLEMENT-001C` |
| AUTHORITY | `NONE — DERIVED TRUTH` — records a determination; authorizes nothing |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT |

---

## 1. DETERMINATION

> ### NEXT AUTHORIZED MISSION: **`IMPLEMENT-001D` — Atomic Commit & Baseline Advancement**
>
> **Zero lines of code.** An operator act plus three records.
>
> Every code and configuration precondition is discharged. What remains is to commit what
> exists, push it, and record the evolution version.

---

## 2. `IMPLEMENT-001D` — scope

| # | Deliverable | Effort | Blocking |
|---|---|---|---|
| **1** | **Execute the five-commit sequence** of `IMPLEMENT-001C` Deliverable 06 §4. Discharges `OA-1` (P0 **suspensive**), `CK-REG-DRIFT`/`G-07`, **15** stale `content_hash` values, `B-1`, `C-1b`, RIB `GATE-12` + `GATE-04`/`VAL-02`, RFP `CLO-01`. | operator act | **YES** |
| **2** | **Configure the git remote and push.** `GG-4`, OPEN since `OAA-001` §5. `RB-01` already cleared the CI DP-03 guard, so the first push will pass it. | operator act | **YES — R-1 CRITICAL** |
| **3** | **Post-commit gate confirmation.** `./verify.sh` · `make uccep-gate` · `make closure-gate` · **`make rib-gate` (expect exit 0)** · **`make rfp-gate` (now evaluable)**. | verification | **YES** |
| **4** | **Record `UCOS-EVO-001-W01`** in `EVOLUTION-001` §6 and `RELEASE-001` §3.2 per `RELEASE-001` §5.1 step 5. Reaches the **`RELEASED`** lifecycle state. | record | No |
| **5** | **Author `IMPLEMENT-001` D02, D03, D04.** D04 must define `B-1`/`B-2` (the gate-prerequisites all 9 backlog items cite); D03 must define `W1-C3` (the `UCCEP-F-003` record discharge). | authoring | No |
| **6** | **Correct the `CAEM-001` citation record** — `03:72` and `05:31` assert `00-BOOK/**` is protected area **X-1** and requires a **`CEP-009`** route. Both are disproved (`IMPLEMENT-001B` D00 §3.1–3.2). `CAEM-001` is still **untracked**, so this is correctable *before* it enters Repository Truth. | record | No |

**Exit criteria:** working tree clean · `verify.sh` GREEN · `uccep-gate` blocking=none ·
`closure-gate` `CLOSED` gaps=0 · **`rib-gate` exit 0** · **`rfp-gate` evaluable** ·
`EVOLUTION-001` §6 records `UCOS-EVO-001-W01`.

### 2.1 Items deferred out of `IMPLEMENT-001C` — and why

Named in `IMPLEMENT-001B` D09 §2 as `IMPLEMENT-001C` scope, but **not** in the approved
remediation backlog (D06 §1 admission record). Per this mission's mandate — *"Reject any
remediation not explicitly approved"* — they were rejected here and carry forward as items 4–6:

| Item | Why deferred |
|---|---|
| Commit sequence | Phase 5 was *"Commit **Preparation**"* — determine grouping, not execute |
| `IMPLEMENT-001` D02/D03/D04 | Content creation, not remediation |
| `CAEM-001` citation correction | Another programme's output — **`X-9`: "No cross-programme edits"** |
| `EVOLUTION-001` §2 classification | Partially discharged as `WP-RO-001` §5 content; writing into `EVOLUTION-001` itself is `X-9` |
| Mark `UCCEP-F-006` `IMPLEMENTED` in `uccep-bindings.json` | Substantively discharged by `RB-03`; the **record** is `UCCEP-000000`'s act (`X-9`) |

---

## 3. THEN — `WAVE-002`

Authorized once `IMPLEMENT-001D` exits green. Order unchanged from `IMPLEMENT-001` D01 §5.

| Order | Item | Class | Priority | Scope | Why here |
|---|---|---|---|---|---|
| **1** | **`EB-07`** — measured phase-3 verdict | Enhancement | **HIGH** | **S** | Zero dependencies. `phase3_engine.py:546` `"repository_status": "NOT-CLOSED"` is a literal, so `closure-gate` (`CLOSED`) and `phase3 --gate` (`NOT-CLOSED`) contradict each other inside one programme. |
| **2** | **`EB-01`** — bind `UCOS-UAR-001` | Extension | **HIGH** | **S** | Establishes the enforcement-binding pattern. Must fix all **5** defects: the no-op `_check_write_scope` (`uar_engine.py:72-77`), the three hardcoded verdict literals (`:104-107`), the undetected `F401`, the seal-not-over-emitted-bytes, and the zero wiring. |
| **3** | **`EB-02`** — Metering & Billing (Part 13) | Extension | **HIGH** | **L** | The only item discharging `D22` Meterable + `D23` Billable. Declare the disjointness boundary against `platform/measurement/` (`UCOS-UMA-001`). |
| **4** | **`EB-04`** — Registers 8–11 (`GG-3`) | Infrastructure | MEDIUM | **M** | Reuse `change-ledger.json` as register 8's basis — a derived projection, not a discharge. |
| **5** | **`EB-03`** — Universal Idea Box | New capability | MEDIUM | **M** | Only green-field item. Must not become a second capability-state authority (`AEOS-001` #3). |
| **6** | **`EB-05`** — Twin dimensions & subjects | Extension | MEDIUM | **M** | Subjects emergent (data); dimensions/sources are fail-closed allowlists at `connectors/base.py:38`. |
| **7** | **`EB-08`** — Traceability fill | Enhancement | MEDIUM | **L** | Cheapest after new-artifact creation settles. **2.2%** (348/15,509). Sole cause of `CK-HEALTH` RED. |
| **8** | **`EB-06`** — Industry Generation (Part 43) | Extension | MEDIUM | **XL** | Largest; last. `ACFV` **R-7**: registry content only, never a new numbered family. |
| **—** | **`EB-09`** | Enhancement | LOW | M | ⛔ **NOT ORDERABLE** — `UCIC-001` FROZEN v1.0; `CEP-008` VI.1 two-valued calculus (`ACFV` **AG-03**). Awaits `CEP-009`, which **does** hold jurisdiction here: `EB-09` seeks to amend a frozen, ratified instrument — exactly CEP-009 V.1's subject. |

### 3.1 Wave-002 additions carried from `IMPLEMENT-001A/B/C`

| Item | Source | Class | Priority |
|---|---|---|---|
| **Extend lint + test surface** to `00-MASTER/**/*_engine.py` and `00-BOOK/tools/` | `IMPLEMENT-001A` D04 §5.1 · risk **R-4** | Infrastructure | **HIGH** |
| Extend the DP-03 review-scope exemption to `repo-ops.sh` `architecture-freeze` **without weakening the 18 write-time guards** | `IMPLEMENT-001C` D04 §7 | Defect correction | P2 |
| Measure `functions`, `public_api`, `exception_paths`, `repository`, or amend `CoverageProfile.REQUIRED` via its owning route | `C-2.2` · `RB-04` §6 | Enhancement | P2 |
| **Investigate concurrent programme-engine invocation safety** — one unreproduced `uccep-gate` exit 2 in 14 attempts | `IMPLEMENT-001C` D04 §6 · risk **R-9** | Defect correction | P3 |
| Author an `EPIC-PLAT-003` specification so `repo-ops.sh` ceases to self-own | `RB-04` §5 | Documentation | P3 |

---

## 4. WHAT IS NOT AUTHORIZED

| Act | Why not |
|---|---|
| Beginning any `EB-*` item | `EVOLUTION-001` §4 wave entry: `IMPLEMENT-001` D04, which defines `B-1`/`B-2`, still does not exist |
| Reverting `00-BOOK/SCHEMAS/**` | No instrument freezes them; four Control-Tower standards authorize additive deltas; the widening is provably admits-only; reverting restores **539** schema violations |
| Reverting `00-BOOK/tools/config.py` | Not a corpus artifact (`REG-AUTO-001` §2); a declared registration **input** (§3 P3) |
| Reverting `platform/repository_operations/**` | Now authorized under P-7 via `WP-RO-001`; reverting restores two gates that cannot fail |
| Narrowing `FROZEN_PREFIXES` | **21 call sites**, of which **18 are write-time guards** for which whole-tree `00-BOOK/` breadth is correct. Narrowing weakens 18 to fix 1. |
| Restoring `coverage: [6 × covered:1/total:1]` or `"paths": []` | Restores certification by fiat — defects `RO-F-01` / `RO-F-02` |
| Deleting the `EIP-018 (FP-N)` comments | `GOV-002` §6/`RA5` make code citations traceability evidence to **preserve**; `WP-RO-001` §3 maps them |
| Editing `uccep-bindings.json`, `CAEM-001`, `EVOLUTION-001`, `07-OPERATOR-ACTION-REGISTER.md` | **`X-9`** — another programme's outputs. Item 6 is permitted only because `CAEM-001` is still untracked. |
| Writing to `00-SOURCE/`, `99-FREEZE/`, `00-CEP/`, `00-CMG/`, `00-BOOK/DATA/` ledgers | X-1, X-2, X-3, X-4, X-5 — genuinely protected, currently **0 `git status` entries** |
| Force-push, history rewrite, squash, artifact removal | `RELEASE-001` §2.2 · `EVOLUTION-001` §5 |
| Certifying a new **baseline** | `UCOS-BASELINE-001` stands until `IMPLEMENT-001D` records `UCOS-EVO-001-W01`; a new *baseline* needs a capability milestone, not a remediation wave |

---

## 5. AUTHORIZATION CHAIN

```
UCOS-BASELINE-001  (df763bf9 · CERTIFIED-PROVISIONAL · 68/68 · X-1/X-2/X-3/X-4/X-5 intact)
        │
        ├── EVOLUTION-001 · RELEASE-001 · OAA-001
        │
        └── IMPLEMENT-001   ⛔ INTERRUPTED — D00 ✓ D01 ✓ D02 ✗ D03 ✗ D04 ✗
                 │
                 ├── IMPLEMENT-001A   audited · 4 blocking findings · NOT CERTIFIED
                 │
                 ├── IMPLEMENT-001B   disposed · 8 findings / 8 dispositions · 0 blocking
                 │                    3 citation errors found · 3 new findings discovered
                 │                    commit AUTHORIZED · 0 fixes implemented
                 │
                 └── IMPLEMENT-001C  ✓ THIS MISSION
                          │           RB-01…RB-05 DISCHARGED · 6 functional lines
                          │           7/7 conflicts closed · 0 material conflicts open
                          │           CERTIFIED lifecycle state REACHED
                          │           verify.sh GREEN · 0 preconditions outstanding
                          │
                          └── IMPLEMENT-001D   ◀── THE NEXT AUTHORIZED MISSION
                                   │            0 lines of code
                                   │            5 commits → push → UCOS-EVO-001-W01
                                   │            + IMPLEMENT-001 D02/D03/D04
                                   │            + CAEM-001 citation correction
                                   │
                                   └── WAVE-002   ◀── after 001D exits green
                                            EB-07 → EB-01 → EB-02 → EB-04
                                                  → EB-03 → EB-05 → EB-08 → EB-06
                                            + lint/test surface · freeze-scope · coverage
                                            + concurrency · EPIC-PLAT-003 spec
                                            (EB-09 excluded — CEP-009/AG-03)
```

Standing constraints: **`AC-1`** every item traces to an existing backlog entry · **`AC-2`** work
selection derived, never manual · **`AC-3`** additive-only, corpus-read-only, trace-preserving ·
**`AC-4`** no parallel identifier system (**allocation**, per `NF-1`/`NF-3`) · **`AC-5`**
`verify.sh` GREEN after every cycle · **`AC-7`** all determinations PROVISIONAL until `VAC-01`
closes.

---

## 6. THE STANDING LESSON FROM THIS MISSION

`IMPLEMENT-001B` was right about *what* to fix and wrong about *how*, twice — and both errors
were caught only by measuring before editing.

- **`RB-01`** was assessed as *"1 constant, 2 consumers."* It is **21 call sites**, 18 of them
  write-time guards. Executing the preferred option would have weakened 18 security guards to fix
  one review gate. The approved alternative was taken instead.
- **The drift set** was recorded as 13 registered artifacts. It is **15** — `IMPLEMENT-001B`
  queried only `00-BOOK/SCHEMAS/` and missed `repo-operations.json` and
  `03-ARCHITECTURAL-DECISION-ASSIMILATION-MATRIX.md`.

And this mission made its own error: a comment naming `GATE-12`, `VAL-02` and `IMPLEMENT`
verbatim, caught by `UCOS-RIB-001`'s own `--check-no-enumeration` guard before it landed.

> **A plan's scope estimate is a hypothesis. Measure the blast radius before editing, and let the
> repository's own guards adjudicate.**
>
> Three missions, three classes of error: `IMPLEMENT-001A` mis-graded findings by trusting a
> derived document as authority; `IMPLEMENT-001B` mis-sized two of them by sampling instead of
> enumerating; `IMPLEMENT-001C` mis-worded a comment. Each was caught by the layer after it —
> which is what the layering is for.

---

## 7. DETERMINATION

> ### NEXT AUTHORIZED MISSION: **`IMPLEMENT-001D` — Atomic Commit & Baseline Advancement**
>
> Six deliverables. **Zero lines of code.**
>
> All code and configuration preconditions are discharged: `RB-01`…`RB-05` executed,
> 7 of 7 constitutional conflicts closed, 0 material conflicts open, `RELEASE-001` §4 passing
> **7 of 7 unqualified**, `verify.sh` GREEN.
>
> What remains is an operator act: **commit the 131 paths, configure a remote, push, and record
> `UCOS-EVO-001-W01`.** That reaches the `RELEASED` lifecycle state and opens `WAVE-002`, which
> begins with `EB-07` — because in a repository governed by gates, the first thing to fix is a
> gate that cannot fail. Three remain.

---

*END — `IMPLEMENT-001C` Deliverable 08 · AUTHORITY = NONE · `CERTIFIED-PROVISIONAL` · Tier T1 VACANT*
