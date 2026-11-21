# ADR-0033: Actors queue mint requests; the operator mints in scheduled windows

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-09-04 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | `UCKP-ART-05`, `REG-AUTO-001` |
| Supersedes | none |

## Context

An allocation permit is `single_use` and bound to a specific `head`. Any commit that moves the
head invalidates every outstanding permit. Measured twice on this branch:
`P-UCOS-CORPUS-001` authorized an allocation and was never spent because *"the coverage
programme's own commit moved HEAD before it could be exercised"*; `P-UCOS-CORPUS-003` was
minutes from the same fate.

With more than one actor this is not an edge case. It is the normal outcome.

## Decision

Actors never mint. An actor needing identity appends a request to
`00-BOOK/DATA/mint-requests.jsonl` and continues against the request. The operator mints in a
scheduled window, so every identity in that window lands in one commit and only one permit is
ever outstanding.

The refusal is already structural: `--mint` without `--permit` fails `NO_ALLOCATION`.

## Alternatives rejected

**Parallelize minting.** Rejected, and it should stay rejected when someone proposes it after
waiting for a window: identity is irreversible by constitutional design, and the wait is the
price of an identifier that is never reissued.

**Bind permits to a branch rather than a head.** Rejected: the head binding is what makes a
permit authorize *this* allocation and no other; loosening it to a branch would authorize any
allocation on that branch.

## Revisit conditions

- The mint window becomes a throughput bottleneck measured in days rather than hours, at which
  point the remedy is more frequent windows, not concurrent minting.

## Consequences

Minting stays serial — which it must — but predictably rather than surprisingly. No actor's
permit is invalidated by another's merge, because at most one permit is live at a time.

## Compliance

`ART-05` is the whole basis: an irreversible act cannot be made concurrent without risking a
reissue. `REG-AUTO-001` continues to govern the allocation itself; this decision governs only
when it is requested and by whom.

## Validation evidence

Three permits were exercised this session under exactly this discipline —
`P-UCOS-CORPUS-003`, `P-UCOS-UGA-002` and `P-UCOS-UGA-003` — each issued by the operator
against a manifest the agent measured and presented, and each spent before the head moved.
`00-BOOK/DATA/allocation-permits.json` records all three, including
`P-UCOS-CORPUS-001` left in place and dead by binding, which the register notes is *"the
stronger guarantee"* than deletion.
