# 02 — USIS-001 COMMIT EVIDENCE

**Repository-derived evidence of the atomic USIS-001 baseline commit.**

---

## 1 — Commit identity

| Field | Value |
|---|---|
| Commit SHA | `07e0de4df3c4536c9f5ce5dbadd09dcd1423a950` |
| Parent SHA | `2bf53124b1c441262219d1b59f179ead8f946f49` (Wave-0 baseline) |
| Branch | `governance-reconciliation` |
| Subject | `USIS-001: register Universal Science & Intelligence Constitution` |
| Tag | none (STOP condition — no tag) |
| Pushed | no (STOP condition — no push) |

## 2 — Committed file set (18 files — exactly the accepted scope)

| Status | Path |
|:--:|---|
| A | `15-UNIVERSAL-SCIENCE-INTELLIGENCE/00-CONSTITUTION/USIS-001-UNIVERSAL-SCIENCE-INTELLIGENCE-CONSTITUTION.md` |
| A | `00-BOOK/PORTAL/UCOS-USIS-000002.md` |
| M | `00-BOOK/PORTAL/UCOS-USIS-000001.md` |
| M | `00-BOOK/PORTAL/index.md` |
| M | `00-BOOK/CONTROL-TOWER/PROGRAM-CONTROL-TOWER.md` |
| M | `00-BOOK/DATA/artifacts.json` |
| M | `00-BOOK/DATA/certification.json` |
| M | `00-BOOK/DATA/change-ledger.json` |
| M | `00-BOOK/DATA/control-tower.json` |
| M | `00-BOOK/DATA/id-ledger.json` |
| M | `00-BOOK/DATA/relationships.json` |
| M | `00-BOOK/DATA/volumes.json` |
| M | `00-BOOK/REGISTRIES/CERTIFICATION-REGISTRY.md` |
| M | `00-BOOK/REGISTRIES/CHANGE-VERSION-LINEAGE-REGISTRY.md` |
| M | `00-BOOK/REGISTRIES/KNOWLEDGE-GRAPH-REGISTRY.md` |
| M | `00-BOOK/REGISTRIES/UNIVERSAL-ARTIFACT-REGISTRY.md` |
| M | `00-BOOK/REGISTRIES/UNIVERSAL-PAGE-REGISTRY.md` |
| M | `00-BOOK/REGISTRIES/VOLUME-REGISTRY.md` |

`git show --stat`: **18 files changed, 23 118 insertions(+), 22 841 deletions(-)** (deterministic registry regenerations account for the large line churn).

**Counts:** staged file count at commit = **18**; committed file count = **18**; post-commit staged = **0**.

## 3 — Scope isolation (nothing extraneous committed)

- `git diff --cached --name-only | grep 00-MASTER/` → **NONE**. No operational-memory artifact was committed.
- `config.py` and all frozen paths (`engine/ platform/ 00-SOURCE/ 99-FREEZE/ 00-BOOK/tools/ 00-BOOK/VOLUMES/`) — **not** in the commit.
- Post-commit `git status` = **18 untracked only**, all under `00-MASTER/` (operational memory; excluded from the registration gate). No modified/staged residue.

## 4 — Pre-commit gate

The project's managed pre-commit hook (ruff lint + format check over engine + platform via `.ec1-venv`) ran and reported **`All checks passed!` / `pre-commit: OK`**. The hook was **not** bypassed. The USIS-001 change touches only Markdown/JSON under `00-BOOK/` and `15-…/`, so no source formatting was affected.

## 5 — Post-commit gate

`00-BOOK/tools/register.sh --guard`:
```
TRANSACTION COMPLETE — every artifact on disk is registered, classified, validated, and synchronized.
-- Guard: checking committed synchronized state for drift
Guard PASSED — repository, registry, control tower, twin, and portal are in sync.
```
Exit **0**. The registration drift that existed pre-commit is fully resolved by this commit.

## 6 — Determinism (unchanged across the commit boundary)

Guard-scope raw byte hash (`00-BOOK/{DATA/*.json, REGISTRIES/*.md, CONTROL-TOWER/*.md, PORTAL/*.md}`):
`1dee678abd0e69c5d04823b7ac66c7100397fcc55627858efcca72381d5e9106` — **identical pre-commit and post-commit**, and stable across `register.sh` re-runs (write-if-changed regeneration; append-only ledger allocates no new IDs).
