# IMPLEMENT-001 · DELIVERABLE 02 — WAVE COMPOSITION AND EXECUTION MODEL

| Field | Value |
|---|---|
| MISSION | `IMPLEMENT-001` — First Production Implementation Mission |
| AUTHORITY | `NONE — DERIVED TRUTH` |
| AUTHORED BY | `IMPLEMENT-001E` — IMPLEMENT-001 Closeout (Phase 2) |
| INPUT | Deliverable 00 (EB-01…EB-09) · Deliverable 01 (dependency classes, critical path, topological order) |
| GOVERNED BY | `EVOLUTION-001` §4 (wave lifecycle, entry/exit criteria) · `RELEASE-001` §1 (change lifecycle) |
| REPOSITORY ANCHOR | the containing commit — owned by version control, never restated here (`UCOS-RFP-001` RFP-2) |
| MEASURED AT | `8aede74` · working tree clean (0 entries) · `verify.sh` GREEN 5/5 |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT (`VAC-01` · `CMG-OQ-02` · `UCCEP-F-004`) |

> This deliverable **models** wave execution. It authorizes no wave, starts no item, allocates no
> identifier, and creates no governance. It is the third of five and was absent from the
> `IMPLEMENT-001` set until `IMPLEMENT-001E`.

---

## 1. WHY THIS DELIVERABLE EXISTS, AND WHAT IT MAY NOT CONTAIN

`IMPLEMENT-001A` Deliverable 00 §3.2 records Deliverable 02 as *"implied by the 00→01 sequence and
by `EB-*` scope/wave modelling"* — with an **empty citation column**. Unlike D03 (cited by D00 line
180) and D04 (cited by all nine items), **no artifact states D02's required content.** Its subject
is therefore derived, and the derivation is constrained from both sides:

| Constraint | Consequence for D02 |
|---|---|
| **Knowledge Once** | D00 already holds every item's capability, source, classification, measured status and dependency verdict. D01 already holds the dependency classes, the graph, the critical path and the topological order. **D02 restates none of it.** |
| `EVOLUTION-001` §4 | Supplies *generic* wave entry/exit criteria for any wave. D02 **binds** them to `EB-01…EB-09` concretely — the generic criteria alone are not checkable against an item. |
| `AC-1` | D02 introduces no backlog item. The item set is exactly D00's nine. |
| `X-9` | D02 does not edit `EVOLUTION-001`, `IMPLEMENT-001C`, or any other programme's output. Where it finds them inconsistent it **resolves and supersedes by statement**, never by edit. |

What is genuinely absent from the repository, and is therefore this deliverable's content:

1. **Which wave is which** — the token `Wave-001` carries four incompatible meanings (§2).
2. **A checkable wave-admission test** per item (§4).
3. **Per-item acceptance conditions** — the exit predicate for each item (§5).
4. **A wave-capacity determination** — whether the composition the repository already states is
   executable as one wave (§6).

---

## 2. THE WAVE-IDENTIFIER COLLISION

Four artifacts use wave numbering. They do not agree. This was undetected until `IMPLEMENT-001E`
because no deliverable owned wave composition.

| # | Reading | Source | `Wave-001` means | `Wave-002` means |
|---|---|---|---|---|
| **R-a** | Roadmap | `EVOLUTION-001` §3 — *"Wave-002 (Next executable)"*, listing `GAP-1`…`GAP-7` + infrastructure | *implicit* — the certified baseline work (68/68), already delivered | the next executable wave, **GAP-keyed** |
| **R-b** | Critical path | `IMPLEMENT-001` D01 §4 — the ASCII bracket `└── WAVE-001 ──┘` | `EB-07` + `EB-01` — a **two-item** wave | *unstated* |
| **R-c** | Release register | `UCOS-EVO-001-W01`, registered by `IMPLEMENT-001D` in `EVOLUTION-001` §6.1 / `RELEASE-001` §3.2 | the remediation + finalization release: 9 commits, 135 files, **0 `EB-*` items** | *reserved, unassigned* |
| **R-d** | Successor plan | `IMPLEMENT-001C` D08 §3 — *"THEN — `WAVE-002`"* | *unstated* | all **8** orderable `EB-*` items, **EB-keyed** |

**The conflict is material, not cosmetic.** Under **R-b** an item could claim Wave-001 membership;
under **R-c** Wave-001 is closed and contains no item at all. `EVOLUTION-001` §4 attaches entry and
exit criteria *per wave*, so an item whose wave is ambiguous has no determinable entry gate.

### 2.1 Resolution — by authority rank, not by preference

| Step | Determination | Basis |
|---|---|---|
| 1 | **`EVOLUTION-001` is the wave authority.** §4 is titled *Wave Execution Governance* and is the only instrument defining the wave lifecycle and its entry/exit criteria. `IMPLEMENT-001` D01 is a dependency graph; it has no wave-naming remit. | `EVOLUTION-001` §4 |
| 2 | **`EVOLUTION-001` §3 reserved the next-executable slot as `Wave-002` before any `EB-*` identifier existed.** D00's `EB-*` numbering post-dates it. A later document cannot renumber an earlier authority's wave by drawing a bracket. | `EVOLUTION-001` §3 vs D00 |
| 3 | **`UCOS-EVO-001-W01` is registered and published.** `EVOLUTION-001` §6.1 and `RELEASE-001` §3.2 bind `W01` to commit range `91a8b1d…ac44985`, lifecycle state `RELEASED`. Under `EVOLUTION-001` principle 1 (*the baseline is immutable*) and principle 4 (*append-only; predecessors preserved*), a registered version identifier is not reassignable. | `EVOLUTION-001` §6.1 |
| 4 | **Therefore `Wave-001` ≡ `UCOS-EVO-001-W01`** — the remediation and finalization wave. It contains **0** `EB-*` items and is **CLOSED**. | R-c prevails |
| 5 | **Therefore `Wave-002` is the first `EB`-executing wave**, and **R-d** states its composition. **R-a** is the same wave under the older GAP keys; §3.1 maps them so the two readings are one. | R-a ≡ R-d |
| 6 | **D01 §4's `WAVE-001` bracket is superseded.** It is a drafting label predating `W01`'s registration, and it conflicts with an authority that already held the slot. Corrected reading: the bracket marks the **evidence-integrity prefix** of Wave-002 — the two items that must precede the other six — not a wave. | this §2.1 |

> **D01 is not edited.** `EVOLUTION-001` principle 4 requires predecessors preserved; the label is
> superseded by this statement, and D01 remains readable as authored. Anyone reading D01 §4 must
> read it with this section.

---

## 3. RESOLVED WAVE REGISTER

| Wave | Version identifier | Composition | `EB-*` items | Lifecycle state | Evidence |
|---|---|---|---|---|---|
| **Wave-001** | `UCOS-EVO-001-W01` | Remediation + finalization: `RG-09-A`, `WP-RO-001`, programme-engine disclosure, authority witness, mission record, evolution record, producer convergence | **0** | **CLOSED / RELEASED** | `EVOLUTION-001` §6.1; 9 commits `91a8b1d…ac44985`; `verify.sh` GREEN |
| **Wave-002** | `UCOS-EVO-001-W02` *(reserved, unissued)* | The 8 orderable executable items | **8** — `EB-07 EB-01 EB-02 EB-04 EB-03 EB-05 EB-08 EB-06` | **PROPOSED** — not entered | `RELEASE-001` §3.2 reserves the identifier; `IMPLEMENT-001C` D08 §3 states the order |
| **Unassigned** | — | `EB-09` | **1** | **NOT ORDERABLE** | `CEP-009` / `ACFV` `AG-03`; D00 `EB-09`, D01 §5 |

**9 items · 8 in Wave-002 · 1 unassignable · 0 in Wave-001.**

Execution order within Wave-002 is **not restated here** — it is D01 §5's topological order, and
`IMPLEMENT-001C` D08 §3 records the identical sequence. D02 fixes *membership and boundaries*; D01
fixes *order*.

### 3.1 GAP-key ↔ EB-key reconciliation

`EVOLUTION-001` §3 and D00 describe the same work under two key systems. This mapping is why
**R-a** and **R-d** are one wave and not two, and it is stated once, here.

| `EVOLUTION-001` §3 item | `EB-*` | Note |
|---|---|---|
| GAP-1 Universal Idea Box | `EB-03` | 1:1 |
| GAP-3 Analysis registry binding | `EB-01` | 1:1 |
| GAP-4 Metering/Billing realization | `EB-02` | 1:1 |
| GAP-6 Digital Twin subject expansion | `EB-05` | 1:1 |
| GAP-7 Operational ecosystem generation | `EB-06` | 1:1. **Title corrected** by D00: MIP Part 43 is *Industry Generation Framework*; no MIP part bears the roadmap's label. |
| GAP-5 Validation evidence extensions | `EB-09` | 1:1 — the unassignable item |
| GAP-2 Constitutional Asset pointer-index | **none** | Excluded by D00 §3 as documentation-only; `CIOA`/`CCE` bindings already satisfy it |
| `UCCEP-F-001` measured phase-3 verdict | `EB-07` | `EVOLUTION-001` §3 lists it under *Enhancements*, not the wave table |
| `UCCEP-F-002` traceability fill | `EB-08` | as above |
| GG-3 Registers 8–11 | `EB-04` | `EVOLUTION-001` §3 lists it under *Infrastructure* |
| GG-4 upstream configuration | **none** | Operator act. **Discharged out-of-band**: the remote is configured and `integration/recovery-001` is published at `8aede74` |
| GG-6 `UCIC-001` ownership | **none** | Governance allocation act, not code (D00 §3) |

**Every `EVOLUTION-001` §3 entry is accounted for: 6 map to Wave-002 items, 1 to the unassignable
item, 4 are excluded with a stated reason, 1 is discharged.** No roadmap entry is silently dropped.

---

## 4. THE WAVE-ADMISSION TEST

`EVOLUTION-001` §4 gives four wave entry criteria. They are stated per *wave*; an item cannot be
checked against them directly. This section binds each to a **measurable predicate**, so admission
is decided by measurement rather than by assertion.

| `EVOLUTION-001` §4 entry criterion | Bound predicate | Where measured | State at `8aede74` |
|---|---|---|---|
| *All items classified* | Every item carries exactly one `EVOLUTION-001` §2 classification | D00 per-item `Classification` row | ✅ **MET** — 9/9 classified; 0 unclassified |
| *Impact analysis complete (no baseline destabilization)* | The 5 `EVOLUTION-001` §5 baseline-protection rules hold, measured, at wave entry | `EVOLUTION-001` §6.1 §5-compliance table | ✅ **MET** at `W01` exit — baseline SHA preserved, `uccep-gate` `blocking=none`, closure `CLOSED` `gaps=0`, `ukb validate` PASS, coverage 94.28% |
| *Dependencies satisfied* | Item has **0** unsatisfied `⇒ SATISFIED-PREREQ` and **0** unsatisfied `⇒ GOVERNANCE-PREREQ` | D01 §2 graph | ✅ **8/9 MET** · ⛔ `EB-09` FAILS (`CEP-009`) |
| *`verify.sh` GREEN at entry* | Exit 0, all stages | live | ✅ **MET** — 5/5, coverage 94.28% |
| **+ Gate-prerequisites** *(not in §4; supplied by D04)* | `B-1` **and** `B-2` both DISCHARGED | D04 | ⛔ **NOT MET** — `B-1` discharged, **`B-2` OPEN** |

> **The admission test is a conjunction.** Four of five conditions hold for eight items. The fifth
> — the gate-prerequisite conjunct that D00 attaches to **every** item as *"Blocking conditions:
> `B-1`, `B-2`"* — does not. **No item is admissible while `B-2` is open.** The determination and
> its single unblocking act are D04's; D02 records only that the admission test is not satisfied
> and therefore **Wave-002 has not entered**.

### 4.1 Why the gate-prerequisite conjunct is part of admission

`EVOLUTION-001` §4's entry list does not mention `B-1`/`B-2`, which could be read as making them
optional. It does not. D01 §2 classifies them as `⇒ GATE-PREREQ`, *"Repository-state condition that
must hold before any item executes"*, with consequence *"blocks the whole wave set"* — and D00
attaches them to all nine items individually. A wave whose every member is blocked cannot satisfy
§4's *"Dependencies satisfied"* however the list is read. The conjunct is therefore **derived, not
added**.

---

## 5. PER-ITEM ACCEPTANCE CONDITIONS

`EVOLUTION-001` §4 wave-exit requires *"All wave items implemented"*. What counts as implemented is
nowhere stated per item. Absent that, an item could be declared done on assertion — the precise
failure mode `IMPLEMENT-001A`/`B`/`C` were each convened to correct.

Each condition below is **derived from the item's own measured-status row in D00**: the acceptance
condition is the negation of the measured defect, expressed as a command or a counted metric. No
condition is invented, and none is a restatement of the item's capability.

| Item | Acceptance condition — ALL clauses required | Derived from (D00 row) |
|---|---|---|
| **EB-07** | `phase3_engine.py --gate` verdict is a **function of measured state**: `repository_status` is no longer the literal at `:546`; the engine's verdict and `make closure-gate` **agree** on one tree; `CK-CLOSURE-P3` ceases to be a standing advisory failure; a negative-path test proves the gate **can** report the other value | *Measured status*: literal at `:546`; the two engines of one programme contradict each other |
| **EB-01** | `UCOS-UAR-001` reachable from an entry point: ≥1 `Makefile` target **and** ≥1 workflow **and** ≥1 test; `grep UAR uccep.json` > 0 (UCCEP membership); **all 5 recorded defects fixed** — `_check_write_scope()` examines something and can fail; `determination`/`gate`/`gate_exit` derived not literal; `F401` cleared; seal computed over emitted bytes; wiring present. Consequence: RIB `VER-09`/`VER-11` and URRC unbound-engine count return to 0 | *Measured status* + *Latent defect found*; `EVOLUTION-001` §6.2 `W01-F-01` |
| **EB-02** | 5 components + 4 registries exist and are exercised; branch coverage ≥ 90%; `D22` Meterable and `D23` Billable discharged; **the disjointness boundary against `platform/measurement/` (`UCOS-UMA-001`) is declared in an artifact**, not assumed; the 22-interface conformance test passes | *Duplication risk to manage*; *Capability* |
| **EB-03** | One append-only, **unclassified-on-entry** store + schema + write path + surface; entry requires **no** `blueprint_ref` and **no** `family`; `engine/registry/**` remains the sole capability-state authority (`AEOS-001` #3) — provable by the Idea Box holding no capability state | *Hard constraint*; the inverse-of-`platform/generation/registry.py` finding |
| **EB-04** | `changes.json` · `knowledge.json` · `regeneration.json` · `rollback.json` present in `00-BOOK/DATA/` with 4 schemas and append-only, forward-only write paths; `change-ledger.json` is **reused as register 8's basis and not mistaken for its discharge**; `REG-01…REG-11` specification numbering is **not** conflated with register numbering | *Precision required*; *Trap to avoid* |
| **EB-05** | The 9 empty dimensions populated; `DIMENSIONS` allowlist extended by **append-only** edit to `base.py:38`; new subjects arrive as **data** (no allowlist edit); `twin.json` remains generated, never hand-edited | *Decisive mechanic*; *Constraint* |
| **EB-08** | Traceability slot fill rises from the measured **348/15,509 (2.24%)** baseline; `complete` > 0; `CK-HEALTH` ceases to be RED **or** its residual cause is named and is not traceability | *Measured status*; D01 §3 `CAUSAL` edge |
| **EB-06** | 4 components + 3 registries; authored as **registry content**, with **no new numbered top-level family** (`ACFV` **R-7**); sector ontologies are **data** in `00-BOOK/DATA/` per `LAW P43-001`; Part 43 readiness moves off **0/3** | *Precedent constraint*; *Measured status* |
| **EB-09** | **No acceptance condition is stated.** Not orderable: a constitutional act (`CEP-009` disposing of `ACFV` `AG-03`) must precede any code. Stating acceptance for an inadmissible item would imply admissibility. | D00 *Blocking conditions*; D01 §5 |

**Standing clauses — applying to every item, in addition to the above.** These are not new
governance; each is an existing standing constraint restated as an exit obligation because
`EVOLUTION-001` §4 wave-exit requires registries, traceability and certification evidence updated.

| Clause | Source |
|---|---|
| `verify.sh` GREEN after the item, not only after the wave | `AC-5` |
| Coverage ≥ 90% maintained | `RELEASE-001` §4 |
| `uccep-gate` `blocking=none` preserved | `EVOLUTION-001` §5 |
| `closure-gate` `CLOSED`, `gaps=0` preserved | `EVOLUTION-001` §5 |
| Registration remains at its fixed point — the item does not reopen `B-2` | D04 `B-2` |
| Additive only: 0 deletions, 0 renames, predecessors preserved | `EVOLUTION-001` principles 2 and 4 |
| Item declares its `EVOLUTION-001` §2 classification before implementation | `RELEASE-001` §1 `CLASSIFIED` |
| No new numbered top-level family without passing the Architecture Admission Test | `ACFV` **R-7** |

---

## 6. WAVE-CAPACITY DETERMINATION

`EVOLUTION-001` §4 makes wave exit **atomic**: *"All wave items implemented"* plus five further
conditions, evaluated once, for the whole wave. Applied to the composition the repository already
states, that has a measurable consequence.

| Measure | Value | Source |
|---|---|---|
| Items in Wave-002 | 8 | §3 |
| Scope spread | **S → XL** (`EB-07` S · `EB-06` XL) | D00 §4 |
| Largest single item | `EB-06`, **XL**, 4 components + 3 registries, Part 43 readiness 0/3 | D00 `EB-06` |
| Largest counted workload | `EB-08`, **15,509** field slots, currently 348 filled | D00 `EB-08`, re-measured 2.24% |
| Hard inter-item dependencies | **0** | D01 §3 — *"not one hard dependency between any two executable backlog items"* |
| Advisory ordering edges | 3 (`EB-01`→later items; `EB-07`→certification claims; `EB-08`→`CK-HEALTH`) | D01 §3 |

**Determination.** With 0 hard inter-item dependencies, an 8-item wave is *technically* coherent —
D01 §3 already established that eight items could in principle execute in parallel. But under an
atomic exit gate it is **operationally unfalsifiable until the last item lands**: `EB-07`'s S-scope
correction cannot be certified as released until `EB-06`'s XL scope completes, and D01 §3's
`CAUSAL` edge means `EB-08`'s cost **grows** with every artifact the other seven create.

`IMPLEMENT-001E` **does not re-split the wave.** Two existing authorities (`EVOLUTION-001` §3 as
`R-a`, `IMPLEMENT-001C` D08 §3 as `R-d`) state an 8-item composition; overriding both would be a
re-plan, and this mission's mandate is closeout, not re-planning. What D02 records instead:

> **Composition is 8 items as already stated. The atomicity of `EVOLUTION-001` §4's exit gate is
> disclosed as a capacity risk, not resolved.** If the operator prefers incremental release, the
> instrument to change is `EVOLUTION-001` §4 — a governance act with its own route — not this
> deliverable. The **evidence-integrity prefix** (`EB-07` then `EB-01`, the pair D01 §4 bracketed)
> should complete before the remaining six begin regardless of how the wave is finally cut, because
> those two are what make later certification claims worth anything: one makes a gate able to fail,
> the other makes a registry able to report.

---

## 7. WHAT THIS DELIVERABLE DOES NOT DO

| Not done | Why |
|---|---|
| Authorize Wave-002 entry | The admission test in §4 is **not satisfied** — `B-2` is open (D04) |
| Start, schedule or estimate any item | D02 models composition; execution is a Wave-002 act |
| Restate item detail or execution order | D00 and D01 §5 hold them — Knowledge Once |
| Edit `EVOLUTION-001`, `IMPLEMENT-001C` D08, or D01 | `X-9`; append-only. §2.1 supersedes by statement |
| Re-split the wave | Would override two standing authorities; outside a closeout mandate (§6) |
| Register any artifact or allocate any identifier | `00-MASTER/` is excluded from registration (D04 §2.3); 0 identifiers allocated |
| Assign `EB-09` to a wave | Not orderable; assigning it would imply admissibility |

---

## 8. DETERMINATION

> ### ✅ **WAVE COMPOSITION IS DETERMINED. WAVE-002 HAS NOT ENTERED.**
>
> The four-way `Wave-001` collision is **resolved by authority rank**: `Wave-001` ≡
> `UCOS-EVO-001-W01`, remediation, **0 `EB-*` items, CLOSED**. `Wave-002` is the first
> `EB`-executing wave, composition **8 items**, state **PROPOSED**. `EB-09` is unassignable.
> D01 §4's `WAVE-001` bracket is superseded and re-read as the evidence-integrity prefix.
>
> All 12 `EVOLUTION-001` §3 roadmap entries are reconciled to `EB-*` keys or excluded with a stated
> reason — **0 silently dropped**.
>
> The wave-admission test is bound to five measurable predicates. **Four hold. The fifth does
> not:** `B-2` Registration Fixed Point is **OPEN**, and D00 attaches it to every one of the nine
> items. **Wave-002 is therefore INADMISSIBLE at `8aede74`**, on the repository's own measurement
> rather than on judgement.
>
> Acceptance conditions are stated for 8 items — each derived from that item's own measured defect,
> none invented — plus 8 standing clauses. `EB-09` deliberately has none.

---

*END — `IMPLEMENT-001` Deliverable 02 · AUTHORITY = NONE · `CERTIFIED-PROVISIONAL` · Tier T1 VACANT*
