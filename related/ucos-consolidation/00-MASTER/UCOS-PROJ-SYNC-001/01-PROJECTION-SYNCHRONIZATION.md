# 01 — PROJECTION SYNCHRONIZATION

**Mission:** UCOS Ω∞ Post-Wave 0 Canonical Projection Synchronization (UCOS-PROJ-SYNC-001)
**Type:** Repository synchronization (NOT new implementation, NOT Wave 1)
**Branch:** `governance-reconciliation`
**Baseline (pre-sync) HEAD:** `0bcea68` — *Wave 0: establish USIS as first-class program (PROVISIONAL tier)*
**Convergence commit:** `2bf5312` — *REG-AUTO-001: synchronize canonical projections to Wave 0 baseline*

---

## 1. Mandate

Wave 0 was accepted (PASS) and committed atomically as `0bcea68`. That commit
**intentionally excluded** the REG-AUTO-001 projection artifacts
(`DATA/`, `REGISTRIES/`, `CONTROL-TOWER/`, `PORTAL/`) because those shared
projection files also carried pre-existing, unrelated drift. As designed,
`register.sh --guard` therefore reported projection drift. This mission resolves
that deferred synchronization by regenerating **only repository-derived
projections** from canonical repository truth.

## 2. Projection ownership model (repository evidence)

Artifact enumeration is defined in `00-BOOK/tools/ukb.py::_iter_files` /
`_repo_artifact_paths` as:

```
git ls-files --cached --others --exclude-standard
  MINUS EXCLUDE_DIR_PREFIXES  (.git/, .github/, .kiro/, 00-BOOK/tools/,
                               00-BOOK/DATA/, 00-BOOK/REGISTRIES/,
                               00-BOOK/CONTROL-TOWER/, 00-BOOK/VOLUMES/,
                               00-BOOK/PORTAL/, 00-MASTER/, MCP-001-...md)
  INTERSECT INCLUDE_EXTENSIONS (.md, .txt, .docx, .json)
```

Consequences used by this mission:

- The four projection trees (`DATA/`, `REGISTRIES/`, `CONTROL-TOWER/`, `PORTAL/`)
  are **generated outputs** — mechanically re-derived, never hand-registered.
  They are exactly the `register.sh --guard` scope.
- `00-MASTER/` is **operational memory**, excluded from the corpus scan. Mission
  reports and evidence placed there (including this document) are **not**
  registrable artifacts and cannot create projection drift.

## 3. Projections regenerated

All regeneration performed with the canonical environment
`.ec1-venv/bin/python` (Python 3.12) via the repository tooling.

| Projection tree | Files touched | Mechanism |
|---|---|---|
| `00-BOOK/DATA/` | artifacts.json, id-ledger.json, relationships.json, change-ledger.json, volumes.json, control-tower.json, certification.json | `ukb build` + `ukbx twin` + `ukbx certify` |
| `00-BOOK/REGISTRIES/` | UNIVERSAL-ARTIFACT-REGISTRY, UNIVERSAL-PAGE-REGISTRY, KNOWLEDGE-GRAPH-REGISTRY, VOLUME-REGISTRY, CHANGE-VERSION-LINEAGE-REGISTRY, CERTIFICATION-REGISTRY | `ukb build` + `ukbx certify` |
| `00-BOOK/CONTROL-TOWER/` | PROGRAM-CONTROL-TOWER.md | `ukb build` + `ukbx twin` |
| `00-BOOK/PORTAL/` | index.md + 4 updated pages + 10 new pages | `ukbx portal` |

**New navigation pages generated (10):** `UCOS-REF-000007` … `UCOS-REF-000015`,
`UCOS-USIS-000001`.
**Updated pages (4):** `UCOS-ARCH-000024`, `UCOS-IDX-000001`, `UCOS-SEC-000001`,
`UCOS-SVC-000018` (cross-reference / index refresh).

## 4. Canonical source artifacts

**No canonical source artifact was modified.** The only non-projection files
committed are five reference **source** documents that the registry now
references (see `02-REGISTRY-RECONCILIATION.md`); they are repository truth that
already existed on disk and were committed for baseline coherence, not authored
or altered here. No new knowledge was introduced.

## 5. Result

`register.sh` reports **TRANSACTION COMPLETE** and `register.sh --guard` reports
**Guard PASSED** — the four projection trees are byte-for-byte in agreement with
canonical repository truth. Detailed evidence: `03-GUARD-VALIDATION.md`,
`04-DETERMINISTIC-REGENERATION.md`.
