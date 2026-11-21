# 10 — Integration Architecture

> PROGRAM **UCOS-UMA-001** · PHASE-001 · UNIVERSAL MEASUREMENT AUTHORITY
> BASELINE `b67a720` · AUTHORITY = **NONE (DESIGN ONLY)** · MODE = DESIGN-ONLY · NON-IMPLEMENTING · FAIL-CLOSED.
> This document also carries the **Dependency Register** mandated by the mission's Mandatory Honesty clause.

---

## 0. Purpose

Define how UMA integrates with the frozen authorities and pipelines — UKB, Closure Pipeline, Validation, Certification, Continuous Ingestion, Digital Twin, Knowledge Graph, Registries, Governance — **without redesigning any of them**. Integration is one-directional in principle: consumers pull measurements from UMA; UMA pulls truth (read-only) from UKB.

## 1. Integration Invariants

1. UMA **reads** sources (incl. UKB) and **serves** metrics. It never writes to a source or a consumer's store.
2. Consumers **decide**; UMA **measures**. No consumer delegates its decision to UMA, and UMA delegates no measurement to a consumer.
3. Every integration crosses the **public API** (doc 09) or a governed control-plane event (doc 13); no back-door coupling.

## 2. Integration Map

```
        UKB ──(read-only truth)──►  UMA  ──(Measure* envelopes)──► Closure Pipeline
     Registries ──(descriptors)──►  UMA  ──►  Validation Authority
  Continuous Ingestion ──(events)─► UMA  ──►  Certification Authority
   Knowledge Graph ──(edges)─────► UMA  ──►  Governance Authority
     Git / files ─────(sources)──► UMA  ──►  Digital Twin / Dashboards
```

## 3. Integration Contracts (per authority)

| Authority | UMA role | Direction | Contract |
|---|---|---|---|
| **UKB (Repository Truth)** | consumer of truth | UKB→UMA (read) | UMA reads canonical registry/homes to compute integrity/representation/Knowledge-Once metrics. UMA writes nothing to UKB. UKB remains sole truth. |
| **Closure Pipeline** | supplier of coverage/completeness | UMA→Closure | Closure calls `MeasureCoverage/Completeness/Assimilation`; asserts CLOSED/NOT-CLOSED from the envelope. Closure stops *producing* measurements. |
| **Validation** | supplier of validation coverage | UMA→Validation | Validation calls `MeasureValidation`; decides pass/fail. |
| **Certification** | supplier of metric bundle | UMA→Certification | Certification calls `MeasureCertification`; signs. Certificate cites `result_id`. |
| **Continuous Ingestion (CLOSURE-005)** | triggerer of re-measurement | Ingestion→UMA | On new knowledge, ingestion requests a fresh run; UMA re-measures. Ingestion gate itself is unchanged. |
| **Digital Twin** | measurement subscriber | UMA→Twin | Twin renders sealed metrics; never sources truth from Twin. |
| **Knowledge Graph** | source + consumer | both (read edges / serve relationship metrics) | UMA reads graph edges as a source; serves traceability metrics. Does not own the graph. |
| **Registries (canonical)** | distinct from UMA registries | read | UMA reads canonical registries as sources; UMA's NS/ID/adapter registries are *measurement control*, not canonical registries (no conflict with Single Canonical Registry). |
| **Governance (CEP/CONST)** | metric consumer + control authority | both | Governance consumes governance metrics AND authorizes control-plane changes to UMA (doc 13). |

## 4. Distinguishing UMA Registries from Canonical Registries (Single Registry preserved)

CONST-01 mandates a Single Canonical Registry (UKB). UMA's Namespace/Identifier/Adapter/Ontology registries are **not** canonical registries — they hold *measurement descriptors* (how to find and count things), never canonical knowledge. This distinction is constitutional and must be stated in ratification: UMA introduces no competing canonical registry.

## 5. Dependency Register (Mandatory Honesty)

Every discovered dependency on existing Closure Programs, with recommendation:

| # | Dependency (current) | Program | Current role | Recommendation | Rationale |
|---|---|---|---|:---:|---|
| D-1 | `closure_engine.py` discovery (26 regex families) | CLOSURE-002 | sole discoverer | **TRANSFER → UMA** | Discovery is a measurement function; UMA owns measurement. Content seeds registries. |
| D-2 | `closure_engine.py` closure determination | CLOSURE-002 | asserts CLOSED | **RETAIN (Closure)** | Determination is a decision, not a measurement; UMA must never decide. |
| D-3 | `closure.json` (measurement fields) | CLOSURE-002 | metrics carrier | **TRANSFER → UMA** | Metric production/storage is UMA's; Closure reads envelopes. |
| D-4 | `closure.json` (determination field) | CLOSURE-002 | closure verdict | **RETAIN (Closure)** | Verdict is a Closure artifact citing a UMA result. |
| D-5 | `phase2_engine.py` reconciliation counts | CLOSURE-002 | assimilation metrics | **TRANSFER → UMA** | Assimilation Ratio is a UMA metric (3.3). Reconciliation *action* stays with enrichment. |
| D-6 | `phase3_engine.py` planning inputs | CLOSURE-002 | planning | **RETAIN (Closure)** | Planning is not measurement; it consumes UMA gap metrics. |
| D-7 | CLOSURE-007 §05 "Measurement Authority" charter | CLOSURE-007 | documentary MA + MA-1..7 | **SUPERSEDE → UMA** | UMA doc 01 is its permanent successor; MA requirements become UMA obligations. |
| D-8 | CLOSURE-007 Namespace Catalog / Identifier Catalog | CLOSURE-007 | census tables | **TRANSFER (as seed) → UMA registries** | Catalogs become seed data for docs 05/06 registries. |
| D-9 | CLOSURE-006 completeness/coverage audits | CLOSURE-006 | one-off measurements | **SUPERSEDE (recurring) → UMA** | Becomes standing `MeasureArchitecturalCompleteness`. Frozen constitution text untouched. |
| D-10 | UKB canonical truth | UKB | Repository Truth | **RETAIN (UKB), read-only to UMA** | Truth is never a measurement dependency to transfer. |
| D-11 | Continuous Ingestion gate (CLOSURE-005) | CLOSURE-005 | ingestion decision | **RETAIN**; add UMA re-measure trigger | Gate decision stays; it *invokes* UMA. |
| D-12 | Determinism CI (`determinism.yml`) | repo CI | reproducibility check | **EXTEND → cover UMA replay** | Existing determinism guarantee generalizes to UMA runs. |

**Net principle:** every *measurement* responsibility transfers to UMA; every *decision, enrichment, planning, or truth* responsibility remains with its current owner and becomes a UMA consumer. No frozen constitutional text (CONST-*, CEP-*) is modified.

## 6. Migration of Integrations

Sequencing of these transfers (shadow → cutover → retire) is specified in doc 18; adoption in doc 19.

*END — 10 · UCOS-UMA-001 · AUTHORITY = NONE (DESIGN ONLY) · MODIFIES NOTHING.*
