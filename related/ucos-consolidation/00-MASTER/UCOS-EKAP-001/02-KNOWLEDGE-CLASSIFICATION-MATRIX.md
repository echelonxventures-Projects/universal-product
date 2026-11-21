# EKAP-002 — Knowledge Classification Matrix

| Field | Value |
|-------|-------|
| ARTIFACT ID | EKAP-002 (Knowledge Classification Matrix) |
| PROGRAM | UCOS-EKAP-001 |
| STATUS | COMPLETE (analysis) · PRE-WAVE-0 · AUTHORITY = NONE (DERIVED) |
| SOURCES | `closure.json` families/dispositions · FREEZE C2 (23 types/6 streams) · USIS-002/003/006 |

> **Purpose.** Classify every knowledge concept into the mission taxonomy, reconciled against the FREEZE C2 realization model and the USIS substrate. Every family maps to exactly one realization type, one stream, and one USIS home — so classification is total and single-valued (zero unclassified).

---

## 1 — Family → classification → realization type → stream → USIS home

| Family | Mission class | Realization type (C2) | Stream (C2) | USIS home (post-Wave-0) |
|--------|---------------|-----------------------|-------------|-------------------------|
| LAW (Ω∞-*) | Law | CONSTITUTIONAL_LAW | Governance | (constitution; referenced by USIS) |
| CEP | Principle / Evidence | CONSTITUTIONAL_EVIDENCE_PRINCIPLE | Governance | referenced |
| FOUNDATION | Principle | CONSTITUTIONAL_FOUNDATION | Governance | referenced |
| GOV / UCOS-GOV | Governance | GOVERNANCE_DETERMINATION | Governance | Governance-Intelligence domain (ref) |
| UCOS-RAT | Governance | RATIFICATION_DETERMINATION | Governance | referenced |
| UCOS-RECON | Governance | RECONCILIATION_DETERMINATION | Governance | referenced |
| UKDA-DEC | Governance | GOVERNANCE_DECISION | Governance | referenced |
| MEP | Governance (evolution) | CONSTITUTIONAL_EVOLUTION_PROPOSAL | Governance | referenced |
| UCKO | Ontology | ONTOLOGY | Knowledge | Knowledge Universe (U-KNW) |
| METACLASS (AMC/DMR/…) | Model / Meta | META_MODEL | Knowledge | Knowledge / Meta-Model (USIS-004) |
| MCP / MCS | Master / Protocol | MASTER_CONTEXT_PROTOCOL | Knowledge | referenced (operational memory) |
| ARCH | Theory / Architecture | ARCHITECTURE_SPECIFICATION | Documentation | referenced by each universe |
| EPIC | Project | PROGRAM_EPIC | Documentation | Project Registry (USIS-009) |
| PHASE | Documentation / Lifecycle | LIFECYCLE_PHASE | Documentation | referenced |
| BAND-UNIT (EC3-*) | Registry | EXECUTION_BAND_UNIT | Registry | referenced |
| EC3-GATE | Governance (gate) | ADMISSION_GATE | Governance | referenced |
| UCOS-COMP / UCOS-EXEC | Engine | SOFTWARE_ENGINE | Software | Engines (USIS 12) via Software stream |
| DATA | Model / Data | DATA_MODEL | Software | Universal Data Universe (U-DAT, ref 10-DATA) |
| SERVICE | Service | SERVICE | Software | Services (USIS 13) via Software stream |
| APPLICATION | Implementation | APPLICATION | Software | referenced |
| INFRASTRUCTURE | Implementation | INFRASTRUCTURE_COMPONENT | Infrastructure | referenced |
| PLATFORM | Engine / Platform | PLATFORM_COMPONENT | Software | referenced |
| RUNTIME | Runtime | RUNTIME_COMPONENT | Software | Runtime (USIS 14, ref 08-RUNTIME) |

Coverage: **26 families → 23 realization types → 6 streams**, total and single-valued. **Unclassified concepts: 0** (closure `detail.unclassified = 0`).

## 2 — Mission classification taxonomy — coverage

Every mission-required class is represented in the corpus and mapped to a canonical owner:

| Mission class | Represented by | Canonical owner tier (USIS-004) |
|---------------|----------------|--------------------------------|
| Science | (new via USIS U-SCI) | Science |
| Discipline / Domain / Sub-Domain | ARCH families + USIS domains | Discipline/Domain |
| Capability | EPIC/BAND-UNIT/component families | Capability |
| Theory | ARCH-* / RUNTIME-002 theory docs | Theory |
| Law | LAW (Ω∞-*) | Governance/Constitution |
| Principle | CEP / FOUNDATION | Governance |
| Ontology | UCKO | Ontology |
| Taxonomy | (closure taxonomy registers) | Taxonomy |
| Registry | BAND-UNIT / REG artifacts | Registry |
| Knowledge Object | 431 concepts (UKO nodes) | Knowledge Object |
| Pattern / Model / Algorithm | METACLASS / DATA / (USIS U-ALG/U-MDL) | Model/Algorithm |
| Engine / Service / Runtime | UCOS-COMP/EXEC / SERVICE / RUNTIME | Engine/Service/Runtime |
| Validation / Certification / Evidence | TRACK/CCE + certification.json | Validation/Certification/Evidence |
| Governance | GOV/UCOS-GOV/RAT/RECON/MEP | Governance |
| Implementation / Project | APPLICATION/INFRASTRUCTURE/PLATFORM / EPIC | Implementation/Project |
| Documentation / Reference / Archive | 04-REFERENCE / 00-SOURCE / PHASE | Documentation/Reference |
| Future Candidate | USIS U-FUT | Future |
| Unknown Classification | USIS U-UNK (reserved) | Unknown (0 actual) |

**Unknown Classification (actual): 0.** The Unknown-Sciences slot is reserved (open), not populated by any existing artifact.

## 3 — Classification determination

Every concept and every registered artifact carries exactly one classification (family → type → stream → volume), verified by the closure system (`unclassified = 0`) and the registration gate (`classification` gate, config-driven + metadata + path-derived catch-all). **Zero unclassified knowledge.**
