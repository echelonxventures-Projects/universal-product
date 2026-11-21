# 01 — REPOSITORY AUTHORITY INVENTORY

> **Program:** Implementation Authority Program (IAP)
> **Mission:** IAC-001A — Repository Authority Inventory Certification
> **Version:** 1.0 · **Mode:** READ-ONLY · **Authority:** Repository Truth
> **Baseline:** HEAD `836475c` (branch `governance-reconciliation`)
> **Date:** 2026-07-24
> **Scope note:** This mission identifies **what is authoritative and what is derived**. It does **not** determine implementation readiness or architectural completeness.

---

## 1. Purpose

Produce the authoritative inventory of everything that constitutes **Repository Truth** for implementation, and classify every significant artifact family into exactly one authority category using **repository evidence only**.

## 2. The authority mechanism (decisive, self-declared by the repository)

Authority in this repository is a **pure function of the tracked, un-ignored corpus**. This is not inferred — it is written policy:

- `.gitignore` repeatedly invokes **GOV-005 §5.3** to declare deterministically re-derivable engine output as **NON-ARTIFACTS "bounded by the ignore authority"** (paraphrased; exact text in `.gitignore`).
- Commit `a091722` (**EAC-001** — "activate certified constitutional baseline") fixes the admission scope: **ADMIT** root determinations, `00-MASTER` program registers + authored engines, regenerated `00-BOOK` canonical projections, portal pages, `04-REFERENCE`; **EXCLUDE** engine JSON state + `00-MASTER` program execution evidence as re-derivable **NON-ARTIFACTS**.
- `00-MASTER/RTR-001/05-FINAL-DETERMINATION.md` independently rules that `closure.json` is *"authoritative machine state (non-authoritative for governance)"* and that the `ukb`/`ukbx` gates are authoritative for committed-corpus integrity.

**Rule applied throughout this inventory:**

| Signal | Authority consequence |
|---|---|
| Git-tracked **and** un-ignored + authored source of truth | Canonical Authority |
| Git-tracked, but produced by an engine/registration transaction | Derived / Generated-but-registered Authority |
| Gitignored, deterministically re-derivable engine output | Generated Artifact — **NON-AUTHORITATIVE** |
| Gitignored per-clone/runtime/build transient | Temporary / External — **NON-AUTHORITATIVE** |

## 3. Repository scale (measured)

- Total git-tracked files: **4,051**
- Tracked-file distribution (top families): `00-BOOK` 1,204 · `platform` 554 · `00-MASTER` 445 · `engine` 372 · `service` 281 · `data` 256 · `infrastructure` 244 · `application` 233 · `02-MASTER` 79 · `00-CEP` 48.

## 4. Authority categories (this mission's taxonomy)

1. **Canonical Authority** — authored source of truth; tracked; the thing implementation must conform to.
2. **Derived Authority** — tracked determinations/state derived read-only from canonical truth (carry derived, not originating, authority).
3. **Generated Artifact** — machine output; either (a) tracked-and-registered projection (SoT = engine + registration) or (b) gitignored re-derivable output (non-authoritative).
4. **Historical Artifact** — superseded/prior-run material retained for record.
5. **Reference Evidence** — source/reference documents and registered evidence ledgers.
6. **Temporary Artifact** — per-run/per-clone transients (gitignored).
7. **External Evidence** — out-of-corpus signals (e.g., DR-RAT-11 finality act; per-clone runtime telemetry).

## 5. Inventory summary (families → category)

| # | Location / family | Type | Tracked | Gitignored | Generated | Impl. Authority | Evidence-only | Category |
|---|---|---|---|---|---|---|---|---|
| 1 | `00-CEP/CEP-000..010` | Constitutions | Yes | No | No | **Yes** | No | Canonical |
| 2 | `03-CATALOGS/` (7 canonical catalogs) | Catalogs | Yes | No | No | **Yes** | No | Canonical |
| 3 | `04-REFERENCE/*REFERENCE*ARCHITECTURE*.md` (7 REF constitutions) | Reference constitutions | Yes | No | No | **Yes** | No | Canonical |
| 4 | `04-REFERENCE/*.docx` + `ARCHITECTURAL-SOURCES/` | Source documents | Yes | No | No | No | Yes | Reference Evidence |
| 5 | `15-UNIVERSAL-SCIENCE-INTELLIGENCE/` (USIS-001/002/003/004 + USIS-GOV-000) | Universe/constitution (canonical home) | Yes | No | No | **Yes** | No | Canonical |
| 6 | `00-MASTER/UCOS-USIS-001/` | USIS program authoring | Yes | No | No | **Yes** | No | Canonical |
| 7 | `00-BOOK/SCHEMAS/*.schema.json` | Schemas | Yes | No | No | **Yes** | No | Canonical |
| 8 | `engine/**/*.py` (372) incl. `closure_engine.py`, `phase2/3_engine.py`, `engine/knowledge/seed.py` | Engines (authored code) | Yes | No | No | **Yes** | No | Canonical |
| 9 | `data/_evidence/**` (123 json, `UCOS-DATA-*`) | Certification evidence (registered family) | Yes | No | Yes (engine) | No | Yes | Reference Evidence (registered/canonical record) |
| 10 | `00-BOOK/DATA/*.json` (artifacts, certification, twin, control-tower, volumes, …) | Canonical projections | Yes | No | **Yes** | No (projection) | Partly | Generated-but-registered / Derived |
| 11 | `00-BOOK/REGISTRIES/*.md` (CERTIFICATION, VOLUME, UNIVERSAL-ARTIFACT, UNIVERSAL-PAGE, KNOWLEDGE-GRAPH, CHANGE-VERSION-LINEAGE) | Registries (projections) | Yes | No | **Yes** | No (projection) | No | Generated-but-registered / Derived |
| 12 | `00-BOOK/DATA/twin.json`, `infrastructure/_evidence/**/twin-sync.json`, twin certification md | Digital Twin artifacts | Yes | No | Yes (engine) | No | Yes | Derived / Reference Evidence |
| 13 | `00-MASTER/EIP-018D/*` | Derived determinations (self-declared `AUTHORITY = NONE`) | Yes | No | No | No | No | Derived Authority |
| 14 | `00-MASTER/RTR-001/*`, root `01..11-*.md` prior-audit reports | Determinations / audit reports | Yes | No | No | No | No | Derived Authority / Historical |
| 15 | `00-MASTER/STATE/mcs-state.json` (+ schema) | MCP operational state | Yes | No | Yes (MCP) | No | No | Derived (operational state) |
| 16 | `00-MASTER/UAKOS-CLOSURE-002/{closure,phase2,phase3}.json` | Engine JSON state | No | **Yes** | **Yes** | **No** | No | **Generated — NON-AUTHORITATIVE** |
| 17 | `00-MASTER/UAKOS-CLOSURE-002/NN-*.md` (incl. registers 20/22/31/37/38/40) | Numbered engine reports/registers | No | **Yes** | **Yes** | **No** | No | **Generated — NON-AUTHORITATIVE** |
| 18 | `00-MASTER/UAKOS-CLOSURE-002/{closure,phase2,phase3}_engine.py` + README/CHARTER/PLAN/CONTRACT | Authored engine + charter | Yes | No | No | **Yes** | No | Canonical (SoT of #16/#17) |
| 19 | `/knowledge/` (repo-root store) | Generated knowledge store | No | **Yes** | **Yes** | No | No | **Generated — NON-AUTHORITATIVE** (SoT = `engine/knowledge/seed.py`) |
| 20 | `determinism-evidence/`, `00-MASTER/**/evidence/`, `provenance.json`, `10-UNIVERSAL-GAP-DEPENDENCY-GRAPH.json` | Program execution evidence / engine state | No | **Yes** | **Yes** | **No** | No | **Generated — NON-AUTHORITATIVE** |
| 21 | `.runtime/` | Governance runtime telemetry (per-clone) | No | **Yes** | **Yes** | **No** | No | Temporary / External |
| 22 | `.register.lock`, `__pycache__/`, `*.pyc`, `.ec1-venv/`, `build/`, `dist/`, `*.egg-info/`, `.pytest_cache/`, `.ruff_cache/`, `.coverage`, `coverage.xml`, `~$*` | Build/test/office transients | No | **Yes** | **Yes** | **No** | No | Temporary |
| 23 | `intelligence/die/` | Unverified orphan (excluded from RC-1 baseline) | No | **Yes** | n/a | **No** | No | Temporary / Quarantined |

Detailed per-category breakdowns follow in `02`–`05`; the consolidated field matrix is `06`; the determination is `07`.

---
*End of 01-REPOSITORY-AUTHORITY-INVENTORY.md*
