# 01 — Wave-0 Commit Determination

| Field | Value |
|-------|-------|
| ARTIFACT ID | WAVE0-BASE-01 (Commit Determination) |
| MISSION | Wave-0 Canonical Baseline Establishment — Atomic Commit |
| STATUS | COMPLETE · one atomic commit created · AUTHORITY = NONE (DERIVED) |
| COMMIT | `0bcea68458c07e7f21e2af267bf235ee09518260` (parent `57d91b7`) |

> Note: this artifact (and the 02/03 outputs) reference the commit SHA and are therefore produced **after** the commit; they are post-commit evidence and are **uncommitted** (they cannot be inside the commit they describe).

---

## 1 — Commit-scope determination (repository truth)

The commit represents the **complete accepted Wave-0 realization source + governance**, isolated from unrelated working-tree state by **path staging**.

**INCLUDED (15 files):**
- `00-BOOK/tools/config.py` — Phase 0.3 governed registration (append-only USIS family: VOL-024, CLASSIFY_RULE, CHAINS, PROGRAM_ROOTS, CROSS_PROGRAM). Diff-vs-HEAD verified USIS-only, no contamination.
- `15-UNIVERSAL-SCIENCE-INTELLIGENCE/USIS-GOV-000-…md` — Phase 0.4 registered corpus root (`UCOS-USIS-000001`, VOL-024).
- `00-MASTER/UCOS-USIS-WAVE0/**` — Wave-0 operational memory: Phase 0.1 governance activation, FREEZE-C4 engine + package (3 registers), Wave-0 completion determination, and the 7 acceptance artifacts (01–07).

**EXCLUDED — and why (all explicit mission prohibitions honored):**
| Excluded | Reason |
|----------|--------|
| `00-BOOK/DATA/**`, `REGISTRIES/**`, `CONTROL-TOWER/**`, `PORTAL/**` (regenerated projections) | REG-AUTO generated state that **entangles** Wave-0's USIS registration with **pre-existing REF drift** in shared files; committing them whole would include "unrelated reference registrations" (forbidden). Deferred to a separate REG-AUTO sync (§3 of 03). |
| `00-BOOK/PORTAL/UCOS-REF-000007…015.md`, `04-REFERENCE/*.docx` | Pre-existing unrelated reference-file drift (forbidden). |
| `00-MASTER/UAKOS-PHASE-*`, `UCOS-CRAT-001`, `UCOS-CVER-001`, `UCOS-EKAP-001`, `UCOS-USIS-001`, `EIP-018D` | Pre-existing / separate-mission operational-memory packages (forbidden: unrelated). |

## 2 — Constraint compliance

| Rule | Honored? |
|------|:--------:|
| ONLY Wave-0 artifacts | ✅ (staged scope verified: 0 REF/docx/projection/pre-existing-op-memory) |
| No unrelated historical drift | ✅ |
| No unrelated reference registrations | ✅ (they live only in the excluded projections) |
| No unrelated operational-memory packages | ✅ (only Wave-0's own `UCOS-USIS-WAVE0` included, as required by the "acceptance artifacts included" check) |
| No reconcile historical drift / no unrelated cleanup | ✅ (pre-existing drift left untouched) |
| Hooks not skipped | ✅ (pre-commit ruff gate ran and passed; no `--no-verify`) |
| One atomic commit | ✅ |

## 3 — Pre-commit verification (all passed before committing)

- config.py diff-vs-HEAD = USIS-only (append-only) ✅
- Deterministic regeneration unchanged (build idempotent; change count stable) ✅
- Validation unchanged (`ukb validate` 1002; `ukb enforce` 1002/1002) ✅
- Volume duplicates = NONE; acceptance PASS remains valid ✅
- Pre-commit hook = ruff lint/format on engine+platform (untouched by Wave 0) → passes ✅

## 4 — Determination

**COMMIT AUTHORIZED-SCOPE ESTABLISHED and CREATED.** One atomic commit `0bcea68` captures the accepted Wave-0 realization source + governance, with unrelated drift correctly excluded. The REG-AUTO projection sync (which must also reconcile the pre-existing REF drift) is the explicit next step, requiring separate authorization.

*END — 01 · WAVE-0 COMMIT DETERMINATION · AUTHORITY = NONE (DERIVED).*
