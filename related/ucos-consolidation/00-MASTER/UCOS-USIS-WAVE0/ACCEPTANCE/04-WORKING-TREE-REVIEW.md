# 04 — Working-Tree Review

| Field | Value |
|-------|-------|
| ARTIFACT ID | WAVE0-ACC-04 (Working-Tree Review) |
| MISSION | Wave-0 Acceptance / Baseline Certification |
| STATUS | COMPLETE · AUTHORITY = NONE (DERIVED) · READ-ONLY |
| BASELINE | HEAD `57d91b7` = 995 committed artifacts; working tree at this mission = 52 changed paths |

> **Purpose.** Classify every modified/new path and separate genuine Wave-0 output from pre-existing uncommitted drift. **Key fact:** the first `ukb validate` of the execution session (before any edit) already reported **1001** artifacts vs HEAD's **995** → the working tree carried **+6 pre-existing uncommitted drift before Wave 0 began.** Wave-0's net artifact contribution is **+1** (`UCOS-USIS-000001`).

---

## 1 — Wave-0 output (this program's genuine changes)

| Path | Class | Verdict |
|------|-------|:-------:|
| `00-BOOK/tools/config.py` (M) | Tooling / Canonical config | Wave-0 (Phase 0.3) — append-only USIS family + `VOL-023` **(defective volume id → B1)** |
| `15-UNIVERSAL-SCIENCE-INTELLIGENCE/USIS-GOV-000-…md` (??) | Canonical corpus | Wave-0 (Phase 0.4) — registered root, classified USIS, homed. **Carries `UCOS-VOLUME: VOL-023` → must become `VOL-024` (B1).** |
| `00-BOOK/PORTAL/UCOS-USIS-000001.md` (??) | Generated (portal) | Wave-0 — deterministic portal page for the USIS root |
| `00-MASTER/UCOS-USIS-WAVE0/**` (??) | Governance / Evidence | Wave-0 — Phase 0.1 determination, FREEZE-C4 engine+package, completion, this ACCEPTANCE set (operational memory; excluded from registration gate) |
| `00-MASTER/EIP-018D/**` (??) | Governance | This session's prior reconciliation package (operational memory) |
| `00-BOOK/DATA/{artifacts,relationships,id-ledger,control-tower,change-ledger,certification,volumes}.json` (M) | Generated (registry) | Wave-0 regeneration deltas (USIS node/edges/id) **+ pre-existing drift merged** — `volumes.json` carries **B1 duplicate `VOL-023`** |
| `00-BOOK/REGISTRIES/{UNIVERSAL-ARTIFACT,UNIVERSAL-PAGE,VOLUME,KNOWLEDGE-GRAPH,CERTIFICATION,CHANGE-VERSION-LINEAGE}-REGISTRY.md` (M) | Generated (registry) | Regenerated; `VOLUME-REGISTRY.md` shows the **B1 duplicate `VOL-023`** (4 rows) |
| `00-BOOK/CONTROL-TOWER/PROGRAM-CONTROL-TOWER.md` (M) | Generated | Regenerated control-tower projection |
| `00-BOOK/PORTAL/{index,UCOS-IDX-000001,UCOS-ARCH-000024,UCOS-SEC-000001,UCOS-SVC-000018}.md` (M) | Generated (portal) | Regenerated (USIS edges touch SEC-000001/SVC-000018; index refresh) |

## 2 — Pre-existing uncommitted drift (NOT Wave-0 output; present at session start)

| Path | Class | Verdict |
|------|-------|:-------:|
| `00-BOOK/PORTAL/UCOS-REF-000007…015.md` (??) | Generated (portal) | **Pre-existing** — portal pages for `04-REFERENCE` reference files; registered before Wave 0 (working tree was 1001 at session start). Accounts for the +6 delta vs HEAD. |
| `00-BOOK/DATA` REF registrations (within M files) | Generated (registry) | **Pre-existing** REG-AUTO drift (`UCOS-REF-000007…015`) |
| `04-REFERENCE/*.docx` (5, ??) | Documentation (reference corpus) | **Pre-existing** untracked reference documents |
| `00-MASTER/UAKOS-PHASE-001A-R1 … 007`, `UCOS-CRAT-001`, `UCOS-CVER-001`, `UCOS-EKAP-001`, `UCOS-USIS-001` (??) | Governance / Evidence (operational memory) | **Pre-existing** untracked operational-memory packages (EKAP/CVER/CRAT/USIS specs + UAKOS phases) |

## 3 — Anomaly classification (as requested)

| Category | Finding |
|----------|---------|
| **Unexpected modifications** | None outside the expected Wave-0 + REG-AUTO regeneration set. No source/engine/frozen path (`engine/**`, `platform/**`, `data/**`, `service/**`, `application/**`, `infrastructure/**`, `00-SOURCE/**`, `99-FREEZE/**`) modified. |
| **Accidental edits** | None detected. `config.py` change is confined to append-only USIS additions. |
| **Duplicate generation** | **YES — B1: duplicate `VOL-023`** in `volumes.json` (25 count) and `VOLUME-REGISTRY.md` (4 rows). Blocking. |
| **Stale artifacts** | None attributable to Wave 0. (Advisory OBS-1 stale dashboard is a pre-existing projection.) |
| **Orphan artifacts** | None — `ukb enforce` 0 unclassified/unregistered; USIS root parented + depended (acyclic). |
| **Missing artifacts** | None required by Wave 0 (per-area USIS-001…021 are Wave-1, correctly absent). |
| **Collision** | **YES — B1: `VOL-023` claimed by both SECURITY-GOVERNANCE (SEC, pre-existing) and USIS (Wave-0).** |

## 4 — Pre-existing observations (out of Wave-0 scope; for separate governance)

- **SECURITY volume split:** `config.py` defines `VOL-011 = SECURITY/SEC`, yet the metadata auto-discovery homed `14-SECURITY/SECURITY-GOV-*` artifacts to a separate discovered `VOL-023 = SECURITY-GOVERNANCE/SEC`. This split predates Wave 0 (present at HEAD) and is a pre-existing anomaly, not caused by this program. It is noted for separate reconciliation; it does not change the B1 remediation (USIS → VOL-024).
- **Commit hygiene:** committing the working tree as-is would bundle Wave-0 output with pre-existing REG-AUTO drift and untracked operational-memory packages in one commit. Recommend the atomic Wave-0 commit be scoped to Wave-0 paths (config.py, `15-…/`, USIS portal page, and the Wave-0-attributable registry deltas) once B1 is fixed — separate from the pre-existing drift.

## 5 — Determination

Working-tree review: **one blocking defect (B1 duplicate/collision `VOL-023`)**; all other Wave-0 paths are correctly classified, No-Orphan clean, and confined to permitted surfaces. Pre-existing drift is identified and separated. **REJECT** pending B1.

*END — 04 · WORKING-TREE REVIEW · B1 BLOCKING · AUTHORITY = NONE (DERIVED).*
