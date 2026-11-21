# CIOS-05 — CONTINUOUS IMPLEMENTATION OPERATING SYSTEM · ENGINE INTERFACES

| Field | Value |
|---|---|
| MISSION | `IMR-003A` — CIOS Constitution & Architecture |
| ARTIFACT | `CIOS-05` — Engine Interfaces (mission Output 5) · **also the Public Interface Specification** (required output 12) |
| DELIVERED BY | `IMR-003A-R1` gap closure (Phase 4). **Additive**: no recovered artifact mutated. |
| ARTIFACT KIND | Interface specification (`CMG-K-05`) |
| DISCHARGES | the `CIOS-P-*` port family (allocated `IMR-003A` OUTPUT 0.4, never populated) |
| NUMERIC CONTRACT | **48 ports** — 2 per engine × 24 engines. Engine `CIOS-E-nn` holds inbound `CIOS-P-(2n-1)` and outbound `CIOS-P-(2n)`. |
| DOWNSTREAM SIGNIFICANCE | **This is the surface `IMR-003B` and every downstream mission consumes.** It is the subject of the Architecture & Interface Stability Contract (`IMR-003A-R1/09`). |
| AUTHORITY OF ITS OWN | **NONE.** A port is a declared contract, not an authority. |
| CONFLICT RULE | `CIOS-01` governs over this artifact; a located canonical instrument governs over `CIOS-01`'s bindings. |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. PORT DISCIPLINE

### 1.1 What a port is

| A port **is** | A port **is NOT** |
|---|---|
| a named, declared contract on an engine boundary | an API endpoint, RPC method, socket, topic or queue implementation |
| specified by direction, payload **class**, pre/post-condition and failure mode | specified by a serialization format, protocol, transport or schema language |
| a **declared data entry** (`CIOS-L-23`), addable without amending law | code — CIOS creates none (`AC-12`) |
| deterministic: same input ⇒ same output (`CIOS-L-17`) | stateful across invocations |

**Zero-enumeration compliance is structural here.** `CIOS-L-22` forbids CIOS from enumerating any protocol, serialization format, language or infrastructure. Ports are therefore specified by **payload class** — an abstract structural description — and never by wire format. A downstream mission choosing a format is making an implementation decision that CIOS neither constrains nor blesses.

### 1.2 Port rules

| ID | Rule | Enforces |
|---|---|---|
| `PR-1` | Every engine has exactly one inbound and one outbound port. No engine has a third. | `CIOS-03` §4 |
| `PR-2` | A port's payload class names no format, protocol, language, vendor or platform. | `CIOS-L-22`; `CK-SELF-NO-ENUMERATION` |
| `PR-3` | Every port declares a fail-closed failure mode. Absence of a declared failure mode is itself a defect. | `CIOS-L-07` |
| `PR-4` | An outbound port may write only within its engine's plane write scope (`CIOS-02` §4). | `CIOS-INV-02` |
| `PR-5` | `CIOS-PL-D` outbound ports emit **findings only** and write nothing. | `WS-6` |
| `PR-6` | A port carries no authority. Traversing a port never confers a right the traverser lacked. | `CIOS-L-11`; `CIOS-INV-12` |
| `PR-7` | Ports are versioned by the stability contract, not by in-place edit. Change routes through `CEP-009` III.1. | `IMR-003A-R1/09`; `CIOS-01` VIII.3 |
| `PR-8` | A port that cannot resolve its counterparty fails closed and emits a finding. It never degrades to a partial transfer. | `CIOS-L-07` |

---

## 2. THE PUBLIC INTERFACE — 8 PORTS

The **public surface** is the subset of ports crossing the CIOS boundary. Everything else is internal and may not be relied upon by any downstream mission.

**This distinction is the core of the contract.** A downstream mission that binds an internal port has bound something CIOS does not guarantee.

| Port | Engine | Direction | Role | Payload class |
|---|---|---|---|---|
| **`CIOS-P-01`** | `CIOS-E-01` | **INGRESS** | the **sole** submission entry point into CIOS | *submission descriptor* — subject, declared scope, declared dependencies, provenance, submitter authority |
| **`CIOS-P-35`** | `CIOS-E-18` | **INGRESS** | the **sole** override entry point into protected/sealed work | *override request* — authority identifier (`CIOS-OR-01` \| `CIOS-OR-02`), target, evidence set, protocol record reference |
| **`CIOS-P-30`** | `CIOS-E-15` | **EGRESS** | handoff to the located Execution Queue | *handoff record* — identity record reference, bound plan epoch, derived priority position |
| **`CIOS-P-40`** | `CIOS-E-20` | **EGRESS** | append to Repository Truth | *truth append record* — sealed item reference, terminal state, evidence set |
| **`CIOS-P-42`** | `CIOS-E-21` | **EGRESS** | traceability emission | *traceability edge* — `id → artifact` binding, canonical home reference |
| **`CIOS-P-44`** | `CIOS-E-22` | **EGRESS** | invariant findings | *finding* — invariant identifier, breach description, observed state reference |
| **`CIOS-P-46`** | `CIOS-E-23` | **EGRESS** | monotonicity findings | *finding* — epoch pair, certified-set cardinalities, direction |
| **`CIOS-P-48`** | `CIOS-E-24` | **EGRESS** | determinism findings | *finding* — replay pair, divergent field set |

### 2.1 Public-surface properties

| Property | Statement |
|---|---|
| **Single ingress for work** | `CIOS-P-01` is the only way a submission enters CIOS. There is no side door, no privileged path, no bulk-load bypass (`CEP-001` LAW-5 Non-Bypass). |
| **Single ingress for override** | `CIOS-P-35` is the only way protected or sealed work is reached, and it admits exactly two located authorities (`CIOS-L-21`). |
| **Egress is append or advisory only** | Of six egress ports, `P-30` hands off, `P-40`/`P-42` append, and `P-44`/`P-46`/`P-48` advise. **No egress port mutates a located artifact.** |
| **No egress port carries authority** | A finding is evidence, never an act (`PR-6`). |
| **Asymmetry is deliberate** | 2 ingress vs 6 egress. CIOS is designed to be hard to inject into and easy to observe. |

---

## 3. FULL PORT REGISTER — 48 PORTS

`I` = inbound · `O` = outbound. "Scope" is the write scope the outbound port operates within (`CIOS-02` §4).

### 3.1 `CIOS-PL-A` — Assimilation · `CIOS-P-01 … CIOS-P-28`

| Port | Dir | Engine | Payload class | Pre-condition | Post-condition / failure |
|---|---|---|---|---|---|
| `CIOS-P-01` | I | `E-01` | submission descriptor | submitter authority resolvable | in `CIOS-PT-00` · **fail:** not accepted |
| `CIOS-P-02` | O | `E-01` | intake record + provisional handle | `CIOS-PT-00` writable | scope `CIOS-PT-00` · **fail:** no intake |
| `CIOS-P-03` | I | `E-02` | intake record | `CIOS-P-02` produced | — |
| `CIOS-P-04` | O | `E-02` | context verdict (`CIOS-S-02`) | `G-01` verdict obtained | **fail:** non-admission on missing/ambiguous context |
| `CIOS-P-05` | I | `E-03` | context-cleared submission | `P-04` = PASS | — |
| `CIOS-P-06` | O | `E-03` | recurrence verdict `NEW \| EXTEND \| REJECT` | closure truth readable | **fail:** unresolvable match ⇒ non-admission; never resolves to `NEW` |
| `CIOS-P-07` | I | `E-04` | recurrence verdict | `P-06` ≠ REJECT | — |
| `CIOS-P-08` | O | `E-04` | resolved `(home, owner)` | exactly one home resolves | binds `CIOS-ID-11` · **fail:** 0 or >1 home ⇒ non-admission |
| `CIOS-P-09` | I | `E-05` | submission scope + admitted-item scopes | `P-08` produced | — |
| `CIOS-P-10` | O | `E-05` | overlap verdict + surviving owner | resolution order total | **fail:** unresolved overlap ⇒ non-admission, no deferral |
| `CIOS-P-11` | I | `E-06` | candidate `(home, owner, identity intent)` | `P-08`, `P-10` produced | — |
| `CIOS-P-12` | O | `E-06` | duplication verdict + breached classes | registers readable | **fail:** any duplicate ⇒ non-admission |
| `CIOS-P-13` | I | `E-07` | located minted fields | `P-12` = clear | — |
| `CIOS-P-14` | O | `E-07` | complete 22-field identity record | all 22 fields resolved | **fail:** any unresolved field ⇒ non-admission (`CIOS-INV-07`) |
| `CIOS-P-15` | I | `E-08` | declared dependency set | `P-14` produced | — |
| `CIOS-P-16` | O | `E-08` | dependency verdict + partial-order position | no cycle reported | **fail:** unresolvable dep **or** *reported* cycle ⇒ non-admission (see `UCCEP-F-003` bound, `CIOS-04` §2 `E-08`) |
| `CIOS-P-17` | I | `E-09` | submission + Repository Truth | `P-16` = PASS | — |
| `CIOS-P-18` | O | `E-09` | impact assessment + exactly one primary class | `CEP-009` IV.6 satisfied | **fail:** ambiguous class ⇒ non-admission |
| `CIOS-P-19` | I | `E-10` | verdict set of `E-02 … E-09` | all verdicts PASS | — |
| `CIOS-P-20` | O | `E-10` | `CIOS-PT-03` membership record | — | scope `CIOS-PT-03` · **fail:** item remains `CIOS-PT-00` |
| `CIOS-P-21` | I | `E-11` | `CIOS-PT-03` + `PLAN[n]` (read) + order | `P-20`, `P-24` produced | — |
| `CIOS-P-22` | O | `E-11` | staged candidate `PLAN[n+1]` | `PLAN[n]` untouched | scope `PLAN[n+1]` · **fail:** `PLAN[n]` stays active (DEGRADED-FUTURE) |
| `CIOS-P-23` | I | `E-12` | `CIOS-PT-03` + key vector `CIOS-K-01…08` | — | — |
| `CIOS-P-24` | O | `E-12` | **total** order over `CIOS-PT-03` | order is total | **fail:** unresolved tie ⇒ `CIOS-INV-09` breach, inadmissible |
| `CIOS-P-25` | I | `E-13` | `CIOS-PT-03` + new admissions + order | — | — |
| `CIOS-P-26` | O | `E-13` | resequenced `CIOS-PT-03` | target ⊆ `CIOS-PT-03` | scope `CIOS-PT-03` **only** · **fail:** reach outside ⇒ full rejection, no partial |
| `CIOS-P-27` | I | `E-14` | `PLAN[n+1]` + batch-cut boundary signal | at Quiescent Adoption Point | — |
| `CIOS-P-28` | O | `E-14` | adopted `PLAN[n]` (`n := n+1`) | adoption atomic | applies to `CIOS-PT-03` only · **fail:** no adoption; **no partial epoch** |

### 3.2 `CIOS-PL-B` — Execution · `CIOS-P-29 … CIOS-P-36`

| Port | Dir | Engine | Payload class | Pre-condition | Post-condition / failure |
|---|---|---|---|---|---|
| `CIOS-P-29` | I | `E-15` | head of `CIOS-Q-04` | queue non-empty | — |
| **`CIOS-P-30`** | O | `E-15` | **handoff record** → located Execution Queue | located queue accepts | **CIOS relinquishes control** · **fail:** item stays in `CIOS-Q-04`; never forced |
| `CIOS-P-31` | I | `E-16` | dispatch event + active epoch | dispatch occurred | — |
| `CIOS-P-32` | O | `E-16` | immutable `(item, epoch)` binding | epoch resolvable | scope `CIOS-PT-02` · **fail:** item not dispatched (no unbound in-flight item) |
| `CIOS-P-33` | I | `E-17` | interruption attempt (any source) | — | — |
| `CIOS-P-34` | O | `E-17` | rejection + finding | — | **default-deny** · **fail:** reject |
| **`CIOS-P-35`** | I | `E-18` | **override request** | authority ∈ {`CIOS-OR-01`,`CIOS-OR-02`} ∧ evidence present ∧ protocol record present | — |
| `CIOS-P-36` | O | `E-18` | adjudication + **mandatory** immutable record | record written | **default-deny** · **fail:** reject; an unrecorded override is **void** |

### 3.3 `CIOS-PL-C` — Truth · `CIOS-P-37 … CIOS-P-42`

| Port | Dir | Engine | Payload class | Pre-condition | Post-condition / failure |
|---|---|---|---|---|---|
| `CIOS-P-37` | I | `E-19` | terminal-state event | item ∈ `CIOS-PT-02` ∧ terminal | — |
| `CIOS-P-38` | O | `E-19` | `CIOS-PT-01` membership record | all preconditions met | scope `CIOS-PT-01` (append) · **fail:** item stays `CIOS-PT-02`; **no partial seal** |
| `CIOS-P-39` | I | `E-20` | seal record | `P-38` produced | — |
| **`CIOS-P-40`** | O | `E-20` | **truth append record** | append-only | scope Repository Truth (append) · **fail:** no seal — prefers unsealed truth to false truth |
| `CIOS-P-41` | I | `E-21` | sealed item + canonical home | `P-40` produced | — |
| **`CIOS-P-42`** | O | `E-21` | **traceability edge** | binding resolvable | **fail:** finding + item marked traceability-incomplete; does **not** block seal (`UCCEP-F-002` bound) |

### 3.4 `CIOS-PL-D` — Observation · `CIOS-P-43 … CIOS-P-48`

Every outbound port here writes **nothing** (`PR-5`, `WS-6`).

| Port | Dir | Engine | Payload class | Pre-condition | Post-condition / failure |
|---|---|---|---|---|---|
| `CIOS-P-43` | I | `E-22` | observable state, all planes | read access | — |
| **`CIOS-P-44`** | O | `E-22` | **finding** per breach of `CIOS-INV-01…12` (excl. `INV-10`) | — | writes nothing · **fail:** inability to observe is itself a finding; never reports a pass |
| `CIOS-P-45` | I | `E-23` | certified set per epoch | ≥2 epochs observable | — |
| **`CIOS-P-46`** | O | `E-23` | **finding** on `CIOS-INV-10` | — | writes nothing · **fail:** decrease ⇒ maximum-severity finding |
| `CIOS-P-47` | I | `E-24` | replayed run pair | ≥2 runs observable | — |
| **`CIOS-P-48`** | O | `E-24` | **finding** on determinism | — | writes nothing · **fail:** divergence ⇒ finding; witnessed ordinal **excluded** (`AIF-L04`, `AC-10`) |

---

## 4. PORT COUNT RECONCILIATION

| Plane | Engines | Ports | Range |
|---|---|---|---|
| `CIOS-PL-A` | 14 | **28** | `P-01 … P-28` |
| `CIOS-PL-B` | 4 | **8** | `P-29 … P-36` |
| `CIOS-PL-C` | 3 | **6** | `P-37 … P-42` |
| `CIOS-PL-D` | 3 | **6** | `P-43 … P-48` |
| **Total** | **24** | **48** | `P-01 … P-48` |

| Classification | Count | Ports |
|---|---|---|
| **Public — ingress** | **2** | `P-01`, `P-35` |
| **Public — egress** | **6** | `P-30`, `P-40`, `P-42`, `P-44`, `P-46`, `P-48` |
| **Internal** | **40** | all others |
| Ports with declared fail-closed mode | **48 / 48** | `PR-3` satisfied |
| Ports naming a format/protocol/language/vendor | **0** | `PR-2`, `CIOS-L-22` satisfied |
| Ports conferring authority | **0** | `PR-6` satisfied |
| Observation ports with write authority | **0** | `PR-5`, `WS-6` satisfied |

---

## 5. WHAT THE INTERFACE DOES NOT EXPOSE

Recorded so downstream missions do not mistake a located surface for a CIOS surface:

| Not exposed by CIOS | Consume it from |
|---|---|
| Dispatch | `IEC-001` C7 (EC-3 lane) |
| READY evaluation | `IEC-001` `03` P1–P7 |
| Item state transitions | `IEC-001` `06` (10 states) |
| Quality gate verdicts | `IEC-001` `08` Q1–Q8 |
| Batch formation | `IEC-001` `05` |
| Backlog, waves, order, critical path | `IMG-001` `03`–`09` |
| Identity minting | `AIF` + `REG-AUTO-001` + `00-BOOK/tools/` |
| Constitutional gate verdicts | `UCCEP-000000` `G-01…G-14` |
| Registration / id-ledger allocation | `REG-AUTO-001` |
| Validation execution | `CEP-004`; `verify.sh`; `engine/validation` |
| Certification execution | `CEP-005`; EC-3 gate; `engine/certification` |
| Freeze / seal | `CEP-007` — and **unavailable** (`GD-10`; `CIOS-01` IX.2) |

A downstream mission needing any of the above binds the located owner **directly**. Routing it through CIOS would create a second interface to a mechanism that already has one — a `CIOS-L-09` breach.

---

## AUTHORITY BOUNDARY (MANDATORY)

This artifact declares port contracts. It owns no mechanism, no registry, no gate, no identifier space and no concern. No port confers authority. Every authority named is located in an instrument existing independently at `b26c5bb`. Where this artifact and a located canonical instrument disagree, **the located instrument governs and this artifact SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `CIOS-05` · PROVISIONAL · ADDITIVE · COMPOSITION-ONLY · AUTHORITY-NEUTRAL**
