# 02 — Platform Architecture

> PROGRAM **UCOS-UMA-001** · PHASE-001 · UNIVERSAL MEASUREMENT AUTHORITY
> BASELINE `b67a720` · AUTHORITY = **NONE (DESIGN ONLY)** · MODE = DESIGN-ONLY · NON-IMPLEMENTING · FAIL-CLOSED.

---

## 0. Purpose

Define UMA as a **platform** — a set of standing, self-registering services with stable contracts — rather than a script invoked by a program. This document fixes the platform's layers, service catalog, control/data planes, and the invariants every service inherits.

## 1. Platform Tenets

| Tenet | Statement |
|---|---|
| Platform, not program | UMA is always-available and version-stable; Closure Programs call it, not the reverse. |
| Contract-first | Every service is defined by a versioned contract (doc 09) before any implementation. |
| Registry-driven | What UMA can discover/measure is defined by registries (docs 05–07), not code branches. |
| Agnostic core | The core knows nothing about specific repositories, languages, DBs, clouds (doc — NFRs §7). |
| Derived-only | No UMA service ever writes canonical knowledge; all outputs are derived artifacts. |
| Deterministic & replayable | Every service call is a pure function of (inputs, manifest, registry snapshot). |

## 2. Layered Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│  L5  CONSUMPTION PLANE   (Closure · Validation · Certification ·    │
│                            Governance · Digital Twin · Dashboards)  │
├───────────────────────────────────────────────────────────────────┤
│  L4  PUBLIC API PLANE     Measure* APIs (doc 09) · stable contracts │
├───────────────────────────────────────────────────────────────────┤
│  L3  MEASUREMENT SERVICES  (the UMA service catalog — §3)           │
│       Measurement · Coverage · Completeness · Evidence · Relationship│
│       Semantic · Ontology · Statistics · Validation-Metrics · Cert-M │
├───────────────────────────────────────────────────────────────────┤
│  L2  DISCOVERY PLANE       Discovery Service · Source Adapters ·     │
│                             Namespace Registry · Identifier Registry │
├───────────────────────────────────────────────────────────────────┤
│  L1  SUBSTRATE PLANE       Manifest Store · Metric Store · Evidence  │
│                             Ledger · Registry Store · Result Cache   │
├───────────────────────────────────────────────────────────────────┤
│  L0  SOURCE PLANE (read-only)  UKB · Git · files (md/json/yaml/py) · │
│       registries · knowledge stores · graphs · docx/pdf/img · convo  │
└───────────────────────────────────────────────────────────────────┘
```

- **L0 is strictly read-only.** UMA never writes to a source. UKB is the truth authority at L0.
- **L1 substrate** holds only *derived* data: manifests, metric records, evidence pointers, registry descriptors, caches. Never canonical knowledge (Knowledge Once).
- **L2 discovery** turns raw sources into a normalized *Observation Set* using registered adapters + registered families.
- **L3 services** compute metrics from Observation Sets. Each is independently addressable, versioned, and stateless w.r.t. calls.
- **L4 API** exposes the twelve Measure* operations.
- **L5 consumers** never reach below L4.

## 3. Service Catalog (control/data classification)

| Service | Plane | Role | Reads | Writes (derived only) |
|---|---|---|---|---|
| Namespace Registry Service | L2 | Governs namespace descriptors | Registry Store | Registry Store |
| Identifier Registry Service | L2 | Governs identifier-family descriptors | Registry Store | Registry Store |
| Discovery Service | L2 | Registry-driven detection → Observation Set | L0 via adapters | Result Cache |
| Source Adapter Registry | L2 | Governs per-format adapters | Registry Store | Registry Store |
| Coverage Service | L3 | Measured/represented vs universe | Observation Set | Metric Store |
| Measurement Service | L3 | Generic metric evaluation engine | Observation Set, Meta-Model | Metric Store |
| Evidence Service | L3 | Locates & quantifies backing artifacts | Observation Set, L0 | Evidence Ledger |
| Relationship Service | L3 | Edges between entities (traceability graph) | Observation Set, UKB graph | Metric Store |
| Semantic Service | L3 | ID-less / prose entity detection | Observation Set | Metric Store |
| Ontology Service | L3 | Classifies entities against a registered ontology | Registry Store | Metric Store |
| Repository Statistics Service | L3 | Structural counts/statistics | Observation Set | Metric Store |
| Completeness Service | L3 | Domain completeness metrics | Coverage + Ontology | Metric Store |
| Validation Metrics Service | L3 | Coverage basis for validation | Observation Set | Metric Store |
| Certification Metrics Service | L3 | Metric bundle for certification | Metric Store | Metric Store |

Component-level responsibilities and interfaces are specified in doc 03; per-service data objects in doc 11.

## 4. Control Plane vs Data Plane

- **Control plane** (governs *what can be measured*): Namespace Registry, Identifier Registry, Source Adapter Registry, Meta-Model, Manifest Store. Changes here are governed events (doc 13) and are versioned/audited.
- **Data plane** (performs measurement): Discovery + all L3 services. Pure, deterministic, cacheable, horizontally scalable.

Separation guarantees that measurement *semantics* change only through governed control-plane changes, never through silent data-plane behavior — closing the CLOSURE-007 defect where semantics were embedded in code (`FAMILIES`).

## 5. Platform Invariants (inherited by every service)

1. **Manifest-bound:** every call cites a Measurement Manifest (doc 04 §Manifest).
2. **Registry-snapshot-bound:** every call records the registry version it ran against.
3. **Read-only at L0:** zero writes to any source.
4. **Derived-only at L1:** all outputs carry `authority = NONE`.
5. **Fail-closed:** any unresolved source, adapter, or family yields an explicit `UNKNOWN` observation, never a silent drop.
6. **Deterministic:** no wall-clock, no RNG, no network nondeterminism inside a measurement.
7. **Idempotent:** re-execution is side-effect-free w.r.t. sources.

## 6. Deployment Topology (agnostic)

UMA is describable as (and portable across): a single-process library, a set of local CLI stages, a service mesh, or a distributed job fabric. The architecture mandates only the **contracts and planes**, never the substrate. Runtime realizations are in doc 12; the reference realization in doc 17.

## 7. Dependencies Surfaced Here

- The **Discovery Service** subsumes the discovery role of `closure_engine.py` (CLOSURE-002). → TRANSFER (doc 10/20).
- The **Substrate/Metric Store** must not duplicate UKB. → Knowledge Once preserved: UMA stores metrics + pointers, never knowledge.

*END — 02 · UCOS-UMA-001 · AUTHORITY = NONE (DESIGN ONLY) · MODIFIES NOTHING.*
