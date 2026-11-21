# EVO-USIS-W2-INTEGRATION-001 · 09 — Regression Report (Phase 8)

| Field | Value |
|-------|-------|
| ARTIFACT ID | EVO-USIS-W2-INT-001-REG | PROGRAM | UCOS-USIS-001 |
| CONFLICT RULE | Higher frozen/governing instruments prevail. |

> **Purpose.** Verify all previously certified architecture layers remain unchanged. Coverage = 100%.

## 1 — Spine regression check

| Layer | Universal ID | Status |
|-------|--------------|--------|
| USIS-007 Domain | UCOS-USIS-000007 | ACTIVE |
| USIS-006 Capability | UCOS-USIS-000008 | ACTIVE |
| USIS-009 Model | UCOS-USIS-000009 | ACTIVE |
| USIS-008 Algorithm | UCOS-USIS-000010 | ACTIVE |
| USIS-010 Pattern | UCOS-USIS-000011 | ACTIVE |
| USIS-011 Engine | UCOS-USIS-000012 | ACTIVE |
| USIS-013 Runtime | UCOS-USIS-000013 | ACTIVE |
| USIS-012 Service | UCOS-USIS-000014 | ACTIVE |
| USIS-017 API/SDK | UCOS-USIS-000015 | ACTIVE |
| USIS-INT-001 Integration (this) | UCOS-USIS-000016 | ACTIVE |

## 2 — Verification

| Check | Result | Evidence |
|-------|--------|----------|
| All prior layers unchanged | PASS | 9 spine layers ACTIVE (programmatic == True); registered count grew 1133 → 1134 (+1 only) |
| No regressions | PASS | `ukbx certify` re-ran over full scope (1134) → 10/10; prior certifications hold |
| No ownership drift | PASS | 9 distinct homes intact; 1 owner/tier; USIS-INT-001 owns only the Implementation-tier composition |
| No dependency drift | PASS | `twin --check` C-07 acyclic; prior edges intact; +24 new edges from USIS-INT-001 only |
| No registry drift | PASS | `ukb validate` append-only ledger intact; no renumber/reuse; no prior artifact mutated |
| No frozen-stream change | PASS | `git status engine/ platform/` = 0 |

## 3 — Determination

**0 regressions.** All previously certified layers unchanged; no ownership/dependency/registry drift; frozen streams untouched. Coverage = **100%**.

*END — 09 Regression Report · 0 regressions · 100%.*
