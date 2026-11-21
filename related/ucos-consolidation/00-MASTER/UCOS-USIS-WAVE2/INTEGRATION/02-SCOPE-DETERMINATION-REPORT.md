# EVO-USIS-W2-INTEGRATION-001 · 02 — Scope Determination Report (Phase 1)

| Field | Value |
|-------|-------|
| ARTIFACT ID | EVO-USIS-W2-INT-001-SCOPE | PROGRAM | UCOS-USIS-001 |
| CONFLICT RULE | Higher frozen/governing instruments prevail. |

> **Purpose.** Determine the canonical implementation scope from Repository Truth. Coverage = 100%.

## 1 — Canonical software / engine / platform / runtime streams (discovered, read-only)

| Stream | Path | Files | Status | Integration action |
|--------|------|:-----:|--------|--------------------|
| Engine | `engine/` | 922 | EC-1 certified · frozen | reference only (0 writes; DP-03) |
| Platform | `platform/` | 1475 | EC-2 frozen | reference only (0 writes; DP-03) |
| Service | `service/` | 545 | Software stream | reference only |
| Infrastructure | `infrastructure/` | 456 | Software stream | reference only |
| Application | `application/` | 457 | Software stream | reference only |
| Intelligence (RIE) | `intelligence/` | 58 | RIE (distinct from USIS subject-matter) | reference only |
| Knowledge | `knowledge/` | 12 | Software stream | reference only |

## 2 — Integration targets & existing/missing/reusable

| Dimension | Determination |
|-----------|---------------|
| Integration targets | the 9 certified Wave-2 architecture layers (USIS-007/006/009/008/010/011/013/012/017) → Implementation tier (USIS-004 tier 19) |
| Existing implementations | Software streams above (frozen/EC-certified) — reused by reference |
| Missing implementations | none required at Wave-2: per-capability code is Wave-3 (Software stream); Implementation tier here is a composition specification, not code |
| Reusable implementations | all discovered Software streams; `ukb`/`ukbx`/`register.sh`; registries; UCIC-001 |
| Canonical implementation home | `15-…/20-PROJECTS/` (USIS-005 §2 implementation projects) |

## 3 — Determination

Scope = the executable-composition binding of the 9-layer spine to the Implementation tier, referencing the discovered Software streams as-is. **No new Software-stream code is in scope** (Wave-3 / Software-stream owns that). Scope Determination coverage = **100%**.

*END — 02 Scope Determination Report · 100%.*
