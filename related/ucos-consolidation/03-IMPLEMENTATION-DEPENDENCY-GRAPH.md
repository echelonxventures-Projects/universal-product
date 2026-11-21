# 03 — IMPLEMENTATION DEPENDENCY GRAPH

> **Mission:** IMG-001 · **Baseline:** `ab78f35` · **Branch:** governance-reconciliation · **Date:** 2026-07-23
> **Mode:** READ-ONLY. No implementation, no commits, no tags, no push.
> **Authority:** Repository Truth is sole implementation authority. The dependency structure is **derived** from the repository's own constitutional layer-gate model; per-object edges are not carried in `closure.json` and are not invented — dependency is expressed at the constitutional-layer granularity (flagged where relevant).

---

## 1. Dependency model

`closure.json` at `ab78f35` does **not** carry explicit concept→concept edges. The only ordering model in Repository Truth is the constitutional **layer-gate** model (predecessor class + wave) used by `phase3_engine.py` in `38-DEPENDENCY-REGISTER.md`. Under that model, dependency is a **strict partial order over constitutional layers**:

```
Constitution (W1)  ◁  Architecture (W2)  ◁  Governance/Registry/Roadmap (W3)  ◁  Capability/Platform (W4)  ◁  Realization (W5)
```

An object in layer *N* depends on the completion of all objects in layers *< N*. There are **no intra-layer edges** (objects within a wave are mutually independent). This yields an acyclic graph by construction.

---

## 2. Node classification

| Node role | Definition | Members |
|---|---|---|
| **Implementation roots** | nodes with no predecessor layer | **Wave-01 LAW** — 20 objects (Ω∞-001 … Ω∞-020) |
| **Intermediate nodes** | nodes with both predecessors and dependents | **Wave-02, Wave-03, Wave-04** — 15 + 32 + 11 = 58 objects |
| **Leaf nodes** | nodes with no dependents (nothing depends on them) | **Wave-05 realization span** — 12 objects |

**Sentinels (NOT REQUIRED, 13):** family-catalog identifier registrations. They are graph-present (homed) but carry no implementable artifact; they are **isolated nodes** (no in/out implementation edges) and are excluded from the executable graph.

---

## 3. Layer-gate edge set

| Predecessor layer | Dependent layer | Edge semantics |
|---|---|---|
| W1 Constitution | W2 Architecture | architecture presupposes constitution |
| W2 Architecture | W3 Governance/Registry/Roadmap | governance presupposes architecture |
| W3 Governance/… | W4 Capability/Platform | platform presupposes governance |
| W4 Capability/Platform | W5 Realization | realization presupposes platform/capability |

Effective (non-sentinel) implementable node counts per layer: W1 20 · W2 14 · W3 25 · W4 10 · W5 8 → **77 implementable**, plus **13 sentinels (NOT REQUIRED)** = 90.

---

## 4. Graph diagram (layer granularity)

```
        [W1] Constitution — 20 ROOTS (READY)
              Ω∞-001 … Ω∞-020
                     │  (gate)
        [W2] Architecture — 14 impl (4 GENERATED, 10 BLOCKED)
              ARCH-API/EVENT/WORKFLOW/RUNTIME-001 (GENERATED)
              ARCH-AI/BCDR/CERT/GAP/INFRA/INTEGRATION/MASTER/OBS/QUALITY/TEST-001 (BLOCKED)
                     │  (gate)
        [W3] Governance/Registry/Roadmap/Knowledge — 25 impl (BLOCKED)
              GOV-007..010, UCOS-GOV-001/003/005, UCOS-RECON-*, UCOS-RAT-001,
              PHASE-*, MCP-000, MEP-06/08, MCS-000, UCOS-COMP-*
                     │  (gate)
        [W4] Capability/Platform/Gate — 10 impl (BLOCKED)
              PLATFORM-003/004/007/013/014/015/016/017/018, EC-3-AP-1
                     │  (gate)
        [W5] Realization — 8 LEAVES (GENERATED)
              APPLICATION-015/017/019/020, DATA-027, INFRASTRUCTURE-004,
              RUNTIME-000/020
```

---

## 5. Quality checks (mission-mandated)

| Check | Result | Evidence |
|---|---|---|
| No duplicate implementation ownership | **PASS** | `duplicate_canonical_homes = 0`; each of the 90 has exactly one canonical home (`files[0]`) |
| No orphan implementation | **PASS** | `orphan_concepts = 0`; every object `homed = true` |
| No cyclic implementation dependency | **PASS** | layer-gate is a strict partial order over 5 layers → acyclic by construction; no object depends on a later-or-equal layer |
| No unresolved prerequisite | **PASS (within scope)** | every dependent layer's prerequisite is a defined lower layer; W1 has no prerequisite. **ASSUMPTION:** no hidden cross-layer prerequisite exists beyond the family taxonomy — supported by `gap_total = 0` |
| No unresolved destination | **PASS** | every object has a resolved canonical home (`files[0]` non-empty) |
| No unresolved validation owner | **PASS** | validation harness `verify.sh` present; per-type validation owner assigned via family template (`02` §5) |
| No unresolved certification owner | **PASS (in-corpus)** | EC-3 gate is the in-corpus certification owner for all types; **exception:** UCOS-RAT absolute finality is externally owned (DR-RAT-11) — recorded, not a defect |

---

## 6. Reverse-dependency summary

| Layer | Depends on | Depended on by (reverse) |
|---|---|---|
| W1 Constitution | — | W2, W3, W4, W5 (all 70 higher objects) |
| W2 Architecture | W1 | W3, W4, W5 |
| W3 Governance/… | W1, W2 | W4, W5 |
| W4 Capability/Platform | W1, W2, W3 | W5 |
| W5 Realization | W1, W2, W3, W4 | — (leaves) |

---

## 7. Determinism statement

The graph is fully determined by (a) each object's `family` (Repository Truth) and (b) the fixed family→layer map. No manual ordering is introduced. Re-running the same rule on the same `closure.json` reproduces this graph exactly.

---
*End of 03-IMPLEMENTATION-DEPENDENCY-GRAPH.md*
