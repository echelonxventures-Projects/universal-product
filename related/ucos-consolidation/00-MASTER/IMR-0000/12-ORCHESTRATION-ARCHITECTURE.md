# IMR-0000/12 — ORCHESTRATION ARCHITECTURE

| Field | Value |
|---|---|
| MISSION | `IMR-0000` — CIOS Platform Foundation |
| ARTIFACT | `12` — Orchestration Architecture (**deliverable 22**) · directive capability 14 |
| ARTIFACT KIND | Architecture (`CMG-K-05`) — binding declaration + protection model |
| SUBSYSTEM | `SS-07` `CIOS-ORCH` (engines `E-15` ready handoff, `E-16` dispatch window, `E-17` interruption guard; ports `P-29`–`P-34`, public: **`CIOS-P-30`**) |
| MISSION MODE REMINDER | **No executable orchestration is produced** (`MC-05`). This artifact declares a handoff and protection discipline in text. |
| CENTRAL CLAIM | **The platform orchestrates nothing.** It hands off, then protects. Dispatch, state transitions, quality gates and batch formation are `IEC-001`'s, exercised in the EC-3 lane by the located Execution Authority. |
| AUTHORITY OF ITS OWN | **NONE.** `CIOS-01` I.4 — CIOS holds no execution authority. |
| CONFLICT RULE | Located instrument governs (`IEC-001`, then `GOV-INT-001` SECTION 8, then `CEP-009` for overrides); then `IMR-003A` (`CIOS-09`, `CIOS-11`); then this artifact. |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. THE HANDOFF DISCIPLINE

| ID | Rule | Located basis |
|---|---|---|
| `OA-1` | The platform hands the head of `CIOS-Q-04` to the located Execution Queue through `CIOS-P-30` and **relinquishes all further control**. It retains no dispatch right, no reordering right and no recall right. | `E-15`; `CIOS-01` I.4, VII.1 |
| `OA-2` | If the located queue does not accept, the item **stays in `CIOS-Q-04`**. It is never forced, never retried around the queue, and never dispatched by another path. | `E-15` FAIL mode; `CEP-001` LAW-5 Non-Bypass |
| `OA-3` | The item is bound at dispatch to the epoch then active, and holds that binding **until terminal state**. | `CIOS-INV-04`; `E-16` |
| `OA-4` | Every attempt to interrupt, suspend, mutate, reorder or invalidate a dispatched item is **rejected by default**. | `CIOS-L-03`; `E-17` |
| `OA-5` | The **only** lawful reach into protected or sealed work is `CIOS-P-35` on `SS-14`, admitting exactly two located override authorities under declared, evidenced, recorded protocol. **An unrecorded override is void.** | `CIOS-L-21`; `E-18` |
| `OA-6` | The interval between handoff and seal contains **no platform stage**. Declaring one would create a second lifecycle over a located mechanism. | `CIOS-07` §3; `CIOS-L-09` |

### 1.1 The boundary, drawn

```
SS-06  order derived, epoch adopted
   │
SS-07  E-15  ──►  CIOS-P-30  ──►  ╔══════════════════════════════════════╗
                                   ║  LOCATED EXECUTION — IEC-001         ║
   E-16  holds (item, epoch)       ║  READY predicates ....... 03 P1–P7   ║
   E-17  rejects interruption      ║  Queue order ............ 04         ║
        (default-deny)             ║  Batch formation ........ 05         ║
                                   ║  Dispatch ............... C7 · EC-3  ║
SS-14  E-18  ◄── CIOS-P-35 ──      ║  State machine .......... 06 (10)    ║
        (narrow-allow: OR-01/02)   ║  Quality gates .......... 08 (Q1–Q8) ║
                                   ║  Validation ............. CEP-004    ║
                                   ║  Certification .......... CEP-005    ║
                                   ╚══════════════════════════════════════╝
                                                    │
SS-01  E-19 seal  ◄─────────────────────  terminal-state event
SS-13  E-20 truth append · E-21 traceability edge
```

**During the interval the platform retains exactly two responsibilities, both protective and neither controlling:** `E-16` holds the epoch binding, and `E-17` rejects interruption.

---

## 2. THE PROTECTION MODEL

`CIOS-11` owns the interruption classes and the quiesce protocol. Bound here, not restated. The platform-level consequence:

| Posture | Engine | Behaviour |
|---|---|---|
| **default-deny** | `E-17` | rejects **all** interruption attempts, from any source, with a finding |
| **narrow-allow** | `E-18` | admits **only** `CIOS-OR-01` (Constitutional Migration Authority) and `CIOS-OR-02` (Critical Repository Integrity Authority), each acting by declared, evidenced, recorded protocol |

| Property | Value | Basis |
|---|---|---|
| Interruption classes declared | **10** (`CIOS-IC-01 … IC-10`), declared data, extensible | `CIOS-11` |
| Override authorities | **2**, both located; **a third may not be added by the platform** | `CIOS-L-21` |
| Unrecorded overrides | **void** | `E-18` `P-36` |
| Items resequenced after dispatch | **0** | `CIOS-L-18` |
| Sealed items rewritten | **0** — byte-identical across epochs | `CIOS-INV-03` |
| Reaches into `PT-01`/`PT-02` by the platform | **0** | `CIOS-L-19` |

### 2.1 Why default-deny plus narrow-allow, rather than a single policy

A single permission model would have to encode *who may interrupt what, when* — which is a discretionary judgement, and engines have no discretion (`CIOS-03` §1). Splitting the posture keeps both halves mechanical: `E-17` needs no knowledge of authorities (it rejects everything), and `E-18` needs no knowledge of interruption classes (it checks membership in a two-element located set plus the presence of evidence and a protocol record). Neither engine decides anything.

---

## 3. WHAT ORCHESTRATION MEANS AT PLATFORM LEVEL

The word is used in the corpus for three different things. The platform binds all three and owns none.

| Sense | Owner | Platform binding |
|---|---|---|
| **execution control** — the controller loop, dispatch, states, gates | `IEC-001` C1–C12 | `SS-07` handoff at `P-30`; nothing further |
| **governance orchestration** — the execution architecture and its lanes | `GOV-INT-001` SECTION 8; transaction `T` | read-only; the platform adds no phase to `T` |
| **session orchestration** — one logical capability per session, checkpointed | `MCS-000` §05/§06; `MCP-003`; `MCP-007` | `SS-11` binding (`13`, `14`) |

**No fourth sense is introduced.** A future programme that needs "orchestration" resolves it to one of these three and binds the located owner directly (`IFL-05`, `IFL-06`, `IFL-08` in `19`).

---

## 4. PROPERTIES

| Property | Value |
|---|---|
| Controllers, loops, dispatchers or executors defined | **0** |
| Executable orchestration produced | **0** (`MC-05`) |
| Dispatch rights held | **0** |
| Located queues reordered | **0** |
| Quality gates re-implemented | **0** |
| Item states defined | **0** |
| Platform stages inside the execution interval | **0** |
| Public ports on `SS-07` | **1** — `CIOS-P-30` egress |
| Control retained after `P-30` | **none** |
| Phases added to transaction `T` | **0** |

---

## 5. WHAT THIS ARTIFACT DOES NOT DO

| Not done | Located owner |
|---|---|
| Dispatch, schedule a dispatch, or authorize execution | `IEC-001` C7 (EC-3 lane); `CMG` T4 Execution Authority |
| Evaluate READY predicates, form batches, or transition item states | `IEC-001` `03`, `05`, `06` |
| Implement, re-implement or re-evaluate a quality gate | `IEC-001` `08` Q1–Q8 |
| Define or extend the interruption classes or the quiesce protocol | `CIOS-11` — bound by pointer |
| Add a third override authority | `CIOS-L-21` — exactly two, both located |
| Produce an executable, agent, runtime, deployment or infrastructure binding | `MC-05`, `MC-06` |
| Reach protected or sealed work | `CIOS-L-19`, `CIOS-L-21`; only `CIOS-P-35` reaches, and only for two located authorities |

---

## AUTHORITY BOUNDARY (MANDATORY)

This artifact declares a handoff and protection discipline. **It orchestrates nothing and produces no executable orchestration.** It holds no dispatch right, defines no controller, no queue order, no item state and no quality gate; it retains no control after handoff; it reaches no protected or sealed work. Every authority named is located in an instrument existing independently at `b26c5bb`, and dispatch authority remains with the located Execution Authority exercised through the located controller in the EC-3 lane. Where this artifact and a located canonical instrument disagree, **the located instrument governs and this artifact SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `IMR-0000/12` · PROVISIONAL · ADDITIVE · DESIGN-ONLY · AUTHORITY-NEUTRAL**
