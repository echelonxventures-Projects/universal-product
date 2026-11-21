# 02 — USIS-002 COMMIT EVIDENCE

Repository-derived evidence of the single atomic commit that establishes the
USIS-002 canonical baseline.

---

## 1 — Commit identity

| Field | Value |
|---|---|
| Commit SHA | `8db7d522e40f0e0a37d10d27f43d913b2f871dd5` |
| Short SHA | `8db7d52` |
| Parent SHA | `07e0de4df3c4536c9f5ce5dbadd09dcd1423a950` (`07e0de4`) |
| Parent subject | `USIS-001: register Universal Science & Intelligence Constitution` |
| Branch | `governance-reconciliation` |
| Subject | `USIS-002: register Universal Science & Intelligence Universe Catalog` |
| Trailers | none (single subject line; no invented metadata) |

## 2 — Change statistics (from `git show --stat`)

| Metric | Value |
|---|---|
| Staged file count (pre-commit) | **19** |
| Committed file count | **19** |
| Staged file count (post-commit) | **0** |
| Files created | 2 (`00-BOOK/PORTAL/UCOS-USIS-000003.md`, `15-…/06-UNIVERSES/USIS-002-UNIVERSE-CATALOG.md`) |
| Files modified | 17 (regenerated projections) |
| Insertions / deletions | 23186 / 22848 |

The large insertion/deletion counts are the deterministic re-serialization of
`relationships.json` and `KNOWLEDGE-GRAPH-REGISTRY.md` (the same behavior recorded
for the USIS-001 baseline commit); net semantic change is the addition of one
artifact and its 8 edges.

## 3 — Committed file manifest (19)

```
00-BOOK/CONTROL-TOWER/PROGRAM-CONTROL-TOWER.md
00-BOOK/DATA/artifacts.json
00-BOOK/DATA/certification.json
00-BOOK/DATA/change-ledger.json
00-BOOK/DATA/control-tower.json
00-BOOK/DATA/id-ledger.json
00-BOOK/DATA/relationships.json
00-BOOK/DATA/volumes.json
00-BOOK/PORTAL/UCOS-USIS-000001.md
00-BOOK/PORTAL/UCOS-USIS-000002.md
00-BOOK/PORTAL/UCOS-USIS-000003.md        (new)
00-BOOK/PORTAL/index.md
00-BOOK/REGISTRIES/CERTIFICATION-REGISTRY.md
00-BOOK/REGISTRIES/CHANGE-VERSION-LINEAGE-REGISTRY.md
00-BOOK/REGISTRIES/KNOWLEDGE-GRAPH-REGISTRY.md
00-BOOK/REGISTRIES/UNIVERSAL-ARTIFACT-REGISTRY.md
00-BOOK/REGISTRIES/UNIVERSAL-PAGE-REGISTRY.md
00-BOOK/REGISTRIES/VOLUME-REGISTRY.md
15-UNIVERSAL-SCIENCE-INTELLIGENCE/06-UNIVERSES/USIS-002-UNIVERSE-CATALOG.md   (new)
```

## 4 — Pre-commit hook

The repository pre-commit gate ran and **passed** (not skipped):

```
== pre-commit: ruff lint + format check (engine + platform)
All checks passed!
884 files already formatted
✓ pre-commit: OK
```

## 5 — Post-commit verification ledger

| Check | Result | Evidence |
|---|:--:|---|
| Commit created successfully | ✅ | `8db7d52` present; `git log` shows it atop `07e0de4` |
| Repository reflects committed USIS-002 baseline | ✅ | catalog + projections committed; `git show --stat` = 19 files |
| Staged changes empty | ✅ | `git diff --cached --name-only` = 0 |
| Working tree clean (excluding operational memory) | ✅ | non-`00-MASTER` `git status` empty |
| `register.sh --guard` PASS | ✅ | **exit 0** — "Guard PASSED — repository, registry, control tower, twin, and portal are in sync." |
| Deterministic regeneration unchanged | ✅ | guard-scope SHA-256 `b406563c21af1316fe34ab6414a0e2c45822093ec7e312187e3e59680a113dbd` |
| Repository synchronized | ✅ | `ukb enforce` 1004/1004; 0 unregistered/unclassified/invalid |
| Frozen paths / `config.py` untouched | ✅ | `git diff` empty on frozen/governed paths |

## 6 — Determination

The atomic commit is created, verified, and drift-free. Guard transitions from the
pre-commit exit-3 (intentionally uncommitted) to **exit 0 (in sync)** — the defining
signal that the USIS-002 baseline is established. Baseline verdict in `03`.
