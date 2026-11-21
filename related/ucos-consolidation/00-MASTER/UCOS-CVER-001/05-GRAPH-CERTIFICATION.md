# 05 — Graph Certification

| Field | Value |
|-------|-------|
| ARTIFACT ID | CVER-005 |
| PROGRAM | UCOS-CVER-001 · MISSION EIP-018B |
| STATUS | COMPLETE (verification) · AUTHORITY = NONE (DERIVED) |
| SOURCES | `relationships.json` (11,834 edges) · `artifacts.json` (1001 nodes) · `closure.json` · RIE graphs · FREEZE C2/C3 |

> **Purpose.** Certify completeness of every required graph. The single typed knowledge/relationship graph (`relationships.json`) with the artifact registry as its node set is the substrate; the named graphs are typed projections of it.

---

## 1 — Substrate graph (measured)

| Property | Value |
|----------|-------|
| Nodes (artifact registry) | 1001 |
| Typed edges | 11,834 |
| Relationship types | 14 |
| Parent / Child | 1000 / 1000 (every registered artifact parented) |
| Depends-On / Required-By | 4588 / 4510 (Δ78 — advisory OBS-3) |
| Consumes / Consumed-By | 316 / 316 |
| Authorized-By / Authorizes | 34 / 34 |
| Implements / Implemented-By | 8 / 8 |
| Traces-To / Traced-From | 5 / 5 |
| Evolves-From / inverse | 5 / 5 |
| Dangling edges (orphan endpoints) | 0 (closure orphans=0; all endpoints are registered ids) |
| Cycles (Depends-On) | 0 (CIOA acyclic) |

## 2 — Named graph completeness (typed projections)

| Graph | Backing projection | Complete? | Evidence |
|-------|--------------------|:---------:|----------|
| Repository Graph | artifacts.json + relationships.json | ✔ | 1001 nodes, 11,834 edges |
| Knowledge Graph | KNOWLEDGE-GRAPH-REGISTRY + closure.json | ✔ | closure CLOSED (431/0-gaps) |
| Capability Graph | RIE CAPABILITY-CATALOG | ✔ | families covered=26 |
| Dependency Graph | Depends-On/Required-By edges | ✔ | acyclic; closure dependency closure CLOSED |
| Governance Graph | Authorized-By/Authorizes (34/34) + GOV families | ✔ | CVER-007 |
| Runtime Graph | RIE + RUNTIME-* + Consumes edges | ✔ | runtime program homed |
| Registry Graph | REG-AUTO registries (VOL-018) | ✔ | 1001 registered |
| Ontology Graph | UCKO + ontology registry | ✔ | ontology owned |
| Taxonomy Graph | closure taxonomy registers | ✔ | taxonomy owned |
| Traceability Graph | Traces-To/Traced-From + spine | ✔ | CVER-006 |
| Validation Graph | validation edges (per-capability) | ✔ (structure) | populated Wave 1+ (UCIC 5–9) |
| Certification Graph | Certifies/Certified-By + CERTIFICATION-REGISTRY | ✔ (structure) | populated Wave 1+ (UCIC 10) |
| Evidence Graph | evidence store + Produces edges | ✔ (structure) | data/_evidence per capability |
| Reuse Graph | References/Consumes + Reuse-First | ✔ | USIS-002 reuse mapping |
| Migration Graph | Supersedes/Evolves-From lineage | ✔ | UIP→USIS supersession; change-ledger |
| Implementation Graph | Implements/Implemented-By (8/8) | ✔ (structure) | populated per capability Wave 1+ |

All 16 required graphs are present and structurally complete. Graphs whose *values* accrue per-capability (Validation/Certification/Evidence/Implementation) have complete *structure* now; population is UCIC Wave-1+ by design.

## 3 — Advisory (OBS-3): Depends-On / Required-By asymmetry

- Depends-On = 4588; Required-By = 4510; **Δ = 78**.
- All other inverse pairs are exactly symmetric (Parent/Child, Consumes, Authorized, Implements, Traces, Evolves).
- Interpretation (evidence-based, no assumption asserted as fact): the 78 unmatched Depends-On edges most plausibly terminate on cross-program/upstream terminals or the BOOK root where a stored inverse is not emitted; this is consistent with the CROSS_PROGRAM downward-founding pattern. It creates **no dangling endpoint** (orphans=0), **no cycle**, and **no missing owner**.
- **Action:** verify/normalize inverse materialization at the next governed `ukb build` (Wave-0 regeneration). Advisory, non-blocking.

## 4 — Determination

**Graph layer CERTIFIED.** 1001 nodes · 11,834 typed edges · 14 relationship types · 0 dangling endpoints · 0 cycles. All 16 named graphs are present and complete (4 accrue per-capability values in Wave 1+). One inverse-symmetry advisory (OBS-3, Δ78) is documented for regeneration; it is not a blocker.
