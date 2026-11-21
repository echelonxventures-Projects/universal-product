# EVO-USIS-W3-REGISTRY-001 · 02 — Repository Structure Report

| Field | Value |
|-------|-------|
| PROGRAMME | EVO-USIS-W3-REGISTRY-001 (S-02) |
| PHASE | 1 — Canonical Home Determination |
| RESULT | PASS — 0 structural variance; single canonical home |

## Canonical home determination

| Item | Determination | Authority |
|------|---------------|-----------|
| Artifact | `USIS-021` — Universal Science & Intelligence Master Registry | structure spec `05` §3 (`USIS-021 · MASTER-REGISTRY · 04`) |
| Home path | `15-UNIVERSAL-SCIENCE-INTELLIGENCE/04-REGISTRIES/USIS-021-UNIVERSAL-SCIENCE-INTELLIGENCE-MASTER-REGISTRY.md` | structure spec §2 (area 04) + §3 (naming pattern) |
| Owning scope | The USIS master-registry surface under `04-REGISTRIES/`, homed beneath root anchor `USIS-REGISTRY-ROOT` | USIS-REG-000 Part B |
| Classification | `USIS` / `VOL-024` via path rule `r"^15-UNIVERSAL-SCIENCE-INTELLIGENCE/"` (config.py:275) + mandatory front-matter (§4) | REG-AUTO-001 3-layer mechanism |
| Parent | `USIS-GOV-000` (non-chained; `PROGRAM_ROOTS["USIS"]`) | config.py:671 |

## Structural variance check

- **New area created:** 0 — `04-REGISTRIES/` already materialized by S-01.
- **New file created:** 1 — `USIS-021-…-MASTER-REGISTRY.md`.
- **`config.py` edit:** 0 — path rule + metadata self-classification + non-chained parent already suffice (matches S-01 precedent; DP-03 additive-only honoured).
- **Writes to frozen streams** (`engine/**`, `platform/**`, `00-SOURCE/**`, `99-FREEZE/**`, `00-CEP/**`): **0**.
- **Duplicate home / renamed / renumbered artifact:** 0.

## Naming conformance

`USIS-021-UNIVERSAL-SCIENCE-INTELLIGENCE-MASTER-REGISTRY.md` conforms to the program pattern (cf. `USIS-001-UNIVERSAL-SCIENCE-INTELLIGENCE-CONSTITUTION`, `USIS-018-…-FOUNDATION-FREEZE-DETERMINATION`). Seq `021` matches the structure-spec founding sequence.

## Determination

**PHASE 1 PASS.** Exactly one canonical home; one additive file; zero structural variance; zero frozen-path writes; zero `config.py` edit.
