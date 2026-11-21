# 17 — Reference Implementation Blueprint

> PROGRAM **UCOS-UMA-001** · PHASE-001 · UNIVERSAL MEASUREMENT AUTHORITY
> BASELINE `b67a720` · AUTHORITY = **NONE (DESIGN ONLY)** · MODE = DESIGN-ONLY · NON-IMPLEMENTING · FAIL-CLOSED.
> This is a *blueprint* — it describes how a conforming implementation would be structured. It contains **no code** and prescribes no language, framework, or runtime.

---

## 0. Purpose

Give implementers an unambiguous, technology-agnostic map from the constitutional architecture (docs 01–16) to buildable modules, so any team can build a **conforming** UMA. Conformance is defined by contracts and invariants, not by a specific stack.

## 1. Conformance Definition

An implementation is a conforming UMA iff it:
1. exposes the twelve Measure* operations + control-plane read ops (doc 09) with the Result Envelope (doc 04 §5);
2. drives discovery **only** from registries (docs 05–07) — no hard-coded families;
3. enforces fail-closed UNCOVERED semantics (docs 07, 08);
4. guarantees determinism, replayability, idempotence (doc 12);
5. stores descriptors/metrics/pointers only — never canonical knowledge (doc 11 §5);
6. authorizes control-plane changes under existing governance (doc 13);
7. asserts `authority = NONE` on every output (doc 01).

## 2. Module Decomposition (logical, stack-agnostic)

| Module | Realizes | Key contract |
|---|---|---|
| `gateway` | UMA Gateway (doc 03 §2.1) | Measure* API (doc 09) |
| `kernel` | Measurement Kernel | run lifecycle (doc 12 §1) |
| `resolver` | Metric Resolver | Meta-Model interpreter (doc 04) |
| `discovery` | Discovery Core | Observation Set (doc 07) |
| `adapters/*` | Source Adapters | per-format read + disposition (doc 07 §3) |
| `registry` | Registry Core | NS/ID/adapter/ontology/metric snapshots (docs 05,06) |
| `evidence` | Evidence Core | EvidenceRef ledger (doc 11) |
| `store` | Substrate | manifests, results, cache (storage-agnostic, doc 11 §6) |
| `services/*` | L3 metric services | doc 02 §3 |
| `ledger` | Governance Ledger | audit (doc 13 §5) |

## 3. Build Order (dependency-respecting)

```
1. Meta-Model + Result Envelope schema        (doc 04)   ── everything depends on this
2. Registry Core + descriptor schemas          (docs 05,06,07)
3. Source Adapters (text first, then non-text)  (doc 07)
4. Discovery Core → Observation Set             (doc 07)
5. Metric Resolver + seed metrics 3.1–3.14      (doc 08)
6. Evidence Core + Store (seal/replay)          (docs 11,12)
7. Gateway + Measure* API                       (doc 09)
8. Governance Ledger + control-plane workflow   (doc 13)
9. Consumer adapters (Closure/Validation/Cert)  (doc 10)
```

## 4. Reference Realization Options (illustrative, non-binding)

The mission requires agnosticism, so the blueprint lists *options*, not requirements:

| Concern | Option A (local) | Option B (service) | Constraint that holds either way |
|---|---|---|---|
| Runtime | CLI stages | service mesh | deterministic, read-only L0 |
| Store | flat files / JSON | document/graph DB | descriptors+pointers only |
| Registries | versioned files | governed DB tables | immutable snapshots |
| Transport | in-process calls | RPC/HTTP | Result Envelope unchanged |
| Determinism | content hashing | content hashing | replay equality mandatory |

The existing repository already contains a *degenerate* UMA: `closure_engine.py` is a single-module, hard-coded-family, text-only realization. The blueprint's first milestone is to re-express its behavior as registry-driven modules (see doc 18).

## 5. Seed Data (from existing evidence, not new truth)

- Namespace Registry seed: CLOSURE-007 report 02 (Namespace Catalog).
- Identifier Registry seed: CLOSURE-007 report 03 (26 families → declarative MatchRules).
- Exclusion/Assumption seed: CLOSURE-007 report 09 (Measurement Assumption Register).
- These are *imported as descriptors*; they assert nothing until a governed run executes.

## 6. Conformance Test Suite (design-level)

| Test class | Asserts | Doc |
|---|---|---|
| Determinism | identical inputs ⇒ identical result | 12 |
| Replay | `ReplayResult` byte-identical | 09 |
| Fail-closed | injected unknown NS/ID/source ⇒ UNCOVERED + PARTIAL | 07,08 |
| Read-only | zero source writes during a run | 15 |
| Knowledge-Once | UMA store holds no canonical content; rebuild reproduces | 11 |
| Registry-driven | removing a family removes discovery of it (no hidden regex) | 06 |
| Authority | every output `authority = NONE` | 01 |

A build passing all classes is a conforming UMA; doc 20 makes this the ratification precondition.

## 7. Dependency Determination

- The reference build **absorbs** `closure_engine.py` discovery behavior as its `discovery`+`adapters` seed (TRANSFER). It does not delete or modify the existing file; migration (doc 18) governs eventual retirement of its discovery authority.

*END — 17 · UCOS-UMA-001 · AUTHORITY = NONE (DESIGN ONLY) · MODIFIES NOTHING.*
