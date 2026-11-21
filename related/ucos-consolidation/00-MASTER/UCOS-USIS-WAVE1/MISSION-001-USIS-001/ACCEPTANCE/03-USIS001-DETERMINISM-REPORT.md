# 03 — USIS-001 DETERMINISM REPORT (independent)

**Claim under test.** The USIS-001 registration regenerates the synchronized projections **deterministically** — two independent full `register.sh` transactions produce byte-identical guard-scope output (modulo the intentional per-run `generated_at` stamp).

---

## 1 — Method (independent, reproducible)

1. With the corpus in its post-registration state, snapshot the entire guard scope
   `00-BOOK/{DATA, REGISTRIES, CONTROL-TOWER, PORTAL}` → `/tmp/snap1`.
2. Re-run the complete transaction: `register.sh` (10 phases) → **TRANSACTION COMPLETE (exit 0)**.
3. Recursively diff the regenerated guard scope against `/tmp/snap1`, neutralizing only the
   documented volatile fields (`generated_at`, append-only `audit run` counters, connector `as_of`).

## 2 — Result

| Guard-scope directory | `diff -r` (volatile-neutralized) | Verdict |
|---|:--:|:--:|
| `00-BOOK/DATA/` | exit 0 (no differences) | **byte-identical** |
| `00-BOOK/REGISTRIES/` | exit 0 (no differences) | **byte-identical** |
| `00-BOOK/CONTROL-TOWER/` | exit 0 (no differences) | **byte-identical** |
| `00-BOOK/PORTAL/` | exit 0 (no differences) | **byte-identical** |

**DETERMINISM: PASS.** Content is reproduced exactly across independent transactions. The only per-run variation is the `generated_at` timestamp, which the engine's own `_stamp_eq_json` neutralizer treats as non-semantic (consistent with the implementer's byte-stable guard-scope hash `b53f7fcb61ba125a7b61f79f291f8157ead7442c1c855a9481bdd4b042bc6f24`).

## 3 — Idempotence corroboration

- Re-running `register.sh` allocated **no new IDs or pages** (append-only ledger; page cursor stable at 9 136) — repeated runs add no artifacts (corpus fixed at **1003**) and no change/version/lineage growth beyond the single USIS-001 event.
- `ukbx sync --due` reported **+0 new signals** on re-run (steady-state, cadence-respecting) — the transaction does not accrete audit state when nothing changed.
- Working tree was identical before and after all re-runs (`16 modified + 20 untracked`), i.e. the acceptance review itself introduced **zero** additional drift.

## 4 — Drift determinism (guard)

`register.sh --guard` deterministically returns **exit 3** and enumerates the identical guard-scope set on each run — the regenerated 16 files plus the new `PORTAL/UCOS-USIS-000002.md`. The drift is stable in both **content** (§2) and **membership** (§2 of `02-USIS001-VALIDATION-SUMMARY.md`), and is entirely attributable to the uncommitted USIS-001 artifact.

## 5 — Determination

**USIS-001 regeneration is deterministic and idempotent.** Repeated independent transactions converge on identical repository state; the pending drift is a stable, fully-attributable, commit-ready delta.
