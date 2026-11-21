# 09 — Public API Specification

> PROGRAM **UCOS-UMA-001** · PHASE-001 · UNIVERSAL MEASUREMENT AUTHORITY
> BASELINE `b67a720` · AUTHORITY = **NONE (DESIGN ONLY)** · MODE = DESIGN-ONLY · NON-IMPLEMENTING · FAIL-CLOSED.

---

## 0. Purpose

Specify the UMA public API — the stable, versioned, transport-agnostic contract by which all consumers (Closure, Validation, Certification, Governance, Digital Twin) obtain measurements. The API is described abstractly (operations, inputs, outputs, guarantees); no transport, framework, or code is prescribed.

## 1. API Principles

| Principle | Statement |
|---|---|
| Contract-first | Operations are frozen contracts; behavior changes only via versioned amendment (doc 13/14). |
| Read-only | No API operation mutates a source. All operations are queries. |
| Manifest-bound | Every operation takes a `manifest_id`; the result cites it. |
| Deterministic | Same (operation, args, manifest, baseline, registry version) ⇒ same result. |
| Fail-closed | Missing/ambiguous inputs → typed error or `UNKNOWN` result, never a guessed value. |
| Envelope-uniform | Every operation returns the Measurement Result Envelope (doc 04 §5). |

## 2. Common Request / Response Shape

```
Request  { operation, scope, manifest_id, [entity_ref], [baseline] }
Response = MeasurementResult (doc 04 §5)
           { metric_id(s), value, status, manifest_id, registry_version,
             baseline, source_state_hash, evidence[], uncovered[], assumptions[],
             authority = NONE }
```

`scope` selects a universe (repository / namespace / path / domain). `entity_ref` narrows to a namespace, family, or artifact where relevant.

## 3. The Twelve Constitutional Operations (mission minimum)

| # | Operation | Purpose | Backing metric(s) (doc 08) | Primary consumer |
|---|---|---|---|---|
| A-1 | `MeasureRepository(scope)` | Full repository measurement bundle | 3.1, 3.2, 3.4, 3.7, 3.12 | Closure, Governance |
| A-2 | `MeasureNamespace(namespace_id)` | Members, coverage, status of one namespace | 3.4, 3.7 | Closure |
| A-3 | `MeasureCoverage(scope)` | Covered ÷ universe, with uncovered ledger | 3.4 | Closure, Validation |
| A-4 | `MeasureAssimilation(scope)` | External→canonical assimilation ratio | 3.3 | Closure (Domain B) |
| A-5 | `MeasureTraceability(scope)` | Relationship/traceability completeness | 3.2, Relationship Svc | Closure, Cert |
| A-6 | `MeasureValidation(scope)` | Validation coverage basis | 3.9 | Validation authority |
| A-7 | `MeasureCertification(scope)` | Certification metric bundle | 3.10 | Certification authority |
| A-8 | `MeasureEvolution(baselineₐ, baseld_b)` | Delta of measured state across baselines | 3.11 | Governance |
| A-9 | `MeasureKnowledge(scope)` | Knowledge Once + representation metrics | 3.13, 3.2 | UKB-adjacent, Closure |
| A-10 | `MeasureGovernance(scope)` | Authority uniqueness + freeze integrity | 3.8, 3.14 | Governance |
| A-11 | `MeasureRepositoryHealth(scope)` | Composite health roll-up | weakest-of(3.1,3.4,3.8,3.12) | Dashboards, Governance |
| A-12 | `MeasureArchitecturalCompleteness(scope)` | Domain completeness, zero-UNKNOWN | 3.5, 3.6 | Closure, Cert |

## 4. Supporting (control-plane) Operations

Read-only introspection of the control plane (governed writes are not public API — they are governance events, doc 13):

| Operation | Purpose |
|---|---|
| `ListNamespaces()` / `DescribeNamespace(id)` | Namespace Registry snapshot (doc 05) |
| `ListIdentifierFamilies()` / `DescribeFamily(id)` | Identifier Registry snapshot (doc 06) |
| `ListSourceAdapters()` | Source Adapter Registry (doc 07) |
| `ListMetrics()` / `DescribeMetric(id)` | Meta-Model catalog (doc 04) |
| `GetManifest(id)` / `ListManifests()` | Measurement Manifests |
| `GetResult(result_id)` / `ReplayResult(result_id)` | Retrieve / reproduce a sealed result |

`ReplayResult` re-executes against the pinned manifest+baseline and MUST return a byte-identical value (replayability contract).

## 5. Error Model (fail-closed)

| Error | Condition | Never does |
|---|---|---|
| `E_UNKNOWN_MANIFEST` | manifest_id not registered | run with a default |
| `E_REGISTRY_MISMATCH` | requested vs pinned registry version differ | silently pick one |
| `E_SOURCE_UNAVAILABLE` | a declared source root unreachable | report partial as complete |
| `E_UNRESOLVED_METRIC` | metric dependency missing | fabricate a value |

Errors are explicit; a well-formed but blind measurement returns `status = PARTIAL` with a populated `uncovered[]` rather than an error — visibility over silence.

## 6. Versioning & Compatibility

- APIs carry `api_version`; the meta-model carries `schema_version`. Both are stamped into every result.
- Backward-incompatible changes require a new major version and a governance amendment (doc 14). Prior sealed results remain reproducible against their pinned versions.

## 7. Dependency Determination

- Closure/Validation/Certification today read measurement directly from `closure.json`/`phase2.json`. Post-UMA they call A-1…A-12 and receive envelopes. The JSON engines become either retired or thin UMA clients. → measurement-read path **TRANSFERS** to this API (doc 20).

*END — 09 · UCOS-UMA-001 · AUTHORITY = NONE (DESIGN ONLY) · MODIFIES NOTHING.*
