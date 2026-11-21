# 00-MASTER — MASTER CONTEXT SYSTEM (MCS) · UCOS Ω∞

**The permanent operational control plane of UCOS Ω∞.** The single operational memory that makes the program **state-driven, not conversation-driven** — ending repeated discovery, audits, planning, and "what next" determination.

> **AUTHORITY = NONE — DERIVED TRUTH.** MCS coordinates, remembers, tracks, synchronizes, and controls execution. It creates no constitutional authority, redefines no architecture, supersedes nothing. It is *operational memory*, not corpus: it never writes `00-SOURCE/`, `99-FREEZE/`, or `00-BOOK/`, and is subordinate to all governance.

## Deterministic boot (do this first, every session)

```bash
# 1–2 answer WHO/WHY/RULES and WHERE/WHAT-NEXT — always read both:
#   00-MASTER/MCP-001-MASTER-CONTEXT.md   (identity + rules)
#   00-MASTER/MCP-002-MASTER-STATE.md     (state + Next Authorized Capability)
# then verify the repository:
git branch --show-current && git rev-parse HEAD && git status --porcelain && git fetch --quiet && git rev-list --left-right --count origin/governance-reconciliation...HEAD
```

## Components (one responsibility each)

| File | Answers | Cadence |
|------|---------|---------|
| `MCS-000-MASTER-CONTEXT-SYSTEM-ARCHITECTURE.md` | How is the control plane structured? | rare |
| `MCP-001-MASTER-CONTEXT.md` | Who are we and by what rules? | rare |
| `MCP-002-MASTER-STATE.md` | **Where are we and what is next?** | every session |
| `MCP-003-MASTER-EXECUTION.md` | What is authorized to run? | per capability |
| `MCP-004-MASTER-DECISIONS.md` | Why is it this way? | per decision |
| `MCP-005-MASTER-DASHBOARD.md` | How much is done? | per report |
| `MCP-006-MASTER-TRACEABILITY.md` | Can we prove it? | per validated unit |
| `MCP-007-MASTER-RECOVERY.md` | How do we resume? | per interruption |

Supporting: `STATE/` (machine mirror of MCP-002 + schema, regenerated) · `CHECKPOINTS/` (append-only session resume anchors).

## Reading order

`MCP-001` → `MCP-002` (always) → then `MCP-003`/`004`/`005`/`006`/`007` on demand. Full rules of the control plane are in `MCS-000`.

## Provenance

Established 2026-07-18 under **Mission MCP-002**, decomposing the monolithic root `MCP-001-MASTER-CONTEXT-AND-EXECUTION-SYSTEM.md` (now a redirect pointer) into these single-responsibility components with zero content loss. See `MCS-000 §12` (Migration Plan) and `MCP-004` (MCS-DEC-001).
