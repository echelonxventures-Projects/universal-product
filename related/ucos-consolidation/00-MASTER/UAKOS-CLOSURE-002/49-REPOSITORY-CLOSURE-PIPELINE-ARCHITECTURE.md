# 49 — Repository Closure Pipeline Architecture (Phase-004)

| Field | Value |
|-------|-------|
| PROGRAM | UAKOS-CLOSURE-002 · PHASE-004 |
| STATUS | PLANNING / GOVERNANCE — no implementation artifact modified |
| AUTHORITY | NONE — DERIVED TRUTH |
| BASELINE | branch `governance-reconciliation` · HEAD `b67a720` |
| PRINCIPLE | Knowledge Once (`UCKO-PRIN-0001`) · Frozen-Corpus-Read-Only (`UCKO-PRIN-0002`) · Determinism (`UCKO-PRIN-0005`) · Fail-Closed (`TRACK-001`) |

> Defines the **permanent** architecture of the Repository Closure Pipeline as a reusable platform capability. It reuses existing authority; it introduces no engine, registry, ID system, graph, or traceability store.

## 1. Stage map, ownership, boundaries

| # | Stage | Owner (canonical) | Writes Repository Truth? | Boundary |
|---|-------|-------------------|:------------------------:|----------|
| S0 | **Authoritative Repository Engine** | `00-BOOK/tools/ukb.py` + `register.sh --guard` | **YES — sole writer** | Assigns Universal IDs/pages, builds registries + knowledge graph, enforces registration/drift. Nothing else may write Repository Truth. |
| S1 | **External Knowledge Ingestion (EKI)** | `closure_engine.py` (Phase-001) | no | Reads external/repo sources; emits evidence. Never assigns IDs, never registers. |
| S2 | **Concept Extraction** | `closure_engine.py` | no | Deterministic canonical-anchor extraction; no semantic invention (Charter §5 boundary). |
| S3 | **Canonical Matching** | `closure_engine.py` | no | Matches anchors to existing canonical homes / ukb registry; recommends, never creates. |
| S4 | **Knowledge Graph** | authoritative: `00-BOOK/DATA/relationships.json` (ukb). Projection: `phase2_engine.py` (Phase-002) | no (projection) | Phase-002 projects reconciliation views (20–35); it reuses the authoritative graph, never a parallel one. |
| S5 | **Traceability** | `MCP-006` + `ukb trace` | no (consumes) | Pipeline consumes/feeds the one traceability spine; no parallel trace store. |
| S6 | **Gap Analysis** | EKI gaps (`10`) + ukb gaps (`13`/`19`) → one consolidated register | no | Measures; never fabricates absence (prove, don't assume). |
| S7 | **Implementation Planning** | Enrichment plan (`09`) → routes gaps to canonical destinations | no | Feeds the normal capability-admission path (`AEOS-001`/`UCIC-001`); does not implement. |
| S8 | **Validation** | `CEP-004` + `verify.sh` + `ukb validate` | no | Reuses existing validators; adds none. |
| S9 | **Certification** | `CEP-005` + CCE (`UCOS-COMP-000001`) + `register.sh --guard` | no | Reuses existing certification; fail-closed. |
| S10 | **Repository Closure** | Determination (`19`) + closure certificate | no | Certificate is green only when all S1–S9 gates pass (see doc 54). |

## 2. Dataflow

```
External sources / repo / uploads / conversations
      │  S1 EKI
      ▼
closure_engine.py ──S2 extract──S3 match──▶ closure.json  (interface contract v1)
      │                                          │  S4 (Phase-002, read-only)
      │                                          ▼
      │                                   phase2_engine.py ─▶ 20..35 + phase2.json
      ▼  S6 gaps / S7 plan (evidence + recommendations only)
      └──────────────▶  ukb.py + register.sh  ◀── S5 traceability (MCP-006)
                              │  S0 (SOLE writer of Repository Truth)
                              ▼
              Registries · Knowledge Graph · Traceability · Digital Twin
                              │  S8 validate (CEP-004) · S9 certify (CEP-005/CCE)
                              ▼
                     S10 Repository Closure Determination (19)
```

## 3. Invariants

- **Single writer:** only S0 (ukb + register.sh) mutates Repository Truth. S1–S7 are evidence/recommendation producers.
- **Read-only downstream:** Phase-N consumes Phase-(N-1) JSON model read-only (Knowledge Once — no re-extraction).
- **No parallel authority:** one engine, one registry, one ID system, one graph, one traceability model, one determination.
- **Operational-memory placement:** pipeline **tooling** lives in `00-MASTER/` (RECON-C1: excluded from corpus). Its **ratified outputs** enter Repository Truth only via S0.

---

*END — 49 · Pipeline Architecture · AUTHORITY = NONE.*
