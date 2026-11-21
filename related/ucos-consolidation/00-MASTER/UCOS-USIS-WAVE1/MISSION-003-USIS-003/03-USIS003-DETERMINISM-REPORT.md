# 03 — USIS-003 DETERMINISM & DRIFT-ATTRIBUTION REPORT

---

## 1 — Determinism method (reproducible)

```
find 00-BOOK/DATA 00-BOOK/REGISTRIES 00-BOOK/CONTROL-TOWER 00-BOOK/PORTAL -type f \
  | LC_ALL=C sort | xargs shasum -a 256 | shasum -a 256
```

## 2 — Determinism result

| Observation | Guard-scope aggregate SHA-256 |
|---|---|
| USIS-004 baseline (`e33c05b`) | `14ce16f86f5fedd28e401f00ec486eae9e8486d929bc31d30ec9b77b58195970` |
| USIS-003 — this review, run A | `4d97626235722c2bdbc61ca431b813c462a5af3f00425d620470651c3d86504d` |
| USIS-003 — this review, run B | `4d97626235722c2bdbc61ca431b813c462a5af3f00425d620470651c3d86504d` |

**DETERMINISM: PASS.** The digest evolved deterministically from the baseline once
USIS-003 registered (expected), and is **byte-identical across independent
back-to-back `register.sh` transactions**. The governing invariant — byte-stability
across re-runs — holds (idempotent regeneration).

## 3 — Guard status

`register.sh --guard` → **exit 3** (uncommitted registration). The transaction
sealed COMPLETE but the regenerated synchronized state is not committed (STOP
forbids commit). Correct, expected pending-commit signal — not a defect.

## 4 — Drift attribution (guard drift is SOLELY USIS-003)

Complete tracked drift vs `e33c05b`:

**New files (untracked):**
- `15-…/07-SCIENCES/USIS-003-UNIVERSAL-SCIENCE-CATALOG.md` (the science catalog)
- `00-BOOK/PORTAL/UCOS-USIS-000005.md` (its portal page)

**Regenerated projections (modified):** `00-BOOK/DATA/*.json`,
`00-BOOK/REGISTRIES/*.md`, `00-BOOK/CONTROL-TOWER/PROGRAM-CONTROL-TOWER.md`,
`00-BOOK/PORTAL/{index.md + prior USIS pages}`.

**Attribution proof — exactly one artifact:**

| Aggregate metric | Baseline | Post-USIS-003 | Delta |
|---|---|---|---|
| Registered artifacts | 1005 | 1006 | **+1** |
| Change events | 1098 | 1099 | +1 |
| VOL-024 artifact_count | 4 | 5 | +1 |
| **New Universal IDs** | — | — | **only `UCOS-USIS-000005`** |

- Content-bearing diffs reference **only** `UCOS-USIS-000005` / `USIS-003` /
  `UNIVERSAL-SCIENCE-CATALOG`.
- **No other new Universal ID.** **No frozen-path change.** **No `config.py`
  change.** (verified with empty `git diff`.)

**Conclusion:** the guard drift is **wholly and solely attributable to the
intentionally uncommitted USIS-003 registration**. No unrelated or collateral drift.

## 5 — Determination

**Determinism PASS; drift fully attributed to USIS-003.** The repository is
byte-stable and ready for atomic baseline establishment: a single authorized commit
of the science catalog + regenerated projections will clear the guard to exit 0.
