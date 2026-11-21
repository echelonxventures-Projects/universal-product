# IMPLEMENT-001A · DELIVERABLE 05 — NEXT AUTHORIZED EPIC

| Field | Value |
|---|---|
| MISSION | `IMPLEMENT-001A` |
| AUTHORITY | `NONE — DERIVED TRUTH` — this deliverable **records** a determination; it authorizes nothing |
| GOVERNED BY | `EVOLUTION-001` §4 (wave governance) · `RELEASE-001` §1 (lifecycle) · `OAA-001` §4 (`AC-1`…`AC-7`) |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT |

---

## 1. DETERMINATION

> ### ⛔ **NO IMPLEMENTATION EPIC IS AUTHORIZED TO BEGIN.**
>
> The next authorized act is **not an epic**. It is the **closure of `IMPLEMENT-001`** and the
> discharge of four preconditions.

`EVOLUTION-001` §4 sets the wave entry criteria. Three of four are unmet:

| Entry criterion | Status |
|---|---|
| All items classified | ⚠ **PARTIAL** — the 9 backlog items are classified; the code changes actually made are not |
| Impact analysis complete (no baseline destabilization) | ⛔ **UNMET** — 14 undispositioned frozen-corpus writes destabilize the `EVOLUTION-001` §1 rule-1 baseline protection |
| Dependencies satisfied | ⛔ **UNMET** — `B-1`/`B-2` are defined in the absent `IMPLEMENT-001` D04 |
| `verify.sh` GREEN at entry | ✓ **MET** |

Beginning Wave-002 now would carry forward one interrupted mission, one undispositioned
constitutional act, five unresolvable identifiers, and two permanently-red gates — which is
exactly what the mission's final success criterion forbids.

---

## 2. THE NEXT AUTHORIZED ACT — `IMPLEMENT-001B`

**`IMPLEMENT-001B` — Implementation Closure & Commit Authorization.**

Not an implementation epic. A closure mission. Scope is fixed, small, and entirely acts of
record.

| # | Deliverable | Discharges | Effort |
|---|---|---|---|
| 1 | **`IMPLEMENT-001` Deliverables 02, 03, 04.** D04 must define `B-1` and `B-2` (the gate-prerequisites cited by all 9 backlog items). D03 must define `W1-C3` (the `UCCEP-F-003` record discharge). D02 as implied by the 00→01 sequence. | C-5 · the interruption | authoring |
| 2 | **`RG-09-A` disposition.** Either `CEP-009` amendment authorizing the `00-BOOK/SCHEMAS` + `config.py` widening (and a matching `ec1-ci.yml` guard exclusion citing it), or `CEP-002` Art 27 deferral **plus revert of the 14 files**. This is `CAEM-001` §05 **S-2(a)/(b)**, never performed. | C-1 · `repo-ops.sh` `architecture-freeze` · the CI DP-03 step | act of record |
| 3 | **`EIP-018` identifier resolution.** Declare the programme and its `FP-N` register under a non-colliding id (`EIP-018` is held by *Pre-Wave-0 Constitutional Refinement*, `00-MASTER/EIP-018D/`), or re-cite the 8 lines to a located authority. | C-4 · `AC-4` · `RELEASE-001` §2.1 | act of record |
| 4 | **Known-red disclosure.** Record `repo-ops.sh` `repository-acceptance` as expected-FAIL with a named owner for the 4 unmeasured coverage dimensions; close `OA-3` by pinning `jsonschema` and dropping `\|\| true`. | C-2 · C-3 | act of record + 2 lines |
| 5 | **`EVOLUTION-001` classification of the change set.** Classify Groups A–F under §2 (extension / enhancement / infrastructure / amendment) so the code changes are governed, not merely present. | CLASSIFIED state | act of record |
| 6 | **Execute the four-commit sequence** of `IMPLEMENT-001A` D02 §6.1, then `EVOLUTION-001` §6 + `RELEASE-001` §3.2 version entries. | `B-1` · `B-2`/`CK-REG-DRIFT` · `RIB` `GATE-12`/`GATE-04` · `RFP` `CLO-01` | operator act |

**Exit criteria:** `verify.sh` GREEN · `make uccep-gate` blocking=none · `make closure-gate`
`CLOSED` · `make rib-gate` **exit 0** · `make rfp-gate` **evaluable** · working tree clean ·
`EVOLUTION-001` §6 records `UCOS-EVO-001-W01`.

### 2.1 Prerequisite, out of band and above all of it

**Configure a git remote and push** (`GG-4`, OPEN since `OAA-001` §5). `UCOS-BASELINE-001`
and 96 uncommitted paths exist on exactly one disk. `*.bundle` is now correctly gitignored,
which removed the local workaround without supplying the durable path. This is the
highest-exposure, lowest-effort action in the entire register (D04 §6 action 1) and it
gates nothing — it can be done immediately, in parallel, by the operator.

---

## 3. THE EPIC AFTER THAT — `WAVE-002`, and the order it must run in

Authorized **only** once `IMPLEMENT-001B` exits green. The ordering is `IMPLEMENT-001` D01
§5's topological order, unchanged and re-confirmed by this mission.

| Order | Item | Class | Priority | Scope | Why here |
|---|---|---|---|---|---|
| **1** | **`EB-07`** — measured phase-3 verdict | Enhancement | **HIGH** | **S** | Zero dependencies. Makes a gate capable of failing. Until then `CK-CLOSURE-P3` fails advisorily in every UCCEP run and the two engines of one programme contradict each other (`closure-gate` → `CLOSED` vs `phase3 --gate` → `repo=NOT-CLOSED`). **Certifying new work behind a verdict that cannot vary produces evidence of unknown value.** |
| **2** | **`EB-01`** — bind `UCOS-UAR-001` | Extension | **HIGH** | **S** | Highest enforcement-value-to-scope ratio. Establishes the enforcement-binding pattern every later item will copy. Must additionally fix all **5** defects: the no-op `_check_write_scope`, the three hardcoded verdict literals, the `F401`, the seal-not-over-emitted-bytes, and the zero wiring. |
| **3** | **`EB-02`** — Metering & Billing (Part 13) | Extension | **HIGH** | **L** | The only item discharging two immutable directives (`D22` Meterable, `D23` Billable) and the only one unblocking the 22-interface conformance test. All three MIP part-dependencies present. Must declare the disjointness boundary against `platform/measurement/` (`UCOS-UMA-001`) or `AEOS-001` / Knowledge Once is at risk. |
| **4** | **`EB-04`** — Registers 8–11 (`GG-3`) | Infrastructure | MEDIUM | **M** | id-ledger present; 4 schemas in scope. Reuse `change-ledger.json` as the basis for register 8 — it is a *derived projection*, not a discharge. Do not conflate `REG-08` (the Dependency **spec**) with register 8. |
| **5** | **`EB-03`** — Universal Idea Box | New capability | MEDIUM | **M** | The only green-field item in the mandate. Must **not** become a second capability-state authority (`AEOS-001` deny-list #3). `platform/generation/registry.py` is classified-on-entry — a pattern reference, not a host. |
| **6** | **`EB-05`** — Twin dimensions & subjects | Extension | MEDIUM | **M** | Subject types are emergent (pure data, `setdefault` in `rollup_dimensions()`); dimensions and sources are hardcoded fail-closed allowlists at `connectors/base.py:38` and need one append-only code edit. `twin.json` is generated — never hand-edited. |
| **7** | **`EB-08`** — Traceability fill | Enhancement | MEDIUM | **L** | Cheapest **after** new-artifact creation settles: every earlier item adds 13 more empty slots. Currently **2.2%** (348 / 15,509); sole cause of `CK-HEALTH` RED. |
| **8** | **`EB-06`** — Industry Generation (Part 43) | Extension | MEDIUM | **XL** | Largest item; last. `UCOS-ACFV-000001` **R-7**: author as registry content, never a new numbered family. A `16-COMMERCE/` directory would fail the Architecture Admission Test. Sector ontologies are **data** in `00-BOOK/DATA/` per `LAW P43-001`. |
| **—** | **`EB-09`** — Validation evidence extensions | Enhancement | LOW | M | ⛔ **NOT ORDERABLE.** Governance-blocked: `UCIC-001` is FROZEN v1.0; `CEP-008` VI.1 defines a two-valued certification calculus (`ACFV` **AG-03**), so a confidence model requires a constitutional clarification, not code. **Ineligible for any wave until `CEP-009` disposes of `AG-03`.** |

**Ordering rationale, restated:** there is **not one hard dependency between any two
backlog items** (D01 §3). Eight could execute in parallel. They should not, because items
1, 2 and 7 determine whether the other five can be **honestly certified**.

### 3.1 Additional Wave-002 items this mission adds

Not new capability — repair of gaps this mission measured and no register holds.

| Item | Class | Priority | Scope | Basis |
|---|---|---|---|---|
| **Extend the lint + test surface** to `00-MASTER/**/*_engine.py` and `00-BOOK/tools/` | Infrastructure | **HIGH** | S | D04 §5.1 · risk R-4. The governance mechanism is itself unlinted and untested; demonstrated by the undetected `F401` in `uar_engine.py`. |
| **Measure the 4 remaining acceptance coverage dimensions** (`functions`, `public_api`, `exception_paths`, `repository`) or amend `CoverageProfile.REQUIRED` through the proper route | Enhancement | MEDIUM | M | C-2. Without this, `repo-ops.sh` is permanently red. |

---

## 4. WHAT IS **NOT** AUTHORIZED

| Act | Why not |
|---|---|
| Beginning any `EB-*` item | Wave entry criteria unmet (§1). `IMPLEMENT-001` D04, which defines the gate-prerequisites, does not exist. |
| Committing the current tree as one commit | `IMPLEMENT-001A` D02: would make an undispositioned DP-03 violation permanent under a no-force-push history. Four commits, after four preconditions. |
| Any further write to `00-BOOK/**` | `DP-03` / **X-1**. The 14 existing writes are already undispositioned; adding more compounds C-1. |
| Any write to `00-SOURCE/**`, `99-FREEZE/**` | Frozen. `FROZEN_PREFIXES`. |
| `EB-09` | `CEP-009` / `AG-03` unresolved. |
| Certifying a new baseline | `IMPLEMENT-001A` D03: certification withheld. `UCOS-BASELINE-001` remains the last certified state. |
| Recording an evolution version | `RELEASE-001` §1: `RELEASED` requires `CERTIFIED` first. |
| Force-push, history rewrite, artifact removal | `RELEASE-001` §2.2 · `EVOLUTION-001` §5. |

---

## 5. AUTHORIZATION CHAIN — as it actually stands

```
UCOS-BASELINE-001  (df763bf9 · CERTIFIED-PROVISIONAL · 68/68 realized)
        │
        ├── EVOLUTION-001   governance model ESTABLISHED
        ├── RELEASE-001     lifecycle ESTABLISHED
        ├── OAA-001         WP-IMR-001 AUTHORIZED  (engineering realization, corpus-read-only)
        │
        └── IMPLEMENT-001   ⛔ INTERRUPTED — D00 ✓ · D01 ✓ · D02 ✗ · D03 ✗ · D04 ✗
                 │
                 └── IMPLEMENT-001A  ✓ THIS MISSION — audited, measured, NOT CERTIFIED
                          │
                          └── IMPLEMENT-001B   ◀── THE NEXT AUTHORIZED ACT
                                   │            closure + 4 dispositions + 4 commits
                                   │
                                   └── WAVE-002   ◀── authorized only after 001B exits green
                                            EB-07 → EB-01 → EB-02 → EB-04
                                                  → EB-03 → EB-05 → EB-08 → EB-06
                                            (EB-09 excluded — CEP-009/AG-03)
```

Standing constraints, unchanged: **`AC-1`** every item traces to an existing backlog entry ·
**`AC-2`** work selection derived, never manual · **`AC-3`** additive-only, corpus-read-only,
trace-preserving · **`AC-4`** no parallel identifier system · **`AC-5`** `verify.sh` GREEN
after every cycle · **`AC-7`** all determinations PROVISIONAL until `VAC-01` closes.

---

## 6. DETERMINATION

> ### NEXT AUTHORIZED EPIC: **NONE.**
>
> ### NEXT AUTHORIZED ACT: **`IMPLEMENT-001B` — Implementation Closure & Commit Authorization.**
>
> Six deliverables. Five are acts of record. One is a four-commit sequence. No new
> functionality, no new identifier family, no architectural change.
>
> **In parallel and immediately, by the operator:** configure a git remote and push. The
> certified baseline exists on one disk.
>
> `WAVE-002` becomes authorized the moment `IMPLEMENT-001B` exits green, and it begins with
> `EB-07` — because the first thing to fix in a repository governed by gates is a gate that
> cannot fail.

---

*END — `IMPLEMENT-001A` Deliverable 05 · AUTHORITY = NONE · `CERTIFIED-PROVISIONAL` · Tier T1 VACANT*
