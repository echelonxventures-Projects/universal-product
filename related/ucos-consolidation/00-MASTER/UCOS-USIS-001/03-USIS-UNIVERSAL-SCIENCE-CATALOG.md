# USIS-003 — Universal Science Catalog

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-003 (Universal Science Catalog — seed registration) |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| STATUS | PROPOSED · AWAITING RATIFICATION · PRE-WAVE-0 |
| OWNING UNIVERSE | USIS-U-SCI (Universal Science) |
| DEPENDS-ON | USIS-002 · USIS-004 (meta-model) · LAW USIS-00 |
| NATURE | **Open registry seed.** Sciences below are initial members of an unbounded set; unlimited future disciplines register without redesign (LAW USIS-00 C-00.4). |

> **Purpose.** Establish constitutional ownership for all scientific disciplines under the Universal Science Universe, each conforming to the Universal Capability Meta-Model (USIS-004) and LAW Ω∞-000.

---

## 1 — Science registry model

Each science is a registry row: `{ id: USIS-SCI-<NAME>, home: 06-DOMAINS/SCIENCE/<NAME>/, universe: USIS-U-SCI (+ cross-links), owner, status, sub-disciplines[] }`.
- Each science owns its **discipline → domain → sub-domain → capability** tree (USIS-004).
- Sciences cross-link to intelligence/analytics/learning universes rather than duplicating them (LAW USIS-02).
- The set is **open**: `USIS-SCI-FUTURE-*` and the Unknown Sciences Universe (USIS-U-UNK) are permanent registration-only slots.

## 2 — Seed scientific disciplines (30 registered members)

| # | Science | id | Primary cross-links |
|---|---------|-----|--------------------|
| 1 | Mathematics | USIS-SCI-MATH | U-ALG, U-MDL |
| 2 | Statistics | USIS-SCI-STAT | U-ANL, U-PRD |
| 3 | Computer Science | USIS-SCI-CS | U-ALG, U-INT |
| 4 | Data Science | USIS-SCI-DATA | U-DAT, U-ANL |
| 5 | Information Science | USIS-SCI-INFO | U-KNW |
| 6 | Knowledge Science | USIS-SCI-KNOW | U-KNW |
| 7 | Decision Science | USIS-SCI-DEC | U-DEC |
| 8 | Systems Science | USIS-SCI-SYS | U-SIM, U-AUT |
| 9 | Complexity Science | USIS-SCI-CPLX | U-SIM, U-MAS |
| 10 | Computational Science | USIS-SCI-COMP | U-ALG, U-SIM |
| 11 | Learning Science | USIS-SCI-LEARN | U-LRN |
| 12 | Behavioral Science | USIS-SCI-BEH | U-BEH |
| 13 | Cognitive Science | USIS-SCI-COG | U-COG |
| 14 | Psychology | USIS-SCI-PSY | U-PSY, U-HUM |
| 15 | Neuroscience | USIS-SCI-NEURO | U-COG, U-HUM |
| 16 | Biology | USIS-SCI-BIO | U-SCI |
| 17 | Chemistry | USIS-SCI-CHEM | U-SCI |
| 18 | Physics | USIS-SCI-PHYS | U-SCI, U-SIM |
| 19 | Astronomy | USIS-SCI-ASTRO | U-SCI |
| 20 | Medicine | USIS-SCI-MED | U-HUM, U-ANL |
| 21 | Environmental Science | USIS-SCI-ENV | U-SCI |
| 22 | Engineering Sciences | USIS-SCI-ENG | U-SCI, U-AUT |
| 23 | Economics | USIS-SCI-ECON | U-ANL, U-DEC |
| 24 | Sociology | USIS-SCI-SOC | U-BEH |
| 25 | Anthropology | USIS-SCI-ANTH | U-HUM |
| 26 | Political Science | USIS-SCI-POL | U-DEC |
| 27 | Linguistics | USIS-SCI-LING | U-INT, U-KNW |
| 28 | Civilization Sciences | USIS-SCI-CIV | U-SCI |
| 29 | Future Sciences | USIS-SCI-FUTURE-* | USIS-U-FUT (open) |
| 30 | Unknown Future Sciences | USIS-SCI-UNKNOWN-* | USIS-U-UNK (open) |

## 3 — Extensibility guarantee

Adding a science = append a registry row + author its canonical-home artifact with USIS classification metadata (USIS-005 §4) + declare its discipline tree per the meta-model. **No engine, schema, ontology-core, or architecture change is required** (LAW USIS-00). There is no compiled maximum count of sciences, disciplines, domains, or capabilities. Interdisciplinary sciences register as new members with cross-links (e.g. Computational Biology = new row cross-linking BIO + COMP), never as duplicates.
