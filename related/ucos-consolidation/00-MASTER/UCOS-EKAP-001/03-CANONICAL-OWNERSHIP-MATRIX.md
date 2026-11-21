# EKAP-003 — Canonical Ownership Matrix

| Field | Value |
|-------|-------|
| ARTIFACT ID | EKAP-003 (Canonical Ownership Matrix) |
| PROGRAM | UCOS-EKAP-001 |
| STATUS | COMPLETE (analysis) · PRE-WAVE-0 · AUTHORITY = NONE (DERIVED) |
| SOURCES | closure canonical-home register · `config.py` PROGRAM_ROOTS/CHAINS · USIS-002…007 |
| INVARIANT | No concept has multiple constitutional owners (closure `duplicate_homes = 0`). |

> **Purpose.** Establish, for every knowledge concern, its single canonical owner across the constitutional, registry, ontology, taxonomy, capability, theory, evidence, runtime, validation, certification, documentation, and implementation dimensions — with reference/source artifacts explicitly held as evidence-only (never owners).

---

## 1 — Program-level canonical ownership (Knowledge-Once)

| Concern | Canonical owner (program root) | Home tree |
|---------|-------------------------------|-----------|
| Constitution / supreme law | LAW Ω∞-000 · MIP `UCOS-MIP-000002` | root / 00-SOURCE (frozen) |
| Governance determinations | `UCOS-GOV-*` (VOL-020) | 02-MASTER |
| Execution determinations | `UCOS-EXEC-*` (VOL-020) | 02-MASTER |
| Architecture theory | `ARCH_*` constitutions | 02-MASTER / 04-REFERENCE |
| Runtime | RUNTIME-001…014 | 08-RUNTIME |
| Platform | PLATFORM-GOV-000 chain | 09-PLATFORM |
| Data | DATA-GOV-000 chain | 10-DATA |
| Service | SERVICE-GOV-000 chain | 11-SERVICE |
| Application | APP / 12-APPLICATION | 12-APPLICATION |
| Infrastructure | 13-INFRASTRUCTURE | 13-INFRASTRUCTURE |
| Security | 14-SECURITY | 14-SECURITY |
| Ontology | UCKO family | knowledge corpus |
| Meta-models | METACLASS family | knowledge corpus |
| Knowledge Book / registries | UKB `UCOS-BOOK-000000` | 00-BOOK |
| Digital Twin | UKB-ADV (VOL-021) | 00-BOOK/ADVANCEMENT |
| Master Book Architecture | UMB (VOL-022) | 00-BOOK/MASTER-BOOK |
| **Science & Intelligence** | **USIS-GOV-000** (proposed) | **15-… (Wave 0)** |

Each program has exactly one `PROGRAM_ROOT` (config.py) and a single acyclic `Depends-On` chain (CROSS_PROGRAM) — **zero circular ownership, zero duplicate ownership**.

## 2 — Per-dimension canonical ownership (USIS scope)

For science/intelligence knowledge, USIS assigns a single canonical owner per dimension (USIS-004 meta-model tiers):

| Dimension | Canonical owner |
|-----------|-----------------|
| Canonical Owner | the owning USIS universe (USIS-U-*) / science (USIS-SCI-*) |
| Canonical Constitution | USIS-001 (+ LAW Ω∞-000, Part 20/21) |
| Canonical Registry | `04-REGISTRIES/` per-universe registry (USIS-009) |
| Canonical Ontology | `02-ONTOLOGY/` (U-KNW / UCKO) |
| Canonical Taxonomy | `03-TAXONOMY/` |
| Canonical Capability | `08-DOMAINS/…` capability home |
| Canonical Theory | `01-THEORY/` |
| Canonical Evidence | `17-EVIDENCE/` + `data/_evidence/` |
| Canonical Runtime | `14-RUNTIME/` (ref 08-RUNTIME) |
| Canonical Validation | `15-VALIDATION/` |
| Canonical Certification | `16-CERTIFICATION/` (+ CERTIFICATION-REGISTRY) |
| Canonical Documentation | `19-DOCUMENTATION/` |
| Canonical Implementation | Software/Infrastructure stream artifact, **referenced** (never owned by the reference tier) |

## 3 — Reference / source ownership rule (evidence-only)

| Artifact class | Ownership role | Rule |
|----------------|----------------|------|
| `00-SOURCE/**` (frozen constitutions/phases/vision/architecture docx) | **Evidence source** | frozen; never implementation authority; canonical concepts derived from them are owned by their homed family |
| `04-REFERENCE/**` (references, plans, reference architectures) | **Evidence / reference** | reference-class; informs but never owns implementation |
| `03-CATALOGS/**` | Catalog owner | owns the canonical catalog entry for its domain |
| Reference-Architecture md (04-REFERENCE) | Reference | referenced by ARCH constitutions, not an owner |

**Knowledge Assimilation Law compliance:** reference/source artifacts are classified VOL-001/002/003 evidence and are structurally barred from being implementation authority (they carry no governing-determination role; UCIC Stage 3 requires a determination + anchor, which reference artifacts are not). See EKAP-006.

## 4 — Ownership determination

- Concepts with multiple constitutional owners: **0** (closure `duplicate_homes = 0`).
- Orphan concepts (no owner): **0** (closure `orphans = 0`).
- Every family maps to exactly one program root; every program root is acyclic. **Canonical ownership is total and single-valued.**
