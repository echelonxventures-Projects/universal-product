# MCP-001 — MASTER CONTEXT & EXECUTION SYSTEM → MOVED TO THE MASTER CONTEXT SYSTEM (`00-MASTER/`)

| Field | Value |
|-------|-------|
| STATUS | **REDIRECT POINTER** — content decomposed into the Master Context System (MCS) |
| SUPERSEDED BY | `00-MASTER/` (MCS-000 + MCP-001…007) |
| AUTHORITY | **NONE — DERIVED TRUTH** (unchanged) |
| MIGRATION | Mission MCP-002 · 2026-07-18 · decision `MCS-DEC-001` (see `00-MASTER/MCP-004-MASTER-DECISIONS.md`) |

> **This file has been decomposed, not deleted.** The single monolithic MCP-001 (17 sections mixing permanent identity with dynamic state) was split into the **Master Context System** under `00-MASTER/`, where each artifact has exactly one responsibility. No content was lost; git history retains the original. This stub remains so the well-known entry path keeps resolving.

## Deterministic boot — read these two files first, every session

1. **`00-MASTER/MCP-001-MASTER-CONTEXT.md`** — who we are and by what rules (permanent identity).
2. **`00-MASTER/MCP-002-MASTER-STATE.md`** — where we are and what to do next (dynamic state).

Then verify the repository:
```bash
git branch --show-current && git rev-parse HEAD && git status --porcelain && git fetch --quiet && git rev-list --left-right --count origin/governance-reconciliation...HEAD
```

## The Master Context System (`00-MASTER/`)

| Component | Answers | Was (this file's section) |
|-----------|---------|---------------------------|
| `MCS-000-MASTER-CONTEXT-SYSTEM-ARCHITECTURE.md` | How is the control plane structured? | §17 (validation) + new architecture |
| `MCP-001-MASTER-CONTEXT.md` | Who are we / by what rules? | §01, §02, §05, §12, §15, §16 |
| `MCP-002-MASTER-STATE.md` | Where are we / what next? | §08 |
| `MCP-003-MASTER-EXECUTION.md` | What is authorized to run? | §06, §07, §09 |
| `MCP-004-MASTER-DECISIONS.md` | Why is it this way? | §04 |
| `MCP-005-MASTER-DASHBOARD.md` | How much is done? | §03, §10, §14 |
| `MCP-006-MASTER-TRACEABILITY.md` | Can we prove it? | (new consolidated trace graph) |
| `MCP-007-MASTER-RECOVERY.md` | How do we resume? | §11 |

Full section→component mapping and rollback: `00-MASTER/MCS-000-MASTER-CONTEXT-SYSTEM-ARCHITECTURE.md` §12 (Migration Plan). Subsystem index: `00-MASTER/README.md`.

---

*REDIRECT POINTER · The operational memory of UCOS Ω∞ now lives in `00-MASTER/` · AUTHORITY = NONE (DERIVED TRUTH)*
