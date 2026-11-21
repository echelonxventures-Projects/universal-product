# IMR-003A-R1 · OUTPUT 6 — INTERFACE MATRIX

| Field | Value |
|---|---|
| MISSION | `IMR-003A-R1` |
| ARTIFACT | Output 6 — Interface Matrix |
| SCOPE | **Consumer-facing** binding matrix: which counterparty binds which port, under what obligation. The port **specifications** are owned by `IMR-003A/05-CIOS-ENGINE-INTERFACES.md` and are **bound here by pointer, not restated** (Knowledge Once). |
| CHECKPOINT | CP-006 |
| DISCLOSURE | PROVISIONAL; Tier T1 VACANT |
| VERDICT | **8 PUBLIC PORTS FROZEN FOR DOWNSTREAM RELIANCE · 40 INTERNAL PORTS NOT GUARANTEED.** |

---

## 1. WHAT THIS MATRIX ADDS

| Surface | Owner | Content |
|---|---|---|
| **Port specifications** — direction, payload class, pre/post-condition, failure mode | `IMR-003A/05` | all 48 ports |
| **Consumer bindings** — who may bind, what they may rely on, what they must not | `IMR-003A-R1/06` (this artifact) | the reliance contract |

A downstream mission reads `IMR-003A/05` to learn *what a port is* and this matrix to learn *whether it may bind it*.

---

## 2. THE RELIANCE BOUNDARY

| Class | Count | Reliance permitted? | Change route |
|---|---|---|---|
| **PUBLIC** | **8** | **YES** — downstream missions may bind and rely | `CEP-009` III.1 only; never in-place edit (`PR-7`) |
| **INTERNAL** | **40** | **NO** — not guaranteed; may change by data change | `cios-bindings.json` data change (`CIOS-L-23`) |

This is the operative distinction of the whole interface contract. **A downstream mission that binds an internal port has bound something CIOS does not guarantee**, and any breakage that results is not a contract violation.

---

## 3. PUBLIC INTERFACE MATRIX — THE 8 FROZEN PORTS

| Port | Dir | Counterparty | Counterparty obligation | CIOS obligation | Frozen |
|---|---|---|---|---|---|
| **`CIOS-P-01`** | INGRESS | any submitter of any kind | present a submission descriptor with resolvable submitter authority | accept into `CIOS-PT-00`, or reject; **never partially accept** | **YES** |
| **`CIOS-P-35`** | INGRESS | `CIOS-OR-01` \| `CIOS-OR-02` **only** | present authority id + evidence set + protocol record **before** any effect | default-deny; adjudicate via `E-18`; an unrecorded override is **void** | **YES** |
| **`CIOS-P-30`** | EGRESS | located Execution Queue (`IEC-001` `04`) | accept or decline; CIOS never forces | relinquish all control on acceptance | **YES** |
| **`CIOS-P-40`** | EGRESS | Repository Truth (`AIF-L08` ledger) | accept append | append-only; fail closed on incomplete append | **YES** |
| **`CIOS-P-42`** | EGRESS | traceability graph (`CEP-008`, `UMB-007`) | accept edge | emit edge or emit finding; **claim no closure** | **YES** |
| **`CIOS-P-44`** | EGRESS | located authorities (`CEP-010`, findings register) | act or not — CIOS cannot compel | emit one finding per `CIOS-INV-*` breach; write nothing | **YES** |
| **`CIOS-P-46`** | EGRESS | located authorities; `CIOS-OR-02` remedy path | act or not | emit maximum-severity finding on regression; write nothing | **YES** |
| **`CIOS-P-48`** | EGRESS | located authorities | act or not | emit finding on divergence, ordinal excluded; write nothing | **YES** |

### 3.1 Reliance guarantees for the 8 public ports

For each frozen port a downstream mission may rely on the following, and on nothing further:

| Guarantee | Basis |
|---|---|
| The port **exists** and keeps its identifier | `PR-7`; this matrix |
| Its **direction** does not reverse | `IMR-003A/05` §3 |
| Its **payload class** is not narrowed | `PR-7` |
| Its **failure mode is fail-closed** and does not become fail-open | `PR-3`; `CIOS-L-07` |
| It **confers no authority** on the traverser | `PR-6` |
| Its **write scope** does not widen | `PR-4`; `CIOS-INV-02` |
| Change arrives only via `CEP-009` III.1, with an impact assessment | `CIOS-01` VIII.3 |

| **Not** guaranteed | Why |
|---|---|
| Any serialization format, protocol, transport or schema | `CIOS-L-22` forbids CIOS enumerating them; the choice is the implementer's |
| Latency, throughput, ordering across ports | CIOS declares no runtime model; it creates no code (`AC-12`) |
| That a finding will be acted upon | a finding is evidence, never an act (`PR-6`) |
| Behaviour of the 40 internal ports | §2 |

---

## 4. INTERNAL PORTS — NOT FOR DOWNSTREAM RELIANCE

40 ports, spanning `CIOS-P-02 … P-29` (excluding `P-01`), `P-31 … P-34`, `P-36 … P-39`, `P-41`, `P-43`, `P-45`, `P-47`. Specifications in `IMR-003A/05` §3.

| Plane | Internal ports |
|---|---|
| `CIOS-PL-A` | 27 — `P-02 … P-28` |
| `CIOS-PL-B` | 6 — `P-29`, `P-31`, `P-32`, `P-33`, `P-34`, `P-36` |
| `CIOS-PL-C` | 4 — `P-37`, `P-38`, `P-39`, `P-41` |
| `CIOS-PL-D` | 3 — `P-43`, `P-45`, `P-47` |
| **Total** | **40** |

They exist to make the engine composition inspectable, not to be consumed. Adding, renaming or altering one is a **data change** to `cios-bindings.json` and amends no law.

---

## 5. WHAT DOWNSTREAM MISSIONS MUST BIND ELSEWHERE

The single most common misuse this matrix prevents: routing a located mechanism through CIOS. Doing so would create a second interface to a mechanism that already has one — a `CIOS-L-09` breach.

| Needed capability | Bind **directly** to | **Not** via CIOS |
|---|---|---|
| Dispatch | `IEC-001` C7 (EC-3 lane) | ✓ |
| READY evaluation | `IEC-001` `03` P1–P7 | ✓ |
| Item state machine | `IEC-001` `06` | ✓ |
| Quality gate verdicts | `IEC-001` `08` Q1–Q8 | ✓ |
| Batch formation | `IEC-001` `05` | ✓ |
| Backlog / waves / order / critical path | `IMG-001` `03`–`09` | ✓ |
| Identity minting | `AIF` + `REG-AUTO-001` + `00-BOOK/tools/` | ✓ |
| Constitutional gate verdicts | `UCCEP-000000` `G-01…G-14` | ✓ |
| Registration / `id-ledger` | `REG-AUTO-001` | ✓ |
| Validation execution | `CEP-004`, `verify.sh`, `engine/validation` | ✓ |
| Certification execution | `CEP-005`, EC-3 gate, `engine/certification` | ✓ |
| Freeze / seal | `CEP-007` — **and unavailable** (`GD-10`) | ✓ |

---

## 6. INTERFACE COVERAGE

| Check | Result | Machine check |
|---|---|---|
| Ports declared | **48** | `V-07` |
| Ports per engine | **2** (inbound + outbound) | `V-09` |
| Port convention `E-nn → P-(2n-1)`, `P-(2n)` | **24 / 24 conform** | `V-09` |
| Port identifier collisions | **0** | `V-07` |
| Public ports | **8** | `cios-bindings.json` `public_ports` |
| Public ingress | **2** (`P-01`, `P-35`) | §3 |
| Public egress | **6** | §3 |
| Internal ports | **40** | §4 |
| Ports with a declared fail-closed mode | **48 / 48** | `PR-3` |
| Ports naming a format/protocol/language/vendor | **0** | `V-89` |
| Ports conferring authority | **0** | `PR-6` |
| Observation ports with write authority | **0** | `V-23` |
| Egress ports that mutate a located artifact | **0** | `V-73` |

### 6.1 Ingress asymmetry

**2 ingress vs 6 egress.** CIOS is deliberately hard to inject into and easy to observe:

- exactly **one** way for work to enter (`P-01`) — no side door, no bulk-load bypass (`CEP-001` LAW-5 Non-Bypass);
- exactly **one** way to reach protected work (`P-35`) — admitting exactly two located authorities (`CIOS-L-21`);
- **six** ways to observe what CIOS did, of which three carry no write authority at all.

---

## AUTHORITY BOUNDARY (MANDATORY)

This matrix records consumer bindings and the reliance boundary. Port specifications are owned by `IMR-003A/05` and are not restated here. No port confers authority. This matrix creates no interface, confers no authority, and authorizes no execution. Where it and a located canonical instrument disagree, **the located instrument governs and this matrix SHALL be corrected**.

**END OF ARTIFACT — `IMR-003A-R1` OUTPUT 6 · PROVISIONAL · ADDITIVE · AUTHORITY-NEUTRAL**
