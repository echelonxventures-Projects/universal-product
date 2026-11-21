# 12 — Runtime Architecture

> PROGRAM **UCOS-UMA-001** · PHASE-001 · UNIVERSAL MEASUREMENT AUTHORITY
> BASELINE `b67a720` · AUTHORITY = **NONE (DESIGN ONLY)** · MODE = DESIGN-ONLY · NON-IMPLEMENTING · FAIL-CLOSED.

---

## 0. Purpose

Define how UMA *executes* at runtime: the lifecycle of a measurement run, execution guarantees (determinism, idempotence, replayability), concurrency/distribution model, and caching — all while remaining infrastructure/cloud/vendor agnostic.

## 1. Run Lifecycle (state machine)

```
REQUESTED ─► BOUND ─► DISCOVERED ─► MEASURED ─► SEALED
     │         │           │            │          │
  validate   pin        observe      compute    immutable,
  manifest  registry    (adapters)   metrics    addressable,
            snapshot                            replayable
     └──────────────── any unresolved dependency ───────► FAILED-CLOSED (explicit)
```

- **REQUESTED→BOUND:** manifest validated; registry snapshot pinned; unknown manifest ⇒ FAILED-CLOSED.
- **BOUND→DISCOVERED:** Discovery Core produces Observation Set + Uncovered ledger.
- **DISCOVERED→MEASURED:** Metric Resolver computes the requested metrics over the DAG.
- **MEASURED→SEALED:** Result envelope written append-only, keyed by `(manifest_id, registry_version, source_state_hash, metric_id)`.
- No transition invents data; any gap surfaces as PARTIAL/UNKNOWN, not a stall or a guess.

## 2. Execution Guarantees

| Guarantee | Mechanism |
|---|---|
| **Deterministic** | Run is a pure function of (manifest, registry snapshot, source content). No clock/RNG/network in-band. |
| **Replayable** | `ReplayResult` re-runs the sealed key and MUST reproduce byte-identically (doc 09). |
| **Idempotent** | Re-running writes no new source state; identical key ⇒ cache hit, not recompute-with-drift. |
| **Fail-closed** | Missing adapter/family/evidence ⇒ explicit UNCOVERED/UNKNOWN; never silent success. |
| **Isolated** | One run never reads another run's mutable state; only sealed (immutable) results are cross-referenced. |

## 3. The Source-State Hash (determinism key)

Before measuring, the runtime computes a content hash over exactly the in-scope sources (per manifest `source_roots` + `extensions` + `size_policy`). This hash:
- is the determinism contract key (identical hash ⇒ identical result);
- pins the run to a concrete source state independent of git baseline naming;
- makes CLOSURE-007's "repo-only vs full-corpus" ambiguity impossible — the scope is hashed and recorded, not implied by an env var.

## 4. Concurrency & Distribution (agnostic)

- **Parallelism unit:** discovery per source and metric per DAG node are independently schedulable (pure functions), enabling embarrassingly parallel execution.
- **Distribution:** the runtime is describable as single-process, multi-process, or a distributed job fabric; the contract requires only that scheduling preserve the DAG order and determinism.
- **No shared mutable state:** workers exchange immutable Observation Sets and Results; coordination is by content-addressed keys.
- **Infinite scalability:** because runs are pure and sharded by source/metric, horizontal scale-out changes throughput, never results.

## 5. Caching & Incrementality

- **Result cache** keyed by content-addressed run key; a repeat request is served from cache (idempotence).
- **Incremental discovery:** when only some sources change, only affected observations and dependent metrics recompute; unaffected sealed results are reused. Determinism is preserved because keys include the source-state hash.
- Cache is a performance layer only — deleting it never changes results (rebuild test, doc 11 §5).

## 6. Failure & Recovery Semantics

| Failure | Runtime behavior |
|---|---|
| Source unreachable | mark affected observations UNCOVERED-SOURCE; metric → PARTIAL; run still SEALS (visibly partial) |
| Adapter crash on one artifact | that artifact → UNCOVERED; run continues (no whole-run poison) |
| Registry snapshot missing | FAILED-CLOSED at BOUND (never run against an unpinned registry) |
| Partial completion / interruption | run is resumable; unsealed runs are discarded, never partially trusted |

## 7. Observability

The runtime emits (as derived telemetry, never as truth): run timings, cache hit ratio, uncovered counts by kind, registry version in use. Telemetry is excluded from the determinism contract (it never affects a Result value).

## 8. Dependency Determination

- The current runtime is a one-shot `python closure_engine.py` invocation embedded in a Closure Program. UMA's standing runtime **subsumes** that execution role (TRANSFER), while the Closure Program's *decision step* becomes a post-UMA consumer that reads a SEALED result. Final in doc 20.

*END — 12 · UCOS-UMA-001 · AUTHORITY = NONE (DESIGN ONLY) · MODIFIES NOTHING.*
