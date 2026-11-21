# 09 — REPOSITORY-WIDE IMPLEMENTATION BACKLOG

> **Mission:** IMG-001 · **Baseline:** `ab78f35` · **Branch:** governance-reconciliation · **Date:** 2026-07-23
> **Mode:** READ-ONLY. No implementation, no commits, no tags, no push.
> **Authority:** Repository Truth is sole implementation authority. This backlog is the **canonical execution input** for all future implementation programs. It is derived entirely from `closure.json` @ `ab78f35` and the deterministic model in `02`–`08`.

---

## 1. Backlog scope

The backlog contains the **77 executable** unrealized CKOs (READY + BLOCKED + GENERATED). The 13 NOT REQUIRED family sentinels are recorded as **closed / no-action** (§5). Knowledge Once holds: each item appears exactly once.

| Segment | Count |
|---|---|
| Executable backlog items | 77 |
| Closed (NOT REQUIRED sentinels) | 13 |
| **Total tracked** | **90** |

---

## 2. Backlog ordering

Backlog priority = topological order (`05`): Wave-01 → Wave-05, then (family, id). The **actionable frontier** (executable now) is the 20 Wave-01 READY items; the remainder are queued behind their layer gate.

---

## 3. Backlog by wave (execution buckets)

### BL-W1 · Constitution · 20 items · **ACTIONABLE NOW (READY)**
Codify constitutional articles `Ω∞-001 … Ω∞-020` into the constitution corpus.
- Completion signal: each `SPECIFIED → IMPLEMENTED`, `in_code = true`.
- Unblocks: all of Waves 2–5.

### BL-W2 · Architecture · 14 items · queued behind BL-W1
- **Generate (4):** `ARCH-API-001, ARCH-EVENT-001, ARCH-WORKFLOW-001, ARCH-RUNTIME-001` — requires factory realizers; `event.py`/`workflow.py`/`runtime.py` **absent** (must be present to generate).
- **Author (10):** `ARCH-AI-001, ARCH-BCDR-001, ARCH-CERT-001, ARCH-GAP-001, ARCH-INFRA-001, ARCH-INTEGRATION-001, ARCH-MASTER-001, ARCH-OBS-001, ARCH-QUALITY-001, ARCH-TEST-001`.

### BL-W3 · Governance / Registry / Roadmap / Knowledge · 25 items · queued behind BL-W2
`GOV-007/008/009/010`; `UCOS-GOV-001/003/005`; `UCOS-RECON-0000/0001/001/C1`; `UCOS-RAT-001` (finality externally gated — DR-RAT-11); `Phase-001/002/003/020/024/025`; `MCP-000`; `MEP-06/08`; `MCS-000`; `UCOS-COMP-001000/001010/009010`.

### BL-W4 · Capability / Platform / Gate · 10 items · queued behind BL-W3
`EC-3-AP-1`; `PLATFORM-003/004/007/013/014/015/016/017/018`.

### BL-W5 · Realization · 8 items · queued behind BL-W4 · **GENERATED (factory)**
`APPLICATION-015/017/019/020` (application.py); `DATA-027` (data.py); `INFRASTRUCTURE-004`; `RUNTIME-000/020` (runtime.py absent).

---

## 4. Backlog item schema (per executable item)

Each backlog item inherits, from the manifest (`02`) and matrix (`08`):

| Field | Source |
|---|---|
| Canonical ID / Type | `closure.json` id / family |
| Destination (home) | `closure.json.files[0]` |
| Target package | family→package map (`02` §3) |
| Wave / priority | `04` / `05` |
| Readiness | `08` |
| Required artifacts/registries/schemas/runtime/validation/certification/traceability/evidence | family-type template (`02` §5) |
| Completion / validation / certification criteria | `02` §6 |

Rather than duplicate 77 rows, the backlog references the single-source tables in `01`, `02`, `05`, `08` (Knowledge Once — no field is re-authored here).

---

## 5. Closed backlog items (NOT REQUIRED, no action) · 13
`APPLICATION-000, ARCH-XXX-000, DATA-000, EPIC-XXX-000, INFRASTRUCTURE-000, MEP-00, PLATFORM-000, SERVICE-000, UCKO-XXX-000, UCOS-EXEC-000, UCOS-GOV-000, UCOS-RAT-000, UKDA-DEC-000` — family-taxonomy sentinels; recorded closed with justification (`08` §4).

---

## 6. Backlog burn-down signal (deterministic)

| Milestone | Signal in regenerated `closure.json` |
|---|---|
| BL-W1 complete | 0 SPECIFIED LAW; Wave-02 becomes READY |
| BL-W2 complete | 0 SPECIFIED ARCH; generative roots IMPLEMENTED |
| BL-W3 complete | 0 SPECIFIED GOV/UCOS-*/PHASE/MCP/MEP/MCS/UCOS-COMP |
| BL-W4 complete | 0 SPECIFIED PLATFORM/EC3-GATE |
| BL-W5 complete | 0 SPECIFIED realization span |
| **R1 resolved** | **SPECIFIED total = 0** (90 → 0); repository reaches LEVEL-5 Implementation Complete |

---

## 7. Backlog quality attestation

| Check | Result |
|---|---|
| Knowledge Once (each item once) | ✔ 90 distinct IDs |
| No orphan / no duplicate home | ✔ invariants 0 |
| Every executable item has resolved destination | ✔ `files[0]` non-empty |
| Every item has wave, readiness, package | ✔ derived |
| No cyclic ordering | ✔ (`03` acyclic) |

---
*End of 09-IMPLEMENTATION-BACKLOG.md*
