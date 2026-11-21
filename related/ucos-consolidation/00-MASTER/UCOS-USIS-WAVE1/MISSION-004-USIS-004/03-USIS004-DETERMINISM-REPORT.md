# 03 — USIS-004 DETERMINISM & DRIFT-ATTRIBUTION REPORT

---

## 1 — Determinism method (reproducible)

```
find 00-BOOK/DATA 00-BOOK/REGISTRIES 00-BOOK/CONTROL-TOWER 00-BOOK/PORTAL -type f \
  | LC_ALL=C sort | xargs shasum -a 256 | shasum -a 256
```

Aggregates the entire guard-scope projection surface into a single SHA-256.

## 2 — Determinism result

| Observation | Guard-scope aggregate SHA-256 |
|---|---|
| USIS-002 baseline (`8db7d52`) | `b406563c21af1316fe34ab6414a0e2c45822093ec7e312187e3e59680a113dbd` |
| USIS-004 — this review, run A | `14ce16f86f5fedd28e401f00ec486eae9e8486d929bc31d30ec9b77b58195970` |
| USIS-004 — this review, run B | `14ce16f86f5fedd28e401f00ec486eae9e8486d929bc31d30ec9b77b58195970` |

**DETERMINISM: PASS.** The digest evolved deterministically from the baseline once
USIS-004 registered (expected), and is **byte-identical across independent
back-to-back `register.sh` transactions**. The governing invariant — byte-stability
across re-runs — holds; re-running on the unchanged post-USIS-004 state produces no
file rewrite (idempotent).

## 3 — Guard status

`register.sh --guard` → **exit 3** (uncommitted registration). The transaction
sealed COMPLETE but the regenerated synchronized state is not committed (STOP
forbids commit). This is the correct, expected pending-commit signal — not a defect.

## 4 — Drift attribution (guard drift is SOLELY USIS-004)

Complete tracked drift vs `8db7d52`:

**New files (untracked):**
- `15-…/05-META-MODEL/USIS-004-UNIVERSAL-CAPABILITY-META-MODEL.md` (the meta-model)
- `00-BOOK/PORTAL/UCOS-USIS-000004.md` (its portal page)

**Regenerated projections (modified):** `00-BOOK/DATA/*.json`, `00-BOOK/REGISTRIES/*.md`,
`00-BOOK/CONTROL-TOWER/PROGRAM-CONTROL-TOWER.md`, `00-BOOK/PORTAL/{index.md,
UCOS-USIS-000001.md, UCOS-USIS-000002.md, UCOS-USIS-000003.md}`.

**Attribution proof — the change is exactly one artifact:**

| Aggregate metric | Baseline | Post-USIS-004 | Delta |
|---|---|---|---|
| Registered artifacts | 1004 | 1005 | **+1** |
| Page cursor / max end | 9139 | 9142 | +3 (append-only) |
| Change events | 1097 | 1098 | +1 |
| VOL-024 artifact_count | 3 | 4 | +1 |
| **New Universal IDs** | — | — | **only `UCOS-USIS-000004`** |

- Content-bearing diffs reference **only** `UCOS-USIS-000004` / `USIS-004` /
  `UNIVERSAL-CAPABILITY-META-MODEL`.
- **No other new Universal ID.** **No frozen-path change.** **No `config.py`
  change.** (both verified with empty `git diff`.)

**Conclusion:** the guard drift is **wholly and solely attributable to the
intentionally uncommitted USIS-004 registration**. No unrelated or collateral drift.

## 5 — Determination

**Determinism PASS; drift fully attributed to USIS-004.** The repository is
byte-stable and ready for atomic baseline establishment: a single authorized commit
of the meta-model + regenerated projections will clear the guard to exit 0.
