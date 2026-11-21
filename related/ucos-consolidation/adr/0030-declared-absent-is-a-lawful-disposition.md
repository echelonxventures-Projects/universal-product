# ADR-0030: A deliberate gap is a record, not a defect: `DECLARED_ABSENT` with a reason

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-09-04 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | `UCOS-EXCLUSION-REGISTER-001`, `UCKP-ART-16` |
| Supersedes | none |

## Context

Most recurring requirement arguments are not about whether something works. They are about
whether something *missing* is a defect or a decision — and with no way to say "we chose not
to", every gap is re-argued by whoever next notices it.

The repository already applies the opposite discipline elsewhere and states it plainly: the
exclusion register refuses an ignored path with no declared class, and records that *"an
exemption without a stated reason is a silent one, which is the defect the register exists to
end."* Requirements have no equivalent.

## Decision

`DECLARED_ABSENT` becomes a first-class requirement disposition, requiring **a reason and a
decision reference**. A requirement in that state is satisfied for gate purposes and counted
separately in every projection.

A requirement may not sit in `DECLARED_ABSENT` implicitly. The absence of an owner without such
a record remains a failure.

## Alternatives rejected

**Leave gaps unrecorded and rely on judgement.** Rejected — this is the status quo, and it is
what produced a conformance audit re-deriving conclusions the repository had already reached.

**Treat every gap as a defect until closed.** Rejected: it makes deliberate scope decisions
indistinguishable from oversights, and a permanently failing gate is a gate people learn to
ignore.

## Revisit conditions

- A `DECLARED_ABSENT` record accumulates without review such that the disposition becomes a
  way of parking work rather than deciding it. The remedy would be a ratchet on the count, not
  the removal of the disposition.

## Consequences

"Zero gap" becomes achievable and honest at the same time: every requirement resolves to an
owner or to a recorded decision saying it deliberately does not. Four agnosticism axes and the
L9 vacancy become citable records rather than recurring findings.

## Compliance

`UCKP-ART-16` (executable governance) is satisfied because the disposition is machine-checkable
rather than a note. The pattern is taken from `UCOS-EXCLUSION-REGISTER-001`, which already
requires a class and a rationale for every excluded path.

## Validation evidence

The exclusion register's own refusal text is the precedent, quoted above and readable at
`00-BOOK/DATA/exclusion-register.json`.
