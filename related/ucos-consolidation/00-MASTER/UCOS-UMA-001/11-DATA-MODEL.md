# 11 — Data Model

> PROGRAM **UCOS-UMA-001** · PHASE-001 · UNIVERSAL MEASUREMENT AUTHORITY
> BASELINE `b67a720` · AUTHORITY = **NONE (DESIGN ONLY)** · MODE = DESIGN-ONLY · NON-IMPLEMENTING · FAIL-CLOSED.

---

## 0. Purpose

Define the logical data model for UMA — the entities the platform stores and their relationships. The model is **storage-agnostic** (doc — NFRs): it maps equally onto a document store, relational schema, graph DB, or flat files. **Critical invariant: UMA stores descriptors, metrics, manifests, and evidence *pointers* — never canonical knowledge (Knowledge Once).**

## 1. Entity Overview

```
                       ┌──────────────┐
                       │  Manifest     │
                       └──────┬───────┘
                              │ bound-by
        ┌──────────────┐      ▼        ┌───────────────┐
        │ RegistrySnap  │◄── MeasurementRun ──►│ Result      │
        └──────┬───────┘          │            └────┬───────┘
   snapshot-of │                  │ produces        │ cites
   ┌───────────┼───────────┐      ▼                 ▼
┌──▼───┐  ┌────▼────┐  ┌────▼────┐  ┌──────────┐  ┌────────────┐
│ NS    │  │ IdFamily │  │ Adapter │  │Observation│  │ EvidenceRef│
│Desc.  │  │ Desc.    │  │ Desc.   │  │  Set      │  │ (pointer)  │
└──────┘  └─────────┘  └─────────┘  └────┬─────┘  └────────────┘
                                          │ contains
                                    ┌─────▼──────┐  ┌────────────┐
                                    │ Observation │  │ Uncovered  │
                                    └────────────┘  └────────────┘
```

## 2. Core Entities

| Entity | Key fields | Notes |
|---|---|---|
| **NamespaceDescriptor** | namespace_id, status, owner, families[], evidence[] | doc 05 |
| **IdentifierFamilyDescriptor** | family_id, namespace_id, match_rule, width/case policy, sentinels | doc 06 |
| **SourceAdapterDescriptor** | adapter_id, formats[], capability, disposition_on_fail, size_policy | doc 07 |
| **MetricDefinition** | metric_id, formula, domain, evidence spec, deps, failure conditions, determinism_class | doc 04 |
| **Manifest** | manifest_id, scan_mode, source_roots[], extensions[], size_cap, registry_version, exclusions[], assumptions[], baseline | doc 04 |
| **RegistrySnapshot** | registry_version, {NS,ID,adapter,ontology,metric} versions, hash | immutable |
| **MeasurementRun** | run_id, manifest_id, registry_version, baseline, source_state_hash, started/sealed marker | orchestration record |
| **ObservationSet** | run_id, observations[], uncovered[] | product of Discovery |
| **Observation** | entity_kind, namespace_id, family_id, artifact_ref, value/attributes | one detected entity |
| **Uncovered** | kind (NS/ID/SOURCE/OVER-CAP/PROSE), target, reason | fail-closed record |
| **EvidenceRef** | source_id, path, byte/line range, content_hash | **pointer only**, never a copy |
| **MeasurementResult** | metric_id, value, status, manifest_id, registry_version, evidence[], uncovered[], authority=NONE | doc 04 §5 |
| **ExclusionRecord / AssumptionRecord** | kind, target, rationale, authority, since_baseline | MA-7 |
| **Ontology / OntologyClass** | class_id, definition, match cues | doc 08 Ontology Service |

## 3. Key Relationships & Cardinalities

- Namespace `1 ──< N` IdentifierFamily.
- Manifest `1 ── 1` RegistrySnapshot (pinned); `1 ──< N` MeasurementRun.
- MeasurementRun `1 ── 1` ObservationSet; `1 ──< N` MeasurementResult.
- Observation / Result `N ──< N` EvidenceRef (pointers).
- Result `references` upstream Results (metric DAG, doc 08).

## 4. Immutability, Sealing & Provenance

- **Descriptors & metric defs:** versioned; a change creates a new version, never edits in place (replayability).
- **Manifests & snapshots:** immutable once created.
- **Runs & Results:** **sealed** — once produced they are append-only, addressable by `result_id`, and reproducible via `ReplayResult` (doc 09).
- **Provenance:** every Result transitively records manifest → snapshot → source_state_hash → evidence, giving a complete audit chain (Evidence Before Conclusion).

## 5. Knowledge Once Enforcement (data-level)

- No entity holds canonical concept content. `EvidenceRef` is `{source_id, locator, hash}` — it *points into* UKB/repo, it does not copy.
- UKB remains the sole home of truth; UMA's stores are strictly derivative and disposable/rebuildable from sources + registries.
- Rebuild test: deleting all UMA data and re-running every sealed manifest MUST reproduce identical Results — proving UMA holds no unique truth.

## 6. Storage-Agnostic Mapping

| Logical entity | Document store | Relational | Graph |
|---|---|---|---|
| Descriptors | collections | tables + version col | typed nodes |
| Observations | nested docs | fact table | edges/nodes |
| Results | result docs | results table | result nodes + DAG edges |
| EvidenceRef | embedded pointers | FK to source registry | edges to source nodes |

The model prescribes entities and invariants, not the substrate — satisfying database/technology agnosticism.

## 7. Dependency Determination

- `closure.json`/`phase2.json`/`phase3.json` today conflate *measurement data* and *closure determination* in one file. The data model separates them: UMA owns MeasurementResult; Closure owns its determination artifact that *cites* a Result. → measurement data **TRANSFERS**; determination data **REMAINS** (doc 20).

*END — 11 · UCOS-UMA-001 · AUTHORITY = NONE (DESIGN ONLY) · MODIFIES NOTHING.*
