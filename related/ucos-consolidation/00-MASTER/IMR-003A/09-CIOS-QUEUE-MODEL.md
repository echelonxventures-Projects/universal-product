# CIOS-09 — CONTINUOUS IMPLEMENTATION OPERATING SYSTEM · QUEUE MODEL

| Field | Value |
|---|---|
| MISSION | `IMR-003A` — CIOS Constitution & Architecture |
| ARTIFACT | `CIOS-09` — Queue Model (mission Output 9) |
| DELIVERED BY | `IMR-003A-R1` gap closure (Phase 4). **Additive**: no recovered artifact mutated. |
| DISCHARGES | the `CIOS-Q-*` family; `CIOS-01` Art VII.3 row r1 — *"`IEC-001` `04` begins at the Execution Queue; the queues upstream of it are undefined in the repository"* |
| NUMERIC CONTRACT | **4 queues**, `CIOS-Q-01 … CIOS-Q-04` |
| NON-DUPLICATION BASIS | Every CIOS queue is **strictly upstream** of the located Execution Queue. CIOS defines nothing at or downstream of it. |
| AUTHORITY OF ITS OWN | **NONE.** |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. THE BOUNDARY THAT MAKES THIS NON-DUPLICATIVE

`IEC-001` `04` defines four queues, measured at its baseline: Execution Queue (77), Ready Queue (20), Blocked Set (45), Excluded Set (13). Those remain **wholly located and untouched**.

The located model's earliest membership rule is *"`disposition=SPECIFIED` ∧ not sentinel at load"* — it presupposes an object that **already exists in Repository Truth**. Nothing in the repository describes how a submission becomes such an object. That undefined interval is what `CIOS-Q-01 … CIOS-Q-04` occupy.

```
  submission
      │
      ▼
┌─────────────────────── CIOS (this artifact) ───────────────────────┐
│  CIOS-Q-01 INTAKE ─▶ CIOS-Q-02 ADMISSION ─▶ CIOS-Q-03 OPEN ─▶     │
│                                              CIOS-Q-04 HANDOFF     │
└────────────────────────────┬───────────────────────────────────────┘
                             │  CIOS-P-30 — handoff; CIOS relinquishes control
                             ▼
╔═══════════════════════ LOCATED — IEC-001 04 ═══════════════════════╗
║  Execution Queue ─▶ Ready Queue ─▶ Execution Batch                 ║
║  Blocked Set · Excluded Set                                        ║
╚════════════════════════════════════════════════════════════════════╝
```

| Test | Result |
|---|---|
| Does any CIOS queue duplicate a located queue's membership rule? | **NO** — located membership begins at `disposition=SPECIFIED`; CIOS queues end before that |
| Does any CIOS queue reorder a located queue? | **NO** — CIOS relinquishes control at `CIOS-P-30` (`E-15` EXCLUDES) |
| Does CIOS define a second Ready Queue? | **NO** — `CIOS-Q-04` is a *handoff* queue; readiness is evaluated by located `P1 … P7`, which CIOS does not re-evaluate |
| Does CIOS define a second Blocked Set? | **NO** — a CIOS non-admission returns the submission to `CIOS-PT-00` (`LT-4`), which is not a blocked set but a discardable intake partition |

---

## 2. THE FOUR QUEUES

| ID | Queue | Membership rule (derived) | Order | Partition | Plane |
|---|---|---|---|---|---|
| **`CIOS-Q-01`** | **Intake** | received at `CIOS-P-01`, not yet at `CIOS-S-02` | arrival, by witnessed admission ordinal (`CIOS-ID-06`) | `CIOS-PT-00` | `PL-A` |
| **`CIOS-Q-02`** | **Admission** | in stage traversal `CIOS-S-02 … CIOS-S-18`, no terminal verdict | by stage reached, then ordinal | `CIOS-PT-00` | `PL-A` |
| **`CIOS-Q-03`** | **Open** | admitted at `CIOS-S-19`; not yet handed off | **total** order from `CIOS-K-01 … CIOS-K-08` (`CIOS-10`) | `CIOS-PT-03` | `PL-A` |
| **`CIOS-Q-04`** | **Handoff** | in the adopted epoch `PLAN[n]`, awaiting acceptance by the located Execution Queue | inherits `CIOS-Q-03` order | `CIOS-PT-03` | `PL-A` → `PL-B` boundary |

### 2.1 Per-queue detail

**`CIOS-Q-01` — Intake.** Holds submissions that have entered but on which no substantive determination has been made. Members are *freely discardable and outside every plan* (`CIOS-01` Art V). Unbounded in size (`CIOS-L-24`). A submission here has no identity beyond a provisional handle (`E-01` EXCLUDES).

**`CIOS-Q-02` — Admission.** Holds submissions mid-traversal. This queue is where fail-closed bites: a submission whose stage verdict is unresolved stays here and **never advances** (`LT-2`). It does not accumulate as a backlog of near-admissions; on terminal non-admission it returns to `CIOS-Q-01` for discard (`LT-4`).

**`CIOS-Q-03` — Open.** The only CIOS queue that is **resequenceable**. `E-13` (Realignment) writes here and nowhere else (`CIOS-L-19`, `CIOS-01` V.2). This single restriction is what makes continuous replanning safe.

**`CIOS-Q-04` — Handoff.** The boundary queue. Membership is fixed by the adopted epoch; realignment cannot reach it, because realignment writes only `CIOS-Q-03` and adoption is atomic (`E-14`). An item the located Execution Queue declines remains here; CIOS never forces admission (`E-15` FAIL).

---

## 3. QUEUE OPERATIONS

| Operation | Trigger (derived) | Effect | Engine |
|---|---|---|---|
| **Receive** → `CIOS-Q-01` | submission at `CIOS-P-01` | placed by arrival ordinal | `E-01` |
| **Enter** → `CIOS-Q-02` | `CIOS-S-01` complete | begins stage traversal | `E-02` |
| **Advance** within `CIOS-Q-02` | a stage verdict resolves PASS | stage counter advances | `E-02 … E-09` |
| **Admit** → `CIOS-Q-03` | all of `CIOS-S-02 … CIOS-S-18` PASS | partition `PT-00 → PT-03` | `E-10` |
| **Return** → `CIOS-Q-01` | any terminal non-admission | no partial admission retained | `E-10` |
| **Resequence** within `CIOS-Q-03` | new admission or realignment trigger | order re-derived | `E-13` + `E-12` |
| **Stage** → `PLAN[n+1]` | epoch composition | candidate composed; `PLAN[n]` untouched | `E-11` |
| **Adopt** → `CIOS-Q-04` | Quiescent Adoption Point reached | atomic; applies only to `CIOS-PT-03` | `E-14` |
| **Hand off** → located Execution Queue | located queue accepts | **CIOS relinquishes control** | `E-15` |
| **Retain** in `CIOS-Q-04` | located queue declines | never forced | `E-15` |

**No operation removes an item from `CIOS-Q-04` except acceptance by the located queue.** There is no timeout eviction, no priority preemption and no forced drain — each would be a `CIOS-L-03` breach in spirit and would give CIOS a dispatch power it does not hold (`CIOS-01` I.4).

---

## 4. QUEUE PROPERTIES

| Property | Value | Basis |
|---|---|---|
| Queues | **4** | §2 |
| Queues at or downstream of the located Execution Queue | **0** | §1 |
| Queues that are resequenceable | **1** (`CIOS-Q-03`) | `CIOS-L-19`; `CIOS-01` V.2 |
| Queues with a size bound | **0** — all unbounded | `CIOS-L-24` |
| Queues with a total order | **2** (`CIOS-Q-03`, `CIOS-Q-04`) | `CIOS-INV-09` |
| Queues written by more than one plane | **0** | `CIOS-INV-02`; `CIOS-02` §4.3 |
| Queues from which CIOS can force downstream admission | **0** | `CIOS-01` I.4 |
| Manual insertion or reordering permitted | **NO** | `CIOS-L-16` (Derived Selection) |
| Ordering by timestamp | **NO** — by witnessed ordinal | `CIOS-L-15`; `AIF-L04` |

### 4.1 Unboundedness

No queue declares a capacity, high-water mark, admission-control threshold or backpressure signal. This is required, not an omission:

- `CIOS-L-24` forbids assuming a finite number of submissions, items or planning cycles.
- A backpressure signal from any queue toward `CIOS-P-01` would be a **back-edge into `CIOS-PL-A`**, which `CIOS-06` §5.1 establishes must not exist — it would let queue state gate admission, reintroducing the halt condition `CIOS-01` P.2 identifies.

Queue growth is therefore lawful and expected. An oversized `CIOS-Q-03` is an **observation** for `CIOS-PL-D` (`E-22`) to report as a finding, never a condition that throttles intake.

---

## 5. RELATIONSHIP TO THE LOCATED QUEUE FAMILY

| Located queue (`IEC-001` `04`) | Owner | CIOS relationship |
|---|---|---|
| Execution Queue | `IEC-001` | receives from `CIOS-Q-04` via `CIOS-P-30`; **CIOS does not order it** |
| Ready Queue | `IEC-001` | membership by located `P1 … P7`; **CIOS does not evaluate them** |
| Execution Batch | `IEC-001` `05` | batch formation is located; CIOS reads only the batch-cut **boundary** as the Quiescent Adoption Point |
| Blocked Set | `IEC-001` | located; CIOS non-admissions do not enter it |
| Excluded Set | `IEC-001` | located sentinels; outside CIOS entirely |

CIOS reads exactly **one** signal from the located queue family — the batch-cut boundary, consumed by `E-14` at `CIOS-P-27` — and writes exactly **one** — the handoff at `CIOS-P-30`. This narrow two-signal coupling is what keeps the located queue model sovereign.

---

## AUTHORITY BOUNDARY (MANDATORY)

This artifact declares four queues strictly upstream of the located Execution Queue. It owns no located queue, no mechanism, no registry, no gate, no identifier space and no concern. Every located queue named remains governed by `IEC-001`. Where this artifact and a located canonical instrument disagree, **the located instrument governs and this artifact SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `CIOS-09` · PROVISIONAL · ADDITIVE · COMPOSITION-ONLY · AUTHORITY-NEUTRAL**
