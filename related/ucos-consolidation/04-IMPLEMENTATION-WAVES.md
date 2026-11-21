# 04 — IMPLEMENTATION WAVES

> **Mission:** IMG-001 · **Baseline:** `ab78f35` · **Branch:** governance-reconciliation · **Date:** 2026-07-23
> **Mode:** READ-ONLY. No implementation, no commits, no tags, no push.
> **Authority:** Repository Truth is sole implementation authority. Wave partition is **derived** from the repository's family→constitutional-class→wave model (`phase3_engine.py` layer model), applied to the 90 SPECIFIED CKOs at `ab78f35`. No manual ordering is introduced.

---

## 1. Partition rule

Every unrealized CKO is assigned to **exactly one** deterministic execution wave by its `family`:

| Wave | Constitutional class | Families |
|---|---|---|
| Wave-01 | Constitution | LAW |
| Wave-02 | Architecture | ARCH |
| Wave-03 | Governance / Registry / Roadmap / Knowledge | GOV, UCOS-GOV, UCOS-RECON, UCOS-RAT, PHASE, EPIC, MCP, MEP, MCS, UCOS-EXEC, UCOS-COMP, UCKO, UKDA-DEC |
| Wave-04 | Capability / Platform / Gate | PLATFORM, EC3-GATE |
| Wave-05 | Realization | DATA, SERVICE, APPLICATION, INFRASTRUCTURE, RUNTIME |

**Wave invariants (all satisfied):** (i) no dependency violation — a wave depends only on strictly lower waves; (ii) maximum safe parallelism — no intra-wave edges, so all members of a wave run in parallel; (iii) deterministic — assignment is a pure function of `family`.

---

## 2. Wave partition (counts)

| Wave | Total | READY | BLOCKED | GENERATED | NOT REQUIRED |
|---|---|---|---|---|---|
| Wave-01 | 20 | 20 | 0 | 0 | 0 |
| Wave-02 | 15 | 0 | 10 | 4 | 1 |
| Wave-03 | 32 | 0 | 25 | 0 | 7 |
| Wave-04 | 11 | 0 | 10 | 0 | 1 |
| Wave-05 | 12 | 0 | 0 | 8 | 4 |
| **Total** | **90** | **20** | **45** | **12** | **13** |

Effective implementable per wave (excluding NOT REQUIRED sentinels): W1 20 · W2 14 · W3 25 · W4 10 · W5 8 = **77**.

---

## 3. Wave contents

### Wave-01 — Constitution · 20 (all READY, implementation roots)
`Ω∞-001, Ω∞-002, Ω∞-003, Ω∞-004, Ω∞-005, Ω∞-006, Ω∞-007, Ω∞-008, Ω∞-009, Ω∞-010, Ω∞-011, Ω∞-012, Ω∞-013, Ω∞-014, Ω∞-015, Ω∞-016, Ω∞-017, Ω∞-018, Ω∞-019, Ω∞-020`

### Wave-02 — Architecture · 15
- **GENERATED (4):** `ARCH-API-001, ARCH-EVENT-001, ARCH-RUNTIME-001, ARCH-WORKFLOW-001`
- **BLOCKED (10):** `ARCH-AI-001, ARCH-BCDR-001, ARCH-CERT-001, ARCH-GAP-001, ARCH-INFRA-001, ARCH-INTEGRATION-001, ARCH-MASTER-001, ARCH-OBS-001, ARCH-QUALITY-001, ARCH-TEST-001`
- **NOT REQUIRED (1):** `ARCH-XXX-000`

### Wave-03 — Governance / Registry / Roadmap / Knowledge · 32
- **BLOCKED (25):** `GOV-007, GOV-008, GOV-009, GOV-010, MCP-000, MCS-000, MEP-06, MEP-08, Phase-001, Phase-002, Phase-003, Phase-020, Phase-024, Phase-025, UCOS-COMP-001000, UCOS-COMP-001010, UCOS-COMP-009010, UCOS-GOV-001, UCOS-GOV-003, UCOS-GOV-005, UCOS-RAT-001, UCOS-RECON-0000, UCOS-RECON-0001, UCOS-RECON-001, UCOS-RECON-C1`
- **NOT REQUIRED (7):** `EPIC-XXX-000, MEP-00, UCKO-XXX-000, UCOS-EXEC-000, UCOS-GOV-000, UCOS-RAT-000, UKDA-DEC-000`

### Wave-04 — Capability / Platform / Gate · 11
- **BLOCKED (10):** `EC-3-AP-1, PLATFORM-003, PLATFORM-004, PLATFORM-007, PLATFORM-013, PLATFORM-014, PLATFORM-015, PLATFORM-016, PLATFORM-017, PLATFORM-018`
- **NOT REQUIRED (1):** `PLATFORM-000`

### Wave-05 — Realization · 12 (leaves)
- **GENERATED (8):** `APPLICATION-015, APPLICATION-017, APPLICATION-019, APPLICATION-020, DATA-027, INFRASTRUCTURE-004, RUNTIME-000, RUNTIME-020`
- **NOT REQUIRED (4):** `APPLICATION-000, DATA-000, INFRASTRUCTURE-000, SERVICE-000`

---

## 4. Wave gating

```
Wave-01 ─gate─▶ Wave-02 ─gate─▶ Wave-03 ─gate─▶ Wave-04 ─gate─▶ Wave-05
 (READY)        (start after   (start after    (start after    (start after
                 W1 complete)   W2 complete)    W3 complete)    W4 complete)
```

- **Executable now:** only Wave-01 (20 READY roots). All higher waves are BLOCKED strictly on the immediately-lower wave.
- **Sentinels (13 NOT REQUIRED)** are excluded from execution in every wave; they do not gate anything.
- **GENERATED objects** (Wave-02 generative roots + Wave-05 realization span) are produced by the engine/factory pipeline once their wave opens; note the realizers `event.py`, `workflow.py`, `runtime.py` are currently **absent** from `engine/factory/factories/` (Repository Truth) and must exist for the Wave-02/Wave-05 generation step to run.

---

## 5. Determinism & safety attestation

| Property | Status |
|---|---|
| Every object in exactly one wave | ✔ (sum = 90) |
| No dependency violation across waves | ✔ (strict layer order) |
| Maximum safe parallelism within wave | ✔ (no intra-wave edges) |
| Reproducible from `closure.json` | ✔ (pure function of `family`) |

---
*End of 04-IMPLEMENTATION-WAVES.md*



---

## 6 — ASSIMILATION SEQUENCING REFINEMENT (REP-002 · WAVE-1 · B7 / AAD-016)

> **Provenance.** REP-002 Wave-1 · Backlog **B7** (Decision **AAD-016**, *Implementation Sequence Refinement*) · Disposition **EXTEND** · Canonical owner **IMG-001** (this artifact). Authorities: REP-001, AAP-001. **Additive**: this refinement **does not alter** the wave partition in §1–§5 (which remains authoritative); it prepends a deterministic **Assimilation Pre-Wave (W0-A)** that gates the reuse-first EXTEND backlog ahead of the constitutional Wave-01 roots.

### 6.1 — Assimilation Pre-Wave (W0-A) — deterministic, reuse-first, additive-only

| Order | Backlog | Decision | Owner (reuse) | Action | Depends on |
|---|---|---|---|---|---|
| W0-A.1 | B3 | AAD-001 Meta-Platform | PLATFORM-005 | EXTEND | METACLASS, PLATFORM-001 |
| W0-A.2 | B4 | AAD-002 Platform Builder | PLATFORM-010 + APPLICATION-FACTORY | EXTEND | PLATFORM-010 |
| W0-A.3 | B6 | AAD-014 Declarative Composition | PLATFORM-010 + UNIVERSAL-COMPILER | EXTEND | PLATFORM-010 |
| W0-A.4 | B5 | AAD-010 Constitutional Reuse Gate | Context Assimilation Gate | EXTEND | Context Assimilation Gate |
| W0-A.5 | B7 | AAD-016 Sequence Refinement | IMG-001 · IEC-001 · IMP-000 | EXTEND | — |

**Excluded (by mission):** AAD-003/005 (Nucleus — pending constitutional determination) and AAD-018 (Execution Spine — separate program). These are **not** sequenced here.

### 6.2 — Gating

`W0-A (assimilation EXTENDs) ─gate─▶ Wave-01 (LAW roots) ─gate─▶ … ─gate─▶ Wave-05`. W0-A is additive-only (EXTEND of existing owners; zero new artifacts) and therefore introduces no dependency into the realization waves; §4 gating is unchanged. Determinism preserved: W0-A order is a pure function of backlog id.

**§6 — ASSIMILATION SEQUENCING REFINEMENT — EXTEND COMPLETE · ADDITIVE · WAVE PARTITION UNCHANGED.**
