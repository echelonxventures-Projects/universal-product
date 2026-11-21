# IMR-003A-R1 · OUTPUT 17 — ARCHITECTURE & INTERFACE FREEZE REPORT

# CIOS ARCHITECTURE & INTERFACE STABILITY CONTRACT v1.0

| Field | Value |
|---|---|
| MISSION | `IMR-003A-R1` — Constitutional Recovery, Gap Closure & Architecture Freeze |
| ARTIFACT | Output 17 — Architecture Freeze Report |
| INSTRUMENT | **CIOS Architecture & Interface Stability Contract v1.0** |
| SUBJECT | The 23-artifact CIOS architecture at `00-MASTER/IMR-003A/` |
| BASELINE | `b26c5bb66c37717fe4eb96552bad4b9d8b74d890` — **not re-baselined** |
| CHECKPOINT | CP-006 |
| VERIFICATION | 162 / 162 machine checks PASS; 8 / 8 consistency dimensions; 0 unresolved conflicts (`08-ARCHITECTURE-VERIFICATION-REPORT.md`) |
| **INSTRUMENT CLASS** | **DECLARATION-SCOPED STABILITY CONTRACT — NOT a `CEP-007` CONSTITUTIONAL FREEZE** |
| DISCLOSURE | PROVISIONAL (`CMG-L-12`); Tier T1 **VACANT** (`VAC-01`) |
| STATUS | **IN FORCE** for downstream reliance, by composition and change-routing |

---

## 1. MANDATORY DISCLOSURE — WHAT THIS INSTRUMENT IS, AND IS NOT

The recovery instruction requires an *"Architecture Freeze v1.0"* whose contracts are *"immutable"*. **A `CEP-007` constitutional freeze is unavailable, and any attempt at one would be void.** This is an eligibility fact measured from located clauses, not a preference.

| Located clause | Requirement | Measured state | Limb |
|---|---|---|---|
| `CEP-007` III.2 | ratification (`CEP-006`) is an **entry condition** to the freeze lifecycle | Tier T1 **VACANT** (`VAC-01`, `located: false`); `CEP-006` names no competent authority; *"No programme may self-ratify"* (`UCCEP-000006` **ED-1**) | **FAIL** |
| `CEP-007` IV.1 | eligibility = VALIDATED ∧ CERTIFIED (active) ∧ RATIFIED — conjunctive | aggregate certification capped at `CERTIFIED-PROVISIONAL`; 31 of 43 artifacts PROVISIONAL | **FAIL** |
| `CEP-007` V.1 | preconditions include rooted-and-closed traceability (`CEP-001` XVIII) | `UCCEP-F-002` — 1198 / 1198 artifacts incomplete (≈22.7 %) | **FAIL** |
| `CEP-007` V.5 | *freeze SHALL NOT proceed while any precondition is unsatisfied* | three independent limbs fail | **PROHIBITED** |
| `CEP-007` IV.4 / II.4 | an attempted freeze of an ineligible artifact, or outside authorization, **SHALL be void** | a declared freeze here would be a **nullity** | **VOID** |
| `CEP-007` I.5 | freeze authority **SHALL NEVER be self-conferred** | CIOS holds no freeze authority | **N/A** |
| `GD-10` + `GD-10-C1` | freeze **REJECTED on eligibility**; no act shall declare, imply or record a freeze | binding precedent | **BINDING** |

### 1.1 What this instrument therefore does NOT do

| Does **NOT** | Machine check |
|---|---|
| declare a `CEP-007` freeze | `V-69` |
| declare a freeze baseline | `V-69` |
| declare a freeze authorization | `V-69` |
| assert freeze eligibility | `V-69` |
| add an entry to the `CEP-007` freeze registry (Art XVI) | `V-72` |
| alter the FROZEN population (27 artifacts in `artifacts.json`) | `V-73` |
| claim `CEP-004` validation, `CEP-005` active certification, or `CEP-006` ratification | `IMR-003A/20` §5 |
| claim constitutional immutability | §2 |
| affect, close or pre-empt `VAC-01` | `GD-10-C4` |
| treat any commit as a freeze baseline | `GD-10-C5` |

**This is a deliberate, disclosed divergence from the literal instruction**, taken because the literal act is void under located law. Recorded as `CIOS-GAP-13`, owner `CEP-007` freeze authority, unblocking condition **closure of `VAC-01`**.

### 1.2 What this instrument DOES do

It is the strongest lawful instrument available: a **binding stability declaration over CIOS's own declaration surface** — a surface CIOS exclusively owns, in a registration-excluded programme zone, containing **zero** corpus artifacts.

| Property | Value |
|---|---|
| Binding on | downstream missions consuming CIOS, **by composition** |
| Scope | CIOS's own declaration only — `00-MASTER/IMR-003A/` |
| Corpus artifacts within scope | **0** |
| Change route | `CEP-009` III.1 **only** — with impact assessment; never in-place edit |
| Enforcement | `r1_verify.py` (162 checks) at any later HEAD |
| Immutability class | **change-routed**, not sealed. True immutability requires a seal, which requires freeze, which is unavailable. |
| Authority conferred | **NONE** |

---

## 2. THE FROZEN SURFACE

The recovery instruction names ten items to freeze. Each is declared **STABLE** below, in the change-routed sense of §1.2.

| # | Instruction item | Delivered as | Stability |
|---|---|---|---|
| 1 | **Public Interfaces** | `IMR-003A/05` — 48 ports, **8 public** (`P-01`, `P-35` ingress; `P-30`, `P-40`, `P-42`, `P-44`, `P-46`, `P-48` egress) | **STABLE** — the 8 public ports are the reliance surface; the 40 internal ports are expressly **not** guaranteed (`06-INTERFACE-MATRIX.md` §2) |
| 2 | **Engine Contracts** | `IMR-003A/03`, `04`, `05` — 24 engines, each with class, plane, ports, responsibility, exclusion list, fail mode | **STABLE** |
| 3 | **Registry Contracts** | `07-REGISTRY-MATRIX.md` — 14 contracts, **all read-only** | **STABLE** |
| 4 | **Canonical Mission Object** | `IMR-003A/08` — the Canonical Submission Object, 22 fields `CIOS-ID-01…ID-22` | **STABLE** |
| 5 | **Mission Namespace** | `IMR-003A` OUTPUT 0.4 + `10-NAMESPACE-RECONCILIATION.md` — token `CIOS`, 13 identifier families | **STABLE** |
| 6 | **Mission Lifecycle** | `IMR-003A/07` — 24 stages `CIOS-S-01…S-24`, all 14 located gates bound | **STABLE** |
| 7 | **State Machine** | `CIOS-01` Art V (4 mutability partitions, one-way) + `IEC-001` `06` (10 item states, **located**) | **STABLE** (CIOS part); located part remains `IEC-001`'s |
| 8 | **Governance Contracts** | `IMR-003A/14` — 33 rules `GR-01…GR-33`, all with located owners | **STABLE** |
| 9 | **Validation Contracts** | `IMR-003A/15` — 14 rules `VR-01…VR-14`; 4 self-checks | **STABLE** |
| 10 | **Certification Contracts** | `IMR-003A/16` — 12 rules `CR-01…CR-12` | **STABLE** |

### 2.1 The stability guarantee

For each item above, a downstream mission may rely on the following and nothing further:

| Guaranteed | Not guaranteed |
|---|---|
| the element **exists** and keeps its identifier | any serialization format, protocol, transport or schema (`CIOS-L-22`) |
| declared **cardinalities** hold (24 / 24 / 22 / 48 / 8 / 4 / 4 / 2 / 10 / 7 / 14) | latency, throughput, cross-port ordering |
| **directions** do not reverse | that a finding will be acted upon |
| **failure modes stay fail-closed** | behaviour of the 40 internal ports |
| **write scopes do not widen** | runtime behaviour of any engine (CIOS creates no code) |
| **no element confers authority** | anything requiring `CEP-004`/`005`/`006`/`007` status |
| change arrives only via `CEP-009` III.1 | — |

### 2.2 Locked vs extensible

| **LOCKED** — requires `CEP-009` III.1 change to `CIOS-01` | **EXTENSIBLE** — data change to `cios-bindings.json` (`CIOS-L-23`) |
|---|---|
| 24 laws · 12 invariants · 4 planes · 4 partitions | gap register entries |
| Art X.1 cardinalities: **24** engines, **24** stages, **22** identity fields (`NS-4`) | declared class ranks for `CIOS-K-07` |
| priority key ranks **1–3** (located-order preservation) | key discriminators between ranks **4** and **7** |
| priority key rank **8** (totality terminator) | port payload-class detail that does not narrow |
| the 8 public ports | the 40 internal ports |
| the 2 override authorities (`CIOS-L-21`) | — |
| absence of a back-edge into `CIOS-PL-A` | — |
| zero CIOS stages in the located execution interval | — |

Two positions are structurally locked and may never move: **ranks 1–3** (or the located 77 would be reordered, breaching `CIOS-01` I.3) and **rank 8** (or `CIOS-INV-09` totality fails).

---

## 3. FREEZE PRECONDITIONS — MEASURED

| Precondition for this stability contract | Required | Measured | Verdict |
|---|---|---|---|
| All declared outputs present | 23 | **23** | **PASS** |
| Architectural gaps | 0 | **0** (was 28) | **PASS** |
| Dangling references (`CIOS-INV-11`) | 0 | **0** (was 12) | **PASS** |
| `CIOS-01` Art X.1 limbs satisfied | 8 | **8** | **PASS** |
| Mission acceptance `AC-1…AC-12` | 12 | **12** | **PASS** |
| Recovery acceptance `RAC-1…RAC-8` | 8 | **8** | **PASS** |
| Machine checks | all | **162 / 162** | **PASS** |
| Consistency dimensions | 8 | **8** | **PASS** |
| Unresolved conflicts | 0 | **0** | **PASS** |
| Duplicate responsibilities | 0 | **0** | **PASS** |
| Unresolved overlaps | 0 | **0** | **PASS** |
| Engines without a contract | 0 | **0** | **PASS** |
| Interfaces undefined | 0 | **0** | **PASS** |
| Registries unspecified | 0 | **0** | **PASS** |
| Lifecycles undefined | 0 | **0** | **PASS** |
| Governance rules undocumented | 0 | **0** (33 documented) | **PASS** |
| Validation rules undocumented | 0 | **0** (14 documented) | **PASS** |
| Certification rules undocumented | 0 | **0** (12 documented) | **PASS** |
| Gaps without a named owner | 0 | **0** (14/14 owned) | **PASS** |
| Corpus artifacts mutated | 0 | **0** | **PASS** |
| Recovered artifacts altered | 0 bytes | **0 bytes** | **PASS** |
| Repository Truth delta | none | **none** | **PASS** |

**Every precondition of this instrument is satisfied. None is waived.**

---

## 4. DOWNSTREAM AUTHORIZATION

### 4.1 What `IMR-003B` and downstream missions MAY now do

| Permitted | Basis |
|---|---|
| **Design and architect** implementation against the 8 public ports | `IMR-003A/05` §2; `06-INTERFACE-MATRIX.md` §3 |
| Rely on the 24 engine contracts, 24 stages, 22-field submission object, 4 queues, 8-element key vector | §2 |
| Rely on the 33 governance, 14 validation, 12 certification rules | §2 |
| Bind located mechanisms **directly** where CIOS exposes none | `06-INTERFACE-MATRIX.md` §5 |
| Extend CIOS by **data change** to `cios-bindings.json` within the extensible set | `CIOS-L-23`; §2.2 |
| Proceed **without modifying the foundation** | §4.2 |

### 4.2 The foundation-stability guarantee

The mission's success criterion requires that *"`IMR-003B` and all downstream missions can begin without modifying the foundation."* Verified:

| Test | Result |
|---|---|
| Are there unresolved architectural gaps a downstream mission would have to close first? | **NO** — 0 architectural gaps |
| Are there dangling references a downstream mission would have to repair? | **NO** — 0 (was 12) |
| Is any engine without a contract? | **NO** — 24/24 contracted |
| Is any interface undefined? | **NO** — 48 ports specified, 8 public |
| Is any lifecycle stage ungated? | **NO** — 24/24 gated or self-checked |
| Would a downstream mission need to allocate a namespace? | **NO** — `CIOS` allocated; 13 families populated |
| Would a downstream mission need to alter a located instrument? | **NO** — 0 located instruments amended |
| Would it need to reorder the located 77 or the wave partition? | **NO** — both preserved exactly |
| **∴ can downstream work begin without modifying the foundation?** | **YES** |

### 4.3 What remains BLOCKED — and what it blocks

| Blocked | Blocks | Does **not** block |
|---|---|---|
| `CIOS-G-01`, `CIOS-G-02` | CIOS **supremacy** | CIOS operation by composition and reference |
| `CIOS-G-03` (`VAC-01`) | standing above PROVISIONAL; ratification; active certification; **freeze** | admission as an architecture of record |
| `CIOS-G-04` (`UCCEP-F-003`) | corpus-wide machine enforcement of `CIOS-INV-05` | the in-artifact and self-check proof |
| `CIOS-G-05` (`UCCEP-F-006`) | non-degrading identity-record validation | fail-closed treatment of degraded validation |
| `CIOS-G-06` (`UCCEP-F-002`) | traceability **closure** claims | traceability **emission** |
| `CIOS-G-07` (`R1-F-001`) | commit-witnessed registration | working-tree registration |
| `GG-3`, `GG-4`, `GG-6`, `IAC-001 B+C` | **execution** of any implementation work package | **design** of downstream implementation |

**The critical distinction: downstream architecture and design are AUTHORIZED. Downstream EXECUTION remains BLOCKED**, exactly as `IMR-001` and `IMR-003A` recorded. This mission discharges none of those gates and does not authorize execution.

---

## 5. CHANGE CONTROL

| Rule | Statement |
|---|---|
| `SC-1` | A locked element (§2.2 left column) changes **only** by `CEP-009` III.1 with an impact assessment and exactly one primary class (IV.6). Never by in-place edit. |
| `SC-2` | An extensible element (§2.2 right column) changes by **data change** to `cios-bindings.json`, amending no law and altering no engine. |
| `SC-3` | Any change SHALL re-run `r1_verify.py`. A change that reduces the PASS count is **inadmissible**. |
| `SC-4` | Narrowing a public port's payload class, reversing its direction, converting a fail-closed mode to fail-open, or widening a write scope is a **breaking change** requiring `CEP-009` III.1. |
| `SC-5` | Removing a public port requires `CEP-009` III.1 **and** a successor declaration; downstream consumers must be identified in the impact assessment. |
| `SC-6` | An amendment that moves a located mechanism into CIOS is **VOID** (`CIOS-01` VIII.4; `CIOS-L-09`; `CEP-001` LAW-4). |
| `SC-7` | An amendment adding a back-edge into `CIOS-PL-A` is **VOID** — it would reintroduce the finite-project halt condition `CIOS-01` P.2 identifies. |
| `SC-8` | This contract confers no freeze and may not be cited as one. Its citation in support of a `CEP-007` eligibility claim is **void**. |
| `SC-9` | On closure of `VAC-01`, freeze re-assessment is reserved to `CEP-007`'s owner under its Article XX. This contract does not pre-authorize it and does not survive as an objection to it (`GD-10-C4`). |

---

## 6. STABILITY CERTIFICATE

```
CIOS ARCHITECTURE & INTERFACE STABILITY CONTRACT v1.0
------------------------------------------------------------------
INSTRUMENT     : Declaration-scoped stability contract
                 *** NOT a CEP-007 constitutional freeze ***
SUBJECT        : CIOS architecture — 23 artifacts, 00-MASTER/IMR-003A/
MISSION        : IMR-003A (recovered and completed by IMR-003A-R1)
BASELINE       : b26c5bb  (not re-baselined; NOT a freeze baseline)
SCOPE          : CIOS's own declaration; 0 corpus artifacts
VERIFICATION   : 162/162 machine checks PASS (exit 0)
                 8/8 consistency dimensions CONSISTENT
                 3 conflicts found, 3 resolved, 0 unresolved
CLOSURE        : CIOS-01 Art X.1 — 8/8 limbs SATISFIED
ACCEPTANCE     : AC-1..AC-12  12/12 PASS
                 RAC-1..RAC-8  8/8 PASS
NON-DESTRUCTION: VERIFIED — 0 bytes of recovered work altered
FROZEN SURFACE : 8 public interfaces · 24 engine contracts
                 14 registry contracts · 22-field submission object
                 CIOS namespace · 24-stage lifecycle
                 4 mutability partitions · 33 governance rules
                 14 validation rules · 12 certification rules
CHANGE ROUTE   : CEP-009 III.1 only (locked) / data change (extensible)
STANDING       : PROVISIONAL (CMG-L-12); Tier T1 VACANT (VAC-01)
NOT CLAIMED    : CEP-004 validation · CEP-005 active certification
                 CEP-006 ratification · CEP-007 freeze
                 traceability closure · constitutional immutability
RESIDUE        : 7 BLOCKED-EXTERNAL conditions, all owner-named
KNOWLEDGE ONCE : preserved — pointers only; zero duplication
------------------------------------------------------------------
DOWNSTREAM     : IMR-003B AND DOWNSTREAM MISSIONS ARE AUTHORIZED
                 TO BEGIN ARCHITECTURE AND DESIGN AGAINST THIS
                 SURFACE WITHOUT MODIFYING THE FOUNDATION.
                 EXECUTION REMAINS NOT AUTHORIZED (GG-3, GG-4,
                 GG-6, IAC-001 B+C, CIOS-G-01..G-07).
------------------------------------------------------------------
VERDICT        : STABILITY CONTRACT IN FORCE.
                 ARCHITECTURE IS IMPLEMENTATION-READY.
                 NO CONSTITUTIONAL FREEZE IS DECLARED,
                 IMPLIED, OR RECORDED.
------------------------------------------------------------------
```

---

## AUTHORITY BOUNDARY (MANDATORY)

This instrument declares stability over **CIOS's own declaration surface** and nothing else. It is **not** a `CEP-007` freeze, not a seal, not a freeze baseline, and not a claim of constitutional immutability. It confers no authority on itself or on CIOS, discharges no gate or finding, mutates no registry, adds no entry to the freeze registry, does not affect `VAC-01`, and **authorizes no execution**. Every authority named is located in an instrument existing independently at `b26c5bb`. Where this instrument and a located canonical instrument disagree, **the located instrument governs and this instrument SHALL be corrected**.

**END OF ARTIFACT — `IMR-003A-R1` OUTPUT 17 · PROVISIONAL · ADDITIVE · AUTHORITY-NEUTRAL**
