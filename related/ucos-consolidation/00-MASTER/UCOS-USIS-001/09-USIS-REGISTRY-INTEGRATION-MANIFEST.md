# USIS-009 — Registry Integration Manifest

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-009 (Registry Integration Manifest) |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| STATUS | PROPOSED · AWAITING RATIFICATION · PRE-WAVE-0 |
| DEPENDS-ON | USIS-005 · USIS-002/003/006/007 · REG-AUTO-001 · config.py |
| GUARANTEE | No orphan capabilities; every artifact classified + registered; registration gate PASS. |

> **Purpose.** Specify how every USIS entity is registered into the target registries with canonical ownership and zero orphans, using the existing config-driven, metadata-driven, gate-enforced machinery.

---

## 1 — Registration mechanism (three layers, existing machinery)

1. **Curated config mapping** (governed `config.py` edit — Wave 0): append `USIS` family (`^15-UNIVERSAL-SCIENCE-INTELLIGENCE/` → `USIS`/`USIS`/`VOL-023`), `CHAINS["USIS"]`, `PROGRAM_ROOTS["USIS"]=USIS-GOV-000`, `CROSS_PROGRAM ("USIS", <prior program>)`, and `VOLUMES` append `VOL-023`. Append-only; nothing renumbered.
2. **Metadata self-declaration** (per artifact): `UCOS-PROGRAM/CATEGORY/VOLUME/FAMILY/DOMAIN` front-matter (USIS-005 §4) classifies each artifact independent of the curated rule (`METADATA_CLASSIFY_KEYS`).
3. **Path-derived catch-all** (`ukb.py::classify()`): guarantees `unclassified == 0` as a third net.

Materialized by `register.sh --guard` (regenerates registries + twin + portal; runs enforcement gates) — the same path every prior program used.

## 2 — Target registry integration (the 12 registries)

| # | Target registry | USIS integration | Backing store / home |
|---|-----------------|------------------|----------------------|
| 1 | Capability Registry | universes/sciences/domains/capabilities (`USIS-U-*`, `USIS-SCI-*`, `USIS-DOM-*`, `USIS-CAP-*`) | RIE capability catalog; `04-REGISTRIES/`, `08-DOMAINS/` |
| 2 | Ontology Registry | substrate ontology (USIS-005 `02-ONTOLOGY/`) | Part 19/U24 ontology registry |
| 3 | Taxonomy Registry | science/universe/domain/algorithm/model taxonomy | `03-TAXONOMY/` |
| 4 | Knowledge Registry | USIS artifacts as knowledge-graph nodes | KNOWLEDGE-GRAPH-REGISTRY (regenerated) |
| 5 | Execution Registry | USIS capabilities under the Universal Science & Intelligence stream | EXEC-REG-001 `executions.json` (post-C4) |
| 6 | Validation Registry | grounding/explanation/bounded-autonomy validation records | `15-VALIDATION/`; evidence store |
| 7 | Certification Registry | science-intelligence certifications | CERTIFICATION-REGISTRY (regenerated) |
| 8 | Evidence Registry | inference/analytics/learning/self-evolution traces + provenance | `17-EVIDENCE/`; `data/_evidence/<CAP-ID>/` |
| 9 | Dependency Registry | USIS Depends-On edges (acyclic; downward-founded) | `relationships.json` (regenerated) |
| 10 | Architecture Registry | USIS-001…021 architecture artifacts | UNIVERSAL-ARTIFACT-REGISTRY (regenerated) |
| 11 | Project Registry | `20-PROJECTS/` implementation projects | MCP-003 backlog |
| 12 | Implementation Registry | per-capability UCIC realization records | UCIC evidence + MCP-006 traceability |

Program-specific registries under `04-REGISTRIES/`: Universe · Science · Domain · Capability · Algorithm · Model · Pattern · Insight · Reasoning-Trace · Dataset · Learned-Change · Self-Evolution.

## 3 — No-Orphan proof obligations (GOV-001-T3; verified in USIS-011)

Every USIS artifact must be, at build time: **classified** (program `USIS`, not `OTHER`), **parented** (Parent edge to chain predecessor; root `USIS-GOV-000`), **depended** (`USIS-GOV-000` Depends-On prior program terminal; acyclic), **registered** (present in every synchronized register), **homed** (exactly one canonical home under `15-…/`). Enforcement order (fail-fast): `eligibility → validity → classification → registration`. Target at completion: **0 unregistered, 0 unclassified, 0 orphan**.

## 4 — Determinism & append-only

All registry writes are deterministic regenerations (idempotent); identity append-only (Universal IDs never reused/renumbered); adding a future science/domain/algorithm/model appends a row + homed artifact and never rewrites an existing entry (CR-INF-007).

_Specifies registration; performs none. The `config.py` edit + `register.sh` transaction are governed Wave-0 steps, pending authorization._
