# USIS-003 — Universal Science Catalog

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-003 (Universal Science Catalog — registered corpus instantiation) |
| UCOS-PROGRAM | USIS |
| UCOS-CATEGORY | USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| MISSION | Wave 1 · Mission 3 — establish the constitutional Universal Science Catalog of USIS |
| CLASSIFICATION | Constitutional Registry — the canonical catalog of scientific disciplines owned by the Universal Science Universe (subordinate to USIS-001, USIS-002, USIS-004, and to LAW Ω∞-000 / MIP Parts 19/20/21) |
| STATUS | RATIFIED (PROVISIONAL / engineering-authority tier) · Wave 1 · registered |
| OWNING UNIVERSE | USIS-U-SCI (Universal Science — USIS-002 catalog row #1) |
| DEPENDS-ON | USIS-002 · USIS-004 |
| PARENT | (program family USIS — parents structurally to the USIS program root USIS-GOV-000) |
| REALIZES | LAW Ω∞-000 · MIP Part 19 (Knowledge) · Part 20 (Intelligence/Analytics) · Part 21 (Learning) · conforms to USIS-004 Universal Capability Meta-Model (LAW USIS-08) |
| GOVERNED BY | USIS-001 (LAW USIS-01/02/04/05/08/09) · USIS-004 (24-tier meta-model) · UCIC-001 · GOV-001-T3 (No-Orphan) · GOV-002 (traceability) · REG-AUTO-001 (registration) · FREEZE C4 (7-stream execution model) |
| AUTHORITY | **NONE — DERIVED.** Operationalizes the constitutional ownership conferred by USIS-001 (LAW USIS-01/02) and the Universal Science Universe established in USIS-002; conforms to the USIS-004 meta-model (LAW USIS-08). Absolute FINALIZED standing remains pending the out-of-corpus External Constituent Act (DR-RAT-11 — external, non-blocking). |
| PROVENANCE | Registered instantiation of the ratified establishment-package blueprint `00-MASTER/UCOS-USIS-001/03-USIS-UNIVERSAL-SCIENCE-CATALOG.md` (operational memory). No new knowledge is introduced; the 30 seed disciplines and the science-registry model are carried verbatim in substance. Corrections vs the blueprint: (a) STATUS raised from "PROPOSED · PRE-WAVE-0" to "RATIFIED (PROVISIONAL) · registered"; (b) VOL-024 canonical (config.py:275); (c) canonical science home resolved to `07-SCIENCES/` per USIS-005 §2/§3 (D-A), superseding the blueprint §1 `06-DOMAINS/SCIENCE/` shorthand. |
| CONFLICT RULE | Higher frozen/governing instruments prevail; this instrument is void to the extent of any conflict. Where a science cross-links an existing canonical universe/concern, the canonical home governs and this catalog holds only a reference (LAW USIS-02). |

> **Purpose.** Establish the **canonical registry of scientific disciplines** owned by the Universal Science Universe (`USIS-U-SCI`) — the third Wave-1 capability of the Substrate Foundation. This catalog enumerates the constitutional sciences as members of an **open, recursively extensible registry** (LAW USIS-00 C-00.4 / LAW USIS-09), each the **single canonical owner** of one scientific discipline, each **conforming to the Universal Capability Meta-Model** (USIS-004; LAW USIS-08), each **cross-linking** to intelligence/analytics/learning/data universes by **reference** (LAW USIS-02) rather than duplicating them. **This instrument establishes only the catalog.** It authors no individual science, no discipline universe, no capability catalog, and no per-science architecture — those are separately-authorized later (Wave-3) missions.

---

## PART A — Constitutional basis and scope

This catalog is the registered instantiation of the science-ownership mandate of USIS-001 and the Universal Science Universe established in USIS-002:

- **USIS-001 LAW USIS-01** admits *all* sciences as first-class, observer-relative disciplines under USIS.
- **USIS-002** established `USIS-U-SCI` (Universal Science) as catalog row #1 — the universe that **owns all scientific disciplines**. USIS-003 populates that ownership.
- **USIS-004 LAW USIS-08** requires every capability to conform to the 24-tier meta-model. Each science here is a **Science-tier** node (USIS-004 Part C, tier 1: `USIS-SCI-*`, parent = Universal Science Universe, closure = registry closure) and owns its downward discipline → domain → sub-domain → capability chain at its own later realization.
- **USIS-001 LAW USIS-02** binds each science that cross-links an existing canonical universe to **reference** it, never fork a competing catalog/registry.
- **USIS-001 LAW USIS-09** makes the science set **open and recursively extensible**; `USIS-SCI-FUTURE-*` and the Unknown-Sciences slot are permanent registration-only receptors; growth is append-only.

**Scope of this instrument (Wave 1 · Mission 3).** This catalog:
- creates the `15-UNIVERSAL-SCIENCE-INTELLIGENCE/07-SCIENCES/` home and this single registered catalog artifact;
- enumerates the 30 constitutional seed disciplines as registry rows owned by `USIS-U-SCI`, each conforming to the USIS-004 meta-model and cross-linking universes by reference;
- founds downward-only on `USIS-002` and `USIS-004` (Depends-On; parents to the USIS program root), introducing no upstream change and no cycle;
- authors **no** individual science architecture, discipline universe, domain, capability catalog, algorithm, model, or capability instance;
- reuses, without duplication, the existing registration/validation/certification engines (`ukb`, `ukbx`, `register.sh`), the universal registries, UCIC-001, and the governance instruments as the sole authorities.

## PART B — Science registry model (the catalog IS the science registry)

Each science is a registry row of the canonical form (blueprint §1):

```
{ id: USIS-SCI-<NAME>, home: 07-SCIENCES/<NAME>/, universe: USIS-U-SCI (+ cross-links),
  owner, status, sub-disciplines[] }
```

- **Single canonical owner (LAW USIS-05).** Each science owns exactly one scientific discipline and (when later authored) one canonical home under `07-SCIENCES/`. No two rows own the same discipline; interdisciplinary sciences register as **new** rows with cross-links (e.g. Computational Biology = BIO × COMP), never duplicates.
- **Meta-model conformance (LAW USIS-08; USIS-004).** Each science is a Science-tier node whose discipline → domain → sub-domain → capability tree conforms to the USIS-004 24-tier chain when realized. This catalog records the Science tier only; lower tiers are per-science later work.
- **Cross-links, not duplication (LAW USIS-02).** Sciences cross-link to intelligence/analytics/learning/data universes established (or to be established) elsewhere; the cross-link is a **reference** edge, never a re-home.
- **Openness / append-only (LAW USIS-09).** `USIS-SCI-FUTURE-*` and `USIS-SCI-UNKNOWN-*` (routed to `USIS-U-FUT` / `USIS-U-UNK`) are permanent open slots. Adding a science = append a row + (later) author its home; no existing row is rewritten, renumbered, or removed.
- **This catalog is the canonical Universal Science Registry.** The machine-readable registry projection is produced by the **reused** universal mechanism (`ukb build` → `00-BOOK/DATA` + `00-BOOK/REGISTRIES`); no parallel allocator, ontology, taxonomy, or competing registry is created here (LAW USIS-02).

## PART C — The 30 constitutional seed disciplines

Each row is a canonical registry member owned by `USIS-U-SCI`. `home` is the single canonical sub-home under `07-SCIENCES/` (materialized only when the science itself is later authored — **not** created by this catalog); `cross-links` are **reference** edges to other universes (LAW USIS-02).

| # | Science | id | Primary cross-links (REFERENCE only) |
|---|---------|-----|--------------------------------------|
| 1 | Mathematics | `USIS-SCI-MATH` | `USIS-U-ALG`, `USIS-U-MDL` |
| 2 | Statistics | `USIS-SCI-STAT` | `USIS-U-ANL`, `USIS-U-PRD` |
| 3 | Computer Science | `USIS-SCI-CS` | `USIS-U-ALG`, `USIS-U-INT` |
| 4 | Data Science | `USIS-SCI-DATA` | `USIS-U-DAT`, `USIS-U-ANL` |
| 5 | Information Science | `USIS-SCI-INFO` | `USIS-U-KNW` |
| 6 | Knowledge Science | `USIS-SCI-KNOW` | `USIS-U-KNW` |
| 7 | Decision Science | `USIS-SCI-DEC` | `USIS-U-DEC` |
| 8 | Systems Science | `USIS-SCI-SYS` | `USIS-U-SIM`, `USIS-U-AUT` |
| 9 | Complexity Science | `USIS-SCI-CPLX` | `USIS-U-SIM`, `USIS-U-MAS` |
| 10 | Computational Science | `USIS-SCI-COMP` | `USIS-U-ALG`, `USIS-U-SIM` |
| 11 | Learning Science | `USIS-SCI-LEARN` | `USIS-U-LRN` |
| 12 | Behavioral Science | `USIS-SCI-BEH` | `USIS-U-BEH` |
| 13 | Cognitive Science | `USIS-SCI-COG` | `USIS-U-COG` |
| 14 | Psychology | `USIS-SCI-PSY` | `USIS-U-PSY`, `USIS-U-HUM` |
| 15 | Neuroscience | `USIS-SCI-NEURO` | `USIS-U-COG`, `USIS-U-HUM` |
| 16 | Biology | `USIS-SCI-BIO` | `USIS-U-SCI` |
| 17 | Chemistry | `USIS-SCI-CHEM` | `USIS-U-SCI` |
| 18 | Physics | `USIS-SCI-PHYS` | `USIS-U-SCI`, `USIS-U-SIM` |
| 19 | Astronomy | `USIS-SCI-ASTRO` | `USIS-U-SCI` |
| 20 | Medicine | `USIS-SCI-MED` | `USIS-U-HUM`, `USIS-U-ANL` |
| 21 | Environmental Science | `USIS-SCI-ENV` | `USIS-U-SCI` |
| 22 | Engineering Sciences | `USIS-SCI-ENG` | `USIS-U-SCI`, `USIS-U-AUT` |
| 23 | Economics | `USIS-SCI-ECON` | `USIS-U-ANL`, `USIS-U-DEC` |
| 24 | Sociology | `USIS-SCI-SOC` | `USIS-U-BEH` |
| 25 | Anthropology | `USIS-SCI-ANTH` | `USIS-U-HUM` |
| 26 | Political Science | `USIS-SCI-POL` | `USIS-U-DEC` |
| 27 | Linguistics | `USIS-SCI-LING` | `USIS-U-INT`, `USIS-U-KNW` |
| 28 | Civilization Sciences | `USIS-SCI-CIV` | `USIS-U-SCI` |
| 29 | Future Sciences | `USIS-SCI-FUTURE-*` | `USIS-U-FUT` (permanent open slot) |
| 30 | Unknown Future Sciences | `USIS-SCI-UNKNOWN-*` | `USIS-U-UNK` (permanent open slot) |

**Open-slot invariant.** Rows 29–30 (`USIS-SCI-FUTURE-*`, `USIS-SCI-UNKNOWN-*`) are permanent, never closed, never removed — the constructive proof that the science set is uncapped (LAW USIS-09; USIS-011 obl. 20/21). They route to the reserved universes `USIS-U-FUT` / `USIS-U-UNK` established in USIS-002.

## PART D — Non-duplication mapping (Reuse-First, LAW USIS-02)

Every cross-link above is a **reference** to a canonical universe home; no science re-homes or forks a target. Re-homing any target violates LAW USIS-02 and fails USIS-011 obligations 2/3.

| Cross-link target | Canonical home (REFERENCE only) |
|---|---|
| `USIS-U-DAT` (Data) | `10-DATA/` + U07 (via USIS-002 row 9) |
| `USIS-U-ANL` / `USIS-U-PRD` (Analytics/Prediction) | U16 / MIP Part 20 (via USIS-002) |
| `USIS-U-INT` / `USIS-U-COG` / `USIS-U-BEH` / `USIS-U-PSY` / `USIS-U-HUM` | U25 / MIP Part 20 (via USIS-002) |
| `USIS-U-KNW` (Knowledge) | U24 / MIP Part 19 (via USIS-002) |
| `USIS-U-SIM` (Simulation) | U26 / MIP Part 25 (via USIS-002) |
| `USIS-U-LRN` (Learning) | MIP Part 21 (via USIS-002) |
| `USIS-U-ALG` / `USIS-U-MDL` / `USIS-U-DEC` / `USIS-U-AUT` / `USIS-U-MAS` | U25 (via USIS-002) |
| `USIS-U-FUT` / `USIS-U-UNK` | reserved universes (via USIS-002) |

## PART E — Directory-home determination (D-A, resolved by Repository Truth)

The blueprint `03 §1` writes `home: 06-DOMAINS/SCIENCE/<NAME>/`, while the authoritative Canonical Repository Structure Specification (USIS-005) assigns science homes to **`07-SCIENCES/`**:

- **USIS-005 §2** — "`07-SCIENCES/` # Universal Science discipline homes (`USIS-SCI-*`)"; `08-DOMAINS/` is a *distinct* area ("cross-universe domains + Human-Intelligence families").
- **USIS-005 §3** — "USIS-003 | UNIVERSAL-SCIENCE-CATALOG | Area 07"; "Per-science: `USIS-SCI-<NAME>-NNN` under `07-SCIENCES/`".

**Determination:** the canonical home for the Science Catalog and for every per-science sub-home is **`15-UNIVERSAL-SCIENCE-INTELLIGENCE/07-SCIENCES/`**. The blueprint `06-DOMAINS/SCIENCE/` phrasing is a superseded shorthand (it conflated the science area with the distinct cross-universe domain area) — the same class of resolution applied to USIS-002 (D-1).

## PART F — Constitutional invariants (fail-closed self-check; verified in USIS-011)

1. Duplicate science / catalog / registry created by USIS-003: **0** (single catalog; cross-linked universes referenced, never forked).
2. Hard-coded present-day tech in the catalog architecture: **0** (LAW USIS-04 — sciences are agnostic disciplines; concrete methods/tools are registered content in lower tiers).
3. Orphan sciences (unowned/unhomed discipline): **0** (every row owned by `USIS-U-SCI`; one home each).
4. Closed (finite-by-construction) science registry: **0** (`USIS-SCI-FUTURE-*`/`USIS-SCI-UNKNOWN-*` open; append-only).
5. USIS-003 edits to any frozen instrument: **0** (authored only under `15-…/07-SCIENCES/`).
6. Science lacking owner + meta-model conformance + (for cross-linking sciences) a reference edge: **0** (Part B/C/D complete).
7. Circular ownership / dependency cycles: **0** (Depends-On downward to USIS-002/USIS-004; cross-links are downward reference edges; recursion via sub-disciplines is a strict forest).

Any nonzero ⇒ NOT CONSTITUTIONALLY CONFORMANT.

## PART G — What this catalog intentionally does NOT do

- It authors **no** individual science (no `07-SCIENCES/<NAME>/` architecture files); science sub-homes are named here but materialized only at each science's separately-authorized mission.
- It authors **no** discipline universe, capability catalog, domain, algorithm, model, or capability instance.
- It authors **no** USIS-005 structure-realization content and begins **no** downstream science universe.
- It creates **no** parallel registry, allocator, ontology, taxonomy, or certifier; it reuses the universal mechanism and references the USIS-004 meta-model.
- It performs **no** `config.py` edit (USIS-003 is non-chained, parenting to the program root `USIS-GOV-000` and self-declaring its downward `Depends-On` edges to USIS-002 and USIS-004).

*END — USIS-003 · UNIVERSAL SCIENCE CATALOG · RATIFIED (PROVISIONAL) · AUTHORITY = NONE (DERIVED).*
