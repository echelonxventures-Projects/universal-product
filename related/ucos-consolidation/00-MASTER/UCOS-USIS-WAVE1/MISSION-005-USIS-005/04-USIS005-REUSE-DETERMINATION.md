# 04 — USIS-005 REUSE DETERMINATION

**Principle:** Reuse before creation · Knowledge Once · Zero Duplicates (LAW
USIS-02). Repository Truth prevails over assumptions. USIS-005 creates **only** the
Theory/Ontology/Taxonomy foundation that has no canonical predecessor; everything
below is reused/referenced as authority.

Legend — **REUSE** · **EXTEND** (append-only) · **REFERENCE** (link, never fork) ·
**CREATE**.

---

## 1 — Reusable engines & tooling (REUSE)

| Asset | USIS-005 disposition |
|---|---|
| `ukb.py` (allocation/classification/graph/registers) | **REUSE** |
| `ukbx.py` (twin/portal/certify) | **REUSE** |
| `register.sh` (10-phase transaction + `--guard`) | **REUSE** |
| `config.py` (`^15-…/ → USIS/USIS/VOL-024`) | **REUSE** — already routes areas 01/02/03; **no edit** |

## 2 — Reusable universes / constitutions / metadata (REFERENCE)

| Asset | Disposition | Why not duplicated |
|---|---|---|
| USIS-001 constitution (LAW USIS-00/02/04/08/09) | **REFERENCE** | governing determination + anchor |
| USIS-002 Universe Catalog (21 universes) | **REFERENCE** | the ontology/taxonomy organizes these universes' concepts |
| USIS-004 Meta-Model (tiers 6 Theory / 7 Ontology / 8 Taxonomy) | **REFERENCE** (`Implements`) | USIS-005 conforms to the committed meta-model tier contract; does not redefine it |
| **U24 Knowledge Universe / MIP Part 19 ontology registry** | **REFERENCE** | the substrate ontology **reuses** the canonical knowledge ontology; forking it would violate LAW USIS-02 |
| Self-classification metadata (`METADATA_CLASSIFY_KEYS`) | **REUSE** | USIS-005 front-matter classifies via the same keys |

## 3 — Reusable registries (EXTEND via reused mechanism, not new registries)

| Registry | Disposition |
|---|---|
| UNIVERSAL-ARTIFACT / PAGE / KNOWLEDGE-GRAPH / CHANGE-VERSION-LINEAGE / CERTIFICATION | **EXTEND** (append rows/edges) |
| Ontology Registry / Taxonomy Registry (USIS-009 §2 targets) | **REFERENCE / EXTEND** — the ontology/taxonomy foundation records into the existing Part-19/U24 ontology + taxonomy registries; it does **not** stand up a competing allocator |
| VOLUME-REGISTRY | **REUSE** — VOL-024; no new volume |

## 4 — Reusable validation / certification / governance / traceability (REUSE)

| Asset | Disposition |
|---|---|
| UCIC-001 (15-stage fail-closed) · SCIENCE_INTELLIGENCE lifecycle (USIS-008) | **REUSE** |
| GOV-001-T3 (No-Orphan) · GOV-002 (traceability) · REG-AUTO-001 | **REUSE** |
| `ukb validate`/`enforce`, `ukbx validate`/`twin --check`/`certify`, `register.sh --guard` | **REUSE** |
| USIS-011 obligations (esp. **11 Ontology Closure**, **12 Taxonomy Closure**, 2/3 no-dup, 4 orphan, 5 acyclic, 10 registry closure, 18 byte-stable) | **REUSE** — fail-closed predicates |
| CI gates (`ucos-registration-gate.yml`, `ec1-ci.yml`, `determinism.yml`) | **REUSE** |

## 5 — The structure-specification is REUSED, not re-created (critical Reuse-First finding)

The repository structure (21-area tree, naming, classification, No-Orphan homing)
is **already canonically encoded** in committed `config.py` + the physical `15-…/`
tree. The establishment blueprint `05-…STRUCTURE-SPECIFICATION.md` is
**operational-memory build guidance** (its §6: "performs no registration").

Therefore USIS-005 **must not** register a "repository structure specification"
corpus artifact — doing so would duplicate the canonical structure encoding
(LAW USIS-02 / Knowledge-Once, USIS-011 obl 2/3/8). The structure spec is
**REFERENCE-ONLY**. USIS-005's genuinely-new content is the **Theory/Ontology/
Taxonomy foundation**, which has no canonical predecessor.

## 6 — Content USIS-005 must CREATE (no canonical predecessor)

| USIS-005 artifact | Home | Realizes / references |
|---|---|---|
| Theory / Ontology / Taxonomy Foundation | `15-…/01-THEORY/` (recommended) | **Implements** USIS-004 tiers 6/7/8; **references** U24/Part 19 ontology, USIS-002 universes, USIS-001 laws; discharges USIS-011 obl 11/12 at foundation level |

## 7 — Must-never-duplicate register (LAW USIS-02)

| Target | Canonical home (REFERENCE only) | Duplication risk if forked |
|---|---|---|
| Repository structure | `config.py` + physical tree | a competing structure registry |
| Knowledge ontology | U24 / MIP Part 19 | a competing ontology-core |
| Meta-model tiers | USIS-004 | a competing capability model |
| Registration / ID allocation | `ukb.py` + `id-ledger.json` | a second allocator |
| Certification runtime | `ukbx certify` | a second certifier |

## 8 — Reuse-first conclusion

All infrastructure, laws, universes, meta-model tiers, and the repository
structure are reusable/referenceable. The **only** genuinely-new content is the
Theory/Ontology/Taxonomy foundation. **No duplication is required or permitted.**
