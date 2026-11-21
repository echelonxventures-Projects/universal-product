# 03 — Component Architecture

> PROGRAM **UCOS-UMA-001** · PHASE-001 · UNIVERSAL MEASUREMENT AUTHORITY
> BASELINE `b67a720` · AUTHORITY = **NONE (DESIGN ONLY)** · MODE = DESIGN-ONLY · NON-IMPLEMENTING · FAIL-CLOSED.

---

## 0. Purpose

Decompose the platform (doc 02) into components with explicit responsibilities, inbound/outbound contracts, and invariants. Each component is a governed unit with a stable interface; internals are unspecified (implementation-free).

## 1. Component Map

```
                    ┌──────────────────────────────────────────┐
                    │            UMA GATEWAY (API L4)            │
                    │  routes Measure* calls · binds manifest    │
                    └───────┬───────────────────────┬───────────┘
                            │                        │
                 ┌──────────▼─────────┐    ┌─────────▼──────────┐
                 │  MEASUREMENT KERNEL │    │  METRIC RESOLVER    │
                 │  orchestrates a run │    │  meta-model → value │
                 └───┬───────────┬────┘    └─────────┬──────────┘
                     │           │                   │
        ┌────────────▼──┐  ┌─────▼────────┐   ┌──────▼────────────┐
        │ DISCOVERY CORE │  │ EVIDENCE CORE│   │ REGISTRY CORE      │
        │ observation set│  │ evidence ledg│   │ NS/ID/adapter/onto │
        └───┬────────────┘  └──────────────┘   └────────────────────┘
            │
   ┌────────▼─────────┐
   │ SOURCE ADAPTERS   │  git · md · json · yaml · py · docx · pdf · img · graph · convo · future
   └──────────────────┘
```

## 2. Component Specifications

### 2.1 UMA Gateway (L4)
- **Responsibility:** single entry point for the twelve Measure* operations; binds each request to a Measurement Manifest and a registry snapshot; enforces fail-closed on unknown manifest/registry.
- **Inbound:** API request (doc 09).
- **Outbound:** normalized `MeasurementRequest` to the Kernel.
- **Invariant:** never computes metrics itself; pure routing + binding.

### 2.2 Measurement Kernel
- **Responsibility:** orchestrates a run: resolve manifest → snapshot registries → invoke Discovery Core → assemble Observation Set → dispatch to required L3 services via Metric Resolver → assemble `MeasurementResult` envelope.
- **Invariant:** deterministic ordering; no source writes; emits `UNKNOWN` for any unresolved dependency.

### 2.3 Metric Resolver
- **Responsibility:** given a metric id from the Meta-Model (doc 04), resolve its formula, dependencies, evidence requirements, and compute the value from the Observation Set + upstream metrics.
- **Invariant:** a metric is computable only if all declared dependencies resolved; otherwise result = `UNKNOWN` with failure condition recorded.

### 2.4 Discovery Core
- **Responsibility:** produce the **Observation Set** — the normalized enumeration of every entity (namespace instance, identifier instance, artifact, relationship candidate, prose concept) detected across in-scope sources, using only registered adapters and registered families.
- **Inbound:** Manifest scope; Registry snapshot; Source Adapters.
- **Outbound:** Observation Set (doc 11).
- **Invariant:** registry-driven only. A source/entity not covered by a registered adapter/family becomes an explicit `UNCOVERED` observation, never a silent omission (fail-closed; satisfies MA-2/MA-5).

### 2.5 Evidence Core
- **Responsibility:** for every observation and every metric, record the physical backing evidence (path, byte range/line, content hash, source id) into the Evidence Ledger.
- **Invariant:** no determination without an evidence pointer (Evidence Before Conclusion). Evidence is a pointer, not a copy (Knowledge Once).

### 2.6 Registry Core
- **Responsibility:** hosts the Namespace Registry, Identifier Registry, Source Adapter Registry, and Ontology Registry; serves immutable versioned snapshots to runs.
- **Invariant:** control-plane; every change is a governed, versioned, audited event (doc 13).

### 2.7 Source Adapters
- **Responsibility:** convert one input format into normalized observations; declare their own capabilities and limits (e.g., max size, extractable fields) in the Source Adapter Registry.
- **Invariant:** self-registering (MA-1); declared disposition for what they cannot parse (MA-5). Each adapter is deterministic for a given input.

### 2.8 L3 Metric Services (from doc 02 §3)
Each L3 service is a component that consumes the Observation Set (+ possibly other metrics) and emits metric records. They share the invariants of §Platform Invariants (doc 02 §5) and are individually contract-defined in doc 09.

## 3. Component Interaction — a canonical run

1. Consumer calls `MeasureCoverage(scope, manifest_id)` at the Gateway.
2. Gateway binds manifest + registry snapshot → Kernel.
3. Kernel invokes Discovery Core → Observation Set (adapters + families from snapshot).
4. Kernel dispatches to Coverage Service via Metric Resolver.
5. Coverage Service computes metric; Evidence Core records backing evidence.
6. Kernel assembles `MeasurementResult` (value + manifest + registry version + evidence + UNKNOWNs).
7. Gateway returns result; Result Cache stores it keyed by (manifest, registry version, source state hash).

Same inputs ⇒ same cache key ⇒ replayable, deterministic (doc 12).

## 4. Component-Level Fail-Closed Matrix

| Failure | Component | Behavior |
|---|---|---|
| Unknown manifest | Gateway | reject; no measurement |
| Unregistered source format | Discovery Core / Adapters | emit `UNCOVERED` observation; metric flags partial |
| Unregistered identifier family | Discovery Core | emit `UNCOVERED`; never guess |
| Missing evidence | Evidence Core | metric → `UNKNOWN`; determination blocked |
| Unresolved metric dependency | Metric Resolver | metric → `UNKNOWN` |
| Registry version mismatch | Registry Core | reject run; require explicit snapshot |

## 5. Dependencies Surfaced Here

- **Discovery Core + Source Adapters** replace the monolithic regex block in `closure_engine.py`. → TRANSFER discovery (doc 20).
- **Registry Core** is the concrete home of the CLOSURE-007 "Namespace Registry / Measurement Manifest / Assumption Register" proposals (§05 governance interfaces). → NEW, owned by UMA.

*END — 03 · UCOS-UMA-001 · AUTHORITY = NONE (DESIGN ONLY) · MODIFIES NOTHING.*
