# ADR-0037: Decisions D-01…D-12 and their successors are the operator's; agents propose

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-09-04 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | `CEP-002` §14.2, `CMG-000001` XLIV.5, `UCKP-ART-16` |
| Supersedes | none |

## Context

An agent that authorizes its own irreversible acts is the failure mode the constitution names
most directly: `CMG-000001` XLIV.5 prohibits self-ratification, and `CLAUDE.md` states of
identity allocation that *"you may not self-authorize it."*

This session tested that boundary three times, and each time the permit's authorization prose
recorded that the operator was shown a manifest and instructed the act — *"the agent recorded
that instruction; it did not originate it."*

## Decision

Decisions of the class recorded in this ADR series are taken by the operator alone. An agent
may measure, propose, draft the record and present a manifest; it may not decide.

The proposal lane is the route: a proposal never becomes truth until it has passed the
assimilation gates.

## Alternatives rejected

**Let agents decide reversible things.** Rejected as a category: the difficulty is that
reversibility is itself a judgement, and an agent that judges an act reversible has already
decided.

**Require operator approval for every commit.** Rejected — it makes the operator the
bottleneck for work that gates already govern, and eight commits this session were validated by
gates without needing a decision.

## Revisit conditions

- A class of decision is identified that is both frequent and genuinely mechanical, at which
  point it should be delegated explicitly and by name rather than by an agent's discretion.

## Consequences

The operator lane is thin but blocking: it appears at permits, reserved decisions and go-live.
Everything else proceeds under gates.

## Compliance

`CEP-002` §14.2 reserves this decision class. `CMG-000001` XLIV.5 prohibits self-ratification,
which is also why L9 — the law governing constitutional evolution's own governance — is open by
construction rather than closed from inside.

## Validation evidence

Three permits this session (`P-UCOS-CORPUS-003`, `P-UCOS-UGA-002`, `P-UCOS-UGA-003`), each
carrying an `$authorization` recording the operator's instruction and the agent's role in
recording rather than originating it.
