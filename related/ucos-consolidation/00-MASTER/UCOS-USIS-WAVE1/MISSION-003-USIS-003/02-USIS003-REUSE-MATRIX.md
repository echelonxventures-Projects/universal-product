# 02 — USIS-003 REUSE MATRIX

**Principle:** Reuse before creation · Knowledge Once · Zero Duplicates (LAW
USIS-02). USIS-003 (Universal Science Catalog) creates **only** the science-catalog
content with no canonical predecessor; every engine, registry, gate, universe, and
governance instrument below is **reused as authority**, never re-implemented.

Legend — **REUSE** (invoke/consume as-is) · **EXTEND** (append-only into an
existing open structure) · **REFERENCE** (link to a canonical home, never fork) ·
**CREATE** (genuinely new USIS content) · **PREREQUISITE** (must exist first).

---

## 1 — Engines & tooling (all REUSE)

| Asset | Location | USIS-003 disposition |
|---|---|---|
| `ukb.py` | `00-BOOK/tools/` | **REUSE** — sole ID/registration/classification/graph authority |
| `ukbx.py` | `00-BOOK/tools/` | **REUSE** — twin/portal/certify runtime |
| `register.sh` | `00-BOOK/tools/` | **REUSE** — 10-phase transaction + `--guard` convergence gate |
| `config.py` | `00-BOOK/tools/` | **REUSE** — `^15-…/ → USIS/USIS/VOL-024` already routes `07-SCIENCES/`; no edit expected (non-chained, program-root parenting) |

## 2 — Universal registries & DATA projections (EXTEND via reused mechanism)

| Asset | USIS-003 disposition |
|---|---|
| UNIVERSAL-ARTIFACT-REGISTRY | **EXTEND** — append rows for the Science-Catalog artifact |
| UNIVERSAL-PAGE-REGISTRY / `id-ledger.json` | **EXTEND** — append-only page allocation (cursor 9139→) |
| KNOWLEDGE-GRAPH-REGISTRY | **EXTEND** — new edges (Depends-On USIS-002/USIS-004; science→`USIS-U-SCI`; science↔cross-link universes); acyclic |
| VOLUME-REGISTRY | **REUSE** — VOL-024; **no new volume** |
| CHANGE-VERSION-LINEAGE / CERTIFICATION registries | **EXTEND** — change/version + certification rows for the new artifact |

## 3 — Constitutional / prior USIS assets

| Asset | Disposition | Note |
|---|---|---|
| USIS-001 (LAW USIS-00/01/02/05/08/09) | **REFERENCE** | governing determination + constitutional anchor |
| USIS-002 Universe Catalog — universe `USIS-U-SCI` | **REFERENCE** (Depends-On) | USIS-003's owning universe; established, ACTIVE |
| **USIS-004 Universal Capability Meta-Model** | **PREREQUISITE** (Depends-On) | **NOT yet implemented** — the 24-tier Science→…→Lifecycle chain USIS-003 conforms to (LAW USIS-08). Must be reused/referenced but does not exist. |
| Cross-linked universes (`USIS-U-INT/ANL/LRN/DAT/KNW/DEC/…`) | **REFERENCE** | science rows cross-link, never re-home (LAW USIS-02) |
| MIP universes (U16/U24/U25/U26/U28) + Parts 19/20/21 | **REFERENCE** | realization anchors via the owning universes |

## 4 — Governance, validation, certification (all REUSE)

| Asset | Disposition |
|---|---|
| UCIC-001 (15-stage fail-closed) | **REUSE** — execution model |
| SCIENCE_INTELLIGENCE lifecycle (USIS-008) | **REUSE** — DEFINED→…→CERTIFIED |
| GOV-001-T3 (No-Orphan) · GOV-002 (traceability) · REG-AUTO-001 | **REUSE** — governance gates |
| `ukb validate`/`enforce`, `ukbx validate`/`twin --check`/`certify`, `register.sh --guard` | **REUSE** — validation/certification/determinism gates |
| USIS-011 proof obligations (esp. 2/3 no-dup, 4 orphan, 5 acyclic, **13 capability closure**, **14 dependency closure**, 10 registry closure, 18 byte-stable) | **REUSE** — fail-closed acceptance predicates |
| CI gates (`ucos-registration-gate.yml`, `ec1-ci.yml`, `determinism.yml`) | **REUSE** — independent backstop |

## 5 — Content USIS-003 must CREATE (no canonical predecessor)

| USIS-003 artifact | Corpus home | Realizes / references |
|---|---|---|
| Universal Science Catalog (30 seed disciplines) | `15-…/07-SCIENCES/` (USIS-005 §2/§3) | owner `USIS-U-SCI`; conforms to USIS-004 meta-model; cross-links to intelligence/analytics/learning universes (REFERENCE) |

## 6 — Reuse-First conclusion

Every capability USIS-003 needs is reusable **except one**: its declared
meta-model dependency **USIS-004 does not exist**. Reuse-First cannot be satisfied
for the meta-model tier because the canonical instance has not been created. This
is not a duplication risk — it is a **missing prerequisite** (see `03`/`05`).
