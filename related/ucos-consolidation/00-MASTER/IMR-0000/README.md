# IMR-0000 — CIOS PLATFORM FOUNDATION · MISSION INDEX

| Field | Value |
|---|---|
| MISSION | `IMR-0000` — CIOS Platform Foundation · Universal Programme Management Foundation |
| WORK PACKAGE | `WP-IMR-0000` |
| SUBJECT TOKEN | **`CIOS`** — reused, not re-allocated (`NS-1`) |
| MISSION MODE | **DESIGN ONLY** — no implementation, no runtime, no execution engine, no code, no repository refactor |
| BASELINE | `b26c5bb66c37717fe4eb96552bad4b9d8b74d890` · branch `programme/evo-usis-005` |
| AUTHORITY | **NONE of its own.** Composition-and-specification instrument. Every mechanism is a pointer to a located owner. |
| STANDING | **PROVISIONAL** (`CMG-L-12`) · Tier T1 **VACANT** (`VAC-01`) · **not** validated · **not** certified active · **not** ratified · **not** frozen and **not freezable** |
| ARCHITECTURAL INPUTS | `IMR-003A` + `IMR-003A-R1` — consumed **read-only and unmodified** |
| TERMINAL ACT | **Architecture Stability Contract v1.0** (`22`) + declaration (`25` §9) — **NOT** a `CEP-007` freeze |

> **What `IMR-0000` is.** The platform shape that `IMR-003A` did not supply: a subsystem decomposition of the existing 24 CIOS engines, an object model that reaches objects other than submissions, a registry admissibility test, a lifecycle axis reconciliation, and a 20-entry catalogue telling any future programme exactly which surface to bind. One new architectural layer, and it owns nothing.
>
> **What `IMR-0000` is not.** It is not an authority, not a successor to CIOS, not a peer of CIOS, and not a second platform. It creates no registry, no engine, no port, no state, no graph, no namespace and no identifier. It discharges no gate. Where it and a located canonical instrument conflict, **the located instrument governs and `IMR-0000` SHALL be corrected**; where it and `IMR-003A` conflict, **`IMR-003A` governs**.

---

## Mission history

| Event | Record |
|---|---|
| Registered · 30 deliverables declared · constraints and divergences stated **before** authoring | `00-MISSION-REGISTRATION-RECORD.md` |
| **Context Assimilation Directive** received mid-mission, after `00` and before any architecture artifact | `00A` — gate passed; **0 artifacts regenerated, 0 restarted, 0 discarded**; 6 further capabilities seated additively |
| Architecture authored | `01 … 21` |
| Stability, gaps, readiness, completion | `22 … 25` |

---

## Artifact index

| # | Artifact | Subject | Deliverable |
|---|---|---|---|
| — | [`00-MISSION-REGISTRATION-RECORD.md`](00-MISSION-REGISTRATION-RECORD.md) | registration · `MC-01…10` · mission-local families · `AC-1…14` · disclosed divergences `D-1…D-7` | — |
| — | [`00A-CONTEXT-ASSIMILATION-AND-COVERAGE-DETERMINATION.md`](00A-CONTEXT-ASSIMILATION-AND-COVERAGE-DETERMINATION.md) | the Context Assimilation Gate · **the 9 directive outputs** · coverage matrix (30) · gap matrix (11) · reuse matrix (20) · **authoritative deliverable→artifact map** | — |
| 1 | [`01-CIOS-PLATFORM-MODEL.md`](01-CIOS-PLATFORM-MODEL.md) | 5 layers · `PL-R1…R10` · *"Engineering Management Platform"* vocabulary resolution | **D1** |
| 2 | [`02-CIOS-SUBSYSTEM-ARCHITECTURE.md`](02-CIOS-SUBSYSTEM-ARCHITECTURE.md) | **17 subsystems** `SS-01…SS-17` · 10 fields each · engine partition (24/24, disjoint, exhaustive) · 0 duplicate responsibilities | — |
| 3 | [`03-UNIVERSAL-OBJECT-MODEL.md`](03-UNIVERSAL-OBJECT-MODEL.md) | **20 attributes** `UOM-A-01…A-20` · `UOM-R-1…R-9` · reduction proof to `CIOS-ID-01…22` | **D2** |
| 4 | [`04-UNIVERSAL-UNIQUENESS-PRINCIPLE-FRAMEWORK.md`](04-UNIVERSAL-UNIQUENESS-PRINCIPLE-FRAMEWORK.md) | `UUP-01…UUP-09` · closure claim · conformance test · measured state | **D4** |
| 5 | [`05-CIOS-IDENTITY-FRAMEWORK.md`](05-CIOS-IDENTITY-FRAMEWORK.md) | 5 identity planes · `IDF-1…8` · identity source per object kind · **mints nothing** | **D5** |
| 6 | [`06-CIOS-NAMESPACE-FRAMEWORK.md`](06-CIOS-NAMESPACE-FRAMEWORK.md) | 3 namespace tiers · `NF-1…6` · **the third token refusal** · collision check | **D6** |
| 7 | [`07-CANONICAL-REGISTRY-FRAMEWORK.md`](07-CANONICAL-REGISTRY-FRAMEWORK.md) | `RF-1…8` admissibility test · **`REG-01…REG-11`** · `RR-1…RR-6` register relationships | **D3, D7–D17** |
| 8 | [`08-LIFECYCLE-FRAMEWORK.md`](08-LIFECYCLE-FRAMEWORK.md) | **4 axes** `LX-1…LX-4` · `LR-1…7` · 5 located models reconciled · **0 new states** | **D18** |
| 9 | [`09-DEPENDENCY-GRAPH-ARCHITECTURE.md`](09-DEPENDENCY-GRAPH-ARCHITECTURE.md) | `DG-1…6` · 5 dependency scopes · what acyclicity is and is not proven | **D19** |
| 10 | [`10-PLANNING-ARCHITECTURE.md`](10-PLANNING-ARCHITECTURE.md) | `PA-1…6` · epoch model · the no-lock proof · degradation semantics | **D20** |
| 11 | [`11-SCHEDULING-ARCHITECTURE.md`](11-SCHEDULING-ARCHITECTURE.md) | `SA-1…6` · locked ranks 1–3 and 8 · 4 independent clocks · the queue boundary | **D21** |
| 12 | [`12-ORCHESTRATION-ARCHITECTURE.md`](12-ORCHESTRATION-ARCHITECTURE.md) | `OA-1…6` · handoff and relinquishment · default-deny + narrow-allow | **D22** |
| 13 | [`13-CHECKPOINT-FRAMEWORK.md`](13-CHECKPOINT-FRAMEWORK.md) | `CF-1…8` · CP-S session record vs CP-A adoption instant | **D23** |
| 14 | [`14-RECOVERY-FRAMEWORK.md`](14-RECOVERY-FRAMEWORK.md) | `RV-1…RV-5` classes · `RF-R1…R7` · forward-only · 5 unavailable capabilities | **D24** |
| 15 | [`15-GOVERNANCE-FRAMEWORK.md`](15-GOVERNANCE-FRAMEWORK.md) | 8 tiers · 16-row binding map · disposition obligation · **how the platform is itself governed** | **D25** |
| 16 | [`16-KNOWLEDGE-GRAPH-FRAMEWORK.md`](16-KNOWLEDGE-GRAPH-FRAMEWORK.md) | `KG-1…8` · Knowledge Once at admission · measured closure (434 / 0) | **D26** |
| 17 | [`17-DIGITAL-TWIN-FRAMEWORK.md`](17-DIGITAL-TWIN-FRAMEWORK.md) | `DT-1…6` · derived, not persistence · 5 conflations prevented | **D27** |
| 18 | [`18-INTELLIGENCE-FRAMEWORKS.md`](18-INTELLIGENCE-FRAMEWORKS.md) | `IP-1…6` discipline · Engineering (`SS-13`) · Governance (`SS-14`) · Evolution (`SS-17`) | — |
| 19 | [`19-PUBLIC-INTERFACE-CATALOGUE.md`](19-PUBLIC-INTERFACE-CATALOGUE.md) | **`IF-01…IF-08`** (8 ports) + **`IFL-01…IFL-12`** (direct bindings) = **20-entry surface** | **D29** |
| 20 | [`20-VALIDATION-AND-CERTIFICATION-FRAMEWORK.md`](20-VALIDATION-AND-CERTIFICATION-FRAMEWORK.md) | 3 validation surfaces · `VF-1…5` · `CF-C1…C6` · **`PCK-01…PCK-12`** self-checks | — |
| 21 | [`21-TRACEABILITY-FRAMEWORK-AND-MATRIX.md`](21-TRACEABILITY-FRAMEWORK-AND-MATRIX.md) | `TF-1…7` · 4 traceability scopes · **`TM-01…TM-37`** | **D30** |
| 22 | [`22-ARCHITECTURE-STABILITY-CONTRACT.md`](22-ARCHITECTURE-STABILITY-CONTRACT.md) | **`ASC-01…ASC-10`** v1.0 · what may be relied on · why this is not a freeze | **D28** |
| 23 | [`23-GAP-ANALYSIS-AND-PLATFORM-GATES.md`](23-GAP-ANALYSIS-AND-PLATFORM-GATES.md) | `PGAP-01…11` dispositions · **`PG-01…PG-09`** · **`PF-01…PF-07`** | — |
| 24 | [`24-PLATFORM-IMPLEMENTATION-READINESS.md`](24-PLATFORM-IMPLEMENTATION-READINESS.md) | readiness by dimension · what a downstream mission can and cannot do today | — |
| 25 | [`25-MISSION-COMPLETION-AND-ARCHITECTURE-FREEZE.md`](25-MISSION-COMPLETION-AND-ARCHITECTURE-FREEZE.md) | completion report · **Architecture Freeze Declaration** · recommendation for `IMR-0001` | — |
| — | [`imr-0000-platform-bindings.json`](imr-0000-platform-bindings.json) | machine-readable projection — **DATA ONLY, AUTHORITY NONE** | — |
| — | `README.md` | this index | — |

---

## Reading order

| If you want to | Read |
|---|---|
| **implement against the platform** | **`19`** (the 20-entry surface), then `02`, `07`, `08` |
| understand why the platform exists and what it owns | `01` §1–§2, then `02` §1 |
| know what every canonical object must carry | `03` |
| check your own conformance to uniqueness | `04` §4 |
| register a programme or a mission correctly | `07` `REG-01`, `REG-02` — and note the `IMR-003A` termination precedent |
| know which lifecycle model answers your question | `08` §2–§3 |
| know what is **absent** rather than merely undiscovered | `23` |
| know what may change and by what route | `22` |
| know what is ready and what is blocked | `24`, then `25` §8–§9 |
| know what the mid-mission directive changed | `00A` Outputs 4 and 6 |

---

## The numbers

| Element | Count | Element | Count |
|---|---|---|---|
| Platform layers | 5 (1 new) | Registry specifications `REG-*` | 11 |
| Subsystems `SS-*` | 17 | Register relationship types `RR-*` | 6 |
| — engine-bearing | 12 | Lifecycle axes `LX-*` | 4 |
| — binding-only | 5 | Interface catalogue entries | 20 |
| Engines (consumed, **0 created**) | 24 | Self-checks `PCK-*` | 12 |
| Ports (consumed, **0 created**) | 48 (8 public) | Traceability rows `TM-*` | 37 |
| Object attributes `UOM-A-*` | 20 | Stability clauses `ASC-*` | 10 |
| Uniqueness clauses `UUP-*` | 9 | Platform gates `PG-*` (all OPEN) | 9 |
| Registry framework rules `RF-*` | 8 | Findings `PF-*` | 7 |

---

## Standing limits — read before relying on anything here

| Limit | Basis |
|---|---|
| Every determination is **PROVISIONAL** | `CMG-L-12`; Tier T1 VACANT (`VAC-01`, `UCCEP-F-004`) |
| **Not validated** under `CEP-004` — a self-check is not a validation | `CIOS-15` `VR-04`; `20` §1 |
| **Not certified** active under `CEP-005`; ceiling `CERTIFIED-PROVISIONAL` | `CIOS-16` §1; `20` §2 |
| **Not ratified** under `CEP-006`; no competent authority exists | `VAC-01`; `CIOS-G-03` |
| **Not frozen** under `CEP-007`, and **cannot be** — an attempt would be **void** | `CEP-007` II.4/IV.4; `GD-10`; `CIOS-GAP-13`; `22` §1 |
| The `22` stability contract is **declaration-scoped**, not a constitutional freeze | `22`; `25` §9.2 |
| **No governing supremacy** over any programme — composition and reference only | `PG-08` ← `CIOS-G-01`; `PG-07` ← `CIOS-G-02` |
| **No corpus traceability closure** claimed | `UCCEP-F-002` (1198 artifacts); `21` §1 |
| **No registry created**; 2 specifications describe registers that **do not exist** | `07` §5; `PGAP-02`, `PGAP-03` |
| **No machine verifier** — self-checks were evaluated by inspection | `MC-05`; `PF-06` |
| Mission home is **untracked** at `b26c5bb`; the registration claim is unwitnessed by any commit | `PF-03`; `PG-09` |
| **No gate and no finding discharged** — CIOS's or inherited | `23` §2–§3 |
| **No execution authorized**; execution remains blocked by `GG-3`, `GG-4`, `GG-6`, `IAC-001 B+C` | `24` §4 |
| Attribute count is **20**, not the 19 the instruction implies | `PF-01`; `03` §4.1 |
| `IEC-001` / `IMG-001` resolve to **content**, not to files bearing those names | `PF-07`; `20` `PCK-06` |

---

**`IMR-0000` owns no mechanism, no registry, no gate, no identifier space and no concern. Every authority it names is located in an instrument that exists independently at `b26c5bb`. `IMR-003A` and `IMR-003A-R1` are unmodified. Deleting this mission home restores `b26c5bb` exactly. This mission confers no authority on itself and authorizes no execution.**
