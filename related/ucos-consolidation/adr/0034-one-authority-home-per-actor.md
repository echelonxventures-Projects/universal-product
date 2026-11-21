# ADR-0034: An actor's unit of work is one authority home, claimed from an append-only ledger

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-09-04 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | `UCOS-CAA-001`, `ADR-0032` |
| Supersedes | none |

## Context

`ADR-0032` removes the collisions that are mechanical. What remains is two actors editing the
same declaration, which no merge driver can resolve — an `AUTHORED` conflict is a real
disagreement between two people.

The repository already partitions itself: every instrument has exactly one authority, and
`00-MASTER/<AUTH>/` is where its declaration, engine and evidence live.

## Decision

An actor claims **one authority home** at a time, by appending a line to
`00-BOOK/DATA/claims.jsonl`. Claiming is an append, so claiming never conflicts. Two open
claims on one authority home are refused.

Work outside a claimed home — a shared register, a cross-cutting refactor — is coordinated by
the merge classes, not by the claim.

## Alternatives rejected

**Claim at file granularity.** Rejected: a declaration and its engine change together, so
file-level claims would either be constantly contended or constantly stale.

**No claims; rely on the merge classes alone.** Rejected — the merge classes handle mechanical
conflicts, not two people editing one declaration with different intent.

## Revisit conditions

- Authority homes prove too coarse, with several actors routinely needing the same one. That
  would indicate the authority is too large, and the remedy is splitting the authority rather
  than the claim.

## Consequences

Actors in different authority homes cannot conflict except in shared registers, which
`ADR-0032` handles. The claim ledger is append-only, so it is itself concurrency-safe.

## Compliance

`UCOS-CAA-001` already establishes exactly one authority per instrument; this decision reuses
that partition rather than inventing a second one.

## Validation evidence

`00-BOOK/DATA/claims.jsonl` exists and is declared `APPEND_ONLY` in
`00-BOOK/DATA/workspace-coordination.json` at commit `c0c43f88`.
