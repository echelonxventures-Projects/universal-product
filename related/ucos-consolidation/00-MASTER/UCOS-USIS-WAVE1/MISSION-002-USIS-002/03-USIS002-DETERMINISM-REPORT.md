# 03 — USIS-002 DETERMINISM & DRIFT-ATTRIBUTION REPORT

---

## 1 — Determinism method (reproducible)

```
find 00-BOOK/DATA 00-BOOK/REGISTRIES 00-BOOK/CONTROL-TOWER 00-BOOK/PORTAL -type f \
  | LC_ALL=C sort | xargs shasum -a 256 | shasum -a 256
```

This aggregates the entire guard-scope projection surface into a single SHA-256.
Confirmed reproducible: at the USIS-001 baseline (`07e0de4`) it independently
reproduces the recorded digest `b53f7fcb…`.

## 2 — Determinism result

| Observation | Guard-scope aggregate SHA-256 |
|---|---|
| USIS-001 baseline (`07e0de4`) | `b53f7fcb61ba125a7b61f79f291f8157ead7442c1c855a9481bdd4b042bc6f24` |
| USIS-002 — this review, run A | `b406563c21af1316fe34ab6414a0e2c45822093ec7e312187e3e59680a113dbd` |
| USIS-002 — this review, run B | `b406563c21af1316fe34ab6414a0e2c45822093ec7e312187e3e59680a113dbd` |

**DETERMINISM: PASS.** The digest evolved deterministically from the baseline once
USIS-002 registered (expected), and is **byte-identical across independent
back-to-back `register.sh` transactions**. The governing invariant — byte-stability
across re-runs, not a fixed digest — holds. Re-running the transaction on the
unchanged post-USIS-002 state produces no file rewrite (idempotent; `generated_at`
is only re-stamped when content actually changes).

## 3 — Guard status

`register.sh --guard` → **exit 3** (uncommitted registration). Per the guard
contract, exit 3 means the transaction sealed COMPLETE but the regenerated
synchronized state is not committed. The mission STOP condition forbids commit, so
this is the **correct and expected** signal, not a defect.

## 4 — Drift attribution (guard drift is SOLELY USIS-002)

Every drifted path was inspected. The complete tracked drift vs `07e0de4`:

**New files (untracked):**
- `15-UNIVERSAL-SCIENCE-INTELLIGENCE/06-UNIVERSES/USIS-002-UNIVERSE-CATALOG.md` (the catalog)
- `00-BOOK/PORTAL/UCOS-USIS-000003.md` (its portal page)

**Regenerated projections (modified):** `00-BOOK/DATA/{artifacts,relationships,id-ledger,change-ledger,control-tower,certification,volumes}.json`, `00-BOOK/REGISTRIES/{UNIVERSAL-ARTIFACT,UNIVERSAL-PAGE,KNOWLEDGE-GRAPH,CHANGE-VERSION-LINEAGE,CERTIFICATION,VOLUME}-REGISTRY.md`, `00-BOOK/CONTROL-TOWER/PROGRAM-CONTROL-TOWER.md`, `00-BOOK/PORTAL/{index.md, UCOS-USIS-000001.md, UCOS-USIS-000002.md}`.

**Attribution proof — the change is exactly one artifact:**

| Aggregate metric | Baseline | Post-USIS-002 | Delta |
|---|---|---|---|
| Registered artifacts | 1003 | 1004 | **+1** |
| Page cursor / max end | 9136 | 9139 | +3 (append-only pages) |
| Knowledge-graph edges | 11845 | 11853 | +8 (the 8 USIS-002 edges) |
| Change events | 1096 | 1097 | +1 |
| ACTIVE artifacts | 910 | 911 | +1 |
| USIS program count | 2 | 3 | +1 |
| VOL-024 artifact_count | 2 | 3 | +1 |
| **New Universal IDs** | — | — | **only `UCOS-USIS-000003`** |

- Content-bearing diffs (`artifacts.json`, `relationships.json`,
  `KNOWLEDGE-GRAPH-REGISTRY.md`, portal pages, etc.) reference **only**
  `UCOS-USIS-000003` / `USIS-002` / `UNIVERSE-CATALOG`.
- Count-only diffs (`certification.json`, `control-tower.json`, `volumes.json`,
  `CERTIFICATION-REGISTRY.md`, `PROGRAM-CONTROL-TOWER.md`) change **solely** the
  aggregate counters above plus `generated_at`.
- **No other new Universal ID.** **No frozen-path change.** **No `config.py`
  change.** (both verified with empty `git diff`.)

**Conclusion:** the guard drift is **wholly and solely attributable to the
intentionally uncommitted USIS-002 registration**. There is no unrelated,
collateral, or unexplained drift.

## 5 — Determination

**Determinism PASS; drift fully attributed to USIS-002.** The repository is
byte-stable and ready for atomic baseline establishment: a single authorized
commit of the catalog + regenerated projections will clear the guard to exit 0.
